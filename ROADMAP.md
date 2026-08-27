# ROADMAP.md — RoboCert Research and Development Roadmap

> **Project:** RoboCert  
> **Objective:** Mathematical certification of robot reachability, collision freedom, singularity separation, and feasibility under geometric, calibration, and manufacturing uncertainty.
>
> **Audience:** researchers and engineers in computational real algebraic geometry, robot kinematics, polynomial optimization, certified numerics, computational geometry, formal verification, and scientific software.
>
> **Status:** research roadmap; milestones are gated by mathematical soundness, reproducibility, and independently checkable certificates.

---

# 0. Governing Principle

RoboCert exists to distinguish:

\[
\boxed{
\text{empirical evidence}
\neq
\text{mathematical certificate}
}
\]

and:

\[
\boxed{
\text{candidate solution}
\neq
\text{certified theorem}
}
\]

The project therefore prioritizes:

1. soundness;
2. precise formal semantics;
3. independently checkable certificates;
4. reproducibility;
5. useful certified coverage;
6. computational performance;
7. automation and user experience.

This ordering is deliberate.

A faster solver that weakens soundness is a regression.

A broader feature set without certificate semantics is not progress toward the core objective.

---

# 1. Long-Term Research Goal

Given:

- a robot model;
- tool geometry;
- workstation CAD;
- obstacles;
- required task poses or task regions;
- joint limits;
- manufacturing tolerances;
- calibration uncertainty;
- safety margins;

RoboCert should be able to formulate and attempt to certify claims of the form

\[
\forall\theta\in\Theta\;
\forall x\in T\;
\exists q\in R:
J(q)
\land
K(q,\theta,x)
\land
C(q,\theta)
\land
S(q,\theta),
\]

where:

- \(q\) denotes robot configuration;
- \(\theta\) denotes uncertain geometric/calibration parameters;
- \(x\) denotes task parameters;
- \(J(q)\) denotes joint-limit constraints;
- \(K(q,\theta,x)\) denotes task/kinematic constraints;
- \(C(q,\theta)\) denotes collision or clearance constraints;
- \(S(q,\theta)\) denotes singularity-separation constraints.

RoboCert should also certify infeasibility when possible:

\[
\nexists q,\theta,x
\quad
\text{such that all required constraints hold},
\]

or equivalently prove emptiness of a corresponding semialgebraic set.

The project should support both:

\[
\text{certified feasible regions}
\]

and:

\[
\text{certified infeasible problem instances}.
\]

---

# 2. Core Research Thesis

The project is based on the thesis that industrial robot feasibility and safety questions can be decomposed into a hierarchy of mathematically tractable subproblems involving:

- semialgebraic sets;
- real algebraic geometry;
- polynomial systems;
- Gröbner bases;
- elimination theory;
- real quantifier elimination;
- cylindrical algebraic decomposition;
- Positivstellensatz certificates;
- sum-of-squares relaxations;
- semidefinite programming;
- validated numerics;
- interval methods;
- exact arithmetic;
- computational geometry;
- configuration-space decomposition.

No single method is expected to solve all industrial instances.

RoboCert is therefore a **hybrid certification architecture**.

The intended flow is:

\[
\text{engineering model}
\rightarrow
\text{formal claim}
\rightarrow
\text{candidate generation}
\rightarrow
\text{certificate construction}
\rightarrow
\text{independent checking}.
\]

---

# 3. Principal Research Workstreams

RoboCert development is organized around ten coupled workstreams.

## WS1 — Formal specification and quantifier semantics

Research questions:

- How should reachability, robust feasibility, and continuous-lift claims be serialized?
- How should quantifier dependencies be represented?
- How should strict inequalities and safety margins be modeled?
- How should uncertainty semantics be encoded?

Key output:

\[
\boxed{\text{FormalClaim}}
\]

with immutable semantics.

---

## WS2 — Computational real algebraic geometry

Research questions:

- Which robot kinematic formulations minimize polynomial degree?
- When should tangent-half-angle substitutions be used?
- Which Gröbner orderings are effective for robot systems?
- When does elimination preserve enough real structure?
- How far can exact real quantifier elimination scale?

Key techniques:

- Gröbner bases;
- elimination ideals;
- subresultants;
- comprehensive Gröbner systems;
- discriminant varieties;
- real root isolation;
- CAD/QE.

---

## WS3 — Polynomial optimization and positivity certificates

Research questions:

- Which safety inequalities admit useful SOS certificates?
- How should sparse SOS be exploited for serial manipulators?
- How should SDP solutions be rationally reconstructed and checked?
- Which Positivstellensatz formulations give useful infeasibility certificates?

Key techniques:

- SOS;
- SDP;
- moment relaxations;
- sparse/chordal polynomial optimization;
- rational reconstruction.

---

## WS4 — Certified numerics and interval methods

Research questions:

- Which interval formulations scale for robust collision and IK verification?
- How should interval Newton/Krawczyk be integrated with symbolic preprocessing?
- Which branch-and-bound strategies minimize unresolved volume?

Key techniques:

- outward-rounded interval arithmetic;
- interval Newton;
- Krawczyk operators;
- validated branch-and-bound;
- exact/interval hybrid checking.

---

## WS5 — Robot kinematics and singularity theory

Research questions:

- How should singularity notions be formalized across manipulator families?
- Which algebraic surrogates are sufficient for margin certification?
- How should redundant manipulators be handled?
- How should continuous task-space lifting be certified?

Key objects:

- forward kinematics;
- inverse kinematics;
- Jacobians;
- rank strata;
- configuration-space topology;
- connected safe regions.

---

## WS6 — Computational geometry and collision certification

Research questions:

- How should CAD geometry be converted into conservative certifiable representations?
- Which primitive/convex approximations minimize conservatism?
- How can C-space collision certificates be independently checked?
- How should geometry approximation error propagate into clearance margins?

Key techniques:

- convex decomposition;
- outer geometry approximations;
- separating planes/polynomials;
- configuration-space region certification;
- exact geometric predicates.

---

## WS7 — Robustness and manufacturing uncertainty

Research questions:

- How should dimensional tolerances, calibration error, and TCP uncertainty be represented?
- Which uncertainty sets are computationally tractable?
- When does interval uncertainty become too conservative?
- Can robust region certificates exploit parameter structure?

Key claims:

\[
\forall\theta\in\Theta
\]

rather than nominal-only statements.

---

## WS8 — Certificate format and trusted checker

Research questions:

- Which certificate types can be independently checked?
- How small can the trusted computing base be?
- Which parts of the geometry pipeline must be trusted?
- Can solver-specific proof objects be normalized into RoboCert-native formats?

Key output:

\[
\boxed{\text{CheckedCertificate}}
\]

which alone can support `CERTIFIED_*`.

---

## WS9 — Scientific computing and solver engineering

Research questions:

- How should exact, interval, symbolic, and floating-point backends interoperate?
- How should caching and parallelism preserve proof semantics?
- How should decomposition be distributed?
- How should solver failures map into RoboCert statuses?

Key requirement:

performance optimization must never weaken soundness.

---

## WS10 — Multi-agent orchestration and explanation

Research questions:

- Which mathematical backends should agents invoke for which problem structures?
- How can agents propose formulations without changing theorem semantics?
- How can infeasibility certificates be converted into useful engineering explanations?

Key rule:

\[
\text{LLM orchestration}
\notin
\text{trusted proof boundary}.
\]

---

# 4. Phase Structure

The roadmap is divided into ten major phases.

Each phase has:

- a mathematical objective;
- software deliverables;
- benchmark deliverables;
- certificate deliverables;
- exit criteria.

A phase is complete only when its exit criteria are satisfied.

---

# Phase 0 — Formal Semantics and Certification Kernel

## Objective

Define precisely what RoboCert means by:

- feasible;
- infeasible;
- certified;
- reachable;
- collision-free;
- singularity-separated;
- robust;
- continuous-path feasible;
- unknown.

This phase precedes serious solver integration.

---

## 0.1 Formal claim schema

Implement a typed claim representation containing:

```text
Variables
Domains
QuantifierPrefix
Predicates
Margins
Assumptions
UncertaintySemantics
GeometrySemantics
Provenance
```

Example:

\[
\forall\theta\in\Theta\;
\forall x\in T\;
\exists q\in Q:
\Phi(q,\theta,x).
\]

Quantifier order MUST be immutable after claim construction unless a new claim is created.

---

## 0.2 Result semantics

Implement normative result classes:

```text
CERTIFIED_FEASIBLE
CERTIFIED_INFEASIBLE
COUNTEREXAMPLE
NUMERICALLY_FEASIBLE
NUMERICALLY_INFEASIBLE
UNKNOWN
```

No solver adapter may emit `CERTIFIED_*` directly.

---

## 0.3 Certificate interface

Define a common interface:

```text
Certificate
Checker
CheckedCertificate
```

Certificate requirements:

- claim hash;
- model hash;
- assumptions;
- certificate family;
- payload;
- checker version;
- arithmetic mode;
- provenance.

---

## 0.4 Trusted-computing-base document

Document which components are trusted for each certificate family.

Example:

```text
candidate SOS solver: untrusted
rational reconstruction: untrusted
exact polynomial identity checker: trusted
validated PSD checker: trusted
```

---

## 0.5 Exit criteria

Phase 0 is complete when:

The functional Phase 0 exit criteria below are implemented and covered by the
current test suite. This engineering milestone does not approve a production
certificate backend and does not mark Phase 1 complete; production results stay
`UNKNOWN` while the evidence gates remain closed.

- [x] claim schema exists;
- [x] result semantics exist;
- [x] hash binding exists;
- [x] checker interface exists;
- [x] no code path can bypass checker promotion;
- [x] quantifier-reordering tests exist;
- [x] strict-vs-weak inequality tests exist;
- [x] corrupted-certificate tests exist.

---

# Phase 1 — Exact Planar 2R Certification

## Objective

Construct the first theorem-level end-to-end RoboCert pipeline.

Use a planar two-revolute-joint robot because the system is small enough for independent analytic validation.

---

## 1.1 Model

Let:

\[
q=(q_1,q_2),
\]

with uncertain link lengths:

\[
L_i\in[L_i^-,L_i^+].
\]

Forward kinematics:

\[
x=
L_1\cos q_1+
L_2\cos(q_1+q_2),
\]

\[
y=
L_1\sin q_1+
L_2\sin(q_1+q_2).
\]

Use tangent-half-angle variables:

\[
t_i=\tan\frac{q_i}{2}.
\]

Derive exact rational/polynomial constraints.

---

## 1.2 Required properties

The benchmark must combine:

- joint limits;
- one analytic obstacle;
- task-region reachability;
- singularity separation;
- interval link-length uncertainty.

Target theorem:

\[
\forall\theta\in\Theta\;
\forall x\in T\;
\exists q\in Q:
K(q,\theta,x)
\land
C(q,\theta)
\land
S(q,\theta).
\]

---

## 1.3 Exact backend

Implement at least one exact route using:

- Gröbner elimination;
- real root isolation;
- QE/CAD;
- or equivalent exact real algebraic computation.

---

## 1.4 Interval backend

Implement a second rigorous route using:

- interval subdivision;
- interval kinematics;
- interval Jacobian bounds;
- validated obstacle separation.

---

## 1.5 Cross-validation

The exact and interval methods should agree on small benchmark instances.

Disagreement triggers investigation before proceeding.

---

## 1.6 Exit criteria

- [ ] complete 2R formal model;
- [ ] exact polynomialization tested;
- [ ] chart-boundary handling tested;
- [ ] exact or validated reachability certificate;
- [ ] exact or validated obstacle certificate;
- [ ] singularity-margin certificate;
- [ ] interval uncertainty support;
- [ ] independent checker;
- [ ] complete reproducibility from clean environment.

---

# Phase 2 — Planar 3R and Quantifier Alternation

## Objective

Move from isolated feasible sets to redundancy and task-region quantification.

Target:

\[
\forall x\in T\;\exists q\in Q.
\]

This phase tests genuine quantified reasoning.

---

## 2.1 New challenges

- redundancy;
- multiple IK branches;
- disconnected feasible sets;
- branch transitions;
- nontrivial obstacle constraints;
- larger elimination systems.

---

## 2.2 Research targets

Evaluate:

- variable ordering sensitivity;
- comprehensive Gröbner systems;
- discriminant-based parameter decomposition;
- CAD projection ordering;
- interval decomposition over task regions.

---

## 2.3 Continuous-lift distinction

Add separate claims for:

### Pointwise reachability

\[
\forall s\;\exists q_s.
\]

### Continuous path lift

\[
\exists q(\cdot)\;\forall s.
\]

Do not conflate them.

---

## 2.4 Exit criteria

- [ ] pointwise task-region certification;
- [ ] branch-aware IK representation;
- [ ] certified detection of unreachable subregions;
- [ ] explicit distinction between pointwise and continuous feasibility;
- [ ] at least one benchmark where pointwise reachability holds but continuous-lift constraints are nontrivial.

---

# Phase 3 — SOS/SDP Certification Backend

## Objective

Introduce scalable positivity certificates for polynomial inequalities.

---

## 3.1 Core functionality

Given:

\[
K=\{x:g_i(x)\ge0,\ h_j(x)=0\},
\]

attempt to certify:

\[
p(x)\ge\gamma>0
\quad\forall x\in K.
\]

---

## 3.2 Required components

- polynomial model export;
- SOS formulation;
- SDP solver adapter;
- Gram-matrix extraction;
- rational reconstruction;
- exact identity checking;
- validated PSD checking.

---

## 3.3 Certificate semantics

A numerical SDP solution is only a candidate.

The final certificate should contain data sufficient to validate:

\[
p-\gamma
=
\sigma_0+
\sum_i\sigma_i g_i+
\sum_j\lambda_j h_j.
\]

---

## 3.4 Sparse structure

Investigate:

- correlative sparsity;
- chordal decomposition;
- term sparsity;
- structured kinematic polynomial systems.

---

## 3.5 Exit criteria

- [ ] exact/validated SOS certificate checker;
- [ ] rational reconstruction pipeline;
- [ ] singularity-margin SOS benchmark;
- [ ] collision-separation SOS benchmark;
- [ ] checker rejects perturbed Gram matrices;
- [ ] solver failure maps to `UNKNOWN`.

---

# Phase 4 — Certified Configuration-Space Collision Regions

## Objective

Move from pointwise collision checking to certified regions in configuration space.

---

## 4.1 Initial geometry classes

Support:

- spheres;
- capsules;
- boxes;
- cylinders;
- convex polytopes.

---

## 4.2 C-space region certificates

Integrate C-IRIS-style reasoning where appropriate.

The project should distinguish:

```text
candidate region
certified region
unresolved region
```

---

## 4.3 Independent validation

Where possible, retain:

- separating plane/polynomial data;
- pairwise geometry constraints;
- region inequalities;
- exact/validated certificate data.

---

## 4.4 Domain decomposition

Represent:

\[
Q=
R_1\cup\cdots\cup R_N\cup U,
\]

where:

- \(R_i\) are certified;
- \(U\) is unresolved.

---

## 4.5 Exit criteria

- [ ] certified collision-free convex region;
- [ ] explicit clearance margin;
- [ ] deterministic checker;
- [ ] unresolved-region preservation;
- [ ] adversarial near-contact benchmark;
- [ ] comparison against dense collision sampling as a diagnostic only.

---

# Phase 5 — Robust Manufacturing and Calibration Tolerances

## Objective

Elevate RoboCert from nominal geometry to bounded uncertainty.

---

## 5.1 Uncertainty classes

Support at least:

- interval/box uncertainty;
- polyhedral uncertainty;
- ellipsoidal uncertainty;
- basic semialgebraic uncertainty.

---

## 5.2 Initial uncertain parameters

Include:

- link lengths;
- joint-axis offsets;
- tool-center-point position;
- tool-center-point orientation;
- fixture pose;
- obstacle pose;
- calibration error.

---

## 5.3 Robust claim classes

### Adjustable feasibility

\[
\forall\theta\in\Theta\;\exists q.
\]

### Static robust feasibility

\[
\exists q\;\forall\theta\in\Theta.
\]

### Robust task-region feasibility

\[
\forall\theta\in\Theta\;
\forall x\in T\;
\exists q.
\]

---

## 5.4 Research targets

Compare:

- interval propagation;
- SOS robustification;
- QE;
- decomposition in parameter space;
- monotonicity-based reduction where provable.

---

## 5.5 Exit criteria

- [ ] uncertainty schema;
- [ ] robust 2R benchmark;
- [ ] robust 3R benchmark;
- [ ] calibration-error benchmark;
- [ ] counterexample generation for tolerance-induced failure;
- [ ] no vertex-only approximation unless mathematically justified.

---

# Phase 6 — Industrial 6-DOF Local Certification

## Objective

Demonstrate useful local certification on a standard industrial manipulator.

Global exact QE is not the target.

The goal is hybrid certification.

---

## 6.1 Candidate workflow

\[
\text{sampling/NLP}
\rightarrow
\text{candidate region}
\rightarrow
\text{rigorous local certification}.
\]

---

## 6.2 Model support

Integrate:

- URDF;
- Drake multibody model;
- collision geometry;
- tool frame;
- joint limits.

---

## 6.3 Target certificates

At least:

- local collision-free C-space region;
- joint-limit margin;
- local singularity margin;
- one task pose or task neighborhood;
- optional tolerance set.

---

## 6.4 Benchmark families

Candidate robots:

- UR3e;
- UR5e;
- KUKA iiwa;
- Franka Emika Panda;
- equivalent open model.

---

## 6.5 Exit criteria

- [ ] imported industrial robot;
- [ ] local certified region;
- [ ] checked collision certificate;
- [ ] checked singularity-margin certificate;
- [ ] end-to-end report with model hashes;
- [ ] replayable certificate check without rerunning search.

---

# Phase 7 — CAD/B-Rep Ingestion and Conservative Geometry Compilation

## Objective

Connect industrial CAD to certification-compatible geometry.

This phase is essential for commercial relevance.

---

## 7.1 Input formats

Prioritize:

- STEP;
- B-Rep;
- standard CAD assemblies;
- optionally meshes.

---

## 7.2 Geometry normalization

Implement:

- unit normalization;
- frame extraction;
- topology validation;
- healing with provenance;
- convex decomposition;
- conservative outer approximation.

---

## 7.3 Mathematical contract

For a true body \(\mathcal B\), construct:

\[
\mathcal B
\subseteq
\widehat{\mathcal B}_{\mathrm{outer}}.
\]

Record approximation error.

---

## 7.4 Research targets

Investigate:

- certified convex hull/envelope methods;
- algebraic proxy surfaces;
- exact primitive recognition;
- NURBS-to-conservative approximation;
- mesh enclosure guarantees.

---

## 7.5 Exit criteria

- [ ] STEP ingestion;
- [ ] unit/frame provenance;
- [ ] conservative geometry representation;
- [ ] approximation-bound artifact;
- [ ] collision certificate using converted CAD;
- [ ] regression test for geometry-healing changes.

---

# Phase 8 — Continuous Task and Path Certification

## Objective

Move beyond isolated task poses.

Certify continuous task execution properties.

---

## 8.1 Task classes

Support:

- Cartesian line segment;
- circular arc;
- spline;
- orientation cone;
- continuous pose tube.

---

## 8.2 Distinct claims

### Pointwise task feasibility

\[
\forall s\in[0,1]\;\exists q_s.
\]

### Continuous lift

\[
\exists q:[0,1]\to Q
\quad
\forall s:
F(q(s))=x(s).
\]

### Safe continuous lift

\[
\exists q(\cdot)
\quad
\forall s:
C(q(s))\land S(q(s)).
\]

---

## 8.3 Research targets

Investigate:

- connected certified C-space regions;
- branch continuation;
- topological obstruction detection;
- path lifting through certified cells;
- graph of certified regions.

---

## 8.4 Exit criteria

- [ ] continuous task specification;
- [ ] certified piecewise-connected path through certified regions;
- [ ] explicit distinction between pointwise and continuous feasibility;
- [ ] benchmark with branch transition;
- [ ] counterexample when continuous lift fails.

---

# Phase 9 — Certified Infeasibility and Minimal Conflict Analysis

## Objective

Make negative answers as valuable as positive ones.

Target:

> No feasible configuration exists because constraints A, B, and C are mutually inconsistent.

---

## 9.1 Infeasibility certificate families

Support:

- exact real algebraic contradiction;
- Positivstellensatz refutation;
- validated interval exclusion;
- exact dual certificates where applicable;
- SMT proof objects where available.

---

## 9.2 Minimal conflict extraction

Given:

\[
A\land B\land C\land D
\]

certified infeasible, search for a smaller certified infeasible subset.

---

## 9.3 Engineering explanations

Map formal conflicts back to:

- joint limits;
- fixture clearance;
- task pose;
- singularity margin;
- tolerance assumptions.

---

## 9.4 Exit criteria

- [ ] at least two independent infeasibility certificate families;
- [ ] minimal/small conflict extraction;
- [ ] checked explanation provenance;
- [ ] no heuristic conflict presented as certified.

---

# Phase 10 — Multi-Agent Research Orchestration

## Objective

Introduce autonomous agents only after stable deterministic APIs exist.

---

## 10.1 Agent roles

Implement:

- `SpecificationAgent`;
- `GeometryAgent`;
- `AlgebraAgent`;
- `OptimizationAgent`;
- `IntervalAgent`;
- `CounterexampleAgent`;
- `CertificateAgent`;
- `ExplanationAgent`;
- `SupervisorAgent`.

The checker remains deterministic software.

---

## 10.2 Method planning

The system may choose:

- exact algebra;
- QE;
- SOS;
- interval;
- hybrid decomposition;
- counterexample search.

Method selection itself may be heuristic.

Final certification may not be.

---

## 10.3 Exit criteria

- [ ] agent outputs structured problem specifications;
- [ ] agents cannot mutate certified claim semantics;
- [ ] agents cannot bypass checker;
- [ ] agent-generated derivations are independently validated;
- [ ] complete provenance for every tool invocation affecting proof artifacts.

---

# 5. Cross-Cutting Stage Gates

Every phase must pass the following gates.

---

## Gate A — Semantic correctness

Questions:

- Are quantifiers correct?
- Are strict inequalities preserved?
- Are uncertainty semantics correct?
- Are units and frames explicit?
- Is the exact theorem statement serialized?

Failure blocks promotion.

---

## Gate B — Mathematical soundness

Questions:

- Is the certificate family mathematically appropriate?
- Are all theorem assumptions recorded?
- Are denominator conditions included?
- Are geometric approximations conservative in the correct direction?
- Are numerical bounds rigorous?

Failure blocks promotion.

---

## Gate C — Independent checkability

Questions:

- Can a deterministic checker validate the certificate?
- Is checking possible without rerunning the candidate generator?
- Is the certificate tied to exact model and claim hashes?

Failure blocks `CERTIFIED_*`.

---

## Gate D — Adversarial robustness

Test:

- near-contact;
- near-singular;
- repeated roots;
- small margins;
- degenerate geometry;
- chart boundaries;
- narrow feasible regions;
- tolerance-induced topology changes.

Unexpected acceptance blocks promotion.

---

## Gate E — Reproducibility

A clean environment must reproduce:

```text
model
+ claim
+ certificate
+ checker
    =>
same checker result
```

---

# 6. Benchmark Ladder

RoboCert should maintain a permanent benchmark ladder.

## Level 1 — 2R planar exact

Purpose:

- analytic auditability;
- exact algebra;
- interval comparison.

---

## Level 2 — 3R planar quantified

Purpose:

- quantifier alternation;
- redundancy;
- branch analysis.

---

## Level 3 — spatial 3-DOF

Purpose:

- nonplanar polynomial systems;
- elimination;
- singularity structure.

---

## Level 4 — 6-DOF local certification

Purpose:

- realistic robot model;
- local C-space certification;
- hybrid methods.

---

## Level 5 — 6/7-DOF robust certification

Purpose:

- tolerances;
- calibration error;
- uncertainty propagation.

---

## Level 6 — CAD workstation

Purpose:

- STEP/B-Rep;
- fixtures;
- tool geometry;
- obstacles.

---

## Level 7 — continuous process path

Purpose:

- welding;
- dispensing;
- scanning;
- machining-like end-effector path constraints.

---

# 7. Quantitative Success Metrics

The project should measure more than runtime.

---

## 7.1 Soundness

Target:

\[
\boxed{0\text{ false certifications}}
\]

across all known benchmark truth sets.

---

## 7.2 Certified coverage

For target region \(R\):

\[
\text{coverage}
=
\frac{\mu(R_{\mathrm{cert}})}
{\mu(R)}.
\]

---

## 7.3 Conservatism

Estimate gap:

\[
R_{\mathrm{cert}}
\subseteq
R_{\mathrm{true}}.
\]

Track how much feasible region is lost to conservative approximation.

---

## 7.4 Certificate size

Measure:

- bytes;
- polynomial terms;
- interval boxes;
- matrix dimensions;
- number of local cells.

---

## 7.5 Check time

A healthy architecture aims for:

\[
T_{\mathrm{check}}
\ll
T_{\mathrm{search}}.
\]

---

## 7.6 Robustness width

Measure largest uncertainty set \(\Theta\) for which certification still succeeds.

---

## 7.7 Explanation quality

For certified infeasibility:

- size of conflict set;
- mapping to engineering constraints;
- reproducibility of explanation.

---

# 8. Research Risk Register

The roadmap must explicitly recognize hard research risks.

---

## Risk R1 — Gröbner/QE explosion

Problem:

Polynomial degree and variable count may become intractable.

Mitigation:

- exploit sparsity;
- eliminate locally;
- decompose parameter space;
- use exact methods only where dimension permits;
- switch to SOS/interval hybrids.

---

## Risk R2 — SOS conservatism

Problem:

Low-order relaxations may fail to certify true positivity.

Mitigation:

- increase degree selectively;
- exploit sparsity;
- domain decomposition;
- use interval verification;
- exactify only successful candidates.

---

## Risk R3 — SDP numerical instability

Problem:

Near-singular Gram matrices may produce unreliable candidate certificates.

Mitigation:

- high precision;
- rational reconstruction;
- exact identity checking;
- validated eigenvalue bounds.

---

## Risk R4 — Interval dependency explosion

Problem:

Intervals may become excessively conservative.

Mitigation:

- symbolic preprocessing;
- coordinate scaling;
- centered forms;
- affine arithmetic where rigorous;
- subdivision;
- hybrid exact/interval methods.

---

## Risk R5 — CAD approximation unsoundness

Problem:

A visually accurate mesh may not provide a safe enclosure.

Mitigation:

- explicit containment semantics;
- certified outer approximation;
- approximation-error artifacts;
- geometry checker.

---

## Risk R6 — Quantifier misinterpretation

Problem:

Engineering requirements may be encoded with the wrong dependency structure.

Mitigation:

- quantifiers displayed in UI;
- immutable claim schema;
- semantic tests;
- explicit adjustable/static robust modes.

---

## Risk R7 — Trusted computing base too large

Problem:

If the full solver stack is trusted, certification loses auditability.

Mitigation:

- proof-carrying architecture;
- small checkers;
- exact/validated rechecking;
- certificate normalization.

---

## Risk R8 — Industrial-scale dimensionality

Problem:

Full global certification for 6/7-DOF workcells may be infeasible.

Mitigation:

- local certified regions;
- domain decomposition;
- candidate generation by heuristics;
- region graphs;
- partial certification with explicit unresolved regions.

---

# 9. Research Publication Plan

RoboCert should produce publishable contributions incrementally.

---

## Paper A — Formal semantics and benchmark suite

Topic:

A formal specification language for certified robot configuration-space claims.

Potential contribution:

- quantifier semantics;
- certificate/result taxonomy;
- benchmark suite.

---

## Paper B — Exact/interval hybrid planar certification

Topic:

Hybrid real-algebraic and interval certification for robust robot reachability.

Potential contribution:

- exact 2R/3R pipeline;
- uncertainty-aware certificates;
- method comparison.

---

## Paper C — Checked SOS certificates for robot safety margins

Topic:

Rationally reconstructed and independently checked SOS certificates for robotic collision/singularity margins.

---

## Paper D — Conservative CAD-to-certificate geometry

Topic:

Certified conversion from CAD/B-Rep to conservative collision representations.

---

## Paper E — Hybrid industrial C-space certification

Topic:

Combining heuristic region discovery with rigorous local certification for 6/7-DOF manipulators.

---

## Paper F — Certified infeasibility explanations

Topic:

Minimal conflict extraction from algebraic/optimization certificates for robot workcell design.

---

# 10. Software Release Plan

Releases should reflect mathematical capability, not just UI features.

---

## `v0.1` — Formal core

Includes:

- claim schema;
- result schema;
- checker interface;
- provenance;
- 2R model.

No industrial claims.

---

## `v0.2` — Exact/interval planar certification

Includes:

- exact 2R certificates;
- interval certificates;
- robust link tolerance.

---

## `v0.3` — Quantified 3R

Includes:

- task-region quantifiers;
- 3R redundancy;
- branch analysis.

---

## `v0.4` — SOS backend

Includes:

- SDP candidate generation;
- rational reconstruction;
- checked positivity certificates.

---

## `v0.5` — Certified C-space regions

Includes:

- primitive collision geometry;
- local certified collision-free regions.

---

## `v0.6` — Robust uncertainty

Includes:

- calibration/tolerance models;
- robust certificates.

---

## `v0.7` — Industrial robot support

Includes:

- URDF/Drake;
- 6-DOF local certification;
- tool frame integration.

---

## `v0.8` — CAD workcells

Includes:

- STEP/B-Rep ingestion;
- conservative geometry compilation.

---

## `v0.9` — Continuous tasks and infeasibility explanations

Includes:

- task paths;
- connected certified region graphs;
- certified conflict explanations.

---

## `v1.0` — Auditable certified robotics platform

Minimum expectations:

- stable formal semantics;
- multiple certificate families;
- deterministic independent checking;
- industrial robot + workcell import;
- robust geometric certification;
- reproducible proof artifacts;
- clear safety/assumption boundaries.

---

# 11. Recommended Expert Ownership

The project should assign principal ownership by discipline.

---

## Computational real algebraic geometry lead

Owns:

- semialgebraic formulation;
- polynomialization;
- Gröbner methods;
- QE/CAD;
- real root isolation;
- algebraic correctness.

This is the most central mathematical role.

---

## Robot kinematics and mechanism theory lead

Owns:

- robot models;
- Jacobians;
- singularities;
- configuration spaces;
- continuous task feasibility;
- branch semantics.

---

## Polynomial optimization lead

Owns:

- SOS;
- SDP;
- Positivstellensatz certificates;
- sparse relaxations;
- exactification.

---

## Certified numerics/formal verification lead

Owns:

- intervals;
- validated linear algebra;
- checkers;
- proof objects;
- trusted computing base.

---

## Computational geometry/CAD lead

Owns:

- B-Rep;
- convex decomposition;
- conservative geometry;
- collision certificate geometry.

---

## Scientific software lead

Owns:

- architecture;
- solver adapters;
- reproducibility;
- performance;
- packaging;
- benchmark infrastructure.

---

# 12. Immediate Next Actions

The project should begin with the following concrete tasks.

---

## Task 1 — freeze claim semantics

Implement:

```text
Claim
Quantifier
Domain
Predicate
Assumption
Margin
UncertaintySet
```

Do this before solver integration.

---

## Task 2 — implement 2R symbolic model

Produce both:

- trigonometric reference model;
- rational/polynomial model.

Cross-check numerically over random nonsingular configurations.

---

## Task 3 — define first certificate format

Start with one simple family:

```text
IntervalBoxCertificate
```

or:

```text
ExactPolynomialCertificate
```

---

## Task 4 — implement first checker

The checker should be independent of the solver.

---

## Task 5 — build first theorem benchmark

Use:

- 2R;
- one circular obstacle;
- joint limits;
- interval link lengths;
- rectangular task region;
- singularity margin.

---

## Task 6 — establish CI soundness tests

CI should reject:

- corrupted certificates;
- hash mismatches;
- quantifier changes;
- dropped unresolved boxes;
- non-rigorous status promotion.

---

# 13. First Twelve Research Milestones

A concrete milestone sequence:

1. **FormalClaim schema**
2. **Result status state machine**
3. **Certificate/checker interface**
4. **2R exact kinematics**
5. **2R interval validator**
6. **2R robust reachability certificate**
7. **3R quantified reachability**
8. **Checked SOS positivity certificate**
9. **Certified C-space collision region**
10. **6-DOF local certification**
11. **STEP/B-Rep conservative geometry**
12. **Certified infeasibility explanation**

Each milestone must include:

- theorem statement;
- implementation;
- certificate artifact;
- checker;
- benchmark;
- reproducibility record.

---

# 14. What Not to Build First

Do not prioritize:

- elaborate GUI;
- cloud orchestration;
- natural-language CAD;
- generative design;
- dynamic simulation;
- RL control;
- digital twins;
- large robot libraries;
- multi-agent autonomy.

These may become valuable later.

They do not establish the core scientific contribution.

The first product must be:

\[
\boxed{
\text{a small problem with a real mathematical certificate}
}
\]

not:

\[
\boxed{
\text{a large system with only numerical evidence}
}
\]

---

# 15. Definition of Research-Grade Completion

A RoboCert milestone is research-grade only if another expert can reconstruct:

\[
(\text{model},
\text{claim},
\text{assumptions},
\text{certificate},
\text{checker})
\]

and independently obtain the same result.

A publication-quality result should additionally include:

- alternative method comparison;
- failure cases;
- conservatism analysis;
- conditioning analysis;
- runtime;
- certificate size;
- checker time;
- explicit limitations.

---

# 16. Final Strategic Target

The long-term system should support workflows of the form:

```text
Robot + Tool + Workstation CAD + Obstacles
                  |
                  v
       Formal geometric model
                  |
                  v
       Quantified safety claim
                  |
                  v
       Candidate region search
                  |
       +----------+----------+
       |                     |
       v                     v
  algebra/QE             SOS/SDP
       |                     |
       +----------+----------+
                  |
                  v
        interval validation
                  |
                  v
      serialized certificate
                  |
                  v
     deterministic checker
                  |
          +-------+-------+
          |               |
          v               v
 CERTIFIED_*           REJECTED
                          |
                          v
                       UNKNOWN
```

The final product category is therefore not merely:

```text
robot simulation
```

or:

```text
AI CAD
```

but:

\[
\boxed{
\textbf{Certified Robot Configuration-Space Engineering}
}
\]

with a mathematical core capable of producing auditable guarantees over entire regions, uncertainty sets, and task families.

---

# 17. Project Maxim

Every contributor and agent should preserve the following rule:

> **A smaller certified region is more valuable than a larger region supported only by unverified confidence.**

RoboCert succeeds when it can say, precisely and reproducibly:

\[
\boxed{
\text{This statement has been checked under these assumptions.}
}
\]

and when it cannot, it must say:

\[
\boxed{
\text{UNKNOWN}
}
\]

without ambiguity.
