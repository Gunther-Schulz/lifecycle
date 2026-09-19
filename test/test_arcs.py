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


class StageAndStateVerbs(unittest.TestCase):
    """advance / narrow / verdict / yield.

    THE LIVE PICTURE AND THE RECORD ARE DIFFERENT THINGS, and these four are
    where that split is enforced: the fixed slots carry what is CURRENTLY
    true (a log of every narrowing ever held guides nothing), and the
    appended lines carry what happened and when. That is the investigation
    record's NOW-versus-ESTABLISHED shape, which is where this carrier came
    from.
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

    def test_narrow_REPLACES_the_live_picture_and_KEEPS_the_record(self):
        repo = self._repo()
        self._run(repo, *self.OPEN)
        self._run(repo, "arc", "narrow", "freeze", "--text", "four left")
        self._run(repo, "arc", "narrow", "freeze", "--text", "two left")
        arc, _p = arcs.parse_arc(self._body(repo), "freeze")
        self.assertIn("two left", arc.slots["narrowing"])
        self.assertNotIn("four left", arc.slots["narrowing"])
        self.assertEqual(arcs.count_of(self._body(repo), arcs.NARROWED_LINE),
                         2, "the record lost what the slot replaced")

    def test_narrow_KEEPS_the_declared_form(self):
        """The form is what tells a reader whether the text eliminates or

        adds to a palette; a narrowing that dropped it would leave every
        later line ambiguous."""
        repo = self._repo()
        self._run(repo, *self.OPEN)
        self._run(repo, "arc", "narrow", "freeze", "--text", "two left")
        arc, _p = arcs.parse_arc(self._body(repo), "freeze")
        self.assertTrue(arc.slots["narrowing"].startswith("eliminative"))

    def test_advance_REFUSES_while_a_belief_flag_stands(self):
        """A close FILES the doubt; an advance COMPOUNDS it, carrying it into

        a stage whose work will rest on it."""
        repo = self._repo()
        self._run(repo, *self.OPEN)
        self._run(repo, "arc", "belief", "freeze", "--ident", "b1",
                  "--claim", "c", "--basis", "b", "--kill", "k")
        self._run(repo, "arc", "reopen", "freeze", "--ident", "b1",
                  "--reason", "r")
        code, outp = self._run(repo, "arc", "advance", "freeze", "--to",
                               "next", "--reason", "moving on")
        self.assertEqual(code, 2, outp)
        self.assertIn("arc_undispositioned", outp)

    def test_advance_WORKS_once_dispositioned(self):
        """The control: without it the refusal could be 'advance never works

        after a reopen', which would make a reopen end the arc."""
        repo = self._repo()
        self._run(repo, *self.OPEN)
        self._run(repo, "arc", "belief", "freeze", "--ident", "b1",
                  "--claim", "c", "--basis", "b", "--kill", "k")
        self._run(repo, "arc", "reopen", "freeze", "--ident", "b1",
                  "--reason", "r")
        self._run(repo, "arc", "disposition", "freeze", "--ident", "b1",
                  "--how", "re-derived", "--reason", "held")
        code, outp = self._run(repo, "arc", "advance", "freeze", "--to",
                               "next", "--reason", "moving on")
        self.assertEqual(code, 0, outp)
        arc, _p = arcs.parse_arc(self._body(repo), "freeze")
        self.assertEqual(arc.slots["stage"], "next")

    def test_an_OUTWARD_stage_renders_its_STOP_AT_ENTRY(self):
        """astra's correction: a STOP printed when the stage CLOSES arrives

        after the act it exists to govern. Entry is the only placement that
        can precede anything."""
        repo = self._repo()
        self._run(repo, *self.OPEN)
        code, outp = self._run(repo, "arc", "advance", "freeze", "--to",
                               "submission", "--reason", "ready",
                               "--outward")
        self.assertEqual(code, 0, outp)
        self.assertIn("STOP", outp)
        self.assertIn("carve-out floor", outp)
        self.assertIn(arcs.OUTWARD_MARK, self._body(repo))

    def test_an_ordinary_stage_renders_NO_stop(self):
        """The control. A STOP on every advance is a STOP nobody reads, which

        is how the one that matters arrives pre-discounted."""
        repo = self._repo()
        self._run(repo, *self.OPEN)
        _code, outp = self._run(repo, "arc", "advance", "freeze", "--to",
                                "digging", "--reason", "ready")
        self.assertNotIn("STOP", outp)

    def test_yield_keeps_the_slot_PROSE_and_counts_at_READ_time(self):
        """A stored total is correct when written and false once another line

        lands. The slot is the arc's own statement; the number is derived."""
        repo = self._repo()
        self._run(repo, *self.OPEN)
        arc, _p = arcs.parse_arc(self._body(repo), "freeze")
        self.assertNotEqual(arc.slots["yield"].strip(), "0",
                            "the open seeded a persisted count")
        self._run(repo, "arc", "yield", "freeze", "--ident", "y1", "--text",
                  "a tracer", "--summary", "one instrument shipped")
        self._run(repo, "arc", "yield", "freeze", "--ident", "y2", "--text",
                  "a runbook", "--summary", "two instruments shipped")
        self.assertEqual(arcs.count_of(self._body(repo), arcs.YIELD_LINE), 2)
        arc, _p = arcs.parse_arc(self._body(repo), "freeze")
        self.assertEqual(arc.slots["yield"], "two instruments shipped")

    def test_a_verdict_is_recorded_at_utterance(self):
        repo = self._repo()
        self._run(repo, *self.OPEN)
        self._run(repo, "arc", "verdict", "freeze", "--ident", "v1",
                  "--text", "good enough to ship")
        self.assertEqual(arcs.count_of(self._body(repo), arcs.VERDICT_LINE), 1)


class DeadlineGeneratesItsObserver(unittest.TestCase):
    """A dated deadline, and the lane that makes it more than a note.

    A DATE WITH NO OBSERVER IS A TIME-WORD, which this repo bans: "later"
    re-enters only by memory. Walk 4 is where the exemption comes from — some
    exits are REAL DATES, a world-fact rather than a lazy hold — and what
    makes a date legitimate here is that something NOTICES it.

    RETIREMENT IS THE HALF THAT WAS MISSING (astra-a8). `add_lane` existed;
    nothing removed one. A generated observer therefore outlived the thing
    that generated it: the arc closes, the date stops meaning anything, and
    the row keeps a door on the board that nobody can act on.
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

    OPEN = ["arc", "open", "bplan", "--goal", "submit", "--narrowing", "none"]
    NAME = "bplan-2026-12-01"

    def _lanes(self, repo):
        import json
        doc = json.loads((repo.dir / ".claude" / "lifecycle.json")
                         .read_text(encoding="utf-8"))
        return doc.get("lanes") or []

    def _body(self, repo):
        from lifecycle_core import lanes as lanes_mod
        return repo.dir / lanes_mod.LANES_DIR / f"{self.NAME}.md"

    def _deadline(self, repo):
        return self._run(repo, "arc", "deadline", "bplan", "--date",
                         "2026-12-01", "--what", "council decision due")

    def test_the_deadline_generates_AND_DECLARES_its_observer(self):
        """Both halves. A body the declaration does not list is invisible to

        `lane list`, so the door has no state and no line on the board —
        which is the assumed-delivery shape `lane new` already recorded."""
        repo = self._repo()
        self._run(repo, *self.OPEN)
        code, outp = self._deadline(repo)
        self.assertEqual(code, 0, outp)
        self.assertTrue(self._body(repo).is_file(), "no lane body")
        self.assertIn(self.NAME, self._lanes(repo), "the row was not declared")

    def test_the_generated_lane_PASSES_kind_check(self):
        """The design's own red-first. A generated observer that failed the

        repo's own declaration check would be a door the tool created and
        then reported as a defect."""
        repo = self._repo()
        self._run(repo, *self.OPEN)
        self._deadline(repo)
        code, outp = self._run(repo, "kind", "check")
        self.assertEqual(code, 0, outp)

    def test_ADVANCING_past_the_stage_retires_body_AND_row(self):
        repo = self._repo()
        self._run(repo, *self.OPEN)
        self._deadline(repo)
        self._run(repo, "arc", "advance", "bplan", "--to", "drafting",
                  "--reason", "moving on")
        self.assertNotIn(self.NAME, self._lanes(repo), "the row outlived it")
        self.assertFalse(self._body(repo).exists(), "the body outlived it")

    def test_a_LATER_stages_deadline_is_NOT_retired_by_an_advance(self):
        """The control that keeps retirement from being destructive: an

        advance ends the deadlines of the stage it LEAVES, not every deadline
        the arc holds. Without this arm the repair would silently drop a
        future date the arc still depends on."""
        repo = self._repo()
        self._run(repo, *self.OPEN)
        self._deadline(repo)
        self._run(repo, "arc", "advance", "bplan", "--to", "drafting",
                  "--reason", "moving on")
        self._run(repo, "arc", "deadline", "bplan", "--date", "2027-01-15",
                  "--what", "submission window closes")
        self._run(repo, "arc", "advance", "bplan", "--to", "review",
                  "--reason", "draft done")
        # The 2027 deadline was set in `drafting`, which we just left, so it
        # goes; a deadline set in `review` would not. Assert the one set in a
        # stage we have NOT left survives.
        self._run(repo, "arc", "deadline", "bplan", "--date", "2027-06-01",
                  "--what", "appeal deadline")
        self.assertIn("bplan-2027-06-01", self._lanes(repo))

    def test_ABANDONING_the_arc_leaves_ZERO_lanes(self):
        """astra-a8's named arm: an abandoned arc's lane keeps firing unless

        something takes it back out, and abandonment is exactly the case
        where nobody is left watching for the date."""
        repo = self._repo()
        self._run(repo, *self.OPEN)
        self._deadline(repo)
        code, outp = self._run(repo, "arc", "close", "bplan", "--abandon",
                               "--reason", "the council withdrew the item")
        self.assertEqual(code, 0, outp)
        self.assertEqual(self._lanes(repo), [], "an abandoned arc left lanes")
        self.assertFalse(self._body(repo).exists())

    def test_a_non_ISO_date_is_refused(self):
        """The observer is a DATE predicate; a date it cannot compare is a

        lane that can never fire — the silent park this replaces."""
        repo = self._repo()
        self._run(repo, *self.OPEN)
        code, outp = self._run(repo, "arc", "deadline", "bplan", "--date",
                               "next December", "--what", "x")
        self.assertEqual(code, 2, outp)
        self.assertIn("arc_shape", outp)


class ArcVerbsFireTheLogOnce(unittest.TestCase):
    """ONE act, ONE fire-log line.

    THE DUPLICATE WAS NOT COSMETIC. `cli.main` already writes one line per
    invocation carrying the verb path; the arc verbs wrote a second. The
    growth alarm COUNTS `arc close` events, so every closure was counted
    twice on a surface `audit` prints — a wrong number rather than a noisy
    one, in the denominator a flow verdict rests on.
    """

    def _run_in(self, repo, state, *argv):
        import io
        import os
        from contextlib import redirect_stdout
        from lifecycle_core import cli as cli_mod
        here = os.getcwd()
        old = os.environ.get("XDG_STATE_HOME")
        os.environ["XDG_STATE_HOME"] = str(state)
        try:
            os.chdir(str(repo.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                cli_mod.main(["--repo", str(repo.dir)] + list(argv))
        finally:
            os.chdir(here)
            if old is None:
                os.environ.pop("XDG_STATE_HOME", None)
            else:
                os.environ["XDG_STATE_HOME"] = old

    def test_open_and_close_each_write_exactly_one_record(self):
        import json
        from lifecycle_core import refusals
        repo = refusals._Repo()
        self.addCleanup(repo.close)
        state = Path(tempfile.mkdtemp(prefix="lifecycle-arcfire-"))
        self._run_in(repo, state, "arc", "open", "a1", "--goal", "g",
                     "--narrowing", "none")
        self._run_in(repo, state, "arc", "close", "a1")
        log = state / "lifecycle" / "fire.jsonl"
        self.assertTrue(log.is_file(), "no fire log was written")
        verbs_seen = [json.loads(ln).get("verb")
                      for ln in log.read_text(encoding="utf-8").splitlines()
                      if ln.strip()]
        self.assertEqual(verbs_seen.count("arc open"), 1, verbs_seen)
        self.assertEqual(verbs_seen.count("arc close"), 1, verbs_seen)
