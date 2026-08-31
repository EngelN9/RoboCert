# External solver backends

RoboCert's pipeline is `search -> certificate construction -> independent deterministic checker`.
Every external mathematical or robotics system named here belongs on the **left** of that arrow.
None is trusted, none is a dependency, and none appears on the certification path.

## The rule

> A solver proposes. The checker decides. A proposal that cannot be independently re-derived is
> not evidence, and its failure is `UNKNOWN` — never infeasibility, never a lowered standard.

Concretely, and without exception:

- no backend output is promoted to `CERTIFIED_*`;
- `pyproject.toml`'s `dependencies` stays empty; any adapter is an optional extra;
- a backend being unavailable, crashing, timing out, or disagreeing produces `UNKNOWN` via
  `results.unknown_from_check`;
- numerical success is not certification. A solver reporting "solved" contributes exactly one
  thing: a candidate artifact for the checker to re-derive exactly.

## What decides implementation order

Not the generator's power — the **checker's** cost. For each family the question is *what must
the checker do, and what must it trust?* A backend whose certificate can only be validated by
re-running the backend has no place in a soundness-first architecture, however capable it is.

| Backend | Role | Certificate emitted | Minimal checker | Checker dependencies |
|---|---|---|---|---|
| **Julia + SumOfSquares.jl + JuMP** | Untrusted generator | Rational Gram matrices, monomial bases, multipliers | Exact identity `p-γ = σ₀+Σσᵢgᵢ+Σλⱼhⱼ` **and** exact PSD per Gram | **None** — `src/robocert/sos.py` |
| **Singular / CoCoA / SymPy / SageMath / Risa-Asir** | Untrusted generator | Cofactors `hᵢ` with `Σhᵢfᵢ = g` | Exact polynomial identity | **None** — `src/robocert/polynomial.py` |
| **dReal / iSAT** | Untrusted **search** only | Rational counterexample point | Existing point evaluator (`checkers.py`) | **None** |
| **Drake + C-IRIS** | Untrusted generator | Region inequalities, separating-plane polynomials | **Reduces to the SOS checker** plus exact geometry predicates | None to check; Drake to generate |
| **Risa/Asir QE, iSAT UNSAT** | Research experiment only | Quantifier-eliminated formula | *Checking ≈ redoing the elimination* | — |

Two consequences worth stating plainly:

1. **SOS and Gröbner-cofactor checking share one primitive** — exact rational polynomial
   arithmetic. It is built once, in `polynomial.py`, and both families sit on it.
2. **C-IRIS is not an independent certificate family.** Its separating-plane certificate is
   checked *by the SOS checker*. Drake is therefore late in the order despite being the most
   visible tool on the list — not a judgement about Drake, a fact about what its output needs.

**dReal's δ-satisfiability is not a proof.** A δ-sat answer says a δ-perturbed problem is
satisfiable, which does not establish satisfiability of the actual problem. It maps to `UNKNOWN`.
Only an exact rational counterexample, re-evaluated by RoboCert, yields `COUNTEREXAMPLE`.

**Quantifier elimination is kept experimental** for the same reason: a QE result is not
independently checkable without redoing the elimination, so it cannot back a `CERTIFIED_*`
family. It remains useful for exploration and for generating candidates that other families can
certify.

## What exists today

`src/robocert/polynomial.py`, `src/robocert/linalg_exact.py`, and `src/robocert/sos.py` — the
exact-algebra core and the Positivstellensatz verifier. **No adapter, no extra, no external tool
is installed or invoked**, and `dependencies = []` is unchanged.

`sos.py` is deliberately not a `checking.Checker`: that protocol requires a
`certificate_family`, and there is no family to bind to. RC-001, which claims the SOS scheme
suits the planar-2R singularity-margin reduction, is `E0`, and `research/README.md` requires
`E2` before a production checker implementing a claim may be written. What `sos.py` verifies is
an algebraic identity plus a PSD condition — Positivstellensatz *sufficiency*, which is
elementary and is not RC-001's content. Binding it to a family is a separate, evidence-gated
change.

## Order of work

1. **Exact algebra core + SOS verifier** — done, no dependencies.
2. **Untrusted adapter boundary** — `robocert.backends` protocol plus `pyproject.toml` extras;
   first adapter emits a candidate from Julia/SumOfSquares. Generation only.
3. **Gröbner cofactor / ideal-membership checker** on the same core → certified infeasibility
   (`ROADMAP.md` Phase 9).
4. **dReal adapter**, counterexample search only.
5. **Drake/C-IRIS region generation**, checked by (1).

Nothing beyond step 1 is built. Scaffolding an adapter boundary before a generator exists would
be speculative, and the checker is the part that has to be right first.
