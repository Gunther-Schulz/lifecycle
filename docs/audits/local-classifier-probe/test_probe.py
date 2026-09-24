"""Instrument checks; execute directly with any Python >=3.10 (no model needed)."""
import importlib.util
import contextlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("probe", ROOT / "tools/local-classifier-probe.py")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class ProbeTests(unittest.TestCase):
    def test_split_leakage_rejected(self):
        with self.assertRaisesRegex(ValueError, "leaks"):
            probe.validate_splits([{"id": "a", "session": "same", "split": "tune"},
                                   {"id": "b", "session": "same", "split": "test"}])

    def test_whole_session_split_accepted(self):
        probe.validate_splits([{"id": "a", "session": "one", "split": "tune"},
                               {"id": "b", "session": "two", "split": "test"}])

    def test_duplicate_event_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            probe.validate_splits([{"id": "a", "session": "one", "split": "tune"}]*2)

    def test_missing_annotation_rejected(self):
        data = {"events": [{"id": "a", "candidates": [{"path": "p"}]}]}
        with self.assertRaisesRegex(ValueError, "mismatch"):
            probe.validate_labels(data, {"events": {"a": {}}})

    def test_arithmetic_and_unknown_not_false_positive(self):
        labels = {"a": {"relevant": True}, "b": {"relevant": True},
                  "c": {"relevant": False}, "d": {"relevant": None}}
        self.assertEqual(probe.counts(["a", "c", "d"], labels),
                         dict(tp=1, fp=1, fn=1, relevant=2, selected=3, unjudged_selected=1))

    def test_top_k_threshold_and_tie_order(self):
        self.assertEqual(probe.select({"z": .9, "a": .9, "b": .8, "c": .7}, .75, 2), ["a", "z"])

    def test_empty_query_never_infers(self):
        def forbidden(*args):
            self.fail("Scorer called without context")
        result = probe.score_event({"id": "a", "query": "  ",
                                    "candidates": [{"path": "p", "text": "t"}]}, forbidden)
        self.assertEqual(result["status"], "COULD NOT VERIFY")
        self.assertEqual(result["scores"], {})

    def test_present_query_scores_actual_candidates(self):
        result = probe.score_event({"id": "a", "query": "q",
                                    "candidates": [{"path": "p", "text": "t"}]}, lambda t, q: .7)
        self.assertEqual(result["scores"], {"p": .7})

    def test_no_relevant_labels_not_perfect_recall(self):
        self.assertIsNone(probe.aggregate([dict(tp=0, fp=0, fn=0, relevant=0,
                                               selected=0, unjudged_selected=0)])["recall"])

    def summary_fixture(self, directory):
        p = Path(directory)
        data = {"events": [{"id": ident, "session": ident, "split": split,
                            "candidates": [{"path": "p", "baseline": True, "citation": True}]}
                           for ident, split in (("a", "tune"), ("b", "test"))]}
        labels = {"events": {ident: {"p": {"relevant": True, "reason": "planted relevant"}}
                             for ident in ("a", "b")}}
        probe.dump(p / "data.json", data)
        probe.dump(p / "labels.json", labels)
        scores = {"complete": True,
                  "dataset_sha256": probe.digest((p / "data.json").read_bytes()),
                  "labels_sha256": probe.digest((p / "labels.json").read_bytes()),
                  "controls": {"relevant": .9, "irrelevant": .1}, "peak_rss_gib": 1,
                  "events": [{"id": i, "status": "SCORED", "scores": {"p": .9}, "seconds": .1}
                             for i in ("a", "b")]}
        probe.dump(p / "scores.json", scores)
        return SimpleNamespace(dataset=p / "data.json", labels=p / "labels.json",
                               scores=p / "scores.json", output=p / "summary.json"), scores

    def test_summary_checks_input_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            args, _ = self.summary_fixture(directory)
            args.labels.write_text(args.labels.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Frozen input"):
                probe.summarize(args)

    def test_summary_refuses_partial_run(self):
        with tempfile.TemporaryDirectory() as directory:
            args, scores = self.summary_fixture(directory)
            scores["complete"] = False
            probe.dump(args.scores, scores)
            with self.assertRaisesRegex(ValueError, "Incomplete"):
                probe.summarize(args)

    def test_summary_refuses_missing_candidate_score(self):
        with tempfile.TemporaryDirectory() as directory:
            args, scores = self.summary_fixture(directory)
            scores["events"][1]["scores"] = {}
            probe.dump(args.scores, scores)
            with self.assertRaisesRegex(ValueError, "Missing scores"):
                probe.summarize(args)

    def test_equal_quality_does_not_justify_model(self):
        with tempfile.TemporaryDirectory() as directory:
            args, _ = self.summary_fixture(directory)
            with contextlib.redirect_stdout(io.StringIO()):
                probe.summarize(args)
            result = json.loads(args.output.read_text())
            self.assertEqual(result["threshold"], .7)
            self.assertEqual(result["recall_gain_over_best_baseline"], 0)
            self.assertEqual(result["verdict"], "REJECT_THIS_CONFIGURATION")


if __name__ == "__main__":
    unittest.main()
