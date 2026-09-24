# Untaken levers toward purpose.md's goal — round input, session lifecycle-64

**2026-09-24, on the operator's direction** ("are there levers we could be
taking that we are not yet?", then refined in conversation). This file
SUPERSEDES the scratchpad memo pointed at lifecycle-d9 earlier today and the
compact forms in the two messages sent there (msg c716b73a, amendment
4bb077cd): lever 4 here carries the operator's correction, and the seams
synthesis at the end postdates both. OBSERVED lines were read at the
artifacts at this desk on 2026-09-24; DERIVED lines are this desk's
judgment with inputs named. Round input, not decisions.

## 0. A dangling booking (correction, also sent to dev-17 and d9)

The KILL TEST is assigned but its home no longer holds it. OBSERVED:
ITEMS-DONE.md's arc-kind build closure states, in three slots, "the KILL
TEST and the ONE PILOT ARC belong to lc-239 beat 1"; `lifecycle item slots
lc-239` shows the item re-scoped to the eight-repo schema migration
(PARKED), zero kill-test text. Named home, nothing at the home. Repair:
re-book explicitly (own item or an lc-239 amendment).

## 1. Measure the goal itself, recurringly — under the gate ordering

The goal's two stated metrics — loss-under-kill (purpose.md's acceptance
criterion) and operator interventions (kill condition 1; lc-161/lc-228) —
have zero runs between them. OBSERVED: the kill test has never run (and see
0); the intervention meter exists as lc-161 stage 1 at
tools/operator-interventions.py (CORRECTED 2026-09-24, verified at the
artifact: TRACKED at fbd5ecd with uncommitted modifications — the earlier
"untracked" claim was a stale session-start snapshot; d9's §6 grading
caught it). DERIVED: without an
end-to-end series, candidates are graded by plausibility — the route to
kill condition 2.

Two refinements from the design of record (read after the first draft):
(a) GATE ORDERING BINDS THIS LEVER — answerable-not-felt.md: grading
EFFECT over an unfired mechanism is unreadable ("a mechanism that never
fired and one that fired and did not help produce identical evidence").
So kill-and-resume drills (which measure whether the written state
CARRIES — gate 1's read half) run before intervention-rate conclusions
(gate 2), and any null on lc-161's series is read against gate 1 first.
(b) THE KILL TEST IS THE MISSING RETRIEVAL MEASUREMENT. The design doc
says retrieval's real measurement "does not yet exist: it would have to
ask whether the record that would have answered a question was read
before the question was answered some other way." A kill-and-resume
drill asks exactly that, at the one seam where the answer is forced.
Concrete: schedule drills as a recurring probe, not a one-off; finish
lc-161 through classification; grade candidates afterwards on whether the
series moves.

## 2. Withdraw surfacing; don't tune it

OBSERVED: audit counter 224 surfacings / 8 reads since 2026-09-20 (this
session's start banner; lc-276's evidence read 125/8 at writing).
CORRECTED 2026-09-24 (refocus round §0.1, accepted by this desk as judge):
377 of 379 surfacings came from a verb that is itself a declared reader of
the surfaced kind, so the count measured TAUTOLOGICAL notices and "firing
harder" is tier-1 volume growing — the informative-notice leg is UNTESTED,
not refuted. The lever survives at narrower width: R1 removes tier-1;
tier-2 withdrawal waits for the lc-276 falsifier's evidence.
DERIVED: a 61-line block trains every reader
that the block says nothing — the channel degrades itself. Silence-as-
default is in lc-276's option set as members (1), (2), (5); this memo
argues it is the POSTURE, not a tiebreak. Nearly free: strip the banner to
deltas plus refusals; the existing counter measures the withdrawal (reads
should rise as lines fall).

## 3. Demands ride existing verbs before any new seam is built

OBSERVED (lc-276 evidence): in session 09020605 every behaviour change
came from a refusal, none from a notice. DERIVED: lifecycle already owns
acts every session passes through — item add, item close, arc advance, the
write gate — each a free demand point on enforcement infrastructure
already red-first-proven. Resume read-back (lc-276 option 6) is this
lever's special case at the wake seam. lc-276's open question stands:
what a restatement is checked against, computably — an unchecked
read-back is presence in demand's costume.
Concrete: (a) a survey artifact enumerating every existing verb × the
demand it could carry × the miss cost it prevents (enumeration derivable
from cli.py's action table, so coverage is checkable; lc-276 option 3's
costly-miss filter decides which get built); (b) the first build is
lc-277's own done-criterion — the seam-fired goal question at dispatch /
item close / arc advance, fire-logged — making lc-277 this lever's pilot
rather than a separate mechanism; (c) a one-demand-per-verb ceiling per
round, graded on the surfaced-vs-read counter windowed, so the lever
cannot become the over-constraint law 26 warns about.

## 4. Short ACTING FRAMES via main + lanes — as corrected by the operator

This lever's first form ("short sessions on purpose") was WRONG and is
superseded; the operator's correction (2026-09-24, first-hand at session
lifecycle-64): window LENGTH as the drift cause is not established, and
killing a running session costs in-flight continuity; the proposal is a
main session with subagents and/or peer sessions. Grading, DERIVED: the
correction is right on the evidence — purpose.md blames the acting
frame's self-blindness, not its length; CodeBolt's docs say the acting
agent is a poor judge of its own drift at any length; and the
governance-decay measurement (rule absent from context → violations
0%→30-59%) argues for MORE of the right state present, not less.
The amended lever: short acting frames via main+lanes (a dispatch lane is
a disposable window by construction), the MAIN desk's frame broken by
outside readers at seams (the seam-fired goal question; fresh-context
verification of the desk's own bookings), and the kill test retained as
the LOSS METER — compaction and crashes are involuntary kills, and cheap
lane handoffs need measured-low loss — never as an operating mode.
Symmetric honesty: main+lanes has no control arm either (the-loop.md's
own limit line), so lever 5's admission bar applies to it too. The
narrowed measurable question: does drift stratify by acting-frame
length/architecture — carriable by the lc-277 probe. Residual the lanes
do not fix: the long-lived main desk itself frame-locks (the operator's
Scheuklappen complaint is about the sessions they interact with), so the
outside-reader seams on the MAIN desk are the load-bearing half.

## 5. Pre-registered probes as the admission bar for mechanisms

OBSERVED: the erosion probe and the drift-treatment probe are the only
two-sided measurements here; both worked (HEALTH twice; the treatment arm
caught not being applied — lc-277). the-loop.md's limit line: no control
arm for the desk/peer split. DERIVED: make "ships with its pre-registered
probe and falsifier" the admission rule for mechanisms — lc-276
pre-registering its kill condition is the only reason the 224/8 verdict
was readable.
Concrete: (a) a round decision line, zero build: no mechanism candidate
is admitted without a pre-registered probe naming its falsifier, its
measurement window, and — for anything drift-shaped — hard negatives
(legitimate pivots that look like drift; ContinuityBench, on lc-277's
evidence); applied to the three prior-art candidates now, so the round's
own output is the rule's first exercise. (b) Later, if earned: a `probe:`
slot demanded at promotion to READY for mechanism-shipping items —
presence computable at the carrier, fill quality judgment (law 26 shape).
Whether to mint the slot now or after one manual pass is the round's
call; the decision line alone binds the three candidates.

## The seams synthesis (operator + desk, 2026-09-24) — the ordering's WHY

The operator's thesis: seeing and writing the right things at the right
time is the load-bearing pair — if the seams work, fact dilution in a
long session is largely harmless, and session lifecycle reduces to
arithmetic (prefix re-billing vs re-grounding cost). Grading, DERIVED
with the record's support: nearly every measured failure class here is a
missing read or write AT A MOMENT, not a corrupted window — the
17-times-handled doc unread, the three moments-of-application instances,
224/8, governance decay tracking absence-from-context. One leg the
two-part formulation drops: INDEPENDENT FEEDBACK. Hyperfocus is not a
fact problem — a frame-locked session re-reads correct state through the
wrong lens, so the outside reader at a seam is not replaceable by better
presence (the creed's third pillar; answerable-not-felt.md's
independence-not-timing correction says the same from the research side).
Two closures: the write side is what SETS the re-grounding price, so
good seams make restarts cheap and the architecture debate low-stakes —
testable by stratifying the drift probe by seam compliance (if the
architecture variable stops mattering once compliance is high, the
thesis is confirmed at mechanism level). And the safety margin of
"dilution doesn't matter" is exactly the decided-but-unwritten tail of
the window, held near zero by the write discipline — the same quantity
the kill test meters.
Implied priority ordering for the round: demand-at-the-moment first
(lc-276/277), outside-reader seams second (small; only cover for
frame-lock), architecture last — its stakes are what the first two
determine.

## Loose ends noted while writing this (not this file's to fix)

- tools/operator-interventions.py: RESOLVED — tracked at fbd5ecd (the
  untracked reading was stale; see lever 1's correction). Its uncommitted
  modifications are d9's in-flight work, not a loose end.
- The asked-once pipeline (purpose.md's "asks each thing once") has seeds
  (`not-derivable:` records; ledger-answers resolution on lc-8) and no
  item; becomes visible as a gap once lever 1's meter runs — a consider,
  gated on lc-161.
- The hook/no-hook natural experiment (answerable-not-felt.md, "the one
  thing worth measuring next") remains unrun and is the cheapest gate-1
  comparison available.
