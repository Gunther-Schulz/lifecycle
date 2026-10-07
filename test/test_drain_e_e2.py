"""Drain wave E, lane E2 — what a reader of the carrier is shown.

lc-299: lc-294 SHIPPED STANDBY WITH THREE READER GAPS.

  1. `item check` refused a READY block holding an UNKNOWN slot and said
     nothing about a STANDBY one. STANDBY promises everything READY promises
     — decision-complete, executable by a fresh context — so a slot nobody
     has ever written is exactly as impossible to have judged there.
  2. `item add --grade STANDBY` wrote the grade in a repo that never opted
     into it, and the verb's own `item check` then refused the block it had
     just written. `item bench` already refuses at its door; `add` did not.
  3. `head_draining` has two firing arms and only the EMPTY-head one had a
     dated fixture. The both-halves arm (a head that shrinks in each half and
     is still non-empty) was reachable by no fixture anywhere.

EVERY ARM REACHES ONLY THROUGH NAMES THE OLD BUILD ALREADY HAD (`cli.main`,
`exits`, the roster's `_Repo` and its STANDBY fixtures), so a red against
the unmodified code is an assertion FAILURE at the defect and never an
import error (law 4).

HALF 3 IS NOT A RED-FIRST REPAIR AND DOES NOT CLAIM TO BE. The branch it
exercises already existed; what was missing is the fixture. Its red was
taken by disabling that one comparison in a scratch copy, which is stated in
the lane's report rather than left to be assumed from a green line.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, exits  # noqa: E402
from lifecycle_core import items as items_mod  # noqa: E402
from lifecycle_core import refusals as R  # noqa: E402


def run(repo: Path, *argv):
    """`(code, output)` of one CLI run inside `repo`."""
    here = os.getcwd()
    buf = io.StringIO()
    try:
        os.chdir(str(repo))
        with redirect_stdout(buf):
            code = cli.main(["--repo", str(repo)] + list(argv))
    finally:
        os.chdir(here)
    return code, buf.getvalue()


def flat(text: str) -> str:
    return " ".join(text.split())


UNKNOWN_ROW = "FINDING [ready_with_unknown_slot]"

#: The seed block graded STANDBY with one slot nobody ever wrote. The arms
#: below differ from this in ONE property each: the slot, or the grade.
STANDBY_UNKNOWN = R.STANDBY_SEED.replace("goal: mitigate", "goal: UNKNOWN", 1)


class ItemCheckRefusesSTANDBYOverAnUnknownSlot(unittest.TestCase):
    """lc-299 half 1."""

    def _check(self, items: str, declaration=R.STANDBY_DECLARATION):
        r = R._Repo(items=items, declaration=declaration)
        self.addCleanup(r.close)
        return run(r.dir, "item", "check")

    def test_a_STANDBY_block_holding_UNKNOWN_is_REFUSED(self):
        self.assertIn("grade: STANDBY", STANDBY_UNKNOWN)
        self.assertIn("goal: UNKNOWN", STANDBY_UNKNOWN)
        code, outp = self._check(STANDBY_UNKNOWN)
        self.assertEqual(code, exits.FINDING, outp)
        self.assertIn(UNKNOWN_ROW, outp)
        # The message names the grade the block HAS. One that said READY
        # about a STANDBY block would send its reader to the wrong line.
        hit = next(ln for ln in outp.splitlines() if UNKNOWN_ROW in ln)
        self.assertIn("STANDBY", hit)
        self.assertIn("`goal`", hit)
        self.assertNotIn("is READY", hit)

    def test_CONTROL_the_same_STANDBY_block_with_the_slot_filled_is_CLEAN(self):
        code, outp = self._check(R.STANDBY_SEED)
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertNotIn("ready_with_unknown_slot", outp)

    def test_MUST_NOT_MOVE_a_READY_block_holding_UNKNOWN_still_fires(self):
        code, outp = self._check(
            R.SEED_ITEMS.replace("goal: mitigate", "goal: UNKNOWN", 1))
        self.assertEqual(code, exits.FINDING, outp)
        hit = next(ln for ln in outp.splitlines() if UNKNOWN_ROW in ln)
        self.assertIn("is READY", hit)

    def test_MUST_NOT_FIRE_on_the_grades_that_promise_no_judgment(self):
        """NEW and PARKED are where a migrated UNKNOWN is SUPPOSED to sit:
        the grade workflow fills it before READY. Widening to "every open
        grade" would have made each migrated entry a finding."""
        for grade, blocker in (("NEW", "decision which path the arc takes"),
                               ("PARKED", "decision which path the arc takes")):
            items = (R.SEED_ITEMS
                     .replace("grade: READY", f"grade: {grade}", 1)
                     .replace("goal: mitigate", "goal: UNKNOWN", 1)
                     .replace("blocked-by: NONE", f"blocked-by: {blocker}", 1))
            code, outp = self._check(items)
            self.assertNotIn("ready_with_unknown_slot", outp, grade)
            self.assertEqual(code, exits.CLEAN, f"{grade}: {outp}")

    def test_an_UNDECLARED_repo_reports_BOTH_refusals(self):
        """Two defects, two rows. The opt-in refusal must not swallow the
        slot refusal: repairing one would otherwise reveal the other."""
        code, outp = self._check(STANDBY_UNKNOWN,
                                 declaration=R.GOOD_FULL_DECLARATION)
        self.assertEqual(code, exits.FINDING, outp)
        self.assertIn(UNKNOWN_ROW, outp)
        self.assertIn("FINDING [standby_undeclared]", outp)

    def test_the_ROW_names_STANDBY(self):
        """The registry is the source (law 3): a row whose text says READY
        alone would describe a refusal narrower than the one that fires."""
        row = next(r for r in R.ROWS if r.ident == "ready_with_unknown_slot")
        self.assertIn("STANDBY", row.refusal)


class ItemAddRefusesAnUndeclaredSTANDBYAtTheDoor(unittest.TestCase):
    """lc-299 half 2."""

    ADD = R.GOOD_ADD + ["--grade", "STANDBY", "--join", "new"]

    def _repo(self, declaration):
        r = R._Repo(declaration=declaration)
        self.addCleanup(r.close)
        return r.dir

    def test_an_UNDECLARED_repo_is_REFUSED_and_NOTHING_is_written(self):
        repo = self._repo(R.GOOD_FULL_DECLARATION)
        before = (repo / "ITEMS.md").read_text(encoding="utf-8")
        code, outp = run(repo, *self.ADD)
        self.assertEqual(code, exits.FINDING, outp)
        self.assertIn("FINDING [standby_undeclared]", outp)
        self.assertIn("Nothing was written", flat(outp))
        self.assertEqual((repo / "ITEMS.md").read_text(encoding="utf-8"),
                         before)
        head = subprocess.run(["git", "-C", str(repo), "status",
                               "--porcelain", "--untracked-files=no"],
                              capture_output=True, text=True).stdout
        self.assertEqual(head, "", outp)

    def test_a_DECLARING_repo_books_it_and_the_check_agrees(self):
        repo = self._repo(R.STANDBY_DECLARATION)
        code, outp = run(repo, *self.ADD)
        self.assertEqual(code, exits.CLEAN, outp)
        parsed = items_mod.parse((repo / "ITEMS.md")
                                 .read_text(encoding="utf-8"))
        self.assertEqual([it.grade for it in parsed.items], ["STANDBY"])
        code, outp = run(repo, "item", "check")
        self.assertEqual(code, exits.CLEAN, outp)

    def test_MUST_NOT_MOVE_an_undeclared_repo_still_books_READY(self):
        repo = self._repo(R.GOOD_FULL_DECLARATION)
        code, outp = run(repo, *(R.GOOD_ADD + ["--join", "new"]))
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertNotIn("standby_undeclared", outp)


#: Half 3's history. One arc cites three READY items; one closes in each half
#: of the window, so the head runs 3 → 2 → 1 and is NON-EMPTY at every cut.
#: `added` is held at 1 and the baseline follows, exactly as the roster's own
#: `DRAIN_PLANT` does it, so conservation holds at each cut.
_ARC = {"sched": "## sched\ngoal: ship xx-1, then xx-2, then xx-3\n"}
BOTH_HALVES = [
    ("before", {"xx-1": "READY", "xx-2": "READY", "xx-3": "READY",
                "xx-9": "STANDBY"}, 1, (), _ARC),
    ("first-half", {"xx-1": "READY", "xx-2": "READY", "xx-9": "STANDBY"},
     1, ("xx-3",), _ARC),
    ("now", {"xx-1": "READY", "xx-9": "STANDBY"}, 1, ("xx-3", "xx-2"), _ARC),
]
#: The same closes in the same halves with the arc citing xx-1 alone: the
#: head is 1 at every cut. The arms differ in what the ARC cites, nothing else.
_ARC_FLAT = {"sched": "## sched\ngoal: ship xx-1\n"}
HEAD_HELD = [(age, grades, added, closed, _ARC_FLAT)
             for age, grades, added, closed, _arc in BOTH_HALVES]


class HeadDrainingFiresOnANonEmptyShrinkingHead(unittest.TestCase):
    """lc-299 half 3 — the dated fixture for the both-halves arm."""

    def test_a_head_shrinking_in_BOTH_halves_FIRES_while_non_empty(self):
        got = R._standby_history(BOTH_HALVES)
        self.assertEqual(got.code, exits.FINDING, got.output)
        hit = flat(got.output)
        self.assertIn("FINDING [head_draining] the scheduled head shrank in "
                      "BOTH halves of the window (3 → 2 → 1)", hit)
        # THE OTHER ARM DID NOT ANSWER FOR THIS ONE: the head is not empty.
        self.assertNotIn("is EMPTY", hit)
        self.assertIn("1 on the scheduled head", hit)
        self.assertIn("1 STANDBY", hit)
        # And the sibling trigger is silent, so the verdict is this arm's.
        self.assertNotIn("FINDING [ready_outgrows_head]", hit)

    def test_CONTROL_the_same_flow_with_a_head_that_HELD_is_clean(self):
        got = R._standby_history(HEAD_HELD)
        self.assertNotIn("FINDING [head_draining]", got.output)
        self.assertIn("head_draining: CLEAN — head 1 → 1 → 1",
                      flat(got.output))


if __name__ == "__main__":
    unittest.main()
