# 2026-09-24: the refocus design round. What fires at which moment, and what it demands

**Desk:** lifecycle-d9 (Opus 5.5), Job 2 of
`docs/directives/2026-09-24-refocus-design-round-kickoff.md`.
**Status:** REVISION 2, after the attack round. It is the operator's
decision round in waiting.

Revision 1 (`7400e56`) was attacked by two fresh-context arms:
- **opus:** 16 findings, 5 blocking;
- **codex gpt-6-astra (additive):** 12 findings.

Most of revision 1's recommendations did not survive. It is replaced here in
place; `git show 7400e56:<this path>` has it. §5 records what the attack
changed, finding by finding.

## 0. The corrected evidence (read this before any decision)

**1. Kill condition 1 was measured on tautological notices only.**
Measured at this desk after opus F1, by joining every surfacing record for
this repo in `fire.jsonl` against the declared readers in
`.claude/lifecycle.json`:
- 377 of 379 kind-surfacings came from a verb that is itself a declared
  reader of the kind it surfaced.
- The other 2 are `arc open` surfacing `arc index`.

So "125 surfaced / 8 read" measured notices that told the session nothing it
had not just been handed. **The O6 counter has NOT tested whether an
INFORMATIVE notice changes behaviour. That leg is untested, not refuted.**

What still stands for the DEMAND direction is the adherence split
(purpose.md, dotfiles-measured, 5 of 6, one session). The observation that
refusals changed behaviour every time they fired is session 09020605's own
grading, and it is testimony.

**2. The counter cannot attribute anything to a session.**
- `firelog.fire()` writes `at`, `verb`, `repo`, `outcome`, `detail` and no
  session key (`firelog.py:51-61`).
- My revision-1 window join gave 114 surfacing records; opus's recount of
  the same window gave 129. Neither instrument can separate sessions, so the
  discrepancy stays open against both (law 17).
- My probe script was not persisted. I withdraw its per-kind "touched
  directly" figures as evidence of anything beyond the fact that direct file
  work is invisible to `kind read`.

**3. Reads ARE computable in this stack, though not by a lifecycle verb.**
`dotfiles/claude/hooks/required-reading-gate.py` computes reads from the
transcript and refuses a session's first Write/Edit until the declared files
were Read (header, lines 1-19, opened). Revision 1's "a demand for a READ
cannot be checked here" is true of lifecycle verbs only.

**4. A lifecycle verb already knows its session.**
`desk.py:74-95` `resolve_desk_id` defaults to `CLAUDE_CODE_SESSION_ID`, which
is set in the Bash tool environment (relayed by opus, which ran `echo`).

**5. Booking already has a near-match demand.**
- `item add` runs `candidates()` (rarity-weighted requirement tokens plus a
  shared write-set) and refuses with `FINDING [join_undisposed]` until the
  call carries `--join merge-into|supersede|new --absence`
  (`verbs.py:731-738`, opened).
- Its over-fire history is measured: 126 of 138 before lc-46, and
  boilerplate matches after it (lc-248).
- `ledger add` has no such gate.

**6. The goal question's admission is already gated, by the operator.**
LEDGER.md:130: "run the drift probe treatment arm? → YES … 5 governed-repo
sessions or 4 weeks … Slot admission gated on its outcome". The window,
consumer and grading are in `docs/directives/2026-09-20-drift-treatment-arm-directive.md`
(opened, lines 20-30).

**7. Required prose already exists at the D3 seams.**
- `arc advance --reason`, `arc narrow --text` (`cli.py:714-727`, relayed by
  opus).
- `item close --reason` → `closed-reason:`.

## 1. The principle that survives

**Lifecycle changes behaviour at acts, by refusal.** This is measured every
time it fires, and it is also the only lever lifecycle owns. Two
qualifications, both from the attack:
- **Reuse before adding.** Where an act already demands prose or already
  runs a match, the round widens that demand. It never stacks a second flag
  on the same act (law 26's first question; the fixing module's WHERE/WHAT
  axes).
- **Conditional before unconditional.** A demand that fires on every act
  (item close runs ~63/week in the real repos since 2026-09-17, per the
  opus fire-log census) must justify its cost on data. A demand that fires
  only when a check found something justifies itself by the mechanism bar.

## 2. The decisions (the operator round draws from these)

**R1. The surfacing channel (lc-276).**
- **RECOMMENDED:**
  - Remove TIER-1 notices: those whose acting verb is a declared reader of
    the surfaced kind (377 of 379). They are the design's own "over-trigger"
    degenerate form (O6 §6) and carry no information.
  - Keep TIER-2 surfacing (the 2 of 379) and the counter unchanged.
  - The demand leg stays OPEN, because its evidence was tautological.
- lc-256 keeps its scope and its MUST-NOT-MOVE.
- lc-276's falsifier stays on the counter, as its done-criterion requires:
  if tier-2 surfacings, once their moments are informative, are followed by a
  read in the window less often than 1 in 10 over the first 30, the notice
  leg is dead on real data and the demand leg is designed then.
- **Classed as a defect repair** under the freeze: a notice naming a kind
  the acting verb just read is shipped output that carries nothing. The
  operator confirms or rejects that class in the round.

**R2. Fire lines carry the session key.**
- **RECOMMENDED:** `firelog.fire()` records the session (via
  `resolve_desk_id`'s source, `CLAUDE_CODE_SESSION_ID`, absent → the field
  says absent, never omitted).
- This repairs the counter's measured blindness (§0.2).
- It is the precondition for every per-session derivation below and for the
  lc-161 after-measure.
- **Classed as a defect repair** of a shipped instrument. It is additive to
  the log line, so no carrier schema moves.

**R3. The goal question at seams (lc-277), as the TREATMENT ARM, not as a
release.**
- **RECOMMENDED:** the treatment arm keeps its operator-decided window and
  grading. What changes is its TRIGGER: from a brief directive (memory) to
  the verbs.
  - At the acts that already demand prose (`item close --reason`,
    `arc advance --reason`, `arc narrow --text`), the verb PRINTS the live
    goal immediately before recording. The already-demanded prose is the
    written answer. No new flag, no new slot, no schema change.
  - Each such act's fire line gains `goal-seam=<seam>`. With R2's session
    key, seams-per-session derive from the record.
- **Scope, stated, since it amends an operator-decided arm:**
  - The probe design's treatment seams are "round open, wave authorization,
    record update". This moves the arm to verb seams, which breaks
    comparability with rows 1-2 (both self-graded, n=2).
  - Catches, wrong restatements and operator interventions stay
    independently graded, per the probe design. A fire line cannot supply
    them.
  - The dispatch seam lives in dispatch-guards and is booked there as a
    separate item. lc-277's done-criterion names dispatch, so lc-277 stays
    open until that lands. It is NOT closed by this.
- **Falsifier:** the probe's own pre-registered caught-by-whom criterion
  over the window. Too few established drift episodes gives COULD NOT
  VERIFY, never a verdict (directive lines 26-28).

**R4. Resume read-back (dev-17's candidate 1, filed under lc-276 option 6).**
- **RECOMMENDED: PARK.** The named missing evidence is R3's arm outcome. A
  read-back is the goal question fired at the resume seam, and the arm
  decides whether an environment-fired restatement does anything.
- Design facts carried so the park is cheap to lift:
  - the session key exists (§0.4);
  - the observer must be the lifecycle verbs, not the dotfiles gate, whose
    scope is Write/Edit/MultiEdit/NotebookEdit while carrier writes go
    through `lifecycle` via Bash;
  - desk state overwrites (`desk.py:197`), so the read-back needs its own
    record, which is a schema change (law 25).
- Falsifier to pre-register when lifted: recovery errors (the next act
  contradicts the record), never textual novelty. Astra: an identical
  correct read-back is success.

**R5. When `/standort` fires.**
- **RECOMMENDED:** stays manual.
- Its run's ledger line takes a FIXED question prefix, `standort: <scope>
  position check`, so runs become countable by exact match. That is a
  convention in `standort.md`, not a schema slot.
- **Named deferral:** a trigger is decided once 4 runs are recorded, on two
  counts read from those lines:
  - how many runs changed a verdict or booked an item (a run that changes
    nothing needs no trigger);
  - the interval between runs.
- Revision 1's arc-advance demand is withdrawn:
  - unbuildable, since ledger lines carry no date or type slot (`ledger.py`
    134-135);
  - under-sampled, at ~4 advances a month;
  - its skip flag was an unverified override (law 11).

**R6. Freshness fingerprints (lc-282, dev-17's candidate 3).**
- **RECOMMENDED:** no new mechanism.
  - The directive-staleness rule already exists as a judgment-register row
    ("directives: a cited file changed past the citation -> stale. audits:
    never", `judgment.py:65-78`, relayed by opus).
  - Its home is retire's second pass, which prints NOT RUN.
- lc-282's decision is therefore: the projection population it asks about is
  (a) directives, which that register row covers once its pass runs, and
  (b) prose status claims (CLAUDE.md role lines, the-loop.md cells).
- (b) is judgment-shaped, since both motivating incidents carry no pinnable
  source, and it is already served by the-loop.md's dated-status convention.
- Audits stay "never": they are historical. That was astra's
  historical-vs-current finding, and the existing row already says it.
- lc-282 is re-pointed to "make retire's pass 2 run the existing row", or
  dropped if that is already booked. The build item's first act is that
  carrier search.

**R7. `ledger add` gets the booking gate `item add` already has.**
- **RECOMMENDED:** widen `candidates()` to decision lines, and refuse an
  undisposed near-match with the same `--join` vocabulary. It is ONE
  matcher, not lc-278's equality reader, which answers a different question.
- This is the whole of revision 1's D2 that survives.
- Its over-fire risk is the one lc-46/lc-248 already measured, so it ships
  with that rate reported.
- It is new reach, so it waits for the freeze exit.

**R8. The freeze exit.**
LEDGER.md:138 freezes new mechanism and names no exit. Revision 1 made
"baseline recorded" the exit. That reverses an operator-pinned decision by
inference, and it is withdrawn. The exit is the operator's.
- **RECOMMENDED:** R1 and R2 proceed now as defect repairs.
- R3 (a change to an existing trial's trigger, no new slot) proceeds after
  the lc-161 baseline is recorded.
- R7 and every other new mechanism wait for an explicit freeze exit.

**R9. lc-281's answer.**
- Lifecycle enforces at ACTS, by refusal; that is measured.
- Notice-borne enforcement is UNTESTED (§0.1), so it is no class.
- So a corpus rule is class (a) if a refusal enforces it today, (b) if an
  act lifecycle owns could carry a refusal for it, (c) otherwise. Revision
  1's "never by notice" is withdrawn as wider than its basis.
- This answer unblocks lc-281.

## 3. The lc-161 baseline must separate the classes the decisions are graded
on

Both arms found that revision 1's falsifiers read categories the baseline
did not collect. So the extractor's stage-2 classification carries, per
operator message, one of these classes:
- **legitimate (the operator's by kind):** IGNITION, DECISION, TASTE, INFO;
- **the refocus's targets:**
  - ALREADY-IN-RECORD (the operator points to something the record held; a
    duplicate booking is a subclass);
  - STEER (goal or direction, including "what is the goal?");
  - CORRECTION (other catches);
  - NUDGE (continue, status);
  - RATIFICATION (answering an ask the session could settle);
  - RELAY;
- **the third answer:** COULD-NOT-CLASSIFY.

R1 is graded on ALREADY-IN-RECORD, R3 on STEER, and the refocus as a whole
on targets per 100 turns. Attribution across decisions stays weak by
construction, because several ship in one window. That is said here so the
after-measure is not over-read.

## 4. The transition table (sign-off requirement; OBSERVER column)

| arrow | verb | record written | check that proves it | OBSERVER |
|---|---|---|---|---|
| a verb reads its own kind | any declared-reader verb | no surfacing line (R1) | red-first: a reader verb of kind K no longer prints K; `arc open` still surfaces `arc index` | the verb invocation |
| any verb runs | every verb | fire line with `session=` (R2) | red-first: with the env var set, the line carries it; unset, it carries `session=absent` | the verb invocation |
| a seam act records its prose | `item close` / `arc advance` / `arc narrow` | the existing prose, plus a fire line `goal-seam=` | red-first: the goal line prints before the record, and the fire line carries the seam | the verb invocation |
| treatment rows are derived | a derivation over `goal-seam` lines keyed by session | the seams column of `drift-treatment-log.tsv` | seams equal the fire-line count per session | the desk grading the arm (the directive's named grader), not memory; catches and interventions are graded independently by that desk |
| a `/standort` run happens | `ledger add decision` with the fixed prefix | the ledger line | exact-prefix count | the run itself; the trigger decision reads the count once 4 exist |
| a ledger decision near-matches (R7, after freeze exit) | `ledger add` | the refusal, or `--join` disposition | red-first on a near-match plant | the verb invocation |

## 6. Late input: lifecycle-64's levers memo, graded

The memo is persisted verbatim at
`docs/audits/2026-09-24-levers-memo-lifecycle-64.md`; the operator directed
it into this round.

| lever | grade at this desk | disposition |
|---|---|---|
| 0 kill test dangles | CONFIRMED (0 hits in ITEMS.md) | booked lc-283 (dev-17 raised the same, deduped) |
| 1 measure the goal recurringly | ACCEPTED. One stale premise: the extractor is TRACKED (`fbd5ecd`), not untracked, and stage 2 is running | lc-161 stages 1-2; recurring kill drills ride lc-283 |
| 2 withdraw surfacing | PARTLY REJECTED on the memo's own evidence: the 224/8 count is the same tautological population (§0.1, 377 of 379), so "firing harder" is the tier-1 volume growing | R1 removes tier-1; tier-2 withdrawal waits for evidence |
| 3 demands ride existing verbs | ACCEPTED, and it is R3's shape | adds the rule to §1 (below); the verb × demand × miss-cost survey is booked as lc-284, blocked on the freeze exit |
| 4 short acting frames (AMENDED on operator correction, relayed by lifecycle-64: restarts replaced by main desk + lanes/peers; window length is not an established cause) | ACCEPTED as amended; the load-bearing half is outside readers at the MAIN desk's seams, and the kill test stays the loss meter | lc-285 amended in place; blocked on whether the drift probe carries an acting-frame-architecture axis |
| 5 pre-registered probe as the admission bar | ACCEPTED | operator question (a scope rule for every future mechanism) |

§1 addendum, from lever 3: **at most one new demand per verb per round.**
That caps the reuse principle so it cannot become the over-constraint that
law 26 warns about.

## 5. What the attack changed (disposition per finding)

| finding | disposition |
|---|---|
| opus F1 (tier-1 only) | ACCEPTED, re-measured: 377/379 (§0.1); R1 rewritten, R9 narrowed |
| opus F2 (reads computable) | ACCEPTED (§0.3) |
| opus F3, astra 5, 6 (lc-277 not closed; no session key) | ACCEPTED: R2 added, R3 states lc-277 stays open |
| opus F4, F15 (falsifier uncomputable, seam class) | ACCEPTED: R3 keeps the probe's grading and names the seam amendment |
| opus F5, F13, astra 9 (standort predicate, skip override) | ACCEPTED: R5 withdrawn to manual plus counted runs |
| opus F6-F8, astra 11-12 (D7 re-invents, checks nothing) | ACCEPTED: R6 |
| opus F9, astra 3-4, opus cat-6 (D2 re-invents the join) | ACCEPTED: R7 reuses `candidates()` |
| opus F10, astra 8 (session key known; desk overwrites) | ACCEPTED: R4 |
| opus F11 (row 1 fully applied) | ACCEPTED: row 1 is 2 of 2; lc-277's "minority" wording to be amended |
| opus F12 (counts irreproducible) | ACCEPTED (§0.2) |
| opus F14, astra 2 (baseline lacks classes) | ACCEPTED (§3) |
| opus F16 (lc-256 MUST-NOT-MOVE) | ACCEPTED: R1 keeps lc-256's scope |
| opus cat-4 (observers) | ACCEPTED: §4 rebuilt |
| opus cat-5 (stacking, schema, freeze) | ACCEPTED: no new flags or slots in R1-R3; R8 |
| astra 1 (tier-1 verbs that only enumerate files) | ACCEPTED in part: R1 keys on DECLARED reader, and whether a declared reader truly reads is a separate reach question for `retire` (its staleness pass prints NOT RUN) |
| astra 7 (identical read-back) | ACCEPTED: R4 falsifier |
| astra 10 (admission gate) | ACCEPTED: R3 and R8 |

## 7. JUDGE RULINGS (lifecycle-64, 2026-09-24, under the operator's delegation stated first-hand in that session)

Relayed verbatim in substance from lifecycle-64's message to d9. It binds as
the operator's own delegated ruling.

1. **R1 and R2: YES, now, as defect repairs.**
   - R1 keys on the DECLARED-reader predicate. The §4 red-first pair is run,
     with `arc open` surfacing `arc index` as the surviving positive control.
     Tier-2, the counter, and lc-276's 1-in-10-over-30 falsifier are all
     kept.
   - R2: an absent environment variable writes `session=absent`, never
     omitted, red-first.
   - R2 lands WITH OR BEFORE R1.
2. **R3: YES, after two conditions.**
   - Conditions: the lc-161 stage-2 baseline is recorded (an artifact in
     `docs/audits/` cited by a ledger line), and R2 is live.
   - LEDGER:130's arm, window and grading stand.
   - Rows 1-2 are kept, marked pre-move, and never pooled with later rows.
   - Catches, wrong restatements and interventions are graded
     independently.
   - lc-277 stays OPEN on its dispatch seam.
   - The falsifier is the probe's own criterion, and thin data gives COULD
     NOT VERIFY.
3. **R7: a NARROW freeze exit, for R7 only.**
   - It builds when the stage-2 baseline is recorded AND b4's wave is 7 of 7
     desk-verified.
   - It ships with the lc-46/lc-248 over-fire rate and a red-first
     near-match plant.
   - The general freeze stays in force.
4. **Admission bar: YES, ledgered now.**
   - It binds NEW MECHANISMS, not defect repairs of shipped instruments.
   - A candidate claiming no probe is possible surfaces that claim as its
     own numbered question.
   - The `probe:` slot stays deferred.
   - R3 and R7 already satisfy the bar.
