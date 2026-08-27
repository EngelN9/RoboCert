---
name: isolate-steps
description: Decompose a soundness argument into standalone, context-free implications for adversarial review. Use before dispatching referee-naive, or whenever a multi-step proof/algorithm-correctness argument needs to be checked step by step rather than as a whole.
---

# isolate-steps

The single strongest technique in the adversarial protocol
(`docs/methodology/anthropic-research-methodology-source.md` §7.3). A step that
survives review *in context* — where the reviewer knows what conclusion is wanted —
frequently fails the identical review once that context is removed. Removing the
pull toward the desired conclusion is the point.

## Procedure

1. Read the target proof/argument file (a `research/notes/` sketch or a
   `research/CLAIMS.md` entry's `proof:` file).
2. Break it into its individual inferences — each place where the argument goes
   from some set of established facts to a new one.
3. For each inference, write it as a fully standalone statement:
   - state the hypotheses explicitly and completely, using neutral mathematical
     language (not RoboCert-specific jargon unless the inference is genuinely about
     RoboCert's specific objects, e.g. a rationalized kinematic identity);
   - state the claimed conclusion;
   - **strip all indication of the surrounding conjecture, the desired final
     result, or what the "expected" answer is.**

   Example shape: *"Let `K = {x : g_i(x) >= 0}` for polynomials `g_i` as follows:
   [...]. Does `p(x) >= gamma` for all `x` in `K`? Prove or give a
   counterexample."* — not *"Show that step 4 of the singularity-margin proof is
   valid."*

4. Number the isolated implications (`I-1`, `I-2`, ...) and hand each to
   `referee-naive` (via the `referee` skill or directly through the `Agent` tool)
   as its own, separate task with no other context attached.
5. Collect results keyed by implication number for the audit table.

## Rules

- If an inference is too large to state as one standalone implication, it isn't
  isolated yet — split it further.
- Do not editorialize about which step you expect to be weak when isolating it;
  that reintroduces exactly the context this technique removes.
