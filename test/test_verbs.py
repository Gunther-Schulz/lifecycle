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

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits, items, refusals, verbs  # noqa: E402

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
                              "--evidence", "the wave-4 measurement",
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

    def _add(self, blocker):
        return refusals._cli(refusals.GOOD_ADD + ["--blocked-by", blocker])

    def _park(self, blocker):
        return refusals._cli(["item", "park", "xx-1", "--blocked-by", blocker],
                             items=refusals.SEED_ITEMS)

    def _amend(self, blocker):
        return refusals._cli(
            ["item", "amend", "xx-1", "--blocked-by", blocker,
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
        separator rather than on the TYPE would fire here."""
        self._accepted(self._add("evidence " + self.DF_135[len("decision "):]),
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
        repo = Path("/home/g/dev/Gunther-Schulz/dotfiles")
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


if __name__ == "__main__":
    unittest.main()
