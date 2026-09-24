# RoboCert continuity handoff — 2026-09-07, updated through 2026-09-24

This file preserves the project context needed after the original repository-setup
session is deleted. It is a progress and continuation record, not a mathematical
review, proof, attestation, or release approval. The maintainer requested English
for subsequent communication on 2026-09-07.

## September 24 update — RC-004 repair and two E0 arguments

This section supersedes the older statements below that RC-004 and RC-006 have
no written arguments; it does not supersede their evidence gates. At inspection,
`refutation-and-simulation` had a clean working tree, was one local commit ahead
of the exact remote feature-branch head `23c5744`, and draft PR #3 targeted
`main`. That local commit, `f350551`, repairs RC-004 endpoint conversion: a
platform `tan`/float comparison could round outward, so supported exact-rational
limits now use rational Taylor enclosures, inward grid rounding, and the strict
principal-chart input range `[-31/10,31/10]`. Unsupported or too-narrow limits
reject rather than widen the domain.

- `research/proofs/rc004-joint-limit-inward-rounding.md` argues the subset
  relation on that supported chart, including endpoint enclosure, monotonicity,
  closed endpoints, excluded `+/-pi`, and the absence of periodic wrap coverage.
- `research/proofs/rc006-sos-verifier-correspondence.md` maps accepted typed
  certificates through shape, exact PSD, Gram expansion, equality pairing, and
  canonical polynomial identity. It is not a robot-property correspondence or
  a production checker authorization.
- Both ledger entries remain **E0**. No tier changed, no attestation changed,
  no checker was registered, and `refute`/`COUNTEREXAMPLE` was not wired into
  the CLI or generated reports. PR #3 remains draft. Owner E1 reads, fresh
  referee work, human adversarial review, formal re-attestation, local ACL
  repair, and the actual-endpoint universal-clearance decision remain blocked
  on the owner as described below.

Local evidence on 2026-09-24: the focused RC-004/RC-006 tests passed (71),
the full suite passed (420) with 11 Lean-conformance tests explicitly skipped
because the pinned Lean toolchain is not installed, and the simulation/boundary
subset passed (85) with the optional MuJoCo extra installed. Ruff lint/format,
strict mypy, the seven-entry ledger, report-language checks, frozen RC-002 run,
and wheel/sdist build plus clean wheel-install smoke passed. The attestation
record check passed its digest/policy checks but reported local Rocq and
Isabelle kernel reruns as **unavailable**, not as passes. These checks are
implementation evidence, not an owner read, proof promotion, or a certificate.
Fresh PR #3 exact-head CI remains a publication check, not a substitute for
those research and formal gates.

## September 15 update — work committed on its own branch, refutation defect repaired

This section supersedes the September 14 list "Owner decisions now blocking progress",
items 1, 3 and 4, which are now decided. Items 2 and 5 still stand. No tier changed, no
attestation was edited, and no checker was registered.

### Where the work is

- The formerly uncommitted working tree is committed on branch `refutation-and-simulation`,
  cut from `fbc9867`, and opened as a separate draft pull request **stacked on**
  `phase-0.5-formal-layer`, so its diff shows only this work and it cannot merge ahead of
  PR #2. It was deliberately **not** committed onto `phase-0.5-formal-layer` itself: PR #2's
  description states that the simulation, refutation and research-ledger changes are not
  part of it. PR #2 was not touched. Merge PR #2 first; GitHub then retargets the stacked
  PR to `main` if the `phase-0.5-formal-layer` branch is deleted on merge, and otherwise
  change its base to `main` by hand.
- Each intermediate commit was tested in an isolated worktree. All non-Lean tests passed at
  every commit. Ten Lean-conformance tests failed at each, and the same ten fail at
  `fbc9867`, which is CI-green, in a fresh worktree. A new worktree has no `formal/.lake`
  build cache and the generated Lean file does not elaborate there. That is an environment
  effect, not a defect in any commit.

### Defect found and repaired in `refute`

Reading `refute` against RC-007's guards found that it looked values up in the caller's
Mapping separately for the type check, domain check, evaluation, and recording. A mapping
returning different values on different reads could therefore pass the checks at one point
and have another, unchecked point recorded in an accepted `CheckedCounterexample`. It was
reproduced on the unrepaired code with q = 5, outside the domain, recorded. Unrelated
keys of mixed types also raised instead of being rejected. `refute` now reads the mapping once,
requires distinct string keys, rebuilds each value as a plain `Rational`, and uses only that
snapshot. Regression tests pin the invariant that a recorded witness must itself pass
`refute`. Full suite: **427 passed**. Details are in RC-007's history. No public entry point
emitted `COUNTEREXAMPLE`, so no published result was affected.

### Decisions made on the owner's delegation

- **RC-005 domain:** `t` ranges over R^2, matching the proof. The statement was clarified
  with a history line, and the Q-versus-R items in its `fidelity:` field are now confirmed
  divergences rather than ambiguities.
- **`COUNTEREXAMPLE` gating:** `refute` stays a library API. It is not wired into the CLI
  or any report until RC-007 has an owner read (E1).
- **Line endings:** `*.xml` is pinned to LF in `.gitattributes`, so the example model's
  recorded `model_sha256` is the same on Windows and Linux checkouts.

### Deliberately deferred, and why

- **Binding Lean attestations to their import closure (Sept 14 item 2),** restating the
  Isabelle transport over `real`, and a Rocq lockfile. Each changes a pinned digest or the
  record format, so each needs a fresh exact-head kernel run and reviewed transcription
  (`formal/AGENTS.md` rule 7). All three belong to the formal layer, which is PR #2's scope.
  Do them after PR #2 merges, as a single re-attestation cycle, not piecemeal.
- **The RC-007 correspondence argument.** The E0 draft now exists at
  `research/proofs/rc007-refutation-correspondence.md` against the repaired code. It still
  needs the owner's line-by-line E1 read and, after that, fresh referee contexts that never
  saw its construction. `refute` remains excluded from the CLI and generated reports.

### Still only the owner can do

1. Read the RC-002 corrigendum, then RUN002 with fresh packets and the `referee` skill, then
   RC-002 at E2. In the meantime, the line-by-line read of RC-005 can take it to E1. RC-005
   depends on RC-002, so its own `referee` run only counts once RC-002 is at E2.
2. Find one adversarial human reviewer. TCB obligation 8 requires one before any production
   checker registration, and no agent can meet it.
3. Fix the `.pytest-basetemp` ACL from an elevated prompt. The command is in the
   September 14 session record; until then use a fresh `--basetemp`.

## September 14 update — attestations complete, one binding gap found

This section supersedes the **formal-attestation status** in both sections below: the
September 11 line reporting `REJECTED` because Rocq and Isabelle were unattested, and the
September 7 table row "Only Lean has an entry". Everything else below still stands. No
commit, push, fetch, tier change, attestation edit, or checker registration was performed
to write it.

### What changed

- `HEAD` is now `fbc9867` (`Complete-reviewed-formal-attestations`, 2026-09-12, by the
  owner), `0 0` ahead/behind the cached `origin/phase-0.5-formal-layer`. The remote was not
  fetched. The commit touched only `formal/README.md`,
  `formal/attestations/planar2r-exact-witness.json` and `tests/test_attestation.py`, and
  none of the uncommitted working-tree files, which remain uncommitted.
- Rocq and Isabelle entries were transcribed after review of exact-head CI run 33356967720
  at `0531db5`. The record now satisfies `PLANAR2R_ATTESTATION_POLICY`; locally
  `scripts/check_attestations.py` reports all three digests matching and "all required
  systems attested". Rocq and Isabelle toolchains are still absent on this machine, which
  is reported as unavailable and is not a pass. This satisfies a *policy*. It promotes no RC
  claim and registers no checker.
- The pinned Lean `leanprover/lean4:v4.33.1` is now installed through elan. The Lean tests
  that were skipped now run: **423 passed, 0 skipped** on 2026-09-14, with ruff lint and
  format, strict mypy, the ledger (7 entries) and the attestation check all passing.

### Found on 2026-09-14: a Lean attestation does not bind its statement's meaning

Each attestation pins its proof source and statement text. For Rocq and Isabelle that
also pins meaning, because their definitions sit in the hashed file. For Lean it does not.
`exactWitness_sound` is stated in `Soundness.lean`, but `Claim.Semantics`
(`Semantics.lean`), `FormulaVarsQuantified` (`Wellformed.lean`), the checker
(`Checker.lean`) and `Claim` (`Syntax.lean`) are unhashed. Lean's axiom gate is an
allow-list, and the exact axiom-set re-run comparison exists only for Rocq and Isabelle. An
edit to `Semantics.lean` that still builds therefore leaves the attestation validating. Full
account: [TCB, "What the digests bind"](architecture/trusted-computing-base.md). Nothing was
changed to exploit or repair it.

A consequence for an earlier recommendation: restating the Isabelle transport over `real`
(the Q-versus-R divergence recorded in RC-002's and RC-005's `fidelity:` fields) is no longer
a routine edit. It changes a pinned `artifact_digest`, which invalidates the reviewed Isabelle
entry and requires a fresh exact-head CI run, review and transcription.

### Owner decisions now blocking progress

1. Commit the working tree, which now sits on a newer `HEAD`, before anything else changes it.
2. Whether to extend attestation binding to Lean's import closure. This changes the record
   format, so the lean4 entry would need re-attestation under `formal/AGENTS.md` rule 7.
3. Whether RC-005's `t` ranges over R or Q, and whether the Isabelle restatement is worth a
   re-attestation.
4. Whether `COUNTEREXAMPLE` stays reachable while RC-007 is E0.
5. The reading gates that remain the critical path: the RC-002 corrigendum, then RC-005's
   line-by-line read and the `referee` protocol.

A stale comment remains in the `rocq` job of `.github/workflows/ci.yml`, saying the record
lists Rocq as pending. It is a comment only and was left untouched.

## September 11 update — checkpoint before the owner's attestation commit

This section supersedes the September 7 **repository-state and test-count**
observations below. It preserves that earlier handoff as historical context. The
project owner requested this update before deleting the active session; no commit,
push, tier change, attestation transcription, or production-checker registration
was performed to create it.

### Live repository state

- Branch: `phase-0.5-formal-layer` at
  `0531db56736b4777b9323de03a60c4b684dea486` (`Add the exact algebra core and a
  Positivstellensatz verifier`). Its cached relation to
  `origin/phase-0.5-formal-layer` is `0 0` ahead/behind. This checkpoint did not
  fetch or otherwise assert current remote GitHub/CI state.
- `6ef5115` (canonical Isabelle cartouche repair) is an ancestor of `HEAD`; the
  old instruction to push it is historical. Do not resume at that commit.
- The checkout is intentionally **dirty**: 24 tracked files are modified and 14
  paths are untracked. The untracked paths include the refutation API, optional
  simulation package and tests, the historical result schema, the September 7
  audit, the September 11 exploratory note, methodology sources, and this handoff.
  `HEAD` does not reproduce them. Preserve the whole tree; do not use reset,
  checkout, or broad clean operations.
- `git diff --check` passed. Git printed CRLF-to-LF warnings for existing modified
  files; no whitespace error was reported.

### Fresh local engineering evidence

On 2026-09-11, using a writable workspace-local pytest base directory:

- `412 passed, 11 skipped` in 16.81 seconds. Every skip was the unavailable pinned
  Lean `leanprover/lean4:v4.33.1` toolchain; skips are not successful Lean runs.
- Ruff lint and format checks passed; strict mypy passed for 23 source files.
- `scripts/check_ledger.py` accepted 7 ledger entries, and the frozen RUN001
  validator accepted its artifacts, isolation rules, and manifest.
- `scripts/check_attestations.py` verified the committed Lean record but returned
  the real policy verdict `REJECTED` because Rocq and Isabelle remain unavailable
  and unattested. `scripts/check_lean_conformance.py` likewise reported Lean
  unavailable after evaluating the 18 Python-side vectors. Neither zero exit code
  is proof-kernel acceptance.

These checks are implementation evidence only. They do not promote a research
tier, create a `CheckedCertificate`, establish a robot property, or make a failed
search/inference result decisive.

### Cross-session progress that must be retained

| Workstream | Durable status at this checkpoint |
| --- | --- |
| Phase 0.5 formal layer | The current branch contains hardened rerun/evidence tooling, canonical Isabelle cartouches, Lean-toolchain probing, and exact algebra. Lean is the only committed attestation entry; Rocq and Isabelle require a fresh hardened-path CI run, reviewed evidence artifacts, and manual transcription. Proof-assistant models remain proof-time only and cannot register a checker. |
| Exact algebra | `polynomial.py`, `linalg_exact.py`, and `sos.py` are exact-rational utilities. RC-006 is E0 because the implementation-correspondence argument is unwritten; `sos.py` is not a registered certificate family. |
| Refutation and simulation | The result v0.2 contract, exact universal-claim refutation API, optional MuJoCo candidate-search layer, provenance, and isolation guards exist in the dirty tree. Simulation is a lead generator, not a certificate path. Declared external MJCF references are recorded but their contents are not recursively hashed. |
| RC-007 | A new E0 ledger entry records the implementation-correspondence obligation for `refute()`, which can lead to `COUNTEREXAMPLE` only after exact universal-prefix, domain, and whole-formula checks. The owner must decide whether this live result-status path should remain enabled while RC-007 is E0; the entry itself makes no decision. |
| RC-002 / RC-003 / RC-005 | RC-002 remains E1; RUN001 is permanently stopped for promotion. RC-003 remains EX. RC-005 remains E0. The required owner reads, fresh cross-provider review, isolated steps, hostile/naive reviews, negation control, and correspondence gates remain open. Production `certify`/`check` remains fail-closed with `UNKNOWN`. |
| September 11 lead | `research/notes/2026-09-11-universal-clearance-lead.md` is deliberately an E0 exploratory note, not a claim. It suggests an actual-endpoint universal-clearance route after RC-005 review, but documents the `Seg` nondegeneracy, quantifier-domain, and detached-conjunct gaps that prohibit using it now. |

The authoritative research tiers are now: RC-001 E0, RC-002 E1, RC-003 EX,
RC-004 E0, RC-005 E0, RC-006 E0, and RC-007 E0. Read the live ledger rather than
relying on a session summary.

### Sessions inspected for this update

The following RoboCert sessions were read at their latest completed turn. Their
titles and summaries are not authority; the working tree and the artifacts named
above are authoritative.

- `01a052b8-9ab8-7700-b0b5-57e3686a9962`: formal-attestation reruns; clean pause
  at `6ef5115`, now superseded by current `HEAD`.
- `01a05a0e-3df3-7111-a547-c61c4b54bf34`: optional MuJoCo backend, declared-asset
  provenance, and the unresolved planar-2R coordinate-transport route.
- `01a00046-6b15-7221-b255-771a438a8a36`: September 7 integrated
  refutation/simulation audit and its hardening repairs.
- `01a00271-13ec-7202-9f0d-150d81be3d97`: Phase 0 baseline PR #1 merge and
  synchronization at local `main` `064dabe`.
- `01a00271-13e9-7522-bbe4-f628024c2824`: earlier fail-closed MVP gate repair:
  RC-002 E1, RC-003 EX, RC-005 E0, and an empty production registry.

### Safe continuation order

1. Preserve and review the entire dirty slice before deciding its commit or PR
   boundary. Recheck remote state immediately before any publication.
2. Resolve the formal-attestation evidence workflow on a chosen exact revision;
   do not transcribe Rocq/Isabelle entries from old logs or from a local
   unavailability report.
3. Obtain the required owner reads for the RC-002 corrigendum and RC-005 proof;
   then, and only then, prepare a new frozen RUN002 and apply the repository
   referee protocol. RUN001 judgments are not reusable.
4. Decide the policy boundary for the E0 RC-007 refutation implementation before
   relying on it for a published `COUNTEREXAMPLE` result.
5. Treat the September 11 universal-clearance note as a lead to attack after
   RC-005 review, not as permission to build a universal checker or alter tiers.

## Start here

Read this file, the current root `AGENTS.md`, [research rules](../research/README.md),
[claim ledger](../research/CLAIMS.md), and [TCB declaration](architecture/trusted-computing-base.md).
Before editing, inspect the actual branch and working tree: several sessions have
contributed to the same checkout. Preserve all existing changes.

The governing invariant remains: search may be heuristic; certification may not.
Production checker registration is empty. Public `certify` and `check` remain
closed and return `UNKNOWN`. The newer generic refutation API can establish a
`COUNTEREXAMPLE` to a supported serialized universal formula; this is a distinct
path and does not enable production feasibility certificates.

## Repository checkpoint

Observed locally on 2026-09-07:

- Branch: `phase-0.5-formal-layer`.
- HEAD: `0531db56736b4777b9323de03a60c4b684dea486`, adding the exact algebra core
  and Positivstellensatz verification utility.
- HEAD versus cached `origin/phase-0.5-formal-layer`: `0 0` ahead/behind.
  This review did not fetch or independently query live GitHub CI/PR state.
- Local `main`: `064dabe`, `Establish reproducible Phase 0 baseline (#1)`.
  The other session records PR #1 as merged; the old discussion of Phase 0
  remaining unpublished is historical and must not guide current work.
- The working tree is dirty. It includes refutation, simulation, result-schema,
  packaging, tests, research-attempt and documentation changes. HEAD alone does
  not reproduce those changes. No commit or push was performed by this handoff.
- Package remains `0.1.0a0`, Python >=3.11, Apache-2.0, Hatchling, with no core
  runtime dependencies. MuJoCo is an optional extra.

Preserve the entire current checkout, especially untracked `src/robocert/refutation.py`,
`src/robocert/simulation/`, `examples/simulation/`, the new refutation/simulation
tests, `schemas/result-0.1.0.schema.json`, and the September 7 audit. Deleting this
conversation is not a substitute for committing or backing up the working tree.

## Progress and limits

| Area | Current evidence and limits |
| --- | --- |
| Phase 0 | Immutable specification, exact rational serialization, canonical hashes, envelopes, checker/result boundaries, package and CI infrastructure exist. The original 51-test result is superseded by later suites. |
| Planar 2R research | Kinematics, witness helpers, CLI and proofs exist. Historical production registration, target rewriting and four-chart assumptions were quarantined. Read the [MVP gates](architecture/phase1-pose-tolerance-mvp-gates.md) before restarting this work. |
| Formal layer | Lean, Rocq and Isabelle source models and rerun/evidence tools exist. Proof-assistant models do not prove Python implementation correspondence or physical-model correctness. Only Lean has an entry in the committed attestation; Rocq/Isabelle remain pending. |
| Exact algebra | `polynomial.py`, `linalg_exact.py`, and `sos.py` provide rational polynomial, PSD and identity operations. RC-006 remains E0; `sos.py` is not a registered certificate family. |
| Refutation | Complete rational assignments, purely universal prefixes, domain membership and the entire Boolean formula are checked. Mixed/existential prefixes cannot be refuted by one failing point. Model identity, coordinate and unit correspondence remain material obligations. |
| Simulation | Optional MuJoCo candidate search, provenance, finite-value guards, sampling validation and import-boundary tests exist. No sampled violation is automatically a runtime counterexample or certificate. External MJCF asset contents are not recursively hashed. |
| Serialization | Current result schema is 0.2.0 with required `counterexample` field; claims and certificates remain 0.1.0. The historical result 0.1.0 schema is packaged separately. This does not implement the proposed problem-schema 0.2.0 or pose-tolerance family. |

The [September 7 audit](../research/reports/2026-09-07-counterexample-simulation-audit.md)
has a follow-up repair section at the top: it supersedes the original PARTIAL
finding tables and assessment retained below. The three identified repairs and
additional sampling guards were implemented. Its latest recorded regression is
406 passed / 11 skipped, with lint, types, ledger, frozen-run and distribution
checks passing. These are implementation results, not research-tier promotions.

The README documentation debt noted here earlier was resolved on 2026-09-24. The README and
ROADMAP were restructured into a short overview and an ordered plan with gates, and the
original texts are archived verbatim under `docs/archive/`. No tier changed.

## Research state and next gates

Current ledger: RC-001 E0; RC-002 E1; RC-003 EX; RC-004 E0; RC-005 E0; RC-006 E0.
No tier was changed during this review.

1. Preserve and review the integrated uncommitted slice before choosing commit,
   push or PR scope. The old instruction to push `6ef5115` is stale: it is already
   an ancestor of current HEAD. Recheck live remote state before any publication.
2. Finish formal evidence review using a CI run bound to the chosen revision and
   both prover artifacts. Retain planted axiom/oracle controls and reruns for
   already-attested systems. Reviewed transcription is still pending; evidence
   JSON is provenance and must never self-promote an attestation entry.
3. The owner must read the [RC-002 corrigendum](../research/proofs/rc002-frozen-task-corrigendum-2026-08-24.md)
   before its new content is covered by E1. RUN001 is stopped, with substantive
   blind-audit findings; retain its frozen packets and manifest. A new RUN002
   needs fresh packets/contexts and the repository referee protocol. Never reuse
   RUN001 judgments as a passing verdict.
4. The [RC-005 proof](../research/proofs/planar-2r-pose-tolerance-witness-proof-rc005.md)
   needs owner reading and subsequent independent E2 review. The proposed
   principal-chart pose-tolerance MVP remains gated; it does not establish the
   robust `forall theta forall x exists q` milestone.
5. RC-004 needs its conservatism argument; RC-006 needs written implementation
   correspondence. Passing finite tests does not discharge either obligation.
6. The MuJoCo-to-planar-2R universal refutation example remains mathematically
   unresolved: the existing builder is existential and the target-based
   second-link clearance formula cannot be detached from its FK equalities.
   Preserve A-001/A-003 in [ATTEMPTS.md](../research/ATTEMPTS.md). Candidate angle
   conversion returns a rational approximation to `tan(q/2)`, not an exact
   transcendental coordinate transport. Re-evaluation concerns the rational point
   actually supplied and does not prove it equals the simulator configuration.

## Session evidence reviewed

The live app inventory exposed this session and five other RoboCert sessions.
Their latest two turns were read, including imported external-session messages.
This is not a complete export of all historical or archived conversations. Work
descriptions below are labels for this handoff, not renamed session titles.

| Session ID | Work description and durable outcome |
| --- | --- |
| `019ff5b6-e627-75c2-9e3b-093694746b7c` | This session: public repository setup, initial Phase 0 implementation and Cloud/Automations advice. Current files and later sessions supersede its old branch/test/publication status. |
| `01a00046-6b15-7221-b255-771a438a8a36` | Research environment and September 7 integrated refutation/simulation audit; latest turn repaired remaining input/sampling boundaries and reported 406 passed / 11 skipped. |
| `01a05a0e-3df3-7111-a547-c61c4b54bf34` | MuJoCo optional backend, provenance and candidate-coordinate work; A-003 preserves why a general planar-2R universal refutation example is blocked. Later schema/hardening work supersedes its earlier optional-field proposal. |
| `01a052b8-9ab8-7700-b0b5-57e3686a9962` | Formal attestation reruns, Isabelle cartouche repair and Lean toolchain detection. Paused at `6ef5115`; that branch position is now historical. Evidence transcription and human proof gates remain open. |
| `01a00271-13ec-7202-9f0d-150d81be3d97` | Phase 0 CI repair and PR #1 merge/synchronization at `064dabe`; frozen-run and line-ending reproducibility fixes. |
| `01a00271-13e9-7522-bbe4-f628024c2824` | MVP soundness gate repair: registry quarantine, stopped RUN001, RC-003 refutation, RC-005 draft and gate matrix. No E2 or production activation. |

The earlier Cloud/Automations discussion was advisory; this session created no
automation. Preserve the recommendation to use bounded, reviewable work and keep
research/promotion gates explicit. Recheck current product capabilities and account
configuration before implementation; the August feature advice is not a current
deployment specification. No private conversations, credentials or blind private
mappings are copied into this public repository.

## Continuation checks

Fresh checks during this handoff on 2026-09-07: **406 passed, 11 skipped**
in 13.54 seconds, using `--basetemp .pytest-basetemp/session-handoff-20260907`.
All skips identify the unavailable pinned Lean v4.33.1 toolchain. The ledger
validator accepted all six entries; the RUN001 validator accepted the existing
artifacts, isolation rules and SHA-256 manifest. All eight local links in this
handoff resolved, and `git diff --check` passed. Lint, types, packaging and live
kernel runs were not repeated in this documentation-only handoff; their earlier
results remain attributed to the September 7 implementation audit.

Use `.venv/Scripts/python.exe` on this Windows checkout. Commands already present
in the project include:

```text
-m pytest -q --basetemp .pytest-basetemp/<new-run-name>
-m ruff check src tests scripts benchmarks/proof-verification/scripts
-m mypy
scripts/check_ledger.py
benchmarks/proof-verification/scripts/check_rc002_run.py
scripts/check_attestations.py
scripts/check_lean_conformance.py
```

Use a fresh scratch path if a prior pytest directory has inaccessible ACLs.
Unavailable proof tools and skipped tests are not passes. Lean probing supports
`--lake` and `ROBOCERT_LAKE`; consult the script before invoking a strict run.
The September 7 audit records packaging commands and output paths. Do not infer
new kernel acceptance from a zero exit code that merely reports unavailability.

This handoff changes documentation only and introduces no mathematical assumption,
proof verdict, checker registration or permission to publish. The user intends to
delete this conversation after preservation; the repo documents are the continuation
entry point even if session IDs can no longer be opened.
