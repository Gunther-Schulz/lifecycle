"""Wave 2, item C: the plugin's template registry, and `lifecycle workflow
bind` (design §3.8b/§3.11 — carrier-rework-design-2026-08-26.md).

The refusal roster proves six FINDING sites with their own plant/control
pair: `binding_slot_unbound` (two firing inputs — a present UNKNOWN value,
and the CORRECTED shape, a required key absent entirely),
`binding_template_missing`, and `binding_template_unparsable` (all three
`kind check` findings, in `refusals.ROWS` beside `dangling_reference`) and
`workflow_binding_exists` (the bind verb's own refuse-without-`--force`,
in `refusals.WORKFLOW_ROWS`). What is here is the rest: the parser's four
shapes (an absent `Slots:` line, a present-but-empty one, a malformed slot
name, a well-formed list), the round trip against a real bind (every
required slot present as a key, `--set` filling some and `UNKNOWN` filling
the rest), the two exit-3 "unreadable input" cases (a missing template, an
undeclared `--set` slot), and the `--force` overwrite.

CORRECTED 2026-08-26 (the judgment desk's own defect): the first cut of
`binding_slot_unbound` compared only VALUES against `UNKNOWN`, never
whether the binding's KEYS match the template's declared slots — so a
template gaining a slot left every binding written before it reading
CLEAN, with no UNKNOWN value to find. `_validate_template_bindings` now
parses the template via `read_template()` (one parser, one caller) and
treats an absent required key as the same finding; a template that
exists but fails to parse gets its own finding,
`binding_template_unparsable`.

`workflows.registry_dir` is a MODULE-LEVEL FUNCTION precisely so tests can
redirect it: the real `plugin/workflows/` ships holding only `.gitkeep`,
and a fixture template must never be planted there.
"""

import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli, exits  # noqa: E402
from lifecycle_core import declaration as decl  # noqa: E402
from lifecycle_core import items as items_mod  # noqa: E402
from lifecycle_core import workflows as workflows_mod  # noqa: E402
from lifecycle_core.refusals import (  # noqa: E402
    GOOD_FULL_DECLARATION, _Repo as _RefusalsRepo)


def _run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(argv)
    return code, buf.getvalue()


class ScratchRegistry:
    """A throwaway `plugin/workflows/`-shaped directory, monkeypatched onto
    `workflows.registry_dir` for the test's duration — isolated from the
    real registry the same way `refusals.py`'s `_decl_run_with_templates`
    and `_workflow_cli` isolate it for the roster rows."""

    def __init__(self, templates=None):
        import tempfile
        self.dir = Path(tempfile.mkdtemp(prefix="lifecycle-wftest-reg-"))
        for tid, body in (templates or {}).items():
            (self.dir / f"{tid}.md").write_text(body, encoding="utf-8")
        self._orig = workflows_mod.registry_dir
        workflows_mod.registry_dir = lambda: self.dir

    def write(self, template_id: str, body: str) -> None:
        (self.dir / f"{template_id}.md").write_text(body, encoding="utf-8")

    def cleanup(self):
        import shutil
        workflows_mod.registry_dir = self._orig
        shutil.rmtree(self.dir, ignore_errors=True)


def _decl_with_binding(binding: dict) -> dict:
    d = json.loads(json.dumps(GOOD_FULL_DECLARATION))
    d["template-bindings"] = binding
    return d


class SlotParsing(unittest.TestCase):
    """`read_template()`'s four shapes: absent `Slots:` (zero slots, VALID),
    present-but-empty (PARSE FAILURE), a malformed name (PARSE FAILURE,
    named), and a well-formed comma list."""

    def setUp(self):
        self.reg = ScratchRegistry()

    def tearDown(self):
        self.reg.cleanup()

    def test_absent_slots_line_is_zero_required_slots(self):
        self.reg.write("noslots", "just a procedure\nno Slots: line at all\n")
        t = workflows_mod.read_template("noslots")
        self.assertIsNone(t.problem, t.problem)
        self.assertEqual(t.slots, [])

    def test_present_empty_slots_line_is_a_parse_failure(self):
        self.reg.write("empty", "Slots:\n\nprocedure\n")
        t = workflows_mod.read_template("empty")
        self.assertIsNotNone(t.problem)
        self.assertIn("PARSE FAILURE", t.problem)
        # Never silently read as zero (brief §1) — a caller reading only
        # `.slots` on a failed parse would otherwise see the same [] an
        # absent line produces.
        self.assertEqual(t.slots, [])

    def test_malformed_slot_name_is_a_parse_failure_named(self):
        self.reg.write("bad", "Slots: a, Bad-Name!, c\n\nprocedure\n")
        t = workflows_mod.read_template("bad")
        self.assertIsNotNone(t.problem)
        self.assertIn("Bad-Name!", t.problem)

    def test_well_formed_slots_line_parses(self):
        self.reg.write("good", "Slots: a, b_c, d-e\n\nprocedure\n")
        t = workflows_mod.read_template("good")
        self.assertIsNone(t.problem, t.problem)
        self.assertEqual(t.slots, ["a", "b_c", "d-e"])

    def test_missing_file_is_named_not_read_as_zero_slots(self):
        t = workflows_mod.read_template("nosuchtemplate")
        self.assertIsNotNone(t.problem)
        self.assertIsNone(t.path)


class BindRoundTrip(unittest.TestCase):
    """`workflow bind` writes every required slot as a key — `--set` fills
    some, everything else is `items_mod.UNKNOWN` — and the write round-
    trips through the repo's own declaration reader."""

    def setUp(self):
        self.reg = ScratchRegistry(
            templates={"t1": "Slots: a, b\n\nprocedure text\n"})
        self.repo = _RefusalsRepo()

    def tearDown(self):
        self.reg.cleanup()
        self.repo.close()

    def test_bind_writes_every_required_slot_some_set_some_unknown(self):
        code, out = _run(["--repo", str(self.repo.dir), "workflow", "bind",
                          "t1", "--set", "a=hello"])
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("filled: a", out)
        self.assertIn("UNKNOWN: b", out)

        res = decl.read(self.repo.dir)
        tb = res.declaration["template-bindings"]
        self.assertEqual(tb["t1"], {"a": "hello", "b": items_mod.UNKNOWN})

    def test_bind_with_no_set_leaves_every_slot_unknown(self):
        code, out = _run(["--repo", str(self.repo.dir), "workflow", "bind",
                          "t1"])
        self.assertEqual(code, exits.CLEAN, out)
        res = decl.read(self.repo.dir)
        tb = res.declaration["template-bindings"]
        self.assertEqual(tb["t1"], {"a": items_mod.UNKNOWN,
                                    "b": items_mod.UNKNOWN})

    def test_zero_slot_template_binds_to_an_empty_entry(self):
        self.reg.write("empty-tmpl", "no Slots: line — zero required slots\n")
        code, out = _run(["--repo", str(self.repo.dir), "workflow", "bind",
                          "empty-tmpl"])
        self.assertEqual(code, exits.CLEAN, out)
        res = decl.read(self.repo.dir)
        self.assertEqual(res.declaration["template-bindings"]["empty-tmpl"], {})


class ExitThreeCases(unittest.TestCase):
    """§2's two UNREADABLE-INPUT cases: a template id with no file, and a
    `--set` naming a slot the template does not declare. Both exit 3, and
    neither prints a `FINDING [...]` bracket — the brief's own rule:
    unreadable input is not a finding."""

    def setUp(self):
        self.reg = ScratchRegistry(
            templates={"t1": "Slots: a, b\n\nprocedure text\n"})
        self.repo = _RefusalsRepo()

    def tearDown(self):
        self.reg.cleanup()
        self.repo.close()

    def test_missing_template_exits_3(self):
        code, out = _run(["--repo", str(self.repo.dir), "workflow", "bind",
                          "nosuchtemplate"])
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertNotIn("FINDING [", out)

    def test_undeclared_set_slot_exits_3(self):
        code, out = _run(["--repo", str(self.repo.dir), "workflow", "bind",
                          "t1", "--set", "zzz=hi"])
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("zzz", out)
        self.assertNotIn("FINDING [", out)

    def test_malformed_template_exits_3_not_2(self):
        """A template that EXISTS but fails to parse (a malformed `Slots:`
        line) is the same UNREADABLE-INPUT shape as a missing file: the
        binder cannot form a required-slot set to bind against either
        way. Judgment call, flagged: the brief names only the no-file
        case's exit code explicitly; this extends the same rule to the
        sibling failure the parser also names, rather than leaving it
        undecided."""
        self.reg.write("bad", "Slots: a, Bad-Name!\n\nprocedure\n")
        code, out = _run(["--repo", str(self.repo.dir), "workflow", "bind",
                          "bad"])
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertNotIn("FINDING [", out)


class RefusalAndForce(unittest.TestCase):
    """The roster's own `workflow_binding_exists` row proves this with a
    real plant/control; this is the same pair read directly."""

    def setUp(self):
        self.reg = ScratchRegistry(
            templates={"t1": "Slots: a\n\nprocedure\n"})
        self.repo = _RefusalsRepo()

    def tearDown(self):
        self.reg.cleanup()
        self.repo.close()

    def test_refuses_over_an_existing_binding(self):
        c1, _ = _run(["--repo", str(self.repo.dir), "workflow", "bind", "t1"])
        self.assertEqual(c1, exits.CLEAN)
        c2, out2 = _run(["--repo", str(self.repo.dir), "workflow", "bind",
                         "t1"])
        self.assertEqual(c2, exits.FINDING, out2)
        self.assertIn("FINDING [workflow_binding_exists]", out2)

    def test_force_overwrites(self):
        c1, _ = _run(["--repo", str(self.repo.dir), "workflow", "bind", "t1"])
        self.assertEqual(c1, exits.CLEAN)
        c2, out2 = _run(["--repo", str(self.repo.dir), "workflow", "bind",
                         "t1", "--set", "a=filled", "--force"])
        self.assertEqual(c2, exits.CLEAN, out2)
        res = decl.read(self.repo.dir)
        self.assertEqual(res.declaration["template-bindings"]["t1"],
                         {"a": "filled"})


class KindCheckFindings(unittest.TestCase):
    """`kind check`'s two new findings, red on a constructed binding and
    green after repair — the same pair `refusals.py`'s rows prove, read
    here directly against `decl.read()`."""

    def setUp(self):
        self.reg = ScratchRegistry(
            templates={"t1": "Slots: a\n\nprocedure\n"})
        self.repo = _RefusalsRepo(
            declaration=_decl_with_binding({"t1": {"a": items_mod.UNKNOWN}}))

    def tearDown(self):
        self.reg.cleanup()
        self.repo.close()

    def test_unbound_slot_is_red_then_green_after_repair(self):
        res = decl.read(self.repo.dir)
        self.assertIn("binding_slot_unbound",
                      [f.row for f in res.findings])

        fixed = json.loads((self.repo.dir / ".claude" / "lifecycle.json")
                           .read_text(encoding="utf-8"))
        fixed["template-bindings"]["t1"]["a"] = "filled"
        (self.repo.dir / ".claude" / "lifecycle.json").write_text(
            json.dumps(fixed), encoding="utf-8")
        res2 = decl.read(self.repo.dir)
        self.assertNotIn("binding_slot_unbound",
                         [f.row for f in res2.findings])

    def test_missing_template_is_red_then_green_after_repair(self):
        fixed = json.loads((self.repo.dir / ".claude" / "lifecycle.json")
                           .read_text(encoding="utf-8"))
        fixed["template-bindings"] = {"ghost": {}}
        (self.repo.dir / ".claude" / "lifecycle.json").write_text(
            json.dumps(fixed), encoding="utf-8")
        res = decl.read(self.repo.dir)
        self.assertIn("binding_template_missing",
                      [f.row for f in res.findings])

        self.reg.write("ghost", "no Slots: line — zero required slots\n")
        res2 = decl.read(self.repo.dir)
        self.assertNotIn("binding_template_missing",
                         [f.row for f in res2.findings])

    def test_absent_required_key_is_the_same_finding_as_unknown_value(self):
        """CORRECTED 2026-08-26: the first cut of `binding_slot_unbound`
        fired only on a PRESENT value equal to UNKNOWN. A required slot
        ABSENT from the binding entirely (a template gaining a slot after
        the binding was written) is the same defect with no value to
        see, and read CLEAN before this correction — the discriminating
        arm that matters."""
        self.reg.write("t1", "Slots: a, b\n\nprocedure\n")
        fixed = json.loads((self.repo.dir / ".claude" / "lifecycle.json")
                           .read_text(encoding="utf-8"))
        # `b` is not a key at all — not even UNKNOWN.
        fixed["template-bindings"] = {"t1": {"a": "filled"}}
        (self.repo.dir / ".claude" / "lifecycle.json").write_text(
            json.dumps(fixed), encoding="utf-8")
        res = decl.read(self.repo.dir)
        self.assertIn("binding_slot_unbound", [f.row for f in res.findings])

        fixed["template-bindings"]["t1"]["b"] = "also-filled"
        (self.repo.dir / ".claude" / "lifecycle.json").write_text(
            json.dumps(fixed), encoding="utf-8")
        res2 = decl.read(self.repo.dir)
        self.assertNotIn("binding_slot_unbound",
                         [f.row for f in res2.findings])

    def test_unparsable_template_is_red_then_green_after_repair(self):
        self.reg.write("bad", "Slots: a, Bad-Name!\n\nprocedure\n")
        fixed = json.loads((self.repo.dir / ".claude" / "lifecycle.json")
                           .read_text(encoding="utf-8"))
        fixed["template-bindings"] = {"bad": {"a": "filled"}}
        (self.repo.dir / ".claude" / "lifecycle.json").write_text(
            json.dumps(fixed), encoding="utf-8")
        res = decl.read(self.repo.dir)
        self.assertIn("binding_template_unparsable",
                      [f.row for f in res.findings])

        self.reg.write("bad", "Slots: a\n\nprocedure\n")
        res2 = decl.read(self.repo.dir)
        self.assertNotIn("binding_template_unparsable",
                         [f.row for f in res2.findings])


if __name__ == "__main__":
    unittest.main()
