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
        self.assertIn("growth check: CLEAN — the home holds nothing", block)
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
        self.assertEqual(retire.EXIT_VERBS["compact"], ("item compact",))
        self.assertEqual(sorted(retire.EXIT_CONTROLLED_MODES),
                         sorted(m for m in decl.GROWTH_MODES
                                if m != "unbounded-with-reason"),
                         "the mode list is restated rather than derived, so a "
                         "mode added to the declaration would be exempt "
                         "silently")


if __name__ == "__main__":
    unittest.main()
