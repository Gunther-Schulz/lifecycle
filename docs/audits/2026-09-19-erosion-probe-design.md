# The erosion probe — DESIGN, 2026-09-19 (lc-222)

**Status: a DESIGNED probe, which is one of lc-222's two declared closures.
Not yet run.** The other closure — a recorded finding that no available
measurement discriminates — was considered and is NOT the answer here; the
discriminating measurement exists and the data is already on disk.

Designed at the executing desk `lifecycle-38`; the discriminating quantity
was CORRECTED by the driving desk `cachyos-setup-b3` before anything was
built, and the correction is recorded below rather than quietly absorbed,
because the first design would have shipped a probe that fails the item's own
bar.

## The claim under test

`arXiv:2605.09315` — **"Do Self-Evolving Agents Forget? Capability
Degradation and Preservation in Lifelong LLM Agent Adaptation"** (Yu, Yuan,
Jin, Liu, Yu, Wang; submitted 10 May 2026). **OPENED AT THIS DESK 2026-09-19**,
discharging lc-222's MUST-NOT-BUILD that the paper be read before it is rested
on; until now it was lane-verified and unread here. The repo's summary of it
is accurate.

Its measured finding, from the abstract: self-evolution is often
non-monotonic — adapting to new task distributions can progressively degrade
previously acquired capabilities, consistently, across all four evolution
channels (workflow, skill, model, memory). The mitigation the authors propose
is a stabilization principle constraining destructive capability drift.

**This repo grows its corpus every session, so the paper is counter-evidence
to its central activity**, which is why lc-222 exists at all: a load-bearing
claim earns a probe designed to DISPROVE it, and none had been run.

## THE ANALOGY IS STATED, NOT ASSUMED

The paper measures erosion of an AGENT's capability. This probe measures
erosion of the REPO's INSTRUMENTS — whether accumulated refusal rows retain
their discriminating power as more accumulate. Those are analogous, not
identical, and the paper's result does not transfer by itself. What carries
across is the SHAPE: a system that accumulates capability-bearing artifacts
may degrade previously acquired ones while appearing to improve in aggregate.
The probe tests that shape in this repo's own terms and on this repo's own
data. It is not a replication.

## THE FIRST DESIGN WAS WRONG AND IS RECORDED HERE

**Proposed:** the PROVEN FRACTION of the roster over time — rows proven red
against rows total, as the roster grows.

**Why it fails the item's own bar,** which forbids any probe whose result is
consistent with both erosion and health: the aggregate fraction falls
MECHANICALLY whenever new rows land faster than arrangements are recorded.
That is booking lag — healthy growth — and it reads as erosion. A falling
fraction would therefore have been reported as a finding when it evidences
nothing, which is this repo's whole signature class aimed at the instrument
built to check for it.

## The discriminating quantity: SURVIVAL of previously-proven rows

Of the rows PROVEN at T0, what fraction still prove at T1 — **per row,
longitudinally**, across the roster's growth history.

| | erosion predicts | health predicts |
|---|---|---|
| previously-proven rows at a later T | REGRESS | SURVIVE |
| dilution by newly-added rows | no effect | no effect |

Dilution touches neither column, which is exactly what the aggregate could
not manage. **The outcome that flips the verdict each way is named before any
data is pulled:** a measurable regression rate among previously-proven rows,
rising with roster size, is erosion; survival at a flat rate under a growing
roster is health.

## Rider 1 — the third answer is load-bearing, not hygiene

A previously-proven row that no longer proves has TWO possible causes and they
are not the same finding:

- its **ARRANGEMENT broke** — the mutation anchor moved under a legitimate
  refactor. `prove-rows` already answers this as COULD NOT VERIFY ("the anchor
  matches ...", and "no mutation recorded for ..."). **This is NOT erosion**
  and must not be counted as it.
- its **mutation no longer DARKENS** the row while the arrangement still
  resolves. **This is the erosion signal.**

Without the split, ordinary refactor churn reads as capability erosion and the
probe manufactures the result it was built to test for. `prove-rows`' own
three-answer contract supplies the discriminator; the probe consumes it rather
than re-deriving it.

## Rider 2 — reach, stated so the result is not over-read

This probe measures the **ROSTER channel of environment capability ONLY.** It
says nothing about rule-corpus effects on session BEHAVIOUR, which is the
other half of what the corpus-growth worry is about and which this instrument
cannot see.

**Consequence for what the result may be used for:** it BOUNDS always-on
mechanism admission for INSTRUMENT-BEARING mechanisms, and is silent beyond
that. A result here does not license or forbid a prose rule, a convention, or
a required slot.

## The instrument and whether the data is already held

**Held.** `tools/prove-rows.py` prints a per-row verdict — `[ident] PROVEN` /
`FAILED` / `COULD NOT VERIFY` — plus a stated baseline and an explicit list of
rows with no recorded mutation, so the roster says how much of itself is
proven. Git holds every past roster state.

**One real constraint on running it:** `prove-rows` REFUSES TO START on a
dirty tree, and its own reason is provenance — a `PROVEN` it prints over an
uncommitted state cites a state nobody can fetch. So the longitudinal run
needs CLEAN historical checkouts, one per sampled commit, which is what a git
worktree is for.

## What this probe cannot be asked

It cannot answer whether the repo's corpus growth helps. It answers only
whether previously-acquired instrument capability is retained as the roster
grows. A null result is informative about erosion and says nothing about
benefit.
