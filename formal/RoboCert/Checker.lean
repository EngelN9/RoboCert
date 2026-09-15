/-
# The exact-witness checker, as an executable model

Mirrors `src/robocert/checkers.py::ExactWitnessChecker.check` (lines 95-149).

`Certificate` here carries only what the semantic question needs: the conclusion and the
parsed witness. Payload parsing (`checkers.py::_parse_witness`) and the metadata
cross-checks in `checking.py::_run_checker` are a BINDING concern, not a semantic one, and
are deferred to Phase 0.5b. See `formal/README.md`.
-/
import RoboCert.Semantics

namespace RoboCert

/-- `certificates.py::CertificateConclusion` -/
inductive Conclusion where
  | feasible | infeasible
  deriving DecidableEq, Repr

/-- A candidate certificate, reduced to its semantic content. -/
structure Certificate where
  conclusion : Conclusion
  witness : Env

/-- Decision procedure for the order relations. `checkers.py::_RELATION_OPS`. -/
def Relation.decide : Relation → Rat → Rat → Bool
  | .eq, a, b => a == b
  | .gt, a, b => b < a
  | .ge, a, b => b ≤ a
  | .lt, a, b => a < b
  | .le, a, b => a ≤ b

/-- `checkers.py::evaluate_predicate`. Fails closed when either side does not evaluate. -/
def Predicate.decideP (p : Predicate) (e : Env) : Bool :=
  match p.left.eval e, p.right.eval e with
  | Option.some l, Option.some r => p.relation.decide l r
  | _, _ => false

/- `checkers.py::evaluate_formula`, as a Bool. -/
mutual

def Formula.decideF (c : Claim) (e : Env) : Formula → Bool
  | .pred id =>
    match c.findPredicate id with
    | Option.some p => p.decideP e
    | Option.none => false
  | .and ops => Formula.decideAll c e ops
  | .or ops => Formula.decideAny c e ops
  | .not f => ! Formula.decideF c e f

def Formula.decideAll (c : Claim) (e : Env) : List Formula → Bool
  | [] => true
  | f :: fs => Formula.decideF c e f && Formula.decideAll c e fs

def Formula.decideAny (c : Claim) (e : Env) : List Formula → Bool
  | [] => false
  | f :: fs => Formula.decideF c e f || Formula.decideAny c e fs

end

/-- Interval membership as a Bool. `checkers.py:134-135`. -/
def IntervalDomain.memBool (i : IntervalDomain) (v : Rat) : Bool :=
  (if i.lowerClosed then i.lower ≤ v else i.lower < v) &&
  (if i.upperClosed then v ≤ i.upper else v < i.upper)

/-- Every component of this block's domain must be bound by the witness, in range.
`checkers.py:125-139`. Fails closed on a missing domain or a missing binding. -/
def blockWitnessOk (c : Claim) (w : Env) (b : QuantifierBlock) : Bool :=
  match c.findDomain b.domainId with
  | Option.none => false
  | Option.some d =>
    d.components.all fun comp =>
      match w comp.variableId with
      | Option.none => false
      | Option.some v => comp.memBool v

/--
`ExactWitnessChecker.check`.

The third conjunct is the guard added after the 2026-08-17 audit
(`research/CLAIMS.md` RC-002): a single witness point can only ever establish an existential
claim, so any non-`EXISTS` block is rejected rather than ignored. `Soundness.lean` shows why
that rejection is not optional.
-/
def ExactWitnessChecker.check (c : Claim) (cert : Certificate) : Bool :=
  (cert.conclusion == Conclusion.feasible) &&
  (c.quantifiers.all fun b => b.kind == QuantifierKind.exists_) &&
  (c.quantifiers.all (blockWitnessOk c cert.witness)) &&
  (Formula.decideF c cert.witness c.formula)

end RoboCert
