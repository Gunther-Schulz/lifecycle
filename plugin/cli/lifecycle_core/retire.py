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

WHAT IS NOT CHECKED SAYS SO. Most declared exits are not acts this build
performs — `never`, `compact` and `delete` have no verb yet — so their kinds
are reported NOT CHECKED with the reason rather than folded into a clean
line. A walk that reported nine clean kinds while only checking one would be
the assurance wider than its predicate that this whole arc keeps finding.
"""

import re
from pathlib import Path

from . import exits, firelog, judgment
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
PERFORMED_EXITS = ("move",)

#: Which fire-log verb records each performed exit. Read from the design's
#: own recording-act rather than guessed: `items`' declared recording act IS
#: the `item close` fire-log line.
EXIT_VERBS = {"move": ("item close",)}


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

def list_home(repo: Path, home: str) -> tuple:
    """`(instances, note)` for one kind's declared home, RE-LISTED now.

    Three home shapes, each counted by what an INSTANCE of that kind is:
    a carrier file counts its fixed-slot blocks, a glob counts its files, a
    plain file counts as one. The note says which notion was used, because a
    number without its notion is the figure two readers disagree about.
    """
    if "*" in home:
        base = repo
        hits = sorted(base.glob(home))
        return [str(p.relative_to(repo)) for p in hits if p.is_file()], \
            f"glob {home!r}: one instance per file"
    path = repo / home
    if not path.exists():
        return [], f"{home!r} is not present"
    if path.is_dir():
        hits = sorted(p for p in path.rglob("*") if p.is_file())
        return [str(p.relative_to(repo)) for p in hits], \
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
    if mode != "bounded-by-exit":
        out(f"    growth check: NOT APPLICABLE — `{mode or 'undeclared'}` is "
            "not bounded-by-exit, so 'grew without an exit event' is not the "
            "alarm this kind declared.")
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
    verbs_ = EXIT_VERBS.get(action, ())
    events = [r for r in log if str(r.get("verb", "")) in verbs_]
    out(f"    exit events: {len(events)} ({', '.join(verbs_)}) recorded for "
        "this repo")
    if count and not events:
        out(f"    FINDING [kind_grew_without_exit] kind {name!r} holds "
            f"{count} instance(s), declares `bounded-by-exit`, and its exit "
            "has recorded NOTHING. The alarm is FLOW: the count above is not "
            "the finding and no size would be — a large kind draining "
            "steadily is fine and this one is not draining at all. A recorded "
            "DROP clears this exactly as a completion does.")
        return exits.FINDING, "grew"
    out("    growth check: CLEAN — the exit has fired for this kind.")
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
            out(f"    COULD NOT VERIFY: {note}")
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
        "`.claude/lifecycle.json` with its own six stages; or removed, with a "
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
        out(f"    scope: CLEAN — no line outside the law list carries another "
            "kind's marker.")
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
