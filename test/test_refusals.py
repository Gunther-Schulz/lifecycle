"""Every refusal row in this build: the plant fires, the control does not.

THE PAIR IS THE PROOF. A row asserting only that its plant produced a
non-zero exit separates "something happened" from "nothing happened", when
the question is WHICH outcome happened — so could-not-verify would pass as
verified-wrong. Each row therefore asserts two things: the plant equals the
code the row NAMES, and the control DIFFERS from it. The second half is what
catches a plant that missed its target and left the check reading a file
that was already broken.

The rows are not restated here. They are imported from
`lifecycle_core.refusals`, which is also what `--test` (stage 8) will print.
One source, two consumers.
"""

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "plugin" / "cli"))

from lifecycle_core import exits, refusals, roster  # noqa: E402


def _prove_rows():
    """`tools/prove-rows.py` as a module — its filename is not an identifier.

    The REAL object, never a re-parse of its text: the anchors these arms
    grade are the ones the tool itself would use, and a second reading of the
    same file is a second body that can agree with the source while the tool
    disagrees with both.
    """
    path = REPO / "tools" / "prove-rows.py"
    spec = importlib.util.spec_from_file_location("prove_rows", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class RefusalRows(unittest.TestCase):

    def test_every_row_fires_and_its_control_does_not(self):
        self.assertTrue(refusals.ROWS, "the roster is empty")
        for row in refusals.ROWS:
            with self.subTest(row=row.ident):
                fired = row.fire()
                control = row.control()
                self.assertEqual(
                    fired.code, row.expect,
                    f"[{row.ident}] firing input {row.firing_input!r} exited "
                    f"{exits.word(fired.code)}, expected "
                    f"{exits.word(row.expect)}.\n{fired.output}")
                self.assertNotEqual(
                    control.code, row.expect,
                    f"[{row.ident}] the CONTROL also exited "
                    f"{exits.word(row.expect)} — the input under test is not "
                    f"what produced it.\n{control.output}")

    def test_a_findings_row_names_itself_in_its_output(self):
        """A finding and the roster entry proving it carry ONE name.

        Without this, a row can 'pass' on a finding raised by something else
        entirely — the plant broke the file in two ways and the check saw the
        wrong one.
        """
        for row in refusals.ROWS:
            if row.expect != exits.FINDING:
                continue
            with self.subTest(row=row.ident):
                fired = row.fire()
                self.assertIn(f"[{row.expected_finding_row}]", fired.output,
                              f"[{row.ident}] fired, but nothing in its "
                              f"output names that row:\n{fired.output}")

    def test_control_is_clean_where_the_row_is_about_a_valid_input(self):
        """The BASELINE, stated rather than assumed.

        Over an already-red baseline a plant-and-check proof is
        indistinguishable from a check that is simply always red.
        """
        good = refusals._decl_run(**refusals._GOOD_KW)
        self.assertEqual(good.code, exits.CLEAN,
                         f"the control declaration is not clean:\n{good.output}")

    def test_row_idents_are_unique(self):
        """Two rows under one ident are one row in every report.

        Found by hand while stages 4-6 added a CROSS-HOME duplicate row
        beside stage 3's within-file one: both were called `duplicate_id`,
        and `--test`'s roster, a failure message and this suite's own
        subTest label would each have named one of them without saying
        which. The hand-derivation is the prototype; this is the mechanism.
        """
        seen = {}
        for row in refusals.ROWS:
            seen.setdefault(row.ident, []).append(row.firing_input)
        clashes = {k: v for k, v in seen.items() if len(v) > 1}
        self.assertEqual(clashes, {},
                         "row idents must be unique; use `finding_row` where "
                         "two roster rows prove one refusal")

    def test_prose_rest_rows_are_labelled_not_dropped(self):
        self.assertTrue(refusals.PROSE_REST)
        for name, why in refusals.PROSE_REST:
            with self.subTest(row=name):
                self.assertTrue(why.strip(),
                                f"prose-rest row {name!r} carries no reason")


class ProofArrangementsPointAtOnePlace(unittest.TestCase):
    """The recorded mutation anchors in `tools/prove-rows.py`.

    A row's proof is only as good as the anchor that finds the place to
    disable. An anchor that matches somewhere it was never meant to retires
    that row's proof — silently, because the tool then honestly reports COULD
    NOT VERIFY and a reader takes it for a stale arrangement rather than for
    an unrelated verb's collision.
    """

    @staticmethod
    def _whole_line_hits(text: str, anchor: str) -> list:
        """Line numbers where `anchor` occupies COMPLETE lines of `text`.

        WRITTEN HERE RATHER THAN IMPORTED, deliberately. Grading the anchor
        table with the tool's own matcher would move the expectation with the
        mutant: a matcher loosened back to substring would still find today's
        anchors unique, and this arm would stay green over exactly the change
        it exists to catch. The definition is the parent, so it is spelled
        from the definition.
        """
        out, i = [], text.find(anchor)
        while i != -1:
            end = i + len(anchor)
            if (i == 0 or text[i - 1] == "\n") and \
                    (end == len(text) or text[end] == "\n"):
                out.append(text.count("\n", 0, i) + 1)
            i = text.find(anchor, i + 1)
        return out

    def test_every_recorded_anchor_is_a_whole_line_run(self):
        """No anchor may begin or end in the middle of a line.

        A mid-line START is the measured defect: `    if r.returncode != 0:`
        is a substring of the same line at any deeper indent, so an unrelated
        verb spelling a git check the ordinary way retires another row's
        proof. A mid-line END is the mirror — a prefix match in an equality's
        costume, satisfied by any longer line that begins the same way.
        """
        mod = _prove_rows()
        core = REPO / "plugin" / "cli" / "lifecycle_core"
        self.assertTrue(mod.MUTATIONS, "no mutation arrangements are recorded")
        for ident, fname, anchor, _replacement, _what in mod.MUTATIONS:
            with self.subTest(row=ident):
                text = (core / fname).read_text(encoding="utf-8")
                hits = self._whole_line_hits(text, anchor)
                self.assertEqual(
                    len(hits), 1,
                    f"[{ident}] its anchor occupies complete lines at "
                    f"{len(hits)} place(s) in {fname}, not one. Raw substring "
                    f"occurrences: {text.count(anchor)}. An anchor that is "
                    "not a whole-line run either matches nothing (the run "
                    "goes COULD NOT VERIFY and the row is unproven) or "
                    "matches a longer line it was never aimed at.")

    def test_the_matcher_rejects_the_same_line_at_a_deeper_indent(self):
        """`anchor_hits` itself, on a fixture carrying the measured defect.

        The arm above grades the TABLE and would stay green on a table that
        happens to be unique under either matcher; this one grades the
        MATCHER, so the two do not share a blind spot.
        """
        mod = _prove_rows()
        anchor = "    if r.returncode != 0:"
        deeper = "        if r.returncode != 0:"
        text = (f"def a():\n{anchor}\n        pass\n"
                f"def b():\n    if x:\n{deeper}\n            pass\n")
        self.assertEqual(text.count(anchor), 2,
                         "the fixture must carry the collision by substring, "
                         "or this arm cannot see the property it certifies")
        self.assertEqual(
            len(mod.anchor_hits(text, anchor)), 1,
            "the deeper-indented copy was counted: the matcher is still "
            "reading substrings, so an unrelated verb can retire a row's "
            "proof by spelling one line the ordinary way")

    def test_the_matcher_rejects_a_line_that_merely_begins_the_same_way(self):
        """The far end: an anchor is not a PREFIX of a longer line."""
        mod = _prove_rows()
        anchor = "    if kind == \"evidence\":"
        text = f"def a():\n{anchor}  # and more\n        pass\n"
        self.assertEqual(text.count(anchor), 1,
                         "the fixture must carry the prefix collision, or "
                         "this arm cannot see the property it certifies")
        self.assertEqual(
            len(mod.anchor_hits(text, anchor)), 0,
            "a line that merely BEGINS with the anchor was accepted — a "
            "prefix match standing in for an equality")


class TheRouteComparisonFailsInBothDirections(unittest.TestCase):
    """lc-30: the stray direction is a FINDING, never a note beside a CLEAN.

    A SECOND INSTRUMENT beside the roster row. `route_set_unnamed`'s own
    plant runs the whole check over a COPY of the package with one real row
    narrowed, which is the altitude the check ships at; these arms drive
    `check_routes` directly over a CONSTRUCTED row, so the two do not share
    the copy machinery as a blind spot — a copy that failed to mutate
    returns a green from the row and would leave these arms untouched.

    THE MUST-NOT-MOVE ARMS ARE HERE TOO, and they are the half a
    fires-on-everything change would pass without them: a row whose text and
    watched set AGREE must stay silent, and the mirror direction must still
    fire under its OWN name. Without those, a check that simply returned
    FINDING would score identically to this one.
    """

    @staticmethod
    def _routes(route_set, watched):
        """`check_routes` over ONE synthetic row, and nothing else.

        The roster is SWAPPED rather than appended to: the arms assert on the
        row's own entry, and an assertion over a report that also holds the
        86 real rows would pass on any report containing the grade anywhere.
        """
        row = refusals.Row(
            ident="synthetic_probe",
            refusal="a constructed row — this arm grades the COMPARISON, "
                    "never a real refusal",
            firing_input="not fired here",
            expect=exits.FINDING,
            fire=lambda: None,
            control=lambda: None,
            route_set=tuple(route_set),
            routes_watched=lambda: set(watched),
        )
        buf = []
        with mock.patch.object(refusals, "ROWS", [row]):
            code = roster.check_routes(buf.append)
        out = "\n".join(buf)
        assert out.count("    synthetic_probe\n") == 1, (
            "the arrangement did not reach the row's entry exactly once, so "
            "no assertion below can say which row it graded:\n" + out)
        return code, out

    def test_a_route_the_code_watches_and_the_text_omits_is_a_finding(self):
        code, out = self._routes(("a", "b"), {"a", "b", "c"})
        self.assertEqual(
            code, exits.FINDING,
            "the code watches `c` and the refusal's text does not name it — "
            "the refusal catches more than it says and this contributed "
            f"CLEAN until lc-30:\n{out}")
        self.assertIn("FINDING [route_set_unnamed]", out)
        self.assertIn("c", out)

    def test_that_finding_does_not_also_print_the_clean_verdict(self):
        """The negative half: a verdict line contradicting the finding above
        it is what a reader who stops at the verdict takes away."""
        _code, out = self._routes(("a", "b"), {"a", "b", "c"})
        self.assertNotIn(
            "routes: CLEAN", out,
            "the row emitted its finding AND printed the clean verdict — the "
            f"`else` on `missing` is back:\n{out}")

    def test_the_mirror_direction_still_fires_under_its_own_name(self):
        """MUST NOT MOVE: `route_set_unwatched` is untouched by lc-30."""
        code, out = self._routes(("a", "b", "c"), {"a", "b"})
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [route_set_unwatched]", out)
        self.assertNotIn(
            "FINDING [route_set_unnamed]", out,
            "a route named by the text and watched by nothing was reported "
            f"as the MIRROR defect — the two repairs are opposite:\n{out}")

    def test_a_row_whose_text_and_code_agree_stays_silent(self):
        """MUST NOT MOVE, and the arm that separates this change from one
        that merely denies more: agreement is CLEAN in both directions."""
        code, out = self._routes(("a", "b"), {"a", "b"})
        self.assertEqual(code, exits.CLEAN, out)
        self.assertNotIn("FINDING [route_set_unnamed]", out)
        self.assertNotIn("FINDING [route_set_unwatched]", out)
        self.assertIn("routes: CLEAN", out)

    def test_both_directions_at_once_name_both_rows(self):
        """Disagreement in both directions is two findings, not one: the
        repairs differ, so an operator told only "these disagree" cannot
        tell which is owed."""
        code, out = self._routes(("a", "x"), {"a", "y"})
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("FINDING [route_set_unnamed]", out)
        self.assertIn("FINDING [route_set_unwatched]", out)
        self.assertNotIn("routes: CLEAN", out)


if __name__ == "__main__":
    unittest.main()
