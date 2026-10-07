"""Drain wave D, lane D3 — lc-62, the near-match between a ledger answer and
a waiting decision question.

WHAT THESE ARMS HOLD APART. The read-side half (wave C) named a near-miss
once per ITEM and per ledger line. Over the real carriers that was about 300
lines on one repo, every one of them a boilerplate re-grade blocker set
beside a MOOT ledger line — a notice telling the reader to ledger an answer
where `item ready` tells the same item a ledger answer is not the route.

Three things are pinned here, each with the arm that must not move:

  * ONE LINE PER DISTINCT BLOCKER QUESTION, carrying the count of items and
    at most three example ids — and two different questions are still two
    lines;
  * a MOOT ledger line is nobody's near-answer, and a migration re-grade
    blocker is not near-matched — while a LIVE answer beside an ordinary
    question still is;
  * `ledger add decision` names the standing blocker its question nearly
    names AS IT ANSWERS, and still writes the line and exits as before.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits  # noqa: E402
from lifecycle_core import grammar  # noqa: E402
from lifecycle_core import items  # noqa: E402
from lifecycle_core import ledger  # noqa: E402
from lifecycle_core import refusals  # noqa: E402

BARE = "whether the gate reads the serving config"
ABOUT = f"the item own body says decision OPEN: {BARE}"
OTHER_BARE = "which capture window is the canonical one"
OTHER_ABOUT = f"still open at the desk: {OTHER_BARE}"
ANSWER = "yes, it reads the serving config"
STATEMENT = "not-derivable: 2026-10-07 a preference with no ledger precedent"


def _carrier(questions):
    """A live carrier of PARKED items `xx-1..n`, one per entry of
    `questions`; each entry is a callable from the item's id to its blocker
    question, so a fixture can give every item its OWN `(item <id>)` suffix
    the way `migrate` and `grammar.for_item` do."""
    blocks = []
    for n, question in enumerate(questions, start=1):
        ident = f"xx-{n}"
        blocks.append(
            f"{grammar.render_heading(ident)}\ngrade: PARKED\n"
            f"requirement: fixture block {n}, valid in every slot — LEDGER.md\n"
            "goal: mitigate\nwrite-set: tools/thing.py\n"
            "done-criterion: it goes red then green\nevidence: none yet\n"
            f"blocked-by: decision {question(ident)}\n{STATEMENT}\n")
    head = (f"schema: {items.SCHEMA_FLOOR}\nbaseline: {len(blocks)}\n"
            "added: 0\ncompacted: 0\n\n")
    return head + "\n".join(blocks)


def _ledger(*pairs):
    return ledger.head_text() + "\n" + "".join(
        ledger.render("decision", {"question": q, "answer": a}) + "\n"
        for q, a in pairs)


def _own(question):
    return lambda ident: grammar.for_item(question, ident)


def _same(question):
    return lambda ident: question


def _near_lines(output):
    return [ln for ln in output.splitlines() if "near-match" in ln]


def _check(questions, *pairs):
    return refusals._cli(["item", "check"], items=_carrier(questions),
                         ledger_text=_ledger(*pairs))


class OncePerDistinctQuestion(unittest.TestCase):
    """The ruling: a near-match is reported once per DISTINCT blocker
    question, never once per item."""

    def test_five_items_on_one_question_are_ONE_line(self):
        fired = _check([_same(ABOUT)] * 5, (BARE, ANSWER))
        near = _near_lines(fired.output)
        self.assertEqual(len(near), 1, fired.output)
        self.assertIn("5 item(s)", near[0])
        self.assertIn(repr(ABOUT), near[0])
        self.assertIn(repr(BARE), near[0])
        self.assertIn("LEDGER.md:3", near[0])
        self.assertIn("NOT resolved", near[0])

    def test_the_line_carries_at_most_THREE_example_ids(self):
        fired = _check([_same(ABOUT)] * 5, (BARE, ANSWER))
        near = _near_lines(fired.output)
        self.assertEqual(len(near), 1, fired.output)
        named = [i for i in range(1, 6) if f"xx-{i}" in near[0]]
        self.assertEqual(named, [1, 2, 3], near[0])
        self.assertIn("2 more", near[0])

    def test_each_items_OWN_id_suffix_does_not_make_the_question_distinct(self):
        """The measured carriers: every item's question carries
        `(item <its id>)`, so literally no two are equal."""
        fired = _check([_own(BARE)] * 4, (BARE, ANSWER))
        near = _near_lines(fired.output)
        self.assertEqual(len(near), 1, fired.output)
        self.assertIn("4 item(s)", near[0])

    def test_several_ledger_lines_on_one_question_stay_ONE_line(self):
        fired = _check([_same(ABOUT)] * 2, (BARE, ANSWER), (BARE, "no"),
                       (BARE, "yes after all"))
        near = _near_lines(fired.output)
        self.assertEqual(len(near), 1, fired.output)
        for lineno in (3, 4, 5):
            self.assertIn(str(lineno), near[0])

    # --- must not move ---------------------------------------------------

    def test_TWO_distinct_questions_are_still_two_lines(self):
        fired = _check([_same(ABOUT), _same(OTHER_ABOUT), _same(ABOUT)],
                       (BARE, ANSWER), (OTHER_BARE, "the second"))
        near = _near_lines(fired.output)
        self.assertEqual(len(near), 2, fired.output)
        first = next(ln for ln in near if repr(ABOUT) in ln)
        second = next(ln for ln in near if repr(OTHER_ABOUT) in ln)
        self.assertIn("2 item(s)", first)
        self.assertIn("1 item(s)", second)
        self.assertIn("xx-2", second)
        self.assertNotIn("xx-2", first)

    def test_one_item_alone_is_still_named(self):
        fired = _check([_same(ABOUT)], (BARE, ANSWER))
        near = _near_lines(fired.output)
        self.assertEqual(len(near), 1, fired.output)
        self.assertIn("1 item(s)", near[0])
        self.assertIn("xx-1", near[0])

    def test_grouping_moves_no_exit_code_and_no_census_line(self):
        grouped = _check([_same(ABOUT)] * 5, (BARE, ANSWER))
        far = _check([_same(ABOUT)] * 5, (OTHER_BARE, ANSWER))
        self.assertEqual(_near_lines(far.output), [])
        self.assertEqual(grouped.code, far.code, grouped.output)

        def census(o):
            return [ln for ln in o.splitlines()
                    if ln.startswith(("decision blockers:", "census:",
                                      "item check:"))]
        self.assertEqual(census(grouped.output), census(far.output))
        self.assertEqual(len(census(grouped.output)), 3, grouped.output)


class AMootLineIsNobodysNearAnswer(unittest.TestCase):
    """`decision_for`'s own rule, mirrored: a moot line says the question
    died with the item whose closure wrote it."""

    MOOT = ledger.moot_answer("xx-9")

    def test_item_check_names_no_near_match_to_a_MOOT_line(self):
        fired = _check([_same(ABOUT)] * 3, (BARE, self.MOOT))
        self.assertEqual(_near_lines(fired.output), [], fired.output)

    def test_item_ready_names_no_near_match_to_a_MOOT_line(self):
        fired = refusals._cli(["item", "ready", "xx-1"],
                              items=_carrier([_same(ABOUT)]),
                              ledger_text=_ledger((BARE, self.MOOT)))
        self.assertNotIn("near-match", fired.output)
        self.assertIn("BLOCKED", fired.output)
        self.assertNotIn("UNBLOCKED", fired.output)
        self.assertIn("so it has not been answered", fired.output)

    def test_the_reader_drops_a_moot_line_and_keeps_its_closers_own(self):
        led = ledger.parse(_ledger((BARE, self.MOOT)))
        self.assertEqual(ledger.near_decisions_for(led, ABOUT), [])
        self.assertEqual(
            ledger.near_decisions_for(led, ABOUT, for_item="xx-1"), [])
        own = ledger.near_decisions_for(led, ABOUT, for_item="xx-9")
        self.assertEqual([ln.lineno for ln, _how in own], [3])

    # --- must not move ---------------------------------------------------

    def test_a_LIVE_answer_beside_the_moot_line_is_still_reported(self):
        fired = _check([_same(ABOUT)] * 3, (BARE, self.MOOT), (BARE, ANSWER))
        near = _near_lines(fired.output)
        self.assertEqual(len(near), 1, fired.output)
        self.assertIn("LEDGER.md:4", near[0])
        self.assertNotIn("LEDGER.md:3", near[0])
        ready = refusals._cli(["item", "ready", "xx-1"],
                              items=_carrier([_same(ABOUT)]),
                              ledger_text=_ledger((BARE, self.MOOT),
                                                  (BARE, ANSWER)))
        self.assertIn("near-match", ready.output)
        self.assertIn("LEDGER.md:4", ready.output)
        self.assertNotIn("UNBLOCKED", ready.output)


class AMigrationRegradeIsNotNearMatched(unittest.TestCase):
    """`item ready` tells such an item a ledger answer is not the route;
    `item check` must not say the opposite one line later."""

    Q = grammar.INCOMPLETE_DECISION

    def test_item_check_names_no_near_match_on_a_migration_question(self):
        self.assertTrue(grammar.is_migration_question(
            grammar.for_item(self.Q, "xx-1")))
        fired = _check([_own(self.Q)] * 4, (self.Q, ANSWER))
        self.assertEqual(_near_lines(fired.output), [], fired.output)

    # --- must not move ---------------------------------------------------

    def test_an_ORDINARY_question_with_the_same_suffix_is_still_reported(self):
        fired = _check([_own(BARE)] * 4, (BARE, ANSWER))
        self.assertEqual(len(_near_lines(fired.output)), 1, fired.output)

    def test_a_question_that_QUOTES_the_minted_text_is_still_reported(self):
        """Equality with the minter's text is the gate, never containment: a
        hand-booked question quoting it is somebody's real decision."""
        quoting = f"do we accept the default '{self.Q}' for the legacy set"
        self.assertFalse(grammar.is_migration_question(quoting))
        fired = _check([_same(quoting)] * 2, (self.Q, ANSWER))
        self.assertEqual(len(_near_lines(fired.output)), 1, fired.output)


def _answer(question, questions, *pairs, answer=ANSWER, extra=()):
    """`ledger add decision` in a scratch repo, then the ledger and the
    carrier AS THE VERB LEFT THEM."""
    with refusals._Repo(items=_carrier(questions),
                        ledger_text=_ledger(*pairs)) as repo:
        fired = refusals._cli_in(repo, [
            "ledger", "add", "decision", "--question", question,
            "--answer", answer, *extra])
        text = (repo.dir / "LEDGER.md").read_text(encoding="utf-8")
        ready = refusals._cli_in(repo, ["item", "ready", "xx-1"])
    return fired, text, ready


class NamedAsItAnswers(unittest.TestCase):
    """The ANSWER-time half: the desk writing the answer is the one party
    that can still copy the blocker's exact question, and it was told
    nothing."""

    def test_ledger_add_names_the_blocker_its_question_nearly_names(self):
        fired, text, _ready = _answer(BARE, [_same(ABOUT)] * 5)
        near = _near_lines(fired.output)
        self.assertEqual(len(near), 1, fired.output)
        self.assertIn("5 item(s)", near[0])
        self.assertIn(repr(ABOUT), near[0])
        self.assertIn("NOT resolved", near[0])
        self.assertIn("xx-1", near[0])
        self.assertNotIn("xx-4", near[0])

    def test_the_line_is_still_written_and_the_exit_does_not_move(self):
        fired, text, ready = _answer(BARE, [_same(ABOUT)] * 2)
        self.assertEqual(fired.code, exits.CLEAN, fired.output)
        self.assertIn(ledger.render(
            "decision", {"question": BARE, "answer": ANSWER}), text)
        # REPORTED, NEVER RESOLVED: the item is still blocked afterwards.
        self.assertNotIn("UNBLOCKED", ready.output)
        self.assertIn("BLOCKED", ready.output)

    # --- must not move ---------------------------------------------------

    def test_the_EXACT_question_answers_and_names_no_near_match(self):
        fired, _text, ready = _answer(ABOUT, [_same(ABOUT)] * 2)
        self.assertEqual(fired.code, exits.CLEAN, fired.output)
        self.assertEqual(_near_lines(fired.output), [], fired.output)
        self.assertIn("UNBLOCKED", ready.output)

    def test_an_UNRELATED_question_names_no_near_match(self):
        fired, _text, _ready = _answer(OTHER_BARE, [_same(ABOUT)] * 2)
        self.assertEqual(fired.code, exits.CLEAN, fired.output)
        self.assertEqual(_near_lines(fired.output), [], fired.output)

    def test_a_migration_regrade_blocker_is_not_named_at_answer_time(self):
        q = grammar.INCOMPLETE_DECISION
        fired, _text, _ready = _answer(q, [_own(q)] * 3)
        self.assertEqual(fired.code, exits.CLEAN, fired.output)
        self.assertEqual(_near_lines(fired.output), [], fired.output)

    def test_a_blocker_ALREADY_answered_exactly_is_not_named(self):
        """Its answer is in the ledger under its own question; it waits on
        nothing, so a second question nearly naming it is not its miss."""
        fired, text, _ready = _answer(
            BARE, [_same(ABOUT)] * 2, (ABOUT, "settled last week"),
            extra=("--join", "new", "--absence",
                   "the bare question, asked for another purpose"))
        self.assertEqual(fired.code, exits.CLEAN, fired.output)
        self.assertIn(ledger.render(
            "decision", {"question": BARE, "answer": ANSWER}), text)
        self.assertEqual(_near_lines(fired.output), [], fired.output)

    def test_no_item_carrier_question_no_note_and_no_refusal(self):
        fired, text, _ready = _answer(BARE, [])
        self.assertEqual(fired.code, exits.CLEAN, fired.output)
        self.assertEqual(_near_lines(fired.output), [], fired.output)
        self.assertIn(BARE, text)


if __name__ == "__main__":
    unittest.main()
