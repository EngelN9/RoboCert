# Reconciliation

Status: `STOPPED_SUBSTANTIVE`; RC-002 remains E1.

The Codex and Claude theorem-only ledgers were frozen and merged into
`outputs/ledger-union.md`. Two fresh Codex single-proof blind audits were then
frozen. Both found substantive omissions, so this run cannot support E2:

- P1 proves the central pointwise equivalence, but does not emit the requested
  bounded existential theorem and does not fully discharge the hypothesis/scope
  and rational-polynomial syntax obligations.
- P2 likewise omits the bounded existential and rational syntax conclusions in
  the frozen packet, and silently uses FK polynomials equal to the negatives of
  the frozen definitions without an explicit sign bridge.

The corresponding Claude P1/P2 audit requests were blocked before inference by
the provider session limit; see `outputs/claude-audit-attempts.md`. This external
block is not the reason for rejection: either Codex substantive finding already
prevents promotion under the frozen protocol.

No cross-proof adjudication, negation control, disagreement resolution, or E2
promotion was performed after the substantive stop. The defects must be repaired
in source proofs, then frozen and reviewed under a new run id. The private source
mapping for this run remains undisclosed.
