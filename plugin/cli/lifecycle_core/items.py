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

#: THE FORWARD POINTER (lc-120). A closed body's slots cannot be corrected —
#: `item amend` refuses one and that refusal is RIGHT: the done home holds what
#: was true when the item closed, and editing it there would rewrite a record
#: other counts have already read. The consequence was that a slot which turns
#: out FALSE keeps asserting itself forever while its correction lives only in
#: a ledger line the done-home reader never loads. That is the appended-
#: correction failure at carrier scale: both versions stand, and the reader who
#: stops at the first takes the superseded one.
#:
#: SO THE REPAIR IS APPEND-ONLY, and it is not an amendment by another name.
#: The original `closed-reason:` and `closed-ref:` are never touched. A pointer
#: is not an edit of the record — it is the record saying a later one exists.
#:
#: IT REPEATS, like the amendment and promotion lines above and for the reason
#: this entry itself documents. A single-valued pointer would leave the SECOND
#: superseding correction with no home, which is precisely the defect this slot
#: repairs, reintroduced one level up. The alternative — refusing a second
#: pointer — would need a refusal of its own, and the only refusal this work
#: was ruled to add is the sibling of `closed_ref_unresolvable`.
CLOSURE_SUPERSEDED_BY = "closure-superseded-by"

DONE_ONLY_SLOTS = ("superseded-by", "blocker-moot", CLOSED_REASON, CLOSED_REF,
                   CLOSURE_SUPERSEDED_BY)

#: THE EXERCISE RECORD FOR AN `evidence` BLOCKER (lc-175). lc-164 made the
#: BOOKING run the predicate and refused exit 0, so every evidence blocker in
#: a carrier answered 1 at its mint by construction. That proves the predicate
#: can say NOT YET; it does not prove it can ever say ARRIVED, and one run
#: cannot. A peer desk exercised three blockers by hand on 2026-09-18 — live
#: exit, a constructed positive, a constructed negative — and NOTHING IN THE
#: CARRIER RECORDED THAT THEY DID: an exercise nobody can see is a discipline
#: that holds only while the person who held it is in the room.
#:
#: CONDITIONAL, NOT A MEMBER OF `SLOTS`, and the shape was decided by
#: MEASUREMENT rather than by symmetry with the fixed run. Measured on this
#: carrier 2026-09-19: 8 evidence blockers, 3 of them READY; 25 decision
#: blockers, 16 of them READY. A member of `SLOTS` is written into every block
#: by the migration, and the value it would carry is UNKNOWN — which
#: `ready_with_unknown_slot` turns into a finding. That would have made 3 items
#: findings the day this shipped, and this item's MUST-NOT-MOVE forbids
#: exactly that. So it follows `DONE_ONLY_SLOTS`: optional, legal only where
#: its blocker type makes it MEAN something, and deliberately absent from
#: `UNKNOWNABLE_SLOTS` so the transitional value cannot un-READY a live item.
#:
#: THE ABSENCE IS REPORTED, NEVER RAISED. The done-criterion asks that an
#: unexercised blocker be "visible as such rather than silently unexercised" —
#: which a COUNT satisfies and a finding over-satisfies. This is I5's move
#: (the-loop.md): the fix for an invisible absence was never a better duty, it
#: was a count at close that makes a zero answerable.
#:
#: THE CONSTRUCTED ARMS ARE THE AUTHOR'S ACT, NEVER THE TOOL'S (MUST-NOT-MOVE).
#: A verb that synthesised a positive would be grading its own plant — the
#: same-parentage defect law 2 exists against. So this slot is a FORM whose
#: absence is readable, not a predicate the tool computes.
BLOCKER_EXERCISE = "blocker-exercise"

#: THE DERIVABILITY STATEMENT FOR A `decision` BLOCKER (lc-179). lc-169 made
#: the mint DEMAND why a question is not derivable from the record, and that
#: demand works — it forces the thinking while the author still has the record
#: open. But the demand's product is PRINTED AT THE DOOR AND PERSISTED
#: NOWHERE, exactly as its `--absence` precedent behaves, so the statement is
#: gone the moment the terminal scrolls and no later reader can check it
#: against the world.
#:
#: THE CONSUMER IS NAMED AND REAL, which is what makes this more than
#: symmetry: lc-158's own story is a decision blocker MIS-TYPED at booking —
#: read as a decision, actually a factual question a measurement could settle.
#: A persisted statement is what lets a later reader catch that class. A
#: printed one cannot, and the carrier today cannot tell a blocker booked WITH
#: a statement from one booked before lc-169 existed.
#:
#: SPELLED AS THE FLAG IS SPELLED. `--not-derivable` is the door's vocabulary
#: and this is the same concept persisted, so it takes the same word — one
#: spelling per concept, the rule `grammar` exists to hold.
NOT_DERIVABLE = "not-derivable"

#: Slots legal only beside a `blocked-by` of a particular TYPE, each with the
#: refusal row its misplacement fires. A slot present where its type is not is
#: a finding, in the same direction as `done_slot_on_live_item` — a slot legal
#: everywhere is an annotation, not a slot.
#:
#: A ROW PER SLOT, and this is deliberately NOT the §3.8c reading that would
#: merge them. The two misplacements share an ANSWER CLASS (remove the slot or
#: correct the blocker), which on §3.8c alone argues for one row. REACH decides
#: it the other way: a row is proven by its plant, and one plant certifies the
#: CLASS THAT FIRED and not its variants — merged, whichever slot the single
#: plant did not use would ship a refusal message nobody had ever seen fire.
#: Two rows, two plants, two controls; the shared answer class is a note for
#: the route question, never a reason to leave half the surface unproven.
BLOCKER_SLOT_RULES = {
    BLOCKER_EXERCISE: ("evidence", "blocker_exercise_misplaced",
                       "records that a PREDICATE was exercised — its live "
                       "exit and the two constructed arms that show it "
                       "answering both ways — and only an `evidence` blocker "
                       "has a predicate"),
    NOT_DERIVABLE: ("decision", "not_derivable_misplaced",
                    "records why a QUESTION is not derivable from the "
                    "record, and only a `decision` blocker asks a question"),
}
BLOCKER_ONLY_SLOTS = tuple(BLOCKER_SLOT_RULES)

#: The FORWARD-ONLY DOOR STAMP's opener (D-7 rev.). A conditional slot
#: carrying this records that the block PASSED THROUGH the door and owes its
#: content; a block carrying no line at all never passed through one, and the
#: two are different answers. Spelled once here because two readers consume
#: it — the door that writes it and the census that counts it — and a second
#: spelling would let the writer produce a value its own counter files under
#: the wrong bucket.
SLOT_STAMP_NONE_YET = "none-yet"

#: `<date> <ledger-ref> <one line>`, the three parts the design names. Checked
#: as ONE predicate with ONE home because two consumers read it: the parser
#: grades what is on disk and the verb grades what it is about to write, and a
#: second spelling would let the writer produce a line its own reader refuses —
#: the divergence `grammar` exists to prevent, applied to one more value.
#:
#: The REF is matched as a bare token rather than as a sha: `item close --ref`
#: writes the operator's own spelling and this follows it, so whether the ref
#: RESOLVES is a question for the repo and not for a regex (the verb asks git).
_CLOSURE_POINTER_VALUE = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(\S+)\s+(\S.*)$")


def closure_pointer_problem(value: str) -> str | None:
    """Why `value` is not a well-formed forward pointer, or None.

    THE ONE PREDICATE FOR BOTH DOORS — see `_CLOSURE_POINTER_VALUE` above.
    """
    v = (value or "")
    if not v.strip():
        return (f"`{CLOSURE_SUPERSEDED_BY}:` is empty. The pointer's whole "
                "content is a date, a ref and a sentence; an empty one records "
                "that a correction exists and says nothing about where.")
    if not _CLOSURE_POINTER_VALUE.match(v):
        return (f"`{CLOSURE_SUPERSEDED_BY}:` is not `<date> <ledger-ref> <one "
                f"line>`: {v[:60]!r}. A pointer nobody can place in time, or "
                "that names no ref, or that names a ref and then says nothing, "
                "is a claim that a correction exists rather than a route to "
                "it — which is the state this slot exists to end.")
    return None

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

#: TWO QUESTIONS THAT WERE ONE TUPLE UNTIL lc-175, and they came apart the
#: moment a slot needed different answers to them:
#:   (1) MAY this slot hold UNKNOWN at all, or is UNKNOWN there a value
#:       nothing can ever fill in (`unknown_slot_misplaced`)?
#:   (2) does UNKNOWN here REFUSE the item READY (`ready_with_unknown_slot`)?
#: `UNKNOWNABLE_SLOTS` answered both while every slot's answers agreed, which
#: is why the conflation was invisible rather than wrong. `blocker-exercise`
#: answers YES to (1) — UNKNOWN is precisely its migration value — and NO to
#: (2), because 3 of this carrier's 8 evidence blockers sit on READY items and
#: converting them was forbidden by that item's MUST-NOT-MOVE.
#:
#: FOUND BY THE RED-FIRST RUN, not by reading: the new slot's UNKNOWN arm came
#: back `unknown_slot_misplaced` — a true finding from an instrument aimed at
#: a distinction the code did not yet draw.
UNKNOWN_LEGAL_SLOTS = UNKNOWNABLE_SLOTS + BLOCKER_ONLY_SLOTS

#: EVIDENCE MARKS (lc-167) — the closed vocabulary separating evidence a
#: session RAN from evidence it CONCLUDED.
#:
#: WHY THE CARRIER NEEDS IT: measured over one desk's full day of booking,
#: every item booked from measured evidence held up, and the one booked from
#: a just-formed conclusion — a plausible code path read but not the one that
#: actually runs — was wrong within the hour and would have sent a lane to
#: make a no-op change. Read from this repo's other end the same day: over 88
#: closed items, `amended-evidence` is the most-amended slot at 39%, which is
#: the same fact seen as an entry whose evidence moved after booking. The
#: slot took both kinds and marked neither.
#:
#: THE WORDS ARE NOT INVENTED HERE. The corpus already sorts a finding's
#: sentences into OBSERVED, RECALLED and DERIVED, and separately requires
#: another party's claim to be relayed AS that party's. Those are the four.
#: `MEASURED` rather than the corpus's `OBSERVED` for the executed one, on
#: the one-spelling-per-concept rule: this repo already spells that route
#: `measure` in the investigation record's own vocabulary (`records.ROUTES`),
#: and a concept taught under two names in one repo mints entries that read
#: green to their author under either.
#:
#: WHAT THE PREDICATE ESTABLISHES, and it is narrower than the rule: that a
#: mark is PRESENT, never that it is true. This is the form the corpus names
#: for a duty whose firing moment is an event — a fixed, named token whose
#: absence is readable at a glance without grading content; grading the fill
#: is a second and cheaper step, run only over tokens that exist. A checker
#: that tried to decide whether a sentence really was measured would be
#: grading prose, which is the guard that fires on legitimate work (law 11).
#: `PERISHABLE` IS A FIFTH MEMBER AND NOT A SLOT MARKER (lc-244, W2; the
#: round's E10 form correction supersedes D-5's original slot-marker
#: wording). It joins the set the admission door already checks, so its
#: PRESENCE enforces for free through the same predicate — a marker in a new
#: place would have needed a new enforcement path and would have been
#: enforced nowhere until someone built one.
#:
#: IT IS THE ONE MEMBER THAT TAKES ARGUMENTS, and both are load-bearing.
#: The DATE meets law 26 at the base-slot case: the FIRST mark anyone writes
#: has no comparison input, so a form without its own date has no computable
#: absence at exactly the case the rule exists for (B7). The COMMAND is what
#: makes the staleness answerable rather than felt — a flag saying "this may
#: be stale" and nothing more hands its reader the work of rediscovering how
#: the claim was taken in the first place.
PERISHABLE = "PERISHABLE"
PERISHABLE_FORM = "PERISHABLE(<date>, re-derive: <command>)"

EVIDENCE_MARKS = ("MEASURED", "DERIVED", "RECALLED", "RELAYED", PERISHABLE)

_EVIDENCE_MARK = re.compile(r"\b(" + "|".join(EVIDENCE_MARKS) + r")\b")

#: The WELL-FORMED spelling. Anchored on the closing paren rather than run to
#: end-of-line: an evidence slot is prose and the mark sits inside it, so a
#: greedy tail would swallow the sentence that follows the mark into the
#: `re-derive` command and then report a command nobody wrote.
_PERISHABLE_OK = re.compile(
    r"\bPERISHABLE\(\s*(\d{4}-\d{2}-\d{2})\s*,\s*re-derive:\s*([^)]+?)\s*\)")

#: The mark's NAME wherever it appears — well-formed or not. The pair is the
#: whole grammar check: a token matching this and not the form above is a
#: PERISHABLE somebody meant and misspelled, which is a different answer from
#: a slot that never claimed to carry one.
_PERISHABLE_ANY = re.compile(r"\bPERISHABLE\b")

#: What each mark claims, quoted back to the author at the refusal. Kept
#: beside the vocabulary rather than in the message: the refusal text and the
#: accepted set are one fact, and two bodies for it drift the day a mark is
#: added.
EVIDENCE_MARK_GLOSS = {
    "MEASURED": "a command this session ran, a file it read, a count it took",
    "DERIVED": "a cause, a meaning, an absence, a survivor — reasoned from "
               "something else rather than seen",
    "RECALLED": "held in memory, not re-read at the artifact",
    "RELAYED": "another party's report, carried as theirs",
    PERISHABLE: ("a claim that ROTS — true when taken and not thereafter; "
                 "spelled " + PERISHABLE_FORM + ", carrying the date it was "
                 "taken and the command that re-takes it"),
}


def perishable_marks(value: str) -> list:
    """Every WELL-FORMED `PERISHABLE(...)` in one evidence value.

    Returns `(date, command)` pairs in the order they appear. A slot may
    carry several: evidence is per claim, and two claims can rot on
    different clocks for different reasons.
    """
    return [(m.group(1), m.group(2).strip())
            for m in _PERISHABLE_OK.finditer(value or "")]


def perishable_grammar_problem(value: str) -> str | None:
    """Why a `PERISHABLE` token in this value is malformed, or None (W-9).

    WHY THIS IS A SECOND PREDICATE AND NOT A WIDENING OF THE FIRST.
    `evidence_mark_problem` is presence-only BY DESIGN and says so: it asks
    whether ANY mark is there, never whether a sentence really was measured.
    That is the right predicate for four members whose whole content is the
    word. `PERISHABLE` is the one member carrying ARGUMENTS, and arguments
    can be wrong in ways a presence test cannot see.

    AND THE MIXED SLOT IS WHY IT MATTERS, which is the case the attack found
    (W-9). A slot reading `MEASURED ... PERISHABLE(no date here) ...` passes
    the presence predicate outright — a valid sibling satisfies it — so the
    malformed mark ships, the freshness read never matches it, and the claim
    is silently exempt from the staleness it declared. An entirely unmarked
    slot is NOT a control for that case: it fails the first predicate for a
    different reason.
    """
    v = "" if value is None else str(value)
    if not _PERISHABLE_ANY.search(v):
        return None
    if _PERISHABLE_OK.search(v):
        return None
    return ("the evidence slot names PERISHABLE and does not spell it. The "
            "form is " + PERISHABLE_FORM + " — the DATE because the first "
            "mark anyone writes has no comparison input, so a form without "
            "its own date has no computable absence at exactly the case the "
            "mark exists for; the COMMAND because a flag that says a claim "
            "may be stale and stops there hands its reader the work of "
            "rediscovering how the claim was taken. A MIXED slot does not "
            "excuse it: a valid mark beside this one satisfies the "
            "presence check and leaves this mark unreadable, so the claim "
            "ends up exempt from the very staleness it declared.")


#: One flagged claim: which item, the mark's own date and command, and the
#: line that introduced it.
@dataclass(frozen=True)
class PerishableFlag:
    ident: str
    date: str
    command: str
    line: int


def evidence_events(item) -> list:
    """Every evidence write in one block, `(line, date, text)`, IN FILE ORDER.

    ONE BODY FOR TWO READERS, and that is not tidiness — it is the defect
    this function was extracted after. The freshness check walked the
    ORIGINAL value and the count beside it read `slots`, which on an amended
    item is the LAST amendment's text; the two disagreed exactly where it
    mattered, and the symptom was a flagged claim whose report line vanished
    the moment the item was amended for an unrelated reason. A count and a
    verdict over the same population must come from one walk or they will
    part company without a symptom.

    THE ORIGINAL, NOT THE VALUE IN FORCE. `slots` resolves amendments; this
    wants the sequence. A mark written at booking on an item amended later —
    the common case, since evidence is the most-amended slot at 39% — lives
    only in `originals`.
    """
    events = []
    base = item.originals.get("evidence", item.slots.get("evidence"))
    if base:
        events.append((item.line, None, str(base)))
    for name, raw, lineno in item.amendments:
        if name != AMEND_PREFIX + "evidence":
            continue
        m = _AMEND_VALUE.match(raw)
        if not m:
            # A malformed amendment is `item_shape`'s finding, already
            # reported there. Skipping it here rather than guessing a date
            # keeps one defect to one report.
            continue
        events.append((lineno, m.group(1), m.group(2)))
    return events


def perishable_never_rederived(item, today: str) -> list:
    """Flagged claims in one block — `PERISHABLE` with no later re-derivation.

    THE RULE, and it is falsifiable rather than a feeling. A mark fires if
    and only if NO evidence write sequenced after the mark's own introducing
    line names that mark's command — and the mark's day has passed.

    SEQUENCE, NOT DATE ARITHMETIC, and that is the whole of the same-day
    case (T-c3). Amendments are appended, so the carrier's own order IS the
    total order over evidence writes; an amendment sitting after the mark
    counts as later even when it carries the same date. Resolving same-day
    by comparing dates would deem a NORMAL IMMEDIATE REPAIR stale until
    tomorrow — an author who marks a claim perishable and re-derives it an
    hour later would be flagged for doing exactly the right thing, which is
    a guard firing on legitimate work (law 11).

    THE CLOCK APPEARS ONCE, and only where sequence cannot answer: has the
    mark's day PASSED. A mark written today has not yet had the day in which
    its re-derivation could arrive, so firing on it would again fire before
    the opportunity existed. It decides nothing about ordering — the
    must-not-build forbids a freshness rule that reads the clock instead of
    the carrier's order, and this reads the carrier's order and then asks
    one question the order cannot answer.

    WHAT IS NOT GRADED, deliberately: the re-derivation's RESULT. This asks
    only whether the command was NAMED in a later evidence write. Grading
    whether the re-derivation actually held would be a checker deciding
    whether a sentence is true, which is the thing the mark vocabulary
    exists to avoid doing.
    """
    events = evidence_events(item)
    flags = []
    for i, (lineno, _date, text) in enumerate(events):
        for mark_date, command in perishable_marks(text):
            want = " ".join(command.split())
            rederived = False
            for j in range(i + 1, len(events)):
                _ln, jdate, jtext = events[j]
                if jdate is not None and jdate < mark_date:
                    # OUT-OF-ORDER CARRIER. Appends are chronological, so
                    # this means the file was hand-edited; an earlier-dated
                    # write is not evidence of a LATER re-derivation and is
                    # not counted as one.
                    continue
                if want and want in " ".join(jtext.split()):
                    rederived = True
                    break
            if not rederived and mark_date < today:
                flags.append(PerishableFlag(item.ident, mark_date, command,
                                            lineno))
    return flags


def evidence_mark_problem(value: str) -> str | None:
    """Why this evidence value cannot be WRITTEN, or None (lc-167).

    AT THE WRITE DOORS ONLY, never at the parser. Every entry booked before
    this rule carries an unmarked slot, and a check over the carrier would
    fire on all of them at once — the guard firing on legitimate work, which
    trains the override reflex that kills it. The distinction is cheap
    exactly at booking, where the author still knows which half is which, and
    unreconstructable afterwards, which is the whole reason the mark exists
    rather than a later pass.
    """
    v = "" if value is None else str(value).strip()
    if not v or v.upper() == UNKNOWN:
        # Empty is `slot_value_problem`'s finding, not this one; UNKNOWN is
        # the migration's declared transitional value — an entry recording
        # that nobody has written evidence yet has nothing to mark.
        return None
    if _EVIDENCE_MARK.search(v):
        return None
    return ("the evidence slot carries no mark, so nothing in it says which "
            "sentences this session RAN and which it CONCLUDED. Mark each "
            "claim with one of: "
            + "; ".join(f"{m} ({EVIDENCE_MARK_GLOSS[m]})"
                        for m in EVIDENCE_MARKS)
            + ". A MIXED slot is the ordinary case and stays legal — most "
              "real evidence is part executed and part inferred, and the "
              "mark is per claim rather than per entry. What this refuses is "
              "a slot with no mark at all, because an unrun inference stated "
              "as fact then reads exactly like an executed command, and the "
              "entry that was wrong within the hour read exactly like the "
              "ones that held.")

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
#: THE CONDITIONAL SLOTS ARE AMENDABLE TOO, and leaving them out was a reach
#: defect rather than a decision. `_check_blocker` is reached by `item add`,
#: `item park` AND `item amend`, and all three DEMAND these values; only `add`
#: persisted one. `amend` refused outright — `amend_nothing_to_amend`, because
#: the slots were not in this tuple — and `park` validated the value and
#: dropped it. Measured at the effect site 2026-09-19, found by the slot's own
#: first real consumer within the hour it shipped.
#:
#: AMENDMENT IS THE RIGHT DOOR FOR THEM, not an in-place rewrite: a
#: derivability statement that turns out wrong is a CORRECTION, and this
#: carrier's whole ethic is that the superseded text stays readable. The
#: resolver puts an `amended-<slot>:` value in force even where the block
#: carries no base line at all, which is exactly the population needing
#: repair — every decision blocker booked before lc-179 existed.
AMENDABLE_SLOTS = (tuple(s for s in SLOTS if s != "grade")
                   + BLOCKER_ONLY_SLOTS)
AMEND_PREFIX = "amended-"
AMEND_REASON = "amend-reason"

#: Every amendment line's value opens with its ISO date. The date is a fixed
#: shape rather than a separator, deliberately: a ` — ` separator would be
#: refused inside any value that already carries one, and this carrier's
#: values carry them constantly (`requirement: … — record: …`). A guard that
#: fired on the ordinary value would stop the lane (R11).
_AMEND_VALUE = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(\S.*)$")


def opens_with_date(value: str) -> bool:
    """Does `value` already open with its ISO date?

    PUBLIC SO THE WRITER CAN ASK THE READER (lc-179). `verbs.py` composes a
    `not-derivable:` value and this module grades it; a second date pattern
    over there would be the divergence `grammar` exists to prevent, with the
    writer free to produce a shape its own reader refuses. Same reasoning as
    `closure_pointer_problem` being one predicate for both doors.
    """
    return bool(_AMEND_VALUE.match(value or ""))

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
    #: The value each amended slot held BEFORE any amendment resolved it —
    #: `slot -> original value`, set only for slots an amendment superseded.
    #:
    #: THE MISSING HALF OF `amendments` (lc-244). That field keeps the record
    #: of how a value got here and `slots` keeps the value in force, and
    #: between them the ORIGINAL was the one thing no reader could recover:
    #: `_resolve_amendments` overwrote it in place. It did not matter while
    #: every reader wanted the current value — and the first reader that
    #: wants the whole SEQUENCE is the perishable freshness check, whose
    #: whole subject is a mark written at booking and an amendment that may
    #: or may not have re-derived it. Reconstructing that from the file
    #: bytes at the reader would be a second parser for one fact.
    originals: dict = field(default_factory=dict)
    #: `(name, raw-value, lineno)` for every promotion line, IN FILE ORDER.
    #: Its OWN list rather than a share of `amendments`: these resolve NO
    #: slot — the grade they record moved in place — so folding them in would
    #: put lines with no slot to supersede through the resolver, and every
    #: reader of `amendments` would then be reading two kinds of act.
    promotions: list = field(default_factory=list)
    #: `(name, raw-value, lineno)` for every forward pointer, IN FILE ORDER.
    #: Its own list for the promotions' reason exactly: a pointer resolves no
    #: slot either. It says a LATER record exists and leaves every existing
    #: line asserting what it always asserted, which is what makes it a
    #: pointer rather than an amendment the done home is not allowed to have.
    closure_pointers: list = field(default_factory=list)

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
    #: `(ident, line)` for every `## <id>` heading in the ARCHIVE region —
    #: ids ONLY, bodies untouched (lc-177).
    #:
    #: THE ARCHIVE IS SKIPPED FOR A GOOD REASON AND THAT REASON IS ABOUT
    #: SHAPE. Pre-migration bodies are held verbatim and are not graded, so
    #: the parser stops at the heading. But two questions were riding on that
    #: one stop, and only one of them is about shape: WHICH IDS EXIST is a
    #: different question from IS THIS BODY WELL-FORMED, and the archive
    #: answers the first perfectly well. Measured here before the repair: a
    #: closure body below the heading was invisible to `next_ident`, which
    #: re-issued its id, and `item check` then printed `move integrity:
    #: CLEAN — no id in both homes (1 live, 1 done)` while the id sat in both
    #: files on disk.
    #:
    #: CONSERVATIVE BY CONSTRUCTION. A `## <id>` line inside quoted archive
    #: text would be read as an id in use; the cost of that is an id the
    #: allocator skips, which harms nothing, against the cost of the other
    #: direction, which is the collision above.
    archive_idents: list = field(default_factory=list)
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
            # IDS ONLY, and nothing else about these lines is read (lc-177).
            # The bodies stay ungraded — that exclusion is correct and is why
            # the parser stops here at all — while the ids they carry stop
            # being invisible to the allocator and to move integrity.
            for off, arch in enumerate(lines[i:]):
                am = _BLOCK_HEADING.match(arch)
                if am:
                    out.archive_idents.append(
                        (am.group(1).strip(), i + off + 1))
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
        # FORWARD POINTERS REPEAT TOO (lc-120), and are routed before the
        # repeat check for the amendment lines' reason: a body whose SECOND
        # correction is a shape finding has no route for that correction,
        # which is the defect this slot was added to end.
        if slot == CLOSURE_SUPERSEDED_BY:
            current.closure_pointers.append((slot, val, lineno))
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
               and s not in BLOCKER_ONLY_SLOTS
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

    # THE BLOCKER-TYPED SLOTS ARE LEGAL ONLY BESIDE THEIR TYPE (lc-175). A
    # slot legal everywhere is an annotation rather than a slot, which is the
    # direction `done_slot_on_live_item` above already sets. An exercise
    # record beside a blocker that runs no predicate records an act that
    # cannot have happened.
    #
    # PREFIX IS NOT NEEDED AND NOT PASSED: this asks only whether the blocker
    # IS the slot's type, and every non-match — item id, decision, NONE,
    # untyped prose — is equally not-evidence. Threading a prefix here to
    # sharpen a distinction the check does not make would be a second reader
    # of the blocker value with its own chance to disagree.
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

    # THE FORWARD POINTER IS GRADED ON ITS OWN SHAPE (lc-120), in its own
    # verdict for the reason the closure reason's date check is in one: these
    # lines are OPTIONAL and they REPEAT, so a check folded into a neighbour
    # would run only when that neighbour was present and only for the first
    # pointer. Every pointer on the block is graded, not just the first — the
    # second is exactly the one an append-only path exists to allow.
    for _name, raw, lineno in item.closure_pointers:
        problem = closure_pointer_problem(raw)
        if problem:
            out.problems.append((
                "item_shape", lineno,
                f"block {item.ident!r}: {problem}"))

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

    # CONDITIONAL-SLOT PLACEMENT IS GRADED AFTER RESOLUTION, and the position
    # of these lines is the whole check (P3). A conditional slot is legal
    # beside one TYPE of blocker, and which type this block carries is its
    # RESOLVED value — law 8's "an item's CURRENT truth comes from `item
    # slots`, which resolves amendments". Graded before the resolve, as it
    # was, this read the base line and failed in both directions:
    #
    #   LOUD — a re-type INTO a type made a correctly-placed slot read as
    #   misplaced. Found in operation, re-typing an item's blocker to
    #   `decision` on a ruling: the amendment was accepted at the door and
    #   the commit gate then refused the block the door had just written. A
    #   guard firing on legitimate work stops the lane (law 11), and this
    #   one stopped a ruling being executed at all.
    #
    #   SILENT — a re-type OUT of `evidence` left a stranded
    #   `blocker-exercise:` invisible, because the base line still said
    #   `evidence`. That is the direction that matters here: the stamp this
    #   part introduces is written for evidence-kind blockers only, and
    #   "the re-type clears the stamp" is unprovable if the check that would
    #   catch a stranded one cannot see it.
    #
    # PREFIX IS NOT NEEDED AND NOT PASSED: this asks only whether the blocker
    # IS the slot's type, and every non-match — item id, decision, external,
    # NONE, untyped prose — is equally not-evidence. Threading a prefix here
    # to sharpen a distinction the check does not make would be a second
    # reader of the blocker value with its own chance to disagree.
    for slot_, (want, row, what) in BLOCKER_SLOT_RULES.items():
        if slot_ not in item.slots:
            continue
        kind_, _detail = classify_blocker(item.slots.get("blocked-by", ""),
                                          None)
        if kind_ != want:
            out.problems.append((
                row, item.line,
                f"block {item.ident!r} carries `{slot_}:` beside a "
                f"`blocked-by` that is not a `{want}` blocker "
                f"({kind_ or 'untyped'}). The slot {what}. Beside any other "
                "type it records something that cannot have happened."))

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
    #
    # THAT SENTENCE IS TRUE ONLY ABOUT THE LAYOUT IT ARGUES AGAINST, and
    # measurement found the opposite failure in the layout it defends
    # (lc-165, 2026-09-18). Readers of this order take the line in the SLOT'S
    # POSITION as current and get the superseded value: cs-48's live
    # requirement contradicted its own later amendment, cs-35 took four
    # amendments in ninety minutes with superseded lines standing above the
    # true state, and in none of those cases did anyone read the top line as
    # the superseded one.
    #
    # NEITHER ORDER IS THE DEFECT, which is why this check is NOT inverted
    # and the order below still stands: whichever value sits in the slot's
    # position, a reader infers currency from WHERE THE LINE SITS, and in an
    # append-only block two values of one slot both legitimately exist.
    # Re-ordering moves the ambiguity to the other line. The repair is
    # EXPLICIT MARKING — a tool-written head line naming which slots carry an
    # amendment, with a check that it matches the amendments present — and it
    # is a new line in the block, so law 25 binds it to the schema wave. Left
    # standing here rather than silently corrected: the next reader would
    # otherwise re-derive this whole conflict from the comment alone.
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
        # FIRST WRITE WINS for the original: with two amendments to one slot
        # the value being superseded the second time is the FIRST
        # amendment's, which is already on `amendments`. What is unrecoverable
        # anywhere else is the booked value, and that is this one.
        item.originals.setdefault(slot, item.slots.get(slot))
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
BLOCKER_TYPES = ("item", "decision", "evidence", "external")

#: HOW EACH MEMBER IS SPELLED in a blocker slot, DERIVED so that every
#: message naming the closed set is one body (NIT2). Nine sites restated this
#: list in prose before the `external` member was minted, and a restated
#: vocabulary goes stale one site at a time: the member is added, eight
#: messages update, the ninth keeps telling authors the old set is closed.
#: A derived text cannot be falsified by ADDING a member — only by breaking
#: the derivation — which is why the arrangement that proves it mutates this
#: function rather than planting a member.
def blocker_type_spellings(prefix: str | None) -> tuple:
    """The spelling of each `BLOCKER_TYPES` member, in declaration order."""
    spelled = {
        "item": f"`{prefix or 'prefix'}-<n>`",
        "decision": "`decision <question>`",
        "evidence": "`evidence <predicate>`",
        "external": "`external <event>`",
    }
    # KeyError rather than a silent skip if a member is added without its
    # spelling: a message that quietly omitted the new member is exactly the
    # drift this function exists to remove, and it would read as complete.
    return tuple(spelled[m] for m in BLOCKER_TYPES)


def blocker_types_rendered(prefix: str | None) -> str:
    """The closed set as one comma-separated phrase, for a refusal's text."""
    return ", ".join(blocker_type_spellings(prefix))
BLOCKER_NONE = "NONE"

#: A dash by itself, whatever glyph a hand-typed value used: plain hyphen,
#: en dash, em dash. `is_blocker_none_synonym` treats all three the same,
#: since a keyboard or an editor's autocorrect picks whichever one it likes.
_BLOCKER_NONE_DASHES = ("-", "–", "—")


def is_blocker_none_synonym(value: str) -> bool:
    """Whether an UNTYPED `blocked-by` value SPELLS "nothing here" rather

    than a genuinely unrecognised edge (lc-266). `classify_blocker` already
    resolves the one true spelling, `NONE`, to the `"none"` type — this is
    only ever asked about a value it left untyped. Case-blind, so `None`,
    `NONE` written with a stray lowercase letter, and `n/a` all count; the
    dash form takes a plain hyphen, an en dash or an em dash.

    ONE FUNCTION, because it is called from both doors that refuse an
    untyped blocker (`items.check_blocker_targets`, `verbs._check_blocker`)
    and a second spelling of "reads as nothing" would drift from the first
    exactly where it matters — the two doors disagreeing about which values
    get the repair token.
    """
    v = (value or "").strip()
    if not v:
        return False
    if v.lower() in ("nothing", "none", "n/a"):
        return True
    return v in _BLOCKER_NONE_DASHES


#: The shared clause naming the repair for a NONE-synonym untyped value
#: (lc-266), interpolated by both doors rather than spelled twice. It
#: replaces the bypass-implying "reached the file by a path that did not
#: pass it" framing for exactly this case: the two causes it cannot tell
#: apart are a hand edit AROUND the door and an author with no access to
#: the door at all, and naming only the first would accuse the second.
BLOCKER_UNTYPED_SYNONYM_CLAUSE = (
    "reads as \"nothing here\" but is not the one token the vocabulary "
    "accepts for it — the repair is `blocked-by: NONE`. Either a hand "
    "edit landed near the door instead of through it, or this came from "
    "an author with no access to the door at all; the text does not say "
    "which."
)


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
    if v.startswith("external "):
        # D-8's minted member, and it is minted from RECORDED instances
        # rather than guessed: this carrier already held waits nothing here
        # can test — another repo's release, an operator's reply — and every
        # one of them was typed `evidence false`, a predicate that can never
        # fire. On the board that reads as ordinary machine-court waiting,
        # which is the neighbour-fold this contract exists to end.
        #
        # EVALUATED BY NOTHING, ON PURPOSE. The other two typed edges promise
        # a re-evaluation somebody can run; this one promises only that an
        # event has not happened yet. Its ENDING is therefore an ACT, not a
        # predicate — see `_blocker_state`, which says so in the rendering
        # rather than leaving a reader to look for a predicate to repair.
        rest = v[len("external "):].strip()
        return ("external", rest) if rest else (None, "")
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
    # THE CONDITIONAL SLOTS FOLLOW THE FIXED RUN, present-only (lc-175). They
    # are rendered HERE rather than by the caller for the reason this function
    # exists at all: one place spells the on-disk shape, so a verb that
    # composed the line itself could write a block its own checker refuses.
    for slot in BLOCKER_ONLY_SLOTS:
        if slots.get(slot):
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


def render_closure_pointer(date: str, ref: str, line: str) -> str:
    """The ONE line a forward-pointer act appends (lc-120).

    Spelled here and nowhere else, for `render_amendment`'s reason: the verb
    writes this shape and `closure_pointer_problem` grades it, so a literal at
    the writing end would be free to drift from the predicate at the reading
    end — and it would drift QUIETLY, the writer producing a line its own
    reader had stopped recognising.
    """
    return grammar.render_slot(CLOSURE_SUPERSEDED_BY, f"{date} {ref} {line}")


def append_closure_pointer(text: str, ident: str, date: str, ref: str,
                           line: str):
    """Append one forward pointer to a CLOSED block. `(text, found)`.

    THE SAME WALK the two appended kinds above use, and the reuse is the
    point: `_append_to_block` already backs over the blank lines between
    blocks, and a second walk written for the done home would land pointers in
    the gap — where they parse as belonging to the FOLLOWING body, which in a
    closure home is somebody else's closed record.
    """
    return _append_to_block(text, ident,
                            [render_closure_pointer(date, ref, line)])


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

    EVERY home is read — live, closed, and COMPACTED. Ids are immutable across
    moves, so an id allocator that looked only at the live carrier would
    re-issue the id of everything ever closed — and the collision would
    surface as a DUPLICATE finding months later, in a file nobody was editing.

    THE THIRD HOME IS THE COMPACTION RECORD (lc-148), and it is here because
    the sentence above was FALSE for one verb: `item compact` takes a body out
    of both carriers, so after it the ids it folded were in no home this
    function could see and `item add` re-issued them — measured, with `item
    check` reporting CLEAN throughout. The record was already written and
    already parsed; `retire.compacted_home` turns those ledger lines into a
    home in this shape, and every CALLER passes it beside the other two. A
    caller that passes only the carriers gets exactly the old behaviour, which
    is why the omission is invisible and why all three call sites moved in one
    change rather than one by one.

    AND IT WAS FALSE AGAIN, IN THIS FUNCTION'S OWN RETELLING OF THAT (lc-177).
    The paragraph above recounted lc-148 while "EVERY home is read" stayed
    wrong for a different reason: the done-home parse STOPS at
    `## Archive (pre-migration)`, so a closure body below that heading was in
    no home this function could see. Found in operation at a peer carrier —
    the allocator re-issued an id and `item add` wrote a second body under it
    — and reproduced here before the repair. The archive's ids are now read
    (`Parsed.archive_idents`) while its bodies stay ungraded, which is the
    only part of that exclusion anything ever needed.

    THE FALSE ASSURANCE WAS HALF THE DEFECT. A claim in prose beside a
    mechanism is held by nothing and inherits the mechanism's authority to
    every reader, so a sentence like "EVERY home is read" is what stops the
    next person looking. It is corrected here rather than left to be noticed
    a third time (law 26).
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
        # THE ARCHIVE REGION, ids only (lc-177). Without this the sentence
        # above is false in a fourth place: a closure body below the archive
        # heading is in no parsed home, so the allocator re-issues its id and
        # `item add` writes a second body under it into the live carrier.
        for ident, _line in getattr(p, "archive_idents", ()):
            n = grammar.id_number(prefix, ident)
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


def bump_compacted(text: str) -> tuple[str, bool]:
    """`(text, True)` with the head's `compacted:` count ONE higher.

    THE COUNT IS PERSISTED, NEVER RE-DERIVED, for the reason `conservation`
    above states about the whole right-hand side: a number recomputed from
    the files it grades moves with every corruption and stays green on all of
    them. So the compaction act increments it here.

    A HEAD CARRYING NO `compacted:` LINE RETURNS False rather than growing
    one. A key this function invented would put a value in the identity's
    right-hand side that no migration wrote, and the caller's answer to that
    is COULD NOT VERIFY — which is a different answer from a bump that
    happened, and must not share its exit code.

    Its own function beside `conservation` rather than a branch inside the
    compaction verb: the head's shape is this module's, and a second writer
    of a head line is the second spelling `grammar` exists to prevent.
    """
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if grammar.starts_section(ln):
            break
        if grammar.is_slot(ln, "compacted"):
            try:
                n = int(ln.split(":", 1)[1].strip())
            except ValueError:
                return text, False
            lines[i] = grammar.render_slot("compacted", n + 1)
            return "\n".join(lines), True
    return text, False


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
    # THE ARCHIVE REGION COUNTS HERE TOO (lc-177). This check read
    # `done_parsed.items`, which stops at the archive heading — so an id in
    # the live carrier AND in an archived body printed
    # `move integrity: CLEAN — no id in both homes`, a clean line over a
    # region the verb never parsed. That is lc-172's rule at a site lc-172
    # did not reach, which is why the CLEAN line below now states the
    # archived count rather than implying the done count is the whole file.
    done_side = ([(d.ident, d.line) for d in done_parsed.items]
                 + list(getattr(done_parsed, "archive_idents", ())))
    both = [(ident, live[ident], line)
            for ident, line in done_side if ident in live]
    for ident, live_line, done_line in both:
        out(f"FINDING [duplicate_id] id {ident!r} is in BOTH homes — live at "
            f"line {live_line}, done at line {done_line}. This is DUPLICATE "
            "and RECOVERABLE, never loss: a close appends to the done home "
            "and then deletes from the carrier, so a crash between the two "
            "leaves exactly this. The repair is to delete the LIVE copy once "
            "the done copy is confirmed complete — not to pick one at random.")
    if both:
        return exits.FINDING
    n_arch = len(getattr(done_parsed, "archive_idents", ()))
    out(f"move integrity: CLEAN — no id in both homes ({len(live)} live, "
        f"{len(done_parsed.items)} done"
        + (f", {n_arch} archived" if n_arch else "")
        + "). Every id in the done home was compared, the archive region "
          "included — its bodies are held verbatim and ungraded, and its IDS "
          "are read.")
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
        if not prefix:
            # NO PREFIX IS ITS OWN ANSWER AND IT IS GRADE-BLIND. Without a
            # declared prefix nothing can be typed at all — not here and not
            # in `check_parked_blockers`, which needs the same prefix — so
            # every blocked block is unresolved and the verb has formed no
            # verdict. Collected before the classify below, because
            # classifying against a prefix that does not exist is the
            # question this branch exists to refuse.
            untypeable.append((it, raw))
            continue
        kind, detail = classify_blocker(raw, prefix)
        if kind == "item":
            typed.append((it, detail))
        elif kind is None and it.grade != "PARKED":
            # UNTYPEABLE, AND IT USED TO BE DROPPED (lc-186). This arm read
            # `elif not prefix`, so a value the vocabulary does not recognise
            # was collected ONLY when no prefix was declared — with one
            # present it matched neither arm and was counted nowhere. Measured
            # by a review lane: a READY item blocked by a mistyped id printed
            # `blocker targets: CLEAN — 4 item-id blocker(s)` with the fifth
            # in neither the count nor the output, while the well-formed
            # spelling of the same blocker correctly found `dangling_reference`.
            #
            # `check_parked_blockers` covers PARKED only, so a READY item
            # carrying one had nothing at all — which is precisely the
            # permanent silent park this function's own docstring is about.
            #
            # AND PARKED IS EXCLUDED HERE FOR THE SAME REASON, which is this
            # item's own must-not-move rather than caution: `parked_without_
            # typed_blocker` already reports exactly this input on a PARKED
            # block, and a second finding for one defect tells the reader
            # there are two. Measured the moment this arm first ran: a fixture
            # with two PARKED prose blockers went from 2 finding lines to 4.
            # The gap was never PARKED — it was every OTHER grade.
            untypeable.append((it, raw))

    if not prefix and untypeable:
        # NO PREFIX IS A DIFFERENT ANSWER FROM A BAD VALUE, and the split is
        # the point: without a declared prefix the tool cannot TELL an id from
        # prose, so it has formed no verdict about these blocks. That is
        # could-not-verify. With a prefix it can tell, and a value it cannot
        # type is a finding about the value.
        out("COULD NOT VERIFY: no `id-prefix` in the declaration, so an "
            f"item-id blocker on {len(untypeable)} block(s) cannot be told "
            "from prose that resembles one, and none was resolved.")
        return exits.COULD_NOT_VERIFY
    for it, raw in untypeable:
        # THE EXISTING ROW, not a new one: this is the same refusal the write
        # path emits for the same input (`verbs._check_blocker`), reached by
        # the other door. A second row for one refusal would need its own
        # plant and control to say anything the first does not.
        if is_blocker_none_synonym(raw):
            # lc-266: a NONE-synonym gets the repair token instead of the
            # bypass-implying framing below — "today's text" is kept for
            # every OTHER untyped value, unchanged.
            out(f"FINDING [blocker_untyped] line {it.line}: block "
                f"{it.ident!r} is blocked by {raw!r}, which "
                f"{BLOCKER_UNTYPED_SYNONYM_CLAUSE} It is a permanent silent "
                "park either way: the block reads as blocked and never "
                "surfaces in `item ready`, and nothing resolves a wait "
                "nobody can type.")
            continue
        out(f"FINDING [blocker_untyped] line {it.line}: block {it.ident!r} is "
            f"blocked by {raw!r}, which is not one of the closed edge types "
            f"({blocker_types_rendered(prefix)}, "
            "or NONE). The write path refuses this at `item add`, `item park` "
            "and `item amend`, so a value in this shape reached the file by a "
            "path that did not pass it — a merge, a hand edit, or a target "
            "renamed after the fact. It is a permanent silent park either "
            "way: the block reads as blocked and never surfaces in `item "
            "ready`, and nothing resolves a wait nobody can type.")
    if untypeable:
        return exits.FINDING
    if not typed:
        # A VERDICT WITH NO OUTPUT IS NOT READABLE AS A VERDICT (lc-186, and
        # lc-172's rule at a site it did not reach). This returned CLEAN and
        # printed NOTHING, so a carrier with no item-id blockers was
        # indistinguishable in the report from a check that never ran.
        out(f"blocker targets: CLEAN — 0 item-id blocker(s) among "
            f"{len(items_parsed.items)} block(s) examined, so there was no id "
            "to resolve. A zero here is a measurement over a population that "
            "was read, not an absence of checking.")
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


#: A trailing shell `# comment` on an evidence predicate, stripped the SAME
#: way `verify.py`'s own RUN-line parser already strips one from a Verify
#: block's command (`verify.py`, `parse_block`, `re.sub(r'\s+#.*$', '', ...)`)
#: — the same idiom, read and reused rather than a second one invented beside
#: it. A shell already treats `#` this way when it RUNS the predicate
#: (`lanes.evaluate_trigger`), so this only makes the TEXT comparison agree
#: with what the shell would actually execute.
_TRAILING_SHELL_COMMENT = re.compile(r"\s+#.*$")


def _is_unclearable_evidence(predicate: str) -> bool:
    """Is this evidence predicate PROVABLY unable to ever clear (lc-193).

    NARROW ON PURPOSE, and the narrowness is the whole point. §3.1's
    MUST-NOT-MOVE is that an evidence predicate simply not true YET is not a
    softlock — `lanes.evaluate_trigger`'s QUIET (exit 1) is the ordinary,
    expected, everyday state of a wait that has not resolved, and lc-164
    already grades those at booking; this function must not re-judge them.
    The one case this repo can PROVE without running anything, and the one
    the entry's own measurement found eight live instances of, is the
    literal shell command `false` — POSIX-guaranteed to exit 1
    UNCONDITIONALLY, every time, forever, by definition of the builtin
    rather than by anything the world does. That is categorically different
    from "the check has not gone green yet": no future state of the
    filesystem, the network, or another repo can ever flip it. Nothing else
    is treated as unclearable — not `exit 1`, not `/bin/false`, not `true &&
    false` — because proving those would need more than a text comparison,
    and a check that reached for that reach would be reasoning about the
    world rather than reading a closed, deliberately narrow vocabulary.
    """
    command = _TRAILING_SHELL_COMMENT.sub("", predicate).strip()
    return command == "false"


def check_blocker_graph(items_parsed: Parsed, out, prefix: str | None) -> int:
    """Traverse the item-id blocker GRAPH, not just its edges (lc-193).

    `check_blocker_targets` above, and the write path's `_check_blocker`,
    both ask a per-EDGE question: does the id an item-id blocker names
    exist, and is it buried. Neither asks whether the GRAPH those edges
    form can ever drain. So `xx-A blocked-by xx-B` and `xx-B blocked-by
    xx-A` both resolve, neither is dangling, neither is dropped, and both
    items wait forever while `item ready` renders each as ordinary BLOCKED
    work and `item check` reports CLEAN — the operator's player-loop frame
    names this a SOFTLOCK: a state reached legitimately from which no
    progress is possible, and the game does not say so. This is lc-14's own
    "permanent silent park" (quoted in `check_blocker_targets`'s docstring)
    reached by a different route: that check was built to watch the edge it
    came in on, never the condition it names.

    THE COMPUTABLE SLICE IS EXACTLY TWO SHAPES AND NO MORE, per the entry's
    own scope, and this function does not extend it:

    1. a CYCLE among item-id blockers — any ring, not only a length-2 one;
    2. a CHAIN of item-id blockers terminating in a member whose OWN
       blocker is the literal, provably-unclearable `evidence false`
       (`_is_unclearable_evidence`) — chain length ONE is the base case: an
       item can name itself with no item-id links at all.

    THE THREE MUST-NOT-MOVE RULES, each a way this could become the R11
    guard that fires on legitimate work: (1) a DECISION blocker is waiting
    on a party, which is the system working, and is never reported; (2) an
    EVIDENCE predicate that is simply not true YET is not re-judged — only
    the literal, provable idiom is; (3) this function REPORTS and never
    unblocks anything — breaking a cycle is a judgment about which item was
    booked wrong, which stays the desk's.

    EDGES ARE `classify_blocker`'s THIRD BRANCH, THE SAME CLOSED VOCABULARY
    `check_blocker_targets` reads — a second reading would disagree with the
    first exactly where it matters. A blocker this function cannot type
    (`kind is None`) or that names an id no LIVE item holds (closed,
    dropped, or never existed) is `blocker_untyped` / `dangling_reference`'s
    business, reported there and not duplicated here: reaching such a
    target simply LEAVES this function's graph, which is not itself a
    finding — a chain into a DONE target has already been answered, exactly
    as `_blocker_state`'s own DONE branch reads it.

    REACH, STATED RATHER THAN LEFT TO BE DISCOVERED: item-id EDGES need the
    declared `id-prefix` to be told apart from prose at all (the same
    dependency `classify_blocker` itself has), so without one this function
    sees no edges and therefore no cycle and no multi-hop chain — but a
    length-ONE unclearable terminal needs no prefix, because `evidence` and
    `NONE` and `decision` are recognised by their own fixed leading words
    regardless. So this does NOT fall back to COULD NOT VERIFY on a missing
    prefix the way `check_blocker_targets` does: the narrower shape stays
    fully checkable, and only the graph's reach beyond one hop is reduced.
    A future caller wiring this beside `check_blocker_targets` in `item
    check`'s pipeline (cli.py, outside this change's write-set) should say
    so alongside it if that limit matters to the reader.
    """
    by_id = {it.ident: it for it in items_parsed.items}
    edges: dict[str, str] = {}
    terminals: dict[str, tuple] = {}
    for it in items_parsed.items:
        kind, detail = classify_blocker(it.slots.get("blocked-by", ""), prefix)
        if kind == "item":
            edges[it.ident] = detail
        elif kind is not None:
            terminals[it.ident] = (kind, detail)
        # kind is None: untyped prose, `blocker_untyped`'s finding already
        # covers it, and it forms no edge and no terminal here.

    # --- shape 1: CYCLES among item-id blockers -----------------------------
    # A FUNCTIONAL graph — every node has out-degree at most one, since a
    # block carries a single `blocked-by` value — so a walk from any node
    # either leaves `edges` (terminal or a target outside the live carrier)
    # or re-enters a node already on the CURRENT walk, which is the ring.
    UNSEEN, IN_PROGRESS, DONE = 0, 1, 2
    status: dict[str, int] = {}
    cycles: list = []
    for start in edges:
        if status.get(start, UNSEEN) != UNSEEN:
            continue
        path: list = []
        node = start
        while True:
            if node not in edges:
                for n in path:
                    status[n] = DONE
                break
            st = status.get(node, UNSEEN)
            if st == IN_PROGRESS:
                i = path.index(node)
                ring = tuple(path[i:])
                cycles.append(ring)
                for n in path:
                    status[n] = DONE
                break
            if st == DONE:
                for n in path:
                    status[n] = DONE
                break
            status[node] = IN_PROGRESS
            path.append(node)
            node = edges[node]

    # --- shape 2: CHAINS terminating in a member that can NEVER CLEAR ------
    # Reversed once, so every ancestor of an unclearable terminal is found in
    # one walk rather than re-walking the same suffix once per ancestor.
    rev: dict[str, list] = {}
    for src, dst in edges.items():
        rev.setdefault(dst, []).append(src)

    def _ancestors(root: str) -> list:
        members = [root]
        seen = {root}
        frontier = [root]
        while frontier:
            nxt = []
            for n in frontier:
                for anc in rev.get(n, ()):
                    if anc not in seen:
                        seen.add(anc)
                        members.append(anc)
                        nxt.append(anc)
            frontier = nxt
        return members

    chains: list = []
    for ident, (kind, detail) in terminals.items():
        if kind == "evidence" and _is_unclearable_evidence(detail):
            chains.append((ident, sorted(_ancestors(ident))))

    n_findings = len(cycles) + len(chains)
    if not n_findings:
        out(f"blocker graph: CLEAN — {len(edges)} item-id blocker edge(s) "
            "traversed, no cycle and no chain terminating in a member that "
            "can never clear.")
        return exits.CLEAN

    for ring in sorted(cycles):
        out(f"FINDING [blocker_softlock] a CYCLE among item-id blockers: "
            + " -> ".join(ring) + f" -> {ring[0]}. Every member waits on "
            "another member of this same ring, so none of them can ever "
            "become schedulable — the ring's own resolution is what each "
            "member is waiting for, and nothing outside the ring can supply "
            "it. `item ready` renders each as ordinary BLOCKED work and "
            "`item check` reports CLEAN on the edges alone: this is the "
            "softlock the player-loop frame names, a state reached "
            "legitimately from which no progress is possible. This reports "
            "the ring; breaking it is a judgment about which item was "
            "booked wrong, and stays the desk's.")
    for terminal, members in sorted(chains):
        _kind, detail = terminals[terminal]
        others = [m for m in members if m != terminal]
        chain_desc = (f"{terminal} directly" if not others
                      else f"{', '.join(others)} -> {terminal}")
        out(f"FINDING [blocker_softlock] a CHAIN terminating in a member "
            f"that can NEVER CLEAR: {chain_desc}. {terminal!r}'s evidence "
            f"predicate ({detail!r}) is the literal command `false`, which "
            "exits 1 unconditionally and forever by construction — not "
            "evidence that has simply not arrived yet, which this check "
            "does not and must not re-judge (lc-164 already grades that at "
            "booking). Every member named here waits, directly or through "
            "another member, on a predicate that can never fire, and "
            "`item ready` renders each as ordinary machine-court waiting.")
    out(f"blocker graph: FINDING — {len(cycles)} cycle(s), {len(chains)} "
        f"unclearable chain(s), over {len(edges)} item-id blocker edge(s) "
        "traversed.")
    return exits.FINDING


# --- the census: three answers -----------------------------------------------

def census(parsed: Parsed) -> dict:
    """open / closed / cannot-express / unknown-with-counts.

    FOUR answers, and the fourth is new (D-3, P1). An unknown grade word is
    neither open nor closed and is never folded into either: the drain and
    retirement triggers read these numbers, and a counter that guessed would
    inflate exactly the ones that decide whether a repo owes a pass.

    CANNOT-EXPRESS IS NOT UNKNOWN, and that distinction is this bucket's
    whole reason. An unknown word arrived by a merge or an older tool — it is
    a reading failure, and `item check` answers COULD NOT VERIFY over it. A
    `cannot-express(<date>): <reason>` grade is the vocabulary's own declared
    arm: somebody reached a state the five grades cannot say and RECORDED
    that, with a date and a reason. Counting it as unknown would report a
    working mechanism as a broken carrier, and — worse in the direction that
    matters — would inflate the very figure a reader consults to decide
    whether the carrier is healthy.

    THE COUNT IS THE DISPOSITIONS-OWED FIGURE. An instance leaves by being
    amended away (re-typed to a real member once one exists, or its slot
    corrected), so zero means drained, and the OLDEST date is what the drain
    act's trigger reads. Both are returned rather than printed here: this
    function counts, and the verb that prints decides how to say it.

    A MALFORMED CLAIM COUNTS AS UNKNOWN, deliberately. `cannot-express:` with
    no date cannot be aged, and an instance that can never become the oldest
    is one the drain can never see reach zero — so it belongs in the bucket
    that already means "somebody must look at this", not in the one whose
    emptiness is a health claim.
    """
    from . import vocab

    open_n = closed_n = 0
    unknown: dict = {}
    oov_dates: list = []
    for it in parsed.items:
        g = it.grade
        if g in GRADES_OPEN:
            open_n += 1
        elif g in GRADES_CLOSED:
            closed_n += 1
        else:
            parsed_oov = vocab.parse_oov(g)
            if parsed_oov is not None:
                oov_dates.append(parsed_oov.date)
            else:
                unknown[g or "(empty)"] = unknown.get(g or "(empty)", 0) + 1
    return {"open": open_n, "closed": closed_n, "unknown": unknown,
            "cannot-express": len(oov_dates),
            "cannot-express-oldest": min(oov_dates) if oov_dates else None,
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
                f"{blocker_types_rendered(prefix)} — because an aging item is routed "
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

    # THE UNEXERCISED EVIDENCE BLOCKERS ARE COUNTED, NOT RAISED (lc-175).
    # The done-criterion asks that a blocker without an exercise record be
    # "visible as such rather than silently unexercised", and a COUNT is what
    # satisfies that without making every pre-existing blocker a finding the
    # day the slot ships (MUST-NOT-MOVE). It is I5's move from the-loop.md:
    # the repair for an invisible absence was never a better duty, it was a
    # count that makes a zero answerable.
    #
    # BOTH NUMBERS, because one of them alone is a label over a body: the
    # exercised count is what proves the line can ever move, and a bare
    # "0 unexercised" over a carrier holding no evidence blockers at all
    # reads exactly like a carrier whose blockers are all exercised.
    exercised, owed, predates = blocker_slot_census(parsed, BLOCKER_EXERCISE)
    if exercised or owed or predates:
        # THE LINE SPLITS, IT DOES NOT RENAME (D-7, lc-175's MUST-NOT-MOVE).
        # `UNEXERCISED` stays the umbrella and keeps its meaning — an
        # unexercised blocker is still visible AS absent and still not a
        # finding — and the split names the two states inside it. Dropping
        # the word would have moved lc-175's guarantee while claiming to
        # honour it; its own test is what said so.
        out(f"evidence blockers: {exercised} exercised, {owed + predates} "
            f"UNEXERCISED — of those {owed} OWED "
            f"(stamped at the door, arms not yet written) and {predates} "
            "PREDATES THE MECHANISM (booked before the door stamped, so "
            "nobody had the opportunity). An exercise "
            "nobody can see is a discipline that holds only while the person "
            "who held it is in the room; lc-164's booking run proves the "
            "predicate can say NOT YET and cannot prove it ever says "
            "ARRIVED. The THIRD count is not a quieter spelling of the "
            "second: only OWED is work this carrier can ask anyone for.")

    # THE PERISHABLE FLAG (lc-244, W2). A REPORT LINE, never a finding: a
    # claim whose re-derivation is owed is not a defect in the carrier, and
    # a refusal here would fire on entries whose authors did exactly the
    # right thing by marking the rot in the first place — which would teach
    # the lesson "do not mark it" (law 11).
    #
    # BOTH NUMBERS AGAIN, for the reason the blockers line gives: a bare
    # "0 flagged" over a carrier carrying no perishable marks at all reads
    # exactly like a carrier whose every perishable claim is fresh, and only
    # the second number tells those apart.
    from datetime import date as _date
    today = _date.today().isoformat()
    marked, flagged = 0, []
    for it in parsed.items:
        # THE SAME WALK the flag uses. Counted any other way, the
        # denominator and the verdict answer about different populations.
        marked += sum(len(perishable_marks(text))
                      for _ln, _date, text in evidence_events(it))
        flagged.extend(perishable_never_rederived(it, today))
    if marked:
        if flagged:
            out(f"perishable evidence: {marked} mark(s), {len(flagged)} "
                "NEVER RE-DERIVED — "
                + "; ".join(f"{f.ident} ({f.date}, re-derive: {f.command})"
                            for f in flagged[:8])
                + ("" if len(flagged) <= 8 else
                   f"; and {len(flagged) - 8} more")
                + ". Each names the command that re-takes it, so the repair "
                  "is one run and one `item amend --evidence` carrying the "
                  "dated result — a demand that writes nothing at the "
                  "consuming moment is a demand measured at zero (W-8).")
        else:
            out(f"perishable evidence: {marked} mark(s), 0 never "
                "re-derived — every perishable claim has a later evidence "
                "write naming its own command. The first number is the "
                "denominator this verdict rests on: zero flagged over zero "
                "marks would print the same and mean nothing.")

    # THE DERIVABILITY COUNT (lc-179), the same move one slot over. lc-169
    # demands the statement at the door and persists nothing, so today every
    # decision blocker in both homes is identical on this axis — the ones
    # booked WITH a statement are indistinguishable from the ones booked
    # before that demand existed. The named consumer is lc-158: a decision
    # blocker MIS-TYPED at booking, read as a decision and actually a factual
    # question a measurement could settle. That class is findable from a
    # persisted statement and unfindable from a printed one.
    stated, stamped, unstated = blocker_slot_census(parsed, NOT_DERIVABLE)
    if stated or stamped or unstated:
        out(f"decision blockers: {stated} with a derivability statement, "
            f"{stamped + unstated} UNSTATED (no `{NOT_DERIVABLE}:` record). "
            "lc-169 "
            "demands the statement at the door; what is printed there "
            "scrolls away, so a blocker whose reason was stated and one "
            "whose reason never existed read the same to every later "
            "reader.")

    c = census(parsed)
    out(f"census: open {c['open']}  closed {c['closed']}  "
        f"unknown {sum(c['unknown'].values())}  (total {c['total']})")
    for word_, n in sorted(c["unknown"].items()):
        out(f"  unknown grade {word_!r}: {n} — READ, never folded into open "
            "or closed. It reached this file by a merge or an older tool.")
    if c["cannot-express"]:
        # THE DISPOSITIONS-OWED LINE (D-3). Printed only when nonzero: a
        # standing "0 cannot-express" would add a line to every run of every
        # session for a number whose whole meaning is that it is not zero,
        # and a readout nobody reads is where the one real instance would
        # arrive pre-discounted.
        out(f"cannot-express: {c['cannot-express']}, oldest "
            f"{c['cannot-express-oldest']} — states the closed vocabulary "
            "could not say, RECORDED with their reasons rather than filed "
            "under a neighbour. This count IS the dispositions owed: an "
            "instance leaves by being amended away, to a real member once "
            "one exists or to a corrected slot, and the reasons are what a "
            "widening is minted FROM. Zero means drained.")
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

    # THE CONDITIONAL SLOTS ARE PRINTED WHERE THEY ARE PRESENT (lc-175). This
    # verb is the pickup instrument — the entries' own rule is "`item slots`
    # at pickup, never directive prose" — so a slot this reader cannot see is
    # a slot the desk picking the item up does not know exists. Present-only,
    # never padded with a blank: an empty line for a slot that is not legal on
    # this block would report an absence where there is no slot to be absent.
    shown = list(SLOTS) + [s for s in BLOCKER_ONLY_SLOTS if s in item.slots]
    slots = {slot: item.slots.get(slot, "") for slot in shown}
    if args.json:
        out(json.dumps({"ident": item.ident, "slots": slots}, ensure_ascii=False))
    else:
        for slot in shown:
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
            if slot in UNKNOWN_LEGAL_SLOTS:
                counts[slot] = counts.get(slot, 0) + 1
            else:
                misplaced.append((it.ident, it.line, slot))
    return counts, misplaced


def blocker_slot_census(parsed: Parsed, slot: str,
                        prefix: str | None = None):
    """`(recorded, missing)` for one conditional blocker slot (lc-175, lc-179).

    THE POPULATION IS THE MATCHING BLOCKER TYPE, never all items: an item
    with no predicate has nothing to exercise and one with no question has no
    derivability to state, so folding them into the denominator would make
    the number fall every time an unrelated item is booked — a metric that
    moves for reasons its subject did not.

    UNKNOWN COUNTS AS MISSING, and that is the migration's whole point: the
    transitional value means nobody ever recorded one, which is exactly what
    the missing bucket is for. These slots are NOT in `UNKNOWNABLE_SLOTS`, so
    the value reaches this count without reaching `ready_with_unknown_slot`.

    ONE FUNCTION FOR BOTH SLOTS rather than a second copy: the question is
    identical one word over, and two bodies for one question is where a
    divergence hides — the second would be the one nobody re-reads when the
    rule moves.
    """
    want = BLOCKER_SLOT_RULES[slot][0]
    recorded = owed = predates = 0
    for it in parsed.items:
        kind, _detail = classify_blocker(it.slots.get("blocked-by", ""),
                                         prefix)
        if kind != want:
            continue
        v = (it.slots.get(slot) or "").strip()
        if not v or v.upper() == UNKNOWN:
            # NEITHER A RECORD NOR A STAMP: this block never passed through
            # the stamping door, so nobody ever had the opportunity to
            # exercise it. That is a THIRD answer and not a quieter spelling
            # of "missing" — folding it into owed counts work nobody could
            # have done, in the very figure a desk reads to decide whether it
            # owes any.
            predates += 1
        elif v.startswith(SLOT_STAMP_NONE_YET):
            owed += 1
        else:
            recorded += 1
    return recorded, owed, predates


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


#: THE CORRESPONDENCE (lc-135). `repair_shape`'s judgment classes are a
#: SECOND VOCABULARY over findings the checker (`check_file` /
#: `check_done_file`) already carries: a row says WHAT IS WRONG, a judgment
#: class says WHAT THE VERB DECLINED TO REPAIR AND WHY. Desk measurement
#: 2026-09-15 over copies of dotfiles' carriers found the mapping
#: one-to-one: closed-still-blocked -> blocked_in_done_home (4/4),
#: missing-slot and unknown-slot -> item_shape (5/5) — and
#: unjoinable-continuation the same way (a continuation with no host is a
#: malformed `slot: value` line under the live check too). Declared here,
#: beside the JUDGMENT_* constants it maps, because the mapping IS the
#: correspondence this item pins — widen it here and
#: `reconcile_repair_judgments` widens with it, with no second edit.
JUDGMENT_TO_ROW = {
    JUDGMENT_MISSING: "item_shape",
    JUDGMENT_UNKNOWN: "item_shape",
    JUDGMENT_UNJOINABLE: "item_shape",
    JUDGMENT_BLOCKED_CLOSED: "blocked_in_done_home",
}

#: The checker rows this reconciliation compares against — DERIVED from the
#: mapping's own values, never repeated: a row this file's checkers emit for
#: reasons `repair_shape` never judges (an id/prefix mismatch, say) is
#: outside this set and outside the comparison, exactly because no judgment
#: class could ever name it.
_RECONCILED_ROWS = frozenset(JUDGMENT_TO_ROW.values())

#: A `Path` the checker never reads from disk — `check_file`/`check_done_file`
#: only consult it for `Finding.name` when `text=` is given, so this stands in
#: for whichever real carrier the reconciliation is asked about.
_RECONCILE_PATH = Path("<reconciliation>")


@dataclass
class JudgmentReconciliation:
    """Whether `repair_shape`'s judgments and the checker's residual findings
    — over the SAME (repaired) carrier text — name the same bodies.

    Two closed lists, sorted `(ident, row)` pairs, EMPTY when the vocabularies
    agree:

    - `listed_only`: a body `repair_shape` judged that no residual finding
      matches — either the checker's row for it went silent, or the judgment
      class is not in `JUDGMENT_TO_ROW` at all (a class added with no row).
    - `residual_only`: a residual finding under a row this file's `--test`
      believes `repair_shape` covers, with no matching judgment — a row
      that started firing on a body the verb was never taught to declare.

    THE TWO VOCABULARIES STAY SEPARATE. This pins their CORRESPONDENCE, over
    identity, never their prose and never a count: equal counts are not
    agreement, and `agrees` is the only verdict this dataclass renders.
    """
    listed_only: list = field(default_factory=list)
    residual_only: list = field(default_factory=list)

    @property
    def agrees(self) -> bool:
        return not self.listed_only and not self.residual_only


def reconcile_repair_judgments(text: str, checker, prefix: str | None = None
                               ) -> JudgmentReconciliation:
    """Run `repair_shape`, then `checker` over the REPAIRED text, and compare.

    `checker` is `check_file` or `check_done_file` — whichever owns the
    carrier `text` belongs to; both share the `(path, out, prefix=, text=,
    collect=)` shape this calls them with. Grading the REPAIRED text, not the
    original, is what makes the checker's findings RESIDUAL: every join and
    move `repair_shape` actually performed already cleared its own finding,
    so what is left over is exactly the population a judgment class should
    explain — a defect check_file/check_done_file report BEFORE repair but
    not after would silently vanish from both sides of this comparison, and
    that is a difference the mechanical half accounts for, not the drift
    lc-135 exists to catch.
    """
    repaired = repair_shape(text, prefix=prefix)

    # `row` is None when `cls` carries no entry in JUDGMENT_TO_ROW — a
    # judgment class with no row, which can never equal a real finding's
    # `(ident, row)` pair below and so always lands in `listed_only`.
    judged = {(ident, JUDGMENT_TO_ROW.get(cls))
              for ident, cls, _detail in repaired.judgments}

    collected: list = []
    checker(_RECONCILE_PATH, lambda _s: None, prefix=prefix,
            text=repaired.text, collect=collected)
    residual = {(f.ident, f.row) for f in collected
                if f.row in _RECONCILED_ROWS}

    def _key(pair):
        return (pair[0] or "", pair[1] or "")

    return JudgmentReconciliation(
        listed_only=sorted(judged - residual, key=_key),
        residual_only=sorted(residual - judged, key=_key))


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
        # ONE HOME FOR THE MESSAGE, never both streams — every other verb in
        # this repo renders COULD NOT VERIFY through out(), and this was the
        # package's one err() emit of the phrase (lc-132). `err` stays a
        # parameter: cli.py's caller still supplies one, and narrowing the
        # signature is a change to a file outside this item's write-set.
        for why in unverified:
            out(f"COULD NOT VERIFY: {why}")
        # "condition(s)", not "carrier(s)": a carrier can be scanned AND
        # still carry a could-not-verify, so counting carriers here would
        # contradict the "counted over N of M" line directly above it.
        out(f"item check --staged: {exits.word(exits.COULD_NOT_VERIFY)} — "
            f"{len(unverified)} could-not-verify condition(s), so the counts "
            "above are not a full verdict.")
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
WAVE_VENUE = "venue"
WAVE_FOREIGN = "other-repo"

#: WHY a bucket sits outside the lanes — two reasons, not one, and they route
#: to different repairs. The join COULD NOT READ a missing slot or a prose
#: one: a reading failure, repaired by somebody rewriting the slot. It read a
#: venue and a `<path>@<repo>` boundary perfectly well; those name NO FILE
#: HERE, which is repaired by nothing, because nothing is wrong with them.
#:
#: BOTH still count toward the exit contract — an item that is not in the plan
#: is not in the plan, whatever the reason — so this split changes the
#: SENTENCE and never the code. Saying the join "could not read"
#: `decision:who-seeds-greenfield-carriers` is an assurance wider than the
#: predicate establishes: it reads it fine, and lc-125 exists to say so. The
#: same sentence was already false of `<path>@<repo>`, which this report had
#: called unreadable since lc-123 — the venue bucket is what made the older
#: instance visible.
WAVE_UNREADABLE = (WAVE_UNSET, WAVE_PROSE)
WAVE_NOT_A_FILE_HERE = (WAVE_VENUE, WAVE_FOREIGN)

#: The non-lane buckets, in report order. COMPOSED from the two reasons rather
#: than listed again, so a bucket cannot belong to a reason and be missing
#: from the report — or sit in the report under no reason at all, which is how
#: the sentence above came to describe a population it no longer matched.
WAVE_NON_PATH = WAVE_UNREADABLE + WAVE_NOT_A_FILE_HERE

#: A repo-relative path ENTRY. Deliberately narrow: a space, a parenthesis, a
#: semicolon or a colon means the author wrote prose or a VENUE
#: (`decision:<question>`, which `item add --write-set` accepts beside paths),
#: and prose read as a path would put an item in a lane on a boundary nobody
#: stated. A TRAILING SLASH marks a directory entry — the only directory form
#: recognised here, because deriving directory-ness from the working tree
#: would make the join depend on what happens to exist today rather than on
#: the slot the desk wrote.
_WAVE_PATH_ENTRY = re.compile(r"^[A-Za-z0-9._][A-Za-z0-9._/-]*$")

#: A VENUE entry — `<word>:<rest>`, the shape `item add --write-set` accepts
#: beside paths (`decision:who-seeds-greenfield-carriers`). It is a LEGAL slot
#: value naming a boundary that is not a file, so it earns its own bucket
#: rather than the prose label it wore: prose says a human must rewrite the
#: slot, a venue says the boundary genuinely is a decision and there is
#: nothing to rewrite. Two answers, two repairs.
#:
#: DELIBERATELY NARROWER THAN `<word>:<rest>` READS, and the narrowing is the
#: whole shippability question: a PATH can wear that shape too. The word half
#: admits no slash and no dot, so `docs/notes:draft.md` and
#: `plugin/cli/x.py:12` are excluded by their prefix; the rest half admits no
#: dot, so `notes:draft.md` is excluded by its extension. Everything doubtful
#: therefore stays PROSE, which is the conservative direction: a venue
#: miscalled prose is the status quo this bucket improves on, while a path
#: miscalled a venue is a defect newly wearing a legal value's label — the
#: same inversion pointing the other way, and the worse one.
_WAVE_VENUE_ENTRY = re.compile(r"^[a-z][a-z0-9-]*:[A-Za-z0-9][A-Za-z0-9_-]*$")


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
    venues = [e for e in unparsed if _WAVE_VENUE_ENTRY.match(e)]
    # ALL of the unreadable half must be venues, never merely some: one
    # genuinely prose entry makes the slot unreadable, and prose is the
    # answer that says a human has to rewrite it. A slot graded `venue` on
    # its venue entries alone would hide the prose one behind a legal label.
    if unparsed and len(venues) == len(unparsed):
        return (WAVE_VENUE, [],
                f"names a VENUE, not a path: {venues[0]!r} "
                f"({len(parses)} of {len(entries)} entry/entries parse as "
                "paths — a venue is a LEGAL write-set value this join cannot "
                "cluster, not a defect)")
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


def wave_entry_frequency(rows):
    """`{entry: how many of these items name it}` — CARRIER-WIDE.

    Counted over ITEMS, never over occurrences, and over the same population
    the join above runs on: the number's whole meaning is "how many writers
    would a group cut here hold", so an item naming one file twice must not
    make that file look like two carriers.
    """
    freq: dict = {}
    for _ident, paths in rows:
        for p in set(paths):
            freq[p] = freq.get(p, 0) + 1
    return freq


def wave_group_key(paths, freq):
    """The entry an item is GROUPED BY: its most-frequent path, ties by name.

    The tie-break is alphabetical rather than slot order, because slot order
    is the desk's typing order — a partition that moved when someone
    reordered a comma-separated list would be a plan nobody could reproduce.
    """
    return min(paths, key=lambda p: (-freq.get(p, 0), p))


def wave_groups(rows):
    """`[(key, [ident, …]), …]` — the PARTITION beside the join (lc-124).

    THE JOIN IS TRUE AND UNUSABLE AS A SCHEDULE, which is why this exists
    beside it rather than instead of it. Over this carrier the join closed
    49 path-valued items into ONE lane — not because the slots are coarse
    (ignoring directory entries still gave 3 components) but because six hot
    files chain every otherwise-disjoint pair. The partition answers the
    other question: which group each item belongs to if the carrier is cut
    on its hot files. That cut runs THROUGH real collisions, so it is a PLAN
    and never a permission — `wave_group_serializations` is what keeps it
    honest. Groups are ordered by size then key, so a desk reading the
    report twice reads the same order.
    """
    freq = wave_entry_frequency(rows)
    groups: dict = {}
    for ident, paths in rows:
        groups.setdefault(wave_group_key(paths, freq), []).append(ident)
    return sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0]))


def wave_group_serializations(rows, groups):
    """`[(key, (group_a, group_b), [ident, …], [ident, …]), …]` — every file
    crossing a group boundary, with BOTH groups and both sides named.

    THIS IS WHAT MAKES THE GROUPING SAFE TO READ, and dropping one of these
    lines would make the grouped mode WORSE than the one-lane answer it
    sits beside: two groups printed side by side read as parallel, and a
    file both of them write is exactly the one-writer breach the join exists
    to prevent — it does not stop being one because a frequency count put
    the two items in different groups. The collision notion is the JOIN'S
    OWN (`wave_witnesses`), containment included: a second spelling of
    "these two collide" would answer differently from the lane list printed
    directly above it, and the desk would have no way to tell which was
    lying.
    """
    owner = {ident: key for key, members in groups for ident in members}
    hits: dict = {}
    for i in range(len(rows)):
        ida, pa = rows[i]
        for j in range(i + 1, len(rows)):
            idb, pb = rows[j]
            ga, gb = owner[ida], owner[idb]
            if ga == gb:
                continue
            for key, _by_containment in wave_witnesses(pa, pb):
                first, second = sorted((ga, gb))
                sides = hits.setdefault((key, (first, second)), (set(), set()))
                sides[0 if ga == first else 1].add(ida)
                sides[0 if gb == first else 1].add(idb)
    return [(key, pair,
             sorted(side_a, key=_wave_ident_key),
             sorted(side_b, key=_wave_ident_key))
            for (key, pair), (side_a, side_b) in sorted(hits.items())]


def report_waves(schedulable, out, *, ready_n, live_n, excluded,
                 grouped=False) -> int:
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

    # DERIVED from the run, never listed again: a bucket added to
    # `WAVE_NON_PATH` and forgotten here would raise on its first member —
    # loud, but only for the one carrier that happens to carry it, and
    # silent-by-absence in the report's zeros for every other.
    buckets: dict = {key: [] for key in WAVE_NON_PATH}
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

    # THE GROUPED SECTION IS APPENDED, never substituted for the lane list:
    # the join is the truthful answer and the partition is a proposal over
    # it, so a reader must be able to see both at once. Appending is also
    # what makes the default output byte-identical to the verb before this
    # flag existed — nothing above this branch moved.
    if grouped:
        groups = wave_groups(rows)
        crossings = wave_group_serializations(rows, groups)
        out("")
        out(f"GROUPS: {len(groups)} over {len(rows)} path-valued item(s) — a "
            "PLAN, never a permission. Each item sits in the group of its "
            "write-set's MOST-FREQUENT entry, counted over these same "
            f"{len(rows)} item(s). Unlike lanes, groups are NOT disjoint by "
            "construction: the cut runs through real collisions, and every "
            "one of them is named below.")
        for n, (key, members) in enumerate(groups, start=1):
            out(f"group {n} ({key}): {len(members)} item(s) — "
                + ", ".join(sorted(members, key=_wave_ident_key)))
        if not crossings:
            out("SERIALIZE: 0 — none. No file crosses a group boundary over "
                "this population, so the groups above are parallel as "
                "printed.")
        else:
            out(f"SERIALIZE: {len(crossings)} cross-group shared file(s) — "
                "these group PAIRS do NOT run at once; dispatching them in "
                "parallel hands two writers one file.")
            for key, (ga, gb), side_a, side_b in crossings:
                out(f"      {key}: group ({ga}) {', '.join(side_a)} "
                    f"vs group ({gb}) {', '.join(side_b)}")

    out("")
    out("NOT CLUSTERED — for TWO reasons, kept apart because they route to "
        "different repairs. A write-set the join COULD NOT READ as this "
        "repo's paths is never put in a lane, because a join over a slot "
        "nobody could read would read exactly like one over a slot that was "
        "read. A write-set it read perfectly well that names NO FILE HERE — a "
        "venue, another repo's boundary — has nothing to cluster and needs no "
        "repair at all:")
    for key in WAVE_NON_PATH:
        hits = buckets[key]
        out(f"  {key}: {len(hits)}" + (" — none" if not hits else ""))
        for ident, why in hits:
            out(f"      {ident}: {why}")

    unreadable = sum(len(buckets[k]) for k in WAVE_UNREADABLE)
    elsewhere = sum(len(buckets[k]) for k in WAVE_NOT_A_FILE_HERE)
    unread = unreadable + elsewhere
    out("")
    out("NO SIZING, NO TIER, NO ORDER: this verb computes the join and stops. "
        "How many lanes one dispatch carries, which tier each takes and what "
        "runs first stay the desk's judgment — the mapping is derivable, the "
        "crossover is not.")
    if unread:
        out(f"item waves: COULD NOT VERIFY — {unread} of "
            f"{len(schedulable)} schedulable item(s) are outside the lanes: "
            f"{unreadable} with a write-set this join could not read, and "
            f"{elsewhere} whose write-set it read and which name no file in "
            "this repo. Either way the lanes above are a plan over "
            f"{len(rows)} item(s) and NOT the whole schedulable set.")
        return exits.COULD_NOT_VERIFY
    out(f"item waves: CLEAN — every one of the {len(rows)} schedulable "
        "item(s) carries a path-valued write-set, so the mapping above covers "
        "the whole population.")
    return exits.CLEAN
