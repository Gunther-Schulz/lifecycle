"""The write verbs: `item add` (stage 4) and `item ready|park|close` (stage 5).

INTAKE IS A MERGE (§3.2), NOT AN INSERT. `item add` is the only admission
path — both doors and every detector — and before it writes anything it asks
whether this item is already here. That question is the whole point: a
carrier grows because every sighting of one problem enters as a new row, and
no amount of later pruning recovers the fact that three rows were one.

THE JOIN IS TWO-PHASE BECAUSE THE CALLER IS NOT A PROMPT. The design says
"the caller answers merge-into / supersede / new". A CLI has no dialogue, so
the answer is a flag: an add that finds candidates and carries no `--join`
REFUSES and prints them, with the matching `rejected:` ledger lines beside
each. The refusal IS the question. An add that wrote first and reported the
candidates afterwards would be an insert with a report attached.

WHY `new` COSTS MORE THAN THE OTHER TWO. `new` needs a NAMED ABSENCE — what
the build needs that is not here now — and a one-file, one-hunk write-set
with the session live is vetoed outright: booking that costs what doing it
costs is a deferral refuting itself in its own arithmetic. Operator-mentioned
items skip the VETO, never the join: the operator's intent is authority, but
whether the thing is already booked is a question about the carrier, and
authority does not answer it.

THE MOVE (§3.1) IS APPEND, DELETE, COMMIT — in that order, and the order is
the design rather than an implementation choice. The window between append
and delete holds two copies, which is recoverable; the opposite order would
put the window on the loss side. `check_move_integrity` is what makes that
window visible afterwards.
"""

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from . import exits, ledger
from . import items as items_mod

#: A candidate needs this many shared requirement tokens. ONE would match
#: nearly every pair of items in a repo whose vocabulary is its own domain,
#: and a join that lists forty candidates is a join nobody reads — the
#: over-firing guard that trains the reflex to skip it. Write-set path
#: matching is exact and needs no threshold; this is only for prose.
MATCH_MIN_TOKENS = 2

#: Words that carry no discriminating power in a requirement line. Kept
#: short on purpose: a long stopword list is a second vocabulary to maintain,
#: and the two-token threshold above is what actually does the work.
STOPWORDS = frozenset("""
that this with from have been were will would should could when what which
they them then than there their these those into over under after before
because while about above below only just also more most some such very
than does done doing make makes made take takes need needs must never
always where whose whom else same both each other another every
""".split())

_TOKEN = re.compile(r"[a-z0-9][a-z0-9-]{3,}")

#: Write-set sentinels. `UNKNOWN` NEVER matches (§3.2, stated in the design
#: itself) — it means "nobody recorded one", and treating unknown as a match
#: would join every migrated entry to every other. `NONE` never matches
#: either, for the same reason one level over: two items that both realize
#: nowhere are not thereby related.
WRITE_SET_SENTINELS = ("NONE", "UNKNOWN")

SOURCE_OPERATOR = "operator"
SOURCE_SESSION = "session"
DETECTOR_PREFIX = "detector:"


@dataclass
class Ctx:
    repo: Path
    declaration: dict
    prefix: str
    items_path: Path
    done_path: Path
    ledger_path: Path


# --- context ------------------------------------------------------------------

def _kind_home(declaration: dict, kind: str) -> str | None:
    body = (declaration.get("kinds") or {}).get(kind)
    home = body.get("home") if isinstance(body, dict) else None
    return home if isinstance(home, str) and home.strip() else None


def context(repo: Path, declaration: dict, out):
    """`(Ctx, code)` — the homes, resolved THROUGH the declaration.

    The done home is resolved through the top-level `closure-home`, and a
    `done bodies` kind naming a DIFFERENT home is a finding rather than a
    tiebreak. Two spellings of one fact diverge, and the one that diverges
    silently is whichever the reader did not open.
    """
    items_home = _kind_home(declaration, "items")
    if not items_home:
        out("FINDING [kind_stage_undeclared] the `items` kind declares no "
            "`home`, so there is no carrier to write to.")
        return None, exits.FINDING

    closure = declaration.get("closure-home")
    if not isinstance(closure, str) or not closure.strip():
        out("FINDING [declaration_malformed] no `closure-home` in the "
            "declaration. A closure MOVES a body to a home; without the "
            "declaration there is nowhere for it to move to, and a close "
            "that had nowhere to move would be a delete.")
        return None, exits.FINDING

    done_home = _kind_home(declaration, "done bodies")
    if done_home and done_home != closure:
        out(f"FINDING [closure_home_split] the declaration names TWO closure "
            f"homes: `closure-home` says {closure!r} and the `done bodies` "
            f"kind's `home` says {done_home!r}. One fact, one home — a reader "
            "resolves through whichever it happens to open, and the two "
            "diverge from the moment they disagree.")
        return None, exits.FINDING

    ledger_home = _kind_home(declaration, "ledger lines")
    return Ctx(
        repo=repo,
        declaration=declaration,
        prefix=declaration.get("id-prefix") or "",
        items_path=repo / items_home,
        done_path=repo / closure,
        ledger_path=repo / (ledger_home or "LEDGER.md"),
    ), exits.CLEAN


def _load(path: Path):
    """`(Parsed, why-not)` for a carrier home. An ABSENT home is COULD NOT
    VERIFY, never an empty one: they differ in whether anything was checked."""
    if not path.exists():
        return None, (f"no carrier at {path}. An absent file and an empty one "
                      "are not the same answer, and neither is clean.")
    try:
        return items_mod.parse(path.read_text(encoding="utf-8")), None
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"{path} could not be read ({exc!r})."


# --- origin (§3.1) ------------------------------------------------------------

def origin_repo() -> Path | None:
    """The git work tree containing the CWD — the writer's own repo."""
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return Path(r.stdout.strip()).resolve()


def check_origin(ctx: Ctx, out) -> int:
    """A PUBLIC repo refuses an item whose source cwd is another repo (§3.1).

    The hazard is content crossing INTO a public tree from a private one —
    a requirement line quoting another project's problem, an evidence
    pointer naming its paths. The rule is coarse on purpose: it refuses by
    ORIGIN rather than by inspecting the prose, because "is this sentence
    about another repo" has no predicate and the inspection would be the
    judgment remainder pretending to be a check.
    """
    if ctx.declaration.get("public") is not True:
        return exits.CLEAN
    here = origin_repo()
    if here is None:
        out("COULD NOT VERIFY: this repo declares `public: true`, and the "
            "writer's own repo could not be resolved (cwd is not inside a "
            "git work tree). A foreign-origin item cannot be ruled out, and "
            "an unruled-out foreign origin on a public repo is not clean.")
        return exits.COULD_NOT_VERIFY
    if here != ctx.repo.resolve():
        out(f"FINDING [foreign_origin_item] this repo declares `public: "
            f"true` and the item's source cwd is another repo ({here}). "
            "Items are admitted from inside the repo they belong to: the "
            "requirement, the evidence pointer and the write-set all carry "
            "that repo's vocabulary, and a public tree is where it stops "
            "being retractable.")
        return exits.FINDING
    return exits.CLEAN


# --- the join (§3.2) ----------------------------------------------------------

def write_set_entries(value: str) -> list:
    """The write-set's paths/venues. Comma-separated, sentinels dropped.

    Compared as whole normalized ENTRIES, never by substring: `tools/x.py`
    and `tools/x.py.bak` share a prefix and are not the same write-set, and
    a substring test is a prefix match wearing an equality's costume.
    """
    out = []
    for part in (value or "").split(","):
        p = part.strip()
        if not p or p.upper() in WRITE_SET_SENTINELS:
            continue
        out.append(p)
    return out


def requirement_tokens(value: str) -> set:
    return {t for t in _TOKEN.findall((value or "").lower())
            if t not in STOPWORDS}


def candidates(parsed, requirement: str, write_set: str) -> list:
    """`[(item, [why…])]` — LIVE items this intake may already be.

    Live means an OPEN grade. A closed item is not a merge target: merging
    into it would resurrect a body from the done home, which is a move the
    carrier has no verb for and conservation would not survive.
    """
    want_paths = set(write_set_entries(write_set))
    want_tokens = requirement_tokens(requirement)
    found = []
    for it in parsed.items:
        if it.grade not in items_mod.GRADES_OPEN:
            continue
        why = []
        shared_paths = want_paths & set(write_set_entries(
            it.slots.get("write-set", "")))
        if shared_paths:
            why.append("shares write-set " + ", ".join(sorted(shared_paths)))
        shared_tokens = want_tokens & requirement_tokens(
            it.slots.get("requirement", ""))
        if len(shared_tokens) >= MATCH_MIN_TOKENS:
            why.append(f"shares {len(shared_tokens)} requirement token(s): "
                       + ", ".join(sorted(shared_tokens)))
        if why:
            found.append((it, why))
    return found


def print_candidates(ctx: Ctx, found: list, out) -> None:
    """The join's own screen: every candidate, with its matching `rejected:`
    ledger lines beside it (§3.6's first gated reader).

    The rejected lines are the half that stops a re-proposal: an approach
    already tried and rejected reads, from inside a fresh session, exactly
    like a new idea.
    """
    parsed, why = ledger.read(ctx.ledger_path)
    if parsed is None:
        out(f"  (rejected-line gate COULD NOT RUN: {why})")
    for it, reasons in found:
        out(f"  candidate {it.ident}  [{it.grade}]  line {it.line}")
        out(f"      requirement: {it.slots.get('requirement', '')}")
        out(f"      write-set:   {it.slots.get('write-set', '')}")
        for r in reasons:
            out(f"      match: {r}")
        if parsed is not None:
            hits = ledger.rejected_for(parsed, it.ident)
            if hits:
                for h in hits:
                    out(f"      rejected: {h.slots['approach']} — "
                        f"{h.slots['why']}")
            else:
                out("      rejected: none recorded for this item")


# --- the cost test (§3.2) -----------------------------------------------------

def cost_test(write_set: str, hunks: int | None, source: str):
    """`(verdict, message)` — verdict in "veto", "clear", "unverified".

    "A one-file, one-hunk write-set with the session live prints 'do it
    now?'" The tool can see the file count; it cannot see the hunk count, so
    the caller states it — and a caller that does NOT state it leaves the
    test unevaluated, which is COULD NOT VERIFY rather than a pass. That
    distinction is the whole rule: a cost test that silently cleared every
    add it could not evaluate would clear exactly the adds worth vetoing.
    """
    entries = write_set_entries(write_set)
    if len(entries) != 1:
        return "clear", (f"cost test: not applicable — the write-set names "
                         f"{len(entries)} path(s); the do-it-now shape is one "
                         "file, one hunk.")
    if hunks is None:
        return "unverified", (
            "the write-set names ONE file and the hunk count was not stated "
            "(`--hunks <n>`). A one-file, one-hunk write-set with the session "
            "live is do-it-now, not book-it — and this add cannot tell which "
            "it is. State the hunk count.")
    if hunks != 1:
        return "clear", (f"cost test: clear — one file but {hunks} hunks, "
                         "which is not the do-it-now shape.")
    if source == SOURCE_OPERATOR:
        return "clear", ("cost test: one file, one hunk — DO IT NOW? — but "
                         "the source is the operator, who skips the veto. "
                         "The join above was not skipped and never is.")
    return "veto", (
        f"do it now? The write-set is one file ({entries[0]}) and one hunk, "
        "and the session that can see this is live. Booking it costs about "
        "what doing it costs, so the entry would be the deferral refuting "
        "itself in its own arithmetic. If it genuinely cannot be done here, "
        "the blocker is real and belongs on an `item park`; if the operator "
        "asked for it to be booked, say so with `--source operator`.")


# --- the move (§3.1) ----------------------------------------------------------

def move_to_done(ctx: Ctx, ident: str, closing_grade: str, note: str,
                 out) -> int:
    """Append to the done home, delete from the carrier, commit BOTH.

    ONE ACT, in this order, and the order carries the design's judgment: the
    window between append and delete holds two copies of one body, which the
    next `item check` reports as DUPLICATE and recoverable. Deleting first
    would put the same window on the loss side, where a crash leaves nothing
    to recover and no record that there was anything to recover.
    """
    items_text = ctx.items_path.read_text(encoding="utf-8")
    kept, body = items_mod.replace_body(items_text, ident)
    if body is None:
        out(f"FINDING [unknown_item] no live block {ident!r} in "
            f"{ctx.items_path.name}.")
        return exits.FINDING

    body = _regrade(body, closing_grade)
    if note:
        body = body.rstrip("\n") + f"\n{note}\n"

    if not ctx.done_path.exists():
        ctx.done_path.write_text(f"schema: {items_mod.SCHEMA_FLOOR}\n",
                                 encoding="utf-8")
    done_text = ctx.done_path.read_text(encoding="utf-8")

    # 1. APPEND to the done home — before the tree ever holds one copy fewer.
    done_new = _insert_before_archive(done_text, body)
    ctx.done_path.write_text(done_new, encoding="utf-8")
    # 2. DELETE from the carrier.
    ctx.items_path.write_text(kept.rstrip("\n") + "\n", encoding="utf-8")
    out(f"moved {ident} → {ctx.done_path.name} (grade {closing_grade})")
    # 3. COMMIT is the CALLER's, because the act's file set is the caller's:
    # a supersede writes three files and a drop writes three, and committing
    # the pair here would leave the third behind — a ledger line recording a
    # move that the same commit did not contain.
    return exits.CLEAN


def _regrade(body: str, grade: str) -> str:
    lines = body.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("grade:"):
            lines[i] = f"grade: {grade}"
            break
    return "\n".join(lines)


def _insert_before_archive(done_text: str, body: str) -> str:
    """Append a body to the done home's LIVE section.

    Before the archive heading, never after it: the archive holds
    pre-migration bodies verbatim, and a fixed-slot block written into it
    would be exempted from the shape check that is supposed to grade it.
    """
    lines = done_text.split("\n")
    for i, ln in enumerate(lines):
        if ln.strip() == items_mod.ARCHIVE_HEADING:
            head = "\n".join(lines[:i]).rstrip("\n")
            tail = "\n".join(lines[i:])
            return f"{head}\n\n{body.rstrip(chr(10))}\n\n{tail}"
    return done_text.rstrip("\n") + "\n\n" + body.rstrip("\n") + "\n"


def commit_paths(ctx: Ctx, paths, msg: str, out, skip: bool = False) -> int:
    """Commit exactly the files this act wrote, BY PATHSPEC, never the index.

    The index is shared with whatever else is running in this work tree, so
    `git add` then commit would carry a co-writer's staged paths out under
    this message. The pathspec form ignores the index for everything else.
    """
    if skip:
        out("NOT COMMITTED (--no-commit): the files are consistent on disk, "
            "but the set is durable together only once committed. A caller "
            "batching moves owns that commit.")
        return exits.CLEAN
    rel = [str(p.relative_to(ctx.repo)) for p in paths]
    r = subprocess.run(["git", "-C", str(ctx.repo), "commit", "-m", msg,
                        "--"] + rel, capture_output=True, text=True)
    if r.returncode != 0:
        out(f"FINDING [move_uncommitted] the move is on disk but was NOT "
            f"committed, so the two halves are not durable together: "
            f"{(r.stderr or r.stdout).strip()[:300]!r}. The files are "
            "consistent — this is the third step of the move failing, not "
            "the move.")
        return exits.FINDING
    out(f"committed: {msg}")
    return exits.CLEAN


# --- `item add` ---------------------------------------------------------------

def cmd_item_add(args, out, ctx: Ctx) -> int:
    code = check_origin(ctx, out)
    if code != exits.CLEAN:
        return code

    source = args.source or SOURCE_SESSION
    if source not in (SOURCE_SESSION, SOURCE_OPERATOR) and not \
            source.startswith(DETECTOR_PREFIX):
        out(f"FINDING [unknown_source] `--source {source}` is not one of "
            f"{SOURCE_SESSION}, {SOURCE_OPERATOR}, {DETECTOR_PREFIX}<name>. "
            "The doors are closed the same way the grades are: an "
            "unrecognised source would decide the cost test's veto silently.")
        return exits.FINDING

    slots, code = _collect_slots(args, ctx, out)
    if code != exits.CLEAN:
        return code

    parsed, why = _load(ctx.items_path)
    if parsed is None:
        out(f"COULD NOT VERIFY: {why}")
        return exits.COULD_NOT_VERIFY
    done_parsed, done_why = _load(ctx.done_path)

    code = _check_blocker(slots["blocked-by"], ctx, parsed, done_parsed,
                          done_why, out)
    if code != exits.CLEAN:
        return code

    found = candidates(parsed, slots["requirement"], slots["write-set"])
    join = args.join
    if found and not join:
        out(f"FINDING [join_undisposed] intake is a MERGE, and this add "
            f"matches {len(found)} live item(s). Answer with `--join "
            "merge-into <id>`, `--join supersede <id>` or `--join new "
            "--absence \"<what is missing now>\"` — nothing was written.")
        print_candidates(ctx, found, out)
        return exits.FINDING

    if join and join.startswith("merge-into"):
        return _do_merge(args, ctx, parsed, out)
    if join and join.startswith("supersede"):
        return _do_supersede(args, ctx, parsed, slots, out)

    return _do_new(args, ctx, parsed, done_parsed, done_why, slots, source, out)


def _collect_slots(args, ctx: Ctx, out):
    """The seven slots, validated. Grade DERIVED unless stated."""
    slots = {
        "requirement": (args.requirement or "").strip(),
        "goal": (args.goal or "").strip(),
        "write-set": (args.write_set or "").strip(),
        "done-criterion": (args.done_criterion or "").strip(),
        "evidence": (args.evidence or "").strip(),
        "blocked-by": (args.blocked_by or items_mod.BLOCKER_NONE).strip(),
    }

    goals = ctx.declaration.get("goals") or []
    if slots["goal"] and slots["goal"] not in goals:
        out(f"FINDING [dangling_reference] `--goal {slots['goal']}` is not "
            f"one of the declared goals ({', '.join(goals) or 'none'}). An "
            "item advancing none of the repo's goals is a retire-lane drop "
            "candidate, which is a judgment the carrier can only make "
            "against a declared list.")
        return None, exits.FINDING

    # Slot completeness decides the grade, and UNKNOWN is not complete: it is
    # the migration's marker for "nobody recorded one", and the grade
    # workflow fills it. Treating it as filled would grade a migrated entry
    # READY on a slot nobody has ever written.
    complete = all(slots[s] for s in
                   ("requirement", "goal", "write-set", "done-criterion",
                    "evidence")) and slots["write-set"].upper() != "UNKNOWN"

    if args.grade:
        grade = args.grade
        if grade not in items_mod.GRADES:
            out(f"FINDING [unknown_grade_write] `--grade {grade}` is not one "
                f"of the five grades ({', '.join(items_mod.GRADES)}). The "
                "vocabulary is CLOSED on write: a word the counter does not "
                "know is folded into neither open nor closed, and the drain "
                "triggers read exactly those numbers.")
            return None, exits.FINDING
    else:
        grade = "READY" if complete else "NEW"
    slots["grade"] = grade

    if grade == "NEW" and not complete:
        kind, _d = items_mod.classify_blocker(slots["blocked-by"], ctx.prefix)
        if kind in (None, "none"):
            missing = [s for s in ("requirement", "goal", "write-set",
                                   "done-criterion", "evidence")
                       if not slots[s]]
            if slots["write-set"].upper() == "UNKNOWN":
                missing.append("write-set (UNKNOWN)")
            out("FINDING [new_without_typed_blocker] slots are incomplete "
                f"({', '.join(missing)}), so this item is NEW — and a NEW "
                "item carries a TYPED blocker saying what it is waiting for: "
                f"`<{ctx.prefix}-<n>>`, `decision <question>` or `evidence "
                "<predicate>`. An incomplete item with nothing to wait for is "
                "the entry that ages in nobody's court.")
            return None, exits.FINDING

    for slot in items_mod.SLOTS:
        problem = items_mod.slot_value_problem(slot, slots.get(slot))
        if problem:
            out(f"FINDING [item_shape] {problem}")
            return None, exits.FINDING
    return slots, exits.CLEAN


def _check_blocker(value: str, ctx: Ctx, parsed, done_parsed, done_why, out) -> int:
    """Typed, and — for an item-id blocker — pointing at an item that IS."""
    kind, detail = items_mod.classify_blocker(value, ctx.prefix)
    if kind is None:
        out(f"FINDING [blocker_untyped] `--blocked-by {value!r}` is not a "
            f"typed blocker. The edge types are closed (§3.1): "
            f"`{ctx.prefix}-<n>`, `decision <question>`, `evidence "
            "<predicate>`, or NONE. Prose is not an edge — an aging item is "
            "routed by whose court it sits in, and prose sits in nobody's.")
        return exits.FINDING
    if kind != "item":
        return exits.CLEAN
    if done_parsed is None:
        out(f"COULD NOT VERIFY: `blocked-by {detail}` names an item, and the "
            f"done home could not be read to confirm it exists. {done_why}")
        return exits.COULD_NOT_VERIFY
    known = {it.ident for it in parsed.items} | {
        it.ident for it in done_parsed.items}
    if detail not in known:
        out(f"FINDING [dangling_reference] `blocked-by {detail}` names an "
            "item that is in neither home. A blocker pointing at nothing "
            "reads exactly like one pointing at live work, and it never "
            "resolves — the item waits forever in a court that does not "
            "exist.")
        return exits.FINDING
    dropped = [it for it in done_parsed.items
               if it.ident == detail and it.grade == "DROPPED"]
    if dropped:
        out(f"FINDING [dangling_reference] `blocked-by {detail}` names a "
            "DROPPED item. An item-id blocker resolves on its target's DONE; "
            "a dropped target never reaches DONE, so this blocker can only "
            "expire, never clear.")
        return exits.FINDING
    return exits.CLEAN


def _do_merge(args, ctx: Ctx, parsed, out) -> int:
    target = args.join.split(None, 1)[1].strip() if " " in args.join else ""
    it = next((i for i in parsed.items if i.ident == target), None)
    if it is None:
        out(f"FINDING [unknown_item] `--join merge-into {target}` names no "
            "LIVE item. A merge target must be open: merging into a closed "
            "item would resurrect a body from the done home, and conservation "
            "counts that body on the closed side.")
        return exits.FINDING
    out(f"merged into {it.ident} — NOTHING was written to the carrier.")
    out("    This is intake being idempotent, which is what makes a detector "
        "safe to run twice: the second sighting of one problem is the same "
        "problem, and a second row would make it two.")
    out(f"    {it.ident} [{it.grade}]  {it.slots.get('requirement', '')}")
    args.fire_detail = f"merge-into {it.ident}"
    return exits.CLEAN


def _do_supersede(args, ctx: Ctx, parsed, slots, out) -> int:
    """The new item supersedes a live one: body to the done home, reason here.

    ROUTED ONE WAY (§3.6). The body is counted in the done home; the reason
    is a ledger line and is outside the conservation identity by
    construction — it is not a body and was never counted. Writing the
    reason into the moved body instead would put a decision inside an
    archive nobody gates on.
    """
    target = args.join.split(None, 1)[1].strip() if " " in args.join else ""
    it = next((i for i in parsed.items if i.ident == target), None)
    if it is None:
        out(f"FINDING [unknown_item] `--join supersede {target}` names no "
            "LIVE item.")
        return exits.FINDING
    problem = ledger.check_prose(args.reason, "the supersede reason")
    if problem:
        out(f"FINDING [ledger_body] {problem}")
        return exits.FINDING

    with items_mod.carrier_lock(ctx.items_path):
        parsed2, why = _load(ctx.items_path)
        if parsed2 is None:
            out(f"COULD NOT VERIFY: {why}")
            return exits.COULD_NOT_VERIFY
        done_parsed, done_why = _load(ctx.done_path)
        ident, id_why = items_mod.next_ident(ctx.prefix, parsed2, done_parsed)
        if ident is None:
            out(f"COULD NOT VERIFY: {id_why}")
            return exits.COULD_NOT_VERIFY
        if done_parsed is None:
            out(f"COULD NOT VERIFY: the done home could not be read, so an "
                f"id cannot be proven unused. {done_why}")
            return exits.COULD_NOT_VERIFY

        code = _append_item(ctx, ident, slots, out)
        if code != exits.CLEAN:
            return code
        code = move_to_done(ctx, it.ident, "DONE",
                            f"superseded-by: {ident}", out)
        if code != exits.CLEAN:
            return code
        line = ledger.append(ctx.ledger_path, "superseded",
                             {"id": it.ident, "by": ident,
                              "reason": args.reason.strip()})
        out(f"ledger: {line}")
        code = commit_paths(
            ctx, (ctx.items_path, ctx.done_path, ctx.ledger_path),
            f"lifecycle: {ident} supersedes {it.ident}", out,
            skip=args.no_commit)
        if code != exits.CLEAN:
            return code
    args.fire_detail = f"supersede {it.ident} by {ident}"
    return exits.CLEAN


def _do_new(args, ctx: Ctx, parsed, done_parsed, done_why, slots, source, out) -> int:
    absence = (args.absence or "").strip()
    if not absence:
        out("FINDING [new_without_absence] `new` is taken only with a NAMED "
            "absence (`--absence \"…\"`): what the build needs that is not "
            "here NOW — the realizing write is at another desk or repo, "
            "evidence or an operator decision is outstanding, the work needs "
            "a tier this session is not, or its blast radius exceeds this "
            "session's remaining attention. An absence this session can "
            "dissolve is the next step wearing an absence's costume.")
        return exits.FINDING

    verdict, message = cost_test(slots["write-set"], args.hunks, source)
    if verdict == "unverified":
        out(f"COULD NOT VERIFY: {message}")
        return exits.COULD_NOT_VERIFY
    if verdict == "veto":
        out(f"FINDING [cost_test_veto] {message}")
        return exits.FINDING
    out(message)

    if done_parsed is None:
        out(f"COULD NOT VERIFY: the done home could not be read, so a new id "
            f"cannot be proven unused. Ids are immutable across moves, so an "
            f"allocator blind to the closed home re-issues them. {done_why}")
        return exits.COULD_NOT_VERIFY

    with items_mod.carrier_lock(ctx.items_path):
        parsed2, why = _load(ctx.items_path)
        if parsed2 is None:
            out(f"COULD NOT VERIFY: {why}")
            return exits.COULD_NOT_VERIFY
        done2, _w = _load(ctx.done_path)
        ident, id_why = items_mod.next_ident(ctx.prefix, parsed2, done2)
        if ident is None:
            out(f"COULD NOT VERIFY: {id_why}")
            return exits.COULD_NOT_VERIFY
        code = _append_item(ctx, ident, slots, out)
    if code != exits.CLEAN:
        return code
    out(f"absence named: {absence}")
    args.fire_detail = f"new {ident} source={source}"
    return code


def _append_item(ctx: Ctx, ident: str, slots: dict, out) -> int:
    """Write one block and bump `added`. Both, or the identity breaks.

    `added` is the identity's own right-hand side: an add that wrote a body
    without bumping it would leave conservation reporting a short carrier
    forever, and the number it reported would be correct.
    """
    text = ctx.items_path.read_text(encoding="utf-8")
    block = items_mod.render_block(ident, slots)
    text = text.rstrip("\n") + "\n\n" + block
    text, ok = _bump_added(text)
    if not ok:
        out("FINDING [item_shape] the carrier head carries no `added: <n>` "
            "line, so this add could not record itself in the conservation "
            "identity. The head is written by the tool; a carrier missing it "
            "was created by something else.")
        return exits.FINDING
    ctx.items_path.write_text(text, encoding="utf-8")
    out(f"added {ident} [{slots['grade']}] → {ctx.items_path.name}")
    for slot in items_mod.SLOTS:
        out(f"    {slot}: {slots[slot]}")
    return exits.CLEAN


def _bump_added(text: str):
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("## "):
            break
        if ln.startswith("added:"):
            try:
                n = int(ln.split(":", 1)[1].strip())
            except ValueError:
                return text, False
            lines[i] = f"added: {n + 1}"
            return "\n".join(lines), True
    return text, False


# --- `item ready` (stage 5) ---------------------------------------------------

def cmd_item_ready(args, out, ctx: Ctx) -> int:
    """PRINTS "READY and unblocked". PROMOTES NOTHING. Both halves are load-bearing.

    READY IS JUDGED, NEVER DERIVED (§3.1). A verb that promoted an unblocked
    NEW item to READY would be deriving a decision-completeness judgment from
    a graph property — and this repo has the recorded failure that produces:
    a queue of 95 entries labelled ready that nobody believed, because the
    label asserted something no one had judged. Blocker clearance decides
    SCHEDULABILITY, which is a different question with a different answer.
    """
    parsed, why = _load(ctx.items_path)
    if parsed is None:
        out(f"COULD NOT VERIFY: {why}")
        return exits.COULD_NOT_VERIFY
    it = next((i for i in parsed.items if i.ident == args.ident), None)
    if it is None:
        out(f"FINDING [unknown_item] no live block {args.ident!r} in "
            f"{ctx.items_path.name}.")
        return exits.FINDING

    done_parsed, done_why = _load(ctx.done_path)
    state, code, note = _blocker_state(it, ctx, parsed, done_parsed, done_why)

    out(f"{it.ident} [{it.grade}]  {it.slots.get('requirement', '')}")
    out(f"    blocked-by: {it.slots.get('blocked-by', '')}")
    out(f"    {state}")
    if note:
        out(f"    {note}")
    if it.grade == "READY" and state.startswith("UNBLOCKED"):
        out("READY and unblocked — schedulable now.")
    elif it.grade == "READY":
        out("READY but blocked — decision-complete, not schedulable. The "
            "grade is the desk's judgment and is unaffected by the blocker.")
    else:
        out(f"grade is {it.grade}, not READY. THIS VERB PROMOTES NOTHING: "
            "READY is a judgment the desk makes — a fresh context could "
            "execute this now — and clearing a blocker is not that judgment.")
    return code


def _blocker_state(it, ctx: Ctx, parsed, done_parsed, done_why):
    """`(state, code, note)` for one item's blocker."""
    value = it.slots.get("blocked-by", "")
    kind, detail = items_mod.classify_blocker(value, ctx.prefix)
    if kind == "none":
        return "UNBLOCKED — no blocker recorded.", exits.CLEAN, ""
    if kind is None:
        return ("FINDING [blocker_untyped] the blocker is prose, not a typed "
                "edge, so nothing can re-evaluate it."), exits.FINDING, ""
    if kind == "decision":
        return (f"BLOCKED — in the OPERATOR's court: {detail!r}. A decision "
                "blocker never resolves mechanically and is never "
                "auto-dropped; it is surfaced until answered."), exits.CLEAN, ""
    if kind == "evidence":
        # The predicate is a TRIGGER, and trigger evaluation plus its policy
        # is §3.3/§3.4 — `lane list`, stage 7. Building a second evaluator
        # here would put two bodies behind one contract, and they would
        # disagree about the >=2 BROKEN case first.
        return ("COULD NOT VERIFY — the blocker is an evidence predicate "
                f"({detail!r}), evaluated like a trigger. This build carries "
                "no trigger evaluator (§3.3/§3.4, `lane list`, stage 7), so "
                "whether it has cleared is unknown — which is not the same "
                "as still blocked."), exits.COULD_NOT_VERIFY, ""
    if done_parsed is None:
        return (f"COULD NOT VERIFY — blocker names {detail}, and the done "
                f"home could not be read to see whether it is DONE. "
                f"{done_why}"), exits.COULD_NOT_VERIFY, ""
    target = next((i for i in list(parsed.items) + list(done_parsed.items)
                   if i.ident == detail), None)
    if target is None:
        return (f"FINDING [dangling_reference] blocker names {detail}, which "
                "is in neither home."), exits.FINDING, ""
    if target.grade == "DONE":
        return (f"UNBLOCKED — {detail} is DONE.", exits.CLEAN,
                "\u00a73.1 has the item return to NEW for re-grade here — a "
                "cleared blocker changes what is knowable about it, so the "
                "grade is re-judged rather than inherited. THAT TRANSITION "
                "IS THE DRAIN LANE'S GRADE WORKFLOW (wave 2), not this "
                "verb: this one promotes and demotes nothing, and a message "
                "that did not say so would leave a reader waiting for a "
                "write that never comes.")
    if target.grade == "DROPPED":
        return (f"FINDING [dangling_reference] blocker names {detail}, which "
                "is DROPPED. An item-id blocker resolves on DONE; a dropped "
                "target never reaches it."), exits.FINDING, ""
    return (f"BLOCKED — in the MACHINE's court: {detail} is {target.grade}. "
            "Re-evaluated each pass."), exits.CLEAN, ""


# --- `item park` (stage 5) ----------------------------------------------------

def cmd_item_park(args, out, ctx: Ctx) -> int:
    """PARKED, and a PARKED item without a typed blocker is a checker finding.

    The refusal is HERE and in the file check both. Here it is cheap and
    names the fix; there it catches the block that reached the file some
    other way. A rule enforced only on the write path is a convention with a
    mechanism's reputation.
    """
    value = (args.blocked_by or "").strip()
    kind, detail = items_mod.classify_blocker(value, ctx.prefix)
    if kind in (None, "none"):
        out("FINDING [parked_without_typed_blocker] `item park` needs a "
            f"TYPED `--blocked-by`: `{ctx.prefix}-<n>`, `decision "
            "<question>`, or `evidence <predicate>`. Prose only — or "
            f"nothing — was given ({value!r}). PARKED says the item is "
            "waiting; the type says WHOSE COURT it waits in, and an item in "
            "nobody's court is the one that ages out silently.")
        return exits.FINDING

    parsed, why = _load(ctx.items_path)
    if parsed is None:
        out(f"COULD NOT VERIFY: {why}")
        return exits.COULD_NOT_VERIFY
    done_parsed, done_why = _load(ctx.done_path)
    code = _check_blocker(value, ctx, parsed, done_parsed, done_why, out)
    if code != exits.CLEAN:
        return code

    with items_mod.carrier_lock(ctx.items_path):
        text = ctx.items_path.read_text(encoding="utf-8")
        new, ok = _set_slots(text, args.ident, {"grade": "PARKED",
                                                "blocked-by": value})
        if not ok:
            out(f"FINDING [unknown_item] no live block {args.ident!r} in "
                f"{ctx.items_path.name}.")
            return exits.FINDING
        ctx.items_path.write_text(new, encoding="utf-8")
    out(f"{args.ident} → PARKED, blocked-by: {value}")
    args.fire_detail = f"park {args.ident}"
    return exits.CLEAN


def _set_slots(text: str, ident: str, updates: dict):
    """Rewrite named slots of one block IN PLACE. `(text, found)`.

    In place, and only the named slots: rendering the whole block from a
    parsed dict would rewrite every slot the tool did not mean to touch, and
    a slot rewritten identically is still a slot this act claimed authorship
    of in the diff.
    """
    lines = text.split("\n")
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == items_mod.ARCHIVE_HEADING:
            break
        m = items_mod._BLOCK_HEADING.match(ln)
        if not m:
            continue
        if m.group(1) == ident:
            start = i
            continue
        if start is not None:
            break
    if start is None:
        return text, False
    i = start + 1
    while i < len(lines) and not lines[i].startswith("## "):
        for slot, value in updates.items():
            if lines[i].startswith(f"{slot}:"):
                lines[i] = f"{slot}: {value}"
        i += 1
    return "\n".join(lines), True


# --- `item close` (stage 5) ---------------------------------------------------

def cmd_item_close(args, out, ctx: Ctx) -> int:
    """The MOVE, then conservation — re-run at EVERY close, not asserted once.

    An identity that has never been seen to fail is not a check, and one
    computed only at migration time is a claim about a day that has passed.
    Running it here means every close either confirms the carrier is whole
    or names the moment it stopped being.
    """
    grade = "DROPPED" if args.drop else "DONE"
    reason = (args.reason or "").strip()
    if args.drop:
        problem = ledger.check_prose(args.reason, "the drop reason")
        if problem:
            out(f"FINDING [ledger_body] {problem} A drop is an exit of equal "
                "standing to a completion — the carrier's goal is to lose "
                "nothing SILENTLY, which a recorded drop satisfies and an "
                "unrecorded one does not.")
            return exits.FINDING

    with items_mod.carrier_lock(ctx.items_path):
        if not ctx.items_path.exists():
            out(f"COULD NOT VERIFY: no carrier at {ctx.items_path}.")
            return exits.COULD_NOT_VERIFY
        code = move_to_done(ctx, args.ident, grade, "", out)
        if code != exits.CLEAN:
            return code
        touched = [ctx.items_path, ctx.done_path]
        if args.drop:
            line = ledger.append(ctx.ledger_path, "dropped",
                                 {"id": args.ident, "reason": reason})
            out(f"ledger: {line}")
            touched.append(ctx.ledger_path)
        code = commit_paths(ctx, touched,
                            f"lifecycle: close {args.ident} ({grade})", out,
                            skip=args.no_commit)

        items_parsed, why = _load(ctx.items_path)
        done_parsed, done_why = _load(ctx.done_path)
        if items_parsed is None:
            out(f"COULD NOT VERIFY: {why}")
            return exits.worst([code, exits.COULD_NOT_VERIFY])
        code = exits.worst([code, items_mod.report_conservation(
            items_mod.conservation(items_parsed, done_parsed, done_why), out)])
    args.fire_detail = f"close {args.ident} {grade}"
    return code


# --- `ledger add` (stage 6) ---------------------------------------------------

def cmd_ledger_add(args, out, ctx: Ctx) -> int:
    """Append one fixed-slot line. The TOOL writes slots; the SESSION writes prose.

    Every prose argument below is REQUIRED and none has a default. That is
    the split §3.6 asks for, and it is what keeps the operator-as-backstop
    moment at every rationale line: a generated reason would be a paraphrase
    with nobody's judgment behind it, and it would read exactly like one
    somebody meant.
    """
    if not args.line_kind:
        out("COULD NOT VERIFY: `ledger add` needs a line kind: "
            + ", ".join(ledger.KINDS))
        return exits.COULD_NOT_VERIFY

    if args.line_kind == "superseded":
        slots = {"id": args.ident, "by": args.by, "reason": args.reason}
        prose = [(args.reason, "the supersede reason")]
    elif args.line_kind == "rejected":
        slots = {"item": args.item, "approach": args.approach,
                 "why": args.why_text}
        prose = [(args.approach, "the rejected approach"),
                 (args.why_text, "the rejection reason")]
    elif args.line_kind == "dropped":
        slots = {"id": args.ident, "reason": args.reason}
        prose = [(args.reason, "the drop reason")]
    else:
        slots = {"question": args.question, "answer": args.answer}
        prose = [(args.question, "the decision question"),
                 (args.answer, "the decision answer")]

    for value, what in prose:
        problem = ledger.check_prose(value, what)
        if problem:
            out(f"FINDING [ledger_body] {problem}")
            return exits.FINDING

    line = ledger.append(ctx.ledger_path, args.line_kind,
                         {k: str(v).strip() for k, v in slots.items()})
    out(f"ledger: {line}")
    args.fire_detail = f"ledger add {args.line_kind}"
    return exits.CLEAN
