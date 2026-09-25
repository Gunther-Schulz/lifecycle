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
  * a schema migration REFUSES to guess, and the apply is blocked per repo;
  * `SCHEMA_FLOOR` is single-sourced: `items.py` and `ledger.py` import
    `declaration.py`'s rather than each restating the number, so a bump to
    one can no longer leave the others silently behind.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

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

from lifecycle_core import cli, exits, items, ledger, retire  # noqa: E402
from lifecycle_core import declaration as decl  # noqa: E402
from lifecycle_core.refusals import (  # noqa: E402
    EMPTY_DONE, GOOD_FULL_DECLARATION, SEED_ITEMS)


def build(items_text=SEED_ITEMS, done_text=EMPTY_DONE, declaration=None,
          ledger_text=None) -> Path:
    # DERIVED, never restated (lc-218): a literal here disagrees with
    # SEED_ITEMS/EMPTY_DONE the moment SCHEMA_FLOOR moves, and the repo
    # then fails `schema_mismatch` for a reason the test is not about.
    if ledger_text is None:
        ledger_text = f"schema: {decl.SCHEMA_FLOOR}\n"
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
        head = (f"schema: {decl.SCHEMA_FLOOR}\nbaseline: {n}\n"
                "added: 0\ncompacted: 0\n\n")
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
        self.assertEqual(parsed.head.get("schema"), decl.SCHEMA_FLOOR)
        self.assertEqual(len(parsed.items), 1)

    def test_the_same_block_BELOW_the_schema_line_is_a_shape_break(self):
        """The control. Without it, "comments are allowed" is
        indistinguishable from "the head is not checked at all"."""
        head = f"schema: {decl.SCHEMA_FLOOR}\n"
        text = SEED_ITEMS.replace(head, head + self.PREAMBLE, 1)
        parsed = items.parse(text)
        self.assertTrue(parsed.problems,
                        "a comment below the version must be a shape break — "
                        "everything from the version down is tool-written")
        self.assertTrue(any("comment AFTER" in m for _r, _l, m in parsed.problems),
                        parsed.problems)

    def test_the_ledger_reads_a_preamble_and_still_finds_its_version(self):
        from lifecycle_core import ledger
        parsed = ledger.parse(self.PREAMBLE + f"schema: {decl.SCHEMA_FLOOR}\n"
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
        head = (f"schema: {decl.SCHEMA_FLOOR}\nbaseline: 1\n"
                f"added: {added}\ncompacted: 0\n\n")
        done = EMPTY_DONE + "\n" + "\n".join(
            block(f"xx-{100 + i}", grade="DONE") for i in range(closed_n))
        d = build(items_text=head + block("xx-1"), done_text=done)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return run_cli(d, "item", "ratio")

    def test_a_LARGE_carrier_that_drains_is_clean(self):
        """DRAINS is a property of a HISTORY, not of one snapshot (lc-291).
        This case once read 60:40 at a single commit as draining, and that
        snapshot is the very verdict lc-291 found false: a 1.5:1 carrier may
        be growing without bound. So the carrier here is large at every cut
        and its open count falls over the window."""
        from lifecycle_core import refusals
        f = refusals._ratio_history(
            [("before", 60, 30), ("first-half", 60, 35), ("now", 60, 40)])
        self.assertEqual(f.code, exits.CLEAN, f.output)
        self.assertIn("ratio: CLEAN — the carrier is draining", f.output)

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
        d = build(items_text=SEED_ITEMS.replace(
                      f"schema: {decl.SCHEMA_FLOOR}", "schema: 1"),
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
        """A `--schema-from` at this build's floor over a repo stamped 1 must
        not be resolved by reading the file's own number: one of the two is
        wrong, and that is exactly what must not be silently settled.

        THE NUMBER IS DERIVED, AND THE BUMP IS WHY. This case was written as
        the literal `5` while the floor was 4 — which made it exercise the
        `schema_above_floor` branch (a build cannot migrate DOWN) and not the
        MISMATCH branch its own name and docstring describe. It passed for a
        reason nobody planted, and the 4->5 bump is what exposed it: at floor
        5 the literal stopped being above the floor, fell through to the
        mismatch, and went red. The above-floor branch is not left uncovered —
        `schema_above_floor` is a registered roster row with its own plant and
        control, so this case was duplicating that one by accident while its
        stated subject went untested.

        Derived from `SCHEMA_FLOOR`, `from_n` can never exceed the floor, so
        this exercises the mismatch at every future bump instead of silently
        changing which branch it lands in. COULD NOT VERIFY rather than
        FINDING is the honest answer and the one the branch returns: the tool
        cannot tell which of the two numbers is wrong, and saying so is the
        third answer rather than a verdict it has not earned.
        """
        supplied = {**self.OLD,
                    "leak-scan": {"source-scope-foreign-path": True}}
        d = self._repo(supplied)
        code, out = run_cli(d, "migrate", "--schema-from",
                            str(decl.SCHEMA_FLOOR))
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("the flag is the caller's claim", out, out)


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


class SchemaFloorSingleSourced(unittest.TestCase):
    """`SCHEMA_FLOOR` used to be defined three times, independently, and
    nothing pinned them equal (`declaration.py`, `items.py`, `ledger.py`).
    `items.py` and `ledger.py` now IMPORT `declaration.py`'s rather than
    restating the literal — this is the test that was missing, and it is
    what makes a future bump to one module's floor unable to leave the
    other two silently behind.
    """

    def test_all_three_floors_are_equal(self):
        self.assertEqual(items.SCHEMA_FLOOR, decl.SCHEMA_FLOOR)
        self.assertEqual(ledger.SCHEMA_FLOOR, decl.SCHEMA_FLOOR)


class TheApplyRewritesTheLineTheReaderFound(unittest.TestCase):
    """lc-205: the plan and the write must not be two predicates.

    The dry run resolved a carrier head through `carrier_schema` — skip
    comments, partition on the first colon, compare `head.strip()` — while the
    apply matched `raw.strip().startswith("schema:")` over every line. They
    agree exactly while the head is spelled the writer's way, and law 25 makes
    the dry run the thing that licenses applying across every declared repo,
    so the disagreement is invisible to the check that authorises the act: the
    dry run exercises the reader and never the writer.

    FOUR ARMS, AND THE THIRD IS NOT A VARIANT OF THE FIRST. A head the reader
    accepts and the writer did not match was not merely left alone — the
    writer, having missed it, CARRIED ON SCANNING and rewrote the first BODY
    line beginning `schema:`, leaving the real version line untouched and
    printing `written:` at exit 0. Measured before the fix: line 1 stayed
    `schema : 1` while a body `schema: 9` became `schema: 2`. That is a silent
    content corruption on the apply branch, not a missed write, and a fix that
    only widened the writer's match would have satisfied the first two arms
    and left it whole.

    The fourth arm is the CONTROL and it bounds the repair: both predicates
    strip leading whitespace, so a head indented by accident is a GOOD case
    and must keep migrating. Without it, "reject anything unusual" passes the
    other three.
    """

    HEADS = {
        "internal space": "schema : 1",
        "internal tab": "schema\t: 1",
        "leading space (CONTROL — a good head)": "  schema: 1",
    }

    def _repo(self, head, body_extra=""):
        items_text = SEED_ITEMS.replace(
            f"schema: {decl.SCHEMA_FLOOR}\n", head + "\n", 1)
        if body_extra:
            items_text = items_text + body_extra
        d = build(items_text=items_text, ledger_text="schema: 1\n",
                  done_text=EMPTY_DONE.replace(
                      f"schema: {decl.SCHEMA_FLOOR}", "schema: 1", 1))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        doc = json.loads((d / ".claude" / "lifecycle.json")
                         .read_text(encoding="utf-8"))
        doc["schema"] = 1
        (d / ".claude" / "lifecycle.json").write_text(json.dumps(doc),
                                                      encoding="utf-8")
        return d

    def test_every_head_the_reader_accepts_is_actually_rewritten(self):
        """The written: line must not report a write that did not happen."""
        for name, head in self.HEADS.items():
            with self.subTest(head=name):
                d = self._repo(head)
                before = (d / "ITEMS.md").read_text(encoding="utf-8")
                code, out = run_cli(d, "migrate", "--schema-from", "1",
                                    "--apply")
                after = (d / "ITEMS.md").read_text(encoding="utf-8")
                if "written: ITEMS.md" in out:
                    self.assertNotEqual(
                        before, after,
                        f"{name}: the run printed `written: ITEMS.md` and the "
                        f"carrier came back byte-identical. exit={code}")
                    self.assertEqual(
                        after.split("\n")[0], f"schema: {decl.SCHEMA_FLOOR}",
                        f"{name}: the head is what must carry the new version")
                else:
                    self.assertNotEqual(
                        code, exits.CLEAN,
                        f"{name}: no write was reported, so the run must not "
                        f"report CLEAN")

    def test_a_missed_head_does_not_rewrite_a_body_line(self):
        """THE CORRUPTION ARM. The writer must not go looking past the head.

        A body line beginning `schema:` is the discriminating input: before the
        fix the writer reached it, rewrote it, and reported a clean carrier
        bump. It asserts on what must NOT have changed, which is what catches
        this degrading rather than only breaking.
        """
        d = self._repo("schema : 1", body_extra="schema: 9\n")
        code, out = run_cli(d, "migrate", "--schema-from", "1", "--apply")
        lines = (d / "ITEMS.md").read_text(encoding="utf-8").split("\n")
        self.assertIn("schema: 9", lines,
                      f"a BODY line was rewritten by the schema migration — "
                      f"the head is the only line it may touch. exit={code}\n"
                      f"{out}")

    def test_the_reader_and_the_writer_resolve_through_one_body(self):
        """The structural half, so a future second search is visible.

        `schema_head` returns the POSITION as well as the number, and
        `carrier_schema` is a thin wrapper over it. A caller that rewrites the
        head uses that index; one that searches for itself re-creates the
        defect, and the assertion on the absent search is what would say so.
        """
        for head in ("schema: 1", "schema : 1", "schema\t: 1", "  schema: 1"):
            with self.subTest(head=head):
                i, n, why = decl.schema_head(head + "\n\nbody\n", "c")
                self.assertEqual((i, n, why), (0, 1, None))
        src = (Path(__file__).resolve().parents[1] / "plugin" / "cli"
               / "lifecycle_core" / "migrate.py").read_text(encoding="utf-8")
        self.assertIn("decl.schema_head(", src,
                      "migrate.py must locate the head through the reader's "
                      "own body, not a search of its own")
        # COMMENTS ARE STRIPPED BEFORE THIS SCAN, and the first draft of this
        # assertion is why: it matched the explanatory comment ABOVE the fix
        # describing the old predicate, so it reported the defect present in
        # the file that had just removed it — a substring test over rendered
        # text standing in for a comparison of code.
        code_only = "\n".join(
            ln for ln in src.split("\n") if not ln.strip().startswith("#"))
        self.assertNotIn('startswith("schema:")', code_only,
                         "migrate.py searches for the schema head with its "
                         "own predicate again — that is the lc-205 defect "
                         "restored; it must consume `decl.schema_head`")


if __name__ == "__main__":
    unittest.main()


class GlobHomedCarrierReach(unittest.TestCase):
    """A glob-homed LIVE carrier joins one-schema-per-repo; its RECORD home
    does not (lc-242, arc design N9 / T-a2).

    THE CONTRADICTION THIS RESOLVES. `carrier_homes` dropped every glob home,
    so a kind whose bodies are `arcs/*.md` sat OUTSIDE one-schema-per-repo
    silently — neither checked nor declared exempt, which is the worst of the
    three states because nothing says which it is. Reversing the exclusion
    wholesale is equally wrong in the other direction: it would make every
    CLOSED body schema-stamped and a bump would rewrite the archive, which
    contradicts what a closure record IS.

    SO THE REVERSAL IS FOR THE LIVE HOME ONLY, and the closed home's absence
    from `carrier_homes` IS the exemption — stated in the law text in the
    same act, because an exemption living only in code is a rule nobody can
    read and one living only in prose is a rule nothing enforces.
    """

    ARCS = {
        "home": "arcs/*.md",
        "writer": "verb:arc",
        "reader": ["session"],
        "staleness": "beliefs by kill-condition; premises re-ground at pickup",
        "exit": {"action": "move", "recording-act": "arc close"},
        "growth": "bounded-by-exit",
        "trigger": "verb arc",
    }
    CLOSED = {
        "home": "arcs/closed/*.md",
        "writer": "verb:arc close",
        "reader": ["session"],
        "staleness": "none, declared why: closed bodies are record",
        "exit": {"action": "compact", "recording-act": "arc compact"},
        "growth": "unbounded-with-reason: accrues at arc-closure rate; "
                  "retention is the record role",
        "trigger": "none, declared why: nothing fires on a closed record",
    }

    def _decl(self):
        d = json.loads(json.dumps(GOOD_FULL_DECLARATION))
        d["kinds"]["arcs"] = self.ARCS
        d["kinds"]["closed arcs"] = self.CLOSED
        return d

    def _repo(self, live_schema, closed_schema):
        d = build(declaration=self._decl())
        (d / "arcs").mkdir()
        (d / "arcs" / "closed").mkdir()
        (d / "arcs" / "a1.md").write_text(
            f"schema: {live_schema}\n\n## goal\nx\n", encoding="utf-8")
        (d / "arcs" / "closed" / "a0.md").write_text(
            f"schema: {closed_schema}\n\n## goal\nx\n", encoding="utf-8")
        return d

    def test_the_LIVE_glob_home_is_reached(self):
        """A live arc body stamped below the declaration is a finding."""
        repo = self._repo(decl.SCHEMA_FLOOR - 1, decl.SCHEMA_FLOOR)
        res = decl.Result(code=0)
        doc = json.loads(
            (repo / ".claude" / "lifecycle.json").read_text(encoding="utf-8"))
        decl.check_schema_agreement(repo, doc, res)
        rows = [f.row for f in res.findings]
        self.assertIn("schema_mismatch", rows,
                      f"the live arc home was not reached: {res.findings}")

    def test_the_CLOSED_home_is_EXEMPT_and_that_is_the_pin(self):
        """A closed body at an OLD schema is a record pinned at its closing
        version, never a mismatch. Without this a bump rewrites the archive."""
        repo = self._repo(decl.SCHEMA_FLOOR, decl.SCHEMA_FLOOR - 1)
        res = decl.Result(code=0)
        doc = json.loads(
            (repo / ".claude" / "lifecycle.json").read_text(encoding="utf-8"))
        decl.check_schema_agreement(repo, doc, res)
        self.assertEqual([f.row for f in res.findings], [],
                         f"a closed record was graded against the floor: "
                         f"{res.findings}")

    def test_a_matching_live_body_is_clean(self):
        """The control: the reach must not fire on an agreeing carrier."""
        repo = self._repo(decl.SCHEMA_FLOOR, decl.SCHEMA_FLOOR)
        res = decl.Result(code=0)
        doc = json.loads(
            (repo / ".claude" / "lifecycle.json").read_text(encoding="utf-8"))
        decl.check_schema_agreement(repo, doc, res)
        self.assertEqual([f.row for f in res.findings], [], str(res.findings))

    def test_the_three_existing_carriers_are_unmoved(self):
        """MUST-NOT-MOVE: a repo declaring no arcs answers exactly as before."""
        repo = build()
        doc = json.loads(
            (repo / ".claude" / "lifecycle.json").read_text(encoding="utf-8"))
        homes = decl.carrier_homes(doc)
        self.assertEqual(sorted(homes), ["done bodies", "items",
                                         "ledger lines"])
