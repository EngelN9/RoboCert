# Counterexample and simulation implementation audit — 2026-09-07

## Follow-up repair status

The initial findings below are retained as the pre-repair record. On resumption,
all three identified hardening obligations were repaired:

- Model-hash type validation now precedes evidence construction. A planted
  constructor test fails if malformed input reaches that boundary.
- Direct MuJoCo q/control values are normalized and checked for finiteness before
  engine state changes. Tests confirm positions, velocities and controls are
  unchanged after rejection. Invalid timestep overrides are refused before model
  loading, tested using a nonexistent model path.
- The simulation source guard now covers refutation imports and promotion symbols,
  with planted import tests. Sampling also rejects malformed axis shapes, incorrect
  sample counts, and non-finite, out-of-region or wrong-dimensional generated points
  before invoking the backend.

The original PARTIAL assessment below describes the earlier checkpoint. The
follow-up implementation checks cover the requested repairs; formal-tool availability
and model-correspondence limitations continue to apply. No research-tier promotion
or production checker registration results from these changes.

## Audit target and conventions

Target: the local working-tree refutation API, result v0.2 schema migration,
and optional MuJoCo search layer based on commit
`0531db56736b4777b9323de03a60c4b684dea486`. The working tree contains uncommitted
changes, including work from other sessions; this commit alone does not reproduce
the audited implementation. This is an implementation review, not an independent
mathematical referee verdict or a release approval.

For a serialized claim `forall z in D: Phi(z)`, the proposed refutation is a
complete rational assignment `a` with `a in D` and `Phi(a) = false`. All quantified
blocks must be universal. Open and closed bounds retain their declared meanings;
the whole Boolean formula is evaluated with Fraction arithmetic. A failing point
for a mixed or existential prefix is insufficient. The result refers to the
serialized formula and assumptions; coordinate, unit, and physical-model
correspondence remain caller obligations.

## Status summary and dependency graph

RC-002 remains E1; RC-005 and RC-006 remain E0; RC-003 remains EX. This review
changes none of their ledger fields. RUN001 remains stopped, with no new blind
audit or adjudication. RUN002 requires the owner's reading decision on the
corrigendum. No research tier or production checker registration follows from this
record.

Follow-up verification: **406 passed, 11 skipped** using
`-m pytest -q --basetemp .pytest-basetemp/resume-final`. The first full follow-up
run identified a report-index language-guard failure; replacing the index wording
with "refutation API review" resolved it. Ruff, strict mypy, the ledger and RUN001
validators, and diff whitespace checks pass. The rebuilt wheel and sdist in
`dist/resume-20260907` passed `scripts/check_distribution.py` with a clean wheel
installation using `.package-smoke/resume-20260907`. The production registry remains
empty and the core import probe leaves MuJoCo unloaded. Attestation still reports
policy REJECTED for unavailable Rocq/Isabelle evidence; live Lean conformance is
unavailable. The 11 skipped tests are not passes.

Runtime dependency: validated Claim and Rational assignment -> universal-prefix
and domain guards -> whole-formula evaluator -> CheckedCounterexample -> result
factory. Simulation -> candidate assignment is an optional input path. The
production certificate registry is empty. The generic evaluator and Python runtime
remain trusted implementation dependencies; the formal checker models do not
establish correspondence for this new refutation implementation.

## Evidence inventory and results

Fresh local checks on 2026-09-07 used Python 3.14.6 and MuJoCo 3.12.0 on Windows.

| Check | Observed result | Interpretation |
| --- | --- | --- |
| Full pytest suite | 390 passed, 11 skipped | Includes installed MuJoCo tests; skips are unavailable Lean-toolchain tests |
| Ruff, src/tests/scripts/benchmark scripts | Exit 0 | Static lint pass |
| Strict mypy | Exit 0; 23 source files | Type-check pass |
| Research ledger validator | Exit 0; 6 entries | Ledger structure resolves |
| RC-002 run validator | Exit 0 | Existing RUN001 artifacts, isolation rules and SHA-256 manifest validate |
| Attestation check | Exit 0; policy REJECTED | Recorded Lean entry matches artifact/statement digests; Rocq and Isabelle unavailable |
| Lean conformance | Exit 0; Python 18 vectors, 8 accepted/10 rejected | Live Lean comparison unavailable; no installed pinned v4.33.1 toolchain |
| Core import probe | Empty production registry; MuJoCo absent from sys.modules | Import does not activate simulation or register a checker |
| Historical result schema comparison | Byte-for-byte equal to HEAD's original schema | v0.1 contract preserved |
| Distribution build and validation | Exit 0; wheel and sdist inspected, clean wheel installation passed | Both result schemas packaged and loadable |
| Report language and diff whitespace checks | Exit 0 | Documentation checks pass |

The historical schema SHA-256 is
`494bfdecf2dcbca59f9339fd2569f5b637a6ef0d0c7fc149e7479129afcc2fc4`.
Commands returning zero for unavailable formal tools must not be interpreted as
kernel acceptance.

## Soundness findings and required repairs

| Step or obligation | Evidence and verdict | Severity / disposition |
| --- | --- | --- |
| Result wire identity | The previous draft tightened the v0.1 contract in place. Current factories emit v0.2, require a counterexample field, and package the original v0.1 schema separately. Claims and embedded certificates stay v0.1. | Substantive compatibility defect repaired |
| Pointwise refutation rule | Source guards and tests cover universal blocks, domain endpoints, malformed assignments, and Boolean formulas. Scope is the serialized claim. | Tested implementation; no general correctness proof asserted |
| Malformed model hash | Validation occurs in RefutationReport after CheckedCounterexample construction on the accepting branch. It raises without returning an accepted report. | Substantive gap against the requested pre-construction validation invariant; validate the hash before evidence construction |
| Simulation numeric records | Record constructors reject non-finite numeric values; threshold constructors require finite nonnegative limits. Normal search sampling checks finite bounds and generated values. | Tested supported paths |
| Direct MuJoCo input | set_configuration checks lengths but not finite q/control values before writing engine state. load_model applies a timestep before provenance validation rejects non-finite values. | Substantive remaining hardening: validate inputs before engine mutation |
| Structural isolation regression guard | Current simulation source does not import refutation. The forbidden-symbol test list omits robocert.refutation and its promotion symbols. | Substantive test coverage gap: add explicit prohibition and planted controls |
| Model provenance | Entry-file hash and declared external references are recorded. Referenced asset contents are not hashed recursively. | Reproducibility limitation; preserve the asset tree and backend version |

Schema validation checks structure, not truth. Historical witnessless documents
must not be automatically promoted. Full replay requires the supplied Claim and
model identity together with the witness; the result object is not a standalone
physical-model validation artifact.

## Negative results and where to attack

No new search for a mathematical counterexample was performed for this report.
No runtime counterexample result is published by this audit. The tests use
synthetic claims and simulation fixtures; finding no sampled violation supplies
no universal evidence. Prior research failures remain in
[ATTEMPTS.md](../ATTEMPTS.md), unchanged by this documentation update.

Prioritize malformed-input validation before evidence or engine-state mutation,
then adversarial tests for the refutation import boundary. Further review should
attack sampling/helper failure paths and replay with external MJCF assets. Passing
the existing suite does not discharge these missing obligations.

## Verification methodology and reproducibility

Run from the repository root using `.venv/Scripts/python.exe`:

```text
-m pytest -q --basetemp C:\Users\User\AppData\Local\Temp\robocert-audit-20260907
-m ruff check src tests scripts benchmarks/proof-verification/scripts
-m mypy
scripts/check_ledger.py
benchmarks/proof-verification/scripts/check_rc002_run.py
scripts/check_attestations.py
scripts/check_lean_conformance.py
-m build --no-isolation --outdir dist/audit-20260907
scripts/check_distribution.py dist/audit-20260907 --work-dir .package-smoke/audit-20260907
scripts/check_report_language.py research/reports/2026-09-07-counterexample-simulation-audit.md
```

These are checks of the integrated local tree. No fresh cross-provider referee
session or planted mathematical-defect detection rate was measured. The historical
schema was compared to `git show HEAD:schemas/result.schema.json` using raw bytes.

## Status assessment and disclosure

Assessment: PARTIAL implementation coverage; the requested hardening slice is
not yet complete. Formal attestation remains BLOCKED by unavailable evidence,
with the runtime attestation policy retaining REJECTED. This audit supports no
new claim promotion or certified robot result.

Codex assisted with source inspection, documentation and test execution. The
review shares context with implementation work and is not an independent blind
review. Existing user changes were preserved; no commit, push, attestation
transcription, or ledger-tier change was performed.
