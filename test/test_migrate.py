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

from lifecycle_core import cli, exits, items, ledger, migrate  # noqa: E402
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
        self.assertIn("BLOCKED — in the OPERATOR's court",
                      run_cli(d, "item", "ready", "xx-1")[1])

        code, outp = run_cli(d, "ledger", "add", "decision",
                             "--question", question,
                             "--answer", "stays NEW; the desk regrades")
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertIn("UNBLOCKED — the ledger ANSWERS this decision",
                      run_cli(d, "item", "ready", "xx-1")[1])

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


if __name__ == "__main__":
    unittest.main()
