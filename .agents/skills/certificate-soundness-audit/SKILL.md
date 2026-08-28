---
name: certificate-soundness-audit
description: Independently audit RoboCert mathematical certificates, certificate backends, checkers, and certification results for soundness. Use when reviewing whether a claimed CERTIFIED_FEASIBLE or CERTIFIED_INFEASIBLE result is actually supported by its exact claim, quantifiers, domains, assumptions, transformations, certificate semantics, checker, arithmetic model, tolerances, and inference chain. Also use when auditing COUNTEREXAMPLE, REJECTED, UNKNOWN, solver status, numerical evidence, or a proposed certification pipeline. Do not use for ordinary implementation work, performance tuning, heuristic search, or documentation review that does not assess mathematical soundness.
---

# Certificate Soundness Audit

Independently determine whether a RoboCert result is supported by a valid, reproducible, machine-checkable argument. Treat the solver, certificate generator, checker, and explanatory text as potentially fallible artifacts; the status string alone is never proof.

## Trigger and non-trigger conditions

Use this skill for requests to:

- audit or review a certificate, proof object, certificate schema, certification backend, checker, or certified result;
- determine whether numerical feasibility, infeasibility, collision freedom, reachability, singularity separation, or robustness was certified;
- review a promotion from `NUMERICALLY_*` or `UNKNOWN` to `CERTIFIED_*`;
- assess rejected certificates, counterexamples, unresolved boxes, timeout behavior, or failure semantics;
- inspect whether a backend/checker preserves the stated mathematical claim.

Do not invoke it for:

- ordinary coding, refactoring, optimization, or benchmarking with no soundness question;
- heuristic candidate search or simulation-only exploration, unless the question is whether its output may be called a certificate;
- prose or formatting review that does not evaluate mathematical validity;
- changing a claim to make an invalid certificate pass.

If the request combines implementation with an audit, perform the audit first and keep implementation changes separate and explicitly scoped.

## Audit procedure

### 1. Establish the audit boundary

Identify the exact result, claim identifier, input/model version, certificate artifact, backend, checker, and relevant source revision. Record missing artifacts as `BLOCKED`; never reconstruct absent evidence from solver logs or descriptions. Preserve the repository's existing work and do not modify the claim, certificate, or status while auditing.

State the audit target and the strongest status it could support. Distinguish:

- candidate or search output;
- numerical validation;
- validated interval evidence;
- exact computation;
- checked certificate.

Only `CHECKED_CERTIFICATE` evidence may support `CERTIFIED_*`.

### 2. Reconstruct the exact mathematical claim

Write the theorem in a normalized form before judging the certificate. Include:

- variables and types;
- every equality, weak inequality, strict inequality, Boolean condition, and margin;
- all domains and boundary conventions;
- the complete quantifier prefix and witness dependencies;
- uncertainty sets and their semantics;
- geometry representation and containment direction;
- the requested conclusion and result status.

Check that adjustable, static-robust, and policy claims are not conflated. Check that pointwise reachability is not presented as continuous path lifting, connected safe-region feasibility, or dynamic feasibility.

### 3. Audit assumptions and transformations

Trace every input-to-claim transformation and require its soundness direction. Check frame conventions, units, chart boundaries, denominator nonvanishing conditions, strict inequalities, tolerance interpretation, geometry approximations, eliminated variables, and real-versus-complex solution semantics.

For each transformation, classify it as `EXACT`, conservative outer/inner approximation, relaxation, strengthening, numerical approximation, or unsupported. A transformation that changes the claim must have a stated equivalence proof or a new explicitly labeled claim. Never silently reorder quantifiers, clear denominators, replace `>` with `>=`, treat a mesh or bounding box as exact, or replace correlated uncertainty with an unexplained box.

### 4. Audit certificate semantics

Determine what the certificate actually proves and whether its payload is complete. Verify that it serializes the claim, assumptions, domains, certificate family, input/model hashes, arithmetic model, checker identity/version, and all data required for independent replay.

Check family-specific obligations:

- exact algebra: coefficient field, variable order, identities, elimination conditions, real-root and inequality conditions;
- QE/CAD: original formula, strict/weak semantics, variable ordering, projection data, and a trusted or independently checkable proof artifact;
- SOS/SDP: exact polynomial identity, domain multipliers, rational reconstruction or validated bounds, and positive-semidefinite verification;
- intervals: outward rounding, enclosure validity, complete box coverage, justified pruning, and preserved unresolved boxes;
- geometry/collision: exact or declared conservative containment, separation proof, and clearance margin;
- singularity: stated rank notion and a certified minor or lower bound sufficient for that notion.

Reject certificates that contain only solver logs, floating-point coefficients, residuals, sampled points, optimizer convergence, repeated approximate solver agreement, or an unchecked Gram matrix.

### 5. Audit the independent checker

Review the checker as a separate proof obligation. Verify that it:

- parses and validates the full certificate schema;
- binds all claims and artifacts to exact hashes;
- recomputes rather than trusts solver-reported conclusions;
- checks exact identities, interval inclusion, domain membership, sign conditions, PSD conditions, and geometric containment under the declared arithmetic model;
- fails closed on malformed input, exceptions, unsupported features, missing fields, overflow, timeout, or unresolved subproblems;
- cannot accept a weaker claim than the serialized claim;
- is deterministic and does not depend on hidden solver state or LLM judgment.

Inspect negative and corruption tests. A checker that accepts a mutated coefficient, bound, hash, domain constraint, quantifier, or certificate status is unsound for the affected claim family. Passing tests are evidence about the checker implementation, not proof that the mathematical model is correct; audit both.

### 6. Audit every inference and tolerance

Build a step table with columns:

```text
step | asserted implication | evidence | arithmetic/soundness level | verdict | severity
```

For each implication, ask whether the conclusion follows for all permitted inputs, not merely sampled or typical inputs. Track rounding mode, precision, interval width, epsilon margins, residual thresholds, conditioning, and conversions between units or numeric types. Treat an unvalidated floating-point comparison as numerical evidence only.

Use `fatal` for a gap that invalidates the claimed result, `substantive` for a missing proof obligation, `minor` for a repairable local omission, and `expository` for a valid but underspecified statement. When evidence is absent or cannot be independently reproduced, report `BLOCKED` or `UNKNOWN`, not approval.

### 7. Apply result-status rules

Enforce these interpretations:

- `CERTIFIED_FEASIBLE`: allowed only after a complete certificate is accepted by the appropriate deterministic checker and bound to the exact claim and inputs.
- `CERTIFIED_INFEASIBLE`: allowed only after a checked infeasibility/emptiness certificate or another sound proof of the stated infeasibility claim.
- `COUNTEREXAMPLE`: valid only when the witness is in the stated domain and its violation is itself sufficiently validated. A numerical candidate may be reported as a candidate, not as a validated counterexample.
- `REJECTED`: means the certificate or checker rejected the artifact; do not reinterpret rejection as infeasibility or as proof that the underlying claim is false.
- `UNKNOWN`: is required when certification is not established, including timeout, missing artifacts, unsupported checker features, failed reconstruction, unresolved boxes, or failed certificate search. Failure to certify is not proof of infeasibility.
- `NUMERICALLY_FEASIBLE` and `NUMERICALLY_INFEASIBLE`: remain numerical statuses unless an independent sound proof upgrades them.

Never promote or downgrade a status merely to make a pipeline appear decisive. If the checker accepts a certificate but the claim reconstruction, arithmetic model, or checker implementation is unsound, report the certification as unsupported and identify the exact failure.

## Required audit output

Return a concise but evidence-backed report containing:

1. `Audit target`: exact claim, status, artifact, inputs, and revisions.
2. `Claim reconstruction`: formula, quantifiers, domains, assumptions, and dependencies.
3. `Evidence inventory`: available artifacts and missing evidence.
4. `Soundness findings`: transformation, certificate, checker, arithmetic, tolerance, and inference findings with severity.
5. `Status assessment`: `PASS`, `FAIL`, `BLOCKED`, or `NOT_EVALUATED`, plus the supported RoboCert status if any.
6. `Required repairs`: concrete obligations before certification can be accepted.

Use `PASS` only when the audited claim is fully supported under the declared trust model. Use `FAIL` when a concrete soundness defect defeats the claim. Use `BLOCKED` when required evidence is unavailable. Use `NOT_EVALUATED` when the audit scope was explicitly limited and no conclusion about soundness should be inferred.

Do not certify, merge, release, or alter repository artifacts as a consequence of this audit unless the user separately requests that work. Report limitations plainly, and preserve `UNKNOWN` whenever the proof obligation remains unresolved.
