# Specialization lattice

Nodes are strengthenings of a claim family's hypotheses (fix a parameter, restrict
the class, drop uncertainty, bound dimension); edges are implications; each node
carries a status. The top-level lattice mirrors `ROADMAP.md`'s Benchmark Ladder:

```
C_general (industrial CAD workstation, Phase 7)
  ⊃ C_continuous-path (Phase 8)
  ⊃ C_robust-6-7dof (Phase 5, Level 5)
  ⊃ C_6dof-local (Phase 6, Level 4)
  ⊃ C_spatial-3dof (Level 3)
  ⊃ C_3R-planar-quantified (Phase 2, Level 2)
  ⊃ C_2R-planar-exact (Phase 1, Level 1)
```

A special case is logged here only if it passes the three meaningfulness tests
before being accepted (not decorative):

1. **Not already known.** Check `research/literature/` first.
2. **Retains the difficulty.** State explicitly which feature of the general problem
   the special case is meant to preserve, and confirm it still has it.
3. **The dependence on the extra hypothesis is understood.** After proving the
   special case, identify every step that uses the extra hypothesis and what it
   would take to drop it — this feeds `research/OBSTRUCTIONS.md` directly.

Watch for **generalization theatre**: a special-case proof presented as "the general
argument modulo technicalities," where the technicalities are the whole problem.
Force the question explicitly for every extra hypothesis: convenience, or
load-bearing?

## Entry format (one file per node, or a section per node in a family file)

```markdown
## <node id>, e.g. C_2R-planar-exact.nominal
parent: <id of the node this specializes, or "none">
extra_hypothesis: <what's added relative to the parent>
status: open | E1 | E2 | E3 | refuted
test_1_not_known: <result of the literature check>
test_2_retains_difficulty: <which feature of the general problem this keeps>
test_3_hypothesis_dependence: <map of every proof step that uses the extra hypothesis>
claims: [RC-xxx, ...]
```

---

See `2r-planar.md` for the first populated node, matching the Phase-1 pilot
(`ROADMAP.md` §32 / `research/CLAIMS.md` RC-001).
