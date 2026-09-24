# Revised direction: rationale and open questions

Date: 2026-09-24. This note records why the [roadmap](../../ROADMAP.md) was reordered after an external assessment (received by the owner and not committed to this repository) was compared with the repository. **It is a planning record. It is not evidence, it changes no evidence tier, and it adds no certification capability.** The public registry remains empty, and `certify` returns `UNKNOWN`.

Literature cited here is limited to entries under `research/literature/`. The assessment cited further papers, vendor specifications, and standards. None of those has a verified literature entry, so they appear below only as unverified assertions of the assessment.

## Positioning

The assessment argued that RoboCert should not compete on how many degrees of freedom it can cover. Configuration-space region methods of the C-IRIS family (LIT-001) already use the same rational parametrization and scale further. RoboCert's distinctive aim is the combination of:

- exact, independently checkable arithmetic;
- target reachability;
- a singularity margin;

all stated as one claim. The repository already follows this reasoning: [backends](../architecture/backends.md) treats C-IRIS-type output as a candidate that the exact SOS verifier must recheck.

## Adopted, as proposals

Each item below is a proposal, named by description rather than claim ID. It enters `research/CLAIMS.md` at E0 only when someone writes a statement and argument for it.

| Proposal | Where it sits | Condition |
|---|---|---|
| Margin-shrunk SOS targets for RC-001, so a rounded certificate can lie in the interior of the SOS cone | Roadmap G2 | Depends on the RC-006 verifier |
| Uncertainty-inflation lemma (explicit displacement bound turning a point margin into a box statement) | Roadmap G3 | Must use actual-link clearance and outward enclosures |
| Precision SCARA-style planar demonstrator | Roadmap G4 | Only after measuring that margins stay useful |
| Exact recheck of third-party configuration-space certificates | Roadmap G5 | Timeboxed; stops if artifacts cannot be exported |
| Tolerance-form targets instead of exact equalities | Already RC-005 (E0) | No new claim needed |
| Claim, assumptions, evidence, and independent check stated together in every future report | Existing policy (`AGENTS.md`) | Nothing new |

## Not adopted

- **Renumbering.** The assessment used RC-003 to RC-007 for other claims (a 3R witness, multi-obstacle witnesses, robust nR, spatial 3R, spatial RCM). The ledger's IDs stand. EX entries are never deleted, and reusing an ID would change what every existing reference to it means.
- **"Tolerance reach depends on RC-002 only."** This is the route refuted by A-001 (RC-003, EX). A tolerance claim has to use the actual link endpoints, as RC-005 does.
- **"RC-002 is complete."** RC-002 is E1. Its only frozen referee run stopped with substantive findings (A-002), and it is not registered.
- **Treating `IntervalDomain` as an uncertainty engine.** It is a rational interval *type* for quantifier domains (`src/robocert/specification.py`). RoboCert has no interval arithmetic, enclosure, or branch-and-bound code.

## Technical corrections recorded

1. **Clearance must be actual-link.** RC-002's second-link clearance conjunct reads the fixed target as the link endpoint. P2 Remark 9.5 shows it is unsound when detached from the exact forward-kinematics equalities (`research/ATTEMPTS.md` A-001 and A-003). Any universal or inflation claim must use the RC-005-style encoding.
2. **The rounding direction follows the quantifier.** RC-004 rounds joint limits *inward*, which is sound for existential witnesses. A universal claim over a joint box needs an *outward* enclosure, and needs its own claim.
3. **Rechecking a C-IRIS-type certificate is more than an SOS check.** Beyond the identity and PSD conditions, a recheck must establish:
   - the region's meaning in half-angle coordinates;
   - containment within the chart and joint range;
   - what the separating planes assert;
   - the obstacle geometry.

   That is a new reduction claim, starting at E0.
4. **Multi-link reduction.** Freezing distal joints at rational values gives a rigid offset body with a rational offset vector, whose length is generally irrational. A 2R-style kernel would need to accept that vector. The present kernel takes scalar link lengths.

## Already implemented (not new work)

- **Exact-target reachability.** A rational witness generally cannot hit an independently chosen target exactly. The research driver (`src/robocert/certify2r.py`) certifies the point the witness actually reaches and reports the deviation. The 2026-08-28 adversary note records an exact instance that is satisfiable but has no rational witness in its box. The note proposes it as a regression fixture for "search failure must return `UNKNOWN`" (`research/notes/2026-08-28-rc005-adversary-search.md`, item d).
- **Exact certificate checking primitives.** Exact polynomial identity, exact PSD with a zero-pivot guard, and SOS verification exist (`polynomial.py`, `linalg_exact.py`, `sos.py`; RC-006). What remains is review, not construction.
- **Generation separated from validation for region methods.** Required by `AGENTS.md` §11.4 and reflected in [backends](../architecture/backends.md).

## Unverified assumptions in the assessment

- **Demand.** That exact verification is valued by regulators or industry. The assessment itself found no standard that requires formal proofs.
- **The C-IRIS exactness gap.** That published configuration-space certificates are never re-verified exactly. This rests on the absence of such a description in the sources consulted, which the assessment itself flags as uncertain.
- **Vendor figures.** Repeatability, accuracy, and payload figures for commercial arms and joint modules come from vendor or reseller material, and are indicative at most.
- **Scaling.** Branch-and-bound and SOS scaling for planar chains with more than two links is unmeasured.

## Decision gates and stop conditions

See the [roadmap](../../ROADMAP.md) for the full ordering.

- **G1** is owner-bound and comes first:
  - owner reads of the RC-002 corrigendum, RC-005, and RC-006;
  - a fresh frozen referee run for RC-002.
- **G2** records a boundary-rounding failure in `ATTEMPTS.md` rather than retrying silently.
- **G3's** claim tier can never exceed RC-005's.
- **G4** stops the micrometer-scale demonstrator if the inflated margin exceeds plausible clearance.
- **G5** stops if certificate artifacts cannot be exported. It is not rebuilt on RoboCert's own SOS pipeline.

## Open owner decisions

1. Whether the G3 inflation lemma is drafted now as E0 work, in parallel with G1, or waits for RC-005's E1 read.
2. Whether the G5 export spike is worth funding while the demand case remains unverified.
3. Whether to create literature entries (via the `cite` skill) for the additional sources the assessment relied on, before any of them is used in a claim.
