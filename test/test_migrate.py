"""What a CLOSED entry is, on the way in — lc-18, lc-19, lc-21, cf-324.

WHAT THE ROSTER ALREADY COVERS is the refusal: `migration_unclassified` has a
plant, a control and a recorded mutation, and the two AMBIGUOUS shapes added
here report under it. A roster row proves that a finding FIRES; it cannot
prove the states that produce a CLEAN answer, because a row's control only
has to DIFFER from its plant.

So what is here is the other half, and for this lane the other half is the
whole point: **a closure written back into the open carrier produces no
finding at all.** It reopens finished work silently, in a file a human then
reads as the truth.

THE MUST-NOT-MOVE CASES ARE HALF THIS FILE, deliberately. Every case here has
a partner asserting what the change must NOT have done, because without them
a matcher loosened until the closures stop leaking scores identically to one
that got the distinction right:

  * a capitalised NON-grade word mid-title still migrates as ungraded work;
  * `UNDONE` and `DROPPED-BY` are not closure words;
  * a grade word with NO rule is still UNCLASSIFIED, never guessed at;
  * an ungraded entry UNDER the closure heading is CLOSED, not refused — the
    heading already said it, and refusing them would fire on the whole
    measured population (7 root + 1 corpus entry);
  * a re-run over an UNMOVED source still answers.
"""

import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, exits, items, migrate  # noqa: E402
from lifecycle_core.refusals import GOOD_FULL_DECLARATION  # noqa: E402


def build(backlog: str, done: str = "# old done\n\n## Done\n\n"
                                    "- **DONE 2026-01-01 — c.** b\n") -> Path:
    """A repo with an OLD carrier and no successor homes yet."""
    d = Path(tempfile.mkdtemp(prefix="lifecycle-migrate-"))
    run = lambda *a: subprocess.run(a, cwd=str(d), capture_output=True,  # noqa: E731
                                    text=True)
    run("git", "init", "-q", "-b", "main")
    run("git", "config", "core.hooksPath", str(d / ".nohooks"))
    run("git", "config", "user.email", "migrate@lifecycle.invalid")
    run("git", "config", "user.name", "migrate test")
    (d / ".claude").mkdir()
    (d / ".claude" / "lifecycle.json").write_text(
        json.dumps(GOOD_FULL_DECLARATION), encoding="utf-8")
    (d / "LAWS.md").write_text("law\n", encoding="utf-8")
    (d / "LEDGER.md").write_text("schema: 2\n", encoding="utf-8")
    (d / "BACKLOG.md").write_text(backlog, encoding="utf-8")
    (d / "BACKLOG-DONE.md").write_text(done, encoding="utf-8")
    run("git", "add", "-A")
    run("git", "commit", "-qm", "seed")
    return d


REPORT = "docs/audits/report.md"


def run_cli(repo: Path, *argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(["--repo", str(repo)] + list(argv))
    return code, buf.getvalue()


def migrate_run(repo: Path, *extra):
    return run_cli(repo, "migrate", "--report", REPORT, *extra)


def entry(text: str, section: str = "Open") -> migrate.Entry:
    """One classified entry, read through the real reader.

    Through `read_carrier` rather than constructed: the closure-section flag
    is set THERE, and an Entry built by hand would be graded against a field
    this test set itself.
    """
    read = migrate.read_carrier(f"# c\n\n## {section}\n\n{text}\n")
    assert len(read.entries) == 1, read.entries
    migrate.classify(read.entries[0])
    return read.entries[0]


class ClosureVocabulary(unittest.TestCase):
    """lc-19 — the closed grades had NO RULE, so every properly-graded
    closure in a source carrier was UNCLASSIFIED by construction."""

    def test_every_closed_grade_has_a_rule_and_maps_to_itself(self):
        """DERIVED from `items.GRADES_CLOSED`, never from a list here.

        A restated pair beside the vocabulary would stay green the day the
        vocabulary grew — the exact shape that made `DROPPED` ruleless while
        it sat in this plugin's own default grade list.
        """
        self.assertTrue(items.GRADES_CLOSED)
        for word in items.GRADES_CLOSED:
            self.assertIn(word, migrate.RULES, f"{word} has no migration rule")
            self.assertEqual(migrate.RULES[word][0], word)

    def test_a_closure_grade_word_routes_to_the_done_home(self):
        d = build("# old\n\n## Open\n\n"
                  "- **DONE 2026-08-01 (abc1234) — a closure.** body\n"
                  "- **DROPPED 2026-08-02 — overtaken.** body\n"
                  "- **READY 2026-08-03 — real open work.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        live = (d / "ITEMS.md").read_text(encoding="utf-8")
        archive = (d / "ITEMS-DONE.md").read_text(encoding="utf-8")
        self.assertIn("real open work", live)
        self.assertNotIn("a closure", live)
        self.assertNotIn("overtaken", live)
        self.assertIn("- **DONE 2026-08-01 (abc1234) — a closure.** body",
                      archive)
        self.assertIn("- **DROPPED 2026-08-02 — overtaken.** body", archive)

    def test_a_grade_word_with_no_rule_is_still_unclassified(self):
        """MUST NOT MOVE. `ERLEDIGT` and `RESOLVED` are real words in the
        measured carriers and they have no rule. The repair for lc-19 is
        RULES, never a looser matcher — a word nobody mapped must report as
        unclassified rather than be read as a closure because it looks like
        one.

        ASSERTED WITHOUT THE NEW FIELDS, deliberately: this arm has to be
        runnable against the OLD build, where it must ALSO pass. An assertion
        touching `Entry.closure` would raise there instead — and a red that
        is an attribute error proves the code is new, never that the check
        discriminates (law 4).
        """
        for word in ("ERLEDIGT", "RESOLVED", "TRACED", "EXECUTED"):
            e = entry(f"- **{word} 2026-08-01 — x.** body")
            self.assertEqual(e.grade_word, word)
            self.assertIsNone(e.grade, word)
            self.assertIn("no rule", e.unclassified_why)


class ClosureSection(unittest.TestCase):
    """lc-18 — the design modelled closures as a separate FILE while both
    real dotfiles carriers keep theirs as a `## Done` section of the same
    file. Measured: 7 root entries and 1 corpus entry written back as open
    work."""

    def test_entries_under_a_done_section_never_enter_the_open_carrier(self):
        d = build("# old\n\n## Open\n\n"
                  "- **READY 2026-08-03 — real open work.** body\n\n"
                  "## Done (move here with the commit pointer, prune at "
                  "reviews)\n\n"
                  "- **A closed thing, 2026-08-01 (abc1234).** why it closed\n"
                  "- **Another closed thing, 2026-08-02 (def5678).** why\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        live = (d / "ITEMS.md").read_text(encoding="utf-8")
        archive = (d / "ITEMS-DONE.md").read_text(encoding="utf-8")
        self.assertIn("real open work", live)
        self.assertNotIn("A closed thing", live)
        self.assertNotIn("Another closed thing", live)
        self.assertIn("- **A closed thing, 2026-08-01 (abc1234).** "
                      "why it closed", archive)
        self.assertIn("- **Another closed thing, 2026-08-02 (def5678).** why",
                      archive)

    def test_the_heading_matches_on_its_first_word_not_the_whole_line(self):
        """The real heading carries an explanatory tail, exactly as the CUT
        section's does. A whole-line match would find neither."""
        e = entry("- **A closed thing.** body",
                  section="Done (move here with the commit pointer, prune at "
                          "reviews)")
        self.assertTrue(e.in_closure_section)
        self.assertTrue(e.closure)

    def test_an_open_section_is_not_a_closure_section(self):
        """MUST NOT MOVE: ordinary open work still migrates."""
        e = entry("- **A live thing.** body", section="Open")
        self.assertFalse(e.in_closure_section)
        self.assertFalse(e.closure)
        self.assertEqual(e.grade, "NEW")

    def test_a_declared_closure_FILE_does_not_remove_the_default_section(self):
        """The cache-fix shape: `Closure-home: BACKLOG-DONE.md`. The
        declaration ADDS a name; it never subtracts the default one, because
        a carrier declaring a closure file and ALSO keeping a `## Done`
        section is exactly the state in which reading that section as open
        work is the defect."""
        names, why = migrate.closure_sections_for(
            "# c\n\nClosure-home: BACKLOG-DONE.md\n\n## Open\n")
        self.assertEqual(names, ("Done",))
        self.assertIn("BACKLOG-DONE.md", why)
        self.assertIn("FILE", why)

    def test_a_declared_closure_SECTION_is_read_by_its_first_word(self):
        names, why = migrate.closure_sections_for(
            "# c\n\nClosure-home: ## Erledigt (mit Commit-Zeiger)\n")
        self.assertIn("Erledigt", names)
        self.assertIn("Done", names)
        self.assertIn("SECTION", why)

    def test_the_declaration_is_read_at_column_zero_only(self):
        """Both dotfiles carriers DISCUSS the phrase inside indented item
        bodies. A search that matched those would read an item's prose as a
        declaration — a predicate firing on legitimate work."""
        names, why = migrate.closure_sections_for(
            "# c\n\n- **READY — a repo with no\n"
            "  `Closure-home:` declaration keeps a `## Done` section.** b\n")
        self.assertEqual(names, ("Done",))
        self.assertIn("declares no `Closure-home:`", why)

    def test_the_basis_travels_with_the_read(self):
        """"No entry sat under a closure heading" and "this run looked under
        a heading this carrier does not use" both produce a zero, so the
        heading and its basis are carried rather than inferred."""
        read = migrate.read_carrier("# c\n\n## Open\n\n- **x.** b\n")
        self.assertEqual(read.closure_sections, ("Done",))
        self.assertTrue(read.closure_sections_why)


class AmbiguousEntries(unittest.TestCase):
    """lc-21 and the open-graded-under-Done case. Both REFUSE: never a
    silent NEW, never a silent DONE."""

    def test_a_closure_word_mid_title_refuses(self):
        e = entry("- **The statusline drift check — DONE 2026-08-01 "
                  "(abc1234).** body")
        self.assertIsNone(e.grade_word)
        self.assertIsNone(e.grade)
        self.assertFalse(e.closure)
        self.assertIn("AMBIGUOUS", e.unclassified_why)
        self.assertIn("DONE", e.unclassified_why)

    def test_a_capitalised_non_grade_word_mid_title_is_still_ungraded(self):
        """THE OVER-FIRE ARM, and it is what decides whether this is
        shippable at all. Without it a matcher loosened until the counts
        improve scores identically to one that got the distinction right.

        ASSERTED WITHOUT THE NEW FIELDS so it runs — and PASSES — against the
        OLD build too, which is what makes it a must-not-move control rather
        than an attribute error wearing a red's clothes. `grade == "NEW"`
        settles it on its own: a closure carries `grade is None`.
        """
        for title in (
            "The retirement sweep — TODO before the next review",
            "The API surface — REVIEW it after the wave",
            "A note about the WIP series",
            "The check is UNDONE and needs a second pass",
            "Superseded by cf-9, DROPPED-BY that entry's own close",
            "A DONELIKE word that merely starts the same way",
        ):
            e = entry(f"- **{title}.** body")
            self.assertIsNone(e.grade_word, title)
            self.assertEqual(e.grade, "NEW", title)
            self.assertEqual(e.unclassified_why, "", title)

    def test_an_open_grade_word_under_the_closure_heading_refuses(self):
        e = entry("- **READY 2026-08-01 — an open grade under Done.** b",
                  section="Done")
        self.assertEqual(e.grade_word, "READY")
        self.assertIsNone(e.grade)
        self.assertFalse(e.closure)
        self.assertIn("AMBIGUOUS", e.unclassified_why)

    def test_an_ungraded_entry_under_the_closure_heading_is_closed(self):
        """MUST NOT MOVE — the PRECEDENCE case, and the whole measured
        population sits in it. Those entries carry no grade word precisely
        because the heading already said it; scanning the title first would
        refuse all eight as ambiguous, which is a guard firing on legitimate
        work."""
        e = entry("- **A closed thing — DONE 2026-08-01 (abc1234).** why",
                  section="Done")
        self.assertTrue(e.closure)
        self.assertEqual(e.unclassified_why, "")

    def test_a_closure_grade_word_under_the_closure_heading_is_closed(self):
        e = entry("- **DONE 2026-08-01 — agreeing with its heading.** b",
                  section="Done")
        self.assertTrue(e.closure)
        self.assertEqual(e.unclassified_why, "")

    def test_the_title_is_scanned_PAST_the_requirement_cap(self):
        """The scan runs over the UNCAPPED headline. A pattern run over a
        capped one is a search over a partial view of its own subject, and a
        closure word past the cap would return exactly what a title with no
        closure word returns."""
        pad = "x" * (migrate.REQUIREMENT_CAP + 40)
        e = entry(f"- **{pad} — DONE 2026-08-01.** body")
        self.assertGreater(len(migrate.headline_of(e)),
                           migrate.REQUIREMENT_CAP)
        self.assertLessEqual(len(migrate.title_of(e)),
                             migrate.REQUIREMENT_CAP)
        self.assertIn("AMBIGUOUS", e.unclassified_why)

    def test_the_ambiguity_branch_has_its_own_roster_row(self):
        """lc-17 lane B — the row lane A could not add, and what unblocks
        lc-30.

        WITHOUT IT the ambiguity branch is proven by nothing. Both shapes
        above surface under `migration_unclassified`, whose own plant is the
        NO-RULE word — so disabling the closure-word scan changed no verdict
        at all, and `prove-rows` reported FAILED rather than a proof
        (measured on a copy of HEAD: `rows changed: NONE`).

        ASSERTED OVER THE ROSTER'S OWN DECLARATION, never over a list here: a
        restated family would stay green the day the row was deleted, which
        is the deletion this test exists to make loud.
        """
        from lifecycle_core import refusals

        rows = {r.ident: r for r in refusals.ROWS}
        self.assertIn("migration_ambiguous_closure", rows)
        row = rows["migration_ambiguous_closure"]
        # ONE REFUSAL, TWO FIRING INPUTS — the family is what lets a mutation
        # at the ambiguity branch darken this row without reading as a stray.
        self.assertEqual(row.expected_finding_row, "migration_unclassified")
        self.assertIn("migration_unclassified", rows)

    def test_the_ambiguous_row_text_covers_BOTH_shapes_the_code_routes(self):
        """The row's TEXT is what the operator is handed as the cause, and a
        text narrower than what the code routes through it names the wrong
        one — lc-30's asymmetry, in this row's own words.

        THE TWO SHAPES ARE READ FROM THE CODE, by exercising the reader, not
        from a list restated here: an expectation derived from the row it
        grades moves with the row and stays green on the corruption it exists
        to catch.
        """
        from lifecycle_core import refusals

        row = {r.ident: r for r in refusals.ROWS}["migration_ambiguous_closure"]
        mid_title = entry("- **A thing — DONE 2026-08-01 (abc1234).** body")
        open_under_done = entry(
            "- **READY 2026-08-01 — an open grade under Done.** b",
            section="Done")
        for e in (mid_title, open_under_done):
            self.assertIn("AMBIGUOUS", e.unclassified_why)
        # Both shapes are routed, so the row's text names both: the closure
        # word standing alone later in an ungraded title, and an OPEN grade
        # word under the closure heading.
        # LOWERCASED before matching: the row's prose emphasises words in
        # caps, and a case-sensitive phrase test would go red on an edit that
        # changed nothing about what the text covers.
        text = row.refusal
        low = text.lower()
        self.assertIn("later in the title", low)
        self.assertIn("closure heading", low)
        for word in items.GRADES_CLOSED:
            self.assertIn(word, text, f"{word} is a routed closure word")

    def test_the_run_quotes_the_refused_entry_and_the_report_does_not(self):
        """The desk needs to see WHICH entry it is being asked about. The
        report is generated into a tree that may be public and says of
        itself that it describes entries rather than quoting them — so the
        quote is in the run's own output and the report carries the line,
        the word and the reason."""
        d = build("# old\n\n## Open\n\n"
                  "- **The statusline drift check — DONE 2026-08-01.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[migration_unclassified]", out)
        self.assertIn("The statusline drift check", out)
        report = (d / REPORT).read_text(encoding="utf-8")
        self.assertNotIn("The statusline drift check", report)
        self.assertIn("AMBIGUOUS", report)
        self.assertIn("BACKLOG.md:5", report)


class SourceBlob(unittest.TestCase):
    """cf-324 — three `BACKLOG.md` blobs in one afternoon, and nothing in
    the tool noticed a source moving under it."""

    def test_the_blob_sha_is_gits_own(self):
        """The DEFINITION, not our own reasoning about it. A sha printed in
        a report is useful only if the operator can reproduce it, and
        `git hash-object` is what they will run."""
        d = Path(tempfile.mkdtemp(prefix="lifecycle-blob-"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        for payload in (b"", b"hello\n", "über\r\nzeilen\n".encode("utf-8")):
            p = d / "f"
            p.write_bytes(payload)
            r = subprocess.run(["git", "hash-object", str(p)],
                               capture_output=True, text=True, cwd=str(d))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(migrate.blob_sha(payload), r.stdout.strip())

    def test_a_rerun_over_a_moved_source_could_not_verify(self):
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        (d / "BACKLOG.md").write_text(
            "# old\n\n## Open\n\n- **READY 2026-08-03 — DIFFERENT.** body\n",
            encoding="utf-8")
        code, out = migrate_run(d, "--force")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("has MOVED", out)
        self.assertNotIn("DIFFERENT",
                         (d / "ITEMS.md").read_text(encoding="utf-8"))

    def test_a_moved_closure_home_could_not_verify_too(self):
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        (d / "BACKLOG-DONE.md").write_text(
            "# old done\n\n## Done\n\n- **DONE 2026-01-02 — moved.** b\n",
            encoding="utf-8")
        code, out = migrate_run(d, "--force")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("closure home", out)

    def test_a_rerun_over_an_unmoved_source_still_answers(self):
        """MUST NOT MOVE. A pin that refused every re-run would be
        indistinguishable from one that works, and `--report-only` — whose
        whole job is re-rendering over the same source — would be dead."""
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        code, out = migrate_run(d, "--report-only")
        self.assertEqual(code, exits.CLEAN, out)
        code, out = migrate_run(d, "--force")
        self.assertEqual(code, exits.CLEAN, out)

    def test_a_report_with_no_recorded_blob_is_not_a_mismatch(self):
        """A report written by an earlier build carries no blob line. An
        absent record is an UNPINNED run, not a moved source — treating the
        two the same would refuse every repo whose report predates this
        check."""
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "docs" / "audits").mkdir(parents=True)
        (d / REPORT).write_text("# an older report, no blob line\n",
                                encoding="utf-8")
        code, out = migrate_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("source-blob: ",
                      (d / REPORT).read_text(encoding="utf-8"))

    def test_the_recorded_line_is_what_the_next_run_resolves(self):
        """The pin is a POINTER a later run must resolve, so it is at column
        zero and machine-readable rather than inside a sentence."""
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        report = (d / REPORT).read_text(encoding="utf-8")
        m = migrate._RECORDED_SOURCE_BLOB.search(report)
        self.assertIsNotNone(m, report[:800])
        self.assertEqual(
            m.group(1),
            migrate.blob_sha((d / "BACKLOG.md").read_bytes()))


class ReconciliationWithThreeColumns(unittest.TestCase):
    """The identity that makes 'not migrated' visible now has THREE columns.
    A closure is neither written nor unclassified, and folding it into
    either would make one of those numbers say something it does not."""

    def test_the_identity_holds_and_is_printed_with_three_terms(self):
        d = build("# old\n\n## Open\n\n"
                  "- **READY 2026-08-03 — open.** body\n"
                  "- **DONE 2026-08-01 — closed.** body\n"
                  "- **FLURB 2026-08-02 — no rule covers this.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("3 read == 1 written + 1 closed + 1 unclassified", out)
        report = (d / REPORT).read_text(encoding="utf-8")
        self.assertIn("3 entries read = 1 written + 1 closed + "
                      "1 unclassified — HOLDS", report)

    def test_conservation_counts_the_in_carrier_closures(self):
        """Both sides use `archive_entries` over the text actually written,
        so the identity holds by construction rather than by a coincidence
        between two notions of an entry."""
        d = build("# old\n\n## Open\n\n"
                  "- **READY 2026-08-03 — open.** body\n"
                  "- **DONE 2026-08-01 — closed.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        report = (d / REPORT).read_text(encoding="utf-8")
        self.assertIn("Conservation (§3.1)", report)
        self.assertNotIn("FAILS", report)

    def test_the_closure_zero_is_stated_explicitly(self):
        """An omitted line reads as "checked and clean" whichever of the two
        it was — the could-not-verify failure the three-answers rule
        forbids."""
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — open.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        report = (d / REPORT).read_text(encoding="utf-8")
        self.assertIn("## Closures routed to the done home", report)
        self.assertIn("**None — zero.**", report)
        self.assertIn("`## Done`", report)


if __name__ == "__main__":
    unittest.main()
