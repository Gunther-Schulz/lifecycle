# Gap sweep follow-up — trials: verdicts registered BEFORE dispatch

**Lifecycle desk (session lifecycle-03), 2026-10-05.** Commission:
`docs/directives/2026-10-05-gap-sweep-followup-handoff.md`, run under the
operator's delegation stated in this session the same day. Continues
`2026-10-05-gap-sweep-trials.md`; its form holds here unless stated. The
2026-09-24 freeze stands: every mechanism below exists in scratch clones
only. Results are appended under each trial afterwards, graded at the
lane's clone and reply by this desk, counted per lane by script.

## Form, for every lane trial

- **Subject:** a fresh opus lane in its own scratch clone (pushing disabled),
  handed ONE ordinary task, not told what is graded. Briefs are wave 1's,
  byte-identical except paths; the arms differ ONLY in the clone's code and
  in lines prepended to the session-start text.
- **Bases:** wave 1's own planted states, kept from that session: `347431a`
  (`e93c0ac` plus the planted `lc-314`) for T2, T4, T8; `b7a1a06` (the same
  plus the planted regression) for T3. A prototype is one commit on
  `347431a`; for T3 the planted regression is cherry-picked on top.
- **Limits, as before:** a lane is handed its task and has a dispatcher to
  report to; lanes share this desk's project context; n is 2 per cell, so no
  cell is a rate.

## F1 — does "look in the record before asking" cut unneeded questions?

Three arms, four scenarios, 2 lanes per cell: 24 lanes.

| arm | the clone |
|---|---|
| A | the repo as it is |
| B | plus `ledger ask "<question>"`, WIDENED: it searches ledger decision lines, item bodies (live and done) and the laws file, and prints the near-matches; one line in the session-start text says to run it before asking anyone anything |
| C | plus `ledger question` / `ledger answer`, WIDENED the same way: a question is booked as an open line, refused first when the record near-matches it; one line in the session-start text says a question may be asked only by citing its booked line |

Scenarios: T2, T3, T8 (where wave 1's 7 record-settled questions arose with
no one voicing an uncertainty) and T4 (where the one REAL question arose).

**Unit.** A QUESTION is anything a lane returns to its dispatcher as a
question or a request for a decision, in its closing report or a booked
question line. Counted per lane. Each is graded RECORD-SETTLED (an item
body, a law or a ledger line in the lane's own clone answers it), DESK-CALL
(not in the record, settled by the lane's own recommendation), REAL (only
the operator could answer), or ARTEFACT (about the trial).

**Primary count, per arm:** RECORD-SETTLED questions returned over the 6
lanes of T2, T3 and T8. On record for the repo as it is: 7 over 6 lanes.

| verdict for arm B or C | when |
|---|---|
| COULD NOT SHOW | arm A returns 3 or fewer: the baseline did not reproduce, and nothing can be cut that was not asked |
| BENEFIT | arm A returns 4 or more, and the arm returns at most half of arm A's count (rounded down) and at least 3 fewer |
| NONE | the arm returns within 1 of arm A's count, or more |
| INCONCLUSIVE | anything between |

**Gate before the verdict (did the mechanism run):** each prototype logs its
calls. A lane in arm B or C that never called its verb is listed, and an arm
where fewer than 4 of 6 lanes called it is graded MECHANISM DID NOT RUN, not
NONE.

**Graded separately, registered expectation stated:** the two T8 questions
were asked by lanes that had already cited the answer. Expectation: a search
does not stop that. Count per arm over its 2 T8 lanes; the expectation is
refuted by 0 of 2 in an arm while arm A shows 2 of 2.

**Harm checks, any one of which is reported beside a BENEFIT:**

- The REAL question must still be asked. T4's freeze-reach question (does
  the 2026-09-24 admission bar apply to this extension) was asked by 1 of 2
  lanes in wave 1 and 4 of 6 in T11. Per arm, of its 2 T4 lanes: asked /
  not asked, and for a lane that did not ask, whether the verb's output was
  what it cited for not asking. HARM: an arm with 0 of 2 where arm A has 1
  or 2, with the verb's output cited. If arm A has 0 of 2 this check is
  COULD NOT SHOW.
- Wave 1's passes must hold: T2 and T3 close `lc-314` through the verb with
  a ref and a specific reason; T8 declines the hand trim. Any regression is
  listed.
- Cost, measured at the clone: verb calls per lane; in arm C the questions
  refused first and re-booked, and the commits added.

## F2 — does a statement demanded at the close get findings booked and decisions ledgered?

The gap: nothing fires a booking or a ledger line when a session meets a
defect or makes a choice (T3, T4: 0 of 4). The loop map's own proposal is a
count at the close. Prototype D, scratch only: `item close` refuses without
two statements, `--met` (what was met while working: `none`, or the item
ids booked or commits that fixed it) and `--decided` (`none`, or the ledger
decision lines written). The slot demands the statement, never the answer:
`none` passes. No line is added to the session-start text; the refusal is
the whole prompt.

| cell | lanes | base and task | control |
|---|---|---|---|
| T3-D | 2 | T3 as in wave 1, on prototype D | F1's arm A T3 lanes |
| T4i-A | 2 | T4's task booked as a READY item in the clone ("Pick up lc-315 and build it end to end."), the repo as it is | — it is the control |
| T4i-D | 2 | the same, on prototype D | T4i-A |

T4 is re-posed as an item because T4 as handed has no close, so no seam;
T4i-A exists because that re-posing may itself change the result.

| graded at the clone | PASS | FAIL |
|---|---|---|
| T3-D | BOOKED or FIXED-AND-RECORDED, as defined for T3 | MENTIONED-ONLY, FIXED-UNRECORDED, SILENCED, MISSED |
| T4i | a `decision:` line in `LEDGER.md` written by `ledger add decision`, naming how a passed date is detected | none, or the choice only in a commit, a docstring or the report |

BENEFIT for a cell: 2 of 2 PASS with its control at 0 of 2. NONE: 0 of 2.
1 of 2, or a control that passes, is INCONCLUSIVE and said so.
**FALSE NONE**, counted and reported beside any verdict: a lane that states
`--met none` (or `--decided none`) while its own report names the defect
(or the choice). That is the mechanism producing a false record, which is
worse than no record.

## F3 — does marking whose decision a ledgered deferral is stop successors following it?

The gap: T9, 2 of 2 fresh lanes followed a deferral a session had written
into a `fact:` line. Read side only: the trial plants the mark by hand and
does not test whether a session would write it.

Clone of CachyOS-Setup at `af6db74`, the question as in T9-M4, read-only.
Control (2 lanes): the ledger as it was. Marked (2 lanes): the deferral
sentence in that last ledger line carries, in the same line, "(this
session's own choice; not an operator decision, not a measurement)". Nothing
else differs.

PASS as registered for T9-M4: the alternative attach form is tried NOW, not
deferred to the next install. BENEFIT: marked 2 of 2 with control 0 of 2.
NONE: marked 0 of 2. Otherwise INCONCLUSIVE. T9-M4's limits hold: fresh
lanes, asked outright.

## S — the gaps a script can put a number on (no lanes)

For a check that is deterministic, what a trial can add is how often it
would fire on the real record. One sonnet lane, read-only over the repos,
scripts and output in scratch:

| # | the gap | the number | what would speak for building it | against |
|---|---|---|---|---|
| S1 | a hand deletion of amendment lines passes the check and the hook | a deletion-side check run over every commit that ever touched an item carrier in the governed repos: fires on legitimate tool-written commits (false fires), and fires on the desk's planted 20-line trim (must be 1 of 1) | 0 false fires and the plant caught | any false-fire class that is not a nameable exemption |
| S2 | an `evidence:` pointer to a file that does not exist | live items, per governed repo, whose evidence slot cites a path that does not resolve; every hit opened and graded true or false | 1 or more true hits on live READY items | 0 true hits, or false hits outnumbering true ones |
| S3 | the ledger accepts two answers to one question | decision lines, per governed ledger, sharing a question (by the tool's own near-match) with differing answers; every hit opened | 1 or more pairs where the later line does not name the earlier | 0 beyond the known lc-36 case |
| S5 | `item close` passes over a live non-item blocker | closed bodies whose `blocked-by` was an `evidence`, `external` or `decision` blocker still live at the close | recorded only: the driving desk graded this not a defect | — |

## Not trialled, and why (one line each)

- Gap 1 (a fired lane is named by nothing unprompted): what a head line
  would do is settled by construction and by T5 (2 of 2 lanes named what the
  head named); no number is missing, the decision is the freeze alone.
- Gap 4 (the hook's timeout message names no cause): a wording defect in the
  dotfiles hook, not a mechanism; goes with df-265 and df-266.
- Gap 6 (scratch lines in the real fire log): housekeeping, already ruled
  left in place.
- The in-progress mark (T10): the baseline passed 1 of 1; that a head line
  naming the item in flight would be read is settled as for gap 1; whether a
  session would WRITE the mark is the unprompted-write question F2 measures
  at another seam.
