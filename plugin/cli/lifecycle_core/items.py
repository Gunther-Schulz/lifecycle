"""`ITEMS.md`: the shape, the parser, the file lock, the shape check.

THE FILE IS TOOL-OWNED. Fixed-slot blocks, one writer, a schema line at the
top. A hand edit that breaks the shape fails the shape check — that is what
makes "the tool is the only writer" a mechanism rather than a convention.

WHAT THE PARSER MUST SURVIVE, and this is the design's own distinction: a
BROKEN SHAPE is a finding, while an UNKNOWN GRADE WORD is READABLE. A grade
word reaching this file by a merge or by an older tool must not crash the
parse and must not be silently folded into open or closed — it is reported in
the census's THIRD ANSWER, open / closed / unknown-with-counts, which is the
shape `backlog-census.py` had and this successor keeps by design. A counter
that folds what it does not recognise into the open queue inflates exactly
the numbers the drain triggers read.

THREE ANSWERS, HERE SPECIFICALLY. `item check` returns COULD NOT VERIFY — not
CLEAN — when the file carries a grade word it cannot classify. The file is
well-formed, so it is not a shape finding; but every count printed beside it
is provisional, and a provisional count reported as CLEAN is a number shaped
like a pass.

THE ARCHIVE IS NOT PARSED. `ITEMS-DONE.md` carries an
`## Archive (pre-migration)` section holding historical bodies VERBATIM.
Those bodies were written by hand, by other tools, over years — they will
never satisfy a fixed-slot shape and were never meant to. The shape check
skips everything from that heading onward; conservation still counts it.
"""

import fcntl
import re
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from . import exits

#: The carrier format this build understands. A file stamped ABOVE it is
#: refused rather than parsed: an old tool reading a new file drops the slots
#: it does not recognise, and a dropped slot is invisible in the output.
SCHEMA_FLOOR = 1

#: §3.1 — five grades, closed. A repo's declared EXTRA grade words are not
#: accepted; the migration maps their meanings and its report says so per
#: entry.
GRADES_OPEN = ("NEW", "READY", "PARKED")
GRADES_CLOSED = ("DONE", "DROPPED")
GRADES = GRADES_OPEN + GRADES_CLOSED

#: The slots, in order. Fixed: a block carries exactly these, exactly once,
#: in this sequence. Order is part of the shape rather than decoration — a
#: diff over a tool-written file should show what CHANGED, not where a slot
#: wandered to.
SLOTS = ("grade", "requirement", "goal", "write-set", "done-criterion",
         "evidence", "blocked-by")

#: Head lines the carrier understands. `schema` is required and first;
#: the conservation trio is optional here because the identity that uses it
#: (`items + done == baseline + added - compacted`) is written by the close
#: verb, which this build does not carry — the SLOTS exist now so that verb
#: does not have to change the file's shape to start using them.
HEAD_KEYS = ("schema", "baseline", "added", "compacted")
HEAD_INT_KEYS = ("schema", "baseline", "added", "compacted")

ARCHIVE_HEADING = "## Archive (pre-migration)"

_HEAD_LINE = re.compile(r"^([a-z-]+):\s*(.*)$")
_BLOCK_HEADING = re.compile(r"^##\s+(\S+)\s*$")
_SLOT_LINE = re.compile(r"^([a-z-]+):\s?(.*)$")


@dataclass
class Item:
    ident: str
    slots: dict
    line: int

    @property
    def grade(self) -> str:
        return (self.slots.get("grade") or "").strip()


@dataclass
class Parsed:
    head: dict = field(default_factory=dict)
    items: list = field(default_factory=list)
    #: (row-id, line-number, message) — shape problems, never grade problems.
    problems: list = field(default_factory=list)
    archive_lines: int = 0
    #: Set when the file is stamped above the floor: nothing below the head
    #: was parsed, and no count from this object means anything.
    refused: bool = False


# --- the lock ----------------------------------------------------------------

@contextmanager
def carrier_lock(path: Path, *, timeout_note: str = ""):
    """Serialize every writer of a carrier file.

    "Subagents never book" is a CONVENTION and conventions do not serialize
    anything; this does. The lock is a sibling `.lock` file rather than the
    carrier itself, because a writer that locks the file it is about to
    replace by rename loses the lock with the inode.

    `flock` is advisory and process-wide: it holds across processes on one
    machine, which is the collision this design is built for. ACROSS machines
    the carrier rides git and a collision is a loud merge conflict — a
    database is the answer only if that recurs measurably.
    """
    lock_path = Path(str(path) + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fh = open(lock_path, "a+")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        yield fh
    finally:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        finally:
            fh.close()


# --- parsing -----------------------------------------------------------------

def parse(text: str) -> Parsed:
    """Read a carrier file. Never raises on content — problems are collected.

    A parser that threw on a bad block would make one hand edit take the
    whole file out of reach, including the 300 blocks that are fine. The
    caller gets what parsed AND what did not.
    """
    out = Parsed()
    lines = text.split("\n")

    # --- head
    i = 0
    while i < len(lines) and not lines[i].startswith("## "):
        raw = lines[i]
        i += 1
        if not raw.strip():
            continue
        m = _HEAD_LINE.match(raw)
        if not m:
            out.problems.append(("item_shape", i,
                                 f"head line {i} is not `key: value`: {raw!r}"))
            continue
        key, val = m.group(1), m.group(2).strip()
        if key not in HEAD_KEYS:
            out.problems.append(("item_shape", i,
                                 f"unknown head key {key!r} on line {i}; the "
                                 f"head keys are {', '.join(HEAD_KEYS)}"))
            continue
        if key in HEAD_INT_KEYS:
            try:
                out.head[key] = int(val)
            except ValueError:
                out.problems.append(("item_shape", i,
                                     f"head key {key!r} must be an integer, "
                                     f"got {val!r}"))
                continue
        else:
            out.head[key] = val

    if "schema" not in out.head:
        out.problems.append(("item_shape", 1,
                             "the file carries no `schema: <n>` head line. "
                             "A carrier without a version cannot be refused "
                             "by a future tool, which is the whole reason "
                             "the line exists."))
    elif out.head["schema"] > SCHEMA_FLOOR:
        out.problems.append((
            "schema_above_floor", 1,
            f"file is stamped schema {out.head['schema']}; this build "
            f"understands {SCHEMA_FLOOR}. REFUSING TO PARSE the body — an "
            "old tool that parsed it anyway would drop every slot it does "
            "not recognise, silently."))
        out.refused = True
        return out

    # --- blocks
    current = None
    seen_order = []
    while i < len(lines):
        raw = lines[i]
        lineno = i + 1
        i += 1

        if raw.strip() == ARCHIVE_HEADING:
            if current is not None:
                _close_block(out, current, seen_order)
                current = None
            out.archive_lines = len(lines) - i
            break

        m = _BLOCK_HEADING.match(raw)
        if m:
            if current is not None:
                _close_block(out, current, seen_order)
            current = Item(ident=m.group(1), slots={}, line=lineno)
            seen_order = []
            continue

        if not raw.strip():
            continue

        if current is None:
            out.problems.append(("item_shape", lineno,
                                 f"line {lineno} sits outside any block: "
                                 f"{raw[:60]!r}. Every line after the head "
                                 "belongs to a `## <id>` block."))
            continue

        sm = _SLOT_LINE.match(raw)
        if not sm:
            out.problems.append((
                "item_shape", lineno,
                f"line {lineno} in block {current.ident!r} is not a "
                f"`slot: value` line: {raw[:60]!r}. Slot values are ONE line "
                "— a wrapped value is a shape break, not a long value."))
            continue
        slot, val = sm.group(1), sm.group(2)
        if slot in current.slots:
            out.problems.append(("item_shape", lineno,
                                 f"block {current.ident!r} repeats slot "
                                 f"{slot!r}."))
            continue
        current.slots[slot] = val
        seen_order.append(slot)

    if current is not None:
        _close_block(out, current, seen_order)

    ids = {}
    for it in out.items:
        ids.setdefault(it.ident, []).append(it.line)
    for ident, at in ids.items():
        if len(at) > 1:
            out.problems.append((
                "duplicate_id", at[1],
                f"id {ident!r} appears {len(at)} times (lines "
                f"{', '.join(str(a) for a in at)}). A crash between the "
                "append and the commit of a close leaves two copies — that "
                "is DUPLICATE and recoverable, never loss."))
    return out


def _close_block(out: Parsed, item: Item, seen_order: list) -> None:
    missing = [s for s in SLOTS if s not in item.slots]
    unknown = [s for s in seen_order if s not in SLOTS]
    if missing:
        out.problems.append((
            "item_shape", item.line,
            f"block {item.ident!r} (line {item.line}) is missing slot(s): "
            + ", ".join(missing)
            + ". The tool writes every slot; a block missing one was written "
            "by hand."))
    if unknown:
        out.problems.append(("item_shape", item.line,
                             f"block {item.ident!r} carries unknown slot(s): "
                             + ", ".join(unknown)))
    known_order = [s for s in seen_order if s in SLOTS]
    if not missing and not unknown and known_order != list(SLOTS):
        out.problems.append((
            "item_shape", item.line,
            f"block {item.ident!r} has its slots out of order: "
            f"{', '.join(known_order)}. The order is fixed so a diff shows "
            "what changed, not where a slot wandered."))
    out.items.append(item)


def check_ids(parsed: Parsed, prefix: str | None) -> list:
    """Ids are `<declared-prefix>-<n>`, checked against the DECLARATION.

    Read from the declaration rather than inferred from the file: inferring
    the prefix from the ids present would make any consistent corruption look
    correct, which is the same-parentage defect in miniature.
    """
    if not prefix:
        return []
    pat = re.compile(rf"^{re.escape(prefix)}-\d+$")
    return [(it.ident, it.line) for it in parsed.items if not pat.match(it.ident)]


# --- the census: three answers -----------------------------------------------

def census(parsed: Parsed) -> dict:
    """open / closed / unknown-with-counts.

    THREE answers, not two. An unknown grade word is neither open nor closed
    and is never folded into either: the drain and retirement triggers read
    these numbers, and a counter that guessed would inflate exactly the ones
    that decide whether a repo owes a pass.
    """
    open_n = closed_n = 0
    unknown: dict = {}
    for it in parsed.items:
        g = it.grade
        if g in GRADES_OPEN:
            open_n += 1
        elif g in GRADES_CLOSED:
            closed_n += 1
        else:
            unknown[g or "(empty)"] = unknown.get(g or "(empty)", 0) + 1
    return {"open": open_n, "closed": closed_n, "unknown": unknown,
            "total": len(parsed.items)}


# --- the shape check ---------------------------------------------------------

def check_file(path: Path, out, prefix: str | None = None) -> int:
    """The pre-commit shape check over one carrier file."""
    if not path.exists():
        out(f"COULD NOT VERIFY: no carrier at {path}. An absent file and an "
            "empty one are not the same answer, and neither is clean.")
        return exits.COULD_NOT_VERIFY
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        out(f"COULD NOT VERIFY: {path} could not be read ({exc!r}).")
        return exits.COULD_NOT_VERIFY

    parsed = parse(text)
    for row, line, msg in parsed.problems:
        out(f"FINDING [{row}] {path.name}:{line}: {msg}")

    if parsed.refused:
        out(f"item check: {exits.word(exits.FINDING)} — the body was not "
            "parsed, so no count below would have meant anything.")
        return exits.FINDING

    bad_ids = check_ids(parsed, prefix)
    for ident, line in bad_ids:
        out(f"FINDING [item_shape] {path.name}:{line}: id {ident!r} does not "
            f"match the declared prefix {prefix!r} — ids are "
            f"`{prefix}-<n>` and immutable across moves.")

    c = census(parsed)
    out(f"census: open {c['open']}  closed {c['closed']}  "
        f"unknown {sum(c['unknown'].values())}  (total {c['total']})")
    for word_, n in sorted(c["unknown"].items()):
        out(f"  unknown grade {word_!r}: {n} — READ, never folded into open "
            "or closed. It reached this file by a merge or an older tool.")
    if parsed.archive_lines:
        out(f"archive: {parsed.archive_lines} line(s) after "
            f"{ARCHIVE_HEADING!r}, held verbatim and not shape-checked.")

    code = exits.CLEAN
    if parsed.problems or bad_ids:
        code = exits.FINDING
    if c["unknown"]:
        code = exits.worst([code, exits.COULD_NOT_VERIFY])

    out(f"item check: {exits.word(code)} — "
        f"{len(parsed.problems) + len(bad_ids)} shape finding(s), "
        f"{len(c['unknown'])} unclassifiable grade word(s).")
    return code
