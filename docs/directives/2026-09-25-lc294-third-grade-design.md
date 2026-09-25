# 2026-09-25: lc-294 design — the third READY grade and its two triggers

**Desk:** lifecycle-d8. **Judge:** lifecycle-64, under the operator's final
delegation (LEDGER decision lines 2026-09-25). **Status: DESIGN FOR REVIEW —
nothing is built until the judge rules on §6.** Authority: the freeze
exception at LEDGER:159 ("third READY grade: narrow freeze exception granted"),
which reverses LEDGER:104 (the reversal record is its own line, 2026-09-25).

## 1. What it fixes, measured

`item ready --head` at 1e06021: **84 READY, 43 PARKED**; READY items cited
by an OPEN arc (`arcs/answerable.md`, `arcs/drift-trigger.md`): **2**. READY
count at the lc-291 window cuts, read from git: 54 (14 days ago), 64 (7),
114 (3.5), 117 (1), 84 now. The lc-292 pass classed 81 of today's READY as
genuine defect repairs, so parking them would be false; the grade still says
"do next" about 84 items while 2 are on any schedule. That is the accretion
doctrine's decay case: "the grade then asserts an intent nobody holds".

## 2. The grade word

**`STANDBY`** — decision-complete (everything READY promises), not on the
scheduled head. Rejected spellings: `BACKLOG` (names the carrier, not a
state), `SHELVED` (reads as abandoned), `READY-LATER` (a hyphenated grade
is a second spelling of READY).

**Declared, tool-read.** A new optional declaration key
`"grades_extra": {"STANDBY": {"like": "READY", "schedulable": false}}`
widens the open vocabulary PER REPO; `items.GRADES_OPEN` stays the tool's
floor. A repo declaring nothing behaves exactly as today (optional key → no
schema bump, §3.8c). `item check`, the census and `item ratio` count STANDBY
as OPEN; `item ready --head` never lists it; `item promote` accepts it as a
source grade.

## 3. The scheduled head — computable

**HEAD := READY items whose id appears in the body of an OPEN arc**
(`arc status` already enumerates open arcs). No new slot: the arc layer is
where the 2026-09-19 decision (ground 3) said scheduling intent lives, and
this makes that sentence executable.

## 4. The two triggers — both FINDINGs from `item ratio`'s cuts, never auto-moves

Moving an item between READY and STANDBY is a JUDGED act (law 10: READY is
judged, never derived). The triggers say a pass is OWED; the desk runs
`item bench <id>` / `item promote <id>`, each with a required `--reason`.

- **DEMOTE owed** — `ready_outgrows_head`: READY minus HEAD exceeds the
  READY items that LEFT READY (closed, dropped, or benched) over the lc-291
  window. Plain: more READY-but-unscheduled work sits there than the repo
  cleared in a week. Today: 82 unscheduled vs READY exits over 7 days
  (to be counted at build; ~70 of the week's 74 closures came from READY,
  estimate). **Fragile today** because the lc-292 pass itself inflated this
  week's exits — the §5 probe must price that.
- **RETURN owed** — `head_draining`: HEAD is empty, or HEAD shrank in both
  window halves while STANDBY holds items — the head draining faster than it
  fills. Same cuts, same three answers: no older commit / carrier born in
  the window → COULD NOT VERIFY, as lc-291.

## 5. Admission-bar probe (pre-registered, R-rules ruling 4)

- **Natural red (demote):** the live carrier at build HEAD must fire
  `ready_outgrows_head`. If it does NOT fire, the predicate is wrong for the
  case that motivated it — a build finding, not a pass.
- **Hard negative:** a repo with READY items and zero movement over the
  window (dispatch-guards, statiker today) must answer COULD NOT VERIFY or
  CLEAN, never a demote FINDING — an idle repo is not a decaying one
  (lc-291's idle rule).
- **Return red-first:** a dated fixture whose head empties while STANDBY is
  non-empty fires `head_draining`; the same fixture with a non-empty head
  is silent.
- **Window:** the lc-291 cuts (7 days, PLACEHOLDER), reused, never a second
  constant.
- **Falsifier after ship:** within 14 days, the demote finding either
  produces a bench pass that brings READY within reach of the head, or it
  fires on every session start with no pass following — the latter is the
  override-reflex failure (law 11) and withdraws the trigger.

## 6. Decisions for the judge

1. **Grade word `STANDBY`** — or another.
2. **HEAD = READY cited by an open arc.** Limit, stated: the arcs are one
   day old (created 9b3e931, 2026-09-24), so HEAD has no history yet; the
   RETURN trigger's "shrank in both halves" is COULD NOT VERIFY until a
   window of arc history exists. Accept, or define HEAD another way.
3. **Triggers FIND, desk moves** (no auto-demotion) — recommended, per law 10.
4. **Migration (law 25):** READY's meaning NARROWS; no existing grade word
   moves. The first bench pass over the 81 class-(a) items is a desk pass
   through `item bench`, not a migration, so law 25 does not bind it; the
   declaration key is optional, so no schema bump and no cross-repo
   dry-run. If the judge reads the narrowed meaning as a schema change, the
   migration is: dry-run over all 10 roster repos, read-back per target.
5. **Write-set** grows to add `plugin/cli/lifecycle_core/declaration.py`
   (the key), `plugin/cli/lifecycle_core/cli.py` (the `bench` verb),
   `.claude/lifecycle.json` (declare STANDBY here), `test/test_verbs.py`
   (the dispatch table lc-120 measured), plus the booked six.

## Reader table (build)

Built at `1ca7176`. This is the sweep for the case where the grade vocabulary
gains a value. It was run over the package source after the build and covers
constants AND literals. `refusals.py` is left out because it holds fixtures,
not readers. Comment and prose lines are left out as well.

    grep -nE 'GRADES(_OPEN|_CLOSED|_DECLARED)?\b|\bSTANDBY\b|"(NEW|READY|PARKED|DONE|DROPPED)"' \
      plugin/cli/lifecycle_core/*.py | grep -v refusals.py

| site | reads | STANDBY treatment |
|---|---|---|
| `items.py:70` `GRADES_OPEN` | the open set | STANDBY is a member, so it is OPEN wherever open/closed is asked |
| `items.py:2325` `census` | open / closed / unknown | counted OPEN, never unknown (`StandbyIsAnOpenGrade`) |
| `items.py:2672-2690` `check_file` | the opt-in | undeclared gives `FINDING [standby_undeclared]`; no declaration handed gives COULD NOT VERIFY; declared gives CLEAN |
| `items.py:2655` `ready_with_unknown_slot` | READY only | **does not fire on STANDBY.** A STANDBY item can only come from READY through `bench`, and READY-with-UNKNOWN is already a finding. A HAND-graded STANDBY holding UNKNOWN is not caught (gap, reported) |
| `items.py:976` `done_slot_on_live_item` | not closed | STANDBY is live, so a done-only slot on it is a finding, as on READY |
| `items.py:1968` untypeable-blocker collection | not PARKED | STANDBY is treated like READY |
| `items.py:2046` `check_blocker_targets` buried set | DROPPED | unaffected: a STANDBY target is a live target |
| `items.py:3017` `check_done_file` | not closed | STANDBY in the done home is `open_grade_in_done_home` |
| `items.py:3331` closed-body judgment | closed | unaffected |
| `items.py:3541` `check_parked_blockers` | PARKED | unaffected: STANDBY is not a wait |
| `verbs.py:332` intake join live set | `GRADES_OPEN` | STANDBY items are live merge candidates |
| `verbs.py:831` `item add --grade` | `GRADES` | STANDBY is accepted at the door. In an undeclared repo `item check` and the commit gate's `--staged` run then refuse it (gap, reported: no door-side refusal) |
| `verbs.py:1511-1560` `item ready <id>` | READY | STANDBY falls to "grade is STANDBY, not READY. THIS VERB PROMOTES NOTHING" |
| `verbs.py:1587` `item ready --head` | READY | **never lists STANDBY** (`test_bench_writes_…`) |
| `cli.py:448` `item waves` | READY | never schedules STANDBY |
| `verbs.py:2390-2403` blocker-target resolution | DONE / DROPPED | a STANDBY target reads "BLOCKED — in the MACHINE's court: … is STANDBY", like any open target |
| `verbs.py:2109, 2183-2194` statusline | `GRADES` + per-word counts | a KNOWN grade with its own `.<n>S` segment, printed only when nonzero. Never in R and never the head id |
| `verbs.py:2624` `item promote` | writes READY | accepts any unblocked open source grade, so STANDBY → READY is the return path (`test_promote_returns_…`) |
| `verbs.py:2686, 2698` `item bench` | READY → writes STANDBY | the only writer of STANDBY |
| `verbs.py:1997, 2022-2052` schedule triggers | READY / STANDBY | HEAD = READY ∩ ids in open arc bodies; STANDBY counted for `head_draining` |
| `verbs.py:3180, 3403` `item close` | writes DONE / DROPPED | closes from any live grade, STANDBY included |
| `verbs.py:1263` supersede lookup | DROPPED | unaffected |
| `declaration.py:734-794` | `GRADES_DECLARED` | the opt-in's accepted set, and nothing else |
| `declaration.py:835` `closure-words` | `GRADES_CLOSED` | unaffected: closure words map onto closed grades only |
| `vocab.py:150-158` registry | `GRADES` + `minted` | member, and a run-time mint record citing LEDGER:159 |
| `desk.py:46` | DONE | unaffected |
| `migrate.py` (61, 162, 168, 251, 308, 619, 642, 744, 759, 3155, 3205, 3208) | legacy word → grade mapping over `GRADES_CLOSED` and literal NEW/READY/PARKED | **never emits STANDBY.** `RULES` maps legacy words to NEW/READY/PARKED/closed only, and STANDBY is a per-repo opt-in that no legacy carrier could have declared. A migrated carrier gets STANDBY only through a later `item bench` |

`CLAUDE.md` pointer: **not added.** A fresh reader of `item check`'s census
sees STANDBY counted under `open`, and the `standby_undeclared` text names the
declaration key. Neither needs a laws-file line to explain it.
