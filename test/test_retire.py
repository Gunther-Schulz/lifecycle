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

import _isolation  # noqa: F401  # lc-183: before any verb runs

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
from lifecycle_core import declaration as decl  # noqa: E402
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
       "--evidence", "MEASURED none yet", "--hunks", "4",
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
        # THE SECOND ITEM IS ADMITTED FIRST, and the reason WAS a measured
        # property rather than fixture taste: a compacted id left BOTH homes,
        # so the allocator — which returns the LOWEST unused n — minted `xx-1`
        # again afterwards, and adding after the compaction would have had
        # this arm close a body that is not the one it thinks it is. lc-148
        # closed that hole (the compaction record is now a home the allocator
        # reads, and `ACompactedIdIsNeverReIssued` below is where that is
        # asserted); the ordering stays because this arm is about the PIN and
        # should not re-derive its subject from a behaviour it does not test.
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


class ACompactedIdIsNeverReIssued(unittest.TestCase):
    """lc-148, at the altitude the defect lives at.

    THE WALK, NOT A UNIT CALL. `next_ident` was never wrong about the homes it
    was GIVEN, so a unit arm on it passed throughout; what stopped being true
    was its stated premise — every home is read — the day a verb started
    taking bodies out of every home. The defect is only visible where the
    caller assembles the homes, which is `item add`.

    MEASURED BEFORE THE FIX, in this fixture: close xx-1, compact xx-1, then
    `item add` printed `added xx-1 [READY] → ITEMS.md` while the ledger
    already carried the compaction record, and `item check` reported CLEAN
    throughout — the id back in circulation with nothing failing.
    """

    def _closed_and_compacted(self) -> Path:
        d = build()
        code, out = run_cli(d, "item", "close", "xx-1", "--reason", REASON)
        self.assertEqual(code, exits.CLEAN, out)
        code, out = run_cli(d, "item", "compact", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn(retire.compaction_question("xx-1"),
                      (d / "LEDGER.md").read_text(encoding="utf-8"),
                      "the fixture never recorded a compaction, so this arm "
                      "could not have seen the defect")
        return d

    def test_item_add_after_a_compaction_does_not_re_issue_the_id(self):
        d = self._closed_and_compacted()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, *ADD)
        self.assertEqual(code, exits.CLEAN, out)
        # THE CARRIER, never the message: "added xx-2" is a summary, and a run
        # that printed it while writing a block under another id would satisfy
        # a text match.
        parsed = items.parse((d / "ITEMS.md").read_text(encoding="utf-8"))
        self.assertEqual([it.ident for it in parsed.items], ["xx-2"])
        # And the record the allocator reads is the SAME line recovery reads —
        # untouched by having been read.
        self.assertIn(retire.compaction_question("xx-1"),
                      (d / "LEDGER.md").read_text(encoding="utf-8"))

    def test_the_SUPERSEDE_join_allocates_past_the_compacted_id_too(self):
        """The allocator's second door. An arm on `new` alone certifies one
        of the two call sites, and the other one writes a body just the
        same."""
        d = self._closed_and_compacted()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, *ADD)
        self.assertEqual(code, exits.CLEAN, out)
        code, out = run_cli(d, *(ADD + ("--join", "supersede xx-2",
                                        "--reason", REASON)))
        self.assertEqual(code, exits.CLEAN, out)
        parsed = items.parse((d / "ITEMS.md").read_text(encoding="utf-8"))
        self.assertEqual([it.ident for it in parsed.items], ["xx-3"])
        self.assertIn("## xx-2",
                      (d / "ITEMS-DONE.md").read_text(encoding="utf-8"))

    def test_an_ORDINARY_close_keeps_the_id_out_of_circulation_as_before(self):
        """MUST-NOT-MOVE: ids are immutable across moves, which is the
        property the allocator's docstring was always about."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "item", "close", "xx-1", "--reason", REASON)
        self.assertEqual(code, exits.CLEAN, out)
        code, out = run_cli(d, *ADD)
        self.assertEqual(code, exits.CLEAN, out)
        parsed = items.parse((d / "ITEMS.md").read_text(encoding="utf-8"))
        self.assertEqual([it.ident for it in parsed.items], ["xx-2"])

    def test_a_decision_line_that_is_NOT_a_compaction_consumes_no_id(self):
        """The negative half of the pair, and the one that fails if the
        recogniser matches on an id appearing anywhere in a decision rather
        than on the compaction sentence it was written with."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        with open(d / "LEDGER.md", "a", encoding="utf-8") as fh:
            fh.write("decision: whether xx-2 belongs in this wave → yes\n")
        code, out = run_cli(d, *ADD)
        self.assertEqual(code, exits.CLEAN, out)
        parsed = items.parse((d / "ITEMS.md").read_text(encoding="utf-8"))
        self.assertEqual([it.ident for it in parsed.items], ["xx-1", "xx-2"])

    def test_a_repo_with_NO_LEDGER_AT_ALL_still_allocates(self):
        """MUST-NOT-MOVE, and the one a reuse test alone would never catch: a
        change that made every allocation consult a missing file would pass
        the arms above while breaking every fresh repo."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "LEDGER.md").unlink()
        self.assertFalse((d / "LEDGER.md").exists())
        code, out = run_cli(d, *ADD)
        self.assertEqual(code, exits.CLEAN, out)
        parsed = items.parse((d / "ITEMS.md").read_text(encoding="utf-8"))
        self.assertEqual([it.ident for it in parsed.items], ["xx-1", "xx-2"])

    def test_a_ledger_STAMPED_ABOVE_THE_FLOOR_is_could_not_verify(self):
        """The third answer, and the difference between the two absences: an
        absent ledger proves no compaction was recorded (the verb creates the
        file), while a ledger this build refuses to parse is a home that
        EXISTS and was not read. Allocating through it would mint an id whose
        unusedness nothing established."""
        from lifecycle_core import ledger as ledger_mod
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "LEDGER.md").write_text(
            f"schema: {ledger_mod.SCHEMA_FLOOR + 1}\n", encoding="utf-8")
        before = (d / "ITEMS.md").read_text(encoding="utf-8")
        code, out = run_cli(d, *ADD)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("COULD NOT VERIFY", out)
        # NOTHING WAS WRITTEN: a refusal that had already appended the block
        # would print the same line.
        self.assertEqual((d / "ITEMS.md").read_text(encoding="utf-8"), before)


class TheCompactionRecordReadsBackAsAHome(unittest.TestCase):
    """One spelling, both directions. `compacted_ident` is
    `compaction_question` read backwards, and the pair is what keeps the
    allocator seeing what the verb wrote."""

    def test_the_recogniser_reads_back_exactly_what_the_writer_wrote(self):
        self.assertEqual(
            retire.compacted_ident(retire.compaction_question("xx-9")), "xx-9")

    def test_a_question_that_merely_STARTS_the_same_way_is_not_one(self):
        """Both ends anchored. A head-only match is a prefix test wearing an
        equality's costume, and the id it yields is whatever follows."""
        longer = retire.compaction_question("xx-9") + " eventually"
        self.assertIsNone(retire.compacted_ident(longer))
        self.assertIsNone(retire.compacted_ident("whether xx-9 is compacted"))
        self.assertIsNone(retire.compacted_ident(""))

    def test_the_home_is_built_through_the_LEDGERS_OWN_PARSER(self):
        """Read back out of `ledger.parse`, never out of a second reader over
        the same text: two parsers for one line diverge silently, and the
        divergence here puts compacted ids back into circulation."""
        from lifecycle_core import ledger as ledger_mod
        text = (f"schema: {ledger_mod.SCHEMA_FLOOR}\n"
                + ledger_mod.render("decision",
                                    {"question": retire.compaction_question("xx-4"),
                                     "answer": "ITEMS-DONE.md at blob "
                                               + "0" * 40}) + "\n"
                + ledger_mod.render("dropped",
                                    {"id": "xx-7", "reason": "overtaken"})
                + "\n")
        parsed = ledger_mod.parse(text)
        self.assertEqual(parsed.unreadable, [], "the fixture ledger does not "
                                                "parse, so this arm grades "
                                                "nothing")
        home = retire.compacted_home(parsed)
        self.assertEqual([it.ident for it in home.items], ["xx-4"])

    def test_no_ledger_is_an_EMPTY_home_rather_than_a_crash(self):
        home = retire.compacted_home(None)
        self.assertEqual(home.items, [])


class TheWalkAsksACompactedKindAboutItsExit(unittest.TestCase):
    """lc-145 — the walk reports the done-bodies kind honestly.

    TWO GATES, AND EITHER ALONE IS INERT (measured before building): the MODE
    gate returned NOT APPLICABLE for every mode but `bounded-by-exit` BEFORE
    `PERFORMED_EXITS` was ever consulted, so adding `compact` to that tuple
    changed no kind's verdict — the old-vs-new audit diff over that one line
    moved parentheticals in unrelated messages and nothing else.

    ASSERTED INSIDE THE KIND'S OWN BLOCK. The walk prints twenty-odd kinds and
    more than one of them can carry this finding, so a match over the whole
    report would pass on a run that fired for a different kind entirely.
    """

    def _block(self, out: str, name: str) -> str:
        """The one block for `name`, isolated before anything is asserted.

        Exactly one, else ABORT: zero means the walk never reached the kind
        and the assertion would be about a report that does not mention it;
        two means the assertion cannot say which one it graded.
        """
        blocks = [b for b in out.split("\nkind: ")[1:]
                  if b.split("\n", 1)[0].strip() == name]
        self.assertEqual(len(blocks), 1,
                         f"{len(blocks)} blocks for kind {name!r}; the "
                         "arrangement did not put exactly one in front of "
                         "the assertion")
        return blocks[0]

    def test_a_COMPACTED_kind_holding_bodies_with_no_compaction_FIRES(self):
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "item", "close", "xx-1", "--reason", REASON)
        self.assertEqual(code, exits.CLEAN, out)
        code, out = run_cli(d, "audit")
        block = self._block(out, "done bodies")
        self.assertIn("[kind_grew_without_exit]", block)
        self.assertIn("declares `compacted`", block)
        self.assertIn("exit events: 0 (item compact)", block)
        # THE WALK'S OWN ANSWER IS COULD NOT VERIFY BY CONSTRUCTION — the
        # staleness half needs pass history and this is the first pass — so
        # the exit code is 3 whatever the growth question found. That is
        # exactly why the roster row calls `growth_verdict` instead: a pair
        # whose plant and control both exit 3 discriminates nothing.
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)

    def test_the_SAME_kind_after_a_REAL_compaction_reads_the_EVENT(self):
        """The control, and it is the one that proves the walk reads a
        recorded event rather than an empty home: the kind still holds a body
        here, so a pass cannot come from there being nothing to grade."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, *ADD)
        self.assertEqual(code, exits.CLEAN, out)
        for ident in ("xx-1", "xx-2"):
            code, out = run_cli(d, "item", "close", ident, "--reason", REASON)
            self.assertEqual(code, exits.CLEAN, out)
        code, out = run_cli(d, "item", "compact", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)

        code, out = run_cli(d, "audit")
        block = self._block(out, "done bodies")
        self.assertIn("count:  1", block, "the kind's home is empty, so this "
                                          "arm would pass on the zero-count "
                                          "branch instead of on the event")
        self.assertIn("exit events: 1 (item compact)", block)
        self.assertIn("growth check: CLEAN — the exit has fired", block)
        self.assertNotIn("[kind_grew_without_exit]", block)

    def test_a_home_holding_NOTHING_is_CLEAN_without_claiming_a_fire(self):
        """MUST-NOT-MOVE — a repo with no done bodies still reports the kind
        CLEAN — and the message repair the widening made necessary: the
        verdict was always right and the sentence was not, because a kind
        holding nothing has had no exit fire for it.

        THE HOME IS REMOVED RATHER THAN EMPTIED, and the difference is a
        MEASURED defect in the counter that this change does not touch:
        `list_home` decides a file's notion by SHAPE, so a carrier holding no
        blocks reads as "a single file, one instance" and the kind is counted
        as holding something. That is not new here — on the build before this
        change, a repo whose `ITEMS.md` carries only its head already counted
        1 and already fired this finding for the `items` kind (measured
        2026-09-15 at 9e681e3). Reported as its own defect rather than
        silently repaired under this item, and NOT pinned here, because an arm
        asserting the miscount would enshrine it.
        """
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "ITEMS-DONE.md").unlink()
        code, out = run_cli(d, "audit")
        block = self._block(out, "done bodies")
        self.assertIn("count:  0", block)
        # THE PHRASE MOVED UNDER lc-172, THE VERDICT DID NOT. This branch must
        # still answer CLEAN and must still refuse to claim a fire — both
        # pinned below and unchanged. What lc-172 required is that the line
        # carry the DENOMINATOR proving the instrument was live, so the
        # sentence now says the home WAS examined and holds 0. The arm follows
        # the wording rather than the wording following the arm, because the
        # behaviour under test is the verdict and the refusal, not the prose.
        self.assertIn("growth check: CLEAN — the home WAS examined and holds "
                      "0 instance(s)", block)
        # AND THE DENOMINATOR IS PART OF THE CONTRACT NOW: a clean line here
        # that did not say what it examined is the shape lc-172 removes.
        self.assertIn("the path WAS resolved", block)
        # THE VERDICT LINE, not the phrase: the sentence this branch prints
        # NAMES the answer it is not giving, so a bare search for those words
        # matches the very message that refuses to claim them.
        self.assertNotIn("growth check: CLEAN — the exit has fired", block)
        self.assertNotIn("[kind_grew_without_exit]", block)

    def test_an_UNBOUNDED_WITH_REASON_kind_is_still_NOT_APPLICABLE(self):
        """MUST-NOT-MOVE, and the boundary of the widening: one mode is the
        declared opt-out and it keeps its exemption. A gate that admitted
        every mode would fire on kinds that said in their own declaration why
        growth is controlled by something else."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "audit")
        block = self._block(out, "ledger lines")
        self.assertIn("growth check: NOT APPLICABLE", block)
        self.assertIn("unbounded-with-reason", block)
        self.assertNotIn("[kind_grew_without_exit]", block)

    def test_a_BOUNDED_BY_EXIT_kinds_finding_text_is_unchanged(self):
        """MUST-NOT-MOVE: the other findings keep their exact text. The mode
        is now READ instead of restated, so this arm is what says the reading
        returns the same words for the kind the message was written for."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "audit")
        block = self._block(out, "items")
        self.assertIn("[kind_grew_without_exit]", block)
        self.assertIn("declares `bounded-by-exit`, and its exit has recorded "
                      "NOTHING", block)

    def test_compact_is_a_PERFORMED_exit_and_names_its_verb(self):
        """The second gate, pinned where it is read: a kind whose exit this
        build performs must not be answered NOT CHECKED, and the verb named
        must be the one that writes the fire-log line."""
        self.assertIn("compact", retire.PERFORMED_EXITS)
        # RE-KEYED ON (KIND, ACTION), not weakened (FF-3). The claim this
        # case makes is unchanged — a performed exit names the verb that
        # writes its fire-log line — and it is now asserted per KIND, which
        # is strictly more than the old single-tuple form said: two kinds
        # compact, by two different verbs, and an action-keyed map could not
        # express that at all.
        self.assertEqual(retire.EXIT_VERBS[("done bodies", "compact")],
                         ("item compact",))
        self.assertEqual(retire.EXIT_VERBS[("closed arcs", "compact")],
                         ("arc compact",))
        self.assertEqual(sorted(retire.EXIT_CONTROLLED_MODES),
                         sorted(m for m in decl.GROWTH_MODES
                                if m != "unbounded-with-reason"),
                         "the mode list is restated rather than derived, so a "
                         "mode added to the declaration would be exempt "
                         "silently")


if __name__ == "__main__":
    unittest.main()


class AnAbsenceClaimNamesWhatProvesTheInstrumentWasLive(unittest.TestCase):
    """lc-172 — a zero from a dead instrument and a zero from a live one.

    MEASURED, and it is why this exists: the fire log's declared home is
    `$XDG_STATE_HOME/lifecycle/fire.jsonl`; the walk did not expand the
    variable, so it searched for a literal `$XDG_STATE_HOME/…`, found
    nothing, counted 0 and reported the kind CLEAN — while the file held
    133,087,757 bytes across 1,173,626 lines. Every XDG-homed kind was
    exempt from R22's alarm, silently, and the line saying so was the most
    reassuring in the output.

    THE FIXTURE MOVED IN lc-170 AND THE CLAIM DID NOT. That item made the
    walk RESOLVE `$XDG_STATE_HOME` and the other XDG bases, which is the end
    state lc-172's could-not-verify was only the honest waypoint to — so the
    original spelling of this arm stopped being an unresolvable home and
    started being a resolvable one. What is unresolvable now is a variable
    that is unset AND has no spec default, and that is what these arms use.
    The claim under test — an unexamined population answers could-not-verify
    rather than clean — is untouched; only the instance that exercises it
    moved, because the world moved under the fixture.

    THE BOUNDARY IS DELIBERATE AND NARROW: the discriminator is whether the
    instrument SAW anything, never whether it FOUND anything. An in-tree home
    that is simply absent stays CLEAN — the walk resolved it and there is no
    file, which is data about the repo.
    """

    def _tmp(self):
        d = Path(tempfile.mkdtemp(prefix="lc172-"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    #: Unset, and not one of the four XDG bases the walk defaults — so it
    #: survives expansion with its `$` intact, which is exactly the dead
    #: instrument this class is about.
    UNRESOLVABLE = "$LIFECYCLE_NO_SUCH_BASE_DIR"

    def test_an_unexpanded_variable_home_is_could_not_verify(self):
        d = self._tmp()
        instances, note = retire.list_home(
            d, self.UNRESOLVABLE + "/lifecycle/fire.jsonl")
        self.assertIsNone(instances, note)
        self.assertIn("NOTHING was examined", note)
        self.assertIn("home_unresolvable", retire.unresolvable_line(note))

    def test_the_braced_spelling_is_caught_too(self):
        """`${VAR}` is the same unresolved home in a different costume."""
        instances, _ = retire.list_home(
            self._tmp(), "${LIFECYCLE_NO_SUCH_BASE_DIR}/x.jsonl")
        self.assertIsNone(instances)

    def test_an_absent_in_tree_home_stays_clean_and_says_it_resolved(self):
        """MUST-NOT-MOVE from the earlier item, and lc-172 does not move it."""
        instances, note = retire.list_home(self._tmp(), "ITEMS-DONE.md")
        self.assertEqual(instances, [])
        self.assertIn("the path WAS resolved", note)

    def test_a_real_population_is_counted_with_its_notion(self):
        d = self._tmp()
        (d / "ITEMS.md").write_text("schema: 2\nbaseline: 0\n", encoding="utf-8")
        instances, note = retire.list_home(d, "ITEMS.md")
        self.assertIsNotNone(instances)
        self.assertTrue(note)

    def test_a_glob_over_a_missing_directory_reports_what_it_searched(self):
        """Also CLEAN — an in-tree directory's absence is an observation —
        but the denominator must say there was nothing to match, or the zero
        is indistinguishable from a pattern that matched nothing."""
        instances, note = retire.list_home(self._tmp(), "docs/nowhere/*.md")
        self.assertEqual(instances, [])
        # PHRASE UPDATED BY lc-170, substance untouched: the note used to say
        # "in this repo" and a resolved home can now be OUTSIDE the tree, so
        # the claim that survives is that the note names the directory it
        # searched and did not find.
        self.assertIn("does not exist", note)
        self.assertIn("docs/nowhere", note)


class GrowthExitVerbsAreKindAware(unittest.TestCase):
    """The exit map keys on (KIND, ACTION), never on action alone (FF-3).

    THE TRAP THIS AVOIDS IS A ONE-WORD FIX. `arcs` declares its exit action
    as `move`, which is the same word `items` declares — so a map keyed on
    the action alone has exactly two wrong answers available and no right
    one: leave it, and an arc close is invisible so the arcs kind reads
    GREW WITHOUT AN EXIT while its exit has been firing; add `arc close` to
    the `move` tuple, and an arc close now satisfies the ITEMS kind, whose
    growth alarm then goes quiet on a carrier that genuinely stopped
    draining.

    So the pair below is both directions, and neither alone would have
    caught the other.
    """

    ARC_LOG = [{"verb": "arc close"}, {"verb": "arc close"}]
    ITEM_LOG = [{"verb": "item close"}]

    def _check(self, kind, action, count, log):
        buf = []
        code, state = retire.check_growth(kind, "bounded-by-exit", action,
                                          count, log, True, buf.append)
        return code, state, "\n".join(buf)

    def test_an_arc_close_satisfies_the_ARCS_kind(self):
        code, state, outp = self._check("arcs", "move", 2, self.ARC_LOG)
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertNotIn("kind_grew_without_exit", outp)

    def test_an_arc_close_does_NOT_satisfy_the_ITEMS_kind(self):
        """The direction a naive fix breaks: the items alarm must stay loud

        on a carrier that is not draining, whatever the arcs did."""
        code, state, outp = self._check("items", "move", 5, self.ARC_LOG)
        self.assertEqual(code, exits.FINDING, outp)
        self.assertIn("kind_grew_without_exit", outp)

    def test_an_item_close_still_satisfies_the_ITEMS_kind(self):
        """The control for both: without it the map could refuse everything

        and the case above would pass while the alarm fired on every repo."""
        code, state, outp = self._check("items", "move", 5, self.ITEM_LOG)
        self.assertEqual(code, exits.CLEAN, outp)

    def test_an_item_close_does_NOT_satisfy_the_ARCS_kind(self):
        code, state, outp = self._check("arcs", "move", 2, self.ITEM_LOG)
        self.assertEqual(code, exits.FINDING, outp)


class SurfacedVsReadInTheAudit(unittest.TestCase):
    """lc-264: the audit's per-kind surfaced-vs-read table and its answers.

    None of the three answers is a FINDING — a never-read kind is a review
    candidate (O6 §6), so the arms pin that it is LISTED and that the exit
    stays CLEAN, and that both empty states are COULD NOT VERIFY rather than
    a clean zero.
    """

    REPO = Path("/repo/under/audit")

    def setUp(self):
        import os
        self.os = os
        self.tmp = Path(tempfile.mkdtemp())
        self.old = os.environ.get("XDG_STATE_HOME")
        os.environ["XDG_STATE_HOME"] = str(self.tmp)

    def tearDown(self):
        if self.old is None:
            self.os.environ.pop("XDG_STATE_HOME", None)
        else:
            self.os.environ["XDG_STATE_HOME"] = self.old
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, *details):
        if details:
            path = retire.firelog.log_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("".join(
                json.dumps({"at": "2026-09-21T10:00:00+00:00",
                            "verb": "item check", "repo": str(self.REPO),
                            "detail": d}) + "\n" for d in details),
                encoding="utf-8")
        lines = []
        code = retire.surfacing_report(self.REPO, lines.append)
        return code, "\n".join(lines)

    def test_no_log_is_COULD_NOT_VERIFY(self):
        code, outp = self._run()
        self.assertEqual(code, exits.COULD_NOT_VERIFY, outp)
        self.assertIn("no readable fire log", outp)

    def test_no_surfacing_is_COULD_NOT_VERIFY_not_a_clean_zero(self):
        code, outp = self._run("read=items")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, outp)
        self.assertIn("no due read has been surfaced", outp)

    def test_a_never_read_kind_is_LISTED_and_the_exit_stays_CLEAN(self):
        code, outp = self._run("surfaced=items,ledger lines",
                               "close lc-1 DONE; surfaced=items", "read=items")
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertIn("2 surfacing record(s), 1 read record(s)", outp)
        ledger = [ln for ln in outp.splitlines() if "ledger lines" in ln
                  and "surfaced" in ln]
        self.assertEqual(len(ledger), 1, outp)
        self.assertIn("<- surfaced, never read", ledger[0])
        items_row = [ln for ln in outp.splitlines()
                     if ln.strip().startswith("items ")]
        self.assertEqual(len(items_row), 1, outp)
        self.assertNotIn("never read", items_row[0])
        self.assertIn("never read: 1 of 2 surfaced kind(s)", outp)
        self.assertIn("PROSE-REST", outp)
        self.assertNotIn("FINDING", outp)
