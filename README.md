# RoboCert

RoboCert studies independently checkable mathematical claims about robot configurations: reachability, modeled collision clearance, joint limits, and singularity margins, eventually under bounded uncertainty. A result counts only when a serialized claim with explicit assumptions and domains has a certificate that a deterministic checker, bound to the exact inputs, accepts.

Search, optimization, and simulation can propose candidates. They never certify anything. `UNKNOWN` means no certificate was accepted; it does not mean the claim is false or infeasible.

## Status at a glance

**Research / pre-alpha. No robot property and no physical safety property is currently certified.**

- The production checker registry is empty (`src/robocert/checking.py`, `_PRODUCTION_CHECKERS`).
- `robocert certify` returns `UNKNOWN` without running search or building a certificate. `robocert check` accepts no certificate family.
- The long-term goal is a research direction, not a capability. See [certification goals](docs/concepts/certification-goals.md).

## Implemented (research code, not registered)

None of the following can produce a `CERTIFIED_*` result.

- **Formal core.** Typed claims, versioned schemas, canonical hashes, and the result contract (v0.2.0; claims and certificates v0.1.0). See [formal core](docs/architecture/formal-core.md).
- **Closed public gate.** The fail-closed CLI and its checker boundary. See [trusted computing base](docs/architecture/trusted-computing-base.md).
- **Planar 2R.** Exact-witness encoding and candidate search (`kinematics2r.py`, `certify2r.py`, `witness_search2r.py`), research use only (RC-002).
- **Exact algebra.** Rational polynomial identity, exact PSD, and SOS certificate verification utilities (`polynomial.py`, `linalg_exact.py`, `sos.py`), bound to no certificate family (RC-006).
- **Refutation.** `refute` as a library API only; it is deliberately not wired into the CLI or reports (RC-007).
- **Joint limits.** Inward rational rounding of radian joint limits to half-angle boxes (RC-004).
- **Simulation.** An optional MuJoCo falsification search. Its outcomes are leads, not evidence. See [examples](examples/README.md).
- **Formal proofs.** Lean 4, Rocq, and Isabelle developments prove selected properties of *models*, with recorded fidelity gaps. They prove nothing about the Python code or a physical robot. See [formal scope](formal/README.md).

## Research claims and open obligations

The table is a snapshot as of 2026-09-30. [`research/CLAIMS.md`](research/CLAIMS.md) is authoritative, and the [evidence tiers](research/README.md) define E0–E4 and EX.

| Claim | Subject | Tier | Next open obligation |
|---|---|---|---|
| RC-001 | Proposed SOS certificate scheme for a planar-2R singularity margin under interval link-length uncertainty | E0 | Unreviewed E0 sketch only; statement to be made precise (roadmap G2) |
| RC-002 | Planar-2R exact rational witness encoding for one fixed instance | E1 | Owner read of the corrigendum, then a fresh frozen referee run (RUN001 stopped with substantive findings and cannot be reused; A-002) |
| RC-003 | One-inequality pose tolerance | EX | Refuted (`research/ATTEMPTS.md` A-001); never to be reused |
| RC-004 | Inward joint-limit rounding | E0 | Owner read of the correspondence argument |
| RC-005 | Actual-endpoint pose-tolerance witness | E0 | Owner read; its E2 is capped by RC-002 |
| RC-006 | Exact rational SOS verifier correspondence | E0 | Owner read of the correspondence argument |
| RC-007 | `refute` correspondence | E0 | Owner read; CLI and report gate stays closed until E1 |
| RC-014 | Proposed uniform-branch planar-2R layout certificate family | E0 | Exact domain coverage, algebraic witness, checker soundness, and owner checkpoint; [first-target strategy](docs/strategy/first-target.md) |

Cross-cutting obligations before any production checker:

- implementation correspondence for the exact code proposed;
- the full [certificate-family obligation](docs/architecture/trusted-computing-base.md#future-certificate-family-obligation), including one adversarial *human* review;
- closing the attestation-binding gap: the Lean attestation does not hash `Semantics.lean`, the file that fixes what its theorem means.

The [MVP gate record](docs/architecture/phase1-pose-tolerance-mvp-gates.md) lists the gates for the proposed pose-tolerance family (RC-005).

## Direction (proposals, not capabilities)

The [roadmap](ROADMAP.md) orders the research work. Its order sets priority; it is not evidence and changes no tier.

1. Close the existing planar-2R evidence gates, and review the rational polynomial, PSD, and SOS primitives that later work shares.
2. Specify a checkable singularity-margin family under interval link-length uncertainty (RC-001).
3. State an explicit uncertainty-inflation bound that uses RC-005-style actual-link clearance and outward joint-box enclosures.
4. Measure whether a precision SCARA-style planar slice keeps useful margins.
5. Test whether third-party configuration-space certificates can be exported for independent rational-arithmetic recheck.

Spatial arms, paths, dynamics, and clinical or industrial safety assurances are later or out of scope. The [strategy note](docs/strategy/revised-direction.md) records the rationale, the gates, and what remains unverified.

## Try it

Use Python 3.11 or newer:

```text
python -m venv .venv

# Windows PowerShell
.venv/Scripts/python -m pip install -e ".[dev]"
.venv/Scripts/python -m pytest --basetemp=.pytest-basetemp

# POSIX shell
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest
```

On POSIX systems without a `python` command, use `python3 -m venv .venv` for the first line.

The [development guide](docs/development.md) lists the full set of CI checks. The [examples](examples/README.md) show the closed public gate and the research-only simulation outcomes.

## Documentation

| Document | Purpose |
|---|---|
| [ROADMAP.md](ROADMAP.md) | Ordered research plan, dependencies, and decision gates |
| [docs/strategy/revised-direction.md](docs/strategy/revised-direction.md) | Why the direction changed, and what was not adopted |
| [docs/concepts/certification-goals.md](docs/concepts/certification-goals.md) | Target claim shapes, result statuses, terminology |
| [docs/architecture/proposed-methods.md](docs/architecture/proposed-methods.md) | Method families and their proof obligations |
| [docs/architecture/formal-core.md](docs/architecture/formal-core.md) | Implemented claim model and serialization |
| [docs/architecture/trusted-computing-base.md](docs/architecture/trusted-computing-base.md) | What is trusted, and the checker-registration obligation |
| [docs/architecture/backends.md](docs/architecture/backends.md) | External solvers as untrusted generators |
| [research/README.md](research/README.md) | Evidence tiers and ledger rules |
| [formal/README.md](formal/README.md) | Scope of the proof-assistant developments |
| [docs/SESSION_HANDOFF.md](docs/SESSION_HANDOFF.md) | Current continuation record |
| [AGENTS.md](AGENTS.md) | Canonical engineering and soundness policy |
| [overview](docs/archive/initial-project-overview.md) and [phased roadmap](docs/archive/initial-phased-roadmap.md) | The original overview and phased roadmap, historical only |

Licensed under [Apache-2.0](LICENSE). RoboCert does not establish the safety of a physical robot, medical device, or deployment.
