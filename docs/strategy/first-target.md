# RoboCert: recommended first target and next steps

Ruby Lin · 26 September 2026 · Source of truth for the first-target work (see §5, step 1).

Target planar precision cell layout sign-off, and do nothing else until a cheap kill test shows the claim survives real tolerances. Every candidate here is an E0 hypothesis; RoboCert could address this problem, it has not solved it.

## 1. Recommended target

A precision assembly integrator, or an in-house automation engineer, fixing fixture, tray and feeder coordinates for a SCARA-style planar cell before steel is cut.

The decision they make: commit to this layout, or move the feeder.

The fit comes from three features of this buyer. The cell runs unchanged for years, so a slow certificate on fixed geometry is worth producing. Clearances are millimetres and repeatability is on the order of ±0.01–0.02 mm, so near-singular behaviour and tolerance stack-up actually bite. And it is the only candidate where reachability, singularity margin and robustness to tolerance are all load-bearing at once.

## 2. The claim, in plain words

For link lengths within tolerance, every target point is reachable on one elbow branch with a guaranteed distance from singularity and a guaranteed clearance from obstacles — verified in exact rational arithmetic and independently recheckable.

It is design justification for a planar kinematic model, not a safety case and not a motion guarantee. Section 3 makes every term precise, states the claim with explicit quantifiers, and lists what it does not assert.

## 3. Formal statement

The claim is a first-order statement over ℝ with rational data, and the recommended form is the uniform-branch version (U) with a dimensionless singularity margin. Nothing here is certified for any concrete cell; the main statement is an E0 claim schema.

### 3.1 Model and data

All data are rational. A problem instance is the tuple D = (L̄, δ, Q, P, ρ, O, r).

**Link lengths.** L = (L₁, L₂) ranges over the tolerance box

$$
\Delta = [\bar L_1 - \delta_1,\ \bar L_1 + \delta_1] \times [\bar L_2 - \delta_2,\ \bar L_2 + \delta_2] \subset \mathbb{Q}^2_{>0}
$$

**Joint domain.** Q = [q₁⁻, q₁⁺] × [q₂⁻, q₂⁺] ⊂ (−π, π)².

**Kinematics.** With the base at the origin, the end-effector map f_L and the elbow point e_L are

$$
f_L(q) = \begin{pmatrix} L_1\cos q_1 + L_2\cos(q_1+q_2) \\ L_1\sin q_1 + L_2\sin(q_1+q_2) \end{pmatrix}, \qquad e_L(q) = \begin{pmatrix} L_1\cos q_1 \\ L_1\sin q_1 \end{pmatrix}
$$

**Rational parameterisation.** The substitution t_i = tan(q_i / 2) is a bijection (−π, π) → ℝ with

$$
\cos q_i = \frac{1 - t_i^2}{1 + t_i^2}, \qquad \sin q_i = \frac{2 t_i}{1 + t_i^2}
$$

Under it, f_L and e_L are rational maps in (L, t) with rational coefficients and positive denominator (1 + t₁²)(1 + t₂²), and Q becomes the box T = [t₁⁻, t₁⁺] × [t₂⁻, t₂⁺].

**Target set.** R = P ⊕ B̄(0, ρ), where P ⊂ ℚ² is the finite set of nominal pick and place positions, ρ ∈ ℚ≥0 is placement tolerance, B̄ is a closed disc and ⊕ is Minkowski sum.

**Obstacles.** O = O₁ ∪ … ∪ O_m, each O_j a closed convex polygon with rational vertices.

**Link geometry.** Each link is a segment thickened by radius r ∈ ℚ≥0.

Two standing hypotheses:

- **H1 (rational limits).** t_i^± = tan(q_i^± / 2) ∈ ℚ, obtained if necessary by rounding each joint limit inward.
- **H2 (model fidelity).** The physical cell's link lengths lie in Δ and its geometry is as stated. H2 is an assumption about the world; no certificate verifies it.

### 3.2 Singularity margin

For planar 2R the Jacobian determinant factorises, which settles the choice of measure.

$$
\det J_L(q) = \det \frac{\partial f_L}{\partial q}(q) = L_1 L_2 \sin q_2
$$

Two candidate measures:

$$
\sigma_A(L, q) = |\det J_L(q)| = L_1 L_2\,|\sin q_2| \quad [\text{length}^2], \qquad \sigma_B(q) = |\sin q_2| \quad [\text{dimensionless}]
$$

**Lemma 1 (scaling equivalence).** For ε > 0 and L ∈ Δ, with m_Δ = (L̄₁ − δ₁)(L̄₂ − δ₂) and M_Δ = (L̄₁ + δ₁)(L̄₂ + δ₂):

$$
\sigma_B(q) \ge \varepsilon \;\Rightarrow\; \sigma_A(L, q) \ge \varepsilon\, m_\Delta, \qquad \sigma_A(L, q) \ge \varepsilon' \;\Rightarrow\; \sigma_B(q) \ge \varepsilon' / M_\Delta
$$

*Proof.* Immediate from the factorisation and L₁L₂ ∈ [m_Δ, M_Δ]. ∎

Recommendation: use σ_B. Its threshold does not change with units, and any σ_A requirement converts to it by Lemma 1. In the rational parameterisation it is a polynomial inequality with no square root:

$$
\sigma_B(q) \ge \varepsilon \iff 4 t_2^2 \ge \varepsilon^2 (1 + t_2^2)^2
$$

**Lemma 2 (reach annulus).** Let L ∈ ℝ²₊, x ∈ ℝ² and ε ∈ (0, 1]. Ignoring joint limits and obstacles, there exists q with f_L(q) = x and σ_B(q) ≥ ε if and only if

$$
\left( \|x\|^2 - L_1^2 - L_2^2 \right)^2 \le (1 - \varepsilon^2)\,(2 L_1 L_2)^2
$$

*Proof.* By the law of cosines, ‖f_L(q)‖² = L₁² + L₂² + 2L₁L₂ cos q₂, so any solution forces cos q₂ = c := (‖x‖² − L₁² − L₂²) / (2L₁L₂), and sin² q₂ = 1 − c² ≥ ε² is the displayed inequality. Conversely, if it holds then |c| < 1, q₂ = ± arccos c gives |sin q₂| ≥ ε, and since the vector (L₁ + L₂ cos q₂, L₂ sin q₂) has norm ‖x‖, a rotation angle q₁ with f_L(q) = x exists. ∎

Consequence: reachability together with the margin reduces to a polynomial inequality in (x, L) alone. Joint limits and clearance are where the configuration-space work actually lies.

### 3.3 Clearance

The arm's occupied set is the union of its two link segments, thickened by r:

$$
A_L(q) = \big( [0,\, e_L(q)] \cup [e_L(q),\, f_L(q)] \big) \oplus \bar B(0, r)
$$

For μ > 0, since thickening by r lowers distance by exactly r, the clearance requirement splits into finitely many segment–polygon conditions:

$$
\operatorname{dist}\big(A_L(q), O\big) \ge \mu \iff \operatorname{dist}\big(S_k(L,q), O_j\big) \ge \mu + r \quad \text{for } k = 1, 2,\ j = 1, \dots, m
$$

where S₁ = [0, e_L(q)] and S₂ = [e_L(q), f_L(q)].

**Proposition 3 (separating-line form).** Let η > 0, S = [s₀, s₁] a segment and O_j = conv{v₁, …, v_k} a polygon. Then dist(S, O_j) ≥ η if and only if there exist a ∈ ℝ² and b ∈ ℝ with

$$
\|a\|^2 \le 1, \qquad a \cdot s_i \le b \ \ (i = 0, 1), \qquad a \cdot v_l \ge b + \eta \ \ (l = 1, \dots, k)
$$

*Proof.* (⇐) The linear conditions extend to all convex combinations, so a · (o − s) ≥ η for every s ∈ S and o ∈ O_j, and a · (o − s) ≤ ‖a‖ ‖o − s‖ ≤ ‖o − s‖. (⇒) Take a closest pair (s\*, o\*), set a = (o\* − s\*) / ‖o\* − s\*‖ and b = a · s\*; the separating hyperplane theorem for disjoint compact convex sets gives the conditions with margin ‖o\* − s\*‖ ≥ η. ∎

Why this form: the endpoints s_i are rational functions of (L, t), the conditions are polynomial after clearing positive denominators, and no square root appears. When a and b are allowed to depend on (L, t) this is the parametric separating-hyperplane certificate that C-IRIS uses for collision-freeness [[2]](#sources); the relaxation ‖a‖² ≤ 1 instead of ‖a‖ = 1 is sound and loses nothing.

### 3.4 The claim, formally

Fix ε ∈ (0, 1] and μ > 0, both rational. A configuration is admissible for L when it respects joint limits, the margin and the clearance:

$$
\mathrm{Adm}_D(L, q;\, \varepsilon, \mu) \;:\!\iff\; q \in Q \;\wedge\; \sigma_B(q) \ge \varepsilon \;\wedge\; \operatorname{dist}\big(A_L(q), O\big) \ge \mu
$$

The two elbow branches are Q_b = { q ∈ Q : b · sin q₂ > 0 } for b ∈ {+1, −1}.

**Lemma 4 (at most one solution per branch).** If (‖x‖² − L₁² − L₂²)² < (2L₁L₂)², then f_L(q) = x has at most one solution in each Q_b.

*Proof.* By the law of cosines cos q₂ = c with |c| < 1, so q₂ = b · arccos c is fixed by the branch; q₁ is then fixed modulo 2π by the direction of x, and Q ⊂ (−π, π)² admits at most one representative. ∎

**Claim (P), pointwise branch.**

$$
\forall L \in \Delta\ \ \forall x \in R\ \ \exists q:\quad f_L(q) = x \;\wedge\; \mathrm{Adm}_D(L, q;\, \varepsilon, \mu)
$$

**Claim (U), uniform branch.**

$$
\exists b \in \{+1, -1\}\ \ \forall L \in \Delta\ \ \forall x \in R\ \ \exists q \in Q_b:\quad f_L(q) = x \;\wedge\; \mathrm{Adm}_D(L, q;\, \varepsilon, \mu)
$$

By Lemmas 2 and 4, the witness q in (U) is unique for each (L, x), so (U) is equivalently a statement about one explicit inverse-kinematics map g_{L,b}: R → Q_b.

**Proposition 5 (why U, not P).** (U) implies (P); the converse fails in general. Moreover, any continuous curve in Q joining a point of Q₊₁ to a point of Q₋₁ contains a configuration with σ_B = 0.

*Proof.* The implication is immediate. For the second part, sin q₂ is continuous along the curve and changes sign, so it vanishes somewhere by the intermediate value theorem. ∎

Proposition 5 is a fact about the configuration space, not a motion claim. Its practical reading: under (P), a certified cell may still need the arm to change elbow branch between two targets, and every such change passes through a singular configuration. (U) rules that out, which is why it is the recommended form for layout sign-off.

**Status.** For every concrete instance D, whether (U) holds is unknown. It is an E0 claim schema, not a theorem.

### 3.5 Certificate and checker

Write Φ_D(ε, μ) for Claim (U) with the branch b fixed. By §§3.1–3.3, Φ_D is a first-order formula over the reals with rational coefficients, of the form ∀(L, x) ∃q. It is decidable in principle by quantifier elimination, but that route is far too expensive to serve as a checker, so the claim is carried by a certificate instead.

**Certificate.** A finite object C = (b, (K_i, w_i) for i = 1, …, N), where:

- the cells K_i are rational boxes whose union covers the quantified domain;
- each witness w_i establishes on K_i the three conditions of Adm_D — the annulus inequality of Lemma 2, the joint limits, and the separating-line conditions of Proposition 3 with (a, b) allowed to be polynomial in the cell variables;
- each inequality p ≥ 0 on a cell is carried by a polynomial identity with rational coefficients, for instance

$$
p = \sigma_0 + \sum_k \sigma_k\, g_k, \qquad \sigma_k = z_k^{\top} G_k\, z_k,\ \ G_k \in \mathbb{Q}^{n_k \times n_k},\ G_k \succeq 0
$$

where the g_k ≥ 0 describe the cell and the z_k are monomial vectors.

**Checker.** A procedure Check(D, C) ∈ {accept, reject} using integer and rational arithmetic only:

1. **Cover.** The cells cover the domain, by exact rational comparisons.
2. **Identities.** Every polynomial identity holds coefficient by coefficient in the rational polynomial ring.
3. **Positivity.** Every G_k is positive semidefinite, decided by exact rational LDLᵀ elimination.

**Soundness requirement.**

$$
\mathrm{Check}(D, C) = \mathrm{accept} \;\Longrightarrow\; \Phi_D(\varepsilon, \mu)
$$

Soundness is a theorem about the checker and the certificate format, proved once, not per instance.

**Why this is exact.** D and C are finite sets of rationals, and each step is a finite rational computation with no rounding, so any independent implementation reaches the same verdict. This is the practice already used for exact SOS results, where a standalone program reads only archived certificates and decides positive semidefiniteness by exact rational elimination [[6]](#sources); numerical Gram matrices are turned into rational ones by rounding and projection [[5]](#sources).

**What the checker does not establish.** Hypothesis H2; completeness, since reject does not mean Φ_D is false; and nothing in §3.6. How the existential ∃q is discharged is left open as O5 in §3.7.

### 3.6 What the statement does not assert

Φ_D is a statement about the static map (L, q) ↦ (f_L(q), A_L(q)) under the model of §3.1. Stated as exclusions:

- **No curves.** It makes no statement about any curve γ: [0, 1] → Q, so nothing about executing a sequence of targets. Proposition 5 describes the configuration space; it is not a path guarantee.
- **No time or dynamics.** No velocities beyond what σ_B ≥ ε implies about invertibility of J_L, and no torques, inertia, controller behaviour or contact forces.
- **No safety.** No statement about harm to people, and no claim of compliance with ISO 10218 or any other safety standard.
- **Planar projection only.** A SCARA's vertical axis and tool rotation are outside the model; the claim concerns the two planar joints.
- **Model-relative truth.** Φ_D holds for the model under H1 and H2. Whether the physical cell satisfies H2 is not verified, and any change to D voids the certificate.

### 3.7 Open modelling choices

Each choice changes what the certificate proves; none should be settled silently in code.

| ID | Choice | Options | Recommendation |
|--------|--------------------|------------------------------------------------|--------------------------------------------------|
| O1 | IK branch | (P) branch may vary per target; (U) one branch for all of R | (U), by Proposition 5 |
| O2 | Margin measure | σ_A = \|det J_L\|; σ_B = \|sin q₂\|; condition number of J_L | σ_B, by Lemma 1; the condition number depends on L and q jointly and is unit-sensitive unless lengths are normalised |
| O3 | Tolerance model | Link lengths only; plus joint zero offsets β, with q ↦ q + β; plus base offset τ ∈ B̄(0, ρ_b) | At minimum add the q₂ offset, which shifts σ_B directly. Base offset can be handled soundly but conservatively by replacing R with R ⊕ B̄(0, ρ_b) and O with O ⊕ B̄(0, ρ_b), which decouples the shared τ |
| O4 | Target set | Finite P ⊕ B̄(0, ρ); finite union of rational polygons | P ⊕ B̄(0, ρ): it matches discrete pick positions with placement tolerance |
| O5 | Discharging ∃q | Algebraic witnesses on the variety f_L(q) = x; image covering of R by f_L over cells of Δ × Q_b | Open; decide against the existing RC-002 encoding before the kill test is coded |
| O6 | Link geometry | Segments thickened by r; general convex polygons | Segments with r, which keeps Proposition 3 to two endpoints per link |

## 4. Why this target

No existing method establishes Claim (U): each covers at most one of reachability, margin and robustness.

| Method | What it gives | What it leaves open |
|-------------------------|------------------------------------------------|------------------------------------------------|
| CAD reach study, offline simulation | Reachability at sampled waypoints, nominal geometry | Behaviour between samples; points that pass reach but are near-singular and fail at commissioning |
| SCARA layout optimisation | A workpiece position as far as possible from singular configurations [[3]](#sources) | An optimum, not a bound: no statement that every point clears a threshold |
| C-IRIS | Collision-free C-space regions, rigorously certified, scaling to 7-DOF and 12-DOF bimanual arms [[1]](#sources) | Target reachability, singularity margin, robustness to link-length error; the certificate is nominal and solver-derived |

Exactness earns its place for two specific reasons. Near a singularity σ_B is close to zero, so a floating-point value is least trustworthy exactly where the decision turns. And SOS methods on double-precision SDP solvers emit approximate nonnegativity certificates [[4]](#sources); a sampled answer cannot tell "no bad point exists" from "no bad point was sampled" [[2]](#sources).

## 5. Next steps

Every step narrows scope and ends in something written down; the failure to guard against is drifting back into "continue the roadmap".

| # | Step | Done when |
|-----|------------------------------------------------------------|----------------------------------------|
| 1 | Make this document the source of truth: commit it as `docs/strategy/first-target.md` | The repo file and this document match; one is named canonical |
| 2 | Freeze the roadmap: no G2 work, no RC-002 changes beyond what the kill test needs | Freeze noted in `revised-direction.md` |
| 3 | Settle the open modelling choices O1–O6 of §3.7 | Each choice recorded, with its reason |
| 4 | Fix the instance D from one real SCARA datasheet and one real tray footprint | Every input marked datasheet or assumption |
| 5 | Run the kill test of §6, and only the kill test | `docs/strategy/kill-test-result.md` exists |
| 6 | Run the two side checks of §7 as separate tasks, in parallel with step 5 | Each has a one-page written finding |
| 7 | Decide at one checkpoint, weighing the kill test and side checks together | Dated decision written into `revised-direction.md` |

```mermaid
flowchart TD
  A[1–3 Source of truth,<br/>freeze, modelling choices] --> B[4–5 Kill test]
  A --> C[6 Side checks]
  B --> D{7 Checkpoint}
  C --> D
  D -->|margin survives<br/>and demand exists| E[Proceed to G2]
  D -->|margin tight| F[Tighten certificate<br/>first]
  D -->|nothing survives<br/>or no demand| G[Fallback]
```

The side checks feed the same checkpoint on purpose: a technically surviving margin with no one who wants the certificate is still a reason to take the fallback.

## 6. The kill test

Question: for one realistic instance D, does the integrator's requirement (ε_req, μ_req) survive a plausible tolerance δ?

**Inputs,** each taken from a named datasheet or marked as an assumption:

1. L̄₁, L̄₂ and δ, covering manufacturing plus calibration error — this fixes Δ.
2. The pick and place set P and placement tolerance ρ — this fixes R. Use the actual tray footprint, not a generous rectangle.
3. The obstacle polygons O and link radius r, with the true available clearance.
4. ε_req, derived from tolerable velocity amplification rather than chosen for convenience, and μ_req.

**Rules.**

- Stop after fixing inputs and get approval before computing. Invented numbers presented as real are the largest risk in this step.
- Reuse RC-002's encoding and witness polynomials; add only what the test needs.
- No floating point in any step the result depends on.

**Formal decision.** For a fixed branch b, the feasible set is

$$
F_D = \{ (\varepsilon, \mu) \in (0, 1] \times \mathbb{Q}_{>0} \;:\; \Phi_D(\varepsilon, \mu) \}
$$

**Lemma 6 (monotonicity).** F_D is downward closed: (ε, μ) ∈ F_D, ε′ ≤ ε and μ′ ≤ μ imply (ε′, μ′) ∈ F_D. It can only grow when Δ, R or O shrink; in particular it is non-increasing in δ.

*Proof.* Every condition in Adm_D is a threshold inequality, and shrinking Δ, R or O removes universally quantified cases or obstacle constraints. ∎

Two kinds of exact evidence locate the requirement:

- **Inner evidence.** A certificate C with Check(D, C) = accept for Φ_D(ε_in, μ_in), proving (ε_in, μ_in) ∈ F_D.
- **Outer evidence.** A rational point (L\*, x\*) ∈ Δ × R at which the unique candidate of Lemma 4 in Q_b fails Adm_D(ε_out, μ_out), proving (ε_out, μ_out) ∉ F_D. The candidate's half-angle t₂ lies in a quadratic extension of ℚ, so this check is exact but not purely rational.

| Outcome | Formal condition at (ε_req, μ_req) | Reading | Action |
|----------------|------------------------------|------------------------------|--------------------------|
| Proceed | Inner evidence | The distinctive claim is real for this D | Proceed to G2 |
| Tighten | Neither inner nor outer evidence | Conservatism is the bottleneck, not the concept | Tighten the certificate before G2 |
| Fallback | Outer evidence for both branches | Claim (U) provably fails for this D | Take the fallback |

The fallback row is a proof, not a failure of the method. Every reported ε or μ is a certified bound on the frontier of F_D, never the frontier itself.

## 7. Side checks

Two cheap checks, each run as its own task so neither leaks into the kill test.

### 7.1 Demand: does anyone value exactly rechecked certificates?

Partially supported, but only outside robotics. Under DO-178C and DO-333, formal methods can earn certification credit, and a tool whose output is used for credit must be qualified [[7]](#sources). One case study checked a model checker's proof certificates with a qualified proof checker instead of qualifying the tool itself [[8]](#sources). No evidence of demand in robot cell integration was found.

- **Check:** ask two or three integrators what evidence they hand over at cell acceptance, and whether a reach or singularity claim has ever been disputed after handover.
- **Weakened by:** no customer ever asking for an analytical artifact; sign-off test-based and schedule-driven.
- **Refuted by:** a customer or notified body rejecting analytical evidence for this class of claim.

### 7.2 C-IRIS exactness gap

The claim "never re-verified exactly" is too strong. Exact rational rounding of SOS certificates is a known, packaged technique [[5]](#sources), and solver-free exact rechecking from archived certificate files is already practised elsewhere [[6]](#sources). The defensible version: no one appears to have applied it to published robot C-space certificates. That is unconfirmed.

- **Check:** read the Drake C-IRIS certificate-verification path; see whether the SDP is wrapped in verified or interval arithmetic. About one afternoon.
- **Refuted by:** existing rational rounding or verified SDP on C-IRIS separating-hyperplane certificates.

## 8. Checkpoint, fallback and project scope

One decision, taken once both the kill test and the side checks have reported, written into `revised-direction.md` with its date and the evidence it rests on.

**Fallback.** If the margin does not survive, or no buyer wants the certificate, switch to the exact checker of §3.5 as a detachable artifact: a certificate that travels with a layout proposal and is rechecked by a small rational-arithmetic program with no solver in it. It does not depend on a tight inflated margin. Its own blocker is export — if rechecking needs RoboCert internals, the result is a second solver, not a checker.

**Out of project scope,** whichever way the checkpoint goes (the claim's own exclusions are in §3.6):

- 6- and 7-DOF planning in cluttered scenes, where C-IRIS already scales.
- Human-robot collaborative safety, which ISO 10218:2025 governs through power-and-force limiting and speed-and-separation monitoring at application level [[9]](#sources).
- High-mix cells whose layout changes often enough that a fixed-geometry certificate goes stale.

## Sources

1. [Certified Polyhedral Decompositions of Collision-Free Configuration Space](https://arxiv.org/pdf/2302.12219) — C-IRIS scope and scaling.
2. [Finding and Optimizing Certified, Collision-Free Regions in Configuration Space](https://arxiv.org/pdf/2205.03690) — sampling-density limitation; parametric separating hyperplanes.
3. [Singularity avoidance for SCARA robots](https://www.sciencedirect.com/science/article/abs/pii/092188909290015Q) — layout optimisation against singular configurations.
4. [Computer-Assisted Proofs for Lyapunov Stability via SOS](https://arxiv.org/html/2006.09884v2) — double-precision SDP yields approximate certificates.
5. [Sums of squares in Macaulay2](https://arxiv.org/pdf/1812.05475) — rational rounding and projection.
6. [Explicit Separators for Consecutive Levels of Parrilo's Hierarchy](https://arxiv.org/pdf/2608.27743) — solver-free exact rational verification.
7. [DO-333 Certification Case Studies](https://loonwerks.com/publications/pdf/cofer2014nfm.pdf) — certification credit and tool qualification.
8. [Qualification of a Model Checker for Avionics Software Verification](https://link.springer.com/chapter/10.1007/978-3-319-57288-8_29) — proof certificates in lieu of tool qualification.
9. [ISO 10218:2025 explained](https://theresarobotforthat.com/blog/iso-10218-2025-explained/) — collaborative safety as an application property.
