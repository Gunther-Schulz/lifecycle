# The direction-drift trigger probe — DESIGN, 2026-09-20

**Status: a DESIGNED probe, not yet run.** Written at the desk that took the
operator's 2026-09-20 sharpening first-hand; the carrier's own cost test
vetoed booking the design as an item (one file, one hunk, session live), so
it was written in the same session. Precedent for the bar this document must
meet: `2026-09-19-erosion-probe-design.md` in this directory — the
discriminating quantity named before data is pulled, the result consistent
with both hypotheses named so no finding is manufactured, reach bounded.

## The claim under test

**OPERATOR, first-hand, 2026-09-20:** pressing a drifting session with "what
do you think the goal is?" usually returns a CORRECT answer and the course
then corrects — including where the goal was only partly stated and had to
be inferred. The operator supplies no content in that ask, only the trigger;
they are today the only trigger, which they name babysitting.

**The competing prediction, from the literature this repo already carries:**
intrinsic self-correction without external information degrades rather than
improves (arXiv:2310.01798: the model is more likely to modify a correct
answer than repair a wrong one), and the research companion's own line — a
seam-triggered LLM self-reflection inherits the identical failure mode as
continuous self-monitoring, merely fired less often.

**These disagree only if the operator's ask carries nothing but the
trigger.** It does not, and that is the confound: the ask arrives TIMED
(the operator asks when they see drift) and SIGNED (the ask itself is
evidence that someone suspects drift right now). An environment-fired ask at
a seam has neither property. Whether the correction survives losing both is
the whole question, and neither the operator's observation nor the
literature answers it, because neither has varied it.

## THE ANALOGY IS STATED, NOT ASSUMED

arXiv:2310.01798 measures self-correction on closed benchmark answers; this
probe measures course correction against a goal held in an open work
context. What carries across is the shape — a party asked to re-examine its
own state with no new information — not the numbers. The operator's
observation is likewise not a measurement yet: it is recollection-grade
until the baseline sweep below turns it into a rate.

## The vacuous quantity, named first so it is not reported

**The rate of correct goal restatements proves nothing.** A seam-fired
question answered correctly with no course change is consistent with BOTH
hypotheses at once: no drift was present (mechanism healthy, nothing to
catch) and drift was present and sailed through (mechanism inert ritual).
Aggregating restatement-correctness would manufacture a green the way the
erosion probe's proven-fraction would have manufactured a red. Only events
where drift is INDEPENDENTLY ESTABLISHED discriminate.

## The discriminating quantity: caught-by-whom, over established drift

The unit is a DRIFT EPISODE — a stretch whose in-flight action is later
established to have been off-goal (an operator correction landed, or the
course-corrections carrier records the pre-change action as wrong, the
carrier's own existing criterion). Over episodes, the probe reads WHO fired
the catch.

| | operator-observation predicts | self-correction literature predicts |
|---|---|---|
| seam-fired goal question over a drifting stretch | the answer contradicts the in-flight action; course changes without the operator | correct-sounding restatement, no course change |
| operator drift-interventions per treated session | FALL against baseline | UNCHANGED |

Restatement-correctness moves neither column, which is exactly what the
vacuous quantity could not manage. **The outcome that flips the verdict each
way, named before any data is pulled:** environment-fired catches appearing
at a rate comparable to the operator-fired baseline while operator
interventions fall is the operator's reading confirmed — the trigger alone
suffices; correct restatements with near-zero course changes while the
operator keeps catching the same drift is the confound confirmed — the
suspicion signal, not the question, does the work.

## The two arms

**BASELINE (retrospective, data held).** Operator-fired goal-question events
in the transcript corpus: each graded for whether the answer was correct and
whether the course changed. This turns "usually correct" from recollection
into a rate. INSTRUMENT LIMIT, load-bearing — REASON CORRECTED BY THE SWEEP
ITSELF (2026-09-20): the session-search MCP's declared scope excludes
queue-operation records, and this design originally reasoned that operator
goal-questions live there as mid-turn interjections. MEASURED: zero of the
seven baseline events is a queue-operation record — all seven are plain
`type=user` turns — while goal-token question hits split 112 user to 67
queue-operation across the corpus, so the excluded population is real and
sizeable but is not where this event class lives. The raw-JSONL instruction
STANDS, on corrected ground: the class spans record types nothing declares
in advance, and a sweep keyed to the record type the original reasoning
named would have returned ZERO events, the known positive included. A zero
from the search tool over this class remains an instrument reading, not an
absence.

**One graded specimen already in hand (2026-09-20, the non-technical
session; operator-pasted and operator-confirmed in this repo's own
conversation):** the operator asked what the goal was; the session's read
was correct by the operator's own grading ("yes, so hoping you are back on
track") and the arc re-corrected. The read closed with a one-bit
confirmation demand — "is that the goal, or is it something else, in your
words?" — which is the slot pattern's whole shape already: statement plus
cheap confirmation. One event. The operator reports doing this across
projects and sessions with "usually correct" results; that stays
recollection-grade until the sweep counts it, and it also says the baseline
data spans MULTIPLE project corpora, not one. (SUPERSEDED 2026-09-20, same
day: the sweep ran — the baseline-result section below carries the rate
this paragraph was waiting for.)

**TREATMENT (prospective, mechanism must exist in trial form).** Sessions
run with a seam-fired goal-question demand: the investigation record's GOAL
slot re-read and a one-line "how the current move serves it" written at each
seam (round open, wave authorization, record update). No hook needs building
for the trial — a directive in the brief suffices for N sessions — which
keeps the probe ahead of any design-arc admission decision rather than
depending on one.

## THE BASELINE ARM HAS RUN — measured 2026-09-20

Sweep executed by a delegated opus desk over the LOCAL transcript corpus
only (65 project directories, 2,447 JSONL files, 982,105 records; Remote
Control and cloud sessions write no JSONL here, so their events are
invisible to these counts by construction). Rows verified at this desk:
the TSV re-read, the two load-bearing unsigned-ask rows re-opened at the
raw records. Evidence artifacts (12-row TSV, the read-and-excluded TIER A
chunk list, the reach probe): in the operator's `dotfiles` repo — a
PRIVATE repo; there is no repo named "dotfiles-private" — at
`claude/records/drift-baseline-2026-09-20/`. Private deliberately: the
artifacts carry personal-session pointers, and 12 of the read-residue
file's 274 lines quote chunks from personal sessions, so that directory
never moves to a less private home.

- **The knowledge leg is now a rate, and it is 7 of 7.** Seven operator
  goal-question events, 2026-08-04 to 2026-09-20, four projects. Every
  goal-read CORRECT on the operator's own next turns; rider 1's
  wrong-restatement class is EMPTY (0 corrected-by-operator, 0 unclear),
  including two events where the goal had to be INFERRED rather than read
  back. "Usually correct" was under-claimed.
- **Course change followed in 6 of 7** (one N-A) — 5 of 7 under strict
  attribution: in one event the direction moved only after a SECOND
  operator intervention three minutes later, so that row's YES is about
  the stretch, not the goal-read alone.
- **The confound is measured, not argued: 5 of 7 asks were SIGNED** — four
  carried the drift complaint inside the ask itself, one followed six
  same-session babysitting complaints. The unsigned cell holds n=2 and
  splits (one course change, one N-A). **So the baseline arm returns
  COULD NOT VERIFY on trigger-sufficiency** — exactly the outcome the
  vacuous-quantity section predicted a restatement-rate would paper over.
  The treatment arm remains the only discriminator; what the baseline
  settles is the knowledge leg and the confound's size.
- **Pattern-reach bound, part of the rate's basis:** one of the seven
  events carries NO goal word ("why are we doing these reviews? isn't it
  overkill?") and was found only by a wider direction-check net — so any
  goal-keyed instrument under-counts the class by at least 1 in 7, and
  the true class is wider than any keyword family proves.
- **Adjacent rows recorded, deliberately not pooled:** one drift
  INTERVENTION with no question (operator asserts the goal, session
  re-aims) — baseline material for the drift-interventions-per-session
  row of the outcome table; one INVERSE event (operator states the goal,
  session corrects the formulation, operator accepts) — the
  adjustability leg of WHAT SURVIVES A QUIET running in the other
  direction.

## Rider 1 — the third answer is load-bearing

A fired question answered with a WRONG goal restatement is a different
finding from restated-correctly-but-uncorrected, and the two are not pooled:
the first contradicts the operator's observation at the KNOWLEDGE leg (the
goal was not articulable after all) and would redirect the fix toward
presence, not demand; the second is the trigger-insufficiency signal this
probe exists to test. Pooling them would blur the one split that decides
where the repair goes.

## Rider 2 — reach, stated so the result is not over-read

The probe measures ONE trigger content (the goal question) at ONE class of
seam, in governed repos carrying an investigation record. It is silent on:
drift detection in general, ungoverned repos, conversational sessions with
no record (the 2026-09-20 specimen 2 class), and whether total operator
babysitting falls — only the drift-intervention slice is counted.

## What each outcome decides

- **FIRE** (environment-fired catches at a comparable rate, operator
  interventions fall): the goal question precipitates as a demanded seam
  slot — a design-arc admission with this probe as its evidence, the
  required-slots pattern applied to direction.
- **QUIET** (restatements correct, catches absent, operator still the
  instrument): the suspicion-signal confound is real; the direction-drift
  bullet in `answerable-not-felt.md` reverts to NO MECHANISM with this
  candidate recorded as killed and the reason attached — which is a
  closure, not a failure.
- **COULD NOT VERIFY** (too few established drift episodes land in the
  treatment window to read either way): reported as exactly that, with the
  episode count, never as either verdict.

**WHAT SURVIVES A QUIET — added 2026-09-20 from the operator's own
refinement, first-hand: "usually correct, not always — but then I can
adjust."** The adjustability depends entirely on the answer being STATED: a
wrong goal-read written down is graded in one glance and corrected in one
turn, where a wrong goal held silently drifts for an afternoon. So a QUIET
result kills only the TRIGGER-SUFFICES claim; it demotes the candidate from
removes-the-operator-trigger to cheapens-the-operator's-grading (they scan
a line instead of detecting drift from the work's behavior) — a separate
and weaker license the round weighs against its honest cost, which is that
it still spends operator attention at every seam. Under QUIET the
direction-drift bullet records the demotion, not a bare kill.

## What this probe cannot be asked

Whether the goal question is the BEST trigger content, whether babysitting
overall falls, and whether any of this transfers outside governed repos.
A FIRE here licenses one seam slot; it does not license seam-fired
self-reflection in general, which the research companion's independence
finding still bounds.
