"""The GRAMMAR every verb writes and every verb reads (lc-40).

ONE MODULE FOR THE VALUES THAT CROSS VERBS. Nothing here is a policy or a
threshold — it is the on-disk SHAPE: how a block heading is spelled, how a
`slot: value` line is spelled, how an id is spelled, what the ledger's
separators are, and what the ledger refuses. Every one of those is a fact two
or more modules must agree on, and every one of them was spelled more than
once before this module existed.

WHY A MODULE RATHER THAN A CONVENTION. A second spelling of one fact does not
fail loudly — it ages apart, and the divergence is silent in the quiet
direction: the writer keeps writing a shape the reader has stopped
recognising, and every affected line reads as something nobody wrote. This is
the same argument `ledger._MOOT_ANSWER` makes for its own pair and the same
one `migrate._ledger_storable` makes for importing the ledger's predicate
instead of restating it; this module is that argument applied to the whole
grammar rather than to one value at a time.

THE MEASURED CASE, which is why the heading has THREE functions below and not
one. `verbs._set_slots` found a block with the `## <id>` REGEX and ended it
with `startswith("## ")` — two spellings of "a heading", disagreeing on
exactly one input: a heading whose separator is not a single space. Measured
2026-08-28 against HEAD: a carrier whose second block reads `##\txx-2` (a tab,
which the reader's regex accepts and has always accepted), and `item park
xx-1` wrote `grade: PARKED` and the blocker into xx-2 as well — exit 0, no
finding, no notice. The control with a space heading left xx-2 untouched. The
two spellings were individually correct; jointly they silently edited an item
nobody named.

SO THE THREE HEADING QUESTIONS ARE NAMED APART, because they are three
different questions and collapsing them is what produced the defect:

  `heading_ident(line)`  — is this the heading of an ITEM BLOCK, and whose?
  `starts_section(line)` — does a `## ` SECTION start here? (the head-region
                           boundary: it stops at `## Archive (pre-migration)`
                           as much as at a block, which is what the head scan
                           means and what a block regex would MISS)
  `ends_block(line)`     — does the block that was open END here? ANY `##`
                           heading ends it, whatever its whitespace and
                           whatever its text — a block's own body lines never
                           begin with `##`, so the wide reading is the safe
                           one, and the narrow reading is the defect above.

`starts_section` and `ends_block` differ on a tab-separated heading and on
nothing else. That difference is the whole bug, so it is stated here once
rather than re-derived at each call site.

IMPORTS NOTHING FROM THE PACKAGE. Every module below imports this one, so a
back-edge would be a cycle; keeping it pure is what lets it be the bottom of
the stack rather than another peer.
"""

import re

# --- the item carrier's line shapes -------------------------------------------

#: A block heading and the id in it. `\s+` between the marker and the id is
#: DELIBERATE and predates this module: the carrier is hand-editable and a
#: merge or another tool may put a tab there, so the reader accepts it. Every
#: consumer must therefore accept it too, which is what `ends_block` is for.
BLOCK_HEADING = re.compile(r"^##\s+(\S+)\s*$")

#: A `## ` section start, the NARROW reading — one marker, one space. This is
#: the head-region boundary: the head ends at the first section of any kind,
#: block or archive heading alike.
HEADING_PREFIX = "## "

#: ANY `##` heading, the WIDE reading — the block terminator. See the module
#: docstring: a block's own body lines never begin with `##`, so nothing is
#: swallowed by reading this widely, while reading it narrowly loses the
#: heading whose separator is not a single space.
_ANY_HEADING = re.compile(r"^##\s")

#: A head line (`key: value` with any spacing after the colon) and a slot line
#: (at most ONE space after the colon, so a value's own leading whitespace
#: survives the round trip). Two shapes, kept apart on purpose.
HEAD_LINE = re.compile(r"^([a-z-]+):\s*(.*)$")
SLOT_LINE = re.compile(r"^([a-z-]+):\s?(.*)$")

#: THE PRE-MIGRATION ARCHIVE HEADING, one spelling for both carriers. It was
#: a literal in `items.py` and again in `ledger.py`; the two files must agree
#: about where the ungraded region begins, and two literals for that is the
#: divergence this module exists to remove.
ARCHIVE_HEADING = "## Archive (pre-migration)"


def heading_ident(line: str) -> str | None:
    """The id in a block heading, or None if `line` is not one."""
    m = BLOCK_HEADING.match(line)
    return m.group(1) if m else None


def render_heading(ident: str) -> str:
    """A block heading. The ONLY place the written shape is spelled."""
    return f"{HEADING_PREFIX}{ident}"


def starts_section(line: str) -> bool:
    """Does a `## ` section start here? The HEAD-REGION boundary.

    Narrow by contract, not by oversight: the head ends at the first section
    of ANY kind, and `## Archive (pre-migration)` is such a section while not
    being a block. `heading_ident` would return None for it and the head scan
    would run on past the archive, which is the opposite error.
    """
    return line.startswith(HEADING_PREFIX)


def ends_block(line: str) -> bool:
    """Does the currently-open block END here? ANY `##` heading ends it.

    THE WIDE READING IS THE CORRECT ONE and the narrow one is a measured
    defect — see the module docstring. A caller that finds a block with
    `heading_ident` must end it with THIS, or the two disagree on a heading
    whose separator is not a single space and the caller writes past the
    block it was given.
    """
    return bool(_ANY_HEADING.match(line))


def render_slot(key: str, value) -> str:
    """One `slot: value` line. The ONLY place the written shape is spelled."""
    return f"{key}: {value}"


def is_slot(line: str, key: str) -> bool:
    """Does `line` carry the slot named `key`?

    Anchored on the KEY plus its colon rather than on the bare key: a
    `startswith(key)` test is a prefix match in an equality's costume, and it
    would read `blocked-by-note:` as `blocked-by`.
    """
    return line.startswith(f"{key}:")


# --- ids ----------------------------------------------------------------------

def id_re(prefix: str) -> re.Pattern:
    """`^<prefix>-<n>$`, the id shape, with the prefix escaped.

    The prefix comes from the DECLARATION at every call site; inferring it
    from the ids present would make any consistent corruption look correct.
    Group 1 is the number, so one pattern serves both the shape check and the
    allocator — they were two patterns differing only in that group, which is
    two spellings of one fact.
    """
    return re.compile(rf"^{re.escape(prefix)}-(\d+)$")


def id_number(prefix: str, ident: str) -> int | None:
    """The `<n>` of `ident` under `prefix`, or None if it is not that shape."""
    m = id_re(prefix).match(ident)
    return int(m.group(1)) if m else None


# --- the ledger's line shapes, and the refusal that guards them ---------------

#: Slot separator, and the decision line's question/answer separator. Both are
#: the design's own spellings and are matched literally.
SEP = " — "
ARROW = " → "

#: A reason longer than this is a BODY wearing a reason's clothes. The
#: ledger's whole contract is one line per decision event; a cap is the only
#: mechanical expression of that, since "is this prose a body?" has no
#: predicate. Generous on purpose — it catches a pasted paragraph, not a
#: carefully worded sentence.
REASON_CAP = 300


def check_prose(value: str, what: str) -> str | None:
    """Why `value` may not be written as ledger prose, or None — `ledger_body`.

    Checked at the WRITER rather than at the reader: a file that never
    receives an ambiguous line never needs a reader that can resolve one.

    THE ONE PREDICATE FOR EVERY DOOR. `ledger add`, `migrate`'s mint and the
    three hand-write blocker doors all reach this function rather than
    restating what the ledger refuses; a second spelling would age apart from
    the writer it must agree with, and it would fail in the QUIET direction —
    a gate passing a question the real writer then refuses, which is how a
    blocker becomes permanently unanswerable (lc-40, lc-49).
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


# --- the minted blocker question ----------------------------------------------

#: THE MINTING FORM, and it carries NEITHER separator on purpose (lc-40).
#: `ledger add decision` refuses a question carrying the ledger's own slot
#: separator — rightly, because an escaped spelling would put two forms of
#: every value in that file. `item ready` resolves a `decision` blocker by
#: QUESTION-SLOT EQUALITY, so a question rephrased at ANSWER time no longer
#: matches the blocker it was written to clear. Each mechanism is correct
#: alone; jointly they made 69 of 99 decision-blocked items permanently
#: unanswerable (measured over dotfiles' carrier, 2026-08-27). The repair is
#: at the MINT — the separator never enters the question — and it lives HERE,
#: beside the predicate that judges it, so an edit to the text and the rule it
#: must satisfy cannot drift into different files.
REGRADE_BLOCKER = ('decision regrade: was READY under the old carrier'
                   ': READY is judged, never inherited')
