/-
# Soundness of the exact-witness checker
-/
import RoboCert.Checker
import RoboCert.Wellformed

namespace RoboCert

theorem Relation.decide_iff (r : Relation) (a b : Rat) :
    r.decide a b = true ↔ r.Holds a b := by
  cases r <;> simp [Relation.decide, Relation.Holds]

theorem Predicate.decideP_iff (p : Predicate) (e : Env) :
    p.decideP e = true ↔ p.Holds e := by
  unfold Predicate.decideP Predicate.Holds
  cases hl : p.left.eval e <;> cases hr : p.right.eval e <;>
    simp [Relation.decide_iff]

/- Adequacy of the Bool evaluator against the Prop semantics.

Stated as an iff, not an implication: `Formula.not` is interpreted by negation, so the
`.not` case of the forward direction needs the backward direction at the operand. -/
mutual

theorem Formula.decideF_iff (c : Claim) (e : Env) :
    ∀ f : Formula, Formula.decideF c e f = true ↔ Formula.Holds c e f
  | .pred id => by
    unfold Formula.decideF Formula.Holds
    cases hp : c.findPredicate id <;> simp [Predicate.decideP_iff]
  | .and ops => by
    unfold Formula.decideF Formula.Holds
    exact Formula.decideAll_iff c e ops
  | .or ops => by
    unfold Formula.decideF Formula.Holds
    exact Formula.decideAny_iff c e ops
  | .not f => by
    unfold Formula.decideF Formula.Holds
    have h := Formula.decideF_iff c e f
    constructor
    · intro hnot hh
      rw [h.mpr hh] at hnot
      simp at hnot
    · intro hnh
      cases hd : Formula.decideF c e f
      · simp
      · exact absurd (h.mp hd) hnh

theorem Formula.decideAll_iff (c : Claim) (e : Env) :
    ∀ fs : List Formula, Formula.decideAll c e fs = true ↔ Formula.HoldsAll c e fs
  | [] => by simp [Formula.decideAll, Formula.HoldsAll]
  | f :: fs => by
    simp [Formula.decideAll, Formula.HoldsAll, Formula.decideF_iff c e f,
      Formula.decideAll_iff c e fs]

theorem Formula.decideAny_iff (c : Claim) (e : Env) :
    ∀ fs : List Formula, Formula.decideAny c e fs = true ↔ Formula.HoldsAny c e fs
  | [] => by simp [Formula.decideAny, Formula.HoldsAny]
  | f :: fs => by
    simp [Formula.decideAny, Formula.HoldsAny, Formula.decideF_iff c e f,
      Formula.decideAny_iff c e fs]

end

/- ## Congruence: evaluation depends only on the variables actually mentioned.

This is what lets the witness environment (which may bind extra variables) be replaced by the
environment the quantifier prefix builds (which binds exactly the quantified ones). -/

theorem evalPowers_congr (e w : Env) : ∀ pws : List MonomialPower,
    (∀ pw ∈ pws, e pw.variableId = w pw.variableId) → evalPowers e pws = evalPowers w pws
  | [], _ => rfl
  | pw :: rest, h => by
    have hpw : e pw.variableId = w pw.variableId := h pw (by simp)
    have hrest := evalPowers_congr e w rest (fun q hq => h q (by simp [hq]))
    simp [evalPowers, hpw, hrest]

theorem Term.eval_congr (t : Term) (e w : Env)
    (h : ∀ pw ∈ t.powers, e pw.variableId = w pw.variableId) : t.eval e = t.eval w := by
  simp [Term.eval, evalPowers_congr e w t.powers h]

theorem evalTerms_congr (e w : Env) : ∀ ts : List Term,
    (∀ t ∈ ts, ∀ pw ∈ t.powers, e pw.variableId = w pw.variableId) →
      evalTerms e ts = evalTerms w ts
  | [], _ => rfl
  | t :: rest, h => by
    have ht := Term.eval_congr t e w (h t (by simp))
    have hrest := evalTerms_congr e w rest (fun u hu => h u (by simp [hu]))
    simp [evalTerms, ht, hrest]

theorem Polynomial.eval_congr (p : Polynomial) (e w : Env)
    (h : ∀ x, p.Mentions x → e x = w x) : p.eval e = p.eval w := by
  refine evalTerms_congr e w p.terms (fun t ht pw hpw => h pw.variableId ?_)
  exact ⟨t, ht, pw, hpw, rfl⟩

theorem Predicate.decideP_congr (pr : Predicate) (e w : Env)
    (h : ∀ x, pr.Mentions x → e x = w x) : pr.decideP e = pr.decideP w := by
  have hl := Polynomial.eval_congr pr.left e w (fun x hx => h x (Or.inl hx))
  have hr := Polynomial.eval_congr pr.right e w (fun x hx => h x (Or.inr hx))
  simp [Predicate.decideP, hl, hr]

mutual

theorem Formula.decideF_congr (c : Claim) (e w : Env) : ∀ f : Formula,
    (∀ x, Formula.Mentions c f x → e x = w x) →
      Formula.decideF c e f = Formula.decideF c w f
  | .pred id, h => by
    have h' : ∀ x, Formula.Mentions c (Formula.pred id) x → e x = w x := h
    unfold Formula.decideF
    cases hp : c.findPredicate id with
    | none => rfl
    | some pr =>
      refine Predicate.decideP_congr pr e w (fun x hx => h' x ?_)
      simp [Formula.Mentions, hp, hx]
  | .and ops, h => by
    unfold Formula.decideF
    exact Formula.decideAll_congr c e w ops h
  | .or ops, h => by
    unfold Formula.decideF
    exact Formula.decideAny_congr c e w ops h
  | .not f, h => by
    unfold Formula.decideF
    simp [Formula.decideF_congr c e w f h]

theorem Formula.decideAll_congr (c : Claim) (e w : Env) : ∀ fs : List Formula,
    (∀ x, Formula.MentionsAny c fs x → e x = w x) →
      Formula.decideAll c e fs = Formula.decideAll c w fs
  | [], _ => rfl
  | f :: fs, h => by
    have hf := Formula.decideF_congr c e w f (fun x hx => h x (Or.inl hx))
    have hrest := Formula.decideAll_congr c e w fs (fun x hx => h x (Or.inr hx))
    simp [Formula.decideAll, hf, hrest]

theorem Formula.decideAny_congr (c : Claim) (e w : Env) : ∀ fs : List Formula,
    (∀ x, Formula.MentionsAny c fs x → e x = w x) →
      Formula.decideAny c e fs = Formula.decideAny c w fs
  | [], _ => rfl
  | f :: fs, h => by
    have hf := Formula.decideF_congr c e w f (fun x hx => h x (Or.inl hx))
    have hrest := Formula.decideAny_congr c e w fs (fun x hx => h x (Or.inr hx))
    simp [Formula.decideAny, hf, hrest]

end

/- ## Building the environment the quantifier prefix demands, from the flat witness. -/

/-- Extend `e` with the witness's value for each component variable, in order. -/
def extendComps (w : Env) : Env → List IntervalDomain → Env
  | e, [] => e
  | e, comp :: rest =>
    match w comp.variableId with
    | Option.some v => extendComps w (e.extend comp.variableId v) rest
    | Option.none => extendComps w e rest

theorem IntervalDomain.memVal_of_memBool {i : IntervalDomain} {v : Rat}
    (h : i.memBool v = true) : i.MemVal v := by
  unfold IntervalDomain.memBool at h
  unfold IntervalDomain.MemVal
  cases hl : i.lowerClosed <;> cases hu : i.upperClosed <;>
    simp [hl, hu] at h ⊢ <;> exact h

/-- Variables untouched by `comps` keep their old value. -/
theorem extendComps_not_mem (w : Env) : ∀ (comps : List IntervalDomain) (e : Env) (x : String),
    (∀ comp ∈ comps, comp.variableId ≠ x) → extendComps w e comps x = e x
  | [], _, _, _ => rfl
  | comp :: rest, e, x, h => by
    have hne : comp.variableId ≠ x := h comp (by simp)
    have hrest : ∀ q ∈ rest, q.variableId ≠ x := fun q hq => h q (by simp [hq])
    cases hw : w comp.variableId with
    | none =>
      simp only [extendComps, hw]
      exact extendComps_not_mem w rest e x hrest
    | some v =>
      simp only [extendComps, hw]
      rw [extendComps_not_mem w rest _ x hrest]
      simp only [Env.extend]
      rw [if_neg hne.symm]

/-- Variables assigned by `comps` end up holding the witness's value. -/
theorem extendComps_mem (w : Env) : ∀ (comps : List IntervalDomain) (e : Env) (x : String),
    (∀ comp ∈ comps, (w comp.variableId).isSome = true) →
    (∃ comp ∈ comps, comp.variableId = x) →
    extendComps w e comps x = w x
  | [], _, _, _, hex => by simp at hex
  | comp :: rest, e, x, hsome, hex => by
    have hrestSome : ∀ q ∈ rest, (w q.variableId).isSome = true :=
      fun q hq => hsome q (by simp [hq])
    cases hw : w comp.variableId with
    | none =>
      have := hsome comp (by simp)
      rw [hw] at this
      simp at this
    | some v =>
      simp only [extendComps, hw]
      by_cases hin : ∃ q ∈ rest, q.variableId = x
      · exact extendComps_mem w rest _ x hrestSome hin
      · have hnot : ∀ q ∈ rest, q.variableId ≠ x := by
          intro q hq heq
          exact hin ⟨q, hq, heq⟩
        have hx : comp.variableId = x := by
          rcases hex with ⟨q, hq, hqx⟩
          rcases List.mem_cons.mp hq with h1 | h2
          · subst h1; exact hqx
          · exact absurd hqx (hnot q h2)
        rw [extendComps_not_mem w rest _ x hnot]
        rw [← hx, hw]
        simp [Env.extend]

theorem findDomain_of_blockWitnessOk {c : Claim} {w : Env} {b : QuantifierBlock}
    (h : blockWitnessOk c w b = true) :
    ∃ d, c.findDomain b.domainId = Option.some d ∧
      (d.components.all fun comp =>
        match w comp.variableId with
        | Option.none => false
        | Option.some v => comp.memBool v) = true := by
  unfold blockWitnessOk at h
  revert h
  cases hd : c.findDomain b.domainId with
  | none => intro h; simp at h
  | some d => intro h; exact ⟨d, rfl, h⟩

/-- A witness that lands in every component's interval induces an `AssignsBox` step. -/
theorem assignsBox_extendComps (w : Env) :
    ∀ (comps : List IntervalDomain) (e : Env),
    (comps.all fun comp =>
      match w comp.variableId with
      | Option.none => false
      | Option.some v => comp.memBool v) = true →
    AssignsBox e comps (extendComps w e comps)
  | [], _, _ => rfl
  | comp :: rest, e, h => by
    simp only [List.all_cons, Bool.and_eq_true] at h
    obtain ⟨hhead, htail⟩ := h
    cases hw : w comp.variableId with
    | none => rw [hw] at hhead; simp at hhead
    | some v =>
      rw [hw] at hhead
      refine ⟨v, IntervalDomain.memVal_of_memBool hhead, ?_⟩
      simp only [extendComps, hw]
      exact assignsBox_extendComps w rest _ htail

/- ## The main induction.

The invariant: for every variable the formula mentions, either `e` already agrees with the
witness, or some REMAINING block will bind it. At the end of the prefix no blocks remain, so
`e` agrees with the witness everywhere the formula looks -- which is exactly what congruence
needs. -/

theorem semFrom_of_witness (c : Claim) (w : Env)
    (hform : Formula.decideF c w c.formula = true) :
    ∀ (blocks : List QuantifierBlock) (e : Env),
    (∀ b ∈ blocks, b.kind = QuantifierKind.exists_) →
    (∀ b ∈ blocks, blockWitnessOk c w b = true) →
    (∀ x, Formula.Mentions c c.formula x → e x = w x ∨ BoundBy c blocks x) →
    c.SemFrom blocks e
  | [], e, _, _, hcov => by
    show Formula.Holds c e c.formula
    have hagree : ∀ x, Formula.Mentions c c.formula x → e x = w x := by
      intro x hx
      rcases hcov x hx with hv | hb
      · exact hv
      · obtain ⟨b, hb, _⟩ := hb
        simp at hb
    have hcongr := Formula.decideF_congr c e w c.formula hagree
    exact (Formula.decideF_iff c e c.formula).mp (by rw [hcongr]; exact hform)
  | b :: rest, e, hex, hok, hcov => by
    obtain ⟨d, hd, hcomps⟩ := findDomain_of_blockWitnessOk (hok b (by simp))
    have hkind : b.kind = QuantifierKind.exists_ := hex b (by simp)
    have hsome : ∀ comp ∈ d.components, (w comp.variableId).isSome = true := by
      intro comp hcomp
      have hc := (List.all_eq_true.mp hcomps) comp hcomp
      cases hwv : w comp.variableId with
      | none => rw [hwv] at hc; simp at hc
      | some v => simp
    simp only [Claim.SemFrom, hd, hkind]
    refine ⟨extendComps w e d.components,
      assignsBox_extendComps w d.components e hcomps, ?_⟩
    refine semFrom_of_witness c w hform rest _
      (fun q hq => hex q (by simp [hq]))
      (fun q hq => hok q (by simp [hq])) ?_
    intro x hx
    rcases hcov x hx with hv | hb
    · by_cases hin : ∃ comp ∈ d.components, comp.variableId = x
      · exact Or.inl (extendComps_mem w d.components e x hsome hin)
      · refine Or.inl ?_
        rw [extendComps_not_mem w d.components e x (fun q hq hqx => hin ⟨q, hq, hqx⟩)]
        exact hv
    · obtain ⟨b', hb', d', hd', comp, hcomp, hcx⟩ := hb
      rcases List.mem_cons.mp hb' with heq | hmem
      · subst heq
        rw [hd'] at hd
        injection hd with hdd
        exact Or.inl (extendComps_mem w d.components e x hsome ⟨comp, hdd ▸ hcomp, hcx⟩)
      · exact Or.inr ⟨b', hmem, d', hd', comp, hcomp, hcx⟩

/--
**Soundness of the exact-witness checker.**

If the checker accepts, the claim's semantics hold.

Scope, restated because the theorem alone does not carry it:
* `Claim.Semantics` quantifies over `Rat`, not `Real` (see `Semantics.lean`);
* this is a statement about `formal/RoboCert/Checker.lean`, NOT about
  `src/robocert/checkers.py`; that correspondence is tested, not proved;
* `hwf` is a consequence of Python's claim validation, asserted rather than derived
  (see `Wellformed.lean`);
* nothing here concerns a physical robot.
-/
theorem exactWitness_sound (c : Claim) (cert : Certificate)
    (hwf : c.FormulaVarsQuantified)
    (h : ExactWitnessChecker.check c cert = true) : c.Semantics := by
  unfold ExactWitnessChecker.check at h
  simp only [Bool.and_eq_true] at h
  obtain ⟨⟨⟨_, hex⟩, hok⟩, hform⟩ := h
  refine semFrom_of_witness c cert.witness hform c.quantifiers Env.empty ?_ ?_ ?_
  · intro b hb
    have := (List.all_eq_true.mp hex) b hb
    simpa using this
  · intro b hb
    exact (List.all_eq_true.mp hok) b hb
  · intro x hx
    exact Or.inr (hwf x hx)

end RoboCert
