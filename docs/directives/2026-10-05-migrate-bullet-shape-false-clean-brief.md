# Brief: `migrate` under the bullet shape reports CLEAN over a carrier it read nothing from

Title: opus: migrate bullet-shape false clean
Dispatcher: lifecycle desk (session lifecycle-b5), 2026-10-05, from trial T7
of the gap sweep (`docs/audits/2026-10-05-gap-sweep-trials.md`).

Working copy: /home/g/dev/Gunther-Schulz/lifecycle (the real checkout, shared
with the dispatcher, who writes only under `docs/` while you run).
Base check, your first act: `git merge-base --is-ancestor b1a73d2 HEAD` must
succeed, and `git log --oneline b1a73d2..HEAD` may show only commits that
leave your four files untouched (the commit adding this brief is one). Then
`git status --porcelain -- plugin/cli/lifecycle_core/migrate.py plugin/cli/lifecycle_core/refusals.py tools/prove-rows.py test/test_migrate.py`
must be empty. Anything else: report it as a gap and stop.
Scratch: your OWN scratchpad; any file you put in a shared directory carries
the prefix `migbullet-`.

Environment, in every shell command that runs a `lifecycle` verb or a test
outside the suite's own isolation:
    export XDG_STATE_HOME=<a directory in your scratchpad>
    export LIFECYCLE_COMMIT_TRAILER=$'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01YMV14w73dgk3XgQRvvxz5o'
Unset, every verb appends to the operator's real fire log.

## Grounding basis — read before building; the report cites what was actually read
- `CLAUDE.md` of this repo: laws 1, 2, 3, 4, 11, 22, 24 and the whole `## Verify` section (the PAIR rule for a new prove-rows arrangement is there).
- `plugin/cli/lifecycle_core/migrate.py`: `read_carrier` (the bullet reader), `_bullet_shape_note`'s neighbourhood (the existing NOTE), and in `run` the refusal `migration_heading_shape_empty` — your new refusal sits directly beside it.
- `plugin/cli/lifecycle_core/refusals.py`: the row `migration_heading_shape_empty` and `_migrate_run`.
- `tools/prove-rows.py`: the arrangement for `migration_heading_shape_empty`.
- `test/test_migrate.py`: classes `HeadingShapeOverNoHeadings` and `BulletShapeNote`.

## Background (established; verify at the cited lines)
- MEASURED by the dispatcher at b1a73d2, scratch repos, real CLI: a carrier whose entries are four `### ` headings, migrated with the default shape, printed `source entries read: 0`, `items written: 0`, `migrate: CLEAN`, exit 0, wrote an empty `ITEMS.md` and put the freeze banner on the source. The mirror case (a bullet carrier under `--entry-shape heading`) is refused: `COULD NOT VERIFY [migration_heading_shape_empty]`, exit 3, nothing written.
- MEASURED, same run: in a bullet carrier, a line `* **READY — zeta: starred bullet**` was not read as an entry; its text was appended to the requirement of the entry above it. The report's bullet identity counted 6 top-level bullets where the file has 7 list lines. Nothing in stdout or the report mentions the line.
- Read at b1a73d2: `_BULLET = re.compile(r"^- (.*)$")` (migrate.py:248); the heading-shape refusal at migrate.py:2798-2810; its row at refusals.py:2614; its arrangement at tools/prove-rows.py:632; the existing bullet-shape NOTE fires only when `read.entries_under_level3` is non-zero, so it is silent when zero entries were read.
- MEASURED: a plain `- ` bullet that is neither bold nor grade-led is NOT silent — the report counts and lists it as prose. That path is correct and must not move.

## The settled design — implement exactly this, do not redesign

TWO changes, one commit each, in this order.

### Change 1 — a new refusal: `migration_bullet_shape_empty`
- OUTCOME: a `bullet` read (the default shape included) that found ZERO entries in a source carrier which shows that the declared shape does not match it answers COULD NOT VERIFY, exit 3, and writes NOTHING — no successor home, no report, no banner on the source; the source bytes are unchanged.
- "Shows that the shape does not match" is exactly: the read holds at least one level-3 heading (`read.level3_headings`), OR at least one top-level line opening with `* ` or `+ ` (the new `read.other_marker_lines` of Change 2 — so Change 1's condition uses a count you add to `Read` in THIS commit; Change 2 then adds the reporting of it).
- SITE: in `run`, immediately after the `migration_heading_shape_empty` block, before anything is written. Same "nothing has been written yet" position.
- TEXT: `COULD NOT VERIFY [migration_bullet_shape_empty] ` followed by a sentence saying that the `bullet` shape (which is the default) read zero entries from <source name>, which holds N level-3 heading(s) and M line(s) opening with `* ` or `+ `; that zero entries is a number shaped exactly like a clean migration; that nothing was written; and the two repairs: `--entry-shape heading` if its entries are its level-3 headings, and that this shape reads `- ` as the bullet if they are list lines under another marker.
- MUST-NOT-MOVE, each with a test: (a) a bullet carrier with at least one entry migrates exactly as before, whatever headings or other markers it also holds; (b) a carrier with zero entries and NEITHER signal — an empty carrier, or one holding only plain `- ` prose bullets — still migrates CLEAN as before.
- The line counted for `other_marker_lines`: a top-level line matching `^[*+] ` under the bullet shape, EXCLUDING a horizontal rule (a line that is only three or more `*` with optional single spaces between). Collected as `(lineno, section)` like `non_entry_bullets`. READING SEMANTICS DO NOT CHANGE: the line still falls through to the body rule exactly as today.
- REGISTRY (law 2): a row `migration_bullet_shape_empty` in `refusals.py` beside the heading one; `expect=exits.COULD_NOT_VERIFY`; fire = `_migrate_run` over a carrier whose only content under `## Open` is one `### ` heading with a body line; control = the SAME carrier with one bold `- ` entry added, which must migrate (the arms differ in whether the bullet shape finds an entry, and in nothing else).
- PROOF: an arrangement in `tools/prove-rows.py` that replaces your condition line with `if False:` — the verdict moves 3 to 0. Admit it on the PAIR the laws file requires: once at the real anchor (`rows changed:` your row), once re-pointed at an inert comment line (must FAIL with "the row did NOT change"). Quote both in the report. `prove-rows.py` refuses to start while a file it mutates differs from HEAD, so it runs AFTER your commit; if it fails, the repair is a NEW commit.

### Change 2 — the other-marker lines are SAID
- OUTCOME: in a bullet read that DID find entries, top-level `* ` / `+ ` lines are no longer silent.
- STDOUT: one line, printed where the existing bullet-shape NOTE is printed, only when the count is non-zero: `NOTE: N line(s) in <source name> open with "* " or "+ " (first at line L). The bullet shape reads "- " as the bullet, so these were read as BODY of the entry above them, not as entries.` A NOTE: no exit-code change, nothing else written.
- REPORT: one row in the counts table directly under the non-entry prose row — top-level lines opening with `* ` or `+ ` (read as body, not as entries) and the count, printed also when it is zero — and, when non-zero, a short list of their line numbers and sections in the manner of the `Non-entry bullets` section.
- The report's existing bullet identity (`N top-level bullets = entries + prose + cut`) is NOT changed: these lines are not `- ` bullets and stay outside it; the new row is what makes them visible.

## Verifier (in order; real output pasted in the report)
1. RED-FIRST, the arrangement stated: your new tests run against the migrate.py of your base commit (a scratch copy of `plugin/` and `test/` with only that file taken from the base), each new assertion failing on the defect and not on an import error (law 4). Then green on your tree.
2. `python3 -m unittest discover -s test -p 'test_*.py'` — the dispatcher's baseline at b1a73d2 is `Ran 1206 tests ... OK` with no skips; report your full counts.
3. `python3 plugin/cli/lifecycle --test` — baseline `rows: 138 ... lifecycle --test: CLEAN`; yours must be CLEAN with 139 rows.
4. After each commit: `python3 tools/prove-rows.py` — last line "every recorded arrangement held".
5. Effect site: build a scratch git repo holding a `BACKLOG.md` whose entries are `### ` headings, run `lifecycle init` and `lifecycle migrate` there with the default shape, and paste the exit code, the stdout, and `git status --short` of that repo (expected: exit 3, your refusal text, no `ITEMS.md`).

## Write boundaries
You own exactly: `plugin/cli/lifecycle_core/migrate.py`, `plugin/cli/lifecycle_core/refusals.py`, `tools/prove-rows.py`, `test/test_migrate.py`. Nothing else in the repo; no carrier (`ITEMS.md`, `LEDGER.md`), no docs. If the build cannot be completed inside those four files, that is a gap to report with the file named, not a file to edit.
NOT deployment-coupled. LIVE ON WRITE: yes, in one respect — `cli.py` imports the package, and every session-start hook on this machine runs this checkout's CLI, so a `migrate.py` or `refusals.py` that does not import breaks session start everywhere. Land multi-hunk changes to one file as ONE write, and run `python3 -c "import sys; sys.path.insert(0,'plugin/cli'); import lifecycle_core.cli"` after every save.
Never push. Never `--no-verify`.

## Commit plan
Guards, read by the dispatcher: `git config --global core.hooksPath` = `~/dev/Gunther-Schulz/dotfiles/git/hooks` (pre-commit, post-commit, pre-push); the pre-commit runs the item-carrier shape check, which your write set does not touch. No version-bump guard in this repo (read: no manifest version check among those hooks' printed lanes — from their output on the dispatcher's own commits today, the hook files themselves unopened, unverified). Two commits, Change 1 then Change 2, each `git commit -F <message file> -- <paths>`. Message style: this repo's — a title naming the behaviour, then WHAT / WHY / RED paragraphs (see `git log -3`). Both trailers on each commit:
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
`Claude-Session: https://claude.ai/code/session_01YMV14w73dgk3XgQRvvxz5o`

Before your first build call, send ONE message on the report channel naming any Background line you found wrong or unopened and any two lines of this brief that contradict each other ("none" is an answer), then continue without waiting for a reply.

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
(the report channel line is in your dispatch prompt)
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
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
Never amend — always a new commit: the amend-gate denies
subagent amends regardless of ownership (source: §1 amend
rule).
After sending the report your write grant is over: a defect you
find later is REPORTED, never edited or amended (source: §4
ownership rule).
