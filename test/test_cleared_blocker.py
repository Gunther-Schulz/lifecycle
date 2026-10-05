"""A blocker CLEARED on a PARKED item is a state the carrier accepts.

THE DEFECT. `item promote` over an `external` blocker refuses and names the
act that ends the wait: `item amend --blocked-by NONE --reason`. That act
wrote its amendment group and then could not commit it — the commit-time
shape gate ran `item check --staged` over the block the verb had just
written and reported `parked_without_typed_blocker` about it. Measured
2026-10-05 on a scratch carrier (an `external` blocker) and on the real one
(a `decision` blocker): exit 2, `move_uncommitted`, the carrier left
modified on disk.

WHY THE GATE IS INSTALLED HERE. Every other fixture repo in this suite
points `core.hooksPath` at nothing, so a commit inside one is graded by no
gate at all — and on such a repo the amend exits 0 on the UNREPAIRED code
too, which would make this arm green for a reason nobody wrote down. The
refusal lives in the gate, so the gate is part of the arrangement: a
pre-commit hook running THIS checkout's `item check --staged`, which is the
one command the machine's own hook runs.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLI = REPO / "plugin" / "cli" / "lifecycle"

sys.path.insert(0, str(REPO / "plugin" / "cli"))

from lifecycle_core import exits, items, refusals  # noqa: E402

HEAD = "schema: 2\nbaseline: 1\nadded: 0\ncompacted: 0\n"
EVENT = "external the vendor ships release 9"
REASON = "release 9 shipped on 2026-10-04, tag v9.0.0 on the vendor's remote"

#: The commit-time gate, as the machine's hook runs it: the CLI's own exit 2
#: blocks the commit and its report goes to the committer.
GATE = f"""#!/bin/sh
out=$("{sys.executable}" "{CLI}" --repo "$(git rev-parse --show-toplevel)" \\
      item check --staged 2>&1)
rc=$?
if [ "$rc" -eq 2 ]; then
    echo "This staged edit INTRODUCES a shape break in an item carrier:" >&2
    echo "$out" >&2
    exit 1
fi
exit 0
"""


class _Base(unittest.TestCase):

    def _repo(self, items_text, *, gated=True):
        r = refusals._Repo(items=items_text)
        self.addCleanup(r.close)
        if gated:
            hooks = r.dir / ".gate"
            hooks.mkdir()
            hook = hooks / "pre-commit"
            hook.write_text(GATE, encoding="utf-8")
            hook.chmod(0o755)
            subprocess.run(["git", "config", "core.hooksPath", str(hooks)],
                           cwd=str(r.dir), check=True)
        return r

    def _run(self, repo, *argv):
        import io
        from contextlib import redirect_stdout
        from lifecycle_core import cli as cli_mod
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli_mod.main(["--repo", str(repo.dir)] + list(argv))
        return code, buf.getvalue()

    def _git(self, repo, *argv):
        return subprocess.run(["git", *argv], cwd=str(repo.dir),
                              capture_output=True, text=True).stdout

    def _tracked_changes(self, repo):
        """`git status` over TRACKED files. The fixture's own hook directory
        and the carrier's lock file are untracked by construction and are
        not what "the amendment is committed" is about."""
        return self._git(repo, "status", "--short", "--untracked-files=no")

    def _item(self, repo):
        return items.parse((repo.dir / "ITEMS.md").read_text(
            encoding="utf-8")).items[0]


class ClearingAParkedBlockerCommits(_Base):
    """park on an external event → the prescribed amend → promote."""

    def test_the_prescribed_amend_commits_and_the_head_names_the_promotion(self):
        r = self._repo(HEAD + refusals._blocked_block("xx-1", "NEW", "NONE"))
        code, out = self._run(r, "item", "park", "xx-1", "--blocked-by", EVENT)
        self.assertEqual(code, exits.CLEAN, out)

        # THE TOOL'S OWN TEXT PRESCRIBES THE ACT under test.
        code, out = self._run(r, "item", "promote", "xx-1", "--by", "desk",
                              "--reason", "complete")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[promote_while_blocked]", out)
        self.assertIn("`item amend --blocked-by NONE --reason`", out)

        before = self._git(r, "rev-parse", "HEAD").strip()
        code, out = self._run(r, "item", "amend", "xx-1", "--blocked-by",
                              "NONE", "--reason", REASON)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("move_uncommitted", out)
        self.assertIn("committed: lifecycle: amend xx-1", out)
        self.assertNotEqual(self._git(r, "rev-parse", "HEAD").strip(), before)
        self.assertEqual(self._tracked_changes(r), "",
                         "the amendment is committed and the tree is clean")
        self.assertIn("amended-blocked-by:",
                      self._git(r, "show", "HEAD:ITEMS.md"))
        last = out.rstrip("\n").splitlines()[-1]
        self.assertIn("xx-1 is still PARKED", last)
        self.assertIn("`item promote", last)

        # THE CARRIER ACCEPTS THE STATE AND SAYS IT HOLDS ONE.
        code, out = self._run(r, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("parked_without_typed_blocker", out)
        self.assertIn("PARKED with a CLEARED blocker: 1 item(s) — xx-1", out)
        self.assertIn("`item ready --head`", out)

        # THE HEAD NAMES IT, among the waits that are over.
        today = self._item(r).amendments[0][1][:10]
        code, out = self._run(r, "item", "ready", "--head")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("--- waits OVER: 1 item(s)", out)
        self.assertIn(f"xx-1 [PARKED] blocker cleared by amendment on "
                      f"{today}: {REASON}", out)

        code, out = self._run(r, "item", "ready", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn(f"UNBLOCKED — blocker cleared by amendment on {today}: "
                      f"{REASON}", out)

        # NOTHING WAS PROMOTED until a desk judged it (law 10).
        self.assertEqual(self._item(r).grade, "PARKED")
        code, out = self._run(r, "item", "promote", "xx-1", "--by", "desk",
                              "--reason", "complete, and the event arrived")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(self._tracked_changes(r), "")
        self.assertEqual(self._item(r).grade, "READY")

        # ...and once promoted it is no longer a wait the head owes naming.
        code, out = self._run(r, "item", "ready", "--head")
        self.assertNotIn("waits OVER", out)
        code, out = self._run(r, "item", "check")
        self.assertNotIn("CLEARED blocker", out)

    def test_a_decision_blocker_clears_the_same_way(self):
        """The real carrier's instance (lc-239) was a `decision` blocker."""
        r = self._repo(HEAD + refusals._blocked_block(
            "xx-1", "PARKED", "decision which window"))
        code, out = self._run(r, "item", "amend", "xx-1", "--blocked-by",
                              "NONE", "--reason", "the desk re-graded it")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(self._tracked_changes(r), "")

    def test_the_head_clips_a_long_reason_and_ready_does_not(self):
        long_reason = "the event arrived, and " + "x" * 400
        r = self._repo(HEAD + refusals._blocked_block("xx-1", "PARKED", EVENT)
                       + f"amend-reason: 2026-10-05 {long_reason}\n"
                         "amended-blocked-by: 2026-10-05 NONE\n", gated=False)
        code, out = self._run(r, "item", "ready", "--head")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("xx-1 [PARKED] blocker cleared by amendment on "
                      "2026-10-05: the event arrived", out)
        self.assertNotIn(long_reason, out)
        code, out = self._run(r, "item", "ready", "xx-1")
        self.assertIn(long_reason, out)


class TheExemptionIsNarrow(_Base):
    """What still fires: every PARKED block whose BASE line is not typed."""

    AMEND = ("amend-reason: 2026-10-05 cleared\n"
             "amended-blocked-by: 2026-10-05 NONE\n")

    def _check(self, block):
        r = self._repo(HEAD + block, gated=False)
        return self._run(r, "item", "check")

    def test_a_base_NONE_still_fires(self):
        code, out = self._check(
            refusals._blocked_block("xx-1", "PARKED", "NONE"))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [parked_without_typed_blocker]", out)
        self.assertNotIn("CLEARED blocker", out)

    def test_a_base_NONE_under_a_NONE_amendment_still_fires(self):
        """The amendment alone is not the exemption: the base line must have
        carried a typed blocker for there to have been a wait to clear."""
        code, out = self._check(
            refusals._blocked_block("xx-1", "PARKED", "NONE") + self.AMEND)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [parked_without_typed_blocker]", out)

    def test_a_prose_base_under_a_NONE_amendment_still_fires(self):
        code, out = self._check(
            refusals._blocked_block("xx-1", "PARKED", "we should think")
            + self.AMEND)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [parked_without_typed_blocker]", out)

    def test_a_typed_base_amended_to_prose_still_fires(self):
        code, out = self._check(
            refusals._blocked_block("xx-1", "PARKED", EVENT)
            + "amend-reason: 2026-10-05 retyped\n"
              "amended-blocked-by: 2026-10-05 we should think\n")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [parked_without_typed_blocker]", out)

    def test_the_typed_base_under_a_NONE_amendment_is_the_one_exempt(self):
        """The control of the four above: same block, base line typed."""
        code, out = self._check(
            refusals._blocked_block("xx-1", "PARKED", EVENT) + self.AMEND)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("parked_without_typed_blocker", out)
        self.assertIn("PARKED with a CLEARED blocker: 1 item(s) — xx-1", out)


if __name__ == "__main__":
    unittest.main()
