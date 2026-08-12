# RoboCert

> **Mathematical certification of robot reachability, collision freedom, singularity separation, and feasibility under geometric and manufacturing uncertainty.**

RoboCert is a research project for **certified robotics**.

Given a robot model, tool geometry, workstation CAD, obstacles, task requirements, joint limits, and bounded manufacturing/calibration uncertainty, RoboCert aims to answer questions stronger than conventional simulation:

> **Certified feasibility:**  
> Every configuration or task instance in a specified region satisfies the required reachability, collision-separation, joint-limit, and singularity-margin conditions, under explicitly stated assumptions.

or

> **Certified infeasibility:**  
> No feasible configuration exists because the supplied algebraic, geometric, or robust constraints are mutually inconsistent.

The intended distinction is fundamental:

\[
\text{simulation / sampling evidence}
\;\neq\;
\text{mathematical certificate over a continuum of states}.
\]

RoboCert is therefore not primarily a trajectory simulator, CAD package, or AI motion planner. Its core purpose is to construct, verify, and explain **machine-checkable certificates for quantified statements about robot configuration spaces**.

---

## Status

**Research / pre-alpha.**

RoboCert is currently a project specification and research architecture. No production safety claim should be inferred from this repository until individual certificate backends, checkers, numerical kernels, geometry pipelines, and system assumptions have been independently validated.

---

## 1. Motivation

Conventional robotics software can efficiently test:

- whether a particular configuration is in collision;
- whether a numerical inverse-kinematics solver finds a solution;
- whether a sampled trajectory violates joint limits;
- whether a Jacobian is poorly conditioned at sampled configurations;
- whether a physics simulation succeeds for a finite set of trials.

Those computations are indispensable, but they do not by themselves establish a universally quantified claim such as

\[
\forall q\in R,\qquad \operatorname{Safe}(q).
\]

Nor does failure of a nonlinear optimizer generally prove

\[
\nexists q\in Q,\qquad \operatorname{Feasible}(q).
\]

RoboCert targets exactly this gap.

The project seeks to move from

\[
q_1,q_2,\ldots,q_N\ \text{tested successfully}
\]

to statements of the form

\[
\forall q\in R,\ \forall \theta\in\Theta:
\operatorname{Safe}(q,\theta),
\]

and from

\[
\text{a solver did not find a solution}
\]

to

\[
\forall q\in Q,\ \forall \theta\in\Theta:
\neg\operatorname{Feasible}(q,\theta),
\]

whenever a sound certificate can be constructed.

---

## 2. Project objective

Let

- \(q\in Q\) denote robot configuration variables;
- \(x\in X\) denote task-space variables;
- \(\theta\in\Theta\) denote bounded geometric, calibration, or manufacturing uncertainty;
- \(W\) denote the workstation geometry;
- \(T\) denote a set of required tasks or poses.

RoboCert should compile engineering input into a mathematical model and attempt to certify propositions including:

### 2.1 Robust collision freedom

\[
\forall q\in R,\ \forall\theta\in\Theta:
\operatorname{dist}\!\left(
\mathcal R(q,\theta),
\mathcal O(\theta)
\right)\ge \delta_{\mathrm{col}}>0.
\]

Here:

- \(\mathcal R(q,\theta)\) is the occupied robot/tool geometry;
- \(\mathcal O(\theta)\) is the obstacle/workstation geometry;
- \(\delta_{\mathrm{col}}\) is a required clearance margin.

### 2.2 Robust joint-limit satisfaction

\[
\forall q\in R:
q_i^{\min}+\delta_i
\le q_i
\le q_i^{\max}-\delta_i.
\]

### 2.3 Reachability of an entire task region

For a task region \(T\),

\[
\forall x\in T,\ \forall\theta\in\Theta,\ 
\exists q\in R:
F(q,\theta)=x
\land
\operatorname{Safe}(q,\theta).
\]

The order of quantifiers is part of the specification and must never be changed silently.

For example,

\[
\forall \theta\,\exists q
\]

means that a feasible configuration may depend on the realized uncertainty, whereas

\[
\exists q\,\forall \theta
\]

requires a single configuration to work robustly for all admissible uncertainty. These are different engineering claims.

### 2.4 Singularity separation

For a Jacobian \(J(q,\theta)\), certify a margin such as

\[
\sigma_{\min}(J(q,\theta))
\ge \varepsilon
\qquad
\forall(q,\theta)\in R\times\Theta.
\]

When a polynomial/rational formulation is used, equivalent algebraic conditions may be imposed through minors, Gram matrices, determinant inequalities, or certified lower bounds.

### 2.5 Certified infeasibility

Given constraints

\[
f_i(z)=0,\qquad
g_j(z)\ge 0,\qquad
h_k(z)>0,
\]

with \(z=(q,x,\theta,\ldots)\), prove that the associated semialgebraic set

\[
S=
\left\{
z\in\mathbb R^n:
f_i(z)=0,\;
g_j(z)\ge0,\;
h_k(z)>0
\right\}
\]

is empty.

A valid result is therefore not merely

```text
OPTIMIZER_STATUS = INFEASIBLE
```

but, wherever feasible, an independently checkable mathematical witness of infeasibility.

---

## 3. Mathematical viewpoint

The central mathematical object in RoboCert is usually a **semialgebraic set**.

A basic closed semialgebraic set has the form

\[
S=
\left\{
z\in\mathbb R^n:
f_1(z)=\cdots=f_r(z)=0,\;
g_1(z)\ge0,\ldots,g_m(z)\ge0
\right\},
\]

where \(f_i,g_j\in\mathbb R[z_1,\ldots,z_n]\).

Robot kinematics contain trigonometric functions, but revolute joints can often be rationalized using the tangent-half-angle substitution

\[
t_i=\tan\frac{q_i}{2},
\]

so that

\[
\sin q_i=\frac{2t_i}{1+t_i^2},
\qquad
\cos q_i=\frac{1-t_i^2}{1+t_i^2}.
\]

After clearing denominators with appropriate domain bookkeeping, many kinematic and collision-separation statements become polynomial or rational inequalities.

This makes available tools from:

- real algebraic geometry;
- computational algebraic geometry;
- semialgebraic geometry;
- Gröbner-basis methods;
- elimination theory;
- real quantifier elimination;
- cylindrical algebraic decomposition;
- resultants and discriminants;
- Positivstellensatz certificates;
- sum-of-squares optimization;
- semidefinite programming;
- interval arithmetic;
- validated numerics;
- exact rational arithmetic;
- computational and convex geometry.

RoboCert should be **method-pluralistic**: exact symbolic methods, convex certificates, interval methods, and numerical global optimization are complementary backends rather than competing philosophies.

---

## 4. The principal specification

A representative RoboCert contract is

\[
\boxed{
\forall\theta\in\Theta\;
\forall x\in T\;
\exists q\in R:
J(q)
\land
K(q,\theta,x)
\land
C(q,\theta)
\land
S(q,\theta)
}
\]

where:

- \(J(q)\): joint-limit constraints;
- \(K(q,\theta,x)\): kinematic task constraints;
- \(C(q,\theta)\): collision/clearance constraints;
- \(S(q,\theta)\): singularity-separation constraints.

A stronger robust-realization contract may instead require

\[
\boxed{
\exists q\in R\;
\forall\theta\in\Theta:
J(q)\land C(q,\theta)\land S(q,\theta)\land K(q,\theta,x)
}
\]

for each task \(x\).

The exact quantifier prefix is therefore a first-class object in RoboCert.

No frontend, agent, optimizer, or model converter may reorder quantifiers without producing a new problem specification.

---

## 5. Design principles

### 5.1 Soundness before convenience

A successful certification result must mean what it says.

RoboCert should prefer

\[
\text{UNKNOWN}
\]

over an unjustified

\[
\text{CERTIFIED}.
\]

Failure to certify does **not** imply infeasibility.

### 5.2 Proof is distinct from search

The architecture should separate:

1. **search / synthesis**, which may use heuristics, nonlinear optimization, sampling, machine learning, or LLM agents;
2. **certification**, which constructs a mathematical witness;
3. **checking**, which independently validates that witness.

Conceptually:

```text
engineering problem
       |
       v
candidate generator
       |
       v
certificate constructor
       |
       v
independent checker
       |
       +----> CERTIFIED
       |
       +----> REJECTED / UNKNOWN
```

### 5.3 Explicit assumptions

Every result must carry its assumptions.

Examples:

- rigid-body geometry;
- exact joint-axis model;
- bounded calibration error;
- bounded link-dimensional tolerances;
- obstacle convexity;
- static obstacles;
- no elastic deformation;
- exact or bounded tool-center-point error;
- kinematic rather than dynamic feasibility;
- chosen floating-point error model;
- chosen collision geometry approximation.

A theorem proved under an incorrect engineering model is still the wrong engineering answer.

### 5.4 Small trusted computing base

Where practical, RoboCert should generate certificates that are cheaper and simpler to check than to discover.

The target architecture is:

\[
\text{untrusted/high-complexity search}
\longrightarrow
\text{compact certificate}
\longrightarrow
\text{small trusted checker}.
\]

### 5.5 No LLM in the soundness boundary

An AI agent may:

- parse user intent;
- propose formulations;
- choose candidate methods;
- call solvers;
- generate diagnostic explanations;
- suggest decomposition strategies.

An AI agent must not be the authority that decides whether a theorem has been proved.

The final certification state must be determined by deterministic certificate-checking code.

---

## 6. Inputs

RoboCert should eventually accept the following project-level inputs.

### 6.1 Robot model

Possible representations:

- URDF;
- SDF;
- MJCF;
- Drake model;
- manufacturer kinematic specification;
- explicit symbolic kinematic chain.

Required semantic data include:

- joint type;
- joint axes;
- link frames;
- joint limits;
- fixed transforms;
- collision geometry;
- tool mounting frame.

### 6.2 Tool geometry

Possible representations:

- STEP;
- B-Rep;
- convex primitives;
- certified convex decomposition;
- mesh with declared approximation semantics.

### 6.3 Workstation CAD

Possible representations:

- STEP assembly;
- B-Rep;
- analytic primitives;
- mesh;
- simplified certified collision model.

### 6.4 Obstacles

Each obstacle should specify:

- geometry;
- frame;
- pose;
- uncertainty set;
- required clearance;
- static/dynamic status.

### 6.5 Required tasks

Examples:

- isolated end-effector poses;
- pose boxes;
- Cartesian line segments;
- orientation cones;
- continuous task-space regions;
- parameterized process paths.

### 6.6 Joint limits

Hard limits:

\[
q_i^{\min}\le q_i\le q_i^{\max}.
\]

Optional operational margins:

\[
q_i^{\min}+\delta_i
\le q_i
\le
q_i^{\max}-\delta_i.
\]

### 6.7 Manufacturing and calibration tolerances

Uncertain parameters are represented as sets:

\[
\theta\in\Theta.
\]

The first implementation should prefer mathematically tractable uncertainty sets:

- intervals;
- boxes;
- polytopes;
- ellipsoids;
- basic semialgebraic sets.

---

## 7. Outputs

RoboCert should produce one of a deliberately small number of statuses.

### `CERTIFIED_FEASIBLE`

A formally specified region or task family satisfies the requested properties, with a valid certificate.

### `CERTIFIED_INFEASIBLE`

The requested conjunction of constraints has no realization, with a valid infeasibility certificate.

### `COUNTEREXAMPLE`

A concrete configuration, task point, or uncertainty realization violates the requested property.

A counterexample disproves a universal claim even when no global certificate has been constructed.

### `NUMERICALLY_FEASIBLE`

A candidate solution was found but has not been mathematically certified.

### `NUMERICALLY_INFEASIBLE`

A numerical solver failed or reported infeasibility, but no sound mathematical infeasibility certificate has been checked.

This status must never be presented as proof.

### `UNKNOWN`

RoboCert could neither certify the requested claim nor produce a valid counterexample within the selected computational resources/methods.

`UNKNOWN` is an expected and scientifically legitimate output.

---

## 8. Certificate classes

RoboCert should support multiple certificate families.

### 8.1 Exact algebraic certificates

Potential techniques:

- Gröbner bases;
- elimination ideals;
- resultants;
- comprehensive Gröbner systems;
- Sturm sequences;
- real-root isolation;
- CAD / real quantifier elimination.

Suitable for:

- low-dimensional exact inverse kinematics;
- parametric feasibility;
- discrete branch classification;
- exact infeasibility;
- topology changes associated with discriminant varieties.

### 8.2 Positivstellensatz / SOS certificates

For a domain

\[
K=\{x:g_i(x)\ge0,\;h_j(x)=0\},
\]

prove polynomial nonnegativity or strict positivity over \(K\) using a representation in an appropriate quadratic module or preordering.

A schematic certificate is

\[
p=
\sigma_0+
\sum_i\sigma_i g_i+
\sum_j \lambda_j h_j,
\]

where \(\sigma_i\) are sums of squares.

Suitable for:

- collision-separation inequalities;
- singularity margins;
- robust inequalities;
- invariant or safe sets;
- polynomial optimization bounds.

### 8.3 Convex separation certificates

Suitable when collision geometry or transformed geometry admits separating hyperplanes/polynomials.

This family includes C-space region certification ideas such as C-IRIS.

### 8.4 Interval certificates

Use:

- interval arithmetic;
- interval Newton methods;
- Krawczyk operators;
- validated branch-and-bound;
- directed rounding.

Suitable for:

- root existence/uniqueness;
- robust inequality verification over boxes;
- certified lower bounds;
- validating numerically generated candidates.

### 8.5 Rational reconstruction

When an SDP or floating-point computation produces an approximate algebraic certificate, attempt to recover exact rational data and re-check the resulting identity/inequalities exactly or with validated bounds.

---

## 9. Collision certification

Collision is one of the hardest interfaces between CAD geometry and real algebraic reasoning.

RoboCert should distinguish at least four geometric levels:

### Level A — analytic convex primitives

Examples:

- spheres;
- capsules;
- boxes;
- cylinders;
- convex polytopes.

This should be the first certification target.

### Level B — certified convex decomposition

Complex links and obstacles are replaced by unions of convex pieces with a documented containment relation.

The approximation direction matters.

For safety:

\[
\mathcal G_{\mathrm{true}}
\subseteq
\mathcal G_{\mathrm{outer}}
\]

is useful for conservative collision exclusion.

### Level C — algebraic surface models

Geometry is represented by polynomial inequalities

\[
g_i(x)\ge0.
\]

This can interface directly with real algebraic and SOS methods.

### Level D — general CAD/B-Rep

STEP/B-Rep geometry must be translated into a certification-compatible representation.

This translation itself requires a geometric contract. A visually accurate tessellation is not automatically a conservative certified representation.

---

## 10. Singularity certification

For forward kinematics

\[
F:Q\rightarrow SE(3),
\]

let \(J(q)\) denote an appropriate differential kinematic map.

The singular set can often be represented algebraically after rational parameterization.

For a square Jacobian:

\[
\Sigma=
\{q:\det J(q)=0\}.
\]

More generally:

\[
\Sigma=
\left\{
q:
\text{all maximal-rank minors of }J(q)\text{ vanish}
\right\}.
\]

RoboCert should support stronger margin certificates, for example

\[
\inf_{q\in R}
\sigma_{\min}(J(q))
\ge\varepsilon,
\]

or a certified lower bound on an algebraic surrogate such as

\[
\det(JJ^\top)\ge\gamma>0
\]

when the mathematical conditions make that surrogate sufficient for the intended claim.

The certificate must state exactly which singularity notion is being excluded.

---

## 11. Reachability certification

RoboCert must distinguish:

### Pointwise IK existence

\[
\exists q:F(q)=x.
\]

### Region reachability

\[
\forall x\in T\;\exists q:F(q)=x.
\]

### Safe region reachability

\[
\forall x\in T\;\exists q:
F(q)=x
\land
q\in Q_{\mathrm{safe}}.
\]

### Robust safe region reachability

\[
\forall x\in T\;
\forall\theta\in\Theta\;
\exists q:
F(q,\theta)=x
\land
q\in Q_{\mathrm{safe}}(\theta).
\]

### Continuous-lift reachability

Pointwise existence is weaker than existence of a continuous configuration path.

For a task path

\[
x:[0,1]\to X,
\]

the stronger question is whether there exists a continuous lift

\[
q:[0,1]\to Q
\]

such that

\[
F(q(s))=x(s)
\quad
\forall s\in[0,1]
\]

while maintaining all safety conditions.

This distinction is essential for manipulation and process trajectories.

---

## 12. Robustness and tolerances

Manufacturing tolerance turns a deterministic model into a quantified family.

For nominal parameter \(\theta_0\), define

\[
\Theta=
\{\theta:
|\theta_i-\theta_{0,i}|\le\Delta_i\}.
\]

A robust safety certificate may require

\[
\forall(q,\theta)\in R\times\Theta:
g(q,\theta)\ge0.
\]

This is stronger than checking all tolerance extremes individually when the uncertain dependence is coupled or nonlinear.

RoboCert should preserve a clear distinction between:

- epistemic uncertainty;
- manufacturing tolerance;
- calibration uncertainty;
- runtime state-estimation uncertainty;
- approximation error introduced by geometry conversion.

These uncertainty sources may have different semantics and therefore different quantifier structures.

---

## 13. Proposed architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                         RoboCert                             │
├──────────────────────────────────────────────────────────────┤
│  1. Input / CAD / robot-model ingestion                     │
│     URDF · STEP · tool geometry · obstacles · tolerances     │
├──────────────────────────────────────────────────────────────┤
│  2. Geometry normalization                                  │
│     frames · convex decomposition · conservative envelopes   │
├──────────────────────────────────────────────────────────────┤
│  3. Symbolic model compiler                                 │
│     kinematics · constraints · rationalization · domains     │
├──────────────────────────────────────────────────────────────┤
│  4. Problem specification                                   │
│     variables · semialgebraic sets · quantifier prefix       │
├──────────────────────────────────────────────────────────────┤
│  5. Method planner                                           │
│     exact · QE · SOS/SDP · interval · hybrid                │
├──────────────────────────────────────────────────────────────┤
│  6. Candidate/search backends                               │
│     IK · NLP · global optimization · sampling                │
├──────────────────────────────────────────────────────────────┤
│  7. Certificate backends                                    │
│     Gröbner/QE · SOS · C-space separation · intervals        │
├──────────────────────────────────────────────────────────────┤
│  8. Independent certificate checkers                        │
│     exact arithmetic · validated numerics                    │
├──────────────────────────────────────────────────────────────┤
│  9. Result object                                            │
│     theorem · assumptions · certificate · counterexample     │
├──────────────────────────────────────────────────────────────┤
│ 10. Explanation / visualization                             │
│     regions · failure cores · engineering report             │
└──────────────────────────────────────────────────────────────┘
```

---

## 14. Proposed software layers

The project should avoid premature commitment to a single CAS or solver.

### Layer 1 — robotics and multibody model

Candidate foundation:

- **Drake**

Reasons:

- mature rigid-body and kinematic modeling;
- geometry and collision infrastructure;
- mathematical programming abstraction;
- C-IRIS/C-space certification functionality already present.

### Layer 2 — symbolic algebra

Candidate tools:

- Singular;
- SageMath;
- SymPy;
- Risa/Asir;
- Macaulay2.

The initial backend should be selected by benchmark rather than ideology.

### Layer 3 — exact real algebra / quantifier elimination

Candidate backends:

- Risa/Asir workflows;
- CAD/QE implementations;
- Gröbner-based parametric decomposition;
- optional external CAS adapters where licensing permits.

### Layer 4 — SOS / polynomial optimization

Candidate backends may include:

- Drake `MathematicalProgram`;
- Julia polynomial/SOS ecosystems;
- SDP solver adapters.

### Layer 5 — validated numerics

Candidate technologies:

- MPFR-style directed rounding;
- interval arithmetic libraries;
- arbitrary-precision linear algebra;
- exact rational arithmetic.

### Layer 6 — CAD

Candidate foundations:

- OpenCascade;
- FreeCAD;
- build123d.

The CAD layer is not part of the proof boundary unless its geometry conversion is accompanied by a certified enclosure/representation argument.

---

## 15. Agent architecture

RoboCert may eventually use a multi-agent interface, but agents orchestrate mathematics rather than replace it.

### `SpecificationAgent`

Responsibilities:

- parse engineering intent;
- identify ambiguous quantifier semantics;
- construct a formal problem draft;
- require explicit assumptions.

### `GeometryAgent`

Responsibilities:

- inspect CAD;
- propose conservative geometric approximations;
- call convex-decomposition and frame-normalization tools.

### `AlgebraAgent`

Responsibilities:

- derive polynomial/rational formulations;
- perform elimination;
- identify algebraic branches;
- generate candidate exact certificates.

### `OptimizationAgent`

Responsibilities:

- formulate SOS/SDP/global-optimization problems;
- exploit sparsity;
- produce candidate certificates and bounds.

### `IntervalAgent`

Responsibilities:

- validate numerical roots;
- certify boxes;
- perform branch-and-bound verification.

### `CounterexampleAgent`

Responsibilities:

- aggressively search for violations;
- falsify universal claims quickly.

### `CertificateChecker`

**Not an LLM agent.**

Responsibilities:

- verify certificate syntax;
- check polynomial identities;
- validate interval bounds;
- verify exact/rational inequalities;
- return deterministic pass/fail.

### `ExplanationAgent`

Responsibilities:

- translate a checked result into engineering language;
- identify active constraints;
- display assumptions;
- produce reproducible reports.

---

## 16. Trusted computing base

A central research goal is to minimize RoboCert's trusted computing base (TCB).

A certification result may depend on:

1. parser correctness;
2. robot/CAD model correctness;
3. geometry enclosure correctness;
4. symbolic compilation correctness;
5. certificate checker correctness;
6. exact-arithmetic or validated-numeric kernel correctness.

The candidate-generating optimizer need not necessarily belong to the TCB if its output is independently checkable.

This is an important architectural advantage.

---

## 17. Result schema

Every certified result should be serializable.

Example:

```yaml
robocert_result:
  version: 0.1
  status: CERTIFIED_FEASIBLE

  claim:
    type: robust_region_safety
    quantifiers:
      - forall: q
        domain: certified_region_R
      - forall: theta
        domain: tolerance_set_Theta

  guarantees:
    collision_clearance_m: 0.005
    singularity_margin:
      metric: minimum_singular_value
      lower_bound: 0.08
    joint_limits: satisfied

  assumptions:
    rigid_body_model: true
    obstacle_motion: static
    calibration_model: bounded_box
    geometry_representation: conservative_outer_enclosure

  certificate:
    family: sos
    artifact: certificates/region_004.sos.json
    checker: robocert-check-sos
    checker_version: 0.1

  provenance:
    robot_model_hash: ...
    workstation_model_hash: ...
    specification_hash: ...
```

The result object should be immutable after certification. Any change to input geometry, tolerances, task constraints, or mathematical assumptions invalidates the result hash.

---

## 18. Infeasibility explanations

A major product goal is not only to prove infeasibility but to explain it.

Suppose

\[
A\land B\land C\land D
\]

is infeasible.

RoboCert should attempt to identify a small conflicting subset, e.g.

\[
A\land B\land C
\]

already infeasible.

Engineering output might then state:

> The required tool pose cannot be achieved while simultaneously satisfying the shoulder joint limit, the 12 mm fixture clearance, and the specified wrist singularity margin.

The explanation is secondary to the mathematical proof: an explanation must be derived from a checked infeasibility result rather than generated speculatively.

---

## 19. Method-selection strategy

No single method will scale across all RoboCert problems.

A proposed hierarchy is:

```text
1. Normalize and simplify the problem.
2. Search aggressively for counterexamples.
3. Detect exploitable structure.
4. Choose one or more certification backends.
5. Construct candidate certificates.
6. Check them independently.
7. Decompose the domain if global certification fails.
8. Return certified subregions + unresolved region.
```

Possible routing rules:

### Low-dimensional polynomial system

Prefer:

- Gröbner bases;
- comprehensive Gröbner systems;
- real root isolation;
- quantifier elimination.

### Moderate-dimensional polynomial inequality

Prefer:

- SOS/SDP;
- sparse polynomial optimization;
- interval validation.

### Box uncertainty

Prefer:

- interval arithmetic;
- branch-and-bound;
- SOS relaxations where useful.

### Collision-free C-space region

Prefer:

- C-IRIS-style convex certification where assumptions fit;
- conservative geometry decomposition;
- independent validation of region certificates.

### High-dimensional difficult problem

Use a hybrid:

\[
\text{sampling/NLP}
\rightarrow
\text{candidate decomposition}
\rightarrow
\text{local rigorous certification}.
\]

Sampling may guide the proof search but may not substitute for the proof.

---

## 20. Domain decomposition

Global certification over a large nonconvex configuration space may be intractable.

RoboCert should therefore treat decomposition as a first-class technique.

Given \(Q\),

\[
Q=R_1\cup\cdots\cup R_N\cup U,
\]

where each \(R_i\) is certified and \(U\) remains unresolved.

The output may report:

\[
R_{\mathrm{cert}}
=
\bigcup_{i=1}^N R_i
\]

and explicitly retain the residual set \(U\).

This supports an anytime workflow without sacrificing logical soundness:

- certified regions stay certified;
- unresolved regions stay unresolved.

---

## 21. Proof obligations for geometry approximation

If a true CAD body \(\mathcal B\) is replaced by an approximate body \(\widehat{\mathcal B}\), the approximation relation must be explicit.

For conservative collision safety, an outer approximation should satisfy

\[
\mathcal B\subseteq\widehat{\mathcal B}.
\]

If RoboCert certifies

\[
\widehat{\mathcal B}_1(q)
\cap
\widehat{\mathcal B}_2
=
\varnothing
\]

for all \(q\in R\), then collision freedom transfers to the contained true bodies.

By contrast, an inner approximation is generally unsafe for collision-exclusion claims.

This kind of containment proof is part of the certificate chain.

---

## 22. Numerical policy

The project should maintain an explicit hierarchy of numerical trust.

### Level 0 — ordinary floating point

Useful for search only.

### Level 1 — high precision

Useful for conditioning and reconstruction, but not automatically rigorous.

### Level 2 — interval / directed rounding

Suitable for validated inequalities and enclosures.

### Level 3 — exact rational / algebraic arithmetic

Preferred for final checking when computationally practical.

A displayed value such as

\[
1.0\times10^{-12}
\]

must never be interpreted as zero solely because it is small.

---

## 23. Benchmark problems

The first benchmarks should be deliberately small enough that independent methods can cross-check one another.

### Benchmark A — planar 2R manipulator

Certify:

- a rectangular reachable task region;
- joint limits;
- obstacle avoidance;
- distance from kinematic singularity.

Use both:

- exact real algebraic methods;
- interval subdivision.

### Benchmark B — planar 3R manipulator

Add:

- redundancy;
- obstacle interactions;
- quantifier structure
  \[
  \forall x\exists q.
  \]

### Benchmark C — 3-DOF spatial chain

Test:

- Gröbner/QE trajectory certification;
- parametric task path;
- exact branch transitions.

### Benchmark D — 6-DOF industrial arm

Certify local regions using:

- C-IRIS-style collision certificates;
- SOS singularity margins;
- interval verification of joint/tolerance constraints.

### Benchmark E — 6/7-DOF arm with tolerances

Add:

- link-length tolerances;
- TCP calibration error;
- obstacle-pose uncertainty;
- robust clearance.

---

## 24. Evaluation metrics

RoboCert must not be evaluated only by runtime.

### Soundness

Number of false certifications:

\[
\boxed{0}
\]

is the mandatory target.

### Coverage

Measure certified volume or task coverage:

\[
\frac{\mu(R_{\mathrm{cert}})}
{\mu(R_{\mathrm{target}})}.
\]

### Conservatism

Estimate the gap between the true safe region and the certified region.

### Certificate generation time

Time to produce a candidate certificate.

### Certificate checking time

The checker should ideally be substantially cheaper than discovery.

### Certificate size

Important for auditability and storage.

### Robustness width

Maximum tolerances for which a certificate remains valid.

### Independent agreement

For small benchmarks, compare:

- QE;
- interval methods;
- SOS;
- exhaustive high-resolution sampling.

Sampling is used as a diagnostic cross-check, not as the source of truth.

---

## 25. Testing philosophy

RoboCert should have three testing layers.

### Unit tests

For:

- polynomial transformations;
- frame transformations;
- tangent-half-angle conversions;
- interval operations;
- certificate serialization.

### Property tests

Examples:

- generated polynomial kinematics agree with numerical forward kinematics at randomly selected nonsingular points;
- certified outer geometry contains sampled points from the source geometry;
- certificate checker rejects deliberately corrupted certificates.

### Adversarial certification tests

Inject:

- near-contact geometries;
- near-singular configurations;
- degenerate polynomial systems;
- nearly dependent constraints;
- narrow feasible corridors;
- very small tolerance margins.

The system should become more conservative or return `UNKNOWN`, not silently become unsound.

---

## 26. Reproducibility

Every run should record:

- exact input-file hashes;
- solver versions;
- checker versions;
- tolerance parameters;
- random seeds used for search;
- arithmetic precision;
- problem formulation;
- quantifier ordering;
- certificate artifact;
- final checker result.

A certified statement should be reproducible independently of the explanatory AI layer.

---

## 27. Security and safety boundary

RoboCert certificates are statements about mathematical models.

They do not automatically certify:

- controller implementation;
- PLC logic;
- network behavior;
- sensor faults;
- actuator failures;
- unmodeled elasticity;
- human behavior;
- dynamic obstacles;
- electrical safety;
- functional-safety compliance.

A future safety case may incorporate RoboCert results, but RoboCert should not claim compliance with industrial functional-safety standards merely because a geometric theorem has been proved.

---

## 28. Non-goals

At least initially, RoboCert is **not** intended to be:

- a general-purpose CAD editor;
- a replacement for Drake, ROS, MoveIt, Gazebo, or MuJoCo;
- an LLM-based robot controller;
- a generic physics simulator;
- a black-box trajectory generator;
- a substitute for hardware validation;
- a guarantee about phenomena omitted from the mathematical model.

---

## 29. Research questions

The project is driven by several open-ended research questions.

### RQ1 — scalable semialgebraic compilation

How can industrial robot/CAD constraints be compiled into polynomial or rational form without excessive degree growth?

### RQ2 — representation selection

When should a constraint be represented:

- exactly algebraically;
- by a convex relaxation;
- by intervals;
- by conservative geometric envelopes?

### RQ3 — quantifier scalability

How far can practical real quantifier elimination be pushed for low- and medium-DOF robot families?

### RQ4 — hybrid certification

Can candidate regions generated by sampling/NLP be decomposed and certified by exact/SOS/interval methods efficiently?

### RQ5 — robust manufacturing certificates

Can tolerances be propagated symbolically enough to certify useful industrial margins without catastrophic conservatism?

### RQ6 — minimal trusted kernel

Can the majority of solver infrastructure be removed from the trusted computing base by exporting compact proof objects?

### RQ7 — explanatory infeasibility

Can algebraic/optimization certificates be converted into useful minimal engineering conflict explanations?

### RQ8 — certified geometry conversion

How can B-Rep and mesh input be converted into conservative polynomial/convex representations with quantified approximation error?

---

## 30. Initial repository structure

```text
robocert/
├── README.md
├── docs/
│   ├── mathematics/
│   ├── architecture/
│   ├── certificates/
│   └── benchmarks/
├── schemas/
│   ├── project.schema.json
│   ├── claim.schema.json
│   └── certificate.schema.json
├── src/
│   └── robocert/
│       ├── model/
│       ├── geometry/
│       ├── algebra/
│       ├── specification/
│       ├── search/
│       ├── certification/
│       │   ├── qe/
│       │   ├── sos/
│       │   ├── interval/
│       │   └── cspace/
│       ├── checking/
│       ├── diagnostics/
│       └── reporting/
├── tests/
│   ├── unit/
│   ├── property/
│   └── adversarial/
├── benchmarks/
│   ├── planar_2r/
│   ├── planar_3r/
│   ├── spatial_3dof/
│   ├── industrial_6dof/
│   └── robust_7dof/
└── certificates/
```

---

## 31. Development roadmap

### Phase 0 — mathematical specification

Deliverables:

- formal claim language;
- quantifier semantics;
- result status taxonomy;
- certificate interface;
- assumptions/provenance format.

**Exit criterion:** the meaning of `CERTIFIED_FEASIBLE` is mathematically unambiguous.

### Phase 1 — planar exact prototype

Robot:

- 2R / 3R planar manipulator.

Capabilities:

- polynomialized kinematics;
- exact joint limits;
- analytic obstacles;
- Gröbner/QE backend;
- interval checker;
- exact counterexamples.

**Exit criterion:** at least two independent rigorous methods agree on benchmark certificates.

### Phase 2 — polynomial optimization prototype

Add:

- SOS certificates;
- SDP backend;
- rational reconstruction;
- validated certificate checker;
- singularity-margin certificates.

### Phase 3 — C-space collision regions

Integrate:

- Drake robot models;
- C-IRIS-style certified regions;
- conservative geometry conversion;
- region serialization.

### Phase 4 — robust tolerances

Add:

- \(\theta\)-parameterized models;
- interval uncertainty;
- robust collision margins;
- calibration/manufacturing uncertainty.

### Phase 5 — industrial CAD ingestion

Add:

- STEP/B-Rep pipelines;
- certified convex/outer approximations;
- tool/workstation assemblies;
- provenance hashes.

### Phase 6 — continuous task certification

Add:

- line/spline task paths;
- pointwise vs continuous-lift semantics;
- certified path families;
- connected safe-region reasoning.

### Phase 7 — multi-agent orchestration

Add agents only after deterministic mathematical APIs exist.

The agent layer should consume the formal APIs rather than define their semantics.

### Phase 8 — dynamics

Possible future extension:

\[
M(q)\ddot q+C(q,\dot q)\dot q+g(q)=\tau
\]

with certified:

- torque feasibility;
- invariant sets;
- control-barrier conditions;
- robust dynamic reachability.

---

## 32. First minimal viable theorem

The first serious RoboCert milestone should not be "import a 6-DOF robot."

It should be a theorem small enough to audit completely.

For example:

> Given a planar 2R robot with interval link-length tolerances, rectangular joint limits, a circular obstacle, and a rectangular task region \(T\), certify that every task point \(x\in T\) has at least one collision-free inverse-kinematics solution satisfying a specified singularity margin for every admissible link realization.

Formally:

\[
\forall \theta\in\Theta\;
\forall x\in T\;
\exists q\in Q:
F(q,\theta)=x
\land
C(q,\theta)
\land
S(q,\theta).
\]

This benchmark already exercises:

- quantifier alternation;
- real algebraic geometry;
- robust uncertainty;
- IK;
- collision;
- singularity avoidance;
- certificate generation;
- independent checking.

That is a meaningful foundation for the larger system.

---

## 33. Research foundations

RoboCert is motivated by, but not limited to, several strands of recent research.

### C-IRIS

**A. Amice, H. Dai, P. Werner, A. Zhang, R. Tedrake.**  
*Finding and Optimizing Certified, Collision-Free Regions in Configuration Space for Robot Manipulators.*  
Introduces C-IRIS, using convex optimization to construct collision-free polytopes in a rational parameterization of robot configuration space.

- https://arxiv.org/abs/2205.03690

### Certified polyhedral decompositions

**H. Dai, A. Amice, P. Werner, A. Zhang, R. Tedrake.**  
*Certified Polyhedral Decompositions of Collision-Free Configuration Space.*  
Develops certified C-space decomposition and reports implementations for manipulators including KUKA iiwa, UR3e, and bimanual systems.

- https://arxiv.org/abs/2302.12219

### Drake C-space certification implementation

Drake currently exposes `CspaceFreePolytope` and associated separation-certificate machinery for C-IRIS-style certification.

- https://drake.mit.edu/doxygen_cxx/classdrake_1_1geometry_1_1_optimization_1_1_cspace_free_polytope.html
- https://drake.mit.edu/doxygen_cxx/group__planning__iris.html

### Real quantifier elimination for robot trajectory certification

**Y. Nakai, A. Terui, M. Mikawa.**  
*Trajectory Planning and Certification for 3-DOF Robot Manipulators Using Real Quantifier Elimination Based on Comprehensive Gröbner Systems.*  
Uses real quantifier elimination based on comprehensive Gröbner systems to certify inverse-kinematic solution existence along parameterized trajectories.

- https://arxiv.org/abs/2607.11657

### Verified task-space reachability under joint constraints

**H. Hu, C. Liu, Y. Wang.**  
*Verified Task-Space Motion Planning Under Joint-Space Constraints.*  
Uses SOS/S-procedure ideas to compute certifiably reachable local task-space regions under bounded joint displacement.

- https://arxiv.org/abs/2605.22991

### IRIS-NP as a non-rigorous candidate-region generator

**M. Petersen, R. Tedrake.**  
*Growing Convex Collision-Free Regions in Configuration Space using Nonlinear Programming.*  
Provides a faster probabilistic alternative to rigorous C-IRIS and can serve as an initializer for subsequent certification.

- https://arxiv.org/abs/2303.14737

RoboCert should preserve the conceptual distinction between:

\[
\text{probabilistic / sampled evidence}
\quad\text{and}\quad
\text{rigorous certification}.
\]

---

## 34. Terminology

### Certified

A claim for which RoboCert possesses a certificate accepted by the corresponding deterministic checker under the recorded assumptions.

### Verified

Reserved for a property independently checked by a sound verification procedure. Documentation should avoid using *verified* as a synonym for *tested*.

### Reachable

Must specify whether this means:

- pointwise IK existence;
- robust IK existence;
- path-connected reachability;
- dynamically reachable.

### Collision-free

Must specify:

- geometry representation;
- uncertainty model;
- required clearance;
- whether the guarantee is pointwise, regional, or trajectory-wide.

### Singularity-free

Must specify:

- Jacobian definition;
- rank criterion;
- numerical/algebraic margin.

---

## 35. Contributing

RoboCert particularly needs contributors with expertise in:

1. computational real algebraic geometry;
2. robot kinematics and mechanism theory;
3. polynomial optimization and SOS/SDP;
4. certified numerics and interval arithmetic;
5. computational geometry and collision certification;
6. formal methods and proof checking;
7. robust optimization and uncertainty quantification;
8. global nonlinear optimization;
9. symbolic-numeric computation;
10. scientific-computing and solver engineering;
11. CAD kernels and geometric modeling;
12. motion planning and configuration-space topology.

Contributions that improve certificate soundness, independent checking, and model transparency take priority over UI or agent autonomy.

---

## 36. Scientific standard

A RoboCert publication or benchmark claiming a certified property should provide enough information for an independent group to reconstruct the statement:

\[
(\text{model},\text{domain},\text{quantifiers},\text{assumptions},\text{certificate})
\]

and rerun the checker.

The project should treat reproducibility and falsifiability as design requirements, not documentation afterthoughts.

---

## 37. Project philosophy

The defining idea of RoboCert is simple:

> **Search may be heuristic. Certification may not be.**

Fast robot software can propose configurations, paths, decompositions, candidate safe regions, and candidate proofs.

RoboCert's purpose is to determine which of those candidates support a mathematically valid statement over the entire specified domain.

The long-term objective is therefore:

\[
\boxed{
\text{CAD + robotics + real algebraic geometry + certified numerics}
\longrightarrow
\text{auditable engineering guarantees}
}
\]

rather than merely

\[
\boxed{
\text{CAD + simulation}
\longrightarrow
\text{successful sampled trajectories}.
}
\]

---

## License

**TBD.**

Before accepting substantial external contributions, the project should choose an explicit open-source license and contribution policy compatible with all solver and CAD dependencies.

---

## Disclaimer

RoboCert is a research project. A mathematical certificate is valid only with respect to its formal model and stated assumptions. Deployment on physical robotic systems requires independent engineering validation, appropriate safety analysis, and compliance with applicable laws, standards, and industrial safety requirements.
