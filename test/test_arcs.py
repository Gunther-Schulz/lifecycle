"""The arc carrier's own obligations (lc-231).

WHAT THESE GRADE. The roster proves each REFUSAL fires; these cover the
properties whose breakage is SILENT — conservation's two signs, which are two
diagnoses and not one message, and the body shape's per-arc narrowing
declaration, which the walks showed is not universal.

THE SIGNS ARE THE REAL RED HERE. An earlier draft of the design had them
REVERSED (astra-a7), and reversed signs are the worst kind of wrong in this
family: the message still renders, the numbers still appear, and a desk
reading "OVER" over a genuine loss repairs the recoverable case while the
body stays gone. So the pair below is not "conservation notices" — it is
"conservation notices AND calls it by the right name in each direction".
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import arcs  # noqa: E402


class ArcBodyShape(unittest.TestCase):

    def _body(self, **over):
        slots = {"goal": "find the freeze root cause",
                 "stage": "narrowing the thread chain",
                 "narrowing": "eliminative — three candidates left",
                 "premises": "the tracer fires on every frame",
                 "beliefs": "b1: RHIThread blocks first (basis: 11 captures)",
                 "yield": "0"}
        slots.update(over)
        return arcs.render_arc("freeze", slots, 6)

    def test_a_well_formed_body_parses_clean(self):
        _arc, problems = arcs.parse_arc(self._body(), "freeze")
        self.assertEqual(problems, [], problems)

    def test_a_missing_slot_is_a_finding(self):
        text = "\n".join(ln for ln in self._body().splitlines()
                         if not ln.startswith("yield:"))
        _arc, problems = arcs.parse_arc(text, "freeze")
        self.assertTrue(any("yield" in p[2] for p in problems), problems)

    def test_a_duplicated_slot_is_a_finding(self):
        text = self._body() + "stage: a second stage line\n"
        _arc, problems = arcs.parse_arc(text, "freeze")
        self.assertTrue(any("twice" in p[2] for p in problems), problems)

    def test_an_UNDECLARED_narrowing_form_is_a_finding(self):
        """Requirement 3: the form is a per-arc DECLARATION. A reader has to

        know whether the lines under it are eliminations or a palette, and
        walk 2's divergent arc INVERTS the meaning — so an unknown form is a
        state nobody can read, not a cosmetic slip."""
        _arc, problems = arcs.parse_arc(
            self._body(narrowing="convergent — whatever that means"), "freeze")
        self.assertTrue(any("narrowing form" in p[2] for p in problems),
                        problems)

    def test_each_declared_form_is_accepted(self):
        """The control: a check that refused every form would pass the case

        above while making the slot unusable."""
        for form in arcs.NARROWING_FORMS:
            with self.subTest(form=form):
                _arc, problems = arcs.parse_arc(
                    self._body(narrowing=f"{form} — three left"), "freeze")
                self.assertEqual(problems, [], problems)


class ArcConservation(unittest.TestCase):

    def _repo(self, *, baseline=0, opened=0, closed=0,
              live=(), closed_bodies=()):
        d = Path(tempfile.mkdtemp(prefix="lifecycle-arcs-"))
        self.addCleanup(lambda: None)
        (d / arcs.ARCS_DIR).mkdir(parents=True)
        (d / arcs.CLOSED_DIR).mkdir(parents=True)
        arcs.index_path(d).write_text(
            arcs.render_index({"baseline": baseline, "opened": opened,
                               "closed": closed}, 6), encoding="utf-8")
        for slug in live:
            (d / arcs.ARCS_DIR / f"{slug}.md").write_text("x\n",
                                                          encoding="utf-8")
        for slug in closed_bodies:
            (d / arcs.CLOSED_DIR / f"{slug}.md").write_text("x\n",
                                                            encoding="utf-8")
        return d

    def test_agreeing_counters_are_clean(self):
        repo = self._repo(opened=2, closed=1, live=("a",),
                          closed_bodies=("b",))
        got = arcs.conservation(repo)
        self.assertTrue(got.ok, got.message)

    def test_a_body_gone_by_a_path_that_is_not_a_closure_is_SHORT(self):
        """FEWER bodies than admissions. The LOSS side, and the sign is the

        whole assertion: reversed, a desk reads a real loss as the
        recoverable case and repairs the wrong one."""
        repo = self._repo(opened=2, closed=0, live=("a",))
        got = arcs.conservation(repo)
        self.assertFalse(got.ok)
        self.assertEqual(got.sign, "SHORT")
        self.assertIn("LOSS", got.message)

    def test_an_interrupted_close_is_OVER_and_says_it_is_recoverable(self):
        """MORE bodies than admissions. The move appends to the closed home

        before deleting from the live one, so the window between those two
        writes legitimately holds both — that is the design working, and a
        message that told the loss story here would send a desk hunting for
        a body nothing lost."""
        repo = self._repo(opened=1, closed=1, live=("a",),
                          closed_bodies=("a",))
        got = arcs.conservation(repo)
        self.assertFalse(got.ok)
        self.assertEqual(got.sign, "OVER")
        self.assertIn("recoverable", got.message)

    def test_the_closed_counter_and_the_closed_home_are_compared(self):
        """The second invariant. Without it the closed home could drift from

        its counter while the live equation still balanced."""
        repo = self._repo(opened=2, closed=1, live=("a",))
        got = arcs.conservation(repo)
        self.assertFalse(got.ok)

    def test_an_ABSENT_index_is_not_zero(self):
        """A repo that never opened an arc and one whose INDEX was deleted

        are different facts, and answering 0/0/0 for both would report the
        loss case as a clean start."""
        d = Path(tempfile.mkdtemp(prefix="lifecycle-arcs-"))
        idx = arcs.read_index(d)
        self.assertFalse(idx.ok)
        self.assertIn("no arc index", idx.why)
        got = arcs.conservation(d)
        self.assertFalse(got.ok)
        self.assertEqual(got.sign, "unread")


if __name__ == "__main__":
    unittest.main()


class ArcVerbCore(unittest.TestCase):
    """open / status / close, and the ORDER that decides the crash window.

    LAW 9 IS THE SUBJECT HERE, not the happy path. The body and the counter
    move in one act, and WHICH is written first decides what a crash between
    them looks like: body-then-counter leaves a body nothing admitted, which
    conservation reads as OVER and recoverable; counter-then-body would leave
    an admission with no body, which reads SHORT — the LOSS side — over a
    loss that never happened. The window is the same either way; the NAME it
    gets is what a desk acts on.
    """

    def _repo(self):
        from lifecycle_core import refusals
        r = refusals._Repo()
        self.addCleanup(r.close)
        return r

    def _run(self, repo, *argv):
        import io
        import os
        from contextlib import redirect_stdout
        from lifecycle_core import cli as cli_mod
        here = os.getcwd()
        try:
            os.chdir(str(repo.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(repo.dir)] + list(argv))
        finally:
            os.chdir(here)
        return code, buf.getvalue()

    OPEN = ["arc", "open", "freeze", "--goal", "find the root cause",
            "--narrowing", "eliminative"]

    def test_open_then_close_is_a_clean_round_trip(self):
        repo = self._repo()
        code, outp = self._run(repo, *self.OPEN)
        self.assertEqual(code, 0, outp)
        self.assertTrue((repo.dir / "arcs" / "freeze.md").is_file())
        code, outp = self._run(repo, "arc", "close", "freeze")
        self.assertEqual(code, 0, outp)
        self.assertFalse((repo.dir / "arcs" / "freeze.md").exists())
        self.assertTrue((repo.dir / "arcs" / "closed" / "freeze.md").is_file())
        self.assertIn("index agrees", outp)

    def test_the_open_COMMITS_body_and_counter_together(self):
        """A new file is UNTRACKED, and `git commit -- <path>` refuses one.

        Measured on the first end-to-end open: both halves were consistent on
        disk and the commit failed, which is the recording step failing
        rather than the write. Law 9 asks for them to be durable TOGETHER, so
        a green that stopped at 'on disk' would not be the claim."""
        import subprocess
        repo = self._repo()
        self._run(repo, *self.OPEN)
        r = subprocess.run(["git", "-C", str(repo.dir), "status",
                            "--porcelain"], capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), "",
                         f"the open left the tree dirty: {r.stdout!r}")

    def test_a_body_with_no_counter_reads_OVER_not_SHORT(self):
        """THE CRASH WINDOW, constructed rather than crashed. This is the

        state a failure between the two writes leaves, and the assertion is
        the SIGN: recoverable, not loss."""
        repo = self._repo()
        self._run(repo, *self.OPEN)
        # Undo only the counter, leaving the body — exactly the window.
        arcs.index_path(repo.dir).write_text(
            arcs.render_index({"baseline": 0, "opened": 0, "closed": 0}, 6),
            encoding="utf-8")
        got = arcs.conservation(repo.dir)
        self.assertFalse(got.ok)
        self.assertEqual(got.sign, "OVER")

    def test_opening_twice_refuses_rather_than_overwriting(self):
        repo = self._repo()
        self._run(repo, *self.OPEN)
        code, outp = self._run(repo, *self.OPEN)
        self.assertEqual(code, 2, outp)
        self.assertIn("arc_exists", outp)

    def test_an_undeclared_narrowing_form_is_refused_at_the_door(self):
        repo = self._repo()
        code, outp = self._run(
            repo, "arc", "open", "freeze", "--goal", "g",
            "--narrowing", "convergent")
        self.assertEqual(code, 2, outp)
        self.assertIn("arc_shape", outp)

    def test_status_over_a_repo_with_no_arcs_is_CLEAN_not_a_finding(self):
        """Arcs are OPTIONAL. A repo that never wanted one is the ordinary

        case, and a verb that reported a finding there would make every
        zero-arc project carry an alarm about a mechanism it declined."""
        repo = self._repo()
        code, outp = self._run(repo, "arc", "status")
        self.assertEqual(code, 0, outp)
        self.assertIn("NONE", outp)


class ArcShapeAtTheCommitBoundary(unittest.TestCase):
    """The pre-commit hook watches the arc home too (astra-a6).

    WHY THIS ARM RUNS THE HOOK ITSELF. The consumer is a git hook, and its
    subject is the STAGED bytes rather than the working tree — so a fixture
    that called the parser directly would prove the parser and leave the
    thing under test, the hook's reach, unexercised. The hook rejected every
    GLOB home before this, which meant the commit-time boundary stopped
    exactly where the newest carrier began: the three fixed-path carriers
    were guarded and an arc body could be committed in any shape at all.

    THE PLANT IS A HAND-MANGLED BODY, which is the case the guard exists
    for — law 8's "a hand edit that breaks the shape fails at commit". The
    control is a body the VERB wrote, so the pair separates "the hook sees
    arc files" from "the hook fails arc files".
    """

    HOOK = Path(__file__).resolve().parents[1] / "plugin" / "hooks" / "pre-commit"

    def _repo(self):
        import json
        import subprocess
        from lifecycle_core import refusals
        d = Path(tempfile.mkdtemp(prefix="lifecycle-archook-"))
        run = lambda *a: subprocess.run(a, cwd=str(d), capture_output=True,  # noqa: E731
                                        text=True)
        run("git", "init", "-q", "-b", "main")
        run("git", "config", "core.hooksPath", str(d / ".nohooks"))
        run("git", "config", "user.email", "arc@lifecycle.invalid")
        run("git", "config", "user.name", "arc fixture")
        (d / ".claude").mkdir()
        doc = json.loads(json.dumps(refusals.GOOD_FULL_DECLARATION))
        doc["kinds"]["arcs"] = {
            "home": "arcs/*.md", "writer": "verb:arc", "reader": ["session"],
            "staleness": "beliefs by kill-condition",
            "exit": {"action": "move", "recording-act": "arc close"},
            "growth": "bounded-by-exit", "trigger": "verb arc"}
        (d / ".claude" / "lifecycle.json").write_text(json.dumps(doc),
                                                      encoding="utf-8")
        (d / "LAWS.md").write_text("law\n", encoding="utf-8")
        (d / "ITEMS.md").write_text(
            "schema: 6\nbaseline: 0\nadded: 0\ncompacted: 0\n",
            encoding="utf-8")
        (d / "ITEMS-DONE.md").write_text("schema: 6\n", encoding="utf-8")
        (d / "LEDGER.md").write_text("schema: 6\n", encoding="utf-8")
        (d / "arcs").mkdir()
        run("git", "add", "-A")
        run("git", "commit", "-qm", "seed")
        return d, run

    def _hook(self, repo):
        import subprocess
        return subprocess.run([sys.executable, str(self.HOOK)], cwd=str(repo),
                              capture_output=True, text=True)

    def test_a_hand_mangled_arc_body_STOPS_the_commit(self):
        repo, run = self._repo()
        (repo / "arcs" / "freeze.md").write_text(
            "schema: 6\n\n## freeze\ngoal: g\nstage: s\n", encoding="utf-8")
        run("git", "add", "arcs/freeze.md")
        got = self._hook(repo)
        self.assertEqual(got.returncode, 1, got.stderr)
        self.assertIn("arc_shape", got.stderr)

    def test_a_verb_written_arc_body_passes(self):
        """The control. Without it the arm above would pass on a hook that

        failed every arc body, which would make the carrier unusable."""
        repo, run = self._repo()
        (repo / "arcs" / "freeze.md").write_text(
            arcs.render_arc("freeze", {
                "goal": "g", "stage": "s",
                "narrowing": "eliminative — x", "premises": "p",
                "beliefs": "b", "yield": "0"}, 6), encoding="utf-8")
        run("git", "add", "arcs/freeze.md")
        got = self._hook(repo)
        self.assertEqual(got.returncode, 0, got.stderr)

    def test_the_INDEX_is_not_graded_as_a_body(self):
        """It lives inside the arc home and matches its glob, so a reader

        taking the glob at face value would fail the counters file forever."""
        repo, run = self._repo()
        arcs.index_path(repo).parent.mkdir(parents=True, exist_ok=True)
        arcs.index_path(repo).write_text(
            arcs.render_index({"baseline": 0, "opened": 0, "closed": 0}, 6),
            encoding="utf-8")
        run("git", "add", "arcs/INDEX.md")
        got = self._hook(repo)
        self.assertEqual(got.returncode, 0, got.stderr)


class BeliefsAndPropagation(unittest.TestCase):
    """Beliefs, premises, and the reopen that flags every citer.

    THE PROPAGATION IS THE MECHANISM, not the record. A reopen that only
    named its affected beliefs would leave them in an output nobody re-reads
    — the evaporation this carrier exists to stop — so each affected belief
    gets a LINE and the movement verbs consult those lines.
    """

    def _repo(self):
        from lifecycle_core import refusals
        r = refusals._Repo()
        self.addCleanup(r.close)
        return r

    def _run(self, repo, *argv):
        import io
        import os
        from contextlib import redirect_stdout
        from lifecycle_core import cli as cli_mod
        here = os.getcwd()
        try:
            os.chdir(str(repo.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(repo.dir)] + list(argv))
        finally:
            os.chdir(here)
        return code, buf.getvalue()

    OPEN = ["arc", "open", "freeze", "--goal", "g", "--narrowing",
            "eliminative"]

    def _body(self, repo):
        return (repo.dir / "arcs" / "freeze.md").read_text(encoding="utf-8")

    def _seed(self, repo):
        self._run(repo, *self.OPEN)
        self._run(repo, "arc", "belief", "freeze", "--ident", "b1",
                  "--claim", "RHIThread blocks first", "--basis",
                  "11 captures", "--kill", "a capture showing otherwise")
        self._run(repo, "arc", "belief", "freeze", "--ident", "b2",
                  "--claim", "the stall follows b1", "--basis", "derived",
                  "--kill", "b1 dies")

    def test_a_reopen_flags_the_belief_AND_its_citers(self):
        repo = self._repo()
        self._seed(repo)
        code, outp = self._run(repo, "arc", "reopen", "freeze", "--ident",
                               "b1", "--reason", "a 12th capture disagrees")
        self.assertEqual(code, 0, outp)
        self.assertEqual(arcs.undispositioned(self._body(repo)), ["b1", "b2"])

    def test_a_belief_citing_NOTHING_is_not_dragged_in(self):
        """The control for propagation: a reopen must not flag the whole arc,

        or the disposition demand becomes noise and the override reflex it
        would train is what kills a guard (law 11)."""
        repo = self._repo()
        self._run(repo, *self.OPEN)
        self._run(repo, "arc", "belief", "freeze", "--ident", "b1",
                  "--claim", "c", "--basis", "b", "--kill", "k")
        self._run(repo, "arc", "belief", "freeze", "--ident", "b9",
                  "--claim", "unrelated", "--basis", "b", "--kill", "k")
        self._run(repo, "arc", "reopen", "freeze", "--ident", "b1",
                  "--reason", "r")
        self.assertEqual(arcs.undispositioned(self._body(repo)), ["b1"])

    def test_a_disposition_clears_the_flag_and_close_then_works(self):
        repo = self._repo()
        self._seed(repo)
        self._run(repo, "arc", "reopen", "freeze", "--ident", "b1",
                  "--reason", "r")
        code, outp = self._run(repo, "arc", "close", "freeze")
        self.assertEqual(code, 2, outp)
        for ident in ("b1", "b2"):
            self._run(repo, "arc", "disposition", "freeze", "--ident", ident,
                      "--how", "accepted-stale", "--reason",
                      "the arc is closing on other grounds")
        self.assertEqual(arcs.undispositioned(self._body(repo)), [])
        code, outp = self._run(repo, "arc", "close", "freeze")
        self.assertEqual(code, 0, outp)

    def test_LAST_ACT_WINS_so_a_re_reopen_blocks_again(self):
        """A belief can be reopened, answered, and reopened again as evidence

        moves. Reading the FIRST act would freeze an arc on a question
        already answered; reading the last is what makes the flag a live
        state rather than a scar."""
        repo = self._repo()
        self._seed(repo)
        self._run(repo, "arc", "reopen", "freeze", "--ident", "b1",
                  "--reason", "r1")
        self._run(repo, "arc", "disposition", "freeze", "--ident", "b1",
                  "--how", "re-derived", "--reason", "held")
        self._run(repo, "arc", "disposition", "freeze", "--ident", "b2",
                  "--how", "re-derived", "--reason", "held")
        self.assertEqual(arcs.undispositioned(self._body(repo)), [])
        self._run(repo, "arc", "reopen", "freeze", "--ident", "b1",
                  "--reason", "r2, new evidence")
        self.assertIn("b1", arcs.undispositioned(self._body(repo)))

    def test_reopening_a_belief_that_was_never_recorded_REFUSES(self):
        """A flag over a claim nobody made demands a disposition that cannot

        be satisfied honestly."""
        repo = self._repo()
        self._run(repo, *self.OPEN)
        code, outp = self._run(repo, "arc", "reopen", "freeze", "--ident",
                               "b7", "--reason", "r")
        self.assertEqual(code, 2, outp)
        self.assertIn("unknown_arc", outp)

    def test_an_unknown_disposition_word_is_refused(self):
        repo = self._repo()
        self._seed(repo)
        self._run(repo, "arc", "reopen", "freeze", "--ident", "b1",
                  "--reason", "r")
        code, outp = self._run(repo, "arc", "disposition", "freeze",
                               "--ident", "b1", "--how", "noted",
                               "--reason", "r")
        self.assertEqual(code, 2, outp)
        self.assertIn("arc_shape", outp)

    def test_a_premise_is_recorded_apart_from_a_belief(self):
        """Different staleness in kind: a belief dies when its kill-condition

        fires, a premise when the world it came from moves."""
        repo = self._repo()
        self._run(repo, *self.OPEN)
        self._run(repo, "arc", "premise", "freeze", "--ident", "p1",
                  "--text", "the tracer fires on every frame")
        kinds = {r.kind for r in arcs.appended_lines(self._body(repo))}
        self.assertIn(arcs.PREMISE_LINE, kinds)
        self.assertNotIn(arcs.BELIEF_LINE, kinds)
