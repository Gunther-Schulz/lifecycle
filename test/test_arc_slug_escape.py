"""An arc verb never writes through its slug (found by lc-317's sweep).

`arc open` tested the slug; the other arc verbs built `arcs/<slug>.md` from
the caller's word and asked only whether that path EXISTS. With a live arc in
place the `arcs/` directory exists, so `../README` resolved to a root file
and the verbs appended to it, moved it, or declared a lane from it.

THE FIXTURE HOLDS A LIVE ARC ON PURPOSE. Without one `arcs/` is absent, the
escaping path cannot resolve, and every verb answers `unknown_arc` for the
wrong reason — the arrangement in which this defect reads clean.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli as cli_mod  # noqa: E402
from lifecycle_core import exits, refusals  # noqa: E402

OPEN = ["arc", "open", "freeze", "--goal", "find the root cause",
        "--narrowing", "eliminative"]

VERBS = {
    "premise": ["--ident", "p1", "--text", "t"],
    "belief": ["--ident", "b1", "--claim", "t", "--basis", "seen",
               "--kill", "k"],
    "advance": ["--to", "s2", "--reason", "r"],
    "narrow": ["--text", "t"],
    "yield": ["--ident", "y1", "--text", "t", "--summary", "s"],
    "deadline": ["--date", "2030-01-01", "--what", "w"],
    "close": ["--abandon", "--reason", "r"],
}


class AnArcVerbNeverWritesThroughItsSlug(unittest.TestCase):

    def _repo(self):
        r = refusals._Repo()
        self.addCleanup(r.close)
        return r

    def _run(self, repo, *argv):
        here = os.getcwd()
        try:
            os.chdir(str(repo.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                try:
                    code = cli_mod.main(["--repo", str(repo.dir)] + list(argv))
                except SystemExit as exc:
                    code = exc.code
        finally:
            os.chdir(here)
        return code, buf.getvalue()

    def _tree(self, root):
        return {(str(p.relative_to(root)), p.read_bytes())
                for p in root.rglob("*")
                if p.is_file() and ".git" not in p.relative_to(root).parts}

    def _seeded(self):
        repo = self._repo()
        code, outp = self._run(repo, *OPEN)
        self.assertEqual(code, exits.CLEAN, outp)
        victim = repo.dir / "README.md"
        victim.write_text("a root file no arc verb may touch\n",
                          encoding="utf-8")
        for argv in (("add", "-A"),
                     ("commit", "-qm", "seed a root file beside a live arc")):
            done = subprocess.run(["git", "-C", str(repo.dir), *argv],
                                  capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stderr)
        return repo

    def test_an_escaping_slug_is_refused_and_nothing_is_written(self):
        for verb, tail in VERBS.items():
            with self.subTest(verb=verb):
                repo = self._seeded()
                before = self._tree(repo.dir)
                code, outp = self._run(repo, "arc", verb, "../README", *tail)
                self.assertEqual(code, exits.FINDING, outp)
                self.assertIn("unknown_arc", outp)
                self.assertEqual(self._tree(repo.dir), before,
                                 f"arc {verb} changed the tree:\n{outp}")

    def test_the_live_arc_itself_still_takes_the_verb(self):
        """The control: a check refusing every slug passes the arm above."""
        repo = self._seeded()
        code, outp = self._run(repo, "arc", "premise", "freeze",
                               "--ident", "p1", "--text", "t")
        self.assertEqual(code, exits.CLEAN, outp)


if __name__ == "__main__":
    unittest.main()
