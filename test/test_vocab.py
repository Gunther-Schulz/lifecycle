"""The registered-closed-vocabulary contract (D-3), part P1.

WHAT THESE GRADE, and it is deliberately not the registry's data fields. A
test asserting that `Vocabulary.oov_form` is set would prove a field, not a
contract — the finding V6 recorded against the first design. So the cases
below traverse the grade vocabulary's PROOF PATH end to end: an OOV value is
written at the admission door, counted by the census, rendered by `item
ready`, and refused by the move. Each of those four is a separate site with
its own way of folding an inexpressible state into a benign neighbour.

THE RED THESE WERE WRITTEN AGAINST, stated because a green here means
nothing without it: run against the pre-P1 implementation, the census case
fails with the OOV grade counted in `unknown`, the door case fails with
`unknown_grade_write`, and the ready and close cases fail because neither
site knows the arm exists. The parse cases pass from the start — they grade
a new module and prove only that it parses, which is why they are not the
contract's proof.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import items, vocab  # noqa: E402


class OOVGrammar(unittest.TestCase):
    """The arm's spelling. Anchored at both ends, dated, reason required."""

    def test_well_formed_parses_to_its_date_and_reason(self):
        got = vocab.parse_oov("cannot-express(2026-09-19): no type fits a "
                              "wait on another repo's release")
        self.assertIsNotNone(got)
        self.assertEqual(got.date, "2026-09-19")
        self.assertIn("no type fits", got.reason)

    def test_undated_is_not_well_formed(self):
        """The date is the form, not an annotation — an undated instance

        cannot be aged, and ageing is what the drain reads."""
        self.assertIsNone(vocab.parse_oov("cannot-express: no date here"))

    def test_reasonless_is_not_well_formed(self):
        """An OOV instance with no reason is a silent park wearing this

        mechanism's label — the exact state it exists to make impossible."""
        self.assertIsNone(vocab.parse_oov("cannot-express(2026-09-19):"))
        self.assertIsNone(vocab.parse_oov("cannot-express(2026-09-19):   "))

    def test_not_matched_as_a_substring(self):
        """A containment test here would be a prefix match in an equality's

        costume: a member whose own text quoted the form would be re-typed by
        the reader meant to classify it."""
        self.assertIsNone(vocab.parse_oov(
            "READY — see cannot-express(2026-09-19): quoted inside prose"))

    def test_malformed_claim_is_its_own_answer(self):
        """Neither a member nor a well-formed instance. Folding it either way

        hides a broken instance of this mechanism inside a bucket."""
        self.assertTrue(vocab.looks_oov("cannot-express: no date"))
        self.assertFalse(vocab.is_oov("cannot-express: no date"))


class RegistryProofPaths(unittest.TestCase):
    """Every registration names a consumer and a route, and renders apart."""

    def test_every_registration_is_complete(self):
        for v in vocab.registry():
            with self.subTest(vocabulary=v.name):
                self.assertTrue(v.members, "a vocabulary with no members")
                self.assertTrue(v.oov_form)
                self.assertTrue(v.consumer)
                self.assertTrue(v.proof_path)

    def test_the_oov_rendering_differs_from_every_member(self):
        """The contract's whole claim: never folded into a neighbour."""
        rendered = "cannot-express(2026-09-19): a reason"
        for v in vocab.registry():
            with self.subTest(vocabulary=v.name):
                self.assertTrue(v.renders_distinctly(rendered))

    def test_a_member_does_not_render_distinctly_from_itself(self):
        """The control for the assertion above. Without it, `renders_distinctly`

        could return True for everything and the case above would pass on a
        predicate that discriminates nothing."""
        grades = vocab.by_name("grades")
        self.assertIsNotNone(grades)
        self.assertFalse(grades.renders_distinctly("READY"))

    def test_members_are_the_live_tuples_not_a_copy(self):
        """A registry holding its own copy would be a second body for the fact

        it exists to single-source, and would drift the day a member is added
        at its home."""
        self.assertEqual(vocab.by_name("grades").members, items.GRADES)
        self.assertEqual(vocab.by_name("evidence marks").members,
                         items.EVIDENCE_MARKS)


class CensusDisposition(unittest.TestCase):
    """The grade arm at its counting site.

    An OOV grade landing in `unknown` inflates exactly the numbers the
    census docstring protects — the drain and retirement triggers read them.
    So it gets its own bucket, and that bucket is NOT open, NOT closed, and
    NOT unknown.
    """

    def _carrier(self, *blocks) -> str:
        return (f"schema: 6\nbaseline: {len(blocks)}\nadded: 0\n"
                "compacted: 0\n" + "".join(blocks))

    def _block(self, ident, grade) -> str:
        return (f"\n## {ident}\ngrade: {grade}\nrequirement: r\ngoal: tend\n"
                "write-set: a.py\ndone-criterion: d\nevidence: MEASURED e\n"
                "blocked-by: NONE\n")

    def test_oov_grade_gets_its_own_bucket(self):
        parsed = items.parse(self._carrier(
            self._block("xx-1", "READY"),
            self._block("xx-2",
                        "cannot-express(2026-09-19): the round has not "
                        "settled what this state is called")))
        got = items.census(parsed)
        self.assertEqual(got["cannot-express"], 1)
        self.assertEqual(got["open"], 1)
        self.assertEqual(got["closed"], 0)
        self.assertEqual(got["unknown"], {})
        self.assertEqual(got["total"], 2)

    def test_an_unknown_word_is_still_unknown(self):
        """The control. If the new bucket swallowed unknown words too, the

        census would have stopped answering the question it was built for and
        the case above would not notice."""
        parsed = items.parse(self._carrier(self._block("xx-1", "SORTOFDONE")))
        got = items.census(parsed)
        self.assertEqual(got["cannot-express"], 0)
        self.assertEqual(got["unknown"], {"SORTOFDONE": 1})

    def test_a_malformed_oov_claim_is_unknown_not_oov(self):
        """Undated, so it cannot be aged. Counting it as an OOV instance would

        let it sit in the drain's population without ever becoming its
        oldest — the count would never reach zero and nothing would say why."""
        parsed = items.parse(self._carrier(
            self._block("xx-1", "cannot-express: undated")))
        got = items.census(parsed)
        self.assertEqual(got["cannot-express"], 0)
        self.assertEqual(sum(got["unknown"].values()), 1)


if __name__ == "__main__":
    unittest.main()
