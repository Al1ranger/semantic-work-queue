# Consensus boundary

submit(RFC number, raw SHA-256, deadline) -> independent complete-body GET ->
independent AI primary-topic inference -> exact report equivalence -> actual FIFO
lane insertion -> enrolled worker leases -> fenced delivery acknowledgement.

The caller cannot provide a document, routing topic, priority, worker or confidence.
Commitment equality alone does not route: substantive topic classification controls
which lane receives the job. All validators refetch the body and rerun the task.
The report binds deployment, creator/id, policy, source, attempt and observer time.
UNKNOWN quarantines instead of routing. Failed network consensus aborts the write,
not a fake CONFLICTED record. An individual validator's mismatch rejects its
equivalence vote; the network uses quorum, not unanimity. A deadline always
permits permissionless terminal closure.

## Architectural difference

This is a work-queue runtime: independent FIFO heads/tails, worker memberships,
fenced lease generations, expired-lease redelivery, bounded pruning and dead letters.
It is not a graph update, certificate consumer, documentation cover optimizer,
score-based selection, source tariff compiler or asset settlement.

## State machine

SUBMITTED -> WAITING -> LEASED -> ACKED
SUBMITTED -> REJECTED / QUARANTINED
SUBMITTED / WAITING / LEASED -> DEAD after deadline
LEASED -> LEASED with a new token after expiry, maximum three generations
Third expired lease -> DEAD via permissionless prune

## Limits and responsibility

RFC-only adapter; four immutable categories, full UTF-8 bodies <=16 KiB. Source
bytes may not be truncated. Epoch time is from the transaction message. Deadline
limits routing and receipt validity; queue jobs describe the committed document
snapshot, not the latest source or external real-world facts. An ACK records
delivery receipt, never proves service execution. The worker can reread the URL
and verify the stored raw hash. No native value, tokens, budgets or transfers.

Membership is permissionless lane opt-in, NOT professional qualification. Workers
can delay a lane by leasing its head; max three 300-second leases and permissionless
pruning bound this obstruction per job. FIFO is consensus routing order, not
submission order. Bounded prune advances <=16 entries/call; repeat if needed.
