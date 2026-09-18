"""The suite's own isolation, imported by EVERY test module (lc-183).

THE FIRE LOG IS MACHINE-WIDE AND THE SUITE WAS WRITING TO THE REAL ONE.
`firelog.state_dir()` reads `XDG_STATE_HOME` and falls back to the running
user's `~/.local/state`, so every arm that drives a real verb appended a
record to the OPERATOR's log. Measured before this file did anything: one
`unittest discover` run over the suite added 869 records to a live
132MB/1.2M-line file, and 81.6% of that file's records carry a `/tmp` repo
path — scratch repos built by this suite and by `tools/prove-rows.py`.

IT IS THE PARTIAL-OVERRIDE CLASS, which is why two isolating files were not
enough and why the fix belongs HERE rather than in a third one. `test_desk`
and `test_declaration` each rebind `XDG_STATE_HOME` around their own arms —
correctly, for their own purposes — while every other arm ran against live
state. A fixture that isolates the destination while a sibling global stays
keyed to the real world aims the exercised path at real data OUTSIDE the
test, and the green is identical either way. The exercised path here is an
APPEND, which is one of the destructive members: nothing fails, the record
just grows.

THE ISOLATION SET IS CHECKED AGAINST WHAT THE EXERCISED PATH CONSUMES, never
against what a given arm happens to touch. The path under test consumes
exactly one global for this purpose — `XDG_STATE_HOME`, read at
`firelog.state_dir()` — so binding it once, before any test module is
imported, covers every arm including the ones nobody thought to isolate.

WHAT THIS DOES NOT DO: silence the instrument. The fire log still records
every real verb run; this moves the SUITE's records to a scratch directory
that is removed when the run ends. A fix that stopped the log recording would
trade a polluted register for no register at all.

THE ARMS THAT ALREADY ISOLATE KEEP DOING SO. They save and restore the
variable around their own fixtures, so they now restore to this run's scratch
value rather than to the machine's — which is the direction that widens the
isolation instead of relocating it.
"""

import atexit
import os
import shutil
import tempfile

#: IMPORTED BY EACH TEST MODULE RATHER THAN BY THE PACKAGE, and that is a
#: measurement rather than a preference. `test/__init__.py` looked like the
#: one load-bearing place, and it is DEAD under this repo's own declared
#: command: `unittest discover -s test` puts the directory on `sys.path` and
#: imports the modules TOP-LEVEL, so the package is never imported at all.
#: Probed both ways before choosing — `-s test` imported this zero times,
#: `-s .` once. A fix resting on the first form would have been a green that
#: changed nothing, which is the same shape as the defect it repairs.
#:
#: So the import is per-module and `TestEveryModuleIsolatesTheFireLog` derives
#: the list from the directory rather than restating it: a new test file that
#: forgets the line is a FINDING, not a silent hole. An
#: environment that already names a state home is LEFT ALONE: a caller who
#: set it (a sandbox, a harness, `tools/prove-rows.py`) has already answered
#: this question, and overriding them would be this file making the same
#: mistake one layer up.
if not os.environ.get("XDG_STATE_HOME"):
    _SUITE_STATE = tempfile.mkdtemp(prefix="lifecycle-suite-state-")
    os.environ["XDG_STATE_HOME"] = _SUITE_STATE
    atexit.register(shutil.rmtree, _SUITE_STATE, ignore_errors=True)
