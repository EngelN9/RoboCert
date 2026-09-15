/-
# RoboCert claim semantics

This is the file that matters. It says what a `Claim` MEANS, independently of any checker.

The soundness theorem in `Soundness.lean` concludes `Claim.Semantics`, so everything the
project is entitled to believe from a Lean-checked acceptance is bounded by what is written
here. Read this file before trusting that theorem.

Two scope limits, both deliberate and both load-bearing:

1. **Rationals, not reals.** `Claim.Semantics` quantifies over `Rat`, mirroring the exact
   rational arithmetic of `src/robocert/checkers.py`. RC-005's bounded existential quantifies
   over the REALS in its box. For a purely existential claim the transport `∃ℚ → ∃ℝ` is the
   sound direction, so nothing here is wrong -- but it is an unproved step, and a claim with a
   `forall` block over ℝ is NOT implied by its ℚ counterpart. Deferred to Phase 0.5b, which
   needs mathlib.
2. **Model, not machine.** Nothing here is a statement about a physical robot.

Fail-closed convention: an unresolvable reference (missing domain, missing predicate, missing
variable binding) makes the semantics `False` rather than vacuously true. That is the safe
direction for a soundness theorem -- it forces the checker to reject.
-/
import RoboCert.Syntax

namespace RoboCert

/-- A partial assignment of exact rationals to variable identifiers. -/
def Env := String → Option Rat

/-- The empty environment binds nothing. -/
def Env.empty : Env := fun _ => Option.none

/-- Bind (or rebind) one variable. -/
def Env.extend (e : Env) (name : String) (v : Rat) : Env :=
  fun n => if n = name then Option.some v else e n

/-- Exact rational power. Written out rather than relying on a `Monoid.npow` instance. -/
def ratPow (v : Rat) : Nat → Rat
  | 0 => 1
  | n + 1 => v * ratPow v n

/-- Evaluate a monomial. `none` if any variable is unbound -- mirrors the `KeyError` that
`src/robocert/checkers.py:145` catches and turns into a rejection.

The mechanism is faithful; the path is not live. From a valid `Claim` this `none` is
unreachable: every predicate variable must be declared and every declared variable quantified
exactly once (`specification.py:746`, `:751`), so the domain-membership check rejects a missing
binding before the formula is evaluated at all. Both sides still reject, for different reasons.
Recorded as divergence 9 in `formal/README.md`. -/
def evalPowers (e : Env) : List MonomialPower → Option Rat
  | [] => Option.some 1
  | pw :: rest =>
    match e pw.variableId, evalPowers e rest with
    | Option.some v, Option.some acc => Option.some (ratPow v pw.exponent * acc)
    | _, _ => Option.none

/-- `checkers.py::evaluate_polynomial`, inner loop. -/
def Term.eval (t : Term) (e : Env) : Option Rat :=
  match evalPowers e t.powers with
  | Option.some m => Option.some (t.coefficient * m)
  | Option.none => Option.none

def evalTerms (e : Env) : List Term → Option Rat
  | [] => Option.some 0
  | t :: rest =>
    match t.eval e, evalTerms e rest with
    | Option.some a, Option.some b => Option.some (a + b)
    | _, _ => Option.none

/-- `checkers.py::evaluate_polynomial`. -/
def Polynomial.eval (p : Polynomial) (e : Env) : Option Rat := evalTerms e p.terms

/-- The order relations, as propositions. `checkers.py::_RELATION_OPS`. -/
def Relation.Holds : Relation → Rat → Rat → Prop
  | .eq, a, b => a = b
  | .gt, a, b => b < a
  | .ge, a, b => b ≤ a
  | .lt, a, b => a < b
  | .le, a, b => a ≤ b

/-- `checkers.py::evaluate_predicate`. False if either side fails to evaluate. -/
def Predicate.Holds (p : Predicate) (e : Env) : Prop :=
  match p.left.eval e, p.right.eval e with
  | Option.some l, Option.some r => p.relation.Holds l r
  | _, _ => False

/- `checkers.py::evaluate_formula`. `and` on the empty list is `True` and `or` on the empty
list is `False`, matching Python's `all()`/`any()`. -/
mutual

def Formula.Holds (c : Claim) (e : Env) : Formula → Prop
  | .pred id =>
    match c.findPredicate id with
    | Option.some p => p.Holds e
    | Option.none => False
  | .and ops => Formula.HoldsAll c e ops
  | .or ops => Formula.HoldsAny c e ops
  | .not f => ¬ Formula.Holds c e f

def Formula.HoldsAll (c : Claim) (e : Env) : List Formula → Prop
  | [] => True
  | f :: fs => Formula.Holds c e f ∧ Formula.HoldsAll c e fs

def Formula.HoldsAny (c : Claim) (e : Env) : List Formula → Prop
  | [] => False
  | f :: fs => Formula.Holds c e f ∨ Formula.HoldsAny c e fs

end

/-- Membership in one interval axis, honouring the open/closed boundary flags.
Mirrors `checkers.py:134-135` exactly:
`lower_ok = value > lower or (lower_closed and value == lower)`. -/
def IntervalDomain.MemVal (i : IntervalDomain) (v : Rat) : Prop :=
  (if i.lowerClosed then i.lower ≤ v else i.lower < v) ∧
  (if i.upperClosed then v ≤ i.upper else v < i.upper)

/-- `AssignsBox e comps e'` holds when `e'` extends `e` by giving every component variable a
value inside its own interval, in component order. -/
def AssignsBox : Env → List IntervalDomain → Env → Prop
  | e, [], e' => e' = e
  | e, comp :: rest, e' =>
    ∃ v, comp.MemVal v ∧ AssignsBox (e.extend comp.variableId v) rest e'

/--
The quantifier prefix, interpreted in order.

This is the definition that makes the 2026-08-17 checker bug unstatable: a `forall` block
becomes a genuine `∀`, so no single witness can discharge it.
-/
def Claim.SemFrom (c : Claim) : List QuantifierBlock → Env → Prop
  | [], e => Formula.Holds c e c.formula
  | b :: rest, e =>
    match c.findDomain b.domainId with
    | Option.none => False
    | Option.some d =>
      match b.kind with
      | .forAll => ∀ e', AssignsBox e d.components e' → c.SemFrom rest e'
      | .exists_ => ∃ e', AssignsBox e d.components e' ∧ c.SemFrom rest e'

/-- What a RoboCert claim asserts. -/
def Claim.Semantics (c : Claim) : Prop := c.SemFrom c.quantifiers Env.empty

end RoboCert
