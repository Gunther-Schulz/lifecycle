"""The suite does not write to the operator's machine-wide fire log (lc-183).

MEASURED BEFORE ANY OF THIS EXISTED: one `unittest discover` run appended 869
records to a live 132MB / 1.2M-line log, and 81.6% of that file's records
carried a `/tmp` repo path — scratch repos built by this suite and by
`tools/prove-rows.py`. The busiest single day in it, 435,065 records, is a
test-run signature rather than a day of work.

THE PARTIAL-OVERRIDE CLASS, which is why two isolating files were not enough.
`test_desk` and `test_declaration` each rebound `XDG_STATE_HOME` around their
own arms — correctly — while every other arm ran against live state. A
fixture that isolates the destination while a sibling global stays keyed to
the real world aims the exercised path at real data OUTSIDE the test, and its
green is identical either way. The exercised path here is an APPEND: nothing
fails, the record just grows.

WHAT THESE ARMS ARE FOR. The isolation is an ABSENCE — "the real log did not
grow" — and an absence needs the instrument shown live, so the second class
below writes through the real code path and proves it still records. An
isolation that worked by breaking the logger would pass the first arm and
fail the second, and it would be the worse outcome: a polluted register
traded for no register.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import ast
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugin" / "cli"))

from lifecycle_core import firelog  # noqa: E402

ISOLATION_IMPORT = "_isolation"


class EveryTestModuleImportsTheIsolation(unittest.TestCase):
    """DERIVED FROM THE DIRECTORY, never a list restated beside it.

    A hardcoded roster of modules is the coverage assertion that cannot age
    loudly: the suite gains a file, the assertion stays green, and the new
    file writes to the operator's log exactly as every file did before this
    item. So the population is read from disk at run time.
    """

    def test_no_test_module_is_missing_it(self):
        missing = []
        for path in sorted((ROOT / "test").glob("test_*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names.update(a.name for a in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names.add(node.module)
            if ISOLATION_IMPORT not in names:
                missing.append(path.name)
        self.assertEqual(
            missing, [],
            "these test modules do not import `_isolation`, so the verbs they "
            "drive append to the operator's machine-wide fire log: "
            + ", ".join(missing))

    def test_the_check_would_notice_a_module_that_lacked_it(self):
        """The known positive: the predicate above returns [] over the real
        directory, and a zero from a predicate nobody has seen fire is what a
        dead check returns too."""
        tree = ast.parse("import os\n")
        names = {a.name for n in ast.walk(tree)
                 if isinstance(n, ast.Import) for a in n.names}
        self.assertNotIn(ISOLATION_IMPORT, names,
                         "the import detector matches a module that has no "
                         "such import, so its clean answer proves nothing")


class TheLogStillRecordsRealRuns(unittest.TestCase):
    """MUST-NOT-MOVE: this isolates the suite, it does not silence the log."""

    def test_a_fire_lands_in_the_redirected_home_and_is_readable(self):
        before = firelog.log_path()
        self.assertTrue(
            str(before).startswith(os.environ["XDG_STATE_HOME"]),
            f"the log path is not inside this run's scratch state dir: "
            f"{before}")
        firelog.fire("test-probe", repo="/tmp/lc183-probe", outcome=0)
        self.assertTrue(before.is_file(),
                        "the logger wrote nothing at all — an isolation that "
                        "works by breaking the instrument is the worse "
                        "outcome")
        text = before.read_text(encoding="utf-8")
        self.assertIn("test-probe", text,
                      "the record did not reach the redirected log")

    def test_the_redirected_home_is_NOT_the_users_own(self):
        """The arm that would have failed before this item, and the only one
        that distinguishes a real isolation from a fixture that happens to
        agree with the machine."""
        real = Path.home() / ".local" / "state" / "lifecycle" / "fire.jsonl"
        self.assertNotEqual(firelog.log_path().resolve(), real.resolve())


class TheRosterSelfTestKeepsItsRowsOutOfTheLiveLog(unittest.TestCase):
    """lc-304: `lifecycle --test` drives every roster row, and each row that
    runs a real verb appends a record. Measured 2026-10-04: 169 per run, into
    the operator's machine-wide log.

    The live log is stood in for by a scratch HOME with `XDG_STATE_HOME`
    UNSET, which is the production arrangement: the suite's own isolation
    sets the variable, so an arm that left it set would test the fixture and
    never the fallback the defect lives in. The roster is replaced by one
    stub row that fires one record, so the arm costs nothing and still
    separates "rows land live" from "rows land in scratch".
    """

    def setUp(self):
        import shutil
        import tempfile
        from lifecycle_core import roster
        self.roster = roster
        self.home = Path(tempfile.mkdtemp(prefix="lc304-home-"))
        self.addCleanup(shutil.rmtree, self.home, ignore_errors=True)
        self.env = {k: os.environ.get(k) for k in ("HOME", "XDG_STATE_HOME")}
        self.cmd_test = roster.cmd_test

        def stub(out, list_only=False):
            firelog.fire("stub-row", repo="/scratch/lifecycle-verb-x")
            return 0
        roster.cmd_test = stub
        os.environ["HOME"] = str(self.home)

    def tearDown(self):
        self.roster.cmd_test = self.cmd_test
        for k, v in self.env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def _verbs(self, log):
        import json
        if not log.is_file():
            return []
        return [json.loads(ln)["verb"]
                for ln in log.read_text(encoding="utf-8").splitlines()]

    def test_with_no_state_home_set_only_the_run_itself_is_logged_live(self):
        from lifecycle_core import cli
        os.environ.pop("XDG_STATE_HOME", None)
        live = firelog.log_path()
        self.assertTrue(str(live).startswith(str(self.home)), live)
        self.assertEqual(cli.main(["--test"]), 0)
        self.assertEqual(self._verbs(live), ["--test"])
        self.assertNotIn("XDG_STATE_HOME", os.environ)

    def test_a_state_home_the_caller_set_is_left_alone(self):
        from lifecycle_core import cli
        state = self.home / "callers-state"
        os.environ["XDG_STATE_HOME"] = str(state)
        self.assertEqual(cli.main(["--test"]), 0)
        self.assertEqual(self._verbs(state / "lifecycle" / "fire.jsonl"),
                         ["stub-row", "--test"])
        self.assertEqual(os.environ["XDG_STATE_HOME"], str(state))
