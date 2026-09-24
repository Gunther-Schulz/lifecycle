# lc-263 retrieval baselines — executed

**2026-09-22. Verdict: keep BM25 as an experimental candidate; reject BGE as
an automatic reranking layer for this sample.** The replay reused lc-262's
frozen 13 events, 175 candidate pairs, labels and whole-session split. No
Lifecycle runtime behavior changed.

| Arm | Held-out relevant recovered | Missed | Irrelevant surfaced | Unjudged surfaced | Recall | Precision |
|---|---:|---:|---:|---:|---:|---:|
| BM25 top-3 | 11/17 | 6 | 9 | 1 | 64.7% | 55.0% |
| BM25 top-10 → BGE top-3 | 9/17 | 8 | 9 | 3 | 52.9% | 50.0% |
| lc-262 exact citation reference | 10/17 | 7 | 0 | 0 | 58.8% | 100% |

BGE was better on the six-event tuning split (10/12 versus BM25's 7/12), but
fell behind on the seven-event held-out split. The reranker therefore did not
generalize in this test. BM25 beat exact citation lookup on recall by 5.9
points, at the cost of nine labeled false surfaces and one unjudged selection.
That makes BM25 worth considering only as an advisory candidate with explicit
noise controls; it is not evidence for changing mandatory reads.

CPU performance was acceptable for a bounded experiment: BGE reranking p95 was
**1.146 seconds per event**, and peak RSS was **1.424 GiB** on the AMD Ryzen 9
9950X3D using eight threads. The model was `BAAI/bge-reranker-base` at revision
`580465186bcc87f862a9b2f9003d720af2377980`, loaded offline from the cache.
Scores are ranking values, not calibrated probabilities.

The sample remains too small for adoption: seven held-out events across two
session groups, below the pre-registered 20-event/five-group bar. Labels are
single-curator historical judgments. The candidate pool is curated and
citation-rich, and the BGE arm only sees BM25's top ten, so this does not test
full-corpus recall.

The first run exposed and fixed a reproducibility issue: the output directory
was absent. The rerun created the declared directory and completed all 13
events. Raw rankings and timing are in `retrieval-baselines/results.json`;
the executable is `tools/retrieval-baselines.py`; the frozen inputs are the
lc-262 dataset and labels. The correct next experiment, if desired, is a
larger BM25 evaluation or BM25 plus embeddings, rather than more tuning of this
BGE layer.
