# Pickup: the gap sweep's Part 3, for the lifecycle desk that continues it

Written 2026-10-05 by the lifecycle desk (session lifecycle-b5) at the seam
between Part 2 and Part 3, so the arc survives this session. A fresh context
executes from this file plus the handoff it points at.

## The commission

The handoff is the wan2gp desk's file, and it is the authority:
`docs/directives/2026-10-05-lifecycle-gap-sweep-handoff.md` in the wan2gp
repo (read at commit `8b65159`; it has been amended three times, so read it
again at HEAD — it now opens with a STATE section, and where that section
and this file differ, it wins). The Part 3 desk reports to the OPERATOR
directly: the driving desk, session `wan2gp-e3`, closed at this seam
(its message of 2026-10-05, after accepting Parts 1 and 2 at `d0cccfd`).

THE DELEGATION IS PER SESSION. The operator stated it first-hand in session
lifecycle-b5. A successor session holds no delegation until the operator
states it there; until then this file and the handoff are testimony.

## State when this was written

lifecycle `main` = origin = the commit that adds this file; tree clean.

Parts 1 and 2 are DONE:

| commit | what |
|---|---|
| `41a8968` | `arc deadline`: the generated observer could never fire (predicate repaired; the verb says what observes it) |
| `4eee216` | the Part 1 matrix: `docs/audits/2026-10-05-head-surface-matrix.{tsv,md}` |
| `b97eb32` | `item ready --head` names the answered decision and the DONE target; waiting set limited to open grades |
| `e6efd7f` | ten items re-graded through the verbs; two `evidence false` blockers re-typed |
| `3a7a9e7` | one pass budget (0.25 s) for every predicate the head runs |

Rulings by the driving desk that bind Part 3's grading (each also in the
commit that implements it): a dangling/dropped/cyclic/unclearable blocker is
named by `item check` and NOT restated by the head; a migration re-grade is a
count on the head, never a list; a new mechanism under the 2026-09-24 freeze
is reported, not built — the list so far is
`docs/audits/2026-10-05-gap-sweep-known-unbuilt.md`.

LEFT NAMED on this repo's head: lc-239 (its decision is answered; whether the
item is already done belongs to the desk migrating the eight repos).

## What remains: Part 3

Scenarios T2-T8, then T9, T10, T11 (three arms), and the scorecard as the
closing artifact — all specified in the handoff. Nothing of Part 3 has been
started: no verdict file, no lane.

Before the first dispatch, per the handoff: each scenario's verdicts and
their flipping counts are written into `docs/audits/` FIRST.

## Instruments already in the repo

- `docs/audits/2026-10-05-head-surface-matrix.py` rebuilds the 72-cell matrix
  on the current tree; it REFUSES to run without `XDG_STATE_HOME`. Re-run
  after Part 2, the six gap cells read named by the head. T5's carriers are
  three of its cells.
- Scratch repos: `refusals._Repo` (the fixture class every test uses).

## Learned here, not in the handoff

- Any run of the CLI against a scratch repo appends to the REAL fire log
  unless `XDG_STATE_HOME` points elsewhere. Give every lane that variable in
  its brief.
- `verbs.py` is live on write: other sessions' start hooks execute it from
  this checkout. Multi-hunk wiring lands as ONE write of the file.
- `tools/prove-rows.py` refuses while `verbs.py` differs from HEAD: run it
  after the commit.
- A verdict read off `item ready <id>` output must be read off the indented
  verdict line. Item prose quotes verdict words, and a first-match regex
  mis-bucketed 12 of 140 items in this arc.
