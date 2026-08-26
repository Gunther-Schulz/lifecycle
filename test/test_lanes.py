"""Stage 7's contract, tested where the roster cannot reach it.

The refusal roster proves the REFUSALS — the states that produce a finding.
It cannot prove the states that produce a CLEAN answer, because a row's
control only has to differ from its plant. So the trigger predicate's
reserved-code mapping is asserted here, all three states and both edges,
against a real subprocess.

WHY THE MAPPING IS THE THING WORTH TESTING. `evaluate_trigger` is the one
place the two exit-code contracts meet, and the whole design turns on `>=2`
being BROKEN rather than quiet. A mapping that silently folded 2 into quiet
would leave every board in the system clean forever.
"""

import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import lanes, migrate  # noqa: E402


class TriggerContract(unittest.TestCase):

    def test_zero_is_fire(self):
        self.assertEqual(lanes.evaluate_trigger("exit 0").state, lanes.FIRE)

    def test_one_is_quiet(self):
        self.assertEqual(lanes.evaluate_trigger("exit 1").state, lanes.QUIET)

    def test_two_is_broken_and_not_quiet(self):
        t = lanes.evaluate_trigger("exit 2")
        self.assertEqual(t.state, lanes.BROKEN)
        self.assertNotEqual(t.state, lanes.QUIET)
        self.assertEqual(t.code, 2)

    def test_every_code_above_two_is_broken(self):
        """>=2 is RESERVED, so the mapping is total above the edge — not a
        list of the codes somebody happened to think of."""
        for code in (3, 7, 42, 127):
            with self.subTest(code=code):
                self.assertEqual(lanes.evaluate_trigger(f"exit {code}").state,
                                 lanes.BROKEN)

    def test_a_command_that_does_not_exist_is_broken(self):
        self.assertEqual(
            lanes.evaluate_trigger("no-such-command-b7f3e").state,
            lanes.BROKEN)

    def test_an_empty_predicate_is_broken_not_quiet(self):
        self.assertEqual(lanes.evaluate_trigger("   ").state, lanes.BROKEN)

    def test_a_hung_predicate_is_broken_not_quiet(self):
        """A wait whose two failure modes are indistinguishable is the worst
        instrument shape there is: a hung predicate and a quiet one look the
        same to a waiter, and the quiet reading is the one that renders a
        dead lane clean."""
        t = lanes.evaluate_trigger("sleep 5", timeout=1)
        self.assertEqual(t.state, lanes.BROKEN)
        self.assertIsNone(t.code)

    def test_the_state_is_a_word_not_a_code(self):
        """The two contracts must not be unifiable by accident. Returning the
        integer would let a trigger's `2` be passed where a verb contract's
        `2` is read, and the two mean different things."""
        for cmd in ("exit 0", "exit 1", "exit 2"):
            self.assertIsInstance(lanes.evaluate_trigger(cmd).state, str)

    def test_the_predicate_runs_in_the_repo(self):
        """The cwd is the REPO's, so a repo-relative predicate means what it
        says. The pair is two directories, one holding the marker and one
        not — pinned INSIDE the test, never read off the process's own cwd,
        which the environment is free to change between runs."""
        import tempfile
        with_marker = Path(tempfile.mkdtemp(prefix="lifecycle-trig-yes-"))
        without = Path(tempfile.mkdtemp(prefix="lifecycle-trig-no-"))
        (with_marker / "marker").write_text("x", encoding="utf-8")
        try:
            self.assertEqual(
                lanes.evaluate_trigger("test -f marker", cwd=with_marker).state,
                lanes.FIRE)
            self.assertEqual(
                lanes.evaluate_trigger("test -f marker", cwd=without).state,
                lanes.QUIET)
        finally:
            for d in (with_marker, without):
                subprocess.run(["rm", "-rf", str(d)])


class MigrationClassification(unittest.TestCase):
    """The rules are §4 row 1's. These assert the MAPPING, not the prose."""

    def test_grade_word_does_not_prefix_match(self):
        """`OPEN-BOOKED` must not collapse onto `OPEN`, and `MITIGATE-goal`
        must not become a grade word at all. A substring test here would be
        a prefix match in an equality's costume, silently giving an entry
        another word's rule."""
        read = migrate.read_carrier(
            "## Open\n\n- **OPEN-BOOKED 2026-01-01 — x.** body\n")
        self.assertEqual(len(read.entries), 1)
        migrate.classify(read.entries[0])
        self.assertEqual(read.entries[0].grade_word, "OPEN-BOOKED")
        self.assertIsNone(read.entries[0].grade)

    def test_a_covered_word_maps_and_an_uncovered_one_does_not(self):
        read = migrate.read_carrier(
            "## Open\n\n- **RECORD 2026-01-01 — a.** b\n"
            "- **FLURB 2026-01-01 — c.** d\n")
        for e in read.entries:
            migrate.classify(e)
        self.assertEqual(read.entries[0].grade, "READY")
        self.assertIsNone(read.entries[1].grade)

    def test_an_ungraded_entry_is_new_and_a_prose_bullet_is_not_an_entry(self):
        read = migrate.read_carrier(
            "## Open\n\n- **Watch this thing.** body\n"
            "- Step 1, a prose bullet in a prose section\n")
        self.assertEqual(len(read.entries), 1)
        self.assertEqual(len(read.non_entry_bullets), 1)
        migrate.classify(read.entries[0])
        self.assertIsNone(read.entries[0].grade_word)
        self.assertEqual(read.entries[0].grade, "NEW")

    def test_an_unbolded_grade_led_bullet_is_an_entry(self):
        """The carrier holds two entries written as plain `- DONE …`
        bullets. A rule keyed only on `- **` would drop them silently."""
        read = migrate.read_carrier(
            "## Open\n\n- DONE 2026-01-01 (abc123): a closure that stayed\n")
        self.assertEqual(len(read.entries), 1)
        self.assertEqual(read.non_entry_bullets, [])

    def test_the_grades_section_is_cut_not_migrated(self):
        """§4 row 1 CUTS `## Grades` — the tool owns the vocabulary. Its
        bullets DESCRIBE grade words and are not work items. The first real
        run migrated them as `cf-1` and `cf-2`, which is what a cut nobody
        applied looks like from the other side."""
        read = migrate.read_carrier(
            "## Grades — three since 2026-08-11\n\n"
            "- **READY** — the SCHEDULED HEAD, capped at ten.\n\n"
            "## Open\n\n- **READY 2026-01-01 — real work.** body\n")
        self.assertEqual(len(read.cut_bullets), 1)
        self.assertEqual(len(read.entries), 1)
        self.assertEqual(read.entries[0].section, "Open")

    def test_every_bullet_lands_in_exactly_one_column(self):
        """The identity that makes 'not migrated' visible. A bullet the
        reader simply did not see would leave a gap in the sum rather than
        no trace at all."""
        read = migrate.read_carrier(
            "## Grades — x\n\n- **READY** — a declaration.\n\n"
            "## Open\n\n- **READY 2026-01-01 — real work.** body\n"
            "- Step 1, a prose bullet\n")
        self.assertEqual(
            read.total_bullets,
            len(read.entries) + len(read.non_entry_bullets)
            + len(read.cut_bullets))

    def test_the_parked_branch_is_recorded_as_taken(self):
        """§4 row 1 offers PARKED two dispositions. The second is taken and
        the rule text says WHY, so a reader of the report is not left to
        infer that a typed blocker was looked for."""
        read = migrate.read_carrier("## Open\n\n- **PARKED 2026-01-01 — x.** y\n")
        migrate.classify(read.entries[0])
        self.assertEqual(read.entries[0].grade, "NEW")
        self.assertIn("NO typed blocker is derivable", read.entries[0].rule)


class EvidenceBlockerAndMootClose(unittest.TestCase):
    """Assigned items A and E, exercised through the CLI.

    Neither has a refusal row of its own on the CLEAN paths — a roster row
    proves a REFUSAL, and "the evidence arrived" and "the close recorded the
    moot question" are both clean outcomes. So they are asserted here, or
    they are asserted only in a transcript, which is correct once and gone.
    """

    def _repo(self, blocked_by):
        from lifecycle_core import refusals
        items = refusals.SEED_ITEMS.replace("blocked-by: NONE",
                                            f"blocked-by: {blocked_by}")
        return refusals._Repo(items=items)

    def _run(self, repo, argv):
        import io
        import os
        from contextlib import redirect_stdout
        from lifecycle_core import cli as cli_mod
        here = os.getcwd()
        try:
            os.chdir(str(repo.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(repo.dir)] + argv)
            return code, buf.getvalue()
        finally:
            os.chdir(here)

    def test_item_ready_uses_the_one_trigger_evaluator(self):
        """ITEM A. W1b returned COULD NOT VERIFY here rather than building a
        second evaluator. All three states now come from `lanes`, and the
        mapping is NOT the identity: a predicate that FIRES means the
        evidence ARRIVED, so 0 is UNBLOCKED."""
        for predicate, expect_code, expect_text in (
                ("true", 0, "UNBLOCKED"),
                ("false", 0, "BLOCKED"),
                ("exit 2", 2, "trigger_broken")):
            with self.subTest(predicate=predicate):
                r = self._repo(f"evidence {predicate}")
                try:
                    code, out = self._run(r, ["item", "ready", "xx-1"])
                    self.assertEqual(code, expect_code, out)
                    self.assertIn(expect_text, out)
                    self.assertNotIn("no trigger evaluator", out)
                finally:
                    r.close()

    def test_a_broken_blocker_is_not_reported_as_waiting(self):
        r = self._repo("evidence exit 2")
        try:
            _code, out = self._run(r, ["item", "ready", "xx-1"])
            self.assertIn("blocker is BROKEN", out)
            self.assertNotIn("READY but blocked", out)
        finally:
            r.close()

    def test_close_over_an_unanswered_decision_records_it_moot(self):
        """ITEM E. The close stays UNGUARDED — closing is the desk's act and
        a guard there fires on legitimate work — but the question does not
        stay in the operator's queue after the item that asked it is gone."""
        r = self._repo("decision which window is canonical")
        try:
            code, out = self._run(r, ["item", "close", "xx-1"])
            self.assertEqual(code, 0, out)
            self.assertIn("blocker-moot", out)
            done = (r.dir / "ITEMS-DONE.md").read_text(encoding="utf-8")
            self.assertIn("blocker-moot: which window is canonical", done)
            ledger = (r.dir / "LEDGER.md").read_text(encoding="utf-8")
            self.assertIn("decision: which window is canonical → moot "
                          "(closed by xx-1)", ledger)
        finally:
            r.close()

    def test_a_close_with_no_decision_blocker_records_nothing(self):
        """The control. Without it the annotation could fire on every close
        and this suite would not know."""
        r = self._repo("NONE")
        try:
            code, out = self._run(r, ["item", "close", "xx-1"])
            self.assertEqual(code, 0, out)
            self.assertNotIn("blocker-moot", out)
            self.assertNotIn("blocker-moot",
                             (r.dir / "ITEMS-DONE.md").read_text(encoding="utf-8"))
            self.assertNotIn("decision:",
                             (r.dir / "LEDGER.md").read_text(encoding="utf-8"))
        finally:
            r.close()

    def test_an_item_id_blocker_is_not_made_moot_by_a_close(self):
        """Only a `decision` blocker qualifies. An item-id blocker resolves
        mechanically on its target's DONE and an evidence one is
        re-evaluated each pass — neither is left hanging by a close, so
        annotating them would be noise on every archived body."""
        r = self._repo("evidence true")
        try:
            self._run(r, ["item", "close", "xx-1"])
            self.assertNotIn("blocker-moot",
                             (r.dir / "ITEMS-DONE.md").read_text(encoding="utf-8"))
        finally:
            r.close()


if __name__ == "__main__":
    unittest.main()
