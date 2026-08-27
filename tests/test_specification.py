from __future__ import annotations

from dataclasses import replace
from math import gcd

import pytest
from hypothesis import given
from hypothesis import strategies as st

from robocert.specification import (
    BoxDomain,
    Claim,
    Formula,
    IntervalDomain,
    QuantifierBlock,
    QuantifierKind,
    Rational,
    Relation,
    Unit,
    ValidationError,
)


@given(
    numerator=st.integers(min_value=-(10**9), max_value=10**9),
    denominator=st.integers(min_value=-(10**9), max_value=10**9).filter(lambda value: value != 0),
)
def test_rational_normalizes_exactly(numerator: int, denominator: int) -> None:
    value = Rational(numerator, denominator)
    assert value.denominator > 0
    assert gcd(abs(value.numerator), value.denominator) == 1
    assert value.numerator * denominator == numerator * value.denominator


def test_rational_json_rejects_noncanonical_representation() -> None:
    with pytest.raises(ValidationError, match="canonical"):
        Rational.from_dict({"numerator": 2, "denominator": 4})


def test_claim_round_trip_is_exact(sample_claim: Claim) -> None:
    assert Claim.from_dict(sample_claim.to_dict()) == sample_claim


@pytest.mark.parametrize("mutation", ["unknown_version", "extra_field"])
def test_claim_parser_rejects_unknown_contract_fields(sample_claim: Claim, mutation: str) -> None:
    artifact = sample_claim.to_dict()
    if mutation == "unknown_version":
        artifact["schema_version"] = "9.0.0"
    else:
        artifact["extra"] = True
    with pytest.raises(ValidationError):
        Claim.from_dict(artifact)


def test_quantifier_order_is_immutable_and_hash_sensitive(sample_claim: Claim) -> None:
    with pytest.raises(TypeError):
        sample_claim.quantifiers[0] = sample_claim.quantifiers[1]  # type: ignore[index]

    reordered = replace(sample_claim, quantifiers=tuple(reversed(sample_claim.quantifiers)))
    assert reordered.quantifiers != sample_claim.quantifiers
    assert reordered.digest() != sample_claim.digest()


def test_strict_and_weak_relations_remain_distinct(sample_claim: Claim) -> None:
    original = sample_claim.predicates[0]
    weakened = replace(original, relation=Relation.GE)
    weakened_claim = replace(sample_claim, predicates=(weakened,))

    assert original.relation is Relation.GT
    assert weakened.relation is Relation.GE
    assert weakened_claim.digest() != sample_claim.digest()
    assert Claim.from_dict(weakened_claim.to_dict()).predicates[0].relation is Relation.GE


def test_duplicate_variable_identifier_is_rejected(sample_claim: Claim) -> None:
    with pytest.raises(ValidationError, match="variable identifiers"):
        replace(sample_claim, variables=(sample_claim.variables[0], sample_claim.variables[0]))


def test_box_dimension_must_match_quantifier_block(sample_claim: Claim) -> None:
    theta_domain = sample_claim.domains[0]
    assert isinstance(theta_domain, BoxDomain)
    extra_component = IntervalDomain(
        "Theta.extra",
        "q",
        Rational(-1),
        Rational(1),
        unit=Unit.RADIAN,
    )
    invalid_domain = replace(
        theta_domain,
        components=(*theta_domain.components, extra_component),
    )
    with pytest.raises(ValidationError, match="does not match domain"):
        replace(sample_claim, domains=(invalid_domain, sample_claim.domains[1]))


def test_formula_must_reference_declared_predicate(sample_claim: Claim) -> None:
    with pytest.raises(ValidationError, match="unknown predicate"):
        replace(sample_claim, formula=Formula.predicate("missing"))


def test_every_variable_must_be_quantified(sample_claim: Claim) -> None:
    invalid_quantifiers = (QuantifierBlock(QuantifierKind.FORALL, ("theta",), "Theta"),)
    with pytest.raises(ValidationError, match="exactly once"):
        replace(sample_claim, quantifiers=invalid_quantifiers)
