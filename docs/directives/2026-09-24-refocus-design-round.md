# 2026-09-24: the refocus design round. What fires at which moment, and what it demands

**Desk:** lifecycle-d9 (Opus 5.5), Job 2 of
`docs/directives/2026-09-24-refocus-design-round-kickoff.md`. **Base:**
`5d902c7`. **Status:** DRAFT. Awaiting a fresh-context attack round, then the
operator's decision round. Nothing here is decided yet.
**Covers:** lc-276 (the O6 demand leg), lc-277 (a seam-fired goal question),
the `/standort` trigger, and one prior-art candidate (resume read-back, from
`docs/audits/2026-09-24-prior-art-problem-side-synthesis.md`). lc-281 is
blocked on this round's outcome.

## 0. The question, and the boundary that shapes every answer

The question is: **given that lifecycle observes ACTS only, what fires at
which moment, and what does it DEMAND?**

The boundary is O6 design §2, still true at `5d902c7`. Lifecycle sees verb
invocations (one fire line each), git hooks, and session-start hooks. It does
not see file reads, reply text, or reasoning. So a demand for a READ cannot
be checked here. Only a demand for a WRITE made at an ACT can be. That one
sentence settles most of this round.

## 1. The evidence the round rests on, graded

- **Notices did not change behaviour; refusals did.** The O6 counter reads
  125 surfacings against 8 `kind read` records since 2026-09-20. Session
  09020605 surfaced about 61 due-read lines and made 0 reads. The claim that
  "every behaviour change came from a refusal, none from a notice" is that
  session's own grading (testimony, lc-276 evidence slot).
- **MEASURED THIS ROUND: the counter is blind in exactly the way O6 §8's kill
  condition 2 predicted.** The fire log was joined to session 09020605's
  transcript by repo and time window (15:10:51 to 16:47:55Z). Findings:
  - 114 surfacing records in the window, 0 `kind read` records.
  - Surfacings per kind: items 102, done bodies 80, ledger lines 5, arcs 4,
    arc index 4, journal entries 3, laws 3, plugin cache versions 3, the fire
    log 3.
  - Tool calls naming the kind's home, counted after the first surfacing of
    that kind: items 25, done bodies 30, ledger lines 27, arcs 10, laws 12,
    arc index 1, journal entries 0, plugin cache versions 0, the fire log 0.
  - So the session DID work in the surfaced homes, directly, and the counter
    saw none of it.
  - DERIVED, and not causal: those calls include writes and greps that the
    work needed anyway. Nothing here shows a surfacing CAUSED a read. It
    shows only that "8 reads" is not a measurement of reading.
  - The three kinds with a zero (journal, plugin cache, fire log) are the
    only clean "surfaced and never touched" cases.
  - The probe script ran inline at the desk and is not persisted. Its inputs
    were the transcript, `fire.jsonl`, and `.claude/lifecycle.json` homes.
- **Most surfacing is tier-1 tautology.** Of the 114 records, 102 name
  `items`, and nearly every one came from `item check` or `item ready`,
  verbs that read ITEMS.md themselves. lc-256's evidence already inferred
  this. It is now observed: the fire detail itself pairs `verb: item check`
  with `surfaced=done bodies,items`.
- **The goal question: the knowledge holds, the trigger is missing.** The
  drift arc's B1 is 7 of 7 correct restatements when asked. Its B3 is that
  the treatment arm was applied at 1 of 4 and 2 of 2 seams, self-graded, and
  carried only by a brief directive, which is memory.
- **The adherence split** (visible-output duties fire; remember-to duties do
  not) is purpose.md's DEMAND pillar. It is measured in dotfiles as 5 of 6,
  from one session.
- **Prior art, desk-graded by dev-17 today** (the synthesis cited above):
  - Receiver-side read-back (I-PASS, with a 47% bundle effect;
    desk-verified by dev-17).
  - Goal restated per action (ReflAct, arXiv 2505.15182; dev-17
    desk-verified the paper exists).
  - Drift sidecars (CodeBolt).
  - None of these isolates the demand component.

## 2. The principle this round proposes (D2 is where it gets decided)

**Lifecycle demands WRITES at ACTS it owns, and it never demands reads.**
Where a read matters at an act, the VERB PERFORMS THE READ as part of the act
and demands an acknowledgment ONLY WHEN THE READ FOUND SOMETHING.

Two effects follow:
- The read becomes observable by construction, because the verb did it. This
  generalizes tier 1.
- A demand fires only on a non-empty result, which keeps false fires near
  zero. That is the mechanism bar, and law 26's "can the default make the
  writing unnecessary?" answered as "mostly yes".

This is option 1 of lc-276 (the verb reads the kind) joined to option 3
(demand only where a miss is costly), with the cost test made computable: a
miss is costly where the act would duplicate or contradict something the
record already holds.

## 3. The decisions (numbered; each with a recommendation and its falsifier)

**D1. The fate of the surfacing channel (lc-276).**
- (a) Keep it as is.
- (b) Deltas only (lc-276 option 2).
- (c) Two-stage retrieval (option 4, lc-240).
- (d) **RECOMMENDED: withdraw due-read lines from verb output.** Tier-1 lines
  go immediately, since the acting verb reads the kind itself. Tier-2 lines
  go because their effect cannot be measured by any instrument that can be
  built here (§1, kill condition 2). Keep `kind read` and the fire-log
  counter as instruments. Surfacing comes back only as part of a D2 demand.
- **Falsifier:** once D1 ships, the lc-161 after-measure shows operator
  catches of the unread-artifact class ("this was already in X") rising
  against the Job 3 baseline. That would mean the notices were doing work
  the counter could not see.
- **Consequence:** lc-256 (the windowed counter) is re-scoped to count D2
  and D3 firings and their fills. It does not keep counting surfacings.

**D2. The demand leg (lc-276's core): conditional demands at booking.**
- **RECOMMENDED:** `item add` and `ledger add` search the item and ledger
  carriers for near-matches of the new text (the normalized-match reader
  lc-278 builds for the census, one reader). They PRINT the hits.
  - If there is a hit, the verb refuses unless the call carries
    `--related <ids or ledger lines>` or `--related none:<one-line reason>`.
  - If there is no hit, nothing is printed and nothing is demanded.
- This is the "booking into an area the ledger decides" case from lc-276
  option 3, and lc-99 is its measured instance: a blocker unresolved for 11
  days over one apostrophe.
- **Falsifier:** over the first 30 demand firings, either of these kills it:
  - `none:` fills exceed 80% (the matcher over-fires, law 11);
  - operator catches of duplicate or contradicting bookings do not fall
    against the baseline.
- **Declared undetected:** whether a `--related` fill is TRUE. That is
  judgment. The slot demands the statement, never the answer (law 26).

**D3. The seam-fired goal question (lc-277).**
- **RECOMMENDED:** at three seams lifecycle owns, the verb prints the live
  goal and refuses unless the call carries `--goal-check "<one line: what
  this act moved toward the goal, or off-goal: reason>"`. The seams:
  - `item close`: the item's `goal=` slot text, and the goal of any arc
    whose record cites the item id;
  - `arc advance`: the arc's own goal;
  - `arc narrow`.
- Each firing writes one fire line, `goal-seam=<seam> arc=<id> filled=<y/n>`.
  The drift treatment log is then DERIVED from the fire log by a verb, not
  by a session's memory. That closes lc-277's done-criterion and B3.
- **Signing, deliberately:** the question carries no complaint. It is the
  UNSIGNED arm that separates H1 from H2 in the drift probe.
- **Dispatch seam:** it lives in dispatch-guards, not here. A brief-gate
  lane requiring a `Goal:` line in every brief would be the fourth seam. It
  is proposed as a separate item in that repo, and this round does not build
  it.
- **Falsifier:** the pre-registered criterion of the drift probe (its design
  doc) over the derived rows. Also, if more than 50% of fills are the same
  text repeated inside a session, the demand is ceremony and the seam set
  shrinks.

**D4. Resume read-back (dev-17's candidate 1, the receiving half of the kill
test).**
- **RECOMMENDED: design now, build as the second slice, after D3's firing
  data exists.**
- The mechanism: a session's first CARRIER WRITE is refused until the
  session has recorded a read-back through a verb, `lifecycle desk readback
  --goal … --now … --next …`. The read-back is checked only for form: a
  named arc resolves, cited ids resolve.
- **Named unverified premise:** how a lifecycle verb knows its session. The
  desk-state kind is keyed per session uuid, which suggests a route, but
  that route has not been opened this round. The build item's first act is
  that check.
- The home spans two repos: the dotfiles write gate and a lifecycle verb.
- **Falsifier:** read-backs that restate the record with no difference from
  the injected banner, in more than 80% of sessions. That would be presence
  in a demand's costume.

**D5. When `/standort` fires.**
- (a) Manual only, as today.
- (b) A timer or cadence. Disfavoured: the frame's prediction is that an
  act-anchored trigger beats a memory-anchored or timer-anchored one.
- (c) **RECOMMENDED: demanded at `arc advance`.**
  - The verb refuses unless the ledger holds a `/standort` decision line
    dated after that arc's previous advance, or the call carries
    `--standort-skip "<reason>"`.
  - Manual runs stay available.
  - A stage change is the rare, costly moment where a position check pays
    for itself.
- **Falsifier:** skip reasons used at more than half the advances, or no
  standort run in 30 days changing a verdict (every run a TWEAK with no
  booking). In that case the demand moves or goes.

**D7. Freshness fingerprints on persisted projections (lc-282, dev-17's
candidate 3, booked at `ea67e9d`).**
- **RECOMMENDED: no new stage. The home is each kind's existing staleness
  stage.**
- The staleness stage declares "change-coupling — … moved past the citation"
  for audits, directives, design notes and begehung findings (read from
  `.claude/lifecycle.json` at `ea67e9d`). What is missing is EXECUTING it.
- The build: a body that cites `path@<commit>` is a FINDING when `path`
  changed after `<commit>`. The check runs in the `retire` / `audit` walk
  and in `/standort` phase 8. Both are acts, and it is a refusal-grade
  finding, never a notice (D1).
- Order: after D4.
- **Falsifier (reach):** if under a quarter of directive and audit claims
  carry a `path@commit` pin, the check examines almost nothing. That is an
  instrument answering a narrower question than it names. In that case the
  default moves to the writer: the verbs stamp the source when they write,
  law 26's first question.
- **Unverified:** whether any current check executes change-coupling beyond
  "the pointer resolves". A grep for `change-coupling` in
  `plugin/cli/lifecycle_core/` finds only declaration fixtures in
  `refusals.py` and a label in `judgment.py`. The build item's first act is
  to read the retire walk.

**D6. Order, under the freeze.**
- **RECOMMENDED:** nothing from D1 to D5 ships until the lc-161 baseline is
  recorded (Job 3; ledgered with its extractor commit and data-file
  pointer).
- Then, in order: D1 (the smallest, and a removal), D3, D5, D2 (after lc-278
  lands its reader), D4.
- Each lands as its own item with its roster rows red-first.
- This round's ledger line unblocks lc-281. Its answer to lc-281's question:
  lifecycle enforces at ACTS, by refusal or by demanded write, never by
  notice. So a corpus rule is class (a) or (b) only if an act can carry it.

## 4. The transition table (sign-off requirement; OBSERVER column)

Home of this table: this document, until the build items quote it.

| arrow | verb | record written | check that proves it | OBSERVER |
|---|---|---|---|---|
| a booking resembles held record | `item add` / `ledger add` | fire line `demand=related filled=<y/n>`; the fill in the item or ledger body | red-first: a near-match plant refuses without `--related`, a distinct text passes silent | the verb invocation |
| an item closes | `item close` | fire line `goal-seam=close`; the fill as an item amendment | red-first: close without `--goal-check` refuses | the verb invocation |
| an arc advances or narrows | `arc advance` / `arc narrow` | fire line `goal-seam=advance`/`narrow`; the fill as an arc line | red-first as above | the verb invocation |
| an arc advances without a position check | `arc advance` | the refusal, or a `standort-skip` arc line | red-first: no standort ledger line since the last advance, so it refuses | the verb invocation, reading the ledger |
| a session resumes (first carrier write) | `desk readback` (D4) | fire line `readback`; the fill in desk state | red-first: a first write without a read-back is refused by the gate | the dotfiles write gate (a harness hook) |
| a demand is satisfied by rote | the counter verb (lc-256, re-scoped) | none; it reads fire lines | fill-diversity and `none:` rates against the falsifiers above | the counter's own run at session start (banner) and at `/standort` phase 6, **not memory** |
| drift treatment row | a verb deriving it from `goal-seam` lines | `drift-treatment-log.tsv` row | the row's seams equal the fire lines' count | the derivation verb, run by `/standort` |

The one row whose observer is a person or a periodic run is the rote-fill
row. That is the honest remainder: whether a fill is meaningful is judgment.

## 5. What this round does NOT claim

- That any demand improves outcomes. Gate 2 is graded only against the lc-161
  baseline, after gate 1 shows the demands firing.
- That fills are true. The slot demands the statement, never the answer.
- That D1's withdrawal loses nothing. Its falsifier exists because the
  counter is blind.
