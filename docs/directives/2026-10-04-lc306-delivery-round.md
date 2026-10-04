# 2026-10-04: design round on lc-306. How seam content reaches a session whose callers filter verb output

**Desk:** lifecycle-4f, wave 4 of
`docs/directives/2026-10-04-refocus-opus-desk-handoff.md`.
**Status:** GRADED AND SHIPPED (LEDGER:179, build `50ffc11`). The judgment
desk (tmp-ad) approved D1 to D4 as written, with one condition, and ruled
D5: allowed. The probe of section 4 passed and section 8 records it. The
text below section 8 stands as proposed.

**The condition, now part of D1:** "last" across two streams is a claim
about FLUSH order, not print order. Under `2>&1` both streams share one
pipe and stdout is block-buffered into it, so the run flushes stdout before
it writes the goal line. A test runs the verb in a child process with both
streams on one pipe; removing the flush alone turns it red.

**D5 as ruled:** the change ships inside the drift-arm window. Rows after
it are marked POST-DELIVERY and never pooled. The arm's report states the
mid-window change and that the arm switch halves treated sessions from
that date.

**Recommendation in one line:** move the goal line to where filters do not
cut it (last line of the run, on stderr), ship that with the arm switch as
the first trialed mechanism, and hold the refusal form in reserve with a
pre-stated trigger. The evidence does not support the prediction that only
a refusal survives the callers' filters.

## 1. What was measured

`tools/verb-delivery.py` (new, committed with this file) joins each
fire-log record to the Bash call that produced it and to the tool result
the session received. Window 2026-09-25 to now, roster repos, 1,853 verb
calls in 189 transcript files. All figures machine-computed.

| class | fire records | joined | marker in the tool result |
|---|---|---|---|
| goal seam (a print) | 24 | 22 | 3 (13%) |
| refused write (outcome 2 on a carrier-writing verb) | 82 | 75 | 71 (94%) |
| finding from a reading verb | 335 | 47 | 30 (63%) |

Caller shapes of the 22 goal-seam calls: 10 piped to `grep`, 9 piped to
`tail`, 3 bare. The 3 bare calls are the 3 deliveries.

Caller shapes of the 75 refused writes: 35 piped to `tail`, 21 bare, 7
piped to `grep`, 7 piped to `head`, 5 captured. 49 of 75 are piped, yet 71
arrive.

**Controls.** The join reproduces the hand count already on record (2 of
14 in one lifecycle session, 0 of 4 in one statiker session, row 3 and 4
of the drift log). The first run of the tool classed 15 goal-seam calls as
bare with 12 of them undelivered, which cannot be; the scan stopped at a
semicolon inside a quoted `--reason`. Made quote-aware and checked on five
constructed shapes.

**Not verified:** 288 of 335 reading-verb findings did not join (most are
session-start hook runs, which are not Bash calls), so the 63% is a
fraction of the joined 47 only. Delivered means the marker is in the tool
result, not that it was read.

## 2. What the evidence says about each candidate

**The refusal survives, but not for the reason the candidate assumed.**
Candidate (a) was that a nonzero exit stops the pipeline. It does not: in
49 of 75 refused writes the verb sat in a pipe, where the filter's exit
code replaces the verb's. The refusal text arrived anyway in 45 of those
49, because a refused verb prints little else, so the refusal is the tail
of a short output. Its advantage is POSITION and BREVITY. The goal line has
neither: it is printed first, ahead of the move, the commit and the
conservation lines.

**Stderr (c) is half a channel.** Callers merge stderr into the pipe
(`2>&1`) in 9 of the 19 piped goal-seam calls and 47 of the 49 piped
refused writes. Stderr alone would have reached 13 of 22 goal seams.

**Position alone is half a channel too.** A last line survives `tail` and
is cut by `grep` and `head`.

**The two together cover what either misses.** On the 22 recorded
goal-seam calls: 3 bare, 10 `grep` with stderr free (stderr passes), 9
`tail` with stderr merged (last line passes). Derived, not yet run: 22 of
22. On the wider population of 75 write-verb calls: derived 58 of 75
(77%); the misses are `grep` and `head` with stderr merged, and captures.

**Candidate (b)**, a pending record the next verb re-reads and refuses on,
is a demand with a delay. Nothing measured here argues for it over (a),
and it adds a carrier.

**The refusal form (a)** does what round 2's principle asks: the verb
retrieves and refuses until a disposition is written. Of 71 delivered
refusals, 58 (82%) were followed by the same verb running clean in the
same session within 30 minutes. Its cost: every close becomes two
invocations and a new required slot, on an act that is legitimate every
time. That is a required input, not a guard, and it should be admitted as
one.

**Withdrawing the print** is the remaining option. It is premature: the
print has been tested 3 times.

## 3. The decisions proposed

**D1. The goal line moves; nothing else changes.** At the three seams
(`item close`, `arc advance`, `arc narrow`) the goal line is emitted
(i) as the LAST output of the run, after the verb's own lines and after
the due-read lines the wrapper appends, and (ii) on stderr. The text and
its sources are unchanged (`verbs._goal_line`). Reuse: the wrapper tail in
`cli.py` that already appends the due-read lines is the one site that runs
after everything else; the verb hands it the lines the way it already
hands it `fire_detail`.

**D2. It ships with the arm switch, as the per-arc design specifies for a
print.** ON emits the line and records `arm=on`; OFF emits nothing and
records `arm=off; withheld=goal-seam`. Arm from the session id and the
mechanism name, no flag. DELIVERED is the marker in the tool result,
measured by `tools/verb-delivery.py`.

**D3. The fire log and the drift log say what they count.**
`goal-seam=` stays the record of a print. The delivery tool is the record
of an arrival. The drift log's `checks_written` column is already
deliveries (rows 3 and 4); its header note says so.

**D4. The refusal form is held, with its trigger written now.** If, once
delivery is at or above the gate, 20 delivered goal lines produce no
goal-check in the reason prose that follows them, the notice leg is
refuted WITH delivery, which round 2 could not say (it was starved). The
next design round then takes the refusal form. Before that there is no
evidence a demand is needed here, and law 26 asks first whether the
default can make the demand unnecessary.

**D5. Question for the judgment desk: round 2's D5.** Round 2 ruled no
mechanism change inside the drift-arm window, which closes 2026-10-18.
This ships inside it. Recommendation: allow it. The arm has been measuring
a treatment that arrived 3 times in 22, so the window protects nothing.
Rows written after the change are marked POST-DELIVERY and never pooled
with earlier rows, the convention the PRE-MOVE rows already follow. The
arm switch also halves the treated sessions, which the arm's reader must
know.

## 4. The pre-registered probe (runs after grading, before any build)

**What runs.** For every joined goal-seam call and every joined
refused-write call in the rows file, the recorded filter (`tail -N`,
`head -N`, `grep` with its pattern, `cut`) is applied to a synthetic
output shaped as D1 specifies: the verb's usual lines on stdout, the goal
line last and on stderr, stderr merged or free as the call had it. Only
those four filters are executed, with their recorded arguments; a call
with any other filter, a capture or a redirect is counted UNDELIVERED
without being run.

**Criterion.**

| arm | threshold | expectation, stated now |
|---|---|---|
| goal-seam calls delivered | at least 18 of 22 | 22 |
| write-verb calls delivered | at least 53 of 75 (70%) | 58 |
| control: the same replay with the line FIRST and on stdout | at most 5 of 22 | 3, today's measured figure |

PASS needs all three. The control is what makes the replay an instrument:
if it does not reproduce today's 3, the replay is not modelling the
callers and the other two arms mean nothing.

**After the build, the live gate.** The per-arc design's delivery gate:
fewer than half of ON fires delivered is NOT DELIVERED, and the arm
reports delivery and stops.

## 5. What this does not do

- It does not make the goal line a demand. It makes a notice arrive.
- It will not survive a caller who merges stderr and greps. 7 of 75
  write-verb calls have that shape.
- Callers adapt. A line that is always last may be cut by habit later; the
  live gate is what would show it.
- It cannot be graded for EFFECT soon. The per-arc design expects COULD
  NOT VERIFY at today's arc rate. The first result will be about delivery.

## 6. Transition table

Home: this file. No row is built before grading and a probe pass.

| arrow | verb | record written | check that proves it | OBSERVER |
|---|---|---|---|---|
| a seam verb finishes, arm ON | `item close`, `arc advance`, `arc narrow` | goal line last on stderr; fire detail `goal-seam=<seam>; arm=on` | red-first: the line is the final line of the run's stderr and absent from stdout; a fixed session id yields a fixed arm | the verb invocation |
| a seam verb finishes, arm OFF | the same three | no goal line; fire detail `arm=off; withheld=goal-seam` | red-first: nothing matching the marker on either stream; the withheld token present | the verb invocation |
| the line reaches the session or not | none; read afterwards | a row per fire record: shape, stderr, delivered | `tools/verb-delivery.py`, shown live on a known delivered and a known cut call | the grading run of the per-arc design |
| 20 delivered lines, no goal-check | none | a ledger line: notice leg refuted with delivery | the count from the delivery rows joined to the drift log | the drift log's writer, at each new row |
| the drift window closes | none | rows marked POST-DELIVERY | the row's own note | the date, 2026-10-18, already on the arm's item |

## 7. Reproduce

```
python3 tools/verb-delivery.py --since 2026-09-25 --out <file outside the repo>
```

## 8. The probe as run, and the first live calls (2026-10-04)

`python3 tools/verb-delivery.py --since 2026-09-25 --until <the commit
time of 63bd5e2> --replay`. Machine-computed.

| arm | threshold | expected | result |
|---|---|---|---|
| goal-seam calls delivered | at least 18 of 22 | 22 | 22: PASS |
| write-verb calls delivered | at least 53 of 75 | 58 | 60: PASS |
| control: line first, on stdout | at most 5 of 22 | 3 | 3: PASS |

The write-verb arm came in 2 over the expectation. Derived, not checked
row by row: merged `head` or `grep` calls whose arguments happen to keep
the modelled line. The model is six
stdout lines, so that arm depends on the model's length; the goal-seam arm
and the control do not.

A first run used a shorter window by mistake (18 and 68 joined calls) and
is not the result. The figures above are over the window the thresholds
were registered on.

Live, through real shell pipelines in a scratch repo after the build:

| call shape | session arm | goal line in the output |
|---|---|---|
| `2>&1 \| tail -1` | ON | yes, the one line kept |
| `2>&1 \| grep narrowed` | ON | no (the named residual) |
| `\| grep narrowed`, stderr free | ON | yes |
| bare | OFF | no; the fire line reads `arm=off; withheld=goal-seam` |

The desk that built this is itself in the OFF arm, so its own seams
withhold the line. The first live roster record of that is the close of
lc-306.
