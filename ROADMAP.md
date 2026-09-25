# RoboCert roadmap

This is the current research plan as of 2026-09-24. A roadmap item is a proposal until its mathematical claim, implementation, and evidence satisfy the [research ledger](research/CLAIMS.md) and the [production checker obligations](docs/architecture/trusted-computing-base.md#future-certificate-family-obligation). Reordering or rewording this plan changes no evidence tier and adds no capability. The former phase-by-phase plan is preserved as [historical context](docs/archive/initial-phased-roadmap.md); its phase numbers are not current milestones.

## Current baseline

Phase 0's functional core and packaging exist: formal claims, artifact hashes, result semantics, schema validation, CI, and a checker boundary. The production registry is empty, so public certification remains `UNKNOWN`. The following are research implementations, not registered checkers:

- planar 2R encoding and search;
- exact polynomial, PSD, and SOS utilities;
- refutation;
- optional simulation.

Formal proofs concern selected models and lemmas, with documented fidelity gaps.

The [ledger](research/CLAIMS.md) is authoritative for claim identifiers and tiers: RC-001 E0, RC-002 E1, RC-003 EX, RC-004 E0, RC-005 E0, RC-006 E0, and RC-007 E0. The external assessment behind this revision gave RC-003 through RC-007 different meanings. **Those assignments are not adopted.** Its new proposals are named by description in the [strategy note](docs/strategy/revised-direction.md). A proposal receives an RC identifier only when someone writes its E0 ledger entry.

## Ordered work, dependencies, and decision gates

Each gate states what must hold before the next step, and when to stop or record a failure instead.

**G0 — Documentation matches the ledger.**
- Every document uses ledger IDs and tiers only as `research/CLAIMS.md` records them.
- References to the former README and ROADMAP point into `docs/archive/`.

**G1 — Close the existing planar-2R evidence gates.** Owner-bound, highest priority.
- RC-002: the owner reads the corrigendum line by line, then a fresh frozen cross-provider referee run follows. The stopped RUN001 cannot be reused.
- RC-005: the owner reads it for E1. Its E2 counts only once RC-002 is at E2 (monotonicity).
- RC-006: the owner reads the correspondence argument. The exact SOS and PSD verifier is the shared primitive under RC-001 and any third-party certificate recheck.
- Pass condition: RC-002 and RC-005 at E2, plus implementation correspondence, per the [MVP gate record](docs/architecture/phase1-pose-tolerance-mvp-gates.md). Until then the registry stays empty.

**G2 — Specify a robust singularity-margin family (RC-001).**
- State the exact planar claim, the parameter box, and a *margin-shrunk* inequality (a strict positive margin rather than `>= 0`), so that a rounded certificate can lie in the interior of the SOS cone.
- When its argument is written, RC-001 should declare its dependency on RC-006.
- An SDP solver is an untrusted, optional generator. Its output is a candidate only.
- Pass condition: a first rational reconstruction is accepted by the exact verifier on a small instance.
- Failure record: if rounding fails because the certificate sits on the cone boundary, log the attempt in `research/ATTEMPTS.md` with the diagnosed step rather than retrying silently.

**G3 — Uncertainty-inflation lemma (proposal; a future E0 claim).** The idea: a configuration whose clearance exceeds the margin by an explicit displacement bound keeps the margin over a joint-space box. Any statement must:
- use *actual-link* clearance, as in RC-005, never the RC-002 second-link conjunct, which P2 Remark 9.5 shows is unsound on its own (compare A-001 and A-003);
- convert radian boxes to half-angle boxes by rounding *outward*. RC-004's inward rounding is sound for existential claims and would be unsound for a universal one;
- be supported by tests that try to falsify the bound near the margin.

Its tier can never exceed RC-005's.

**G4 — Precision SCARA-style feasibility measurement (proposal).**
- Evaluate a documented planar slice with declared dimensional, calibration, and encoder-error intervals. Keep repeatability separate from absolute accuracy.
- Vendor specifications are assumptions to verify, not guarantees.
- Stop condition: if the inflated margin at the chosen scale exceeds plausible clearances, drop the micrometer-scale demonstrator rather than escalating methods to rescue it.

**G5 — Exact recheck of third-party configuration-space certificates (proposal, timeboxed).**
- First establish whether the tool can export monomial bases, Gram matrices, separating-plane polynomials, and region data.
- If it can, the recheck needs more than the SOS identity. It also needs a new reduction claim covering the region's semantics in half-angle coordinates, joint-range containment, the meaning of the separating planes, and the obstacle geometry. Any literature it relies on needs `research/literature/` entries first.
- Stop condition: if export is impractical, shelve the work. Do not rebuild it on RoboCert's own SOS pipeline, which would tie it to RC-001.
- Solver success is never checker acceptance.

**Deferred** (separate proposed claims, each entering at E0):
- multi-link point witnesses, which need a kernel that accepts a rigid offset body given by a rational vector rather than a scalar link length;
- multiple obstacles and self-collision;
- planar remote-center-of-motion;
- planar virtual-fixture geometry;
- spatial 3R, then full-pose 6R/7R.

**Outside the current plan:** CAD ingestion, path or trajectory certification, dynamics, network or latency behaviour, and digital-twin fidelity.

Work on search utilities or documentation may proceed independently when it keeps the public gate closed.

## Acceptance for any future certificate family

A family needs:
- an exact claim and quantifier domain;
- explicit units and the direction of every geometry approximation;
- reproducible certificate and model hashes;
- a deterministic independent checker;
- positive, negative, boundary, and corruption tests.

Unresolved boxes, unsupported inputs, timeouts, failed reconstruction, and checker exceptions remain `UNKNOWN`. A checked statement about a model does not establish physical-system safety.

See [proposed methods](docs/architecture/proposed-methods.md), [certification goals](docs/concepts/certification-goals.md), and the [strategy note](docs/strategy/revised-direction.md) for detail and open questions.
