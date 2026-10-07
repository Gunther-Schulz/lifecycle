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


class ReportOnlyWouldRefuse(unittest.TestCase):
    """lc-88: a --merge --report-only over a source the real merge refuses
    REPORTS the collisions, as a plan-level warning, exit 0, nothing written.
    Two sources, two refusals; the real refusals keep their text and code."""

    def seeded(self):
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        return d

    HOMES = ("# second\n\n## Open\n\n"
             "- **READY 2026-08-03 — first.** a different body, same "
             "headline\n"
             "- **READY 2026-09-09 — genuinely new work.** body\n")
    SELF = ("# second\n\n## Open\n\n"
            "- **READY 2026-08-03 — repeated source work.** first body\n"
            "- **READY 2026-08-03 — repeated source work.** second body\n"
            "- **READY 2026-09-10 — genuinely new work.** body\n")

    def dry(self, d, text):
        (d / "SECOND.md").write_text(text, encoding="utf-8")
        before = (d / "ITEMS.md").read_bytes()
        report_before = (d / REPORT).read_bytes()
        code, out = migrate_run(d, "--from", "SECOND.md", "--from-done",
                                "NONE", "--merge", "--report-only")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual((d / "ITEMS.md").read_bytes(), before)
        self.assertNotEqual((d / REPORT).read_bytes(), report_before,
                            "the dry run wrote no report, so this arm "
                            "graded a file it did not produce")
        return out, (d / REPORT).read_text(encoding="utf-8")

    def real(self, d, text):
        (d / "SECOND.md").write_text(text, encoding="utf-8")
        return migrate_run(d, "--from", "SECOND.md", "--from-done", "NONE",
                           "--merge")

    def test_arm1_a_source_colliding_with_the_homes_is_reported(self):
        d = self.seeded()
        out, report = self.dry(d, self.HOMES)
        for text in (out, report):
            self.assertIn("merge_duplicate_body", text)
            self.assertIn("WOULD refuse", text)
        code, real_out = self.real(d, self.HOMES)
        self.assertEqual(code, exits.FINDING, real_out)
        self.assertIn("FINDING [merge_duplicate_body]", real_out)

    def test_arm2_a_source_repeating_itself_is_reported(self):
        d = self.seeded()
        out, report = self.dry(d, self.SELF)
        for text in (out, report):
            self.assertIn("merge_source_self_duplicate", text)
            self.assertIn("WOULD refuse", text)
        code, real_out = self.real(d, self.SELF)
        self.assertEqual(code, exits.FINDING, real_out)
        self.assertIn("FINDING [merge_source_self_duplicate]", real_out)

    def test_control_a_clean_source_gets_no_would_refuse_warning(self):
        d = self.seeded()
        out, report = self.dry(
            d, "# second\n\n## Open\n\n"
               "- **READY 2026-09-09 — genuinely new work.** body\n")
        for text in (out, report):
            self.assertNotIn("WOULD refuse", text)
