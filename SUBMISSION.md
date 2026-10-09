# Submission text

Contribution Type: Builder -> Intelligent Contracts
Contribution Date: 10/09/2026

Title: SemanticWorkQueue — Source-Grounded Dispatch and Fenced Leases

Notes / Description:

SemanticWorkQueue is a reusable GenLayer source-grounded dispatch runtime. Jobs bind an RFC, raw SHA-256 commitment and deadline; callers cannot choose topic, priority or worker. Leader and validators independently fetch the complete document, verify identity and bytes, and infer its primary substantive topic. Exact report equivalence determines insertion into a real FIFO lane. Enrolled workers claim the head through 30–300 second leases. ACK requires the authenticated worker and current job-bound fencing token. Expired generations can be reclaimed; stale tokens cannot acknowledge delivery. Permissionless expiry and bounded pruning prevent creator or worker vetoes; three expired leases dead-letter a job. UNKNOWN quarantines without routing. StudioNet proofs show RFC 2119 routed to MODALITY, claimed and ACKed, plus deadline expiry of an unresolved job. Deployed source matches GitHub; 30 mocked direct tests pass. ACK is receipt, not verified service completion.

Evidence:

- https://github.com/Al1ranger/semantic-work-queue
- https://github.com/Al1ranger/semantic-work-queue/blob/main/contracts/SemanticWorkQueue.py
- https://github.com/Al1ranger/semantic-work-queue/blob/main/README.md
- https://github.com/Al1ranger/semantic-work-queue/blob/main/LIVE_PROOFS.md
- https://explorer-studio.genlayer.com/address/0x8983539344F0E03D459C969bACDd25c560EfD32d
- https://explorer-studio.genlayer.com/tx/0xbeae0b6b0d74ed276b67c7daa32d17bb9400b826ed2e86eb445fd752df1ace76
- https://explorer-studio.genlayer.com/tx/0x61ff51bc94dc6a43b3030fdbaabac51392d6c015fc034e38ea1fcab285e3dd5c
- https://explorer-studio.genlayer.com/tx/0x320ae3f4e71a3f6b042761659dc086da08fa46c8bc2ca37e3058fee8d8bac7e0
- https://explorer-studio.genlayer.com/tx/0xf81adfcad0772c53d7e4e18bf9dfac8138f3c07dc12d04d8cc733ecf50b01a19
- https://explorer-studio.genlayer.com/tx/0xdd445ed651dcc0d02527b2df563b632338eb63c1758aec51597c29e52f99de87

Not production-audited; no acceptance or points guarantee. Do not claim the
negative rejection or expired-lease scenarios were executed live. They pass only
in mocked direct tests; the negative job submission itself is not a rejection proof.
