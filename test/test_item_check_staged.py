"""`item check --staged`: the commit-time shape gate's checker half (lc-128).

WHY THESE ARMS RUN THE BINARY. The consumer is a pre-commit hook, so the
altitude the gate operates at is the process — stdin-free argv parse, the
exit code, which stream each line lands on. A unit-level arm over
`items.check_staged` would leave the plumbing the gate actually ships with
unexercised, which is the class the guard/checker devbook names.

WHAT SEPARATES A REAL BUILD FROM THE TWO NULL ONES. Every arm here that
asserts the mode works asserts a PAIR, never an exit code alone: the newly
staged break IS reported, and the pre-existing one is NOT. A build that
accepts `--staged` and writes nothing fails the first; a build that runs the
plain check under the flag — the naive non-fix — fails the second. An
exit-code assertion alone would score those three builds identically, which
is precisely the false red the devbook records for a fix that adds a flag.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLI = REPO / "plugin" / "cli" / "lifecycle"

sys.path.insert(0, str(REPO / "plugin" / "cli"))

from lifecycle_core import exits, items  # noqa: E402

#: Hooks are pointed at a path that cannot exist: a fixture repo on this
#: machine inherits a GLOBAL `core.hooksPath`, so an un-neutralised commit
#: here would run the operator's whole hook chain against a throwaway tree.
GIT_ENV = ("-c", "core.hooksPath=/nonexistent-lifecycle-test-hooks",
           "-c", "user.email=lane@invalid.example",
           "-c", "user.name=lc-128 fixture")

DECLARATION = {
    "schema": 2,
    "id-prefix": "tt",
    "closure-home": "ITEMS-DONE.md",
    "kinds": {"items": {"home": "ITEMS.md"}},
}

HEAD_CARRIER = """schema: 2

baseline: 0
added: 1
compacted: 0

## tt-1
grade: PARKED
requirement: a pre-existing shape break — record: LEDGER.md:1
goal: g
write-set: foo.py
done-criterion: d
evidence: none
blocked-by: waiting on something vague
"""

#: The same body with a NEW broken block spliced in ABOVE the old one, so
#: `tt-1`'s line number moves. The shift is the point: a line-keyed identity
#: reports the untouched block as new, and the gate then fires on work the
#: committer did not do.
STAGED_CARRIER = """schema: 2
baseline: 0
added: 2
compacted: 0

## tt-2
grade: PARKED
requirement: a NEWLY staged shape break — record: LEDGER.md:2
goal: g
write-set: bar.py
done-criterion: d
evidence: none
blocked-by: some prose nobody can re-evaluate

## tt-1
grade: PARKED
requirement: a pre-existing shape break — record: LEDGER.md:1
goal: g
write-set: foo.py
done-criterion: d
evidence: none
blocked-by: waiting on something vague
"""

EMPTY_DONE = "schema: 2\n"


class Fixture:
    """A throwaway git repo carrying a declaration and the two carriers."""

    def __init__(self, td, *, carrier=HEAD_CARRIER, done=EMPTY_DONE,
                 commit=True):
        self.path = Path(td)
        (self.path / ".claude").mkdir()
        (self.path / ".claude" / "lifecycle.json").write_text(
            json.dumps(DECLARATION), encoding="utf-8")
        self.git("init", "-q")
        if carrier is not None:
            self.write("ITEMS.md", carrier)
        if done is not None:
            self.write("ITEMS-DONE.md", done)
        if commit:
            self.git("add", "-A")
            self.git("commit", "-qm", "fixture HEAD")

    def git(self, *argv):
        return subprocess.run(("git", "-C", str(self.path)) + GIT_ENV + argv,
                              capture_output=True, text=True, timeout=30)

    def write(self, name, text):
        (self.path / name).write_text(text, encoding="utf-8")

    def stage(self, name, text):
        self.write(name, text)
        self.git("add", name)

    def check(self, *flags):
        """`(code, stdout, stderr)` for the real binary over this repo."""
        p = subprocess.run(
            [sys.executable, str(CLI), "--repo", str(self.path),
             "item", "check", *flags],
            capture_output=True, text=True, timeout=60)
        return p.returncode, p.stdout, p.stderr


def finding_lines(stdout):
    """Only the `FINDING [...]` entries, each on its own line.

    Asserted over these rather than over the whole report: a substring test
    against the full text passes on any report carrying the token anywhere,
    including inside a summary count or a quoted block body.
    """
    return [ln for ln in stdout.splitlines() if ln.startswith("FINDING [")]


class TheDefectTheModeExistsFor(unittest.TestCase):
    """The plain check cannot separate a new break from a carried one.

    This is the red-first arm's subject, kept as a MUST-NOT-MOVE assertion:
    the plain path is unchanged by this item, and an arm that started
    passing here would mean the staged mode had leaked into it.
    """

    def test_plain_check_reports_both_undifferentiated(self):
        with tempfile.TemporaryDirectory(prefix="lc128-") as td:
            fx = Fixture(td)
            fx.stage("ITEMS.md", STAGED_CARRIER)
            code, stdout, _err = fx.check()
            lines = finding_lines(stdout)
            self.assertEqual(code, exits.FINDING, stdout)
            self.assertEqual(len(lines), 2, stdout)
            self.assertTrue(any("'tt-1'" in ln for ln in lines), stdout)
            self.assertTrue(any("'tt-2'" in ln for ln in lines), stdout)


class StagedBreakIsReportedAndCarriedOnesAreNot(unittest.TestCase):
    """Arm (a): exit 2, the new block quoted, the pre-existing one silent."""

    def _run(self):
        with tempfile.TemporaryDirectory(prefix="lc128-") as td:
            fx = Fixture(td)
            fx.stage("ITEMS.md", STAGED_CARRIER)
            return fx.check("--staged")

    def test_exit_is_finding(self):
        code, stdout, _err = self._run()
        self.assertEqual(code, exits.FINDING, stdout)

    def test_only_the_new_block_is_reported(self):
        _code, stdout, _err = self._run()
        lines = finding_lines(stdout)
        self.assertEqual(len(lines), 1, stdout)
        self.assertIn("'tt-2'", lines[0])
        # THE PAIR. Without this conjunct the arm passes against a build
        # that runs the plain check under the flag and changes nothing.
        self.assertNotIn("'tt-1'", lines[0])

    def test_the_pre_existing_count_is_printed_not_the_body(self):
        _code, stdout, _err = self._run()
        counts = [ln for ln in stdout.splitlines()
                  if ln.startswith("staged: ")]
        self.assertEqual(len(counts), 1, stdout)
        self.assertIn("1 NEW shape finding(s)", counts[0])
        self.assertIn("1 pre-existing finding(s)", counts[0])

    def test_the_new_block_is_quoted(self):
        _code, stdout, _err = self._run()
        quoted = [ln for ln in stdout.splitlines() if ln.startswith("    | ")]
        self.assertIn("    | ## tt-2", quoted)
        self.assertIn("    | blocked-by: some prose nobody can re-evaluate",
                      quoted)
        self.assertNotIn("    | ## tt-1", quoted)


class AnEditElsewhereIsClean(unittest.TestCase):
    """Arm (b): the finding sits at HEAD, the staged edit is somewhere else."""

    def test_exit_clean_with_the_carried_count_named(self):
        with tempfile.TemporaryDirectory(prefix="lc128-") as td:
            fx = Fixture(td)
            fx.stage("ITEMS.md", HEAD_CARRIER.replace("added: 1", "added: 2")
                     + """
## tt-5
grade: NEW
requirement: a clean block — record: LEDGER.md:5
goal: g
write-set: baz.py
done-criterion: d
evidence: none
blocked-by: NONE
""")
            code, stdout, _err = fx.check("--staged")
            self.assertEqual(code, exits.CLEAN, stdout)
            self.assertEqual(finding_lines(stdout), [], stdout)
            self.assertIn("1 pre-existing finding(s)", stdout)


class NothingStagedSaysSo(unittest.TestCase):
    """Arm (d): a clean answer about this commit, never a could-not-verify."""

    def test_exit_clean_and_the_line_names_the_carriers(self):
        with tempfile.TemporaryDirectory(prefix="lc128-") as td:
            fx = Fixture(td)
            code, stdout, _err = fx.check("--staged")
            self.assertEqual(code, exits.CLEAN, stdout)
            self.assertIn("nothing staged for the carriers", stdout)
            self.assertIn("ITEMS.md", stdout)
            self.assertIn("ITEMS-DONE.md", stdout)


class UnreadableCarrierIsTheThirdAnswer(unittest.TestCase):
    """Arm (c): declared and absent from both index and HEAD — exit 3."""

    def test_exit_three_and_stdout_names_what_was_missing(self):
        # lc-132: COULD NOT VERIFY moves to out() — one home for the
        # message, never both streams. The subject (exit 3, the missing
        # carriers named) is unchanged; only the stream moves.
        with tempfile.TemporaryDirectory(prefix="lc128-") as td:
            fx = Fixture(td, carrier=None, done=None, commit=False)
            fx.git("add", "-A")
            fx.git("commit", "-qm", "declaration only")
            code, stdout, stderr = fx.check("--staged")
            self.assertEqual(code, exits.COULD_NOT_VERIFY, stdout + stderr)
            self.assertIn("COULD NOT VERIFY", stdout)
            self.assertIn("ITEMS.md", stdout)
            self.assertIn("ITEMS-DONE.md", stdout)
            self.assertNotIn("COULD NOT VERIFY", stderr)
            self.assertEqual(finding_lines(stdout), [], stdout)

    def test_the_counts_name_how_much_they_cover(self):
        """A bare `0 pre-existing` over an ungraded carrier is a pass-shaped
        number, which law 1 forbids outright."""
        with tempfile.TemporaryDirectory(prefix="lc128-") as td:
            fx = Fixture(td, carrier=None, done=None, commit=False)
            fx.git("add", "-A")
            fx.git("commit", "-qm", "declaration only")
            _code, stdout, _err = fx.check("--staged")
            self.assertIn("Counted over 0 of 2 declared carrier(s)", stdout)


class ACarrierStagedAsNewIsNotUnverifiable(unittest.TestCase):
    """Absent at HEAD but staged as a new file: every finding in it is new."""

    def test_every_finding_is_new_and_the_exit_is_a_finding(self):
        with tempfile.TemporaryDirectory(prefix="lc128-") as td:
            fx = Fixture(td, carrier=None, done=None, commit=False)
            fx.git("add", "-A")
            fx.git("commit", "-qm", "declaration only")
            fx.stage("ITEMS.md", HEAD_CARRIER)
            fx.stage("ITEMS-DONE.md", EMPTY_DONE)
            code, stdout, stderr = fx.check("--staged")
            self.assertEqual(code, exits.FINDING, stdout + stderr)
            lines = finding_lines(stdout)
            self.assertEqual(len(lines), 1, stdout)
            self.assertIn("'tt-1'", lines[0])
            self.assertIn("Counted over 2 of 2 declared carrier(s)", stdout)


class AStagedDeletionIsNotClean(unittest.TestCase):
    """A carrier staged for deletion has no staged body to grade."""

    def test_exit_three_naming_the_index_absence(self):
        # lc-132: same subject (exit 3, the index-absence named); only the
        # stream moves, from err()/stderr to out()/stdout.
        with tempfile.TemporaryDirectory(prefix="lc128-") as td:
            fx = Fixture(td)
            fx.git("rm", "-q", "--cached", "ITEMS.md")
            code, stdout, stderr = fx.check("--staged")
            self.assertEqual(code, exits.COULD_NOT_VERIFY, stdout + stderr)
            self.assertIn("resolves at HEAD but not in the index", stdout)
            self.assertNotIn("resolves at HEAD but not in the index", stderr)


class ANewlyIntroducedCouldNotVerifyIsNotClean(unittest.TestCase):
    """The hole a finding-set diff alone would leave.

    An unclassifiable grade word prints a census line, never a `FINDING`, so
    a gate reading only the finding set reports CLEAN over a staged edit the
    check could not classify — a finding and an unreadable input sharing an
    exit code, which is the one thing law 1 names.
    """

    def test_exit_three_when_the_staged_body_cannot_be_classified(self):
        # lc-132: same subject (exit 3, the unclassifiable grade named);
        # only the stream moves, from err()/stderr to out()/stdout.
        with tempfile.TemporaryDirectory(prefix="lc128-") as td:
            fx = Fixture(td)
            fx.stage("ITEMS.md",
                     HEAD_CARRIER.replace("grade: PARKED", "grade: BOGUSWORD"))
            code, stdout, stderr = fx.check("--staged")
            self.assertEqual(finding_lines(stdout), [], stdout)
            self.assertEqual(code, exits.COULD_NOT_VERIFY, stdout + stderr)
            self.assertIn("could not classify something this edit introduced",
                          stdout)
            self.assertNotIn("could not classify something this edit introduced",
                             stderr)


class FindingIdentity(unittest.TestCase):
    """What makes two findings the same finding across a staged edit."""

    def _f(self, line, msg, ident):
        return items.Finding("row", "ITEMS.md", line, msg, ident)

    def test_the_line_number_is_not_in_it(self):
        a = self._f(6, "block 'tt-1' is PARKED", "tt-1")
        b = self._f(415, "block 'tt-1' is PARKED", "tt-1")
        self.assertEqual(a.identity("ITEMS.md"), b.identity("ITEMS.md"))

    def test_digits_in_the_message_are_normalized(self):
        a = self._f(6, "head line 6 is not `key: value`", None)
        b = self._f(9, "head line 9 is not `key: value`", None)
        self.assertEqual(a.identity("ITEMS.md"), b.identity("ITEMS.md"))

    def test_the_ident_discriminates_two_blocks_with_one_defect(self):
        """Without the ident these two collapse: the normalized messages are
        equal once the digits inside the idents are replaced."""
        a = self._f(6, "block 'tt-1' is PARKED", "tt-1")
        b = self._f(6, "block 'tt-2' is PARKED", "tt-2")
        self.assertNotEqual(a.identity("ITEMS.md"), b.identity("ITEMS.md"))

    def test_the_carrier_path_discriminates(self):
        a = self._f(6, "block 'tt-1' is PARKED", "tt-1")
        self.assertNotEqual(a.identity("ITEMS.md"),
                            a.identity("ITEMS-DONE.md"))


class TheRefactorChangedNothingThePlainCheckPrints(unittest.TestCase):
    """`collect=` and `text=` are handles, not a new rendering.

    The finding line is built by `Finding.render()` now; this pins that the
    printed form still matches what the carrier check has always emitted,
    since every existing consumer — and dotfiles' 23 carried findings —
    reads that shape.
    """

    def test_the_rendered_line_matches_the_collected_finding(self):
        buf = []
        collected = []
        items.check_file(Path("ITEMS.md"), buf.append, prefix="tt",
                         text=HEAD_CARRIER, collect=collected)
        lines = finding_lines("\n".join(buf))
        self.assertEqual(len(collected), 1, buf)
        self.assertEqual(lines, [collected[0].render()])
        self.assertEqual(collected[0].row, "parked_without_typed_blocker")
        self.assertEqual(collected[0].ident, "tt-1")
        self.assertEqual(collected[0].name, "ITEMS.md")

    def test_text_overrides_the_path_without_touching_disk(self):
        """`text=` is read instead of the path, which need not exist."""
        buf = []
        code = items.check_file(Path("/nonexistent/ITEMS.md"), buf.append,
                                prefix="tt", text="schema: 2\n")
        self.assertEqual(code, exits.CLEAN, buf)
        self.assertNotIn("COULD NOT VERIFY", "\n".join(buf))


class OwningIdent(unittest.TestCase):
    """A finding's block: the last block starting at or above its line."""

    def test_a_head_finding_belongs_to_no_block(self):
        parsed = items.parse(HEAD_CARRIER)
        self.assertIsNone(items._owning_ident(parsed, 1))

    def test_a_finding_inside_a_block_takes_its_ident(self):
        parsed = items.parse(HEAD_CARRIER)
        self.assertEqual(items._owning_ident(parsed, 12), "tt-1")


if __name__ == "__main__":
    unittest.main()
