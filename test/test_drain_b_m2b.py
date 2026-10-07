"""Drain wave B, lane M2b: migrate provenance and residue defects."""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits  # noqa: E402

from test_migrate import MERGE_SOURCE_B, build, migrate_run  # noqa: E402
from test_migrate_residue import commit, tend_items  # noqa: E402


class SecondMergeBooksNoSecondResidue(unittest.TestCase):
    """lc-71 — a re-run of the same --merge appends no second residue item."""

    def test_two_merge_runs_of_one_source_book_one_residue_item(self):
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        commit(d, "docs/x.md", "see BACKLOG.md and SECOND.md\n")
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        (d / "SECOND.md").write_text(MERGE_SOURCE_B, encoding="utf-8")
        merge = ("--from", "SECOND.md", "--from-done", "NONE", "--merge")
        self.assertEqual(migrate_run(d, *merge)[0], exits.CLEAN)
        after_first = len(tend_items(d))
        self.assertEqual(after_first, 2, "one residue per distinct carrier")
        self.assertEqual(migrate_run(d, *merge)[0], exits.CLEAN)
        self.assertEqual(len(tend_items(d)), after_first,
                         "the second --merge appended another residue item")


if __name__ == "__main__":
    unittest.main()
