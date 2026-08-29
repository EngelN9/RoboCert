/-
# The well-formedness a soundness proof actually consumes

`src/robocert/specification.py::Claim.__post_init__` (lines 670-760) enforces a long list of
invariants. Only one consequence of them is needed to prove the exact-witness checker sound,
and it is isolated here rather than re-deriving the whole validator in Lean.

`Claim.FormulaVarsQuantified` says: every variable the formula can mention is bound by some
quantifier block's domain. In Python this follows from three separate checks:

  * `specification.py:749-755` -- every predicate references only declared variables;
  * `specification.py:745-747` -- every declared variable is quantified exactly once;
  * `specification.py:738-743` -- a block's `variable_ids` equal its domain's component
    variables, in order.

**Correspondence obligation (open, Phase 0.5b):** that the Python validator implies this Lean
predicate is asserted, not proved. It is exactly the kind of claim the differential
conformance harness is for. Recorded in `formal/README.md`.
-/
import RoboCert.Semantics

namespace RoboCert

/-- `x` occurs in some monomial of `p`. -/
def Polynomial.Mentions (p : Polynomial) (x : String) : Prop :=
  ∃ t ∈ p.terms, ∃ pw ∈ t.powers, pw.variableId = x

/-- `x` occurs on either side of `pr`. -/
def Predicate.Mentions (pr : Predicate) (x : String) : Prop :=
  pr.left.Mentions x ∨ pr.right.Mentions x

/- Variables a formula can mention, resolved through the claim's predicate table. -/
mutual

def Formula.Mentions (c : Claim) : Formula → String → Prop
  | .pred id, x =>
    match c.findPredicate id with
    | Option.some p => p.Mentions x
    | Option.none => False
  | .and ops, x => Formula.MentionsAny c ops x
  | .or ops, x => Formula.MentionsAny c ops x
  | .not f, x => Formula.Mentions c f x

def Formula.MentionsAny (c : Claim) : List Formula → String → Prop
  | [], _ => False
  | f :: fs, x => Formula.Mentions c f x ∨ Formula.MentionsAny c fs x

end

/-- `x` is bound by the domain of one of `blocks`. -/
def BoundBy (c : Claim) (blocks : List QuantifierBlock) (x : String) : Prop :=
  ∃ b ∈ blocks, ∃ d, c.findDomain b.domainId = Option.some d ∧
    ∃ comp ∈ d.components, comp.variableId = x

/-- The single well-formedness consequence the soundness theorem consumes. -/
def Claim.FormulaVarsQuantified (c : Claim) : Prop :=
  ∀ x, Formula.Mentions c c.formula x → BoundBy c c.quantifiers x

end RoboCert
