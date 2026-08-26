"""Wave 2, item B: `lifecycle desk state` and its declaration field.

The refusal roster (`refusals.py`'s `DESK_ROWS`) proves the two FINDING
sites — an unknown value, a value missing its own shape — with a plant and a
control each. What is here is the rest: the four CLEAN values actually
recorded, the home path's own property (never `.claude/`), the overwrite
(never append) behaviour, desk-identity resolution (`--desk` over the
environment over a refusal), and the `delegation` declaration field accepted
both absent and present.
"""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, exits  # noqa: E402
from lifecycle_core import declaration as decl  # noqa: E402
from lifecycle_core import desk as desk_mod  # noqa: E402
from lifecycle_core.refusals import (  # noqa: E402
    GOOD_FULL_DECLARATION, _Repo as _RefusalsRepo)


def _run(argv, env=None):
    buf = io.StringIO()
    old = dict(os.environ)
    try:
        if env is not None:
            os.environ.clear()
            os.environ.update(env)
        with redirect_stdout(buf):
            code = cli.main(argv)
    finally:
        os.environ.clear()
        os.environ.update(old)
    return code, buf.getvalue()


class ScratchStateHome:
    """A throwaway `$XDG_STATE_HOME`, isolated from the real machine's —
    the same reason `refusals.py`'s `_desk_cli` isolates it for the roster
    rows: a test run must not leave `desk-state/*.json` debris under the
    operator's real state directory."""

    def __init__(self):
        self.dir = Path(tempfile.mkdtemp(prefix="lifecycle-desk-test-"))

    def path_for(self, desk_id: str) -> Path:
        """The expected file, resolved against THIS scratch root directly —
        never `desk_mod.desk_state_path()`, which reads the process's
        CURRENT `XDG_STATE_HOME`: by the time a test calls it, `_run()` has
        already restored the real environment, so it would resolve against
        the operator's real state dir rather than the scratch one the CLI
        call actually used."""
        return self.dir / "lifecycle" / desk_mod.DESK_STATE_DIRNAME / \
            f"{desk_id}.json"

    def env(self, **extra):
        base = {k: v for k, v in os.environ.items()
                if k not in ("CLAUDE_CODE_SESSION_ID", "XDG_STATE_HOME")}
        base["XDG_STATE_HOME"] = str(self.dir)
        base.update(extra)
        return base

    def cleanup(self):
        import shutil
        shutil.rmtree(self.dir, ignore_errors=True)


class ScratchRepo:
    """A full git work tree carrying a declaration AND both carrier homes —
    `_RefusalsRepo` (`refusals.py`'s own fixture) rather than a hand-rolled
    one, so `check_schema_agreement`'s carrier reads find real files instead
    of answering COULD NOT VERIFY about ones this test never created."""

    def __init__(self, declaration=None):
        self._repo = _RefusalsRepo(declaration=declaration)
        self.dir = self._repo.dir

    def cleanup(self):
        self._repo.close()


class ClosedVocabulary(unittest.TestCase):
    """The four values, each recorded CLEAN; two invalid inputs refused with
    the vocabulary named (the roster's own pair proves this too — this is
    the CLEAN half a roster row cannot prove, since a row's control only has
    to differ from its plant)."""

    def setUp(self):
        self.state = ScratchStateHome()

    def tearDown(self):
        self.state.cleanup()

    def test_reported_is_clean(self):
        code, out = _run(
            ["desk", "state", "REPORTED", "msg-42", "--desk", "d1"],
            env=self.state.env())
        self.assertEqual(code, exits.CLEAN, out)

    def test_waiting_on_is_clean(self):
        code, out = _run(
            ["desk", "state", "WAITING-ON", "lane:pr", "--horizon", "45m",
             "--desk", "d1"],
            env=self.state.env())
        self.assertEqual(code, exits.CLEAN, out)

    def test_blocked_is_clean(self):
        code, out = _run(
            ["desk", "state", "BLOCKED", "awaiting-operator", "--desk", "d1"],
            env=self.state.env())
        self.assertEqual(code, exits.CLEAN, out)

    def test_done_is_clean(self):
        code, out = _run(["desk", "state", "DONE", "--desk", "d1"],
                         env=self.state.env())
        self.assertEqual(code, exits.CLEAN, out)

    def test_an_unknown_value_is_a_finding_naming_the_vocabulary(self):
        code, out = _run(["desk", "state", "BOGUS", "--desk", "d1"],
                         env=self.state.env())
        self.assertEqual(code, exits.FINDING, out)
        for word in desk_mod.DESK_STATE_VALUES:
            self.assertIn(word, out)

    def test_a_second_unknown_value_is_also_a_finding(self):
        """Two distinct invalid inputs, per the brief's own verifier step —
        not the same one run twice."""
        code, out = _run(["desk", "state", "waiting", "--desk", "d1"],
                         env=self.state.env())
        self.assertEqual(code, exits.FINDING, out)

    def test_reported_with_no_argument_is_a_shape_finding(self):
        code, out = _run(["desk", "state", "REPORTED", "--desk", "d1"],
                         env=self.state.env())
        self.assertEqual(code, exits.FINDING, out)

    def test_waiting_on_with_no_horizon_is_a_shape_finding(self):
        code, out = _run(
            ["desk", "state", "WAITING-ON", "lane:pr", "--desk", "d1"],
            env=self.state.env())
        self.assertEqual(code, exits.FINDING, out)


class TheHome(unittest.TestCase):
    """The state file's home is under XDG state, never `.claude/` — a
    NEGATIVE assertion, because that is the property the booking cares
    about and a positive path check would pass on any path."""

    def setUp(self):
        self.state = ScratchStateHome()

    def tearDown(self):
        self.state.cleanup()

    def test_the_file_is_under_xdg_state_never_dot_claude(self):
        code, out = _run(["desk", "state", "DONE", "--desk", "d-home"],
                         env=self.state.env())
        self.assertEqual(code, exits.CLEAN, out)
        path = self.state.path_for("d-home")
        self.assertTrue(path.is_file(), out)
        self.assertTrue(str(path).startswith(str(self.state.dir)), path)
        self.assertNotIn(".claude", path.parts)


class OverwriteNotAppend(unittest.TestCase):
    """Two records in one turn leave ONE record — the verb ALWAYS
    overwrites; there is no history."""

    def setUp(self):
        self.state = ScratchStateHome()

    def tearDown(self):
        self.state.cleanup()

    def test_two_calls_leave_one_record(self):
        env = self.state.env()
        code1, out1 = _run(
            ["desk", "state", "WAITING-ON", "lane:pr", "--horizon", "45m",
             "--desk", "d-over"], env=env)
        self.assertEqual(code1, exits.CLEAN, out1)
        code2, out2 = _run(
            ["desk", "state", "REPORTED", "msg-9", "--desk", "d-over"],
            env=env)
        self.assertEqual(code2, exits.CLEAN, out2)

        path = self.state.path_for("d-over")
        rec = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(rec["value"], "REPORTED")
        self.assertEqual(rec["argument"], "msg-9")
        # ONE file, one JSON object — never a JSONL append.
        self.assertEqual(path.read_text(encoding="utf-8").count("\n{"), 0)


class DeskIdentity(unittest.TestCase):
    """`--desk` explicit always wins; the default is the environment's
    session id; neither present is a refusal, never a derived key."""

    def setUp(self):
        self.state = ScratchStateHome()

    def tearDown(self):
        self.state.cleanup()

    def test_explicit_desk_wins_over_the_environment(self):
        env = self.state.env(CLAUDE_CODE_SESSION_ID="env-session-id")
        code, out = _run(
            ["desk", "state", "DONE", "--desk", "explicit-id"], env=env)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertTrue(self.state.path_for("explicit-id").is_file())
        self.assertFalse(self.state.path_for("env-session-id").is_file())
        self.assertIn("explicit-id", out)
        self.assertIn("--desk", out)

    def test_the_environment_is_the_default(self):
        env = self.state.env(CLAUDE_CODE_SESSION_ID="env-session-id-2")
        code, out = _run(["desk", "state", "DONE"], env=env)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertTrue(self.state.path_for("env-session-id-2").is_file())
        self.assertIn("CLAUDE_CODE_SESSION_ID", out)

    def test_neither_present_is_a_refusal_not_a_derived_key(self):
        """No `--desk`, no `CLAUDE_CODE_SESSION_ID` — REFUSE. NEVER a
        repo-path-plus-user fallback: two desks on the same repo as the same
        user would otherwise collide on one file silently."""
        env = self.state.env()
        env.pop("CLAUDE_CODE_SESSION_ID", None)
        code, out = _run(["desk", "state", "DONE"], env=env)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("CLAUDE_CODE_SESSION_ID", out)
        # Nothing was written anywhere under the scratch state root.
        self.assertFalse((self.state.dir / "lifecycle" / "desk-state").exists())


class DelegationField(unittest.TestCase):
    """The declaration's `delegation` key is OPTIONAL: absent, or one of the
    closed two-value vocabulary, both pass `kind check` CLEAN; anything else
    is a `declaration_malformed` finding."""

    def test_absent_is_clean(self):
        self.assertNotIn("delegation", GOOD_FULL_DECLARATION)
        repo = ScratchRepo()
        try:
            code, out = _run(["--repo", str(repo.dir), "kind", "check"])
            self.assertEqual(code, exits.CLEAN, out)
        finally:
            repo.cleanup()

    def _check(self, declaration):
        repo = ScratchRepo(declaration=declaration)
        try:
            res = decl.read(repo.dir)
            return res
        finally:
            repo.cleanup()

    def test_present_and_valid_is_clean(self):
        for value in decl.DELEGATION_VALUES:
            with self.subTest(value=value):
                d = dict(GOOD_FULL_DECLARATION)
                d["delegation"] = value
                res = self._check(d)
                self.assertEqual(res.code, exits.CLEAN, res.findings)

    def test_present_and_invalid_is_a_finding(self):
        d = dict(GOOD_FULL_DECLARATION)
        d["delegation"] = "sideways"
        res = self._check(d)
        self.assertEqual(res.code, exits.FINDING)
        self.assertTrue(any(f.row == "declaration_malformed"
                            for f in res.findings), res.findings)

    def test_absent_reads_clean_via_decl_read_too(self):
        d = dict(GOOD_FULL_DECLARATION)
        self.assertNotIn("delegation", d)
        res = self._check(d)
        self.assertEqual(res.code, exits.CLEAN, res.findings)
