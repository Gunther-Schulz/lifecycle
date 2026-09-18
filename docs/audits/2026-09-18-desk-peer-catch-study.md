# Who catches errors in desk/peer sessions — a transcript study

**Run:** 2026-09-18, desk 9553b0, three sonnet discovery lanes, read-only.
**Sample:** 9 sessions across 6 projects and 3 arcs, each carrying ≥20 peer and
≥20 operator messages so every bucket was observable. Drawn from a frame of 168
sessions with peer traffic (3,203 peer messages, 6,799 operator interjections
machine-wide).
**Question it serves:** lc-157 / the operator's #2 — is desk/peer
ONE-DIRECTIONAL CHECKING (the desk checks the peer) or TWO ASYMMETRIC
INFORMATION HOLDERS (each corrects the other from its own view)?

---

## The answer

**Two asymmetric information holders. The one-directional reading is refuted by
the direction data, and refuted hardest in the direction that reading does not
allow.** In the lane with the cleanest direction breakdown, cross-session
catches ran **8:1 PEER→DESK** — the opposite of "the desk checks the peer" —
with one desk→peer and one ambiguous. A second lane's five cross events split
3 caught by the peer-desk against 2 caught by the executing session. The third
lane's cross events include six separate cases of a peer correcting the desk.

**And the basis is overwhelmingly the artifact, not the prose.** Of the 25
cross-session catches, roughly 21 cite a concrete artifact read — a grep, a
document re-read, a fixture run, a schema quoted verbatim — against about 4
resting on reasoning alone. One lane put it exactly: every cross catch in its
set "involved the catching party actually checking something rather than just
disagreeing on tone."

That is arXiv:2606.09863's judge result reproduced in operational data from the
other side: grading prose caught almost nothing; reading artifacts caught
almost everything.

---

## The counts, and what they are NOT

103 events graded across the three lanes.

| bucket | L1 | L2 | L3 | total |
|---|---|---|---|---|
| SELF | 34 | 16 | 13 | 63 |
| CROSS | 10 | 10 | 5 | 25 |
| MECHANISM | 4 | 0 | 1 | 5 |
| ESCAPED | 0 | 1 | 9 | 10 |
| **graded** | **48** | **27** | **28** | **103** |

**THESE ARE RAW COUNTS AND NOT PROPORTIONS OF ALL CORRECTIONS.** The instrument
reads INBOUND records only (cross-session messages and operator interjections),
and a SELF or MECHANISM catch produces no inbound record at all — a mechanism
catch lands in a tool result, a self-catch needs no message. So two of the four
buckets are under-counted BY CONSTRUCTION. This was the dispatching desk's
design defect, found by a lane's critique pass before extraction began, and the
scope was narrowed to the CROSS question in consequence. Only the CROSS row
carries weight.

**A sharper form of the same caveat, which a lane derived from its own data:**
essentially all 63 SELF events are a party catching its own error and then
REPORTING the retraction across the channel — that is structurally how they
entered the sample. So "SELF: 63" means *63 self-catches that were
COMMUNICATED*. A self-catch nobody mentioned is invisible to this study
entirely.

---

## The re-grading that moves the headline

One lane filed "a party's own dispatched lane caught that party's error" as
SELF. Under the independence framing this study serves, a dispatched lane is a
SEPARATE CONTEXT WITH ITS OWN INFORMATION — which is the property under test.
Asked to re-split its 34 SELF events from its own notes, that lane returned:

- **LANE-CAUGHT: 12** (a dispatched lane or arm surfaced it; 7 explicit, e.g.
  "the lane caught all three", "two cheaper lanes caught what this desk
  asserted")
- **TRUE-SELF: 18** (the party re-ran or re-read something itself)
- **CAN'T TELL: 4** (notes do not pin it down; not reconstructed)

So in that lane's sample the headline moves from "34 SELF vs 10 CROSS" to
**22 cross-context vs 18 true-self, with 4 unclassified** — close to parity,
and nothing like a picture of parties reliably checking themselves.

---

## The most important finding, and nobody was looking for it

**A PEER'S OWN "SELF-CORRECTION" LABEL IS NOT EVIDENCE OF WHO CAUGHT SOMETHING.**
A lane found two independent cases where a desk praised its peer's
"self-correction" — in one case calling it "the arc's best piece of
self-correction" — when the raw transcript shows the catch was
OPERATOR-TRIGGERED. The desk could not see otherwise: **a peer sees only what
is reported to it, never the other session's private turns with the operator.**

Two consequences, and the second is the load-bearing one:

1. As a measurement hazard it means any study resting on a party's own account
   of who caught something is reading a systematically biased record.
2. As a FINDING about desk/peer it means **the desk systematically
   over-attributes self-correction to the peer** — and that bears directly on
   the operator's trust calibration (lc-161), which is built from exactly these
   reports. The operator's confidence in a desk's judgment is calibrated on a
   record that inflates the desk's apparent self-sufficiency.

---

## MECHANISM is near-zero, and one lane explained why

MECHANISM totals 5 of 103, and 0 in one lane. That lane's account is worth more
than the number: in its three transcripts there was **not one case of a bare
"test failed → party fixed it"**. Every mechanism-adjacent incident involved a
party's own wrong DIAGNOSIS of what the mechanism meant, which is why those
events tallied SELF or CROSS. Its own honest read: this may be a real property
of how these desks work — mechanisms feed into judgment before action — or an
instrument artifact, and it could not tell the two apart from this data.

---

## Named limits — every one volunteered by the lane it constrains

- **No positive control on any lane's sampling scorer.** One lane stated
  plainly: "NO POSITIVE CONTROL WAS RUN... the set is
  retraction-vocabulary-heavy and will systematically favor LOUD,
  self-announced corrections over a fact quietly corrected in passing." All
  three counts are FLOORS.
- **ESCAPED=0 in one lane was a sampling artifact, not a finding** — confirmed
  by another lane finding 9 operator-caught events in its own sample. Two lanes
  with different keyword sets diverging on one bucket measures the instrument,
  not the phenomenon. This is the only cross-lane instrument check available
  and it fired.
- **Coverage was not exhaustive in any lane.** The largest session (753 inbound)
  was keyword-sampled, and the lane said so rather than implying a census.
- **The sample is operator-selected, not random.** Nine sessions chosen for
  having both traffic types. No lane generalized past its own three.
- **No control arm exists and none is possible here.** This measures who
  catches, never whether desk/peer beats a single session. That needs matched
  tasks run both ways.

## Instrument defects found and fixed mid-run

All three by lanes, none by the desk that built the instrument, all in the
commissioned critique pass before extraction:

1. Verification was AGGREGATE-ONLY ("25 = 5 + 20"), equally consistent with
   compensating misclassifications. Measured after: 0 disagreements across 865
   messages against a strict classifier, which discriminates on a planted case.
2. **THREE populations share the `queue-operation` record type, not two.**
   Measured: 726 records = 291 empty + 206 peer + 168 task-notification + 61
   REAL operator. 73% of what the instrument called "operator" was background
   task notifications, inflating ESCAPED ~4x.
3. The structural blindness above (two of four buckets unreachable).

Defect 3 would have produced a CROSS-dominant tally matching the desk's own
prior expectation, from three lanes agreeing with each other while sharing one
instrument — agreement certifying nothing on an axis none of them varied.

**Session-search cannot be used for this work and this is why:** its declared
scope is user/assistant messages, which EXCLUDES `queue-operation` — where both
peer messages and operator interjections live. A study built on it would find
both buckets near-empty and report that as a finding.
