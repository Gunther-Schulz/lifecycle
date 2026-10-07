# Drain wave B — 19 defect repairs, six lanes (2026-10-07)

Second wave of the 2026-10-07 drain (operator direction, first-hand:
the desk decides). The 2026-09-24 freeze stands: **defect repairs only.**

**This brief is a DELTA over `docs/directives/2026-10-07-drain-wave-a.md`.**
Read that file completely first. Its sections "Grounding basis",
"Background", "The settled design" (the six per-item steps and the box),
"Verifier", "Write boundaries", "Commit plan", "Critique pass" and "Tail"
bind here unchanged, except where a line below says otherwise. Where the
two files disagree, this one wins.

## Changes against wave A

1. **Base check, with its one recovery.** BASE is quoted in your dispatch
   prompt. Three reads as in wave A. If HEAD is BEHIND BASE over a clean
   tree, run `git merge --ff-only <BASE>` once, re-run the three reads,
   and report it as a deviation. Any other failing state halts the lane.
   The base check is the ONLY lane-wide halt; every later gap halts the
   item, and you finish the others.
2. **Blockers.** Before building an item, read its effective `blocked-by`
   from `item slots`. Anything other than `NONE` makes the item a GAP —
   except lc-138, whose decision is answered (below).
3. **Registry rows — lanes R1, R2, R3 and M2a only, and only where the
   item's done-criterion requires a finding the tool does not emit
   today.** `plugin/cli/lifecycle_core/refusals.py` and `tools/prove-rows.py`
   are in those lanes' write sets for exactly this. A new row carries
   what law 2 demands: its firing input and control, proven red first,
   its route set, and a recorded prove-rows arrangement admitted on the
   PAIR (CLAUDE.md, "A NEW ARRANGEMENT IS ADMITTED ON A PAIR": real
   anchor → `rows changed: <the row>`; inert anchor → `rows changed:
   NONE` and FAIL; both outputs quoted). Read "ADDING A ROW CAN RETIRE A
   NEIGHBOUR'S PROOF" in the same file before you add one. Where an
   existing row already names the refusal, reuse it; a new row is the
   last resort, and the report says why none fit.
   **Other lanes add rows to the same two files in other worktrees.**
   Insert each new row, and each new arrangement, immediately AFTER the
   existing entry most closely related to it — never at the end of a
   list — so the hunks do not collide at integration.
4. **New tests go in your lane's own NEW test file** (named per lane
   below; `git add -N` it). Edit an existing test file only where your
   item's done-criterion changes a behaviour that file asserts, and name
   each such edit in the report with the criterion sentence licensing it.
5. **Trailer.** Exactly the line in your dispatch prompt.
6. **Still boxed for every lane:** no new verb, flag, stage or schema
   field; no carrier or docs write; no softened predicate; nothing
   outside your write set.

## Rulings the item bodies do not carry

- **lc-138** — decided, LEDGER.md decision line of 2026-10-07 (verify
  with `grep -n 'REFUSE-ON-DIRTY' LEDGER.md`): **refuse-on-dirty.** When
  the ledger carrier has uncommitted changes at verb entry, `ledger add`
  writes nothing and commits nothing; it names the carrier and says the
  pending edit must be committed first under its own message. Red-first:
  a carrier dirty with an unrelated hand edit at verb entry. MUST-NOT-MOVE:
  a clean-carrier invocation still commits exactly what the verb wrote;
  `--no-commit` callers are not refused by this check unless the item
  body says otherwise.
- **lc-85** — decided at this desk on lane A's evidence: **exit 0 stays.**
  The existing tests in `BulletShapeOverNoEntries` state that zero
  entries is an answer, and they do not move. Only the SUMMARY changes:
  a run whose reconciliation is 0 read == 0 written says in its summary
  line that it was vacuous and examined no entry, and does not print a
  bare CLEAN. Red-first as the item states it.

## Lanes

Ids travel with a content anchor (the body's opening words).

**Lane R1 (opus) — ledger commit refusal and the flag-order error.**
Write set: `plugin/cli/lifecycle_core/verbs.py`, `plugin/cli/lifecycle_core/cli.py`,
`plugin/cli/lifecycle_core/refusals.py`, `tools/prove-rows.py`,
NEW `test/test_drain_b_r1.py`.
- lc-138 "the ledger verb commits its carrier WHOLESALE"
- lc-211 "THE --repo FLAG-ORDER ERROR TELLS A CALLER THEIR REPO PATH IS BAD WHEN THE FAULT IS ARGUMENT ORDER"

**Lane R2 (opus) — the walk on a second machine, and the empty record.**
Write set: `plugin/cli/lifecycle_core/retire.py`, `plugin/cli/lifecycle_core/records.py`,
`plugin/cli/lifecycle_core/refusals.py`, `tools/prove-rows.py`,
NEW `test/test_drain_b_r2.py`.
- lc-314 "THE AUDIT WALK READS A MACHINE-LOCAL LOG AS THE REPO'S EXIT HISTORY"
- lc-188 "A RECORD WITH ZERO GRADED LINES READS CLEAN"

**Lane R3 (opus) — lane list, lane new, verify.**
Write set: `plugin/cli/lifecycle_core/lanes.py`, `plugin/cli/lifecycle_core/verify.py`,
`plugin/cli/lifecycle_core/refusals.py`, `tools/prove-rows.py`,
NEW `test/test_drain_b_r3.py`.
- lc-212 "AN EMPTY ROSTER EXITS CLEAN, BETWEEN TWO NEIGHBOURS THAT BOTH REFUSE"
- lc-202 "lane new DOES NOT VALIDATE ITS ONE POSITIONAL ARGUMENT"
- lc-230 "THE VERIFY VERB COLLAPSES THREE ANSWERS INTO TWO AT THE EXACT BOUNDARY IT EXISTS TO DEFEND"

**Lane M2a (sonnet) — migrate, summary and gates.**
Write set: `plugin/cli/lifecycle_core/migrate.py`, `plugin/cli/lifecycle_core/refusals.py`
(the `migration_ledger_nonzero` row only, for lc-150), `tools/prove-rows.py`
(that row's arrangement only, if its anchor moves), NEW `test/test_drain_b_m2a.py`.
Lane M2b edits other functions of `migrate.py` in another worktree.
- lc-85 "migrate's terminal summary prints CLEAN beside a reconciliation that can be 0 read == 0 written" (ruling above)
- lc-150 "migration_ledger_nonzero OVER-FIRES"
- lc-88 "migrate --report-only structurally CANNOT answer 'would this merge refuse?'"
- lc-34 "A two-run merge has an UNENFORCED precondition"

**Lane M2b (sonnet) — migrate, provenance and residue.**
Write set: `plugin/cli/lifecycle_core/migrate.py`, NEW `test/test_drain_b_m2b.py`.
Lane M2a edits other functions of `migrate.py` in another worktree.
- lc-71 "migrate --merge run twice in one repo appends a SECOND residue item"
- lc-83 "migrate's residue consumer list is built by a SUBSTRING match on the carrier basename"
- lc-94 "The re-import DETECTOR may inherit the pseudo-ident defect lc-92 found one function over"
- lc-114 "The re-import provenance lookup keys on MUTABLE state while an immutable pin sits in the same record"
- lc-214 "THE DELETION-RECORD IDEMPOTENCE TEST IS TWO INDEPENDENT SUBSTRING TESTS, NOT A ROW MATCH"

**Lane V2 (sonnet) — verbs, the judgment register, the leak scan's own root.**
Write set: `plugin/cli/lifecycle_core/verbs.py`, `plugin/cli/lifecycle_core/judgment.py`,
`plugin/cli/lifecycle_core/cli.py` (the `item close` subparser and its
dispatch only), `tools/absence-scan.mjs`, `test/absence-scan.test.mjs`,
NEW `test/test_drain_b_v2.py`. Lane R1 edits other functions of
`verbs.py` and `cli.py` in another worktree.
- lc-109 "the judgment register's OVERRIDE evidence is decided by a SUBSTRING MATCH OVER A RENDERED MESSAGE"
- lc-110 "the judgment register prices a rule's retirement on a DENOMINATOR that omits its new commonest outcome"
- lc-275 "The duplicate check at item add fails in both directions"
- lc-270 "item close takes a bare id and moves whatever body carries it" — if its done-criterion can only be met by a new flag or a new row, it is a GAP for this lane.
- lc-32 "A repo copy placed under a Claude Code scratchpad fails two absence-scan tests" (its amended criterion: the scan stops asserting over its own checkout root; verifier `node --test test/absence-scan.test.mjs`. Your worktree path may itself reproduce the defect — measure the battery before your first edit and say what you saw.)

## Verifier

As wave A, with `<BASE>` from your prompt. Lanes adding a row also paste
the admission pair. The full `python3 tools/prove-rows.py` walk runs
once at the end of the lane; it takes several minutes — await it, and
send an INTERIM report only if you must.

## Tail (execution)

A mid-run message may not arrive before the turn ends: on a gap
HALT THE ITEM, FINISH THE REMAINDER, REPORT — never halt the
LANE, since "halt and wait" is not a survivable state for a
subagent (source: §2, the delivery binding).
Closing report (mandatory; the project's own report form if it
defines one, else the §2 form here — never both; "none" is a
valid slot answer, silence is not): (a) items completed w/
evidence, (b) checks RUN w/ real output — FULL counts incl.
skips (`N passed, M failed, K skipped`), each skip dispositioned
(which check, why, whether the reason touches the item); a skip
in a check YOU built is a finding, not a pass — the built branch
did not execute, (c) gaps surfaced —
incl. anything needing a tier above yours, returned as a question
with its evidence, never settled at your tier,
(d) deviations w/ reason, (e) candidate lessons, (f) files
touched + commit hashes (unpushed) — only commits whose
Co-Authored-By trailer is YOURS; one you cannot claim by
trailer is "present in the tree, not mine"; a `.git/config`
write counts as a repo write, (g) what was NOT verified,
(h) sources actually read, of those the brief named.
Every claim about something OUTSIDE your own work — a file you
did not write, a mechanism, another repo, a tool's behavior —
names the read that opened it, or carries "inferred,
unverified"; a recommendation resting on an unopened claim
carries the grade too.
Drain your inbox before sending, and between parts of a
multi-part report: every dispatcher message received up to send
time is dispositioned or named as unhandled.
(The report channel line is in your dispatch prompt.)
Message ≤3000 chars each: a report longer than one message is
SPLIT into labeled parts (1/N) — do NOT write a report FILE
(harness-blocked for subagents); supporting data goes to the
brief's assigned DATA files, the message carries key findings
+ any such paths. A missing decision, file,
or value is surfaced as a gap, never bridged with a guess.
A check that got backgrounded is AWAITED before the closing
report (TaskOutput block=true on its task id) — ending your
turn orphans it; a report sent with a check still running is
an INTERIM report, says so, and names what remains.
Commits unpushed, by pathspec — `git commit -m "…" -- <paths>`
with every flag BEFORE the `--` (after it git reads `-m` as a
pathspec and the commit fails; `-F` for a multi-line message),
never
`git add` then `git commit` and never `-A`: the index is shared,
so a co-writer staging between your `git status` and your commit
rides out under your message whatever you added. A NEW file is
invisible to a pathspec commit until `git add -N <path>`
registers it (intent-to-add: zero content staged, full body
still committed). Trailer:
`Co-Authored-By: Claude <model> <noreply@anthropic.com>`.
Never amend — always a new commit: the amend-gate denies
subagent amends regardless of ownership (source: §1 amend
rule).
After sending the report your write grant is over: a defect you
find later is REPORTED, never edited or amended (source: §4
ownership rule).

Per-item report rows: FIXED (commit) / NOT-REPRODUCED (command + output) /
GAP (what is missing, with evidence).
