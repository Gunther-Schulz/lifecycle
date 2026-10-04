"""The goal line at the three seams: LAST, on STDERR, under a trial arm.

lc-306, design round `docs/directives/2026-10-04-lc306-delivery-round.md`.
Measured before this change: the goal line was printed first, on stdout, and
reached the session at 3 of 22 seam calls, because callers pipe a verb
through `grep` or `tail`. A refused write reached it at 71 of 75 under the
same filters, for one reason: it is the end of a short output.

Three things are pinned here.
  * PLACE: the line is the final line of the run's stderr and is not on
    stdout at all.
  * FLUSH ORDER: with both streams on ONE pipe (`2>&1`), the line is still
    last. Stdout is block-buffered into a pipe, so this holds only if
    stdout is flushed before the line is written; it is checked through a
    real child process, the only place the buffering exists.
  * ARM: the session id decides ON or OFF. OFF emits nothing and records
    what it withheld.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import hashlib
import io
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugin" / "cli"))

from lifecycle_core import cli, firelog, verbs  # noqa: E402
from lifecycle_core import refusals as R  # noqa: E402

CLI = ROOT / "plugin" / "cli" / "lifecycle"
OPEN = ("arc", "open", "freeze", "--goal", "g", "--narrowing", "eliminative")
GOAL = "goal (arc freeze): g"


def parity(session: str) -> str:
    """The arm, derived HERE from the design's sentence and not from the
    function under test: sha256 of `<session>:goal-seam`, last byte even is
    ON."""
    last = hashlib.sha256(f"{session}:goal-seam".encode()).digest()[-1]
    return "on" if last % 2 == 0 else "off"


def session_for(arm: str) -> str:
    return next(f"session-{i}" for i in range(64)
                if parity(f"session-{i}") == arm)


class Base(unittest.TestCase):
    def setUp(self):
        self.old = os.environ.get(firelog.SESSION_ENV)
        self.repo = R._Repo(declaration=R.GOOD_FULL_DECLARATION)
        self.addCleanup(self.repo.close)
        self.addCleanup(self._restore)

    def _restore(self):
        if self.old is None:
            os.environ.pop(firelog.SESSION_ENV, None)
        else:
            os.environ[firelog.SESSION_ENV] = self.old

    def _session(self, value):
        if value is None:
            os.environ.pop(firelog.SESSION_ENV, None)
        else:
            os.environ[firelog.SESSION_ENV] = value

    def _run(self, *argv):
        here = os.getcwd()
        out, err = io.StringIO(), io.StringIO()
        try:
            os.chdir(str(self.repo.dir))
            with redirect_stdout(out), redirect_stderr(err):
                code = cli.main(["--repo", str(self.repo.dir)] + list(argv))
        finally:
            os.chdir(here)
        return code, out.getvalue(), err.getvalue()

    def _detail(self, verb):
        rec = firelog.last_run(verb, repo=str(self.repo.dir))
        self.assertIsNotNone(rec, f"no fire-log record for {verb!r}")
        return rec.get("detail") or ""


class TheArmIsDecidedByTheSession(Base):
    def test_a_fixed_session_yields_a_fixed_arm_and_both_arms_occur(self):
        for sid in ("session-0", "session-1", "session-2", "session-3"):
            self._session(sid)
            self.assertEqual(verbs.trial_arm("goal-seam"), parity(sid), sid)
        self.assertEqual({parity(f"session-{i}") for i in range(64)},
                         {"on", "off"})

    def test_no_session_is_unassigned_never_an_arm(self):
        self._session(None)
        self.assertEqual(verbs.trial_arm("goal-seam"), "unassigned")


class OnTheLineIsLastAndOnStderr(Base):
    def test_arc_narrow(self):
        self._session(session_for("on"))
        self._run(*OPEN)
        code, out, err = self._run("arc", "narrow", "freeze", "--text",
                                   "two left")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(err.rstrip("\n").split("\n")[-1], GOAL, err)
        self.assertNotIn("goal (", out)
        detail = self._detail("arc narrow")
        self.assertIn("goal-seam=narrow", detail)
        self.assertIn("arm=on", detail)
        self.assertNotIn("withheld=", detail)

    def test_arc_advance(self):
        self._session(session_for("on"))
        self._run(*OPEN)
        code, out, err = self._run("arc", "advance", "freeze", "--to", "next",
                                   "--reason", "moving on")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(err.rstrip("\n").split("\n")[-1], GOAL, err)
        self.assertNotIn("goal (", out)
        self.assertIn("goal-seam=advance; arm=on", self._detail("arc advance"))

    def test_an_unassigned_run_still_gets_the_line(self):
        self._session(None)
        self._run(*OPEN)
        code, out, err = self._run("arc", "narrow", "freeze", "--text",
                                   "two left")
        self.assertEqual(code, 0, out + err)
        self.assertEqual(err.rstrip("\n").split("\n")[-1], GOAL, err)
        self.assertIn("arm=unassigned", self._detail("arc narrow"))


class OffWithholdsAndSaysSo(Base):
    def test_arc_narrow_emits_nothing_and_records_the_withholding(self):
        self._session(session_for("off"))
        self._run(*OPEN)
        code, out, err = self._run("arc", "narrow", "freeze", "--text",
                                   "two left")
        self.assertEqual(code, 0, out + err)
        self.assertNotIn("goal (", out + err)
        self.assertNotIn("goal:", out + err)
        detail = self._detail("arc narrow")
        self.assertEqual(firelog.detail_tokens(detail, "arm"), ["off"])
        self.assertEqual(firelog.detail_tokens(detail, "withheld"),
                         ["goal-seam"])
        self.assertEqual(firelog.detail_tokens(detail, "goal-seam"), [],
                         "an OFF run printed nothing, so it records no print")


class OnOnePipeTheLineIsStillLast(Base):
    """THE FLUSH ARM. A child process with stdout and stderr on the same
    pipe is the shape `2>&1 | tail` gives the verb. In-process redirection
    cannot show this: a StringIO is never block-buffered."""

    def _child(self, *argv):
        env = dict(os.environ)
        env[firelog.SESSION_ENV] = session_for("on")
        proc = subprocess.run(
            [sys.executable, str(CLI), "--repo", str(self.repo.dir), *argv],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            env=env, cwd=str(self.repo.dir))
        return proc.returncode, proc.stdout

    def test_the_merged_stream_ends_on_the_goal_line(self):
        code, outp = self._child(*OPEN)
        self.assertEqual(code, 0, outp)
        code, outp = self._child("arc", "narrow", "freeze", "--text",
                                 "two left")
        self.assertEqual(code, 0, outp)
        lines = outp.rstrip("\n").split("\n")
        self.assertGreater(len(lines), 1, outp)
        self.assertEqual(lines[-1], GOAL, outp)


if __name__ == "__main__":
    unittest.main()
