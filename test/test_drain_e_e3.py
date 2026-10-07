"""Drain wave E, lane E3 — the wave join's own sentence (lc-139).

THE WAVE JOIN'S OWN SENTENCE (lc-139). `item waves` joins WRITE sets and
printed that its lanes are "disjoint by construction, so the whole set of
lanes is the PARALLEL set". A lane that edits a shared verification
instrument collides with every lane that RUNS it, and the join cannot see
that: no slot records what an item reads or executes. The repair taken is
the criterion's STATEMENT arm — the verb's own text says its predicate is
write-write only and names what it therefore cannot see — so these arms
assert the sentence, and that nothing else moved: no item gains a
collision, and the COULD NOT VERIFY line for items outside the lanes keeps
its exact text.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits  # noqa: E402
from lifecycle_core import items  # noqa: E402

from test_waves import WavesBase, block  # noqa: E402


class TheJoinSaysWhatItsPredicateCovers(WavesBase):
    """lc-139 — an assurance no wider than a write-write predicate."""

    def _limit(self, out):
        hits = [ln for ln in out.splitlines()
                if ln.startswith("WRITE-WRITE ONLY:")]
        self.assertEqual(len(hits), 1, out)
        return hits[0]

    def test_the_verb_states_its_predicate_and_what_it_cannot_see(self):
        with self._repo(INSTRUMENT_CASE) as repo:
            _code, out = self._waves(repo)
        limit = self._limit(out)
        self.assertIn("what items WRITE", limit)
        self.assertIn("READS or EXECUTES", limit)
        self.assertIn("verifier", limit)
        self.assertIn("no slot records", limit)

    def test_the_lanes_are_no_longer_called_THE_parallel_set_outright(self):
        with self._repo(INSTRUMENT_CASE) as repo:
            _code, out = self._waves(repo)
        self.assertNotIn(OLD_ASSURANCE, out)
        lanes = next(ln for ln in out.splitlines() if ln.startswith("LANES:"))
        self.assertIn("WRITE-WRITE", lanes)

    def test_the_CLEAN_verdict_carries_the_limit_too(self):
        with self._repo(INSTRUMENT_CASE) as repo:
            code, out = self._waves(repo)
        self.assertEqual(code, exits.CLEAN, out)
        verdict = next(ln for ln in out.splitlines()
                       if ln.startswith("item waves: CLEAN"))
        self.assertIn("WRITE-WRITE", verdict)

    def test_a_grouped_cut_with_no_crossing_is_not_parallel_outright(self):
        with self._repo(INSTRUMENT_CASE) as repo:
            _code, out = self._waves(repo, grouped=True)
        zero = next(ln for ln in out.splitlines()
                    if ln.startswith("SERIALIZE: 0"))
        self.assertIn("WRITE-WRITE", zero)

    def test_NO_item_gains_a_collision_the_join_did_not_compute(self):
        """The statement arm reports nothing new: four items on four files
        are still four lanes, each alone, and the exit is still CLEAN."""
        with self._repo(INSTRUMENT_CASE) as repo:
            code, out = self._waves(repo, grouped=True)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("LANES: 4 over 4 path-valued item(s).", out)
        alone = [ln for ln in out.splitlines() if " alone — " in ln]
        self.assertEqual(len(alone), 4, out)
        self.assertNotIn("      shared ", out)
        self.assertIn("SERIALIZE: 0", out)

    def test_an_ordinary_shared_file_is_still_the_only_collision(self):
        with self._repo([block("xx-1", "tools/prove-rows.py"),
                         block("xx-2", "tools/prove-rows.py"),
                         block("xx-3", "tools/init.py")]) as repo:
            _code, out = self._waves(repo)
        self.assertIn("LANES: 2 over 3 path-valued item(s).", out)
        self.assertIn("      shared tools/prove-rows.py: xx-1, xx-2", out)
        self.assertEqual(self._lane_of(out, "xx-1"),
                         self._lane_of(out, "xx-2"))
        self.assertNotEqual(self._lane_of(out, "xx-1"),
                            self._lane_of(out, "xx-3"))

    def test_the_COULD_NOT_VERIFY_line_keeps_its_exact_text(self):
        with self._repo([block("xx-1", "tools/prove-rows.py"),
                         block("xx-2", "tools/items.py"),
                         block("xx-3", "wherever the fix lands")]) as repo:
            code, out = self._waves(repo)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn(OUTSIDE_THE_LANES, out.splitlines())
        # The limit is stated over a partial plan as well: it is a property
        # of the predicate, not of a run that happened to end CLEAN.
        self._limit(out)


if __name__ == "__main__":
    unittest.main()
