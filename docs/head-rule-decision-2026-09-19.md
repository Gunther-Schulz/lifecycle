# The head-rule question — DECLINED BOTH WAYS, 2026-09-19

**Decision:** declare NEITHER a third grade NOR a lead goal. Ruled by the
driving desk `cachyos-setup-b3` under the operator's standing delegation of
2026-09-19; proposed by the executing desk `lifecycle-38` as queue item 6 of
`docs/directives/2026-09-19-answerable-arc-decision-round.md` (addendum 3).

**This file exists because the ledger's answer slot caps at 300 characters
and these grounds are a body.** The ledger carries the decision and points
here; this is the body, not a second copy of the decision. The ledger line is
the decision's home and this file must never be read as overriding it.

## What was asked

The declaration reads `head-rule: none` with no lead goal, so the head of the
READY set is SOURCE ORDER — a fresh desk asked for "the head" gets entry
order, which is arbitrary. Two independent routes reached this question: the
carrier's size, and the arc walk's multi-arc scheduling.

## The measured state it was decided against

Read at `efdd5c5`, not recalled:

| figure | value |
|---|---|
| live items | 126 |
| READY | 115 |
| schedulable (blocker gate passed) | 105 |
| PARKED | 10 |
| `item ratio` capture:drain | 225:107 = 2.10:1, CLEAN (tripwire 3:1) |
| READY sharing goal `enforce-the-invariants` | **92 of 115** |

The last row is the one that decided it, and it came from the driving desk's
independent read rather than from the proposal — the executing desk's argument
did not have it.

## Grounds

**1. The third grade's own firing condition is UNMET.** The backlog
doctrine's trigger is the ready set outgrowing what the repo will EVER
schedule. The drain record contradicts that: 107 bodies closed, ratio 2.10:1
CLEAN and steady. The datum that raised the question was SIZE (105
schedulable), and size is precisely the source the doctrine refuses — "no size
cap stands behind either: the number has no honest source."

**2. A lead goal FAILS ITS STATED PURPOSE on the measured distribution.**
Declaring one orders the head only if the goal partitions the set. With 92 of
115 READY in a single goal it does not: the head stays indistinguishable from
the tail, and the one-line declaration buys ceremony rather than ordering.
This is why the executing desk's recommendation — declare a lead goal as the
cheap first move — was declined. It was the right shape of argument against
the wrong distribution, and the distribution was not in evidence when it was
made.

**3. READY is decision-completeness, never queue position** (doctrine,
verbatim). Scheduling intent has a real home on this machine and it is not a
grade: it is the arc directive layer, which is where a fresh desk actually
receives its head today.

## Re-open events — each computable or incident-shaped, none a time-word

- **(a)** `item ratio`'s window shows the head NOT draining — scheduled-out
  below booked-in. This is the doctrine's own return trigger and is computable
  from the carrier's record.
- **(b)** A MEASURED INCIDENT of a fresh desk mispulling from source order.
  An incident, not an impression.
- **(c)** **lc-162 lands** (per-goal `item ratio`). That is the instrument
  that would give a lead-goal declaration an evidence basis instead of a
  guess. Re-ask then.
- **(d)** **lc-231's arc-kind design.** Multi-arc scheduling was the second
  route to this question, and an arc kind is where "what is scheduled" gets a
  home with an owner. The question folds into that design rather than into a
  grade.

## Reach, stated because a decline is an absence claim

**This basis does not rule out that multi-arc scheduling needs an ordered
head.** Re-open event (d) is where that half stays open, deliberately. The
grounds above establish that the CARRIER does not need a third grade today and
that a lead goal would not order it; they establish nothing about whether an
arc layer needs its own ordering, which is a different question about a
mechanism that does not exist yet.
