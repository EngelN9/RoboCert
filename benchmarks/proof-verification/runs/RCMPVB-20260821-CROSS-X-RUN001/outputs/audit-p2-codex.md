AUDIT REPORT — P2

SCOPE

The observable submission establishes a largely sound pointwise equivalence for its own predicate through Theorem 10.2. It does not establish the required bounded-witness equivalence, does not establish the rational-polynomial syntax obligation, and silently redefines both forward-kinematics polynomials as the negatives of the frozen polynomials. The observable proof ends at §10.3 despite references to §§12–14.

DEPENDENCY GRAPH AND RISK TAGS

```text
Lemma 2.5 + Proposition 3.1
  [CHART, INV, DIV]
        |
        +--> Proposition 4.3: rationalized FK
        |      [E, DIV, SYM]
        |
        +--> Lemma 5.1 --> Proposition 5.3: determinant margin
        |      [DIV, INV, CASE]
        |
        +--> Lemma 7.3: numerator/scaling identities
               [DIV, SYM]
                    |
Lemma 2.3             |       Lemma 6.1
[INV, CASE]           |       [CASE, DIV, GEN]
       \               |              /
        \              v             /
         +------> Proposition 7.8
                    [CASE, DIV, INV, L->G]
                       /              \
                      v                v
             Proposition 8.2     Lemmas 9.2–9.3
             first segment       conditional Q2>0
             [CASE, DIV]         [GEN, DIV, CIRC]
                                      |
                                      v
                               Proposition 9.4
                               second segment
                               [CASE, DIV, CIRC]
                       \              /
                        v            v
                         Theorem 10.2
                         [L->G, CIRC]
                              |
                 missing frozen-F sign bridge
                         [SYM, NOT]
                              |
                 missing bounded corollary
                         [Q, L->G]
                              |
                 missing Q-polynomial audit
                         [SYM, REG]
```

TAGGED-STEP AUDIT

1. Half-angle chart `[CHART, INV, DIV]`: DISCHARGED. Lemma 2.5 proves the bijection, inverse, range, and trigonometric identities; Proposition 3.1 proves every denominator is positive. The identity \((1-t^2)^2+(2t)^2=(1+t^2)^2\) is explicitly computed in Lemma 7.3.

2. Denominator and sign discipline `[DIV]`: DISCHARGED for the pointwise argument. All divisions by \(D_i\) use \(D_i>0\); division by the second-segment squared length occurs only after conditional positivity is established.

3. Forward-kinematics identification `[E, DIV, SYM]`: PARTIALLY DISCHARGED. Proposition 4.3 correctly proves the zero-set equivalence for the candidate’s polynomials. However,
   \[
   F_x^{\mathrm{candidate}}=-F_x^{\mathrm{frozen}},\qquad
   F_y^{\mathrm{candidate}}=-F_y^{\mathrm{frozen}},
   \]
   and the proof never states or consumes these identities. It therefore does not prove the exact frozen identities required by O6, although the zero loci coincide.

4. Absolute-value squaring `[INV, CASE]`: DISCHARGED. Lemma 2.3 proves the equivalence for a nonnegative threshold and is separately applied to the determinant and distance bounds.

5. Point-to-segment split `[CASE, DIV, GEN]`: PARTIALLY DISCHARGED. Lemma 6.1 proves both directions, selector coverage, and seam agreement for a nondegenerate segment. It does not separately state the requested general degenerate-segment case. The application-specific second-segment degeneracy is nevertheless analyzed correctly in Lemmas 9.2 and 9.4.

6. First-segment encoding `[CASE, DIV, L->G]`: DISCHARGED. The scaling identities, all three selectors, both implications, weak seams, and endpoint/interior distance expressions agree with the frozen \(\Phi_1\).

7. Second-segment proxy `[GEN, DIV]`: DISCHARGED. The candidate’s \(\mathbf h,\Sigma^{(2)},\Pi^{(2)}\) are respectively the frozen \(V,Q_2,W_2\), and the identities are proved unconditionally.

8. Conditional second-segment nondegeneracy `[GEN, DIV, CIRC]`: DISCHARGED. The proof first obtains FK, then derives
   \[
   \Sigma^{(2)}=D_1^2L_2^2>0.
   \]
   It explicitly shows that the proxy predicate is vacuously true when \(\Sigma^{(2)}=0\) and rejects unconditional use.

9. Second endpoint and interior substitution `[CASE, DIV, CIRC]`: DISCHARGED under the FK gate. Proposition 9.4 justifies replacing \(p_2\) by \(P^\star\), reuses the elbow expression corresponding to \(H_{1,B}\), and performs all multiplication or division by \(Q_2\) only after positivity is known.

10. Pointwise final implication `[L->G, CIRC]`: PARTIALLY DISCHARGED relative to the frozen theorem. The staging in Theorem 10.2 is noncircular and proves the geometric equivalence for the candidate’s predicate. The unstated sign bridge between the candidate and frozen \(F_x,F_y\) leaves the exact frozen implication formally incomplete.

11. Bounded existential transport `[Q, L->G]`: NOT DISCHARGED. The parameters \(a_i,b_i\), the box \(\mathcal B\), its four bounds, and the existential corollary do not appear in the observable proof.

12. Rational-polynomial syntax `[SYM, REG]`: PARTIALLY DISCHARGED. The formulas are displayed as polynomial atoms and Boolean combinations over real coefficients. Rationality, the full frozen atom list, the Boolean tree, constant atoms, and the four rational box bounds are not established.

UNION OBLIGATION LEDGER

- O1 — Chart identities and range: DISCHARGED.
- O2 — Positivity register: DISCHARGED.
- O3 — Nonnegative squaring: DISCHARGED.
- O4 — Point-to-segment lemma: PARTIALLY DISCHARGED. The nondegenerate case is complete; the requested separate general degenerate case is absent.
- O5 — Rationalized kinematics: DISCHARGED.
- O6 — FK equivalence: PARTIALLY DISCHARGED. The zero-set equivalence is proved for sign-reversed definitions, but the exact frozen identities are not.
- O7 — Physical link lengths: DISCHARGED under the frozen positivity hypotheses.
- O8 — Jacobian determinant: DISCHARGED.
- O9 — Singularity clearing: DISCHARGED.
- O10 — First-segment scaling: DISCHARGED.
- O11 — First-segment assembly: DISCHARGED.
- O12 — Second-segment proxy identities: DISCHARGED.
- O13 — Conditional nondegeneracy: DISCHARGED.
- O14 — Second-segment branches: DISCHARGED.
- O15 — Second-segment assembly: DISCHARGED.
- O16 — Pointwise forward direction: PARTIALLY DISCHARGED because it starts from the candidate’s redefined \(\Phi\), not explicitly the frozen \(\Phi\).
- O17 — Pointwise reverse direction: PARTIALLY DISCHARGED for the same exact-formula mismatch.
- O18 — Bounded existential corollary: NOT DISCHARGED.
- O19 — Rational-polynomial syntax: PARTIALLY DISCHARGED.
- O20 — Hypothesis and scope audit: PARTIALLY DISCHARGED. Several hypothesis strengths and chart limits are discussed, but rationality, \(a_i<b_i\), bounded transport, and all frozen exclusions are not audited. References to absent theorems claiming to “repair” chart loss go beyond the frozen scope.

DIFFICULTY FORECAST AUDIT

- F1 — Conditional \(\Phi_2\): DISCHARGED. The proof expressly denies unconditional second-link equivalence.
- F2 — \(Q_2=0\): DISCHARGED. No division occurs before FK implies \(Q_2>0\); the off-FK vacuous branch is explicitly computed.
- F3 — Coordinate and sign discipline: PARTIALLY DISCHARGED. \(J=\partial p_2/\partial q\), denominator signs, and squaring are correct. The frozen FK polynomials are nevertheless redefined with opposite signs without an explicit correspondence step.
- F4 — Selector coverage: DISCHARGED. The selectors are correctly described as overlapping, both seams are checked, and both directions are proved.
- F5 — Scope and hypothesis drift: PARTIALLY DISCHARGED. The finite-chart limitation is recognized and no witness-failure-to-infeasibility inference is made. The bounded box is omitted, and unsupported references to absent torus-repair results exceed the assigned theorem.

HYPOTHESIS CONSUMPTION AND DELETION TESTS

- \(L_1>0\): Consumed as \(L_1^2>0\) in Corollary 3.2 and Proposition 8.2 to make the first physical segment nondegenerate. If removed entirely, \(L_1=0\) makes the third branch of the frozen \(\Phi_1\) pass vacuously, so clearance equivalence can fail. The proof validly shows that the sign \(L_1>0\) can be weakened to \(L_1\ne0\).

- \(L_2>0\): Consumed in Lemmas 9.2–9.3 to infer \(Q_2=D_1^2L_2^2>0\) after FK. If removed, \(L_2=0\) permits \(p_1=p_2=P^\star\), while the degenerate proxy can pass without proving second-segment clearance. The sign can validly be weakened to \(L_2\ne0\).

- \(r>0\) and \(\mu>0\): Consumed only through \(R=r+\mu\ge0\), chiefly in Corollary 6.2. Removing either positivity hypothesis while allowing that parameter to become arbitrarily negative can make \(R<0\), in which case the geometric inequality is automatic but its squared encoding need not hold. Neither is separately needed if \(R\ge0\) is assumed directly.

- \(\varepsilon>0\): Consumed only as \(\varepsilon\ge0\) in Proposition 5.3. Deleting all sign control permits \(\varepsilon<0\), for which the geometric determinant inequality is automatic but \(G\ge0\) need not be. Weakening to \(\varepsilon\ge0\) is valid.

- \(\varepsilon\le|L_1L_2|\): Not consumed by the pointwise equivalence. Corollary 5.4 correctly identifies it as a non-vacuity condition. Deleting it leaves the equivalence valid but may leave both sides unsatisfiable.

- \(a_i<b_i\): Not consumed because the bounded theorem is absent. For transport of a pointwise equivalence under the same existential domain, nonemptiness is unnecessary; deleting these inequalities does not invalidate the logical transport.

- Rationality of all fixed data: Not consumed in the real pointwise proof. It is essential for the requested conclusion that the atoms and box bounds lie over \(\mathbf Q\). The candidate explicitly works over arbitrary real coefficients, so deletion preserves only a real-semialgebraic statement.

The proof therefore proves more than required in the valid directions \(L_i\ne0\), \(R\ge0\), and \(\varepsilon\ge0\), but proves less than required concerning the bounded rational instance and its syntactic encoding.

ZERO, BOUNDARY, SEAM, AND DEGENERACY ATTACKS

- \(t_i=0\): \(D_i=1\), so there is no denominator failure. At \(t_2=0\), \(G=-\varepsilon^2<0\) under the frozen hypotheses, matching \(\det J=0\).
- Chart boundary: No finite \(t_i\) represents \(q_i=\pi\); both sides of the pointwise theorem use the same finite chart. This is correctly recognized.
- \(R=0\): The candidate’s broader theorem remains valid because its squaring lemma handles equality at zero.
- \(\varepsilon=0\): The broader determinant equivalence remains valid and is explicitly separated.
- Determinant equality boundary: \(G=0\) exactly matches \(|\det J|=\varepsilon\); weak inequalities are preserved.
- First selector seam \(s^\star=0\): Endpoint-A and interior squared distances are proved equal.
- Second selector seam \(s^\star=1\): Endpoint-B and interior squared distances are proved equal.
- First-segment degeneracy: Excluded by \(L_1\ne0\).
- Proxy degeneracy \(Q_2=0\): The proof explicitly computes that \(\Psi^{(2)}\) then passes vacuously, but proves that FK and \(L_2\ne0\) make this case impossible.
- Undefined projection parameter: It is never used for the second segment before conditional nondegeneracy; the first segment is unconditionally nondegenerate.
- Second-segment endpoint substitution: It is invoked only after \(p_2=P^\star\) has been established.
- Reused \(H_{1,B}\): Correctly represents the squared distance from \(C\) to the shared elbow endpoint.
- Absolute-value squaring: Both operands are shown nonnegative at each application.
- Denominator signs: All \(D_i,D_i^2,D_1D_2\) are strictly positive; \(Q_2\) is strictly positive only under FK, exactly where required.
- Empty or reversed box: Not audited because no bounded statement is supplied.
- Malformed, unsupported, or out-of-domain witness: Not addressed by mathematical content.

UNTAGGED STEPS PASSED OVER

The periodicity lemma, monomial expansion, degree table, and numerical spot checks are not load-bearing for the frozen pointwise theorem. Their routine algebra appears consistent, but they do not discharge the missing bounded, rational-syntax, or implementation obligations. Claims referring to absent Theorems 12.1 and 13.5 cannot be audited from the observable submission.

IMPLEMENTATION-CORRESPONDENCE OBLIGATIONS

- IC1 — Builder coefficients and Boolean tree: NOT DISCHARGED. No deterministic implementation evidence is supplied, and the candidate’s FK coefficients have the opposite sign from the frozen definitions.
- IC2 — Existential prefix and four closed bounds: NOT DISCHARGED.
- IC3 — Exact-rational evaluation and seam controls: NOT DISCHARGED.
- IC4 — Fail-closed malformed/unsupported/out-of-domain handling: NOT DISCHARGED.

DEFECTS

1. Substantive — The required bounded-witness equivalence is entirely absent.
2. Substantive — The rational-coefficient and complete atom/Boolean-tree assertion is not proved; the proof instead fixes arbitrary real data.
3. Substantive — The submitted predicate silently uses \(F_x,F_y\) equal to the negatives of the frozen polynomials. Equality-zero semantics survive, but exact correspondence to the theorem as written is not established.
4. Minor — The general point-to-segment lemma omits the separately requested degenerate-segment case, although the relevant application-specific degeneracy is handled correctly.
5. Minor — The fixed box hypotheses \(a_i<b_i\) and their logical role are never discussed.
6. Expository — The submission refers to absent §§12–14 and makes uncheckable statements about later chart-loss repairs outside the frozen theorem’s scope.
7. Substantive run-level gap — None of IC1–IC4 has observable evidence. Mathematical proof agreement cannot discharge them.

VERDICT

V4 — The central pointwise geometric argument is substantially sound, including the load-bearing conditional treatment of \(\Phi_2\), but the submission is incomplete as a proof of the frozen task. Two required conclusions are missing, and the exact frozen FK predicate is not explicitly connected to the sign-reversed predicate actually proved.

Confidence: 0.98.

Most likely error if the proof is treated as complete: a scope/formula mismatch—accepting Theorem 10.2 for the candidate’s redefined pointwise predicate as though it also established the frozen rational predicate, its bounded existential corollary, and the separate implementation correspondence.
