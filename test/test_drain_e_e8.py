"""Drain wave E, lane E8 — the declaration's references and reserved names.

lc-215: `migrate --schema-from` said "in every carrier" over the carriers
`declaration.carrier_homes` resolves and no others, and refused a repo
outright for lacking a `LEDGER.md` it had never declared.

Each class states which arm was RED against the unmodified code and which
arms are the MUST-NOT-MOVE half, because a repair that quietens a refusal is
only a repair while the refusals around it still fire.
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

from lifecycle_core import cli, exits  # noqa: E402
from lifecycle_core import declaration as decl  # noqa: E402
from lifecycle_core.refusals import (  # noqa: E402
    EMPTY_DONE, GOOD_FULL_DECLARATION, SEED_ITEMS)


def build(declaration, *, schema=None, ledger=True, extra=None) -> Path:
    """A scratch repo at `schema` (default: this build's floor).

    `ledger=False` leaves `LEDGER.md` out entirely — the population lc-215 is
    about. `extra` is `{relative path: text}` written beside the carriers.
    """
    floor = f"schema: {decl.SCHEMA_FLOOR}"
    head = floor if schema is None else f"schema: {schema}"
    d = Path(tempfile.mkdtemp(prefix="lifecycle-e8-"))
    run = lambda *a: subprocess.run(a, cwd=str(d), capture_output=True,  # noqa: E731
                                    text=True)
    run("git", "init", "-q", "-b", "main")
    run("git", "config", "core.hooksPath", str(d / ".nohooks"))
    run("git", "config", "user.email", "e8@lifecycle.invalid")
    run("git", "config", "user.name", "e8 test")
    (d / ".claude").mkdir()
    (d / ".claude" / "lifecycle.json").write_text(
        json.dumps(declaration), encoding="utf-8")
    (d / "LAWS.md").write_text("law\n", encoding="utf-8")
    (d / "ITEMS.md").write_text(SEED_ITEMS.replace(floor, head),
                                encoding="utf-8")
    (d / "ITEMS-DONE.md").write_text(EMPTY_DONE.replace(floor, head),
                                     encoding="utf-8")
    if ledger:
        (d / "LEDGER.md").write_text(head + "\n", encoding="utf-8")
    for rel, text in (extra or {}).items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    run("git", "add", "-A")
    run("git", "commit", "-qm", "seed")
    return d


def run_cli(repo: Path, *argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(["--repo", str(repo)] + list(argv))
    return code, buf.getvalue()


def good(**kinds_change):
    """`GOOD_FULL_DECLARATION`, copied, with kinds added (a body) or removed
    (`None`)."""
    doc = json.loads(json.dumps(GOOD_FULL_DECLARATION))
    for name, body in kinds_change.items():
        name = name.replace("_", " ")
        if body is None:
            doc["kinds"].pop(name, None)
        else:
            doc["kinds"][name] = body
    return doc


#: A schema-1 declaration registering the `items` kind ONLY — no
#: `ledger lines` kind — with every key the migration would otherwise call
#: unclassified already supplied. The same shape `test_schema.py`'s
#: `SchemaMigrationRefusesToGuess.OLD` uses.
OLD_NO_LEDGER_KIND = {
    "schema": 1, "id-prefix": "xx", "public": False, "laws": "LAWS.md",
    "closure-home": "ITEMS-DONE.md", "trigger-policy": "on-demand",
    "goals": ["mitigate"], "ready-cap": 10,
    "head-rule": {"lead-goal": "mitigate"},
    "lanes": [], "template-bindings": {},
    "leak-scan": {"source-scope-foreign-path": True},
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

LEDGER_KIND = {
    "home": "LEDGER.md", "writer": "verb:ledger add",
    "reader": ["verb:item ready"],
    "staleness": "none, declared why: a decision is never stale",
    "exit": {"action": "compact", "recording-act": "the fire log"},
    "bound": "unbounded, declared why: decisions accrue",
}


class AnUndeclaredAbsentLedgerDoesNotRefuseTheMigration(unittest.TestCase):
    """lc-215, consequence (a).

    `carrier_homes` gives the ledger a home whether or not the repo declares
    one: `LEDGER.md`, `verbs.context`'s own fallback. That default is right —
    it is where `ledger add` writes — and it stays. What was wrong is what the
    two consumers did with it: a repo that declares no `ledger lines` kind
    and has no file there was refused, by `migrate --schema-from` BEFORE any
    plan printed and by `kind check` as could-not-verify, for lacking a file
    it never said it had.
    """

    def _repo(self, declaration, **kw):
        d = build(declaration, **kw)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def test_RED_FIRST_the_dry_run_prints_its_plan_and_says_why_not(self):
        d = self._repo(OLD_NO_LEDGER_KIND, schema=1, ledger=False)
        code, out = run_cli(d, "migrate", "--schema-from", "1")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("declaration changes:", out,
                      "the run refused before printing any plan")
        self.assertIn("DRY RUN complete, nothing written", out)
        # TOLD, not merely let through: the skipped default is named, with
        # the two facts that make skipping it correct.
        not_examined = [ln for ln in out.split("\n")
                        if ln.strip().startswith("not examined:")]
        self.assertEqual(len(not_examined), 1, out)
        self.assertIn("LEDGER.md", not_examined[0])
        self.assertIn("declares no `ledger lines` kind", not_examined[0])

    def test_RED_FIRST_the_apply_migrates_what_the_repo_has(self):
        d = self._repo(OLD_NO_LEDGER_KIND, schema=1, ledger=False)
        code, out = run_cli(d, "migrate", "--schema-from", "1", "--apply")
        self.assertEqual(code, exits.CLEAN, out)
        after = json.loads((d / ".claude" / "lifecycle.json").read_text())
        self.assertEqual(after["schema"], decl.SCHEMA_FLOOR)
        for name in ("ITEMS.md", "ITEMS-DONE.md"):
            self.assertIn(f"schema: {decl.SCHEMA_FLOOR}",
                          (d / name).read_text(encoding="utf-8"), name)
        self.assertFalse((d / "LEDGER.md").exists(),
                         "the migration created a ledger nobody declared")

    def test_RED_FIRST_kind_check_does_not_call_it_unverifiable(self):
        """The second consumer of the same resolution, same defect."""
        doc = good(ledger_lines=None)
        d = self._repo(doc, ledger=False)
        res = decl.Result(code=0)
        decl.check_schema_agreement(d, doc, res)
        self.assertEqual(res.unverified, [], str(res.unverified))
        self.assertEqual(res.findings, [], str(res.findings))

    def test_MUST_NOT_MOVE_a_DECLARED_ledger_that_is_absent_still_refuses(self):
        """The quiet is for a file the repo never declared, and only that."""
        doc = {**OLD_NO_LEDGER_KIND,
               "kinds": {**OLD_NO_LEDGER_KIND["kinds"],
                         "ledger lines": LEDGER_KIND}}
        d = self._repo(doc, schema=1, ledger=False)
        code, out = run_cli(d, "migrate", "--schema-from", "1")
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("`ledger lines` carrier 'LEDGER.md'", out)
        self.assertNotIn("declaration changes:", out)

        at_floor = good()
        d2 = self._repo(at_floor, ledger=False)
        res = decl.Result(code=0)
        decl.check_schema_agreement(d2, at_floor, res)
        self.assertEqual(len(res.unverified), 1, str(res.unverified))

    def test_MUST_NOT_MOVE_an_undeclared_ledger_that_EXISTS_is_still_bumped(self):
        """The default is still the tool's ledger home: a file sitting there
        is a carrier, declared kind or not, and moves with the others."""
        d = self._repo(OLD_NO_LEDGER_KIND, schema=1, ledger=True)
        code, out = run_cli(d, "migrate", "--schema-from", "1", "--apply")
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn(f"schema: {decl.SCHEMA_FLOOR}",
                      (d / "LEDGER.md").read_text(encoding="utf-8"))
        self.assertNotIn("not examined:", out)

    def test_MUST_NOT_MOVE_an_undeclared_ledger_that_exists_is_still_graded(self):
        doc = good(ledger_lines=None)
        d = self._repo(doc, ledger=True)
        (d / "LEDGER.md").write_text(
            f"schema: {decl.SCHEMA_FLOOR - 1}\n", encoding="utf-8")
        res = decl.Result(code=0)
        decl.check_schema_agreement(d, doc, res)
        self.assertEqual([f.row for f in res.findings], ["schema_mismatch"])

    def test_MUST_NOT_BUILD_carrier_homes_resolves_what_it_always_did(self):
        """`carrier_homes` is NOT narrowed: `retire` reads it for the set of
        block carriers, and a ledger that vanished from it there would be a
        second, silent change riding this one."""
        doc = good(ledger_lines=None)
        self.assertEqual(decl.carrier_homes(doc)["ledger lines"], "LEDGER.md")
        self.assertEqual(sorted(decl.carrier_homes(good())),
                         ["done bodies", "items", "ledger lines"])
        self.assertEqual(decl.carrier_defaults(good()), frozenset())
        self.assertEqual(decl.carrier_defaults(doc),
                         frozenset({"ledger lines"}))


class TheCleanSentenceNamesWhatItExamined(unittest.TestCase):
    """lc-215, consequence (b).

    "already at schema N in the declaration and in every carrier" was said
    over the carriers `carrier_homes` resolves. A sentence wider than the loop
    above it is the assurance wider than its predicate, so it now names the
    kinds — and a schema-bearing file under a declared kind the loop does not
    reach is TOLD it was not reached.
    """

    NOTES = {
        "home": "NOTES.md", "writer": "session", "reader": ["session"],
        "staleness": "none, declared why: a fixture",
        "exit": {"action": "delete", "recording-act": "the fire log"},
        "growth": "bounded-by-exit",
        "trigger": "none, declared why: a fixture",
    }

    def _repo(self, declaration, **kw):
        d = build(declaration, **kw)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def _nothing_to_do(self, d):
        code, out = run_cli(d, "migrate", "--schema-from",
                            str(decl.SCHEMA_FLOOR), "--apply")
        self.assertEqual(code, exits.CLEAN, out)
        line = [ln for ln in out.split("\n") if "nothing to do" in ln]
        self.assertEqual(len(line), 1, out)
        return out, line[0]

    def test_RED_FIRST_the_sentence_names_the_kinds_not_every_carrier(self):
        d = self._repo(good())
        out, line = self._nothing_to_do(d)
        self.assertNotIn("every carrier", out)
        for kind in decl.carrier_homes(good()):
            self.assertIn(kind, line)
        self.assertIn("3 carrier file(s) examined", line)

    def test_RED_FIRST_a_schema_bearing_carrier_outside_them_is_told(self):
        d = self._repo(good(notes=self.NOTES),
                       extra={"NOTES.md": "schema: 3\n\nbody\n"})
        out, line = self._nothing_to_do(d)
        told = [ln for ln in out.split("\n")
                if ln.strip().startswith("NOT REACHED")]
        self.assertEqual(len(told), 1, out)
        self.assertIn("notes", told[0])
        self.assertIn("NOTES.md", told[0])
        self.assertIn("schema 3", told[0])
        # And the CLEAN sentence does not read as covering it.
        self.assertIn("NOT examined", line)

    def test_CONTROL_a_declared_kind_with_no_schema_line_is_not_listed(self):
        """`laws` is a declared kind whose home carries no `schema:` head; an
        instrument that listed it would be reporting every declared file."""
        d = self._repo(good(notes=self.NOTES),
                       extra={"NOTES.md": "just prose\n"})
        out, line = self._nothing_to_do(d)
        self.assertNotIn("NOT REACHED", out)
        self.assertNotIn("NOT examined", line)

    def test_the_reader_is_one_body_and_skips_the_reached_homes(self):
        doc = good(notes=self.NOTES)
        d = self._repo(doc, extra={"NOTES.md": "schema: 3\n"})
        self.assertEqual(decl.unreached_schema_carriers(d, doc),
                         [("notes", "NOTES.md", 3)])
        self.assertEqual(decl.unreached_schema_carriers(d, good()), [])


if __name__ == "__main__":
    unittest.main()
