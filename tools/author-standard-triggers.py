#!/usr/bin/env python3
"""Add authored trigger stages to a schema-2 lifecycle declaration, textually.

Usage: author-standard-triggers.py <path to .claude/lifecycle.json> [extra.json]
The optional second file maps further kind names to their trigger text.
Inserts one line after the `growth` line of the `items` and `ledger lines`
kinds and proves by a parsed comparison that nothing else changed."""
import json, sys

#: this tool rewrites a tracked file (the declaration it is pointed at)
MUTATES_TRACKED_FILES = True
path = sys.argv[1]
TRIG = {
    "items": "verb item add — admission is the write that CREATES a body; `item park` and `item close` move one already admitted, so they are transitions of this kind rather than its trigger",
    "ledger lines": "verb ledger add decision — the button, and one of four: `ledger add` is a command GROUP, so the trigger names a leaf; `dropped`, `rejected` and `superseded` write this kind by the same act and are listed in the writer; `session` is the path around the button, for a fact or an open question",
}
if len(sys.argv) > 2:
    TRIG.update(json.load(open(sys.argv[2], encoding="utf-8")))
text = open(path, encoding="utf-8").read()
before = json.loads(text)
lines = text.split("\n")
out, kind = [], None
for ln in lines:
    s = ln.strip()
    for k in TRIG:
        if s == json.dumps(k) + ": {":
            kind = k
    if kind and s.startswith('"growth":') and "trigger" not in before["kinds"][kind]:
        if s.endswith(","):
            sys.exit(f"{kind}: growth is not the last key; edit by hand")
        indent = ln[: len(ln) - len(ln.lstrip())]
        out.append(ln + ",")
        out.append(indent + '"trigger": ' + json.dumps(TRIG[kind], ensure_ascii=False))
        kind = None
        continue
    out.append(ln)
new = "\n".join(out)
after = json.loads(new)
for k in TRIG:
    before["kinds"][k].setdefault("trigger", TRIG[k])
if after != before:
    sys.exit("parsed result differs from the expected one; nothing written")
open(path, "w", encoding="utf-8").write(new)
print("wrote", path)
