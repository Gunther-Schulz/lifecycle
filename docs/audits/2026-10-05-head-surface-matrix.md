# Which unprompted surface names an item whose state changed — the matrix

**2026-10-05, lifecycle desk, commissioned by the wan2gp desk's gap-sweep
handoff** (`docs/directives/2026-10-05-lifecycle-gap-sweep-handoff.md` in the
wan2gp repo). Data: `2026-10-05-head-surface-matrix.tsv`, beside this file.
**Measured at `bbf6ef0`** — the head pass with lc-313 in it and before the two
repairs this measurement produced. It is a record of that state and is not
re-run when the code moves; the newer audit cites this one.

## The question

A session reads one thing without being asked: the session-start pass. An
item whose state has changed so that somebody now owes an act — is it NAMED
there?

## What "unprompted" is

Read from the hook (dotfiles `claude/hooks/session-scan.py`), not assumed:
it runs FIVE verbs — `item check`, `kind list --digest`, `kind list
--structure`, `item ready --head`, `item ratio` — and the status bar runs
`item statusline`. `lane list`, `arc status`, `audit`, `kind moments` and
`ledger check` are never run unprompted.

## Method

- The tree at `bbf6ef0`, exported with `git archive` and run from there.
- One fresh scratch git repo per cell, built by the tool's own fixture class
  (`refusals._Repo`); supporting state — a closed target, a ledger answer —
  written through the tool's verbs.
- 4 open grades (NEW, READY, PARKED, STANDBY) x 18 blocker states = 72
  cells. Every cell also holds a READY, unblocked bystander as the head's
  positive control: named in 72 of 72.
- "Names the item" is a word-boundary match on the subject's id in the
  surface's output. A surface that prints a COUNT covering the item and not
  its id is "no".
- Tool state (`XDG_STATE_HOME`, `XDG_CONFIG_HOME`) pointed into scratch for
  every run, so the real fire log took no line.

## Columns

`next_act_owed_by` is this desk's GRADING, read off the per-item verdict
text (`item ready <id>`); everything else is observed. Each surface has two
columns: its exit code and whether its output names the item.

## What could not be exercised

- `item ratio` and `audit` answered COULD NOT VERIFY (exit 3) on every
  scratch repo: no flow and no history. Their columns are in the file and
  mean only that.
- The closed grades are not cells of this kind. Through `item close` the
  body leaves the carrier, so no surface can name it. Ten door runs and two
  hand-planted in-carrier closed grades were exercised instead; their
  results are in the commit that repaired the head pass.

## Findings at `bbf6ef0`

Cells where the desk owes an act because something CHANGED, and no
unprompted surface names the item — 6 cells:

| blocker state | grades | per-item verdict |
|---|---|---|
| decision ANSWERED by the ledger | NEW, PARKED, STANDBY | UNBLOCKED, re-grade owed |
| item-id blocker, target now DONE | NEW, PARKED, STANDBY | UNBLOCKED, re-grade owed |

A third family is owed and unnamed without anything having changed: a
migration re-grade (3 cells). The driving desk ruled a count line, no
per-item lines.

Named already, by `item check` and not by the head: a DROPPED target, a
target in no home, a cycle, a chain to an unclearable member, `evidence
false`, an untyped blocker. One finding, one home; the head does not
restate them.

On this repo's own carrier the same day: 9 items in the two unnamed
families (8 answered decisions, 1 target DONE).
