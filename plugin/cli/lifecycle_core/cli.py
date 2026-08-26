"""`lifecycle` — one entry point, one fire log (design §3.8).

Subcommands are added a stage at a time; a verb that is not built yet is
NAMED here and refuses with COULD NOT VERIFY rather than "unknown command",
so a caller can tell "this build does not have it" from "you typed it wrong".

Exit codes are `exits.py`'s contract — 0 clean, 2 finding, 3 could not
verify — for every verb here, without exception.
"""

import argparse
import subprocess
import sys
from pathlib import Path

from . import exits, firelog, ledger as ledger_mod
from . import declaration as decl
from . import items as items_mod
from . import verbs

#: Verbs the design names that this build does not carry yet. Listed rather
#: than omitted: a refusal that says "wave 1 stage N builds this" is a fact,
#: while an "unknown command" is a lie about the design.
NOT_YET_BUILT = {
    # `item ratio` is NOT in D-d's stage list at all — stage 5 is
    # `item ready|park|close`. W1a's entry here read "stage 5", which the
    # stage-5 build then contradicted by shipping without it. Recorded as an
    # unassigned verb rather than given a stage this desk did not assign.
    "item ratio": "a stage D-d does not assign — surfaced to the desk",
    "lane": "stage 7",
    "migrate": "stage 9",
    "--test": "stage 8",
}

#: Which stages this build carries, for the refusal messages above. A build
#: that claimed its own coverage from a hardcoded sentence would say
#: "stages 1-3" forever.
STAGES_BUILT = "1-6"


def resolve_repo(explicit: str | None) -> tuple[Path | None, str | None]:
    """The repo to act on: `--repo`, else the work tree containing cwd.

    Returns (path, why-not). Not a git work tree is COULD NOT VERIFY, never a
    default to cwd: acting on the wrong tree is worse than refusing.
    """
    if explicit:
        p = Path(explicit).expanduser()
        if not p.is_dir():
            return None, f"--repo {explicit!r} is not a directory."
        return p.resolve(), None
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, f"could not run git to find the repo root ({exc!r})."
    if r.returncode != 0 or not r.stdout.strip():
        return None, ("not inside a git work tree, and no --repo was given. "
                      "Refusing rather than guessing at the current "
                      "directory.")
    return Path(r.stdout.strip()).resolve(), None


def _report(res, out) -> None:
    """Findings and unverified halves, each labelled with its own answer."""
    for f in res.findings:
        out(f"FINDING [{f.row}] {f.message}")
    for u in res.unverified:
        out(f"COULD NOT VERIFY: {u}")


def cmd_kind(args, out) -> int:
    repo, why = resolve_repo(args.repo)
    if repo is None:
        out(f"COULD NOT VERIFY: {why}")
        return exits.COULD_NOT_VERIFY

    res = decl.read(repo)

    if args.kind_action == "check":
        _report(res, out)
        if res.code == exits.CLEAN:
            n = len(res.declaration.get("kinds", {})) if res.declaration else 0
            out(f"kind check: CLEAN — {n} kind(s) registered, every stage "
                f"declared, declaration visible to git.")
        else:
            out(f"kind check: {exits.word(res.code)} — "
                f"{len(res.findings)} finding(s), "
                f"{len(res.unverified)} check(s) could not verify.")
        return res.code

    # `list` and `show` need a body; without one there is nothing to render
    # and the refusal is the answer.
    if res.declaration is None:
        _report(res, out)
        out(f"kind {args.kind_action}: {exits.word(res.code)} — no readable "
            "declaration, so nothing was listed. An empty listing here would "
            "read exactly like a repo that registers nothing.")
        return res.code

    if args.kind_action == "show":
        kinds = res.declaration.get("kinds", {})
        if args.name not in kinds:
            out(f"FINDING [unregistered_kind] {args.name!r} is not a "
                f"registered kind. Registered: {', '.join(kinds) or '(none)'}")
            return exits.FINDING
        sub = {"kinds": {args.name: kinds[args.name]}}
        for line in decl.render_kinds(sub):
            out(line)
        return exits.CLEAN

    d = res.declaration
    out(f"repo: {repo}")
    out(f"declaration: {res.path}")
    out(f"schema: {d.get('schema')}   id-prefix: {d.get('id-prefix')}   "
        f"public: {d.get('public')}")
    out(f"laws: {d.get('laws')}   closure-home: {d.get('closure-home')}")
    out(f"trigger-policy: {d.get('trigger-policy')}   "
        f"ready-cap: {d.get('ready-cap')}   head-rule: {d.get('head-rule')}")
    out(f"goals: {', '.join(d.get('goals') or []) or '(none declared)'}")
    lanes = d.get("lanes")
    out(f"lanes: {', '.join(lanes) if lanes else '(empty — declared, not absent)'}")
    tb = d.get("template-bindings")
    out(f"template-bindings: {', '.join(tb) if tb else '(empty — declared, not absent)'}")
    out("")
    for line in decl.render_kinds(d):
        out(line)
    if res.findings or res.unverified:
        out("")
        _report(res, out)
    return res.code


def _context(args, out):
    """`(Ctx, code)` — the repo, its declaration, and the three homes.

    Shared by every carrier verb so that "where does this repo keep its
    items" is answered in ONE place. A second resolver would be a second
    reading of the declaration, and the two would disagree the day a key
    moved.
    """
    repo, why = resolve_repo(args.repo)
    if repo is None:
        out(f"COULD NOT VERIFY: {why}")
        return None, exits.COULD_NOT_VERIFY
    args.resolved_repo = str(repo)
    res = decl.read(repo)
    if res.declaration is None:
        _report(res, out)
        out("the carrier's homes are named by the declaration, and there is "
            "no readable declaration to name them.")
        return None, res.code
    return verbs.context(repo, res.declaration, out)


def cmd_item_check(args, out) -> int:
    ctx, code = _context(args, out)
    if ctx is None:
        return code
    code = items_mod.check_file(ctx.items_path, out, prefix=ctx.prefix)

    # THE MOVE'S OWN WINDOW. `check_file` reads one home; an id sitting in
    # BOTH is invisible to it by construction, and that is exactly what an
    # interrupted close leaves behind. The cross-home question is asked here
    # or it is asked nowhere.
    items_parsed, why = verbs._load(ctx.items_path)
    done_parsed, done_why = verbs._load(ctx.done_path)
    if items_parsed is None:
        out(f"COULD NOT VERIFY: {why}")
        return exits.worst([code, exits.COULD_NOT_VERIFY])
    code = exits.worst([code, items_mod.check_move_integrity(
        items_parsed, done_parsed, out, done_why)])
    code = exits.worst([code, items_mod.report_conservation(
        items_mod.conservation(items_parsed, done_parsed, done_why), out)])
    return code


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="lifecycle",
        description="Lifecycle management for everything a repo persists. "
                    "Exit codes: 0 clean, 2 a finding, 3 could not verify.")
    p.add_argument("--repo", help="repo root to act on (default: the work "
                                  "tree containing the current directory)")
    sub = p.add_subparsers(dest="verb")

    k = sub.add_parser("kind", help="the kind registry")
    ks = k.add_subparsers(dest="kind_action")
    ks.add_parser("list", help="every registered kind, every stage, longhand")
    ks.add_parser("check", help="validate the declaration")
    show = ks.add_parser("show", help="one kind, every stage")
    show.add_argument("name")

    it = sub.add_parser("item", help="the item carrier")
    its = it.add_subparsers(dest="item_action")
    its.add_parser("check", help="the shape check over the carrier file")

    add = its.add_parser("add", help="the ONLY admission path (the intake join)")
    add.add_argument("--requirement", help="why, one line + a record pointer")
    add.add_argument("--goal", help="one of the repo's declared goals")
    add.add_argument("--write-set", dest="write_set",
                     help="comma-separated paths/venues, or NONE, or UNKNOWN")
    add.add_argument("--done-criterion", dest="done_criterion")
    add.add_argument("--evidence")
    add.add_argument("--blocked-by", dest="blocked_by",
                     help="TYPED: `<prefix>-<n>` | `decision <q>` | "
                          "`evidence <predicate>` | NONE")
    add.add_argument("--grade", help="normally DERIVED from slot "
                                     "completeness; stated only to override")
    add.add_argument("--source", help=f"{verbs.SOURCE_SESSION} (default), "
                                      f"{verbs.SOURCE_OPERATOR}, or "
                                      f"{verbs.DETECTOR_PREFIX}<name>")
    add.add_argument("--hunks", type=int,
                     help="hunks the realizing write touches — the cost "
                          "test's other half, which the tool cannot see")
    add.add_argument("--join", help="the join's answer: `merge-into <id>`, "
                                    "`supersede <id>`, or `new`")
    add.add_argument("--absence", help="what the build needs that is not "
                                       "here NOW; required for `new`")
    add.add_argument("--reason", help="the SESSION's prose for a ledger line")
    add.add_argument("--no-commit", dest="no_commit", action="store_true",
                     help="skip the move's third step (a batching caller "
                          "owns the commit)")

    ready = its.add_parser("ready", help="READY-and-unblocked; PROMOTES NOTHING")
    ready.add_argument("ident")

    park = its.add_parser("park", help="PARKED, with a typed blocker")
    park.add_argument("ident")
    park.add_argument("--blocked-by", dest="blocked_by", help="TYPED; required")

    close = its.add_parser("close", help="the MOVE: append, delete, commit")
    close.add_argument("ident")
    close.add_argument("--drop", action="store_true",
                       help="close as DROPPED rather than DONE")
    close.add_argument("--reason", help="the SESSION's prose; required for "
                                        "--drop (a ledger `dropped:` line)")
    close.add_argument("--no-commit", dest="no_commit", action="store_true")

    its.add_parser("ratio", help="(not built in this build)")

    led = sub.add_parser("ledger", help="decisions only, parsed, gated")
    leds = led.add_subparsers(dest="ledger_action")
    leds.add_parser("check", help="the ledger's own shape check")

    ladd = leds.add_parser("add", help="append one fixed-slot line")
    ladds = ladd.add_subparsers(dest="line_kind")
    sup = ladds.add_parser("superseded")
    sup.add_argument("ident")
    sup.add_argument("--by", required=True)
    sup.add_argument("--reason")
    rej = ladds.add_parser("rejected")
    rej.add_argument("item")
    rej.add_argument("--approach")
    rej.add_argument("--why", dest="why_text")
    dro = ladds.add_parser("dropped")
    dro.add_argument("ident")
    dro.add_argument("--reason")
    dec = ladds.add_parser("decision")
    dec.add_argument("--question")
    dec.add_argument("--answer")

    lrej = leds.add_parser("rejected",
                           help="THE GATE: every rejected approach for an "
                                "item, run before a re-grade")
    lrej.add_argument("--for", dest="for_item", required=True)

    lane = sub.add_parser("lane", help="(not built in this build)")
    lane.add_subparsers(dest="lane_action").add_parser("list")
    sub.add_parser("migrate", help="(not built in this build)")
    return p


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    out = lambda s: sys.stdout.write(f"{s}\n")  # noqa: E731

    if "--test" in argv:
        out("COULD NOT VERIFY: `--test` is the refusal-table roster and is "
            f"built in stage 8 of wave 1; this build carries stages "
            f"{STAGES_BUILT}. The rows this build implements are executable "
            "in lifecycle_core/refusals.py and are exercised by "
            "test/test_refusals.py.")
        firelog.fire("--test", outcome=exits.COULD_NOT_VERIFY)
        return exits.COULD_NOT_VERIFY

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.verb is None:
        parser.print_help()
        return exits.COULD_NOT_VERIFY

    path = args.verb
    if args.verb == "kind":
        if not args.kind_action:
            out("COULD NOT VERIFY: `kind` needs an action: list, check, show.")
            return exits.COULD_NOT_VERIFY
        path = f"kind {args.kind_action}"
        code = cmd_kind(args, out)
    elif args.verb == "item":
        if not args.item_action:
            out("COULD NOT VERIFY: `item` needs an action.")
            return exits.COULD_NOT_VERIFY
        path = f"item {args.item_action}"
        if args.item_action == "check":
            code = cmd_item_check(args, out)
        elif args.item_action in ("add", "ready", "park", "close"):
            code = _carrier_verb(args, out)
        else:
            out(f"COULD NOT VERIFY: `{path}` is built in "
                f"{NOT_YET_BUILT[path]}; this build carries stages "
                f"{STAGES_BUILT}. It is not an unknown verb — it is an "
                "unbuilt one, and the difference matters to whoever is "
                "reading this.")
            code = exits.COULD_NOT_VERIFY
    elif args.verb == "ledger":
        if not args.ledger_action:
            out("COULD NOT VERIFY: `ledger` needs an action: check, add, "
                "rejected --for <item>.")
            return exits.COULD_NOT_VERIFY
        path = f"ledger {args.ledger_action}"
        code = cmd_ledger(args, out)
    else:
        stage = NOT_YET_BUILT.get(path, "a later stage")
        out(f"COULD NOT VERIFY: `{path}` is built in {stage} of wave 1; this "
            f"build carries stages {STAGES_BUILT}.")
        code = exits.COULD_NOT_VERIFY

    # ONE line per invocation, carrying the RESOLVED repo rather than the
    # `--repo` flag: §3.1 says the tool records the writer's repo on every
    # write, and the flag is absent on every invocation that used the cwd.
    firelog.fire(path,
                 repo=getattr(args, "resolved_repo", None) or args.repo,
                 outcome=code,
                 detail=getattr(args, "fire_detail", None))
    return code


def _carrier_verb(args, out) -> int:
    ctx, code = _context(args, out)
    if ctx is None:
        return code
    if args.item_action == "add":
        return verbs.cmd_item_add(args, out, ctx)
    if args.item_action == "ready":
        return verbs.cmd_item_ready(args, out, ctx)
    if args.item_action == "park":
        return verbs.cmd_item_park(args, out, ctx)
    return verbs.cmd_item_close(args, out, ctx)


def cmd_ledger(args, out) -> int:
    ctx, code = _context(args, out)
    if ctx is None:
        return code

    if args.ledger_action == "check":
        return ledger_mod.check_file(ctx.ledger_path, out)

    if args.ledger_action == "rejected":
        # THE GATE. Run before a re-grade, and an ABSENT ledger is COULD NOT
        # VERIFY: "no rejections recorded" and "the file the gate reads is
        # not there" are different answers, and only one of them clears a
        # re-grade.
        parsed, why = ledger_mod.read(ctx.ledger_path)
        if parsed is None:
            out(f"COULD NOT VERIFY: {why}")
            return exits.COULD_NOT_VERIFY
        hits = ledger_mod.rejected_for(parsed, args.for_item)
        if not hits:
            out(f"ledger rejected --for {args.for_item}: NONE recorded — the "
                f"gate RAN and found nothing. {len(parsed.lines)} ledger "
                f"line(s) read.")
            return exits.CLEAN
        out(f"ledger rejected --for {args.for_item}: {len(hits)} recorded. "
            "These approaches were tried and rejected; a re-grade that "
            "proposes one again is re-deriving a settled decision.")
        for h in hits:
            out(f"  approach: {h.slots['approach']}")
            out(f"  why:      {h.slots['why']}")
        return exits.CLEAN

    return verbs.cmd_ledger_add(args, out, ctx)
