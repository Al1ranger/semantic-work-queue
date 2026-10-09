# SemanticWorkQueue

Consensus-grounded semantic dispatch into leased FIFO work lanes.

## Problem and why GenLayer

Workers need shared ordering and crash recovery, but an ordinary queue cannot
independently interpret an external document before choosing its processing lane.
Here validators fetch and semantically classify complete primary-source documents;
that consequential result selects an actual onchain FIFO lane. Mere title matching,
caller summaries and a locally computed graph transition cannot determine routing.

```text
RFC identity + raw commitment -> independent full-body acquisition
 -> independently inferred primary topic -> exact consensus report
 -> NAMES / ADDRESSES / MODALITY / GENERAL FIFO
 -> enrolled worker lease -> ACK, redelivery or dead letter
```

No caller-supplied topic, score, summary, worker or priority. Not a certificate,
graph or service-completion proof. RFC-only concrete adapter; reusable queue
runtime for source-grounded document-processing workers.

## State and consensus

```text
SUBMITTED -> WAITING -> LEASED -> ACKED
          -> REJECTED / QUARANTINED
          -> DEAD after deadline or exhausted fetch retries
LEASED -> new fenced lease after expiry -> DEAD after third expired lease
```

Leader and validators independently fetch full RFC Editor bodies, recompute raw
SHA-256, enforce the exact RFC header/UTF-8/size and infer primary purpose from
the full content. Exact equality covers the whole decision-bearing report. No
confidence tolerance. UNKNOWN quarantines; disagreement applies no write.
Malformed AI response is not counted as successful consensus. Three unavailable
acquisitions dead-letter a job; all unresolved jobs can expire at deadline.

## Queue safety and liveness

- Actual per-lane FIFO indexes; only its head may be claimed.
- Workers enroll as their authenticated address in each desired lane.
- 30–300 second leases, max three generations, bounded by job deadline.
- ACK requires the same worker, job and current lease token before expiry.
- Public tokens fence replay; possession alone gives no authority.
- Anyone can prune expired/exhausted heads or expire unresolved jobs.
- No owner-controlled finalization, terminal resets or unilateral cancellation.
- ACK proves receipt acknowledgement only, not completion of external service.

## Install, test and deploy

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/genvm-lint check contracts/SemanticWorkQueue.py --json
.venv/Scripts/python -m pytest tests -q
npm ci
npm install -g genlayer@0.39.2
genlayer network set studionet
genlayer account use YOUR_ENCRYPTED_TEST_KEYSTORE
genlayer account unlock
genlayer deploy --contract contracts/SemanticWorkQueue.py
```

Concrete runner pinned. Direct tests mock HTTP/AI and run the leader only; helper
equivalence checks are not distributed disagreement experiments. Windows cleanup
defers only gltest's open temporary message-file unlink, never test assertions.

## Example workflow

Fetch [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119.txt) raw bytes and calculate
their SHA-256 locally; then submit the commitment. Validators must still refetch
and infer its purpose independently. RFC 2119 defines normative requirement
words; [RFC 2606](https://www.rfc-editor.org/rfc/rfc2606.txt) reserves DNS names.
These are expected demo topics, not caller-supplied routing instructions.

```powershell
$deadline=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()+7200
genlayer write ADDRESS submit --args demo 2119 RAW_SHA256 $deadline
node scripts/inspect.mjs ADDRESS CREATOR demo
genlayer write ADDRESS route --args JOB_KEY
genlayer write ADDRESS enroll --args MODALITY
genlayer write ADDRESS claim --args MODALITY 300
node scripts/inspect.mjs ADDRESS CREATOR demo
genlayer write ADDRESS acknowledge --args JOB_KEY CURRENT_TOKEN
```

Use SDK reads for address/string typing. The inspect script validates definition,
source report and lease roots/bindings and returns safe metadata. Expired head:
`genlayer write ADDRESS prune --args MODALITY`. Unresolved deadline:
`genlayer write ADDRESS expire --args JOB_KEY`.

`scripts/check.mjs --success HASH` checks FINALIZED, leader SUCCESS and majority
agreement; `--error HASH EXPECTED_TEXT` validates execution errors. `--source ADDRESS`
compares Explorer source. Never treat a finalized error or CLI banner as success.

Optional Windows public RPC fallback: prepend
`--require ./scripts/windows_read_transport.cjs` to Node read commands. A separate
`windows_broadcast_once.cjs` opt-in forwards only already-signed StudioNet payloads
once, caching success and failure. Never blindly resend an unknown broadcast.
Signing remains in an encrypted keystore. StudioNet is gasless; no transfers.

See [architecture](docs/architecture.md), [security](SECURITY.md) and
[proof matrix](LIVE_PROOFS.md). No production audit, unique invention claim,
steward acceptance or points guaranteed.
