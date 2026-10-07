"""The cli verdict printers say what they examined (lc-107, lc-108).

lc-107: `audit` and `retire` discarded the declaration's own Result whenever
the declaration was READABLE, so a declaration-level finding left a verb
reporting clean. lc-108: `kind check`'s CLEAN line did not say how many git
hooks it checked, so an empty guarded set read byte-identically to a checked
one. Both arms drive the real CLI over a real git repo built here.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "plugin" / "cli"))

from lifecycle_core import exits, ledger as ledger_mod, refusals  # noqa: E402

CLI = str(REPO_ROOT / "plugin" / "cli" / "lifecycle")
HOOK_BODY = "#!/bin/sh\nexit 0\n"


class _Repo:
    def __init__(self, commit=True):
        self.dir = Path(tempfile.mkdtemp(prefix="lc107-"))
        self.git("init", "-q", "-b", "main")
        self.git("config", "core.hooksPath", str(self.dir / ".nohooks"))
        self.git("config", "user.email", "walk@lifecycle.invalid")
        self.git("config", "user.name", "lc107 fixture")
        (self.dir / ".claude").mkdir()
        (self.dir / ".claude" / "lifecycle.json").write_text(
            json.dumps(refusals.GOOD_DECLARATION, indent=2), encoding="utf-8")
        (self.dir / "ITEMS.md").write_text(refusals.EMPTY_ITEMS,
                                           encoding="utf-8")
        (self.dir / "ITEMS-DONE.md").write_text(refusals.EMPTY_DONE,
                                                encoding="utf-8")
        (self.dir / "LEDGER.md").write_text(ledger_mod.head_text(),
                                            encoding="utf-8")
        (self.dir / "LAWS.md").write_text("# laws\n\n1. A law. (J1)\n",
                                          encoding="utf-8")
        self._commit = commit

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=str(self.dir),
                              capture_output=True, text=True)

    def hook(self, mode):
        p = self.dir / "tools" / "git-hooks" / "pre-commit"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(HOOK_BODY, encoding="utf-8")
        p.chmod(mode)

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-qm", "fixture")

    def run(self, *verb):
        env = dict(os.environ)
        env["XDG_STATE_HOME"] = os.environ.get("XDG_STATE_HOME", "")
        p = subprocess.run([sys.executable, CLI, "--repo", str(self.dir),
                            *verb], capture_output=True, text=True, env=env)
        return p.returncode, p.stdout + p.stderr

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        shutil.rmtree(self.dir, ignore_errors=True)
        return False


class TestWalkVerbsSurfaceTheDeclaration(unittest.TestCase):
    """lc-107."""

    def _bad(self, r):
        r.hook(0o644)       # committed non-executable: a declaration-level finding
        r.commit()

    def test_kind_check_names_the_finding_in_the_fixture(self):
        # the arrangement, read back: the finding exists at the declaration
        with _Repo() as r:
            self._bad(r)
            code, text = r.run("kind", "check")
            self.assertIn("hook_not_executable", text)
            self.assertEqual(code, exits.FINDING, text)

    def test_audit_prints_the_declaration_finding_and_folds_its_code(self):
        with _Repo() as r:
            self._bad(r)
            code, text = r.run("audit")
            self.assertIn("hook_not_executable", text)
            self.assertIn(code, (exits.FINDING, exits.COULD_NOT_VERIFY), text)

    def test_retire_prints_the_declaration_finding_and_folds_its_code(self):
        with _Repo() as r:
            self._bad(r)
            code, text = r.run("retire")
            self.assertIn("hook_not_executable", text)
            self.assertIn(code, (exits.FINDING, exits.COULD_NOT_VERIFY), text)

    def test_clean_declaration_prints_no_declaration_finding(self):
        with _Repo() as r:
            r.hook(0o755)
            r.commit()
            _, text = r.run("audit")
            self.assertNotIn("hook_not_executable", text)
            self.assertNotIn("declaration check", text)


class TestKindCheckStatesTheHookCount(unittest.TestCase):
    """lc-108."""

    def test_empty_guarded_set_is_a_stated_zero_and_still_a_pass(self):
        with _Repo() as r:
            r.commit()
            code, text = r.run("kind", "check")
            self.assertIn("CLEAN", text)
            self.assertIn("0 shipped git hook(s) checked", text)
            self.assertEqual(code, exits.CLEAN, text)

    def test_one_hook_is_a_stated_one(self):
        with _Repo() as r:
            r.hook(0o755)
            r.commit()
            code, text = r.run("kind", "check")
            self.assertIn("1 shipped git hook(s) checked", text)
            self.assertEqual(code, exits.CLEAN, text)

    def test_unborn_head_has_its_own_wording(self):
        with _Repo() as r:
            code, text = r.run("kind", "check")
            self.assertIn("no commit yet", text)
            self.assertNotIn("0 shipped git hook(s) checked", text)


if __name__ == "__main__":
    unittest.main()
