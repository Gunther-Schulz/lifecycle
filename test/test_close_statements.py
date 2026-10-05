"""`item close` demands two statements about the work the close ends.

Each refusal is asserted twice over: the finding name, and that NOTHING was
written — "refused" and "refused after writing" share an exit code.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits, ledger  # noqa: E402
from test_moves import build, run_cli  # noqa: E402


class CloseStatements(unittest.TestCase):

    def setUp(self):
        self.d = build()
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)

    def _snap(self):
        return ((self.d / "ITEMS.md").read_text(encoding="utf-8"),
                (self.d / "ITEMS-DONE.md").read_text(encoding="utf-8"))

    def _refused(self, *argv, finding):
        before = self._snap()
        code, out = run_cli(self.d, "item", "close", "xx-1", *argv)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn(f"[{finding}]", out)
        self.assertEqual(self._snap(), before, "written despite the refusal")
        return out

    def test_neither_statement_is_refused_with_the_verbatim_text(self):
        out = self._refused(finding="close_statement_missing")
        self.assertIn(
            "`item close` needs two statements about the work this close "
            "ends. --met \"<none | the item ids you booked, or the commits "
            "that fixed, whatever you met while working that was NOT this "
            "item>\" and --decided \"<none | LEDGER.md:<line> of each "
            "decision line written for a choice this work made>\". `none` "
            "is a valid statement.", out)

    def test_one_statement_alone_is_refused(self):
        self._refused("--met", "none", finding="close_statement_missing")
        self._refused("--decided", "none", finding="close_statement_missing")
        self._refused("--met", " ", "--decided", "none",
                      finding="close_statement_missing")

    def test_an_unresolvable_item_id_is_refused_and_named(self):
        out = self._refused("--met", "xx-99999", "--decided", "none",
                            finding="close_statement_unresolved")
        self.assertIn("xx-99999", out)

    def test_an_unresolvable_sha_is_refused_and_named(self):
        sha = "0123456789abcdef0123456789abcdef01234567"
        out = self._refused("--met", sha, "--decided", "none",
                            finding="close_statement_unresolved")
        self.assertIn(sha, out)

    def test_a_ledger_line_that_is_not_a_decision_is_refused(self):
        out = self._refused("--met", "none", "--decided", "LEDGER.md:1",
                            finding="close_statement_unresolved")
        self.assertIn("LEDGER.md:1", out)

    def test_a_ledger_line_past_the_end_is_refused(self):
        self._refused("--met", "none", "--decided", "LEDGER.md:999",
                      finding="close_statement_unresolved")

    def test_resolving_statements_close_and_land_after_closed_reason(self):
        ledger.append(self.d / "LEDGER.md", "decision",
                      {"question": "which shape", "answer": "this one"})
        lines = (self.d / "LEDGER.md").read_text(
            encoding="utf-8").splitlines()
        n = next(i for i, ln in enumerate(lines, 1)
                 if ln.startswith("decision:"))
        code, out = run_cli(
            self.d, "item", "close", "xx-1", "--reason", "built",
            "--ref", "HEAD", "--met", "xx-1,HEAD",
            "--decided", f"LEDGER.md:{n}")
        self.assertEqual(code, exits.CLEAN, out)
        done = (self.d / "ITEMS-DONE.md").read_text(
            encoding="utf-8").splitlines()
        slots = [ln.split(":", 1)[0] for ln in done
                 if ln.split(":", 1)[0] in (
                     "closed-reason", "closed-met", "closed-decided",
                     "closed-ref")]
        self.assertEqual(slots, ["closed-reason", "closed-met",
                                 "closed-decided", "closed-ref"])
        self.assertIn(f"closed-decided: LEDGER.md:{n}", done)
        code, out = run_cli(self.d, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)

    def test_none_passes_for_both(self):
        code, out = run_cli(self.d, "item", "close", "xx-1",
                            "--met", "none", "--decided", "none")
        self.assertEqual(code, exits.CLEAN, out)
        done = (self.d / "ITEMS-DONE.md").read_text(encoding="utf-8")
        self.assertIn("closed-met: none", done)
        self.assertIn("closed-decided: none", done)

    def test_an_id_of_another_repo_is_refused_with_the_cross_repo_sentence(self):
        """The declared prefix decides what an item id IS here (`xx`)."""
        out = self._refused("--met", "df-12", "--decided", "none",
                            finding="close_statement_unresolved")
        self.assertIn("df-12", out)
        self.assertIn("`xx-<n>`", out)
        self.assertIn("named in the `--reason` text instead", out)

    def test_a_token_that_is_neither_id_nor_commit_says_so(self):
        out = self._refused("--met", "no such thing", "--decided", "none",
                            finding="close_statement_unresolved")
        self.assertIn("neither an item id", out)
        self.assertNotIn("ANOTHER repo", out)

    def test_a_closed_item_of_this_repo_resolves(self):
        code, out = run_cli(self.d, "item", "close", "xx-1",
                            "--met", "none", "--decided", "none")
        self.assertEqual(code, exits.CLEAN, out)
        d2 = build()
        self.addCleanup(shutil.rmtree, d2, ignore_errors=True)
        code, out = run_cli(d2, "item", "close", "xx-1",
                            "--met", "xx-1", "--decided", "none")
        self.assertEqual(code, exits.CLEAN, out)

    def test_a_closed_body_without_the_statements_is_no_finding(self):
        """Bodies closed before this change are not findings for lacking
        the two lines: the slots are legal in the done home, never owed.
        The older shape is this close's own body minus the two lines."""
        code, out = run_cli(self.d, "item", "close", "xx-1", "--reason",
                            "built", "--met", "none", "--decided", "none")
        self.assertEqual(code, exits.CLEAN, out)
        done = self.d / "ITEMS-DONE.md"
        kept = [ln for ln in done.read_text(encoding="utf-8").split("\n")
                if not ln.startswith(("closed-met:", "closed-decided:"))]
        self.assertIn("closed-reason:", "\n".join(kept))
        done.write_text("\n".join(kept), encoding="utf-8")
        code, out = run_cli(self.d, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)


class TheLedgerReferenceIsTheDeclaredHome(unittest.TestCase):
    """`<the ledger home as the declaration gives it>:<line>` — a repo whose
    ledger lives elsewhere is taught, and held to, ITS spelling."""

    def setUp(self):
        self.d = build()
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)
        decl_path = self.d / ".claude" / "lifecycle.json"
        doc = json.loads(decl_path.read_text(encoding="utf-8"))
        doc["kinds"]["ledger lines"]["home"] = "docs/DECISIONS.md"
        decl_path.write_text(json.dumps(doc), encoding="utf-8")
        (self.d / "docs").mkdir()
        (self.d / "LEDGER.md").rename(self.d / "docs" / "DECISIONS.md")
        subprocess.run(["git", "add", "-A"], cwd=str(self.d),
                       capture_output=True)
        subprocess.run(["git", "commit", "-qm", "ledger moved"],
                       cwd=str(self.d), capture_output=True)
        ledger.append(self.d / "docs" / "DECISIONS.md", "decision",
                      {"question": "which shape", "answer": "this one"})
        lines = (self.d / "docs" / "DECISIONS.md").read_text(
            encoding="utf-8").splitlines()
        self.n = next(i for i, ln in enumerate(lines, 1)
                      if ln.startswith("decision:"))

    def test_the_refusal_text_names_the_declared_home(self):
        code, out = run_cli(self.d, "item", "close", "xx-1")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("docs/DECISIONS.md:<line>", out)
        self.assertNotIn("LEDGER.md", out)

    def test_the_declared_spelling_resolves_and_the_default_one_does_not(self):
        code, out = run_cli(self.d, "item", "close", "xx-1", "--met", "none",
                            "--decided", f"LEDGER.md:{self.n}")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[close_statement_unresolved]", out)
        code, out = run_cli(self.d, "item", "close", "xx-1", "--met", "none",
                            "--decided", f"docs/DECISIONS.md:{self.n}")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn(f"closed-decided: docs/DECISIONS.md:{self.n}",
                      (self.d / "ITEMS-DONE.md").read_text(encoding="utf-8"))


class CloseStatementsDrop(unittest.TestCase):

    def setUp(self):
        self.d = build()
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)

    def _snap(self):
        return ((self.d / "ITEMS.md").read_text(encoding="utf-8"),
                (self.d / "ITEMS-DONE.md").read_text(encoding="utf-8"))

    def test_a_drop_is_untouched(self):
        code, out = run_cli(self.d, "item", "close", "xx-1", "--drop",
                            "--reason", "overtaken")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("closed-met", self._snap()[1])


if __name__ == "__main__":
    unittest.main()
