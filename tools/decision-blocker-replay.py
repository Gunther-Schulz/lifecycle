#!/usr/bin/env python3
"""Replay probe for refocus design round 2, decision D3.

The question D3 asks before anything is built: when a `decision` blocker
was BOOKED, did the ledger as of that moment already hold a decision line
the shipped comparator (`verbs.decision_candidates`, R7 / lc-289) matches?

Read-only over git history. For each roster repo it walks every commit
that touched the item carrier, finds the first commit in which each
(item id, decision question) pair appears, reads the ledger AS OF THAT
COMMIT (`git show <commit>:LEDGER.md`), and runs the comparator on the
question. It writes one JSON row per booked blocker to `--out`, which
lives outside the repo: other repos' carrier text is not this repo's to
publish.

What it cannot see, said here so the output is not over-read:
  * a blocker whose booking commit carries no ledger file is COULD NOT
    VERIFY for that row, never a non-match;
  * a commit that books many blockers at once is a MIGRATION, not a
    session booking; those rows are flagged and never pooled;
  * whether a match ANSWERS the question is judgment. The tool lists
    fires; grading them TRUE or FALSE is done by a reader.

Controls, run on every invocation and printed (`selftest`): each repo's
newest decision question replayed against its own ledger must fire on
itself, and a nonsense question must not. A repo where the first fails
has a ledger the comparator cannot read, and its zero is not a zero.

Exit 0 with the tally; exit 3 when no repo could be read at all.
"""
import argparse
import collections
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "plugin" / "cli"))

from lifecycle_core import lanes, ledger, verbs  # noqa: E402

ITEMS = "ITEMS.md"
LEDGER = "LEDGER.md"
MIGRATION_AT = 20  # pairs first seen in one commit, at or above which it is a migration
HEAD_RE = re.compile(r"^## (\S+)\s*$")
BLOCKER_RE = re.compile(
    r"^(?:blocked-by|amended-blocked-by): (?:\d{4}-\d{2}-\d{2} )?decision (.+?)\s*$")
NONSENSE = "zzqx plomberoo vint quazzle frebnik"


def git(repo: str, *args: str):
    proc = subprocess.run(["git", "-C", repo, *args], capture_output=True,
                          text=True, errors="replace")
    return proc.returncode, proc.stdout


def pairs_in(text: str) -> set:
    """`{(item id, decision question)}` in one carrier body."""
    found = set()
    ident = None
    for line in text.splitlines():
        m = HEAD_RE.match(line)
        if m:
            ident = m.group(1)
            continue
        m = BLOCKER_RE.match(line)
        if m and ident:
            found.add((ident, m.group(1)))
    return found


def ledger_at(repo: str, commit: str):
    """The parsed ledger as of `commit`, or None when the commit has none."""
    rc, text = git(repo, "show", f"{commit}:{LEDGER}")
    if rc != 0:
        return None
    try:
        return ledger.parse(text)
    except Exception:
        return None


def decision_lines(parsed) -> list:
    return [ln for ln in parsed.lines if ln.kind == "decision"]


def replay_repo(repo: str) -> dict:
    name = Path(repo).name
    rc, out = git(repo, "log", "--reverse", "--format=%H %cs", "--", ITEMS)
    if rc != 0 or not out.strip():
        return {"repo": name, "readable": False, "rows": [], "selftest": None}
    seen = set()
    rows = []
    for entry in out.split("\n"):
        if not entry.strip():
            continue
        commit, date = entry.split()
        rc, text = git(repo, "show", f"{commit}:{ITEMS}")
        if rc != 0:
            continue
        new = sorted(pairs_in(text) - seen)
        if not new:
            continue
        seen.update(new)
        parsed = ledger_at(repo, commit)
        n_decisions = len(decision_lines(parsed)) if parsed is not None else None
        for ident, question in new:
            row = {"repo": name, "item": ident, "question": question,
                   "commit": commit[:10], "date": date,
                   "booked_with": len(new),
                   "migration": len(new) >= MIGRATION_AT,
                   "ledger_decisions_then": n_decisions, "matches": []}
            if parsed is not None:
                for ln, shared in verbs.decision_candidates(parsed, question):
                    row["matches"].append({
                        "line": ln.lineno,
                        "question": ln.slots.get("question", ""),
                        "answer": ln.slots.get("answer", ""),
                        "shared": shared})
            rows.append(row)

    selftest = None
    head_ledger = Path(repo) / LEDGER
    try:
        parsed = ledger.parse(head_ledger.read_text(encoding="utf-8"))
        decisions = decision_lines(parsed)
        if decisions:
            newest = decisions[-1].slots.get("question", "")
            selftest = {
                "decisions": len(decisions),
                "self_fires": any(
                    ln.lineno == decisions[-1].lineno
                    for ln, _ in verbs.decision_candidates(parsed, newest)),
                "nonsense_fires": bool(verbs.decision_candidates(parsed, NONSENSE)),
            }
        else:
            selftest = {"decisions": 0, "self_fires": None, "nonsense_fires": None}
    except (OSError, Exception):
        selftest = None
    return {"repo": name, "readable": True, "rows": rows, "selftest": selftest}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True, help="JSONL of every booked blocker row")
    args = ap.parse_args()

    roster = [ln.strip() for ln in lanes.roster_path().read_text(
        encoding="utf-8").splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")]
    results = [replay_repo(r) for r in roster]
    if not any(r["readable"] for r in results):
        print("COULD NOT VERIFY — no roster repo's item-carrier history could be read")
        return 3

    out_path = Path(args.out).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        for r in results:
            for row in r["rows"]:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    tot = collections.Counter()
    print("repo | blockers booked | migration-born | session-booked | "
          "no ledger then | ledger had 0 decisions | FIRES (session-booked) | "
          "selftest")
    for r in results:
        if not r["readable"]:
            print(f"{r['repo']} | UNREADABLE — no item-carrier history")
            continue
        rows = r["rows"]
        mig = [x for x in rows if x["migration"]]
        ses = [x for x in rows if not x["migration"]]
        nol = [x for x in ses if x["ledger_decisions_then"] is None]
        zero = [x for x in ses if x["ledger_decisions_then"] == 0]
        fires = [x for x in ses if x["matches"]]
        mfires = [x for x in mig if x["matches"]]
        st = r["selftest"]
        if st is None:
            st_txt = "ledger unreadable at HEAD"
        elif st["decisions"] == 0:
            st_txt = "0 decision lines at HEAD — the comparator has nothing to match"
        else:
            st_txt = (f"{st['decisions']} decisions; self-match "
                      f"{'FIRES' if st['self_fires'] else 'DOES NOT FIRE'}; "
                      f"nonsense {'FIRES' if st['nonsense_fires'] else 'silent'}")
        print(f"{r['repo']} | {len(rows)} | {len(mig)} | {len(ses)} | {len(nol)} | "
              f"{len(zero)} | {len(fires)} (+{len(mfires)} migration-born) | {st_txt}")
        tot["booked"] += len(rows)
        tot["migration"] += len(mig)
        tot["session"] += len(ses)
        tot["no_ledger"] += len(nol)
        tot["zero_decisions"] += len(zero)
        tot["fires"] += len(fires)
        tot["exercisable"] += len([x for x in ses
                                   if (x["ledger_decisions_then"] or 0) > 0])
    print(f"TOTAL | booked {tot['booked']} | migration-born {tot['migration']} | "
          f"session-booked {tot['session']} | no ledger then {tot['no_ledger']} | "
          f"ledger had 0 decisions {tot['zero_decisions']} | "
          f"EXERCISABLE (session-booked, ledger held >=1 decision) "
          f"{tot['exercisable']} | FIRES {tot['fires']}")
    print(f"rows written: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
