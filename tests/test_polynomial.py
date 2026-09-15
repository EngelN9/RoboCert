"""Exact symbolic polynomial arithmetic.

`checkers.py::evaluate_polynomial` evaluates at a point; these operations must hold at *every*
point, because a certificate checker verifies identities rather than samples. Agreement at
sampled points is exactly the weaker property this module exists to replace, so the property
tests below check structural laws, not sampled equality.
"""

from __future__ import annotations

from fractions import Fraction

from hypothesis import given
from hypothesis import strategies as st

from robocert.polynomial import (
    add,
    constant,
    is_zero,
    monomial,
    multiply,
    product,
    subtract,
    summation,
)
from robocert.specification import MonomialPower, Polynomial, Rational, Term


def test_zero_polynomial_is_the_only_termless_one() -> None:
    assert is_zero(Polynomial.zero())
    assert is_zero(constant(0))
    assert not is_zero(constant(1))


def test_addition_combines_like_monomials() -> None:
    """Canonicalization is `Polynomial.__post_init__`'s job; this confirms it is relied on."""
    result = add(monomial(2, x=1), monomial(3, x=1))

    assert result == monomial(5, x=1)
    assert len(result.terms) == 1


def test_addition_cancelling_to_zero_leaves_no_terms() -> None:
    assert is_zero(add(monomial(2, x=1), monomial(-2, x=1)))


def test_subtraction_of_equals_is_zero() -> None:
    polynomial = add(monomial(3, x=2, y=1), constant(Fraction(-5, 7)))

    assert is_zero(subtract(polynomial, polynomial))


def test_multiplication_sums_exponents() -> None:
    result = multiply(monomial(2, x=2), monomial(3, x=1, y=4))

    assert result == monomial(6, x=3, y=4)


def test_multiplication_expands_a_square() -> None:
    """(x - 1)^2 = x^2 - 2x + 1 -- the decomposition the SOS positive control relies on."""
    x_minus_one = add(monomial(1, x=1), constant(-1))

    result = multiply(x_minus_one, x_minus_one)

    expected = summation([monomial(1, x=2), monomial(-2, x=1), constant(1)])
    assert result == expected


def test_multiplication_by_zero_is_zero() -> None:
    assert is_zero(multiply(monomial(3, x=2), constant(0)))


def test_empty_sum_and_product_are_the_identities() -> None:
    assert is_zero(summation([]))
    assert product([]) == constant(1)


def test_rational_coefficients_stay_exact() -> None:
    """A third is not 0.333...; nothing here may go through float."""
    third = constant(Fraction(1, 3))

    assert multiply(third, constant(3)) == constant(1)
    assert is_zero(subtract(multiply(third, constant(3)), constant(1)))


def test_results_are_canonical_polynomials() -> None:
    """Output must satisfy the same invariants the validated constructor enforces on input."""
    result = multiply(
        add(monomial(1, x=1), monomial(1, y=1)),
        add(monomial(1, x=1), monomial(-1, y=1)),
    )

    assert result == Polynomial(
        terms=(
            Term(Rational(1), powers=(MonomialPower("x", 2),)),
            Term(Rational(-1), powers=(MonomialPower("y", 2),)),
        )
    )
    assert all(term.coefficient.numerator != 0 for term in result.terms)


_coefficients = st.integers(min_value=-6, max_value=6)
_exponents = st.integers(min_value=0, max_value=3)


@st.composite
def _polynomials(draw: st.DrawFn) -> Polynomial:
    entries = draw(
        st.lists(st.tuples(_coefficients, _exponents, _exponents), min_size=0, max_size=4)
    )
    return summation(
        [
            monomial(coefficient, **{k: v for k, v in (("x", i), ("y", j)) if v})
            for coefficient, i, j in entries
        ]
    )


@given(_polynomials(), _polynomials(), _polynomials())
def test_multiplication_distributes_over_addition(
    a: Polynomial, b: Polynomial, c: Polynomial
) -> None:
    assert multiply(a, add(b, c)) == add(multiply(a, b), multiply(a, c))


@given(_polynomials(), _polynomials())
def test_multiplication_commutes(a: Polynomial, b: Polynomial) -> None:
    assert multiply(a, b) == multiply(b, a)


@given(_polynomials())
def test_subtracting_self_is_zero(a: Polynomial) -> None:
    assert is_zero(subtract(a, a))
