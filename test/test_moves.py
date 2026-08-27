"""The close MOVE and the conservation identity, exercised rather than asserted.

WHAT THE REFUSAL ROWS DO NOT COVER. `refusals.py` proves each refusal FIRES
on its firing input. These are the obligations whose failure is silent: an
identity that balances across a real close rather than only in a constructed
file, and the crash window the move's ordering exists to survive.

THE INTERRUPTED MOVE IS SIMULATED AT THE REAL INSTANT. Not by writing two
copies into two files by hand — that arrangement would pass whether or not
the production code orders its writes the way the design says. Instead the
carrier's write is made to raise, midway through the real `move_to_done`, so
what is on disk afterwards is what a genuine crash would leave. The test
then asserts the two halves that matter and are easy to conflate: the state
is reported as DUPLICATE and RECOVERABLE, and it is NOT reported as loss.
A reader who takes DUPLICATE for corruption deletes a copy at random.
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
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, exits, items, verbs  # noqa: E402
from lifecycle_core.refusals import (  # noqa: E402
    EMPTY_DONE, GOOD_FULL_DECLARATION, SEED_ITEMS)


def build(items_text=SEED_ITEMS, done_text=EMPTY_DONE) -> Path:
    d = Path(tempfile.mkdtemp(prefix="lifecycle-move-"))
    run = lambda *a: subprocess.run(a, cwd=str(d), capture_output=True,  # noqa: E731
                                    text=True)
    run("git", "init", "-q", "-b", "main")
    run("git", "config", "core.hooksPath", str(d / ".nohooks"))
    run("git", "config", "user.email", "move@lifecycle.invalid")
    run("git", "config", "user.name", "move test")
    (d / ".claude").mkdir()
    (d / ".claude" / "lifecycle.json").write_text(
        json.dumps(GOOD_FULL_DECLARATION), encoding="utf-8")
    (d / "LAWS.md").write_text("law\n", encoding="utf-8")
    # The carrier lock is transient per-process state and the plugin's own
    # `.gitignore` ignores it (this repo's `.gitignore:9`). A fixture without
    # it reports an untracked `ITEMS.md.lock` that no declaring repo would
    # ever see — a fixture artefact that reads exactly like a finding.
    (d / ".gitignore").write_text("__pycache__/\n*.py[co]\n*.lock\n",
                                  encoding="utf-8")
    (d / "ITEMS.md").write_text(items_text, encoding="utf-8")
    (d / "ITEMS-DONE.md").write_text(done_text, encoding="utf-8")
    (d / "LEDGER.md").write_text("schema: 1\n", encoding="utf-8")
    run("git", "add", "-A")
    run("git", "commit", "-qm", "seed")
    return d


def run_cli(repo: Path, *argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(["--repo", str(repo)] + list(argv))
    return code, buf.getvalue()


class Conservation(unittest.TestCase):

    def test_the_identity_holds_ACROSS_a_real_close(self):
        """baseline -> add -> close -> re-run, with the numbers moving.

        A close moves a body between the two sides of `items + done`, so the
        identity must not move. Computing it once on a constructed file would
        assert arithmetic; running it either side of a real close asserts
        that the MOVE conserves.
        """
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)

        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("items 1 + done 0", out)

        code, out = run_cli(
            d, "item", "add",
            "--requirement", "the serving config is read from defaults — x.md",
            "--goal", "verify", "--write-set", "tools/replay.mjs",
            "--done-criterion", "the gate reads what is serving",
            "--evidence", "none yet", "--hunks", "4",
            "--absence", "the decision belongs to a desk this session is not")
        self.assertEqual(code, exits.CLEAN, out)

        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("items 2 + done 0", out)
        self.assertIn("baseline 1 + added 1", out)

        code, out = run_cli(d, "item", "close", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("items 1 + done 1", out)
        self.assertIn("conservation: CLEAN", out)

        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("items 1 + done 1", out)

    def test_a_body_removed_by_hand_makes_the_identity_FAIL(self):
        """The violation arm. An identity never seen to fail is not a check."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)

        text = (d / "ITEMS.md").read_text()
        kept, body = items.replace_body(text, "xx-1")
        self.assertIsNotNone(body, "the plant did not remove anything")
        (d / "ITEMS.md").write_text(kept, encoding="utf-8")

        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[conservation_short]", out)
        self.assertIn("SHORT by 1", out)
        # And NOT the surplus story: the two signs are two diagnoses with
        # two repairs, and the wrong one sends a reader hunting for a
        # duplicate that is not there.
        self.assertNotIn("[conservation_surplus]", out)


class InterruptedMove(unittest.TestCase):

    def test_a_crash_between_append_and_delete_is_DUPLICATE_not_loss(self):
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        ctx, code = verbs.context(d, GOOD_FULL_DECLARATION, lambda s: None)
        self.assertEqual(code, exits.CLEAN)

        real_write = Path.write_text

        def crash_on_the_carrier(self, *a, **kw):
            # The carrier's write is step 2. Raising here leaves step 1 done
            # and step 3 unreached — exactly the window the design names.
            if self.name == "ITEMS.md":
                raise OSError("simulated crash between the append and the "
                              "delete")
            return real_write(self, *a, **kw)

        with mock.patch.object(Path, "write_text", crash_on_the_carrier):
            with self.assertRaises(OSError):
                verbs.move_to_done(ctx, "xx-1", "DONE", "", lambda s: None)

        # The premise of everything below, pinned rather than assumed: the
        # append really happened and the delete really did not.
        self.assertIn("## xx-1", (d / "ITEMS.md").read_text())
        self.assertIn("## xx-1", (d / "ITEMS-DONE.md").read_text())

        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[duplicate_id]", out)
        self.assertIn("in BOTH homes", out)
        self.assertIn("RECOVERABLE", out)
        # The half that is easy to lose: this must NOT read as loss, and the
        # message must say which copy to remove. A reader told only
        # "duplicate" picks one at random, and half the time picks the one
        # the done home does not have.
        self.assertIn("never loss", out)
        self.assertIn("delete the LIVE copy", out)

        # AND the conservation line must tell the same story. It reports a
        # SURPLUS here, not a shortfall: this state has an extra copy, not a
        # missing body. One message for both signs is what this assertion
        # caught — it described a hand deletion over the recoverable case.
        self.assertIn("[conservation_surplus]", out)
        self.assertNotIn("[conservation_short]", out)
        self.assertIn("interrupted close", out)

    def test_the_same_repo_WITHOUT_the_interruption_is_clean(self):
        """The control. Without it, "the crash is detected" is
        indistinguishable from "this check always fires"."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "item", "close", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("move integrity: CLEAN", out)


class LedgerGate(unittest.TestCase):

    def test_the_rejected_gate_separates_none_recorded_from_no_ledger(self):
        """Two answers a gate must never share.

        "No rejections recorded" clears a re-grade. "The file I read is not
        there" does not, and rendering it as the first is the absence of
        evidence wearing a verdict's clothes.
        """
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)

        code, out = run_cli(d, "ledger", "rejected", "--for", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("NONE recorded — the gate RAN", out)

        code, out = run_cli(d, "ledger", "add", "rejected", "xx-1",
                            "--approach", "a substring match over the joined list",
                            "--why", "any longer body beginning the same way passes")
        self.assertEqual(code, exits.CLEAN, out)

        code, out = run_cli(d, "ledger", "rejected", "--for", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("1 recorded", out)
        self.assertIn("a substring match", out)

        # A rejection recorded against ANOTHER item must not surface here:
        # the reader anchors on the item SLOT, not on the id appearing
        # anywhere in the line.
        code, out = run_cli(d, "ledger", "rejected", "--for", "xx-2")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("NONE recorded", out)

        (d / "LEDGER.md").unlink()
        code, out = run_cli(d, "ledger", "rejected", "--for", "xx-1")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("COULD NOT VERIFY", out)

    def test_intake_prints_matching_rejected_lines_beside_candidates(self):
        """§3.6's other gated reader, at its real call site."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        run_cli(d, "ledger", "add", "rejected", "xx-1",
                "--approach", "widen the harvest window",
                "--why", "it hides the double fire rather than fixing it")

        code, out = run_cli(
            d, "item", "add",
            "--requirement", "the harvest timer fires twice per window",
            "--goal", "mitigate", "--write-set", "tools/harvest.mjs",
            "--done-criterion", "one fire", "--evidence", "none",
            "--hunks", "4", "--absence", "x")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[join_undisposed]", out)
        self.assertIn("candidate xx-1", out)
        self.assertIn("widen the harvest window", out)
        self.assertIn("hides the double fire", out)


class EveryJoinAnswersTheCommitQuestion(unittest.TestCase):
    """lc-25 — no join of `item add` writes the carrier silently.

    `commit_paths` was called from the supersede join alone, while
    `--no-commit` was advertised on the verb as though a commit were the
    default for every join: `new` wrote `ITEMS.md` and said nothing, and
    `merge-into` wrote nothing and said nothing about that either. The two
    are indistinguishable to a reader of the output, and the first one leaves
    a dirty carrier in a SHARED work tree — where it rides out under the next
    co-writer's pathspec commit, under their message.
    """

    def _status(self, d):
        subprocess.run(["git", "-C", str(d), "update-index", "--refresh"],
                       capture_output=True, text=True)
        return subprocess.run(["git", "-C", str(d), "status", "--porcelain"],
                              capture_output=True, text=True).stdout

    ADD = ("item", "add",
           "--requirement", "the serving config is read from defaults — x.md",
           "--goal", "verify", "--write-set", "tools/replay.mjs",
           "--done-criterion", "the gate reads what is serving",
           "--evidence", "none yet", "--hunks", "4",
           "--absence", "the decision belongs to a desk this session is not")

    def test_join_new_commits_its_own_write_and_leaves_the_tree_clean(self):
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual(self._status(d), "", "the fixture did not start clean")
        code, out = run_cli(d, *self.ADD, "--join", "new")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("committed: lifecycle: add xx-2", out)
        self.assertEqual(self._status(d), "", out)

    def test_no_commit_is_the_PAIR_that_shows_the_commit_did_it(self):
        """The same add with `--no-commit`: the carrier IS written and the
        tree IS dirty, and the run says so. Without this arm "clean tree"
        could equally mean the add wrote nothing."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, *self.ADD, "--join", "new", "--no-commit")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("NOT COMMITTED (--no-commit)", out)
        self.assertIn("M ITEMS.md", self._status(d))

    def test_the_commit_is_BY_PATHSPEC_and_leaves_a_co_writer_alone(self):
        """The half that "it commits" does not assert. The index is shared,
        so an add that staged before committing would carry a co-writer's
        work tree out under its own message — the failure `commit_paths`
        docstring names, planted here as a real second dirty file."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "LAWS.md").write_text("law\na co-writer's uncommitted line\n",
                                   encoding="utf-8")
        code, out = run_cli(d, *self.ADD, "--join", "new")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn(" M LAWS.md", self._status(d),
                      "the co-writer's file was swept into this commit")
        head = subprocess.run(
            ["git", "-C", str(d), "show", "--name-only", "--format=", "HEAD"],
            capture_output=True, text=True).stdout.split()
        self.assertEqual(head, ["ITEMS.md"], out)

    def test_the_merge_join_says_NOT_COMMITTED_rather_than_nothing(self):
        """A merge writes no file, so there is nothing to commit — but
        "printed no commit line" was true of the unrecorded write too, and a
        reader could not tell them apart."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(
            d, "item", "add",
            "--requirement", "the harvest timer double-fires on a rotated "
                             "capture again — LEDGER.md",
            "--goal", "mitigate", "--write-set", "tools/harvest.mjs",
            "--done-criterion", "one fire per window", "--evidence", "none yet",
            "--hunks", "4", "--join", "merge-into xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("NOT COMMITTED", out)
        self.assertEqual(self._status(d), "", out)

    def test_EVERY_join_answers_in_the_same_closed_vocabulary(self):
        """The enumeration, so a join added later cannot be silent by
        omission: each of the three prints `committed:` or `NOT COMMITTED`."""
        for argv in (
                list(self.ADD) + ["--join", "new"],
                ["item", "add",
                 "--requirement", "the harvest timer double-fires on a "
                                  "rotated capture again — LEDGER.md",
                 "--goal", "mitigate", "--write-set", "tools/harvest.mjs",
                 "--done-criterion", "one fire per window",
                 "--evidence", "none yet", "--hunks", "4",
                 "--join", "merge-into xx-1"],
                list(self.ADD) + ["--join", "supersede xx-1",
                                  "--reason", "the rotated capture is the "
                                              "real subject"]):
            with self.subTest(join=argv[-1]):
                d = build()
                self.addCleanup(shutil.rmtree, d, ignore_errors=True)
                code, out = run_cli(d, *argv)
                self.assertEqual(code, exits.CLEAN, out)
                self.assertTrue("committed: " in out or "NOT COMMITTED" in out,
                                out)


if __name__ == "__main__":
    unittest.main()
