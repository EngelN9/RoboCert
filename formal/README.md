# `formal/` — proof-assistant-neutral soundness layer

Three kernels, one boundary. Lean 4, Rocq, and Isabelle/HOL each prove theorems about parts
of RoboCert's design. None of them run at certification time, and a result from any of them
can never, by itself, cause a certificate to be `CERTIFIED_*`.

## Scope, before anything else

Every proof in this directory is about a **model**. Nothing here is a statement about a
physical robot, a controller, a workcell, or a safety standard. The model-to-reality step is
carried entirely by `Assumption` records (`src/robocert/specification.py:547`) and is never
proved. `AGENTS.md` §61–§64 and §66 govern how results from this directory may be described;
in particular "formally verified hardware" is forbidden wording, and no declaration name
anywhere under `formal/` may contain `safe`, `verified_safe`, or `certified` — see "Naming
rule" below.

## Division of labour

| System | Assignment | Directory |
|---|---|---|
| **Lean 4** | checker-model soundness: `check c cert = true → c.Semantics` | `formal/RoboCert/` (top level — see "A layout asymmetry" below) |
| **Rocq** | exact polynomial identities; future: Positivstellensatz/SOS-style certificates, real-closed-field reasoning, validated interval arithmetic | `formal/rocq/RoboCert/` |
| **Isabelle/HOL** | quantified semialgebraic claims; future: independent real quantifier-elimination cross-checking | `formal/isabelle/RoboCert/` |

None of the three reimplements CAD, QE, an SDP solver, or a numerical backend. That is a
permanent non-goal for this directory, not a temporary scoping choice — see
`docs/architecture/trusted-computing-base.md`.

## What this layer is

RoboCert's runtime is Python and stays Python. This directory is **proof-only**:

- each system proves properties of a source-level model of some part of `src/robocert/`, or
  states supporting facts about a research claim (`research/CLAIMS.md`);
- none is a runtime dependency. `pyproject.toml` keeps `dependencies = []`, the wheel does
  not contain `formal/`, and reproducing a RoboCert result per `AGENTS.md` §34 still needs
  only `model + claim + assumptions + certificate + checker` — no proof-assistant install;
- none can register a checker or unlock `CERTIFIED_*` by itself.

**The one channel that does reach the runtime** is the attestation gate,
`src/robocert/attestation.py`. It is narrower than "reach": an attestation can only *veto* an
acceptance a Python checker already reached on its own (`AttestedChecker.check` computes
`inner.accepted and not violations`). It can never manufacture one. A missing, corrupted,
mismatched, or failed attestation forces rejection, which `results.unknown_from_check` maps
to `UNKNOWN` — never `CERTIFIED_*`. See
`docs/architecture/trusted-computing-base.md`, "The attestation gate", for the full account,
and `tests/test_attestation.py` for the valid/corrupted/mismatched/failed/unavailable test
matrix plus the Hypothesis property test asserting the veto-only property holds for arbitrary
payloads.

**Validating an attestation is not the same as running a kernel.** It checks that a
well-formed, hash-bound record *claims* a kernel accepted a statement. Re-running the kernel
and confirming that claim is `scripts/check_attestations.py`'s job, run in CI (jobs `formal`,
`rocq`, `isabelle` in `.github/workflows/ci.yml`) where the toolchains are actually installed.
Absent that re-run, an attestation is **provenance, not proof**.

## What is proved, and what is assumed

| | Status |
|---|---|
| Lean: `check c cert = true → c.Semantics` | **PROVED**, kernel-checked, no `sorryAx` — confirmed locally via `lake build` + `scripts/check_lean_axioms.py` |
| Lean model ≡ Python implementation | **NOT PROVED; differentially TESTED.** `scripts/check_lean_conformance.py` runs 18 shared claim/certificate vectors through the Lean model and the shipped Python checker and requires identical verdicts (8 accepted, 10 rejected). The `formal` CI job runs it under `--require-lean`. Agreement on a finite vector set is evidence, not equivalence — see "Differential conformance" below for what it does and does not cover |
| ℚ semantics → ℝ semantics | **NOT PROVED.** Needs mathlib, deliberately not pinned yet |
| Certificate payload parsing / hash binding | **NOT MODELLED** by Lean. `verify_certificate`'s metadata cross-checks are a separate concern |
| Rocq: `formal/rocq/RoboCert/Planar2R.v` compiles with no `admit` | **CONFIRMED** — the `rocq` CI job reports "toolchain available and compiled cleanly" under `--require rocq` on Rocq 9.2. Getting there took three fixes: a false green (job passed with no Rocq on PATH), the Rocq 9 rename of `coqc` to `rocq compile`, and one genuinely FALSE lemma the kernel caught (divergence 5 below) |
| Isabelle: `formal/isabelle/RoboCert/Planar2R.thy` builds with no `sorry` | **CONFIRMED** — the `isabelle` CI job reports "session built cleanly" under `--require isabelle`, so a real kernel ran. Its first attempt failed on a `ROOT` layout error (theory in a subdirectory needs an explicit `directories` declaration), not on the mathematics |
| The committed attestation record is rejected by `PLANAR2R_ATTESTATION_POLICY` | **CONFIRMED** — `tests/test_attestation.py::test_committed_attestation_record_matches_real_policy_and_is_honestly_incomplete` runs the real policy against it, not a description of the policy |

All three kernel rows are now settled facts, each confirmed by a kernel that actually ran in
CI under a `--require` assertion that makes a toolchain-absent false pass impossible. Everything else is an open bridge or an honestly unconfirmed claim, and the table
says so rather than implying otherwise. Note that a kernel building does NOT make it an
attestation: `formal/attestations/planar2r-exact-witness.json` still carries no
`kernel_accepted` entry for it, because promoting one out of `pending_systems` requires
recording the toolchain and digests from that specific successful run (`formal/AGENTS.md`
rule 7).

## A layout asymmetry, recorded rather than hidden

Lean's sources live directly under `formal/RoboCert/` (the original Phase 0.5a layout), while
Rocq and Isabelle each got their own `formal/rocq/` and `formal/isabelle/` subdirectory when
they were added. This is inconsistent and is not a deliberate design choice — moving Lean
into a matching `formal/lean/RoboCert/` subdirectory (and updating `lean-toolchain`,
`lakefile.toml`, the `formal` CI job's paths, and `scripts/check_lean_axioms.py`'s
`FORMAL_DIR`) is a reasonable future cleanup, deliberately not done in the same change that
added the other two systems, to avoid touching a working, already-verified build alongside
two unverified new ones.

## Deliberate divergences from `specification.py` (Lean)

Recorded so that a correspondence review has a checklist rather than a diff.

1. **`Formula.not` takes one `Formula`**, where Python carries a one-element `operands` list
   whose length is enforced at `specification.py:494`. The Lean type makes the invariant
   structural.
2. **`IntervalDomain` carries no `lower < upper` invariant** in `Syntax.lean`. Python enforces
   it strictly at `specification.py:200`. Keeping the syntax type permissive lets us represent
   -- and reason about -- claims the runtime would reject. This matters: RC-005 §1 admits
   `a_i <= b_i`, so the runtime is currently *stricter* than the claim it is meant to
   implement. Safe direction, but previously unrecorded anywhere.
   `formal/isabelle/RoboCert/Planar2R.thy`'s `in_box` definition follows the same
   non-strict convention, and proves it is nonvacuous at `a_i = b_i`
   (`singleton_box_admits_its_point`).
3. **`Certificate` is modelled as `conclusion + witness`** in Lean, omitting hashes, family,
   checker identity, and provenance. Those belong to the binding theorem, not the semantic
   one.
4. **Field names are camelCase** in Lean, snake_case in Python.
5. **Rocq nondegeneracy hypotheses are setoid, not Leibniz.** `Planar2R.v` uses
   `~ (D == 0)`, not `D <> 0`. Over `Q` these differ: `0#5` is `== 0` but not `= 0`, so the
   Leibniz form admits a counterexample that makes the lemma FALSE. The first version of that
   file used `<>` and the Rocq kernel rejected it -- a case of a proof assistant catching a
   wrong statement rather than a wrong proof. RC-005 itself is unaffected; its hypothesis is
   `L1, L2 > 0` over the reals, stronger than either reading.
6. The upstream methodology manual uses a `lean/` directory
   (`docs/methodology/anthropic-research-methodology-source.md:80`); this project uses
   `formal/`.
7. **A missing domain fails closed in Lean; in Python it would raise, and be caught.**
   `blockWitnessOk` (`Checker.lean:69`) returns `false` when `Claim.findDomain` misses.
   `checkers.py:127` does a bare `domains_by_id[block.domain_id]` lookup, which would raise
   `KeyError`. Two independent things make that benign, and both are worth stating because
   either alone would be weaker. First, it is unreachable: `specification.py:737` rejects a
   quantifier naming an unknown domain at construction, so no valid `Claim` reaches the lookup.
   Second, if it were reached the exception would not escape — `checking.py:140` wraps every
   `checker.check` call in `except Exception` ("fail closed at the trusted checker boundary")
   and returns a rejection, which `results.unknown_from_check` maps to `UNKNOWN`. So the two
   sides differ in mechanism (`false` versus caught-exception) and agree in outcome. This is
   the same shape as divergence 2: the Lean syntax type can represent a state the runtime
   refuses to build. Found while writing the conformance harness, which is what it is for.
   Neither side changed.
8. **Empty `and`/`or` are reachable in Lean, unconstructible in Python.** `Formula.HoldsAll [] =
   True` and `Formula.HoldsAny [] = False` mirror Python's `all()`/`any()`, but
   `specification.py:497` rejects an `and`/`or` formula with no operands, so no vector can
   exercise them. Recorded rather than tested.
9. **The unbound-variable path is unreachable from a valid `Claim`.** `evalPowers` returns
   `none` for a variable the environment does not bind, modelling the `KeyError` that
   `checkers.py:146` catches. In practice every predicate variable must be declared
   (`specification.py:751`) and every declared variable quantified exactly once
   (`specification.py:746`), so the domain-membership check rejects a missing binding before
   the formula is ever evaluated. Both sides still reject; they reject for different reasons.

## Differential conformance

`RoboCert.exactWitness_sound` is a theorem about `Checker.lean`. Whether that model describes
`src/robocert/checkers.py` is a separate question, and it is not proved anywhere. Without an
answer the Lean development is unfalsifiable in the wrong direction: the model could drift
arbitrarily from the runtime and every gate in the repository would stay green.

`scripts/check_lean_conformance.py` is the bridge. It builds claim/certificate vectors, runs
each through the real shipped `planar2r_exact_witness_checker` object, emits a Lean file with
one `#guard` per vector asserting the model returns the same `Bool`, and elaborates it with
`lake env lean`. Nothing is committed: the vectors' Python definitions are the reviewable
source, so there is no generated artifact to go stale.

**Covered.** The worked instance (`L1 = L2 = 5`, `t1 = 1/2`, `t2 = -1/3`) that
`formal/attestations/planar2r-exact-witness.json` also names; a witness outside its box; a
witness inside the box that falsifies the formula; a missing binding; an extra binding; an
`infeasible` conclusion; a `forall` block (the RC-002 guard); all four open/closed interval
boundary flags with the witness exactly on the endpoint; two existential blocks; nested `not`,
a disjunction whose first operand is false, a failing conjunction; and exponent/coefficient
arithmetic against Lean's hand-written `ratPow`. Every one of them is additionally
required to satisfy the soundness theorem's hypothesis — see "In scope for the theorem" below.

**In scope for the theorem.** `exactWitness_sound` does not conclude anything about an
arbitrary claim: it assumes `hwf : c.FormulaVarsQuantified` (`Wellformed.lean`). A vector
violating that hypothesis could agree perfectly on the Bool and still sit entirely outside the
theorem, which would make its agreement worthless as evidence for soundness. Every vector is
therefore required to satisfy it, and `build_vectors` raises rather than admitting one that
does not.

That check is also, as far as it goes, the differential evidence `Wellformed.lean` asks for:
its header records that "the Python validator implies this Lean predicate is asserted, not
proved", and names this harness as the mechanism. Eighteen instances is what the harness can
supply. **Its limit, stated rather than glossed:** `formula_vars_quantified` is a Python
*restatement* of the Lean predicate, evaluated on Python `Claim` objects. It resolves
unresolvable ids exactly as the Lean definitions do (an unknown predicate mentions nothing; a
block naming an unknown domain binds nothing) and is guarded by a non-vacuity control, but it
is not the Lean predicate evaluated on the Lean terms. The stronger form — a decidable `Bool`
mirror in `Wellformed.lean` with a `... = true → c.FormulaVarsQuantified` lemma, `#guard`ed per
vector and added to the axiom audit — is a deliberate deferral, not an oversight. The
obligation stays open.

**Not covered, and not claimed.** Agreement on 18 vectors is differential evidence, not a proof
of equivalence (`AGENTS.md` §66). It says nothing about vectors outside the set. It also says
nothing about the parts of the Python path the Lean model deliberately omits — payload parsing
(`checkers.py::_parse_witness`), the metadata and hash cross-checks in
`checking.py::_run_checker`, and `attestation.py::AttestedChecker` — see divergence 3.

**The harness can fail, and that was measured, not assumed.** `tests/test_lean_conformance.py`
plants a defect and requires detection: a flipped verdict, and eight per-vector mutations of the
emitted Lean (connective swap, boundary-flag flip, `exists_`→`forAll`, relation swap, exponent
change). Each is planted at a site that is load-bearing *for that vector*. Mutations applied to
the first occurrence anywhere in the file are deliberately **not** used as controls: three of
them (`Relation.gt`, `lowerClosed`, `Formula.and`) were measured as undetected, in every case
because at that particular site the change preserves the verdict — `relation` is irrelevant to a
claim already rejected by the quantifier guard, a boundary flag is irrelevant to an interior
witness, and `and`→`or` is irrelevant when every conjunct is true. That is a property of where
the mutation landed, not a hole in the harness, and it is recorded here rather than left for a
reader to rediscover.

One vector was rewritten because of this measurement: `high_exponent_arithmetic` originally
carried a slack bound, so flipping its exponent from 3 to 2 changed nothing and the vector did
not perform the check it was named for. Its bound is now tight between the two.

## Layout

```
lean-toolchain, lakefile.toml, lake-manifest.json    Lean pins (top level -- see asymmetry note)
RoboCert/Syntax.lean      mirrors src/robocert/specification.py
RoboCert/Semantics.lean   what a Claim MEANS -- read this before trusting anything
RoboCert/Checker.lean     the checker model, as an executable Bool
RoboCert/Soundness.lean   check = true → Semantics
RoboCert/Audit.lean       #print axioms guards
Statements/               QUARANTINE: statement-only, `sorry` permitted, never imported above

rocq/_CoqProject                          Rocq build config
rocq/RoboCert/Planar2R.v                  exact polynomial identities (RC-005 nondegeneracy)

isabelle/ROOT                             Isabelle session definition
isabelle/RoboCert/Planar2R.thy            bounded-existential transport (RC-002 corrigendum C2)

attestations/planar2r-exact-witness.json  committed, hash-bound attestation record
```

## Two Lean targets

`RoboCert` must be `sorry`-free and is covered by the axiom audit. `Statements` exists so that
RC-002/RC-005 theorem statements can be formalized before their proofs, per
`docs/methodology/anthropic-research-methodology-source.md:188` -- "Formalizing a statement
forces every implicit quantifier and coercion into the open." It is never imported by
`RoboCert`, so an unproved lemma there cannot leak into an audited theorem. Rocq and Isabelle
have no equivalent quarantine yet; both of their files so far are proof-complete
(`ring`/`blast`/`simp`-level), so the question has not yet arisen.

## Build

```bash
# Lean
cd formal && lake build

# Does the proved theorem describe the SHIPPED checker? Differential conformance, fail-closed.
python scripts/check_lean_conformance.py --require-lean

# Rocq (once installed; see the `rocq` CI job for the current best-effort install method)
rocq compile -Q formal/rocq/RoboCert RoboCert formal/rocq/RoboCert/Planar2R.v

# Isabelle (once installed; see the `isabelle` CI job)
isabelle build -D formal/isabelle

# Cross-check whatever is ACTUALLY installed against the committed attestation record.
# Never invents a pass for a system it cannot run.
python scripts/check_attestations.py
```

Lean's toolchain is pinned in `lean-toolchain`; dependency revisions are pinned in
`lake-manifest.json`, which is committed. There are no Lean dependencies yet -- mathlib is
deliberately not used, because the mathematics so far is exact rational arithmetic and
structural induction. Rocq and Isabelle do not yet have committed lockfiles analogous to
`lake-manifest.json`; their CI jobs pin a version by URL/opam package instead. This is a
tracked gap, not a silent omission — see `AGENTS.md` §57's disclosure tables.

Attestation *toolchain-version* format for reports, per
`docs/methodology/anthropic-research-methodology-source.md:411` and
`research/reports/README.md:24`:

```
lean: leanprover/lean4:v4.33.1 / no dependencies
rocq: rocq-prover 9.0.0 (pending first successful CI run)
isabelle: Isabelle2025 (pending first successful CI run)
```

Do not confuse this reporting convention with an *attestation record*
(`src/robocert/attestation.py`, `formal/attestations/*.json`) — the former is prose for a
research report, the latter is a structured, hash-bound, machine-checked artifact.

## Naming rule

No declaration name anywhere under `formal/` may contain `safe`, `verified_safe`, or
`certified`. Names state what is proved: `exactWitness_sound`, `pythagorean_identity`,
`bounded_existential_transport` — never `checker_is_safe`.
