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


if __name__ == "__main__":
    unittest.main()
