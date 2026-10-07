"""Drain wave E, lane E7 — the migrator (lc-36, lc-217, lc-150 arm 2).

Each arm is red-first against the unmodified code and carries its
MUST-NOT-MOVE partner."""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits, items, migrate  # noqa: E402
from test_migrate import build, migrate_run  # noqa: E402


def read_requirements(repo: Path) -> list:
    text = (repo / "ITEMS.md").read_text(encoding="utf-8")
    return [ln[len("requirement: "):] for ln in text.splitlines()
            if ln.startswith("requirement: ")]


class TruncatedRequirementIsMarked(unittest.TestCase):
    """lc-36: a headline longer than the slot cut is never a bare ellipsis;
    the slot says TRUNCATED and carries the source range."""

    def long_source(self):
        pad = "word " * (migrate.REQUIREMENT_CAP // 5 + 30)
        return ("# old\n\n## Open\n\n"
                f"- **READY 2026-01-03 — {pad.strip()}.** body line\n")

    def test_a_long_headline_carries_TRUNCATED_and_its_range(self):
        d = build(self.long_source())
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        req = read_requirements(d)
        self.assertEqual(len(req), 1, req)
        self.assertIn("TRUNCATED", req[0])
        self.assertRegex(req[0], r"BACKLOG\.md:\d+-\d+")
        self.assertNotRegex(req[0].split(" — record:")[0].split("[")[0],
                            r"…$")

    def test_control_a_headline_that_fits_travels_whole_unmarked(self):
        d = build("# old\n\n## Open\n\n"
                  "- **READY 2026-01-03 — a short headline.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        req = read_requirements(d)
        self.assertEqual(len(req), 1, req)
        self.assertNotIn("TRUNCATED", req[0])
        self.assertTrue(req[0].startswith("READY 2026-01-03 — a short headline")
                        or "a short headline" in req[0], req[0])

    def test_no_record_file_is_written_for_a_truncated_item(self):
        d = build(self.long_source())
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        before = {p.name for p in d.rglob("*") if p.is_file()
                  and ".git" not in p.parts}
        migrate_run(d)
        after = {p.name for p in d.rglob("*") if p.is_file()
                 and ".git" not in p.parts}
        extra = after - before
        self.assertFalse([n for n in extra if "record" in n.lower()], extra)


class UnreadableLedgerLineIsNotZero(unittest.TestCase):
    """lc-150 ARM 2 ONLY (wave E ruling: the absolute count stays, arm 1 is
    withdrawn). An unreadable ledger line is could-not-verify with its
    reason, never folded into 'ledger lines: 0' and CLEAN."""

    ENTRY = "# old\n\n## Open\n\n- **READY 2026-01-03 — one.** body\n"

    def seeded(self, line: str):
        d = build(self.ENTRY)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        with open(d / "LEDGER.md", "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        return d

    def test_an_unclassifiable_line_is_could_not_verify_never_clean(self):
        from lifecycle_core import ledger as ledger_mod
        line = "this line is in no ledger kind at all"
        self.assertIsNone(ledger_mod.parse_line(line))
        d = self.seeded(line)
        code, out = migrate_run(d)
        self.assertIn("UNREADABLE", out)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("COULD NOT VERIFY", out)
        self.assertIn("LEDGER.md", out)
        self.assertNotIn("migrate: CLEAN", out)

    def test_control_one_well_formed_line_still_gives_the_finding(self):
        from lifecycle_core import ledger as ledger_mod
        line = ledger_mod.render("superseded", {
            "id": "x-1", "by": "x-2", "reason": "a reason"})
        self.assertIsNotNone(ledger_mod.parse_line(line))
        d = self.seeded(line)
        code, out = migrate_run(d)
        self.assertIn("FINDING [migration_ledger_nonzero]", out)
        self.assertEqual(code, exits.FINDING, out)

    def test_control_a_clean_ledger_stays_clean(self):
        d = build(self.ENTRY)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("COULD NOT VERIFY", out)


if __name__ == "__main__":
    unittest.main()
