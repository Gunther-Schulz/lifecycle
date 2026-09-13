# Drain desk handoff — 2026-09-13

Written at the close of a drain session (`dotfiles-b8`) so the arc survives it.
Consumer: the next desk draining this carrier, whether a fresh session or this
one resumed. Read before the first dispatch.

State at writing: `main` at `4312399`, pushed, tree clean, carrier CLEAN,
conservation 115, flow 2.14:1 against a 3:1 tripwire (no retirement pass owed),
**44 schedulable** of 58 READY, no lane running.

**STATE REFRESHED — same session, later wave.** `main` at `da630a5`, pushed,
carrier CLEAN, conservation 119, flow `111:52 = 2.13:1` (CLEAN), **46
schedulable**, no lane running, 451 tests green, `lifecycle --test` CLEAN.
The line above is kept as written because the rulings below were formed
against it; this paragraph is the live state. A successor reads THIS one.
`prove-rows` is now **67 PROVEN with zero COULD NOT VERIFY** — the booked
`[ledger_body]` exception is closed (`6220cdd`).

(Corrected in place, same session: this line first read 45. The figure came
from counting lines containing `SCHEDULABLE` in `item ready --head` output,
and one of them is lc-111's BODY, which discusses the word. That is the
word-presence-over-free-prose count the backlog doctrine warns about, made by
the desk that had just booked lc-111 for the adjacent defect. Count the item
lines — `^\s*\d+\. lc-\d+ \[READY\].*SCHEDULABLE$` — never the word.)

## What this session closed

`lc-12` (a lane body with no decision table is a finding) · `lc-38` (the
migration-pointer property, closed DONE on lc-86's prior work plus a regression
pin) · `lc-115` (test_hook_modes answers "no repository" with a skip) ·
`lc-112` (`item park` refuses a blocker that would not govern). `lc-87` dropped
as a duplicate of lc-112. Six evidence predicates repaired; `lc-30` drained —
its blocking evidence had arrived weeks earlier and nothing re-read it.

Second wave, same session: `lc-56` (`ledger add` commits its own line, closing
the last carrier write with no committing actor) and `lc-81` (`init` derives
repo visibility or says it could not, instead of writing a silent default) —
both verified at the artifact, not from their reports. The prover's
`[ledger_body]` row was repaired by following its predicate to `grammar.py`,
closing a registered refusal that had read COULD NOT VERIFY for weeks. Booked:
`lc-116` (the `--no-commit` mirror), `lc-117` (mutating tools declare
themselves), `lc-119` (unguarded subprocess calls in `init`), `lc-120` (the
exit-code decision). `lc-47`/`lc-58`'s cycle dissolved; `lc-60` and `lc-61`
re-grounded and pulled from the dispatch set rather than built on stale
premises.

## Standing rulings — carried, not re-derived

1. **Serialize any lane whose write set touches a shared test baseline.** The
   prover-collision basis for serialization is DEAD (prove-rows now runs in
   private snapshots), but every lane runs the full suite as its baseline, so a
   lane mid-edit on a test file poisons every other lane's reds. The join over
   write-boundaries is necessary and not sufficient — check the read-or-execute
   overlap too.
2. **Any mutate-and-restore instrument runs in a private copy — the prover
   included, not only the formal bite.** This desk violated it twice in one day
   after writing the rule. Treat the prose as insufficient (see lc-100).
3. **A private CLONE at the pin beats `git archive` where the old side needs
   in-repo state** — measured both ways inside lc-112: archive self-check
   failures=2/errors=3, clone self-check green.
4. **Cross-repo write-sets carry a typed blocker and never dispatch from here.**
   An item whose realizing write lands outside this repo is surfaced, never
   executed.
5. **`tools/prove-rows.py` is never granted to a lane.** The lane composes the
   mutation entry with plant and control and reports it owed; the desk lands
   it, so a check and its subject never share one author in one commit. The
   roster Row in `refusals.py` IS grantable — a Row declares, a mutation entry
   proves, and only the second needs separate authorship.
6. **A change that emits a NEW finding ident needs `refusals.py` in its write
   set.** `roster.check_coverage` fails any emitted ident absent from
   `refusals.ROWS`, so a lane without it lands correct code and a red tree.
   Ask at brief time.
7. **Pin historical commits in red-first arrangements, never HEAD.** Specimens
   get repaired and the proof expires.
8. **Address the dispatcher as `main`** in lane briefs — SendMessage refuses
   this session's own name from inside it.
9. **State updates to a live lane travel by ARTIFACT** (the brief file it can
   re-read), not by message alone. A lost directive announces itself; a lost
   state update leaves the lane confidently reporting gaps already closed.
   Grade every reported gap against the desk's own record before acting.
10. **Read the registered-procedure section FROM THE FILE, never the injected
    snapshot**, and report the computed fingerprint. Measured repeatedly stale;
    in lc-112 the missing paragraph changed what the lane BUILT.

Added in the second wave, each paid for once:

11. **OPEN THE CODE BEFORE WRITING THE BRIEF — the entry is not the world.**
    Every item dispatched or examined in wave two had a premise the entry got
    wrong: lc-60's reader half did not exist, lc-47/lc-58 were an
    unschedulable cycle, lc-81's counts were unreproducible and its safety
    argument named the field's meaning rather than its READERS. The entries
    read decision-complete and were not. Budget the grounding pass at the
    desk, not only at the lane.
12. **A MUTATING TOOL NEVER APPEARS IN A BRIEF'S BASELINE LIST.** A baseline
    list reads as commands to run on the tree as found, and it beats any
    prohibition elsewhere in the same document — measured twice in one hour,
    in briefs that carried both. Give it its own labelled block with the
    private-copy requirement attached to the command. (lc-100 fixes the tool;
    lc-117 makes the property declarable.)
13. **A LOST DIRECTIVE ANNOUNCES ITSELF ONLY WHERE THE LANE WOULD BLOCK.**
    Where it settles something the lane can decide alone, its loss is as
    silent as a lost state update: the lane decides, ships, and reports the
    choice as its own deviation, and the desk reads a deviation where there
    was a countermand. Measured on lc-81 — and the dropped directive was the
    WORSE answer, so "deliver directives more reliably" is not automatically
    the fix. Anything a lane must actually follow goes in the brief FILE.
14. **A DESK RULING AGAINST A LANE THAT HAS READ THE CODE STARTS BEHIND.**
    lc-81's lane held two facts the desk did not and reached the better
    design. Rule on mechanism, not on conclusions, and verify the lane's
    cited facts at the artifact before overruling — twice now the artifact
    settled it against the desk.
15. **GRADE A LANE REPORT AT THE ARTIFACT, AND GRADE YOUR OWN INSTRUMENT
    TOO.** A desk grep under-reported which arms passed and nearly booked a
    lane's correct report as a discrepancy: the pattern keyed on a line shape
    only some rows carry. Both times a conflict appeared between report and
    measurement this session, the desk's instrument was the defective one.

## Open decisions — the operator's, not the desk's

- **Continue here vs. delegate to a fresh drain desk.** Recommended at the
  close of this session: delegate. The judgment had drained, the remaining set
  is brief-covered, and this desk's own error rate in its last stretch was
  eight mistakes, five caught by lanes or gates rather than by itself. Not
  blocking; recorded so the next desk knows the recommendation existed.
- ~~**`lc-100`'s design**~~ — **RULED, second wave: clone by default**, with an
  explicit flag to mutate the invoked tree. The reservation approach is
  rejected on the entry's own evidence: it had already failed stale once, and
  it depends on being read. Confirmed in the wild the same hour — the
  writer-reservation gate warned about a holder whose lane had already
  finished and reported. Decision recorded in `LEDGER.md`; build is lc-100,
  still open.
- **`lc-120` carries a live decision blocker** and is the one thing here a
  desk should NOT rule alone: whether `lifecycle init`'s exit code should say
  that a declared value was unresolved, or whether the emitted COULD NOT
  VERIFY line is the whole contract. Fourteen existing assertions encode an
  answer nobody recorded as a decision, and a remote-less repo — the normal
  case — would flip to COULD NOT VERIFY almost always under the other reading.

## In flight elsewhere

The judgment desk (`dotfiles-9e`) holds corpus and devbook edits. Protocol both
ways: it asks before editing a registered section while a lane of this desk
pins its fingerprint, and this desk names the pinning lane. Current fingerprint
at writing: `0faaa709…`, class `guard/checker builds` eval-open.

Routed to it this session and accepted: the two-mutation rule for pinning an
already-true property; the stored-brief probe detector; the must-not-move arm
must not carry the guard it grades; the whole-file-write dropped-content check;
the mailbox asymmetry above. Grading a lane report includes dispositioning
slot (e) BY COUNT in the digest — a digest silent on slot (e) has not graded
the report.
