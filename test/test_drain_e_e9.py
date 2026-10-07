"""Drain wave E, lane E9: lc-23 (init seeds the carriers), lc-225 (the
round series), lc-41 (commit-or-say), lc-194 (a shell answers for the last
process only)."""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import argparse
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "plugin" / "cli"))

from lifecycle_core import cli, exits  # noqa: E402
from lifecycle_core import declaration as decl  # noqa: E402
from lifecycle_core import workflows as workflows_mod  # noqa: E402

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


# --- lc-41: every carrier-writing verb commits its write or says NOT COMMITTED

def _leaf_verbs(parser, prefix=()):
    """Every leaf verb path of the RUNNING parser, e.g. ('item', 'add').

    Derived from the argparse object `cli.build_parser()` returns, never
    restated, so a verb added later is a new member of this set by
    construction."""
    subs = [a for a in parser._actions
            if isinstance(a, argparse._SubParsersAction)]
    if not subs:
        return [prefix]
    out = []
    for action in subs:
        for name, sub in action.choices.items():
            out += _leaf_verbs(sub, prefix + (name,))
    return out


#: Verbs that write NO declared carrier by construction (they read, or they
#: write only the fire log). A verb absent from this set AND from the tables
#: below is UNCLASSIFIED and fails the enumeration test.
READ_ONLY = {
    ("kind", "list"), ("kind", "check"), ("kind", "sweep"), ("kind", "show"),
    ("kind", "read"), ("kind", "moments"),
    ("item", "check"), ("item", "slots"), ("item", "ready"),
    ("item", "waves"), ("item", "ratio"), ("item", "statusline"),
    ("ledger", "check"), ("lane", "list"), ("lane", "population"),
    ("retire",), ("audit",), ("verify",), ("record", "check"),
    ("arc", "status"),
}

#: Verbs that commit through `verbs.commit_paths`, which commits by pathspec
#: or says NOT COMMITTED (--no-commit) or FINDS [move_uncommitted]: the item,
#: ledger and arc families, graded by their own suites.
COMMITS_VIA_COMMIT_PATHS = {
    ("item", "add"), ("item", "amend"), ("item", "promote"),
    ("item", "bench"), ("item", "park"), ("item", "close"),
    ("item", "compact"), ("item", "supersede-closure"),
    ("item", "repair"),
    ("ledger", "add", "superseded"), ("ledger", "add", "rejected"),
    ("ledger", "add", "dropped"), ("ledger", "add", "decision"),
    ("ledger", "rejected"),
    ("arc", "open"), ("arc", "close"), ("arc", "deadline"),
    ("arc", "premise"), ("arc", "belief"), ("arc", "reopen"),
    ("arc", "disposition"), ("arc", "advance"), ("arc", "narrow"),
    ("arc", "verdict"), ("arc", "yield"),
}

#: The verbs this lane's commit-or-say line (lc-41) lives in, probed below.
SAYS_NOT_COMMITTED = {
    ("init",), ("lane", "new"), ("workflow", "bind"), ("desk", "state"),
}

#: Writes that are NOT claimed here, each with the reason: the migrator's
#: carrier writes sit in migrate.py / cli.py, outside this lane's write set
#: (reported as a GAP), and `lane register` writes the machine-wide roster,
#: which no repo declaration names as a kind.
UNCLAIMED = {
    ("migrate",): "migrate.py writes carriers and commits nothing: GAP for "
                  "the lane holding migrate.py",
    ("lane", "register"): "machine-wide roster, not a declared repo carrier",
}


class Lc41EnumerationFromTheRunningParser(unittest.TestCase):

    def test_every_leaf_verb_of_the_running_parser_is_classified(self):
        leaves = set(_leaf_verbs(cli.build_parser()))
        self.assertTrue(len(leaves) > 30, leaves)  # the walk saw the parser
        known = (READ_ONLY | COMMITS_VIA_COMMIT_PATHS | SAYS_NOT_COMMITTED
                 | set(UNCLAIMED))
        unclassified = sorted(leaves - known)
        self.assertEqual(
            unclassified, [],
            "a verb the parser carries is in no class: decide whether it "
            "writes a declared carrier and, if so, that it commits or says "
            "NOT COMMITTED")
        stale = sorted(known - leaves)
        self.assertEqual(stale, [], "a classified verb the parser no longer "
                                    "carries")


class _Bare:
    def __init__(self):
        self.repo = ScratchGitRepo()
        self.repo.write("CLAUDE.md", "# laws\n")
        self.repo.commit_as("op@example.invalid")
        self.dir = self.repo.dir

    def tree(self):
        return subprocess.run(
            ["git", "-C", str(self.dir), "status", "--porcelain"],
            capture_output=True, text=True).stdout.strip()

    def commit_all(self):
        self.repo.commit_as("op@example.invalid", message="step")

    def close(self):
        self.repo.close()


class Lc41CommitOrSay(unittest.TestCase):
    """A verb that writes into the tree either leaves the tree clean (it
    committed) or says NOT COMMITTED. The silent state — dirty tree, no such
    line — is the defect."""

    def setUp(self):
        self.b = _Bare()
        self.addCleanup(self.b.close)
        self.state = tempfile.mkdtemp(prefix="lane-e9-state-")
        self._old = os.environ.get("XDG_STATE_HOME")
        os.environ["XDG_STATE_HOME"] = self.state
        self.addCleanup(self._restore)

    def _restore(self):
        if self._old is None:
            os.environ.pop("XDG_STATE_HOME", None)
        else:
            os.environ["XDG_STATE_HOME"] = self._old

    def _assert_commit_or_say(self, out):
        dirty = self.b.tree()
        if dirty:
            self.assertIn("NOT COMMITTED", out,
                          f"the tree is dirty and the verb said nothing:\n"
                          f"{dirty}\n{out}")

    def test_init_says_not_committed(self):
        code, out = _run(["--repo", str(self.b.dir), "init"])
        self.assertTrue(self.b.tree(), "init wrote nothing into the tree")
        self._assert_commit_or_say(out)

    def test_lane_new_says_not_committed(self):
        _run(["--repo", str(self.b.dir), "init"])
        self.b.commit_all()
        code, out = _run(["--repo", str(self.b.dir), "lane", "new", "door1"])
        self.assertTrue(self.b.tree(), "lane new wrote nothing")
        self._assert_commit_or_say(out)

    def test_workflow_bind_says_not_committed(self):
        _run(["--repo", str(self.b.dir), "init"])
        self.b.commit_all()
        reg = Path(tempfile.mkdtemp(prefix="lane-e9-reg-"))
        (reg / "t1.md").write_text("Slots: a, b\n\nprocedure\n",
                                   encoding="utf-8")
        orig = workflows_mod.registry_dir
        workflows_mod.registry_dir = lambda: reg
        self.addCleanup(setattr, workflows_mod, "registry_dir", orig)
        code, out = _run(["--repo", str(self.b.dir), "workflow", "bind", "t1"])
        self.assertEqual(code, exits.CLEAN, out)
        self.assertTrue(self.b.tree(), "workflow bind wrote nothing")
        self._assert_commit_or_say(out)

    def test_desk_state_says_not_committed_though_it_writes_outside_the_repo(self):
        code, out = _run(["--repo", str(self.b.dir), "desk", "state",
                          "REPORTED", "done", "--desk", "probe-desk"])
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("NOT COMMITTED", out)
        self.assertIn("outside every repo", out)

    def test_a_read_only_verb_is_not_made_to_say_it(self):
        """The control: a read-only verb prints no NOT COMMITTED line."""
        _run(["--repo", str(self.b.dir), "init"])
        self.b.commit_all()
        code, out = _run(["--repo", str(self.b.dir), "kind", "check"])
        self.assertNotIn("NOT COMMITTED", out)


if __name__ == "__main__":
    unittest.main()
