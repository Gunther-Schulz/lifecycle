# lc-262: local GLiClass retrieval experiment — executed

**2026-09-22. Verdict: REJECT_THIS_CONFIGURATION.** Build and offline replay
completed. Do not add this GLiClass formulation as a runtime dependency: on the
held-out sample it recovered less relevant state than exact citation lookup
and exceeded the declared CPU latency budget. This rejects one pinned model,
input representation and inference configuration, not local models as a class.

## What ran

The [pre-registered design](local-classifier-probe-design.md) and
[reproduction instructions](local-classifier-probe/README.md) are the contract
and executable route. Thirteen historical `item add` acts from three session
groups, with six tuning events from one group and seven held-out events from
the other two. Fourteen candidate documents, restricted to versions present at
each event: **175 scored pairs**, with **seven absent-document pairs excluded**.
The query used the newly persisted requirement, goal and write-set; no later
item amendments, task outcomes or session transcripts were model inputs.

Labels were assigned before scoring from historical records, independently of
GLiClass outputs. They are single-curator judgments, not independently audited
ground truth. Uncertain background relevance is explicitly unjudged. Candidate
selection is curated and citation-rich, so this measures neither full-corpus
retrieval nor how often a running agent actually benefits from a surfaced file.

Pinned checkpoint: `knowledgator/gliclass-instruct-base-v1.0` at
`4f6a108b08a5537f395521d19b5073e197923dd3`.
Python 3.13.15, GLiClass 0.1.20, Transformers 5.17.0, PyTorch 2.14.0+cpu;
[requirements](local-classifier-probe/requirements.txt) pins the whole environment.
Hardware: AMD Ryzen 9 9950X3D, eight inference threads, CPU float32.
GPU performance is unmeasured; sandbox `nvidia-smi` could not communicate with
the driver, which does not establish a host driver fault.

## Held-out results

All arms were capped at three surfaced documents per act. Model threshold 0.7
was selected by the frozen tuning rule. All three candidate thresholds scored
zero tuning utility; the declared tie-break chose the highest. No threshold
was changed after seeing the held-out results.

| Arm | Relevant recovered / 17 | Relevant missed | Labeled irrelevant surfaced | Unjudged surfaced | Recall | Precision on judged selections |
|---|---:|---:|---:|---:|---:|---:|
| Current deterministic surfacing rule | 0 | 17 | 0 | 7 | 0% | Undefined |
| Exact citation lookup | 10 | 7 | 0 | 0 | 58.8% | 100% |
| GLiClass | 1 | 16 | 3 | 0 | 5.9% | 25% |

The deterministic rule surfaced the ledger in each held-out act. Its
task-specific relevance was unjudged for those events: **this is not evidence
that the ledger is irrelevant or its mandatory read should be removed**.
The more useful comparator is citation lookup, which selected ten known
relevant documents without a labeled false surface on this small sample.

Model recall was **52.9 percentage points below citation lookup**. The paired
session-cluster bootstrap's descriptive 95% interval was -60.0 to -42.9 points.
Only two held-out session groups underlie that interval; it is not a reliable
population confidence claim. The pre-registered minimum for adoption was
twenty held-out events across five groups, which this sample also does not meet.

Additional **post-hoc diagnostic**, not a retuned primary result: removing the
threshold and taking the model's top three per act still recovered only 1/17,
with fourteen labeled irrelevant and six unjudged selections. The poor result
is therefore not explained solely by the high selected threshold. This
calculation uses `select(scores, 0)` and `counts` from the harness on held-out
rows in `scores.json` and `labels.json`.

## Resources, controls and replication

- Warm held-out p95: **8.965 seconds per act** for 13–14 sequential candidate
  passes, versus a 2-second budget. This is the maximum of seven observations,
  not a stable population-tail estimate. Tokenization and token-count
  instrumentation are included; disk preparation and model download are not.
- Peak process RSS: **1.376 GiB**, within the 4-GiB budget. Includes model and
  Python/runtime overhead. Model/tokenizer loading took 0.622 seconds from the
  warm filesystem cache, separately from package import time.
- Positive/negative sanity scores: password-reset passage 0.008053, unrelated
  recipe 0.000247. The ordered pair passes its rank control; their small values
  are another reason not to interpret raw scores as calibrated probabilities.
- Empty query: actual shared scoring path returned **COULD NOT VERIFY**, zero
  inference calls. This is separately tested against a scorer that raises if
  invoked; an empty input does not silently become a negative prediction.
- Maximum rendered input: 1,119 tokens; **7/175 pairs truncated** at 1,024.
  Every document was also represented by a fixed prefix plus headings rather
  than its full body. This representation can omit decisive passages and is a
  limitation of this configuration, not evidence about the full documents.
- The first run overlapped repository verification. It is retained as
  `scores-initial.json` / `summary-initial.json` but its latency is superseded.
  The final run began after those checks completed, with identical settings.
  **All 175 pair scores were exactly identical between runs**; only timings and
  resource measurements differed. Dataset, label, design and harness hashes
  in the final scores match their on-disk artifacts.
- Additional model-card topic control ranked `space` and `technology` above
  unrelated categories on the author's NASA example. The author's mixed
  sentiment example ranked positive above negative; no broad sentiment-quality
  claim follows. These diagnostics were run after the primary evaluation and
  are not included in its metrics. Package loading emitted model-type and
  deprecation warnings but completed; compatibility beyond these executed
  controls and replay is not independently certified.

Raw selections, scores, exclusions, hashes and counts are in
[summary.json](local-classifier-probe/summary.json),
[scores.json](local-classifier-probe/scores.json),
[dataset.json](local-classifier-probe/dataset.json), and
[labels.json](local-classifier-probe/labels.json).

## Validation and remaining scope

[Verbatim verification summaries](local-classifier-probe/verification.txt):

```text
Ran 13 tests
OK

Ran 1002 tests in 65.366s
OK

rows: 128   128 passed, 0 failed, 0 could not verify, 0 raised, 0 skipped
prose-rest rows (not executed, labelled): 6
lifecycle --test: CLEAN
```

The thirteen instrument tests exercise split leakage, missing annotations,
unknown-label arithmetic, ranking/budget behavior, missing-context abstention,
frozen-input changes, incomplete runs, missing scores and a no-benefit outcome.
Dataset preparation was repeated from Git and compared byte-for-byte with the
frozen dataset. The artifact leak scan and `git diff --check` passed. The first
sandbox verification had five Node `spawnSync git EPERM` failures and one
unverifiable roster control; rerunning outside the sandbox passed, without any
production-code repair or relaxed checks.

No hooks, background service, model dependency in Lifecycle itself, automatic
record writes, or new refusal gates were installed. No sudo or system package
installation was needed; the isolated Python environment occupies about 1.2 GiB
and the downloaded model cache about 723 MiB, both under disposable `/tmp` paths.

**Recommendation:** keep this as a completed negative experiment. Before any
neural retrieval integration, establish whether citation-based surfacing alone
solves enough of the missing-read cases. A later local-model trial could test
shorter task queries, chunk-aware document representations or a dedicated
reranker, with newly held-out sessions and reviewed labels. Those are hypotheses
for new experiments; they were not tested or authorized as runtime changes here.
