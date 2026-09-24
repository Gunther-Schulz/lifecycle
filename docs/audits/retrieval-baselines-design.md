# lc-263 retrieval-shaped follow-up

Pre-registered 2026-09-22. This reuses lc-262's frozen `dataset.json` and
`labels.json`, preserving its historical event revisions, whole-session split,
candidate pool and single-curator label limitations. It tests whether the
negative GLiClass result came from using a classifier as a retriever.

Treatments are: BM25 over the fixed candidate text, then BM25 top-10 followed
by `BAAI/bge-reranker-base` query-document scoring and top-3 selection. BM25 is
the no-download lexical baseline. BGE is pinned to revision
`580465186bcc87f862a9b2f9003d720af2377980`, loaded offline, CPU float32, and
used only after lexical shortlisting. No runtime integration is authorized.

The primary held-out comparison is BM25 versus reranking on the same test events.
The existing exact-citation and GLiClass results remain reference arms from
lc-262. Ties sort by path. Each arm returns at most three documents. Report
relevant recovered/missed, labeled irrelevant, unjudged selections, precision,
recall, p95 latency and peak RSS. The BGE score is a ranking score, not a
calibrated probability. The sample's adoption bar remains lc-262's: at least 20
held-out events over 5 sessions, at least 0.10 recall gain over the best simple
baseline, false surfaces <=0.5 per event, CPU p95 <=2 seconds, RSS <=4 GiB.

The dataset and labels are frozen before model execution. Missing model weights,
changed input hashes or incomplete event output are COULD NOT VERIFY. This is a
retrieval benchmark, not evidence that any document should become a mandatory
read or that the model may write beliefs.
