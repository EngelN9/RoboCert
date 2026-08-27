---
name: log-attempt
description: Log an abandoned proof or algorithm-design attempt to research/ATTEMPTS.md with a diagnosed failure point. Use whenever a proof strategy, reduction, or algorithm design is abandoned or fails referee review — not for successes.
---

# log-attempt

Failed attempts are data, not noise (`research/README.md` workstream mapping, W4).
"This didn't work" is not an acceptable entry — a diagnosed failure point is.

## Procedure

1. Find the next free `A-<number>` in `research/ATTEMPTS.md`.
2. Fill in every field of the entry format there. In particular:
   - `broke_at` must name the *exact* step, lemma, or inequality that failed — not
     "the general case" or "the harder part."
   - `required` must state the precise proposition that step actually needed.
   - `status_of_required` must be one of `true`/`false`/`unknown` — if you don't
     know, say `unknown`, don't guess.
   - if `status_of_required: false`, include the smallest counterexample you have,
     or dispatch the `adversary` agent to find one before closing the entry.
3. Append the entry to `research/ATTEMPTS.md`.
4. Check for a pattern: search existing `A-xxx` entries for the same `broke_at`
   requirement across different `route`s. If this is the **third or more**
   independent route failing at the same requirement, that's a candidate
   obstruction — draft an `research/OBSTRUCTIONS.md` entry (see that file's format)
   with `barrier_statement` set to the shared `required` proposition, and consider
   attacking it directly with the `adversary` agent before accepting it as real.

## Do not

- Do not delete or water down a failed attempt because it's embarrassing or because
  a later attempt superseded it. The reason it failed is often the most valuable
  content in the repository.
- Do not log an attempt that's still in progress — this skill is for routes that
  are genuinely abandoned or definitively refuted, not a running scratchpad (use
  `research/notes/` for that).
