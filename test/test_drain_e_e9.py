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


# --- lc-194: a shell answers for the last process only

from lifecycle_core import lanes as lanes_mod  # noqa: E402
from lifecycle_core import verify as verify_mod  # noqa: E402

_PLUGIN = Path(__file__).resolve().parent.parent / "plugin"


def _trigger(command):
    return lanes_mod.evaluate_trigger(command, cwd=Path(tempfile.gettempdir()))


def _verify(command):
    return verify_mod.run_one(command, Path(tempfile.gettempdir()), 20)


class Lc194TriggerPipelines(unittest.TestCase):
    """The ruling: only an EARLIER stage exiting 126 or 127 is BROKEN; any
    other non-zero earlier stage leaves the verdict as it is today."""

    def test_a_pipeline_whose_first_stage_does_not_exist_is_broken(self):
        t = _trigger("no_such_cmd_lc194 | grep -q .")
        self.assertEqual(t.state, lanes_mod.BROKEN, t)

    def test_a_first_stage_that_is_not_executable_is_broken(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "tool.sh"
            f.write_text("#!/bin/sh\necho x\n")
            f.chmod(0o644)
            t = lanes_mod.evaluate_trigger(f"{f} | grep -q .", cwd=Path(td))
            self.assertEqual(t.state, lanes_mod.BROKEN, t)

    def test_must_not_move_the_glob_idiom_stays_quiet(self):
        """`ls <glob> 2>/dev/null | grep -q .`: ls exits 2 when nothing
        matches and the pipeline is correctly QUIET (the reverted first
        build flipped a live predicate here)."""
        t = _trigger("ls /nonexistent_lc194_glob* 2>/dev/null | grep -q .")
        self.assertEqual(t.state, lanes_mod.QUIET, t)

    def test_must_not_move_a_working_pipeline_fires_and_stays_quiet(self):
        self.assertEqual(_trigger("echo x | grep -q x").state, lanes_mod.FIRE)
        self.assertEqual(_trigger("echo x | grep -q nope").state,
                         lanes_mod.QUIET)

    def test_must_not_move_a_reader_closing_the_pipe_early_fires(self):
        self.assertEqual(_trigger("yes | grep -q y").state, lanes_mod.FIRE)

    def test_must_not_move_bare_and_chained_spellings(self):
        self.assertEqual(_trigger("no_such_cmd_lc194").state, lanes_mod.BROKEN)
        self.assertEqual(_trigger("true && no_such_cmd_lc194").state,
                         lanes_mod.BROKEN)
        self.assertEqual(_trigger("exit 0").state, lanes_mod.FIRE)
        self.assertEqual(_trigger("exit 1").state, lanes_mod.QUIET)

    def test_a_quiet_answer_over_a_failed_earlier_stage_says_it_cannot_discriminate(self):
        t = _trigger("ls /nonexistent_lc194_glob* 2>/dev/null | grep -q .")
        self.assertIn("cannot discriminate", t.detail)

    def test_a_working_quiet_pipeline_carries_no_such_note(self):
        t = _trigger("echo x | grep -q nope")
        self.assertNotIn("cannot discriminate", t.detail)


class Lc194VerifyPipelines(unittest.TestCase):

    def test_a_pipeline_whose_first_stage_does_not_exist_did_not_run(self):
        verdict, code, detail = _verify("no_such_cmd_lc194 | cat")
        self.assertEqual(verdict, "did-not-run", (verdict, code, detail))

    def test_must_not_move_a_failing_earlier_stage_other_than_126_127(self):
        verdict, code, detail = _verify("ls /nonexistent_lc194_glob* 2>/dev/null | cat")
        self.assertEqual(verdict, "ran-clean", (verdict, code, detail))
        self.assertIn("cannot discriminate", detail)

    def test_must_not_move_a_working_pipeline_is_clean_without_a_note(self):
        verdict, code, detail = _verify("echo x | cat")
        self.assertEqual((verdict, code, detail), ("ran-clean", 0, ""))

    def test_must_not_move_bare_and_chained_spellings(self):
        self.assertEqual(_verify("no_such_cmd_lc194")[0], "did-not-run")
        self.assertEqual(_verify("true && no_such_cmd_lc194")[0],
                         "did-not-run")
        self.assertEqual(_verify("exit 3")[0], "could-not-verify")


class Lc194EnumerationOfShellVerdictSites(unittest.TestCase):
    """The enumeration is the deliverable: every site in plugin/ and tools/
    that takes a verdict through a shell, keyed on the invariant (a shell
    invocation: `shell=True`, or an argv naming a shell with `-c`), not on
    the idiom the two found sites share."""

    SHELL_ARGV = ("sh", "/bin/sh", "bash", "/bin/bash", "dash", "zsh")

    def _sites(self):
        import ast
        found = []
        for root in (_PLUGIN, _PLUGIN.parent / "tools"):
            for p in sorted(root.rglob("*.py")):
                try:
                    tree = ast.parse(p.read_text(encoding="utf-8"))
                except SyntaxError:
                    continue
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Call):
                        continue
                    shell_kw = any(k.arg == "shell"
                                   and isinstance(k.value, ast.Constant)
                                   and k.value.value is True
                                   for k in node.keywords)
                    shell_argv = (
                        node.args and isinstance(node.args[0], ast.List)
                        and node.args[0].elts
                        and isinstance(node.args[0].elts[0], ast.Constant)
                        and node.args[0].elts[0].value in self.SHELL_ARGV
                        and any(isinstance(e, ast.Constant) and e.value == "-c"
                                for e in node.args[0].elts))
                    if shell_kw or shell_argv:
                        found.append((str(p.relative_to(_PLUGIN.parent)),
                                      "shell=True" if shell_kw else "argv -c"))
        return found

    def test_the_only_shell_verdict_sites_are_the_declared_ones(self):
        sites = self._sites()
        files = sorted({f for f, _k in sites})
        # lanes.py: the ONE helper both verdict sites go through
        # (evaluate_trigger, verify.run_one). verbs.py: the booking-time
        # `/bin/sh -n -c` SYNTAX parse — `-n` executes nothing, so no exit
        # code of a last stage is taken as a verdict about a command.
        self.assertEqual(
            files, ["plugin/cli/lifecycle_core/lanes.py",
                    "plugin/cli/lifecycle_core/verbs.py"],
            f"a new shell verdict site appeared (or one vanished): {sites}")

    def test_verify_takes_its_shell_verdict_through_the_one_helper(self):
        src = (_PLUGIN / "cli" / "lifecycle_core" / "verify.py").read_text()
        self.assertNotIn("shell=True", src)
        self.assertIn("lanes.run_shell", src)

    def test_positive_control_the_walk_sees_a_known_site(self):
        self.assertTrue(any(f.endswith("verbs.py") and k == "argv -c"
                            for f, k in self._sites()))


if __name__ == "__main__":
    unittest.main()
