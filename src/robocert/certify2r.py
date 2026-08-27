"""Historical research driver for four-chart planar-2R witness experiments.

This module is deliberately not wired into the public CLI while RC-002 remains
below E2. It must not be treated as a production certificate backend.

Orchestration only. This module builds claims, assembles candidate certificates,
and submits them to `robocert.checking.verify_certificate`; it never decides
acceptance itself (AGENTS.md SS20 -- search and orchestration must not emit
`CERTIFIED_*`, only the checker gate may).

The four-chart construction implements proof P2 SS13. The half-angle chart
`t = tan(q/2)` covers only `q in (-pi, pi)`, and P2 Theorem 12.1 exhibits
explicit rational data whose only admissible configuration has `q1 = pi` --
unreachable by any finite `t`. P2 Theorem 13.5 recovers full torus coverage by
running the SAME predicate at the four sign-flipped link-length pairs
`(+-L1, +-L2)`; a configuration is admissible somewhere on the torus iff at
least one of the four is satisfiable.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from fractions import Fraction

from robocert.artifacts import ArtifactDigest
from robocert.certificates import Certificate, CertificateConclusion
from robocert.checkers import PLANAR2R_EXACT_WITNESS_FAMILY, planar2r_exact_witness_checker
from robocert.checking import CheckReport, verify_certificate
from robocert.kinematics2r import build_planar2r_claim
from robocert.specification import Claim
from robocert.witness_search2r import solve_reachable_targets, witness_payload

# P2 Notation 13.1: delta in {0, pi}^2, recorded as integer multiples of pi so
# the chart offset stays exact (pi has no rational representation).
CHART_OFFSETS: tuple[tuple[int, int], ...] = ((0, 0), (1, 0), (0, 1), (1, 1))


def chart_link_lengths(
    l1: Fraction, l2: Fraction, offset: tuple[int, int]
) -> tuple[Fraction, Fraction]:
    """P2 Notation 13.1: lambda(delta) = (eta1*L1, eta1*eta2*L2).

    Yields exactly the four sign choices (+-L1, +-L2) as `offset` ranges over
    CHART_OFFSETS -- verified against P2's explicit enumeration.
    """
    n1, n2 = offset
    eta1 = -1 if n1 else 1
    eta2 = -1 if n2 else 1
    return (eta1 * l1, eta1 * eta2 * l2)


def chart_configuration(t1: Fraction, t2: Fraction, offset: tuple[int, int]) -> tuple[float, float]:
    """Map a chart-local witness back to the true configuration q + delta.

    Returns floats: q = 2*arctan(t) + n*pi is transcendental and has no exact
    rational form. This is REPORTING ONLY -- nothing in the checked path ever
    sees these values (AGENTS.md SS22.3).
    """
    n1, n2 = offset
    return (
        2 * math.atan(float(t1)) + n1 * math.pi,
        2 * math.atan(float(t2)) + n2 * math.pi,
    )


@dataclass(frozen=True, slots=True)
class Planar2RProblem:
    """A fully rational planar-2R certification instance."""

    l1: Fraction
    l2: Fraction
    target: tuple[Fraction, Fraction]
    obstacle_center: tuple[Fraction, Fraction]
    obstacle_radius: Fraction
    clearance_margin: Fraction
    epsilon: Fraction
    t1_bounds: tuple[Fraction, Fraction]
    t2_bounds: tuple[Fraction, Fraction]
    problem_id: str = "planar2r.instance"


def build_chart_claim(problem: Planar2RProblem, offset: tuple[int, int]) -> Claim:
    """Build the claim for one chart of `problem` (P2 Definition 10.1 at lambda)."""
    lam1, lam2 = chart_link_lengths(problem.l1, problem.l2, offset)
    x, y = problem.target
    return build_planar2r_claim(
        l1=lam1,
        l2=lam2,
        x=x,
        y=y,
        epsilon=problem.epsilon,
        obstacle_center=problem.obstacle_center,
        obstacle_radius=problem.obstacle_radius,
        clearance_margin=problem.clearance_margin,
        t1_bounds=problem.t1_bounds,
        t2_bounds=problem.t2_bounds,
        claim_id=f"{problem.problem_id}.chart{offset[0]}{offset[1]}",
    )


def candidate_certificate(
    claim: Claim,
    model_hash: ArtifactDigest,
    t1: Fraction,
    t2: Fraction,
    certificate_id: str = "planar2r-candidate",
) -> Certificate:
    """Assemble an unchecked candidate certificate for a witness.

    Construction implies nothing about validity; only `verify_certificate` can
    accept it. Checker identity fields are taken from the registered checker so
    a version bump cannot silently desynchronize them.
    """
    checker = planar2r_exact_witness_checker
    return Certificate(
        certificate_id=certificate_id,
        family=PLANAR2R_EXACT_WITNESS_FAMILY,
        conclusion=CertificateConclusion.FEASIBLE,
        claim_hash=claim.digest(),
        model_hash=model_hash,
        assumption_ids=tuple(item.assumption_id for item in claim.assumptions),
        checker_id=checker.checker_id,
        checker_version=checker.checker_version,
        arithmetic_mode=checker.arithmetic_mode,
        payload=witness_payload(t1, t2),
        provenance=claim.provenance,
    )


def check_witness_on_chart(
    problem: Planar2RProblem,
    offset: tuple[int, int],
    t1: Fraction,
    t2: Fraction,
    model_hash: ArtifactDigest,
) -> tuple[Claim, Certificate, CheckReport]:
    """Submit one witness on one chart to the checker gate.

    Returns the artifacts alongside the report so a caller can serialize exactly
    what was checked. The report's `accepted` flag is the only authority here.
    """
    claim = build_chart_claim(problem, offset)
    certificate = candidate_certificate(claim, model_hash, t1, t2)
    return claim, certificate, verify_certificate(claim, model_hash, certificate)


@dataclass(frozen=True, slots=True)
class CertificationOutcome:
    """What `certify_problem` established, and everything needed to re-check it."""

    accepted: bool
    diagnostics: tuple[str, ...]
    chart: tuple[int, int] | None = None
    witness: tuple[Fraction, Fraction] | None = None
    achieved: tuple[Fraction, Fraction] | None = None
    deviation_squared: Fraction | None = None
    configuration: tuple[float, float] | None = None
    claim: Claim | None = None
    certificate: Certificate | None = None


def certify_problem(problem: Planar2RProblem, model_hash: ArtifactDigest) -> CertificationOutcome:
    """Search all four charts for a certifiable witness and submit it to the gate.

    Returns the first accepted result, preferring smaller deviation from the
    requested target. A negative outcome means no witness was found and checked
    -- NOT that none exists. Proof P2 Theorem 12.1 shows the encoding can miss
    genuinely admissible configurations, and inward-rounded joint limits and the
    reconstruction ladder add two more ways to come up empty. Callers must map
    this to UNKNOWN, never to infeasibility (P2 Warning 11.5).
    """
    attempted = 0
    for offset in CHART_OFFSETS:
        lam1, lam2 = chart_link_lengths(problem.l1, problem.l2, offset)
        for candidate in solve_reachable_targets(lam1, lam2, problem.target):
            attempted += 1
            # Certify the point the witness EXACTLY reaches, not the requested
            # one -- an exact FK equality is unreachable by a reconstructed
            # rational. The deviation is reported so the gap is visible.
            achieved_problem = replace(problem, target=candidate.achieved)
            claim, certificate, report = check_witness_on_chart(
                achieved_problem, offset, candidate.t1, candidate.t2, model_hash
            )
            if report.accepted:
                return CertificationOutcome(
                    accepted=True,
                    diagnostics=report.diagnostics,
                    chart=offset,
                    witness=(candidate.t1, candidate.t2),
                    achieved=candidate.achieved,
                    deviation_squared=candidate.deviation_squared,
                    configuration=chart_configuration(candidate.t1, candidate.t2, offset),
                    claim=claim,
                    certificate=certificate,
                )

    reason = (
        f"no witness accepted after {attempted} candidate(s) across {len(CHART_OFFSETS)} charts"
        if attempted
        else "inverse kinematics found no solution on any chart"
    )
    return CertificationOutcome(accepted=False, diagnostics=(reason,))


__all__ = [
    "CHART_OFFSETS",
    "CertificationOutcome",
    "Planar2RProblem",
    "build_chart_claim",
    "candidate_certificate",
    "certify_problem",
    "chart_configuration",
    "chart_link_lengths",
    "check_witness_on_chart",
]
