# Brief: the close statement and the deletion-side check, into the real tool

Written 2026-10-05 by the lifecycle desk (session lifecycle-03). Authority:
LEDGER.md:199, the operator's release of the 2026-09-24 freeze for these two
mechanisms only, stated first-hand in this desk's session as well. Evidence
and the trial numbers: `docs/audits/2026-10-05-gap-sweep-followup-trials.md`,
sections F2 and S1.

The dispatch prompt names the working copy, the scratch directory (SCRATCH)
and the state directory; none of them is written here, because this tree is
public.

## Grounding basis — read before building; the report cites what was read

- The executor's working copy's CLAUDE.md: laws 1, 2, 4, 8, 11, 24, 26, the
  two exit-code contracts, and the whole Verify section (the PAIR rule for a
  new arrangement, the sibling-row rule, "adding a row can retire a
  neighbour's proof").
- `plugin/cli/lifecycle_core/verbs.py`: `cmd_item_close`, `commit_paths`,
  `cmd_item_amend` (the re-typing door that clears a conditional slot),
  `cmd_item_repair`. `items.py`: the done-only slot vocabulary and its order
  check, `check_staged` and `Finding.identity`, `BLOCKER_ONLY_SLOTS`.
  `refusals.py`: the roster form, `Row.finding_row`. `tools/prove-rows.py`.
- `declaration.py`: how the optional key `grades-extra` is read and
  validated (`GRADES_EXTRA_KEY`); it is the precedent for part B's key.
- The prototype of part A, a patch against commit `347431a`:
  `$XDG_STATE_HOME/claude/gap-sweep-2026-10-05/followup/prototype-PD.patch`.
  The replay script of part B's predicate: `scan-s1.py` with
  `scan_common.py` in the same directory.

## Background (established; verify at the cited lines)

- OPENED by the dispatcher, a script over every `.py/.sh/.fish/.mjs/.js/.json`
  file of the ten governed repos (6025 files; control: 16 files call
  `item ready`): nothing outside this repo's own code and tests invokes
  `item close` programmatically. The other hits are prose in declarations
  and one hook message. So the callers are sessions, who meet the refusal.
- OPENED: the machine-wide commit hook runs THIS checkout's
  `item check --staged` for every governed repo and blocks on exit 2. So a
  finding part B adds to the staged check is live for every repo the moment
  it lands, and a test that needs the gate installs its own hook running the
  working copy's CLI (the repo's fixtures neutralise hooks).
- OPENED: the repo-local hook's text names "a DECLARED exemption in the
  declaration" for a deliberate hand edit; a search of `lifecycle_core` and
  the declaration for `exempt` finds no such key. The exemption is promised
  in prose and does not exist.
- From the S1 scan (a lane's script, its 26 listed commits grouped by this
  desk, three opened): over 1383 commits touching an item carrier, a line
  other than `grade:` / `blocked-by:` left a still-live block in 26 commits:
  8 removed only a `not-derivable:` line (tool-written, on a re-typing), 4
  were bulk rewrites, 14 were in-place hand edits. Whether every one of the
  8 also changed the block's blocker TYPE in the same commit is UNVERIFIED.
- From the F2 trial: the prototype's slot order is closed-reason,
  closed-met, closed-decided, closed-ref; it edited 68 `item close` call
  sites (12 in refusals.py, 56 in tests). Read at the patch, not re-counted.

## The settled design — implement exactly this, do not redesign

### Part A — `item close` demands two statements (port the prototype)

As trialled. The DONE close (a drop is untouched) refuses unless both are
given: `--met "<none | item ids booked, or commits that fixed, whatever was
met while working that was NOT this item>"` and `--decided "<none | the
ledger decision lines written for a choice this work made>"`. `none` passes
for either: the slot demands the statement, never the answer. Tokens are
validated (an item id exists in either home; a commit resolves; a ledger
reference names a `decision:` line). Refusals `close_statement_missing` and
`close_statement_unresolved`, exit 2, nothing written, the missing-statement
text verbatim from the prototype. On success the closed body carries
`closed-met:` and `closed-decided:`; closed bodies written before this
change are NOT findings for lacking them.

Two things the prototype did not settle, settled here:

- The ledger reference is `<the ledger home's file name as the declaration
  gives it>:<line>`, never a hardcoded `LEDGER.md`.
- The item-id token accepts the repo's declared prefix (the prototype
  accepted any `<prefix>-<n>`): an id of another repo is not resolvable
  here and is refused as unresolved, with a sentence saying a cross-repo
  item is named in the reason text instead.

### Part B — the staged check refuses a line removed from a live block

In `check_staged`, over the LIVE home only: for every item id that is live
in both the HEAD body and the staged body, every line of its HEAD block that
is absent from its staged block (multiset; an in-place edit is a removal
plus an addition) is a finding `live_block_line_removed`, exit 2, naming the
item, the slot prefix and the first 80 characters of the removed line. One
finding per item, listing its removed lines.

Exemptions, each verified by the gate in data it reads (law 11), each
COUNTED in the check's output when it applies, never silent:

1. A `grade:` line or a `blocked-by:` line: the tool rewrites these in
   place.
2. A conditional slot (`BLOCKER_ONLY_SLOTS`) removed in a block whose
   effective blocker TYPE differs between HEAD and staged: the re-typing
   door clears it.
3. The tool's own commit: `commit_paths` sets `LIFECYCLE_WRITER_VERB=<verb>`
   in the environment of the `git commit` child it starts, and the gate
   exempts a staged carrier when that variable names one of the verbs that
   LEGITIMATELY remove such lines. Which verbs those are is not assumed:
   a test runs every carrier-writing verb over a fixture and applies part
   B's predicate to its write; the set that fires is the list, expected to
   be `item repair` and `migrate` and nothing else. If another verb fires,
   that is a gap to REPORT with the fixture, not an exemption to add. This
   exemption is forgeable by setting the variable by hand, so its roster
   entry is labelled PROSE-REST for that reach.
4. A declared rewrite: the STAGED declaration carries, under a new optional
   top-level key `carrier-rewrites`, an entry `{"carrier": "<repo-relative
   path>", "date": "<today, ISO>", "reason": "<non-empty>"}` that HEAD's
   declaration does not carry. That is the declared exemption the hook's
   own text promises. The key is validated like `grades-extra` (optional,
   shape-checked, an entry with an empty reason or a carrier that is not a
   declared item home is a finding); entries are a record and are never
   removed. No schema bump: the key is optional, as `grades-extra` is.

The finding's text names all three routes that are open to its reader: the
verb that owns the change (`item amend` appends and retains), the declared
rewrite for a deliberate bulk edit, and never `--no-verify`.

`item check` without `--staged` is unchanged: it has no HEAD to compare.

## Verifier (in order; real output pasted into SCRATCH/build-effect.txt)

1. RED FIRST for each part, arrangement stated: new expectations against
   the old code, failing on an assertion or an exit code, never on a missing
   symbol or an unknown option (law 4). For part A that means the red is
   taken on the no-flags close (old code closes; the test expects exit 2).
2. Part B's known positive: the scratch clone SCRATCH/base-trimprobe, whose
   HEAD commit removed 20 amendment lines from one live item by hand. With
   HEAD^ as the base and HEAD's carrier staged, the gate must fire and name
   that item.
3. Part B's replay, the false-fire measure: over the history of the ten
   governed repos (read-only; the roster is `~/.config/lifecycle/repos`),
   apply the BUILT predicate to every commit that touched an item carrier's
   live home, with exemptions 1 and 2 active and 3 and 4 inactive. Expected
   from the scan: fires on 18 commits (14 hand edits, 4 bulk rewrites) and
   on 0 of the 8 `not-derivable` commits. Report the count, every commit
   whose subject starts `lifecycle:` that fires (expected none), and any
   difference from the expected 18 with the commit named. A difference is a
   finding to report, not a predicate to tune.
4. `python3 -m unittest discover -s test -p 'test_*.py'`: full counts,
   skips dispositioned.
5. `python3 plugin/cli/lifecycle --test`: CLEAN, the emit-site coverage and
   the route-set check included.
6. `python3 tools/prove-rows.py` after the commits: exit 0. Every new row
   has a recorded arrangement admitted on the PAIR (the real anchor changes
   the row; an inert anchor changes none); every existing arrangement whose
   mutated expression a new row now reads is re-checked.
7. `python3 plugin/cli/lifecycle item check` and `item ready --head` on the
   working copy's own carrier: exit codes and findings unchanged from HEAD.

## Write boundaries

The working copy and SCRATCH files with the prefix `build-`. Realizing
files (law 24): `verbs.py`, `cli.py`, `items.py`, `declaration.py`,
`refusals.py`, `tools/prove-rows.py`, the tests; add any file that must
move with them and say so. NOT `ITEMS.md`, `ITEMS-DONE.md`, `LEDGER.md`,
`CLAUDE.md`, `docs/`: the desk books, updates the gap map and the laws
text at integration. Nothing in the working copy is live on write; the
real checkout is, which is why the build happens in a clone.

## Commit plan

TWO commits, part A then part B, each leaving the suite green, titles
`item close: two statements about the work the close ends` and
`item check --staged: a line removed from a live block is refused`. Guards
read by the dispatcher: the machine-wide hooks path holds pre-commit,
post-commit and pre-push and runs in a clone as anywhere; its carrier gate
runs the REAL checkout's CLI, which does not know part A's slots, so no
commit of this build may stage `ITEMS-DONE.md` (none needs to). No
version-bump guard: `plugin.json` has not moved with the last eight code
commits. Never amend, never `--no-verify`.
