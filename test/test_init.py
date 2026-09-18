"""Wave 2, item A: `lifecycle init` — a fresh repo's declaration and lane
stubs (design §3.11: "a fresh repo reaches a valid declaration and checked
lane files without reading this document").

`ScratchGitRepo` below is deliberately NOT `refusals._Repo`: that fixture
seeds a full declaration and both carrier homes already in place, which is
exactly the state `init` is supposed to CREATE rather than consume. `init`'s
own tests need repos that do not already carry a declaration.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import ast
import inspect
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
        # lc-119: this fixture has no tracked CLAUDE.md, so the laws
        # reading is unresolved and the exit code now carries that —
        # legitimately-changed from CLEAN, since --id-prefix does
        # not touch the laws or public readings this arm is not about.
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
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
        # lc-119: no tracked CLAUDE.md here, so the first (successful) init
        # carries an unresolved laws reading in its exit code —
        # legitimately-changed.
        self.assertEqual(code1, exits.COULD_NOT_VERIFY, out1)

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
        # lc-119: no tracked CLAUDE.md — laws unresolved — legitimately
        # changed from CLEAN.
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
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
        # lc-119: this fixture also has no tracked CLAUDE.md, so init's OWN
        # exit code now carries the unresolved laws reading too —
        # legitimately-changed. This does not disturb the gap this test
        # documents (kind check answering COULD NOT VERIFY on the absent
        # carriers below); both readings now agree the repo is unresolved.
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
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
        # lc-119: this arm's own name is the unresolved laws branch — the
        # exit code now carries exactly what the name says.
        # Legitimately-changed from CLEAN.
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
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
        # lc-119: no tracked CLAUDE.md — laws unresolved — legitimately
        # changed from CLEAN. This arm is about git-visibility, not
        # laws, so the unrelated unresolved reading is left as-is rather
        # than masked by adding a CLAUDE.md this arm does not need.
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)

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
        # lc-119: no tracked CLAUDE.md — laws unresolved — legitimately
        # changed from CLEAN.
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
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
        # lc-119: no tracked CLAUDE.md — laws unresolved — legitimately
        # changed from CLEAN.
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        doc = json.loads((r.dir / ".claude" / "lifecycle.json").read_text())
        self.assertIn("lanes", doc)
        self.assertEqual(doc["lanes"], [])

    def test_a_named_lane_gets_a_stub_carrying_all_four_parts(self):
        r = ScratchGitRepo()
        r.commit_as("op@example.invalid")
        self.addCleanup(r.close)
        code, out = _run(["--repo", str(r.dir), "init", "--lane", "drain"])
        # lc-119: no tracked CLAUDE.md — laws unresolved — legitimately
        # changed from CLEAN.
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
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


def _gh_on_path(case, *, stdout="", stderr="", exit_code=0):
    """Put a `gh` on PATH that answers from a script instead of a network.

    END-TO-END on purpose: the arms below drive the real `subprocess.run`
    inside `determine_public` rather than stubbing the function, so the
    exit-code read, the JSON parse and `cmd_init`'s own wiring are all
    exercised. Stubbing the function would leave exactly the plumbing the
    defect lived in untested.
    """
    bin_dir = Path(tempfile.mkdtemp(prefix="lifecycle-fakebin-"))
    case.addCleanup(shutil.rmtree, bin_dir, True)
    script = ["#!/bin/sh"]
    if stderr:
        script.append(f'printf \'%s\\n\' "{stderr}" >&2')
    if stdout:
        script.append("cat <<'LIFECYCLE_JSON'")
        script.append(stdout)
        script.append("LIFECYCLE_JSON")
    script.append(f"exit {exit_code}")
    gh = bin_dir / "gh"
    gh.write_text("\n".join(script) + "\n", encoding="utf-8")
    gh.chmod(0o755)
    old_path = os.environ.get("PATH", "")
    case.addCleanup(os.environ.__setitem__, "PATH", old_path)
    os.environ["PATH"] = f"{bin_dir}{os.pathsep}{old_path}"
    return gh


class PublicFlagArm(unittest.TestCase):
    """lc-81: `public` is DERIVED or declared unresolved — never a silent
    hardcoded default.

    `public` is the one field whose wrong value fails TOWARD EXPOSURE: a
    declared-private repo relaxes the leak scan, and `verbs.check_origin`
    reads the same flag. So these arms are a DISCRIMINATING SET rather
    than one happy path — PUBLIC and PRIVATE must land DIFFERENT values,
    because a check both of them satisfy measures nothing — and every
    unresolved route must still leave a usable declaration behind.
    """

    def _repo_with_a_remote(self):
        r = ScratchGitRepo()
        self.addCleanup(r.close)
        # A tracked CLAUDE.md so the LAWS reading resolves (operator-only)
        # instead of adding its own could-not-verify to every arm below —
        # lc-119 makes an unresolved declared value reach the exit code,
        # and these arms exist to discriminate on the PUBLIC branch alone;
        # an unresolved laws reading would report COULD_NOT_VERIFY for
        # every arm here regardless of what gh answers, which is exactly
        # the non-discriminating confound the corpus's instrument rules
        # warn against.
        r.write("CLAUDE.md", "# laws\n")
        r.commit_as("op@example.invalid")
        # A remote that cannot be reached by anything real: the arms fake
        # `gh`, and a URL at .invalid guarantees that a fake which failed
        # to land cannot silently become a network call instead.
        r._git("remote", "add", "origin", "https://example.invalid/o/n.git")
        return r

    @staticmethod
    def _declaration(r):
        return json.loads((r.dir / ".claude" / "lifecycle.json").read_text())

    def test_a_PUBLIC_gh_visibility_is_derived_into_the_flag(self):
        """THE DEFECT'S OWN ARM: this is the repo the entry describes — gh
        says PUBLIC — and the flag written must be true, with its reason."""
        r = self._repo_with_a_remote()
        _gh_on_path(self, stdout='{"visibility":"PUBLIC"}')
        code, out = _run(["--repo", str(r.dir), "init"])
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIs(self._declaration(r)["public"], True, out)
        self.assertIn("public: True", out)
        self.assertIn("PUBLIC", out)

    def test_a_PRIVATE_gh_visibility_is_derived_into_the_flag(self):
        """THE DISCRIMINATING HALF. Without it, an implementation that
        hardcoded `True` would pass the arm above — the two must DIFFER,
        and the reason printed must name which reading was taken."""
        r = self._repo_with_a_remote()
        _gh_on_path(self, stdout='{"visibility":"PRIVATE"}')
        code, out = _run(["--repo", str(r.dir), "init"])
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIs(self._declaration(r)["public"], False, out)
        self.assertIn("public: False", out)
        self.assertIn("private branch", out)

    def test_no_remote_still_initialises_and_DERIVES_false(self):
        """MUST-NOT-MOVE (2): a repo with no `gh` remote initialises rather
        than failing — and reaches that state WITHOUT consulting `gh` at
        all, which is why no fake is installed here. A repair that made
        `init` depend on gh being installed, authenticated or reachable
        would be a bigger behaviour change than the defect.

        AND THE VALUE HERE IS DERIVED, NOT UNRESOLVED: a repo with no
        remote has no hosted repository that could be public. The arm
        asserts the line does NOT present this as a could-not-verify
        reading, because the unresolved case goes the other way (`true`)
        and conflating the two would hide exactly that split."""
        r = ScratchGitRepo()
        self.addCleanup(r.close)
        # A tracked CLAUDE.md, same reason as `_repo_with_a_remote` above:
        # isolate this arm to the PUBLIC branch alone, so a laws-unresolved
        # reading cannot also darken this "no-remote is DERIVED, not
        # unresolved" assertion.
        r.write("CLAUDE.md", "# laws\n")
        r.commit_as("op@example.invalid")
        code, out = _run(["--repo", str(r.dir), "init"])
        self.assertEqual(code, exits.CLEAN, out)
        doc = self._declaration(r)
        self.assertIsInstance(doc["public"], bool)
        self.assertIs(doc["public"], False, out)
        self.assertEqual(set(doc.keys()), set(decl.REQUIRED_KEYS))
        self.assertIn("public: False — no-remote branch:", out)
        self.assertIn("no git remote", out)
        self.assertIn("checked: git remote", out)
        self.assertNotIn("public: False — COULD NOT VERIFY", out)

    def test_a_gh_that_cannot_answer_is_unresolved_and_fails_LOUD(self):
        """The exit-code route. `init` still succeeds; the reading does
        not, and says which command failed — and the value written is
        `true`, the loud direction (dispatcher ruling): `check_origin`
        then refuses a foreign-cwd item by name instead of silently not
        running."""
        r = self._repo_with_a_remote()
        _gh_on_path(self, stderr="could not resolve to a Repository",
                    exit_code=1)
        code, out = _run(["--repo", str(r.dir), "init"])
        # lc-119: the public branch is unresolved here (gh failed) and the
        # laws branch is resolved (the fixture now carries CLAUDE.md) — so
        # this reading is unresolved for exactly the reason the test name
        # says. Legitimately-changed from CLEAN.
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIs(self._declaration(r)["public"], True, out)
        self.assertIn("public: True — COULD NOT VERIFY", out)
        self.assertIn("gh repo view --json visibility", out)
        self.assertIn("check_origin", out)

    def test_an_unrecognised_visibility_word_is_unresolved_not_a_guess(self):
        """A visibility GitHub has not shipped yet must not silently
        collapse into `false` as "not PUBLIC" — the word is quoted back."""
        r = self._repo_with_a_remote()
        _gh_on_path(self, stdout='{"visibility":"SOMETHING-NEW"}')
        code, out = _run(["--repo", str(r.dir), "init"])
        # lc-119: public unresolved (unrecognised word), laws resolved —
        # legitimately-changed from CLEAN.
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIs(self._declaration(r)["public"], True, out)
        self.assertIn("public: True — COULD NOT VERIFY", out)
        self.assertIn("SOMETHING-NEW", out)

    def test_output_gh_cannot_parse_as_json_is_unresolved(self):
        """The parse route, separate from the exit-code route: a `gh` that
        exits 0 and prints something else is the failure that reads most
        like a success."""
        r = self._repo_with_a_remote()
        _gh_on_path(self, stdout="not json at all")
        code, out = _run(["--repo", str(r.dir), "init"])
        # lc-119: public unresolved (unparseable JSON), laws resolved —
        # legitimately-changed from CLEAN.
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIs(self._declaration(r)["public"], True, out)
        self.assertIn("public: True — COULD NOT VERIFY", out)

    def test_no_remote_and_unresolved_with_a_remote_land_OPPOSITE_values(self):
        """THE ARM THAT PROVES THE SPLIT IS REAL. The two cases the ruling
        separates must reach DIFFERENT values from the same verb — a build
        that collapsed them (either way) satisfies every other arm in this
        class in one direction or the other, and only this pair catches
        it. Both repos are otherwise identical."""
        bare = ScratchGitRepo()
        self.addCleanup(bare.close)
        bare.commit_as("op@example.invalid")
        _code_a, out_a = _run(["--repo", str(bare.dir), "init"])

        hosted = self._repo_with_a_remote()
        _gh_on_path(self, stderr="gh is not authenticated", exit_code=1)
        _code_b, out_b = _run(["--repo", str(hosted.dir), "init"])

        self.assertIs(self._declaration(bare)["public"], False, out_a)
        self.assertIs(self._declaration(hosted)["public"], True, out_b)
        self.assertNotEqual(self._declaration(bare)["public"],
                            self._declaration(hosted)["public"])


class TwoUnresolvedReadingsStillReadOneExitCode(unittest.TestCase):
    """lc-119's aggregation reuses the branch each reading already
    returned (`laws_unresolved` / `public_unresolved`) and folds them
    through `exits.worst`, never a second detection of the same
    condition — the COMMON section's "two paths must not double-report".
    No existing PublicFlagArm/LawsBranchArm fixture exercises BOTH
    readings unresolved at once, so this is new coverage of the
    combination itself, not a re-examination of a prior CLEAN assertion.
    """

    def test_laws_and_public_both_unresolved_is_one_could_not_verify_exit(self):
        r = ScratchGitRepo()
        self.addCleanup(r.close)
        r.commit_as("op@example.invalid")  # no CLAUDE.md: laws unresolved
        r._git("remote", "add", "origin", "https://example.invalid/o/n.git")
        _gh_on_path(self, stderr="gh is not authenticated", exit_code=1)
        code, out = _run(["--repo", str(r.dir), "init"])
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("no tracked CLAUDE.md", out)
        self.assertIn("public: True — COULD NOT VERIFY", out)


class ExistingCouldNotVerifyLinesAreFrozen(unittest.TestCase):
    """MUST-NOT-MOVE (1) for lc-81: the could-not-verify lines `init`
    ALREADY emitted keep their exact text.

    This class NEVER calls `determine_public`. That is deliberate: an arm
    that ran under the mechanism on trial could be skipped or diverted by
    it and the swallowed proof would read as a pass, so the pin is asked
    of an instrument independent of the thing being changed.

    Two instruments, because they fail differently:

    * the BEHAVIOURAL pin drives the one could-not-verify branch reachable
      end-to-end from a scratch git repo, and compares the whole returned
      tuple;
    * the SOURCE pin covers the three branches that cannot be reached
      without breaking git itself. It is a GOLDEN-TEXT pin and is labelled
      as one — its job is to make an edit to those lines loud, not to
      prove the branch executes. The fragments are the exact per-line
      source literals, because adjacent Python string literals are not
      contiguous in the source text.
    """

    #: The joined runtime reason of the one reachable branch.
    _REACHABLE_REASON = ("no tracked CLAUDE.md in this repo (checked: "
                         "git ls-files --error-unmatch CLAUDE.md)")

    #: Source-contiguous fragments of every could-not-verify line that
    #: existed before lc-81 — four `determine_laws` reasons and the two
    #: lines `cmd_init` emits.
    _SOURCE_FRAGMENTS = (
        '"no tracked CLAUDE.md in this repo (checked: git ls-files "',
        '"--error-unmatch CLAUDE.md)"',
        '"git could not read CLAUDE.md\'s author history (checked: "',
        '"git log --format=%ae -- CLAUDE.md; {log.stderr.strip()!r})"',
        '"CLAUDE.md is tracked but carries no commit history "',
        '"(checked: git log --format=%ae -- CLAUDE.md, 0 lines)"',
        '"this repo\'s own operator identity could not be read "',
        '"(checked: git config user.email)"',
        '"laws: {laws_file} (the local overlay) — COULD NOT VERIFY: "',
        '"COULD NOT VERIFY: git could not answer whether the "',
        '"declaration is ignored (checked: git check-ignore --no-index "',
    )

    def test_the_reachable_branch_returns_its_reason_byte_for_byte(self):
        r = ScratchGitRepo()
        self.addCleanup(r.close)
        r.commit_as("op@example.invalid")  # no CLAUDE.md at all
        self.assertEqual(
            init_mod.determine_laws(r.dir),
            ("CLAUDE.local.md", "could-not-verify", self._REACHABLE_REASON))

    def test_every_pre_existing_line_is_still_in_the_source_byte_for_byte(self):
        src = inspect.getsource(init_mod)
        for fragment in self._SOURCE_FRAGMENTS:
            self.assertIn(fragment, src,
                          "a could-not-verify line that predates lc-81 "
                          f"moved: {fragment}")


class GitSubprocessFailuresAreCouldNotVerify(unittest.TestCase):
    """Every git reading is bounded and turns an unavailable git into a
    named unresolved reading rather than an exception escaping `init`."""

    def _without_git_on_path(self):
        empty_bin = Path(tempfile.mkdtemp(prefix="lifecycle-no-git-"))
        self.addCleanup(shutil.rmtree, empty_bin, True)
        old_path = os.environ.get("PATH", "")
        self.addCleanup(os.environ.__setitem__, "PATH", old_path)
        os.environ["PATH"] = str(empty_bin)

    def test_determine_laws_without_git_is_could_not_verify(self):
        self._without_git_on_path()
        try:
            reading = init_mod.determine_laws(Path("/unreadable-repo"))
        except OSError:
            reading = ()
        self.assertIn("could-not-verify", reading,
                      "git missing from PATH did not yield COULD NOT VERIFY")

    def test_determine_public_without_git_is_could_not_verify(self):
        self._without_git_on_path()
        try:
            reading = init_mod.determine_public(Path("/unreadable-repo"))
        except OSError:
            reading = ()
        self.assertIn("could-not-verify", reading,
                      "git missing from PATH did not yield COULD NOT VERIFY")


class AllInitSubprocessRunsAreGuarded(unittest.TestCase):
    """Source-derived coverage: a later subprocess call cannot evade this
    test merely because this test copied an earlier call-site count."""

    @staticmethod
    def _is_subprocess_run(node):
        return (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "run"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "subprocess")

    @staticmethod
    def _handles_subprocess_errors(try_node):
        for handler in try_node.handlers:
            names = []
            types = handler.type.elts if isinstance(handler.type, ast.Tuple) else [handler.type]
            for error in types:
                if isinstance(error, ast.Name):
                    names.append(error.id)
                elif (isinstance(error, ast.Attribute)
                      and isinstance(error.value, ast.Name)):
                    names.append(f"{error.value.id}.{error.attr}")
            if {"OSError", "subprocess.SubprocessError"}.issubset(names):
                return True
        return False

    def test_each_subprocess_run_has_timeout_and_exception_guard(self):
        tree = ast.parse(inspect.getsource(init_mod))
        unguarded = []

        def walk(node, guards=()):
            if self._is_subprocess_run(node):
                has_timeout = any(keyword.arg == "timeout" for keyword in node.keywords)
                has_guard = any(self._handles_subprocess_errors(guard)
                                for guard in guards)
                if not (has_timeout and has_guard):
                    missing = []
                    if not has_timeout:
                        missing.append("timeout")
                    if not has_guard:
                        missing.append("exception guard")
                    unguarded.append(f"line {node.lineno}: missing {', '.join(missing)}")
            for child in ast.iter_child_nodes(node):
                walk(child, guards + (node,) if isinstance(node, ast.Try) else guards)

        walk(tree)
        self.assertEqual([], unguarded,
                         "subprocess.run calls lacking safeguards:\n"
                         + "\n".join(unguarded))


if __name__ == "__main__":
    unittest.main()
