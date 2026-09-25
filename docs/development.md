# Development guide

Engineering and soundness rules live in [`AGENTS.md`](../AGENTS.md). This page covers setting up, running the same checks as CI, and the hooks that guard the research ledger. A passing check is implementation evidence. It never raises an evidence tier.

## Set up

Python 3.11 or newer:

```text
python -m venv .venv

# Windows PowerShell
.venv/Scripts/python -m pip install -e ".[dev]"

# POSIX shell
.venv/bin/python -m pip install -e ".[dev]"
```

Optional extras:

- `dev`: the test, lint, type, and build tools.
- `mujoco`: the untrusted simulation falsification backend. It is never imported by the core package ([backends](architecture/backends.md)).

The runtime `dependencies` list is empty by policy.

## Checks run by CI

These mirror `.github/workflows/ci.yml`. Run them from the repository root.

```text
python -m pytest --basetemp=.pytest-basetemp
python -m ruff check src tests scripts benchmarks/proof-verification/scripts
python -m ruff format --check src tests scripts benchmarks/proof-verification/scripts
python -m mypy src/robocert
python scripts/check_ledger.py
python scripts/check_report_language.py research/reports
python benchmarks/proof-verification/scripts/check_rc002_run.py --all-runs
python -m pip check
python -m build --no-isolation
python scripts/check_distribution.py dist --work-dir .package-smoke
```

On Windows, the in-project `--basetemp` is the supported fallback when the system temporary directory denies pytest cleanup. It changes only test scratch space, not test semantics.

## Formal developments

CI also builds the Lean development and runs `scripts/check_lean_axioms.py` and `scripts/check_lean_conformance.py --require-lean`. It re-checks the Rocq and Isabelle attestations with `scripts/check_attestations.py --require rocq` and `--require isabelle`.

Locally, `python scripts/check_attestations.py` reports whether the recorded digests match. It reports a missing toolchain as unavailable, which is not a pass. Toolchain pins and scope are in [`formal/README.md`](../formal/README.md).

Files whose digests are pinned in `formal/attestations/` must not be edited casually. Any change to one needs a fresh CI run on the exact commit and a reviewed transcription of the attestation.

## Ledger and report hooks

`.claude/settings.json` runs:

- `scripts/check_ledger.py` after every edit. It checks monotonicity, the dependency DAG, orphan references, the referee gate, and the history gate on `research/CLAIMS.md`.
- `scripts/check_report_language.py` before every edit. It blocks overclaiming language in `research/reports/` unless an E2-or-higher claim backs it.

The hooks are designed not to be bypassed. Tier rules are in [`research/README.md`](../research/README.md).

## Frozen artifacts

Everything under `benchmarks/proof-verification/runs/` is frozen and hash-validated. Repairs go into a new run id, never into an existing run.
