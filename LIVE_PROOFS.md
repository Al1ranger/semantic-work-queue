# Proof matrix

Experimental StudioNet deployment verified October 8–9, 2026. No production audit
or unanimity claim. Contract source is unchanged from published commit
`eda0f8759d8d958c79d0270f949e7df48d06f6c9`.

Contract: [0x8983539344F0E03D459C969bACDd25c560EfD32d](https://explorer-studio.genlayer.com/address/0x8983539344F0E03D459C969bACDd25c560EfD32d).
Normalized deployed source SHA-256:
`a80ed0ece2d033c94c2c28c9746b95d62a01a25f2d83496c4c50113129ba6896`.
Source equality normalizes CRLF and final newline only, never source evidence.
Dedicated encrypted gasless test wallet: `0x7a413BB4AB62E31d62d4cD9efC8C8a8Dae37FB42`.
No funds moved and no keys exported.

## Finalized successful receipts

Every entry below was checked for FINALIZED, leader SUCCESS and MAJORITY_AGREE.
Network quorum is not unanimity; some validator receipts contained errors.

| Stage | Transaction | Verified outcome |
| --- | --- | --- |
| Deployment | [0xbeae…ce76](https://explorer-studio.genlayer.com/tx/0xbeae0b6b0d74ed276b67c7daa32d17bb9400b826ed2e86eb445fd752df1ace76) | Matching published source; recovered from wallet history without resending |
| Submit normative-live | [0x1eb7…73af](https://explorer-studio.genlayer.com/tx/0x1eb78e0e0e7d9317c0f802121440c1c26175f918e2a9d82f2736d6904e9073af) | Bound SUBMITTED definition, independently checked root and job key |
| Independently route RFC 2119 | [0x61ff…dd5c](https://explorer-studio.genlayer.com/tx/0x61ff51bc94dc6a43b3030fdbaabac51392d6c015fc034e38ea1fcab285e3dd5c) | WAITING; MODALITY lane, ticket 0; full raw hash, report root and binding checked |
| Enroll authenticated worker | [0x0008…fa9d](https://explorer-studio.genlayer.com/tx/0x000895ef6116194b7b806f1ca0a43520d321e8173d47f75ca51fdfaa577efa9d) | MODALITY enrollment executed |
| Claim FIFO head | [0x320a…c7e0](https://explorer-studio.genlayer.com/tx/0x320ae3f4e71a3f6b042761659dc086da08fa46c8bc2ca37e3058fee8d8bac7e0) | LEASED; generation 1, same authenticated worker; token/root/bindings checked |
| Delivery acknowledgement | [0xf81a…1a19](https://explorer-studio.genlayer.com/tx/0xf81adfcad0772c53d7e4e18bf9dfac8138f3c07dc12d04d8cc733ecf50b01a19) | ACKED; MODALITY head=tail=1, no head job; delivery receipt only |
| Submit wrong-commitment negative job | [0x142a…8d18](https://explorer-studio.genlayer.com/tx/0x142af7b69a943baccbb6af5b68cecae0722bae595af6e167e144a14c98048d18) | SUBMITTED; this receipt does not prove hash rejection |
| Expire unresolved job after deadline | [0xdd44…de87](https://explorer-studio.genlayer.com/tx/0xdd445ed651dcc0d02527b2df563b632338eb63c1758aec51597c29e52f99de87) | DEAD, reason DEADLINE; definition root and job binding independently checked; no lane insertion |

Normal job key: `4f9c77be98aaf0b9e98225902622ab7eb95ea4332cf578d03f4e896e05201425`.
Negative job key: `0b1242857aec7f7302bfc3c45b9c873f06e5482e5ca16d4bb26df1a9324e8354`.

Independent public source fetches returned HTTP 200:

| Source | Raw bytes | SHA-256 | Live observation |
| --- | ---: | --- | --- |
| RFC 2119 | 4723 | 3c2ceb7bfc84cd34720f4a5271338ab9d8280d34bdd1eb250c64306202f2ed8b | MODALITY, exact byte/hash match |
| RFC 2606 | 8008 | b6869c8984701701bc2e6973b6ffc750d497f845cc1a65a106e9301590a13ab0 | Independently fetched only; routing not run |

## Local verification and scope

GenVM lint and SDK validation pass: 11 methods, 4 views, 7 writes, no constructor
parameters; informational newer-runner notice only. 30 direct tests pass with
mocked HTTP/AI and leader-only execution. One mocked Node transport test passes;
it sends no transaction. These are not distributed disagreement experiments.

| Scenario | Direct | Live |
| --- | --- | --- |
| Fetched semantic topic selects actual FIFO lane | PASS | PASS: RFC 2119 -> MODALITY ticket 0 |
| Wrong commitment rejects without queue insertion | PASS | Not run; negative submission only |
| UNKNOWN quarantines without queue insertion | PASS | Not run |
| FIFO prevents bypassing live head | PASS | Not run |
| Worker/lane identity and acknowledgement binding | PASS | PASS: enrolled worker claimed and ACKed bound lease |
| Expired lease redelivery fences previous ACK | PASS | Not run |
| Third expired lease permissionlessly dead-letters | PASS | Not run |
| Unresolved deadline expiry | PASS | PASS: tampered-live -> DEAD / DEADLINE |
| Bounded prune | PASS | Not run |
| Exact report mismatch rejects equivalence | PASS helper | Distributed disagreement not run |

## Recovery and excluded attempts

Initial deployment CLI transport returned an unknown outcome. Wallet history
identified nonce 125 and the finalized successful deployment; it was not resent.
A sandboxed submit attempt could not access the OS keyring and did not broadcast
(history/nonce checked). Signing used the native encrypted keystore thereafter.

On continuation, one CLI command stopped before loading its relative-path signer.
The correctly scoped negative route then failed during the read-only nonce lookup,
before broadcast. No transaction is claimed for either failed command. Public
DNS subsequently returned ENOTFOUND; permission-review checks also timed out.
After native RPC connectivity recovered, permissionless expiry finalized
successfully. An independent read verified DEAD / DEADLINE and intact definition
bindings. This is a deadline-closure proof, not a semantic hash-rejection proof.
No redelivery or stale-token rejection live proof is claimed.
