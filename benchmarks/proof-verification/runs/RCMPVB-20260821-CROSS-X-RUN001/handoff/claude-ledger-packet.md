# Session L — theorem intake packet

Execution condition: fresh context, no tools, no repository access, and no prior proof or audit text. Return the complete observable response only.

## Frozen instructions

# RC-002 ledger prompt v2

You are a senior research mathematician acting as referee for a journal with a
high rejection rate. You will receive only the frozen theorem. You must not use
tools, inspect a repository, retrieve a proof, or rely on prior conversations.

1. Restate the theorem and formally parse every object, hypothesis, quantifier,
   equivalence, boundary case, and scope exclusion. Distinguish the pointwise
   theorem from its existential corollary and from the separate implementation
   correspondence obligation.
2. Attempt seriously to disprove the statement as written. Test the smallest
   and degenerate admissible cases, signs, denominator zeros, chart boundaries,
   selector seams, segment degeneracy, squaring conditions, and quantifier
   readings. Report `FOUND COUNTEREXAMPLE`, `NO COUNTEREXAMPLE FOUND`, or
   `STATEMENT AMBIGUOUS`, with exact details. Stop if ill-posed.
3. Derive from the theorem alone a numbered obligation ledger `O1`...`On`.
   Each obligation must be independently checkable, and dependencies must be
   explicit. Do not anticipate either candidate proof.
4. Pre-register three to five likely difficulty points `F1`...`Fk`, including
   the characteristic invalid shortcut at each point.
5. Emit a single self-contained block headed `LEDGER v1`. Include the formal
   parse, counterexample-search result, obligation ledger, dependency graph, and
   difficulty forecast. Then stop.

Do not evaluate implementation correspondence from prose. List it as a separate
evidence obligation requiring code/test artifacts.

## Frozen theorem

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
