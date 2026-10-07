"""lc-332 — a re-typed blocker leaves a block `item check` reads CLEAN.

`item amend` re-typing a blocker clears the conditional slot that is legal
only beside the OLD blocker type (`not-derivable:` beside a decision). It
cleared the base line and left an earlier `amended-not-derivable:` line
behind: an amendment with nothing to supersede, which the shape check
refuses as "an addition wearing a correction's clothes". So the tool's own
verb wrote a block its own check rejects.

Measured on the live carrier 2026-10-07 (lc-154, not committed, restored):
releasing a parked item from a decision blocker to NONE gave
`FINDING [item_shape] ... 'amended-not-derivable' ... amends a slot the block
does not carry`.

THE PAIR. The red arm amends the conditional slot once and then re-types;
the control re-types a block whose conditional slot was never amended, which
was clean before the repair and must stay so.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, exits  # noqa: E402
from lifecycle_core import refusals as R  # noqa: E402


def run(repo: Path, *argv):
    here = os.getcwd()
    buf = io.StringIO()
    try:
        os.chdir(str(repo))
        with redirect_stdout(buf):
            try:
                code = cli.main(["--repo", str(repo)] + list(argv))
            except SystemExit as exc:
                code = exc.code
    finally:
        os.chdir(here)
    return code, buf.getvalue()


ADD = ["item", "add",
       "--requirement", "the harvest timer double-fires — docs/x.md",
       "--goal", "mitigate",
       "--write-set", "tools/thing.py",
       "--done-criterion", "the check goes red on the defect and green after",
       "--evidence", "MEASURED here: two fires in one minute",
       "--blocked-by", "decision which of the two timers is the owner",
       "--not-derivable", "searched the ledger for timer: no line decides it",
       "--join", "new", "--absence", "a decision"]


class AReTypedBlockerLeavesACleanBlock(unittest.TestCase):

    def _repo(self):
        r = R._Repo()
        self.addCleanup(r.close)
        code, out = run(r.dir, *ADD)
        self.assertEqual(code, exits.CLEAN, out)
        return r

    def _block(self, r):
        return (r.dir / "ITEMS.md").read_text(encoding="utf-8")

    def test_an_AMENDED_conditional_slot_is_cleared_with_its_base(self):
        r = self._repo()
        code, out = run(r.dir, "item", "amend", "xx-1",
                        "--not-derivable", "looked again: still no line",
                        "--reason", "second search")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("amended-not-derivable:", self._block(r))

        code, out = run(r.dir, "item", "amend", "xx-1",
                        "--blocked-by", "NONE", "--reason", "decided")
        self.assertEqual(code, exits.CLEAN, out)
        text = self._block(r)
        self.assertNotIn("not-derivable:", text,
                         "a line legal only beside a decision blocker "
                         "survived the re-type away from one")
        self.assertIn("amended-blocked-by:", text)

        code, out = run(r.dir, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("[item_shape]", out)

    def test_CONTROL_an_unamended_conditional_slot_was_and_stays_clean(self):
        r = self._repo()
        code, out = run(r.dir, "item", "amend", "xx-1",
                        "--blocked-by", "NONE", "--reason", "decided")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("not-derivable:", self._block(r))
        code, out = run(r.dir, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)

    def test_the_record_of_the_decision_itself_is_kept(self):
        """Only the conditional annotation goes: the superseded blocker line
        and every other amendment stay verbatim."""
        r = self._repo()
        run(r.dir, "item", "amend", "xx-1",
            "--not-derivable", "looked again: still no line",
            "--reason", "second search")
        run(r.dir, "item", "amend", "xx-1",
            "--blocked-by", "NONE", "--reason", "decided")
        text = self._block(r)
        self.assertIn("blocked-by: decision which of the two timers", text)
        self.assertIn("amend-reason:", text)


class TheCommitGateAcceptsThatClear(unittest.TestCase):
    """The other half, which the verb arms cannot see: their scratch repos
    run with hooks off, and it is the commit gate that reads the removed
    lines. Measured on the live carrier 2026-10-07: with the verb repaired,
    its own commit was refused (`live_block_line_removed`) over the
    `amended-not-derivable:` line it had just cleared."""

    def _texts(self, r):
        head = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
        return head

    def _amended(self):
        r = R._Repo()
        self.addCleanup(r.close)
        run(r.dir, *ADD)
        run(r.dir, "item", "amend", "xx-1",
            "--not-derivable", "looked again: still no line",
            "--reason", "second search")
        return r, self._texts(r)

    def test_the_amended_line_cleared_by_a_RETYPE_is_exempt(self):
        from lifecycle_core import items
        r, head = self._amended()
        run(r.dir, "item", "amend", "xx-1",
            "--blocked-by", "NONE", "--reason", "decided")
        res = items.removed_live_lines(head, self._texts(r), "xx")
        self.assertEqual(res.removed, [], res.removed)
        self.assertEqual(res.exempt_retyped, 2)

    def test_CONTROL_the_same_line_removed_WITHOUT_a_retype_is_reported(self):
        from lifecycle_core import items
        _r, head = self._amended()
        staged = "\n".join(ln for ln in head.split("\n")
                           if not ln.startswith("amended-not-derivable:"))
        self.assertNotEqual(staged, head)
        res = items.removed_live_lines(head, staged, "xx")
        self.assertEqual([ident for ident, _k in res.removed], ["xx-1"])


if __name__ == "__main__":
    unittest.main()
