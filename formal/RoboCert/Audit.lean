/-
# Axiom audit — the fail-closed gate

This file is the Lean analogue of RoboCert's empty production checker registry
(`src/robocert/checking.py:82`). It exists so that a `sorry` cannot reach an audited
theorem silently.

`lake build` only WARNS on `sorry`. `#print axioms` is what actually reveals a
`sorryAx` dependency, so every theorem the project relies on is listed here and CI checks
this file's output. A theorem that is not listed here is not audited.

Expected axiom set for every entry below, and nothing else:

    [propext, Classical.choice, Quot.sound]

If `sorryAx` appears, the build is unsound and CI must fail. See `formal/AGENTS.md`.
-/
import RoboCert.Soundness

namespace RoboCert

-- Adequacy of the Bool evaluator against the Prop semantics.
#print axioms Formula.decideF_iff

-- Evaluation depends only on mentioned variables.
#print axioms Formula.decideF_congr

-- A witness inside every interval induces a valid quantifier-prefix assignment.
#print axioms assignsBox_extendComps

-- The induction carrying the witness through the prefix.
#print axioms semFrom_of_witness

-- THE theorem.
#print axioms exactWitness_sound

end RoboCert
