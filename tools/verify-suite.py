#!/usr/bin/env python3
"""Run the unit suite and say what it did NOT run (lc-198).

`unittest discover` exits 0 when an arm skips, and this repo's Verify section
reads exit codes, so a reach arm that vanishes (its input absent: a fresh
clone, another machine, a CI runner) leaves a green. This runner reads the
RESULT OBJECT, never the -v rendering (law 17): `res.testsRun`,
`res.failures`, `res.errors`, `res.skipped` with each test's `id()`.

THE THREE ANSWERS (law 1; codes from `lifecycle_core.exits`, the one home):
  0  clean         — tests ran, none failed, no reach arm skipped
  2  finding       — at least one failure or error
  3  could not verify — a REACH ARM skipped (a skip whose reason starts with
                    `REACH ARM:`), or nothing ran at all. Outranks a finding,
                    by `exits.worst`: the list of failures is not the whole
                    list when a reach arm did not run.

An ordinary skip is REPORTED with its count and reason and does not change
the code: an arm that legitimately cannot run somewhere may still skip. The
only skip that withdraws the clean is the one whose own reason declares it
a reach arm.

USAGE: python3 tools/verify-suite.py [--start-dir test] [--pattern 'test_*.py']
Reads only; writes no tracked file.
"""

import argparse
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "plugin" / "cli"))

from lifecycle_core import exits  # noqa: E402

REACH_MARK = "REACH ARM:"


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--start-dir", default=str(REPO / "test"))
    ap.add_argument("--pattern", default="test_*.py")
    args = ap.parse_args(argv)

    suite = unittest.defaultTestLoader.discover(
        args.start_dir, pattern=args.pattern)
    res = unittest.TextTestRunner(stream=sys.stderr, verbosity=0).run(suite)

    skipped = [(t.id(), reason) for t, reason in res.skipped]
    reach = [(i, r) for i, r in skipped if r.startswith(REACH_MARK)]
    print(f"ran: {res.testsRun}  failures: {len(res.failures)}  "
          f"errors: {len(res.errors)}  skipped: {len(skipped)}  "
          f"reach-arm skips: {len(reach)}")
    for ident, reason in skipped:
        kind = "REACH ARM" if (ident, reason) in reach else "skip"
        print(f"    {kind}: {ident} -- {reason}")

    codes = [exits.CLEAN]
    if res.failures or res.errors:
        codes.append(exits.FINDING)
    if reach or res.testsRun == 0:
        codes.append(exits.COULD_NOT_VERIFY)
    code = exits.worst(codes)
    if res.testsRun == 0:
        print("COULD NOT VERIFY: the run examined no test at all.")
    elif reach:
        print(f"COULD NOT VERIFY: {len(reach)} reach arm(s) did not run, so "
              "the suite's pass covers less than its reach.")
    print(exits.word(code))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
