"""The git hooks a repo SHIPS stay launchable — the branches the roster rows
do not reach (lc-103).

`refusals.HOOK_ROWS` proves the two FIRING inputs: a hook under
`tools/git-hooks/` and a hook the plugin manifest declares, each committed at
100644, each against a control differing in the mode alone. What a plant/
control pair cannot carry is the rest of the answer space, and every one of
those is a way for this guard to be wrong QUIETLY:

  * the scope — an ordinary tracked file at 100644 must not fire, asserted in
    a fixture where the in-scope hook DOES fire in the same run, because a
    scope test over a clean fixture passes against a checker that ignores
    paths entirely;
  * the could-not-verify answers — a symlink, a path git cannot be asked
    about, a declared script absent from the tree;
  * the one state that must stay SILENT: a repo with no commit, which is what
    every other roster row's control is, and where a could-not-verify here
    would have degraded them all;
  * the population itself, over the REAL repo — the anti-vacuity pin. A guard
    whose population derives to nothing is green forever and reads exactly
    like a guard over a healthy repo.
"""

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

from lifecycle_core import declaration as decl  # noqa: E402
from lifecycle_core import exits, ledger as ledger_mod, refusals  # noqa: E402

HOOK_BODY = "#!/bin/sh\nexit 0\n"


class _Fixture:
    """A real git repo carrying a valid declaration, plus whatever this test
    plants. A real `git init` and a real commit, because the whole subject is
    what git's TREE records — a fake would answer whatever was hoped for."""

    def __init__(self):
        self.dir = Path(tempfile.mkdtemp(prefix="lc103-hookmode-"))
        self._git("init", "-q", "-b", "main")
        # No hooks from the machine's global core.hooksPath: this repo is an
        # instrument, and an unrelated gate firing inside it would be read as
        # this test's own verdict.
        self._git("config", "core.hooksPath", str(self.dir / ".nohooks"))
        self._git("config", "user.email", "hookmode@lifecycle.invalid")
        self._git("config", "user.name", "lc103 fixture")
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

    def _git(self, *args):
        return subprocess.run(["git", *args], cwd=str(self.dir),
                              capture_output=True, text=True)

    def write(self, rel, body, mode=0o644):
        p = self.dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
        p.chmod(mode)
        return p

    def symlink(self, rel, target):
        p = self.dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(target, p)
        return p

    def commit(self):
        self._git("add", "-A")
        self._git("commit", "-qm", "fixture")

    def modes(self):
        """What git ACTUALLY recorded — the arrangement, read back before any
        verdict over it counts."""
        p = self._git("ls-tree", "-r", "HEAD")
        out = {}
        for line in p.stdout.splitlines():
            meta, _, path = line.partition("\t")
            bits = meta.split()
            if path and len(bits) >= 3:
                out[path] = bits[0]
        return out

    def read(self):
        return decl.read(self.dir)

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def _hook_findings(res):
    return [f for f in res.findings if f.row == "hook_not_executable"]


def _hook_unverified(res):
    return [u for u in res.unverified if "hook" in u or "HEAD" in u]


class Population(unittest.TestCase):
    """THE ANTI-VACUITY PIN, over the real repo rather than a fixture.

    The guard's population is derived every run, so the way it fails silently
    is by deriving to NOTHING — a green indistinguishable from a healthy repo.
    This test is what goes red if either half of the union stops reaching its
    member, and it is the known-positive for the derivation: both paths are
    present, and both are real.

    IT PINS `hook_population`, which is the expression the CHECK ITSELF uses.
    An earlier cut of this test rebuilt the union out of the two helpers and
    stayed GREEN under the injection that removes the `tools/git-hooks/`
    half — measured, lc-103 bite 1 — because a pin over a restatement of the
    population grades the restatement.
    """

    def test_both_halves_of_the_union_reach_a_real_member(self):
        modes, declared = decl.hook_population(REPO_ROOT)
        self.assertEqual(declared, ["plugin/hooks/pre-commit"],
                         "the manifest-declared half derived to "
                         f"{declared!r}; a population that derives to nothing "
                         "is green forever")
        self.assertIsNotNone(modes)
        self.assertIn("plugin/hooks/pre-commit", modes)
        self.assertIn("tools/git-hooks/pre-push", modes,
                      "the repo's OWN hook tooling — the half the manifest "
                      "does not declare, and the half that actually shipped "
                      "dead in 0cbd1ad")
        for path, mode in modes.items():
            self.assertEqual(mode, decl.EXECUTABLE_MODE,
                             f"{path} is committed at {mode}")

    def test_this_repo_emits_no_hook_finding_today(self):
        res = decl.read(REPO_ROOT)
        self.assertEqual(_hook_findings(res), [])


class Scope(unittest.TestCase):
    """A NON-hook file's mode is not policed — asserted in a fixture where the
    in-scope hook fires in the SAME run. A scope test over a clean fixture
    passes against a checker that ignores paths entirely."""

    def test_only_the_hook_fires_while_four_other_modes_are_wrong(self):
        with _Fixture() as f:
            f.write("tools/git-hooks/pre-push", HOOK_BODY, 0o644)
            f.write("notes.md", "an ordinary tracked file\n", 0o644)
            f.write("tools/hooks-note.md", "prose about hooks\n", 0o644)
            # A sibling directory whose name STARTS with the guarded one: a
            # pathspec compared as text rather than as a path prefix would
            # swallow it, which is the prefix match in an equality's costume.
            f.write("tools/git-hooks-extra/helper.sh", HOOK_BODY, 0o644)
            # DIRECTLY under, and no deeper: a nested file is not a hook git
            # will ever launch from this directory.
            f.write("tools/git-hooks/sub/deep.sh", HOOK_BODY, 0o644)
            f.commit()

            recorded = f.modes()
            for rel in ("tools/git-hooks/pre-push", "notes.md",
                        "tools/hooks-note.md",
                        "tools/git-hooks-extra/helper.sh",
                        "tools/git-hooks/sub/deep.sh"):
                self.assertEqual(recorded.get(rel), "100644",
                                 f"the arrangement never carried {rel} at "
                                 "100644, so its silence proves nothing")

            findings = _hook_findings(f.read())
            self.assertEqual(len(findings), 1, [x.message for x in findings])
            self.assertIn("tools/git-hooks/pre-push", findings[0].message)
            for rel in ("notes.md", "tools/hooks-note.md",
                        "tools/git-hooks-extra/helper.sh",
                        "tools/git-hooks/sub/deep.sh"):
                self.assertNotIn(rel, findings[0].message)


class CouldNotVerify(unittest.TestCase):
    """The third answer, at each site that has one. Silence and a
    pass-shaped zero are never options here."""

    def test_a_tracked_symlink_is_could_not_verify_not_a_finding(self):
        with _Fixture() as f:
            f.write("tools/real-hook", HOOK_BODY, 0o755)
            f.symlink("tools/git-hooks/pre-push", "../real-hook")
            f.commit()
            self.assertEqual(f.modes().get("tools/git-hooks/pre-push"),
                             decl.SYMLINK_MODE,
                             "the arrangement never committed a symlink")
            res = f.read()
            self.assertEqual(_hook_findings(res), [],
                             "a symlink is not a finding: the target's mode "
                             "decides, and firing here would be the guard "
                             "firing on legitimate work")
            self.assertTrue(
                any("SYMLINK" in u and "tools/git-hooks/pre-push" in u
                    for u in res.unverified), res.unverified)
            self.assertEqual(res.code, exits.COULD_NOT_VERIFY)

    def test_a_path_git_cannot_be_asked_about_is_could_not_verify(self):
        with _Fixture() as f:
            shutil.rmtree(f.dir / ".git")
            res = f.read()
            self.assertEqual(_hook_findings(res), [])
            self.assertTrue(any("HEAD" in u for u in res.unverified),
                            res.unverified)

    def test_a_declared_script_absent_from_the_tree_is_could_not_verify(self):
        with _Fixture() as f:
            root = f.dir / "pluginroot"
            (root / ".claude-plugin").mkdir(parents=True)
            (root / ".claude-plugin" / "plugin.json").write_text(
                json.dumps({"name": "scratch",
                            decl.PLUGIN_GIT_HOOKS_KEY: {
                                "pre-commit": {"script": "hooks/pre-commit"}}},
                           indent=2), encoding="utf-8")
            f.commit()
            self.assertNotIn("pluginroot/hooks/pre-commit", f.modes(),
                             "the arrangement accidentally committed the very "
                             "script this case is about")
            orig = decl.plugin_root
            decl.plugin_root = lambda: root
            try:
                res = f.read()
            finally:
                decl.plugin_root = orig
            self.assertEqual(_hook_findings(res), [])
            self.assertTrue(
                any("pluginroot/hooks/pre-commit" in u for u in res.unverified),
                res.unverified)


class NoCommitYet(unittest.TestCase):
    """The state every other roster row's CONTROL is in.

    A repo with no commit has committed no hook, so the guarded set is EMPTY —
    a state, not an unanswered question. Answering could-not-verify here would
    have degraded every declaration row's control from CLEAN to 3, and the
    row whose `expect` IS 3 would have stopped discriminating altogether.
    """

    def test_an_unborn_head_is_silent_and_the_repo_still_reads_clean(self):
        with _Fixture() as f:
            self.assertEqual(
                f._git("rev-parse", "--verify", "-q", "HEAD").returncode, 1,
                "the arrangement is not the unborn-HEAD state it names")
            self.assertIs(decl.head_commit(f.dir), False)
            res = f.read()
            self.assertEqual(_hook_findings(res), [])
            self.assertEqual(_hook_unverified(res), [])
            self.assertEqual(res.code, exits.CLEAN, res.unverified)


if __name__ == "__main__":
    unittest.main()
