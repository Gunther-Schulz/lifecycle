# opus: lc-294 build — the STANDBY grade, `item bench`, and two triggers

Working copy: this repo's checkout (the dispatcher's working copy). Base check, FIRST ACT:
`git merge-base --is-ancestor <base> HEAD`, `git log --oneline <base>..HEAD`,
`git status --porcelain`. Base = the commit that adds THIS FILE (run
`git log -1 --format=%h -- docs/directives/2026-09-25-lc294-build-brief.md`).
Anything on top of it, or a dirty tree: HALT and report. The dispatcher
(desk lifecycle-d8) writes nothing in this checkout while you run.
Scratch: your OWN scratchpad only.

## Grounding basis — read before building; the report cites what was read

- the executor skill (`dispatch-guards:executor`) — load FIRST
- `docs/directives/2026-09-25-lc294-third-grade-design.md` — the design; §6's
  questions are RULED below, and where the two differ THIS BRIEF WINS
- `CLAUDE.md` of this repo — laws 2, 8, 10, 11, 22, 24, 26; the Verify block
- `plugin/cli/lifecycle_core/vocab.py` — the registered-closed-vocabulary
  contract (D-3): members are MINTED from recorded reasons
- `plugin/cli/lifecycle_core/items.py:62-64` (GRADES), `census` (~2259),
  the unknown-grade handling it feeds
- `plugin/cli/lifecycle_core/verbs.py` `cmd_item_park` (~2183) — the model for
  `item bench`; `cmd_item_promote` (~1500-1560); `_net_growth` and
  `_carrier_flow_at` (the lc-291 window cuts, ~1660-1790) — the window you REUSE
- `plugin/cli/lifecycle_core/cli.py` ~933 (park's subparser), ~1284 (the action
  tuple), `_carrier_verb` (~1448)
- `test/test_verbs.py` — its hand-written dispatch table DERIVES the action
  tuple; it must move with a new verb (law 24's worked example, lc-120)
- `plugin/cli/lifecycle_core/declaration.py` — how optional keys are declared
  and validated (`closure_words` / `_validate_closure_words`, ~691-780, is the
  existing optional-key instance to copy)
- `arcs/answerable.md`, `arcs/drift-trigger.md` and `lifecycle arc status` —
  what an OPEN arc is

## Background (established; each opened by the dispatcher at brief time)

- `grep -c grades_extra` over every roster repo's `.claude/lifecycle.json`: 0
  (no repo declares it today). Roster: `~/.config/lifecycle/repos`.
- The demote predicate, computed by the dispatcher at bdd4560 with a scratch
  script over git cuts: lifecycle 84 READY, HEAD 2 (arc-cited), unscheduled 82,
  READY exits over 7 days 22 → FIRES. Over the 10 roster repos without the idle
  rule it fired in 9, idle repos included (dispatch-guards 11 READY / 0 exits)
  — hence ruling (a) below.
- PRE-BUILD outputs for the byte-identity pair are ALREADY CAPTURED, before any
  code change, at
  the dispatcher's scratchpad under `lc294/pre/` (path given in the dispatch message; it carries a session id and stays out of history):
  `dg-item_check.txt`, `dg-item_ready___head.txt`, `dg-item_ratio.txt`
  (dispatch-guards, which declares nothing; rc 2 / 2 / 0), and
  `scratch-standby-check.txt` (a scratch undeclared repo whose block is
  hand-graded STANDBY: rc=3, "unknown grade 'STANDBY': 1"). READ them; do not
  regenerate them.

## The settled design — implement exactly this, do not redesign

1. **Mint `STANDBY` into `items.GRADES_OPEN`** (after PARKED). Its reason
   travels in the vocab registry entry for "grades" (vocab.py): state that
   STANDBY was minted 2026-09-25 from LEDGER.md's decision "operator: grant a
   freeze exception for the third READY grade and its demote and return
   triggers" (LEDGER:159), meaning decision-complete but not on the scheduled
   head. Use an existing field or add one; the reason must be readable from the
   registry at run time, not only a comment.
2. **Declaration key** `"grades_extra": ["STANDBY"]`, OPTIONAL (no schema bump,
   §3.8c — copy the `closure_words` optional-key pattern). Only the member
   `STANDBY` is accepted in it; anything else is a declaration finding.
   Declare it in THIS repo's `.claude/lifecycle.json`.
3. **`item bench <id> --reason <why>`**: READY → STANDBY. Modeled on `item
   park`: tool-written, committed through `commit_paths`, `--no-commit`
   supported, `--reason` REQUIRED and recorded on the block (an amend-style
   `bench-reason:` line, dated, like `promote-reason:`). Refuses (FINDING):
   the repo does not declare STANDBY; the item is not READY; no reason.
   Wire it: subparser, the action tuple, `_carrier_verb`, `test_verbs.py`'s
   table.
4. **`item promote` accepts STANDBY as a source grade** (STANDBY → READY, the
   return move), with its existing required `--by`/`--reason`.
5. **`item check` refusal `standby_undeclared`**: a block graded STANDBY in a
   repo whose declaration lacks it is a FINDING naming the block. (Today such a
   block is counted "unknown grade", exit 3.)
6. **Readers** (the gains-a-value sweep — enumerate FROM SOURCE, not from this
   list): STANDBY is OPEN everywhere a reader asks open/closed (census, the
   intake join's live set, conservation, waves); `item ready --head` never
   lists it; blocker-target resolution treats a STANDBY target like any open
   one; the statusline counts it (say how). Every site that reads the grade
   vocabulary gets one line in the reader table (Verifier step 6).
7. **Two FINDINGs from `item ratio`**, evaluated ONLY when the repo declares
   STANDBY, over the SAME cuts `_net_growth` uses (reuse; never a second
   window constant):
   - `ready_outgrows_head`: HEAD := READY items whose id appears in the body
     of an OPEN arc. FIRES when (READY − HEAD) > (ids READY at the window's
     start cut that are not READY now).
   - `head_draining`: FIRES when HEAD is empty while STANDBY holds items, or
     HEAD shrank in both window halves while STANDBY holds items. Where arc
     history does not cover the window (the arcs kind has no file at the start
     cut), this is COULD NOT VERIFY naming that reason — the three-answer
     contract, stated verbatim in the output.
   - IDLE RULE (ruling a): no capture and no drain over the window → CLEAN
     "no flow", never either finding. Reuse `_net_growth`'s movement test.
   - Neither trigger moves anything. Their text names the owed pass: `item
     bench` / `item promote`, each with its reason.
8. **Law 24**: `refusals.py` gets rows `standby_undeclared`, `bench_undeclared`
   (bench refused without the declaration), `ready_outgrows_head`,
   `head_draining`, each with plant + control; `tools/prove-rows.py` gets an
   arrangement per row, each ADMITTED ON A PAIR (lc-142: real anchor PROVEN,
   inert comment-line anchor FAILED with "rows changed: NONE"), both outputs
   quoted in the report.

## Verifier (in order; real output pasted in the report)

1. Red-first per new row: the plant run against the PRE-change code fails for
   the stated reason (assertion, never an import error — law 4); arrangement
   stated.
2. The HARD-NEGATIVE PAIR (judge demand 3): (i) the scratch undeclared repo
   with a hand-graded STANDBY block: pre-build output (the captured file) BESIDE
   post-build output (`FINDING [standby_undeclared]`); (ii) dispatch-guards run
   through `item check`, `item ready --head`, `item ratio` post-build, `diff`ed
   against the three captured pre-build files — byte-identical, or every
   differing line explained.
3. Natural red: `lifecycle item ratio` in THIS repo at your final commit FIRES
   `ready_outgrows_head`; quote it.
4. Containment: `item ratio` over all 10 roster repos; the set firing either
   new finding must be exactly the declaring repos with flow (expected:
   lifecycle alone); quote the per-repo line.
5. The Verify block from CLAUDE.md, every exit code read without a pipe:
   unittest suite (count, and skips vs the 1094 baseline), `--test`,
   `tools/prove-rows.py` (PROVEN count ≥ 114, 0 FAILED), `audit` (rc=3 with 5
   COULD NOT VERIFY lines is the pre-existing baseline), `node --test
   test/absence-scan.test.mjs`, `node tools/absence-scan.mjs --git-range ..HEAD`.
6. The READER TABLE: append a section "## Reader table (build)" to
   `docs/directives/2026-09-25-lc294-third-grade-design.md`, one row per site
   that reads the grade vocabulary, derived by a grep you quote (constants AND
   literals), each with file:line and its STANDBY treatment. migrate.py's
   legacy-word mappings may be one row with the reason they never emit a live
   STANDBY.

## Write boundaries

Owned: `plugin/cli/lifecycle_core/{items,verbs,cli,declaration,refusals,vocab}.py`,
`tools/prove-rows.py`, `test/test_items.py`, `test/test_verbs.py`,
`test/test_declaration.py`, `.claude/lifecycle.json`,
`docs/directives/2026-09-25-lc294-third-grade-design.md`, and `CLAUDE.md`
ONLY for one pointer line if a fresh reader of `item check`'s census would
otherwise be surprised by STANDBY (your call; say which). NOT ITEMS.md,
ITEMS-DONE.md, LEDGER.md — the bench pass and the close are the desk's.
Not deployment-coupled; no written path is live on write (the lifecycle CLI
resolves through `~/.local/bin/lifecycle` → this checkout, so a commit here IS
what later invocations run — run the suite before each commit).

## Commit plan

Guards, read at brief time: `core.hooksPath` = `~/dev/Gunther-Schulz/dotfiles/git/hooks`
(pre-commit: the carrier shape check over staged carriers; post-commit;
pre-push: the leak scan + suite — you do not push). No payload-version guard.
Commit by pathspec, several commits fine (code+tests together per step).
`--no-verify` is NEVER taken. Never amend. Trailer:
`Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.

## Gaps and critique

Before your first build call, send ONE message: which Background line you
find unopened or wrong, and which two lines of this brief contradict each
other; then continue without waiting. A missing decision, file or value is
surfaced as a gap, never bridged with a guess.

## Report tail (EXECUTION, pasted verbatim)

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
    Report channel: SendMessage to the dispatcher — your final text reaches no one.
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
