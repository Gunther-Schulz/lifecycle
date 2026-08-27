"""The carrier parser and shape check, beyond what the refusal rows cover.

The rows in `refusals.py` prove each REFUSAL fires. These cover the parser's
other obligations — the ones whose failure is silent rather than loud: an
archive section that must NOT be shape-checked, an absent file that must not
read as an empty one, and the census's refusal to guess.
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits, items  # noqa: E402
from lifecycle_core.refusals import (  # noqa: E402
    EMPTY_DONE, FOUR_BLOCKER_ITEMS, GOOD_ITEMS)


def run_check(text=None, prefix="xx"):
    with tempfile.TemporaryDirectory(prefix="lifecycle-items-") as td:
        p = Path(td) / "ITEMS.md"
        if text is not None:
            p.write_text(text, encoding="utf-8")
        buf = []
        code = items.check_file(p, buf.append, prefix=prefix)
        return code, "\n".join(buf)


class Archive(unittest.TestCase):

    #: A body of exactly the kind the pre-migration archive holds: a `##`
    #: heading that is not an id, no fixed slots, hand-written prose. The two
    #: tests below feed it the SAME bytes and differ in one thing only —
    #: whether the archive heading precedes it.
    BODY = ("- **READY 2026-01-01 — an old hand-written body.**\n"
            "## not-an-id-at-all\n"
            "grade: READY\n"
            "prose: whatever\n")

    def test_archive_bodies_are_held_verbatim_and_not_shape_checked(self):
        """The pre-migration archive is prose from before the tool existed.

        Shape-checking it would report hundreds of findings about text that
        was never meant to satisfy a fixed-slot shape, and a checker that
        fires on legitimate content trains the override reflex that kills it.
        """
        code, out = run_check(
            GOOD_ITEMS + "\n" + items.ARCHIVE_HEADING + "\n\n" + self.BODY)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("archive:", out)

    def test_the_same_bytes_ABOVE_the_archive_heading_do_fire(self):
        """The control for the test above: it is the HEADING that exempts.

        Without this pair, 'the archive is skipped' is indistinguishable from
        'the shape check does not work' — both produce a green.
        """
        code, out = run_check(GOOD_ITEMS + "\n" + self.BODY)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("not-an-id-at-all", out)


class ThirdAnswer(unittest.TestCase):

    def test_an_absent_carrier_is_could_not_verify_not_clean(self):
        code, out = run_check(None)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("COULD NOT VERIFY", out)

    def test_an_unknown_grade_word_is_counted_apart_never_folded(self):
        code, out = run_check(GOOD_ITEMS.replace("grade: READY", "grade: FOO"))
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("open 0", out)
        self.assertIn("unknown 1", out)

    def test_a_known_grade_word_is_not_counted_as_unknown(self):
        code, out = run_check(GOOD_ITEMS)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("open 1", out)
        self.assertIn("unknown 0", out)


class Shape(unittest.TestCase):

    def test_slots_out_of_order_are_a_finding(self):
        lines = GOOD_ITEMS.split("\n")
        i = lines.index("goal: mitigate")
        j = lines.index("evidence: none yet")
        lines[i], lines[j] = lines[j], lines[i]
        code, out = run_check("\n".join(lines))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("out of order", out)

    def test_an_id_off_the_declared_prefix_is_a_finding(self):
        code, out = run_check(GOOD_ITEMS.replace("## xx-1", "## zz-1"))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("declared prefix", out)

    def test_the_prefix_comes_from_the_declaration_not_from_the_file(self):
        """Inferring the prefix from the ids present would make any
        consistent corruption look correct — the same-parentage defect."""
        code, _ = run_check(GOOD_ITEMS.replace("## xx-1", "## zz-1"),
                            prefix="zz")
        self.assertEqual(code, exits.CLEAN)

    def test_a_wrapped_slot_value_is_a_shape_break(self):
        code, out = run_check(
            GOOD_ITEMS.replace("evidence: none yet",
                               "evidence: a value that\n  wrapped onto a second line"))
        self.assertEqual(code, exits.FINDING, out)


class BlockerTargets(unittest.TestCase):
    """lc-28 — an item-id blocker already sitting in the carrier.

    THE OVER-FIRE ARM IS WHAT DECIDES WHETHER THIS SHIPS, so the fixture
    carries ALL FOUR of §3.1's blocker forms at once and every test below
    runs against that same carrier. `decision <q>`, `evidence <predicate>`
    and NONE resolve against nothing BY DESIGN — a check that could not tell
    them from a dangling id would fire on legitimate work, which is the
    repair that stops the lane (R11). A fixture holding only the item form
    would score identically whether or not the check got that right.
    """

    def _run(self, text, prefix="xx", done=EMPTY_DONE):
        live = items.parse(text)
        done_parsed = items.parse(done) if done is not None else None
        buf = []
        code = items.check_blocker_targets(live, done_parsed, buf.append,
                                           "the done home was not read",
                                           prefix=prefix)
        return code, "\n".join(buf)

    def test_a_dangling_id_is_a_finding_and_names_its_block(self):
        code, out = self._run(FOUR_BLOCKER_ITEMS)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [dangling_reference]", out)
        self.assertIn("xx-9999", out)
        self.assertIn("'xx-1'", out)

    def test_the_other_three_forms_do_not_fire(self):
        """THE MUST-NOT ROWS, asserted individually rather than by a count:
        a check that fired on `decision` and missed the dangling id would
        satisfy a bare "one finding" assertion."""
        code, out = self._run(FOUR_BLOCKER_ITEMS)
        self.assertEqual(out.count("FINDING [dangling_reference]"), 1, out)
        for must_not in ("xx-2", "xx-3", "xx-4", "decision which window",
                         "evidence test -f /nonexistent"):
            self.assertNotIn(must_not, out)

    def test_it_goes_clean_once_the_id_resolves(self):
        """The control: the SAME carrier, the SAME four forms, the item
        blocker retargeted to a live id. The arms differ in the ID ALONE."""
        code, out = self._run(FOUR_BLOCKER_ITEMS.replace(
            "blocked-by: xx-9999", "blocked-by: xx-4"))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("blocker targets: CLEAN", out)

    def test_a_blocker_resolving_in_the_DONE_home_is_not_dangling(self):
        """An item-id blocker resolves on its target's DONE, so a closed
        target is a wait that has been answered — not a dangling one. Reading
        the live home alone would report it as dangling, which is the same
        over-fire one step over."""
        done = EMPTY_DONE + (
            "\n## xx-9999\ngrade: DONE\n"
            "requirement: the closed target — LEDGER.md\ngoal: mitigate\n"
            "write-set: tools/thing.py\ndone-criterion: done\n"
            "evidence: none yet\nblocked-by: NONE\n")
        code, out = self._run(FOUR_BLOCKER_ITEMS, done=done)
        self.assertEqual(code, exits.CLEAN, out)

    def test_an_unreadable_done_home_is_could_not_verify_not_clean(self):
        code, out = self._run(FOUR_BLOCKER_ITEMS, done=None)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("COULD NOT VERIFY", out)

    def test_no_declared_prefix_is_could_not_verify_not_clean(self):
        """Without the prefix an item-id blocker cannot be told from prose
        that resembles one. Answering CLEAN there is the number shaped like a
        pass — the third answer the design refuses to fold."""
        code, out = self._run(FOUR_BLOCKER_ITEMS, prefix=None)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("id-prefix", out)

    def test_a_carrier_with_no_blockers_says_nothing(self):
        code, out = self._run(GOOD_ITEMS)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(out, "")


if __name__ == "__main__":
    unittest.main()
