"""Drain wave E, lane E9: lc-23 (init seeds the carriers), lc-225 (the
round series), lc-41 (commit-or-say), lc-194 (a shell answers for the last
process only)."""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "plugin" / "cli"))

from lifecycle_core import cli, exits  # noqa: E402
from lifecycle_core import declaration as decl  # noqa: E402

from test_init import ScratchGitRepo  # noqa: E402
from test_records import GOOD as GOOD_RECORD, run_one as run_record  # noqa: E402


def _run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(argv)
    return code, buf.getvalue()


class Lc23InitSeedsCarriers(unittest.TestCase):
    """lc-23: a greenfield repo after init has the three carriers resolvable
    and `kind check` answers CLEAN rather than COULD NOT VERIFY on them."""

    def _bare(self):
        r = ScratchGitRepo()
        r.write("CLAUDE.md", "# laws\n")
        r.commit_as("op@example.invalid")
        self.addCleanup(r.close)
        return r

    def test_bare_repo_after_init_has_clean_kind_check(self):
        r = self._bare()
        code, out = _run(["--repo", str(r.dir), "init"])
        self.assertEqual(code, exits.CLEAN, out)
        for name in ("ITEMS.md", "ITEMS-DONE.md", "LEDGER.md"):
            self.assertTrue((r.dir / name).is_file(), name)
            self.assertIn(f"seeded {name}", out)
        code2, out2 = _run(["--repo", str(r.dir), "kind", "check"])
        self.assertEqual(code2, exits.CLEAN, out2)
        self.assertNotIn("is not present", out2)

    def test_present_carrier_is_left_untouched(self):
        r = self._bare()
        r.write("LEDGER.md", f"schema: {decl.SCHEMA_FLOOR}\n\nkept line\n")
        before = (r.dir / "LEDGER.md").read_text()
        code, out = _run(["--repo", str(r.dir), "init"])
        self.assertEqual((r.dir / "LEDGER.md").read_text(), before)
        self.assertIn("LEDGER.md already present", out)
        self.assertTrue((r.dir / "ITEMS.md").is_file())


def _with_rounds(*lines):
    return GOOD_RECORD + "".join(f"{ln}\n" for ln in lines)


class Lc225RoundSeries(unittest.TestCase):
    """lc-225: the record carries per-round yield and `record check` prints
    the series where the next round's composer reads it; a zero-yield round
    is an explicit zero. Three answers, one arm each."""

    def test_control_without_rounds_prints_no_series_and_stays_clean(self):
        code, out = run_record(GOOD_RECORD)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("ROUNDS", out)

    def test_series_is_printed_with_explicit_zeros_and_stays_clean(self):
        code, out = run_record(_with_rounds(
            "2026-09-19 ROUND 1 yield: 2 — first instrument",
            "2026-09-20 ROUND 2 yield: 0 — second instrument",
            "2026-09-21 ROUND 3 yield: 0 — third instrument"))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("round 4 is next", out)
        self.assertIn("round 2: yield 0", out)
        self.assertIn("round 3: yield 0", out)
        self.assertIn("the last 2 round(s) returned nothing new", out)

    def test_nonzero_last_round_names_its_yield_not_a_zero_run(self):
        code, out = run_record(_with_rounds(
            "ROUND 1 yield: 0 — a", "ROUND 2 yield: 3 — b"))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("the last round yielded 3", out)
        self.assertNotIn("returned nothing new", out)

    def test_skipped_round_number_is_a_finding(self):
        code, out = run_record(_with_rounds(
            "ROUND 1 yield: 1 — a", "ROUND 3 yield: 0 — c"))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[record_round_series_broken]", out)

    def test_round_without_a_readable_yield_is_could_not_verify(self):
        code, out = run_record(_with_rounds(
            "ROUND 1 yield: 1 — a", "ROUND 2 — forgot the yield"))
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("[record_round_unreadable]", out)

    def test_non_integer_yield_is_could_not_verify(self):
        code, out = run_record(_with_rounds("ROUND 1 yield: lots — a"))
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)


if __name__ == "__main__":
    unittest.main()
