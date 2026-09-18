"""`exits.worst()` — the function that decides every verb's exit code.

WHY THIS FILE EXISTS. `worst()` is reached from 48 call sites and carries a
deliberately-decided contract with a paragraph of reasoning behind it:
COULD_NOT_VERIFY outranks FINDING, because the caller most at risk reads 2 as
"here is the complete list of what is wrong" and acts on the list, so 3
withdraws the promise of COMPLETENESS while every finding still prints in
full. Until this file existed, no test exercised the function at all —
measured with a positive control, `worst(` returned ZERO hits across `test/`
while a control pattern over the same tree hit. The whole argument sat in
prose beside the mechanism, held by nothing, which is law 26's second clause
at the one function that decides whether any run reads as clean.

THE SECOND ARM IS THE ONE THAT LASTS, and it is the reason this is not three
equality assertions. The docstring names its own most likely future defect:

    The ordering is explicit rather than `max()`: max would rank FINDING(2)
    below COULD_NOT_VERIFY(3) by accident of the numbers — the right answer
    for the wrong reason, and one that would silently invert the day the
    numbers changed.

MEASURED, both arms, rather than argued — and the first result corrected what
this paragraph originally claimed. Swapping the body for `max(codes,
default=CLEAN)` fails exactly ONE test here, and it is NOT an ordering one:
every ordering assertion passes, because today the numbers happen to agree,
exactly as the docstring predicts. What catches it is
`test_unknown_code_ranks_as_could_not_verify` — `max([COULD_NOT_VERIFY, 99])`
is 99 where the real body keeps 3, first-wins among equal ranks — which is a
different property that the ordering arm cannot see. So the honest statement
is that NO ordering assertion can distinguish `max()` today, and the case
filed below as merely undocumented is the only one that does.

The defect that matters is therefore not `max()` itself but the inversion it
would one day permit silently. Inverting the rank map so FINDING outranks
COULD_NOT_VERIFY fails FIVE of the nine, the must-not arm among them. That is
why the load-bearing arm asserts what must NOT come back — never a 2 out of
any set containing a could-not-verify — and pins the ORDERING against the
rank map rather than against the literals, so the day someone renumbers the
codes the test moves with the contract and not with the constants.

EXPECTATIONS ARE DERIVED FROM THE DOCSTRING, NOT FROM THE BODY. Where the
contract is silent the test says so in `test_undocumented_*` rather than
freezing whatever the implementation happens to do today: an expectation read
off the artifact it grades moves with the mutant and stays green on the
corruption it exists to catch.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits  # noqa: E402


class WorstOrdering(unittest.TestCase):
    """The documented ranking, stated as the docstring states it."""

    def test_empty_of_each_alone(self):
        for code in exits.ALL:
            self.assertEqual(exits.worst([code]), code,
                             f"one {exits.word(code)} must report itself")

    def test_clean_loses_to_both(self):
        self.assertEqual(exits.worst([exits.CLEAN, exits.FINDING]),
                         exits.FINDING)
        self.assertEqual(exits.worst([exits.CLEAN, exits.COULD_NOT_VERIFY]),
                         exits.COULD_NOT_VERIFY)

    def test_could_not_verify_outranks_finding(self):
        """The deliberate half — the one the docstring argues for."""
        self.assertEqual(exits.worst([exits.FINDING, exits.COULD_NOT_VERIFY]),
                         exits.COULD_NOT_VERIFY)

    def test_order_of_arguments_does_not_matter(self):
        """`worst` is a fold over a set; a caller's ordering is not a verdict."""
        for combo in itertools.permutations(exits.ALL):
            self.assertEqual(exits.worst(list(combo)),
                             exits.COULD_NOT_VERIFY,
                             f"{combo} must report COULD NOT VERIFY")


class WorstMustNot(unittest.TestCase):
    """The degrading arm: what must NEVER come back.

    A presence-assertion catches this function BREAKING. These catch it
    DEGRADING — a `max()` refactor, or a renumbering that silently inverts the
    ranking — which is the failure the docstring predicts of itself.
    """

    def test_never_finding_when_anything_could_not_verify(self):
        pool = list(exits.ALL)
        for n in (1, 2, 3, 4):
            for combo in itertools.product(pool, repeat=n):
                if exits.COULD_NOT_VERIFY not in combo:
                    continue
                got = exits.worst(list(combo))
                self.assertNotEqual(
                    got, exits.FINDING,
                    f"worst({combo}) returned FINDING; a set holding a "
                    f"could-not-verify must never report the complete-list "
                    f"promise that exit 2 makes")
                self.assertEqual(got, exits.COULD_NOT_VERIFY, f"worst({combo})")

    def test_never_clean_when_anything_is_not_clean(self):
        pool = list(exits.ALL)
        for n in (1, 2, 3):
            for combo in itertools.product(pool, repeat=n):
                if all(c == exits.CLEAN for c in combo):
                    continue
                self.assertNotEqual(
                    exits.worst(list(combo)), exits.CLEAN,
                    f"worst({combo}) reported CLEAN over a non-clean member")

    def test_ranking_is_not_the_numbers(self):
        """Pin the ORDER, not the literals.

        The contract is a ranking; the integers are its current spelling. This
        asserts the ranking holds as a ranking, so a renumbering that keeps the
        contract passes and one that inverts it fails — which is precisely the
        distinction `max()` cannot make.
        """
        ranked = [exits.CLEAN, exits.FINDING, exits.COULD_NOT_VERIFY]
        for lower, higher in itertools.combinations(ranked, 2):
            self.assertEqual(
                exits.worst([lower, higher]), higher,
                f"{exits.word(higher)} must outrank {exits.word(lower)}")


class WorstUndocumented(unittest.TestCase):
    """Behaviour the CONTRACT does not decide — recorded, not blessed.

    These two cases are reachable and the docstring is silent on both. They
    are asserted here so a change to either is visible rather than silent, and
    each carries what the open question actually is. A test that simply froze
    today's behaviour as correct would be deriving its expectation from the
    artifact it grades.
    """

    def test_unknown_code_ranks_as_could_not_verify(self):
        """`rank.get(c, 2)` sorts an unrecognised code with COULD_NOT_VERIFY.

        Defensible — an unrecognised verdict is exactly a verdict the tool
        could not form — but it is in the BODY and not in the contract. OPEN:
        whether an unknown code should instead be refused outright, since
        silently ranking it hides the fact that something produced a code this
        module does not know.
        """
        self.assertEqual(exits.worst([exits.CLEAN, 99]),
                         99,
                         "an unrecognised code currently wins over CLEAN")
        self.assertEqual(exits.worst([exits.COULD_NOT_VERIFY, 99]),
                         exits.COULD_NOT_VERIFY,
                         "first-wins among equal ranks: the known code stands")

    def test_empty_reports_clean(self):
        """No checks answered -> CLEAN.

        OPEN, and it is this repo's own 0-of-0 question: a run that verified
        NOTHING reporting the same code as a run that verified everything and
        found nothing is the shape law 1 exists against. It is recorded rather
        than corrected because the fix is a CALLER question — whether any call
        site can reach `worst([])` — and that enumeration is not this file's
        to make.
        """
        self.assertEqual(exits.worst([]), exits.CLEAN)


if __name__ == "__main__":
    unittest.main()
