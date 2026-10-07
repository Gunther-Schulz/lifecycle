"""Drain wave B, lane M2b: migrate provenance and residue defects."""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits, migrate  # noqa: E402

from test_migrate import (LIVE_HEAD, MERGE_SOURCE_B, build, commit_all,  # noqa: E402
                          migrate_run, retire_run, run_cli)
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


class ReadersAreWholePathComponents(unittest.TestCase):
    """lc-83 — the consumer list names carrier-name matches, not substrings."""

    def test_a_longer_name_is_not_a_consumer_and_the_matched_line_is_shown(self):
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        commit(d, "doc.md", "see FEATURE-BACKLOG.md for the other repo\n")
        commit(d, "genuine.md", "intro\nThe queue lives in BACKLOG.md here.\n")
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        ev = tend_items(d)[0].slots["evidence"]
        self.assertIn("genuine.md", ev)
        self.assertIn("The queue lives in BACKLOG.md here.", ev)
        self.assertNotIn("doc.md", ev)

    def test_a_path_component_spelling_is_still_a_consumer(self):
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        commit(d, "a.md", "cat ./BACKLOG.md\n")
        commit(d, "b.md", "`BACKLOG.md`, weekly\n")
        commit(d, "c.md", "BACKLOG.md.bak and MY_BACKLOG.md\n")
        migrate_run(d)
        ev = tend_items(d)[0].slots["evidence"]
        self.assertIn("a.md", ev)
        self.assertIn("b.md", ev)
        self.assertNotIn("c.md", ev)


class ArchiveMarkersAreNotItemProvenance(unittest.TestCase):
    """lc-94 — an archive's `## Done` pseudo-ident must not skip a new body."""

    CLOSED = ("# second\n\n## Open\n\n"
              "- **READY 2026-09-01 — alpha.** body\n\n"
              "## Done\n\n"
              "- **DONE 2026-08-01 — closed two.** body\n")

    def _first_merge(self):
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        migrate_run(d)
        commit_all(d, "m0")
        (d / "SECOND.md").write_text(self.CLOSED, encoding="utf-8")
        commit_all(d, "s")
        self.assertEqual(migrate_run(
            d, "--from", "SECOND.md", "--from-done", "NONE", "--merge")[0],
            exits.CLEAN)
        commit_all(d, "m1")
        return d

    def _remerge(self, d, text):
        (d / "SECOND.md").write_text(text, encoding="utf-8")
        return run_cli(d, "migrate", "--report", "docs/audits/r2.md",
                       "--from", "SECOND.md", "--from-done", "NONE",
                       "--merge")

    def test_a_new_open_entry_at_an_archived_closures_range_is_written(self):
        d = self._first_merge()
        # The first merge archived a closure marker for SECOND.md:15-16
        # (measured: the pseudo-ident `Done` in provenance_index). The
        # rewritten source puts a NEW open entry on exactly that range.
        pad = "\n".join(f"filler line {n}" for n in range(1, 10))
        new = ("# second\n\n## Open\n\n" + pad + "\n\n"
               "- **READY 2026-10-01 — brand new work.** body\n")
        self.assertEqual(new.split("\n").index(
            "- **READY 2026-10-01 — brand new work.** body") + 1, 15)
        code, out = self._remerge(d, new)
        # The exit is deliberately not graded: the rewritten source dropped
        # two entries the homes still hold, so the per-source arithmetic is
        # a separate, genuine COULD NOT VERIFY. The defect is the SKIP.
        self.assertNotIn("already migrated as Done", out)
        self.assertEqual(
            (d / "ITEMS.md").read_text(encoding="utf-8")
            .count("brand new work"), 1,
            "the new body was skipped as a re-import of the pseudo-ident")

    def test_a_body_in_a_done_home_block_is_still_a_reimport(self):
        """MUST NOT MOVE: the live blocks of both homes still answer 'is this
        body already present'."""
        d = self._first_merge()
        code, out = self._remerge(d, (d / "SECOND.md").read_text(
            encoding="utf-8"))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual((d / "ITEMS.md").read_text(encoding="utf-8")
                         .count("alpha"), 1)
        self.assertIn("RE-IMPORTS skipped:       2 ", out)


class ReimportResolvesThePinnedBlob(unittest.TestCase):
    """lc-114 — the re-import lookup compares BODIES at the pinned blob."""

    TWO = ("# second\n\n## Open\n\n"
           "- **READY 2026-09-01 — alpha work.** alpha body\n"
           "- **READY 2026-09-02 — beta work.** beta body\n")

    def _merged(self):
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        migrate_run(d)
        commit_all(d, "m0")
        (d / "SECOND.md").write_text(self.TWO, encoding="utf-8")
        commit_all(d, "s")
        self.assertEqual(migrate_run(
            d, "--from", "SECOND.md", "--from-done", "NONE", "--merge")[0],
            exits.CLEAN)
        commit_all(d, "m1")
        return d

    def _remerge(self, d, text, report="docs/audits/r2.md"):
        (d / "SECOND.md").write_text(text, encoding="utf-8")
        return run_cli(d, "migrate", "--report", report, "--from",
                       "SECOND.md", "--from-done", "NONE", "--merge")

    def test_an_edit_above_a_migrated_entry_is_still_a_reimport(self):
        d = self._merged()
        before = (d / "ITEMS.md").read_text(encoding="utf-8")
        edited = (d / "SECOND.md").read_text(encoding="utf-8").replace(
            "## Open\n", "A paragraph added above.\nAnd another.\n\n## Open\n",
            1)
        code, out = self._remerge(d, edited)
        self.assertNotIn("merge_duplicate_body", out)
        self.assertIn("RE-IMPORTS skipped:       2 ", out)
        self.assertEqual((d / "ITEMS.md").read_text(encoding="utf-8")
                         .count("alpha work"), before.count("alpha work"))

    def test_a_new_duplicate_headline_with_another_body_still_refuses(self):
        """MUST NOT FIRE the other way: the repair is not a no-op."""
        d = self._merged()
        edited = (d / "SECOND.md").read_text(encoding="utf-8") + (
            "- **READY 2026-09-01 — alpha work.** a DIFFERENT body\n")
        code, out = self._remerge(d, edited)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[merge_duplicate_body]", out)

    def test_an_unpinned_anchor_is_could_not_verify_not_a_key_match(self):
        d = self._merged()
        items = (d / "ITEMS.md").read_text(encoding="utf-8")
        import re as _re
        unpinned = _re.sub(r"( at blob [0-9a-f]{40})", "", items)
        self.assertNotEqual(unpinned, items)
        (d / "ITEMS.md").write_text(unpinned, encoding="utf-8")
        commit_all(d, "unpin")
        code, out = self._remerge(
            d, (d / "SECOND.md").read_text(encoding="utf-8") + (
                "- **READY 2026-09-09 — gamma work.** gamma body\n"))
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("COULD NOT VERIFY", out)
        self.assertNotIn("gamma work", (d / "ITEMS.md").read_text(
            encoding="utf-8"))

    def test_an_unresolvable_pin_is_could_not_verify(self):
        d = self._merged()
        items = (d / "ITEMS.md").read_text(encoding="utf-8")
        import re as _re
        gone = _re.sub(r" at blob [0-9a-f]{40}", " at blob " + "a" * 40, items)
        (d / "ITEMS.md").write_text(gone, encoding="utf-8")
        commit_all(d, "badpin")
        code, out = self._remerge(
            d, (d / "SECOND.md").read_text(encoding="utf-8") + (
                "- **READY 2026-09-09 — gamma work.** gamma body\n"))
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)


class DeletionRecordIdempotenceIsARowMatch(unittest.TestCase):
    """lc-214 — `already` is a ROW (this path AND this blob in one record)."""

    def _laws_with(self, d, text):
        (d / "LAWS.md").write_text(text, encoding="utf-8")
        commit_all(d, "laws")

    def test_an_earlier_blob_row_plus_this_blob_elsewhere_still_records(self):
        d = build(LIVE_HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        sha = migrate.blob_sha((d / "BACKLOG.md").read_bytes())
        earlier = "e" * 40
        # The discriminating input, drawn from a realistic laws file: the
        # same path at an EARLIER blob, and this run's blob cited in prose.
        self._laws_with(d, (
            "law\n\n## Deletion record — BACKLOG.md (2026-01-01)\n\n"
            "| path | blob deleted |\n|---|---|\n"
            f"| `BACKLOG.md` | `{earlier}` |\n\n"
            f"Note: the file now being retired was read at `{sha}`.\n"))
        code, out = retire_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertFalse((d / "BACKLOG.md").exists())
        laws = (d / "LAWS.md").read_text(encoding="utf-8")
        self.assertIn(f"| `BACKLOG.md` | `{sha}` |", laws,
                      "no record of THIS blob was written")
        self.assertIn("deletion record is appended", out)

    def test_a_row_already_naming_this_path_and_blob_is_not_duplicated(self):
        """MUST NOT MOVE: the same fact is recorded once, and the
        disposition line says the record was already there."""
        d = build(LIVE_HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        sha = migrate.blob_sha((d / "BACKLOG.md").read_bytes())
        self._laws_with(d, "law\n" + migrate.deletion_record(
            "BACKLOG.md", "ITEMS.md", sha, "2026-01-01"))
        before = (d / "LAWS.md").read_text(encoding="utf-8")
        code, out = retire_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual((d / "LAWS.md").read_text(encoding="utf-8"), before)
        self.assertFalse((d / "BACKLOG.md").exists())
        self.assertNotIn("deletion record is appended", out)
        self.assertIn("already", out.split("DISPOSITION (lc-86):")[1].lower())


if __name__ == "__main__":
    unittest.main()
