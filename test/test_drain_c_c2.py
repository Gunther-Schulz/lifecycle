"""Drain wave C, lane C2 — a row's name in its own output; the lane name
`init --lane` writes through.

One class per item, each carrying the arms its done-criterion names.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits, refusals, roster  # noqa: E402


# --- lc-316 ------------------------------------------------------------------

#: The five rows lc-316 names. Stated HERE, from the item, and never derived
#: from the roster: the arm below asserts the roster's own unnamed set against
#: it, and an expectation read off the roster would move with it.
LC316_ROWS = (
    "laws_absent_could_not_verify",
    "unknown_grade_read",
    "grade_arm_malformed",
    "cost_test_unverified",
    "conservation_unverified",
)


def _named(row, fired) -> bool:
    return f"[{row.expected_finding_row}]" in fired.output


class EveryRowIsNamedInItsOwnOutput(unittest.TestCase):
    """lc-316: a row is named in its plant's output WHATEVER its expected
    code. A could-not-verify row that prints no name is graded on exit code
    3 alone, and every could-not-verify is a 3.
    """

    def test_no_row_fires_without_naming_itself(self):
        unnamed = []
        ran = 0
        for row in refusals.ROWS:
            if getattr(row, "skip_reason", None):
                continue
            ran += 1
            if not _named(row, row.fire()):
                unnamed.append(row.ident)
        # The population, stated: a loop over nothing would pass this arm.
        self.assertGreater(ran, 100, "the roster walk examined too few rows "
                                     "to mean anything")
        self.assertEqual(unnamed, [], "row(s) whose plant output carries no "
                                      "bracketed row name")

    def test_the_five_named_rows_keep_their_exit_code(self):
        """MUST-NOT-MOVE: naming a row changes no exit code. Each of the five
        still exits COULD NOT VERIFY, and now says which row answered.
        """
        by_ident = {r.ident: r for r in refusals.ROWS}
        for ident in LC316_ROWS:
            with self.subTest(row=ident):
                row = by_ident[ident]
                fired = row.fire()
                self.assertEqual(fired.code, exits.COULD_NOT_VERIFY,
                                 fired.output)
                self.assertTrue(_named(row, fired), fired.output)
                # The control must NOT carry the name: a tag printed on
                # every path names nothing.
                self.assertFalse(_named(row, row.control()),
                                 "the control's output carries the row name "
                                 "too, so the name separates nothing")


def _fake_row(*, output: str) -> refusals.Row:
    return refusals.Row(
        ident="lc316_probe_row",
        refusal="a probe row for the roster's own name check",
        firing_input="a plant exiting COULD NOT VERIFY",
        expect=exits.COULD_NOT_VERIFY,
        fire=lambda: refusals.Fired(exits.COULD_NOT_VERIFY, output),
        control=lambda: refusals.Fired(exits.CLEAN, "clean\n"),
    )


def _roster_lines(row) -> list:
    """Run the real roster runner over ONE row and return its lines."""
    buf = io.StringIO()
    with mock.patch.object(refusals, "ROWS", [row]):
        roster.cmd_test(lambda s="": buf.write(str(s) + "\n"))
    return buf.getvalue().splitlines()


class TheRosterNameCheckIsNotGatedOnFinding(unittest.TestCase):
    """lc-316, the other half: the roster's own name check ran only for rows
    expecting FINDING, so an unnamed could-not-verify row read PASS.

    The pair differs in the plant's OUTPUT alone — same row, same codes.
    """

    def test_an_unnamed_could_not_verify_plant_fails_the_row(self):
        lines = _roster_lines(_fake_row(
            output="COULD NOT VERIFY: something, under no name\n"))
        verdict = [ln for ln in lines if "lc316_probe_row" in ln
                   and ln.split()[:1] in (["PASS"], ["FAIL"])]
        self.assertEqual(len(verdict), 1, lines)
        self.assertTrue(verdict[0].startswith("FAIL"), verdict[0])
        self.assertTrue(
            any("names row [lc316_probe_row]" in ln.replace("\n", " ")
                or "row [lc316_probe_row]" in ln for ln in lines), lines)

    def test_a_named_could_not_verify_plant_passes_the_row(self):
        lines = _roster_lines(_fake_row(
            output="COULD NOT VERIFY [lc316_probe_row] something\n"))
        verdict = [ln for ln in lines if "lc316_probe_row" in ln
                   and ln.split()[:1] in (["PASS"], ["FAIL"])]
        self.assertEqual(len(verdict), 1, lines)
        self.assertTrue(verdict[0].startswith("PASS"), verdict[0])


# --- lc-317 ------------------------------------------------------------------

ENTRY = Path(__file__).resolve().parents[1] / "plugin" / "cli" / "lifecycle"


class InitRefusesAnUnsafeLaneName(unittest.TestCase):
    """lc-317: `init --lane <name>` builds `lanes/<name>.md` from the
    caller's word. An unsafe one is refused BEFORE ANY WRITE, under the same
    finding `lane new` gives the same input.

    Every arm drives the REAL ENTRY POINT in a child process, because one of
    the three inputs used to end in a traceback and the question is the
    PROCESS exit code: a crash is a 1, and a 1 is none of the three answers.
    """

    def setUp(self):
        # The repo sits one level DOWN inside the scratch root, so a name
        # that climbs out of it (`../escape`) lands somewhere this test can
        # see and removes afterwards.
        self.root = Path(tempfile.mkdtemp(prefix="lifecycle-c2-init-"))
        self.repo = self.root / "outer" / "repo"
        self.repo.mkdir(parents=True)
        self._git("init", "-q", "-b", "main")
        self._git("config", "core.hooksPath", str(self.repo / ".nohooks"))
        self._git("config", "user.email", "op@example.invalid")
        self._git("config", "user.name", "operator")
        (self.repo / "README.md").write_text("scratch\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _git(self, *argv):
        r = subprocess.run(["git", "-C", str(self.repo), *argv],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr

    def _tree(self) -> dict:
        """Every file under the scratch ROOT outside `.git`, with its bytes —
        the root and not the repo, so a write that escapes is in the view."""
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in sorted(self.root.rglob("*"))
                if p.is_file() and ".git" not in p.relative_to(self.root).parts}

    def _init(self, *lanes):
        argv = [sys.executable, str(ENTRY), "--repo", str(self.repo), "init",
                "--id-prefix", "zz"]
        for name in lanes:
            argv += ["--lane", name]
        r = subprocess.run(argv, capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def _assert_refused_and_nothing_written(self, *lanes):
        before = self._tree()
        code, out = self._init(*lanes)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [lane_new_unsafe_door]", out)
        self.assertNotIn("Traceback", out)
        self.assertEqual(self._tree(), before,
                         "the refusal wrote something anyway")

    def test_a_name_that_climbs_out_of_the_lanes_directory(self):
        self._assert_refused_and_nothing_written("../escape")

    def test_a_name_carrying_a_slash(self):
        self._assert_refused_and_nothing_written("bad/door")

    def test_the_empty_name(self):
        self._assert_refused_and_nothing_written("")

    def test_one_unsafe_name_refuses_the_safe_one_beside_it(self):
        """Before ANY write: the safe sibling's stub and the declaration are
        not written either, whichever order the names came in."""
        self._assert_refused_and_nothing_written("goodlane", "../escape")

    def test_a_safe_name_still_writes_its_stub(self):
        """CONTROL: the same verb in the same repo, the name's characters the
        only difference."""
        code, out = self._init("goodlane")
        self.assertNotIn("[lane_new_unsafe_door]", out)
        self.assertNotIn(code, (1, exits.FINDING), out)
        self.assertTrue((self.repo / "lanes" / "goodlane.md").is_file(), out)
        doc = json.loads((self.repo / ".claude" / "lifecycle.json")
                         .read_text(encoding="utf-8"))
        self.assertEqual(doc["lanes"], ["goodlane"])


if __name__ == "__main__":
    unittest.main()
