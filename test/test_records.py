"""`record check` — the investigation record's form (lc-156).

EVERY ARM IS A PAIR. A planted record goes red on the class it plants, and a
CONTROL differing in exactly that one line comes back clean. An arm asserting
only that something was found separates nothing: the correct and the
defective record both satisfy "a finding exists", and the assertion that
matters is that the NAMED row fired and the control's did not.

THE CONFORMANT FIXTURE IS THE CONTROL EVERY ARM MUTATES ONE LINE AWAY FROM.
It is written here from the FORMAT's template, never copied out of a live
record: an expectation derived from the artifact it grades moves with the
artifact and stays green on the drift it exists to catch.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits                       # noqa: E402
from lifecycle_core import records as rec              # noqa: E402


GOOD = """# proj — arc    (opened 2026-09-18; sessions: aaaaaa)

## GOAL
close the thing the requester asked for, in their words

## NOW
current approach: read the carrier first — killed if the carrier is stale

## ESTABLISHED
[VERIFIED] the parser folds wrapped lines — test_records.py::test_fold, green
[INVALIDATED] the home was ~/.claude — superseded by XDG (format file, line 7)

## OPEN
[PENDING] does the gate fire on a real closure — route: measure — probe: plant a closed record; red = the gate fires, green = it is blind

## MOVES
2026-09-18 opened — cc: none
"""


class _Home:
    """A throwaway records home holding exactly the files an arm names."""

    def __init__(self, **files):
        self.dir = Path(tempfile.mkdtemp(prefix="lifecycle-records-"))
        for name, text in files.items():
            (self.dir / f"{name}.md").write_text(text, encoding="utf-8")

    def run(self):
        class _Args:
            dir = str(self.dir)
        said = []
        code = rec.cmd_record_check(_Args(), said.append)
        return code, "\n".join(said)


def run_one(text):
    return _Home(record=text).run()


class ControlIsClean(unittest.TestCase):
    """THE BASELINE, asserted before any arm claims a red means anything.

    Over an already-red baseline a plant-and-check proof is indistinguishable
    from a checker that is simply always red — so the conformant record's
    CLEAN is what makes every arm below evidence rather than noise.
    """

    def test_conformant_record_is_clean(self):
        code, out = run_one(GOOD)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("record check: CLEAN", out)


class SlotsAndShape(unittest.TestCase):

    def test_missing_slot_is_a_finding(self):
        code, out = run_one(GOOD.replace("## MOVES", "## NOTES"))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("record_slot_missing", out)
        self.assertIn("MOVES", out)

    def test_annotated_heading_is_the_same_slot(self):
        """The over-fire arm, and it guards a guard that would stop the lane.

        Two live records annotate their headings (`## GOAL (the requester's
        words)`). A checker demanding a bare heading reports five missing
        slots on a record that has five, which is a guard firing on
        legitimate work.
        """
        annotated = (GOOD
                     .replace("## GOAL", "## GOAL (the requester's words)")
                     .replace("## NOW", "## NOW — approach, and what kills it")
                     .replace("## OPEN", "## OPEN (each with its probe)"))
        code, out = run_one(annotated)
        self.assertEqual(code, exits.CLEAN, out)

    def test_foreign_heading_does_not_absorb_into_the_previous_slot(self):
        """A section the format does not name ends the slot before it.

        Without the termination, this record's prose bullet is graded as an
        OPEN line and reported as untagged — a finding pointing at the wrong
        place in the file, which is worse than none.
        """
        code, out = run_one(GOOD + "\n## HELD FOR WAVE 4\n- some prose\n")
        self.assertEqual(code, exits.CLEAN, out)

    def test_empty_now_is_a_finding(self):
        code, out = run_one(GOOD.replace(
            "current approach: read the carrier first — killed if the carrier "
            "is stale\n", ""))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("record_now_empty", out)

    def test_wrapped_line_folds_into_the_line_it_continues(self):
        """The fold arm. Its absence would fire on every wrap in the corpus."""
        wrapped = GOOD.replace(
            "[VERIFIED] the parser folds wrapped lines — test_records.py"
            "::test_fold, green",
            "[VERIFIED] the parser folds wrapped lines — test_records.py\n"
            "  ::test_fold, green")
        code, out = run_one(wrapped)
        self.assertEqual(code, exits.CLEAN, out)


class LineGrammar(unittest.TestCase):

    def test_untagged_prose_line_is_a_finding(self):
        """The class that would otherwise pass BY HAVING NO TAGGED LINES."""
        prose = GOOD.replace(
            "[VERIFIED] the parser folds wrapped lines — test_records.py"
            "::test_fold, green",
            "- the parser folds wrapped lines, we checked")
        code, out = run_one(prose)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("record_line_untagged", out)

    def test_whole_record_of_prose_is_a_finding_not_a_pass(self):
        allprose = """# proj — arc

## GOAL
a goal

## NOW
an approach

## ESTABLISHED
- we found a thing. Basis: somewhere
- and another thing

## OPEN
- something we do not know

## MOVES
nothing yet
"""
        code, out = run_one(allprose)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("record_line_untagged", out)

    def test_unknown_tag_is_a_finding(self):
        code, out = run_one(GOOD.replace("[VERIFIED] the parser",
                                         "[CONFIRMED] the parser"))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("record_tag_unknown", out)

    def test_tagged_line_without_a_basis_is_a_finding(self):
        code, out = run_one(GOOD.replace(
            "[VERIFIED] the parser folds wrapped lines — test_records.py"
            "::test_fold, green",
            "[VERIFIED] the parser folds wrapped lines"))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("record_line_unbasised", out)

    def test_a_hyphen_is_not_an_em_dash(self):
        """Two spellings of one slot is what the single separator prevents."""
        code, out = run_one(GOOD.replace(
            "wrapped lines — test_records.py", "wrapped lines - test_records.py"))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("record_line_unbasised", out)


class RouteAndProbe(unittest.TestCase):

    def test_pending_without_a_route_is_a_finding(self):
        code, out = run_one(GOOD.replace(" — route: measure", ""))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("record_route_invalid", out)

    def test_route_outside_the_closed_set_is_a_finding(self):
        code, out = run_one(GOOD.replace("route: measure", "route: think"))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("record_route_invalid", out)

    def test_pending_without_a_probe_is_a_finding(self):
        code, out = run_one(GOOD.replace(
            " — probe: plant a closed record; red = the gate fires, green = "
            "it is blind", ""))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("record_probe_missing", out)

    def test_waiting_asks_are_counted_and_are_not_findings(self):
        """A question waiting on the reporter is correct work, and invisible.

        The line exists because nothing wakes an `ask`; it must therefore be
        SURFACED without being graded, and an arm that only counted findings
        would not notice if it silently became one.
        """
        code, out = run_one(GOOD.replace("route: measure", "route: ask"))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("waiting on the reporter: 1", out)


class ClosureGate(unittest.TestCase):

    def test_closed_with_an_undrained_pending_is_a_finding(self):
        code, out = run_one(GOOD + "\n## CLOSED\nESTABLISHED → LEDGER.md; "
                                   "OPEN → lc-99\n")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("record_closed_undrained", out)

    def test_closed_with_no_pointer_is_a_finding(self):
        drained = GOOD.replace(
            "[PENDING] does the gate fire on a real closure — route: measure "
            "— probe: plant a closed record; red = the gate fires, green = "
            "it is blind",
            "[VERIFIED] the gate fires — test_records.py::ClosureGate, green")
        code, out = run_one(drained + "\n## CLOSED\n")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("record_closed_unpointed", out)

    def test_closed_and_drained_and_pointed_is_clean(self):
        """The control for both gate arms: closure done RIGHT stays clean."""
        drained = GOOD.replace(
            "[PENDING] does the gate fire on a real closure — route: measure "
            "— probe: plant a closed record; red = the gate fires, green = "
            "it is blind",
            "[VERIFIED] the gate fires — test_records.py::ClosureGate, green")
        code, out = run_one(drained + "\n## CLOSED\nESTABLISHED → LEDGER.md; "
                                      "OPEN → lc-99\n")
        self.assertEqual(code, exits.CLEAN, out)

    def test_the_word_closed_in_prose_does_not_trip_the_gate(self):
        """Anchored on the HEADING, never on the word.

        A record whose NOW says "ARC CLOSED and desk-verified closable" is in
        the live home today with eight PENDING lines under it. A detector
        keyed on the word reports that record closed-with-undrained and sends
        its author to drain an arc that is still running.
        """
        code, out = run_one(GOOD.replace(
            "current approach: read the carrier first",
            "ARC CLOSED and desk-verified closable; approach: read it first"))
        self.assertEqual(code, exits.CLEAN, out)


class ThreeAnswers(unittest.TestCase):

    def test_no_home_is_could_not_verify(self):
        d = Path(tempfile.mkdtemp()) / "nope"

        class _Args:
            dir = str(d)
        said = []
        self.assertEqual(rec.cmd_record_check(_Args(), said.append),
                         exits.COULD_NOT_VERIFY)
        self.assertIn("COULD NOT VERIFY", "\n".join(said))

    def test_empty_home_is_could_not_verify_not_clean(self):
        code, out = _Home().run()
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("0 of 0", out)

    def test_unreadable_record_is_could_not_verify_and_outranks_a_finding(self):
        """The ordering arm, and it is the verb's whole contract.

        A run that could not read part of its input cannot promise the
        findings it DID emit are the complete list. Folding that into FINDING
        hands the caller a list it will act on as complete.
        """
        h = _Home(good=GOOD, bad=GOOD.replace("[VERIFIED] the parser folds "
                                              "wrapped lines — test_records"
                                              ".py::test_fold, green",
                                              "[VERIFIED] no basis here"))
        (h.dir / "unreadable.md").write_bytes(b"\xff\xfe\x00 not utf-8 \xff")
        code, out = h.run()
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("record_line_unbasised", out)
        self.assertIn("could not be read", out)


if __name__ == "__main__":
    unittest.main()
