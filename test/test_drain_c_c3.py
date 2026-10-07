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


#: THE MEASURED PAIR (df-130, 2026-08-28). The ledger was written with the
#: bare question; the standing blocker was a SENTENCE ABOUT that question.
#: No answer could ever equal it, and nothing said the two were related.
BARE = "whether the gate reads the serving config"
ABOUT = f"the item own body says decision OPEN: {BARE}"
#: The same question retyped by hand: punctuation alone differs.
RETYPED = "whether the gate, reads the serving config?"
ANSWER = "yes, it reads the serving config"
STATEMENT = ("not-derivable: 2026-10-07 a preference with no ledger "
             "precedent\n")


def _blocked(question, *, stated=True):
    text = _graded("PARKED", f"decision {question}")
    return text.rstrip("\n") + "\n" + (STATEMENT if stated else "")


def _ledger(question=BARE):
    from lifecycle_core import ledger
    return (ledger.head_text() + "\n" + ledger.render(
        "decision", {"question": question, "answer": ANSWER}) + "\n")


def _verb(argv, question, *, stated=True, ledger_question=BARE):
    from lifecycle_core import refusals
    return refusals._cli(argv, items=_blocked(question, stated=stated),
                         ledger_text=_ledger(ledger_question))


class AnsweredInOtherWords(unittest.TestCase):
    """lc-62 — the ANSWER side of a decision blocker is equality, and a
    near-miss between a ledger question and a standing blocker was silent.

    NEVER RESOLVED, ONLY REPORTED: every arm that names a near-miss also
    asserts the item is still BLOCKED. Equality stays the rule; what changes
    is that the reader is handed the ledger line and its exact question.
    """

    def test_item_ready_names_the_ledger_line_on_the_measured_pair(self):
        fired = _verb(["item", "ready", "xx-1"], ABOUT)
        self.assertIn("BLOCKED", fired.output)
        self.assertNotIn("UNBLOCKED", fired.output)
        self.assertIn("near-match", fired.output)
        self.assertIn(repr(BARE), fired.output)
        self.assertIn("LEDGER.md:3", fired.output)
        self.assertIn(repr(ANSWER), fired.output)

    def test_item_ready_no_longer_says_NO_line_names_it(self):
        """The flat sentence is what sent the answerer away: the ledger DID
        hold the answer, one retyping apart."""
        fired = _verb(["item", "ready", "xx-1"], RETYPED)
        self.assertNotIn("so it has not been answered", fired.output)
        self.assertIn("near-match", fired.output)
        self.assertNotIn("UNBLOCKED", fired.output)

    def test_item_check_reports_the_measured_pair(self):
        fired = _verb(["item", "check"], ABOUT)
        hit = next((ln for ln in fired.output.splitlines()
                    if "near-match: xx-1" in ln), "")
        self.assertIn(repr(BARE), hit, fired.output)
        self.assertIn("LEDGER.md:3", hit)
        self.assertIn("NOT resolved", hit)

    def test_item_check_reports_a_near_miss_on_a_STATED_blocker(self):
        """The door has demanded the statement since lc-169, so the arm that
        skipped stated blockers skipped every blocker booked since."""
        stated = _verb(["item", "check"], RETYPED, stated=True)
        unstated = _verb(["item", "check"], RETYPED, stated=False)
        self.assertIn("near-match: xx-1", unstated.output)
        self.assertIn("near-match: xx-1", stated.output)

    # --- the controls: what must not move --------------------------------

    def test_the_near_miss_never_resolves_the_blocker(self):
        from lifecycle_core import ledger
        led = ledger.parse(_ledger())
        for q in (ABOUT, RETYPED):
            with self.subTest(q=q):
                self.assertEqual(ledger.decision_for(led, q), [])
        self.assertEqual(len(ledger.decision_for(led, BARE)), 1)

    def test_the_exact_question_still_UNBLOCKS_and_names_no_near_miss(self):
        fired = _verb(["item", "ready", "xx-1"], BARE)
        self.assertIn("UNBLOCKED — the ledger ANSWERS this decision",
                      fired.output)
        self.assertNotIn("near-match", fired.output)
        checked = _verb(["item", "check"], BARE)
        self.assertNotIn("near-match", checked.output)

    def test_an_UNRELATED_ledger_question_keeps_the_flat_sentence(self):
        other = "which capture window is the canonical one"
        fired = _verb(["item", "ready", "xx-1"], ABOUT, ledger_question=other)
        self.assertIn("so it has not been answered", fired.output)
        self.assertNotIn("near-match", fired.output)
        checked = _verb(["item", "check"], ABOUT, ledger_question=other)
        self.assertNotIn("near-match", checked.output)

    def test_a_SHORT_shared_fragment_is_not_a_near_miss(self):
        """Containment is reported only where the contained side is a whole
        question's worth of words; two words in common is ordinary English."""
        fired = _verb(["item", "ready", "xx-1"], ABOUT,
                      ledger_question="the gate")
        self.assertNotIn("near-match", fired.output)
        self.assertIn("so it has not been answered", fired.output)

    def test_containment_is_by_WORDS_and_not_by_characters(self):
        """`gate reads the` sits inside `investigate reads the` as characters
        and not as words."""
        fired = _verb(["item", "check"],
                      "whether to investigate reads the serving path",
                      ledger_question="gate reads the serving path")
        self.assertNotIn("near-match", fired.output)

    def test_the_exit_codes_and_the_census_do_not_move(self):
        near = _verb(["item", "check"], ABOUT)
        far = _verb(["item", "check"], ABOUT,
                    ledger_question="which capture window is the canonical "
                                    "one")
        self.assertEqual(near.code, far.code, near.output)

        def census(o):
            return [ln for ln in o.splitlines()
                    if ln.startswith(("decision blockers:", "census:",
                                      "item check:"))]
        self.assertEqual(census(near.output), census(far.output))
        self.assertEqual(len(census(near.output)), 3, near.output)
        ready_near = _verb(["item", "ready", "xx-1"], ABOUT)
        ready_far = _verb(["item", "ready", "xx-1"], ABOUT,
                          ledger_question="which capture window is the "
                                          "canonical one")
        self.assertEqual(ready_near.code, ready_far.code)


if __name__ == "__main__":
    unittest.main()
