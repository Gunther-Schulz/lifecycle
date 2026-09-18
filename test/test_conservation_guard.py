"""The commit-time conservation guard (lc-159 half 2).

WHAT IT PROTECTS. A truncated carrier parses clean with fewer items, so a verb
reads it, edits what it sees, and writes the short body back — turning a
recoverable truncation (the bodies are still in git) into the carrier's new
recorded truth. The guard sits at the single commit path every carrier write
already passes through.

THE PAIR THAT MAKES IT A CHECK RATHER THAN AN ASSERTION. Both arms are here
because either alone is satisfiable by a broken guard: one that always fires
passes the SHORT arm, one that never fires passes the SURPLUS arm. Only the
two together say it discriminates.

  * SHORT  -> REFUSED. A body left by a path that is not a closure.
  * SURPLUS -> ALLOWED. The ordinary cause is an INTERRUPTED CLOSE: the move
    appends to the done home before deleting from the carrier, so that window
    legitimately holds both copies. A guard failing here would fire on the
    design working as designed and block the commit that finishes the move —
    law 11's guard-fires-on-legitimate-work, which is what kills guards.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits, items, verbs  # noqa: E402
from lifecycle_core.refusals import (  # noqa: E402
    EMPTY_DONE, GOOD_FULL_DECLARATION, SEED_ITEMS)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_moves import build  # noqa: E402


class TheGuardDiscriminates(unittest.TestCase):

    def _ctx(self, d):
        ctx, code = verbs.context(d, GOOD_FULL_DECLARATION, lambda s: None)
        self.assertEqual(code, exits.CLEAN)
        return ctx

    def test_a_SHORT_carrier_is_refused_at_the_commit(self):
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        ctx = self._ctx(d)

        # Truncate the carrier the way an interrupted write would: the head
        # survives, the bodies do not.
        text = (d / "ITEMS.md").read_text()
        head = text.split("\n## ")[0]
        (d / "ITEMS.md").write_text(head + "\n", encoding="utf-8")

        said = []
        code = verbs.commit_paths(ctx, (ctx.items_path,), "would destroy it",
                                  said.append)
        blob = "\n".join(said)
        self.assertEqual(code, exits.FINDING, blob)
        self.assertIn("conservation_short", blob)
        self.assertIn("REFUSING TO COMMIT", blob)

    def test_a_SURPLUS_carrier_PASSES_the_guard(self):
        """The over-firing arm, and the one that keeps the guard alive.

        An interrupted close leaves a body in BOTH homes. That state is
        expected debris, is recoverable, and its repair needs a commit — so a
        guard refusing here would block the fix for a fault it did not cause.
        """
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        ctx = self._ctx(d)

        text = (d / "ITEMS.md").read_text()
        parsed = items.parse(text)
        body = parsed.items[0].raw if hasattr(parsed.items[0], "raw") else None
        if body is None:
            _, body = items.replace_body(text, parsed.items[0].ident)
        # Append to the done home WITHOUT deleting from the carrier: exactly
        # the window the move's own ordering creates.
        done = (d / "ITEMS-DONE.md").read_text()
        (d / "ITEMS-DONE.md").write_text(
            done.rstrip("\n") + "\n\n" + body.rstrip("\n") + "\n",
            encoding="utf-8")

        c = items.conservation(items.parse((d / "ITEMS.md").read_text()),
                               items.parse((d / "ITEMS-DONE.md").read_text()))
        self.assertFalse(c["ok"], "the fixture did not create a surplus")
        self.assertGreater(c["actual"], c["expected"],
                           "the fixture created a SHORT, not a surplus — this "
                           "arm would then be testing the other branch")

        said = []
        code = verbs.conservation_guard(ctx, (ctx.items_path,), said.append)
        blob = "\n".join(said)
        self.assertEqual(
            code, exits.CLEAN,
            "the guard refused a SURPLUS. That is an interrupted close, it is "
            f"recoverable, and its repair needs the commit: {blob}")

    def test_an_INTACT_carrier_passes_the_guard(self):
        """The baseline. Without it, the SHORT arm is indistinguishable from a
        guard that refuses everything."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        ctx = self._ctx(d)
        said = []
        code = verbs.conservation_guard(ctx, (ctx.items_path,), said.append)
        blob = "\n".join(said)
        self.assertEqual(code, exits.CLEAN, blob)
        self.assertEqual(blob, "", f"an intact carrier said something: {blob}")

    def test_a_LEDGER_only_commit_is_not_graded(self):
        """Reach: the guard is about the ITEM carrier. A ledger write does not
        move the identity and must not be made to answer for it."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        ctx = self._ctx(d)
        text = (d / "ITEMS.md").read_text()
        head = text.split("\n## ")[0]
        (d / "ITEMS.md").write_text(head + "\n", encoding="utf-8")

        said = []
        code = verbs.conservation_guard(ctx, (ctx.ledger_path,), said.append)
        self.assertEqual(
            code, exits.CLEAN, "a ledger-only commit was graded against the "
            "item carrier's identity: " + "\n".join(said))


if __name__ == "__main__":
    unittest.main()
