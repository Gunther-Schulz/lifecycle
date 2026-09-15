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
import json
import posixpath
import re
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from . import exits
from . import declaration as decl
from . import grammar

#: The carrier format this build understands. A file stamped ABOVE it is
#: refused rather than parsed: an old tool reading a new file drops the slots
#: it does not recognise, and a dropped slot is invisible in the output.
#:
#: ONE SCHEMA VERSION PER REPO (§3.8c): this floor and the declaration's must
#: be the same number, and `schema_mismatch` fires where a repo's carrier and
#: its declaration disagree. The floor answers "can this build read the file";
#: the mismatch answers "does this repo agree with itself".
#:
#: SINGLE-SOURCED (2026-08-26): this used to be its own literal `= 2`, and so
#: did `ledger.py`'s, with nothing pinning the three equal — a bump to one
#: could leave the others silently behind, and no test caught it
#: (`test_schema.SchemaFloorSingleSourced` is the one that now would).
#: `declaration.py` is the home because the declaration's own schema rule
#: lives there and `test_schema.py` already pointed at it.
SCHEMA_FLOOR = decl.SCHEMA_FLOOR

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
#: THE CLOSURE RECORD (lc-44). `item close --reason` accepted the session's
#: prose on a DONE close and wrote it NOWHERE — not the moved body, not the
#: ledger, not the commit message — while printing "moved <id> → ITEMS-DONE.md
#: (grade DONE)" plus a commit, which reads as a complete closure record.
#: Measured 2026-08-27 in dotfiles: df-143 closed with a 900-char reason naming
#: its commit ref; grep for that ref returned 0 in all three carriers
#: afterwards, and the closure basis had to be written into the ledger BY HAND.
#:
#: THE HOME IS THE MOVED BODY, never the ledger (judgment desk, 2026-08-27).
#: A dropped body may be pruned, so a DROP's record cannot live only there and
#: keeps its ledger `dropped:` line; the ledger stays decisions, supersessions
#: and drops. Two homes for one fact is the paraphrase-drift the carrier
#: doctrine forbids, so the DONE reason lives in exactly one of them.
#:
#: TWO LINES, on the promote precedent's reasoning: WHY it closed and WHICH
#: commit it closed at are two facts, and joining them needs a separator
#: INSIDE a value — which this carrier's prose carries constantly. The date is
#: a fixed shape instead, spelled as the amendment and promotion lines spell
#: it.
CLOSED_REASON = "closed-reason"
CLOSED_REF = "closed-ref"

DONE_ONLY_SLOTS = ("superseded-by", "blocker-moot", CLOSED_REASON, CLOSED_REF)

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

#: THE AMENDMENT LINES (lc-27). Until this wave no verb edited a block, so
#: every correction to a booked item was either a second item or a hand edit
#: — a law-8 violation with no other way out. An amendment is APPEND-ONLY:
#: the act writes a DATED GROUP at the end of the block, and the earlier
#: slot-line is RETAINED exactly as it was written. Nothing is rewritten in
#: place, so the block carries what it used to say beside what it says now.
#:
#: TWO FORMS, ONE MECHANISM. One `amended-<slot>:` line is the slot-line
#: form; several under one `amend-reason:` header is the dated-block form —
#: which is what makes a three-slot correction ONE act and one group rather
#: than three, the difference between annotating a carrier and doubling it.
#:
#: `grade` IS NOT AMENDABLE. A grade moves by judgment through `item park`,
#: `item close` and the desk's own re-grade; an amendment path to it would be
#: a second, quieter writer of the one slot READY-is-judged depends on.
AMENDABLE_SLOTS = tuple(s for s in SLOTS if s != "grade")
AMEND_PREFIX = "amended-"
AMEND_REASON = "amend-reason"

#: Every amendment line's value opens with its ISO date. The date is a fixed
#: shape rather than a separator, deliberately: a ` — ` separator would be
#: refused inside any value that already carries one, and this carrier's
#: values carry them constantly (`requirement: … — record: …`). A guard that
#: fired on the ordinary value would stop the lane (R11).
_AMEND_VALUE = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(\S.*)$")

#: THE PROMOTION LINES (lc-39). There was NO PATH FROM NEW TO READY: `grade`
#: is written once at admission, the note above says why `item amend` refuses
#: it, and `item ready` promotes nothing — so an item whose slots a desk later
#: filled could never be graded, and the head was empty by construction. The
#: repair is the third grade-moving path that note already names: the desk's
#: own re-grade, `item promote`. It moves `grade` IN PLACE — the shape `item
#: park` uses for a transition the tool owns end to end — and APPENDS this
#: dated pair, which is the RECORD of who judged and why.
#:
#: THE RECORD IS A HOME, not a flag on the act (R23): a design line that names
#: a thing names its home, and "recording who judged and why" with no home is
#: a record nobody can read. Here the home is the block itself, beside the
#: grade the judgment produced.
#:
#: TWO LINES RATHER THAN ONE, for exactly the reason `_AMEND_VALUE` states
#: above: WHO and WHY are two free-text facts, and joining them onto one line
#: needs a separator INSIDE a value — which this carrier's values already
#: carry constantly, so the parse would break on ordinary prose. The date is a
#: fixed shape instead, spelled as the amendment lines spell it.
#:
#: THEY REPEAT BY DESIGN, like the amendment lines: an item parked after its
#: promotion and judged again later carries both judgments, and a second
#: judgment that erased the first would leave the carrier unable to say the
#: desk had ever changed its mind.
PROMOTE_REASON = "promote-reason"
PROMOTED_BY = "promoted-by"
PROMOTION_LINES = (PROMOTE_REASON, PROMOTED_BY)

#: Head lines the carrier understands. `schema` is required and first;
#: the conservation trio is optional here because the identity that uses it
#: (`items + done == baseline + added - compacted`) is written by the close
#: verb, which this build does not carry — the SLOTS exist now so that verb
#: does not have to change the file's shape to start using them.
HEAD_KEYS = ("schema", "baseline", "added", "compacted")
HEAD_INT_KEYS = ("schema", "baseline", "added", "compacted")

#: SINGLE-SOURCED IN `grammar` (lc-40), together with the three line shapes
#: below: `ledger.py` carried its own literal of this heading and its own copy
#: of `_HEAD_LINE`, and every writer that scans for a block boundary spelled
#: the heading again by hand. Re-exported under the original private names so
#: the readers in this file and in `verbs.py` keep working unchanged.
ARCHIVE_HEADING = grammar.ARCHIVE_HEADING

_HEAD_LINE = grammar.HEAD_LINE
_BLOCK_HEADING = grammar.BLOCK_HEADING
_SLOT_LINE = grammar.SLOT_LINE
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
    #: `(name, raw-value, lineno)` for every amendment line, IN FILE ORDER.
    #: Held beside `slots` rather than folded into it: `slots` carries the
    #: value in force and this carries the record of how it got there, and a
    #: reader that wanted only the current value would otherwise have to know
    #: the resolution rule to get it right.
    amendments: list = field(default_factory=list)
    #: `(name, raw-value, lineno)` for every promotion line, IN FILE ORDER.
    #: Its OWN list rather than a share of `amendments`: these resolve NO
    #: slot — the grade they record moved in place — so folding them in would
    #: put lines with no slot to supersede through the resolver, and every
    #: reader of `amendments` would then be reading two kinds of act.
    promotions: list = field(default_factory=list)

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
    while i < len(lines) and not grammar.starts_section(lines[i]):
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
        # AMENDMENT LINES REPEAT BY DESIGN and are therefore routed before
        # the repeat check, never through it: an append-only edit path whose
        # second use is a shape finding is not an edit path.
        if slot == AMEND_REASON or slot.startswith(AMEND_PREFIX):
            current.amendments.append((slot, val, lineno))
            seen_order.append(slot)
            continue
        # PROMOTION LINES REPEAT TOO, and for the same reason: a desk that
        # judges an item twice writes two records, and the second one erasing
        # the first is the edit path law 8 exists to keep out of this file.
        if slot in PROMOTION_LINES:
            current.promotions.append((slot, val, lineno))
            seen_order.append(slot)
            continue
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
               if s not in SLOTS and s not in DONE_ONLY_SLOTS
               and not _is_amend_line(s) and s not in PROMOTION_LINES]
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

    # THE CLOSURE REASON CARRIES ITS DATE, checked on the same half the
    # amendment and promotion lines are checked on and for the same reason: a
    # closure record nobody can place in time is a claim about a closure
    # rather than a record of one. Its own verdict rather than a branch inside
    # another (lc-44): the closed-body slots are optional, so a check folded
    # into one of them would only run when that one was present.
    closed_reason = item.slots.get(CLOSED_REASON)
    if closed_reason is not None and not _AMEND_VALUE.match(closed_reason):
        out.problems.append((
            "item_shape", item.line,
            f"block {item.ident!r}: `{CLOSED_REASON}:` does not open with its "
            f"ISO date: {closed_reason[:60]!r}. A closure records WHEN the "
            "item left; undated it is prose beside a grade."))

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

    _resolve_amendments(out, item, seen_order)
    _check_promotions(out, item, seen_order)
    out.items.append(item)


def _is_amend_line(name: str) -> bool:
    return name == AMEND_REASON or name.startswith(AMEND_PREFIX)


def _check_promotions(out: Parsed, item: Item, seen_order: list) -> None:
    """Validate the block's promotion lines. They resolve NOTHING.

    NOTHING TO RESOLVE IS THE POINT, and it is what separates this from
    `_resolve_amendments`: a promotion moved `grade` IN PLACE, so the slot
    already says what the judgment decided. These lines record WHO decided it
    and WHY — facts the fixed slots have no room for, and which no reader
    should have to reconstruct from a diff.

    Checked, though, on both halves the amendment lines are checked on: the
    ISO date every appended line opens with, and the ORDER that keeps an
    appended line out of the fixed slots.

    THE FIXED RUN IS `SLOTS`, AND NOT `SLOTS + DONE_ONLY_SLOTS`. The
    closed-body slots are themselves APPENDED — `item close` writes
    `blocker-moot:` onto a body it has already moved, after whatever the
    block accumulated while it was live. Counting them as fixed makes the
    ordinary close of a promoted item a finding: measured here 2026-08-27, a
    promoted item closed over a moot decision reported "carries a promotion
    line among the fixed slots" about a file the tool itself had just
    written correctly. A guard that fires on legitimate work stops the lane
    (R11), so the predicate names the run it actually means — the block's
    own seven slots, which are the values an appended line could be read as
    superseding. A promotion line among THOSE still fires.
    """
    if not item.promotions:
        return

    fixed_at = [i for i, s in enumerate(seen_order) if s in SLOTS]
    promo_at = [i for i, s in enumerate(seen_order) if s in PROMOTION_LINES]
    if fixed_at and promo_at and min(promo_at) < max(fixed_at):
        out.problems.append((
            "item_shape", item.line,
            f"block {item.ident!r} carries a promotion line among the fixed "
            "slots. The record of a judgment is APPENDED after the block's "
            "own slots, so the block reads as what it says, then who judged "
            "it so."))

    for name, raw, lineno in item.promotions:
        if not _AMEND_VALUE.match(raw):
            out.problems.append((
                "item_shape", lineno,
                f"block {item.ident!r}: the promotion line {name!r} on line "
                f"{lineno} does not open with its ISO date: {raw[:60]!r}. A "
                "promotion records WHEN the desk judged; undated it is a "
                "claim about a judgment nobody can place in time."))


def _resolve_amendments(out: Parsed, item: Item, seen_order: list) -> None:
    """Validate the block's amendment lines and put the value IN FORCE into
    `item.slots`.

    RESOLVED HERE RATHER THAN AT EVERY READER, and that is the whole reason
    the amendment is a slot-line and not a second block: `item ready`, the
    head, the retire walk and the shape check all read `slots`, and a reader
    that had to know the resolution rule would be a reader that could get it
    wrong. The RAW lines stay on `item.amendments`, so what the block used to
    say is never lost — which is the property the append-only ethic is about.

    LAST WINS, because the file is append-only and therefore chronological.
    Order is read off the FILE rather than off the dates: two amendments made
    on one day carry one date, and a sort by that date would put them in an
    order nobody wrote.

    THE FIXED RUN IS `SLOTS`, AND NOT `SLOTS + DONE_ONLY_SLOTS` — the same
    predicate `_check_promotions` uses, for the same reason (lc-42). The
    closed-body slots are themselves APPENDED: `item close` writes
    `blocker-moot:` onto a body it has already MOVED, after whatever that body
    accumulated while it was live. Counting them as fixed makes the ordinary
    close of an AMENDED item a finding — the close puts `blocker-moot:` below
    the amendment group, so `max(fixed_at)` lands past every amendment and the
    check reports a reordering about a file the tool itself just wrote
    correctly. Observed n=2 in a live carrier (dotfiles' done home, df-75 and
    df-64, both amended by the wave-4 grade pass and then closed). A guard that
    fires on legitimate work stops the lane (R11), so the predicate names the
    run it actually means — the block's own seven slots, which are the values
    an appended line could be read as SUPERSEDING. That is also this check's
    own stated rationale: a `blocker-moot:` line supersedes nothing, so an
    amendment sitting above it reads as nothing. An amendment among the seven
    still fires.
    """
    if not item.amendments:
        return

    # ORDER: the group follows the fixed slots. A superseding line ABOVE the
    # value it supersedes reads, to a human, as the value being superseded —
    # the diff would show the correction where the original belongs.
    fixed_at = [i for i, s in enumerate(seen_order) if s in SLOTS]
    amend_at = [i for i, s in enumerate(seen_order) if _is_amend_line(s)]
    if fixed_at and amend_at and min(amend_at) < max(fixed_at):
        out.problems.append((
            "item_shape", item.line,
            f"block {item.ident!r} carries an amendment line among the fixed "
            "slots. Amendments are APPENDED after the block's own slots, so "
            "the block reads as what it said, then what it now says."))

    for name, raw, lineno in item.amendments:
        m = _AMEND_VALUE.match(raw)
        if not m:
            out.problems.append((
                "item_shape", lineno,
                f"block {item.ident!r}: the amendment line {name!r} on line "
                f"{lineno} does not open with its ISO date: {raw[:60]!r}. An "
                "amendment records WHEN the value changed; undated it is an "
                "in-place rewrite with a longer file."))
            continue
        value = m.group(2)
        if name == AMEND_REASON:
            continue
        slot = name[len(AMEND_PREFIX):]
        if slot not in AMENDABLE_SLOTS:
            out.problems.append((
                "item_shape", lineno,
                f"block {item.ident!r}: {name!r} on line {lineno} amends "
                f"{slot!r}, which is not one of the amendable slots "
                f"({', '.join(AMENDABLE_SLOTS)}). `grade` moves by judgment "
                "through `item park`, `item close` and the desk's re-grade, "
                "never by amendment."))
            continue
        if slot not in item.slots:
            out.problems.append((
                "item_shape", lineno,
                f"block {item.ident!r}: {name!r} on line {lineno} amends a "
                f"slot the block does not carry. An amendment SUPERSEDES a "
                "value; with nothing to supersede it is an addition wearing a "
                "correction's clothes."))
            continue
        problem = slot_value_problem(slot, value)
        if problem:
            out.problems.append(("item_shape", lineno, problem))
            continue
        item.slots[slot] = value


def check_ids(parsed: Parsed, prefix: str | None) -> list:
    """Ids are `<declared-prefix>-<n>`, checked against the DECLARATION.

    Read from the declaration rather than inferred from the file: inferring
    the prefix from the ids present would make any consistent corruption look
    correct, which is the same-parentage defect in miniature.
    """
    if not prefix:
        return []
    pat = grammar.id_re(prefix)
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
    if prefix and grammar.id_re(prefix).match(v):
        return "item", v
    return None, ""


# --- writing: the shape, spelled in exactly one place ------------------------

def render_block(ident: str, slots: dict) -> str:
    """One item block. THE ONLY place the on-disk shape is spelled.

    Slot ORDER comes from `SLOTS`, never from the caller's dict, so a caller
    that builds its mapping in another order cannot write a file the shape
    check then reports as out of order.
    """
    out = [grammar.render_heading(ident)]
    for slot in SLOTS:
        out.append(grammar.render_slot(slot, slots[slot]))
    return "\n".join(out) + "\n"


def render_amendment(date: str, reason: str, updates: dict) -> list:
    """The lines ONE amendment act appends. The only place the shape is spelled.

    The reason opens the group and the superseding slot-lines follow in
    `SLOTS` order, so a group is readable as one act rather than as loose
    lines that happen to share a date.
    """
    lines = [f"{AMEND_REASON}: {date} {reason}"]
    for slot in AMENDABLE_SLOTS:
        if slot in updates:
            lines.append(f"{AMEND_PREFIX}{slot}: {date} {updates[slot]}")
    return lines


def render_promotion(date: str, by: str, reason: str) -> list:
    """The lines ONE promotion act appends. The only place the shape is spelled.

    The reason opens the group, exactly as it does for an amendment, so the
    two appended kinds read the same way down the block: what was decided,
    then by whom.
    """
    return [f"{PROMOTE_REASON}: {date} {reason}",
            f"{PROMOTED_BY}: {date} {by}"]


def append_amendment(text: str, ident: str, date: str, reason: str,
                     updates: dict):
    """Append one dated amendment group to a LIVE block. `(text, found)`.

    APPENDED, never substituted: `_set_slots` rewrites a slot line in place
    and is the right shape for a state transition the tool owns end to end
    (`item park`'s grade). A correction to a value a desk wrote is a
    different act — the earlier line is evidence of what was believed, and
    an edit path that deleted it would leave the carrier unable to say it
    had ever been wrong.
    """
    return _append_to_block(text, ident,
                            render_amendment(date, reason, updates))


def append_promotion(text: str, ident: str, date: str, by: str, reason: str):
    """Append one dated promotion record to a LIVE block. `(text, found)`.

    The GRADE is not written here — `item promote` moves it in place. This
    writes only the record the grade cannot hold, which is why the two acts
    are one write of one buffer at the call site rather than two writes of
    the file: a crash between them would leave a grade nobody judged, or a
    judgment of a grade that never moved.
    """
    return _append_to_block(text, ident, render_promotion(date, by, reason))


def _append_to_block(text: str, ident: str, body: list):
    """Append `body` inside one LIVE block, after everything it already has.

    ONE WALK FOR BOTH APPENDED KINDS. The end-of-block search below has a
    subtlety — backing over the blank lines that separate this block from the
    next — and a second copy of it would drift from this one silently: the
    copy that stopped backing up would land its lines in the GAP, where they
    parse as belonging to the following block.

    The LIVE section only: everything from the archive heading on is held
    verbatim, and a pre-migration body has nothing to append to.
    """
    lines = text.split("\n")
    cut = len(lines)
    for i, ln in enumerate(lines):
        if ln.strip() == ARCHIVE_HEADING:
            cut = i
            break
    start = None
    for i in range(cut):
        m = _BLOCK_HEADING.match(lines[i])
        if m and m.group(1) == ident:
            start = i
            break
    if start is None:
        return text, False
    end = cut
    for i in range(start + 1, cut):
        if _BLOCK_HEADING.match(lines[i]):
            end = i
            break
    # Back over the blank lines that separate this block from the next, so
    # the group lands INSIDE the block rather than in the gap after it.
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    return "\n".join(lines[:end] + list(body) + lines[end:]), True


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
    for p in parsed:
        if p is None:
            continue
        for it in p.items:
            n = grammar.id_number(prefix, it.ident)
            if n is not None:
                used.add(n)
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


def check_blocker_targets(items_parsed: Parsed, done_parsed: Parsed | None,
                          out, done_unreadable: str | None = None,
                          prefix: str | None = None) -> int:
    """An item-id blocker over the CARRIER: does the id it names exist?

    ITS OWN VERDICT, never a branch inside `check_move_integrity` above.
    That function ends `if both: return FINDING` / else print the ok line, so
    a failure branch folded into it would delete "move integrity: CLEAN" from
    every report in which this fired — two questions collapsed into one
    answer, and the quieter one disappears.

    THE WRITE PATH IS NOT THE ONLY PATH, which is the whole reason this
    exists beside `verbs._check_blocker`. That one runs at `item add` and
    `item park`; a merge, a hand edit, or a blocker whose target was renamed
    after the fact all reach the file without passing it. Measured, by
    accident and with a real mistake: lc-14 was written `blocked-by: lc-15`
    before lc-15 existed and BOTH `item check` and `kind check` reported
    CLEAN. The consequence is a permanent silent park — the item never
    surfaces in `item ready` because it reads as blocked, and nothing ever
    says the blocker is fictional, so it can neither drain nor be noticed.

    THE OTHER THREE FORMS RESOLVE AGAINST NOTHING BY DESIGN and must not
    fire. `decision <question>` sits in the operator's court, `evidence
    <predicate>` in the machine's, and NONE waits for nothing; none of them
    names an id, so none of them has a target to dangle. A check that could
    not tell them apart from a dangling id would fire on legitimate work,
    which is the repair that stops the lane (R11). `classify_blocker` is what
    tells them apart, and it is the SAME function the write path uses — a
    second reading of the closed edge vocabulary would disagree with the
    first exactly where it matters.

    BOTH HOMES, because an item-id blocker RESOLVES on its target's DONE: a
    blocker naming a closed item is a wait that has been answered, not a
    dangling one. Without the done home the answer is COULD NOT VERIFY —
    reading the live home alone would report every such blocker as dangling,
    which is the same over-fire one homeless step away.

    THE SAME REACH AS THE WRITE PATH — lc-29, and it was not true before it.
    The two sides now agree on what an item-id blocker RESOLVES AGAINST: its
    target's DONE. `verbs._check_blocker` refuses both a blocker naming an id
    no home holds and one naming a DROPPED target, at all three of its doors,
    and the `item ready` resolver answers the same two; this check asks both
    questions over the carrier. They are ONE refusal because they are one
    failure: an id no home holds can never reach DONE and a DROPPED one never
    will, so each is the same PERMANENT SILENT PARK, differing only in whether
    the target was never there or is there and buried. The earlier asymmetry
    meant a blocker the write path refuses outright could sit in the file
    forever with the only check that reads the file calling it CLEAN.

    lc-28 built this to EXISTENCE and SAID SO — in the docstring and in the ok
    line — rather than leaving the narrowness implied. That stated reach is
    what made the gap bookable (lc-29) instead of invisible, and it is why
    this paragraph is part of the change rather than commentary on it: an
    assurance outliving its predicate is what stops anyone looking.
    """
    typed = []
    untypeable = []
    for it in items_parsed.items:
        raw = (it.slots.get("blocked-by") or "").strip()
        if not raw or raw == BLOCKER_NONE:
            continue
        kind, detail = classify_blocker(raw, prefix)
        if kind == "item":
            typed.append((it, detail))
        elif not prefix:
            untypeable.append(it)

    if untypeable:
        out("COULD NOT VERIFY: no `id-prefix` in the declaration, so an "
            f"item-id blocker on {len(untypeable)} block(s) cannot be told "
            "from prose that resembles one, and none was resolved.")
        return exits.COULD_NOT_VERIFY
    if not typed:
        return exits.CLEAN
    if done_parsed is None:
        out(f"COULD NOT VERIFY: {len(typed)} item-id blocker(s) name an id, "
            "and the done home could not be read to confirm it exists. "
            f"{done_unreadable or ''}")
        return exits.COULD_NOT_VERIFY

    known = {it.ident for it in items_parsed.items} | {
        it.ident for it in done_parsed.items}
    buried = {it.ident for it in done_parsed.items if it.grade == "DROPPED"}
    # ONE LIST, TWO MESSAGES — not two lists with two verdicts. The roster
    # carries this as ONE row (`dangling_reference_carrier`), so one exit
    # answer is what a reader can act on; a second verdict beside it would
    # split a refusal the design keeps whole and would need its own plant,
    # control and §3.9 line to say anything. The REPAIR differs between the
    # two, which is why the messages do.
    dangling = [(it, detail) for it, detail in typed
                if detail not in known or detail in buried]
    for it, detail in dangling:
        if detail not in known:
            out(f"FINDING [dangling_reference] line {it.line}: block "
                f"{it.ident!r} is blocked by {detail!r}, an id NEITHER home "
                "holds. A blocker pointing at nothing reads exactly like one "
                "pointing at live work and it never resolves: the block never "
                "surfaces in `item ready` because it reads as blocked, and "
                "nothing else ever says the wait is fictional — a permanent "
                "silent park. Point it at a real id, or retype the blocker to "
                "the court it actually sits in.")
        else:
            out(f"FINDING [dangling_reference] line {it.line}: block "
                f"{it.ident!r} is blocked by {detail!r}, which is DROPPED. An "
                "item-id blocker resolves on its target's DONE; a dropped "
                "target never reaches DONE, so this blocker can only expire, "
                "never clear — the same permanent silent park as an id no "
                "home holds, one grade over. The write path refuses this "
                "blocker outright; a merge or a hand edit reaches the file "
                "without passing it. Point it at a live id, or retype the "
                "blocker to the court it actually sits in.")
    if dangling:
        return exits.FINDING
    out(f"blocker targets: CLEAN — {len(typed)} item-id blocker(s), every id "
        f"resolved in one of the two homes and none of them DROPPED. The "
        "reach is the write path's: an id-blocker resolves on its target's "
        "DONE, so a target that cannot reach DONE is refused here too.")
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

#: Every run of digits, for the identity normalization below.
_DIGIT_RUN = re.compile(r"\d+")


@dataclass(frozen=True)
class Finding:
    """One shape finding, as DATA beside the line the check prints.

    The check used to emit findings through `out` and return nothing but an
    exit code, so a second reader — `item check --staged`, which must say
    which findings are NEW — had only the rendered line to work from. That
    line carries no block ident (a `parsed.problems` tuple is
    `(row, line, message)` by construction, items.py's `Parsed.problems`),
    and it carries the carrier's BASENAME rather than its path. Parsing it
    back would be a comparison over rendered text standing in for a
    comparison of bodies.

    So the check builds these and renders FROM them: one source, and the
    printed line is `render()` of this object rather than a sibling
    f-string that can drift from it.
    """
    row: str
    #: The carrier as the printed line names it — its basename.
    name: str
    line: int
    msg: str
    #: The block this finding sits in, or None for a finding that belongs to
    #: no block (a head line, a line before the first block).
    ident: str | None = None

    def render(self) -> str:
        return f"FINDING [{self.row}] {self.name}:{self.line}: {self.msg}"

    def identity(self, carrier_path: str) -> tuple:
        """What makes two findings THE SAME finding across a staged edit.

        THE LINE NUMBER IS NOT IN IT, and that is the load-bearing decision:
        a staged block inserted above a pre-existing one shifts every line
        below it, so a line-keyed identity reports the whole carrier as new
        — which is the gate-fires-on-legitimate-work class (law 11). The
        message's DIGITS go the same way and for the same reason: several
        messages quote the line number back.

        The ident is what discriminates two blocks carrying the same defect,
        whose normalized messages are otherwise equal.
        """
        return (self.row, carrier_path, self.ident,
                _DIGIT_RUN.sub("#", self.msg))


def _owning_ident(parsed: Parsed, line: int) -> str | None:
    """The block a line sits in: the last block STARTING at or above it.

    DERIVED, not read: a `Parsed` item records where it starts and not where
    it ends, so this is the only answer available from the parse. It is
    sound for the use it has — a finding's identity — because a finding
    below the last block's start belongs to that block, and one above the
    first block's start belongs to the head, which is `None`.
    """
    owner = None
    for it in parsed.items:
        if it.line <= line:
            owner = it.ident
        else:
            break
    return owner


def check_file(path: Path, out, prefix: str | None = None, *,
               text: str | None = None, collect: list | None = None) -> int:
    """The pre-commit shape check over one carrier file.

    `text` runs the check over a body that is not on disk — the git INDEX's,
    for `--staged`. `collect` receives every `Finding` the run produced, in
    printed order. Neither changes what the check FINDS or prints; they are
    the reporting mode's two handles on a check that otherwise only speaks
    through `out`.
    """
    if text is None:
        if not path.exists():
            out(f"COULD NOT VERIFY: no carrier at {path}. An absent file and an "
                "empty one are not the same answer, and neither is clean.")
            return exits.COULD_NOT_VERIFY
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            out(f"COULD NOT VERIFY: {path} could not be read ({exc!r}).")
            return exits.COULD_NOT_VERIFY

    def finding(row, line, msg, ident=None):
        f = Finding(row, path.name, line, msg, ident)
        if collect is not None:
            collect.append(f)
        out(f.render())

    parsed = parse(text)
    for row, line, msg in parsed.problems:
        finding(row, line, msg, _owning_ident(parsed, line))

    if parsed.refused:
        out(f"item check: {exits.word(exits.FINDING)} — the body was not "
            "parsed, so no count below would have meant anything.")
        return exits.FINDING

    bad_ids = check_ids(parsed, prefix)
    for ident, line in bad_ids:
        finding("item_shape", line,
                f"id {ident!r} does not match the declared prefix "
                f"{prefix!r} — ids are `{prefix}-<n>` and immutable across "
                "moves.", ident)

    untyped, blockers_unverified = check_parked_blockers(parsed, prefix)
    for ident, line, value in untyped:
        finding("parked_without_typed_blocker", line,
                f"block {ident!r} is PARKED with an untyped `blocked-by`: "
                f"{value!r}. The types are closed — "
                f"`<{prefix or 'prefix'}-<n>>`, `decision <question>`, "
                "`evidence <predicate>` — because an aging item is routed "
                "by WHOSE COURT it sits in, and prose sits in nobody's. A "
                "parked item nothing can re-evaluate is a drop waiting to "
                "happen quietly.", ident)
    if blockers_unverified:
        out(f"COULD NOT VERIFY: {blockers_unverified}")

    unk_counts, unk_misplaced = unknown_slots(parsed)
    for ident, line, slot in unk_misplaced:
        finding("unknown_slot_misplaced", line,
                f"block {ident!r} holds UNKNOWN in `{slot}`. UNKNOWN is the "
                "migration's declared marker for a slot nobody ever "
                "recorded, and the grade workflow fills it — but a grade is "
                "one of the five and a blocker is typed or NONE, so UNKNOWN "
                "there is a value nothing can ever fill in.", ident)
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
        finding("ready_with_unknown_slot", line,
                f"block {ident!r} is READY and still holds UNKNOWN in "
                + ", ".join(f"`{s}`" for s in slots_)
                + ". READY is the desk's judgment that a fresh context could "
                  "execute this now, and a slot nobody has ever written is "
                  "the one thing that judgment cannot have been made over.",
                ident)
    if ready_unknown:
        code = exits.worst([code, exits.FINDING])

    out(f"item check: {exits.word(code)} — "
        f"{len(parsed.problems) + len(bad_ids) + len(untyped) + len(unk_misplaced) + len(ready_unknown)}"
        f" shape finding(s), {len(c['unknown'])} unclassifiable grade word(s).")
    return code


def cmd_item_slots(args, out, path: Path) -> int:
    """Report one block's effective fixed slots without changing its carrier.

    `parse` closes each positional block and calls `_resolve_amendments`, so
    `item.slots` is the one existing answer to which amendment is in force.
    Reading that mapping is intentionally not a scan for a slot word in prose:
    a slot's place in the parsed block, not a word discussed by its body,
    anchors this future checker-facing interface.
    """
    if not path.exists():
        out(f"COULD NOT VERIFY: no carrier at {path}. An absent file and an "
            "empty one are not the same answer, and neither has slots.")
        return exits.COULD_NOT_VERIFY
    try:
        parsed = parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        out(f"COULD NOT VERIFY: {path} could not be read ({exc!r}).")
        return exits.COULD_NOT_VERIFY

    item = next((it for it in parsed.items if it.ident == args.ident), None)
    if item is None:
        out(f"FINDING [unknown_item] no live block {args.ident!r} in "
            f"{path.name}.")
        return exits.FINDING

    slots = {slot: item.slots.get(slot, "") for slot in SLOTS}
    if args.json:
        out(json.dumps({"ident": item.ident, "slots": slots}, ensure_ascii=False))
    else:
        for slot in SLOTS:
            out(f"{slot}: {slots[slot]}")
    return exits.CLEAN


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

#: THE `blocker-moot:` RECORD FOR AN ITEM-ID BLOCKER, in the two states a
#: close can honestly report about one (lc-90). Spelled HERE and nowhere else,
#: for the reason `ledger.moot_answer` is spelled once: `verbs.py` writes the
#: record and this module's discharge reads it back by EQUALITY, so a second
#: spelling on either side would drift silently and the discharge would stop
#: recognising the very line the close had just written.
#:
#: TWO FORMS BECAUSE THE TWO FACTS ARE DIFFERENT, and collapsing them would
#: make the record lie in one direction: a target that CLOSED answered the
#: wait, while a DROPPED closing item abandoned it unanswered. The second form
#: claims no discharge — it records that the waiter is gone, which is the only
#: thing a drop establishes.
_ITEM_MOOT_ANSWERED = "{ident} (the blocker closed before this item did)"
_ITEM_MOOT_ABANDONED = "{ident} (never resolved; this item was dropped)"


def item_moot_record(ident: str, *, abandoned: bool) -> str:
    """The `blocker-moot:` value a close writes for the item-id blocker `ident`.

    The single writer of this shape, called by `verbs.cmd_item_close` rather
    than composed there — see the note above.
    """
    shape = _ITEM_MOOT_ABANDONED if abandoned else _ITEM_MOOT_ANSWERED
    return shape.format(ident=ident)


#: THE `blocker-moot:` RECORD FOR A `decision` BLOCKER THE LEDGER ALREADY
#: ANSWERS (lc-55) — the THIRD fact a close can honestly report about a
#: blocker, beside `item_moot_record`'s two, and here for the same reason
#: those two are separate: one record that covered both would make the body
#: say the question died unanswered while the ledger holds its answer.
#:
#: THE UNANSWERED FORM STAYS THE BARE QUESTION and is deliberately not moved
#: here: every record already sitting in a closure home carries it, and
#: `_moot_discharges` reads it back by equality against the blocker's own
#: detail. This form is ADDED beside it, never in place of it.
#:
#: WRITING NOTHING WAS THE OTHER CANDIDATE AND IT IS WRONG. `move_to_done`
#: clears the base `blocked-by:` LINE, but an `amended-blocked-by:` line
#: survives the close untouched (lc-90) — so a close that recorded nothing
#: left an ANSWERED blocker standing in the closure home with nothing to
#: discharge it, and the next `item check` reported `blocked_in_done_home`
#: against a body `item amend` correctly refuses to repair. Measured on a
#: private clone while building lc-55's first half, which wrote no record.
_DECISION_MOOT_ANSWERED = ("{question} (answered in the ledger before this "
                           "item closed)")


def decision_moot_record(question: str) -> str:
    """The `blocker-moot:` value a close writes for an ANSWERED decision.

    The single writer of this shape, called by `verbs.cmd_item_close` rather
    than composed there — the discharge below reads it back by EQUALITY, so a
    second spelling on either side would drift and the discharge would stop
    recognising the very line the close had just written.
    """
    return _DECISION_MOOT_ANSWERED.format(question=(question or "").strip())


def _moot_discharges(item: Item, detail: str, kind: str = "decision") -> bool:
    """Did this body's closure record the very blocker `detail` names (lc-48)?

    EQUALITY, never containment or a normalised compare. The moot record is
    written by `item close` from the blocker's own DETAIL, so the two strings
    have one producer and an exact match is available — and a looser predicate
    would discharge a blocker on a moot record about something else, which is
    the one case this check exists to keep firing. A substring test here would
    be the prefix match in an equality's costume: any longer question that
    happens to begin with a shorter one would read as discharged.

    TWO TYPES REACH THIS, and the earlier sentence here said one (lc-90). It
    claimed an `<item-id>` blocker "resolves mechanically on its target's
    DONE" — nothing resolves it: `move_to_done` clears the base `blocked-by:`
    LINE, and where an `amended-blocked-by:` line supersedes that line the
    EFFECTIVE blocker survives the close untouched, which is how a body that
    did arrive by a close was still reported here. So a close now records an
    item-id blocker too, in `item_moot_record`'s two forms, and this discharges
    on either of them — for the id the effective blocker actually names, which
    is what keeps a record about some other item from clearing this one.
    An `evidence` blocker is still annotated by no close and still has no
    record to be discharged by; the type test below is what keeps it a finding.

    THE `decision` TYPE HAS TWO RECORD FORMS NOW (lc-55), and both discharge
    for the question the effective blocker actually names: the bare question,
    written when the close makes an unanswered question moot, and
    `decision_moot_record`'s answered form, written when the ledger already
    answers it. Both are compared by EQUALITY against a record built from THIS
    body's own detail, so a record about another question still discharges
    nothing — the widening is one more exact shape, never a looser predicate.
    """
    moot = (item.slots.get("blocker-moot") or "").strip()
    if not moot:
        return False
    if kind == "item":
        target = (detail or "").strip()
        return bool(target) and moot in (
            item_moot_record(target, abandoned=False),
            item_moot_record(target, abandoned=True))
    if kind != "decision":
        return False
    question = (detail or "").strip()
    return moot in (question, decision_moot_record(question))


def check_done_file(path: Path, out, prefix: str | None = None, *,
                    text: str | None = None,
                    collect: list | None = None) -> int:
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
        operator's queue after the item that asked it is gone.
      * the ARCHIVE is skipped, as everywhere else: those bodies predate the
        tool and were never meant to satisfy a fixed-slot shape.

    WHAT `item close` ACTUALLY DOES, and the earlier sentence here said
    otherwise (lc-48): it clears the `blocked-by:` SLOT LINE and records the
    question as `blocker-moot:`. It does NOT clear the EFFECTIVE value, and it
    must not — an `amended-blocked-by:` line resolves last-wins OVER the slot
    line, and removing that amendment is precisely the in-place rewrite the
    append-only model forbids. So an amended-then-closed body carries
    `blocked-by: NONE` with a live decision blocker resolving above it, and
    this check read that as a defect on the exact body the close had annotated
    correctly (measured on dotfiles' done home, df-141, 2026-08-27). The
    docstring and the code disagreed and the CODE was right; the check is what
    changed. The DISCHARGE below is that repair, and it is deliberately narrow:
    the moot record must name the very question the effective blocker names.

    THE SAME SURVIVAL REACHES THE OTHER TYPES, and lc-48 repaired only the one
    it had measured (lc-90). An amended `<item-id>` blocker survives the close
    exactly as the decision one did — measured at 11a8c1d on a scratch repo:
    `item close` exited 0 and the next `item check` reported this row against a
    body the close had just written. The close now records that type too
    (`item_moot_record`) and the discharge above recognises it. An `evidence`
    blocker is the REMAINDER, left as it stands rather than repaired blind: it
    reaches this row by the same route and the same measurement, but what a
    close should say about a predicate nobody re-evaluated is a design question
    this repair did not settle — so for that one type the sentence below still
    over-reads, and the body it names may well have arrived by a close.
    """
    if text is None:
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

    def finding(row, line, msg, ident=None):
        f = Finding(row, path.name, line, msg, ident)
        if collect is not None:
            collect.append(f)
        out(f.render())

    parsed = parse(text)
    for row, line, msg in parsed.problems:
        finding(row, line, msg, _owning_ident(parsed, line))
    if parsed.refused:
        out(f"done-home check: {exits.word(exits.FINDING)} — the body was not "
            "parsed.")
        return exits.FINDING

    bad_ids = check_ids(parsed, prefix)
    for ident, line in bad_ids:
        finding("item_shape", line,
                f"id {ident!r} does not match the declared prefix "
                f"{prefix!r}.", ident)

    open_here = [it for it in parsed.items if it.grade not in GRADES_CLOSED]
    for it in open_here:
        finding("open_grade_in_done_home", it.line,
                f"block {it.ident!r} is graded {it.grade or '(none)'} in the "
                "CLOSURE home. Every body here left the carrier by a close, "
                "so its grade is DONE or DROPPED; an open grade here is a "
                "body that arrived by some other path — and conservation "
                "counts it on the closed side whatever its grade says.",
                it.ident)

    blocked = []
    for it in parsed.items:
        kind, detail = classify_blocker(it.slots.get("blocked-by", ""), prefix)
        # THE PREDICATE LINE BELOW IS AN ANCHOR `tools/prove-rows.py` records
        # for this row, so the discharge is a branch INSIDE it rather than a
        # `continue` above it: an equivalent rewrite would leave that
        # arrangement resolving nothing, and a mutation whose anchor has
        # moved reports COULD NOT VERIFY — which is honest and is still a
        # row this repo can no longer prove.
        if kind not in (None, "none"):
            if _moot_discharges(it, detail, kind):
                continue
            blocked.append(it)
            finding("blocked_in_done_home", it.line,
                    f"block {it.ident!r} is closed and still carries "
                    f"`blocked-by: {it.slots.get('blocked-by', '')}`. A "
                    "closed item waits for nothing, and this body carries no "
                    "`blocker-moot:` naming that question — so it did not "
                    "arrive here by a close, which is the path that records "
                    "the question as moot precisely so the operator's "
                    "decision queue does not keep listing it after the item "
                    "that asked it is gone.", it.ident)

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


# --- the shape repair (lc-129) -----------------------------------------------

#: THE SPLIT IS THE WHOLE VERB. A wrapped value and an appended line sitting
#: among the fixed slots are damage to a block's SHAPE: every word survives the
#: repair, and the transformation is total on its input. A missing slot, an
#: unknown slot and a closed body still carrying its blocker are damage to its
#: CONTENT, where repairing means supplying a value nobody wrote — which is the
#: failure this verb must not have. So those are LISTED for a desk pass and
#: their bodies are not touched.
#:
#: THE CLASS NAMES ARE THE VERB'S OUTPUT VOCABULARY, closed and declared here
#: rather than spelled at each emit site: the desk pass reads the list, and a
#: fourth name improvised at a fourth site is a grade word nobody counts.
JUDGMENT_MISSING = "missing-slot"
JUDGMENT_UNKNOWN = "unknown-slot"
JUDGMENT_BLOCKED_CLOSED = "closed-still-blocked"
#: A continuation line with NO slot line above it to join to — the one wrapped
#: value the mechanical half cannot repair, because choosing a host for it
#: would be choosing which slot the words belong to. Listed, never guessed.
JUDGMENT_UNJOINABLE = "unjoinable-continuation"


@dataclass
class ShapeRepair:
    """What one pass over a carrier changed, and what it refused to change."""
    text: str = ""
    #: `(ident, slot, lineno, continuation-lines-joined)`
    joins: list = field(default_factory=list)
    #: `(ident, line-name, lineno)`
    moves: list = field(default_factory=list)
    #: `(ident, one of the JUDGMENT_* words, detail)`
    judgments: list = field(default_factory=list)

    @property
    def repaired(self) -> bool:
        return bool(self.joins or self.moves)


def _appended_line(name: str) -> bool:
    """Is `name` a line the block ACCUMULATED rather than one of its seven?

    The three kinds ride one predicate because the checker already treats them
    as one: `_resolve_amendments`, `_check_promotions` and `_close_block`'s
    `tail_out_of_place` each fire on the same arrangement — an appended record
    sitting among the values it could be read as superseding. A repair that
    moved one kind and left its twins would leave two thirds of that finding
    standing, under a verb whose report said the block was repaired.
    """
    return (_is_amend_line(name) or name in PROMOTION_LINES
            or name in DONE_ONLY_SLOTS)


def _entry_kind(name: str) -> str:
    if name in SLOTS:
        return "fixed"
    if _appended_line(name):
        return "appended"
    return "other"


def repair_shape(text: str, prefix: str | None = None) -> ShapeRepair:
    """Join wrapped slot values; move appended lines below the fixed slots.

    THE ARCHIVE AND THE HEAD PASS THROUGH VERBATIM. Those bodies predate the
    tool and are skipped by every shape check here; joining their wrapped prose
    would rewrite history the parser deliberately does not grade.

    NOTHING IS PARSED AND RE-RENDERED. The rebuild is over the block's own
    LINES, so a value this build cannot classify still reaches the output
    character for character — which is what lets the verb repair a block that
    also carries an unknown slot without touching the unknown slot.
    """
    res = ShapeRepair()
    parsed = parse(text)
    by_ident = {}
    for it in parsed.items:
        by_ident.setdefault(it.ident, it)

    lines = text.split("\n")
    n = len(lines)
    out_lines = []
    i = 0
    while i < n and not _BLOCK_HEADING.match(lines[i]) \
            and lines[i].strip() != ARCHIVE_HEADING:
        out_lines.append(lines[i])
        i += 1

    while i < n:
        if lines[i].strip() == ARCHIVE_HEADING:
            out_lines.extend(lines[i:])
            break
        m = _BLOCK_HEADING.match(lines[i])
        if not m:
            # A line outside any block. The parser reports it; this verb has
            # no block to attach it to, so it travels unchanged.
            out_lines.append(lines[i])
            i += 1
            continue
        out_lines.append(lines[i])
        ident = m.group(1)
        start = i + 1
        i = start
        while i < n and not _BLOCK_HEADING.match(lines[i]) \
                and lines[i].strip() != ARCHIVE_HEADING:
            i += 1
        out_lines.extend(_repair_block(ident, lines[start:i], start + 1, res,
                                       by_ident.get(ident), prefix))

    res.text = "\n".join(out_lines)
    return res


def _repair_block(ident: str, body: list, first_lineno: int,
                  res: ShapeRepair, item, prefix: str | None) -> list:
    entries = []
    for off, raw in enumerate(body):
        lineno = first_lineno + off
        if not raw.strip():
            entries.append({"name": None, "kind": "blank", "lineno": lineno,
                            "lines": [raw]})
            continue
        sm = _SLOT_LINE.match(raw)
        if sm:
            name = sm.group(1)
            entries.append({"name": name, "kind": _entry_kind(name),
                            "lineno": lineno, "lines": [raw]})
            continue
        host = entries[-1] if entries else None
        if host is None or host["kind"] in ("blank", "orphan"):
            # A BLANK LINE ENDS A VALUE. A continuation after one is not
            # unambiguously the wrapped tail of the slot above it, and picking
            # a host for it would be picking which slot owns the words.
            res.judgments.append((ident, JUDGMENT_UNJOINABLE,
                                  f"line {lineno}: {raw.strip()[:60]!r}"))
            entries.append({"name": None, "kind": "orphan", "lineno": lineno,
                            "lines": [raw]})
            continue
        host["lines"].append(raw)

    for e in entries:
        if len(e["lines"]) > 1:
            joined = " ".join([e["lines"][0].rstrip()]
                              + [ln.strip() for ln in e["lines"][1:]])
            res.joins.append((ident, e["name"], e["lineno"],
                              len(e["lines"]) - 1))
            e["lines"] = [joined]

    # THE MOVE LANDS THE APPENDED LINES IMMEDIATELY AFTER THE LAST FIXED SLOT,
    # never at the end of the block — and it keeps them in FILE ORDER. Both
    # halves are the append-only ethic: `_resolve_amendments` reads LAST WINS
    # off the file, so an earlier amendment moved below a later one would
    # change which value is in force, and that is an invention, not a repair.
    fixed_at = [k for k, e in enumerate(entries) if e["kind"] == "fixed"]
    if fixed_at:
        last = max(fixed_at)
        move_at = [k for k in range(last) if entries[k]["kind"] == "appended"]
        if move_at:
            moving = set(move_at)
            head = [e for k, e in enumerate(entries[:last + 1])
                    if k not in moving]
            moved = [entries[k] for k in move_at]
            entries = head + moved + entries[last + 1:]
            for e in moved:
                res.moves.append((ident, e["name"], e["lineno"]))

    names = [e["name"] for e in entries if e["name"]]
    missing = [s for s in SLOTS if s not in names]
    if missing:
        res.judgments.append((ident, JUDGMENT_MISSING, ", ".join(missing)))
    unknown = list(dict.fromkeys(nm for nm in names
                                 if _entry_kind(nm) == "other"))
    if unknown:
        res.judgments.append((ident, JUDGMENT_UNKNOWN, ", ".join(unknown)))
    if item is not None and item.grade in GRADES_CLOSED:
        # THE SAME PREDICATE `check_done_file` USES, reached through the same
        # two calls rather than re-derived: a second reading of "is this
        # blocker discharged" would disagree with the checker about exactly
        # the bodies a desk pass is being handed.
        raw_blocker = item.slots.get("blocked-by", "")
        kind, detail = classify_blocker(raw_blocker, prefix)
        if kind not in (None, "none") and not _moot_discharges(item, detail,
                                                               kind):
            res.judgments.append((ident, JUDGMENT_BLOCKED_CLOSED, raw_blocker))

    out = []
    for e in entries:
        out.extend(e["lines"])
    return out


# --- the staged shape gate ---------------------------------------------------

#: How long a `git show` may take before the staged check calls it unreadable.
#: Bounded because the consumer is a pre-commit hook, which the harness
#: cancels at its own limit and whose output is then discarded — an unbounded
#: child there turns a gate's could-not-verify branch into silence.
_GIT_TIMEOUT = 20


def rel_to(repo: Path, path: Path) -> str:
    """A carrier's path as GIT spells it: repo-relative, forward slashes.

    `git show :<path>` reads the index only under the repo-relative spelling,
    and the declaration gives homes that way already — this is the one place
    the absolute `Ctx` path is turned back.
    """
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return path.name


def _git_blob(repo: Path, spec: str) -> tuple[str | None, str]:
    """`(text, why-not)` for one `git show <spec>` — `:<path>` is the INDEX.

    A failure is never folded into "empty": an absent blob and an empty one
    are different answers, and only the caller knows which of them is the
    defect it is looking for.
    """
    try:
        p = subprocess.run(["git", "-C", str(repo), "show", spec],
                           capture_output=True, text=True,
                           timeout=_GIT_TIMEOUT)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, f"`git show {spec}` could not run ({exc!r})"
    if p.returncode != 0:
        detail = (p.stderr or "").strip().splitlines()
        return None, (f"`git show {spec}` exited {p.returncode}"
                      + (f": {detail[0]}" if detail else ""))
    return p.stdout, ""


def _quote_block(text: str, finding: Finding) -> list:
    """The block a finding sits in, as quoted lines — its LINE if it has none.

    Quoted rather than pointed at: the consumer is a commit-time gate, and a
    line number into a body the committer is in the middle of editing is the
    one pointer that will have moved by the time they read it.
    """
    if finding.ident:
        _, body = replace_body(text, finding.ident)
        if body is not None:
            return [f"    | {ln}" for ln in body.rstrip("\n").split("\n")]
    lines = text.split("\n")
    if 1 <= finding.line <= len(lines):
        return [f"    | {lines[finding.line - 1]}"]
    return ["    | (the finding names no block and no line of this body)"]


def check_staged(repo: Path, carriers, out, err) -> int:
    """`item check --staged`: the shape findings a STAGED edit INTRODUCES.

    WHY A DIFF AND NOT THE PLAIN CHECK. A commit-time gate that refused every
    finding in the carrier would refuse every commit in a repo that carries
    any — dotfiles carries 23 — and a guard that fires on legitimate work is
    the class law 11 forbids: it trains `--no-verify`, which kills every lane
    in the hook at once. So the gate asks the narrower question the committer
    can actually answer: did THIS edit introduce a break.

    THE IDENTITY CARRIES NO LINE NUMBER (`Finding.identity`). A block staged
    above a pre-existing one shifts every line under it, and a line-keyed
    diff would then report the untouched remainder as newly broken — the
    same false fire by another route.

    `carriers` is `(repo-relative path, Path, checker, prefix)` per carrier:
    the live home takes `check_file`, the closure home `check_done_file`.
    Both are checked because both are carriers the tool owns (law 8), and a
    gate guarding one of two leaves the other's breaks reported by nothing
    while the wiring reads as covered.
    """
    silent = lambda _s: None  # noqa: E731
    unverified: list = []
    new_all: list = []
    pre_existing = 0
    unchanged: list = []
    #: Carriers whose staged body was actually scanned. Counted here and not
    #: derived from `len(carriers) - len(unverified)`: a carrier can be both
    #: graded AND carry a could-not-verify (the newly-introduced case below),
    #: so the subtraction would under-report exactly where it is read.
    graded = 0

    for rel, path, checker, prefix in carriers:
        idx_text, idx_why = _git_blob(repo, f":{rel}")
        head_text, head_why = _git_blob(repo, f"HEAD:{rel}")

        if idx_text is None and head_text is None:
            unverified.append(
                f"{rel}: readable at neither the index nor HEAD — {idx_why}; "
                f"{head_why}. The declaration names this carrier, so its "
                "absence from both is not a clean answer about the staged "
                "shape: nothing was checked.")
            continue
        if idx_text is None:
            unverified.append(
                f"{rel}: resolves at HEAD but not in the index — {idx_why}. "
                "A carrier staged for deletion has no staged body to check, "
                "and a deletion reported as 'no new findings' would be the "
                "loudest thing this gate could be silent about.")
            continue

        graded += 1
        idx_findings: list = []
        idx_code = checker(path, silent, prefix=prefix,
                           text=idx_text, collect=idx_findings)
        head_findings: list = []
        head_code = exits.CLEAN
        if head_text is not None:
            head_code = checker(path, silent, prefix=prefix,
                                text=head_text, collect=head_findings)

        # A COULD-NOT-VERIFY THE EDIT INTRODUCED is its own answer, not a
        # clean one (law 1). The check reports that state through its CODE
        # rather than through a finding line — an unclassifiable grade word
        # prints a census line, not a `FINDING` — so a gate reading only the
        # finding set would pass a staged `grade: BOGUS` in silence.
        if (idx_code == exits.COULD_NOT_VERIFY
                and head_code != exits.COULD_NOT_VERIFY):
            unverified.append(
                f"{rel}: the staged body is COULD NOT VERIFY where HEAD's is "
                f"{exits.word(head_code)} — the check could not classify "
                "something this edit introduced. Run `item check` without "
                "`--staged` for the naming line.")

        baseline = {f.identity(rel) for f in head_findings}
        for f in idx_findings:
            if f.identity(rel) in baseline:
                pre_existing += 1
            else:
                new_all.append((rel, idx_text, f))

        if head_text is not None and idx_text == head_text:
            unchanged.append(rel)

    for rel, idx_text, f in new_all:
        out(f.render())
        for ln in _quote_block(idx_text, f):
            out(ln)

    if len(unchanged) == len(carriers):
        out("staged: nothing staged for the carriers "
            + ", ".join(rel for rel, _p, _c, _x in carriers)
            + " — their index bodies equal HEAD's. A clean answer about this "
              "commit, not a could-not-verify.")

    # THE COUNTS NAME THE CARRIERS THEY COVER. A bare "0 pre-existing" beside
    # a carrier nothing graded is a pass-shaped number over an absence, which
    # is the one output this repo's three-answers law forbids outright.
    out(f"staged: {len(new_all)} NEW shape finding(s); "
        f"{pre_existing} pre-existing finding(s) carried, not reported — "
        "they are in the carrier at HEAD and this commit did not introduce "
        f"them. Counted over {graded} of {len(carriers)} declared carrier(s).")

    if unverified:
        for why in unverified:
            err(f"COULD NOT VERIFY: {why}")
        # "condition(s)", not "carrier(s)": a carrier can be scanned AND
        # still carry a could-not-verify, so counting carriers here would
        # contradict the "counted over N of M" line directly above it.
        out(f"item check --staged: {exits.word(exits.COULD_NOT_VERIFY)} — "
            f"{len(unverified)} could-not-verify condition(s), so the counts "
            "above are not a full verdict; see stderr.")
        return exits.COULD_NOT_VERIFY

    code = exits.FINDING if new_all else exits.CLEAN
    out(f"item check --staged: {exits.word(code)} — {len(new_all)} finding(s) "
        "this staged edit introduced.")
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


# --- the wave planner (lc-123) -----------------------------------------------

#: The four answers `item waves` gives about ONE item's write-set. Only the
#: first is a lane: an item whose write boundary cannot be read as this repo's
#: paths is NEVER clustered, because clustering it would assert a join over a
#: set nobody read. The other three are listed with counts and explicit zeros
#: instead — an omitted key reads exactly like "checked and clean", which is
#: the could-not-verify failure the three-answers rule forbids.
WAVE_PATHS = "path-valued"
WAVE_UNSET = "missing/UNKNOWN/NONE"
WAVE_PROSE = "prose"
WAVE_FOREIGN = "other-repo"

#: The non-lane buckets, in report order. A RUN rather than three literals at
#: the print site, so the report cannot quietly print only the ones that
#: happen to be non-empty.
WAVE_NON_PATH = (WAVE_UNSET, WAVE_PROSE, WAVE_FOREIGN)

#: A repo-relative path ENTRY. Deliberately narrow: a space, a parenthesis, a
#: semicolon or a colon means the author wrote prose or a VENUE
#: (`decision:<question>`, which `item add --write-set` accepts beside paths),
#: and prose read as a path would put an item in a lane on a boundary nobody
#: stated. A TRAILING SLASH marks a directory entry — the only directory form
#: recognised here, because deriving directory-ness from the working tree
#: would make the join depend on what happens to exist today rather than on
#: the slot the desk wrote.
_WAVE_PATH_ENTRY = re.compile(r"^[A-Za-z0-9._][A-Za-z0-9._/-]*$")


def _wave_foreign_entry(entry: str) -> bool:
    """Does this entry name a boundary OUTSIDE the repo being planned?

    `<path>@<repo>` is this carrier's own foreign form (lc-66, lc-67:
    `docs/directives/…md@cache-fix`); an absolute path, a `~` path and a `../`
    escape each name a boundary this repo's one writer does not hold. Such an
    item is not unschedulable — it is unschedulable HERE, which is a different
    sentence and the reason this bucket is its own key rather than prose.
    """
    return (entry.startswith("/") or entry.startswith("~")
            or entry.startswith("../") or entry == ".."
            or "@" in entry)


def wave_normalize(entry: str) -> str:
    """One path entry, normalized for comparison; a trailing slash SURVIVES.

    The slash is the directory marker (see `_WAVE_PATH_ENTRY`), so a
    normalizer that dropped it would silently turn `test/` — every file under
    test — into `test`, a single file nothing else names, and the whole lane
    it binds would vanish without a message.
    """
    trailing = entry.endswith("/")
    p = posixpath.normpath(entry)
    return f"{p}/" if trailing and not p.endswith("/") else p


def effective_write_set(item: Item) -> str:
    """The write-set IN FORCE for `item` — the amended value where one exists.

    THE EFFECTIVE SLOT RULE, applied here rather than re-derived: a slot's
    value is the LAST `amended-<slot>:` line where the block carries one, else
    the base slot line. `parse` already resolves it (`_resolve_amendments`,
    last-wins, order read off the file), so the rule is satisfied by reading
    `slots` and would be BROKEN by reading the block's raw lines — which is
    why this reader exists at all: a second reader that went to the raw text
    would cluster items by a write boundary the desk had already superseded.
    """
    return item.slots.get("write-set", "")


def classify_write_set(value: str):
    """`(bucket, paths, why)` for ONE effective write-set slot.

    `paths` is non-empty only for `WAVE_PATHS`; `why` is the quoted evidence
    for every other bucket. A MIXED slot — some entries paths, some not —
    lands in the non-path bucket with the count of what did parse, and is not
    clustered: a join over the parsing half would be a lane assertion resting
    on a partial read of the slot, and it would read exactly like a complete
    one.
    """
    # Deferred: `verbs` imports THIS module, so the dependency only runs one
    # way at import time. The split itself is single-sourced there on purpose
    # — `write_set_entries` is the system's existing instance of "what the
    # entries of a write-set are", sentinel handling included, and a second
    # split here would drift from the intake join's the day either moved.
    from . import verbs as verbs_mod

    raw = (value or "").strip()
    if not raw:
        return WAVE_UNSET, [], "the slot is absent or empty"
    entries = verbs_mod.write_set_entries(raw)
    if not entries:
        return WAVE_UNSET, [], f"every entry is a sentinel: {raw!r}"

    parses = [e for e in entries if _WAVE_PATH_ENTRY.match(e)]
    foreign = [e for e in entries if _wave_foreign_entry(e)]
    if foreign:
        return (WAVE_FOREIGN, [],
                f"names a write boundary outside this repo: {foreign[0]!r} "
                f"({len(parses)} of {len(entries)} entry/entries parse as "
                "repo-relative paths)")
    unparsed = [e for e in entries if not _WAVE_PATH_ENTRY.match(e)]
    if unparsed:
        return (WAVE_PROSE, [],
                f"does not parse as a path: {unparsed[0]!r} "
                f"({len(parses)} of {len(entries)} entry/entries parse as "
                "paths — a MIXED slot is not clustered on its parsing half)")
    return WAVE_PATHS, [wave_normalize(e) for e in entries], None


def wave_covers(entry: str, other: str) -> bool:
    """Does `entry` — a DIRECTORY entry — contain `other`?

    Segment-wise, never by substring: `test/` contains `test/x.py` and does
    NOT contain `testing/x.py`, which a `startswith("test")` would call a hit.
    That is the prefix-match-in-an-equality's-costume shape, and the trailing
    slash is what makes this containment a real answer rather than one.

    CONTAINMENT IS THE CONSERVATIVE DIRECTION, and it is a decision: an item
    claiming all of `test/` really does collide with one naming
    `test/test_migrate.py`, so equality alone would UNDER-join and hand two
    writers the same file in parallel — the one failure this join exists to
    prevent. Over-joining costs elapsed time and nothing else, and the lane's
    binder line names the directory entry so the desk can see the merge and
    overrule it.
    """
    if not entry.endswith("/"):
        return False
    return other == entry[:-1] or other.startswith(entry)


def wave_witnesses(a_paths, b_paths):
    """`[(key, by_containment), …]` — why two items collide, from their sets.

    The key is the path that BINDS them: the shared entry where they are
    equal, the containing directory entry where one covers the other.
    """
    hits: dict = {}
    for x in a_paths:
        for y in b_paths:
            if x == y:
                hits.setdefault(x, False)
            elif wave_covers(x, y):
                hits[x] = True
            elif wave_covers(y, x):
                hits[y] = True
    return sorted(hits.items())


def _wave_ident_key(ident: str):
    """Sort ids the way their author reads them — `lc-16` before `lc-100`.

    A plain string sort puts `lc-100` first, and a report a desk scans for its
    own item's lane is a report whose order has to be the obvious one.
    """
    prefix, _, tail = ident.rpartition("-")
    return (prefix, 0, int(tail)) if tail.isdigit() else (prefix, 1, 0, ident)


def wave_lanes(rows):
    """The connected components of the file-overlap graph.

    `rows` is `[(ident, [path, …]), …]`; a lane is
    `{"members": [ident, …], "binders": [(key, by_containment, carriers,
    covered)]}`. Members SERIALIZE (they share a file); lanes are disjoint and
    therefore parallel. Single-item lanes are lanes: an item colliding with
    nothing is the parallel case, not an omission.

    A CONTAINMENT BINDER SPLITS ITS MEMBERS IN TWO, and the split is the
    actionable half: `carriers` wrote the directory entry, `covered` were
    pulled in by it. One coarse slot can merge every otherwise-disjoint lane
    in a carrier, and a binder line that listed both sides together would show
    the merge while hiding whose slot caused it — the desk would see a giant
    lane and have nothing to sharpen.
    """
    parent = {ident: ident for ident, _ in rows}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    binders: dict = {}
    for i in range(len(rows)):
        ida, pa = rows[i]
        for j in range(i + 1, len(rows)):
            idb, pb = rows[j]
            hits = wave_witnesses(pa, pb)
            if not hits:
                continue
            ra, rb = find(ida), find(idb)
            if ra != rb:
                parent[rb] = ra
            for key, by_containment in hits:
                seen = binders.setdefault(key, [False, set()])
                seen[0] = seen[0] or by_containment
                seen[1].update((ida, idb))

    order = [ident for ident, _ in rows]
    lanes: dict = {}
    for ident in order:
        lanes.setdefault(find(ident), []).append(ident)

    owns = {ident: set(paths) for ident, paths in rows}
    out = []
    for root in dict.fromkeys(find(i) for i in order):
        members = lanes[root]
        member_set = set(members)
        rows_out = []
        for key, (by_containment, carried) in sorted(binders.items()):
            inside = sorted(carried & member_set, key=_wave_ident_key)
            if len(inside) < 2:
                continue
            carriers = [i for i in inside if key in owns[i]]
            covered = [i for i in inside if key not in owns[i]]
            rows_out.append((key, by_containment, carriers, covered))
        out.append({"members": members, "binders": rows_out})
    return out


def report_waves(schedulable, out, *, ready_n, live_n, excluded) -> int:
    """`item waves` — the join, printed. WRITES NOTHING, decides no sizing.

    `schedulable` is `[Item]` already through the blocker gate (the caller
    reuses `item ready --head`'s own predicate rather than restating it);
    `excluded` is `[(ident, why)]` for every READY item the gate held back,
    printed rather than subtracted — a population that shrank silently is a
    plan over a set the reader never saw.

    THE EXIT CODE ANSWERS ONE QUESTION: is the mapping COMPLETE? Every
    schedulable item path-valued and the join covers the population, so the
    run is CLEAN; any item whose boundary could not be read as paths, or an
    empty population, and the lane list is not the whole answer — COULD NOT
    VERIFY, which is exactly the promise `exits.worst` says that code
    withdraws. It never returns FINDING: whether a prose write-set is a defect
    is `item check`'s question and lc-111's item, and a planning verb that
    also graded the carrier would be two checkers with one exit code.
    """
    out("item waves — the write-set join over the schedulable READY set. "
        "READ-ONLY: it writes no carrier and schedules nothing.")
    out(f"scanned: {live_n} live item(s), {ready_n} READY, "
        f"{len(schedulable)} schedulable (the blocker gate), "
        f"{len(excluded)} READY but held back.")
    for ident, why in excluded:
        out(f"    held back: {ident} — {why}")

    if not schedulable:
        out("")
        out("COULD NOT VERIFY: no schedulable item, so there was nothing to "
            f"join — not a plan with zero collisions. {ready_n} item(s) are "
            f"graded READY and {len(excluded)} of those the blocker gate held "
            "back; a lane list printed over an empty population reads exactly "
            "like a carrier whose work is all independent.")
        return exits.COULD_NOT_VERIFY

    buckets: dict = {WAVE_UNSET: [], WAVE_PROSE: [], WAVE_FOREIGN: []}
    rows = []
    for it in schedulable:
        bucket, paths, why = classify_write_set(effective_write_set(it))
        if bucket == WAVE_PATHS:
            rows.append((it.ident, paths))
        else:
            buckets[bucket].append((it.ident, why))

    lanes = wave_lanes(rows)
    out("")
    out(f"LANES: {len(lanes)} over {len(rows)} path-valued item(s). Members of "
        "one lane SHARE A FILE and serialize; the lanes are disjoint by "
        "construction, so the whole set of lanes is the PARALLEL set — "
        f"{len(lanes)} lane(s) can run at once.")
    for n, lane in enumerate(lanes, start=1):
        members = lane["members"]
        if len(members) == 1:
            out(f"lane {n}: {members[0]} alone — its write-set shares no file "
                "with any other schedulable item.")
            continue
        out(f"lane {n}: {len(members)} item(s) — {', '.join(members)}")
        for key, by_containment, carriers, covered in lane["binders"]:
            if not covered:
                out(f"      shared {key}: {', '.join(carriers)}")
                continue
            out(f"      shared {key} — a DIRECTORY entry, written by "
                f"{', '.join(carriers)}; it covers files named by "
                f"{len(covered)} other member(s): {', '.join(covered)}")

    out("")
    out("NOT CLUSTERED — a write-set that cannot be read as this repo's paths "
        "is never put in a lane, because a join over a slot nobody could read "
        "would read exactly like one over a slot that was read:")
    for key in WAVE_NON_PATH:
        hits = buckets[key]
        out(f"  {key}: {len(hits)}" + (" — none" if not hits else ""))
        for ident, why in hits:
            out(f"      {ident}: {why}")

    unread = sum(len(buckets[k]) for k in WAVE_NON_PATH)
    out("")
    out("NO SIZING, NO TIER, NO ORDER: this verb computes the join and stops. "
        "How many lanes one dispatch carries, which tier each takes and what "
        "runs first stay the desk's judgment — the mapping is derivable, the "
        "crossover is not.")
    if unread:
        out(f"item waves: COULD NOT VERIFY — {unread} of "
            f"{len(schedulable)} schedulable item(s) have a write-set this "
            "join could not read, so the lanes above are a plan over "
            f"{len(rows)} item(s) and NOT the whole schedulable set.")
        return exits.COULD_NOT_VERIFY
    out(f"item waves: CLEAN — every one of the {len(rows)} schedulable "
        "item(s) carries a path-valued write-set, so the mapping above covers "
        "the whole population.")
    return exits.CLEAN
