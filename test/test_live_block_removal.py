"""`item check --staged` refuses a line removed from a block that stays live.

THE GATE ARMS RUN THE BINARY, for `test_item_check_staged`'s reason: the
consumer is a pre-commit hook, so the altitude is the process — argv, the
exit code, the environment the hook inherits. Every refusing arm asserts a
PAIR: the removal IS reported, and the same body with nothing removed is
not.

THE RED WAS TAKEN ON `TheGateFiresOnARemovedLine`, against the build before
the predicate existed: that build exits 0 over a staged hand deletion, and
the arm expects 2. An exit code, never a missing symbol (law 4).
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLI = REPO / "plugin" / "cli" / "lifecycle"

sys.path.insert(0, str(REPO / "plugin" / "cli"))

from lifecycle_core import cli, exits, items, refusals  # noqa: E402
from lifecycle_core import declaration as decl  # noqa: E402
from test_item_check_staged import (  # noqa: E402
    DECLARATION, Fixture, finding_lines)
from test_moves import build, run_cli  # noqa: E402
from test_repair import WRAPPED_AND_MISPLACED  # noqa: E402

ROW = "live_block_line_removed"

HEAD_CARRIER = """schema: 2
baseline: 0
added: 2
compacted: 0

## tt-1
grade: READY
requirement: the first thing — record: LEDGER.md:1
goal: g
write-set: foo.py
done-criterion: d
evidence: MEASURED 2026-09-01 ran it
blocked-by: NONE
amend-reason: 2026-09-02 the write set grew
amended-write-set: 2026-09-02 foo.py, bar.py

## tt-2
grade: PARKED
requirement: the second thing — record: LEDGER.md:2
goal: g
write-set: baz.py
done-criterion: d
evidence: MEASURED 2026-09-01 ran it
blocked-by: decision which shape
not-derivable: 2026-09-03 constitutively the operator's preference
"""

#: tt-1's two amendment lines deleted by hand — the measured defect's shape.
TRIMMED = HEAD_CARRIER.replace(
    "amend-reason: 2026-09-02 the write set grew\n"
    "amended-write-set: 2026-09-02 foo.py, bar.py\n", "")

#: The control: tt-1 GAINS a line and loses none.
APPENDED = HEAD_CARRIER.replace(
    "amended-write-set: 2026-09-02 foo.py, bar.py\n",
    "amended-write-set: 2026-09-02 foo.py, bar.py\n"
    "amend-reason: 2026-09-04 and again\n"
    "amended-write-set: 2026-09-04 foo.py, bar.py, qux.py\n")


def check_staged(fx, env=None):
    full = dict(os.environ)
    full.pop("LIFECYCLE_WRITER_VERB", None)
    full.update(env or {})
    p = subprocess.run(
        [sys.executable, str(CLI), "--repo", str(fx.path),
         "item", "check", "--staged"],
        capture_output=True, text=True, timeout=60, env=full)
    return p.returncode, p.stdout


def removal_lines(stdout):
    return [ln for ln in finding_lines(stdout) if f"[{ROW}]" in ln]


class TheGateFiresOnARemovedLine(unittest.TestCase):

    def test_a_hand_deletion_is_a_finding_naming_the_item(self):
        with tempfile.TemporaryDirectory(prefix="lbr-") as td:
            fx = Fixture(td, carrier=HEAD_CARRIER)
            fx.stage("ITEMS.md", TRIMMED)
            code, out = check_staged(fx)
            self.assertEqual(code, exits.FINDING, out)
            lines = removal_lines(out)
            self.assertEqual(len(lines), 1, out)
            self.assertIn("'tt-1'", lines[0])
            self.assertNotIn("'tt-2'", lines[0])

    def test_an_append_is_clean(self):
        """THE PAIR's other half: same block, edited, nothing removed."""
        with tempfile.TemporaryDirectory(prefix="lbr-") as td:
            fx = Fixture(td, carrier=HEAD_CARRIER)
            fx.stage("ITEMS.md", APPENDED)
            code, out = check_staged(fx)
            self.assertEqual(code, exits.CLEAN, out)
            self.assertEqual(removal_lines(out), [], out)


class WhatTheFindingSays(unittest.TestCase):

    def _out(self, staged):
        with tempfile.TemporaryDirectory(prefix="lbr-") as td:
            fx = Fixture(td, carrier=HEAD_CARRIER)
            fx.stage("ITEMS.md", staged)
            return check_staged(fx)

    def test_it_lists_each_removed_line_with_its_slot_prefix(self):
        _code, out = self._out(TRIMMED)
        self.assertIn("    - `amend-reason` amend-reason: 2026-09-02 the "
                      "write set grew", out)
        self.assertIn("    - `amended-write-set` amended-write-set: "
                      "2026-09-02 foo.py, bar.py", out)

    def test_a_long_line_is_clipped_at_eighty_characters(self):
        long_line = "amend-reason: 2026-09-02 " + "x" * 200
        head = HEAD_CARRIER.replace(
            "amend-reason: 2026-09-02 the write set grew", long_line)
        with tempfile.TemporaryDirectory(prefix="lbr-") as td:
            fx = Fixture(td, carrier=head)
            fx.stage("ITEMS.md", head.replace(long_line + "\n", ""))
            _code, out = check_staged(fx)
        self.assertIn(f"    - `amend-reason` {long_line[:80]}…", out)
        self.assertNotIn(long_line[:81], out)

    def test_it_names_the_three_routes(self):
        _code, out = self._out(TRIMMED)
        self.assertIn("`item amend tt-1 --<slot> <new value> --reason "
                      "<why>`", out)
        self.assertIn('{"carrier": "ITEMS.md", "date": "<today, ISO>", '
                      '"reason": "<why>"} under `carrier-rewrites`', out)
        self.assertIn("NEVER `--no-verify`", out)

    def test_one_finding_per_item_when_two_blocks_lose_lines(self):
        both = TRIMMED.replace(
            "requirement: the second thing — record: LEDGER.md:2\n",
            "requirement: the second thing, reworded — record: LEDGER.md:2\n")
        code, out = self._out(both)
        self.assertEqual(code, exits.FINDING, out)
        lines = removal_lines(out)
        self.assertEqual(len(lines), 2, out)
        self.assertIn("'tt-1'", lines[0])
        self.assertIn("'tt-2'", lines[1])
        self.assertIn("2 finding(s) this staged edit introduced", out)

    def test_an_in_place_edit_is_a_removal_plus_an_addition(self):
        edited = HEAD_CARRIER.replace("write-set: baz.py", "write-set: zap.py")
        code, out = self._out(edited)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("    - `write-set` write-set: baz.py", out)

    def test_a_line_that_only_MOVED_inside_its_block_is_nothing(self):
        moved = HEAD_CARRIER.replace(
            "amend-reason: 2026-09-02 the write set grew\n"
            "amended-write-set: 2026-09-02 foo.py, bar.py\n",
            "amended-write-set: 2026-09-02 foo.py, bar.py\n"
            "amend-reason: 2026-09-02 the write set grew\n")
        _code, out = self._out(moved)
        self.assertEqual(removal_lines(out), [], out)

    def test_a_block_that_LEFT_the_live_home_is_not_this_checks_subject(self):
        gone = HEAD_CARRIER[:HEAD_CARRIER.index("## tt-2")]
        _code, out = self._out(gone)
        self.assertEqual(removal_lines(out), [], out)


class TheLineLevelExemptionsAreCounted(unittest.TestCase):

    def _out(self, staged):
        with tempfile.TemporaryDirectory(prefix="lbr-") as td:
            fx = Fixture(td, carrier=HEAD_CARRIER)
            fx.stage("ITEMS.md", staged)
            return check_staged(fx)

    def test_grade_and_blocked_by_are_rewritten_in_place(self):
        staged = HEAD_CARRIER.replace("grade: READY", "grade: PARKED").replace(
            "blocked-by: NONE", "blocked-by: tt-2")
        code, out = self._out(staged)
        self.assertEqual(removal_lines(out), [], out)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("2 `grade:`/`blocked-by:` line(s) the tool rewrites "
                      "in place", out)

    def test_a_conditional_slot_beside_a_RETYPED_blocker_is_exempt(self):
        staged = HEAD_CARRIER.replace(
            "blocked-by: decision which shape\n"
            "not-derivable: 2026-09-03 constitutively the operator's "
            "preference\n", "blocked-by: tt-1\n")
        code, out = self._out(staged)
        self.assertEqual(removal_lines(out), [], out)
        self.assertIn("1 conditional slot line(s) cleared beside a blocker "
                      "whose TYPE changed", out)

    def test_the_same_slot_removed_with_the_TYPE_UNCHANGED_fires(self):
        """THE PAIR for exemption 2: the conditional slot goes, the blocker
        is re-worded and still a `decision`."""
        staged = HEAD_CARRIER.replace(
            "blocked-by: decision which shape\n"
            "not-derivable: 2026-09-03 constitutively the operator's "
            "preference\n", "blocked-by: decision which other shape\n")
        code, out = self._out(staged)
        self.assertEqual(code, exits.FINDING, out)
        lines = removal_lines(out)
        self.assertEqual(len(lines), 1, out)
        self.assertIn("'tt-2'", lines[0])
        self.assertIn("    - `not-derivable` not-derivable:", out)

    def test_the_type_is_the_EFFECTIVE_one_amendments_included(self):
        """Re-typed by an appended `amended-blocked-by:` — the slot line
        never moved, and the parser's resolution is what the gate reads."""
        staged = HEAD_CARRIER.replace(
            "not-derivable: 2026-09-03 constitutively the operator's "
            "preference\n",
            "amend-reason: 2026-09-05 the wait is on tt-1 now\n"
            "amended-blocked-by: 2026-09-05 tt-1\n")
        _code, out = self._out(staged)
        self.assertEqual(removal_lines(out), [], out)
        self.assertIn("1 conditional slot line(s) cleared", out)

    def test_no_exemption_line_when_none_applied(self):
        _code, out = self._out(APPENDED)
        self.assertNotIn("EXEMPT", out)


class TheToolsOwnCommit(unittest.TestCase):
    """Exemption 3: the variable `commit_paths` sets, honoured for the verbs
    that legitimately remove lines and for no other."""

    def _out(self, verb):
        with tempfile.TemporaryDirectory(prefix="lbr-") as td:
            fx = Fixture(td, carrier=HEAD_CARRIER)
            fx.stage("ITEMS.md", TRIMMED)
            return check_staged(fx, {items.WRITER_VERB_ENV: verb})

    def test_item_repair_is_exempt_and_counted(self):
        code, out = self._out("item repair")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(removal_lines(out), [], out)
        self.assertIn("2 line(s) in ITEMS.md under the tool's own commit "
                      "(LIFECYCLE_WRITER_VERB=item repair)", out)

    def test_another_verbs_name_exempts_nothing(self):
        for verb in ("item park", "item amend", "item close", "repair", ""):
            with self.subTest(verb=verb):
                code, out = self._out(verb)
                self.assertEqual(code, exits.FINDING, out)
                self.assertEqual(len(removal_lines(out)), 1, out)


class TheDeclaredRewrite(unittest.TestCase):
    """Exemption 4: an entry under `carrier-rewrites` that THIS COMMIT adds."""

    ENTRY = {"carrier": "ITEMS.md", "date": "2026-10-05",
             "reason": "citations re-rooted to the source blob"}

    def _fx(self, td, head_entries=None):
        fx = Fixture(td, carrier=HEAD_CARRIER, commit=False)
        if head_entries is not None:
            fx.write(".claude/lifecycle.json", json.dumps(
                {**DECLARATION, decl.CARRIER_REWRITES_KEY: head_entries}))
        fx.git("add", "-A")
        fx.git("commit", "-qm", "fixture HEAD")
        fx.stage("ITEMS.md", TRIMMED)
        return fx

    def _declare(self, fx, entries):
        fx.stage(".claude/lifecycle.json", json.dumps(
            {**DECLARATION, decl.CARRIER_REWRITES_KEY: entries}))

    def test_an_entry_added_in_this_commit_exempts_and_is_counted(self):
        with tempfile.TemporaryDirectory(prefix="lbr-") as td:
            fx = self._fx(td)
            self._declare(fx, [self.ENTRY])
            code, out = check_staged(fx)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(removal_lines(out), [], out)
        self.assertIn("2 line(s) in ITEMS.md under the rewrite this commit "
                      "declares (2026-10-05: citations re-rooted to the "
                      "source blob)", out)

    def test_an_entry_HEAD_already_carries_licenses_nothing(self):
        with tempfile.TemporaryDirectory(prefix="lbr-") as td:
            fx = self._fx(td, head_entries=[self.ENTRY])
            code, out = check_staged(fx)
        self.assertEqual(code, exits.FINDING, out)
        self.assertEqual(len(removal_lines(out)), 1, out)

    def test_a_second_entry_beside_an_old_one_exempts(self):
        with tempfile.TemporaryDirectory(prefix="lbr-") as td:
            fx = self._fx(td, head_entries=[self.ENTRY])
            self._declare(fx, [self.ENTRY, {**self.ENTRY,
                                            "reason": "a second rewrite"}])
            code, out = check_staged(fx)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("a second rewrite", out)

    def test_an_entry_naming_another_carrier_licenses_nothing(self):
        with tempfile.TemporaryDirectory(prefix="lbr-") as td:
            fx = self._fx(td)
            self._declare(fx, [{**self.ENTRY, "carrier": "ITEMS-DONE.md"}])
            code, out = check_staged(fx)
        self.assertEqual(code, exits.FINDING, out)

    def test_an_entry_with_an_empty_reason_licenses_nothing(self):
        with tempfile.TemporaryDirectory(prefix="lbr-") as td:
            fx = self._fx(td)
            self._declare(fx, [{**self.ENTRY, "reason": " "}])
            code, out = check_staged(fx)
        self.assertEqual(code, exits.FINDING, out)

    def test_an_entry_written_but_NOT_STAGED_licenses_nothing(self):
        """The declaration must ride the commit: the gate reads the index."""
        with tempfile.TemporaryDirectory(prefix="lbr-") as td:
            fx = self._fx(td)
            fx.write(".claude/lifecycle.json", json.dumps(
                {**DECLARATION, decl.CARRIER_REWRITES_KEY: [self.ENTRY]}))
            code, out = check_staged(fx)
        self.assertEqual(code, exits.FINDING, out)


class WhatTheGateDoesNotGrade(unittest.TestCase):

    DONE = ("schema: 2\n\n## tt-9\ngrade: DONE\nrequirement: closed — "
            "record: LEDGER.md:3\ngoal: g\nwrite-set: a.py\n"
            "done-criterion: d\nevidence: MEASURED 2026-09-01 ran\n"
            "blocked-by: NONE\nclosed-reason: 2026-09-02 built\n")

    def test_the_closure_home_is_not_graded_for_removals(self):
        with tempfile.TemporaryDirectory(prefix="lbr-") as td:
            fx = Fixture(td, carrier=HEAD_CARRIER, done=self.DONE)
            fx.stage("ITEMS-DONE.md", self.DONE.replace(
                "closed-reason: 2026-09-02 built\n", ""))
            _code, out = check_staged(fx)
        self.assertEqual(removal_lines(out), [], out)

    def test_the_plain_check_is_unchanged(self):
        """`item check` has no HEAD to compare, and says nothing new."""
        with tempfile.TemporaryDirectory(prefix="lbr-") as td:
            fx = Fixture(td, carrier=HEAD_CARRIER)
            before = fx.check()
            fx.stage("ITEMS.md", TRIMMED)
            after = fx.check()
        self.assertNotIn(ROW, after[1])
        self.assertEqual(before[0], after[0], after[1])

    def test_a_carrier_staged_as_NEW_has_no_HEAD_block_to_lose_from(self):
        with tempfile.TemporaryDirectory(prefix="lbr-") as td:
            fx = Fixture(td, carrier=None)
            fx.stage("ITEMS.md", TRIMMED)
            _code, out = check_staged(fx)
        self.assertEqual(removal_lines(out), [], out)


class ThePredicate(unittest.TestCase):
    """`items.removed_live_lines` over two bodies, no git."""

    def test_the_multiset_counts_duplicates(self):
        dup = HEAD_CARRIER.replace(
            "amend-reason: 2026-09-02 the write set grew\n",
            "amend-reason: 2026-09-02 the write set grew\n" * 2)
        res = items.removed_live_lines(dup, HEAD_CARRIER, "tt")
        self.assertEqual(res.removed, [("tt-1", [
            ("amend-reason", "amend-reason: 2026-09-02 the write set grew")])])

    def test_blank_lines_are_not_content(self):
        spaced = HEAD_CARRIER.replace("goal: g\n", "goal: g\n\n")
        self.assertEqual(
            items.removed_live_lines(spaced, HEAD_CARRIER, "tt").removed, [])

    def test_a_line_with_no_slot_opener_is_filed_as_such(self):
        prose = HEAD_CARRIER.replace(
            "blocked-by: NONE\n", "blocked-by: NONE\n  a stray continuation\n")
        res = items.removed_live_lines(prose, HEAD_CARRIER, "tt")
        self.assertEqual(res.removed, [("tt-1", [
            (items.NO_SLOT_PREFIX, "  a stray continuation")])])

    def test_amended_blocked_by_is_NOT_the_in_place_slot(self):
        """`amended-blocked-by:` is a record; only `blocked-by:` itself is
        rewritten in place. A prefix test would exempt both."""
        head = HEAD_CARRIER.replace(
            "amended-write-set: 2026-09-02 foo.py, bar.py\n",
            "amended-write-set: 2026-09-02 foo.py, bar.py\n"
            "amended-blocked-by: 2026-09-02 NONE\n")
        res = items.removed_live_lines(head, HEAD_CARRIER, "tt")
        self.assertEqual([p for _i, ls in res.removed for p, _l in ls],
                         ["amended-blocked-by"])
        self.assertEqual(res.exempt_rewritten, 0)


class TheDeclarationKey(unittest.TestCase):
    """`carrier-rewrites`, validated like `grades-extra`: optional, shaped."""

    GOOD = {"carrier": "ITEMS.md", "date": "2026-10-05", "reason": "why"}

    def _findings(self, value):
        d = json.loads(json.dumps(refusals.GOOD_FULL_DECLARATION))
        d[decl.CARRIER_REWRITES_KEY] = value
        res = decl.Result(code=exits.CLEAN)
        decl.validate(d, res)
        return [f.message for f in res.findings
                if decl.CARRIER_REWRITES_KEY in f.message]

    def test_absent_is_no_finding_and_declares_nothing(self):
        d = json.loads(json.dumps(refusals.GOOD_FULL_DECLARATION))
        res = decl.Result(code=exits.CLEAN)
        decl.validate(d, res)
        self.assertEqual([f for f in res.findings
                          if decl.CARRIER_REWRITES_KEY in f.message], [])
        self.assertEqual(decl.carrier_rewrites(d), [])

    def test_a_well_formed_entry_is_accepted_and_read(self):
        self.assertEqual(self._findings([self.GOOD]), [])
        self.assertEqual(
            decl.carrier_rewrites({decl.CARRIER_REWRITES_KEY: [self.GOOD]}),
            [self.GOOD])

    def test_shape_problems_are_declaration_findings(self):
        for bad in ("ITEMS.md", {"carrier": "ITEMS.md"}, ["ITEMS.md"],
                    [{**self.GOOD, "reason": ""}],
                    [{**self.GOOD, "reason": "   "}],
                    [{k: v for k, v in self.GOOD.items() if k != "date"}],
                    [{**self.GOOD, "date": "5 October"}],
                    [{**self.GOOD, "by": "a desk"}]):
            with self.subTest(bad=bad):
                self.assertTrue(self._findings(bad))

    def test_a_carrier_that_is_not_the_item_home_is_a_finding(self):
        for other in ("ITEMS-DONE.md", "LEDGER.md", "notes.md"):
            with self.subTest(carrier=other):
                msgs = self._findings([{**self.GOOD, "carrier": other}])
                self.assertEqual(len(msgs), 1, msgs)
                self.assertIn("declared item home", msgs[0])

    def test_a_malformed_entry_is_not_read_as_a_licence(self):
        self.assertEqual(decl.carrier_rewrites(
            {decl.CARRIER_REWRITES_KEY: [{**self.GOOD, "reason": ""},
                                         self.GOOD]}), [self.GOOD])
        for bad in ("ITEMS.md", {"carrier": "ITEMS.md"}):
            self.assertEqual(decl.carrier_rewrites(
                {decl.CARRIER_REWRITES_KEY: bad}), [])


# --- which verbs remove lines: MEASURED over each verb's own write ----------

def _block(ident, grade, blocker, *extra):
    return (f"\n## {ident}\ngrade: {grade}\n"
            f"requirement: item {ident} of the walk — LEDGER.md\n"
            "goal: mitigate\nwrite-set: tools/harvest.mjs\n"
            "done-criterion: one fire per window\n"
            "evidence: MEASURED 2026-09-01 the fixture ran\n"
            f"blocked-by: {blocker}\n" + "".join(f"{ln}\n" for ln in extra))


def _carrier(*blocks):
    return (f"schema: {items.SCHEMA_FLOOR}\nbaseline: {len(blocks)}\n"
            "added: 0\ncompacted: 0\n" + "".join(blocks))


_ND = "not-derivable: 2026-09-03 constitutively the operator's preference"
_EX = ("blocker-exercise: 2026-09-19 live 1 | positive `true` 0 | "
       "negative `false` 1")

TWO_READY = _carrier(_block("xx-1", "READY", "NONE"),
                     _block("xx-2", "READY", "NONE"))
NEW_ITEM = _carrier(_block("xx-1", "NEW", "NONE"),
                    _block("xx-2", "READY", "NONE"))
PARKED_ON_DECISION = _carrier(
    _block("xx-1", "PARKED", "decision which shape", _ND),
    _block("xx-2", "READY", "NONE"))
PARKED_ON_EVIDENCE = _carrier(
    _block("xx-1", "PARKED", "evidence test -e arrived.flag", _EX),
    _block("xx-2", "READY", "NONE"))
WRAPPED = WRAPPED_AND_MISPLACED.replace("tt-", "xx-").replace(
    "schema: 2", f"schema: {items.SCHEMA_FLOOR}")

_CLOSE = ["--met", "none", "--decided", "none"]
_NEW_ND = ["--not-derivable", "the record was searched and does not answer "
                              "it: no ledger line, no audit"]

#: verb -> [(what the scenario exercises, HEAD carrier, [argv, …])].
#: HAND-WRITTEN BECAUSE IT IS THE CLAIM about what each verb writes; its
#: COMPLETENESS against the CLI is a separate arm, derived from the parser.
#: A scenario runs every argv in order and the predicate is applied to the
#: carrier before the FIRST and after the LAST.
SCENARIOS = {
    "item add": [
        ("a booking appends a block", TWO_READY,
         [refusals.GOOD_ADD]),
        ("a superseding booking closes the old block", TWO_READY,
         [refusals.GOOD_ADD + ["--join", "supersede xx-1",
                               "--reason", "the old item named one half"]]),
    ],
    "item park": [
        ("a first park of a READY item", TWO_READY,
         [["item", "park", "xx-1", "--blocked-by",
           "decision which shape"] + _NEW_ND]),
        ("a RE-PARK on another decision: `not-derivable:` is rewritten in "
         "place, the blocker type unchanged", PARKED_ON_DECISION,
         [["item", "park", "xx-1", "--blocked-by",
           "decision which other shape"] + _NEW_ND]),
        ("a re-park from a decision onto an item", PARKED_ON_DECISION,
         [["item", "park", "xx-1", "--blocked-by", "xx-2"]]),
        ("a RE-PARK on the SAME evidence predicate: `blocker-exercise:` is "
         "rewritten in place", PARKED_ON_EVIDENCE,
         [["item", "park", "xx-1", "--blocked-by",
           "evidence test -e arrived.flag"]]),
    ],
    "item promote": [
        ("a NEW item judged READY", NEW_ITEM,
         [["item", "promote", "xx-1", "--by", "desk-1", "--reason",
           "decision-complete on its own slots"]]),
    ],
    "item bench": [
        ("a READY item benched", TWO_READY,
         [["item", "bench", "xx-1", "--reason",
           "decision-complete and no open arc schedules it"]]),
    ],
    "item amend": [
        ("an ordinary slot amended", TWO_READY,
         [["item", "amend", "xx-1", "--done-criterion",
           "one fire per rotated window", "--reason", "the unit moved"]]),
        ("a re-type away from `decision` strands `not-derivable:`",
         PARKED_ON_DECISION,
         [["item", "amend", "xx-1", "--blocked-by", "NONE", "--reason",
           "the decision was answered"]]),
        ("the conditional slot itself amended, blocker unchanged",
         PARKED_ON_DECISION,
         [["item", "amend", "xx-1"] + _NEW_ND + ["--reason",
                                                 "names its searches now"]]),
        ("a re-type away from `evidence` strands `blocker-exercise:`",
         PARKED_ON_EVIDENCE,
         [["item", "amend", "xx-1", "--blocked-by", "xx-2", "--reason",
           "the wait is on the other item"]]),
    ],
    "item close": [
        ("a DONE close beside a block that stays", TWO_READY,
         [["item", "close", "xx-1", "--reason", "built"] + _CLOSE]),
        ("a drop beside a block that stays", TWO_READY,
         [["item", "close", "xx-1", "--drop", "--reason", "overtaken"]]),
    ],
    "item compact": [
        ("a closed body compacted", TWO_READY,
         [["item", "close", "xx-1", "--reason", "built and verified on the "
           "rotated fixture"] + _CLOSE,
          ["item", "compact", "xx-1"]]),
    ],
    "item supersede-closure": [
        ("a forward pointer on a closed body", TWO_READY,
         [["item", "close", "xx-1", "--reason", "built"] + _CLOSE,
          ["item", "supersede-closure", "xx-1", "--ref", "HEAD", "--line",
           "the later record corrects the reason"]]),
    ],
    "item repair": [
        ("a wrapped value joined back into its slot line", WRAPPED,
         [["item", "repair", "--shape"]]),
    ],
}

#: `item` actions that READ. Each is run and the carrier's bytes compared, so
#: "reads only" is observed here rather than asserted.
READ_ONLY = {
    "item check": [["item", "check"]],
    "item slots": [["item", "slots", "xx-1"]],
    "item ready": [["item", "ready"], ["item", "ready", "--head"]],
    "item waves": [["item", "waves"]],
    "item ratio": [["item", "ratio"]],
    "item statusline": [["item", "statusline"]],
}

#: Top-level verbs that are not `item`. `migrate` WRITES the item home and
#: is walked below; the rest are classified by a read of their write sites
#: (every `write_text` in the package, 2026-10-05) and are NOT executed here.
NOT_ITEM = {
    "migrate": "WRITES the item home — walked in its own arm below",
    "init": "writes a NEW carrier into a repo that has none; no HEAD block",
    "kind": "reads; `kind` writes no carrier",
    "arc": "writes arc bodies and the arc index, never the item home",
    "ledger": "writes the ledger",
    "lane": "writes lane files",
    "workflow": "writes the declaration's bindings",
    "desk": "writes desk state under the tool-state home",
    "retire": "the walk reads; compaction is `item compact`",
    "audit": "reads",
    "verify": "reads",
    "record": "reads",
}


def _parser_verbs():
    """`(top-level verbs, item actions)` from the live argparse tree."""
    parser = cli.build_parser()
    sub = argparse._SubParsersAction  # noqa: SLF001
    top = next(a for a in parser._actions if isinstance(a, sub))  # noqa: SLF001
    item = next(a for a in top.choices["item"]._actions  # noqa: SLF001
                if isinstance(a, sub))
    return set(top.choices), set(item.choices)


def _walk(head, argvs, declaration=None):
    """`(RemovedLines, before, after, [(code, out), …])` for one scenario."""
    d = build(head)
    try:
        if declaration is not None:
            (d / ".claude" / "lifecycle.json").write_text(
                json.dumps(declaration), encoding="utf-8")
            subprocess.run(["git", "commit", "-qam", "declaration"],
                           cwd=str(d), capture_output=True)
        carrier = d / "ITEMS.md"
        before = carrier.read_text(encoding="utf-8")
        runs = [run_cli(d, *argv) for argv in argvs]
        after = carrier.read_text(encoding="utf-8")
        return items.removed_live_lines(before, after, "xx"), before, after, runs
    finally:
        shutil.rmtree(d, ignore_errors=True)


class WhichVerbsRemoveLinesFromALiveBlock(unittest.TestCase):
    """Exemption 3's verb list is MEASURED: every carrier-writing verb runs
    over fixtures and part B's predicate is applied to what it wrote.

    WHAT THIS ARM ESTABLISHES AND WHAT IT DOES NOT. The scenarios are chosen
    by hand, so a verb reading CLEAN here is clean over THESE writes; the
    completeness arm guarantees every verb the CLI carries has at least one,
    never that a verb's every write path is among them.
    """

    #: The verbs whose scenarios fire, as measured. `item repair` is the
    #: exempt one. `item park` FIRES AND IS NOT EXEMPT: a re-park that keeps
    #: the blocker's type rewrites the conditional slot in place, which
    #: destroys the earlier statement — reported as a gap, not licensed.
    MEASURED_TO_FIRE = {"item repair", "item park"}

    def test_every_verb_the_CLI_carries_is_classified(self):
        top, item_actions = _parser_verbs()
        self.assertEqual(top - {"item"}, set(NOT_ITEM))
        self.assertEqual({f"item {a}" for a in item_actions},
                         set(SCENARIOS) | set(READ_ONLY))

    def test_the_reading_actions_leave_the_carrier_byte_identical(self):
        for verb, argvs in sorted(READ_ONLY.items()):
            with self.subTest(verb=verb):
                _res, before, after, _runs = _walk(PARKED_ON_DECISION, argvs)
                self.assertEqual(before, after)

    def test_each_writing_scenario_WROTE(self):
        """The walk's positive control: a scenario whose verb refused wrote
        nothing, and its clean answer would be an unread instrument."""
        for verb, scenarios in sorted(SCENARIOS.items()):
            for what, head, argvs in scenarios:
                with self.subTest(verb=verb, what=what):
                    declaration = (refusals.STANDBY_DECLARATION
                                   if verb == "item bench" else None)
                    _res, before, after, runs = _walk(head, argvs, declaration)
                    for code, out in runs:
                        self.assertEqual(code, exits.CLEAN, out)
                    if verb != "item supersede-closure":
                        self.assertNotEqual(before, after, runs)

    def test_the_verbs_that_fire_are_the_measured_set(self):
        fired = {}
        for verb, scenarios in sorted(SCENARIOS.items()):
            for what, head, argvs in scenarios:
                declaration = (refusals.STANDBY_DECLARATION
                               if verb == "item bench" else None)
                res, _b, _a, _runs = _walk(head, argvs, declaration)
                if res.removed:
                    fired.setdefault(verb, []).append((what, res.removed))
        self.assertEqual(set(fired), self.MEASURED_TO_FIRE, fired)

    def test_the_exempt_list_is_the_firing_verbs_minus_the_reported_gap(self):
        self.assertEqual(set(items.LINE_REMOVING_VERBS),
                         self.MEASURED_TO_FIRE - {"item park"})

    def test_the_park_gap_is_the_in_place_conditional_slot(self):
        """The reported gap, pinned to its exact shape so a repair of
        `item park` turns this arm red rather than leaving it stale."""
        for n, slot, line in ((1, "not-derivable", _ND),
                              (3, "blocker-exercise", _EX)):
            what, head, argvs = SCENARIOS["item park"][n]
            with self.subTest(what=what):
                res, _b, _a, _runs = _walk(head, argvs)
                self.assertEqual(res.removed, [("xx-1", [(slot, line)])])
                self.assertEqual(res.exempt_retyped, 0)

    def test_the_other_park_scenarios_remove_nothing(self):
        """THE PAIR for the gap: a first park, and a re-park that changes
        the blocker's type, are clean over the same verb."""
        for n in (0, 2):
            what, head, argvs = SCENARIOS["item park"][n]
            with self.subTest(what=what):
                res, _b, _a, _runs = _walk(head, argvs)
                self.assertEqual(res.removed, [])

    def test_the_retyping_door_is_exempt_by_type_not_by_verb(self):
        for n in (1, 3):
            what, head, argvs = SCENARIOS["item amend"][n]
            with self.subTest(what=what):
                res, _b, _a, _runs = _walk(head, argvs)
                self.assertEqual(res.removed, [])
                self.assertEqual(res.exempt_retyped, 1)

    def test_migrate_over_a_populated_carrier_rewrites_live_blocks(self):
        """`migrate` WRITES and does not COMMIT (it says so itself), so no
        verb name ever reaches the gate for it: its commit is a session's,
        and a re-derivation that rewrites live blocks passes by the declared
        rewrite or not at all. Measured here on `--force`."""
        d = build(refusals.MERGE_TARGET_ITEMS)
        try:
            (d / "BACKLOG.md").write_text(
                "# old\n\n## Open\n\n- **READY 2026-01-01 — an ordinary "
                "entry, reworded at the source.** body\n", encoding="utf-8")
            carrier = d / "ITEMS.md"
            before = carrier.read_text(encoding="utf-8")
            head_before = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=str(d),
                capture_output=True, text=True).stdout
            code, out = run_cli(d, "migrate", "--report",
                                "docs/audits/report.md", "--from-done",
                                "NONE", "--force")
            after = carrier.read_text(encoding="utf-8")
            head_after = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=str(d),
                capture_output=True, text=True).stdout
        finally:
            shutil.rmtree(d, ignore_errors=True)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotEqual(before, after, out)
        self.assertEqual(head_before, head_after,
                         "migrate committed; exemption 3 could now name it")
        res = items.removed_live_lines(before, after, "xx")
        self.assertEqual([i for i, _ls in res.removed], ["xx-1"], out)

    def test_migrate_merge_appends_and_removes_nothing(self):
        """THE PAIR: the same source over the same carrier, appended."""
        d = build(refusals.MERGE_TARGET_ITEMS)
        try:
            (d / "BACKLOG.md").write_text(
                "# old\n\n## Open\n\n- **READY 2026-01-01 — an ordinary "
                "entry, reworded at the source.** body\n", encoding="utf-8")
            carrier = d / "ITEMS.md"
            before = carrier.read_text(encoding="utf-8")
            code, out = run_cli(d, "migrate", "--report",
                                "docs/audits/report.md", "--from-done",
                                "NONE", "--merge")
            after = carrier.read_text(encoding="utf-8")
        finally:
            shutil.rmtree(d, ignore_errors=True)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotEqual(before, after, out)
        self.assertEqual(
            items.removed_live_lines(before, after, "xx").removed, [], out)


# --- the gate as a real hook, and the tool's own commit through it ----------

HOOK = """#!/bin/sh
exec "{python}" "{cli}" item check --staged
"""


def _with_gate(head):
    """A scratch repo whose pre-commit hook runs THIS working copy's CLI.

    The repo's fixtures neutralise hooks, so an arm that needs the gate
    installs its own — and installs the staged check alone, never the
    machine's hook chain.
    """
    d = build(head)
    hooks = d / ".gate"
    hooks.mkdir()
    hook = hooks / "pre-commit"
    hook.write_text(HOOK.format(python=sys.executable, cli=CLI),
                    encoding="utf-8")
    hook.chmod(hook.stat().st_mode | stat.S_IXUSR)
    subprocess.run(["git", "config", "core.hooksPath", str(hooks)],
                   cwd=str(d), capture_output=True)
    return d


def _hand_commit(d, text, env=None):
    (d / "ITEMS.md").write_text(text, encoding="utf-8")
    full = dict(os.environ)
    full.pop(items.WRITER_VERB_ENV, None)
    full.update(env or {})
    return subprocess.run(
        ["git", "commit", "-m", "a hand edit", "--", "ITEMS.md"],
        cwd=str(d), capture_output=True, text=True, env=full)


def _subjects(d):
    return subprocess.run(["git", "log", "--format=%s"], cwd=str(d),
                          capture_output=True, text=True).stdout.splitlines()


class TheGateAsARealHook(unittest.TestCase):

    HEAD = _carrier(_block(
        "xx-1", "READY", "NONE",
        "amend-reason: 2026-09-02 the unit moved",
        "amended-done-criterion: 2026-09-02 one fire per rotated window"))

    def test_a_hand_trim_is_refused_by_the_commit(self):
        d = _with_gate(self.HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        r = _hand_commit(d, _carrier(_block("xx-1", "READY", "NONE")))
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn(f"[{ROW}]", r.stdout + r.stderr)
        self.assertEqual(_subjects(d), ["seed"])

    def test_a_hand_append_is_committed(self):
        """THE PAIR: same hook, same block, nothing removed."""
        d = _with_gate(self.HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        r = _hand_commit(d, self.HEAD + "amend-reason: 2026-09-03 again\n"
                         "amended-done-criterion: 2026-09-03 per window\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(_subjects(d)[0], "a hand edit")

    def test_item_repair_commits_THROUGH_the_gate(self):
        """The tool's own commit: `commit_paths` names the verb, the gate
        reads it, and the join that removes lines is exempt and counted."""
        d = _with_gate(WRAPPED)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "item", "repair", "--shape")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("committed: item repair --shape", out)
        self.assertTrue(_subjects(d)[0].startswith("item repair --shape"),
                        _subjects(d))

    def test_the_same_join_committed_BY_HAND_is_refused(self):
        """THE PAIR for exemption 3: the bytes `item repair` writes, staged
        by a session with no verb named — the diff is identical and only
        the committer differs."""
        d = _with_gate(WRAPPED)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "item", "repair", "--shape", "--no-commit")
        self.assertEqual(code, exits.CLEAN, out)
        r = _hand_commit(d, (d / "ITEMS.md").read_text(encoding="utf-8"))
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn(f"[{ROW}]", r.stdout + r.stderr)

    def test_a_stale_verb_name_in_the_shell_does_not_ride_another_verb(self):
        """`commit_paths` SETS OR CLEARS the name. `item park` re-parking in
        place fires the gate; with `item repair` left in the calling shell
        it must still fire, because park's commit names park."""
        d = _with_gate(PARKED_ON_DECISION)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        saved = os.environ.get(items.WRITER_VERB_ENV)
        os.environ[items.WRITER_VERB_ENV] = "item repair"
        try:
            code, out = run_cli(d, *SCENARIOS["item park"][1][2][0])
        finally:
            if saved is None:
                os.environ.pop(items.WRITER_VERB_ENV, None)
            else:
                os.environ[items.WRITER_VERB_ENV] = saved
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("[move_uncommitted]", out)
        self.assertEqual(_subjects(d), ["seed"])

    def test_an_ordinary_verb_commits_through_the_gate(self):
        d = _with_gate(self.HEAD)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        code, out = run_cli(d, "item", "amend", "xx-1", "--write-set",
                            "tools/harvest.mjs, tools/rotate.mjs",
                            "--reason", "the realizing file was missing")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(_subjects(d)[0], "lifecycle: amend xx-1")


if __name__ == "__main__":
    unittest.main()
