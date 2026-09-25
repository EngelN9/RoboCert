# External solver backends

RoboCert's pipeline is `search -> certificate construction -> independent deterministic checker`.
Every external mathematical or robotics system named here belongs on the **left** of that arrow.
None is trusted, none is a dependency, and none appears on the certification path.

```text
search / simulation
        |
        v
candidate or counterexample
        |
        v
formal certificate construction
        |
        v
independent checker
        |
        +----> CERTIFIED
        |
        +----> REJECTED / UNKNOWN
```

Every backend on this page lives in the **first box**. Nothing any of them produces enters the
third box except as an artifact the checker re-derives for itself.

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
| **MuJoCo** | Untrusted **falsification / search** only | *none* | *n/a -- its output is not a certificate* | **None** -- optional extra, never imported by the core |
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

## MuJoCo is not a certificate family

MuJoCo is the first backend here that is a **physics** engine rather than a mathematics one, and
that difference is the whole point of its boundary.

Every other backend on this page argues about *the same mathematical object* RoboCert certifies —
a Julia SOS decomposition and RoboCert's exact checker are talking about one polynomial. MuJoCo is
not. It integrates rigid-body dynamics with link inertia, contact compliance, actuator models,
friction, and gravity, none of which appear in the kinematic model a RoboCert claim quantifies
over. It is deliberately the *higher-fidelity* model.

Two consequences follow, and neither is negotiable:

1. **A MuJoCo contact does not falsify a RoboCert claim.** It falsifies a statement about MuJoCo's
   model. Under `AGENTS.md` §31 a `COUNTEREXAMPLE` requires a witness validated *in the claim's own
   domain, against the claim's own predicate*, in exact arithmetic. A violating configuration found
   here is a **lead** for that validation, not a substitute for it. `FalsificationOutcome`
   deliberately shares no member name with `ResultStatus`, and
   `tests/test_simulation_boundary.py` fails if `robocert/simulation/` ever names a promotion
   symbol in executable code.
2. **`NO_COUNTEREXAMPLE_FOUND` is not evidence of anything.** A finite sample that failed to break
   a property says nothing about the unsampled continuum (`AGENTS.md` §4.4). It is a failed
   refutation. The one place it may be cited is as the adversarial-search step in `AGENTS.md` §68's
   milestone criterion 4 — which is a check that no contradiction was found, explicitly not a proof
   that none exists.

### Cashing a lead

`src/robocert/refutation.py` is where a lead becomes a result, and the direction of the
dependency is the point: **the untrusted layer proposes, the trusted core decides.**
`robocert.simulation` does not import `refutation` and never calls it. The composition happens in
the caller:

```text
search_for_counterexample(...)   -> FalsificationReport      (untrusted; simulation model)
candidate_assignment(..., transform=...)
                                 -> Mapping[str, Rational]   (untrusted; exact conversion)
refute(claim, model_hash, ...)   -> RefutationReport         (trusted; claim's own model)
counterexample_result(...)       -> ResultStatus.COUNTEREXAMPLE
```

`refute` re-derives everything from the claim alone and rejects unless the prefix is purely
universal, the point lies in the declared domain, and the whole formula is exactly false there.
A rejection is `UNKNOWN`. Two rejections are worth expecting rather than treating as bugs: a
candidate outside the claim's domain, and a candidate that violates the *simulator's* property
while satisfying the *claim's* formula — the second is the two-model gap showing up honestly.

`candidate_assignment` converts exactly by default, because a Python float is a dyadic rational
and `Fraction(value)` is the sampled point itself. Rounding via `max_denominator` is available for
a more auditable witness and is harmless: a counterexample need not be the simulator's point, only
*a* point of the domain where the formula is false, and the rounded point is re-checked from
scratch.

**Coordinates.** `candidate_assignment` maps sampled coordinates onto claim variables
positionally, and the identity default is only right when coordinates and units already agree. A
claim in tangent-half-angle variables `t = tan(q/2)` does not correspond to sampled radians, so
pass `transform=robocert.witness_search2r.angle_to_t_candidate`.

That transport needs no rounding-direction argument, which is worth stating because its sibling
`joint_limits_to_t_bounds` does. That function builds a *domain*, which nothing downstream
re-derives, so its inward rounding is what makes the certified box a subset of the requested one.
A candidate *point* is re-derived from scratch by `refute`, so rounding direction can cost a lead
but cannot buy an unsound acceptance. It is ergonomics, not soundness.

**Why the shipped example still stops at the report.** Not the transport -- that works. There is
no universally quantified planar-2R claim for a transported point to refute, and building one is
blocked on mathematics rather than plumbing. `kinematics2r.build_planar2r_claim` is an
`exists (t1, t2)` claim carrying exact forward-kinematics equalities, while `refute` requires a
purely universal prefix. Dropping those equalities and flipping the prefix does not work: P2
Proposition 9.4(3) and Remark 9.5 prove the second-segment clearance conjunct *unsound
standalone* -- it holds at parameters where the true distance is arbitrarily small -- and
meaningful only inside the conjunction the FK equalities complete. A universal safety claim
therefore needs a new encoding deriving the second link's endpoint from `(t1, t2)` rather than
from the fixed target constant, at higher polynomial degree. That is a new `RC-xxx` at `E0` with
its own referees, not a helper function. Logged as `A-003` in `research/ATTEMPTS.md`, which also
notes that `A-001` failed at the same underlying requirement.

What it is genuinely good for: contact and collision experiments, actuator-torque and joint-limit
validation, gravity/friction/inertia sanity checks, adversarial sampling of a candidate safe
region, and comparing the algebraic model against a richer physical one so that a disagreement
surfaces as a lead rather than as a silent modelling error.

**Where it lives.** `src/robocert/simulation/` — `mujoco_backend.py` is the only module in the
repository that imports `mujoco`, `robocert/__init__.py` does not import the subpackage at all, and
the subpackage imports nothing from `robocert.checking`, `robocert.results`,
`robocert.certificates`, or `robocert.checkers`. `pyproject.toml`'s `dependencies` remains `[]`;
MuJoCo is the `mujoco` extra and is not installed in CI.

**What CI does and does not cover.** The MuJoCo-dependent tests skip when the extra is absent, so
CI never executes `mujoco_backend.py`. It does still *type-check* it: `mypy --strict` covers the
whole package and the `mujoco.*` override supplies the missing stubs, so a signature or name error
in that module fails CI even though no simulation runs. What escapes CI is behavioural drift in
MuJoCo's own API, which only a local run with the extra installed will catch.

**Reproducibility, and its limit.** Every report records the MuJoCo version, the SHA-256 of the
MJCF, the random seed, the timestep, the solver settings, the sample count, and each violating
configuration. That is enough to replay the search *on the recorded version and platform*. It is
not a cross-version guarantee: a physics engine may change its solver between releases, and this
project does not claim otherwise. The whole provenance record sits inside the report's digest, so
two searches that differ in version, model, asset tree, timestep, or margin cannot present the
same hash.

**What the model digest does and does not identify.** `model_sha256` covers the entry MJCF only.
A model that pulls in `<include>` files, meshes, or textures is not identified by that digest, so
`SimulationProvenance.model_external_references` lists the paths the file declares. An empty list
means the model is self-contained and the digest is complete; a non-empty one means the report is
reproducible solely alongside the same asset tree, and says so rather than leaving the reader to
assume otherwise. The paths are recorded as declared — `meshdir`/`assetdir` are not resolved and
nested includes are not followed, because a half-correct resolution would be a worse provenance
record than an honest list of what was referenced.

**No ledger entry.** `research/CLAIMS.md` records research/design claims about algorithms,
reductions, and checker soundness. This integration asserts none — its outputs are stipulated never
to cross the boundary, so there is no soundness proposition to referee. Adding an `E0` entry would
misdescribe what was built.

**Quantifier elimination is kept experimental** for the same reason: a QE result is not
independently checkable without redoing the elimination, so it cannot back a `CERTIFIED_*`
family. It remains useful for exploration and for generating candidates that other families can
certify.

## What exists today

`src/robocert/polynomial.py`, `src/robocert/linalg_exact.py`, and `src/robocert/sos.py` — the
exact-algebra core and the Positivstellensatz verifier. No adapter on the *certificate* side is
installed or invoked, and `dependencies = []` is unchanged.

`src/robocert/simulation/` — the MuJoCo falsification layer described above. It is the one
external tool with an adapter, and it is on the search side only: it emits no certificate, so
there is nothing for it to be checked against.

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
   (Phase 9 of the archived `docs/archive/initial-phased-roadmap.md`; not in the current
   `ROADMAP.md` order).
4. **dReal adapter**, counterexample search only.
5. **Drake/C-IRIS region generation**, checked by (1).

Nothing beyond step 1 is built on the certificate side. The MuJoCo falsification layer sits
outside this ordering entirely: it is ordered by checker cost, and MuJoCo emits nothing a checker
could accept, so it neither blocks nor is blocked by any step above. Scaffolding an adapter boundary before a generator exists would
be speculative, and the checker is the part that has to be right first.
