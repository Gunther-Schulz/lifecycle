# Drift-trigger probe, TREATMENT arm — standing directive (2026-09-20)

Operator GO 2026-09-20 ("as you recommend", answering the numbered round
at the driving desk). Design and grading semantics:
`docs/audits/2026-09-20-direction-drift-trigger-probe-design.md` — this
directive operationalizes its TREATMENT paragraph and adds nothing to it.

## Who delivers what (the assumed-delivery walk, stated at birth)

- **WRITER of the demand into a session:** the desk composing a brief or
  desk-kickoff for a session that will work in a GOVERNED repo (one
  carrying `.claude/lifecycle.json` and an investigation record) pastes
  the demand block below VERBATIM into that brief. During the trial the
  composing desks are lifecycle-d9 and any peer desk it kicks off; the
  kickoff message for a peer desk carries this directive's path.
- **ARTIFACT in the treated session:** the goal-check line in the reply
  at each seam — a seam passed without one is visible by its absence.
- **GRADER:** the driving desk, at the treated session's close, appends
  ONE row to `docs/audits/drift-treatment-log.tsv` (header already
  committed; the desk is the writer, the row is the record).
- **CONSUMER of the result:** the O6 arc's slot-admission decision — the
  goal-question SLOT is admitted or declined on this arm's outcome, per
  the design doc's FIRE/QUIET/COULD-NOT-VERIFY section, graded against
  INDEPENDENTLY ESTABLISHED drift episodes (operator corrections landing,
  or course-corrections lines recording the pre-change action as wrong).
- **WINDOW:** 5 treated sessions, or 4 weeks, whichever first; too few
  established drift episodes in the window is COULD NOT VERIFY with the
  episode count, never either verdict.

## The demand block (pasted verbatim into treated briefs)

```
GOAL-CHECK DEMAND (drift-probe treatment arm, directive
docs/directives/2026-09-20-drift-treatment-arm-directive.md):
at each seam — a decision round opened, a wave authorized, the
investigation record updated — re-read the investigation record's GOAL
slot and write ONE line in the reply:
  goal-check: <the goal, restated in one line> — served by <how the
  current move serves it, one line>
If the restatement and the in-flight action contradict, say so in the
same line and re-aim before the next tool call. The line is the
artifact: a seam passed without one is a skipped demand, visible in
the reply.
```

## Log row semantics (one row per treated session, desk-graded)

`seams` = seam events in the session per the definition above;
`checks_written` = goal-check lines actually present; `catches` = checks
whose restatement contradicted the in-flight action AND the course
changed without operator intervention; `wrong_restatements` = rider 1's
class, never pooled with uncorrected-but-correct; `operator_interventions`
= operator drift-catches in the same session (the second row of the
design doc's outcome table).
