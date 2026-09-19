"""The registered-closed-vocabulary contract (D-3), part P1.

WHAT THESE GRADE, and it is deliberately not the registry's data fields. A
test asserting that `Vocabulary.oov_form` is set would prove a field, not a
contract — the finding V6 recorded against the first design. So the cases
below traverse the grade vocabulary's PROOF PATH end to end: an OOV value is
written at the admission door, counted by the census, rendered by `item
ready`, and refused by the move. Each of those four is a separate site with
its own way of folding an inexpressible state into a benign neighbour.

THE RED THESE WERE WRITTEN AGAINST, stated because a green here means
nothing without it: run against the pre-P1 implementation, the census case
fails with the OOV grade counted in `unknown`, the door case fails with
`unknown_grade_write`, and the ready and close cases fail because neither
site knows the arm exists. The parse cases pass from the start — they grade
a new module and prove only that it parses, which is why they are not the
contract's proof.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import items, vocab  # noqa: E402


class OOVGrammar(unittest.TestCase):
    """The arm's spelling. Anchored at both ends, dated, reason required."""

    def test_well_formed_parses_to_its_date_and_reason(self):
        got = vocab.parse_oov("cannot-express(2026-09-19): no type fits a "
                              "wait on another repo's release")
        self.assertIsNotNone(got)
        self.assertEqual(got.date, "2026-09-19")
        self.assertIn("no type fits", got.reason)

    def test_undated_is_not_well_formed(self):
        """The date is the form, not an annotation — an undated instance

        cannot be aged, and ageing is what the drain reads."""
        self.assertIsNone(vocab.parse_oov("cannot-express: no date here"))

    def test_reasonless_is_not_well_formed(self):
        """An OOV instance with no reason is a silent park wearing this

        mechanism's label — the exact state it exists to make impossible."""
        self.assertIsNone(vocab.parse_oov("cannot-express(2026-09-19):"))
        self.assertIsNone(vocab.parse_oov("cannot-express(2026-09-19):   "))

    def test_not_matched_as_a_substring(self):
        """A containment test here would be a prefix match in an equality's

        costume: a member whose own text quoted the form would be re-typed by
        the reader meant to classify it."""
        self.assertIsNone(vocab.parse_oov(
            "READY — see cannot-express(2026-09-19): quoted inside prose"))

    def test_malformed_claim_is_its_own_answer(self):
        """Neither a member nor a well-formed instance. Folding it either way

        hides a broken instance of this mechanism inside a bucket."""
        self.assertTrue(vocab.looks_oov("cannot-express: no date"))
        self.assertFalse(vocab.is_oov("cannot-express: no date"))


class RegistryProofPaths(unittest.TestCase):
    """Every registration names a consumer and a route, and renders apart."""

    def test_every_registration_is_complete(self):
        for v in vocab.registry():
            with self.subTest(vocabulary=v.name):
                self.assertTrue(v.members, "a vocabulary with no members")
                self.assertTrue(v.oov_form)
                self.assertTrue(v.consumer)
                self.assertTrue(v.proof_path)

    def test_the_oov_rendering_differs_from_every_member(self):
        """The contract's whole claim: never folded into a neighbour."""
        rendered = "cannot-express(2026-09-19): a reason"
        for v in vocab.registry():
            with self.subTest(vocabulary=v.name):
                self.assertTrue(v.renders_distinctly(rendered))

    def test_a_member_does_not_render_distinctly_from_itself(self):
        """The control for the assertion above. Without it, `renders_distinctly`

        could return True for everything and the case above would pass on a
        predicate that discriminates nothing."""
        grades = vocab.by_name("grades")
        self.assertIsNotNone(grades)
        self.assertFalse(grades.renders_distinctly("READY"))

    def test_members_are_the_live_tuples_not_a_copy(self):
        """A registry holding its own copy would be a second body for the fact

        it exists to single-source, and would drift the day a member is added
        at its home."""
        self.assertEqual(vocab.by_name("grades").members, items.GRADES)
        self.assertEqual(vocab.by_name("evidence marks").members,
                         items.EVIDENCE_MARKS)


class CensusDisposition(unittest.TestCase):
    """The grade arm at its counting site.

    An OOV grade landing in `unknown` inflates exactly the numbers the
    census docstring protects — the drain and retirement triggers read them.
    So it gets its own bucket, and that bucket is NOT open, NOT closed, and
    NOT unknown.
    """

    def _carrier(self, *blocks) -> str:
        return (f"schema: 6\nbaseline: {len(blocks)}\nadded: 0\n"
                "compacted: 0\n" + "".join(blocks))

    def _block(self, ident, grade) -> str:
        return (f"\n## {ident}\ngrade: {grade}\nrequirement: r\ngoal: tend\n"
                "write-set: a.py\ndone-criterion: d\nevidence: MEASURED e\n"
                "blocked-by: NONE\n")

    def test_oov_grade_gets_its_own_bucket(self):
        parsed = items.parse(self._carrier(
            self._block("xx-1", "READY"),
            self._block("xx-2",
                        "cannot-express(2026-09-19): the round has not "
                        "settled what this state is called")))
        got = items.census(parsed)
        self.assertEqual(got["cannot-express"], 1)
        self.assertEqual(got["open"], 1)
        self.assertEqual(got["closed"], 0)
        self.assertEqual(got["unknown"], {})
        self.assertEqual(got["total"], 2)

    def test_an_unknown_word_is_still_unknown(self):
        """The control. If the new bucket swallowed unknown words too, the

        census would have stopped answering the question it was built for and
        the case above would not notice."""
        parsed = items.parse(self._carrier(self._block("xx-1", "SORTOFDONE")))
        got = items.census(parsed)
        self.assertEqual(got["cannot-express"], 0)
        self.assertEqual(got["unknown"], {"SORTOFDONE": 1})

    def test_a_malformed_oov_claim_is_unknown_not_oov(self):
        """Undated, so it cannot be aged. Counting it as an OOV instance would

        let it sit in the drain's population without ever becoming its
        oldest — the count would never reach zero and nothing would say why."""
        parsed = items.parse(self._carrier(
            self._block("xx-1", "cannot-express: undated")))
        got = items.census(parsed)
        self.assertEqual(got["cannot-express"], 0)
        self.assertEqual(sum(got["unknown"].values()), 1)


class GradeArmAtItsThreeVerbSites(unittest.TestCase):
    """The proof path, walked. Door, reader, move.

    THIS IS THE PART THAT MAKES THE REGISTRATION MORE THAN A DATA FIELD. A
    registry entry asserting `oov_form` is set proves nothing about whether
    the operational path ever reaches the renderer — the finding astra
    recorded against the first design. So each case below drives a real verb
    over a real carrier and reads what the verb printed.
    """

    def _repo(self, items_text=None):
        from lifecycle_core import refusals
        r = refusals._Repo(items=items_text or refusals.SEED_ITEMS)
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

    OOV = "cannot-express(2026-09-19): the round has not settled a word for a wait on another repo's release"

    def _carrier_with_oov(self):
        """SEED_ITEMS plus an arm-graded body — and the HEAD COUNTER moved

        with it. A second body under `baseline: 1` is two bodies against one
        admission, which conservation correctly calls OVER; the first version
        of this fixture did exactly that and reddened the close CONTROL, not
        the case under test. The premise a fixture does not pin is one the
        checker is free to catch, and here it did.
        """
        from lifecycle_core import refusals
        seed = refusals.SEED_ITEMS.replace("baseline: 1", "baseline: 2", 1)
        self.assertIn("baseline: 2", seed, "the head counter did not move")
        return seed + (
            f"\n## xx-2\ngrade: {self.OOV}\nrequirement: r\ngoal: mitigate\n"
            "write-set: tools/a.mjs\ndone-criterion: d\n"
            "evidence: MEASURED e\nblocked-by: NONE\n")

    def test_the_door_accepts_the_arm(self):
        """An arm the door refuses is an arm nobody can record, and a

        vocabulary whose OOV value cannot be WRITTEN has not gained one."""
        repo = self._repo()
        code, outp = self._run(
            repo, "item", "add", "--requirement", "a thing", "--goal",
            "mitigate", "--write-set", "tools/a.mjs,tools/b.mjs",
            "--done-criterion", "d", "--evidence", "MEASURED e",
            "--blocked-by", "NONE", "--grade", self.OOV,
            "--join", "new", "--absence", "the word does not exist yet")
        self.assertEqual(code, 0, outp)
        self.assertIn(self.OOV,
                      (repo.dir / "ITEMS.md").read_text(encoding="utf-8"))

    def test_the_door_still_refuses_a_word_that_is_not_a_member(self):
        """The control. Opening the door to the arm must not open it to

        anything — an unrecognised word would be folded into neither open nor
        closed, and the drain triggers read exactly those numbers."""
        repo = self._repo()
        code, outp = self._run(
            repo, "item", "add", "--requirement", "a thing", "--goal",
            "mitigate", "--write-set", "tools/a.mjs,tools/b.mjs",
            "--done-criterion", "d", "--evidence", "MEASURED e",
            "--blocked-by", "NONE", "--grade", "SORTOFDONE",
            "--join", "new", "--absence", "x")
        self.assertEqual(code, 2, outp)
        self.assertIn("unknown_grade_write", outp)

    def test_the_door_refuses_a_malformed_arm(self):
        """Undated: it would enter the carrier and never be ageable, so the

        drain could never watch it reach zero."""
        repo = self._repo()
        code, outp = self._run(
            repo, "item", "add", "--requirement", "a thing", "--goal",
            "mitigate", "--write-set", "tools/a.mjs,tools/b.mjs",
            "--done-criterion", "d", "--evidence", "MEASURED e",
            "--blocked-by", "NONE", "--grade", "cannot-express: undated",
            "--join", "new", "--absence", "x")
        self.assertEqual(code, 2, outp)

    def test_ready_renders_it_unschedulable_WITH_ITS_REASON(self):
        """Not "grade is X, not READY". The reason is the payload: it is what

        a widening gets minted from, and a rendering that dropped it would
        leave the count as the only signal — a number with no content."""
        repo = self._repo(self._carrier_with_oov())
        _code, outp = self._run(repo, "item", "ready", "xx-2")
        self.assertIn("not schedulable", outp.lower())
        self.assertIn("the round has not settled a word", outp)
        self.assertIn("2026-09-19", outp)

    def test_ready_still_says_schedulable_for_a_real_member(self):
        """The control: if the new branch caught everything, every item would

        read unschedulable and the case above would prove nothing."""
        repo = self._repo(self._carrier_with_oov())
        _code, outp = self._run(repo, "item", "ready", "xx-1")
        self.assertIn("schedulable now", outp)

    def test_the_move_refuses_to_close_an_arm_graded_body(self):
        """A grade must be a real member at close. Closing one would file an

        inexpressible state under DONE — the neighbour-folding this contract
        exists to prevent, at the one door after which nobody looks again."""
        repo = self._repo(self._carrier_with_oov())
        code, outp = self._run(repo, "item", "close", "xx-2",
                               "--reason", "closing it anyway")
        self.assertEqual(code, 2, outp)
        self.assertIn("xx-2",
                      (repo.dir / "ITEMS.md").read_text(encoding="utf-8"))

    def test_the_statusline_does_not_call_the_arm_an_unknown_word(self):
        """The fourth site that classifies a grade, found by sweeping for

        GRADES references rather than by listing the sites already in hand.
        The statusline's `!n?` counter means "words this carrier's closed
        vocabulary does not know" — a reading failure somebody must repair.
        An arm grade is the opposite: a state the vocabulary knowingly
        cannot say, recorded on purpose. Counting it there would raise a
        repair flag on the mechanism working.

        NO ALWAYS-ON DELTA: this REMOVES a false count rather than adding a
        line, so the wave's inventory gains no row from it.
        """
        repo = self._repo(self._carrier_with_oov())
        _code, outp = self._run(repo, "item", "statusline")
        self.assertNotIn("!1?", outp)

    def test_the_statusline_still_flags_a_genuinely_unknown_word(self):
        """The control: without it the counter could have been disabled

        outright and the case above would read identically."""
        from lifecycle_core import refusals
        seed = refusals.SEED_ITEMS.replace("baseline: 1", "baseline: 2", 1)
        repo = self._repo(seed + (
            "\n## xx-3\ngrade: SORTOFDONE\nrequirement: r\ngoal: mitigate\n"
            "write-set: tools/a.mjs\ndone-criterion: d\n"
            "evidence: MEASURED e\nblocked-by: NONE\n"))
        _code, outp = self._run(repo, "item", "statusline")
        self.assertIn("!1?", outp)

    def test_the_move_still_closes_a_real_member(self):
        """The control for the refusal: a close that refused everything would

        pass the case above while breaking the verb."""
        repo = self._repo(self._carrier_with_oov())
        code, outp = self._run(repo, "item", "close", "xx-1",
                               "--reason", "done")
        self.assertEqual(code, 0, outp)


class ExternalBlockerAndItsEnding(unittest.TestCase):
    """D-8's minted member, and the ENDING astra-c2 found missing (P4).

    THE MEMBER IS MINTED FROM RECORDED INSTANCES, never guessed: this repo's
    carrier already holds waits nothing here can test — another repo's
    release, an operator's reply — and they were all typed `evidence false`,
    a predicate that can never fire. That reads on the board as ordinary
    machine-court waiting, which is the neighbour-fold this contract exists
    to end.

    AN ENDING IS PART OF THE TYPE. A blocker nothing evaluates needs a
    defined way OUT or it is a permanent silent park under a new name — the
    first design had the court print and no transition, so its red-first
    could pass while no item ever became schedulable again. The case below
    therefore drives a REAL TRANSITION and reads schedulability afterwards,
    not the rendering.
    """

    def _repo(self, items_text=None):
        from lifecycle_core import refusals
        r = refusals._Repo(items=items_text or refusals.SEED_ITEMS)
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

    EVENT = "external the upstream cache-fix release lands"

    def _add_external(self, repo):
        return self._run(
            repo, "item", "add", "--requirement", "waits on another repo",
            "--goal", "mitigate", "--write-set", "tools/a.mjs,tools/b.mjs",
            "--done-criterion", "d", "--evidence", "MEASURED e",
            "--blocked-by", self.EVENT,
            "--join", "new", "--absence", "the release has not happened")

    def test_the_door_accepts_the_minted_member(self):
        repo = self._repo()
        code, outp = self._run(
            repo, "item", "add", "--requirement", "waits on another repo",
            "--goal", "mitigate", "--write-set", "tools/a.mjs,tools/b.mjs",
            "--done-criterion", "d", "--evidence", "MEASURED e",
            "--blocked-by", self.EVENT,
            "--join", "new", "--absence", "the release has not happened")
        self.assertEqual(code, 0, outp)

    def test_it_is_classified_external_and_not_untyped(self):
        from lifecycle_core import items as items_mod
        kind, detail = items_mod.classify_blocker(self.EVENT, "xx")
        self.assertEqual(kind, "external")
        self.assertIn("cache-fix release", detail)

    def test_an_external_blocker_names_no_court_but_the_WORLD(self):
        """Not the machine's court and not the operator's. Both of those

        promise a re-evaluation somebody could run; this one promises only
        that an event has not happened, and saying otherwise sends a reader
        looking for a predicate to fix or a question to answer."""
        repo = self._repo()
        self._add_external(repo)
        _code, outp = self._run(repo, "item", "ready", "xx-2")
        self.assertIn("WORLD", outp)
        self.assertNotIn("MACHINE's court", outp)
        self.assertNotIn("OPERATOR's court", outp)

    def test_THE_REAL_TRANSITION_out_of_waiting(self):
        """The ending, exercised rather than rendered: after the arrival is

        recorded by amendment, the item is SCHEDULABLE. A court print alone
        would pass on a design where nothing ever left the wait."""
        repo = self._repo()
        self._add_external(repo)
        _c, before = self._run(repo, "item", "ready", "xx-2")
        self.assertNotIn("schedulable now", before)
        code, _o = self._run(
            repo, "item", "amend", "xx-2", "--blocked-by", "NONE",
            "--reason", "ARRIVED 2026-09-19: the cache-fix release landed, "
                        "tag v2.1.0 fetched and verified at the remote")
        self.assertEqual(code, 0)
        _c2, after = self._run(repo, "item", "ready", "xx-2")
        self.assertIn("schedulable now", after)

    def test_an_unamended_external_blocker_does_NOT_become_schedulable(self):
        """The control for the transition: without it the case above would

        pass on a build that called everything schedulable."""
        repo = self._repo()
        self._add_external(repo)
        _c, outp = self._run(repo, "item", "ready", "xx-2")
        self.assertNotIn("schedulable now", outp)

    def test_the_type_list_in_a_refusal_is_DERIVED_from_the_vocabulary(self):
        """NIT2: a derived text cannot be falsified by adding a member, only

        by breaking the derivation — so the claim worth asserting is that
        every member of the closed vocabulary reaches the message. A
        hardcoded list would pass today and silently omit the next member.
        """
        from lifecycle_core import items as items_mod
        repo = self._repo()
        _code, outp = self._run(
            repo, "item", "add", "--requirement", "r", "--goal", "mitigate",
            "--write-set", "tools/a.mjs,tools/b.mjs", "--done-criterion", "d",
            "--evidence", "MEASURED e", "--blocked-by", "just some prose",
            "--join", "new", "--absence", "x")
        for member in items_mod.BLOCKER_TYPES:
            if member == "item":
                continue  # spelled as the repo's own id prefix, not the word
            with self.subTest(member=member):
                self.assertIn(member, outp)

    def test_an_untyped_blocker_writes_a_countable_fire_log_event(self):
        """B9: the BLOCKER slot's exemption has to BUY something. A refusal

        where no type fits is the widening signal for this very vocabulary,
        and it was observable only in a desk's scrollback — so the refusal
        records an event carrying the row name, and the signal becomes
        countable from the log rather than remembered.
        """
        import json
        from lifecycle_core import firelog
        repo = self._repo()
        before = 0
        path = firelog.log_path()
        if path.exists():
            before = len(path.read_text(encoding="utf-8").splitlines())
        self._run(
            repo, "item", "add", "--requirement", "r", "--goal", "mitigate",
            "--write-set", "tools/a.mjs,tools/b.mjs", "--done-criterion", "d",
            "--evidence", "MEASURED e", "--blocked-by", "just some prose",
            "--join", "new", "--absence", "x")
        self.assertTrue(path.exists(), "no fire log was written at all")
        lines = path.read_text(encoding="utf-8").splitlines()[before:]
        details = [json.loads(ln).get("detail", "") for ln in lines if ln]
        self.assertTrue(
            any("blocker_untyped" in d for d in details),
            f"no event carries the row name; details seen: {details}")


class ConditionalSlotPlacementReadsTheEFFECTIVEBlocker(unittest.TestCase):
    """A conditional slot is placed against the blocker IN FORCE (P3).

    FOUND IN OPERATION rather than by reading: re-typing lc-82's blocker from
    `evidence` to `decision` — a ruling from the round desk — produced a
    block its own commit gate refused, reporting `not_derivable_misplaced`
    against a blocker that classifies as `decision` when resolved.

    THE CAUSE IS ORDERING. `_close_block` graded placement BEFORE it called
    `_resolve_amendments`, so the check read the base slot line while the
    item's current truth is the last `amended-blocked-by:` (law 8: an item's
    CURRENT truth comes from the resolved slots). The two directions fail
    differently and only one of them is loud:

      LOUD — a re-type INTO a type makes a correctly-placed slot read as
      misplaced, which is a guard firing on legitimate work (law 11) and is
      what stopped the ruling being executed.

      SILENT, AND IT IS P3's OWN RED — a re-type OUT of `evidence` leaves a
      stranded `blocker-exercise:` invisible, because the base line still
      says `evidence` and the check is satisfied. That is attack r2's B2
      exactly, and without this repair P3's "re-type clears the stamp"
      red-first could not fire at all: the check it asserts a zero from was
      blind to the very case.
    """

    def _carrier(self, block):
        return ("schema: 6\nbaseline: 1\nadded: 0\ncompacted: 0\n" + block)

    def _rows(self, text):
        from lifecycle_core import items as items_mod
        return [r for r, _l, _m in items_mod.parse(text).problems]

    RETYPED_TO_DECISION = (
        "\n## xx-1\ngrade: PARKED\nrequirement: r\ngoal: tend\n"
        "write-set: a.py\ndone-criterion: d\nevidence: MEASURED e\n"
        "blocked-by: evidence false  # the old unfalsifiable spelling\n"
        "not-derivable: constitutively the operator's\n"
        "amend-reason: 2026-09-19 re-typed to the court it sits in\n"
        "amended-blocked-by: 2026-09-19 decision is the set complete?\n")

    RETYPED_OUT_OF_EVIDENCE = (
        "\n## xx-1\ngrade: PARKED\nrequirement: r\ngoal: tend\n"
        "write-set: a.py\ndone-criterion: d\nevidence: MEASURED e\n"
        "blocked-by: evidence false  # the old unfalsifiable spelling\n"
        "blocker-exercise: none-yet 2026-09-19\n"
        "amend-reason: 2026-09-19 re-typed to an external wait\n"
        "amended-blocked-by: 2026-09-19 external the release lands\n")

    def test_a_slot_correct_under_the_AMENDED_blocker_is_not_misplaced(self):
        """The loud direction: the guard must stop firing on legitimate work."""
        rows = self._rows(self._carrier(self.RETYPED_TO_DECISION))
        self.assertNotIn("not_derivable_misplaced", rows)

    def test_a_slot_STRANDED_by_a_re_type_IS_misplaced(self):
        """The silent direction, and P3's own red: an exercise record left

        behind by a re-type out of `evidence` must be visible."""
        rows = self._rows(self._carrier(self.RETYPED_OUT_OF_EVIDENCE))
        self.assertIn("blocker_exercise_misplaced", rows)

    def test_an_UNAMENDED_misplacement_still_fires(self):
        """The control. Both cases above turn on amendments, so without an

        unamended arm the check could have been disabled outright and both
        would still pass."""
        rows = self._rows(self._carrier(
            "\n## xx-1\ngrade: PARKED\nrequirement: r\ngoal: tend\n"
            "write-set: a.py\ndone-criterion: d\nevidence: MEASURED e\n"
            "blocked-by: decision is the set complete?\n"
            "blocker-exercise: none-yet 2026-09-19\n"))
        self.assertIn("blocker_exercise_misplaced", rows)

    def test_a_correctly_placed_unamended_slot_does_not_fire(self):
        """The second control: the check must still pass what is right."""
        rows = self._rows(self._carrier(
            "\n## xx-1\ngrade: PARKED\nrequirement: r\ngoal: tend\n"
            "write-set: a.py\ndone-criterion: d\nevidence: MEASURED e\n"
            "blocked-by: evidence test -f /nonexistent\n"
            "blocker-exercise: none-yet 2026-09-19\n"))
        self.assertNotIn("blocker_exercise_misplaced", rows)


if __name__ == "__main__":
    unittest.main()
