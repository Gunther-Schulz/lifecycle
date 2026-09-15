"""`item compact` — the done body's declared exit, exercised end to end.

WHAT THE REFUSAL ROW DOES NOT COVER. `refusals.py` proves the refusal FIRES
on its firing input and stays quiet on its control. These are the obligations
whose failure is SILENT: a record that resolves to the wrong text, a pin that
moves, an identity that stops balancing the moment its right-hand side is
used for the first time, and a refusal that refuses while having already
written something.

THE RECOVERY IS ASSERTED BYTE-FOR-BYTE, OUT OF GIT, and that is the whole
criterion of lc-47: the body may leave the carrier only because
`git cat-file -p <blob>` gives it back exactly. A test asserting that the
ledger line merely CONTAINS a sha would pass against a record pointing at any
blob in the repo — a match over rendered text standing in for a comparison of
bodies.

THE PIN IS A BLOB AND THE HAZARD IS MEASURED ELSEWHERE. The sibling repo
pinned a REVISION for 318 line-anchored citations and 313 of them landed on
the wrong entry with nothing failing, because a line number always resolves.
`ThePinIsTheVintageBlob` below is that hazard turned into an arm: after a
LATER close rewrites the done home, the pinned blob still yields the body and
`HEAD:ITEMS-DONE.md` no longer does — which is the difference a revision pin
would have erased.
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

from lifecycle_core import cli, exits, items, retire  # noqa: E402
from lifecycle_core.refusals import (  # noqa: E402
    EMPTY_DONE, GOOD_FULL_DECLARATION, SEED_ITEMS)

#: A closure reason long enough to BE the mass this verb exists to move: the
#: desk measured `closed-reason` at a median 1067 characters over the real
#: done home, and a fixture reason of four words would let a compaction that
#: silently truncated its record still pass.
REASON = ("the checker went red on the real defect and green after it, with "
          "the arrangement recorded: which side was old, where the "
          "expectation came from, and the baseline green first")

ADD = ("item", "add",
       "--requirement", "the serving config is read from defaults — x.md",
       "--goal", "verify", "--write-set", "tools/replay.mjs",
       "--done-criterion", "the gate reads what is serving",
       "--evidence", "none yet", "--hunks", "4",
       "--absence", "the decision belongs to a desk this session is not")


def build(items_text=SEED_ITEMS, done_text=EMPTY_DONE) -> Path:
    """A real git work tree — `git` is the instrument under test here, so a
    fixture without a history would answer about nothing."""
    d = Path(tempfile.mkdtemp(prefix="lifecycle-compact-"))
    run = lambda *a: subprocess.run(a, cwd=str(d), capture_output=True,  # noqa: E731
                                    text=True)
    run("git", "init", "-q", "-b", "main")
    run("git", "config", "core.hooksPath", str(d / ".nohooks"))
    run("git", "config", "user.email", "compact@lifecycle.invalid")
    run("git", "config", "user.name", "compact test")
    (d / ".claude").mkdir()
    (d / ".claude" / "lifecycle.json").write_text(
        json.dumps(GOOD_FULL_DECLARATION), encoding="utf-8")
    (d / "LAWS.md").write_text("law\n", encoding="utf-8")
    (d / ".gitignore").write_text("__pycache__/\n*.py[co]\n*.lock\n",
                                  encoding="utf-8")
    (d / "ITEMS.md").write_text(items_text, encoding="utf-8")
    (d / "ITEMS-DONE.md").write_text(done_text, encoding="utf-8")
    (d / "LEDGER.md").write_text("schema: 1\n", encoding="utf-8")
    run("git", "add", "-A")
    run("git", "commit", "-qm", "seed")
    return d


def run_cli(repo: Path, *argv):
    """One invocation, answering with the code the PROCESS would answer with.

    `SystemExit` IS CAUGHT HERE, and it is not a convenience: a usage error is
    the one answer `cli.main` delivers by raising rather than returning
    (cli.py:390, "UNREADABLE INPUT, not a finding: exit 3"), and the entry
    point turns it into the process's exit code. An in-process caller that let
    it propagate would turn the very answer this file's CLI-surface arm is
    about — a verb the surface does not carry — into a test ERROR, which
    proves only that the code is new and scores identically against a build
    that carries the verb and does nothing.
    """
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            code = cli.main(["--repo", str(repo)] + list(argv))
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else exits.COULD_NOT_VERIFY
    return code, buf.getvalue()


def git(repo: Path, *argv) -> str:
    p = subprocess.run(["git", "-C", str(repo), *argv], capture_output=True,
                       text=True)
    return p.stdout


def blob_in(out: str) -> str:
    """The 40-hex blob the compaction's own output named.

    READ OFF THE RECORD, never recomputed here: a test that resolved the pin
    itself would be comparing the code against a second implementation of the
    same idea, and both could be wrong the same way.
    """
    for word in out.replace(";", " ").split():
        if retire._BLOB_SHA.match(word):
            return word
    raise AssertionError(f"no 40-hex blob in the compaction's output: {out!r}")


class TheRecordResolvesBackOutOfGit(unittest.TestCase):

    def test_the_compacted_body_comes_back_BYTE_FOR_BYTE_at_the_pin(self):
        """lc-47's criterion, as its own arm.

        Captured BEFORE the compaction and compared after — not re-derived
        from the compacted state, which would have nothing left to compare.
        """
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        ref = git(d, "rev-parse", "HEAD").strip()
        code, out = run_cli(d, "item", "close", "xx-1", "--reason", REASON,
                            "--ref", ref)
        self.assertEqual(code, exits.CLEAN, out)

        before = items.replace_body(
            (d / "ITEMS-DONE.md").read_text(encoding="utf-8"), "xx-1")[1]
        self.assertIsNotNone(before, "the fixture never closed anything")
        self.assertIn("closed-reason:", before)
        self.assertIn("closed-ref:", before)

        code, out = run_cli(d, "item", "compact", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)

        blob = blob_in(out)
        recovered = items.replace_body(
            git(d, "cat-file", "-p", blob), "xx-1")[1]
        self.assertEqual(recovered, before, "the record does not resolve to "
                                            "the text that was removed")

        # AND THE CARRIER ACTUALLY SHRANK. Without this the arm above passes
        # over a verb that wrote a record and removed nothing.
        self.assertNotIn("## xx-1",
                         (d / "ITEMS-DONE.md").read_text(encoding="utf-8"))

    def test_the_record_names_the_id_the_ref_and_the_blob(self):
        """The three fields lc-47's answer names, each asserted on the LEDGER
        LINE itself rather than on the run's prose — the line is what a later
        reader has."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        ref = git(d, "rev-parse", "HEAD").strip()
        run_cli(d, "item", "close", "xx-1", "--reason", REASON, "--ref", ref)
        code, out = run_cli(d, "item", "compact", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        blob = blob_in(out)

        lines = [ln for ln in
                 (d / "LEDGER.md").read_text(encoding="utf-8").split("\n")
                 if ln.startswith("decision:") and "xx-1" in ln]
        self.assertEqual(len(lines), 1, "the record is not exactly one line")
        line = lines[0]
        self.assertIn("xx-1", line)
        self.assertIn(ref, line)
        self.assertIn(blob, line)
        # The line must be one the ledger's OWN parser reads back, or the
        # record is a line nobody can classify — the third answer, written by
        # the tool itself.
        from lifecycle_core import ledger
        self.assertIsNotNone(ledger.parse_line(line), line)

    def test_a_body_with_NO_closed_ref_is_compacted_and_the_absence_SPOKEN(self):
        """A closure legitimately has no ref. The blob is what makes the body
        recoverable, so the compaction proceeds — and says which field is
        empty rather than writing a record whose reader cannot tell an absent
        ref from a lost one."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        run_cli(d, "item", "close", "xx-1", "--reason", REASON)
        code, out = run_cli(d, "item", "compact", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn(retire.NO_CLOSED_REF, out)
        self.assertIn(retire.NO_CLOSED_REF,
                      (d / "LEDGER.md").read_text(encoding="utf-8"))


class ThePinIsTheVintageBlob(unittest.TestCase):

    def test_a_LATER_commit_does_not_move_what_the_record_resolves_to(self):
        """The sibling repo's measured hazard, as an arm.

        A record pinning `HEAD:ITEMS-DONE.md` would resolve, after the next
        close, to a file this body is no longer in — and nothing would fail,
        which is what makes it worse than pinning nothing. The second half of
        this arm is the discriminator: HEAD's blob must have MOVED, or the
        first half passes in a repo where no pin could have gone wrong.
        """
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        # THE SECOND ITEM IS ADMITTED FIRST, and the reason is a measured
        # property rather than fixture taste: a compacted id leaves BOTH
        # homes, so the allocator — which returns the LOWEST unused n — mints
        # `xx-1` again afterwards (`migrate.py`'s own note says so). Adding
        # after the compaction would have this arm close a body that is not
        # the one it thinks it is.
        code, out = run_cli(d, *ADD)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("xx-2", out)

        run_cli(d, "item", "close", "xx-1", "--reason", REASON)
        before = items.replace_body(
            (d / "ITEMS-DONE.md").read_text(encoding="utf-8"), "xx-1")[1]
        code, out = run_cli(d, "item", "compact", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        blob = blob_in(out)

        code, out = run_cli(d, "item", "close", "xx-2", "--reason", REASON)
        self.assertEqual(code, exits.CLEAN, out)

        head_blob = git(d, "rev-parse", "HEAD:ITEMS-DONE.md").strip()
        self.assertNotEqual(head_blob, blob, "the done home did not change, "
                                             "so this arm could not tell a "
                                             "blob pin from a revision pin")
        self.assertNotIn("## xx-1", git(d, "cat-file", "-p", head_blob),
                         "xx-1 is still at HEAD, so the arm proves nothing")
        self.assertEqual(
            items.replace_body(git(d, "cat-file", "-p", blob), "xx-1")[1],
            before, "the pinned blob stopped yielding the body")


class TheIdentityStillBalances(unittest.TestCase):

    def test_conservation_is_CLEAN_with_compacted_above_zero(self):
        """The first exit that moves the identity's RIGHT-hand side.

        The line is READ rather than predicted: `item check` prints the
        arithmetic and this asserts on what it printed, so a verb that moved
        the count without moving the body (or the reverse) fails here.
        """
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("− compacted 0", out)

        run_cli(d, "item", "close", "xx-1", "--reason", REASON)
        code, out = run_cli(d, "item", "compact", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("items 0 + done 0", out)
        self.assertIn("− compacted 1", out)
        self.assertIn("conservation: CLEAN", out)

        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("− compacted 1", out)
        self.assertIn("conservation: CLEAN", out)
        self.assertNotIn("[conservation_short]", out)
        self.assertNotIn("[conservation_surplus]", out)


class ItRefusesToStripWhatThePinDoesNotCarry(unittest.TestCase):

    def _closed_then_edited(self):
        d = build()
        run_cli(d, "item", "close", "xx-1", "--reason", REASON)
        done = d / "ITEMS-DONE.md"
        text = done.read_text(encoding="utf-8")
        planted = text.replace("red on the real defect",
                               "RED on the real defect")
        self.assertNotEqual(planted, text, "the plant's anchor is not in the "
                                           "done home, so this arm never "
                                           "carried the difference")
        done.write_text(planted, encoding="utf-8")
        self.assertIn("RED on the real defect",
                      done.read_text(encoding="utf-8"))
        return d

    def test_an_uncommitted_body_is_REFUSED_and_NOTHING_is_written(self):
        d = self._closed_then_edited()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        before_done = (d / "ITEMS-DONE.md").read_text(encoding="utf-8")
        before_items = (d / "ITEMS.md").read_text(encoding="utf-8")
        before_ledger = (d / "LEDGER.md").read_text(encoding="utf-8")

        code, out = run_cli(d, "item", "compact", "xx-1")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[compaction_would_strip]", out)
        self.assertIn("DIFFER", out)

        # THE HALF A MESSAGE CANNOT ASSERT. "It refused" is checked at the
        # files: a refusal that had already written the ledger line, or
        # already raised the count, would print exactly the same text.
        self.assertEqual((d / "ITEMS-DONE.md").read_text(encoding="utf-8"),
                         before_done)
        self.assertEqual((d / "ITEMS.md").read_text(encoding="utf-8"),
                         before_items)
        self.assertEqual((d / "LEDGER.md").read_text(encoding="utf-8"),
                         before_ledger)

    def test_the_SAME_repo_with_the_edit_COMMITTED_compacts(self):
        """The control. Without it, "the refusal fires" is indistinguishable
        from a verb that refuses everything — and the two score identically on
        the arm above."""
        d = self._closed_then_edited()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        subprocess.run(["git", "-C", str(d), "commit", "-qm", "the edit",
                        "--", "ITEMS-DONE.md"], capture_output=True, text=True)
        code, out = run_cli(d, "item", "compact", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("[compaction_would_strip]", out)

    def test_an_id_in_BOTH_homes_is_refused_as_DUPLICATE_not_compacted(self):
        """The interrupted-close window is RECOVERABLE, and compacting the
        done copy would delete the copy the documented repair keeps — while
        the head bump absorbed the surplus, so the state that made the
        interruption visible would be gone with it."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        run_cli(d, "item", "close", "xx-1", "--reason", REASON)
        # Put the live copy back: this is the state a crash between the
        # append and the delete leaves, reached here by writing the file
        # rather than by crashing, because what is under test is the READER.
        done_body = items.replace_body(
            (d / "ITEMS-DONE.md").read_text(encoding="utf-8"), "xx-1")[1]
        (d / "ITEMS.md").write_text(
            (d / "ITEMS.md").read_text(encoding="utf-8").rstrip("\n")
            + "\n\n" + done_body, encoding="utf-8")
        subprocess.run(["git", "-C", str(d), "commit", "-qm", "the window",
                        "--", "ITEMS.md"], capture_output=True, text=True)

        code, out = run_cli(d, "item", "compact", "xx-1")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[duplicate_id]", out)
        self.assertIn("delete the LIVE copy", out)
        self.assertIn("## xx-1",
                      (d / "ITEMS-DONE.md").read_text(encoding="utf-8"))

    def test_an_id_in_NEITHER_home_is_unknown_rather_than_a_usage_error(self):
        """ALSO the CLI-surface arm, and that is why it is here rather than
        in a comment: before this change the same call returned COULD NOT
        VERIFY with argparse's usage text, because the verb was not in the
        surface at all. An id the carrier does not carry must answer about
        the ID, not about the command line."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "item", "compact", "xx-404")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[unknown_item]", out)
        self.assertNotIn("usage:", out)


class TheDropRulingIsUntouched(unittest.TestCase):
    """lc-47's must-not-move, and lc-44's ruling under it.

    A DROP's record is its ledger `dropped:` line and its reason was never in
    the body. This change adds a second ledger-writing exit, so the arm that
    matters is that the DROP path still writes exactly one line and still
    writes no closure slots onto the moved body.
    """

    def test_a_drop_keeps_exactly_ONE_ledger_line_and_no_second_copy(self):
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "item", "close", "xx-1", "--drop",
                            "--reason", "overtaken by the schema wave")
        self.assertEqual(code, exits.CLEAN, out)

        lines = [ln for ln in
                 (d / "LEDGER.md").read_text(encoding="utf-8").split("\n")
                 if "xx-1" in ln]
        self.assertEqual(len(lines), 1, lines)
        self.assertTrue(lines[0].startswith("dropped:"), lines[0])
        self.assertIn("overtaken by the schema wave", lines[0])

        body = items.replace_body(
            (d / "ITEMS-DONE.md").read_text(encoding="utf-8"), "xx-1")[1]
        self.assertNotIn(f"{items.CLOSED_REASON}:", body)
        self.assertNotIn(f"{items.CLOSED_REF}:", body)


if __name__ == "__main__":
    unittest.main()
