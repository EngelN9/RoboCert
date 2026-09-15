# Phase 0 Trusted Computing Base

This document records the initial trusted-computing-base (TCB) boundary. It is a
design declaration, not an external validation or formal proof of the
implementation.

## Trusted to RUN — Phase 0 artifact identity

The following components determine the meaning or identity of a Phase 0 artifact:

| Component | Role | Failure consequence |
| --- | --- | --- |
| Specification constructors and parsers | Enforce typed claim semantics and references | A malformed or semantically different claim may be accepted |
| Canonical JSON encoder | Produces platform-independent artifact bytes | Equivalent artifacts may hash differently or distinct artifacts may be confused |
| SHA-256 implementation | Binds claims, models, and provenance | Artifact identity may be incorrect |
| Certificate preflight checks | Bind certificate metadata to the exact claim/model/checker | A certificate may be checked against the wrong theorem |
| Result promotion factories | Restrict `CERTIFIED_*` to accepted checker output, and `COUNTEREXAMPLE` to a refuted point | Numerical or unchecked evidence may be promoted |
| Refutation guards (`src/robocert/refutation.py`) | Decide whether one rational point falsifies a universally quantified claim | A point that refutes nothing may be reported as a counterexample |
| Python runtime and standard library | Execute all above components | Any trusted behavior may be incorrect |

The JSON Schema validator used in development tests is not the sole enforcement
mechanism. Runtime constructors independently reject malformed data so package
soundness does not depend on applications remembering to run JSON Schema first.

### The second promotion path

Until now `CERTIFIED_*` was the only status asserting a mathematical fact, and
`verify_certificate` was its only gate. `COUNTEREXAMPLE` is now the second, gated by
`refutation.refute`. Both are type-gated in the same way: `counterexample_result` accepts only a
`CheckedCounterexample`, which only `refute` can construct, exactly as `certified_result` accepts
only a `CheckedCertificate`.

The two paths are not equally demanding, and that asymmetry is deliberate rather than an
oversight:

| | establish `forall q in Q: Phi(q)` | refute it |
| --- | --- | --- |
| What is needed | reasoning over a continuum | one point of `Q` |
| Machinery | a certificate family, a checker, an `E2` research claim | exact evaluation at a point |
| Gate | `verify_certificate` + the empty production registry | `refute`'s three guards |

The current refutation API is exported independently of the production checker registry.
Its logical rule is pointwise falsification of a universal formula. The simplicity of that
rule does not discharge implementation correctness: domain handling, exact evaluation,
artifact binding, and the promotion factory are part of the runtime TCB and require review.
That correspondence is ledgered as `research/CLAIMS.md` RC-007, at `E0` with no written
argument, on the precedent RC-006 sets for `sos.py`. The path to `COUNTEREXAMPLE` is
therefore open while its implementation claim is unreviewed. The owner's decision
(2026-09-15): `refute` stays available as a library API, and is not wired into the CLI or
any report until RC-007 has an owner read (`E1`). That caution is not hypothetical: on
2026-09-15 a close reading found that `refute` looked values up in the caller's mapping
separately for each check, so a mapping returning different values could have an unchecked
point recorded as a counterexample. It now reads the mapping once and checks a single
snapshot (RC-007 history).

What `refute` establishes is `not (forall q in Q: Phi(q))` **for the claim exactly as
serialized**. Whether that claim faithfully models the engineering question is, as everywhere
else here, outside what code can check.

Its three guards each fail closed:

1. **Purely universal prefix.** Any `exists` block is rejected outright, not filtered. For
   `forall x exists q: Phi(x, q)`, a failing `(x, q)` pair shows only that this `q` was a poor
   choice. This mirrors `ExactWitnessChecker`, which rejects any non-`EXISTS` block for the
   symmetric reason.
2. **Exact domain membership**, with open and closed endpoints honoured (`AGENTS.md` §31).
3. **Exact evaluation of the whole formula**, never a sub-formula, with any arithmetic failure
   treated as a rejection. Diagnostics deliberately do not name which conjunct failed: proof P2
   Remark 9.5 records that individual conjuncts of the planar-2R encoding carry no meaning in
   isolation, and asks that they not be surfaced as standalone findings.

A rejection is `UNKNOWN`, never feasibility. `unknown_from_refutation` is the only mapping
provided, and it refuses to downgrade an accepted refutation.

**Schema.** `schemas/result.schema.json` is result v0.2.0. Every emitted result has a
required `counterexample` field, containing a witness object only for `COUNTEREXAMPLE`
and null for every other status. `RESULT_SCHEMA_VERSION` is independent of claim and
certificate v0.1.0. The previous schema is preserved byte-for-byte in
`schemas/result-0.1.0.schema.json`; both contracts are packaged and loadable.
This is a version migration: the earlier contract allowed a counterexample without
the new payload, so tightening it under the same schema identity was incompatible.
Historical validation is not evidence of exact refutation, and no automatic promotion
from a historical document is provided.

**Audit status.** The [2026-09-07 implementation audit](../../research/reports/2026-09-07-counterexample-simulation-audit.md)
records the initial findings and their subsequent repairs. Malformed model hashes
now raise before evidence construction. Direct MuJoCo configuration/control inputs
and timestep overrides are validated before engine mutation, and regression tests
explicitly forbid refutation imports and promotion symbols in simulation code.

**Import surface.** `refutation.py` reuses `checkers.evaluate_formula`, the generic exact
evaluator that module already advertises as domain-independent and reusable. That reuse pulls
`robocert.checkers` and `robocert.attestation` into `import robocert`'s graph for the first time.
No behaviour changes: the production registry is a frozen empty mapping, and importing a checker
implementation registers nothing.

## Trusted to PROVE

A separate and much weaker kind of trust. These components determine whether a *soundness
argument* is valid. They never execute during certification and cannot affect any result.

| Component | Role | Failure consequence |
| --- | --- | --- |
| Lean 4 kernel and pinned toolchain (`formal/lean-toolchain`) | Accepts the checker-model soundness proof in `formal/RoboCert/` | A soundness argument believed kernel-checked may be invalid. **No runtime behaviour changes.** |
| Rocq kernel and pinned toolchain (`formal/rocq/`) | Accepts the exact polynomial identities in `formal/rocq/RoboCert/Planar2R.v` | Same as above, for a different (algebra-focused) soundness argument. **No runtime behaviour changes.** |
| Isabelle/HOL kernel and pinned release (`formal/isabelle/`) | Accepts the bounded-existential/quantifier-transport statements in `formal/isabelle/RoboCert/Planar2R.thy` | Same as above, for a different (quantifier-focused) soundness argument. **No runtime behaviour changes.** |

Explicitly **not** implied by those rows:

- None of the three is in the run-time TCB above, and none executes during `certify` or
  `check`.
- None appears in `pyproject.toml`'s `dependencies`, which remains empty. The wheel does not
  contain `formal/`.
- None is required to reproduce a result. The `AGENTS.md` §34 reproducibility base stays
  `model + claim + assumptions + certificate + checker`; a user needs no proof-assistant
  install.
- A proof from any of the three does **not**, by itself, discharge any of the eight
  obligations in "Future certificate-family obligation" below, authorize a production
  checker registration, or permit a `CERTIFIED_*` result.

### The attestation gate — a bounded exception to "cannot affect any result"

`src/robocert/attestation.py` is the one place a proof-assistant result reaches as far as a
`CheckerDecision`, and it is deliberately narrow: `AttestedChecker.check` computes
`inner.accepted and not violations`. An attestation can only **veto** an acceptance the
Python checker already reached on its own; it can never manufacture one. There is no branch
in that computation where a passing attestation makes the result more accepting than the
inner checker's verdict alone. This is why the row above still says "cannot affect any
result" in the *positive* direction while the gate exists in the *negative* one: the
attestation mechanism can turn an accept into `UNKNOWN`, never the reverse.

An attestation is a JSON record inside `Certificate.payload["attestations"]`
(`ATTESTATION_KEY`), naming an opaque `system` string, bound by exact-match to the
certificate's `claim_hash`, `model_hash`, `checker_id`, and `checker_version`, carrying a
`kernel_accepted` boolean and an `axioms` list checked against a policy-supplied allow-list.
`robocert.attestation` names no proof assistant; the set of required systems and each one's
permitted axioms is policy data supplied by the checker that wraps itself in
`AttestedChecker` (see `PLANAR2R_ATTESTATION_POLICY` in `src/robocert/checkers.py`).

**Missing, corrupted, mismatched, or failed proof checking rejects — it is never treated as
`CERTIFIED_*`.** A required system with no usable entry is "unavailable proof checking" in
exactly the sense the requirement demanded, and it vetoes identically to a kernel that ran
and reported failure. `tests/test_attestation.py` covers all five categories (valid,
corrupted, mismatched, failed, unavailable) plus a Hypothesis property test asserting the
tightening property holds for arbitrary attestation payloads, not merely the cases enumerated
by hand.

### What validating an attestation does NOT do

Validating an attestation checks that a well-formed, hash-bound record *claims* a kernel
accepted a statement. **It does not run a kernel.** Re-running the kernel and confirming the
claim is `scripts/check_attestations.py`'s job, which runs in CI where the toolchains are
installed (the `formal`, `rocq`, and `isabelle` jobs in `.github/workflows/ci.yml`). Absent
that re-run, an attestation is **provenance, not proof** — evidence that some kernel accepted
a statement with a given digest at some point, not a live guarantee.

**What the digests bind, and what they do not.** Each entry pins two files: the named proof
source (`artifact_digest`) and its statement text (`statement_digest`). `_check_bound_digests`
in `scripts/check_attestations.py` fails the record if either changes. For Rocq and Isabelle
that also pins what the attested statements *mean*: the definitions they use (`D`, `C`, `S`;
`in_box`) live in the hashed file, and their only imports come from the recorded toolchain.
**For Lean it does not.** `exactWitness_sound` is stated in `Soundness.lean`, but its meaning
is fixed elsewhere: `Claim.Semantics` in `Semantics.lean`, `Claim.FormulaVarsQuantified` in
`Wellformed.lean`, `ExactWitnessChecker.check` in `Checker.lean`, and `Claim` in `Syntax.lean`.
No digest covers those four files. The exact axiom-set comparison on kernel re-run is implemented
for Rocq and Isabelle only; Lean's gate, `scripts/check_lean_axioms.py`, is an allow-list.
The differential conformance vectors compare checker verdicts, which reflect `Checker.lean`, not
`Semantics.lean`. So an edit to `Semantics.lean` that still builds and needs no new axiom
changes the proposition a Lean attestation vouches for while the attestation keeps validating.
Until the binding covers the import closure, a Lean attestation vouches for a proof file, not
for the proposition a reader takes it to state. Recorded 2026-09-14 from reading the checker
code. None of those files has been edited, and the committed attestation is unchanged.

### The unproved bridges

`formal/RoboCert/Checker.lean`, `formal/rocq/RoboCert/Planar2R.v`, and
`formal/isabelle/RoboCert/Planar2R.thy` are each a **model** of some part of
`src/robocert/`. The kernels prove properties of those models. The thing that actually runs
is the Python.

Nothing in `formal/` proves that a model and the Python it models agree. The current finite
bridge is `scripts/check_lean_conformance.py`: 18 shared claim/certificate vectors must produce
the same verdict in the Lean checker model and the shipped Python checker. This is differential
evidence, not equivalence, and says nothing about untested inputs or deliberately unmodelled
payload parsing, metadata/hash checks, and attestation handling. A reader who forgets this will
overstate what the layer buys.
The same applies to `Claim.FormulaVarsQuantified` in `formal/RoboCert/Wellformed.lean`, which
is asserted to follow from Python's claim validation rather than derived from it, and to the
Rocq/Isabelle files, which state supporting algebraic and quantifier facts about the RC-005
proposal rather than a soundness theorem for a registered checker.

Adding any dependency to any of the three toolchains (mathlib included) is a reviewed change
that must extend the "Trusted to PROVE" table, satisfying obligation 3 below.

## Not trusted for certification

The following may propose evidence but can never directly emit a certified result:

- optimization or numerical solver adapters;
- candidate certificate generators;
- sampling, simulation, or counterexample search;
- orchestration agents or LLM output;
- reporting and visualization layers;
- third-party code implementing the `Checker` protocol but not registered by the
  RoboCert package;
- **every external mathematical or robotics system**, named explicitly so the boundary is not a
  matter of interpretation: Drake and C-IRIS, SymPy, SageMath, Julia with SumOfSquares.jl and
  JuMP, Risa/Asir, CoCoA, Singular, dReal and iSAT, and MuJoCo. Each may propose a candidate
  certificate. None is a dependency of this package, none executes during `check`, and none can
  raise a result above `UNKNOWN` by succeeding. A solver reporting "solved" contributes exactly
  one thing: an artifact for a RoboCert checker to re-derive exactly. See
  `docs/architecture/backends.md`.

Two of those deserve a specific note, because their output is easy to mistake for a proof.
**dReal's δ-satisfiability is not satisfiability** — it concerns a δ-perturbed problem, so it maps
to `UNKNOWN`; only an exact rational counterexample, re-evaluated here, yields `COUNTEREXAMPLE`.
**Quantifier-elimination output is not independently checkable** without redoing the elimination,
so QE backends stay experimental and cannot support a `CERTIFIED_*` family.

### Physics simulation (not trusted, not registered, optional)

`src/robocert/simulation/` adapts MuJoCo for falsification search: adversarial sampling of a
candidate configuration region, contact and clearance experiments, actuator-force and joint-limit
observation. It is the weakest kind of evidence this repository produces, and its boundary is
therefore structural rather than documentary:

- `pyproject.toml`'s `dependencies` stays `[]`; MuJoCo is the optional `mujoco` extra, is not
  installed in CI, and is not required to reproduce any result.
- `robocert/__init__.py` does not import the subpackage, and `simulation/mujoco_backend.py` is the
  only module in the repository that imports `mujoco`. `import robocert` therefore never loads it.
- The subpackage imports nothing from `robocert.checking`, `robocert.results`,
  `robocert.certificates`, or `robocert.checkers`, so no code path exists from a simulation
  observation to a `CheckerDecision`. There is no simulation analogue of the attestation gate:
  simulation output does not reach a `CheckerDecision` at all, in either direction.
- `tests/test_simulation_boundary.py` enforces both of the above by reading the module sources and
  by importing the package in a subprocess. A refactor that reintroduces the coupling fails the
  suite.

MuJoCo simulates a **different, higher-fidelity model** than the one a RoboCert claim quantifies
over, which is what makes a contact it reports a *candidate* counterexample rather than a
counterexample. `FalsificationOutcome.COUNTEREXAMPLE_FOUND` is not `ResultStatus.COUNTEREXAMPLE`
and cannot become one without exact re-validation against RoboCert's own model
(`AGENTS.md` §31). `NO_COUNTEREXAMPLE_FOUND` means only that a finite sample found nothing.

### Exact-algebra utilities (not trusted, not registered)

`src/robocert/polynomial.py`, `src/robocert/linalg_exact.py`, and `src/robocert/sos.py` provide
exact rational polynomial arithmetic, an exact PSD decision, and Positivstellensatz certificate
verification. They add no dependency — `dependencies` remains empty.

`sos.py` is **not** a `Checker` and is registered nowhere. It verifies an algebraic identity plus
a PSD condition, which is Positivstellensatz *sufficiency* and elementary. It is not RC-001,
which claims the SOS scheme suits the planar-2R singularity-margin reduction and is `E0`. Binding
this verifier to a certificate family is a separate change subject to the obligations below.

Phase 0 deliberately registers no production checker. Test code temporarily
installs either a deterministic fixture checker or the quarantined RC-002
research checker into the private registry to exercise promotion, mathematical
evaluation, and corruption rejection. Those monkeypatched registrations are
test evidence only; neither is a production checker.

## Future certificate-family obligation

Adding a production checker requires a reviewed code change that:

1. defines a versioned certificate-family payload schema;
2. states the exact theorem and arithmetic semantics checked;
3. identifies all additional trusted libraries and versions;
4. provides positive, negative, adversarial, and corrupted-certificate tests;
5. binds the checker identity, version, arithmetic mode, claim hash, model hash,
   assumptions, and provenance;
6. fails closed on malformed artifacts, unsupported versions, exceptions, and
   resource exhaustion;
7. documents independently known benchmark truth and remaining limitations;
8. has survived at least one adversarial review by a human, in addition to the `E2`
   referee protocol. `E2` is adversarial AI review only, and AI reviewers share failure
   modes that separating their contexts cannot remove (`research/README.md` rule 6).
   This is the one point at which RoboCert requires an adversarial human, and it is
   placed at registration because registration is what makes `CERTIFIED_*` reachable.
