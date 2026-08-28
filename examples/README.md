# Examples

Three historical planar-2R research inputs used by the public-gate regression
tests. No E2-approved production checker is registered, so every public
`certify` invocation currently returns `UNKNOWN` without running the legacy
search or constructing a certificate.

| File | Verdict | Exit | Why |
|---|---|---|---|
| `reachable.json` | `UNKNOWN` | 1 | The production certification gate is closed; reachability is not evaluated. |
| `obstacle-blocked.json` | `UNKNOWN` | 1 | The production certification gate is closed; clearance is not evaluated. |
| `out-of-reach.json` | `UNKNOWN` | 1 | The production certification gate is closed; infeasibility is not evaluated. |

Run one:

```bash
robocert certify examples/reachable.json -o /tmp/run
robocert check /tmp/run
```

## Reading the verdicts

`UNKNOWN` means no certificate was accepted. It does **not** mean the property
is false, the target is unreachable, or an obstacle blocks every witness. The
current public command deliberately does not run search, joint-coordinate
conversion, claim construction, or checking. `robocert check` likewise accepts
no stored artifact while the gate is closed.

## Writing your own

The disabled public boundary only checks that the file is JSON and refuses JSON
float literals. It does not validate the historical problem schema or interpret
its joint limits, margins, or geometry. Decimal values should still be written
as strings so future exact parsers do not receive binary floating-point values.

The proposed `0.2.0` format will require exact rational principal-chart bounds
directly. It is intentionally not implemented before RC-002 and RC-005 reach E2.

Full field reference:

```bash
robocert schema problem.schema.json
```
