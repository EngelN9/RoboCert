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
| Result promotion factories | Restrict `CERTIFIED_*` to accepted checker output | Numerical or unchecked evidence may be promoted |
| Python runtime and standard library | Execute all above components | Any trusted behavior may be incorrect |

The JSON Schema validator used in development tests is not the sole enforcement
mechanism. Runtime constructors independently reject malformed data so package
soundness does not depend on applications remembering to run JSON Schema first.

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
- A proof from any of the three does **not**, by itself, discharge any of the seven
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

### The unproved bridges

`formal/RoboCert/Checker.lean`, `formal/rocq/RoboCert/Planar2R.v`, and
`formal/isabelle/RoboCert/Planar2R.thy` are each a **model** of some part of
`src/robocert/`. The kernels prove properties of those models. The thing that actually runs
is the Python.

Nothing in `formal/` establishes that a model and the Python it models agree. That
correspondence is established by differential testing against shared conformance vectors, not
by proof — this is planned but not yet built (tracked as future work; not to be confused with
this phase's own designation). A reader who forgets this will overstate what the layer buys.
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
  RoboCert package.

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
7. documents independently known benchmark truth and remaining limitations.
