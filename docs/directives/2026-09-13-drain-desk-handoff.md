# Drain desk handoff — 2026-09-13

Written at the close of a drain session (`dotfiles-b8`) so the arc survives it.
Consumer: the next desk draining this carrier, whether a fresh session or this
one resumed. Read before the first dispatch.

State at writing: `main` at `4312399`, pushed, tree clean, carrier CLEAN,
conservation 115, flow 2.14:1 against a 3:1 tripwire (no retirement pass owed),
**44 schedulable** of 58 READY, no lane running.

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

## Open decisions — the operator's, not the desk's

- **Continue here vs. delegate to a fresh drain desk.** Recommended at the
  close of this session: delegate. The judgment had drained, the remaining set
  is brief-covered, and this desk's own error rate in its last stretch was
  eight mistakes, five caught by lanes or gates rather than by itself. Not
  blocking; recorded so the next desk knows the recommendation existed.
- **`lc-100`'s design** — reservation vs. clone-by-default for the prover. The
  entry's own record shows the reservation approach already failing in the
  stale direction. Re-opened, ruled by nobody yet. Write is `tools/`, so the
  desk may decide it.

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
