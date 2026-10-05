# Brief: migrate stops minting an unclearable blocker (lc-308) and reads the slots an entry states under their label (lc-311)

Title: sonnet: migrate — parked blocker that can clear (lc-308), labelled slots travel (lc-311)
Working copy: this repo's main checkout (the dispatch prompt names the path).
Base check: `git merge-base --is-ancestor <base> HEAD` and
`git log --oneline <base>..HEAD`, where `<base>` is the commit that added
this file (the dispatch prompt names it). Base contained and nothing on top
that touches the two write-set files is the clean start; anything else is a
gap to report, never a rebase. Then `git status --porcelain` over the two
write-set files: a modified file there is a HALT.
Scratch: the agent's OWN scratchpad.

Two items, ONE lane, because both land in the same two files. They are built
and committed ONE AFTER THE OTHER — lc-308 complete and committed before
lc-311 is started — so each commit carries one change and its own red-first.

## Grounding basis — read before building; the report cites what was actually read

- the executor skill (`dispatch-guards:executor`) — load FIRST.
- `CLAUDE.md` — the `## Verify` section, and the conventions on comments and
  restated counts. This repo's comments carry the WHY of each rule; match
  their density and register in what you write.
- `ITEMS.md` — the blocks headed `## lc-308` and `## lc-311`, whole. Their
  done-criteria are what the desk closes them against.
- `plugin/cli/lifecycle_core/migrate.py` — `Entry`, `_read_heading_entries`,
  the comment block opening "§3.1's MIGRATION WRITE-RULES", `_ledger_storable`,
  `migration_blocker`, the three constants after it, `build_items`,
  `blocker_types`, and in `render_report` the blocker table and the section
  "What this migration does NOT carry".
- `plugin/cli/lifecycle_core/items.py` — `_is_unclearable_evidence` and the
  chain half of the blocker-graph check that calls it; `classify_write_set`.
- `test/test_migrate.py` — the existing cases around the parked-evidence
  blocker and around `--entry-shape heading`, as the idiom to match.

## Background (established; verify at the cited lines)

Each line was opened at the desk on 2026-10-05 at commit `cfcb3f9`, command
and hit beside it. Line numbers shift; the quoted text is the anchor.

- A PARKED entry naming missing evidence migrates with the blocker
  `evidence false  # the named missing evidence in the source body`.
  `grep -n PARKED_EVIDENCE_PREDICATE` over `plugin/` and `test/`: three hits —
  `migrate.py` (the return in `migration_blocker`, and the constant's
  definition) and one assertion in `test/test_migrate.py`. No other reader.
- `item check` reports that literal as a softlock. Read in `items.py`:
  `_is_unclearable_evidence` is true for the literal shell command `false`,
  and the chain half of the blocker-graph check emits
  `FINDING [blocker_softlock] a CHAIN terminating in a member that can NEVER
  CLEAR`. So the migrator's own output fails the tool's own check.
- The rule is restated in four places, all in `migrate.py`:
  `grep -n -i 'named missing evidence'` over `plugin/`, `docs/` and
  `CLAUDE.md` hits the write-rules comment (`PARKED with its named missing
  evidence -> KEEPS blocked-by: evidence`), the `why` string in
  `migration_blocker`, the constant, and one table row in `render_report`
  (`| PARKED carrying its named missing evidence | \`evidence\` |`). The two
  hits under `docs/` are a dated audit report and a dated directive: history,
  NOT to be edited.
- `build_items` writes `"write-set": UNKNOWN` and `"done-criterion": UNKNOWN`
  for every entry unconditionally (read at the `render_block` call).
- Under `--entry-shape heading`, `Entry.text` is the heading title followed
  by the whole body WHITESPACE-JOINED into one line
  (`pending.text = " ".join(pending.text.split())` in `close`). Paragraph
  boundaries do not survive in `text`. Nothing on `Entry` holds the raw body.
- `render_report`'s "does NOT carry" section says `goal` and `done-criterion`
  "are written `UNKNOWN`". After lc-311 that sentence is false for
  `done-criterion` where a label was read.
- Baseline, run at the desk at `cfcb3f9`: `python3 -m unittest discover -s
  test -p 'test_*.py'` → `Ran 1157 tests … OK`; `python3 plugin/cli/lifecycle
  --test` → `rows: 138   138 passed, 0 failed, 0 could not verify, 0 raised,
  0 skipped`, `CLEAN`.
- The label spellings lc-311 must read were counted over the motivating
  carrier (a private repo's backlog; counts only, no content travels here).
  Paragraph-opening forms seen: `*Write-set:*`, `**Write-set:**`,
  `*Done-criterion:*`, `**Done-criterion:**`, and the same with a full stop
  in place of the colon. A minority open with the label word followed by
  something else before the punctuation (a parenthesis, more words); those
  are deliberately NOT read — see the design.
- This repo is PUBLIC and its pre-push runs a leak scan. Fixture text is
  synthetic: no content copied from any other repo, no home-directory path.

## The settled design — implement exactly this, do not redesign

### lc-308 — a parked entry naming missing evidence gets a decision blocker

1. In `migration_blocker`, the branch `entry.grade_word == "PARKED"` and
   `_NAMED_EVIDENCE` matches returns `"decision " + PARKED_EVIDENCE_QUESTION`.
   The `_NAMED_DECISION` branch above it is unchanged and still tested first.
2. New module constant, placed where `PARKED_EVIDENCE_PREDICATE` stands,
   which is REMOVED:

       PARKED_EVIDENCE_QUESTION = ("the missing evidence named in the source "
                                   "body: state it as a predicate that can "
                                   "fire, then re-grade")

   The wording is fixed. It differs from `PARKED_DECISION_QUESTION` on
   purpose, so the two branches stay distinguishable in the carrier. It
   passes through `_ledger_storable` at the existing single call site in
   `build_items`; do not add a second call.
3. The `why` string of that branch says what is now true: the migrator cannot
   compose a predicate it could stand behind, the literal `false` it used to
   write is one `item check` proves can never clear, so the entry goes to the
   desk as a decision naming exactly what must be supplied.
4. The write-rules comment block is amended in place — its third row and the
   paragraph beneath it ("The third is the one that is easy to lose…") — to
   state the new rule and its reason. The old reasoning (a named-evidence
   entry is in the machine's court) is kept as what the rule USED to say and
   why it was wrong in effect: nothing ever evaluated the predicate.
5. The `render_report` table row for this branch is amended to the new type.
6. No new `FINDING` emit site. No roster row. `blocker_types` needs no change
   beyond what the type change gives it — confirm by reading it.

### lc-311 — a slot stated under its literal label travels

1. `Entry` gains one field, `body: str = ""`: the entry's raw body lines,
   joined with `"\n"`, exactly as read, heading line excluded. Populated ONLY
   by `_read_heading_entries` (accumulate `raw` where `text` accumulates
   `raw.strip()`); every other reader leaves it empty. Field comment in the
   register of its neighbours.
2. New function `labelled_slots(entry) -> tuple[dict, dict]` in `migrate.py`,
   placed directly above `build_items`. First value: slot name → value, for
   slots read. Second: slot name → count of labelled paragraphs found.
   - Empty `entry.body` → `({}, {})`. This is what keeps every bullet-shape
     run bit-for-bit what it was; lc-311 is scoped to the heading shape.
   - A PARAGRAPH is a maximal run of non-blank lines of `body`. Lines inside
     a fenced code block (between lines starting with three backticks) are
     never a paragraph start.
   - A paragraph is LABELLED when its first line, stripped, matches, case
     insensitively: start, zero to two of `*` or `_`, the literal
     `write-set` or `done-criterion`, zero to two of `*` or `_`, optional
     spaces, ONE of `:` or `.`, zero to two of `*` or `_`, then the rest.
     Anything between the label word and the punctuation other than emphasis
     marks and spaces means NOT labelled.
   - The value is the rest of that first line plus the paragraph's remaining
     lines, whitespace-collapsed to one line, stripped.
   - `write-set` only: every backtick is removed and ONE trailing full stop
     is removed. `done-criterion`: no change beyond the collapse.
   - A slot whose label opens exactly ONE paragraph, with a non-empty value,
     is returned. A slot labelled in two or more paragraphs is NOT returned —
     the tool does not choose between them. An empty value is not returned.
3. `build_items` calls it once per written entry and writes the returned
   value where one exists, `UNKNOWN` otherwise. `goal` stays `UNKNOWN`.
   `migration_blocker(e, slots_incomplete=True)` is unchanged: `goal` is
   still missing, so every migrated entry is still slot-incomplete.
4. Third answer, decided: if `items_mod`'s own parse or shape check of the
   rendered block refuses a slot VALUE this function produced, that slot is
   written `UNKNOWN` and counted as "labelled, not storable". Find out
   whether such a refusal exists by reading `items.py`; if none can fire on
   a one-line value, say so in the report with the read, and add no dead
   branch.
5. `render_report` gains, inside the "does NOT carry" section, the per-slot
   counts for the run: filled from the entry's own label; left `UNKNOWN`
   with no label; left `UNKNOWN` because labelled more than once; and the
   not-storable count if point 4 produced that branch. Zeros are printed.
   The sentence there saying `done-criterion` is written `UNKNOWN` is
   reworded so it is true. The counts are report lines, not findings.
6. Every entry counted is one `build_items` wrote. The three (or four)
   counts per slot sum to the number of items written; assert that in a
   test rather than stating it in a comment.

## Verifier (in order; real output pasted in the report)

1. Red-first, per item, by running the NEW tests against the OLD
   implementation: write the item's tests before its implementation, run
   them, paste the red. Never reach "old" by reverting the working tree.
   State the unmutated baseline first (the 1157 / 138 above, re-run by you).
   - lc-308: a parked source entry naming missing evidence, in BOTH entry
     shapes. Assert the migrated block's `blocked-by` is
     `"decision " + migrate.PARKED_EVIDENCE_QUESTION`; assert the string
     `evidence false` appears nowhere in the migrated carrier; assert the
     blocker-graph check over that carrier reports no `blocker_softlock`.
     The existing assertion on `PARKED_EVIDENCE_PREDICATE` pins the old
     behaviour: re-aim it, and name it in the report as re-aimed.
     A parked entry naming a missing DECISION still gets
     `PARKED_DECISION_QUESTION` — a control, must stay green throughout.
   - lc-311, fixtures in the heading shape: (a) both labels present once →
     both slots carry the entry's words; (b) no label → both `UNKNOWN`;
     (c) `write-set` labelled twice → `UNKNOWN`, counted as such, while that
     entry's singly-labelled `done-criterion` is still filled; (d) the label
     word followed by a parenthesis before the colon → `UNKNOWN`; (e) a
     label-looking line inside a fenced code block → not read; (f) each of
     the spellings listed in Background is read; (g) a `write-set` value in
     backticks with a trailing full stop comes out as a bare comma list that
     `items.classify_write_set` puts in its paths bucket; (h) a bullet-shape
     run over a fixture containing the same label text writes `UNKNOWN` for
     both — the scope control; (i) the counts identity of design point 6.
2. `python3 -m unittest discover -s test -p 'test_*.py'`
3. `python3 plugin/cli/lifecycle --test`
4. `python3 tools/prove-rows.py`
5. `node --test test/absence-scan.test.mjs` and
   `node tools/absence-scan.mjs --git-range ..HEAD`

Expected: 2 green with more than 1157 tests; 3 still `138 passed` and
`CLEAN` (no row was added); 4 and 5 as at baseline — run them at the base
commit first if their baseline output is needed for the comparison.

## Write boundaries

- Owned: `plugin/cli/lifecycle_core/migrate.py`, `test/test_migrate.py`.
  Nothing else. In particular NOT `ITEMS.md`, `ITEMS-DONE.md`, `LEDGER.md`
  — closing the two items is the desk's act, by the tool's own verbs — and
  not `docs/`.
- If a correct build needs a third file (`refusals.py`, `tools/prove-rows.py`,
  `cli.py`), that is a gap: finish what the two files allow, report the rest.
- Not deployment-coupled and not live on write: `migrate.py` runs only when
  the `migrate` verb is invoked. No other session writes this copy; the desk
  writes nothing in it until your report is booked.
- Commit by pathspec, both files named, every flag before `--`. Never amend.
  Commits stay unpushed; pushing is the desk's act.

## Commit plan

- Two commits, in this order: lc-308, then lc-311. Title idiom from this
  repo's log: `migrate: <what is now true, in a clause> (lc-308)`; the body
  says what changed, why, and how red was shown, with its counts.
- Trailer, exact: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`
- Guards, each with the read that found it:
  - `core.hooksPath` is set to a machine-wide hooks directory holding
    `pre-commit`, `pre-push`, `post-commit` (read: `git config
    core.hooksPath`, directory listed).
  - That `pre-commit` refuses a plugin-payload change without a version
    bump, and `migrate.py` is payload. It exempts a plugin absent from the
    installed roster. Observed: commit `458f3e2` changed `migrate.py`
    yesterday with no bump and landed. Derived, unverified: the same
    exemption holds for you. If it refuses, do NOT bump and do NOT use
    `--no-verify`: report the refusal text as a gap.
  - The same hook carries a carrier shape gate for `ITEMS.md` and its
    siblings; you touch none of them.
  - A repo-local `pre-commit` may be chained after it — unverified whether
    one is installed in this checkout. A red from it is a finding to report.

## Critique pass, before the first build call

Send ONE message on the report channel naming which Background line you
found wrong or could not confirm at its anchor, and which two lines of this
brief contradict each other — "none" is a valid answer for either. Then
continue without waiting for a reply.

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
