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

from lifecycle_core import exits, items, refusals  # noqa: E402
from lifecycle_core.refusals import (  # noqa: E402
    DONE_BLOCK, EMPTY_DONE, FOUR_BLOCKER_ITEMS, GOOD_ITEMS)


def run_check(text=None, prefix="xx"):
    with tempfile.TemporaryDirectory(prefix="lifecycle-items-") as td:
        p = Path(td) / "ITEMS.md"
        if text is not None:
            p.write_text(text, encoding="utf-8")
        buf = []
        code = items.check_file(p, buf.append, prefix=prefix)
        return code, "\n".join(buf)


def run_done_check(text=None, prefix="xx"):
    """`check_done_file` over a throwaway done home. Its own runner because
    the done home asks three questions the live check cannot (§3.8c), and a
    caller that reached for `run_check` would be grading the wrong file."""
    with tempfile.TemporaryDirectory(prefix="lifecycle-done-") as td:
        p = Path(td) / "ITEMS-DONE.md"
        if text is not None:
            p.write_text(text, encoding="utf-8")
        buf = []
        code = items.check_done_file(p, buf.append, prefix=prefix)
        return code, "\n".join(buf)


class ItemSlotsOverTheRealCarrier(unittest.TestCase):
    """`item slots` reads one parsed block's positional slots, never prose."""

    REPO = Path(__file__).resolve().parents[1]

    def _run(self, ident):
        """Run the public verb; an unbuilt parser is deliberately an assertion red.

        Catching argparse's `SystemExit` keeps the red at the claimed
        observable: once the name exists, a first-wins implementation still
        fails the value assertion below rather than changing this arm's kind.
        """
        import io
        from contextlib import redirect_stdout
        from lifecycle_core import cli as cli_mod

        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(self.REPO), "item", "slots",
                                     ident])
        except SystemExit as exc:
            code = exc.code
        return code, buf.getvalue()

    def _item(self, ident):
        parsed = items.parse((self.REPO / "ITEMS.md").read_text(encoding="utf-8"))
        return next(it for it in parsed.items if it.ident == ident)

    def test_lc_7_reports_the_LAST_amended_evidence_not_the_first(self):
        item = self._item("lc-7")
        evidence = [raw.split(" ", 1)[1] for name, raw, _ in item.amendments
                    if name == "amended-evidence"]
        self.assertEqual(len(evidence), 2, "the real-carrier discriminator vanished")
        self.assertNotEqual(evidence[0], evidence[1])

        code, out = self._run("lc-7")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn(f"evidence: {evidence[-1]}", out)
        self.assertNotIn(f"evidence: {evidence[0]}", out)

    def test_lc_22_without_amendments_reports_base_slots_byte_unchanged(self):
        item = self._item("lc-22")
        self.assertEqual(item.amendments, [], "this control must have no amendments")

        code, out = self._run("lc-22")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(out.splitlines(),
                         [f"{slot}: {item.slots[slot]}" for slot in items.SLOTS])


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


class ClosedBodySlotVocabulary(unittest.TestCase):
    """`DONE_ONLY_SLOTS` has consumers that ENUMERATE it, and a restated
    enumeration cannot age loudly.

    The row text is the case that motivated this: `done_slot_on_live_item`
    named two of the four slots after lc-44 added the other two, and neither
    its plant, its control, nor the roster's coverage check could see it — a
    row's text is not an input any of them grades. So the enumeration is
    derived at construction and this asserts that it was.

    HERE RATHER THAN IN `test_refusals.py` because the SOURCE of the
    enumeration is this module's tuple: what fails when a fifth slot is added
    is this vocabulary's consumers, and this is the file that owns it.
    """

    def test_the_live_slot_row_names_EVERY_closed_body_slot(self):
        from lifecycle_core import refusals
        row = next(r for r in refusals.ROWS
                   if r.ident == "done_slot_on_live_item")
        missing = [s for s in items.DONE_ONLY_SLOTS
                   if f"`{s}:`" not in row.refusal]
        self.assertEqual(
            missing, [],
            f"the row's own text names {row.refusal!r} while "
            f"DONE_ONLY_SLOTS holds {items.DONE_ONLY_SLOTS}. A restated "
            "enumeration beside its source stays byte-identical to health "
            "when the source grows.")

    def test_the_assertion_can_FAIL(self):
        """The instrument's positive control. Without it the assertion above
        passes against a `missing` list that could never be non-empty — a
        membership test over a text is exactly the shape that returns a
        clean zero when it is looking at the wrong string."""
        restated = ("a LIVE block carrying a closed-body slot — "
                    "`superseded-by:` or `blocker-moot:`, each of which "
                    "records something a CLOSURE did")
        missing = [s for s in items.DONE_ONLY_SLOTS
                   if f"`{s}:`" not in restated]
        self.assertEqual(missing, ["closed-reason", "closed-ref"],
                         "the pre-lc-44 text must still be caught")


class MootBlockerInDoneHome(unittest.TestCase):
    """lc-48 — `blocked_in_done_home` against the body a close annotated.

    THE MECHANISM, because the fixtures are unreadable without it: `item
    close` clears the `blocked-by:` SLOT LINE, and an `amended-blocked-by:`
    line resolves last-wins OVER that line. So a body whose blocker was
    amended and then closed reads `blocked-by: NONE` while its EFFECTIVE
    blocker is still the decision — and the check fired on the exact body the
    close had recorded correctly (dotfiles' done home, df-141, 2026-08-27).
    Clearing the amendment instead is the in-place rewrite the append-only
    model forbids, so the CHECK is what moved.

    Every fixture below is the SAME body differing in one thing, because the
    question is which outcome happened and not whether something did.
    """

    #: The df-141 shape: amended into a decision blocker, then closed with the
    #: moot record naming that same question.
    QUESTION = "does the desk accept the amendment in place"

    def _body(self, *extra, blocker="NONE"):
        block = DONE_BLOCK.replace("blocked-by: NONE",
                                   f"blocked-by: {blocker}")
        return (EMPTY_DONE + "\n" + block.rstrip("\n") + "\n"
                + "".join(l + "\n" for l in extra))

    def _amended(self, question, moot=None):
        extra = [f"amend-reason: 2026-08-27 the desk retyped the blocker",
                 f"amended-blocked-by: 2026-08-27 decision {question}"]
        if moot is not None:
            extra.append(f"blocker-moot: {moot}")
        return self._body(*extra)

    def test_the_df_141_shape_is_CLEAN(self):
        """The red: before lc-48 this fired on a correctly closed body."""
        code, out = run_done_check(self._amended(self.QUESTION,
                                                 moot=self.QUESTION))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("blocked_in_done_home", out)

    def test_the_SAME_body_with_NO_moot_record_still_fires(self):
        """THE ARM THE REPAIR MUST NOT TAKE WITH IT. A live blocker with no
        moot record is a body that arrived by a path that is not a close —
        the real defect, and the one this row exists for."""
        code, out = run_done_check(self._amended(self.QUESTION))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("blocked_in_done_home", out)

    def test_a_moot_record_of_a_DIFFERENT_question_does_not_discharge(self):
        """MUST-NOT-MOVE. A discharge keyed on the presence of any
        `blocker-moot:` line would clear a blocker on a record about
        something else — and its green would be identical to the green
        above."""
        code, out = run_done_check(
            self._amended(self.QUESTION, moot="an entirely other question"))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("blocked_in_done_home", out)

    def test_a_moot_record_that_is_a_PREFIX_does_not_discharge(self):
        """The equality is exact. A containment test would read a shorter
        question as discharging every longer one that begins with it."""
        code, out = run_done_check(
            self._amended(self.QUESTION, moot=self.QUESTION.split(" in ")[0]))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("blocked_in_done_home", out)

    def test_an_EVIDENCE_blocker_is_not_dischargeable_by_a_moot_record(self):
        """Only the `decision` type is annotated by a close, so only that
        type has a moot record to be discharged by. A discharge that ignored
        the type would clear a surviving evidence blocker on a line no close
        ever wrote for it."""
        code, out = run_done_check(self._body(
            "blocker-moot: the CI lane reports green",
            blocker="evidence the CI lane reports green"))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("blocked_in_done_home", out)

    def test_the_five_NONE_bodies_stay_clean_by_the_UNCHANGED_branch(self):
        """The other five real blocks carrying `blocker-moot:` (df-1, df-39,
        df-64, df-73, df-75) had `blocked-by` amended to NONE before close.
        They leave by the type test, exactly as they did before lc-48 — so
        their green says nothing about the new branch and this asserts the
        branch they actually take."""
        it = items.parse(self._body("blocker-moot: a regrade note")).items[0]
        kind, detail = items.classify_blocker(it.slots["blocked-by"], "xx")
        self.assertEqual(kind, "none")
        self.assertFalse(items._moot_discharges(it, detail),
                         "a NONE blocker must not reach the discharge at all")
        code, out = run_done_check(self._body("blocker-moot: a regrade note"))
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


class TheCostTestsThirdConjunct(unittest.TestCase):
    """§3.11's intake cost test has THREE conjuncts; the third is the blocker.

    The declared rule (`judgment.RULES`, `intake-cost-test`) reads "write-set
    <= 1 file AND session live AND no typed blocker -> the tool asks 'do it
    now?'; any other shape -> NEW". A TYPED BLOCKER IS THEREFORE THE EXEMPTION
    THE SPEC ALREADY GRANTS, and `cost_test` never received it — so a
    correctly blocked one-file item was vetoed, twice, across two desks and
    two repos.

    What makes that a dead end rather than an annoyance is that the veto
    leaves NO CORRECT VERB: `item park` re-grades an ident that must already
    exist, so it cannot create the item; `item add` refuses it; and the
    refusal's own two offered exits are both wrong here — inflating `--hunks`
    is the override reflex, and `--source operator` writes FALSE PROVENANCE
    whenever the asker was a peer desk rather than the operator, since a
    delegation does not convert a desk's ask into the operator's decision. The
    author's only compliant move is then to not book the item at all, which is
    the silent loss the two-exits rule exists to prevent. These arms are that
    third exit.

    AT THE CLI ALTITUDE ON PURPOSE, and the reason is a measured trap rather
    than a preference: a unit call to `cost_test` carrying the new argument
    reds against the old build as a TypeError — an ERROR, which proves only
    that the signature is new and scores identically against a build that
    takes the argument and ignores it. Every arm below runs the verb the rule
    actually ships behind, where the old build accepts every flag and its red
    is an assertion FAILURE at the defect.

    THE LAST THREE ARMS MUST NOT MOVE. Without them a change that merely
    cleared more would score the same as one that got the distinction right:
    an UNTYPED blocker buys no exemption, and an unblocked one-file add still
    meets the ask and still refuses to clear what it cannot evaluate.
    """

    #: A real cross-boundary booking: one file, and the file is another
    #: repo's — the realizing write is a desk this session is not.
    FOREIGN_FILE = "../dotfiles/bootstrap/manifest.py"
    DECISION_BLOCKER = ("decision when the judgment desk lands its bundled "
                        "corpus queue")

    def _repo(self, **kw):
        r = refusals._Repo(**kw)
        self.addCleanup(r.close)
        return r

    def _run(self, repo, *argv):
        import io
        import os
        from contextlib import redirect_stdout
        from lifecycle_core import cli as cli_mod
        here = os.getcwd()
        try:
            os.chdir(str(repo.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(repo.dir)] + list(argv))
        finally:
            os.chdir(here)
        return code, buf.getvalue()

    def _add(self, *extra, write_set=None, hunks=None):
        """One `item add --join new`, slots complete, one-file write-set."""
        argv = [
            "item", "add",
            "--requirement", "the deploy roster is hand-checked — LEDGER.md",
            "--goal", "verify",
            "--write-set", write_set or self.FOREIGN_FILE,
            "--done-criterion", "the roster is declared, not hand-checked",
            "--evidence", "measured at the drainage desk",
            "--absence", "the realizing write is another desk's",
        ]
        if hunks is not None:
            argv += ["--hunks", str(hunks)]
        return argv + list(extra)

    # --- the third conjunct ---------------------------------------------

    def test_a_typed_decision_blocker_is_not_met_with_the_do_it_now_ask(self):
        """The rule's own third conjunct, at the altitude it ships at.

        One file, one hunk, session live — the first two conjuncts hold — and
        a correctly typed decision blocker, which makes the conjunction FALSE.
        The declared answer is "any other shape -> NEW", so the ask must not
        fire.
        """
        r = self._repo()
        code, out = self._run(r, *self._add(
            "--blocked-by", self.DECISION_BLOCKER, hunks=1))
        self.assertNotIn("[cost_test_veto]", out)
        self.assertEqual(code, exits.CLEAN, out)

    def test_a_typed_evidence_blocker_is_not_met_with_it_either(self):
        """The conjunct says TYPED, not `decision`. `evidence` is typed too.

        Here because a fix keyed to the one blocker type that happened to
        appear in both live firings would pass the arm above and still leave
        two thirds of §3.1's closed edge set vetoed.
        """
        r = self._repo()
        code, out = self._run(r, *self._add(
            "--blocked-by", "evidence the roster count stops moving", hunks=1))
        self.assertNotIn("[cost_test_veto]", out)
        self.assertEqual(code, exits.CLEAN, out)

    def test_the_add_to_parked_path_exists_end_to_end(self):
        """The half that makes this a dead end, not a missing parameter.

        A cross-boundary item must be creatable in ONE verb, parked, with its
        typed blocker intact — and WITHOUT a hunk count, because an author who
        cannot do the work here has no hunk count to state and the old build
        met that with COULD NOT VERIFY. The carrier is read back rather than
        the exit code trusted: an add that answers CLEAN and writes nothing
        would satisfy an exit-code assertion exactly as a real one does.
        """
        r = self._repo()
        code, out = self._run(r, *self._add(
            "--blocked-by", self.DECISION_BLOCKER, "--grade", "PARKED"))
        self.assertEqual(code, exits.CLEAN, out)
        carrier = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
        self.assertIn("grade: PARKED", carrier)
        self.assertIn(f"blocked-by: {self.DECISION_BLOCKER}", carrier)
        self.assertIn(self.FOREIGN_FILE, carrier)

    # --- must not move ----------------------------------------------------

    def test_an_untyped_blocker_buys_no_exemption(self):
        """Prose is not a typed blocker, and must not become a way past the ask.

        The exemption the spec grants is TYPED; if untyped prose bought it,
        the ask would be escapable by writing a sentence.
        """
        r = self._repo()
        code, out = self._run(r, *self._add(
            "--blocked-by", "we should think about it", hunks=1))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[blocker_untyped]", out)

    def test_an_unblocked_one_file_one_hunk_add_still_meets_the_ask(self):
        r = self._repo()
        code, out = self._run(r, *self._add("--blocked-by", "NONE", hunks=1))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[cost_test_veto]", out)

    def test_an_unblocked_one_file_add_without_hunks_is_still_unverified(self):
        r = self._repo()
        code, out = self._run(r, *self._add("--blocked-by", "NONE"))
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("COULD NOT VERIFY", out)


def _park_block(ident: str, grade: str, blocker: str,
                amended: str | None = None) -> str:
    """One fixture block, optionally carrying a superseding amendment group.

    The amendment is the LAST thing in the block, which is where
    `_resolve_amendments` requires it: a superseding line above the value it
    supersedes is its own `item_shape` finding, and a fixture that tripped it
    would red for a reason this class is not about.
    """
    body = (f"\n## {ident}\ngrade: {grade}\n"
            "requirement: a park-supersession fixture block — LEDGER.md\n"
            "goal: mitigate\nwrite-set: tools/thing.py\n"
            "done-criterion: it goes red then green\nevidence: none yet\n"
            f"blocked-by: {blocker}\n")
    if amended is not None:
        body += ("amend-reason: 2026-09-12 the earlier wait was cleared by "
                 "the retirement pass\n"
                 f"amended-blocked-by: 2026-09-12 {amended}\n")
    return body


class ParkWritesTheValueThatGoverns(unittest.TestCase):
    """`item park` cannot return CLEAN over a blocker that would not govern.

    THE DEFECT (lc-112). `cmd_item_park` wrote the BASE `blocked-by:` slot,
    and `items.parse` resolves an `amended-blocked-by:` line LAST-WINS over
    it. So on a block carrying such a line park moved the grade to PARKED,
    printed the typed blocker back and returned CLEAN while the EFFECTIVE
    blocker was untouched — the verb's output true about the slot it wrote and
    false about the item. Measured n=2 at the drain desk 2026-09-13 (lc-24 and
    lc-66, both `amended-blocked-by: 2026-09-12 NONE`), and INVISIBLE to park's
    own output: what caught it was `item check` reading the carrier the way a
    reader does.

    AT THE CLI ALTITUDE ON PURPOSE, for the reason the class above states: a
    unit call to the new helper reds against the old build as an ImportError or
    an AttributeError — an ERROR, which proves only that the name is new and
    scores identically against a build that carries the name and still writes
    the ungoverned slot. Every arm below runs the verb, where the old build
    accepts the same argv and its red is an assertion FAILURE at the defect.
    Read `failures=` vs `errors=` per arm, never the red count.

    THE CARRIER IS READ BACK, never the exit code trusted. A refusal that
    returned FINDING and had already written the slot would satisfy an
    exit-code assertion exactly as a real one does, and "nothing was written"
    is half of what this refusal promises.

    THE LAST TWO ARMS MUST NOT MOVE, and they are what decides shippability.
    An ordinary block — no amendment line — must park exactly as it did
    before, same output and same exit: a repair that changed the ordinary path
    would be a bigger behaviour change than the defect. And the block whose
    amendment ALREADY says what park was told must park too, because that is
    the state `item amend` leaves behind and therefore the second half of the
    repair route this refusal names.
    """

    TYPED = "evidence test -f docs/never-written.md"

    def _repo(self, **kw):
        r = refusals._Repo(**kw)
        self.addCleanup(r.close)
        return r

    def _run(self, repo, *argv):
        import io
        import os
        from contextlib import redirect_stdout
        from lifecycle_core import cli as cli_mod
        here = os.getcwd()
        try:
            os.chdir(str(repo.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(repo.dir)] + list(argv))
        finally:
            os.chdir(here)
        return code, buf.getvalue()

    def _carrier(self, *blocks) -> str:
        return (f"schema: 2\nbaseline: {len(blocks)}\nadded: 0\n"
                "compacted: 0\n" + "".join(blocks))

    def _effective(self, repo, ident: str):
        """What `items.parse` puts IN FORCE — the reader's answer, not park's.

        A separate instrument from the verb under test on purpose: park prints
        the value it WROTE, which is the one thing that cannot be trusted here.
        """
        parsed = items.parse(
            (repo.dir / "ITEMS.md").read_text(encoding="utf-8"))
        it = next((i for i in parsed.items if i.ident == ident), None)
        return None if it is None else it.slots.get("blocked-by")

    # --- the defect -------------------------------------------------------

    def test_park_refuses_where_an_amendment_would_supersede_its_write(self):
        """The measured defect: CLEAN over a blocker that does not govern."""
        r = self._repo(items=self._carrier(
            _park_block("xx-1", "READY", "NONE", amended="NONE")))
        before = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
        code, out = self._run(r, "item", "park", "xx-1",
                              "--blocked-by", self.TYPED)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[park_over_superseding_amendment]", out)
        self.assertEqual(self._effective(r, "xx-1"), "NONE", out)
        self.assertEqual((r.dir / "ITEMS.md").read_text(encoding="utf-8"),
                         before,
                         "the refusal wrote to the carrier")

    def test_the_grade_does_not_move_on_that_refusal(self):
        """The half `item check` caught: PARKED beside an untyped blocker.

        Its own arm because the grade and the blocker are two writes of one
        `_set_slots` call, and a repair that refused the blocker while letting
        the grade through would produce exactly the state the drain desk
        measured — and would pass the arm above.
        """
        r = self._repo(items=self._carrier(
            _park_block("xx-1", "READY", "NONE", amended="NONE")))
        code, out = self._run(r, "item", "park", "xx-1",
                              "--blocked-by", self.TYPED)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("grade: READY",
                      (r.dir / "ITEMS.md").read_text(encoding="utf-8"))

    def test_it_fires_on_a_TYPED_amendment_that_merely_differs(self):
        """DISCRIMINATION, and the arm a narrower fix would fail.

        Both measured instances amended to NONE, so a repair keyed to "the
        effective blocker is untyped" would pass every other arm here and still
        return CLEAN over this one — a typed amendment the park write does not
        govern either. The invariant is that the EFFECTIVE blocker equals the
        value given, not that it is typed.
        """
        r = self._repo(items=self._carrier(
            _park_block("xx-1", "READY", "NONE",
                        amended="decision which window is canonical")))
        code, out = self._run(r, "item", "park", "xx-1",
                              "--blocked-by", self.TYPED)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[park_over_superseding_amendment]", out)
        self.assertEqual(self._effective(r, "xx-1"),
                         "decision which window is canonical", out)

    def test_the_refusal_names_the_verb_that_does_supersede(self):
        """A refusal that does not name the route is a dead end (R11's
        sibling): the desk repaired both measured items through `item amend`,
        and that is the exit this refusal has to hand the next author."""
        r = self._repo(items=self._carrier(
            _park_block("xx-1", "READY", "NONE", amended="NONE")))
        _code, out = self._run(r, "item", "park", "xx-1",
                               "--blocked-by", self.TYPED)
        self.assertIn("item amend xx-1", out)
        self.assertIn("--reason", out)

    # --- must not move ----------------------------------------------------

    def test_a_block_with_no_amendment_parks_exactly_as_before(self):
        """THE ORDINARY PATH, unchanged: same output, same write, same exit."""
        r = self._repo(items=self._carrier(
            _park_block("xx-1", "READY", "NONE")))
        code, out = self._run(r, "item", "park", "xx-1",
                              "--blocked-by", self.TYPED)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn(f"xx-1 → PARKED, blocked-by: {self.TYPED}", out)
        self.assertEqual(self._effective(r, "xx-1"), self.TYPED, out)
        self.assertIn("grade: PARKED",
                      (r.dir / "ITEMS.md").read_text(encoding="utf-8"))

    def test_an_amendment_already_saying_it_parks_too(self):
        """The state `item amend` leaves — the refusal's own repair route.

        Here because a predicate keyed to the mere PRESENCE of an
        `amended-blocked-by:` line would refuse this forever, which would make
        the fix the refusal names unreachable: amend, then park, then refused
        again. The value in force already equals the value given, so there is
        nothing to refuse.
        """
        r = self._repo(items=self._carrier(
            _park_block("xx-1", "READY", "NONE", amended=self.TYPED)))
        code, out = self._run(r, "item", "park", "xx-1",
                              "--blocked-by", self.TYPED)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(self._effective(r, "xx-1"), self.TYPED, out)
        self.assertIn("grade: PARKED",
                      (r.dir / "ITEMS.md").read_text(encoding="utf-8"))

    def test_an_untyped_blocker_is_still_refused_before_any_of_this(self):
        """`parked_without_typed_blocker` still owns its case, and first.

        The new check sits after the typed gate, so a prose blocker must still
        produce the OLD refusal — a new check that shadowed the named one would
        leave every author reading the vaguer message forever.
        """
        r = self._repo(items=self._carrier(
            _park_block("xx-1", "READY", "NONE", amended="NONE")))
        code, out = self._run(r, "item", "park", "xx-1",
                              "--blocked-by", "we should think about it")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[parked_without_typed_blocker]", out)
        self.assertNotIn("[park_over_superseding_amendment]", out)


class CloseRefusesADeclaredCarriedPointer(unittest.TestCase):
    """`item close` cannot file a body that declares a forward-carrier clause.

    THE DEFECT (lc-22). The closure MOVE had no guard against carrying a
    declared obligation into the closure home. An entry can name itself the
    carrier for a pointer another desk still owes — "this entry is the carrier
    that moves with it", the real clause's own words — and when its own work
    closed, the move filed that clause among the closed bodies, where the
    obligation then read as discharged because its carrier was filed as
    discharged.

    THE INPUT IS THE REAL ONE. `refusals.CARRIED_POINTER_CLAUSE` is the L10
    entry's own text, read out of dotfiles `claude/BACKLOG.md` at `bb8edd4`
    rather than composed here; the constant's comment carries the provenance
    and the single transformation (unwrapping) the carrier's shape rule forces.

    AT THE CLI ALTITUDE, for the reason the park class above states: a unit
    call to the new helper reds against the old build as an AttributeError —
    an ERROR, which proves only that the name is new. Every arm here but the
    corpus one runs the verb, where the old build accepts the same argv and
    its red is an assertion FAILURE at the defect. Read `failures=` vs
    `errors=` per arm, never the red count. THE CORPUS ARM IS THE EXCEPTION
    and says so in its own docstring.

    BOTH HOMES ARE READ BACK BYTE-FOR-BYTE, never the exit code trusted. A
    refusal that returned FINDING after appending to the closure home would
    satisfy an exit-code assertion exactly as a real one does, and "the move
    did not happen" is half of what this refusal promises.

    THE MUST-NOT-MOVE ARM ASKS AN INSTRUMENT INDEPENDENT OF THE THING ON
    TRIAL: it reads the two homes and the parsed carrier, never the predicate,
    because an arm that asked the predicate whether the predicate had stayed
    quiet would swallow its own proof.
    """

    #: A body about carriers and pointers that declares NOTHING — the same 384
    #: bytes as the plant with the marker respelled. It is the control for the
    #: refusal AND the over-fire probe, since it still says "this entry is the
    #: carrier that moves with it".
    PROSE = refusals.CARRIED_POINTER_PROSE_ITEMS
    PLANT = refusals.CARRIED_POINTER_ITEMS

    #: This repo's own prose, none of it written as a fixture for this guard.
    CORPUS = ("CLAUDE.md", "JOURNAL.md", "LEDGER.md", "ITEMS.md",
              "ITEMS-DONE.md")
    REPO = Path(__file__).resolve().parents[1]

    def _repo(self, **kw):
        r = refusals._Repo(**kw)
        self.addCleanup(r.close)
        return r

    def _run(self, repo, *argv):
        import io
        import os
        from contextlib import redirect_stdout
        from lifecycle_core import cli as cli_mod
        here = os.getcwd()
        try:
            os.chdir(str(repo.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(repo.dir)] + list(argv))
        finally:
            os.chdir(here)
        return code, buf.getvalue()

    def _homes(self, repo):
        return ((repo.dir / "ITEMS.md").read_bytes(),
                (repo.dir / "ITEMS-DONE.md").read_bytes())

    # --- the defect -------------------------------------------------------

    def test_the_real_clause_REFUSES_the_close(self):
        """The measured defect: the move went through and said nothing."""
        r = self._repo(items=self.PLANT)
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[close_carries_pointer]", out)

    def test_the_refusal_QUOTES_the_clause_it_found(self):
        """A refusal naming no text leaves the author hunting for it.

        The whole clause, never a prefix: a quotation cut to a column width is
        a partial view standing in for its body, and the reader cannot tell a
        short clause from a clipped one.
        """
        r = self._repo(items=self.PLANT)
        _code, out = self._run(r, "item", "close", "xx-1")
        self.assertIn(refusals.CARRIED_POINTER_CLAUSE, out)

    def test_NEITHER_home_moved_a_byte(self):
        """The move must not have happened — the refusal's other half."""
        r = self._repo(items=self.PLANT)
        before = self._homes(r)
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.FINDING, out)
        self.assertEqual(self._homes(r), before,
                         "a home changed under a refusal that promises no move")

    def test_a_DROP_is_refused_too(self):
        """A drop MOVES the body as well, so the clause lands either way.

        No carve-out is made for `--drop`: an abandoned item's residue is the
        orphaned-pointer case rather than an exception to it, and the clause
        reaches the closure home by the same act.
        """
        r = self._repo(items=self.PLANT)
        before = self._homes(r)
        code, out = self._run(r, "item", "close", "xx-1", "--drop",
                              "--reason", "overtaken by the schema wave")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[close_carries_pointer]", out)
        self.assertEqual(self._homes(r), before)

    # --- must not move ----------------------------------------------------

    def test_a_body_DISCUSSING_carriers_closes_exactly_as_before(self):
        """The over-fire arm at the verb: the same bytes, marker respelled.

        Graded by the HOMES and by `items.parse`, never by the predicate: an
        arm that asked the thing on trial whether it had stayed quiet would
        report its own silence as a pass.
        """
        r = self._repo(items=self.PROSE)
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("[close_carries_pointer]", out)

        live = items.parse((r.dir / "ITEMS.md").read_text(encoding="utf-8"))
        done = items.parse(
            (r.dir / "ITEMS-DONE.md").read_text(encoding="utf-8"))
        self.assertEqual([i.ident for i in live.items], [])
        closed = next(i for i in done.items if i.ident == "xx-1")
        self.assertEqual(closed.grade, "DONE")
        self.assertIn("this entry is the carrier that moves with it",
                      closed.slots["requirement"])

    def test_an_ORDINARY_item_closes_exactly_as_before(self):
        """Nothing about carriers at all — the plain path, unchanged."""
        r = self._repo(items=refusals.SEED_ITEMS)
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("[close_carries_pointer]", out)
        done = items.parse(
            (r.dir / "ITEMS-DONE.md").read_text(encoding="utf-8"))
        self.assertEqual([i.ident for i in done.items], ["xx-1"])

    # --- the wider over-fire arm ------------------------------------------

    def test_the_predicate_is_silent_over_this_repos_OWN_prose(self):
        """The arm the class devbook calls the one that matters — real prose.

        REACHES THROUGH A NEW NAME, so against the old build this arm reds as
        an ERROR and proves only that the code is new. It is not a defect red
        and is not reported as one; it PINS a property, and its proof is the
        pair the devbook demands for that case: loosen the predicate to the
        words the design forbids and this arm goes red as an assertion FAILURE
        (measured: 252 lines), while the positive control below proves the arm
        can see the condition at all.

        A ZERO HERE IS ONLY A FINDING WITH THE CONTROL IN THE SAME RUN: a
        pattern that could never match returns exactly what a true absence
        returns.
        """
        from lifecycle_core import verbs
        self.assertTrue(
            verbs._carried_pointer_lines(refusals.CARRIED_POINTER_CLAUSE),
            "positive control silent — the instrument is dead, and every zero "
            "below means nothing")

        hits = []
        for name in self.CORPUS:
            path = self.REPO / name
            self.assertTrue(path.exists(),
                            f"{name} is not here: this arm grades the REAL "
                            "prose and cannot verify without it")
            text = path.read_text(encoding="utf-8")
            hits += [f"{name}:{n}: {line}"
                     for n, line in verbs._carried_pointer_lines(text)]
        self.assertEqual(hits, [], "the predicate fires on prose nobody wrote "
                                   "as a fixture — over-firing on legitimate "
                                   "work stops the lane (R11)")
