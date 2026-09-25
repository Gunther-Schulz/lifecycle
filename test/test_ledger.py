"""`ledger add` COMMITS its line, or the run is not CLEAN (lc-56).

THE SIBLING OF lc-25, one verb over. lc-25 made every join of `item add`
answer the commit question — `committed:` or `NOT COMMITTED`, never silence —
and `ledger add` never got the same contract: it appended the line, printed
it, and returned CLEAN with ` M LEDGER.md` left in a SHARED work tree.

THAT IS THE ASSUMED-DELIVERY CLASS: it does not fail, it ACCUMULATES. The
consequence is one verb over and silent — `item ready` resolves a `decision`
blocker against a ledger line, so an item reads UNBLOCKED in a tree where the
answer was never committed, and the dirty carrier rides out under the next
co-writer's pathspec commit under their message.

THE COMMITTED BLOB IS THE INSTRUMENT, never the file on disk: the defect
wrote the disk correctly every time, so an assertion over `LEDGER.md` passes
against the build this file exists to refuse. Every arm below reads `git show
HEAD:LEDGER.md`.

AND EVERY LINE KIND IS ASKED. One code path serves all four, but a fix
written into one of the four branches would be a fix for one kind of four and
the other three would keep accumulating — the enumeration is what makes that
visible rather than arguable.

A NEW TEST THAT REDS AS AN *ERROR* PROVES ONLY THAT THE CODE IS NEW. Read
unittest's `failures=` vs `errors=` split per arm: a fixture reaching through
a name the old side does not have dies before any assertion and scores
identically against a build that carries the name and still commits nothing.
Every arm here reaches only through names the OLD build already had (`cli`,
`exits`, the CLI surface), so its red is an assertion FAILURE at the defect.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, exits  # noqa: E402
from lifecycle_core import ledger as ledger_mod  # noqa: E402
from lifecycle_core.refusals import (  # noqa: E402
    EMPTY_DONE, GOOD_FULL_DECLARATION, SEED_ITEMS)


def build(*, track_ledger: bool = True) -> Path:
    """A seeded git repo, the same fixture shape `test_moves.py` uses.

    `track_ledger=False` seeds a repo whose ledger is NOT under version
    control — the arrangement in which the commit CANNOT succeed. It is the
    third answer's fixture: the write lands, the recording step fails, and
    the run must say so rather than returning CLEAN.
    """
    d = Path(tempfile.mkdtemp(prefix="lifecycle-ledger-"))
    run = lambda *a: subprocess.run(a, cwd=str(d), capture_output=True,  # noqa: E731
                                    text=True)
    run("git", "init", "-q", "-b", "main")
    run("git", "config", "core.hooksPath", str(d / ".nohooks"))
    run("git", "config", "user.email", "ledger@lifecycle.invalid")
    run("git", "config", "user.name", "ledger test")
    (d / ".claude").mkdir()
    (d / ".claude" / "lifecycle.json").write_text(
        json.dumps(GOOD_FULL_DECLARATION), encoding="utf-8")
    (d / "LAWS.md").write_text("law\n", encoding="utf-8")
    (d / ".gitignore").write_text("__pycache__/\n*.py[co]\n*.lock\n",
                                  encoding="utf-8")
    (d / "ITEMS.md").write_text(SEED_ITEMS, encoding="utf-8")
    (d / "ITEMS-DONE.md").write_text(EMPTY_DONE, encoding="utf-8")
    if track_ledger:
        (d / "LEDGER.md").write_text("schema: 1\n", encoding="utf-8")
    run("git", "add", "-A")
    run("git", "commit", "-qm", "seed")
    return d


def run_cli(repo: Path, *argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(["--repo", str(repo)] + list(argv))
    return code, buf.getvalue()


def head(d: Path) -> str:
    return subprocess.run(["git", "-C", str(d), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def status(d: Path) -> str:
    subprocess.run(["git", "-C", str(d), "update-index", "--refresh"],
                   capture_output=True, text=True)
    return subprocess.run(["git", "-C", str(d), "status", "--porcelain"],
                          capture_output=True, text=True).stdout


def committed_ledger(d: Path) -> str:
    """`LEDGER.md` AS COMMITTED. The file on disk answers a different
    question, and it answered it correctly throughout the defect."""
    r = subprocess.run(["git", "-C", str(d), "show", "HEAD:LEDGER.md"],
                       capture_output=True, text=True)
    return r.stdout


#: The four kinds and one invocation each, with the SUBSTANCE a reader can
#: find again in the committed blob. Closed on purpose: a kind added to
#: `ledger.KINDS` without an entry here is a kind nothing asks the commit
#: question of.
INVOCATIONS = {
    "superseded": (("ledger", "add", "superseded", "xx-1", "--by", "xx-9",
                    "--reason", "the rotated capture is the real subject"),
                   "superseded: xx-1 by xx-9"),
    "rejected": (("ledger", "add", "rejected", "xx-1",
                  "--approach", "a substring match over the joined list",
                  "--why", "any longer body beginning the same way passes"),
                 "rejected: xx-1"),
    "dropped": (("ledger", "add", "dropped", "xx-1",
                 "--reason", "overtaken by the migration"),
                "dropped: xx-1"),
    "decision": (("ledger", "add", "decision",
                  "--question", "does ledger add commit its own line",
                  "--answer", "it does, and the blob is the proof"),
                 "decision: does ledger add commit its own line"),
}


class LedgerAddCommitsItsOwnWrite(unittest.TestCase):
    """lc-56's named defect, at the CLI altitude the verb operates at."""

    def test_a_decision_line_is_COMMITTED_and_HEAD_MOVES(self):
        """The recorded red, as an assertion.

        Measured at 06d8281 in a private clone: `item add` printed
        `committed: lifecycle: add lc-116` and moved HEAD, while `ledger add
        decision` in the same clone and the same run printed only its line,
        returned CLEAN, left ` M LEDGER.md` and did not move HEAD.
        """
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        before = head(d)
        self.assertEqual(status(d), "", "the fixture did not start clean")

        argv, substance = INVOCATIONS["decision"]
        code, out = run_cli(d, *argv)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("committed: lifecycle: ledger decision", out)
        self.assertNotEqual(head(d), before, out)
        self.assertEqual(status(d), "", out)
        # THE HALF THE DEFECT SATISFIED: the line on disk. Kept so a reader
        # can see that this arm is not it.
        self.assertIn(substance, (d / "LEDGER.md").read_text(encoding="utf-8"))
        # THE HALF IT DID NOT: the line in the commit.
        self.assertIn(substance, committed_ledger(d), out)

    def test_EVERY_line_kind_answers_the_commit_question(self):
        """A fix that commits one kind is a fix for one of four.

        The enumeration is closed over `INVOCATIONS`, so a kind reaching the
        verb without an entry is a missing case rather than a silent pass.
        """
        from lifecycle_core import ledger as ledger_mod
        self.assertEqual(set(INVOCATIONS), set(ledger_mod.KINDS),
                         "a line kind exists that no arm here invokes")
        for kind, (argv, substance) in INVOCATIONS.items():
            with self.subTest(kind=kind):
                d = build()
                self.addCleanup(shutil.rmtree, d, ignore_errors=True)
                before = head(d)
                code, out = run_cli(d, *argv)
                self.assertEqual(code, exits.CLEAN, out)
                self.assertTrue("committed: " in out or "NOT COMMITTED" in out,
                                out)
                self.assertNotEqual(head(d), before, out)
                self.assertEqual(status(d), "", out)
                self.assertIn(substance, committed_ledger(d), out)

    def test_the_commit_is_BY_PATHSPEC_and_leaves_a_co_writer_alone(self):
        """The half "it commits" does not assert.

        The index is SHARED with whatever else runs in this work tree, so a
        ledger write that staged before committing would carry a co-writer's
        uncommitted file out under its own message — the failure
        `commit_paths`'s own docstring names, planted here as a real second
        dirty file rather than argued.
        """
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "LAWS.md").write_text("law\na co-writer's uncommitted line\n",
                                   encoding="utf-8")
        argv, _substance = INVOCATIONS["decision"]
        code, out = run_cli(d, *argv)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn(" M LAWS.md", status(d),
                      "the co-writer's file was swept into this commit")
        names = subprocess.run(
            ["git", "-C", str(d), "show", "--name-only", "--format=", "HEAD"],
            capture_output=True, text=True).stdout.split()
        self.assertEqual(names, ["LEDGER.md"], out)

    def test_an_UNCOMMITTABLE_write_is_a_FINDING_and_never_a_CLEAN(self):
        """The invariant's other half, and the discriminating arm.

        "Commits or says NOT COMMITTED" is satisfied vacuously by a verb that
        can never fail to commit. Here the commit CANNOT succeed — the ledger
        is untracked, so the pathspec matches nothing git knows — and the run
        must report the recording step failing rather than returning CLEAN
        over an uncommitted decision. The line itself still lands: the files
        are consistent, which is exactly what `move_uncommitted` says.
        """
        d = build(track_ledger=False)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        before = head(d)
        argv, substance = INVOCATIONS["decision"]
        code, out = run_cli(d, *argv)
        self.assertNotEqual(code, exits.CLEAN, out)
        self.assertIn("[move_uncommitted]", out)
        self.assertIn("the ledger line", out)
        self.assertEqual(head(d), before, out)
        self.assertIn(substance, (d / "LEDGER.md").read_text(encoding="utf-8"))

    def test_a_REFUSED_line_commits_nothing(self):
        """MUST NOT MOVE: the prose gate still runs BEFORE the write.

        A reason carrying the slot separator is refused, and the refusal is
        unchanged by the commit step — nothing is written, so there is
        nothing to commit and HEAD must not move. Without this arm, a commit
        placed above the gate would pass every assertion above.
        """
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        before = head(d)
        code, out = run_cli(d, "ledger", "add", "decision",
                            "--question", "does the gate still run",
                            "--answer", "it does — and this answer proves it")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[ledger_body]", out)
        self.assertNotIn("committed:", out)
        self.assertEqual(head(d), before, out)
        self.assertEqual(status(d), "", out)


class TheSiblingVerbIsUNCHANGED(unittest.TestCase):
    """MUST NOT MOVE: `item add` behaves exactly as lc-25 left it.

    Asked of an INSTRUMENT INDEPENDENT of the thing on trial — this arm
    exercises the `item add` path, which lc-56 does not touch, so a change
    that "fixed" the ledger by moving `commit_paths` or its message would go
    red here rather than being swallowed.
    """

    ADD = ("item", "add",
           "--requirement", "the serving config is read from defaults — x.md",
           "--goal", "verify", "--write-set", "tools/replay.mjs",
           "--done-criterion", "the gate reads what is serving",
           "--evidence", "MEASURED none yet", "--hunks", "4",
           "--absence", "the decision belongs to a desk this session is not")

    def test_item_add_still_commits_its_own_write_by_pathspec(self):
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, *self.ADD, "--join", "new")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("committed: lifecycle: add xx-2", out)
        self.assertEqual(status(d), "", out)
        names = subprocess.run(
            ["git", "-C", str(d), "show", "--name-only", "--format=", "HEAD"],
            capture_output=True, text=True).stdout.split()
        self.assertEqual(names, ["ITEMS.md"], out)

    def test_item_add_still_honours_no_commit(self):
        """MUST NOT MOVE (lc-116): `item add`'s own flag, which PREDATES the

        ledger's, is untouched by the widening — `--no-commit` still writes
        the carrier, still says NOT COMMITTED, and still leaves the tree
        dirty, exactly as before `ledger add` gained the same escape."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, *self.ADD, "--join", "new", "--no-commit")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("NOT COMMITTED (--no-commit)", out)
        self.assertIn("M ITEMS.md", status(d))


class LedgerAddHonoursNoCommit(unittest.TestCase):
    """lc-116: `ledger add` gains the SAME escape `item add` already has.

    `--no-commit` writes the line and prints the SAME NOT COMMITTED text
    every other verb prints, from the SAME function (`commit_paths`' skip
    branch) — never a second spelling of that sentence. Closed over
    `INVOCATIONS` (lc-56's own enumeration) so a line kind reaching the verb
    without an arm here is a missing case rather than a silent pass.
    """

    def test_EVERY_line_kind_honours_no_commit(self):
        from lifecycle_core import ledger as ledger_mod
        self.assertEqual(set(INVOCATIONS), set(ledger_mod.KINDS),
                         "a line kind exists that no arm here invokes")
        for kind, (argv, substance) in INVOCATIONS.items():
            with self.subTest(kind=kind):
                d = build()
                self.addCleanup(shutil.rmtree, d, ignore_errors=True)
                before = head(d)
                code, out = run_cli(d, *argv, "--no-commit")
                self.assertEqual(code, exits.CLEAN, out)
                self.assertIn("NOT COMMITTED (--no-commit)", out, out)
                self.assertEqual(head(d), before,
                                 "a --no-commit run moved HEAD")
                self.assertIn("M LEDGER.md", status(d), out)
                self.assertIn(substance,
                              (d / "LEDGER.md").read_text(encoding="utf-8"))

    def test_no_commit_leaves_the_line_for_a_LATER_batched_commit(self):
        """The use case that motivated the ask (lc-116's own evidence):

        several ledger lines land uncommitted, then one caller-owned commit
        carries them all together."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        before = head(d)
        run_cli(d, "ledger", "add", "decision", "--question", "q1",
               "--answer", "a1", "--no-commit")
        run_cli(d, "ledger", "add", "decision", "--question", "q2",
               "--answer", "a2", "--no-commit")
        self.assertEqual(head(d), before, "a batched write moved HEAD early")
        r = subprocess.run(["git", "-C", str(d), "commit", "-am",
                            "batched ledger lines"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotEqual(head(d), before)
        blob = committed_ledger(d)
        self.assertIn("decision: q1", blob)
        self.assertIn("decision: q2", blob)


class LedgerAddDecisionRunsTheIntakeJoin(unittest.TestCase):
    """R7 (lc-289): `ledger add decision` runs the SAME rarity join `item
    add` already runs (lc-46), pointed at the ledger's OWN decision
    questions instead of an item's requirement line. `cmd_ledger_add` had NO
    match step before this — a re-decided question could be written twice
    with nobody the wiser.
    """

    #: Four informative tokens shared (retirement, pass, fixed, cadence),
    #: well past `MATCH_MIN_TOKENS` — a discriminating margin, not a
    #: boundary case.
    QUESTION = "is the retirement pass run on a fixed cadence"
    ANSWER = "yes, monthly"
    NEAR_MATCH = "should the retirement pass run on a fixed cadence too"
    #: Shares NO token with QUESTION/NEAR_MATCH — the control shape.
    UNRELATED = "is the plugin cache versioned per pin"

    def _seed(self, d: Path):
        """Append one `decision:` line to the fixture's ledger and commit
        it, so the join has something in the carrier to match against."""
        line = ledger_mod.render(
            "decision", {"question": self.QUESTION, "answer": self.ANSWER})
        text = (d / "LEDGER.md").read_text(encoding="utf-8")
        (d / "LEDGER.md").write_text(text + line + "\n", encoding="utf-8")
        r = subprocess.run(["git", "-C", str(d), "commit", "-am",
                            "seed a decision line"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_RED_FIRST_a_near_match_with_no_join_is_a_FINDING(self):
        """THE RECORDED RED: run against the pre-R7 code (`cmd_ledger_add`
        with no match step), this arm reaches only through names the OLD
        build already had (`cli`, `exits`, the CLI surface) — no new symbol
        this test needs is absent from the old build, so a red there is an
        ASSERTION FAILURE at the defect (`code == exits.CLEAN`, no near-match
        step ever ran) and never an import error. Confirmed by hand against
        this file's HEAD~1 (verbs.py before `_check_decision_join` existed):
        `code=0`, `"committed: lifecycle: ledger decision"` in `out`,
        `"ledger_join_undisposed" not in out` — the exact failure this test
        exists to catch.
        """
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self._seed(d)
        before = head(d)
        code, out = run_cli(d, "ledger", "add", "decision", "--question",
                            self.NEAR_MATCH, "--answer", "yes")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[ledger_join_undisposed]", out)
        self.assertIn("match: LEDGER.md:", out)
        self.assertIn(self.QUESTION, out)
        self.assertEqual(head(d), before, "a refused add moved HEAD")
        self.assertNotIn(self.NEAR_MATCH,
                         (d / "LEDGER.md").read_text(encoding="utf-8"))

    def test_no_match_writes_exactly_as_before(self):
        """MUST NOT MOVE: an unrelated question sees no output added — the
        join is silent where there is nothing to disclose."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self._seed(d)
        before = head(d)
        code, out = run_cli(d, "ledger", "add", "decision", "--question",
                            self.UNRELATED, "--answer", "yes, three kept")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("ledger_join_undisposed", out)
        self.assertIn("committed: lifecycle: ledger decision", out)
        self.assertNotEqual(head(d), before, out)
        self.assertIn(self.UNRELATED,
                      committed_ledger(d))

    def test_join_new_with_absence_writes(self):
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self._seed(d)
        before = head(d)
        code, out = run_cli(
            d, "ledger", "add", "decision", "--question", self.NEAR_MATCH,
            "--answer", "yes", "--join", "new", "--absence",
            "a different scheduling window, not previously decided")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("committed: lifecycle: ledger decision", out)
        self.assertNotEqual(head(d), before, out)
        self.assertIn(self.NEAR_MATCH, committed_ledger(d))

    def test_a_wrong_join_value_is_a_FINDING(self):
        """UNLIKE `item add`, `merge-into` and `supersede` are not accepted
        here — a ledger line is append-only prose, not a body another verb
        can fold or move."""
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self._seed(d)
        before = head(d)
        code, out = run_cli(d, "ledger", "add", "decision", "--question",
                            self.NEAR_MATCH, "--answer", "yes",
                            "--join", "merge-into")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[ledger_join_undisposed]", out)
        self.assertIn("only accepted disposition", out)
        self.assertEqual(head(d), before, out)

    def test_join_new_without_absence_is_a_FINDING(self):
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self._seed(d)
        before = head(d)
        code, out = run_cli(d, "ledger", "add", "decision", "--question",
                            self.NEAR_MATCH, "--answer", "yes",
                            "--join", "new")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[ledger_join_undisposed]", out)
        self.assertIn("named absence", out)
        self.assertEqual(head(d), before, out)


class TheDecisionCapSeparatesPinnedPairs(unittest.TestCase):
    """lc-289 RED-FIRST, on pairs PINNED BY IDENTITY in the pre-repair replay
    (docs/audits/2026-09-24-lc289-replay-pinned.jsonl, commit 6824bf0).

    THE CAP NEEDS ITS CORPUS. In a two-line ledger every shared token is
    kept — nothing else exists to show it common — so a toy fixture cannot
    tell the caps apart. Each arm therefore joins the real fire line against
    the real decisions BEFORE it, read from git at the pinned commit. A
    missing object FAILS rather than skips: a vanished arm is a reach arm
    deleted (lc-198), and a green suite would hide it.
    """

    PINNED_REV = "6824bf0"

    @classmethod
    def setUpClass(cls):
        repo = Path(__file__).resolve().parents[1]
        r = subprocess.run(["git", "-C", str(repo), "show",
                            f"{cls.PINNED_REV}:LEDGER.md"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise AssertionError(f"pinned ledger unreadable at "
                                 f"{cls.PINNED_REV}: {r.stderr.strip()}")
        d = Path(tempfile.mkdtemp(prefix="lifecycle-lc289-"))
        try:
            (d / "LEDGER.md").write_text(r.stdout, encoding="utf-8")
            parsed, why = ledger_mod.read(d / "LEDGER.md")
        finally:
            shutil.rmtree(d, ignore_errors=True)
        assert parsed is not None, why
        cls.decisions = [ln for ln in parsed.lines if ln.kind == "decision"]

    def _shared(self, fire_line, best_line, cap):
        from lifecycle_core import verbs
        i = next(n for n, ln in enumerate(self.decisions)
                 if ln.lineno == fire_line)
        before = self.decisions[:i]
        other = next(ln for ln in before if ln.lineno == best_line)
        want = verbs.requirement_tokens(
            self.decisions[i].slots.get("question", ""))
        its = verbs.requirement_tokens(other.slots.get("question", ""))
        freq = verbs.document_frequency(before, key="question")
        return verbs.informative_tokens(want & its, freq, len(before), its,
                                        max_fraction=cap)

    def test_a_pinned_WEAK_pair_fires_before_the_cap_and_is_silent_after(self):
        from lifecycle_core import verbs
        old = self._shared(37, 33, verbs.MATCH_MAX_DOC_FRACTION)
        new = self._shared(37, 33, verbs.DECISION_MATCH_MAX_DOC_FRACTION)
        self.assertEqual(old, {"path", "scope"})
        self.assertGreaterEqual(len(old), verbs.MATCH_MIN_TOKENS)
        self.assertLess(len(new), verbs.MATCH_MIN_TOKENS, new)

    def test_a_pinned_STRONG_pair_fires_on_both_sides_of_the_cap(self):
        from lifecycle_core import verbs
        old = self._shared(39, 36, verbs.MATCH_MAX_DOC_FRACTION)
        new = self._shared(39, 36, verbs.DECISION_MATCH_MAX_DOC_FRACTION)
        self.assertGreaterEqual(len(old), verbs.MATCH_MIN_TOKENS, old)
        self.assertGreaterEqual(len(new), verbs.MATCH_MIN_TOKENS, new)

    def test_the_JOIN_ITSELF_applies_the_decision_cap(self):
        """Through `decision_candidates`, not the helper: the arms above
        pass each cap explicitly, so they stay green even if the join never
        used the decision cap. This one asks the shipped join."""
        from types import SimpleNamespace
        from lifecycle_core import verbs

        def matches(fire_line):
            i = next(n for n, ln in enumerate(self.decisions)
                     if ln.lineno == fire_line)
            q = self.decisions[i].slots.get("question", "")
            prefix = SimpleNamespace(lines=self.decisions[:i])
            return {ln.lineno for ln, _ in verbs.decision_candidates(prefix, q)}

        self.assertNotIn(33, matches(37))
        self.assertIn(36, matches(39))

    def test_the_item_join_keeps_its_own_cap(self):
        """The decision cap is a PARAMETER, never a change to the shared
        constant: item add still reads the majority line."""
        from lifecycle_core import verbs
        self.assertEqual(verbs.MATCH_MAX_DOC_FRACTION, 0.5)
        self.assertEqual(
            self._shared(37, 33, None),
            self._shared(37, 33, verbs.MATCH_MAX_DOC_FRACTION))


if __name__ == "__main__":
    unittest.main()
