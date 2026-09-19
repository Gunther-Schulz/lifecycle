"""The intake join's token half, over a MIGRATED carrier (lc-46).

The VERB's own refusal is a roster row (`join_undisposed`), and it fires on a
shared WRITE-SET path — so the roster proves the refusal and says nothing
about the token match beside it. These cover what the token match owes, which
is the half whose failure is silent in both directions: a join that fires on
nearly every item trains the reflex that kills it (R11), and one that fires on
nothing is a merge check that has stopped checking.

THE FIXTURES CARRY THE MIGRATION'S OWN TAIL because that is the defect's
mechanism, not decoration: every migrated body ends in `— record:
<carrier>:<line>`, so `record` and `backlog` land in nearly every requirement
line at once and supply `MATCH_MIN_TOKENS` by construction. Measured over
dotfiles' migrated carrier 2026-08-27: 126 of 138 live items matched an
ordinary add.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits, items, ledger, refusals, verbs  # noqa: E402

TAIL = " — record: BACKLOG.md:{n}"

#: Subjects with no word in common — so the ONLY thing every item shares is
#: the migration tail. Without that property the fixture could not tell a
#: rarity rule from a broken one.
SUBJECTS = (
    "the sampler emits a truncated waveform on its second pass",
    "kerning tables drift after a font upgrade",
    "invoices round downward at the third decimal",
    "night mode inverts photographs of documents",
    "shipping labels print mirrored on continuous stationery",
    "the greenhouse valve reopens without a schedule",
    "backup rotation keeps eleven weeklies instead of four",
    "map tiles blur at zoom seventeen",
    "subtitles desynchronise after a chapter jump",
    "the turnstile counts pairs as singles",
)


def carrier(subjects, prefix="xx"):
    out = ["schema: 2", "baseline: 0", ""]
    for i, subject in enumerate(subjects, start=1):
        out += [
            f"## {prefix}-{i}",
            "grade: NEW",
            f"requirement: PARKED 2026-08-27 — {subject}"
            + TAIL.format(n=100 + i),
            "goal: mitigate",
            f"write-set: tools/thing{i}.py",
            "done-criterion: it stops doing that",
            "evidence: none yet",
            "blocked-by: NONE",
            "",
        ]
    return "\n".join(out)


def incoming(subject, n=999):
    return f"PARKED 2026-08-27 — {subject}" + TAIL.format(n=n)


class RarityWeightedJoin(unittest.TestCase):

    def setUp(self):
        self.parsed = items.parse(carrier(SUBJECTS))
        self.assertEqual(self.parsed.problems, [], "fixture must be clean")
        self.assertEqual(len(self.parsed.items), len(SUBJECTS))

    def test_the_migration_tail_alone_matches_NOTHING(self):
        """The defect itself: an add sharing only the tail with every item.

        `record` and `backlog` are two tokens, `MATCH_MIN_TOKENS` is two, so
        before this the tail alone matched the whole carrier.
        """
        req = incoming("the pump primes twice on a cold morning")
        found = verbs.candidates(self.parsed, req, "tools/pump.py")
        self.assertEqual(found, [], [i.ident for i, _ in found])

    def test_the_ARRANGEMENT_that_test_rests_on(self):
        """Its own control — without this the test above passes against a
        join that matches nothing at all.

        Both halves are asserted from the fixture: the tail tokens ARE shared
        (so the old two-token rule would have fired on every item), and they
        ARE the only thing shared.
        """
        req = incoming("the pump primes twice on a cold morning")
        want = verbs.requirement_tokens(req)
        for it in self.parsed.items:
            mine = verbs.requirement_tokens(it.slots["requirement"])
            self.assertEqual(want & mine, {"record", "backlog", "parked",
                                           "2026-08-27"},
                             f"{it.ident}: the fixture's only shared tokens "
                             "must be the tail's")
        freq = verbs.document_frequency(self.parsed.items)
        self.assertEqual(freq["record"], len(SUBJECTS))
        self.assertEqual(freq["backlog"], len(SUBJECTS))

    def test_two_items_sharing_RARE_tokens_still_match(self):
        """THE MUST-NOT-MOVE ARM. A rarity rule that dropped these would be
        a join that has stopped joining, and its green is identical to the
        green above."""
        req = incoming("kerning tables drift after a wholesale font upgrade")
        found = verbs.candidates(self.parsed, req, "tools/fonts.py")
        self.assertEqual([i.ident for i, _ in found], ["xx-2"], found)
        self.assertIn("kerning", found[0][1][0])

    def test_a_planted_REAL_duplicate_still_fires(self):
        req = incoming(SUBJECTS[4])
        found = verbs.candidates(self.parsed, req, "tools/labels.py")
        self.assertEqual([i.ident for i, _ in found], ["xx-5"], found)

    def test_a_shared_WRITE_SET_path_matches_whatever_the_tokens_do(self):
        """The path half is exact and has no vocabulary that can flood, so
        rarity must not reach it: an add sharing ONLY the tail but landing in
        a live item's file is still a candidate."""
        req = incoming("the pump primes twice on a cold morning")
        found = verbs.candidates(self.parsed, req, "tools/thing3.py")
        self.assertEqual([i.ident for i, _ in found], ["xx-3"], found)
        self.assertIn("shares write-set", found[0][1][0])

    def test_a_TWO_ITEM_carrier_still_joins(self):
        """The small-carrier arm, and it is where a naive fraction dies:
        document frequency counts the candidate itself, so in a two-item
        carrier every shared token sits at 100% and a whole-carrier fraction
        would drop the lot — killing the duplicate detection exactly where
        the carrier is smallest."""
        small = items.parse(carrier(SUBJECTS[:2]))
        req = incoming(SUBJECTS[1])
        found = verbs.candidates(small, req, "tools/fonts.py")
        self.assertEqual([i.ident for i, _ in found], ["xx-2"], found)

    def test_a_CLOSED_item_is_never_a_candidate(self):
        """Unchanged by lc-46 and asserted because the live filter moved:
        `candidates` now builds the live list once, up front, for the
        frequency table. A filter that moved and stopped filtering would be
        invisible in every test above."""
        text = carrier(SUBJECTS).replace("## xx-2\ngrade: NEW",
                                         "## xx-2\ngrade: DONE")
        found = verbs.candidates(items.parse(text),
                                 incoming(SUBJECTS[1]), "tools/fonts.py")
        self.assertEqual(found, [], found)


class ClosureRecordIsWritten(unittest.TestCase):
    """lc-44 — `item close --reason/--ref` reaching the MOVED BODY.

    THE DEFECT WAS SILENT AND THAT IS THE WHOLE POINT: `--reason` was bound,
    validated on the DONE branch, and written NOWHERE, while the verb printed
    a move and a commit that read as a complete closure record. Measured in
    dotfiles 2026-08-27 — df-143 closed with a 900-char reason naming its
    commit ref, and a grep for that ref returned 0 in all three carriers.

    So the assertions here are about the FILE, never the output: an output
    assertion would have passed against the defect. The two output arms below
    are the opposite question — that a legitimately ABSENT line is SPOKEN,
    because an unspoken absence is byte-identical to the defect.

    HERE RATHER THAN IN `test_moves.py`, which owns the move's own integrity:
    these grade what the close WRITES, and the closure record is a verb-level
    contract (`--reason` in, a slot line out) rather than a property of the
    two-file move.
    """

    REASON = "shipped in the wave-4 batch; the battery is green"

    def _repo(self, **kw):
        r = refusals._Repo(items=refusals.SEED_ITEMS, **kw)
        self.addCleanup(r.close)
        return r

    def _run(self, repo, *argv):
        import io, os
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

    def _head(self, repo):
        import subprocess
        return subprocess.run(["git", "-C", str(repo.dir), "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()

    def _carriers(self, repo):
        return {n: (repo.dir / n).read_text(encoding="utf-8")
                for n in ("ITEMS.md", "ITEMS-DONE.md", "LEDGER.md")}

    def test_a_DONE_close_writes_both_lines_onto_the_moved_body(self):
        """The red, made re-runnable: grep the ref in all three carriers."""
        r = self._repo()
        sha = self._head(r)
        code, out = self._run(r, "item", "close", "xx-1",
                              "--reason", self.REASON, "--ref", sha)
        self.assertEqual(code, exits.CLEAN, out)
        c = self._carriers(r)
        self.assertIn(f"closed-reason: 2026", c["ITEMS-DONE.md"])
        self.assertIn(self.REASON, c["ITEMS-DONE.md"])
        self.assertIn(f"closed-ref: {sha}", c["ITEMS-DONE.md"])
        # ONE HOME. Two homes for one fact is the paraphrase-drift the
        # carrier doctrine forbids, so the ref must NOT also be in the
        # ledger — and it was in NEITHER before this shipped.
        self.assertNotIn(sha, c["LEDGER.md"])
        self.assertNotIn(sha, c["ITEMS.md"])

    def test_a_REASON_ALONE_lands_on_the_body(self):
        """THE DISCRIMINATING RED, and it needs its own arm because every
        assertion above passes `--ref` — a flag the old binary rejects at
        argparse, so those go red on UNRECOGNISED ARGUMENT and would score
        identically against a build that took `--ref` and still wrote
        nothing. This one uses only `--reason`, which the old binary accepts
        and then discards, and it is the df-143 shape exactly: a reason
        naming a ref, greppable in no carrier afterwards.
        """
        r = self._repo()
        sha = self._head(r)
        code, out = self._run(r, "item", "close", "xx-1",
                              "--reason", f"closed at {sha}")
        self.assertEqual(code, exits.CLEAN, out)
        c = self._carriers(r)
        self.assertIn(f"closed-reason: 2026", c["ITEMS-DONE.md"])
        self.assertIn(sha, c["ITEMS-DONE.md"])
        self.assertNotIn("closed-ref:", c["ITEMS-DONE.md"])
        self.assertNotIn(sha, c["LEDGER.md"])

    def test_the_closure_record_survives_item_check(self):
        """The lc-42 arm. The closed-body slots are APPENDED after whatever
        the block accumulated while it was live, so an amended body closed
        with both lines is where an ordering check fires if the fixed run is
        wrong."""
        r = self._repo()
        code, out = self._run(r, "item", "amend", "xx-1",
                              "--evidence", "MEASURED in the wave-4 pass",
                              "--reason", "the desk corrected the evidence")
        self.assertEqual(code, exits.CLEAN, out)
        code, out = self._run(r, "item", "close", "xx-1",
                              "--reason", self.REASON, "--ref", "HEAD")
        self.assertEqual(code, exits.CLEAN, out)
        code, out = self._run(r, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)

    def test_a_DROP_close_gets_NEITHER_line(self):
        """MUST-NOT-MOVE. A dropped body may be pruned, so its record is the
        ledger `dropped:` line — exactly one of them, and no second copy."""
        r = self._repo()
        code, out = self._run(r, "item", "close", "xx-1", "--drop",
                              "--reason", "overtaken by the rework",
                              "--ref", self._head(r))
        self.assertEqual(code, exits.CLEAN, out)
        c = self._carriers(r)
        self.assertNotIn("closed-reason:", c["ITEMS-DONE.md"])
        self.assertNotIn("closed-ref:", c["ITEMS-DONE.md"])
        self.assertEqual(
            sum(1 for l in c["LEDGER.md"].split("\n")
                if l.startswith("dropped:")), 1, c["LEDGER.md"])
        # SAID, never swallowed: a `--ref` dropped in silence would look
        # exactly like one that landed.
        self.assertIn("NOT WRITTEN", out)

    def test_a_DONE_close_with_NEITHER_flag_behaves_as_before(self):
        """MUST-NOT-MOVE: the lines are optional, and a close that demanded
        them would fire on every closure that legitimately has no ref."""
        r = self._repo()
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        body = (r.dir / "ITEMS-DONE.md").read_text(encoding="utf-8")
        self.assertNotIn("closed-reason:", body)
        self.assertNotIn("closed-ref:", body)

    def test_BOTH_absences_are_SPOKEN(self):
        """The half that is not about the file. A silent absence is
        indistinguishable from the defect this item repaired, where the verb
        printed a complete-looking closure and had written nothing."""
        r = self._repo()
        _code, out = self._run(r, "item", "close", "xx-1")
        self.assertIn("closed-reason: not given, no line written", out)
        self.assertIn("closed-ref: not given, no line written", out)

    def test_only_the_MISSING_one_is_reported_missing(self):
        """The control for the arm above: a message printed unconditionally
        would satisfy it while saying nothing true."""
        r = self._repo()
        _code, out = self._run(r, "item", "close", "xx-1",
                               "--reason", self.REASON)
        self.assertNotIn("closed-reason: not given", out)
        self.assertIn("closed-ref: not given, no line written", out)

    def test_an_unresolvable_ref_REFUSES_and_moves_NOTHING(self):
        """The refusal runs BEFORE the move. A validation after it would
        leave a body in the done home with a permanent bad ref, or a
        half-move — and the roster row proves only the exit code."""
        r = self._repo()
        before = self._carriers(r)
        code, out = self._run(r, "item", "close", "xx-1",
                              "--ref", "0123456789abcdef0123456789abcdef01234567")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("closed_ref_unresolvable", out)
        self.assertIn("0123456789abcdef0123456789abcdef01234567", out)
        self.assertEqual(self._carriers(r), before,
                         "the refused close touched a carrier")


class ItemBlockerAtClose(unittest.TestCase):
    """lc-90 — what a close does with an `<item-id>` blocker, all four states.

    THE DEFECT WAS REACHABLE BY EXACTLY ONE ROUTE and the item's own wording
    named the other one, so the fixtures here are built the way the defect
    actually occurs. `move_to_done` rewrites the `blocked-by:` LINE to NONE, so
    a base-slot blocker never reached the done home at all — it was DELETED,
    silently, whatever its target was doing. An `amended-blocked-by:` line
    resolves last-wins OVER that line and the move does not touch it, so an
    amended blocker rode into the closure home alive and `item check` reported
    `blocked_in_done_home` against a body no verb could repair afterwards —
    `item amend` refuses a closed body, correctly. Measured at 11a8c1d on a
    scratch repo: `item close` exited 0 and the next `item check` exited 2.

    So the two halves are ONE defect with opposite signs: the amended value
    survived and was reported, the base value was discarded and was not. Both
    end here, at the verb, before anything moves.

    THE ASSERTIONS ARE ABOUT THE FILE AND THE NEXT CHECK'S VERDICT, never the
    close's own exit code alone: the close never runs the done home's shape
    check, so at 11a8c1d it exited CLEAN over the state it had just minted.
    """

    def _repo(self, items_text, done_text=None):
        r = refusals._Repo(items=items_text, done=done_text)
        self.addCleanup(r.close)
        return r

    def _run(self, repo, *argv):
        import io, os
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

    def _carriers(self, repo):
        return {n: (repo.dir / n).read_text(encoding="utf-8")
                for n in ("ITEMS.md", "ITEMS-DONE.md", "LEDGER.md")}

    #: The amended shape — the one the defect actually rode in on. The base
    #: slot is NONE and the amendment carries the blocker, which is what the
    #: move cannot clear.
    #: `baseline` COUNTS BOTH HOMES and is passed rather than fixed: a
    #: fixture whose baseline does not match the bodies it holds closes onto
    #: a conservation finding, and an arm reading that as its own refusal
    #: would be green for a reason nobody wrote down. Measured while writing
    #: these: a hardcoded 2 turned the decision arm red on `conservation_short`.
    def _amended(self, blocker, base="NONE", baseline=1):
        return (
            f"schema: 2\nbaseline: {baseline}\nadded: 0\ncompacted: 0\n"
            + refusals._blocked_block("xx-1", "READY", base).rstrip("\n")
            + "\namend-reason: 2026-09-13 the desk retyped the blocker\n"
            + f"amended-blocked-by: 2026-09-13 {blocker}\n")

    CLOSED_TARGET = refusals.EMPTY_DONE + refusals._blocked_block(
        "xx-2", "DONE", "NONE")
    DROPPED_TARGET = refusals.EMPTY_DONE + refusals._blocked_block(
        "xx-2", "DROPPED", "NONE")

    def test_the_AMENDED_blocker_that_survived_the_close_is_now_recorded(self):
        """THE RED, made re-runnable. At 11a8c1d this exact arrangement closed
        CLEAN and the next `item check` returned FINDING
        `blocked_in_done_home` — against a body that HAD arrived by a close,
        which is what made the finding unrepairable rather than merely
        wrong."""
        r = self._repo(self._amended("xx-2", baseline=2), self.CLOSED_TARGET)
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        done = (r.dir / "ITEMS-DONE.md").read_text(encoding="utf-8")
        self.assertIn(
            f"blocker-moot: {items.item_moot_record('xx-2', abandoned=False)}",
            done)
        code, out = self._run(r, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("blocked_in_done_home", out)

    def test_a_LIVE_target_refuses_the_close_and_moves_NOTHING(self):
        """The must-not-move, and the refusal runs BEFORE the move: a verdict
        delivered after it would be about a body already sitting where
        `item amend` refuses to touch it."""
        items_text = ("schema: 2\nbaseline: 2\nadded: 0\ncompacted: 0\n"
                      + refusals._blocked_block("xx-1", "READY", "xx-2")
                      + refusals._blocked_block("xx-2", "READY", "NONE"))
        r = self._repo(items_text)
        before = self._carriers(r)
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("close_over_live_blocker", out)
        self.assertEqual(self._carriers(r), before,
                         "the refused close touched a carrier")

    def test_the_BASE_slot_form_is_refused_too_and_was_SILENTLY_CLEARED(self):
        """The half nothing reported. At 11a8c1d this closed CLEAN, the done
        home stayed clean, and the live dependency was simply gone — the
        `blocked-by:` line rewritten to NONE and the old value dropped by its
        caller. A clean done home was never evidence that the wait had been
        met."""
        items_text = ("schema: 2\nbaseline: 2\nadded: 0\ncompacted: 0\n"
                      + refusals._blocked_block("xx-1", "READY", "xx-2")
                      + refusals._blocked_block("xx-2", "READY", "NONE"))
        r = self._repo(items_text)
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("xx-2 is still live in the carrier", out)

    def test_a_DROPPED_target_refuses_rather_than_discharging(self):
        """An item-id blocker resolves on its target's DONE — `_check_blocker`
        refuses to WRITE one naming a dropped target for exactly this reason,
        so a close that read DROPPED as a discharge would assert at one verb
        what the tool refuses two verbs over."""
        r = self._repo(self._amended("xx-2", baseline=2), self.DROPPED_TARGET)
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("close_over_live_blocker", out)
        self.assertIn("DROPPED", out)

    def test_a_target_in_NEITHER_home_refuses(self):
        """The fourth state. A blocker pointing at nothing never resolves, so
        reading its absence as a discharge would make the emptiest possible
        evidence the strongest."""
        r = self._repo(self._amended("xx-9999"))
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("NEITHER home", out)

    def test_a_DROP_records_the_wait_ABANDONED_never_answered(self):
        """A drop is an exit of equal standing and must stay available over a
        live dependency — but the record it writes says the waiter is gone,
        which is the only thing a drop establishes. The two forms differ in
        the file, not only in the prose: the answered form must be ABSENT."""
        items_text = ("schema: 2\nbaseline: 2\nadded: 0\ncompacted: 0\n"
                      + refusals._blocked_block("xx-1", "READY", "xx-2")
                      + refusals._blocked_block("xx-2", "READY", "NONE"))
        r = self._repo(items_text)
        code, out = self._run(r, "item", "close", "xx-1", "--drop",
                              "--reason", "overtaken by the rework")
        self.assertEqual(code, exits.CLEAN, out)
        done = (r.dir / "ITEMS-DONE.md").read_text(encoding="utf-8")
        self.assertIn(items.item_moot_record("xx-2", abandoned=True), done)
        self.assertNotIn(items.item_moot_record("xx-2", abandoned=False), done)
        code, out = self._run(r, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)

    def test_a_CLOSED_target_beats_the_drop_form_on_a_DROP(self):
        """The record states what is TRUE, not what the verb happened to be.
        A drop whose blocker had genuinely closed records the closure — the
        abandonment form would understate a wait that was met."""
        r = self._repo(self._amended("xx-2", baseline=2), self.CLOSED_TARGET)
        code, out = self._run(r, "item", "close", "xx-1", "--drop",
                              "--reason", "overtaken by the rework")
        self.assertEqual(code, exits.CLEAN, out)
        done = (r.dir / "ITEMS-DONE.md").read_text(encoding="utf-8")
        self.assertIn(items.item_moot_record("xx-2", abandoned=False), done)

    def test_the_record_discharges_ONLY_the_id_it_NAMES(self):
        """The discrimination arm. The discharge is an EQUALITY against a
        record built for THAT id, so a body carrying the record for some other
        item is still a surviving blocker — a predicate that merely looked for
        a `blocker-moot:` line would clear every one of them."""
        def home(named):
            return (refusals.EMPTY_DONE
                    + refusals._blocked_block("xx-1", "DONE", "xx-2")
                    .rstrip("\n") + "\nblocker-moot: "
                    + items.item_moot_record(named, abandoned=False) + "\n")

        one_body = "schema: 2\nbaseline: 1\nadded: 0\ncompacted: 0\n"
        r = self._repo(one_body, home("xx-77"))
        code, out = self._run(r, "item", "check")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("blocked_in_done_home", out)
        # THE OTHER HALF OF THE PAIR, in the same fixture shape: the record
        # for the id the blocker DOES name clears it. Without this arm the
        # red above is equally consistent with a discharge that never fires.
        r2 = self._repo(one_body, home("xx-2"))
        code, out = self._run(r2, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("blocked_in_done_home", out)

    def test_a_DECISION_blocker_keeps_EXACTLY_the_record_it_had(self):
        """MUST-NOT-MOVE, both halves: the body line AND the ledger line. The
        decision type is the one this item was forbidden to disturb."""
        r = self._repo(self._amended("decision which window is canonical"))
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        c = self._carriers(r)
        self.assertIn("blocker-moot: which window is canonical",
                      c["ITEMS-DONE.md"])
        self.assertIn("decision: which window is canonical", c["LEDGER.md"])
        self.assertIn("moot (closed by xx-1)", c["LEDGER.md"])

    def test_an_item_blocker_writes_NO_ledger_line(self):
        """One fact, one home. The target item's own closure is already the
        ledger's record of it; a second `decision:` line about a dependency
        nobody asked as a question is the paraphrase-drift the carrier
        doctrine forbids."""
        r = self._repo(self._amended("xx-2", baseline=2), self.CLOSED_TARGET)
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("decision:", self._carriers(r)["LEDGER.md"])

    def test_an_UNREADABLE_done_home_is_COULD_NOT_VERIFY_not_a_close(self):
        """Three answers. Whether the wait was answered is a question about
        the closure home, so with that home unreadable the honest result is
        neither a discharge nor a refusal — and it must not fall through to a
        move, because the move would then write the state nobody could check.
        """
        r = self._repo(self._amended("xx-2", baseline=2), self.CLOSED_TARGET)
        (r.dir / "ITEMS-DONE.md").unlink()
        before = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("COULD NOT VERIFY", out)
        self.assertEqual((r.dir / "ITEMS.md").read_text(encoding="utf-8"),
                         before, "an unverifiable close moved the body anyway")


class LedgerStorableBlocker(unittest.TestCase):
    """lc-49 — the THREE hand-write doors into an unanswerable decision.

    lc-40 closed the MINT and left `item add`, `item park` and `item amend`
    open. The roster row (`blocker_unstorable`) fires ONE of the three, so it
    says nothing about the other two — and the door the defect actually came
    through was `item amend`, the one no row covers. These walk all three.

    THE FIRING TEXT IS THE REAL ONE. `df-135` reached dotfiles' carrier
    through `item amend --blocked-by`, which retyped an `evidence` blocker
    into a `decision` one and carried the ledger's slot separator in with it
    (repaired in dotfiles `ec47c3c`). It is copied byte-for-byte rather than
    paraphrased: a constructed sentence would prove the predicate parses, not
    that it discriminates on what actually got in.
    """

    #: The value `item amend --blocked-by` wrote into dotfiles df-135, taken
    #: verbatim from `ec47c3c^:ITEMS.md`.
    DF_135 = ("decision lifecycle lc-38 must settle the pointer anchor first "
              "— re-extracting against ranges known to be 2 lines stale would "
              "bake the offset into the repaired bodies")
    #: The SAME question with the separator gone. Every control below differs
    #: from its plant in the separator alone.
    DF_135_REPHRASED = DF_135.replace(" — ", "; ")

    #: lc-169 DEMANDS THE STATEMENT AT ALL THREE DOORS, so all three
    #: helpers carry one. It is supplied in the helper rather than per arm
    #: because this class's subject is the SEPARATOR, and an arm differing in
    #: two things at once would separate nothing.
    NOT_DERIVABLE = "lc-38's anchor decision is in no record this desk holds"

    def _add(self, blocker):
        return refusals._cli(refusals.GOOD_ADD + [
            "--blocked-by", blocker, "--not-derivable", self.NOT_DERIVABLE])

    def _park(self, blocker):
        return refusals._cli(["item", "park", "xx-1", "--blocked-by", blocker,
                              "--not-derivable", self.NOT_DERIVABLE],
                             items=refusals.SEED_ITEMS)

    def _amend(self, blocker):
        return refusals._cli(
            ["item", "amend", "xx-1", "--blocked-by", blocker,
             "--not-derivable", self.NOT_DERIVABLE,
             "--reason", "the desk retyped the blocker"],
            items=refusals.SEED_ITEMS)

    def _refused(self, fired, door):
        self.assertEqual(fired.code, exits.FINDING,
                         f"{door} accepted it:\n{fired.output}")
        self.assertIn("blocker_unstorable", fired.output)

    def _accepted(self, fired, door):
        self.assertEqual(fired.code, exits.CLEAN,
                         f"{door} refused the control:\n{fired.output}")
        self.assertNotIn("blocker_unstorable", fired.output)

    def test_item_add_refuses_it(self):
        self._refused(self._add(self.DF_135), "item add")

    def test_item_park_refuses_it(self):
        self._refused(self._park(self.DF_135), "item park")

    def test_item_amend_refuses_it(self):
        """The door df-135 came through."""
        self._refused(self._amend(self.DF_135), "item amend")

    def test_all_three_doors_ACCEPT_the_rephrased_question(self):
        """The control, one per door: the arms differ in the separator alone,
        so a gate that had simply started refusing decision blockers would
        score identically on the three tests above and fail here."""
        self._accepted(self._add(self.DF_135_REPHRASED), "item add")
        self._accepted(self._park(self.DF_135_REPHRASED), "item park")
        self._accepted(self._amend(self.DF_135_REPHRASED), "item amend")

    def test_the_carrier_is_UNWRITTEN_after_a_refusal(self):
        """A refusal that reported and wrote anyway would be a message, not a
        gate — and the report reads the same either way."""
        with refusals._Repo(items=refusals.SEED_ITEMS) as r:
            before = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
            import io, os
            from contextlib import redirect_stdout
            from lifecycle_core import cli as cli_mod
            here = os.getcwd()
            try:
                os.chdir(str(r.dir))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    code = cli_mod.main([
                        "--repo", str(r.dir), "item", "amend", "xx-1",
                        "--blocked-by", self.DF_135,
                        "--reason", "the desk retyped the blocker"])
            finally:
                os.chdir(here)
            self.assertEqual(code, exits.FINDING, buf.getvalue())
            self.assertEqual((r.dir / "ITEMS.md").read_text(encoding="utf-8"),
                             before, "the refused amendment reached the file")

    def test_an_EVIDENCE_blocker_carrying_the_separator_is_UNAFFECTED(self):
        """MUST-NOT-MOVE, and the sharpest arm: df-135's blocker was an
        EVIDENCE one before the amend retyped it. Only the ledger stores a
        decision question, so only that type is gated — a check keyed on the
        separator rather than on the TYPE would fire here.

        THE PREDICATE IS SPELLED `false  # <prose>` SINCE lc-130, and the
        reason is a finding rather than a convenience: df-135's question
        retyped as an evidence blocker is PROSE IN A SHELL SLOT — it parses,
        and it exits 127 — which is the exact class the mint-time predicate
        lint exists to refuse. This fixture was one instance of it. The
        spelling is the LIVE CARRIER's own idiom for a wait that has not
        arrived (ITEMS.md:13, :24), the same one `test_items.py`'s
        third-conjunct arm took: exit 1, still waiting. It leaves the property
        under test untouched — the value is still an `evidence` blocker and
        still carries the ledger's own ` — ` separator, so a storability check
        keyed on the separator rather than on the TYPE still fires here.
        Swapping this for a separator-free predicate would have removed the
        discrimination, which is why it was not done."""
        self._accepted(
            self._add("evidence false  # " + self.DF_135[len("decision "):]),
            "item add (evidence)")

    def test_an_ITEM_ID_blocker_is_UNAFFECTED(self):
        fired = refusals._cli(refusals.GOOD_ADD + ["--blocked-by", "xx-1"],
                              items=refusals.SEED_ITEMS)
        self._accepted(fired, "item add (item-id)")

    def test_a_NONE_blocker_is_UNAFFECTED(self):
        self._accepted(self._add("NONE"), "item add (NONE)")

    def test_the_67_REPAIRED_dotfiles_TEXTS_all_pass_and_the_OLD_ONES_do_not(self):
        """The instrument on a known positive AND a known negative, both
        drawn from the real carrier rather than constructed.

        Read-only, and skipped rather than failed where the carrier is not on
        this machine: a check that cannot reach its input is COULD NOT VERIFY,
        never a pass.
        """
        import subprocess
        from lifecycle_core import ledger
        # DERIVED, never hardcoded. An absolute home path here is a
        # publication-bar finding (absence-scan `foreign-path`) and breaks on
        # every other checkout; the sibling layout is the only assumption, and
        # the skip below already covers its absence.
        repo = Path(__file__).resolve().parents[2] / "dotfiles"
        if not (repo / "ITEMS.md").exists():
            self.skipTest(f"no carrier at {repo}: this arm grades the REAL "
                          "texts and has no input here")

        def unstorable(text):
            parsed = items.parse(text)
            out = []
            for it in parsed.items:
                kind, detail = items.classify_blocker(
                    it.slots.get("blocked-by", ""), "df")
                if kind == "decision" and ledger.check_prose(
                        detail, "the decision question"):
                    out.append(it.ident)
            return out

        now = unstorable((repo / "ITEMS.md").read_text(encoding="utf-8"))
        self.assertEqual(now, [], "repaired texts must all pass")
        before = subprocess.run(
            ["git", "-C", str(repo), "show", "ec47c3c^:ITEMS.md"],
            capture_output=True, text=True)
        if before.returncode != 0:
            self.skipTest("ec47c3c^ is not reachable in that checkout")
        # THE POSITIVE CONTROL. Without it the empty list above is what a
        # predicate matching nothing at all also returns.
        self.assertEqual(len(unstorable(before.stdout)), 67,
                         "the pre-repair carrier must still be refused")


class OneGrammarFindsAndEndsABlock(unittest.TestCase):
    """lc-40 — `_set_slots` found a block by one grammar and ended it by another.

    THE TWO SPELLINGS. The search used the `## <id>` regex, which accepts any
    whitespace between the marker and the id and always has; the write loop
    ended the block on `startswith("## ")`, which accepts exactly one space.
    They agree on every heading a human types and disagree on a tab — and
    where they disagreed the loop ran past the block it was given and wrote
    the caller's slots into the NEXT item.

    MEASURED, not reasoned: against the pre-fix binary this fixture's `item
    park xx-1` set `grade: PARKED` and the blocker on xx-2 as well, exit 0 and
    no finding. Silent, because both blocks stay well-formed afterwards and
    the carrier still parses.

    THE ARMS DIFFER IN ONE CHARACTER — the second heading's separator — so a
    build that had simply stopped writing anything would fail the control, and
    one that wrote everywhere would fail the plant.
    """

    #: The tab is the whole plant. Named rather than inlined so the two
    #: carriers below cannot drift apart in anything else.
    PLANT_SEP = "\t"
    CONTROL_SEP = " "

    @staticmethod
    def _carrier(sep):
        return (
            "schema: 2\nbaseline: 2\nadded: 0\ncompacted: 0\n"
            "\n## xx-1\ngrade: READY\n"
            "requirement: first block requirement\n"
            "goal: mitigate\nwrite-set: tools/a.py\n"
            "done-criterion: it goes red then green\nevidence: none yet\n"
            "blocked-by: NONE\n"
            f"\n##{sep}xx-2\ngrade: READY\n"
            "requirement: second block requirement\n"
            "goal: mitigate\nwrite-set: tools/b.py\n"
            "done-criterion: it goes red then green\nevidence: none yet\n"
            "blocked-by: NONE\n")

    def _xx2_slots(self, sep, text):
        block = text.split(f"##{sep}xx-2", 1)[1]
        return {ln.split(":", 1)[0]: ln.split(":", 1)[1].strip()
                for ln in block.split("\n") if ":" in ln and not ln.startswith("#")}

    def test_a_tab_headed_NEIGHBOUR_is_not_written_through(self):
        """THE DEFECT. Red against the pre-fix binary: xx-2 came back PARKED."""
        import io
        import os
        from contextlib import redirect_stdout
        from lifecycle_core import cli as cli_mod
        with refusals._Repo(items=self._carrier(self.PLANT_SEP)) as r:
            here = os.getcwd()
            try:
                os.chdir(str(r.dir))
                with redirect_stdout(io.StringIO()):
                    code = cli_mod.main([
                        "--repo", str(r.dir), "item", "park", "xx-1",
                        "--blocked-by", "decision which window is canonical",
                        "--not-derivable", "a preference with no precedent in the ledger — constitutively the operator's",])
            finally:
                os.chdir(here)
            self.assertEqual(code, exits.CLEAN)
            slots = self._xx2_slots(
                self.PLANT_SEP,
                (r.dir / "ITEMS.md").read_text(encoding="utf-8"))
        self.assertEqual(slots["grade"], "READY",
                         "xx-2 was parked by a call that named xx-1")
        self.assertEqual(slots["blocked-by"], "NONE",
                         "xx-2 took xx-1's blocker")

    def test_the_named_block_IS_still_written(self):
        """The must-move half. Without it a build that refused to write
        anything would pass the test above and prove nothing."""
        import io
        import os
        from contextlib import redirect_stdout
        from lifecycle_core import cli as cli_mod
        with refusals._Repo(items=self._carrier(self.PLANT_SEP)) as r:
            here = os.getcwd()
            try:
                os.chdir(str(r.dir))
                with redirect_stdout(io.StringIO()):
                    cli_mod.main([
                        "--repo", str(r.dir), "item", "park", "xx-1",
                        "--blocked-by", "decision which window is canonical",
                        "--not-derivable", "a preference with no precedent in the ledger — constitutively the operator's",])
            finally:
                os.chdir(here)
            text = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
        first = text.split("## xx-1", 1)[1].split("\n##", 1)[0]
        self.assertIn("grade: PARKED", first)
        self.assertIn("blocked-by: decision which window is canonical", first)


class PromoteAlsoRespectsTheBlockBoundary(unittest.TestCase):
    """lc-63 — `item promote` had NO RED OF ITS OWN for the lc-40
    block-boundary defect. It is the SECOND caller of `_set_slots`
    (`verbs.py`; park's call is the first, exercised above), and until this
    class the fix's reach into promote was INFERENCE through the shared
    helper, never an executed arm — a red certifies the CLASS that fired,
    never the instrument's reach, and park and promote are two variants
    because they write different slots.

    MEASURED, not reasoned, against a private clone of `66bd2af` (the
    commit the park arm's own docstring cites, ancestor of the lc-40 fix;
    its own self-check — the CONTROL arm below, space-separated headings —
    ran green first, proving the clone's arrangement sound before any red
    from it is trusted): `item promote xx-1 --by ... --reason ...` on the
    PLANT carrier (tab-separated second heading) exits 0 and writes `grade:
    READY` into `xx-2` as well as `xx-1` — silent, because both blocks stay
    well-formed afterwards and the carrier still parses. Run against the
    CURRENT, fixed `_set_slots`, the same call leaves `xx-2` at `grade: NEW`
    and only `xx-1` moves. Both runs used this exact fixture and the exact
    `PROMOTE` argv below.

    Mirrors `OneGrammarFindsAndEndsABlock` above: same tab plant, same
    control separator, same shared helper — reached through the write
    promote makes (`grade: READY`) rather than the one park makes
    (`grade: PARKED` plus `blocked-by`).
    """

    #: Same plant as the park arm's fixture; the tab is the whole plant.
    PLANT_SEP = "\t"
    CONTROL_SEP = " "

    @staticmethod
    def _carrier(sep):
        return (
            "schema: 2\nbaseline: 2\nadded: 0\ncompacted: 0\n"
            "\n## xx-1\ngrade: NEW\n"
            "requirement: first block requirement\n"
            "goal: mitigate\nwrite-set: tools/a.py\n"
            "done-criterion: it goes red then green\nevidence: none yet\n"
            "blocked-by: NONE\n"
            f"\n##{sep}xx-2\ngrade: NEW\n"
            "requirement: second block requirement\n"
            "goal: mitigate\nwrite-set: tools/b.py\n"
            "done-criterion: it goes red then green\nevidence: none yet\n"
            "blocked-by: NONE\n")

    #: xx-2 starts at `grade: NEW`, distinct from the `grade: READY` promote
    #: writes into xx-1 — a mis-write into xx-2 is otherwise indistinguishable
    #: from its own starting value, which is why the park fixture's shared
    #: `grade: READY` shape would not discriminate here.
    PROMOTE = ["item", "promote", "xx-1", "--by", "the drain desk",
               "--reason", "lc-63's own red-first arm"]

    def _xx2_slots(self, sep, text):
        block = text.split(f"##{sep}xx-2", 1)[1]
        return {ln.split(":", 1)[0]: ln.split(":", 1)[1].strip()
                for ln in block.split("\n") if ":" in ln and not ln.startswith("#")}

    def test_a_tab_headed_NEIGHBOUR_is_not_re_graded_by_promote(self):
        """THE DEFECT. Red demonstrated separately against a private clone
        of 66bd2af (pre-lc-40-fix, self-check green first via the CONTROL
        arm): the same `item promote xx-1` call wrote `grade: READY` into
        `xx-2` too, exit 0, no finding. Against the current, fixed
        `_set_slots` this stays `NEW`."""
        import io
        import os
        from contextlib import redirect_stdout
        from lifecycle_core import cli as cli_mod
        with refusals._Repo(items=self._carrier(self.PLANT_SEP)) as r:
            here = os.getcwd()
            try:
                os.chdir(str(r.dir))
                with redirect_stdout(io.StringIO()):
                    code = cli_mod.main(["--repo", str(r.dir)] + self.PROMOTE)
            finally:
                os.chdir(here)
            self.assertEqual(code, exits.CLEAN)
            slots = self._xx2_slots(
                self.PLANT_SEP,
                (r.dir / "ITEMS.md").read_text(encoding="utf-8"))
        self.assertEqual(slots["grade"], "NEW",
                         "xx-2 was re-graded by a promote that named xx-1")

    def test_the_named_block_IS_still_promoted(self):
        """The must-move half. Without it a build that refused to write
        anything would pass the test above and prove nothing."""
        import io
        import os
        from contextlib import redirect_stdout
        from lifecycle_core import cli as cli_mod
        with refusals._Repo(items=self._carrier(self.PLANT_SEP)) as r:
            here = os.getcwd()
            try:
                os.chdir(str(r.dir))
                with redirect_stdout(io.StringIO()):
                    code = cli_mod.main(["--repo", str(r.dir)] + self.PROMOTE)
            finally:
                os.chdir(here)
            self.assertEqual(code, exits.CLEAN)
            text = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
        first = text.split("## xx-1", 1)[1].split("\n##", 1)[0]
        self.assertIn("grade: READY", first)


class HeadingPredicatesAreDeliberatelyDifferent(unittest.TestCase):
    """The two heading questions `grammar` keeps apart, and the input that
    separates them — so a later edit collapsing them fails here rather than
    in a carrier."""

    def test_ends_block_is_WIDER_than_starts_section(self):
        from lifecycle_core import grammar
        tab = "##\txx-2"
        self.assertTrue(grammar.ends_block(tab))
        self.assertFalse(grammar.starts_section(tab),
                         "the head-region boundary is the narrow reading")
        # And they agree on everything an ordinary carrier holds.
        for ln in ("## xx-1", grammar.ARCHIVE_HEADING):
            self.assertTrue(grammar.ends_block(ln))
            self.assertTrue(grammar.starts_section(ln))
        for ln in ("grade: READY", "", "requirement: x", "# a comment"):
            self.assertFalse(grammar.ends_block(ln))
            self.assertFalse(grammar.starts_section(ln))

    def test_the_archive_heading_is_NOT_a_block_heading(self):
        """Why `starts_section` cannot simply be `heading_ident is not None`:
        the head region ends at the archive too, and the block regex misses
        it."""
        from lifecycle_core import grammar
        self.assertIsNone(grammar.heading_ident(grammar.ARCHIVE_HEADING))
        self.assertTrue(grammar.starts_section(grammar.ARCHIVE_HEADING))

    def test_is_slot_anchors_the_terminator(self):
        from lifecycle_core import grammar
        self.assertTrue(grammar.is_slot("blocked-by: NONE", "blocked-by"))
        self.assertFalse(grammar.is_slot("blocked-by-note: x", "blocked-by"))

    def test_the_minted_blocker_is_ledger_storable(self):
        """The minting form and the predicate that judges it now share a file;
        this is the pair, asserted rather than assumed."""
        from lifecycle_core import grammar
        self.assertIsNone(grammar.check_prose(
            grammar.REGRADE_BLOCKER.split(" ", 1)[1],
            "the minted decision question"))


class ItemStatusline(unittest.TestCase):
    """`item statusline` (lc-45) — the cheap single-pass approximation.

    RECONCILIATION IS THE POINT, not just the new verb's own output: a
    fixture asserting only what this verb prints would pass whether or not
    its counts agree with the real carrier. Each test below checks the new
    line against an INDEPENDENT read of the same fixture — `items.parse`
    (the ground truth this verb deliberately does not call) and, for the
    clean case, `item ready --head`'s own report.
    """

    def _repo(self, items_text):
        r = refusals._Repo(items=items_text)
        self.addCleanup(r.close)
        return r

    def _run(self, repo, *argv):
        import io
        from contextlib import redirect_stdout
        from lifecycle_core import cli as cli_mod
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli_mod.main(["--repo", str(repo.dir)] + list(argv))
        return code, buf.getvalue()

    def test_clean_reconciles_with_ready_head(self):
        """One unblocked READY (the head), one item-id-blocked READY, one
        PARKED, one NEW. NEW must not count toward either letter."""
        carrier = (
            "schema: 2\nbaseline: 4\nadded: 0\ncompacted: 0\n"
            + refusals._blocked_block("xx-1", "READY", "NONE")
            + refusals._blocked_block("xx-2", "READY", "xx-9999")
            + refusals._blocked_block("xx-3", "PARKED", "decision which window")
            + refusals._blocked_block("xx-4", "NEW", "NONE")
        )
        r = self._repo(carrier)

        # Independent ground truth — never the code under test.
        parsed = items.parse(carrier)
        from collections import Counter
        counts = Counter(it.grade for it in parsed.items)
        self.assertEqual(counts, {"READY": 2, "PARKED": 1, "NEW": 1}, counts)

        code, out = self._run(r, "item", "statusline")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(out.strip(), "2R.1P head xx-1")

        # Cross-check against the heavier verb: it must agree on the READY
        # count and on xx-1 being the schedulable one, xx-2 not.
        _, head_out = self._run(r, "item", "ready", "--head")
        self.assertIn("head: 2 READY, 1 schedulable now.", head_out, head_out)
        self.assertIn("1. xx-1 [READY]", head_out, head_out)
        self.assertIn("xx-1 [READY] goal=mitigate  SCHEDULABLE", head_out,
                      head_out)
        self.assertIn("xx-2 [READY] goal=mitigate  not schedulable", head_out,
                      head_out)

    def test_no_schedulable_ready_prints_dash_head(self):
        """Every READY item is blocked (a dangling id, an unanswered
        decision) — the head is `-`, never a guess at one of them."""
        carrier = (
            "schema: 2\nbaseline: 2\nadded: 0\ncompacted: 0\n"
            + refusals._blocked_block("xx-1", "READY", "xx-9999")
            + refusals._blocked_block("xx-2", "READY", "decision which window")
        )
        r = self._repo(carrier)
        code, out = self._run(r, "item", "statusline")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(out.strip(), "2R.0P head -")

    def test_unparseable_item_block_is_could_not_verify(self):
        """A block heading with no `grade:` line before the next heading (or
        EOF) — never a count that silently excludes it."""
        corrupt = ("schema: 2\nbaseline: 0\nadded: 0\ncompacted: 0\n\n"
                  "## xx-1\nrequirement: no grade line ever arrives\n")
        r = self._repo(corrupt)
        code, out = self._run(r, "item", "statusline")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertTrue(out.strip().startswith("n/a ("), out)
        self.assertIn("xx-1", out)
        self.assertNotRegex(out, r"\d+R\.\d+P",
                            "a could-not-verify line must never look numeric")

    def test_no_item_block_at_all_is_could_not_verify(self):
        """A carrier with no `## <id>` heading at all — the grade-line regex
        cannot even locate an item, distinct from the malformed-block case
        above and worth its own message."""
        headless = "schema: 2\nbaseline: 0\nadded: 0\ncompacted: 0\n"
        r = self._repo(headless)
        code, out = self._run(r, "item", "statusline")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertTrue(out.strip().startswith("n/a ("), out)
        self.assertIn("no item block found", out)

    def test_unknown_grade_word_is_a_finding(self):
        """A `grade:` word outside `items_mod.GRADES` — the carrier's closed
        vocabulary — is a FINDING trailing `!N?`, never folded into READY or
        PARKED and never silently dropped."""
        carrier = (
            "schema: 2\nbaseline: 2\nadded: 0\ncompacted: 0\n"
            + refusals._blocked_block("xx-1", "READY", "NONE")
            + refusals._blocked_block("xx-2", "SUPERSEDED", "NONE")
        )
        r = self._repo(carrier)
        self.assertNotIn("SUPERSEDED", items.GRADES, items.GRADES)
        code, out = self._run(r, "item", "statusline")
        self.assertEqual(code, exits.FINDING, out)
        self.assertEqual(out.strip(), "1R.0P head xx-1 !1?")

    def test_a_BROKEN_evidence_predicate_is_the_named_divergence_case(self):
        """THE CONCRETE DIVERGENCE CASE the docstring names (lc-45 dispatch
        report, sign-off condition): this verb has no evaluator for an
        `evidence <predicate>` blocker at all, so a READY item whose
        predicate is BROKEN (an unbalanced quote — `/bin/sh -c` exits >=2,
        the >=2-is-BROKEN half of the lane trigger contract, never a quiet
        wait per §3.3) reads as merely "not the head" here, exactly like an
        ordinary wait. `item ready --head` — the authoritative answer this
        verb explicitly defers to — evaluates the SAME predicate and raises
        `FINDING [trigger_broken]` instead, exiting FINDING rather than
        CLEAN. Both sides run for real over the SAME carrier: an assertion
        against only one side could not show the two verbs disagree."""
        carrier = (
            "schema: 2\nbaseline: 2\nadded: 0\ncompacted: 0\n"
            + refusals._blocked_block("xx-1", "READY",
                                      "evidence echo 'unterminated")
            + refusals._blocked_block("xx-2", "READY", "NONE")
        )
        r = self._repo(carrier)

        code, out = self._run(r, "item", "statusline")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(out.strip(), "2R.0P head xx-2", out)

        head_code, head_out = self._run(r, "item", "ready", "--head")
        self.assertEqual(head_code, exits.FINDING, head_out)
        self.assertIn("FINDING [trigger_broken]", head_out, head_out)
        self.assertIn("xx-1 [READY] goal=mitigate  not schedulable", head_out,
                      head_out)


class DecisionBlockerAtClose(unittest.TestCase):
    """lc-55 — `item ready` and `item close` over ONE ledger state.

    THE DIVERGENCE, reproduced on a private clone at 9839f46: an operator
    answers the question with `ledger add decision`, `item ready` reports
    "UNBLOCKED — the ledger ANSWERS this decision" citing the line, and
    `item close` then reports the same blocker "was never answered", writes
    `blocker-moot:` onto the moved body and appends a SECOND `decision:` line
    recording the question moot. One question, two contradictory lines, both
    live in the carrier and neither marked as superseding the other.

    THE MECHANISM IS ONE READER SHORT, not a disagreeing pair. `_blocker_state`
    — what `item ready` calls — resolves a `decision` blocker against
    `ledger.decision_for` (lc-26). `cmd_item_close` read the ledger NOWHERE: it
    took `_effective_blocker`'s type and treated every `decision` blocker as
    unanswered by construction, so its verdict could not depend on the ledger
    state it was writing into. The repo has ONE trigger evaluator for
    `evidence` blockers (CLAUDE.md, "The router, and the ONE trigger
    evaluator") and ONE disposition for `<item-id>` ones; the `decision` type
    had a reader used by exactly one of its two consumers.

    THE ARMS ARE A PAIR AND DIFFER IN THE LEDGER LINE ALONE. Answered: no moot
    record, no second line. Unanswered: the moot record, unchanged — the
    must-not-move half, without which a close that had simply stopped
    recording moot decisions would score identically on the first arm.
    """

    QUESTION = "which window is canonical"
    ANSWER = "the 30-day window is canonical"

    def _repo(self, ledger_text=None, *, amended=False):
        """One READY item blocked on QUESTION, and the ledger state under test.

        The BASE slot form, not the amended one: `_effective_blocker` resolves
        both and this is the shape the reproduction walked.
        """
        blocker = f"decision {self.QUESTION}"
        if amended:
            # THE FORM THE BLOCKER SURVIVES THE MOVE IN. `move_to_done` clears
            # the base `blocked-by:` LINE and does not touch an
            # `amended-blocked-by:` one (lc-90), so only this shape can ask
            # what the closure home holds afterwards.
            body = (refusals._blocked_block("xx-1", "READY", "NONE")
                    .rstrip("\n")
                    + "\namend-reason: 2026-09-13 the desk retyped it\n"
                    + f"amended-blocked-by: 2026-09-13 {blocker}\n")
        else:
            body = refusals._blocked_block("xx-1", "READY", blocker)
        items_text = ("schema: 2\nbaseline: 1\nadded: 0\ncompacted: 0\n"
                      + body)
        r = refusals._Repo(items=items_text, ledger_text=ledger_text)
        self.addCleanup(r.close)
        return r

    def _ledger(self, answer):
        """A ledger whose one `decision:` line carries `answer` for QUESTION.

        Rendered by the ledger module rather than spelled here: a literal
        would be a second spelling of a line shape whose recogniser is what
        the arms are measuring.
        """
        return (ledger.head_text()
                + ledger.render("decision", {"question": self.QUESTION,
                                             "answer": answer}) + "\n")

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

    def _carriers(self, repo):
        return {n: (repo.dir / n).read_text(encoding="utf-8")
                for n in ("ITEMS.md", "ITEMS-DONE.md", "LEDGER.md")}

    def test_an_ANSWERED_decision_records_ANSWERED_never_moot(self):
        """THE RED. At 9839f46 this close wrote the bare question as
        `blocker-moot:` — the form that says nobody ever answered it — onto
        the moved body, and appended `→ moot (closed by xx-1)` beneath the
        answer it had just been given, exiting CLEAN over both.

        THE TWO FORMS DIFFER IN THE FILE, not only in the prose: the answered
        record must be present and the never-answered one ABSENT, the same
        pair `test_a_DROP_records_the_wait_ABANDONED_never_answered` asserts
        one blocker type over."""
        r = self._repo(self._ledger(self.ANSWER))
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        c = self._carriers(r)
        self.assertIn(
            f"blocker-moot: {items.decision_moot_record(self.QUESTION)}",
            c["ITEMS-DONE.md"], c["ITEMS-DONE.md"])
        self.assertNotIn(
            f"blocker-moot: {self.QUESTION}\n", c["ITEMS-DONE.md"],
            "the close recorded an ANSWERED question as never-answered, on a "
            "body `item amend` refuses to touch afterwards:\n" + out)
        self.assertNotIn(
            ledger.moot_answer("xx-1"), c["LEDGER.md"],
            "the close wrote a second, contradictory `decision:` line:\n"
            + c["LEDGER.md"])
        self.assertEqual(
            c["LEDGER.md"].count(f"decision: {self.QUESTION}"), 1,
            "one question, one home:\n" + c["LEDGER.md"])

    def test_ready_and_close_AGREE_on_the_ANSWERED_state(self):
        """The done-criterion itself, both verbs against ONE ledger state —
        the agreement, not either verb's wording. Asserted on the verdict
        SENTENCES the two verbs print, because the contradiction the item
        records was readable in exactly those."""
        r = self._repo(self._ledger(self.ANSWER))
        ready_code, ready_out = self._run(r, "item", "ready", "xx-1")
        self.assertEqual(ready_code, exits.CLEAN, ready_out)
        self.assertIn("UNBLOCKED — the ledger ANSWERS this decision",
                      ready_out, ready_out)
        close_code, close_out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(close_code, exits.CLEAN, close_out)
        self.assertNotIn(
            "was never answered", close_out,
            "`item close` called never-answered what `item ready` had just "
            "read off the same line:\n" + close_out)

    def test_an_UNANSWERED_decision_STILL_records_moot(self):
        """MUST-NOT-MOVE, and the discrimination half of the pair: this arm
        differs from the two above in the ledger's one line and nothing else.
        Without it, a close that had stopped writing moot records altogether
        would pass them both."""
        r = self._repo()
        ready_code, ready_out = self._run(r, "item", "ready", "xx-1")
        self.assertEqual(ready_code, exits.CLEAN, ready_out)
        self.assertIn("BLOCKED — in the OPERATOR's court", ready_out,
                      ready_out)
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        c = self._carriers(r)
        self.assertIn(f"blocker-moot: {self.QUESTION}\n", c["ITEMS-DONE.md"],
                      c["ITEMS-DONE.md"])
        self.assertNotIn(items.decision_moot_record(self.QUESTION),
                         c["ITEMS-DONE.md"],
                         "the answered form on an unanswered question")
        self.assertIn(ledger.moot_answer("xx-1"), c["LEDGER.md"],
                      c["LEDGER.md"])

    def test_ANOTHER_items_moot_line_is_not_an_answer_here(self):
        """MUST-NOT-MOVE over the G4 scoping. A moot line says the question
        died with ONE item; read as an answer it would clear every other item
        waiting on it. `item ready` refuses it by name, and the close reaches
        the same reader with the same `for_item`, so it must refuse it too —
        a close that had taken any matching line as an answer would leave this
        item's own wait unrecorded."""
        r = self._repo(self._ledger(ledger.moot_answer("xx-9")))
        ready_code, ready_out = self._run(r, "item", "ready", "xx-1")
        self.assertEqual(ready_code, exits.CLEAN, ready_out)
        self.assertIn("records this question MOOT", ready_out, ready_out)
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        c = self._carriers(r)
        self.assertIn(f"blocker-moot: {self.QUESTION}", c["ITEMS-DONE.md"],
                      c["ITEMS-DONE.md"])
        self.assertIn(ledger.moot_answer("xx-1"), c["LEDGER.md"],
                      c["LEDGER.md"])

    def test_an_AMENDED_answered_blocker_leaves_the_done_home_CLEAN(self):
        """THE NEIGHBOURING CASE, and the one that caught the first half of
        this fix mid-build. `move_to_done` clears the base `blocked-by:` LINE,
        so a base-slot blocker is gone from the moved body whatever the close
        records — every arm above runs on that form and none of them can see
        this. An `amended-blocked-by:` line SURVIVES the close untouched
        (lc-90), so it is the form that needs the record on the body, and a
        close that wrote nothing for an ANSWERED question left it standing in
        the closure home with nothing to discharge it: `item check` then
        reported `blocked_in_done_home` against a body `item amend` correctly
        refuses to repair. Measured on a private clone before this arm
        existed — the close exited 0 and the next check exited 2."""
        r = self._repo(self._ledger(self.ANSWER), amended=True)
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn(
            f"blocker-moot: {items.decision_moot_record(self.QUESTION)}",
            (r.dir / "ITEMS-DONE.md").read_text(encoding="utf-8"))
        check_code, check_out = self._run(r, "item", "check")
        self.assertEqual(check_code, exits.CLEAN, check_out)
        self.assertNotIn("blocked_in_done_home", check_out, check_out)

    def test_the_ANSWERED_record_discharges_ONLY_the_question_it_NAMES(self):
        """The discrimination arm for the widened discharge. The answered form
        is one more EXACT shape, never a looser predicate: a body carrying the
        record for some OTHER question is still a surviving blocker, and a
        discharge that had merely looked for a `blocker-moot:` line would clear
        every one of them."""
        def home(named):
            return (refusals.EMPTY_DONE
                    + refusals._blocked_block("xx-1", "DONE", "NONE")
                    .rstrip("\n")
                    + "\namend-reason: 2026-09-13 the desk retyped it\n"
                    + f"amended-blocked-by: 2026-09-13 decision {self.QUESTION}"
                    + "\nblocker-moot: " + items.decision_moot_record(named)
                    + "\n")
        one_body = "schema: 2\nbaseline: 1\nadded: 0\ncompacted: 0\n"
        r = refusals._Repo(items=one_body, done=home("some other question"))
        self.addCleanup(r.close)
        code, out = self._run(r, "item", "check")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("blocked_in_done_home", out)
        # The other half of the pair, same fixture shape: the record for the
        # question the blocker DOES name clears it. Without this arm the red
        # above is equally consistent with a discharge that never fires.
        r2 = refusals._Repo(items=one_body, done=home(self.QUESTION))
        self.addCleanup(r2.close)
        code, out = self._run(r2, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("blocked_in_done_home", out)

    def test_an_UNREADABLE_ledger_is_COULD_NOT_VERIFY_not_a_close(self):
        """The third answer, and the third state both verbs must agree on.
        `item ready` already answers COULD NOT VERIFY here. At 9839f46 the
        close exited CLEAN, wrote "was never answered" onto the moved body,
        and CREATED the ledger to hold a moot line about a question nothing
        could check — the assertion is unverifiable and the body is
        unamendable the moment it moves."""
        r = self._repo()
        (r.dir / "LEDGER.md").unlink()
        ready_code, ready_out = self._run(r, "item", "ready", "xx-1")
        self.assertEqual(ready_code, exits.COULD_NOT_VERIFY, ready_out)
        before = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
        code, out = self._run(r, "item", "close", "xx-1")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("COULD NOT VERIFY", out)
        self.assertEqual((r.dir / "ITEMS.md").read_text(encoding="utf-8"),
                         before, "an unverifiable close moved the body anyway")
        self.assertFalse((r.dir / "LEDGER.md").exists(),
                         "the close minted a ledger to hold a moot line it "
                         "could not have checked")


class TheMintTimePredicateLint(unittest.TestCase):
    """`evidence <predicate>` is LINTED at the mint (lc-130).

    THE DEFECT IT KILLS: prose booked into a shell slot. The predicate never
    parses, every `item ready` pass reports it BROKEN, and until someone reads
    that board the item waits in nobody's court — caught by hand, late, in a
    live carrier.

    WHY IT SITS IN `_check_blocker` AND NOT IN THE TWO VERBS THE DESIGN NAMES.
    That function already serves THREE doors — `item add`, `item park` and
    `item amend --blocked-by` — and its own docstring records why: a per-verb
    check covers exactly the verbs somebody remembered. The third door is the
    one a per-verb reading misses, so it has its own arm below.

    WHAT THE FIXTURE PREDICATES CAN DO: nothing. Each one is inert by
    construction — a read of a file every Linux carries, a bare `exit`, or a
    `touch` INSIDE the test's own temp directory. `TheProbeOrdering` below
    proves that claim rather than asserting it: a marker the probe would write
    is present after a predicate that PARSES, and absent after one that does
    not — the pair, not the zero alone.
    """

    #: Prose in a shell slot. The real incident's predicate is a private
    #: carrier's text and does not travel into this public repo; what makes
    #: the case is the FAILURE MODE, and this reproduces it exactly — `sh -n`
    #: exits 2 on the unbalanced parenthesis, before anything is executed.
    PROSE = ("an operating interval has passed since the burst (measure then "
             "cut: the timing rule; the next review is the consumer")
    #: Parses, and exits 0 — refused since lc-164, which is what this
    #: constant's old name (`MINTS`) asserted and its arm now denies. Spelled
    #: as the measured incident's SHAPE rather than as a bare `true`: a test
    #: over a command whose output was discarded, which is how an
    #: unfalsifiable clause reaches a carrier looking like a real check.
    CANNOT_FAIL = "test -z \"$(printf 'a-process' | head -0)\""

    def _run(self, repo, *argv):
        import io, os
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

    def _add(self, repo, predicate):
        return self._run(repo, *(refusals.GOOD_ADD
                                 + ["--blocked-by", f"evidence {predicate}"]))

    def test_a_predicate_that_does_not_PARSE_is_refused_at_item_add(self):
        with refusals._Repo() as r:
            before = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
            code, out = self._add(r, self.PROSE)
            self.assertEqual(
                code, exits.FINDING,
                f"prose in a shell slot was admitted.\n{out}")
            self.assertIn("blocker_predicate_broken", out,
                          f"the refusal names no registry row.\n{out}")
            self.assertIn(
                self.PROSE, out,
                "the refusal does not QUOTE the predicate — the author "
                f"cannot see which text failed.\n{out}")
            self.assertEqual(
                (r.dir / "ITEMS.md").read_text(encoding="utf-8"), before,
                "the carrier was written despite the refusal")

    def test_the_same_predicate_is_refused_at_item_park(self):
        with refusals._Repo(items=refusals.FOUR_BLOCKER_ITEMS) as r:
            before = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
            code, out = self._run(r, "item", "park", "xx-3",
                                  "--blocked-by", f"evidence {self.PROSE}")
            self.assertEqual(code, exits.FINDING, out)
            self.assertIn("blocker_predicate_broken", out, out)
            self.assertEqual(
                (r.dir / "ITEMS.md").read_text(encoding="utf-8"), before,
                "the park wrote the grade over an unparseable predicate")

    def test_the_THIRD_door_amend_is_covered_too(self):
        """The door the design's own table does not name. It is free here
        only because the check sits at the shared function — a per-verb
        repair would have covered the two that were remembered."""
        with refusals._Repo(items=refusals.FOUR_BLOCKER_ITEMS) as r:
            before = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
            code, out = self._run(r, "item", "amend", "xx-3",
                                  "--reason", "the blocker was retyped",
                                  "--blocked-by", f"evidence {self.PROSE}")
            self.assertEqual(code, exits.FINDING, out)
            self.assertIn("blocker_predicate_broken", out, out)
            self.assertEqual(
                (r.dir / "ITEMS.md").read_text(encoding="utf-8"), before,
                "the amendment was appended over an unparseable predicate")

    def test_a_predicate_that_parses_and_exits_2_or_more_is_refused(self):
        """§3.3 RESERVES `>=2` for BROKEN, and the mint reads that reservation
        through the ONE trigger evaluator rather than a second body of its
        own — two readings would disagree about this case first."""
        with refusals._Repo() as r:
            code, out = self._add(r, "exit 7")
            self.assertEqual(code, exits.FINDING,
                             f"a predicate exiting 7 was admitted.\n{out}")
            self.assertIn("blocker_predicate_broken", out, out)
            self.assertIn("exit 7", out,
                          f"the refusal does not quote the predicate.\n{out}")

    def test_a_predicate_exiting_0_IS_REFUSED(self):
        """lc-164 — and this arm asserted the OPPOSITE until today.

        IT WAS `test_a_predicate_exiting_0_MINTS`, reading "a working
        predicate was refused — a guard that fires on legitimate work stops
        the lane (R11)". The sentence is right and its instance was wrong:
        lc-130 asked whether a predicate WORKS and treated 0 and 1 as one
        answer, so an exit-0 predicate stood here as the must-not-move
        control for the parse lint. It is not legitimate work. An evidence
        blocker whose predicate is TRUE at booking blocks nothing — the item
        is schedulable today, or the predicate cannot fail — and the measured
        incident is the second: a `pgrep` piped through `head -0` made the
        clause true for every input, and the item read UNBLOCKED while what
        it waited for had not happened.

        R11's OWN CONTROL DID NOT MOVE: `test_a_predicate_exiting_1_MINTS`
        below is the arm proving this lint does not refuse every evidence
        predicate, and exit 1 — the evidence has not arrived yet — is what
        every legitimate blocker answers at its booking.
        """
        with refusals._Repo() as r:
            before = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
            code, out = self._add(r, self.CANNOT_FAIL)
            self.assertEqual(
                code, exits.FINDING,
                f"a predicate that cannot fail was admitted.\n{out}")
            self.assertIn("blocker_predicate_satisfied_at_booking", out,
                          f"the refusal names no registry row.\n{out}")
            # QUOTED AS THE VERB QUOTES IT (`{detail!r}`), which the sibling
            # arm above could assert as a bare substring only because its
            # fixture carries no quote characters. This predicate does — the
            # incident's shape needs them — so the assertion reads the form
            # the author actually sees rather than one repr never emits.
            self.assertIn(
                repr(self.CANNOT_FAIL), out,
                "the refusal does not QUOTE the predicate — the author "
                f"cannot see which text was refused.\n{out}")
            self.assertEqual(
                (r.dir / "ITEMS.md").read_text(encoding="utf-8"), before,
                "the carrier was written despite the refusal")

    def test_the_refusal_names_BOTH_readings_because_one_run_cannot_split_them(self):
        """The message is the whole deliverable here, so it is asserted.

        A run exiting 0 is consistent with an item already unblocked AND
        with a predicate that cannot fail, and the repairs differ — drop the
        blocker, or rewrite the predicate. An operator told only "this exits
        0" cannot tell which is owed, which is the same failure the route-set
        pair was split to avoid.
        """
        with refusals._Repo() as r:
            _code, out = self._add(r, self.CANNOT_FAIL)
            self.assertIn("schedulable today", out,
                          f"the already-unblocked reading is missing.\n{out}")
            self.assertIn("CANNOT FAIL", out,
                          f"the unfalsifiable reading is missing.\n{out}")

    def test_the_exit_0_refusal_reaches_park_and_amend_too(self):
        """The three doors, as lc-130's own arms established them.

        Free because the grade sits at the shared function — but free is not
        proven, and a later repair keyed to `item add` alone would pass every
        arm above.
        """
        for argv in (["item", "park", "xx-3"], ["item", "amend", "xx-3",
                                                "--reason", "retyped"]):
            with refusals._Repo(items=refusals.FOUR_BLOCKER_ITEMS) as r:
                before = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
                code, out = self._run(r, *(argv + [
                    "--blocked-by", f"evidence {self.CANNOT_FAIL}"]))
                self.assertEqual(code, exits.FINDING,
                                 f"{argv[1]} admitted it.\n{out}")
                self.assertIn("blocker_predicate_satisfied_at_booking", out, out)
                self.assertEqual(
                    (r.dir / "ITEMS.md").read_text(encoding="utf-8"), before,
                    f"{argv[1]} wrote over a predicate that cannot fail")

    def test_a_predicate_exiting_1_MINTS(self):
        """QUIET is the ordinary state of an evidence blocker — the evidence
        has not arrived yet. Refusing it would refuse every blocker booked
        before its evidence exists, which is all of them."""
        with refusals._Repo() as r:
            code, out = self._add(r, "test -f /nonexistent-lifecycle-probe")
            self.assertEqual(code, exits.CLEAN,
                             f"a waiting predicate was refused.\n{out}")

    def test_the_lint_does_NOT_reach_the_other_blocker_TYPES(self):
        """The scope arm. A `decision` blocker and an item-id blocker are
        prose and an id by design; a lint that ran over them would refuse
        every legitimate one of both kinds."""
        with refusals._Repo(items=refusals.FOUR_BLOCKER_ITEMS) as r:
            code, out = self._run(r, *(refusals.GOOD_ADD + [
                "--blocked-by", f"decision {self.PROSE}",
                "--not-derivable", "a preference with no precedent in the ledger — constitutively the operator's",]))
            self.assertEqual(
                code, exits.CLEAN,
                f"the lint reached a `decision` blocker.\n{out}")
            self.assertNotIn("blocker_predicate_broken", out, out)
        with refusals._Repo(items=refusals.FOUR_BLOCKER_ITEMS) as r:
            code, out = self._run(r, *(refusals.GOOD_ADD
                                       + ["--blocked-by", "xx-1"]))
            self.assertEqual(code, exits.CLEAN,
                             f"the lint reached an item-id blocker.\n{out}")


class TheProbeOrdering(unittest.TestCase):
    """`sh -n` FIRST, and the MARKER is what proves it.

    A read of the implementation would say the parse check runs before the
    probe. That is a NON-EVENT claim about execution — "nothing ran" returns
    byte-identically whether the ordering holds or the probe is simply
    broken — so it is answered by an instrument at the effect site: a marker
    file the predicate would create. The zero counts only as a PAIR, with a
    known positive beside it.
    """

    def _add(self, repo, predicate):
        import io, os
        from contextlib import redirect_stdout
        from lifecycle_core import cli as cli_mod
        here = os.getcwd()
        try:
            os.chdir(str(repo.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(
                    ["--repo", str(repo.dir)] + refusals.GOOD_ADD
                    + ["--blocked-by", f"evidence {predicate}"])
        finally:
            os.chdir(here)
        return code, buf.getvalue()

    def test_a_PARSING_predicate_is_probed_and_a_BROKEN_one_never_runs(self):
        with refusals._Repo() as r:
            positive = r.dir / "marker-probe-ran"
            # KNOWN POSITIVE: it parses, it runs, and running it leaves the
            # marker. Without this arm the negative below is equally
            # consistent with a probe that never runs at all.
            #
            # THE `exit 1` IS lc-164 AND NOT DECORATION. This arm's subject is
            # ORDERING — parse before probe — and it says so through the mint's
            # verdict plus the marker. A bare `touch` exits 0, which lc-164
            # now refuses, so leaving it would have turned an ordering arm into
            # a second reading of that refusal and lost the CLEAN assertion
            # that makes the marker mean "probed and admitted". The predicate
            # still parses and still runs; only its ANSWER moved, to the one
            # this lint calls ordinary waiting.
            code, out = self._add(r, f"touch {positive}; exit 1")
            self.assertEqual(code, exits.CLEAN, out)
            self.assertTrue(
                positive.exists(),
                "the probe did not run — so the negative arm below proves "
                f"nothing about ordering.\n{out}")
        with refusals._Repo() as r:
            negative = r.dir / "marker-must-not-exist"
            # The SAME touch, followed by text that cannot parse. `sh -n`
            # rejects the whole program, so nothing in it executes.
            code, out = self._add(r, f"touch {negative}; if ((( ")
            self.assertEqual(code, exits.FINDING, out)
            self.assertFalse(
                negative.exists(),
                "an unparseable predicate was EXECUTED — the parse check "
                f"does not run first.\n{out}")


class TheCarrierVerbDispatchHasNoDefault(unittest.TestCase):
    """lc-146: an action with no branch of its own must not run CLOSE.

    `_carrier_verb` ended in an unguarded `return verbs.cmd_item_close(...)`,
    so whatever the CALLER's action tuple admitted without a branch here ran
    a two-file MOVE under that action's name. The safety was a property of a
    tuple someone else edits; the risk sat in this function. These arms hold
    the callee to it directly, which is why they drive `_carrier_verb` rather
    than the CLI surface — argparse `choices` would refuse the very input the
    hazard is about, so a surface-level arm cannot reach it at all.

    PER ACTION, NEVER IN AGGREGATE. "Nothing unexpected was called" passes
    against a build that refuses everything, which is the other way to make
    the unknown-action arm green and the wrong one.
    """

    #: action → the function the dispatch must reach. HAND-WRITTEN BECAUSE IT
    #: IS THE CLAIM: a table derived from cli.py's own branches would move
    #: with the mutant and stay green on exactly the rewiring these arms
    #: exist to catch. Its COMPLETENESS against the caller is a separate arm,
    #: and that one IS derived from the source.
    DESTINATIONS = {
        "add": "cmd_item_add",
        "amend": "cmd_item_amend",
        "promote": "cmd_item_promote",
        "ready": "cmd_item_ready",
        "park": "cmd_item_park",
        "close": "cmd_item_close",
        "compact": "cmd_item_compact",
        "ratio": "cmd_item_ratio",
        "statusline": "cmd_item_statusline",
        "supersede-closure": "cmd_item_supersede_closure",
    }

    #: `compact` lives in `retire`, every other destination in `verbs`, and
    #: `cmd_item_head` is the `ready --head` fork. Recorded here so the patch
    #: set is the WHOLE set of functions the dispatch can reach: one left
    #: unpatched would run for real, and an arm that wrote to the fixture
    #: would be measuring something other than where the call went.
    IN_RETIRE = ("cmd_item_compact",)
    ALSO_PATCHED = ("cmd_item_head",)

    def _drive(self, repo, action, **extra):
        """`(code, calls, output)` for one `_carrier_verb` invocation.

        Every reachable destination is replaced by a recorder, so WHICH verb
        the dispatch chose is read off the call it made rather than off a
        side effect it left.
        """
        import argparse
        import contextlib
        from unittest import mock
        from lifecycle_core import cli as cli_mod
        from lifecycle_core import retire as retire_mod

        calls = []

        def recorder(label):
            def _called(a, o, c):
                calls.append(label)
                return exits.CLEAN
            return _called

        kwargs = {"repo": str(repo.dir), "item_action": action,
                  "ident": "xx-1", "head": False}
        kwargs.update(extra)
        args = argparse.Namespace(**kwargs)
        lines = []
        with contextlib.ExitStack() as stack:
            for act, name in self.DESTINATIONS.items():
                mod = retire_mod if name in self.IN_RETIRE else verbs
                stack.enter_context(
                    mock.patch.object(mod, name, recorder(act)))
            for name in self.ALSO_PATCHED:
                stack.enter_context(
                    mock.patch.object(verbs, name, recorder(name)))
            code = cli_mod._carrier_verb(args, lines.append)
        return code, calls, "\n".join(lines)

    def _caller_actions(self):
        """The action set the CALLER admits, read out of cli.py's own syntax
        tree — never restated here, which is a comparison basis that cannot
        age loudly: the tuple gains an action and a restated copy stays
        green while covering one member fewer."""
        import ast
        from lifecycle_core import cli as cli_mod

        source = Path(cli_mod.__file__).read_text(encoding="utf-8")
        found = []
        for node in ast.walk(ast.parse(source)):
            if not isinstance(node, ast.Compare):
                continue
            if len(node.ops) != 1 or not isinstance(node.ops[0], ast.In):
                continue
            left = node.left
            if not (isinstance(left, ast.Attribute)
                    and left.attr == "item_action"):
                continue
            right = node.comparators[0]
            if not isinstance(right, (ast.Tuple, ast.List, ast.Set)):
                continue
            found.append({e.value for e in right.elts
                          if isinstance(e, ast.Constant)})
        return found

    def test_an_UNBRANCHED_action_never_reaches_the_destructive_close(self):
        """The defect itself.

        THE ARM CARRIES ITS OWN POSITIVE CONTROL, and without it the negative
        below proves nothing: `_carrier_verb` returns before any dispatch
        when the context does not resolve, and "no verb was called" is then
        true for a reason that has nothing to do with the dispatch. So the
        SAME fixture drives a known action first and that call must be seen.
        """
        with refusals._Repo() as r:
            code, calls, out = self._drive(r, "park")
            self.assertEqual(
                calls, ["park"],
                "the fixture never reached the dispatch at all, so the "
                f"unknown-action arm below would be quiet for free.\n{out}")
            self.assertEqual(code, exits.CLEAN, out)

            code, calls, out = self._drive(r, "quarantine")
            self.assertNotIn(
                "close", calls,
                "an action with NO BRANCH of its own reached cmd_item_close "
                "— a two-file MOVE ran under another verb's name, which is "
                f"the whole of lc-146.\n{out}")
            self.assertEqual(
                calls, [],
                f"an unrecognised action dispatched to a verb.\n{out}")
            self.assertEqual(
                code, exits.COULD_NOT_VERIFY,
                "an action this dispatch does not carry is COULD NOT "
                f"VERIFY, never an act.\n{out}")
            self.assertIn("COULD NOT VERIFY", out, out)

    def test_every_action_the_caller_admits_reaches_ITS_OWN_verb(self):
        """MUST-NOT-MOVE, one subTest per action: an aggregate arm passes
        against a build that refuses everything."""
        with refusals._Repo() as r:
            for action in sorted(self.DESTINATIONS):
                with self.subTest(action=action):
                    code, calls, out = self._drive(r, action)
                    self.assertEqual(
                        calls, [action],
                        f"`item {action}` no longer reaches "
                        f"{self.DESTINATIONS[action]}.\n{out}")
                    self.assertEqual(code, exits.CLEAN, out)

    def test_the_READY_fork_keeps_both_of_its_own_answers(self):
        """The branch this edit sits beside: `--head` is a different verb and
        an id-less run is a refusal, not a pick."""
        with refusals._Repo() as r:
            code, calls, out = self._drive(r, "ready", head=True)
            self.assertEqual(calls, ["cmd_item_head"], out)
            self.assertEqual(code, exits.CLEAN, out)

            code, calls, out = self._drive(r, "ready", ident=None)
            self.assertEqual(
                calls, [],
                f"an id-less `item ready` dispatched to a verb.\n{out}")
            self.assertEqual(code, exits.COULD_NOT_VERIFY, out)

    def test_the_destination_table_covers_every_action_the_caller_admits(self):
        """The coverage half, derived from the source.

        An action added to the caller's tuple without a destination here is
        an action the arms above never walk — and after lc-146 it is also an
        action the dispatch refuses, so this arm is where that shows up.
        """
        found = self._caller_actions()
        self.assertEqual(
            len(found), 1,
            "cli.py carries "
            f"{len(found)} `item_action in <tuple>` comparisons; this arm "
            "reads one. Zero means the extraction stopped matching the "
            "source and every assertion below it is vacuous.")
        admitted = found[0]
        self.assertTrue(
            admitted,
            "the extracted action set is EMPTY, which reads exactly like a "
            "caller that admits nothing — an unread instrument, not a pass.")
        self.assertEqual(
            admitted, set(self.DESTINATIONS),
            "the caller's action tuple and this file's destination table "
            "have parted company.")


class TheCommitAttributionTrailer(unittest.TestCase):
    """`commit_paths` writes AI attribution, and writes it whole or not at all.

    THE DEFECT THIS ARM FIXES was found in operation, not predicted: two
    commits in another repo (`6fe939f`, `1e451a1`) produced by `item amend`
    carried no `Co-Authored-By` trailer. The reporting peer proposed checking
    `item add` and `item close` as separate axes; the surface answers that by
    construction instead — `commit_paths` is the ONE commit implementation in
    this package and has nine call sites, so every carrier write shared the
    defect and no verb ever differed from another.

    WHY THE TOOL CANNOT COMPOSE THE TRAILER ITSELF, which is the whole reason
    this is an env var and not a constant. The block names a MODEL and a
    SESSION URL. Both belong to whichever session invoked the verb, and
    neither is knowable from inside a CLI process. A constant compiled in
    here would attribute every commit made by every future session to
    whatever model happened to be current on the day this line was written —
    a label the checked party writes about itself, which is precisely the
    class the arc this fix belongs to exists to remove.

    WHY A HALF-BLOCK IS DROPPED RATHER THAN WRITTEN, and this is the arm that
    would not exist without reading the consumer. This machine's global
    pre-push hook (`core.hooksPath` -> dotfiles/git/hooks) decides
    BOOKED vs UNBOOKED by exactly this predicate: `_ist_subagent_trailer`
    counts a commit as an unbooked subagent commit when it carries
    `Co-Authored-By: Claude ` AND LACKS `Claude-Session:`. So a trailer
    supplied with only its first half does not merely under-attribute — it
    FORGES the shape a different guard acts on, in a repo whose false-fire
    budget that hook's own comments record as already spent. Dropping it is
    the only option that cannot manufacture a false positive there.

    AND IT IS A WARNING, NEVER A REFUSAL. Refusing the commit would leave the
    carrier's halves written to disk and uncommitted — the exact split
    `commit_paths` exists to prevent — to punish an unset environment
    variable. The operator's decision was commit-bare-and-warn, and the
    malformed case inherits it: an absent attribution is already named on
    every push by the hook above, so the gap stays measured either way.
    """

    COMPLETE = ("Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>\n"
                "Claude-Session: https://claude.ai/code/session_example")

    def test_unset_env_yields_no_block_and_says_so(self):
        block, warning = verbs.attribution_block({})
        self.assertEqual(block, "")
        self.assertIn(verbs.COMMIT_TRAILER_ENV, warning)

    def test_a_complete_block_passes_through_untouched(self):
        block, warning = verbs.attribution_block(
            {verbs.COMMIT_TRAILER_ENV: self.COMPLETE})
        self.assertEqual(block, self.COMPLETE)
        self.assertEqual(warning, "")

    def test_the_half_block_is_dropped_and_the_reason_is_named(self):
        """The forged-unbooked-subagent shape never reaches a commit."""
        half = "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
        block, warning = verbs.attribution_block(
            {verbs.COMMIT_TRAILER_ENV: half})
        self.assertEqual(block, "")
        self.assertIn("Claude-Session:", warning)

    def test_a_human_coauthor_is_not_the_forged_shape(self):
        """The discriminating arm: the guard's predicate is `Claude `, so an
        ordinary human co-author trailer must pass. Without this, a predicate
        keyed on `Co-Authored-By:` alone would read as correct on all three
        arms above while silently refusing every human co-authored commit."""
        human = "Co-Authored-By: Someone Real <someone@example.invalid>"
        block, warning = verbs.attribution_block(
            {verbs.COMMIT_TRAILER_ENV: human})
        self.assertEqual(block, human)
        self.assertEqual(warning, "")

    def test_the_trailer_reaches_the_actual_commit_object(self):
        """AT THE EFFECT SITE. The three arms above grade a pure function;
        this one grades the thing the defect was about — what `git log`
        shows for a commit the tool actually made. A helper returning the
        right string proves nothing if the caller drops it."""
        import os
        import subprocess
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for cmd in (["init", "-q"],
                        ["config", "user.email", "t@example.invalid"],
                        ["config", "user.name", "T"],
                        ["config", "commit.gpgsign", "false"]):
                subprocess.run(["git", "-C", str(root)] + cmd, check=True,
                               capture_output=True)
            f = root / "carrier.md"
            f.write_text("body\n")
            subprocess.run(["git", "-C", str(root), "add", "carrier.md"],
                           check=True, capture_output=True)

            ctx = verbs.Ctx(repo=root, declaration={}, prefix="xx",
                            items_path=root / "ITEMS.md",
                            done_path=root / "ITEMS-DONE.md",
                            ledger_path=root / "LEDGER.md")

            said = []
            old = os.environ.get(verbs.COMMIT_TRAILER_ENV)
            os.environ[verbs.COMMIT_TRAILER_ENV] = self.COMPLETE
            try:
                code = verbs.commit_paths(ctx, (f,), "a carrier write",
                                          said.append)
            finally:
                if old is None:
                    os.environ.pop(verbs.COMMIT_TRAILER_ENV, None)
                else:
                    os.environ[verbs.COMMIT_TRAILER_ENV] = old

            self.assertEqual(code, exits.CLEAN, said)
            body = subprocess.run(
                ["git", "-C", str(root), "log", "-1", "--format=%B"],
                capture_output=True, text=True).stdout
            self.assertIn("Co-Authored-By: Claude Opus 5", body)
            self.assertIn("Claude-Session:", body)
            self.assertIn("a carrier write", body)


if __name__ == "__main__":
    unittest.main()


class ConditionalSlotsReachAllThreeDoors(unittest.TestCase):
    """The conditional blocker slots are written by every door that DEMANDS
    them — `item add`, `item park`, `item amend`.

    THE DEFECT THIS PINS, measured at the effect site 2026-09-19 and found by
    the slot's own first real consumer rather than by review: `_check_blocker`
    is reached by all three doors and all three demand the value; only `item
    add` persisted it. `item park` validated the statement and DROPPED it;
    `item amend` refused outright, because the slots were absent from
    `AMENDABLE_SLOTS`.

    THE MECHANISM IS THE DOCSTRING OF THE FUNCTION ITS AUTHOR WAS EDITING.
    `_check_blocker` says the CHECK lives there because "a per-verb check
    would have covered exactly the verbs somebody remembered" — and the
    persistence was then written per-verb, covering exactly the verb its
    author remembered.

    RED-FIRST PER DOOR, never one arm for the class: a single arm would
    certify the door that fired and not its variants, which is the same
    reach defect one level up — and it is the defect this case exists to
    repair, so committing it here would be the test inheriting the bug.
    """

    WHY = "constitutively the operator's — a preference about scope"
    ARMS = "positive `true` 0 | negative `false` 1"
    DQ = "decision which instrument the arc adopts"
    EQ = "evidence test -f /tmp/definitely-not-there"

    def _repo(self, **kw):
        r = refusals._Repo(items=refusals.SEED_ITEMS, **kw)
        self.addCleanup(r.close)
        return r

    def _run(self, repo, *argv):
        import io, os
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

    def _slot(self, repo, ident, slot):
        text = (repo.dir / "ITEMS.md").read_text(encoding="utf-8")
        it = next((i for i in items.parse(text).items if i.ident == ident),
                  None)
        self.assertIsNotNone(it, f"{ident} is not in the carrier")
        return it.slots.get(slot)

    def _ident(self, out):
        import re
        m = re.search(r"added (\S+) \[", out)
        self.assertIsNotNone(m, f"no id in add output:\n{out}")
        return m.group(1)

    # --- door 1: add (this one already worked; it is the CONTROL) ----------

    def test_ADD_persists_both_slots(self):
        """The control arm. It passed before this repair and must keep
        passing — a fix that moved the working door while repairing the
        broken ones would be indistinguishable from a fix that worked."""
        r = self._repo()
        code, out = self._run(r, "item", "add", "--requirement",
                              "the add door control for slot reach",
                              "--goal", "mitigate", "--write-set",
                              "tools/a.py,tools/b.py", "--done-criterion",
                              "red then green", "--evidence",
                              "MEASURED: at the desk", "--blocked-by", self.DQ,
                              "--not-derivable", self.WHY, "--grade", "PARKED",
                              "--join", "new", "--absence", "probe")
        self.assertEqual(code, exits.CLEAN, out)
        got = self._slot(r, self._ident(out), "not-derivable")
        self.assertIsNotNone(got, f"the add door dropped the statement\n{out}")
        self.assertIn(self.WHY, got)

    # --- door 2: park -----------------------------------------------------

    def test_PARK_persists_the_derivability_statement(self):
        r = self._repo()
        code, out = self._run(r, "item", "add", "--requirement",
                              "the park door reach case", "--goal", "mitigate",
                              "--write-set", "tools/a.py,tools/b.py",
                              "--done-criterion", "red then green",
                              "--evidence", "MEASURED: at the desk",
                              "--blocked-by", "NONE", "--grade", "NEW",
                              "--join", "new", "--absence", "probe")
        self.assertEqual(code, exits.CLEAN, out)
        ident = self._ident(out)
        code, out = self._run(r, "item", "park", ident, "--blocked-by",
                              self.DQ, "--not-derivable", self.WHY)
        self.assertEqual(code, exits.CLEAN, out)
        got = self._slot(r, ident, "not-derivable")
        self.assertIsNotNone(
            got, f"PARK demanded the statement and dropped it.\n{out}")
        self.assertIn(self.WHY, got)

    def test_PARK_persists_the_exercise_record(self):
        r = self._repo()
        code, out = self._run(r, "item", "add", "--requirement",
                              "the park door exercise case", "--goal",
                              "mitigate", "--write-set",
                              "tools/a.py,tools/b.py", "--done-criterion",
                              "red then green", "--evidence",
                              "MEASURED: at the desk", "--blocked-by", "NONE",
                              "--grade", "NEW", "--join", "new", "--absence",
                              "probe")
        self.assertEqual(code, exits.CLEAN, out)
        ident = self._ident(out)
        code, out = self._run(r, "item", "park", ident, "--blocked-by",
                              self.EQ, "--blocker-exercise", self.ARMS)
        self.assertEqual(code, exits.CLEAN, out)
        got = self._slot(r, ident, "blocker-exercise")
        self.assertIsNotNone(
            got, f"PARK dropped the exercise record.\n{out}")
        self.assertIn("negative", got)

    def test_PARK_writes_NOTHING_where_the_blocker_type_does_not_match(self):
        """CONTROL for the park door: the misplacement refusals must stay
        unreachable THROUGH THE VERBS. A door that wrote the slot beside the
        wrong blocker would mint a finding the author could not have caused."""
        r = self._repo()
        code, out = self._run(r, "item", "add", "--requirement",
                              "the park door control case", "--goal",
                              "mitigate", "--write-set",
                              "tools/a.py,tools/b.py", "--done-criterion",
                              "red then green", "--evidence",
                              "MEASURED: at the desk", "--blocked-by", "NONE",
                              "--grade", "NEW", "--join", "new", "--absence",
                              "probe")
        ident = self._ident(out)
        # A DECISION blocker with an EXERCISE record offered: wrong pairing.
        code, out = self._run(r, "item", "park", ident, "--blocked-by",
                              self.DQ, "--not-derivable", self.WHY,
                              "--blocker-exercise", self.ARMS)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIsNone(
            self._slot(r, ident, "blocker-exercise"),
            "park wrote an exercise record beside a decision blocker")
        self.assertIsNotNone(self._slot(r, ident, "not-derivable"))

    # --- door 3: amend ----------------------------------------------------

    def test_AMEND_can_write_the_derivability_statement(self):
        r = self._repo()
        code, out = self._run(r, "item", "add", "--requirement",
                              "the amend door reach case", "--goal",
                              "mitigate", "--write-set",
                              "tools/a.py,tools/b.py", "--done-criterion",
                              "red then green", "--evidence",
                              "MEASURED: at the desk", "--blocked-by", self.DQ,
                              "--not-derivable", "the original statement",
                              "--grade", "PARKED", "--join", "new",
                              "--absence", "probe")
        self.assertEqual(code, exits.CLEAN, out)
        ident = self._ident(out)
        code, out = self._run(r, "item", "amend", ident, "--reason",
                              "the statement was wrong and is corrected",
                              "--not-derivable", self.WHY)
        self.assertEqual(
            code, exits.CLEAN,
            f"AMEND refused to write a slot it demands.\n{out}")
        text = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
        self.assertIn(self.WHY, text, "the amended statement is not on disk")

    def test_AMEND_can_ADD_the_slot_to_a_block_that_never_had_it(self):
        """The insertion half, and the case lc-52 actually is: a block parked
        before the slot existed carries no line to rewrite. `_set_slots`
        rewrites existing lines ONLY, so without an insert this door repairs
        nothing for exactly the population that needs repairing."""
        r = self._repo()
        code, out = self._run(r, "item", "add", "--requirement",
                              "the amend insertion case", "--goal",
                              "mitigate", "--write-set",
                              "tools/a.py,tools/b.py", "--done-criterion",
                              "red then green", "--evidence",
                              "MEASURED: at the desk", "--blocked-by", "NONE",
                              "--grade", "NEW", "--join", "new", "--absence",
                              "probe")
        ident = self._ident(out)
        code, out = self._run(r, "item", "amend", ident, "--reason",
                              "retype the blocker and state its derivability",
                              "--blocked-by", self.DQ,
                              "--not-derivable", self.WHY)
        self.assertEqual(code, exits.CLEAN, out)
        text = (r.dir / "ITEMS.md").read_text(encoding="utf-8")
        self.assertIn(self.WHY, text,
                      "amend could not ADD the slot to a block lacking it")
        code, out = self._run(r, "item", "check")
        self.assertNotIn("item_shape", out,
                         f"the inserted slot broke the block's shape\n{out}")


class KindMomentsTest(unittest.TestCase):
    """`kind moments` — the O6 evaluation half, wired (lc-243 W1 act 1).

    THE ROSTER PAIR PROVES THE TWO FINDINGS and nothing else: plant BROKEN,
    plant MALFORMED, each against a control. What it cannot reach is the
    verdict LINE's honesty and the two absence arms, and those are exactly
    where this verb could report a pass-shaped number over nothing — a run
    with no kinds, a run with no reader entries, and a CLEAN whose moments
    were all UNDECLARED so no predicate ever ran.
    """

    def _kinds(self, reader):
        d = json.loads(json.dumps(refusals.GOOD_DECLARATION))
        d["kinds"]["items"]["reader"] = reader
        return d

    def _run(self, doc, repo=None):
        buf = []
        code = verbs.cmd_kind_moments(None, buf.append, repo, doc)
        return code, "\n".join(buf)

    def test_a_declaration_with_NO_KINDS_is_could_not_verify(self):
        code, out = self._run({"kinds": {}})
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("registers no kinds", out)

    def test_kinds_that_declare_NO_READER_are_could_not_verify(self):
        """Zero evaluations is not zero problems. Both print as a zero."""
        d = json.loads(json.dumps(refusals.GOOD_DECLARATION))
        d["kinds"]["items"].pop("reader", None)
        code, out = self._run(d)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("NOT ONE declares a reader entry", out)

    def test_an_ABSENT_when_is_UNDECLARED_and_never_a_finding(self):
        """Law 11's arm. Nearly every kind in this repo is this case, so a
        row grading absence would fire on the whole registry at once."""
        code, out = self._run(self._kinds(["session", "verb:item ready"]))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("UNDECLARED", out)
        self.assertNotIn("FINDING", out)

    def test_the_CLEAN_line_separates_declared_from_EXECUTED(self):
        """The assurance-wider-than-predicate arm, and the one this verb
        would otherwise fail: a registry whose moments are all UNDECLARED
        reads `50 moments ... CLEAN`, which a reader takes for fifty
        predicates that answered. The second number is what refuses that."""
        code, out = self._run(self._kinds(["session", "verb:item ready"]))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("2 declared moment(s)", out)
        self.assertIn("0 of them EXECUTED", out)

    def test_an_EXECUTED_moment_is_counted_as_executed(self):
        """The control direction: with a real predicate the second number
        MOVES. Without this arm the assertion above is satisfied by a verb
        that can never count an execution at all."""
        code, out = self._run(
            self._kinds([{"reader": "session", "when": "predicate true"}]))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("1 of them EXECUTED", out)
        self.assertIn("FIRE", out)

    def test_broken_and_malformed_are_SEPARATE_findings(self):
        """One input of each, together: the summary must name both counts
        apart. A single folded row would report `2 problems` and hand one
        word to two different repairs."""
        code, out = self._run(self._kinds([
            {"reader": "session", "when": "predicate exit 2"},
            {"reader": "verb:item ready", "when": "predicate true"},
        ]))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [reader_moment_broken]", out)
        self.assertIn("FINDING [reader_moment_malformed]", out)
        self.assertIn("1 broken", out)
        self.assertIn("1 malformed", out)
