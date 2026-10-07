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


if __name__ == "__main__":
    unittest.main()
