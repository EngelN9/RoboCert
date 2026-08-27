# Phase 1 Slice 1 — planar-2R single-instance witness checker (exact-rational certificate)

> **Historical checkpoint, not current delivery status.** On 2026-08-24 the
> unrefereed family was removed from the production registry. RC-002 remains E1
> after frozen run `RCMPVB-20260821-CROSS-X-RUN001` found substantive
> proof-packet omissions. The public CLI now returns `UNKNOWN`; the checker is
> exercised only under explicit research-test registration.

## 1. Statement and conventions

Target theorem this slice is one instance of (`AGENTS.md` §68, `README.md` §32,
`ROADMAP.md` Phase 1):

```
forall theta in Theta, forall x in T, exists q in Q:
  F(q, theta) = x  AND  C(q, theta)  AND  S(q, theta)
```

for a planar 2R robot under interval link-length uncertainty (`theta`), a task
region (`x`), joint limits, one circular obstacle (`C`), and a singularity
margin (`S`).

This slice does **not** attempt that theorem. It certifies one fixed rational
instance: given link lengths `L1, L2`, a target tool point `(x, y)`, a circular
obstacle, and a singularity-margin bound `epsilon`, it certifies existence of a
witness configuration `q = (q1, q2)` — represented via the tangent-half-angle
substitution `t = tan(q/2)`, never as a raw angle — satisfying forward
kinematics, joint limits, obstacle clearance, and the singularity margin,
simultaneously, exactly, per the registered checker described below. `L1, L2,
x, y`, and the obstacle are fixed rational constants, not quantified variables
(`src/robocert/kinematics2r.py` module docstring states this identically).
`q = pi` is excluded by construction: only finite rational `t` bounds are
used, and `t -> +-inf` only as `q -> +-pi`.

## 2. Status summary

| Claim | Tier | One-line status |
|---|---|---|
| `RC-001` | `E0` | SOS-based certificate scheme intended to hold for all theta (link-length uncertainty), for the singularity margin. Not attempted by this slice; remains open. |
| `RC-002` | `E1` | The tangent-half-angle + case-split polynomial encoding this slice's checker implements. Human read attested, and two rigorous proofs supplied (`research/proofs/`). Not `E2`: the hostile referee pass was an *assisted* audit (§7), and `BENCHMARK.md` §38 requires an independent blind audit. |

## 3. Dependency graph

Both entries have `depends: []` — no dependency edges yet. `RC-002`'s
`target_checker` field points to `src/robocert/checkers.py`. At this historical
checkpoint it was registered as `"planar2r.exact_witness"`; that registration
has since been quarantined pending E2.

## 4. Results

At this historical checkpoint, the registered `"planar2r.exact_witness"`
checker (`ExactWitnessChecker`,
`checker_id="robocert.planar2r_exact_witness"`, `checker_version="0.1.0"`,
`arithmetic_mode="exact-rational"`) accepts a `Certificate` for the flagship
instance — `L1=L2=5`, witness `t1=1/2, t2=-1/3`, target `(39/5, 27/5)`,
obstacle center `(4,-3)`, radius `49/10`, clearance margin `1/10`,
`epsilon=1` — through the real `verify_certificate` gate, producing a
`CheckedCertificate` and, via `certified_result`, a `CertificationResult`
with `status == ResultStatus.CERTIFIED_FEASIBLE`
(`tests/test_checkers.py::test_positive_witness_is_certified_feasible`).
This obstacle-clearance boundary is exact-equality, not generic: segment 1's
distance to the obstacle equals the required clearance exactly (found
independently in the adversarial pass, §7), which the checker's non-strict
`>=` predicate correctly accepts.

Every predicate involved — the two FK identities, the singularity-margin
inequality, and the thirteen obstacle-clearance predicates (two segments,
three cases each, one shared) — is evaluated by the checker with Python
`fractions.Fraction` arithmetic only; no floating point appears anywhere in
the checked path (`src/robocert/checkers.py::evaluate_polynomial`/
`evaluate_formula`).

The checkpoint recorded 79 passing tests across the full `src/robocert` package
(`tests/test_kinematics2r.py`: 11, `tests/test_checkers.py`: 20, plus the
pre-existing Phase 0 suite: 48), `mypy --strict src/robocert` reports no
issues, `ruff check` reports no issues, at the current uncommitted working
tree (§8).

## 5. Negative results and limitations

Verbatim from `src/robocert/kinematics2r.py`'s module docstring — this slice
does not prove:

- Coverage holding for all theta over any link-length interval — `L1, L2` are
  fixed constants baked into predicate coefficients.
- Coverage holding for all x over any task-region box — `(x, y)` is a fixed
  constant.
- Simultaneous worst-case behavior across reachability, joint limits,
  clearance, and singularity margin under any uncertainty — the four
  sub-claims are checked at one shared witness for one instance.
- Anything about the `q = pi` chart boundary beyond excluding it by
  construction (finite rational `t` bounds only).

**Chart incompleteness, now proved rather than suspected.** Proof P2
Theorem 12.1 supplies explicit rational data (`L1 = L2 = 1`,
`P* = (-1,-1)`, `C = (0,-1/2)`, `R = 3/10`, `eps = 1/2`) for which the
configuration `q = (pi, pi/2)` meets every geometric condition while the
polynomial system has no real solution at all. The encoding is therefore
sound but not complete on the configuration torus, and — the consequence
that matters operationally, P2 Warning 11.5 — **"no witness found" does not
establish that no configuration exists.** RoboCert's status machinery
already enforces the safe reading: the checker refuses a certificate whose
conclusion is `infeasible`, and every rejection reaches the caller as
`UNKNOWN`. The independent audit in §7 confirmed by execution that no code
path leads from a rejection to `CERTIFIED_INFEASIBLE`. P2 §13 gives a repair
(four sign-flipped copies of the same predicate, recovering completeness on
the torus); it is not implemented, and the current positivity guard on link
lengths would have to be relaxed to admit it.

`RC-001`'s SOS-based certificate scheme for the singularity margin, intended
to hold for all theta, was not attempted; it remains open at `E0` with no
work against it yet.

## 6. Where to attack

Ranked by the author's own judgment of where this is weakest. Items 1–3 of the
previous revision have been addressed and are recorded in §7; these are what
remain.

1. **No blind audit has been performed.** The hostile referee pass was
   *assisted* — it was handed the weak points, which `BENCHMARK.md` §33
   requires be withheld from a blind audit. It found real defects anyway, but
   per §5 and §18 an assisted result cannot stand in for independent defect
   discovery, and §38 makes a blind audit a precondition for calling anything
   benchmark-verified. This is the single reason `RC-002` sits at `E1`.
2. **The parameter-level correspondence rests on instance checking, not a
   symbolic proof.** The independent audit (§7) established exact
   coefficient identity between the shipped clearance predicates and proof P2's
   Definitions 7.1/8.1/9.1 across 108 instances covering every degeneracy the
   proof names — but that is exhaustive-in-practice, not a proof over the
   parameter field. (The `F_x`/`F_y` half *is* a proof: those coefficients are
   linear in `(L1, L2, x, y)`, so agreement at spanning points settles it.)
   Closing the remainder needs a symbolic check.
3. **Single-chart scope is a real limitation, now proved so.** P2 Theorem 12.1
   gives explicit rational data with an admissible configuration the encoding
   cannot represent. The four-chart repair (P2 §13) is not implemented, and
   `build_planar2r_claim`'s `l1 > 0, l2 > 0` guard actively forecloses it —
   the repair needs `L_i != 0` with sign flips.
4. **The untrusted candidate generator (`witness_search2r.py`) only
   implements the "pick a rational witness first, derive the target from it"
   direction.** The harder direction — an independently-chosen target point,
   solved numerically, then rational-reconstructed — is documented but not
   built, so nothing has exercised the checker's behavior on a
   float-reconstruction-then-rejected witness yet.

## 7. Verification methodology

Two layers, run independently of each other:

- **Property tests** (`tests/test_kinematics2r.py`, written alongside the
  implementation): Hypothesis-driven cross-checks of the FK identity against
  its own from-scratch trig re-derivation inside the test, the singularity
  margin against `math.sin`, and the checker's clearance case selectors
  against a hand-written numeric point-to-segment distance function, plus
  explicit boundary/degenerate-case tests (zero-width joint domain,
  zero-length link, the `t=huge` chart-boundary check, the exact-equality
  obstacle-contact case).
- **Adversarial pass** (this session, via the `adversary` subagent,
  `.claude/agents/adversary.md`, full read access to the implementation — a
  post-hoc audit, not a blind search, since there is no separate soundness
  argument being hidden from it): independently re-derived FK, clearance, and
  the singularity margin from scratch (no import of `robocert` code) in
  Phase A; then, in Phase B, solved for and tested the *other* real IK branch
  reaching the same target point (found to correctly violate clearance and be
  correctly rejected by the checker), grid-searched for spurious extra FK
  roots (601x601, found none beyond the two real branches), solved exactly
  for the obstacle-clearance selector's repeated-root boundary (elbow
  landing exactly on the obstacle center — correctly rejected by the
  checker), cross-checked the checker's clearance-case-split evaluation
  against an independent exact-Fraction distance function over 3201 rational
  samples (a 201-point grid plus 3000 random samples, denominators to 5
  digits, seed 12345) with zero mismatches, and fuzzed the checker's
  `Certificate` payload parsing (non-canonical rationals, huge unreduced
  values, wrong-cased keys) — all correctly rejected by the checker. No
  counterexample was found. This is the evidence toward AGENTS.md §68
  completion criterion 4 ("an adversarial counterexample search finds no
  valid contradiction"); it does not by itself promote `RC-002`'s tier (§6
  item 2).

- **Referee pass, labeled `assisted_audit`** (`BENCHMARK.md` §18). Four
  `referee-naive` agents checked isolated context-free implications (the
  squaring equivalence, the elbow-norm identity, and both cleared
  distance forms stated separately so a discrepancy would surface as
  disagreement); all held. A **negation control** on the squaring step was
  correctly refuted, so the pipeline demonstrably discriminates on this
  material rather than agreeing with whatever it is handed. The
  `referee-hostile` pass was assisted and must not be counted as independent
  discovery — but it rejected two of the three attack angles it was given
  ("S3 is the soundest step in the note"; the segment asymmetry "does not
  land", with its own re-derivation showing both forms correct) and instead
  found three defects that had not been suggested to it, all in the *note's
  argumentation* rather than in the encoding. It also independently
  rediscovered the degenerate branch that P2 proves as Remark 9.5.
- **Planted-error calibration, now performed** (the gap this section
  previously recorded as outstanding; `BENCHMARK.md` §42). The referee's
  central finding was that the note cited a test as an independent
  cross-check when that test derives its inputs from the same half-angle
  forms the encoding uses. Confirmed: no `math.cos` existed anywhere in the
  kinematics tests. Corrupting the *shared* assumption (sine convention
  flipped in both the encoding and that test's own derivation) gives a
  measured differential — the self-referential test **passed**, blind to it;
  the newly added independent trig oracle **failed**, catching it. Both
  files were restored and the full suite re-run.
- **Implementation-correspondence audit** (`PASS`), discharging the one
  obligation proof P2 §15 explicitly declines to cover: symbol-by-symbol
  agreement between Definition 10.1 and the shipped predicates. Method: exact
  coefficient identity on 108 instances, including `(x,y) = (-L1, 0)`,
  `C = O`, `C = P*`, the Thales case, and the vacuous-margin regime, against
  a reimplementation written from the proof text rather than from the code.
  It confirmed the Boolean structure and selector/distance pairing, verified
  that `CERTIFIED_INFEASIBLE` is structurally unreachable from any rejection,
  and found one substantive defect *outside* this claim: the shared checker
  silently ignored non-`EXISTS` quantifier blocks and would accept a false
  `forall` claim from a single witness. Fixed and regression-tested
  (`test_forall_quantifier_is_rejected_not_silently_ignored`). Its two minor
  findings were also actioned: the vacuous-margin regime is now refused at
  build time per P2 Corollary 5.4, and the sub-formula evaluators were
  removed from the public surface per P2 Remark 9.5.

## 8. Reproducibility manifest

```yaml
repo: C:\Users\User\Documents\GitHub\RoboCert (uncommitted working tree --
  repository has one prior commit, 42aa49a "Initial RoboCert research
  protocol"; everything described in this report is untracked/modified on
  top of it, not yet committed)
python: >=3.11 (see pyproject.toml); mypy python_version 3.11; ruff
  target-version py311
dependencies: none at runtime (pyproject.toml dependencies = []); dev deps
  hypothesis, jsonschema, mypy, pytest, ruff, build
commands:
  - .venv/Scripts/python -m pytest -q          # 79 passed
  - .venv/Scripts/python -m mypy src/robocert   # no issues
  - .venv/Scripts/python -m ruff check src/robocert tests  # no issues
seeds: 12345 (adversarial pass's random rational sampling); Hypothesis's own
  internal seeding for property tests (not separately pinned)
models: this report and the code it describes were produced in a Claude Code
  session; see §9 for role breakdown
date: 2026-08-16
```

## 9. Disclosure

All code (`kinematics2r.py`, `checkers.py`, `witness_search2r.py`, the
`checking.py` registration edit) and all tests were written by Claude in this
session, including the FK/clearance/singularity-margin polynomial derivation.
The adversarial pass (§7) was run by a separate subagent instance
(`.claude/agents/adversary.md`) with no memory of how the encoding was
derived. Two candidate proof documents now exist in `research/proofs/`, and a
human has read them; accordingly `research/CLAIMS.md` records `RC-002` at `E1`.
This does not constitute the fresh hostile/naive cross-provider review required
for `E2`. The reproducible v2 blind cross-verification run remains pending and
must preserve its ledger, isolated audits, negation control, adjudications, and
implementation-correspondence evidence before any promotion. All
numerical/property-test claims in this report are machine-checked (`pytest` exit
status); the "no counterexample found" claim rests on the adversarial pass's
search coverage as stated in §7, not on a completeness proof.
