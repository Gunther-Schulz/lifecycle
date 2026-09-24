#!/usr/bin/env python3
"""Offline lc-262 retrieval probe. No hooks, carrier writes, or remote inference.

prepare reads historical git blobs; run uses a downloaded model offline;
summarize scores frozen annotations. See the companion design for limitations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugin" / "cli"))
from lifecycle_core import declaration, items

MODEL = "knowledgator/gliclass-instruct-base-v1.0"
REVISION = "4f6a108b08a5537f395521d19b5073e197923dd3"
SEED = 262
POLICY = {"budget": 3, "thresholds": [0.3, 0.5, 0.7],
          "min_events": 20, "min_sessions": 5, "gain": 0.10,
          "max_noise": 0.5, "max_p95_seconds": 2.0, "max_rss_gib": 4.0}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True)


def blob(commit, path):
    return git("show", f"{commit}:{path}")


def features(path, text):
    # Query-independent representation: no label-guided excerpt selection.
    headings = "\n".join(x for x in text.splitlines() if x.startswith("#"))
    return f"Document: {path}\n{text[:1600]}\nHeadings:\n{headings[:900]}"


def prepare(args):
    manifest = json.loads(Path(args.manifest).read_text())
    events, exclusions = [], []
    for spec in manifest["events"]:
        commit = git("rev-parse", spec["commit"]).strip()
        message = git("show", "-s", "--format=%B", commit)
        session = re.search(r"^Claude-Session: (.+)$", message, re.M)
        if not session:
            exclusions.append({"id": spec["id"], "reason": "No session trailer"})
            continue
        parsed = items.parse(blob(commit, "ITEMS.md"))
        found = [x for x in parsed.items if x.ident == spec["id"]]
        if len(found) != 1:
            raise ValueError(f"Expected one historical item: {spec['id']}")
        slots = found[0].slots
        # The act is observed AFTER item add persisted these slots. No commit
        # message, later amendments, outcomes, or transcript enters the query.
        query = "Act: item add\n" + "\n".join(
            f"{k}: {slots[k]}" for k in ("requirement", "goal", "write-set"))
        tree = set(git("ls-tree", "-r", "--name-only", commit).splitlines())
        doc = json.loads(blob(commit, ".claude/lifecycle.json"))
        due = {d.kind for d in declaration.due_reads_for_act(doc, "item add")}
        homes = [v["home"] for k, v in doc["kinds"].items() if k in due]
        candidates = []
        for path in manifest["candidates"]:
            if path not in tree:
                exclusions.append({"id": spec["id"], "path": path,
                                   "reason": "Document absent at event revision"})
                continue
            text = blob(commit, path)
            candidates.append({"path": path, "blob_sha256": digest(text.encode()),
                               "text": features(path, text),
                               "baseline": any(Path(path).match(h) or path == h
                                               for h in homes),
                               "citation": path in query})
        events.append({"id": spec["id"], "commit": commit,
                       "session": digest(session[1].encode())[:16],
                       "split": spec["split"], "query": query,
                       "candidates": candidates})
    validate_splits(events)
    dump(args.output, {"schema": 1, "events": events, "exclusions": exclusions,
                       "manifest_sha256": digest(Path(args.manifest).read_bytes()),
                       "baseline_source_sha256": digest(
                           (ROOT / "plugin/cli/lifecycle_core/declaration.py").read_bytes()),
                       "representation": "path + first 1600 characters + first 900 heading characters"})
    print(f"Prepared {len(events)} events; {len(exclusions)} missing-document/session exclusions")


def validate_splits(events):
    sessions = {}
    ids = set()
    for event in events:
        if event["id"] in ids:
            raise ValueError("Duplicate event id")
        ids.add(event["id"])
        if event["split"] not in {"tune", "test"}:
            raise ValueError("Unknown split")
        previous = sessions.setdefault(event["session"], event["split"])
        if previous != event["split"]:
            raise ValueError("Session leaks across tune/test")


def validate_labels(data, labels):
    expected = {e["id"] for e in data["events"]}
    if set(labels["events"]) != expected:
        raise ValueError("Annotation/event set mismatch")
    for event in data["events"]:
        actual = {c["path"] for c in event["candidates"]}
        row = labels["events"][event["id"]]
        if set(row) != actual:
            raise ValueError(f"Candidate/annotation set mismatch: {event['id']}")
        if any(v["relevant"] not in (True, False, None) or not v["reason"] for v in row.values()):
            raise ValueError("Every label needs relevance (or null) and rationale")


def select(scores, threshold, budget=3):
    return [p for p, s in sorted(scores.items(), key=lambda x: (-x[1], x[0]))
            if s >= threshold][:budget]


def counts(selected, annotations):
    known = {p: v["relevant"] for p, v in annotations.items() if v["relevant"] is not None}
    chosen = set(selected) & known.keys()
    tp = sum(known[p] for p in chosen)
    total = sum(known.values())
    return {"tp": tp, "fp": len(chosen) - tp, "fn": total - tp,
            "relevant": total, "selected": len(selected),
            "unjudged_selected": len(set(selected) - known.keys())}


def aggregate(rows):
    summed = {k: sum(r[k] for r in rows) for k in rows[0]} if rows else {}
    if not summed or not summed["relevant"]:
        return {**summed, "recall": None, "precision": None}
    return {**summed, "recall": summed["tp"] / summed["relevant"],
            "precision": summed["tp"] / (summed["tp"] + summed["fp"])
            if summed["tp"] + summed["fp"] else None}


def quantile(xs, fraction):
    return sorted(xs)[max(0, math.ceil(len(xs) * fraction) - 1)] if xs else None


def score_event(event, scorer):
    if not event["query"].strip():
        return {"id": event["id"], "status": "COULD NOT VERIFY",
                "reason": "Empty act query", "scores": {}}
    return {"id": event["id"], "status": "SCORED", "scores": {
        c["path"]: scorer(c["text"], event["query"])
        for c in event["candidates"]}}


def run(args):
    # Set before importing libraries; model loading and all scoring are offline.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    import importlib.metadata
    import platform
    import torch
    from gliclass import GLiClassModel, ZeroShotClassificationPipeline
    from transformers import AutoTokenizer
    data_bytes = Path(args.dataset).read_bytes()
    label_bytes = Path(args.labels).read_bytes()
    design_bytes = Path(args.design).read_bytes()
    data = json.loads(data_bytes)
    validate_splits(data["events"])
    validate_labels(data, json.loads(label_bytes))
    torch.set_num_threads(args.threads)
    torch.manual_seed(SEED)
    started = time.perf_counter()
    model = GLiClassModel.from_pretrained(MODEL, revision=REVISION, local_files_only=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, local_files_only=True)
    model.eval()
    pipeline = ZeroShotClassificationPipeline(model, tokenizer,
                 classification_type="multi-label", device="cpu", max_length=1024,
                 progress_bar=False)
    load_seconds = time.perf_counter() - started
    token_lengths = []

    def score(text, query):
        rendered = pipeline.pipe.prepare_input(text, [query])
        token_lengths.append(len(tokenizer(rendered, truncation=False)["input_ids"]))
        with torch.inference_mode():
            result = pipeline(text, [query], threshold=0.0)[0]
        if len(result) != 1 or not math.isfinite(float(result[0]["score"])):
            raise ValueError("Expected one finite relevance score")
        return float(result[0]["score"])

    # Separate sanity controls, never used to tune a threshold or inflate metrics.
    controls = {}
    question = "How do I reset my account password?"
    for name, text in {
        "relevant": "To reset your account password, click Forgot password on the login page and follow the reset email.",
        "irrelevant": "Banana bread uses ripe bananas, flour, sugar and butter. Bake until golden.",
    }.items():
        controls[name] = score(text, question)
    calls_before = len(token_lengths)
    controls["insufficient_context"] = score_event(
        {"id": "empty-query", "query": "", "candidates": [{"path": "control", "text": question}]}, score)
    controls["insufficient_context"]["inference_calls"] = len(token_lengths) - calls_before
    token_lengths.clear()
    output = {"schema": 1, "model": MODEL, "revision": REVISION, "policy": POLICY,
              "dataset_sha256": digest(data_bytes), "labels_sha256": digest(label_bytes),
              "design_sha256": digest(design_bytes),
              "harness_sha256": digest(Path(__file__).read_bytes()),
              "python": platform.python_version(), "platform": platform.system(),
              "cpu": next((line.split(":", 1)[1].strip() for line in
                           Path("/proc/cpuinfo").read_text().splitlines()
                           if line.startswith("model name")), platform.machine()),
              "threads": args.threads, "device": "cpu", "dtype": str(next(model.parameters()).dtype),
              "packages": {n: importlib.metadata.version(n) for n in
                           ("gliclass", "transformers", "torch", "huggingface-hub", "tokenizers")},
              "load_seconds": load_seconds, "controls": controls, "events": []}
    for event in data["events"]:
        before = time.perf_counter()
        row = score_event(event, score)
        row["seconds"] = time.perf_counter() - before
        output["events"].append(row)
        output["peak_rss_gib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024**2
        dump(args.output, output)
        print(f"{event['id']}: {len(row['scores'])} candidates, {row['seconds']:.3f}s", flush=True)
    output["complete"] = True
    output["input_tokens"] = {"max": max(token_lengths), "pairs": len(token_lengths),
                              "truncated_pairs": sum(n > 1024 for n in token_lengths)}
    dump(args.output, output)


def summarize(args):
    data = json.loads(Path(args.dataset).read_text())
    labels = json.loads(Path(args.labels).read_text())
    result = json.loads(Path(args.scores).read_text())
    validate_splits(data["events"])
    validate_labels(data, labels)
    for key, path in (("dataset_sha256", args.dataset), ("labels_sha256", args.labels)):
        if result[key] != digest(Path(path).read_bytes()):
            raise ValueError(f"Frozen input changed: {key}")
    scored = {e["id"]: e for e in result["events"]}
    if not result.get("complete") or set(scored) != {e["id"] for e in data["events"]}:
        raise ValueError("Incomplete inference run")
    for event in data["events"]:
        if scored[event["id"]]["status"] != "SCORED" or set(scored[event["id"]]["scores"]) != {c["path"] for c in event["candidates"]}:
            raise ValueError("Missing scores; cannot report clean metrics")
    tune = [e for e in data["events"] if e["split"] == "tune"]
    test = [e for e in data["events"] if e["split"] == "test"]
    if not tune or not test:
        raise ValueError("Both tune and held-out events are required")
    # Maximize tp - 2*fp on tuning sessions only; tie favors higher threshold.
    utilities = {}
    for threshold in POLICY["thresholds"]:
        rows = [counts(select(scored[e["id"]]["scores"], threshold), labels["events"][e["id"]]) for e in tune]
        utilities[threshold] = sum(r["tp"] - 2*r["fp"] for r in rows)
    threshold = max(utilities, key=lambda t: (utilities[t], t))
    rows = []
    for e in test:
        model = select(scored[e["id"]]["scores"], threshold)
        baseline = sorted(c["path"] for c in e["candidates"] if c["baseline"])[:3]
        citation = sorted(c["path"] for c in e["candidates"] if c["citation"])[:3]
        annotation = labels["events"][e["id"]]
        rows.append({"id": e["id"], "session": e["session"],
                     "model": counts(model, annotation),
                     "baseline": counts(baseline, annotation),
                     "citation": counts(citation, annotation),
                     "selected": {"model": model, "baseline": baseline, "citation": citation}})
    metrics = {arm: aggregate([r[arm] for r in rows]) for arm in ("model", "baseline", "citation")}
    # Paired cluster bootstrap preserves correlation within each session.
    groups = sorted({r["session"] for r in rows})
    rng = random.Random(SEED)
    deltas = []
    for _ in range(2000):
        sample = [r for group in rng.choices(groups, k=len(groups)) for r in rows if r["session"] == group]
        m = aggregate([r["model"] for r in sample])["recall"]
        c = aggregate([r["citation"] for r in sample])["recall"]
        if m is not None and c is not None:
            deltas.append(m-c)
    delta = metrics["model"]["recall"] - max(metrics[a]["recall"] for a in ("baseline", "citation"))
    p95 = quantile([scored[e["id"]]["seconds"] for e in test], .95)
    reasons = []
    if len(test) < POLICY["min_events"] or len(groups) < POLICY["min_sessions"]:
        reasons.append("Small convenience sample; insufficient independent sessions for adoption")
    controls_pass = result["controls"]["relevant"] > result["controls"]["irrelevant"]
    feasibility = p95 <= POLICY["max_p95_seconds"] and result["peak_rss_gib"] <= POLICY["max_rss_gib"]
    quality = delta >= POLICY["gain"] and metrics["model"]["fp"] / len(test) <= POLICY["max_noise"]
    if not controls_pass:
        verdict = "INCONCLUSIVE"
        reasons.append("Model failed relevant-versus-irrelevant sanity control")
    elif not feasibility or not quality:
        verdict = "REJECT_THIS_CONFIGURATION"
        reasons.append("Fails pre-registered latency/memory or incremental-retrieval/noise criterion")
    elif reasons:
        verdict = "INCONCLUSIVE"
    else:
        verdict = "ADOPT_FOR_SHADOW_TRIAL"
    summary = {"threshold": threshold, "tuning_utility": utilities,
               "held_out_events": len(test), "held_out_sessions": len(groups),
               "metrics": metrics, "recall_gain_over_best_baseline": delta,
               "recall_gain_vs_citation_cluster_bootstrap_95pct": [quantile(deltas, .025), quantile(deltas, .975)],
               "p95_event_seconds": p95, "peak_rss_gib": result["peak_rss_gib"],
               "controls_pass": controls_pass, "verdict": verdict, "reasons": reasons, "rows": rows}
    dump(args.output, summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--manifest", required=True)
    p.add_argument("--output", required=True)
    p.set_defaults(func=prepare)
    p = sub.add_parser("run")
    for key in ("dataset", "labels", "design", "output"):
        p.add_argument("--" + key, required=True)
    p.add_argument("--threads", type=int, default=8)
    p.set_defaults(func=run)
    p = sub.add_parser("summarize")
    for key in ("dataset", "labels", "scores", "output"):
        p.add_argument("--" + key, required=True)
    p.set_defaults(func=summarize)
    args = parser.parse_args()
    try:
        args.func(args)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(f"COULD NOT VERIFY: {exc}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
