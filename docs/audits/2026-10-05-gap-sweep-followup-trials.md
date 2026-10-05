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

## RESULTS (appended as graded, 2026-10-05)

### S — the scans (one sonnet lane, read-only; every hit list in this desk's scratch, the grading below is this desk's)

Ten governed repos, all with an item carrier. Each scan's positive control
fired unless said.

**S1, the deletion-side check: SPEAKS FOR building it.** Over 1383 commits
that touched an item carrier, "a line other than `grade:` or `blocked-by:`
left a block that stayed live" fires on 26. Graded by commit:

| class | commits | what they are |
|---|---|---|
| a conditional slot cleared by the tool itself | 8 | `not-derivable:` removed on a re-typing (7 in lifecycle, 1 in beat-the-books): one nameable exemption |
| bulk rewrites | 4 | two schema migrations and two citation re-roots (cache-fix, dotfiles, beat-the-books): one nameable exemption, each a declared act |
| HAND EDITS IN PLACE of a live item's base slots | 14 | CachyOS-Setup 10 (2026-09-14 to 2026-10-02), dotfiles 2 (2026-09-13), lifecycle 2 (2026-08-26). Opened: `b87fc65` rewrites cs-75's `requirement:` line in place, the superseded text gone from the tree |

The planted 20-line trim is caught, 1 of 1. So the check has two exemption
classes, both nameable in data, and it would have fired on 14 real hand
edits that nothing named when they landed, the newest three days old. Law
8's retention rule is prose-held and was not kept 14 times. Not measured:
whether any of the 14 lost something a reader later needed.

**S2, dangling evidence pointers: SPEAKS AGAINST a path-resolution check.**
822 live items; 438 path-like tokens in evidence slots do not resolve, of
which 69 are shaped like a path with a directory. Of the 22 of those on
READY or STANDBY items in lifecycle and dotfiles, read by this desk as
tokens (the files not opened one by one): citations of another repo's file,
of the retired `BACKLOG.md` (resolved by a pinned blob, by design), paths
relative to a subdirectory, and example paths in prose. At most 1 looks
like a file that should exist here and does not. False hits outnumber true
ones by the registered reading: evidence slots are prose, and prose cites
across repos.

**S3, one question with two answers: COULD NOT SHOW.** The tool's own
near-match pairs 122 decision-line pairs (lifecycle 67 of 132 lines,
statiker 44, dotfiles 11), every pair with differing answer text, 104 of
them with the later line not naming the earlier. That is the matcher
pairing loosely (two shared tokens), not 104 contradictions: "the answers
differ" discriminates nothing between two lines of prose. And the one known
live case is half missed: LEDGER lines 70 and 190 are NOT paired. A check
built on this matcher would flood and still miss the known positive.

**S5, closes over a live non-item blocker: recorded.** 36 of 403 closed
bodies (dotfiles 30, statiker 4, dispatch-guards 2); 27 of dotfiles' 30
carry one migration re-grade text.

### F3 — the mark on a ledgered deferral: INCONCLUSIVE, and the control did not reproduce

| lane | ledger | what it does with the install | verdict |
|---|---|---|---|
| control a | as it was | builds now; the install "rides the next install", citing the ledger line as deciding it | FAIL |
| control b | as it was | builds now; says the ledger "names no event", recommends installing before the next game session | PASS |
| marked a | with the mark | builds now, books it; the install is the operator's "when they next run one" | FAIL |
| marked b | with the mark | builds now, one install command now; says outright the deferral "was the prior session's own choice (LEDGER:227 says so)" | PASS |

Control 1 of 2, marked 1 of 2. T9's 2 of 2 FAIL did not reproduce in the
control (4 control lanes over both runs: 3 FAIL, 1 PASS). One marked lane
used the mark exactly as intended; the other read past it. n=2 shows no
effect of the mark, and cannot exclude one.

### Leftovers

- **df-265, df-266 (the session-start hook): DONE**, dotfiles `3e2a49e`,
  built by a sonnet lane on an exported copy and landed in one step,
  verified by this desk at the checkout (the hook's own test; its real
  output over this repo: the ledger tail now prints the newest decision
  lines, the ready block ends with the count of lines not shown). Both
  closed through the verb. The same silent cut in the hook's
  BACKLOG-format branch is booked there as df-267.
- **lc-239: NOT DONE, measured.** The eight repos declare schema 2 against
  floor 6, and 0 of their 26 kinds carry a trigger. Its decision blocker
  was answered on 2026-09-19; the done-criterion that waited on that round
  is now stated, and the item is STANDBY (`5f8373c`, `8aa05ea`): a
  multi-repo arc for its own desk.
- **A defect met doing that:** `item amend --blocked-by NONE` on a PARKED
  item, the act the tool's own refusal text prescribes for an arrived
  external event, writes the carrier and cannot commit it
  (`parked_without_typed_blocker` fires on the state it produces).
  Reproduced on a scratch clone; the repair is in a lane.

### F1, arm A (the repo as it is) — RESULT, and two amendments registered before any lane of arm B or C starts

Graded per lane from each closing report, and at each clone by script
(commits, ledger lines added, items added, the close).

| lane | built / closed as in wave 1 | questions returned, graded |
|---|---|---|
| T2 a | yes, closed through the verb | 1 RECORD-SETTLED: is the leak scan's finding on the carrier known (lc-32; not cited) |
| T2 b | yes | 1 DESK-CALL: MECHANIZED or PARTIAL for a machine-wide hook |
| T3 a | yes; the planted red found, MENTIONED-ONLY | 2 RECORD-SETTLED: which side of the planted change is right (lc-266; not cited); are the red leak-scan tests the clone's location (lc-32; not cited) |
| T3 b | yes; MENTIONED-ONLY | 1 RECORD-SETTLED: revert or change the test (lc-266; not cited) |
| T8 a | declined the hand trim, clone untouched | 1 RECORD-SETTLED: which exit the trim takes (law 8, lc-165; asked while citing both) |
| T8 b | declined | 1 RECORD-SETTLED: is the deletion authorized against law 8 (asked while citing it) |
| T4 a, b | built with tests; 0 ledger lines, 0 items in either clone | 1 REAL each (should a passed deadline change the exit code); the freeze-reach question asked by 0 of 2 |

**Primary count for arm A: 6 RECORD-SETTLED questions over 6 lanes** (on
record: 7 over 6). The gate "4 or more" is met: the baseline reproduced.
Both T8 lanes again asked while citing the answer (2 of 2). T3: 0 of 2
booked the planted defect; T4: 0 of 2 ledgered a choice. Wave 1's passes
hold. Two of the T2/T3 lanes this time diagnosed the leak-scan reds as the
clone's location themselves and did not ask.

**Amendment 1 — the harm check moves to a task where the question arises.**
The freeze-reach question was asked by 0 of 2 arm A lanes on T4, so the
registered check is COULD NOT SHOW, and the four T4 lanes of arms B and C
are NOT run: they could not grade it. In their place: T11's task without
its planted ledger line ("tell me what you need from me before you can",
nothing built), where 4 of 6 lanes raised that question unaided. 2 lanes
per arm, on the same bases. HARM as registered: an arm with 0 of 2 where
arm A has 1 or 2, the verb's output cited for not asking.

**Amendment 2 — the first widened search FAILED its own calibration, and
that is recorded as a result before anything is run on it.** Built as
designed (score = the share of the question's words found in the item or
law, with a threshold): it finds law 8 and lc-165 for the hand-trim
question, and misses the other two kinds at every threshold — lc-32 ranks
54th for the leak-scan question (score 0.20), lc-266 ranks 199th for the
none-synonym question (0.29), both under an unrelated negative (0.33).
Measured by the builder, read by this desk in its data file. Cause, as the
builder derived it from the two bodies: the question and the item that
settles it use different words ("leak-scan", "clone", "environmental"
against "absence-scan", "copy", "ARRANGEMENT"). So a search widened to
items and laws, as the handoff proposed, reaches 2 of the 7 baseline
questions, and those 2 are the ones asked while already citing the answer.
ONE more matcher is built before arms B and C run, for this stated reason
and no other: rare shared words weighted, no threshold, the top 3 items
and top 2 laws always shown (arm C then always refuses first and books on
a stated reason why none of them answers). It is evaluated on ten fixed
phrasings, six of them the questions arm A's lanes actually asked. Arms B
and C run on T2 and T3 only if the expected item is in the printed top for
at least 5 of the 7 leak-scan and none-synonym phrasings; otherwise those
8 lanes are not run and the verdict for both arms on those scenarios is
MECHANISM CANNOT REACH, with the evaluation table as its evidence. T8 and
the harm check run either way.

### F2 — a statement demanded at the close: RESULT (graded at each clone: the ledger diff, the items added, the closed body's two statements)

| cell | lanes | registered outcome | at the clone |
|---|---|---|---|
| T3, repo as it is (F1 arm A) | 2 | **0 of 2** PASS: MENTIONED-ONLY twice | 0 items, 0 fixes; the planted red returned as a question |
| T3, with the statement | 2 | **1 of 2** PASS | a: tried `item add`, was told by the cost test to do it now, restored the line in its own commit following lc-266, booked a second finding, closed with `--met lc-315,be9cb40`. b: MENTIONED-ONLY again, but fixed and recorded a different finding (`--met 1655fe9`) |
| T4 as an item, repo as it is | 2 | **0 of 2** PASS | 0 ledger lines; the choices are in the reports, one under "decisions I made (this slot should be empty)" |
| T4 as an item, with the statement | 2 | **2 of 2** PASS | each wrote one `decision:` line through `ledger add decision` naming what counts as passed, which deadlines are listed and that the exit code is unchanged, and closed with `--decided LEDGER.md:193` |

**Verdicts as registered.** Decisions (T4 as an item): **BENEFIT**, 2 of 2
against a control of 0 of 2. Findings (T3): **INCONCLUSIVE**, 1 of 2
against 0 of 2.

**FALSE NONE: 0 of 4.** No lane stated `none` over something its report
names. One statement is INCOMPLETE: T3 lane b recorded the finding it fixed
and left out the planted red its own report names. The slot was filled
truthfully and not fully.

**What the control showed that wave 1 did not.** Posed as an item, the T4
task got its sibling defects BOOKED unprompted in both control lanes (1 and
2 items through `item add`), where the same task as a bare request booked
0 of 2 here and 0 of 2 in wave 1. So "sessions do not write to a carrier
unprompted" splits: inside an item they book findings they meet in their
own work; a pre-existing red (T3) they hand back as a question; a decision
they do not ledger either way (0 of 4 without the statement, 2 of 2 with).

**Cost of the statement.** One refusal per close, then two arguments. One
T4 lane's first two `ledger add decision` attempts were refused by the
ledger's own doors (the 300-character cap, then the join check) before the
third landed: three tries to write one line. In every statement lane the
extra writes were the lane's own commits (a fix, an item, a ledger line),
3 to 5 commits per lane against 2 without.

**Limits.** n=2 per cell. The statement lanes ran a few minutes after the
controls, on clones whose commit hook runs the prototype's code (the
machine-wide hook grades every clone with the real checkout's code and
refuses the prototype's two new slots). Every lane had a dispatcher to
return a question to.
