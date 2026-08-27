"""`lifecycle migrate` — the old carrier into `ITEMS.md`, and a REPORT.

IT IS A DRY RUN (brief D-e). It WRITES the successor files and READS the old
carrier; it never edits, moves or deletes `BACKLOG.md` or `BACKLOG-DONE.md`.
Retiring the old carrier is a separate act after a human has read the report,
and the design's acceptance criterion — "the report reconciles entry counts;
zero entries routed to the ledger" — is a property of the REPORT, so nothing
has to be destroyed to check it.

EVERY RULE APPLIED HERE IS THE DESIGN'S (§4 row 1, §3.1), AND NOTHING ELSE IS.
An entry the rules do not cover is reported UNCLASSIFIED with its grade word
and its line number (D-f). It is never given a plausible mapping: a guessed
mapping is a design decision taken at the executing tier, and it is invisible
afterwards because it looks exactly like a rule.

THE THREE ANSWERS, HERE. The report's own reconciliation is an identity —
`entries read == items written + unclassified` — and it is CHECKED rather than
narrated. A migration that could not read a source file answers COULD NOT
VERIFY: an unread carrier contributes zero entries, and zero is a number
shaped exactly like a clean migration.

WHAT MIGRATES INTO THE LEDGER: NOTHING, by default (§4 row 1, §3.6). The
count is printed anyway, and it is printed as a number rather than as a
sentence, because "nothing migrated" and "nothing was counted" read the same.

WHAT A CLOSED ENTRY IS — the three routes out of the source, not two (lc-18,
lc-19, lc-21). A source carrier states a closure in three shapes and this
build reads all three, because a closure written back as live work is the one
migration defect that is SILENT: the entry lands in the successor looking
exactly like work nobody has started.

  * a CLOSURE GRADE WORD at the bullet start — the tool's own closed
    vocabulary (`items.GRADES_CLOSED`), which had no rule here at all, so
    every properly-graded closure fell through to UNCLASSIFIED;
  * a CLOSURE SECTION in the `--from` carrier itself — the shape the design
    modelled as a separate `--from-done` FILE, while real carriers keep a
    `## Done` section of the same file;
  * a closure word LATER in the title of an otherwise ungraded bullet — which
    is the AMBIGUOUS shape, and it REFUSES rather than choosing.

REFUSAL IS THE ANSWER WHERE THE SOURCE IS AMBIGUOUS, and it is the same
answer class D-f already gives an uncovered grade word: the entry is NOT
written, it is reported with its line and the reason, and the run exits
FINDING. The desk that owns the carrier decides, one entry at a time. The two
ambiguous shapes are a closure word mid-title (is it a closure, or prose
naming one?) and an OPEN grade word sitting under a closure heading (which of
the two does the author mean?). Guessing either would be a classification
rule invented here, and it would read afterwards exactly like a rule.

THE SOURCE IS PINNED BY ITS BLOB (cf-324). The report header records the git
blob sha of every source this run read, and a re-run whose report already
records a DIFFERENT sha answers COULD NOT VERIFY rather than quietly
producing a second answer over a third file. The recorded case: three
`BACKLOG.md` blobs in one afternoon, with a regenerated report whose record
pointers were stale before the commit landed.
"""

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from . import exits
from . import declaration as decl
from . import items as items_mod
from . import ledger as ledger_mod

#: THE CLASSIFICATION RULES, as data rather than as branches, so the report
#: can print the rule beside every entry it applied it to. Source: design §4
#: row 1, plus §3.1 for the two extra words whose MEANINGS map.
#:
#: `RECORD -> READY` is §3.1's own sentence: "RECORD's substance —
#: decision-complete, not scheduled — is READY-unscheduled … the rest are
#: READY and visible, not a separate word". The `ready-cap` and the head rule
#: pick the scheduled head at READ time; they are not a second grade and the
#: migration does not apply them.
RULES = {
    "READY": ("READY", "§4 row 1: READY→READY (scheduled by cap/head-rule at "
                       "read time, not by this migration)"),
    "RECORD": ("READY", "§4 row 1: RECORD→READY-unscheduled; §3.1: the rest "
                        "are READY and visible, not a separate word"),
    "PARKED": ("PARKED?", "§4 row 1: PARKED→PARKED with a typed blocker, or "
                          "NEW"),
    "HANDOFF": ("NEW", "§4 row 1: →NEW with a typed blocker or DROPPED"),
    "OPEN": ("NEW", "§4 row 1 and §3.1: OPEN→NEW"),
    "BUST": ("NEW", "§4 row 1: →NEW with a typed blocker or DROPPED"),
    "PARTLY": ("NEW", "§4 row 1: →NEW with a typed blocker or DROPPED"),
    "CANDIDATE": ("NEW", "§4 row 1: →NEW with a typed blocker or DROPPED"),
    "FINDING": ("NEW", "§4 row 1: →NEW with a typed blocker or DROPPED"),
    "NEW": ("NEW", "§4 row 1: →NEW with a typed blocker or DROPPED"),
    "POINTER": ("NEW", "§3.1: POINTER → an item whose body lives elsewhere, "
                       "referenced"),
}

#: THE CLOSURE WORDS, DERIVED from the vocabulary's own home rather than
#: restated here (lc-19). `items.GRADES_CLOSED` is where the closed grades are
#: declared, so a word added there gains a migration rule in the same act — a
#: hardcoded pair beside it would be a second body for one fact, and it would
#: stay green the day the vocabulary grew.
#:
#: THE FIX IS RULES, NEVER A LOOSER MATCHER. `classify` matched the grade word
#: and then asked `RULES.get(word)`; the table held eleven words and neither
#: `DONE` nor `DROPPED`, so every properly-graded closure in a source carrier
#: was UNCLASSIFIED by construction. `DROPPED` is the sharp one: it belongs to
#: this plugin's OWN default vocabulary and still had no rule. A word with no
#: rule must STILL report as unclassified rather than be guessed at, which is
#: why the repair is a table entry and not a widened pattern.
CLOSURE_RULES = {
    word: (word, f"§3.1: `{word}` is the closed vocabulary's own word — a "
                 "closure MOVES to the done home; it never enters the open "
                 "carrier, and it never inherits a grade the source did not "
                 "carry")
    for word in items_mod.GRADES_CLOSED
}
RULES.update(CLOSURE_RULES)

#: An entry with no grade word at all. §4 row 1 lists "ungraded" beside the
#: seven words that share its rule.
UNGRADED_RULE = ("NEW", "§4 row 1: ungraded → NEW with a typed blocker or "
                        "DROPPED")

#: An ungraded entry sitting under the carrier's own closure heading. The
#: SECTION is the author's statement that the entry is closed — it is why
#: those entries carry no grade word: the heading already said it (lc-18).
#: The body is archived VERBATIM, so no grade is written for it anywhere; this
#: rule records the ROUTE, not a grade the source never carried.
SECTION_CLOSURE_RULE = ("§4 row 1 + lc-18: ungraded, under the carrier's own "
                        "closure heading — the heading is the closure "
                        "statement, and the body is archived verbatim")

#: Sections §4 row 1 CUTS rather than migrates: "`## Grades` prose
#: declarations, `Closure-home:` line, declared extra words | CUT — the tool
#: owns the vocabulary". Matched on the heading's FIRST WORD, because the
#: carrier's real heading carries an explanatory tail after it.
#:
#: This is a rule of the design, not a judgment made here — and it is DATA so
#: the report can print what was cut and why. Without it the section's own
#: prose bullets, which DESCRIBE the grade words, migrate as work items: the
#: first run of this migration did exactly that and turned the two grade
#: definitions into `cf-1` and `cf-2`.
CUT_SECTIONS = ("Grades",)

#: Sections whose entries are the carrier's OWN CLOSURE BODIES (lc-18). The
#: design modelled closures as a separate FILE (`--from-done`) and both real
#: dotfiles carriers keep theirs as a `## Done` section of the same file, so
#: without this every closed body migrated back as live work — measured at
#: 7 root entries and 1 corpus entry.
#:
#: Matched on the heading's FIRST WORD for the same reason `CUT_SECTIONS` is:
#: the real heading carries an explanatory tail — "## Done (move here with
#: the commit pointer, prune at reviews)".
#:
#: THE DEFAULT IS UNCONDITIONAL, and that is the point rather than an
#: oversight: a `Closure-home:` naming a FILE does not license reading a
#: `## Done` section in the same carrier as open work. The declaration ADDS a
#: name; it never subtracts the default one.
CLOSURE_SECTIONS_DEFAULT = ("Done",)

#: The carrier's own `Closure-home:` declaration, at column zero. Anchored
#: there deliberately: both dotfiles carriers discuss the phrase inside
#: indented item bodies, and a search that matched those would read an item's
#: prose as a declaration.
_CLOSURE_HOME_LINE = re.compile(r"^Closure-home:[ \t]*(.+)$", re.MULTILINE)
#: A declared value that names a FILE rather than a section heading. One
#: token, one dotted suffix — `BACKLOG-DONE.md` is the real instance.
_FILE_LIKE = re.compile(r"^\S+\.[A-Za-z0-9]+$")

#: The write-set of a migrated entry. §4 row 1: "write-set absent → UNKNOWN",
#: and §3.2 makes UNKNOWN never match in the join — which is what stops every
#: migrated entry joining every other one.
UNKNOWN = "UNKNOWN"

#: A requirement line is ONE line and the old bodies are paragraphs. The cap
#: is the shape rule made explicit rather than a formatting taste: a slot
#: value that wrapped would parse as a shape break.
REQUIREMENT_CAP = 240

#: An ENTRY in the old carrier. Two forms, and the second is why the rule is
#: not just "starts with `- **`": the carrier holds two entries written as
#: plain `- DONE …` bullets. So an entry is a top-level bullet that is either
#: BOLD or starts with a grade-shaped word. A top-level bullet that is
#: neither is PROSE inside a prose section — the handoff's step list, the
#: build order's ranking — and is reported as non-entry content rather than
#: migrated into an item nobody wrote.
_BULLET = re.compile(r"^- (.*)$")
_HEADING = re.compile(r"^(#+)\s+(.*)$")
#: A grade-shaped word: uppercase, at least two characters, not followed by a
#: lowercase letter. The trailing guard is what stops `MITIGATE-goal` and
#: `OPEN-BOOKED` collapsing onto `MITIGATE` and `OPEN` — a prefix match in an
#: equality's costume, which would silently give an entry another word's rule.
_GRADE_WORD = re.compile(r"^([A-Z][A-Z0-9-]*[A-Z0-9])(?![a-z])")
#: A CLOSURE word standing alone somewhere OTHER than the bullet start
#: (lc-21). Both guards are `[A-Za-z0-9-]`, tighter than `_GRADE_WORD`'s
#: trailing `(?![a-z])`, because this pattern runs over a whole title rather
#: than over a word the carrier's own shape already isolated: `DROPPED-BY` and
#: `UNDONE` must not register, and a matcher loosened until the counts improve
#: scores identically to one that got the distinction right.
#:
#: DERIVED from `items.GRADES_CLOSED`, like `CLOSURE_RULES` — one vocabulary,
#: one home.
_CLOSURE_WORD = re.compile(
    r"(?<![A-Za-z0-9-])(" + "|".join(items_mod.GRADES_CLOSED)
    + r")(?![A-Za-z0-9-])")


@dataclass
class Entry:
    line: int
    end_line: int
    section: str
    raw_first: str
    text: str
    bold: bool
    grade_word: str | None = None
    grade: str | None = None
    rule: str = ""
    ident: str | None = None
    unclassified_why: str = ""
    #: This entry sits under the source carrier's own closure heading. Set by
    #: `read_carrier` from the section name, read by `classify`: the heading
    #: is a statement about every entry beneath it, and it is the only place
    #: the carrier's ungraded closures say they are closed.
    in_closure_section: bool = False
    #: ROUTED TO THE DONE HOME. A third disposition beside "written" and
    #: "unclassified", and it is a FIELD rather than a grade value because a
    #: closure's body is archived VERBATIM: writing a grade for it would
    #: assert something the source never carried.
    closure: bool = False
    #: The TYPED blocker the write-rules gave this entry, and which branch
    #: produced it. Held per entry so the report can print the per-TYPE
    #: counts §3.1 asks for — a total is the number that hides the untyped one.
    blocker: str = ""
    blocker_rule: str = ""


@dataclass
class Read:
    entries: list = field(default_factory=list)
    #: Top-level bullets that are neither bold nor grade-led — prose, not
    #: entries. Counted and located, never silently dropped.
    non_entry_bullets: list = field(default_factory=list)
    sections: dict = field(default_factory=dict)
    total_bullets: int = 0
    #: `(lineno, section)` for every bullet inside a section §4 row 1 CUTS.
    #: Counted apart from both the entries and the prose bullets, so "cut by
    #: a rule" never renders as "there was nothing there".
    cut_bullets: list = field(default_factory=list)
    #: The closure-section names this read applied, and WHY those. Carried so
    #: the report prints the basis rather than the outcome alone: "no entry
    #: sat under a closure heading" and "this run looked under the wrong
    #: heading name" produce the same zero.
    closure_sections: tuple = ()
    closure_sections_why: str = ""


def closure_sections_for(text: str) -> tuple:
    """`(first-words, why)` — the closure headings THIS carrier uses (lc-18).

    The declaration ADDS a name and never subtracts the default: a carrier
    that declares a closure FILE and also keeps a `## Done` section has both,
    and reading that section as open work is exactly the defect.
    """
    names = list(CLOSURE_SECTIONS_DEFAULT)
    default_why = ", ".join(f"`## {n}`" for n in names)
    m = _CLOSURE_HOME_LINE.search(text)
    if m is None:
        return tuple(names), (
            f"the source carrier declares no `Closure-home:`, so the default "
            f"in-carrier closure heading applies: {default_why}")
    declared = m.group(1).strip()
    if _FILE_LIKE.match(declared):
        return tuple(names), (
            f"the source carrier declares `Closure-home: {declared}` — a "
            f"FILE, which is what `--from-done` reads. The default heading "
            f"{default_why} still applies: a declared closure FILE does not "
            f"license reading a closure SECTION in the same carrier as open "
            f"work, and a declaration adds a name rather than removing one")
    word = declared.lstrip("#").strip()
    word = word.split()[0] if word.split() else ""
    if word and word not in names:
        names.append(word)
    return tuple(names), (
        f"the source carrier declares `Closure-home: {declared}`, which names "
        f"a SECTION rather than a file — matched on its first word, "
        f"`{word}`, beside the default {default_why}")


def read_carrier(text: str, closure_sections: tuple | None = None) -> Read:
    """Parse a source carrier.

    `closure_sections` defaults to this carrier's OWN — derived from its
    `Closure-home:` line, or the default heading where it declares none.
    """
    out = Read()
    if closure_sections is None:
        out.closure_sections, out.closure_sections_why = \
            closure_sections_for(text)
    else:
        out.closure_sections = tuple(closure_sections)
        out.closure_sections_why = "supplied by the caller"
    lines = text.split("\n")
    section = "(before any heading)"
    pending = None

    def close(end):
        if pending is None:
            return
        pending.end_line = end
        joined = " ".join(pending.text.split())
        pending.text = joined
        out.entries.append(pending)

    for i, raw in enumerate(lines):
        lineno = i + 1
        m = _HEADING.match(raw)
        if m and len(m.group(1)) <= 2:
            close(lineno - 1)
            pending = None
            section = m.group(2).strip()
            out.sections.setdefault(section, 0)
            continue
        b = _BULLET.match(raw)
        if b:
            close(lineno - 1)
            pending = None
            out.total_bullets += 1
            first_word = section.split()[0] if section.split() else ""
            if first_word in CUT_SECTIONS:
                out.cut_bullets.append((lineno, section))
                continue
            content = b.group(1)
            bold = content.startswith("**")
            stripped = content[2:] if bold else content
            gw = _GRADE_WORD.match(stripped.strip())
            if not bold and not gw:
                out.non_entry_bullets.append((lineno, section))
                continue
            pending = Entry(line=lineno, end_line=lineno, section=section,
                            raw_first=content, text=stripped, bold=bold,
                            in_closure_section=first_word
                            in out.closure_sections)
            out.sections[section] = out.sections.get(section, 0) + 1
            continue
        if pending is not None:
            pending.text += " " + raw.strip()
    close(len(lines))
    return out


def headline_of(entry: Entry) -> str:
    """The entry's own headline, ONE line, UNCAPPED.

    Taken from the bold segment where there is one — the carrier's own form
    puts the headline there — and from the first sentence otherwise. Never
    generated: a requirement line this tool composed would be a paraphrase
    with nobody's judgment behind it, and it would read exactly like one an
    author wrote.

    THE CAP LIVES IN `title_of`, NOT HERE, and the split is the point: a
    pattern run over a CAPPED headline is a search over a partial view of its
    own subject, and a closure word past column 240 would return exactly what
    a title with no closure word returns.
    """
    text = entry.text
    if entry.bold:
        end = text.find("**")
        headline = text[:end] if end != -1 else text
    else:
        headline = text
    headline = " ".join(headline.split()).strip(" .")
    if not headline:
        headline = "(the source entry's headline was empty)"
    return headline


def title_of(entry: Entry) -> str:
    """`headline_of`, capped to one requirement line's width."""
    headline = headline_of(entry)
    if len(headline) > REQUIREMENT_CAP:
        headline = headline[:REQUIREMENT_CAP - 1].rstrip() + "…"
    return headline


def closure_word_in_title(entry: Entry) -> str | None:
    """A closure word standing alone LATER in a bold entry's title (lc-21).

    ONLY over a bold entry's title, and that is a property of the shape rather
    than a choice: `read_carrier` admits an entry only when it is bold OR led
    by a grade-shaped word, and a grade-led entry never reaches this — so the
    text scanned here is always the author's own headline, never a paragraph
    of body prose in which "the check is DONE" would fire.
    """
    if not entry.bold:
        return None
    m = _CLOSURE_WORD.search(headline_of(entry))
    return m.group(1) if m else None


def _refuse(entry: Entry, why: str) -> None:
    """The AMBIGUOUS answer — D-f's own class, reached by a second road.

    Not written, reported with its line and its reason, and the run exits
    FINDING under `migration_unclassified`. Refusing is what keeps the
    decision with the desk that owns the carrier: a guess here would be a
    classification rule invented at this tier and invisible afterwards,
    because it would look exactly like a rule.
    """
    entry.grade = None
    entry.closure = False
    entry.rule = ""
    entry.unclassified_why = why


def classify(entry: Entry) -> None:
    stripped = entry.text.strip()
    m = _GRADE_WORD.match(stripped)
    entry.grade_word = m.group(1) if m else None
    if entry.grade_word is None:
        # THE SECTION DECIDES BEFORE THE TITLE DOES, and the order is the
        # rule. An ungraded entry under the carrier's own closure heading
        # carries no grade word precisely BECAUSE the heading already said it
        # — that is the dotfiles shape, measured at 7 root and 1 corpus
        # entry. Scanning its title first would refuse every one of them as
        # ambiguous, which is a guard firing on legitimate work.
        if entry.in_closure_section:
            entry.closure = True
            entry.grade = None
            entry.rule = SECTION_CLOSURE_RULE
            return
        word = closure_word_in_title(entry)
        if word is not None:
            _refuse(entry, (
                f"AMBIGUOUS: no grade word at the bullet start, and the "
                f"closure word {word!r} stands alone later in the title. A "
                f"closure written back as open work is silent, and a closure "
                f"read out of a title that merely NAMES one is a guess — the "
                f"desk that owns the carrier decides this entry"))
            return
        entry.grade, entry.rule = UNGRADED_RULE
        return
    rule = RULES.get(entry.grade_word)
    if rule is None:
        entry.grade = None
        entry.rule = ""
        entry.unclassified_why = (
            f"no rule in §4 row 1 or §3.1 covers the grade word "
            f"{entry.grade_word!r}")
        return
    grade, why = rule
    if grade in items_mod.GRADES_CLOSED:
        # A CLOSURE WHEREVER IT SITS. The word is the tool's own, and it says
        # the same thing under a live heading as under a closure heading.
        entry.closure = True
        entry.grade = None
        entry.rule = why
        return
    if entry.in_closure_section:
        _refuse(entry, (
            f"AMBIGUOUS: the OPEN grade word {entry.grade_word!r} under the "
            f"carrier's own closure heading {entry.section[:40]!r}. The "
            f"word says open and the section says closed; nothing in §4 row 1 "
            f"or §3.1 ranks one over the other, and picking either would "
            f"write a disposition the author did not"))
        return
    if grade == "PARKED?":
        # §4 row 1 offers PARKED two dispositions and the choice turns on
        # whether a TYPED blocker exists. The old carrier has no blocker
        # slot, and no rule in the design derives one from a body — so the
        # PARKED branch is unreachable over this carrier and every entry
        # takes the second. Extracting a blocker from prose would be a
        # classification rule invented here, which is the one thing D-f
        # forbids.
        entry.grade = "NEW"
        entry.rule = why + " — NO typed blocker is derivable (the old " \
                           "carrier has no blocker slot and the design " \
                           "states no rule for deriving one), so the second " \
                           "branch is taken"
        return
    entry.grade, entry.rule = grade, why


#: §3.1's MIGRATION WRITE-RULES, blocking and fixed. The blocker a migrated
#: entry carries is TYPED and the typing is the rule — an untyped blocker
#: would satisfy "every migrated item is blocked" while sitting in nobody's
#: court, which is the entry that ages out silently.
#:
#:   old READY        -> NEW, blocked-by: decision "regrade: …"
#:   slot-incomplete  -> NEW, blocked-by: decision <what the desk must supply>
#:   PARKED with its named missing evidence -> KEEPS blocked-by: evidence
#:
#: The third is the one that is easy to lose: a parked entry whose evidence is
#: named is ALREADY in the machine's court, and converting it to a decision
#: would move a waiting item into the operator's queue for no reason.
REGRADE_BLOCKER = ('decision regrade: was READY under the old carrier'
                   ' — READY is judged, never inherited')

#: An entry's own body names its missing evidence when it says so in the old
#: carrier's own vocabulary. Matched on the carrier's phrase rather than
#: guessed from prose: a classification rule invented at this tier is exactly
#: what D-f forbids, and this one is the carrier's own words.
#: THE TWO COURTS ARE NOT ONE. "Missing evidence" and a "Trigger:" put an
#: item in the MACHINE's court — something will arrive and re-evaluate it.
#: "Missing decision" puts it in the OPERATOR's, where nothing mechanical ever
#: clears it. Conflating them would convert every parked decision into an
#: evidence predicate nothing evaluates, which is the item that waits forever
#: while the board shows ordinary waiting.
_NAMED_EVIDENCE = re.compile(
    r"\b(missing evidence|named missing (?:evidence|piece)|trigger:)",
    re.IGNORECASE)
_NAMED_DECISION = re.compile(r"\bmissing decision\b", re.IGNORECASE)


def migration_blocker(entry: Entry, slots_incomplete: bool):
    """`(blocked-by, why)` for one migrated entry — TYPED, always (§3.1).

    THE TYPE IS THE RULE. "Every migrated entry carries a blocker" is
    satisfied by prose, and prose sits in nobody's court — so each branch here
    produces one of the three closed types and the report prints which branch
    ran. Under the new closed goal vocabulary nearly every migrated open item
    is slot-incomplete anyway, so the counts will LOOK like "all"; that is
    precisely why the criterion is stated per TYPE and never as a total.
    """
    if entry.grade_word == "PARKED":
        # THE NAMED MISSING PIECE DECIDES THE COURT, and the entry's own words
        # are what name it — never a reading of the prose invented here.
        if _NAMED_DECISION.search(entry.text):
            return ("decision " + PARKED_DECISION_QUESTION,
                    "PARKED naming a missing DECISION is in the OPERATOR's "
                    "court, so it keeps a `decision` blocker: nothing "
                    "mechanical ever clears it, and an evidence predicate "
                    "here would be one nothing evaluates")
        if _NAMED_EVIDENCE.search(entry.text):
            return ("evidence " + PARKED_EVIDENCE_PREDICATE,
                    "PARKED carrying its named missing evidence KEEPS an "
                    "`evidence` blocker — it is already in the MACHINE's "
                    "court and converting it to a decision would move a "
                    "waiting item into the operator's queue for no reason")
    if entry.grade_word in ("READY", "RECORD"):
        return (REGRADE_BLOCKER,
                "old READY never inherits READY (§3.1): the grade is a "
                "judgment about a carrier that no longer exists, so it "
                "returns to the desk as a decision")
    if slots_incomplete:
        return ("decision " + INCOMPLETE_DECISION,
                "slot-incomplete -> NEW with a `decision` blocker naming what "
                "the desk must supply; never NONE, which is the entry that "
                "ages in nobody's court")
    return ("decision " + INCOMPLETE_DECISION,
            "no rule left this entry complete, so it carries the same "
            "decision blocker rather than NONE")


#: The evidence predicate a kept-PARKED entry carries. It names the SOURCE
#: line, so the predicate points at the body that states the missing evidence
#: rather than at a sentence this tool composed.
PARKED_EVIDENCE_PREDICATE = "false  # the named missing evidence in the source body"

#: The question a PARKED-on-a-decision entry carries across. It names the
#: SOURCE body rather than restating it: the entry already says what decision
#: is missing, and a second wording of it here would be a paraphrase that
#: drifts from the body it summarizes.
PARKED_DECISION_QUESTION = ("the missing decision named in the source body — "
                            "answer it, then re-grade")

#: What the desk must supply, for a slot-incomplete entry. One sentence, and
#: it names the SLOTS rather than describing them: a decision question the
#: desk cannot act on is a blocker in a decision's costume.
INCOMPLETE_DECISION = ("regrade: fill goal, write-set, done-criterion and "
                       "evidence, or drop")


def build_items(entries, prefix: str, source_name: str) -> str:
    """The successor carrier. Ids are allocated in SOURCE ORDER, from 1."""
    blocks = []
    n = 0
    for e in entries:
        if e.grade is None:
            continue
        n += 1
        e.ident = f"{prefix}-{n}"
        # EVERY MIGRATED ENTRY IS OPEN, and the write-rules are about OPEN
        # items only: the done home holds closed bodies, where a blocker is a
        # shape finding rather than a migration output. This build's migration
        # writes nothing into the done home but the verbatim archive, so the
        # rule holds by construction here and is CHECKED by the done home's
        # own shape check rather than assumed.
        blocked, why = migration_blocker(e, slots_incomplete=True)
        e.blocker = blocked
        e.blocker_rule = why
        blocks.append(items_mod.render_block(e.ident, {
            # NEVER READY (§3.1, blocking). READY is a judgment about a
            # carrier that no longer exists; inheriting it would re-create
            # the 95-entry queue nobody believed, in a new file.
            "grade": "NEW",
            "requirement": f"{title_of(e)} — record: {source_name}:{e.line}",
            # THE GAP, WRITTEN AS A GAP. §4 row 1 names UNKNOWN for the
            # write-set and says nothing about `goal`, `done-criterion` or
            # `evidence` — and a slot cannot be empty. UNKNOWN is the
            # design's own DECLARED transitional marker: the join never
            # matches on it, the retire lane never reads it as "advances no
            # goal", `item check` counts it, and `item ready` REFUSES it.
            "goal": UNKNOWN,
            "write-set": UNKNOWN,
            "done-criterion": UNKNOWN,
            # The source body IS the evidence a migrated entry actually has.
            # A line range, not a copy: the body stays where it is and git
            # keeps it.
            "evidence": f"{source_name}:{e.line}-{e.end_line}",
            "blocked-by": blocked,
        }))
    return blocks, n


#: What separates the two archive regions in the done home. A COMMENT rather
#: than a heading: the archive is held verbatim and not shape-checked, and a
#: second `## …` line inside it would read as a block heading to anything that
#: later learns to parse the region.
CLOSURE_REGION_NOTE = (
    "<!-- CLOSURES READ FROM THE `--from` CARRIER ITSELF (lc-18/lc-19). The\n"
    "     design modelled closures as a separate `--from-done` FILE; a real\n"
    "     carrier states them in its own `## Done` section or with a closure\n"
    "     grade word. These bodies are VERBATIM from the source, at the line\n"
    "     ranges named beside each one, and they are archived rather than\n"
    "     written as items: a closure that migrates back as open work is the\n"
    "     one migration defect that is silent. -->")


def closure_bodies(entries, src_text: str, src_name: str) -> str:
    """The VERBATIM source bodies of every closure found in the `--from`
    carrier, as one archive region.

    VERBATIM AND LINE-RANGED, never re-rendered. A closure's body is the
    author's own record of what closed and why; re-rendering it into slots
    would be a paraphrase of a body nobody is going to read twice, and the
    line range is what lets a reader go back to the source that is still
    there (this is a DRY RUN and the old carrier is not touched).
    """
    if not entries:
        return ""
    lines = src_text.split("\n")
    out = ["", CLOSURE_REGION_NOTE, ""]
    for e in entries:
        out.append(f"<!-- {src_name}:{e.line}-{e.end_line} — {e.rule} -->")
        out.extend(lines[e.line - 1:e.end_line])
        out.append("")
    return "\n".join(out)


def blob_sha(data: bytes) -> str:
    """The GIT BLOB sha1 of `data` — the same name git gives the same bytes.

    Git's own definition, not a hash of our own invention (cf-324): a sha
    printed in a report is only useful if the operator can reproduce it, and
    `git hash-object <file>` is what they will run. The header and the NUL
    are part of that definition; a bare `sha1(data)` would be a hash of
    another kind compared against this one.
    """
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


#: The blob lines this build writes into a report header, and reads back out
#: of one on a re-run. At column zero and machine-readable on purpose: a
#: pointer a later run must RESOLVE cannot live inside a sentence.
_RECORDED_SOURCE_BLOB = re.compile(r"^source-blob:\s*([0-9a-f]{40})\b",
                                   re.MULTILINE)
_RECORDED_DONE_BLOB = re.compile(r"^done-blob:\s*([0-9a-f]{40}|NONE)\b",
                                 re.MULTILINE)


def source_moved(prior_report: str, src_blob: str, done_blob: str):
    """`(what, recorded, now)` for the first source whose blob has MOVED, or
    None — cf-324.

    A report with NO recorded blob is not a mismatch: it predates this build,
    and treating an absent record as a moved source would refuse every repo
    whose report was written by the last version. That is a real limit and it
    is stated in the run's own output rather than left to be discovered.
    """
    for label, pat, now in (("the source carrier", _RECORDED_SOURCE_BLOB,
                             src_blob),
                            ("the source closure home", _RECORDED_DONE_BLOB,
                             done_blob)):
        m = pat.search(prior_report)
        if m is not None and m.group(1) != now:
            return label, m.group(1), now
    return None


# --- the SCHEMA path (§3.8c, law 25) ------------------------------------------
#
# TWO MODES, TWO SPELLINGS, and the separation is the rule rather than a
# preference: `--from <path>` is the CARRIER source and `--schema-from <n>` is
# the SCHEMA path. A flag that meant a path in one invocation and a version in
# another is the shape where a caller's habit silently answers a different
# question.

def _growth_from_bound(value: str):
    """`(growth-value, why)` or `(None, why-not)` for one old `bound` string.

    THE THREE MODES ARE A CLOSED VOCABULARY and a COUNT is not one of them —
    R22 withdrew caps outright, so a `bound` that names a number has no
    mechanical successor and the repo must choose one. Guessing here would
    write a growth mode nobody decided, and it would read afterwards exactly
    like a decision.
    """
    v = str(value or "").strip()
    low = v.lower()
    for mode in decl.GROWTH_MODES:
        if low.startswith(mode):
            return v, f"already in the growth vocabulary ({mode})"
    if low.startswith("unbounded"):
        rest = v[len("unbounded"):].lstrip(" ,:—-")
        rest = rest[len("declared why:"):].strip() if \
            rest.lower().startswith("declared why:") else rest
        if len(rest) < 8:
            return None, ("`unbounded` with no declared reason — the word "
                          "carries the obligation and the reason is the repo's")
        return f"unbounded-with-reason — {rest}", \
            "`unbounded, declared why: …` -> `unbounded-with-reason — …`"
    if low.startswith("compact"):
        return f"compacted — {v}", "`compact…` -> `compacted`"
    return None, (f"{v[:60]!r} names a COUNT or a SIZE, and R22 withdrew caps: "
                  f"a size is not a growth control. The repo chooses one of "
                  f"{', '.join(decl.GROWTH_MODES)}")


def _plan_schema(repo, doc, from_n: int, to_n: int):
    """`(changes, unclassified)` — what a schema bump would do, per key.

    NOTHING IS GUESSED. A transformation the design states is a CHANGE; one
    that needs a decision the design leaves to the repo is UNCLASSIFIED, and
    an UNCLASSIFIED blocks the apply FOR THIS REPO ONLY (§3.11's own sentence
    about the drift detector's dry run). Reported with the key and the reason,
    never given a plausible value — a guessed value is a design decision taken
    by a migration and invisible afterwards, because it looks exactly like a
    declaration.
    """
    changes = []
    unclassified = []

    if doc.get("schema") != to_n:
        changes.append(("schema", f"{doc.get('schema')} -> {to_n}",
                        "one schema version per repo (§3.8c)"))

    for key, why in decl.RETIRED_KEYS.items():
        if key in doc and key != "bound":
            changes.append((key, "REMOVED", why))

    if "leak-scan" not in doc:
        unclassified.append(
            ("leak-scan",
             "§3.3 enables the source-scope foreign-path class PER REPO by "
             "declaration, and which way it goes is the repo's call — the "
             "corpus-only class is right for a repo whose own prose names "
             "this machine's home and blind in one whose payload is `.md`. "
             "There is no default: refuse-unless-declared is this design's "
             "answer everywhere a public tree is involved."))

    kinds = doc.get("kinds")
    if isinstance(kinds, dict):
        for name, body in kinds.items():
            if not isinstance(body, dict):
                continue
            if "bound" in body:
                new, why = _growth_from_bound(body["bound"])
                if new is None:
                    unclassified.append(
                        (f"kinds.{name}.bound", f"{why}."))
                else:
                    changes.append((f"kinds.{name}.bound -> growth", new[:70],
                                    why))
            for stage in ("reader", "writer"):
                value = body.get(stage)
                values = value if isinstance(value, list) else \
                    ([value] if isinstance(value, str) else [])
                for typ, target in decl.parse_refs(values):
                    if typ is None:
                        unclassified.append(
                            (f"kinds.{name}.{stage}",
                             f"{target[:60]!r} is PROSE, and §3.8c's types are "
                             f"closed. Which type it is — a lane, a verb, a "
                             f"hook, a producer, the session, the operator — "
                             f"is a reading of the repo's own intent and no "
                             f"rule in the design derives it from the "
                             f"sentence."))
    return changes, unclassified


def run_schema(args, out, ctx) -> int:
    """`migrate --schema-from <n>` — DRY RUN unless `--apply` (law 25)."""
    from_n = args.schema_from
    to_n = decl.SCHEMA_FLOOR
    doc = ctx.declaration
    repo = ctx.repo

    out(f"migrate --schema-from {from_n} -> {to_n}   repo: {repo}")
    out("DRY RUN" if not args.apply else "APPLY")
    out("")

    if from_n > to_n:
        out(f"FINDING [schema_above_floor] this repo is being migrated FROM "
            f"{from_n}, which is above this build's {to_n}. A build cannot "
            "migrate a file it cannot read — that is the floor's whole point.")
        return exits.FINDING

    declared = doc.get("schema")
    if declared != from_n:
        out(f"COULD NOT VERIFY: `--schema-from {from_n}` was stated and the "
            f"declaration is stamped {declared!r}. Refusing rather than "
            "reading the file's own number: the flag is the caller's claim "
            "about where this repo is, and a mismatch means one of the two is "
            "wrong — which is exactly what must not be silently resolved.")
        return exits.COULD_NOT_VERIFY

    changes, unclassified = _plan_schema(repo, doc, from_n, to_n)

    carrier_changes = []
    for kind, home in decl.carrier_homes(doc).items():
        n, why = decl.carrier_schema(repo / home)
        if n is None:
            out(f"COULD NOT VERIFY: the `{kind}` carrier could not be read for "
                f"its schema line: {why}.")
            return exits.COULD_NOT_VERIFY
        if n != to_n:
            carrier_changes.append((home, n, to_n))

    out(f"declaration changes: {len(changes)}")
    for key, what, why in changes:
        out(f"    {key}: {what}")
        out(f"        rule: {why}")
    out(f"carrier `schema:` lines to bump: {len(carrier_changes)}")
    for home, n, m in carrier_changes:
        out(f"    {home}: {n} -> {m}")
    out(f"UNCLASSIFIED (blocking the apply FOR THIS REPO): {len(unclassified)}")
    for key, why in unclassified:
        out(f"    {key}")
        out(f"        {why}")
    out("")

    if unclassified:
        out("FINDING [migration_unclassified] the apply is BLOCKED for this "
            "repo and for this repo only (§3.11): each key above needs a "
            "decision the design leaves to the repo, and a migration that "
            "guessed one would write a declaration nobody made — invisible "
            "afterwards, because it would look exactly like a declaration. "
            "Supply them, then re-run.")
        return exits.FINDING

    if not args.apply:
        out("migrate --schema-from: DRY RUN complete, nothing written. Law "
            "25: every schema change ships its migration, dry-run first, over "
            "every declared repo, before it is applied anywhere. Re-run with "
            "`--apply` to write.")
        return exits.CLEAN

    if not changes and not carrier_changes:
        out("migrate --schema-from: nothing to do — this repo is already at "
            f"schema {to_n} in the declaration and in every carrier.")
        return exits.CLEAN

    new_doc = json.loads(json.dumps(doc))
    new_doc["schema"] = to_n
    for key in decl.RETIRED_KEYS:
        if key == "bound":
            continue
        new_doc.pop(key, None)
    for name, body in (new_doc.get("kinds") or {}).items():
        if isinstance(body, dict) and "bound" in body:
            growth, _why = _growth_from_bound(body.pop("bound"))
            body["growth"] = growth
    path = repo / decl.DECLARATION_REL
    try:
        path.write_text(json.dumps(new_doc, indent=2, ensure_ascii=False)
                        + "\n", encoding="utf-8")
    except OSError as exc:
        out(f"COULD NOT VERIFY: the declaration could not be written "
            f"({exc!r}). Nothing else was touched.")
        return exits.COULD_NOT_VERIFY
    out(f"written: {decl.DECLARATION_REL}")

    for home, n, m in carrier_changes:
        p = repo / home
        try:
            text = p.read_text(encoding="utf-8")
            lines = text.split("\n")
            for i, raw in enumerate(lines):
                if raw.strip().startswith("schema:"):
                    lines[i] = f"schema: {m}"
                    break
            p.write_text("\n".join(lines), encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            out(f"COULD NOT VERIFY: {home} could not be rewritten ({exc!r}). "
                "The declaration is already at the new schema, so this repo "
                "is now MID-MIGRATION and `schema_mismatch` will say so.")
            return exits.COULD_NOT_VERIFY
        out(f"written: {home} (schema {n} -> {m})")

    out(f"migrate --schema-from: APPLIED — {len(changes)} declaration "
        f"change(s), {len(carrier_changes)} carrier line(s).")
    return exits.CLEAN


def run(args, out, ctx) -> int:
    if args.schema_from is not None:
        return run_schema(args, out, ctx)
    src_name = args.from_carrier or "BACKLOG.md"
    done_name = args.from_done or "BACKLOG-DONE.md"
    src = ctx.repo / src_name

    #: A repo may genuinely have NO legacy closure home — the plugin repo is
    #: the case: it has never closed anything through one. That absence is
    #: STATED by the caller (`--from-done NONE`) and never inferred from a
    #: missing file, because the two are different facts: an unread closure
    #: home contributes zero archive bodies, and zero is a number shaped
    #: exactly like a repo that had none.
    no_done = str(done_name).strip().upper() == "NONE"
    src_done = None if no_done else ctx.repo / done_name

    if not src.is_file():
        out(f"COULD NOT VERIFY: no source carrier at {src}. An absent source "
            "contributes zero entries, and zero entries is a number shaped "
            "exactly like a clean migration.")
        return exits.COULD_NOT_VERIFY
    if src_done is not None and not src_done.is_file():
        out(f"COULD NOT VERIFY: no source closure home at {src_done}. If this "
            "repo genuinely has none, say so — `--from-done NONE` — rather "
            "than leaving it absent: a stated absence and an unread file are "
            "different answers, and only one of them means the archive count "
            "of zero is true.")
        return exits.COULD_NOT_VERIFY
    try:
        # THE BYTES, not the decoded text, for the blob (cf-324).
        # `read_text` translates newlines, so a sha over its output would be a
        # hash of a TRANSFORMED view compared against git's hash of the file.
        src_bytes = src.read_bytes()
        done_bytes = b"" if src_done is None else src_done.read_bytes()
        src_text = src.read_text(encoding="utf-8")
        done_text = "" if src_done is None else src_done.read_text(
            encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        out(f"COULD NOT VERIFY: a source carrier could not be read ({exc!r}).")
        return exits.COULD_NOT_VERIFY

    src_blob = blob_sha(src_bytes)
    done_blob = "NONE" if src_done is None else blob_sha(done_bytes)

    report_only = getattr(args, "report_only", False)
    if not args.force and not report_only:
        for p in (ctx.items_path, ctx.done_path):
            if p.exists():
                out(f"FINDING [migrate_would_overwrite] {p.name} already "
                    "exists. Refusing to overwrite a carrier: this is a DRY "
                    "RUN that PRODUCES the successor files, and a second run "
                    "over a carrier already in use would replace real work "
                    "with a re-derivation of the old one. Pass `--force` if "
                    "that is what is wanted.")
                return exits.FINDING

    # --- cf-324: THE SOURCE IS PINNED BY ITS BLOB, and the pin is checked
    # BEFORE anything is written. The report is where the pin lives, because
    # the report is the artifact a later run is regenerating; a run that
    # produced a second answer over a third file would look exactly like the
    # first one.
    report_rel = args.report or (f"docs/audits/migration-report-"
                                 f"{date.today().isoformat()}.md")
    report_path = ctx.repo / report_rel
    prior_report = ""
    if report_path.is_file():
        try:
            prior_report = report_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            prior_report = ""
    moved = source_moved(prior_report, src_blob, done_blob) if prior_report \
        else None
    if moved is not None:
        what, recorded, now = moved
        out(f"COULD NOT VERIFY: {what} has MOVED since {report_rel} was "
            f"written. That report records blob {recorded}; the file on disk "
            f"is blob {now}. Refusing to produce a second answer over a "
            "different source: the answer would be indistinguishable from "
            "the first one, and every record pointer in the existing report "
            "already points into the OTHER blob. Re-run against a NEW "
            "`--report` path to record a fresh answer, or restore the source "
            "the report was written from.")
        return exits.COULD_NOT_VERIFY

    read = read_carrier(src_text)
    for e in read.entries:
        classify(e)
    done_read = read_carrier(done_text)

    written, n_items = build_items(read.entries, ctx.prefix, src_name)
    unclassified = [e for e in read.entries
                    if e.grade is None and not e.closure]
    closures = [e for e in read.entries if e.closure]

    # --- the successor files
    closure_text = closure_bodies(closures, src_text, src_name)
    # ONE NOTION OF AN ARCHIVE BODY ON BOTH SIDES. `archive_entries` counts
    # what the conservation identity counts, so the in-carrier closures are
    # counted by the same function over the same text that is written — never
    # by the entry count, which is a different notion and would make the
    # identity hold by a coincidence rather than by construction.
    archive_count = (items_mod.archive_entries(done_text)
                     + items_mod.archive_entries(closure_text))
    baseline = n_items + archive_count
    head = (f"schema: {items_mod.SCHEMA_FLOOR}\n"
            f"baseline: {baseline}\nadded: 0\ncompacted: 0\n")
    # THE ARCHIVE SECTION IS WRITTEN EVEN WHEN IT IS EMPTY, and it says which
    # of the two it is. A done home with no archive heading and one whose
    # archive is empty look the same from the outside, and only one of them
    # means "this repo had no legacy closure home".
    #
    # THE NOTE PRECEDES THE SCHEMA LINE, and the check caught it the other way
    # round on this file's first run: a comment block may come BEFORE the
    # version and never after, because everything from the version down is
    # tool-written and a comment there is a hand edit in the one region whose
    # shape is the mechanism.
    archive_note = (
        "" if src_done is not None else
        "# This repo had NO legacy closure home. The absence was STATED at\n"
        "# migration time (`--from-done NONE`), never inferred from a missing\n"
        "# file: the archive below is empty because there was nothing to\n"
        "# archive, which is a different fact from nothing having been read.\n"
        "\n")
    # `--report-only` RE-RENDERS THE REPORT AND TOUCHES NOTHING ELSE. R3 has
    # the report's findings enter the carrier as ITEMS via intake and the
    # report then POINT AT the item ids — which is circular unless the report
    # can be re-rendered after the intake. Without this flag the pointer would
    # be a hand edit that the next `migrate` erases, and a pointer with an
    # expiry date is the kind of arrangement this repo keeps finding.
    if not report_only:
        ctx.items_path.write_text(head + "\n" + "\n".join(written),
                                  encoding="utf-8")
        ctx.done_path.write_text(
            archive_note + f"schema: {items_mod.SCHEMA_FLOOR}\n\n"
            + f"{items_mod.ARCHIVE_HEADING}\n\n" + done_text + closure_text,
            encoding="utf-8")

    # --- the ledger: NOTHING migrates into it (§3.6, §4 row 1)
    if not ctx.ledger_path.exists():
        ctx.ledger_path.write_text(ledger_mod.head_text(), encoding="utf-8")
    lparsed, lwhy = ledger_mod.read(ctx.ledger_path)
    ledger_count = None if lparsed is None else len(lparsed.lines)

    # --- the report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_report(ctx, read, done_read, src_name, done_name, n_items,
                      unclassified, archive_count, baseline, ledger_count,
                      lwhy, report_rel, closures, src_blob, done_blob),
        encoding="utf-8")

    # --- the run's own answer
    out(f"migrate: DRY RUN — {src_name} and {done_name} are READ and are not "
        "edited, moved or deleted (D-e).")
    out(f"    source blob:              {src_blob}  ({src_name})")
    out(f"    source done-home blob:    {done_blob}  ({done_name})")
    out(f"    source entries read:      {len(read.entries)}")
    out(f"    items written:            {n_items} → {ctx.items_path.name}")
    out(f"    CLOSURES routed to the done home: {len(closures)} → "
        f"{ctx.done_path.name}, verbatim")
    out(f"    closure heading(s) read:  "
        f"{', '.join('## ' + s for s in read.closure_sections)} — "
        f"{read.closure_sections_why}")
    out(f"    UNCLASSIFIED (reported):  {len(unclassified)}")
    out(f"    reconciliation:           {len(read.entries)} read == "
        f"{n_items} written + {len(closures)} closed + "
        f"{len(unclassified)} unclassified")
    bt = blocker_types(read.entries)
    out(f"    grades written:           NEW {n_items}, READY 0 — §3.1: a "
        "migrated entry NEVER inherits READY")
    out("    blockers, PER TYPE (never a total — a total is the number that "
        "hides the untyped one):")
    for typ in ("decision", "evidence", "item-id", "NONE", "untyped"):
        out(f"        {typ:<10} {bt.get(typ, 0)}")
    out(f"    archive bodies:           {archive_count} → "
        f"{ctx.done_path.name}, verbatim")
    out(f"    ledger lines:             {ledger_count} (nothing migrates into "
        "the ledger — §3.6, §4 row 1)")
    out(f"    report:                   {report_rel}")

    code = exits.CLEAN
    if len(read.entries) != n_items + len(closures) + len(unclassified):
        # NOT A REGISTERED ROW, deliberately. Every entry is written, closed
        # or unclassified BY CONSTRUCTION — the three sets partition the read
        # entries — so no INPUT falsifies this, and a predicate no input can
        # falsify is unprovable rather than unproven. Registering it would
        # put a row in the roster that can never go red, which is the
        # clean-forever check the roster exists to prevent. It is kept as a
        # COULD NOT VERIFY on the run's own arithmetic: a run whose counts
        # disagree with themselves cannot promise a complete list, and that
        # is what code 3 means.
        out("COULD NOT VERIFY: this run's own arithmetic disagrees — "
            f"{len(read.entries)} entries read, {n_items} written, "
            f"{len(closures)} closed, {len(unclassified)} unclassified. "
            "Nothing below is a complete list.")
        code = exits.COULD_NOT_VERIFY
    if ledger_count is None:
        out(f"COULD NOT VERIFY: the ledger could not be read, so 'zero "
            f"entries routed to the ledger' was not checked. {lwhy}")
        code = exits.worst([code, exits.COULD_NOT_VERIFY])
    elif ledger_count != 0:
        out(f"FINDING [migration_ledger_nonzero] {ledger_count} ledger "
            "line(s) after a migration that must route none. §3.6: the "
            "ledger carries no bodies and nothing migrates into it.")
        code = exits.worst([code, exits.FINDING])
    if unclassified:
        out(f"FINDING [migration_unclassified] {len(unclassified)} entry/ies "
            "match no rule in §4 row 1 or §3.1, or are AMBIGUOUS about "
            "whether they are closed, and were NOT written. Each is listed "
            "in the report with its line number and its reason. This is a "
            "finding for the desk, not a defect for the migration to "
            "resolve: a guessed mapping is a design decision taken here and "
            "invisible afterwards.")
        # QUOTED HERE AND NOT IN THE REPORT. The desk running this needs to
        # see WHICH entry it is being asked about, and the run's own output
        # is the place a quote costs nothing: the report is a generated file
        # in a tree that may be public, and it states that it describes
        # entries rather than quoting them. One headline each, capped.
        for e in unclassified:
            out(f"    {src_name}:{e.line}  {e.unclassified_why}")
            out(f"        entry: {title_of(e)}")
        code = exits.worst([code, exits.FINDING])
    out(f"migrate: {exits.word(code)}")
    return code


def blocker_types(entries) -> dict:
    """`{type: n}` over what the write-rules actually wrote.

    PER TYPE, never a total. "All migrated items are blocked" is satisfied by
    an untyped blocker and by a blocker written into a closed body; the per-
    type counts are the only form in which the criterion can be checked, and
    `untyped` appearing at all is the finding.
    """
    out = {"decision": 0, "evidence": 0, "item-id": 0, "NONE": 0, "untyped": 0}
    for e in entries:
        if e.grade is None:
            continue
        v = (e.blocker or "").strip()
        if not v or v == items_mod.BLOCKER_NONE:
            out["NONE"] += 1
        elif v.startswith("decision "):
            out["decision"] += 1
        elif v.startswith("evidence "):
            out["evidence"] += 1
        elif re.fullmatch(r"[a-z][a-z0-9-]*-\d+", v):
            out["item-id"] += 1
        else:
            out["untyped"] += 1
    return out


def routed_items(ctx, report_rel: str) -> list:
    """Items whose `evidence` slot CITES this report — read from the carrier.

    THE POINTER IS DERIVED, never written down. A hand-maintained list of
    "findings routed to items" is a second body for a fact the carrier already
    holds, and it would go stale the first time an item was closed or
    renumbered. Anchored on the report's BASENAME inside the evidence slot,
    which is where an intake naming this report puts it.
    """
    basename = Path(report_rel).name
    try:
        parsed = items_mod.parse(ctx.items_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return []
    return [it for it in parsed.items
            if basename in (it.slots.get("evidence") or "")]


def render_report(ctx, read, done_read, src_name, done_name, n_items,
                  unclassified, archive_count, baseline, ledger_count,
                  lwhy, report_rel="", closures=(), src_blob="",
                  done_blob="") -> str:
    """The classification report.

    IT DESCRIBES ENTRIES; IT DOES NOT QUOTE THEM. Every entry appears as its
    line number, its grade word and the rule applied — never as its prose.
    That is the publication bar's shape applied to a generated artifact in a
    public tree: a report that quoted bodies would republish them under a
    second name, where nobody would look for them again.
    """
    L = []
    a = L.append
    a(f"# Migration report — {src_name} → {ctx.items_path.name} "
      f"({date.today().isoformat()})")
    a("")
    a("Produced by `lifecycle migrate`. **A DRY RUN**: the source carriers "
      f"`{src_name}` and `{done_name}` were READ. They are not edited, not "
      "moved and not deleted, and retiring them is a separate act after a "
      "human has read this file.")
    a("")
    a("This report DESCRIBES entries — line number, grade word, rule "
      "applied. It does not quote their prose.")
    a("")
    a("## The sources this run read, PINNED BY BLOB")
    a("")
    a("The git blob sha of every source, so a later run can tell whether it "
      "is looking at the same file. **A re-run whose report already records "
      "a DIFFERENT sha answers COULD NOT VERIFY** and writes nothing: a "
      "second answer over a third file is indistinguishable from the first "
      "one, and every record pointer below already points into the blob "
      "named here. Reproduce with `git hash-object <file>`.")
    a("")
    a(f"source-blob: {src_blob}  ({src_name})")
    a("")
    a(f"done-blob: {done_blob}  ({done_name})")
    a("")
    a("A report carrying NO blob line predates this check, and an absent "
      "record is not a mismatch — it is an unpinned run, which this build "
      "says rather than treating as agreement.")
    a("")
    a("## Reconciliation")
    a("")
    a("| quantity | count |")
    a("|---|---|")
    a(f"| top-level bullets in `{src_name}` | {read.total_bullets} |")
    a(f"| of those, ENTRIES (bold, or led by a grade-shaped word) | "
      f"{len(read.entries)} |")
    a(f"| of those, non-entry prose bullets (not migrated) | "
      f"{len(read.non_entry_bullets)} |")
    a(f"| of those, bullets in a section §4 row 1 CUTS | "
      f"{len(read.cut_bullets)} |")
    a(f"| items written to `{ctx.items_path.name}` | {n_items} |")
    a(f"| of those, CLOSURES routed to `{ctx.done_path.name}` instead | "
      f"{len(closures)} |")
    a(f"| entries reported UNCLASSIFIED or AMBIGUOUS (not written) | "
      f"{len(unclassified)} |")
    a(f"| archive bodies in `{ctx.done_path.name}` (verbatim) | "
      f"{archive_count} |")
    a(f"| entries routed to the ledger | "
      f"{'COULD NOT VERIFY' if ledger_count is None else ledger_count} |")
    a("")
    ident_ok = (len(read.entries)
                == n_items + len(closures) + len(unclassified))
    a(f"**Identity:** {len(read.entries)} entries read = {n_items} written + "
      f"{len(closures)} closed + {len(unclassified)} unclassified — "
      f"{'HOLDS' if ident_ok else 'FAILS'}. THREE columns, not two: a closure "
      "read out of the source carrier is neither written as an item nor "
      "unclassified, and folding it into either would make one of those "
      "numbers say something it does not.")
    a("")
    bullets_ok = (read.total_bullets == len(read.entries)
                  + len(read.non_entry_bullets) + len(read.cut_bullets))
    a(f"**Bullet identity:** {read.total_bullets} top-level bullets = "
      f"{len(read.entries)} entries + {len(read.non_entry_bullets)} prose + "
      f"{len(read.cut_bullets)} cut — {'HOLDS' if bullets_ok else 'FAILS'}. "
      "This is the identity that makes 'not migrated' visible: every bullet "
      "in the source is in exactly one of the three columns, so a bullet the "
      "migration simply did not see would show up as a gap in the sum rather "
      "than as nothing at all.")
    a("")
    a(f"**Conservation (§3.1), computed on the produced files:** "
      f"items {n_items} + done {archive_count} = {n_items + archive_count}; "
      f"baseline {baseline} + added 0 − compacted 0 = {baseline}. "
      f"{'HOLDS' if n_items + archive_count == baseline else 'FAILS'}.")
    a("")
    a("The bullet count and the archive count use DIFFERENT notions of an "
      "entry, deliberately and not accidentally: the archive count is "
      "`items_mod.archive_entries`, every line opening `- ` in the archived "
      "body, which is the notion the conservation identity uses on both "
      "sides of the migration. The entry count above is the migration's own "
      "notion. Where the two differ over the same file, the difference is "
      "sub-bullets at column zero and is not a lost body.")
    a("")
    a("## The MIGRATION WRITE-RULES (§3.1, blocking and fixed)")
    a("")
    a("**No migrated entry inherits READY.** READY is the desk's judgment "
      "that a fresh context could execute an item now, made about a carrier "
      "that no longer exists. Every entry below is written NEW.")
    a("")
    a("**Every migrated OPEN entry carries a TYPED blocker.** The typing is "
      "the rule, not a detail: \"every migrated item is blocked\" is "
      "satisfied by prose, and prose sits in nobody's court — which is the "
      "entry that ages out silently. The three branches:")
    a("")
    a("| branch | blocker | why |")
    a("|---|---|---|")
    a("| old READY / RECORD | `decision` | the grade returns to the desk for "
      "a re-grade; it is not inherited |")
    a("| PARKED carrying its named missing evidence | `evidence` | it is "
      "already in the MACHINE's court, and converting it to a decision would "
      "move a waiting item into the operator's queue for no reason |")
    a("| slot-incomplete (everything else) | `decision` | NEW with a decision "
      "naming what the desk must supply — never `NONE` |")
    a("")
    bt = blocker_types(read.entries)
    a("**Blockers written, PER TYPE.** A total is the number that hides the "
      "untyped one, so there is no total here:")
    a("")
    a("| blocker type | entries |")
    a("|---|---|")
    for typ in ("decision", "evidence", "item-id", "NONE", "untyped"):
        a(f"| `{typ}` | {bt.get(typ, 0)} |")
    a("")
    a(f"`untyped` and `NONE` are both **{bt.get('untyped', 0) + bt.get('NONE', 0)}"
      "**, and either being non-zero is a finding rather than a statistic. "
      "Under the closed goal vocabulary nearly every migrated open item is "
      "slot-incomplete anyway, so the `decision` count will LOOK like \"all\" "
      "— which is precisely why the criterion is stated per type.")
    a("")
    a("**The done home holds no blocker.** The write-rules are about OPEN "
      "items; a blocker in the closure home is a shape finding, not a "
      "migration output. This migration writes nothing into the done home but "
      "the verbatim archive, so the property holds by construction — and it "
      "is CHECKED by the done home's own shape check rather than assumed.")
    a("")
    a("## What a CLOSED entry is (lc-18, lc-19, lc-21)")
    a("")
    a("A source carrier states a closure in three shapes, and this run read "
      "all three. A closure written back into the open carrier is the one "
      "migration defect that is SILENT — the entry lands looking exactly "
      "like work nobody has started.")
    a("")
    a("| shape | disposition |")
    a("|---|---|")
    a("| a CLOSURE GRADE WORD at the bullet start (`"
      + "`, `".join(items_mod.GRADES_CLOSED)
      + "`) | archived verbatim to the done home |")
    a("| an entry under the carrier's own CLOSURE HEADING | archived "
      "verbatim to the done home |")
    a("| a closure word standing alone LATER in an ungraded title | "
      "**REFUSED** — reported, never written either way |")
    a("| an OPEN grade word under the closure heading | **REFUSED** — the "
      "word says open and the section says closed |")
    a("")
    a(f"**Closure heading(s) read:** "
      + ", ".join(f"`## {s}`" for s in read.closure_sections)
      + f" — {read.closure_sections_why}.")
    a("")
    a("The heading is stated rather than assumed because the two failures "
      "look identical from outside: \"no entry sat under a closure heading\" "
      "and \"this run looked under a heading this carrier does not use\" "
      "both produce a zero here.")
    a("")
    a("**The SECTION decides before the TITLE does, and the order is the "
      "rule.** An ungraded entry under a closure heading carries no grade "
      "word precisely BECAUSE the heading already said it. Scanning its "
      "title for a closure word first would refuse every one of them as "
      "ambiguous — a guard firing on legitimate work, which is the repair "
      "that trains a reader to discount the warning that will one day be "
      "real.")
    a("")
    a("**Closure bodies are archived VERBATIM, at a named line range, and "
      "are never re-rendered as items.** A closure's body is the author's "
      "own record of what closed and why; re-rendering it into slots would "
      "be a paraphrase of a body nobody reads twice. This is a DRY RUN, so "
      f"the source in `{src_name}` is untouched and the range still "
      "resolves.")
    a("")
    a("## Grade-word rules (design §4 row 1, §3.1)")
    a("")
    a("These classify the SOURCE word — which entries are entries, which are "
      "closures, and which are unclassifiable. An OPEN grade is then "
      "overridden to NEW by the write-rules above; the mapping is kept "
      "because it decides UNCLASSIFIED, and because a reader needs to see "
      "which word each entry carried.")
    a("")
    a("| source grade word | §4 row 1 says | after the §3.1 write-rules |")
    a("|---|---|---|")
    for word, (grade, why) in RULES.items():
        if grade in items_mod.GRADES_CLOSED:
            a(f"| `{word}` | {grade} | **CLOSED** — {why} |")
            continue
        shown = "NEW" if grade == "PARKED?" else grade
        a(f"| `{word}` | {shown} | NEW — {why} |")
    a(f"| (ungraded) | {UNGRADED_RULE[0]} | NEW — {UNGRADED_RULE[1]} |")
    a("| (ungraded, under a closure heading) | — | **CLOSED** — "
      f"{SECTION_CLOSURE_RULE} |")
    a("| anything else | — | **UNCLASSIFIED**, reported with its grade word "
      "and line number (D-f). Never guessed. |")
    a("")
    a("## Outcome per class")
    a("")
    counts: dict = {}
    for e in read.entries:
        key = e.grade_word or "(ungraded)"
        if e.closure:
            target = "CLOSED → the done home"
        else:
            target = e.grade or "UNCLASSIFIED / AMBIGUOUS"
        counts.setdefault((key, target), 0)
        counts[(key, target)] += 1
    a("| source grade word | → | entries |")
    a("|---|---|---|")
    for (word, target), n in sorted(counts.items(), key=lambda kv: -kv[1]):
        a(f"| `{word}` | {target} | {n} |")
    a("")
    a("## Entries by source section")
    a("")
    a("| section | entries |")
    a("|---|---|")
    for name, n in read.sections.items():
        a(f"| {name[:90]} | {n} |")
    a("")
    if read.non_entry_bullets:
        a("## Non-entry bullets — prose, not migrated")
        a("")
        a("Top-level bullets that are neither bold nor led by a "
          "grade-shaped word. They sit in the carrier's PROSE sections and "
          "are listed here so that 'not migrated' is a visible decision "
          "rather than a silent omission.")
        a("")
        for lineno, section in read.non_entry_bullets:
            a(f"- `{src_name}:{lineno}` — section: {section[:70]}")
        a("")
    if read.cut_bullets:
        a("## CUT by §4 row 1 — the grade-vocabulary declarations")
        a("")
        a("\"`## Grades` prose declarations, `Closure-home:` line, declared "
          "extra words | CUT — the tool owns the vocabulary\". The bullets "
          "below DESCRIBE the old carrier's grade words; they are not work "
          "items, and the successor's vocabulary is the tool's closed five. "
          "Listed rather than dropped in silence — the first run of this "
          "migration migrated them as items, which is what a cut nobody "
          "prints looks like from the other side.")
        a("")
        for lineno, section in read.cut_bullets:
            a(f"- `{src_name}:{lineno}` — section: {section[:70]}")
        a("")
        a(f"The successor's closure home is named by "
          f"`.claude/lifecycle.json`'s `closure-home` key, not by a "
          f"`Closure-home:` line in the carrier: one fact, one home, and the "
          f"declaration is where every reader already resolves it.")
        a("")
    a("## Closures routed to the done home")
    a("")
    if not closures:
        a(f"**None — zero.** No entry in `{src_name}` carried a closure grade "
          "word and none sat under "
          + ", ".join(f"`## {s}`" for s in read.closure_sections)
          + ". The zero is stated because an omitted line reads as \"checked "
            "and clean\" whichever of the two it was.")
    else:
        a(f"{len(closures)} entry/ies. Each body is in "
          f"`{ctx.done_path.name}` VERBATIM, under the archive heading, "
          "preceded by a comment naming its source line range and the rule "
          "that routed it.")
        a("")
        a("| line | source grade word | section | rule |")
        a("|---|---|---|---|")
        for e in closures:
            a(f"| `{src_name}:{e.line}-{e.end_line}` | "
              f"`{e.grade_word or '(ungraded)'}` | {e.section[:40]} | "
              f"{e.rule[:110]} |")
    a("")
    a("## UNCLASSIFIED and AMBIGUOUS — findings for the desk")
    a("")
    if not unclassified:
        a("**None — zero.** Every entry read matched a rule or a closure "
          "shape.")
    else:
        a(f"{len(unclassified)} entry/ies match no rule, or are AMBIGUOUS "
          "about whether they are closed. Each is reported with its line "
          "number and its reason and was NOT written to either successor "
          "home. This is a finding for the desk: a guessed mapping is a "
          "design decision taken by the migration and invisible afterwards, "
          "because it looks exactly like a rule. **The entries themselves "
          "are quoted in the RUN's output, not here** — this file is "
          "generated into a tree that may be public and it describes rather "
          "than republishes.")
        a("")
        a("| line | grade word | section | why |")
        a("|---|---|---|---|")
        for e in unclassified:
            a(f"| `{src_name}:{e.line}` | `{e.grade_word}` | "
              f"{e.section[:40]} | {e.unclassified_why} |")
    a("")
    a("## What this migration does NOT carry, named rather than discovered")
    a("")
    a("- **`goal`, `done-criterion` and `evidence` have no rule in §4 row "
      "1.** Only the write-set does (\"write-set absent → UNKNOWN\"). A slot "
      "cannot be empty, so `goal` and `done-criterion` are written `UNKNOWN` "
      "at the same width the design gives the write-set, and `evidence` "
      f"carries the source line range in `{src_name}`. The design gap is "
      "reported, not closed here.")
    a("- **The PARKED branch of §4 row 1 is unreachable over this carrier.** "
      "\"PARKED→PARKED with a typed blocker or NEW\" turns on a typed "
      "blocker, and the old carrier has no blocker slot; no rule in the "
      "design derives one from a body. Every PARKED entry therefore takes "
      "the NEW branch, and the parked-ness — which court the item waits in "
      "— is not carried across. That is the largest single information loss "
      "in this migration and it is a decision for the desk, not for the "
      "tool.")
    a("- **A NARRATIVE section's bold bullets migrate as items, because §4 "
      "row 1 states no rule that stops them.** The rule list covers grade "
      "words and \"ungraded\", and a handoff paragraph's bullet is ungraded — "
      "so it becomes a NEW item. Only `## Grades` is CUT by name. The "
      "per-section table above is where this is visible: a section whose "
      "heading is a status narrative rather than a queue contributed entries, "
      "and whether that is wanted is the desk's call, not a rule this tool "
      "may invent.")
    a("- **Live entry BODIES are not carried.** An item's slots are one line "
      "each; the old entries are paragraphs. In this DRY RUN the bodies stay "
      f"in `{src_name}`, and git keeps them either way — but a later act "
      "that retires the old carrier drops them to history, and that is worth "
      "deciding rather than discovering.")
    a("")
    a("## Where these findings WENT (R3)")
    a("")
    a("**A finding in an audit nobody routes is a finding nobody acts on.** "
      "§3.8c bullet 8 sends this report's findings into the carrier as ITEMS "
      "via intake, and has the report point at the item ids rather than "
      "carrying the findings itself. The table below is READ FROM THE "
      "CARRIER at report time — items whose `evidence` slot cites this file — "
      "so it cannot go stale against it, and an empty table means the routing "
      "has not happened rather than that there was nothing to route.")
    a("")
    routed = routed_items(ctx, report_rel)
    if not routed:
        a("**None yet.** On the FIRST run of a migration this is expected and "
          "says so: the items are added after the report exists, and "
          "`lifecycle migrate --report-only` re-renders this section once "
          "they do. On any later run an empty table is the finding.")
    else:
        a("| item | grade | blocked-by | requirement |")
        a("|---|---|---|---|")
        for it in routed:
            a(f"| `{it.ident}` | {it.grade} | "
              f"`{it.slots.get('blocked-by', '')[:40]}` | "
              f"{it.slots.get('requirement', '')[:150]} |")
        a("")
        a(f"{len(routed)} finding(s) routed. Each is an ITEM with a typed "
          "blocker, so it sits in a named court and the retire lane can see "
          "it age — which is the whole difference between a routed finding "
          "and a paragraph in a file.")
    a("")
    a("## Ledger")
    a("")
    if ledger_count is None:
        a(f"COULD NOT VERIFY — {lwhy}")
    else:
        a(f"`{ctx.ledger_path.name}` holds {ledger_count} line(s). Nothing "
          "migrates into the ledger (§3.6, §4 row 1); the acceptance "
          "criterion is that this number is zero, and it is printed as a "
          "number because \"nothing migrated\" and \"nothing was counted\" "
          "read the same in prose.")
    a("")
    return "\n".join(L) + "\n"
