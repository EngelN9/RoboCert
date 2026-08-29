(*
  Planar-2R: the bounded-existential / interval-membership shape.

  Isabelle/HOL's assignment in this phase, per formal/README.md, is quantified
  semialgebraic claims and independent real quantifier-elimination cross-checking. This
  first file does NOT attempt real QE -- that is explicitly out of scope for Phase 0.5b
  (see the plan's "Explicit non-goals"). It cross-checks the one quantifier-handling step
  every planar-2R claim in this repository depends on: the transport from a pointwise
  equivalence to a bounded-existential one.

  That step is stated in prose in research/proofs/rc002-frozen-task-corrigendum-2026-08-24.md
  section C2 ("Explicit bounded existential transport"): given Phi(t) <-> Geo(t) for every
  t, and a box B, then (exists t in B. Phi t) <-> (exists t in B. Geo t). This file states
  and proves that transport generically, over an arbitrary pair of predicates and an
  arbitrary closed rational box, independently of Lean's formalization
  (formal/RoboCert/Semantics.lean's Claim.SemFrom does the analogous thing for the FULL
  quantifier prefix, not just a single EXISTS block; the two are complementary, not
  duplicates).

  This is a statement about a MODEL, not a physical robot. See formal/README.md.
*)

theory Planar2R
  imports Complex_Main
begin

text \<open>
  A closed rational box in the two half-angle coordinates \<open>t1\<close>, \<open>t2\<close>. Deliberately
  non-strict (\<open>a1 \<le> t1\<close>, not \<open>a1 < t1\<close>): RC-005 section 1 admits \<open>a_i \<le> b_i\<close>, including
  the degenerate single-point case \<open>a_i = b_i\<close>, which the current Python runtime's
  IntervalDomain (specification.py, enforcing \<open>lower < upper\<close> strictly) does not accept.
  That gap is recorded in formal/README.md ("Deliberate divergences"); this definition
  follows the mathematical claim, not the current runtime restriction.
\<close>

definition in_box :: "rat \<Rightarrow> rat \<Rightarrow> rat \<Rightarrow> rat \<Rightarrow> rat \<Rightarrow> rat \<Rightarrow> bool" where
  "in_box a1 b1 a2 b2 t1 t2 \<equiv> a1 \<le> t1 \<and> t1 \<le> b1 \<and> a2 \<le> t2 \<and> t2 \<le> b2"

text \<open>
  A degenerate (single-point) box is nonvacuous: it admits exactly its one point. This is
  the fact the RC-005 adversary run's "unavailable" finding needed and no artifact
  previously stated outright -- that the claim's domain genuinely includes \<open>a_i = b_i\<close>,
  not merely that nothing in the corrigendum's prose forbids it.
\<close>

lemma singleton_box_admits_its_point:
  "in_box a a b b a b"
  unfolding in_box_def by simp

text \<open>
  The bounded-existential transport, generic in the predicates \<open>Phi\<close> and \<open>Geo\<close> and in the
  box bounds. This is exactly corrigendum section C2's step (C2.1) to (C2.3), and the proof
  is the same one given there in prose: take the witness on one side, apply the pointwise
  equivalence at that witness, and it is a witness on the other side. \<open>blast\<close> finds exactly
  that argument automatically, which is itself informative: the corrigendum is correct in
  claiming "no compactness, nonemptiness, solver completeness, or witness construction is
  used in this logical transport" -- a proof search restricted to pure first-order logic
  (no arithmetic, no case split on the box being empty or not) suffices.
\<close>

lemma bounded_existential_transport:
  assumes pointwise: "\<And>t1 t2. Phi t1 t2 \<longleftrightarrow> Geo t1 t2"
  shows "(\<exists>t1 t2. in_box a1 b1 a2 b2 t1 t2 \<and> Phi t1 t2)
       \<longleftrightarrow> (\<exists>t1 t2. in_box a1 b1 a2 b2 t1 t2 \<and> Geo t1 t2)"
  using pointwise by blast

text \<open>
  Corollary, stated because it is the actual shape of RC-005's target theorem: an empty box
  (\<open>a1 > b1\<close> or \<open>a2 > b2\<close>) makes both existentials false regardless of \<open>Phi\<close>/\<open>Geo\<close>, so the
  hypothesis \<open>a_i \<le> b_i\<close> is not consumed by the transport itself -- confirming the
  corrigendum's C4 hypothesis-consumption audit, which states exactly this about \<open>a_i < b_i\<close>
  (there stated for the non-degenerate case; \<open>a_i \<le> b_i\<close> here is the weaker, RC-005-actual
  hypothesis, and the argument is identical).
\<close>

lemma empty_box_forces_false:
  assumes empty: "a1 > b1"
  shows "\<not> (\<exists>t1 t2. in_box a1 b1 a2 b2 t1 t2 \<and> Phi t1 t2)"
  using empty unfolding in_box_def by force

text \<open>
  Scope, restated. This file establishes two generic first-order-logic facts about closed
  rational boxes. It does NOT establish:
  \<^item> anything about the polynomial identities \<open>T\<close>, \<open>G\<close>, or the \<open>Seg\<close> construct -- those are
    formal/rocq's assignment;
  \<^item> real quantifier elimination in any form; no CAD/QE backend is implemented anywhere in
    this repository (see ROADMAP.md Phase 1 and this plan's "Explicit non-goals");
  \<^item> that \<open>src/robocert/specification.py\<close> or any checker implements this shape correctly --
    an implementation-correspondence obligation, open per RC-005 section 9;
  \<^item> anything about a physical robot.

  RC-005 remains at tier E0 in research/CLAIMS.md. Nothing in this file promotes it.
\<close>

end
