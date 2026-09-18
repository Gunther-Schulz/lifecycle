# lc-157 — what the literature says, and what it changes

**Written:** 2026-09-18 by cachyos-setup-33, integrating three discovery lanes
dispatched per the operator's direction in `answerable-not-felt.md` §"Next
session — scout the external landscape IN PARALLEL". Companion to that note;
the note is the design, this is what the outside evidence does to it.

**Provenance is graded per claim and the grades are not uniform.** Two abstracts
were fetched by this desk directly from the arXiv API (raw source, not a
summarizer) and are marked DESK-VERIFIED. Everything else carries the grade its
lane gave it. A lane's "read primary text" is LANE-VERIFIED — testimony from a
party that opened the source. A search snippet is SNIPPET and is weaker than
both. The note's own reader should not flatten these.

---

## The headline: the note names the wrong variable

`answerable-not-felt.md` offers two candidate explanations for why the
desk/peer division works — **momentum independence** (the executor is inside
the flow and feels its state; the desk is outside it and queries) and **role
separation** as such. The evidence says neither is the variable, and converges
on a third that both underspecify:

> **What does the work is an INDEPENDENT SIGNAL — one the generating party
> cannot see or influence while producing its answer.** Separate model,
> separate context, or an external deterministic check all supply it. Role
> labels inside a shared context do not.

Three independent lines support this, and one of them is a proof.

**Role separation alone is provably negative, not merely unhelpful.**
*On the Reliability Limits of LLM-Based Multi-Agent Planning* (arXiv:2603.26993)
— DESK-VERIFIED, quoted verbatim from the raw abstract:

> "We show that, without new exogenous signals, any delegated network is
> decision-theoretically dominated by a centralized Bayes decision maker with
> access to the same information."

The qualifier is the whole finding. Splitting work across parties operating on
*the same information* buys a communication bottleneck and nothing else. So if
desk/peer helps, it cannot be because there are two roles — it can only be
because the desk acquires information the peer's report does not carry.

**Asking the same context to check itself degrades accuracy.**
*Large Language Models Cannot Self-Correct Reasoning Yet* (arXiv:2310.01798,
ICLR 2024) — abstract DESK-VERIFIED; the numbers below LANE-VERIFIED against
the HTML v1 primary text. Intrinsic self-correction, meaning no external
feedback: GSM8K GPT-3.5 75.9 → 75.1 → 74.7 across rounds; CommonSenseQA
75.8 → 38.1 → 41.8. The lane quotes the mechanism: the model "is more likely to
modify a correct answer to an incorrect one than to revise an incorrect answer
to a correct one," because it reasons *from* its own prior output rather than
toward an independent check of it.

**The cleanest datum varies independence and nothing else.**
arXiv:2607.17044 — DESK-VERIFIED abstract. A production agent with verification
loops staffed by small task-specialized verifier models. Its own decomposition
is honest in a way that helps us: most of the uplift comes from scaffolding and
specialist models, and the verification step's isolated contribution is small
(+1.5 points) but concentrated where it converts otherwise-failing tasks. The
line that matters here, verbatim:

> "Specialist-swap ablations suggest that the loop's value depends on who
> observes it: replacing the small trained verifier with the generating
> frontier model eliminates most rescues."

Same seam, same timing, same artifact — only the observer's independence
varied, and it moved the number. The lane reports the underlying counts as
6 rescues → 2 (LANE-VERIFIED, HTML v1).

### What this changes in the note

The note's prose states the **timing** property as load-bearing ("triggered at
the seam"). The evidence says the **independence** property is load-bearing,
and timing only answers *when to fire*. The practical consequence is sharp: a
seam-triggered LLM self-reflection — "am I done? really?" — inherits the
identical failure mode as continuous self-monitoring, merely fired less often.

The note's five ranked mechanisms are all deterministic rather than reflective,
so they sit on the winning side of this literature **by construction** — but
that is currently an accident of good taste, not a stated criterion. It should
become one.

**Proposed reframing:** *answerable by something that cannot see your answer.*

---

## What the corpus has been reinventing, with names

The single highest-value return from the lanes. Each of these is an existing
name for something the corpus arrived at independently.

| corpus concept | existing name | source |
|---|---|---|
| "the wrong answer is shaped exactly like the right one" | **false success**, **silent failure** | arXiv:2606.09863; cluster at 2609.10548, 2603.25764, 2608.23663, 2510.22224 |
| pit-of-success vs. remember-to duty; the mechanism bar | **poka-yoke**, *control* vs *warning* tier — the warning tier "relies on human response" and is explicitly the weaker one | manufacturing/HCI field term |
| Fixing's "what counts as correct comes from the DEFINITION" | **the test oracle problem** | classical software testing, ~40 years old |
| persisting state outside the context so it is queried, not recalled | **externalization**; **structured note-taking** / **agentic memory** | arXiv:2604.08224; Anthropic's context-engineering post |
| a record going stale while still looking current | **state drift**, **Implicit Conflict** | arXiv:2605.06527 (STALE) |
| the outward/irreversible gate | **admission control** — verification at the seam where output crosses into effects | arXiv:2605.17998 |
| desk verifies at the artifact | **generator/verifier**; **verification asymmetry** | generator-verifier literature |

The investigation record's closest named prior art is Anthropic's own
**structured note-taking**. The desk/peer split's closest match by *function* is
**generator/verifier**; by *state externalization* it is **planner/executor**;
neither names the momentum hypothesis.

---

## Verification is cheap, and that is an argument about mechanism #1

- Verification accuracy 87.0% vs generation 63.0% overall; on hard problems
  76.5% vs 32.4%, better than 2× (arXiv:2509.17995, SNIPPET).
- A 400M cross-encoder retains 98.7% of full verification accuracy at up to
  99.97% less compute (arXiv:2506.18203, SNIPPET).
- Cheap TF-IDF detectors at the completion boundary reach AUROC 0.83–0.95 and
  recover 4–8× more false successes than the best LLM judge at equal flag rate,
  at ~3,300× lower latency (arXiv:2606.09863, DESK-VERIFIED abstract).
- The same paper, DESK-VERIFIED verbatim: "no configuration across 5 judges,
  5 prompt strategies, and full task specifications exceeds AUROC 0.65."
  Judges keyed on *confident closing language* rather than verified state.

**Read together: grading prose is near-worthless; reading state works; and the
cheap deterministic detector beats the smart judge.** That is the note's
"mechanize the answerable half" thesis with numbers under it, and it argues for
building mechanism #1 rather than for reaching for a stronger desk.

**Named breakdown condition, which the note should carry:** verifier-based
approaches are strongest in narrow *verifiable* domains (math, code,
theorem-proving) with clear step-correctness. Outside domains with robust
answer-equivalence, the verifier's own correctness becomes the unverified
premise (SNIPPET). The repo's own verify blocks and self-tests sit inside the
verifiable domain; the judgment remainder does not, which is a second
independent argument for the note's honest boundary.

---

## Mechanisms outside the note's five

1. **Independent-observer verification as its own architecture** — a second
   process with its own view of ground truth, structurally distinct from
   counting registered checks. tau2-bench's dual-control domain measures it:
   false success 45–48% of failures under single control, **3%** under dual
   (DESK-VERIFIED). The desk role already *is* this, undocumented as a
   mechanism. Recommend adding as candidate #0.
2. **Admission control at the world-boundary** — gate where output becomes an
   effect (a commit, a push, a delivered report), distinct from any internal
   step boundary (arXiv:2605.17998). This maps exactly onto the corpus's
   existing irreversible/outward gate, which means the concept is already
   carried in prose and is a candidate for mechanization here.
3. **Planner-mediated oracle** — output checked against a typed intermediate
   plan artifact committed to *before* execution (arXiv:2607.17044). Distinct
   from the note's #2 dry-run: it catches drift even when the done-criterion is
   satisfiable.
4. **Cheap syntactic triage** — trajectory length, loop detectors, TF-IDF over
   the closing message. Flags "look here" without semantic verification;
   cheaper than the note's #4 record lint.
5. **Layered pass levels** making a partial state distinguishable from a full
   pass — L0 compiles / L1 tests / L2 static analysis / L3 exploit-resistant;
   silent failure = passes L0–L1, fails L2–L3, measured 170/1030 (16.5%) across
   seven agent frameworks (arXiv:2609.10548, LANE-VERIFIED). A working
   instance of the corpus's three-answer convention.
6. **Scalable oversight / debate** — a complexity-theoretic account of *why* a
   checking party can validate work it could not itself produce (Irving et al.
   2018; arXiv:2311.14125). Relevant if the desk is ever framed as overseeing a
   more capable peer.

---

## A caution the note does not carry

**The desk has its own biases.** The LLM-as-judge literature documents
self-preference bias (arXiv:2410.21819) and position/verbosity effects
(arXiv:2412.05579) — an evaluating party can systematically favour its own
reasoning style and be swayed by ordering, independent of any
momentum or context question. If the desk role is formalized, this belongs in
its definition. A desk grading *prose* is exposed to this; a desk reading
*artifacts* largely is not — which is the same conclusion the headline reaches
from the other direction.

---

## Three gaps: the note's most distinctive claims are unmeasured

Not refuted — **unmeasured**. All three are original to this work.

1. **"Persistence guides by mere existence."** Nobody measures it. The closest
   source (Anthropic's note-taking post) is qualitative. Every measured number
   found concerns a *query* or a *second party acting on* persisted content.
   The lane named the missing ablation: (a) no record, (b) record present but
   never referenced, (c) record present and actively re-read. **Nobody runs
   arm (b).**
2. **Momentum as a variable independent of context separation.** Every study
   that varies anything varies context or model sharing; none holds sharing
   fixed and varies time-in-flow. The literature's blind spot relative to the
   note's own hypothesis.
3. **Fires-by-construction vs. remember-to.** No paper runs the comparison.
   Flagged by its lane as a zero from two targeted queries, *not* a canvassed
   literature — a weaker absence claim than (1) and (2), and marked as such.

**AMENDMENT 2026-09-18, second desk (lifecycle-6f): GAPS (1)-LIKE AND (3) NOW
HAVE MEASURED PAPERS, AND ONE OF THEM IS COUNTER-EVIDENCE.** A second literature
pass was dispatched from this desk — redundantly, as it turned out, since this
document already existed and was not read first, which is itself the failure
this whole note is about. It was not wholly redundant: three MEASURED papers
below were not in the original pass. All three are LANE-VERIFIED and none has
been opened at this desk, so they carry that grade and nothing rests on them
yet.

- **Governance decay under compaction** (arXiv:2606.22528, LANE-VERIFIED):
  measures a rule that survives in the corpus while vanishing from context
  after compaction — violation rate 0% → 30-59%. This is the closest external
  measurement of "knowledge fails at MOMENTS OF APPLICATION, not at storage",
  which the note asserts and nobody had measured. It is not gap (1)'s missing
  arm (b) — it varies compaction, not reference — but it is the first outside
  number on the same phenomenon.
- **Do self-evolving agents forget?** (arXiv:2605.09315, LANE-VERIFIED):
  measures that accumulating rules, skills and memory across evolution channels
  causes NON-MONOTONIC CAPABILITY EROSION unless explicitly constrained.
  **THIS IS COUNTER-EVIDENCE TO THIS REPO'S CENTRAL ACTIVITY AND IS RECORDED AS
  SUCH.** A corpus that grows every session is the thing it measures decaying.
  It does not refute the design — the qualifier "unless explicitly constrained"
  is where every constraint here lives, and the repo's own retirement trigger
  and fire-rate review are exactly such constraints — but a session reading this
  document should meet the disconfirming paper before the confirming ones, and
  the probe it implies has not been run here.
- **Fabrication after tool failure** (arXiv:2609.14758, LANE-VERIFIED):
  measures that naming an explicit THIRD STATE before answering cuts agent
  dishonesty 14.10% → 0.87%. That is near-experimental support for law 1 and it
  lands squarely on gap (3), which this document recorded as unmeasured. The
  absence claim there was correctly labelled weak — two targeted queries, not a
  canvassed literature — and it was wrong.

Also reported, ungraded here: overclaiming propensity (arXiv:2609.20812, agents
misrepresenting incomplete coverage ~80% of the time) and an anchoring/oracle
formalization close to law 22 (arXiv:2608.17214). And a NEGATIVE result worth
keeping: no formal three-valued verification-contract paper matching this
repo's construct was found, which agrees with the tooling survey's independent
finding that no exit-code convention for the third answer exists anywhere.

**The corpus is ahead of the literature on (3) and should keep its own data.**
The adherence split — a duty with a visible output fires; a remember-to duty
under-fires even while loaded, 5 of 6 corrections in one session against a rule
loaded the whole time — is an original measurement with no external
counterpart. That is a reason to keep measuring it, not to discard the claim
for lack of outside support.

---

## Counter-evidence on external memory, which the note treats as a free win

- **MEMDRIFT** (arXiv:2605.24941, LANE-VERIFIED): all 7 frontier models tested
  show measurable behavioural drift when biased content sits in persisted
  memory; "biased memories act as implicit steering vectors."
- **STALE** (arXiv:2605.06527): names "Implicit Conflict" — a later observation
  invalidates an earlier memory without explicit negation, and downstream
  behaviour keeps following the old one *even when the new fact is present and
  retrievable*. The lane could not extract its numbers (PDF returned structural
  metadata only) — an open gap, not a verified zero.
- Multi-agent debate does not reliably beat single-agent baselines
  (arXiv:2502.08788, lane-quoted fragment); its proposed fix is model
  *heterogeneity*, which is another form of the independence variable.

STALE's failure mode is precisely the risk the corpus already names as
paraphrase drift and stale premises. It is the strongest argument for pairing
any persist-and-query mechanism with a staleness check rather than shipping
persistence alone.

---

## Source grades, collected

**DESK-VERIFIED** (this desk fetched the raw abstract from the arXiv API):
2603.26993, 2606.09863, 2607.17044, 2310.01798.

**LANE-VERIFIED** (a lane opened primary text and quoted it): 2310.01798
(numbers, HTML v1), 2607.17044 (counts, HTML v1), 2609.10548, 2510.22224,
2606.30653 (abs HTML, verbatim), 2502.08788 (fragment), 2605.17998 (partial,
PDF extraction limited), 2604.08224, 2605.24941.

**SNIPPET** (search-engine summary only, not independently opened): 2305.11738,
2303.11366, 2407.04549, 2509.17995, 2506.18203, 2606.20629, 2311.14125,
2412.05579, 2410.21819, 2609.02246, 2309.11495.

**Flagged weak and relied on for nothing:** 2511.07784 (degraded PDF-derived
summary the lane could not verify against source text).

**Instrument checks reported by the lanes:** the persistence lane confirmed its
search path live against Anthropic's own blog before trusting any zero; the
roles lane used "Reflexion" → 2303.11366 and "CRITIC" → 2305.11738 as
known-positive controls, both hitting the correct papers; the triggers lane
reports every query returned real on-topic results with no dead query read as
an absence.
