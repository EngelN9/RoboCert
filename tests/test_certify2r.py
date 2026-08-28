from __future__ import annotations

import math
from fractions import Fraction

import pytest

from robocert import checking
from robocert.artifacts import ArtifactDigest, digest_json
from robocert.certify2r import (
    CHART_OFFSETS,
    Planar2RProblem,
    chart_configuration,
    chart_link_lengths,
    check_witness_on_chart,
)
from robocert.checkers import PLANAR2R_EXACT_WITNESS_FAMILY, planar2r_exact_witness_checker
from robocert.results import ResultStatus, certified_result


@pytest.fixture(autouse=True)
def _enable_research_checker_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """Exercise the historical theorem seam without production registration."""

    monkeypatch.setattr(
        checking,
        "_PRODUCTION_CHECKERS",
        {PLANAR2R_EXACT_WITNESS_FAMILY: planar2r_exact_witness_checker},
    )


# Proof P2 Theorem 12.1, verbatim. This instance is PROVED to have an admissible
# configuration q = (pi, pi/2) on the torus, while the single-chart encoding has
# no real solution at all -- the arm must fold back along -x, which t = tan(q/2)
# cannot express. P2 Remark 13.6 works through the recovery: chart delta = (pi, 0)
# with witness t = (0, 1).
_THEOREM_12_1 = Planar2RProblem(
    l1=Fraction(1),
    l2=Fraction(1),
    target=(Fraction(-1), Fraction(-1)),
    obstacle_center=(Fraction(0), Fraction(-1, 2)),
    obstacle_radius=Fraction(1, 5),
    clearance_margin=Fraction(1, 10),  # R = r + mu = 3/10
    epsilon=Fraction(1, 2),
    t1_bounds=(Fraction(-10), Fraction(10)),
    t2_bounds=(Fraction(-10), Fraction(10)),
    problem_id="p2.theorem12_1",
)


def _model_hash() -> ArtifactDigest:
    return digest_json({"model": "p2-theorem-12-1"})


def test_chart_link_lengths_match_p2_notation_13_1() -> None:
    """P2 SS13 enumerates lambda(delta) explicitly; reproduce that table exactly."""
    l1, l2 = Fraction(3), Fraction(7)
    assert chart_link_lengths(l1, l2, (0, 0)) == (Fraction(3), Fraction(7))
    assert chart_link_lengths(l1, l2, (1, 0)) == (Fraction(-3), Fraction(-7))
    assert chart_link_lengths(l1, l2, (0, 1)) == (Fraction(3), Fraction(-7))
    assert chart_link_lengths(l1, l2, (1, 1)) == (Fraction(-3), Fraction(7))
    # The four offsets must yield the four sign choices, each exactly once.
    assert len({chart_link_lengths(l1, l2, o) for o in CHART_OFFSETS}) == 4


def test_theorem_12_1_is_rejected_on_the_principal_chart() -> None:
    """The negative half of P2 Theorem 12.1: no real solution on chart (0,0).

    Sampled densely rather than proved here -- the proof is P2's. This pins that
    our encoding really does exhibit the gap the four-chart driver exists to fix,
    so the acceptance test below is measuring something.
    """
    _, _, report = check_witness_on_chart(
        _THEOREM_12_1, (0, 0), Fraction(0), Fraction(1), _model_hash()
    )
    assert report.accepted is False

    # And no other witness on this chart works either: the FK identity forces
    # cos(q2) = 0, and P2 shows the only two solutions are q1 = pi (off-chart)
    # and q1 = -pi/2 (obstacle intrusion).
    for numerator in range(-40, 41):
        t1 = Fraction(numerator, 8)
        for t2 in (Fraction(1), Fraction(-1)):  # q2 = +-pi/2, the only FK-feasible values
            _, _, probe = check_witness_on_chart(_THEOREM_12_1, (0, 0), t1, t2, _model_hash())
            assert probe.accepted is False, (t1, t2)


def test_theorem_12_1_certifies_on_the_flipped_chart() -> None:
    """The recovery of P2 Remark 13.6: chart delta = (pi, 0), witness t = (0, 1).

    This is the whole point of four-chart coverage -- a configuration that is
    genuinely admissible, that the principal chart cannot see.
    """
    claim, certificate, report = check_witness_on_chart(
        _THEOREM_12_1, (1, 0), Fraction(0), Fraction(1), _model_hash()
    )
    assert report.accepted is True, report.diagnostics
    assert report.checked_certificate is not None

    result = certified_result(report.checked_certificate)
    assert result.status is ResultStatus.CERTIFIED_FEASIBLE
    assert result.claim_hash == claim.digest()
    assert certificate.family == "planar2r.exact_witness"


def test_recovered_configuration_is_the_one_the_proof_names() -> None:
    """P2 Theorem 12.1(1) names q = (pi, pi/2) as the admissible configuration.
    Mapping the chart-local witness back through q + delta must land there."""
    q1, q2 = chart_configuration(Fraction(0), Fraction(1), (1, 0))
    assert math.isclose(q1, math.pi, abs_tol=1e-12)
    assert math.isclose(q2, math.pi / 2, abs_tol=1e-12)


def test_recovered_configuration_is_independently_admissible() -> None:
    """Verify the recovered q against the geometry directly, in floats, with no
    reference to the encoding -- the same check P2 Theorem 12.1(1) performs by
    hand. If this disagrees with the certificate, the encoding is wrong."""
    q1, q2 = chart_configuration(Fraction(0), Fraction(1), (1, 0))
    l1, l2 = 1.0, 1.0
    elbow = (l1 * math.cos(q1), l1 * math.sin(q1))
    tool = (elbow[0] + l2 * math.cos(q1 + q2), elbow[1] + l2 * math.sin(q1 + q2))

    assert math.isclose(tool[0], -1.0, abs_tol=1e-9)
    assert math.isclose(tool[1], -1.0, abs_tol=1e-9)
    assert abs(l1 * l2 * math.sin(q2)) >= 0.5 - 1e-12

    cx, cy, radius = 0.0, -0.5, 0.3

    def segment_distance(ax: float, ay: float, bx: float, by: float) -> float:
        vx, vy = bx - ax, by - ay
        wx, wy = cx - ax, cy - ay
        s = max(0.0, min(1.0, (wx * vx + wy * vy) / (vx * vx + vy * vy)))
        return math.hypot(cx - (ax + s * vx), cy - (ay + s * vy))

    assert segment_distance(0.0, 0.0, *elbow) >= radius - 1e-12
    assert segment_distance(elbow[0], elbow[1], *tool) >= radius - 1e-12


@pytest.mark.parametrize("offset", CHART_OFFSETS)
def test_every_chart_builds_a_well_formed_claim(offset: tuple[int, int]) -> None:
    """Negative link lengths must flow through claim construction unobstructed --
    P2 (H1) requires only L_i != 0, and the four-chart repair needs the sign
    flips. A positivity guard here would foreclose Theorem 13.5."""
    claim, certificate, _ = check_witness_on_chart(
        _THEOREM_12_1, offset, Fraction(0), Fraction(1), _model_hash()
    )
    assert claim.digest() == certificate.claim_hash
    assert len(claim.predicates) == 16  # 2 FK + 1 margin + 13 clearance
