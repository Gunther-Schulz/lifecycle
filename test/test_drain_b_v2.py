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


if __name__ == "__main__":
    unittest.main()
