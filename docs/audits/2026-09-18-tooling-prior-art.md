# Prior art in TOOLING — has anyone built this?

**2026-09-18, three sonnet discovery lanes from the lifecycle desk, read-only.**
Companion to `docs/answerable-not-felt-research.md`, which is the LITERATURE
home and stays so; this is the axis that document does not cover — it carries
one mention of a repository in 253 lines, because it surveyed papers.

**Provenance, per the companion's own discipline.** Everything here is
LANE-VERIFIED at best: a lane opened a README, fetched a page, or queried the
GitHub API. Nothing was opened at this desk. Star counts and recency are as the
lanes read them today. No verdict in this repo rests on any of it yet.

**The question asked:** has anyone built what we are building, and is there a
mechanism worth taking?

## The headline, and it is a real absence rather than an unsearched one

**No project combines the three things that make this system what it is** — a
registry of KINDS with declared stages, refusals proven RED-FIRST by mutation,
and growth judged by FLOW rather than by caps. Each exists somewhere, alone.
The combination has no footprint in adopted tooling.

**A second team reached one of our laws independently.** `rjmurillo/ai-agents`
issue #5698 proposes growth-by-flow with the alarm stated as a thing that grew
without an exit event — applied to GitHub issues, unimplemented, one of ten
sub-tasks done. It corroborates that the problem is real and supplies no
mechanism.

**And a caution about what corroboration means right now.** Several hits were
real repositories, confirmed live, belonging to other individuals, pushed within
the last week, independently minting near-identical phrasing to this corpus. One
(`a9650615/LLM_constitution`, dead since July) carries "Ten Base Laws", dispatch
discipline, and "accepted only by a context that did not produce it" — with no
kind registry or red-first proof underneath. Either the vocabulary is converging
across people solving this simultaneously, or a great many of us are being handed
the same words by the same models. **Vocabulary agreement is not independent
corroboration**, and a survey that counted those as confirming hits would be
measuring its own echo.

## What is worth taking — four mechanisms

| # | source | mechanism | where it lands here |
|---|---|---|---|
| 1 | mu2 (cmu-pasta, 53★, dormant 2024) | mutation-guided fuzzing: kills a mutant across a GENERATED input corpus, not one hand-picked case | the REACH gap — lc-200 |
| 2 | Stryker | `killedBy: [testId]` in its result schema — per-mutant test attribution | prove-rows' "this row and no other", already invented here |
| 3 | Checkov | every check ships `passing_resources` AND `failing_resources` | law 2's pair, adopted at scale |
| 4 | Dosu (commercial, no repo) | per-document `ttl_days:` frontmatter as a declared shelf-life contract | a kind declaring its own staleness horizon |

**1 is the one that matters tonight.** It answers the exact hole this repo found
in itself today: a registered, green, mutation-PROVEN row whose proof fires on
WELL-FORMED input and is blind to the malformed case. Killing a mutant across a
generated corpus is reach-certification rather than existence-certification.
Dormant research prototype, so the idea travels and the code does not.

**2 and 3 say the discipline survives contact with real users**, which one
repo's experience cannot establish. Conforming prove-rows' output to Stryker's
attribution field costs nothing and buys a shape other people already read.

**5, worth its own line because it is the established answer stopping exactly
where our problem starts:** SonarSource S2699 detects a test with no assertions.
It is structural only — blind to an assertion that is present and tautological,
which is precisely this repo's failure class (law 22, a check no input can
falsify). The industry's answer to "is this test dead" cannot see the dead test
we care about.

## Two clean negatives

**No exit-code convention for the third answer exists anywhere.** The nearest
first-class status is NUnit's `Assert.Inconclusive` — inside a test framework,
not a process contract. TAP has TODO/SKIP, which is a different claim: a skip did
not run, a could-not-verify ran and could not decide. So the three-answer
contract was not reinvented here; it was invented, and there is nothing to
conform to. (The literature lane reached the same zero from the papers side.)

**Nothing enforces cross-row isolation as a gate.** Stryker carries the
attribution field and treats it as best-effort; no tool found fails a build
because a mutation darkened a row it should not have. prove-rows' pair assertion
appears to have no external counterpart.

**And one open question, mechanically unanswered:** direction drift — work
steadily going the wrong way while every individual step is correct — returned a
genuine zero. The lane named its queries. Everything found was sprint-velocity
bookkeeping or diff-versus-spec scope checking; nothing separates a wrong
trajectory from ordinary iteration. This repo names it as an open corner and the
outside world does not have it either.

## Weaker hits, recorded so the survey's reach is legible

`TerminallyLazy/Tree-Ring-Memory` (17★, active) — a non-mutating `audit` verb
over agent memory catching stale expiry, contradiction candidates, supersession
integrity; its promoted/rejected/deferred/observed outcome vocabulary is the
steal. `pallaprolus/drift` and `sunnydachs/doc-drift` — doc-code drift by
signature mismatch and git-blame age; no lifecycle model. `npryce/adr-tools`
(5692★) and `thomvaill/log4brains` (1593★) — supersession as a LABEL, never
checked against whether the superseding decision landed; **both unmaintained for
18+ months**, which is a small datum for the thesis that a write-only carrier
rots. `probot/stale` (archived) — the naive time cap this repo explicitly
rejects, since a relabel resets the timer; useful as the wrong-answer baseline.
CodeScene's health TREND against a file's own trailing baseline is the closest
commercial analogue to flow-based retirement, aimed at code rather than
carriers.

**False friend, flagged so nobody chases it:** `invariantlabs-ai/invariant`
(458★) is runtime trace-security guardrails. Pure name collision on "invariant".

## What this survey did NOT establish

No project was installed, run, or read beyond the surfaces named. "No footprint
in adopted tooling" is an absence claim resting on three lanes' searches, each of
which reported its queries; it is not a canvass. A closed-source or internal
system would not appear at all. And the four mechanisms above are candidates for
booking, not decisions — none has been graded against the design at this desk.
