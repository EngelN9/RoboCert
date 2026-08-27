---
name: referee
description: Adversarially review a research/CLAIMS.md soundness argument and promote it from E1 to E2. Use when a claim's proof file is believed correct and ready for independent review, or when explicitly asked to referee/audit a research claim.
---

# referee

Implements the adversarial verification protocol this project's methodology is
built on (`docs/methodology/anthropic-research-methodology-source.md` §7). This is
the only path from `E1` to `E2` in `research/CLAIMS.md` — see
`research/README.md` rule 1: **a context that produced an argument may never
evaluate it.**

## Preconditions

- The target `RC-xxx` entry exists in `research/CLAIMS.md` at `tier: E1`.
- Its `proof:` file contains a full soundness argument a human has already read and
  believed (that's what `E1` means).

If either is false, stop and say so — do not referee an `E0` sketch or an argument
nobody has read yet.

## Procedure

1. **Isolate steps.** Use the `isolate-steps` skill to decompose the proof into
   standalone, context-free implications — each with the conjecture/claim goal
   stripped out.

2. **Dispatch hostile + naive review in parallel, in fresh contexts.** Use the
   `Agent` tool to run:
   - `referee-hostile` (`.claude/agents/referee-hostile.md`) on the full argument,
     told it contains an error and asked to find it.
   - `referee-naive` (`.claude/agents/referee-naive.md`), once per isolated
     implication from step 1, with zero conjecture context.

   Do this in one message with multiple tool calls (parallel), not sequentially —
   these are independent reviews and must not see each other's output.

3. **Negation control.** Pick the claim's central inequality or existence/uniqueness
   statement. Run its negation through the same `referee-naive` review. If the
   pipeline produces a confident "proof" of both the claim and its negation, the
   pipeline has no discriminating power on this material — stop, do not promote,
   and log this as an `A-xxx` entry in `research/ATTEMPTS.md` instead ("referee
   pipeline miscalibrated on this material", not a claim about the math).

4. **Compile the audit table.** For every step reviewed:

   | Step | Claim | Dependency | Valid? | Issue | Severity |
   |---|---|---|---|---|---|

   Severity: `fatal` (destroys the claim) / `substantive` (major missing argument) /
   `minor` (repairable local gap) / `expository` (valid but underspecified).

5. **Decide.**
   - Any `fatal` finding → do not promote. Log the failure point in
     `research/ATTEMPTS.md` via `log-attempt`, or in `research/OBSTRUCTIONS.md` if
     three or more independent attempts have now failed at the same requirement.
   - Only `substantive`/`minor`/`expository` findings, all addressed or explicitly
     accepted as known limitations → promote.

6. **Promote.** Append the audit table to the claim's `proof:` file (or a sibling
   file referenced from it), then edit `research/CLAIMS.md`:
   - `tier: E2`
   - `referee: <path to the audit table>`
   - append a `history:` line, e.g. `- <date> -> E2 after hostile+naive referee`

   `scripts/check_ledger.py` runs automatically on this edit and will reject the
   promotion if `referee:` is still `none` or no `history:` line was added — this is
   enforcement, not just a reminder.

## Rules

- Never ask "is this proof correct?" — that's answered agreeably. Ask "this
  argument contains at least one error; find it," per the hostile-framing principle.
- `referee-hostile` and `referee-naive` have no Edit/Write access — they cannot
  "fix" what they're reviewing, only report on it.
- False positives from a hostile referee are cheap to dismiss; a missed error is
  not. When in doubt, don't promote.
