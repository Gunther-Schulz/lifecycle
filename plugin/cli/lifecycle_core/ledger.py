"""`LEDGER.md`: decisions only, parsed, gated (design §3.6).

NO BODIES, AND NOTHING MIGRATES IN. One fixed-slot line per decision event.
That is not a size preference — it is what makes the ledger PARSEABLE and
therefore gateable. A carrier holding bodies is read by people; a carrier
holding slots is read by the gates that must run before a re-grade.

THE SPLIT BETWEEN TOOL AND SESSION IS DELIBERATE. The tool writes the SLOTS;
the SESSION writes the reason prose. The tool never generates a rationale —
every writer below REQUIRES its prose argument and refuses without it. The
reason is the operator-as-backstop moment at every rationale line, and a
generated one would be a paraphrase with nobody's judgment behind it.

THE READERS ARE GATES, NOT HABITS. `rejected --for <item>` runs in the grade
workflow BEFORE a re-grade; intake prints matching rejected lines beside its
join candidates. Nothing here is meant to be browsed.

THE SEPARATORS ARE PART OF THE SHAPE. ` — ` between slots, ` → ` between a
decision's question and its answer. A slot value containing its own separator
would make the parse ambiguous — the same body reading as two different
splits — so a writer REFUSES such a value rather than escaping it. Escaping
would put a second spelling of every value into the file, and the reader
would then have to know which one it was looking at.

SUPERSEDE IS ROUTED ONE WAY: the body to the done home (counted there by
conservation), the REASON here. The ledger line is outside the conservation
identity by construction — it is not a body and was never counted.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from . import exits

#: The ledger format this build understands, same floor rule as `ITEMS.md`,
#: and the SAME NUMBER: one schema version per repo (§3.8c).
SCHEMA_FLOOR = 2

#: Slot separator, and the decision line's question/answer separator. Both
#: are the design's own spellings and are matched literally.
SEP = " — "
ARROW = " → "

#: The four line kinds, closed. A fifth spelling reaching the file is READ
#: and reported in the third answer — never crashed on, never folded into a
#: known kind.
KINDS = ("superseded", "rejected", "dropped", "decision")

#: A reason longer than this is a BODY wearing a reason's clothes. The
#: ledger's whole contract is one line per decision event; a cap is the only
#: mechanical expression of that, since "is this prose a body?" has no
#: predicate. Generous on purpose — it catches a pasted paragraph, not a
#: carefully worded sentence.
REASON_CAP = 300

#: THE PRE-MIGRATION ARCHIVE, exactly as `ITEMS-DONE.md` has one and for
#: exactly the same reason. A repo that kept a prose ledger before the tool
#: owned the file has history that will never satisfy a fixed-slot shape and
#: was never meant to. Held VERBATIM below this heading, counted apart, never
#: classified into a known kind.
#:
#: NOT a softened predicate: above the heading the shape is unchanged, and the
#: archive's own line count is printed so a reader can see how much of the
#: file this run did not grade. Deleting the history to make the parse clean
#: is the exit that leaves no trace, which is the loss this carrier exists to
#: prevent (exit: never-delete).
ARCHIVE_HEADING = "## Archive (pre-migration)"

_HEAD_LINE = re.compile(r"^([a-z-]+):\s*(.*)$")
#: A comment line in the PREAMBLE — matched by shape, since the block this
#: licenses is prose a human writes. Same predicate as the carrier's.
_COMMENT_LINE = re.compile(r"^\s*(#|<!--|-->|-\s|>\s|\*\s)")


@dataclass
class Line:
    kind: str
    slots: dict
    lineno: int
    raw: str


@dataclass
class Parsed:
    head: dict = field(default_factory=dict)
    lines: list = field(default_factory=list)
    #: (row-id, lineno, message) — shape problems.
    problems: list = field(default_factory=list)
    #: Lines that are neither head nor a known kind, by lineno. THE THIRD
    #: ANSWER: read, counted, never folded into a known kind.
    unreadable: list = field(default_factory=list)
    #: Lines below the archive heading: held verbatim, counted, not graded.
    archive_lines: int = 0
    refused: bool = False


# --- writing -----------------------------------------------------------------

def check_prose(value: str, what: str) -> str | None:
    """Why `value` may not be written as ledger prose, or None.

    Checked at the WRITER rather than at the reader: a file that never
    receives an ambiguous line never needs a reader that can resolve one.
    """
    if value is None or not str(value).strip():
        return (f"{what} is empty. The tool writes the slots; the SESSION "
                "writes the reason prose, and a generated rationale would be "
                "a paraphrase with nobody's judgment behind it. There is no "
                "default here on purpose.")
    v = str(value)
    if "\n" in v or "\r" in v:
        return (f"{what} spans more than one line. The ledger carries NO "
                "BODIES — one fixed-slot line per decision event. A body "
                "belongs in the done home, which counts it.")
    if len(v) > REASON_CAP:
        return (f"{what} is {len(v)} characters, over the {REASON_CAP}-cap. "
                "That length is a body wearing a reason's clothes; the body "
                "belongs in the done home.")
    if SEP in v:
        return (f"{what} contains the slot separator {SEP!r}, which would "
                "make the line parse into different slots than it was "
                "written with. Rephrase rather than escaping: an escaped "
                "spelling puts two forms of every value in the file and the "
                "reader cannot tell which it is looking at.")
    if ARROW in v:
        return (f"{what} contains the decision separator {ARROW!r}, same "
                "ambiguity as the slot separator.")
    return None


def render(kind: str, slots: dict) -> str:
    """One ledger line from its slots. The ONLY place a line is spelled."""
    if kind == "superseded":
        return f"superseded: {slots['id']} by {slots['by']}{SEP}{slots['reason']}"
    if kind == "rejected":
        return (f"rejected: {slots['item']}{SEP}{slots['approach']}"
                f"{SEP}{slots['why']}")
    if kind == "dropped":
        return f"dropped: {slots['id']}{SEP}{slots['reason']}"
    if kind == "decision":
        return f"decision: {slots['question']}{ARROW}{slots['answer']}"
    raise ValueError(f"unknown ledger kind {kind!r}; the kinds are "
                     f"{', '.join(KINDS)}")


def head_text() -> str:
    """A new ledger, empty but for its head."""
    return f"schema: {SCHEMA_FLOOR}\n"


def append(path: Path, kind: str, slots: dict) -> str:
    """Append one rendered line. Returns the line as written.

    APPEND-ONLY, and it creates the head when the file is absent: a ledger
    with no schema line cannot be refused by a future tool, which is the
    whole reason the line exists.

    BEFORE THE ARCHIVE HEADING, never after it — the same rule the carrier's
    move already follows for the same reason. A line written below the
    heading sits in the region held verbatim and not graded, so it would be
    invisible to `ledger check` and to every gate that reads this file: a
    decision recorded where nothing reads it is a decision not recorded.
    """
    line = render(kind, slots)
    if not path.exists():
        path.write_text(head_text() + "\n" + line + "\n", encoding="utf-8")
        return line
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    for i, raw in enumerate(lines):
        if raw.strip() == ARCHIVE_HEADING:
            head = "\n".join(lines[:i]).rstrip("\n")
            tail = "\n".join(lines[i:])
            path.write_text(f"{head}\n{line}\n\n{tail}", encoding="utf-8")
            return line
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return line


# --- parsing -----------------------------------------------------------------

def parse(text: str) -> Parsed:
    """Read a ledger. Never raises on content.

    A line this build cannot classify is UNREADABLE and counted apart — the
    same three answers the carrier's census gives a grade word it does not
    know. Folding it into a known kind would put a line nobody wrote into
    the output of a gate.
    """
    out = Parsed()
    lines = text.split("\n")

    # A COMMENT BLOCK MAY PRECEDE THE SCHEMA LINE (§3.8c). Before this, the
    # first non-blank line had to BE `schema: <n>`, so a repo's ledger was
    # exactly `schema: 1` until its first decision — a carrier in a PUBLIC
    # repo that could not say what it was for. Only before: everything below
    # the version is one fixed-slot line per decision event, and a comment
    # there would be a line the gates read and cannot classify.
    i = 0
    while i < len(lines):
        raw = lines[i]
        i += 1
        if not raw.strip():
            continue
        if _COMMENT_LINE.match(raw):
            continue
        m = _HEAD_LINE.match(raw)
        if m and m.group(1) == "schema":
            try:
                out.head["schema"] = int(m.group(2).strip())
            except ValueError:
                out.problems.append(("ledger_shape", i,
                                     f"`schema` must be an integer, got "
                                     f"{m.group(2).strip()!r}."))
            break
        # Anything before a schema line that is not blank means the head is
        # missing; stop looking and let the check below say so.
        i -= 1
        break

    if "schema" not in out.head:
        out.problems.append(("ledger_shape", 1,
                             "the ledger carries no `schema: <n>` head line."))
    elif out.head["schema"] > SCHEMA_FLOOR:
        out.problems.append((
            "schema_above_floor", 1,
            f"ledger is stamped schema {out.head['schema']}; this build "
            f"understands {SCHEMA_FLOOR}. REFUSING TO PARSE the body."))
        out.refused = True
        return out

    while i < len(lines):
        raw = lines[i]
        lineno = i + 1
        i += 1
        if raw.strip() == ARCHIVE_HEADING:
            out.archive_lines = len(lines) - i
            break
        if not raw.strip():
            continue
        parsed = parse_line(raw)
        if parsed is None:
            out.unreadable.append((lineno, raw))
            continue
        kind, slots = parsed
        out.lines.append(Line(kind=kind, slots=slots, lineno=lineno, raw=raw))
    return out


def parse_line(raw: str):
    """`(kind, slots)` or None. None means THIS BUILD cannot read the line —
    never that the line is worthless."""
    head, colon, rest = raw.partition(":")
    kind = head.strip()
    if not colon or kind not in KINDS:
        return None
    rest = rest.strip()

    if kind == "superseded":
        left, sep, reason = rest.partition(SEP)
        if not sep:
            return None
        old, by_sep, new = left.partition(" by ")
        if not by_sep:
            return None
        return kind, {"id": old.strip(), "by": new.strip(),
                      "reason": reason.strip()}
    if kind == "rejected":
        parts = rest.split(SEP)
        if len(parts) != 3:
            return None
        return kind, {"item": parts[0].strip(), "approach": parts[1].strip(),
                      "why": parts[2].strip()}
    if kind == "dropped":
        ident, sep, reason = rest.partition(SEP)
        if not sep:
            return None
        return kind, {"id": ident.strip(), "reason": reason.strip()}
    if kind == "decision":
        q, sep, a = rest.partition(ARROW)
        if not sep:
            return None
        return kind, {"question": q.strip(), "answer": a.strip()}
    return None


def read(path: Path):
    """`(Parsed, could_not_verify_reason)`.

    An ABSENT ledger is not an empty one and is not clean: a gate that runs
    `rejected --for <item>` against a file that is not there must not report
    "no rejections" — that reads exactly like a checked, clean answer.
    """
    if not path.exists():
        return None, (f"no ledger at {path}. An absent ledger and one with no "
                      "matching line are not the same answer: the first means "
                      "the gate could not run, the second that it ran and "
                      "found nothing.")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"{path} could not be read ({exc!r})."
    return parse(text), None


# --- the gated readers -------------------------------------------------------

def rejected_for(parsed: Parsed, item: str) -> list:
    """Every `rejected:` line whose ITEM slot names `item`.

    Anchored on the SLOT, never on the word appearing anywhere in the line:
    a reason sentence mentioning `cf-12` is prose, and a reader matching the
    whole rendered line would return it as a rejection of cf-12.
    """
    return [ln for ln in parsed.lines
            if ln.kind == "rejected" and ln.slots.get("item") == item]


def counts(parsed: Parsed) -> dict:
    """Per-kind counts plus the unreadable tally — the third answer, always
    rendered even when zero, so a reader can tell "none" from "not asked"."""
    out = {k: 0 for k in KINDS}
    for ln in parsed.lines:
        out[ln.kind] += 1
    out["unreadable"] = len(parsed.unreadable)
    return out


def check_file(path: Path, out) -> int:
    """The ledger's own shape check, three answers."""
    parsed, why = read(path)
    if parsed is None:
        out(f"COULD NOT VERIFY: {why}")
        return exits.COULD_NOT_VERIFY
    for row, lineno, msg in parsed.problems:
        out(f"FINDING [{row}] {path.name}:{lineno}: {msg}")
    if parsed.refused:
        out("ledger check: FINDING — the body was not parsed.")
        return exits.FINDING
    c = counts(parsed)
    out("ledger: " + "  ".join(f"{k} {c[k]}" for k in KINDS)
        + f"  unreadable {c['unreadable']}")
    for lineno, raw in parsed.unreadable:
        out(f"  unreadable line {lineno}: {raw[:70]!r} — READ, never folded "
            "into a known kind. It reached this file by a merge or an older "
            "tool.")
    if parsed.archive_lines:
        out(f"archive: {parsed.archive_lines} line(s) after "
            f"{ARCHIVE_HEADING!r}, held verbatim and NOT graded. This run says "
            "how much of the file it did not read rather than reporting a "
            "clean parse over the part it did.")
    code = exits.FINDING if parsed.problems else exits.CLEAN
    if parsed.unreadable:
        code = exits.worst([code, exits.COULD_NOT_VERIFY])
    out(f"ledger check: {exits.word(code)} — {len(parsed.problems)} shape "
        f"finding(s), {c['unreadable']} unreadable line(s).")
    return code
