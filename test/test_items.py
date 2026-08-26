"""The carrier parser and shape check, beyond what the refusal rows cover.

The rows in `refusals.py` prove each REFUSAL fires. These cover the parser's
other obligations — the ones whose failure is silent rather than loud: an
archive section that must NOT be shape-checked, an absent file that must not
read as an empty one, and the census's refusal to guess.
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import exits, items  # noqa: E402
from lifecycle_core.refusals import GOOD_ITEMS  # noqa: E402


def run_check(text=None, prefix="xx"):
    with tempfile.TemporaryDirectory(prefix="lifecycle-items-") as td:
        p = Path(td) / "ITEMS.md"
        if text is not None:
            p.write_text(text, encoding="utf-8")
        buf = []
        code = items.check_file(p, buf.append, prefix=prefix)
        return code, "\n".join(buf)


class Archive(unittest.TestCase):

    #: A body of exactly the kind the pre-migration archive holds: a `##`
    #: heading that is not an id, no fixed slots, hand-written prose. The two
    #: tests below feed it the SAME bytes and differ in one thing only —
    #: whether the archive heading precedes it.
    BODY = ("- **READY 2026-01-01 — an old hand-written body.**\n"
            "## not-an-id-at-all\n"
            "grade: READY\n"
            "prose: whatever\n")

    def test_archive_bodies_are_held_verbatim_and_not_shape_checked(self):
        """The pre-migration archive is prose from before the tool existed.

        Shape-checking it would report hundreds of findings about text that
        was never meant to satisfy a fixed-slot shape, and a checker that
        fires on legitimate content trains the override reflex that kills it.
        """
        code, out = run_check(
            GOOD_ITEMS + "\n" + items.ARCHIVE_HEADING + "\n\n" + self.BODY)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("archive:", out)

    def test_the_same_bytes_ABOVE_the_archive_heading_do_fire(self):
        """The control for the test above: it is the HEADING that exempts.

        Without this pair, 'the archive is skipped' is indistinguishable from
        'the shape check does not work' — both produce a green.
        """
        code, out = run_check(GOOD_ITEMS + "\n" + self.BODY)
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("not-an-id-at-all", out)


class ThirdAnswer(unittest.TestCase):

    def test_an_absent_carrier_is_could_not_verify_not_clean(self):
        code, out = run_check(None)
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("COULD NOT VERIFY", out)

    def test_an_unknown_grade_word_is_counted_apart_never_folded(self):
        code, out = run_check(GOOD_ITEMS.replace("grade: READY", "grade: FOO"))
        self.assertEqual(code, exits.COULD_NOT_VERIFY, out)
        self.assertIn("open 0", out)
        self.assertIn("unknown 1", out)

    def test_a_known_grade_word_is_not_counted_as_unknown(self):
        code, out = run_check(GOOD_ITEMS)
        self.assertEqual(code, exits.CLEAN, out)
        self.assertIn("open 1", out)
        self.assertIn("unknown 0", out)


class Shape(unittest.TestCase):

    def test_slots_out_of_order_are_a_finding(self):
        lines = GOOD_ITEMS.split("\n")
        i = lines.index("goal: mitigate")
        j = lines.index("evidence: none yet")
        lines[i], lines[j] = lines[j], lines[i]
        code, out = run_check("\n".join(lines))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("out of order", out)

    def test_an_id_off_the_declared_prefix_is_a_finding(self):
        code, out = run_check(GOOD_ITEMS.replace("## xx-1", "## zz-1"))
        self.assertEqual(code, exits.FINDING, out)
        self.assertIn("declared prefix", out)

    def test_the_prefix_comes_from_the_declaration_not_from_the_file(self):
        """Inferring the prefix from the ids present would make any
        consistent corruption look correct — the same-parentage defect."""
        code, _ = run_check(GOOD_ITEMS.replace("## xx-1", "## zz-1"),
                            prefix="zz")
        self.assertEqual(code, exits.CLEAN)

    def test_a_wrapped_slot_value_is_a_shape_break(self):
        code, out = run_check(
            GOOD_ITEMS.replace("evidence: none yet",
                               "evidence: a value that\n  wrapped onto a second line"))
        self.assertEqual(code, exits.FINDING, out)


if __name__ == "__main__":
    unittest.main()
