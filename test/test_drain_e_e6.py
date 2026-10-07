"""Drain wave E, lane E6 — the audit walk and the sweep (2026-10-07).

ONE FILE FOR THE LANE (wave B change 4). Every fixture is a real git work
tree in a temp directory: each item here turns on something git or the
filesystem says — a carrier retired by the real `migrate --retire-source`, a
worktree registered by the real `git worktree add`, a file tracked by the
real index.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, exits, retire  # noqa: E402
from lifecycle_core.refusals import GOOD_FULL_DECLARATION  # noqa: E402


def git(repo: Path, *argv):
    return subprocess.run(["git", "-C", str(repo)] + list(argv),
                          capture_output=True, text=True)


def commit_all(repo: Path, message: str) -> None:
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", message)


def build(files: dict, declaration: dict | None = None) -> Path:
    """A committed fixture repo carrying the full good declaration."""
    d = Path(tempfile.mkdtemp(prefix="lifecycle-e6-"))
    git(d, "init", "-q", "-b", "main")
    git(d, "config", "core.hooksPath", str(d / ".nohooks"))
    git(d, "config", "user.email", "e6@lifecycle.invalid")
    git(d, "config", "user.name", "e6 test")
    (d / ".claude").mkdir()
    (d / ".claude" / "lifecycle.json").write_text(
        json.dumps(GOOD_FULL_DECLARATION if declaration is None
                   else declaration), encoding="utf-8")
    for rel, text in files.items():
        path = d / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    commit_all(d, "seed")
    return d


def run_cli(repo: Path, *argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(["--repo", str(repo)] + list(argv))
    return code, buf.getvalue()


def captured(fn, *args):
    lines = []
    code = fn(*args, lines.append)
    return code, "\n".join(lines)


# --- lc-99 --------------------------------------------------------------------

OLD_CARRIER = ("# BACKLOG\n\n## Open\n\n"
               "- **READY 2026-08-03 — real open work.** body\n")
OLD_DONE = "# old done\n\n## Done\n\n- **DONE 2026-01-01 — c.** b\n"


def retired_repo() -> Path:
    """A repo whose old carrier the REAL `migrate --retire-source` deleted,
    so the laws file holds the record as that verb writes it and not as this
    file imagines it."""
    d = build({"LAWS.md": "law\n", "LEDGER.md": "schema: 2\n",
               "BACKLOG.md": OLD_CARRIER, "BACKLOG-DONE.md": OLD_DONE})
    code, out = run_cli(d, "migrate", "--report", "docs/audits/report.md",
                        "--retire-source")
    assert code == exits.CLEAN, out
    assert not (d / "BACKLOG.md").exists(), out
    return d


def laws_scope(repo: Path):
    return captured(lambda out: retire.laws_scope_audit(repo, "LAWS.md", out))


class ARetiredCarriersDeletionRecordIsNotALawsScopeFinding(unittest.TestCase):
    """lc-99 — sanctioned output that fires a check forever trains the
    discount reflex: every repo that retired a carrier carried a
    `laws_scope_audit` finding it could not clear (LEDGER.md:78, reading 1)."""

    def setUp(self):
        self.d = retired_repo()
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        self.laws = self.d / "LAWS.md"

    def test_the_fixture_really_holds_the_record(self):
        """The premise, pinned: a CLEAN below over a laws file with no record
        in it would be a pass about nothing."""
        self.assertEqual(
            self.laws.read_text(encoding="utf-8").count("## Deletion record"),
            1)

    def test_the_laws_scope_is_CLEAN_and_says_what_it_passed(self):
        code, out = laws_scope(self.d)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("[laws_scope_audit]", out)
        self.assertIn("scope: CLEAN", out)
        self.assertIn("deletion record", out)

    def test_the_audit_verb_reads_CLEAN_on_the_laws_scope(self):
        """Through `cli.main`, the verb a session actually runs."""
        _code, out = run_cli(self.d, "audit")
        self.assertIn("LAWS SCOPE AUDIT", out)
        self.assertIn("scope: CLEAN", out)
        self.assertNotIn("[laws_scope_audit]", out)

    def test_an_ordinary_measured_figure_line_STILL_fires(self):
        """THE CONTROL: the same laws file, one measured line added."""
        self.laws.write_text(
            self.laws.read_text(encoding="utf-8")
            + "\nThe walk covered 41 files on the last pass.\n",
            encoding="utf-8")
        code, out = laws_scope(self.d)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[laws_scope_audit] 1 line(s)", out)
        self.assertIn("41 files", out)

    def test_a_numbered_step_line_STILL_fires(self):
        self.laws.write_text(
            self.laws.read_text(encoding="utf-8")
            + "\n1. run the migration\n", encoding="utf-8")
        code, out = laws_scope(self.d)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[laws_scope_audit] 1 line(s)", out)

    def test_a_record_somebody_EDITED_is_not_the_writers_record(self):
        """The pass is for the shape the WRITER writes, compared whole. A
        block that only opens like one — the heading kept, a line of the body
        rewritten — is prose in the laws file and is graded as prose."""
        text = self.laws.read_text(encoding="utf-8")
        self.assertIn("Nothing is lost", text)
        self.laws.write_text(text.replace("Nothing is lost", "Little is lost"),
                             encoding="utf-8")
        code, out = laws_scope(self.d)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[laws_scope_audit]", out)

    def test_a_bare_heading_that_only_NAMES_a_deletion_record_fires(self):
        """A prefix is not the record: the dated heading alone, with no body
        under it, is a dated line like any other."""
        d = build({"LAWS.md": "law\n\n## Deletion record — BACKLOG.md "
                              "(2026-09-13)\n\nsome prose\n",
                   "LEDGER.md": "schema: 2\n"})
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = laws_scope(d)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[laws_scope_audit] 1 line(s)", out)


# --- lc-201 -------------------------------------------------------------------

def swept_repo() -> Path:
    """A repo whose every tracked file a registered home claims, so the
    tracked-file verdict is CLEAN and anything else in the output is about
    the worktrees."""
    return build({"LAWS.md": "law\n", "LEDGER.md": "schema: 2\n"})


def add_worktree(test, repo: Path, *flags) -> Path:
    """A worktree registered by the real `git worktree add`, OUTSIDE the
    repo's own tree. Returns its path as git prints it."""
    holder = Path(tempfile.mkdtemp(prefix="lifecycle-e6-wt-"))
    test.addCleanup(shutil.rmtree, holder, ignore_errors=True)
    wt = holder / "frozen-reader"
    p = git(repo, "worktree", "add", "-q", *flags, str(wt))
    assert p.returncode == 0, p.stderr
    return wt.resolve()


class TheSweepNamesTheWorktreeRegistrationsItCannotReach(unittest.TestCase):
    """lc-201 — a registration lives in `.git/worktrees/`, which a sweep over
    `git ls-files` never walks. It stops being invisible; it does not stop
    existing."""

    def setUp(self):
        self.d = swept_repo()
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)

    def test_a_registered_worktree_is_NAMED(self):
        wt = add_worktree(self, self.d, "--detach")
        code, out = run_cli(self.d, "kind", "sweep")
        self.assertIn("git worktree registrations: 1", out)
        self.assertIn(str(wt), out)
        self.assertIn("detached", out)
        # MUST-NOT-MOVE (lc-76): the tracked-file verdict and the exit code.
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("sweep: CLEAN — all 2 tracked file(s)", out)

    def test_with_NONE_registered_the_sweep_SAYS_so(self):
        """Not clean by silence: the list was read, and the line says it."""
        code, out = run_cli(self.d, "kind", "sweep")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("git worktree registrations: 0", out)
        self.assertIn("WAS read", out)

    def test_a_branch_and_a_lock_are_shown_as_git_reports_them(self):
        wt = add_worktree(self, self.d, "-b", "side")
        self.assertEqual(
            git(self.d, "worktree", "lock", "--reason", "held", str(wt)
                ).returncode, 0)
        _code, out = run_cli(self.d, "kind", "sweep")
        line = next(ln for ln in out.split("\n") if str(wt) in ln)
        self.assertIn("refs/heads/side", line)
        self.assertIn("locked", line)

    def test_a_sweep_run_FROM_a_registered_worktree_marks_its_own(self):
        wt = add_worktree(self, self.d, "--detach")
        _code, out = run_cli(wt, "kind", "sweep")
        line = next(ln for ln in out.split("\n") if str(wt) in ln)
        self.assertIn("this checkout", line)

    def test_NOTHING_is_removed_or_pruned(self):
        """MUST-NOT-BUILD. What a party is standing in is not moved."""
        wt = add_worktree(self, self.d, "--detach")
        before = git(self.d, "worktree", "list", "--porcelain").stdout
        run_cli(self.d, "kind", "sweep")
        self.assertEqual(
            git(self.d, "worktree", "list", "--porcelain").stdout, before)
        self.assertTrue(wt.is_dir())

    def test_a_stray_still_fires_with_its_text_beside_a_worktree(self):
        add_worktree(self, self.d, "--detach")
        (self.d / "TRACKING.md").write_text("stray\n", encoding="utf-8")
        commit_all(self.d, "a stray")
        code, out = run_cli(self.d, "kind", "sweep")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [unregistered_persisted_thing] 1 tracked "
                      "file(s) resolve to no registered kind:", out)
        self.assertIn("git worktree registrations: 1", out)

    def test_an_unreadable_worktree_list_is_COULD_NOT_VERIFY(self):
        """THREE ANSWERS: a list git would not give is not a list of none."""
        real = retire._git

        def failing(repo, *argv):
            if argv[:1] == ("worktree",):
                return 128, "fatal: planted"
            return real(repo, *argv)
        retire._git = failing
        self.addCleanup(setattr, retire, "_git", real)
        code, out = run_cli(self.d, "kind", "sweep")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertNotIn("git worktree registrations: 0", out)
        self.assertIn("fatal: planted", out)


class TheWorktreeListIsParsedAsGitWritesIt(unittest.TestCase):
    def test_the_main_checkout_is_not_a_registration(self):
        text = ("worktree /a/main\nHEAD " + "1" * 40 + "\nbranch "
                "refs/heads/main\n\nworktree /b/side\nHEAD " + "2" * 40
                + "\ndetached\nprunable gitdir file points to non-existent "
                "location\n\n")
        regs = retire.parse_worktree_list(text)
        self.assertEqual([r["path"] for r in regs], ["/b/side"])
        self.assertEqual(regs[0]["head"], "2" * 40)
        self.assertTrue(regs[0]["detached"])
        self.assertIn("non-existent", regs[0]["prunable"])


if __name__ == "__main__":
    unittest.main()
