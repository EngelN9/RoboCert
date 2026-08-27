# Soundness argument for RC-002: planar-2R exact-witness polynomial encoding

> **SUPERSEDED AS THE AUTHORITATIVE ARGUMENT (2026-08-17).** Two rigorous
> proofs of this claim now exist and take precedence over this note:
> `research/proofs/planar-2r-exact-witness-proof-p1.md` and
> `research/proofs/planar-2r-exact-witness-proof-p2.md`. This note is retained
> as an informal reading guide and as the historical record of what was argued
> before those proofs existed. Where this note and the proofs differ, the
> proofs win.
>
> **A defect in this note that the proofs exposed.** §0 below claimed a plain
> "if and only if". That is correct *on the half-angle chart* (proof P2,
> Theorem 10.2), but P2 Theorem 12.1 exhibits explicit rational data for which
> an admissible configuration exists on the configuration torus while the
> polynomial system has **no real solution** — the chart omits `q_i = pi`, and
> that omission is not vacuous. The operational consequence, stated as P2
> Warning 11.5 and absent from this note as originally written:
> **"no witness found" does not establish infeasibility.** RoboCert's status
> taxonomy already forces the safe reading (a rejected certificate yields
> `UNKNOWN`, never `CERTIFIED_INFEASIBLE`), but this note should have said so
> and did not. P2 §13 also gives a repair: four sign-flipped copies of the same
> predicate recover completeness on the torus.

This is a standalone reading of the argument behind `RC-002` in
`research/CLAIMS.md`, meant to be read and judged on its own — not the
implementation (`src/robocert/kinematics2r.py`), which this argument is
*about*, not a substitute for reading. Writing and testing code is a
different act from reading it to judge whether it's actually sound; this note
exists to make that second act possible without wading through the source.

## 0. What is being claimed

For a planar 2-link robot (shoulder at the origin, revolute joints with
angles `q1, q2`, rigid links of length `L1, L2 > 0`), fixed rational
constants `x, y` (target tool point), `cx, cy, r` (obstacle center and
radius), `mu > 0` (clearance margin), and `epsilon > 0` (singularity margin):
there is a system of polynomial predicates over two real variables `t1, t2`
(standing for `tan(q1/2)`, `tan(q2/2)`) such that the predicates hold at
`(t1, t2)` **if and only if** the corresponding configuration `q = (q1, q2)`
(a) reaches `(x, y)` exactly, (b) keeps both arm segments at distance `>= r+mu`
from the obstacle center, and (c) satisfies `|det J(q)| >= epsilon`. The claim
is about the *equivalence* — that checking the polynomials is exactly as
strong as checking the original geometric conditions, no weaker (a gap here
would let the checker accept invalid configurations) and no stronger (a gap
here would make it reject valid ones, which is safe but was worth ruling out
too).

## S1. Denominator positivity (the chart)

**Claim:** for `t = tan(q/2)` with `q` ranging over `(-pi, pi)`, and
`D = 1 + t^2`: (a) `D >= 1` for every real `t`; (b) `D` is never used with `t`
outside a finite range in this encoding, since only finite rational `t`
bounds are ever declared as the witness domain.

**Why:** `t^2 >= 0` for every real `t`, so `D = 1+t^2 >= 1` unconditionally —
no case split on the sign of `t`, and no value of `t` makes `D` vanish or
change sign. Separately, `t = tan(q/2) -> +-infinity` only as `q -> +-pi`;
since the encoding only ever declares finite rational interval bounds for
`t1, t2` (`IntervalDomain` requires a strictly finite `lower < upper`, so a
degenerate or unbounded domain is not representable at all), `q = pi` is
excluded by construction, not by an added side-condition someone could forget
to check.

**Consequence used downstream:** every time this argument multiplies both
sides of an equation or inequality by `D1`, `D2`, `D1^2`, `D2^2`, or a product
of these, that's a multiplication by a *provably positive* quantity, so it
never flips an inequality's direction and never introduces or removes a
solution. This is the one fact that makes every later "clear the
denominator" step in this note actually valid rather than merely convenient.

## S2. Forward-kinematics rationalization

**Claim:** with `cos(q) = (1-t^2)/D`, `sin(q) = 2t/D` (`D=1+t^2`), the
standard planar 2-link forward kinematics `x = L1*cos(q1) + L2*cos(q1+q2)`,
`y = L1*sin(q1) + L2*sin(q1+q2)` is equivalent, after multiplying both sides
by `D1*D2 > 0` (valid by S1), to two polynomial equalities in `t1, t2` with
no remaining denominators.

**Why:** substitute the half-angle forms into the sum-angle identities
`cos(q1+q2) = cos(q1)cos(q2) - sin(q1)sin(q2)`,
`sin(q1+q2) = sin(q1)cos(q2) + cos(q1)sin(q2)`, multiply through by `D1*D2`,
and collect terms. This is routine algebra (quartic in two variables), not a
place where an error would be subtle to reason about *abstractly* — the
actual risk is a transcription slip in expanding the quartic, which is why
the real correctness check for this step is not re-reading the algebra again
but a numeric cross-check: for many random `(t1,t2)`, compute
`q1=2*atan(t1), q2=2*atan(t2)` and the resulting `(x,y)` two independent
ways (via `math.cos`/`sin` directly, and via the claimed polynomial
identities evaluated at those `(t1,t2)`) and confirm agreement. This
property test exists (`tests/test_kinematics2r.py`,
`test_fk_identity_vanishes_exactly_at_its_own_witness`, Hypothesis-driven
random sampling) and passes; the adversarial pass additionally grid-searched
a 601x601 float grid for spurious extra roots beyond the two genuine IK
branches and found none (Slice 1 report §7).

## S3. Singularity margin without a sign case-split

**Claim:** for the standard 2R Jacobian, `det J(q) = L1*L2*sin(q2)`; the
claim `|det J(q)| >= epsilon` is equivalent, after rationalizing and squaring,
to the single polynomial inequality
`(4*L1^2*L2^2 - 2*epsilon^2)*t2^2 - epsilon^2*t2^4 - epsilon^2 >= 0`,
with **no separate sign branch needed**.

**Why:** `det J = L1*L2*sin(q2) = 2*L1*L2*t2/D2`. In general, `|a| >= b` is
equivalent to `a^2 >= b^2` **only when `b >= 0`** — squaring an inequality
against a value that could be negative silently drops information. Here
`b = epsilon*D2`, and `epsilon > 0` is given, and `D2 >= 1` by S1, so
`b = epsilon*D2 > 0` unconditionally — not merely nonnegative, strictly
positive for every real `t2`. That's exactly the condition needed for the
squaring step to be a genuine equivalence rather than a one-directional
implication, and it's a global fact (true for every `t2` in the domain), not
something that needs to be checked per-witness. Squaring
`(2*L1*L2*t2)^2 >= (epsilon*D2)^2` and expanding `D2 = 1+t2^2` gives the
stated quartic.

## S4. Segment 1 (shoulder-to-elbow) clearance case split

Segment 1 runs from the fixed origin `A=(0,0)` to the elbow
`B(t1) = (L1(1-t1^2), 2*L1*t1)/D1`. For a point `C=(cx,cy)` and a segment
`A-B`, the squared distance from `C` to the segment is a standard 3-case
function of the projection parameter `s = ((C-A).(B-A)) / |B-A|^2`: if
`s<=0` the closest point is `A`; if `s>=1` it's `B`; otherwise it's the
interior foot of the perpendicular, with squared distance
`|C-A|^2 - ((C-A).(B-A))^2/|B-A|^2`.

**Claim:** `|B(t1)|^2 = L1^2` identically (not just at the true witness — for
*every* `t1`). Consequence: `v.v := |B-A|^2 = L1^2`, a *constant*, which is
what lets every later step avoid dividing by a `t1`-dependent quantity for
this segment.

**Why:** `|B(t1)|^2 = [L1(1-t1^2)]^2 + [2*L1*t1]^2 = L1^2[(1-t1^2)^2+4t1^2]
= L1^2[1 - 2t1^2 + t1^4 + 4t1^2] = L1^2[1+2t1^2+t1^4] = L1^2*(1+t1^2)^2 =
L1^2*D1^2`, and `v = B/D1` (since `A=0`), so `v.v = |B|^2/D1^2 =
L1^2*D1^2/D1^2 = L1^2`. This is really just "the elbow is always exactly
distance `L1` from the shoulder, regardless of what `t1` is" — true by
construction of the forward-kinematics formula, not a coincidence needing
separate justification.

**Case selectors and distances**, with `Wn1(t1) := cx*L1(1-t1^2) + cy*2*L1*t1`
(the numerator of `(C-A).(B-A)`, since `(C-A).(B-A) = C.B = Wn1/D1`) and
`Ex, Ey := cx*D1 - L1(1-t1^2), cy*D1 - 2*L1*t1` (numerator of `D1*(C-B)`):

- `s <= 0 <=> Wn1/(D1*L1^2) <= 0 <=> Wn1 <= 0` (since `D1*L1^2 > 0` by S1 and
  `L1>0`), distance `= |C|^2 = cx^2+cy^2`.
- `s >= 1 <=> Wn1 >= D1*L1^2 <=> Wn1 - L1^2*D1 >= 0`, distance
  `= |C-B|^2 = (Ex^2+Ey^2)/D1^2`, so the cleared form is `Ex^2+Ey^2 >= R^2*D1^2`.
- otherwise (`0<=s<=1`): distance `= |C|^2 - Wn1^2/(D1^2*L1^2)`, so the
  cleared form is `(cx^2+cy^2-R^2)*D1^2*L1^2 - Wn1^2 >= 0`.

Each is obtained from the standard point-to-segment distance formula by
substituting the rational forms and multiplying through by manifestly
positive quantities (`D1`, `L1^2`, or both, per S1) — the same
multiply-by-a-provably-positive-quantity move as S2/S3, applied to a
genuinely 3-case (not spurious) geometric split: which of the segment's two
endpoints, or its interior, is nearest is a real fact about the geometry that
has to be case-split, not an artifact of this encoding.

## S5. Segment 2 (elbow-to-tool) clearance case split

Segment 2 runs from the fixed tool point `A=(x,y)` (justified by treating the
FK identity, S2, as already holding — this segment's predicates are only
meaningful in conjunction with S2, which the overall formula enforces via
`AND`, so this is not an independent, unconditional fact the way S4's
`v.v=L1^2` is) to the same elbow `B(t1)`.

**Claim:** `v.v` here (`Qn2(t1) := |B(t1)*D1 - A*D1|^2`, i.e. the analogous
squared-length numerator) is **not** constant in `t1` — unlike segment 1 — but
is provably positive at any `t1` where the FK identity (S2) also holds,
because then `|B(t1)-A| = L2 > 0` exactly (the elbow-to-tool distance at the
true kinematic witness is the second link length by definition of forward
kinematics).

**Why this matters:** the case-split algebra for segment 2 (structurally
identical to S4's, with `Wn2 := (cx-x)*Vn_x + (cy-y)*Vn_y` where
`Vn = B*D1 - A*D1`, and `Qn2 := |Vn|^2`) requires dividing by `Qn2` at one
point to go from `s`'s definition to a polynomial selector — and that step is
only valid where `Qn2 > 0`. Outside the FK-satisfying locus, `Qn2` could in
principle be zero or the case split could misbehave, but the overall formula
is an `AND` of the FK predicates with the clearance predicates, so any
witness where `Qn2` would be problematic is a witness that already fails the
FK conjunct and is rejected regardless of what the clearance predicates say.
This is a real dependency between S2 and S5 worth flagging explicitly (see
"Where this argument is weakest," below) rather than leaving implicit.

The resulting case selectors and distances (by the same substitution-and-clear
method as S4, using `Qn2` where S4 used the constant `L1^2`):

- `s<=0 <=> Wn2 <= 0`, distance `= (x-cx)^2+(y-cy)^2 >= R^2` (constant, since
  both endpoints of this comparison are fixed points).
- `s>=1 <=> Wn2*D1 - Qn2 >= 0`, distance `= Ex^2+Ey^2 >= R^2*D1^2` — note this
  is the *same* `Ex, Ey` as S4's case-B distance, since both refer to the
  distance from `C` to the shared elbow point `B(t1)`; the implementation
  reuses one predicate for both, which is a simplification worth independent
  scrutiny (does reusing it introduce any coupling that shouldn't be there?
  the adversarial pass exercised this specific case — Slice 1 report §7,
  "repeated-root / degenerate boundary" — and found it correctly rejected an
  elbow-on-obstacle-center configuration).
- otherwise: distance `= ((x-cx)^2+(y-cy)^2-R^2)*Qn2 - Wn2^2 >= 0` — no extra
  `D1` factor here (unlike S4's analogous case), because `v.v = Qn2/D1^2` for
  this segment (not a bare constant), so squaring `w.v = Wn2/D1` and dividing
  by `v.v` cancels the `D1^2` exactly, leaving no residual `D1` power. This is
  the step most likely to contain a transcription slip if done by hand (an
  earlier draft of this derivation, produced separately during design and not
  used for the shipped implementation, in fact carried a spurious extra `D1`
  factor here before being caught) — the actual implementation avoids
  hand-expansion entirely by computing this via a small internal scratch
  polynomial multiplier (`_ScratchPolynomial` in `kinematics2r.py`) rather
  than transcribing the expanded quartic by hand, and the result is verified
  in `tests/test_kinematics2r.py` via both an exact self-consistency check at
  the worked witness and a 3201-sample cross-check (in the adversarial pass)
  against an independently written point-to-segment distance function.

## Supporting evidence (not part of the argument itself)

An adversarial pass (Slice 1 report §7) independently re-derived S2/S3 from
scratch (no import of the implementation), solved for and tested the *other*
real IK branch reaching the same target (correctly rejected on clearance),
grid-searched for spurious FK roots (none found), solved exactly for S4's
repeated-root boundary (elbow on the obstacle center — correctly rejected),
and cross-checked S4/S5's case-split evaluation against an independent
exact-Fraction distance function over 3201 rational samples (zero
mismatches). This is evidence the encoding behaves as claimed on the cases
tried; it is not a proof of completeness over the full rational plane, and
does not substitute for this argument being read and judged on its own terms.

## Where this argument is weakest (read this section skeptically)

1. **S5's dependence on S2 holding** (noted above) is a real conditional
   dependency between two parts of the formula that this note states but
   does not independently verify beyond the adversarial pass's targeted
   probes. A referee should look here first.
2. **The three-way case split (S4, S5) covers `s<=0`, `s>=1`, `0<=s<=1`** —
   these overlap at the seams (`s=0`, `s=1`) rather than partition strictly,
   which is intentional (non-strict inequalities on both sides of each case
   so adjacent cases agree at the boundary by continuity) but is exactly the
   kind of place an off-by-one in the selector inequalities (`<=` vs `<`,
   `>=` vs `>`) would be easy to get wrong and hard to notice from testing
   alone if the test suite's samples don't happen to land exactly on a seam.
   (One test does land exactly on a seam by construction — the worked
   instance's clearance boundary coincides with `Wn1=0` — but that is one
   point, not a systematic seam check.)
3. **This argument, and the property tests, were both written by the same
   process** (this session) that wrote the implementation. The adversarial
   pass was a separate subagent instance, which helps, but a truly
   independent human check has not happened yet — that's the entire reason
   this note exists.

## What this does NOT claim

Nothing here establishes robustness across any link-length interval
(`forall theta`) or task-region box (`forall x`) — `L1, L2, x, y`, and the
obstacle are fixed constants throughout this argument, matching `RC-002`'s
stated scope exactly. `RC-001`'s SOS-based, robust approach to the
singularity margin is a separate, still-open claim this note says nothing
about.
