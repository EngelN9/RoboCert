# UNION LEDGER v1

Run: `RCMPVB-20260821-CROSS-X-RUN001`  
Item: `RC-002`  
Inputs: the two independently frozen theorem-only ledgers. No candidate proof
was used to construct this union.

Both ledgers returned `NO COUNTEREXAMPLE FOUND` under the same necessary reading:
the polynomiality assertion concerns the atoms of `Phi`, the brace on the
geometric side is a conjunction, `[A,B]` is a closed segment, and the occurrence
of `H_{1,B}` in the middle branch of `Phi_2` is deliberate.

## Formal scope

The fixed rational instance precedes all quantifiers. The pointwise statement is

```text
FOR ALL finite (t1,t2) in R^2:
    Phi(t1,t2) IFF geometric_conjunction(t1,t2).
```

The bounded statement is its restriction to the same closed `t`-box on both
sides:

```text
EXISTS (t1,t2) in [a1,b1] x [a2,b2]: Phi
IFF
EXISTS (t1,t2) in [a1,b1] x [a2,b2]: geometric_conjunction.
```

It is not a torus-completeness, robust, path, decision-procedure, or certified-
infeasibility theorem. `J` is differentiated with respect to `q`, not `t`.

Hypothesis roles agreed by both ledgers:

- positivity of `L1,L2` prevents both physical segments from degenerating;
- `R=r+mu>0` and `epsilon>0` justify the two nonnegative squaring steps;
- `epsilon <= |L1 L2|` is a non-vacuity condition, not needed for the
  pointwise equivalence;
- `a_i<b_i` makes the box nonempty but is not needed to transport a pointwise
  equivalence under the same existential quantifier;
- rationality is needed for the syntactic/exact-arithmetic claim, not for the
  real pointwise equivalence.

## Counterexample-search controls and near misses

No counterexample to the frozen theorem was found. Two near misses are mandatory
audit targets:

1. `Phi_2` is false as an unconditional encoding of second-link clearance. If
   `p1=P*`, then `Q2=W2=H_{2,I}=0`, so its interior branch may pass vacuously.
   The theorem survives only because `F_x=F_y=0` first implies `p2=P*`, and the
   nonzero second-link length then forces `p1!=P*` and `Q2>0`.
2. A feasible torus configuration can occur at `q1=pi`, outside every finite
   principal half-angle coordinate. Both sides of the frozen theorem quantify
   over the same finite `t`, so this does not refute the theorem; it forbids any
   promotion from failed chart search to infeasibility.

## Union obligation ledger

- **O1 — Chart identities and range.** Prove for every finite real `t` that
  `D=1+t^2>0`, `cos(2 atan t)=C/D`, `sin(2 atan t)=S/D`,
  `C^2+S^2=D^2`, and `t -> 2 atan t` maps bijectively onto `(-pi,pi)`.
- **O2 — Positivity register.** Record the sign of every factor used to clear
  an equality or inequality: `D_i`, `D1 D2`, `D_i^2`, `L_i^2`, `R`, `epsilon`,
  and, only under the FK gate, `Q2`.
- **O3 — Nonnegative squaring.** Prove `u>=v iff u^2>=v^2` for `u,v>=0` and
  cite it separately for distance and determinant bounds.
- **O4 — Point-to-segment lemma.** Derive the two endpoint and one interior
  projection cases from minimization over `[0,1]`; prove coverage and agreement
  on both seams. State the degenerate-segment case separately.
- **O5 — Rationalized kinematics.** Derive the rational formulas for `p1,p2`
  from O1, including the angle-addition identities.
- **O6 — FK equivalence.** Prove exactly
  `Fx=D1 D2 (x-p2_x)` and `Fy=D1 D2 (y-p2_y)`, hence both zero iff `p2=P*`.
- **O7 — Physical link lengths.** Prove `||p1-p0||=L1` and
  `||p2-p1||=L2`, so both physical segments are nondegenerate.
- **O8 — Jacobian determinant.** Compute all entries of `d p2/d q` and derive
  `det J=L1 L2 sin(q2)`. Distinguish it from `d p2/d t`.
- **O9 — Singularity clearing.** Prove `|det J|>=epsilon iff G>=0`, including
  absolute value, nonnegative squaring, positive denominator, and coefficient
  expansion. State that the upper-margin hypothesis controls non-vacuity only.
- **O10 — First-segment scaling.** Derive `W1`, `E`, `H_{1,A}`,
  `H_{1,B}`, and `H_{1,I}` as exact positive clearings of the projection
  parameter and squared-distance branches.
- **O11 — First-segment assembly.** Translate all three guards, prove they
  cover and may overlap, verify weak-boundary semantics, and conclude
  `Phi_1 iff dist(C,[p0,p1])>=R` in both directions.
- **O12 — Second-segment proxy identities.** Prove unconditionally that
  `V=D1(p1-P*)`, `Q2=D1^2||p1-P*||^2`, and
  `W2=D1 <C-P*,p1-P*>`.
- **O13 — Conditional nondegeneracy.** Under `Fx=Fy=0`, derive
  `p2=P*`, `||p1-P*||=L2`, and `Q2=D1^2 L2^2>0`. Explicitly reject the
  same conclusion without the FK gate.
- **O14 — Second-segment branches.** Under the FK gate, translate the three
  projection guards and prove the endpoint/interior inequalities. Justify the
  reuse of `H_{1,B}` at endpoint `p1` and every division/multiplication by
  `Q2`.
- **O15 — Second-segment assembly.** Under the FK gate only, prove coverage,
  seam compatibility, and
  `Phi_2 iff dist(C,[p1,p2])>=R` in both directions. State that the
  unconditional lemma is false.
- **O16 — Pointwise forward direction.** From `Phi`, establish FK first, then
  first clearance, conditional second clearance, and the determinant margin.
- **O17 — Pointwise reverse direction.** From the geometric conjunction,
  establish FK first, then use it before deriving `Phi_2`; derive every
  conjunct without changing a weak inequality to a strict one.
- **O18 — Bounded existential corollary.** Transport O16/O17 under the same
  `EXISTS(t1,t2)` and the same closed box. Make no existence, completeness, or
  infeasibility claim.
- **O19 — Rational-polynomial syntax.** Enumerate every distinct atom and the
  conjunction/disjunction tree; show each atom is an equality or weak inequality
  over `Q[t1,t2]`, including constant atoms and the four box bounds.
- **O20 — Hypothesis and scope audit.** Identify the exact consumer of each
  hypothesis and verify that the proof does not add torus completeness,
  uncertainty quantifiers, path feasibility, `q`-box conversion, or an
  infeasibility conclusion.

Dependency spine:

```text
O1 -> O5 -> O6 -> O13 -> O14 -> O15 -> O16/O17 -> O18 -> O20
O1/O2/O7 -> O10 -> O11 ------------------------^ 
O3/O4 -----------------------> O10/O11/O14/O15
O8 -> O9 --------------------------------------^
O2 -> O19
```

## Union difficulty forecast

- **F1 — Conditional `Phi_2`.** Characteristic error: compare the four
  conjuncts independently and assert unconditional second-segment equivalence.
- **F2 — `Q2=0`.** Characteristic error: divide by `Q2`, or claim it is positive
  from `L2>0`, before using FK.
- **F3 — Coordinate and sign discipline.** Characteristic error: use
  `d p2/d t`, square a signed expression, or clear an inequality without proving
  the multiplier positive.
- **F4 — Selector coverage.** Characteristic error: call overlapping guards a
  partition, omit the reverse direction, or lose equality at a seam.
- **F5 — Scope and hypothesis drift.** Characteristic error: use non-vacuity as
  an equivalence step, identify a rational `t`-box with a rational `q`-box, or
  convert chart-level witness failure into infeasibility.

## Separate implementation-correspondence obligations

- **IC1:** coefficient-by-coefficient and Boolean-tree correspondence between
  the frozen formula and builder output, including shared `H_{1,B}`.
- **IC2:** exact `EXISTS(t1,t2)` prefix and all four closed rational `t` bounds.
- **IC3:** deterministic exact-rational evaluation, including seams,
  determinant equality, and the off-FK `Q2=0` control.
- **IC4:** fail-closed rejection of unsupported quantifiers, malformed or
  non-rational payloads, and out-of-domain witnesses.

These implementation obligations do not prove O1–O20, and proof agreement does
not discharge them.
