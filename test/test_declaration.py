"""The repository declaration's registered homes stay sweep-complete."""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]

# THE PACKAGE, IMPORTED HERE SINCE lc-182. This module used to read the
# declaration as JSON and shell out, so it needed no import; the desk-state
# scope arms drive the roster helper directly, which is what lets them run
# the SAME arrangement the row runs rather than a second spelling of it.
sys.path.insert(0, str(ROOT / "plugin" / "cli"))

from lifecycle_core import declaration as decl, exits, refusals  # noqa: E402
from lifecycle_core import lanes as lanes_mod  # noqa: E402


class DeclaredHomesSweep(unittest.TestCase):
    def test_declared_homes_keep_sweep_clean_and_claim_future_directives(self):
        """This pins the outcome, not today's number of directive files."""
        declaration = json.loads(
            (ROOT / ".claude" / "lifecycle.json").read_text(encoding="utf-8")
        )
        kinds = declaration["kinds"]

        self.assertEqual(kinds["directives"]["home"], "docs/directives/*.md")
        self.assertEqual(kinds["workflow definitions"]["home"],
                         "plugin/workflows")
        # DERIVED FROM THE VOCABULARY, NOT RESTATED BESIDE IT. These read
        # as a literal six-member set until the seventh stage arrives, and
        # then they are two more places that must be found by hand. The
        # module owns the list; this asserts the kind carries all of it.
        self.assertEqual(set(kinds["directives"]), set(decl.KIND_STAGES))
        self.assertEqual(set(kinds["workflow definitions"]),
                         set(decl.KIND_STAGES))

        run = subprocess.run(
            ["python3", "plugin/cli/lifecycle", "kind", "sweep"],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("kind sweep: CLEAN", run.stdout)
        self.assertNotIn("plugin/skills/.gitkeep", run.stdout)


if __name__ == "__main__":
    unittest.main()


class InvestigationRecordsAreARegisteredKind(unittest.TestCase):
    """lc-166 — invariant 1 reaching a home the tracked-file sweep cannot see.

    `kind sweep` walks TRACKED files, and the investigation record lives in
    XDG state outside every repo on purpose: no repo dirtied, no permission
    dialog from the `.claude`-shape protection, and it survives across
    branches. That design is right, and its consequence is that the sweep
    structurally cannot reach these files — so a shipped verb
    (`lifecycle record check`) was grading a kind no declaration governed.
    """

    def _check(self, tmp, *, declare, write_record=True):
        """`declaration.check` over a scratch repo, records home redirected."""
        import os
        import sys
        sys.path.insert(0, str(ROOT / "plugin" / "cli"))
        from lifecycle_core import declaration as decl

        repo = tmp / "repo"
        repo.mkdir(parents=True, exist_ok=True)
        doc = {"kinds": {}}
        if declare:
            doc["kinds"]["investigation records"] = {
                "home": "$XDG_STATE_HOME/claude/investigations/repo--*.md",
                "writer": "session", "reader": ["session"],
                "staleness": "change-coupling", "exit": {"action": "never"},
                "growth": "unbounded-with-reason",
            }
        if write_record:
            home = tmp / "state" / "claude" / "investigations"
            home.mkdir(parents=True, exist_ok=True)
            (home / f"{repo.name}--arc.md").write_text("# r\n", encoding="utf-8")

        res = decl.Result(decl.exits.CLEAN)
        old = os.environ.get("XDG_STATE_HOME")
        os.environ["XDG_STATE_HOME"] = str(tmp / "state")
        try:
            decl.check_records_kind_declared(repo, doc, res)
        finally:
            if old is None:
                os.environ.pop("XDG_STATE_HOME", None)
            else:
                os.environ["XDG_STATE_HOME"] = old
        return [f.row for f in res.findings]

    def _tmp(self):
        import shutil
        import tempfile
        d = Path(tempfile.mkdtemp(prefix="lc166-"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def test_records_without_a_kind_are_a_finding(self):
        self.assertIn("records_kind_undeclared", self._check(self._tmp(),
                                                             declare=False))

    def test_the_same_records_with_the_kind_declared_are_clean(self):
        """The pair: same records present, the DECLARATION is what differs."""
        self.assertEqual(self._check(self._tmp(), declare=True), [])

    def test_a_repo_with_no_records_is_silent(self):
        """The over-fire arm. A repo that never opened an investigation owes
        no kind, and a check firing there would land on every repo in the
        roster — a guard on legitimate work, which stops the lane."""
        self.assertEqual(
            self._check(self._tmp(), declare=False, write_record=False), [])

    def test_this_repo_declares_every_stage(self):
        declaration = json.loads(
            (ROOT / ".claude" / "lifecycle.json").read_text(encoding="utf-8"))
        kind = declaration["kinds"]["investigation records"]
        self.assertEqual(sorted(kind), sorted(decl.KIND_STAGES))
        self.assertIn("claude/investigations", kind["home"])
        # THE FILES NEVER MOVE INTO ANY TREE — the exit is graduation of the
        # record's CONTENT, and a `move` here would undo the three benefits
        # the home exists for.
        self.assertEqual(kind["exit"]["action"], "never")


class DeskStateIsScopedToTheRepoThatWroteIt(unittest.TestCase):
    """lc-182 — the detector lc-171 could not have, and the arm it failed.

    THE WITHDRAWN CUT ASKED ONLY WHETHER FILES EXIST. Desk state is
    machine-wide, so that check demanded every repo declare the kind because
    SOME OTHER repo's session had written a file: the roster went from CLEAN
    to 22 rows COULD NOT VERIFY in one run, every one a declaration row
    running `kind check` over a scratch repo. Law 11's guard firing on
    legitimate work, and the repair was a SCOPE rather than a softer
    predicate — the writer now records its repo, on the fire log's own idiom.

    THE SECOND ARM IS THE POINT. A row carries one pair, and that pair proves
    the refusal's own axis (declared or not); this class carries the REACH
    arm, which is the one that was wrong before and which no green row would
    have caught.
    """

    def _run(self, *, declare, mine):
        return refusals._desk_state_kind_run(declare=declare, mine=mine)

    def test_a_repo_that_wrote_desk_state_and_declares_no_kind_FIRES(self):
        fired = self._run(declare=False, mine=True)
        self.assertEqual(fired.code, exits.FINDING, fired.output)
        self.assertIn("desk_state_kind_undeclared", fired.output)

    def test_declaring_the_kind_clears_it(self):
        fired = self._run(declare=True, mine=True)
        self.assertEqual(fired.code, exits.CLEAN, fired.output)

    def test_ANOTHER_repos_desk_state_does_NOT_fire_here(self):
        """THE ARM THE FIRST CUT FAILED, and the whole reason lc-182 exists.

        The file is present, the kind is undeclared, and this repo wrote
        none of it — so the check must stay silent. A detector that fired
        here would report a finding in every repo on the machine the moment
        any one desk stored state.
        """
        fired = self._run(declare=False, mine=False)
        self.assertEqual(fired.code, exits.CLEAN, fired.output)
        self.assertNotIn("desk_state_kind_undeclared", fired.output)

    def test_the_writer_records_the_repo_so_the_scope_exists_at_all(self):
        """The half in `desk.py`: without this key the scope above is not
        computable, and the check would have to guess — which is how the
        withdrawn cut over-fired."""
        import inspect
        from lifecycle_core import desk as desk_mod
        src = inspect.getsource(desk_mod.cmd_desk_state)
        self.assertIn('"repo": str(repo)', src,
                      "the desk-state writer no longer records its repo, so "
                      "nothing can scope a machine-wide kind to one repo")


class TheRegistryDigest(unittest.TestCase):
    """lc-219: the MAP a session holds — one line per kind.

    Twenty of twenty-five kinds declare `reader: session` and no command fires
    those reads, so the registry goes in front of the session instead. These
    three arms are the ones the ruling named, and the second is the one that
    matters: a home that cannot be RESOLVED must render COULD NOT VERIFY with
    its reason and never `0 file(s)`, because a zero and an unreadable home
    are the same string to a reader and this block is trusted at a glance.
    """

    def _repo(self, kinds):
        d = Path(tempfile.mkdtemp(prefix="lc219-"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        doc = json.loads(json.dumps(refusals.GOOD_FULL_DECLARATION))
        doc["kinds"] = kinds
        (d / ".claude").mkdir()
        (d / ".claude" / "lifecycle.json").write_text(json.dumps(doc),
                                                      encoding="utf-8")
        return d, doc

    @staticmethod
    def _kind(home, reader):
        return {"home": home, "writer": "session", "reader": reader,
                "staleness": "none, declared why: fixture",
                "exit": {"action": "never", "recording-act": "fixture"},
                "growth": "unbounded-with-reason — fixture",
                "trigger": "none, declared why: fixture"}

    def test_a_planted_member_moves_the_count_AND_the_newest_name(self):
        """The counts are what make it bite. A bare map would name the
        directory and a session would still not reach the document."""
        d, doc = self._repo({"notes": self._kind("notes/*.md", ["session"])})
        (d / "notes").mkdir()
        (d / "notes" / "older.md").write_text("a", encoding="utf-8")
        before = "\n".join(decl.render_digest(doc, d))
        self.assertIn("1 file(s)", before)
        self.assertIn("older.md", before)

        newer = d / "notes" / "newer.md"
        newer.write_text("b", encoding="utf-8")
        os.utime(newer, (time.time() + 10, time.time() + 10))
        after = "\n".join(decl.render_digest(doc, d))
        self.assertIn("2 file(s)", after)
        self.assertIn("newest: notes/newer.md", after,
                      "the newest member must move with the plant — a count "
                      "that grows while the pointer stays put sends a session "
                      "to the wrong document")

    def test_an_UNRESOLVABLE_home_is_could_not_verify_and_never_a_zero(self):
        """THE ASSERTION IS ON WHAT MUST NOT APPEAR.

        `0 file(s)` over a home nothing examined is an absence claim with no
        instrument behind it, and it reads exactly like a true zero. The
        boundary is the retire walk's own: an UNRESOLVABLE home (an unknown
        variable) is the dead instrument, while an in-tree home that is simply
        absent is an observation and stays a number.
        """
        d, doc = self._repo(
            {"nowhere": self._kind("$LC219_NOT_A_REAL_VAR/x/*.md", ["session"])})
        text = "\n".join(decl.render_digest(doc, d))
        self.assertIn("COULD NOT VERIFY", text)
        self.assertNotIn("0 file(s)", text,
                         "a population no instrument examined must not be "
                         "reported as a count of zero")

    def test_the_session_marker_discriminates_rather_than_decorating(self):
        """The control. Without it, a marker on every line says nothing."""
        d, doc = self._repo({
            "read by a verb": self._kind("a.md", ["verb:item ready"]),
            "read by nobody": self._kind("b.md", ["session"]),
        })
        (d / "a.md").write_text("a", encoding="utf-8")
        (d / "b.md").write_text("b", encoding="utf-8")
        lines = decl.render_digest(doc, d)
        by_verb = next(ln for ln in lines if "read by a verb" in ln)
        by_none = next(ln for ln in lines if "read by nobody" in ln)
        self.assertNotIn("[session-read]", by_verb)
        self.assertIn("[session-read]", by_none)

    def test_a_mixed_session_and_verb_reader_has_no_session_marker(self):
        """RED-FIRST: any verb reader means a verb reads the kind for you."""
        d, doc = self._repo({
            "mixed readers": self._kind(
                "mixed.md", ["session", "verb:item ready"]),
        })
        (d / "mixed.md").write_text("mixed", encoding="utf-8")
        line = next(ln for ln in decl.render_digest(doc, d)
                    if "mixed readers" in ln)
        self.assertNotIn("[session-read]", line)

    def test_a_dict_form_verb_reader_has_no_session_marker(self):
        d, doc = self._repo({
            "dict verb reader": self._kind(
                "dict.md", [{"reader": "verb:item ready"}]),
        })
        (d / "dict.md").write_text("dict", encoding="utf-8")
        line = next(ln for ln in decl.render_digest(doc, d)
                    if "dict verb reader" in ln)
        self.assertNotIn("[session-read]", line)


class ReaderWhenStage(unittest.TestCase):
    """lc-224 — the reader stage gains a per-entry WHEN.

    Decision (LEDGER 8a5d760): the WHEN attaches PER READER ENTRY rather than
    as an eighth stage — a per-kind scalar cannot describe a kind whose
    reader list mixes a bare role with a `verb:`/`hook:` reference, and this
    repo's own `laws` kind (`reader: ["session", "verb:audit"]`,
    `GOOD_FULL_DECLARATION`) is exactly such a kind. A `reader` list entry is
    EITHER today's bare string (unchanged) OR an object carrying `reader`
    and `when`.
    """

    @staticmethod
    def _kind(reader):
        return {"home": "x.md", "writer": "session", "reader": reader,
                "staleness": "none, declared why: fixture",
                "exit": {"action": "never", "recording-act": "fixture"},
                "growth": "unbounded-with-reason — a fixture kind",
                "trigger": "none, declared why: fixture"}

    def _findings(self, reader):
        doc = json.loads(json.dumps(refusals.GOOD_FULL_DECLARATION))
        doc["kinds"] = {"widgets": self._kind(reader)}
        res = decl.Result(exits.CLEAN)
        decl.validate(doc, res)
        return [f.row for f in res.findings]

    def _messages(self, reader):
        doc = json.loads(json.dumps(refusals.GOOD_FULL_DECLARATION))
        doc["kinds"] = {"widgets": self._kind(reader)}
        res = decl.Result(exits.CLEAN)
        decl.validate(doc, res)
        return [f.message for f in res.findings]

    # --- shape: a bare string is unchanged, an object is now accepted ------

    def test_a_bare_string_reader_still_validates_exactly_as_before(self):
        self.assertEqual(self._findings(["session"]), [])

    def test_an_object_reader_with_a_predicate_when_validates_clean(self):
        self.assertEqual(
            self._findings([{"reader": "session", "when": "predicate true"}]),
            [])

    def test_an_object_reader_with_a_declared_none_when_validates_clean(self):
        self.assertEqual(
            self._findings([{"reader": "session",
                             "when": "none, declared why: no button exists"}]),
            [])

    # --- malformed shapes ---------------------------------------------------

    def test_object_missing_its_reader_key_is_malformed(self):
        """DISCRIMINATING on message, not just ident: the old shape check
        rejects any non-string entry with its GENERIC message too, so the
        ident alone would pass on the unchanged file for the wrong reason."""
        msgs = self._messages([{"when": "predicate true"}])
        self.assertTrue(any("must carry a non-empty `reader` key" in m
                            for m in msgs), msgs)

    def test_object_whose_reader_is_not_a_string_is_malformed(self):
        msgs = self._messages([{"reader": 7, "when": "predicate true"}])
        self.assertTrue(any("must carry a non-empty `reader` key" in m
                            for m in msgs), msgs)

    def test_when_that_is_not_a_string_is_malformed(self):
        msgs = self._messages([{"reader": "session", "when": 7}])
        self.assertTrue(any("carries a `when` that is not a non-empty "
                            "string" in m for m in msgs), msgs)

    def test_when_outside_the_closed_vocabulary_is_malformed(self):
        msgs = self._messages([{"reader": "session", "when": "verb audit"}])
        self.assertTrue(any("must BEGIN with one of" in m
                            and "when" in m for m in msgs), msgs)

    def test_when_is_illegal_on_a_prefixed_reader(self):
        """The moment is the referenced act firing; a `when` there is a
        second answer to a settled question. DISCRIMINATING on message: the
        old shape check would call this malformed too, for the wrong
        reason (any non-string entry), so the ident alone proves nothing
        pre-implementation."""
        msgs = self._messages(
            [{"reader": "verb:audit", "when": "predicate true"}])
        self.assertTrue(any("only legal on a bare reader" in m
                            for m in msgs), msgs)

    # --- missing reasons ----------------------------------------------------

    def test_none_when_with_no_reason_is_kind_stage_undeclared(self):
        findings = self._findings([{"reader": "session", "when": "none"}])
        self.assertIn("kind_stage_undeclared", findings)

    def test_predicate_when_naming_nothing_is_kind_stage_undeclared(self):
        findings = self._findings(
            [{"reader": "session", "when": "predicate"}])
        self.assertIn("kind_stage_undeclared", findings)

    # --- MUST-NOT-MOVE: existing all-string declarations are untouched -----

    def test_the_repos_own_laws_kind_reader_list_is_still_clean(self):
        """`laws` is this repo's own mixed kind — `["session",
        "verb:audit"]` — and it carries no `when` at all, so it must
        validate byte-identically to before this change: clean."""
        doc = json.loads(json.dumps(refusals.GOOD_FULL_DECLARATION))
        res = decl.Result(exits.CLEAN)
        decl.validate(doc, res)
        self.assertEqual(res.findings, [])


class ReaderWhenPartitionAgreement(unittest.TestCase):
    """ONE invalid-state partition, consumed by BOTH instruments (D-3, P2).

    THE DEFECT THIS GRADES. `_check_reader_when` and `read_moments` each
    parsed a `when` with their own copy of the same three lines, and two
    bodies behind one contract disagree. They did: a `predicate` naming
    nothing, a non-string `when`, a `none` with no why, and — the one that
    bites — a PREFIXED reader carrying a `when`, which the checker refuses
    and which `read_moments` had no guard against, so it EXECUTED. Both
    attack arms reproduced that hole with a marker file.

    HOW AGREEMENT IS OBSERVED, and it is deliberately not by asking the
    shared classifier what it thinks. Reading one instrument's answer off
    the other, or both off the thing they share, is the same-parentage
    error: the expectation would move with the mutant. So each side is read
    from its OWN observable output — the checker by whether it recorded a
    finding for the entry, `read_moments` by whether the state it returns is
    MALFORMED — and the assertion is that those two independent readings
    agree for every input.

    PRESENCE IS ITS OWN ARGUMENT. An ABSENT `when` is the legitimate default
    across every kind in this repo, so it must stay UNDECLARED at both
    sides; a naive extraction folds it into MALFORMED and fires on 26 kinds
    at once, which is the guard-on-legitimate-work shape (law 11).
    """

    @staticmethod
    def _kind(reader):
        return {"home": "x.md", "writer": "session", "reader": reader,
                "staleness": "none, declared why: fixture",
                "exit": {"action": "never", "recording-act": "fixture"},
                "growth": "unbounded-with-reason — a fixture kind",
                "trigger": "none, declared why: fixture"}

    #: The seven, with their provenance so the count is checkable rather
    #: than asserted: r3's three probes, then r2's four disagreement cases.
    MALFORMED_CASES = [
        ("r3: verb mode, which this narrower vocabulary excludes",
         "session", "verb audit"),
        ("r3: a mode naming no command", "session", "predicate"),
        ("r3: pure prose", "session", "whenever the session starts"),
        ("r2: a non-string when", "session", 123),
        ("r2: none with no why", "session", "none"),
        ("r2: a PREFIXED reader carrying a when", "verb:audit",
         "predicate true"),
        ("r2: a mode whose command is separators only", "session",
         "predicate :"),
    ]

    #: The controls. Without them the assertion below passes on a build that
    #: calls EVERYTHING malformed.
    WELL_FORMED_CASES = [
        ("a runnable predicate", "session", "predicate true"),
        ("a declared none", "session", "none, declared why: fixture"),
    ]

    def _checker_flags(self, ref, when):
        """Did the CHECKER record a finding about this entry's `when`?

        Read off `res.findings`, which is the checker's own output, rather
        than off the classifier they now share — the whole point of an
        agreement test is two independent readings.
        """
        body = self._kind([{"reader": ref, "when": when}])
        doc = {"kinds": {"fixture": body}}
        res = decl.Result(code=0)
        decl._validate_kind("fixture", body, res, decl.ref_world(doc))
        return any("when" in f.message for f in res.findings)

    def _moments_flags(self, ref, when):
        """And `read_moments`' own answer for the same input."""
        moments = decl.read_moments(self._kind([{"reader": ref,
                                                 "when": when}]))
        return [m.state for m in moments] == [decl.READ_MOMENT_MALFORMED]

    def test_both_instruments_agree_on_every_malformed_input(self):
        for label, ref, when in self.MALFORMED_CASES:
            with self.subTest(case=label):
                self.assertTrue(self._checker_flags(ref, when),
                                "the checker did not flag it")
                self.assertTrue(self._moments_flags(ref, when),
                                "read_moments did not call it MALFORMED")

    def test_both_instruments_agree_on_every_well_formed_input(self):
        for label, ref, when in self.WELL_FORMED_CASES:
            with self.subTest(case=label):
                self.assertFalse(self._checker_flags(ref, when),
                                 "the checker flagged a valid `when`")
                self.assertFalse(self._moments_flags(ref, when),
                                 "read_moments called a valid `when` "
                                 "MALFORMED")

    def test_an_absent_when_is_malformed_at_neither(self):
        """The legitimate default across all 26 kinds. A partition that

        folded absence into MALFORMED would fire on every one of them.
        `session` is DERIVED rather than UNDECLARED since lc-253 (O6 §4
        Part A) — the point this test makes (not malformed) is unchanged by
        which non-malformed state it lands on; `operator` is the ref shape
        neither tier derives, so it still reaches UNDECLARED unmoved."""
        body = self._kind(["session"])
        res = decl.Result(code=0)
        decl._validate_kind("fixture", body, res, {"kinds": {"fixture": {}}})
        self.assertEqual(res.findings, [])
        self.assertEqual([m.state for m in decl.read_moments(body)],
                         [decl.READ_MOMENT_DERIVED])
        residue = self._kind(["operator"])
        self.assertEqual([m.state for m in decl.read_moments(residue)],
                         [decl.READ_MOMENT_UNDECLARED])

    def test_a_prefixed_reader_with_a_when_is_never_EXECUTED(self):
        """The live repair, and the reason the partition is read BEFORE

        anything runs. Both attack arms drove this case with a `predicate
        touch <marker>` and watched the file appear: `read_moments` had no
        bare-reader guard, so a `when` the checker refuses was still run.
        The marker is the observation — a state assertion alone would pass
        on a build that classified correctly and executed anyway.
        """
        import tempfile
        from pathlib import Path as _P
        with tempfile.TemporaryDirectory(prefix="lc-p2-") as td:
            marker = _P(td) / "executed"
            body = self._kind([{"reader": "verb:audit",
                                "when": f"predicate touch {marker}"}])
            decl.read_moments(body, repo=_P(td))
            self.assertFalse(marker.exists(),
                             "a prefixed reader's `when` was EXECUTED")


class ReadMomentsEvaluation(unittest.TestCase):
    """The evaluation half — no precedent in this repo before lc-224.

    Routes through `lanes.evaluate_trigger` and nothing else, so it cannot
    disagree with `lane list` or `item ready` about what BROKEN means (the
    ONE-evaluator rule, CLAUDE.md "The router, and the ONE trigger
    evaluator"). Three answers, each its own test, per law 1.
    """

    @staticmethod
    def _kind(reader):
        return {"home": "x.md", "writer": "session", "reader": reader,
                "staleness": "none, declared why: fixture",
                "exit": {"action": "never", "recording-act": "fixture"},
                "growth": "unbounded-with-reason — a fixture kind",
                "trigger": "none, declared why: fixture"}

    def test_fire(self):
        moments = decl.read_moments(
            self._kind([{"reader": "session", "when": "predicate true"}]))
        self.assertEqual([m.state for m in moments], ["FIRE"])

    def test_quiet(self):
        moments = decl.read_moments(
            self._kind([{"reader": "session", "when": "predicate false"}]))
        self.assertEqual([m.state for m in moments], ["QUIET"])

    def test_broken_nonzero_exit(self):
        moments = decl.read_moments(
            self._kind([{"reader": "session", "when": "predicate exit 2"}]))
        self.assertEqual([m.state for m in moments], ["BROKEN"])

    def test_broken_cannot_run_at_all(self):
        """A `cwd` that does not exist makes `subprocess.run` raise OSError —
        the arm `evaluate_trigger` reserves for a predicate that could not be
        run at all, distinct from one that ran and exited >=2."""
        moments = decl.read_moments(
            self._kind([{"reader": "session", "when": "predicate true"}]),
            repo=Path("/lc224-does-not-exist-anywhere"))
        self.assertEqual([m.state for m in moments], ["BROKEN"])

    def test_a_none_when_is_reported_but_not_evaluated(self):
        moments = decl.read_moments(self._kind(
            [{"reader": "session",
             "when": "none, declared why: no button exists"}]))
        self.assertEqual([m.state for m in moments], ["NONE"])

    def test_an_absent_when_is_reported_but_not_evaluated(self):
        """An absent moment and a quiet one are different answers — both are
        reported, never omitted; only a `predicate` WHEN is ever run.
        `operator` is the residue ref shape neither tier derives (O6 §4
        Part A, lc-253's CONTROL), so it is the one still reaching
        UNDECLARED here — see DerivedReaderMoments below for `session`/
        `verb:` on the DERIVED side."""
        moments = decl.read_moments(self._kind(["operator"]))
        self.assertEqual([m.state for m in moments], ["UNDECLARED"])

    def test_a_mixed_kind_evaluates_exactly_one_moment(self):
        """lc-224's own motivating shape: a `laws`-style mixed reader list,
        `when` on only the bare entry. Both entries are REPORTED; only the
        one carrying a `predicate` WHEN is actually RUN. `verb:audit`'s
        absent `when` is DERIVED (tier 1, O6 §4 Part A, lc-253) rather than
        UNDECLARED — it is still never EXECUTED, which is this test's actual
        claim (`spy.call_count == 1`, for the `session` entry alone)."""
        body = self._kind(
            [{"reader": "session", "when": "predicate true"}, "verb:audit"])
        with mock.patch.object(lanes_mod, "evaluate_trigger",
                               wraps=lanes_mod.evaluate_trigger) as spy:
            moments = decl.read_moments(body)
        self.assertEqual(spy.call_count, 1)
        self.assertEqual(len(moments), 2)
        states = {m.reader: m.state for m in moments}
        self.assertEqual(states["verb:audit"], "DERIVED")
        self.assertIn(states["session"], ("FIRE", "QUIET", "BROKEN"))


class DerivedReaderMoments(unittest.TestCase):
    """O6 §4 Part A (lc-253): a `verb:` or bare `session` reader with no

    authored `when` gets a computed default instead of folding into
    UNDECLARED — the same neighbour-fold vocab.py's contract exists to end
    (a state the vocabulary could not say renders as its nearest benign
    member), here caught by the evaluator itself. RED-FIRST, live over this
    repo's own declaration before this change: `kind moments` printed 50
    UNDECLARED / 0 DERIVED (desk measurement, 2026-09-20, quoted in the item).
    """

    @staticmethod
    def _kind(reader, home="x.md"):
        return {"home": home, "writer": "session", "reader": reader,
                "staleness": "none, declared why: fixture",
                "exit": {"action": "never", "recording-act": "fixture"},
                "growth": "unbounded-with-reason — a fixture kind",
                "trigger": "none, declared why: fixture"}

    def test_tier_1_a_verb_reader_with_no_when_is_DERIVED(self):
        moments = decl.read_moments(self._kind(["verb:item ready"]))
        self.assertEqual([m.state for m in moments], ["DERIVED"])
        self.assertIn("tier 1", moments[0].detail)
        self.assertIn("'item ready' running", moments[0].detail)

    def test_tier_2_a_session_reader_with_no_when_is_DERIVED(self):
        moments = decl.read_moments(self._kind(["session"], home="ITEMS.md"))
        self.assertEqual([m.state for m in moments], ["DERIVED"])
        self.assertIn("tier 2", moments[0].detail)
        self.assertIn("ITEMS.md", moments[0].detail)
        self.assertIn("being written", moments[0].detail)

    def test_tier_2_with_no_home_reports_undeclared_home_rather_than_crash(self):
        """A kind lacking `home` is itself a declaration defect elsewhere
        (law 2); this evaluator must not crash or invent a path for it."""
        body = {"reader": ["session"]}
        moments = decl.read_moments(body)
        self.assertEqual([m.state for m in moments], ["DERIVED"])
        self.assertIn("undeclared", moments[0].detail)

    def test_CONTROL_a_reader_neither_tier_derives_stays_UNDECLARED(self):
        """§4 Part A's own control: an `operator` bare reader, and every

        prefixed shape besides `verb:` (`lane:`, `hook:`, `producer:`), have
        no stated default and must not move — proving DERIVED narrows
        UNDECLARED to the genuine residue rather than replacing it."""
        for ref in ("operator", "lane:something", "hook:something",
                    "producer:something"):
            with self.subTest(ref=ref):
                moments = decl.read_moments(self._kind([ref]))
                self.assertEqual([m.state for m in moments], ["UNDECLARED"],
                                 f"{ref!r} moved off UNDECLARED")

    def test_an_authored_when_still_OVERRIDES_derivation(self):
        """§4 Part A: 'DERIVED unless a `when` overrides it' — an authored

        `when` on a derivable ref is not shadowed by the new default."""
        moments = decl.read_moments(self._kind(
            [{"reader": "session", "when": "none, declared why: fixture"}]))
        self.assertEqual([m.state for m in moments], ["NONE"])

    def test_DERIVED_is_registered_in_the_closed_vocabulary(self):
        """lc-241's contract: a new read-moment state must be a member of a
        registered vocabulary, not a bare string only this module knows."""
        from lifecycle_core import vocab
        v = vocab.by_name("reader moment states")
        self.assertIsNotNone(v, "no 'reader moment states' registration")
        self.assertIn(decl.READ_MOMENT_DERIVED, v.members)
        self.assertIn(decl.READ_MOMENT_UNDECLARED, v.members)
        self.assertIn(decl.READ_MOMENT_MALFORMED, v.members)
        self.assertIn(decl.READ_MOMENT_NONE, v.members)


class DueReadsForAct(unittest.TestCase):
    """O6 §4 Part B (lc-254): the acting verb's own output names the kinds

    whose DERIVED reader moment fires for that act. RED-FIRST, live over
    this repo's own declaration before this change: `python3 plugin/cli/
    lifecycle item ready --head` printed no due-read line and its fire.jsonl
    line carried no `detail` key at all (measured 2026-09-20 at HEAD 8b7e939,
    quoted in the lane's report to the dispatcher).
    """

    @staticmethod
    def _kind(reader, writer, home="x.md"):
        return {"home": home, "writer": writer, "reader": reader,
                "staleness": "none, declared why: fixture",
                "exit": {"action": "never", "recording-act": "fixture"},
                "growth": "unbounded-with-reason: fixture",
                "trigger": "none, declared why: fixture"}

    def test_tier_1_fires_on_the_exact_verb_and_nothing_else(self):
        doc = {"kinds": {"items": self._kind(["verb:item ready"], "session")}}
        self.assertEqual([d.kind for d in decl.due_reads_for_act(
            doc, "item ready")], ["items"])
        self.assertEqual(decl.due_reads_for_act(doc, "item park"), [],
                          "an unrelated act must not surface a Tier 1 kind")

    def test_tier_2_fires_when_the_act_is_one_of_the_kinds_own_writers(self):
        """The write-target mapping is the kind's OWN `writer` field — this

        repo's real `items` shape (`writer: "verb:item add, verb:item park,
        verb:item close"`, `reader: [..., "session"]`)."""
        doc = {"kinds": {"items": self._kind(
            ["verb:item ready", "session"],
            "verb:item add, verb:item park, verb:item close")}}
        for act in ("item add", "item park", "item close"):
            with self.subTest(act=act):
                due = decl.due_reads_for_act(doc, act)
                self.assertEqual([d.kind for d in due], ["items"])
                self.assertIn("tier 2", due[0].note)
        self.assertEqual(decl.due_reads_for_act(doc, "item ratio"), [],
                          "a writer verb not named in `writer` must not fire")

    def test_an_authored_when_is_never_surfaced_here(self):
        """DERIVED is only ever the ABSENT-`when` default (O6 §4 Part A);

        an authored `when` on a derivable ref shape is a declaration, not a
        derivation, and this act-time surface must not treat it as due."""
        doc = {"kinds": {"items": self._kind(
            [{"reader": "verb:item ready",
              "when": "none, declared why: fixture"}], "session")}}
        self.assertEqual(decl.due_reads_for_act(doc, "item ready"), [])

    def test_CONTROL_a_reader_neither_tier_derives_never_fires(self):
        """§4 Part A's own control, replayed at this surface: `operator` and

        every prefixed shape besides `verb:` have no computable default, so
        no act can ever make them due here."""
        for ref in ("operator", "lane:something", "hook:something",
                    "producer:something"):
            with self.subTest(ref=ref):
                doc = {"kinds": {"items": self._kind([ref], "session")}}
                self.assertEqual(
                    decl.due_reads_for_act(doc, "item ready"), [],
                    f"{ref!r} must never surface")

    def test_never_executes_a_predicate(self):
        """A kind with an authored, EXECUTABLE `when` on an unrelated reader

        sits beside the derivable one — this must never run it (only
        `read_moments` runs predicates), proven by a marker file that a run
        would create and this call must not."""
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            marker = Path(td) / "marker"
            doc = {"kinds": {"items": self._kind(
                [{"reader": "session",
                  "when": f"predicate: touch {marker}"},
                 "verb:item ready"],
                "session")}}
            decl.due_reads_for_act(doc, "item ready")
            self.assertFalse(marker.exists(),
                              "due_reads_for_act executed a `when` predicate")

    def test_multiple_kinds_and_a_kind_matched_by_both_tiers_once_each(self):
        doc = {"kinds": {
            "items": self._kind(["verb:item ready"], "session"),
            "ledger lines": self._kind(["verb:item ready"], "session"),
            "desk state": self._kind(["verb:desk state", "session"],
                                      "verb:desk state"),
        }}
        due = decl.due_reads_for_act(doc, "item ready")
        self.assertEqual(sorted(d.kind for d in due),
                          ["items", "ledger lines"])
        # `desk state`'s reader carries BOTH a Tier 1 ref matching its own
        # verb and a Tier 2 session ref whose writer matches the same verb —
        # at most one DueRead per kind (a kind is due or it is not).
        due2 = decl.due_reads_for_act(doc, "desk state")
        self.assertEqual([d.kind for d in due2], ["desk state"])

    def test_empty_declaration_returns_empty_never_crashes(self):
        self.assertEqual(decl.due_reads_for_act({"kinds": {}}, "item ready"),
                          [])
        self.assertEqual(decl.due_reads_for_act({}, "item ready"), [])

    def test_reproduces_this_repos_own_live_shape(self):
        """`closed arcs` (home `arcs/closed/*.md`, writer `verb:arc close`,

        reader `["session"]`) is this repo's live Tier-2-only shape (no
        `verb:` reader entry at all) — measured against `.claude/
        lifecycle.json` at HEAD, quoted rather than re-typed by hand."""
        doc = decl_module_json_fixture()
        due = decl.due_reads_for_act(doc, "arc close")
        self.assertEqual([d.kind for d in due], ["closed arcs"])
        self.assertIn("arcs/closed", due[0].note)


def decl_module_json_fixture():
    """This repo's own live `.claude/lifecycle.json`, read fresh — the

    fixture `DueReadsForAct.test_reproduces_this_repos_own_live_shape` needs
    the real `closed arcs` kind rather than a hand-typed copy that could
    silently drift from it.
    """
    import json
    repo_root = Path(__file__).resolve().parent.parent
    return json.loads((repo_root / ".claude" / "lifecycle.json")
                       .read_text(encoding="utf-8"))


class StructureReadout(unittest.TestCase):
    """lc-174 — the session-start announcement carries STRUCTURE, not only
    state: the count of registered kinds, the writer split (verb-written /
    writer:session / other), and how many kinds leave a stage undeclared.

    DISCRIMINATION, not presence: every assertion here is on the actual
    NUMBERS from a declaration this test constructs and controls — a test
    only checking that some structure line appeared would pass for a
    readout computing the wrong thing.
    """

    _FULL = {
        "home": "x.md", "writer": "session", "reader": ["session"],
        "staleness": "none, declared why: fixture",
        "exit": {"action": "never", "recording-act": "fixture"},
        "growth": "unbounded-with-reason: fixture",
        "trigger": "none, declared why: fixture",
    }

    @classmethod
    def _kind(cls, writer, stages=None):
        """A kind body carrying `writer` and every stage in `stages`
        (default: all seven) — omitting a name from `stages` is how a test
        plants an undeclared stage on purpose."""
        keep = decl.KIND_STAGES if stages is None else stages
        body = {k: v for k, v in cls._FULL.items() if k in keep}
        body["writer"] = writer
        return body

    def test_the_three_buckets_and_the_denominator(self):
        """A writer naming a verb AND session together — this repo's own
        `ledger lines` shape (`verb:ledger add, session`) — must land in
        the verb bucket: a kind written partly by a verb still carries
        partial self-administration, which is the property the split
        predicts (the booking's own wording)."""
        doc = {"kinds": {
            "a": self._kind("verb:item close"),
            "b": self._kind("verb:item add, session"),
            "c": self._kind("session"),
            "d": self._kind("session"),
            "e": self._kind("producer:plugin-installer"),
        }}
        s = decl.structure_summary(doc)
        # `both` counts the OVERLAP the exclusive buckets cannot show: this
        # fixture's verb+session kind sits in `verb` (deliberately — partial
        # self-administration is the property the split predicts) and is
        # ALSO session-written. The buckets still partition (2+2+1 == 5);
        # `both` is a second reading of the same population, never a fourth
        # bucket, which is why it is excluded from that sum.
        self.assertEqual(s, {"total": 5, "verb": 2, "session": 2,
                             "other": 1, "both": 1, "undeclared": 0})
        self.assertEqual(s["verb"] + s["session"] + s["other"], s["total"])
        self.assertEqual(decl.render_structure(doc), [
            "kinds registered: 5",
            "writer split: 2 of 5 verb-written, 2 of 5 session-only, "
            "1 of 5 other — 1 of the verb-written also name session, so "
            "3 of 5 carry a session writer in all",
            "stage undeclared: 0 of 5",
        ])

    def test_a_writer_naming_neither_verb_nor_session_lands_in_other_and_is_visible(self):
        doc = {"kinds": {"only-one": self._kind("hook:pre-commit")}}
        s = decl.structure_summary(doc)
        self.assertEqual((s["verb"], s["session"], s["other"]), (0, 0, 1))
        self.assertIn("1 of 1 other", "\n".join(decl.render_structure(doc)))

    def test_a_missing_or_malformed_writer_also_lands_in_other(self):
        doc = {"kinds": {
            "no-writer": {k: v for k, v in self._kind("session").items()
                         if k != "writer"},
            "blank-writer": self._kind("   "),
        }}
        s = decl.structure_summary(doc)
        self.assertEqual((s["verb"], s["session"], s["other"]), (0, 0, 2))

    def test_an_undeclared_stage_is_counted_against_the_total(self):
        doc = {"kinds": {
            "clean": self._kind("session"),
            "missing-exit": self._kind(
                "session",
                stages=[s for s in decl.KIND_STAGES if s != "exit"]),
        }}
        s = decl.structure_summary(doc)
        self.assertEqual(s["undeclared"], 1)
        self.assertIn("stage undeclared: 1 of 2",
                      "\n".join(decl.render_structure(doc)))

    def test_a_malformed_kind_body_counts_as_other_and_undeclared(self):
        """Not a dict at all — `_validate_kind`'s own verdict for this shape
        is that every one of the seven stages is undeclared; this function
        agrees rather than crashing on `.get`."""
        doc = {"kinds": {"broken": "not-an-object"}}
        # `both` is 0 here and must be PRESENT rather than absent: a
        # malformed body has no writer to overlap with, which is a counted
        # zero, not a missing key. A summary whose shape changed with its
        # content would make every caller test for the key first.
        self.assertEqual(decl.structure_summary(doc),
                         {"total": 1, "verb": 0, "session": 0, "other": 1,
                          "both": 0, "undeclared": 1})

    def test_empty_declaration_prints_zeros_never_silence(self):
        """MUST-NOT-MOVE: a clean, empty declaration still prints its
        counts with denominators — never a bare silence that reads as
        nothing to report."""
        self.assertEqual(decl.render_structure({"kinds": {}}), [
            "kinds registered: 0",
            # No overlap clause: `both` is 0, so the sentence stays the
            # short form. The clause appears only when it has something to
            # report, which is what keeps a clean readout from carrying a
            # trailing "0 of the verb-written also name session".
            "writer split: 0 of 0 verb-written, 0 of 0 session-only, "
            "0 of 0 other",
            "stage undeclared: 0 of 0",
        ])

    def test_reproduces_this_repos_own_live_declaration(self):
        """Proved against the artifact the item names, not merely reasoned
        about: `ledger lines`' mixed writer is this repo's own instance of
        the verb+session case, and it must classify as verb here exactly
        as the booking's MEASURED-AGAIN figures count it."""
        doc = json.loads((ROOT / ".claude" / "lifecycle.json")
                         .read_text(encoding="utf-8"))
        s = decl.structure_summary(doc)
        self.assertEqual(s["total"], len(doc["kinds"]))
        self.assertEqual(s["verb"] + s["session"] + s["other"], s["total"])
        self.assertEqual(
            decl._writer_bucket(doc["kinds"]["ledger lines"]["writer"]),
            "verb")
        self.assertEqual(
            decl._writer_bucket(doc["kinds"]["journal entries"]["writer"]),
            "session")
        self.assertEqual(
            decl._writer_bucket(
                doc["kinds"]["plugin cache versions"]["writer"]),
            "other")

    # THE CLI-LEVEL ARM, added once the reconciliation it was waiting on
    # landed. The lane that wrote the rest of this class deliberately left
    # this test out while `cmd_kind` carried two competing `--structure`
    # branches — one its own, one a concurrent writer's — on the grounds
    # that a test written against either shape would pin the wrong one.
    # That was right, and the note it left instead is how the collision was
    # found at all. One branch remains; the arm can exist.
    #
    # IT ASSERTS SHAPE, NOT COUNTS. Running against this repo's own live
    # declaration is the point — it is the real fixture, and a hand-built
    # one would not prove the flag is REACHABLE — but the counts move every
    # time a kind is registered, so pinning them here would make an
    # unrelated declaration edit fail this test for the wrong reason.
    def test_kind_list_structure_is_reachable_from_the_CLI(self):
        import io
        from contextlib import redirect_stdout
        from lifecycle_core import cli as cli_mod

        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                code = cli_mod.main(["kind", "list", "--structure"])
        except SystemExit as exc:
            code = exc.code
        said = buf.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("kinds registered:", said)
        self.assertIn("writer split:", said)
        self.assertIn("stage undeclared:", said)
        # lc-172's denominator rule: every count prints against what it was
        # counted over. A bare number cannot distinguish a small numerator
        # from a small population.
        self.assertIn(" of ", said)

    # THE MUTUAL EXCLUSION IS THE DISCRIMINATING ARM, and it is why the
    # branch ORDER in `cmd_kind` stopped mattering: both `--structure` and
    # `--digest` return, so whichever ran first would win silently and a
    # later reader moving a block would change the answer with no test to
    # notice. argparse refusing the pair makes that unreachable rather than
    # merely undocumented.
    def test_structure_and_digest_cannot_be_asked_together(self):
        import io
        from contextlib import redirect_stdout, redirect_stderr
        from lifecycle_core import cli as cli_mod

        out, err = io.StringIO(), io.StringIO()
        try:
            with redirect_stdout(out), redirect_stderr(err):
                code = cli_mod.main(["kind", "list", "--structure",
                                     "--digest"])
        except SystemExit as exc:
            code = exc.code
        self.assertNotEqual(code, 0)
        self.assertIn("not allowed with", out.getvalue() + err.getvalue())


class GrowthVocabularyGainsItsArm(unittest.TestCase):
    """The growth stage accepts the out-of-vocabulary arm (D-3, on contact).

    THE CONTACT THAT REGISTERED IT. The arc INDEX is a SINGLE FIXED FILE: it
    does not accrue, it is never compacted, and it has no exit — so none of
    `bounded-by-exit` / `compacted` / `unbounded-with-reason` can say what is
    true of it. Every one of the three would be a neighbour standing in for a
    state the vocabulary cannot express, which is the exact failure the
    registered-closed-vocabulary contract exists to end.

    SO THE ARM IS USED RATHER THAN THE NEAREST NEIGHBOUR, and that is the
    whole point of having built it: the honest answer is recorded WITH ITS
    REASON and becomes the widening signal, instead of a kind quietly
    claiming a growth control it does not have.
    """

    @staticmethod
    def _kind(growth):
        return {"home": "arcs/INDEX", "writer": "verb:arc open",
                "reader": ["session"],
                "staleness": "none, declared why: counters are current by "
                             "construction",
                "exit": {"action": "never", "recording-act": "none"},
                "growth": growth,
                "trigger": "none, declared why: nothing fires on a counter"}

    def _findings(self, growth):
        body = self._kind(growth)
        doc = {"kinds": {"arc index": body}}
        res = decl.Result(code=0)
        decl._validate_kind("arc index", body, res, decl.ref_world(doc))
        return [f.row for f in res.findings]

    def test_the_arm_is_ACCEPTED_where_no_member_is_true(self):
        rows = self._findings(
            "cannot-express(2026-09-19): a single fixed file that neither "
            "accrues nor is compacted nor has an exit")
        self.assertNotIn("declaration_malformed", rows)

    def test_a_MEMBER_is_still_accepted(self):
        """The control: opening the door to the arm must not close it on the

        vocabulary's own members."""
        self.assertEqual(self._findings("bounded-by-exit"), [])

    def test_a_WORD_THAT_IS_NEITHER_is_still_refused(self):
        """The second control, and the one that decides whether this bought

        anything: an unrecognised word must stay refused. An arm that
        admitted any string would have widened the vocabulary to everything
        rather than given it a way to say it cannot speak."""
        self.assertIn("declaration_malformed", self._findings("smallish"))

    def test_a_MALFORMED_arm_is_refused(self):
        """Undated: it could never be aged, so the widening signal it is

        supposed to be could never reach zero owed."""
        self.assertIn("declaration_malformed",
                      self._findings("cannot-express: no date here"))


class MomentsBannerLineTest(unittest.TestCase):
    """The W1 act-2 banner line (lc-243) — a NAMED-STALE, best-effort carrier.

    Every arm here is an absence or a staleness arm, because those are the
    ones whose failure is silent: a missing record rendered as "clean", a
    week-old verdict rendered in the present tense, an unreadable detail
    rendered as zeros. The happy path breaks loudly and needs one arm only.
    """

    def _line(self, rec):
        orig = decl.firelog.last_run
        decl.firelog.last_run = lambda verb, repo=None: rec
        try:
            return "\n".join(decl.render_moments_line(Path("/nowhere")))
        finally:
            decl.firelog.last_run = orig

    @staticmethod
    def _rec(days_ago=0, **fields):
        from datetime import date, timedelta
        day = (date.today() - timedelta(days=days_ago)).isoformat()
        parts = " ".join(f"{k}={v}" for k, v in fields.items())
        return {"at": f"{day}T12:00:00+00:00", "verb": "kind moments",
                "detail": parts}

    def test_NO_RECORD_is_a_fact_about_the_machine_not_the_repo(self):
        """The carrier is machine-local. Rendering its absence as "clean"
        would turn a missing log into a verdict about the declaration."""
        line = self._line(None)
        self.assertIn("no recorded run on this machine", line)
        self.assertNotIn("clean", line)

    def test_a_clean_run_carries_its_DATE(self):
        line = self._line(self._rec(broken=0, malformed=0,
                                    declared=4, executed=2))
        self.assertIn("LAST RUN", line)
        self.assertIn("clean", line)
        from datetime import date
        self.assertIn(date.today().isoformat(), line)

    def test_a_clean_run_with_entries_and_derived_carries_all_reach_counts(self):
        line = self._line(self._rec(broken=0, malformed=0, entries=50,
                                    declared=0, derived=47, executed=0))
        self.assertIn("; 50 reader entries — 0 declared, 47 derived, 0 "
                      "executed — no predicate ran, so this verdict is "
                      "about the declaration only", line)

    def test_a_clean_run_with_derived_but_no_entries_carries_three_counts(self):
        line = self._line(self._rec(broken=0, malformed=0, declared=0,
                                    derived=47, executed=0))
        self.assertIn("; 0 declared moment(s), 47 derived, 0 executed — "
                      "no predicate ran, so this verdict is about the "
                      "declaration only", line)

    def test_an_old_format_clean_run_keeps_its_exact_reach_wording(self):
        rec = self._rec(broken=0, malformed=0, declared=4, executed=2)
        line = self._line(rec)
        self.assertEqual(
            line, "moments: LAST RUN " + rec["at"].split("T")[0]
            + " clean — 0 broken, 0 malformed; 4 declared moment(s), "
            "2 executed")

    def test_a_run_that_EXECUTED_NOTHING_says_so_beside_its_zeros(self):
        """The assurance-wider-than-predicate arm, carried through the log:
        `0 broken, 0 malformed` is what a dead evaluator also writes."""
        line = self._line(self._rec(broken=0, malformed=0,
                                    declared=50, executed=0))
        self.assertIn("0 executed", line)
        self.assertIn("about the declaration only", line)

    def test_an_OLD_run_is_named_STALE_rather_than_read_as_current(self):
        line = self._line(self._rec(days_ago=30, broken=0, malformed=0,
                                    declared=4, executed=4))
        self.assertIn("STALE", line)
        self.assertIn("30 day(s) old", line)

    def test_a_RECENT_run_reports_its_age_without_the_stale_word(self):
        """The control for the arm above: without it, a renderer that
        stamped STALE on everything would pass that assertion."""
        line = self._line(self._rec(days_ago=1, broken=0, malformed=0,
                                    declared=4, executed=4))
        self.assertIn("1 day(s) old", line)
        self.assertNotIn("STALE", line)

    def test_an_UNPARSEABLE_detail_reports_no_counts_rather_than_zeros(self):
        """A record this build cannot read is its own answer. Rendering it
        as zeros would invent a clean verdict out of a format change."""
        line = self._line({"at": "2026-09-19T12:00:00+00:00",
                           "verb": "kind moments", "detail": "who knows"})
        self.assertIn("could not parse", line)
        self.assertNotIn("0 broken", line)

    def test_findings_are_reported_with_both_counts(self):
        line = self._line(self._rec(broken=2, malformed=1,
                                    declared=9, executed=5))
        self.assertIn("2 broken", line)
        self.assertIn("1 malformed", line)


class SurfacingBannerLineTest(unittest.TestCase):
    """The surfaced-vs-read banner line (lc-264, O6 §7 row 3's observer).

    Driven through a REAL fire log under a scratch `XDG_STATE_HOME`, never a
    stubbed tally: the parser is the part that can drift silently (a compound
    detail, another repo's records, a torn line), and a stub would pass over
    exactly that. One arm runs the CLI itself, the surface the banner reads.
    """

    REPO = "/repo/under/test"

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.old = os.environ.get("XDG_STATE_HOME")
        os.environ["XDG_STATE_HOME"] = str(self.tmp)

    def tearDown(self):
        if self.old is None:
            os.environ.pop("XDG_STATE_HOME", None)
        else:
            os.environ["XDG_STATE_HOME"] = self.old
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _log(self, *recs, raw=()):
        path = decl.firelog.log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            for r in recs:
                fh.write(json.dumps(r) + "\n")
            for line in raw:
                fh.write(line + "\n")

    def _rec(self, detail, repo=None, at="2026-09-21T10:00:00+00:00"):
        return {"at": at, "verb": "item check",
                "repo": repo or self.REPO, "detail": detail}

    def _line(self, repo=None):
        return "\n".join(decl.render_surfacing_line(repo or self.REPO))

    def test_NO_LOG_is_a_fact_about_the_machine(self):
        line = self._line()
        self.assertIn("no readable fire log on this machine", line)
        self.assertNotIn("never read", line)

    def test_a_log_with_no_surfacing_for_THIS_repo_says_so(self):
        """Another repo's surfacing must not count here: the partition is
        the repo field, and a log full of foreign lines is still zero."""
        self._log(self._rec("surfaced=items", repo="/other/repo"))
        line = self._line()
        self.assertIn("no due read has been surfaced for this repo", line)
        self.assertNotIn("since", line)

    def test_the_COMPOUND_detail_is_parsed_whole(self):
        """cli.py APPENDS the surfacing with `; ` after a verb's own detail,
        so a parser keyed to the field's start misses every closing line."""
        self._log(
            self._rec("close lc-9 DONE; surfaced=done bodies,items",
                      at="2026-09-22T10:00:00+00:00"),
            self._rec("surfaced=items", at="2026-09-20T10:00:00+00:00"),
            self._rec("read=items"),
            raw=['{"torn": ', ""])
        tally = decl.firelog.surfacing_tally(self.REPO)
        self.assertEqual(tally["kinds"], {"done bodies": [1, 0],
                                          "items": [2, 1]})
        self.assertEqual((tally["surfacings"], tally["reads"]), (2, 1))
        self.assertEqual(tally["first"], "2026-09-20")
        self.assertEqual(
            self._line(),
            "surfacing: since 2026-09-20 — 2 surfacing(s) over 2 kind(s), "
            "1 read(s) through `kind read`; never read: done bodies "
            "(direct file opens are not counted)")

    def test_a_READ_NOT_surfaced_is_not_listed_as_never_read(self):
        self._log(self._rec("surfaced=items"), self._rec("read=items"),
                  self._rec("read=git config"))
        line = self._line()
        self.assertIn("every surfaced kind read at least once", line)
        self.assertIn("over 1 kind(s)", line)

    def test_the_CLI_banner_carries_the_line_and_keeps_its_exit(self):
        """Through the verb the session-start banner calls, not the function:
        wiring is where a green unit arm and a dark banner part company."""
        cmd = [sys.executable, str(ROOT / "plugin" / "cli" / "lifecycle"),
               "--repo", str(ROOT), "kind", "list", "--structure"]
        # THE EXIT IS COMPARED AGAINST A PAIRED RUN, not against "not a
        # finding": a usage error exits 3 and passes that test, which is how
        # this arm's first draft read green over a command that never ran.
        bare = subprocess.run(cmd, capture_output=True, text=True,
                              env=dict(os.environ))
        self._log(self._rec("surfaced=ledger lines", repo=str(ROOT)))
        run = subprocess.run(cmd, capture_output=True, text=True,
                             env=dict(os.environ))
        self.assertIn("kinds registered:", run.stdout, run.stderr)
        self.assertEqual(run.returncode, bare.returncode, run.stdout)
        lines = run.stdout.splitlines()
        surf = [ln for ln in lines if ln.startswith("surfacing:")]
        self.assertEqual(len(surf), 1, run.stdout + run.stderr)
        self.assertIn("never read: ledger lines", surf[0])
        moments = [i for i, ln in enumerate(lines) if ln.startswith("moments:")]
        self.assertEqual(moments and moments[0] + 1,
                         lines.index(surf[0]), run.stdout)
        self.assertIn("no readable fire log", bare.stdout)


class CommandGroupIsNotAVerb(unittest.TestCase):
    """lc-279: a command GROUP passing as a verb (lc-268 review, defect D1).

    `item` resolves in the parser — as a GROUP, not as an action — and
    before this fix that satisfied both `_verb_exists`'s prefix-inclusive
    walk and `cli_verbs()`'s bare-top-level addition, so `trigger: verb
    item` and a `verb:item` reader both read CLEAN: a WHEN that will never
    fire, indistinguishable from one that is reachable. RED-FIRST against
    the pre-fix `declaration.py`: both plants below read CLEAN there
    (verified directly, not relayed from the review — the old module was
    loaded under a separate package name from `git show HEAD` at the
    commit before this fix landed and read against the identical
    fixtures).
    """

    def test_a_group_shaped_trigger_names_itself_a_group(self):
        d = json.loads(json.dumps(refusals.GOOD_DECLARATION))
        d["kinds"]["items"]["trigger"] = "verb item"
        fired = refusals._decl_run(declaration=d, gitignore="", laws_lines=10)
        self.assertEqual(fired.code, exits.FINDING, fired.output)
        self.assertIn("FINDING [trigger_verb_unknown]", fired.output)
        self.assertIn("command GROUP", fired.output)
        self.assertIn("add", fired.output, "the group's own actions must be "
                      "listed, not just named as a group")

    def test_a_full_verb_path_trigger_stays_clean(self):
        """MUST-NOT-MOVE: the existing full-path trigger the roster's own
        `GOOD_DECLARATION` carries (`verb item add`)."""
        fired = refusals._decl_run(**refusals._GOOD_KW)
        self.assertEqual(fired.code, exits.CLEAN, fired.output)

    def test_a_misspelled_verb_still_reads_UNKNOWN_not_a_group(self):
        """MUST-NOT-MOVE: lc-168's original row, `item clsoe`."""
        fired = refusals._decl_run(
            declaration=refusals._kind_trigger_unknown_verb(),
            gitignore="", laws_lines=10)
        self.assertEqual(fired.code, exits.FINDING, fired.output)
        self.assertIn("FINDING [trigger_verb_unknown]", fired.output)
        self.assertNotIn("command GROUP", fired.output)

    def test_a_group_shaped_verb_reader_names_itself_a_group(self):
        d = json.loads(json.dumps(refusals.GOOD_DECLARATION))
        d["kinds"]["items"]["reader"] = ["verb:item"]
        fired = refusals._decl_run(declaration=d, gitignore="", laws_lines=10)
        self.assertEqual(fired.code, exits.FINDING, fired.output)
        self.assertIn("FINDING [dangling_reference]", fired.output)
        self.assertIn("command GROUP", fired.output)
        self.assertIn("ready", fired.output)

    def test_a_full_path_verb_reader_stays_clean(self):
        """MUST-NOT-MOVE: `GOOD_DECLARATION`'s own `verb:item ready` reader."""
        fired = refusals._decl_run(**refusals._GOOD_KW)
        self.assertEqual(fired.code, exits.CLEAN, fired.output)

    def test_a_dangling_lane_reference_is_unaffected(self):
        """MUST-NOT-MOVE: lc-168's `dangling_reference` row, `lane: nope` —
        the new verb-group branch sits ahead of the pool lookup and must
        never intercept a different reference type."""
        fired = refusals._decl_run(declaration=refusals._kind_lane_nope(),
                                   gitignore="", laws_lines=10)
        self.assertEqual(fired.code, exits.FINDING, fired.output)
        self.assertIn("FINDING [dangling_reference]", fired.output)
        self.assertNotIn("command GROUP", fired.output)

    def test_the_ONE_predicate_agrees_with_itself_at_both_call_sites(self):
        """`_verb_lookup("item")` is what both `_validate_kind` and
        `_check_typed_refs` call — asserted directly, since the whole
        defect was two call sites each deriving their own (wrong) answer."""
        status, actions = decl._verb_lookup("item")
        self.assertEqual(status, "group")
        self.assertIn("add", actions)
        self.assertIn("ready", actions)
        self.assertEqual(actions, tuple(sorted(actions)))

    def test_the_predicate_still_answers_leaf_and_unknown(self):
        self.assertEqual(decl._verb_lookup("item ready")[0], "leaf")
        self.assertEqual(decl._verb_lookup("item nope-nope")[0], "unknown")


class GradesExtraKey(unittest.TestCase):
    """lc-294: the optional `grades_extra` opt-in. Absent is today's
    behaviour; present, it accepts `items.GRADES_DECLARED` and nothing else."""

    def _findings(self, value):
        d = json.loads(json.dumps(refusals.GOOD_FULL_DECLARATION))
        d[decl.GRADES_EXTRA_KEY] = value
        res = decl.Result(code=exits.CLEAN)
        decl.validate(d, res)
        return [f.message for f in res.findings
                if decl.GRADES_EXTRA_KEY in f.message]

    def test_absent_is_no_finding_and_declares_nothing(self):
        d = json.loads(json.dumps(refusals.GOOD_FULL_DECLARATION))
        res = decl.Result(code=exits.CLEAN)
        decl.validate(d, res)
        self.assertEqual([f for f in res.findings
                          if decl.GRADES_EXTRA_KEY in f.message], [])
        self.assertFalse(decl.declares_standby(d))

    def test_STANDBY_is_accepted_and_read(self):
        self.assertEqual(self._findings(["STANDBY"]), [])
        self.assertTrue(decl.declares_standby(refusals.STANDBY_DECLARATION))

    def test_anything_else_is_a_declaration_finding(self):
        self.assertTrue(self._findings(["BACKLOG"]))
        self.assertTrue(self._findings("STANDBY"))
        self.assertTrue(self._findings(["STANDBY", "STANDBY"]))

    def test_a_malformed_value_reads_as_declaring_nothing(self):
        for bad in ("STANDBY", ["BACKLOG"], {"STANDBY": {}}):
            self.assertEqual(decl.grades_extra({decl.GRADES_EXTRA_KEY: bad}),
                             ())
