# Certification goals and terminology

**Goals, not capabilities.** This page explains what RoboCert's target statements would mean. The public package certifies none of them today: the production checker registry is empty and `robocert certify` returns `UNKNOWN`. Current status is in the [README](../../README.md). Claim tiers are recorded in [`research/CLAIMS.md`](../../research/CLAIMS.md). The normative rules are in [`AGENTS.md`](../../AGENTS.md), and this page does not restate or override them.

The full original treatment is in the [archived project overview](../archive/initial-project-overview.md), §2–4, §7, §11 and §34.

## Notation

- `q` is a robot configuration, `x` a task parameter, and `theta` a bounded geometric, calibration, or manufacturing parameter.
- `T` is a task region, `R` a configuration region, and `Theta` an uncertainty set.
- Revolute joints are rationalized by the tangent half-angle `t = tan(q/2)`, so `sin q = 2t/(1+t^2)` and `cos q = (1-t^2)/(1+t^2)`. A finite `t` cannot represent `q = pi`. A single chart is therefore incomplete on the torus, and every claim must say which chart or charts it covers.
- After clearing denominators, which must be justified, the kinematic, clearance, and margin conditions become polynomial conditions over a semialgebraic set.

## Target claim shapes

The long-term contract has the form

```text
forall theta in Theta, forall x in T, exists q in R:
    J(q) and K(q, theta, x) and C(q, theta) and S(q, theta)
```

where `J` is joint limits, `K` the kinematic task, `C` clearance to modeled obstacles, and `S` a stated singularity margin.

- **The quantifier prefix is part of the claim.** `forall theta exists q` lets the configuration depend on the realized uncertainty. `exists q forall theta` requires one configuration to work for every admissible `theta`. They are different engineering statements, and nothing may reorder them silently.
- **Certified infeasibility** means proving that the associated semialgebraic set is empty, with an independently checkable witness of emptiness. An optimizer reporting "infeasible" is not such a witness.
- **Direction of approximation.** An approximation (of geometry, joint limits, or coordinates) is sound only in the direction the quantifier needs:
  - an existential claim may shrink its domain;
  - a universal claim must enlarge it.

  For example, rounding radian joint limits *inward* to a rational half-angle box (RC-004) suits existential witnesses and would be unsound for a universal claim.

What exists today is narrower than every shape above. RC-002 concerns one fixed rational planar-2R instance, with no `theta`, no task region, and an existential witness only. Its tier is E1, and it is not registered.

## Result statuses

The result contract (`src/robocert/results.py`) defines six statuses:

| Status | Meaning | Reachable today? |
|---|---|---|
| `CERTIFIED_FEASIBLE` | A registered checker accepted a certificate for the stated claim | No: no registered checker |
| `CERTIFIED_INFEASIBLE` | A registered checker accepted an emptiness certificate | No |
| `COUNTEREXAMPLE` | An exact rational point in the claim's own domain falsifies a purely universal claim | Not from the CLI: `refute` is a library API gated by RC-007 (E0) |
| `NUMERICALLY_FEASIBLE` | A candidate was found; nothing is certified | Not from the public CLI |
| `NUMERICALLY_INFEASIBLE` | A numerical method reported infeasibility; this is never a proof | Not from the public CLI |
| `UNKNOWN` | No certificate was accepted and no checked counterexample exists | Yes, for every public `certify` call |

`UNKNOWN` never means false, unreachable, or infeasible. Failure to find a witness is not evidence of infeasibility.

Simulation outcomes (`COUNTEREXAMPLE_FOUND`, `NO_COUNTEREXAMPLE_FOUND`, `SIMULATION_ERROR`) are deliberately separate from these statuses. A violation found in MuJoCo is a lead about MuJoCo's model, not a RoboCert `COUNTEREXAMPLE`. See [backends](../architecture/backends.md).

## Terminology

- **Candidate:** any output of search, optimization, sampling, or an external solver. It carries no weight until a checker accepts a certificate for it.
- **Witness:** a concrete assignment exhibited for an existential claim, and checked exactly.
- **Certificate:** a serialized artifact that a checker can validate without trusting whatever produced it.
- **Checker:** deterministic code that accepts or rejects a certificate against a claim, bound to exact input hashes. A checker supports a `CERTIFIED_*` status only once it is registered, and registration has its own [obligations](../architecture/trusted-computing-base.md#future-certificate-family-obligation).
- **Certified:** accepted by a registered checker under the recorded assumptions. No current output qualifies.
- **Verified:** reserved for a sound verification procedure. It is never a synonym for *tested*.
- **Reachable, collision-free, singularity-free:** each must name its sense. Reachable can mean pointwise, robust, path-connected, or dynamic. Collision-free must name its geometry, uncertainty, clearance, and scope. Singularity-free must name its Jacobian, rank criterion, and margin.
- **Evidence tier (E0–E4, EX):** the review status of a *research claim* in the ledger, defined in [`research/README.md`](../../research/README.md). A tier is a property of an argument, not of a robot. Tests, proof-assistant attestations, and roadmap changes do not raise one.
