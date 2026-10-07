"""Drain wave B, lane R1 — lc-138 and lc-211.

lc-138: `ledger add` COMMITTED ITS CARRIER WHOLESALE. The commit is by
pathspec, and a pathspec is FILE-granular: whatever else sat uncommitted in
the ledger at verb entry rode out under `lifecycle: ledger <kind>`, a message
that describes none of it. The ruling (LEDGER.md, REFUSE-ON-DIRTY) is that a
carrier dirty at entry is refused BEFORE anything is written.

lc-211: `lifecycle kind check --repo X` exits 3 — correctly — under a message
that never says the fault is ARGUMENT ORDER.

EVERY ARM REACHES ONLY THROUGH NAMES THE OLD BUILD ALREADY HAD (`cli.main`,
`exits`, the CLI surface, git), so a red against the unmodified code is an
assertion FAILURE at the defect and never an import error (law 4). The one
exception is named where it stands.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, exits  # noqa: E402
from lifecycle_core import ledger as ledger_mod  # noqa: E402
from lifecycle_core.refusals import (  # noqa: E402
    EMPTY_DONE, GOOD_FULL_DECLARATION, SEED_ITEMS)


def build() -> Path:
    """A seeded git repo with a TRACKED, committed ledger."""
    d = Path(tempfile.mkdtemp(prefix="lifecycle-drain-b-r1-"))
    run = lambda *a: subprocess.run(a, cwd=str(d), capture_output=True,  # noqa: E731
                                    text=True)
    run("git", "init", "-q", "-b", "main")
    run("git", "config", "core.hooksPath", str(d / ".nohooks"))
    run("git", "config", "user.email", "r1@lifecycle.invalid")
    run("git", "config", "user.name", "drain b r1")
    (d / ".claude").mkdir()
    (d / ".claude" / "lifecycle.json").write_text(
        json.dumps(GOOD_FULL_DECLARATION), encoding="utf-8")
    (d / "LAWS.md").write_text("law\n", encoding="utf-8")
    (d / ".gitignore").write_text("__pycache__/\n*.py[co]\n*.lock\n",
                                  encoding="utf-8")
    (d / "ITEMS.md").write_text(SEED_ITEMS, encoding="utf-8")
    (d / "ITEMS-DONE.md").write_text(EMPTY_DONE, encoding="utf-8")
    (d / "LEDGER.md").write_text(ledger_mod.head_text(), encoding="utf-8")
    run("git", "add", "-A")
    run("git", "commit", "-qm", "seed")
    return d


def run_cli(repo: Path, *argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(["--repo", str(repo)] + list(argv))
    return code, buf.getvalue()


def git(d: Path, *argv) -> str:
    return subprocess.run(["git", "-C", str(d)] + list(argv),
                          capture_output=True, text=True).stdout


def head(d: Path) -> str:
    return git(d, "rev-parse", "HEAD").strip()


#: One invocation per line kind, with the substance a reader can find again.
#: Closed against `ledger.KINDS` in the arm below: the refusal sits before
#: the write, and a kind reaching the write by another branch would be a
#: kind this file never asked the question of.
INVOCATIONS = {
    "superseded": (("ledger", "add", "superseded", "xx-1", "--by", "xx-9",
                    "--reason", "replaced by the reworked entry"),
                   "superseded: xx-1"),
    "rejected": (("ledger", "add", "rejected", "xx-1",
                  "--approach", "a second spelling of the predicate",
                  "--why", "two bodies behind one contract drift"),
                 "rejected: xx-1"),
    "dropped": (("ledger", "add", "dropped", "xx-1",
                 "--reason", "overtaken by the rework"),
                "dropped: xx-1"),
    "decision": (("ledger", "add", "decision",
                  "--question", "does the ledger verb absorb a hand edit",
                  "--answer", "no"),
                 "decision: does the ledger verb absorb a hand edit"),
}

#: The unrelated hand edit. A well-formed ledger line on purpose: the
#: carrier's own declaration names a session a writer of ledger lines, so
#: this is the LEGITIMATE pending edit of the measured incident and not a
#: malformed file some other check would refuse first.
HAND_EDIT = "dropped: zz-7 — a hand-appended line nobody has committed yet\n"


def hand_edit(d: Path) -> None:
    p = d / "LEDGER.md"
    p.write_text(p.read_text(encoding="utf-8") + HAND_EDIT, encoding="utf-8")


class TheLedgerVerbRefusesADirtyCarrier(unittest.TestCase):
    """lc-138, red-first: a carrier dirty with an unrelated hand edit."""

    def test_the_kinds_enumerated_here_are_the_ledgers_own(self):
        self.assertEqual(set(INVOCATIONS), set(ledger_mod.KINDS),
                         "a line kind exists that no arm here invokes")

    def test_a_hand_edit_is_NOT_absorbed_into_the_verbs_commit(self):
        for kind, (argv, substance) in INVOCATIONS.items():
            with self.subTest(kind=kind):
                d = build()
                self.addCleanup(shutil.rmtree, d, ignore_errors=True)
                hand_edit(d)
                before = head(d)
                on_disk = (d / "LEDGER.md").read_text(encoding="utf-8")

                code, out = run_cli(d, *argv)

                # THE DEFECT, stated at the effect site: the hand edit must
                # not be in any commit this verb made.
                self.assertNotIn("zz-7", git(d, "show", "HEAD:LEDGER.md"),
                                 "the verb's commit carried a hand edit its "
                                 "message does not describe:\n" + out)
                self.assertEqual(head(d), before, "a refused run moved HEAD")
                self.assertEqual(code, exits.FINDING, out)
                self.assertIn("FINDING [ledger_carrier_dirty]", out)
                # The message names the carrier and the repair.
                self.assertIn("LEDGER.md", out)
                self.assertIn("own message", out)
                # NOTHING WAS WRITTEN: the file is byte-identical to what the
                # hand left, so the pending edit is intact and the verb's
                # line is absent.
                self.assertEqual(
                    (d / "LEDGER.md").read_text(encoding="utf-8"), on_disk)
                self.assertNotIn(substance, on_disk)

    def test_a_STAGED_hand_edit_is_refused_too(self):
        """The index is the other place a pending edit sits, and a pathspec
        commit takes the working-tree file whatever the index holds."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        hand_edit(d)
        git(d, "add", "--", "LEDGER.md")
        before = head(d)
        code, out = run_cli(d, *INVOCATIONS["dropped"][0])
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [ledger_carrier_dirty]", out)
        self.assertEqual(head(d), before)

    def test_after_the_hand_edit_is_committed_the_same_add_lands(self):
        """The repair the message names actually works — the refusal is the
        DIRT and not the verb, on one tree."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        hand_edit(d)
        argv, substance = INVOCATIONS["dropped"]
        code, out = run_cli(d, *argv)
        self.assertEqual(code, exits.FINDING, out)
        r = subprocess.run(["git", "-C", str(d), "commit", "-qm",
                            "the hand edit, under its own message", "--",
                            "LEDGER.md"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        code, out = run_cli(d, *argv)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn(substance, git(d, "show", "HEAD:LEDGER.md"))


class ACleanCarrierStillCommitsExactlyWhatTheVerbWrote(unittest.TestCase):
    """lc-138, MUST-NOT-MOVE."""

    def test_the_commit_is_exactly_the_verbs_own_line(self):
        for kind, (argv, substance) in INVOCATIONS.items():
            with self.subTest(kind=kind):
                d = build()
                self.addCleanup(shutil.rmtree, d, ignore_errors=True)
                before = head(d)
                code, out = run_cli(d, *argv)
                self.assertEqual(code, exits.CLEAN, out)
                self.assertNotIn("ledger_carrier_dirty", out)
                self.assertNotEqual(head(d), before, "nothing was committed")
                self.assertEqual(
                    git(d, "show", "--name-only", "--format=", "HEAD").split(),
                    ["LEDGER.md"])
                diff = git(d, "show", "--format=", "-U0", "HEAD")
                added = [ln[1:] for ln in diff.splitlines()
                         if ln.startswith("+") and not ln.startswith("+++")]
                removed = [ln for ln in diff.splitlines()
                           if ln.startswith("-") and not ln.startswith("---")]
                self.assertEqual(removed, [], diff)
                self.assertEqual(len(added), 1, diff)
                self.assertTrue(added[0].startswith(substance), diff)
                self.assertEqual(git(d, "status", "--porcelain"), "")

    def test_no_commit_is_NOT_refused_over_a_dirty_carrier(self):
        """The ruling's own boundary: a `--no-commit` caller is batching and
        owns the commit, so a carrier dirty with its own earlier lines is
        that caller's ordinary state."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        before = head(d)
        for q in ("q1", "q2"):
            code, out = run_cli(d, "ledger", "add", "decision", "--question",
                                q, "--answer", "a", "--no-commit")
            self.assertEqual(code, exits.CLEAN, out)
            self.assertNotIn("ledger_carrier_dirty", out)
        self.assertEqual(head(d), before)
        text = (d / "LEDGER.md").read_text(encoding="utf-8")
        self.assertIn("decision: q1", text)
        self.assertIn("decision: q2", text)

    def test_a_dirty_SIBLING_file_does_not_refuse_the_ledger_verb(self):
        """The predicate is about the CARRIER. A dirty tree elsewhere is the
        shared-checkout norm and is exactly what the pathspec commit already
        leaves alone."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "LAWS.md").write_text("law\nanother\n", encoding="utf-8")
        argv, substance = INVOCATIONS["dropped"]
        code, out = run_cli(d, *argv)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn(substance, git(d, "show", "HEAD:LEDGER.md"))
        self.assertIn("M LAWS.md", git(d, "status", "--porcelain"))


class TheDirtyQuestionHasAThirdAnswer(unittest.TestCase):
    """law 1. THIS CLASS REACHES THROUGH A NAME THE OLD BUILD LACKS
    (`verbs.carrier_dirty`), so against unmodified code it reds as an ERROR
    and proves only that the code is new — it is NOT part of lc-138's
    red-first evidence, and is here because "git could not answer" must not
    read as "clean"."""

    def test_git_unable_to_answer_is_neither_clean_nor_dirty(self):
        from lifecycle_core import verbs
        d = Path(tempfile.mkdtemp(prefix="lifecycle-drain-b-r1-nogit-"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "LEDGER.md").write_text("schema: 1\n", encoding="utf-8")
        dirty, why = verbs.carrier_dirty(d, d / "LEDGER.md")
        self.assertIsNone(dirty)
        self.assertTrue(why)

    def test_the_pair_on_a_real_tree(self):
        from lifecycle_core import verbs
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertIs(verbs.carrier_dirty(d, d / "LEDGER.md")[0], False)
        hand_edit(d)
        self.assertIs(verbs.carrier_dirty(d, d / "LEDGER.md")[0], True)


def run_raw(*argv):
    """`cli.main` over argv EXACTLY as typed — no `--repo` prepended, which
    is the whole subject here. A usage error leaves by `SystemExit`, and its
    text goes to stderr; both are returned."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = cli.main(list(argv))
        except SystemExit as exc:
            code = exc.code
    return code, out.getvalue(), err.getvalue()


class TheRepoFlagAfterTheSubcommandNamesFlagOrder(unittest.TestCase):
    """lc-211. The exit code was always right (3, could-not-verify) and is
    asserted in every arm so the repair cannot move it."""

    def test_a_repo_flag_after_the_subcommand_names_ORDER_and_the_spelling(self):
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out, err = run_raw("kind", "check", "--repo", str(d))
        self.assertEqual(code, exits.COULD_NOT_VERIFY, err)
        # RED-FIRST: the unmodified message is argparse's bare
        # "unrecognized arguments: --repo <path>", which names neither.
        self.assertIn("FLAG ORDER", err)
        self.assertIn(f"lifecycle --repo {d} kind check", err)
        # THE PATH IS NOT IMPLICATED, and the message says so rather than
        # leaving the reader to infer it from an absence.
        self.assertIn("was not examined", err)
        self.assertNotIn("is not a directory", out + err)
        self.assertNotIn("unrecognized arguments", err)

    def test_the_equals_form_is_the_same_fault(self):
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, _out, err = run_raw("item", "check", f"--repo={d}")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, err)
        self.assertIn("FLAG ORDER", err)
        self.assertIn(f"lifecycle --repo {d} item check", err)

    def test_a_trailing_repo_flag_with_no_value_still_names_order(self):
        code, _out, err = run_raw("kind", "check", "--repo")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, err)
        self.assertIn("FLAG ORDER", err)
        self.assertIn("lifecycle --repo <path> kind check", err)

    def test_CONTROL_a_bad_path_BEFORE_the_subcommand_still_blames_the_path(self):
        """The arm that proves the new message DISCRIMINATES: here the path
        really is the fault, and the order is right."""
        bad = str(Path(tempfile.gettempdir()) / "lifecycle-drain-b-r1-no-such")
        code, out, err = run_raw("--repo", bad, "kind", "check")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out + err)
        self.assertIn("is not a directory", out)
        self.assertIn(bad, out)
        self.assertNotIn("FLAG ORDER", out + err)

    def test_CONTROL_another_stray_flag_is_still_an_unrecognized_argument(self):
        """MUST NOT MOVE: the order message is for `--repo` alone. A flag no
        parser knows is not an ordering fault and keeps argparse's wording."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, _out, err = run_raw("--repo", str(d), "kind", "check",
                                  "--no-such-flag")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, err)
        self.assertIn("unrecognized arguments: --no-such-flag", err)
        self.assertNotIn("FLAG ORDER", err)

    def test_CONTROL_the_correct_order_runs_the_verb(self):
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out, err = run_raw("--repo", str(d), "ledger", "check")
        self.assertEqual(code, exits.CLEAN, out + err)
        self.assertNotIn("FLAG ORDER", out + err)


if __name__ == "__main__":
    unittest.main()
