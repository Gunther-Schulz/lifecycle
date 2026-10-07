# Drain wave D — 12 defect repairs, five lanes (2026-10-07)

Fourth wave of the 2026-10-07 drain (operator direction, first-hand: the
desk decides). The 2026-09-24 freeze stands: **defect repairs only.**

**This brief is a DELTA over three files. Read them completely, in
order, before this one:** `docs/directives/2026-10-07-drain-wave-a.md`
(the common rules), `docs/directives/2026-10-07-drain-wave-b.md` (its
"Changes against wave A") and `docs/directives/2026-10-07-drain-wave-c.md`
(its "Changes against wave B", all four, including what earlier lanes
measured about the harness and the prover). Where files disagree, the
later one wins.

## Changes against wave C

1. **The prover now also runs every row's CONTROL under each mutation**
   (lc-200, landed). An arrangement whose mutation reddens a control is
   FAILED. A mutation that SWAPS a condition instead of removing it does
   exactly that — write arrangements that DISABLE the check. The full
   walk takes roughly twice as long as before; await it.
2. **A prover anchor is a dependent of the source line it quotes**
   (measured three times today). Before editing a line in a core file,
   `grep -n -F '<that line>' tools/prove-rows.py`; if an arrangement
   quotes it, re-anchor that arrangement in the same commit and run its
   single-ident proof. `test_refusals` goes red when you miss one.
3. **Every item and arc verb now refuses a carrier with uncommitted
   changes at entry** (lc-318, landed). Fixtures that hand-edit a
   carrier and then call a committing verb must commit the edit first.
4. **Every test module imports `_isolation` FIRST**, before any verb
   runs, or its verb runs land in the operator's live fire log. The
   suite has a guard for this; run the full suite before your first run
   of a new test file's verbs, not after.
5. Registry rows stay open to every lane on wave C's terms.

## Rulings the item bodies do not carry

- **lc-62** — the read-side half was built in wave C and REVERTED at
  integration (its commit is `8a3e415` on branch
  `worktree-agent-a8ed30f20055f2d9d`; `git cherry-pick 8a3e415` onto
  your base is the sanctioned start, expect small conflicts with later
  commits). It over-fired on real carriers: about 300 near-match lines
  on one governed repo, where one boilerplate blocker question is shared
  by hundreds of items. **The ruling: a near-match is reported ONCE PER
  DISTINCT BLOCKER QUESTION**, with the count of items carrying it and
  at most three example ids, never once per item. For this item only you
  MAY run `item check` and `item ready` READ-ONLY over the repos listed
  in `~/.config/lifecycle/repos`, with `XDG_STATE_HOME` on scratch, to
  measure the line count before and after; write nothing there. The
  answer-time half (`ledger add decision` naming a near-match as it
  answers) is in scope: `cmd_ledger_add` is in your write set.
- **lc-203** — the fix is built: `docs/directives/2026-10-07-lc203-built-not-landed.md`
  holds the patch. Your work is the 22 fixtures it exposes (three roster
  rows' fixtures and five test files whose carrier heads do not
  balance): make each fixture's head counters true of its bodies, then
  land the patch. A fixture is repaired by correcting its COUNTERS,
  never by loosening the check. `item statusline` stays out: it is one
  line-pass by design; it states that it did not check.
- **lc-321** — `item repair --shape` exists to rewrite a damaged and
  possibly uncommitted carrier: it does NOT refuse a dirty carrier; it
  says in its output that it commits the carrier whole and names what
  was already pending. The retire compaction site takes the ordinary
  entry check.
- **lc-325** — an entry says it creates a file by the path not existing
  while its PARENT DIRECTORY is tracked; `item add` does not grade READY
  an entry with a path whose parent directory is not tracked either. No
  new slot.

## Lanes

Ids travel with a content anchor (the body's opening words).

**Lane D1 (opus) — verbs that leave something behind.**
Write set: `plugin/cli/lifecycle_core/verbs.py` (the arc verbs, `cmd_item_close`
and its dispositions, `cmd_item_add`'s grading), `plugin/cli/lifecycle_core/items.py`
(the done-home check's blocker dispositions only), NEW `test/test_drain_d_d1.py`,
and `test/test_arcs.py` where lc-320's criterion changes an assertion.
- lc-320 "arc advance AND arc close RETIRE A DEADLINE LANE AND DO NOT COMMIT IT"
- lc-322 "AN AMENDED external BLOCKER RIDES INTO THE CLOSURE HOME ALIVE"
- lc-325 "A MISSPELLED WRITE-SET PATH STILL BOOKS READY"

**Lane D2 (opus) — conservation in the reading verbs; two commit sites.**
Write set: `plugin/cli/lifecycle_core/cli.py`, `plugin/cli/lifecycle_core/retire.py`
(the compaction commit site only), `plugin/cli/lifecycle_core/refusals.py`
(the fixtures of rows `capture_dominated`, `net_growth`, `goal_query_undeclared`),
`test/test_items.py`, `test/test_verbs.py`, `test/test_waves.py`,
`test/test_schema.py`, `test/test_init.py`, NEW `test/test_drain_d_d2.py`.
- lc-203 "CONSERVATION IS THE ONLY INSTRUMENT THAT SEES A TRUNCATED CARRIER, AND IT RUNS IN EXACTLY ONE VERB"
- lc-321 "TWO COMMITTING SITES STILL TAKE A DIRTY CARRIER"

**Lane D3 (opus) — the near-match between a ledger answer and a waiting question.**
Write set: `plugin/cli/lifecycle_core/items.py` (the near-match report),
`plugin/cli/lifecycle_core/ledger.py`, `plugin/cli/lifecycle_core/verbs.py`
(`cmd_ledger_add` and the `item ready` line that renders an unanswered
decision), `test/test_drain_c_c3.py` as the reverted commit carries it,
NEW `test/test_drain_d_d3.py`.
- lc-62 "lc-40's repair covers the MINT side only; the ANSWER side is still verbatim-equality"

**Lane D4 (opus) — names and proofs still missing.**
Write set: `tools/prove-rows.py` (arrangements), `plugin/cli/lifecycle_core/refusals.py`
(rows for lc-323 only), the four emitting sites lc-323 names in
`items.py`, `declaration.py`, `cli.py` (`_report` only) and `init.py`,
NEW `test/test_drain_d_d4.py`.
- lc-323 "FOUR NAMING LEFTOVERS FROM lc-316 AND lc-317"
- lc-324 "FOURTEEN ROSTER ROWS ARE DARKENED BY NO ARRANGEMENT" — an arrangement per row, each admitted on the pair; a row for which none is possible is reported with the reason. Finish what fits; the rest is a named remainder.

**Lane D5 (sonnet) — the flow ratio, and verdicts asked of a shell.**
Write set: `plugin/cli/lifecycle_core/verbs.py` (`cmd_item_ratio` and
its helpers only), `plugin/cli/lifecycle_core/lanes.py`, `plugin/cli/lifecycle_core/verify.py`,
NEW `test/test_drain_d_d5.py`.
- lc-293 "item ratio lifetime tripwire reads drain as closed bodies only"
- lc-220 "THE RETIREMENT TRIPWIRE COMPUTES A LIFETIME RATIO WHERE THE RULE SPECIFIES A STRETCH" — lc-291 added a windowed reading after this was booked: measure what is still true first.
- lc-194 "A SHELL ANSWERS FOR THE LAST PROCESS ONLY"

## Verifier

As wave C, with `<BASE>` from your prompt.

## Tail (execution)

The wave A file's "Tail (execution)" block binds here verbatim; the
report channel line is in your dispatch prompt. Keep every message at or
under 3000 characters and number the parts once you know the count.
Per-item report rows: FIXED (commit) / NOT-REPRODUCED (command + output) /
GAP (what is missing, with evidence).
