"""Drain wave C, lane C3 — the live home's closed grades (lc-134).

WHAT THESE ARMS HOLD APART. The closure home refuses an OPEN grade
(`open_grade_in_done_home`); the live carrier had no mirror, so a block
graded DONE or DROPPED while it still sat in `ITEMS.md` passed `item check`
CLEAN and was counted on the closed side of the census while live. Such a
body arises from a hand edit or an interrupted close, which is the
population the carrier checks exist for.

THE CONTROLS ARE THE OTHER HALF AND THEY MUST NOT MOVE: every OPEN grade in
the live home still passes, the done home's own direction is unchanged, and
a closed body below the archive heading stays exempt.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits  # noqa: E402
from lifecycle_core import items  # noqa: E402
from lifecycle_core.refusals import (  # noqa: E402
    DONE_BLOCK, EMPTY_DONE, GOOD_ITEMS)

ROW = "[closed_grade_in_live_home]"


def _check(text, *, done=False, grades_extra=()):
    """`(exit, output)` of the live check, or of the done home's with `done`."""
    buf = []
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / ("ITEMS-DONE.md" if done else "ITEMS.md")
        path.write_text(text, encoding="utf-8")
        if done:
            code = items.check_done_file(path, buf.append, prefix="xx")
        else:
            code = items.check_file(path, buf.append, prefix="xx",
                                    grades_extra=grades_extra)
    return code, "\n".join(buf)


def _graded(grade, blocker="NONE"):
    return (GOOD_ITEMS.replace("grade: READY", f"grade: {grade}")
            .replace("blocked-by: NONE", f"blocked-by: {blocker}"))


class ClosedGradeInTheLiveHome(unittest.TestCase):
    """lc-134 — the mirror of `open_grade_in_done_home`."""

    def test_a_DROPPED_block_in_the_live_carrier_is_a_FINDING(self):
        code, out = _check(_graded("DROPPED"))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn(ROW, out)
        hit = next(ln for ln in out.splitlines() if ROW in ln)
        self.assertIn("'xx-1'", hit)
        self.assertIn("DROPPED", hit)

    def test_a_DONE_block_in_the_live_carrier_is_a_FINDING(self):
        code, out = _check(_graded("DONE"))
        self.assertEqual(code, exits.FINDING, out)
        hit = next((ln for ln in out.splitlines() if ROW in ln), "")
        self.assertIn("'xx-1'", hit, out)
        self.assertIn("DONE", hit)

    def test_the_closing_line_counts_it_and_does_not_say_CLEAN(self):
        _code, out = _check(_graded("DROPPED"))
        last = out.splitlines()[-1]
        self.assertTrue(last.startswith("item check: FINDING"), last)
        self.assertIn("1 shape finding(s)", last)

    def test_every_OPEN_grade_in_the_live_home_still_passes(self):
        arms = (("READY", "NONE", ()),
                ("NEW", "external the upstream release lands", ()),
                ("PARKED", "external the upstream release lands", ()),
                (items.STANDBY, "NONE", (items.STANDBY,)))
        self.assertEqual({a[0] for a in arms}, set(items.GRADES_OPEN))
        for grade, blocker, extra in arms:
            with self.subTest(grade=grade):
                code, out = _check(_graded(grade, blocker), grades_extra=extra)
                self.assertEqual(code, exits.CLEAN, out)
                self.assertNotIn(ROW, out)

    def test_the_done_homes_own_direction_is_unchanged(self):
        code, out = _check(EMPTY_DONE + "\n" + DONE_BLOCK, done=True)
        self.assertEqual(code, exits.CLEAN, out)
        code, out = _check(EMPTY_DONE + "\n" + DONE_BLOCK.replace(
            "grade: DONE", "grade: READY"), done=True)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[open_grade_in_done_home]", out)
        self.assertNotIn(ROW, out)

    def test_a_closed_body_below_the_archive_heading_stays_exempt(self):
        text = (GOOD_ITEMS.rstrip("\n") + "\n\n" + items.ARCHIVE_HEADING
                + "\n\n" + DONE_BLOCK.replace("## xx-1", "## xx-7"))
        code, out = _check(text)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn(ROW, out)
        self.assertIn("archive:", out)


if __name__ == "__main__":
    unittest.main()
