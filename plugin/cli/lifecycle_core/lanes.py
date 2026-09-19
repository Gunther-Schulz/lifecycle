"""Lanes, the trigger predicate, and the generated ROUTER (design §3.3/§3.4).

THE TWO EXIT-CODE CONTRACTS MEET HERE, and nowhere else in this system. A
lane's `Trigger:` is a COMMAND this module EXECUTES, and its codes are the
design's reserved set:

    0  fire     1  quiet     >=2  broken

`lane list` READS that code and REPORTS the lane's state. It EXITS under the
`lifecycle` verb contract in `exits.py` (0 clean / 2 a finding / 3 could not
verify). The two collide on the value `2` — "a finding" there, "broken"
here — and the collision is deliberate rather than accidental: a `lane list`
run that finds a broken predicate exits `2` because it FOUND something, not
because it saw a `2`. `trigger_state()` below returns a WORD, never a code,
so no caller can accidentally pass one contract's integer into the other.

THE BROKEN PATH IS THE WHOLE REASON THIS IS SPECIFIED. A predicate that
errors — `gh` unauthenticated, a moved script, a syntax error — exits >=2,
and a router that folded that into "quiet" would render a dead lane as a
clean board. Broken is louder than quiet, and it is a FINDING.

LONGHAND, NEVER SPARSE (§3.3). The roster count and every repo's resolution
state are printed in full: an absent roster is BROKEN, a listed repo that
does not resolve is NAMED. A table that omits what it has nothing to say
about renders as silence, and silence reads as clean.

WHAT THIS BUILD DOES NOT DO. `Decides:` and `Ends:` are reported by PRESENCE
and not parsed, and the one-screen cap is not checked at all — both wave 2's.
THE DECISION TABLE IS THE EXCEPTION, and lc-12 is why: it is §3.3's fourth
parsed part and the only one with no label, so the `startswith` scan that
finds the other three is structurally incapable of reaching it, and a lane
missing it printed all three labels it could find and exited CLEAN. Its
PRESENCE is therefore checked (`has_decision_table`) and its absence is a
FINDING; its rows are not parsed. This module still parses no part's body
beyond `Trigger:` — what the router needs — and says so in its own output
rather than implying it read the whole lane.
"""

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from . import exits
from . import declaration as decl

#: The roster: one repo path per line. `#` comments and blank lines ignored.
#: Under `$XDG_CONFIG_HOME` (defaulting per the XDG spec) rather than
#: `~/.claude/`, for the reason `firelog.py` records: a read or write under
#: the Claude config directory costs a permission dialog on this machine.
ROSTER_REL = Path("lifecycle") / "repos"

#: Where a repo keeps its lane bodies (§3.8's REPO layer: `lanes/*.md`).
LANES_DIR = "lanes"

#: A predicate that has not answered in this long is BROKEN, not quiet. A
#: hung predicate and a quiet one are indistinguishable to a waiter, and the
#: quiet reading is the one that renders a dead lane as a clean board.
TRIGGER_TIMEOUT_S = 30

_TRIGGER_LINE = re.compile(r"^Trigger:\s*(.+?)\s*$")
#: The lane's other three parsed parts (§3.3). Their PRESENCE is reported;
#: parsing their bodies is wave 2's.
LANE_PARTS = ("Decides:", "Trigger:", "Ends:")

#: THE FOURTH PART, and the one no label can reach (lc-12). §3.3 names FOUR
#: parsed parts; `LANE_PARTS` above carries three, because a decision table
#: has no `Label:` prefix — the `startswith` scan is STRUCTURALLY incapable
#: of finding it, so a lane missing the table printed all three labels it
#: could find and the board exited CLEAN over a lane that routes nowhere.
#:
#: WHAT IS RECOGNISED, AND WHERE EACH CLAUSE COMES FROM. §3.3 says "a
#: decision table → workflows" and names NO syntax, so the shape is derived
#: from the two facts the design does state: a lane body is MARKDOWN
#: (`lanes/<name>.md`), whose only table construct is the pipe table, and the
#: table maps a condition TO a workflow, which takes at least two columns.
#: The delimiter row is the signature — the one line of a markdown table that
#: does not occur in ordinary prose — and the header line above it is what
#: makes it a table rather than a stray horizontal rule.
#:
#: BODY ROWS ARE NOT REQUIRED, deliberately. A header and delimiter with no
#: rows is an EMPTY decision table, which is a different defect from a
#: MISSING one; demanding a row here would refuse a lane that carries the
#: part §3.3 asks for, and a guard that fires on legitimate work stops the
#: lane (R11). Two lane fixtures in this repo's own tests are exactly that
#: shape, and they are legitimate.
_TABLE_DELIM = re.compile(r"^\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*){1,}\|?$")


def has_decision_table(text: str) -> bool:
    """True where a lane body carries §3.3's decision table.

    THE PAIR THIS EXISTS TO SEPARATE: a lane carrying the table, and a lane
    carrying every LABELLED part and no table. Nothing could tell them apart
    before — `parts_present` printed `Decides:, Trigger:, Ends:` over both
    and the router exited CLEAN over both.
    """
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if i == 0:
            continue
        if not _TABLE_DELIM.match(line.strip()):
            continue
        header = lines[i - 1].strip()
        if header and "|" in header:
            return True
    return False


def table_absent_message(name: str) -> str:
    """ONE BODY for the finding, read by both renderers. A message restated
    in the longhand and again in the JSON emitter is two bodies for one fact,
    and the `--json` non-negotiable is that the two carry the SAME finding.
    """
    return (f"lane {name!r} carries no decision table. §3.3 names FOUR parsed "
            "parts, and the table is the one with no label: the `startswith` "
            "scan that finds `Decides:`, `Trigger:` and `Ends:` cannot reach "
            "it, so this lane printed all three and read as complete. A lane "
            "with no table routes nowhere — it is a trigger with no "
            "disposition, which is the clean-board shape this module exists "
            "against.")

#: The three states a trigger predicate's exit code maps to. WORDS, never
#: codes: returning the integer would let a caller pass a trigger's `2` into
#: a place that reads the verb contract's `2`, and the two mean different
#: things.
FIRE, QUIET, BROKEN = "FIRE", "QUIET", "BROKEN"


def roster_path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config")
    return Path(base) / ROSTER_REL


def lane_stub(name: str) -> str:
    """A lane body carrying all FOUR of §3.3's parsed parts (`LANE_PARTS`
    above finds three of them by `startswith`; the decision table has no
    label and is structurally undetectable by that scan — lc-12, dispositioned
    — but the stub emits it anyway, since a stub that silently dropped a
    part would read as though its author forgot it).

    ONE STUB BODY, NOT TWO. This used to live in `init.py` as a private
    `_lane_stub`, written only for `init --lane`'s own use; `lane new`
    writes the identical file for the identical reason, so this is the one
    body both callers share rather than two copies that happen to agree
    today. Moved here (wave 2, item A) because `lanes.py` is where every
    other lane-shape fact already lives (`LANE_PARTS`, `LANES_DIR`,
    `_TRIGGER_LINE`) — `init.py` imports this rather than the reverse, since
    a lane body's shape is this module's concern and `init` is one of two
    callers of it.

    THE `Trigger:` LINE IS A REAL, SAFE, QUIET PREDICATE (`exit 1`), not a
    grammar of its own: a lifecycle lane's trigger is EXECUTED AS A SHELL
    COMMAND (`evaluate_trigger` above; design §3.3), so a placeholder that
    is not valid shell would make every freshly created lane read as BROKEN
    in `lane list` — the opposite of quiet-by-default, and exactly the
    "stub whose own trigger does not parse... ship[ping] at scale" defect
    this function exists to prevent.
    """
    return (
        f"# Lane: {name}\n\n"
        "Decides: TODO — the decisions this lane may take alone, each with "
        "its recording act (anything else returns to the operator)\n\n"
        "Trigger: exit 1  # TODO — replace with the real predicate: "
        "0 fire / 1 quiet / >=2 broken\n\n"
        "| condition | workflow |\n"
        "|---|---|\n"
        "| TODO | TODO |\n\n"
        "Ends: TODO — a closed set of dispositions, each an item transition\n"
    )


# --- the trigger predicate ---------------------------------------------------

@dataclass
class Trigger:
    """One predicate's answer. `state` is a WORD; `code` is kept only so a
    report can show what the predicate actually exited."""
    state: str
    code: int | None
    detail: str = ""


def evaluate_trigger(command: str, cwd: Path | None = None,
                     timeout: int = TRIGGER_TIMEOUT_S) -> Trigger:
    """Run a `Trigger:` predicate and map its exit code to a state word.

    THE RESERVED CODES ARE §3.3'S, and the mapping is total on purpose:
    every integer is one of the three, so there is no code that falls
    through into silence. A predicate that could not be RUN AT ALL (no
    shell, an OSError) is BROKEN too — the lane's state is unknown and
    unknown is not quiet.

    ONE EVALUATOR, NOT TWO. `item ready`'s `evidence <predicate>` blocker is
    "evaluated like a trigger" (§3.1), and it calls THIS function. Two
    bodies behind one contract would disagree about the `>=2` BROKEN case
    first, which is the case that decides whether a dead lane reads as a
    clean board.
    """
    if not command or not command.strip():
        return Trigger(BROKEN, None,
                       "the predicate is empty. A lane with no `Trigger:` "
                       "command has no state, and no state is not quiet.")
    try:
        p = subprocess.run(command, shell=True, cwd=str(cwd) if cwd else None,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return Trigger(BROKEN, None,
                       f"the predicate did not answer within {timeout}s. A "
                       "hung predicate and a quiet one look identical to a "
                       "waiter, and the quiet reading renders a dead lane as "
                       "a clean board.")
    except (OSError, ValueError) as exc:
        return Trigger(BROKEN, None, f"the predicate could not be run ({exc!r}).")
    code = p.returncode
    tail = (p.stderr or p.stdout or "").strip().replace("\n", " ")[:200]
    if code == 0:
        return Trigger(FIRE, 0, tail)
    if code == 1:
        return Trigger(QUIET, 1, tail)
    return Trigger(BROKEN, code,
                   f"the predicate exited {code}; >=2 is RESERVED for BROKEN "
                   f"(§3.3). {tail}")


# --- lane bodies -------------------------------------------------------------

@dataclass
class Lane:
    name: str
    path: Path | None
    trigger: str | None = None
    #: Which of §3.3's LABELLED parts the body carries. Reported rather than
    #: enforced; the one-screen cap is wave 2's. The decision table is NOT in
    #: this list and cannot be — it has no label for `LANE_PARTS` to match —
    #: which is what `table_present` below carries instead (lc-12).
    parts_present: list = field(default_factory=list)
    #: Whether the body carries §3.3's decision table. `None` where the body
    #: was never READ (no file, unreadable): "no opinion" and "read it, no
    #: table" are different facts and only the second is a finding — the same
    #: split `lane_files_on_disk` makes for an absent directory.
    table_present: bool | None = None
    problem: str | None = None


def read_lane(repo: Path, name: str) -> Lane:
    """Load one lane body, pull its `Trigger:` line out of it, and answer
    whether it carries §3.3's decision table (lc-12).

    A lane the declaration names and the tree does not carry is a PROBLEM
    with a name, never an omission: the router prints it, because a lane
    missing from a sparse table reads as a lane with nothing to say.
    """
    path = repo / LANES_DIR / f"{name}.md"
    if not path.is_file():
        return Lane(name, None, problem=(
            f"declared lane {name!r} has no body at {LANES_DIR}/{name}.md. A "
            "declared lane with no file cannot be triggered, and a router "
            "that skipped it would show a shorter board rather than a broken "
            "one."))
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return Lane(name, path, problem=f"{path} could not be read ({exc!r}).")
    trig = None
    for line in text.split("\n"):
        m = _TRIGGER_LINE.match(line)
        if m:
            trig = m.group(1)
            break
    present = [p for p in LANE_PARTS
               if any(ln.startswith(p) for ln in text.split("\n"))]
    lane = Lane(name, path, trigger=trig, parts_present=present,
                table_present=has_decision_table(text))
    if trig is None:
        lane.problem = (f"lane {name!r} carries no `Trigger:` line. §3.3 makes "
                        "the trigger one of the four parsed parts; without it "
                        "the lane has no state to report.")
    return lane


def lane_files_on_disk(repo: Path) -> list:
    """Every lane BODY the tree carries, by door name, sorted.

    THE OTHER DIRECTION OF THE REGISTRATION INVARIANT. `read_lane` above
    answers "the declaration names this door — is there a body?"; this
    answers "there is a body — does the declaration name this door?". Until
    this existed the invariant held one way only: `LANES_DIR` was used solely
    to build a path from an ALREADY-DECLARED name, so a file the declaration
    did not list was invisible to every verb, and `lane list` rendered the
    repo as a clean board with zero lanes over a tree carrying one.

    NO DIRECTORY, NO OPINION. A repo with no `lanes/` is not a repo hiding an
    undeclared lane, and it must not be reported as one — the empty list here
    is a real answer, not a shrug (the caller in `declaration.py` is where an
    unreadable directory becomes COULD NOT VERIFY).

    `*.md` AND THE STEM, because that is the exact shape `read_lane` resolves
    a declared name to (`lanes/<name>.md`). A scan that collected some other
    shape would report doors the declaration could never have named, which is
    a guard firing on legitimate work.
    """
    d = repo / LANES_DIR
    if not d.is_dir():
        return []
    return sorted(p.stem for p in d.glob("*.md") if p.is_file())


# --- the roster --------------------------------------------------------------

@dataclass
class RepoRow:
    """One line of the roster, resolved — or named as unresolved."""
    raw: str
    path: Path | None = None
    resolution: str = ""
    declaration: dict | None = None
    decl_code: int = exits.CLEAN
    decl_notes: list = field(default_factory=list)
    #: The SAME two halves `decl_notes` renders as prose, kept STRUCTURED —
    #: `decl.Finding` objects and unverified-reason strings — so a consumer
    #: (the `--json` emitter) can carry each finding's row id as its own
    #: field rather than only inside a rendered bracketed-row-name string.
    #: (Worded around the literal bracket form on purpose: the emit-site
    #: coverage scan in `roster.py` reads this file's SOURCE for that exact
    #: shape, and a docstring quoting it would report itself as an
    #: unregistered site — `roster.py`'s own docstring names the same trap.)
    decl_findings: list = field(default_factory=list)
    decl_unverified: list = field(default_factory=list)
    lanes: list = field(default_factory=list)
    triggers: dict = field(default_factory=dict)


def read_roster(path: Path):
    """`(lines, why-not)` — the roster's repo paths, comments dropped."""
    if not path.exists():
        return None, (
            f"no roster at {path}. §3.3 calls an absent roster BROKEN: the "
            "router is GENERATED over it, so with no roster there is no board "
            "at all — and an empty board renders exactly like a board on "
            "which every lane is quiet.")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"{path} could not be read ({exc!r})."
    out = []
    for raw in text.split("\n"):
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        out.append(s)
    return out, None


#: THE ROSTER'S OWN CONTRACT LINE (lc-246). The roster either IS the
#: declared-repo population or is a deliberate SUBSET of it, and those are
#: different files with different meanings for every mechanism generated over
#: them. Today it says neither, and that silence is what makes an INCOMPLETE
#: roster the one case the router has no answer for: a listed-but-thin roster
#: renders as a clean board, indistinguishable from a complete one.
#:
#: DECLARED IN THE FILE rather than inferred from its contents, because the
#: two readings are indistinguishable BY CONTENT — a roster listing one repo
#: out of ten is either wrong or deliberate, and nothing in the list says
#: which. Only its author can.
ROSTER_CONTRACT = "contract:"
ROSTER_POPULATION = "population"
ROSTER_SUBSET = "subset"
ROSTER_CONTRACTS = (ROSTER_POPULATION, ROSTER_SUBSET)

#: How a declaration announces a repo, used by the sweep below. The same
#: relative path `declaration.DECLARATION_REL` names; spelled from that
#: constant rather than restated, so a repo that moves its declaration moves
#: this sweep with it.
_DECL_GLOB = "*/.claude/lifecycle.json"


def roster_contract(path: Path):
    """`(contract, why-not)` — which reading the roster DECLARES of itself.

    Read from a `# contract: population|subset` comment line. `None` is the
    honest answer for a roster that declares nothing, and it is NOT a default
    to one of the two: defaulting would answer, in the tool's own voice, the
    question this whole entry exists to make someone answer.
    """
    if not path.exists():
        return None, f"no roster at {path}."
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"{path} could not be read ({exc!r})."
    for raw in text.split("\n"):
        s = raw.strip()
        if not s.startswith("#"):
            continue
        body = s.lstrip("#").strip()
        if not body.lower().startswith(ROSTER_CONTRACT):
            continue
        word = body[len(ROSTER_CONTRACT):].strip().split()[0:1]
        word = (word[0].lower().strip(" .,;") if word else "")
        if word in ROSTER_CONTRACTS:
            return word, None
        return None, (
            f"the roster's contract line says {word!r}, which is not one of "
            + " or ".join(ROSTER_CONTRACTS) + ".")
    return None, (
        "the roster declares no contract. Add ONE comment line — "
        f"`# {ROSTER_CONTRACT} {ROSTER_POPULATION}` if this file is meant to "
        f"list every declaring repo, or `# {ROSTER_CONTRACT} "
        f"{ROSTER_SUBSET}` if it is a deliberate selection — because a "
        "roster listing one repo out of ten is either wrong or intended and "
        "nothing in the list itself can say which.")


def declared_repos_under(roots) -> list:
    """Every repo carrying a declaration under these roots, BY SWEEP.

    THE SCOPE IS THE CALLER'S CLAIM AND IS NEVER GUESSED HERE. A sweep's
    reach IS the basis of any absence it reports, and a root hardcoded in
    this package would be both a machine path (law 6) and a reach nobody
    chose — the same defect one level up from the roster this function
    grades. So the roots come in; with none, the caller gets no population
    and must say so.
    """
    found = []
    for root in roots:
        base = Path(root).expanduser()
        if not base.is_dir():
            continue
        for hit in base.glob("**/" + _DECL_GLOB):
            repo = hit.parent.parent
            if not repo.is_dir():
                continue
            # THE SAME PREDICATE THE ROSTER SIDE USES, and it is not
            # tidiness. `resolve_repo_row` refuses a directory that is not a
            # git work tree, so a sweep counting one would put a repo in the
            # population that the roster could never legitimately list — and
            # the divergence it caused could never be cleared by any edit to
            # the roster. That is a finding with no repair, which trains the
            # override reflex exactly as a guard firing on legitimate work
            # does. Two populations compared by two predicates are not
            # comparable at all.
            row = resolve_repo_row(str(repo))
            if row.resolution.startswith("UNRESOLVED"):
                continue
            found.append(Path(row.path).resolve())
    return sorted(set(found))


def roster_divergence(path: Path, roots) -> dict:
    """What the roster lists against what the sweep finds, both directions.

    BOTH DIRECTIONS, because they are different findings with different
    repairs: a declaring repo the roster OMITS is a mechanism scoped to a
    population nobody chose, while a roster line naming a repo that carries
    no declaration is a line that will fail to resolve on every future run.
    """
    entries, why = read_roster(path)
    listed = []
    for raw in (entries or []):
        row = resolve_repo_row(raw)
        if not row.resolution.startswith("UNRESOLVED"):
            listed.append(Path(row.path).resolve())
    swept = declared_repos_under(roots)
    return {
        "roster_error": why,
        "listed": sorted(set(listed)),
        "swept": swept,
        "missing": [p for p in swept if p not in set(listed)],
        "extra": [p for p in listed if p not in set(swept)],
    }


def check_roster_population(out, roots) -> int:
    """Does the roster match the declared-repo population? (lc-246)

    THREE ANSWERS, and the middle one is the whole point. With no scope
    stated this CANNOT answer — a sweep with no roots finds nothing, and
    nothing is shaped exactly like a complete roster. With no contract
    declared it also cannot answer, because the same divergence is a defect
    under one reading and the intended state under the other.

    IT NEVER REPAIRS WHAT IT MEASURES. There is deliberately no verb here
    that rewrites the roster from the sweep: a tool that fixes the population
    it is supposed to report on has no independent reading left to give, and
    the next run would confirm its own edit. The roster is the operator's
    file; this prints what to put in it.
    """
    path = roster_path()
    contract, why_contract = roster_contract(path)
    if not roots:
        out("roster population: COULD NOT VERIFY — no sweep root was "
            "given, so the declared-repo population was never enumerated. "
            "A sweep with no roots returns nothing, and nothing here reads "
            "exactly like a roster that already lists everything. The root "
            "is the caller's claim about reach and this package will not "
            "invent one: a path baked in here would be a machine path "
            "(law 6) and a scope nobody chose.")
        return exits.COULD_NOT_VERIFY

    div = roster_divergence(path, roots)
    if div["roster_error"] and not div["listed"]:
        out(f"roster population: COULD NOT VERIFY — {div['roster_error']}")
        return exits.COULD_NOT_VERIFY

    swept, listed = div["swept"], div["listed"]
    missing, extra = div["missing"], div["extra"]
    out(f"roster population: {len(listed)} listed, {len(swept)} found by "
        f"sweep under {', '.join(str(r) for r in roots)}")

    if contract is None:
        out("    FINDING [roster_population_undeclared] " + (why_contract or "")
            + " Until it says, this divergence cannot be graded: "
            f"{len(missing)} declaring repo(s) are absent from the roster "
            f"and {len(extra)} listed repo(s) carry no declaration, and "
            "BOTH numbers are the intended state under one reading and a "
            "defect under the other.")
        for p_ in missing:
            out(f"        absent from the roster: {p_}")
        for p_ in extra:
            out(f"        listed, carries no declaration: {p_}")
        return exits.FINDING

    if contract == ROSTER_SUBSET:
        out(f"    roster population: CLEAN — the roster DECLARES itself a "
            f"{ROSTER_SUBSET} ({len(missing)} declaring repo(s) are "
            "deliberately not listed), so a divergence from the swept "
            "population is this file's intended state and not a finding. "
            "What that reading OWES is elsewhere: every verb that reads this "
            "file as THE population is then reading a subset, and that is a "
            "finding about those verbs rather than about this list.")
        return exits.CLEAN

    if not missing and not extra:
        out(f"    roster population: CLEAN — the roster declares itself the "
            f"{ROSTER_POPULATION} and matches the sweep exactly, over "
            f"{len(swept)} repo(s). Both numbers are shown above because "
            "`0 missing` over a sweep that found nothing prints the same.")
        return exits.CLEAN

    out("    FINDING [roster_population_diverges] the roster declares itself "
        f"the {ROSTER_POPULATION} and does not match the sweep: "
        f"{len(missing)} declaring repo(s) absent from it, {len(extra)} "
        "listed repo(s) carrying no declaration. Every mechanism generated "
        "over this file — `lane list`'s board, and any reading of law 25's "
        "EVERY DECLARED REPO that trusts it — is scoped to a population "
        "nobody chose, and renders the rest as ABSENT rather than as "
        "UNLISTED.")
    for p_ in missing:
        out(f"        absent from the roster: {p_}")
    for p_ in extra:
        out(f"        listed, carries no declaration: {p_}")
    out("    This tool does not write that file. A verb that repaired the "
        "population it is supposed to measure would confirm its own edit on "
        "the next run.")
    return exits.FINDING


def resolve_repo_row(raw: str) -> RepoRow:
    """One roster line → a resolution state, NAMED whatever the answer."""
    row = RepoRow(raw=raw)
    p = Path(raw).expanduser()
    if not p.exists():
        row.resolution = "UNRESOLVED — no such path"
        return row
    if not p.is_dir():
        row.resolution = "UNRESOLVED — not a directory"
        return row
    row.path = p.resolve()
    git = subprocess.run(["git", "-C", str(row.path), "rev-parse",
                          "--show-toplevel"], capture_output=True, text=True)
    if git.returncode != 0:
        row.resolution = "UNRESOLVED — not a git work tree"
        return row
    top = Path(git.stdout.strip()).resolve()
    if top != row.path:
        row.resolution = f"UNRESOLVED — inside another work tree ({top})"
        return row

    res = decl.read(row.path)
    row.decl_code = res.code
    row.declaration = res.declaration
    row.decl_findings = list(res.findings)
    row.decl_unverified = list(res.unverified)
    row.decl_notes = ([f"FINDING [{f.row}] {f.message}" for f in res.findings]
                      + [f"COULD NOT VERIFY: {u}" for u in res.unverified])
    if res.declaration is None:
        row.resolution = "RESOLVED, DECLARATION UNREADABLE"
        return row
    row.resolution = "RESOLVED"
    lanes = res.declaration.get("lanes")
    row.lanes = list(lanes) if isinstance(lanes, list) else []
    return row


# --- `lane new` ---------------------------------------------------------------

def cmd_lane_new(args, out, repo: Path) -> int:
    """`lifecycle lane new <door>` — write `lanes/<door>.md` from
    `lane_stub()`, as a STUB a human then fills.

    REFUSES IF THE FILE EXISTS; `--force` overwrites. No silent overwrite —
    the same rule `init` applies to the declaration it writes.

    IT REGISTERS ITS OWN OUTPUT (lc-14, judgment desk 2026-08-26). Writing
    the body and declaring the door were two acts and only the first had a
    verb, so this verb's DEFAULT outcome was a lane file no verb could see:
    `lane list` walks the declaration's OWN `lanes` list and has no directory
    scan, so the door had no state, no trigger evaluation and no line on the
    board. The hand step that closed it was delivered by nobody — the same
    assumed-delivery shape as `init` leaving carriers uncreated — and a hint
    in this verb's output is not a delivery. So the name goes into the
    declaration's `lanes` list in the SAME run, and the door reads QUIET in
    `lane list` immediately.

    NO NEW VERB, deliberately. `init` already writes the declaration, so a
    declaration write is not a new class of act for this tool, and a `lane
    register` verb would have collided with the existing one — which puts a
    REPO on the router's roster, a different mechanism entirely.

    A REGISTRATION THAT DID NOT HAPPEN IS NOT CLEAN. Where the declaration
    cannot be read or its `lanes` key is not a list, the body is on disk and
    undeclared; this verb says so and exits COULD NOT VERIFY rather than
    reporting a door it did not open. The residue is loud either way —
    `check_lanes_registered` makes an undeclared body a `kind check` finding.

    VERIFIES ITS OWN WRITE against the real parser before returning CLEAN:
    a stub `read_lane` cannot read back is not a stub, it is a defect this
    verb would otherwise ship at scale.
    """
    door = args.door
    lanes_dir = repo / LANES_DIR
    path = lanes_dir / f"{door}.md"
    if path.exists() and not getattr(args, "force", False):
        out(f"FINDING [lane_new_exists] lane {door!r} already exists at "
            f"{path}. Refusing to overwrite it — pass --force to "
            "overwrite. A silent overwrite of a lane body is not "
            "available.")
        return exits.FINDING

    lanes_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(lane_stub(door), encoding="utf-8")
    out(f"wrote lane stub: {path}")

    lane = read_lane(repo, door)
    if lane.problem:
        out(f"internal: the stub just written does not read back cleanly "
            f"via this repo's own reader: {lane.problem} Nothing further "
            "is claimed about it.")
        return exits.COULD_NOT_VERIFY
    out(f"trigger: {lane.trigger!r}")
    out("parts present: " + (", ".join(lane.parts_present) or "(none)"))

    added, why = decl.add_lane(repo, door)
    if why is not None:
        out(f"COULD NOT VERIFY: {why} The body is on disk and the door is "
            "NOT declared, which `kind check` now reports as a finding "
            "([lane_undeclared]) rather than leaving it invisible.")
        return exits.COULD_NOT_VERIFY
    if added:
        out(f"declared: {door!r} appended to this repo's `lanes` list in "
            f"{decl.DECLARATION_REL}.")
    else:
        # "Already there" and "added" are different facts, and a verb that
        # printed one line for both would leave a caller unable to tell a
        # working registration from a no-op (`lane register`'s own rule).
        out(f"declared: {door!r} was already in this repo's `lanes` list — "
            "nothing written to the declaration.")
    return exits.CLEAN


# --- `lane register` ----------------------------------------------------------

def cmd_lane_register(args, out) -> int:
    """Put a repo on the roster — the verb that CREATES the router's input.

    NOTHING CREATED THIS FILE BEFORE. `lane list` answered `roster_absent` on
    this machine for a whole wave, correctly, because the roster's creation
    sat outside every write boundary and no verb owned it. An absent roster is
    BROKEN by design (§3.3), so the state was loud — but a loud state nobody
    can clear is a trigger that trains the override reflex, which is why the
    verb exists rather than an instruction to write the file by hand.

    IT REFUSES WHAT `lane list` WOULD LATER CALL UNRESOLVED. Registering a
    path that does not resolve would move the finding from this verb, where
    the caller is standing right next to the mistake, into every future router
    run — a listing that is broken from birth.

    IT IS IDEMPOTENT, and it says which of the two happened. "Added" and
    "already there" are different facts, and a verb that printed one line for
    both would leave a caller unable to tell a working registration from a
    no-op.
    """
    path = roster_path()
    target = Path(args.repo_path).expanduser() if args.repo_path else Path.cwd()
    row = resolve_repo_row(str(target))
    if row.resolution.startswith("UNRESOLVED"):
        out(f"FINDING [repo_unresolved] {target} does not resolve: "
            f"{row.resolution}. Refusing to register it — a roster line that "
            "cannot be resolved is a finding in every future `lane list`, and "
            "the moment to catch it is now, next to the caller who typed it.")
        return exits.FINDING
    resolved = str(row.path)

    entries, why = read_roster(path)
    if entries is None and path.exists():
        out(f"COULD NOT VERIFY: {why}")
        return exits.COULD_NOT_VERIFY
    entries = entries or []
    already = [e for e in entries
               if str(Path(e).expanduser().resolve()) == resolved
               or e == resolved]
    if already:
        out(f"already registered: {resolved}")
        out(f"roster: {path}  ({len(entries)} repo(s) listed)")
        out("lane register: CLEAN — nothing written. The roster already "
            "carries this repo, and saying so is not the same answer as "
            "having added it.")
        return exits.CLEAN

    if args.dry_run:
        out(f"DRY RUN — would append {resolved} to {path}")
        out(f"roster: {len(entries)} repo(s) listed today, "
            f"{len(entries) + 1} after.")
        out("lane register: CLEAN — nothing was written (--dry-run).")
        return exits.CLEAN

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        existed = path.exists()
        with open(path, "a", encoding="utf-8") as fh:
            if not existed:
                fh.write("# lifecycle roster — one repo path per line.\n"
                         "# `lane list` is GENERATED over this file; an "
                         "absent roster is BROKEN, never an empty board.\n")
            fh.write(resolved + "\n")
    except OSError as exc:
        out(f"COULD NOT VERIFY: the roster at {path} could not be written "
            f"({exc!r}). Nothing was registered and nothing else is claimed.")
        return exits.COULD_NOT_VERIFY

    out(f"registered: {resolved}")
    out(f"roster: {path}  ({len(entries) + 1} repo(s) listed)")
    out("lane register: CLEAN")
    return exits.CLEAN


# --- `lane list` -------------------------------------------------------------
#
# WAVE 2: `--json`, beside the longhand, from ONE shared walk. Splitting the
# walk from its two renderers is what makes "same exit code, same finding
# set" (the design's own non-negotiable for `--json`) true BY CONSTRUCTION
# rather than by two independently written passes that happen to agree
# today: a single `gather_lane_list` computes every finding and the overall
# code exactly once, and `render_*_longhand`/`render_*_json` only FORMAT what
# it already decided. Neither renderer may compute a code or a finding of
# its own.

@dataclass
class LaneRunResult:
    """One declared lane's state, as the walk found it."""
    name: str
    parts_present: list = field(default_factory=list)
    #: Mirrors `Lane.table_present` exactly, tri-state included: `None` is a
    #: body this walk never read, `False` is the lc-12 finding.
    table_present: bool | None = None
    trigger: str | None = None
    problem: str | None = None
    not_run: bool = False
    state: str | None = None          # FIRE / QUIET / BROKEN, or None
    predicate_exit: int | None = None
    detail: str = ""
    #: Set to "trigger_broken" exactly where the longhand prints that
    #: bracketed row name — never invented for a JSON-only purpose, since a
    #: row id not proven by the refusal roster is not this walk's to mint.
    row: str | None = None


@dataclass
class RepoRunResult:
    """One roster line's resolution and everything found beneath it."""
    raw: str
    resolution: str
    repo_unresolved: bool = False
    declaration_code: int | None = None
    #: Mirrors `Result.declaration is None` from `decl.read()` exactly —
    #: named rather than re-derived from the other fields, which is what a
    #: repo with a CLEAN declaration but zero lanes and no findings would be
    #: indistinguishable from under a re-derived guess.
    declaration_present: bool = False
    decl_findings: list = field(default_factory=list)       # decl.Finding
    decl_unverified: list = field(default_factory=list)     # str
    trigger_policy: object = None
    lanes_declared: list = field(default_factory=list)
    lane_runs: list = field(default_factory=list)            # LaneRunResult


@dataclass
class RosterRunResult:
    """The whole `lane list` walk, computed once, rendered twice."""
    roster_path: Path
    roster_absent: bool
    roster_error: str | None = None
    roster_count: int = 0
    repos: list = field(default_factory=list)                # RepoRunResult
    total_lanes: int = 0
    fired: int = 0
    quiet: int = 0
    broken: int = 0
    #: Lanes whose body was read and carries no decision table (lc-12).
    #: Counted BESIDE `broken` and never inside it: BROKEN is a state of the
    #: trigger PREDICATE (§3.3's reserved codes), and a lane with a working
    #: predicate and no table has a state — what it lacks is the part that
    #: turns that state into a route.
    table_absent: int = 0
    code: int = exits.CLEAN


def gather_lane_list(args) -> RosterRunResult:
    """The generated router's WALK — every finding and the final code,
    computed exactly once. No printing here; `render_*` below format this.
    """
    path = roster_path()
    entries, why = read_roster(path)
    if entries is None:
        return RosterRunResult(roster_path=path, roster_absent=True,
                               roster_error=why, code=exits.FINDING)

    run = RosterRunResult(roster_path=path, roster_absent=False,
                          roster_count=len(entries))
    codes = [exits.CLEAN]
    for raw in entries:
        row = resolve_repo_row(raw)
        rr = RepoRunResult(raw=raw, resolution=row.resolution,
                           repo_unresolved=row.resolution.startswith("UNRESOLVED"))
        if rr.repo_unresolved:
            codes.append(exits.FINDING)
            run.repos.append(rr)
            continue

        rr.declaration_code = row.decl_code
        rr.decl_findings = row.decl_findings
        rr.decl_unverified = row.decl_unverified
        codes.append(row.decl_code)
        if row.declaration is None:
            run.repos.append(rr)
            continue

        rr.declaration_present = True
        rr.trigger_policy = row.declaration.get("trigger-policy")
        rr.lanes_declared = list(row.lanes)

        for name in row.lanes:
            run.total_lanes += 1
            lane = read_lane(row.path, name)
            # ITS OWN VERDICT, NEVER FOLDED INTO `problem` (lc-12). `problem`
            # is rendered under `trigger_broken` by every branch below, so a
            # missing table folded in there would ship under another row's
            # name AND mark a lane with a working predicate BROKEN. It is
            # also computed HERE, before the branches, because a lane can be
            # both: a body with no `Trigger:` line and no table is two
            # findings, and a branch that returned early would print one.
            if lane.table_present is False:
                run.table_absent += 1
                codes.append(exits.FINDING)
            if lane.problem:
                run.broken += 1
                codes.append(exits.FINDING)
                rr.lane_runs.append(LaneRunResult(
                    name=name, parts_present=lane.parts_present,
                    table_present=lane.table_present,
                    trigger=lane.trigger, problem=lane.problem,
                    row="trigger_broken"))
                continue
            if args.no_run:
                codes.append(exits.COULD_NOT_VERIFY)
                rr.lane_runs.append(LaneRunResult(
                    name=name, parts_present=lane.parts_present,
                    table_present=lane.table_present,
                    trigger=lane.trigger, not_run=True))
                continue
            t = evaluate_trigger(lane.trigger, cwd=row.path)
            lr = LaneRunResult(name=name, parts_present=lane.parts_present,
                               table_present=lane.table_present,
                               trigger=lane.trigger, state=t.state,
                               predicate_exit=t.code, detail=t.detail)
            if t.state == BROKEN:
                lr.row = "trigger_broken"
                run.broken += 1
                codes.append(exits.FINDING)
            elif t.state == FIRE:
                run.fired += 1
            else:
                run.quiet += 1
            rr.lane_runs.append(lr)
        run.repos.append(rr)

    run.code = exits.worst(codes)
    return run


def render_lane_list_longhand(run: RosterRunResult, out) -> None:
    """The board a human reads. Every state printed, including the zeros: a
    repo with no declared lanes says so in a line of its own, because "0
    lanes" and "this repo was skipped" are different facts and only one of
    them is clean.
    """
    if run.roster_absent:
        out(f"FINDING [roster_absent] {run.roster_error}")
        out(f"roster: {run.roster_path}")
        out("lane list: FINDING — the router could not be generated. This is "
            "a FINDING and not a could-not-verify: §3.3 names an absent "
            "roster BROKEN, which is a state of the system rather than a "
            "limit of this run.")
        return

    out(f"roster: {run.roster_path}")
    out(f"roster count: {run.roster_count} repo(s) listed")
    out("")

    for rr in run.repos:
        out(f"repo: {rr.raw}")
        out(f"    resolution: {rr.resolution}")
        if rr.repo_unresolved:
            out("    FINDING [repo_unresolved] the roster lists this repo and "
                "it does not resolve. A router that dropped the line would "
                "print a shorter board rather than a broken one.")
            out("")
            continue

        out(f"    declaration: {exits.word(rr.declaration_code)}")
        for f in rr.decl_findings:
            out(f"        FINDING [{f.row}] {f.message}")
        for u in rr.decl_unverified:
            out(f"        COULD NOT VERIFY: {u}")
        if _no_declaration_body(rr):
            out("")
            continue

        out(f"    trigger-policy: {rr.trigger_policy}")
        out(f"    declared lanes: {len(rr.lanes_declared)}"
            + (f" — {', '.join(rr.lanes_declared)}" if rr.lanes_declared else
               " — EMPTY, declared rather than absent (§3.0: an empty "
               "declared list is a stated fact)"))

        for lr in rr.lane_runs:
            # BEFORE the trigger branches, and outside them: a lane can carry
            # both findings, and the BROKEN branch below returns.
            if lr.table_present is False:
                out(f"    lane {lr.name}: no decision table")
                out(f"        FINDING [lane_table_absent] "
                    f"{table_absent_message(lr.name)}")
            if lr.problem:
                out(f"    lane {lr.name}: BROKEN — {lr.problem}")
                out("        FINDING [trigger_broken] a lane whose body or "
                    "trigger cannot be read has no state, and no state is "
                    "not quiet.")
                continue
            out(f"    lane {lr.name}: parts present "
                f"{', '.join(lr.parts_present) or '(none)'}")
            out(f"        trigger: {lr.trigger}")
            if lr.not_run:
                out("        NOT RUN (--no-run): the state below would be the "
                    "predicate's, and this run did not ask it. Not quiet.")
                continue
            out(f"        state: {lr.state}   predicate exit: {lr.predicate_exit}")
            if lr.detail:
                out(f"        detail: {lr.detail}")
            if lr.state == BROKEN:
                out("        FINDING [trigger_broken] the predicate's exit is "
                    ">=2, which §3.3 RESERVES for BROKEN. Reported as a "
                    "finding rather than folded into quiet: a dead lane that "
                    "renders quiet is a clean board over a router that does "
                    "not work.")
        out("")

    out(f"lanes: {run.total_lanes} total   FIRE {run.fired}   "
        f"QUIET {run.quiet}   BROKEN {run.broken}   "
        f"NO DECISION TABLE {run.table_absent}")
    out("this build parses `Trigger:` only; `Decides:` and `Ends:` are "
        "reported by PRESENCE and are parsed in wave 2. The decision table "
        "is CHECKED for presence and its absence is a finding above (lc-12) "
        "— its rows are not parsed either. The one-screen cap is wave 2's "
        "too — this run does not check it and does not imply it did.")
    out(f"lane list: {exits.word(run.code)}")


def _no_declaration_body(rr: "RepoRunResult") -> bool:
    """True where `resolve_repo_row` never reached a readable declaration
    (`decl.read()`'s own `Result.declaration is None`) — mirrored directly
    via `declaration_present` rather than re-derived from the other fields,
    which would misjudge a CLEAN declaration with zero lanes and no
    findings as this case."""
    return not rr.declaration_present


def render_lane_list_json(run: RosterRunResult, out) -> None:
    """ONE JSON document on stdout. Same exit code, same finding set as the
    longhand — both renderers read the identical `RosterRunResult`, so
    nothing here computes a verdict of its own; it only names each finding's
    row id as a FIELD rather than only inside rendered prose (§B).
    """
    if run.roster_absent:
        doc = {
            "roster_path": str(run.roster_path),
            "roster_absent": True,
            "findings": [{"row": "roster_absent", "message": run.roster_error}],
            "code": exits.word(run.code),
            "exit": run.code,
        }
        out(json.dumps(doc, indent=2))
        return

    repos_out = []
    for rr in run.repos:
        entry = {"raw": rr.raw, "resolution": rr.resolution}
        if rr.repo_unresolved:
            entry["findings"] = [{
                "row": "repo_unresolved",
                "message": "the roster lists this repo and it does not "
                           "resolve. A router that dropped the line would "
                           "print a shorter board rather than a broken one.",
            }]
            repos_out.append(entry)
            continue

        entry["declaration"] = {
            "code": exits.word(rr.declaration_code),
            "findings": [{"row": f.row, "message": f.message}
                        for f in rr.decl_findings],
            "unverified": list(rr.decl_unverified),
        }
        if _no_declaration_body(rr):
            repos_out.append(entry)
            continue

        entry["trigger_policy"] = rr.trigger_policy
        entry["lanes_declared"] = list(rr.lanes_declared)
        lane_rows = []
        for lr in rr.lane_runs:
            lane_entry = {
                "name": lr.name,
                "parts_present": list(lr.parts_present),
                "table_present": lr.table_present,
                "trigger": lr.trigger,
            }
            if lr.table_present is False:
                # A `findings` LIST, the shape the declaration half already
                # uses, rather than a second scalar beside `row`: a lane can
                # carry this finding and `trigger_broken` at once, and a
                # scalar would drop one — which is the finding set DIVERGING
                # between the two renderings, the one thing `--json` may
                # never do. The message body is the longhand's own.
                lane_entry["findings"] = [{
                    "row": "lane_table_absent",
                    "message": table_absent_message(lr.name),
                }]
            if lr.problem:
                lane_entry["problem"] = lr.problem
            if lr.not_run:
                lane_entry["not_run"] = True
            if lr.state is not None:
                lane_entry["state"] = lr.state
                lane_entry["predicate_exit"] = lr.predicate_exit
                if lr.detail:
                    lane_entry["detail"] = lr.detail
            if lr.row:
                lane_entry["row"] = lr.row
            lane_rows.append(lane_entry)
        entry["lanes"] = lane_rows
        repos_out.append(entry)

    doc = {
        "roster_path": str(run.roster_path),
        "roster_count": run.roster_count,
        "repos": repos_out,
        "lanes_total": run.total_lanes,
        "fired": run.fired,
        "quiet": run.quiet,
        "broken": run.broken,
        "table_absent": run.table_absent,
        "code": exits.word(run.code),
        "exit": run.code,
    }
    out(json.dumps(doc, indent=2))


def cmd_lane_list(args, out) -> int:
    """The generated router. LONGHAND by default; `--json` selects the
    machine-readable emitter. Both read the SAME walk (`gather_lane_list`):
    same exit code, same finding set, whichever rendering was asked for.
    """
    run = gather_lane_list(args)
    if getattr(args, "json", False):
        render_lane_list_json(run, out)
    else:
        render_lane_list_longhand(run, out)
    return run.code
