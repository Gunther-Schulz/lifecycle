"""`lifecycle retire`, `lifecycle audit`, `lifecycle kind sweep`.

THE WALK IS ONE BODY WITH TWO VERBS OVER IT (design §3.11). `retire` is the
lifecycle walk over every registered kind; `audit` is the SAME walk run
read-only on demand, reporting instead of acting. Two bodies behind one
contract would disagree about the case that matters — a kind whose exit did
nothing — and that is the case that decides whether a board reads clean.

IT RE-LISTS EVERY HOME ON EVERY PASS, never a cached index (§3.0). A cached
index of what a kind holds is Terraform's state-file-versus-reality defect and
this repo's own `quota_pressure` stock-versus-flow defect, one level up: the
index says what the last pass saw and the world says what is there, and the
walk exists to catch exactly the difference.

GROWTH IS FLOW, NEVER SIZE (R22). The finding is not "this kind is large" —
it is a kind that GREW WITHOUT AN EXIT EVENT. A large kind draining steadily
is fine and a small one that never drains is not, so no count appears in a
predicate here; counts are printed because a reader wants them, and they
decide nothing.

WHAT IS NOT CHECKED SAYS SO. Most declared exits are not acts this WALK
reads — `never` and `delete` have no verb at all — so their kinds are
reported NOT CHECKED with the reason rather than folded into a clean line. A
walk that reported nine clean kinds while only checking one would be the
assurance wider than its predicate that this whole arc keeps finding.
`compact` LEFT that list with lc-145: the verb exists, it writes a fire-log
line like any other, and a walk that went on answering NOT CHECKED for the
kinds it serves was reporting the absence of a reader that was there.
"""

import os
import re
from pathlib import Path

from . import atomic, exits, firelog, judgment
from . import declaration as decl
from . import grammar
from . import items as items_mod

#: The staleness placeholder §3.11 rule 1 states, with its own status. THREE
#: passes is a number nobody has measured; the first full walk replaces it,
#: and until then it is printed as a placeholder rather than as a threshold.
STALE_PASSES_N = 3
STALE_PASSES_STATUS = ("PLACEHOLDER — §3.11 rule 1 says so in the design's own "
                       "words; the first full walk replaces it with a number "
                       "the passes produced")

#: The exit actions this build actually PERFORMS and records. A kind whose
#: exit is anything else has no event to look for, and saying that is a
#: different answer from saying its exit never fired.
#:
#: `compact` JOINED ON lc-145, because the verb joined the build: `item
#: compact` performs and records that exit, so leaving it out here answered
#: NOT CHECKED about a reader this build has.
PERFORMED_EXITS = ("move", "compact")

#: THE GROWTH MODES WHOSE CONTROL IS AN EXIT EVENT (lc-145), derived from the
#: declaration's own closed list rather than restated beside it — a mode added
#: there is asked the question by default, and a silent exemption is exactly
#: what this repo's R22 alarm cannot afford.
#:
#: `unbounded-with-reason` is the ONE declared opt-out: that mode says outright
#: that growth is controlled by something other than an exit, and it carries
#: its reason. `compacted` is not an opt-out — it names compaction AS the
#: control — so a compacted kind whose compaction has never fired is precisely
#: the kind R22 means. Before lc-145 the gate below read `bounded-by-exit`
#: alone, so every compacted kind was exempt from the alarm it had declared.
UNCONTROLLED_GROWTH_MODE = "unbounded-with-reason"
EXIT_CONTROLLED_MODES = tuple(m for m in decl.GROWTH_MODES
                              if m != UNCONTROLLED_GROWTH_MODE)

#: Which fire-log verb records each performed exit. Read from the design's
#: own recording-act rather than guessed: `items`' declared recording act IS
#: the `item close` fire-log line, and `done bodies`' is the `item compact`
#: one.
#: KEYED ON (KIND, ACTION), never on the action alone (FF-3). `arcs` and
#: `items` both declare their exit action as `move`, so an action-keyed map
#: has two wrong answers available and no right one: leave it and an `arc
#: close` is invisible, so the arcs kind reads GREW WITHOUT AN EXIT while its
#: exit has been firing; add `arc close` beside `item close` and an arc
#: closure now satisfies the ITEMS alarm, which then goes quiet on a carrier
#: that genuinely stopped draining. The collision is stated here so a builder
#: adding the next kind cannot inherit it.
EXIT_VERBS = {
    ("items", "move"): ("item close",),
    ("arcs", "move"): ("arc close",),
    ("done bodies", "compact"): ("item compact",),
    ("closed arcs", "compact"): ("arc compact",),
}


# --- the fire log, read back --------------------------------------------------

def read_fire_log(repo: Path | None = None) -> list:
    """Every fire-log record, optionally narrowed to one repo.

    THREE ANSWERS: an unreadable or absent log returns an empty list AND the
    caller is told, because "no exit events" and "no log to read" are the two
    answers a growth alarm must never share — the first fires the alarm and
    the second says nothing at all.
    """
    path = firelog.log_path()
    if not path.is_file():
        return []
    out = []
    try:
        import json
        for line in path.read_text(encoding="utf-8").split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if not isinstance(rec, dict):
                continue
            if repo is not None and rec.get("repo") != str(repo):
                continue
            out.append(rec)
    except (OSError, UnicodeDecodeError):
        return []
    return out


def fire_log_readable() -> bool:
    path = firelog.log_path()
    if not path.is_file():
        return False
    try:
        path.read_text(encoding="utf-8")
        return True
    except (OSError, UnicodeDecodeError):
        return False


# --- listing a kind's real home ----------------------------------------------

#: A home still carrying a shell-style variable AFTER `expand_home` has run
#: (lc-170). Before that it meant "this walk does not expand variables",
#: which stopped being true in the same change — the docstring is corrected
#: with the behaviour rather than left recounting the old one (law 26). What
#: reaches this now is a variable that is unset AND has no spec default, so
#: the home was never resolved and anything counted under it would be a count
#: of nothing rather than a count of zero.
_UNEXPANDED = re.compile(r"\$\w|\$\{")


def unresolvable_line(note: str) -> str:
    """The walk's answer for a home it could not examine, as ONE body.

    The walk prints it and the roster row that proves it builds it, so the
    ident and the sentence cannot drift apart into two spellings of one
    refusal.
    """
    return f"COULD NOT VERIFY [home_unresolvable] {note}"


#: The XDG base directories this walk knows how to default, and NOTHING ELSE
#: (lc-170). Each maps to the spec's own fallback, derived from the running
#: user's home at call time — law 6 forbids a hardcoded machine path or XDG
#: root in this tree, and `records.records_dir` already resolves one variable
#: exactly this way. This is that idiom generalised rather than a second
#: spelling of it.
#:
#: A VARIABLE NOT IN THIS TABLE AND NOT IN THE ENVIRONMENT STAYS UNRESOLVED,
#: which keeps `home_unresolvable` reachable: guessing a default for an
#: arbitrary name would turn "I could not see this population" into a
#: confident reading of the wrong directory, which is the failure lc-172
#: removed rather than one to reintroduce one layer down.
_XDG_DEFAULTS = {
    "XDG_STATE_HOME": (".local", "state"),
    "XDG_DATA_HOME": (".local", "share"),
    "XDG_CONFIG_HOME": (".config",),
    "XDG_CACHE_HOME": (".cache",),
}

_VAR = re.compile(r"\$\{(\w+)\}|\$(\w+)")


def expand_home(home: str) -> str:
    """`home` with environment and XDG-default substitutions applied.

    WHY THE WALK RESOLVES THESE AT ALL (lc-170). lc-172 made an unexpanded
    home answer COULD NOT VERIFY instead of reporting CLEAN over a population
    nothing had examined — the honest answer, and still the wrong END STATE:
    every XDG-homed kind then sits permanently outside R22's alarm, saying so
    loudly instead of quietly. The fire log is the case that proves it
    matters, and `kind sweep` cannot cover these kinds either, since it walks
    TRACKED files and these live outside every tree by design.

    Unresolved variables are LEFT STANDING rather than dropped, so the caller
    can still tell an unresolvable home from a resolved one.
    """
    def sub(m):
        name = m.group(1) or m.group(2)
        val = os.environ.get(name)
        if val:
            return val
        parts = _XDG_DEFAULTS.get(name)
        if parts:
            return str(Path.home().joinpath(*parts))
        return m.group(0)
    return os.path.expanduser(_VAR.sub(sub, home))


def _shown(path: Path, repo: Path) -> str:
    """A path as a reader should see it: repo-relative in the tree, else its
    own absolute spelling. A `relative_to` over an out-of-tree home raises,
    and an out-of-tree home is exactly what lc-170 made reachable."""
    try:
        return str(path.relative_to(repo))
    except ValueError:
        return str(path)


def list_home(repo: Path, home: str) -> tuple:
    """`(instances, note)` for one kind's declared home, RE-LISTED now.

    Three home shapes, each counted by what an INSTANCE of that kind is:
    a carrier file counts its fixed-slot blocks, a glob counts its files, a
    plain file counts as one. The note says which notion was used, because a
    number without its notion is the figure two readers disagree about.
    """
    # lc-172: AN ABSENCE CLAIM NAMES WHAT PROVES ITS INSTRUMENT WAS LIVE, and
    # the three returns below are where this walk's instrument can be dead.
    # An unexamined home yields an empty list, an empty home yields an empty
    # list, and until now both printed "the home holds nothing, so nothing has
    # grown" — CLEAN. MEASURED 2026-09-18: the fire log's declared home is
    # `$XDG_STATE_HOME/lifecycle/fire.jsonl`, this walk does not expand the
    # variable, so it looked for a literal `$XDG_STATE_HOME/…`, found nothing,
    # counted 0 and reported the kind CLEAN — while the file held 133,087,757
    # bytes across 1,173,626 lines. The alarm R22 specifies was unreachable
    # for every XDG-homed kind, silently, and the sentence saying so was the
    # most reassuring line in the output.
    #
    # `None` is COULD NOT VERIFY here — both callers already route it that way
    # — so the repair is to answer it wherever the population was never seen.
    # RESOLVED FIRST (lc-170), then judged. What survives expansion with a
    # `$` still in it is genuinely unresolvable — an unknown variable, unset
    # and with no spec default — and THAT is the dead instrument lc-172
    # named. A home this walk can resolve is a home it must examine, or the
    # XDG-homed kinds stay outside R22's alarm while saying so politely.
    resolved = expand_home(home)
    if _UNEXPANDED.search(resolved):
        return None, (f"{home!r} carries a variable this walk cannot resolve "
                      f"(unset, and not one of "
                      f"{', '.join(sorted(_XDG_DEFAULTS))}), so NOTHING was "
                      "examined. A count of 0 here would be an absence claim "
                      "over a population no instrument ever saw.")
    if "*" in resolved:
        stem = resolved.split("*", 1)[0]
        base = repo / (stem if stem.endswith("/") else str(Path(stem).parent))
        if not base.is_dir():
            # IN-TREE AND ABSENT IS AN OBSERVATION, not a dead instrument:
            # the walk resolved the path in this repo's terms and the
            # directory is not there, which is a fact about the repo. The
            # denominator says so, so a reader can tell this zero from one
            # measured over files that exist.
            return [], (f"glob {home!r}: 0 instance(s) — the directory "
                        f"{(_shown(base, repo) if base != repo else '.')!r} "
                        "does not exist, so there was nothing to "
                        "match rather than nothing matching.")
        hits = sorted(base.glob(resolved.split(str(base), 1)[-1].lstrip("/"))
                      if Path(resolved).is_absolute() else repo.glob(resolved))
        return [_shown(p, repo) for p in hits if p.is_file()], \
            f"glob {home!r}: one instance per file, searched under {stem or './'}"
    path = repo / resolved
    if not path.exists():
        # DELIBERATELY NOT COULD-NOT-VERIFY, and the boundary is lc-172's own:
        # the discriminator is whether the instrument SAW anything, never
        # whether it FOUND anything. An in-tree home is resolvable, so its
        # absence is data about the repo — the walk looked and there is no
        # file. Only an UNRESOLVABLE home (above) is the dead instrument, and
        # that is the case the fire log measured. An earlier item pins this
        # branch CLEAN as MUST-NOT-MOVE, and applying lc-172 to both cases
        # would have moved it on a reading its own incident does not support.
        return [], (f"{home!r} is not present: 0 instance(s), and the path "
                    "WAS resolved — an absent in-tree home is an observation, "
                    "not an unexamined population.")
    if path.is_dir():
        hits = sorted(p for p in path.rglob("*") if p.is_file())
        return [_shown(p, repo) for p in hits], \
            f"directory {home!r}: one instance per file"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"{home!r} could not be read ({exc!r})"
    if f"\n{grammar.HEADING_PREFIX}" in text or grammar.starts_section(text):
        parsed = items_mod.parse(text)
        return [it.ident for it in parsed.items], \
            f"carrier {home!r}: one instance per fixed-slot block"
    return [home], f"{home!r}: a single file, one instance"


# --- the growth question, on its own ------------------------------------------

def check_growth(name, mode, action, count, log, log_present, out):
    """`(code, state)` for ONE kind's growth. FLOW, never size.

    ITS OWN FUNCTION because the walk's overall answer is COULD NOT VERIFY by
    construction — the per-kind staleness predicate needs pass history and
    this is the first walk — and folding a real FINDING into that would leave
    the one alarm R22 actually specifies unreachable to a caller reading exit
    codes. The walk calls this; so does the roster row that proves it.

    Only a kind whose exit this build actually PERFORMS can be asked whether
    its exit fired. The rest are NOT CHECKED with the reason, which is a
    different answer from "its exit never fired" and must not share a line
    with it.
    """
    if mode not in EXIT_CONTROLLED_MODES:
        out(f"    growth check: NOT APPLICABLE — `{mode or 'undeclared'}` is "
            "not controlled by an exit event "
            f"({', '.join(EXIT_CONTROLLED_MODES)}), so 'grew without an exit "
            "event' is not the alarm this kind declared.")
        return exits.CLEAN, "n/a"
    if action not in PERFORMED_EXITS:
        out(f"    growth check: NOT CHECKED — the declared exit action "
            f"`{action}` is not one this build performs "
            f"({', '.join(PERFORMED_EXITS)}), so there is no recorded event to "
            "look for. NOT the same answer as 'its exit never fired'.")
        return exits.COULD_NOT_VERIFY, "unchecked"
    if not log_present:
        out("    growth check: COULD NOT VERIFY — no fire log, so no exit "
            "event could be seen. An unread log contributes zero events, and "
            "zero events is exactly what fires this alarm.")
        return exits.COULD_NOT_VERIFY, "unchecked"
    verbs_ = EXIT_VERBS.get((name, action))
    if verbs_ is None:
        # A KIND NOBODY MAPPED IS ITS OWN ANSWER, not zero events. Zero
        # events is what FIRES this alarm, so folding an unmapped kind into
        # it would report "grew without an exit" about a kind whose exit this
        # build simply does not know how to look for — a verdict over a
        # question never asked. Two kinds are in exactly that state today
        # (`design notes` and `the fire log`), whose recording acts are prose
        # graduations rather than verbs, and the honest answer for them is
        # that nothing here can see their exit fire.
        out(f"    growth check: COULD NOT VERIFY — no exit verb is mapped "
            f"for kind {name!r} at action `{action}`, so there is no event "
            "to look for. NOT the same answer as 'its exit never fired': "
            "that one is a finding about the kind, this one is a gap in "
            "this map.")
        return exits.COULD_NOT_VERIFY, "unchecked"
    events = [r for r in log if str(r.get("verb", "")) in verbs_]
    out(f"    exit events: {len(events)} ({', '.join(verbs_)}) recorded for "
        "this repo")
    if count and not events:
        # THE DECLARED MODE, READ rather than restated: this message named
        # `bounded-by-exit` while the gate above admitted one mode, and the
        # day the gate widened the sentence started lying about the very kind
        # it was firing on (lc-145).
        out(f"    FINDING [kind_grew_without_exit] kind {name!r} holds "
            f"{count} instance(s), declares `{mode}`, and its exit "
            "has recorded NOTHING. The alarm is FLOW: the count above is not "
            "the finding and no size would be — a large kind draining "
            "steadily is fine and this one is not draining at all. A recorded "
            "DROP clears this exactly as a completion does.")
        return exits.FINDING, "grew"
    if not count:
        # NOT THE SAME CLEAN. A kind whose home holds nothing has not grown,
        # and saying "the exit has fired" about it asserts an event that never
        # happened — the verdict is the same and the sentence is not.
        out("    growth check: CLEAN — the home WAS examined and holds 0 "
            "instance(s), so nothing has grown. NOT the same answer as 'the "
            "exit has fired', and not the same as a home this walk could not "
            "read — that one is COULD NOT VERIFY and says what it could not "
            "see (lc-172).")
        return exits.CLEAN, "clean"
    out(f"    growth check: CLEAN — the exit has fired for this kind: "
        f"{len(events)} recorded event(s) over {count} instance(s). Both "
        "numbers are the denominator this verdict rests on: an exit that "
        "fired is a FLOW, and zero events over any count is the alarm.")
    return exits.CLEAN, "clean"


def growth_verdict(repo: Path, doc: dict, out) -> int:
    """Every registered kind's growth question, and NOTHING else.

    The row that proves `kind_grew_without_exit` calls this rather than the
    whole walk: the walk answers COULD NOT VERIFY for the staleness half by
    construction, and a pair whose plant and control both exit 3 discriminates
    nothing.
    """
    kinds = doc.get("kinds")
    if not isinstance(kinds, dict) or not kinds:
        out("COULD NOT VERIFY: the declaration registers no kinds.")
        return exits.COULD_NOT_VERIFY
    log = read_fire_log(repo)
    log_present = fire_log_readable()
    code = exits.CLEAN
    for name, body in kinds.items():
        if not isinstance(body, dict):
            continue
        home = body.get("home")
        growth = str(body.get("growth") or "")
        mode = growth.split()[0].strip(":,—-").lower() if growth.strip() else ""
        ex = body.get("exit") if isinstance(body.get("exit"), dict) else {}
        if not isinstance(home, str) or not home.strip():
            continue
        instances, _note = list_home(repo, home)
        if instances is None:
            continue
        out(f"kind: {name}")
        g_code, _state = check_growth(name, mode, ex.get("action"),
                                      len(instances), log, log_present, out)
        code = exits.worst([code, g_code])
    return code


# --- the walk ----------------------------------------------------------------

def walk(repo: Path, doc: dict, out, *, acting: bool) -> int:
    """Every registered kind: its real home re-listed, its growth, its exit."""
    kinds = doc.get("kinds")
    if not isinstance(kinds, dict) or not kinds:
        out("FINDING [unregistered_kind] the declaration registers no kinds, "
            "so the walk has nothing to walk. A repo that persists something "
            "registers it.")
        return exits.FINDING

    log = read_fire_log(repo)
    log_present = fire_log_readable()
    code = exits.CLEAN
    grew = []
    unchecked = []

    out(f"the lifecycle walk over {len(kinds)} registered kind(s) — homes "
        "RE-LISTED on this pass, never read from a cached index.")
    out(f"exit events read from the fire log: "
        + (f"{len(log)} record(s) for this repo" if log_present else
           "NO FIRE LOG PRESENT — this is COULD NOT VERIFY for every "
           "exit question below, never zero events"))
    out("")

    for name, body in kinds.items():
        if not isinstance(body, dict):
            out(f"kind: {name}")
            out("    COULD NOT VERIFY: the registry row is not an object.")
            code = exits.worst([code, exits.COULD_NOT_VERIFY])
            continue
        home = body.get("home")
        growth = str(body.get("growth") or "")
        mode = growth.split()[0].strip(":,—-").lower() if growth.strip() else ""
        ex = body.get("exit") if isinstance(body.get("exit"), dict) else {}
        action = ex.get("action")

        out(f"kind: {name}")
        out(f"    home:   {home}")
        out(f"    growth: {mode or '(undeclared)'}")
        out(f"    exit:   {action or '(undeclared)'} — "
            f"{ex.get('recording-act', '(no recording act)')}")

        if not isinstance(home, str) or not home.strip():
            out("    COULD NOT VERIFY: no home declared, so nothing could be "
                "listed. An undeclared home is a `kind check` finding; here "
                "it is simply unlistable.")
            code = exits.worst([code, exits.COULD_NOT_VERIFY])
            out("")
            continue

        instances, note = list_home(repo, home)
        if instances is None:
            out("    " + unresolvable_line(note))
            code = exits.worst([code, exits.COULD_NOT_VERIFY])
            out("")
            continue
        out(f"    count:  {len(instances)}   ({note})")

        # THE GROWTH QUESTION, and it is a FLOW question.
        g_code, g_state = check_growth(name, mode, action, len(instances),
                                       log, log_present, out)
        if g_state == "grew":
            grew.append(name)
        elif g_state == "unchecked":
            unchecked.append(name)
        code = exits.worst([code, g_code])

        # STALENESS (§3.11 rule 1) is REPORTED with its predicate, and the
        # placeholder N says it is a placeholder in its own output.
        stale = str(body.get("staleness") or "")
        out(f"    staleness: {stale[:160]}")
        if stale.strip().lower().startswith("none"):
            out("    staleness check: NOT APPLICABLE — declared none, with "
                "its reason.")
        else:
            out(f"    staleness check: NOT RUN — the per-kind predicate needs "
                f"pass history (N = {STALE_PASSES_N}, {STALE_PASSES_STATUS}), "
                "and this is the first walk. Reported rather than answered: a "
                "staleness check with no history returns 'nothing is stale' "
                "over every repo, which is a number shaped like a pass.")
            code = exits.worst([code, exits.COULD_NOT_VERIFY])
        out("")

    if acting:
        out("EXITS TAKEN THIS PASS: none. `retire` in this build WALKS and "
            "REPORTS; the acts its findings call for — compaction, the "
            "recorded drop — are their own verbs and each records itself. A "
            "walk that took an exit it could not record would be the "
            "unrecorded deletion this carrier exists to prevent.")
        out("")

    out(f"walk: {len(kinds)} kind(s); grew-without-exit {len(grew)}"
        + (f" ({', '.join(grew)})" if grew else "")
        + f"; growth unchecked {len(unchecked)}"
        + (f" ({', '.join(unchecked)})" if unchecked else ""))
    # THE NO-YIELD DISPOSITION, WRITTEN WHERE ITS ACTOR READS (lc-243 W1).
    # The disposition named an actor (the session running this pass) and an
    # event (this pass firing) and lived in a closed item's done-criterion,
    # which that session never opens — a named reader who never loads the
    # carrier makes the naming decorative, and a line nobody grades
    # accumulates instead of failing. So the obligation is printed by the
    # pass itself, at the moment the actor is standing in it.
    out("")
    out("ALSO OWED BY THIS PASS: grade the standing flag lines on their "
        "CATCHES since the last pass, and record the grading in the pass's "
        "ledger note — `moments:` (lc-243 W1 act 2) and `perishable "
        "evidence:` (lc-244 W2) are the two today. A line that has caught "
        "nothing across several passes is a line to retire, and no-yield is "
        "a verdict this pass OWNS rather than a fact anyone notices: "
        "nothing else reads a quiet flag line. A line added later joins "
        "this list by being named here, which is the only place the pass "
        "looks.")
    return code


# --- `kind sweep` — the unregistered-file half of invariant 1 ----------------

#: Directories a sweep never descends into: git's own store, caches, and the
#: node/python build detritus. Named rather than pattern-guessed, because a
#: sweep that skipped something by accident would report a clean board over
#: exactly the file nobody registered.
SWEEP_SKIP_DIRS = (".git", "node_modules", "__pycache__", ".pytest_cache",
                   ".mypy_cache", ".ruff_cache", "dist", "build")


def sweep(repo: Path, doc: dict, out) -> int:
    """Every TRACKED file resolves to a registered kind, or it is a finding.

    INVARIANT 1, and it is the half `kind check` cannot reach: that verb
    validates the registry, this one asks the world whether anything is
    sitting outside it. The two together are what makes "nothing stray
    re-accumulates unnoticed" a mechanism rather than a habit.

    TRACKED, deliberately. An untracked file is this machine's business and
    reaches no clone; a tracked one is what every reader gets. Running over
    the working tree instead would fire on scratch, editor state and every
    build artifact — the guard firing on legitimate work that trains the
    override reflex.
    """
    import subprocess
    kinds = doc.get("kinds") if isinstance(doc.get("kinds"), dict) else {}
    homes = []
    for name, body in kinds.items():
        home = body.get("home") if isinstance(body, dict) else None
        if isinstance(home, str) and home.strip():
            homes.append((name, home.strip()))

    try:
        p = subprocess.run(["git", "-C", str(repo), "ls-files"],
                           capture_output=True, text=True)
    except (OSError, subprocess.SubprocessError) as exc:
        out(f"COULD NOT VERIFY: git could not list the tracked files "
            f"({exc!r}), so nothing was swept. An empty sweep reads exactly "
            "like a repo with nothing stray in it.")
        return exits.COULD_NOT_VERIFY
    if p.returncode != 0:
        out(f"COULD NOT VERIFY: `git ls-files` exited {p.returncode}: "
            f"{p.stderr.strip()[:200]!r}")
        return exits.COULD_NOT_VERIFY

    tracked = [f for f in p.stdout.split("\n") if f.strip()]
    tracked = [f for f in tracked
               if not any(part in SWEEP_SKIP_DIRS for part in Path(f).parts)]
    # THE REGISTRY ITSELF IS NOT SWEPT. `.claude/lifecycle.json` is the list
    # every other file is checked against; demanding that it register itself
    # is a self-reference that catches nothing — the file's absence is already
    # `declaration_absent` and its shape is already `kind check`'s.
    registry_rel = str(decl.DECLARATION_REL)
    tracked = [f for f in tracked if f != registry_rel]

    out(f"kind sweep — invariant 1, over {len(tracked)} TRACKED file(s) "
        f"against {len(homes)} registered home(s).")
    out("Tracked rather than the working tree: an untracked file reaches no "
        "clone, and sweeping the tree would fire on scratch and build output "
        "— a guard firing on legitimate work.")
    out("")
    for name, home in homes:
        out(f"    home: {home:<28} kind: {name}")
    out("")

    unregistered = []
    for f in tracked:
        if not any(_home_claims(home, f) for _n, home in homes):
            unregistered.append(f)

    if not unregistered:
        out(f"sweep: CLEAN — all {len(tracked)} tracked file(s) resolve to a "
            "registered kind.")
        return exits.CLEAN

    out(f"FINDING [unregistered_persisted_thing] {len(unregistered)} tracked "
        f"file(s) resolve to no registered kind:")
    for f in unregistered:
        out(f"    {f}")
    out("")
    out("Each is one of three things and no fourth (design §4, the file "
        "sweep): an instance of an existing registered kind whose home does "
        "not yet claim it; a REPO-SPECIFIC kind that belongs in "
        "`.claude/lifecycle.json` with its own seven stages; or removed, with a "
        "ledger line naming the commit. A file whose NAME wears a kind's "
        "costume is the tell.")
    return exits.FINDING


def _home_claims(home: str, rel: str) -> bool:
    """Does a declared home cover this repo-relative path?

    Anchored on PATH SEGMENTS, never on a substring: `docs/audits/*.md` and
    `docs/audits-old/x.md` share a prefix, and a substring test would claim
    the second — a prefix match in an equality's costume.
    """
    # `removeprefix`, NEVER `lstrip("./")`. `lstrip` takes a CHARACTER SET, so
    # it eats the leading dot of every dotfile: `.gitignore` became
    # `gitignore` and a home that named it exactly compared unequal — a
    # registered file reported as unregistered, which is a guard firing on
    # legitimate work. Measured on this repo's own sweep.
    home = home.strip().removeprefix("./")
    rel = rel.strip().removeprefix("./")
    if "*" in home:
        return Path(rel).match(home)
    if home == rel:
        return True
    home_parts = Path(home).parts
    rel_parts = Path(rel).parts
    return len(rel_parts) > len(home_parts) and \
        rel_parts[:len(home_parts)] == home_parts


# --- the laws scope audit (design §3.3; replaces the 60-line cap) ------------

#: The four markers §3.3 names, each belonging to another KIND. A line
#: carrying one is POSSIBLY mis-homed — the word is load-bearing, because the
#: same markers appear legitimately inside a law's one-line basis pointer, and
#: hardening "possibly mis-homed" into "mis-homed" is what would turn this
#: review into a refusal.
MARKERS = (
    ("workflow", re.compile(r"^\s*(?:\d+\.|[a-z]\))\s+\S"),
     "a numbered step sequence belongs in a WORKFLOW"),
    ("journal", re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
     "a dated incident belongs in the JOURNAL"),
    ("audit", re.compile(
        r"\b\d[\d,._]*\s?(?:lines?|entries|entry|files?|sessions?|rows?|"
        r"seconds?|ms|s\b|MiB|GiB|%|calls?|tokens?)\b"),
     "a measured figure with a unit belongs in an AUDIT"),
    ("journal-citation", re.compile(
        r"[\w./-]+\.(?:py|mjs|cjs|js|md|json|jsonl|sh|ya?ml|toml):\d+"),
     "a file:line citation wrapped in explanation belongs in the JOURNAL"),
)

_NUMBERED = re.compile(r"^\s*(\d+)\.\s+\S")


def law_list_lines(lines) -> set:
    """The line numbers (1-based) of the file's LAW LIST and its bodies.

    DERIVED FROM THE FILE'S SHAPE, never from a heading's text. A heading is a
    label over a body that moves, and keying the audit to the words "## The
    LAWS" would make renaming the heading silently turn the whole file into
    findings. The law list is the longest run of top-level numbered items,
    together with the continuation lines each item owns — which is what makes
    a law's own one-line basis pointer exempt without naming it.
    """
    runs = []
    current = []
    last_n = 0
    for i, raw in enumerate(lines, start=1):
        m = _NUMBERED.match(raw)
        if m:
            n = int(m.group(1))
            if current and n == last_n + 1:
                current.append(i)
            else:
                if current:
                    runs.append(current)
                current = [i]
            last_n = n
            continue
        if current and (not raw.strip() or raw.startswith((" ", "\t"))):
            current.append(i)
            continue
        if current:
            runs.append(current)
            current = []
            last_n = 0
    if current:
        runs.append(current)
    if not runs:
        return set()
    longest = max(runs, key=lambda r: sum(
        1 for i in r if _NUMBERED.match(lines[i - 1])))
    if sum(1 for i in longest if _NUMBERED.match(lines[i - 1])) < 3:
        return set()
    return set(longest)


def laws_scope_audit(repo: Path, laws_rel: str, out) -> int:
    """The mechanism that REPLACED the 60-line cap (R22).

    THE CAP WAS WITHDRAWN, NOT MOVED. A laws file may need 200 lines and the
    only question is whether every line is a law — so the size is a NUMBER
    here, reported and deciding nothing, and the control is SCOPE.

    TWO HALVES, and the output says which is which. The computable slice
    flags lines carrying another kind's markers as POSSIBLY MIS-HOMED — a
    finding for review, never a refusal, since a law's own one-line basis
    pointer legitimately carries the same markers. The judgment remainder —
    IS this line a law — is the review's and is labelled PROSE-REST
    (invariant 9). "Possibly mis-homed" hardens into "mis-homed" the moment
    the output stops hedging, which is why the hedge is in the string and not
    in a reader's memory.
    """
    path = repo / laws_rel
    if not path.is_file():
        out(f"COULD NOT VERIFY: the declared laws file {laws_rel!r} is not in "
            "the working tree. An absent file and a well-scoped one are not "
            "the same answer.")
        return exits.COULD_NOT_VERIFY
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        out(f"COULD NOT VERIFY: {laws_rel!r} could not be read ({exc!r}).")
        return exits.COULD_NOT_VERIFY

    lines = text.split("\n")
    law_lines = law_list_lines(lines)
    hits = []
    for i, raw in enumerate(lines, start=1):
        if i in law_lines or not raw.strip():
            continue
        for name, pat, why in MARKERS:
            if pat.search(raw):
                hits.append((i, name, why, raw.strip()[:90]))
                break

    out(f"LAWS SCOPE AUDIT — {laws_rel}")
    out(f"    size: {len(lines)} lines. A NUMBER, not a cap (R22): the size "
        "is reported and decides nothing. The control is SCOPE — whether "
        "every line is a law — and a 200-line laws file every line of which "
        "is a law is correct.")
    out(f"    law list: {sum(1 for i in law_lines if _NUMBERED.match(lines[i - 1]))}"
        f" numbered law(s) across {len(law_lines)} line(s), derived from the "
        "file's own shape rather than from a heading — a heading is a label "
        "over a body that moves.")
    out("    markers looked for, each belonging to ANOTHER kind: "
        + "; ".join(f"{n} ({w})" for n, _p, w in MARKERS))

    if not hits:
        # lc-172: THE DENOMINATOR IS THE CLAIM'S EVIDENCE. "No line carries a
        # marker" and "this audit examined no lines" print the same sentence
        # and mean opposite things, so the examined population is named here
        # rather than left on an earlier line a reader may not reach.
        examined = sum(1 for i, raw in enumerate(lines, start=1)
                       if i not in law_lines and raw.strip())
        out(f"    scope: CLEAN — 0 of {examined} line(s) outside the law list "
            f"carry another kind's marker, over {len(MARKERS)} marker(s) "
            "looked for. Both numbers are the proof this audit was live: a "
            "zero over 0 examined lines is what a dead pattern returns.")
        out("    PROSE-REST: whether each line inside the law list IS a law "
            "is the review's judgment and no predicate here answers it "
            "(invariant 9). This run checked SCOPE MARKERS and says so rather "
            "than implying it graded the laws.")
        return exits.CLEAN

    out(f"    FINDING [laws_scope_audit] {len(hits)} line(s) outside the law "
        "list carry another kind's marker and are POSSIBLY MIS-HOMED. "
        "POSSIBLY: the same markers appear legitimately in a law's one-line "
        "basis pointer, so this is a finding for REVIEW and never a refusal. "
        "The hedge is the verdict — hardened into \"mis-homed\" it would be a "
        "claim this predicate does not establish.")
    by_marker: dict = {}
    for lineno, name, why, snippet in hits:
        by_marker.setdefault(name, []).append((lineno, snippet))
    for name, _pat, why in MARKERS:
        rows = by_marker.get(name)
        if not rows:
            out(f"        {name}: 0")
            continue
        out(f"        {name}: {len(rows)} — {why}")
        for lineno, snippet in rows:
            out(f"            {laws_rel}:{lineno}  {snippet}")
    out("    PROSE-REST: whether each flagged line is really mis-homed, and "
        "whether each line inside the law list IS a law, are the review's "
        "judgment. No predicate here answers either (invariant 9).")
    return exits.FINDING


# --- the verbs ---------------------------------------------------------------

def cmd_retire(args, out, repo: Path, doc: dict) -> int:
    out("lifecycle retire — the lifecycle walk over every registered kind.")
    out("")
    return walk(repo, doc, out, acting=True)


def cmd_audit(args, out, repo: Path, doc: dict) -> int:
    """The retire lane's walk, run READ-ONLY on demand — one screen per repo."""
    out(f"lifecycle audit — {repo}")
    out("The retire lane's walk, read-only. Same body, same findings; this "
        "one reports where `retire` acts.")
    out("")
    code = walk(repo, doc, out, acting=False)

    laws = doc.get("laws")
    out("")
    if isinstance(laws, str) and laws.strip():
        code = exits.worst([code, laws_scope_audit(repo, laws, out)])
    else:
        out("COULD NOT VERIFY: the declaration names no laws file, so the "
            "scope audit had nothing to read.")
        code = exits.worst([code, exits.COULD_NOT_VERIFY])

    code = exits.worst([code, judgment.report(out, read_fire_log())])

    out("")
    out(f"lifecycle audit: {exits.word(code)}")
    return code


def cmd_kind_sweep(args, out, repo: Path, doc: dict) -> int:
    code = sweep(repo, doc, out)
    out(f"kind sweep: {exits.word(code)}")
    return code


# --- `item compact` — the done body's declared exit (lc-58 + lc-47) ----------
#
# THE LAST ARROW OF AN ITEM'S LIFE. `.claude/lifecycle.json` registers a kind
# `done bodies` whose exit action is `compact` and whose growth control is
# `compacted`; until this verb existed the arrow was unreachable and the
# carrier's conservation line could only ever read `compacted 0` — a number
# nothing could ever move, which is a count shaped like a control.
#
# WHERE THE RECORD LIVES, and the two answers this is NOT (lc-47). The entry
# offered LIFT (put the closure lines in the record) or EXEMPT (spare bodies
# carrying them); measured over the real done home, EXEMPT spares every body
# holding the mass and LIFT only relocates ~60k characters into a ledger read
# chronologically. So neither: the body leaves the carrier and stays
# recoverable at a BLOB PIN, which shrinks the carrier and moves the fact one
# step — from a file a reader loads to git-at-a-pin — rather than into a
# second live home (invariant 3).
#
# THE PIN IS A BLOB SHA AND NEVER A REVISION. `git cat-file -p <40-hex>`
# yields the same bytes forever; `HEAD:ITEMS-DONE.md` names whatever the file
# holds today. The sibling repo measured what the second costs: 313 of 318
# line-anchored pointers landed on the wrong entry and NOTHING FAILED,
# because a line number always resolves. A compaction pinning a revision
# would manufacture confident wrong pointers, which is worse than one that
# pinned nothing at all.

#: What a resolved pin must look like before anything is written. A pin that
#: is not 40 hex is not a blob, whatever git printed.
_BLOB_SHA = re.compile(r"^[0-9a-f]{40}$")

#: The record's KIND is read from the DECLARATION, not invented here: the
#: `done bodies` kind declares its exit recording-act as "a ledger decision
#: line naming the compacted range". So this writes an ordinary `decision:`
#: line through `ledger.append` and the ledger's closed four-kind vocabulary
#: does not move for this verb.
#:
#: NEITHER HALF MAY CARRY THE LEDGER'S OWN SEPARATORS (`grammar.check_prose`):
#: a value carrying ` — ` or ` → ` parses into different slots than it was
#: written with. Both halves below are composed from an id, a path and hex,
#: so neither can.
NO_CLOSED_REF = "no closed-ref recorded"


def compaction_question(ident: str) -> str:
    return f"where the compacted body of {ident} resolves"


def compaction_answer(done_rel: str, blob: str, ref: str) -> str:
    return (f"{done_rel} at blob {blob}; closed-ref {ref}; recover with "
            f"git cat-file -p {blob}")


#: THE QUESTION'S TWO FIXED HALVES, DERIVED FROM THE WRITER rather than
#: restated beside it. `compacted_ident` below is `compaction_question` read
#: backwards, and the pair is the ledger's own MOOT-answer shape (`ledger.py`):
#: one spelling, writer and recogniser adjacent, because two literals for one
#: sentence diverge SILENTLY — the writer keeps writing a shape the reader has
#: stopped recognising, and here that reader is the id allocator, so every
#: compacted id would quietly come back into circulation.
_Q_HEAD, _Q_TAIL = compaction_question("\x00").split("\x00")


def compacted_ident(question: str) -> str | None:
    """The id a compaction question names, or None for any other question.

    BOTH ENDS ARE ANCHORED. A head-only match is a prefix test wearing an
    equality's costume: any longer question beginning the same way would
    satisfy it, and the id it yielded would be whatever followed.
    """
    q = (question or "").strip()
    if not q.startswith(_Q_HEAD) or not q.endswith(_Q_TAIL):
        return None
    ident = q[len(_Q_HEAD):len(q) - len(_Q_TAIL)].strip()
    return ident or None


def compacted_home(ledger_parsed) -> "items_mod.Parsed":
    """The compacted ids as a HOME the allocator reads (lc-148).

    `next_ident`'s reason for correctness is that EVERY home is read, live and
    closed. Compaction is the first verb that takes a body out of BOTH, so the
    record it writes is the third home — and this builds that home out of the
    ledger lines `ledger.parse_line` has already read back, never out of a
    second parser over the same text.

    A `Parsed` rather than a bare set of ids, because a `Parsed` is what the
    allocator reads — `migrate.IdentAllocator` builds the same shape for the
    ids one run has issued. A second notion of "an id in use" would be a
    second body for a fact the parser already holds.

    `None` — no ledger to read — yields an EMPTY home rather than raising:
    whether an unreadable ledger is could-not-verify is the CALLER's question,
    because only the caller knows an absent file from a broken one.
    """
    home = items_mod.Parsed()
    if ledger_parsed is None:
        return home
    for ln in getattr(ledger_parsed, "lines", ()):
        if ln.kind != "decision":
            continue
        ident = compacted_ident(ln.slots.get("question", ""))
        if ident:
            home.items.append(items_mod.Item(ident=ident, slots={},
                                             line=ln.lineno))
    return home


def compacted_home_at(ledger_path) -> tuple:
    """`(home, why-not)` — the same home, read off the ledger FILE.

    ONE BODY FOR TWO CALLERS (`item add`'s two joins and the migration's
    allocator): the three answers below are a judgement, and a second copy of
    that judgement in the other caller would be two bodies for one fact — the
    divergence silent, since both would keep allocating.

    AN ABSENT LEDGER IS AN EMPTY HOME, NOT COULD-NOT-VERIFY, and that is not
    the usual absent-file shortcut: `item compact` writes its record through
    `ledger.append`, which CREATES the file when it is missing, so a repo with
    no ledger has recorded no compaction and no id was ever folded. The
    absence is evidence, not ignorance — and an allocator that refused on a
    missing file would pass its own reuse test while breaking every fresh
    repo. A ledger that IS there and cannot be read is the other answer: the
    home exists and this run could not see it, which is could-not-verify,
    exactly what the done home already gets.
    """
    from . import ledger as ledger_mod

    if not Path(ledger_path).exists():
        return compacted_home(None), None
    parsed, why = ledger_mod.read(Path(ledger_path))
    if parsed is None:
        return None, why
    if parsed.refused:
        return None, (f"{ledger_path} is stamped above the schema floor, so "
                      "its body was not parsed and the ids compaction folded "
                      "out of both carriers could not be read.")
    return compacted_home(parsed), None


def _git(repo: Path, *argv) -> tuple:
    import subprocess
    p = subprocess.run(["git", "-C", str(repo), *argv],
                       capture_output=True, text=True)
    return p.returncode, (p.stdout if p.returncode == 0
                          else (p.stderr or p.stdout))


def pinned_body(repo: Path, done_rel: str, ident: str) -> tuple:
    """`(blob, body, why)` — the done body as GIT holds it, at a blob pin.

    RESOLVED BEFORE ANYTHING IS WRITTEN, and the blob it returns is what the
    record carries. The body is extracted by `items.replace_body` — the SAME
    function the caller extracts the live body with — so the comparison the
    caller makes is between two parsed blocks and never a match over rendered
    text, which any longer body beginning the same way would satisfy.
    """
    code, out = _git(repo, "rev-parse", f"HEAD:{done_rel}")
    if code != 0:
        return None, None, (f"git holds no {done_rel} at HEAD "
                            f"({out.strip()[:160]!r}), so there is no "
                            "committed copy to resolve the body back out of")
    blob = out.strip()
    if not _BLOB_SHA.match(blob):
        return None, None, (f"the pin resolved to {blob!r}, which is not a "
                            "40-hex blob sha — a record carrying it would not "
                            "resolve for anybody")
    code, text = _git(repo, "cat-file", "-p", blob)
    if code != 0:
        return blob, None, (f"blob {blob} could not be read "
                            f"({text.strip()[:160]!r})")
    _kept, body = items_mod.replace_body(text, ident)
    if body is None:
        return blob, None, (f"blob {blob} carries no `{ident}` block, so the "
                            "committed copy of the done home does not hold "
                            "this body at all")
    return blob, body, None


def cmd_item_compact(args, out, ctx) -> int:
    """Collapse one closed body to a ledger line, the body kept at a blob pin.

    THE ORDER IS RECORD FIRST, and it carries the same judgment
    `verbs.move_to_done` states for append-then-delete: the window between
    the writes must fall on the recoverable side. The record is written, then
    the body is removed, then the head's count is raised — so a crash leaves
    a record naming a body that is still present (over-recorded, visible and
    harmless), never a body removed with nothing naming where it went. The
    head bump last means a crash before it leaves the identity SHORT, which
    is the loud finding rather than the quiet one.

    NOTHING IS WRITTEN UNTIL THE PIN IS PROVEN. Every refusal below returns
    before the first write, so a refused compaction leaves the tree exactly as
    it found it — which is what makes "it refused" checkable by reading the
    carrier rather than by trusting the message.
    """
    from . import ledger as ledger_mod
    from . import verbs as verbs_mod

    ident = args.ident
    if not ctx.done_path.exists():
        out(f"COULD NOT VERIFY: no done home at {ctx.done_path}. An absent "
            "closure home and one holding no such body are not the same "
            "answer: the first means this verb could not run.")
        return exits.COULD_NOT_VERIFY
    done_rel = str(ctx.done_path.relative_to(ctx.repo))

    with items_mod.carrier_lock(ctx.items_path):
        items_text = ctx.items_path.read_text(encoding="utf-8")
        items_parsed = items_mod.parse(items_text)
        if "compacted" not in items_parsed.head:
            out("COULD NOT VERIFY: the carrier head declares no `compacted:`, "
                "so this exit has nowhere to be counted and the conservation "
                "identity could not survive it. Nothing was written.")
            return exits.COULD_NOT_VERIFY

        # AN ID IN BOTH HOMES IS NOT COMPACTED, and the row is the one that
        # already owns this input. Compacting the done copy of a DUPLICATE
        # would delete exactly the copy `item check` tells a reader to KEEP,
        # and the identity would come out balanced afterwards — the surplus
        # absorbed by the bump, so the state that made it visible would be
        # gone. A repair wearing an exit's costume.
        live = {it.ident for it in items_parsed.items}
        if ident in live:
            out(f"FINDING [duplicate_id] id {ident!r} is in BOTH homes, so it "
                "is NOT compactable: this is the interrupted-close window, "
                "which is DUPLICATE and recoverable. Compacting the done copy "
                "would delete the copy the repair keeps and leave the "
                "identity balanced afterwards, so the evidence of the "
                "interruption would go with it. The repair is unchanged — "
                "delete the LIVE copy once the done copy is confirmed "
                "complete, then compact.")
            return exits.FINDING

        done_text = ctx.done_path.read_text(encoding="utf-8")
        kept, body = items_mod.replace_body(done_text, ident)
        if body is None:
            out(f"FINDING [unknown_item] no closed block {ident!r} in "
                f"{done_rel}. Compaction is the DONE BODY's exit, so a live "
                "item takes `item close` first; and a body below "
                f"`{items_mod.ARCHIVE_HEADING}` is held verbatim and is not "
                "reachable from here at all.")
            return exits.FINDING

        blob, pinned, why = pinned_body(ctx.repo, done_rel, ident)
        detail = None
        if pinned is None:
            detail = why
        elif pinned != body:
            detail = (f"the body in {done_rel} and the body at blob {blob} "
                      f"DIFFER — {len(body)} characters here against "
                      f"{len(pinned)} there. The difference is uncommitted, "
                      "so it exists in no blob any record could name")
        if detail is not None:
            out(f"FINDING [compaction_would_strip] {ident} was NOT compacted: "
                f"{detail}. This verb's whole design is that the body leaves "
                "the carrier and stays byte-for-byte recoverable at a blob "
                "pin, so a body the pin does not carry is one it would strip "
                "SILENTLY — the carrier would shrink and the text would be "
                "nowhere. COMMIT the done home and run this again. Nothing "
                "was written.")
            return exits.FINDING

        ref = NO_CLOSED_REF
        for ln in body.split("\n"):
            if grammar.is_slot(ln, items_mod.CLOSED_REF):
                ref = ln.split(":", 1)[1].strip() or NO_CLOSED_REF
                break
        new_items, bumped = items_mod.bump_compacted(items_text)
        if not bumped:
            out("COULD NOT VERIFY: the head's `compacted:` count is not an "
                "integer this build could raise, so the identity could not "
                "record this exit. Nothing was written.")
            return exits.COULD_NOT_VERIFY

        # 1. THE RECORD, before the tree ever holds one body fewer.
        line = ledger_mod.append(ctx.ledger_path, "decision",
                                 {"question": compaction_question(ident),
                                  "answer": compaction_answer(done_rel, blob,
                                                              ref)})
        out(f"ledger: {line}")
        # 2. THE BODY LEAVES. 3. THE COUNT RISES.
        atomic.write_text(ctx.done_path, kept.rstrip("\n") + "\n", encoding="utf-8")
        atomic.write_text(ctx.items_path, new_items, encoding="utf-8")
        out(f"compacted {ident}: {len(body)} character(s) left {done_rel}; "
            f"the body resolves at blob {blob}")
        if ref == NO_CLOSED_REF:
            out(f"closed-ref: {NO_CLOSED_REF} on this body, and the record "
                "says so rather than omitting the field. A closure "
                "legitimately has none; the BLOB is what makes the body "
                "recoverable either way.")
        code = verbs_mod.commit_paths(
            ctx, [ctx.ledger_path, ctx.done_path, ctx.items_path],
            f"lifecycle: compact {ident}", out,
            skip=getattr(args, "no_commit", False), what="the compaction")

        # CONSERVATION IS RE-RUN AT THE ACT, never asserted about it. This is
        # the first exit that moves the identity's RIGHT-hand side, so a run
        # that only ever saw closures would never have exercised the
        # subtraction at all.
        after = items_mod.parse(ctx.items_path.read_text(encoding="utf-8"))
        try:
            done_after = items_mod.parse(
                ctx.done_path.read_text(encoding="utf-8"))
            done_why = None
        except (OSError, UnicodeDecodeError) as exc:
            done_after, done_why = None, f"{done_rel} could not be read ({exc!r})"
        code = exits.worst([code, items_mod.report_conservation(
            items_mod.conservation(after, done_after, done_why), out)])
    args.fire_detail = f"compact {ident}"
    return code
