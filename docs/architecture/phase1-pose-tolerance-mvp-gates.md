# Principal-chart pose-tolerance MVP gate record

Date: 2026-08-24  
Delivery status: **BLOCKED before production implementation**

This record maps the MVP acceptance requirements to the current code/research
seams and evidence. A missing gate is reported as `BLOCKED` or `UNKNOWN`; it is
not inferred from passing tests.

## Current claim boundary

The proposed MVP claim is

\[
\exists(t_1,t_2)\in B:
\|P(t)-P^\star\|^2\le\tau^2
\land C_1(t)\land C_2(t)
\land |\det J(t)|\ge\varepsilon,
\]

where `B` is an exact rational box in principal tangent-half-angle coordinates
and both clearance predicates use the actual rationalized link endpoints. The
MVP does not include four-chart coverage, radian-bound conversion, uncertainty,
task-region universals, path feasibility, counterexample publication, or
certified infeasibility.

## Requirement-to-evidence matrix

| Requirement | Code or research seam | Focused evidence | Full regression evidence | Status |
|---|---|---|---|---|
| Unrefereed checker cannot certify | `src/robocert/checking.py::_PRODUCTION_CHECKERS` | `tests/test_checking.py::test_unrefereed_planar2r_family_is_not_registered` | 121 tests | PASS |
| Public CLI avoids legacy four-chart and float conversion | `src/robocert/cli.py::_cmd_certify_disabled` | `test_closed_gate_does_not_enter_legacy_search_or_limit_conversion`; focused 41 tests | 121 tests; Ruff; mypy | PASS |
| RC-002 independent theorem intake | RUN001 `ledger-codex.md`, `ledger-claude.md`, and metadata hashes | run validator checks hashes, fresh contexts, and Claude hard-disabled tools | RUN001 manifest validator | PASS |
| RC-002 P1/P2 blind audits | RUN001 Codex P1/P2 audit artifacts | both frozen Codex audits found substantive omissions | run stopped; Claude audits blocked before inference | FAIL / BLOCKED |
| RC-002 proof repair | `research/proofs/rc002-frozen-task-corrigendum-2026-08-24.md` | explicit existential, sign bridge, syntax, degeneracy, and scope repairs | ledger parser passes | BLOCKED on project-owner E1 read; no new run |
| Old one-inequality tolerance route rejected | RC-003 and `research/ATTEMPTS.md` A-001 | exact rational counterexample recomputed: virtual clearance squared `1/8`, required radius squared `1/16`, actual clearance squared `0` | ledger parser passes | PASS (`EX`) |
| Correct actual-endpoint tolerance theorem | RC-005 and `research/proofs/planar-2r-pose-tolerance-witness-proof-rc005.md` | E0 proof covers tolerance clearing, actual segments, selectors, seams, nondegeneracy, singularity, and existential transport | ledger parser passes | BLOCKED on project-owner E1 read |
| RC-005 hostile/naive, isolated-step, and negation controls | future RC-005 referee artifacts | none authorized at E0 | none | BLOCKED by E1 precondition |
| Problem schema `0.2.0` | future `schemas/problem.schema.json` and parser | not written because proof gates are closed | current packaged schema remains `0.1.0` | BLOCKED |
| Versioned pose-tolerance payload schema | future family payload schema | not written | none | BLOCKED |
| Corrected claim builder | future principal-chart builder | not written | none | BLOCKED |
| Full normalized-problem model hash and claim reconstruction | future `certify`/`check` path | not written | none | BLOCKED |
| Production family registration | future `planar2r.pose_tolerance_witness` registry entry | registry is deliberately empty | public examples return `UNKNOWN` | BLOCKED until RC-002 and RC-005 reach E2 and correspondence passes |
| Build and packaged schema presence | external `robocert-dist-final4-20260824` artifacts | wheel and sdist contain all four current `0.1.0` schemas; clean wheel import reports `production_registry=()` and `square_metre` support | wheel SHA-256 `371491643B51E387A37C6EE0B688D9BD7DDF78B29B950CC40D99182123DF0C6E`; sdist SHA-256 `ECF3F439EC13CDA6728B4354D92BB0C356D4B57823B75F4FC6062B3664DC674F` | PASS for current Phase 0 package only |
| Independent certificate soundness audit | three fresh read-only audits under `research/reports/` | first two audits found only acknowledged gates plus repairable consistency defects; all defects were repaired | `2026-08-24-certificate-soundness-audit-final-confirmation.md` reports no remaining actionable concrete FAIL | PASS for the current fail-closed delivery; not approval of a checker |

## Frozen RUN001 disposition

`RCMPVB-20260821-CROSS-X-RUN001` is permanently a failed run for promotion.
Both Codex blind audits judged the central pointwise geometry substantially
sound but found substantive frozen-task omissions. Claude P1/P2 audits could not
start because the provider reported a session limit. No adjudication, negation
control, or E2 promotion followed. Repairs require a new run id; RUN001 artifacts
remain frozen and hash-validated.

## Human and external prerequisites

Before any production checker, schema `0.2.0`, or claim builder is implemented:

1. the project owner must read the RC-002 corrigendum line by line and explicitly
   attest that it repairs A-002;
2. the project owner must read the RC-005 proof line by line and explicitly
   attest it for E1;
3. a new RC-002 frozen run must complete both providers' blind audits and all
   required controls without unresolved fatal or substantive findings;
4. RC-005 must complete fresh hostile and isolated naive reviews plus a negation
   control under the `referee` protocol; and
5. deterministic implementation correspondence must be produced for the exact
   code proposed for registration.

Until then, `UNKNOWN` is the only public certification outcome.
