# Drain wave C — 17 defect repairs, six lanes (2026-10-07)

Third wave of the 2026-10-07 drain (operator direction, first-hand: the
desk decides). The 2026-09-24 freeze stands: **defect repairs only.**

**This brief is a DELTA over two files. Read them completely, in order,
before this one:** `docs/directives/2026-10-07-drain-wave-a.md` (the
common rules: grounding, the six per-item steps, the box, verifier,
write boundaries, commit plan, critique pass, tail) and
`docs/directives/2026-10-07-drain-wave-b.md` (its "Changes against wave
A", all six, bind here). Where files disagree, the later one wins.

## Changes against wave B

1. **Registry rows are open to EVERY lane of this wave**, on wave B's
   terms (change 3 there): only where the item's done-criterion needs a
   finding or a NAMED could-not-verify answer the tool does not give
   today; reuse an existing row first and say why none fit; firing input
   and control; a recorded prove-rows arrangement admitted on the PAIR;
   each new row and arrangement inserted directly after its nearest
   relative, never at a list end. `plugin/cli/lifecycle_core/refusals.py`
   and the arrangement list of `tools/prove-rows.py` are therefore in
   every lane's write set for that purpose only.
2. **Grounding additions.** A write gate will refuse your first write
   until you have Read `docs/the-loop.md`, `docs/answerable-not-felt.md`
   and `docs/purpose.md` — read them before the critique pass.
3. **What earlier lanes measured, so you do not pay for it again**
   (relayed from wave A and B closing reports, each lane's own run):
   - the worktree harness refuses a shell line that mixes `git` with
     pipes, variables or a heredoc: one plain `git` command per call,
     edits by the Edit tool, commit messages in a file made with Write;
   - `tools/prove-rows.py` refuses to start while a core file differs
     from HEAD, so an admission pair runs AFTER that item's commit; a
     pair that fails is repaired by a further commit, never an amend;
   - the inert arm swaps a comment for a comment, re-pointed in memory
     from a scratch driver — never by committing an inert anchor;
   - the fire log is keyed by the checkout's path, so `audit` and
     `retire` inside a worktree read an empty log: no figure from them
     is evidence about the repo;
   - one suite arm skips in a worktree (`no carrier at .../worktrees/dotfiles`);
     that skip is expected, anything beyond it is a finding;
   - run the suite from the repo root, never with cwd `test/`.
4. **Your baseline is yours to measure** before the first edit; the
   figures in the wave A file are stale.

## Rulings the item bodies do not carry

- **lc-318** rests on the ledger ruling (`grep -n 'REFUSE-ON-DIRTY' LEDGER.md`)
  and on `verbs.carrier_dirty`, which lc-138 added. A `--no-commit`
  caller is never refused: the batching caller owns that commit.
- **lc-105 and lc-318 are one mechanism seen twice** — a close that
  moves a body it then cannot commit leaves the carrier dirty, and the
  next verb sweeps it up. Build lc-105 first; lc-318 then closes the
  second half.

## Lanes

Ids travel with a content anchor (the body's opening words).

**Lane C1 (opus) — closing over a live evidence blocker; dirty carriers.**
Write set: `plugin/cli/lifecycle_core/verbs.py`, `plugin/cli/lifecycle_core/items.py`
(the done-home check's message for lc-105 only), NEW `test/test_drain_c_c1.py`.
- lc-105 "An AMENDED evidence blocker rides into the closure home alive" (read its newest amended-evidence line: the route is wider than the heading says)
- lc-318 "EVERY CARRIER VERB BUT ledger add STILL COMMITS ITS CARRIER WHOLE OVER A PENDING HAND EDIT"

**Lane C2 (opus) — unnamed could-not-verify answers; the unsafe lane name at init.**
Write set: `plugin/cli/lifecycle_core/roster.py`, `plugin/cli/lifecycle_core/init.py`,
and ONLY the five emitting messages lc-316 names, wherever they sit in
`declaration.py`, `items.py` and `verbs.py`; NEW `test/test_drain_c_c2.py`.
- lc-316 "FIVE COULD-NOT-VERIFY ROWS PRINT NO ROW NAME IN THEIR OWN OUTPUT"
- lc-317 "init --lane WRITES THROUGH AN UNSAFE LANE NAME"

**Lane C3 (opus) — the live home's closed grades, and decision blockers.**
Write set: `plugin/cli/lifecycle_core/items.py`, `plugin/cli/lifecycle_core/ledger.py`,
`plugin/cli/lifecycle_core/verbs.py` (lc-165 only), NEW `test/test_drain_c_c3.py`.
- lc-134 "The live home has NO MIRROR of open_grade_in_done_home"
- lc-233 "A DECISION BLOCKER CAN BE WRITTEN IN A FORM ITS OWN ANSWER IS REFUSED IN"
- lc-62 "lc-40's repair covers the MINT side only; the ANSWER side is still verbatim-equality"
- lc-165 "AN AMENDED ENTRY HEAD KEEPS THE SUPERSEDED VALUE"

**Lane C4 (opus) — write-sets nobody resolved; the carrier nobody counted.**
Write set: `plugin/cli/lifecycle_core/items.py`, `plugin/cli/lifecycle_core/cli.py`,
NEW `test/test_drain_c_c4.py`. Lanes C1, C2 and C3 edit other functions
of `items.py` in other worktrees.
- lc-111 "The write-set slot is graded for PRESENCE, never for RESOLVABILITY"
- lc-185 "THE WAVE JOIN COMPARES PATH STRINGS NOBODY RESOLVED"
- lc-203 "CONSERVATION IS THE ONLY INSTRUMENT THAT SEES A TRUNCATED CARRIER, AND IT RUNS IN EXACTLY ONE VERB"
- lc-250 "An evidence blocker can gate an item on a predicate no outcome of which changes the item disposition"

**Lane C5 (opus) — what the prover does not prove.**
Write set: `tools/prove-rows.py` (the engine; other lanes only add
entries to its arrangement list), `test/test_prove_rows.py`.
- lc-200 "EVERY ARRANGEMENT PROVES A ROW FIRES AND NONE PROVES IT STAYS SILENT"
- lc-106 "the mutation prover proves ROWS, not their BRANCHES"
If either criterion asks for more than the prover grading what it
already runs — a new subcommand, a new file format — that part is a GAP.

**Lane C6 (sonnet) — retire, the roster runner, the slot parser, migrate.**
Write set: `plugin/cli/lifecycle_core/retire.py`, `plugin/cli/lifecycle_core/roster.py`
(the row runner only; lane C2 edits its name check), `plugin/cli/lifecycle_core/grammar.py`,
`plugin/cli/lifecycle_core/migrate.py`, NEW `test/test_drain_c_c6.py`,
and `test/test_migrate_residue.py` for lc-319.
- lc-184 "A GLOB HOME CLAIMS ITS SUFFIX AT ANY DEPTH"
- lc-101 "one roster row can abort the whole roster, and the abort reads as a finding" (if the abort is handled in `refusals.py`, that file is in your write set for it)
- lc-122 "two smaller CLI/checker defects, one booking" (its write-set is prose: resolve each half to its realizing file first; a half that lands outside this lane's files is a GAP)
- lc-319 "A TRACKED PRIOR MIGRATION REPORT IS LISTED AS A CARRIER READER BY THE NEXT RUN"

## Verifier

As wave B, with `<BASE>` from your prompt.

## Tail (execution)

The wave A file's "Tail (execution)" block binds here verbatim; the
report channel line is in your dispatch prompt. Keep every message at or
under 3000 characters — the gate refuses longer ones — and number the
parts once you know the count. Per-item report rows: FIXED (commit) /
NOT-REPRODUCED (command + output) / GAP (what is missing, with evidence).
