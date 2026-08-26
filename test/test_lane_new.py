"""Wave 2, item A: `lifecycle lane new` — the lane-authoring verb.

The refusal roster (`refusals.py`'s `lane_new_exists` row, in `LANE_ROWS`)
proves the exists-without-`--force` refusal with its own plant/control pair.
What is here is the rest: the round-trip against the real parser, the
DISCRIMINATING arm that would have caught the struck pipe-grammar defect (a
freshly created lane reads QUIET in `lane list`, never BROKEN), the
byte-identical guarantee that `lane_stub()` is one body shared by `init` and
`lane new` rather than two copies, and the refusal/`--force` pair directly.

CORRECTED BRIEF, 2026-08-26: a lifecycle lane's `Trigger:` line is a shell
command (`lanes.py`'s `evaluate_trigger`; design §3.3) — not the
pipe-delimited `event|intent` grammar `~/.claude/runbook-format.md` governs
for `docs/runbooks/` standing procedures, a different artifact entirely.
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
from lifecycle_core import init as init_mod  # noqa: E402
from lifecycle_core import lanes as lanes_mod  # noqa: E402


def _run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(argv)
    return code, buf.getvalue()


class ScratchGitRepo:
    """A git work tree with a declaration and both carrier homes — enough
    for `kind check`'s one-schema-per-repo agreement to read CLEAN, which
    `lane list`'s per-repo declaration read otherwise degrades to COULD NOT
    VERIFY over (an unrelated finding that would obscure the lane state
    these tests are actually about)."""

    def __init__(self, lanes=None):
        self.dir = Path(tempfile.mkdtemp(prefix="lifecycle-lanenew-"))
        run = lambda *a: subprocess.run(  # noqa: E731
            a, cwd=str(self.dir), capture_output=True, text=True)
        run("git", "init", "-q", "-b", "main")
        run("git", "config", "core.hooksPath", str(self.dir / ".nohooks"))
        run("git", "config", "user.email", "lanenew@lifecycle.invalid")
        run("git", "config", "user.name", "lane new test")
        d = {
            "schema": 2, "id-prefix": "xx", "public": True,
            "laws": "LAWS.md", "closure-home": "ITEMS-DONE.md",
            "trigger-policy": "on-demand", "goals": ["see"],
            "head-rule": "none", "lanes": list(lanes or []),
            "template-bindings": {},
            "leak-scan": {"source-scope-foreign-path": True},
            "kinds": {
                "items": {
                    "home": "ITEMS.md", "writer": "verb:item add",
                    "reader": ["verb:item ready"],
                    "staleness": "none, declared why: test fixture",
                    "exit": {"action": "move", "recording-act": "test"},
                    "growth": "bounded-by-exit — test fixture",
                },
            },
        }
        (self.dir / ".claude").mkdir()
        (self.dir / ".claude" / "lifecycle.json").write_text(
            json.dumps(d), encoding="utf-8")
        (self.dir / "LAWS.md").write_text("law\n", encoding="utf-8")
        (self.dir / "ITEMS.md").write_text(
            "schema: 2\nbaseline: 0\nadded: 0\ncompacted: 0\n",
            encoding="utf-8")
        (self.dir / "ITEMS-DONE.md").write_text("schema: 2\n", encoding="utf-8")
        (self.dir / "LEDGER.md").write_text("schema: 2\n", encoding="utf-8")
        run("git", "add", "-A")
        run("git", "commit", "-qm", "seed")

    def cleanup(self):
        import shutil
        shutil.rmtree(self.dir, ignore_errors=True)


class ScratchRoster:
    """A throwaway `$XDG_CONFIG_HOME/lifecycle/repos` — isolated from the
    real machine's, the same reason `refusals.py`'s `_lane_cli` isolates it."""

    def __init__(self, repo_paths):
        self.cfg = Path(tempfile.mkdtemp(prefix="lifecycle-lanenew-cfg-"))
        (self.cfg / "lifecycle").mkdir()
        (self.cfg / "lifecycle" / "repos").write_text(
            "\n".join(str(p) for p in repo_paths) + "\n", encoding="utf-8")

    def env(self):
        base = {k: v for k, v in os.environ.items()
                if k != "XDG_CONFIG_HOME"}
        base["XDG_CONFIG_HOME"] = str(self.cfg)
        return base

    def cleanup(self):
        import shutil
        shutil.rmtree(self.cfg, ignore_errors=True)


class RoundTrip(unittest.TestCase):
    """`lane new` writes a stub the repo's own reader can read back —
    trigger parsed, all three `LANE_PARTS` present."""

    def setUp(self):
        self.repo = ScratchGitRepo()

    def tearDown(self):
        self.repo.cleanup()

    def test_round_trip_against_read_lane(self):
        code, out = _run(["--repo", str(self.repo.dir), "lane", "new", "pr"])
        self.assertEqual(code, exits.CLEAN, out)
        lane = lanes_mod.read_lane(self.repo.dir, "pr")
        self.assertIsNone(lane.problem, lane.problem)
        self.assertIsNotNone(lane.trigger)
        for part in lanes_mod.LANE_PARTS:
            self.assertIn(part, lane.parts_present)

    def test_own_output_names_it_unregistered_when_undeclared(self):
        code, out = _run(["--repo", str(self.repo.dir), "lane", "new", "pr"])
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("UNREGISTERED", out)

    def test_own_output_names_it_declared_when_it_is(self):
        repo = ScratchGitRepo(lanes=["pr"])
        try:
            code, out = _run(["--repo", str(repo.dir), "lane", "new", "pr"])
            self.assertEqual(code, exits.CLEAN, out)
            self.assertIn("declared", out)
            self.assertNotIn("UNREGISTERED", out)
        finally:
            repo.cleanup()

    def test_lane_list_says_nothing_about_an_undeclared_door(self):
        """CHECKED, not assumed: `lane list` walks the declaration's OWN
        `lanes` list and has no directory scan, so an undeclared door is
        invisible to it — never a finding, never a mention. `lane new`'s
        own output (above) is the only place this is learned from."""
        code, out = _run(["--repo", str(self.repo.dir), "lane", "new", "pr"])
        self.assertEqual(code, exits.CLEAN, out)
        roster = ScratchRoster([self.repo.dir])
        try:
            lcode, lout = _run_env(["lane", "list"], roster.env())
            self.assertNotIn("pr", lout)
        finally:
            roster.cleanup()


def _run_env(argv, env):
    old = dict(os.environ)
    try:
        os.environ.clear()
        os.environ.update(env)
        return _run(argv)
    finally:
        os.environ.clear()
        os.environ.update(old)


class DiscriminatingArm(unittest.TestCase):
    """THE arm that would have caught the struck pipe-grammar defect: a
    freshly created, DECLARED lane reads QUIET in `lane list` — never
    BROKEN. A pipe-delimited line executed as a shell command fails and
    would read BROKEN instead; this is what distinguishes the two designs
    where a round-trip against `read_lane` alone cannot (that check only
    reads the regex-captured text, never executes it)."""

    def test_a_fresh_declared_lane_reads_quiet_not_broken(self):
        repo = ScratchGitRepo(lanes=["pr"])
        try:
            code, out = _run(["--repo", str(repo.dir), "lane", "new", "pr"])
            self.assertEqual(code, exits.CLEAN, out)
            roster = ScratchRoster([repo.dir])
            try:
                lcode, lout = _run_env(["lane", "list"], roster.env())
                self.assertIn("state: QUIET", lout, lout)
                self.assertNotIn("state: BROKEN", lout, lout)
                self.assertNotIn("FINDING [trigger_broken]", lout, lout)
            finally:
                roster.cleanup()
        finally:
            repo.cleanup()


class OneStubBodyNotTwo(unittest.TestCase):
    """`lane_stub()` moved to `lanes.py`; `init --lane` and `lane new` call
    the SAME function — proved by byte-identical output for the same name,
    not merely by both currently reading the same source line."""

    def test_init_and_lane_new_write_byte_identical_stubs(self):
        via_init = ScratchGitRepo()
        try:
            code, out = _run(["--repo", str(via_init.dir), "init",
                              "--force", "--lane", "pr"])
            self.assertEqual(code, exits.CLEAN, out)
            init_body = (via_init.dir / "lanes" / "pr.md").read_text(
                encoding="utf-8")
        finally:
            via_init.cleanup()

        via_new = ScratchGitRepo()
        try:
            code, out = _run(["--repo", str(via_new.dir), "lane", "new", "pr"])
            self.assertEqual(code, exits.CLEAN, out)
            new_body = (via_new.dir / "lanes" / "pr.md").read_text(
                encoding="utf-8")
        finally:
            via_new.cleanup()

        self.assertEqual(init_body, new_body)
        # And directly against the shared function, never re-derived.
        self.assertEqual(new_body, lanes_mod.lane_stub("pr"))


class RefusalAndForce(unittest.TestCase):
    """The roster's own `lane_new_exists` row proves this with a real
    plant/control; this is the same pair read directly, for the CLEAN
    `--force` half a roster row's control does not have to prove twice."""

    def setUp(self):
        self.repo = ScratchGitRepo()

    def tearDown(self):
        self.repo.cleanup()

    def test_refuses_over_an_existing_file(self):
        c1, _ = _run(["--repo", str(self.repo.dir), "lane", "new", "pr"])
        self.assertEqual(c1, exits.CLEAN)
        c2, out2 = _run(["--repo", str(self.repo.dir), "lane", "new", "pr"])
        self.assertEqual(c2, exits.FINDING, out2)
        self.assertIn("FINDING [lane_new_exists]", out2)

    def test_force_overwrites(self):
        c1, _ = _run(["--repo", str(self.repo.dir), "lane", "new", "pr"])
        self.assertEqual(c1, exits.CLEAN)
        path = self.repo.dir / "lanes" / "pr.md"
        path.write_text("garbage — no Trigger line at all\n", encoding="utf-8")
        c2, out2 = _run(["--repo", str(self.repo.dir), "lane", "new", "pr",
                         "--force"])
        self.assertEqual(c2, exits.CLEAN, out2)
        self.assertEqual(path.read_text(encoding="utf-8"),
                         lanes_mod.lane_stub("pr"))
