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
    row.decl_notes = ([f"FINDING [{f.row}] {f.message}" for f in res.findings]
                      + [f"COULD NOT VERIFY: {u}" for u in res.unverified])
    if res.declaration is None:
        row.resolution = "RESOLVED, DECLARATION UNREADABLE"
        return row
    row.resolution = "RESOLVED"
    lanes = res.declaration.get("lanes")
    row.lanes = list(lanes) if isinstance(lanes, list) else []
    return row


# --- `lane list` -------------------------------------------------------------

def cmd_lane_list(args, out) -> int:
    """The generated router. LONGHAND, and it exits under the VERB contract.

    Every state below is printed, including the zeros: a repo with no
    declared lanes says so in a line of its own, because "0 lanes" and "this
    repo was skipped" are different facts and only one of them is clean.
    """
    path = roster_path()
    entries, why = read_roster(path)
    if entries is None:
        out(f"FINDING [roster_absent] {why}")
        out(f"roster: {path}")
        out("lane list: FINDING — the router could not be generated. This is "
            "a FINDING and not a could-not-verify: §3.3 names an absent "
            "roster BROKEN, which is a state of the system rather than a "
            "limit of this run.")
        return exits.FINDING

    out(f"roster: {path}")
    out(f"roster count: {len(entries)} repo(s) listed")
    out("")

    codes = [exits.CLEAN]
    total_lanes = 0
    fired = quiet = broken = 0
    for raw in entries:
        row = resolve_repo_row(raw)
        out(f"repo: {raw}")
        out(f"    resolution: {row.resolution}")
        if row.resolution.startswith("UNRESOLVED"):
            out("    FINDING [repo_unresolved] the roster lists this repo and "
                "it does not resolve. A router that dropped the line would "
                "print a shorter board rather than a broken one.")
            codes.append(exits.FINDING)
            out("")
            continue

        out(f"    declaration: {exits.word(row.decl_code)}")
        for note in row.decl_notes:
            out(f"        {note}")
        codes.append(row.decl_code)
        if row.declaration is None:
            out("")
            continue

        policy = row.declaration.get("trigger-policy")
        out(f"    trigger-policy: {policy}")
        out(f"    declared lanes: {len(row.lanes)}"
            + (f" — {', '.join(row.lanes)}" if row.lanes else
               " — EMPTY, declared rather than absent (§3.0: an empty "
               "declared list is a stated fact)"))

        for name in row.lanes:
            total_lanes += 1
            lane = read_lane(row.path, name)
            if lane.problem:
                out(f"    lane {name}: BROKEN — {lane.problem}")
                out("        FINDING [trigger_broken] a lane whose body or "
                    "trigger cannot be read has no state, and no state is "
                    "not quiet.")
                broken += 1
                codes.append(exits.FINDING)
                continue
            out(f"    lane {name}: parts present "
                f"{', '.join(lane.parts_present) or '(none)'}")
            out(f"        trigger: {lane.trigger}")
            if args.no_run:
                out("        NOT RUN (--no-run): the state below would be the "
                    "predicate's, and this run did not ask it. Not quiet.")
                codes.append(exits.COULD_NOT_VERIFY)
                continue
            t = evaluate_trigger(lane.trigger, cwd=row.path)
            out(f"        state: {t.state}   predicate exit: {t.code}")
            if t.detail:
                out(f"        detail: {t.detail}")
            if t.state == BROKEN:
                out("        FINDING [trigger_broken] the predicate's exit is "
                    ">=2, which §3.3 RESERVES for BROKEN. Reported as a "
                    "finding rather than folded into quiet: a dead lane that "
                    "renders quiet is a clean board over a router that does "
                    "not work.")
                broken += 1
                codes.append(exits.FINDING)
            elif t.state == FIRE:
                fired += 1
            else:
                quiet += 1
        out("")

    out(f"lanes: {total_lanes} total   FIRE {fired}   QUIET {quiet}   "
        f"BROKEN {broken}")
    out("this build parses `Trigger:` only; `Decides:`, the decision table "
        "and `Ends:` are reported by PRESENCE and are parsed in wave 2. The "
        "one-screen cap is wave 2's too — this run does not check it and does "
        "not imply it did.")
    code = exits.worst(codes)
    out(f"lane list: {exits.word(code)}")
    return code
