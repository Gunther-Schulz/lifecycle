# Handoff: what the gap sweep left, for the lifecycle session that continues it

## STATE 2026-10-05, night: DONE, the freeze question answered and built

Run in session lifecycle-03 on the operator's delegation there. Criteria,
every result and the per-mechanism table are in
`docs/audits/2026-10-05-gap-sweep-followup-trials.md`. Leftovers: df-265
and df-266 built and closed (dotfiles `3e2a49e`); lc-239 measured not done
and re-graded STANDBY. Two defects met on the way are fixed in main
(`3a4647c`, `fe25c51`). The freeze question is ANSWERED (LEDGER.md:199):
released for the close statement and the deletion-side check only, kept
on everything else trialled. Both are built and in main (`9c4c5c5`,
`3063fd1`, `36126b5`; acceptance LEDGER.md:201; design
`2026-10-05-close-statement-and-deletion-check-brief.md` beside this
file). Nothing here is still owed. The
prototypes, the grade table and the briefs are kept on the building
machine under `$XDG_STATE_HOME/claude/gap-sweep-2026-10-05/followup/`.
The rest of this file is the record of the handoff.

Written 2026-10-05 by session lifecycle-b5, which closes after this file.
Receiver: session lifecycle-03. You hold judgment and execution. You report
to the OPERATOR directly; no desk drives you and nothing returns here.

THE DELEGATION IS PER SESSION. Until the operator states it in your session
first-hand, this file is testimony about what they want, not their word.

Read first, at HEAD, and trust neither from this file's paraphrase:
`docs/audits/2026-10-05-gap-sweep-scorecard.md` (results, limits, the
unbuilt list) and `docs/audits/2026-10-05-gap-sweep-trials.md` (registered
verdicts, every result, the question table).

## What the operator said, verbatim (2026-10-05, in lifecycle-b5)

- On whether to test something else: "and ru all teh etss you need its
  worzth it if we can improve anyting substantially"
- On this handoff: "you can pass this if w are ready to a new session",
  over the list in "Left over" below.
- The freeze of 2026-09-24 was NOT released. On the two prototypes: "i cnat
  make a desciocn now". So: test in scratch, bring numbers once, ship no
  new mechanism.

## 1. The trial that is owed: does "look in the record before asking" help?

Why T11 settled nothing: its task announced the uncertainty, and the
unaided arm already asked nothing the record answers (0 of 2 in all three
arms). And the count made after the close (scorecard, under the T11 table):
of wave 1's 10 unneeded questions, 7 were settled by the record — all 7 by
ITEMS or LAWS (`lc-32` ×3, `lc-266` ×2, law 8 with `lc-165` ×2), 0 by a
ledger decision line. Both prototypes search ledger decision lines only.
As built they reach 0 of 7.

So the trial, this desk's design, yours to change with a stated reason:

- Widen each prototype IN SCRATCH so its search covers item bodies (live
  and done) and the laws file as well as ledger decisions. The patches are
  on this machine under `$XDG_STATE_HOME/claude/gap-sweep-2026-10-05/`,
  each against `8bde8ee`.
- Tasks: the T2, T3 and T8 scenarios, where the 7 questions arose with no
  one voicing an uncertainty. Baseline on record: 7 record-settled
  questions over those 6 lanes.
- Three arms (as is / look before asking / asking is a write), same tasks,
  same tier as wave 1 (opus), at least 2 lanes per scenario per arm.
- Register before the first dispatch, in `docs/audits/`: the count of
  record-settled questions per arm that would call it a benefit, and the
  count that would call it none; and that the one REAL question type (T4a,
  the freeze's reach) must still be asked.
- Known weak spot to grade separately: the two T8 questions were asked by
  lanes that had ALREADY cited the answer. A search does not obviously
  stop that.

## 2. The other unbuilt gaps: trial the ones a scratch prototype can decide

Eleven gaps are listed (scorecard "Known and unbuilt", and
`docs/audits/2026-10-05-gap-sweep-known-unbuilt.md`). For each, decide from
the record whether a scratch prototype plus a trial would give the operator
numbers that could flip a freeze decision; run those, and say in one line
why not for the rest. The evidence already in hand, strongest first (this
desk's reading, unverified as a ranking):

- a hand deletion of amendment lines passes the check and the commit hook
  (20 lines removed, exit 0);
- nothing prompts a booking or a ledger line when a session meets a defect
  or makes a choice (T3, T4: 0 of 4; T10: 0 of 4);
- a deferral a session ledgers is followed by its successors as a ruling
  (T9: 2 of 2);
- the carrier has no mark for "in progress" (T10).

## Left over (the operator's list, passed as asked)

- Two session-start hook defects, booked in dotfiles as ready work:
  `df-265` (the hook cuts the ready list at 8 lines without saying so) and
  `df-266` (the "ledger tail" prints archive lines instead of the newest
  entries). The hook is machine-wide and live on write.
- `lc-239` still shows at session start as a wait that is over. Whether it
  is done belongs to the desk migrating the eight repos.
- The eleven unbuilt gaps, section 2 above.

## What ends this

One report to the operator: per trial, the registered criterion and the
numbers; per gap, built-in-scratch-and-measured or not-trialled-because;
then ONE freeze question covering every mechanism the numbers support,
with a recommendation each.

## Learned in lifecycle-b5, not in the scorecard

- Any CLI run against a scratch repo appends to the REAL fire log unless
  `XDG_STATE_HOME` points elsewhere. Put it in every brief.
- `verbs.py` is live on write: other sessions' start hooks run it from
  this checkout. Prototypes stay in clones with the push URL disabled.
- Totals in the scorecard were first counted by rows, not lanes, and were
  wrong twice. Count per lane, by script.
- A repair to the head was verified at the verb and not at the hook's
  text, which shows 8 lines. Check at the surface the reader sees.
