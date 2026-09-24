"""The ARC carrier — the multi-session unit of work (lc-231, D-2).

WHAT AN ARC IS, and why it is a new kind rather than a widened lane. A LANE
is a stateless router row: a declaration entry whose `Trigger:` a `lane list`
run evaluates, pointing at a runbook. It holds no per-instance state and has
no stages. An arc is a STATEFUL CARRIER ENTRY — goal, current stage, the
narrowing, premises, beliefs with their bases and kill-conditions, a yield
count. Widening lanes to carry that would rebuild the item carrier inside the
router, which is two homes for one shape (invariant 3). The unification
question was asked FIRST and answered in the ledger before any of this was
built, because the repo may already own a mechanism and re-inventing one is
this arc's own recorded failure class.

WHAT IT IS FOR. statiker and daneel capture richly and in flight, and what
they do NOT do is outlive their own arc: the record lives while the protocol
runs, then the arc ends and session 11 re-derives what session 3 knew.
Lifecycle's job is to be what they write INTO, so the capture survives the
protocol, gets a home and a staleness rule, and is readable by the next
session whether or not it runs any protocol at all.

ARCS ARE OPTIONAL (walk 3). A project with no through-line degenerates under
a stage machine into ceremony, so nothing instantiates an arc automatically
and a zero-arc repo runs on its queue untouched. This module exists to be
used per-arc, never to be satisfied per-project.

THE BODY'S SHAPE IS NOT UNIVERSAL AND SAYS SO. The narrowing's form is a
per-arc declaration — eliminative, palette-with-dispositions, or none —
because walk 2 showed a divergent arc INVERTING the narrowing into a palette
whose dead ends are the main asset, and a schema that hardcoded the
convergent form would have made three of the eight requirements wrong rather
than merely missing.

CONSERVATION IS PROJECT-SCOPED AND TRAVELS WITH THE REPO. The fire log is
advisory only — machine-local, best-effort — so the authoritative history is
`arcs/INDEX.md`'s head counters, tool-written in the SAME ACT as the body
write (law 9's one-act move discipline).
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from . import grammar

#: Where the two homes live, relative to the repo. Spelled here because the
#: declaration names them too and a second spelling would drift: these are
#: the DEFAULTS a fresh repo is initialised with, and the declaration is
#: authoritative for a repo that has moved them.
ARCS_HOME = "arcs/*.md"
CLOSED_ARCS_HOME = "arcs/closed/*.md"
ARCS_DIR = "arcs"
CLOSED_DIR = "arcs/closed"
#: EXTENSIONLESS ON PURPOSE, and it is the whole repair of a class that
#: surfaced in FOUR readers. `arcs/INDEX.md` sat inside the arcs kind's own
#: home glob `arcs/*.md`, so every reader of that home had to skip it by
#: name — `live_slugs`, the schema reach's `carrier_paths`, the pre-commit
#: hook, and finally `retire`'s GENERIC walker, where a name-based exclusion
#: would have been a kind-specific hack in shared code. MEASURED rather than
#: assumed: pathlib's glob MATCHES a leading-dot name where shell glob does
#: not, so `.index.md` escapes nothing here; dropping the extension is what
#: takes it out of the glob. It is then a persisted thing resolving to no
#: kind, which invariant 1 forbids — so it is REGISTERED as its own kind
#: rather than hidden inside another's home.
INDEX_REL = "arcs/INDEX"

#: An arc body's FIXED slots, in order — the same discipline the item carrier
#: keeps: a block carries exactly these, exactly once, in this sequence, so a
#: diff shows what CHANGED rather than where a slot wandered to.
#:
#: `narrowing` carries its SHAPE and not only its content (requirement 3):
#: the walks showed the form differing by work-kind, so the arc declares
#: which form it is running and a reader knows what the lines under it mean.
ARC_SLOTS = ("goal", "stage", "narrowing", "premises", "beliefs", "yield")

#: The declared narrowing forms. CLOSED, and registered under the vocabulary
#: contract like every other closed value set here — a form nobody can
#: express is exactly the state that contract exists to surface.
NARROWING_FORMS = ("eliminative", "palette-with-dispositions", "none")

#: APPENDED LINE KINDS — the arc's record, below its fixed slots.
#:
#: WHY APPENDED RATHER THAN IN A SLOT, and the constraint is the carrier's
#: own: a slot value is ONE LINE, and an arc accumulates many beliefs and
#: many premises. The item carrier already solved this shape — fixed run
#: first, dated lines appended below — so the arc follows it rather than
#: inventing a second layout. A reader that knows one knows the other.
#:
#: THE FIXED `beliefs:` AND `premises:` SLOTS ARE PROSE, NEVER A COUNT. A
#: persisted total is the label-over-body class: correct when written and
#: silently false once the body grows, with arithmetic the only reader that
#: would notice. So the slots carry the arc's own one-line statement of what
#: it currently rests on, and anything that needs the NUMBER counts the
#: lines at read time.
BELIEF_LINE = "belief"
PREMISE_LINE = "premise"
REDERIVE_LINE = "re-derive"
DISPOSITION_LINE = "disposition"
DEADLINE_LINE = "deadline"
ADVANCED_LINE = "advanced"
NARROWED_LINE = "narrowed"
VERDICT_LINE = "verdict"
YIELD_LINE = "yielded"
APPENDED_LINE_KINDS = (BELIEF_LINE, PREMISE_LINE, REDERIVE_LINE,
                       DISPOSITION_LINE, DEADLINE_LINE, ADVANCED_LINE,
                       NARROWED_LINE, VERDICT_LINE, YIELD_LINE)

#: The mark an OUTWARD stage carries (requirement 8). Outward stages wire the
#: carve-out floor into STRUCTURE rather than into anybody's memory: an act
#: whose consequence leaves the operator's controlled sphere is one the arc
#: has to render a STOP for, and rendering it at the stage's ENTRY is the
#: whole correction — astra's finding was that an outward STOP printed at the
#: stage's CLOSE arrives after the act it exists to govern.
OUTWARD_MARK = "outward"

#: How a disposition may answer a re-derive flag. CLOSED: the point of the
#: flag is that the arc cannot move past a belief nobody re-examined, and an
#: open-ended answer would let "noted" clear it.
DISPOSITIONS = ("re-derived", "accepted-stale")

_APPENDED = re.compile(
    r"^(" + "|".join(APPENDED_LINE_KINDS) + r"):\s*(\S+)\s+(.*)$")


@dataclass(frozen=True)
class Appended:
    """One appended record line: its kind, the id it concerns, its text."""
    kind: str
    ident: str
    text: str


def appended_lines(text: str) -> list:
    """Every appended record line in one arc body, in file order."""
    out = []
    for raw in text.splitlines():
        m = _APPENDED.match(raw.strip())
        if m:
            out.append(Appended(m.group(1), m.group(2), m.group(3).strip()))
    return out


def undispositioned(text: str) -> list:
    """Belief ids carrying a re-derive flag no disposition has answered.

    THE CONSUMING SEAM (astra-a5). A reopen that only PRINTED its affected
    beliefs left the arc free to advance past them — the flag existed in an
    output nobody re-read, which is the same evaporation the carrier exists
    to stop. So the flag is a LINE, and this is the predicate the movement
    verbs consult.

    LAST WINS, per id: a belief can be reopened, dispositioned, and reopened
    again as evidence moves, and only the latest act counts. Reading the
    first would freeze an arc on a question already answered.
    """
    state = {}
    for rec in appended_lines(text):
        if rec.kind == REDERIVE_LINE:
            state[rec.ident] = True
        elif rec.kind == DISPOSITION_LINE:
            state[rec.ident] = False
    return sorted(i for i, flagged in state.items() if flagged)


def citers(text: str, belief_id: str) -> list:
    """Belief ids whose own line NAMES `belief_id` — the propagation set.

    WITHIN-ARC ONLY, AND DECLARED (the design's cross-arc ruling). A belief
    in another arc, or a carrier item, that cites this one is PRINTED and
    inboxed rather than auto-flagged: flagging across a boundary would let
    one arc's reopen silently stop another's movement, and the party that
    would have to dispose of it never asked for the edge.
    """
    out = []
    for rec in appended_lines(text):
        if rec.kind != BELIEF_LINE or rec.ident == belief_id:
            continue
        if re.search(r"\b" + re.escape(belief_id) + r"\b", rec.text):
            out.append(rec.ident)
    return sorted(set(out))

#: The INDEX head counters. `baseline` is the population that existed before
#: the counters did; `opened` and `closed` are FLOW. Conservation reads
#: opened − closed against the live bodies, never a stock count against a
#: cap: growth is controlled by flow here as everywhere (R22).
INDEX_COUNTERS = ("baseline", "opened", "closed")

_COUNTER = re.compile(r"^(baseline|opened|closed):\s*(\d+)\s*$")


@dataclass
class Arc:
    """One arc body, parsed."""
    slug: str
    slots: dict = field(default_factory=dict)
    line: int = 0


@dataclass
class Index:
    """The INDEX head counters, and what could not be read."""
    counters: dict = field(default_factory=dict)
    why: str = ""

    @property
    def ok(self) -> bool:
        return not self.why


def index_path(repo: Path) -> Path:
    return repo / INDEX_REL


def read_index(repo: Path) -> Index:
    """The head counters, or an Index carrying WHY they could not be read.

    A MISSING INDEX IS NOT ZERO. A repo that has never opened an arc has no
    counters, and answering `0/0/0` there would be indistinguishable from one
    whose INDEX was deleted — the loss case. So absence is reported as
    absence and the caller decides; `arc open` creates it, nothing else
    invents it.
    """
    path = index_path(repo)
    if not path.is_file():
        return Index(why=f"no arc index at {INDEX_REL}")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return Index(why=f"{INDEX_REL} could not be read ({exc!r})")
    counters = {}
    for raw in text.splitlines():
        m = _COUNTER.match(raw.strip())
        if m:
            counters[m.group(1)] = int(m.group(2))
    missing = [c for c in INDEX_COUNTERS if c not in counters]
    if missing:
        return Index(counters=counters,
                     why=f"{INDEX_REL} carries no "
                         + ", ".join(f"`{m}:`" for m in missing)
                         + " line, so conservation has no denominator")
    return Index(counters=counters)


def render_index(counters: dict, schema: int) -> str:
    """The INDEX file's whole body. ONE place spells it, as with every other

    carrier here: a caller composing the lines itself could write a file this
    module's own reader rejects.

    IT CARRIES A `schema:` HEAD like every other tool-written carrier, and
    that is not decoration. The live arc home is now REACHED by
    one-schema-per-repo (lc-242), and the reach is a glob over `arcs/*.md`
    which this file sits inside — so an unstamped index would be read as a
    carrier with no schema line and answer COULD NOT VERIFY forever. Stamping
    it is the honest resolution rather than teaching the reach to skip it:
    the index IS a tool-written carrier and one-schema-per-repo means what it
    says.
    """
    lines = [f"schema: {int(schema)}", ""]
    lines += [f"{c}: {int(counters.get(c, 0))}" for c in INDEX_COUNTERS]
    lines.append("")
    lines.append("# The arc index — FLOW counters, never a stock cap (R22).")
    lines.append("# `opened` and `closed` are written by `arc open` and `arc")
    lines.append("# close` in the same act as the body write (law 9), so a")
    lines.append("# crash leaves a DUPLICATE and never a loss. `baseline` is")
    lines.append("# the population that existed before these counters did.")
    return "\n".join(lines) + "\n"


#: Kept as the index's NAME, no longer as an exclusion anybody applies. The
#: index is outside the arc home's glob now, so no reader skips it — the
#: registry knows it as its own kind instead.
INDEX_STEM = "INDEX"


def is_arc_body(path: Path) -> bool:
    """Is this file an arc BODY?

    NO NAME EXCLUSION ANY MORE. It read `stem != INDEX` while the counters
    file lived inside this glob; four readers needed that skip and the fifth
    would have inherited it. The index is extensionless and registered
    separately now, so membership is simply what the home says it is.
    """
    return path.is_file() and path.suffix == ".md"


def live_slugs(repo: Path) -> list:
    """Every live arc body's slug, sorted. The CLOSED home is not read here:

    they are different populations and conservation compares them separately.
    """
    d = repo / ARCS_DIR
    if not d.is_dir():
        return []
    return sorted(p.stem for p in d.glob("*.md") if is_arc_body(p))


def closed_slugs(repo: Path) -> list:
    d = repo / CLOSED_DIR
    if not d.is_dir():
        return []
    return sorted(p.stem for p in d.glob("*.md") if is_arc_body(p))


@dataclass
class Conservation:
    """The two invariants, each with its own verdict and its own sign."""
    ok: bool
    sign: str = ""
    message: str = ""


def conservation(repo: Path) -> Conservation:
    """`opened − closed == live` AND `closed == closed files`.

    TWO SIGNS, TWO DIAGNOSES, and they are not one message. SHORT — fewer
    bodies than admissions — means a body left by a path that is not a
    closure: a hand deletion, a bad merge, the LOSS side. OVER means the
    homes hold more than was ever admitted, whose ordinary cause is an
    interrupted close, and it is RECOVERABLE. One message for both would tell
    the loss story over the recoverable case, which is why this repo's item
    carrier already carries two rows and why the arc carrier copies that
    rather than inventing a third spelling.

    THE SIGNS ARE THE REPO'S OWN CONVENTION AND WERE REVERSED in an earlier
    draft of the design (astra-a7). Fewer bodies than admissions is SHORT.
    """
    idx = read_index(repo)
    if not idx.ok:
        return Conservation(False, "unread", idx.why)
    opened = idx.counters["opened"]
    closed_n = idx.counters["closed"]
    baseline = idx.counters["baseline"]
    live_list = live_slugs(repo)
    closed_list = closed_slugs(repo)
    live = len(live_list)
    closed_files = len(closed_list)

    expect_live = baseline + opened - closed_n
    if live != expect_live:
        sign = "SHORT" if live < expect_live else "OVER"
        delta = abs(expect_live - live)
        if sign == "OVER":
            # lc-267: the same unaccounted-vs-duplicate split the item
            # carrier's `report_conservation` makes, at arc scale — a slug
            # in BOTH homes is this carrier's own `duplicate_id` shape (the
            # window an interrupted `arc close` leaves), and a surplus a
            # duplicate cannot explain names the other cause instead: a
            # body that reached a home without passing `arc open`/`arc
            # close`.
            dup = len(set(live_list) & set(closed_list))
            unaccounted = max(delta - dup, 0)
            if unaccounted:
                over_text = (
                    f"OVER means the homes hold more than was admitted. "
                    f"{dup} of the surplus match a slug in BOTH homes — the "
                    "ordinary INTERRUPTED-CLOSE case, where `arc close` "
                    f"appends before it deletes. {unaccounted} do"
                    f"{'es' if unaccounted == 1 else ''} not: that part is "
                    "UNACCOUNTED FOR, and its ordinary cause is a body that "
                    "reached a home without passing `arc open`/`arc "
                    "close`. Only the duplicate part is recoverable by "
                    "waiting for the close to finish; the unaccounted part "
                    "is not.")
            else:
                over_text = (
                    "OVER means the homes hold more than was admitted, "
                    "whose ordinary cause is an INTERRUPTED CLOSE: the move "
                    "appends to the closed home before deleting from the "
                    "live one, so the window between those writes "
                    "legitimately holds both. It is recoverable and must "
                    "not be repaired as if it were loss.")
        else:
            over_text = ("SHORT means a body left by a path that is not a "
                        "closure — a hand deletion or a bad merge — and it "
                        "is the LOSS side.")
        return Conservation(
            False, sign,
            f"arc conservation is {sign} by {delta}: the "
            f"index records baseline {baseline} + opened {opened} − closed "
            f"{closed_n} = {expect_live} live bodies and the home holds "
            f"{live}. " + over_text)
    if closed_files != closed_n:
        sign = "SHORT" if closed_files < closed_n else "OVER"
        return Conservation(
            False, sign,
            f"the arc index records {closed_n} closure(s) and the closed home "
            f"holds {closed_files} body/bodies ({sign}). The counter and the "
            "home are two spellings of one fact, and they part company "
            "silently.")
    return Conservation(True, "", f"arc conservation: {live} live, "
                                  f"{closed_files} closed, index agrees.")


def render_arc(slug: str, slots: dict, schema: int) -> str:
    """One arc body. THE ONLY place the on-disk shape is spelled.

    ITS OWN RENDERER, not `items.render_block` (attack r2 N1). That function
    renders ITEM shape — the item carrier's slots, in the item carrier's
    order — and reusing it would make the arc body an item body wearing a
    different heading. One spelling per kind, and the arc's spelling lives
    here.

    THE `schema:` HEAD IS THE LIVE ARC'S HALF OF THE VERSION STORY: live arcs
    enter the bump machinery and closed bodies PIN at the version they closed
    at. One file per arc means the head is per FILE rather than per carrier,
    which is what lets a closed body keep its own number while the live ones
    move together.
    """
    out = [f"schema: {int(schema)}", ""]
    out.append(grammar.render_heading(slug))
    for slot in ARC_SLOTS:
        out.append(grammar.render_slot(slot, slots[slot]))
    return "\n".join(out) + "\n"


def lane_name(slug: str, date: str) -> str:
    """The generated observer's name: `<arc-slug>-<date>`.

    DERIVED FROM BOTH, because either alone collides: one arc may hold
    several deadlines, and several arcs may share a date. A collision would
    put two observers on one row and retiring either would take the other's
    door off the board.
    """
    return f"{slug}-{date}"


def deadline_lanes(text: str, *, stage: str | None = None) -> list:
    """The generated lane names this arc owns, optionally for ONE stage.

    A DEADLINE BELONGS TO THE STAGE THAT SET IT, which is what makes
    retirement-on-advance correct rather than destructive: leaving a stage
    ends the deadlines that stage was keeping, and a lane that outlived its
    stage would keep firing about a date nothing is waiting for any more.
    Close and abandon take the remainder, whatever stage set it.
    """
    out = []
    for rec in appended_lines(text):
        if rec.kind != DEADLINE_LINE:
            continue
        parts = rec.text.split(None, 1)
        rec_stage = parts[0] if parts else ""
        if stage is None or rec_stage == stage:
            out.append(rec.ident)
    return sorted(set(out))


def set_slot(text: str, slot: str, value: str) -> str:
    """Rewrite one FIXED slot of an arc body in place.

    IN PLACE AND ONLY THE NAMED SLOT, the same discipline `_set_slots` keeps
    for items: re-rendering the whole body from a parsed dict would rewrite
    every slot this act did not mean to touch, and a slot rewritten
    identically is still a slot the diff claims authorship of.

    THE FIXED SLOTS ARE THE LIVE PICTURE; the appended lines are the record.
    `narrowing:` is overwritten because what is still open is a CURRENT
    state — a log of every narrowing ever held guides nothing — while
    `narrowed:` lines below keep what was ruled out and when. That split is
    the investigation record's own NOW-versus-ESTABLISHED shape, which is
    where this carrier's design came from.
    """
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if grammar.is_slot(ln, slot):
            lines[i] = grammar.render_slot(slot, value)
            break
    return "\n".join(lines)


def count_of(text: str, kind: str) -> int:
    """How many appended records of one kind this body carries.

    DERIVED AT READ TIME, never stored. A count written into a slot is
    correct the moment it is written and silently false once the body grows,
    with arithmetic the only reader that would notice — so the number is
    computed where it is asked for and the slot beside it stays prose.
    """
    return sum(1 for r in appended_lines(text) if r.kind == kind)


def render_status(repo: Path) -> list:
    """The `arc status` lines — the banner's renderer (N8).

    ONE SMALL FIXED FIELD-SET PER OPEN ARC, and the always-on cost is bounded
    by the EXIT rather than by a cap: arcs leave by being closed, so the
    block's size is governed by flow the way every other growth question here
    is (R22). A cap would bound a label and be escaped by relabelling.

    LONGHAND, NEVER A SPARSE TABLE. A repo with no arcs says so in a line of
    its own, because a silent block reads as "nothing to report" and
    "no arcs" and "the index is unreadable" are different answers — the same
    reason `lane list` prints its roster state longhand.
    """
    lines = []
    idx = read_index(repo)
    live = live_slugs(repo)
    if not idx.ok and not live:
        lines.append(f"arcs: NONE — {idx.why}. A repo that has never opened "
                     "an arc is the ordinary state: arcs are OPTIONAL and "
                     "instantiated per-arc, never a per-project obligation.")
        return lines
    if not live:
        lines.append("arcs: 0 open. The index is readable and the home is "
                     "empty, which is a different answer from having no "
                     "index at all.")
    for slug in live:
        path = repo / ARCS_DIR / f"{slug}.md"
        try:
            arc, _problems = parse_arc(path.read_text(encoding="utf-8"), slug)
        except OSError as exc:
            lines.append(f"  {slug}: COULD NOT VERIFY — body unreadable "
                         f"({exc!r})")
            continue
        lines.append(f"  {slug} — stage: {arc.slots.get('stage', '?')}")
        lines.append(f"      narrowing: {arc.slots.get('narrowing', '?')}")
        lines.append(f"      yield: {arc.slots.get('yield', '?')}")
    cons = conservation(repo)
    lines.append(f"  {cons.message}")
    return lines


def parse_arc(text: str, slug: str) -> tuple:
    """`(Arc, problems)` for one arc body's text.

    Problems are `(row, line, message)` triples, the same shape the item
    carrier's parser returns, so a caller that already renders findings from
    one can render these without a second formatter.
    """
    problems = []
    slots = {}
    for i, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip()
        if not line.strip() or line.startswith("#"):
            continue
        for slot in ARC_SLOTS:
            if grammar.is_slot(line, slot):
                if slot in slots:
                    problems.append((
                        "arc_shape", i,
                        f"arc {slug!r} carries `{slot}:` twice. A body "
                        "carries each slot exactly once; two lines for one "
                        "fact diverge from the moment they disagree."))
                slots[slot] = line.split(":", 1)[1].strip()
                break
    missing = [s for s in ARC_SLOTS if s not in slots]
    if missing:
        problems.append((
            "arc_shape", 1,
            f"arc {slug!r} is missing " + ", ".join(f"`{m}:`" for m in missing)
            + ". Every slot is written; a blank one is the undeclared-stage "
              "shape at arc scale — a plausible face on a gap."))
    form = (slots.get("narrowing") or "").split()[0:1]
    if form and form[0] not in NARROWING_FORMS:
        problems.append((
            "arc_shape", 1,
            f"arc {slug!r} declares narrowing form {form[0]!r}, which is not "
            f"one of {', '.join(NARROWING_FORMS)}. The form is a per-arc "
            "DECLARATION (requirement 3): a reader has to know whether the "
            "lines under it are eliminations or a palette, and a form nobody "
            "can express is the state the vocabulary contract exists to "
            "surface rather than to hide."))
    return Arc(slug, slots), problems
