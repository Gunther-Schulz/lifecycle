"""Drain wave E, lane E9: lc-23 (init seeds the carriers), lc-225 (the
round series), lc-41 (commit-or-say), lc-194 (a shell answers for the last
process only)."""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "plugin" / "cli"))

from lifecycle_core import cli, exits  # noqa: E402
from lifecycle_core import declaration as decl  # noqa: E402

from test_init import ScratchGitRepo  # noqa: E402


def _run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(argv)
    return code, buf.getvalue()


class Lc23InitSeedsCarriers(unittest.TestCase):
    """lc-23: a greenfield repo after init has the three carriers resolvable
    and `kind check` answers CLEAN rather than COULD NOT VERIFY on them."""

    def _bare(self):
        r = ScratchGitRepo()
        r.write("CLAUDE.md", "# laws\n")
        r.commit_as("op@example.invalid")
        self.addCleanup(r.close)
        return r

    def test_bare_repo_after_init_has_clean_kind_check(self):
        r = self._bare()
        code, out = _run(["--repo", str(r.dir), "init"])
        self.assertEqual(code, exits.CLEAN, out)
        for name in ("ITEMS.md", "ITEMS-DONE.md", "LEDGER.md"):
            self.assertTrue((r.dir / name).is_file(), name)
            self.assertIn(f"seeded {name}", out)
        code2, out2 = _run(["--repo", str(r.dir), "kind", "check"])
        self.assertEqual(code2, exits.CLEAN, out2)
        self.assertNotIn("is not present", out2)

    def test_present_carrier_is_left_untouched(self):
        r = self._bare()
        r.write("LEDGER.md", f"schema: {decl.SCHEMA_FLOOR}\n\nkept line\n")
        before = (r.dir / "LEDGER.md").read_text()
        code, out = _run(["--repo", str(r.dir), "init"])
        self.assertEqual((r.dir / "LEDGER.md").read_text(), before)
        self.assertIn("LEDGER.md already present", out)
        self.assertTrue((r.dir / "ITEMS.md").is_file())


if __name__ == "__main__":
    unittest.main()
