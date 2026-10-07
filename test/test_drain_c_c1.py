"""Drain wave C, lane C1 — lc-105 and lc-318.

lc-105: `item close` MOVED A BODY OVER A LIVE `evidence` BLOCKER WITHOUT
ASKING THE PREDICATE. The move clears the `blocked-by:` LINE and records
nothing for this type, so two bodies reached the closure home that the next
`item check` reds and no verb can repair: one whose blocker was AMENDED (the
amendment resolves last-wins over the cleared line), and one whose base
blocker carried a `blocker-exercise:` slot (legal only beside an evidence
blocker, now sitting beside NONE).

EVERY RED-FIRST ARM REACHES ONLY THROUGH NAMES THE OLD BUILD ALREADY HAD
(`cli.main`, `exits`, `lanes.evaluate_trigger`, the CLI surface, git), so a
red against the unmodified code is an assertion FAILURE at the defect and
never an import error (law 4).
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
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, exits, lanes  # noqa: E402
from lifecycle_core import ledger as ledger_mod  # noqa: E402
from lifecycle_core.refusals import (  # noqa: E402
    EMPTY_DONE, GOOD_FULL_DECLARATION, SEED_ITEMS)


def build(items_text: str = SEED_ITEMS) -> Path:
    """A seeded git repo with every carrier TRACKED and committed."""
    d = Path(tempfile.mkdtemp(prefix="lifecycle-drain-c-c1-"))
    run = lambda *a: subprocess.run(a, cwd=str(d), capture_output=True,  # noqa: E731
                                    text=True)
    run("git", "init", "-q", "-b", "main")
    run("git", "config", "core.hooksPath", str(d / ".nohooks"))
    run("git", "config", "user.email", "c1@lifecycle.invalid")
    run("git", "config", "user.name", "drain c c1")
    (d / ".claude").mkdir()
    (d / ".claude" / "lifecycle.json").write_text(
        json.dumps(GOOD_FULL_DECLARATION), encoding="utf-8")
    (d / "LAWS.md").write_text("law\n", encoding="utf-8")
    (d / ".gitignore").write_text("__pycache__/\n*.py[co]\n*.lock\n*.flag\n",
                                  encoding="utf-8")
    (d / "ITEMS.md").write_text(items_text, encoding="utf-8")
    (d / "ITEMS-DONE.md").write_text(EMPTY_DONE, encoding="utf-8")
    (d / "LEDGER.md").write_text(ledger_mod.head_text(), encoding="utf-8")
    run("git", "add", "-A")
    run("git", "commit", "-qm", "seed")
    return d


def run_cli(repo: Path, *argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(["--repo", str(repo)] + list(argv))
    return code, buf.getvalue()


def git(d: Path, *argv) -> str:
    return subprocess.run(["git", "-C", str(d)] + list(argv),
                          capture_output=True, text=True).stdout


def head(d: Path) -> str:
    return git(d, "rev-parse", "HEAD").strip()


def flat(text: str) -> str:
    """Whitespace-normalised, so an assertion on a phrase does not depend on
    where a message happens to wrap."""
    return " ".join(text.split())


#: QUIET (exit 1) until `arrived.flag` exists, then FIRED (exit 0). The flag
#: is git-ignored in `build`, so creating it never dirties the tree.
PREDICATE = "test -e arrived.flag"
#: QUIET at its booking run, so the mint admits it; BROKEN (exit 2, which the
#: evaluator RESERVES) once `broken.flag` exists. A predicate that was broken
#: from the start could not be booked at all.
BREAKABLE = "if test -e broken.flag; then exit 2; fi; test -e arrived.flag"

DONE_CLOSE = ("item", "close", "xx-1", "--met", "none", "--decided", "none")
DROP_CLOSE = ("item", "close", "xx-1", "--drop", "--reason",
              "abandoned before the evidence came")


def amended(predicate: str = PREDICATE) -> Path:
    """xx-1 with the blocker AMENDED onto it by the verb — the booked route."""
    d = build()
    code, out = run_cli(d, "item", "amend", "xx-1", "--blocked-by",
                        f"evidence {predicate}", "--reason",
                        "now waits on a fact a command can settle")
    assert code == exits.CLEAN, out
    return d


def based(predicate: str = PREDICATE) -> Path:
    """xx-1 with the evidence blocker on its BASE line, beside the door's own
    `blocker-exercise:` stamp — the shape `item add` writes."""
    return build(SEED_ITEMS.replace(
        "blocked-by: NONE",
        f"blocked-by: evidence {predicate}\n"
        "blocker-exercise: none-yet 2026-10-07"))


SHAPES = {"amended": amended, "base": based}


class ACloseOverAnEvidenceBlockerAsksThePredicate(unittest.TestCase):
    """lc-105, red-first. Each arm states the defect at its effect site: what
    the NEXT `item check` says about the tree the close left behind."""

    def _repo(self, shape, predicate=PREDICATE):
        d = SHAPES[shape](predicate)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def test_ARRIVED_discharges_with_a_record_the_done_home_reads_back(self):
        for shape in SHAPES:
            with self.subTest(shape=shape):
                d = self._repo(shape)
                (d / "arrived.flag").write_text("here\n", encoding="utf-8")
                code, out = run_cli(d, *DONE_CLOSE)
                self.assertEqual(code, exits.CLEAN, out)
                done = (d / "ITEMS-DONE.md").read_text(encoding="utf-8")
                self.assertIn(f"blocker-moot: evidence {PREDICATE} ", done)
                self.assertIn("arrived", done)
                # THE DEFECT: this exited 2 against a body no verb can amend.
                code, out = run_cli(d, "item", "check")
                self.assertEqual(code, exits.CLEAN, out)
                self.assertEqual(git(d, "status", "--porcelain"), "")

    def test_NOT_ARRIVED_refuses_a_DONE_close_and_moves_nothing(self):
        for shape in SHAPES:
            with self.subTest(shape=shape):
                d = self._repo(shape)
                before = head(d)
                live = (d / "ITEMS.md").read_text(encoding="utf-8")
                code, out = run_cli(d, *DONE_CLOSE)
                self.assertEqual(code, exits.FINDING, out)
                self.assertIn("FINDING [close_over_live_blocker]", out)
                self.assertIn(PREDICATE, out)
                # The two exits the item-id refusal already prints.
                self.assertIn("--blocked-by NONE", out)
                self.assertIn("--drop", out)
                self.assertEqual(head(d), before, "a refused close moved HEAD")
                self.assertEqual(
                    (d / "ITEMS.md").read_text(encoding="utf-8"), live)
                self.assertNotIn(
                    "## xx-1",
                    (d / "ITEMS-DONE.md").read_text(encoding="utf-8"))
                self.assertEqual(git(d, "status", "--porcelain"), "")

    def test_NOT_ARRIVED_under_DROP_records_the_wait_ABANDONED(self):
        """The relayed route (dotfiles, df-34 and df-132): a drop over a live
        evidence blocker landed a body the commit gate then refused."""
        for shape in SHAPES:
            with self.subTest(shape=shape):
                d = self._repo(shape)
                code, out = run_cli(d, *DROP_CLOSE)
                self.assertEqual(code, exits.CLEAN, out)
                done = (d / "ITEMS-DONE.md").read_text(encoding="utf-8")
                self.assertIn("grade: DROPPED", done)
                self.assertIn(f"blocker-moot: evidence {PREDICATE} ", done)
                self.assertIn("dropped", done.split("blocker-moot:", 1)[1])
                self.assertNotIn("the evidence arrived", done)
                code, out = run_cli(d, "item", "check")
                self.assertEqual(code, exits.CLEAN, out)
                self.assertIn("dropped: xx-1",
                              git(d, "show", "HEAD:LEDGER.md"))
                self.assertEqual(git(d, "status", "--porcelain"), "")

    def test_BROKEN_is_COULD_NOT_VERIFY_and_refuses_DONE_and_DROP_alike(self):
        for shape in SHAPES:
            for name, argv in (("done", DONE_CLOSE), ("drop", DROP_CLOSE)):
                with self.subTest(shape=shape, close=name):
                    d = self._repo(shape, BREAKABLE)
                    (d / "broken.flag").write_text("x\n", encoding="utf-8")
                    before = head(d)
                    live = (d / "ITEMS.md").read_text(encoding="utf-8")
                    code, out = run_cli(d, *argv)
                    self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
                    self.assertIn("COULD NOT VERIFY", out)
                    self.assertNotIn("FINDING [", out)
                    self.assertIn("NOT CLOSED", out)
                    self.assertEqual(head(d), before)
                    self.assertEqual(
                        (d / "ITEMS.md").read_text(encoding="utf-8"), live)
                    self.assertEqual(git(d, "status", "--porcelain"), "")

    def test_the_predicate_goes_through_THE_trigger_evaluator_once(self):
        """Never a second body behind the contract: the close must call the
        function `lane list` and `item ready` call, with this predicate, in
        this repo — and once, because a predicate may be slow."""
        d = self._repo("amended")
        real = lanes.evaluate_trigger
        calls = []

        def spy(command, *a, **kw):
            calls.append((command, kw.get("cwd")))
            return real(command, *a, **kw)

        with mock.patch.object(lanes, "evaluate_trigger", spy):
            run_cli(d, *DONE_CLOSE)
        self.assertEqual([c for c, _cwd in calls], [PREDICATE])
        self.assertEqual(Path(calls[0][1]).resolve(), d.resolve())


class WhatTheEvidenceDispositionMustNotMove(unittest.TestCase):
    """lc-105, MUST-NOT-MOVE. Green on the old build and on the new one."""

    def test_CONTROL_an_unblocked_close_evaluates_nothing(self):
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        with mock.patch.object(lanes, "evaluate_trigger",
                               side_effect=AssertionError("no predicate")):
            code, out = run_cli(d, *DONE_CLOSE)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("blocker-moot",
                         (d / "ITEMS-DONE.md").read_text(encoding="utf-8"))
        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)

    def test_a_hand_planted_evidence_blocker_in_the_done_home_still_fires(self):
        """The row's real defect is untouched: a closed body with a live
        blocker and NO record of this predicate."""
        d = build(SEED_ITEMS.replace("baseline: 1", "baseline: 2"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        body = SEED_ITEMS.split("\n\n", 1)[1].replace(
            "## xx-1", "## xx-2").replace("grade: READY", "grade: DONE").replace(
            "blocked-by: NONE", f"blocked-by: evidence {PREDICATE}")
        (d / "ITEMS-DONE.md").write_text(EMPTY_DONE + "\n" + body,
                                         encoding="utf-8")
        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [blocked_in_done_home]", out)

    def test_a_record_of_ANOTHER_predicate_does_not_discharge(self):
        """Equality on the predicate, as for the other two types: a record
        about some other command clears nothing."""
        d = build(SEED_ITEMS.replace("baseline: 1", "baseline: 2"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        body = SEED_ITEMS.split("\n\n", 1)[1].replace(
            "## xx-1", "## xx-2").replace("grade: READY", "grade: DONE")
        body = (body.rstrip("\n") + "\n"
                "amend-reason: 2026-10-07 retyped by hand\n"
                f"amended-blocked-by: 2026-10-07 evidence {PREDICATE}\n"
                "blocker-moot: evidence test -e other.flag (the predicate "
                "exited 0 at this close: the evidence arrived)\n")
        (d / "ITEMS-DONE.md").write_text(EMPTY_DONE + "\n" + body,
                                         encoding="utf-8")
        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [blocked_in_done_home]", out)


class TheDoneHomeMessageNoLongerOverReads(unittest.TestCase):
    """lc-105: the finding said the body "did not arrive here by a close".
    For a blocker type no close records, a body that DID arrive by a close
    reaches this row — so the sentence asserted a provenance it never read."""

    def test_the_message_does_not_assert_the_body_missed_a_close(self):
        d = build(SEED_ITEMS.replace("baseline: 1", "baseline: 2"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        body = SEED_ITEMS.split("\n\n", 1)[1].replace(
            "## xx-1", "## xx-2").replace("grade: READY", "grade: DONE").replace(
            "blocked-by: NONE", "blocked-by: external the vendor ships")
        (d / "ITEMS-DONE.md").write_text(EMPTY_DONE + "\n" + body,
                                         encoding="utf-8")
        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [blocked_in_done_home]", out)
        self.assertNotIn("so it did not arrive here by a close", flat(out))


if __name__ == "__main__":
    unittest.main()
