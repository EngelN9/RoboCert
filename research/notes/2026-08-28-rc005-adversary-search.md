# RC-005 adversary search, 2026-08-28

**E0 exploratory record.** This is a search log, not an argument and not a review.
Finding no counterexample is not evidence of soundness at any tier; it is a
statement about coverage. RC-005 remains `E0` and is unaffected by this file
except for the history note that points at it.

## Protocol

Three `adversary` subagents (`.claude/agents/adversary.md`) were dispatched in
parallel, in mutually isolated fresh contexts, per `research/README.md` rule 2 and
`.claude/CLAUDE.md` #5. None shared context with any other, and none shared context
with whatever produced the RC-005 argument.

Each received a **claim-only packet** — the geometric statement, the definitions of
`T`, `G`, `Seg(U,V)`, `Phi_005`, the box atoms, and the §1 data hypotheses — and was
explicitly denied `research/proofs/**`, `research/notes/**`, `research/CLAIMS.md`,
`research/ATTEMPTS.md`, `research/OBSTRUCTIONS.md`, `benchmarks/proof-verification/**`,
`docs/architecture/phase1-pose-tolerance-mvp-gates.md`, and
`src/robocert/kinematics2r.py`. All three reported opening no forbidden path.

Packet: `rc005-claim-packet.md`, SHA-256
`4d370ade2e169464fcae671bd4872e3d503090187bb152a28286d1a926aed67d`
(session scratchpad; not a repo artifact).

Assigned focus:

| Agent | Focus |
|---|---|
| A | the two clearance conjuncts `Phi_1 = Seg((0,0),A)`, `Phi_2 = Seg(A,B)` |
| B | the scalar conjuncts `T` (pose tolerance) and `G` (singularity) |
| C | `(C-bounded)`, the box, and the chart |

## Outcome

No agent produced a counterexample to either `(C-pointwise)` or `(C-bounded)`.

Agents A, B and C each independently reduced part of the encoding to **exact
symbolic identities** over `Q`, rather than resting on evaluation:

- `Q_ == L1^2 D^2` for `Phi_1` and `Q_ == L2^2 D^2` for `Phi_2` (A, C)
- `H_I == cross(W,N)^2 - R^2 D^2 Q_` for both instantiations (A)
- `T == D^2 (tau^2 - ||p2 - P*||^2)` (B)
- `G == D_2^2 (detJ^2 - eps^2)` (B), equivalently `4 L1^2 L2^2 t2^2 - eps^2 D_2^2` (A, C)

Because the last two are rational-function identities whose denominators vanish
nowhere (`D >= 1`), they range over **all real** `(t1,t2)`, not only rational ones.
No irrational counterexample to the two scalar conjuncts can exist. This is a
stronger statement than any finite search supports, and it is the most substantive
thing the run produced.

Aggregate exact-rational evaluation across the three agents is on the order of 10^7
instances with zero disagreements, every conjunct compared independently rather than
only in conjunction, and every §1 hypothesis asserted before evaluation. Agent A
additionally ran a 14-mutant differential test, killing 12; the two survivors are
the redundancy recorded under F2 below.

## Findings

### F1 — `Seg` is unsound at a degenerate segment, and the side condition is on the wrong object

All three agents converged on this independently.

If `Q_ = 0` (i.e. `U = V`), then `Z = 0` and `H_I = H_A * Q_ - Z^2 = 0`, so branch III
of `Seg` fires unconditionally and `Seg` reports clearance **regardless of the actual
distance** — including for an obstacle centre strictly inside the disc. Agent C
measured this directly: 78,975 exhaustive degenerate cases, 29,364 wrong. Agent A's
minimal instance: `L1 = 0, C = p0, R = 1`, true distance `0 < 1`, `Phi_1` true.

This is **not** a counterexample to RC-005. Every such instance violates §1's
`L1 > 0, L2 > 0`, and the identities `Q_ == L1^2 D^2`, `Q_ == L2^2 D^2` with `D >= 1`
put `Q_ >= L1^2 > 0` and `Q_ >= L2^2 > 0` on all admissible data. RC-005 is safe as
stated.

The observation is that `Q_ > 0` is a precondition of the **generic `Seg` construct**,
discharged for RC-005 only by a fact about its two call sites. A reuse of `Seg` for a
segment whose length can vanish — a prismatic joint at zero extension, a variable or
uncertain link length, a collapsed swept segment between two poses — inherits a silent
"clear" verdict in the unsound direction. Agent B's recommendation, independently
reached: the `Q_ > 0` side condition belongs on `Seg` itself, not only on `L1, L2 > 0`.

Relevant beyond RC-005: `Seg` is the natural construct to carry into Phase 4 C-space
collision regions and Phase 5 uncertain link lengths, where a vanishing `Q_` stops
being excluded by hypothesis.

### F2 — branch III's guards are redundant, in the sound direction only

`H_I >= 0` with `Q_ > 0` already asserts line-distance `>= R`, and segment-distance
dominates line-distance, so branch III is sound unguarded. Agent A's mutants M6/M7,
dropping one or both guards, survived 8,000 exact cases; a dedicated scan found
185,410 cases with `H_I >= 0` and `Z` outside `[0,Q_]`, none with clearance actually
failing. Dropping branch A or branch III instead breaks the encoding immediately
(3,024 and 1,659 disagreements).

Recorded as an observation about the encoding, not a defect. Redundancy that fails
safe is not a soundness problem, but a checker implementing `Seg` should not have the
guards silently optimized away either — that is a correspondence question, not a
mathematical one.

### F3 — the chart hole is a specific circle, and there is no chart-offset parameter

`q_i = 2 arctan t_i` ranges over the open `(-pi, pi)`, so no finite `t` names
`q_i = pi`. RC-005 §1 already disclaims torus completeness. What the search adds is
the exact shape and an instance.

Agent C: `L1 = L2 = 1`, `P* = (-1,-1)`, `C = (1/2,-1/2)`, `rho = 3/5`, `mu = 0`,
`tau = 0`, `epsilon = 0`. All §1 hypotheses hold. The configuration `q = (pi, pi/2)`
satisfies all four geometric conditions exactly (`|p2-P*|^2 = 0`; `dist^2 = 1/2 >= 9/25`;
`dist^2 = 9/4 >= 9/25`; `|det J| = 1 >= 0`), and `tau = 0` forces the IK set to exactly
`{(pi, pi/2), (-pi/2, -pi/2)}`. The only finite-`t` member is `t = (-1,-1)`, where
`Phi_1` fails (`dist^2 = 1/4 < 9/25`). Exhaustive exact sweep of 802,401 points
confirms one point with `T >= 0`. So both sides of `(C-bounded)` are false for every
admissible box while the physical problem is feasible.

Both sides share the gap, so `(C-bounded)` survives — this is a scope limit, not a
refutation. The additions worth keeping:

- the unreachable set is `{q1 = pi} ∪ {q2 = pi}` in `T^2` — two circles, 1-dimensional,
  not isolated points;
- with `epsilon > 0` the `q2 = pi` circle is excluded anyway (`sin pi = 0`), so the
  residual hole is **exactly the circle `q1 = pi`**;
- its location is an artifact of the chart origin, and §1/§2 expose **no chart-offset
  parameter**, so the hole cannot be moved off a region of interest;
- the gap bites only when the physical feasible set is nonempty and contained in
  `{q1 = pi} ∪ {q2 = pi}`, hence (being closed) has empty interior. `tau = 0` is the
  clean trigger. Agent C did not construct a `tau > 0` trigger and explicitly did not
  claim one is impossible — that is a stated limit of coverage, not a negative result.

Architectural note: RC-002's four-chart driver (`src/robocert/certify2r.py`, P2
Theorem 13.5) closes the analogous gap for the exact-witness family. RC-005's MVP is
principal-chart only per `docs/architecture/phase1-pose-tolerance-mvp-gates.md`, and
has no equivalent. Whether the MVP wants one is a scoping decision, not a soundness
defect.

### F4 — satisfiable instances whose witness set contains no rational point

Agent C, verified in exact `Q(sqrt 7)` arithmetic with exact sign tests for box
membership: `L1 = 1, L2 = 2, P* = (2,2), C = (0,0), rho = mu = tau = epsilon = 0,
B = [0,1]^2`. All §1 hypotheses hold. Witness `t1 = (4 - sqrt7)/9`, `t2 = sqrt7/7`,
with `|p2 - P*|^2 = 0` exactly. `|P*|^2 = 8` forces `cos q2 = 3/4`, hence `t2^2 = 1/7`,
which has no rational solution. Exhaustive scan of 160,801 rational grid points in `B`
found none.

RC-005 claims no completeness — §7 states no conclusion follows when search fails to
produce a witness, and §8 restricts the negative outcome to `UNKNOWN`. So this is
consistent with the claim. Its value is as a concrete, exactly-verified instance of
the incompleteness the claim already disclaims, suitable as a regression fixture: the
witness search must return `UNKNOWN` here and must never be read as infeasibility.

### F5 — hypothesis tightness map

Agents B and C independently probed which §1 hypotheses do work.

Load-bearing, with exact failure instances if dropped:

- `L1, L2` non-vanishing — see F1. Only `!= 0` is consumed; **negative** link lengths
  are fine (agent C, 40,000 exact samples, seed 403, zero atom mismatches). Note this
  matches the RC-002 build guard already relaxed from `> 0` to `!= 0`.
- `R = rho + mu >= 0` — `H_A >= 0` encodes `dist^2 >= R^2`, strictly stronger than
  `dist >= R` when `R < 0`. Agent C: 15,081 + 13,299 atom disagreements in 40,000
  (seed 402). Agent B minimal instance: `C = p0, R = -1`.
- `epsilon >= 0` — `G` is the squared form; for `epsilon < 0` it encodes
  `|det J| >= |epsilon|`. Agent C: 26,771/40,000 (seed 305). Agent B minimal instance:
  `L1 = L2 = 1, t2 = 0, epsilon = -1`.

Inert:

- `tau >= 0` does no work, because the geometric side is stated in already-squared
  form `||p2-P*||^2 <= tau^2` (agent C, 40,000 exact samples with `tau < 0`, seed 304,
  zero mismatches).
- `a_i <= b_i` does no work for `(C-bounded)`: if violated the box is empty and both
  sides are false. Degenerate boxes verified directly — 40,000 single-point-box
  instances (seed 501) and 4,000 x 41 line-box instances (seed 502), zero failures.
- rationality of the data is consumed by exact evaluation, not by the truth of
  `(C-pointwise)` as a statement about reals.

### F6 — what `(C-bounded)` is and is not equivalent to

Agent C: because single-point boxes `B = [c,c] x [d,d]` with `c,d in Q` are admissible,
`{(C-bounded) for every admissible B}` **implies** `(C-pointwise)` at every rational
point. `(C-bounded)` has no existential slack at `Q^2`, so a rational-point pointwise
defect cannot be washed out by the quantifier. It does not imply `(C-pointwise)` at
irrational points. So `(C-bounded)` is exactly as strong as `(C-pointwise)` on `Q^2`
and strictly weaker off it.

The transport `(C-pointwise) -> (C-bounded)` was reported to consume exactly three
facts: that every element of `B` is a pair of finite reals; that the four non-strict
box atoms cut out the same `B` on both sides; and that both existentials range over
`R^2 ∩ B` rather than `Q^2 ∩ B`. Boundedness is not among them.

## Two packet transcription defects — mine, not RC-005's

Agent C reported two under-specifications. Both are artifacts of how the packet was
written and are **not** present in `research/proofs/planar-2r-pose-tolerance-witness-proof-rc005.md`.
Recording them so they are not mistaken for proof defects:

1. The packet introduced `Seg` as "for vectors `U, V` in `Q[t1,t2]^2`" and dropped the
   proof's phrasing "let a nondegenerate segment have endpoints `U/D` and `V/D`".
   Read literally, `W = C*D - U` then mixes a `D`-scaled centre with an unscaled
   endpoint, which is wrong unless `U, V` are the `D`-homogenizations; agent C measured
   22,452 disagreements in 200,000 exact cases against the literal reading. RC-005 §4
   states the homogenization correctly. The packet did not.
2. The packet's unit paragraph omitted RC-005 §1's sentence placing the input domain
   in "the dimensionless principal-chart coordinates `t_i = tan(q_i/2)`", leaving
   `[a_i, b_i]` without a declared space. Agent C's instance showing the cost of the
   misreading (`B = [-1,1]^2` in `t` admits a witness at `q ≈ (1.5708, 1.5708)` rad,
   ~32.7 degrees outside `[-1,1]` rad in both joints) is a real hazard for a **user-facing
   input format**, but not a defect of the proof.

The second is worth carrying into the problem-schema design whenever schema `0.2.0` is
written: a box field that could be read as either radians or `t` is a user-facing
soundness trap, whatever the proof says.

## Explicitly not stated here

Agent C raised a rationality observation about which joint limits are exactly
representable with rational `t`-endpoints, attributing it to a standard result. Per
`.claude/CLAUDE.md` #4 no literature claim may be stated without a
`research/literature/LIT-xxx.md` entry created via the `cite` skill in the same
session. No such entry was created, so the claim is **not** recorded here and must not
be repeated in any report until it is cited. It is noted only as an open question
bearing on RC-004.

## Coverage limits

Stated so the negative result is not read as broader than it is. Not covered:

- irrational `t` beyond the two `Q(sqrt 7)` points of F4, except where the symbolic
  identities cover all reals;
- a `tau > 0` chart-gap trigger driven by exact clearance tangency;
- `L1/L2` ratios outside `[1/12, 12]` and data magnitudes beyond 30 in agent C's
  atomwise sweeps (agents A and B went to `10^24` and `10^18` respectively on their
  own focus areas);
- boxes wider than `|t| = 10^12`.

## What this does not license

No promotion. No production registration. No checker. RC-005 is `E0`; only a
project-owner line-by-line read moves it to `E1`, and only the `referee` skill's
hostile + naive + negation protocol moves it to `E2`. `research/CLAIMS.md`'s
monotonicity rule additionally caps RC-005 at RC-002's tier while the declared
dependency stands.
