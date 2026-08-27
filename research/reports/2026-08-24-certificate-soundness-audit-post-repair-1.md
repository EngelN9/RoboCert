# Certificate soundness audit — post-repair confirmation 1

Date: 2026-08-24  
Auditor: second fresh read-only Codex context using the repository-local
`certificate-soundness-audit` skill  
Audit target: live workspace on branch `agent/phase-0-formal-core`, committed
HEAD `42aa49ac8c7ad13a8d4893285e6ed2613015bef8`  
Auditor edits: none

## Assessment

The production safety boundary passed. The strongest supported public runtime
result remained `UNKNOWN`; RC-003's rational counterexample-backed refutation remained research evidence
(`EX`), not a runtime `COUNTEREXAMPLE`.

The auditor confirmed:

- immutable empty production registry;
- unconditional public `certify`/`check` `UNKNOWN` behavior;
- exact quantifier/domain checking and checked-certificate-only promotion;
- correct failed-run disposition for RC-002 RUN001;
- exact RC-003 counterexample;
- RC-005 correctly held at E0 with squared-length `epsilon` units;
- repaired historical link-length assumption and Jacobian margin unit;
- 121 tests, Ruff, strict mypy, ledger validation, RUN001 validation, and a clean
  wheel smoke test, all treated as engineering evidence rather than proof.

Certification and reproducibility remained `BLOCKED`: RC-002/RC-005 had not
passed their human and E2 gates, and the no-commit instruction meant HEAD could
not identify the largely untracked workspace.

## Residual consistency findings

The auditor found four non-certifying documentation/evidence inconsistencies:

1. gate-record test counts and the sdist hash were stale after later edits;
2. global CLI help did not explain that `schema` legitimately returns exit 0;
3. a historical CLI report still called the refuted RC-003 route merely
   unimplemented; and
4. a historical builder docstring named a nonexistent four-chart helper.

These findings were repaired after this audit. A further fresh confirmation is
required before describing the current workspace as free of actionable concrete
FAIL findings.
