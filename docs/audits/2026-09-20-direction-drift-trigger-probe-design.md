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
into a rate. INSTRUMENT LIMIT, load-bearing: the session-search MCP's
declared scope excludes queue-operation records — exactly where operator
MID-TURN interjections live, and pressing a drifting session is
characteristically mid-turn. The baseline sweep therefore reads raw session
JSONL, not the search tool, or it under-counts the very events it exists to
count. A zero from the search tool over this class is an instrument reading,
not an absence.

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
data spans MULTIPLE project corpora, not one.

**TREATMENT (prospective, mechanism must exist in trial form).** Sessions
run with a seam-fired goal-question demand: the investigation record's GOAL
slot re-read and a one-line "how the current move serves it" written at each
seam (round open, wave authorization, record update). No hook needs building
for the trial — a directive in the brief suffices for N sessions — which
keeps the probe ahead of any design-arc admission decision rather than
depending on one.

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
