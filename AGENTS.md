# AGENTS.md — RoboCert Research and Engineering Protocol

> **Audience:** autonomous coding agents, research agents, mathematical tool agents, and human contributors working in the RoboCert repository.
>
> **Normative status:** this file defines repository-wide operating rules unless a more specific `AGENTS.md` in a subdirectory explicitly strengthens them.
>
> **Project:** RoboCert — mathematical certification of robotic reachability, collision freedom, singularity separation, and feasibility under geometric and manufacturing uncertainty.

---

# 0. Prime Directive

RoboCert is not a simulation project whose outputs happen to include confidence scores.

RoboCert is a **certification project**.

The defining project invariant is:

\[
\boxed{
\text{Search may be heuristic. Certification may not be.}
}
\]

Any agent working in this repository MUST preserve the distinction between:

- finding a candidate;
- numerically validating a candidate;
- constructing a certificate;
- independently checking a certificate.

An agent MUST NOT collapse these into a single notion of "success."

The system is allowed to return:

- `CERTIFIED_FEASIBLE`;
- `CERTIFIED_INFEASIBLE`;
- `COUNTEREXAMPLE`;
- `NUMERICALLY_FEASIBLE`;
- `NUMERICALLY_INFEASIBLE`;
- `UNKNOWN`.

The system is **not** allowed to promote a numerical outcome to a certified outcome merely because:

- an optimizer converged;
- a simulator passed many samples;
- a residual is small;
- a Jacobian determinant is nonzero at sampled points;
- a collision library reported no collisions on a sampled path;
- an LLM believes the argument is correct;
- multiple approximate solvers agree.

When doubt exists, return `UNKNOWN`.

---

# 1. Mission

RoboCert accepts engineering inputs such as:

- robot model;
- tool geometry;
- workstation CAD;
- obstacles;
- required task poses or task regions;
- joint limits;
- manufacturing tolerances;
- calibration tolerances;
- required clearance margins;
- singularity-separation margins.

RoboCert attempts to produce mathematically auditable statements over sets of configurations, tasks, and uncertainty realizations.

A representative target statement is:

\[
\forall \theta\in\Theta\;
\forall x\in T\;
\exists q\in R:
J(q)
\land
K(q,\theta,x)
\land
C(q,\theta)
\land
S(q,\theta).
\]

Where:

- \(q\) is a robot configuration;
- \(\theta\) is a vector of uncertain parameters;
- \(x\) is a task variable;
- \(J\) encodes joint-limit constraints;
- \(K\) encodes kinematic task satisfaction;
- \(C\) encodes collision or clearance constraints;
- \(S\) encodes singularity-separation constraints.

Agents MUST treat the **quantifier prefix** as part of the theorem.

For example:

\[
\forall\theta\;\exists q
\]

and

\[
\exists q\;\forall\theta
\]

are different claims and MUST NOT be interchanged.

---

# 2. Expertise Standard

The expected reasoning level in the mathematical core is that of a specialist in:

- computational real algebraic geometry;
- semialgebraic geometry;
- polynomial systems;
- elimination theory;
- Gröbner bases;
- real quantifier elimination;
- cylindrical algebraic decomposition;
- Positivstellensatz theory;
- polynomial optimization;
- sum-of-squares methods;
- semidefinite programming;
- interval arithmetic;
- validated numerics;
- symbolic-numeric computation;
- computational geometry;
- robot kinematics and configuration spaces.

Agents may use approximate methods for search, decomposition, initialization, and performance acceleration.

Agents MUST know when an approximate method ceases to support a rigorous statement.

---

# 3. Authority and Instruction Precedence

Within the repository, obey instructions in the following order:

1. safety and legal constraints;
2. explicit human maintainer instructions;
3. this root `AGENTS.md`;
4. more specific nested `AGENTS.md` files;
5. module-level documentation;
6. code comments;
7. inferred conventions.

A nested `AGENTS.md` MAY:

- impose stricter proof obligations;
- impose stricter testing requirements;
- constrain backend choice;
- restrict arithmetic modes;
- require more exactness.

A nested `AGENTS.md` MUST NOT weaken the root soundness rules without an explicit maintainer-approved exception.

---

# 4. Core Soundness Invariants

Every agent MUST preserve all of the following invariants.

## 4.1 Certification means checked certification

A result MAY be labeled `CERTIFIED_*` only if:

1. the claim is explicitly serialized;
2. all domains and assumptions are explicitly serialized;
3. a certificate artifact exists;
4. a deterministic checker accepts the certificate;
5. the checker is appropriate for the claimed certificate family;
6. the checker result is bound to the exact input/model hashes.

No other path may produce a `CERTIFIED_*` status.

---

## 4.2 Failure to prove is not proof of failure

If a backend times out, diverges, exhausts memory, reaches relaxation limits, or fails to find a certificate, the result is generally:

```text
UNKNOWN
```

unless another sound procedure proves infeasibility or finds a valid counterexample.

---

## 4.3 A numerical residual is not an equality proof

Given:

\[
|f(x^\ast)| < 10^{-12},
\]

an agent MUST NOT infer:

\[
f(x^\ast)=0.
\]

Use one of:

- exact arithmetic;
- interval enclosure;
- interval Newton;
- Krawczyk operator;
- rational reconstruction followed by exact checking;
- certified root isolation;
- another mathematically valid validation method.

---

## 4.4 Sampling is not universal quantification

Testing:

\[
q_1,\dots,q_N\in R
\]

does not prove:

\[
\forall q\in R.
\]

Sampling MAY be used to:

- find counterexamples;
- estimate difficult regions;
- initialize decomposition;
- guide solver selection;
- benchmark conservatism;
- debug formulations.

Sampling MUST NOT be the certification argument.

---

## 4.5 LLM output is never a proof certificate

An LLM or autonomous agent MAY:

- derive candidate equations;
- suggest transformations;
- propose lemmas;
- generate solver input;
- explain checked results.

An LLM MUST NOT be the final authority for:

- theorem validity;
- interval inclusion;
- polynomial identity;
- semidefinite feasibility;
- geometric containment;
- exact infeasibility.

The final authority must be deterministic and machine-checkable.

---

## 4.6 Geometry approximations require directional semantics

If true geometry \(\mathcal B\) is replaced by an approximation \(\widehat{\mathcal B}\), the relation MUST be declared.

Examples:

### Conservative outer approximation

\[
\mathcal B\subseteq\widehat{\mathcal B}.
\]

Appropriate for collision-exclusion proofs.

### Inner approximation

\[
\widehat{\mathcal B}\subseteq\mathcal B.
\]

Potentially useful for occupancy existence, but generally unsafe for proving collision freedom.

Agents MUST NOT substitute a mesh, convex hull, bounding box, or simplified primitive without recording whether the substitution is:

- exact;
- outer-conservative;
- inner-conservative;
- non-certified approximation.

---

# 5. Mathematical Object Model

The preferred mathematical representation is a quantified formula over semialgebraic sets.

A basic semialgebraic set has the form:

\[
S=
\left\{
z\in\mathbb R^n:
f_1(z)=\cdots=f_r(z)=0,\;
g_1(z)\ge0,\ldots,g_m(z)\ge0
\right\}.
\]

The internal specification SHOULD represent:

- variables;
- variable domains;
- equalities;
- weak inequalities;
- strict inequalities;
- Boolean combinations;
- quantifier prefix;
- uncertainty semantics;
- provenance;
- transformation history.

Agents MUST preserve strict inequalities explicitly.

Do not silently replace:

\[
g(x)>0
\]

with:

\[
g(x)\ge0.
\]

If an epsilon margin is introduced, it MUST be recorded:

\[
g(x)\ge \varepsilon.
\]

---

# 6. Quantifier Discipline

Quantifiers are first-class data.

## 6.1 Never reorder quantifiers silently

The formulas:

\[
\forall x\in T\;\exists q\in Q:\Phi(x,q)
\]

and

\[
\exists q\in Q\;\forall x\in T:\Phi(x,q)
\]

are not equivalent.

Any transformation that changes quantifier order requires:

- a proof of equivalence;
- or a new claim identifier;
- or explicit classification as a relaxation/strengthening.

---

## 6.2 Record dependency semantics

When a witness depends on a universally quantified variable, this dependency matters.

For:

\[
\forall \theta\in\Theta\;\exists q:\Phi(q,\theta),
\]

the witness \(q\) may depend on \(\theta\).

For:

\[
\exists q\;\forall\theta\in\Theta:\Phi(q,\theta),
\]

the same \(q\) must work for every \(\theta\).

Agents MUST state which interpretation is required by the engineering problem.

---

## 6.3 Path lifting is stronger than pointwise reachability

Pointwise reachability:

\[
\forall s\in[0,1]\;\exists q_s:
F(q_s)=x(s)
\]

does not imply existence of a continuous lift:

\[
\exists q:[0,1]\to Q
\quad
\forall s,\;
F(q(s))=x(s).
\]

Agents MUST distinguish:

- pointwise IK feasibility;
- continuous path feasibility;
- connected safe-region feasibility;
- dynamic trajectory feasibility.

---

# 7. Robot Kinematic Modeling Rules

## 7.1 Frame conventions must be explicit

Every transform MUST identify:

- source frame;
- target frame;
- convention;
- multiplication order;
- units.

Do not rely on ambiguous names like:

```text
T1
T2
T_tool
```

Prefer names with direction semantics, e.g.:

```text
X_WB   # pose of base B in world W
X_BT   # pose of tool T in base B
```

or a project-approved equivalent.

---

## 7.2 Revolute-joint rationalization

For a revolute joint angle \(q_i\), the tangent-half-angle substitution may be used:

\[
t_i=\tan\frac{q_i}{2},
\]

with:

\[
\sin q_i=\frac{2t_i}{1+t_i^2},
\qquad
\cos q_i=\frac{1-t_i^2}{1+t_i^2}.
\]

Agents MUST account for:

- excluded angle values;
- chart boundaries;
- denominator nonvanishing;
- joint interval mapping;
- periodicity;
- branch behavior.

Clearing denominators without tracking their signs and nonzero conditions is forbidden.

---

## 7.3 Avoid gratuitous polynomial degree growth

Before invoking Gröbner, CAD, QE, or SOS backends:

- simplify expressions;
- exploit kinematic sparsity;
- eliminate trivial variables;
- preserve block structure;
- use auxiliary variables when degree reduction is beneficial;
- exploit symmetries;
- exploit known joint limits;
- remove redundant constraints when sound.

Every simplification must preserve the claimed set or explicitly declare itself a relaxation.

---

# 8. Real Algebraic Geometry Protocol

The computational real algebraic geometry layer is central to RoboCert.

## 8.1 Preferred exact operations

Use exact arithmetic where feasible for:

- polynomial coefficients;
- ideal operations;
- Gröbner bases;
- resultants;
- subresultant chains;
- discriminants;
- Sturm sequences;
- rational univariate representations;
- elimination;
- exact sign conditions.

---

## 8.2 Gröbner bases

When computing a Gröbner basis, record:

- coefficient field;
- variable ordering;
- monomial ordering;
- input ideal hash;
- backend/version;
- whether modular methods were used;
- reconstruction/verification status.

A Gröbner basis generated numerically is not automatically exact.

If modular computation or rational reconstruction is used, verify the final basis exactly.

---

## 8.3 Elimination

When using an elimination ideal:

\[
I\cap k[x_1,\dots,x_m],
\]

record the elimination ordering and preserve the distinction between:

- Zariski closure;
- real solution projection;
- semialgebraic projection.

Eliminating algebraic variables over \(\mathbb C\) may introduce real branches that are not feasible under inequalities.

Agents MUST not confuse algebraic elimination with complete real quantifier elimination.

---

## 8.4 Quantifier elimination

For QE/CAD-style methods, record:

- quantified formula;
- variable ordering;
- projection ordering;
- strict/weak inequality semantics;
- equational constraints used;
- assumptions on coefficient exactness;
- generated cell decomposition or equivalent proof artifact if available.

A backend saying `true` is insufficient for `CERTIFIED_*` unless the backend itself is inside the declared trusted base or emits a checkable witness accepted by RoboCert.

---

## 8.5 Real root isolation

When isolating real roots, each root interval SHOULD satisfy:

- rational endpoints;
- disjointness;
- root count;
- multiplicity information where relevant.

If uniqueness is claimed, prove it.

---

# 9. Polynomial Optimization and SOS Protocol

## 9.1 Numerical SDP output is not yet a certificate

A floating-point SDP solution MAY generate a candidate SOS decomposition.

Before certification, RoboCert SHOULD:

1. reconstruct rational coefficients where practical;
2. verify polynomial identities exactly;
3. verify PSD conditions exactly or through validated bounds;
4. include all domain constraints used in the certificate.

---

## 9.2 Positivstellensatz assumptions must be explicit

If using a quadratic module or preordering, state:

- generators \(g_i\);
- equality constraints \(h_j\);
- compactness/Archimedean assumptions if required;
- relaxation degree;
- multiplier structure;
- sparsity decomposition.

Do not claim completeness at a fixed relaxation order unless mathematically justified.

---

## 9.3 Distinguish lower bounds from positivity certificates

A numerical lower bound:

\[
\gamma_{\text{num}}>0
\]

is not a certified lower bound unless validated.

For a certified claim:

\[
p(x)\ge \gamma>0
\quad \forall x\in K,
\]

the lower bound must itself be certified.

---

## 9.4 Sparse SOS

For high-dimensional problems, exploit:

- correlative sparsity;
- term sparsity;
- chordal decomposition;
- localizing matrix structure.

Agents MUST preserve proof semantics when decomposing the problem.

---

# 10. Interval Arithmetic and Validated Numerics Protocol

## 10.1 Directed rounding

Certified interval operations require outward rounding.

Plain IEEE floating-point endpoint computations are not sufficient unless the library guarantees directed rounding or an equivalent validated enclosure.

---

## 10.2 Interval inclusion

For an interval function \(F(X)\), verify inclusion guarantees.

Do not assume that replacing each operation by naive endpoint arithmetic preserves correctness in the presence of dependency.

---

## 10.3 Interval Newton / Krawczyk

When proving root existence or uniqueness, record:

- initial box;
- Jacobian enclosure;
- preconditioner;
- inclusion result;
- uniqueness result;
- final isolating box.

A converged Newton iteration is not equivalent to interval Newton certification.

---

## 10.4 Branch-and-bound

For validated branch-and-bound:

- every terminal box must be classified;
- unresolved boxes must remain unresolved;
- pruning must be justified by certified bounds;
- no box may disappear because of timeout or memory pressure.

The union of classified and unresolved boxes must cover the original domain.

---

# 11. Collision Certification Protocol

Collision certification is a set problem, not a finite query problem.

Given robot geometry \(\mathcal R(q,\theta)\) and obstacle geometry \(\mathcal O(\theta)\), a robust regional claim may be:

\[
\forall(q,\theta)\in R\times\Theta:
\operatorname{dist}(
\mathcal R(q,\theta),
\mathcal O(\theta)
)
\ge\delta.
\]

## 11.1 Exact primitive geometry

Prefer exact analytic representations for initial milestones:

- spheres;
- capsules;
- boxes;
- cylinders;
- convex polytopes.

---

## 11.2 Convex decomposition

If a nonconvex body is decomposed:

\[
\mathcal B=\bigcup_i \mathcal B_i,
\]

record whether decomposition is:

- exact;
- outer;
- inner;
- approximate.

---

## 11.3 Separation certificates

When using separating planes or polynomial separators, certificate data SHOULD include:

- separator coefficients;
- domain;
- body pair;
- positivity/nonintersection proof;
- clearance margin if claimed.

---

## 11.4 Configuration-space region certification

For C-IRIS-style methods, agents SHOULD separate:

- candidate region construction;
- separating-certificate generation;
- final region validation.

A candidate polytope is not certified merely because an algorithm intended to produce certified polytopes returned successfully. The repository must retain enough evidence to independently validate the result under the adopted trust model.

---

# 12. Singularity Certification Protocol

## 12.1 State the singularity notion

Possible notions include:

- loss of rank of geometric Jacobian;
- loss of rank of task Jacobian;
- vanishing determinant for square Jacobians;
- loss of manipulability;
- low minimum singular value.

Never use "singularity-free" without stating the criterion.

---

## 12.2 Rank certification

For a matrix \(J(q)\), rank loss may be encoded by vanishing minors.

If full row rank \(r\) is required, one may certify that at least one \(r\times r\) minor stays nonzero, or certify a lower bound on:

\[
\sigma_{\min}(J).
\]

The chosen surrogate must be mathematically sufficient for the stated claim.

---

## 12.3 Margin claims

A claim such as:

\[
\sigma_{\min}(J(q))\ge\varepsilon
\]

requires a certified lower bound.

Sampling singular values is insufficient.

---

# 13. Robustness and Uncertainty Protocol

Uncertain parameters are denoted by:

\[
\theta\in\Theta.
\]

Agents MUST distinguish:

- manufacturing tolerance;
- calibration error;
- perception uncertainty;
- state-estimation uncertainty;
- geometry approximation error;
- thermal drift;
- compliance model uncertainty.

Different uncertainty types may require different semantics.

---

## 13.1 Box uncertainty

A common initial model is:

\[
\Theta=
\prod_i
[\theta_i^-,\theta_i^+].
\]

Do not assume checking all vertices of \(\Theta\) is sufficient for nonlinear constraints unless convexity/monotonicity proves it.

---

## 13.2 Correlated uncertainty

If uncertainty is correlated, do not replace it by an independent box unless the resulting set is an explicitly conservative superset.

Record the induced conservatism.

---

## 13.3 Robust claim semantics

Distinguish:

### Adjustable feasibility

\[
\forall\theta\in\Theta\;\exists q:\Phi(q,\theta).
\]

### Static robust feasibility

\[
\exists q\;\forall\theta\in\Theta:\Phi(q,\theta).
\]

### Policy feasibility

\[
\exists \pi\;\forall\theta\in\Theta:
\Phi(\pi(\theta),\theta).
\]

These are not interchangeable.

---

# 14. Formal Methods and Proof Objects

The long-term architecture should minimize the trusted computing base.

## 14.1 Solver/checker separation

Preferred pattern:

```text
high-complexity solver
        |
        v
candidate certificate
        |
        v
small deterministic checker
        |
   +----+----+
   |         |
 PASS      FAIL
```

The checker SHOULD be simpler than the solver.

---

## 14.2 Proof-carrying results

Every certified artifact SHOULD include:

- claim identifier;
- input hashes;
- theorem statement;
- assumptions;
- certificate family;
- certificate payload;
- checker identity;
- checker version;
- checker output;
- arithmetic mode;
- timestamp;
- provenance.

---

## 14.3 No hidden proof state

A certificate MUST NOT depend on unrecorded in-memory solver state.

If a checker cannot reproduce acceptance from serialized artifacts, the result is not portable enough for RoboCert.

---

# 15. Result Semantics

The following statuses are normative.

## 15.1 `CERTIFIED_FEASIBLE`

Use only when a formal feasibility claim has a checked certificate.

---

## 15.2 `CERTIFIED_INFEASIBLE`

Use only when emptiness/inconsistency has a checked certificate.

---

## 15.3 `COUNTEREXAMPLE`

Use when a concrete witness falsifies a universal claim and the witness itself is validated sufficiently to establish violation.

---

## 15.4 `NUMERICALLY_FEASIBLE`

Use when a numerical candidate exists but no rigorous certificate has been checked.

---

## 15.5 `NUMERICALLY_INFEASIBLE`

Use when a numerical solver reports failure or infeasibility without a rigorous certificate.

---

## 15.6 `UNKNOWN`

Use whenever certification is not established and no validated counterexample has been produced.

`UNKNOWN` is not an error.

---

# 16. Agent Roles

RoboCert may use multiple specialized agents.

Agents MUST remain within their role boundaries.

---

## 16.1 `SpecificationAgent`

Responsibilities:

- parse user intent;
- identify variables;
- identify domains;
- identify quantifiers;
- identify uncertainty semantics;
- identify margins;
- produce a formal claim draft.

Forbidden:

- silently choosing quantifier order;
- inventing tolerances;
- inventing missing safety margins;
- declaring certification.

Required output:

```text
FormalClaimDraft
Assumptions
Ambiguities
RequiredUserDecisions
```

---

## 16.2 `GeometryAgent`

Responsibilities:

- ingest CAD/mesh/primitive geometry;
- normalize frames;
- construct conservative geometric models;
- perform decomposition;
- produce geometry provenance.

Forbidden:

- calling an unvalidated simplification "exact";
- dropping small features without recording a bound;
- replacing a body by an inner approximation for collision safety.

Required output:

```text
GeometryModel
ContainmentRelations
ApproximationBounds
FrameMap
Provenance
```

---

## 16.3 `AlgebraAgent`

Responsibilities:

- derive polynomial/rational constraints;
- simplify symbolic systems;
- perform elimination;
- generate candidate Gröbner/QE certificates;
- detect algebraic branch structure.

Forbidden:

- clearing denominators without domain conditions;
- using complex algebraic feasibility as a substitute for real feasibility;
- ignoring inequalities after elimination.

---

## 16.4 `OptimizationAgent`

Responsibilities:

- formulate polynomial optimization;
- formulate SOS/SDP relaxations;
- exploit sparsity;
- generate candidate positivity/infeasibility certificates.

Forbidden:

- treating numerical SDP feasibility as final certification;
- suppressing solver conditioning warnings;
- claiming positivity from an unchecked Gram matrix.

---

## 16.5 `IntervalAgent`

Responsibilities:

- validate roots;
- certify inequalities on boxes;
- perform rigorous subdivision;
- validate numerical bounds.

Forbidden:

- using ordinary floating-point intervals without outward rounding guarantees;
- dropping unresolved boxes.

---

## 16.6 `CounterexampleAgent`

Responsibilities:

- search aggressively for violating configurations;
- attack universal claims;
- test boundary cases;
- explore near-singular and near-contact regions.

This agent is encouraged to use:

- random search;
- adversarial optimization;
- continuation;
- local optimization;
- global heuristics.

A candidate counterexample must still be validated before publication.

---

## 16.7 `CertificateAgent`

Responsibilities:

- assemble proof objects;
- normalize certificate formats;
- invoke deterministic checkers;
- bind certificates to model hashes.

Forbidden:

- "fixing" a failing certificate by weakening the claim without changing the claim identifier.

---

## 16.8 `CertificateChecker`

This MUST be deterministic software, not an LLM persona.

Responsibilities:

- verify syntax;
- verify hashes;
- verify exact identities;
- verify interval inclusions;
- verify PSD conditions under the declared arithmetic model;
- verify geometric containment proofs;
- emit pass/fail with diagnostics.

---

## 16.9 `ExplanationAgent`

Responsibilities:

- translate checked mathematics into engineering language;
- report assumptions;
- report active constraints;
- report uncertainty;
- explain infeasibility cores.

Forbidden:

- adding unsupported causal explanations;
- rewriting `UNKNOWN` as "probably safe";
- omitting material assumptions.

---

## 16.10 `SupervisorAgent`

Responsibilities:

- coordinate agents;
- preserve specification state;
- route problems;
- detect role violations;
- stop unsafe promotion of numerical results.

The SupervisorAgent MUST NOT override a failing checker.

---

# 17. Agent Communication Contract

Agent-to-agent messages SHOULD be structured.

Preferred fields:

```yaml
message:
  task_id: ...
  claim_id: ...
  sender_role: ...
  receiver_role: ...
  input_hashes: [...]
  assumptions: [...]
  requested_operation: ...
  output_semantics: ...
  soundness_level: ...
  artifacts: [...]
  unresolved_questions: [...]
```

Do not pass mathematical results as prose only when a structured representation exists.

---

# 18. Soundness Levels

Every computational artifact SHOULD declare a soundness level.

## `HEURISTIC`

May be wrong.

Examples:

- LLM derivation;
- random search;
- floating-point optimizer result;
- simulation trace.

## `NUMERICAL`

Numerically validated but not rigorous.

Examples:

- high-precision residual;
- repeated solver agreement;
- dense sampling.

## `VALIDATED`

Uses rigorous interval or equivalent enclosure guarantees.

## `EXACT`

Uses exact algebraic/rational computation.

## `CHECKED_CERTIFICATE`

Accepted by an independent deterministic checker.

Only `CHECKED_CERTIFICATE` may support `CERTIFIED_*` statuses.

---

# 19. Repository Architecture

Recommended layout:

```text
robocert/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── docs/
│   ├── mathematics/
│   ├── architecture/
│   ├── certificates/
│   ├── geometry/
│   ├── assumptions/
│   └── benchmarks/
├── schemas/
│   ├── project.schema.json
│   ├── claim.schema.json
│   ├── result.schema.json
│   └── certificate.schema.json
├── src/
│   └── robocert/
│       ├── model/
│       ├── geometry/
│       ├── kinematics/
│       ├── algebra/
│       ├── specification/
│       ├── search/
│       ├── optimization/
│       ├── certification/
│       │   ├── exact/
│       │   ├── qe/
│       │   ├── sos/
│       │   ├── interval/
│       │   └── cspace/
│       ├── checking/
│       ├── diagnostics/
│       ├── provenance/
│       └── reporting/
├── tests/
│   ├── unit/
│   ├── property/
│   ├── regression/
│   ├── adversarial/
│   └── certificate/
├── benchmarks/
│   ├── planar_2r/
│   ├── planar_3r/
│   ├── spatial_3dof/
│   ├── industrial_6dof/
│   └── robust_7dof/
└── certificates/
```

---

# 20. Module Dependency Rules

To preserve a small trusted computing base:

- `checking/` MUST NOT depend on agent orchestration code;
- `checking/` SHOULD avoid heavyweight solver dependencies where possible;
- `reporting/` MUST NOT change mathematical result status;
- `search/` MUST NOT emit `CERTIFIED_*`;
- `optimization/` MAY emit candidate certificates but not final certified status;
- `certification/` MAY construct certificates;
- `checking/` determines certificate acceptance;
- `provenance/` binds claims to inputs and artifacts.

Circular dependencies between:

```text
search
certification
checking
```

should be treated as architectural defects.

---

# 21. Development Workflow for Agents

For every nontrivial task, follow this sequence.

## Step 1 — classify the task

Determine whether the task is:

- mathematical specification;
- symbolic transformation;
- geometry processing;
- numerical search;
- certificate generation;
- checker implementation;
- benchmark creation;
- documentation;
- performance optimization;
- agent orchestration.

---

## Step 2 — identify soundness impact

Ask:

- Can this change affect a certified claim?
- Is this code inside the trusted computing base?
- Can this change alter quantifier semantics?
- Can this change alter geometry containment?
- Can this change arithmetic rigor?
- Can this change result-status promotion?

If yes, treat it as **soundness-critical**.

---

## Step 3 — state invariants before editing

For soundness-critical work, record the invariants that must remain true.

Example:

```text
Invariant 1: every returned box covers a subset of the original domain.
Invariant 2: pruned boxes have a certified exclusion proof.
Invariant 3: unresolved boxes are preserved.
```

---

## Step 4 — implement the smallest correct change

Avoid broad refactors during proof-critical changes unless required.

Prefer:

- local modifications;
- explicit types;
- explicit contracts;
- deterministic behavior;
- reproducible tests.

---

## Step 5 — add tests before claiming completion

Soundness-critical code requires:

- positive tests;
- negative tests;
- adversarial tests;
- corrupted-certificate tests where applicable.

---

## Step 6 — run the narrowest relevant benchmark

Do not rely only on unit tests.

Use a benchmark whose mathematical answer is known independently.

---

## Step 7 — report limitations

Agents MUST state:

- what was proved;
- what was tested only numerically;
- what remains unknown;
- what assumptions were added.

---

# 22. Coding Standards

## 22.1 Explicit types

Use types to distinguish:

```text
CandidateSolution
ValidatedSolution
Certificate
CheckedCertificate
Counterexample
UnknownResult
```

Do not use one generic `Result` object with loosely interpreted flags.

---

## 22.2 Units

Physical quantities MUST carry units or be normalized under an explicit convention.

Never mix:

- meters and millimeters;
- radians and degrees;
- Newtons and kilogram-force.

If dimensionless normalization is used, record the scaling map.

---

## 22.3 Exact types

Prefer explicit types such as:

```text
Rational
AlgebraicNumber
Interval
Polynomial
SemialgebraicFormula
```

over raw floating-point arrays in proof-critical code.

---

## 22.4 Determinism

Certificate checking MUST be deterministic.

If a solver uses randomization:

- record seed;
- separate search from checking;
- ensure checking does not depend on random choice.

---

## 22.5 Error handling

Soundness-critical functions MUST fail closed.

Bad:

```python
try:
    verify()
except Exception:
    return True
```

Acceptable principle:

```text
verification exception
        =>
certificate rejected
```

---

# 23. Naming Conventions

Names SHOULD encode semantics.

Prefer:

```text
candidate_region
certified_region
outer_collision_geometry
exact_polynomial
validated_interval
```

Avoid ambiguous names:

```text
safe_region
good_solution
verified
exact
```

unless the type guarantees the meaning.

---

# 24. Testing Requirements

## 24.1 Unit tests

Required for:

- coordinate transforms;
- polynomialization;
- rationalization;
- interval operations;
- certificate parsing;
- hash/provenance logic;
- status transitions.

---

## 24.2 Property tests

Examples:

### Kinematic consistency

For randomly sampled nonsingular configurations:

\[
F_{\text{symbolic}}(q)
\approx
F_{\text{reference}}(q).
\]

This is a diagnostic property, not certification.

### Outer-geometry property

For sampled true-geometry points \(x\):

\[
x\in\widehat{\mathcal B}_{\text{outer}}.
\]

Again, sampling is a bug detector. The final containment claim requires a stronger argument.

### Certificate corruption

Mutate:

- one coefficient;
- one bound;
- one hash;
- one domain constraint.

The checker MUST reject.

---

## 24.3 Regression tests

Every previously discovered soundness bug MUST receive a permanent regression test.

---

## 24.4 Adversarial tests

Include:

- tangential contact;
- zero-clearance contact;
- almost singular Jacobians;
- repeated polynomial roots;
- multiple roots;
- denominator near zero;
- chart boundaries;
- tiny feasible components;
- narrow passages;
- degenerate CAD primitives;
- tolerance intervals spanning topology changes;
- nearly singular SDP Gram matrices.

---

# 25. Benchmark Policy

Initial benchmarks SHOULD include analytically understandable systems.

## Benchmark A — planar 2R

Must support independent hand/algebraic checking.

Target claims:

- reachability;
- joint limits;
- circular obstacle avoidance;
- singularity separation;
- interval link-length uncertainty.

---

## Benchmark B — planar 3R

Target:

\[
\forall x\in T\;\exists q.
\]

Add redundancy.

---

## Benchmark C — spatial 3-DOF

Exercise:

- elimination;
- branch structure;
- exact root isolation;
- parameterized task paths.

---

## Benchmark D — industrial 6-DOF

Use local C-space certification rather than attempting global QE.

---

## Benchmark E — robust 6/7-DOF

Add:

- link tolerances;
- TCP calibration uncertainty;
- obstacle pose uncertainty;
- robust clearance.

---

# 26. Cross-Validation Policy

For small benchmarks, agents SHOULD seek agreement among independent rigorous methods.

Examples:

```text
QE
vs
interval branch-and-bound
```

or:

```text
exact elimination
vs
validated homotopy/root isolation
```

or:

```text
SOS certificate
vs
interval lower bound
```

Agreement increases confidence in implementation correctness.

It does not eliminate the need for each method's own soundness argument.

---

# 27. Performance Optimization Rules

Performance work MUST NOT weaken soundness.

Allowed optimizations include:

- expression simplification;
- sparsity exploitation;
- decomposition;
- caching;
- parallel search;
- modular exact arithmetic;
- certified pruning;
- warm starts;
- candidate generation by heuristics.

Forbidden shortcuts include:

- replacing rigorous bounds with approximate bounds without changing result semantics;
- dropping unresolved cells;
- treating timeout as infeasibility;
- reducing precision without revalidation;
- using nonconservative geometry approximations for certified safety.

---

# 28. Domain Decomposition Protocol

If a domain \(Q\) is decomposed:

\[
Q=R_1\cup\cdots\cup R_n\cup U,
\]

the system MUST preserve coverage.

Where:

- each \(R_i\) is classified;
- \(U\) is unresolved.

A partial result MAY report:

\[
R_{\text{cert}}
=
\bigcup_{i\in I_{\text{cert}}}R_i.
\]

But it MUST NOT silently discard \(U\).

---

# 29. Infeasibility Protocol

A numerical solver returning `infeasible` is not sufficient.

Preferred certificate families include:

- Positivstellensatz refutations;
- exact elimination leading to contradiction;
- interval exclusion covering the entire domain;
- exact linear/convex dual certificates;
- SMT proof objects where available.

If no checkable witness exists:

```text
NUMERICALLY_INFEASIBLE
```

or:

```text
UNKNOWN
```

must be used.

---

# 30. Minimal Conflict Explanations

When a conjunction:

\[
A\land B\land C\land D
\]

is certified infeasible, an explanation subsystem MAY search for a smaller infeasible subset.

For example:

\[
A\land B\land C
\]

may already be infeasible.

Agents MUST distinguish:

- **certified unsat core**;
- **heuristic conflict hypothesis**.

Do not present the latter as proof.

---

# 31. Counterexample Protocol

A counterexample to:

\[
\forall z\in D:\Phi(z)
\]

is a \(z^\ast\in D\) such that:

\[
\neg\Phi(z^\ast).
\]

Before publishing `COUNTEREXAMPLE`, validate:

1. \(z^\ast\in D\);
2. the violated condition;
3. all frame/unit conversions;
4. uncertainty realization if applicable.

A floating-point near-violation SHOULD be interval-validated when close to the boundary.

---

# 32. CAD and Geometry Ingestion Rules

## 32.1 STEP/B-Rep

Record:

- source file hash;
- CAD kernel version;
- unit scale;
- healing operations;
- tolerance changes;
- topology changes.

---

## 32.2 Meshes

Meshes are not exact solids by default.

Record:

- watertightness;
- manifold status;
- orientation;
- tessellation error;
- simplification error;
- containment semantics.

---

## 32.3 Geometry healing

Any healing operation that changes geometry MUST produce:

- before/after hashes;
- declared tolerance;
- geometric error bound if used in certification.

---

# 33. Provenance Requirements

Every proof-critical artifact MUST be reproducible.

Record at least:

- repository commit;
- input hashes;
- solver backend;
- solver version;
- checker version;
- arithmetic precision;
- random seed for heuristic search;
- platform details if numerically relevant;
- claim hash;
- certificate hash.

---

# 34. Reproducibility Rules

A certified result MUST be reproducible from:

```text
model
+ claim
+ assumptions
+ certificate
+ checker
```

The explanatory text is not part of the proof.

---

# 35. Documentation Rules

Documentation MUST preserve semantic distinctions.

Never write:

> "RoboCert proved the robot is safe."

unless the exact safety property is explicitly defined.

Prefer:

> "RoboCert certified that every configuration in region \(R\), under uncertainty set \(\Theta\), maintains at least 5 mm clearance from the modeled static obstacles and satisfies the declared joint and singularity-margin constraints."

---

# 36. Claim Wording Rules

Avoid vague terms.

## Avoid

- safe;
- reachable;
- singularity-free;
- exact;
- verified;
- robust;
- guaranteed.

unless each is qualified.

## Prefer

- collision-free with clearance \(\delta\);
- pointwise IK reachable;
- continuously liftable;
- rank-\(r\) Jacobian condition;
- exact rational identity;
- interval-validated lower bound;
- robust over parameter set \(\Theta\);
- accepted by checker \(C\).

---

# 37. Pull Request Requirements

Every PR affecting mathematical semantics MUST include:

1. problem statement;
2. affected theorem/claim semantics;
3. soundness impact;
4. mathematical justification;
5. tests;
6. benchmark result;
7. known limitations.

A PR that changes a certificate checker SHOULD include deliberately invalid certificates demonstrating rejection.

---

# 38. Soundness-Critical Review Checklist

Before merging proof-critical code, verify:

- [ ] Quantifier order preserved.
- [ ] Strict vs weak inequalities preserved.
- [ ] Units preserved.
- [ ] Frame conventions preserved.
- [ ] Geometry containment direction preserved.
- [ ] Denominator conditions preserved.
- [ ] No numerical result promoted to certified.
- [ ] Unknown regions preserved.
- [ ] Certificate bound to exact claim hash.
- [ ] Checker fails closed.
- [ ] Corrupted certificates rejected.
- [ ] Arithmetic model documented.
- [ ] Assumptions serialized.
- [ ] Reproducibility data recorded.

---

# 39. Research Experiment Rules

Research branches may use exploratory code.

However:

- experimental results MUST be labeled experimental;
- notebooks MUST NOT directly emit `CERTIFIED_*`;
- exploratory simplifications MUST be documented;
- benchmark conclusions MUST separate empirical observations from proved results.

---

# 40. Notebook Policy

Notebooks are permitted for:

- derivations;
- visualization;
- experiment design;
- numerical exploration;
- benchmark analysis.

Production proof logic MUST migrate into tested modules.

A notebook cell output is not a certificate.

---

# 41. Symbolic-Numeric Interface Rules

The symbolic-numeric boundary is high risk.

When moving from exact to floating-point:

- record conversion;
- record precision;
- record scaling;
- retain exact source where possible.

When moving from floating-point back to exact:

- use rational reconstruction cautiously;
- verify reconstructed identities exactly;
- reject unstable reconstruction.

---

# 42. Scaling and Conditioning

Polynomial systems can be numerically pathological.

Agents SHOULD:

- nondimensionalize physical variables;
- scale polynomial coefficients;
- normalize coordinates;
- inspect condition numbers;
- avoid unnecessary high-degree representations.

Scaling transformations MUST be invertible and recorded.

---

# 43. Lie Group / Polynomial Interface

Rigid transformations live naturally in:

\[
SE(3).
\]

Polynomial backends may use alternative parameterizations.

Agents MUST record the map between:

- rotation matrices;
- quaternions;
- tangent-half-angle variables;
- exponential coordinates;
- polynomial embedding variables.

All representation constraints MUST be included.

Example for unit quaternion \(u\):

\[
u^\top u=1.
\]

Do not omit normalization constraints.

---

# 44. Quaternion Rules

If quaternions are used:

- account for the double cover \(q\sim -q\);
- include unit-norm constraint;
- avoid artificial discontinuities where possible;
- specify whether orientation equality is modulo sign.

---

# 45. Strict Inequalities

Strict inequalities require care in exact and SOS formulations.

For:

\[
g(x)>0,
\]

possible representations include a certified margin:

\[
g(x)\ge\varepsilon,\qquad \varepsilon>0.
\]

Do not silently replace strict positivity by nonnegativity.

---

# 46. Boundary Analysis

Many failures occur on boundaries.

Agents SHOULD explicitly test:

- joint-limit boundaries;
- obstacle contact boundaries;
- singularity varieties;
- denominator-zero sets;
- uncertainty-set boundaries;
- CAD decomposition boundaries.

---

# 47. Degeneracy Policy

Degenerate cases MUST be treated intentionally.

Examples:

- repeated roots;
- zero-length links;
- coincident joint axes;
- singular geometry;
- zero-clearance obstacle contact;
- rank-deficient constraint Jacobians.

Do not assume "generic position" unless stated as an explicit assumption.

---

# 48. Genericity Assumptions

If a theorem requires genericity, record it.

Examples:

- distinct roots;
- transversal intersection;
- nonzero determinant;
- nonparallel axes.

An engineering certificate under a genericity assumption is invalid if the actual model may violate that assumption.

---

# 49. Exact vs Conservative Modeling

RoboCert may certify a conservative model.

This is acceptable if the direction is clear.

Example:

\[
\mathcal F_{\text{cert}}
\subseteq
\mathcal F_{\text{true}}
\]

for a conservatively certified feasible region.

Do not describe conservative under-approximation as the complete feasible set.

---

# 50. Completeness Claims

Most RoboCert backends are not expected to be complete at industrial scale.

Agents MUST NOT claim:

> "No certificate exists."

when they only know:

> "This backend did not find a certificate."

Completeness claims require a theorem about the method and its assumptions.

---

# 51. Termination Claims

Timeout is not a mathematical result.

Resource exhaustion is not a mathematical result.

A solver exception is not a mathematical result.

Map these to:

```text
UNKNOWN
```

unless a previously checked artifact already establishes the claim.

---

# 52. Proof Certificate Versioning

Certificate formats MUST be versioned.

A checker MUST reject:

- unknown major versions;
- malformed certificates;
- incompatible claim schemas;
- mismatched input hashes.

---

# 53. Checker Independence

Where practical, certificate checking SHOULD use a different implementation path from certificate generation.

Example:

```text
SOS generation: floating-point SDP backend
SOS checking: exact polynomial identity + exact/validated PSD check
```

This reduces correlated implementation error.

---

# 54. Hash Binding

A certificate MUST bind to:

- robot model;
- tool geometry;
- workstation geometry;
- task definition;
- joint limits;
- uncertainty set;
- margins;
- mathematical formulation.

Changing any one invalidates the certificate.

---

# 55. Cache Safety

Cached proof artifacts MUST include dependency hashes.

Never reuse a certificate based only on filename or human-readable model name.

---

# 56. Parallelism Rules

Parallelize:

- counterexample search;
- decomposition;
- independent backend attempts;
- candidate generation.

Be careful parallelizing:

- mutable exact algebra state;
- global rounding mode;
- shared interval contexts;
- non-thread-safe CAS backends.

Checker determinism must be preserved.

---

# 57. External Solver Policy

External solvers are allowed.

For each solver, document:

- license;
- version;
- role;
- trusted/untrusted status;
- certificate output;
- reproducibility;
- failure semantics.

A proprietary or opaque solver MAY be used for candidate search if its output is independently certifiable.

---

# 58. Solver Adapter Contract

Every solver adapter SHOULD map native statuses into RoboCert semantics explicitly.

Example:

```text
native OPTIMAL
    -> candidate solution
    -> NOT automatically CERTIFIED_FEASIBLE
```

```text
native INFEASIBLE
    -> NUMERICALLY_INFEASIBLE
    -> unless a checkable infeasibility certificate is verified
```

---

# 59. Formal Specification Schema

A formal claim SHOULD include:

```yaml
claim:
  id: ...
  variables:
    q: ...
    theta: ...
    x: ...
  quantifiers:
    - forall: theta
      domain: Theta
    - forall: x
      domain: T
    - exists: q
      domain: Q
  predicates:
    - joint_limits
    - kinematics
    - collision_clearance
    - singularity_margin
  assumptions:
    - rigid_body
    - static_obstacles
  margins:
    collision: 0.005
    singularity: 0.08
```

Agents MUST not certify an informal natural-language claim without a formal counterpart.

---

# 60. Assumption Management

Assumptions are part of the theorem.

Common assumptions include:

- rigid links;
- exact actuator position realization;
- static obstacles;
- no elastic deflection;
- bounded calibration error;
- bounded thermal drift;
- exact workpiece fixturing within tolerance;
- conservative collision geometry.

Agents MUST not omit assumptions from user-facing reports if they materially affect interpretation.

---

# 61. Dynamics Boundary

Unless dynamic constraints are explicitly modeled, a geometric/kinematic certificate does not prove dynamic executability.

Do not infer:

\[
\text{kinematically feasible}
\Rightarrow
\text{dynamically feasible}.
\]

Future dynamic claims may involve:

\[
M(q)\ddot q+
C(q,\dot q)\dot q+
g(q)=\tau.
\]

Such claims require explicit velocity, acceleration, torque, contact, and timing constraints.

---

# 62. Control Boundary

A configuration-space safety certificate is not automatically a controller safety certificate.

Do not infer:

\[
q\in R_{\text{safe}}
\]

implies a controller will remain inside \(R_{\text{safe}}\).

That requires invariance or reachability analysis.

---

# 63. Functional Safety Boundary

RoboCert mathematical certificates do not automatically establish compliance with industrial safety standards.

Agents MUST not claim standards compliance unless the project includes a separate validated safety case and applicable certification process.

---

# 64. Human Factors Boundary

Human motion, intent, and behavior require explicit models.

Static obstacle certification cannot be extrapolated to unmodeled humans.

---

# 65. Explanation Policy

User-facing explanations SHOULD state:

1. what was certified;
2. over which domain;
3. under which uncertainty set;
4. with what margins;
5. under which assumptions;
6. with which certificate family;
7. checker status;
8. unresolved limitations.

---

# 66. No Overclaiming

Forbidden wording unless precisely justified:

- "100% safe";
- "guaranteed in reality";
- "proof that the robot can never collide";
- "formally verified hardware";
- "certified for all manufacturing errors";

Prefer domain-qualified language.

---

# 67. Research Citation Policy

When adding research claims to documentation:

- cite primary literature where possible;
- distinguish established theorem from project hypothesis;
- distinguish peer-reviewed work from preprint;
- record exact method relevance.

Do not cite a paper merely because it contains similar terminology.

---

# 68. First Mathematical Milestone

The first complete theorem-level milestone SHOULD be a planar 2R robot with:

- interval link-length tolerances;
- rectangular joint limits;
- one analytic obstacle;
- a compact task region;
- a singularity margin.

Target statement:

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

The milestone is complete only when:

1. the claim is formally serialized;
2. at least one rigorous backend constructs a certificate;
3. an independent checker accepts it;
4. an adversarial counterexample search finds no valid contradiction;
5. results are reproducible from a clean environment.

---

# 69. Research Roadmap Priorities

Prioritize in this order:

1. formal claim semantics;
2. exact 2R/3R benchmarks;
3. certificate schema;
4. checker architecture;
5. interval verification;
6. exact algebra/QE;
7. SOS/SDP certificate reconstruction;
8. C-space collision certification;
9. robust tolerance handling;
10. industrial CAD ingestion;
11. multi-agent orchestration;
12. dynamics and control extensions.

Do not invert this order solely to build a more impressive UI.

---

# 70. What Agents Should Optimize For

Primary objectives:

1. soundness;
2. semantic precision;
3. reproducibility;
4. independently checkable certificates;
5. useful certified coverage;
6. computational efficiency;
7. usability.

Not the reverse.

---

# 71. Completion Criteria for Agent Tasks

An agent may declare a task complete only if:

- requested functionality exists;
- relevant tests pass;
- soundness semantics are preserved;
- documentation is updated when semantics change;
- limitations are stated;
- no numerical result has been mislabeled certified;
- no unresolved proof obligation is hidden.

---

# 72. Mandatory Stop Conditions

An agent MUST stop promotion to certified status if any of the following occurs:

- quantifier ambiguity;
- unknown unit conversion;
- unknown frame convention;
- unchecked geometry approximation;
- missing uncertainty semantics;
- checker mismatch;
- certificate hash mismatch;
- interval library lacks rigorous rounding guarantees;
- exact reconstruction fails;
- solver output cannot be independently validated.

The appropriate outcome is usually:

```text
UNKNOWN
```

with diagnostics.

---

# 73. Preferred Mathematical Failure Mode

When a proof attempt fails, produce useful structured diagnostics:

```yaml
certification_failure:
  status: UNKNOWN
  failed_backend: sos
  reason: relaxation_not_strictly_positive
  unresolved_domain: ...
  candidate_counterexamples: [...]
  recommended_next_methods:
    - interval_subdivision
    - domain_decomposition
    - exact_elimination
```

Do not fabricate a theorem to avoid an inconclusive result.

---

# 74. Subdirectory AGENTS.md Guidance

Subdirectories may define specialized rules.

Recommended:

```text
src/robocert/algebra/AGENTS.md
src/robocert/certification/sos/AGENTS.md
src/robocert/certification/interval/AGENTS.md
src/robocert/checking/AGENTS.md
src/robocert/geometry/AGENTS.md
```

Examples:

- the interval subtree may require a specific rigorous rounding library;
- the checker subtree may prohibit network access and nondeterminism;
- the algebra subtree may require exact coefficient fields by default.

---

# 75. Final Rule

When deciding between:

```text
a stronger claim with incomplete justification
```

and:

```text
a weaker claim with a valid certificate
```

choose the weaker certified claim.

When deciding between:

```text
a confident answer
```

and:

```text
UNKNOWN
```

choose `UNKNOWN` unless the confidence can be converted into a checked mathematical argument.

RoboCert exists to make the following distinction operational:

\[
\boxed{
\text{evidence}
\neq
\text{certificate}
}
\]

and:

\[
\boxed{
\text{candidate}
\neq
\text{theorem}
}
\]

Every agent in this repository is responsible for preserving that distinction.
