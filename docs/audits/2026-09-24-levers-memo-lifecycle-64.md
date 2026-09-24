> Copied verbatim from session lifecycle-64's scratchpad by desk lifecycle-d9, 2026-09-24, because the source file dies with that session. Graded in docs/directives/2026-09-24-refocus-design-round.md §6.

# Untaken levers toward purpose.md's goal — input for the refocus round

From session lifecycle-64, 2026-09-24, on the operator's direction ("are
there levers we could be taking that we are not yet?"). Grounded at this
desk in purpose.md, the-loop.md, the prior-art synthesis
(docs/audits/2026-09-24-prior-art-problem-side-synthesis.md), and the
slots of lc-276/lc-277/lc-281/lc-239. OBSERVED lines were read at the
artifact today; DERIVED lines are this desk's judgment with inputs named.

## 0. A dangling booking, first (correction, also sent to dev-17)

The KILL TEST is assigned but its home no longer holds it. OBSERVED:
ITEMS-DONE.md's arc-kind build closure states, in three slots, "the KILL
TEST and the ONE PILOT ARC belong to lc-239 beat 1"; `lifecycle item
slots lc-239` today shows the item re-scoped to the eight-repo schema
migration (PARKED), zero kill-test text. Named home, nothing at the home
— the dangling-consumer class. Repair: re-book explicitly (own item or an
lc-239 amendment). dev-17 received this same correction and may raise it
too — dedupe against that.

## 1. Measure the goal itself, recurringly; let the series rule the round

The goal's two stated metrics — loss-under-kill (purpose.md acceptance
criterion) and operator interventions (kill condition 1, lc-161/lc-228)
— have zero runs between them. OBSERVED: the kill test has never run
(and see 0); the intervention meter exists as lc-161 stage 1, extraction
built, sitting UNTRACKED at tools/operator-interventions.py. DERIVED:
without an end-to-end series, mechanism candidates are graded by
plausibility — the route to purpose.md's kill condition 2. The erosion
probe only settled its question because it was pre-registered and
recurring; the same move at system scale is available and untaken.
Concrete: kill-and-resume drills as a scheduled probe, not a one-off;
lc-161 finished through classification; every candidate afterwards asked
one question — did the series move.

## 2. Withdraw surfacing; don't tune it

OBSERVED: audit counter now 224 surfacings / 8 reads since 2026-09-20
(this session's start banner; lc-276's evidence read 125/8 when written
— kill condition 1 firing harder each session). One session saw ~61
due-read lines, made 0 reads. DERIVED: a 61-line block trains every
reader that the block says nothing — the channel degrades itself
(metric-cadence: the cost is the reader). Silence-as-default is lc-276
option set members (1), (2), (5), but listed as options among six; this
memo argues it is the posture. Nearly free: strip the banner to deltas
plus refusals, and the existing counter measures the withdrawal (reads
should rise as lines fall).

## 3. Demands ride existing verbs before any new seam is built

OBSERVED (lc-276 evidence): in session 09020605 every behaviour change
came from a refusal, none from a notice. DERIVED: lifecycle already owns
acts every session passes through — item add, item close, arc advance,
the write gate — and each is a free demand point: the read or
restatement a moment needs can be demanded by the verb that defines the
moment, no new observer, on enforcement infrastructure already
red-first-proven. Resume read-back (lc-276 option 6) is this lever's
special case at the wake seam; the general form is a sweep over existing
verbs, cheaper than any prior-art candidate. lc-276's open question
stands either way: what a restatement is checked against, computably —
an unchecked read-back is presence in demand's costume and would
replicate the 224/8 failure one seam earlier.
Concrete: (a) a survey artifact enumerating every existing verb × the
demand it could carry × the cost of the miss it prevents (lc-276 option
3's costly-miss filter decides which get built) — the enumeration is
derivable from cli.py's action table, so coverage is checkable; (b) the
first build is lc-277's own done-criterion — the goal-line demand at
dispatch / item close / arc advance, each firing written to the fire
log — which makes lc-277 lever 3's pilot rather than a separate
mechanism; (c) one demand-per-verb ceiling per round, graded on the
surfaced-vs-read counter windowed, so the lever cannot become the
over-constraint law 26 warns about.

## 4. The unnamed candidate: short sessions on purpose, once kill-loss is low

DERIVED from purpose.md's own premises. Both drift modes — amnesia and
hyperfocus — are one disease, the window winning over external state;
every mechanism so far detects or corrects drift INSIDE a long window.
The other attack is bounding the window: with the kill test passing,
sessions are disposable, and deliberate frequent restarts contain
hyperfocus by construction — a wrong frame cannot compound for hours
when nothing lives for hours, and each wake re-reads the record fresh
(the input from outside the frame arrives as the successor). The restart
posture already exists in the operator corpus for COST reasons
(restart-over-compact); nobody has proposed it as the DRIFT mechanism.
It inverts lc-277: the drift check becomes the residual guard of a short
session rather than the main defense of a long one. Preconditions,
honestly: levers 1 and 2 first — measured-low kill loss and cheap
re-entry, else it is cold-start overhead paid to lose state more often.
Recommendation: on the round's agenda BESIDE the three prior-art
candidates, not after them — the only candidate attacking both drift
modes with machinery already trusted.

## 5. Half-pulled: pre-registered probes as the admission bar for mechanisms

OBSERVED: the erosion probe and the drift-treatment probe are the only
two-sided measurements here; both worked (HEALTH twice; the treatment
arm caught not being applied — lc-277). the-loop.md's own limit line:
no control arm exists for the desk/peer split. DERIVED: make "ships with
its pre-registered probe and falsifier" the admission rule for any new
mechanism — lc-276 pre-registering its kill condition is the only reason
today's 224/8 verdict was readable at all.
Concrete: (a) a round decision line: no mechanism candidate is admitted
to build without a pre-registered probe naming its falsifier, its
measurement window, and — for anything drift-shaped — hard negatives
(legitimate pivots that look like drift, the ContinuityBench point on
lc-277); applied immediately to the three prior-art candidates, so the
round's own output is the rule's first exercise; (b) the enforcement
form, law-26-shaped: a `probe:` slot demanded at promotion to READY for
items whose done-criterion ships a mechanism — presence computable at
the carrier, fill quality stays judgment; whether that slot is minted
now or after the round's manual first pass is the round's call — the
decision line alone already binds the three candidates.

## Not a lever: the judgment share

Roughly half of historical captures were the operator designing the
system, none a defect (purpose.md, 19/19 measured). The target there is
the asked-once property, not zero. Its seed exists — `not-derivable:`
records, the ledger-answers-this-decision resolution (lc-8) — and
finishing it into a real dedupe (no question travels twice) becomes
visible as a gap once lever 1's meter runs.
