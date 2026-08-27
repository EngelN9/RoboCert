from __future__ import annotations

from collections.abc import Callable

import pytest

from robocert.artifacts import ArtifactDigest, digest_json
from robocert.certificates import Certificate, CertificateConclusion
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


@pytest.fixture
def sample_claim() -> Claim:
    theta = Variable("theta", unit=Unit.METRE)
    q = Variable("q", unit=Unit.RADIAN)
    theta_axis = IntervalDomain(
        domain_id="Theta.theta",
        variable_id="theta",
        lower=Rational(9, 10),
        upper=Rational(11, 10),
        unit=Unit.METRE,
    )
    q_axis = IntervalDomain(
        domain_id="Q.q",
        variable_id="q",
        lower=Rational(-1),
        upper=Rational(1),
        unit=Unit.RADIAN,
    )
    theta_domain = BoxDomain("Theta", components=(theta_axis,))
    q_domain = BoxDomain("Q", components=(q_axis,))
    q_polynomial = Polynomial(terms=(Term(Rational(1), powers=(MonomialPower("q", 1),)),))
    predicate = Predicate(
        predicate_id="positive_q",
        left=q_polynomial,
        relation=Relation.GT,
        right=Polynomial.zero(),
    )
    return Claim(
        claim_id="phase0.fixture",
        variables=(theta, q),
        domains=(theta_domain, q_domain),
        quantifiers=(
            QuantifierBlock(QuantifierKind.FORALL, ("theta",), "Theta"),
            QuantifierBlock(QuantifierKind.EXISTS, ("q",), "Q"),
        ),
        predicates=(predicate,),
        formula=Formula.predicate("positive_q"),
        assumptions=(Assumption("rigid", "Rigid-body model", "model"),),
        margins=(Margin("clearance", "distance", Relation.GE, Rational(1, 1000), Unit.METRE),),
        uncertainty_semantics=UncertaintySemantics.ADJUSTABLE,
        geometry_semantics=GeometrySemantics.EXACT,
        provenance=(
            ProvenanceEntry(
                "fixture-source",
                digest_json({"source": "unit-test"}),
                "Deterministic test source",
            ),
        ),
    )


@pytest.fixture
def model_hash() -> ArtifactDigest:
    return digest_json({"model": "phase0-fixture"})


@pytest.fixture
def make_certificate(
    sample_claim: Claim,
    model_hash: ArtifactDigest,
) -> Callable[..., Certificate]:
    def factory(**overrides: object) -> Certificate:
        values: dict[str, object] = {
            "certificate_id": "fixture-certificate",
            "family": "fixture.exact",
            "conclusion": CertificateConclusion.FEASIBLE,
            "claim_hash": sample_claim.digest(),
            "model_hash": model_hash,
            "assumption_ids": tuple(item.assumption_id for item in sample_claim.assumptions),
            "checker_id": "fixture-checker",
            "checker_version": "1.0.0",
            "arithmetic_mode": "exact-rational",
            "payload": {"proof": "fixture-ok"},
            "provenance": sample_claim.provenance,
        }
        values.update(overrides)
        return Certificate(**values)  # type: ignore[arg-type]

    return factory
