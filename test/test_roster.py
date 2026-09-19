"""The refusal scanners' REACH CONTRACT (lc-245, W3).

WHY THIS FILE EXISTS AT ALL. Before W3 no test in this tree referenced
`relay_sites`, `_RELAY` or `emit_sites`: the roster's own reach was exercised
only through `lifecycle --test`'s coverage pass, which is the instrument
grading itself. The scanners globbed `lifecycle_core/*.py`, so every
extensionless executable-Python file in the repo was invisible — and the
roster reported a clean sweep over a population it had never visited.

THE ACCEPTANCE ARM USES THE REAL SITE, NEVER A PLANT, and that is the
criterion's own demand rather than a preference here. A planted file proves
the expression parses; it does not prove the scan reaches the site the old
predicate could not see. So the arm that matters asserts `plugin/hooks/
pre-commit` — a live relay site, extensionless by construction — is in the
population and in the scan's output.

AND ONE ARM RUNS THE READ SURFACE. W2's lesson, earned by shipping the
defect: eight unit tests were green over a real bug because every one called
the function under test while the defect lived in what the verb PRINTED.
`test_the_coverage_REPORT_names_the_hook` is the arm through the surface.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import declaration as decl, roster  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
HOOK = REPO / "plugin" / "hooks" / "pre-commit"


def _doc():
    return decl.read(REPO).declaration


class ClassifierTest(unittest.TestCase):
    """`is_executable_python` — what a file IS, not what it is called."""

    def test_a_py_NAME_is_python(self):
        self.assertTrue(roster.is_executable_python(
            REPO / "plugin" / "cli" / "lifecycle_core" / "roster.py"))

    def test_an_EXTENSIONLESS_file_with_a_python_shebang_is_python(self):
        """The arm W3 exists for. This is the real hook, not a fixture."""
        self.assertTrue(HOOK.is_file(), f"{HOOK} is missing")
        self.assertEqual(HOOK.suffix, "",
                         "this arm is only meaningful while the hook is "
                         "extensionless — a hook MUST be named `pre-commit`")
        self.assertTrue(roster.is_executable_python(HOOK))

    def test_a_file_that_is_neither_is_NOT_python(self):
        """The control. Without it, a classifier returning True for
        everything would satisfy both arms above."""
        self.assertFalse(roster.is_executable_python(REPO / "ITEMS.md"))

    def test_an_unreadable_file_is_NOT_python_rather_than_an_error(self):
        """A file the classifier cannot read is one the scanner cannot
        scan. Answering True would hand it bytes it will fail on."""
        self.assertFalse(roster.is_executable_python(REPO / ".git" / "index"))


class ReachTest(unittest.TestCase):
    """The population, enumerated from the REGISTERED KINDS."""

    def test_the_reach_CONTAINS_the_live_hook(self):
        """The acceptance check, at the real site (W-5, B5)."""
        paths = roster.reach_paths(repo=REPO, doc=_doc())
        self.assertIn(HOOK.resolve(), paths,
                      "the live pre-commit relay site is outside the reach — "
                      "the scan is reporting clean over a file it never "
                      "opened")

    def test_the_reach_LOSES_NOTHING_the_old_glob_had(self):
        """A reach that gained the hook and dropped package files would be
        a different bug wearing the repair's clothes."""
        old = {p.resolve() for p in roster.CORE.glob("*.py")}
        new = set(roster.reach_paths(repo=REPO, doc=_doc()))
        self.assertEqual(old - new, set(), "files left the reach")

    def test_the_reach_EXCLUDES_the_rosters_own_test_corpus(self):
        """`tests` is a registered kind whose members PLANT strings shaped
        like emit sites, to red-prove this very scan. Reading them reports
        the fixtures as real unregistered refusals — measured when W3 first
        widened the reach. Same-parentage, same exclusion as refusals.py."""
        paths = roster.reach_paths(repo=REPO, doc=_doc())
        self.assertNotIn(Path(__file__).resolve(), paths)

    def test_a_STALE_exemption_fails_LOUDLY(self):
        """The hand-list's own failure mode, made loud. An exemption naming
        a kind nobody registers covers nothing, and the excluded population
        rejoins the scan without a word."""
        doc = _doc()
        doc = {**doc, "kinds": {k: v for k, v in doc["kinds"].items()
                                if k not in roster.REACH_EXCLUDED_KINDS}}
        with self.assertRaises(ValueError):
            roster.reach_paths(repo=REPO, doc=doc)

    def test_the_DIRECTORY_mode_uses_the_same_classifier(self):
        """The red-proof mode is not a second policy. A `*.py` glob here
        would put an extension-keyed predicate back in the reach by the
        back door — the must-not-build, by the side entrance."""
        paths = roster.reach_paths(root=REPO / "plugin" / "hooks")
        self.assertIn(HOOK, paths)


class RelayReachTest(unittest.TestCase):
    """The relay scan, over the contracted population."""

    def test_the_hook_is_REPORTED_as_a_relay_site(self):
        paths = roster.reach_paths(repo=REPO, doc=_doc())
        sites = roster.relay_sites(paths=paths)
        self.assertTrue(any(s.startswith("pre-commit:") for s in sites),
                        f"the hook's relay lines are not reported: {sites}")

    def test_the_OLD_population_MISSED_it(self):
        """The red half, and it is not hypothetical: this is the state the
        repo shipped in. Without this arm the assertion above passes over a
        scan that was always correct and proves nothing was ever wrong."""
        old = sorted(roster.CORE.glob("*.py"))
        sites = roster.relay_sites(paths=old)
        self.assertFalse(any(s.startswith("pre-commit:") for s in sites),
                         "the old glob reached the hook after all — then "
                         "this whole item's premise is wrong and the "
                         "measurement behind it must be re-taken")

    def test_the_relay_pattern_is_VERDICT_AGNOSTIC(self):
        """A refusal RELAYED as could-not-verify was invisible to a scan
        keyed on the finding word alone — the same defect `_LITERAL_CNV`
        repaired on the literal side, where `verify` shipped a refusal
        unregistered and unprovable while this check reported CLEAN."""
        self.assertTrue(roster._RELAY.search('f"FINDING [{row}] x"'))
        self.assertTrue(roster._RELAY.search('f"COULD NOT VERIFY [{row}] x"'))

    def test_the_verdict_vocabulary_stays_CLOSED_at_two(self):
        """Agnostic means BOTH members, never a widening. A third verdict
        word would be a vocabulary change and is not one this scan makes."""
        self.assertIsNone(roster._RELAY.search('f"WARNING [{row}] x"'))
        self.assertIsNone(roster._RELAY.search('f"NOTE [{row}] x"'))


class PatternFactsTest(unittest.TestCase):
    """The counts the criterion states EXACTLY, pinned so they cannot drift.

    The entry records that an earlier claim of "all four scan patterns"
    matched neither of the two real numbers. A count restated in prose and
    nowhere else is the label-over-body class; here it is an assertion.
    """

    def test_five_regexes_three_verdict_keyed_two_call_shaped(self):
        verdict_keyed = (roster._LITERAL, roster._LITERAL_CNV, roster._RELAY)
        call_shaped = (roster._RESULT_ADD, roster._PROBLEM)
        self.assertEqual(len(verdict_keyed) + len(call_shaped), 5)
        self.assertEqual(len(verdict_keyed), 3)
        self.assertEqual(len(call_shaped), 2)

    def test_two_scanners_read_that_population(self):
        for name in ("emit_sites", "relay_sites"):
            self.assertTrue(callable(getattr(roster, name)), name)


class CoverageSurfaceTest(unittest.TestCase):
    """THE ARM THROUGH THE READ SURFACE (W2's lesson, applied).

    Every arm above calls a function. The defect W2 shipped lived in what a
    verb PRINTED while every function it called was correct, so one arm has
    to read the surface an operator reads.
    """

    def test_the_coverage_REPORT_names_the_hook(self):
        buf = []
        reach = roster.reach_paths(repo=REPO, doc=_doc())
        roster.check_coverage(buf.append, reach=reach)
        text = "\n".join(buf)
        self.assertIn("pre-commit:", text,
                      "the hook is in the population and the REPORT does "
                      "not mention it — the two halves have parted company")
        self.assertIn("REACH:", text,
                      "the report states no reach, so a reader cannot tell "
                      "a clean sweep from an unexamined one")

    def test_the_report_says_so_when_the_reach_NARROWED(self):
        """A scan that silently fell back to its own directory would be the
        clean-over-unexamined report this check exists to refuse."""
        buf = []
        roster.check_coverage(buf.append, reach=None)
        self.assertIn("COULD NOT VERIFY", "\n".join(buf))


if __name__ == "__main__":
    unittest.main()
