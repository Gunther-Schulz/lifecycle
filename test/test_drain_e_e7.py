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


if __name__ == "__main__":
    unittest.main()
