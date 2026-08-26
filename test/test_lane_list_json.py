"""Wave 2, item B: `lane list --json` — the query surface for consumers.

THE NON-NEGOTIABLE (design, established fact 7 + the brief's settled design
B): `--json` changes the RENDERING, never the VERDICT. Same roster, same
repos -> `lane list` and `lane list --json` must produce the SAME exit code
and the SAME finding set, not merely equal counts (two different sets of the
same size would pass a count check). Both renderers here are built from one
shared walk (`lanes.gather_lane_list`) for exactly this reason — see that
module's own docstring at the `lane list` section.

This file proves it stays true across the states the design cares about:
a firing lane, a broken one (the finding it exists to make loud), a repo
with declared lanes of zero (the arm this whole item exists for — "0 lanes"
and "this repo was skipped" must not read the same), an unresolved roster
entry, and an absent roster.
"""

import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, lanes  # noqa: E402
from lifecycle_core import refusals  # noqa: E402


def _run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(argv)
    return code, buf.getvalue()


class LaneListJsonBase(unittest.TestCase):
    """Points `XDG_CONFIG_HOME` at a fresh scratch dir per test, so the
    roster is this test's own and never a real one on the machine running
    the suite — the same isolation `lanes.roster_path()` is designed for."""

    def setUp(self):
        self._old_xdg = os.environ.get("XDG_CONFIG_HOME")
        self._scratch = tempfile.mkdtemp(prefix="lifecycle-json-xdg-")
        os.environ["XDG_CONFIG_HOME"] = self._scratch
        self._repos = []

    def tearDown(self):
        if self._old_xdg is None:
            os.environ.pop("XDG_CONFIG_HOME", None)
        else:
            os.environ["XDG_CONFIG_HOME"] = self._old_xdg
        import shutil
        shutil.rmtree(self._scratch, ignore_errors=True)
        for r in self._repos:
            r.close()

    def write_roster(self, *lines):
        path = lanes.roster_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def repo(self, **kw):
        r = refusals._Repo(**kw)
        self._repos.append(r)
        return r


class MustNotMoveRow(LaneListJsonBase):
    """Arm 9: same roster, same repos -> `lane list` and `lane list --json`
    exit identically and carry the identical finding set — the row ids at
    every level (declaration findings, repo-unresolved, trigger-broken), not
    only equal counts.
    """

    def test_a_firing_and_a_broken_lane_agree_on_exit_and_findings(self):
        r1 = self.repo(lanes=["drain"], lane_files={
            "drain": "Decides: x\nTrigger: exit 0\n| a | b |\n|---|---|\n"
                     "Ends: y\n"})
        r2 = self.repo(lanes=["bust"], lane_files={
            "bust": "Decides: x\nTrigger: exit 5\n| a | b |\n|---|---|\n"
                    "Ends: y\n"})
        self.write_roster(str(r1.dir), str(r2.dir), "/no/such/path")

        code_text, out_text = _run(["lane", "list"])
        code_json, out_json = _run(["lane", "list", "--json"])

        self.assertEqual(code_text, code_json)
        self.assertEqual(code_text, 2, out_text)  # a real assertion, not just "equal"

        import json
        doc = json.loads(out_json)
        self.assertEqual(doc["exit"], code_text)

        # The finding SET, by row id, not by count: repo_unresolved once,
        # trigger_broken once, drawn from the JSON structure.
        found_rows = {f["row"] for r in doc["repos"] for f in r.get("findings", [])}
        found_rows |= {ln.get("row") for r in doc["repos"]
                      for ln in r.get("lanes", []) if ln.get("row")}
        self.assertEqual(found_rows, {"repo_unresolved", "trigger_broken"})

        # Same set is visible in the longhand text too — a different
        # RENDERING of the identical finding.
        self.assertIn("FINDING [repo_unresolved]", out_text)
        self.assertIn("FINDING [trigger_broken]", out_text)
        self.assertEqual(doc["fired"], 1)
        self.assertEqual(doc["broken"], 1)
        self.assertEqual(doc["quiet"], 0)

    def test_a_malformed_declaration_agrees_on_exit_and_findings(self):
        bad = dict(refusals.GOOD_FULL_DECLARATION)
        del bad["goals"]
        r = self.repo(declaration=bad)
        self.write_roster(str(r.dir))

        code_text, out_text = _run(["lane", "list"])
        code_json, out_json = _run(["lane", "list", "--json"])
        self.assertEqual(code_text, code_json)
        self.assertEqual(code_text, 2, out_text)

        import json
        doc = json.loads(out_json)
        rows = {f["row"] for f in doc["repos"][0]["declaration"]["findings"]}
        self.assertIn("declaration_malformed", rows)
        self.assertIn("FINDING [declaration_malformed]", out_text)

    def test_no_run_agrees_on_exit_as_could_not_verify(self):
        r = self.repo(lanes=["drain"],
                      lane_files={"drain": "Decides: x\nTrigger: exit 0\nEnds: y\n"})
        self.write_roster(str(r.dir))
        code_text, out_text = _run(["lane", "list", "--no-run"])
        code_json, out_json = _run(["lane", "list", "--no-run", "--json"])
        self.assertEqual(code_text, code_json)
        self.assertEqual(code_text, 3, out_text)  # COULD_NOT_VERIFY
        import json
        doc = json.loads(out_json)
        self.assertTrue(doc["repos"][0]["lanes"][0]["not_run"])
        self.assertIn("NOT RUN (--no-run)", out_text)


class TheZeros(LaneListJsonBase):
    """Arm 10 — the arm this whole item exists for: a repo with zero
    declared lanes states the zero explicitly in JSON too, and a
    roster-absent run emits ITS finding in JSON as well. Neither renders as
    silence, which would read as clean.
    """

    def test_a_repo_with_zero_declared_lanes_states_the_zero(self):
        r = self.repo(lanes=[])
        self.write_roster(str(r.dir))

        code_text, out_text = _run(["lane", "list"])
        code_json, out_json = _run(["lane", "list", "--json"])
        self.assertEqual(code_text, code_json, out_text)
        self.assertEqual(code_text, 0, out_text)  # CLEAN

        import json
        doc = json.loads(out_json)
        self.assertEqual(doc["repos"][0]["lanes_declared"], [])
        self.assertIn("lanes_declared", doc["repos"][0])  # present, not omitted
        self.assertEqual(doc["lanes_total"], 0)
        self.assertIn("declared lanes: 0", out_text)
        self.assertIn("EMPTY, declared rather than absent", out_text)

    def test_an_absent_roster_emits_its_finding_in_json_too(self):
        # No write_roster() call at all: the roster file was never created.
        code_text, out_text = _run(["lane", "list"])
        code_json, out_json = _run(["lane", "list", "--json"])
        self.assertEqual(code_text, code_json)
        self.assertEqual(code_text, 2, out_text)  # a FINDING, never CLEAN

        import json
        doc = json.loads(out_json)
        self.assertTrue(doc["roster_absent"])
        self.assertEqual(doc["findings"][0]["row"], "roster_absent")
        self.assertIn("FINDING [roster_absent]", out_text)

    def test_json_output_is_a_single_document_not_interleaved(self):
        """B's own non-negotiable: 'Output is a single JSON document on
        stdout. Longhand lines do not interleave with it.'"""
        r = self.repo(lanes=["drain"],
                      lane_files={"drain": "Decides: x\nTrigger: exit 1\nEnds: y\n"})
        self.write_roster(str(r.dir))
        _code, out_json = _run(["lane", "list", "--json"])
        import json
        # json.loads succeeding on the WHOLE stdout is the proof: any stray
        # longhand line before or after the document would break the parse.
        doc = json.loads(out_json)
        self.assertIsInstance(doc, dict)


if __name__ == "__main__":
    unittest.main()
