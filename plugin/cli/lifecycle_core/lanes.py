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

WHAT THIS BUILD DOES NOT DO. The lane BODY's other three parsed parts
(`Decides:`, the decision table, `Ends:`) are wave 2's, and so is the
one-screen cap. This module parses `Trigger:` — what the router needs — and
says so in its own output rather than implying it read the whole lane.
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
    #: Which of §3.3's four parts the body carries. Reported rather than
    #: enforced: the one-screen cap and the decision table are wave 2's.
    parts_present: list = field(default_factory=list)
    problem: str | None = None


def read_lane(repo: Path, name: str) -> Lane:
    """Load one lane body and pull its `Trigger:` line out of it.

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
    lane = Lane(name, path, trigger=trig, parts_present=present)
    if trig is None:
        lane.problem = (f"lane {name!r} carries no `Trigger:` line. §3.3 makes "
                        "the trigger one of the four parsed parts; without it "
                        "the lane has no state to report.")
    return lane


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

    DOES NOT TOUCH THE DECLARATION. Writing the lane BODY and DECLARING it
    (adding its name to the repo's `lanes` list) are two separate acts —
    this verb performs only the first, and says so. CHECKED, NOT ASSUMED:
    `lane list` walks the declaration's OWN `lanes` list — a file this door
    is not declared under is not merely flagged, it is INVISIBLE to the
    router, which has no directory scan of its own. So THIS verb's own
    output is the one place the author learns "UNREGISTERED" from; `lane
    list` will say nothing about this door at all until it is declared.
    (No verb in this build currently adds a lane name to an EXISTING
    declaration's `lanes` list after `init` time — `lane register` puts a
    REPO on the router's roster, a different mechanism entirely; that gap
    is not this verb's to close.)

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

    res = decl.read(repo)
    declared = list((res.declaration or {}).get("lanes") or []) \
        if res.declaration else []
    if door in declared:
        out(f"declared: {door!r} is already in this repo's `lanes` list.")
    else:
        out(f"UNREGISTERED: {door!r} is not yet in this repo's declared "
            "`lanes` list. Writing the file and declaring it are two acts — "
            "this verb performs only the first. `lane list` walks the "
            "declaration's own list, so it will say NOTHING about this "
            "door — not even a finding — until its name is added there; "
            "learn this from this tool's own output now, not from the "
            "router's silence later.")
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
            if lane.problem:
                run.broken += 1
                codes.append(exits.FINDING)
                rr.lane_runs.append(LaneRunResult(
                    name=name, parts_present=lane.parts_present,
                    trigger=lane.trigger, problem=lane.problem,
                    row="trigger_broken"))
                continue
            if args.no_run:
                codes.append(exits.COULD_NOT_VERIFY)
                rr.lane_runs.append(LaneRunResult(
                    name=name, parts_present=lane.parts_present,
                    trigger=lane.trigger, not_run=True))
                continue
            t = evaluate_trigger(lane.trigger, cwd=row.path)
            lr = LaneRunResult(name=name, parts_present=lane.parts_present,
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
        f"QUIET {run.quiet}   BROKEN {run.broken}")
    out("this build parses `Trigger:` only; `Decides:`, the decision table "
        "and `Ends:` are reported by PRESENCE and are parsed in wave 2. The "
        "one-screen cap is wave 2's too — this run does not check it and does "
        "not imply it did.")
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
                "trigger": lr.trigger,
            }
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
