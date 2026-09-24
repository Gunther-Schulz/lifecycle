# Reproducing lc-262

Run commands from the repository root. The experiment's contract and limitations
are in `../local-classifier-probe-design.md`; its result is in
`../local-classifier-probe-results.md`.

## Inputs and outputs

- `manifest.json`: selected historical commits, item IDs, session-separated
  splits and fixed candidate pool.
- `dataset.json`: historical queries, candidate representations, content hashes,
  baseline selections and exclusions. No transcript ingestion.
- `labels.json`: pre-score curator annotations and per-pair rationales.
- `requirements.txt`: exact packages used; PyTorch is the CPU wheel.
- `scores.json`, `summary.json`: final inference and held-out evaluation.
- `scores-initial.json`, `summary-initial.json`: first run, overlapping repository
  tests; retained for transparency, not authoritative for latency.
- `model-card-controls.json`: additional post-run diagnostic using the model
  author's sentiment/topic examples; not part of the primary evaluation.
- `test_probe.py`: instrument tests independent of downloaded model libraries.

`prepare` uses git objects and Lifecycle's own item parser and surfacing function.
It does not use working-tree versions of candidate documents. Keep the git
history when reproducing. The current surfacing implementation is hashed in the
dataset; a changed implementation is a different baseline.

## Install and download (once; network required)

Use Python 3.13, the version used for this run. `uv` can obtain it when absent.
No sudo is needed. Choose writable paths for the environment and model cache:

```bash
uv venv --python 3.13 /tmp/lifecycle-classifier-venv
uv pip install --python /tmp/lifecycle-classifier-venv/bin/python \
  --torch-backend cpu -r docs/audits/local-classifier-probe/requirements.txt
export HF_HOME=/tmp/lifecycle-hf-cache
/tmp/lifecycle-classifier-venv/bin/python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download(
    'knowledgator/gliclass-instruct-base-v1.0',
    revision='4f6a108b08a5537f395521d19b5073e197923dd3',
    allow_patterns=['*.json', '*.safetensors', '*.txt', '*.model'],
)
PY
```

The package lock is specific to the tested Linux/Python environment; other
platforms may need different wheels. The environment and model cache are
disposable and deliberately outside the repository. Point `HF_HOME` at a
persistent writable cache if retaining the weights across reboots matters.

## Run offline

```bash
python tools/local-classifier-probe.py prepare \
  --manifest docs/audits/local-classifier-probe/manifest.json \
  --output /tmp/lifecycle-probe-dataset.json
cmp docs/audits/local-classifier-probe/dataset.json /tmp/lifecycle-probe-dataset.json
python docs/audits/local-classifier-probe/test_probe.py

HF_HOME=/tmp/lifecycle-hf-cache /tmp/lifecycle-classifier-venv/bin/python \
  tools/local-classifier-probe.py run \
  --dataset docs/audits/local-classifier-probe/dataset.json \
  --labels docs/audits/local-classifier-probe/labels.json \
  --design docs/audits/local-classifier-probe-design.md \
  --threads 8 --output /tmp/lifecycle-probe-scores.json

python tools/local-classifier-probe.py summarize \
  --dataset docs/audits/local-classifier-probe/dataset.json \
  --labels docs/audits/local-classifier-probe/labels.json \
  --scores /tmp/lifecycle-probe-scores.json \
  --output /tmp/lifecycle-probe-summary.json
```

`run` sets Hugging Face/Transformers offline mode and uses
`local_files_only=True`; only the download step uses the network. Keep other
CPU-intensive tasks idle when measuring latency. Exit 0 means the command
completed, not that adoption passed; the recommendation is `verdict` in the
summary. Invalid/incomplete evidence returns exit 3, COULD NOT VERIFY.

The extra model-card diagnostic is reproducible with the same pinned model and
`ZeroShotClassificationPipeline(..., classification_type='multi-label',
device='cpu')`, threshold 0, using these exact pairs:

- `The food was excellent but the service was painfully slow.` with
  `positive`, `negative`, `neutral`.
- `NASA launched a new Mars rover to search for signs of ancient life.` with
  `space`, `politics`, `sports`, `technology`, `health`.

Those examples are from the author's
[model card](https://huggingface.co/knowledgator/gliclass-instruct-base-v1.0).
