# Reproduction

This directory contains `results.json`. Use the lc-262 environment and frozen
inputs:

```bash
HF_HOME=/tmp/lifecycle-hf-cache /tmp/lifecycle-classifier-venv/bin/python \
  tools/retrieval-baselines.py \
  --dataset docs/audits/local-classifier-probe/dataset.json \
  --labels docs/audits/local-classifier-probe/labels.json \
  --cache /tmp/lifecycle-hf-cache --threads 8 \
  --output /tmp/retrieval-baselines.json
```

The only network step is downloading the pinned BGE checkpoint. No sudo is
needed. The replay uses CPU inference and writes no Lifecycle carriers.
