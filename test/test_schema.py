"""The schema wave's obligations whose failure is SILENT.

WHAT THE ROSTER ALREADY COVERS is every REFUSAL this wave adds: each has a
plant, a control and a recorded mutation. A roster row proves that a finding
FIRES; it cannot prove the states that produce a CLEAN answer, because a row's
control only has to DIFFER from its plant.

So what is here is the other half — the properties whose breakage produces no
finding at all:

  * the head is DERIVED and has no cap, and `--head` orders by the head rule;
  * `head-rule` accepts BOTH forms and one reader answers for both;
  * a comment block before a carrier's schema line is READ, not merely
    tolerated — and the same block after it is a shape break;
  * a closure CLEARS the wait, and records the decision half only;
  * the flow ratio is a ratio and not a size;
  * a schema migration REFUSES to guess, and the apply is blocked per repo.
"""

import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, exits, items, retire  # noqa: E402
from lifecycle_core import declaration as decl  # noqa: E402
from lifecycle_core.refusals import (  # noqa: E402
    EMPTY_DONE, GOOD_FULL_DECLARATION, SEED_ITEMS)


def build(items_text=SEED_ITEMS, done_text=EMPTY_DONE, declaration=None,
          ledger_text="schema: 2\n") -> Path:
    d = Path(tempfile.mkdtemp(prefix="lifecycle-schema-"))
    run = lambda *a: subprocess.run(a, cwd=str(d), capture_output=True,  # noqa: E731
                                    text=True)
    run("git", "init", "-q", "-b", "main")
    run("git", "config", "core.hooksPath", str(d / ".nohooks"))
    run("git", "config", "user.email", "schema@lifecycle.invalid")
    run("git", "config", "user.name", "schema test")
    (d / ".claude").mkdir()
    (d / ".claude" / "lifecycle.json").write_text(
        json.dumps(declaration or GOOD_FULL_DECLARATION), encoding="utf-8")
    (d / "LAWS.md").write_text("law\n", encoding="utf-8")
    (d / "ITEMS.md").write_text(items_text, encoding="utf-8")
    (d / "ITEMS-DONE.md").write_text(done_text, encoding="utf-8")
    (d / "LEDGER.md").write_text(ledger_text, encoding="utf-8")
    run("git", "add", "-A")
    run("git", "commit", "-qm", "seed")
    return d


def run_cli(repo: Path, *argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(["--repo", str(repo)] + list(argv))
    return code, buf.getvalue()


def block(ident, grade="READY", goal="mitigate", blocked="NONE", extra=""):
    return (f"## {ident}\ngrade: {grade}\n"
            f"requirement: a block — record: LEDGER.md\n"
            f"goal: {goal}\nwrite-set: tools/{ident}.py\n"
            f"done-criterion: it goes red then green\nevidence: none yet\n"
            f"blocked-by: {blocked}\n" + extra)


class DerivedHead(unittest.TestCase):
    """R22: the head is DERIVED and there is NO CAP.

    The cap it replaces bounded a LABEL, and a capped label is escaped by
    relabelling — this repo's own 2026-08-11 incident. So the discriminating
    property is not "the head is short" but "every READY item is listed,
    whatever the count", and the lead goal decides ORDER rather than
    membership.
    """

    def _repo(self, n=12):
        head = f"schema: 2\nbaseline: {n}\nadded: 0\ncompacted: 0\n\n"
        goals = ["mitigate" if i % 3 == 0 else "verify" for i in range(n)]
        body = "\n".join(block(f"xx-{i + 1}", goal=goals[i]) for i in range(n))
        return build(items_text=head + body)

    def test_every_ready_item_is_listed_past_any_old_cap(self):
        d = self._repo(12)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "item", "ready", "--head")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("head: 12 READY", out)
        self.assertIn("NO CAP", out)
        for i in range(1, 13):
            self.assertIn(f"xx-{i} [READY]", out,
                          f"xx-{i} is missing from the head — a head that "
                          "truncates is the cap again in a listing's clothes")

    def test_the_lead_goal_orders_and_does_not_filter(self):
        d = self._repo(12)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        _code, out = run_cli(d, "item", "ready", "--head")
        lead_at = out.index("--- LEAD (mitigate)")
        rest_at = out.index("--- the rest")
        self.assertLess(lead_at, rest_at,
                        "the lead group must precede the rest")
        # And membership is unchanged: the non-lead items are still THERE.
        self.assertIn("--- the rest: 8 item(s)", out)
        self.assertIn("--- LEAD (mitigate): 4 item(s)", out)


class HeadRuleBothForms(unittest.TestCase):
    """The predicate WIDENED to match the message (desk ruling).

    The message always said "an object carrying `lead-goal` … or the string
    \"none\"" while the code accepted only the object — an assurance wider
    than its predicate inside the validator whose job IS predicates. Both
    forms are read in ONE place, so the validator and `--head` cannot
    disagree about what a head rule says.
    """

    def test_the_bare_string_none_is_accepted(self):
        d = build(declaration={**GOOD_FULL_DECLARATION, "head-rule": "none"})
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "kind", "check")
        self.assertEqual(code, exits.CLEAN, out)

    def test_the_object_form_is_still_accepted(self):
        d = build()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "kind", "check")
        self.assertEqual(code, exits.CLEAN, out)

    def test_one_reader_answers_for_both_forms(self):
        self.assertEqual(decl.head_lead_goal("none"), "none")
        self.assertEqual(decl.head_lead_goal({"lead-goal": "none"}), "none")
        self.assertEqual(decl.head_lead_goal({"lead-goal": "mitigate"}),
                         "mitigate")
        # And neither form's failure is silently readable as a goal.
        self.assertIsNone(decl.head_lead_goal("mitigate"))
        self.assertIsNone(decl.head_lead_goal({}))
        self.assertIsNone(decl.head_lead_goal(None))


class CommentBlockBeforeTheSchemaLine(unittest.TestCase):
    """A carrier in a PUBLIC repo can say what it is for (§3.8c).

    Before this, the first non-blank line had to BE the version, so a repo's
    ledger was exactly `schema: 1` until its first decision. The permission is
    one way round and the pair proves it: the same block above the version
    parses, and below it is a shape break.
    """

    PREAMBLE = ("# What this file is for, in a public repo.\n"
                "# One fixed-slot block per item; the tool is the only writer.\n"
                "\n")

    def test_a_comment_block_above_the_schema_line_parses(self):
        parsed = items.parse(self.PREAMBLE + SEED_ITEMS)
        self.assertEqual(parsed.problems, [], parsed.problems)
        self.assertEqual(parsed.head.get("schema"), 2)
        self.assertEqual(len(parsed.items), 1)

    def test_the_same_block_BELOW_the_schema_line_is_a_shape_break(self):
        """The control. Without it, "comments are allowed" is
        indistinguishable from "the head is not checked at all"."""
        text = SEED_ITEMS.replace("schema: 2\n", "schema: 2\n" + self.PREAMBLE,
                                  1)
        parsed = items.parse(text)
        self.assertTrue(parsed.problems,
                        "a comment below the version must be a shape break — "
                        "everything from the version down is tool-written")
        self.assertTrue(any("comment AFTER" in m for _r, _l, m in parsed.problems),
                        parsed.problems)

    def test_the_ledger_reads_a_preamble_and_still_finds_its_version(self):
        from lifecycle_core import ledger
        parsed = ledger.parse(self.PREAMBLE + "schema: 2\n"
                              "dropped: xx-1 — overtaken by the rework\n")
        self.assertEqual(parsed.problems, [], parsed.problems)
        self.assertEqual(len(parsed.lines), 1)
        self.assertEqual(parsed.unreadable, [])


class TheClosureClearsTheWait(unittest.TestCase):
    """A closed item waits for nothing, and only ONE type earns the record.

    Both halves matter and they pull opposite ways. Clearing is what makes "no
    blocker in the done home" a property the tool maintains rather than a hope.
    Annotating only the `decision` type is what keeps the archive free of
    noise: an item-id blocker resolves on its target's DONE and an evidence
    one is re-evaluated each pass, so neither is left hanging by a close.
    """

    def _closed(self, blocked):
        d = build(items_text=SEED_ITEMS.replace("blocked-by: NONE",
                                                f"blocked-by: {blocked}"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "item", "close", "xx-1")
        return code, out, (d / "ITEMS-DONE.md").read_text(encoding="utf-8"), d

    def test_a_decision_blocker_is_cleared_AND_recorded(self):
        _code, _out, done, _d = self._closed("decision which window is canonical")
        self.assertIn("blocked-by: NONE", done)
        self.assertIn("blocker-moot: which window is canonical", done)

    def test_an_evidence_blocker_is_cleared_and_NOT_annotated(self):
        _code, _out, done, _d = self._closed("evidence true")
        self.assertIn("blocked-by: NONE", done)
        self.assertNotIn("blocker-moot", done)

    def test_the_done_home_check_fires_on_a_surviving_blocker(self):
        """The violation arm: a blocker that reached the closure home by some
        path that is not a close."""
        d = build(done_text=EMPTY_DONE + "\n"
                  + block("xx-2", grade="DONE",
                          blocked="decision which window"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[blocked_in_done_home]", out)

    def test_the_same_done_home_without_the_blocker_is_clean(self):
        d = build(items_text=SEED_ITEMS.replace("baseline: 1", "baseline: 2"),
                  done_text=EMPTY_DONE + "\n" + block("xx-2", grade="DONE"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("done-home check: CLEAN", out)


class FlowNotSize(unittest.TestCase):
    """`item ratio` reads a RATIO, and a big carrier draining is fine.

    The discriminating pair is two carriers where the SIZE ordering and the
    HEALTH ordering disagree: a large one draining steadily is clean and a
    small one that never drains is the finding. A size-based alarm gets both
    of these backwards, which is why R22 withdrew caps.
    """

    def _ratio(self, added, closed_n):
        head = f"schema: 2\nbaseline: 1\nadded: {added}\ncompacted: 0\n\n"
        done = EMPTY_DONE + "\n" + "\n".join(
            block(f"xx-{100 + i}", grade="DONE") for i in range(closed_n))
        d = build(items_text=head + block("xx-1"), done_text=done)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return run_cli(d, "item", "ratio")

    def test_a_LARGE_carrier_that_drains_is_clean(self):
        code, out = self._ratio(added=60, closed_n=40)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("ratio: CLEAN", out)

    def test_a_SMALL_carrier_that_never_drains_is_a_finding(self):
        code, out = self._ratio(added=3, closed_n=0)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[capture_dominated]", out)
        self.assertIn("NO drain", out)

    def test_no_flow_on_either_side_is_could_not_verify_not_clean(self):
        code, out = self._ratio(added=0, closed_n=0)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("COULD NOT VERIFY", out)


class SchemaMigrationRefusesToGuess(unittest.TestCase):
    """Law 25, and the half that makes it safe: what it will NOT do.

    A migration that guessed a value the design leaves to the repo would
    write a declaration nobody made, and it would read afterwards exactly
    like a declaration somebody did. So an unguessable key is UNCLASSIFIED
    and BLOCKS the apply — for that repo, and only that repo.
    """

    OLD = {
        "schema": 1, "id-prefix": "xx", "public": False, "laws": "LAWS.md",
        "closure-home": "ITEMS-DONE.md", "trigger-policy": "on-demand",
        "goals": ["mitigate"], "ready-cap": 10,
        "head-rule": {"lead-goal": "mitigate"},
        "lanes": [], "template-bindings": {},
        "kinds": {
            "items": {
                "home": "ITEMS.md", "writer": "verb:item add",
                "reader": ["verb:item ready"],
                "staleness": "change-coupling — the cited record moved",
                "exit": {"action": "move", "recording-act": "the fire log"},
                "bound": "unbounded, declared why: the ready-cap bounds the head",
            },
        },
    }

    def _repo(self, declaration):
        d = build(items_text=SEED_ITEMS.replace("schema: 2", "schema: 1"),
                  done_text="schema: 1\n",
                  ledger_text="schema: 1\n",
                  declaration=declaration)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def test_an_unguessable_key_blocks_the_apply(self):
        d = self._repo(self.OLD)
        code, out = run_cli(d, "migrate", "--schema-from", "1")
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[migration_unclassified]", out)
        self.assertIn("leak-scan", out)
        # And NOTHING was written: the declaration is still at the old schema.
        after = json.loads((d / ".claude" / "lifecycle.json").read_text())
        self.assertEqual(after["schema"], 1)
        self.assertIn("ready-cap", after)

    def test_with_the_decision_supplied_the_dry_run_is_clean_and_writes_nothing(self):
        supplied = {**self.OLD,
                    "leak-scan": {"source-scope-foreign-path": True}}
        d = self._repo(supplied)
        code, out = run_cli(d, "migrate", "--schema-from", "1")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("DRY RUN complete, nothing written", out)
        after = json.loads((d / ".claude" / "lifecycle.json").read_text())
        self.assertEqual(after["schema"], 1,
                         "a DRY RUN that wrote is not a dry run")

    def test_apply_bumps_the_declaration_and_every_carrier_together(self):
        supplied = {**self.OLD,
                    "leak-scan": {"source-scope-foreign-path": True}}
        d = self._repo(supplied)
        code, out = run_cli(d, "migrate", "--schema-from", "1", "--apply")
        self.assertEqual(code, exits.CLEAN, out)
        after = json.loads((d / ".claude" / "lifecycle.json").read_text())
        self.assertEqual(after["schema"], decl.SCHEMA_FLOOR)
        self.assertNotIn("ready-cap", after)
        self.assertNotIn("bound", after["kinds"]["items"])
        self.assertTrue(after["kinds"]["items"]["growth"].startswith(
            "unbounded-with-reason"))
        for name in ("ITEMS.md", "ITEMS-DONE.md", "LEDGER.md"):
            self.assertIn(f"schema: {decl.SCHEMA_FLOOR}",
                          (d / name).read_text(encoding="utf-8"),
                          f"{name} was left at the old schema — one schema "
                          "version per repo means they move together")
        # And the repo now agrees with itself, which is the point.
        code, out = run_cli(d, "kind", "check")
        self.assertNotIn("[schema_mismatch]", out)

    def test_the_flag_is_the_callers_claim_and_a_mismatch_refuses(self):
        """`--schema-from 5` over a repo stamped 1 must not be resolved by
        reading the file's own number: one of the two is wrong, and that is
        exactly what must not be silently settled."""
        supplied = {**self.OLD,
                    "leak-scan": {"source-scope-foreign-path": True}}
        d = self._repo(supplied)
        code, out = run_cli(d, "migrate", "--schema-from", "5")
        self.assertEqual(code, exits.FINDING, out)


class UsageErrorsAreNotFindings(unittest.TestCase):
    """§3.8c: argparse's exit 2 remapped to 3, with a `usage:` prefix.

    A mistyped flag and a real defect in the repo left the process under the
    same code, so a caller reading exit codes — a lane predicate, a gate, a
    hook — could not tell "the tool found something" from "you typed it
    wrong".
    """

    def test_an_unknown_flag_exits_could_not_verify(self):
        with self.assertRaises(SystemExit) as cm:
            with redirect_stdout(io.StringIO()):
                cli.main(["kind", "check", "--no-such-flag"])
        self.assertEqual(cm.exception.code, exits.COULD_NOT_VERIFY)

    def test_a_real_finding_still_exits_two(self):
        """The control: the remap must not swallow the FINDING code."""
        d = build(items_text=SEED_ITEMS.replace("baseline: 1", "baseline: 2"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "item", "check")
        self.assertEqual(code, exits.FINDING, out)


class TheSweepAnchorsOnSegments(unittest.TestCase):
    """`kind sweep`'s home matching, where a substring test would lie.

    `docs/audits` and `docs/audits-old` share a prefix and are different
    homes; `.gitignore` starts with a dot and a `lstrip("./")` ate it, so a
    registered file reported as unregistered — a guard firing on legitimate
    work, measured on this repo's own sweep.
    """

    def test_a_dotfile_home_matches_itself(self):
        self.assertTrue(retire._home_claims(".gitignore", ".gitignore"))

    def test_a_sibling_directory_sharing_a_prefix_is_not_claimed(self):
        self.assertTrue(retire._home_claims("docs/audits", "docs/audits/a.md"))
        self.assertFalse(retire._home_claims("docs/audits",
                                             "docs/audits-old/a.md"))

    def test_a_glob_home_claims_by_pattern(self):
        self.assertTrue(retire._home_claims("docs/audits/*.md",
                                            "docs/audits/a.md"))
        self.assertFalse(retire._home_claims("docs/audits/*.md",
                                             "docs/other/a.md"))


if __name__ == "__main__":
    unittest.main()
