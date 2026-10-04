#!/usr/bin/env python3
"""Tally the fire log over a NAMED window, for the roster repos only.

Read-only. Written for the 2026-10-04 refocus design round, whose
predecessor withdrew its own figures because the probe that produced them
was never persisted (docs/directives/2026-09-24-refocus-design-round.md
section 0.2). This is that probe, kept.

What it counts, per window, over records whose `repo` is a roster entry:

  verb runs      every record except `item statusline` (a render tick, not
                 an act a session chose)
  sessions       distinct `session` values on those records
  surfacings     records whose detail carries `surfaced=`
  kind reads     records whose detail carries `read=`
  goal seams     records whose detail carries `goal-seam=`, per session

and, separately and never pooled, the records whose repo is NOT a roster
entry (test fixtures and scratch repos writing to the live log).

Three answers (law 1): exit 0 with the tally; exit 3 COULD NOT VERIFY when
the log or the roster cannot be read, or when the window holds no roster
record at all — an empty window is not a zero. Malformed lines are counted
and printed, never skipped silently.

    python3 tools/fire-window-tally.py --since 2026-09-25 [--until 2026-10-05]
"""
import argparse
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "plugin" / "cli"))

from lifecycle_core import firelog, lanes  # noqa: E402

TICK_VERBS = {"item statusline"}


def detail_values(detail: str, key: str) -> list:
    """Values of `key=` tokens in a `; `-separated fire detail."""
    out = []
    for part in detail.split(";"):
        part = part.strip()
        if part.startswith(key + "="):
            out.append(part[len(key) + 1:])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--since", required=True, help="inclusive, ISO date or datetime")
    ap.add_argument("--until", default="9999", help="exclusive, ISO date or datetime")
    args = ap.parse_args()

    roster_file = lanes.roster_path()
    try:
        roster = {ln.strip() for ln in roster_file.read_text(encoding="utf-8").splitlines()
                  if ln.strip() and not ln.lstrip().startswith("#")}
    except OSError as exc:
        print(f"COULD NOT VERIFY — the roster could not be read: {exc}")
        return 3
    log = firelog.log_path()
    try:
        fh = open(log, encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"COULD NOT VERIFY — the fire log could not be read: {exc}")
        return 3

    malformed = 0
    runs = collections.Counter()
    sessions = collections.defaultdict(set)
    verbs = collections.defaultdict(collections.Counter)
    surfaced = []
    reads = []
    seams = collections.defaultdict(collections.Counter)
    foreign = collections.Counter()
    oldest = None
    with fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                malformed += 1
                continue
            if not isinstance(rec, dict):
                malformed += 1
                continue
            at = str(rec.get("at", ""))
            if oldest is None or at < oldest:
                oldest = at
            if not (args.since <= at < args.until):
                continue
            verb = str(rec.get("verb", ""))
            if verb in TICK_VERBS:
                continue
            repo = str(rec.get("repo", ""))
            if repo not in roster:
                foreign[at[:10]] += 1
                continue
            name = Path(repo).name
            sess = str(rec.get("session", "absent"))[:8]
            detail = str(rec.get("detail", ""))
            runs[name] += 1
            sessions[name].add(sess)
            verbs[name][verb] += 1
            for kinds in detail_values(detail, "surfaced"):
                surfaced.append((at[:16], name, verb, kinds, sess))
            for kind in detail_values(detail, "read"):
                reads.append((at[:16], name, kind, sess))
            for seam in detail_values(detail, "goal-seam"):
                seams[(name, sess)][seam] += 1

    print(f"window: {args.since} <= at < {args.until}; roster {len(roster)} repo(s); "
          f"oldest record in the live log {oldest}; malformed line(s) {malformed}")
    total = sum(runs.values())
    if not total:
        print("COULD NOT VERIFY — the window holds no roster record; this says "
              "nothing about any count below it.")
        return 3
    all_sessions = sum(len(s) for s in sessions.values())
    print(f"verb runs (ticks excluded): {total} across {len(runs)} repo(s), "
          f"{all_sessions} repo-session pair(s)")
    for name in sorted(runs, key=runs.get, reverse=True):
        top = ", ".join(f"{v} {n}" for v, n in verbs[name].most_common(6))
        print(f"  {name}: {runs[name]} run(s), {len(sessions[name])} session(s) — {top}")
    print(f"surfacings: {len(surfaced)}")
    for row in surfaced:
        print("  " + " | ".join(row))
    print(f"kind reads: {len(reads)}")
    for row in reads:
        print("  " + " | ".join(row))
    print(f"goal seams: {sum(sum(c.values()) for c in seams.values())} "
          f"in {len(seams)} repo-session pair(s)")
    for (name, sess), c in sorted(seams.items()):
        print(f"  {name} {sess}: " + ", ".join(f"{k} {n}" for k, n in sorted(c.items())))
    print(f"NOT ROSTER (never pooled above): {sum(foreign.values())} run(s) — "
          + (", ".join(f"{d} {n}" for d, n in sorted(foreign.items())) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
