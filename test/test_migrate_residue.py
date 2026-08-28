"""lc-65 — migrate books its own detectable residue (design §3.1b at 2b60cab).

The migration converts the carrier and leaves consumers of the OLD one still
pointing at it. Nobody is scheduled to notice: that is the assumed-delivery
class — a write with no committing actor ACCUMULATES, and the only detector
is a count of what piled up. The migration is the one party that knows the
residue exists at the moment it creates it, so it is the party that books it.

ONE CLASS ONLY, and the scope is as load-bearing as the class itself. The
frozen ARCHIVE is not booked here — R22 withdrew every size cap and the
archive's growth is the `done bodies` kind's declared compaction exit, so a
line-count tripwire would both re-add a banned cap and double the retire
lane. The un-decomposed METHOD FILE is not booked here either — no universal
marker exists for a tool to key on, so it rides the file sweep (§4). Three of
these tests assert those two absences, because "books the readers" and "books
everything it can think of" produce the same green on the readers arm alone.

THE OVER-FIRE ARMS ARE HALF THIS FILE. A detector keyed to a name that
appears in the source carrier's own record tails, in every migrated item's
`evidence`, and in the report describing the migration would fire on every
repo it ever runs in — so the exclusions are tested with the mentions
actually present rather than in a repo where nothing says the name at all.
"""

import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits, items  # noqa: E402

from test_migrate import REPORT, build, migrate_run, run_cli  # noqa: E402

#: A source whose OWN body names the carrier — the migration's record tails
#: are spelled exactly this way, so this is the shape every real source has.
SOURCE = ("# old carrier\n\n"
          "## Open\n\n"
          "- **READY 2026-01-01 — the sampler truncates its second pass.** "
          "record: BACKLOG.md:3\n"
          "- **PARKED 2026-01-02 — kerning drifts after a font upgrade.** "
          "record: BACKLOG.md:5\n")


def commit(repo: Path, rel: str, text: str):
    """Write a TRACKED file — tracked is the whole population the detector
    reads, so an uncommitted fixture would test the untracked case by
    accident."""
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"],
                   capture_output=True, text=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", f"add {rel}"],
                   capture_output=True, text=True)
    tracked = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--error-unmatch", rel],
        capture_output=True, text=True)
    assert tracked.returncode == 0, f"fixture not tracked: {rel}"


def tend_items(repo: Path) -> list:
    parsed = items.parse((repo / "ITEMS.md").read_text(encoding="utf-8"))
    return [it for it in parsed.items
            if (it.slots.get("goal") or "").strip() == "tend"]


class ReadersBooked(unittest.TestCase):

    def setUp(self):
        self.repo = build(SOURCE)
        commit(self.repo, "docs/dev-loop.md",
               "The queue lives in BACKLOG.md and is graded weekly.\n")
        commit(self.repo, "tools/banner.mjs",
               "const CARRIER = 'BACKLOG.md';\n")

    def test_exactly_one_parked_tend_item_is_booked(self):
        code, out = migrate_run(self.repo)
        self.assertIn(code, (exits.CLEAN, exits.FINDING), out)
        got = tend_items(self.repo)
        self.assertEqual(len(got), 1, [i.ident for i in got])
        self.assertEqual(got[0].grade, "PARKED", got[0].slots)

    def test_its_blocker_is_the_typed_decision_the_design_names(self):
        migrate_run(self.repo)
        blocker = tend_items(self.repo)[0].slots["blocked-by"].strip()
        self.assertTrue(blocker.startswith("decision "), blocker)
        self.assertIn("every consumer migrated or declared exempt", blocker)

    def test_the_hit_paths_are_in_the_evidence_slot(self):
        migrate_run(self.repo)
        ev = tend_items(self.repo)[0].slots["evidence"]
        self.assertIn("docs/dev-loop.md", ev)
        self.assertIn("tools/banner.mjs", ev)

    def test_no_slot_is_the_UNKNOWN_transitional_marker(self):
        """UNKNOWN is the marker for MIGRATED entries, whose slots nobody
        ever wrote. This item is tool-generated: every slot is real text, or
        the item silently fails the re-grade UNKNOWN exists to force."""
        migrate_run(self.repo)
        slots = tend_items(self.repo)[0].slots
        for name in ("requirement", "goal", "write-set", "done-criterion",
                     "evidence"):
            self.assertNotIn("UNKNOWN", slots[name], name)

    def test_the_produced_carrier_passes_item_check(self):
        """The end-to-end arm, and it is where lc-64 and lc-65 meet: the
        booked goal is `tend` in a repo whose declaration does not list it,
        and a PARKED item without a typed blocker is itself a finding."""
        migrate_run(self.repo)
        code, out = run_cli(self.repo, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)

    def test_the_run_and_the_report_both_say_it_was_booked(self):
        _, out = migrate_run(self.repo)
        self.assertIn("residue", out.lower())
        report = (self.repo / REPORT).read_text(encoding="utf-8")
        self.assertIn("residue", report.lower())
        self.assertIn("docs/dev-loop.md", report)


class TheArithmeticStillHolds(unittest.TestCase):
    """The residue item comes from no source entry, so folding it into the
    source count would break the reconciliation identity on every migration
    after — and the conservation identity would be short by exactly one."""

    def setUp(self):
        self.repo = build(SOURCE)
        commit(self.repo, "docs/dev-loop.md", "see BACKLOG.md\n")

    def test_the_run_does_not_answer_could_not_verify(self):
        code, out = migrate_run(self.repo)
        self.assertNotEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertNotIn("arithmetic disagrees", out)

    def test_the_reconciliation_identity_counts_source_entries_only(self):
        _, out = migrate_run(self.repo)
        self.assertIn("2 read == 2 written + 0 closed + 0 unclassified", out)

    def test_conservation_holds_over_the_produced_carrier(self):
        migrate_run(self.repo)
        code, out = run_cli(self.repo, "item", "check")
        self.assertIn("conservation: CLEAN", out)
        self.assertEqual(code, exits.CLEAN, out)

    def test_the_residue_evidence_is_not_shaped_like_a_source_pointer(self):
        """`per_source_counts` re-reads the homes and counts blocks whose
        `evidence` is exactly `<source>:<n>-<n>` — the merge path's
        independent derivation. An evidence slot that matched that anchor
        would inflate it and answer COULD NOT VERIFY on every merge."""
        migrate_run(self.repo)
        from lifecycle_core.migrate import per_source_counts
        n_items, _ = per_source_counts(
            (self.repo / "ITEMS.md").read_text(encoding="utf-8"), "",
            "BACKLOG.md")
        self.assertEqual(n_items, 2, "the residue item was counted as a "
                                     "source-derived block")


class TheOverFireArms(unittest.TestCase):
    """Every one of these repos CONTAINS the string `BACKLOG.md` — in the
    source's own record tails, in the successor carrier, in the report. A
    detector that skipped the exclusions is green on the class above and
    fires here, in every repo it ever runs in."""

    def test_a_repo_whose_only_mentions_are_the_source_itself_books_nothing(self):
        repo = build(SOURCE)
        code, out = migrate_run(repo)
        self.assertEqual(tend_items(repo), [], "the source carrier's own "
                                               "record tails were read as a "
                                               "consumer of itself")
        self.assertIn(code, (exits.CLEAN, exits.FINDING), out)

    def test_the_successor_carrier_and_report_are_not_readers(self):
        """A SECOND run, after the successor homes and the report have been
        committed: `ITEMS.md` names the old carrier in every migrated item's
        evidence, and the report names it throughout."""
        repo = build(SOURCE)
        migrate_run(repo)
        subprocess.run(["git", "-C", str(repo), "add", "-A"],
                       capture_output=True, text=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "successors"],
                       capture_output=True, text=True)
        self.assertIn("BACKLOG.md",
                      (repo / "ITEMS.md").read_text(encoding="utf-8"),
                      "fixture premise: the successor must name the source")
        migrate_run(repo, "--force")
        self.assertEqual(tend_items(repo), [])

    def test_an_untracked_reader_is_out_of_scope(self):
        repo = build(SOURCE)
        (repo / "scratch.md").write_text("BACKLOG.md\n", encoding="utf-8")
        migrate_run(repo)
        self.assertEqual(tend_items(repo), [], "an untracked file is not a "
                                               "consumer the migration broke")

    def test_a_tracked_file_naming_nothing_relevant_is_not_a_reader(self):
        repo = build(SOURCE)
        commit(repo, "docs/unrelated.md", "the kerning tables drift.\n")
        migrate_run(repo)
        self.assertEqual(tend_items(repo), [])


class TheClassesNotBooked(unittest.TestCase):
    """§3.1b names two candidates that are explicitly NOT migrate's. Asserted
    as absences because a build that booked everything it could think of
    scores identically on the readers arm."""

    def setUp(self):
        self.repo = build(SOURCE)
        commit(self.repo, "docs/dev-loop.md",
               "The method file. The queue is BACKLOG.md.\n")
        # An archive far past any line count anyone might have picked.
        commit(self.repo, "BACKLOG-DONE.md",
               "# old done\n\n## Done\n\n"
               + "".join(f"- **DONE 2026-01-01 — closed {n}.** body\n"
                         for n in range(400)))

    def test_only_one_residue_item_exists_for_all_three_candidates(self):
        migrate_run(self.repo)
        got = tend_items(self.repo)
        self.assertEqual(len(got), 1, [i.slots["requirement"] for i in got])

    def test_no_item_mentions_the_archive_or_a_size_tripwire(self):
        migrate_run(self.repo)
        body = " ".join(v for it in tend_items(self.repo)
                        for v in it.slots.values()).lower()
        for banned in ("archive", "tripwire", "line count", "oversiz"):
            self.assertNotIn(banned, body)

    def test_no_item_mentions_the_method_file(self):
        migrate_run(self.repo)
        body = " ".join(v for it in tend_items(self.repo)
                        for v in it.slots.values()).lower()
        for banned in ("method file", "decompos", "dev-loop.md — "):
            self.assertNotIn(banned, body)


class ReportOnlyWritesNothing(unittest.TestCase):
    """The mode ruling: the residue is written by any carrier-writing run,
    and `--report-only` re-renders its description while touching no
    carrier."""

    def setUp(self):
        self.repo = build(SOURCE)
        commit(self.repo, "docs/dev-loop.md", "see BACKLOG.md\n")

    def test_report_only_over_a_fresh_repo_writes_no_carrier(self):
        code, out = migrate_run(self.repo, "--report-only")
        self.assertFalse((self.repo / "ITEMS.md").exists(), out)

    def test_report_only_still_describes_the_residue(self):
        migrate_run(self.repo, "--report-only")
        report = (self.repo / REPORT).read_text(encoding="utf-8")
        self.assertIn("docs/dev-loop.md", report)


if __name__ == "__main__":
    unittest.main()
