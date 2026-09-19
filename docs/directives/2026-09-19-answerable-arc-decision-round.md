# 2026-09-19 — answerable-not-felt arc: decided round + execution delegation

**Driving desk:** `cachyos-setup-2b` (fable; judgment holder, operator
interface, release gate). **Executing desk:** `cachyos-setup-be` (opus).
**Authority:** operator, 2026-09-19, first-hand at the driving desk: *"yes do
all as recommeneed"* over the numbered round below. The delegation binds the
executing desk only once the operator states it first-hand in that session;
until then this file is testimony.

**REPORT-CHANNEL: SendMessage cachyos-setup-2b** — cadence: one message per
wave close, plus any decision round or blocker; final terminal text reaches
no one. Base commit: `e71a414` (read at compose time). Arrival check: two
reads (`git merge-base --is-ancestor e71a414 HEAD`; `git log --oneline
e71a414..HEAD`) plus `git status --porcelain` — foreign commits on top or a
dirty tree HALT and report; this directive's own commit on top of e71a414 is
expected and clean.

**Wave declarations:** wave A is a BOOKING wave (records decisions, mints
items — opens more than it closes, by design). Wave C is a GROOMING pass
(closes/merges more than it opens, and says so in its report). Wave B is a
BUILD wave (closes ≥ opens).

## Grounding — read before acting; report cites what was read

- `docs/answerable-not-felt.md` — the design of record, including the
  research-correction warning block at its head.
- `docs/answerable-not-felt-research.md` — the correction's basis.
- `docs/the-loop.md` — the gap map; O6 is the ranked-first gap.
- `docs/audits/2026-09-18-desk-peer-catch-study.md` — decides D1 below.
- `docs/audits/2026-09-18-robustness-clean-without-looking.md` — the
  reach/blind-spot discipline every new mechanism in this arc must meet.
- Carrier entries: read each item named below with `item slots <id>` (the
  tool's own reader resolves amendments; hand extraction shipped stale
  briefs — J23). Never trust a base slot without its amendments.

## The decided round (operator decisions — record, then execute)

**D1 — lc-158 unblocks.** Its blocker ("decision: is desk/peer
one-directional checking or two asymmetric information holders?") is
ANSWERED: two asymmetric information holders, measured —
`docs/audits/2026-09-18-desk-peer-catch-study.md`, 103 graded events, 9
sessions; cross-session catches 8:1 peer→desk in the cleanest lane;
artifact-reads dominate prose ~21:4. Record the answer by the
decision-blocker answer path and unblock. (Blocker text from the carrier
enumeration lane, 2026-09-18; the study read first-hand at the driving desk.)

**D2 — lc-161 sample decision.** Blocker ("same sample as the catch study or
fresh?") decided: SAME 9-session sample. Basis: the extractor exists, the
absorption question needs no control arm (a stall is observable as elapsed
time without progress, the entry's own words), and a fresh sample buys
nothing the question needs. Record and unblock.

**D3 — lc-157 umbrella disposition.** [RULED 2026-09-19, driving desk, on
the executing desk's critique: the earlier parenthesis here carried two
opposite verbs ("keep NEW → regrade"); the correct disposition is CLOSE at
wave A close — lc-157's done-criterion ("the design decision is made … and
each chosen one is split into its own item") is satisfied once wave A's six
mints land. The #3–#5 holds and their re-open events are recorded as LEDGER
DECISION LINES before the close, so they survive in a live, tool-read home
rather than inside a closed body.] Record on the entry: mechanism #1
(verify-the-verifiers) is BUILT (`lifecycle verify`, test_verify.py);
narrowed #2 (blocked-by evidence predicate graded at booking) is BUILT
(lc-164 made the booking run a graded fact). Candidate #0 —
INDEPENDENT-OBSERVER VERIFICATION (the research doc's strongest addition:
tau2-bench dual-control, false success 45–48% → 3%) — is ADMITTED as its own
new item (mint it in wave A: requirement = the desk role's verification duty
stated as a mechanism, defined by WHAT IT INDEPENDENTLY READS, never by
authority over the peer; write-set = design decision first, so it is born
blocked-by that design decision). #3 (idle-is-answerable), #4 (per-write
record lint), #5 (class-recurrence counter) stay HELD, each with its
re-open event recorded on the umbrella: #3 re-opens when finds carry a
defect-class tag; #4 when lc-156's checker has a fire record; #5 is
hypothesis — mechanism bar unmet (same-class is judgment-shaped), re-opens
only on a computable class marker.

**D4 — mints M1–M4** (wave A mints SIX in total: M1–M4 below, M5 in
addendum 2, and D3's #0 — a wave A close counts BY ID against those six,
never against any heading's number; the executing desk crafts conforming
entries —
slot text below is the settled DESIGN, not final slot wording; the intake
join and refusal contract govern final form):

- **M1 — O6 reader-trigger.** The reader stage gains a WHEN the way lc-168
  gave one to the writer: same closed vocabulary (verb / predicate /
  none-with-reason), same single evaluator (`lanes.evaluate_trigger`), same
  three-answer contract. Basis: the-loop.md O6 ("the central one"; measured
  cost 2026-09-18: a document handled 17 times unread at the moment it was
  needed, four lanes re-deriving what it held). Write-set: declaration.py,
  its tests, and the schema question it raises (an eighth stage is a
  schema-shape change — SEQUENCED AFTER lc-218's bump, never bundled with
  it, per lc-218's own MUST-NOT-BUILD).
- **M2 — round-series readout.** An investigation arc's instrument rounds
  and their yields become persisted, printed state ("round 5; rounds 2–4
  returned nothing new") surfaced where the session composing the next
  round sees it. Basis: the corpus re-entry-seam convention (instrument
  rounds never present as a cycle to the session running them; the operator
  is today the only party who sees the series — measured 2026-09-18,
  CachyOS freeze arc, "keep playing" recommended over an unchanged
  instrument while the data sat on disk). Pattern: I5's count-at-close move
  (a count makes a zero answerable) applied to rounds. Likely home:
  investigation record slots + `record check`; the entry names that as a
  design question, not a decision.
- **M3 — goal-advance slot.** An operator-facing recommendation carries a
  filled slot: what this advances toward the arc's GOAL, or why holding
  position is the recommendation. Required-slot pattern
  (`docs/required-slots-as-an-autonomy-lever.md`): presence computable,
  fill quality judgment; the fill cannot be written without reading the
  goal. Specimen the entry cites: "Keep playing — the rig is healthy"
  (2026-09-18), retracted by its own author as advancing nothing. Design
  question the entry carries: enforcement home (record check? prose form?
  desk convention?) — that is the item's first decision, not pre-decided
  here.
- **M4 — I3/I4 close-counts.** Bookings and ledger writes fire from memory
  (the-loop.md I3/I4, "the same gap... cheapest one to misjudge"); the fix
  is I5's proven route: a COUNT at close (items booked, ledger lines
  written, against the session's finds/decisions), making a zero answerable
  instead of silent. Home: the close ceremony's checklist + whatever verb
  renders it (lc-97 territory — cross-reference, do not duplicate it).

**D5 — grooming pass (wave C, kaemmung-shaped).** Over the 106-READY set:
- Merge or dedupe the flagged clusters (each names distinct sites — verify
  before merging, a distinct site is NOT a duplicate): lc-150/lc-208
  (migration_ledger_nonzero), lc-180/lc-190/lc-203 (conservation
  diagnostics), lc-151/lc-187 (unresolvable-home handling). From the
  enumeration lane, unverified — the pass verifies at the entries.
- Repair the stale-story items: lc-3/lc-7 carry grade NEW while their
  requirement text and blockers read PARKED (regrade or amend, whichever
  the tool's rules permit); lc-218's superseded base blocker is the lc-165
  class — leave the mechanics to lc-165's fix, but confirm the effective
  value reads correctly via `item slots`.
- Doc-lag fixes: the-loop.md O3 row (roster now exists — `e71a414`; date
  the cell per the file's own convention) and CLAUDE.md's opening "six
  declared stages" → seven (verify against declaration.py's KIND_STAGES
  before editing).
- The stale detached worktree registration
  (`.../scratchpad/wt-old`, detached at 2c65b8d, observed 2026-09-19 at
  the driving desk via `git worktree list`) — lc-201's own specimen;
  disposition it (prune if truly dead, else report).
- **The head-rule question returns to the driving desk as a DECISION with
  evidence** (current declaration: `head-rule: none`; 106 READY of 118 open
  is past what the repo schedules): propose, with the corpus backlog
  doctrine's third-grade trigger as the frame, do not decide.

## Wave order and boundaries

**A (book/record: D1–D4) → C (groom: D5) → B (build).** C before B so the
queue is readable and merged before builds close into it. Wave B's content,
pre-decided: lc-218 FIRST (the owed schema bump, alone in its act per its
MUST-NOT-BUILD), then lc-174, lc-176, lc-193, and lc-175+lc-179 bundled
(shared 7-file write-set — one lane, two items, per-item commits). The
executing desk routes its own lanes by standing defaults (sonnet execution;
verdict stages per the routing reference) and re-reads each entry's evidence
at pickup (the design's own mechanism 5) before building it.

**Write boundary:** the lifecycle repo, whole (carriers via the tool's own
verbs ONLY — law 8; plugin code + tests via ordinary edits). Out of scope,
returns to the driving desk: any write outside this repo; any corpus
(`~/.claude/`) mint or edit; the head-rule decision; anything
irreversible/outward beyond ordinary pushes. Commits carry the executing
desk's own attribution trailer; push per the repo's own rules (leak scan
armed — a scan finding is a report, never a --no-verify).

**Known frictions, so they cost one read instead of five round trips:** the
carrier verbs refuse hard (slot caps ~300 chars on blockers, ' — '
separator refused inside decision questions, unmarked evidence refused,
one-file-one-hunk cost test on small bookings) — read the refusal, fix the
slot, don't fight the gate; a refusal naming a cost test may mean the
correct act is doing the fix instead of booking it.

## Horizons

Driving desk arms a recurring ~30 min horizon per active wave; the executing
desk's ack of the operator's first-hand confirmation is the event that
authorizes wave A — no wave starts before it.

## Addendum, 2026-09-19 (driving desk, pre-activation)

**lc-222 rides wave B, scheduled FIRST beside lc-218 (disjoint sets).** The
driving desk's plan prose said "probe the erosion counter-evidence early —
it bounds how much more always-on mechanism is safe to add"; the numbered
round did not carry it and the wave plan above scheduled it nowhere
(caught by the operator's audit question). lc-222 is READY and needs no new
decision. Its RESULT returns to the driving desk before any further
mechanism admission beyond this directive's scope — that is the "bounds"
consequence made operational.

## Addendum 2, 2026-09-19 (driving desk; operator intent stated first-hand:
## "that's one of the pillars of lifecycle I want to solve")

**M5 — the operator-question pipeline (fifth mint, wave A).** The dominant
capture route (~a third of all learning, capture audit) is a one-line
operator question, and sessions measurably do not ask these of themselves —
nor should they try: intrinsic self-questioning degrades (research doc,
arXiv:2310.01798), so the asking party must be independent, and a check must
key on ARTIFACT state, never prose (the AUROC 0.65 judge ceiling). The
solvable formulation: NO OPERATOR QUESTION NEEDS ASKING TWICE. Two halves:

- **MINE:** a discovery pass over this machine's transcripts enumerating
  operator questions that changed a session's course, classified into a
  taxonomy. Feasibility basis: the capture audit's event types SATURATED
  (~18 types, nothing new after the 18th sampled entry) — the classes are
  finite. Instrument: the catch study's extractor (exists); going forward,
  the course-corrections carrier is the capture seam (a course change
  following an operator question carries the question verbatim).
- **DRAIN:** each recurring class gets a recorded disposition — a required
  slot at its firing moment (M3 is the first instance: "do you know what
  we're here for" → goal-advance slot; the required-slots doc lists seven
  more conventions awaiting theirs), a deterministic artifact-keyed check
  ("is this booked?" → M4's close-count; "by now something should have
  materialized" → M2's readout), or HELD with a named re-open event. A
  disposition is an exit; a class with none is the carrier's alarm.

Boundary, recorded so the pillar is not over-claimed: the NOVEL question —
one nobody thought to ask — stays the operator's, is not a gap, and enters
the pipeline the first time it is asked. Always-on additions from the drain
wait on lc-222's result (addendum 1). M5's mining half is discovery and may
run parallel to any wave; its booking rides wave A with the other mints.

## Addendum 3 — wave C close and the SUCCESSOR QUEUE (driving desk, 2026-09-19)

Waves A and C-partial are CLOSED and pushed (origin/main `31f8572`,
verified by fetch at the driving desk). The executing desk `cachyos-setup-be`
is closed. Suite state at close: 6 of 6 registered checks executed —
4 clean, 2 pre-existing could-not-verifies (prove-rows rc=3, audit rc=3),
both identical at the eb69b02 baseline, neither wave work. The one real
red (roster kind unregistered) is FIXED (`2a154ea`).

**The successor desk picks up HERE, none of it done:**

1. Grooming remainder: merge lc-150/lc-208 into one entry with TWO
   red-first arms (same site, two defects); do NOT merge lc-180/190/203
   or lc-151/187 (distinct defects/sites — bundle by write-set at join
   time); regrade lc-3/lc-7 (grade NEW over PARKED text, both slots
   UNKNOWN, `blocked-by: evidence false` where the predicate is the
   literal string "false"); demote the five UNKNOWN-slot READY items
   (an unknown boundary parks).
2. Book the verify.py defect — **ONE arm only**: a wrapped command's
   rc=3 (this CLI's own could-not-verify) renders as RAN-FAILED — the
   three-answer collapse inside the enforcement instrument. The
   exit-contract arm was KILLED by the executing desk's own re-run
   (its earlier rc=0 was zsh pipe-status, tail's exit not the verb's);
   do not book it.
3. Mint the ARC KIND item (born blocked on its design decision), design
   inputs: the four walk findings, live-working-state + kill test,
   belief vocabulary with reopen-and-propagate (all in
   `docs/directives/2026-09-19-arc-walk-synthesis.md` §Additional
   inputs, and this directive's message history is NOT the carrier —
   the doc is).
4. Amend lc-226 (add the grounded-first fill beside goal-advance),
   lc-228 (intervention-taxonomy hypotheses + derivable-fraction
   metric), lc-229 (first target: the narrowing).
5. Fix the-loop.md's O3 row (roster now exists AND is a registered
   kind — date the cell) and its O4 row if the digest hook lands.
6. Compose the head-rule proposal for the driving desk/operator:
   datum from close — `item ratio` 221:106 = 2.08:1 CLEAN under the
   3:1 tripwire, so the argument stands on schedule-size (106 READY)
   alone, not drainage. Two independent routes reached this question
   (carrier size; the arc walk's multi-arc scheduling).
7. Wave B, gated on nothing now: lc-222 FIRST (erosion probe — its
   result gates further always-on mechanism admission), lc-218 alone
   in its act (schema bump), then lc-174, lc-176, lc-193, lc-175+lc-179
   bundled (shared write-set).
8. Two routed findings for the design round: the declaration's ref
   vocabulary cannot express a harness hook in another repo (the
   roster kind's `reader` names `session` as the nearest true value);
   and the attribution hook's "unmarked" line cannot distinguish
   no-trailer from recorder-never-saw-it (`git commit -q` delivers no
   gitOperation) — the same three-answer shape as item 2.
9. Standing observation: the stale detached worktree
   (`…/scratchpad/wt-old`, detached 2c65b8d) — report-not-prune,
   ownership unverified, operator's call.

Known-unmarked commit: 4a4ad6e (trailer env unset for one call;
reported, visible to the hook, deliberately not rebased).
Second known-unmarked commit: 14df96e (queue item 1, executing desk
`lifecycle-38`, 2026-09-19) — committed with `git commit -q`, which
delivers no `gitOperation` and so no SHA to the recorder, exactly the
mechanism queue item 8 routes as a finding. Same disposition as
4a4ad6e: reported, visible to the hook, deliberately not rebased. It
is an UNPLANTED positive control for item 8's second finding, produced
by the desk the finding was routed from; `-q` dropped for the rest of
the queue.

## Addendum 4 — successor desk pair (2026-09-19, driving desk cachyos-setup-b3)

**Driving desk:** `cachyos-setup-b3` (fable; judgment holder, operator
interface, release gate — succeeds `cachyos-setup-2b`, which closed the
prior pair in addendum 3 and is no longer driving). **Executing desk:**
`lifecycle-38` (opus, opened by the operator 2026-09-19). **Authority:**
the delegation binds the executing desk only once the operator states it
first-hand in that session; until then this addendum is testimony. The
operator's continuation instruction at the driving desk ("continue
lifecycle from this directive") is on that desk's record.

**REPORT-CHANNEL: SendMessage cachyos-setup-b3** — cadence: one message
per queue-item close (batching adjacent small items is fine), plus any
decision round or blocker; final terminal text reaches no one.

**Run declaration** (per queue item, inheriting the head directive's wave
declarations): items 1 and 5 are GROOMING (close ≥ open); items 2–4 are
BOOKING (open more than close, by design); item 7 is wave B BUILD
(closes ≥ opens); items 6 and 8 are COMPOSITIONS — proposals and routed
findings returned to the driving desk, deciding nothing themselves; item
9 is report-not-prune.

**Base commit: `37f0a6c`** (read at compose time; addendum 3's queue was
written in that commit and nothing has landed since — "none of it done"
re-verified at the driving desk: clean tree, HEAD = origin/main).
Arrival check, three reads: `git merge-base --is-ancestor 37f0a6c HEAD`;
`git log --oneline 37f0a6c..HEAD`; `git status --porcelain`. This
addendum's own commit on top of `37f0a6c` is expected and clean; foreign
commits or a dirty tree HALT and report.

**Item 9 widened by a driving-desk observation (2026-09-19, `git
worktree list` at compose time): TWO detached worktrees, not one** —
`…/scratchpad/wt-old` at `2c65b8d` (the known specimen) and a
`…/scratchpad/base-eb69b02` at `eb69b02` (matching the closed pair's
attack-round baseline commit). Report-not-prune for both; ownership
unverified; operator's call.

**Everything else — grounding list, write boundary (this repo whole,
carrier writes via the tool's verbs only, law 8), out-of-scope returns
(now to `cachyos-setup-b3`), known frictions, lc-222's gating role —
stands as the head directive and addendum 3 state it.** The executing
desk re-reads each item's slots with `item slots <id>` at pickup, never
from this file's prose.

**Horizons:** the driving desk arms a recurring ~30 min artifact watch;
the executing desk's ack that the operator's first-hand confirmation is
on its record is the event that authorizes queue work — no item starts
before it.

## Addendum 5 — the design round's AGENDA: routed findings and open decisions

Written at the executing desk `lifecycle-38` on the driving desk's
direction, 2026-09-19, at that desk's seam. **This exists because the
agenda had accumulated in a peer channel, and a channel is not a
carrier** — addendum 3 says so about this arc's own message history, and
the rule applies to the list of things the round must decide as much as
to anything else. Nothing here is new work; it is the arc's findings
given a home the round will actually read.

**EXTENDED at the executing desk `cachyos-setup-36`, 2026-09-19, at the
wave B seam** — findings (i)-(l), two input documents, and the round's
own frame and execution shape, all relayed from the driving desk
`cachyos-setup-b3` where the operator stated them first-hand. Landed as
ONE edit before this desk hands the bundle to a successor, for the same
reason the addendum exists at all: an agenda that lives in a channel
dies with the session holding it.

---

## THE ROUND'S ORGANIZING FRAME — draw the map first, place every input in it

**Operator direction 2026-09-19, filled out at the driving desk; DERIVED
placement.** The round OPENS by drawing the pieces-and-seams map and
placing every input into it, rather than deciding eleven findings
piecemeal.

1. **The per-piece half is built.** The seven stages, plus lc-224's
   reader moments, govern each kind's own lifecycle.
2. **The missing half is the EDGES** — the inter-piece judgment moments:
   a find → book; a decision → ledger; a journey with no map →
   runbook-or-declined; a probe used twice → tool; about-to-believe →
   validation read; a flat series → question the instrument; a recurring
   operator question → disposition; and always, goal → next step. Each
   owes FOUR parts: an observable TRIGGER, a QUESTION posed with the
   relevant state in front, a TYPED SLOT with closed vocabulary whose
   absence is computable, and the slot's own NEXT STEP so nothing
   terminates in prose.
3. **The invariant generalized, which is what makes it checkable:**
   every persisted thing resolves to a registered kind AND **every
   judgment moment resolves to a registered seam** — a moment with no
   seam is a finding. Every input this round holds, the (a)-(l) family
   and the extract's five requirements and the tracer incident alike, is
   an instance of that one sentence.
4. **The map is DATA, never a document** — edges declared in the
   declaration, `audit` walking the graph and failing on a dangling
   edge, the banner rendering position from it. A map with
   `reader: session` and no trigger is the-loop.md's own confessed
   limit rebuilt one level up, and must not be.

Judgment stays free INSIDE the seams: the frame schedules questions and
never answers them. **The item→done move is the worked example of a
complete edge, and the standard every new edge is graded against.**

## HOW THE ROUND EXECUTES — statiker-shaped, five forcing points

**Operator direction 2026-09-19.** By hand at the desk pair; the
operator may invoke the statiker skill proper in the round session, and
the shape binds either way.

1. **MAP FIRST, as data** — every piece, every edge with
   trigger/question/slot/next-step, and a status per edge (built /
   partial / missing / declined-with-reason). All findings and the
   extract's requirements are placed as edge statuses BEFORE any
   decision is taken.
2. **DECISION ROUND over the map** — each decision ledgered with its
   basis; declines are first-class.
3. **DESIGN each chosen mechanism to the dispatchable stop** —
   decision-complete, write-set named, red-first stated, three answers,
   observer named. Zero design freedom left for a builder.
4. **FRESH-CONTEXT ATTACK on the locked design, before any build** — a
   review-tier arm plus the certified additive codex attack arm. Attack
   lenses PRE-REGISTERED: dangling edges; over-constraint against the
   model's own default (the measured skill-craft ceiling); lc-222's
   erosion bound gating always-on additions; and each borrowed
   tradition's documented degenerate form, using the VERIFIED ones from
   the framework mapping as attack questions and the PARAMETRIC ones
   only as prompts.
5. **NO-DESIGN implementation in write-set waves**, isolated executed
   verify, then the two gates IN ORDER — mechanical before effect, the
   design doc's own rule — against its pre-registered kill conditions.

Robustness is judged computably: `audit` walks the map for dangling
edges; every mechanism goes red-first on its real defect; and every
mechanism names its own degenerate form at design time, with a detector.

**The arc's thesis, operator first-hand:** statiker and daneel prove the
special case — an explicit path plus a forced record yields autonomous
completion. Lifecycle is that machine with the path DECLARED instead of
hardcoded, the forcing points in the SCHEMA instead of a protocol, and
the state surviving sessions.

## DECIDE–RECORD–PROCEED, with junctions only at crucial milestones

**Operator first-hand 2026-09-19; DERIVED placement.** Decisions are
made transparent by the process but made WITHOUT WAITING. The operator
trusts the system's decisions and intervenes to disagree or redirect —
their stated reason statiker works. Junction points exist only for
crucial milestones. The Marvel session's defect was posing questions it
could have answered itself, either by LOOKING (the investigation derives
it) or by JUDGING (a variant is clearly best given what is known, or
known after looking).

**This principle already exists in the operator corpus** —
derivable-preference delegation, the ratification-ask test, the seam
digest, the carve-out floor as the junction set — so the round's job is
NOT minting it but making it ENVIRONMENTAL. The decision seam's typed
slot forces every would-be operator question through three exits:

1. **answerable by LOOKING** → the look is the next act;
2. **answerable by JUDGING** → decided, recorded with its basis and
   derivability reading, proceed, surfaced in the digest;
3. **a genuine junction** (underivable intent, taste, carve-out) →
   waits, and is rare by construction.

lc-169's derivability statement is exit 2's existing slot half; finding
(c)'s missing blocker type is exit 3's; lc-161's decision-absorption
metric is the trust trajectory this flow feeds, where the operator's
intervention rate on exit-2 decisions IS the calibration signal.

## TWO-STAGE RETRIEVAL — the presence leg

**Operator first-hand 2026-09-19, with a worked specimen; DERIVED
consequences.** Not every session ingesting everything, but an INDEX
whose entry ("a tool exists that relates to my task") triggers the LOOK.
The look supplies both the pattern and the recorded prior decision; the
model's own relevance judgment does the matching; the environment only
keeps the index in view.

**The specimen:** the Marvel arc built tool one auto-starting with the
game, an operator taste ruling stated once. Tool two was then built NOT
auto-starting — *"made no sense… it never looked; it didn't even need my
prior decision — if it had looked at the existing tool, judgment would
have been pretty clear."*

**The operator's own naming of the mechanism:** *"like MCP or skills:
they carry descriptions, not the whole corpus, and get loaded when
relevant."* Three DERIVED consequences:

- **An index entry IS a skill description**, and description quality has
  an existing eval discipline — skill-craft's Tier-1 triggering evals
  (blind router simulation, under/over-trigger grading) transfer
  directly. The round inherits an INSTRUMENT, not merely a pattern.
- **The failure modes transfer too:** under-trigger (the Marvel case —
  no entry existed), over-trigger (index noise, the
  reader-stops-reading disease), and description-body DRIFT
  (label-over-body). Lifecycle is better armed than the skill system on
  the third, because kinds carry a staleness stage and skill listings do
  not.
- **Three local instances already exist** — the runbook router table,
  `kind list --digest`, and the structure line lc-174 just wired — so
  the round designs a GENERALIZATION, not an invention.

**The gap it names, and the round's to design:** DECISIONS indexed by
the ARTIFACT they concern. The ledger holds decisions chronologically,
and nothing surfaces the fact that an operator decision exists about a
thing shaped like the task now in hand. Booked as work in lc-240,
parked on this round's close; the booking pre-empts no design.

## INPUT DOCUMENTS the round reads

- **`docs/audits/2026-09-19-process-framework-mapping.md`** — landed in
  this repo (committed) rather than cited across a boundary, because it
  lived only in a session scratchpad that dies with its session.
  Produced by a sonnet discovery lane commissioned at the driving desk,
  operator-requested; every claim marked VERIFIED-with-source or
  PARAMETRIC, read whole at both desks. **Four notes to read it
  against:** 8D's dual root-cause requirement (verify the defect's cause
  AND, separately, the cause of the detection failure) is a method add
  for every finding in the (a)-(l) family; Cynefin BOUNDS the
  self-authoring edge (minting a runbook is right only in the complex
  domain — in clear/complicated the right act is applying the documented
  one, which is the anti-ceremony guard the runbook-mint slot needs as a
  named precondition); workflow PROVENANCE/lineage is the closest prior
  art for evidence with a shelf life, stronger than any original row;
  and the VERIFIED degenerate forms are pre-registered attack lenses,
  the PARAMETRIC ones prompts only.
- **The CachyOS-Setup repo's `dev-notes/2026-09-19-arc-friction-extract.md`**
  — a design-register friction extract from that repo's freeze arc
  (session `cachyos-setup-dd`, operator-routed), five requirements and
  six real-situation test fixtures, every line marked MEASURED/DERIVED.
  **Four convergences, so the round reads it against this agenda rather
  than as a new pile:** its requirement 1 (goal as a first-class object
  with an unprompted yield count) is the third independent route to
  M2/lc-162/lc-231 territory; requirement 4 (the consuming moment needs
  a trigger — "most believing is reading") lands directly on lc-224's
  new reader-moments machinery as candidate substrate; requirement 3
  (completion graded where the next reader looks) is the two-exits
  done-where-read rule needing a mechanism; and requirement 2 (evidence
  with a shelf life — comparisons between moving artifacts stored as
  durable facts) is a NEW vocabulary member for the (a)-(l) family: a
  slot kind that cannot express "re-derive at read".

### The routed findings

Lettered as the round received them. (a)-(f) were routed during queue
items 1-8; (g) and (h) were found during wave B.

- **(a) The ref vocabulary cannot express a foreign harness hook.** The
  reading-roster kind's `reader` names `session` because that is the
  nearest true value available, not because it is true.
- **(b) The attribution hook cannot distinguish NO TRAILER from
  RECORDER-NEVER-SAW-IT.** `git commit -q` delivers no `gitOperation`,
  so the recorder gets no SHA and the hook reports "unmarked" for two
  different states.
- **(c) THERE IS NO BLOCKER TYPE FOR AN EVENT THIS REPO CANNOT TEST.**
  `classify_blocker` sanctions exactly three — `item`, `decision`,
  `evidence <executable predicate>` — and a wait on another repo or
  another desk is none of them. **Five specimens**, and the last two
  were created by following the rules correctly: the four
  cross-repo `evidence false` items (lc-24, lc-53, lc-66, lc-147, all
  waiting on claude-code-cache-fix), plus **lc-235 and lc-236**, both of
  which wait on THIS ROUND CLOSING and both of which had to be typed
  `decision` because nothing better exists. Each says so in its own
  derivability statement rather than quietly mistyping.
- **(d) A decision blocker can be written in a form its own answer is
  REFUSED in** (lc-233, booked). The blocker slot accepts a question
  containing the ` — ` slot separator; `ledger add decision` correctly
  refuses one; `decision_for` matches by EXACT equality. Such a blocker
  has exactly one answer that would resolve it and that answer cannot be
  written. Swept: n=1 live at the time (lc-8's), zero closed.
- **(e) `item add` derives NEW where the doctrine PARKS.** An entry with
  an UNKNOWN write-set and a real blocker is graded NEW by the verb, and
  the backlog doctrine says an unknown boundary demotes to parked
  (lc-231 was minted into exactly that state and re-parked by hand). May
  be intended — NEW as a pre-grade state — which is why it is routed
  rather than booked.
- **(f) The join's `test/` directory entry collapses the partition.**
  `item waves` over the schedulable set returns ONE LANE OVER 102 ITEMS,
  because `test/` is a directory entry written by 13 items and covering
  files named by 78 more. The lane count has stopped discriminating, and
  a desk reading only that count reads it as a correct serialization
  verdict. One grain worse than lc-173 states it — lc-173 blames
  `refusals.py` at 6 of 8 write-sets; the real collapser is `test/`.
  Held rather than booked while lc-173 is open.
- **(g) NOTHING FIRES ON A REPO LEFT BEHIND BY A SCHEMA BUMP.** Only a
  schema ABOVE the floor is refused (`declaration.py`, the
  `schema_above_floor` branch); below-floor is silent. So after
  `SCHEMA_FLOOR` moved 2 -> 3 here, dotfiles sat at 2 under a floor of 3,
  DEGRADING rather than failing, and no check anywhere said so — it was
  visible only because law 25 forced a dry-run over every declared repo.
  The "one schema version per repo" invariant has no CROSS-REPO
  detector.
- **(h) THE BOOKING COST-TEST GUARD COMPUTES COST FROM THE WRITE-SET AND
  IS BLIND TO EXECUTION COST.** It vetoed booking lc-234 on the grounds
  that one file and one hunk means booking costs what doing costs. True
  of the ARTIFACT and false of the work: producing that artifact takes a
  clean checkout plus a full `prove-rows` run per sampled commit. Law 11
  shape — a guard firing on legitimate work — and it is REPORTED, not
  repaired: the repair is a declared exemption the guard verifies, never
  a softened predicate or an override habit, and that is the round's
  call rather than a mid-wave edit.

**(i)-(l) were found during wave B's remainder at `cachyos-setup-36`.**

- **(i) A LAWS FILE ASSERTS A MECHANISM'S WIRING THAT CANNOT FIRE.**
  `CLAUDE.md:315-316` states the leak scan "is armed as this repo's
  pre-push hook (`tools/git-hooks/pre-push`, symlinked into
  `.git/hooks/`)". Both that file and the `.git/hooks` symlink exist —
  and both are UNREACHABLE, because `core.hooksPath` is set to the
  machine-wide dotfiles hooks directory and a set `core.hooksPath`
  overrides `.git/hooks` entirely. The EFFECT is real (absence-scan does
  fire on pushes, observed at the driving desk) but it arrives by a
  different route than the one the laws file names. Law 26's
  claim-beside-a-mechanism shape, in the laws file itself, and the
  repo-local hook is a guard that can never fire while reading as armed.
- **(j) A KIND'S TRIGGER PREDICATE IS DOCUMENTED AS EVALUATED AND IS
  EVALUATED BY NOTHING** — booked as **lc-237**, parked on this round.
  `declaration.py:119` describes a kind's `predicate` trigger as run by
  `lanes.evaluate_trigger`; that function's only call sites are
  lanes.py:680 and verbs.py:902/1730, none for a kind stage
  (positive-controlled). The one kind using the mode, `journal entries`,
  FIRES when run by hand — and it fires on a state the laws file
  DELIBERATELY declares (laws 13/15/16 each carry their own
  uncited-reason marker), so wiring it as documented would make it a
  permanent alarm on legitimate work. Two states under one word: a
  predicate that has never run and one that runs quiet are
  indistinguishable in the declaration.
- **(k) A CARRIER VERB WRITES WITHOUT A COMMITTING ACTOR.** `item park`
  writes the carrier and leaves the commit to a hand, where `item add`,
  `item amend` and `item close` all commit themselves. The grade change
  sits uncommitted and nothing says so — the assumed-delivery class
  inside the tool's own verb set, one layer deeper than anything else on
  this list.
- **(l) A PER-WORKING-COPY LOCK RENDERS A CROSS-REPO ACT AS A
  COLLISION.** The writer-reservation gate WARNed on a dotfiles commit
  whose pathspec was dotfiles-only, because a lane held the LIFECYCLE
  copy; and it WARNed on every subsequent lifecycle commit unrelated to
  that lane's paths. The gate is correct about what it can see — the
  vocabulary is one lock per working copy, and it cannot express "two
  repos, one desk, disjoint pathspecs", so that state renders as the
  neighbouring one that reads as ordinary collision risk. Filed as a
  specimen, not a repair: the lock's conservatism is right and only its
  expressiveness is at issue.
- **(m) APPEND-ONLY RETENTION × SCAN-BEFORE-PUBLIC MAKES ONE BOOKING
  CLASS PERMANENTLY UNPUSHABLE — and it is NOT a vocabulary gap like its
  twelve siblings.** `item amend` is append-only and RETAINS the
  superseded line by design; the pre-push leak scan refuses certain byte
  classes in tracked prose. So an entry booked with forbidden bytes
  cannot be repaired by amendment: the amendment lands, the original
  line stays beneath it, and the push stays refused. Law 8's
  verbs-only rule offers no verb that REMOVES, so the carrier has no
  exit at all for this state.
  **MEASURED 2026-09-19:** lc-239 was booked with eight absolute foreign
  home paths in its write-set; the scan blocked the push with 43
  foreign-path findings; amending to a path-free `other-repo:<name>`
  form left the original at ITEMS.md:1350 and the refusal unchanged. The
  bytes entered in ONE unpushed commit plus the tip, and the scan covers
  "tip tree + unpublished interiors" (its own usage line), so clearing
  the tip alone does not clear it. Resolved by pre-publication rewrite
  of UNPUSHED local history at the driving desk — which destroys nothing
  shared, but is an exit the carrier itself does not provide.
  **THE CLASS PREDATES TODAY**, which is why this is not one desk's
  slip: `ITEMS.md:692` already carries a foreign path and is ALREADY on
  origin/main. It went out before the scan could refuse it, and nothing
  can now remove it from a public history.
  **TWO REPAIR CANDIDATES, round input and not decisions.** (1) A
  REDACTION VERB with a declared marker: it removes forbidden bytes
  while preserving the fact THAT an amendment happened, so the
  append-only ethic keeps its guarantee (nothing silently vanishes)
  without keeping the bytes. (2) The PIT-OF-SUCCESS fix, and the
  stronger one: the booking verbs run the scan's own value classes over
  incoming slot text AT ADMISSION, so forbidden bytes never enter a
  carrier at all. Refuse at the constructor rather than at the boundary —
  the same move this repo already makes everywhere else, applied to the
  one gate that currently fires last.
  **WHY IT BELONGS ON THIS LIST DESPITE NOT BEING A VOCABULARY GAP:** it
  is the same family one altitude up. (a)-(l) are one mechanism whose
  vocabulary cannot express a real state; (m) is TWO mechanisms, each
  correct alone, whose contracts have no intersection. Append-only is
  right. Scan-before-public is right. A round designing a general
  third-answer mechanism should know that the family contains this shape
  too, because a third answer does not help here — nothing is being
  mis-rendered, and both parties are already saying exactly what they
  mean.

### THE UNIFYING QUESTION, which is why the list is worth reading as a list

**(a) through (l) are one shape: a vocabulary that cannot express a
state the world actually has, so the state renders as a neighbouring one
that reads as ordinary.** (a) renders a foreign reader as `session`; (b)
renders unknown as unmarked; (c) renders an untestable wait as a quiet
predicate; (d) renders an unanswerable question as an open one; (e)
renders a parked entry as new; (f) renders a collapsed partition as a
serialization verdict; (g) renders a left-behind repo as a healthy one;
(h) renders an expensive job as a cheap one; (i) renders an unreachable
guard as an armed one; (j) renders an unevaluated predicate as a quiet
one; (k) renders an uncommitted write as a landed one; (l) renders a
cross-repo act as a collision.

**(m) IS THE FAMILY'S ODD MEMBER AND IS KEPT DELIBERATELY**: it is not a
vocabulary gap but two correct mechanisms with no shared exit. A general
third-answer mechanism does NOT dissolve it, which is exactly why the
round should hold it beside the twelve — a proposal graded only against
mis-rendering will look complete and leave (m) untouched.

This repo solved exactly this at the EXIT CODE level — law 1's three
answers, and `exits.worst` as its single home. It has not solved it at
the SCHEMA level. **So the round's question is whether the schema gets a
general third-answer mechanism, with (a)-(m) as its test population** —
and that population is what makes the question answerable rather than
architectural, because a proposed mechanism can be graded against thirteen
real cases instead of against taste.

**A FURTHER MEMBER ARRIVES FROM THE FRICTION EXTRACT**, and it is the
one this population did not already contain: a slot kind that cannot
express "re-derive at read" — evidence whose truth has a shelf life,
stored as though it were durable. Its closest prior art is workflow
provenance/lineage (framework mapping, §2.1). Counted here rather than
lettered because it came from a document rather than from this arc's own
routing, and the round should decide whether the population is the
letters alone or the letters plus the extract's requirements.

**ADDED BY THE SAME DESK AS A METHOD NOTE, from the framework mapping's
8D row:** every member of this family deserves the DUAL root-cause
question — not only "what state could the vocabulary not express", but
separately "why did nothing detect that it could not". Several members
above answer the first and are silent on the second, which is itself a
finding about how this list was assembled.

### Open decisions the round carries

1. **lc-234's sampling plan** — which historical commits the erosion
   probe samples, how many, chosen how. The design of record does not
   contain it; lc-234 is parked on it.
2. **lc-231's arc-kind design** — and its FIRST question, per the
   synthesis's requirement 6: is an arc a new registered kind, or the
   existing lane mechanism widened?
3. **The head-rule's open half.** Declined both ways on the carrier
   question (`docs/head-rule-decision-2026-09-19.md`), and that
   decision's own reach note says it does NOT rule out that multi-arc
   scheduling needs an ordered head. Re-open event (d) folds it into
   lc-231's design.
4. **lc-236's two design questions** — where the consolidation token
   lives (the waves verb's output, or the route-line convention), and
   its relation to lc-173 and finding (f).
5. **The unifying question above.**

## Addendum 6 — wave B successor desk (2026-09-19, driving desk cachyos-setup-b3)

**Executing desk:** `cachyos-setup-36` (opus, opened by the operator),
succeeding `lifecycle-38`, which closed at `0a3a12b` on this desk's
verified closable verdict. **Driving desk unchanged:** `cachyos-setup-b3`
(fable; judgment, operator interface, release gate). **Authority:** inert
until the operator states the delegation first-hand in the receiving
session; the receiving desk's ack of that confirmation authorizes work.

**REPORT-CHANNEL: SendMessage cachyos-setup-b3** — one message per item
close (batching adjacent items is fine), decision rounds and blockers
immediately; final terminal text reaches no one.

**Run declaration: BUILD** (closes ≥ opens, counted by id at the wave
close). **Scope: wave B's remainder ONLY, in the derived join's order:**
`lc-224`, then `lc-174` ∥ `lc-176`, then `lc-193`, then `lc-175`+`lc-179`
(one lane, two items, per-item commits). Everything else — the design
round, the Begehung, the three round-blocked items — is out of scope and
returns here. `item slots <id>` at pickup, never directive prose; the
reading-roster gate arms on first write, read the roster first.

**Base commit: `0a3a12b`** (read at compose time; tree clean, remote
settled). Arrival check, three reads: `git merge-base --is-ancestor
0a3a12b HEAD`; `git log --oneline 0a3a12b..HEAD`; `git status
--porcelain`. This addendum's own commit on top is expected and clean;
anything else HALTS and reports.

**lc-224's boundary note:** its first decision (reader-WHEN as sub-field
vs eighth stage) is the item's own. An eighth stage is a schema-shape
change: its OWN numbered bump per lc-218's MUST-NOT-BUILD, law 25's
dry-run over BOTH declared repos (dotfiles is at schema 3 since
`db3b485`), and a dotfiles write is outside this desk's boundary — a
boundary halt to the driving desk, the lc-218 pattern.

**Three load-bearing notes from the outgoing desk** (its closing report;
each would otherwise be re-derived): (1) `prove-rows` accepts a single
ident, and running one ident in a detached worktree at an older commit
is how a pre-existing crash is told from a caused one (so ran on
`capture_dominated`, whose rc=3 crash predates the schema bump — booked
as lc-197, do not re-book). (2) The suite's fixtures DERIVE schema from
`decl.SCHEMA_FLOOR` — a new fixture restating the literal is the defect
that cost 42 tests. (3) The session cwd MOVES under any `cd` into
another repo: absolute paths and `git -C` throughout.

**Commit discipline, from the arc's two unmarked-commit classes:** no
`git commit -q` (the recorder sees no gitOperation), and the ledger
verb's auto-commit needs its trailer env set — two different failures,
both reported rather than rebased when they happen.

**Horizon:** the driving desk arms a recurring ~30 min artifact watch;
no item starts before the operator-confirmation ack.

## QUEUED FOR ADDENDUM 7 — the desk gap

Landed by the executing desk `cachyos-setup-36` at its close, 2026-09-19,
on the driving desk's direction. **These are INPUTS awaiting addendum 7,
not decisions and not work** — they sit here because the list otherwise
lives only in a peer channel, which is the premise-with-no-inbox shape
aimed at the arc's own record. The desk gap inherits them from the
carrier rather than from a conversation that dies with its session.

1. **GROUNDED AUTONOMY** — OPERATOR-COINED 2026-09-19, promoted to the
   arc's named guiding principle: guidance concentrated at the SEAMS
   (when, about what, with which state in view, what answer is demanded)
   and freedom absolute in the SPANS (what to conclude). It subsumes
   enable-over-constrain. A one-line amendment to `docs/purpose.md`
   records the name; that document's own statement–mirror–correction
   charter covers the write, and the write happens AT THE GAP, not at
   this desk.
2. **GOAL / WAYPOINT / PROPOSAL vocabulary** — OPERATOR-RATIFIED. Goals
   are operator-stated at ignition and stable (the measured 5% slot).
   WAYPOINTS are self-derived decompositions and alive (the 17-39%
   slots), each citing its derivation, its exit, and its kill-condition.
   PROPOSALS are system-noticed candidate arcs, booked and ignited by one
   operator yes. The goal-advance slot becomes a TWO-LEVEL check
   (recommendation → waypoint → goal). Drift guard, stated with it:
   waypoints are free, top goals are never self-minted.
3. **The missing-layer scout report** lands as
   `docs/audits/2026-09-19-missing-layer-scout.md`, committed at the gap.
   Its source sits in the driving desk's session scratchpad and dies with
   that session; the full report also survives in that desk's transcript
   as fallback. The path is deliberately NOT written here: it carries a
   session id, and this repo's own leak scan refuses a capture named by
   id in tracked prose — ask the driving desk for it, or take the copy it
   commits.
4. **The corpus-divider refinement at SLICE grain** — slot the moment,
   keep the stance; rare-trigger versus missed-moments. Already covered
   by the operator corpus; named here only as round-reading emphasis, not
   as new work.
5. **lc-240 is BOOKED** — the two-stage-retrieval generalization, PARKED
   on this round's close, beside lc-237 and lc-239. Confirmed by the
   booking desk.
6. **STOP/YIELD ADMISSION LENS** — OPERATOR-STATED connection, DERIVED
   consequence, for the round's attack step. The NLS degenerate form
   (improvement layers that daily work never adopts) has a round-grain
   twin that statiker's recent work already cures: stop rules on every
   cycle — the dispatchable-design stop, the re-entry seam's named
   reason, sufficiency, yield-stop. **So every mechanism the round admits
   must carry its own STOP/YIELD condition; a seam with no sufficiency
   rule is an NLS seed** — locally correct, self-justifying, running
   unadopted. The stop rules are themselves seams: the computable slice
   is the boundary firing plus the series/trend in view plus a
   reason-slot present, and the judgment is whether the reason holds. It
   guards BOTH directions — no continuing on momentum, and no stopping
   before the first discriminating probe.
7. **MAST CORROBORATION NOTE**, DERIVED at the driving desk from the
   day's own record, to sit beside the missing-layer scout's first
   borrowable: this arc's same-day catch record matches the 79% finding.
   Every desk catch today — an impossible population, dead premises,
   wrong hook claims, a hand-join mislabel, a base-slot regex — was a
   SPECIFICATION or COORDINATION catch, and not one was an
   output-correctness bug. The spec-adherence-first verifier emphasis is
   therefore locally evidenced rather than merely imported.
8. **THE CLAUDE CLI MEMORY SYSTEM AS THE NAIVE-VERSION NATURAL
   EXPERIMENT** — OPERATOR-STATED experience, DERIVED mapping. The
   operator ran the built-in memory feature — the same intent as this
   design's persistence half, shipped on by default — found it "very low
   performing and gets stale fast", and turned it off. Every observed
   failure maps to a MISSING LIFECYCLE STAGE: capture without
   staleness/exit/bases (stale-invisibly, the label-over-body class as a
   feature); blob loading without selection/kinds/reader-moments (low
   performing at the decision moment); no refinement leg (the scout's
   triple-discovered accumulation-without-integration failure); no
   verification (silent drift). **The design consequence is the sharpest
   framing the arc has for what it is selling: the differentiator is not
   persistence — which ships by default and measurably fails — but
   GOVERNED persistence.** The operator's turn-off decision is the
   control arm's result.
