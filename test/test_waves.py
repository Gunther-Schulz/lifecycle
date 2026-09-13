"""`item waves` — the item→lane join over write-set overlap (lc-123).

WHAT THESE OWE, and why each arm is a pair rather than a single assertion:
the join's failure is SILENT IN BOTH DIRECTIONS. An under-join hands two
lanes the same file and breaks the one-writer rule; an over-join serializes
work that could have run at once. So the overlap arm and the disjoint arm are
written together over ONE carrier shape — a test that only proved "these two
land in one lane" would pass against a verb that puts everything in one lane,
which is precisely the degenerate answer.

THE NON-PATH BUCKETS ARE ASSERTED AS ABSENCES TOO. `prose-in-a-bucket` is
half the claim; the other half is `prose-in-NO-lane`, and only the second one
fails against a verb that clusters an item on the parsing half of a mixed
slot. An assertion on what must NOT appear catches a check degrading where a
presence assertion catches only one breaking.
"""

import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli as cli_mod, exits, items, refusals  # noqa: E402


def carrier(blocks, baseline=0):
    """A carrier file from `[(ident, {slot: value}), …]`, slots in order."""
    out = [f"schema: {items.SCHEMA_FLOOR}", f"baseline: {baseline}",
           "added: 0", "compacted: 0", ""]
    for ident, slots in blocks:
        out.append(f"## {ident}")
        for slot in items.SLOTS:
            out.append(f"{slot}: {slots[slot]}")
        for extra in slots.get("_extra", ()):
            out.append(extra)
        out.append("")
    return "\n".join(out)


def block(ident, write_set, *, grade="READY", blocked_by="NONE", extra=()):
    return (ident, {
        "grade": grade,
        "requirement": f"{ident} exists so the join has something to join "
                       "— record: test_waves.py",
        "goal": "mitigate",
        "write-set": write_set,
        "done-criterion": "the lane it lands in is the lane it belongs in",
        "evidence": "constructed for this battery",
        "blocked-by": blocked_by,
        "_extra": extra,
    })


class WavesBase(unittest.TestCase):

    def _repo(self, blocks):
        return refusals._Repo(items=carrier(blocks))

    def _waves(self, repo):
        here = os.getcwd()
        try:
            os.chdir(str(repo.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(repo.dir), "item", "waves"])
            return code, buf.getvalue()
        finally:
            os.chdir(here)

    def _lane_of(self, out, ident):
        """Which lane number lists `ident` as a member, or None."""
        for line in out.splitlines():
            if not line.startswith("lane "):
                continue
            head, _, body = line.partition(":")
            members = [t.strip(" ,") for t in body.replace("—", " ").split()]
            if ident in members:
                return head.split()[1]
        return None


class TheOverlapJoin(WavesBase):
    """The done-criterion's first two arms, over ONE carrier.

    The pair is the instrument: `a` and `b` share a file and must land in one
    lane, `c` shares nothing and must land in its own. Either arm alone is
    satisfied by a degenerate verb — all-one-lane passes the first,
    all-singletons passes the second.
    """

    BLOCKS = [
        block("xx-1", "tools/alpha.py,test/test_alpha.py"),
        block("xx-2", "tools/alpha.py,test/test_beta.py"),
        block("xx-3", "docs/unrelated.md"),
    ]

    def test_two_items_sharing_a_file_land_in_ONE_lane(self):
        with self._repo(self.BLOCKS) as r:
            code, out = self._waves(r)
            self.assertEqual(code, exits.CLEAN, out)
            self.assertEqual(self._lane_of(out, "xx-1"),
                             self._lane_of(out, "xx-2"), out)
            self.assertIn("LANES: 2 over 3 path-valued item(s)", out)

    def test_the_shared_file_is_NAMED_as_the_collision_evidence(self):
        """A lane without its binder is an assertion the desk cannot check —
        it would have to re-derive the overlap to know whether to believe
        the serialization."""
        with self._repo(self.BLOCKS) as r:
            _code, out = self._waves(r)
            self.assertIn("shared tools/alpha.py: xx-1, xx-2", out)
            # The files they do NOT share are not evidence of a collision.
            self.assertNotIn("shared test/test_alpha.py", out)

    def test_a_disjoint_item_lands_in_its_OWN_lane(self):
        with self._repo(self.BLOCKS) as r:
            _code, out = self._waves(r)
            self.assertNotEqual(self._lane_of(out, "xx-3"),
                                self._lane_of(out, "xx-1"), out)
            self.assertIn("xx-3 alone", out)

    def test_transitive_collisions_close_into_one_lane(self):
        """a–b and b–c bind, a and c share nothing: one lane, not two.

        Components, not pairs. A pairwise renderer would put `a` and `c` in
        different lanes while `b` sat in both — and two lanes holding one item
        between them is the one-writer breach the join exists to prevent.
        """
        blocks = [
            block("xx-1", "tools/alpha.py"),
            block("xx-2", "tools/alpha.py,tools/beta.py"),
            block("xx-3", "tools/beta.py"),
        ]
        with self._repo(blocks) as r:
            _code, out = self._waves(r)
            self.assertIn("LANES: 1 over 3 path-valued item(s)", out)
            self.assertEqual(self._lane_of(out, "xx-1"),
                             self._lane_of(out, "xx-3"), out)


class ADirectoryEntryCovers(WavesBase):
    """`test/` and `test/test_alpha.py` collide, and the report says whose
    slot did it.

    THE CONSERVATIVE DIRECTION IS A DECISION (see `wave_covers`): equality
    alone would call these two items parallel and hand both the same file.
    The second arm is what keeps the rule from being a substring match.
    """

    def test_a_directory_entry_binds_the_files_under_it(self):
        blocks = [block("xx-1", "test/"),
                  block("xx-2", "test/test_alpha.py")]
        with self._repo(blocks) as r:
            _code, out = self._waves(r)
            self.assertIn("LANES: 1 over 2 path-valued item(s)", out)
            self.assertIn("a DIRECTORY entry, written by xx-1", out)
            self.assertIn("covers files named by 1 other member(s): xx-2", out)

    def test_a_directory_entry_does_NOT_bind_a_sibling_with_the_same_prefix(self):
        """`test/` must not swallow `testing/alpha.py`. The must-not-move arm
        for the containment rule: a `startswith("test")` passes the arm above
        and fails this one."""
        blocks = [block("xx-1", "test/"),
                  block("xx-2", "testing/alpha.py")]
        with self._repo(blocks) as r:
            _code, out = self._waves(r)
            self.assertIn("LANES: 2 over 2 path-valued item(s)", out)
            self.assertNotEqual(self._lane_of(out, "xx-1"),
                                self._lane_of(out, "xx-2"), out)


class ProseIsBucketedAndNeverClustered(WavesBase):

    BLOCKS = [
        block("xx-1", "tools/alpha.py"),
        block("xx-2", "plugin (the parser bits) + battery"),
        block("xx-3", "tools/alpha.py (and the test beside it)"),
    ]

    def test_a_prose_write_set_lands_in_the_prose_bucket(self):
        with self._repo(self.BLOCKS) as r:
            code, out = self._waves(r)
            self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
            self.assertIn("prose: 2", out)
            self.assertIn("xx-2: does not parse as a path", out)

    def test_a_prose_write_set_lands_in_NO_lane(self):
        """The half a presence assertion cannot catch."""
        with self._repo(self.BLOCKS) as r:
            _code, out = self._waves(r)
            self.assertIsNone(self._lane_of(out, "xx-2"), out)
            self.assertIn("LANES: 1 over 1 path-valued item(s)", out)

    def test_a_MIXED_slot_is_not_clustered_on_its_parsing_half(self):
        """xx-3's entry names `tools/alpha.py` inside prose. Reading it as a
        path would put xx-3 in xx-1's lane on a boundary nobody stated."""
        with self._repo(self.BLOCKS) as r:
            _code, out = self._waves(r)
            self.assertIsNone(self._lane_of(out, "xx-3"), out)
            self.assertNotIn("xx-1, xx-3", out)

    def test_every_non_path_bucket_prints_its_ZERO(self):
        """An omitted key reads exactly like `checked and clean`."""
        with self._repo([block("xx-1", "tools/alpha.py")]) as r:
            _code, out = self._waves(r)
            for key in items.WAVE_NON_PATH:
                with self.subTest(bucket=key):
                    self.assertIn(f"  {key}: 0 — none", out)


class SentinelsAndForeignBoundaries(WavesBase):

    def test_UNKNOWN_and_NONE_land_in_their_own_bucket_not_in_prose(self):
        """Three answers, not two: a slot nobody filled and a slot filled with
        prose are different states and route to different repairs."""
        blocks = [block("xx-1", "tools/alpha.py"),
                  block("xx-2", "NONE")]
        with self._repo(blocks) as r:
            code, out = self._waves(r)
            self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
            self.assertIn(f"  {items.WAVE_UNSET}: 1", out)
            self.assertIn(f"  {items.WAVE_PROSE}: 0 — none", out)
            self.assertIsNone(self._lane_of(out, "xx-2"), out)

    def test_a_foreign_path_lands_in_the_other_repo_bucket(self):
        """This carrier's own foreign form, `<path>@<repo>` (lc-66/lc-67)."""
        blocks = [block("xx-1", "tools/alpha.py"),
                  block("xx-2", "docs/design.md@cache-fix")]
        with self._repo(blocks) as r:
            _code, out = self._waves(r)
            self.assertIn(f"  {items.WAVE_FOREIGN}: 1", out)
            self.assertIn("outside this repo", out)
            self.assertIsNone(self._lane_of(out, "xx-2"), out)


class TheEffectiveSlotIsWhatClusters(WavesBase):
    """THE EFFECTIVE SLOT RULE: the last `amended-write-set:` line wins.

    An item amended onto a different write boundary is clustered by the NEW
    one. The pair is the instrument — it lands in the amended item's lane AND
    NOT in the one its base slot named; without the second arm a verb reading
    the base slot passes whenever the two lanes happen to coincide.
    """

    BLOCKS = [
        block("xx-1", "tools/alpha.py"),
        block("xx-2", "tools/beta.py"),
        block("xx-3", "tools/alpha.py",
              extra=("amend-reason: 2026-09-13 the boundary moved when the "
                     "work did",
                     "amended-write-set: 2026-09-13 tools/beta.py")),
    ]

    def test_the_AMENDED_write_set_decides_the_lane(self):
        with self._repo(self.BLOCKS) as r:
            code, out = self._waves(r)
            self.assertEqual(code, exits.CLEAN, out)
            self.assertEqual(self._lane_of(out, "xx-3"),
                             self._lane_of(out, "xx-2"), out)

    def test_the_BASE_write_set_no_longer_clusters_it(self):
        with self._repo(self.BLOCKS) as r:
            _code, out = self._waves(r)
            self.assertNotEqual(self._lane_of(out, "xx-3"),
                                self._lane_of(out, "xx-1"), out)
            self.assertIn("shared tools/beta.py: xx-2, xx-3", out)
            self.assertNotIn("shared tools/alpha.py", out)


class TheEmptyPopulationSaysSo(WavesBase):
    """0 lanes over 0 items reads exactly like "checked, nothing collides"."""

    def test_no_READY_item_is_COULD_NOT_VERIFY_and_says_what_it_scanned(self):
        with self._repo([block("xx-1", "tools/alpha.py", grade="NEW")]) as r:
            code, out = self._waves(r)
            self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
            self.assertIn("COULD NOT VERIFY: no schedulable item", out)
            self.assertIn("1 live item(s), 0 READY", out)
            self.assertNotIn("LANES:", out)

    def test_a_READY_item_held_back_by_its_BLOCKER_is_named_not_subtracted(self):
        """The population shrank; a reader who cannot see WHICH item left
        reads the plan as covering the whole READY set."""
        blocks = [block("xx-1", "tools/alpha.py", grade="READY",
                        blocked_by="decision whether alpha survives at all")]
        with self._repo(blocks) as r:
            code, out = self._waves(r)
            self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
            self.assertIn("1 READY, 0 schedulable", out)
            self.assertIn("held back: xx-1", out)


class ItWritesNothing(WavesBase):
    """Read-only is a claim about the carrier, so it is asserted at the
    carrier — the bytes before and after, not the verb's own promise."""

    def test_the_carrier_is_byte_identical_after_a_run(self):
        blocks = [block("xx-1", "tools/alpha.py"),
                  block("xx-2", "tools/alpha.py")]
        with self._repo(blocks) as r:
            before = (r.dir / "ITEMS.md").read_bytes()
            code, out = self._waves(r)
            self.assertEqual(code, exits.CLEAN, out)
            self.assertEqual((r.dir / "ITEMS.md").read_bytes(), before)


class TheUnitsUnderTheReport(unittest.TestCase):
    """The classifier and the containment rule, where the CLI cannot reach
    every edge cheaply."""

    def test_the_sentinels_are_the_intake_joins_own(self):
        """Single-sourced: a second split here would drift from
        `verbs.write_set_entries` the day either moved."""
        for value in ("UNKNOWN", "none", " NONE "):
            with self.subTest(value=value):
                bucket, paths, _why = items.classify_write_set(value)
                self.assertEqual(bucket, items.WAVE_UNSET)
                self.assertEqual(paths, [])

    def test_a_venue_entry_is_not_a_path(self):
        bucket, paths, why = items.classify_write_set(
            "plugin/cli/x.py,decision:who-owns-this")
        self.assertEqual(bucket, items.WAVE_PROSE)
        self.assertEqual(paths, [])
        self.assertIn("1 of 2", why)

    def test_a_trailing_slash_survives_normalization(self):
        self.assertEqual(items.wave_normalize("./test/"), "test/")
        self.assertEqual(items.wave_normalize("test//alpha.py"),
                         "test/alpha.py")

    def test_covers_is_segment_wise(self):
        self.assertTrue(items.wave_covers("test/", "test/alpha.py"))
        self.assertTrue(items.wave_covers("test/", "test"))
        self.assertFalse(items.wave_covers("test/", "testing/alpha.py"))
        self.assertFalse(items.wave_covers("test", "test/alpha.py"))

    def test_ids_sort_the_way_their_author_reads_them(self):
        self.assertEqual(
            sorted(["lc-100", "lc-16", "lc-9"], key=items._wave_ident_key),
            ["lc-9", "lc-16", "lc-100"])


if __name__ == "__main__":
    unittest.main()
