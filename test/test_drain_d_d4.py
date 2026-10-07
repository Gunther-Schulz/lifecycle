"""Drain wave D, lane D4 — lc-323: four naming leftovers from lc-316/lc-317.

One class per leftover, each carrying the arms the done-criterion names, and
each with a MUST-NOT-MOVE arm on the exit code: naming a refusal changes what
it PRINTS and never what it ANSWERS.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "plugin" / "cli"))

from lifecycle_core import declaration as decl  # noqa: E402
from lifecycle_core import exits, refusals, roster  # noqa: E402

CORE = REPO / "plugin" / "cli" / "lifecycle_core"

#: Bytes no UTF-8 decoder accepts. The unreadable-laws arm is built from
#: CONTENT and not from a file mode: a `chmod 000` file is still readable to
#: root, so a permission-keyed plant would silently become a control there.
NOT_UTF8 = b"law \xff\xfe not utf-8\n"


def _prove_rows():
    """`tools/prove-rows.py` as a module — its filename is not an identifier."""
    path = REPO / "tools" / "prove-rows.py"
    spec = importlib.util.spec_from_file_location("prove_rows_lane_d4", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _cnv_lines(output: str) -> list:
    return [ln for ln in output.splitlines()
            if ln.lstrip().startswith("COULD NOT VERIFY")]


def _row(ident: str):
    found = [r for r in refusals.ROWS if r.ident == ident]
    return found[0] if len(found) == 1 else None


def _arrangement(ident: str):
    """`(file, hits)` for the recorded arrangement of `ident`, or None.

    `hits` is the prover's OWN anchor test over the file at HEAD-in-tree, so
    an arrangement whose anchor the source no longer carries reads here the
    way the prover would read it: not one whole-line run.
    """
    pr = _prove_rows()
    found = [m for m in pr.MUTATIONS if m[0] == ident]
    if len(found) != 1:
        return None
    _ident, fname, anchor, _replacement, _what = found[0]
    text = (CORE / fname).read_text(encoding="utf-8")
    return fname, len(pr.anchor_hits(text, anchor))


# --- 1. one conservation line ------------------------------------------------

class ConservationCouldNotVerifyIsOneLine(unittest.TestCase):
    """The uncomputable identity printed TWO could-not-verify lines: a name
    with no reason, then a reason with no name. One line carries both.
    """

    def _run(self):
        return refusals._cli(
            ["item", "check"],
            items=refusals.SEED_ITEMS.replace("baseline: 1\n", "", 1))

    def test_one_line_carrying_the_name_and_the_reason(self):
        fired = self._run()
        about = [ln for ln in _cnv_lines(fired.output)
                 if "conservation" in ln]
        self.assertEqual(len(about), 1, fired.output)
        self.assertTrue(
            about[0].startswith("COULD NOT VERIFY [conservation_unverified] "),
            about[0])
        # THE REASON, in the same line: the head key the identity lacked.
        self.assertIn("`baseline`", about[0])

    def test_the_exit_code_did_not_move(self):
        self.assertEqual(self._run().code, exits.COULD_NOT_VERIFY)

    def test_a_computable_identity_prints_no_such_line(self):
        """CONTROL: the same carrier with its baseline in place."""
        fired = refusals._cli(["item", "check"], items=refusals.SEED_ITEMS)
        self.assertNotIn("[conservation_unverified]", fired.output)

    def test_the_arrangement_still_finds_its_anchor(self):
        """The row's recorded mutation quotes the emitting line, so rewording
        the line retires the proof unless the anchor moves with it."""
        self.assertEqual(_arrangement("conservation_unverified"),
                         ("items.py", 1))


# --- 2. the laws row, in the bracket form, and its unreadable sibling --------

class TheLawsRowsAreNamedInTheBracketForm(unittest.TestCase):
    """`kind check` printed the laws row's name INSIDE the message, after the
    colon, which is not the form the emit-site scan reads; the unreadable-file
    branch beside it printed no name at all.
    """

    def _kind_check(self, laws: bytes | None):
        with refusals._Repo() as repo:
            path = repo.dir / "LAWS.md"
            if laws is None:
                path.unlink()
            else:
                path.write_bytes(laws)
            return refusals._cli_in(repo, ["kind", "check"])

    def _unverified(self, laws: bytes | None) -> list:
        with refusals._Repo() as repo:
            path = repo.dir / "LAWS.md"
            if laws is None:
                path.unlink()
            else:
                path.write_bytes(laws)
            return [str(u) for u in decl.read(repo.dir).unverified]

    def test_the_absent_laws_file_is_named_in_the_bracket_form(self):
        fired = self._kind_check(None)
        lines = [ln for ln in _cnv_lines(fired.output) if "laws file" in ln]
        self.assertEqual(len(lines), 1, fired.output)
        self.assertTrue(lines[0].startswith(
            "COULD NOT VERIFY [laws_absent_could_not_verify] the declared "
            "laws file"), lines[0])
        self.assertEqual(fired.code, exits.COULD_NOT_VERIFY)

    def test_the_unreadable_laws_file_is_named_too(self):
        fired = self._kind_check(NOT_UTF8)
        lines = [ln for ln in _cnv_lines(fired.output) if "laws file" in ln]
        self.assertEqual(len(lines), 1, fired.output)
        self.assertTrue(lines[0].startswith(
            "COULD NOT VERIFY [laws_unreadable_could_not_verify] the "
            "declared laws file"), lines[0])
        # MUST-NOT-MOVE: it answered could-not-verify before it had a name.
        self.assertEqual(fired.code, exits.COULD_NOT_VERIFY)

    def test_a_readable_laws_file_prints_neither_name(self):
        """CONTROL: a name printed on every path names nothing."""
        fired = self._kind_check(b"law\n")
        self.assertEqual(fired.code, exits.CLEAN, fired.output)
        self.assertNotIn("[laws_absent_could_not_verify]", fired.output)
        self.assertNotIn("[laws_unreadable_could_not_verify]", fired.output)

    def test_the_emit_site_scan_reads_both_names_from_the_source(self):
        sites = roster.emit_sites()
        for ident in ("laws_absent_could_not_verify",
                      "laws_unreadable_could_not_verify"):
            with self.subTest(row=ident):
                self.assertTrue(
                    any(s.startswith("declaration.py:")
                        for s in sites.get(ident, ())), sites.get(ident))

    def test_what_the_other_renderers_are_handed_keeps_its_shape(self):
        """MUST-NOT-MOVE. `Result.unverified` is printed by renderers this
        change does not touch (the router, the workflow binder, migrate, the
        roster's own declaration scaffold), each as `COULD NOT VERIFY: <u>`.
        The absent-file reason they are handed is the string it was: the name
        in brackets, then the sentence — never a second verdict word.
        """
        absent = [u for u in self._unverified(None) if "laws file" in u]
        self.assertEqual(len(absent), 1, absent)
        self.assertTrue(absent[0].startswith(
            "[laws_absent_could_not_verify] the declared laws file"),
            absent[0])
        unreadable = [u for u in self._unverified(NOT_UTF8)
                      if "laws file" in u]
        self.assertEqual(len(unreadable), 1, unreadable)
        self.assertTrue(unreadable[0].startswith(
            "[laws_unreadable_could_not_verify] the declared laws file"),
            unreadable[0])

    def test_an_unnamed_reason_still_prints_with_the_colon(self):
        """CONTROL for `_report`: a could-not-verify reason carrying no row
        name is printed exactly as before — the bracket form is for a reason
        that HAS a name, never a guess from a reason's first characters.
        """
        from lifecycle_core import cli as cli_mod
        res = decl.Result(exits.CLEAN)
        res.cannot_verify("[not a row] a sentence that merely opens with a "
                          "bracket")
        lines = []
        cli_mod._report(res, lines.append)
        self.assertEqual(lines, ["COULD NOT VERIFY: [not a row] a sentence "
                                 "that merely opens with a bracket"])

    def test_the_unreadable_row_is_on_the_roster_with_its_arrangement(self):
        row = _row("laws_unreadable_could_not_verify")
        self.assertIsNotNone(row, "no roster row for the unreadable branch")
        fired, control = row.fire(), row.control()
        self.assertEqual(fired.code, exits.COULD_NOT_VERIFY, fired.output)
        self.assertIn("[laws_unreadable_could_not_verify]", fired.output)
        self.assertEqual(control.code, exits.CLEAN, control.output)
        self.assertEqual(_arrangement("laws_unreadable_could_not_verify"),
                         ("declaration.py", 1))

    def test_the_absent_rows_arrangement_still_finds_its_anchor(self):
        self.assertEqual(_arrangement("laws_absent_could_not_verify"),
                         ("declaration.py", 1))


# --- 3. the init site of the unsafe lane name --------------------------------

class TheInitUnsafeLaneSiteHasItsOwnRow(unittest.TestCase):
    """`init --lane <unsafe>` is refused under the finding `lane new` gives
    the same word, at a SECOND site in another module. The roster proved the
    `lane new` site alone, so deleting the init test left every row green.
    """

    IDENT = "init_lane_unsafe_door"

    def test_a_roster_row_fires_the_init_site(self):
        row = _row(self.IDENT)
        self.assertIsNotNone(row, "no roster row drives the init site")
        # ONE refusal, two firing inputs: the row maps to the finding the
        # site already prints, never to a second name for the same refusal.
        self.assertEqual(row.expected_finding_row, "lane_new_unsafe_door")
        self.assertEqual(row.expect, exits.FINDING)
        fired, control = row.fire(), row.control()
        self.assertEqual(fired.code, exits.FINDING, fired.output)
        self.assertIn("FINDING [lane_new_unsafe_door]", fired.output)
        # THE INIT SITE, not `lane new`'s: only init says what it left
        # unwritten.
        self.assertIn("Nothing was written", fired.output)
        self.assertNotEqual(control.code, exits.FINDING, control.output)
        self.assertNotIn("[lane_new_unsafe_door]", control.output)

    def test_the_row_has_a_recorded_arrangement_in_init(self):
        self.assertEqual(_arrangement(self.IDENT), ("init.py", 1))


# --- 4. the existing-declaration refusal -------------------------------------

class InitOverAnExistingDeclarationIsNamed(unittest.TestCase):
    """`init` refusing to overwrite a declaration exited FINDING under no row
    name, so nothing on the roster could be asked whether it still refuses.
    """

    IDENT = "init_declaration_exists"

    def test_the_refusal_prints_its_row_name(self):
        fired = refusals._cli(["init"])
        self.assertIn(f"FINDING [{self.IDENT}]", fired.output)
        # MUST-NOT-MOVE: it was a finding before it had a name.
        self.assertEqual(fired.code, exits.FINDING)

    def test_force_is_not_refused_and_prints_no_name(self):
        """CONTROL: the same repo, the flag the only difference."""
        fired = refusals._cli(["init", "--force"])
        self.assertNotIn(f"[{self.IDENT}]", fired.output)
        self.assertNotEqual(fired.code, exits.FINDING, fired.output)

    def test_the_row_is_on_the_roster_with_its_arrangement(self):
        row = _row(self.IDENT)
        self.assertIsNotNone(row, "the name is printed under no roster row")
        self.assertEqual(row.expect, exits.FINDING)
        self.assertEqual(_arrangement(self.IDENT), ("init.py", 1))


if __name__ == "__main__":
    unittest.main()
