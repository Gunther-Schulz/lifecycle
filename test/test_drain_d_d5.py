"""Drain wave D, lane D5 — the flow ratio, and verdicts asked of a shell
(2026-10-07).

ONE FILE FOR THE LANE (wave B change 4): every red-first test this lane's
items asked for lives here.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli as cli_mod, exits, lanes, refusals, verify  # noqa: E402
from lifecycle_core.refusals import _Repo, _backdate_head  # noqa: E402


def _ratio(added, closed_bodies, compacted):
    """`item ratio` over a dated git carrier whose head says `added` and
    `compacted` and whose done home holds `closed_bodies` bodies. The head is
    backdated past the window so the verb reaches its verdict instead of
    answering could-not-verify for want of history."""
    items, done = refusals._flow_carrier(added, closed_bodies, compacted)
    with _Repo(items=items, done=done) as r:
        _backdate_head(r.dir)
        here = os.getcwd()
        try:
            os.chdir(str(r.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(r.dir), "item", "ratio"])
        finally:
            os.chdir(here)
    return code, buf.getvalue()


class CompactedCountsAsDrain(unittest.TestCase):
    """lc-293: by conservation open + done = baseline + added - compacted, so
    the drain side of the lifetime ratio is done bodies PLUS the head's
    compacted counter."""

    def test_the_10_8_6_plant_reads_clean(self):
        # 10 added, 8 closed of which 6 were compacted out of the done home.
        code, out = _ratio(10, 2, 6)
        self.assertNotIn("[capture_dominated]", out)
        self.assertIn("ratio: 10:8 = 1.25:1", out)
        self.assertEqual(code, exits.CLEAN, out)

    def test_control_a_genuinely_capture_heavy_carrier_still_fires(self):
        # Same compacted counter, but only 2 drained in total: 10:2 is a
        # real finding and must stay one.
        code, out = _ratio(10, 0, 2)
        self.assertIn("[capture_dominated]", out)
        self.assertEqual(code, exits.FINDING, out)

    def test_control_no_compaction_reads_as_before(self):
        code, out = _ratio(10, 2, 0)
        self.assertIn("ratio: 10:2 = 5.00:1", out)
        self.assertEqual(code, exits.FINDING, out)


class ShellAnswersForTheLastProcess(unittest.TestCase):
    """lc-194: a shell reports the LAST stage of a pipeline, so a pipeline
    whose first stage is broken answered as though it had run. THE SWEEP
    (keyed on the invariant: a subprocess whose returncode becomes a verdict
    through a SHELL) found exactly two sites in `plugin/` and `tools/`:
    `lanes.evaluate_trigger` and `verify.run_one`. Every other `subprocess`
    call is an argv list, one process, no shell between its exit code and
    the verdict."""

    GHOST = "no-such-command-b7f3e"
    HERE = Path.cwd()

    # --- the trigger evaluator --------------------------------------------

    def test_trigger_first_stage_missing_is_broken_not_quiet(self):
        t = lanes.evaluate_trigger(f"{self.GHOST} | grep -q .")
        self.assertEqual(t.state, lanes.BROKEN, t)

    def test_trigger_first_stage_exiting_2_is_broken(self):
        t = lanes.evaluate_trigger("sh -c 'exit 2' | cat")
        self.assertEqual(t.state, lanes.BROKEN, t)
        self.assertIn("stage 1", t.detail)

    def test_trigger_bare_and_chained_spellings_keep_their_answers(self):
        self.assertEqual(lanes.evaluate_trigger(self.GHOST).state, lanes.BROKEN)
        self.assertEqual(
            lanes.evaluate_trigger(f"true && {self.GHOST}").state, lanes.BROKEN)
        self.assertEqual(lanes.evaluate_trigger("exit 0").state, lanes.FIRE)
        self.assertEqual(lanes.evaluate_trigger("exit 1").state, lanes.QUIET)

    def test_trigger_working_pipelines_fire_and_stay_quiet_as_before(self):
        self.assertEqual(
            lanes.evaluate_trigger("echo a | grep -q a").state, lanes.FIRE)
        self.assertEqual(
            lanes.evaluate_trigger("echo a | grep -q b").state, lanes.QUIET)
        # `grep -q` closes the pipe early: the producer dies of SIGPIPE (141)
        # while the predicate FIRED. Reading 141 as broken would forbid every
        # legitimate `producer | grep -q` lane.
        self.assertEqual(
            lanes.evaluate_trigger("yes | grep -q y").state, lanes.FIRE)

    def test_trigger_declares_what_it_cannot_discriminate(self):
        # An earlier stage exiting 1 is indistinguishable from an honest
        # empty answer: the state stays what the last stage said, and the
        # detail SAYS the verdict is the last stage's.
        t = lanes.evaluate_trigger("false | cat")
        self.assertEqual(t.state, lanes.FIRE)
        self.assertIn("cannot discriminate", t.detail)

    # --- verify -----------------------------------------------------------

    def test_verify_first_stage_missing_is_did_not_run_not_clean(self):
        verdict, code, detail = verify.run_one(
            f"{self.GHOST} | cat", self.HERE, 30)
        self.assertEqual(verdict, "did-not-run", (verdict, code, detail))

    def test_verify_first_stage_failing_hard_is_not_clean(self):
        verdict, code, detail = verify.run_one(
            "sh -c 'exit 2' | cat", self.HERE, 30)
        self.assertEqual(verdict, "ran-failed", (verdict, code, detail))
        self.assertIn("stage 1", detail)

    def test_verify_bare_and_chained_spellings_keep_their_answers(self):
        self.assertEqual(
            verify.run_one(self.GHOST, self.HERE, 30)[0], "did-not-run")
        self.assertEqual(
            verify.run_one(f"true && {self.GHOST}", self.HERE, 30)[0],
            "did-not-run")
        self.assertEqual(verify.run_one("true", self.HERE, 30)[0], "ran-clean")
        self.assertEqual(verify.run_one("false", self.HERE, 30)[0], "ran-failed")

    def test_verify_working_pipelines_read_as_before(self):
        self.assertEqual(
            verify.run_one("echo a | grep -q a", self.HERE, 30)[0], "ran-clean")
        self.assertEqual(
            verify.run_one("yes | head -1 >/dev/null", self.HERE, 30)[0],
            "ran-clean")
        self.assertEqual(
            verify.run_one("echo a | grep -q b", self.HERE, 30)[0], "ran-failed")


if __name__ == "__main__":
    unittest.main()
