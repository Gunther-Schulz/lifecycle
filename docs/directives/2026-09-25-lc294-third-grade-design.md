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
