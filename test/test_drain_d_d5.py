"""Drain wave D, lane D5 — the flow ratio, and verdicts asked of a shell
(2026-10-07).

ONE FILE FOR THE LANE (wave B change 4): every red-first test this lane's
items asked for lives here.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugin" / "cli"))

from lifecycle_core import cli as cli_mod, exits, refusals  # noqa: E402
from lifecycle_core.refusals import _Repo, _backdate_head  # noqa: E402


def _ratio(added, closed_bodies, compacted):
    """`item ratio` over a dated git carrier whose head says `added` and
    `compacted` and whose done home holds `closed_bodies` bodies. The head is
    backdated past the window so the verb reaches its verdict instead of
    answering could-not-verify for want of history."""
    items, done = refusals._flow_carrier(added, closed_bodies)
    items = items.replace("compacted: 0", f"compacted: {compacted}")
    with _Repo(items=items, done=done) as r:
        _backdate_head(r.dir)
        here = os.getcwd()
        try:
            os.chdir(str(r.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(r.dir), "item", "ratio"])
        finally:
            os.chdir(here)
    return code, buf.getvalue()


class CompactedCountsAsDrain(unittest.TestCase):
    """lc-293: by conservation open + done = baseline + added - compacted, so
    the drain side of the lifetime ratio is done bodies PLUS the head's
    compacted counter."""

    def test_the_10_8_6_plant_reads_clean(self):
        # 10 added, 8 closed of which 6 were compacted out of the done home.
        code, out = _ratio(10, 2, 6)
        self.assertNotIn("[capture_dominated]", out)
        self.assertIn("ratio: 10:8 = 1.25:1", out)
        self.assertEqual(code, exits.CLEAN, out)

    def test_control_a_genuinely_capture_heavy_carrier_still_fires(self):
        # Same compacted counter, but only 2 drained in total: 10:2 is a
        # real finding and must stay one.
        code, out = _ratio(10, 0, 2)
        self.assertIn("[capture_dominated]", out)
        self.assertEqual(code, exits.FINDING, out)

    def test_control_no_compaction_reads_as_before(self):
        code, out = _ratio(10, 2, 0)
        self.assertIn("ratio: 10:2 = 5.00:1", out)
        self.assertEqual(code, exits.FINDING, out)


if __name__ == "__main__":
    unittest.main()
