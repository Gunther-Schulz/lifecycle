"""The intake join's token half, over a MIGRATED carrier (lc-46).

The VERB's own refusal is a roster row (`join_undisposed`), and it fires on a
shared WRITE-SET path — so the roster proves the refusal and says nothing
about the token match beside it. These cover what the token match owes, which
is the half whose failure is silent in both directions: a join that fires on
nearly every item trains the reflex that kills it (R11), and one that fires on
nothing is a merge check that has stopped checking.

THE FIXTURES CARRY THE MIGRATION'S OWN TAIL because that is the defect's
mechanism, not decoration: every migrated body ends in `— record:
<carrier>:<line>`, so `record` and `backlog` land in nearly every requirement
line at once and supply `MATCH_MIN_TOKENS` by construction. Measured over
dotfiles' migrated carrier 2026-08-27: 126 of 138 live items matched an
ordinary add.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import items, verbs  # noqa: E402

TAIL = " — record: BACKLOG.md:{n}"

#: Subjects with no word in common — so the ONLY thing every item shares is
#: the migration tail. Without that property the fixture could not tell a
#: rarity rule from a broken one.
SUBJECTS = (
    "the sampler emits a truncated waveform on its second pass",
    "kerning tables drift after a font upgrade",
    "invoices round downward at the third decimal",
    "night mode inverts photographs of documents",
    "shipping labels print mirrored on continuous stationery",
    "the greenhouse valve reopens without a schedule",
    "backup rotation keeps eleven weeklies instead of four",
    "map tiles blur at zoom seventeen",
    "subtitles desynchronise after a chapter jump",
    "the turnstile counts pairs as singles",
)


def carrier(subjects, prefix="xx"):
    out = ["schema: 2", "baseline: 0", ""]
    for i, subject in enumerate(subjects, start=1):
        out += [
            f"## {prefix}-{i}",
            "grade: NEW",
            f"requirement: PARKED 2026-08-27 — {subject}"
            + TAIL.format(n=100 + i),
            "goal: mitigate",
            f"write-set: tools/thing{i}.py",
            "done-criterion: it stops doing that",
            "evidence: none yet",
            "blocked-by: NONE",
            "",
        ]
    return "\n".join(out)


def incoming(subject, n=999):
    return f"PARKED 2026-08-27 — {subject}" + TAIL.format(n=n)


class RarityWeightedJoin(unittest.TestCase):

    def setUp(self):
        self.parsed = items.parse(carrier(SUBJECTS))
        self.assertEqual(self.parsed.problems, [], "fixture must be clean")
        self.assertEqual(len(self.parsed.items), len(SUBJECTS))

    def test_the_migration_tail_alone_matches_NOTHING(self):
        """The defect itself: an add sharing only the tail with every item.

        `record` and `backlog` are two tokens, `MATCH_MIN_TOKENS` is two, so
        before this the tail alone matched the whole carrier.
        """
        req = incoming("the pump primes twice on a cold morning")
        found = verbs.candidates(self.parsed, req, "tools/pump.py")
        self.assertEqual(found, [], [i.ident for i, _ in found])

    def test_the_ARRANGEMENT_that_test_rests_on(self):
        """Its own control — without this the test above passes against a
        join that matches nothing at all.

        Both halves are asserted from the fixture: the tail tokens ARE shared
        (so the old two-token rule would have fired on every item), and they
        ARE the only thing shared.
        """
        req = incoming("the pump primes twice on a cold morning")
        want = verbs.requirement_tokens(req)
        for it in self.parsed.items:
            mine = verbs.requirement_tokens(it.slots["requirement"])
            self.assertEqual(want & mine, {"record", "backlog", "parked",
                                           "2026-08-27"},
                             f"{it.ident}: the fixture's only shared tokens "
                             "must be the tail's")
        freq = verbs.document_frequency(self.parsed.items)
        self.assertEqual(freq["record"], len(SUBJECTS))
        self.assertEqual(freq["backlog"], len(SUBJECTS))

    def test_two_items_sharing_RARE_tokens_still_match(self):
        """THE MUST-NOT-MOVE ARM. A rarity rule that dropped these would be
        a join that has stopped joining, and its green is identical to the
        green above."""
        req = incoming("kerning tables drift after a wholesale font upgrade")
        found = verbs.candidates(self.parsed, req, "tools/fonts.py")
        self.assertEqual([i.ident for i, _ in found], ["xx-2"], found)
        self.assertIn("kerning", found[0][1][0])

    def test_a_planted_REAL_duplicate_still_fires(self):
        req = incoming(SUBJECTS[4])
        found = verbs.candidates(self.parsed, req, "tools/labels.py")
        self.assertEqual([i.ident for i, _ in found], ["xx-5"], found)

    def test_a_shared_WRITE_SET_path_matches_whatever_the_tokens_do(self):
        """The path half is exact and has no vocabulary that can flood, so
        rarity must not reach it: an add sharing ONLY the tail but landing in
        a live item's file is still a candidate."""
        req = incoming("the pump primes twice on a cold morning")
        found = verbs.candidates(self.parsed, req, "tools/thing3.py")
        self.assertEqual([i.ident for i, _ in found], ["xx-3"], found)
        self.assertIn("shares write-set", found[0][1][0])

    def test_a_TWO_ITEM_carrier_still_joins(self):
        """The small-carrier arm, and it is where a naive fraction dies:
        document frequency counts the candidate itself, so in a two-item
        carrier every shared token sits at 100% and a whole-carrier fraction
        would drop the lot — killing the duplicate detection exactly where
        the carrier is smallest."""
        small = items.parse(carrier(SUBJECTS[:2]))
        req = incoming(SUBJECTS[1])
        found = verbs.candidates(small, req, "tools/fonts.py")
        self.assertEqual([i.ident for i, _ in found], ["xx-2"], found)

    def test_a_CLOSED_item_is_never_a_candidate(self):
        """Unchanged by lc-46 and asserted because the live filter moved:
        `candidates` now builds the live list once, up front, for the
        frequency table. A filter that moved and stopped filtering would be
        invisible in every test above."""
        text = carrier(SUBJECTS).replace("## xx-2\ngrade: NEW",
                                         "## xx-2\ngrade: DONE")
        found = verbs.candidates(items.parse(text),
                                 incoming(SUBJECTS[1]), "tools/fonts.py")
        self.assertEqual(found, [], found)


if __name__ == "__main__":
    unittest.main()
