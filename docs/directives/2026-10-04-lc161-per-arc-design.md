# 2026-10-04: lc-161 in per-arc form. Design proposal

**Desk:** lifecycle-4f, wave 3 of
`docs/directives/2026-10-04-refocus-opus-desk-handoff.md`.
**Status:** REVISION 2, GRADED. The judgment desk (tmp-ad) approved
revision 1 (`c8710e2`) with one amendment, made here: delivery of a
refusal is separated from compliance with it (section 3). It also ruled
questions 1 and 2 of section 7. lc-161 takes this form. Design only:
nothing builds, nothing releases.

**The decision this executes** (operator, 2026-10-04, relayed by the
driving desk under the delegation on this desk's record; ledgered): lc-161's
later arms run as a per-arc comparison, like work against like with the
mechanism on and off. Not an all-sessions before/after, and not a longer
machine-wide window. Basis: `docs/audits/2026-10-04-lc161-after1.md`.

## 0. The two inputs this design must absorb

1. **One hard arc moves the machine-wide figure more than any mechanism
   here.** AFTER-1: 11.64 operator messages per 100 turns against 5.75,
   five sessions carrying 311 of 514 messages. Whatever compares work must
   compare it inside one stretch of like work.
2. **A fired mechanism is not a delivered one.** The goal print reached the
   session at 2 of 18 counted seams; the rest were cut by `grep` or `tail`
   (`docs/audits/drift-treatment-log.tsv` rows 3 and 4, lc-306). An arm
   must show delivery before its effect is graded.

## 1. The form: a crossover inside the arc

**The arc is its own control.** Within one arc, each session is assigned
to ON or OFF. The comparison is ON sessions against OFF sessions of the
same arc, and the verdict is taken over arcs.

Why this and not matched pairs of arcs: a matched pair needs someone to
judge that two arcs are alike, which cannot be pre-registered, and the
"off" arc is always an older one, which puts time back in as a confound.
Inside one arc the work, the repo, the operator's attention and the state
of the record are the same for both arms.

## 2. What an arc is, for this measure (the matching rule)

A session belongs to a **declared arc** when its transcript names one of:
- a lifecycle arc file (`arcs/<slug>.md`), or
- an investigation record (`<project>--<arc>.md` in the investigations
  directory).

A session naming several is assigned to the one it names most often; a
tie excludes the session, counted. A session naming none is not in any
arc.

Measured today over the 116 sessions of at least 20 turns in the baseline
and AFTER-1 windows (machine-computed, transcript scan for the 12 known
arc and record paths):
- 49 of 116 (42%) name a declared arc or record;
- they sit in two repos. One CachyOS-Setup arc family accounts for most
  of them through five overlapping records; lifecycle accounts for the
  rest;
- so today the machine holds roughly three distinct declared arcs a
  month, not eleven.

That is thin. Section 6 says what follows from it.

## 3. Assignment, exposure and delivery

**Assignment is made by the verb, never by the caller.** A mechanism under
trial computes its arm from the session id it already knows (R2) and its
own name: a hash, ON on even, OFF on odd. No environment variable, no
flag, nothing a session or a brief can set. The fire line records
`arm=on` or `arm=off`.

**OFF logs what it withheld.** At each moment the mechanism would have
acted, an OFF session writes `withheld=<mechanism>` and does nothing else.
That gives both arms the same exposure record: a session where the moment
never came up is in neither arm.

**Delivery is proven per mechanism class, from the transcript:**

| class | DELIVERED means | COMPLIED means |
|---|---|---|
| a print | the mechanism's marker text appears in a tool result of that session | not applicable |
| a refusal | the refusal's text appears in a tool result of that session | delivered, AND the same verb was re-invoked carrying the demanded disposition |

A fire with no delivery is its own bucket, FIRED-UNDELIVERED. It is never
pooled into ON or OFF.

**A refusal that was delivered and not complied with is DEFIED, and it is
counted per arm beside the others.** The session saw the refusal, did not
re-invoke, and routed the work around it. Revision 1 folded that into
non-delivery. That would have hidden the one result that could kill the
demand leg: a demand that arrives and is walked past. Delivery is what
the eligibility rule and the delivery gate read; the defied count is
reported, never used to drop a session.

## 4. Eligibility

- **Session:** at least 20 assistant turns; in a declared arc; at least one
  exposure (a fire or a withheld line); for ON, at least one delivery.
- **Arc:** at least 2 eligible ON and 2 eligible OFF sessions.

## 5. The outcome, the criterion and its thresholds

**Outcome:** operator messages per 100 assistant turns, from
`tools/operator-interventions.py` unchanged, pooled over each arm's
eligible sessions within the arc. For arc *b*: d_b = rate OFF minus rate
ON. Positive means the mechanism reduced operator messages.

The class breakdown is NOT part of the criterion. AFTER-1 showed three
raters filling a rubric gap three ways. If a later arm wants it, the
rubric first gains a label for a bare operator question, and a
double-rated sample must be reported with its agreement.

**Pre-registered, per mechanism:**

| verdict | condition |
|---|---|
| gate: NOT DELIVERED | fewer than half of the ON arm's fires were delivered. The arm stops here and reports delivery, not effect. |
| HELPS | at least 6 eligible arcs, d_b positive in all, or in all but one when there are 8 or more (one-sided sign test at or below 0.05), AND the pooled reduction is at least 20% |
| NO DIFFERENCE SEEN | at least 6 eligible arcs and d_b positive in half or fewer |
| COULD NOT VERIFY | fewer than 6 eligible arcs when the window closes, or any result between the two rows above |

**Window:** until 6 arcs are eligible, or 12 weeks, whichever comes first.

## 6. What this design cannot do, said before it is relied on

- **It will usually return COULD NOT VERIFY at today's arc rate.** About
  three declared arcs a month, each needing four substantial exposed
  sessions, makes six eligible arcs in twelve weeks unlikely. The honest
  expectation, stated in advance: COULD NOT VERIFY for lack of arcs.
- **It cannot grade what already shipped.** R1 removed something and has no
  OFF arm. R3 could be switched from now on, but it is mostly undelivered
  (lc-306), so it would stop at the delivery gate.
- **It only grades mechanisms that ship with the arm switch.** The switch
  (the hash, the `arm=` and `withheld=` fields) is code in each trialed
  mechanism. That is a build, and it is not in this wave.
- **Carry-over runs toward the null.** A mechanism that improves the record
  helps the OFF sessions that follow in the same arc. So HELPS is
  conservative, and NO DIFFERENCE SEEN means no within-arc difference was
  seen, not that the mechanism does nothing.
- **A refusal that protects an invariant is never switched off.** Only a
  mechanism under trial is.
- **Not verified:** whether a subagent's verb sees its parent's session id,
  which decides whether a lane inherits its desk's arm.

## 7. Questions back to the judgment desk

**Rulings, 2026-10-04 (judgment desk):** question 1 YES, as a labelled
secondary beside the per-arc verdict and never the verdict, the label
stating its use (whether more declared arcs are worth waiting for).
Question 2: the arm switch rides each future mechanism's ship set and the
exit ask for that mechanism names it; nothing is built now. Question 3 is
at the operator. Question 4 is noted and not opened. The questions stand
below as asked.

1. **A wider block as a second readout?** Repo-and-week blocks are
   plentiful: 9 of 19 held at least four substantial sessions over the
   same three and a half weeks. A repo-week is not an arc, and the
   operator's decision says arc. Recommendation: show the repo-week figure
   BESIDE the per-arc verdict as a labelled secondary, never as the
   verdict. Its use would be to say whether more declared arcs are worth
   waiting for.
2. **Is the arm switch admissible under the freeze?** It is measurement
   code inside a mechanism, and without it no pre-registered probe in this
   form exists. Recommendation: treat it as part of any future mechanism's
   ship set, not as a thing to build now.
3. **The freeze-release wording has lost its referent.** The parked items
   wait on "the lc-161 after-measurement verdict". Under this form there is
   no single after-measurement, only per-mechanism trials. What releases
   them is the operator's to say; this desk records nothing about it.
4. **More declared arcs.** The measure is starved by how few arcs are
   declared outside two repos. Whether other repos should declare arcs is
   lc-239's territory and not proposed here.

## 8. The transition table (sign-off requirement)

Home: this file. No row is built by this wave.

| arrow | verb | record written | check that proves it | OBSERVER |
|---|---|---|---|---|
| a trialed mechanism reaches its moment | the mechanism's own verb | fire line with `arm=`, and `withheld=` when OFF | red-first: a fixed session id yields a fixed arm; OFF acts on nothing and logs the moment | the verb invocation |
| a session is placed in an arc | the arm's grading run | a row per session: arc, arm, exposure, delivery | the scan is shown live on a session known to name an arc and one known to name none | the grading desk's run, at the window's close or at 6 eligible arcs |
| delivery is established | the grading run | delivered, undelivered and (for a refusal) complied and defied counts per arm | a print: the marker found in a tool result of a known delivered session and absent from a known filtered one. A refusal: a known complied case and a known defied case, or the absence of any defied case in the record stated | the grading run |
| the verdict is taken | the grading run | an audit and one ledger line | the four-row table of section 5, applied to the rows | a desk other than the mechanism's designer |
| the window closes with too few arcs | none | COULD NOT VERIFY, with the arc count | the count itself | the armed window date, written into the trial's item as an evidence blocker |

## 9. Reproduce the feasibility figures

The arc and repo-week counts come from the session rows of
`tools/operator-interventions.py` over the two windows, joined to a scan of
each session's transcript for the 12 arc and record paths. The scan is not
yet a committed tool. It becomes one as a NAMED DELIVERABLE of whichever
wave first runs the grading (judgment desk ruling); until then the figures
in sections 2 and 7 are one uncommitted probe's output.
