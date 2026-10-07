"""Drain wave C, lane C6 — retire, the roster runner, the slot parser, migrate.

lc-184: a declared glob home is anchored at the repo root, by depth.
"""

import _isolation  # noqa: F401

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from unittest import mock  # noqa: E402

from lifecycle_core import exits, refusals, retire, roster  # noqa: E402


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


def _row(ident, fire, control, expect=exits.FINDING):
    return refusals.Row(ident=ident, refusal="r", firing_input="i",
                        expect=expect, fire=fire, control=control,
                        stage="drain-c6")


class OneRowCannotAbortTheRoster(unittest.TestCase):
    """lc-101. argparse's `parser.error` raises SystemExit, which
    `except Exception` does not catch, so one row with an argv that cannot
    parse stopped `--test` mid-run with no `rows:` summary."""

    def _run(self, rows):
        lines = []
        with mock.patch.object(refusals, "ROWS", rows):
            code = roster.cmd_test(lines.append)
        return code, "\n".join(lines)

    def _unparseable(self):
        import argparse
        argparse.ArgumentParser(prog="x").parse_args(["--no-such-flag"])

    def test_a_systemexit_in_a_row_fails_that_row_by_name_and_the_rest_run(self):
        ok = refusals.Fired(exits.FINDING, "FINDING [after_row] x")
        clean = refusals.Fired(exits.CLEAN, "clean")
        rows = [
            _row("drain_c6_bad", self._unparseable, lambda: clean),
            _row("after_row", lambda: ok, lambda: clean),
        ]
        code, text = self._run(rows)
        self.assertIn("rows: 2", text)               # the summary line exists
        self.assertIn("drain_c6_bad", text)          # the bad row is named
        self.assertIn("PASS  after_row", text)       # its sibling still ran
        self.assertNotEqual(code, exits.CLEAN)       # not a passing row

    def test_a_row_raising_an_ordinary_exception_still_surfaces(self):
        def boom():
            raise RuntimeError("unexpected")
        clean = refusals.Fired(exits.CLEAN, "clean")
        code, text = self._run([_row("drain_c6_boom", boom, lambda: clean)])
        self.assertIn("drain_c6_boom", text)
        self.assertIn("RuntimeError", text)
        self.assertNotEqual(code, exits.CLEAN)


if __name__ == "__main__":
    unittest.main()
