# RC-002 frozen-task corrigendum after RUN001

Status: **draft repair, not yet covered by the project owner's E1
attestation.** This file responds to A-002 and the two frozen Codex blind audits.
It must be read and explicitly accepted by the project owner before inclusion in
a new E1-to-E2 referee run.

The original proofs' central pointwise geometry is unchanged. This corrigendum
supplies the frozen-task obligations that were missing or only implicit in the
RUN001 packets.

## C1. Exact bridge for the two FK sign conventions

Let

\[
N_x=L_1C_1D_2+L_2(C_1C_2-S_1S_2),
\]

\[
N_y=L_1S_1D_2+L_2(S_1C_2+C_1S_2).
\]

The frozen task defines

\[
F_x^{\rm frozen}=xD_1D_2-N_x,
\qquad
F_y^{\rm frozen}=yD_1D_2-N_y.
\]

The sign-reversed convention in the second source proof is

\[
F_x^{\rm source}=N_x-xD_1D_2=-F_x^{\rm frozen},
\]

\[
F_y^{\rm source}=N_y-yD_1D_2=-F_y^{\rm frozen}.
\]

Therefore the equality atoms have exactly the same truth values:

\[
F_x^{\rm source}=0\iff F_x^{\rm frozen}=0,
\qquad
F_y^{\rm source}=0\iff F_y^{\rm frozen}=0.
\]

This bridge licenses the source proof's zero-set argument for the frozen theorem.
It does not license a coefficient-level implementation correspondence claim:
the builder must still be compared to the frozen sign convention exactly.

## C2. Explicit bounded existential transport

Write `Geo(t)` for the four geometric conjuncts in the frozen theorem. The
original pointwise result is

\[
\forall t\in\mathbb R^2:\quad \Phi(t)\iff\operatorname{Geo}(t).
\tag{C2.1}
\]

Let

\[
\mathcal B=[a_1,b_1]\times[a_2,b_2]
\]

with the exact membership formula

\[
t_1-a_1\ge0\land b_1-t_1\ge0\land
t_2-a_2\ge0\land b_2-t_2\ge0.
\tag{C2.2}
\]

For the forward implication, a witness `t in B` satisfying `Phi` also satisfies
`Geo` by (C2.1), so the same witness proves the right existential. The reverse
direction uses the same witness and the reverse implication of (C2.1). Hence

\[
\exists t\in\mathcal B:\Phi(t)
\iff
\exists t\in\mathcal B:\operatorname{Geo}(t).
\tag{C2.3}
\]

No compactness, nonemptiness, solver completeness, or witness construction is
used in this logical transport. The hypothesis `a_i<b_i` makes the conventional
box nonempty; (C2.3) would remain true for an empty or degenerate domain because
the same domain occurs on both sides.

## C3. Rational-polynomial and Boolean syntax

Under the frozen rational-data hypotheses, every named expression is in
`Q[t1,t2]`; only addition and multiplication are used. Normalize `P<=0` as
`-P>=0` if a single relation form is required. There are 17 atom occurrences in
the displayed `Phi`:

- three top-level occurrences: `Fx=0`, `Fy=0`, `G>=0`;
- seven in `Phi1`, in branch arities 2, 2, and 3;
- seven in `Phi2`, also in branch arities 2, 2, and 3.

There are 16 distinct predicate records because the exact `H_{1,B}>=0` atom is
reused in `Phi2`'s far-endpoint branch. The two appearances of `W_k<=0` and
`W_k>=0`, and of opposite selector differences, are distinct relational atoms
even when their left polynomials agree up to sign. `H_{1,A}` and `H_{2,A}` are
degree-zero polynomials and must not disappear unless constant folding is proved
semantics-preserving. The top-level tree is one five-way conjunction whose last
two children are the two three-way disjunctions.

Together with the four weak box atoms in (C2.2), this proves that the bounded
formula is a positive Boolean combination of polynomial equalities and weak
inequalities over `Q`. It contains no strict inequality, disequality, numerical
tolerance, or transcendental operation.

## C4. Hypothesis-consumption audit

- `L1>0` is consumed as `L1^2>0` to make segment 1 nondegenerate and to clear
  its interior inequality. Nonzero `L1` would suffice mathematically.
- `L2>0` is consumed after FK to obtain `Q2=D1^2 L2^2>0`. Nonzero `L2` would
  suffice mathematically.
- `r>0` and `mu>0` are consumed only through `R=r+mu>=0` when replacing
  `dist>=R` by `dist^2>=R^2`.
- `epsilon>0` is consumed only through `epsilon>=0` when squaring the absolute
  determinant comparison.
- `epsilon<=|L1L2|` is not used in the pointwise equivalence. It ensures the
  determinant-margin set is nonempty; deleting it can make both sides false for
  every witness without breaking equivalence.
- rationality is consumed by C3 and exact checking, not by the real geometric
  equivalence.
- `a_i<b_i` makes `B` nonempty but is not consumed by C2's same-domain logical
  transport.

The frozen hypotheses imply every weaker condition actually consumed by the
proof. Proving the pointwise equivalence under weaker hypotheses does not change
the frozen theorem.

## C5. Degeneracy and selector controls

For a generic segment `[A,B]`, if `A=B` then the distance is `||C-A||` and no
interior division is defined. The frozen physical segments are never in this
case because their lengths are positive.

For the virtual second segment, `Q2=0` can occur away from FK and makes its
interior disjunct vacuously true. For example, if `p1=P*`, then
`V=0`, `Q2=W2=H_{2,I}=0`, irrespective of whether the obstacle clears the
degenerate virtual segment. This is why the second-segment equivalence is stated
only after `Fx=Fy=0` implies `p2=P*` and positive `L2` implies
`p1!=P*`, hence `Q2>0`.

The selector triples are covers, not partitions. Their endpoint and interior
distance formulas agree at both weak seams, so no equality case is dropped.

## C6. Chart and scope controls

The map `t -> 2 arctan t` is a strictly increasing bijection from `R` onto
`(-pi,pi)`, with inverse `q -> tan(q/2)` on that interval. Thus every witness in
the frozen theorem is principal-chart relative. Finite `t` does not represent
`q=+-pi`.

Neither (C2.1) nor (C2.3) establishes:

- completeness on the configuration torus;
- conversion from arbitrary radian joint limits to exact rational `t` bounds;
- robustness over parameters or task regions;
- continuous path or dynamic feasibility;
- physical robot safety; or
- infeasibility from checker rejection, timeout, or failure to find a witness.

The only sound negative outcome supplied by this family is `UNKNOWN` unless an
independent certificate family proves something stronger.

## C7. Remaining separate implementation obligation

C1--C6 repair proof text only. They do not establish builder coefficients,
serialized quantifier order, exact evaluator behavior, model/claim/certificate
hash binding, or fail-closed corruption handling. Those remain deterministic
implementation-correspondence obligations and must be replayed against the
exact source state proposed for production.
