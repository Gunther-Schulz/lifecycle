"""Drain wave E, lane E5: instruments that say less than they do.

lc-198: a SKIPPED reach arm must be visible in the suite verdict
(`tools/verify-suite.py`), read off the result object.
lc-136: the explicit-zero sweep's disposition table.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools" / "verify-suite.py"
TEST_DIR = REPO_ROOT / "test"

CLEAN, FINDING, COULD_NOT_VERIFY = 0, 2, 3


def _suite(body: str) -> Path:
    """A throwaway one-file suite; returns its directory."""
    d = Path(tempfile.mkdtemp(prefix="lane-e5-suite-"))
    (d / "test_probe.py").write_text(textwrap.dedent(body), encoding="utf-8")
    return d


def _run(start_dir: Path):
    return subprocess.run(
        [sys.executable, str(TOOL), "--start-dir", str(start_dir)],
        capture_output=True, text=True, timeout=120)


class ReachArmSkipIsVisible(unittest.TestCase):

    def test_the_real_reach_arm_carries_the_REACH_ARM_marker_when_it_skips(self):
        """The arm lc-198 names, run for real with its sibling input absent.

        `Path.exists` is patched to False so the arm skips on every machine,
        including one that DOES have a sibling dotfiles checkout; the skip
        reason is read off the result object, never a -v rendering (law 17).
        """
        sys.path.insert(0, str(TEST_DIR))
        try:
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromName(
                "test_verbs.LedgerStorableBlocker."
                "test_the_67_REPAIRED_dotfiles_TEXTS_all_pass_and_the_OLD_ONES_do_not")
            res = unittest.TestResult()
            with mock.patch("pathlib.Path.exists", return_value=False):
                suite.run(res)
        finally:
            sys.path.remove(str(TEST_DIR))
        self.assertEqual(len(res.skipped), 1, res.skipped)
        self.assertTrue(res.skipped[0][1].startswith("REACH ARM:"),
                        res.skipped[0][1])

    def test_a_reach_arm_skip_is_COULD_NOT_VERIFY_with_the_count_stated(self):
        d = _suite('''
            import unittest
            class T(unittest.TestCase):
                def test_ok(self):
                    pass
                def test_reach(self):
                    self.skipTest("REACH ARM: no sibling checkout")
        ''')
        p = _run(d)
        self.assertEqual(p.returncode, COULD_NOT_VERIFY, p.stdout + p.stderr)
        self.assertIn("skipped: 1", p.stdout)
        self.assertIn("test_probe.T.test_reach", p.stdout)
        self.assertIn("COULD NOT VERIFY", p.stdout)

    def test_an_ordinary_skip_is_reported_and_stays_clean(self):
        """MUST-NOT-MOVE: an arm that legitimately cannot run may skip."""
        d = _suite('''
            import unittest
            class T(unittest.TestCase):
                def test_ok(self):
                    pass
                def test_other(self):
                    self.skipTest("platform has no such thing")
        ''')
        p = _run(d)
        self.assertEqual(p.returncode, CLEAN, p.stdout + p.stderr)
        self.assertIn("skipped: 1", p.stdout)
        self.assertIn("test_probe.T.test_other", p.stdout)

    def test_a_failure_is_a_finding_and_zero_skips_is_stated(self):
        d = _suite('''
            import unittest
            class T(unittest.TestCase):
                def test_bad(self):
                    self.assertEqual(1, 2)
        ''')
        p = _run(d)
        self.assertEqual(p.returncode, FINDING, p.stdout + p.stderr)
        self.assertIn("skipped: 0", p.stdout)

    def test_a_run_that_examined_nothing_is_COULD_NOT_VERIFY(self):
        d = Path(tempfile.mkdtemp(prefix="lane-e5-suite-"))
        p = _run(d)
        self.assertEqual(p.returncode, COULD_NOT_VERIFY, p.stdout + p.stderr)
        self.assertIn("ran: 0", p.stdout)

    def test_a_reach_skip_outranks_a_failure(self):
        d = _suite('''
            import unittest
            class T(unittest.TestCase):
                def test_bad(self):
                    self.assertEqual(1, 2)
                def test_reach(self):
                    self.skipTest("REACH ARM: gone")
        ''')
        p = _run(d)
        self.assertEqual(p.returncode, COULD_NOT_VERIFY, p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
