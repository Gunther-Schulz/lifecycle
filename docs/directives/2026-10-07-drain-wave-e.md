# Drain wave E — 33 items, nine lanes, the freeze lifted (2026-10-07)

Fifth wave of the 2026-10-07 drain (operator direction, first-hand: the
desk decides). **The 2026-09-24 freeze is LIFTED** — operator, first-hand
at this desk, 2026-10-07; verify with
`grep -n 'lifted in general' LEDGER.md`. Items that were held because
they need a new flag, slot, row field or mechanism are now buildable.

**This brief is a DELTA over four files. Read them completely, in
order, before this one:** `docs/directives/2026-10-07-drain-wave-a.md`
(the common rules), then the "Changes against" sections of
`docs/directives/2026-10-07-drain-wave-b.md`,
`docs/directives/2026-10-07-drain-wave-c.md` and
`docs/directives/2026-10-07-drain-wave-d.md` (all bind, including what
earlier lanes measured about the harness and the prover). Where files
disagree, the later one wins.

## Changes against wave D

1. **The box's first bullet is replaced.** A new flag, slot, row field,
   refusal row or verb is IN scope exactly where the item's
   done-criterion names it, and nowhere else. The item's done-criterion
   is the design: build what it states, at its size. Anything the
   criterion leaves open that this brief does not rule on is a GAP for
   that item, never a design decision made in the lane.
2. **Still boxed, for every lane:** no change to the declaration schema
   version or to `declaration.SCHEMA_FLOOR`; no migration of any other
   repo; no carrier or docs write (`ITEMS.md`, `ITEMS-DONE.md`,
   `LEDGER.md`, `JOURNAL.md`, `CLAUDE.md`, `arcs/`, `.claude/`, `docs/`);
   no softened predicate; nothing outside your write set. Where an
   item's criterion asks for a `CLAUDE.md` change, put the exact
   replacement text in your report; the desk applies it.
3. **Step 1 for a new mechanism.** "Reproduce first" means: write the
   test the done-criterion asks for and watch it go red against the
   unmodified code for the item's own reason. Where the criterion's
   premise is already false at this base (overtaken, already built), the
   item is NOT-REPRODUCED, as before. Read the item's amendment history
   in the raw block as well as `item slots`: several items carry what an
   earlier lane measured.
4. **A new or widened finding is measured over the real carriers before
   you report it FIXED.** You MAY run `item check`, `item ready`,
   `kind check` and `audit` READ-ONLY over the repos listed in
   `~/.config/lifecycle/repos`, with `XDG_STATE_HOME` on scratch, from
   the base tree and from your tree, and report each repo's exit code
   and changed line count before and after. Write nothing there. A
   check that newly fires on honest existing work is a finding to
   report with the count, not to ship quietly (wave C and D each
   reverted one such change at the desk).
5. Registry rows stay open to every lane on wave C's terms, now also
   for a new mechanism's own refusal.

## Rulings the item bodies do not carry

- **lc-325** — the corrected direction is in
  `docs/directives/2026-10-07-lc325-built-not-landed.md`: keep the
  booking-time resolution and the "read as a file the entry CREATES"
  line; where no parent directory is tracked, STATE it ("creates the
  directory too") and leave the grade alone. The second half (an
  explicit `--grade READY` over an unresolved path) is not in scope.
- **lc-194** — the rule is narrowed by measurement (read the item's
  newest amended-evidence line): only an EARLIER pipeline stage exiting
  126 or 127 is BROKEN; any other non-zero earlier stage leaves the
  verdict exactly as it is today. The reverted first build is in main
  history as `0c079ca`.
- **lc-140** — a DONE body without its closure record is a FINDING; no
  exemption is declared. The two historical bodies will be reported
  until the desk supplies their records. Measure per change 4 and
  report how many DONE bodies each rostered repo would newly report;
  the over-fire arm (DROPPED bodies stay silent) is in the criterion.
- **lc-150** — the absolute count stays. Build ONLY arm 2 (an
  unreadable ledger line is could-not-verify with its reason, never a
  zero that reads clean). Arm 1 is withdrawn: no input makes a run
  route a ledger line, so a delta count could never fire.
- **lc-159** — only HALF 2 is open, and lc-203 (landed in wave D) put
  conservation into the reading verbs. Measure first whether a
  truncated carrier is now loud on every read path the criterion
  names; what is already loud is NOT-REPRODUCED, and only a read path
  still silent is built.
- **lc-198 and lc-95** — the `CLAUDE.md` halves are the desk's (change 2).

## Lanes

Ids travel with a content anchor (the body's opening words). Other
lanes edit other functions of the shared core files in other worktrees.

**Lane E1 (opus) — the doors of close and add; the wrong repo.**
Write set: `plugin/cli/lifecycle_core/verbs.py` (`cmd_item_close`,
`cmd_item_add`'s write-set grading, ident resolution),
`plugin/cli/lifecycle_core/cli.py` (the `item close` subparser and the
ident-taking dispatch), `plugin/cli/lifecycle_core/items.py` (the
write-set resolution helper only), `test/test_verbs.py`,
NEW `test/test_drain_e_e1.py`.
- lc-270 "item close takes a bare id and moves whatever body carries it"
- lc-325 "A MISSPELLED WRITE-SET PATH STILL BOOKS READY"
- lc-104 "wrong-repo invocations under cwd resolution"

**Lane E2 (opus) — what a reader of the carrier is shown.**
Write set: `plugin/cli/lifecycle_core/items.py` (rendering, the
evidence-blocker write path, the STANDBY reader checks),
`plugin/cli/lifecycle_core/verbs.py` (the amend / park / add calls
into those, `item ratio`'s STANDBY reading only),
`plugin/cli/lifecycle_core/cli.py` (flags for lc-250 only),
`test/test_items.py`, NEW `test/test_drain_e_e2.py`.
- lc-165 "AN AMENDED ENTRY HEAD KEEPS THE SUPERSEDED VALUE"
- lc-250 "An evidence blocker can gate an item on a predicate no outcome of which changes the item disposition"
- lc-299 "lc-294 shipped with three reader gaps"

**Lane E3 (opus) — the done home, the wave join, the truncated read.**
Write set: `plugin/cli/lifecycle_core/items.py` (the done-home check,
the waves join, conservation's call sites),
`plugin/cli/lifecycle_core/cli.py` (the `item waves` text only),
`test/test_waves.py`, NEW `test/test_drain_e_e3.py`.
- lc-140 "Invariant 5 says every exit is recorded with its reason and its commit"
- lc-139 "item waves computes its join over WRITE sets only"
- lc-159 "EVERY CARRIER WRITE IS NON-ATOMIC AND A TRUNCATED CARRIER PARSES CLEAN" (half 2 only)

**Lane E4 (opus) — what a roster row declares, and what the prover proves.**
Write set: `plugin/cli/lifecycle_core/roster.py`,
`plugin/cli/lifecycle_core/refusals.py` (the `Row` shape and its
fields), `tools/prove-rows.py` (the engine),
`test/test_roster.py`, `test/test_refusals.py`, `test/test_prove_rows.py`,
NEW `test/test_drain_e_e4.py`; for lc-74 the one statusline emitting
site in `verbs.py`.
- lc-327 "lifecycle --test MAY GRADE THE WRONG CHECKOUT"
- lc-326 "NO ROSTER ROW STATES WHAT CLASS OF INPUT FIRES IT"
- lc-178 "A DEMAND ADDED AT A WRITE DOOR CONTAMINATES EVERY ROSTER CONTROL THAT PASSES THROUGH THAT DOOR"
- lc-328 "FOUR PROOF-SHAPE LEFTOVERS FROM WAVE D"
- lc-74 "the emit-site coverage scanner (--test) detects finding emissions by grepping the literal"

**Lane E5 (sonnet) — tools and batteries that say less than they do.**
Write set: `tools/` (every file except `prove-rows.py`'s engine: for
lc-117 you add ONE module-level constant line to it, nothing else),
NEW `tools/verify-suite.py`, `test/test_verbs.py` (the one skipping
arm lc-198 names), `test/test_waves.py` and `test/test_items.py` (the
explicit-zero assertions lc-136 names; lane E3 adds tests to
`test_waves.py` in another worktree — touch only the assertions you
pair), NEW `test/test_drain_e_e5.py`.
- lc-117 "a repo tool that MUTATES TRACKED FILES is indistinguishable, from outside, from one that only reads"
- lc-198 "A SILENTLY SKIPPED ARM IS A REACH ARM DELETED, AND THE SUITE STILL EXITS 0"
- lc-136 "AN EXPLICIT-ZERO ASSERTION IS SATISFIED BY A DEAD PRODUCER"
- lc-95 "This repo's '## Verify' section misdescribes its own checks" (the check only; read `CLAUDE.md`, never write it)

**Lane E6 (opus) — the audit walk and the sweep.**
Write set: `plugin/cli/lifecycle_core/retire.py`,
`plugin/cli/lifecycle_core/cli.py` (the `--test` and `audit` output
lines lc-204 and lc-76 name), `test/test_retire.py`,
NEW `test/test_drain_e_e6.py`.
- lc-99 "a retire makes the migrated repo's own audit go from CLEAN to FINDING"
- lc-201 "A GIT WORKTREE REGISTRATION IS A PERSISTED THING THAT RESOLVES TO NO REGISTERED KIND"
- lc-204 "LIFECYCLE WRITES USER-GLOBAL STATE UNDER TWO XDG VARIABLES AND NOTHING PUBLISHES THE SET"
- lc-76 "The stray sweep is not part of the read-only pass and has no fourth disposition"

**Lane E7 (sonnet) — the migrator.**
Write set: `plugin/cli/lifecycle_core/migrate.py`, `test/test_migrate.py`,
`test/test_migrate_residue.py`, NEW `test/test_drain_e_e7.py`.
- lc-36 "migrate TRUNCATES the requirement slot at a fixed ~277 chars with an ellipsis"
- lc-217 "A COMPLETED CARRIER MIGRATION THAT LEAVES ITS SOURCE BEHIND IS AN UNFINISHED MIGRATION"
- lc-150 "migration_ledger_nonzero IS WRONG IN BOTH DIRECTIONS AT ONE SITE" (arm 2 only, ruling above)

**Lane E8 (opus) — the declaration's references and reserved names.**
Write set: `plugin/cli/lifecycle_core/declaration.py`,
`plugin/cli/lifecycle_core/cli.py` (`kind check` / orientation output
for lc-70 only), `plugin/cli/lifecycle_core/migrate.py` (`run_schema`'s
closing sentence for lc-215 only; lane E7 edits other functions),
`test/test_declaration.py`, `test/test_schema.py`,
NEW `test/test_drain_e_e8.py`.
- lc-189 "THE PRODUCER ROUTE IS UNFALSIFIABLE IN ONE DIRECTION"
- lc-215 "run_schema's 'in every carrier' MEANS EXACTLY THREE KINDS"
- lc-70 "tend feature completeness"

**Lane E9 (sonnet) — init, records, commit-or-say, shell verdicts.**
Write set: `plugin/cli/lifecycle_core/init.py`,
`plugin/cli/lifecycle_core/records.py`, `plugin/cli/lifecycle_core/lanes.py`,
`plugin/cli/lifecycle_core/verify.py`, `plugin/cli/lifecycle_core/workflows.py`,
`plugin/cli/lifecycle_core/desk.py`, `plugin/cli/lifecycle_core/ledger.py`,
`plugin/cli/lifecycle_core/verbs.py` (only the commit-or-say line of a
verb lc-41 enumerates), `test/test_init.py`, `test/test_records.py`,
`test/test_lanes.py`, `test/test_verify.py`, NEW `test/test_drain_e_e9.py`.
- lc-23 "init creates the declaration and lane stubs but no carrier files"
- lc-225 "AN INVESTIGATION ROUND SERIES IS VISIBLE TO NOBODY WHO IS IN IT"
- lc-41 "Not every carrier-writing verb commits its own write or says NOT COMMITTED"
- lc-194 "A SHELL ANSWERS FOR THE LAST PROCESS ONLY" (ruling above)

## Verifier

As wave D, with `<BASE>` from your prompt, plus change 4's before/after
table for every item that adds or widens a finding.

## Tail (execution)

The wave A file's "Tail (execution)" block binds here verbatim; the
report channel line is in your dispatch prompt. Keep every message at or
under 3000 characters and number the parts once you know the count.
Per-item report rows: FIXED (commit) / NOT-REPRODUCED (command + output) /
GAP (what is missing, with evidence).
