# Drain wave A — 22 STANDBY/READY defect repairs, six lanes (2026-10-07)

Operator direction, first-hand at this desk 2026-10-07: work the backlog
down on the desk's own recommendations while weekly budget remains. The
2026-09-24 freeze stands (LEDGER.md:138, :147): **defect repairs only, no
new mechanism.** This file is the brief for every lane of the wave; the
dispatch prompt names the lane and carries the report channel line.

Working copy: the lane's OWN git worktree (harness-isolated), cwd-relative
paths only. Scratch: the agent's OWN scratchpad.

Base check, the lane's first act, three reads:
`git merge-base --is-ancestor <BASE> HEAD` (must succeed),
`git log --oneline <BASE>..HEAD` (must be empty),
`git status --porcelain` (must be empty). `<BASE>` is the commit that
added this file: `git log -1 --format=%h -- docs/directives/2026-10-07-drain-wave-a.md`
run in the main checkout gave the hash quoted in the dispatch prompt.
Any other state: halt the lane and report it as a gap.

## Grounding basis — read before building; the report cites what was actually read

- the executor skill (`dispatch-guards:executor`) — load FIRST
- `CLAUDE.md` — the LAWS (1, 2, 4, 5, 6, 8, 11, 22, 24, 26) and the
  sections "The two exit-code contracts" and "Verify"
- for each of your items: `XDG_STATE_HOME=<your scratch>/state python3 plugin/cli/lifecycle --repo . item slots lc-<N>`
  (the current truth, amendments resolved) AND the raw block in
  `ITEMS.md` under `## lc-<N>` (the amendment history). The item body is
  the settled design for that item; this file does not restate it.
- the source file(s) the item names, at the site the defect lives

## Background (established; verify at the cited lines)

- Base suite at the main checkout, 2026-10-07: `python3 -m unittest discover -s test -p 'test_*.py'`
  → `Ran 1311 tests in 38.593s  OK` (no skips printed). In a worktree
  outside `~/dev` one arm premised on a sibling dotfiles checkout may
  skip (from item lc-198's body, unverified) — measure YOUR baseline
  before your first edit and report it.
- Commit guards: `git config core.hooksPath` → a machine-wide hooks
  directory holding `pre-commit`, `post-commit`, `pre-push`, no
  `commit-msg` (directory listing read 2026-10-07). `pre-commit` runs a
  lifecycle carrier-shape gate (its line 1036 ff., read) which you do
  not touch because you write no carrier; it also carries trailer and
  claims lanes (from `docs/the-loop.md` row I7, not opened in detail —
  unverified).
- Every item body was written between 2026-08-27 and 2026-10-05 and
  cites line numbers and behaviour AS OF ITS BOOKING. None was
  re-verified at this desk. Treat each as testimony until your own
  red-first run reproduces it.
- The main checkout is the LIVE CLI for every governed repo on this
  machine (a symlink resolves into it). You never write there.

## The settled design — implement exactly this, do not redesign

For EACH item, in the order your lane lists them:

1. **Reproduce first.** Write the test the item's done-criterion asks
   for and run it against the UNMODIFIED code. It must go red for the
   item's own reason — not an import error, not a missing fixture
   (law 4). Paste that red output in the report.
2. **Not reproduced → no change.** If the defect is already repaired,
   overtaken, or the body's premise is false at this base, STOP that
   item: change nothing, keep no test, and report NOT-REPRODUCED with
   the command and its output. That is a complete and valued result.
3. **Fix at the site where the wrong answer is produced or consumed**,
   as small as the item asked for. Before writing, read how the file
   already does the same thing elsewhere and reuse it (law 26: the
   correct predicate usually exists one import away); the report names
   what you reused, or what you read and why nothing fit.
4. **Three answers** (law 1): clean / finding / could-not-verify never
   share an exit code; a run that examined nothing says so.
5. **Then green**: the new test passes, and the full suite is no worse
   than your measured baseline, skips included.
6. **One commit per item.**

The box — what you must NOT do; hitting any of these halts THAT ITEM
(finish the others, report the gap with its evidence):

- no new verb, flag, stage, schema field or refusal ROW; `plugin/cli/lifecycle_core/refusals.py`
  is outside every lane's write set. If a done-criterion can only be
  met by a new registry row (a newly emitted `FINDING [name]`), that is
  a gap, not a build.
- no softened predicate to make a guard quiet (law 11), no deleted or
  loosened existing test. An existing test that goes red under your fix
  is a finding to report with its output — repair it only when the
  item's own done-criterion says that behaviour changes.
- no carrier writes: `ITEMS.md`, `ITEMS-DONE.md`, `LEDGER.md`,
  `JOURNAL.md`, `CLAUDE.md`, `arcs/`, `.claude/`, `docs/` stay
  untouched. No `item close`, `item amend`, `ledger add`. The desk books.
- no file outside your lane's write set. If the fix needs one, that is
  a gap.
- no hardcoded machine path, login or repo root (law 6).
- every hand-run `lifecycle` invocation carries
  `XDG_STATE_HOME=<your scratch>/state` so the live fire log is not written.
- if your fix changes what `lifecycle --test`, `lifecycle audit` or
  `lifecycle item check` say about THIS repo's own tree, paste before
  and after; never adjust the tree or the check to hide it.

## Lanes

Ids travel with a content anchor (the body's opening words); if the id
and the anchor disagree at your base, report it and work from the anchor.

**Lane A — migrate report truth.** Write set:
`plugin/cli/lifecycle_core/migrate.py`, `test/test_migrate.py`, and in
`plugin/cli/lifecycle_core/cli.py` ONLY the migrate subparser and its
dispatch (lane E edits other regions of that file in another worktree).
- lc-310 "`migrate --entry-shape` passed together with `--schema-from` is silently ignored"
- lc-85 "migrate's terminal summary prints CLEAN beside a reconciliation that can be 0 read == 0 written"
- lc-206 "THE MIGRATION REPORT'S CONSERVATION SENTENCE IS x == x"
- lc-207 "A FREEZE-BLOCKED WRITING RUN SAYS 'DRY RUN"
- lc-209 "THE MIGRATION REPORT RENDERS AN UNREADABLE ITEMS.md AS 'None yet"
- lc-213 "A --report-only RUN PRINTS 'items written: N -> ITEMS.md'"
- lc-210 "THE BLOCKER-TYPE TABLE IS A CHECK NO INPUT CAN FALSIFY"

**Lane B — the mutation prover.** Write set: `tools/prove-rows.py`,
`test/test_prove_rows.py`.
- lc-196 "THE BASELINE IS PRINTED AND NEVER GRADED, AND THE ROW NAME IS ONLY CHECKED FOR FINDINGS"
- lc-195 "THE PROVENANCE REFUSAL COVERS 12 OF 21 CORE MODULES"
- lc-221 "THE TWO ROWS ADDED 2026-09-18 HAVE NO RE-RUNNABLE ARRANGEMENT IN prove-rows"
  A new arrangement is admitted on a PAIR (CLAUDE.md, "A NEW ARRANGEMENT
  IS ADMITTED ON A PAIR"): real anchor → `rows changed: <the row>`; inert
  anchor → `rows changed: NONE` and FAIL. Both outputs quoted.

**Lane C — retire.** Write set: `plugin/cli/lifecycle_core/retire.py`,
`test/test_retire.py`.
- lc-149 "An EMPTY carrier counts as one instance"
- lc-187 "TWO BODIES BEHIND ONE CONTRACT DISAGREE ABOUT THE CASE THAT DECIDES A CLEAN BOARD"

**Lane D — verbs.** Write set: `plugin/cli/lifecycle_core/verbs.py`,
`test/test_verbs.py`.
- lc-50 "closed-ref: stores the caller's spelling verbatim, so `--ref HEAD` writes the literal string HEAD"
- lc-138 "the ledger verb commits its carrier WHOLESALE"
- lc-232 "`item park` REWRITES THE BASE `blocked-by:` SLOT"

**Lane E — cli reports and the leak-scan battery.** Write set:
`plugin/cli/lifecycle_core/cli.py` (NOT the migrate subparser or its
dispatch — lane A's), a NEW file `test/test_cli_walk_report.py` for
lc-107 and lc-108, and `test/absence-scan.test.mjs` for lc-147.
- lc-107 "audit and retire DISCARD every declaration-level finding whenever the declaration is READABLE"
- lc-108 "kind check's CLEAN line does not say how many git hooks it checked"
- lc-147 "THE LEAK SCANNER'S OWN BATTERY GIVES A DIFFERENT ANSWER IN A CLONE THAN IN THE REAL CHECKOUT"
  (verifier for this one: `node --test test/absence-scan.test.mjs`,
  baseline `62 pass, 0 fail, 0 skipped` per CLAUDE.md, measured there
  2026-09-18 — re-measure)

**Lane F — declaration, roster, items.** Write set:
`plugin/cli/lifecycle_core/declaration.py`, `plugin/cli/lifecycle_core/roster.py`,
`plugin/cli/lifecycle_core/items.py`, `test/test_declaration.py`,
`test/test_refusals.py`, `test/test_items.py`.
- lc-189 "THE PRODUCER ROUTE IS UNFALSIFIABLE IN ONE DIRECTION"
- lc-191 "THE EMIT-SITE SCAN STATES A LIMIT NARROWER THAN ITS PREDICATE"
- lc-190 "THE CONSERVATION SENTENCE CLAIMS MORE THAN THE SUM ESTABLISHES"
- lc-140 "Invariant 5 says every exit is recorded with its reason and its commit, but the done-home check does not enforce that for a DONE body"

## Verifier (in order; real output pasted in the report)

1. Per item: the red-first run against unmodified code, then the same
   test green after the fix.
2. `python3 -m unittest discover -s test -p 'test_*.py'` — full counts
   against your measured baseline, every skip dispositioned.
3. `XDG_STATE_HOME=<your scratch>/state python3 plugin/cli/lifecycle --test`
   — the closing counts line.
4. `python3 tools/prove-rows.py` once, at the end of the lane, with a
   long timeout (it mutates tracked files in YOUR worktree and restores
   them; if it is interrupted, `git status` must be clean before you
   commit anything further). Paste its closing summary. A row whose
   proof your change retired is a finding to report, not to repair,
   unless prove-rows.py is in your write set.
5. `node tools/absence-scan.mjs --git-range <BASE>..HEAD` — must be clean.

## Write boundaries

Your lane's write set above, nothing else. Not deployment-coupled and
not live on write: nothing executes from a lane worktree. Commit by
pathspec — `git commit -F <msgfile> -- <paths>`; a NEW file takes
`git add -N <file>` first. Never amend, never `--no-verify`, never
push, never `git config`, never `git remote`.

## Commit plan

Guards: the machine-wide `pre-commit` (read: `git config core.hooksPath`,
directory listed). No version bump is owed: no lane touches the plugin
manifest. One commit per item, title `lc-<N>: <what changed>`, body
naming the red-first test, trailer exactly
`Co-Authored-By: Claude <Sonnet 5.5 | Opus 5.5 — your own model> <noreply@anthropic.com>`.
Pre-authorized repair class: if `pre-commit` refuses a commit over its
MESSAGE form, read the refusal, satisfy it, and report the change as a
deviation. Any other refusal halts that item.

## Critique pass

Before your first build call, send ONE message on the report channel:
which Background line you find unopened or wrong, and which two lines
of this brief contradict each other ("none" is valid). Then continue
without waiting for a reply.

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

Per-item report rows carry one of: FIXED (commit) / NOT-REPRODUCED
(command + output) / GAP (what is missing, with evidence).
