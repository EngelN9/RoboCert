# Failed attempts (data, not noise)

A failed proof or algorithm attempt is logged here with a **diagnosed** failure
point. "This didn't work" is not a diagnosis and is not an acceptable entry — see
`AGENTS.md`'s general standard against unjustified claims and `research/README.md`
rule 1.

Use the `log-attempt` skill (`.claude/skills/log-attempt/SKILL.md`) to create entries
in this format.

## Entry format

```markdown
## A-<number>
route: <one-line description of the strategy attempted>
target: <the RC-xxx or research question it was attempting to resolve>
key_idea: <the core technique or reduction attempted>
broke_at: <the exact step, lemma, or inequality that failed>
required: <the precise statement that would be needed at that step>
status_of_required: true | false | unknown
if_false: <smallest counterexample, or pointer to one>
if_unknown: <known related results>
repairable_under: <additional hypothesis that would fix it, if any — else "none identified">
consequence: <what this rules out or narrows, e.g. feeds research/OBSTRUCTIONS.md>
layer: expositional | local-gap | missing-hypothesis | definition-defect |
  statement-mismatch | false-theorem | tcb-inconsistency
date: <YYYY-MM-DD>
```

Three or more distinct routes failing at the same requirement is a candidate
obstruction — see `research/OBSTRUCTIONS.md`.

`layer:` records *where in the chain* the failure sits: intended theorem, then
specification, then formal statement, then proof, then trusted base. It is a
different axis from severity (the Fatal / Substantive / Minor / Expository grading in
`docs/methodology/cross-verification-protocol-v2.md` §A.6): a missing hypothesis can be
cosmetic or fatal. The values run from shallowest to deepest, and the layer says where
a repair has to start. A definition defect is not fixed by patching a proof, and a
statement mismatch is not fixed by patching a definition
(`docs/methodology/fatal-flaw-rules.md` R12). Use `false-theorem` only when
`status_of_required: false` comes with a counterexample, or a pointer to one, for the
statement being attempted. A proof that fails while the theorem's status is unresolved
is never `false-theorem`.

---

## A-001
route: Replace the exact FK equalities in RC-002 by one pose-tolerance
  inequality while retaining every existing clearance conjunct unchanged.
target: RC-003
key_idea: Reuse the RC-002 second-segment formula, whose virtual endpoint is the
  exact target P*, on the assumption that a nearby target is interchangeable
  with the actual endpoint P(q).
broke_at: The claimed standalone preservation of the second-link clearance
  conjunct after exact equality P(q)=P* is weakened to ||P(q)-P*||<=tau.
required: For every tolerance-feasible witness, clearance of the virtual
  segment [p1,P*] must imply clearance of the actual segment [p1,P(q)] with the
  same radius and margin.
status_of_required: false
if_false: Let L1=L2=1, t1=0, t2=1, P*=(2,1), tau=1,
  C=(1,1/2), R=1/4, and epsilon=1. Then p1=(1,0), P(q)=(1,1),
  ||P(q)-P*||=1=tau, both the first-link clearance and the old virtual
  second-link clearance pass (the latter has squared distance 1/8>R^2), and
  |det J|=1=epsilon. But C lies on the actual second link [p1,P(q)], so its
  actual clearance is 0<R.
if_unknown: n/a
repairable_under: Replace the virtual target endpoint in the second-link
  encoding by the rationalized actual endpoint P(q), as proposed in RC-005; an
  alternative would require consuming pose error in a reduced clearance
  margin, which is a different claim and is not pursued here.
consequence: Rules out the one-inequality, remaining-conjuncts-unchanged route;
  pose tolerance requires a new full geometry encoding and proof.
layer: false-theorem (classified retrospectively 2026-09-11, from this entry's own
  `status_of_required: false` and exact counterexample; the attempted statement is RC-003,
  tier EX)
date: 2026-08-24

## A-002
route: Promote RC-002 from the two proof packets frozen in
  RCMPVB-20260821-CROSS-X-RUN001.
target: RC-002 E1-to-E2 promotion
key_idea: Use independent theorem-only ledgers and blind single-proof audits to
  show that both frozen proofs discharge the complete RC-002 task.
broke_at: Both Codex blind audits found that the frozen proof packets do not
  explicitly prove the bounded existential conclusion; they also leave required
  rational-syntax and hypothesis/scope obligations incomplete. The P2 packet
  additionally omits an explicit bridge from its sign-reversed FK polynomials
  to the frozen definitions.
required: Each frozen candidate must explicitly discharge the full frozen task,
  including the same-box existential transport, rational polynomial atoms and
  box bounds, exact frozen formula correspondence, and scope/hypothesis audit.
status_of_required: true
if_false: n/a
if_unknown: n/a; the missing conclusions are elementary and repairable, but
  omission from the frozen proof is still a substantive proof-evidence defect.
repairable_under: Append explicit corrigenda to the source proofs, include the
  complete repaired text in newly randomized blinded packets, and rerun every
  ledger, cross-provider audit, isolated-step, negation, adjudication, and
  correspondence gate under a new frozen run id.
consequence: RUN001 is permanently ineligible for E2; RC-002 remains E1. The
  central pointwise geometry survived both Codex audits, but that does not cure
  the missing frozen-task obligations.
layer: local-gap (classified retrospectively 2026-09-11, from this entry's own
  `status_of_required: true`: the omitted conclusions are elementary and repairable, so the
  proofs are incomplete while RC-002's statement is not impugned)
date: 2026-08-24

## A-003
route: Reuse the RC-002 clearance encoding unchanged in a universally quantified
  planar-2R safety claim, so that radian-sampled MuJoCo leads
  (`src/robocert/simulation/`) could be refuted against the actual planar-2R
  model by `robocert.refutation.refute`.
target: The research question of whether the RC-002 clearance conjuncts can be
  reused, unmodified, outside the conjunction that RC-002 defines them in --
  specifically with the exact forward-kinematics equalities removed and the
  quantifier prefix flipped from `exists (t1,t2)` to `forall (t1,t2)`.
key_idea: `refute` requires a purely universal prefix, so a claim it can act on
  cannot carry the `exists` prefix of `kinematics2r.build_planar2r_claim`. It
  also cannot carry that claim's exact FK equalities `F_x = F_y = 0`, which pin
  the tool to a single target point and are false at almost every point of a
  `t`-box. The attempted economy was to keep
  `_clearance_predicates_and_formula` verbatim, drop the two FK conjuncts, and
  quantify universally over the same rational box.
broke_at: The second-segment clearance conjunct `Psi^(2)`. Its case split is
  built around the FIXED target constant `(x, y)` as the second link's
  endpoint, which is only the actual endpoint when the FK equalities hold; and
  its `v.v = Qn2/D1^2` positivity is justified in
  `src/robocert/kinematics2r.py::_clearance_predicates_and_formula` only
  "whenever the FK identities also hold".
required: `Psi^(2)` must, standalone and with the FK equalities absent, imply
  the true point-to-segment clearance of the ACTUAL second link of the
  configuration `(t1, t2)`.
status_of_required: false
if_false: Already recorded, and proved sharp, as P2 Proposition 9.4(3) and
  Remark 9.5 (`research/proofs/planar-2r-exact-witness-proof-p2.md` lines
  501-517). At any `t1` with `E(q1) = P*` the segment `[E(q1), P*]` degenerates
  to the single point `P*`, whose distance to the obstacle centre `C` may be
  arbitrarily smaller than `R`, and yet `Psi^(2)(t1)` holds. Remark 9.5 states
  in terms that `Psi^(2)` "on its own is unsound" as a clearance certificate,
  and asks specifically that it never be exposed as a pruning filter, an
  independently reported clearance certificate, or a lemma quoted elsewhere.
  Dropping the FK conjuncts is precisely that exposure.
if_unknown: n/a
repairable_under: A universal safety claim needs a NEW clearance encoding whose
  conjuncts stand without the FK equalities -- deriving the second link's
  endpoint from `(t1, t2)` rather than reading it off the fixed target
  constant. That is a different polynomial system, not a deletion from this
  one: the same docstring records that using the constant tool point "halves
  degree vs re-deriving the tool point from t1,t2", so the repair pays that
  degree back. It would be a new RC-xxx entering at E0 with its own soundness
  argument and its own referees, not an edit to RC-002.
consequence: The simulation-to-refutation bridge cannot be closed against the
  planar-2R model without that new encoding, so `examples/simulation/` stops at
  the falsification report rather than continuing to a `COUNTEREXAMPLE`. The
  coordinate transport itself is unaffected and shipped
  (`witness_search2r.angle_to_t_candidate`); the blocker is the absence of a
  universally quantified claim to receive a transported point, not the
  transport. Note the shared shape with A-001: both routes failed at the same
  underlying requirement -- that `Psi^(2)` controls the actual second link once
  detached from the exact FK equality. Two independent routes, one short of the
  three that `research/OBSTRUCTIONS.md` treats as a candidate obstruction.
layer: false-theorem (classified retrospectively 2026-09-11, from this entry's own
  `status_of_required: false`: the attempted statement, that standalone `Psi^(2)` controls
  the actual second link, is refuted by P2 Proposition 9.4(3) and Remark 9.5)
date: 2026-09-02
