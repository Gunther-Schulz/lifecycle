"""`tools/prove-rows.py`'s STARTUP REFUSAL, made re-runnable (lc-144).

WHY THIS FILE EXISTS. The tool rewrites core files and restores them from a
backup taken at startup, so it refuses to start over a mutation target that
already differs from HEAD: residue from a crashed earlier run, or a
co-writer's uncommitted work. Without that refusal the backup captures the
FOREIGN state and the restore writes it back as though it were the original —
which is the measured incident lc-133 was booked from. Until now that refusal
was proven by one executed CLI pair that does not re-run, and a check with no
automated home decays silently. This is its home.

THE ARMS ARE A DISCRIMINATING PAIR OVER ONE FIXTURE, not a single assertion.
The same fixture refuses when its target is dirty and completes the walk when
it is clean, so neither the tool nor the fixture is what separates them — the
dirtiness is. And the dirty arm asserts on the refusal's MESSAGE TEXT, never
on the exit code alone: `prove-rows` exits non-zero for several reasons and a
code-only assertion cannot say which one fired.

WHAT IS STUBBED, AND WHY IT IS NOT THE THING UNDER TEST. `verdicts` and
`sibling_map` read the LIVE roster in a fresh interpreter. Driving them here
would make every arm move with the roster — which is live this wave — and
would spend three interpreter starts per arm to grade a startup predicate
that never reaches them. The `verdicts` stub is still an INSTRUMENT rather
than a constant: it reads the fixture file off disk and reports the row dark
exactly when the mutation is there, so the clean arm's PROVEN verdict is
evidence that the walk really wrote the mutation and really restored it.

NOTHING HERE REACHES FOR A NAME THE PRE-lc-133 BUILD LACKS. `dirty_targets`
and `head_blob` are new; `main`, `MUTATIONS`, `REPO`, `CORE`, `verdicts` and
`sibling_map` are not. A fixture reaching through a new name errors before
any assertion runs, and that red scores identically against a build carrying
the name and doing nothing — so these arms go red at `b387ef0` as assertion
FAILURES.
"""

import contextlib
import hashlib
import importlib.util
import io
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]

#: The fixture module the recorded arrangement mutates. Its condition line is
#: a unique WHOLE LINE and a unique SUBSTRING — the two matchers this tool has
#: worn — so an arm's red can never be the anchor matcher disagreeing with
#: itself across builds.
FIXTURE_MODULE = '''"""A stand-in for a package module carrying one decided condition."""


def decide(flag):
    if flag:
        return "finding"
    return "clean"
'''
ANCHOR = "    if flag:"
REPLACEMENT = "    if False:"
FIXTURE_REL = "plugin/cli/lifecycle_core/probe_mod.py"


def _prove_rows():
    """`tools/prove-rows.py` as a module — its filename is not an identifier.

    The REAL object, never a re-parse of its text: these arms grade the code
    that ships, and a second reading of the same file is a second body that
    can agree with the source while the tool disagrees with both.
    """
    path = REPO / "tools" / "prove-rows.py"
    spec = importlib.util.spec_from_file_location("prove_rows_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TheStartupRefusalOverADirtyMutationTarget(unittest.TestCase):

    def _fixture(self, *, commit_target=True):
        """A throwaway git repo shaped like the tree this tool walks.

        A REAL `git init`, because the predicate under test compares working
        bytes against `git show HEAD:<path>` — a fake would answer whatever
        was hoped for. Hooks are pointed at a directory that does not exist:
        this repo is an instrument, and the machine's global hooks firing
        inside it would be read as the tool's own verdict.
        """
        d = Path(tempfile.mkdtemp(prefix="lc144-prove-rows-"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        core = d / "plugin" / "cli" / "lifecycle_core"
        core.mkdir(parents=True)

        def git(*args):
            r = subprocess.run(("git", "-C", str(d)) + args,
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0,
                             f"the fixture repo could not be built: "
                             f"{args}\n{r.stdout}{r.stderr}")

        git("init", "-q", "-b", "main")
        git("config", "core.hooksPath", str(d / ".nohooks"))
        git("config", "user.email", "lane@lifecycle.invalid")
        git("config", "user.name", "lc-144 arm")
        (d / "README.md").write_text("fixture\n", encoding="utf-8")
        target = core / "probe_mod.py"
        target.write_text(FIXTURE_MODULE, encoding="utf-8")
        if commit_target:
            git("add", "README.md", FIXTURE_REL)
        else:
            # The target stays OUT of HEAD, which is the spec decision this
            # arm pins: the tool cannot establish what it would restore such
            # a file TO, so an unknown baseline is a refusal like any other
            # difference.
            git("add", "README.md")
        git("commit", "-q", "-m", "fixture")
        return d, core, target

    def _run(self, d, core):
        """`main([])` over the fixture, its exit code and everything it said."""
        mod = _prove_rows()
        self._live_during = []
        arrangements = [("probe_row", "probe_mod.py", ANCHOR, REPLACEMENT,
                         "the fixture module's one decided condition")]

        def verdicts(only=None):
            # AN INSTRUMENT, not a constant: it looks at the file the walk
            # writes, so a walk that never mutated returns the baseline
            # signature and the arrangement reports FAILED rather than a
            # PROVEN nobody earned.
            #
            # WHICH TREE IT LOOKS AT IS THE PREMISE, and since lc-163 the
            # walk mutates a COPY and never the live checkout. Read lazily
            # off the tool — `WORK_CORE` is set inside `main()`, after this
            # closure is built — so this stub follows the walk instead of
            # pinning the tree the walk used to write. Left pointed at
            # `core`, it reported every row FAILED: the check's premise had
            # drifted while the check itself still looked sound, which is the
            # anchor class this repo already names.
            # getattr, not attribute access: the red-first proof runs
            # this arm against the PRE-lc-163 tool, which has no such
            # name — and an AttributeError there would be a red that
            # proves the module is old, never that the arm
            # discriminates.
            work = getattr(mod, "WORK_CORE", None)
            watched = Path(work) if work else core
            # RECORDED FOR lc-163's ARM: this closure runs while a mutation
            # is applied, so it is the one moment a test can see what a
            # concurrent READER of the checkout would see.
            self._live_during.append(
                self._sha((core / "probe_mod.py").read_bytes()))
            text = (watched / "probe_mod.py").read_text(encoding="utf-8")
            return {"probe_row": "0/unnamed" if REPLACEMENT in text
                    else "2/named"}

        buf = io.StringIO()
        with mock.patch.object(mod, "REPO", d), \
                mock.patch.object(mod, "CORE", core), \
                mock.patch.object(mod, "MUTATIONS", arrangements), \
                mock.patch.object(mod, "sibling_map",
                                  lambda: {"probe_row": "probe_row"}), \
                mock.patch.object(mod, "verdicts", verdicts), \
                contextlib.redirect_stdout(buf):
            code = mod.main([])
        return code, buf.getvalue(), mod

    @staticmethod
    def _sha(data):
        return hashlib.sha256(data).hexdigest()

    def test_the_same_fixture_refuses_when_dirty_and_walks_when_clean(self):
        """THE PAIR, over ONE fixture, differing in the dirtiness alone.

        Run clean first and the walk completes; add one line to the target and
        the same tool over the same repo refuses. Neither the tool nor the
        fixture separates the arms.
        """
        d, core, target = self._fixture()
        clean_code, clean_out, mod = self._run(d, core)
        self.assertNotIn(
            "REFUSING TO START", clean_out,
            "the tool refused over a target that matches HEAD — an arm that "
            f"refuses everything would score as this one does:\n{clean_out}")
        self.assertIn("[probe_row] PROVEN", clean_out, clean_out)
        self.assertEqual(clean_code, mod.CLEAN, clean_out)

        target.write_text(target.read_text(encoding="utf-8") + "# residue\n",
                          encoding="utf-8")
        dirty_code, dirty_out, _ = self._run(d, core)
        self.assertIn(
            "REFUSING TO START", dirty_out,
            "a target already differing from HEAD was walked anyway: the "
            "backup captures that foreign state and the restore writes it "
            f"back as the original, which is the incident:\n{dirty_out}")
        self.assertEqual(dirty_code, mod.FINDING, dirty_out)

    def test_the_refusal_names_the_path_and_both_sha256s(self):
        """MESSAGE TEXT, never the exit code alone — the tool exits non-zero
        for several reasons and a code cannot say which fired."""
        d, core, target = self._fixture()
        committed = target.read_bytes()
        target.write_text(target.read_text(encoding="utf-8") + "# residue\n",
                          encoding="utf-8")
        working = target.read_bytes()
        self.assertNotEqual(committed, working,
                            "the arrangement did not dirty the target, so "
                            "this arm cannot see the condition it certifies")

        code, out, mod = self._run(d, core)
        self.assertIn("REFUSING TO START", out, out)
        self.assertIn(
            FIXTURE_REL, out,
            f"the refusal did not name the file it is about:\n{out}")
        self.assertIn(
            self._sha(working), out,
            f"the refusal did not print the WORKING sha256:\n{out}")
        self.assertIn(
            self._sha(committed), out,
            f"the refusal did not print the HEAD blob's sha256, so a reader "
            f"cannot tell which side is which:\n{out}")
        self.assertEqual(code, mod.FINDING, out)

    def test_the_refusal_stops_the_walk_rather_than_only_warning(self):
        """THE HARM, and the half a printed warning would not catch.

        What the refusal buys is that no arrangement runs: the backup is
        never taken over the foreign bytes and nothing is written back under
        this tool's hand. A verdict block in the output means the walk
        proceeded anyway.
        """
        d, core, target = self._fixture()
        target.write_text(target.read_text(encoding="utf-8") + "# residue\n",
                          encoding="utf-8")
        _code, out, _mod = self._run(d, core)
        self.assertNotIn(
            "[probe_row]", out,
            "the tool printed the refusal AND walked the arrangement anyway, "
            f"so the refusal is a warning and not a gate:\n{out}")
        self.assertNotIn("BASELINE", out, out)

    def test_a_target_absent_from_head_counts_as_differing(self):
        """The spec decision lc-133's lane made rather than inherited.

        HEAD carrying no blob at the path is not a clean tree: the tool
        cannot establish what it would restore the file TO, and proceeding on
        an unknown baseline is the same hazard by a quieter route.
        """
        d, core, _target = self._fixture(commit_target=False)
        code, out, mod = self._run(d, core)
        self.assertIn("REFUSING TO START", out, out)
        self.assertIn(
            "HEAD carries no blob", out,
            "the refusal fired but reported it as a content difference, so "
            f"the reader is told to compare two shas that do not exist:\n{out}")
        self.assertIn(FIXTURE_REL, out, out)
        self.assertEqual(code, mod.FINDING, out)

    def test_the_clean_walk_restores_the_file_byte_for_byte(self):
        """MUST NOT MOVE: the live target ends at its committed bytes.

        Asserted against the COMMITTED BLOB rather than `git status`, whose
        stat cache keys on (mtime, size) and can report a byte-identical file
        as modified and a same-size edit as clean.

        SINCE lc-163 THE GUARANTEE IS STRONGER THAN THIS ARM CAN SEE: the
        walk mutates a copy, so the live file is not restored — it is never
        written at all. This arm still pins the end state because an end
        state is what a reader of the checkout depends on; what it cannot
        distinguish is restored-correctly from never-touched, and the probe
        that CAN is the hash sampler run during the walk (lc-163's own
        evidence: 3 files diverging under the old tool, 0 under this one,
        same sampler and same arrangements).
        """
        d, core, target = self._fixture()
        before = target.read_bytes()
        code, out, mod = self._run(d, core)
        self.assertEqual(code, mod.CLEAN, out)
        blob = subprocess.run(["git", "-C", str(d), "show", f"HEAD:{FIXTURE_REL}"],
                              capture_output=True).stdout
        self.assertEqual(self._sha(target.read_bytes()), self._sha(blob),
                         "the walk did not restore the target to its "
                         "committed bytes")
        self.assertEqual(before, target.read_bytes())

    def test_the_live_target_is_never_written_DURING_the_walk(self):
        """lc-163 — the window itself, observed from inside it.

        THE END STATE IS NOT THE PROPERTY. A walk that mutates the live file
        and restores it perfectly ends byte-identical, so the restore arm
        above passes either way — and for the whole time it ran, a second
        party reading the checkout saw a source file with one check disabled,
        with nothing marking the window. That is what happened on
        2026-09-18: a peer desk read the tree mid-walk, saw two roster rows
        FAIL, and reported a regression against a commit that was
        deterministically CLEAN.

        So this arm samples from INSIDE the window: the verdict stub runs
        while the mutation is applied, and it records what the LIVE file
        looked like at that instant. Under the in-place tool those samples
        differ from the committed bytes; under the copy they cannot.
        """
        d, core, target = self._fixture()
        before = self._sha(target.read_bytes())
        code, out, mod = self._run(d, core)
        self.assertEqual(code, mod.CLEAN, out)
        self.assertTrue(self._live_during,
                        "nothing sampled from inside the walk — the arm "
                        "proves nothing about the window it names")
        self.assertEqual(set(self._live_during), {before},
                         "the live target differed from its committed bytes "
                         "while the walk ran: a reader of this checkout "
                         "would have seen a disabled check, and the end "
                         "state cannot show it")


if __name__ == "__main__":
    unittest.main()
