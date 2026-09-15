# A possible route past A-003, 2026-09-11

**E0 exploratory note.** This records a lead, not a claim and not an argument. Nothing here
may be cited outside `research/notes/`, and it enters `research/CLAIMS.md` only if someone
writes the argument and files it at `E0` there.

## The gap

`research/ATTEMPTS.md` A-003 records why a MuJoCo lead cannot yet be refuted against the
planar-2R model. `robocert.refutation.refute` needs a purely universal claim. The only
planar-2R encoding RoboCert builds (`kinematics2r.build_planar2r_claim`, RC-002) is
existential. Its second-segment clearance conjunct Ψ⁽²⁾ reads the link's endpoint off the
fixed target constant, and P2 Proposition 9.4(3) and Remark 9.5 show that Ψ⁽²⁾ is unsound
once detached from the FK equalities. A-003's `repairable_under` names the repair: a
clearance encoding that takes the second link's endpoint from `(t1, t2)` itself.

## The lead

RC-005's encoding already has that shape, for a different purpose. Its two point-to-segment
case splits use the actual rationalized points `p0`, `p1(t)`, `p2(t)`, not the target
constant (`research/CLAIMS.md` RC-005 `statement:`; proof, Section 7, equation (7.1)).
Equation (7.1) states each clearance conjunct as its own pointwise equivalence, "for every
finite real `(t1,t2)`". If that holds as stated, the clearance part of RC-005's encoding
does not lean on an FK equality the way RC-002's does. That would make it a candidate
building block for

```text
forall (t1, t2) in B:  dist(C, [p0, p1(t)]) >= R  and  dist(C, [p1(t), p2(t)]) >= R
```

and a claim of that shape is one `refute` can act on.

## Why this is only a lead

- RC-005 is `E0`. Its argument has no owner read and no referee. Building on it now would
  cap anything derived at `E0`, and would invert the order the ledger's monotonicity rule
  exists to protect.
- The 2026-08-28 adversary runs (`research/notes/2026-08-28-rc005-adversary-search.md`)
  found the generic `Seg` construct unsound at `Q_ = 0`: branch III fires vacuously. RC-005
  avoids that point only through `L1, L2 != 0`. A universal claim over a box would need the
  `Q_ > 0` side condition on `Seg` itself, as those runs recommend, not inherited from a
  surrounding conjunction. That is the same dependence on the enclosing formula that sank
  A-001 and A-003.
- RC-005's `statement:` does not say whether `t` ranges over `R` or `Q` (see its
  `fidelity:` field). A universal claim cannot leave that open. Refuting it at one rational
  point is sound under either reading, but asserting it is not.
- Pointwise equivalence of one conjunct may still depend on the others in ways (7.1) does not
  show. Reading the proof of each equivalence for exactly that is the first thing to do, and
  it has not been done.

## When to pick it up

After RC-005 has an owner read, not before. At that point the first concrete step is to
answer, in writing, whether each of RC-005's clearance equivalences holds with the pose-
tolerance and singularity conjuncts removed. If one does not, log it as an attempt. It would
likely be a third route failing at a closely related requirement: a clearance conjunct that
controls the actual link only inside its enclosing formula. Three such failures is the point
at which `research/OBSTRUCTIONS.md` asks for a candidate obstruction to be drafted and
attacked.
