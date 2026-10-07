"""Drain wave D, lane D1 — verbs that leave something behind.

lc-320: `arc advance` AND `arc close` RETIRED A DEADLINE LANE AND DID NOT
COMMIT IT. Retirement rewrites the declaration (the lane's row) and deletes
the lane body; both verbs then committed the arc paths alone, so a verb that
printed `committed:` and exited 0 left the tree dirty behind it. `arc
deadline` commits the declaration whole, so its own entry check had to leave
the declaration out — the leftover was this tool's own hand.

EVERY RED-FIRST ARM REACHES ONLY THROUGH NAMES THE OLD BUILD ALREADY HAD
(`cli.main`, `exits`, the roster's `_Repo`, git), so a red against the
unmodified code is an assertion FAILURE at the defect and never an import
error (law 4).
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import json
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, exits  # noqa: E402
from lifecycle_core import declaration as decl_mod  # noqa: E402
from lifecycle_core import lanes as lanes_mod  # noqa: E402
from lifecycle_core import refusals as R  # noqa: E402

#: The declaration as git and the verbs' messages spell it.
DECL = Path(decl_mod.DECLARATION_REL).as_posix()


def run(repo: Path, *argv):
    """`(code, output)` of one CLI run inside `repo`."""
    here = os.getcwd()
    buf = io.StringIO()
    try:
        os.chdir(str(repo))
        with redirect_stdout(buf):
            code = cli.main(["--repo", str(repo)] + list(argv))
    finally:
        os.chdir(here)
    return code, buf.getvalue()


def git(repo: Path, *argv) -> str:
    p = subprocess.run(["git", "-C", str(repo)] + list(argv),
                       capture_output=True, text=True)
    return p.stdout


def status(repo: Path) -> str:
    return git(repo, "status", "--porcelain")


class ArcVerbsCommitTheLaneTheyRetire(unittest.TestCase):
    """lc-320. Open, deadline, then the movement verb, then `git status`."""

    OPEN = ("arc", "open", "bplan", "--goal", "submit", "--narrowing", "none")
    DEADLINE = ("arc", "deadline", "bplan", "--date", "2026-12-01",
                "--what", "council decision due")
    NAME = "bplan-2026-12-01"

    def _repo(self) -> Path:
        r = R._Repo()
        self.addCleanup(r.close)
        return r.dir

    def _armed(self) -> Path:
        """A repo with one arc and one committed deadline lane, tree clean."""
        repo = self._repo()
        for argv in (self.OPEN, self.DEADLINE):
            code, outp = run(repo, *argv)
            self.assertEqual(code, exits.CLEAN, outp)
        self.assertEqual(status(repo), "", "the fixture itself is dirty")
        self.assertIn(self.NAME, self._lanes(repo))
        return repo

    def _lanes(self, repo: Path) -> list:
        doc = json.loads((repo / decl_mod.DECLARATION_REL)
                         .read_text(encoding="utf-8"))
        return doc.get("lanes") or []

    def _body(self, repo: Path) -> Path:
        return repo / lanes_mod.LANES_DIR / f"{self.NAME}.md"

    # --- the red-first arms ---------------------------------------------------

    def test_ADVANCE_leaves_a_clean_tree_behind_a_retired_lane(self):
        repo = self._armed()
        code, outp = run(repo, "arc", "advance", "bplan", "--to", "drafting",
                         "--reason", "moving on")
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertIn("retired 1 generated observer lane(s)", outp)
        self.assertEqual(
            status(repo), "",
            "`arc advance` reported success and left the tree dirty")
        # THE CHANGE ITSELF, not only the absence of a diff: the commit the
        # verb made is the one that carries the row and the body away.
        named = git(repo, "show", "--name-status", "--format=", "HEAD")
        self.assertIn(DECL, named)
        self.assertIn(f"{lanes_mod.LANES_DIR}/{self.NAME}.md", named)

    def test_CLOSE_leaves_a_clean_tree_behind_a_retired_lane(self):
        repo = self._armed()
        code, outp = run(repo, "arc", "close", "bplan")
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertEqual(
            status(repo), "",
            "`arc close` reported success and left the tree dirty")
        named = git(repo, "show", "--name-status", "--format=", "HEAD")
        self.assertIn(DECL, named)
        self.assertIn(f"{lanes_mod.LANES_DIR}/{self.NAME}.md", named)

    def test_ABANDON_leaves_a_clean_tree_behind_a_retired_lane(self):
        repo = self._armed()
        code, outp = run(repo, "arc", "close", "bplan", "--abandon",
                         "--reason", "the council withdrew the item")
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertEqual(status(repo), "")

    def test_the_ORDINARY_SEQUENCE_advance_then_deadline_still_works(self):
        """The sequence lc-318's first build refused, and the reason `arc
        deadline` left the declaration out of its entry check."""
        repo = self._armed()
        run(repo, "arc", "advance", "bplan", "--to", "drafting",
            "--reason", "moving on")
        code, outp = run(repo, "arc", "deadline", "bplan", "--date",
                         "2027-01-15", "--what", "window closes")
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertEqual(status(repo), "")

    def test_DEADLINE_grades_the_declaration_at_entry(self):
        """It commits the declaration whole, so a pending edit of it would
        ride out under `arcs: deadline`."""
        repo = self._repo()
        run(repo, *self.OPEN)
        decl = repo / decl_mod.DECLARATION_REL
        decl.write_text(decl.read_text(encoding="utf-8") + "\n",
                        encoding="utf-8")
        code, outp = run(repo, *self.DEADLINE)
        self.assertEqual(code, exits.FINDING, outp)
        self.assertIn("FINDING [carrier_dirty_at_entry]", outp)
        self.assertIn(DECL, outp)
        self.assertFalse(self._body(repo).exists(),
                         "refused, and the lane body was written anyway")
        self.assertEqual(self._lanes(repo), [])

    def test_ADVANCE_grades_what_its_retirement_will_commit(self):
        repo = self._armed()
        decl = repo / decl_mod.DECLARATION_REL
        decl.write_text(decl.read_text(encoding="utf-8") + "\n",
                        encoding="utf-8")
        code, outp = run(repo, "arc", "advance", "bplan", "--to", "drafting",
                         "--reason", "moving on")
        self.assertEqual(code, exits.FINDING, outp)
        self.assertIn("FINDING [carrier_dirty_at_entry]", outp)
        self.assertIn(self.NAME, self._lanes(repo),
                      "refused, and the row was removed anyway")
        self.assertTrue(self._body(repo).is_file(),
                        "refused, and the lane body was deleted anyway")

    def test_CLOSE_grades_what_its_retirement_will_commit(self):
        repo = self._armed()
        decl = repo / decl_mod.DECLARATION_REL
        decl.write_text(decl.read_text(encoding="utf-8") + "\n",
                        encoding="utf-8")
        code, outp = run(repo, "arc", "close", "bplan")
        self.assertEqual(code, exits.FINDING, outp)
        self.assertIn("FINDING [carrier_dirty_at_entry]", outp)
        self.assertIn(self.NAME, self._lanes(repo))
        self.assertTrue(self._body(repo).is_file())

    # --- the controls (pass before and after) ---------------------------------

    def test_CONTROL_an_advance_retiring_NOTHING_ignores_the_declaration(self):
        """The declaration is graded only where this verb's commit will name
        it. An advance with no lane to retire writes no row, so a pending
        declaration edit is not its business and must not stop it."""
        repo = self._repo()
        run(repo, *self.OPEN)
        decl = repo / decl_mod.DECLARATION_REL
        decl.write_text(decl.read_text(encoding="utf-8") + "\n",
                        encoding="utf-8")
        code, outp = run(repo, "arc", "advance", "bplan", "--to", "drafting",
                         "--reason", "moving on")
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertEqual(status(repo).split(),
                         ["M", DECL],
                         "the pending edit was committed or lost")

    def test_CONTROL_no_commit_says_NOT_COMMITTED_by_name(self):
        repo = self._armed()
        code, outp = run(repo, "arc", "advance", "bplan", "--to", "drafting",
                         "--reason", "moving on", "--no-commit")
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertIn("NOT COMMITTED (--no-commit): the arc advance", outp)
        self.assertNotEqual(status(repo), "")


# --- lc-322 -------------------------------------------------------------------
#
# AN `external` BLOCKER WAS THE ONE TYPE NO CLOSE SPOKE FOR. `move_to_done`
# clears the base `blocked-by:` LINE and an `amended-blocked-by:` line
# survives it, so an amended external blocker reached the closure home alive:
# the close exited 0 and the next `item check` reported `blocked_in_done_home`
# against a body no verb can repair. A base one was cleared with no record.

EVENT = "the vendor ships a fix"
HEAD = (f"schema: {R.items_mod.SCHEMA_FLOOR}\n"
        "baseline: 1\nadded: 0\ncompacted: 0\n")
#: The blocker on the BASE slot line.
EXTERNAL_BASE = HEAD + R._blocked_block("xx-1", "PARKED", f"external {EVENT}")
#: The blocker on an AMENDMENT over a base line reading NONE — the form that
#: survives the move.
EXTERNAL_AMENDED = (
    HEAD + R._blocked_block("xx-1", "PARKED", "NONE")
    + "amend-reason: 2026-10-07 the wait turned out to be on the vendor\n"
    + f"amended-blocked-by: 2026-10-07 external {EVENT}\n")

CLOSE = ("item", "close", "xx-1", "--met", "none", "--decided", "none")
DROP = ("item", "close", "xx-1", "--drop", "--reason", "overtaken")
ROW = "FINDING [close_over_live_blocker]"


def tracked_changes(repo: Path) -> str:
    """Pending changes to TRACKED files. The carrier lock is an untracked
    sibling this fixture's repo does not ignore, and it is not a write."""
    return git(repo, "status", "--porcelain", "--untracked-files=no")


def flat(text: str) -> str:
    return " ".join(text.split())


class ACloseSpeaksForAnExternalBlocker(unittest.TestCase):

    def _repo(self, items: str) -> Path:
        r = R._Repo(items=items)
        self.addCleanup(r.close)
        return r.dir

    def _done(self, repo: Path) -> str:
        return (repo / "ITEMS-DONE.md").read_text(encoding="utf-8")

    # --- the red-first arms ---------------------------------------------------

    def test_a_DONE_close_over_an_AMENDED_external_blocker_is_REFUSED(self):
        repo = self._repo(EXTERNAL_AMENDED)
        code, outp = run(repo, *CLOSE)
        self.assertEqual(code, exits.FINDING, outp)
        self.assertIn(ROW, outp)
        self.assertIn("NOT CLOSED", outp)
        # THE TWO EXITS ARE NAMED, which is the criterion's own wording.
        self.assertIn("item amend xx-1 --blocked-by NONE", flat(outp))
        self.assertIn("--drop", outp)
        # NOTHING MOVED: the refusal is before the first write.
        self.assertEqual(tracked_changes(repo), "", outp)
        self.assertNotIn("xx-1", self._done(repo))

    def test_a_DONE_close_over_a_BASE_external_blocker_is_REFUSED(self):
        repo = self._repo(EXTERNAL_BASE)
        code, outp = run(repo, *CLOSE)
        self.assertEqual(code, exits.FINDING, outp)
        self.assertIn(ROW, outp)
        self.assertEqual(tracked_changes(repo), "", outp)
        self.assertNotIn("xx-1", self._done(repo))

    def test_a_DROP_over_an_AMENDED_external_blocker_records_it_ABANDONED(self):
        """The body the old close left behind: `item check` reds it."""
        repo = self._repo(EXTERNAL_AMENDED)
        code, outp = run(repo, *DROP)
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertIn(f"blocker-moot: external {EVENT} (", self._done(repo))
        self.assertIn("dropped", self._done(repo))
        code, outp = run(repo, "item", "check")
        self.assertNotIn("blocked_in_done_home", outp)
        self.assertEqual(code, exits.CLEAN, outp)

    def test_a_DROP_over_a_BASE_external_blocker_records_it_ABANDONED(self):
        repo = self._repo(EXTERNAL_BASE)
        code, outp = run(repo, *DROP)
        self.assertEqual(code, exits.CLEAN, outp)
        self.assertIn(f"blocker-moot: external {EVENT} (", self._done(repo))
        self.assertIn("blocker-moot: external", outp,
                      "the record was written and not spoken")
        code, outp = run(repo, "item", "check")
        self.assertEqual(code, exits.CLEAN, outp)

    # --- the controls ---------------------------------------------------------

    def test_CONTROL_the_first_named_exit_WORKS(self):
        """The refusal says `item amend … --blocked-by NONE`; a refusal whose
        own remedy is refused would be a door with no handle."""
        repo = self._repo(EXTERNAL_AMENDED)
        code, outp = run(repo, "item", "amend", "xx-1", "--blocked-by",
                         "NONE", "--reason", "the vendor shipped 4.2")
        self.assertEqual(code, exits.CLEAN, outp)
        code, outp = run(repo, *CLOSE)
        self.assertEqual(code, exits.CLEAN, outp)
        code, outp = run(repo, "item", "check")
        self.assertEqual(code, exits.CLEAN, outp)

    def test_CONTROL_a_record_about_ANOTHER_event_discharges_nothing(self):
        """EQUALITY, as for every other type: the discharge must name the
        very event the effective blocker names."""
        repo = self._repo(HEAD.replace("baseline: 1", "baseline: 0"))
        body = (R._blocked_block("xx-1", "DROPPED", "NONE")
                + "amend-reason: 2026-10-07 retyped\n"
                + f"amended-blocked-by: 2026-10-07 external {EVENT}\n"
                + "blocker-moot: external some other event entirely (an "
                  "external event is observed by no close; this item was "
                  "dropped with the wait unanswered)\n")
        (repo / "ITEMS-DONE.md").write_text(
            R.EMPTY_DONE + body, encoding="utf-8")
        code, outp = run(repo, "item", "check")
        self.assertEqual(code, exits.FINDING, outp)
        self.assertIn("FINDING [blocked_in_done_home]", outp)


if __name__ == "__main__":
    unittest.main()
