"""Drain wave C, lane C1 — lc-105 and lc-318.

lc-105: `item close` MOVED A BODY OVER A LIVE `evidence` BLOCKER WITHOUT
ASKING THE PREDICATE. The move clears the `blocked-by:` LINE and records
nothing for this type, so two bodies reached the closure home that the next
`item check` reds and no verb can repair: one whose blocker was AMENDED (the
amendment resolves last-wins over the cleared line), and one whose base
blocker carried a `blocker-exercise:` slot (legal only beside an evidence
blocker, now sitting beside NONE).

EVERY RED-FIRST ARM REACHES ONLY THROUGH NAMES THE OLD BUILD ALREADY HAD
(`cli.main`, `exits`, `lanes.evaluate_trigger`, the CLI surface, git), so a
red against the unmodified code is an assertion FAILURE at the defect and
never an import error (law 4).
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
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, exits, lanes  # noqa: E402
from lifecycle_core import ledger as ledger_mod  # noqa: E402
from lifecycle_core import refusals as R  # noqa: E402
from lifecycle_core.refusals import (  # noqa: E402
    EMPTY_DONE, GOOD_FULL_DECLARATION, SEED_ITEMS)


def build(items_text: str = SEED_ITEMS) -> Path:
    """A seeded git repo with every carrier TRACKED and committed."""
    d = Path(tempfile.mkdtemp(prefix="lifecycle-drain-c-c1-"))
    run = lambda *a: subprocess.run(a, cwd=str(d), capture_output=True,  # noqa: E731
                                    text=True)
    run("git", "init", "-q", "-b", "main")
    run("git", "config", "core.hooksPath", str(d / ".nohooks"))
    run("git", "config", "user.email", "c1@lifecycle.invalid")
    run("git", "config", "user.name", "drain c c1")
    (d / ".claude").mkdir()
    (d / ".claude" / "lifecycle.json").write_text(
        json.dumps(GOOD_FULL_DECLARATION), encoding="utf-8")
    (d / "LAWS.md").write_text("law\n", encoding="utf-8")
    (d / ".gitignore").write_text("__pycache__/\n*.py[co]\n*.lock\n*.flag\n",
                                  encoding="utf-8")
    (d / "ITEMS.md").write_text(items_text, encoding="utf-8")
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


def flat(text: str) -> str:
    """Whitespace-normalised, so an assertion on a phrase does not depend on
    where a message happens to wrap."""
    return " ".join(text.split())


#: QUIET (exit 1) until `arrived.flag` exists, then FIRED (exit 0). The flag
#: is git-ignored in `build`, so creating it never dirties the tree.
PREDICATE = "test -e arrived.flag"
#: QUIET at its booking run, so the mint admits it; BROKEN (exit 2, which the
#: evaluator RESERVES) once `broken.flag` exists. A predicate that was broken
#: from the start could not be booked at all.
BREAKABLE = "if test -e broken.flag; then exit 2; fi; test -e arrived.flag"

DONE_CLOSE = ("item", "close", "xx-1", "--met", "none", "--decided", "none")
DROP_CLOSE = ("item", "close", "xx-1", "--drop", "--reason",
              "abandoned before the evidence came")


def amended(predicate: str = PREDICATE) -> Path:
    """xx-1 with the blocker AMENDED onto it by the verb — the booked route."""
    d = build()
    code, out = run_cli(d, "item", "amend", "xx-1", "--blocked-by",
                        f"evidence {predicate}", "--reason",
                        "now waits on a fact a command can settle")
    assert code == exits.CLEAN, out
    return d


def based(predicate: str = PREDICATE) -> Path:
    """xx-1 with the evidence blocker on its BASE line, beside the door's own
    `blocker-exercise:` stamp — the shape `item add` writes."""
    return build(SEED_ITEMS.replace(
        "blocked-by: NONE",
        f"blocked-by: evidence {predicate}\n"
        "blocker-exercise: none-yet 2026-10-07"))


SHAPES = {"amended": amended, "base": based}


class ACloseOverAnEvidenceBlockerAsksThePredicate(unittest.TestCase):
    """lc-105, red-first. Each arm states the defect at its effect site: what
    the NEXT `item check` says about the tree the close left behind."""

    def _repo(self, shape, predicate=PREDICATE):
        d = SHAPES[shape](predicate)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def test_ARRIVED_discharges_with_a_record_the_done_home_reads_back(self):
        for shape in SHAPES:
            with self.subTest(shape=shape):
                d = self._repo(shape)
                (d / "arrived.flag").write_text("here\n", encoding="utf-8")
                code, out = run_cli(d, *DONE_CLOSE)
                self.assertEqual(code, exits.CLEAN, out)
                done = (d / "ITEMS-DONE.md").read_text(encoding="utf-8")
                self.assertIn(f"blocker-moot: evidence {PREDICATE} ", done)
                self.assertIn("arrived", done)
                # THE DEFECT: this exited 2 against a body no verb can amend.
                code, out = run_cli(d, "item", "check")
                self.assertEqual(code, exits.CLEAN, out)
                self.assertEqual(git(d, "status", "--porcelain"), "")

    def test_NOT_ARRIVED_refuses_a_DONE_close_and_moves_nothing(self):
        for shape in SHAPES:
            with self.subTest(shape=shape):
                d = self._repo(shape)
                before = head(d)
                live = (d / "ITEMS.md").read_text(encoding="utf-8")
                code, out = run_cli(d, *DONE_CLOSE)
                self.assertEqual(code, exits.FINDING, out)
                self.assertIn("FINDING [close_over_live_blocker]", out)
                self.assertIn(PREDICATE, out)
                # The two exits the item-id refusal already prints.
                self.assertIn("--blocked-by NONE", out)
                self.assertIn("--drop", out)
                self.assertEqual(head(d), before, "a refused close moved HEAD")
                self.assertEqual(
                    (d / "ITEMS.md").read_text(encoding="utf-8"), live)
                self.assertNotIn(
                    "## xx-1",
                    (d / "ITEMS-DONE.md").read_text(encoding="utf-8"))
                self.assertEqual(git(d, "status", "--porcelain"), "")

    def test_NOT_ARRIVED_under_DROP_records_the_wait_ABANDONED(self):
        """The relayed route (dotfiles, df-34 and df-132): a drop over a live
        evidence blocker landed a body the commit gate then refused."""
        for shape in SHAPES:
            with self.subTest(shape=shape):
                d = self._repo(shape)
                code, out = run_cli(d, *DROP_CLOSE)
                self.assertEqual(code, exits.CLEAN, out)
                done = (d / "ITEMS-DONE.md").read_text(encoding="utf-8")
                self.assertIn("grade: DROPPED", done)
                self.assertIn(f"blocker-moot: evidence {PREDICATE} ", done)
                self.assertIn("dropped", done.split("blocker-moot:", 1)[1])
                self.assertNotIn("the evidence arrived", done)
                code, out = run_cli(d, "item", "check")
                self.assertEqual(code, exits.CLEAN, out)
                self.assertIn("dropped: xx-1",
                              git(d, "show", "HEAD:LEDGER.md"))
                self.assertEqual(git(d, "status", "--porcelain"), "")

    def test_BROKEN_is_COULD_NOT_VERIFY_and_refuses_DONE_and_DROP_alike(self):
        for shape in SHAPES:
            for name, argv in (("done", DONE_CLOSE), ("drop", DROP_CLOSE)):
                with self.subTest(shape=shape, close=name):
                    d = self._repo(shape, BREAKABLE)
                    (d / "broken.flag").write_text("x\n", encoding="utf-8")
                    before = head(d)
                    live = (d / "ITEMS.md").read_text(encoding="utf-8")
                    code, out = run_cli(d, *argv)
                    self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
                    self.assertIn("COULD NOT VERIFY", out)
                    self.assertNotIn("FINDING [", out)
                    self.assertIn("NOT CLOSED", out)
                    self.assertEqual(head(d), before)
                    self.assertEqual(
                        (d / "ITEMS.md").read_text(encoding="utf-8"), live)
                    self.assertEqual(git(d, "status", "--porcelain"), "")

    def test_the_predicate_goes_through_THE_trigger_evaluator_once(self):
        """Never a second body behind the contract: the close must call the
        function `lane list` and `item ready` call, with this predicate, in
        this repo — and once, because a predicate may be slow."""
        d = self._repo("amended")
        real = lanes.evaluate_trigger
        calls = []

        def spy(command, *a, **kw):
            calls.append((command, kw.get("cwd")))
            return real(command, *a, **kw)

        with mock.patch.object(lanes, "evaluate_trigger", spy):
            run_cli(d, *DONE_CLOSE)
        self.assertEqual([c for c, _cwd in calls], [PREDICATE])
        self.assertEqual(Path(calls[0][1]).resolve(), d.resolve())


class WhatTheEvidenceDispositionMustNotMove(unittest.TestCase):
    """lc-105, MUST-NOT-MOVE. Green on the old build and on the new one."""

    def test_CONTROL_an_unblocked_close_evaluates_nothing(self):
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        with mock.patch.object(lanes, "evaluate_trigger",
                               side_effect=AssertionError("no predicate")):
            code, out = run_cli(d, *DONE_CLOSE)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("blocker-moot",
                         (d / "ITEMS-DONE.md").read_text(encoding="utf-8"))
        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)

    def test_a_hand_planted_evidence_blocker_in_the_done_home_still_fires(self):
        """The row's real defect is untouched: a closed body with a live
        blocker and NO record of this predicate."""
        d = build(SEED_ITEMS.replace("baseline: 1", "baseline: 2"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        body = SEED_ITEMS.split("\n\n", 1)[1].replace(
            "## xx-1", "## xx-2").replace("grade: READY", "grade: DONE").replace(
            "blocked-by: NONE", f"blocked-by: evidence {PREDICATE}")
        (d / "ITEMS-DONE.md").write_text(EMPTY_DONE + "\n" + body,
                                         encoding="utf-8")
        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [blocked_in_done_home]", out)

    def test_a_record_of_ANOTHER_predicate_does_not_discharge(self):
        """Equality on the predicate, as for the other two types: a record
        about some other command clears nothing."""
        d = build(SEED_ITEMS.replace("baseline: 1", "baseline: 2"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        body = SEED_ITEMS.split("\n\n", 1)[1].replace(
            "## xx-1", "## xx-2").replace("grade: READY", "grade: DONE")
        body = (body.rstrip("\n") + "\n"
                "amend-reason: 2026-10-07 retyped by hand\n"
                f"amended-blocked-by: 2026-10-07 evidence {PREDICATE}\n"
                "blocker-moot: evidence test -e other.flag (the predicate "
                "exited 0 at this close: the evidence arrived)\n")
        (d / "ITEMS-DONE.md").write_text(EMPTY_DONE + "\n" + body,
                                         encoding="utf-8")
        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [blocked_in_done_home]", out)


class TheDoneHomeMessageNoLongerOverReads(unittest.TestCase):
    """lc-105: the finding said the body "did not arrive here by a close".
    For a blocker type no close records, a body that DID arrive by a close
    reaches this row — so the sentence asserted a provenance it never read."""

    def test_the_message_does_not_assert_the_body_missed_a_close(self):
        d = build(SEED_ITEMS.replace("baseline: 1", "baseline: 2"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        body = SEED_ITEMS.split("\n\n", 1)[1].replace(
            "## xx-1", "## xx-2").replace("grade: READY", "grade: DONE").replace(
            "blocked-by: NONE", "blocked-by: external the vendor ships")
        (d / "ITEMS-DONE.md").write_text(EMPTY_DONE + "\n" + body,
                                         encoding="utf-8")
        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [blocked_in_done_home]", out)
        self.assertNotIn("so it did not arrive here by a close", flat(out))


# --- lc-318 -------------------------------------------------------------------
#
# EVERY CARRIER VERB COMMITS ITS CARRIER BY PATHSPEC, and a pathspec is
# FILE-granular: whatever else sat uncommitted in that file at verb entry rode
# out under the verb's own message. lc-138 refused that for `ledger add`; the
# ruling (LEDGER.md, REFUSE-ON-DIRTY) is extended here to every other verb.

HAND = "a hand note nobody has committed yet"
ROW = "FINDING [carrier_dirty_at_entry]"


def two_items(declaration=None, done=None, items=None) -> Path:
    d = build(items if items is not None else R.TWO_SEED_ITEMS)
    extra = False
    if declaration is not None:
        (d / ".claude" / "lifecycle.json").write_text(
            json.dumps(declaration), encoding="utf-8")
        extra = True
    if done is not None:
        (d / "ITEMS-DONE.md").write_text(done, encoding="utf-8")
        extra = True
    if extra:
        subprocess.run(["git", "-C", str(d), "commit", "-qam", "fixture"],
                       capture_output=True, text=True)
    return d


def plain() -> Path:
    return two_items()


def standby() -> Path:
    return two_items(declaration=R.STANDBY_DECLARATION)


def with_closed() -> Path:
    """Two live items and one closed body, xx-9, the identity balanced."""
    return two_items(
        items=R.TWO_SEED_ITEMS.replace("baseline: 2", "baseline: 3", 1),
        done=R.EMPTY_DONE + R._blocked_block("xx-9", "DONE", "NONE"))


def decision_blocked() -> Path:
    """xx-2 waits on an unanswered decision, so a DONE close ledgers it moot
    — the DONE route into the ledger."""
    head_, one, two = R.TWO_SEED_ITEMS.split("\n\n", 2)
    two = two.replace("blocked-by: NONE",
                      "blocked-by: decision which window is canonical")
    return two_items(items="\n\n".join((head_, one, two)))


def arc_open() -> Path:
    d = plain()
    for argv in (R._ARC_OPEN, R._ARC_BELIEF):
        code, out = run_cli(d, *argv)
        assert code == exits.CLEAN, out
    return d


def arc_reopened() -> Path:
    d = arc_open()
    code, out = run_cli(d, "arc", "reopen", "freeze", "--ident", "b1",
                        "--reason", "a capture contradicts it")
    assert code == exits.CLEAN, out
    return d


def edit(rel: str, old: str | None = None):
    """A hand edit of one tracked file: replace `old` once, or append a line."""
    def apply(d: Path) -> str:
        p = d / rel
        text = p.read_text(encoding="utf-8")
        if old is None:
            p.write_text(text.rstrip("\n") + "\n" + HAND_LINES[rel] + "\n",
                         encoding="utf-8")
        else:
            assert old in text, (rel, old)
            p.write_text(text.replace(old, HAND, 1), encoding="utf-8")
        return rel
    return apply


#: What a hand would plausibly append to each file — WELL-FORMED on purpose,
#: so the refusal under test is the DIRT and never a shape check firing first.
HAND_LINES = {
    "LEDGER.md": f"dropped: zz-7 — {HAND}",
    "arcs/freeze.md": f"premise: p9 2026-10-07 {HAND}",
    "arcs/INDEX": f"# {HAND}",
}

ITEMS_EDIT = edit("ITEMS.md", "none yet")       # xx-1's evidence slot
DONE_EDIT = edit("ITEMS-DONE.md", "none yet")   # xx-9's evidence slot
LEDGER_EDIT = edit("LEDGER.md")
ARC_EDIT = edit("arcs/freeze.md")
INDEX_EDIT = edit("arcs/INDEX")


AMEND = ("item", "amend", "xx-2", "--done-criterion", "two fires per window",
         "--reason", "the criterion moved")
CLOSE = ("item", "close", "xx-2", "--met", "none", "--decided", "none")
DROP = ("item", "close", "xx-2", "--drop", "--reason", "overtaken")
SUPERSEDE = tuple(R.GOOD_ADD) + ("--join", "supersede xx-2", "--reason",
                                 "replaced by the reworked entry")
PREMISE = ("arc", "premise", "freeze", "--ident", "p1", "--text",
           "the capture is representative")
DEADLINE = ("arc", "deadline", "freeze", "--date", "2099-01-01", "--what",
            "the capture window closes")

#: (name, fixture, the hand edit, argv, takes --no-commit). ONE ROW PER VERB
#: AND PER CARRIER IT COMMITS — a verb committing three carriers appears three
#: times, because "checks both before writing either" is a claim about each.
ARMS = [
    ("add over ITEMS", plain, ITEMS_EDIT, tuple(R.GOOD_ADD), True),
    ("add-supersede over ITEMS", plain, ITEMS_EDIT, SUPERSEDE, True),
    ("add-supersede over DONE", with_closed, DONE_EDIT, SUPERSEDE, True),
    ("add-supersede over LEDGER", plain, LEDGER_EDIT, SUPERSEDE, True),
    ("amend over ITEMS", plain, ITEMS_EDIT, AMEND, True),
    ("park over ITEMS", plain, ITEMS_EDIT,
     ("item", "park", "xx-2", "--blocked-by",
      "external the vendor ships a fix"), True),
    ("promote over ITEMS", plain, ITEMS_EDIT,
     ("item", "promote", "xx-2", "--by", "the c1 desk", "--reason",
      "the slots are filled"), True),
    ("bench over ITEMS", standby, ITEMS_EDIT,
     ("item", "bench", "xx-2", "--reason", R._BENCH_REASON), True),
    ("close over ITEMS", plain, ITEMS_EDIT, CLOSE, True),
    ("close over DONE", with_closed, DONE_EDIT, CLOSE, True),
    ("close-moot over LEDGER", decision_blocked, LEDGER_EDIT, CLOSE, True),
    ("drop over ITEMS", plain, ITEMS_EDIT, DROP, True),
    ("drop over DONE", with_closed, DONE_EDIT, DROP, True),
    ("drop over LEDGER", plain, LEDGER_EDIT, DROP, True),
    ("supersede-closure over DONE", with_closed, DONE_EDIT,
     ("item", "supersede-closure", "xx-9", "--ref", "HEAD", "--line",
      "the closure reason was falsified the same hour"), True),
    ("arc open over INDEX", arc_open, INDEX_EDIT,
     ("arc", "open", "thaw", "--goal", "a second question", "--narrowing",
      "eliminative"), False),
    ("arc close over the body", arc_open, ARC_EDIT,
     ("arc", "close", "freeze"), False),
    ("arc close over INDEX", arc_open, INDEX_EDIT,
     ("arc", "close", "freeze"), False),
    ("arc premise", arc_open, ARC_EDIT, PREMISE, True),
    ("arc belief", arc_open, ARC_EDIT,
     ("arc", "belief", "freeze", "--ident", "b2", "--claim", "a second claim",
      "--basis", "one capture", "--kill", "none known"), True),
    ("arc verdict", arc_open, ARC_EDIT,
     ("arc", "verdict", "freeze", "--ident", "v1", "--text",
      "the operator prefers the first form"), True),
    ("arc reopen", arc_open, ARC_EDIT,
     ("arc", "reopen", "freeze", "--ident", "b1", "--reason",
      "a capture contradicts it"), True),
    ("arc disposition", arc_reopened, ARC_EDIT,
     ("arc", "disposition", "freeze", "--ident", "b1", "--how", "re-derived",
      "--reason", "re-run over the new capture"), True),
    ("arc advance", arc_open, ARC_EDIT,
     ("arc", "advance", "freeze", "--to", "measuring", "--reason",
      "the instrument is built"), True),
    ("arc narrow", arc_open, ARC_EDIT,
     ("arc", "narrow", "freeze", "--text", "the GPU path is ruled out"), True),
    ("arc yield", arc_open, ARC_EDIT,
     ("arc", "yield", "freeze", "--ident", "y1", "--text", "one tracer",
      "--summary", "one tracer so far"), True),
    ("arc deadline over the body", arc_open, ARC_EDIT, DEADLINE, True),
]


def snapshot(d: Path) -> dict:
    """Every file outside `.git`, by bytes — "nothing was written" stated
    over the whole tree and not only the carrier the arm dirtied.

    `*.lock` IS LEFT OUT, and it is the one exclusion: the carrier lock is an
    empty, git-ignored file the verb creates in order to ASK the question
    under mutual exclusion. It is the instrument, not a write to a carrier.
    """
    return {str(p.relative_to(d)): p.read_bytes()
            for p in sorted(d.rglob("*"))
            if p.is_file() and ".git" not in p.relative_to(d).parts
            and p.suffix != ".lock"}


class EveryCarrierVerbRefusesACarrierDirtyAtEntry(unittest.TestCase):
    """lc-318, red-first per verb family: a carrier dirty with an unrelated
    hand edit at verb entry."""

    def test_a_hand_edit_is_NOT_absorbed_and_nothing_is_written(self):
        for name, fixture, dirty, argv, _nc in ARMS:
            with self.subTest(arm=name):
                d = fixture()
                self.addCleanup(shutil.rmtree, d, ignore_errors=True)
                rel = dirty(d)
                before, tree = head(d), snapshot(d)

                code, out = run_cli(d, *argv)

                # THE DEFECT, at the effect site: no commit this verb made
                # carries the hand edit.
                self.assertNotIn(HAND, git(d, "show", f"HEAD:{rel}"),
                                 "the verb's commit carried a hand edit its "
                                 "message does not describe:\n" + out)
                self.assertEqual(head(d), before, "a refused run moved HEAD")
                # NOTHING WAS WRITTEN — the pending edit is intact, and no
                # OTHER carrier this verb commits was touched either.
                self.assertEqual(snapshot(d), tree, out)
                self.assertEqual(code, exits.FINDING, out)
                self.assertIn(ROW, out)
                self.assertIn(rel, out)
                self.assertIn("own message", flat(out))

    def test_CONTROL_the_same_invocation_on_a_clean_tree_commits(self):
        """MUST-NOT-MOVE, and what makes the arm above discriminate: every
        invocation in the table is VALID, so the refusal is the DIRT."""
        for name, fixture, _dirty, argv, _nc in ARMS:
            with self.subTest(arm=name):
                d = fixture()
                self.addCleanup(shutil.rmtree, d, ignore_errors=True)
                before = head(d)
                code, out = run_cli(d, *argv)
                self.assertEqual(code, exits.CLEAN, out)
                self.assertNotIn("carrier_dirty_at_entry", out)
                self.assertEqual(
                    git(d, "rev-list", "--count", f"{before}..HEAD").strip(),
                    "1", out)
                # Everything the verb wrote is in that one commit.
                self.assertEqual(git(d, "status", "--porcelain"), "", out)

    def test_no_commit_is_NOT_refused_over_a_dirty_carrier(self):
        """The ruling's boundary: the batching caller owns that commit, and a
        carrier dirty with its own earlier writes is its ordinary state."""
        for name, fixture, dirty, argv, takes_no_commit in ARMS:
            if not takes_no_commit:
                continue
            with self.subTest(arm=name):
                d = fixture()
                self.addCleanup(shutil.rmtree, d, ignore_errors=True)
                dirty(d)
                before = head(d)
                code, out = run_cli(d, *argv, "--no-commit")
                self.assertEqual(code, exits.CLEAN, out)
                self.assertNotIn("carrier_dirty_at_entry", out)
                self.assertEqual(head(d), before)

    def test_a_STAGED_hand_edit_is_refused_too(self):
        d = plain()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        ITEMS_EDIT(d)
        git(d, "add", "--", "ITEMS.md")
        before = head(d)
        code, out = run_cli(d, *AMEND)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn(ROW, out)
        self.assertEqual(head(d), before)

    def test_CONTROL_a_dirty_SIBLING_file_refuses_nothing(self):
        """The predicate is about the carriers the verb COMMITS. A dirty tree
        elsewhere is the shared-checkout norm."""
        d = plain()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "LAWS.md").write_text("law\nanother\n", encoding="utf-8")
        LEDGER_EDIT(d)   # `item amend` does not commit the ledger
        code, out = run_cli(d, *AMEND)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(
            git(d, "show", "--name-only", "--format=", "HEAD").split(),
            ["ITEMS.md"])
        self.assertNotIn(HAND, git(d, "show", "HEAD:LEDGER.md"))

    def test_after_the_hand_edit_is_committed_the_same_verb_lands(self):
        """The repair the message names works, on one tree."""
        d = plain()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        ITEMS_EDIT(d)
        code, out = run_cli(d, *AMEND)
        self.assertEqual(code, exits.FINDING, out)
        r = subprocess.run(["git", "-C", str(d), "commit", "-qm",
                            "the hand edit, under its own message", "--",
                            "ITEMS.md"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        code, out = run_cli(d, *AMEND)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("two fires per window", git(d, "show", "HEAD:ITEMS.md"))


class TheOrdinaryArcSequenceIsNotRefused(unittest.TestCase):
    """lc-318, the boundary the entry check was drawn at (law 11).

    `arc advance` retires the leaving stage's deadline lanes by rewriting the
    declaration and deleting the lane body, and commits neither. So the
    declaration is dirty, by the tool's own hand, when `arc deadline` next
    runs — and a check that graded it refused this sequence. The declaration
    is therefore NOT in `arc deadline`'s graded set, which the verb says in
    its own comment; what this pins is that the sequence still works. It
    does NOT pin that the leftover is right: that is a separate defect.
    """

    def test_a_deadline_after_an_advance_that_retired_a_lane_still_lands(self):
        d = arc_open()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        for argv in (DEADLINE,
                     ("arc", "advance", "freeze", "--to", "measuring",
                      "--reason", "the instrument is built")):
            code, out = run_cli(d, *argv)
            self.assertEqual(code, exits.CLEAN, out)
        code, out = run_cli(d, "arc", "deadline", "freeze", "--date",
                            "2099-06-01", "--what", "the second window")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("carrier_dirty_at_entry", out)


class AHalfDoneVerbIsNotSweptUpByTheNextOne(unittest.TestCase):
    """The measured incident (dotfiles, relayed on lc-105 and lc-318): a
    close whose commit was refused left its carriers dirty, and the next
    verb — an amend of ANOTHER item — committed ITEMS.md whole, so the
    deletion half of the move rode out under `lifecycle: amend`."""

    def test_the_next_verb_refuses_instead_of_committing_the_deletion(self):
        d = plain()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        hooks = d / ".hooks"
        hooks.mkdir()
        hook = hooks / "pre-commit"
        hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        hook.chmod(0o755)
        git(d, "config", "core.hooksPath", str(hooks))
        code, out = run_cli(d, *CLOSE)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [move_uncommitted]", out)
        # The gate that refused is gone; the half-done move is still on disk.
        git(d, "config", "core.hooksPath", str(d / ".nohooks"))
        before = head(d)

        code, out = run_cli(d, "item", "amend", "xx-1", "--done-criterion",
                            "two fires per window", "--reason",
                            "the criterion moved")

        self.assertIn("## xx-2", git(d, "show", "HEAD:ITEMS.md"),
                      "the next verb's commit carried the deletion half of "
                      "an earlier, uncommitted move:\n" + out)
        self.assertEqual(head(d), before)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn(ROW, out)


class GitUnableToAnswerIsTheThirdAnswer(unittest.TestCase):
    """lc-318: the could-not-verify branch, END TO END. `git status` is made
    to fail for real — a shim on PATH that refuses that one subcommand and
    hands every other to the real git — so the verb runs its own code down
    to the branch, with nothing stubbed inside this package."""

    def _shim(self) -> Path:
        real = shutil.which("git")
        self.assertTrue(real, "no git on PATH")
        box = Path(tempfile.mkdtemp(prefix="lifecycle-drain-c-c1-shim-"))
        self.addCleanup(shutil.rmtree, box, ignore_errors=True)
        shim = box / "git"
        shim.write_text(
            "#!/bin/sh\n"
            'for a in "$@"; do\n'
            '  if [ "$a" = status ]; then\n'
            '    echo "fatal: simulated: git cannot answer" >&2\n'
            "    exit 128\n"
            "  fi\n"
            "done\n"
            f'exec "{real}" "$@"\n', encoding="utf-8")
        shim.chmod(0o755)
        return box

    def test_the_verb_writes_nothing_and_exits_COULD_NOT_VERIFY(self):
        import os
        box = self._shim()
        for name, fixture, argv in (
                ("amend", plain, AMEND),
                ("close", plain, CLOSE),
                ("drop", plain, DROP),
                ("arc premise", arc_open, PREMISE)):
            with self.subTest(arm=name):
                d = fixture()
                self.addCleanup(shutil.rmtree, d, ignore_errors=True)
                before, tree = head(d), snapshot(d)
                path = box.as_posix() + os.pathsep + os.environ.get("PATH", "")
                with mock.patch.dict(os.environ, {"PATH": path}):
                    code, out = run_cli(d, *argv)
                self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
                self.assertIn("COULD NOT VERIFY", out)
                self.assertIn("simulated: git cannot answer", out)
                self.assertNotIn("FINDING [", out)
                self.assertEqual(head(d), before)
                self.assertEqual(snapshot(d), tree, out)

    def test_CONTROL_the_shim_alone_does_not_break_a_no_commit_verb(self):
        """The shim is the variable: a caller that is never asked the dirty
        question runs through it untouched."""
        import os
        box = self._shim()
        d = plain()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        path = box.as_posix() + os.pathsep + os.environ.get("PATH", "")
        with mock.patch.dict(os.environ, {"PATH": path}):
            code, out = run_cli(d, *AMEND, "--no-commit")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("two fires per window",
                      (d / "ITEMS.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
