#!/usr/bin/env python3
"""List the live items still waiting on a SHARED migration question (lc-312).

Before lc-312 `migrate` minted one literal decision question per branch, and
`item ready` resolves a decision blocker by question-slot equality — so one
ledger answer cleared every item of a branch. The mint is repaired; a carrier
migrated BEFORE that still holds the shared text. This lists what to amend.

READ-ONLY. It prints `<id>\\t<new blocked-by>` on stdout, one line per item
whose EFFECTIVE blocker (read through `item slots`, which resolves amendments —
law 8) is one of the minter's own questions with no item named. The write is
the tool's own verb, run by the desk that owns the carrier:

    lifecycle --repo <repo> item amend <id> --blocked-by "<new blocked-by>" \\
        --not-derivable "<why>" --reason "<why>" [--no-commit]

THE QUESTIONS ARE READ FROM THE RUNNING MINTER, never restated here: a copied
list would stay green the day the minter gains a branch.

NOT REACHED, and said so rather than implied: a question minted before lc-40
carries the ledger's slot separator and is a different literal; this does not
match it. Such an item was never answerable, so it was never over-answered.

Exit: 0 listed (possibly none) · 3 could not read the carrier or an item.
"""
import re
import subprocess
import sys
from pathlib import Path

CLI = Path(__file__).resolve().parents[1] / "plugin" / "cli"
sys.path.insert(0, str(CLI))

from lifecycle_core import items, migrate  # noqa: E402


def shared_questions() -> set:
    """Every decision question `migration_blocker` can return, by execution."""
    probes = [
        ("- **PARKED 2026-01-01 — p.** The missing decision here is x.", True),
        ("- **PARKED 2026-01-01 — p.** Its named missing evidence is x.", True),
        ("- **READY 2026-01-01 — r.** body", True),
        ("- **An entry with no grade word.** body", True),
        ("- **An entry with no grade word.** body", False),
    ]
    out = set()
    for text, incomplete in probes:
        entry = migrate.read_carrier(f"# c\n\n## Open\n\n{text}\n").entries[0]
        migrate.classify(entry, None)
        blocked = migrate.migration_blocker(entry, slots_incomplete=incomplete)[0]
        kind, detail = items.classify_blocker(blocked, None)
        if kind == "decision":
            out.add(detail)
    return out


def main(argv) -> int:
    if len(argv) != 2:
        print("usage: requestion-migrated.py <repo>", file=sys.stderr)
        return 3
    repo = Path(argv[1])
    carrier = repo / "ITEMS.md"
    try:
        text = carrier.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"COULD NOT VERIFY: {carrier} is unreadable: {exc}",
              file=sys.stderr)
        return 3
    questions = shared_questions()
    ids = re.findall(r"(?m)^## ([a-z][a-z0-9-]*-\d+)\b", text)
    unread = listed = 0
    for ident in ids:
        run = subprocess.run(
            [sys.executable, str(CLI / "lifecycle"), "--repo", str(repo),
             "item", "slots", ident], capture_output=True, text=True)
        if run.returncode != 0:
            unread += 1
            print(f"COULD NOT READ {ident}: `item slots` exited "
                  f"{run.returncode}", file=sys.stderr)
            continue
        m = re.search(r"(?m)^blocked-by: (.*)$", run.stdout)
        kind, detail = items.classify_blocker(
            m.group(1).strip() if m else "", None)
        if kind == "decision" and detail in questions:
            listed += 1
            print(f"{ident}\t{migrate._for_item('decision ' + detail, ident)}")
    print(f"minter questions matched against: {len(questions)}; items read: "
          f"{len(ids) - unread} of {len(ids)}; unreadable: {unread}; "
          f"listed: {listed}", file=sys.stderr)
    return 3 if unread else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
