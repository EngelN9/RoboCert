# RC-005 E0 soundness argument: principal-chart pose-tolerance witness

Status: **E0 draft produced on 2026-08-24.** It has not received the project
owner's required line-by-line E1 attestation and has not been refereed. It must
not justify a production checker at this tier.

## 1. Claim and scope

Fix a declared length unit `u` and rational coordinate values

\[
L_1,L_2>0,\quad x,y,c_x,c_y\in\mathbb Q,
\quad \rho,\mu,\tau,\varepsilon\in\mathbb Q_{\ge 0},
\]

and rational closed intervals `[a_i,b_i]` with `a_i<=b_i`. Let

\[
P^\star=(x,y),\qquad C=(c_x,c_y),\qquad R=\rho+\mu,
\qquad \mathcal B=[a_1,b_1]\times[a_2,b_2].
\]

The numerical values for positions, link lengths, radii, clearances, and pose
tolerance are coordinates in `u`. The singularity margin `epsilon`, which bounds
the planar position-Jacobian determinant, is a coordinate in `u^2`. Joint angles
use the declared radian convention, but the input domain is already expressed in
the dimensionless principal-chart coordinates `t_i=tan(q_i/2)`; this claim
performs no floating-point conversion from angle bounds.

For every finite real `t_i`, define

\[
D_i=1+t_i^2,\qquad C_i=1-t_i^2,\qquad S_i=2t_i,
\qquad q_i=2\arctan t_i\in(-\pi,\pi),
\]

and put `D=D_1D_2`. The shoulder, elbow, and tool point are

\[
p_0=(0,0),\qquad
p_1=L_1(\cos q_1,\sin q_1),
\]

\[
p_2=p_1+L_2(\cos(q_1+q_2),\sin(q_1+q_2)).
\]

The claim proved below is exactly

\[
\exists(t_1,t_2)\in\mathcal B:
\|p_2-P^\star\|^2\le\tau^2
\land \operatorname{dist}(C,[p_0,p_1])\ge R
\land \operatorname{dist}(C,[p_1,p_2])\ge R
\land |\det J(q)|\ge\varepsilon .
\tag{GEO}
\]

It is a single fixed-instance existential claim on the principal half-angle
chart. It does not assert torus completeness, uncertainty robustness, universal
task-region coverage, path feasibility, dynamics, physical-machine safety, or
infeasibility when no witness is certified.

## 2. Exact homogeneous endpoints

The half-angle identities give

\[
\cos q_i=C_i/D_i,\qquad \sin q_i=S_i/D_i,
\qquad C_i^2+S_i^2=D_i^2.
\]

Because `D_i=1+t_i^2>0`, also `D>0`. Define homogeneous endpoint numerators

\[
A_x=L_1C_1D_2,\qquad A_y=L_1S_1D_2,
\]

\[
B_x=A_x+L_2(C_1C_2-S_1S_2),
\]

\[
B_y=A_y+L_2(S_1C_2+C_1S_2).
\]

Then, as exact identities,

\[
p_1=A/D,\qquad p_2=B/D,
\]

where `A=(A_x,A_y)` and `B=(B_x,B_y)`. No target point is
used as a geometric endpoint.

The two homogeneous direction vectors are

\[
N_1=A,qquad N_2=B-A.
\]

Using `C_i^2+S_i^2=D_i^2` and the angle-addition identity,

\[
Q_1:=N_1\cdot N_1=L_1^2D^2>0,
\qquad
Q_2:=N_2\cdot N_2=L_2^2D^2>0.
\tag{2.1}
\]

Thus both encoded segments are nondegenerate for every finite real witness,
independently of pose-tolerance satisfaction.

## 3. Pose-tolerance polynomial

Define residual numerators

\[
F_x=xD-B_x,\qquad F_y=yD-B_y
\]

and

\[
T=\tau^2D^2-F_x^2-F_y^2.
\]

Since

\[
p_2-P^\star=(-F_x/D,-F_y/D)
\]

and `D^2>0`, one has

\[
T\ge0
\iff F_x^2+F_y^2\le\tau^2D^2
\iff \|p_2-P^\star\|^2\le\tau^2.
\tag{3.1}
\]

This includes `tau=0` and equality on the tolerance boundary. It is not a
floating-point residual test.

## 4. Generic homogeneous point-to-segment encoding

Let a nondegenerate segment have endpoints `U/D` and `V/D`, where `D>0`,
and let

\[
N=V-U,\quad Q=N\cdot N>0,
\quad W=CD-U,\quad Z=W\cdot N.
\]

Here `W/D=C-U/D`, `N/D=V/D-U/D`, so the ordinary projection parameter is

\[
s_\star={Z\over Q}.
\]

Define

\[
H_A=W\cdot W-R^2D^2,
\]

\[
H_B=(CD-V)\cdot(CD-V)-R^2D^2,
\]

\[
H_I=(W\cdot W-R^2D^2)Q-Z^2.
\]

The polynomial segment formula is

\[
\begin{aligned}
\operatorname{Seg}(U,V):={}&
(Z\le0\land H_A\ge0)\\
&\lor(Z-Q\ge0\land H_B\ge0)\\
&\lor(Z\ge0\land Q-Z\ge0\land H_I\ge0).
\end{aligned}
\tag{SEG}
\]

### Lemma 4.1: selector coverage and seams

The three guards are exactly `s_star<=0`, `s_star>=1`, and
`0<=s_star<=1`, because `Q>0`. They cover the real line and overlap at
`Z=0` and `Z=Q`.

At `Z=0`,

\[
H_I=QH_A.
\]

At `Z=Q`, expansion of `||W-N||^2` gives

\[
H_B=W\cdot W-2Z+Q-R^2D^2
=W\cdot W-Q-R^2D^2,
\]

and hence

\[
H_I=QH_B.
\]

Because `Q>0`, the endpoint and interior inequalities agree in truth value on
both seams. The guards are a cover, not a disjoint partition.

### Lemma 4.2: segment equivalence

For `s in [0,1]`, minimizing

\[
\left\|C-\left({U\over D}+s{N\over D}\right)\right\|^2
=D^{-2}\|W-sN\|^2
\]

gives the clamped projection cases:

- if `Z<=0`, the nearest point is `U/D` and
  `dist^2-R^2=H_A/D^2`;
- if `Z>=Q`, the nearest point is `V/D` and
  `dist^2-R^2=H_B/D^2`;
- if `0<=Z<=Q`, the nearest point has `s=Z/Q` and
  `dist^2-R^2=H_I/(D^2Q)`.

All cleared denominators are strictly positive. Since both the Euclidean
distance and `R` are nonnegative,

\[
\operatorname{dist}(C,[U/D,V/D])\ge R
\iff \operatorname{dist}^2\ge R^2.
\]

Applying the appropriate branch in each direction, using guard coverage and
Lemma 4.1 at overlaps, proves

\[
\operatorname{Seg}(U,V)
\iff \operatorname{dist}(C,[U/D,V/D])\ge R.
\tag{4.1}
\]

This handles endpoint projection, interior projection, both overlapping seams,
zero clearance margin, tangential contact, and all finite robot positions. A
degenerate segment would invalidate division by `Q`, but (2.1) excludes it for
both links.

## 5. The two actual-link formulas

Use (SEG) twice:

\[
\Phi_1=\operatorname{Seg}((0,0),A),
\qquad
\Phi_2^{\rm actual}=\operatorname{Seg}(A,B).
\]

By Lemma 4.2 and the endpoint identities of Section 2,

\[
\Phi_1\iff\operatorname{dist}(C,[p_0,p_1])\ge R,
\]

\[
\Phi_2^{\rm actual}
\iff\operatorname{dist}(C,[p_1,p_2])\ge R.
\tag{5.1}
\]

Unlike RC-002, the second equivalence is unconditional: the actual numerator
`B` is present directly, so no equality `p2=P*` and no target endpoint
substitution is used.

## 6. Singularity polynomial

Differentiating the planar 2R kinematics with respect to `(q1,q2)` gives

\[
\det J(q)=L_1L_2\sin q_2.
\]

Define

\[
G=(4L_1^2L_2^2-2\varepsilon^2)t_2^2
-\varepsilon^2t_2^4-\varepsilon^2.
\]

Using `sin q2=2t2/D2`, nonnegativity of both sides of the absolute-value
comparison, and `D2>0`,

\[
|\det J(q)|\ge\varepsilon
\iff 4L_1^2L_2^2t_2^2\ge\varepsilon^2D_2^2
\iff G\ge0.
\tag{6.1}
\]

The equivalence includes `epsilon=0` and equality on the singularity margin.
No numerical singular value or residual enters it.

## 7. Pointwise and bounded existential equivalence

Define

\[
\Phi_{005}(t_1,t_2)=
(T\ge0)\land\Phi_1\land\Phi_2^{\rm actual}\land(G\ge0).
\]

Equations (3.1), (5.1), and (6.1) are four independent pointwise
equivalences. Therefore, for every finite real `(t1,t2)`,

\[
\Phi_{005}(t_1,t_2)
\iff
\begin{cases}
\|p_2-P^\star\|^2\le\tau^2,\\
\operatorname{dist}(C,[p_0,p_1])\ge R,\\
\operatorname{dist}(C,[p_1,p_2])\ge R,\\
|\det J(q)|\ge\varepsilon.
\end{cases}
\tag{7.1}
\]

The exact rational box is represented by

\[
t_1-a_1\ge0,\quad b_1-t_1\ge0,\quad
t_2-a_2\ge0,\quad b_2-t_2\ge0.
\]

Restricting (7.1) to the same closed box and applying the same existential
quantifier on both sides proves `(GEO) iff exists t in B: Phi_005(t)`.
No conclusion follows when search fails to produce such a witness.

## 8. Polynomial and certificate semantics

Every displayed numerator, dot product, guard, and `H` expression is a
polynomial in `Q[t1,t2]`. The full formula uses only equality-free weak
inequalities combined by conjunction and disjunction. The witness box also uses
weak polynomial inequalities. A rational pair `(t1,t2)` can therefore be
checked by finite exact rational arithmetic.

For the proposed `planar2r.pose_tolerance_witness` family, a certificate payload
means only: “these canonical rational values are the existential witness.” It
does not carry a solver-status proof. Acceptance is sound only if a deterministic
checker independently:

1. reconstructs the exact normalized problem and claim;
2. verifies problem, claim, assumptions, family, checker version, arithmetic
   mode, and hashes all agree;
3. rejects noncanonical or non-rational payloads and unsupported quantifiers;
4. checks the closed box and every branch of `Phi_005` in exact rational
   arithmetic; and
5. fails closed on every parse, reconstruction, or evaluation error.

A checked witness proves only the existential principal-chart statement above.
Checker rejection or absence of a witness means `UNKNOWN`, never
`CERTIFIED_INFEASIBLE`.

## 9. Separate implementation-correspondence obligations

This argument does not establish that future code implements it. Before any
production registration, deterministic evidence must separately establish:

- exact coefficient and Boolean-tree correspondence for `T`, `G`, and both
  actual-segment instances of (SEG);
- exact `EXISTS(t1,t2)` quantifier and closed rational box handling;
- target independence of both clearance formulas and direct dependence on `B`
  for the second link;
- full normalized-problem hashing and claim reconstruction during `check`;
- exact-rational evaluation at tolerance, clearance, singularity, box, and
  selector boundaries;
- fail-closed corruption behavior for every bound metadata and payload field;
- principal-chart boundary regressions that remain `UNKNOWN`.

Until those obligations and the E1/E2 review gates are complete, this document
is research evidence only.
