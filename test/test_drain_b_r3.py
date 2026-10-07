"""Drain wave B, lane R3 — `lane list`, `lane new`, `verify`.

One class per item, each carrying the arms its done-criterion names. Every
arm drives the real verb through `cli.main` (or the real entry point, where
the question is the PROCESS exit code) over a scratch repo and a scratch XDG
config root — the roster these tests write is never the machine's own.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, exits, lanes  # noqa: E402
from lifecycle_core import refusals  # noqa: E402


def _run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(argv)
    return code, buf.getvalue()


class _ScratchRoster(unittest.TestCase):
    """`XDG_CONFIG_HOME` pointed at a fresh scratch dir per test.

    THE ISOLATION IS THE PREMISE AND IS PINNED HERE, not assumed: `lane list`
    reads the roster through `lanes.roster_path()`, which consumes exactly
    this one global. An arm that forgot it would grade the operator's real
    roster — and an arm that WRITES would write there.
    """

    def setUp(self):
        self._old_xdg = os.environ.get("XDG_CONFIG_HOME")
        self._scratch = tempfile.mkdtemp(prefix="lifecycle-r3-xdg-")
        os.environ["XDG_CONFIG_HOME"] = self._scratch
        self._repos = []
        # The premise, asserted: the roster this class writes is under the
        # scratch root and nowhere else.
        self.assertTrue(
            str(lanes.roster_path()).startswith(self._scratch),
            "the roster path is not under this test's scratch root")

    def tearDown(self):
        if self._old_xdg is None:
            os.environ.pop("XDG_CONFIG_HOME", None)
        else:
            os.environ["XDG_CONFIG_HOME"] = self._old_xdg
        shutil.rmtree(self._scratch, ignore_errors=True)
        for r in self._repos:
            r.close()

    def write_roster_text(self, text):
        path = lanes.roster_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def repo(self, **kw):
        r = refusals._Repo(**kw)
        self._repos.append(r)
        return r


# --- lc-212 -------------------------------------------------------------------

#: A roster carrying comments and no entry — spelled here by hand rather than
#: read from `lanes.py`, so the comment-only arm is not derived from the
#: module it grades.
_ROSTER_HEADER_ONLY = ("# lifecycle roster — one repo path per line.\n"
                       "# nothing is listed below this line.\n")


class AnEmptyRosterIsAFinding(_ScratchRoster):
    """lc-212. The router is GENERATED over the roster, so a roster listing
    nothing is a board that was never pointed at anything — and it exited
    CLEAN between two neighbours (absent, unresolvable) that both refuse.

    THREE ARMS, and the third bounds the fix: absent stays a finding under
    its own row; empty becomes a finding under a row of its OWN; a roster
    listing one repo that declares zero lanes stays clean.
    """

    def test_arm_1_an_absent_roster_is_still_a_finding_under_its_own_row(self):
        code, out = _run(["lane", "list"])
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [roster_absent]", out)
        self.assertNotIn("[roster_empty]", out)

    def test_arm_2_a_zero_byte_roster_is_a_finding_naming_its_own_repair(self):
        self.write_roster_text("")
        code, out = _run(["lane", "list"])
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [roster_empty]", out)
        # ITS OWN ROW: the repairs differ (create the file vs register a
        # repo), so the absent row's name must not appear beside it.
        self.assertNotIn("[roster_absent]", out)
        self.assertIn("lane register", out)
        self.assertIn("lane list: FINDING", out)
        self.assertNotIn("lane list: CLEAN", out)

    def test_arm_2_a_comment_only_roster_is_empty_too(self):
        # A header and no entry is the same state: nothing is LISTED. An
        # arm over the zero-byte file alone would pass a fix keyed on file
        # size, which this shape walks straight past.
        self.write_roster_text(_ROSTER_HEADER_ONLY)
        code, out = _run(["lane", "list"])
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [roster_empty]", out)
        self.assertNotIn("[roster_absent]", out)

    def test_arm_2_the_json_rendering_carries_the_same_finding_and_exit(self):
        self.write_roster_text(_ROSTER_HEADER_ONLY)
        code_text, out_text = _run(["lane", "list"])
        code_json, out_json = _run(["lane", "list", "--json"])
        self.assertEqual(code_text, code_json, out_text)
        doc = json.loads(out_json)
        self.assertEqual(doc["exit"], exits.FINDING)
        self.assertEqual([f["row"] for f in doc["findings"]], ["roster_empty"])
        self.assertFalse(doc.get("roster_absent", False))

    def test_arm_3_CONTROL_one_repo_declaring_zero_lanes_stays_clean(self):
        # The documented good case (CLAUDE.md, "The router": a repo declaring
        # zero lanes "says so in a line of its own"). A fix that refused
        # every zero-lane BOARD rather than the empty ROSTER breaks this.
        r = self.repo(lanes=[])
        self.write_roster_text(str(r.dir) + "\n")
        code, out = _run(["lane", "list"])
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("roster count: 1 repo(s) listed", out)
        self.assertIn("declared lanes: 0", out)
        self.assertNotIn("[roster_empty]", out)
        self.assertIn("lane list: CLEAN", out)

    def test_the_refusal_is_a_registry_row_separate_from_roster_absent(self):
        idents = [r.ident for r in refusals.ROWS]
        self.assertIn("roster_empty", idents)
        self.assertIn("roster_absent", idents)
        row = next(r for r in refusals.ROWS if r.ident == "roster_empty")
        self.assertEqual(row.expect, exits.FINDING)
        self.assertEqual(row.expected_finding_row, "roster_empty")


if __name__ == "__main__":
    unittest.main()
