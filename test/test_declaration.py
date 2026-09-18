"""The repository declaration's registered homes stay sweep-complete."""

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DeclaredHomesSweep(unittest.TestCase):
    def test_declared_homes_keep_sweep_clean_and_claim_future_directives(self):
        """This pins the outcome, not today's number of directive files."""
        declaration = json.loads(
            (ROOT / ".claude" / "lifecycle.json").read_text(encoding="utf-8")
        )
        kinds = declaration["kinds"]

        self.assertEqual(kinds["directives"]["home"], "docs/directives/*.md")
        self.assertEqual(kinds["workflow definitions"]["home"],
                         "plugin/workflows")
        self.assertEqual(
            set(kinds["directives"]),
            {"home", "writer", "reader", "staleness", "exit", "growth"},
        )
        self.assertEqual(
            set(kinds["workflow definitions"]),
            {"home", "writer", "reader", "staleness", "exit", "growth"},
        )

        run = subprocess.run(
            ["python3", "plugin/cli/lifecycle", "kind", "sweep"],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("kind sweep: CLEAN", run.stdout)
        self.assertNotIn("plugin/skills/.gitkeep", run.stdout)


if __name__ == "__main__":
    unittest.main()


class InvestigationRecordsAreARegisteredKind(unittest.TestCase):
    """lc-166 — invariant 1 reaching a home the tracked-file sweep cannot see.

    `kind sweep` walks TRACKED files, and the investigation record lives in
    XDG state outside every repo on purpose: no repo dirtied, no permission
    dialog from the `.claude`-shape protection, and it survives across
    branches. That design is right, and its consequence is that the sweep
    structurally cannot reach these files — so a shipped verb
    (`lifecycle record check`) was grading a kind no declaration governed.
    """

    def _check(self, tmp, *, declare, write_record=True):
        """`declaration.check` over a scratch repo, records home redirected."""
        import os
        import sys
        sys.path.insert(0, str(ROOT / "plugin" / "cli"))
        from lifecycle_core import declaration as decl

        repo = tmp / "repo"
        repo.mkdir(parents=True, exist_ok=True)
        doc = {"kinds": {}}
        if declare:
            doc["kinds"]["investigation records"] = {
                "home": "$XDG_STATE_HOME/claude/investigations/repo--*.md",
                "writer": "session", "reader": ["session"],
                "staleness": "change-coupling", "exit": {"action": "never"},
                "growth": "unbounded-with-reason",
            }
        if write_record:
            home = tmp / "state" / "claude" / "investigations"
            home.mkdir(parents=True, exist_ok=True)
            (home / f"{repo.name}--arc.md").write_text("# r\n", encoding="utf-8")

        res = decl.Result(decl.exits.CLEAN)
        old = os.environ.get("XDG_STATE_HOME")
        os.environ["XDG_STATE_HOME"] = str(tmp / "state")
        try:
            decl.check_records_kind_declared(repo, doc, res)
        finally:
            if old is None:
                os.environ.pop("XDG_STATE_HOME", None)
            else:
                os.environ["XDG_STATE_HOME"] = old
        return [f.row for f in res.findings]

    def _tmp(self):
        import shutil
        import tempfile
        d = Path(tempfile.mkdtemp(prefix="lc166-"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def test_records_without_a_kind_are_a_finding(self):
        self.assertIn("records_kind_undeclared", self._check(self._tmp(),
                                                             declare=False))

    def test_the_same_records_with_the_kind_declared_are_clean(self):
        """The pair: same records present, the DECLARATION is what differs."""
        self.assertEqual(self._check(self._tmp(), declare=True), [])

    def test_a_repo_with_no_records_is_silent(self):
        """The over-fire arm. A repo that never opened an investigation owes
        no kind, and a check firing there would land on every repo in the
        roster — a guard on legitimate work, which stops the lane."""
        self.assertEqual(
            self._check(self._tmp(), declare=False, write_record=False), [])

    def test_this_repo_declares_it_with_all_six_stages(self):
        declaration = json.loads(
            (ROOT / ".claude" / "lifecycle.json").read_text(encoding="utf-8"))
        kind = declaration["kinds"]["investigation records"]
        self.assertEqual(sorted(kind),
                         ["exit", "growth", "home", "reader", "staleness",
                          "writer"])
        self.assertIn("claude/investigations", kind["home"])
        # THE FILES NEVER MOVE INTO ANY TREE — the exit is graduation of the
        # record's CONTENT, and a `move` here would undo the three benefits
        # the home exists for.
        self.assertEqual(kind["exit"]["action"], "never")
