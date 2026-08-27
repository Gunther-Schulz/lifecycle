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

import shutil
import subprocess
import sys
import tempfile
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


class LaneFilesOnDisk(unittest.TestCase):
    """lc-13's scan, at the unit the roster row cannot reach.

    The row proves the FINDING. What it cannot prove is the CLEAN side's
    shape — which names the scan returns and which it must not — and those
    are what decide whether the finding over-fires. A scan collecting the
    wrong shape would report doors the declaration could never have named
    (R11: a guard firing on legitimate work stops the lane).
    """

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="lifecycle-lanescan-"))

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_no_lanes_directory_is_an_empty_answer_not_an_error(self):
        self.assertEqual(lanes.lane_files_on_disk(self.dir), [])

    def test_it_returns_stems_sorted(self):
        (self.dir / lanes.LANES_DIR).mkdir()
        for name in ("zeta", "alpha"):
            (self.dir / lanes.LANES_DIR / f"{name}.md").write_text(
                lanes.lane_stub(name), encoding="utf-8")
        self.assertEqual(lanes.lane_files_on_disk(self.dir),
                         ["alpha", "zeta"])

    def test_it_collects_only_what_read_lane_could_resolve(self):
        """THE MUST-NOT ROW. `read_lane` resolves a declared name to
        `lanes/<name>.md` and nothing else, so anything the scan collects
        beyond that shape is a door no declaration could ever have named —
        the scan would demand the repo declare a README or a directory."""
        d = self.dir / lanes.LANES_DIR
        d.mkdir()
        (d / "real.md").write_text(lanes.lane_stub("real"), encoding="utf-8")
        (d / "notes.txt").write_text("not a lane\n", encoding="utf-8")
        (d / "README").write_text("not a lane\n", encoding="utf-8")
        (d / "nested.md").mkdir()          # a DIRECTORY whose name ends .md
        self.assertEqual(lanes.lane_files_on_disk(self.dir), ["real"])


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


class DecisionBlockerResolvesAgainstTheLedger(unittest.TestCase):
    """lc-26 — `item ready` re-derives a decision blocker FROM THE LEDGER.

    No verb ever took a decision blocker off an item: `item park` only SETS
    one, and `item --help` listed no verb that cleared one. So an ANSWERED
    question left the item reading blocked forever, and — the half that
    decides whether this ships — it read byte-identically to a question
    nobody had answered. Every test below therefore comes in a PAIR over the
    same item: answered against unanswered, differing in the ledger alone.

    These are CLEAN outcomes, not refusals, so they have no roster row — the
    same reason the class above gives.
    """

    QUESTION = "which window is canonical"

    def _repo(self, ledger_lines=()):
        from lifecycle_core import refusals
        items = refusals.SEED_ITEMS.replace(
            "blocked-by: NONE", f"blocked-by: decision {self.QUESTION}")
        return refusals._Repo(
            items=items,
            ledger_text="schema: 2\n"
                        + "".join(ln + "\n" for ln in ledger_lines))

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

    def test_an_ANSWERED_decision_reads_unblocked(self):
        r = self._repo([f"decision: {self.QUESTION} → the rotated one"])
        try:
            code, out = self._run(r, ["item", "ready", "xx-1"])
            self.assertEqual(code, 0, out)
            self.assertIn("UNBLOCKED", out)
            self.assertIn("the rotated one", out)
            self.assertIn("READY and unblocked", out)
        finally:
            r.close()

    def test_the_SAME_item_with_no_answering_line_stays_blocked(self):
        """THE PAIR. Without it "unblocked" is indistinguishable from a
        branch that unblocks every decision blocker it sees."""
        r = self._repo()
        try:
            code, out = self._run(r, ["item", "ready", "xx-1"])
            self.assertEqual(code, 0, out)
            self.assertIn("BLOCKED — in the OPERATOR's court", out)
            self.assertNotIn("UNBLOCKED", out)
        finally:
            r.close()

    def test_a_decision_line_naming_ANOTHER_question_does_not_clear_it(self):
        """The over-fire arm. A ledger accumulates decisions, and a reader
        that matched loosely would clear a blocker the operator never
        answered — an item scheduled on a question still open."""
        r = self._repo(["decision: which capture is canonical → the rotated one"])
        try:
            _code, out = self._run(r, ["item", "ready", "xx-1"])
            self.assertIn("BLOCKED — in the OPERATOR's court", out)
        finally:
            r.close()

    def test_a_PREFIX_of_the_question_does_not_clear_it(self):
        """A containment match would let a shorter question answer a longer
        one. The comparison is exact after a strip, and this is the case that
        tells the two apart."""
        r = self._repo(["decision: which window → the rotated one"])
        try:
            _code, out = self._run(r, ["item", "ready", "xx-1"])
            self.assertIn("BLOCKED — in the OPERATOR's court", out)
        finally:
            r.close()

    def test_the_answer_PROSE_quoting_a_question_does_not_clear_it(self):
        """Anchored on the SLOT, never on the word appearing anywhere in the
        line — the reason `rejected_for` states one function up."""
        r = self._repo([f"decision: which capture is canonical → deferred "
                        f"until {self.QUESTION} is settled"])
        try:
            _code, out = self._run(r, ["item", "ready", "xx-1"])
            self.assertIn("BLOCKED — in the OPERATOR's court", out)
        finally:
            r.close()

    def test_an_UNREADABLE_ledger_is_could_not_verify_not_blocked(self):
        """Three answers. Reporting BLOCKED over a ledger nobody could read
        is a wait nobody checked, which is the number shaped like a pass."""
        r = self._repo()
        try:
            (r.dir / "LEDGER.md").unlink()
            code, out = self._run(r, ["item", "ready", "xx-1"])
            self.assertEqual(code, 3, out)
            self.assertIn("COULD NOT VERIFY", out)
        finally:
            r.close()

    def test_the_head_reads_the_ledger_too(self):
        """`item ready --head` derives schedulability from the same state, so
        an answered decision has to reach the board as well as the single-item
        verb — a head that still called it blocked would leave the item
        invisible to the one reader that schedules."""
        r = self._repo([f"decision: {self.QUESTION} → the rotated one"])
        try:
            code, out = self._run(r, ["item", "ready", "--head"])
            self.assertEqual(code, 0, out)
            self.assertIn("1 schedulable now", out)
        finally:
            r.close()


class AMootDecisionUnblocksOnlyItsOwnCloser(unittest.TestCase):
    """G4 — the second gate on lc-26's reader.

    lc-26 made a `decision` blocker resolve against a ledger `decision:` line
    naming the same question. `item close` writes one of those when it closes
    an item over an unanswered decision: `→ moot (closed by xx-2)`. Nobody
    specified what that line does to the OTHER live items on the same
    question, and the answer was: it unblocked all of them, printing "READY
    and unblocked — schedulable now" over a question nobody had answered.

    Every test here comes in a PAIR over the same two-item carrier, because
    a change that simply stopped unblocking decision blockers would score
    identically to the right one against the red case alone.
    """

    QUESTION = "which window is canonical"

    def _repo(self, ledger_lines=()):
        """xx-1 and xx-2, both blocked on the SAME decision question."""
        from lifecycle_core import refusals
        items = refusals.SEED_ITEMS.replace(
            "blocked-by: NONE", f"blocked-by: decision {self.QUESTION}")
        items = items.replace("baseline: 1", "baseline: 2")
        items += refusals._blocked_block("xx-2", "READY",
                                         f"decision {self.QUESTION}")
        return refusals._Repo(
            items=items,
            ledger_text="schema: 2\n"
                        + "".join(ln + "\n" for ln in ledger_lines))

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

    def test_closing_xx2_moot_does_not_unblock_xx1(self):
        """THE RED. The moot line is produced by a REAL close, not planted —
        a planted line would prove the reader parses a shape, not that the
        writer and the reader still agree on it."""
        r = self._repo()
        try:
            code, out = self._run(r, ["item", "close", "xx-2"])
            self.assertEqual(code, 0, out)
            self.assertIn("decision: which window is canonical → moot "
                          "(closed by xx-2)",
                          (r.dir / "LEDGER.md").read_text(encoding="utf-8"))
            code, out = self._run(r, ["item", "ready", "xx-1"])
            self.assertEqual(code, 0, out)
            self.assertIn("BLOCKED — in the OPERATOR's court", out)
            self.assertNotIn("UNBLOCKED", out)
            self.assertNotIn("schedulable now", out)
        finally:
            r.close()

    def test_an_ANSWERED_question_still_unblocks_the_other_item(self):
        """THE MUST-NOT-MOVE ARM, in the same fixture as the red so the two
        share a coordinate. A real answer clears a real blocker; without this
        the test above passes against a reader that unblocks nothing."""
        r = self._repo([f"decision: {self.QUESTION} → the rotated one"])
        try:
            code, out = self._run(r, ["item", "ready", "xx-1"])
            self.assertEqual(code, 0, out)
            self.assertIn("UNBLOCKED", out)
            self.assertIn("READY and unblocked", out)
        finally:
            r.close()

    def test_the_BLOCKED_message_names_the_moot_line_it_found(self):
        """The flat "no `decision:` line names this question" is FALSE once a
        moot line exists, and a reader who checked the ledger would find the
        line it denies. Reporting BLOCKED is right; saying nothing names the
        question is a true-sounding sentence the ledger refutes."""
        r = self._repo()
        try:
            self._run(r, ["item", "close", "xx-2"])
            _code, out = self._run(r, ["item", "ready", "xx-1"])
            self.assertIn("records this question MOOT", out)
            self.assertIn("moot (closed by xx-2)", out)
            self.assertNotIn("No `decision:` line", out)
        finally:
            r.close()

    def test_the_head_board_does_not_call_it_schedulable(self):
        """The second reader. `item ready --head` is what actually schedules,
        so a fix that reached the single-item verb alone would leave the
        board printing the wrong number."""
        r = self._repo()
        try:
            self._run(r, ["item", "close", "xx-2"])
            code, out = self._run(r, ["item", "ready", "--head"])
            self.assertEqual(code, 0, out)
            self.assertIn("0 schedulable now", out)
        finally:
            r.close()

    def test_the_head_board_DOES_count_an_answered_one(self):
        """The head's must-not-move arm — the paired half of the test above."""
        r = self._repo([f"decision: {self.QUESTION} → the rotated one"])
        try:
            code, out = self._run(r, ["item", "ready", "--head"])
            self.assertEqual(code, 0, out)
            self.assertIn("2 schedulable now", out)
        finally:
            r.close()


class TheMootAnswerShapeIsAnchored(unittest.TestCase):
    """The reader's own pair, below the CLI.

    `decision_for` decides WHO a line speaks for; these assert both
    directions of that scoping and the anchoring underneath it, which the
    end-to-end tests exercise only in one configuration each.
    """

    QUESTION = "which window is canonical"

    def _parsed(self, answer):
        from lifecycle_core import ledger
        return ledger.parse(f"schema: 2\ndecision: {self.QUESTION} → {answer}\n")

    def test_a_moot_line_answers_for_its_own_closer(self):
        """The direction that must still WORK. A blanket exclusion would pass
        the red case and fail here, and the two readings are only
        distinguishable at this altitude — a closed item never asks again."""
        from lifecycle_core import ledger
        p = self._parsed("moot (closed by xx-2)")
        self.assertEqual(len(ledger.decision_for(p, self.QUESTION,
                                                 for_item="xx-2")), 1)

    def test_a_moot_line_answers_for_nobody_else(self):
        from lifecycle_core import ledger
        p = self._parsed("moot (closed by xx-2)")
        self.assertEqual(ledger.decision_for(p, self.QUESTION,
                                             for_item="xx-1"), [])
        self.assertEqual(ledger.decision_for(p, self.QUESTION), [])

    def test_the_shape_is_matched_from_the_START(self):
        """An answer that merely CONTAINS the moot wording is an operator's
        answer and clears the blocker. A containment test would read it as
        moot and block an item on a question that was decided — the
        over-fire direction, which is the one that trains an override.

        The bite that moves this is `fullmatch` → `search`. It did NOT move
        while `re.match` and a `^` in the pattern both anchored the start:
        either bite left the other holding, so the check was unfalsifiable
        while reading as extra care. Recorded because a green bite over a
        redundant anchor is indistinguishable from one that discriminates."""
        from lifecycle_core import ledger
        p = self._parsed("superseded, see moot (closed by xx-2)")
        self.assertIsNone(ledger.moot_closer(p.lines[0]))
        self.assertEqual(len(ledger.decision_for(p, self.QUESTION,
                                                 for_item="xx-1")), 1)

    def test_the_shape_is_matched_to_the_END(self):
        """The other end of the same one condition. An answer that STARTS
        with the tool's wording and then says more is an operator's sentence,
        not the tool's line, so it answers the question for everybody. Read
        as moot it would block an item on a question that was decided.

        `fullmatch` → `match` moves this one and leaves the START test green,
        which is what tells the two ends apart."""
        from lifecycle_core import ledger
        p = self._parsed("moot (closed by xx-2) and since settled at the desk")
        self.assertIsNone(ledger.moot_closer(p.lines[0]))
        self.assertEqual(len(ledger.decision_for(p, self.QUESTION,
                                                 for_item="xx-1")), 1)

    def test_the_writer_and_the_reader_share_one_spelling(self):
        """The drift probe. `verbs.py` writes what `moot_answer` returns and
        `moot_closer` reads it; if either end grew its own literal this is
        where it shows, rather than in a board that quietly unblocks again."""
        from lifecycle_core import ledger
        p = self._parsed(ledger.moot_answer("xx-2"))
        self.assertEqual(ledger.moot_closer(p.lines[0]), "xx-2")

    def test_a_blank_closer_is_not_a_closer(self):
        """`moot (closed by )` names nobody, so it answers for nobody — the
        safe direction. Read as a real closer it would answer for any item
        whose id stripped to empty."""
        from lifecycle_core import ledger
        p = self._parsed("moot (closed by  )")
        self.assertIsNone(ledger.moot_closer(p.lines[0]))


class PromotionIsAnActNotADerivation(unittest.TestCase):
    """lc-39 — there was NO PATH from NEW to READY.

    `grade` is written once, by `item add`; `item amend` refuses it by
    design; `item ready` reads it and promotes nothing. So an item admitted
    NEW could never be graded however complete its slots later became, and a
    carrier's head was empty by construction — measured over dotfiles: 133
    items whose slots a desk had filled by amendment, and `item ready --head`
    reporting 2 READY, both of them born complete.

    THE REJECTED ALTERNATIVE IS ON THE RECORD: deriving the grade from slot
    completeness at read time. That makes READY automatic, which law 10
    forbids — the label would assert something nobody judged. So these assert
    an ACT, and the class below the refusals asserts that nothing else in the
    tool started deriving one.

    THE REFUSALS HAVE ROSTER ROWS (`promote_without_judgment`,
    `promote_while_blocked`, `ready_with_unknown_slot_promote`); what is here
    is the half a row cannot prove — the CLEAN outcomes, and the must-not-move
    pairs. A row's control only has to DIFFER from its plant.
    """

    #: Slot-complete, nothing blocking, grade NEW — the shape the desk
    #: measured, and the shape that was unreachable.
    COMPLETE_NEW = """schema: 2
baseline: 1
added: 0
compacted: 0

## xx-1
grade: NEW
requirement: the migrated entry whose slots a desk later filled — BACKLOG.md:5
goal: mitigate
write-set: tools/thing.py
done-criterion: it goes red then green
evidence: measured 2026-08-27
blocked-by: NONE
"""

    def _repo(self, items=None, ledger_lines=()):
        from lifecycle_core import refusals
        return refusals._Repo(
            items=self.COMPLETE_NEW if items is None else items,
            ledger_text="schema: 2\n"
                        + "".join(ln + "\n" for ln in ledger_lines))

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

    PROMOTE = ["item", "promote", "xx-1", "--by", "the wave-4 desk",
               "--reason", "the slots are filled and a fresh context could "
                           "execute this now"]

    def test_the_head_is_empty_before_and_lists_the_item_after(self):
        """THE DONE-CRITERION, as a pair over one carrier. "The head lists
        it" means nothing without the before arm: an item that was always
        listed would satisfy the after arm on its own."""
        r = self._repo()
        try:
            code, before = self._run(r, ["item", "ready", "--head"])
            self.assertEqual(code, 0, before)
            self.assertIn("head: 0 READY, 0 schedulable now", before)
            self.assertIn("No READY item.", before)

            code, out = self._run(r, self.PROMOTE)
            self.assertEqual(code, 0, out)

            code, after = self._run(r, ["item", "ready", "--head"])
            self.assertEqual(code, 0, after)
            self.assertIn("head: 1 READY, 1 schedulable now", after)
            self.assertIn("xx-1 [READY]", after)
            self.assertIn("SCHEDULABLE", after)
        finally:
            r.close()

    def test_the_carrier_records_who_judged_and_why(self):
        """The record is the point of the act. A grade that moved with no
        record is a grade that appeared, and the next reader cannot ask the
        desk that made it."""
        from lifecycle_core import items as items_mod
        r = self._repo()
        try:
            self.assertEqual(self._run(r, self.PROMOTE)[0], 0)
            text = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
            self.assertIn("grade: READY", text)
            self.assertRegex(text, r"promote-reason: \d{4}-\d{2}-\d{2} "
                                   r"the slots are filled")
            self.assertRegex(text, r"promoted-by: \d{4}-\d{2}-\d{2} "
                                   r"the wave-4 desk")
            # The record parses as its own kind, not as an amendment and not
            # as an unknown slot: the shape check is the reader that decides.
            parsed = items_mod.parse(text)
            it = parsed.items[0]
            self.assertEqual(len(it.promotions), 2)
            self.assertEqual(it.amendments, [])
            self.assertEqual(parsed.problems, [])
        finally:
            r.close()

    def test_the_shape_check_accepts_the_written_block(self):
        """The tool must not write a file its own check rejects — the failure
        a reader cannot tell from a hand edit."""
        r = self._repo()
        try:
            self.assertEqual(self._run(r, self.PROMOTE)[0], 0)
            code, out = self._run(r, ["item", "check"])
            self.assertEqual(code, 0, out)
            self.assertIn("item check: CLEAN", out)
            self.assertNotIn("FINDING", out)
        finally:
            r.close()

    def test_a_blocked_item_promotes_once_the_ledger_ANSWERS_it(self):
        """THE PAIR for `promote_while_blocked`. The roster proves the
        refusal fires; this proves it is the BLOCKER that fires it and not
        the promote path — the two carriers differ in the ledger alone."""
        blocked = self.COMPLETE_NEW.replace(
            "blocked-by: NONE", "blocked-by: decision which window is canonical")
        r = self._repo(items=blocked)
        try:
            code, out = self._run(r, self.PROMOTE)
            self.assertEqual(code, 2, out)
            self.assertIn("promote_while_blocked", out)
        finally:
            r.close()
        r = self._repo(items=blocked,
                       ledger_lines=["decision: which window is canonical → "
                                     "the rotated one"])
        try:
            code, out = self._run(r, self.PROMOTE)
            self.assertEqual(code, 0, out)
            self.assertIn("→ READY", out)
        finally:
            r.close()

    def test_a_second_judgment_is_recorded_beside_the_first(self):
        """DELIBERATELY NOT REFUSED. A desk re-affirming its own judgment is
        legitimate work, and a guard that fired on it would be a guard firing
        on a non-defect (R11). The second record is appended, never
        substituted, so the carrier can say the desk judged twice."""
        r = self._repo()
        try:
            self.assertEqual(self._run(r, self.PROMOTE)[0], 0)
            second = list(self.PROMOTE)
            second[second.index("--reason") + 1] = "re-affirmed after review"
            self.assertEqual(self._run(r, second)[0], 0)
            text = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
            self.assertEqual(text.count("promoted-by: "), 2)
            self.assertIn("the slots are filled", text)
            self.assertIn("re-affirmed after review", text)
            self.assertEqual(self._run(r, ["item", "check"])[0], 0)
        finally:
            r.close()

    def test_an_undated_promotion_line_is_a_shape_finding(self):
        """The date is what places a judgment in time; undated, the line is a
        claim about a judgment nobody can locate."""
        r = self._repo(items=self.COMPLETE_NEW
                       + "promoted-by: the wave-4 desk\n")
        try:
            code, out = self._run(r, ["item", "check"])
            self.assertEqual(code, 2, out)
            self.assertIn("does not open with its ISO date", out)
        finally:
            r.close()

    def test_a_promotion_line_among_the_fixed_slots_fires_and_a_closure_does_not(self):
        """THE PAIR THAT DECIDES THIS CHECK SHIPS, measured 2026-08-27.

        The ordering check's fixed run is `SLOTS`, never `SLOTS +
        DONE_ONLY_SLOTS`: `item close` APPENDS `blocker-moot:` onto a body it
        has already moved, so counting the closed-body slots as fixed made
        the ordinary close of a promoted item report a finding about a file
        the tool had just written correctly — a guard firing on legitimate
        work, which stops the lane (R11).

        Both arms are needed. Without the quiet one the check over-fires;
        without the loud one a check that never fires scores identically.
        """
        good = self.COMPLETE_NEW + (
            "promote-reason: 2026-08-27 judged\n"
            "promoted-by: 2026-08-27 the wave-4 desk\n"
            "blocker-moot: which window is canonical\n")
        # The quiet arm: the closure's own annotation follows the record.
        # `blocker-moot:` is closed-only, so the block must be closed for the
        # arm to isolate the ORDER question rather than that one.
        r = self._repo(items=good.replace("grade: NEW", "grade: DONE"))
        try:
            _code, out = self._run(r, ["item", "check"])
            self.assertNotIn("among the fixed slots", out)
        finally:
            r.close()
        # The loud arm: the SAME lines with `promoted-by:` moved above
        # `blocked-by:`, one of the block's own seven.
        bad = good.replace("promoted-by: 2026-08-27 the wave-4 desk\n", "")
        bad = bad.replace("blocked-by: NONE\n",
                          "promoted-by: 2026-08-27 the wave-4 desk\n"
                          "blocked-by: NONE\n")
        r = self._repo(items=bad.replace("grade: NEW", "grade: DONE"))
        try:
            code, out = self._run(r, ["item", "check"])
            self.assertEqual(code, 2, out)
            self.assertIn("carries a promotion line among the fixed slots",
                          out)
        finally:
            r.close()

    def test_nothing_else_started_deriving_the_grade(self):
        """MUST NOT MOVE, and it is the rejected alternative: `item ready`
        still PROMOTES NOTHING and `item amend` still refuses `--grade`. If
        either had changed, READY would be derivable again by a second
        door."""
        from lifecycle_core import items as items_mod
        self.assertNotIn("grade", items_mod.AMENDABLE_SLOTS)
        r = self._repo()
        try:
            before = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
            code, out = self._run(r, ["item", "ready", "xx-1"])
            self.assertEqual(code, 0, out)
            self.assertIn("THIS VERB PROMOTES NOTHING", out)
            self.assertEqual((r.dir / "ITEMS.md").read_text(encoding="utf-8"),
                             before)
        finally:
            r.close()


if __name__ == "__main__":
    unittest.main()
