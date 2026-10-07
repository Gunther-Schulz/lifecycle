"""Drain wave B, lane M2a — migrate summary and gates (lc-85, lc-150, lc-88,
lc-34). Each arm is red-first against the unmodified code and carries its
MUST-NOT-MOVE partner."""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import re
import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits  # noqa: E402
from test_migrate import REPORT, build, migrate_run  # noqa: E402

ENTRY = "- **READY 2026-01-03 — an ordinary entry.** body\n"


class VacuousSummary(unittest.TestCase):
    """lc-85: a 0-read == 0-written run does not print a bare CLEAN."""

    def test_zero_entries_summary_says_vacuous_exit_stays_zero(self):
        d = build("# old\n\n## Open\n\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        summary = out.strip().splitlines()[-1]
        self.assertTrue(summary.startswith("migrate:"), summary)
        self.assertIn("vacuous", summary.lower(), summary)
        self.assertIn("examined no entry", summary)
        self.assertNotRegex(summary, r"^migrate: CLEAN\s*$")

    def test_control_a_run_that_migrated_an_entry_says_clean(self):
        d = build("# old\n\n## Open\n\n" + ENTRY)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(out.strip().splitlines()[-1], "migrate: CLEAN")
