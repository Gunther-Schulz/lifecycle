"""Drain wave D, lane D2 — conservation in the reading verbs; two commit
sites (2026-10-07).

ONE FILE FOR THE LANE (wave B change 4). The lc-203 battery was BUILT by
wave C lane C4 and shelved with its patch
(`docs/directives/2026-10-07-lc203-built-not-landed.md`); it is carried here
rather than into that lane's file, which is outside this lane's write set.

EVERY FIXTURE IS A REAL GIT WORK TREE: both items turn on what git says about
a carrier — what is committed, and what is pending over it.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import json
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli as cli_mod, exits, items, refusals  # noqa: E402


def carrier(blocks):
    """A carrier whose conservation identity balances over `blocks`."""
    out = [f"schema: {items.SCHEMA_FLOOR}", f"baseline: {len(blocks)}",
           "added: 0", "compacted: 0", ""]
    for ident, slots in blocks:
        out.append(f"## {ident}")
        for slot in items.SLOTS:
            out.append(f"{slot}: {slots[slot]}")
        out.append("")
    return "\n".join(out)


def block(ident, write_set, *, grade="READY", blocked_by="NONE"):
    return (ident, {
        "grade": grade,
        "requirement": f"{ident} exists so a carrier has a body to count — "
                       "record: test_drain_d_d2.py",
        "goal": "mitigate",
        "write-set": write_set,
        "done-criterion": "the verdict it draws is the verdict it earns",
        "evidence": "MEASURED: constructed for this battery",
        "blocked-by": blocked_by,
    })


#: The tree every fixture repo tracks, so a READY write-set resolves.
TRACKED = ("docs/readme.md", "test/absence-scan.test.mjs")


def git(repo, *argv):
    return subprocess.run(["git"] + list(argv), cwd=str(repo.dir),
                          capture_output=True, text=True)


class Base(unittest.TestCase):

    def _repo(self, text):
        repo = refusals._Repo(items=text)
        for rel in TRACKED:
            p = repo.dir / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("seed\n", encoding="utf-8")
        git(repo, "add", "--", *TRACKED)
        git(repo, "commit", "-qm", "tracked tree")
        return repo

    def _run(self, repo, *argv):
        here = os.getcwd()
        try:
            os.chdir(str(repo.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(repo.dir)] + list(argv))
            return code, buf.getvalue()
        finally:
            os.chdir(here)


# --- lc-203 -------------------------------------------------------------------

#: A REAL two-item carrier, and the same bytes CUT IMMEDIATELY BEFORE THE
#: SECOND HEADING — the shape `atomic.py`'s docstring warns about. The head
#: still says two bodies were admitted; one is in the file.
WHOLE = carrier([block("xx-1", "docs/readme.md"),
                 block("xx-2", "test/absence-scan.test.mjs")])
CUT = WHOLE[:WHOLE.index("## xx-2")]

#: The reading verbs that print a POPULATION — a count of what they read.
COUNTING_VERBS = (
    ("item", "ready", "--head"),
    ("item", "ready", "xx-1"),
    ("item", "waves"),
    ("item", "ratio"),
)


class EveryReadingVerbStatesItsExtent(Base):
    """lc-203 — conservation was the only instrument that saw a truncated
    carrier, and it ran in exactly one verb.

    Each reading verb is run over the cut carrier and must name the missing
    body itself; over the whole one it must say the extent it checked.
    """

    def test_the_fixture_is_the_truncation_the_item_names(self):
        self.assertIn("baseline: 2", CUT)
        self.assertIn("## xx-1", CUT)
        self.assertNotIn("## xx-2", CUT)

    def test_item_check_already_names_it(self):
        """The baseline arm: the instrument that DID see it, so the arms
        below are red for the missing call and not for the fixture."""
        with self._repo(CUT) as r:
            code, out = self._run(r, "item", "check")
            self.assertIn("FINDING [conservation_short]", out)
            self.assertEqual(code, exits.FINDING, out)

    def test_each_counting_verb_NAMES_the_missing_body(self):
        for argv in COUNTING_VERBS:
            with self.subTest(verb=" ".join(argv)):
                with self._repo(CUT) as r:
                    code, out = self._run(r, *argv)
                    self.assertIn("FINDING [conservation_short]", out)
                    self.assertNotEqual(code, exits.CLEAN, out)

    def test_a_verb_that_was_CLEAN_over_the_cut_carrier_is_now_a_FINDING(self):
        """`ready` answered exit 0 — schedulable — over a carrier missing a
        body. The code is the part a scripted caller reads."""
        for argv in (("item", "ready", "--head"), ("item", "ready", "xx-1"),
                     ("item", "waves")):
            with self.subTest(verb=" ".join(argv)):
                with self._repo(CUT) as r:
                    code, out = self._run(r, *argv)
                    self.assertEqual(code, exits.FINDING, out)

    def test_NO_counting_verb_prints_a_count_with_no_extent_statement(self):
        """The assertion on what must NOT appear: a population reported
        with nothing said about whether it is the whole population. Over the
        WHOLE carrier, so this is the arm that catches the check DEGRADING —
        a verb that stopped running it would still pass the cut-carrier arm
        of nothing but its own silence."""
        for argv in COUNTING_VERBS:
            with self.subTest(verb=" ".join(argv)):
                with self._repo(WHOLE) as r:
                    _code, out = self._run(r, *argv)
                    extent = [ln for ln in out.splitlines()
                              if ln.startswith("conservation: items 2 + done 0")]
                    self.assertEqual(len(extent), 1, out)
                    self.assertIn("conservation: CLEAN", out)

    def test_the_whole_carrier_keeps_the_code_each_verb_gave(self):
        """MUST-NOT-MOVE: a balanced carrier changes no verb's answer."""
        for argv, want in ((("item", "ready", "--head"), exits.CLEAN),
                           (("item", "ready", "xx-1"), exits.CLEAN),
                           (("item", "waves"), exits.CLEAN)):
            with self.subTest(verb=" ".join(argv)):
                with self._repo(WHOLE) as r:
                    code, out = self._run(r, *argv)
                    self.assertEqual(code, want, out)

    def test_slots_names_the_missing_body_too(self):
        with self._repo(CUT) as r:
            code, out = self._run(r, "item", "slots", "xx-1")
            self.assertIn("FINDING [conservation_short]", out)
            self.assertEqual(code, exits.FINDING, out)

    def test_slots_over_a_whole_carrier_is_the_DATA_and_nothing_else(self):
        """`item slots` is the pickup instrument and its `--json` form is
        parsed. It prints no population, so over a balanced carrier it adds
        no line — a second line there would break every reader of it."""
        with self._repo(WHOLE) as r:
            code, out = self._run(r, "item", "slots", "xx-1", "--json")
            self.assertEqual(code, exits.CLEAN, out)
            self.assertEqual(json.loads(out)["ident"], "xx-1")
            code, out = self._run(r, "item", "slots", "xx-1")
            self.assertNotIn("conservation", out)
            self.assertEqual(out.splitlines()[0], "grade: READY")

    def test_a_head_that_cannot_be_computed_is_COULD_NOT_VERIFY(self):
        """The third answer travels with the check: no baseline, no
        identity, and `ready` must not call that carrier clean."""
        with self._repo(WHOLE.replace("baseline: 2\n", "", 1)) as r:
            code, out = self._run(r, "item", "ready", "xx-1")
            self.assertIn("COULD NOT VERIFY: conservation", out)
            self.assertEqual(code, exits.COULD_NOT_VERIFY, out)


if __name__ == "__main__":
    unittest.main()
