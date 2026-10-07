"""Drain wave E, lane E5: instruments that say less than they do.

lc-198: a SKIPPED reach arm must be visible in the suite verdict
(`tools/verify-suite.py`), read off the result object.
lc-136: the explicit-zero sweep's disposition table.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import ast
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools" / "verify-suite.py"
TEST_DIR = REPO_ROOT / "test"

CLEAN, FINDING, COULD_NOT_VERIFY = 0, 2, 3


def _suite(body: str) -> Path:
    """A throwaway one-file suite; returns its directory."""
    d = Path(tempfile.mkdtemp(prefix="lane-e5-suite-"))
    (d / "test_probe.py").write_text(textwrap.dedent(body), encoding="utf-8")
    return d


def _run(start_dir: Path):
    return subprocess.run(
        [sys.executable, str(TOOL), "--start-dir", str(start_dir)],
        capture_output=True, text=True, timeout=120)


class ReachArmSkipIsVisible(unittest.TestCase):

    def test_the_real_reach_arm_carries_the_REACH_ARM_marker_when_it_skips(self):
        """The arm lc-198 names, run for real with its sibling input absent.

        `Path.exists` is patched to False so the arm skips on every machine,
        including one that DOES have a sibling dotfiles checkout; the skip
        reason is read off the result object, never a -v rendering (law 17).
        """
        sys.path.insert(0, str(TEST_DIR))
        try:
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromName(
                "test_verbs.LedgerStorableBlocker."
                "test_the_67_REPAIRED_dotfiles_TEXTS_all_pass_and_the_OLD_ONES_do_not")
            res = unittest.TestResult()
            with mock.patch("pathlib.Path.exists", return_value=False):
                suite.run(res)
        finally:
            sys.path.remove(str(TEST_DIR))
        self.assertEqual(len(res.skipped), 1, res.skipped)
        self.assertTrue(res.skipped[0][1].startswith("REACH ARM:"),
                        res.skipped[0][1])

    def test_a_reach_arm_skip_is_COULD_NOT_VERIFY_with_the_count_stated(self):
        d = _suite('''
            import unittest
            class T(unittest.TestCase):
                def test_ok(self):
                    pass
                def test_reach(self):
                    self.skipTest("REACH ARM: no sibling checkout")
        ''')
        p = _run(d)
        self.assertEqual(p.returncode, COULD_NOT_VERIFY, p.stdout + p.stderr)
        self.assertIn("skipped: 1", p.stdout)
        self.assertIn("test_probe.T.test_reach", p.stdout)
        self.assertIn("COULD NOT VERIFY", p.stdout)

    def test_an_ordinary_skip_is_reported_and_stays_clean(self):
        """MUST-NOT-MOVE: an arm that legitimately cannot run may skip."""
        d = _suite('''
            import unittest
            class T(unittest.TestCase):
                def test_ok(self):
                    pass
                def test_other(self):
                    self.skipTest("platform has no such thing")
        ''')
        p = _run(d)
        self.assertEqual(p.returncode, CLEAN, p.stdout + p.stderr)
        self.assertIn("skipped: 1", p.stdout)
        self.assertIn("test_probe.T.test_other", p.stdout)

    def test_a_failure_is_a_finding_and_zero_skips_is_stated(self):
        d = _suite('''
            import unittest
            class T(unittest.TestCase):
                def test_bad(self):
                    self.assertEqual(1, 2)
        ''')
        p = _run(d)
        self.assertEqual(p.returncode, FINDING, p.stdout + p.stderr)
        self.assertIn("skipped: 0", p.stdout)

    def test_a_run_that_examined_nothing_is_COULD_NOT_VERIFY(self):
        d = Path(tempfile.mkdtemp(prefix="lane-e5-suite-"))
        p = _run(d)
        self.assertEqual(p.returncode, COULD_NOT_VERIFY, p.stdout + p.stderr)
        self.assertIn("ran: 0", p.stdout)

    def test_a_reach_skip_outranks_a_failure(self):
        d = _suite('''
            import unittest
            class T(unittest.TestCase):
                def test_bad(self):
                    self.assertEqual(1, 2)
                def test_reach(self):
                    self.skipTest("REACH ARM: gone")
        ''')
        p = _run(d)
        self.assertEqual(p.returncode, COULD_NOT_VERIFY, p.stdout + p.stderr)


# --- lc-136: the explicit-zero sweep --------------------------------------

#: A STATED zero in an asserted string: `<label>: 0 — none` or
#: `<label>: 0 of <n>`. Law 1 requires the stated zero; the defect is that the
#: assertion is satisfied by a producer that is DEAD (lc-124: `SERIALIZE: 0`
#: stayed green under a mutation dropping every warning). Scope, named so the
#: sweep is not over-read: it covers asserted STRINGS carrying a stated zero
#: in test_waves.py and test_items.py; `assertEqual(x, [])` over a returned
#: list is a different shape and is not swept here.
_STATED_ZERO = re.compile(r": 0 (?:—|of )")
_SWEPT = ("test_waves.py", "test_items.py")

#: Every swept arm's DISPOSITION: the non-zero arm over the SAME producer that
#: goes red when the producer is dead. `(file, test, regex)`: the regex must
#: match the pair's own source, so a pair whose assertion was edited away goes
#: red here. The table is checked BOTH ways against the sweep's derivation
#: (an arm the sweep finds with no row, a row whose arm is gone), so it cannot
#: age silently. Producer-dead mutations run for the three producers,
#: 2026-10-07: bucket counts (`hits = []`): the pairs below for prose, unset,
#: venue, foreign and unresolved went red, the zero arms stayed green;
#: SERIALIZE (`if True:`): only the cross-group arm went red; FILTERED
#: (`len(kept)*0`): test_filter_returns_only_that_goal went red.
_PROSE_PAIR = ("test_waves.py",
               "test_a_prose_write_set_lands_in_the_prose_bucket",
               r'"prose: 2"')
_VENUE_PAIR = ("test_waves.py",
               "test_the_venue_bucket_prints_its_count_and_LEAVES_prose_empty",
               r'"  venue: 1"')
_FILTER_PAIR = ("test_items.py", "test_filter_returns_only_that_goal",
                r"FILTERED to goal=verify: 1 of 2")
DISPOSITIONS = {
    ("test_waves.py", "test_every_non_path_bucket_prints_its_ZERO"): (
        _PROSE_PAIR, _VENUE_PAIR,
        ("test_waves.py",
         "test_UNKNOWN_and_NONE_land_in_their_own_bucket_not_in_prose",
         r"WAVE_UNSET\}: 1"),
        ("test_waves.py", "test_a_foreign_path_lands_in_the_other_repo_bucket",
         r"WAVE_FOREIGN\}: 1"),
        ("test_drain_c_c4.py",
         "test_the_misspelled_item_is_NAMED_with_the_path_that_did_not_resolve",
         r"WAVE_UNRESOLVED\}: 1")),
    ("test_waves.py",
     "test_UNKNOWN_and_NONE_land_in_their_own_bucket_not_in_prose"): (
        _PROSE_PAIR,),
    ("test_waves.py",
     "test_a_partition_with_no_cross_group_file_prints_its_ZERO"): (
        ("test_waves.py",
         "test_the_cross_group_shared_file_is_NAMED_with_BOTH_groups",
         r"tools/cold\.py:"),),
    ("test_waves.py",
     "test_the_venue_bucket_prints_its_count_and_LEAVES_prose_empty"): (
        _PROSE_PAIR,),
    ("test_waves.py", "test_a_carrier_with_no_venue_prints_the_venue_ZERO"): (
        _VENUE_PAIR,),
    ("test_items.py",
     "test_declared_goal_with_no_ready_work_is_an_explicit_zero"): (
        _FILTER_PAIR,),
    ("test_items.py", "test_the_reserved_meta_goal_is_queryable"): (
        _FILTER_PAIR,),
}


def _functions(path: Path):
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.setdefault(node.name, []).append(
                (node, ast.get_source_segment(src, node) or ""))
    return out


def _strings(node):
    """Every literal string piece under `node`, f-string pieces included."""
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            yield sub.value


def sweep():
    """`{(file, test): [asserted zero strings]}` DERIVED from the sources."""
    found = {}
    for name in _SWEPT:
        for fname, defs in _functions(TEST_DIR / name).items():
            for node, _src in defs:
                for call in ast.walk(node):
                    if not (isinstance(call, ast.Call)
                            and isinstance(call.func, ast.Attribute)
                            and call.func.attr == "assertIn"):
                        continue
                    for text in _strings(call.args[0]):
                        if _STATED_ZERO.search(text):
                            found.setdefault((name, fname), []).append(text)
    return found


class ExplicitZeroArmsAreEachPaired(unittest.TestCase):

    def test_the_sweep_finds_arms_and_names_each_with_its_disposition(self):
        derived = sweep()
        report = "\n".join(
            f"  {f}::{t} {texts} -> "
            + ("; ".join(p[1] for p in DISPOSITIONS[(f, t)])
               if (f, t) in DISPOSITIONS else "NO DISPOSITION")
            for (f, t), texts in sorted(derived.items()))
        # A zero count here would be a stated zero, never an omitted key.
        self.assertTrue(derived, "the sweep found no explicit-zero arm: it "
                        "examined nothing or its pattern is dead")
        self.assertEqual(sorted(derived), sorted(DISPOSITIONS),
                         "arms found vs dispositions recorded:\n" + report)

    def test_every_pair_exists_and_still_asserts_a_nonzero_over_the_producer(self):
        for (f, t), pairs in sorted(DISPOSITIONS.items()):
            for pfile, ptest, regex in pairs:
                with self.subTest(arm=f"{f}::{t}", pair=f"{pfile}::{ptest}"):
                    defs = _functions(TEST_DIR / pfile).get(ptest)
                    self.assertTrue(defs, f"pair {pfile}::{ptest} is gone")
                    self.assertTrue(
                        any(re.search(regex, src) for _n, src in defs),
                        f"{ptest} no longer asserts /{regex}/")

    def test_the_sweep_is_live_on_a_known_positive_and_a_known_negative(self):
        """Positive: the SERIALIZE zero arm of lc-124 is found. Negative: an
        arm asserting a NON-zero count line is not."""
        derived = sweep()
        self.assertIn(
            ("test_waves.py",
             "test_a_partition_with_no_cross_group_file_prints_its_ZERO"),
            derived)
        self.assertNotIn(
            ("test_waves.py",
             "test_a_prose_write_set_lands_in_the_prose_bucket"), derived)


# --- lc-95: the Verify section is executed and its numbers derived ---------

CHECK = REPO_ROOT / "tools" / "verify-claude-md.py"

_NODE_TEST = """\
import test from 'node:test';
test('a', () => {});
test('b', () => {});
test('c', () => {});
"""


def _doc(prose: str, commands: str) -> Path:
    """A throwaway repo dir holding a CLAUDE.md-shaped file and its inputs."""
    d = Path(tempfile.mkdtemp(prefix="lane-e5-doc-"))
    (d / "x.test.mjs").write_text(_NODE_TEST, encoding="utf-8")
    (d / "noisy.py").write_text(
        "import sys\nprint('fatal: Not a valid object name', file=sys.stderr)\n",
        encoding="utf-8")
    (d / "bad.py").write_text("import sys\nsys.exit(4)\n", encoding="utf-8")
    (d / "CLAUDE.md").write_text(
        f"# t\n\n## Verify\n\n```bash\n{commands}```\n\n{prose}\n\n## Next\n",
        encoding="utf-8")
    return d


def _check(d: Path, *extra):
    return subprocess.run(
        [sys.executable, str(CHECK), "--repo", str(d), *extra],
        capture_output=True, text=True, timeout=120)


@unittest.skipIf(subprocess.run(["node", "--version"],
                                capture_output=True).returncode != 0,
                 "REACH ARM: node is not installed here")
class VerifySectionIsExecutedAndDerived(unittest.TestCase):

    def test_a_drifted_stated_count_is_a_FINDING_naming_both_numbers(self):
        d = _doc("All 5 node bites pass here.",
                 "node --test x.test.mjs             # the bites\n")
        p = _check(d)
        self.assertEqual(p.returncode, FINDING, p.stdout + p.stderr)
        self.assertIn("derived tests=3", p.stdout)
        self.assertIn("section says 5", p.stdout)

    def test_the_same_section_with_the_true_count_is_CLEAN(self):
        """Pair of the arm above: the figure is DERIVED, so the TRUE number
        passes and the drifted one fails; a check carrying its own copy of
        a count would fail one of the two."""
        d = _doc("All 3 node bites pass here.",
                 "node --test x.test.mjs\n")
        p = _check(d)
        self.assertEqual(p.returncode, CLEAN, p.stdout + p.stderr)
        self.assertIn("AGREES", p.stdout)

    def test_a_pass_fail_skipped_sentence_is_compared_field_by_field(self):
        d = _doc("MEASURED: 3 pass, 1 fail, 0 skipped.",
                 "node --test x.test.mjs\n")
        p = _check(d)
        self.assertEqual(p.returncode, FINDING, p.stdout + p.stderr)
        self.assertIn("fail=0", p.stdout)

    def test_a_documented_command_that_prints_fatal_is_a_FINDING(self):
        """The lc-89 shape: exit 0, a `fatal:` line in the output."""
        d = _doc("", "python3 noisy.py\n")
        p = _check(d)
        self.assertEqual(p.returncode, FINDING, p.stdout + p.stderr)
        self.assertIn("fatal: Not a valid object name", p.stdout)

    def test_a_command_that_exits_nonzero_is_a_FINDING(self):
        d = _doc("", "python3 bad.py\n")
        p = _check(d)
        self.assertEqual(p.returncode, FINDING, p.stdout + p.stderr)
        self.assertIn("exit 4", p.stdout)

    def test_a_skipped_command_is_COULD_NOT_VERIFY_never_a_pass(self):
        d = _doc("", "python3 bad.py\n")
        p = _check(d, "--skip", "bad.py")
        self.assertEqual(p.returncode, COULD_NOT_VERIFY, p.stdout + p.stderr)
        self.assertIn("SKIPPED", p.stdout)

    def test_a_stated_number_for_a_runner_that_did_not_run_is_named(self):
        d = _doc("Ran 340 tests.", "python3 noisy.py\n")
        p = _check(d, "--skip", "noisy.py")
        self.assertEqual(p.returncode, COULD_NOT_VERIFY, p.stdout + p.stderr)
        self.assertIn("which did not run", p.stdout)

    def test_a_missing_section_is_COULD_NOT_VERIFY(self):
        d = _doc("", "python3 noisy.py\n")
        p = _check(d, "--section", "## Nowhere")
        self.assertEqual(p.returncode, COULD_NOT_VERIFY, p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
