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
        reported, never omitted; only a `predicate` WHEN is ever run."""
        moments = decl.read_moments(self._kind(["session"]))
        self.assertEqual([m.state for m in moments], ["UNDECLARED"])

    def test_a_mixed_kind_evaluates_exactly_one_moment(self):
        """lc-224's own motivating shape: a `laws`-style mixed reader list,
        `when` on only the bare entry. Both entries are REPORTED; only the
        one carrying a `predicate` WHEN is actually RUN."""
        body = self._kind(
            [{"reader": "session", "when": "predicate true"}, "verb:audit"])
        with mock.patch.object(lanes_mod, "evaluate_trigger",
                               wraps=lanes_mod.evaluate_trigger) as spy:
            moments = decl.read_moments(body)
        self.assertEqual(spy.call_count, 1)
        self.assertEqual(len(moments), 2)
        states = {m.reader: m.state for m in moments}
        self.assertEqual(states["verb:audit"], "UNDECLARED")
        self.assertIn(states["session"], ("FIRE", "QUIET", "BROKEN"))
