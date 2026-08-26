"""Wave 2, item A: `lifecycle init` — a fresh repo's declaration and lane
stubs (design §3.11: "a fresh repo reaches a valid declaration and checked
lane files without reading this document").

`ScratchGitRepo` below is deliberately NOT `refusals._Repo`: that fixture
seeds a full declaration and both carrier homes already in place, which is
exactly the state `init` is supposed to CREATE rather than consume. `init`'s
own tests need repos that do not already carry a declaration.
"""

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, exits  # noqa: E402
from lifecycle_core import declaration as decl  # noqa: E402
from lifecycle_core import init as init_mod  # noqa: E402


def _run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(argv)
    return code, buf.getvalue()


class ScratchGitRepo:
    """A git work tree this module's own tests shape by hand."""

    def __init__(self):
        self.dir = Path(tempfile.mkdtemp(prefix="lifecycle-init-"))
        self._git("init", "-q", "-b", "main")
        # No machine hooks reaching into an instrument (refusals.py's own
        # `_Scratch` states the same reason): a global core.hooksPath firing
        # here would be read as this test's own verdict.
        self._git("config", "core.hooksPath", str(self.dir / ".nohooks"))
        # A placeholder so the FIRST `commit_as()` always has something
        # staged — an empty tree's `git commit` fails with nothing to do,
        # which is not a state any of these tests are about.
        self.write("README.md", "scratch\n")
        # Every test in this module treats "op@example.invalid" as the
        # operator running `init` here; `set_operator` may be called again
        # to change it.
        self.set_operator("op@example.invalid")

    def _git(self, *argv):
        return subprocess.run(["git", "-C", str(self.dir), *argv],
                              capture_output=True, text=True)

    def set_operator(self, email, name="operator"):
        """PERSISTS `user.email`/`user.name` in this repo's own config —
        `determine_laws` reads exactly this (`git config user.email`,
        repo-scoped) as ITS notion of "the operator running init". Kept
        separate from `commit_as`'s per-commit `-c` override on purpose:
        the two answer different questions (who runs `init` here, vs. who
        authored a given commit in CLAUDE.md's history)."""
        self._git("config", "user.email", email)
        self._git("config", "user.name", name)

    def write(self, rel, text):
        p = self.dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def commit_as(self, email, name="tester", message="c", trailer=None):
        """One commit whose AUTHOR is `email` — the brief's sanctioned
        construction: `git -c user.email=<other> commit …`, a purpose-built
        fixture rather than a mutated real history."""
        self._git("add", "-A")
        msg = message if not trailer else f"{message}\n\n{trailer}"
        r = subprocess.run(
            ["git", "-C", str(self.dir),
             "-c", f"user.email={email}", "-c", f"user.name={name}",
             "commit", "-qm", msg],
            capture_output=True, text=True)
        assert r.returncode == 0, r.stderr

    def seed_carriers(self, schema=None):
        n = schema if schema is not None else decl.SCHEMA_FLOOR
        self.write("ITEMS.md", f"schema: {n}\nbaseline: 0\nadded: 0\ncompacted: 0\n")
        self.write("ITEMS-DONE.md", f"schema: {n}\n")
        self.write("LEDGER.md", f"schema: {n}\n")

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class DerivedIdPrefix(unittest.TestCase):
    """The rule is specified exactly, not left to judgment (brief, section
    A): first letter of each of the first two hyphen/underscore-split
    words, lowercased; a one-word name yields its own first two letters."""

    def test_the_briefs_own_worked_example(self):
        self.assertEqual(init_mod.derive_id_prefix(Path("/x/claude-code-cache-fix")), "cc")
        self.assertEqual(init_mod.derive_id_prefix(Path("/x/lifecycle")), "li")

    def test_underscore_splits_too(self):
        self.assertEqual(init_mod.derive_id_prefix(Path("/x/foo_bar_baz")), "fb")

    def test_explicit_override_wins(self):
        r = ScratchGitRepo()
        r.commit_as("op@example.invalid")
        self.addCleanup(r.close)
        code, out = _run(["--repo", str(r.dir), "init", "--id-prefix", "zz"])
        self.assertEqual(code, exits.CLEAN, out)
        doc = json.loads((r.dir / ".claude" / "lifecycle.json").read_text())
        self.assertEqual(doc["id-prefix"], "zz")
        self.assertIn("explicit --id-prefix", out)


class RefusalArm(unittest.TestCase):
    """Arm 3: `init` REFUSES by default over an existing declaration and
    names the path; `--force` overwrites."""

    def test_a_second_init_without_force_refuses_and_names_the_path(self):
        r = ScratchGitRepo()
        r.commit_as("op@example.invalid")
        self.addCleanup(r.close)
        code1, out1 = _run(["--repo", str(r.dir), "init"])
        self.assertEqual(code1, exits.CLEAN, out1)

        code2, out2 = _run(["--repo", str(r.dir), "init"])
        self.assertEqual(code2, exits.FINDING, out2)
        self.assertIn(str(r.dir / ".claude" / "lifecycle.json"), out2)
        self.assertIn("Refusing to overwrite", out2)

    def test_force_overwrites(self):
        r = ScratchGitRepo()
        r.commit_as("op@example.invalid")
        self.addCleanup(r.close)
        _run(["--repo", str(r.dir), "init", "--id-prefix", "aa"])
        code, out = _run(["--repo", str(r.dir), "init", "--id-prefix", "bb",
                         "--force"])
        self.assertEqual(code, exits.CLEAN, out)
        doc = json.loads((r.dir / ".claude" / "lifecycle.json").read_text())
        self.assertEqual(doc["id-prefix"], "bb")


class RoundTrip(unittest.TestCase):
    """Arm 4: `init` in a scratch repo -> `kind check` clean on the result.
    "A declaration `init` writes that its own checker rejects is the defect
    this arm exists to catch."
    """

    def test_kind_check_is_clean_once_the_repo_also_carries_carriers(self):
        r = ScratchGitRepo()
        # A CLAUDE.md too: `check_laws_present` needs the FILE `init`'s laws
        # branch names to actually exist in the working tree, or that
        # question alone answers COULD NOT VERIFY regardless of the branch
        # taken — a separate concern from the schema-agreement gap this
        # class's own GAP test documents below.
        r.write("CLAUDE.md", "# laws\n")
        r.commit_as("op@example.invalid")
        r.seed_carriers()
        r.commit_as("op@example.invalid", message="seed carriers")
        self.addCleanup(r.close)
        code, out = _run(["--repo", str(r.dir), "init"])
        self.assertEqual(code, exits.CLEAN, out)
        code2, out2 = _run(["--repo", str(r.dir), "kind", "check"])
        self.assertEqual(code2, exits.CLEAN, out2)

    def test_lifecycle_test_suite_stays_clean(self):
        """The OTHER half of "lifecycle --test clean on the result": the
        plugin's own self-test (independent of any one repo) must not have
        regressed — no new unregistered emit site, no broken row."""
        code, out = _run(["--test"])
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("lifecycle --test: CLEAN", out)

    def test_GAP_a_truly_bare_repo_reads_could_not_verify_not_clean(self):
        """NAMED GAP, not silently bridged: `init`'s own scope (brief,
        section A) is the declaration, the .gitignore lines, and lane
        stubs — it does NOT create ITEMS.md/ITEMS-DONE.md/LEDGER.md. On a
        repo that has neither (never migrated, never hand-seeded),
        `check_schema_agreement` cannot read any of the three carriers'
        `schema:` lines and answers COULD NOT VERIFY for each — a real,
        honest third answer, never a FINDING (init wrote nothing wrong),
        but also not the literal CLEAN the round-trip arm's wording asks
        for. This test records the actual behavior rather than asserting
        the wording; see the closing report for the question this raises
        for the dispatching desk."""
        r = ScratchGitRepo()
        r.commit_as("op@example.invalid")
        self.addCleanup(r.close)
        code, out = _run(["--repo", str(r.dir), "init"])
        self.assertEqual(code, exits.CLEAN, out)
        code2, out2 = _run(["--repo", str(r.dir), "kind", "check"])
        self.assertEqual(code2, exits.COULD_NOT_VERIFY, out2)
        self.assertIn("is not present", out2)
        self.assertNotIn("FINDING", out2)  # confirms it is NOT a rejection


class TwelveKeys(unittest.TestCase):
    """Arm 5: the written declaration's key set EQUALS `REQUIRED_KEYS`,
    derived from the constant rather than a restated list."""

    def test_the_key_set_matches_required_keys_exactly(self):
        r = ScratchGitRepo()
        r.commit_as("op@example.invalid")
        self.addCleanup(r.close)
        _run(["--repo", str(r.dir), "init"])
        doc = json.loads((r.dir / ".claude" / "lifecycle.json").read_text())
        self.assertEqual(set(doc.keys()), set(decl.REQUIRED_KEYS))


class RetiredKeysArm(unittest.TestCase):
    """Arm 6: neither retired key ever appears."""

    def test_neither_retired_key_appears(self):
        r = ScratchGitRepo()
        r.commit_as("op@example.invalid")
        self.addCleanup(r.close)
        _run(["--repo", str(r.dir), "init"])
        doc = json.loads((r.dir / ".claude" / "lifecycle.json").read_text())
        for key in decl.RETIRED_KEYS:
            self.assertNotIn(key, doc)


class LawsBranchArm(unittest.TestCase):
    """Arm 7: the three branches, each pasted with its why — plus the
    Co-Authored-By discriminating arm."""

    def test_operator_only_authorship_picks_CLAUDE_md(self):
        r = ScratchGitRepo()
        r.write("CLAUDE.md", "# laws\n")
        r.commit_as("op@example.invalid")
        self.addCleanup(r.close)
        code, out = _run(["--repo", str(r.dir), "init"])
        self.assertEqual(code, exits.CLEAN, out)
        doc = json.loads((r.dir / ".claude" / "lifecycle.json").read_text())
        self.assertEqual(doc["laws"], "CLAUDE.md")
        self.assertIn("operator-only branch", out)

    def test_a_foreign_author_picks_the_overlay(self):
        r = ScratchGitRepo()
        r.write("CLAUDE.md", "# laws\n")
        r.commit_as("op@example.invalid")
        r.write("CLAUDE.md", "# laws v2\n")
        r.commit_as("someone-else@example.invalid", message="foreign edit")
        self.addCleanup(r.close)
        code, out = _run(["--repo", str(r.dir), "init"])
        self.assertEqual(code, exits.CLEAN, out)
        doc = json.loads((r.dir / ".claude" / "lifecycle.json").read_text())
        self.assertEqual(doc["laws"], "CLAUDE.local.md")
        self.assertIn("foreign branch", out)
        self.assertIn("someone-else@example.invalid", out)

    def test_no_tracked_claude_md_is_could_not_verify_and_takes_the_overlay(self):
        r = ScratchGitRepo()
        r.commit_as("op@example.invalid")  # no CLAUDE.md at all
        self.addCleanup(r.close)
        code, out = _run(["--repo", str(r.dir), "init"])
        self.assertEqual(code, exits.CLEAN, out)
        doc = json.loads((r.dir / ".claude" / "lifecycle.json").read_text())
        self.assertEqual(doc["laws"], "CLAUDE.local.md")
        self.assertIn("COULD NOT VERIFY", out)
        self.assertIn("no tracked CLAUDE.md", out)

    def test_a_co_authored_by_trailer_does_not_flip_the_branch(self):
        """THE DISCRIMINATING ARM. A commit AUTHORED by the operator but
        carrying a trailer crediting someone else must still read as
        operator-only — if trailers leaked into the author set, this
        repo's own branch would flip (the brief's own words)."""
        r = ScratchGitRepo()
        r.write("CLAUDE.md", "# laws\n")
        r.commit_as("op@example.invalid",
                    trailer="Co-Authored-By: Someone Else <someone-else@example.invalid>")
        self.addCleanup(r.close)
        code, out = _run(["--repo", str(r.dir), "init"])
        self.assertEqual(code, exits.CLEAN, out)
        doc = json.loads((r.dir / ".claude" / "lifecycle.json").read_text())
        self.assertEqual(doc["laws"], "CLAUDE.md")
        self.assertIn("operator-only branch", out)
        # And the CONTROL half: the same repo WITHOUT the trailer (a fresh
        # scratch) reaches the identical branch — the trailer changed
        # nothing, which is the point.
        r2 = ScratchGitRepo()
        r2.write("CLAUDE.md", "# laws\n")
        r2.commit_as("op@example.invalid")
        self.addCleanup(r2.close)
        _code2, out2 = _run(["--repo", str(r2.dir), "init"])
        self.assertIn("operator-only branch", out2)


class GitVisibilityArm(unittest.TestCase):
    """Arm 8: the declaration is NOT ignored, and `ITEMS.md.lock` IS
    matched — the pair, since either alone could pass for the wrong
    reason (an absent file reads the same as a visible one to a check
    that only asserts the negative)."""

    def test_the_declaration_is_visible_and_the_lock_pattern_is_ignored(self):
        r = ScratchGitRepo()
        r.commit_as("op@example.invalid")
        self.addCleanup(r.close)
        code, out = _run(["--repo", str(r.dir), "init"])
        self.assertEqual(code, exits.CLEAN, out)

        ignored = decl.ignored_by_git(r.dir, decl.DECLARATION_REL)
        self.assertFalse(ignored, "the declaration must not be git-ignored")

        lock_ignored = decl.ignored_by_git(r.dir, Path("ITEMS.md.lock"))
        self.assertTrue(lock_ignored, "the lock-file pattern must be ignored")

        self.assertIn("declaration visible to git", out)

    def test_a_gitignore_that_already_carries_both_lines_is_left_alone(self):
        """Idempotence: running `init --force` twice must not duplicate the
        lines nor lose them."""
        r = ScratchGitRepo()
        r.commit_as("op@example.invalid")
        self.addCleanup(r.close)
        _run(["--repo", str(r.dir), "init"])
        code, out = _run(["--repo", str(r.dir), "init", "--force"])
        self.assertEqual(code, exits.CLEAN, out)
        gi_text = (r.dir / ".gitignore").read_text(encoding="utf-8")
        self.assertEqual(gi_text.count("!.claude/lifecycle.json"), 1)
        self.assertEqual(gi_text.count("ITEMS.md.lock"), 1)
        self.assertIn("already carried both lines", out)


class NoLanesIsAnEmptyListNeverAbsent(unittest.TestCase):
    """Established fact 3: an EMPTY declared list is a stated fact, never
    an absent key — load-bearing for `init` with no `--lane` given."""

    def test_no_lane_flag_yields_an_empty_declared_list(self):
        r = ScratchGitRepo()
        r.commit_as("op@example.invalid")
        self.addCleanup(r.close)
        code, out = _run(["--repo", str(r.dir), "init"])
        self.assertEqual(code, exits.CLEAN, out)
        doc = json.loads((r.dir / ".claude" / "lifecycle.json").read_text())
        self.assertIn("lanes", doc)
        self.assertEqual(doc["lanes"], [])

    def test_a_named_lane_gets_a_stub_carrying_all_four_parts(self):
        r = ScratchGitRepo()
        r.commit_as("op@example.invalid")
        self.addCleanup(r.close)
        code, out = _run(["--repo", str(r.dir), "init", "--lane", "drain"])
        self.assertEqual(code, exits.CLEAN, out)
        body = (r.dir / "lanes" / "drain.md").read_text(encoding="utf-8")
        self.assertIn("Decides:", body)
        self.assertIn("Trigger:", body)
        self.assertIn("Ends:", body)
        self.assertIn("|---|", body)  # the decision table — the 4th part
        # And the stub's own Trigger: line is a real, evaluable predicate.
        from lifecycle_core import lanes as lanes_mod
        lane = lanes_mod.read_lane(r.dir, "drain")
        self.assertIsNone(lane.problem, lane.problem)
        t = lanes_mod.evaluate_trigger(lane.trigger, cwd=r.dir)
        self.assertEqual(t.state, lanes_mod.QUIET)


if __name__ == "__main__":
    unittest.main()
