"""The pre-push leak scan's NO-RANGES FALLBACK, at the hook's own altitude — lc-89.

WHAT THIS IS FOR. The fallback fires on every ordinary push of this repo (the
global `core.hooksPath` dispatcher chains this hook with an empty stdin, since
the repo has no remote in its guarded set). It used to hand the scanner the
range `..HEAD`, whose EMPTY base is not the scanner's sentinel, so git answered
`fatal: Not a valid object name ^{commit}` and the scan reached its coverage
only by DEGRADING — announced on a `degraded:` line naming an empty ref. The
coverage was never wrong; the reader was. A check that fires on a non-defect
trains the reflex that discounts the red that matters one day.

WHY THE ASSERTION IS NOT ONLY AN ABSENCE. The symptom is a STRING, and a hook
that scanned nothing at all would satisfy "no `fatal:` line" perfectly. So
every absence case here has a partner asserting what the change must NOT have
done:

  * the quiet run still reports a NON-ZERO scanned scope;
  * the quiet run still BLOCKS a leak that is reachable only at HEAD — the
    coverage assertion at the effect site, not at the message;
  * a GENUINELY unresolvable base still degrades LOUDLY, naming the ref it
    could not resolve — the fix is to the empty base, never to the diagnostic.

The hook under test is the TRACKED FILE, run with its cwd inside a throwaway
fixture repo: it resolves its root from `git rev-parse --show-toplevel` and
its scanner from `<root>/tools/absence-scan.mjs`, so a fixture cwd is enough
to exercise the real plumbing — stdin parse, range construction, the scanner
subprocess, and the translated exit code.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK = REPO_ROOT / "tools" / "git-hooks" / "pre-push"
SCANNER = REPO_ROOT / "tools" / "absence-scan.mjs"
DECLARATION = REPO_ROOT / ".claude" / "lifecycle.json"

ZERO = "0" * 40
# A syntactically valid sha that no object in a fresh fixture can carry.
UNRESOLVABLE = "d" * 40
# A full 8-4-4-4-12 identifier: the `capture-uuid` class fires on it in a
# SOURCE file, which is what makes the leak arm below a real block.
#
# ASSEMBLED, NOT WRITTEN OUT, and that is load-bearing rather than cute: the
# leak scan walks HEAD's tree, so a literal 8-4-4-4-12 run in this tracked
# file is a FINDING against the repo's own push gate — measured, `absence-scan
# test/test_pre_push_hook.py` exit 2, `capture-uuid` at the literal's line.
# The alternative was an allowlist entry, i.e. a standing exemption to
# maintain forever so that one test could hold bytes it only ever needs at
# run time. The payload the fixture receives is byte-identical either way.
PLANTED_UUID = "-".join(("6ba7b810", "9dad", "11d1", "80b4", "00c04fd430c8"))


def _git(cwd, *args):
    return subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
        cwd=cwd, capture_output=True, text=True, check=True).stdout


class TheNoRangesFallbackScansWithoutCryingWolf(unittest.TestCase):
    """Every case runs the real hook binary over a real git fixture."""

    @classmethod
    def setUpClass(cls):
        if shutil.which("node") is None:
            # Deliberately NOT a skip. This hook's own contract is that a
            # missing `node` BLOCKS the push — "COULD NOT VERIFY is not a
            # pass" — so a run that cannot reach the scanner is a failure of
            # this check too, never a quiet green.
            raise AssertionError(
                "no `node` on PATH: the leak scan cannot run, so the hook's "
                "behaviour is unverified. COULD NOT VERIFY is not a pass.")

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="lc89-"))
        self.addCleanup(shutil.rmtree, self.dir, True)
        (self.dir / "tools").mkdir()
        (self.dir / ".claude").mkdir()
        shutil.copy(SCANNER, self.dir / "tools" / "absence-scan.mjs")
        shutil.copy(DECLARATION, self.dir / ".claude" / "lifecycle.json")
        _git(self.dir, "init", "-q", ".")
        (self.dir / "carrier.md").write_text("an ordinary tracked line\n")
        _git(self.dir, "add", "-A")
        _git(self.dir, "commit", "-qm", "fixture base")

    def _run_hook(self, stdin_text=""):
        p = subprocess.run(
            ["python3", str(HOOK), "origin", "git@example.invalid:none"],
            cwd=self.dir, input=stdin_text, capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def _head(self):
        return _git(self.dir, "rev-parse", "HEAD").strip()

    # --- the defect itself -------------------------------------------------

    def test_the_fallback_names_no_fatal_and_no_empty_ref(self):
        """An ordinary push: neither offending line reaches the reader."""
        code, text = self._run_hook("")
        self.assertEqual(code, 0, text)
        self.assertNotIn("fatal:", text, text)
        self.assertNotIn("is not resolvable", text, text)

    # --- must-not-move: it still scans -------------------------------------

    def test_the_quiet_fallback_still_reports_a_non_zero_scope(self):
        """The absence above is worthless without this: a hook that scanned
        nothing would satisfy it exactly as well."""
        _, text = self._run_hook("")
        m = re.search(r"scope: (\d+) source file\(s\)", text)
        self.assertIsNotNone(m, f"no source-scope line at all:\n{text}")
        self.assertGreater(int(m.group(1)), 0, text)

    def test_the_quiet_fallback_still_blocks_a_leak_only_at_head(self):
        """Coverage asserted at the effect site. The payload is committed on
        top of the fixture base, so only a walk that actually reaches HEAD's
        tree can find it."""
        (self.dir / "leak.md").write_text(f"token {PLANTED_UUID}\n")
        _git(self.dir, "add", "-A")
        _git(self.dir, "commit", "-qm", "plant")
        code, text = self._run_hook("")
        self.assertEqual(code, 1, f"the leak was not blocked:\n{text}")
        self.assertIn("Push BLOCKED", text, text)
        self.assertIn("capture-uuid", text, text)
        # DELIBERATELY NO `fatal:` ASSERTION HERE. This arm is the UNPROBED
        # control of the pair: its job is that coverage did not move, and the
        # old hook's coverage was already right. An assertion on the message
        # would make it go red for the defect too, and a control that fails
        # alongside the probed case proves nothing about the axis it guards.
        # The message is arm one's business, and only arm one's.

    # --- must-not-move: a real unresolvable base still degrades loudly -----

    def test_a_genuinely_unresolvable_base_still_degrades_and_names_it(self):
        """This is the diagnostic the item preserves. It arrives through
        `ranges_from_stdin`, not the fallback, and it must keep saying which
        ref it could not resolve — an empty name there was the defect, silence
        would be worse than the defect."""
        head = self._head()
        code, text = self._run_hook(
            f"refs/heads/main {head} refs/heads/main {UNRESOLVABLE}\n")
        self.assertEqual(code, 0, text)
        self.assertIn("is not resolvable", text, text)
        self.assertIn(UNRESOLVABLE, text,
                      f"the degraded line named no ref:\n{text}")

    def test_a_new_ref_push_is_still_scanned_rather_than_skipped(self):
        """A first push (remote sha all zeros) has no old side. Whatever
        spelling carries that, the content must still be scanned — asserted
        at the effect site with a planted leak, never at the message."""
        (self.dir / "leak.md").write_text(f"token {PLANTED_UUID}\n")
        _git(self.dir, "add", "-A")
        _git(self.dir, "commit", "-qm", "plant")
        head = self._head()
        code, text = self._run_hook(
            f"refs/heads/main {head} refs/heads/main {ZERO}\n")
        self.assertEqual(code, 1, f"a new-ref push scanned nothing:\n{text}")
        self.assertIn("Push BLOCKED", text, text)

    def test_a_new_ref_push_names_no_fatal_and_no_empty_ref(self):
        """lc-89's second site. The coverage arm above deliberately says
        nothing about the message, because a control that also asserts the
        probed property goes red for the defect and certifies nothing about
        the axis it guards. This is that assertion, in its own arm: a first
        push carries no old side, and the spelling that carries it must be
        the scanner's `EMPTY` sentinel rather than a blank — a blank reaches
        git as a bare `^{commit}` and the reader gets a `fatal:` on an
        ordinary push, which is the non-defect fire this item exists to
        stop."""
        (self.dir / "ordinary.md").write_text("nothing interesting\n")
        _git(self.dir, "add", "-A")
        _git(self.dir, "commit", "-qm", "ordinary")
        head = self._head()
        code, text = self._run_hook(
            f"refs/heads/main {head} refs/heads/main {ZERO}\n")
        self.assertNotIn("fatal:", text, text)
        self.assertNotIn("is not resolvable", text, text)
        # The absence above is worthless without this: a hook that scanned
        # nothing at all would satisfy both assertions.
        self.assertIn("scope:", text, text)
        self.assertEqual(code, 0, text)


if __name__ == "__main__":
    unittest.main()
