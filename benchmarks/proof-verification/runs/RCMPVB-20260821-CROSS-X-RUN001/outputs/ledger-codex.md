# LEDGER v1

## Formal parse

1. **Fixed instance data.** The theorem is a schema over arbitrary
   \[
   (L_1,L_2,r,\mu,\varepsilon,x,y,c_x,c_y,a_1,b_1,a_2,b_2)\in\mathbf Q^{13}
   \]
   satisfying
   \[
   L_1,L_2,r,\mu,\varepsilon>0,\qquad
   0<\varepsilon\le L_1L_2,\qquad a_i<b_i.
   \]
   Thus \(R=r+\mu\in\mathbf Q_{>0}\), \(C,P^\star\in\mathbf Q^2\), and \(\mathcal B\) is a nonempty closed rational box.

2. **Witness and chart.** For each finite \(t=(t_1,t_2)\in\mathbf R^2\),
   \[
   D_i=1+t_i^2\ge1,
   \]
   so no denominator vanishes. The map \(q_i=2\arctan t_i\) covers exactly \(q_i\in(-\pi,\pi)\). Values \(q_i=\pm\pi\) and the formal points \(t_i=\pm\infty\) are excluded.

3. **Half-angle quantities.**
   \[
   \cos q_i=\frac{C_i}{D_i},\qquad
   \sin q_i=\frac{S_i}{D_i}.
   \]
   Here \(C=(c_x,c_y)\) and \(C_i=1-t_i^2\) are distinct objects.

4. **Geometry.** The segments are closed:
   \[
   [A,B]=\{A+\lambda(B-A):0\le\lambda\le1\}.
   \]
   Both physical links are nondegenerate:
   \[
   \|p_1-p_0\|=L_1>0,\qquad \|p_2-p_1\|=L_2>0.
   \]
   Euclidean distance includes endpoints and allows equality with \(R\).

5. **Right-hand predicate.** Define \(\Psi(t)\) as the conjunction—not a piecewise definition—of
   \[
   p_2=P^\star,\quad
   \operatorname{dist}(C,[p_0,p_1])\ge R,\quad
   \operatorname{dist}(C,[p_1,p_2])\ge R,\quad
   |\det J(q)|\ge\varepsilon.
   \]
   The vector equality \(p_2=P^\star\) means two scalar equalities.

6. **Pointwise claim.** For every admissible fixed instance,
   \[
   \forall t\in\mathbf R^2:\quad \Phi(t)\iff\Psi(t).
   \]
   The same \(t\) determines \(q,p_1,p_2\) on both sides. There is no separately quantified \(q\).

7. **Existential corollary.**
   \[
   (\exists t\in\mathcal B:\Phi(t))
   \iff
   (\exists t\in\mathcal B:\Psi(t)).
   \]
   This is weaker in form than the pointwise theorem and follows by retaining the same witness in each direction. It does not require compactness or witness attainment arguments.

8. **Polynomiality clause.** The coherent scope is: every atomic relation in the polynomial encoding \(\Phi\), together with an expanded description of \(t\in\mathcal B\), is \(P=0\), \(P\ge0\), or \(P\le0\) for \(P\in\mathbf Q[t_1,t_2]\). The geometric predicates on the right are not syntactically polynomial predicates; they are claimed to have the stated polynomial equivalents. A literal reading covering every relation printed anywhere would incorrectly include the strict data hypotheses \(a_i<b_i\).

9. **Boundary cases.**

   - \(D_i>0\) prevents denominator-zero cases.
   - \(t_i\) may be zero or negative.
   - \(\varepsilon=L_1L_2\) is allowed.
   - Distance equality \(=R\) and determinant equality \(=\varepsilon\) are accepted.
   - Selector seams use overlapping weak inequalities:
     \(W_1=0\), \(W_1=D_1L_1^2\), \(W_2=0\), and \(D_1W_2=Q_2\).
   - The target-based proxy for the second segment may be degenerate when forward kinematics is false; its use must remain guarded by \(F_x=F_y=0\).

10. **Scope exclusions.** No completeness is claimed on the configuration torus, no uncertain data or task points are quantified, no continuous path or trajectory is asserted, and failure of witness search does not establish certified infeasibility.

11. **Implementation correspondence.** Mathematical equivalence, existential validity, and implementation correspondence are three distinct claims. Neither mathematical theorem implies that a particular builder/checker uses this formula nor can implementation tests prove the theorem.

## Counterexample search

**Result: `NO COUNTEREXAMPLE FOUND`**, under the polynomiality interpretation stated above.

Exact adversarial checks:

1. **Forward-kinematics denominators.**
   \[
   F_x=D_1D_2(x-p_{2,x}),\qquad
   F_y=D_1D_2(y-p_{2,y}).
   \]
   Since \(D_1D_2>0\), clearing denominators introduces no extra roots.

2. **Zero and chart-boundary behavior.** At \(t_2=0\),
   \[
   G=-\varepsilon^2<0,\qquad \det J=0.
   \]
   Thus both singularity-margin predicates fail. As \(|t_i|\to\infty\), the omitted chart boundary is approached but never attained by a finite witness.

3. **Extremal singularity threshold.** If \(\varepsilon=L_1L_2\), then
   \[
   G=-\varepsilon^2(t_2^2-1)^2.
   \]
   Hence \(G\ge0\) precisely at \(t_2=\pm1\), where
   \(|\sin q_2|=1\) and \(|\det J|=\varepsilon\).

4. **Sign and squaring check.**
   \[
   G=D_2^2\bigl((\det J)^2-\varepsilon^2\bigr).
   \]
   Because \(D_2^2>0\), \(\varepsilon>0\), and absolute values are nonnegative, no sign information is lost when passing between \(G\ge0\) and \(|\det J|\ge\varepsilon\).

5. **First-segment seams.** Writing \(s=C\cdot p_1\), one has \(W_1=D_1s\). At the seams:
   \[
   W_1=0\implies H_{1,I}=D_1^2L_1^2H_{1,A},
   \]
   \[
   W_1=D_1L_1^2\implies H_{1,I}=L_1^2H_{1,B}.
   \]
   Positive factors ensure overlapping branches agree.

6. **Endpoint collisions.** If \(C=p_0\), the relevant squared clearance is \(-R^2<0\); if \(C=p_1\), the corresponding \(H_{1,B}\) is \(-R^2D_1^2<0\). The weak selector seams do not create a false clearance result.

7. **Second-segment orientation.** Under \(p_2=P^\star\), orient the same segment from \(P^\star\) to \(p_1\). With
   \[
   d=p_1-P^\star,\quad u=C-P^\star,
   \]
   one has
   \[
   V=D_1d,\quad Q_2=D_1^2\|d\|^2=D_1^2L_2^2>0,\quad
   W_2=D_1(u\cdot d).
   \]
   Thus the selector conditions have the correct signs despite reversing the physical link orientation.

8. **Second-segment seams.** Under forward kinematics:
   \[
   W_2=0\implies H_{2,I}=Q_2H_{2,A},
   \]
   \[
   D_1W_2=Q_2\implies H_{2,I}=L_2^2H_{1,B}.
   \]
   Again, branch values agree in sign.

9. **Degenerate proxy trap.** Take \(L_1=1,t_1=0\), \(P^\star=(1,0)=p_1\), and \(C=P^\star\). Then
   \[
   V=0,\quad Q_2=W_2=H_{2,I}=0,
   \]
   so the third branch of \(\Phi_2\) passes even though the degenerate proxy segment has distance \(0<R\). This is not a counterexample to RC-002: since \(L_2>0\), the actual \(p_2\) cannot equal \(p_1=P^\star\), so \(F_x=F_y=0\) is false and both full conjunctions fail. It proves that \(\Phi_2\) must not be asserted equivalent in isolation.

10. **Quantifiers and box boundaries.** The box is closed and all its endpoints are finite. A pointwise equivalence over all \(\mathbf R^2\) restricts directly to the box; no quantifier reversal or witness substitution occurs.

## Obligation ledger

- **O1 — Positivity consequences.** Prove \(R>0\), \(D_i>0\), \(D_1D_2>0\), \(L_i^2>0\), and that \(\mathcal B\) is a nonempty closed box.  
  Dependencies: none.

- **O2 — Half-angle identities.** Prove from \(q_i=2\arctan t_i\) that
  \[
  \cos q_i=C_i/D_i,\qquad \sin q_i=S_i/D_i,
  \]
  including all finite real \(t_i\).  
  Dependencies: O1.

- **O3 — Forward-kinematics equivalence.** Expand the angle-addition identities and prove
  \[
  F_x=D_1D_2(x-p_{2,x}),\qquad
  F_y=D_1D_2(y-p_{2,y}),
  \]
  hence
  \[
  F_x=F_y=0\iff p_2=P^\star.
  \]
  Dependencies: O1, O2.

- **O4 — Jacobian determinant.** Differentiate \(p_2\) with respect to \(q_1,q_2\) and prove
  \[
  \det J(q)=L_1L_2\sin q_2.
  \]
  Dependencies: none beyond the kinematic definitions.

- **O5 — Singularity polynomial equivalence.** Prove
  \[
  G=D_2^2\bigl((\det J)^2-\varepsilon^2\bigr)
  \]
  and then
  \[
  G\ge0\iff|\det J|\ge\varepsilon.
  \]
  Explicitly justify the positive denominator and the squaring step.  
  Dependencies: O1, O2, O4.

- **O6 — Point-to-segment lemma.** For \(d=B-A\ne0\), \(u=C-A\), \(s=u\cdot d\), and \(m=d\cdot d>0\), derive from the definition of distance:
  \[
  \operatorname{dist}(C,[A,B])^2=
  \begin{cases}
  \|u\|^2,&s\le0,\\
  \|u-d\|^2,&s\ge m,\\
  \|u\|^2-s^2/m,&0\le s\le m.
  \end{cases}
  \]
  Prove coverage and agreement at \(s=0,m\).  
  Dependencies: none.

- **O7 — First-segment scaling identities.** With \(A=p_0\), \(B=p_1\), prove
  \[
  W_1=D_1(C\cdot p_1),
  \]
  \[
  (E_x,E_y)=D_1(C-p_1),
  \]
  \[
  H_{1,B}=D_1^2(\|C-p_1\|^2-R^2),
  \]
  and
  \[
  H_{1,I}=D_1^2\!\left[L_1^2(\|C\|^2-R^2)-(C\cdot p_1)^2\right].
  \]
  Dependencies: O1, O2.

- **O8 — First-segment selectors.** Prove the exact equivalences between
  \[
  C\cdot p_1\le0,\quad C\cdot p_1\ge L_1^2,\quad
  0\le C\cdot p_1\le L_1^2
  \]
  and the three selector conditions in \(\Phi_1\), including both seams.  
  Dependencies: O1, O7.

- **O9 — First-clearance equivalence.** Prove
  \[
  \Phi_1(t_1)\iff\operatorname{dist}(C,[p_0,p_1])\ge R.
  \]
  Justify replacing distance comparisons by squared comparisons using \(R>0\).  
  Dependencies: O1, O6, O7, O8.

- **O10 — Second-segment identities under the FK gate.** Assuming \(F_x=F_y=0\), set
  \[
  d=p_1-P^\star,\qquad u=C-P^\star.
  \]
  Prove
  \[
  P^\star=p_2,\quad \|d\|^2=L_2^2>0,
  \]
  \[
  V=D_1d,\quad Q_2=D_1^2L_2^2>0,\quad W_2=D_1(u\cdot d),
  \]
  and derive the endpoint/interior identities represented by \(H_{2,A}\), \(H_{1,B}\), and \(H_{2,I}\).  
  Dependencies: O1, O2, O3, O7.

- **O11 — Second-segment selectors.** Under the assumptions of O10, prove that the three selector regions in \(\Phi_2\) correspond exactly to
  \[
  u\cdot d\le0,\quad u\cdot d\ge\|d\|^2,\quad
  0\le u\cdot d\le\|d\|^2,
  \]
  and verify both seams.  
  Dependencies: O1, O10.

- **O12 — Conditional second-clearance equivalence.** Prove only the guarded statement
  \[
  (F_x=F_y=0)\Longrightarrow
  \left[
  \Phi_2(t_1)\iff
  \operatorname{dist}(C,[p_1,p_2])\ge R
  \right].
  \]
  Do not claim a standalone equivalence for \(\Phi_2\).  
  Dependencies: O3, O6, O10, O11.

- **O13 — Pointwise forward implication.** From \(\Phi(t)\), derive all four conjuncts of \(\Psi(t)\).  
  Dependencies: O3, O5, O9, O12.

- **O14 — Pointwise reverse implication.** From \(\Psi(t)\), derive every conjunct of \(\Phi(t)\), using \(p_2=P^\star\) to activate O12.  
  Dependencies: O3, O5, O9, O12.

- **O15 — Universal pointwise theorem.** Generalize O13 and O14 to every finite \(t\in\mathbf R^2\) and every admissible fixed instance.  
  Dependencies: O13, O14.

- **O16 — Existential corollary.** Prove each direction by taking the same bounded witness supplied on the other side:
  \[
  \exists t\in\mathcal B:\Phi(t)
  \iff
  \exists t\in\mathcal B:\Psi(t).
  \]
  Dependencies: O15.

- **O17 — Rational-polynomial syntax.** Audit every named left-hand expression and prove it lies in \(\mathbf Q[t_1,t_2]\). Verify that every atom of \(\Phi\) is an equality or weak inequality and that
  \[
  t\in\mathcal B
  \iff
  t_1-a_1\ge0,\ b_1-t_1\ge0,\ 
  t_2-a_2\ge0,\ b_2-t_2\ge0.
  \]
  State explicitly that \(\Phi_1,\Phi_2,\Phi\) are Boolean combinations of polynomial atoms, while the geometric predicates obtain polynomial representations through O3, O5, O9, and O12.  
  Dependencies: O1 and direct syntactic expansion; semantic correspondence additionally depends on O3, O5, O9, O12.

## Dependency graph

```text
O1 ──> O2 ──> O3 ───────────────> O10 ──> O11 ──> O12
 │       │                         ▲                 │
 │       └──> O7 ──> O8 ──> O9 ──┘                 │
 │               ▲          ▲                       │
 ├───────────────┘          O6 ─────────────────────┘
 │
 └──> O5 <── O4
       ▲
       O2

O3, O5, O9, O12 ──> O13
O3, O5, O9, O12 ──> O14
O13, O14 ──> O15 ──> O16

O1 ──> O17
O3, O5, O9, O12 ──> semantic portion of O17
```

## Separate implementation-correspondence evidence obligation

**Status: NOT EVALUATED; code/test artifacts are required.**

- **IC1.** Exact evidence that the builder emits the stated coefficients, shared predicates such as \(H_{1,B}\), and the exact conjunction/disjunction tree.
- **IC2.** Exact evidence that the serialized quantifier is `EXISTS (t1,t2)` and that all four closed-box bounds are enforced.
- **IC3.** Deterministic evidence that the registered checker evaluates coefficients, predicates, and formulas using exact rational arithmetic.
- **IC4.** Negative tests proving fail-closed rejection of unsupported quantifier prefixes, malformed witnesses, and witnesses outside \(\mathcal B\).

IC1–IC4 are independent of O1–O17. Satisfying either branch does not satisfy the other.

## Difficulty forecast

- **F1 — Half-angle denominator discipline.** Likely error: clear denominators without proving \(D_i>0\), or silently extend a finite chart result to the whole torus.

- **F2 — Singularity squaring.** Likely error: infer the determinant bound from a squared or numerical residual without deriving the exact identity and checking sign conditions.

- **F3 — Point-to-segment branch logic.** Likely error: use distance to the supporting line for all projections, omit an endpoint regime, or mishandle equality at a selector seam.

- **F4 — Second-segment FK gate.** Likely error: treat \(\Phi_2\) as a standalone segment-distance encoding, divide by \(Q_2\) before proving \(Q_2>0\), or overlook the exact degenerate-proxy example.

- **F5 — Claim-layer separation.** Likely error: conflate the pointwise theorem with its existential corollary, call the geometric syntax itself polynomial, extend beyond the stated chart/scope, or treat a mathematical proof as implementation-correspondence evidence.
