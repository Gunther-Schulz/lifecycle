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
"""

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

#: An entry with no grade word at all. §4 row 1 lists "ungraded" beside the
#: seven words that share its rule.
UNGRADED_RULE = ("NEW", "§4 row 1: ungraded → NEW with a typed blocker or "
                        "DROPPED")

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


def read_carrier(text: str) -> Read:
    out = Read()
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
                            raw_first=content, text=stripped, bold=bold)
            out.sections[section] = out.sections.get(section, 0) + 1
            continue
        if pending is not None:
            pending.text += " " + raw.strip()
    close(len(lines))
    return out


def title_of(entry: Entry) -> str:
    """The entry's own headline, ONE line, capped.

    Taken from the bold segment where there is one — the carrier's own form
    puts the headline there — and from the first sentence otherwise. Never
    generated: a requirement line this tool composed would be a paraphrase
    with nobody's judgment behind it, and it would read exactly like one an
    author wrote.
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
    if len(headline) > REQUIREMENT_CAP:
        headline = headline[:REQUIREMENT_CAP - 1].rstrip() + "…"
    return headline


def classify(entry: Entry) -> None:
    stripped = entry.text.strip()
    m = _GRADE_WORD.match(stripped)
    entry.grade_word = m.group(1) if m else None
    if entry.grade_word is None:
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
        src_text = src.read_text(encoding="utf-8")
        done_text = "" if src_done is None else src_done.read_text(
            encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        out(f"COULD NOT VERIFY: a source carrier could not be read ({exc!r}).")
        return exits.COULD_NOT_VERIFY

    if not args.force:
        for p in (ctx.items_path, ctx.done_path):
            if p.exists():
                out(f"FINDING [migrate_would_overwrite] {p.name} already "
                    "exists. Refusing to overwrite a carrier: this is a DRY "
                    "RUN that PRODUCES the successor files, and a second run "
                    "over a carrier already in use would replace real work "
                    "with a re-derivation of the old one. Pass `--force` if "
                    "that is what is wanted.")
                return exits.FINDING

    read = read_carrier(src_text)
    for e in read.entries:
        classify(e)
    done_read = read_carrier(done_text)

    written, n_items = build_items(read.entries, ctx.prefix, src_name)
    unclassified = [e for e in read.entries if e.grade is None]

    # --- the successor files
    archive_count = items_mod.archive_entries(done_text)
    baseline = n_items + archive_count
    head = (f"schema: {items_mod.SCHEMA_FLOOR}\n"
            f"baseline: {baseline}\nadded: 0\ncompacted: 0\n")
    ctx.items_path.write_text(head + "\n" + "\n".join(written),
                              encoding="utf-8")
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
    ctx.done_path.write_text(
        archive_note + f"schema: {items_mod.SCHEMA_FLOOR}\n\n"
        + f"{items_mod.ARCHIVE_HEADING}\n\n" + done_text, encoding="utf-8")

    # --- the ledger: NOTHING migrates into it (§3.6, §4 row 1)
    if not ctx.ledger_path.exists():
        ctx.ledger_path.write_text(ledger_mod.head_text(), encoding="utf-8")
    lparsed, lwhy = ledger_mod.read(ctx.ledger_path)
    ledger_count = None if lparsed is None else len(lparsed.lines)

    # --- the report
    report_rel = args.report or (f"docs/audits/migration-report-"
                                 f"{date.today().isoformat()}.md")
    report_path = ctx.repo / report_rel
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_report(ctx, read, done_read, src_name, done_name, n_items,
                      unclassified, archive_count, baseline, ledger_count,
                      lwhy),
        encoding="utf-8")

    # --- the run's own answer
    out(f"migrate: DRY RUN — {src_name} and {done_name} are READ and are not "
        "edited, moved or deleted (D-e).")
    out(f"    source entries read:      {len(read.entries)}")
    out(f"    items written:            {n_items} → {ctx.items_path.name}")
    out(f"    UNCLASSIFIED (reported):  {len(unclassified)}")
    out(f"    reconciliation:           {len(read.entries)} read == "
        f"{n_items} written + {len(unclassified)} unclassified")
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
    if len(read.entries) != n_items + len(unclassified):
        # NOT A REGISTERED ROW, deliberately. Every entry is either written
        # or unclassified BY CONSTRUCTION — the two sets partition the read
        # entries — so no INPUT falsifies this, and a predicate no input can
        # falsify is unprovable rather than unproven. Registering it would
        # put a row in the roster that can never go red, which is the
        # clean-forever check the roster exists to prevent. It is kept as a
        # COULD NOT VERIFY on the run's own arithmetic: a run whose counts
        # disagree with themselves cannot promise a complete list, and that
        # is what code 3 means.
        out("COULD NOT VERIFY: this run's own arithmetic disagrees — "
            f"{len(read.entries)} entries read, {n_items} written, "
            f"{len(unclassified)} unclassified. Nothing below is a complete "
            "list.")
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
            "match no rule in §4 row 1 or §3.1 and were NOT written. Each is "
            "listed in the report with its grade word and line number. This "
            "is a finding for the desk, not a defect for the migration to "
            "resolve: a guessed mapping is a design decision taken here and "
            "invisible afterwards.")
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


def render_report(ctx, read, done_read, src_name, done_name, n_items,
                  unclassified, archive_count, baseline, ledger_count,
                  lwhy) -> str:
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
    a(f"| entries reported UNCLASSIFIED (not written) | "
      f"{len(unclassified)} |")
    a(f"| archive bodies in `{ctx.done_path.name}` (verbatim) | "
      f"{archive_count} |")
    a(f"| entries routed to the ledger | "
      f"{'COULD NOT VERIFY' if ledger_count is None else ledger_count} |")
    a("")
    a(f"**Identity:** {len(read.entries)} entries read = {n_items} written + "
      f"{len(unclassified)} unclassified — "
      f"{'HOLDS' if len(read.entries) == n_items + len(unclassified) else 'FAILS'}.")
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
    a("## Grade-word rules (design §4 row 1, §3.1)")
    a("")
    a("These classify the SOURCE word — which entries are entries and which "
      "are unclassifiable. The resulting grade is then overridden to NEW by "
      "the write-rules above; the mapping is kept because it decides "
      "UNCLASSIFIED, and because a reader needs to see which word each entry "
      "carried.")
    a("")
    a("| source grade word | §4 row 1 says | after the §3.1 write-rules |")
    a("|---|---|---|")
    for word, (grade, why) in RULES.items():
        shown = "NEW" if grade == "PARKED?" else grade
        a(f"| `{word}` | {shown} | NEW — {why} |")
    a(f"| (ungraded) | {UNGRADED_RULE[0]} | NEW — {UNGRADED_RULE[1]} |")
    a("| anything else | — | **UNCLASSIFIED**, reported with its grade word "
      "and line number (D-f). Never guessed. |")
    a("")
    a("## Outcome per class")
    a("")
    counts: dict = {}
    for e in read.entries:
        key = e.grade_word or "(ungraded)"
        target = e.grade or "UNCLASSIFIED"
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
    a("## UNCLASSIFIED — findings for the desk")
    a("")
    if not unclassified:
        a("None.")
    else:
        a(f"{len(unclassified)} entry/ies match no rule. Each is reported "
          "with its grade word and line number and was NOT written to the "
          "successor carrier. An unclassified entry is a finding for the "
          "desk: a guessed mapping is a design decision taken by the "
          "migration and invisible afterwards, because it looks exactly like "
          "a rule.")
        a("")
        a("| line | grade word | section |")
        a("|---|---|---|")
        for e in unclassified:
            a(f"| `{src_name}:{e.line}` | `{e.grade_word}` | "
              f"{e.section[:60]} |")
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
