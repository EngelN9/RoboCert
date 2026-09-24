# RC-007 E0 correspondence argument: exact refutation of universal claims

Status: **E0 draft produced on 2026-09-15.** It has not received the project
owner's line-by-line E1 read and has not been through the fresh-context referee
protocol. It does not authorize a CLI or report integration.

## 1. Claim and scope

Let `c` be a valid `Claim`, `m` an `ArtifactDigest`, and `a` a caller-supplied
mapping. The statement considered here is one-way:

> If `refute(c, m, a)` returns an accepted `RefutationReport` containing a
> `CheckedCounterexample`, then the recorded rational assignment is in every
> declared domain, assigns every declared variable exactly once, and makes the
> whole serialized formula false under exact rational evaluation. Because every
> quantifier block is universal, that point refutes the serialized universal
> formula over the rationals. The same rational point also refutes the
> corresponding formula over the reals under the canonical embedding of its
> rational coefficients and operations.

This is not a completeness claim. Rejection means only that this call did not
establish a counterexample and maps to `UNKNOWN`. The argument does not attach
physical meaning to the predicates, validate prose assumptions, prove that a
simulation model corresponds to the serialized claim, or authorize any
`CERTIFIED_*` result.

## 2. Valid-claim invariants used by `refute`

`Claim.__post_init__` is part of the precondition because `refute` accepts a
constructed `Claim`, not arbitrary JSON. It establishes the structural facts on
which the implementation relies:

1. variables, domains, quantifier blocks, and predicates are nonempty and have
   unique identifiers;
2. every domain component names a declared variable and uses the same unit;
3. every quantifier block names an existing domain and lists exactly that
   domain's variables;
4. every declared variable occurs in exactly one quantifier block;
5. every polynomial variable is declared, and every formula leaf names a
   declared predicate;
6. formula constructors admit only predicate leaves, nonempty conjunctions and
   disjunctions, and unary negation;
7. every `Rational` is normalized with a positive, nonzero denominator, and
   monomial exponents are nonnegative integers.

Consequently, once `refute` has established that all quantifier blocks are
`forall`, the prefix is exactly a nonempty sequence of universal blocks covering
all variables. There is no unquantified variable or silently omitted domain.

## 3. The assignment snapshot denotes one point

The caller's object is not trusted to be a stable dictionary. Lines 148--184 of
`refutation.py` first materialize `assignment.items()` once. Failure to iterate is
a rejection. Non-string keys, duplicate yielded keys, and values that are not
`Rational` objects are rejected. Each accepted item is then rebuilt as a plain
`Rational(numerator, denominator)` and all subsequent checks use only that
ordinary dictionary.

This snapshot is load-bearing. A general `Mapping` may return different values
on different reads. Before commit `9a3a04b`, separate reads allowed one point to
pass the type and domain checks while another point was evaluated or recorded.
The current code's single read and reconstruction ensure that domain checking,
formula evaluation, and the emitted assignment concern the same immutable
rational values.

After snapshotting, lines 199--207 compare its key set with the set of declared
variable identifiers. Acceptance is therefore possible only when there is one
snapshot value for every declared variable and no value for an undeclared one.
Uniqueness follows from the duplicate-key check before dictionary construction.

## 4. Universal-prefix and domain guards

Lines 186--197 reject the call if any quantifier block is not `FORALL`. Together
with the valid-claim invariants above, an accepted call has the prefix

\[
\forall x_1\in D_1\;\cdots\;\forall x_n\in D_n.
\]

For each domain component, lines 209--223 convert the recorded rational and both
endpoints to `fractions.Fraction`. `Rational` normalization and `Fraction` give
the same element of \(\mathbb Q\). The two Boolean tests implement exactly

\[
\ell < x\quad\text{or}\quad(\text{lower-closed}\land \ell=x),
\]

and

\[
x < u\quad\text{or}\quad(\text{upper-closed}\land x=u).
\]

Any failed component appends a diagnostic, and any diagnostic returns a rejected
report before evaluation. Thus an accepted report's recorded point lies in every
declared interval, including the intended open/closed endpoint semantics.

## 5. Exact correspondence of `evaluate_formula`

The remaining guard delegates to `checkers.evaluate_formula`; its correspondence
is included here rather than assumed.

For a polynomial term, `evaluate_polynomial` starts from the exact rational
coefficient and multiplies exact `Fraction` powers for every `(variable,
exponent)` pair. It sums the resulting terms in `Fraction`. By the definitions of
integer exponentiation, multiplication, and addition in \(\mathbb Q\), the return
value equals the mathematical polynomial evaluated at the binding.

`evaluate_predicate` finds the unique predicate named by the formula leaf,
evaluates both polynomials as above, and applies the exact relation selected from
`=`, `>`, `>=`, `<`, or `<=`. Claim validation guarantees that the predicate
exists, is unique, uses only bound variables, and carries one of those relations.

Structural induction on a valid `Formula` now gives evaluator correspondence:

- a predicate leaf has the truth value just described;
- `AND` uses `all`, so it is true exactly when every operand is true;
- `OR` uses `any`, so it is true exactly when some operand is true;
- the only remaining valid kind is unary `NOT`, which returns the negation of its
  operand's recursively computed truth value.

There is no floating-point operation in this path. Missing bindings or any other
evaluation exception are caught by lines 229--234 of `refutation.py` and produce
a rejected report. Lines 235--241 also reject when the whole formula evaluates
to true. Acceptance therefore implies exact falsity of the complete formula at
the snapshotted point.

## 6. Construction and status boundary

`CheckedCounterexample` requires the module-private identity token. The only
runtime source location passing that token is the acceptance tail of
`refute`, after all guards above. `RefutationReport.__post_init__` enforces

\[
\texttt{accepted}\iff
\texttt{checked_counterexample is not None}.
\]

The emitted object records the claim digest, supplied model digest, sorted
snapshotted assignment, assumption identifiers, and exact-rational arithmetic
mode. `counterexample_result` accepts only this gated type; failed reports go
through `unknown_from_refutation` and become `UNKNOWN`.

The claim digest binds the complete serialized claim, including assumptions and
provenance. The model digest is a caller-supplied binding and is not recomputed by
`refute`; this argument therefore establishes no claim-to-model correspondence.
Assumptions are recorded statements rather than executable predicates. The
counterexample refutes the serialized formula under those recorded assumptions;
this function does not independently establish that the assumptions hold.

## 7. Logical conclusion and the rational-to-real step

Let \(r\) be the recorded assignment and \(\Phi\) the serialized Boolean formula.
Sections 3--5 give \(r\in D_1\times\cdots\times D_n\) and
\(\neg\Phi(r)\). Elementary first-order logic yields

\[
\neg\bigl(\forall x_1\in D_1\cdots\forall x_n\in D_n:\Phi(x)\bigr).
\]

All coefficients, interval endpoints, and coordinates used here are rational,
and the evaluator's polynomial operations and order relations are preserved by
the canonical embedding \(\mathbb Q\hookrightarrow\mathbb R\). Hence the same
rational point, read as a real point, has the same polynomial values, relation
truth values, Boolean formula truth value, and interval membership. It also
refutes the corresponding real-domain universal formula.

This transport is specific to a concrete rational counterexample. It does not
justify replacing universal quantification over reals with universal
quantification over rationals when attempting to prove a claim.

## 8. Review obligations and known limits

This E0 argument should be reviewed against the exact source revision containing
commit `9a3a04b`. In particular, a reviewer should try to falsify:

- the single-snapshot invariant with adversarial `Mapping` implementations;
- exact key coverage and domain-boundary handling;
- the structural induction for nested Boolean formulas;
- the private-constructor and result-promotion boundary;
- the rational-to-real embedding step; and
- the distinction between a hash binding and semantic model correspondence.

Tests exercise these cases and corruption paths, but tests are evidence about
the implementation, not a substitute for the required owner read or referee
protocol. Until those gates are completed, RC-007 remains E0 and `refute` remains
excluded from the CLI and generated reports.
