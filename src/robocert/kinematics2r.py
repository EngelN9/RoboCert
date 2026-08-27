"""Research-only planar 2R exact-witness Claim construction.

Given one fixed rational instance, this module builds a candidate `Claim` about
an exact rational witness. It does not certify that claim, and its RC-002 family
is not registered for production while the E2 gate remains open.

Limitations (see AGENTS.md §68 for the full target theorem this is one instance
of): no robustness across any link-length interval (`forall theta`) or task-region
box (`forall x`) -- L1, L2, x, y, and the obstacle are fixed rational constants
baked into predicate coefficients, not quantified variables. `q = pi` is excluded
by construction: only finite rational `t` bounds are ever used, and
`t = tan(q/2) -> +-inf` only as `q -> +-pi`, so no finite rational `t` can ever
represent that chart boundary.
"""

from __future__ import annotations

from fractions import Fraction

from robocert.artifacts import digest_json
from robocert.specification import (
    Assumption,
    BoxDomain,
    Claim,
    Formula,
    GeometrySemantics,
    IntervalDomain,
    Margin,
    MonomialPower,
    Polynomial,
    Predicate,
    ProvenanceEntry,
    QuantifierBlock,
    QuantifierKind,
    Rational,
    Relation,
    Term,
    UncertaintySemantics,
    Unit,
    Variable,
)

CLAIM_ID = "phase1.benchmark_a.planar2r_exact_witness.v1"


def _rational(value: Fraction) -> Rational:
    return Rational(value.numerator, value.denominator)


def _mono(coefficient: Fraction, **powers: int) -> Term | None:
    """A single monomial term, or None if its coefficient is zero (Term rejects
    zero coefficients as non-canonical, so zero terms must be filtered here, not
    left for Polynomial to drop)."""
    if coefficient == 0:
        return None
    return Term(
        _rational(coefficient),
        tuple(MonomialPower(name, exponent) for name, exponent in powers.items() if exponent),
    )


def _poly(*terms: Term | None) -> Polynomial:
    return Polynomial(tuple(term for term in terms if term is not None))


_ScratchKey = tuple[tuple[str, int], ...]


class _ScratchPolynomial:
    """Internal multivariate polynomial over Fraction with +, -, * -- used only to
    derive the obstacle-clearance predicates, where hand-expanding the quartics
    directly (as _fk_numerator_polynomials does) would be error-prone (AGENTS.md
    SS7.3/SS8.1: mechanical derivation over hand algebra for anything nontrivial).
    Not part of any public API; converted to `Polynomial` only at the boundary.
    """

    __slots__ = ("terms",)

    def __init__(self, terms: dict[_ScratchKey, Fraction] | None = None) -> None:
        self.terms: dict[_ScratchKey, Fraction] = {}
        for key, coefficient in (terms or {}).items():
            self._add_term(key, coefficient)

    def _add_term(self, key: _ScratchKey, coefficient: Fraction) -> None:
        if coefficient == 0:
            return
        updated = self.terms.get(key, Fraction(0)) + coefficient
        if updated == 0:
            self.terms.pop(key, None)
        else:
            self.terms[key] = updated

    @classmethod
    def constant(cls, value: Fraction) -> _ScratchPolynomial:
        return cls({(): value})

    @classmethod
    def variable(cls, name: str) -> _ScratchPolynomial:
        return cls({((name, 1),): Fraction(1)})

    def __add__(self, other: _ScratchPolynomial) -> _ScratchPolynomial:
        result = _ScratchPolynomial(dict(self.terms))
        for key, coefficient in other.terms.items():
            result._add_term(key, coefficient)
        return result

    def __neg__(self) -> _ScratchPolynomial:
        return _ScratchPolynomial({key: -coefficient for key, coefficient in self.terms.items()})

    def __sub__(self, other: _ScratchPolynomial) -> _ScratchPolynomial:
        return self + (-other)

    def __mul__(self, other: _ScratchPolynomial) -> _ScratchPolynomial:
        result = _ScratchPolynomial()
        for key1, c1 in self.terms.items():
            for key2, c2 in other.terms.items():
                merged: dict[str, int] = dict(key1)
                for variable_id, exponent in key2:
                    merged[variable_id] = merged.get(variable_id, 0) + exponent
                result._add_term(tuple(sorted(merged.items())), c1 * c2)
        return result

    def to_polynomial(self) -> Polynomial:
        terms = tuple(
            Term(_rational(coefficient), tuple(MonomialPower(v, e) for v, e in key if e))
            for key, coefficient in self.terms.items()
            if coefficient != 0
        )
        return Polynomial(terms)


def _fk_numerator_polynomials(
    l1: Fraction, l2: Fraction, x: Fraction, y: Fraction
) -> tuple[Polynomial, Polynomial]:
    """Tangent-half-angle-rationalized forward-kinematics identities, cleared of
    denominators. D1=1+t1^2 and D2=1+t2^2 are provably >=1 for every real t1,t2,
    so clearing them introduces no sign condition to track (AGENTS.md SS7.2).

    x = L1 cos(q1) + L2 cos(q1+q2), y = L1 sin(q1) + L2 sin(q1+q2); derivation
    verified both algebraically and against the worked instance in the design.
    """
    x_num = _poly(
        _mono(l1 + l2 - x),
        _mono(-l1 - l2 - x, t1=2),
        _mono(l1 - l2 - x, t2=2),
        _mono(-l1 + l2 - x, t1=2, t2=2),
        _mono(-4 * l2, t1=1, t2=1),
    )
    y_num = _poly(
        _mono(-y),
        _mono(2 * (l1 + l2), t1=1),
        _mono(2 * l2, t2=1),
        _mono(-y, t1=2),
        _mono(-y, t2=2),
        _mono(2 * (l1 - l2), t1=1, t2=2),
        _mono(-2 * l2, t1=2, t2=1),
        _mono(-y, t1=2, t2=2),
    )
    return x_num, y_num


def _singularity_margin_polynomial(l1: Fraction, l2: Fraction, epsilon: Fraction) -> Polynomial:
    """|det J| >= epsilon, rationalized and squared into one inequality with no
    sign case-split: det J = L1*L2*sin(q2) = 2*L1*L2*t2/D2, and epsilon*D2 > 0
    always (D2 = 1+t2^2 >= 1), so |a| >= b with b provably positive is equivalent
    to a^2 >= b^2 without a separate sign branch.

    (2*L1*L2*t2)^2 >= epsilon^2 * (1+t2^2)^2
      <=> (4*L1^2*L2^2 - 2*epsilon^2)*t2^2 - epsilon^2*t2^4 - epsilon^2 >= 0
    """
    return _poly(
        _mono(4 * l1**2 * l2**2 - 2 * epsilon**2, t2=2),
        _mono(-(epsilon**2), t2=4),
        _mono(-(epsilon**2)),
    )


def _clearance_predicates_and_formula(
    l1: Fraction,
    x: Fraction,
    y: Fraction,
    cx: Fraction,
    cy: Fraction,
    r_squared: Fraction,
) -> tuple[tuple[Predicate, ...], Formula]:
    """Segment/circle clearance, no square roots (squared-distance form).

    Two segments: shoulder(0,0)-elbow(t1), and elbow(t1)-tool(x,y) (the tool is
    the fixed constant (x,y), justified by the FK-equality conjuncts already in
    the formula, halving degree vs re-deriving the tool point from t1,t2).
    Point-to-segment squared distance is an inherent 3-case split (foot of the
    perpendicular before/inside/past the segment -- AGENTS.md SS45/SS46, a real
    boundary structure, not a spurious artifact), each case built by comparing
    the projection parameter s = (w.v)/(v.v) against 0 and 1 without ever
    dividing (multiplying through by the provably-positive denominators instead).
    """
    p = _ScratchPolynomial
    t1 = p.variable("t1")
    one = p.constant(Fraction(1))
    d1 = one + t1 * t1  # 1+t1^2, provably >=1

    bn_x = p.constant(l1) * (one - t1 * t1)  # elbow numerator, x
    bn_y = p.constant(2 * l1) * t1  # elbow numerator, y

    # Segment 1: A=(0,0), B=elbow(t1). v.v collapses to the constant L1^2 (since
    # |elbow(t1)|=L1 identically), so no FK-dependence is needed for positivity.
    wn1 = p.constant(cx) * bn_x + p.constant(cy) * bn_y
    l1_sq_d1 = p.constant(l1 * l1) * d1
    ex = p.constant(cx) * d1 - bn_x
    ey = p.constant(cy) * d1 - bn_y
    seg1_case_a_distance = p.constant(cx * cx + cy * cy - r_squared)
    elbow_clearance = ex * ex + ey * ey - p.constant(r_squared) * (d1 * d1)  # shared with seg 2
    seg1_case_mid_distance = seg1_case_a_distance * (d1 * d1) * p.constant(l1 * l1) - wn1 * wn1

    # Segment 2: A=(x,y), B=elbow(t1). v.v = Qn2/D1^2 (NOT constant); Qn2 > 0 is
    # guaranteed whenever the FK identities also hold (elbow-to-tool distance is
    # then exactly L2 > 0), which is the only case this case-split needs to be
    # meaningful (the surrounding formula is an AND with the FK identities).
    vn_x = bn_x - p.constant(x) * d1
    vn_y = bn_y - p.constant(y) * d1
    wn2 = p.constant(cx - x) * vn_x + p.constant(cy - y) * vn_y
    qn2 = vn_x * vn_x + vn_y * vn_y
    seg2_case_a_distance = p.constant((x - cx) * (x - cx) + (y - cy) * (y - cy) - r_squared)
    seg2_case_mid_distance = seg2_case_a_distance * qn2 - wn2 * wn2

    def pred(name: str, poly: _ScratchPolynomial, relation: Relation) -> Predicate:
        return Predicate(
            name, left=poly.to_polynomial(), relation=relation, right=Polynomial.zero()
        )

    predicates = (
        pred("seg1_case_a_selector", wn1, Relation.LE),
        pred("seg1_case_b_selector", wn1 - l1_sq_d1, Relation.GE),
        pred("seg1_case_mid_selector_lo", wn1, Relation.GE),
        pred("seg1_case_mid_selector_hi", l1_sq_d1 - wn1, Relation.GE),
        pred("seg1_case_a_distance", seg1_case_a_distance, Relation.GE),
        pred("elbow_clearance_ge_r", elbow_clearance, Relation.GE),
        pred("seg1_case_mid_distance", seg1_case_mid_distance, Relation.GE),
        pred("seg2_case_a_selector", wn2, Relation.LE),
        pred("seg2_case_b_selector", wn2 * d1 - qn2, Relation.GE),
        pred("seg2_case_mid_selector_lo", wn2, Relation.GE),
        pred("seg2_case_mid_selector_hi", qn2 - wn2 * d1, Relation.GE),
        pred("seg2_case_a_distance", seg2_case_a_distance, Relation.GE),
        pred("seg2_case_mid_distance", seg2_case_mid_distance, Relation.GE),
    )

    seg1_clearance = Formula.any(
        Formula.all(
            Formula.predicate("seg1_case_a_selector"),
            Formula.predicate("seg1_case_a_distance"),
        ),
        Formula.all(
            Formula.predicate("seg1_case_b_selector"),
            Formula.predicate("elbow_clearance_ge_r"),
        ),
        Formula.all(
            Formula.predicate("seg1_case_mid_selector_lo"),
            Formula.predicate("seg1_case_mid_selector_hi"),
            Formula.predicate("seg1_case_mid_distance"),
        ),
    )
    seg2_clearance = Formula.any(
        Formula.all(
            Formula.predicate("seg2_case_a_selector"),
            Formula.predicate("seg2_case_a_distance"),
        ),
        Formula.all(
            Formula.predicate("seg2_case_b_selector"),
            Formula.predicate("elbow_clearance_ge_r"),
        ),
        Formula.all(
            Formula.predicate("seg2_case_mid_selector_lo"),
            Formula.predicate("seg2_case_mid_selector_hi"),
            Formula.predicate("seg2_case_mid_distance"),
        ),
    )
    return predicates, Formula.all(seg1_clearance, seg2_clearance)


def build_planar2r_claim(
    *,
    l1: Fraction,
    l2: Fraction,
    x: Fraction,
    y: Fraction,
    epsilon: Fraction,
    obstacle_center: tuple[Fraction, Fraction],
    obstacle_radius: Fraction,
    clearance_margin: Fraction,
    t1_bounds: tuple[Fraction, Fraction],
    t2_bounds: tuple[Fraction, Fraction],
    claim_id: str = CLAIM_ID,
) -> Claim:
    """Build the Slice-1 Claim: exists (t1, t2) in the given rational box such
    that forward kinematics hits (x, y) exactly, the singularity margin holds,
    and both arm segments maintain the required clearance from a fixed circular
    obstacle.

    l1, l2 must be NONZERO but may be negative (proof P2 hypothesis (H1) is
    `L_i != 0`, not `L_i > 0`; every use is of `L1^2 > 0`, `L2 != 0` or `|L2|`,
    and no step depends on a sign). Zero-length links remain excluded as a
    degenerate case per AGENTS.md SS47 -- intentionally, not silently.

    Negative link lengths are not a physical robot: they are how the four-chart
    construction of P2 SS13 reaches configurations with `q_i = pi`, which the
    half-angle chart cannot represent (P2 Theorem 12.1). Callers wanting full
    torus-coverage experiments should use the quarantined `certify2r.certify_problem`
    orchestration rather than passing negative lengths directly. No four-chart
    helper is wired into the public production path.
    """
    if l1 == 0 or l2 == 0:
        raise ValueError("link lengths must be nonzero (degenerate zero-length link excluded)")
    if epsilon <= 0:
        raise ValueError("singularity margin epsilon must be strictly positive")
    if epsilon > abs(l1 * l2):
        # Proof P2 Corollary 5.4: for epsilon > |L1*L2| the set {t2 : G(t2) >= 0}
        # is empty, so the claim is unsatisfiable for EVERY target, obstacle and
        # witness box. Building it would be silently vacuous -- the checker would
        # reject every witness and the caller would receive an UNKNOWN carrying no
        # indication that the instance was infeasible by construction. Decidable
        # exactly in rational arithmetic, so refuse at build time.
        raise ValueError(
            f"singularity margin epsilon={epsilon} exceeds |L1*L2|={abs(l1 * l2)}; "
            "no configuration can satisfy it (proof P2 Corollary 5.4)"
        )
    if obstacle_radius <= 0:
        raise ValueError("obstacle radius must be strictly positive (degenerate obstacle excluded)")
    if clearance_margin <= 0:
        raise ValueError("clearance margin must be strictly positive")

    t1_min, t1_max = t1_bounds
    t2_min, t2_max = t2_bounds

    t1_var = Variable("t1", unit=Unit.DIMENSIONLESS)
    t2_var = Variable("t2", unit=Unit.DIMENSIONLESS)

    t1_interval = IntervalDomain(
        "Q.t1", "t1", lower=_rational(t1_min), upper=_rational(t1_max), unit=Unit.DIMENSIONLESS
    )
    t2_interval = IntervalDomain(
        "Q.t2", "t2", lower=_rational(t2_min), upper=_rational(t2_max), unit=Unit.DIMENSIONLESS
    )
    witness_box = BoxDomain("Q", components=(t1_interval, t2_interval))

    x_num, y_num = _fk_numerator_polynomials(l1, l2, x, y)
    margin_poly = _singularity_margin_polynomial(l1, l2, epsilon)
    cx, cy = obstacle_center
    r_squared = (obstacle_radius + clearance_margin) ** 2
    clearance_predicates, clearance_formula = _clearance_predicates_and_formula(
        l1, x, y, cx, cy, r_squared
    )

    predicates = (
        Predicate("fk_x_identity", left=x_num, relation=Relation.EQ, right=Polynomial.zero()),
        Predicate("fk_y_identity", left=y_num, relation=Relation.EQ, right=Polynomial.zero()),
        Predicate(
            "singularity_margin_ge_epsilon",
            left=margin_poly,
            relation=Relation.GE,
            right=Polynomial.zero(),
        ),
        *clearance_predicates,
    )
    formula = Formula.all(
        Formula.predicate("fk_x_identity"),
        Formula.predicate("fk_y_identity"),
        Formula.predicate("singularity_margin_ge_epsilon"),
        clearance_formula,
    )

    instance_params = {
        "l1": _rational(l1).to_dict(),
        "l2": _rational(l2).to_dict(),
        "x": _rational(x).to_dict(),
        "y": _rational(y).to_dict(),
        "epsilon": _rational(epsilon).to_dict(),
        "obstacle_cx": _rational(cx).to_dict(),
        "obstacle_cy": _rational(cy).to_dict(),
        "obstacle_radius": _rational(obstacle_radius).to_dict(),
        "clearance_margin": _rational(clearance_margin).to_dict(),
    }

    return Claim(
        claim_id=claim_id,
        variables=(t1_var, t2_var),
        domains=(witness_box,),
        quantifiers=(QuantifierBlock(QuantifierKind.EXISTS, ("t1", "t2"), "Q"),),
        predicates=predicates,
        formula=formula,
        assumptions=(
            Assumption(
                "rigid_planar_links",
                "Links are rigid, planar, exact rational length; no manufacturing tolerance "
                "in this slice",
                "model",
            ),
            Assumption(
                "nonzero_link_lengths",
                "The effective chart lengths L1 and L2 are nonzero; they may be sign-flipped "
                "coordinates in the quarantined four-chart construction. Degenerate zero-length "
                "links are excluded, not assumed away",
                "degeneracy",
            ),
            Assumption(
                "chart_restricted_joint_range",
                "t1, t2 bounds are finite rationals, so q1, q2 never reach the pi chart boundary",
                "chart",
            ),
            Assumption(
                "single_instance_no_robustness",
                "L1, L2, x, y are fixed rational constants, not quantified; this Claim certifies "
                "exactly one instance, not a robust range",
                "scope",
            ),
            Assumption(
                "static_circular_obstacle",
                "The obstacle is a single fixed circle at a fixed rational center and radius",
                "model",
            ),
        ),
        margins=(
            Margin(
                "singularity_margin",
                "abs_det_jacobian",
                Relation.GE,
                _rational(epsilon),
                Unit.SQUARE_METRE,
            ),
            Margin(
                "obstacle_clearance_margin",
                "distance_to_obstacle_boundary",
                Relation.GE,
                _rational(clearance_margin),
                Unit.METRE,
            ),
        ),
        uncertainty_semantics=UncertaintySemantics.NONE,
        geometry_semantics=GeometrySemantics.EXACT,
        provenance=(
            ProvenanceEntry(
                "planar2r_benchmark_a_instance",
                digest_json(instance_params),
                "Phase 1 Benchmark A, single-instance planar 2R witness certification",
            ),
        ),
    )


__all__ = ["CLAIM_ID", "build_planar2r_claim"]
