# Phase 0 Trusted Computing Base

This document records the initial trusted-computing-base (TCB) boundary. It is a
design declaration, not an external validation or formal proof of the
implementation.

## Trusted for Phase 0 artifact identity

The following components determine the meaning or identity of a Phase 0 artifact:

| Component | Role | Failure consequence |
| --- | --- | --- |
| Specification constructors and parsers | Enforce typed claim semantics and references | A malformed or semantically different claim may be accepted |
| Canonical JSON encoder | Produces platform-independent artifact bytes | Equivalent artifacts may hash differently or distinct artifacts may be confused |
| SHA-256 implementation | Binds claims, models, and provenance | Artifact identity may be incorrect |
| Certificate preflight checks | Bind certificate metadata to the exact claim/model/checker | A certificate may be checked against the wrong theorem |
| Result promotion factories | Restrict `CERTIFIED_*` to accepted checker output | Numerical or unchecked evidence may be promoted |
| Python runtime and standard library | Execute all above components | Any trusted behavior may be incorrect |

The JSON Schema validator used in development tests is not the sole enforcement
mechanism. Runtime constructors independently reject malformed data so package
soundness does not depend on applications remembering to run JSON Schema first.

## Not trusted for certification

The following may propose evidence but can never directly emit a certified result:

- optimization or numerical solver adapters;
- candidate certificate generators;
- sampling, simulation, or counterexample search;
- orchestration agents or LLM output;
- reporting and visualization layers;
- third-party code implementing the `Checker` protocol but not registered by the
  RoboCert package.

Phase 0 deliberately registers no production checker. Test code temporarily
installs either a deterministic fixture checker or the quarantined RC-002
research checker into the private registry to exercise promotion, mathematical
evaluation, and corruption rejection. Those monkeypatched registrations are
test evidence only; neither is a production checker.

## Future certificate-family obligation

Adding a production checker requires a reviewed code change that:

1. defines a versioned certificate-family payload schema;
2. states the exact theorem and arithmetic semantics checked;
3. identifies all additional trusted libraries and versions;
4. provides positive, negative, adversarial, and corrupted-certificate tests;
5. binds the checker identity, version, arithmetic mode, claim hash, model hash,
   assumptions, and provenance;
6. fails closed on malformed artifacts, unsupported versions, exceptions, and
   resource exhaustion;
7. documents independently known benchmark truth and remaining limitations.
