# Method families and their proof obligations

This page lists the certificate and search methods RoboCert has implemented as research code or proposes to study. Each has a **status**:

- **Implemented (research, unregistered):** code exists, but no production checker is registered for it, so it cannot produce a `CERTIFIED_*` result.
- **Proposal:** not implemented. It may not yet have a ledger claim.

Being listed here grants no tier and authorizes no registration. Tiers live in [`research/CLAIMS.md`](../../research/CLAIMS.md). Registration requires the [certificate-family obligation](trusted-computing-base.md#future-certificate-family-obligation). The role of external solvers is fixed in [backends](backends.md): each is an untrusted generator whose output a RoboCert checker must re-derive exactly.

The original design discussion is in the [archived overview](../archive/initial-project-overview.md), §8–12 and §19–22.

## Families

| Family | Status | Ledger | What the checker must decide | Open obligations |
|---|---|---|---|---|
| Exact point witness (planar 2R) | Implemented (research, unregistered) | RC-002 E1 | Exact rational evaluation of every atom at the witness, inside the claim's box | RC-002 corrigendum read and a fresh referee run; implementation correspondence; four-chart coverage is separate from the single-chart encoding |
| Pose-tolerance witness with actual-link clearance | Proposal (proof written, no code) | RC-005 E0 | The same, with the tolerance inequality and actual rationalized link endpoints | Owner read; E2 after RC-002; problem schema v0.2.0 and payload schema not written |
| SOS / Positivstellensatz verification | Utility implemented (research, unbound) | RC-006 E0 | The polynomial identity `target - gamma = sigma_0 + sum sigma_i g_i + sum lambda_j h_j`, with every Gram matrix exactly PSD over Q | Owner read of the correspondence argument. No robot-property reduction is bound to it. |
| Robust singularity margin via SOS | Proposal | RC-001 E0 | An RC-006-accepted certificate for a *margin-shrunk* margin polynomial over an explicit parameter box | Precise statement; soundness argument; rational reconstruction strategy; interior-of-cone design |
| Refutation by exact counterexample | Implemented (library only) | RC-007 E0 | A single-read rational assignment in the domain, a purely universal prefix, and a formula evaluating false | Owner read; stays out of the CLI and reports until E1 |
| Joint-limit rationalization | Implemented (research) | RC-004 E0 | That the half-angle box lies *inside* the requested radian interval | Owner read; the inward direction suits existential claims only |
| Uncertainty inflation (Lipschitz displacement bound) | Proposal | none | That clearance at a point, minus an explicit displacement bound, yields clearance over a joint box | Needs actual-link clearance and an outward radian-to-half-angle enclosure; see the [roadmap](../../ROADMAP.md), G3 |
| Convex separation / configuration-space regions (C-IRIS-type) | Proposal | none (background: LIT-001) | The SOS identities and PSD conditions, *plus* the region's semantics, joint-range containment, separating-plane meaning, and obstacle geometry | Artifact-export feasibility; a new reduction claim; literature entries for any result relied on |
| Interval enclosure, interval Newton / Krawczyk, branch-and-bound | Proposal | none | Sound outward-rounded enclosures and exact leaf checks | Not implemented. `IntervalDomain` is a rational domain type, not interval arithmetic. |
| Exact algebraic (Gröbner cofactors, resultants, root isolation) | Proposal; identity check reusable | none | The cofactor identity `sum h_i f_i = g` by exact polynomial arithmetic (`polynomial.py`) | Which claim shapes it would serve; algebraic-number witnesses need verified root isolation |
| Rational reconstruction from floating-point certificates | Proposal | none | Nothing extra: the reconstructed certificate is checked as any other certificate | Failure is `UNKNOWN`, never infeasibility |
| Simulation falsification (MuJoCo) | Implemented (optional extra) | none | Not applicable: its output is never a certificate | Model correspondence to any claim; see [backends](backends.md) |

## Geometry levels

A clearance claim must name its geometry representation and the direction of approximation. For conservative exclusion, the modeled body must contain the true one.

| Level | Representation | Status |
|---|---|---|
| A | Analytic convex primitives (circles and segments in the plane; spheres, capsules, boxes) | Planar point and segment against circle in research code; spatial primitives are proposals |
| B | Certified convex decomposition with a documented containment relation | Proposal |
| C | Algebraic surface models `g_i(x) >= 0` | Proposal |
| D | General CAD / B-Rep | Out of the current plan. A visually accurate tessellation is not a conservative representation. |

## Numerical trust levels

| Level | Arithmetic | Allowed use |
|---|---|---|
| 0 | Floating point | Search and candidate generation only |
| 1 | High precision | Conditioning and reconstruction; not rigorous by itself |
| 2 | Interval / directed rounding | Validated enclosures (not implemented) |
| 3 | Exact rational | Final checking. All current research checkers use this level. |

A small displayed value is never read as zero because it is small.
