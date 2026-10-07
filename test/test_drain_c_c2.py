"""Drain wave C, lane C2 — a row's name in its own output; the lane name
`init --lane` writes through.

One class per item, each carrying the arms its done-criterion names.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits, refusals, roster  # noqa: E402


# --- lc-316 ------------------------------------------------------------------

#: The five rows lc-316 names. Stated HERE, from the item, and never derived
#: from the roster: the arm below asserts the roster's own unnamed set against
#: it, and an expectation read off the roster would move with it.
LC316_ROWS = (
    "laws_absent_could_not_verify",
    "unknown_grade_read",
    "grade_arm_malformed",
    "cost_test_unverified",
    "conservation_unverified",
)


def _named(row, fired) -> bool:
    return f"[{row.expected_finding_row}]" in fired.output


class EveryRowIsNamedInItsOwnOutput(unittest.TestCase):
    """lc-316: a row is named in its plant's output WHATEVER its expected
    code. A could-not-verify row that prints no name is graded on exit code
    3 alone, and every could-not-verify is a 3.
    """

    def test_no_row_fires_without_naming_itself(self):
        unnamed = []
        ran = 0
        for row in refusals.ROWS:
            if getattr(row, "skip_reason", None):
                continue
            ran += 1
            if not _named(row, row.fire()):
                unnamed.append(row.ident)
        # The population, stated: a loop over nothing would pass this arm.
        self.assertGreater(ran, 100, "the roster walk examined too few rows "
                                     "to mean anything")
        self.assertEqual(unnamed, [], "row(s) whose plant output carries no "
                                      "bracketed row name")

    def test_the_five_named_rows_keep_their_exit_code(self):
        """MUST-NOT-MOVE: naming a row changes no exit code. Each of the five
        still exits COULD NOT VERIFY, and now says which row answered.
        """
        by_ident = {r.ident: r for r in refusals.ROWS}
        for ident in LC316_ROWS:
            with self.subTest(row=ident):
                row = by_ident[ident]
                fired = row.fire()
                self.assertEqual(fired.code, exits.COULD_NOT_VERIFY,
                                 fired.output)
                self.assertTrue(_named(row, fired), fired.output)
                # The control must NOT carry the name: a tag printed on
                # every path names nothing.
                self.assertFalse(_named(row, row.control()),
                                 "the control's output carries the row name "
                                 "too, so the name separates nothing")


def _fake_row(*, output: str) -> refusals.Row:
    return refusals.Row(
        ident="lc316_probe_row",
        refusal="a probe row for the roster's own name check",
        firing_input="a plant exiting COULD NOT VERIFY",
        expect=exits.COULD_NOT_VERIFY,
        fire=lambda: refusals.Fired(exits.COULD_NOT_VERIFY, output),
        control=lambda: refusals.Fired(exits.CLEAN, "clean\n"),
    )


def _roster_lines(row) -> list:
    """Run the real roster runner over ONE row and return its lines."""
    buf = io.StringIO()
    with mock.patch.object(refusals, "ROWS", [row]):
        roster.cmd_test(lambda s="": buf.write(str(s) + "\n"))
    return buf.getvalue().splitlines()


class TheRosterNameCheckIsNotGatedOnFinding(unittest.TestCase):
    """lc-316, the other half: the roster's own name check ran only for rows
    expecting FINDING, so an unnamed could-not-verify row read PASS.

    The pair differs in the plant's OUTPUT alone — same row, same codes.
    """

    def test_an_unnamed_could_not_verify_plant_fails_the_row(self):
        lines = _roster_lines(_fake_row(
            output="COULD NOT VERIFY: something, under no name\n"))
        verdict = [ln for ln in lines if "lc316_probe_row" in ln
                   and ln.split()[:1] in (["PASS"], ["FAIL"])]
        self.assertEqual(len(verdict), 1, lines)
        self.assertTrue(verdict[0].startswith("FAIL"), verdict[0])
        self.assertTrue(
            any("names row [lc316_probe_row]" in ln.replace("\n", " ")
                or "row [lc316_probe_row]" in ln for ln in lines), lines)

    def test_a_named_could_not_verify_plant_passes_the_row(self):
        lines = _roster_lines(_fake_row(
            output="COULD NOT VERIFY [lc316_probe_row] something\n"))
        verdict = [ln for ln in lines if "lc316_probe_row" in ln
                   and ln.split()[:1] in (["PASS"], ["FAIL"])]
        self.assertEqual(len(verdict), 1, lines)
        self.assertTrue(verdict[0].startswith("PASS"), verdict[0])


if __name__ == "__main__":
    unittest.main()
