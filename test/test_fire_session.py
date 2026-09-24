"""Every fire line carries the session that wrote it (refocus round R2).

WHY: the O6 surfaced-vs-read counter could not attribute a single record to a
session. `fire()` wrote at/verb/repo/outcome/detail and nothing else, so a
repo-plus-time-window join was the only route, and two instruments reading
the same window disagreed (114 vs 129 surfacings) with no way to settle it
(docs/directives/2026-09-24-refocus-design-round.md §0.2, judge ruling 1).

THE ABSENT CASE IS WRITTEN, NEVER OMITTED: a line with no `session` key and
a line from a session-less caller would otherwise read the same, and a reader
counting per session would fold the second into nothing.
"""

import _isolation  # noqa: F401  # lc-183: before any verb runs

import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugin" / "cli"))

from lifecycle_core import firelog  # noqa: E402


def _last_line():
    lines = firelog.log_path().read_text(encoding="utf-8").splitlines()
    return json.loads(lines[-1])


class FireLineCarriesSession(unittest.TestCase):
    def setUp(self):
        self._saved = os.environ.get(firelog.SESSION_ENV)

    def tearDown(self):
        if self._saved is None:
            os.environ.pop(firelog.SESSION_ENV, None)
        else:
            os.environ[firelog.SESSION_ENV] = self._saved

    def test_set_env_is_recorded(self):
        os.environ[firelog.SESSION_ENV] = "sess-r2-plant"
        self.assertTrue(firelog.fire("r2 probe", repo="/tmp/r2"))
        self.assertEqual(_last_line().get("session"), "sess-r2-plant")

    def test_unset_env_writes_absent_never_omits(self):
        os.environ.pop(firelog.SESSION_ENV, None)
        self.assertTrue(firelog.fire("r2 probe", repo="/tmp/r2"))
        self.assertEqual(_last_line().get("session"), "absent")

    def test_blank_env_is_absent(self):
        os.environ[firelog.SESSION_ENV] = "   "
        self.assertTrue(firelog.fire("r2 probe", repo="/tmp/r2"))
        self.assertEqual(_last_line().get("session"), "absent")


if __name__ == "__main__":
    unittest.main()
