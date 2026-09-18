"""The carrier parser and shape check, beyond what the refusal rows cover.

The rows in `refusals.py` prove each REFUSAL fires. These cover the parser's
other obligations — the ones whose failure is silent rather than loud: an
archive section that must NOT be shape-checked, an absent file that must not
read as an empty one, and the census's refusal to guess.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

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

    def _live(self):
        parsed = items.parse((self.REPO / "ITEMS.md").read_text(encoding="utf-8"))
        return parsed.items

    def _subject(self, predicate, what):
        """A live item satisfying `predicate`, chosen at RUN TIME.

        ANCHORED TO A PROPERTY, NEVER TO AN ID. Both arms below grade the
        REAL carrier, and every live id is mutating state: the item an arm
        names closes one day, the lookup raises, and the red belongs to a
        legitimate close rather than to `item slots`. MEASURED 2026-09-15 —
        closing `lc-22` errored this class with `StopIteration`, and the
        sibling arm pinned `lc-7` exactly the same way, so the class held
        one landmine per arm. What each arm needs is a SHAPE (amended, or
        not), which the carrier keeps supplying whoever closes what.

        NO SUBJECT IS COULD NOT VERIFY, never a silent pass: an arm that
        selected nothing would assert nothing and read green, which is the
        pass-shaped number law 1 forbids. The repo's own idiom for a real
        input that is absent today is a skip that NAMES what is missing
        (see `test_pre_push_hook`'s no-carrier arm).
        """
        for it in self._live():
            if predicate(it):
                return it
        self.skipTest(f"no live item {what}: this arm grades the REAL "
                      "carrier and has no subject today — COULD NOT VERIFY, "
                      "not a pass")

    @staticmethod
    def _amended_evidence(item):
        return [raw.split(" ", 1)[1] for name, raw, _ in item.amendments
                if name == "amended-evidence"]

    def test_an_AMENDED_item_reports_the_LAST_evidence_not_the_first(self):
        item = self._subject(
            lambda it: len(self._amended_evidence(it)) >= 2,
            "carrying two or more `amended-evidence` lines")
        evidence = self._amended_evidence(item)
        self.assertNotEqual(evidence[0], evidence[-1],
                            "the real-carrier discriminator vanished: this "
                            "subject's first and last amendment are equal, so "
                            "a first-wins implementation would pass")

        code, out = self._run(item.ident)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn(f"evidence: {evidence[-1]}", out)
        self.assertNotIn(f"evidence: {evidence[0]}", out)

    def test_an_UNAMENDED_item_reports_base_slots_byte_unchanged(self):
        item = self._subject(
            lambda it: not it.amendments
            and all(s in it.slots for s in items.SLOTS),
            "carrying no amendments and all fixed slots")

        code, out = self._run(item.ident)
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

    def test_amendment_order_is_FILE_order_not_DATE_order(self):
        """lc-126 — the LAST-WINS rule (`_resolve_amendments`, items.py)
        reads order off the FILE, never off the dates on the amendment
        lines. Every existing arm in this class has the two orders
        agreeing — the arm above carries the SAME date, `2026-08-27`, on
        both corrections — so none of them can tell "last line in the file
        wins" from "latest date wins" apart. This fixture forces the two
        orders to DIVERGE: the amendment FIRST in the file carries the
        LATER date (`2026-09-01`), the one LAST in the file carries the
        EARLIER date (`2026-08-01`).

        RED-FIRST, per the class devbook's rule for a check that pins an
        ALREADY-TRUE property (no red exists against the shipped build —
        `_resolve_amendments` already reads order off the file, never the
        date): proven by TWO mutations, both assertion failures, run by
        hand against a scratch copy before this arm was written.
          * of the BUILD it grades — a resolver that sorts
            `item.amendments` by the ISO date on each `amended-<slot>:`
            line (a stable sort, so same-day pairs keep file order)
            instead of the shipped code's plain file-order loop. Against
            this fixture `goal` resolves to `"verify"` (the LATER-dated
            line) instead of `"retire"`, and the main assertion below —
            run against that mutated resolver — fails.
          * of its own ARRANGEMENT — swap the two dates so file order and
            date order AGREE (the later line also carries the later date,
            as the arm above does): the shipped build and the date-sorted
            mutation then produce the SAME value on that fixture, so a
            green there proves nothing — exactly the non-discrimination
            this entry exists to remove.
        `_resolve_by_date` below is the first mutation kept in the
        battery, never imported by production code, so the discriminator
        assertion is re-run on every pass rather than trusted from a
        one-off scratch run.
        """
        fixture = self._amended(
            "amend-reason: 2026-08-27 the goal was mis-recorded at intake",
            "amended-goal: 2026-09-01 verify",
            "amend-reason: 2026-08-27 verify was wrong too",
            "amended-goal: 2026-08-01 retire")

        p = items.parse(fixture)
        self.assertEqual(p.problems, [])
        self.assertEqual(
            p.items[0].slots["goal"], "retire",
            "FILE order must win: 'retire' is the LAST amendment line in "
            "the block even though its date (2026-08-01) is EARLIER than "
            "the first amendment's (2026-09-01) — a date-order resolver "
            "would pick 'verify' instead")

        by_date = self._resolve_by_date(items.parse(fixture).items[0])
        self.assertEqual(
            by_date, "verify",
            "the date-order mutation must pick the OTHER value on this "
            "fixture, or the fixture does not discriminate 'last in the "
            "file' from 'latest date' at all")
        self.assertNotEqual(
            p.items[0].slots["goal"], by_date,
            "the two rules agree on this fixture — a green here would "
            "prove nothing, which is the non-discrimination this entry "
            "exists to remove")

    @staticmethod
    def _resolve_by_date(item):
        """The BUILD mutation this arm's docstring proves against:
        `_resolve_amendments` with its file-order loop replaced by a
        stable sort on the ISO date of each `amended-<slot>:` line. Lives
        only here, never imported by `lifecycle_core`, as the re-runnable
        half of the class devbook's red-first proof for an already-true
        property — the other half (the arrangement mutation) is prose in
        the caller's docstring, since it changes the FIXTURE, not the
        code, and has no separate implementation to keep.
        """
        ordered = sorted(
            item.amendments,
            key=lambda entry: (items._AMEND_VALUE.match(entry[1]).group(1)
                               if items._AMEND_VALUE.match(entry[1])
                               else ""))
        value = None
        for name, raw, _lineno in ordered:
            if name == items.AMEND_REASON:
                continue
            m = items._AMEND_VALUE.match(raw)
            if not m:
                continue
            slot = name[len(items.AMEND_PREFIX):]
            if slot == "goal":
                value = m.group(2)
        return value

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
        # DERIVED, for the reason this whole class exists. A hardcoded
        # `["closed-reason", "closed-ref"]` here is the restated enumeration
        # one level up — inside the positive CONTROL, where it ages exactly as
        # badly and is harder to see. It went red when lc-120 added a fifth
        # slot, which is this arm catching its own defect rather than the
        # vocabulary's; the expectation now grows with the source.
        expected = [s for s in items.DONE_ONLY_SLOTS
                    if s not in ("superseded-by", "blocker-moot")]
        self.assertTrue(expected,
                        "the control cannot discriminate: the pre-lc-44 text "
                        "names every slot the vocabulary now holds, so an "
                        "empty `missing` would prove nothing")
        self.assertEqual(missing, expected,
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

    def test_a_carrier_with_no_blockers_STATES_WHAT_IT_EXAMINED(self):
        """lc-186 — and this arm asserted SILENCE until today.

        It was `test_a_carrier_with_no_blockers_says_nothing`, pinning
        `self.assertEqual(out, "")`. The silence was deliberate once: with no
        item-id blockers there is nothing to resolve, so the verb said
        nothing. But a verdict with no output is not readable AS a verdict —
        a carrier with no blockers and a check that never ran produce the
        same empty report, which is the absence claim lc-172 removed
        everywhere else and did not reach here.

        The verdict is unchanged: CLEAN, and zero is still zero. What moved
        is that the zero now carries the population it was measured over.
        """
        code, out = self._run(GOOD_ITEMS)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("0 item-id blocker(s)", out)
        self.assertIn("block(s) examined", out,
                      "the clean line claims an absence without naming the "
                      "population it read")


def _done_home_holding(ident, grade):
    """The done home with one closed body at the named GRADE.

    THE ARMS BELOW DIFFER IN THE GRADE ALONE, which is what makes the pair
    say anything: a fixture that also moved the id would be red for a
    neighbouring reason and would prove nothing about the grade.
    """
    return EMPTY_DONE + (
        f"\n## {ident}\ngrade: {grade}\n"
        "requirement: the closed target — LEDGER.md\ngoal: mitigate\n"
        "write-set: tools/thing.py\ndone-criterion: done\n"
        "evidence: none yet\nblocked-by: NONE\n")


class BlockerTargetDropped(BlockerTargets):
    """lc-29 — the carrier check reaches the DROPPED target the write side
    already refuses.

    THE ASYMMETRY THIS CLOSES: `verbs._check_blocker` refuses a blocker
    naming a DROPPED id at `item add`, `item park` and `item amend`, and the
    `item ready` resolver reports the same; only the carrier check asked
    whether the id merely EXISTS. A blocker resolves on its target's DONE,
    and a dropped target never reaches DONE — so the block waits forever and
    drains never, which is the same PERMANENT SILENT PARK the dangling-id
    half exists to catch, one grade over.

    IT INHERITS `BlockerTargets` DELIBERATELY: every must-not-move arm there
    — the other three blocker forms, the live-id control, the two
    could-not-verify answers, the silent clean carrier — re-runs under this
    class too, so a widening that broke one of them cannot ship quietly.
    """

    def test_a_DROPPED_target_is_a_finding(self):
        """RED-FIRST AT THE DEFECT. On the old side this carrier reported
        `blocker targets: CLEAN` in so many words — the write path refuses
        the same blocker and the carrier check passed it."""
        code, out = self._run(FOUR_BLOCKER_ITEMS,
                              done=_done_home_holding("xx-9999", "DROPPED"))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [dangling_reference]", out)
        self.assertIn("DROPPED", out)
        self.assertIn("xx-9999", out)
        self.assertIn("'xx-1'", out)

    def test_a_DONE_target_at_the_same_site_stays_CLEAN(self):
        """THE OTHER HALF OF THE PAIR, differing in the GRADE ALONE. A check
        that fired on any closed target would score identically against the
        arm above while refusing a wait that HAS been answered."""
        code, out = self._run(FOUR_BLOCKER_ITEMS,
                              done=_done_home_holding("xx-9999", "DONE"))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("blocker targets: CLEAN", out)

    def test_the_other_three_forms_do_not_fire_beside_a_DROPPED_target(self):
        """THE OVER-FIRE ARM, asked in the state the widening creates rather
        than in the clean one: a scope test run against a carrier with
        nothing to find passes on a check that ignores the forms entirely."""
        code, out = self._run(FOUR_BLOCKER_ITEMS,
                              done=_done_home_holding("xx-9999", "DROPPED"))
        self.assertEqual(out.count("FINDING [dangling_reference]"), 1, out)
        for must_not in ("xx-2", "xx-3", "xx-4", "decision which window",
                         "evidence test -f /nonexistent"):
            self.assertNotIn(must_not, out)

    def test_an_id_in_NEITHER_home_keeps_its_OWN_finding(self):
        """MUST-NOT-MOVE. The dangling-id case is not reclassified into the
        dropped one: its message says the id is in neither home, which is a
        different repair from retargeting a dropped one. An assertion on the
        row name alone would pass on either message."""
        code, out = self._run(FOUR_BLOCKER_ITEMS)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("NEITHER home", out)
        self.assertNotIn("DROPPED", out)

    def test_the_DROPPED_body_is_found_BESIDE_other_closed_bodies(self):
        """The lookup resolves the id, not merely the presence of a dropped
        body somewhere in the done home. A check that asked "is anything
        DROPPED here?" would pass this arm and the next one identically."""
        done = (_done_home_holding("xx-5000", "DONE")
                + "\n## xx-9999\ngrade: DROPPED\n"
                  "requirement: the dropped target — LEDGER.md\n"
                  "goal: mitigate\nwrite-set: tools/thing.py\n"
                  "done-criterion: done\nevidence: none yet\n"
                  "blocked-by: NONE\n")
        code, out = self._run(FOUR_BLOCKER_ITEMS, done=done)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("xx-9999", out)

    def test_a_DONE_target_stays_CLEAN_though_a_DROPPED_body_sits_beside_it(
            self):
        """THE OTHER HALF OF THAT PAIR, differing in WHICH id the blocker
        names. The same done home, the same dropped body present — a check
        keyed on the home rather than on the target fires here too."""
        done = (_done_home_holding("xx-5000", "DONE")
                + "\n## xx-9999\ngrade: DROPPED\n"
                  "requirement: the dropped target — LEDGER.md\n"
                  "goal: mitigate\nwrite-set: tools/thing.py\n"
                  "done-criterion: done\nevidence: none yet\n"
                  "blocked-by: NONE\n")
        code, out = self._run(FOUR_BLOCKER_ITEMS.replace(
            "blocked-by: xx-9999", "blocked-by: xx-5000"), done=done)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("FINDING", out)


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
            "--evidence", "MEASURED at the drainage desk",
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
            "--blocked-by", self.DECISION_BLOCKER,
            "--not-derivable", "a preference with no precedent in the ledger — constitutively the operator's", hunks=1))
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
            # THE PREDICATE IS A SHELL PREDICATE, and this fixture used to
            # spell it as bare prose — an instance of the very class lc-130's
            # mint lint exists to refuse (it parses, then exits 127,
            # `the: command not found`). Respelled in the carrier's OWN idiom
            # for a wait that has not arrived (`evidence false  # <prose>`,
            # live at ITEMS.md:13 and :24): exit 1, still waiting, which is
            # what this arm's name asserts. `:` would also mint, but it exits
            # 0 — "the evidence ARRIVED" — and that is not what a fixture
            # named `is_not_met` should say. The arm's SUBJECT is untouched:
            # it grades the cost test's third conjunct, which is about the
            # blocker being TYPED, never about how it resolves.
            "--blocked-by", "evidence false  # the roster count stops moving",
            hunks=1))
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
            "--blocked-by", self.DECISION_BLOCKER,
            "--not-derivable", "the judgment desk's schedule is not in any record here", "--grade", "PARKED"))
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

    #: THE TRUE SOURCE LINE, byte-for-byte: dotfiles `claude/BACKLOG.md` at
    #: `bb8edd4`, line 163 — `git show bb8edd4:claude/BACKLOG.md | sed -n
    #: '163p'`, read back through `cat -A` to pin the whitespace. TWO LEADING
    #: SPACES and `commit. ` BEFORE the marker: in the wild the declaration
    #: does NOT sit at column 0, and that is the property the arm below pins.
    #:
    #: WHY IT IS PINNED BY NAME rather than left to the fixtures. Every OTHER
    #: fixture here reaches the predicate through `_clause_block`, which
    #: renders `requirement: {value}` — so each one carries prose before the
    #: marker INCIDENTALLY, as a side effect of the slot rendering, and would
    #: go on carrying it only for as long as that rendering happens to look
    #: that way. A property no test names is a property the next refactor is
    #: free to drop, and its loss would be silent: the fixtures would still
    #: pass, against a predicate that had stopped matching the real thing.
    SOURCE_LINE = ("  commit. CARRIED POINTER (module 1 residue, 2026-08-26): "
                   "accretion.md's")

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
        # THE CONTROL IS PREFIXED AT THE CALL SITE, and the prefix is the
        # whole point of it. `CARRIED_POINTER_CLAUSE` begins AT the marker, so
        # as a bare string its line 1 puts the declaration at column 0 — the
        # one shape the real source line never has. A control in that shape
        # certifies the arm against a predicate anchored to the start of a
        # line, which is a predicate that would MISS every clause in the wild:
        # measured, a `^`-anchored twin leaves this arm green while reding
        # four arms at the verb altitude. An arm whose control cannot see the
        # property it certifies is a weaker instrument than it reads as. The
        # constant itself stays untouched — it is the plant's subject and the
        # quoted-clause arm's expectation, and prefixing it there would move
        # two other arms' subjects to fix this one's control.
        self.assertTrue(
            verbs._carried_pointer_lines(
                "commit. " + refusals.CARRIED_POINTER_CLAUSE),
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

    # --- the mid-line property, pinned by name ----------------------------

    def test_the_marker_is_found_MID_LINE_not_only_at_column_zero(self):
        """The declaration is anchored to ITSELF, never to the line's start.

        THE INPUT IS THE REAL SOURCE LINE, byte-for-byte (`SOURCE_LINE`
        above): two leading spaces and `commit. ` before the marker. That is
        how the clause actually occurs, and no other arm in this class states
        it — the rest reach the predicate through `_clause_block`, which puts
        `requirement: ` in front of the marker as a side effect of rendering a
        slot. They therefore exercise the property by accident, and a rename
        or a re-rendering of that helper would drop it with every one of them
        still green.

        THE PAIR IS OVER ONE PROPERTY, THE MARKER'S SPELLING. The positive is
        the source line; the negative is the SAME line with `CARRIED POINTER`
        respelled as prose, so it keeps the leading whitespace, the `commit. `
        prefix and the subject, and differs in the declaration alone. Without
        the negative the positive would pass against a predicate that matched
        any line whatsoever.

        WHAT PROVES THIS ARM, since it pins a property the shipped build
        already has and so has no red of its own (class devbook: such a check
        earns its place by TWO mutations, both assertion FAILURES):
          * of the BUILD it grades — anchor the predicate with `^` and the
            positive half fails, because the marker is not at column 0 here.
            That is the defect this property excludes;
          * of its own ARRANGEMENT — respell the marker inside SOURCE_LINE
            and the positive half fails against the SHIPPED build, which is
            what shows the arm reads the declaration in this fixture rather
            than passing on the fixture merely existing.
        A THIRD OBSERVATION, not one of the two reds because it produces a
        GREEN: under the `^`-anchored build a SOURCE_LINE with its `commit. `
        prefix removed matches again. That is what identifies the prefix,
        rather than anything else on the line, as the load-bearing part.
        """
        from lifecycle_core import verbs

        found = verbs._carried_pointer_lines(self.SOURCE_LINE)
        self.assertEqual(
            [line for _n, line in found], [self.SOURCE_LINE.strip()],
            "the declaration was not found mid-line. A predicate that only "
            "matches at column 0 misses every clause as it actually occurs: "
            "the source line carries `commit. ` before the marker, and a "
            "carrier's own slot rendering puts `requirement: ` there")

        respelled = self.SOURCE_LINE.replace(
            "CARRIED POINTER", "a carried pointer", 1)
        self.assertEqual(
            verbs._carried_pointer_lines(respelled), [],
            "the same line without the DECLARATION still matched, so what "
            "the positive half found was not the marker — the pair differs "
            "in the marker's spelling and in nothing else")


class TheAllocatorsHomesAreWhateverItIsGIVEN(unittest.TestCase):
    """lc-148's contract, pinned where the allocator lives.

    HONEST ABOUT ITS OWN REACH: this arm passes against the build that had the
    defect, and that is not a reason to leave it out. `next_ident` was never
    wrong about the homes it was given — it reads every `Parsed` it receives
    and always did — so what is pinned here is the SHAPE the callers now
    depend on: a third home, carried in the same variadic, counts exactly like
    the carriers. The discriminating reds for lc-148 are the end-to-end arms
    in `test_retire.py`, where the caller assembles the homes and where the id
    actually came back into circulation.
    """

    def _home(self, *idents) -> items.Parsed:
        p = items.Parsed()
        for n, ident in enumerate(idents, start=1):
            p.items.append(items.Item(ident=ident, slots={}, line=n))
        return p

    def test_an_id_only_a_THIRD_home_holds_is_not_re_issued(self):
        live = self._home("xx-2")
        done = self._home()
        compacted = self._home("xx-1")
        ident, why = items.next_ident("xx", live, done, compacted)
        self.assertIsNone(why)
        self.assertEqual(ident, "xx-3")

    def test_the_SAME_call_without_that_home_mints_the_freed_id(self):
        """The pair. Without it the arm above passes on an allocator that
        returns `xx-3` for its own reasons, and the third home would be
        proving nothing."""
        live = self._home("xx-2")
        done = self._home()
        ident, why = items.next_ident("xx", live, done)
        self.assertIsNone(why)
        self.assertEqual(ident, "xx-1")

    def test_an_EMPTY_third_home_changes_no_allocation(self):
        """MUST-NOT-MOVE for every repo that has never compacted: an empty
        home is not a missing one, and it must not shift a single id."""
        live = self._home("xx-1")
        done = self._home("xx-3")
        self.assertEqual(items.next_ident("xx", live, done)[0],
                         items.next_ident("xx", live, done, self._home())[0])

    def test_no_id_prefix_still_REFUSES_whatever_homes_it_is_given(self):
        """MUST-NOT-MOVE: the refusal is about the DECLARATION and a third
        home does not answer it."""
        ident, why = items.next_ident("", self._home(), self._home(),
                                      self._home("xx-1"))
        self.assertIsNone(ident)
        self.assertIn("id-prefix", why)


class ForwardPointerShape(unittest.TestCase):
    """lc-120 — the done home ACCEPTS a well-formed pointer and grades the rest.

    Acceptance is the half a verb cannot assert about itself: the verb writes
    the line and this decides whether the carrier's own check reads it back as
    well-formed. The two must agree by construction, which is why the verb
    grades what it is about to write with the predicate used here.
    """

    POINTER = ("closure-superseded-by: 2026-09-15 7113d78 the closure reason "
               "was falsified the same hour\n")

    def _done(self, *extra: str) -> str:
        return EMPTY_DONE + "\n" + DONE_BLOCK + "".join(extra)

    def test_a_well_formed_pointer_reads_CLEAN(self):
        code, out = run_done_check(self._done(self.POINTER))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("unknown slot", out)

    def test_the_SAME_body_WITHOUT_the_pointer_is_also_clean(self):
        """The control. Without it, the arm above passes equally against a
        check that stopped grading the done home at all."""
        code, out = run_done_check(self._done())
        self.assertEqual(code, exits.CLEAN, out)

    def test_TWO_pointers_on_one_body_read_CLEAN(self):
        """They repeat by design — a body needing a second correction is
        exactly the case a single-valued slot would strand."""
        second = ("closure-superseded-by: 2026-09-16 abc1234 and the evidence "
                  "slot too\n")
        code, out = run_done_check(self._done(self.POINTER, second))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("repeats slot", out)

    def test_each_MALFORMED_shape_is_named_rather_than_accepted(self):
        """Per case, not in aggregate: an aggregate arm passes against a check
        that refuses every pointer, well-formed or not — and the clean arms
        above would then be the ones failing, which is a different report."""
        for label, value, expect in (
                ("no date", "7113d78 the reason was falsified", "is not"),
                ("no ref", "2026-09-15", "is not"),
                ("ref but no line", "2026-09-15 7113d78", "is not"),
                ("empty", "", "is empty"),
                ("date not ISO", "15-09-2026 7113d78 falsified", "is not")):
            with self.subTest(case=label):
                code, out = run_done_check(
                    self._done(f"closure-superseded-by: {value}\n"))
                self.assertEqual(code, exits.FINDING, out)
                self.assertIn("[item_shape]", out)
                # THE PREDICATE'S OWN MESSAGE, not merely `item_shape` plus the
                # slot name. A build with NO well-formedness check answers
                # `unknown slot(s): closure-superseded-by` — same row, same
                # exit, and the slot name appears in it — so the looser
                # assertion passes on a build that grades nothing. Measured
                # against the old tree, where this arm was green before the
                # check existed.
                self.assertIn(expect, out)
                self.assertNotIn("unknown slot", out)

    def test_a_LIVE_block_carrying_the_slot_is_a_finding(self):
        """Closed-only, like every other slot a CLOSURE writes: on a live item
        the line claims an act that has not happened."""
        live = GOOD_ITEMS.rstrip("\n") + "\n" + self.POINTER
        code, out = run_check(live)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[done_slot_on_live_item]", out)

    def test_a_pointer_AMONG_the_fixed_slots_is_a_finding(self):
        """The appended lines sit after the block's own slots, so a diff over
        an annotated body shows an addition rather than a reordering."""
        misplaced = DONE_BLOCK.replace("goal: mitigate\n",
                                       "goal: mitigate\n" + self.POINTER, 1)
        code, out = run_done_check(EMPTY_DONE + "\n" + misplaced)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[item_shape]", out)
        # The ORDERING message, for the reason the malformed arm states: a
        # build that merely calls the slot unknown answers `item_shape` here
        # too, so the looser assertion is green on a build that has never
        # heard of the slot and cannot be placing it anywhere.
        self.assertIn("among the fixed slots", out)
        self.assertNotIn("unknown slot", out)

    def test_the_predicate_has_ONE_home_the_writer_and_reader_share(self):
        """The writer grades what it is about to write with the predicate the
        parser grades it with. Asserted directly, because the failure of a
        second spelling is SILENT: the writer keeps producing a shape the
        reader has stopped recognising."""
        self.assertIsNone(items.closure_pointer_problem(
            "2026-09-15 7113d78 the reason was falsified"))
        self.assertIsNotNone(items.closure_pointer_problem("2026-09-15"))
        rendered = items.render_closure_pointer("2026-09-15", "7113d78",
                                                "the reason was falsified")
        self.assertTrue(rendered.startswith("closure-superseded-by: "))
        value = rendered.split(": ", 1)[1]
        self.assertIsNone(items.closure_pointer_problem(value),
                          "the renderer produced a value its own reader "
                          "refuses")


class GoalFilteredListing(unittest.TestCase):
    """lc-16 — `item ready --goal`, and the two ways of returning nothing.

    A repo can declare a closed goal set and set a goal per item, then have
    no way to read the carrier back by it. The fix is a listing; the SUBSTANCE
    is that an UNDECLARED goal and a declared goal holding no ready work both
    return no rows and are different answers. Folding them together prints a
    zero shaped exactly like a measurement, which is the false zero this repo
    exists to remove — and a typo is the commonest way to make one.

    THE LOAD-BEARING ASSERTION IS THE NEGATIVE. "The wanted ident appears"
    passes for a filter that filters nothing; only "the OTHER goal's ident is
    ABSENT" separates a working filter from a listing that ignored the flag.
    """

    TWO_GOALS = """schema: 2
baseline: 0

## xx-1
grade: READY
requirement: the verify-goal entry — record: LEDGER.md
goal: verify
write-set: tools/a.py
done-criterion: it goes red on the real defect
evidence: measured here
blocked-by: NONE

## xx-2
grade: READY
requirement: the mitigate-goal entry — record: LEDGER.md
goal: mitigate
write-set: tools/b.py
done-criterion: it goes red on the real defect
evidence: measured here
blocked-by: NONE
"""

    def _run(self, *argv, items_text=None):
        import io
        from contextlib import redirect_stdout
        from lifecycle_core import cli as cli_mod
        r = refusals._Repo(items=items_text or self.TWO_GOALS)
        self.addCleanup(r.close)
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(r.dir)] + list(argv))
        except SystemExit as exc:
            code = exc.code
        return code, buf.getvalue()

    def test_filter_returns_only_that_goal(self):
        code, out = self._run("item", "ready", "--goal", "verify")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("xx-1", out)
        # THE ARM THAT MEANS SOMETHING: a filter that ignored its flag lists
        # both and passes every positive assertion above.
        self.assertNotIn("xx-2", out,
                         "the other goal's entry appears — the flag was "
                         "accepted and not applied")
        self.assertIn("FILTERED to goal=verify: 1 of 2", out)

    def test_the_unfiltered_head_still_lists_both(self):
        """The control: what differs between the arms is the FILTER alone."""
        code, out = self._run("item", "ready", "--head")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("xx-1", out)
        self.assertIn("xx-2", out)
        self.assertNotIn("FILTERED", out)

    def test_undeclared_goal_is_could_not_verify_not_an_empty_listing(self):
        code, out = self._run("item", "ready", "--goal", "mitigat")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("goal_query_undeclared", out)
        self.assertNotIn("xx-1", out)
        self.assertNotIn("xx-2", out)

    def test_declared_goal_with_no_ready_work_is_an_explicit_zero(self):
        """The other half of the pair, and it must NOT be could-not-verify.

        `retire` is declared and carries nothing here. That is a measurement
        — zero, over a named population — and reporting it as could-not-verify
        would throw away the very distinction this verb exists to draw.
        """
        code, out = self._run("item", "ready", "--goal", "retire")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("zero:", out)
        self.assertIn("FILTERED to goal=retire: 0 of 2", out)
        self.assertNotIn("goal_query_undeclared", out)

    def test_an_ident_and_a_goal_together_are_refused(self):
        code, out = self._run("item", "ready", "xx-1", "--goal", "verify")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("names one item AND a filter over many", out)

    def test_the_reserved_meta_goal_is_queryable(self):
        """`tend` is added by the plugin to every repo and declared by none.

        A filter validating against the declaration's own `goals` list alone
        would refuse the one goal every repo is guaranteed to have.
        """
        code, out = self._run("item", "ready", "--goal", "tend")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("FILTERED to goal=tend: 0 of 2", out)
        self.assertNotIn("goal_query_undeclared", out)


class EvidenceCarriesItsMark(unittest.TestCase):
    """lc-167 — an entry says which evidence it RAN and which it CONCLUDED.

    THE PREDICATE IS PRESENCE, NEVER TRUTH, and these arms are written to
    that boundary rather than past it: a checker deciding whether a sentence
    really was measured would be grading prose, which is the guard that fires
    on legitimate work. What is computable is whether the author marked
    anything at all, and that is what the refusal claims.

    THE OVER-FIRE ARM IS THE LOAD-BEARING ONE. Every entry booked before this
    rule carries an unmarked slot — 174 of them across the two homes here —
    so a check that reached the PARSER would fire on the whole carrier at
    once and train the override reflex that kills it. The rule lives at the
    WRITE doors, and the arm below is what pins that.
    """

    UNMARKED = ("the deploy path re-reads the config on every start, so the "
                "gate is looking at the wrong file")
    MARKED = "DERIVED " + UNMARKED

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

    def _add(self, evidence):
        return [a if a != refusals.GOOD_ADD[refusals.GOOD_ADD.index(
            "--evidence") + 1] else evidence for a in refusals.GOOD_ADD]

    # --- the predicate ---------------------------------------------------

    def test_an_unmarked_value_is_a_problem_and_each_mark_clears_it(self):
        self.assertIsNotNone(items.evidence_mark_problem(self.UNMARKED))
        for mark in items.EVIDENCE_MARKS:
            self.assertIsNone(
                items.evidence_mark_problem(f"{mark} {self.UNMARKED}"),
                f"{mark} is in the vocabulary and did not clear the check")

    def test_the_mark_is_a_TOKEN_and_not_the_ordinary_word(self):
        """Lower-case `measured` is prose; `MEASURED` is a mark.

        Matching case-insensitively would pass on almost every evidence slot
        ever written — the word appears constantly in ordinary sentences — so
        the check would read green over exactly the unmarked entries it
        exists to catch. That is the assurance-wider-than-its-predicate
        shape, and the capital is what keeps the token deliberate.
        """
        self.assertIsNotNone(
            items.evidence_mark_problem("measured at the desk last week"))
        self.assertIsNone(items.evidence_mark_problem("MEASURED at the desk"))

    def test_a_MIXED_slot_is_legal_because_most_real_evidence_is_mixed(self):
        """The item's own MUST-NOT-MOVE: the mark is per claim, not per
        entry. A rule admitting only single-kind slots would push authors to
        split one evidence body across two entries to satisfy a checker."""
        self.assertIsNone(items.evidence_mark_problem(
            "MEASURED the walk over 86 tracked files returned 0 findings; "
            "DERIVED that the XDG homes are outside its reach"))

    def test_UNKNOWN_and_empty_are_not_this_check_s_business(self):
        """UNKNOWN is the migration's declared transitional value — an entry
        recording that nobody has written evidence has nothing to mark. Empty
        is `slot_value_problem`'s finding, and two refusals over one input
        would tell the author two different things about one mistake."""
        self.assertIsNone(items.evidence_mark_problem(items.UNKNOWN))
        self.assertIsNone(items.evidence_mark_problem(""))
        self.assertIsNone(items.evidence_mark_problem(None))

    # --- the doors -------------------------------------------------------

    def test_item_add_refuses_an_unmarked_slot_and_writes_nothing(self):
        r = self._repo()
        before = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
        code, out = self._run(r, *self._add(self.UNMARKED))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("evidence_unmarked", out, out)
        self.assertEqual((r.dir / "ITEMS.md").read_text(encoding="utf-8"),
                         before, "the carrier was written despite the refusal")

    def test_the_same_add_MINTS_once_the_claim_is_marked(self):
        r = self._repo()
        code, out = self._run(r, *self._add(self.MARKED))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn(self.MARKED,
                      (r.dir / "ITEMS.md").read_text(encoding="utf-8"))

    def test_the_AMEND_door_is_covered_and_it_is_the_one_that_matters(self):
        """`amended-evidence` is the most-amended slot in this carrier (39%
        of 88 closed items), so the value a lane actually reads is often the
        amended one. A mark demanded at `add` alone would leave the
        read-most value unmarked."""
        r = self._repo(items=refusals.FOUR_BLOCKER_ITEMS)
        before = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
        code, out = self._run(r, "item", "amend", "xx-3",
                              "--reason", "the evidence was re-read",
                              "--evidence", self.UNMARKED)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("evidence_unmarked", out, out)
        self.assertEqual((r.dir / "ITEMS.md").read_text(encoding="utf-8"),
                         before, "the amendment was appended despite it")
        code, out = self._run(r, "item", "amend", "xx-3",
                              "--reason", "the evidence was re-read",
                              "--evidence", self.MARKED)
        self.assertEqual(code, exits.CLEAN, out)

    # --- the over-fire boundary ------------------------------------------

    def test_a_carrier_full_of_UNMARKED_legacy_entries_stays_CLEAN(self):
        """THE ARM THIS RULE LIVES OR DIES ON.

        `GOOD_ITEMS` carries `evidence: none yet` — an unmarked slot, the
        shape every entry booked before today has. `item check` must read it
        clean: the rule is about what gets WRITTEN from now on, and a checker
        that graded the existing carrier would report 174 findings on its
        first run, which is a guard firing on legitimate work (law 11).
        """
        code, out = run_check(refusals.GOOD_ITEMS)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("evidence_unmarked", out, out)


class ADecisionBlockerSaysWhyItIsNotDerivable(unittest.TestCase):
    """lc-169 — the question travels to the operator only after someone asked.

    MEASURED, TWO OF SIX: of six items one desk had blocked on operator
    decisions, lc-166's answer sat one kind over in this repo's own
    declaration and lc-158's in an audit the same desk had written and
    pushed. Both waited until the operator said to decide what could be
    decided. Neither author was careless — nothing asked.

    THE DEMAND IS FOR THE STATEMENT, NEVER THE ANSWER, and the arms below are
    written to exactly that line. A question that is constitutively the
    operator's — intent, preference, authority over the irreversible — passes
    on one line. A checker grading whether the reason is GOOD would be
    deciding the kind split by predicate, which is the judgment this rule
    must not take over.
    """

    QUESTION = "decision which retention window is canonical"
    UNDECIDABLE = ("a preference with no precedent in the ledger — "
                   "constitutively the operator's")

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

    # --- the three doors --------------------------------------------------

    def test_item_add_refuses_it_and_writes_nothing(self):
        r = self._repo()
        before = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
        code, out = self._run(r, *(refusals.GOOD_ADD
                                   + ["--blocked-by", self.QUESTION]))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("decision_not_derivable_unstated", out, out)
        self.assertEqual((r.dir / "ITEMS.md").read_text(encoding="utf-8"),
                         before, "the carrier was written despite the refusal")

    def test_item_park_and_item_amend_are_covered_too(self):
        """The three doors reach one function, which is what makes this free
        — but free is not proven, and a per-verb repair would have covered
        exactly the verbs somebody remembered."""
        for argv in (["item", "park", "xx-1"],
                     ["item", "amend", "xx-1", "--reason", "retyped"]):
            r = self._repo(items=refusals.SEED_ITEMS)
            code, out = self._run(r, *(argv + ["--blocked-by",
                                               self.QUESTION]))
            self.assertEqual(code, exits.FINDING, f"{argv[1]}:\n{out}")
            self.assertIn("decision_not_derivable_unstated", out, out)

    def test_the_same_booking_passes_once_the_statement_is_there(self):
        r = self._repo()
        code, out = self._run(r, *(refusals.GOOD_ADD + [
            "--blocked-by", self.QUESTION,
            "--not-derivable", self.UNDECIDABLE]))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn(f"blocked-by: {self.QUESTION}",
                      (r.dir / "ITEMS.md").read_text(encoding="utf-8"))

    # --- the boundary -----------------------------------------------------

    def test_a_CONSTITUTIVELY_OPERATOR_question_passes_on_one_line(self):
        """The item's MUST-NOT-MOVE. The statement here says the question
        cannot be derived BECAUSE it is a preference — and that is a complete
        answer. A rule that demanded a derivation attempt for every question
        would push the desk to decide what is constitutively the operator's,
        which is the opposite of what this repairs."""
        r = self._repo()
        code, _out = self._run(r, *(refusals.GOOD_ADD + [
            "--blocked-by", "decision whether to publish the marketplace entry",
            "--not-derivable", "an outward act under the operator's accounts — "
                               "theirs by the carve-out floor"]))
        self.assertEqual(code, exits.CLEAN)

    def test_the_demand_does_NOT_reach_the_other_blocker_TYPES(self):
        """Scope. An `evidence` blocker is a predicate and an item-id blocker
        resolves mechanically; neither is a question anybody could derive an
        answer to, and a demand over them would fire on every legitimate one.
        """
        r = self._repo(items=refusals.FOUR_BLOCKER_ITEMS)
        code, out = self._run(r, *(refusals.GOOD_ADD + [
            "--blocked-by", "evidence test -f /nonexistent-lifecycle-probe"]))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("decision_not_derivable_unstated", out, out)

        r2 = self._repo(items=refusals.FOUR_BLOCKER_ITEMS)
        code, out = self._run(r2, *(refusals.GOOD_ADD
                                    + ["--blocked-by", "xx-1"]))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("decision_not_derivable_unstated", out, out)

    def test_a_carrier_full_of_LEGACY_decision_blockers_stays_CLEAN(self):
        """The over-fire boundary, same shape as lc-167's. Every decision
        blocker booked before this rule was booked without a statement — the
        demand is at the WRITE doors, and `item check` must read the existing
        carrier clean."""
        code, out = run_check(refusals.FOUR_BLOCKER_ITEMS)
        self.assertNotIn("decision_not_derivable_unstated", out, out)
        self.assertNotEqual(code, exits.FINDING, out)


class TheArchiveRegionIsReadForIDS(unittest.TestCase):
    """lc-177 — a closure body below `## Archive (pre-migration)` was invisible.

    lc-148 ONE HOME OVER, and that framing is the finding. lc-148 added the
    compaction record as a third home because `next_ident`'s own sentence —
    "EVERY home is read" — was false for `item compact`. The sentence was
    false again, for a different reason, and the paragraph RECOUNTING lc-148
    is the text that was lying: the done-home parse stops at the archive
    heading.

    BOTH ARMS, AND NEITHER IS BELIEVED WITHOUT THE OTHER. One of them is the
    defect and the other is the verb that should have caught it: the
    allocator must not hand out an archived id, and `move integrity` must not
    print CLEAN over a region it never parsed.

    THE BODIES STAY UNGRADED. That exclusion is why the parser stops at the
    heading and it is correct — a repair that started shape-checking archived
    text would trade a silent collision for a loud false finding on every
    pre-migration carrier, which is law 11 and the worse outcome. Only IDS
    are read.
    """

    ARCHIVED = "xx-2"

    def _done_with_archived_body(self):
        return (refusals.EMPTY_DONE
                + refusals._blocked_block("xx-1", "DONE", "NONE")
                + "\n" + items.ARCHIVE_HEADING + "\n\n"
                + refusals._blocked_block(self.ARCHIVED, "DONE", "NONE"))

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

    def test_the_allocator_does_NOT_re_issue_an_archived_id(self):
        r = self._repo(done=self._done_with_archived_body())
        code, out = self._run(r, *refusals.GOOD_ADD)
        self.assertEqual(code, exits.CLEAN, out)
        carrier = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
        self.assertNotIn(f"## {self.ARCHIVED}\n", carrier,
                         "the allocator re-issued an id that is in the "
                         f"archive:\n{out}")

    def test_move_integrity_does_NOT_print_CLEAN_over_the_archive(self):
        """The second arm, and the one that should bother us more: a verb
        reporting CLEAN over a region it never parsed. Its denominator was
        the tell — `1 live, 1 done` counted only what the parser reached."""
        live = ("schema: 2\nbaseline: 1\nadded: 0\ncompacted: 0\n"
                + refusals._blocked_block(self.ARCHIVED, "READY", "NONE"))
        r = self._repo(items=live, done=self._done_with_archived_body())
        _code, out = self._run(r, "item", "check")
        self.assertIn("duplicate_id", out,
                      f"an id in the live carrier AND in an archived body "
                      f"read as no duplicate at all.\n{out}")
        self.assertNotIn("move integrity: CLEAN", out, out)

    def test_the_CLEAN_line_states_the_archived_count(self):
        """lc-172's rule at the site it did not reach: an absence claim names
        what proves its instrument was live. `no id in both homes` over a
        done home whose archive was never read is a clean line about a
        population the verb never saw."""
        r = self._repo(done=self._done_with_archived_body())
        _code, out = self._run(r, "item", "check")
        self.assertIn("move integrity: CLEAN", out, out)
        self.assertIn("1 archived", out,
                      f"the clean line hides the region it compared.\n{out}")

    def test_the_archive_BODIES_are_still_not_shape_checked(self):
        """MUST-NOT-MOVE. A malformed body below the heading stays ungraded —
        ids out, bodies untouched."""
        malformed = (refusals.EMPTY_DONE
                     + refusals._blocked_block("xx-1", "DONE", "NONE")
                     + "\n" + items.ARCHIVE_HEADING + "\n\n"
                     + "## xx-9\nthis body has no slots at all\nand wraps\n")
        code, out = run_done_check(malformed)
        self.assertNotEqual(code, exits.FINDING,
                            f"an archived body was shape-checked.\n{out}")
        self.assertNotIn("xx-9", out, out)
