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
