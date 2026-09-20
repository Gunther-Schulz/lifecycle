# The erosion probe — DESIGN, 2026-09-19 (lc-222)

**Status: RUN TWICE, verdict HEALTH on the roster channel both times.**
First run 2026-09-19 (lc-234, 6 day-boundary samples — results:
`2026-09-19-erosion-probe-results.md` beside this file; verdict issued at
that round desk, lc-234 closed on it). Second run 2026-09-20 (12 samples —
an UNINTENDED replication: this header still read "Not yet run" a day
after the first run closed, and a desk composed a wave from the label
without the one directory listing that would have shown the results file;
the stale label cost a lane, the convergence is what it bought). Second
run's result: THE PROBE HAS RUN section below. The two live catches are
booked as lc-251. The other closure — a recorded finding that no available
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

## THE PROBE HAS RUN — measured 2026-09-20 (SECOND run; the first is
## lc-234's, 2026-09-19, in the results file beside this document)

Executed by a dispatched sonnet lane in a scratch clone (the live checkout
kept moving during the run, which confirmed the clone rationale above);
per-row table re-derived independently at the integrating desk from the
data file, `erosion-survival-2026-09-20.tsv` beside this document — every
transition, count and trajectory agrees cell-for-cell. Twelve samples,
df13f3e (2026-08-26) through cb32a4c (2026-09-20), roster growing 41 → 127
rows; 1,115 row-verdicts; zero unrunnable samples.

**Verdict on the pre-registered criterion: HEALTH.** Of 797
previously-proven row-pair transitions, ONE regressed as rider 1's erosion
class (0.13%); ten of eleven transitions show zero regression of any kind,
including the two largest rosters (94/94, 102/102 survived), so there is
no rate rising with roster size — the flip condition for the erosion
verdict, named above before data was pulled, did not occur. No row was
ever silently dropped from the roster after proving (0 of 797).

**Rider 1 did its job — the split carried three different findings:**

- `amend_nothing_to_amend`: PROVEN seven consecutive samples, FAILED from
  the first sample past 2026-09-19 14:52 — the mutation stopped darkening
  the row with the arrangement intact. THE one erosion instance. Causal
  commit fa6ea7e (verbs.py gained a second branch emitting the same
  finding, which co-fires with the recorded anchor's for the row's firing
  input) — first diagnosed in run 1's results file, independently
  re-derived by the lc-251 lane; the sampled flip commits (0bb97d0 in run
  1, 55591ec in run 2) are just each run's first sample after fa6ea7e.
- `capture_dominated`: reads PROVEN for eight samples and NEVER WAS — the
  recorded mutation makes the arm crash (ZeroDivisionError), and a
  prove-rows scoring defect counted any raise as "changed" until 0737205
  fixed it ("a crashed arm is COULD NOT VERIFY, never a proof"); from the
  first sample carrying that fix the row reads COULD_NOT_VERIFY, which is
  the honest state it was always in. Arrangement-broke-at-birth, NOT
  erosion, live and unrepaired.
- `ledger_body`: a one-sample arrangement dip (2026-09-13) that self-healed
  — the class pooling would have miscounted as erosion.

(A first hypothesis — the lc-30 class, read off two same-day `refusals.py`
commits — was REFUTED by the lc-251 lane's diagnosis and by run 1's own
results file: the causes are a verbs.py product-code commit and a
born-broken arrangement, per the trajectory bullets above. Recorded rather
than deleted because the wrong hypothesis shaped lc-251's first booking.)
Repair booked as **lc-251** (pair-rule re-admission, no other row moves);
the diagnosis lives with that item and run 1's results file.

**What the result licenses, no wider than rider 2:** the roster channel
shows no erosion under growth — arXiv:2605.09315's shape did NOT reproduce
on this repo's instrument data — so accumulation of instrument-bearing
mechanisms is not counter-indicated by this measurement. It says nothing
about rule-corpus effects on session behaviour. The two runs' independent
convergence — different sampling plans, different desks, same verdict, same
two casualties, same causal commit for the erosion instance — is the
replication's one genuine yield, bought at the price of a lane the stale
status header spent.

## What this probe cannot be asked

It cannot answer whether the repo's corpus growth helps. It answers only
whether previously-acquired instrument capability is retained as the roster
grows. A null result is informative about erosion and says nothing about
benefit.
