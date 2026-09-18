"""`item repair --shape`: the MECHANICAL half of hand-written damage (lc-129).

WHY THESE ARMS RUN THE BINARY. The verb writes a carrier and then commits it,
so the altitude it operates at is the process: argv parse, the file on disk,
the commit, the exit code. A unit-level arm over the transform would leave
every one of those unexercised — the class the guard/checker devbook names.
It is also what makes the red DISCRIMINATING: a build without the verb answers
the same argv and leaves the same file, so each arm below fails as an
ASSERTION about the carrier rather than erroring on a name the old side lacks.

WHY THE FIXTURES ARE SYNTHETIC. The design names dotfiles' `df-196` and
`df-184` as its real fixtures, and the round-trip over a COPY of df-196 was
run and reported at build time. It is not baked in HERE: this repo is public
and carries a leak scan armed before its first commit, so a private carrier's
body is exactly the thing that must not travel into it. The fixtures below
reproduce the SHAPE df-196 and df-184 carry — a wrapped value, an amendment
among the fixed slots, a missing slot, an unknown slot, a closed body still
carrying its blocker — which is the property under test; the private words are
not.

WHAT SEPARATES A REAL BUILD FROM THE NULL ONES. Every repairing arm asserts a
PAIR: the damage is gone AND the word multiset is unchanged. A build that
rewrites the block from its parsed slots would pass the first and fail the
second — and dropping a value it could not re-render is exactly the failure
"NEVER invents" names. Every LISTING arm asserts the file is BYTE-IDENTICAL,
because a listed class whose body moved has been repaired by a verb that was
told not to.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLI = REPO / "plugin" / "cli" / "lifecycle"

sys.path.insert(0, str(REPO / "plugin" / "cli"))

from lifecycle_core import exits, items  # noqa: E402

#: Hooks are pointed at a path that cannot exist: a fixture repo on this
#: machine inherits a GLOBAL `core.hooksPath`, so an un-neutralised commit here
#: would run the operator's whole hook chain against a throwaway tree.
GIT_ENV = ("-c", "core.hooksPath=/nonexistent-lifecycle-test-hooks",
           "-c", "user.email=lane@invalid.example",
           "-c", "user.name=lc-129 fixture")

DECLARATION = {
    "schema": 2,
    "id-prefix": "tt",
    "closure-home": "ITEMS-DONE.md",
    "kinds": {"items": {"home": "ITEMS.md"}},
}

CLEAN_CARRIER = """schema: 2

baseline: 0
added: 1
compacted: 0

## tt-1
grade: READY
requirement: the carrier the tool itself writes — record: LEDGER.md:1
goal: g
write-set: foo.py
done-criterion: d
evidence: none
blocked-by: NONE
"""

EMPTY_DONE = "schema: 2\n"

#: df-196's SHAPE: a wrapped value, and an amendment group sitting between
#: `write-set:` and `done-criterion:` rather than below `blocked-by:`.
WRAPPED_AND_MISPLACED = """schema: 2
baseline: 0
added: 1
compacted: 0

## tt-1
grade: READY
requirement: a value somebody wrapped by hand — record: LEDGER.md:1
goal: g
write-set: foo.py
amend-reason: 2026-09-15 the write-set omitted the realizing file
amended-write-set: 2026-09-15 foo.py, bar.py
done-criterion: the verb joins this value back to one line and the
  continuation carries words that must all survive the join, including
  this third line
evidence: none
blocked-by: NONE
"""

#: df-184's SHAPE: a closed body a hand wrote without `blocked-by:`.
MISSING_SLOT_DONE = """schema: 2

## tt-9
grade: DONE
requirement: closed by hand, one slot short — record: LEDGER.md:2
goal: g
write-set: foo.py
done-criterion: d
evidence: none
"""

#: A closed body still carrying its blocker and no `blocker-moot:` — the third
#: judgment class, and the one whose repair would DELETE a recorded wait.
BLOCKED_IN_DONE = """schema: 2

## tt-9
grade: DONE
requirement: closed without the close verb — record: LEDGER.md:2
goal: g
write-set: foo.py
done-criterion: d
evidence: none
blocked-by: decision was this ever answered
"""

#: An unknown slot, with a wrapped value under a KNOWN one beside it. The two
#: together are what keeps the listing honest: the known value is joined, the
#: unknown slot's own line is not renamed, removed, or moved.
UNKNOWN_SLOT = """schema: 2
baseline: 0
added: 1
compacted: 0

## tt-1
grade: READY
requirement: a block a hand annotated — record: LEDGER.md:1
goal: g
write-set: foo.py
done-criterion: the value wraps here and
  continues on this line
evidence: none
blocked-by: NONE
repair-note: a slot no schema declares
"""

#: lc-135's fourth judgment class: a continuation line after a BLANK line —
#: no unambiguous host to join it to, so `repair_shape` lists it rather than
#: guessing which slot it belongs to. Not one of df-196/df-184's shapes; a
#: fixture confirmed at the desk (2026-09-15) to route to `item_shape`, the
#: same row missing-slot and unknown-slot do.
UNJOINABLE_CONTINUATION = """schema: 2
baseline: 0
added: 1
compacted: 0

## tt-1
grade: READY
requirement: r
goal: g
write-set: foo.py
done-criterion: d

  an orphan continuation after a blank line
evidence: none
blocked-by: NONE
"""

ARCHIVE_CARRIER = """schema: 2

## tt-9
grade: DONE
requirement: a closed body — record: LEDGER.md:2
goal: g
write-set: foo.py
done-criterion: d
evidence: none
blocked-by: NONE

## Archive (pre-migration)

- a hand-written body from before the tool
  wrapped exactly as its author left it
  and never shape-checked
"""


def words(text: str) -> list:
    """The word MULTISET, sorted. `str.split()` collapses every run of
    whitespace, so a join of wrapped lines leaves this value identical and any
    dropped or invented word changes it."""
    return sorted(text.split())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Fixture:
    """A throwaway git repo carrying a declaration and the two carriers."""

    def __init__(self, td, *, carrier=CLEAN_CARRIER, done=EMPTY_DONE,
                 commit=True):
        self.path = Path(td)
        (self.path / ".claude").mkdir()
        (self.path / ".claude" / "lifecycle.json").write_text(
            json.dumps(DECLARATION), encoding="utf-8")
        # THE CARRIER LOCK IS A SIBLING `.lock` FILE and every writing verb
        # here leaves one, which is why this repo's own `.gitignore` carries
        # the pattern with that reasoning beside it. A fixture without it would
        # report transient lock debris as an uncommitted repair.
        (self.path / ".gitignore").write_text("*.lock\n", encoding="utf-8")
        self.git("init", "-q")
        (self.path / "ITEMS.md").write_text(carrier, encoding="utf-8")
        (self.path / "ITEMS-DONE.md").write_text(done, encoding="utf-8")
        if commit:
            self.git("add", "-A")
            self.git("commit", "-qm", "fixture HEAD")

    def git(self, *argv):
        return subprocess.run(("git", "-C", str(self.path)) + GIT_ENV + argv,
                              capture_output=True, text=True, timeout=30)

    def items(self) -> Path:
        return self.path / "ITEMS.md"

    def done(self) -> Path:
        return self.path / "ITEMS-DONE.md"

    def repair(self, *flags):
        """`(code, stdout, stderr)` for the real binary over this repo."""
        p = subprocess.run(
            [sys.executable, str(CLI), "--repo", str(self.path),
             "item", "repair", "--shape", *flags],
            capture_output=True, text=True, timeout=60)
        return p.returncode, p.stdout, p.stderr


class TheMechanicalRepairs(unittest.TestCase):
    """What the verb DOES change — and what must survive it."""

    def test_a_wrapped_value_is_JOINED_and_no_word_is_lost(self):
        with tempfile.TemporaryDirectory() as td:
            f = Fixture(td, carrier=WRAPPED_AND_MISPLACED)
            before = f.items().read_text(encoding="utf-8")
            code, out, err = f.repair("--no-commit")
            after = f.items().read_text(encoding="utf-8")
            self.assertEqual(
                words(before), words(after),
                "the join must preserve the word multiset exactly — a verb "
                f"that re-renders the block drops what it cannot spell.\n{out}")
            self.assertNotIn(
                "\n  continuation carries words", after,
                "the wrapped continuation is still its own line, so no join "
                f"happened.\nstdout:\n{out}\nstderr:\n{err}")
            self.assertIn(
                "done-criterion: the verb joins this value back to one line "
                "and the continuation carries words that must all survive "
                "the join, including this third line", after,
                f"the three lines are not one line.\nstdout:\n{out}")
            self.assertEqual(code, exits.CLEAN,
                             f"nothing was left for judgment.\n{out}\n{err}")

    def test_an_amendment_among_the_fixed_slots_MOVES_below_them(self):
        with tempfile.TemporaryDirectory() as td:
            f = Fixture(td, carrier=WRAPPED_AND_MISPLACED)
            before = f.items().read_text(encoding="utf-8")
            code, out, err = f.repair("--no-commit")
            after = f.items().read_text(encoding="utf-8")
            lines = [ln.split(":", 1)[0] for ln in after.split("\n")
                     if ":" in ln and not ln.startswith(" ")]
            fixed = [i for i, n in enumerate(lines)
                     if n in ("grade", "requirement", "goal", "write-set",
                              "done-criterion", "evidence", "blocked-by")]
            amend = [i for i, n in enumerate(lines)
                     if n == "amend-reason" or n.startswith("amended-")]
            self.assertTrue(amend, f"the amendment lines vanished.\n{after}")
            self.assertGreater(
                min(amend), max(fixed),
                "an amendment still sits among the fixed slots — it was not "
                f"moved.\nstdout:\n{out}\nstderr:\n{err}\n{after}")
            self.assertEqual(words(before), words(after),
                             "the move must not change any word.")
            self.assertEqual(code, exits.CLEAN, f"{out}\n{err}")

    def test_the_amendment_lines_keep_their_FILE_ORDER(self):
        """LAST WINS is read off the file, so a move that reorders two
        amendments changes which value is in force — an invention wearing a
        repair's clothes."""
        carrier = WRAPPED_AND_MISPLACED.replace(
            "blocked-by: NONE\n",
            "blocked-by: NONE\n"
            "amended-write-set: 2026-09-15 foo.py, bar.py, baz.py\n")
        with tempfile.TemporaryDirectory() as td:
            f = Fixture(td, carrier=carrier)
            code, out, err = f.repair("--no-commit")
            after = f.items().read_text(encoding="utf-8")
            first = after.index("2026-09-15 foo.py, bar.py\n")
            second = after.index("2026-09-15 foo.py, bar.py, baz.py")
            self.assertLess(
                first, second,
                "the earlier amendment was moved BELOW the later one, so the "
                f"value in force changed.\nstdout:\n{out}\n{after}")
            self.assertEqual(code, exits.CLEAN, f"{out}\n{err}")


class TheJudgmentClassesAreListedNeverRepaired(unittest.TestCase):
    """The half that must NOT move. Each arm asserts the bytes, not the text:
    a listed class whose body changed has been invented on."""

    def test_a_missing_slot_is_LISTED_and_the_file_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as td:
            f = Fixture(td, done=MISSING_SLOT_DONE)
            before = sha(f.done())
            code, out, err = f.repair("--no-commit")
            self.assertEqual(
                before, sha(f.done()),
                "the done home changed — a missing slot was written in.\n"
                f"stdout:\n{out}\nstderr:\n{err}")
            self.assertIn("missing-slot", out,
                          f"the missing slot was not listed.\n{out}")
            self.assertIn("tt-9", out, f"the listing names no block.\n{out}")
            self.assertIn("blocked-by", out,
                          f"the listing names no slot.\n{out}")
            self.assertEqual(
                code, exits.FINDING,
                f"a listed item is a finding for the desk pass.\n{out}\n{err}")

    def test_a_closed_body_still_blocked_is_LISTED_never_cleared(self):
        with tempfile.TemporaryDirectory() as td:
            f = Fixture(td, done=BLOCKED_IN_DONE)
            before = sha(f.done())
            code, out, err = f.repair("--no-commit")
            self.assertEqual(
                before, sha(f.done()),
                "the blocker was edited out — the wait it records is gone.\n"
                f"stdout:\n{out}\nstderr:\n{err}")
            self.assertIn("closed-still-blocked", out,
                          f"the closed-still-blocked body was not listed.\n"
                          f"{out}")
            self.assertEqual(code, exits.FINDING, f"{out}\n{err}")

    def test_an_unknown_slot_is_LISTED_and_its_line_survives_verbatim(self):
        with tempfile.TemporaryDirectory() as td:
            f = Fixture(td, carrier=UNKNOWN_SLOT)
            code, out, err = f.repair("--no-commit")
            after = f.items().read_text(encoding="utf-8")
            self.assertIn(
                "repair-note: a slot no schema declares", after,
                f"the unknown slot's line did not survive.\n{out}\n{after}")
            self.assertIn("unknown-slot", out,
                          f"the unknown slot was not listed.\n{out}")
            self.assertIn(
                "done-criterion: the value wraps here and continues on this "
                "line", after,
                "the KNOWN slot beside it was not joined — a listing must not "
                f"suppress the mechanical half.\n{out}\n{after}")
            self.assertEqual(
                code, exits.FINDING,
                "a run that repaired AND listed still exits FINDING: the "
                f"listing is the part a caller must act on.\n{out}\n{err}")

    def test_a_CLEAN_carrier_is_left_byte_identical_and_lists_nothing(self):
        """The false-fire probe. A verb that rewrites what the tool itself
        wrote stops the lane (R11)."""
        with tempfile.TemporaryDirectory() as td:
            f = Fixture(td)
            before = sha(f.items()), sha(f.done())
            code, out, err = f.repair("--no-commit")
            self.assertEqual(
                before, (sha(f.items()), sha(f.done())),
                f"a clean carrier was rewritten.\nstdout:\n{out}\n{err}")
            self.assertEqual(code, exits.CLEAN,
                             f"a clean carrier is not a finding.\n{out}\n{err}")

    def test_the_ARCHIVE_section_is_not_touched(self):
        """Those bodies predate the tool and were never meant to satisfy a
        fixed-slot shape — joining their wrapped prose would rewrite history
        the shape check deliberately skips."""
        with tempfile.TemporaryDirectory() as td:
            f = Fixture(td, done=ARCHIVE_CARRIER)
            before = sha(f.done())
            code, out, err = f.repair("--no-commit")
            self.assertEqual(
                before, sha(f.done()),
                f"the archive was rewritten.\nstdout:\n{out}\nstderr:\n{err}")
            self.assertEqual(code, exits.CLEAN, f"{out}\n{err}")


class TheJudgmentCheckerReconciliation(unittest.TestCase):
    """lc-135: `repair_shape`'s judgment classes and `item check`'s residual
    findings, over the SAME (repaired) carrier — pinned in correspondence,
    never merged: a row says WHAT IS WRONG, a judgment class says WHAT THE
    VERB DECLINED TO REPAIR AND WHY.

    The four "agrees" arms below are the item's own real fixtures — the
    exact shapes desk measurement 2026-09-15 found mapping one-to-one on
    copies of dotfiles' carriers (closed-still-blocked -> blocked_in_done_
    home, missing-slot/unknown-slot -> item_shape) — reconciling with zero
    unmatched either way. The two red-first arms after them are
    CONSTRUCTED: `JUDGMENT_TO_ROW` and the checker are each degraded in one
    place, in isolation, to show the reconciliation actually discriminates
    rather than agreeing by construction.
    """

    def test_missing_slot_reconciles_over_the_done_home(self):
        rec = items.reconcile_repair_judgments(
            MISSING_SLOT_DONE, items.check_done_file, prefix="tt")
        self.assertTrue(rec.agrees,
                        f"listed_only={rec.listed_only} "
                        f"residual_only={rec.residual_only}")

    def test_closed_still_blocked_reconciles_over_the_done_home(self):
        rec = items.reconcile_repair_judgments(
            BLOCKED_IN_DONE, items.check_done_file, prefix="tt")
        self.assertTrue(rec.agrees,
                        f"listed_only={rec.listed_only} "
                        f"residual_only={rec.residual_only}")

    def test_unknown_slot_reconciles_over_the_live_home(self):
        rec = items.reconcile_repair_judgments(
            UNKNOWN_SLOT, items.check_file, prefix="tt")
        self.assertTrue(rec.agrees,
                        f"listed_only={rec.listed_only} "
                        f"residual_only={rec.residual_only}")

    def test_unjoinable_continuation_reconciles_over_the_live_home(self):
        """The fourth judgment class, not among the item's own dotfiles
        fixtures but in JUDGMENT_TO_ROW: also routes to item_shape."""
        rec = items.reconcile_repair_judgments(
            UNJOINABLE_CONTINUATION, items.check_file, prefix="tt")
        self.assertTrue(rec.agrees,
                        f"listed_only={rec.listed_only} "
                        f"residual_only={rec.residual_only}")

    def test_a_clean_carrier_reconciles_with_both_lists_empty(self):
        """The false-fire probe for this item: a carrier the tool itself
        wrote lists nothing on either side."""
        rec = items.reconcile_repair_judgments(
            CLEAN_CARRIER, items.check_file, prefix="tt")
        self.assertEqual(rec.listed_only, [])
        self.assertEqual(rec.residual_only, [])
        self.assertTrue(rec.agrees)

    def test_a_judgment_class_with_no_row_surfaces_on_both_sides(self):
        """Red-first (a): a judgment class this repo's own JUDGMENT_TO_ROW
        does not map — simulating a class added with no row — can never
        equal a real finding's (ident, row) pair. `None` is not a row any
        checker emits, so the unmapped judgment lands in listed_only AND
        the residual finding it should have matched, now unmatchable, lands
        in residual_only — both sides diverge, which is the honest answer:
        with no row named, nothing here can say which finding it meant.
        This constructs the degraded mapping directly to prove the
        comparison discriminates, rather than waiting for a future class to
        exist."""
        original = dict(items.JUDGMENT_TO_ROW)
        del items.JUDGMENT_TO_ROW[items.JUDGMENT_BLOCKED_CLOSED]
        try:
            rec = items.reconcile_repair_judgments(
                BLOCKED_IN_DONE, items.check_done_file, prefix="tt")
        finally:
            items.JUDGMENT_TO_ROW.clear()
            items.JUDGMENT_TO_ROW.update(original)
        self.assertFalse(rec.agrees)
        self.assertEqual(rec.listed_only, [("tt-9", None)])
        self.assertEqual(rec.residual_only,
                         [("tt-9", "blocked_in_done_home")])

    def test_a_silenced_checker_row_surfaces_as_listed_only(self):
        """Red-first (b): the checker's row for a judged body goes silent —
        a guard removed at that site — so the judgment is still listed but
        no residual finding matches it any more."""
        def silenced(path, out, prefix=None, text=None, collect=None):
            probe: list = []
            code = items.check_done_file(path, out, prefix=prefix,
                                         text=text, collect=probe)
            collect.extend(f for f in probe
                           if f.row != "blocked_in_done_home")
            return code

        rec = items.reconcile_repair_judgments(
            BLOCKED_IN_DONE, silenced, prefix="tt")
        self.assertFalse(rec.agrees)
        self.assertEqual(rec.listed_only, [("tt-9", "blocked_in_done_home")])
        # THE PAIR: nothing ELSE went dark — the residual side is otherwise
        # unaffected, so residual_only stays empty rather than also firing.
        self.assertEqual(rec.residual_only, [])

    def test_a_checker_row_with_no_judgment_surfaces_as_residual_only(self):
        """The mirror shape: the checker starts reporting a body under a
        reconciled row that `repair_shape` never judges at all — 'a row
        added to the checker with no judgment class'."""
        def widened(path, out, prefix=None, text=None, collect=None):
            code = items.check_done_file(path, out, prefix=prefix,
                                         text=text, collect=collect)
            collect.append(items.Finding(
                "item_shape", "ITEMS-DONE.md", 1,
                "a defect repair_shape never judges", "tt-999"))
            return code

        rec = items.reconcile_repair_judgments(EMPTY_DONE, widened,
                                               prefix="tt")
        self.assertFalse(rec.agrees)
        self.assertEqual(rec.residual_only, [("tt-999", "item_shape")])
        self.assertEqual(rec.listed_only, [])


class TheCommitContract(unittest.TestCase):
    """Every carrier-WRITING verb commits its write or says NOT COMMITTED —
    the lc-41 ruling, uniform across the carrier verbs."""

    def test_a_repairing_run_COMMITS_its_write(self):
        with tempfile.TemporaryDirectory() as td:
            f = Fixture(td, carrier=WRAPPED_AND_MISPLACED)
            code, out, err = f.repair()
            self.assertIn("committed:", out,
                          f"the write was not committed.\n{out}\n{err}")
            status = f.git("status", "--porcelain").stdout
            self.assertEqual(
                status.strip(), "",
                f"the repair is on disk but not in a commit.\n{status}")
            log = f.git("log", "-1", "--format=%s").stdout
            self.assertIn("repair", log.lower(),
                          f"the commit does not name the act.\n{log}")
            self.assertEqual(code, exits.CLEAN, f"{out}\n{err}")

    def test_a_run_with_NOTHING_to_repair_says_NOT_COMMITTED(self):
        with tempfile.TemporaryDirectory() as td:
            f = Fixture(td)
            code, out, err = f.repair()
            self.assertIn(
                "NOT COMMITTED", out,
                "a run that wrote nothing must SAY so — 'it printed no commit "
                f"line' is true of a failed write too.\n{out}\n{err}")
            self.assertEqual(code, exits.CLEAN, f"{out}\n{err}")


if __name__ == "__main__":
    unittest.main()
