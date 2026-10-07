"""Drain wave E, lane E1 — the doors of close and add; the wrong repo.

lc-270: `item close` TOOK A BARE ID AND MOVED WHATEVER BODY CARRIED IT. An id
carried from a session's own summary rather than re-read at the carrier
closed the wrong item, and the only signal was the moved body printed AFTER
the act. `--expect TEXT` lets the caller say what the id is supposed to
name; the close then refuses, before anything moves, unless TEXT occurs in
the requirement IN FORCE for that id.

EVERY RED-FIRST ARM REACHES ONLY THROUGH NAMES THE OLD BUILD ALREADY HAD
(`cli.main`, `exits`, the roster's `_Repo` and fixtures, git), so a red
against the unmodified code is an assertion FAILURE at the defect and never
an import error (law 4).
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, exits  # noqa: E402
from lifecycle_core import refusals as R  # noqa: E402


def run(repo: Path, *argv):
    """`(code, output)` of one CLI run inside `repo`, stderr folded in."""
    here = os.getcwd()
    buf = io.StringIO()
    try:
        os.chdir(str(repo))
        with redirect_stdout(buf), redirect_stderr(buf):
            code = cli.main(["--repo", str(repo)] + list(argv))
    finally:
        os.chdir(here)
    return code, buf.getvalue()


def git(repo: Path, *argv) -> str:
    p = subprocess.run(["git", "-C", str(repo)] + list(argv),
                       capture_output=True, text=True)
    return p.stdout


# --- lc-270 -------------------------------------------------------------------

#: `R.SEED_ITEMS`'s one body, xx-1: "the harvest timer double-fires on a
#: rotated capture". The two expectations differ in the TEXT alone.
MATCHING = "harvest timer"
NOT_MATCHING = "the four audit arms"
CLOSE = ("item", "close", "xx-1", "--met", "none", "--decided", "none")
EXPECT_ROW = "FINDING [close_expect_mismatch]"


class CloseChecksWhatTheIdNames(unittest.TestCase):

    def _repo(self) -> Path:
        r = R._Repo(items=R.SEED_ITEMS)
        self.addCleanup(r.close)
        return r.dir

    def _homes(self, repo: Path) -> tuple:
        return ((repo / "ITEMS.md").read_bytes(),
                (repo / "ITEMS-DONE.md").read_bytes(),
                (repo / "LEDGER.md").read_bytes())

    # --- the red-first pair: one close, two expectations ----------------------

    def test_a_MATCHING_expectation_closes(self):
        repo = self._repo()
        code, outp = run(repo, *CLOSE, "--expect", MATCHING)
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertIn("## xx-1", (repo / "ITEMS-DONE.md").read_text())
        self.assertNotIn("## xx-1", (repo / "ITEMS.md").read_text())

    def test_a_NON_MATCHING_expectation_refuses_and_moves_nothing(self):
        repo = self._repo()
        before = self._homes(repo)
        head = git(repo, "rev-parse", "HEAD")
        code, outp = run(repo, *CLOSE, "--expect", NOT_MATCHING)
        self.assertEqual(code, exits.FINDING, outp)
        self.assertIn(EXPECT_ROW, outp)
        # THE REQUIREMENT HEAD, so the caller sees which item the id names.
        self.assertIn("the harvest timer double-fires", outp)
        self.assertIn(NOT_MATCHING, outp)
        self.assertEqual(self._homes(repo), before,
                         "refused, and a home changed anyway")
        self.assertEqual(git(repo, "rev-parse", "HEAD"), head)

    # --- the other answers ------------------------------------------------------

    def test_the_match_is_CASE_INSENSITIVE(self):
        repo = self._repo()
        code, outp = run(repo, *CLOSE, "--expect", "HARVEST Timer")
        self.assertEqual(code, exits.CLEAN, outp)

    def test_a_DROP_is_checked_the_same_way(self):
        repo = self._repo()
        before = self._homes(repo)
        code, outp = run(repo, "item", "close", "xx-1", "--drop", "--reason",
                         "overtaken", "--expect", NOT_MATCHING)
        self.assertEqual(code, exits.FINDING, outp)
        self.assertIn(EXPECT_ROW, outp)
        self.assertEqual(self._homes(repo), before)

    def test_the_requirement_IN_FORCE_is_what_is_matched(self):
        """An amended requirement supersedes: the base wording no longer
        names the item, the amended wording does."""
        repo = self._repo()
        code, outp = run(repo, "item", "amend", "xx-1", "--requirement",
                         "the sweep population grew while this stood",
                         "--reason", "the booked wording named the wrong half")
        self.assertEqual(code, exits.CLEAN, outp)
        before = self._homes(repo)
        code, outp = run(repo, *CLOSE, "--expect", MATCHING)
        self.assertEqual(code, exits.FINDING, outp)
        self.assertIn(EXPECT_ROW, outp)
        self.assertIn("the sweep population grew", outp)
        self.assertEqual(self._homes(repo), before)
        code, outp = run(repo, *CLOSE, "--expect", "sweep POPULATION")
        self.assertEqual(code, exits.CLEAN, outp)

    def test_an_EMPTY_expectation_is_not_a_check_that_passed(self):
        """Blank text occurs in every requirement, so it examined nothing."""
        repo = self._repo()
        before = self._homes(repo)
        code, outp = run(repo, *CLOSE, "--expect", "   ")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, outp)
        self.assertIn("--expect", outp)
        self.assertEqual(self._homes(repo), before)

    def test_an_UNKNOWN_id_keeps_its_own_refusal(self):
        repo = self._repo()
        code, outp = run(repo, "item", "close", "xx-77", "--met", "none",
                         "--decided", "none", "--expect", MATCHING)
        self.assertEqual(code, exits.FINDING, outp)
        self.assertIn("FINDING [unknown_item]", outp)
        self.assertNotIn(EXPECT_ROW, outp)

    # --- must-not-move: the close without the flag -----------------------------

    def test_CONTROL_a_close_WITHOUT_the_flag_is_unchanged(self):
        repo = self._repo()
        code, outp = run(repo, *CLOSE)
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertNotIn("expect", outp.lower())
        self.assertIn("## xx-1", (repo / "ITEMS-DONE.md").read_text())


if __name__ == "__main__":
    unittest.main()
