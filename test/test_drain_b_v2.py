"""Drain wave B, lane V2 — lc-109, lc-110, lc-275 (lc-270 is a gap, lc-32 is JS).

Every arm runs the `item add` verb at the CLI altitude, as
`TheCostTestsThirdConjunct` (test_items.py) does and for the reason it states:
a unit call against a changed signature reds as a TypeError, which proves only
that the signature is new.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli as cli_mod  # noqa: E402
from lifecycle_core import exits, firelog, refusals, verbs  # noqa: E402


class _CostTestBase(unittest.TestCase):
    ONE_FILE = "../dotfiles/bootstrap/manifest.py"
    TWO_FILES = "plugin/a.py,plugin/b.py"
    BLOCKER = "decision when the judgment desk lands its bundled corpus queue"

    def _repo(self, **kw):
        r = refusals._Repo(**kw)
        self.addCleanup(r.close)
        return r

    def _run(self, repo, *argv):
        here = os.getcwd()
        try:
            os.chdir(str(repo.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(repo.dir)] + list(argv))
        finally:
            os.chdir(here)
        return code, buf.getvalue()

    def _add(self, write_set, *extra,
             requirement="the deploy roster is hand-checked — LEDGER.md"):
        return ["item", "add", "--requirement", requirement,
                "--goal", "verify", "--write-set", write_set,
                "--done-criterion", "the roster is declared, not hand-checked",
                "--evidence", "MEASURED at the drainage desk",
                "--absence", "the realizing write is another desk's",
                *extra]

    def _uses(self, repo):
        """The `use=` values the register holds for THIS repo, in order."""
        out = []
        try:
            lines = firelog.log_path().read_text(encoding="utf-8").splitlines()
        except OSError:
            return out
        for ln in lines:
            rec = json.loads(ln)
            if (rec.get("verb") == "judgment:intake-cost-test"
                    and rec.get("repo") == str(repo.dir)):
                out.append(rec["detail"].split()[0])
        return out


class OverrideIsDecidedByStateNotText(_CostTestBase):
    """lc-109: the register write follows the computed reason, not the prose."""

    def _with_phrase(self):
        """Wrap the real cost_test so its MESSAGE (index 1) carries the old
        trigger phrase while verdict and reason (the state) are untouched."""
        real = verbs.cost_test

        def wrapped(*a, **k):
            r = real(*a, **k)
            return (r[0], r[1] + " ... skips the veto ...") + tuple(r[2:])
        verbs.cost_test = wrapped
        self.addCleanup(setattr, verbs, "cost_test", real)

    def test_phrase_in_message_under_operator_source_writes_no_override(self):
        # Two files: the cost test is NOT applicable, so nothing was overridden.
        self._with_phrase()
        r = self._repo()
        code, out = self._run(r, *self._add(self.TWO_FILES,
                                            "--source", "operator"))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("use=overridden", self._uses(r))

    def test_phrase_in_message_under_session_source_writes_no_override(self):
        self._with_phrase()
        r = self._repo()
        code, out = self._run(r, *self._add(self.TWO_FILES))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(self._uses(r), [])

    # --- must not move ---------------------------------------------------

    def test_genuine_operator_override_still_records_overridden(self):
        r = self._repo()
        code, out = self._run(r, *self._add(self.ONE_FILE, "--hunks", "1",
                                            "--source", "operator"))
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(self._uses(r), ["use=overridden"])

    def test_ordinary_fire_still_records_fired(self):
        r = self._repo()
        code, out = self._run(r, *self._add(self.ONE_FILE, "--hunks", "1"))
        self.assertEqual(code, exits.FINDING, out)
        self.assertEqual(self._uses(r), ["use=fired"])

    def test_rewording_the_message_moves_no_register_write(self):
        real = verbs.cost_test

        def reworded(*a, **k):
            r = real(*a, **k)
            return (r[0], "entirely different wording") + tuple(r[2:])
        verbs.cost_test = reworded
        self.addCleanup(setattr, verbs, "cost_test", real)
        r = self._repo()
        self._run(r, *self._add(self.ONE_FILE, "--hunks", "1",
                                "--source", "operator"))
        self.assertEqual(self._uses(r), ["use=overridden"])


class DeclinedByExemptionReachesTheRegister(_CostTestBase):
    """lc-110: an EVALUATION that declines to fire is counted, as `declined`."""

    def _typed_blocker_add(self, r):
        return self._run(r, *self._add(
            self.ONE_FILE, "--hunks", "1", "--blocked-by", self.BLOCKER,
            "--not-derivable", "a preference with no precedent in the ledger"))

    def test_typed_blocker_one_file_item_records_declined(self):
        r = self._repo()
        code, out = self._typed_blocker_add(r)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertEqual(self._uses(r), ["use=declined"])

    def test_declined_is_counted_in_the_fire_rates(self):
        from lifecycle_core import judgment
        r = self._repo()
        self._typed_blocker_add(r)
        recs = [json.loads(ln) for ln in
                firelog.log_path().read_text(encoding="utf-8").splitlines()
                if str(r.dir) in ln]
        rates = judgment.fire_rates(recs)["intake-cost-test"]
        self.assertEqual(rates, {"fired": 0, "legitimate": 0,
                                 "overridden": 0, "declined": 1})

    def test_veto_path_records_fired_and_never_declined(self):
        r = self._repo()
        self._run(r, *self._add(self.ONE_FILE, "--hunks", "1"))
        self.assertEqual(self._uses(r), ["use=fired"])

    def test_multi_file_clear_records_nothing(self):
        r = self._repo()
        self._run(r, *self._add(self.TWO_FILES))
        self.assertEqual(self._uses(r), [])



# --- lc-275: the intake join's candidate predicate -----------------------------
#
# THE BODIES BELOW ARE THE REAL ONES, copied from ITEMS-DONE.md (lc-256, lc-266
# as they stood live; lc-264 and lc-268 as the booking texts). Embedded rather
# than read, because the closure home is a live carrier that moves.

REQ_256 = (
    'SURFACED-AND-NOT-READ IS THE QUESTION THE WHOLE DESIGN RESTS'
    ' ON AND NOTHING COUNTS IT: with the surfacing (lc-254) and t'
    'he read verb (lc-255) both emitting into the fire log, the a'
    'bsence of a read line after a surfacing line is the measurab'
    'le event, and no verb reads that pair. Add the counter, wind'
    'owed, reporting the ratio per kind. Record: the booked desig'
    'n docs/directives/2026-09-20-o6-surfacing-design.md §4 Part '
    "C, §5 D4 and §7's third table row — the row that today has n"
    'o observer of any kind. ORDERING BEYOND THE TYPED EDGE: also'
    ' after lc-252 (this counter reads the very detail word lc-25'
    '2 repairs — the design status header states the order) and a'
    'fter lc-254; the single typed edge below carries the longest'
    ' pole.'
)
WS_256 = 'plugin/cli/lifecycle_core/verbs.py,plugin/cli/lifecycle_core/cli.py,plugin/cli/lifecycle_core/refusals.py,test/test_verbs.py,tools/prove-rows.py'

REQ_264 = (
    'O6 transition table row 3 - a moment surfaced and never read'
    ' - names the surfaced-vs-read counter as its observer and ca'
    'lls it the row that decides whether the design is worth buil'
    'ding; no item carries it. Record: docs/directives/2026-09-20'
    '-o6-surfacing-design.md sections 6-8.'
)
WS_264 = 'plugin/cli/lifecycle_core/firelog.py,plugin/cli/lifecycle_core/declaration.py,plugin/cli/lifecycle_core/cli.py,plugin/cli/lifecycle_core/retire.py,test/test_declaration.py,test/test_retire.py'

REQ_266 = (
    'The blocker_untyped finding says a bad blocked-by value reac'
    'hed the file by a path that did not pass the door, but propo'
    'ses no repair token and cannot distinguish a bypassed door f'
    'rom an author that has no door (an agent without the plugin)'
    ': the bad values stay in the carrier as the visible idiom an'
    'd neighbouring entries teach the defect faster than the chec'
    'k corrects it. Record: peer session cachyos-setup-33 reports'
    ' 2026-09-24; plugin/cli/lifecycle_core/items.py:1843-1851.'
)
WS_266 = 'plugin/cli/lifecycle_core/items.py,plugin/cli/lifecycle_core/verbs.py,test/test_items.py'

REQ_268 = (
    'The robustness review of 2026-09-18 commissioned a second la'
    'ne over the INSTRUMENTS themselves - which recorded proofs p'
    'rove less than they claim, under the lens: a pair proves the'
    ' refusal AXIS and never its REACH; reach is proven by the ar'
    'm that must stay SILENT - and that lane never returned; its '
    'output is unrecoverable and the question was never re-asked.'
    ' Record: docs/audits/2026-09-18-robustness-clean-without-loo'
    'king.md, heading Lane 2; lc-260 disposition.'
)
WS_268 = 'docs/audits/2026-09-18-robustness-clean-without-looking.md'



def _item(ident, requirement, write_set):
    return (f"## {ident}\ngrade: READY\nrequirement: {requirement}\n"
            f"goal: verify\nwrite-set: {write_set}\n"
            "done-criterion: x\nevidence: x\nblocked-by: NONE\n")


#: Two unrelated live items. They exist so the carrier has the population a
#: real one has: the rarity filter (MATCH_MAX_DOC_FRACTION) is relative to it,
#: and in a two-item carrier every shared token sits at 100% and is dropped.
FILLER = (
    _item("lc-901", "the deploy roster drifts from the machines it names, "
                    "so a rebuilt laptop misses two services", "deploy/roster.toml")
    + "\n" +
    _item("lc-902", "photo exports lose their capture timestamps after the "
                    "converter rewrites sidecar metadata", "tools/export.sh")
)


class TheIntakeJoinOffersTheSameDeliverableOnly(unittest.TestCase):
    """lc-275: a live item with the same deliverable is offered, and one that
    shares only common words is not — over the two real pairs."""

    def _parsed(self):
        from lifecycle_core import items as items_mod
        text = "\n".join([_item("lc-256", REQ_256, WS_256),
                          _item("lc-266", REQ_266, WS_266), FILLER])
        return items_mod.parse(text)

    def _offered(self, requirement, write_set):
        return {it.ident: why for it, why in
                verbs.candidates(self._parsed(), requirement, write_set)}

    def test_the_counter_booking_is_offered_its_live_duplicate(self):
        # Write-set left UNKNOWN so the arm exercises the REQUIREMENT half
        # alone; the shared cli.py in the real write-sets would offer it anyway.
        got = self._offered(REQ_264, "UNKNOWN")
        self.assertIn("lc-256", got)
        self.assertTrue(any("counter" in w for w in got["lc-256"]), got)

    def test_two_common_words_do_not_offer_an_unrelated_item(self):
        got = self._offered(REQ_268, WS_268)
        self.assertNotIn("lc-266", got, got)

    def test_the_matched_terms_are_printed_and_no_stopword_is_among_them(self):
        got = self._offered(REQ_264, "UNKNOWN")
        reasons = " ".join(got["lc-256"])
        self.assertNotIn(" stay,", reasons + ",")
        self.assertIn("shares", reasons)

    def test_the_stopwords_never_count_as_tokens(self):
        toks = verbs.requirement_tokens("stay stays the counter")
        self.assertEqual(toks, {"counter"})


if __name__ == "__main__":
    unittest.main()
