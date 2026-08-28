# Phase 0 Formal Core

RoboCert's Phase 0 package defines the data and promotion boundaries that every
future solver and certificate family must obey. It does not certify a robot,
configuration, task, or geometry.

Research-only planar-2R modules now coexist with this core, but they are not
wired into the public CLI and no production checker is registered. Their
presence does not change the Phase 0 promotion boundary.

## Artifact flow

```text
immutable Claim
      |
      v
canonical UTF-8 JSON --SHA-256--> claim hash
      |                              |
      |                              v
      +----------------------> candidate Certificate
                                      |
                                      v
                         registered deterministic Checker
                                      |
                              +-------+-------+
                              |               |
                            PASS            FAIL
                              |               |
                              v               v
                    CheckedCertificate      UNKNOWN
                              |
                              v
                         CERTIFIED_*
```

Phase 0 contains no registered production checker. Consequently,
`verify_certificate()` rejects every candidate family with a diagnostic and no
public Phase 0 operation can produce a `CheckedCertificate`.

## Public Python contracts

The `robocert.specification` module provides immutable values for:

- exact rational coefficients and interval endpoints;
- variables, units, interval axes, and box domains;
- ordered quantifier blocks;
- canonical sparse polynomials and typed relations;
- Boolean formulas over declared predicates;
- assumptions, margins, uncertainty semantics, geometry semantics, and provenance;
- complete formal claims.

`Claim.from_dict()` rejects unknown fields, unknown schema versions, noncanonical
rationals and polynomials, duplicate identifiers, invalid unit/domain bindings,
missing variables, reordered domain bindings, and formula references to missing
predicates.

The certificate and result layers provide:

- `Certificate`, which is only a candidate artifact;
- `Checker`, the deterministic checker protocol;
- `CheckReport`, which records acceptance or fail-closed diagnostics;
- `CheckedCertificate`, which can only be constructed by the checker runner;
- result factories that prevent numerical results from becoming certified results.

## Serialization and hashing

All Phase 0 schemas use version `0.1.0`. Canonical serialization uses UTF-8 JSON
with sorted object keys, no insignificant whitespace, and no ASCII escaping.
JSON floating-point values are forbidden. Exact numeric data uses:

```json
{"numerator": 1, "denominator": 1000}
```

Rationals must be reduced and have a positive denominator before serialized input
is accepted. Digests are represented as `sha256:` followed by 64 lowercase
hexadecimal characters.

Object-key order does not affect a digest. Quantifier order, relation kind,
assumptions, margins, provenance, units, and boundary openness do affect it.

## JSON schemas

The versioned schemas are:

- `schemas/claim.schema.json`;
- `schemas/certificate.schema.json`;
- `schemas/result.schema.json`.

Every versioned artifact object rejects unknown properties. A certificate payload
is the intentional extension point for a future certificate-family schema; it may
contain arbitrary exact JSON values but cannot contain floating-point numbers.

JSON Schema validation checks wire shape. Python construction performs the
cross-reference and canonical-form validation that JSON Schema cannot express,
such as reduced fractions, interval ordering, quantifier/domain correspondence,
and declared predicate references.

## Phase 0 limitations

- No robot or geometry model is enabled in the production core. Quarantined
  planar-2R research modules exist but are not public certification features.
- No solver, search backend, exact certificate family, or interval certificate
  family is enabled on a production path.
- No production checker is registered.
- No physical-system or standards-compliance claim follows from these APIs.
- Deserializing a candidate certificate never creates a checked certificate.
