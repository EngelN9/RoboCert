"""Exact rational arithmetic on `specification.Polynomial`.

`specification.Polynomial` is a validated, canonically-ordered container: `__post_init__`
already combines like monomials, sorts by monomial key, and drops zero coefficients. This module
adds the *symbolic* operations a certificate checker needs -- multiply, add, subtract -- and
relies on that constructor for canonicalization rather than reimplementing it.

Why this exists: `checkers.py::evaluate_polynomial` evaluates a polynomial at a *point*. Every
certificate family in `docs/architecture/backends.md` -- sum-of-squares identities, Groebner
cofactors, C-IRIS separating planes -- needs the polynomial identity checked *symbolically*, over
all points at once. Point evaluation at finitely many points is not a proof of an identity.

Everything is exact. `Fraction` is used internally because `specification.Rational` deliberately
carries only `__add__` and `__lt__`; adding operators to that frozen, trusted type to serve an
arithmetic helper would be the wrong direction of dependency.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from fractions import Fraction

from robocert.specification import MonomialPower, Polynomial, Rational, Term

__all__ = [
    "add",
    "constant",
    "is_zero",
    "monomial",
    "multiply",
    "product",
    "subtract",
    "summation",
    "to_fraction",
]


def to_fraction(value: Rational) -> Fraction:
    return Fraction(value.numerator, value.denominator)


def _to_rational(value: Fraction) -> Rational:
    return Rational(value.numerator, value.denominator)


def _term_powers(term: Term) -> dict[str, int]:
    return {power.variable_id: power.exponent for power in term.powers}


def _build_term(coefficient: Fraction, powers: Mapping[str, int]) -> Term | None:
    """A term, or `None` when the coefficient vanishes.

    `Term.__post_init__` rejects a zero coefficient as non-canonical, so a vanishing product must
    be dropped here rather than handed to the constructor. Exponents of zero are dropped for the
    same reason: `MonomialPower` requires a positive exponent.
    """
    if coefficient == 0:
        return None
    return Term(
        _to_rational(coefficient),
        tuple(
            MonomialPower(variable_id, exponent)
            for variable_id, exponent in sorted(powers.items())
            if exponent != 0
        ),
    )


def _from_terms(terms: Iterable[Term | None]) -> Polynomial:
    """Hand the terms to the validated constructor, which canonicalizes them.

    Duplicated monomials are combined and zero coefficients dropped by
    `Polynomial.__post_init__`; this module never has to do it.
    """
    return Polynomial(terms=tuple(term for term in terms if term is not None))


def constant(value: Fraction | int) -> Polynomial:
    return _from_terms([_build_term(Fraction(value), {})])


def monomial(coefficient: Fraction | int, **powers: int) -> Polynomial:
    """`monomial(3, x=2, y=1)` is `3*x^2*y`. A readability helper for tests and callers."""
    return _from_terms([_build_term(Fraction(coefficient), powers)])


def add(left: Polynomial, right: Polynomial) -> Polynomial:
    return _from_terms([*left.terms, *right.terms])


def subtract(left: Polynomial, right: Polynomial) -> Polynomial:
    negated = [
        _build_term(-to_fraction(term.coefficient), _term_powers(term)) for term in right.terms
    ]
    return _from_terms([*left.terms, *negated])


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    """Distribute, summing exponents monomial-wise. Quadratic in the term counts, deliberately.

    A certificate checker runs once on a fixed artifact; clarity beats an asymptotically better
    representation that is harder to audit.
    """
    products: list[Term | None] = []
    for left_term in left.terms:
        left_powers = _term_powers(left_term)
        left_coefficient = to_fraction(left_term.coefficient)
        for right_term in right.terms:
            powers = dict(left_powers)
            for variable_id, exponent in _term_powers(right_term).items():
                powers[variable_id] = powers.get(variable_id, 0) + exponent
            products.append(
                _build_term(left_coefficient * to_fraction(right_term.coefficient), powers)
            )
    return _from_terms(products)


def summation(polynomials: Iterable[Polynomial]) -> Polynomial:
    """Sum of a possibly empty sequence. The empty sum is the zero polynomial."""
    return _from_terms([term for polynomial in polynomials for term in polynomial.terms])


def product(polynomials: Iterable[Polynomial]) -> Polynomial:
    """Product of a possibly empty sequence. The empty product is the constant 1."""
    result = constant(1)
    for polynomial in polynomials:
        result = multiply(result, polynomial)
    return result


def is_zero(polynomial: Polynomial) -> bool:
    """True iff the polynomial is identically zero.

    Exact and total: canonicalization has already removed every zero coefficient, so the zero
    polynomial is precisely the one with no terms. This is an identity test over all points, not
    an evaluation at any of them.
    """
    return polynomial.terms == ()
