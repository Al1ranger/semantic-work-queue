import ast
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
import pytest

START = int(datetime(2026, 10, 8, 12, tzinfo=timezone.utc).timestamp())


def addr(value):
    return "0x" + value.hex() if isinstance(value, bytes) else str(value)


def warp(vm, seconds):
    text = datetime.fromtimestamp(START + seconds, timezone.utc).isoformat()
    vm.warp(text)
    from genlayer import gl
    gl.message_raw["datetime"] = text


def source(rfc=2119):
    return ("Request for Comments: " + str(rfc) + "\nFull synthetic normative keyword definitions.\n").encode()


def mock(vm, raw=None, topic="MODALITY", status=200, output=None):
    vm.clear_mocks()
    vm.mock_web(r".*rfc[0-9]+\.txt", {"status": status, "body": source() if raw is None else raw})
    vm.mock_llm(r"(?s).*Classify the PRIMARY substantive topic.*", json.dumps({"topic": topic} if output is None else output))


@pytest.fixture
def contract(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    direct_vm.warp("2026-10-08T12:00:00Z")
    return direct_deploy("contracts/SemanticWorkQueue.py")


def submit(contract, creator, name="demo", raw=None, rfc=2119, deadline=3600):
    raw = source(rfc) if raw is None else raw
    contract.submit(name, rfc, hashlib.sha256(raw).hexdigest(), START + deadline)
    return contract.job_key(addr(creator), name)


def routed(contract, vm, creator, name="demo", topic="MODALITY"):
    key = submit(contract, creator, name)
    mock(vm, topic=topic)
    contract.route(key)
    return key


@pytest.fixture
def helpers():
    tree = ast.parse(Path("contracts/SemanticWorkQueue.py").read_text())
    functions = [item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name in
                 ("canonical", "digest", "parse_topic", "equivalent")]
    namespace = {"hashlib": hashlib, "json": json, "LANES": ("NAMES", "ADDRESSES", "MODALITY", "GENERAL")}
    exec(compile(ast.Module(body=functions, type_ignores=[]), "actual_contract_helpers", "exec"), namespace)
    return namespace


def test_semantic_routing_changes_actual_lane(contract, direct_vm, direct_alice, helpers):
    key = routed(contract, direct_vm, direct_alice)
    job = contract.get_job(key)
    assert job["state"] == "WAITING" and job["lane"] == "MODALITY" and job["ticket"] == 0
    assert contract.get_lane("MODALITY")["head_job"] == key
    assert contract.get_lane("NAMES")["tail"] == 0
    assert job["report"]["root"] == helpers["digest"]({k: v for k, v in job["report"].items() if k != "root"})
    second = routed(contract, direct_vm, direct_alice, "other", "NAMES")
    assert contract.get_lane("NAMES")["head_job"] == second


def test_route_is_permissionless_but_not_caller_labelled(contract, direct_vm, direct_alice, direct_bob):
    key = submit(contract, direct_alice)
    direct_vm.sender = direct_bob
    mock(direct_vm, topic="ADDRESSES")
    contract.route(key)
    assert contract.get_job(key)["lane"] == "ADDRESSES"


def test_wrong_commitment_never_enters_queue(contract, direct_vm, direct_alice):
    key = submit(contract, direct_alice)
    mock(direct_vm, raw=source() + b"tampered")
    contract.route(key)
    assert contract.get_job(key)["state"] == "REJECTED"
    assert contract.get_job(key)["terminal_reason"] == "HASH_MISMATCH"
    assert contract.get_lane("MODALITY")["tail"] == 0


def test_unknown_quarantines_without_dispatch(contract, direct_vm, direct_alice):
    key = routed(contract, direct_vm, direct_alice, topic="UNKNOWN")
    assert contract.get_job(key)["state"] == "QUARANTINED"
    assert all(contract.get_lane(lane)["tail"] == 0 for lane in ("NAMES", "MODALITY", "ADDRESSES", "GENERAL"))


def test_authenticated_lease_and_ack_advance_fifo(contract, direct_vm, direct_alice, direct_bob):
    key = routed(contract, direct_vm, direct_alice)
    direct_vm.sender = direct_bob
    contract.enroll("MODALITY")
    contract.claim("MODALITY", 60)
    lease = contract.get_job(key)["lease"]
    assert lease["worker"] == addr(direct_bob) and lease["number"] == 1
    contract.acknowledge(key, lease["token"])
    assert contract.get_job(key)["state"] == "ACKED"
    assert contract.get_lane("MODALITY")["head"] == 1


def test_fifo_cannot_skip_active_head(contract, direct_vm, direct_alice, direct_bob):
    first = routed(contract, direct_vm, direct_alice)
    second = routed(contract, direct_vm, direct_alice, "second")
    contract.enroll("MODALITY")
    contract.claim("MODALITY", 60)
    token = contract.get_job(first)["lease"]["token"]
    direct_vm.sender = direct_bob
    contract.enroll("MODALITY")
    with direct_vm.expect_revert("active lease"):
        contract.claim("MODALITY", 60)
    contract.prune("MODALITY")
    assert contract.get_lane("MODALITY")["head_job"] == first
    direct_vm.sender = direct_alice
    contract.acknowledge(first, token)
    contract.claim("MODALITY", 60)
    assert contract.get_job(second)["state"] == "LEASED"


def test_unenrolled_and_wrong_lane_cannot_claim(contract, direct_vm, direct_alice):
    routed(contract, direct_vm, direct_alice)
    contract.enroll("NAMES")
    with direct_vm.expect_revert("worker not enrolled in lane"):
        contract.claim("MODALITY", 60)


def test_public_token_not_authority(contract, direct_vm, direct_alice, direct_bob):
    key = routed(contract, direct_vm, direct_alice)
    contract.enroll("MODALITY")
    contract.claim("MODALITY", 60)
    token = contract.get_job(key)["lease"]["token"]
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("invalid or expired lease acknowledgement"):
        contract.acknowledge(key, token)


def test_expired_lease_reclaim_fences_old_worker_and_token(contract, direct_vm, direct_alice, direct_bob):
    key = routed(contract, direct_vm, direct_alice)
    contract.enroll("MODALITY")
    contract.claim("MODALITY", 30)
    old = contract.get_job(key)["lease"]["token"]
    warp(direct_vm, 30)
    with direct_vm.expect_revert("invalid or expired lease acknowledgement"):
        contract.acknowledge(key, old)
    direct_vm.sender = direct_bob
    contract.enroll("MODALITY")
    contract.claim("MODALITY", 60)
    new = contract.get_job(key)["lease"]["token"]
    assert old != new and contract.get_job(key)["leases"] == 2
    with direct_vm.expect_revert("invalid or expired lease acknowledgement"):
        contract.acknowledge(key, old)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("invalid or expired lease acknowledgement"):
        contract.acknowledge(key, new)
    direct_vm.sender = direct_bob
    contract.acknowledge(key, new)


def test_third_expired_lease_deadletters_permissionlessly(contract, direct_vm, direct_alice, direct_bob):
    key = routed(contract, direct_vm, direct_alice)
    contract.enroll("MODALITY")
    for index in range(3):
        warp(direct_vm, index * 30)
        contract.claim("MODALITY", 30)
    warp(direct_vm, 90)
    direct_vm.sender = direct_bob
    contract.prune("MODALITY")
    assert contract.get_job(key)["state"] == "DEAD"
    assert contract.get_job(key)["terminal_reason"] == "LEASE_QUOTA"
    assert contract.get_lane("MODALITY")["head"] == 1


def test_third_active_lease_still_ackable(contract, direct_vm, direct_alice):
    key = routed(contract, direct_vm, direct_alice)
    contract.enroll("MODALITY")
    for index in range(3):
        warp(direct_vm, index * 30)
        contract.claim("MODALITY", 30)
    contract.acknowledge(key, contract.get_job(key)["lease"]["token"])
    assert contract.get_job(key)["state"] == "ACKED"


@pytest.mark.parametrize("stage", ["SUBMITTED", "WAITING", "LEASED"])
def test_all_unresolved_states_expire(contract, direct_vm, direct_alice, direct_bob, stage):
    key = submit(contract, direct_alice, deadline=90)
    if stage != "SUBMITTED":
        mock(direct_vm)
        contract.route(key)
    if stage == "LEASED":
        contract.enroll("MODALITY")
        contract.claim("MODALITY", 300)
        assert contract.get_job(key)["lease"]["until"] == START + 90
    warp(direct_vm, 90)
    direct_vm.sender = direct_bob
    contract.expire(key)
    assert contract.get_job(key)["state"] == "DEAD"
    if stage != "SUBMITTED":
        contract.prune("MODALITY")
        assert contract.get_lane("MODALITY")["head"] == 1


def test_cross_job_token_and_replay_rejected(contract, direct_vm, direct_alice):
    key = routed(contract, direct_vm, direct_alice)
    second = routed(contract, direct_vm, direct_alice, "second")
    contract.enroll("MODALITY")
    contract.claim("MODALITY", 60)
    token = contract.get_job(key)["lease"]["token"]
    with direct_vm.expect_revert("invalid or expired lease acknowledgement"):
        contract.acknowledge(second, token)
    contract.acknowledge(key, token)
    with direct_vm.expect_revert("invalid or expired lease acknowledgement"):
        contract.acknowledge(key, token)
    with direct_vm.expect_revert("routing closed"):
        contract.route(key)


def test_creator_namespaces_prevent_id_poisoning(contract, direct_vm, direct_alice, direct_bob):
    first = submit(contract, direct_alice)
    direct_vm.sender = direct_bob
    second = submit(contract, direct_bob)
    assert first != second


def test_unavailable_retry_reports_preserved_and_bounded(contract, direct_vm, direct_alice):
    key = submit(contract, direct_alice)
    mock(direct_vm, status=503)
    for index in range(3):
        contract.route(key)
        assert contract.get_job(key)["attempts"] == index + 1
        assert contract.get_event(index + 1)["details"]["report"]["outcome"] == "UNAVAILABLE"
    assert contract.get_job(key)["state"] == "DEAD"
    with direct_vm.expect_revert("routing closed"):
        contract.route(key)


@pytest.mark.parametrize("raw,reason", [(b"Request for Comments: 2606\nWrong identity", "RFC_IDENTITY"),
    (b"Request for Comments: 2119\n\xff", "INVALID_UTF8"),
    (b"Request for Comments: 2119\n\x00", "RFC_IDENTITY"), (b"x" * 16385, "SOURCE_SIZE")])
def test_bad_full_source_never_routes(contract, direct_vm, direct_alice, raw, reason):
    key = submit(contract, direct_alice, raw=raw)
    mock(direct_vm, raw=raw)
    contract.route(key)
    assert contract.get_job(key)["state"] == "REJECTED"
    assert contract.get_job(key)["terminal_reason"] == reason


def test_malformed_ai_aborts_without_consuming_attempt(contract, direct_vm, direct_alice):
    key = submit(contract, direct_alice)
    mock(direct_vm, output={"topic": "MODALITY", "confidence": 1})
    with direct_vm.expect_revert("[LLM_ERROR] malformed topic"):
        contract.route(key)
    assert contract.get_job(key)["state"] == "SUBMITTED" and contract.get_job(key)["attempts"] == 0


def test_expire_before_deadline_rejected(contract, direct_vm, direct_alice):
    key = submit(contract, direct_alice)
    with direct_vm.expect_revert("not expirable"):
        contract.expire(key)


def test_invalid_inputs_and_native_value(contract, direct_vm, direct_alice):
    with direct_vm.expect_revert("invalid lane"):
        contract.enroll("FAKE")
    with direct_vm.expect_revert("invalid source or deadline"):
        contract.submit("x", 2119, "a" * 63, START + 3600)
    key = routed(contract, direct_vm, direct_alice)
    contract.enroll("MODALITY")
    with direct_vm.expect_revert("invalid lease duration"):
        contract.claim("MODALITY", 301)
    direct_vm.value = 1
    with direct_vm.expect_revert("native value not accepted"):
        contract.expire(key)


def test_duplicate_and_creator_limit(contract, direct_vm, direct_alice):
    submit(contract, direct_alice)
    with direct_vm.expect_revert("duplicate or creator limit"):
        submit(contract, direct_alice)
    for index in range(15):
        submit(contract, direct_alice, "job" + str(index))
    with direct_vm.expect_revert("duplicate or creator limit"):
        submit(contract, direct_alice, "overflow")


def test_event_root_chain_preserves_history(contract, direct_vm, direct_alice, helpers):
    routed(contract, direct_vm, direct_alice)
    first, second = contract.get_event(0), contract.get_event(1)
    assert first["root"] == helpers["digest"]({k: v for k, v in first.items() if k != "root"})
    assert second["previous"] == first["root"]
    assert second["root"] == helpers["digest"]({k: v for k, v in second.items() if k != "root"})


def test_prune_bounded_to_sixteen_entries(contract, direct_vm, direct_alice, direct_bob):
    for index in range(16):
        routed(contract, direct_vm, direct_alice, "item" + str(index))
    direct_vm.sender = direct_bob
    last = routed(contract, direct_vm, direct_bob, "last")
    warp(direct_vm, 3600)
    contract.prune("MODALITY")
    assert contract.get_lane("MODALITY")["head"] == 16
    assert contract.get_job(last)["state"] == "WAITING"
    contract.prune("MODALITY")
    assert contract.get_lane("MODALITY")["head"] == 17
    assert contract.get_job(last)["state"] == "DEAD"


def test_transient_fetch_can_recover_without_changing_spec(contract, direct_vm, direct_alice):
    key = submit(contract, direct_alice)
    original = contract.get_job(key)["spec_root"]
    mock(direct_vm, status=503)
    contract.route(key)
    assert contract.get_job(key)["state"] == "SUBMITTED"
    mock(direct_vm)
    contract.route(key)
    assert contract.get_job(key)["state"] == "WAITING"
    assert contract.get_job(key)["spec_root"] == original
    assert contract.get_event(1)["details"]["report"]["outcome"] == "UNAVAILABLE"


def test_deadline_blocks_new_routing_and_active_receipt(contract, direct_vm, direct_alice):
    key = submit(contract, direct_alice, deadline=60)
    warp(direct_vm, 60)
    mock(direct_vm)
    with direct_vm.expect_revert("routing closed"):
        contract.route(key)


def test_equivalence_requires_all_material_fields(helpers):
    report = {"binding": {"job": "a"}, "hash": "h", "http": 200, "bytes": 400,
              "topic": "NAMES", "outcome": "ROUTED", "reason": "PRIMARY_TOPIC"}
    assert helpers["equivalent"](report, dict(report))
    for field in report:
        changed = dict(report)
        changed[field] = "changed"
        assert not helpers["equivalent"](report, changed)
    for value in ({"topic": "FAKE"}, {"topic": True}, {"topic": "NAMES", "score": 9}, [], "invalid"):
        assert helpers["parse_topic"](value) is None
