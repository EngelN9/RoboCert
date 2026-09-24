# Examples

Three historical planar-2R research inputs used by the public-gate regression
tests. No E2-approved production checker is registered, so every public
`certify` invocation currently returns `UNKNOWN` without running the legacy
search or constructing a certificate.

| File | Verdict | Exit | Why |
|---|---|---|---|
| `reachable.json` | `UNKNOWN` | 1 | The production certification gate is closed; reachability is not evaluated. |
| `obstacle-blocked.json` | `UNKNOWN` | 1 | The production certification gate is closed; clearance is not evaluated. |
| `out-of-reach.json` | `UNKNOWN` | 1 | The production certification gate is closed; infeasibility is not evaluated. |

Run one:

```bash
robocert certify examples/reachable.json -o /tmp/run
robocert check /tmp/run
```

## Reading the verdicts

`UNKNOWN` means no certificate was accepted. It does **not** mean the property
is false, the target is unreachable, or an obstacle blocks every witness. The
current public command deliberately does not run search, joint-coordinate
conversion, claim construction, or checking. `robocert check` likewise accepts
no stored artifact while the gate is closed.

## Simulation falsification (optional `mujoco` extra)

`simulation/` is a different kind of example. It does not call `certify` or `check` and it
produces no certificate. It runs adversarial sampling against a candidate safe joint region in
MuJoCo, looking for a configuration that violates a clearance property.

```bash
pip install "robocert[mujoco]"
```

```bash
python examples/simulation/falsify_planar_2r.py run/simulation
```

Two candidate regions are attacked with one seed and 200 samples each:

| Region | Outcome | Why |
|---|---|---|
| `optimistic` | `COUNTEREXAMPLE_FOUND` | The joint box sweeps the arm through the obstacle. |
| `conservative` | `NO_COUNTEREXAMPLE_FOUND` | The arm is folded away from the obstacle. |

### Reading these outcomes

`COUNTEREXAMPLE_FOUND` is **not** RoboCert's `COUNTEREXAMPLE` status. `planar_2r.xml` models
link inertia, contact compliance, actuators, and gravity — none of which the algebraic planar-2R
model contains. A violation found here refutes a statement about MuJoCo's model and is a *lead*
for exact re-validation against RoboCert's own, nothing more.

`NO_COUNTEREXAMPLE_FOUND` records a search that found no violation. It says 200 sampled points did not break the
property; it says nothing about the continuum they were drawn from, and it is not evidence that
the region is collision-free.

`SIMULATION_ERROR` records detected search failures, including asking for more clearance than the model's
collision margin can observe. That case is refused before sampling rather than answered from
geometry pairs MuJoCo never examined.

Validated simulation records reject non-finite numbers, and property constructors reject
negative or non-finite thresholds. Search failures and direct API validation errors have
different interfaces; direct helper calls can raise `ValueError`. Remaining adapter and
validation gaps are tracked in the [implementation audit](../research/reports/2026-09-07-counterexample-simulation-audit.md).

Each search writes a canonical-JSON report recording the MuJoCo version, model hash, seed,
timestep, solver settings, sample count, and the violating configuration.

## Writing your own

The disabled public boundary only checks that the file is JSON and refuses JSON
float literals. It does not validate the historical problem schema or interpret
its joint limits, margins, or geometry. Decimal values should still be written
as strings so future exact parsers do not receive binary floating-point values.

The proposed `0.2.0` format will require exact rational principal-chart bounds
directly. It is intentionally not implemented before RC-002 and RC-005 reach E2.

Full field reference:

```bash
robocert schema problem.schema.json
```
