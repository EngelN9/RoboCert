# Certificate soundness audit — pre-repair snapshot

Date: 2026-08-24  
Auditor: fresh read-only Codex context using the repository-local
`certificate-soundness-audit` skill  
Audit target: live workspace on branch `agent/phase-0-formal-core`, committed
HEAD `42aa49ac8c7ad13a8d4893285e6ed2613015bef8`  
Auditor edits: none

## Assessment

Overall: `FAIL` as an internally consistent final delivery and `BLOCKED` for any
pose-tolerance certification. The safety boundary itself passed: the production
registry was empty, public `certify` and `check` returned `UNKNOWN`, and no public
path could produce `CERTIFIED_FEASIBLE` or `CERTIFIED_INFEASIBLE`.

The strongest supported runtime status was `UNKNOWN`. RC-003's rational counterexample-backed refutation
was research evidence (`EX`), not a runtime `COUNTEREXAMPLE` result.

## Passed boundaries

- Production registry quarantine and missing-family fail-closed behavior.
- Public `certify` and `check` unconditional `UNKNOWN` behavior.
- Certified-status promotion only from a `CheckedCertificate`.
- Search/check failure does not imply certified infeasibility.
- RUN001 manifest integrity and exact RC-003 counterexample recomputation.
- Current regression, type, lint, ledger, and run-validator evidence, while
  explicitly not treating those checks as mathematical proof.

## Failed or blocked gates

- RUN001 cannot support RC-002 E2: the independent Codex audits found omitted
  bounded-existential transport, incomplete rational syntax/scope, and a missing
  P2 sign bridge.
- Claude P1/P2 audits were blocked before inference by HTTP 429.
- The RC-002 corrigendum has no project-owner attestation or new frozen run.
- RC-005 remains E0; it has no project-owner E1 attestation, hostile/naive
  referee evidence, isolated-step reviews, or negation control.
- Schema `0.2.0`, its family payload, builder, reconstruction path, model hash,
  production checker, and correspondence replay are correctly absent.
- The live workspace is largely untracked, so no Git revision reproduces it.
  This remains blocked because the task explicitly forbids committing.

## Concrete repair findings

1. `examples/README.md` and public CLI help still described certification even
   though the public gate was closed.
2. RUN001 implementation-correspondence prose described a checker as currently
   registered after its quarantine.
3. The historical builder allowed sign-flipped effective link lengths but
   serialized an assumption that both were positive.
4. The planar position-Jacobian determinant margin was labeled dimensionless;
   its unit is squared length. RC-005 likewise needed to state the unit of
   `epsilon` explicitly.

These concrete findings were repaired after this snapshot. A separate fresh
post-repair audit is required; this report must not be interpreted as passing
that later state.
