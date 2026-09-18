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

And the answer this file's own ARRANGEMENT needs (lc-115): the cases below
that read THIS repo's recorded history have no arrangement at all outside a
checkout of it — inside a `git archive HEAD` snapshot, which the guard/checker
devbook now mandates for red-first and bite work, they produced two failures
and three errors that belonged to the arrangement and not to the code. Two
lanes diagnosed them independently and each paid attention for it; the live
risk was a third lane silencing a correct instrument. So those cases SKIP with
the arrangement named — the third answer, which this file already reached for
one case over (a ref that no longer resolves) and left open for the case
where there is no repository to ask.
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


def _absent_repository_reason():
    """`""` when REPO_ROOT IS this repo's own git checkout, else the reason it
    is not — the arrangement NAMED, because a bare skip reads as a pass.

    The question is deliberately narrow: is there a repository here to ask.
    It is asked of git rather than of `.git`, which is a file in a worktree
    and a directory in a checkout, and it compares the TOPLEVEL against
    REPO_ROOT — `rev-parse` walks UPWARDS, so an extracted snapshot that
    happens to sit inside some other repository answers about THAT one, and
    the refs below would then fail to resolve in a tree that reported itself
    a repository.

    What it does NOT cover, on purpose: a checkout whose pinned refs are
    missing (a shallow clone). That is a repository, the question is
    answerable, and `test_the_refs_this_proof_is_pinned_to_still_resolve`
    says in its own words why that stays a loud failure rather than a skip.
    Widening this predicate to cover it would silence that instrument.
    """
    p = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse",
                        "--show-toplevel"], capture_output=True, text=True)
    if p.returncode != 0:
        return (f"no git repository at {REPO_ROOT} "
                f"(git rev-parse --show-toplevel said: "
                f"{(p.stderr.strip() or p.stdout.strip())!r}) — these cases "
                "read this repo's OWN recorded history (the pinned refs, the "
                "committed hook modes), so an extracted snapshot carries no "
                "arrangement for them and a red here would belong to the "
                "arrangement, not to the code")
    top = Path(p.stdout.strip()).resolve()
    if top != REPO_ROOT:
        return (f"{REPO_ROOT} is not a git checkout of its own: git reports "
                f"the enclosing repository as {top}, which cannot answer for "
                "this repo's recorded history — an extracted snapshot placed "
                "inside another repository is the case, and it reads as a "
                "repository to every cheaper test")
    return ""


class _NeedsThisRepo:
    """Mixin: these cases read THIS repo's recorded history, so an absent
    repository is answered with a skip that names the arrangement.

    ONE body, mixed in, rather than the predicate restated per class: a
    restatement drifts, and the class that keeps the old spelling goes back to
    erroring in exactly the arrangement this exists for. The mixin is also
    what the must-not-move arm below DERIVES its population from, so a class
    that drops it is a class that silently leaves both.
    """

    @classmethod
    def setUpClass(cls):
        reason = _absent_repository_reason()
        if reason:
            raise unittest.SkipTest(reason)
        super().setUpClass()


def _guarded_classes():
    """Every test class in this module that declares the precondition —
    DERIVED from the mixin, never a list beside it. A pin over a restated
    population grades the restatement."""
    return sorted(
        (obj for obj in globals().values()
         if isinstance(obj, type) and issubclass(obj, unittest.TestCase)
         and issubclass(obj, _NeedsThisRepo)),
        key=lambda c: c.__name__)


def _hook_findings(res):
    return [f for f in res.findings if f.row == "hook_not_executable"]


def _hook_unverified(res):
    return [u for u in res.unverified if "hook" in u or "HEAD" in u]


class Population(_NeedsThisRepo, unittest.TestCase):
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

    Both cases need a repository: the first reads git's recorded modes, and
    the second is a pass-shaped zero without one — `decl.read` finds no modes
    to police, so it emits no finding and the assertion is satisfied by the
    absence of the very arrangement it grades.
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


class TheRepoSOwnRecordedInstance(_NeedsThisRepo, unittest.TestCase):
    """The pair the incident itself left behind, run at the REAL altitude.

    `0cbd1ad` committed `tools/git-hooks/pre-push` at 100644 and `d8c3934`
    restored the bit — SAME blob `887ecff8`, mode the only difference, which
    is why a bytes-only restore check passed it and the leak scan was dead
    for twenty minutes. A guard for this defect that cannot go red on the
    repo's own recorded instance of it is unproven whatever else it asserts.

    THE REFS ARE PINNED, NOT HEAD. HEAD carries a different blob today
    (`7b5aafe` edited the file), so the mode pair still holds there but the
    same-blob property — the thing that makes the demonstration sharp — exists
    only between these two commits. A proof anchored to a moving ref expires
    the next time anyone touches the file.

    The clone is `--shared` into a temp directory and thrown away; nothing is
    written to this repo, and no worktree is added to its `.git`.
    """

    REFS = {"0cbd1ad": "100644", "d8c3934": "100755"}

    def _clone_at(self, ref, into):
        subprocess.run(["git", "clone", "--quiet", "--shared",
                        str(REPO_ROOT), str(into)],
                       capture_output=True, text=True, check=True)
        subprocess.run(["git", "-C", str(into), "checkout", "--quiet", ref],
                       capture_output=True, text=True, check=True)

    def test_the_refs_this_proof_is_pinned_to_still_resolve(self):
        """A ref that no longer resolves turns every assertion below into a
        setup error wearing a finding's clothes."""
        for ref in self.REFS:
            p = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse",
                                "--verify", "-q", f"{ref}^{{commit}}"],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 0,
                             f"{ref} no longer resolves in this checkout, so "
                             "this proof has no arrangement — a shallow clone "
                             "is the likely cause, and it is a loud failure "
                             "rather than a silent skip on purpose")

    def test_the_same_blob_at_two_modes_is_still_what_these_refs_carry(self):
        blobs = set()
        for ref, mode in self.REFS.items():
            p = subprocess.run(["git", "-C", str(REPO_ROOT), "ls-tree", ref,
                                "--", "tools/git-hooks/pre-push"],
                               capture_output=True, text=True)
            bits = p.stdout.split()
            self.assertEqual(bits[0], mode, p.stdout)
            blobs.add(bits[2])
        self.assertEqual(len(blobs), 1,
                         "the two refs no longer carry the SAME blob, so the "
                         "pair stopped isolating the mode")

    def test_the_guard_fires_at_the_defect_and_is_clean_at_the_fix(self):
        for ref, mode in self.REFS.items():
            with self.subTest(ref=ref, mode=mode):
                work = Path(tempfile.mkdtemp(prefix=f"lc103-{ref}-"))
                try:
                    self._clone_at(ref, work / "repo")
                    p = subprocess.run(
                        [sys.executable,
                         str(REPO_ROOT / "plugin" / "cli" / "lifecycle"),
                         "--repo", str(work / "repo"), "kind", "check"],
                        capture_output=True, text=True)
                    fired = "[hook_not_executable]" in p.stdout
                    if mode == "100644":
                        self.assertTrue(fired, p.stdout)
                        self.assertEqual(p.returncode, exits.FINDING, p.stdout)
                        # The ONLY finding, so nothing else could have moved
                        # the exit code — the pair would otherwise separate
                        # something other than the mode.
                        self.assertEqual(p.stdout.count("FINDING ["), 1,
                                         p.stdout)
                    else:
                        self.assertFalse(fired, p.stdout)
                        self.assertEqual(p.returncode, exits.CLEAN, p.stdout)
                finally:
                    shutil.rmtree(work, ignore_errors=True)


class TheSkipDoesNotSwallowTheProof(unittest.TestCase):
    """MUST-NOT-MOVE: inside a real checkout the guarded cases RUN.

    A precondition that skips too eagerly turns this repo's own recorded
    instance of the defect into a permanent silent pass — strictly worse than
    the arrangement noise it removes, because a green over a skipped proof is
    indistinguishable from a green over a passing one at every altitude a
    reader looks. So the not-skipped path is asserted rather than assumed,
    at the EFFECT site: the guarded classes are loaded and run, and what is
    read back is unittest's own skip list.

    THIS CLASS DELIBERATELY DOES NOT CARRY THE MIXIN, and that is the whole
    reason it can fire. A precondition that over-fires would skip this arm
    along with everything it grades, and the run would report `OK (skipped)`
    in exactly the arrangement the arm exists for — the guard's own blind
    spot, wearing a pass. So it asks a DIFFERENT instrument whether a
    checkout is here: the filesystem, for `.git` itself, which is a
    directory in a checkout, a file in a worktree, and absent from an
    extracted snapshot. Two measurements that CAN diverge is the point; where
    they do — a `.git` git declines to answer for — this goes red rather than
    quiet, which is the honest verdict on an arrangement nobody should be
    trusting.

    TWO answers are asserted, because a setUpClass that RAISES instead of
    skipping empties the skip list too: nothing skipped, AND every loaded
    case actually ran. `testsRun` is compared against the loader's own count
    rather than a number written here, which would be the same restated
    population this file exists to refuse.

    What is NOT asserted here is that the guarded cases PASS. They assert
    that themselves, in the same run, with their own messages; re-asserting
    it would shadow those messages behind this one — a vaguer failure
    forever, at exactly the site where the specific one was available.
    """

    def setUp(self):
        if not (REPO_ROOT / ".git").exists():
            raise unittest.SkipTest(
                f"no .git at {REPO_ROOT} — the extracted-snapshot "
                "arrangement, where the guarded cases are SUPPOSED to skip. "
                "This arm asserts the not-skipped path and has no "
                "arrangement here; the filesystem is asked rather than git "
                "so that an over-firing predicate cannot silence it")

    def test_every_guarded_case_runs_in_this_repos_own_checkout(self):
        guarded = _guarded_classes()
        self.assertNotIn(
            type(self), guarded,
            "this arm acquired the precondition it grades: an over-firing "
            "predicate would now skip it too, and the whole must-not-move "
            "answer would go silent while the run reported OK")
        self.assertIn(Population, guarded)
        self.assertIn(TheRepoSOwnRecordedInstance, guarded)

        loader = unittest.TestLoader()
        result = unittest.TestResult()
        expected = 0
        for cls in guarded:
            suite = loader.loadTestsFromTestCase(cls)
            loaded = suite.countTestCases()
            self.assertGreater(loaded, 0,
                               f"{cls.__name__} loaded no cases at all, so "
                               "its silence proves nothing")
            expected += loaded
            suite.run(result)

        self.assertEqual([f"{t}: {why}" for t, why in result.skipped], [],
                         "a guarded case skipped inside this repo's OWN "
                         "checkout — the precondition swallowed the very "
                         "proof it exists to keep runnable")
        self.assertEqual(result.testsRun, expected,
                         "the guarded classes loaded "
                         f"{expected} cases and ran {result.testsRun}: a "
                         "precondition that raises rather than skips empties "
                         "the skip list while running nothing")


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
