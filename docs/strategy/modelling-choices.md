# First-target modelling choices

Date: 2026-09-26. This note records the proposed choices for O1–O6 in
[`first-target.md`](first-target.md) §3.7 and checks them against the current
RC-002 encoding. It is an E0 planning record. It changes no research evidence
tier, proves no instance, registers no checker, and does not make Claim (U) a
theorem.

## Claim being modelled

For the original link-length-only schema, the quantifier order of Claim (U) is

$$
\exists b\in\{+1,-1\}\;\forall L\in\Delta\;\forall x\in R\;\exists q\in Q_b:
f_L(q)=x\wedge\mathrm{Adm}_D(L,q;\varepsilon,\mu).
$$

With the O3 choice below, the proposed kill-test schema adds a universally
quantified second-joint zero offset. Let
$u=\tan(\beta_2/2)$ range over an approved rational interval $U_\beta$; let
$q$ denote the commanded joint coordinate; and let the physical planar joint
angles be $\theta=(q_1,q_2+\beta_2)$. The resulting proposed order is

$$
\exists b\in\{+1,-1\}\;\forall L\in\Delta\;\forall u\in U_\beta\;
\forall x\in R\;\exists q\in Q:
b\sin\theta_2>0\wedge f_L(\theta)=x\wedge
\mathrm{Adm}_D(L,\theta;\varepsilon,\mu).
$$

Here $Q$ constrains the commanded coordinates. The physical-angle composition
must be encoded from the separate half-angle variables for $q_2$ and $\beta_2$
using exact rational addition identities. It must not be evaluated with
floating-point trigonometry. The bounds of $U_\beta$ become part of the instance
data and must be sourced or explicitly marked as assumptions.

RC-002 instead fixes $L_1,L_2,x,y$ as rational coefficients and quantifies only
$\exists(t_1,t_2)$ over one rational box. Its exact-witness checker deliberately
rejects unsupported quantifier prefixes. Thus RC-002's pointwise algebra can be
reused, but its present claim and checker do not establish the formula above.

## Decisions and RC-002 correspondence

| ID | Decision | Current-state category | RC-002 correspondence and required change |
|---|---|---|---|
| O1 | Adopt (U): one physical elbow branch for all $L$, offsets and targets. | **Conflict** | RC-002 has a fixed-instance existential witness and no serialized branch choice. Its pointwise FK, margin and clearance polynomials are reusable after parameterization, but the quantifier prefix, common branch sign and domain-covering certificate are absent. |
| O2 | Adopt the dimensionless margin $\sigma_B=|\sin\theta_2|$. | **Conflict** (small algebraic replacement) | RC-002 encodes $|L_1L_2\sin q_2|\ge\varepsilon$ and records square-length units. The desired predicate is $4t_2^2\ge\varepsilon^2(1+t_2^2)^2$ without offsets, or its exact angle-addition form with $u$. Replacing the polynomial is mechanically small, but changes the meaning and units, so the kill test needs a distinct claim rather than silently reusing RC-002's margin. |
| O3 | Add a bounded $q_2$ zero offset; do not add a base offset in the kill test. | **Conflict** | RC-002 has fixed link lengths and no uncertainty variables. Add $u=\tan(\beta_2/2)$ with rational bounds, universally quantify it, and use $q_2+\beta_2$ in FK, branch and margin predicates. Compose sine and cosine through exact rational addition identities with their positive product denominator; do not depend on a floating-point angle or silently widen a box. |
| O4 | Adopt $R=P\oplus\bar B(0,\rho)$ for a finite rational set $P$. | **Conflict** | RC-002 bakes one rational target into FK coefficients. Retain those pointwise FK numerators as polynomial templates, but promote the target coordinates to universal variables and encode each closed disc exactly. A finite $P$ gives a finite conjunction of disc-domain coverage obligations. |
| O5 | Use a branch-selected algebraic Skolem witness, not image covering. | **Conflict** | RC-002 accepts one supplied rational $(t_1,t_2)$ and has no parameter-dependent witness or algebraic-extension checker. The proposed witness is described below. Image covering would require a separate global surjectivity and boundary argument and has less direct correspondence with RC-002's pointwise identities. |
| O6 | Use both link segments thickened by rational radius $r$ against rational convex polygons. | **Conflict** | RC-002 checks segment clearance from one circular obstacle by a point-to-segment case split. Its endpoint and FK algebra are reusable, but the obstacle model and clearance witness are not. Replace circle predicates with §3.3 separating-line witnesses for every segment–polygon pair, at margin $\mu+r$. |

None of O1–O6 is already supported as stated by the current RC-002 claim and
checker. O2 has a small local polynomial change, but remains a semantic conflict.
The reusable portion is the exact half-angle FK and endpoint algebra, not the
quantifier handling, domain coverage, uncertainty model, obstacle model or
certificate semantics.

## O5 concrete proposal

For fixed $L$, offset and target $x$, use the law of cosines to define the
physical second-joint cosine

$$
c=\frac{\lVert x\rVert^2-L_1^2-L_2^2}{2L_1L_2}.
$$

Introduce an algebraic variable $s$ satisfying

$$
s^2=1-c^2,\qquad b\,s>0.
$$

The approved positive margin excludes $s=0$, so the branch selects one real
root. Derive the physical second-joint half-angle and the first-joint rotation
from $(c,s,L,x)$, then remove the approved zero offset with exact angle-difference
identities to obtain the commanded witness. On each rational parameter cell,
the certificate must isolate the selected algebraic root, prove every required
denominator nonzero with its sign, and establish FK, commanded joint limits,
dimensionless margin and all separating-line inequalities.

The checker remains separate from search. It should verify rational polynomial
identities modulo the algebraic relation, rational root-isolation/sign data,
cell coverage and exact PSD obligations. Its implementation may use integer and
rational arithmetic only. Search may use floating point to propose cells,
witness expressions and Gram matrices, but acceptance must depend solely on the
exact serialized evidence.

### Cost

- Add an exact quadratic-algebraic representation with deterministic root
  isolation and sign checking.
- Extend identity checking from ordinary rational polynomials to identities
  reduced modulo the witness relation.
- Carry denominator and branch-sign obligations explicitly on every cell.
- Expect larger SOS bases and more cells near joint, branch, target-disc and
  clearance boundaries.
- Add positive, malformed, wrong-root, wrong-branch, uncovered-cell, corrupted
  identity, non-PSD and zero-denominator tests.

This is more work than RC-002's rational point checker, but it exploits the
one-solution-per-branch structure and keeps each accepted witness directly tied
to the pointwise RC-002 algebra. Image covering remains a possible later route;
it is not part of the kill test unless the owner rejects this proposal.

## Scope and status

These choices could address Claim (U) for the approved kill-test instance. They
do not solve it, do not establish a certificate, and do not establish anything
about paths, dynamics, safety, standards compliance or the physical cell.
Hypothesis H2 remains an external assumption. The soundness of any future
checker and certificate format would be a separate proof obligation. Until
exact inner evidence or a validated outer counterexample exists, the instance
status remains unknown and every research statement remains E0.
