"""lc-64 — `tend`, the plugin-reserved meta-goal (cache-fix design §3.1b).

`goal` is a per-repo DOMAIN vocabulary (§3.1), so work a repo does on ITSELF
— method decomposition, hook retirement, migration residue — advances no
declared goal and cannot be booked at all. §3.1b's fix is ONE reserved value,
`tend`, that the plugin adds to EVERY repo's effective goal set: not
declarable, not declared anywhere, accepted everywhere.

THE ARMS THAT DECIDE THIS ARE A PAIR, and the second is what makes the first
mean anything: `--goal tend` is accepted, and a DIFFERENT undeclared goal is
still refused. A build that simply stopped checking goals would satisfy the
first arm alone, and the refusal it deleted would be invisible — the whole
population of undeclared-goal items is exactly what the check exists to
catch.

Every arm here runs the CLI in a scratch repo whose declaration
(`refusals.GOOD_FULL_DECLARATION`) does NOT list `tend` — the "nothing
declared" condition the design names — and the first test PINS that fixture
premise rather than assuming it: a fixture that quietly gained `tend` would
turn the acceptance arm green for the fixture's reason instead of the
build's.
"""

import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, exits, refusals  # noqa: E402
from lifecycle_core import declaration as decl  # noqa: E402
from lifecycle_core.refusals import (  # noqa: E402
    GOOD_ADD, GOOD_FULL_DECLARATION, SEED_ITEMS, _cli)

from test_init import ScratchGitRepo  # noqa: E402

#: THE DESIGN'S OWN WORD, written here rather than read from the module under
#: test. An expectation derived from the artifact it grades moves with the
#: mutant: `RESERVED = decl.RESERVED_GOAL` would stay green through a rename
#: the design never made, and it would have turned this file's first red into
#: an `AttributeError` — a red a build that defines the constant and changes
#: nothing scores identically against.
RESERVED = "tend"

#: A goal no declaration in this repo carries and that the plugin does NOT
#: reserve — the control value the refusal must keep firing on.
UNDECLARED = "not-a-declared-goal-at-all"


def add_with_goal(goal):
    """`GOOD_ADD` with its `--goal` value replaced and nothing else touched:
    the arms below differ in that one token, so a red belongs to the goal
    check and not to a differently-shaped add."""
    argv = list(GOOD_ADD)
    argv[argv.index("--goal") + 1] = goal
    return argv


class FixturePremise(unittest.TestCase):

    def test_the_scratch_declaration_does_not_declare_tend(self):
        """The condition §3.1b names — "in every repo, with nothing
        declared" — held by the fixture rather than assumed of it."""
        self.assertNotIn(RESERVED, GOOD_FULL_DECLARATION["goals"])

    def test_the_shipped_constant_is_the_word_the_design_names(self):
        """The one place the module and the design are compared. Everything
        else in this file spells the value out, so a rename fails HERE, once,
        with the design cited — rather than passing everywhere."""
        self.assertEqual(decl.RESERVED_GOAL, RESERVED)


class EffectiveGoalSet(unittest.TestCase):

    def test_it_is_the_declared_set_union_the_reserved_value(self):
        got = decl.effective_goals({"goals": ["see", "mitigate"]})
        self.assertEqual(got, ["see", "mitigate", RESERVED])

    def test_a_declaration_with_no_goals_key_still_carries_the_reserved_one(self):
        self.assertEqual(decl.effective_goals({}), [RESERVED])

    def test_a_declaration_that_lists_it_anyway_does_not_get_it_twice(self):
        """`tend` is not declarable, but a hand-edited file can still say it.
        A duplicated entry would double it in every message that renders the
        set, so the union is a union."""
        got = decl.effective_goals({"goals": ["see", RESERVED]})
        self.assertEqual(got, ["see", RESERVED])


class ItemAdd(unittest.TestCase):

    def test_the_reserved_goal_is_accepted_with_nothing_declared(self):
        fired = _cli(add_with_goal(RESERVED))
        self.assertEqual(fired.code, exits.CLEAN, fired.output)
        self.assertNotIn("FINDING", fired.output)

    def test_a_different_undeclared_goal_is_still_refused(self):
        """THE MUST-DIFFER ARM. Same add, same repo, one token apart — a
        build that widened the check to everything scores identically to the
        correct one on the acceptance arm alone."""
        fired = _cli(add_with_goal(UNDECLARED))
        self.assertEqual(fired.code, exits.FINDING, fired.output)
        self.assertIn("FINDING [dangling_reference]", fired.output)
        self.assertIn(UNDECLARED, fired.output)

    def test_the_refusal_names_the_reserved_goal_as_an_accepted_value(self):
        """The message states the vocabulary a caller may use; leaving the
        reserved value out of it makes the one goal every repo accepts the
        one goal nobody is told about."""
        fired = _cli(add_with_goal(UNDECLARED))
        self.assertIn(RESERVED, fired.output)


class ItemAmend(unittest.TestCase):
    """The amend path carries its own arm: §3.1's own comment says an amend
    that skipped the check would be the way AROUND it."""

    def _amend(self, goal):
        return _cli(["item", "amend", "xx-1", "--goal", goal,
                     "--reason", "the goal was mis-recorded at intake"],
                    items=SEED_ITEMS)

    def test_the_reserved_goal_is_accepted(self):
        fired = self._amend(RESERVED)
        self.assertEqual(fired.code, exits.CLEAN, fired.output)

    def test_a_different_undeclared_goal_is_still_refused(self):
        fired = self._amend(UNDECLARED)
        self.assertEqual(fired.code, exits.FINDING, fired.output)
        self.assertIn("FINDING [dangling_reference]", fired.output)


class ItemCheck(unittest.TestCase):
    """A MUST-NOT arm, and it is green before this change as well as after:
    measured 2026-08-28, `item check` validates no goal against the
    declaration at all (a carrier block carrying an undeclared goal reads
    CLEAN). It is asserted because §3.1b's done-criterion names `item check`
    explicitly — the obligation is that it never starts refusing `tend`."""

    def test_a_carrier_holding_a_tend_item_reads_clean(self):
        carrier = SEED_ITEMS.replace("goal: mitigate",
                                     f"goal: {RESERVED}")
        self.assertIn(f"goal: {RESERVED}", carrier)
        fired = _cli(["item", "check"], items=carrier)
        self.assertEqual(fired.code, exits.CLEAN, fired.output)
        self.assertNotIn("FINDING", fired.output)


class HeadRuleIsNotWidened(unittest.TestCase):
    """§3.1b: `tend` sits OUTSIDE the head-rule's `lead-goal` ordering —
    meta-work never takes the scheduled head from domain work. So the
    declaration's `lead-goal` check reads the DECLARED set, not the effective
    one, and this arm is the assertion on what must NOT appear: a widening
    that reached this site would be invisible in every arm above.

    THE VERB IS `kind check`, measured rather than assumed: this arm was
    first written against `item check`, which returned CLEAN over a
    declaration whose `lead-goal` names an undeclared goal — `item check`
    grades the CARRIER and validates no declaration at all, so the arm was
    watching a route the effect never travels and its red belonged to the
    arrangement.
    """

    def _lead(self, goal):
        doc = json.loads(json.dumps(GOOD_FULL_DECLARATION))
        doc["head-rule"] = {"lead-goal": goal}
        return _cli(["kind", "check"], declaration=doc)

    def test_a_lead_goal_of_tend_is_still_a_finding(self):
        fired = self._lead(RESERVED)
        self.assertEqual(fired.code, exits.FINDING, fired.output)
        self.assertIn("dangling_reference", fired.output)

    def test_a_declared_lead_goal_is_still_clean(self):
        """The control for the arm above: same verb, same declaration, a
        lead goal that IS declared. Without it a `kind check` red for any
        other reason would read as this arm passing."""
        fired = self._lead("mitigate")
        self.assertEqual(fired.code, exits.CLEAN, fired.output)


class FreshRepo(unittest.TestCase):
    """§3.1b's first seeding verb: `init` gives a fresh repo the effective
    set from its FIRST `item add` — self-work is bookable on day one, before
    the repo accretes machinery with nowhere to file its cleanup."""

    def _init(self):
        r = ScratchGitRepo()
        r.commit_as("op@example.invalid")
        self.addCleanup(r.close)
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(["--repo", str(r.dir), "init", "--id-prefix", "xx"])
        self.assertEqual(code, exits.CLEAN, buf.getvalue())
        r.seed_carriers()
        r.commit_as("op@example.invalid")
        return r, buf.getvalue()

    def _run_in(self, repo, argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(["--repo", str(repo.dir)] + argv)
        return code, buf.getvalue()

    def test_init_does_not_write_the_reserved_goal_into_the_declaration(self):
        """It is reserved, not declared: a repo that carried it in `goals`
        would be declaring a value §3.1b says is not declarable, and the next
        repo's file would disagree with this one's."""
        r, _ = self._init()
        doc = json.loads(
            (r.dir / ".claude" / "lifecycle.json").read_text(encoding="utf-8"))
        self.assertNotIn(RESERVED, doc["goals"])

    def test_a_freshly_initialised_repo_accepts_an_item_on_the_reserved_goal(self):
        r, _ = self._init()
        code, out = self._run_in(r, add_with_goal(RESERVED))
        self.assertEqual(code, exits.CLEAN, out)

    def test_the_same_repo_still_refuses_a_different_undeclared_goal(self):
        r, _ = self._init()
        code, out = self._run_in(r, add_with_goal(UNDECLARED))
        self.assertEqual(code, exits.FINDING, out)

    def test_init_says_the_reserved_goal_is_in_the_effective_set(self):
        """The declaration cannot show it — so the one moment a repo's
        author is told the value exists is `init`'s own output."""
        _, out = self._init()
        self.assertIn(RESERVED, out)


if __name__ == "__main__":
    unittest.main()
