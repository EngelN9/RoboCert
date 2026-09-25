from __future__ import annotations

import math
from decimal import Decimal, localcontext
from fractions import Fraction

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from robocert.witness_search2r import (
    angle_to_t_candidate,
    joint_limits_to_t_bounds,
    solve_reachable_targets,
    t_bounds_to_joint_limits,
    t_to_angle,
)

_L1 = Fraction(5)
_L2 = Fraction(3)  # reach annulus is [2, 8]


def _forward_kinematics(q1: float, q2: float, l1: float, l2: float) -> tuple[float, float]:
    return (
        l1 * math.cos(q1) + l2 * math.cos(q1 + q2),
        l1 * math.sin(q1) + l2 * math.sin(q1 + q2),
    )


def test_solver_returns_nothing_outside_the_reach_annulus() -> None:
    """Emptiness is evidence of unreachability, never a proof of it -- but the
    solver must at least not fabricate candidates for impossible targets."""
    assert solve_reachable_targets(_L1, _L2, (Fraction(50), Fraction(0))) == []
    assert solve_reachable_targets(_L1, _L2, (Fraction(0), Fraction(0))) == []  # inner hole


def test_solver_finds_both_elbow_branches() -> None:
    candidates = solve_reachable_targets(_L1, _L2, (Fraction(6), Fraction(2)))
    assert {c.elbow_branch for c in candidates} == {"up", "down"}


def test_achieved_point_is_exact_and_deviation_is_consistent() -> None:
    """The achieved point must be the exact rational image of the witness, and
    the reported deviation must be exactly the squared distance to the request --
    both checkable by hand, no floats involved."""
    requested = (Fraction(6), Fraction(2))
    best = solve_reachable_targets(_L1, _L2, requested)[0]

    d1 = 1 + best.t1 * best.t1
    d2 = 1 + best.t2 * best.t2
    cos_q1, sin_q1 = (1 - best.t1 * best.t1) / d1, 2 * best.t1 / d1
    cos_q2, sin_q2 = (1 - best.t2 * best.t2) / d2, 2 * best.t2 / d2
    expected = (
        _L1 * cos_q1 + _L2 * (cos_q1 * cos_q2 - sin_q1 * sin_q2),
        _L1 * sin_q1 + _L2 * (sin_q1 * cos_q2 + cos_q1 * sin_q2),
    )
    assert best.achieved == expected
    assert best.requested == requested
    assert best.deviation_squared == (
        (best.achieved[0] - requested[0]) ** 2 + (best.achieved[1] - requested[1]) ** 2
    )


@given(
    x=st.fractions(min_value=Fraction(-7), max_value=Fraction(7), max_denominator=16),
    y=st.fractions(min_value=Fraction(-7), max_value=Fraction(7), max_denominator=16),
)
@settings(max_examples=40, deadline=None)
def test_reachable_targets_are_approached_closely(x: Fraction, y: Fraction) -> None:
    """For any target inside the annulus the best candidate must land very near
    it. This is a quality property of the untrusted search, not a soundness one:
    a poor candidate is rejected by the checker, never wrongly accepted."""
    reach = math.hypot(float(x), float(y))
    if not (2.2 < reach < 7.8):  # stay clear of the annulus boundaries
        return
    candidates = solve_reachable_targets(_L1, _L2, (x, y))
    assert candidates, (x, y)
    assert math.sqrt(float(candidates[0].deviation_squared)) < 1e-6


@pytest.mark.parametrize(
    ("lower", "upper"),
    [
        (Fraction(-5, 2), Fraction(5, 2)),
        (Fraction(-1, 2), Fraction(1, 2)),
        (Fraction(0), Fraction(3)),
        (Fraction(-31, 10), Fraction(31, 10)),  # very close to +-pi
    ],
)
def test_joint_limit_conversion_rounds_inward(lower: Fraction, upper: Fraction) -> None:
    """The soundness-relevant direction (RC-004): the certified q-interval must be
    a SUBSET of the requested one. Rounding outward would let the checker accept
    a configuration violating the user's stated joint limits."""
    t_lower, t_upper = joint_limits_to_t_bounds(lower, upper)
    q_lower, q_upper = t_bounds_to_joint_limits(t_lower, t_upper)
    assert q_lower >= float(lower)
    assert q_upper <= float(upper)
    assert q_lower < q_upper


def test_joint_limit_conversion_is_tight_enough_to_be_useful() -> None:
    """Inward rounding must not throw away meaningful range -- conservative is
    fine, useless is not."""
    t_lower, t_upper = joint_limits_to_t_bounds(Fraction(-5, 2), Fraction(5, 2))
    q_lower, q_upper = t_bounds_to_joint_limits(t_lower, t_upper)
    assert abs(q_lower - (-2.5)) < 1e-9
    assert abs(q_upper - 2.5) < 1e-9


@pytest.mark.parametrize(
    ("lower", "upper"),
    [
        (Fraction(-4), Fraction(1)),  # below -pi
        (Fraction(1), Fraction(4)),  # above +pi
        (Fraction(1), Fraction(1)),  # empty
        (Fraction(2), Fraction(1)),  # inverted
    ],
)
def test_joint_limit_conversion_rejects_unrepresentable_intervals(
    lower: Fraction, upper: Fraction
) -> None:
    with pytest.raises(ValueError):
        joint_limits_to_t_bounds(lower, upper)


def test_angle_to_t_candidate_round_trips_to_float_precision() -> None:
    for angle in (0.0, 0.339554, -0.049178, 1.4, -1.4):
        t = angle_to_t_candidate(angle)
        assert t_to_angle(t) == pytest.approx(angle, abs=1e-9)


def test_angle_to_t_candidate_is_deterministic() -> None:
    assert angle_to_t_candidate(0.339554) == angle_to_t_candidate(0.339554)


def test_angle_to_t_candidate_respects_the_chart_boundary() -> None:
    """The half-angle chart does not reach +-pi (P2 Theorem 12.1)."""

    for angle in (math.pi, -math.pi, 4.0):
        with pytest.raises(ValueError, match="strictly inside"):
            angle_to_t_candidate(angle)


def test_angle_to_t_candidate_is_monotone_like_the_true_transport() -> None:
    """tan(q/2) is strictly increasing on (-pi, pi); the rational candidate must not
    invert that, or a point could land on the wrong side of a joint limit."""

    angles = [-1.5, -0.7, -0.1, 0.0, 0.1, 0.7, 1.5]
    values = [angle_to_t_candidate(angle) for angle in angles]
    assert values == sorted(values)


def test_a_transported_interior_angle_lands_inside_the_inward_rounded_box() -> None:
    """The ordinary case: an angle well inside the joint limits survives both
    approximations -- the inward-rounded domain and the rounded point."""

    lower, upper = joint_limits_to_t_bounds(Fraction(-3, 2), Fraction(3, 2))
    assert lower <= angle_to_t_candidate(0.4) <= upper


def test_a_boundary_candidate_may_be_excluded_by_inward_rounding() -> None:
    """A conservative domain may reject a point at the requested boundary.

    Candidate conversion is approximate and independently rechecked; it has no right to
    weaken the domain's load-bearing inward direction merely to keep a boundary candidate.
    """

    q_upper = Fraction(3, 2)
    _, upper = joint_limits_to_t_bounds(Fraction(-3, 2), q_upper)
    assert upper <= angle_to_t_candidate(float(q_upper))


def test_an_angle_beyond_the_joint_limits_transports_outside_the_box() -> None:
    """The rejection path that matters: a search sampling wider than the certified region.

    `t = tan(q/2)` is strictly increasing, so an angle above the upper joint limit maps above
    the box. A consumer re-checking domain membership rejects it, and the lead is correctly
    lost rather than silently accepted at the wrong configuration.
    """

    _, upper = joint_limits_to_t_bounds(Fraction(-3, 2), Fraction(3, 2))
    lower, _ = joint_limits_to_t_bounds(Fraction(-3, 2), Fraction(3, 2))
    assert angle_to_t_candidate(1.6) > upper
    assert angle_to_t_candidate(-1.6) < lower


def test_a_coarser_denominator_buys_a_smaller_witness_at_a_cost_in_angle() -> None:
    """The size/accuracy trade the caller is choosing, pinned as a checked fact.

    Certificate size is an evaluation metric (docs/archive/initial-project-overview.md §24)
    and AGENTS.md §7.3 warns against
    gratuitous coefficient growth, so the trade needs to be visible rather than folded into
    a default nobody revisits.
    """

    angle = 0.339554
    coarse = angle_to_t_candidate(angle, denominator=10**3)
    fine = angle_to_t_candidate(angle, denominator=10**12)

    assert coarse.denominator < fine.denominator
    assert abs(t_to_angle(coarse) - angle) > abs(t_to_angle(fine) - angle)
    # Coarse is still close enough to be a usable candidate, just not a precise one.
    assert abs(t_to_angle(coarse) - angle) < 1e-3


def _decimal_tan_half(value: Fraction) -> Decimal:
    """Independent high-precision diagnostic oracle for the regression below."""

    with localcontext() as context:
        context.prec = 100
        x = (Decimal(value.numerator) / Decimal(value.denominator)) / 2
        x_squared = x * x
        sine = sine_term = x
        cosine = cosine_term = Decimal(1)
        index = 1
        while True:
            sine_term *= -x_squared / Decimal((2 * index) * (2 * index + 1))
            cosine_term *= -x_squared / Decimal((2 * index - 1) * (2 * index))
            next_sine = sine + sine_term
            next_cosine = cosine + cosine_term
            if next_sine == sine and next_cosine == cosine:
                return +(sine / cosine)
            sine, cosine = next_sine, next_cosine
            index += 1


def _decimal_fraction(value: Fraction) -> Decimal:
    with localcontext() as context:
        context.prec = 100
        return Decimal(value.numerator) / Decimal(value.denominator)


def test_joint_limit_rounding_is_inward_against_the_real_endpoint_regression() -> None:
    """Regression for the old libm comparison, which missed both directions by ~1e-17."""

    q_lower = Fraction(36, 35)
    q_upper = Fraction(79, 70)
    lower, upper = joint_limits_to_t_bounds(q_lower, q_upper)

    assert _decimal_fraction(lower) >= _decimal_tan_half(q_lower)
    assert _decimal_fraction(upper) <= _decimal_tan_half(q_upper)


@pytest.mark.parametrize("denominator", [0, -1, True])
def test_joint_limit_conversion_rejects_invalid_denominators(denominator: int) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        joint_limits_to_t_bounds(Fraction(-1), Fraction(1), denominator=denominator)
