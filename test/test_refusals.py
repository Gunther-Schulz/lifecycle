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

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits, refusals  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
