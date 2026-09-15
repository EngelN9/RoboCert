/-
# RoboCert claim syntax

A direct transcription of the immutable claim objects in `src/robocert/specification.py`.
Field names are camelCase here and snake_case there; the correspondence is 1:1 and is the
first thing a reviewer should check.

Nothing in this file is a statement about a physical robot. See `formal/README.md`.
-/

namespace RoboCert

/-- `specification.py::Unit` -/
inductive Unit where
  | dimensionless | metre | squareMetre | radian | second
  deriving DecidableEq, Repr

/-- `specification.py::QuantifierKind` -/
inductive QuantifierKind where
  | forAll | exists_
  deriving DecidableEq, Repr

/-- `specification.py::Relation` -/
inductive Relation where
  | eq | gt | ge | lt | le
  deriving DecidableEq, Repr

/-- `specification.py::UncertaintySemantics` -/
inductive UncertaintySemantics where
  | none | adjustable | staticRobust | policy
  deriving DecidableEq, Repr

/-- `specification.py::GeometrySemantics` -/
inductive GeometrySemantics where
  | exact | outerConservative | innerConservative | nonCertifiedApproximation
  deriving DecidableEq, Repr

/-- `specification.py::Variable` -/
structure Variable where
  variableId : String
  unit : Unit
  deriving DecidableEq, Repr

/--
`specification.py::IntervalDomain`.

NOTE the Python constructor additionally enforces `lower < upper` STRICTLY
(`specification.py:200`). That invariant is carried in `Wellformed.lean`, not in this
structure, so that the syntax type can also represent claims the runtime would reject —
which is what lets us state and check the drift explicitly.
-/
structure IntervalDomain where
  domainId : String
  variableId : String
  lower : Rat
  upper : Rat
  unit : Unit
  lowerClosed : Bool
  upperClosed : Bool
  deriving DecidableEq, Repr

/-- `specification.py::BoxDomain` -/
structure BoxDomain where
  domainId : String
  components : List IntervalDomain
  deriving DecidableEq, Repr

/-- `specification.py::QuantifierBlock` -/
structure QuantifierBlock where
  kind : QuantifierKind
  variableIds : List String
  domainId : String
  deriving DecidableEq, Repr

/-- `specification.py::MonomialPower`. Python enforces `exponent >= 1`. -/
structure MonomialPower where
  variableId : String
  exponent : Nat
  deriving DecidableEq, Repr

/-- `specification.py::Term`. Python enforces a nonzero coefficient and sorted, distinct powers. -/
structure Term where
  coefficient : Rat
  powers : List MonomialPower
  deriving DecidableEq, Repr

/-- `specification.py::Polynomial`. Python stores terms in canonical combined, sorted form. -/
structure Polynomial where
  terms : List Term
  deriving DecidableEq, Repr

/-- `specification.py::Predicate` -/
structure Predicate where
  predicateId : String
  left : Polynomial
  relation : Relation
  right : Polynomial
  deriving DecidableEq, Repr

/--
`specification.py::Formula`.

Python represents this as a single record with a `kind` tag, an optional `predicate_id`, and
an `operands` tuple, with the well-formedness of each shape enforced in `__post_init__`
(`specification.py:483-497`). In particular Python's `not` carries a one-element operand
list; here it carries a single `Formula`, so that invariant becomes structural rather than
checked. That is a deliberate, documented divergence — see `formal/README.md`.

`and`/`or` stay n-ary to match Python exactly.
-/
inductive Formula where
  | pred (predicateId : String)
  | and (operands : List Formula)
  | or (operands : List Formula)
  | not (operand : Formula)
  deriving Repr

/-- `specification.py::Assumption`. Carried for fidelity; no semantic role in Phase 0.5a. -/
structure Assumption where
  assumptionId : String
  statement : String
  category : String
  deriving DecidableEq, Repr

/-- `specification.py::Margin`. Carried for fidelity; no semantic role in Phase 0.5a. -/
structure Margin where
  marginId : String
  metric : String
  relation : Relation
  bound : Rat
  unit : Unit
  deriving DecidableEq, Repr

/-- `specification.py::ProvenanceEntry`. Carried for fidelity; no semantic role in Phase 0.5a. -/
structure ProvenanceEntry where
  sourceId : String
  artifactHash : String
  description : String
  deriving DecidableEq, Repr

/-- `specification.py::Claim` -/
structure Claim where
  claimId : String
  variables : List Variable
  domains : List BoxDomain
  quantifiers : List QuantifierBlock
  predicates : List Predicate
  formula : Formula
  assumptions : List Assumption
  margins : List Margin
  uncertaintySemantics : UncertaintySemantics
  geometrySemantics : GeometrySemantics
  provenance : List ProvenanceEntry

/-- Look up a box domain by id. `none` is treated as fail-closed downstream. -/
def Claim.findDomain (c : Claim) (id : String) : Option BoxDomain :=
  c.domains.find? (fun d => d.domainId == id)

/-- Look up a predicate by id. `none` is treated as fail-closed downstream. -/
def Claim.findPredicate (c : Claim) (id : String) : Option Predicate :=
  c.predicates.find? (fun p => p.predicateId == id)

end RoboCert
