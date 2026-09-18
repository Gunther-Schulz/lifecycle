"""`lifecycle verify` — mechanism #1 of the answerable-not-felt arc.

THE DEFECT CLASS, from the arc's own evidence: a verify entry at mode 644
that could never execute, and an unquoted `$t` loop where 8 of 9 checks never
ran. Both are the arc's signature — the wrong answer shaped exactly like the
right one — because a check that does not run emits nothing to notice, and a
grep for FAILED finds none in either case.

SO THE ARM THAT MATTERS IS THE THIRD ANSWER. A command that could not START
must be COULD NOT VERIFY and never CLEAN, and the pair below is what makes
that a check rather than an assertion: a passing command returns CLEAN, and
the SAME block with one unrunnable command returns COULD NOT VERIFY. Without
the second, a verb that always said CLEAN would pass the first.
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits, verify  # noqa: E402


def laws(commands: str) -> str:
    return ("# A repo\n\nSome prose.\n\n## Verify\n\n```bash\n"
            + commands + "\n```\n\nMore prose.\n")


class Args:
    def __init__(self, **kw):
        self.list = False
        self.timeout = 30
        for k, v in kw.items():
            setattr(self, k, v)


DECL = {"kinds": {"laws": {"home": "CLAUDE.md"}}}


class TheBlockIsParsed(unittest.TestCase):

    def test_commands_come_out_in_order_without_their_comments(self):
        text = laws("true   # the first\nfalse  # the second")
        self.assertEqual(verify.parse_block(text), ["true", "false"])

    def test_a_comment_only_line_is_not_a_command(self):
        """The real block wraps long notes onto their own comment lines.
        Running one would report a command nobody registered."""
        text = laws("true   # a note\n       # continued on its own line\nfalse")
        self.assertEqual(verify.parse_block(text), ["true", "false"])

    def test_no_verify_heading_yields_nothing(self):
        self.assertEqual(verify.parse_block("# A repo\n\nNo block here.\n"), [])


class TheThreeAnswers(unittest.TestCase):

    def _run(self, commands, **kw):
        d = Path(tempfile.mkdtemp(prefix="lifecycle-verify-"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "CLAUDE.md").write_text(laws(commands), encoding="utf-8")
        said = []
        code = verify.cmd_verify(Args(**kw), said.append, d, DECL)
        return code, "\n".join(said)

    def test_all_registered_commands_running_clean_is_CLEAN(self):
        code, out = self._run("true\ntrue")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("executed: 2 of 2 registered", out)

    def test_a_command_that_CANNOT_START_is_COULD_NOT_VERIFY(self):
        """THE ARM THE VERB EXISTS FOR. Not a finding, not a pass: the run is
        missing a check, so it cannot say what that check would have found."""
        code, out = self._run("true\nthis-command-does-not-exist-anywhere")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("verify_check_did_not_run", out)
        self.assertIn("DID NOT RUN", out)
        self.assertIn("executed: 1 of 2 registered", out)

    def test_a_NON_EXECUTABLE_script_is_COULD_NOT_VERIFY(self):
        """The mode-644 case, which is the arc's own measured instance."""
        d = Path(tempfile.mkdtemp(prefix="lifecycle-verify-"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        script = d / "check.sh"
        script.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        script.chmod(0o644)
        (d / "CLAUDE.md").write_text(laws("true\n./check.sh"), encoding="utf-8")
        said = []
        code = verify.cmd_verify(Args(), said.append, d, DECL)
        out = "\n".join(said)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("verify_check_did_not_run", out)

    def test_a_command_that_RAN_and_failed_is_a_FINDING(self):
        code, out = self._run("true\nfalse")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("verify_check_failed", out)
        self.assertIn("executed: 2 of 2 registered", out)

    def test_a_MISSING_check_outranks_a_failing_one(self):
        """Order matters and it is the verb's point: a run with a check
        missing cannot say what the rest would have found, so the verdict is
        could-not-verify whatever the checks that DID run returned."""
        code, out = self._run("false\nthis-command-does-not-exist-anywhere")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)

    def test_an_EMPTY_block_is_COULD_NOT_VERIFY_not_CLEAN(self):
        """A repo registering nothing must not report a clean verify — the
        0-of-0 pass is the number shaped exactly like a result."""
        d = Path(tempfile.mkdtemp(prefix="lifecycle-verify-"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "CLAUDE.md").write_text("# A repo\n\nNo verify block.\n",
                                     encoding="utf-8")
        said = []
        code = verify.cmd_verify(Args(), said.append, d, DECL)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, "\n".join(said))

    def test_a_TIMEOUT_is_DID_NOT_RUN_never_a_failure(self):
        """A timed-out command produced no verdict. Booking it as a red is
        the same error one level down as booking a check that never started
        as a pass."""
        code, out = self._run("sleep 5", timeout=1)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("timed out", out)


if __name__ == "__main__":
    unittest.main()
