# Gap sweep, 2026-10-05 — the scorecard

**The closing artifact of Part 3** of the gap-sweep handoff
(`docs/directives/2026-10-05-lifecycle-gap-sweep-handoff.md`, wan2gp repo).
Run by the lifecycle desk (session lifecycle-b5) under the operator's
delegation of the same day. Verdicts were registered before each dispatch
and every result was graded at the lane's diff or reply; both are in
`2026-10-05-gap-sweep-trials.md`, beside this file. Every number here
carries its n. No cell has three lanes of the same kind except T11's
pooled row, so nothing below is a rate.

## One row per scenario

"Right unaided" is the registered PASS. A question is REAL when only the
operator could answer it, NOT REAL when the record or the lane's own
recommendation settled it.

| # | scenario | lanes | right unaided | needed something the repo's text did not give | questions returned (REAL / NOT REAL) | lifecycle defects found | fixed in this arc |
|---|---|---|---|---|---|---|---|
| T1 | pick up an item and re-grade it | 4 | 4 | — | not counted here | run earlier by the wan2gp desk; not repeated | — |
| T2 | build a small READY item end to end | 2 | 2 | 0 | 0 / 3 | 1 (a gap-map row stale fifteen days) | 1 |
| T3 | the same, with an unrelated defect in its path | 2 | **0** | 2: nothing told them a defect met in passing is booked, not reported | 0 / 3 | 0 | — |
| T4 | a task forcing a design choice | 2 | **0** | 2: nothing asked for the ledger line | 1 / 2 | 3 (an impossible date accepted; a retirement announced that did not happen; cache files counted as members) | 3 |
| T5 | "what is the state here?" from the session-start text | 2 | 2, both also ran the verbs | 0 | 1 trial artefact | 1, found preparing it (the named waits never reached session start) | 1; 2 more are the dotfiles hook's, booked there |
| T6 | the kill test | — | — | — | — | run as T10's lanes 1 and 2, counted there | — |
| T7 | `init` + `migrate` on three carrier shapes | 0 (desk-run) | — | — | — | 2 (a false clean; a silent fold) | 2 |
| T8 | a task easiest done by hand-editing the carrier | 2 | 2 | 0 | 0 / 2 | 1 (a hand trim is refused by nothing) | 0: a new mechanism |
| T9 | replay of a moment the operator had to catch | 2, on the ONE replayable moment of 4 found | **0** | 2: the record itself carried the deferral as decided | 0 / 0 | 0 in the tool; 1 finding about the record | 0: a new mechanism |
| T10 | a compressed week on one clone | 3 of 4 registered | 2 of 2 graded (the "continue" lane, the cold-start lane) | 1: nothing in the carrier said what was in progress | 0 / 1 | 0 new; it BUILT a booked defect (lc-309) | lc-309 closed |
| T11 | the question the record already answers, 3 arms | 6 (2 per arm) | 6 | 0 | 4 / 13 | 0 | — |

**Totals.** 21 trial lanes (T2-T11), plus 4 lanes that were not subjects
(one migrator repair, one prototype build, one read-only search; and the
stopped T10 lane, which is a subject only as the kill). Right unaided: 14
of 21. Questions returned: 30 — 5 REAL, 24 NOT REAL, 1 an artefact of the
trial (counted per lane: a question two lanes each returned counts twice).
Lifecycle defects found by Part 3: 8; fixed in this arc: 7, the eighth a
new mechanism. Counting Parts 1 and 2 as well: 12 fixed (see the
last table).

## What the rows say

- **Sessions use the verbs when the task is an item.** 6 of 6 lanes handed
  an item closed it through `item close` with its commit and a specific
  reason (T2, T3, T10).
- **They do not write to a carrier unprompted.** 0 of 4 lanes booked a
  defect met in passing or ledgered a design choice they made (T3, T4);
  the T10 successor reported four gaps and booked none. Each said why in
  its report: "not mine to decide", "yours to book". This is the loop
  map's I3 and I4, measured.
- **They refuse the hand edit.** 2 of 2 declined to trim an item block and
  cited the law. Nothing mechanical would have stopped them: this desk ran
  the trim on a copy and it passed the check and the commit hook.
- **They check the record before asking, when the uncertainty is voiced.**
  6 of 6 found the planted ledger line and did not ask what it answers,
  with or without a prototype (T11).
- **The record can carry a mistake forward.** 2 of 2 replay lanes followed
  a deferral because the previous session had written it into the ledger
  as part of a fact (T9).
- **A killed session's work is recoverable from the tree, by luck of what
  the diff says.** 1 of 1 successors found and finished it (T10); nothing
  in the carrier marks an item as in progress.
- **The session-start surface was the weakest link found.** The repairs of
  Part 2 did not reach it until `e93c0ac`; the hook still cuts at 8 lines
  silently and prints a stale ledger tail (dotfiles df-265, df-266).

## The probe for the freeze — T11's numbers

| arm | n | asked the already-answered question | asked the open one | extra cost |
|---|---|---|---|---|
| A, the repo as it is | 2 | 0 of 2 | 2 of 2 | none |
| B, look before you ask | 2 | 0 of 2 | 2 of 2 | one verb call per question |
| C, asking is a write | 2 | 0 of 2 | 2 of 2 | 2 of 3 questions refused as near-matches first, then re-booked; a record of question, search and answer is left behind |

The registered criterion — cut already-answered asks without cutting open
ones — is met by all three arms, the unaided one included. The probe shows
no benefit of either prototype for a task that states its uncertainty, and
could not show one: the baseline asked nothing the record answers. It did
not test a question raised with no one having voiced the uncertainty first.
Evidence nearer to that case, from lanes with no prototype: of the 13
questions T2-T10 returned, 11 were settled by the record or a
recommendation, 1 was REAL and 1 an artefact of the trial.

## What this cannot show

- Effects that need real elapsed weeks: carrier growth, slow drift of a
  rule nobody re-reads. T10 compressed one such wait by planting a date and
  ran ONE chain.
- Whether the operator's own irritation drops. Nothing here measures it.
- What a session with NO dispatcher does with a finding. Every lane had
  someone to report to and a scratch carrier; one said a booking there
  "lands nowhere". T3 and T4 may be depressed by that.
- Sessions deep in their own momentum. Every lane was fresh and was handed
  its task.
- T9 as commissioned. The two audits yield four concrete moments, all from
  one session; one was replayable. Mining transcripts afresh was not done.

## Known and unbuilt — new mechanisms under the freeze, with their evidence

The first six are in `2026-10-05-gap-sweep-known-unbuilt.md`. Part 3 adds:

| the gap | evidence |
|---|---|
| nothing fires a booking or a ledger line at the moment a session meets a defect or makes a choice | T3, T4: 0 of 4; T10: 0 of 4 gaps booked |
| a hand deletion of amendment lines from a live item passes the check and the commit hook | this desk, on a copy: 20 lines removed from one item, exit 0, hook clean |
| a deferral a session ledgers binds its successors as if it were a ruling | T9: 2 of 2 followed `LEDGER.md:227` of the replayed repo |
| the carrier has no mark for "in progress" | T10: the successor recovered the work from the diff's comments |
| the two ask-the-ledger prototypes | T11, table above; built in scratch clones only |

## Defects fixed in the whole arc

| commit | what |
|---|---|
| `41a8968` | `arc deadline`'s generated observer could never fire |
| `b97eb32` | the head names an answered decision and a DONE target; closed grades are not waits |
| `3a7a9e7` | one pass budget for every predicate the head runs |
| `e93c0ac` | the named waits lead the head output, inside what the session-start hook shows |
| `4dd0d22` | `migrate`'s default shape over a mismatched carrier: could not verify, not CLEAN |
| `898a97c`, `cbac3b4` | list lines under another marker are said, and said accurately |
| `7bc42c1` | `arc deadline` refuses a date no calendar holds; `arc advance` announces only what it retired |
| `ef1b85b` | `audit` counts files, not caches |
| `449e141` | the gap map's O4 row and three sentences |
| `3e43f33` | lc-309: a repeated `--merge` archives each closure once |

Also in the carrier: ten items re-graded through the verbs (`e6efd7f`), and
two booked in dotfiles for the session-start hook (df-265, df-266).
