"""Drain wave B, lane R2 — the walk on a second machine (lc-314), and the
record that graded nothing (lc-188, the second half of this file).

WHAT THESE ARMS HOLD APART. `kind_grew_without_exit` counts exit events in
the fire log, and the fire log lives under `XDG_STATE_HOME`: it does not
travel with the repo. The carriers do. So on a second machine, a fresh clone
or a moved checkout the log holds no exit for a kind whose tracked tree shows
the exit was taken, and "zero events" there is a fact about the MACHINE that
the walk printed as a finding about the KIND.

EVERY ARM RUNS UNDER ITS OWN `XDG_STATE_HOME`, holding a log that is PRESENT
and carries a real `item close` for ANOTHER repo. Present, because an absent
log is already could-not-verify by a different branch and an arm reading that
branch would pass for the wrong reason; another repo's close, because the
reader narrows by repo and a log this arm left empty would not show that it
does.

THE CONTROLS ARE THE OTHER HALF AND THEY MUST NOT MOVE: a kind with no exit
in the log AND none in the tree still fires, and a kind whose exit IS in this
machine's log still reads clean.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits, firelog, retire  # noqa: E402
from lifecycle_core import ledger as ledger_mod  # noqa: E402
from lifecycle_core import records as rec  # noqa: E402
from lifecycle_core.refusals import (  # noqa: E402
    EMPTY_DONE, SEED_ITEMS, _GOOD_RECORD)

#: The seed carrier's one block, re-headed as a body the done home holds. Cut
#: from `SEED_ITEMS` rather than written out again, so the two cannot drift.
DONE_WITH_ONE_BODY = (EMPTY_DONE.rstrip("\n") + "\n\n"
                      + SEED_ITEMS.split("\n\n", 1)[1]
                      .replace("## xx-1", "## xx-9", 1)
                      .replace("grade: READY", "grade: DONE", 1))

ITEMS_KIND = {"home": "ITEMS.md", "growth": "bounded-by-exit",
              "exit": {"action": "move"}}
DONE_KIND = {"home": "ITEMS-DONE.md", "growth": "compacted",
             "exit": {"action": "compact"}}
ARCS_KIND = {"home": "arcs/*.md", "growth": "bounded-by-exit",
             "exit": {"action": "move"}}
CLOSED_ARCS_KIND = {"home": "arcs/closed/*.md",
                    "growth": "unbounded-with-reason: accrues at closure rate",
                    "exit": {"action": "compact"}}

MARK = "[exit_log_machine_local]"
ALARM = "[kind_grew_without_exit]"


class _SecondMachine(unittest.TestCase):
    """A repo in a temp dir, read under a fire log that never saw it."""

    def setUp(self):
        self.repo = Path(tempfile.mkdtemp(prefix="lifecycle-r2-repo-"))
        self.state = Path(tempfile.mkdtemp(prefix="lifecycle-r2-xdg-"))
        self.old = os.environ.get("XDG_STATE_HOME")
        os.environ["XDG_STATE_HOME"] = str(self.state)
        # A REAL line through the real writer, for a repo that is not this
        # one: the log is present and readable, and holds nothing for us.
        self.assertTrue(firelog.fire("item close", repo="/some/other/repo"))
        (self.repo / "ITEMS.md").write_text(SEED_ITEMS, encoding="utf-8")
        (self.repo / "ITEMS-DONE.md").write_text(EMPTY_DONE, encoding="utf-8")
        (self.repo / "LEDGER.md").write_text(ledger_mod.head_text(),
                                             encoding="utf-8")

    def tearDown(self):
        if self.old is None:
            os.environ.pop("XDG_STATE_HOME", None)
        else:
            os.environ["XDG_STATE_HOME"] = self.old
        shutil.rmtree(self.repo, ignore_errors=True)
        shutil.rmtree(self.state, ignore_errors=True)

    def verdict(self, **kinds):
        doc = {"closure-home": "ITEMS-DONE.md",
               "kinds": {k.replace("_", " "): v for k, v in kinds.items()}}
        buf = []
        code = retire.growth_verdict(self.repo, doc, buf.append)
        return code, "\n".join(buf)

    def close_here(self, verb="item close"):
        """This machine's log records the exit for THIS repo."""
        self.assertTrue(firelog.fire(verb, repo=str(self.repo)))


class ItemsClosedOnAnotherMachine(_SecondMachine):

    def test_baseline_the_log_is_present_and_holds_nothing_for_this_repo(self):
        """The arrangement, stated as an arm: every result below is read off
        a log that exists. Without this the could-not-verify arms could be
        the absent-log branch answering."""
        self.assertTrue(retire.fire_log_readable())
        self.assertEqual(retire.read_fire_log(self.repo), [])
        self.assertEqual(len(retire.read_fire_log()), 1)

    def test_closed_bodies_in_the_done_home_make_it_could_not_verify(self):
        """lc-314 RED-FIRST. One live item, one closed body in the done
        home, no `item close` in this machine's log: the exit WAS taken, so
        the walk cannot call the kind not draining."""
        (self.repo / "ITEMS-DONE.md").write_text(DONE_WITH_ONE_BODY,
                                                 encoding="utf-8")
        code, out = self.verdict(items=ITEMS_KIND)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("COULD NOT VERIFY " + MARK, out)
        self.assertNotIn(ALARM, out)
        self.assertIn("MACHINE-LOCAL", out)
        # THE EVIDENCE IS NAMED, with its count and its home: a
        # could-not-verify that did not say what it saw would be the same
        # unbasised sentence in the other direction.
        self.assertIn("1 instance(s) in 'ITEMS-DONE.md'", out)

    def test_control_no_exit_anywhere_still_fires(self):
        """The item's own CONTROL: nothing in the log, nothing in the tree."""
        code, out = self.verdict(items=ITEMS_KIND)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING " + ALARM, out)
        self.assertNotIn(MARK, out)

    def test_a_body_closed_then_compacted_still_shows_the_close(self):
        """The done home can be EMPTY over a kind that drained: compaction
        takes the body out of both carriers and leaves a ledger record. A
        reader of the done home alone would fire on the best-drained repo."""
        ledger_mod.append(self.repo / "LEDGER.md", "decision", {
            "question": retire.compaction_question("xx-9"),
            "answer": retire.compaction_answer("ITEMS-DONE.md", "a" * 40,
                                               retire.NO_CLOSED_REF)})
        code, out = self.verdict(items=ITEMS_KIND)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn(MARK, out)
        self.assertIn("1 compaction record(s) in 'LEDGER.md'", out)

    def test_must_not_move_an_exit_in_THIS_log_is_still_clean(self):
        (self.repo / "ITEMS-DONE.md").write_text(DONE_WITH_ONE_BODY,
                                                 encoding="utf-8")
        self.close_here()
        code, out = self.verdict(items=ITEMS_KIND)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("the exit has fired for this kind", out)
        self.assertNotIn(MARK, out)

    def test_must_not_move_an_empty_kind_is_still_clean(self):
        (self.repo / "ITEMS.md").write_text(
            SEED_ITEMS.split("\n\n", 1)[0] + "\n", encoding="utf-8")
        (self.repo / "ITEMS-DONE.md").write_text(DONE_WITH_ONE_BODY,
                                                 encoding="utf-8")
        code, out = self.verdict(items=ITEMS_KIND)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("holds 0 instance(s)", out)


class TheOtherMappedExits(_SecondMachine):
    """Every (kind, action) the walk maps a verb for is held to the rule —
    the defect was measured on three kinds, not on `items` alone."""

    def test_done_bodies_with_a_compaction_record_is_could_not_verify(self):
        (self.repo / "ITEMS-DONE.md").write_text(DONE_WITH_ONE_BODY,
                                                 encoding="utf-8")
        ledger_mod.append(self.repo / "LEDGER.md", "decision", {
            "question": retire.compaction_question("xx-8"),
            "answer": retire.compaction_answer("ITEMS-DONE.md", "b" * 40,
                                               retire.NO_CLOSED_REF)})
        code, out = self.verdict(done_bodies=DONE_KIND)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn(MARK, out)
        self.assertNotIn(ALARM, out)

    def test_control_done_bodies_never_compacted_still_fires(self):
        """A done home holding bodies is NOT evidence that compaction ran:
        the bodies are this kind's own population, not its exit's trace."""
        (self.repo / "ITEMS-DONE.md").write_text(DONE_WITH_ONE_BODY,
                                                 encoding="utf-8")
        code, out = self.verdict(done_bodies=DONE_KIND)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn(ALARM, out)
        self.assertNotIn(MARK, out)

    def _arc(self, rel):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("schema: 6\n\n# an arc\n", encoding="utf-8")

    def test_arcs_with_a_closed_body_is_could_not_verify(self):
        self._arc("arcs/live.md")
        self._arc("arcs/closed/old.md")
        code, out = self.verdict(arcs=ARCS_KIND, closed_arcs=CLOSED_ARCS_KIND)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn(MARK, out)
        self.assertNotIn(ALARM, out)
        self.assertIn("1 instance(s) in 'arcs/closed/*.md'", out)

    def test_control_arcs_never_closed_still_fires(self):
        self._arc("arcs/live.md")
        code, out = self.verdict(arcs=ARCS_KIND, closed_arcs=CLOSED_ARCS_KIND)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn(ALARM, out)
        self.assertNotIn(MARK, out)

    def test_an_arc_close_elsewhere_does_NOT_excuse_the_items_kind(self):
        """The (kind, action) keying, held on the new branch too: `arcs` and
        `items` both declare `move`, and a closed ARC is no trace of an item
        close."""
        self._arc("arcs/closed/old.md")
        code, out = self.verdict(items=ITEMS_KIND,
                                 closed_arcs=CLOSED_ARCS_KIND)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn(ALARM, out)
        self.assertNotIn(MARK, out)


class TheWalkSaysWhichMachineItSpeaksFor(_SecondMachine):

    def walk(self, **kinds):
        doc = {"closure-home": "ITEMS-DONE.md",
               "kinds": {k.replace("_", " "): v for k, v in kinds.items()}}
        buf = []
        code = retire.walk(self.repo, doc, buf.append, acting=False)
        return code, "\n".join(buf)

    def test_the_walk_and_the_verdict_agree_on_the_new_answer(self):
        """One body, two callers (lc-187's rule): the walk prints the same
        sentence the verdict does, and lists the kind as unchecked rather
        than as grown."""
        (self.repo / "ITEMS-DONE.md").write_text(DONE_WITH_ONE_BODY,
                                                 encoding="utf-8")
        _, vout = self.verdict(items=ITEMS_KIND)
        code, wout = self.walk(items=ITEMS_KIND)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, wout)
        line = [l for l in vout.split("\n") if MARK in l]
        self.assertEqual(len(line), 1, vout)
        self.assertIn(line[0], wout)
        self.assertIn("grew-without-exit 0; growth unchecked 1 (items)", wout)

    def test_the_staleness_line_does_not_claim_a_first_walk(self):
        """The criterion's last sentence. 'This is the first walk' is a
        claim about the repo read off nothing but this machine."""
        kind = dict(ITEMS_KIND, staleness="no grade movement across N passes")
        _, out = self.walk(items=kind)
        stale = [l for l in out.split("\n") if "staleness check: NOT RUN" in l]
        self.assertEqual(len(stale), 1, out)
        self.assertNotIn("this is the first walk", stale[0])
        self.assertIn("THIS MACHINE", stale[0])


# --- lc-188: a record with zero graded lines ---------------------------------
#
# `record check` grades the lines under ESTABLISHED and OPEN. A record whose
# two slots hold no line produces an empty finding list — the same value a
# sound record produces — and printed CLEAN with no count, so the two outputs
# were byte-identical. `record_line_untagged` closed the prose case; this is
# the same case with the prose removed.

ESTABLISHED_LINE = ("[VERIFIED] the fold works — test_records.py::test_fold, "
                    "green\n")
OPEN_LINE = ("[PENDING] does the gate fire — route: measure — probe: plant a "
             "closed record; red = it fires, green = it is blind\n")

#: The conformant record with both graded slots EMPTIED, headings standing.
#: Cut from the roster's own control so the arms differ in those two lines
#: and in nothing else.
NOTHING_TO_GRADE = _GOOD_RECORD.replace(ESTABLISHED_LINE, "").replace(
    OPEN_LINE, "")

NOTHING = "[record_nothing_graded]"


def record_check(**files):
    d = Path(tempfile.mkdtemp(prefix="lifecycle-r2-records-"))
    try:
        for name, text in files.items():
            (d / f"{name}.md").write_text(text, encoding="utf-8")

        class _Args:
            dir = str(d)
        said = []
        code = rec.cmd_record_check(_Args(), said.append)
        return code, "\n".join(said)
    finally:
        shutil.rmtree(d, ignore_errors=True)


class ARecordThatGradedNothing(unittest.TestCase):

    def test_the_fixture_differs_from_the_control_in_two_lines(self):
        """The arrangement: both replacements landed, and the five headings
        still stand — so the red below is the empty slots and not a missing
        heading answering under another name."""
        self.assertEqual(_GOOD_RECORD.count(ESTABLISHED_LINE), 1)
        self.assertEqual(_GOOD_RECORD.count(OPEN_LINE), 1)
        for slot in rec.SLOTS:
            self.assertIn(f"## {slot}", NOTHING_TO_GRADE)
        self.assertNotIn("[VERIFIED]", NOTHING_TO_GRADE)
        self.assertNotIn("[PENDING]", NOTHING_TO_GRADE)

    def test_zero_graded_lines_is_could_not_verify_not_clean(self):
        """lc-188 RED-FIRST."""
        code, out = record_check(record=NOTHING_TO_GRADE)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("COULD NOT VERIFY " + NOTHING, out)
        self.assertIn("record.md", out)
        self.assertIn("0 line(s) graded", out)
        self.assertNotIn("record check: CLEAN", out)
        self.assertNotIn("FINDING", out)

    def test_the_clean_path_prints_its_denominator(self):
        """MUST-NOT-MOVE, and the criterion's other half: a count printed
        only when something is wrong is a count nobody reads."""
        code, out = record_check(record=_GOOD_RECORD)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("record check: CLEAN", out)
        self.assertIn("2 line(s) graded", out)
        self.assertNotIn(NOTHING, out)

    def test_a_wrapped_line_is_one_graded_line(self):
        """The count is of LOGICAL lines — what the checker grades — so a
        wrap does not inflate the denominator."""
        wrapped = _GOOD_RECORD.replace(
            "works — test_records.py::test_fold, green",
            "works —\n    test_records.py::test_fold, green")
        self.assertNotEqual(wrapped, _GOOD_RECORD)
        code, out = record_check(record=wrapped)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("2 line(s) graded", out)

    def test_a_finding_keeps_its_verdict_and_gains_the_count(self):
        """MUST-NOT-MOVE: real graded lines, one of them faulty."""
        bad = _GOOD_RECORD.replace("[VERIFIED] the fold", "[CONFIRMED] the fold")
        code, out = record_check(record=bad)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [record_tag_unknown] record.md: 1 line(s)", out)
        self.assertIn("2 line(s) graded", out)
        self.assertNotIn(NOTHING, out)

    def test_untagged_prose_is_graded_and_stays_a_finding(self):
        """The neighbour's case must not be absorbed: a prose line IS a
        graded line — it is what `record_line_untagged` faults."""
        prose = NOTHING_TO_GRADE.replace(
            "## ESTABLISHED\n", "## ESTABLISHED\n- the fold works, we checked\n")
        code, out = record_check(record=prose)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[record_line_untagged]", out)
        self.assertIn("1 line(s) graded", out)
        self.assertNotIn(NOTHING, out)

    def test_one_empty_record_withdraws_clean_from_the_whole_run(self):
        """The run's promise is over every record: one that graded nothing
        outranks the sound one beside it, whose count still prints."""
        code, out = record_check(good=_GOOD_RECORD, hollow=NOTHING_TO_GRADE)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn(NOTHING + " hollow.md", out)
        self.assertNotIn(NOTHING + " good.md", out)
        self.assertIn("2 line(s) graded", out)

    def test_it_outranks_a_finding_and_the_finding_still_prints(self):
        """`exits.worst`'s order, at this site: a record missing its graded
        slots is a finding AND graded nothing, and the code says the list is
        not whole while the list prints in full."""
        gone = NOTHING_TO_GRADE.replace("## OPEN", "## QUESTIONS")
        code, out = record_check(record=gone)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("[record_slot_missing]", out)
        self.assertIn(NOTHING, out)

    def test_a_closed_record_keeps_its_answer(self):
        """A CLOSED record is shape-ungraded BY DESIGN and already says so
        on its own line; test_records.py pins it CLEAN. It has no graded
        line and is not this refusal's case."""
        closed = _GOOD_RECORD.replace(OPEN_LINE, "") + (
            "\n## CLOSED\ngraduated to LEDGER.md:12\n")
        code, out = record_check(record=closed)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("CLOSED record.md", out)
        self.assertNotIn(NOTHING, out)
        self.assertIn("1 closed", out)


if __name__ == "__main__":
    unittest.main()
