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


class Amendments(unittest.TestCase):
    """lc-27 — the append-only edit path, read from the carrier's side.

    The VERB's own refusals are roster rows (`amend_without_reason`,
    `amend_nothing_to_amend`). These cover what the PARSER owes, which is the
    half whose failure is silent: a resolution rule that resolved to the
    wrong value would leave every reader confidently wrong, and a shape check
    that fired on a legitimate second amendment would stop the lane (R11).
    """

    def _amended(self, *lines):
        return GOOD_ITEMS.rstrip("\n") + "\n" + "".join(l + "\n" for l in lines)

    def test_an_amendment_supersedes_the_value_in_force(self):
        p = items.parse(self._amended(
            "amend-reason: 2026-08-27 the goal was mis-recorded at intake",
            "amended-goal: 2026-08-27 verify"))
        self.assertEqual(p.problems, [])
        self.assertEqual(p.items[0].slots["goal"], "verify")

    def test_the_earlier_line_is_RETAINED_not_rewritten(self):
        """The whole point of the form: the block still says what it said.

        Without this the amendment is an in-place rewrite with a date on it,
        and the carrier loses its record of having been wrong."""
        text = self._amended(
            "amend-reason: 2026-08-27 the goal was mis-recorded at intake",
            "amended-goal: 2026-08-27 verify")
        self.assertIn("goal: mitigate", text)
        p = items.parse(text)
        self.assertEqual(
            [(n, v) for n, v, _ln in p.items[0].amendments],
            [("amend-reason",
              "2026-08-27 the goal was mis-recorded at intake"),
             ("amended-goal", "2026-08-27 verify")])

    def test_a_SECOND_amendment_of_one_slot_is_not_a_repeat_finding(self):
        """THE MUST-NOT ARM. Amendment lines repeat by design; routed through
        the repeat check they would make the second correction a shape
        finding, which is an edit path that works once."""
        p = items.parse(self._amended(
            "amend-reason: 2026-08-27 the goal was mis-recorded at intake",
            "amended-goal: 2026-08-27 verify",
            "amend-reason: 2026-08-27 verify was wrong too",
            "amended-goal: 2026-08-27 retire"))
        self.assertEqual(p.problems, [])
        self.assertEqual(p.items[0].slots["goal"], "retire",
                         "LAST wins — the file is append-only, so it is "
                         "chronological")

    def test_an_undated_amendment_line_is_a_finding(self):
        code, out = run_check(self._amended("amended-goal: verify"))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("ISO date", out)

    def test_amending_the_GRADE_is_a_finding(self):
        """READY is judged (law 10). A quiet second writer of the grade slot
        would be exactly the derivation the design refuses."""
        code, out = run_check(self._amended("amended-grade: 2026-08-27 PARKED"))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("amendable slots", out)
        self.assertEqual(items.parse(
            self._amended("amended-grade: 2026-08-27 PARKED")
        ).items[0].slots["grade"], "READY", "the refused amendment must not "
                                            "have been applied anyway")

    def test_an_amendment_ABOVE_the_fixed_slots_is_a_finding(self):
        lines = GOOD_ITEMS.rstrip("\n").split("\n")
        i = lines.index("goal: mitigate")
        lines.insert(i, "amended-goal: 2026-08-27 verify")
        code, out = run_check("\n".join(lines) + "\n")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("among the fixed slots", out)

    def test_amending_a_slot_the_block_does_not_carry_is_a_finding(self):
        text = self._amended("amended-goal: 2026-08-27 verify").replace(
            "goal: mitigate\n", "", 1)
        code, out = run_check(text)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("nothing to supersede", out)

    #: A CLOSED body of the shape `item close` actually writes: the block's
    #: seven slots, then whatever it accumulated while it was live (here an
    #: amendment group), then the closure's own `blocker-moot:` line APPENDED
    #: last. The two tests below feed the same bytes and differ in ONE thing
    #: — where the amendment line sits.
    _CLOSED = (GOOD_ITEMS.rstrip("\n").replace("grade: READY", "grade: DROPPED")
               + "\namend-reason: 2026-08-27 the wave-4 grade pass"
                 "\namended-done-criterion: 2026-08-27 the value now in force"
                 "\nblocker-moot: regrade: fill goal, write-set,"
                 " done-criterion and evidence, or drop\n")

    def test_a_CLOSED_amended_body_is_NOT_a_finding(self):
        """lc-42 — the ordinary close of an amended item, and it must be clean.

        `item close` appends `blocker-moot:` to a body it has already moved,
        so that line sits BELOW the amendment group. With the closed-body
        slots counted as part of the fixed run, `max(fixed_at)` landed past
        every amendment and an ordinary close read as a reordering. Measured
        n=2 in a live carrier (dotfiles' done home, df-75 and df-64). A guard
        that fires on legitimate work stops the lane (R11).
        """
        code, out = run_check(self._CLOSED)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("among the fixed slots", out)

    def test_the_SAME_closed_body_with_the_line_misplaced_still_fires(self):
        """THE CONTROL for the narrower predicate: it must still catch the
        real defect. Without this arm, 'the close is clean' is
        indistinguishable from 'the order check no longer works' — both are
        green."""
        misplaced = self._CLOSED.replace(
            "goal: mitigate\n",
            "amended-goal: 2026-08-27 verify\ngoal: mitigate\n")
        code, out = run_check(misplaced)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("among the fixed slots", out)

    def test_an_unamended_block_is_untouched_by_any_of_this(self):
        """The control for the whole class: the same check over a block with
        no amendment line must read exactly as it did before."""
        code, out = run_check(GOOD_ITEMS)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(items.parse(GOOD_ITEMS).items[0].amendments, [])


class ClosureRecord(unittest.TestCase):
    """lc-44 — the two closed-body slots a DONE close writes.

    The VERB's half (that a `--reason` reaches the body at all) is exercised
    in `test_moves.py` against a real repo. These cover the PARSER's half:
    that the two lines are slots the shape check knows, that a LIVE block
    carrying one is diagnosed as the closure slot it is rather than as an
    unknown word, and that the reason carries its date.
    """

    def _closed(self, *extra):
        return (GOOD_ITEMS.rstrip("\n").replace("grade: READY", "grade: DONE")
                + "\n" + "".join(l + "\n" for l in extra))

    def test_a_closed_body_carrying_the_closure_record_is_CLEAN(self):
        code, out = run_check(self._closed(
            "closed-reason: 2026-08-27 shipped in the wave-4 batch",
            "closed-ref: 0123456789abcdef0123456789abcdef01234567"))
        self.assertEqual(code, exits.CLEAN, out)

    def test_the_SAME_lines_on_a_LIVE_block_are_the_closure_slot_finding(self):
        """The control, and it names the ROW: before these were slots the
        same input was reported as an unknown word, which sends its reader
        looking for a typo rather than for a body claiming a closure that
        has not happened."""
        code, out = run_check(
            GOOD_ITEMS.rstrip("\n")
            + "\nclosed-reason: 2026-08-27 shipped in the wave-4 batch\n")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("done_slot_on_live_item", out)
        self.assertIn("`closed-reason:`", out)

    def test_an_undated_closed_reason_is_a_finding(self):
        code, out = run_check(self._closed(
            "closed-reason: shipped in the wave-4 batch"))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("ISO date", out)

    def test_a_closed_body_WITHOUT_the_record_stays_clean(self):
        """The must-not arm: the record is optional — a close with no
        `--reason` behaves as it did, and a shape check that demanded the
        lines would fire on every body closed before this existed."""
        code, out = run_check(self._closed())
        self.assertEqual(code, exits.CLEAN, out)


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
