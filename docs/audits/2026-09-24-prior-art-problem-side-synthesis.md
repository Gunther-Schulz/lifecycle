# Prior art from the problem side: what four new surveys change

**2026-09-24, session dev-17, on the operator's direction.** The operator
doubted that nothing similar exists, "because this is one of the
frustrations of working with an agent continuously cross-session (and even
within-session it often loses track or gets Scheuklappen)". The four
earlier surveys (literature: `docs/answerable-not-felt-research.md`;
tooling: `2026-09-18-tooling-prior-art.md`; process frameworks:
`2026-09-19-process-framework-mapping.md`; agent layer:
`2026-09-19-missing-layer-scout.md`) searched mostly in OUR solution's
vocabulary (kind registry, red-first refusals, growth by flow), so a
project with the same goal built differently could not surface. Checked
before commissioning: Beads, spec-kit, Taskmaster, BMAD, Agent OS, Cline
Memory Bank, Kiro and claude-flow had 0 hits across `docs/`, `ITEMS.md`
and `LEDGER.md` (case-insensitive grep; the 13 "cline" hits were all
inside "decline").

Four codex lanes (gpt-5.6-luna, read-only, live web search) searched from
the PROBLEM side, in parallel:

| report | angle | web searches |
|---|---|---|
| `2026-09-24-prior-art-tools.md` | practitioner tools (16 systems) | 53 |
| `2026-09-24-prior-art-complaints.md` | where practitioners complain, and what they tried | 21 |
| `2026-09-24-prior-art-handover.md` | continuity in non-AI fields (clinical, ATC, nuclear, ICS, military, logbooks, ADRs) | 46 |
| `2026-09-24-prior-art-drift.md` | within-session drift and tunnel vision | 39 |

## How far to trust the reports

- **Desk-verified: 14 citations, 14 hold.** Each URL was opened at this
  desk (curl, GitHub API, arXiv export) and contains its claimed topic:
  9 from the complaints, handover and drift reports, 5 from the tools
  report. Two specific claims were checked word for word: the I-PASS
  47% (PMC10964397: "a 47.1% reduction in the frequency of
  handoff-related reported major adverse events (1.7 vs. 0.9 events per
  person-year)"), and arXiv 2608.01964's title ("LongHorizon-Harness:
  Advancing Long-Horizon Agents for Real-World Tasks").
- **Not checked:** whether each remaining [VERIFIED] sentence says what its
  source says beyond the topic. Topic-level existence is what was proven.
- **Read reach:** the lanes read no local file except `docs/purpose.md`,
  the only one the prompt permitted (all four stderr logs grepped for
  local paths).
- **The handover and drift reports mark their own "Borrowable" lines
  [UNVERIFIED]**, because each is the lane's application of a source to
  our problem, not a claim the source makes. That grading is correct;
  read them as prompts.
- **First codex web-research run at this site; the role is uncertified.**
  On the sample, no fabricated citation among the 14 checked. The result
  is recorded for the dispatch skill in dispatch-guards
  `dev-notes/dispatch-OBSERVATIONS.md` (2026-09-24 codex web-search
  entry).

## What changes (desk grading against `purpose.md`; the "desk reading" lines are judgment)

**1. The "direction drift has no prior art" verdict is refuted.** The
tooling survey ("Two clean negatives") called direction drift "a genuine
zero", and `the-loop.md` repeats it ("direction drift has no mechanism
and an external survey found none either"). The drift report found direct
answers: CodeBolt's drift detection, a sidecar comparing the current
trajectory against both the original task and the initial plan
(desk-verified to exist); the Intent Drift Score proposal, a
semantic/structural/temporal trajectory score (NeurIPS 2025 venue page,
lane-verified); and ReflAct, where every action restates current state
against the final goal (arXiv 2505.15182, desk-verified). Desk reading:
these are purpose.md's HYPERFOCUS cure, "an input from outside the
frame", built. The survey half of the-loop.md's sentence is now a killed
belief; its "no mechanism HERE" half still stands.

**2. Receiver-side verification is the strongest evidence-backed
mechanism outside AI.** I-PASS (32 hospitals, 47% fewer handoff-related
major adverse events, desk-verified) is a bundle, but its recurring core,
shared with ATC position relief and UK HSE shift handover, is the
RECEIVER confirming: read-back, questions, explicit acceptance, a
post-acceptance check. Desk reading: lifecycle's continuity design is
sender-heavy (write the state well; announce it at start). A DEMAND at
the resume seam, where the waking session restates the state and has it
checked against the record before its first act, would be the kill
test's receiving half, and it is a retrieval mechanism: the design doc's
measured loss is retrieval, not capture. Caveat: 47% is the whole
bundle's effect; no source isolates read-back.

**3. Staleness is the most-reported failure of every practitioner memory
system.** The tools report cites staleness issues against Beads,
Taskmaster, Aider and Claude Code memory; the complaints report adds
"memory can preserve the wrong truth" and AiderDesk's "append forever is
insufficient". Desk reading: this validates purpose.md's living record
(facts vs beliefs, basis, REOPEN), which none of the 16 surveyed systems
has in full. The concrete borrowables are narrower than the concept:
hash/version checks around generated views (Beads #2139), supersession
links (ADRs), and "the event log is the truth, markdown is a projection"
(rosehgal/handoff).

**4. Compaction is the sharpest practitioner pain, and it is
within-session amnesia.** The top complaint is not the blank new session
but compaction making a RUNNING session forget completed work, revive
rejected approaches, or repeat searches (anthropics/claude-code #75759
and openai/codex #36712, both desk-verified to discuss compaction). Desk
reading: direct outside evidence for "the context window is a cache" and
for the kill test, since compaction is an involuntary partial kill
(the-loop.md O7). The complaints report's borrowable, "every
consequential action leaves an external, queryable receipt", is
purpose.md's "every act writes its state as a byproduct", reached
independently.

**5. What people fear losing is WHY and WHAT-NOT-TO-RETRY.** The
complaints report converges on decisions with reasons, failed approaches
and "must not be retried" as the lost content, not file inventories.
Commander's intent (handover report) adds "what would change the plan".
Desk reading: matches the ledger, the design doc's "DEAD ENDS are the
category nobody captures", and the investigation record's NOW slot (the
approach and what would kill it). External confirmation of which slots
matter most; no change.

**6. Still no equivalent system.** Across 16 practitioner systems the
tools report finds persistence of tasks, specs and instructions, with
enforcement mostly limited to schemas, dependency state and hooks, and
behavioural rules left as prose. Closest partial overlaps: Beads (typed
task graph plus session injection), BMAD (append-only history, curated
current memory, evidence references for completion claims),
rosehgal/handoff (event log as source of truth), GSD (compact state,
verification artifacts before the next phase). Desk reading: the
2026-09-18 "the combination is absent" headline survives a problem-side
canvass, now with named near neighbours instead of an unsearched gap.

## Candidate borrows, ranked by desk judgment (candidates, not decisions)

1. **Resume read-back** (from 2): the resuming session restates GOAL, NOW
   and its next act, checked against the record before its first write.
   The receiving half of the kill test; a demand at a seam, so it fits
   law 26's "what must be written" form.
2. **Trajectory conformance check with pre-declared replan triggers**
   (from 1, plus the FAA plan-continuation-bias source): periodic
   comparison of recent work against the goal and the initial plan, by an
   observer outside the acting frame. Its test set needs hard negatives,
   legitimate pivots that look like drift (ContinuityBench,
   lane-verified).
3. **Generated-view freshness checks** (from 3): any projected view
   (banner, digest, handoff) carries the hash or version of the record it
   was generated from, and a check refuses a stale one.

Consumers: lc-281 (the corpus-to-lifecycle migration survey) names this
wave as its input; the refocus design round (lc-276, lc-277) is where the
three candidates get graded.
