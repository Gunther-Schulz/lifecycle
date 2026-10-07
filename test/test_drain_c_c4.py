"""Drain wave C, lane C4 — write-sets nobody resolved; the carrier nobody
counted (2026-10-07).

ONE FILE FOR THE LANE (wave B change 4): every red-first test this lane's
items asked for lives here rather than in the batteries the items name, so
the hunks of six parallel lanes do not meet in `test_items.py`.

EVERY FIXTURE IS A REAL GIT WORK TREE WITH TRACKED DIRECTORIES. The items
below all turn on what a write-set path RESOLVES to, and resolution is asked
of git (`git ls-files`), so a scratch repo that tracked no `plugin/` would
answer "unresolved" for the correct spelling and the misspelled one alike —
an arrangement that could not tell the defect from its control.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli as cli_mod, exits, items, refusals  # noqa: E402


#: The tree every fixture repo tracks. Three top-level directories and one
#: file two items can really share.
TRACKED = (
    "plugin/cli/lifecycle_core/refusals.py",
    "plugin/cli/lifecycle_core/declaration.py",
    "plugin/cli/lifecycle_core/verbs.py",
    "test/absence-scan.test.mjs",
    "docs/readme.md",
)


def carrier(blocks):
    """A carrier whose conservation identity balances over `blocks`."""
    out = [f"schema: {items.SCHEMA_FLOOR}", f"baseline: {len(blocks)}",
           "added: 0", "compacted: 0", ""]
    for ident, slots in blocks:
        out.append(f"## {ident}")
        for slot in items.SLOTS:
            out.append(f"{slot}: {slots[slot]}")
        out.append("")
    return "\n".join(out)


def block(ident, write_set, *, grade="READY", blocked_by="NONE"):
    return (ident, {
        "grade": grade,
        "requirement": f"{ident} exists so a write-set has an owner — "
                       "record: test_drain_c_c4.py",
        "goal": "mitigate",
        "write-set": write_set,
        "done-criterion": "the verdict it draws is the verdict it earns",
        "evidence": "MEASURED: constructed for this battery",
        "blocked-by": blocked_by,
    })


class Base(unittest.TestCase):

    def _repo(self, blocks, *, tracked=TRACKED):
        repo = refusals._Repo(items=carrier(blocks))
        for rel in tracked:
            p = repo.dir / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("seed\n", encoding="utf-8")
        if tracked:
            subprocess.run(["git", "add", "--"] + list(tracked),
                           cwd=str(repo.dir), capture_output=True, text=True)
            subprocess.run(["git", "commit", "-qm", "tracked tree"],
                           cwd=str(repo.dir), capture_output=True, text=True)
        return repo

    def _run(self, repo, *argv):
        here = os.getcwd()
        try:
            os.chdir(str(repo.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(repo.dir)] + list(argv))
            return code, buf.getvalue()
        finally:
            os.chdir(here)


# --- lc-111 -------------------------------------------------------------------

#: THE MOVERS, PINNED. Both values are this repo's own carrier at `f7396b0`
#: (2026-09-13) — the last commit at which lc-24 and lc-66 read `grade:
#: READY` with `blocked-by: NONE`, before that day's parks. Copied as
#: literals rather than read with `git show`, so the proof neither expires
#: when HEAD moves nor skips in a shallow clone; `git show f7396b0:ITEMS.md`
#: is how to re-derive them.
LC24_WRITE_SET = "test/absence-scan.test.mjs,cache-fix test/absence-scan.test.mjs"
LC66_WRITE_SET = ("docs/directives/carrier-rework-design-2026-08-26.md@cache-fix,"
                  "plugin/cli/lifecycle_core/declaration.py,"
                  "plugin/cli/lifecycle_core/verbs.py")
#: THE MUST-NOT-MOVE CONTROL, same commit window (`2b41491`): the identical
#: foreign path, correctly booked behind a blocker.
LC67_WRITE_SET = ("docs/directives/carrier-rework-design-2026-08-26.md@cache-fix,"
                  "plugin/cli/lifecycle_core/verbs.py")

ROW = "FINDING [write_set_foreign_unblocked]"


class WriteSetVenueVerdict(Base):
    """lc-111 — `item check` grades every READY item's write-set ELEMENTS."""

    def _findings(self, out):
        return [ln for ln in out.splitlines() if ROW in ln]

    def test_lc24_a_bare_repo_name_SECOND_in_the_slot_is_a_FINDING(self):
        """The mover the first hand sweep MISSED: its foreign element is the
        second one, behind a local `test/` path."""
        with self._repo([block("xx-1", LC24_WRITE_SET)]) as r:
            code, out = self._run(r, "item", "check")
            hits = self._findings(out)
            self.assertEqual(len(hits), 1, out)
            self.assertIn("xx-1", hits[0])
            self.assertIn("cache-fix test/absence-scan.test.mjs", hits[0])
            self.assertEqual(code, exits.FINDING, out)

    def test_lc66_an_at_repo_suffix_is_a_FINDING(self):
        with self._repo([block("xx-1", LC66_WRITE_SET)]) as r:
            code, out = self._run(r, "item", "check")
            hits = self._findings(out)
            self.assertEqual(len(hits), 1, out)
            self.assertIn("@cache-fix", hits[0])
            self.assertEqual(code, exits.FINDING, out)

    def test_an_absolute_path_is_a_FINDING(self):
        with self._repo([block("xx-1", "/srv/elsewhere/thing.py")]) as r:
            code, out = self._run(r, "item", "check")
            self.assertEqual(len(self._findings(out)), 1, out)
            self.assertEqual(code, exits.FINDING, out)

    def test_lc67_a_foreign_venue_BEHIND_A_BLOCKER_does_not_fire(self):
        """The refusal is the MISSING BLOCKER, never the foreign venue."""
        with self._repo([block("xx-1", "docs/readme.md", grade="PARKED",
                               blocked_by="external the upstream release"),
                         block("xx-2", LC67_WRITE_SET,
                               blocked_by="xx-1")]) as r:
            code, out = self._run(r, "item", "check")
            self.assertEqual(self._findings(out), [], out)
            self.assertIn("1 foreign under a blocker", out)
            self.assertEqual(code, exits.CLEAN, out)

    def test_a_NEW_file_under_a_tracked_directory_does_not_fire(self):
        """Resolvability-or-new, never mere existence — or every booking of
        a file that does not exist yet breaks."""
        with self._repo([block(
                "xx-1", "plugin/cli/lifecycle_core/not_written_yet.py")]) as r:
            code, out = self._run(r, "item", "check")
            self.assertEqual(self._findings(out), [], out)
            self.assertIn("write-set venues: CLEAN", out)
            self.assertIn("1 resolve here", out)
            self.assertEqual(code, exits.CLEAN, out)

    def test_a_tracked_file_and_a_tracked_directory_both_resolve(self):
        with self._repo([block("xx-1", "docs/readme.md,test/")]) as r:
            code, out = self._run(r, "item", "check")
            self.assertIn("2 resolve here", out)
            self.assertEqual(code, exits.CLEAN, out)

    def test_UNKNOWN_is_COULD_NOT_VERIFY_never_a_finding_never_silence(self):
        with self._repo([block("xx-1", "UNKNOWN")]) as r:
            code, out = self._run(r, "item", "check")
            self.assertEqual(self._findings(out), [], out)
            verdict = [ln for ln in out.splitlines()
                       if ln.startswith("write-set venues: COULD NOT VERIFY")]
            self.assertEqual(len(verdict), 1, out)
            self.assertIn("xx-1", verdict[0])
            self.assertEqual(code, exits.COULD_NOT_VERIFY, out)

    def test_only_READY_items_are_graded(self):
        """A NEW item is not on the board, so nothing calls it dispatchable."""
        with self._repo([block("xx-1", LC66_WRITE_SET, grade="NEW")]) as r:
            code, out = self._run(r, "item", "check")
            self.assertEqual(self._findings(out), [], out)
            self.assertIn("no READY item", out)
            self.assertEqual(code, exits.CLEAN, out)

    def test_prose_and_venue_elements_are_COUNTED_not_silently_passed(self):
        """The criterion names three answers; a prose or `decision:` element
        is none of them, so the verdict says how many it did not grade."""
        with self._repo([block("xx-1", "docs/readme.md (the intro only)"),
                         block("xx-2", "decision:who-seeds-it")]) as r:
            code, out = self._run(r, "item", "check")
            self.assertEqual(self._findings(out), [], out)
            line = [ln for ln in out.splitlines()
                    if ln.startswith("write-set venues: NOT GRADED")]
            self.assertEqual(len(line), 1, out)
            self.assertIn("1 prose", line[0])
            self.assertIn("1 venue", line[0])
            self.assertEqual(code, exits.CLEAN, out)

    def test_a_tree_git_cannot_list_is_COULD_NOT_VERIFY(self):
        """Resolution with no tree to resolve against examined nothing."""
        verdict = []
        parsed = items.parse(carrier([block("xx-1", "docs/readme.md")]))
        code = items.check_write_set_venues(
            parsed, verdict.append, None, "`git ls-files` exited 128", "xx")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, verdict)
        self.assertIn("COULD NOT VERIFY", verdict[0])
        self.assertIn("exited 128", verdict[0])


if __name__ == "__main__":
    unittest.main()
