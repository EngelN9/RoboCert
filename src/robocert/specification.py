"""Immutable formal-claim objects for RoboCert's soundness boundary."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum, StrEnum
from functools import total_ordering
from math import gcd
from typing import Any, Self, TypeVar, cast

from robocert.artifacts import ArtifactDigest, JSONValue, digest_json
from robocert.errors import ValidationError

SCHEMA_VERSION = "0.1.0"
_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]*$")


def _validate_identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER_PATTERN.fullmatch(value) is None:
        raise ValidationError(
            f"{label} must start with a letter and contain only letters, digits, '.', ':', '-', '_'"
        )
    return value


def _validate_nonempty(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} must be a non-empty string")
    return value


def _expect_object(
    value: object,
    *,
    required: Iterable[str],
    label: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value):
        raise ValidationError(f"{label} must be a JSON object")
    required_set = set(required)
    actual_set = set(value)
    if actual_set != required_set:
        missing = sorted(required_set - actual_set)
        extra = sorted(actual_set - required_set)
        raise ValidationError(
            f"{label} fields do not match contract; missing={missing}, extra={extra}"
        )
    return cast(Mapping[str, Any], value)


def _expect_array(value: object, label: str) -> Sequence[object]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ValidationError(f"{label} must be a JSON array")
    return cast(Sequence[object], value)


EnumT = TypeVar("EnumT", bound=Enum)


def _parse_enum(enum_type: type[EnumT], value: object, label: str) -> EnumT:
    if not isinstance(value, str):
        raise ValidationError(f"{label} must be a string")
    try:
        return enum_type(value)
    except ValueError as exc:
        raise ValidationError(f"unsupported {label}: {value!r}") from exc


class Unit(StrEnum):
    DIMENSIONLESS = "dimensionless"
    METRE = "metre"
    SQUARE_METRE = "square_metre"
    RADIAN = "radian"
    SECOND = "second"


class QuantifierKind(StrEnum):
    FORALL = "forall"
    EXISTS = "exists"


class Relation(StrEnum):
    EQ = "eq"
    GT = "gt"
    GE = "ge"
    LT = "lt"
    LE = "le"


class FormulaKind(StrEnum):
    PREDICATE = "predicate"
    AND = "and"
    OR = "or"
    NOT = "not"


class UncertaintySemantics(StrEnum):
    NONE = "none"
    ADJUSTABLE = "adjustable"
    STATIC_ROBUST = "static_robust"
    POLICY = "policy"


class GeometrySemantics(StrEnum):
    EXACT = "exact"
    OUTER_CONSERVATIVE = "outer_conservative"
    INNER_CONSERVATIVE = "inner_conservative"
    NON_CERTIFIED_APPROXIMATION = "non_certified_approximation"


@total_ordering
@dataclass(frozen=True, slots=True)
class Rational:
    """A normalized exact rational number."""

    numerator: int
    denominator: int = 1

    def __post_init__(self) -> None:
        if type(self.numerator) is not int or type(self.denominator) is not int:
            raise ValidationError("rational numerator and denominator must be integers")
        if self.denominator == 0:
            raise ValidationError("rational denominator must be nonzero")
        divisor = gcd(abs(self.numerator), abs(self.denominator))
        sign = -1 if self.denominator < 0 else 1
        object.__setattr__(self, "numerator", sign * self.numerator // divisor)
        object.__setattr__(self, "denominator", abs(self.denominator) // divisor)

    def __add__(self, other: Rational) -> Rational:
        if not isinstance(other, Rational):
            return NotImplemented
        return Rational(
            self.numerator * other.denominator + other.numerator * self.denominator,
            self.denominator * other.denominator,
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Rational):
            return NotImplemented
        return self.numerator * other.denominator < other.numerator * self.denominator

    def to_dict(self) -> dict[str, int]:
        return {"numerator": self.numerator, "denominator": self.denominator}

    @classmethod
    def from_dict(cls, value: object) -> Rational:
        data = _expect_object(
            value,
            required=("numerator", "denominator"),
            label="rational",
        )
        if type(data["numerator"]) is not int or type(data["denominator"]) is not int:
            raise ValidationError("rational numerator and denominator must be integers")
        result = cls(data["numerator"], data["denominator"])
        if result.to_dict() != dict(data):
            raise ValidationError("serialized rational must already be in canonical form")
        return result


@dataclass(frozen=True, slots=True)
class Variable:
    variable_id: str
    unit: Unit = Unit.DIMENSIONLESS

    def __post_init__(self) -> None:
        _validate_identifier(self.variable_id, "variable_id")
        if not isinstance(self.unit, Unit):
            raise ValidationError("variable unit must be a Unit")

    def to_dict(self) -> dict[str, str]:
        return {"variable_id": self.variable_id, "unit": self.unit.value}

    @classmethod
    def from_dict(cls, value: object) -> Variable:
        data = _expect_object(value, required=("variable_id", "unit"), label="variable")
        return cls(
            _validate_identifier(data["variable_id"], "variable_id"),
            _parse_enum(Unit, data["unit"], "unit"),
        )


@dataclass(frozen=True, slots=True)
class IntervalDomain:
    domain_id: str
    variable_id: str
    lower: Rational
    upper: Rational
    unit: Unit = Unit.DIMENSIONLESS
    lower_closed: bool = True
    upper_closed: bool = True

    def __post_init__(self) -> None:
        _validate_identifier(self.domain_id, "interval domain_id")
        _validate_identifier(self.variable_id, "interval variable_id")
        if not isinstance(self.lower, Rational) or not isinstance(self.upper, Rational):
            raise ValidationError("interval endpoints must be Rational")
        if not self.lower < self.upper:
            raise ValidationError(
                "interval lower endpoint must be strictly less than upper endpoint"
            )
        if not isinstance(self.unit, Unit):
            raise ValidationError("interval unit must be a Unit")
        if type(self.lower_closed) is not bool or type(self.upper_closed) is not bool:
            raise ValidationError("interval boundary flags must be booleans")

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "domain_id": self.domain_id,
            "variable_id": self.variable_id,
            "lower": self.lower.to_dict(),
            "upper": self.upper.to_dict(),
            "unit": self.unit.value,
            "lower_closed": self.lower_closed,
            "upper_closed": self.upper_closed,
        }

    @classmethod
    def from_dict(cls, value: object) -> IntervalDomain:
        data = _expect_object(
            value,
            required=(
                "domain_id",
                "variable_id",
                "lower",
                "upper",
                "unit",
                "lower_closed",
                "upper_closed",
            ),
            label="interval domain",
        )
        if type(data["lower_closed"]) is not bool or type(data["upper_closed"]) is not bool:
            raise ValidationError("interval boundary flags must be booleans")
        return cls(
            domain_id=_validate_identifier(data["domain_id"], "interval domain_id"),
            variable_id=_validate_identifier(data["variable_id"], "interval variable_id"),
            lower=Rational.from_dict(data["lower"]),
            upper=Rational.from_dict(data["upper"]),
            unit=_parse_enum(Unit, data["unit"], "unit"),
            lower_closed=data["lower_closed"],
            upper_closed=data["upper_closed"],
        )


@dataclass(frozen=True, slots=True)
class BoxDomain:
    domain_id: str
    components: tuple[IntervalDomain, ...]

    def __post_init__(self) -> None:
        _validate_identifier(self.domain_id, "box domain_id")
        object.__setattr__(self, "components", tuple(self.components))
        if not self.components:
            raise ValidationError("box domain must contain at least one interval")
        if any(not isinstance(item, IntervalDomain) for item in self.components):
            raise ValidationError("box domain components must be IntervalDomain values")
        variable_ids = [item.variable_id for item in self.components]
        component_ids = [item.domain_id for item in self.components]
        if len(variable_ids) != len(set(variable_ids)):
            raise ValidationError("box domain variable identifiers must be unique")
        if len(component_ids) != len(set(component_ids)):
            raise ValidationError("box domain component identifiers must be unique")

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "domain_id": self.domain_id,
            "components": [item.to_dict() for item in self.components],
        }

    @classmethod
    def from_dict(cls, value: object) -> BoxDomain:
        data = _expect_object(value, required=("domain_id", "components"), label="box domain")
        return cls(
            domain_id=_validate_identifier(data["domain_id"], "box domain_id"),
            components=tuple(
                IntervalDomain.from_dict(item)
                for item in _expect_array(data["components"], "box domain components")
            ),
        )


@dataclass(frozen=True, slots=True)
class QuantifierBlock:
    kind: QuantifierKind
    variable_ids: tuple[str, ...]
    domain_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, QuantifierKind):
            raise ValidationError("quantifier kind must be a QuantifierKind")
        object.__setattr__(self, "variable_ids", tuple(self.variable_ids))
        if not self.variable_ids:
            raise ValidationError("quantifier block must bind at least one variable")
        for variable_id in self.variable_ids:
            _validate_identifier(variable_id, "quantifier variable_id")
        if len(self.variable_ids) != len(set(self.variable_ids)):
            raise ValidationError("quantifier block variable identifiers must be unique")
        _validate_identifier(self.domain_id, "quantifier domain_id")

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "kind": self.kind.value,
            "variable_ids": list(self.variable_ids),
            "domain_id": self.domain_id,
        }

    @classmethod
    def from_dict(cls, value: object) -> QuantifierBlock:
        data = _expect_object(
            value,
            required=("kind", "variable_ids", "domain_id"),
            label="quantifier block",
        )
        return cls(
            kind=_parse_enum(QuantifierKind, data["kind"], "quantifier kind"),
            variable_ids=tuple(
                _validate_identifier(item, "quantifier variable_id")
                for item in _expect_array(data["variable_ids"], "quantifier variable_ids")
            ),
            domain_id=_validate_identifier(data["domain_id"], "quantifier domain_id"),
        )


@dataclass(frozen=True, slots=True)
class MonomialPower:
    variable_id: str
    exponent: int

    def __post_init__(self) -> None:
        _validate_identifier(self.variable_id, "monomial variable_id")
        if type(self.exponent) is not int or self.exponent < 1:
            raise ValidationError("monomial exponent must be a positive integer")

    def to_dict(self) -> dict[str, JSONValue]:
        return {"variable_id": self.variable_id, "exponent": self.exponent}

    @classmethod
    def from_dict(cls, value: object) -> MonomialPower:
        data = _expect_object(value, required=("variable_id", "exponent"), label="monomial power")
        if type(data["exponent"]) is not int:
            raise ValidationError("monomial exponent must be an integer")
        return cls(
            _validate_identifier(data["variable_id"], "monomial variable_id"),
            data["exponent"],
        )


@dataclass(frozen=True, slots=True)
class Term:
    coefficient: Rational
    powers: tuple[MonomialPower, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.coefficient, Rational):
            raise ValidationError("term coefficient must be Rational")
        if self.coefficient.numerator == 0:
            raise ValidationError("zero-coefficient terms are not canonical")
        powers = tuple(sorted(self.powers, key=lambda item: item.variable_id))
        if any(not isinstance(item, MonomialPower) for item in powers):
            raise ValidationError("term powers must be MonomialPower values")
        if len(powers) != len({item.variable_id for item in powers}):
            raise ValidationError("term may mention each variable at most once")
        object.__setattr__(self, "powers", powers)

    @property
    def monomial_key(self) -> tuple[tuple[str, int], ...]:
        return tuple((item.variable_id, item.exponent) for item in self.powers)

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "coefficient": self.coefficient.to_dict(),
            "powers": [item.to_dict() for item in self.powers],
        }

    @classmethod
    def from_dict(cls, value: object) -> Term:
        data = _expect_object(value, required=("coefficient", "powers"), label="polynomial term")
        result = cls(
            Rational.from_dict(data["coefficient"]),
            tuple(
                MonomialPower.from_dict(item)
                for item in _expect_array(data["powers"], "term powers")
            ),
        )
        if result.to_dict() != dict(data):
            raise ValidationError("serialized term powers must already be in canonical order")
        return result


@dataclass(frozen=True, slots=True)
class Polynomial:
    terms: tuple[Term, ...] = ()

    def __post_init__(self) -> None:
        combined: dict[tuple[tuple[str, int], ...], Rational] = {}
        powers_by_key: dict[tuple[tuple[str, int], ...], tuple[MonomialPower, ...]] = {}
        for term in self.terms:
            if not isinstance(term, Term):
                raise ValidationError("polynomial terms must be Term values")
            combined[term.monomial_key] = (
                combined.get(term.monomial_key, Rational(0)) + term.coefficient
            )
            powers_by_key[term.monomial_key] = term.powers
        normalized = tuple(
            Term(coefficient, powers_by_key[key])
            for key, coefficient in sorted(combined.items())
            if coefficient.numerator != 0
        )
        object.__setattr__(self, "terms", normalized)

    @classmethod
    def zero(cls) -> Polynomial:
        return cls(())

    @property
    def variable_ids(self) -> frozenset[str]:
        return frozenset(power.variable_id for term in self.terms for power in term.powers)

    def to_dict(self) -> dict[str, JSONValue]:
        return {"terms": [item.to_dict() for item in self.terms]}

    @classmethod
    def from_dict(cls, value: object) -> Polynomial:
        data = _expect_object(value, required=("terms",), label="polynomial")
        result = cls(
            tuple(Term.from_dict(item) for item in _expect_array(data["terms"], "polynomial terms"))
        )
        if result.to_dict() != dict(data):
            raise ValidationError("serialized polynomial must already be in canonical form")
        return result


@dataclass(frozen=True, slots=True)
class Predicate:
    predicate_id: str
    left: Polynomial
    relation: Relation
    right: Polynomial

    def __post_init__(self) -> None:
        _validate_identifier(self.predicate_id, "predicate_id")
        if not isinstance(self.left, Polynomial) or not isinstance(self.right, Polynomial):
            raise ValidationError("predicate operands must be Polynomial values")
        if not isinstance(self.relation, Relation):
            raise ValidationError("predicate relation must be a Relation")

    @property
    def variable_ids(self) -> frozenset[str]:
        return self.left.variable_ids | self.right.variable_ids

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "predicate_id": self.predicate_id,
            "left": self.left.to_dict(),
            "relation": self.relation.value,
            "right": self.right.to_dict(),
        }

    @classmethod
    def from_dict(cls, value: object) -> Predicate:
        data = _expect_object(
            value,
            required=("predicate_id", "left", "relation", "right"),
            label="predicate",
        )
        return cls(
            predicate_id=_validate_identifier(data["predicate_id"], "predicate_id"),
            left=Polynomial.from_dict(data["left"]),
            relation=_parse_enum(Relation, data["relation"], "relation"),
            right=Polynomial.from_dict(data["right"]),
        )


@dataclass(frozen=True, slots=True)
class Formula:
    kind: FormulaKind
    predicate_id: str | None = None
    operands: tuple[Formula, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.kind, FormulaKind):
            raise ValidationError("formula kind must be a FormulaKind")
        object.__setattr__(self, "operands", tuple(self.operands))
        if any(not isinstance(item, Formula) for item in self.operands):
            raise ValidationError("formula operands must be Formula values")
        if self.kind is FormulaKind.PREDICATE:
            _validate_identifier(self.predicate_id, "formula predicate_id")
            if self.operands:
                raise ValidationError("predicate formula cannot contain operands")
        elif self.kind is FormulaKind.NOT:
            if self.predicate_id is not None or len(self.operands) != 1:
                raise ValidationError("not formula must contain exactly one operand")
        elif self.predicate_id is not None or not self.operands:
            raise ValidationError("and/or formula must contain operands and no predicate_id")

    @classmethod
    def predicate(cls, predicate_id: str) -> Formula:
        return cls(FormulaKind.PREDICATE, predicate_id=predicate_id)

    @classmethod
    def all(cls, *operands: Formula) -> Formula:
        return cls(FormulaKind.AND, operands=tuple(operands))

    @classmethod
    def any(cls, *operands: Formula) -> Formula:
        return cls(FormulaKind.OR, operands=tuple(operands))

    @classmethod
    def negate(cls, operand: Formula) -> Formula:
        return cls(FormulaKind.NOT, operands=(operand,))

    @property
    def predicate_ids(self) -> frozenset[str]:
        if self.kind is FormulaKind.PREDICATE:
            assert self.predicate_id is not None
            return frozenset((self.predicate_id,))
        return frozenset().union(*(item.predicate_ids for item in self.operands))

    def to_dict(self) -> dict[str, JSONValue]:
        if self.kind is FormulaKind.PREDICATE:
            assert self.predicate_id is not None
            return {"kind": self.kind.value, "predicate_id": self.predicate_id}
        return {"kind": self.kind.value, "operands": [item.to_dict() for item in self.operands]}

    @classmethod
    def from_dict(cls, value: object) -> Formula:
        if not isinstance(value, Mapping):
            raise ValidationError("formula must be a JSON object")
        kind = _parse_enum(FormulaKind, value.get("kind"), "formula kind")
        if kind is FormulaKind.PREDICATE:
            data = _expect_object(
                value, required=("kind", "predicate_id"), label="predicate formula"
            )
            return cls.predicate(_validate_identifier(data["predicate_id"], "formula predicate_id"))
        data = _expect_object(value, required=("kind", "operands"), label=f"{kind.value} formula")
        operands = tuple(
            cls.from_dict(item) for item in _expect_array(data["operands"], "formula operands")
        )
        if kind is FormulaKind.NOT:
            return cls.negate(operands[0]) if len(operands) == 1 else cls(kind, operands=operands)
        return cls(kind, operands=operands)


@dataclass(frozen=True, slots=True)
class Assumption:
    assumption_id: str
    statement: str
    category: str

    def __post_init__(self) -> None:
        _validate_identifier(self.assumption_id, "assumption_id")
        _validate_nonempty(self.statement, "assumption statement")
        _validate_identifier(self.category, "assumption category")

    def to_dict(self) -> dict[str, str]:
        return {
            "assumption_id": self.assumption_id,
            "statement": self.statement,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, value: object) -> Assumption:
        data = _expect_object(
            value,
            required=("assumption_id", "statement", "category"),
            label="assumption",
        )
        return cls(
            _validate_identifier(data["assumption_id"], "assumption_id"),
            _validate_nonempty(data["statement"], "assumption statement"),
            _validate_identifier(data["category"], "assumption category"),
        )


@dataclass(frozen=True, slots=True)
class Margin:
    margin_id: str
    metric: str
    relation: Relation
    bound: Rational
    unit: Unit = Unit.DIMENSIONLESS

    def __post_init__(self) -> None:
        _validate_identifier(self.margin_id, "margin_id")
        _validate_identifier(self.metric, "margin metric")
        if self.relation not in (Relation.GT, Relation.GE, Relation.LT, Relation.LE):
            raise ValidationError("margin relation must preserve a strict or weak inequality")
        if not isinstance(self.bound, Rational):
            raise ValidationError("margin bound must be Rational")
        if not isinstance(self.unit, Unit):
            raise ValidationError("margin unit must be a Unit")

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "margin_id": self.margin_id,
            "metric": self.metric,
            "relation": self.relation.value,
            "bound": self.bound.to_dict(),
            "unit": self.unit.value,
        }

    @classmethod
    def from_dict(cls, value: object) -> Margin:
        data = _expect_object(
            value,
            required=("margin_id", "metric", "relation", "bound", "unit"),
            label="margin",
        )
        return cls(
            margin_id=_validate_identifier(data["margin_id"], "margin_id"),
            metric=_validate_identifier(data["metric"], "margin metric"),
            relation=_parse_enum(Relation, data["relation"], "margin relation"),
            bound=Rational.from_dict(data["bound"]),
            unit=_parse_enum(Unit, data["unit"], "unit"),
        )


@dataclass(frozen=True, slots=True)
class ProvenanceEntry:
    source_id: str
    artifact_hash: ArtifactDigest
    description: str

    def __post_init__(self) -> None:
        _validate_identifier(self.source_id, "provenance source_id")
        if not isinstance(self.artifact_hash, ArtifactDigest):
            raise ValidationError("provenance artifact_hash must be ArtifactDigest")
        _validate_nonempty(self.description, "provenance description")

    def to_dict(self) -> dict[str, str]:
        return {
            "source_id": self.source_id,
            "artifact_hash": str(self.artifact_hash),
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, value: object) -> ProvenanceEntry:
        data = _expect_object(
            value,
            required=("source_id", "artifact_hash", "description"),
            label="provenance entry",
        )
        return cls(
            _validate_identifier(data["source_id"], "provenance source_id"),
            ArtifactDigest.from_json(data["artifact_hash"]),
            _validate_nonempty(data["description"], "provenance description"),
        )


@dataclass(frozen=True, slots=True)
class Claim:
    claim_id: str
    variables: tuple[Variable, ...]
    domains: tuple[BoxDomain, ...]
    quantifiers: tuple[QuantifierBlock, ...]
    predicates: tuple[Predicate, ...]
    formula: Formula
    assumptions: tuple[Assumption, ...]
    margins: tuple[Margin, ...]
    uncertainty_semantics: UncertaintySemantics
    geometry_semantics: GeometrySemantics
    provenance: tuple[ProvenanceEntry, ...]
    schema_version: str = field(default=SCHEMA_VERSION, kw_only=True)

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValidationError(f"unsupported claim schema version: {self.schema_version!r}")
        _validate_identifier(self.claim_id, "claim_id")
        for field_name in (
            "variables",
            "domains",
            "quantifiers",
            "predicates",
            "assumptions",
            "margins",
            "provenance",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))
        typed_collections = (
            (self.variables, Variable, "variables"),
            (self.domains, BoxDomain, "domains"),
            (self.quantifiers, QuantifierBlock, "quantifiers"),
            (self.predicates, Predicate, "predicates"),
            (self.assumptions, Assumption, "assumptions"),
            (self.margins, Margin, "margins"),
            (self.provenance, ProvenanceEntry, "provenance"),
        )
        for values, expected_type, label in typed_collections:
            if any(not isinstance(item, expected_type) for item in values):
                raise ValidationError(f"claim {label} contain an invalid value")
        if not self.variables or not self.domains or not self.quantifiers or not self.predicates:
            raise ValidationError(
                "claim variables, domains, quantifiers, and predicates cannot be empty"
            )
        if not isinstance(self.formula, Formula):
            raise ValidationError("claim formula must be Formula")
        if not isinstance(self.uncertainty_semantics, UncertaintySemantics):
            raise ValidationError("claim uncertainty_semantics is invalid")
        if not isinstance(self.geometry_semantics, GeometrySemantics):
            raise ValidationError("claim geometry_semantics is invalid")

        variable_map: dict[str, Variable] = self._unique_map(
            self.variables, "variable_id", "variable identifiers"
        )
        domain_map: dict[str, BoxDomain] = self._unique_map(
            self.domains, "domain_id", "domain identifiers"
        )
        predicate_map: dict[str, Predicate] = self._unique_map(
            self.predicates, "predicate_id", "predicate identifiers"
        )
        self._unique_map(self.assumptions, "assumption_id", "assumption identifiers")
        self._unique_map(self.margins, "margin_id", "margin identifiers")
        self._unique_map(self.provenance, "source_id", "provenance source identifiers")

        for domain in self.domains:
            for component in domain.components:
                variable = variable_map.get(component.variable_id)
                if variable is None:
                    raise ValidationError(
                        f"domain {domain.domain_id!r} references unknown variable "
                        f"{component.variable_id!r}"
                    )
                if variable.unit is not component.unit:
                    raise ValidationError(
                        f"domain unit for {component.variable_id!r} does not match variable unit"
                    )

        quantified_ids: list[str] = []
        for block in self.quantifiers:
            quantifier_domain = domain_map.get(block.domain_id)
            if quantifier_domain is None:
                raise ValidationError(f"quantifier references unknown domain {block.domain_id!r}")
            domain_ids = tuple(item.variable_id for item in quantifier_domain.components)
            if block.variable_ids != domain_ids:
                raise ValidationError(
                    f"quantifier variables {block.variable_ids!r} does not match domain "
                    f"{block.domain_id!r} variables {domain_ids!r}"
                )
            quantified_ids.extend(block.variable_ids)
        counts = Counter(quantified_ids)
        if set(counts) != set(variable_map) or any(count != 1 for count in counts.values()):
            raise ValidationError("every declared variable must be quantified exactly once")

        for predicate in self.predicates:
            unknown_variables = predicate.variable_ids - set(variable_map)
            if unknown_variables:
                raise ValidationError(
                    f"predicate {predicate.predicate_id!r} references unknown variables "
                    f"{sorted(unknown_variables)!r}"
                )
        unknown_predicates = self.formula.predicate_ids - set(predicate_map)
        if unknown_predicates:
            raise ValidationError(
                f"formula references unknown predicate identifiers: {sorted(unknown_predicates)!r}"
            )

    @staticmethod
    def _unique_map(items: tuple[Any, ...], attr: str, label: str) -> dict[str, Any]:
        values = [getattr(item, attr) for item in items]
        if len(values) != len(set(values)):
            raise ValidationError(f"{label} must be unique")
        return dict(zip(values, items, strict=True))

    def to_dict(self) -> dict[str, JSONValue]:
        return {
            "schema_version": self.schema_version,
            "claim_id": self.claim_id,
            "variables": [item.to_dict() for item in self.variables],
            "domains": [item.to_dict() for item in self.domains],
            "quantifiers": [item.to_dict() for item in self.quantifiers],
            "predicates": [item.to_dict() for item in self.predicates],
            "formula": self.formula.to_dict(),
            "assumptions": [item.to_dict() for item in self.assumptions],
            "margins": [item.to_dict() for item in self.margins],
            "uncertainty_semantics": self.uncertainty_semantics.value,
            "geometry_semantics": self.geometry_semantics.value,
            "provenance": [item.to_dict() for item in self.provenance],
        }

    def digest(self) -> ArtifactDigest:
        return digest_json(self.to_dict())

    @classmethod
    def from_dict(cls, value: object) -> Self:
        data = _expect_object(
            value,
            required=(
                "schema_version",
                "claim_id",
                "variables",
                "domains",
                "quantifiers",
                "predicates",
                "formula",
                "assumptions",
                "margins",
                "uncertainty_semantics",
                "geometry_semantics",
                "provenance",
            ),
            label="claim",
        )
        if data["schema_version"] != SCHEMA_VERSION:
            raise ValidationError(f"unsupported claim schema version: {data['schema_version']!r}")
        return cls(
            schema_version=SCHEMA_VERSION,
            claim_id=_validate_identifier(data["claim_id"], "claim_id"),
            variables=tuple(
                Variable.from_dict(item)
                for item in _expect_array(data["variables"], "claim variables")
            ),
            domains=tuple(
                BoxDomain.from_dict(item)
                for item in _expect_array(data["domains"], "claim domains")
            ),
            quantifiers=tuple(
                QuantifierBlock.from_dict(item)
                for item in _expect_array(data["quantifiers"], "claim quantifiers")
            ),
            predicates=tuple(
                Predicate.from_dict(item)
                for item in _expect_array(data["predicates"], "claim predicates")
            ),
            formula=Formula.from_dict(data["formula"]),
            assumptions=tuple(
                Assumption.from_dict(item)
                for item in _expect_array(data["assumptions"], "claim assumptions")
            ),
            margins=tuple(
                Margin.from_dict(item) for item in _expect_array(data["margins"], "claim margins")
            ),
            uncertainty_semantics=_parse_enum(
                UncertaintySemantics,
                data["uncertainty_semantics"],
                "uncertainty semantics",
            ),
            geometry_semantics=_parse_enum(
                GeometrySemantics,
                data["geometry_semantics"],
                "geometry semantics",
            ),
            provenance=tuple(
                ProvenanceEntry.from_dict(item)
                for item in _expect_array(data["provenance"], "claim provenance")
            ),
        )


__all__ = [
    "SCHEMA_VERSION",
    "Assumption",
    "BoxDomain",
    "Claim",
    "Formula",
    "FormulaKind",
    "GeometrySemantics",
    "IntervalDomain",
    "Margin",
    "MonomialPower",
    "Polynomial",
    "Predicate",
    "ProvenanceEntry",
    "QuantifierBlock",
    "QuantifierKind",
    "Rational",
    "Relation",
    "Term",
    "UncertaintySemantics",
    "Unit",
    "ValidationError",
    "Variable",
]
