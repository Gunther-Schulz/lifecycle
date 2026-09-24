# 2026-09-24: refocus kickoff. A defect-fix wave and ONE design round

**Written by:** the desk of session 09020605 (Opus 5.5), at its close, for the
next session in this repo. **Base commit:** `11e5ae5` (read at write time).
**Authority:** the operator's decisions below were stated first-hand in
session 09020605 and are ledgered. They are testimony here until the operator
confirms this directive in the receiving session. The kickoff paste does that.

## Why this exists: the decision it executes

LEDGER.md, 2026-09-24, `decision: fundamentally re-evaluate lifecycle, or keep
draining the backlog as before?` → **FREEZE-AND-REFOCUS**. In short:

- The core holds. Refusals and gates changed behaviour every time they
  fired. Notices did not: about 61 due-read lines surfaced in one session
  and 0 reads followed; 125 surfaced against 8 read overall.
- The O6 surfacing design's own kill condition 1 ("presence without demand
  — the design is the wrong leg") is firing.
- Reach outside this repo was missing. **FIXED:** lc-273, `lifecycle` now
  resolves by name via dotfiles `bfac708`.
- Frozen: every new mechanism. Allowed: fixing defects already found. Order:
  (1) reach, done; (2) ONE design round; (3) outcome measure lc-161.

The live carrier is the arc: `lifecycle arc status`, arc `answerable`
(stage `refocus`); its narrowing holds the order. Arc `drift-trigger` is
blocked on lc-277.

## Read first, with the reason each one matters

- The reading roster, which the gate enforces: `docs/the-loop.md`,
  `docs/answerable-not-felt.md`, `docs/purpose.md`.
- `docs/answerable-not-felt-research.md`, required for DESIGN-ARC work (repo
  CLAUDE.md). It was NOT read in session 09020605. That gap is one reason the
  round moved to a fresh session.
- `docs/directives/2026-09-20-o6-surfacing-design.md` §2 (lifecycle observes
  ACTS only), §4 (Part A tiers, Part B surfaces), §5 D4, §8 (kill conditions).
- `arcs/answerable.md` and `arcs/drift-trigger.md`: beliefs with their bases
  and kill-conditions.
- Items: `lifecycle item slots lc-276`, `lc-277`, `lc-161`, `lc-256`,
  `lc-281`.

## Job 1: the defect-fix wave (mechanical; dispatch it, do not hold it at the desk)

Allowed under the freeze. Each item's slots are its brief core; quote them,
never paraphrase. Run the write-set join first.

| item | what | write-set (from the item) |
|---|---|---|
| lc-271 | arc header `premises:`/`beliefs:` never updated; `arc narrow --help` does not say it replaces | verbs.py, cli.py, test_arcs.py |
| lc-272 | `record check` grades CLOSED records' shape forever | records.py, test_records.py |
| lc-274 | amend/promotion date message says "no ISO date" for `2026-09-21,` (it is the comma) | items.py, test_items.py |
| lc-278 | census counts ledger-ANSWERED decision blockers as UNSTATED; add near-match hint | items.py, test_items.py |
| lc-280 | `closure_home_split` fires on `./ITEMS-DONE.md` | verbs.py, refusals.py, test_items.py |
| lc-116 | `--no-commit` for `ledger add` AND the arc line verbs (widened 2026-09-24) | cli.py, verbs.py, test_ledger.py, test_arcs.py |

- **Collisions (derived here by hand; re-derive with the join):** items.py
  (lc-274, lc-278), verbs.py (lc-271, lc-280, lc-116) and cli.py (lc-271,
  lc-116). Serialize within those files.
- **Routing preference (operator: codex while the trial lasts):** a
  single-artifact item goes to a codex gpt-5.6-terra lane from a
  decision-complete brief; the desk commits. Multi-commit bundles stay
  Claude sonnet.
- **Codex binding learned 2026-09-24:** run `codex exec … < /dev/null`. With
  stdin open it blocks forever. Recorded in dispatch-guards dev-notes
  `5c2285c`.
- **lc-279** (a command GROUP passes as a verb) waits on a decision: is a
  group-level trigger ever legal? Desk recommendation: NO. It is always a
  finding, and the message lists the group's actions. Ask the operator in
  the kickoff reply's decision round; if they say NO, it joins the wave.

## Job 2: ONE design round, with lc-276 and lc-277 as one question

**The question:** given that lifecycle observes ACTS only, what fires at which
moment, and what does it DEMAND? Presence alone is measured as inert.

Three agenda items belong to this question:
- **lc-276:** the O6 demand leg. Its evidence slot carries the option set:
  1. Drop tier-1 lines where the verb itself reads the kind.
  2. Show deltas only.
  3. Demand only where a miss is costly.
  4. Two-stage retrieval (lc-240).
  5. Retire surfacings that are never read.
- **lc-277:** a goal question fired at seams (dispatch, item close, arc
  advance), each firing logged so the drift treatment arm counts seams from
  the record rather than from memory.
- **When `/standort` fires.** It is the operator's position-check procedure,
  in dotfiles `claude/commands/standort.md`. Today it runs manually; a trigger
  would be new mechanism, so its trigger belongs in this round.

Plus the dependency: **lc-281** (the corpus-to-lifecycle migration survey,
booked for session dev-17) is blocked on this round's outcome.

**Form:**
- Statiker-shaped, as in the repo's earlier rounds: numbered decisions, each
  with a recommendation and its falsifier.
- The transition table carries the OBSERVER column (repo CLAUDE.md sign-off
  rule).
- Decisions go to LEDGER.md and to the `answerable` arc narrowing.

## Job 3: the outcome measure, as a BEFORE measurement

**lc-161** (decision absorption, READY): take the baseline BEFORE any design
from Job 2 ships, meaning operator interventions per session across the
governed repos. Without a before, the refocus cannot be graded. A read-only
discovery lane over transcripts fits; `/standort` phase 2 has the extraction
pattern.

## What session 09020605 verified, so the next session does not redo it

- Suite 1034 OK, 0 skipped; `--test` 128/128 CLEAN; prove-rows 107 of 128
  held (at `e129e90`). The roster is unchanged since.
- lc-268 reach-vs-axis table: `docs/audits/2026-09-18-robustness-clean-without-looking.md`
  Lane 2 (47 reach / 60 axis / 21 no-proof).
- `item check` CLEAN at `11e5ae5`. Two permanent softlocks remain (lc-94,
  lc-136: evidence predicate `false`); not addressed.

## Owed to the operator (theirs, not the desk's)

- `./dot apply`: installed dispatch-guards 0.11.23 vs committed 0.11.26.
- lc-260 (desk/peer control arm) spend decision: frozen, not urgent.
