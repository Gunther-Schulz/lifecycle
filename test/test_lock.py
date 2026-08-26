"""The carrier file lock: it SERIALIZES, and the unlocked arm proves it.

WHY BOTH ARMS RUN EVERY TIME. A lock test that only exercises the locked path
passes whether the lock works or is a no-op — the two are indistinguishable
from a green. The discriminating shape is a PAIR: the same interleaved
read-modify-write, once with the lock and once without, and the two must
DIFFER. Carrying the unlocked arm in the test rather than reaching it by
editing the module also means the red cannot rot: it is re-run on every
suite, not reconstructed from a memory of how it was once produced.

WHAT IS ACTUALLY BEING SHOWN. Each child reads a counter, waits, then writes
counter+1. That wait is the whole collision: without serialization every
child reads the same value and the last writer wins, so N children produce 1.
With the lock they queue and produce N. "Subagents never book" is a
CONVENTION and conventions do not serialize anything; this does.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI = Path(__file__).resolve().parents[1] / "plugin" / "cli"
sys.path.insert(0, str(CLI))

CHILD = r"""
import sys, time
sys.path.insert(0, {cli!r})
from contextlib import nullcontext
from lifecycle_core.items import carrier_lock

target = sys.argv[1]
use_lock = sys.argv[2] == "locked"
ctx = carrier_lock(target) if use_lock else nullcontext()
with ctx:
    n = int(open(target).read().strip())
    time.sleep(0.25)              # the collision window, made wide on purpose
    open(target, "w").write(str(n + 1))
"""

WRITERS = 4


def _race(mode: str) -> int:
    with tempfile.TemporaryDirectory(prefix="lifecycle-lock-") as td:
        target = Path(td) / "ITEMS.md"
        target.write_text("0")
        src = CHILD.format(cli=str(CLI))
        procs = [subprocess.Popen([sys.executable, "-c", src, str(target), mode])
                 for _ in range(WRITERS)]
        for p in procs:
            p.wait(timeout=60)
        return int(target.read_text().strip())


class CarrierLock(unittest.TestCase):

    def test_the_lock_serializes_and_its_absence_does_not(self):
        unlocked = _race("unlocked")
        locked = _race("locked")
        # The red half, run first and asserted: without the lock the writes
        # are lost. If this ever stops being true the pair below has stopped
        # discriminating, and the test says so here rather than passing.
        self.assertLess(
            unlocked, WRITERS,
            f"the UNLOCKED arm kept all {WRITERS} writes ({unlocked}), so "
            "this race no longer collides and the locked arm's success "
            "proves nothing about the lock.")
        self.assertEqual(
            locked, WRITERS,
            f"the LOCKED arm lost writes: {locked} of {WRITERS} survived.")
        self.assertNotEqual(locked, unlocked)


if __name__ == "__main__":
    unittest.main()
