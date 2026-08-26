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
#:
#: ONE SCHEMA VERSION PER REPO (§3.8c): this floor and the declaration's must
#: be the same number, and `schema_mismatch` fires where a repo's carrier and
#: its declaration disagree. The floor answers "can this build read the file";
#: the mismatch answers "does this repo agree with itself".
SCHEMA_FLOOR = 2

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

#: CLOSED-BODY slots (§3.8c, W1c's G4). `superseded-by:` and `blocker-moot:`
#: were being WRITTEN onto moved bodies by `item add --join supersede` and
#: `item close` while being declared nowhere — so the done home carried two
#: slots no shape check knew about, and a closed body carrying either passed
#: everything because nothing shape-checked the done home at all.
#:
#: They are REAL SLOTS now rather than exempted annotations, and the direction
#: matters: exempting them by name would have made the done home a place where
#: an unknown slot is fine, which is the opposite of what a shape check is
#: for. Optional and closed-only — a LIVE block carrying one is a finding,
#: because both record something a closure did.
DONE_ONLY_SLOTS = ("superseded-by", "blocker-moot")

#: The transitional value a migrated slot carries when nobody ever recorded
#: one (§3.1). DECLARED rather than conventional: the retire lane must not
#: read it as "advances no goal", the join must never match on it, `item
#: check` counts it, and `item ready` REFUSES an item holding one — a slot
#: nobody has written is not a slot the desk has judged.
UNKNOWN = "UNKNOWN"

#: Which slots may legitimately hold UNKNOWN after a migration. `grade` and
#: `blocked-by` may not: a grade is always one of the five, and a blocker is
#: typed or NONE.
UNKNOWNABLE_SLOTS = ("goal", "write-set", "done-criterion", "evidence")

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
#: A comment line in the head: a markdown heading or bullet, or an HTML
#: comment. Matched by SHAPE rather than by a marker the writer must remember,
#: because the block this licenses is prose a human writes.
_COMMENT_LINE = re.compile(r"^\s*(#|<!--|-->|-\s|>\s|\*\s)")


def _is_comment(raw: str) -> bool:
    return bool(_COMMENT_LINE.match(raw))


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
    #: The archive section's raw body. Held rather than discarded because
    #: conservation COUNTS it while the shape check skips it — two different
    #: questions over the same bytes, and only one of them is about shape.
    archive_text: str = ""
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
    #
    # A COMMENT BLOCK MAY PRECEDE THE SCHEMA LINE (§3.8c). Before this, the
    # first non-blank line had to BE the schema line, which forced a carrier
    # in a public repo to be exactly `schema: 1` and nothing else — a file
    # that could not say what it was for. The permission is deliberately one
    # way round: comments before the version, never after it. Everything from
    # the schema line on is tool-written, and a comment there would be a hand
    # edit in the one region whose shape is the mechanism behind "the tool is
    # the only writer".
    i = 0
    seen_schema = False
    while i < len(lines) and not lines[i].startswith("## "):
        raw = lines[i]
        i += 1
        if not raw.strip():
            continue
        if _is_comment(raw):
            if seen_schema:
                out.problems.append((
                    "item_shape", i,
                    f"head line {i} is a comment AFTER the `schema:` line: "
                    f"{raw[:60]!r}. A comment block may PRECEDE the schema "
                    "line so a carrier can say what it is for; below it the "
                    "head is tool-written."))
            continue
        m = _HEAD_LINE.match(raw)
        if not m:
            out.problems.append(("item_shape", i,
                                 f"head line {i} is not `key: value`: {raw!r}"))
            continue
        key, val = m.group(1), m.group(2).strip()
        if key == "schema":
            seen_schema = True
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
            out.archive_text = "\n".join(lines[i:])
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
    unknown = [s for s in seen_order
               if s not in SLOTS and s not in DONE_ONLY_SLOTS]
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

    # THE CLOSED-BODY SLOTS ARE CLOSED-ONLY, and that is what makes them
    # slots rather than exemptions. `superseded-by:` records that a closure
    # replaced this body; `blocker-moot:` records a decision the closure made
    # moot. Both are things a CLOSE did, so a live block carrying one is a
    # block claiming an act that has not happened.
    done_only = [s for s in seen_order if s in DONE_ONLY_SLOTS]
    if done_only and item.grade not in GRADES_CLOSED:
        out.problems.append((
            "done_slot_on_live_item", item.line,
            f"block {item.ident!r} is {item.grade or '(no grade)'} and carries "
            + ", ".join(f"`{s}:`" for s in done_only)
            + " — slot(s) only a CLOSURE writes. `superseded-by:` says a "
              "closure replaced this body and `blocker-moot:` says a closure "
              "made a decision moot; on a live item each claims an act that "
              "has not happened, and the annotation is what a later reader "
              "would resolve through."))

    known_order = [s for s in seen_order if s in SLOTS]
    tail_out_of_place = [s for s in seen_order[:len(known_order)]
                         if s in DONE_ONLY_SLOTS]
    if not missing and not unknown and known_order != list(SLOTS):
        out.problems.append((
            "item_shape", item.line,
            f"block {item.ident!r} has its slots out of order: "
            f"{', '.join(known_order)}. The order is fixed so a diff shows "
            "what changed, not where a slot wandered."))
    elif not missing and not unknown and tail_out_of_place:
        out.problems.append((
            "item_shape", item.line,
            f"block {item.ident!r} carries "
            + ", ".join(f"`{s}:`" for s in tail_out_of_place)
            + " among the fixed slots. The closed-body slots follow "
              "`blocked-by:`, so a diff over a moved body shows the closure's "
              "annotation as an addition rather than as a reordering."))
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


# --- typed blockers ----------------------------------------------------------

#: §3.1's edge types, closed: an item id, a decision question, an evidence
#: predicate. "No other edge types" is the design's own sentence, and it is
#: what makes a blocker MECHANICALLY resolvable — an untyped one is prose,
#: and prose is what the aging rules cannot route to anybody's court.
BLOCKER_TYPES = ("item", "decision", "evidence")
BLOCKER_NONE = "NONE"


def classify_blocker(value: str, prefix: str | None):
    """`(type, detail)` — type in BLOCKER_TYPES, `"none"`, or None (untyped).

    `prefix` comes from the DECLARATION. Without it an item-id blocker
    cannot be told from prose that happens to look like one, and the caller
    is told so rather than guessed at — see `check_file`.
    """
    v = (value or "").strip()
    if not v or v == BLOCKER_NONE:
        return "none", ""
    if v.startswith("decision "):
        rest = v[len("decision "):].strip()
        return ("decision", rest) if rest else (None, "")
    if v.startswith("evidence "):
        rest = v[len("evidence "):].strip()
        return ("evidence", rest) if rest else (None, "")
    if prefix and re.fullmatch(rf"{re.escape(prefix)}-\d+", v):
        return "item", v
    return None, ""


# --- writing: the shape, spelled in exactly one place ------------------------

def render_block(ident: str, slots: dict) -> str:
    """One item block. THE ONLY place the on-disk shape is spelled.

    Slot ORDER comes from `SLOTS`, never from the caller's dict, so a caller
    that builds its mapping in another order cannot write a file the shape
    check then reports as out of order.
    """
    out = [f"## {ident}"]
    for slot in SLOTS:
        out.append(f"{slot}: {slots[slot]}")
    return "\n".join(out) + "\n"


def slot_value_problem(slot: str, value: str) -> str | None:
    """Why `value` cannot be written into `slot`, or None.

    Refused at the WRITER. A multi-line value parses as a shape break at
    read time — so the tool that wrote it would have produced a file its own
    check rejects, and the reader could not tell that from a hand edit.
    """
    v = "" if value is None else str(value)
    if not v.strip():
        return (f"slot {slot!r} is empty. Every slot is written; a blank one "
                "is the undeclared-stage shape at item scale — a plausible "
                "face on a gap.")
    if "\n" in v or "\r" in v:
        return (f"slot {slot!r} spans more than one line. Slot values are ONE "
                "line — a wrapped value is a shape break, not a long value, "
                "and the parser reports it as one.")
    return None


def next_ident(prefix: str, *parsed) -> tuple[str | None, str | None]:
    """`(next-id, why-not)` — the lowest unused `<prefix>-<n>`, n from 1.

    EVERY home is read, live and closed. Ids are immutable across moves, so
    an id allocator that looked only at the live carrier would re-issue the
    id of everything ever closed — and the collision would surface as a
    DUPLICATE finding months later, in a file nobody was editing.
    """
    if not prefix:
        return None, ("no `id-prefix` in the declaration, so an id cannot be "
                      "allocated. Ids are `<prefix>-<n>` and the prefix is "
                      "declared, never inferred from the ids already there.")
    used = set()
    pat = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
    for p in parsed:
        if p is None:
            continue
        for it in p.items:
            m = pat.match(it.ident)
            if m:
                used.add(int(m.group(1)))
    n = 1
    while n in used:
        n += 1
    return f"{prefix}-{n}", None


def replace_body(text: str, ident: str) -> tuple[str | None, str | None]:
    """`(text-without-that-block, the-block)` — or `(None, None)` if absent.

    Operates on the LIVE section only: everything from the archive heading
    onward is returned untouched, because those bodies are held verbatim and
    a text edit is exactly what "verbatim" forbids.
    """
    lines = text.split("\n")
    cut = len(lines)
    for i, ln in enumerate(lines):
        if ln.strip() == ARCHIVE_HEADING:
            cut = i
            break
    start = None
    end = None
    for i in range(cut):
        m = _BLOCK_HEADING.match(lines[i])
        if not m:
            continue
        if start is None and m.group(1) == ident:
            start = i
            continue
        if start is not None:
            end = i
            break
    if start is None:
        return None, None
    if end is None:
        end = cut
    body = "\n".join(lines[start:end]).rstrip("\n") + "\n"
    kept = lines[:start] + lines[end:]
    return "\n".join(kept), body


# --- conservation ------------------------------------------------------------

#: A top-level bullet in the archive — the entry notion the OLD carrier used
#: and `backlog-census.py` still uses, so the count that crosses the
#: migration is the same count on both sides of it.
_ARCHIVE_BULLET = re.compile(r"^- ")


def archive_entries(archive_text: str) -> int:
    return sum(1 for ln in archive_text.split("\n")
               if _ARCHIVE_BULLET.match(ln))


def conservation(items_parsed: Parsed, done_parsed: Parsed | None,
                 done_unreadable: str | None = None) -> dict:
    """`items + done == baseline + added − compacted`, re-runnable at will.

    THE IDENTITY IS THE POINT, not the numbers. It says the carrier has lost
    nothing silently: every body ever admitted is either live or in the done
    home, minus what compaction deliberately folded away. A closure moves a
    body between the two sides and the identity does not move — which is why
    a FAILING identity means a body left by some path that is not a closure.

    THREE ANSWERS. A missing head key or an unreadable done home is COULD
    NOT VERIFY, never a clean identity: an unread done home contributes 0,
    and 0 is a number shaped exactly like a pass.
    """
    out = {"ok": None, "why": None, "items": len(items_parsed.items),
           "done": None, "archive": None, "baseline": None, "added": None,
           "compacted": None, "expected": None, "actual": None}

    missing = [k for k in ("baseline", "added", "compacted")
               if k not in items_parsed.head]
    if missing:
        out["why"] = (
            "the carrier head declares no " + ", ".join(f"`{k}`" for k in missing)
            + ". The identity's right-hand side is PERSISTED, not recomputed "
            "— a baseline re-derived from the files it grades would move with "
            "every corruption and stay green on all of them.")
        return out
    if done_parsed is None:
        out["why"] = (done_unreadable or "the done home could not be read")
        out["baseline"] = items_parsed.head["baseline"]
        return out

    out["archive"] = archive_entries(done_parsed.archive_text)
    out["done"] = len(done_parsed.items) + out["archive"]
    out["baseline"] = items_parsed.head["baseline"]
    out["added"] = items_parsed.head["added"]
    out["compacted"] = items_parsed.head["compacted"]
    out["actual"] = out["items"] + out["done"]
    out["expected"] = out["baseline"] + out["added"] - out["compacted"]
    out["ok"] = out["actual"] == out["expected"]
    return out


def report_conservation(c: dict, out) -> int:
    """Render a conservation result and answer with one of the three codes."""
    if c["ok"] is None:
        out(f"COULD NOT VERIFY: conservation — {c['why']}")
        return exits.COULD_NOT_VERIFY
    out(f"conservation: items {c['items']} + done {c['done']} "
        f"(of which archive {c['archive']}) = {c['actual']}   "
        f"baseline {c['baseline']} + added {c['added']} − compacted "
        f"{c['compacted']} = {c['expected']}")
    if c["ok"]:
        out("conservation: CLEAN — nothing left the carrier by a path that "
            "is not a closure.")
        return exits.CLEAN
    delta = c["actual"] - c["expected"]
    # THE SIGN IS THE DIAGNOSIS, and one message for both signs told the
    # wrong story over the recoverable case. Found by the interrupted-move
    # test: a crash between the append and the delete leaves a SURPLUS
    # (+1), and a single message describing "a body left the carrier by a
    # path that is not a closure" reads as LOSS over exactly the state the
    # design says must never read as loss. Two conditions, two rows.
    if delta < 0:
        out(f"FINDING [conservation_short] the identity is SHORT by "
            f"{-delta}. A body left the carrier by a path that is not a "
            "closure — a hand deletion, a bad merge, a half-applied patch. "
            "The bodies are in git; this says one is missing from the "
            "files, not that it is gone.")
    else:
        out(f"FINDING [conservation_surplus] the identity is OVER by "
            f"{delta}: the homes hold MORE bodies than were ever admitted. "
            "This is not loss and must not be repaired as if it were. The "
            "ordinary cause is an interrupted close — the move appends to "
            "the done home before deleting from the carrier, so a crash "
            "between the two leaves both copies and both are counted. Check "
            "the DUPLICATE line above first: if an id is in both homes, this "
            "number is that same event and the repair is the same one.")
    return exits.FINDING


# --- the move's own integrity ------------------------------------------------

def check_move_integrity(items_parsed: Parsed, done_parsed: Parsed | None,
                         out, done_unreadable: str | None = None) -> int:
    """An id present in BOTH homes: DUPLICATE, recoverable, never loss.

    THE WHOLE REASON THE MOVE IS SPECIFIED AS APPEND-THEN-DELETE. The window
    between the two writes holds two copies of one body; a crash there is
    survivable and this is what makes it visible. The opposite ordering —
    delete then append — would put the window on the LOSS side, where a
    crash destroys the body and nothing afterwards can tell that it existed.
    So this finding is the design working, and its message says so: a reader
    who takes DUPLICATE for corruption will "repair" it by deleting one copy
    at random.
    """
    if done_parsed is None:
        out("COULD NOT VERIFY: the done home could not be read, so an id "
            f"present in both homes would not be seen. {done_unreadable or ''}")
        return exits.COULD_NOT_VERIFY
    live = {it.ident: it.line for it in items_parsed.items}
    both = [(d.ident, live[d.ident], d.line)
            for d in done_parsed.items if d.ident in live]
    for ident, live_line, done_line in both:
        out(f"FINDING [duplicate_id] id {ident!r} is in BOTH homes — live at "
            f"line {live_line}, done at line {done_line}. This is DUPLICATE "
            "and RECOVERABLE, never loss: a close appends to the done home "
            "and then deletes from the carrier, so a crash between the two "
            "leaves exactly this. The repair is to delete the LIVE copy once "
            "the done copy is confirmed complete — not to pick one at random.")
    if both:
        return exits.FINDING
    out(f"move integrity: CLEAN — no id in both homes ({len(live)} live, "
        f"{len(done_parsed.items)} done).")
    return exits.CLEAN


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

    untyped, blockers_unverified = check_parked_blockers(parsed, prefix)
    for ident, line, value in untyped:
        out(f"FINDING [parked_without_typed_blocker] {path.name}:{line}: "
            f"block {ident!r} is PARKED with an untyped `blocked-by`: "
            f"{value!r}. The types are closed — `<{prefix or 'prefix'}-<n>>`, "
            "`decision <question>`, `evidence <predicate>` — because an "
            "aging item is routed by WHOSE COURT it sits in, and prose sits "
            "in nobody's. A parked item nothing can re-evaluate is a drop "
            "waiting to happen quietly.")
    if blockers_unverified:
        out(f"COULD NOT VERIFY: {blockers_unverified}")

    unk_counts, unk_misplaced = unknown_slots(parsed)
    for ident, line, slot in unk_misplaced:
        out(f"FINDING [unknown_slot_misplaced] {path.name}:{line}: block "
            f"{ident!r} holds UNKNOWN in `{slot}`. UNKNOWN is the migration's "
            "declared marker for a slot nobody ever recorded, and the grade "
            "workflow fills it — but a grade is one of the five and a blocker "
            "is typed or NONE, so UNKNOWN there is a value nothing can ever "
            "fill in.")
    if unk_counts:
        out("UNKNOWN slots (the migration's declared transitional value, "
            "filled by the grade workflow before READY): "
            + ", ".join(f"{s} {n}" for s, n in sorted(unk_counts.items()))
            + f" — across {sum(1 for it in parsed.items if unknown_slots_of(it))}"
              " item(s).")

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
    if parsed.problems or bad_ids or untyped or unk_misplaced:
        code = exits.FINDING
    if c["unknown"] or blockers_unverified:
        code = exits.worst([code, exits.COULD_NOT_VERIFY])

    # READY IS REFUSED TO AN ITEM HOLDING AN UNKNOWN SLOT — over the CARRIER,
    # not only at `item add` (§3.1). The verb is not the only way a block
    # reaches the file, and a rule enforced only on the write path is a
    # convention with a mechanism's reputation. This is the one that stops a
    # migrated entry being graded READY on a slot nobody has ever written.
    ready_unknown = [(it.ident, it.line, unknown_slots_of(it))
                     for it in parsed.items
                     if it.grade == "READY" and unknown_slots_of(it)]
    for ident, line, slots_ in ready_unknown:
        out(f"FINDING [ready_with_unknown_slot] {path.name}:{line}: block "
            f"{ident!r} is READY and still holds UNKNOWN in "
            + ", ".join(f"`{s}`" for s in slots_)
            + ". READY is the desk's judgment that a fresh context could "
              "execute this now, and a slot nobody has ever written is the "
              "one thing that judgment cannot have been made over.")
    if ready_unknown:
        code = exits.worst([code, exits.FINDING])

    out(f"item check: {exits.word(code)} — "
        f"{len(parsed.problems) + len(bad_ids) + len(untyped) + len(unk_misplaced) + len(ready_unknown)}"
        f" shape finding(s), {len(c['unknown'])} unclassifiable grade word(s).")
    return code


# --- UNKNOWN, the declared transitional value (§3.1) --------------------------

def unknown_slots(parsed: Parsed):
    """`(count_by_slot, misplaced)` for the migration's UNKNOWN marker.

    UNKNOWN IS DECLARED, NOT CONVENTIONAL. It means "nobody ever recorded
    one", and every consumer has to know that: the join never matches on it,
    the retire lane must not read it as "advances no goal", and `item ready`
    refuses an item holding one. So it is COUNTED here rather than left to be
    noticed — a migrated carrier where every goal says UNKNOWN and nothing
    says how many is a carrier whose emptiness is invisible.

    `misplaced` is UNKNOWN in a slot that may never hold it: a grade is one
    of the five and a blocker is typed or NONE, so UNKNOWN there is a slot
    value nothing can ever fill in.
    """
    counts: dict = {}
    misplaced = []
    for it in parsed.items:
        for slot, value in it.slots.items():
            if (value or "").strip().upper() != UNKNOWN:
                continue
            if slot in UNKNOWNABLE_SLOTS:
                counts[slot] = counts.get(slot, 0) + 1
            else:
                misplaced.append((it.ident, it.line, slot))
    return counts, misplaced


def unknown_slots_of(item: Item) -> list:
    """Which of one item's slots still hold the migration's marker."""
    return [s for s in UNKNOWNABLE_SLOTS
            if (item.slots.get(s) or "").strip().upper() == UNKNOWN]


# --- the done home's own shape check (§3.8c; W1c's G4) -----------------------

def check_done_file(path: Path, out, prefix: str | None = None) -> int:
    """The done home is a KIND with the TOOL as its writer, so shape applies.

    IT DID NOT BEFORE, and that was the gap: `item check` ran `check_file`
    over the LIVE carrier only, while the done home was parsed for
    conservation and duplicates by two callers that both ignored
    `parsed.problems`. A closed body carrying anything at all passed
    everything.

    THREE THINGS THE LIVE CHECK CANNOT ASK, all of them about closure:

      * every block here is CLOSED — DONE or DROPPED. An open grade in the
        closure home is a body that arrived by a path that is not a close.
      * no BLOCKER survives a closure. A closed item waits for nothing, and a
        blocker left on it is a wait recorded against a body that has stopped
        waiting — which is exactly what leaves an unanswerable question in the
        operator's queue after the item that asked it is gone. `item close`
        clears it and records it as `blocker-moot:`.
      * the ARCHIVE is skipped, as everywhere else: those bodies predate the
        tool and were never meant to satisfy a fixed-slot shape.
    """
    if not path.exists():
        out(f"COULD NOT VERIFY: no done home at {path}. An absent closure "
            "home and an empty one are not the same answer, and neither is "
            "clean.")
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
        out(f"done-home check: {exits.word(exits.FINDING)} — the body was not "
            "parsed.")
        return exits.FINDING

    bad_ids = check_ids(parsed, prefix)
    for ident, line in bad_ids:
        out(f"FINDING [item_shape] {path.name}:{line}: id {ident!r} does not "
            f"match the declared prefix {prefix!r}.")

    open_here = [it for it in parsed.items if it.grade not in GRADES_CLOSED]
    for it in open_here:
        out(f"FINDING [open_grade_in_done_home] {path.name}:{it.line}: block "
            f"{it.ident!r} is graded {it.grade or '(none)'} in the CLOSURE "
            "home. Every body here left the carrier by a close, so its grade "
            "is DONE or DROPPED; an open grade here is a body that arrived by "
            "some other path — and conservation counts it on the closed side "
            "whatever its grade says.")

    blocked = []
    for it in parsed.items:
        kind, _detail = classify_blocker(it.slots.get("blocked-by", ""), prefix)
        if kind not in (None, "none"):
            blocked.append(it)
            out(f"FINDING [blocked_in_done_home] {path.name}:{it.line}: block "
                f"{it.ident!r} is closed and still carries "
                f"`blocked-by: {it.slots.get('blocked-by', '')}`. A closed "
                "item waits for nothing. `item close` clears the blocker and "
                "records it as `blocker-moot:` precisely so the operator's "
                "decision queue does not keep listing a question after the "
                "item that asked it is gone.")

    n = len(parsed.items)
    out(f"done home: {n} closed block(s), archive {parsed.archive_lines} "
        f"line(s) held verbatim and not shape-checked.")
    code = exits.CLEAN
    if parsed.problems or bad_ids or open_here or blocked:
        code = exits.FINDING
    out(f"done-home check: {exits.word(code)} — "
        f"{len(parsed.problems) + len(bad_ids) + len(open_here) + len(blocked)}"
        " finding(s).")
    return code


def check_parked_blockers(parsed: Parsed, prefix: str | None):
    """`([(id, line, value)], could-not-verify-reason)` for PARKED blocks.

    "A PARKED item without a typed blocker is a checker finding" (§3.1), and
    it is checked HERE — over the file — rather than only at `item park`,
    because the verb is not the only way a block reaches the file. A merge
    and a hand edit both do, and a rule enforced only on the write path is a
    convention with a mechanism's reputation.
    """
    parked = [it for it in parsed.items if it.grade == "PARKED"]
    if not parked:
        return [], None
    if not prefix:
        return [], ("`blocked-by` typing on PARKED blocks was not checked: "
                    "no `id-prefix` in the declaration, so an item-id blocker "
                    "cannot be told from prose that resembles one.")
    untyped = []
    for it in parked:
        kind, _detail = classify_blocker(it.slots.get("blocked-by", ""), prefix)
        if kind is None or kind == "none":
            untyped.append((it.ident, it.line, it.slots.get("blocked-by", "")))
    return untyped, None
