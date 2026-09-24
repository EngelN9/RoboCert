# Research claims ledger (RC-xxx)

Entries here are **research/design claims about algorithms, reductions, and checker
soundness** — e.g. "certificate family F is a sound scheme for claim shape X" or
"this reduction to known result Y holds under conditions Z". They are **not**
instances of the runtime `robocert.Claim` class or `schemas/claim.schema.json`; a
single `RC-xxx` entry may eventually justify many runtime `Claim`/`Certificate` pairs
once its target checker is implemented and registered.

See `research/README.md` for tier definitions and the monotonicity rule. Format is
enforced by `scripts/check_ledger.py`, run automatically on every edit to this file
(`.claude/settings.json`).

## Entry format

```markdown
## RC-<number>
statement: <precise research/design claim, one or two sentences>
tier: E0 | E1 | E2 | E3 | E4 | EX
depends: [RC-xxx, ...]        # or [] if none
proof: <path to the argument, e.g. research/notes/...md>
target_checker: <path to the checker this would justify, or "not yet implemented">
referee: none | <path to the referee audit table, once E2+>
mechanized:                   # optional; one bullet per proof-assistant declaration
  - <system>: <file> <declaration> (<what that declaration states>)
fidelity: <required whenever mechanized: is present -- how each formal statement was
  compared with statement:, and every known divergence; "not independently checked"
  is an acceptable answer, an omitted one is not>
history:
  - <date> created E0
  - <date> -> E<n> after <reason>
```

Tiers change only by appending a `history:` line in the same edit that changes
`tier:`. `tier: E2` or above requires `referee:` to be non-`none`. `mechanized:`
requires `fidelity:` -- a kernel accepting a proposition says nothing about whether it
is the proposition this entry means (see `research/README.md` "Mechanization").

---

## RC-001

statement: The SOS/Positivstellensatz certificate family (`README.md` §8.2) is a
  sound scheme for certifying singularity-margin claims
  `sigma_min(J(q,theta)) >= epsilon` for the planar 2R benchmark
  (`ROADMAP.md` Phase 1 / `README.md` §32 "First minimal viable theorem") under
  interval link-length uncertainty `theta in Theta`.
tier: E0
depends: []
proof: research/notes/2026-08-14-2r-sos-margin-soundness.md
target_checker: src/robocert/certification/sos/ (not yet implemented)
referee: none
history:
  - 2026-08-14 created E0
  - 2026-08-16 noted: Phase 1 Slice 1 shipped a different, non-SOS, non-robust
    approach (RC-002) for a single fixed instance only. This claim's SOS-based,
    robust (`forall theta`) approach remains open and unaddressed.

## RC-002

statement: The tangent-half-angle + case-split point-segment-distance polynomial
  encoding (`src/robocert/kinematics2r.py`) is a sound representation of the
  single-instance planar-2R reachability + joint-limit + obstacle-clearance +
  singularity-margin conjunction (`README.md` §32 "First minimal viable theorem",
  restricted to one fixed rational instance, not robust over `theta` or `x`),
  exactly checkable via rational `Predicate`/`Formula` evaluation
  (`src/robocert/checkers.py::ExactWitnessChecker`).
tier: E1
depends: []
proof: research/proofs/planar-2r-exact-witness-proof-p1.md and
  research/proofs/planar-2r-exact-witness-proof-p2.md (authoritative);
  research/proofs/rc002-frozen-task-corrigendum-2026-08-24.md (draft repair,
  not yet covered by the existing E1 human attestation);
  research/notes/2026-08-16-2r-exact-witness-soundness.md (superseded informal
  reading guide); src/robocert/kinematics2r.py, tests/test_kinematics2r.py
target_checker: src/robocert/checkers.py (research implementation only;
  "planar2r.exact_witness" is not registered in the production registry)
referee: none (see history -- assisted review cannot establish E2, and frozen
  blind RUN001 stopped with substantive findings)
mechanized:
  - lean4: formal/RoboCert/Soundness.lean exactWitness_sound (a MODEL of the target
    checker `ExactWitnessChecker` accepts only certificates whose witness satisfies
    `Claim.Semantics` over Q)
  - isabelle: formal/isabelle/RoboCert/Planar2R.thy bounded_existential_transport
    (pointwise equivalence transports to bounded-existential equivalence on a closed box)
fidelity: Recorded 2026-09-11 by reading the declarations against this entry and its
  proof files; no independent comparison was performed. Neither declaration is RC-002's
  statement. (a) The Lean theorem is about the checker model, not the encoding: it says
  nothing about whether the tangent-half-angle encoding represents planar-2R geometry,
  which is what RC-002 asserts, and its correspondence to the Python checker is
  differential only (18 vectors, scripts/check_lean_conformance.py). Its attestation in
  formal/attestations/planar2r-exact-witness.json hashes Soundness.lean and the statement
  text only; `Claim.Semantics`, which fixes what the theorem says, lives in Semantics.lean
  and is not covered by either digest (noted 2026-09-14). (b) The Isabelle
  lemma formalizes the corrigendum's C2 step, whose hypothesis C2.1 is stated for
  `t in R^2`; `in_box` binds `t1 t2 : rat`, so the artifact is the Q-instance of C2, not
  C2. The proof is generic (`blast`) and restating it over `real` is expected to be
  routine, but until that is done the formal statement is not the intended one.
history:
  - 2026-08-16 created E0
  - 2026-08-16 note: an adversarial pass (independent from-scratch math
    re-derivation + checker fuzzing; see
    research/reports/phase1-slice1-planar2r-exact-witness.md) found no
    counterexample against the flagship worked instance. This is evidence
    toward E1, not a self-promotion -- tier stays E0 pending an actual human
    read and, for E2, the `referee` skill's hostile+naive subagent review.
  - 2026-08-16 note: standalone derivation note written
    (research/notes/2026-08-16-2r-exact-witness-soundness.md) for human
    review; awaiting confirmation before promotion to E1.
  - 2026-08-17 -> E1 after human read attested by the project owner, together
    with two supplied rigorous proofs (P1, P2) that supersede the note as the
    authoritative argument. P2 proves the main equivalence (Theorem 10.2) and,
    beyond what the note claimed, establishes that the single-chart encoding is
    sound but NOT complete on the torus (Theorem 12.1, explicit rational
    counterexample) -- so "no witness found" must never be read as
    infeasibility (Warning 11.5). RoboCert's status machinery already forces
    that reading; an independent audit confirmed CERTIFIED_INFEASIBLE is
    structurally unreachable from a rejection.
  - 2026-08-17 note (why NOT E2): four naive referees and a negation control
    passed, but the hostile referee run was an ASSISTED audit -- it was handed
    the note's weak points, which BENCHMARK.md SS33 requires be withheld in a
    blind audit. It nonetheless found real defects, all in the NOTE's
    argumentation rather than in the encoding: a fatal-as-warrant citation of a
    test that did not perform the described check (the FK identity had no
    independent trig oracle; one has since been added and its planted-error
    differential measured), a garbled derivation of |B|^2 = L1^2, an
    over-quantified claim in S1, and an unstated quantifier projection in S5.
    Per BENCHMARK.md SS38 a blind independent audit is required before this can
    be called benchmark-verified.
  - 2026-08-17 note: the correspondence obligation P2 SS15 leaves explicitly open
    -- symbol-by-symbol agreement between Definition 10.1 and the shipped
    predicates -- was discharged PASS by an independent audit (exact
    coefficient identity on 108 instances covering every degeneracy the proof
    names; the F_x/F_y half is a proof by linearity). That audit found one
    substantive defect OUTSIDE this claim: the shared checker silently ignored
    non-EXISTS quantifier blocks and would accept a false `forall` claim from a
    single witness. Fixed and regression-tested before this entry was written.
  - 2026-08-17 note: the MVP puts P2 Theorem 13.5 into the shipped path. The
    four-chart driver (src/robocert/certify2r.py) runs this encoding at all four
    sign-flipped link-length pairs, so the torus-completeness gap of P2 Theorem
    12.1 is closed for the CLI. The build guard on link lengths was relaxed from
    `> 0` to `!= 0` to permit it, matching P2 hypothesis (H1) and clearing the
    correspondence audit's finding F6. Theorem 12.1's own instance is now a
    regression test: rejected on the principal chart, certified on chart (pi, 0).

  - 2026-08-24 note: RCMPVB-20260821-CROSS-X-RUN001 stopped with substantive
    findings in both Codex blind audits (A-002). The central pointwise geometry
    survived, but the frozen packets did not explicitly discharge the bounded
    existential, full rational-syntax, and hypothesis/scope obligations; P2 also
    lacked an explicit sign bridge to the frozen FK definitions. Claude proof
    audits were blocked before inference by the provider session limit. Tier
    remains E1; RUN001 is not reusable for promotion, and production registration
    was removed pending a newly frozen repaired run.
  - 2026-08-24 note: a frozen-task corrigendum was drafted to address A-002.
    It is not covered by the 2026-08-17 human attestation; a project-owner
    line-by-line read is required before the repaired proof package may enter a
    fresh E1-to-E2 referee run.

## RC-003

statement: The planar-2R claim shape can be extended from exact task-point
  equality `P(q) = P*` to a pose tolerance `||P(q) - P*|| <= tol`, encoded as a
  single additional polynomial inequality after clearing `D1^2 D2^2`, without
  disturbing the soundness of the remaining conjuncts.
tier: EX
depends: [RC-002]
proof: research/ATTEMPTS.md (A-001 exact rational counterexample)
target_checker: not implemented; this refuted claim must never justify a checker
referee: none
history:
  - 2026-08-17 created E0. Motivated by the MVP: the forward-kinematics conjunct
    is an exact equality, so a rationally reconstructed witness essentially never
    satisfies it for an independently chosen target. The MVP works around this by
    certifying the point the witness exactly reaches and reporting the exact
    deviation from the requested one. A genuine pose tolerance is the better
    engineering model -- real tasks have one -- but proofs P1 and P2 establish the
    encoding's equivalence for exact equality ONLY, so shipping it would be
    shipping unproved mathematics. Needs its own proof before it needs code.
  - 2026-08-24 -> EX after A-001 refuted the remaining-conjuncts-unchanged
    route. At a tolerance-feasible, singularity-boundary rational witness, the
    old target-based second-segment formula certifies clearance while the
    obstacle centre lies on the actual second link. RC-005 replaces the virtual
    target endpoint with the rationalized actual endpoint.

## RC-004

statement: Converting a radian joint interval to an exact rational
  `t = tan(q/2)` box by rounding INWARD is a conservative under-approximation:
  the set of configurations the resulting box admits is a subset of the set the
  requested radian interval admits.
tier: E0
depends: []
proof: research/proofs/rc004-joint-limit-inward-rounding.md (E0 draft;
  exact principal-chart implementation correspondence, not owner-reviewed)
target_checker: n/a (an input transformation, not a certificate family)
referee: none
history:
  - 2026-08-17 created E0. `tan(q/2)` is irrational for generic rational radian
    limits (P2 SS3), so the exact rational IntervalDomain cannot represent a
    user's stated joint limits. Rounding inward can only reject a valid witness
    near a limit (incomplete, safe); rounding outward would accept configurations
    violating the user's limits (unsound). The direction is therefore
    soundness-relevant and belongs in the ledger rather than in a code comment,
    even though the argument is short. Currently supported by a property test
    over sampled intervals, not by a proof.
  - 2026-09-24 exact endpoint-enclosure repair at f350551 and E0 argument written.
    The old libm comparison could round outward. The new supported range is
    [-31/10, 31/10], strictly inside the principal chart; unsupported intervals
    reject, and an empty inward grid rejects. No tier change or checker registration.

## RC-005

statement: On the principal tangent-half-angle chart, the polynomial formula
  consisting of the exact pose-tolerance inequality
  `tau^2 D1^2 D2^2 - Fx^2 - Fy^2 >= 0`, exact singularity polynomial, and two
  homogeneous point-to-segment case splits whose endpoints are the actual
  rationalized points `p0`, `p1(t)`, and `p2(t)`, is pointwise equivalent, for
  every `t = (t1, t2)` in R^2, to pose tolerance, both actual-link clearances,
  and the Jacobian determinant margin; restricting both sides to the same exact
  rational closed t-box, with `t` ranging over its real points, preserves
  bounded existential equivalence.
tier: E0
depends: [RC-002]
proof: research/proofs/planar-2r-pose-tolerance-witness-proof-rc005.md
target_checker: not yet implemented; proposed future family
  "planar2r.pose_tolerance_witness" and checker
  "robocert.planar2r_pose_tolerance_witness" version "0.2.0"
referee: none
mechanized:
  - rocq: formal/rocq/RoboCert/Planar2R.v pythagorean_identity,
    segment1_nondegenerate_identity, segment2_nondegenerate_identity,
    segment1_zero_implies_length_zero, segment2_zero_implies_length_zero (algebraic
    identities over Q supporting the nondegeneracy of both encoded segments)
  - isabelle: formal/isabelle/RoboCert/Planar2R.thy bounded_existential_transport,
    singleton_box_admits_its_point, empty_box_forces_false (the box-restriction step
    and the `a_i <= b_i` box semantics)
fidelity: Recorded 2026-09-11 by reading the declarations against this entry and its
  proof; no independent comparison was performed. Together these cover supporting facts,
  not this entry's statement. (a) Rocq states identities over Q; the proof's pointwise
  equivalence (7.1) is asserted "for every finite real (t1,t2)", so the Rocq lemmas are
  the Q-instances of facts the proof uses over R. Rocq's own scope note excludes the `Seg`
  three-branch analysis and all implementation correspondence. (b) The Isabelle transport
  binds `t1 t2 : rat`, while the proof applies the existential to the real box
  (Section 7) and `formal/RoboCert/Semantics.lean` reads this entry's bounded existential
  as ranging over R. (c) Resolved 2026-09-15: `statement:` now fixes `t` in R^2 for both
  the pointwise equivalence and the bounded existential, matching the proof. A checker
  exhibiting a rational witness still establishes the real existential, since a rational
  point of the box is a real one. With the domain fixed, (a) and (b) are confirmed
  divergences: the Rocq and Isabelle declarations are the Q-instances of steps this entry
  states over R, and neither yet mechanizes the statement as written.
  Nothing here is changed by recording it. Lean does not mechanize this entry; its
  Semantics.lean mentions RC-005 only to exclude it from the Q semantics.
history:
  - 2026-08-24 created E0 with a self-contained argument covering tolerance
    denominator clearing, both actual geometric segments, selector coverage and
    seams, nondegeneracy, singularity, closed-box boundaries, rational syntax,
    existential semantics, and explicit implementation-correspondence
    obligations. Awaiting project-owner line-by-line read before E1; no
    production implementation or registration is authorized at E0.
  - 2026-08-28 note: three mutually isolated `adversary` subagents, each given a
    claim-only packet and denied every proof/ledger/benchmark path, searched for
    a counterexample to the pointwise and bounded-existential equivalences. None
    was found. Tier stays E0 -- an adversary finding nothing is a coverage
    statement, not evidence of soundness, and cannot substitute for the owner
    read or the referee protocol. Log:
    research/notes/2026-08-28-rc005-adversary-search.md. Substantive results:
    (a) the two scalar conjuncts reduce to exact rational-function identities
    `T == D^2(tau^2 - ||p2-P*||^2)` and `G == D_2^2(detJ^2 - eps^2)` with
    nowhere-vanishing denominators, so they hold for all REAL t, not only
    rational -- no irrational counterexample to them exists; (b) all three agents
    independently found that the generic `Seg` construct is UNSOUND at `Q_ = 0`
    (branch III fires vacuously and reports clearance for a centre inside the
    disc), reachable only by violating `L1, L2 != 0` -- RC-005 is safe as stated,
    but the `Q_ > 0` side condition belongs on `Seg` itself before any reuse for
    prismatic joints, uncertain link lengths, or swept segments; (c) with
    `eps > 0` the chart's unreachable set is exactly the circle `q1 = pi`, no
    chart-offset parameter exists, and an exact instance is recorded where the
    physical problem is feasible while both sides of the bounded claim are false;
    (d) an exact `Q(sqrt 7)` instance is satisfiable with no rational witness in
    the box, a regression fixture for "search failure must return UNKNOWN";
    (e) `tau >= 0` and `a_i <= b_i` are inert, while `R >= 0`, `eps >= 0` and
    non-vanishing `L1, L2` are load-bearing and tight.
  - 2026-09-15 statement clarified, no tier change: `t` ranges over R^2 for both the
    pointwise equivalence and the bounded existential. The earlier wording left the domain
    unstated, which AGENTS.md sections 1 and 59 do not permit. R was chosen because the
    proof argues over R (equation 7.1, "for every finite real (t1,t2)") and the geometric
    claim concerns real configurations. The quantifier order is unchanged, so this narrows
    an ambiguity rather than changing the claim. The project owner delegated the choice to
    the recommendation that proposed R.

## RC-006

statement: `src/robocert/sos.py::verify` accepts a Positivstellensatz certificate
  `(target, gamma, {g_i}, {h_j}, {sigma_k}, {lambda_j})` only when every Gram matrix is exactly
  positive semidefinite over Q and the identity
  `target - gamma = sigma_0 + sum_i sigma_i g_i + sum_j lambda_j h_j` holds exactly as
  polynomials; consequently an accepted certificate establishes `target >= gamma` on
  `K = {x : g_i(x) >= 0, h_j(x) = 0}`.
tier: E0
depends: []
proof: research/proofs/rc006-sos-verifier-correspondence.md (E0 draft;
  typed-input acceptance implies exact PSD and identity, not owner-reviewed)
target_checker: not registered and not a `checking.Checker`. `src/robocert/sos.py` is a
  verification utility bound to no certificate family; binding one is a separate,
  evidence-gated change
referee: none
history:
  - 2026-08-31 created E0 alongside the exact-algebra core
    (`src/robocert/polynomial.py`, `src/robocert/linalg_exact.py`, `src/robocert/sos.py`). The
    module is deliberately NOT a `Checker`: that protocol requires a `certificate_family`, and
    RC-001 -- which claims the SOS scheme suits the planar-2R singularity-margin reduction -- is
    E0, so there is no family it may legally bind to. What this entry claims is narrower than
    RC-001 and independent of it: not that SOS is the right scheme for any robot question, only
    that this code decides the stated algebraic condition.
  - 2026-08-31 note: two soundness-relevant decisions are load-bearing and were chosen to fail
    closed rather than to be permissive. (a) The exact PSD test refuses a zero diagonal entry
    whose row does not vanish; a naive LDL^T that skips zero pivots accepts `[[0,1],[1,0]]`,
    which is indefinite, and would let a caller certify `x*y` as a sum of squares. (b) A
    certificate carrying no SOS block is rejected rather than reducing the identity to a
    statement about equality multipliers alone, which would say nothing about nonnegativity.
    Both have dedicated tests. Neither is established by those tests -- a passing test is not a
    proof, and this entry stays E0 until the correspondence argument is written and read.
  - 2026-09-24 E0 implementation-correspondence argument written against the
    current exact-algebra utility. No tier change, robot-property suitability
    claim, certificate-family binding, or production checker registration.

## RC-007

statement: `src/robocert/refutation.py::refute` returns an accepted `RefutationReport`
  only when (i) every quantifier block of the serialized `Claim` is `forall`, (ii) the
  assignment gives exactly one `Rational` value to each declared variable and no other,
  (iii) each value lies in its declared interval with open and closed endpoints honoured,
  and (iv) the claim's whole formula evaluates to false at that point in exact rational
  arithmetic; consequently an accepted `CheckedCounterexample` establishes the negation of
  the serialized universal claim, whether its variables are read as ranging over Q or over
  R, since a rational point of the box is a real point of it.
tier: E0
depends: []
proof: research/proofs/rc007-refutation-correspondence.md (E0 draft; includes the
  correspondence argument for `checkers.evaluate_formula`, which guard (iv) delegates to).
  The elementary logical step is that one in-domain point where the formula is false refutes
  a purely universal claim. The implementation-correspondence argument that the shipped code
  decides (i)-(iv) and nothing weaker still requires the project-owner E1 read and fresh
  referee protocol. Tests are supporting implementation evidence, not that review:
  tests/test_refutation.py, tests/test_simulation.py, tests/test_schemas.py
target_checker: none. `refute` is not a `checking.Checker` and binds no certificate family;
  it gates the `COUNTEREXAMPLE` status via `results.counterexample_result`
referee: none
history:
  - 2026-09-11 created E0. Entered after the fact: `refute` shipped and was exported with
    no ledger entry, on the argument (docs/architecture/trusted-computing-base.md, "The
    second promotion path") that refutation is elementary and so needs no evidence gate.
    That argument covers the mathematics, not the code, and RC-006 had already set the
    precedent that code-to-condition correspondence is itself a claim. The omission is
    worth recording because the gap is sharper here than for RC-006: `sos.py` is registered
    nowhere, while `refute` sits on a live path to a result status. Whether that path
    should stay open while this entry is E0 is the owner's decision; this entry does not
    make it.
  - 2026-09-15 defect found and repaired, no tier change. Reading the code against
    guards (ii)-(iv), in preparation for a written argument, found that `refute` looked
    values up in the caller's Mapping separately for the type check, the domain check,
    evaluation, and recording. A Mapping is not obliged to return the same value twice, so
    one could pass the checks at q = 3/4 and have q = 5, outside the domain, recorded in an
    accepted CheckedCounterexample. Planted non-idempotent mappings reproduced this on the
    unrepaired code. Separately, unrelated keys of mixed types raised TypeError instead of
    being rejected. Repair: the mapping is read once, keys must be distinct strings, and
    each value is rebuilt as a plain Rational from a single read; every later step uses only
    that snapshot. Regression tests:
    tests/test_refutation.py::test_a_checked_counterexample_survives_its_own_recheck (the
    invariant that a recorded witness must itself refute the claim) and
    ::test_unrelated_keys_of_mixed_types_are_rejected_not_raised. Each guard was correct in
    isolation. The defect was that they did not concern the same point, which is exactly the
    kind of gap only a correspondence argument, not the logic, can expose. Still no written
    argument, so still E0. Gating, delegated by the owner: the library API stays, and `refute`
    is not to be wired into the CLI or any report until this entry has an owner read (E1).
  - 2026-09-15 note: the E0 implementation-correspondence argument was written at
    research/proofs/rc007-refutation-correspondence.md against the repaired code. It includes
    the exact polynomial/predicate/Boolean evaluator rather than assuming guard (iv), records
    that the supplied model digest is a binding rather than a correspondence proof, and keeps
    assumptions explicit. No owner read or independent referee review has occurred; tier stays
    E0 and the CLI/report gate remains closed.
