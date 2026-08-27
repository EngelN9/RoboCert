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
date: <YYYY-MM-DD>
```

Three or more distinct routes failing at the same requirement is a candidate
obstruction — see `research/OBSTRUCTIONS.md`.

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
date: 2026-08-24
