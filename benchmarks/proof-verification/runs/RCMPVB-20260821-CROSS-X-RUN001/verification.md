# First-checkpoint verification

The run intentionally stops before union-ledger construction and blind audits.

| Check | Result |
|---|---|
| Pre-run baseline | `82 passed` |
| `python scripts/check_ledger.py` | PASS — 2 entries |
| Full `pytest -q` after adding the run-validator regression | PASS — `83 passed` |
| `ruff check src tests scripts benchmarks/proof-verification/scripts` | PASS |
| `mypy src/robocert` | PASS — 11 source files |
| `check_rc002_run.py` | PASS after manifest refresh |

The increase from 82 to 83 is the newly added deterministic run-artifact
validator regression test; it is not additional mathematical evidence for
RC-002. The Codex Session L output reports `NO COUNTEREXAMPLE FOUND`, which is
also not a certification result.

Tool isolation for Codex was prompt-enforced because the subagent API exposed no
hard-disable switch. This deviation is recorded in `metadata.yaml` and the
ledger-output metadata rather than being presented as platform-enforced
`no_tools`.
