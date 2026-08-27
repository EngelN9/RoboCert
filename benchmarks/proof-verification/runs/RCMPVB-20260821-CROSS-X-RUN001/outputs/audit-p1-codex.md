# AUDIT REPORT — P1

## 1. Verdict

**V2 — Core mathematical equivalence is correct, but the submission is incomplete against several explicit ledger obligations.**

**Confidence:** 0.97

No fatal mathematical error was found in the pointwise equivalence. In particular, the proof correctly makes the second-segment argument conditional on the forward-kinematics equations and establishes \(Q_2>0\) before dividing by it.

The principal incompleteness is that the required bounded existential equivalence is never actually stated or proved with an existential quantifier. Step 10 proves only another pointwise equivalence after adjoining the box predicate.

**Most likely error if the proof is nevertheless wrong:** an unnoticed leakage of the conditional \(\Phi_2\) equivalence outside the forward-kinematics locus, where \(Q_2=0\) can make \(\Phi_2\) pass vacuously. No such leakage was found in the submitted final implication.

---

## 2. Reconstructed dependency graph

```text
Chart identities and positive denominators [CHART, DIV, INV]
    |
    +--> Rationalized p1,p2 [SYM, E]
    |        |
    |        +--> FK equivalence [E, DIV]
    |                 |
    |                 +--> p2=P* and Q2=D1^2 L2^2>0 [REG, DIV, CIRC]
    |                          |
    |                          +--> Conditional segment-2 branches [CASE, DIV, INV]
    |                                   |
    |                                   +--> Conditional Phi2 equivalence [L->G, E]
    |
Point-to-segment minimization [CASE, DIV, REG, E]
    |
    +--> Segment-1 selectors and clearings [CASE, DIV, INV]
    |        |
    |        +--> Phi1 equivalence [L->G, E]
    |
    +--> Conditional segment-2 equivalence as above

Jacobian computation [SYM]
    |
    +--> Absolute-value clearing and G equivalence [E, INV]

FK + Phi1 + conditional Phi2 + G
    |
    +--> Pointwise conjunction equivalence [L->G, E]
             |
             +--> Box-conjoined pointwise equivalence [Q, E]
                      |
                      +--> Required existential transport — omitted [Q, L->G]

Rational input hypotheses
    |
    +--> Rational-polynomial coefficient claim [SYM, GEN]
```

Step 6, proving that \(Q_2(t_1)\) is nonconstant, is a side branch tagged `[SYM, GEN]`. It is correct but unused: nonconstancy neither implies pointwise positivity nor contributes to the final theorem. Positivity comes solely from the FK gate in Step 7.

---

## 3. Audit of risky steps

### `[CHART, DIV, INV]` Half-angle chart

For finite \(t\), the proof correctly establishes \(D=1+t^2>0\), the sine and cosine identities, and the range \(2\arctan t\in(-\pi,\pi)\). All denominator clearings used later are therefore sign-safe.

It does not explicitly prove that \(t\mapsto2\arctan t\) is a bijection onto \((-\,\pi,\pi)\). It also proves \(C_1^2+S_1^2=D_1^2\) later but never explicitly states the corresponding \(i=2\) identity. These omissions do not damage the pointwise theorem.

The finite-chart boundary \(q_i=\pm\pi\) is correctly excluded. No torus-completeness inference is made.

### `[SYM, E, DIV]` Forward kinematics

The angle-addition substitutions are correct. Direct expansion gives

\[
F_x=D_1D_2\bigl(x-(p_2)_x\bigr),\qquad
F_y=D_1D_2\bigl(y-(p_2)_y\bigr).
\]

Because \(D_1D_2>0\), the claimed FK equivalence is valid in both directions.

### `[SYM, E, INV]` Jacobian and singularity polynomial

The displayed Jacobian is \(\partial p_2/\partial q\), not \(\partial p_2/\partial t\). Its determinant is correctly reduced to

\[
\det J=L_1L_2\sin q_2
      =\frac{2L_1L_2t_2}{D_2}.
\]

The absolute-value inequality is squared only after both sides have been shown nonnegative. Expansion produces exactly \(G\ge0\). Equality at \(|\det J|=\varepsilon\) is retained.

At \(t_2=0\), \(G=-\varepsilon^2<0\), matching the rank-deficient Jacobian. If \(\varepsilon=|L_1L_2|\), the polynomial reduces to a nonpositive square and accepts precisely \(t_2=\pm1\), as expected.

The candidate omits the frozen hypothesis \(\varepsilon\le |L_1L_2|\) and consequently does not state its non-vacuity-only role. The stronger equivalence for larger \(\varepsilon\) is nevertheless valid.

### `[CASE, DIV, REG, E]` Point-to-segment lemma

For \(A\ne B\), the minimization over \(u\in[0,1]\) is correctly derived. The three weak selector ranges cover all real projection parameters and overlap at \(s=0,1\). The proof explicitly verifies agreement of the adjacent formulas at both seams.

The degenerate case \(A=B\) is not stated separately, despite O4 requiring it. Both physical links are later proved nondegenerate under the theorem hypotheses, so this omission does not invalidate their use of the lemma.

### `[CASE, DIV, INV, L->G]` First segment

The identities

\[
C\cdot p_1=W_1/D_1,\qquad \|p_1\|^2=L_1^2,
\qquad D_1(C-p_1)=(E_x,E_y)
\]

are correct. Every selector and clearance inequality is multiplied only by a strictly positive factor.

The weak guards cover and overlap correctly. Both logical directions follow: any satisfied branch identifies a valid geometric case, and every geometric case supplies a branch.

### `[REG, DIV, CIRC]` Conditional \(Q_2>0\)

Under \(F_x=F_y=0\), the proof first obtains \(p_2=P^\star\), then uses the physical second-link length to derive

\[
Q_2=D_1^2\|p_1-P^\star\|^2
   =D_1^2L_2^2>0.
\]

This ordering is correct and non-circular. No division by \(Q_2\) occurs before this result.

The proof says behavior away from the FK locus is irrelevant, but it does not explicitly demonstrate that unconditional \(\Phi_2\)-clearance equivalence is false.

The mandatory off-FK attack confirms the danger: if \(Q_2=0\), then \(V_x=V_y=W_2=H_{2,I}=0\), so the third branch of \(\Phi_2\) is automatically true. Thus \(\Phi_2\) cannot encode actual second-link clearance unconditionally. The submitted final proof avoids this error by retaining the FK conjunct.

### `[CASE, DIV, INV]` Second-segment branches

With \(A=P^\star=p_2\) and \(B=p_1\), the projection parameter is correctly computed as

\[
s=\frac{W_2D_1}{Q_2}.
\]

The selector clearings are valid because \(D_1,Q_2>0\).

The endpoint \(s\ge1\) is \(B=p_1\), and reuse of \(H_{1,B}\) is correct because

\[
D_1(C-p_1)=(E_x,E_y).
\]

The interior-distance calculation correctly cancels the \(D_1^2\) factors and yields \(H_{2,I}\ge0\). Seam behavior is inherited from the checked general lemma.

### `[L->G, E]` Final pointwise implication

Both directions establish FK first. Consequently, every use of the conditional second-segment equivalence is within its valid domain. No conjunct is compared independently of the FK gate, and no weak inequality is silently strengthened.

The pointwise theorem is established.

### `[Q, L->G]` Bounded witness statement

Step 10 proves

\[
\mathcal D(t)\wedge P(t)\iff \mathcal D(t)\wedge Q(t)
\]

pointwise. It does not write or justify

\[
\exists t\,(\mathcal D(t)\wedge P(t))
\iff
\exists t\,(\mathcal D(t)\wedge Q(t)).
\]

Thus the exact theorem requested as RC-002-exists is absent, even though the preceding pointwise result makes the missing transport immediate.

### `[SYM, GEN]` Polynomial syntax

The definitions visibly consist of polynomial atoms over rational coefficients when the fixed data are rational. However, the proof does not enumerate all distinct atoms, explicitly normalize the four box predicates as polynomial weak inequalities, or enumerate the full conjunction/disjunction tree as O19 requires.

---

## 4. Hypothesis consumption and deletion tests

| Hypothesis | Consumption point | Deletion test |
|---|---|---|
| \(L_1>0\) | Steps 5 and 7: first-link nondegeneracy and positivity of \(D_1^2L_1^2\). | Nonzero \(L_1\) would suffice. If \(L_1=0\), the interior branch of \(\Phi_1\) has zero guards and \(H_{1,I}=0\), so it can pass regardless of actual point clearance. Essential against zero degeneracy. |
| \(L_2>0\) | Step 7: \(Q_2=D_1^2L_2^2>0\), enabling the segment-2 lemma and divisions. | Nonzero \(L_2\) would suffice. If \(L_2=0\), \(Q_2=0\) on FK and \(\Phi_2\) can pass vacuously. Essential against zero degeneracy. |
| \(r>0\), \(\mu>0\) | Used only through \(R=r+\mu>0\) in distance squaring. | The proof actually permits \(r=0\). Individual positivity is stronger than necessary; a nonnegative \(R\) suffices. Removing all control of \(R\) permits \(R<0\), for which \(d\ge R\) is not equivalent to \(d^2\ge R^2\). |
| \(\varepsilon>0\) | Step 3: ensures the determinant-bound right side is nonnegative. | \(\varepsilon=0\) would still preserve the equivalence. Allowing negative \(\varepsilon\) can break it because the geometric inequality becomes automatic while \(G\) still depends on \(\varepsilon^2\). |
| \(\varepsilon\le|L_1L_2|\) | Not consumed by the candidate. | Deletion has no effect on pointwise equivalence. It only permits the determinant-margin predicate to become globally unsatisfiable. The candidate validly proves more but fails to record this frozen hypothesis’s role. |
| Rationality of fixed data | Step 11 and the bounded-domain discussion. | Deletion leaves the real pointwise equivalence valid but removes the conclusion that all atoms lie in \(\mathbf Q[t_1,t_2]\). |
| \(a_i<b_i\) | Mentioned in Step 10 but not used in logical transport. | Deletion does not affect equivalence under the same domain predicate; it only affects whether the conventional box is nonempty. |
| Finite \(a_i,b_i,t_i\) | Step 1 and domain discussion. | Essential to the chosen chart and ordinary polynomial evaluation. Infinite half-angle endpoints are not represented. |

The proof proves valid stronger statements for \(r=0\), arbitrary real coefficients at the geometric level, and \(\varepsilon>|L_1L_2|\). It does not prove torus completeness, robust feasibility, path feasibility, or infeasibility from witness failure.

---

## 5. Boundary and degeneracy attacks

- **Zero denominators:** Impossible for finite \(t_i\), since \(D_i\ge1\).
- **Signed denominator clearing:** All used factors are positive; no inequality reversal was missed.
- **Absolute-value squaring:** Correct because both \(|2L_1L_2t_2|\) and \(\varepsilon D_2\) are nonnegative.
- **Distance squaring:** Correct under \(R>0\).
- **Projection seams \(s=0,1\):** Weak guards overlap, cover both seams, and the distance formulas agree.
- **Obstacle at an endpoint:** The relevant endpoint and interior branches both reject zero clearance when \(R>0\).
- **Rank deficiency:** \(t_2=0\) is rejected because \(G=-\varepsilon^2\).
- **Chart seam:** \(q_i=\pm\pi\) is outside finite \(t_i\); the proof makes no completeness claim there.
- **First-link degeneration:** Excluded by \(L_1>0\); the formula would not remain sound at \(L_1=0\).
- **Second-link degeneration:** Excluded by \(L_2>0\); \(Q_2>0\) is proved only after FK.
- **Off-FK \(Q_2=0\):** \(\Phi_2\) may pass vacuously. The complete conjunction remains sound because FK is established first in both directions.
- **Second-segment endpoint substitution:** Reuse of \(H_{1,B}\) is exact because the relevant endpoint is the same physical elbow \(p_1\).
- **Box boundary:** All four intended bounds are weak, but the proof never explicitly transports the pointwise result under `EXISTS`.

---

## 6. Union obligation ledger

| Obligation | Status | Audit basis |
|---|---|---|
| O1 — Chart identities and range | **PARTIALLY DISCHARGED** | Positivity, trigonometric identities, and image containment are proved. Full bijectivity and the \(i=2\) norm identity are not explicitly proved. |
| O2 — Positivity register | **DISCHARGED** | Signs of all factors actually used in clearings, including conditional \(Q_2\), are established before use. |
| O3 — Nonnegative squaring | **DISCHARGED** | The monotonicity equivalence is stated and applied separately to determinant and distance bounds. |
| O4 — Point-to-segment lemma | **PARTIALLY DISCHARGED** | Minimization, coverage, and seam agreement are proved; the degenerate-segment case is omitted. |
| O5 — Rationalized kinematics | **DISCHARGED** | Half-angle and angle-addition formulas produce the displayed rational \(p_1,p_2\). |
| O6 — FK equivalence | **DISCHARGED** | The numerator identities and positive common denominator establish both directions. |
| O7 — Physical link lengths | **DISCHARGED** | Both links are shown to have positive squared lengths \(L_1^2,L_2^2\). |
| O8 — Jacobian determinant | **DISCHARGED** | All Jacobian entries are displayed and \(\det J=L_1L_2\sin q_2\) is derived. |
| O9 — Singularity clearing | **PARTIALLY DISCHARGED** | The equivalence and expansion are correct, but the upper-margin hypothesis’s non-vacuity-only role is not stated. |
| O10 — First-segment scaling | **DISCHARGED** | All selector and distance numerators are derived using positive factors. |
| O11 — First-segment assembly | **DISCHARGED** | Coverage, overlap, seams, and both logical directions are supported by the case lemma. |
| O12 — Second-segment proxy identities | **PARTIALLY DISCHARGED** | The identities are computed only inside the FK-gated discussion, although they are algebraically unconditional. |
| O13 — Conditional nondegeneracy | **DISCHARGED** | FK is used first to obtain \(p_2=P^\star\), then \(Q_2=D_1^2L_2^2>0\). |
| O14 — Second-segment branches | **DISCHARGED** | Selectors, endpoint substitution, interior inequality, and all positive divisions are checked under FK. |
| O15 — Second-segment assembly | **PARTIALLY DISCHARGED** | Conditional equivalence, coverage, and seams are proved, but the unconditional lemma is not explicitly stated to be false. |
| O16 — Pointwise forward direction | **DISCHARGED** | FK is established before conditional second clearance. |
| O17 — Pointwise reverse direction | **DISCHARGED** | FK is derived first and all weak predicates are preserved. |
| O18 — Bounded existential corollary | **PARTIALLY DISCHARGED** | Only a box-conjoined pointwise equivalence is written; the existential quantifier is omitted. |
| O19 — Rational-polynomial syntax | **PARTIALLY DISCHARGED** | Rational polynomiality is argued generally, but distinct atoms, the Boolean tree, and normalized box atoms are not enumerated. |
| O20 — Hypothesis and scope audit | **PARTIALLY DISCHARGED** | Some chart and implementation limitations are noted, but exact consumption/deletion tests and all exclusions are not supplied. |

---

## 7. Difficulty-forecast audit

| Forecast point | Status | Finding |
|---|---|---|
| F1 — Conditional \(\Phi_2\) | **DISCHARGED** | The proof consistently states and uses only the FK-conditional equivalence. |
| F2 — \(Q_2=0\) | **DISCHARGED** | No division occurs before \(Q_2=D_1^2L_2^2>0\) is established under FK. |
| F3 — Coordinate and sign discipline | **DISCHARGED** | \(J\) is differentiated with respect to \(q\); squaring and clearings use verified nonnegative or positive factors. |
| F4 — Selector coverage | **DISCHARGED** | Weak selectors cover all cases and agree at both seams. |
| F5 — Scope and hypothesis drift | **PARTIALLY DISCHARGED** | No torus or infeasibility overclaim occurs, but the upper-margin hypothesis is omitted and the required existential statement is not emitted. |

---

## 8. Separate implementation-correspondence obligations

| Obligation | Status | Finding |
|---|---|---|
| IC1 — Builder coefficients and Boolean tree | **NOT DISCHARGED** | No implementation artifact or deterministic correspondence evidence is present. |
| IC2 — Existential prefix and closed box handling | **NOT DISCHARGED** | No implementation evidence is present; even the mathematical existential statement is omitted. |
| IC3 — Exact-rational registered-checker evaluation | **NOT DISCHARGED** | No checker or test evidence is present. |
| IC4 — Fail-closed malformed/unsupported witness handling | **NOT DISCHARGED** | No implementation or rejection evidence is present. |

These statuses do not count against the mathematical pointwise equivalence, but the overall run cannot treat the proof as implementation-correspondence evidence.

---

## 9. Defects

1. **Substantive — Required bounded existential theorem not emitted.**  
   Step 10 establishes only a pointwise equivalence with \(\mathcal D\) conjoined. RC-002-exists contains an explicit existential quantifier, which never appears in the proof’s conclusion.

2. **Substantive — Frozen hypothesis and scope audit incomplete.**  
   The candidate omits \(\varepsilon\le|L_1L_2|\), changes \(r>0\) to \(r\ge0\), and does not provide exact consumption/deletion tests. These changes are mathematically safe strengthenings, but O20 is not fulfilled.

3. **Minor — Full chart bijection not proved.**  
   Range containment and the inverse identity for generated \(q\) are shown, but surjectivity and injectivity onto \((-\,\pi,\pi)\) are not explicitly established.

4. **Minor — Degenerate point-to-segment case omitted.**  
   The generic lemma treats only \(A\ne B\). Physical nondegeneracy later protects the theorem.

5. **Minor — Unconditional proxy obligation incompletely presented.**  
   The \(V,Q_2,W_2\) identities are written inside an FK-gated section rather than proved explicitly without FK.

6. **Minor — Off-FK failure of \(\Phi_2\) not explicitly stated.**  
   The proof correctly avoids relying on unconditional equivalence but does not record the \(Q_2=0\) vacuity demanded by O15.

7. **Minor — Polynomial syntax audit incomplete.**  
   The distinct atoms, exact Boolean tree, constant atoms, and normalized four box inequalities are not enumerated.

8. **Expository — Irrelevant nonconstancy argument.**  
   Step 6 proves \(Q_2\) is nonconstant, but this contributes nothing to the required positivity or equivalence and risks obscuring the fact that a nonconstant sum-of-squares polynomial may still vanish.

---

## 10. Untagged material passed over

The following material was treated as expository rather than as an additional proof dependency:

- repeated theorem and definition restatements;
- the undefined internal labels “S1” through “S5”;
- the implementation/specification disclaimers;
- the closing summary and \(\square\);
- prose claims that repeat equivalences already audited above.

No untagged mathematical step was used to cure the missing existential quantification or any implementation-correspondence obligation.
