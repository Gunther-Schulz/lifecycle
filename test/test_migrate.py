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

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, declaration as decl  # noqa: E402
from lifecycle_core import exits, items, ledger, migrate  # noqa: E402
from lifecycle_core.refusals import GOOD_FULL_DECLARATION  # noqa: E402


def build(backlog: str, done: str = "# old done\n\n## Done\n\n"
                                    "- **DONE 2026-01-01 — c.** b\n",
          declaration: dict | None = None) -> Path:
    """A repo with an OLD carrier and no successor homes yet.

    `declaration` overrides the whole document, so a test can seed a repo
    whose declaration differs in ONE key and nothing else — the pair that
    separates "the key is honoured" from "the build changed something else".
    """
    d = Path(tempfile.mkdtemp(prefix="lifecycle-migrate-"))
    run = lambda *a: subprocess.run(a, cwd=str(d), capture_output=True,  # noqa: E731
                                    text=True)
    run("git", "init", "-q", "-b", "main")
    run("git", "config", "core.hooksPath", str(d / ".nohooks"))
    run("git", "config", "user.email", "migrate@lifecycle.invalid")
    run("git", "config", "user.name", "migrate test")
    (d / ".claude").mkdir()
    (d / ".claude" / "lifecycle.json").write_text(
        json.dumps(GOOD_FULL_DECLARATION if declaration is None
                   else declaration), encoding="utf-8")
    (d / "LAWS.md").write_text("law\n", encoding="utf-8")
    (d / "LEDGER.md").write_text("schema: 2\n", encoding="utf-8")
    (d / "BACKLOG.md").write_text(backlog, encoding="utf-8")
    (d / "BACKLOG-DONE.md").write_text(done, encoding="utf-8")
    run("git", "add", "-A")
    run("git", "commit", "-qm", "seed")
    return d


def commit_all(d: Path, message: str) -> None:
    """Commit whatever is in a fixture repo's tree.

    A verb that RECORDS a move reports `move_uncommitted` when the homes are
    untracked, and that finding reads exactly like a finding about the thing
    under test. Arranging it away is what keeps a red attributable.
    """
    run = lambda *a: subprocess.run(a, cwd=str(d), capture_output=True,  # noqa: E731
                                    text=True)
    run("git", "add", "-A")
    run("git", "commit", "-qm", message)


REPORT = "docs/audits/report.md"


def run_cli(repo: Path, *argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(["--repo", str(repo)] + list(argv))
    return code, buf.getvalue()


def migrate_run(repo: Path, *extra):
    return run_cli(repo, "migrate", "--report", REPORT, *extra)


def entry(text: str, section: str = "Open",
          closure_words: dict | None = None) -> migrate.Entry:
    """One classified entry, read through the real reader.

    Through `read_carrier` rather than constructed: the closure-section flag
    is set THERE, and an Entry built by hand would be graded against a field
    this test set itself.
    """
    read = migrate.read_carrier(f"# c\n\n## {section}\n\n{text}\n")
    assert len(read.entries) == 1, read.entries
    migrate.classify(read.entries[0], closure_words)
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


class DateLedClosureBullets(unittest.TestCase):
    """lc-72 — the entry test at `read_carrier` was `bold OR grade-word-led`,
    so a DATE-LED closure line ("- 2026-08-23 — **title**: body", the
    operator corpus's own closure idiom) is neither and fell to
    `non_entry_bullets` UNCONDITIONALLY — the `in_closure_section`
    disposition below it, which would have closed it verbatim, was never
    reached. Measured on statiker's real migration: 25 of 25 `## Done`
    bodies, all this shape, excluded from the archive."""

    def test_a_date_led_closure_bullet_routes_to_the_done_home(self):
        d = build("# old\n\n## Open\n\n"
                  "- **READY 2026-08-03 — real open work.** body\n\n"
                  "## Done\n\n"
                  "- 2026-08-23 — **next-run staging (STOP after the "
                  "record gate) DROPPED, overtaken:** its premise was "
                  "resuming the canonical-market-identity tracker.\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        live = (d / "ITEMS.md").read_text(encoding="utf-8")
        archive = (d / "ITEMS-DONE.md").read_text(encoding="utf-8")
        self.assertIn("real open work", live)
        self.assertNotIn("next-run staging", live)
        self.assertIn(
            "- 2026-08-23 — **next-run staging (STOP after the record "
            "gate) DROPPED, overtaken:** its premise was resuming the "
            "canonical-market-identity tracker.",
            archive)
        report = (d / REPORT).read_text(encoding="utf-8")
        self.assertIn("Bullet identity:", report)
        self.assertIn("Identity:", report)
        self.assertNotIn("FAILS", report)

    def test_a_date_led_bullet_outside_a_closure_section_stays_prose(self):
        """The discriminating pair for the test above: admission depends on
        the SECTION already having said "closed", not on the text's shape
        alone — the same section-before-title precedence `classify` already
        applies, moved to where admission itself is decided."""
        read = migrate.read_carrier(
            "# c\n\n## Open\n\n"
            "- 2026-08-23 — a build note, not an entry.\n")
        self.assertEqual(read.entries, [])
        self.assertEqual(len(read.non_entry_bullets), 1)
        self.assertEqual(read.non_entry_bullets[0][1], "Open")

    def test_an_open_grade_word_under_the_closure_heading_still_refuses(self):
        """Pin against regression: this lane's widening touches only the
        NOT-bold-and-NOT-grade-word branch of `read_carrier`. A bullet that
        already carries a grade word — open or closed — never reaches the
        new date-led check at all, and `classify`'s existing AMBIGUOUS
        branch for an open grade word under a closure heading is
        untouched."""
        e = entry("- **PARKED 2026-08-23 — waiting on evidence.** b",
                  section="Done")
        self.assertEqual(e.grade_word, "PARKED")
        self.assertIsNone(e.grade)
        self.assertFalse(e.closure)
        self.assertIn("AMBIGUOUS", e.unclassified_why)


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
        # THE LINE IS RESOLVED, NEVER RESTATED (lc-86). This assertion carried
        # a hardcoded `BACKLOG.md:5` and the freeze made it stale — the banner
        # moves every line, so the number the report prints is the BANNERED
        # file's. A restated number would have to be edited every time the
        # banner's height changes, and each edit is a chance to write down
        # what the tool does rather than what is true. So the report's own
        # number is read back and RESOLVED against the file the run left on
        # disk, which is the property that actually matters.
        m = re.search(r"`BACKLOG\.md:(\d+)`", report)
        self.assertIsNotNone(m, report[:400])
        cited = (d / "BACKLOG.md").read_text(
            encoding="utf-8").split("\n")[int(m.group(1)) - 1]
        self.assertIn("The statusline drift check", cited)


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
    """The identity that makes 'not migrated' visible now has FOUR columns.
    A closure is neither written nor unclassified, and folding it into
    either would make one of those numbers say something it does not; a
    RE-IMPORT (lc-73) is the fourth, for the same reason — an entry that
    simply vanished from the sum and one that was deliberately not written
    look identical in a three-column identity."""

    def test_the_identity_holds_and_is_printed_with_four_terms(self):
        d = build("# old\n\n## Open\n\n"
                  "- **READY 2026-08-03 — open.** body\n"
                  "- **DONE 2026-08-01 — closed.** body\n"
                  "- **FLURB 2026-08-02 — no rule covers this.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("3 read == 1 written + 1 closed + 1 unclassified "
                      "+ 0 re-imported", out)
        report = (d / REPORT).read_text(encoding="utf-8")
        self.assertIn("3 entries read = 1 written + 1 closed + "
                      "1 unclassified + 0 re-imported — HOLDS", report)

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


MERGE_SOURCE_B = ("# second\n\n## Open\n\n"
                  "- **READY 2026-09-01 — the second carrier's work.** body\n")


def items_with(*idents) -> str:
    """A live carrier carrying exactly these ids, in this order.

    The HOLE the merge test needs is constructed here rather than waited for:
    `compacted` is 0 in every carrier this build has produced, so the id space
    is contiguous today. It will not stay that way — a compacted id leaves
    BOTH homes and the conservation identity subtracts it, so the hole is the
    state compaction creates and this fixture is what guards against it.
    """
    head = (f"schema: {items.SCHEMA_FLOOR}\nbaseline: {len(idents)}\n"
            "added: 0\ncompacted: 0\n")
    blocks = [items.render_block(i, {
        "grade": "NEW",
        "requirement": f"a body already in the carrier as {i}",
        "goal": "UNKNOWN", "write-set": "UNKNOWN",
        "done-criterion": "UNKNOWN", "evidence": "none yet",
        "blocked-by": "decision regrade: what this needs",
    }) for i in idents]
    return head + "\n" + "\n".join(blocks)


class MergeMode(unittest.TestCase):
    """lc-17 — 'N old carriers into one item carrier' had no execution path
    at all: with `ITEMS.md` present, migrate answered
    `FINDING [migrate_would_overwrite]` and the refusal's own text offered
    `--force`, which REPLACES real work with a re-derivation."""

    def prefix(self) -> str:
        return GOOD_FULL_DECLARATION["id-prefix"]

    def test_without_merge_the_overwrite_refusal_is_byte_for_byte_what_it_was(self):
        """THE POINT OF THE FLAG, and the arm that would catch it changing.

        `--from-done NONE` is present deliberately: without a closure home on
        disk the run dies EARLIER at COULD NOT VERIFY, and a test that never
        reaches `migrate_would_overwrite` pins nothing while looking green.
        """
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        before = (d / "ITEMS.md").read_text(encoding="utf-8")
        code, out = migrate_run(d, "--from", "BACKLOG.md",
                                "--from-done", "NONE")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn(
            "FINDING [migrate_would_overwrite] ITEMS.md already exists. "
            "Refusing to overwrite a carrier: this is a DRY RUN that PRODUCES "
            "the successor files, and a second run over a carrier already in "
            "use would replace real work with a re-derivation of the old one. "
            "Pass `--force` if that is what is wanted.", out)
        self.assertEqual((d / "ITEMS.md").read_text(encoding="utf-8"), before)

    def test_two_sources_migrate_into_one_carrier(self):
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        before = (d / "ITEMS.md").read_text(encoding="utf-8")
        (d / "SECOND.md").write_text(MERGE_SOURCE_B, encoding="utf-8")
        code, out = migrate_run(d, "--from", "SECOND.md",
                                "--from-done", "NONE", "--merge")
        self.assertEqual(code, exits.CLEAN, out)
        after = (d / "ITEMS.md").read_text(encoding="utf-8")
        # THE EXISTING ENTRY IS UNTOUCHED — not renumbered, not re-derived.
        # Asserted as a PREFIX of the new file rather than by hunting for its
        # id: a merge that rewrote a slot would still leave the id there.
        first_block = before.split("\n", 5)[5]
        self.assertIn(first_block.rstrip("\n"), after)
        self.assertIn("the second carrier's work", after)
        self.assertIn("first", after)
        parsed = items.parse(after)
        self.assertEqual([it.ident for it in parsed.items],
                         [f"{self.prefix()}-1", f"{self.prefix()}-2"])
        self.assertEqual(parsed.problems, [])

    def test_a_merge_into_a_carrier_with_an_id_HOLE_skips_the_hole_only(self):
        """THE ALLOCATION SHAPE, which is what `next_ident` PER ENTRY buys.

        `next_ident` returns the LOWEST unused n. Called once and incremented
        from, a merge into {1,2,4} writes 3, 4, 5 — re-issuing the live 4, and
        the collision surfaces as a DUPLICATE finding months later in a file
        nobody was editing. Called per entry it writes 3, 5, 6.

        THE HOLE IS THE STATE COMPACTION CREATES: `compacted` is a head field
        and the conservation identity SUBTRACTS it, so a compacted id is gone
        from BOTH homes and `next_ident` cannot see it. Today every carrier
        has `compacted: 0`, which is why the fixture constructs the hole.
        """
        p = self.prefix()
        d = build("# old\n\n## Open\n\n"
                  "- **READY 2026-09-01 — merged one.** body\n"
                  "- **READY 2026-09-02 — merged two.** body\n"
                  "- **READY 2026-09-03 — merged three.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "ITEMS.md").write_text(
            items_with(f"{p}-1", f"{p}-2", f"{p}-4"), encoding="utf-8")
        (d / "ITEMS-DONE.md").write_text(f"schema: {items.SCHEMA_FLOOR}\n",
                                         encoding="utf-8")
        code, out = migrate_run(d, "--from", "BACKLOG.md",
                                "--from-done", "NONE", "--merge")
        self.assertEqual(code, exits.CLEAN, out)
        parsed = items.parse((d / "ITEMS.md").read_text(encoding="utf-8"))
        self.assertEqual([it.ident for it in parsed.items],
                         [f"{p}-1", f"{p}-2", f"{p}-4",
                          f"{p}-3", f"{p}-5", f"{p}-6"])
        # The id that would have collided under once-then-increment.
        self.assertEqual(parsed.problems, [])

    def test_a_merge_does_not_re_issue_an_id_THE_RECORD_holds(self):
        """lc-148 at the THIRD call site, the one a fix for `item add` alone
        would have left silent.

        The hole above is CONSTRUCTED in the carrier; this one is the hole as
        compaction really leaves it — the body gone from both homes and the
        ledger's decision line the only place the id survives. An allocator
        reading the two carriers finds `-3` free and mints it, which is the
        same defect `item add` had, through the same function.
        """
        from lifecycle_core import ledger as ledger_mod
        from lifecycle_core import retire as retire_mod

        p = self.prefix()
        d = build("# old\n\n## Open\n\n"
                  "- **READY 2026-09-01 — merged one.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "ITEMS.md").write_text(items_with(f"{p}-1", f"{p}-2"),
                                    encoding="utf-8")
        (d / "ITEMS-DONE.md").write_text(f"schema: {items.SCHEMA_FLOOR}\n",
                                         encoding="utf-8")
        line = ledger_mod.render(
            "decision",
            {"question": retire_mod.compaction_question(f"{p}-3"),
             "answer": f"ITEMS-DONE.md at blob {'0' * 40}"})
        with open(d / "LEDGER.md", "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        self.assertIsNotNone(
            ledger_mod.parse_line(line),
            "the fixture's record is a line the ledger's own parser cannot "
            "read, so this arm grades a hole nothing could have seen")

        code, out = migrate_run(d, "--from", "BACKLOG.md",
                                "--from-done", "NONE", "--merge")
        # THE RUN ANSWERS `FINDING`, AND NOT FOR THIS ARM'S SUBJECT. Every
        # repo that has ever compacted has a ledger line, and the migration's
        # `migration_ledger_nonzero` check counts the ledger's lines AFTER the
        # run rather than the lines the run routed — so it fires on a ledger
        # that was already there. That is stated here rather than worked
        # around, because a fixture chosen to dodge it would have had no
        # compaction record and this arm would grade nothing. The allocation
        # is what is under test and it is read off the carrier.
        self.assertIn("[migration_ledger_nonzero]", out)
        self.assertNotIn("[migration_unclassified]", out)
        self.assertEqual(code, exits.FINDING, out)
        parsed = items.parse((d / "ITEMS.md").read_text(encoding="utf-8"))
        self.assertEqual([it.ident for it in parsed.items],
                         [f"{p}-1", f"{p}-2", f"{p}-4"])
        self.assertEqual(parsed.problems, [])

    def test_a_duplicate_entry_body_refuses_and_writes_nothing(self):
        """RED-FIRST is the roster's job (`merge_duplicate_body` has a plant
        and a control); what is asserted here is the half a row cannot reach —
        that NOTHING was written, which is what makes the refusal safe on a
        mode that appends."""
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        before = (d / "ITEMS.md").read_text(encoding="utf-8")
        (d / "SECOND.md").write_text(
            "# second\n\n## Open\n\n"
            "- **READY 2026-08-03 — first.** a different body, same "
            "headline\n"
            "- **READY 2026-09-09 — genuinely new work.** body\n",
            encoding="utf-8")
        code, out = migrate_run(d, "--from", "SECOND.md",
                                "--from-done", "NONE", "--merge")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[merge_duplicate_body]", out)
        self.assertIn("already present as", out)
        # THE WHOLE RUN REFUSED: the second, genuinely new entry is absent
        # too. A merge is not idempotent, so a partial append is the shape
        # that corrupts.
        after = (d / "ITEMS.md").read_text(encoding="utf-8")
        self.assertEqual(after, before)
        self.assertNotIn("genuinely new work", after)

    def test_a_source_that_repeats_its_own_headline_refuses_and_writes_nothing(self):
        """An empty successor makes this the source-self route, not homes."""
        d = build("# old\n\n## Open\n\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        before = (d / "ITEMS.md").read_text(encoding="utf-8")
        (d / "SECOND.md").write_text(
            "# second\n\n## Open\n\n"
            "- **READY 2026-08-03 — repeated source work.** first body\n"
            "- **READY 2026-08-03 — repeated source work.** second body\n"
            "- **READY 2026-09-10 — genuinely new work.** body\n",
            encoding="utf-8")
        code, out = migrate_run(d, "--from", "SECOND.md",
                                "--from-done", "NONE", "--merge")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[merge_source_self_duplicate]", out)
        after = (d / "ITEMS.md").read_text(encoding="utf-8")
        self.assertEqual(after, before)
        self.assertNotIn("genuinely new work", after)

    def test_a_headline_that_merely_resembles_one_present_still_merges(self):
        """MUST NOT MOVE. Without this arm a duplicate check loosened until
        the collisions stop scores identically to one that got the
        distinction right — and a guard firing on legitimate work stops the
        lane (R11)."""
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        (d / "SECOND.md").write_text(
            "# second\n\n## Open\n\n"
            "- **READY 2026-08-03 — first thing, longer.** body\n",
            encoding="utf-8")
        code, out = migrate_run(d, "--from", "SECOND.md",
                                "--from-done", "NONE", "--merge")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("first thing, longer",
                      (d / "ITEMS.md").read_text(encoding="utf-8"))

    def test_a_body_already_CLOSED_is_a_duplicate_too(self):
        """The silent half: a closure merged back in as open work lands
        looking exactly like work nobody has started, with the closure that
        answered it one file away."""
        p = self.prefix()
        d = build("# old\n\n## Open\n\n- **READY 2026-09-09 — a closed "
                  "thing.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "ITEMS.md").write_text(items_with(f"{p}-1"), encoding="utf-8")
        (d / "ITEMS-DONE.md").write_text(
            f"schema: {items.SCHEMA_FLOOR}\n\n"
            + items.render_block(f"{p}-2", {
                "grade": "DONE",
                "requirement": "READY 2026-09-09 — a closed thing",
                "goal": "UNKNOWN", "write-set": "UNKNOWN",
                "done-criterion": "UNKNOWN", "evidence": "none",
                "blocked-by": "NONE"}), encoding="utf-8")
        code, out = migrate_run(d, "--from", "BACKLOG.md",
                                "--from-done", "NONE", "--merge")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[merge_duplicate_body]", out)
        self.assertIn(f"{p}-2", out)

    def test_an_absent_items_md_under_merge_is_an_ordinary_first_migration(self):
        """NOT an error — stated in the flag's own help text. A merge into
        nothing is the first migration, and refusing it would make the flag
        unusable as the standing way to bring carriers in."""
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertFalse((d / "ITEMS.md").exists())
        code, out = migrate_run(d, "--from", "BACKLOG.md", "--merge")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("first", (d / "ITEMS.md").read_text(encoding="utf-8"))

    def test_an_empty_items_md_under_merge_is_not_an_error_either(self):
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "ITEMS.md").write_text(
            f"schema: {items.SCHEMA_FLOOR}\nbaseline: 0\nadded: 0\n"
            "compacted: 0\n", encoding="utf-8")
        (d / "ITEMS-DONE.md").write_text(f"schema: {items.SCHEMA_FLOOR}\n",
                                         encoding="utf-8")
        code, out = migrate_run(d, "--from", "BACKLOG.md",
                                "--from-done", "NONE", "--merge")
        self.assertEqual(code, exits.CLEAN, out)
        parsed = items.parse((d / "ITEMS.md").read_text(encoding="utf-8"))
        self.assertEqual([it.ident for it in parsed.items],
                         [f"{self.prefix()}-1"])

    def test_conservation_holds_per_source_and_in_total_after_a_merge(self):
        d = build("# old\n\n## Open\n\n"
                  "- **READY 2026-08-03 — first.** body\n"
                  "- **DONE 2026-08-04 — already closed.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        (d / "SECOND.md").write_text(
            "# second\n\n## Open\n\n"
            "- **READY 2026-09-01 — second open.** body\n"
            "- **DROPPED 2026-09-02 — second closed.** body\n",
            encoding="utf-8")
        code, out = migrate_run(d, "--from", "SECOND.md",
                                "--from-done", "NONE", "--merge")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("conservation, THIS SOURCE (SECOND.md)", out)
        self.assertIn("blocks whose `evidence` names it: 1", out)
        self.assertIn("archive markers naming it:        1", out)
        self.assertIn("conservation: CLEAN", out)
        self.assertNotIn("conservation_short", out)
        self.assertNotIn("conservation_surplus", out)

    def test_the_per_source_figures_are_re_read_not_handed_over(self):
        """LAW 22's second half. A count the writing loop hands the checker is
        exact by construction and cannot fail, so the figures are derived from
        the artifacts: `per_source_counts` reads the files and knows nothing
        about the run that produced them."""
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        n_items, n_closures = migrate.per_source_counts(
            (d / "ITEMS.md").read_text(encoding="utf-8"),
            (d / "ITEMS-DONE.md").read_text(encoding="utf-8"),
            "BACKLOG.md")
        self.assertEqual((n_items, n_closures), (1, 0))
        # A source that contributed nothing reads as zero rather than as the
        # whole file: the count is KEYED on the path.
        self.assertEqual(migrate.per_source_counts(
            (d / "ITEMS.md").read_text(encoding="utf-8"),
            (d / "ITEMS-DONE.md").read_text(encoding="utf-8"),
            "NOTHING.md"), (0, 0))

    def test_the_evidence_key_anchors_its_terminator(self):
        """MUST NOT MOVE. `BACKLOG.md` must not count `BACKLOG.md.bak`'s
        blocks — a prefix test over a rendered slot is an equality's
        costume."""
        text = (f"schema: {items.SCHEMA_FLOOR}\nbaseline: 1\nadded: 0\n"
                "compacted: 0\n\n"
                + items.render_block("xx-1", {
                    "grade": "NEW", "requirement": "r", "goal": "UNKNOWN",
                    "write-set": "UNKNOWN", "done-criterion": "UNKNOWN",
                    "evidence": "BACKLOG.md.bak:5-6",
                    "blocked-by": "NONE"}))
        self.assertEqual(migrate.per_source_counts(text, "", "BACKLOG.md"),
                         (0, 0))
        self.assertEqual(migrate.per_source_counts(text, "",
                                                   "BACKLOG.md.bak"), (1, 0))


class PerSourceBlobPin(unittest.TestCase):
    """lc-17 §F — the pin was single-source by SHAPE: `source_moved` took the
    FIRST recorded line and measured every source against it, so a merge's
    second carrier compared its own bytes to the first carrier's sha."""

    def test_a_second_source_is_a_first_migration_for_itself(self):
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        (d / "SECOND.md").write_text(MERGE_SOURCE_B, encoding="utf-8")
        code, out = migrate_run(d, "--from", "SECOND.md",
                                "--from-done", "NONE", "--merge")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("has MOVED", out)

    def test_both_sources_stay_recorded_in_the_regenerated_report(self):
        """The report is REGENERATED every run. A merge that wrote only its
        own line would drop the first carrier's pin, and the next run over it
        would read that absence as a first migration — un-pinning by
        omission."""
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        (d / "SECOND.md").write_text(MERGE_SOURCE_B, encoding="utf-8")
        self.assertEqual(migrate_run(d, "--from", "SECOND.md", "--from-done",
                                      "NONE", "--merge")[0], exits.CLEAN)
        src_rec, done_rec = migrate.recorded_blobs(
            (d / REPORT).read_text(encoding="utf-8"))
        self.assertEqual(
            src_rec.get("BACKLOG.md"),
            migrate.blob_sha((d / "BACKLOG.md").read_bytes()))
        self.assertEqual(
            src_rec.get("SECOND.md"),
            migrate.blob_sha((d / "SECOND.md").read_bytes()))
        self.assertIn("BACKLOG-DONE.md", done_rec)

    def test_a_moved_source_refuses_for_THAT_source(self):
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        (d / "SECOND.md").write_text(MERGE_SOURCE_B, encoding="utf-8")
        self.assertEqual(migrate_run(d, "--from", "SECOND.md", "--from-done",
                                      "NONE", "--merge")[0], exits.CLEAN)
        (d / "SECOND.md").write_text(
            "# second\n\n## Open\n\n- **READY 2026-09-01 — MOVED.** body\n",
            encoding="utf-8")
        code, out = migrate_run(d, "--from", "SECOND.md", "--from-done",
                                "NONE", "--merge")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("has MOVED", out)
        self.assertNotIn("MOVED.",
                         (d / "ITEMS.md").read_text(encoding="utf-8"))

    def test_a_source_with_no_recorded_line_is_not_a_mismatch(self):
        """An absent record at SOURCE granularity is the same answer as an
        absent record at report granularity: that carrier has not been
        migrated into these homes."""
        report = ("source-blob: " + "a" * 40 + "  (OTHER.md)\n"
                  "done-blob: NONE  (NONE)\n")
        self.assertIsNone(migrate.source_moved(
            report, "b" * 40, "NONE", "BACKLOG.md", "NONE"))
        # …and the SAME path with a different sha still refuses.
        self.assertIsNotNone(migrate.source_moved(
            report, "b" * 40, "NONE", "OTHER.md", "NONE"))

    def test_the_recorded_line_keeps_its_sha_in_group_one(self):
        """MUST NOT MOVE: a reader resolving the sha — the operator running
        `git hash-object` — is unaffected by the path becoming group 2."""
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        m = migrate._RECORDED_SOURCE_BLOB.search(
            (d / REPORT).read_text(encoding="utf-8"))
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1),
                         migrate.blob_sha((d / "BACKLOG.md").read_bytes()))
        self.assertEqual(m.group(2).strip(), "BACKLOG.md")


class ReImportByProvenance(unittest.TestCase):
    """lc-73 — RE-IMPORT IS A PROVENANCE QUESTION, NOT A HEADLINE ONE.

    The headline detector beside this one asks whether two bodies share a
    title, and that answer DECAYS the day anybody edits a requirement: at
    statiker it saw 20 re-imports at one commit and 17 at the next, the three
    that left having gained an `amended-requirement` and nothing else. The
    trigger for that decay is 'somebody edited a slot' — nothing about the
    work — and it fails in the QUIET direction: an already-migrated entry
    becomes re-importable as NEW work and nothing says so.

    HALF OF WHAT IS HERE IS MUST-NOT-MOVE, deliberately. A detector loosened
    until the re-imports stop being refused scores identically to one that got
    the distinction right, so every skip has a partner asserting what the
    change did NOT do: the genuine ambiguity still refuses the whole run, a
    provenance that merely RESEMBLES one present is not a match, and a range
    quoted in the ARCHIVE — which holds the source's own line ranges verbatim
    — anchors nothing, because an archive body is not an item.
    """

    def prefix(self) -> str:
        return GOOD_FULL_DECLARATION["id-prefix"]

    #: A source whose single entry is the one every case here is about.
    SOURCE = "# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n"

    def ranges(self, text: str) -> tuple:
        """`(line, end_line)` of the source's first entry, READ OUT OF THE
        READER rather than counted by hand.

        The fixtures below must cite the range the migration itself would
        write, and a hand-counted one is a second notion of where an entry
        starts: it would pass while the reader disagreed, which is the one
        state these cases exist to detect.
        """
        read = migrate.read_carrier(text)
        for e in read.entries:
            migrate.classify(e)
        return read.entries[0].line, read.entries[0].end_line

    def home(self, *blocks: str, baseline: int | None = None) -> str:
        """A live carrier holding exactly these blocks.

        `baseline` is overridable because it must count every BODY the homes
        hold, archive bodies included — a fixture that plants one in the done
        home and leaves the baseline at the block count fails
        `conservation_surplus` for a reason that has nothing to do with the
        case under test.
        """
        n = len(blocks) if baseline is None else baseline
        head = (f"schema: {items.SCHEMA_FLOOR}\nbaseline: {n}\n"
                "added: 0\ncompacted: 0\n")
        return head + "\n" + "\n".join(blocks)

    def block(self, ident: str, requirement: str, evidence: str,
              extra: str = "") -> str:
        b = items.render_block(ident, {
            "grade": "NEW", "requirement": requirement, "goal": "UNKNOWN",
            "write-set": "UNKNOWN", "done-criterion": "UNKNOWN",
            "evidence": evidence, "blocked-by": "decision regrade: what"})
        return b if not extra else b.rstrip("\n") + "\n" + extra + "\n"

    # --- the skip -----------------------------------------------------------

    def test_a_second_run_over_the_same_source_writes_nothing_twice(self):
        """The whole shape, end to end: what a migration wrote once it
        recognises as its own the second time."""
        d = build(self.SOURCE)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d, "--from-done", "NONE")[0],
                         exits.CLEAN)
        before = (d / "ITEMS.md").read_text(encoding="utf-8")
        code, out = migrate_run(d, "--from", "BACKLOG.md",
                                "--from-done", "NONE", "--merge")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("RE-IMPORTS skipped:       1", out)
        self.assertIn("already migrated as", out)
        after = (d / "ITEMS.md").read_text(encoding="utf-8")
        self.assertEqual(after.count("READY 2026-08-03 — first"), 1)
        self.assertEqual(after, before)

    def test_the_DECAYED_case_is_the_discriminating_one(self):
        """THE CASE A HEADLINE DETECTOR LOSES, and the reason this item
        exists. The successor's requirement has been amended, so the title the
        headline detector compares no longer matches — measured at statiker on
        st-8, st-10 and st-14. The provenance the migration wrote is intact,
        so the entry is still recognised.

        The old detector is RUN here, not described: without that arm this
        case would pass against a build that simply matched harder on
        headlines."""
        p = self.prefix()
        line, end = self.ranges(self.SOURCE)
        d = build(self.SOURCE)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "ITEMS.md").write_text(self.home(self.block(
            f"{p}-1", "a requirement somebody rewrote after the migration",
            f"BACKLOG.md:{line}-{end}")), encoding="utf-8")

        read = migrate.read_carrier(self.SOURCE)
        for e in read.entries:
            migrate.classify(e)
        parsed = items.parse((d / "ITEMS.md").read_text(encoding="utf-8"))
        self.assertEqual(
            migrate.duplicate_bodies(read.entries,
                                     migrate.existing_titles(parsed)), [],
            "the headline detector must MISS this entry, or the case proves "
            "nothing about provenance")

        code, out = migrate_run(d, "--from", "BACKLOG.md",
                                "--from-done", "NONE", "--merge")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("RE-IMPORTS skipped:       1", out)
        self.assertIn(f"already migrated as {p}-1", out)
        self.assertNotIn("READY 2026-08-03 — first",
                         (d / "ITEMS.md").read_text(encoding="utf-8"))

    def test_the_anchor_reads_the_RAW_block_not_the_resolved_slot(self):
        """`items.parse` puts the value IN FORCE into `slots`, so an
        `amended-evidence` line REPLACES the provenance a migration recorded.
        Measured at statiker: five of twenty anchors are invisible in the
        resolved slot and all twenty are intact in the raw block.

        READ AT THE INDEX, because that is where the two readings can be put
        side by side in one case: the same bytes, the resolved slot shown to
        have LOST the anchor and the index shown to still hold it. A run-level
        arm could only show the verdict, and a verdict cannot say which of the
        two readings produced it."""
        p = self.prefix()
        text = self.home(self.block(
            f"{p}-1", "a requirement somebody rewrote after the migration",
            "BACKLOG.md:23-46",
            extra="amended-evidence: 2026-09-12 a later run of prose that "
                  "says nothing about any line range"))
        parsed = items.parse(text)
        self.assertEqual(parsed.problems, [])
        self.assertNotIn("BACKLOG.md:23-46", parsed.items[0].slots["evidence"],
                         "the resolved slot must have LOST the anchor, or "
                         "this case does not test the raw-block read")
        self.assertEqual(migrate.provenance_index(text),
                         {("BACKLOG.md", 23, 46): f"{p}-1"})

    def test_a_re_import_held_only_in_the_DONE_home_is_recognised(self):
        """BOTH HOMES. Thirteen of statiker's twenty anchors sit in
        `ITEMS-DONE.md`; an index over the live carrier alone would re-import
        every one of them as open work, which is this repo's recurring silent
        defect."""
        p = self.prefix()
        line, end = self.ranges(self.SOURCE)
        d = build(self.SOURCE)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "ITEMS.md").write_text(self.home(), encoding="utf-8")
        (d / "ITEMS-DONE.md").write_text(
            f"schema: {items.SCHEMA_FLOOR}\n\n" + self.block(
                f"{p}-9", "a closed body nobody expects back",
                f"BACKLOG.md:{line}-{end}"), encoding="utf-8")
        code, out = migrate_run(d, "--from", "BACKLOG.md",
                                "--from-done", "NONE", "--merge")
        self.assertIn(f"already migrated as {p}-9", out)
        self.assertNotIn("READY 2026-08-03 — first",
                         (d / "ITEMS.md").read_text(encoding="utf-8"))
        # THE RUN'S CODE WAS 3 UNTIL lc-92 CLOSED THE OPEN REMAINDER this
        # comment used to point at: the per-source counter read the resolved
        # `evidence` slot over the live carrier alone, so the body planted in
        # the DONE home was invisible to it and the arithmetic could not be
        # promised. It reconciles now (1 + 0 against 1 read), and what is left
        # is this case's OWN hand-built heads: it writes both homes with a
        # `baseline` that never admitted the planted block, so the identity is
        # over by one. NAMED, not swapped for a bare 2 — any finding at all
        # satisfies a code assertion, which is a could-not-verify wearing a
        # green.
        self.assertIn("FINDING [conservation_surplus]", out)
        self.assertNotIn("COULD NOT VERIFY: the per-source arithmetic "
                         "disagrees", out)
        self.assertEqual(code, exits.FINDING, out)

    def test_the_count_is_printed_even_when_it_is_ZERO(self):
        """An omitted line reads as 'checked and clean' and a true zero reads
        as nothing at all. Under `--merge` the check ran, so its count is
        printed whatever it is (law 1's three answers)."""
        p = self.prefix()
        d = build(self.SOURCE)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "ITEMS.md").write_text(self.home(self.block(
            f"{p}-1", "unrelated work", "none yet")), encoding="utf-8")
        code, out = migrate_run(d, "--from", "BACKLOG.md",
                                "--from-done", "NONE", "--merge")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("RE-IMPORTS skipped:       0", out)
        self.assertIn("+ 0 re-imported", out)

    # --- must not move ------------------------------------------------------

    def test_a_headline_collision_at_DIFFERENT_provenance_still_REFUSES(self):
        """THE MUST-NOT-MOVE CONTROL the design names. Genuine ambiguity —
        two items that share a headline and were never the same import — is
        still the desk's call, and the whole run still refuses."""
        p = self.prefix()
        d = build(self.SOURCE)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        read = migrate.read_carrier(self.SOURCE)
        for e in read.entries:
            migrate.classify(e)
        # THE COLLIDING TITLE IS TAKEN FROM THE READER, never retyped: a
        # hand-copied headline that drifts by one character makes this arm
        # pass against a build that refuses nothing at all.
        headline = migrate.headline_of(read.entries[0])
        (d / "ITEMS.md").write_text(self.home(self.block(
            f"{p}-1", f"{headline} — record: OTHER.md:99",
            "OTHER.md:99-120")), encoding="utf-8")
        before = (d / "ITEMS.md").read_text(encoding="utf-8")
        code, out = migrate_run(d, "--from", "BACKLOG.md",
                                "--from-done", "NONE", "--merge")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[merge_duplicate_body]", out)
        self.assertIn("already present as", out)
        # THE REFUSAL RETURNS BEFORE THE RUN'S COUNTS ARE PRINTED, as it did
        # before this change: a run that refused and then went on to describe
        # what it would have written would be reporting a merge it did not do.
        self.assertNotIn("RE-IMPORTS skipped:", out)
        self.assertEqual((d / "ITEMS.md").read_text(encoding="utf-8"), before)

    def test_a_provenance_that_merely_RESEMBLES_one_present_is_no_match(self):
        """A prefix match wearing an equality's costume. Both halves of the
        triple are probed: a range that EXTENDS the stored one by a digit
        (`:5-6` against a stored `:5-60`) and the same range under a DIFFERENT
        source name. A substring test passes the first and a name-blind one
        passes the second, and each would claim a re-import of an entry nobody
        migrated.

        AT THE INDEX, with the run-level partner below carrying the source
        name half — a near-miss over the SAME source name is counted by
        `per_source_counts`, so a run-level arm for it would be measuring that
        counter rather than this match."""
        line, end = self.ranges(self.SOURCE)
        p = self.prefix()
        near = self.home(self.block(f"{p}-1", "unrelated work",
                                    f"BACKLOG.md:{line}-{end}0"))
        self.assertEqual(migrate.provenance_index(near),
                         {("BACKLOG.md", line, int(f"{end}0")): f"{p}-1"})
        read = migrate.read_carrier(self.SOURCE)
        for e in read.entries:
            migrate.classify(e)
        self.assertEqual(
            migrate.reimported_bodies(read.entries, "BACKLOG.md",
                                      migrate.provenance_index(near)), [],
            "an extended range is not the range")

        other = self.home(self.block(f"{p}-1", "unrelated work",
                                     f"OTHER.md:{line}-{end}"))
        d = build(self.SOURCE)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "ITEMS.md").write_text(other, encoding="utf-8")
        code, out = migrate_run(d, "--from", "BACKLOG.md",
                                "--from-done", "NONE", "--merge")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("RE-IMPORTS skipped:       0", out)
        self.assertIn("READY 2026-08-03 — first",
                      (d / "ITEMS.md").read_text(encoding="utf-8"))

    def test_a_range_quoted_in_the_ARCHIVE_anchors_nothing(self):
        """The archive holds the source's own bodies VERBATIM, at the line
        ranges named beside each one — the very tokens this index is keyed on.
        An archive body is not an ITEM, so counting one would skip an entry
        the successor holds no item for: a silent loss.

        The quoted range sits in the archived BODY rather than in the region's
        `<!-- … — ` marker, so what this case measures is the index's
        attribution and not `per_source_counts`' marker count.

        A REAL BLOCK PRECEDES THE ARCHIVE HEADING, and without it this case is
        an unread instrument: with no block open before the region, an index
        that never closed attribution at a non-block heading would carry
        `None` and score identically to one that closes it properly. Measured
        — the mutation that drops the close darkened nothing until this block
        was there."""
        p = self.prefix()
        line, end = self.ranges(self.SOURCE)
        d = build(self.SOURCE)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "ITEMS.md").write_text(self.home(baseline=2), encoding="utf-8")
        (d / "ITEMS-DONE.md").write_text(
            f"schema: {items.SCHEMA_FLOOR}\n\n"
            + self.block(f"{p}-9", "a closed body of unrelated work",
                         "none yet")
            + f"\n{items.ARCHIVE_HEADING}\n\n"
            f"- **READY 2026-08-03 — first.** body, from "
            f"BACKLOG.md:{line}-{end}\n", encoding="utf-8")
        code, out = migrate_run(d, "--from", "BACKLOG.md",
                                "--from-done", "NONE", "--merge")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("RE-IMPORTS skipped:       0", out)
        self.assertIn("READY 2026-08-03 — first",
                      (d / "ITEMS.md").read_text(encoding="utf-8"))

    # --- the index itself ---------------------------------------------------

    def test_the_index_keys_are_parsed_triples_over_block_bodies_only(self):
        """A unit read of the index, because the run-level cases above can
        only show its verdict. The head region has no block open, so nothing
        in it is attributed."""
        idx = migrate.provenance_index(
            "schema: 2\nbaseline: 1\n# HEAD.md:1-2 is not in a block\n\n"
            "## ab-1\nevidence: BACKLOG.md:23-46\n\n"
            "## ab-2\nevidence: prose\namended-evidence: 2026-09-12 quoted "
            "as `BACKLOG.md:47-73` inside a sentence\n")
        self.assertEqual(idx, {("BACKLOG.md", 23, 46): "ab-1",
                               ("BACKLOG.md", 47, 73): "ab-2"})

    def test_the_first_id_carrying_a_token_wins(self):
        """The index answers 'is this already present'. A second id carrying
        the same provenance is a DUPLICATE-ID question and belongs to the
        carrier's own shape check, not here."""
        idx = migrate.provenance_index(
            "## ab-1\nevidence: BACKLOG.md:1-2\n\n"
            "## ab-2\nevidence: BACKLOG.md:1-2\n")
        self.assertEqual(idx, {("BACKLOG.md", 1, 2): "ab-1"})


class TheConservationCounterFollowsTheAnchor(unittest.TestCase):
    """lc-92 — the counter reads the RAW BLOCK, over BOTH homes.

    WHAT THIS PINNED WHILE THE GAP WAS OPEN, kept because the record of a gap
    having been open is worth more than the tidy file: `per_source_counts`
    answered "how many bodies of this source do the homes hold" from
    `items.parse`'s AMENDMENT-RESOLVED `evidence` slot and over the LIVE
    carrier only — both of the readings lc-73 had already replaced in the
    DETECTOR, one function over, so a skipped re-import left the figure short
    and the merge answered COULD NOT VERIFY over bodies that were all on disk.
    lc-92 closed it: the figure is `provenance_index`'s, so the counter and
    the detector now read one record.

    THE TWO NOTIONS STAY APART. The items figure is provenance over the
    successor BLOCKS; the closures figure is the archive's per-closure
    markers. The archive is out of `provenance_index`'s scope by construction
    — attribution starts at a block heading and `## Archive (pre-migration)`
    is not one — which is what keeps a closure from being counted twice, and
    `test_an_archive_routed_closure_is_counted_once_not_twice` is that
    property executed rather than read off a docstring.
    """

    def test_a_skipped_re_import_reconciles_against_the_raw_anchor(self):
        p = GOOD_FULL_DECLARATION["id-prefix"]
        source = "# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n"
        d = build(source)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d, "--from-done", "NONE")[0],
                         exits.CLEAN)
        # The amendment that used to cost the counter its sight: append-only,
        # so the BASE evidence line — the anchor — survives it untouched.
        text = (d / "ITEMS.md").read_text(encoding="utf-8")
        self.assertIn("evidence: BACKLOG.md:", text)
        (d / "ITEMS.md").write_text(
            text.rstrip("\n") + "\namended-evidence: 2026-09-12 prose that "
            "names no line range\n", encoding="utf-8")

        code, out = migrate_run(d, "--from", "BACKLOG.md",
                                "--from-done", "NONE", "--merge")
        # The DETECTOR sees it — the anchor is read off the raw block.
        self.assertIn("RE-IMPORTS skipped:       1", out)
        self.assertIn(f"already migrated as {p}-1", out)
        # And now so does the COUNTER, off the same record.
        self.assertIn("blocks whose `evidence` names it: 1", out)
        self.assertNotIn("COULD NOT VERIFY: the per-source arithmetic "
                         "disagrees", out)
        self.assertEqual(code, exits.CLEAN, out)

    def test_a_body_that_moved_to_the_done_home_is_still_counted(self):
        """THE POINT OF THE REPAIR. A closed item's block lives in
        `ITEMS-DONE.md`, which the old reading never opened — at statiker 13
        of 20 anchors sat there."""
        p = GOOD_FULL_DECLARATION["id-prefix"]
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d, "--from-done", "NONE")[0],
                         exits.CLEAN)
        # The homes are committed before the close: `item close` records the
        # move, and an uncommitted home makes that step report
        # `move_uncommitted` — an ARRANGEMENT failure that reads exactly like
        # a finding about the counter.
        commit_all(d, "the migrated homes")
        code, out = run_cli(d, "item", "close", f"{p}-1",
                            "--reason", "done with it")
        self.assertEqual(code, exits.CLEAN, out)
        items_text = (d / "ITEMS.md").read_text(encoding="utf-8")
        done_text = (d / "ITEMS-DONE.md").read_text(encoding="utf-8")
        # The move happened — without this the case could pass over a body
        # that never left the live carrier.
        self.assertNotIn(f"## {p}-1", items_text)
        self.assertIn(f"## {p}-1", done_text)
        self.assertEqual(
            migrate.per_source_counts(items_text, done_text, "BACKLOG.md"),
            (1, 0))

    def test_an_archive_routed_closure_is_counted_once_not_twice(self):
        """D3's proof, executed. An archive body is quoted VERBATIM at the
        line range it came from, so the archive region physically carries the
        very tokens the items figure is keyed on. It must contribute nothing:
        items + closures == entries read − unclassified, and the merge is
        CLEAN."""
        d = build("# old\n\n## Open\n\n"
                  "- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        (d / "SECOND.md").write_text(
            "# second\n\n## Open\n\n"
            "- **READY 2026-09-01 — second open.** body\n"
            "- **DROPPED 2026-09-02 — second closed.** body\n",
            encoding="utf-8")
        code, out = migrate_run(d, "--from", "SECOND.md",
                                "--from-done", "NONE", "--merge")
        done_text = (d / "ITEMS-DONE.md").read_text(encoding="utf-8")
        # THE INSTRUMENT'S POSITIVE CONTROL: the token IS in the archive
        # region. Without this the zero contribution below would be
        # unfalsifiable — an archive carrying no token at all reads the same.
        self.assertRegex(done_text, r"<!-- SECOND\.md:\d+-\d+ — ")
        self.assertIn(items.ARCHIVE_HEADING, done_text)
        self.assertIn("blocks whose `evidence` names it: 1", out)
        self.assertIn("archive markers naming it:        1", out)
        self.assertIn("entries read − unclassified:      2", out)
        self.assertNotIn("COULD NOT VERIFY: the per-source arithmetic "
                         "disagrees", out)
        self.assertEqual(code, exits.CLEAN, out)

    def test_a_genuinely_unbalanced_merge_still_answers_could_not_verify(self):
        """MUST NOT MOVE, and it is the one way this repair could make the
        function worse: a read widened until every disagreement rounds to
        clean. A successor block claiming provenance the source does not
        offer is a surplus the counter cannot explain, and saying so is what
        code 3 means."""
        p = GOOD_FULL_DECLARATION["id-prefix"]
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — first.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d, "--from-done", "NONE")[0],
                         exits.CLEAN)
        # THE CONTROL, and it is what makes the red below attributable: the
        # SAME re-merge, before the tamper, reconciles and exits CLEAN. An
        # arrangement that answers COULD NOT VERIFY whatever is done to it
        # proves nothing about the tamper.
        code, out = migrate_run(d, "--from", "BACKLOG.md",
                                "--from-done", "NONE", "--merge")
        self.assertIn("blocks whose `evidence` names it: 1", out)
        self.assertNotIn("COULD NOT VERIFY: the per-source arithmetic "
                         "disagrees", out)
        self.assertEqual(code, exits.CLEAN, out)

        # A second block claiming BACKLOG.md:99-100 — a range no entry in the
        # source occupies. `added` is bumped with it so the TOTAL identity
        # stays clean and the per-source figure is the only thing that can
        # speak.
        #
        # THE SURPLUS DIRECTION, AND IT IS THE ONLY ONE AN INPUT CAN REACH.
        # The shortfall direction — the homes holding FEWER bodies than the
        # source offered — is not constructible from here, and measuring that
        # is how this case got its shape: removing a migrated body from the
        # homes makes its entry stop being a re-import, so the very next merge
        # writes it fresh and the arithmetic balances again (executed: exit 0,
        # `1 + 0` against `1`). That is `merge_conservation`'s own docstring
        # being right — no INPUT falsifies the identity, only a defect in the
        # writer does. A surplus IS reachable, and it is the same widened-read
        # failure seen from the other side.
        text = (d / "ITEMS.md").read_text(encoding="utf-8")
        text, ok = migrate.bump_head(text, "added", 1)
        self.assertTrue(ok)
        (d / "ITEMS.md").write_text(
            text.rstrip("\n") + "\n\n" + items.render_block(f"{p}-2", {
                "grade": "NEW", "requirement": "a body claiming provenance "
                "no entry offers", "goal": "UNKNOWN", "write-set": "UNKNOWN",
                "done-criterion": "UNKNOWN",
                "evidence": "BACKLOG.md:99-100",
                "blocked-by": "NONE"}), encoding="utf-8")

        code, out = migrate_run(d, "--from", "BACKLOG.md",
                                "--from-done", "NONE", "--merge")
        self.assertIn("blocks whose `evidence` names it: 2", out)
        self.assertIn("entries read − unclassified:      1", out)
        self.assertIn("COULD NOT VERIFY: the per-source arithmetic disagrees",
                      out)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)


class RequirementTitle(unittest.TestCase):
    """The duplicate check compares TITLES, and reaching one by chopping a
    rendered string at the first delimiter it happens to contain is a prefix
    match in an equality's costume."""

    def test_the_record_tail_is_parsed_off_at_the_line_end(self):
        self.assertEqual(
            migrate.requirement_title("a thing — record: BACKLOG.md:12"),
            "a thing")

    def test_a_title_carrying_the_phrase_resolves_against_the_LAST_tail(self):
        self.assertEqual(
            migrate.requirement_title(
                "a thing — record: not/a/tail — record: BACKLOG.md:12"),
            "a thing — record: not/a/tail")

    def test_a_requirement_with_no_tail_is_a_title_in_whole(self):
        self.assertEqual(migrate.requirement_title("just a headline"),
                         "just a headline")
        self.assertEqual(
            migrate.requirement_title("mentions — record: but not a path"),
            "mentions — record: but not a path")


class MintedDecisionQuestionsAreAnswerable(unittest.TestCase):
    """lc-40 — the mint wrote questions the ledger REFUSES to record an
    answer to, so the items carrying them were blocked forever.

    Three mechanisms, each right on its own: `ledger add decision` refuses a
    question carrying the ledger's slot separator (an escaped spelling would
    put two forms of every value in that file); `item ready` resolves a
    decision blocker by question-slot EQUALITY (lc-26), so a question
    rephrased at answer time no longer matches; and `migrate` minted the
    separator into two of its three questions. 69 of 99 decision-blocked
    items in dotfiles' carrier were unanswerable by construction.

    WHAT THE FIX MOVES is the MINT and nothing else — so half of what is
    here asserts that the ledger's own predicate did NOT move: a hand-written
    question carrying the separator is refused exactly as before, and an
    em-dash that is not the separator stores exactly as before. Without
    those, a fix that simply stopped refusing would score identically.
    """

    #: The real text, byte-for-byte as `migrate` minted it before the fix and
    #: as 66 of dotfiles' items still carry it. Quoted here as the RED's
    #: input, never as the expectation — the expectation is derived from the
    #: running minter below.
    OLD_REGRADE_QUESTION = ("regrade: was READY under the old carrier — "
                            "READY is judged, never inherited")

    def _every_branch(self):
        """`[(label, blocked-by)]` from the running `migration_blocker`.

        DERIVED BY EXECUTION, never restated: the values are whatever the
        five branches return today. REACH, stated rather than implied — this
        walks the branches that exist now; a branch added later is caught at
        the WRITE by `_ledger_storable`, which `build_items` calls on every
        entry it renders, and the end-to-end case below is what proves that
        call is live.
        """
        parked_dec = entry("- **PARKED 2026-01-01 — p.** The missing "
                           "decision here is which shape to take.")
        parked_ev = entry("- **PARKED 2026-01-01 — p.** Its named missing "
                          "evidence is a measurement nobody has taken.")
        ready = entry("- **READY 2026-01-01 — r.** body")
        record = entry("- **RECORD 2026-01-01 — r.** body")
        plain = entry("- **An entry with no grade word.** body")
        return [
            ("PARKED naming a decision",
             migrate.migration_blocker(parked_dec, slots_incomplete=True)[0]),
            ("PARKED naming evidence",
             migrate.migration_blocker(parked_ev, slots_incomplete=True)[0]),
            ("old READY",
             migrate.migration_blocker(ready, slots_incomplete=True)[0]),
            ("old RECORD",
             migrate.migration_blocker(record, slots_incomplete=True)[0]),
            ("slot-incomplete",
             migrate.migration_blocker(plain, slots_incomplete=True)[0]),
            ("the fall-through",
             migrate.migration_blocker(plain, slots_incomplete=False)[0]),
        ]

    def test_every_branch_of_the_minter_produces_a_storable_question(self):
        branches = self._every_branch()
        # The walk reached something, so a green here is not an empty loop.
        self.assertEqual(len(branches), 6)
        decisions = 0
        for label, blocked in branches:
            kind, detail = items.classify_blocker(blocked, None)
            self.assertIn(kind, ("decision", "evidence"), label)
            if kind != "decision":
                continue
            decisions += 1
            self.assertIsNone(
                ledger.check_prose(detail, "the minted decision question"),
                f"{label} mints a question `ledger add decision` refuses: "
                f"{detail!r}")
        # …and decision questions were actually among them: an evidence-only
        # walk would satisfy the loop above having checked nothing.
        self.assertGreaterEqual(decisions, 4)

    def test_the_minted_question_round_trips_and_unblocks_the_item(self):
        """END TO END, because storable is only half the criterion: lc-26
        matches the ledger's question slot against the blocker EXACTLY, so a
        question that stores but does not match still leaves the item
        blocked."""
        d = build("# old\n\n## Open\n\n- **READY 2026-01-01 — r.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        blocked = [ln for ln in
                   (d / "ITEMS.md").read_text(encoding="utf-8").splitlines()
                   if ln.startswith("blocked-by:")][0]
        kind, question = items.classify_blocker(
            blocked[len("blocked-by: "):], None)
        self.assertEqual(kind, "decision")

        # Before the answer the item reads BLOCKED — the baseline this pair
        # needs, since "UNBLOCKED" below means nothing over an item that was
        # never blocked.
        self.assertIn("BLOCKED — a RE-GRADE owed at the DESK",
                      run_cli(d, "item", "ready", "xx-1")[1])

        code, outp = run_cli(d, "ledger", "add", "decision",
                             "--question", question,
                             "--answer", "stays NEW; the desk regrades")
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertIn("UNBLOCKED — the ledger ANSWERS this decision",
                      run_cli(d, "item", "ready", "xx-1")[1])

    #: One pair per branch of the minter: two entries that take the SAME
    #: branch, so before lc-312 they carried one question between them.
    SAME_BRANCH_PAIRS = [
        ("old READY",
         "- **READY 2026-01-01 — a.** body\n\n"
         "- **READY 2026-01-02 — b.** body\n"),
        ("PARKED naming evidence",
         "- **PARKED 2026-01-01 — a.** Its named missing evidence is one "
         "measurement.\n\n"
         "- **PARKED 2026-01-02 — b.** Its named missing evidence is "
         "another.\n"),
        ("PARKED naming a decision",
         "- **PARKED 2026-01-01 — a.** The missing decision here is one "
         "shape.\n\n"
         "- **PARKED 2026-01-02 — b.** The missing decision here is "
         "another.\n"),
        ("slot-incomplete",
         "- **An entry with no grade word.** body\n\n"
         "- **Another entry with no grade word.** body\n"),
    ]

    def test_an_answer_to_one_migrated_item_leaves_its_sibling_blocked(self):
        """lc-312. `item ready` resolves a decision blocker by QUESTION
        EQUALITY, so two items carrying one literal question are cleared by
        one ledger line — measured on a scratch migration of a real carrier,
        where answering one parked-evidence item printed UNBLOCKED under
        another. The question is unique at the MINT or the answer is not
        about an item at all."""
        for label, body in self.SAME_BRANCH_PAIRS:
            with self.subTest(branch=label):
                d = build("# old\n\n## Open\n\n" + body)
                self.addCleanup(shutil.rmtree, d, ignore_errors=True)
                self.assertEqual(migrate_run(d)[0], exits.CLEAN)
                blocked = [ln[len("blocked-by: "):] for ln in
                           (d / "ITEMS.md").read_text(
                               encoding="utf-8").splitlines()
                           if ln.startswith("blocked-by:")]
                # Both items were written, so the pair below is a pair.
                self.assertEqual(len(blocked), 2)
                kind, question = items.classify_blocker(blocked[0], None)
                self.assertEqual(kind, "decision")
                # BASELINE: both read BLOCKED before any answer exists.
                for ident in ("xx-1", "xx-2"):
                    self.assertIn("BLOCKED — a RE-GRADE owed at the DESK",
                                  run_cli(d, "item", "ready", ident)[1])
                code, outp = run_cli(d, "ledger", "add", "decision",
                                     "--question", question,
                                     "--answer", "settled for the first")
                self.assertEqual(code, exits.CLEAN, outp)
                # The answer LANDED on the item it names — without this the
                # assertion below is satisfied by an answer matching nothing.
                self.assertIn("UNBLOCKED — the ledger ANSWERS this decision",
                              run_cli(d, "item", "ready", "xx-1")[1])
                second = run_cli(d, "item", "ready", "xx-2")[1]
                self.assertIn("BLOCKED — a RE-GRADE owed at the DESK", second)
                self.assertNotIn("UNBLOCKED", second)

    def test_item_ready_routes_a_migrated_blocker_to_the_desk_regrade(self):
        """A migrated blocker is cleared by RE-GRADING the item, and `item
        ready` said the opposite: "in the OPERATOR's court" and "no
        `decision:` line names this question", which reads as an invitation
        to write a ledger answer. Four independent re-grade lanes read it
        that way. One case per branch, since the PARKED-on-evidence branch is
        the one furthest from the operator's court."""
        for label, body in self.SAME_BRANCH_PAIRS:
            with self.subTest(branch=label):
                d = build("# old\n\n## Open\n\n" + body)
                self.addCleanup(shutil.rmtree, d, ignore_errors=True)
                self.assertEqual(migrate_run(d)[0], exits.CLEAN)
                code, outp = run_cli(d, "item", "ready", "xx-1")
                self.assertEqual(code, exits.CLEAN, outp)
                self.assertIn("BLOCKED — a RE-GRADE owed at the DESK", outp)
                self.assertIn("item amend xx-1", outp)
                self.assertNotIn("OPERATOR's court", outp)
                self.assertNotIn("has not been answered", outp)

    def test_a_hand_booked_decision_still_reads_the_operators_court(self):
        """MUST NOT MOVE: the desk wording is for questions `migrate` mints,
        recognised by their own text. A decision somebody booked stays where
        it was, including one that merely quotes a minted question."""
        d = build("# old\n\n## Open\n\n- **READY 2026-01-01 — r.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        commit_all(d, "migrated")
        for question in ("which window is canonical",
                         "is " + migrate.INCOMPLETE_DECISION + " still right"):
            with self.subTest(question=question):
                code, outp = run_cli(
                    d, "item", "amend", "xx-1",
                    "--blocked-by", "decision " + question,
                    "--not-derivable", "the operator's preference",
                    "--reason", "a hand-booked question")
                self.assertEqual(code, exits.CLEAN, outp)
                outp = run_cli(d, "item", "ready", "xx-1")[1]
                self.assertIn("BLOCKED — in the OPERATOR's court", outp)
                self.assertNotIn("RE-GRADE owed", outp)

    def test_the_guard_refuses_a_question_carrying_the_separator(self):
        """The mechanism's OWN red — `_ledger_storable` is what holds the
        mint against a later edit to one of the literals, and a guard shipped
        in the same commit as its subject is otherwise unexercised."""
        with self.assertRaises(ValueError) as raised:
            migrate._ledger_storable(
                "decision " + self.OLD_REGRADE_QUESTION)
        self.assertIn("cannot store", str(raised.exception))
        # MUST NOT MOVE: the same guard passes the text the minter produces
        # today, so the red above belongs to the separator and not to the
        # guard rejecting everything.
        for _label, blocked in self._every_branch():
            self.assertEqual(migrate._ledger_storable(blocked), blocked)

    def test_the_ledger_still_refuses_a_hand_written_separator(self):
        """MUST NOT MOVE: the fix is at the mint, so the ledger's predicate
        is unchanged — a session hand-writing such a question is refused
        exactly as it was."""
        d = build("# old\n\n## Open\n\n- **READY 2026-01-01 — r.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        code, outp = run_cli(d, "ledger", "add", "decision",
                             "--question", self.OLD_REGRADE_QUESTION,
                             "--answer", "an answer")
        self.assertEqual(code, exits.FINDING)
        self.assertIn("contains the slot separator", outp)

    def test_an_em_dash_that_is_not_the_separator_still_stores(self):
        """MUST NOT MOVE: what the ledger refuses is the SEPARATOR ` — `,
        never the character. A question whose em-dash sits inside a word-run
        stored before this change and stores after it."""
        d = build("# old\n\n## Open\n\n- **READY 2026-01-01 — r.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        code, outp = run_cli(d, "ledger", "add", "decision",
                             "--question", "does the A—B split hold",
                             "--answer", "it does")
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertIn("does the A—B split hold", outp)

    def test_the_already_storable_branch_is_byte_for_byte_unchanged(self):
        """MUST NOT MOVE: 30 of the 99 blocked items carry the
        slot-incomplete question, which never had the separator. Repairing
        it too would have re-broken every one of them, since lc-26 matches
        the stored blocker EXACTLY."""
        self.assertEqual(migrate.INCOMPLETE_DECISION,
                         "regrade: fill goal, write-set, done-criterion and "
                         "evidence, or drop")


class TheReportTellsANewlyGovernedRepoHowToWorkItsCarrier(unittest.TestCase):
    """Four facts every first re-grade lane on a migrated carrier met cold
    (relayed by that carrier's desk): the clearing act, the effective read,
    the predicate's exit contract, the commit attribution. Each is asserted
    by the token a reader would act on, taken from its own home where it has
    one."""

    def test_the_four_facts_are_in_the_report(self):
        from lifecycle_core import verbs
        d = build("# old\n\n## Open\n\n- **READY 2026-01-01 — r.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        report = " ".join((d / REPORT).read_text(encoding="utf-8").split())
        for token in ("clears by RE-GRADING the item, not by a ledger answer",
                      "`item slots <id>`",
                      "exits 0 when the evidence has ARRIVED",
                      verbs.COMMIT_TRAILER_ENV):
            with self.subTest(token=token):
                self.assertIn(token, report)


class HeadingShapeSaysWhatItDoesNotCheck(unittest.TestCase):
    """Under `--entry-shape heading` every bullet is body, by declaration. A
    carrier that ALSO holds entries written as top-level bullets loses them
    into the preceding heading entry's body: measured on a real carrier,
    three entries got no item and the run printed only two counts. No
    predicate separates such a bullet from body prose (on that carrier 233
    bold top-level bullets, 3 of them entries), so the run SAYS the shape is
    unchecked instead of pretending to detect it."""

    SOURCE = ("# old\n\n## Open\n\n"
              "### A heading entry\n\nits body\n\n\n"
              "- **An entry written as a bullet.** its own body\n")

    def test_the_run_and_the_report_say_a_bullet_entry_is_absorbed(self):
        d = build(self.SOURCE)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, outp = migrate_run(d, "--entry-shape", "heading")
        self.assertEqual(code, exits.CLEAN, outp)
        # The absorption itself, so the sentence below is about a real case:
        # one item for two entries.
        parsed = items.parse((d / "ITEMS.md").read_text(encoding="utf-8"))
        self.assertEqual(len(parsed.items), 1)
        report = (d / REPORT).read_text(encoding="utf-8")
        for where, text in (("run", outp), ("report", report)):
            with self.subTest(where=where):
                self.assertIn(migrate.HEADING_SHAPE_UNCHECKED,
                              " ".join(text.split()))

    def test_the_bullet_shape_does_not_carry_the_sentence(self):
        """MUST NOT MOVE: it is a statement about the heading shape only."""
        d = build("# old\n\n## Open\n\n- **READY 2026-01-01 — r.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, outp = migrate_run(d)
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertNotIn("gets no item of its own", outp)
        self.assertNotIn("gets no item of its own",
                         (d / REPORT).read_text(encoding="utf-8"))


LIVE_HEAD = ("# BACKLOG — the live queue\n"
             "\n"
             "This file is the queue. Add work here.\n"
             "\n"
             "## Open\n"
             "\n"
             "- **READY 2026-08-03 — real open work.** body\n")

#: The SAME file with the SAME title and a paragraph that makes NO liveness
#: claim. One property differs between this fixture and the one above, which
#: is what makes the pair separate "the banner is placed" from "the paragraph
#: is what decides where".
PROSE_HEAD = LIVE_HEAD.replace("This file is the queue. Add work here.",
                               "Notes on how these entries were written.")


def retire_run(repo: Path, *extra):
    """`migrate --retire-source`, on the COMMAND LINE, through `cli.main`.

    THE ALTITUDE IS THE POINT AND IT IS PINNED HERE. An earlier draft set
    `retire_source` on a parsed namespace, because the flag's declaration sat
    outside that lane's write set — and every one of these tests would have
    PASSED that way, proving the branch while leaving the plumbing the guard
    ships with (argparse, the decision, the exit code) unexercised. A
    unit-level green and a CLI green read identically in a test runner's
    output, so the spelling has to be exercised rather than assumed.
    """
    return run_cli(repo, "migrate", "--report", REPORT, "--retire-source",
                   *extra)


class CitationPins(unittest.TestCase):
    """lc-86 — a line number ALWAYS resolves, which is why a bare one lies so
    quietly: `BACKLOG.md:43` names a line in whatever the file holds today,
    not the entry the migration read. Measured in claude-code-cache-fix, where
    313 of 318 pointers land on the wrong entry and nothing fails."""

    def test_both_anchors_carry_the_pin_in_the_family_spelling(self):
        """BOTH, and the spelling is byte-exact against the operator's
        2026-09-12 ruling — `<path>:<line> at blob <sha>`. Asserted through
        `migrate.BLOB_PIN` rather than against a literal here: a restated
        separator would stay green the day the constant changed, which is the
        same-parentage failure one level down."""
        d = build("# old\n\n## Open\n\n- **READY 2026-08-03 — work.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        parsed = items.parse((d / "ITEMS.md").read_text(encoding="utf-8"))
        self.assertTrue(parsed.items)
        sha = migrate.blob_sha((d / "BACKLOG.md").read_bytes())
        for it in parsed.items:
            for slot in ("requirement", "evidence"):
                self.assertTrue(
                    it.slots[slot].endswith(f"{migrate.BLOB_PIN}{sha}"),
                    f"{slot}: {it.slots[slot]!r}")

    def test_the_pinned_line_resolves_to_the_entry_it_names(self):
        """THE PROPERTY, not the shape. A pin that named the wrong blob, or a
        line number computed over the pre-banner file, would satisfy every
        format assertion above and still point at the wrong body."""
        d = build("# old\n\n## Open\n\n"
                  "- **READY 2026-08-03 — the first entry.** body\n"
                  "- **READY 2026-08-04 — the second entry.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        on_disk = (d / "BACKLOG.md").read_text(encoding="utf-8").split("\n")
        parsed = items.parse((d / "ITEMS.md").read_text(encoding="utf-8"))
        self.assertEqual(len(parsed.items), 2)
        for it in parsed.items:
            m = re.search(r"BACKLOG\.md:(\d+)-(\d+)", it.slots["evidence"])
            body = "\n".join(on_disk[int(m.group(1)) - 1:int(m.group(2))])
            title = it.slots["requirement"].split(" — record:")[0]
            self.assertIn(title.split(" — ")[-1], body)

    def test_the_record_tail_still_parses_with_the_pin(self):
        """THE DEPENDENT THAT WOULD HAVE BROKEN IN SILENCE. The tail pattern
        ends at the line number; the pin lengthened the tail. Unwidened,
        `requirement_title` returns the whole rendered value, `duplicate_bodies`
        compares a title against a title-plus-tail, and `merge_duplicate_body`
        simply stops firing — a refusal going quiet, never a check going red.
        Both spellings must parse: the old carriers are still out there."""
        sha = "a" * 40
        self.assertEqual(
            migrate.requirement_title(f"a title — record: BACKLOG.md:5"
                                      f"{migrate.BLOB_PIN}{sha}"),
            "a title")
        self.assertEqual(
            migrate.requirement_title("a title — record: BACKLOG.md:5"),
            "a title")

    def test_a_pinned_range_is_not_read_as_unpinned(self):
        """THE BACKTRACKING TRAP, and it is why the pattern carries a second
        lookahead. Over `BACKLOG.md:8-8 at blob <sha>` a naive
        `\\d+(?:-\\d+)?(?! at blob …)` gives up the `-8`, matches
        `BACKLOG.md:8`, finds `-8 at blob…` is not the pin, and reports a
        PINNED anchor as unpinned — a refusal firing on legitimate work."""
        sha = "b" * 40
        self.assertEqual(
            migrate.unpinned_anchors(
                f"evidence: BACKLOG.md:8-8{migrate.BLOB_PIN}{sha}\n",
                "BACKLOG.md"),
            [])
        # THE KNOWN POSITIVE for the same instrument. A pattern that could
        # never match returns exactly what a true absence returns.
        self.assertEqual(
            [tok for _n, tok in migrate.unpinned_anchors(
                "evidence: BACKLOG.md:8-8\n", "BACKLOG.md")],
            ["BACKLOG.md:8-8"])


class PinSurvivesAnEditAbove(unittest.TestCase):
    """lc-38 — the anchor rule (a check anchored to mutating state) applied to
    the migration's OWN output. A line number always resolves, so a pointer
    below a later edit goes stale in silence: measured by the wave-4 desk
    2026-08-27 over dotfiles, where 84 of 85 `BACKLOG.md` pointers land exactly
    2 lines early and the one that does not is the single entry ABOVE the edit
    (mechanism verified at `4959d2d`, +2 net INSIDE the first entry).

    WHY THIS IS A SEPARATE CLASS FROM `CitationPins` ABOVE, which already
    asserts that the pin is WRITTEN and that it names the right body at
    migration time. Those cases read a source nobody has touched since, so
    they pass identically against a build that anchors on line numbers alone —
    the property they cannot see is the one lc-38 is about: what the pointer
    answers AFTER the living file moves under it. lc-86 built the pin and this
    class is what would go red if a later build dropped it, which is the half
    that had no mechanism: the repair was proven by hand at the desk and
    nothing in the battery held it.
    """

    #: One entry, deliberately the only one: the edit below is inserted ABOVE
    #: it, so every line of the pointed body shifts and a pointer that survives
    #: cannot be surviving by accident of a range that happens to still overlap.
    SOURCE = ("# BACKLOG\n"
              "\n"
              "## Open\n"
              "\n"
              "- **READY 2026-08-03 — the pointed entry.** its body\n")

    def migrated(self):
        """A repo migrated ONCE, committed, with `(dir, line, end, sha, title)`
        read back out of the carrier the tool wrote.

        COMMITTED because the pin names bytes, and bytes answer only from the
        object database: under a FROZEN disposition the sha is the POST-banner
        blob, which this tool writes and does not commit. A fixture that
        skipped the commit would fail at `cat-file` for a reason that has
        nothing to do with an edit above anything.
        """
        d = build(self.SOURCE)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        commit_all(d, "migrated")
        it = items.parse(
            (d / "ITEMS.md").read_text(encoding="utf-8")).items[0]
        # READ THROUGH `migrate.BLOB_PIN`, never against a restated separator:
        # a literal here would stay green the day the constant changed, which
        # is the same-parentage failure the pin itself exists to answer.
        m = re.search(rf"BACKLOG\.md:(\d+)-(\d+){re.escape(migrate.BLOB_PIN)}"
                      r"([0-9a-f]{40})", it.slots["evidence"])
        self.assertIsNotNone(
            m, f"the evidence slot carries no pinned anchor: "
               f"{it.slots['evidence']!r}")
        # The title comes from the READER, never retyped — a hand-copied
        # headline that drifts by one character passes this against a build
        # whose pointer resolves to nothing at all.
        title = migrate.requirement_title(it.slots["requirement"])
        return (d, int(m.group(1)), int(m.group(2)), m.group(3),
                title.split(" — ")[-1])

    @staticmethod
    def insert_two_lines_above(d: Path, line: int) -> None:
        """The done-criterion's own arrangement: two lines ABOVE the pointed
        entry, in the LIVING source, committed."""
        cur = (d / "BACKLOG.md").read_text(encoding="utf-8").split("\n")
        cur.insert(line - 1, "- **READY 2026-08-01 — an entry above.** other")
        cur.insert(line - 1, "")
        (d / "BACKLOG.md").write_text("\n".join(cur), encoding="utf-8")
        commit_all(d, "edit above the pointed entry")

    def test_the_pointer_still_resolves_to_the_same_body(self):
        """THE DONE-CRITERION, executed. The pointer is resolved through the
        BLOB it names, and what comes back is the body the migration read.

        THE SECOND HALF IS NOT A FLOURISH — it is what makes the first half
        mean anything. Read at the same range in the LIVE file, the pointer now
        lands on the entry that was inserted above, and that is exactly the
        measured dotfiles defect. Without it this case passes on a file nobody
        edited, i.e. against the very build it exists to refuse.
        """
        d, line, end, sha, title = self.migrated()
        self.insert_two_lines_above(d, line)

        pinned = subprocess.run(["git", "-C", str(d), "cat-file", "-p", sha],
                                capture_output=True, text=True)
        self.assertEqual(pinned.returncode, 0, pinned.stderr)
        self.assertIn(title,
                      "\n".join(pinned.stdout.split("\n")[line - 1:end]),
                      "the pinned anchor no longer resolves to its own body")

        live = (d / "BACKLOG.md").read_text(encoding="utf-8").split("\n")
        self.assertNotIn(title, "\n".join(live[line - 1:end]),
                         "the edit did not move the body, so this arrangement "
                         "could not have registered a stale pointer")

    def test_an_unresolvable_pin_fails_loudly_rather_than_resolving(self):
        """MUST NOT MOVE, and it is what decides shippability: a pointer whose
        blob cannot be resolved degrades to an honest COULD NOT VERIFY. A
        corrupt pin that quietly returned SOMETHING would be strictly worse
        than the stale line number, because nothing would look wrong.

        THE PAIR IS THE POINT: the same command over the REAL sha answers, so
        this is the resolution path discriminating rather than a `cat-file`
        that refuses everything in this fixture.
        """
        d, line, end, sha, _title = self.migrated()
        bogus = "d" * 40
        self.assertNotEqual(bogus, sha)
        bad = subprocess.run(["git", "-C", str(d), "cat-file", "-p", bogus],
                             capture_output=True, text=True)
        self.assertNotEqual(bad.returncode, 0,
                            "a bogus blob resolved to something")
        self.assertIn("Not a valid object name", bad.stderr)
        good = subprocess.run(["git", "-C", str(d), "cat-file", "-p", sha],
                              capture_output=True, text=True)
        self.assertEqual(good.returncode, 0, good.stderr)


class FreezeBanner(unittest.TestCase):
    """lc-86 — beat-the-books' `BACKLOG.md` was frozen in the repo's laws file
    and edited by a desk four hours later (`8d4440e8`). A freeze lives where
    the person about to append is looking, which is the file's own head."""

    def test_a_live_reading_head_is_replaced(self):
        d = build(LIVE_HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        head = (d / "BACKLOG.md").read_text(encoding="utf-8")
        self.assertIn(migrate.FROZEN_MARKER, head.split("\n")[0])
        self.assertNotIn("the live queue\n", head.split("## Open")[0])
        self.assertNotIn("Add work here", head)
        self.assertIn(f"{migrate.DISPOSED_FROZEN} —", out)

    def test_a_head_making_no_liveness_claim_keeps_its_prose(self):
        """MUST NOT MOVE. The two errors are not symmetric: missing a
        liveness claim leaves the banner inserted above an intact title, which
        is merely less tidy, while matching ordinary prose DELETES a paragraph
        nobody asked to lose. So the file keeps every word it had."""
        d = build(PROSE_HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        head = (d / "BACKLOG.md").read_text(encoding="utf-8")
        self.assertIn(migrate.FROZEN_MARKER, head.split("\n")[0])
        self.assertIn("Notes on how these entries were written.", head)
        self.assertIn("# BACKLOG — the live queue", head)

    def test_the_banner_is_idempotent(self):
        """SAME BYTES AND SAME BLOB, asserted as both rather than as "no
        exception raised". Keyed on the MARKER, never on the banner's whole
        text — the banner carries a DATE, so a second run on a later day would
        otherwise produce different bytes for an unchanged file and report its
        own write as the source having moved. The DATE IS DELIBERATELY
        DIFFERENT between the two calls below: with the same date, a banner
        that re-applied itself wholesale would still compare equal and this
        would pass over a build that is not idempotent at all."""
        text, first = migrate.apply_freeze_banner(
            LIVE_HEAD, "BACKLOG.md", "ITEMS.md", "2026-09-13")
        again, second = migrate.apply_freeze_banner(
            text, "BACKLOG.md", "ITEMS.md", "2027-01-01")
        self.assertEqual(text, again)
        self.assertEqual(migrate.blob_sha(text.encode("utf-8")),
                         migrate.blob_sha(again.encode("utf-8")))
        self.assertIn("already frozen", second)
        self.assertNotIn("already frozen", first)

    def test_a_report_only_run_then_a_writing_run_reports_no_move(self):
        """THE SEQUENCE THE SPLIT EXISTS FOR. `--report-only` writes no banner
        and records the AS-READ blob; the writing run that follows over the
        same `--report` path freezes the file and records the POST-banner one.
        With one blob doing both jobs, the writing run compares its own
        projected freeze against the dry run's record and refuses a file
        nobody touched. The move check therefore stays on the as-read blob."""
        d = build(LIVE_HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d, "--report-only")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(
            migrate._RECORDED_SOURCE_BLOB.search(
                (d / REPORT).read_text(encoding="utf-8")).group(1),
            migrate.blob_sha((d / "BACKLOG.md").read_bytes()))
        code, out = migrate_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("has MOVED", out)
        # And the record now names the BANNERED file, which is what keeps the
        # NEXT run clean — the property S8 turns on.
        self.assertEqual(
            migrate._RECORDED_SOURCE_BLOB.search(
                (d / REPORT).read_text(encoding="utf-8")).group(1),
            migrate.blob_sha((d / "BACKLOG.md").read_bytes()))

    def test_report_only_touches_the_source_not_at_all(self):
        """MUST NOT MOVE (S2). A run that writes no successor state has
        nothing for the source to be superseded BY, so it does not touch it —
        and `--report-only` exists precisely to be re-runnable."""
        d = build(LIVE_HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        before = (d / "BACKLOG.md").read_bytes()
        code, out = run_cli(d, "migrate", "--report", REPORT, "--report-only")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual((d / "BACKLOG.md").read_bytes(), before)
        self.assertIn(f"{migrate.DISPOSED_UNTOUCHED} —", out)

    def test_a_second_run_reports_no_spurious_move(self):
        """S8, THE TRAP IN THIS ITEM. The banner changes the source's blob,
        and `source_moved` exists because a source moving under the tool is a
        finding. The recorded `source-blob:` must therefore be the POST-banner
        blob, so the second run — which reads an already-bannered file —
        compares equal."""
        d = build(LIVE_HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(migrate_run(d)[0], exits.CLEAN)
        first = (d / "BACKLOG.md").read_bytes()
        code, out = migrate_run(d, "--force")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("has MOVED", out)
        self.assertEqual((d / "BACKLOG.md").read_bytes(), first)
        self.assertEqual(
            (d / "BACKLOG.md").read_text(encoding="utf-8").count(
                migrate.FROZEN_MARKER), 1)

    def test_the_freeze_stands_down_where_it_would_shift_a_cited_line(self):
        """MEASURED, not reasoned: with the banner applied unconditionally two
        of this repo's own re-import cases went red, because a carrier citing
        `BACKLOG.md:5-6` stopped recognising a body the reader now saw at line
        11. The re-import detector is the LOUD half; the quiet half is that
        those anchors still RESOLVE afterwards, several lines off."""
        d = build("# old\n\n## Open\n\n- **READY 2026-01-01 — e.** body\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "ITEMS.md").write_text(
            "schema: 2\nbaseline: 1\nadded: 0\ncompacted: 0\n\n"
            "## lc-1\ngrade: NEW\n"
            "requirement: an older build's entry — record: BACKLOG.md:5\n"
            "goal: UNKNOWN\nwrite-set: UNKNOWN\ndone-criterion: UNKNOWN\n"
            "evidence: BACKLOG.md:5-6\nblocked-by: NONE\n", encoding="utf-8")
        before = (d / "BACKLOG.md").read_bytes()
        code, out = migrate_run(d, "--merge")
        self.assertIn(f"{migrate.DISPOSED_UNTOUCHED} —", out)
        self.assertIn("no blob pin", out)
        self.assertEqual((d / "BACKLOG.md").read_bytes(), before)


class RetireSource(unittest.TestCase):
    """lc-86, the amended requirement: a migration ENDS with the source
    carrier deleted (operator decision 2026-09-12 — old state lives in git).
    The flag exists because the precondition is not computable here."""

    def test_the_source_is_deleted_and_its_citations_still_resolve(self):
        """THE WHOLE POINT, end to end: after the file is gone, the anchor
        the migration wrote still answers — through the blob, never the path."""
        d = build(LIVE_HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        sha = migrate.blob_sha((d / "BACKLOG.md").read_bytes())
        code, out = retire_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertFalse((d / "BACKLOG.md").exists())
        self.assertIn(f"{migrate.DISPOSED_DELETED} —", out)
        ev = items.parse((d / "ITEMS.md").read_text(
            encoding="utf-8")).items[0].slots["evidence"]
        self.assertIn(f"{migrate.BLOB_PIN}{sha}", ev)
        m = re.search(r"BACKLOG\.md:(\d+)-(\d+)", ev)
        blob = subprocess.run(["git", "-C", str(d), "cat-file", "-p", sha],
                              capture_output=True, text=True)
        self.assertEqual(blob.returncode, 0, blob.stderr)
        self.assertIn("real open work",
                      blob.stdout.split("\n")[int(m.group(1)) - 1])

    def test_no_banner_is_written_before_the_delete(self):
        """A sha whose bytes were never committed is a pointer to nothing the
        moment the file is unlinked — this tool does not commit. So the
        DELETED branch writes no banner and pins to the as-read blob, which
        the refusal below guarantees is already in the object database."""
        d = build(LIVE_HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        sha = migrate.blob_sha((d / "BACKLOG.md").read_bytes())
        self.assertEqual(retire_run(d)[0], exits.CLEAN)
        committed = subprocess.run(
            ["git", "-C", str(d), "rev-parse", "HEAD:BACKLOG.md"],
            capture_output=True, text=True).stdout.strip()
        self.assertEqual(sha, committed)

    def test_the_deletion_record_goes_into_the_declared_laws_file(self):
        """THE DECLARED one, resolved through the declaration — never a
        filename this tool picks."""
        d = build(LIVE_HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        declared = json.loads(
            (d / ".claude" / "lifecycle.json").read_text(
                encoding="utf-8"))["laws"]
        sha = migrate.blob_sha((d / "BACKLOG.md").read_bytes())
        self.assertEqual(retire_run(d)[0], exits.CLEAN)
        record = (d / declared).read_text(encoding="utf-8")
        self.assertIn("Deletion record", record)
        self.assertIn(sha, record)
        self.assertIn("git cat-file -p", record)

    def test_the_record_is_not_written_twice_for_one_deletion(self):
        """KEYED ON PATH AND BLOB. A re-created carrier at the SAME content is
        the same fact, and two bodies for one fact diverge. A re-created
        carrier at DIFFERENT content is a different deletion and earns its own
        record — the dotfiles precedent exactly: the exemption spends itself
        on the one content it names."""
        d = build(LIVE_HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(retire_run(d)[0], exits.CLEAN)
        once = (d / "LAWS.md").read_text(encoding="utf-8")
        self.assertEqual(once.count("## Deletion record"), 1)
        # The SAME bytes back, committed, and retired again: one record.
        (d / "BACKLOG.md").write_text(LIVE_HEAD, encoding="utf-8")
        commit_all(d, "carrier back")
        code, out = retire_run(d, "--force")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(
            (d / "LAWS.md").read_text(encoding="utf-8").count(
                "## Deletion record"), 1)

    def test_a_refusal_changes_nothing_at_all(self):
        """The load-bearing half. A precondition on an irreversible act that
        had already half-written is not a precondition."""
        d = build(LIVE_HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        before = (d / "BACKLOG.md").read_bytes()
        laws_before = (d / "LAWS.md").read_bytes()
        code, out = retire_run(d, "--report-only")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[retire_source_not_writing]", out)
        self.assertTrue((d / "BACKLOG.md").exists())
        self.assertEqual((d / "BACKLOG.md").read_bytes(), before)
        self.assertEqual((d / "LAWS.md").read_bytes(), laws_before)
        self.assertFalse((d / "ITEMS.md").exists())

    def test_an_uncommitted_edit_to_the_source_refuses(self):
        """TRACKED IS NOT ENOUGH, and this is the half a presence check
        misses: the blob the citations name is the one READ here, and it lives
        only in the file about to be deleted unless it is also the committed
        content."""
        d = build(LIVE_HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "BACKLOG.md").write_text(LIVE_HEAD + "- **READY 2026-08-05 — "
                                      "uncommitted.** body\n",
                                      encoding="utf-8")
        code, out = retire_run(d)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[retire_source_uncommitted]", out)
        self.assertTrue((d / "BACKLOG.md").exists())

    def test_a_declared_but_absent_laws_file_refuses(self):
        """THE OTHER HALF of the laws condition, exercised HERE because the
        roster cannot hold it. The presence half is decided in
        `declaration.check_laws_present` — reused rather than reimplemented —
        which is the same site `laws_absent_could_not_verify` owns, so a
        roster plant keyed to it makes one mutation darken both rows and
        proves neither. One site, one row; the coverage lives here instead."""
        d = build(LIVE_HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "LAWS.md").unlink()
        code, out = retire_run(d)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[retire_source_laws_absent]", out)
        self.assertTrue((d / "BACKLOG.md").exists())
        self.assertFalse((d / "ITEMS.md").exists())

    def test_schema_from_cannot_retire_a_source_it_never_read(self):
        d = build(LIVE_HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "migrate", "--schema-from", "1",
                            "--retire-source")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[retire_source_not_writing]", out)
        self.assertTrue((d / "BACKLOG.md").exists())

    def test_the_flag_is_declared_on_the_migrate_parser(self):
        """THE SPELLING, exercised rather than assumed. Every test above
        reaches the branch through this one flag, so a build that dropped the
        declaration would fail them all with a usage error — but a build that
        declared a DIFFERENT spelling would too, and the message would say
        nothing about which. Asserted against the parser itself."""
        args = cli.build_parser().parse_args(
            ["migrate", "--retire-source"])
        self.assertTrue(args.retire_source)
        self.assertFalse(cli.build_parser().parse_args(
            ["migrate"]).retire_source)


class DispositionIsAlwaysStated(unittest.TestCase):
    """The three-answers rule applied to the disposition: an omitted line
    reads as 'checked and clean' and a source nobody touched reads as nothing
    at all, and those are different answers."""

    def test_every_mode_names_its_disposition(self):
        for extra, want in ((("--report-only",), migrate.DISPOSED_UNTOUCHED),
                            ((), migrate.DISPOSED_FROZEN)):
            d = build(LIVE_HEAD)
            self.addCleanup(shutil.rmtree, d, ignore_errors=True)
            code, out = migrate_run(d, *extra)
            self.assertEqual(code, exits.CLEAN, out)
            self.assertIn("DISPOSITION (lc-86):", out)
            self.assertIn(want, out)

    def test_the_summary_line_no_longer_claims_a_dry_run_over_a_freeze(self):
        """A summary contradicting the stage three lines below it is the
        paraphrase every reader believes, because it is the one at the top."""
        d = build(LIVE_HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        out = migrate_run(d)[1]
        self.assertNotIn("are READ and are not edited, moved or deleted", out)
        report = (d / REPORT).read_text(encoding="utf-8")
        self.assertNotIn("**A DRY RUN**", report)
        self.assertIn("**FROZEN**", report)


class DeclaredClosureVocabulary(unittest.TestCase):
    """lc-91 — a repo declares its OWN closure words and `migrate` honours
    them, instead of reporting every such closure UNCLASSIFIED.

    EVERY BEHAVIOUR CASE HERE IS A PAIR, and the control is always the SAME
    carrier with the key ABSENT — the state every repo is in until it declares
    one. Without that partner an assertion that the closure reached the done
    home scores identically against a build that routes every unknown word
    there, which is the looser matcher this key exists not to be.

    WHY THE DECLARATION'S OWN REFUSALS ARE TESTED IN THIS FILE. There is no
    `test_declaration.py`; the precedent for an OPTIONAL declaration key is
    `delegation`, whose only test sits in its CONSUMER's file
    (`test_desk.py`). The consumer here is `migrate`.
    """

    #: THE KEY AS A LITERAL, deliberately, and pinned to the constant by its
    #: own case below. The behaviour arms have to be RUNNABLE against the OLD
    #: build, where they must go red on an ASSERTION — reaching through
    #: `decl.CLOSURE_WORDS_KEY` raises there instead, and a red that is an
    #: attribute error proves the code is new, never that the check
    #: discriminates (the same reasoning `ClosureVocabulary` states above).
    KEY = "closure-words"

    #: One key different from the control, and nothing else.
    DECLARED = {"ERLEDIGT": "DONE", "TRACED": "DROPPED"}

    CARRIER = ("# old\n\n## Open\n\n"
               "- **READY 2026-01-01 — ordinary open work.** body\n"
               "- **ERLEDIGT 2026-01-02 — a closure in the repo's own "
               "word.** body\n"
               "- **VERSCHOLLEN 2026-01-03 — a word nobody declared.** body\n")

    def declaring(self, words=None):
        return {**GOOD_FULL_DECLARATION,
                self.KEY: self.DECLARED if words is None else words}

    def migrate_with(self, declaration=None, carrier=None):
        d = build(carrier or self.CARRIER, declaration=declaration)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d)
        return d, code, out

    @staticmethod
    def findings_naming_the_key(doc):
        """Every finding whose message names the key, plant or control."""
        res = decl.Result(exits.CLEAN)
        decl.validate(doc, res)
        return [f for f in res.findings if "closure-words" in f.message]

    # --- the migration ------------------------------------------------------

    def test_a_declared_word_routes_the_closure_to_the_done_home(self):
        d, code, out = self.migrate_with(self.declaring())
        archive = (d / "ITEMS-DONE.md").read_text(encoding="utf-8")
        live = (d / "ITEMS.md").read_text(encoding="utf-8")
        self.assertIn("- **ERLEDIGT 2026-01-02 — a closure in the repo's own "
                      "word.** body", archive, out)
        self.assertNotIn("a closure in the repo's own word", live, out)

    def test_the_same_carrier_without_the_key_leaves_it_unclassified(self):
        """THE CONTROL for the case above — the declaration is the only
        difference, so the closure moving is attributable to it."""
        d, code, out = self.migrate_with()
        archive = (d / "ITEMS-DONE.md").read_text(encoding="utf-8")
        self.assertNotIn("a closure in the repo's own word", archive, out)
        self.assertIn("covers the grade word 'ERLEDIGT'", out)
        self.assertEqual(code, exits.FINDING, out)

    def test_an_undeclared_word_is_still_unclassified_beside_declared_ones(self):
        """MUST NOT MOVE (lc-19's rule, carried). A repo declaring SOME words
        does not thereby declare the rest: the entry the map does not name
        reports UNCLASSIFIED in the same run whose other closure moved."""
        d, code, out = self.migrate_with(self.declaring())
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("covers the grade word 'VERSCHOLLEN'", out)
        self.assertNotIn("VERSCHOLLEN",
                         (d / "ITEMS-DONE.md").read_text(encoding="utf-8"))

    def test_the_declared_word_never_becomes_a_grade(self):
        """TRANSLATION AT INTAKE, not a widened vocabulary: downstream still
        sees only the closed two, so nothing is written carrying the repo's
        own word as a GRADE. Read off the carriers rather than off
        `GRADES_CLOSED`, which a build could widen and this assertion would
        follow."""
        d, _, out = self.migrate_with(self.declaring())
        for home in ("ITEMS.md", "ITEMS-DONE.md"):
            text = (d / home).read_text(encoding="utf-8")
            for line in text.splitlines():
                self.assertFalse(line.startswith("grade: ERLEDIGT"),
                                 f"{home}: {line}")

    def test_classification_marks_it_closed_and_gives_it_no_grade(self):
        e = entry("- **ERLEDIGT 2026-01-02 — x.** body",
                  closure_words=self.DECLARED)
        self.assertTrue(e.closure)
        self.assertIsNone(e.grade)
        self.assertIn("the repo declares `ERLEDIGT`", e.rule)
        bare = entry("- **ERLEDIGT 2026-01-02 — x.** body")
        self.assertFalse(bare.closure)
        self.assertIn("no rule", bare.unclassified_why)

    def test_matching_is_case_sensitive(self):
        """A carrier word differing only in CASE is not the declared word.

        The pair is the point: `_GRADE_WORD` yields uppercase and nothing
        else, so `Erledigt` is not even read as a grade word — it migrates as
        ordinary ungraded work, exactly as it does in a repo that declared
        nothing, while `ERLEDIGT` in the same run is a closure.
        """
        mixed = entry("- **Erledigt 2026-01-02 — x.** body",
                      closure_words=self.DECLARED)
        self.assertIsNone(mixed.grade_word)
        self.assertFalse(mixed.closure)
        self.assertEqual(mixed.grade, "NEW")

    # --- the second derivation site (lc-21's scan) ---------------------------

    def test_a_declared_word_later_in_an_ungraded_title_is_ambiguous(self):
        """THE SECOND DERIVATION SITE. A declared word IS a closure word for
        this repo's carrier, so the lc-21 ambiguity arises for it identically
        — and the silent half is what is at stake: without this the entry is
        written into the open carrier as ordinary NEW work."""
        e = entry("- **a title that says ERLEDIGT later.** body",
                  closure_words=self.DECLARED)
        self.assertIsNone(e.grade)
        self.assertIn("AMBIGUOUS", e.unclassified_why)

    def test_the_same_title_with_an_undeclared_word_still_migrates(self):
        """THE CONTROL. The scan is keyed to the DECLARED words, not to
        capitalisation: an unmapped capitalised word mid-title stays ordinary
        ungraded work, which is the must-not-move partner lc-21 already
        carries for the native words."""
        e = entry("- **a title that says VERSCHOLLEN later.** body",
                  closure_words=self.DECLARED)
        self.assertEqual(e.grade, "NEW")
        self.assertEqual(e.unclassified_why, "")

    # --- the declaration ----------------------------------------------------

    def test_a_repo_declaring_nothing_is_unchanged(self):
        """OPTIONAL, and the key is NOT required — a new required key is a
        schema bump (§3.8c), which would reach every declared repo."""
        self.assertEqual(self.KEY, decl.CLOSURE_WORDS_KEY,
                         "the fixtures above spell the key as a literal so "
                         "they run against the old build; this is the pin "
                         "that keeps the two spellings one")
        self.assertNotIn(decl.CLOSURE_WORDS_KEY, decl.REQUIRED_KEYS)
        self.assertNotIn(decl.CLOSURE_WORDS_KEY, GOOD_FULL_DECLARATION)
        self.assertEqual(self.findings_naming_the_key(GOOD_FULL_DECLARATION),
                         [])
        self.assertEqual(decl.closure_words(GOOD_FULL_DECLARATION), {})

    def test_a_valid_map_is_accepted(self):
        """THE CONTROL every refusal below is one property away from."""
        self.assertEqual(self.findings_naming_the_key(self.declaring()), [])
        self.assertEqual(decl.closure_words(self.declaring()), self.DECLARED)

    def test_a_non_object_is_refused(self):
        found = self.findings_naming_the_key(
            self.declaring(["ERLEDIGT"]))
        self.assertEqual([f.row for f in found], ["declaration_malformed"])
        self.assertEqual(decl.closure_words(self.declaring(["ERLEDIGT"])), {})

    def test_a_grade_outside_the_closed_pair_is_refused(self):
        """A grade the tool does not know would be WRITTEN into the successor
        carrier as a word no verb understands — `classify` routes only closed
        grades to the done home."""
        found = self.findings_naming_the_key(
            self.declaring({"ERLEDIGT": "FERTIG"}))
        self.assertEqual([f.row for f in found], ["declaration_malformed"])
        self.assertIn("FERTIG", found[0].message)

    def test_a_word_no_carrier_could_yield_is_refused(self):
        """Case-sensitivity made loud. A lower- or mixed-case word could
        never match, and a rule that cannot fire reads exactly like one that
        never had to."""
        for dead in ("erledigt", "Erledigt", "E"):
            found = self.findings_naming_the_key(
                self.declaring({dead: "DONE"}))
            self.assertEqual([f.row for f in found],
                             ["declaration_malformed"], dead)
            self.assertIn(repr(dead), found[0].message)

    def test_a_word_the_tool_already_rules_on_is_refused(self):
        """DERIVED from `migrate.RULES`, never from a list here: a restated
        set would stay green the day the tool's own table grew, and the repo
        and the tool would then disagree about that word with nothing saying
        so."""
        for word in sorted(migrate.RULES):
            found = self.findings_naming_the_key(
                self.declaring({word: "DONE"}))
            self.assertEqual([f.row for f in found],
                             ["declaration_malformed"], word)
            self.assertIn("already rules on", found[0].message)

    def test_a_refused_map_migrates_as_if_absent(self):
        """A finding does NOT stop the verb, so the reader before the carrier
        is written is what decides. Half a vocabulary nobody declared is the
        one outcome worse than none."""
        d, code, out = self.migrate_with(
            self.declaring({"ERLEDIGT": "FERTIG"}))
        self.assertIn("covers the grade word 'ERLEDIGT'", out)
        self.assertNotIn("a closure in the repo's own word",
                         (d / "ITEMS-DONE.md").read_text(encoding="utf-8"))

    def test_the_shape_question_is_asked_of_the_pattern_itself(self):
        """`grade_word_shaped` answers for `_GRADE_WORD` rather than for a
        copy of it: every word the tool's own table carries passes, and a
        prefix-plus-junk form does not."""
        for word in sorted(migrate.RULES):
            self.assertTrue(migrate.grade_word_shaped(word), word)
        for junk in ("ERLEDIGT?", "ERLEDIGT x", " ERLEDIGT", "ERLEDIGTe"):
            self.assertFalse(migrate.grade_word_shaped(junk), junk)


class RepeatedFromRefuses(unittest.TestCase):
    """lc-31 — argparse's plain (non-`append`) dest OVERWRITES a repeated
    `--from`: `build_parser().parse_args(["migrate", "--from", "A.md",
    "--from", "B.md"])` returned `from_carrier="B.md"` with NO output, so a
    caller believed two sources were read and one was silently discarded.
    argparse overwriting is a silent wrong answer at the migration entry
    point. Distinct from `--merge`, which is a second INVOCATION naming a
    second source; this is ONE invocation naming two — `--merge` itself is
    untouched by this fix.

    RED, executed against a private clone of `b387ef0` (this item's own
    base commit): the same `parse_args` call there returns `'B.md'`,
    silently — pinned below as `test_a_repeated_from_is_the_measured_defect
    _shape_pre_fix`, which is true of BOTH the old and the fixed build (the
    refusal added by this item runs before that value is ever trusted, not
    by changing what argparse itself does with it).
    """

    def test_a_repeated_from_is_the_measured_defect_shape_pre_fix(self):
        """Pins argparse's own overwrite as a fact independent of the fix:
        a plain (non-`append`) dest keeps only the LAST `--from`. This is
        exactly what made the bug silent, and exactly what the refusal
        below exists to intercept before this value is trusted anywhere."""
        ns = cli.build_parser().parse_args(
            ["migrate", "--from", "A.md", "--from", "B.md"])
        self.assertEqual(ns.from_carrier, "B.md")

    def test_a_second_from_in_one_invocation_refuses(self):
        """THE FIX. `main()` refuses before ever resolving a repo or
        reading a source, so the repeated flag is caught however the rest
        of the invocation is spelled."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(["--repo", "/nonexistent/path/for-lc-31",
                             "migrate", "--from", "A.md", "--from", "B.md"])
        self.assertEqual(code, exits.FINDING)
        self.assertIn(
            "one --from per invocation; use --merge for a second source",
            buf.getvalue())

    def test_the_equals_form_is_also_caught(self):
        """`--from=A.md --from=B.md` is the same flag under argparse's
        other accepted spelling; the raw-argv count the fix takes must see
        both forms or a caller need only reach for `=` to slip through."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(["--repo", "/nonexistent/path/for-lc-31",
                             "migrate", "--from=A.md", "--from=B.md"])
        self.assertEqual(code, exits.FINDING)
        self.assertIn(
            "one --from per invocation; use --merge for a second source",
            buf.getvalue())

    def test_a_single_from_is_unchanged(self):
        """MUST-NOT-MOVE. The ordinary, single-source invocation is not
        touched by this fix."""
        ns = cli.build_parser().parse_args(["migrate", "--from", "A.md"])
        self.assertEqual(ns.from_carrier, "A.md")

    def test_no_from_at_all_is_unchanged(self):
        """MUST-NOT-MOVE, the other boundary: the documented default (no
        `--from`) still parses to `None`, and absence is not a repetition."""
        ns = cli.build_parser().parse_args(["migrate"])
        self.assertIsNone(ns.from_carrier)


#: A carrier whose ENTRIES ARE ITS LEVEL-3 HEADINGS — the shape `bullet`
#: misreads. Every entry carries bullets in its body, two of them shaped like
#: bullet-entries (bold, grade-led), because the misread is exactly a body
#: bullet admitted as an entry. Five headings: two under an open section, one
#: parked, one under a section no rule names, one closed.
HEADING_CARRIER = """# old carrier

A preamble paragraph.

- a bullet before any heading

## Ready

- a bullet in the section's own preamble

### First ready entry

**Booked 2026-01-01.** A prose body.

- a body bullet
- **READY 2026-01-01 — a body bullet shaped like a bullet entry.** x

#### A deeper heading is body

- a bullet under the deeper heading

### Second ready entry whose title says DONE mid-way

A body with no bullet at all.

## Parked

### A parked entry

**PARKED.** Missing evidence: a measurement nobody has taken.

## Notes

### A heading under a section no rule names

- **READY 2026-01-01 — the body leads with a grade word.** x

## Done

### A closed entry

**Shipped.** Closed long ago.

- a closing bullet
"""

HEADING_TITLES = ["First ready entry",
                  "Second ready entry whose title says DONE mid-way",
                  "A parked entry",
                  "A heading under a section no rule names",
                  "A closed entry"]


def heading_read(text: str = HEADING_CARRIER) -> migrate.Read:
    """The carrier through the real reader AND the real classifier, in the
    `heading` shape — the pair `run` applies, never an Entry built by hand."""
    read = migrate.read_carrier(text, entry_shape=migrate.ENTRY_SHAPE_HEADING)
    for e in read.entries:
        migrate.classify_heading(e)
    return read


def heading_run(repo: Path, *extra):
    return migrate_run(repo, "--entry-shape", "heading", *extra)


class HeadingEntriesAreOnePerHeading(unittest.TestCase):
    """`--entry-shape heading`: an entry is a level-3 heading and every bullet
    beneath it is its BODY. Read as bullets, this carrier yields the body
    bullets as entries and none of the headings."""

    def test_one_entry_per_heading_and_the_bullets_are_body(self):
        read = heading_read()
        self.assertEqual([migrate.headline_of(e) for e in read.entries],
                         HEADING_TITLES)
        self.assertTrue(all(e.heading for e in read.entries))
        # Four bullets sit inside entry bodies and two sit outside any entry
        # (before the first heading, and in `## Ready`'s own preamble).
        self.assertEqual(read.body_bullets, 5)
        self.assertEqual(len(read.outside_bullets), 2)
        self.assertEqual(read.total_bullets, 7)
        self.assertEqual(read.non_entry_bullets, [])

    def test_the_same_carrier_read_as_bullets_is_the_misread(self):
        """THE CONTRAST, so the case above is not green for a reader that
        ignores the shape: `bullet` admits the two bullet-shaped body bullets
        and none of the five headings."""
        read = migrate.read_carrier(HEADING_CARRIER)
        self.assertEqual(len(read.entries), 2)
        self.assertFalse(any(e.heading for e in read.entries))
        self.assertTrue(all(e.raw_first.startswith("**READY")
                            for e in read.entries))

    def test_the_headline_is_the_heading_and_nothing_from_the_body(self):
        first = heading_read().entries[0]
        self.assertEqual(migrate.headline_of(first), "First ready entry")
        self.assertEqual(migrate.title_of(first), "First ready entry")
        # ... while the body IS carried in `text`, which is what the existing
        # write-rules read.
        self.assertIn("a body bullet", first.text)

    def test_the_requirement_cap_applies_unchanged(self):
        long_title = "x" * (migrate.REQUIREMENT_CAP + 40)
        read = heading_read(f"# c\n\n## Ready\n\n### {long_title}\n\nbody\n")
        self.assertEqual(len(migrate.title_of(read.entries[0])),
                         migrate.REQUIREMENT_CAP)
        self.assertEqual(migrate.headline_of(read.entries[0]), long_title)

    def test_the_range_runs_from_the_heading_to_the_line_before_the_next(self):
        read = heading_read()
        lines = HEADING_CARRIER.split("\n")
        for e, title in zip(read.entries, HEADING_TITLES):
            self.assertEqual(lines[e.line - 1], f"### {title}")
        first, second = read.entries[0], read.entries[1]
        self.assertEqual(first.end_line, second.line - 1)
        # The second entry ends on the line before `## Parked`, a SHALLOWER
        # heading — a body never runs across a section.
        self.assertEqual(lines[second.end_line + 1 - 1], "## Parked")
        # The last entry ends at the file's last line, not one past it.
        self.assertEqual(read.entries[-1].end_line,
                         len(HEADING_CARRIER.rstrip("\n").split("\n")))

    def test_a_level_four_heading_is_body_not_an_entry(self):
        read = heading_read()
        self.assertNotIn("A deeper heading is body",
                         [migrate.headline_of(e) for e in read.entries])
        first = read.entries[0]
        lines = HEADING_CARRIER.split("\n")
        deeper = lines.index("#### A deeper heading is body") + 1
        self.assertTrue(first.line < deeper <= first.end_line)
        self.assertIn("#### A deeper heading is body", first.text)
        # ... and the bullet UNDER it is that entry's body too.
        self.assertIn("a bullet under the deeper heading", first.text)

    def test_the_heading_count_is_taken_without_the_reader(self):
        """The identity's independent side: counted off the text by its own
        expression, and a level-4 line is not one."""
        self.assertEqual(migrate.level3_lines(HEADING_CARRIER), 5)
        self.assertEqual(heading_read().level3_headings, 5)
        self.assertEqual(migrate.level3_lines("#### deeper\n## two\n###x\n"),
                         0)


class TheSectionGradesAHeadingEntry(unittest.TestCase):
    """In this shape the SECTION is the carrier's only grading statement. The
    body's lead word is not read and the title is not scanned."""

    def by_title(self, title):
        return next(e for e in heading_read().entries
                    if migrate.headline_of(e) == title)

    def test_an_open_section_grades_by_its_first_word_upper_cased(self):
        e = self.by_title("First ready entry")
        self.assertEqual(e.grade_word, "READY")
        self.assertEqual(e.grade, migrate.RULES["READY"][0])
        self.assertEqual(e.rule, migrate.RULES["READY"][1])
        self.assertFalse(e.closure)
        # `Parked` reads as PARKED and takes that word's EXISTING rule whole,
        # NEW-branch sentence included — no mapping is added for this shape.
        p = self.by_title("A parked entry")
        self.assertEqual(p.grade_word, "PARKED")
        self.assertEqual(p.grade, "NEW")
        self.assertTrue(p.rule.startswith(migrate.RULES["PARKED"][1]))

    def test_a_closure_section_archives_and_grades_nothing(self):
        e = self.by_title("A closed entry")
        self.assertTrue(e.closure)
        self.assertIsNone(e.grade)
        self.assertIsNone(e.grade_word)
        self.assertEqual(e.rule, migrate.SECTION_CLOSURE_RULE)

    def test_an_unknown_section_is_ungraded_whatever_its_body_leads_with(self):
        """The body opens with a bold `READY` bullet. Read for a grade, this
        entry would take READY's rule and its regrade blocker; the section
        says nothing, so it is ungraded."""
        e = self.by_title("A heading under a section no rule names")
        self.assertIsNone(e.grade_word)
        self.assertEqual((e.grade, e.rule), migrate.UNGRADED_RULE)
        self.assertFalse(e.closure)

    def test_a_closure_word_in_the_title_is_ordinary_language(self):
        """The bullet shape REFUSES a closure word standing alone later in an
        ungraded title. A heading title is prose, so here it migrates."""
        e = self.by_title("Second ready entry whose title says DONE mid-way")
        self.assertEqual(e.grade, migrate.RULES["READY"][0])
        self.assertEqual(e.unclassified_why, "")
        self.assertFalse(e.closure)

    def test_a_heading_in_a_cut_section_is_counted_and_not_migrated(self):
        read = heading_read(
            "# c\n\n## Grades and what they mean\n\n### READY\n\n- prose\n\n"
            "## Ready\n\n### a real entry\n\nbody\n")
        self.assertEqual([migrate.headline_of(e) for e in read.entries],
                         ["a real entry"])
        self.assertEqual(len(read.cut_headings), 1)
        self.assertEqual(read.level3_headings,
                         len(read.entries) + len(read.cut_headings))
        # The cut heading's bullet belongs to no entry.
        self.assertEqual(read.body_bullets, 0)
        self.assertEqual(len(read.outside_bullets), 1)


class HeadingShapeEndToEnd(unittest.TestCase):
    """The same carrier through the CLI: what lands in each successor home,
    and what the run and the report say about the shape they read."""

    def setUp(self):
        self.d = build(HEADING_CARRIER)
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        self.code, self.out = heading_run(self.d)
        self.items = (self.d / "ITEMS.md").read_text(encoding="utf-8")
        self.done = (self.d / "ITEMS-DONE.md").read_text(encoding="utf-8")
        self.report = (self.d / REPORT).read_text(encoding="utf-8")

    def test_one_item_per_open_heading_and_one_archived_closure(self):
        self.assertEqual(self.code, exits.CLEAN, self.out)
        parsed = items.parse(self.items)
        self.assertEqual(
            [migrate.requirement_title(it.slots["requirement"])
             for it in parsed.items], HEADING_TITLES[:4])
        self.assertIn("source entries read:      5", self.out)
        self.assertIn("items written:            4 ", self.out)
        self.assertIn("CLOSURES routed to the done home: 1 ", self.out)
        self.assertIn("UNCLASSIFIED (reported):  0", self.out)
        # The closure is in the done home VERBATIM, body included, and in the
        # open carrier not at all.
        self.assertIn("### A closed entry\n\n**Shipped.** Closed long ago.\n"
                      "\n- a closing bullet", self.done)
        self.assertNotIn("A closed entry", self.items)
        # No body bullet became an item.
        self.assertNotIn("a body bullet shaped like a bullet entry",
                         self.items)

    def test_the_evidence_range_is_the_heading_through_its_last_body_line(self):
        """Resolved against the file ON DISK — the frozen one, whose lines the
        citations index."""
        src = (self.d / "BACKLOG.md").read_text(encoding="utf-8").split("\n")
        parsed = items.parse(self.items)
        for it, title in zip(parsed.items, HEADING_TITLES):
            m = re.match(r"BACKLOG\.md:(\d+)-(\d+) at blob [0-9a-f]{40}$",
                         it.slots["evidence"])
            self.assertIsNotNone(m, it.slots["evidence"])
            start, end = int(m.group(1)), int(m.group(2))
            self.assertEqual(src[start - 1], f"### {title}")
            self.assertFalse(any(re.match(r"#{1,3}\s", ln)
                                 for ln in src[start:end]))
            self.assertRegex(src[end], r"^#{1,3}\s")

    def test_the_section_decides_the_blocker_the_existing_rules_write(self):
        parsed = items.parse(self.items).items
        blockers = [it.slots["blocked-by"] for it in parsed]
        # Each question ends in its OWN item's id (lc-312), spelled out here
        # rather than taken from the minter's helper, which would move with it.
        own = [f" (item {it.ident})" for it in parsed]
        self.assertEqual(blockers[0], migrate.REGRADE_BLOCKER + own[0])
        self.assertEqual(blockers[1], migrate.REGRADE_BLOCKER + own[1])
        self.assertEqual(blockers[2], "decision "
                         + migrate.PARKED_EVIDENCE_QUESTION + own[2])
        # The unknown-section entry's body LEADS with `READY`; it carries the
        # ungraded blocker and not the regrade one.
        self.assertEqual(blockers[3], "decision "
                         + migrate.INCOMPLETE_DECISION + own[3])

    def test_the_run_and_the_report_both_state_the_shape_they_read(self):
        self.assertIn("    entry shape:              heading — ", self.out)
        self.assertIn("Entry shape read: `heading`", self.report)

    def test_the_heading_accounting_is_printed_as_an_identity(self):
        self.assertIn("level-3 headings read:    5 == 5 entries + 0 cut",
                      self.out)
        self.assertIn("top-level bullets:        5 inside an entry's body, "
                      "2 outside any entry", self.out)
        self.assertIn("**Heading identity:** 5 level-3 headings = 5 entries "
                      "+ 0 cut — HOLDS", self.report)
        self.assertNotIn("Bullet identity", self.report)

    def test_a_reader_that_loses_a_heading_could_not_verify(self):
        """The identity is CHECKED: with the reader's count and the text's
        made to disagree, the run answers COULD NOT VERIFY."""
        d = build(HEADING_CARRIER)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        real = migrate.level3_lines
        migrate.level3_lines = lambda text: real(text) + 1
        self.addCleanup(setattr, migrate, "level3_lines", real)
        code, out = heading_run(d)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("the heading arithmetic disagrees", out)

    def test_report_only_takes_the_option_like_any_other_run(self):
        d = build(HEADING_CARRIER)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        before = (d / "BACKLOG.md").read_bytes()
        code, out = heading_run(d, "--report-only")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("source entries read:      5", out)
        self.assertFalse((d / "ITEMS.md").exists())
        self.assertEqual((d / "BACKLOG.md").read_bytes(), before)

    def test_a_merge_re_run_recognises_every_heading_entry_it_wrote(self):
        """`--merge` behaves as it does today: the provenance this shape
        writes is what the re-import detector reads. Over the OPEN entries
        only — a closure in the `--from` carrier is re-archived by every
        merge re-run in either shape, which is not this option's to change."""
        d = build(HEADING_CARRIER[:HEADING_CARRIER.index("## Done")])
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(heading_run(d)[0], exits.CLEAN)
        commit_all(d, "migrated")
        code, out = heading_run(d, "--merge")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("RE-IMPORTS skipped:       4 ", out)
        self.assertIn("items written:            0 ", out)


class HeadingShapeOverNoHeadings(unittest.TestCase):
    """The declared shape matching nothing in the file. Zero entries reads
    exactly like a clean migration, so it is the third answer."""

    BULLETS = ("# old\n\n## Open\n\n- **READY 2026-01-01 — an ordinary "
               "entry.** body\n")

    def test_it_could_not_verify_and_writes_nothing(self):
        d = build(self.BULLETS)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        before = (d / "BACKLOG.md").read_bytes()
        code, out = heading_run(d)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("COULD NOT VERIFY [migration_heading_shape_empty]", out)
        self.assertFalse((d / "ITEMS.md").exists())
        self.assertFalse((d / "ITEMS-DONE.md").exists())
        self.assertFalse((d / REPORT).exists())
        self.assertEqual((d / "BACKLOG.md").read_bytes(), before)

    def test_one_level_three_heading_is_enough_to_answer(self):
        """MUST-NOT-MOVE: the guard keys on the heading count, so the same
        carrier with one heading migrates."""
        d = build(self.BULLETS.replace("## Open\n\n",
                                       "## Open\n\n### a heading\n\n"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = heading_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("migration_heading_shape_empty", out)
        self.assertIn("source entries read:      1", out)

    def test_the_refusal_has_its_own_roster_row(self):
        from lifecycle_core import refusals
        row = next(r for r in refusals.ROWS
                   if r.ident == "migration_heading_shape_empty")
        self.assertEqual(row.expect, exits.COULD_NOT_VERIFY)
        fired, control = row.fire(), row.control()
        self.assertEqual(fired.code, exits.COULD_NOT_VERIFY, fired.output)
        self.assertIn("[migration_heading_shape_empty]", fired.output)
        self.assertNotIn("[migration_heading_shape_empty]", control.output)
        self.assertNotEqual(control.code, fired.code)


class BulletShapeOverNoEntries(unittest.TestCase):
    """The mirror of `HeadingShapeOverNoHeadings`: the DEFAULT shape reading
    zero entries from a carrier that shows its entries are written some
    other way. Zero reads exactly like a clean migration, so it is the third
    answer — and where the carrier shows no such sign, zero stays an answer."""

    HEADINGS = ("# old\n\n## Open\n\n### first entry\n\nbody one\n\n"
                "### second entry\n\nbody two\n")
    STARRED = ("# old\n\n## Open\n\n"
               "* **READY 2026-01-01 — a starred entry.** body\n"
               "+ **READY 2026-01-02 — a plus entry.** body\n")
    ENTRY = "- **READY 2026-01-03 — an ordinary entry.** body\n"

    def refused(self, text, *extra):
        d = build(text)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        before = (d / "BACKLOG.md").read_bytes()
        code, out = migrate_run(d, *extra)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("COULD NOT VERIFY [migration_bullet_shape_empty]", out)
        self.assertNotIn("migrate: CLEAN", out)
        self.assertFalse((d / "ITEMS.md").exists())
        self.assertFalse((d / "ITEMS-DONE.md").exists())
        self.assertFalse((d / REPORT).exists())
        self.assertEqual((d / "BACKLOG.md").read_bytes(), before)
        return out

    def migrated(self, text, entries):
        d = build(text)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("migration_bullet_shape_empty", out)
        self.assertIn(f"source entries read:      {entries}\n", out)
        self.assertTrue((d / "ITEMS.md").exists())
        return d, out

    def test_headings_under_the_default_shape_could_not_verify(self):
        out = self.refused(self.HEADINGS)
        self.assertIn("holds 2 level-3 heading(s) and 0 line(s) opening "
                      "with `* ` or `+ `", out)
        self.assertIn("--entry-shape heading", out)

    def test_the_shape_named_explicitly_is_refused_the_same(self):
        self.refused(self.HEADINGS, "--entry-shape", "bullet")

    def test_other_marker_lines_alone_could_not_verify(self):
        out = self.refused(self.STARRED)
        self.assertIn("holds 0 level-3 heading(s) and 2 line(s) opening "
                      "with `* ` or `+ `", out)

    def test_a_dry_run_is_refused_too(self):
        self.refused(self.HEADINGS, "--report-only")

    def test_one_entry_is_enough_whatever_else_the_carrier_holds(self):
        """MUST-NOT-MOVE (a): the guard keys on ZERO entries. One bold `- `
        entry beside the same headings and the same other-marker lines
        migrates, and it migrates to the same item as it does without them."""
        mixed = self.HEADINGS + "\n" + self.STARRED[len("# old\n\n## Open\n\n"):] \
            + "\n" + self.ENTRY
        d1, _ = self.migrated(mixed, 1)
        d2, _ = self.migrated("# old\n\n## Open\n\n" + self.ENTRY, 1)
        strip = lambda t: re.sub(r"BACKLOG\.md:\d+(-\d+)? at blob [0-9a-f]+",  # noqa: E731
                                 "BACKLOG.md:N", t)
        self.assertEqual(strip((d1 / "ITEMS.md").read_text(encoding="utf-8")),
                         strip((d2 / "ITEMS.md").read_text(encoding="utf-8")))

    def test_an_empty_carrier_still_migrates(self):
        """MUST-NOT-MOVE (b): zero entries and NEITHER signal is an answer."""
        self.migrated("# old\n\n## Open\n\n", 0)

    def test_plain_prose_bullets_alone_still_migrate(self):
        """MUST-NOT-MOVE (b): a plain `- ` bullet is counted as prose and is
        no sign of another shape."""
        self.migrated("# old\n\n## Open\n\n- a plain prose bullet\n"
                      "- another one\n", 0)

    def test_a_star_rule_is_not_an_other_marker_line(self):
        """`* * *` opens with `* ` and is a horizontal rule, not a list
        line: alone it is no signal."""
        self.migrated("# old\n\n## Open\n\nprose\n\n* * *\n\n***\n\n"
                      "more prose\n", 0)

    def test_the_reader_still_reads_an_other_marker_line_as_body(self):
        """READING SEMANTICS DO NOT CHANGE: the starred line's text is in
        the entry above it, and it is no entry and no prose bullet."""
        read = migrate.read_carrier(
            "# old\n\n## Open\n\n" + self.ENTRY
            + "* **READY — a starred line**\n")
        self.assertEqual(len(read.entries), 1)
        self.assertIn("a starred line", read.entries[0].text)
        self.assertEqual(read.total_bullets, 1)
        self.assertEqual(read.non_entry_bullets, [])

    def test_the_refusal_has_its_own_roster_row(self):
        from lifecycle_core import refusals
        row = next(r for r in refusals.ROWS
                   if r.ident == "migration_bullet_shape_empty")
        self.assertEqual(row.expect, exits.COULD_NOT_VERIFY)
        fired, control = row.fire(), row.control()
        self.assertEqual(fired.code, exits.COULD_NOT_VERIFY, fired.output)
        self.assertIn("[migration_bullet_shape_empty]", fired.output)
        self.assertNotIn("[migration_bullet_shape_empty]", control.output)
        self.assertEqual(control.code, exits.CLEAN, control.output)


class OtherMarkerLinesAreSaid(unittest.TestCase):
    """A `bullet` read that DID find entries, over a carrier that also holds
    top-level `* ` / `+ ` lines: they are read as body exactly as before, and
    the run and the report now say so."""

    PLAIN = ("# old\n\n## Open\n\n"
             "- a plain prose bullet\n"
             "- **READY 2026-01-01 — an ordinary entry.** body\n")
    MIXED = (PLAIN
             + "* **READY 2026-01-02 — a starred line.** body\n"
             + "\n## Later\n\n"
             + "- **READY 2026-01-03 — a second entry.** body\n"
             + "+ a plus line\n"
             + "\n* * *\n")

    def run_over(self, text, *extra):
        d = build(text)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d, *extra)
        return d, code, out, (d / REPORT).read_text(encoding="utf-8")

    @staticmethod
    def line_of(d, opening):
        """The 1-based line of the one line opening with `opening`, in the
        file ON DISK — the frozen one, whose lines every citation indexes
        (the banner in its head moves them)."""
        src = (d / "BACKLOG.md").read_text(encoding="utf-8").split("\n")
        hits = [i + 1 for i, ln in enumerate(src) if ln.startswith(opening)]
        assert len(hits) == 1, (opening, hits)
        return hits[0]

    def test_one_note_line_on_stdout_naming_the_count_and_the_first_line(self):
        d, code, out, report = self.run_over(self.MIXED)
        self.assertEqual(code, exits.CLEAN, out)
        notes = [ln for ln in out.split("\n") if "NOTE: " in ln]
        self.assertEqual(len(notes), 1, out)
        self.assertEqual(
            notes[0].strip(),
            'NOTE: 2 line(s) in BACKLOG.md open with "* " or "+ " (first at '
            f'line {self.line_of(d, "* **READY")}). The bullet shape reads '
            '"- " as the bullet, so these were NOT read as entries: each '
            "is body of the entry above it where one is open, and reaches "
            "no item where none is.")

    def test_the_report_counts_them_and_lists_where_they_are(self):
        d, code, out, report = self.run_over(self.MIXED)
        rows = report.split("\n")
        prose = next(i for i, ln in enumerate(rows)
                     if ln.startswith("| of those, non-entry prose bullets"))
        self.assertEqual(
            rows[prose + 1],
            "| top-level lines opening with `* ` or `+ ` (NOT read as "
            "entries) | 2 |")
        self.assertIn("## Lines under another list marker", report)
        section = report[report.index("## Lines under another list marker"):]
        section = section[:section.index("\n## ", 1)] \
            if "\n## " in section[1:] else section
        listed = [ln for ln in section.split("\n") if ln.startswith("- `")]
        # The star rule is no list line: two lines listed, not three.
        self.assertEqual(listed, [
            f"- `BACKLOG.md:{self.line_of(d, '* **READY')}` — section: Open",
            f"- `BACKLOG.md:{self.line_of(d, '+ a plus line')}` — section: "
            "Later"])

    def test_the_bullet_identity_is_unchanged_and_still_holds(self):
        """These lines are not `- ` bullets and stay outside the identity."""
        d, code, out, report = self.run_over(self.MIXED)
        self.assertIn("**Bullet identity:** 3 top-level bullets = 2 entries "
                      "+ 1 prose + 0 cut — HOLDS", report)

    def test_the_note_changes_no_exit_code_and_no_successor_byte(self):
        """NOTHING ELSE MOVES. The reader is asked directly: the same text
        with and without the count taken reads the same entries, so the
        successor carrier is the one the entries alone decide."""
        d, code, out, report = self.run_over(self.MIXED)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("source entries read:      2\n", out)
        self.assertIn("items written:            2 ", out)
        parsed = items.parse((d / "ITEMS.md").read_text(encoding="utf-8"))
        self.assertEqual(len(parsed.items), 2)
        # The starred line is in the FIRST item's evidence range — body of
        # the entry above it, as before.
        m = re.match(r"BACKLOG\.md:(\d+)-(\d+) at blob ",
                     parsed.items[0].slots["evidence"])
        self.assertIsNotNone(m, parsed.items[0].slots["evidence"])
        self.assertEqual(int(m.group(1)),
                         self.line_of(d, "- **READY 2026-01-01"))
        self.assertGreaterEqual(int(m.group(2)),
                                self.line_of(d, "* **READY"))

    def test_none_of_them_prints_no_note_and_a_zero_row(self):
        d, code, out, report = self.run_over(self.PLAIN)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("NOTE: ", out)
        self.assertIn("| top-level lines opening with `* ` or `+ ` (NOT "
                      "read as entries) | 0 |", report)
        self.assertNotIn("## Lines under another list marker", report)

    def test_a_star_rule_alone_is_a_zero(self):
        d, code, out, report = self.run_over(self.PLAIN + "\n* * *\n\n***\n")
        self.assertNotIn("NOTE: ", out)
        self.assertIn("as entries) | 0 |", report)

    def test_the_heading_shape_says_nothing_of_them(self):
        """In the heading shape every such line is body by DECLARATION."""
        text = ("# old\n\n## Open\n\n### a heading entry\n\n"
                "* a starred body line\n")
        d, code, out, report = self.run_over(text, "--entry-shape", "heading")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn('open with "* "', out)
        self.assertNotIn("opening with `* `", report)


class BulletShapeNote(unittest.TestCase):
    """The other direction of the silent misread: a `bullet` read over a
    carrier whose entries sit beneath level-3 headings says so in ONE line,
    names the option, and changes nothing else."""

    GROUPED = ("# old\n\n## Open\n\n### a group\n\n"
               "- **READY 2026-01-01 — an entry beneath a heading.** body\n\n"
               "### another group\n\n"
               "- **READY 2026-01-02 — a second one.** body\n")
    FLAT = GROUPED.replace("### a group\n\n", "").replace(
        "### another group\n\n", "")

    def run_over(self, text, *extra):
        d = build(text)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d, *extra)
        return d, code, out

    def test_one_note_line_on_stdout_and_in_the_report(self):
        d, code, out = self.run_over(self.GROUPED)
        notes = [ln for ln in out.split("\n") if "NOTE: " in ln]
        self.assertEqual(len(notes), 1, out)
        self.assertIn("2 level-3 heading(s) in BACKLOG.md", notes[0])
        self.assertIn("2 of the 2 entries read sit beneath one", notes[0])
        self.assertIn("--entry-shape heading", notes[0])
        report = (d / REPORT).read_text(encoding="utf-8")
        self.assertEqual(
            len([ln for ln in report.split("\n") if ln.startswith("NOTE: ")]),
            1)
        self.assertIn(notes[0].strip(), report)

    def test_the_note_changes_no_exit_code_and_no_successor_byte(self):
        """Against the SAME entries with the two heading lines removed: the
        verdict is the same, and so is every item slot but the line numbers
        the headings moved."""
        d1, code1, out1 = self.run_over(self.GROUPED)
        d2, code2, out2 = self.run_over(self.FLAT)
        self.assertEqual(code1, code2)
        self.assertEqual(code1, exits.CLEAN, out1)
        strip = lambda t: re.sub(r"BACKLOG\.md:\d+(-\d+)? at blob [0-9a-f]+",  # noqa: E731
                                 "BACKLOG.md:N", t)
        self.assertEqual(strip((d1 / "ITEMS.md").read_text(encoding="utf-8")),
                         strip((d2 / "ITEMS.md").read_text(encoding="utf-8")))
        self.assertNotIn("NOTE: ", out2)
        self.assertNotIn("NOTE: ", (d2 / REPORT).read_text(encoding="utf-8"))

    def test_a_heading_no_entry_sits_beneath_prints_no_note(self):
        """The trigger is an ENTRY beneath a level-3 heading, not a level-3
        heading existing: one over prose alone is not this carrier's
        structure."""
        text = self.FLAT + "\n### a closing remark\n\nprose, no bullet\n"
        d, code, out = self.run_over(text)
        self.assertNotIn("NOTE: ", out)

    def test_the_heading_shape_prints_no_note(self):
        d, code, out = self.run_over(self.GROUPED, "--entry-shape", "heading")
        self.assertNotIn("NOTE: ", out)


class ParkedEvidenceDoesNotMigrateAsAnUnclearableBlocker(unittest.TestCase):
    """lc-308 — a PARKED entry naming missing evidence used to migrate with
    `evidence false`, which `item check` proves can never clear. The migrated
    carrier failed the tool's own check, in both entry shapes."""

    BULLET = ("# c\n\n## Parked\n\n"
              "- **PARKED 2026-01-01 — waits.** Its named missing evidence is "
              "a measurement nobody has taken.\n"
              "- **PARKED 2026-01-01 — asks.** The missing decision here is "
              "which shape to take.\n")
    HEADING = ("# c\n\n## Parked\n\n"
               "### Waits\n\nMissing evidence: a measurement nobody has "
               "taken.\n\n"
               "### Asks\n\nThe missing decision here is which shape to "
               "take.\n")

    def migrated(self, text, *extra):
        d = build(text)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d, *extra)
        self.assertEqual(code, exits.CLEAN, out)
        carrier = (d / "ITEMS.md").read_text(encoding="utf-8")
        return d, carrier, items.parse(carrier).items

    def check_shape(self, text, *extra):
        d, carrier, parsed = self.migrated(text, *extra)
        blockers = [it.slots["blocked-by"] for it in parsed]
        # The evidence-naming entry takes the new decision, the
        # decision-naming one keeps its own question: the two stay distinct.
        self.assertEqual(blockers, [
            "decision " + migrate.PARKED_EVIDENCE_QUESTION
            + f" (item {parsed[0].ident})",
            "decision " + migrate.PARKED_DECISION_QUESTION
            + f" (item {parsed[1].ident})"])
        self.assertNotIn("evidence false", carrier)
        code, out = run_cli(d, "item", "check")
        self.assertNotIn("blocker_softlock", out)

    def test_bullet_shape(self):
        self.check_shape(self.BULLET)

    def test_heading_shape(self):
        self.check_shape(self.HEADING, "--entry-shape", "heading")

    def test_the_report_counts_the_entry_as_a_decision(self):
        d, _carrier, _parsed = self.migrated(self.BULLET)
        report = (d / REPORT).read_text(encoding="utf-8")
        self.assertIn("| `decision` | 2 |", report)
        self.assertIn("| `evidence` | 0 |", report)


LABELLED_CARRIER = """# old carrier

## Ready

### Both labels once

Some prose first.

**Write-set:** `plugin/a.py`, `test/b.py`.

*Done-criterion:* the thing works, shown by
a run that spans two lines.

### No label at all

Write-set is mentioned mid-sentence here, and so is done-criterion.

### Write-set twice

*Write-set:* `plugin/a.py`.

*Write-set:* `plugin/c.py`.

**Done-criterion:** only one of these.

### A parenthesis before the colon

**Write-set (draft):** `plugin/a.py`.

Done-criterion (see above): never read.

### A label inside a fence

```

Write-set: not/a/real/label.py

```

## Done

### A closed entry

**Shipped.**
"""

LABELLED_TITLES = ["Both labels once", "No label at all", "Write-set twice",
                   "A parenthesis before the colon", "A label inside a fence"]


class LabelledSlotsTravel(unittest.TestCase):
    """lc-311 — a slot a source entry states under its literal label migrates
    filled from the entry's own words; everything else stays `UNKNOWN`."""

    def slots_of(self, body: str):
        read = heading_read(f"# c\n\n## Ready\n\n### An entry\n\n{body}\n")
        return migrate.labelled_slots(read.entries[0])

    def test_both_labels_once_fill_both_slots_with_the_entry_words(self):
        values, counts = self.slots_of(
            "**Write-set:** `plugin/a.py`, `test/b.py`.\n\n"
            "*Done-criterion:* works,\nacross two lines.")
        self.assertEqual(values, {"write-set": "plugin/a.py, test/b.py",
                                  "done-criterion": "works, across two lines."})
        self.assertEqual(counts, {"write-set": 1, "done-criterion": 1})

    def test_every_listed_spelling_is_read(self):
        for opener in ("*{}:*", "**{}:**", "*{}.*", "**{}.**"):
            for word, slot in (("Write-set", "write-set"),
                               ("Done-criterion", "done-criterion")):
                with self.subTest(opener=opener, word=word):
                    values, _ = self.slots_of(opener.format(word) + " v")
                    self.assertEqual(values, {slot: "v"})

    def test_no_label_is_no_slot(self):
        self.assertEqual(self.slots_of("Just prose, Write-set: later."),
                         ({}, {}))

    def test_a_parenthesis_before_the_punctuation_is_not_a_label(self):
        self.assertEqual(self.slots_of("**Write-set (draft):** `a.py`.\n\n"
                                       "Done-criterion (see above): x"),
                         ({}, {}))

    def test_a_slot_labelled_twice_is_counted_and_not_returned(self):
        values, counts = self.slots_of("*Write-set:* `a.py`.\n\n"
                                       "*Write-set:* `b.py`.\n\n"
                                       "**Done-criterion:** one")
        self.assertEqual(values, {"done-criterion": "one"})
        self.assertEqual(counts, {"write-set": 2, "done-criterion": 1})

    def test_a_label_inside_a_fenced_block_is_not_read(self):
        # A blank line inside the fence makes the label line the first line
        # of a run of its own; only the fence state keeps it from counting.
        self.assertEqual(self.slots_of("```\n\nWrite-set: x/y.py\n\n```"),
                         ({}, {}))

    def test_an_empty_value_is_not_returned(self):
        values, counts = self.slots_of("**Write-set:**")
        self.assertEqual(values, {})
        self.assertEqual(counts, {"write-set": 1})

    def test_a_write_set_comes_out_as_a_bare_comma_list_the_join_reads(self):
        values, _ = self.slots_of("**Write-set:** `plugin/a.py`, `test/b.py`.")
        bucket, paths, why = items.classify_write_set(values["write-set"])
        self.assertEqual(bucket, items.WAVE_PATHS, why)
        self.assertEqual(paths, ["plugin/a.py", "test/b.py"])

    def test_only_the_write_set_is_stripped_of_backticks_and_its_full_stop(self):
        values, _ = self.slots_of("**Write-set:** `a.py`.\n\n"
                                  "**Done-criterion:** a `thing` holds.")
        self.assertEqual(values["write-set"], "a.py")
        self.assertEqual(values["done-criterion"], "a `thing` holds.")

    def test_a_bullet_entry_has_no_body_and_reads_nothing(self):
        read = migrate.read_carrier(
            "# c\n\n## Ready\n\n- **READY 2026-01-01 — t.** "
            "**Write-set:** `a.py`. **Done-criterion:** x\n")
        self.assertEqual(read.entries[0].body, "")
        self.assertEqual(migrate.labelled_slots(read.entries[0]), ({}, {}))


class LabelledSlotsEndToEnd(unittest.TestCase):

    def setUp(self):
        self.d = build(LABELLED_CARRIER)
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        self.code, self.out = heading_run(self.d)
        self.items = (self.d / "ITEMS.md").read_text(encoding="utf-8")
        self.report = (self.d / REPORT).read_text(encoding="utf-8")
        self.parsed = items.parse(self.items).items

    def slot(self, i, name):
        return self.parsed[i].slots[name]

    def test_a_labelled_and_an_unlabelled_entry(self):
        self.assertEqual(self.code, exits.CLEAN, self.out)
        self.assertEqual(self.slot(0, "write-set"), "plugin/a.py, test/b.py")
        self.assertEqual(self.slot(0, "done-criterion"),
                         "the thing works, shown by a run that spans two "
                         "lines.")
        for slot in ("write-set", "done-criterion"):
            self.assertEqual(self.slot(1, slot), migrate.UNKNOWN)
        # `goal` has no label and stays UNKNOWN on every entry.
        self.assertTrue(all(it.slots["goal"] == migrate.UNKNOWN
                            for it in self.parsed))

    def test_a_doubly_labelled_slot_is_unknown_and_its_sibling_is_filled(self):
        self.assertEqual(self.slot(2, "write-set"), migrate.UNKNOWN)
        self.assertEqual(self.slot(2, "done-criterion"), "only one of these.")

    def test_the_parenthesis_and_the_fence_entries_stay_unknown(self):
        for i in (3, 4):
            for slot in ("write-set", "done-criterion"):
                self.assertEqual(self.slot(i, slot), migrate.UNKNOWN)

    def test_the_migrated_carrier_has_no_shape_finding(self):
        """The third answer: no refusal exists for a one-line value, so none
        is written. This is the read-back that says so."""
        code, out = run_cli(self.d, "item", "check")
        self.assertNotIn("item_shape", out)

    def test_the_counts_sum_to_the_items_written(self):
        read = heading_read(LABELLED_CARRIER)
        outcomes = migrate.slot_outcomes(
            [e for e in read.entries if e.grade is not None])
        for slot in ("write-set", "done-criterion"):
            self.assertEqual(sum(outcomes[slot].values()), len(self.parsed))
        self.assertEqual(outcomes["write-set"],
                         {"filled": 1, "unlabelled": 3, "repeated": 1})
        self.assertEqual(outcomes["done-criterion"],
                         {"filled": 2, "unlabelled": 3, "repeated": 0})

    def test_the_report_prints_the_counts_zeros_included(self):
        self.assertIn("`write-set` — filled from the entry's own label: 1; "
                      "left `UNKNOWN`, no label: 3; left `UNKNOWN`, "
                      "labelled in more than one paragraph: 1", self.report)
        self.assertIn("`done-criterion` — filled from the entry's own label: "
                      "2; left `UNKNOWN`, no label: 3; left `UNKNOWN`, "
                      "labelled in more than one paragraph: 0", self.report)
        self.assertNotIn("`goal` and `done-criterion` are written `UNKNOWN`",
                         self.report)


class LabelledSlotsStayInTheHeadingShape(unittest.TestCase):
    """MUST-NOT-MOVE: a bullet run over the same label text writes UNKNOWN."""

    def test_a_bullet_run_writes_unknown_for_both(self):
        d = build("# c\n\n## Ready\n\n- **READY 2026-01-01 — t.** body\n"
                  "  **Write-set:** `a.py`.\n\n  **Done-criterion:** x\n")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d)
        self.assertEqual(code, exits.CLEAN, out)
        it = items.parse((d / "ITEMS.md").read_text(encoding="utf-8")).items[0]
        self.assertEqual(it.slots["write-set"], migrate.UNKNOWN)
        self.assertEqual(it.slots["done-criterion"], migrate.UNKNOWN)


class BulletShapeIsUnchanged(unittest.TestCase):
    """MUST-NOT-MOVE: without the option, and with `--entry-shape bullet`,
    a bullet carrier migrates as it did. `LIVE_HEAD` is an existing fixture
    of this file."""

    def outputs(self, *extra):
        d = build(LIVE_HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = migrate_run(d, *extra)
        files = {name: (d / name).read_bytes()
                 for name in ("ITEMS.md", "ITEMS-DONE.md", "BACKLOG.md",
                              REPORT)}
        return code, out, files

    def test_the_explicit_default_is_the_omitted_option_byte_for_byte(self):
        self.assertEqual(self.outputs(), self.outputs("--entry-shape",
                                                      "bullet"))

    def test_a_bullet_run_says_nothing_about_shapes(self):
        """The shape line belongs to a `heading` read and the note to entries
        beneath a level-3 heading; this carrier has neither, so its output
        carries no line this option introduced."""
        code, out, files = self.outputs()
        self.assertEqual(code, exits.CLEAN, out)
        report = files[REPORT].decode("utf-8")
        for text in (out, report):
            self.assertNotIn("entry shape", text.lower())
            self.assertNotIn("NOTE: ", text)
            self.assertNotIn("level-3", text)
        self.assertIn("**Bullet identity:**", report)

    def test_the_bullet_reader_reads_what_it_read(self):
        """The existing reader's own figures over the existing fixture, with
        the new counters at rest."""
        read = migrate.read_carrier(LIVE_HEAD)
        self.assertEqual(read.entry_shape, migrate.ENTRY_SHAPE_BULLET)
        self.assertEqual(read.total_bullets,
                         len(read.entries) + len(read.non_entry_bullets)
                         + len(read.cut_bullets))
        self.assertEqual((read.level3_headings, read.entries_under_level3,
                          read.body_bullets), (0, 0, 0))
        self.assertFalse(any(e.heading for e in read.entries))

    def test_the_option_is_declared_with_a_closed_set_and_a_default(self):
        parse = cli.build_parser().parse_args
        self.assertEqual(parse(["migrate"]).entry_shape, "bullet")
        self.assertEqual(
            parse(["migrate", "--entry-shape", "heading"]).entry_shape,
            "heading")
        self.assertEqual(migrate.ENTRY_SHAPES, ("bullet", "heading"))
        with self.assertRaises(ValueError):
            migrate.read_carrier("# c\n", entry_shape="paragraph")


if __name__ == "__main__":
    unittest.main()
