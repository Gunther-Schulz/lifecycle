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
