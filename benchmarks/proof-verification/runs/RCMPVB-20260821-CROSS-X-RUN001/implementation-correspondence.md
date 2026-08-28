# RC-002 implementation correspondence

Historical checkpoint status: `PASS_RETAINED_WITH_REPLAY_LIMITATION`.

Current delivery status: `INVALIDATED_PENDING_REPLAY`. The unrefereed
`planar2r.exact_witness` family has been removed from the production registry,
and the proposed pose-tolerance family is a different claim shape. This artifact
does not authorize either checker. A future E2-approved family must rerun the
correspondence tests against its exact frozen formula and production code.

This is a separate engineering evidence gate. It is not inferred from either
candidate proof or from the Codex obligation ledger.

## IC1 — Builder coefficients and Boolean structure

The existing implementation-correspondence audit recorded in
`research/reports/phase1-slice1-planar2r-exact-witness.md` compared the shipped
clearance predicates against the proof-text definitions on 108 exact-rational
instances, including all named degeneracies, and reported matching coefficients,
selector/distance pairing, and Boolean structure. The FK coefficient comparison
was additionally justified by linearity.

Current regression evidence includes:

- `tests/test_kinematics2r.py::test_fk_identity_agrees_with_independent_trig_kinematics`;
- `test_fk_identity_vanishes_exactly_at_its_own_witness`;
- `test_worked_instance_satisfies_every_predicate`;
- exact seam/contact and numeric point-to-segment cross-checks in the same file.

Limitation: the 108-instance clearance audit is not retained as a standalone
all-parameter symbolic checker. The Phase 1 report explicitly records this as a
remaining weakness. Therefore this PASS is retained evidence, not a new claim
that the current run completed a symbolic proof over the parameter field.

## IC2 — Existential quantifier and closed box

`build_planar2r_claim` serializes one `EXISTS (t1,t2)` quantifier over the box
domain. Current tests accept exact boundary witnesses and reject out-of-domain
witnesses. The unsupported-quantifier regression test ensures a `FORALL` block is
not silently interpreted as an existential witness.

## IC3 — Historical exact checker evaluation

At the historical checkpoint, the exact-witness checker evaluated rationals,
polynomials, predicates, and formulas using exact arithmetic, and tests exercised
the then-registered family through the production verification boundary. That
registration has since been removed. This paragraph records past evidence only;
it does not describe or authorize the current production boundary.

## IC4 — Fail-closed negative behavior

Current tests reject malformed and non-canonical rationals, out-of-domain
witnesses, infeasible conclusions for this family, corrupted certificate fields,
unsupported quantifier prefixes, and checker exceptions. Rejection does not
produce `CERTIFIED_INFEASIBLE`.

## Checkpoint rule

The full test suite passed at this checkpoint. Any later code change to the
builder, specification, checker, registration, or result-promotion path invalidates
this retained PASS until the affected correspondence and regression gates are
rerun. This artifact alone cannot promote `RC-002` to E2 or E3.
