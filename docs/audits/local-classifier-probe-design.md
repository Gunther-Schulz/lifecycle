# lc-262: offline local-classifier retrieval probe

Pre-registered 2026-09-22 before model scoring. Owner/writer: the executing
session. Consumer: the lc-262 pickup/closure and any later integration decision.
Results belong in `local-classifier-probe-results.md`; reproducible inputs and
machine outputs belong in `local-classifier-probe/`; executable entry point is
`tools/local-classifier-probe.py`. No production integration is part of this run.

## Question and observation boundary

Does a local GLiClass relevance scorer recover useful project documents beyond
the existing deterministic surfacing rule and a cheap explicit-citation lookup?
The act is **after `item add` has persisted a body**: the query contains the
historical requirement, goal and write-set. These are available from the
artifact at that seam, although the present fire log does not retain argument
values. This is a git-backed replay, not a claim to have instrumented sessions.
No session transcript is read. Commit messages supply grouping metadata only.

The data is a small, deliberately varied convenience sample: thirteen bookings,
six tuning events from one historical session and seven test events from two
other sessions. Exact commits and candidates are in `manifest.json`. Selection
was by task variety and an available session trailer, before any model scores.
All events from a given session remain in one split; unknown session identity
is an exclusion, not a guessed grouping. Groups are hashed, not raw session IDs.
This sample cannot establish population-level performance or behavior change.

Candidate universe: fourteen fixed project records/designs/audits. Only files
present at the event commit are admitted, with exact content hashes. The new
item is observed after persistence, so that commit's state is available; later
amendments and later documents never enter. Missing candidate versions are
reported explicitly. This is **ranking within a curated pool**, not full-corpus
retrieval. Generalization to other verbs, unseen projects or implicit decisions
is unmeasured. The overlapping topic families across sessions also limit novelty.

## Independent labels and limited reach

`labels.json` is frozen before inference. Relevance is assigned by the curator
from historical task requirements and source documents, independently of
GLiClass output. A positive supplies the task's governing design, specific
evidence, or a directly applicable constraint. Broad project philosophy alone
does not make a document relevant. A negative addresses a different mechanism
or study; uncertainty is null, excluded from tp/fp/fn with selected-unjudged
counts still reported. Each pair carries its rationale. No label is inferred
from the model score, and absence of a citation alone is not a negative label.

This is a single-curator annotation, not an independently audited gold standard.
The curator also builds the harness; independence here is from the **scored
model**, not from experimental design. Historical author citations support many
positives and favor the citation baseline. We deliberately keep that baseline:
a neural model must earn its cost over information already in the input.

## Frozen treatments and measurements

- Model: `knowledgator/gliclass-instruct-base-v1.0`, revision
  `4f6a108b08a5537f395521d19b5073e197923dd3`. CPU float32, eight threads,
  eval/inference mode, seed 262. Load only cached weights, with network disabled.
- Representation: path plus the first 1,600 document characters and the first
  900 characters of its headings; no query-guided or label-guided excerpts.
  GLiClass's documented reranking form: document as text, act query as its
  single label. Maximum model input length 1,024 tokens. This sacrifices deep
  passages for a bounded cheap first trial; negative results only address this
  representation/model/hardware combination. Record actual truncation counts.
- Baseline: call the shipped `due_reads_for_act` function against each event's
  historical declaration for `item add`, then map its kind homes to the same
  candidate pool. This is today's rule replayed on historical state, not an
  assertion the rule had shipped at every event. Record the source hash.
- Cheap comparator: exact candidate paths mentioned in the same query.
- Every arm has a maximum of three documents per act. Deterministic arms use
  path order if over budget; the model sorts by score descending then path.
  This comparison does not authorize replacing mandatory deterministic reads.
- Choose the model threshold from 0.3, 0.5, 0.7 using tuning events only:
  maximize total true positives minus twice false positives; ties choose the
  higher threshold. Never tune on held-out outcomes. Scores are not claimed to
  be calibrated correctness probabilities.
- Held-out measurements: relevant documents recovered/missed, irrelevant and
  unjudged documents surfaced, recall, precision, per-act runtime (all candidate
  forward passes including tokenization), p95 latency, process peak RSS. Report
  model load time separately; sanity calls warm the model before timed events.
  Runtime excludes disk preparation/model download and includes no GPU claim.
- Paired session-cluster bootstrap, 2,000 resamples, seed 262: report 95% interval
  for recall gain over citation lookup. With only two test sessions this interval
  is descriptive and cannot justify a strong statistical claim.

## Controls and decision rule

Separate controls: a password-reset passage and unrelated banana-bread passage
against a password-reset query (relevant must rank above irrelevant); an empty
act query must return COULD NOT VERIFY without calling inference. Controls do
not enter tuning or test metrics. Harness tests must expose split leakage,
missing labels/scores, frozen-input changes and incorrect count arithmetic.

Adoption into a **later shadow trial** requires all of: at least twenty held-out
events across five sessions; absolute recall gain at least 0.10 over the better
of the two baselines; no more than 0.5 false surfaces per act; warm CPU p95 at
most 2 seconds per act; peak process RSS at most 4 GiB; controls pass. This does
not grant runtime integration. A quality/resource failure rejects **this
configuration**, not local models as a class. Otherwise an undersized sample
is INCONCLUSIVE. Failed controls or missing necessary evidence mean INCONCLUSIVE
/ COULD NOT VERIFY, never a fabricated zero or clean success.

Design, annotations and dataset hashes are recorded with the scores. Package
versions, hardware, per-pair scores, selections, exclusions and rerun commands
must survive in the result artifacts. No post-score edits to frozen labels or
decision thresholds; corrections require an explicitly separate run.
