# RCMPVB-20260821-CROSS-X-RUN001

This is a single-item, verification-only RC-002 cross-provider run under
RC-MPVB v0.2.0 and the v2 cross-verification protocol. It is not a scored
dataset run and supplies no model ranking.

Current state: `stopped_substantive_and_claude_audits_blocked`.

The original candidate proofs remain unchanged. Run-local P1/P2 labels were
assigned by a cryptographic random coin flip. The mapping is stored outside the
repository and must not be disclosed until both blind audits are frozen.

Both theorem-only ledgers and the union ledger are frozen. The two Codex blind
audits found substantive proof omissions. Claude blind-audit requests were
blocked before inference by the provider session limit. See `reconciliation.md`
and `outputs/claude-audit-attempts.md`.

For the Codex ledger session, the frozen prompt prohibited all tool use, but the
subagent API did not expose a hard-disable switch. This prompt-enforced condition
is recorded in `metadata.yaml`; it must not be reported as platform-enforced
tool isolation.

Checkpoint evidence is recorded in `verification.md` and
`implementation-correspondence.md`. The correspondence status retains the prior
exact 108-instance audit and current regression passes, while explicitly keeping
the absence of an all-parameter symbolic replay artifact as a limitation.

RC-002 remains E1. This run is a failed frozen run and must never be interpreted
as E2. Repairs require a new run id and the complete protocol.
