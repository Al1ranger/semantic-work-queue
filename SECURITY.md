# Experimental security scope

Not audited production software. Report issues privately before exploitation.

- No secrets, assets, credential exports, upgrade admin or arbitrary URL fetches.
- Caller hash only commits bytes. The contract fetches and semantically evaluates
  the complete body; bad hash/identity/UTF-8/size never enters a lane.
- Exact comparison includes every consequential topic, hash, byte count, outcome
  and binding. UNKNOWN quarantines; malformed AI output forces disagreement.
- Job keys are deployment/creator/id scoped. A bad submission cannot reserve an
  RFC globally. Every retry report is preserved in the append-only event history.
- Enrolled lane membership plus active bound lease token and authenticated sender
  are all required to ACK. Tokens are public fencing identifiers, not secrets.
- Stale acknowledgements, wrong workers, cross-job tokens and terminal resets fail.
- Permissionless deadline expiry and prune eliminate creator/worker vetoes.
- Semantic consensus can be wrong. Exact AI agreement may fail and require network
  rotation; do not weaken it to format-only validation. Public source compromise,
  prompt injection, censorship and Sybil queue spam remain risks. Per-creator
  job limits do not provide Sybil resistance. No priority/fairness across submitters.
- Worker ACK is self-reported receipt only: no claim of verified downstream work.
- Same RFC Editor publisher, NOT multiple independent authorities. Hash commitments
  do not prove publisher honesty or freshness of document claims.
