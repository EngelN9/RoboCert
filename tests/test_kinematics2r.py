from __future__ import annotations

import math
from fractions import Fraction

import pytest
from hypothesis import given
from hypothesis import strategies as st

from robocert.checkers import evaluate_formula
from robocert.errors import ValidationError
from robocert.kinematics2r import build_planar2r_claim
from robocert.specification import Polynomial, Unit

_SMALL_FRACTIONS = st.fractions(min_value=Fraction(-3), max_value=Fraction(3), max_denominator=12)

# An obstacle far from the small arms used below (max reach 10), so tests that
# aren't about obstacle geometry don't need to think about it.
_FAR_OBSTACLE = {
    "obstacle_center": (Fraction(1000), Fraction(1000)),
    "obstacle_radius": Fraction(1),
    "clearance_margin": Fraction(1),
}


def _point_segment_distance_squared(
    px: float, py: float, ax: float, ay: float, bx: float, by: float
) -> float:
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    v_dot_v = vx * vx + vy * vy
    s = max(0.0, min(1.0, (wx * vx + wy * vy) / v_dot_v))
    cx, cy = ax + s * vx, ay + s * vy
    return (px - cx) ** 2 + (py - cy) ** 2


def _evaluate(poly: Polynomial, t1: Fraction, t2: Fraction) -> Fraction:
    total = Fraction(0)
    for term in poly.terms:
        value = Fraction(term.coefficient.numerator, term.coefficient.denominator)
        for power in term.powers:
            base = t1 if power.variable_id == "t1" else t2
            value *= base**power.exponent
        total += value
    return total


def _numeric_fk_via_trig(t1: float, t2: float, l1: float, l2: float) -> tuple[float, float]:
    """Forward kinematics computed through math.cos/math.sin from the ANGLES,
    with no half-angle substitution anywhere. This is the only oracle in the
    suite genuinely independent of the rationalization under test."""
    q1 = 2 * math.atan(t1)
    q2 = 2 * math.atan(t2)
    return (
        l1 * math.cos(q1) + l2 * math.cos(q1 + q2),
        l1 * math.sin(q1) + l2 * math.sin(q1 + q2),
    )


@given(t1=_SMALL_FRACTIONS, t2=_SMALL_FRACTIONS)
def test_fk_identity_agrees_with_independent_trig_kinematics(t1: Fraction, t2: Fraction) -> None:
    """The FK identity must agree with kinematics computed through math.cos/sin
    from the angles themselves.

    This test exists because the sibling test below is NOT independent: it
    derives (x, y) from the same half-angle forms the encoding uses, so a
    consistently-mirrored substitution (e.g. sin q -> -2t/D everywhere) would
    leave it passing while the encoding certified reflected configurations.
    Only a route through the angles can catch that. See
    test_planted_sign_flip_is_caught_by_the_trig_oracle for the demonstration.
    """
    l1, l2 = Fraction(5), Fraction(3)
    x_float, y_float = _numeric_fk_via_trig(float(t1), float(t2), float(l1), float(l2))

    # Build the claim at the exact rational target the encoding would need to
    # hit, then confirm the identity vanishes there to within float tolerance.
    x = Fraction(x_float).limit_denominator(10**9)
    y = Fraction(y_float).limit_denominator(10**9)
    claim = build_planar2r_claim(
        l1=l1,
        l2=l2,
        x=x,
        y=y,
        epsilon=Fraction(1, 1000),
        **_FAR_OBSTACLE,
        t1_bounds=(Fraction(-100), Fraction(100)),
        t2_bounds=(Fraction(-100), Fraction(100)),
    )
    x_poly = next(p.left for p in claim.predicates if p.predicate_id == "fk_x_identity")
    y_poly = next(p.left for p in claim.predicates if p.predicate_id == "fk_y_identity")
    assert abs(float(_evaluate(x_poly, t1, t2))) < 1e-6
    assert abs(float(_evaluate(y_poly, t1, t2))) < 1e-6


def test_planted_sign_flip_is_caught_by_the_trig_oracle() -> None:
    """Planted-error calibration for the oracle above (BENCHMARK.md SS42, and the
    gap recorded in the Slice 1 report's SS7).

    Mirror the arm by negating both sine terms -- the transformation a
    consistently sign-flipped half-angle substitution would produce. The
    self-referential test cannot see this; the trig oracle must."""
    l1, l2, t1, t2 = Fraction(5), Fraction(3), Fraction(1, 2), Fraction(1, 3)
    x_true, y_true = _numeric_fk_via_trig(float(t1), float(t2), float(l1), float(l2))

    # The mirrored encoding reaches (x, -y): reflecting sin flips only y here.
    mirrored_y = Fraction(-y_true).limit_denominator(10**9)
    claim = build_planar2r_claim(
        l1=l1,
        l2=l2,
        x=Fraction(x_true).limit_denominator(10**9),
        y=mirrored_y,
        epsilon=Fraction(1, 1000),
        **_FAR_OBSTACLE,
        t1_bounds=(Fraction(-100), Fraction(100)),
        t2_bounds=(Fraction(-100), Fraction(100)),
    )
    y_poly = next(p.left for p in claim.predicates if p.predicate_id == "fk_y_identity")
    # Against the mirrored target the identity must NOT vanish -- if it did, the
    # encoding could not distinguish an arm from its reflection.
    assert abs(float(_evaluate(y_poly, t1, t2))) > 1e-6


@given(t1=_SMALL_FRACTIONS, t2=_SMALL_FRACTIONS)
def test_fk_identity_vanishes_exactly_at_its_own_witness(t1: Fraction, t2: Fraction) -> None:
    """Build the claim so (x, y) is DERIVED from (t1, t2) exactly (Fraction
    arithmetic, no rounding) -- then the FK identity must evaluate to exactly
    zero at that witness.

    SCOPE: this catches transcription slips in the hand-expanded quartic
    coefficients, and nothing more. It derives (x, y) from the SAME half-angle
    forms the encoding uses, so it is blind to an error in the substitution
    itself. The independent check is
    test_fk_identity_agrees_with_independent_trig_kinematics."""
    l1, l2 = Fraction(5), Fraction(3)
    d1 = 1 + t1 * t1
    d2 = 1 + t2 * t2
    cos_q1, sin_q1 = (1 - t1 * t1) / d1, 2 * t1 / d1
    cos_q2, sin_q2 = (1 - t2 * t2) / d2, 2 * t2 / d2
    x = l1 * cos_q1 + l2 * (cos_q1 * cos_q2 - sin_q1 * sin_q2)
    y = l1 * sin_q1 + l2 * (sin_q1 * cos_q2 + cos_q1 * sin_q2)

    claim = build_planar2r_claim(
        l1=l1,
        l2=l2,
        x=x,
        y=y,
        epsilon=Fraction(1, 1000),
        **_FAR_OBSTACLE,
        t1_bounds=(Fraction(-100), Fraction(100)),
        t2_bounds=(Fraction(-100), Fraction(100)),
    )
    x_poly = next(p.left for p in claim.predicates if p.predicate_id == "fk_x_identity")
    y_poly = next(p.left for p in claim.predicates if p.predicate_id == "fk_y_identity")
    assert _evaluate(x_poly, t1, t2) == 0
    assert _evaluate(y_poly, t1, t2) == 0


@given(t2=_SMALL_FRACTIONS)
def test_singularity_margin_polynomial_matches_numeric_determinant(t2: Fraction) -> None:
    l1, l2, epsilon = Fraction(5), Fraction(3), Fraction(1, 10)
    claim = build_planar2r_claim(
        l1=l1,
        l2=l2,
        x=Fraction(0),
        y=Fraction(8),
        epsilon=epsilon,
        **_FAR_OBSTACLE,
        t1_bounds=(Fraction(-10), Fraction(10)),
        t2_bounds=(Fraction(-10), Fraction(10)),
    )
    margin_poly = next(
        p.left for p in claim.predicates if p.predicate_id == "singularity_margin_ge_epsilon"
    )
    q2 = 2 * math.atan(float(t2))
    numeric_holds = abs(float(l1) * float(l2) * math.sin(q2)) >= float(epsilon) - 1e-9
    exact_holds = _evaluate(margin_poly, Fraction(0), t2) >= 0
    assert exact_holds == numeric_holds


def test_worked_instance_satisfies_every_predicate() -> None:
    # L1=L2=5, t1=1/2, t2=-1/3 -> tool (39/5, 27/5), |det J| = 15 (see plan derivation).
    claim = build_planar2r_claim(
        l1=Fraction(5),
        l2=Fraction(5),
        x=Fraction(39, 5),
        y=Fraction(27, 5),
        epsilon=Fraction(10),
        **_FAR_OBSTACLE,
        t1_bounds=(Fraction(-1), Fraction(1)),
        t2_bounds=(Fraction(-1), Fraction(1)),
    )
    t1, t2 = Fraction(1, 2), Fraction(-1, 3)
    x_poly = next(p.left for p in claim.predicates if p.predicate_id == "fk_x_identity")
    y_poly = next(p.left for p in claim.predicates if p.predicate_id == "fk_y_identity")
    assert _evaluate(x_poly, t1, t2) == 0
    assert _evaluate(y_poly, t1, t2) == 0
    # Only the ACTIVE case of each segment's disjunction needs to hold -- that's
    # exactly what the formula (not a flat "every predicate" check) captures.
    assert evaluate_formula(claim, claim.formula, {"t1": t1, "t2": t2}) is True


def test_zero_width_joint_domain_is_rejected() -> None:
    with pytest.raises(ValidationError):
        build_planar2r_claim(
            l1=Fraction(5),
            l2=Fraction(3),
            x=Fraction(1),
            y=Fraction(1),
            epsilon=Fraction(1, 10),
            **_FAR_OBSTACLE,
            t1_bounds=(Fraction(1, 2), Fraction(1, 2)),
            t2_bounds=(Fraction(-1), Fraction(1)),
        )


def test_zero_length_link_is_rejected() -> None:
    with pytest.raises(ValueError):
        build_planar2r_claim(
            l1=Fraction(0),
            l2=Fraction(3),
            x=Fraction(1),
            y=Fraction(1),
            epsilon=Fraction(1, 10),
            **_FAR_OBSTACLE,
            t1_bounds=(Fraction(-1), Fraction(1)),
            t2_bounds=(Fraction(-1), Fraction(1)),
        )


def test_chart_length_assumption_and_jacobian_units_match_the_claim() -> None:
    claim = build_planar2r_claim(
        l1=Fraction(-5),
        l2=Fraction(3),
        x=Fraction(1),
        y=Fraction(1),
        epsilon=Fraction(1, 10),
        **_FAR_OBSTACLE,
        t1_bounds=(Fraction(-1), Fraction(1)),
        t2_bounds=(Fraction(-1), Fraction(1)),
    )

    length_assumption = next(
        item for item in claim.assumptions if item.assumption_id == "nonzero_link_lengths"
    )
    singularity_margin = next(
        item for item in claim.margins if item.margin_id == "singularity_margin"
    )

    assert "nonzero" in length_assumption.statement
    assert "sign-flipped" in length_assumption.statement
    assert singularity_margin.unit is Unit.SQUARE_METRE


def test_finite_rational_t_bounds_can_never_represent_the_pi_chart_boundary() -> None:
    """t = tan(q/2) -> +-inf only as q -> +-pi; any finite rational t-bound is
    therefore automatically chart-safe (AGENTS.md SS7.2/SS46)."""
    huge = Fraction(10**9)
    claim = build_planar2r_claim(
        l1=Fraction(1),
        l2=Fraction(1),
        x=Fraction(0),
        y=Fraction(1, 2),
        epsilon=Fraction(1, 1000),
        **_FAR_OBSTACLE,
        t1_bounds=(-huge, huge),
        t2_bounds=(-huge, huge),
    )
    q1_at_bound = 2 * math.atan(float(huge))
    assert q1_at_bound < math.pi
    assert claim.domains  # constructed successfully; no float ever reaches +-inf


def test_obstacle_contact_boundary_is_exact_equality() -> None:
    """Worked instance: L1=L2=5, t1=1/2, t2=-1/3 -> elbow (3,4), tool (39/5, 27/5).
    Obstacle center (4,-3), r=49/10, mu=1/10 -> R^2=25. Segment 1's case-A distance
    (cx^2+cy^2-R^2 = 16+9-25 = 0) is an exact-equality boundary contact -- a real,
    non-generic case for free, and it must satisfy the non-strict >= exactly."""
    claim = build_planar2r_claim(
        l1=Fraction(5),
        l2=Fraction(5),
        x=Fraction(39, 5),
        y=Fraction(27, 5),
        epsilon=Fraction(1),
        obstacle_center=(Fraction(4), Fraction(-3)),
        obstacle_radius=Fraction(49, 10),
        clearance_margin=Fraction(1, 10),
        t1_bounds=(Fraction(-1), Fraction(1)),
        t2_bounds=(Fraction(-1), Fraction(1)),
    )
    t1, t2 = Fraction(1, 2), Fraction(-1, 3)
    seg1_case_a = next(p.left for p in claim.predicates if p.predicate_id == "seg1_case_a_distance")
    assert _evaluate(seg1_case_a, t1, t2) == 0
    # An exact-equality boundary contact still satisfies the non-strict >= bound,
    # so the overall claim (evaluated through its disjunctive formula) still holds.
    assert evaluate_formula(claim, claim.formula, {"t1": t1, "t2": t2}) is True


@given(t1=st.fractions(min_value=Fraction(-3), max_value=Fraction(3), max_denominator=8))
def test_segment_circle_case_selectors_pick_exactly_one_case(t1: Fraction) -> None:
    """For any t1 (with a far-away, non-interfering obstacle), exactly one of
    each segment's three (mutually exhaustive, possibly overlapping at seams)
    cases must hold -- the case split must never leave a gap."""
    l1, l2, x, y = Fraction(5), Fraction(3), Fraction(0), Fraction(6)
    claim = build_planar2r_claim(
        l1=l1,
        l2=l2,
        x=x,
        y=y,
        epsilon=Fraction(1, 1000),
        **_FAR_OBSTACLE,
        t1_bounds=(Fraction(-10), Fraction(10)),
        t2_bounds=(Fraction(-10), Fraction(10)),
    )
    t2 = Fraction(1, 4)  # arbitrary, unused by the (t1-only) clearance predicates

    def holds(predicate_id: str) -> bool:
        predicate = next(p for p in claim.predicates if p.predicate_id == predicate_id)
        value = _evaluate(predicate.left, t1, t2) - _evaluate(predicate.right, t1, t2)
        return value <= 0 if predicate.relation.value == "le" else value >= 0

    seg1_cases = [
        holds("seg1_case_a_selector"),
        holds("seg1_case_b_selector"),
        holds("seg1_case_mid_selector_lo") and holds("seg1_case_mid_selector_hi"),
    ]
    seg2_cases = [
        holds("seg2_case_a_selector"),
        holds("seg2_case_b_selector"),
        holds("seg2_case_mid_selector_lo") and holds("seg2_case_mid_selector_hi"),
    ]
    assert any(seg1_cases)
    assert any(seg2_cases)


@given(t1=st.fractions(min_value=Fraction(-3), max_value=Fraction(3), max_denominator=8))
def test_active_clearance_case_matches_numeric_point_to_segment_distance(t1: Fraction) -> None:
    l1, l2, x, y = Fraction(5), Fraction(3), Fraction(0), Fraction(6)
    cx, cy, radius, margin = Fraction(2), Fraction(9), Fraction(1, 2), Fraction(1, 10)
    claim = build_planar2r_claim(
        l1=l1,
        l2=l2,
        x=x,
        y=y,
        epsilon=Fraction(1, 1000),
        obstacle_center=(cx, cy),
        obstacle_radius=radius,
        clearance_margin=margin,
        t1_bounds=(Fraction(-10), Fraction(10)),
        t2_bounds=(Fraction(-10), Fraction(10)),
    )
    t2 = Fraction(1, 4)

    d1 = 1 + t1 * t1
    elbow_x, elbow_y = float(l1 * (1 - t1 * t1) / d1), float(2 * l1 * t1 / d1)
    numeric_dist_sq = _point_segment_distance_squared(
        float(cx), float(cy), 0.0, 0.0, elbow_x, elbow_y
    )
    r_sq = float((radius + margin) ** 2)

    seg1_mid_distance = next(
        p.left for p in claim.predicates if p.predicate_id == "seg1_case_mid_distance"
    )
    mid_selector_lo = next(
        p for p in claim.predicates if p.predicate_id == "seg1_case_mid_selector_lo"
    )
    mid_selector_hi = next(
        p for p in claim.predicates if p.predicate_id == "seg1_case_mid_selector_hi"
    )
    in_mid_case = (
        _evaluate(mid_selector_lo.left, t1, t2) >= 0
        and _evaluate(mid_selector_hi.left, t1, t2) >= 0
    )
    if in_mid_case:
        # seg1_case_mid_distance = (dist^2 - R^2) * D1^2 * L1^2, and D1^2*L1^2 > 0
        # always, so its sign matches the sign of (dist^2 - R^2) exactly.
        exact_holds = _evaluate(seg1_mid_distance, t1, t2) >= 0
        numeric_holds = numeric_dist_sq >= r_sq - 1e-6
        assert exact_holds == numeric_holds
