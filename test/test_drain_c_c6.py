"""Drain wave C, lane C6 — retire, the roster runner, the slot parser, migrate.

lc-184: a declared glob home is anchored at the repo root, by depth.
"""

import _isolation  # noqa: F401

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import retire  # noqa: E402


class GlobHomeIsRootAnchored(unittest.TestCase):
    """lc-184. `Path.match` is right-anchored for a relative pattern, so
    `docs/*.md` claimed `plugin/docs/notes.md`. The inputs are the item's
    measured pair; the controls are the right-depth files that must still
    resolve (law 11: the repair must not turn a working home into a finding)."""

    def test_misplaced_one_level_down_is_not_claimed(self):
        self.assertFalse(retire._home_claims("docs/*.md", "plugin/docs/notes.md"))

    def test_misplaced_vendor_prefix_is_not_claimed(self):
        self.assertFalse(retire._home_claims(
            "docs/audits/*.md", "vendor/docs/audits/fake.md"))

    def test_controls_at_the_right_depth_still_resolve(self):
        self.assertTrue(retire._home_claims("docs/*.md", "docs/notes.md"))
        self.assertTrue(retire._home_claims("docs/audits/*.md",
                                            "docs/audits/real.md"))

    def test_a_glob_does_not_cross_a_directory_boundary(self):
        self.assertFalse(retire._home_claims("docs/*.md", "docs/a/b.md"))

    def test_a_pattern_with_a_prefix_inside_the_name_still_matches(self):
        self.assertTrue(retire._home_claims("docs/begehung-findings-*.tsv",
                                            "docs/begehung-findings-1.tsv"))
        self.assertFalse(retire._home_claims("docs/begehung-findings-*.tsv",
                                             "x/docs/begehung-findings-1.tsv"))


if __name__ == "__main__":
    unittest.main()
