# Brief: the head pass names every item whose evidence has arrived (lc-313)

Title: opus: item ready --head reports arrived evidence (lc-313)
Working copy: this repo's main checkout (the dispatch prompt names the path).
Base check: `git merge-base --is-ancestor <base> HEAD` and
`git log --oneline <base>..HEAD`, `<base>` being the commit that added this
file (named in the dispatch prompt). Base contained and nothing on top is the
clean start; anything else is a gap to report. Then `git status --porcelain`
over the write set: a modified file there is a HALT.
Scratch: the agent's OWN scratchpad; every scratch file name carries `lc313`.

## Grounding basis — read before building; the report cites what was actually read

- the executor skill (`dispatch-guards:executor`) — load FIRST.
- `CLAUDE.md` — the `## Verify` section, law 22, and the paragraph headed
  "the two exit-code contracts".
- `ITEMS.md` — the block `## lc-313`, whole. Its done-criterion is what the
  desk closes against.
- `plugin/cli/lifecycle_core/verbs.py` — `cmd_item_ready`, `cmd_item_head`,
  `_head_of`, `cmd_item_statusline`, and the function holding the text
  "evaluated like a trigger" (the per-item blocker verdict).
- `plugin/cli/lifecycle_core/lanes.py` — `evaluate_trigger` and
  `TRIGGER_TIMEOUT_S`.
- `test/test_verbs.py` — the existing `item ready` cases, as the idiom.

## Background (established; verify at the cited lines)

Opened at the desk on 2026-10-05 at commit `1cf9f0e`; quoted text is the
anchor, line numbers drift.

- The per-item verdict already evaluates an evidence blocker through the one
  shared evaluator: `t = lanes.evaluate_trigger(detail, cwd=ctx.repo)`, then
  `FIRE` → "UNBLOCKED — the evidence predicate (…) FIRED (exit 0)", `QUIET` →
  "BLOCKED — in the MACHINE's court: … Re-evaluated each pass.", else
  `FINDING [trigger_broken]` (read in `verbs.py`).
- `item ready --head` lists READY items only. Measured on a scratch carrier
  at `a0da4cc`: one item parked on `evidence test -e <flag>`; with the flag
  present `item ready <id>` printed the FIRED line, and `item ready --head`
  printed "head: 0 READY, 0 schedulable now. 79 live item(s) in total." and
  never named the item.
- No other surface named it in that state: `item statusline` printed
  `0R.3P head -`; `item check` printed only the exercised/unexercised count
  for evidence blockers; `audit` did not name it. Not searched beyond those
  four: a verb I did not try may report it — if you find one, say so first.
- A session-start hook outside this repo runs `item ready --head` and shows
  its output, so whatever the head prints is what a session sees unprompted
  (read: the hook's line `ready (lifecycle item ready --head):`). Unverified:
  whether that hook truncates long output.
- Baseline at `1cf9f0e` minus two ledger lines, run at the desk at `a0da4cc`:
  unittest `Ran 1184 tests … OK`; `--test` CLEAN.

## The settled design — implement exactly this, do not redesign

OUTCOME, stated before its sites: after this change, a session that does
nothing but read the head pass learns of every item whose wait is over.

1. `item ready --head` evaluates the EFFECTIVE blocker of every live item
   whose grade is not READY and whose effective blocker is typed `evidence`.
   It uses the existing per-item verdict function and therefore the existing
   single evaluator. No second evaluator, no second mapping of exit codes.
2. For each such item whose predicate FIRES: one line naming the item id,
   its grade, the predicate, and that a re-grade is owed at the desk. Placed
   after the READY listing, under its own one-line heading.
3. One count line, ALWAYS printed, zeros included: how many evidence
   predicates this pass ran, how many fired, how many were quiet, how many
   were broken. The four numbers sum; assert that in a test.
4. QUIET items are counted and not listed.
5. BROKEN is never skipped: it goes out through the same `trigger_broken`
   finding text the per-item verdict already produces, and the head's exit
   code follows what that verdict returns for a single item. A FIRED
   predicate does NOT change the exit code: it is information, not a finding.
6. Items blocked on `decision`, `item` or `external`, and READY items, are
   not evaluated here; the head's existing output for them is unchanged.
   With zero evidence-blocked items the only new output is the count line.
7. `--goal` restricts this listing exactly as it restricts the READY one.
8. `item statusline` is OUT of scope and must not start running predicates:
   it is a per-prompt render.
9. Cost is bounded by the evaluator's existing timeout per predicate. Do not
   add caching, a cap, or a flag to skip the evaluation.
10. If the head now reaches a FINDING emit site it did not reach before, the
    repo's own emit-site coverage and route-set checks (`--test`) say whether
    a roster row or arrangement is owed. Follow them; that is the one case in
    which the write set below widens, and it is pre-authorized (see Write
    boundaries).

FREEZE READING, the desk's: a defect repair under LEDGER:147 — the tool
already says such a predicate is "Re-evaluated each pass" and the only pass
that runs unprompted does not evaluate it. If the code shows this reading is
wrong (the head was scoped to READY by a recorded decision, say), STOP the
build, report that with the line, and commit nothing.

## Verifier (in order; real output pasted in the report)

1. Red-first by running the NEW tests against the OLD implementation, never
   by reverting the tree. State the unmutated baseline first.
   - a fixture carrier with one PARKED item on `evidence test -e <flag>`:
     flag absent → not listed, counts say 1 ran / 0 fired / 1 quiet; flag
     present → listed by id, 1 fired. This pair is the red.
   - a predicate that exits 2 → reported as broken, counted, exit code as
     the per-item verdict gives.
   - controls that must stay green throughout: a READY item with `NONE`; a
     `decision`-blocked NEW item (not evaluated — prove it with a marker
     file its question text would create if executed); a NEW item (not
     PARKED) on a fired evidence predicate is listed too; `--goal` filters.
   - the sum identity of design point 3.
2. `python3 -m unittest discover -s test -p 'test_*.py'`
3. `python3 plugin/cli/lifecycle --test`
4. `python3 tools/prove-rows.py`
5. `node --test test/absence-scan.test.mjs` and
   `node tools/absence-scan.mjs --git-range origin/main..HEAD`
6. `python3 plugin/cli/lifecycle item ready --head` in this repo itself,
   output pasted: it now runs this repo's own evidence predicates.

## Write boundaries

- Owned: `plugin/cli/lifecycle_core/verbs.py`, `test/test_verbs.py`.
- Pre-authorized widening, only where step 10 demands it:
  `plugin/cli/lifecycle_core/refusals.py`, `tools/prove-rows.py`. Report it
  as a deviation with the check output that demanded it.
- NOT yours: `ITEMS.md`, `ITEMS-DONE.md`, `LEDGER.md`, `docs/`, the session
  hook outside this repo. Closing lc-313 is the desk's act.
- LIVE ON WRITE: the `lifecycle` command on this machine resolves to this
  checkout, and session-start hooks in other repos call `item ready --head`.
  A half-written `verbs.py` breaks those sessions' start. Keep the file
  importable at every save: build the new function complete before wiring
  the call, and run `python3 plugin/cli/lifecycle item ready --head` after
  each edit of `verbs.py`.
- No other session writes this copy; the desk writes nothing here until your
  report is booked. This repo is PUBLIC: fixtures synthetic, no home paths.
- Commit by pathspec, every flag before `--`. Never amend. Unpushed.

## Commit plan

- One commit: `item ready --head: name every item whose evidence has
  arrived (lc-313)`; body says what changed, why, how red was shown.
- Trailers, BOTH lines, exact:
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` and the
  `Claude-Session:` line the dispatch prompt gives you.
- Guards (read: `git config core.hooksPath` → a machine-wide hooks dir;
  its pre-commit refuses a plugin-payload change without a version bump but
  exempts a plugin absent from the installed roster — observed on six
  payload commits here today with no bump). If it refuses: no bump, no
  `--no-verify`, report the text.

## Critique pass, before the first build call

ONE message: which Background line you found wrong or could not confirm, and
which two lines of this brief contradict each other. "None" is valid. Then
continue without waiting.

## Tail

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
