# 2026-10-04: refocus design round 2. Which demand at which seam converts a due read into an act

**Desk:** lifecycle-4f (Opus 5.5), the executing peer desk of
`docs/directives/2026-10-04-refocus-opus-desk-handoff.md`, wave 1.
**Status:** PROPOSAL, revision 1. Nothing here is decided. It returns to
the judgment desk (tmp-ad) for grading at the artifact before anything is
built, and no line of it is ledgered until then.
**Items:** lc-276 (demand at moment), lc-277 (seam trigger), one question.

## 0. What this round stands on, measured today

Every figure below comes from `tools/fire-window-tally.py` (committed with
this file) unless it carries another label.

**0.1 This is the SECOND round on this question, and the first one
shipped.** The round of 2026-09-24
(`docs/directives/2026-09-24-refocus-design-round.md`, rev 2 plus judge
rulings) decided R1 to R9. R2 (session key on fire lines), R1 (tier-1
notices removed) and R3 (goal print at `item close`, `arc advance`,
`arc narrow`) were built and closed as lc-286, lc-287, lc-288. lc-276 and
lc-277 stayed open because that round left the DEMAND leg open: its
evidence had been tautological. This round consumes what the shipped set
has done since.

**0.2 The post-ship window, 2026-09-25 to 2026-10-04, roster repos only:**

| quantity | value |
|---|---|
| verb runs (statusline ticks excluded) | 1246, across 10 repos and 87 repo-session pairs |
| surfacings (the informative, tier-2 notice) | **1** (`arc narrow` surfacing `arcs`) |
| `kind read` runs | **0** |
| goal-seam fires | 18, in 2 sessions (lifecycle 14, statiker 4) |

Control, same tool, the pre-R1 window 2026-09-20 to 2026-09-24: 386
surfacings and 8 reads, which are the known figures. The instrument sees
both quantities where they exist, so the 1 and the 0 are readings.

**0.3 What those four numbers say.**

- **lc-276's falsifier cannot be reached.** It needs 30 informative
  surfacings (fewer than 1 read in 10 kills the notice leg). The channel
  produced 1 in ten days of normal work. At that rate the window is most
  of a year. The notice leg is neither confirmed nor refuted: it is
  starved. (DERIVED from the rate; the rate is measured.)
- **The read verb is not used.** 0 `kind read` runs in 87 sessions, against
  208 `item slots` runs in this repo alone. Sessions read through the verb
  that serves the act in hand, never through a verb whose only purpose is
  reading. That is the O6 design's kill condition 2 in the field.
- **The goal print fires where traffic is thin.** 18 fires, 17 of them at
  `item close`. The high-traffic acts where a session writes from memory
  are `item add` (72 runs in the window), `item park` (42), `item amend`
  (29) and `ledger add` (14 in statiker alone). The print's EFFECT is
  ungraded: the treatment log holds two rows, both pre-move.

**0.4 The one form that does convert, already in this repo.** Every
measured instance where a due read became an act has the same shape
(`docs/required-slots-as-an-autonomy-lever.md`, the 2026-09-18 table; R7 /
lc-289):

> the VERB retrieves the matching entries from the record, prints them, and
> REFUSES until the call disposes them in writing.

`item add` does it against live items (`--join`). `ledger add decision`
does it against prior decisions (R7). The harness does the same thing one
level out: the reading gate refuses a first write until the named files
were read. In none of these is the session asked to go and retrieve.

**0.5 From outside** (`docs/audits/2026-10-04-substitution-prior-art-research.md`,
RELAYED, lane grades as stated there): seam-time demand against
session-start loading is measured nowhere; the trigger must be the
environment's because the model's sense of needing the record is what
fluency suppresses; a demand should be a separate write step, not a format
imposed inside reasoning.

**0.6 One specimen of a demanded derivation working by hand** (RELAYED,
n=1, `docs/audits/2026-09-29-operator-trigger-specimen-cachyos-setup-71.md`
and lc-301): a per-event derivation demand installed by hand joined a READY
item the record had held through twelve operator pushes.

## 1. The answer this round proposes

**A due read becomes an act when the verb does the reading and demands a
written disposition of what it found. It does not become one when the
session is told a read is due.**

So the demand is a DISPOSITION OF A RETRIEVED SLICE, and the seam is an act
lifecycle already owns at which a session otherwise writes a claim from
memory into a carrier. Three consequences:

1. The notice leg and the stand-alone read verb get no further investment.
2. New demand work means adding a RECORD SOURCE to a join that exists, at a
   verb that already demands prose. It never means a new flag, a new slot
   or a new verb (the 2026-09-24 round's reuse and one-demand-per-verb
   rules stand).
3. Law 26's first question is answered by construction: the default (the
   verb reads) makes the remembered read unnecessary. What must be written,
   and whose absence is computable, is the disposition.

## 2. The decisions

**D1. Adopt section 1 as the round's principle, and record it as the answer
to lc-276's blocker.**
- RECOMMENDED: yes.
- Falsifier: an informative notice that is followed by a read at a rate the
  old 1-in-10 criterion accepts, on any window that reaches 30. The counter
  stays in place, so this can still fire.

**D2. The notice leg: starved, not refuted. Stop building on it.**
- RECOMMENDED: lc-276's 1-in-10-over-30 falsifier is recorded as COULD NOT
  VERIFY BY STARVATION, with the measured rate. Tier-2 surfacing and the
  counter stay as built (they cost nothing when silent). `kind read` stays
  (lc-255 shipped it; removing it is a dependents question nobody has
  asked, and it harms nothing).
- lc-256 (the windowed counter) loses its reason: a window over a channel
  carrying 1 record measures nothing. Recommended disposition: DROP, with
  this measurement as the reason. Its one defect-shaped part, a malformed
  fire-log line graded as a finding, is re-booked alone if the judgment
  desk wants it kept. lc-256 is another desk's booking in this carrier, so
  the drop is the judgment desk's call, not mine.
- Not ruled out by this: making the tier-2 MOMENT a gate (the O6 design's
  B2, "you are about to write X; these kinds are read first"). That is a
  harness hook in dotfiles, outside this working copy, and is named in
  section 5.

**D3. The first new demand: a `decision` blocker is joined against the
ledger at the door.**
- What exists: booking, parking or amending an item with
  `blocked-by: decision <question>` already refuses without a
  `--not-derivable` statement (`decision_not_derivable_unstated`, lc-169).
  The statement's content is unchecked. The blocker later clears by
  question equality with a ledger line.
- What is proposed: at the same three verbs, run R7's decision matcher
  (the lc-289 comparator, cap 0.05, unchanged) over the blocker's question
  against the ledger's decision lines. On a near-match the verb prints each
  matching line and refuses until the `--not-derivable` text cites each one
  by its ledger line reference. No match writes as today.
- Why this seam: it is specimens 1 to 4 of the design of record in the
  carrier's own vocabulary. A decision blocker is the written form of "this
  cannot be settled from the record", stated from memory at the moment the
  record could refute it. It is also where an operator interaction gets
  queued, and lc-161's baseline puts RATIFICATION at 11.0% of operator
  messages.
- Reuse audit: one existing matcher, one existing slot, one existing
  refusal site. The new thing is a conditional content check on a slot the
  verb already demands. It fires only when the matcher found something.
- **Pre-registered probe, run BEFORE any build (admission bar):** replay.
  For every decision blocker ever booked in the roster repos' item
  carriers, take the ledger as of that blocker's booking commit and run the
  comparator. Hand-grade each fire as TRUE (the matched line answers or
  bounds the question) or FALSE.
  - PASS: at least 5 TRUE fires, and TRUE fires outnumber FALSE.
  - FAIL: fewer than 5 TRUE fires (the seam is too rare to earn a refusal),
    or FALSE at or above TRUE (repair is at the comparator per law 26,
    never the threshold per law 11; one repair attempt, then decline).
  - COULD NOT VERIFY: the as-of ledger cannot be reconstructed for more
    than a third of the population.
  The replay is read-only over git history. It is a measurement, not a
  mechanism, so it is not held by the freeze.
- Not known today, and the replay is what supplies it: how often a decision
  blocker was already answered AT BOOKING. The census figure (8 of 57
  ANSWERED) counts blockers answered at any time since, so it is not that
  rate.

**D4. The second candidate, held behind D3's result: the intake join reads
two more sources.**
- `item add`'s `candidates()` reads live items only. The amendment record
  (55% of completed items amended; reasons on file include "booked against
  a premise this repo had already killed" and "the decision it named was
  answered by the operator this afternoon") points at two unread sources at
  booking: ledger decisions and closed or dropped bodies.
- RECOMMENDED: PARK, named evidence D3's replay. Both use the same
  comparator family; if D3's replay fails on FALSE fires the wider join
  fails harder, and if it passes, the same replay harness extends to this
  population at marginal cost. Two demands at `item add` in one round would
  also break the one-per-verb rule, since D3 already touches `item add`.

**D5. The goal seam (lc-277): no change to the mechanism; derive and grade
the rows that exist; say honestly where the window is heading.**
- The treatment arm's window is 5 treated sessions or 4 weeks from
  2026-09-20, so it closes 2026-10-18. Post-move it holds 2 sessions
  (0.2); a third, on 2026-09-24, carries 4 `arc narrow` fires and is the
  desk that built the print, so it is excluded by the directive's
  independence rule. Unless three more governed sessions cross a goal seam in two
  weeks, the arm reports COULD NOT VERIFY on count alone.
- RECOMMENDED now: derive the two post-move rows from the fire lines and
  have them graded by a desk other than the treated ones (the directive's
  independence rule; neither session is this desk). That is the judgment
  desk's or a lane's read of two transcripts, and it is owed whatever else
  is decided.
- NOT recommended: adding the goal print to `item add` or `ledger add` to
  raise traffic. Booking already demands a `goal:` slot; a print there adds
  presence where a demand exists, and it would change the arm mid-window.
- The DISPATCH seam that lc-277's done-criterion names lives in
  dispatch-guards. A search of that repo's item carrier for `goal-seam`,
  `goal seam` and `lc-277` finds nothing, while the same search finds its
  `goal:` slots, so the item the 2026-09-24 round said was booked there is
  not there under any of those names. The write is outside this working
  copy. It stays the judgment desk's obligation to place; lc-277 stays open
  on it.

**D6. Sequence: lc-161's AFTER arm for the 2026-09-24 ship set runs BEFORE
anything from this round ships.**
- The handoff orders round, ship set, then the AFTER arm. Two records in
  this repo point the other way. The freeze holds every new mechanism
  "until the lc-161 after-measurement reports" (lc-284, lc-296, lc-300
  blockers, all on that one question), and the arc's own NEXT line names
  the AFTER arm as the successor desk's first act once a post-ship window
  exists. One exists: ten days, 87 repo-session pairs.
- RECOMMENDED: run AFTER-1 now, same tool and sampling as the baseline
  (`tools/operator-interventions.py`, window 2026-09-25 to 2026-10-04,
  ALREADY-IN-RECORD sampled larger per the item's done-criterion). It
  grades R1 to R3 on their own, and it becomes the clean BEFORE for
  anything this round ships. Shipping first would leave two ship sets in
  one after-window and no way to tell them apart.
- Expected result, stated before the run: no detectable change. R1 removed
  noise and R3 fired 18 times in two sessions. By the item's own rule a
  drop inside sampling error is COULD NOT VERIFY. That outcome still
  discharges the gate question; it does not answer it in favour of a
  release.

**D7. The freeze exit for D3 is not mine and not derivable.**
- D3 is new reach, so it needs an exit the way R7 did. The freeze is an
  operator-pinned decision. Under the corpus floor an act reversing a pin
  travels to the operator first-hand, at the driving desk.
- RECOMMENDED form of the ask, once D3's replay and AFTER-1 are both in
  hand: a NARROW exit for D3 only, on the replay's PASS, shipped lc-289
  style (red-first plant and control, prove-rows pair, over-fire rate
  reported). If the replay fails there is no ask.

**D8. `/standort` and R4 (resume read-back): unchanged.**
- `/standort` stays manual until 4 counted runs exist (2026-09-24 R5).
- R4 stays parked on the treatment arm. Under section 1 its buildable form
  is already visible: a resume verb that prints the desk's recorded state
  and demands a disposition of each open line, which is a join, not a
  restatement. That is noted so the park is cheap to lift; it is not
  proposed.

## 3. The transition table (sign-off requirement)

Home of this table: this file. Only D3 adds an arrow.

| arrow | verb | record written | check that proves it | OBSERVER |
|---|---|---|---|---|
| a `decision` blocker is written and the ledger holds a near-match | `item add`, `item park`, `item amend` (the three existing blocker-writing sites) | the refusal, or the `not-derivable:` line carrying each matched ledger reference | red-first: a planted near-match refuses, and passes once cited; a control with no match writes as today; prove-rows pair per lc-142 | the verb invocation |
| a `decision` blocker is written and nothing matches | same | as today | the control arm above | the verb invocation |
| the replay probe runs | a script under `tools/`, committed | an audit in `docs/audits/` and one ledger line | the as-of ledger reconstruction is shown on one blocker known to have been answered before booking, if one exists, else the absence is stated | this desk, at the wave the judgment desk authorizes |
| the two post-move treatment rows are derived | `tools/fire-window-tally.py` for the seam counts | rows 3 and 4 of `docs/audits/drift-treatment-log.tsv` | seams equal the fire-line count per session | the grading desk named in D5, not the treated session |

## 4. What I did not verify, and what this design does not rule out

- I did not open the two post-move sessions' transcripts. Nothing above
  claims the goal print changed or failed to change anything.
- The test suite writes to the live fire log: 1831 non-roster verb runs on
  2026-09-25, 34,288 in the five days before. The per-repo tally filters
  them out, so no figure above includes them. Whether the suite still does
  this today is unverified (no suite run has happened since 2026-09-25 in
  the log). It is a defect candidate for a separate item.
- D3's refusal rests on a comparator tuned on ledger-to-ledger questions.
  Blocker-to-ledger may behave differently. The replay measures exactly
  that before anything is built.
- Section 1 is drawn from this stack's own instances plus adjacent outside
  evidence. Nothing published tests it. lc-302 (the seam-versus-start
  experiment) remains the discriminating measurement and stays parked
  behind lc-277.

## 5. Obligations that land outside this working copy

Named so they are not read as discharged here:

- the dispatch goal seam (dispatch-guards): not booked, see D5;
- a tier-2 write gate (dotfiles hook), if D2's "not ruled out" is ever
  taken up;
- the session-start banner's carrier read: see the report to the judgment
  desk of the same date. The cause is in this repo and is a defect fix
  here; the 0.5 s timeout it trips is in dotfiles.

## 6. Reproduce

```
python3 tools/fire-window-tally.py --since 2026-09-25
python3 tools/fire-window-tally.py --since 2026-09-20 --until 2026-09-25   # control
python3 plugin/cli/lifecycle item slots lc-276
python3 plugin/cli/lifecycle item slots lc-277
```
