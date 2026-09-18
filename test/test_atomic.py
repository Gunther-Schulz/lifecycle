"""The atomic carrier write (lc-159), and the guard that keeps it the ONLY path.

WHY THIS FILE EXISTS. Every carrier write was `Path.write_text` — truncate,
then write — so an interrupt between the two left the carrier SHORT. The
damage is not the loss but its SHAPE: the parse keys on the head `schema:`
line, so a truncated carrier returns refused=False with fewer items and NO
problems, and every downstream consumer reads a confident, clean, WRONG
answer over a smaller carrier. Measured before the fix, on this repo's own
223483-byte, 71-item ITEMS.md: cut to 400 bytes -> 1 item, 0 problems; to
2000 -> 2 items, 0 problems; to 20000 -> 8 items, 0 problems.

THE SECOND ARM IS THE ONE THAT LASTS. Proving the helper atomic says nothing
about whether the 16 call sites USE it, and a single re-introduced
`Path.write_text` on a carrier restores the whole defect silently. So the
source-derived arm asserts what must NOT appear — the cheap instrument that
catches a check DEGRADING rather than only breaking.
"""

import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import atomic  # noqa: E402

CORE = Path(__file__).resolve().parents[1] / "plugin" / "cli" / "lifecycle_core"

#: The carrier paths. A write to any of these must be atomic; everything else
#: in the package (a declaration, a lane stub, a report) is out of lc-159's
#: scope and is NOT asserted here — naming them would make this arm fire on
#: legitimate work, which is how a guard trains the override reflex.
CARRIER_ATTRS = ("items_path", "done_path", "ledger_path")


class TheHelperIsAtomic(unittest.TestCase):

    def test_an_interrupted_write_leaves_the_TARGET_untouched(self):
        """The property, proven by interrupting a real write.

        RED-FIRST, and the baseline is stated rather than assumed: the second
        arm below runs the OLD idiom against the same interruption and shows
        the target truncated. Without it this arm would pass against any
        implementation that happened not to raise.
        """
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "ITEMS.md"
            original = "schema: 2\n\n## xx-1\nrequirement: the original body\n"
            target.write_text(original, encoding="utf-8")

            real_replace = os.replace

            def boom(src, dst):
                raise OSError("interrupt between the write and the replace")

            os.replace = boom
            try:
                with self.assertRaises(OSError):
                    atomic.write_text(target, "schema: 2\n\n## xx-1\nnew\n")
            finally:
                os.replace = real_replace

            self.assertEqual(
                target.read_text(encoding="utf-8"), original,
                "the target moved despite the write being interrupted — the "
                "whole point of the helper is that it does not")

            leftovers = [p.name for p in Path(td).iterdir()
                         if p.name != "ITEMS.md"]
            self.assertEqual(
                leftovers, [],
                f"the sibling temp survived the failure: {leftovers}. A "
                "reader that globs the carrier's directory would find it.")

    def test_the_OLD_idiom_under_the_SAME_interruption_truncates(self):
        """THE BASELINE. This is what the fix replaced, and it must differ.

        An arm asserting only that the new helper is safe cannot tell a real
        fix from a test that never exercised the failure. This runs the
        truncate-then-write idiom against an interruption at the same instant
        and shows the target SHORT — the two results must differ, or the
        comparison proves nothing about which one is correct.
        """
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "ITEMS.md"
            original = "schema: 2\n\n## xx-1\nrequirement: the original body\n"
            target.write_text(original, encoding="utf-8")

            with self.assertRaises(OSError):
                with open(target, "w", encoding="utf-8") as fh:
                    fh.write("schema: 2\n")          # the head survives ...
                    raise OSError("interrupt mid-write")

            after = target.read_text(encoding="utf-8")
            self.assertNotEqual(
                after, original,
                "the old idiom did NOT truncate, so this baseline proves "
                "nothing and the arm above is unearned")
            self.assertTrue(
                after.startswith("schema:"),
                "the truncated file still carries a valid head — which is "
                "exactly why the parse reads it as a smaller clean carrier "
                "rather than as damage")
            self.assertNotIn("## xx-1", after)

    def test_the_mode_a_repo_chose_survives_the_write(self):
        """`os.replace` carries the SOURCE's mode, which declaration.py's own
        comment records. Without the chmod the helper would silently reset a
        carrier's permissions to whatever the umask gives."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "ITEMS.md"
            target.write_text("schema: 2\n", encoding="utf-8")
            os.chmod(target, 0o640)
            atomic.write_text(target, "schema: 2\n\n## xx-1\nbody\n")
            self.assertEqual(target.stat().st_mode & 0o777, 0o640)


class TheHelperIsTheOnlyCarrierWritePath(unittest.TestCase):

    def test_no_carrier_is_written_with_Path_write_text(self):
        """ASSERTS AN ABSENCE, so it carries its own positive control.

        A pattern that could never match returns exactly what a true absence
        returns. The control below plants the forbidden shape in a string and
        requires the pattern to find it — without that, a typo in the regex
        would read as sixteen clean call sites forever.
        """
        pat = re.compile(
            r'\b(?:\w+\.)?(?:' + "|".join(CARRIER_ATTRS) + r')\.write_text\(')

        planted = 'ctx.items_path.write_text(new, encoding="utf-8")'
        self.assertTrue(
            pat.search(planted),
            "the pattern does not match the very shape it forbids — an "
            "unread instrument, not a clean result")

        offenders = []
        for py in sorted(CORE.glob("*.py")):
            if py.name == "atomic.py":
                continue
            for n, line in enumerate(py.read_text().splitlines(), 1):
                if pat.search(line):
                    offenders.append(f"{py.name}:{n}: {line.strip()}")

        self.assertEqual(
            offenders, [],
            "a carrier is written with Path.write_text, which truncates "
            "before it writes. An interrupt there leaves a SHORT carrier "
            "that parses CLEAN with fewer items:\n  " + "\n  ".join(offenders))

    def test_the_helper_is_actually_reached_by_the_call_sites(self):
        """The companion to the absence arm: absence of the bad shape is not
        presence of the good one. A file could have dropped its carrier write
        entirely and satisfy the arm above."""
        found = 0
        for py in sorted(CORE.glob("*.py")):
            if py.name == "atomic.py":
                continue
            found += len(re.findall(r'\batomic\.write_text\(', py.read_text()))
        self.assertGreaterEqual(
            found, 16,
            f"only {found} atomic carrier writes found; 16 sites were "
            "rewritten, so a lower number means sites were lost rather than "
            "converted")


if __name__ == "__main__":
    unittest.main()
