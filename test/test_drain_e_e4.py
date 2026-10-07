"""Drain wave E, lane E4 — what a roster row declares, and what the prover
proves (lc-327, lc-326, lc-178, lc-328, lc-74).

One class per item, in the lane's order. Each class states the arrangement
its red was taken under, because a red whose arrangement nobody wrote down is
a red nobody can re-take.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "plugin" / "cli"))


def _export(dst: Path, *, git: bool) -> None:
    """This tree's TRACKED files, copied to `dst` from the working tree.

    From the working tree rather than from HEAD, so the arm grades the code
    under test and not the last commit. `git=True` makes the copy a real
    checkout with one commit; the machine's hooks are kept out of it, as
    `refusals._Scratch` keeps them out of every row's scratch repo.
    """
    listed = subprocess.run(["git", "-C", str(REPO), "ls-files"],
                            capture_output=True, text=True)
    assert listed.returncode == 0, listed.stderr
    for rel in filter(None, listed.stdout.split("\n")):
        src = REPO / rel
        if not src.is_file():
            continue
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst / rel)
    if git:
        for argv in (["init", "-q", "-b", "main"],
                     ["config", "core.hooksPath", str(dst / ".nohooks")],
                     ["config", "user.email", "row@lifecycle.invalid"],
                     ["config", "user.name", "lane e4"],
                     ["add", "-A"], ["commit", "-qm", "export"]):
            done = subprocess.run(["git", "-C", str(dst)] + argv,
                                  capture_output=True, text=True)
            assert done.returncode == 0, (argv, done.stderr)


#: The production reach and the coverage check over it, exactly as
#: `roster.cmd_test` assembles them — run in a child so the package imported
#: is the EXPORT's and the cwd is the child's own.
_COVERAGE_CHILD = (
    "import sys\n"
    "sys.path.insert(0, sys.argv[1])\n"
    "from lifecycle_core import roster, declaration as d\n"
    "res = d.read(roster.PACKAGE_REPO)\n"
    "reach = roster.reach_paths(repo=roster.PACKAGE_REPO,\n"
    "                           doc=res.declaration)\n"
    "buf = []\n"
    "code = roster.check_coverage(buf.append, reach=reach)\n"
    "print('REACH-COUNT', len(reach))\n"
    "print('CODE', code)\n"
    "print('\\n'.join(buf))\n"
)

_ONLY_THERE = "lane_e4_only_in_the_other_checkout"


class TheRosterReadsTheTreeItWasLaunchedFrom(unittest.TestCase):
    """lc-327: `--test` graded whatever checkout the process stood in.

    THE ARRANGEMENT IS THE ITEM'S OWN: this tree exported to a scratch
    directory, and the export's coverage pass run with the cwd inside a
    checkout that DIFFERS from it — the other checkout carries one emit site
    the export does not. Both sides of the pair come from one fixture: the
    same child, the same export, the cwd alone moved.

    THE THIRD CWD IS THE SILENT ONE. Standing in no checkout at all the reach
    came back EMPTY and the check printed CLEAN over zero files — a clean
    board over a population nothing opened. It is asserted beside the loud
    case because it is the direction nobody would have reported.
    """

    def _fixture(self, *, git: bool):
        export = Path(tempfile.mkdtemp(prefix="lane-e4-export-"))
        other = Path(tempfile.mkdtemp(prefix="lane-e4-other-"))
        nowhere = Path(tempfile.mkdtemp(prefix="lane-e4-nowhere-"))
        for d in (export, other, nowhere):
            self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        _export(export, git=git)
        _export(other, git=True)
        target = other / "plugin" / "cli" / "lifecycle_core" / "exits.py"
        target.write_text(
            target.read_text(encoding="utf-8")
            + "\n\ndef _planted(out):\n"
              f'    out("FINDING [{_ONLY_THERE}] planted")\n',
            encoding="utf-8")
        return export, other, nowhere

    def _coverage(self, export: Path, cwd: Path):
        done = subprocess.run(
            [sys.executable, "-c", _COVERAGE_CHILD,
             str(export / "plugin" / "cli")],
            cwd=str(cwd), capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr[-2000:])
        lines = done.stdout.split("\n")
        count = int(lines[0].split()[1])
        code = int(lines[1].split()[1])
        return count, code, done.stdout

    def _assert_cwd_is_not_an_input(self, *, git: bool):
        export, other, nowhere = self._fixture(git=git)
        home_count, home_code, home_out = self._coverage(export, export)
        self.assertGreater(
            home_count, 0,
            "the export's own reach is empty, so this arm has no reference "
            f"to compare the moved-cwd runs with:\n{home_out}")
        self.assertEqual(home_code, 0, home_out)

        count, code, out = self._coverage(export, other)
        self.assertNotIn(
            _ONLY_THERE, out,
            "the export's coverage pass reported an emit site that exists "
            "only in the checkout the process was STANDING in — it read "
            f"that tree's files, not its own:\n{out}")
        self.assertEqual((count, code), (home_count, home_code), out)

        count, code, out = self._coverage(export, nowhere)
        self.assertEqual(
            count, home_count,
            "standing in no checkout at all, the reach collapsed — and the "
            "check then reports CLEAN over files it never opened:\n" + out)
        self.assertEqual(code, home_code, out)

    def test_an_exported_tree_reads_its_own_files_from_another_checkout(self):
        self._assert_cwd_is_not_an_input(git=False)

    def test_the_same_holds_when_the_export_is_itself_a_git_checkout(self):
        """The item's own question: was a non-git export the whole cause?
        It was not — the defect is a repo-relative path resolved against the
        cwd, and git never enters it."""
        self._assert_cwd_is_not_an_input(git=True)


if __name__ == "__main__":
    unittest.main()
