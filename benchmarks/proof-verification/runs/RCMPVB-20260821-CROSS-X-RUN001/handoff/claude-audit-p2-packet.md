# RC-002 Session A — P2

Execution condition: fresh context; exactly one blinded proof; no other proof,
audit, provenance, known-weakness hint, repository inspection, or tools.

The provided proof label is `P2`. Complete only this audit and emit
`AUDIT REPORT — P2`.

## Frozen instructions

# RC-002 blind-audit prompt v2

You are refereeing one submitted proof in a fresh context. Another candidate
may or may not exist; you receive no information about that. Treat the proof as
unverified. Use only the frozen task, the union ledger, and this one proof.

1. Reconstruct the proof dependency graph and tag risky steps with `Q`, `E`,
   `L->G`, `GEN`, `DIV`, `INV`, `ROOT`, `CHART`, `SYM`, `CIT`, `CIRC`, `NOT`,
   `CASE`, `LIM`, or `REG`.
2. Audit every tagged step, every ledger obligation and forecast point, and the
   final implication. List any untagged steps passed over.
3. For each theorem hypothesis, identify its exact consumption point and test
   what happens if it is deleted. Check whether the proof proves too much.
4. Attack all zero, boundary, seam, rank-deficient, undefined, and degenerate
   cases. In particular, audit denominator signs, the absolute-value squaring
   equivalence, selector coverage, and the second-segment endpoint substitution.
5. For each obligation assign exactly one of `DISCHARGED`,
   `PARTIALLY DISCHARGED`, `NOT DISCHARGED`, `INCORRECTLY DISCHARGED`, or
   `NOT APPLICABLE`. A discharge must cite an independent derivation, checked
   theorem hypotheses, exhaustive case split, or explicit computation.
6. Report each defect with severity `Fatal`, `Substantive`, `Minor`, or
   `Expository`. Do not repair it.
7. Give verdict `V1` through `V5`, confidence, and the most likely error if the
   proof is wrong.
8. Emit one self-contained block headed `AUDIT REPORT — <provided proof label>`.

Never add hypotheses, reveal or infer provenance, consult another proof or
audit, use a known-weakness list, or treat persuasive exposition as verification.

## Frozen task

# RC-002 — Planar 2R exact-witness encoding on one half-angle chart

## Item metadata

- `item_id`: `RC-002`
- `benchmark_version`: `0.2.0`
- `domain`: exact semialgebraic encoding of planar robot kinematics and clearance
- `coefficient_domain`: `Q`
- `quantifier_structure`: one existential witness pair after fixed instance data
- `expected_output_type`: proof or a precise refutation of the statement as written
- `permitted_prior_results`: elementary real arithmetic, trigonometric identities, and the definition of Euclidean point-to-segment distance; every nontrivial equivalence used from them must be proved
- `provenance`: adapted from RoboCert's Phase 1 planar-2R claim family

## Fixed data and hypotheses

Fix

\[
L_1,L_2,r,\mu,\varepsilon,x,y,c_x,c_y,a_1,b_1,a_2,b_2\in\mathbf Q
\]

with

\[
L_1,L_2,r,\mu,\varepsilon>0,\qquad
\varepsilon\le |L_1L_2|,\qquad
a_i<b_i\quad(i=1,2).
\]

Set

\[
R:=r+\mu,\qquad C:=(c_x,c_y),\qquad P^\star:=(x,y),
\]

and let

\[
\mathcal B:=[a_1,b_1]\times[a_2,b_2].
\]

For every finite real pair \(t=(t_1,t_2)\), define

\[
D_i:=1+t_i^2,\qquad C_i:=1-t_i^2,\qquad S_i:=2t_i,
\qquad q_i:=2\arctan(t_i)\in(-\pi,\pi).
\]

The shoulder, elbow, and tool point are

\[
p_0:=(0,0),\qquad
p_1:=L_1(\cos q_1,\sin q_1),
\]

\[
p_2:=p_1+L_2\bigl(\cos(q_1+q_2),\sin(q_1+q_2)\bigr).
\]

Let \(J(q):=\partial p_2/\partial q\).

## Polynomial encoding

Define the forward-kinematics polynomials

\[
F_x:=xD_1D_2-L_1C_1D_2-L_2(C_1C_2-S_1S_2),
\]

\[
F_y:=yD_1D_2-L_1S_1D_2-L_2(S_1C_2+C_1S_2),
\]

and the singularity polynomial

\[
G:=(4L_1^2L_2^2-2\varepsilon^2)t_2^2
-\varepsilon^2t_2^4-\varepsilon^2.
\]

For the first segment, define

\[
W_1:=c_xL_1C_1+c_yL_1S_1,
\]

\[
E_x:=c_xD_1-L_1C_1,\qquad E_y:=c_yD_1-L_1S_1,
\]

\[
H_{1,A}:=c_x^2+c_y^2-R^2,
\]

\[
H_{1,B}:=E_x^2+E_y^2-R^2D_1^2,
\]

\[
H_{1,I}:=(c_x^2+c_y^2-R^2)D_1^2L_1^2-W_1^2.
\]

Let \(\Phi_1(t_1)\) be

\[
\begin{aligned}
&(W_1\le0\wedge H_{1,A}\ge0)\\
\vee{}&(W_1-D_1L_1^2\ge0\wedge H_{1,B}\ge0)\\
\vee{}&(W_1\ge0\wedge D_1L_1^2-W_1\ge0\wedge H_{1,I}\ge0).
\end{aligned}
\]

For the second segment, define

\[
V_x:=L_1C_1-xD_1,\qquad V_y:=L_1S_1-yD_1,
\]

\[
Q_2:=V_x^2+V_y^2,
\qquad W_2:=(c_x-x)V_x+(c_y-y)V_y,
\]

\[
H_{2,A}:=(x-c_x)^2+(y-c_y)^2-R^2,
\]

\[
H_{2,I}:=H_{2,A}Q_2-W_2^2.
\]

Let \(\Phi_2(t_1)\) be

\[
\begin{aligned}
&(W_2\le0\wedge H_{2,A}\ge0)\\
\vee{}&(W_2D_1-Q_2\ge0\wedge H_{1,B}\ge0)\\
\vee{}&(W_2\ge0\wedge Q_2-W_2D_1\ge0\wedge H_{2,I}\ge0).
\end{aligned}
\]

Finally define

\[
\Phi(t_1,t_2):=(F_x=0)\wedge(F_y=0)\wedge(G\ge0)
\wedge\Phi_1(t_1)\wedge\Phi_2(t_1).
\]

## Theorem to verify

Prove the following pointwise equivalence for every \(t\in\mathbf R^2\), where
\(q=(2\arctan t_1,2\arctan t_2)\):

\[
\Phi(t_1,t_2)
\iff
\begin{cases}
p_2=P^\star,\\
\operatorname{dist}(C,[p_0,p_1])\ge R,\\
\operatorname{dist}(C,[p_1,p_2])\ge R,\\
|\det J(q)|\ge\varepsilon.
\end{cases}
\tag{RC-002-pointwise}
\]

Consequently prove the bounded-witness equivalence

\[
\exists(t_1,t_2)\in\mathcal B:\Phi(t_1,t_2)
\iff
\exists(t_1,t_2)\in\mathcal B:
\begin{cases}
p_2=P^\star,\\
\operatorname{dist}(C,[p_0,p_1])\ge R,\\
\operatorname{dist}(C,[p_1,p_2])\ge R,\\
|\det J(q)|\ge\varepsilon.
\end{cases}
\tag{RC-002-exists}
\]

Also establish that every displayed predicate is a polynomial equality or weak
inequality in \(t_1,t_2\) with rational coefficients.

## Explicit scope exclusions

This item covers one half-angle chart and one fixed rational instance. It does
not claim completeness on the configuration torus, robust quantification over
uncertain parameters or task points, path feasibility, or certified
infeasibility from failure to find a witness.

## Separate implementation-correspondence obligation

The candidate proofs address the mathematical formula above. They do not by
themselves establish that RoboCert serializes or checks exactly this formula.
The run must separately retain deterministic code/test evidence for:

1. the builder's predicate coefficients and Boolean structure;
2. the `EXISTS (t1,t2)` quantifier and bounded box handling;
3. exact-rational predicate/formula evaluation by the registered checker;
4. fail-closed rejection of unsupported quantifier prefixes and malformed or
   out-of-domain witnesses.

Passing the proof audit cannot substitute for this implementation evidence, and
passing the implementation tests cannot substitute for the proof audit.

## Frozen union ledger

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

## Submitted proof

# Candidate proof

This candidate addresses the frozen theorem in `task.md`. Audit only its mathematical content.

## 1. Data, hypotheses, and the geometric problem

### 1.1 Data

Fix real constants
$$L_1,\ L_2,\ x,\ y,\ c_x,\ c_y,\ r,\ \mu,\ \varepsilon\ \in\ \mathbb R,$$
and write
$$O:=(0,0),\qquad C:=(c_x,c_y),\qquad P^\star:=(x,y),\qquad R:=r+\mu .$$
Here $C$ is the obstacle centre, $r$ its radius, $\mu$ a clearance margin, $P^\star$ the target tool point, and $\varepsilon$ a singularity margin. Only the combination $R=r+\mu$ ever occurs.

### 1.2 Standing hypotheses

* **(H1)** $L_1\neq0$ and $L_2\neq0$;
* **(H2)** $\varepsilon\ge0$;
* **(H3)** $R\ge0$.

**Remark 1.1 (each hypothesis is at the strength actually used).**

* (H1) is stated as $L_i\neq0$, not $L_i>0$. Every use below is of $L_1^2>0$, of $L_2\neq0$, or of $\lvert L_2\rvert>0$; no proof uses a sign. This matters concretely: §13 applies the entire development with $L_1$ or $L_2$ replaced by its negative, and that is what repairs the chart loss of Theorem 12.1.
* (H3) is stated as $R\ge0$, not $R>0$. The only consumer of a hypothesis on $R$ is Lemma 2.3, whose hypothesis is $b\ge0$. The hypothesis is nonetheless **not** removable: if $R<0$ then the geometric requirement $\operatorname{dist}\ge R$ is vacuously true while its squared encoding $\operatorname{dist}^2\ge R^2$ is a genuine restriction, so the encoding would reject admissible configurations. Nothing in the data forces $r\ge0$ unless it is assumed; in particular assuming $\mu>0$ does not give (H3), and no hypothesis "$\mu>0$" appears above because $\mu$ enters only through $R$.
* (H2) is stated as $\varepsilon\ge0$ for the same reason. The case $\varepsilon=0$ is genuinely exceptional in exactly one place, the closed form of Corollary 5.4, and is handled there.

In the intended application $L_1,L_2>0$, $r\ge0$, $\mu>0$ and $\varepsilon>0$, so (H1)–(H3) hold with strict inequalities. No hypothesis of rationality is made or used: rationality of the data matters only for exact arithmetic in an implementation, and all statements below are over $\mathbb R$.

### 1.3 Euclidean conventions

For $u,v\in\mathbb R^2$, $u\cdot v$ is the standard inner product and $\lVert u\rVert^2=u\cdot u$. For $A,B\in\mathbb R^2$,
$$[A,B]:=\{A+s(B-A):s\in[0,1]\},\qquad
\operatorname{dist}(C,[A,B]):=\min_{p\in[A,B]}\lVert C-p\rVert .$$
The minimum is attained: $[A,B]$ is the continuous image of $[0,1]$, hence nonempty and compact, and $p\mapsto\lVert C-p\rVert$ is continuous.

### 1.4 Kinematics

For $q=(q_1,q_2)\in\mathbb R^2$ put
$$E(q_1):=\bigl(L_1\cos q_1,\ L_1\sin q_1\bigr),\qquad
P(q):=E(q_1)+L_2\bigl(\cos(q_1+q_2),\ \sin(q_1+q_2)\bigr),$$
the elbow and tool points, and let $J(q):=\partial P/\partial q\in\mathbb R^{2\times2}$. The two link segments are
$$\mathcal S^{(1)}(q):=\bigl[\,O,\ E(q_1)\,\bigr],\qquad
\mathcal S^{(2)}(q):=\bigl[\,E(q_1),\ P(q)\,\bigr].$$

### 1.5 The geometric conditions

For $q\in\mathbb R^2$:

* **(a)** $P(q)=P^\star$;
* **(b)** $\operatorname{dist}\bigl(C,\mathcal S^{(1)}(q)\bigr)\ge R$ **and** $\operatorname{dist}\bigl(C,\mathcal S^{(2)}(q)\bigr)\ge R$;
* **(c)** $\lvert\det J(q)\rvert\ge\varepsilon$.

Call $q$ **admissible** if (a), (b) and (c) all hold.

**Remark 1.2 (the scope of "admissible").** Conditions (a), (b), (c) are definitions internal to this document, and every soundness and completeness statement below is relative to them and to nothing else. In particular (b) models both links as segments of zero thickness and the obstacle as the closed disc of radius $r$ about $C$ inflated by $\mu$. Whether that is an adequate model of physical collision-freeness — link width, joint hardware, the region swept during motion — is not addressed here and must not be read into the word "admissible".

**Lemma 1.3 (periodicity).** $E$, $P$, $J$ and $\det J$ are $2\pi$-periodic in each of $q_1,q_2$. Consequently admissibility is well defined on $\mathbb T=(\mathbb R/2\pi\mathbb Z)^2$.

*Proof.* $E(q_1)$ depends on $q_1$ only through $\cos q_1,\sin q_1$, which are $2\pi$-periodic, and not on $q_2$. The second summand of $P$ depends on $q$ only through $\cos(q_1+q_2),\sin(q_1+q_2)$; replacing $q_i$ by $q_i+2\pi$ changes $q_1+q_2$ by $2\pi$ and so leaves these unchanged. Hence $E$ and $P$ are $2\pi$-periodic in each variable, and therefore so are their partial derivatives, hence $J$ and $\det J$. Conditions (a), (b), (c) are built from $E$, $P$ and $\det J$ together with the constants $C,P^\star,R,\varepsilon$, so each is $2\pi$-periodic in each variable. $\blacksquare$

---

## 2. Elementary tools

**Lemma 2.1 (positive rescaling preserves $=$ and $\ge$).** Let $p,q\in\mathbb R$ and $\lambda>0$. Then
$$p=q\iff\lambda p=\lambda q,\qquad\qquad p\ge q\iff\lambda p\ge\lambda q .$$

*Proof.* If $p=q$ then $\lambda p=\lambda q$; conversely $\lambda\neq0$, so multiplying $\lambda p=\lambda q$ by $\lambda^{-1}$ gives $p=q$. If $p\ge q$ then $p-q\ge0$, and $\lambda>0$ gives $\lambda(p-q)\ge0$, i.e. $\lambda p\ge\lambda q$. Conversely, $\lambda p\ge\lambda q$ gives $\lambda(p-q)\ge0$, and $\lambda^{-1}>0$ gives $p-q\ge0$. $\blacksquare$

**Convention 2.2.** Lemma 2.1 is used pointwise: for $f,g:S\to\mathbb R$ and $\lambda:S\to(0,\infty)$,
$$\{s:f(s)=g(s)\}=\{s:\lambda(s)f(s)=\lambda(s)g(s)\},\qquad
\{s:f(s)\ge g(s)\}=\{s:\lambda(s)f(s)\ge\lambda(s)g(s)\}.$$
Every denominator-clearing step below is an instance of this, and the strict positivity of the multiplier is verified at each use.

**Lemma 2.3 (squaring an inequality).** Let $a\in\mathbb R$ and $b\ge0$. Then
$$\lvert a\rvert\ge b\iff a^2\ge b^2 .$$

*Proof.* **Case $b=0$.** Both sides hold unconditionally, since $\lvert a\rvert\ge0$ and $a^2\ge0$; so the equivalence holds.

**Case $b>0$.** $(\Rightarrow)$ From $\lvert a\rvert\ge b>0$ we obtain $\lvert a\rvert>0$, so Lemma 2.1 may be applied with $\lambda:=\lvert a\rvert$. Doing so to the inequality $\lvert a\rvert\ge b$ gives $\lvert a\rvert^2\ge b\lvert a\rvert$; applying Lemma 2.1 to the same inequality with $\lambda:=b>0$ gives $b\lvert a\rvert\ge b^2$. Chaining, $a^2=\lvert a\rvert^2\ge b^2$.
$(\Leftarrow)$ By contraposition. Suppose $\lvert a\rvert<b$. Multiplying this strict inequality by $\lvert a\rvert\ge0$ gives $\lvert a\rvert^2\le b\lvert a\rvert$, and multiplying it by $b>0$ gives $b\lvert a\rvert<b^2$. Hence $a^2=\lvert a\rvert^2<b^2$. $\blacksquare$

*(The case split is on $b$, not on $a$. It is needed because the multiplier $\lvert a\rvert$ of Lemma 2.1 must be shown strictly positive, and that follows from $b>0$ and only from it.)*

**Remark 2.4.** The hypothesis $b\ge0$ cannot be dropped: for $a=0$, $b=-1$ the left-hand side holds and the right-hand side fails. It is exactly $b\ge0$ that makes the equivalence hold for *every* $a$.

**Lemma 2.5 (half-angle chart).** Define $\tau:\mathbb R\to(-\pi,\pi)$ by $\tau(t):=2\arctan t$. Then $\tau$ is a continuous, strictly increasing bijection with inverse $q\mapsto\tan(q/2)$, and for $q=\tau(t)$, writing $D:=1+t^2$,
$$\cos q=\frac{1-t^2}{D},\qquad\sin q=\frac{2t}{D}.$$

*Proof.* The restriction of $\tan$ to $(-\pi/2,\pi/2)$ is continuous, strictly increasing and surjective onto $\mathbb R$; hence its inverse $\arctan:\mathbb R\to(-\pi/2,\pi/2)$ is a continuous, strictly increasing bijection, and so is $\tau=2\arctan$ onto $(-\pi,\pi)$, with inverse $q\mapsto\tan(q/2)$ (legitimate because $q/2\in(-\pi/2,\pi/2)$).

For the identities set $\theta:=q/2\in(-\pi/2,\pi/2)$, so that $\cos\theta>0$ and $t=\tan\theta=\sin\theta/\cos\theta$. Dividing $\sin^2\theta+\cos^2\theta=1$ by $\cos^2\theta>0$ gives $1+t^2=1/\cos^2\theta$, i.e. $\cos^2\theta=1/D$. Hence
$$\cos q=\cos2\theta=2\cos^2\theta-1=\frac2D-1=\frac{2-D}{D}=\frac{1-t^2}{D},
\qquad
\sin q=2\sin\theta\cos\theta=2t\cos^2\theta=\frac{2t}{D}. \qquad\blacksquare$$

**Notation 2.6.** Put
$$\Theta:\mathbb R^2\to(-\pi,\pi)^2,\qquad \Theta(t_1,t_2):=\bigl(\tau(t_1),\tau(t_2)\bigr),$$
a bijection by Lemma 2.5. **Throughout §§3–12, $q=(q_1,q_2)$ denotes $\Theta(t_1,t_2)$**, and $D_i:=1+t_i^2$.

---

## 3. The chart: unconditional positivity, and its exact cost

**Proposition 3.1.** For every $t\in\mathbb R$ we have $D=1+t^2\ge1>0$, with equality iff $t=0$. In particular $D$ has no real zero.

*Proof.* $t^2\ge0$ for every real $t$, so $1+t^2\ge1$; and $1+t^2=1$ iff $t^2=0$ iff $t=0$. No case distinction on the sign of $t$ arises. $\blacksquare$

**Corollary 3.2.** For all $t_1,t_2\in\mathbb R$ the quantities
$$D_1,\quad D_2,\quad D_1D_2,\quad D_1^2,\quad D_2^2,\quad L_1^2,\quad L_1^2D_1,\quad L_1^2D_1^2$$
are strictly positive, and $\varepsilon D_2\ge0$. Consequently Lemma 2.1 may be applied with any of the former as $\lambda$, and Lemma 2.3 with $b=\varepsilon D_2$.

*Proof.* Strict positivity of $D_1,D_2$ is Proposition 3.1; $L_1^2>0$ by (H1); products of strictly positive reals are strictly positive. Finally $\varepsilon\ge0$ by (H2) and $D_2>0$ give $\varepsilon D_2\ge0$. $\blacksquare$

Thus the chart is **unconditionally** denominator-safe: no restriction of $t_1$ or $t_2$ to a finite interval is used, or needed, at any point below. What a restricted range does is restrict *scope*, which is a separate matter recorded next and pursued in §§12–13.

**Proposition 3.3 (scope of the chart).**

1. $\operatorname{im}\Theta=(-\pi,\pi)^2$. Hence a configuration with $q_1\equiv\pi$ or $q_2\equiv\pi\pmod{2\pi}$ has no $\Theta$-preimage and is not representable in the encoding.
2. For finite $\ell_i<u_i$,
$$\Theta\bigl([\ell_1,u_1]\times[\ell_2,u_2]\bigr)=[\tau(\ell_1),\tau(u_1)]\times[\tau(\ell_2),\tau(u_2)].$$

*Proof.* (1) is Lemma 2.5 together with the definition of $\Theta$. (2): $\tau$ is a continuous strictly increasing bijection onto $(-\pi,\pi)$, hence maps $[\ell,u]$ onto $[\tau(\ell),\tau(u)]$; now take products. $\blacksquare$

Both restrictions are one-directional: they can only *remove* configurations from consideration, never introduce spurious ones. Theorem 12.1 shows the removal is not vacuous; Theorem 13.5 removes it.

---

## 4. Rational forward kinematics

**Definition 4.1.** Define $F_x,F_y\in\mathbb R[t_1,t_2]$ by
$$
\begin{aligned}
F_x&:=L_1(1-t_1^2)D_2+L_2\bigl[(1-t_1^2)(1-t_2^2)-4t_1t_2\bigr]-x\,D_1D_2,\\[2pt]
F_y&:=2L_1t_1D_2+2L_2\bigl[t_1(1-t_2^2)+t_2(1-t_1^2)\bigr]-y\,D_1D_2 .
\end{aligned}
$$

**Lemma 4.2 (monomial expansion).** As elements of $\mathbb R[t_1,t_2]$,
$$
\begin{aligned}
F_x=\;&(L_1+L_2-x)+(-L_1-L_2-x)\,t_1^2+(L_1-L_2-x)\,t_2^2\\
&+(-L_1+L_2-x)\,t_1^2t_2^2-4L_2\,t_1t_2,\\[6pt]
F_y=\;&-y+2(L_1+L_2)\,t_1+2L_2\,t_2-y\,t_1^2-y\,t_2^2\\
&+2(L_1-L_2)\,t_1t_2^2-2L_2\,t_1^2t_2-y\,t_1^2t_2^2 .
\end{aligned}
$$
All monomials not displayed have coefficient $0$; in particular the coefficient of $t_1t_2$ in $F_y$ vanishes.

*Proof.* Expand the three summands of $F_x$:
$$L_1(1-t_1^2)D_2=L_1\bigl(1+t_2^2-t_1^2-t_1^2t_2^2\bigr),$$
$$L_2\bigl[(1-t_1^2)(1-t_2^2)-4t_1t_2\bigr]=L_2\bigl(1-t_1^2-t_2^2+t_1^2t_2^2-4t_1t_2\bigr),$$
$$-x\,D_1D_2=-x\bigl(1+t_1^2+t_2^2+t_1^2t_2^2\bigr).$$
Only the monomials $1,\ t_1^2,\ t_2^2,\ t_1^2t_2^2,\ t_1t_2$ occur, with coefficients respectively
$$L_1+L_2-x,\quad-L_1-L_2-x,\quad L_1-L_2-x,\quad-L_1+L_2-x,\quad-4L_2,$$
which is the displayed formula for $F_x$. Similarly
$$2L_1t_1D_2=2L_1t_1+2L_1t_1t_2^2,$$
$$2L_2\bigl[t_1(1-t_2^2)+t_2(1-t_1^2)\bigr]=2L_2t_1-2L_2t_1t_2^2+2L_2t_2-2L_2t_1^2t_2,$$
$$-y\,D_1D_2=-y-y\,t_1^2-y\,t_2^2-y\,t_1^2t_2^2 .$$
Only $1,\ t_1,\ t_2,\ t_1^2,\ t_2^2,\ t_1t_2^2,\ t_1^2t_2,\ t_1^2t_2^2$ occur, with coefficients respectively
$$-y,\quad 2L_1+2L_2,\quad 2L_2,\quad -y,\quad -y,\quad 2L_1-2L_2,\quad -2L_2,\quad -y,$$
as displayed. No summand contributes a $t_1t_2$ term to $F_y$. $\blacksquare$

**Proposition 4.3 (rationalised forward kinematics).** For every $(t_1,t_2)\in\mathbb R^2$, with $q=\Theta(t_1,t_2)$,
$$P(q)=P^\star\iff\bigl(F_x(t_1,t_2)=0\ \text{ and }\ F_y(t_1,t_2)=0\bigr).$$

*Proof.* The angle-sum identities hold for all real $q_1,q_2$. Substituting Lemma 2.5,
$$\cos(q_1+q_2)=\cos q_1\cos q_2-\sin q_1\sin q_2=\frac{(1-t_1^2)(1-t_2^2)-4t_1t_2}{D_1D_2},$$
$$\sin(q_1+q_2)=\sin q_1\cos q_2+\cos q_1\sin q_2=\frac{2t_1(1-t_2^2)+2t_2(1-t_1^2)}{D_1D_2},$$
the denominators being legitimate since $D_1D_2>0$ (Corollary 3.2). Hence
$$P(q)_1=\frac{L_1(1-t_1^2)D_2+L_2\bigl[(1-t_1^2)(1-t_2^2)-4t_1t_2\bigr]}{D_1D_2},\qquad
P(q)_2=\frac{2L_1t_1D_2+2L_2\bigl[t_1(1-t_2^2)+t_2(1-t_1^2)\bigr]}{D_1D_2}.$$
Now $P(q)=P^\star$ holds iff both coordinate equations hold. For the first, Lemma 2.1 with $\lambda=D_1D_2>0$ gives
$$P(q)_1=x\iff L_1(1-t_1^2)D_2+L_2\bigl[\cdots\bigr]=x\,D_1D_2\iff F_x=0,$$
and identically for the second coordinate with $F_y$. $\blacksquare$

**Remark 4.4 (spot checks of the expansion only).** Let $L_1=L_2=1$. For $(t_1,t_2)=(1,0)$ we have $q=(\pi/2,0)$ and $P(q)=(0,2)$; with $(x,y)=(0,2)$, Lemma 4.2 gives $F_x=2-2=0$ and $F_y=-2+4-2=0$. For $(t_1,t_2)=(0,1)$, $q=(0,\pi/2)$ and $P(q)=(1,1)$; with $(x,y)=(1,1)$, $F_x=1-1=0$ and $F_y=-1+2-1=0$. For $(t_1,t_2)=(1,1)$, $q=(\pi/2,\pi/2)$ and $P(q)=(-1,1)$; with $(x,y)=(-1,1)$, $F_x=3-1+1+1-4=0$ and $F_y=-1+4+2-1-1+0-2-1=0$. These verify the *expansion* of Lemma 4.2. Proposition 4.3 is proved above without appeal to them.

---

## 5. The singularity margin

**Lemma 5.1.** For every $q\in\mathbb R^2$, $\ \det J(q)=L_1L_2\sin q_2$.

*Proof.* Write $c_1=\cos q_1$, $s_1=\sin q_1$, $c_{12}=\cos(q_1+q_2)$, $s_{12}=\sin(q_1+q_2)$. From $P(q)=(L_1c_1+L_2c_{12},\ L_1s_1+L_2s_{12})$ and $\partial(q_1+q_2)/\partial q_1=\partial(q_1+q_2)/\partial q_2=1$,
$$J=\begin{pmatrix}-L_1s_1-L_2s_{12}&-L_2s_{12}\\[2pt] L_1c_1+L_2c_{12}&L_2c_{12}\end{pmatrix},$$
whence
$$
\begin{aligned}
\det J&=(-L_1s_1-L_2s_{12})(L_2c_{12})+(L_2s_{12})(L_1c_1+L_2c_{12})\\
&=-L_1L_2s_1c_{12}-L_2^2s_{12}c_{12}+L_1L_2s_{12}c_1+L_2^2s_{12}c_{12}\\
&=L_1L_2\bigl(s_{12}c_1-c_{12}s_1\bigr)
=L_1L_2\sin\bigl((q_1+q_2)-q_1\bigr)=L_1L_2\sin q_2,
\end{aligned}
$$
using $\sin(\alpha-\beta)=\sin\alpha\cos\beta-\cos\alpha\sin\beta$ with $\alpha=q_1+q_2$, $\beta=q_1$. $\blacksquare$

**Definition 5.2.** $\ G(t_2):=\bigl(4L_1^2L_2^2-2\varepsilon^2\bigr)t_2^2-\varepsilon^2t_2^4-\varepsilon^2\ \in\ \mathbb R[t_2]$.

**Proposition 5.3.** For every $t_2\in\mathbb R$, every $q_1\in\mathbb R$, and $q_2=\tau(t_2)$,
$$\bigl\lvert\det J(q_1,q_2)\bigr\rvert\ge\varepsilon\iff G(t_2)\ge0 .$$

*Proof.* By Lemma 5.1 and Lemma 2.5, $\det J=L_1L_2\sin q_2=2L_1L_2t_2/D_2$, which does not involve $q_1$. Since $D_2>0$ we have $\lvert2L_1L_2t_2/D_2\rvert=\lvert2L_1L_2t_2\rvert/D_2$, and Lemma 2.1 with $\lambda=D_2>0$ gives
$$\lvert\det J\rvert\ge\varepsilon\iff\lvert2L_1L_2t_2\rvert\ge\varepsilon D_2 .$$
Apply Lemma 2.3 with $a:=2L_1L_2t_2$ and $b:=\varepsilon D_2$; its hypothesis $b\ge0$ holds by Corollary 3.2, globally in $t_2$, so no case distinction on the sign of $t_2$ or of $\det J$ arises. Hence
$$\lvert\det J\rvert\ge\varepsilon\iff 4L_1^2L_2^2t_2^2\ge\varepsilon^2D_2^2 .$$
Finally $D_2^2=1+2t_2^2+t_2^4$, so the last inequality reads
$$4L_1^2L_2^2t_2^2-\varepsilon^2-2\varepsilon^2t_2^2-\varepsilon^2t_2^4\ge0,$$
which is exactly $G(t_2)\ge0$. $\blacksquare$

**Corollary 5.4 (feasibility of the singularity constraint).**

1. If $\varepsilon=0$ then $G(t_2)=4L_1^2L_2^2t_2^2\ge0$ for every $t_2$, so $\{t_2:G(t_2)\ge0\}=\mathbb R$.
2. If $\varepsilon>0$ then $\{t_2:G(t_2)\ge0\}\neq\emptyset$ iff $\varepsilon\le\lvert L_1L_2\rvert$, and in that case
$$\{t_2:G(t_2)\ge0\}=\bigl\{t_2:\ u_-\le t_2^2\le u_+\bigr\},\qquad
u_\pm=\frac{\bigl(4L_1^2L_2^2-2\varepsilon^2\bigr)\pm\sqrt{\bigl(4L_1^2L_2^2-2\varepsilon^2\bigr)^2-4\varepsilon^4}}{2\varepsilon^2},$$
with $0<u_-\le1\le u_+$.

*Proof.* (1) is immediate from Definition 5.2 with $\varepsilon=0$.

(2) Put $z:=t_2^2\ge0$. Then $G\ge0$ reads
$$\varepsilon^2z^2-\bigl(4L_1^2L_2^2-2\varepsilon^2\bigr)z+\varepsilon^2\le0,$$
a quadratic in $z$ with strictly positive leading coefficient $\varepsilon^2$. Its solution set in $\mathbb R$ is nonempty iff the discriminant
$$\Delta:=\bigl(4L_1^2L_2^2-2\varepsilon^2\bigr)^2-4\varepsilon^4$$
is $\ge0$, in which case that set is the closed interval $[u_-,u_+]$ with $u_\pm$ as displayed.

Now $\Delta=\bigl(4L_1^2L_2^2-2\varepsilon^2\bigr)^2-(2\varepsilon^2)^2\ge0$ iff $\bigl\lvert4L_1^2L_2^2-2\varepsilon^2\bigr\rvert\ge2\varepsilon^2$. The branch $4L_1^2L_2^2-2\varepsilon^2\le-2\varepsilon^2$ forces $L_1^2L_2^2\le0$, hence $L_1L_2=0$, contradicting (H1). So
$$\Delta\ge0\iff4L_1^2L_2^2\ge4\varepsilon^2\iff(L_1L_2)^2\ge\varepsilon^2\iff\lvert L_1L_2\rvert\ge\varepsilon,$$
the last step by Lemma 2.3 with $a=L_1L_2$, $b=\varepsilon\ge0$.

Assume $\Delta\ge0$. The product of the two roots is $\varepsilon^2/\varepsilon^2=1>0$ and their sum is $\bigl(4L_1^2L_2^2-2\varepsilon^2\bigr)/\varepsilon^2\ge2>0$, using $4L_1^2L_2^2-2\varepsilon^2\ge2\varepsilon^2$ from the previous paragraph. Hence both roots are positive, and $u_-u_+=1$ forces $u_-\le1\le u_+$. Since $z=t_2^2$ ranges over $[0,\infty)$ and $[u_-,u_+]\subseteq(0,\infty)$, the set $\{t_2:u_-\le t_2^2\le u_+\}$ is exactly the solution set, and it is nonempty (it contains $t_2=1$). $\blacksquare$

**Remark 5.5 (independent check).** By Lemma 5.1, condition (c) says $\lvert\sin q_2\rvert\ge\varepsilon/\lvert L_1L_2\rvert$, which is satisfiable by some $q_2\in(-\pi,\pi)$ iff $\varepsilon\le\lvert L_1L_2\rvert$. This agrees with Corollary 5.4 and is obtained without reference to $G$.

---

## 6. Point-to-segment distance: the case split

**Lemma 6.1.** Let $A,B,C\in\mathbb R^2$ with $v:=B-A\neq0$ and $w:=C-A$, and set
$$s^\star:=\frac{w\cdot v}{v\cdot v}\qquad(\text{well defined, since }v\cdot v>0).$$
Define
$$d_{\mathrm I}^2:=w\cdot w,\qquad d_{\mathrm{II}}^2:=\lVert C-B\rVert^2,\qquad
d_{\mathrm{III}}^2:=w\cdot w-\frac{(w\cdot v)^2}{v\cdot v},$$
and put $d^2:=\operatorname{dist}\bigl(C,[A,B]\bigr)^2$. Then:

1. $s^\star\le0\implies d^2=d_{\mathrm I}^2$;
2. $s^\star\ge1\implies d^2=d_{\mathrm{II}}^2$;
3. $0\le s^\star\le1\implies d^2=d_{\mathrm{III}}^2$;
4. *(seam agreement)* $s^\star=0\implies d_{\mathrm I}^2=d_{\mathrm{III}}^2$, and $s^\star=1\implies d_{\mathrm{II}}^2=d_{\mathrm{III}}^2$;
5. *(covering)* at least one of $s^\star\le0$, $s^\star\ge1$, $0\le s^\star\le1$ holds.

*Proof.* For $s\in\mathbb R$ put
$$f(s):=\lVert A+sv-C\rVert^2=\lVert sv-w\rVert^2=(v\cdot v)s^2-2(w\cdot v)s+w\cdot w .$$
Since $v\cdot v>0$, completing the square gives
$$f(s)=(v\cdot v)\bigl(s-s^\star\bigr)^2+d_{\mathrm{III}}^2 ,$$
so $f$ is strictly decreasing on $(-\infty,s^\star]$, strictly increasing on $[s^\star,\infty)$, and $f(s^\star)=d_{\mathrm{III}}^2$ is the global minimum. By definition of $[A,B]$, $d^2=\min_{s\in[0,1]}f(s)$.

(1) If $s^\star\le0$ then $[0,1]\subseteq[s^\star,\infty)$, where $f$ is increasing, so the minimum over $[0,1]$ is at $s=0$: $d^2=f(0)=w\cdot w=d_{\mathrm I}^2$.

(2) If $s^\star\ge1$ then $[0,1]\subseteq(-\infty,s^\star]$, where $f$ is decreasing, so the minimum is at $s=1$:
$$d^2=f(1)=\lVert v-w\rVert^2=\lVert(B-A)-(C-A)\rVert^2=\lVert B-C\rVert^2=d_{\mathrm{II}}^2 .$$

(3) If $0\le s^\star\le1$ then $s^\star\in[0,1]$, and $f(s^\star)$ is the global minimum of $f$, a fortiori the minimum over $[0,1]$; so $d^2=d_{\mathrm{III}}^2$.

(4) If $s^\star=0$ then $w\cdot v=0$, so $d_{\mathrm{III}}^2=w\cdot w=d_{\mathrm I}^2$. If $s^\star=1$ then $w\cdot v=v\cdot v$, so $d_{\mathrm{III}}^2=w\cdot w-(v\cdot v)$, while
$$d_{\mathrm{II}}^2=\lVert v-w\rVert^2=v\cdot v-2\,w\cdot v+w\cdot w=w\cdot w-v\cdot v ;$$
the two agree.

(5) If $s^\star<0$ the first alternative holds; if $s^\star>1$ the second; otherwise $0\le s^\star\le1$. $\blacksquare$

**Corollary 6.2 (a correct disjunctive split with overlapping selectors).** With $A,B,C,v,w,s^\star$ as in Lemma 6.1 and any $R\ge0$,
$$\operatorname{dist}\bigl(C,[A,B]\bigr)\ge R
\iff\bigvee_{k\in\{\mathrm I,\mathrm{II},\mathrm{III}\}}\bigl(\sigma_k\wedge d_k^2\ge R^2\bigr),$$
where
$$\sigma_{\mathrm I}:\ s^\star\le0,\qquad \sigma_{\mathrm{II}}:\ s^\star\ge1,\qquad \sigma_{\mathrm{III}}:\ 0\le s^\star\le1 .$$

*Proof.* First, $\operatorname{dist}(C,[A,B])\ge R\iff d^2\ge R^2$ by Lemma 2.3 applied with $a:=\operatorname{dist}(C,[A,B])\ge0$ (so $\lvert a\rvert=a$ and $a^2=d^2$) and $b:=R\ge0$.

$(\Leftarrow)$ Suppose $\sigma_k$ and $d_k^2\ge R^2$ hold for some $k$. By Lemma 6.1(1)–(3), $\sigma_k$ implies $d_k^2=d^2$; hence $d^2\ge R^2$.

$(\Rightarrow)$ Suppose $d^2\ge R^2$. By Lemma 6.1(5) some $\sigma_k$ holds, and then $d_k^2=d^2\ge R^2$ by Lemma 6.1(1)–(3). $\blacksquare$

**Remark 6.3.** The three selectors overlap at $s^\star\in\{0,1\}$. The overlap is harmless in the $(\Leftarrow)$ direction because, by Lemma 6.1(4), the overlapping formulas return the *same real number*; and the non-strictness is precisely what supplies the covering property (5), which the $(\Rightarrow)$ direction consumes. Section 14 determines exactly which changes to these inequalities break which direction, and where.

---

## 7. Rational data for the two segments

Throughout this section $t_1\in\mathbb R$ is arbitrary and $q_1=\tau(t_1)$.

**Definition 7.1.** Put
$$\mathbf e(t_1):=\bigl(L_1(1-t_1^2),\ 2L_1t_1\bigr)\qquad\text{(the \emph{elbow numerator})},$$
$$\mathbf g(t_1):=D_1C-\mathbf e(t_1),\qquad \mathbf h(t_1):=\mathbf e(t_1)-D_1P^\star,$$
with components $\mathbf g=(g_x,g_y)$ and $\mathbf h=(h_x,h_y)$, and
$$\Pi^{(1)}(t_1):=C\cdot\mathbf e(t_1),\qquad
\Pi^{(2)}(t_1):=(C-P^\star)\cdot\mathbf h(t_1),\qquad
\Sigma^{(2)}(t_1):=\lVert\mathbf h(t_1)\rVert^2 .$$
Explicitly,
$$
\begin{aligned}
\Pi^{(1)}&=L_1\bigl(c_x+2c_yt_1-c_xt_1^2\bigr),\\
g_x&=(c_x-L_1)+(c_x+L_1)t_1^2, &\qquad g_y&=c_y-2L_1t_1+c_yt_1^2,\\
h_x&=(L_1-x)-(L_1+x)t_1^2, &\qquad h_y&=-y+2L_1t_1-yt_1^2,\\
\Pi^{(2)}&=(c_x-x)h_x+(c_y-y)h_y, &\qquad \Sigma^{(2)}&=h_x^2+h_y^2 .
\end{aligned}
$$
All seven are polynomials in $t_1$ alone with real coefficients.

**Remark 7.2 (reading the notation).** $\mathbf e$, $\mathbf g$, $\mathbf h$ are *numerator vectors*, not points. By Lemma 7.3 below,
$$\mathbf e=D_1E(q_1),\qquad \mathbf g=D_1\bigl(C-E(q_1)\bigr),\qquad \mathbf h=D_1\bigl(E(q_1)-P^\star\bigr).$$
In particular no component of $\mathbf g$ or $\mathbf h$ is a coordinate of any of the points $E(q_1)$, $C$, $C-E(q_1)$, $E(q_1)-P^\star$: each is $D_1$ times such a coordinate. Superscripts $(1),(2)$ index **segments**; subscripts $1,2$ index **joints**. Both conventions occur inside a single formula (for instance $D_1\Pi^{(2)}$), and must not be conflated.

**Lemma 7.3 (unconditional identities).** For every $t_1\in\mathbb R$:

1. $E(q_1)=\mathbf e(t_1)/D_1$, and $\lVert\mathbf e(t_1)\rVert^2=L_1^2D_1^2$, hence $\lVert E(q_1)\rVert=\lvert L_1\rvert$;
2. $\mathbf g(t_1)=D_1\bigl(C-E(q_1)\bigr)$, hence $\lVert C-E(q_1)\rVert^2=\bigl(g_x^2+g_y^2\bigr)/D_1^2$;
3. $\mathbf h(t_1)=D_1\bigl(E(q_1)-P^\star\bigr)$, hence $\lVert E(q_1)-P^\star\rVert^2=\Sigma^{(2)}/D_1^2$;
4. $C\cdot E(q_1)=\Pi^{(1)}/D_1$ and $(C-P^\star)\cdot\bigl(E(q_1)-P^\star\bigr)=\Pi^{(2)}/D_1$;
5. $D_1\Pi^{(2)}-\Sigma^{(2)}=\mathbf g\cdot\mathbf h$ and $D_1\bigl(\Pi^{(1)}-L_1^2D_1\bigr)=\mathbf g\cdot\mathbf e$.

None of these uses any hypothesis beyond (H1); in particular none uses condition (a).

*Proof.* (1) By Lemma 2.5,
$$E(q_1)=\Bigl(L_1\frac{1-t_1^2}{D_1},\ L_1\frac{2t_1}{D_1}\Bigr)=\frac{\mathbf e}{D_1},$$
and
$$\lVert\mathbf e\rVert^2=L_1^2(1-t_1^2)^2+4L_1^2t_1^2=L_1^2\bigl(1-2t_1^2+t_1^4+4t_1^2\bigr)=L_1^2(1+t_1^2)^2=L_1^2D_1^2 .$$
Dividing by $D_1^2>0$ gives $\lVert E(q_1)\rVert^2=L_1^2$, so $\lVert E(q_1)\rVert=\lvert L_1\rvert$.

(2) $\mathbf g=D_1C-\mathbf e=D_1C-D_1E(q_1)=D_1\bigl(C-E(q_1)\bigr)$; divide by $D_1>0$ and take squared norms.

(3) $\mathbf h=\mathbf e-D_1P^\star=D_1E(q_1)-D_1P^\star=D_1\bigl(E(q_1)-P^\star\bigr)$; likewise.

(4) $\Pi^{(1)}=C\cdot\mathbf e=D_1\,C\cdot E(q_1)$ and $\Pi^{(2)}=(C-P^\star)\cdot\mathbf h=D_1\,(C-P^\star)\cdot\bigl(E(q_1)-P^\star\bigr)$ by (1) and (3); divide by $D_1>0$.

(5) Using (3) in the second step,
$$D_1\Pi^{(2)}-\Sigma^{(2)}=\mathbf h\cdot\bigl(D_1(C-P^\star)-\mathbf h\bigr)
=\mathbf h\cdot\bigl(D_1C-D_1P^\star-\mathbf e+D_1P^\star\bigr)=\mathbf h\cdot(D_1C-\mathbf e)=\mathbf h\cdot\mathbf g .$$
Similarly, using (1),
$$\mathbf g\cdot\mathbf e=(D_1C-\mathbf e)\cdot\mathbf e=D_1\Pi^{(1)}-L_1^2D_1^2=D_1\bigl(\Pi^{(1)}-L_1^2D_1\bigr). \qquad\blacksquare$$

**Lemma 7.4 (degrees).** As polynomials in $t_1$:

| polynomial | degree at most | leading coefficient | the degree drops exactly when |
|---|---|---|---|
| $\Pi^{(1)}$ | $2$ | $-L_1c_x$ | $c_x=0$ |
| $g_x$ | $2$ | $c_x+L_1$ | $c_x=-L_1$ |
| $g_y$ | $2$ | $c_y$ | $c_y=0$ |
| $h_x$ | $2$ | $-(L_1+x)$ | $x=-L_1$ |
| $h_y$ | $2$ | $-y$ | $y=0$ |
| $\Pi^{(2)}$ | $2$ | $-\bigl[(c_x-x)(L_1+x)+(c_y-y)y\bigr]$ | that expression vanishes |
| $\Sigma^{(2)}$ | $4$ | $(L_1+x)^2+y^2$ | $(x,y)=(-L_1,0)$ |

*Proof.* Read the coefficients off the displayed formulas of Definition 7.1. For $\Sigma^{(2)}=h_x^2+h_y^2$ the coefficient of $t_1^4$ is $(L_1+x)^2+y^2$, a sum of two squares, which vanishes iff $x=-L_1$ and $y=0$. $\blacksquare$

**Remark 7.5.** The entries of the second column are *upper bounds*, attained only under the side conditions of the fourth. Nothing below depends on the degrees; the table is recorded because it is the interface an implementation must respect, and because an implementation that *asserts* $\deg\Sigma^{(2)}=4$ fails on the reachable instance $(x,y)=(-L_1,0)$.

The two link segments share the endpoint $E(q_1)$ and differ only in their other endpoint, which is a constant in both cases once (a) is imposed. The next lemma treats both at once.

**Lemma 7.6 (uniform segment data).** Let $A\in\mathbb R^2$ be a constant point, and set
$$\mathbf h_A(t_1):=\mathbf e(t_1)-D_1A,\qquad \Pi_A:=(C-A)\cdot\mathbf h_A,\qquad \Sigma_A:=\lVert\mathbf h_A\rVert^2 .$$
Put $B:=E(q_1)$, $v:=B-A$, $w:=C-A$. Then
$$v=\frac{\mathbf h_A}{D_1},\qquad v\cdot v=\frac{\Sigma_A}{D_1^2},\qquad w\cdot v=\frac{\Pi_A}{D_1},$$
and $v\neq0\iff\Sigma_A>0$. If $\Sigma_A>0$, then with $s^\star$ and $d_k^2$ as in Lemma 6.1,
$$s^\star=\frac{D_1\Pi_A}{\Sigma_A},\qquad
d_{\mathrm I}^2=\lVert C-A\rVert^2,\qquad
d_{\mathrm{II}}^2=\frac{g_x^2+g_y^2}{D_1^2},\qquad
d_{\mathrm{III}}^2=\lVert C-A\rVert^2-\frac{\Pi_A^2}{\Sigma_A}.$$

*Proof.* By Lemma 7.3(1), $\mathbf h_A=\mathbf e-D_1A=D_1E(q_1)-D_1A=D_1v$; hence $v=\mathbf h_A/D_1$ and $v\cdot v=\Sigma_A/D_1^2$. Since $D_1>0$, $v=0\iff\mathbf h_A=0\iff\Sigma_A=0$. Also $w\cdot v=(C-A)\cdot\mathbf h_A/D_1=\Pi_A/D_1$.

Assume $\Sigma_A>0$. Then
$$s^\star=\frac{w\cdot v}{v\cdot v}=\frac{\Pi_A/D_1}{\Sigma_A/D_1^2}=\frac{D_1\Pi_A}{\Sigma_A}.$$
Next, $d_{\mathrm I}^2=w\cdot w=\lVert C-A\rVert^2$; and $d_{\mathrm{II}}^2=\lVert C-B\rVert^2=\lVert C-E(q_1)\rVert^2=(g_x^2+g_y^2)/D_1^2$ by Lemma 7.3(2); and
$$d_{\mathrm{III}}^2=w\cdot w-\frac{(w\cdot v)^2}{v\cdot v}
=\lVert C-A\rVert^2-\frac{\Pi_A^2/D_1^2}{\Sigma_A/D_1^2}=\lVert C-A\rVert^2-\frac{\Pi_A^2}{\Sigma_A}. \qquad\blacksquare$$

**Corollary 7.7 (the elbow predicate is shared for a structural reason).** In Lemma 7.6 the quantity $d_{\mathrm{II}}^2$ does not depend on $A$. Since both link segments have $B=E(q_1)$ as an endpoint, the case-$\mathrm{II}$ quantity is in both cases the single real number
$$\lVert C-E(q_1)\rVert^2=\frac{g_x^2+g_y^2}{D_1^2},$$
the squared distance from the obstacle centre to the elbow. Two occurrences of one real-valued function of $t_1$ introduce no coupling between the two segments.

**Proposition 7.8 (generic disjunction).** In the setting of Lemma 7.6, assume $\Sigma_A(t_1)>0$ and $R\ge0$. Then
$$\operatorname{dist}\bigl(C,[A,E(q_1)]\bigr)\ge R\iff\Psi_A(t_1),$$
where $\Psi_A(t_1)$ denotes the disjunction
$$
\begin{aligned}
&\bigl[\ \Pi_A\le0\ \wedge\ \lVert C-A\rVert^2-R^2\ge0\ \bigr]\\
\vee\;&\bigl[\ D_1\Pi_A-\Sigma_A\ge0\ \wedge\ g_x^2+g_y^2-R^2D_1^2\ge0\ \bigr]\\
\vee\;&\bigl[\ \Pi_A\ge0\ \wedge\ \Sigma_A-D_1\Pi_A\ge0\ \wedge\ \bigl(\lVert C-A\rVert^2-R^2\bigr)\Sigma_A-\Pi_A^2\ge0\ \bigr].
\end{aligned}
$$

*Proof.* By Lemma 7.6, $v\neq0$, so Lemma 6.1 and Corollary 6.2 apply, the latter using $R\ge0$.

*Selectors.* Since $\Sigma_A>0$, Lemma 2.1 with $\lambda=\Sigma_A$ turns $s^\star\le0$ into $\Sigma_As^\star\le0$, i.e. $D_1\Pi_A\le0$, and Lemma 2.1 with $\lambda=D_1^{-1}>0$ turns this into $\Pi_A\le0$. The same two steps give $s^\star\ge1\iff D_1\Pi_A\ge\Sigma_A\iff D_1\Pi_A-\Sigma_A\ge0$, and consequently
$$0\le s^\star\le1\iff\Pi_A\ge0\ \wedge\ \Sigma_A-D_1\Pi_A\ge0 .$$

*Case values.* $d_{\mathrm I}^2\ge R^2\iff\lVert C-A\rVert^2-R^2\ge0$. By Lemma 2.1 with $\lambda=D_1^2>0$,
$$d_{\mathrm{II}}^2\ge R^2\iff g_x^2+g_y^2\ge R^2D_1^2 .$$
By Lemma 2.1 with $\lambda=\Sigma_A>0$,
$$d_{\mathrm{III}}^2\ge R^2\iff\bigl(\lVert C-A\rVert^2-R^2\bigr)\Sigma_A-\Pi_A^2\ge0 .$$

Substituting these six equivalences into Corollary 6.2 yields exactly $\Psi_A$. $\blacksquare$

---

## 8. Segment 1 (shoulder to elbow)

Here $A=O$, so $\mathbf h_O=\mathbf e$, $\ \Sigma_O=\lVert\mathbf e\rVert^2=L_1^2D_1^2$ and $\Pi_O=C\cdot\mathbf e=\Pi^{(1)}$.

**Definition 8.1.** $\Psi^{(1)}(t_1)$ denotes the disjunction
$$
\begin{aligned}
&\bigl[\ \Pi^{(1)}\le0\ \wedge\ c_x^2+c_y^2-R^2\ge0\ \bigr]\\
\vee\;&\bigl[\ \Pi^{(1)}-L_1^2D_1\ge0\ \wedge\ g_x^2+g_y^2-R^2D_1^2\ge0\ \bigr]\\
\vee\;&\bigl[\ \Pi^{(1)}\ge0\ \wedge\ L_1^2D_1-\Pi^{(1)}\ge0\ \wedge\ \bigl(c_x^2+c_y^2-R^2\bigr)L_1^2D_1^2-\bigl(\Pi^{(1)}\bigr)^2\ge0\ \bigr].
\end{aligned}
$$

**Proposition 8.2 (segment 1; unconditional).** For every $t_1\in\mathbb R$, with $q_1=\tau(t_1)$,
$$\operatorname{dist}\bigl(C,\mathcal S^{(1)}(q)\bigr)\ge R\iff\Psi^{(1)}(t_1).$$
No hypothesis beyond (H1)–(H3) is used; in particular condition (a) is **not** required.

*Proof.* We have $\Sigma_O=L_1^2D_1^2>0$ by Corollary 3.2, so Proposition 7.8 applies with $A=O$. Using $\lVert C-O\rVert^2=c_x^2+c_y^2$ and $\Sigma_O=L_1^2D_1^2$, it yields the equivalence of $\operatorname{dist}(C,\mathcal S^{(1)}(q))\ge R$ with
$$
\begin{aligned}
&\bigl[\Pi^{(1)}\le0\wedge c_x^2+c_y^2-R^2\ge0\bigr]\\
\vee\;&\bigl[D_1\Pi^{(1)}-L_1^2D_1^2\ge0\wedge g_x^2+g_y^2-R^2D_1^2\ge0\bigr]\\
\vee\;&\bigl[\Pi^{(1)}\ge0\wedge L_1^2D_1^2-D_1\Pi^{(1)}\ge0\wedge\bigl(c_x^2+c_y^2-R^2\bigr)L_1^2D_1^2-\bigl(\Pi^{(1)}\bigr)^2\ge0\bigr].
\end{aligned}
$$
By Lemma 2.1 with $\lambda=D_1>0$,
$$D_1\Pi^{(1)}-L_1^2D_1^2\ge0\iff\Pi^{(1)}-L_1^2D_1\ge0,\qquad
L_1^2D_1^2-D_1\Pi^{(1)}\ge0\iff L_1^2D_1-\Pi^{(1)}\ge0 .$$
Substituting these gives exactly $\Psi^{(1)}$. $\blacksquare$

**Remark 8.3.** The cancellation of one factor $D_1$ in the second and third clauses is the only reason $\Psi^{(1)}$ and $\Psi^{(2)}$ below are not of literally identical shape: for segment 1 the squared length $\Sigma_O=L_1^2D_1^2$ carries the factor $D_1^2$ explicitly, while for segment 2 the corresponding quantity does not factor.

---

## 9. Segment 2 (elbow to tool)

The far endpoint of $\mathcal S^{(2)}(q)=[E(q_1),P(q)]$ depends on $q_2$. The encoding replaces $P(q)$ by the constant $P^\star$. This replacement is an identity of sets exactly on the locus where (a) holds. Everything in this section is organised around making that statement, and its failure elsewhere, precise.

Here $A=P^\star$, so $\mathbf h_{P^\star}=\mathbf h$, $\ \Sigma_{P^\star}=\Sigma^{(2)}$ and $\Pi_{P^\star}=\Pi^{(2)}$.

**Definition 9.1.** $\Psi^{(2)}(t_1)$ denotes the disjunction
$$
\begin{aligned}
&\bigl[\ \Pi^{(2)}\le0\ \wedge\ (c_x-x)^2+(c_y-y)^2-R^2\ge0\ \bigr]\\
\vee\;&\bigl[\ D_1\Pi^{(2)}-\Sigma^{(2)}\ge0\ \wedge\ g_x^2+g_y^2-R^2D_1^2\ge0\ \bigr]\\
\vee\;&\bigl[\ \Pi^{(2)}\ge0\ \wedge\ \Sigma^{(2)}-D_1\Pi^{(2)}\ge0\ \wedge\ \bigl((c_x-x)^2+(c_y-y)^2-R^2\bigr)\Sigma^{(2)}-\bigl(\Pi^{(2)}\bigr)^2\ge0\ \bigr].
\end{aligned}
$$
This is a predicate in $t_1$ alone.

**Lemma 9.2 (the degeneracy locus; unconditional).** For every $t_1\in\mathbb R$,
$$\Sigma^{(2)}(t_1)=0\iff E(\tau(t_1))=P^\star .$$
Moreover, if $\Sigma^{(2)}(t_1)=0$ then **no** $t_2\in\mathbb R$ makes $(t_1,t_2)$ satisfy (a); and $\Sigma^{(2)}$ can vanish at some $t_1$ only if $x^2+y^2=L_1^2$.

*Proof.* By Lemma 7.3(3) — which is unconditional — $\Sigma^{(2)}=D_1^2\lVert E(q_1)-P^\star\rVert^2$ with $D_1^2>0$; hence $\Sigma^{(2)}=0\iff E(q_1)=P^\star$.

Suppose $\Sigma^{(2)}(t_1)=0$ and that some $t_2$ made $(t_1,t_2)$ satisfy (a). By definition $P(q)-E(q_1)=L_2\bigl(\cos(q_1+q_2),\sin(q_1+q_2)\bigr)$, a vector of norm $\lvert L_2\rvert>0$ by (H1). Under (a) we have $P(q)=P^\star$, so $\lVert E(q_1)-P^\star\rVert=\lvert L_2\rvert>0$, contradicting $E(q_1)=P^\star$.

Finally $\lVert E(q_1)\rVert=\lvert L_1\rvert$ by Lemma 7.3(1), so $E(q_1)=P^\star$ forces $x^2+y^2=L_1^2$. $\blacksquare$

**Lemma 9.3 (nondegeneracy under (a)).** If $(t_1,t_2)\in\mathbb R^2$ satisfies (a), then
$$\lVert E(q_1)-P^\star\rVert=\lvert L_2\rvert>0\qquad\text{and}\qquad\Sigma^{(2)}(t_1)=L_2^2D_1^2>0 .$$

*Proof.* As in the previous proof, $\lVert P(q)-E(q_1)\rVert=\lvert L_2\rvert$, and (a) gives $P(q)=P^\star$, whence $\lVert E(q_1)-P^\star\rVert=\lvert L_2\rvert$, which is $>0$ by (H1). By Lemma 7.3(3),
$$\Sigma^{(2)}=D_1^2\lVert E(q_1)-P^\star\rVert^2=D_1^2L_2^2>0 . \qquad\blacksquare$$

**Proposition 9.4 (what $\Psi^{(2)}$ says, with and without (a)).** Let $t_1\in\mathbb R$.

1. If $\Sigma^{(2)}(t_1)>0$, then
$$\operatorname{dist}\bigl(C,[E(q_1),P^\star]\bigr)\ge R\iff\Psi^{(2)}(t_1).$$
2. If $(t_1,t_2)$ satisfies (a) for some $t_2$, then $\Sigma^{(2)}(t_1)>0$ and $[E(q_1),P^\star]=\mathcal S^{(2)}(q)$, so
$$\operatorname{dist}\bigl(C,\mathcal S^{(2)}(q)\bigr)\ge R\iff\Psi^{(2)}(t_1).$$
3. If $\Sigma^{(2)}(t_1)=0$, then $\Psi^{(2)}(t_1)$ is **true**, whatever the value of $\lVert C-P^\star\rVert$.

*Proof.* (1) Apply Proposition 7.8 with $A=P^\star$, using $\lVert C-P^\star\rVert^2=(c_x-x)^2+(c_y-y)^2$.

(2) $\Sigma^{(2)}(t_1)>0$ is Lemma 9.3. Under (a), $P(q)=P^\star$, so $\mathcal S^{(2)}(q)=[E(q_1),P(q)]=[E(q_1),P^\star]$ as sets — an identity, not an approximation. Now apply (1).

(3) If $\Sigma^{(2)}(t_1)=0$ then $\mathbf h(t_1)=0$, hence also $\Pi^{(2)}=(C-P^\star)\cdot\mathbf h=0$. The third clause of $\Psi^{(2)}$ then reads
$$0\ge0\ \wedge\ 0-0\ge0\ \wedge\ \bigl(\lVert C-P^\star\rVert^2-R^2\bigr)\cdot0-0\ge0,$$
all three of which hold. Hence $\Psi^{(2)}(t_1)$ is true. $\blacksquare$

**Remark 9.5 ($\Psi^{(2)}$ has no standalone meaning).** Proposition 9.4(3) is sharp and is the exact reason for this restriction. At a parameter $t_1$ with $E(q_1)=P^\star$ the set $[E(q_1),P^\star]$ degenerates to the single point $P^\star$, whose distance to $C$ is $\lVert C-P^\star\rVert$ and may be arbitrarily smaller than $R$ — and yet $\Psi^{(2)}(t_1)$ holds. Thus $\Psi^{(2)}$ **on its own is unsound** as a clearance certificate. Lemma 9.2 shows this can never do harm inside the conjunction defining $\Phi$, because $\Sigma^{(2)}(t_1)=0$ rules out $F_x=F_y=0$. Even where $\Sigma^{(2)}(t_1)>0$ but (a) fails, $\Psi^{(2)}(t_1)$ constrains the distance from $C$ to $[E(q_1),P^\star]$, which is not a link of the configuration $q$. Accordingly $\Psi^{(2)}$ must not be exposed as a separately meaningful predicate — not as a pruning filter, not as an independently reported clearance certificate, not as a lemma quoted elsewhere.

---

## 10. The encoded predicate and the main equivalence

**Definition 10.1.** The encoded predicate $\Phi$ on $\mathbb R^2$ is
$$\Phi(t_1,t_2):\qquad F_x=0\ \wedge\ F_y=0\ \wedge\ G(t_2)\ge0\ \wedge\ \Psi^{(1)}(t_1)\ \wedge\ \Psi^{(2)}(t_1).$$
It is a conjunction of polynomial equations with disjunctions of polynomial inequalities in $(t_1,t_2)$ — a semialgebraic condition — involving no denominators and no auxiliary variables.

**Theorem 10.2 (main equivalence).** Assume (H1)–(H3). For every $(t_1,t_2)\in\mathbb R^2$, with $q=\Theta(t_1,t_2)$,
$$\Phi(t_1,t_2)\iff q\ \text{is admissible, i.e. (a), (b) and (c) hold at }q .$$

*Proof.* $(\Rightarrow)$ Assume $\Phi(t_1,t_2)$.

*Step 1.* From $F_x=F_y=0$ and Proposition 4.3, condition **(a)** holds at $q$.
*Step 2.* From $G(t_2)\ge0$ and Proposition 5.3, condition **(c)** holds at $q$.
*Step 3.* From $\Psi^{(1)}(t_1)$ and Proposition 8.2 — which is unconditional — the first inequality of **(b)** holds.
*Step 4.* Because Step 1 has already established (a), Proposition 9.4(2) is applicable at $t_1$; combined with $\Psi^{(2)}(t_1)$ it yields $\operatorname{dist}(C,\mathcal S^{(2)}(q))\ge R$, the second inequality of **(b)**.

Hence (a), (b) and (c) all hold, and $q$ is admissible.

$(\Leftarrow)$ Assume $q$ is admissible. By Proposition 4.3, $F_x=F_y=0$. By Proposition 5.3, $G(t_2)\ge0$. By Proposition 8.2, the first inequality of (b) gives $\Psi^{(1)}(t_1)$. Because (a) holds, Proposition 9.4(2) is applicable, and the second inequality of (b) gives $\Psi^{(2)}(t_1)$. Hence $\Phi(t_1,t_2)$. $\blacksquare$

**Remark 10.3 (the staging of the proof is load-bearing).** Proposition 9.4(2) carries (a) as a hypothesis, and (a) is one of the three conclusions being derived in the $(\Rightarrow)$ direction. The argument is not circular because the derivation is strictly staged: $\Phi\Rightarrow$ (a) — by Step 1, which uses only the conjuncts $F_x=F_y=0$ — and only then is Proposition 9.4(2) invoked to obtain the second half of (b). Interchanging Steps 1 and 4 would be circular. No analogous risk arises for $\Psi^{(1)}$, since Proposition 8.2 is unconditional. The one remaining gap — that $\Psi^{(2)}$ is a *total* predicate, evaluable, and by Proposition 9.4(3) in fact *true*, at parameters where $s^\star$ is undefined — is closed by Lemma 9.2: at such $t_1$ both sides of the asserted equivalence are false, the left because $F_x=F_y=0$ is unattainable there, the right because (a) fails.

---
