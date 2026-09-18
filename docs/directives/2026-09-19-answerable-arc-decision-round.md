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

**D3 — lc-157 umbrella disposition.** Record on the entry (amend, keep NEW →
regrade as its design decision now made): mechanism #1
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

**D4 — four mints** (wave A; the executing desk crafts conforming entries —
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
