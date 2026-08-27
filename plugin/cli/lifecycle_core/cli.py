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

from . import desk as desk_mod
from . import exits, firelog, lanes as lanes_mod, ledger as ledger_mod
from . import declaration as decl
from . import init as init_mod
from . import items as items_mod
from . import migrate as migrate_mod
from . import retire as retire_mod
from . import verbs
from . import workflows as workflows_mod

#: Verbs the design names that this build does not carry yet. Listed rather
#: than omitted: a refusal that says "wave N builds this" is a fact, while an
#: "unknown command" is a lie about the design.
#:
#: `item ratio` LEFT THIS LIST IN THE SCHEMA WAVE. §3.8c placed it — "every
#: verb has a wave" (law 24) — and a verb with a wave is a verb that gets
#: built. `init`, `lane list --json`, `lane new` and now `workflow bind`
#: left it the same way, each named here until it was built rather than
#: omitted, so a caller could tell "this build does not have it" from "you
#: typed it wrong". EMPTY NOW: every verb wave 2 named has one.
NOT_YET_BUILT = {}

#: Which wave this build carries, for the refusal messages above. A build
#: that claimed its own coverage from a hardcoded sentence would say
#: "stages 1-3" forever.
#:
#: `init` and `lane list --json` LEFT THIS DICT the day they were built (the
#: L2a dispatch) — a withdrawn-but-left key would read exactly like a
#: still-true one (`RETIRED_KEYS`'s own reasoning, one file over). `lane new`
#: LEFT IT TOO (the L2b dispatch, this item). `workflow bind` LEFT IT TOO
#: (the L2c dispatch, this item) — `NOT_YET_BUILT` is empty as of this wave.
STAGES_BUILT = "wave 1 stages 1-9, the schema wave (1d), plus wave 2's " \
               "init, lane list --json, lane new, and workflow bind"


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

    if args.kind_action == "sweep":
        if res.declaration is None:
            _report(res, out)
            out("kind sweep: no readable declaration, so nothing could be "
                "swept. An empty sweep reads exactly like a repo with nothing "
                "stray in it.")
            return res.code
        return retire_mod.cmd_kind_sweep(args, out, repo, res.declaration)

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
        f"head-rule: {d.get('head-rule')}")
    ls = d.get("leak-scan") or {}
    out(f"leak-scan: source-scope-foreign-path "
        f"{(ls or {}).get('source-scope-foreign-path') if isinstance(ls, dict) else ls}"
        + (f" — {ls['reason']}" if isinstance(ls, dict) and ls.get("reason")
           else ""))
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

    # AN ITEM-ID BLOCKER'S TARGET, over the CARRIER. Its own verdict beside
    # the others, never a branch inside `check_move_integrity` — that one ends
    # in a bare ok line, and a failure folded into it would take the line with
    # it. Here rather than in `check_file` because the answer needs BOTH homes
    # (a blocker resolves on its target's DONE) and the declared prefix, and
    # no single-home call has both.
    code = exits.worst([code, items_mod.check_blocker_targets(
        items_parsed, done_parsed, out, done_why, prefix=ctx.prefix)])

    # THE DONE HOME'S OWN SHAPE CHECK. It is a KIND with the TOOL as its
    # writer, so shape applies to it exactly as it applies to the live
    # carrier — and until this wave nothing checked it: the done home was
    # parsed for conservation and duplicates by two callers that both ignored
    # `parsed.problems`, so a closed body carrying anything at all passed
    # everything.
    code = exits.worst([code, items_mod.check_done_file(
        ctx.done_path, out, prefix=ctx.prefix)])

    code = exits.worst([code, items_mod.report_conservation(
        items_mod.conservation(items_parsed, done_parsed, done_why), out)])
    return code


class _Parser(argparse.ArgumentParser):
    """argparse's own usage errors, remapped to the verb contract (§3.8c).

    ARGPARSE EXITS 2 ON A USAGE ERROR, and 2 is this system's FINDING. So a
    mistyped flag and a real defect in the repo left the process under the
    same code, and every caller reading exit codes — a lane predicate, a
    gate, a hook — could not tell "the tool found something" from "you typed
    it wrong". Unreadable INPUT is COULD NOT VERIFY (law 1), so it exits 3,
    and the message keeps argparse's `usage:` prefix because that prefix is
    what tells a human which of the two happened.
    """

    def error(self, message):
        self.print_usage(_sys_stderr())
        _sys_stderr().write(
            f"usage: {message}\n"
            "This is UNREADABLE INPUT, not a finding: exit 3. A usage error "
            "and a defect in the repo must never share an exit code — a "
            "caller that reads only the code cannot tell them apart, and one "
            "of them means 'fix your command line'.\n")
        raise SystemExit(exits.COULD_NOT_VERIFY)

    def exit(self, status=0, message=None):
        if message:
            _sys_stderr().write(message)
        raise SystemExit(exits.COULD_NOT_VERIFY if status == 2 else status)


def _sys_stderr():
    return sys.stderr


def build_parser() -> argparse.ArgumentParser:
    p = _Parser(
        prog="lifecycle",
        description="Lifecycle management for everything a repo persists. "
                    "Exit codes: 0 clean, 2 a finding, 3 could not verify.")
    p.add_argument("--repo", help="repo root to act on (default: the work "
                                  "tree containing the current directory)")
    sub = p.add_subparsers(dest="verb")

    ini = sub.add_parser("init", help="wave 2 (§3.8c) — write a fresh "
                                      "repo's declaration and lane stubs")
    ini.add_argument("--lane", action="append", default=[],
                     help="a door to stub a lane for (repeatable; omit for "
                          "an empty declared `lanes` list)")
    ini.add_argument("--id-prefix", dest="id_prefix",
                     help="override the derived id-prefix")
    ini.add_argument("--force", action="store_true",
                     help="overwrite an existing declaration — without it, "
                          "init REFUSES rather than silently overwriting")

    k = sub.add_parser("kind", help="the kind registry")
    ks = k.add_subparsers(dest="kind_action")
    ks.add_parser("list", help="every registered kind, every stage, longhand")
    ks.add_parser("check", help="validate the declaration")
    ks.add_parser("sweep", help="invariant 1: every tracked file resolves to "
                                "a registered kind")
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
    ready.add_argument("ident", nargs="?",
                       help="one item; omit with --head for the whole head")
    ready.add_argument("--head", action="store_true",
                       help="the DERIVED head: every READY item, ordered by "
                            "the declared head-rule. No cap (R22).")

    # `item amend` (lc-27) — the edit path that LEAVES A RECORD. The slot
    # flags are read from `verbs.AMEND_FLAGS` rather than listed again here:
    # a flag this parser accepted and the verb did not read would be silent
    # by construction, which is the shape this whole carrier is built against.
    amend = its.add_parser("amend", help="correct a booked item's slot — an "
                                         "APPENDED dated line supersedes, the "
                                         "earlier one is retained")
    amend.add_argument("ident")
    for _slot, _attr in verbs.AMEND_FLAGS.items():
        amend.add_argument(f"--{_slot}", dest=_attr,
                           help=f"the value that supersedes `{_slot}:`")
    amend.add_argument("--reason", help="the SESSION's prose: why the earlier "
                                        "value was wrong. REQUIRED")
    amend.add_argument("--no-commit", dest="no_commit", action="store_true",
                       help="write the carrier without committing it — a "
                            "caller batching amendments owns that commit")

    # `item promote` (lc-39) — the desk's re-grade, and the ONLY path from
    # NEW to READY. Both flags are verb-checked rather than argparse-required:
    # `--reason ""` is a missing judgment too, and argparse would call that a
    # usage error (exit 3) where it is a refusal (exit 2).
    promote = its.add_parser("promote", help="the desk's re-grade to READY — "
                                             "an ACT, never a derivation")
    promote.add_argument("ident")
    promote.add_argument("--by", help="WHICH DESK judged it. REQUIRED")
    promote.add_argument("--reason", help="the SESSION's prose: why it is "
                                          "decision-complete. REQUIRED")
    promote.add_argument("--no-commit", dest="no_commit", action="store_true",
                         help="write the carrier without committing it — a "
                              "caller batching promotions owns that commit")

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

    its.add_parser("ratio", help="capture against drain — the FLOW alarm "
                                 "(R22); a ratio, never a size")

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

    lane = sub.add_parser("lane", help="the generated router")
    lanes_sub = lane.add_subparsers(dest="lane_action")
    ll = lanes_sub.add_parser("list", help="every repo in the roster, every "
                                          "lane, every trigger state, LONGHAND")
    ll.add_argument("--no-run", dest="no_run", action="store_true",
                    help="parse the lanes but do NOT execute their "
                         "predicates; each state is then COULD NOT VERIFY, "
                         "never quiet")
    ll.add_argument("--json", action="store_true",
                    help="wave 2 (§3.8c) — one JSON document on stdout "
                         "instead of the longhand board; same exit code, "
                         "same finding set (never a rendering-only change "
                         "to the verdict)")
    lreg = lanes_sub.add_parser("register", help="put a repo on the roster — "
                                                 "the router's input")
    lreg.add_argument("repo_path", nargs="?",
                      help="the repo to register (default: the cwd's)")
    lreg.add_argument("--dry-run", dest="dry_run", action="store_true")
    lnew = lanes_sub.add_parser("new", help="wave 2 (§3.8c) — a lane file "
                                            "from the format, as a STUB a "
                                            "human then fills. Does NOT "
                                            "declare it in this repo's "
                                            "`lanes` list")
    lnew.add_argument("door", help="the lane's name — a door the operator "
                                   "types, never a command")
    lnew.add_argument("--force", action="store_true",
                      help="overwrite an existing lane body — without it, "
                           "`lane new` REFUSES rather than silently "
                           "overwriting")

    wf = sub.add_parser("workflow", help="wave 2 (§3.8b/§3.11) — the "
                                         "plugin's template registry and "
                                         "this repo's bindings into it")
    wf_sub = wf.add_subparsers(dest="workflow_action")
    wbind = wf_sub.add_parser(
        "bind", help="bind a `template-bindings` entry to a plugin "
                     "registry template, filling every required slot")
    wbind.add_argument("template_id", help="the template id — the "
                                           "registry file's stem under "
                                           "plugin/workflows/")
    wbind.add_argument("--set", dest="set", action="append", default=[],
                       metavar="SLOT=VALUE",
                       help="fill one slot at bind time (repeatable); any "
                            "declared slot not filled is written UNKNOWN "
                            "— an explicit unanswered slot, never a "
                            "default")
    wbind.add_argument("--force", action="store_true",
                       help="overwrite an existing binding for this "
                            "template — without it, `workflow bind` "
                            "REFUSES rather than silently overwriting")

    desk = sub.add_parser("desk", help="the delegation-state verb")
    desk_sub = desk.add_subparsers(dest="desk_action")
    dstate = desk_sub.add_parser(
        "state", help="record this desk's turn-end state: REPORTED "
                      "<msg-id> | WAITING-ON <lane|peer> --horizon <t> | "
                      "BLOCKED <named> | DONE. ALWAYS overwrites — one "
                      "current state per desk, no history")
    dstate.add_argument("value", help="REPORTED | WAITING-ON | BLOCKED | "
                                      "DONE — the closed vocabulary; "
                                      "anything else is a refusal")
    dstate.add_argument("argument", nargs="?",
                        help="the value's own argument: the message id "
                             "(REPORTED), the lane or peer (WAITING-ON), "
                             "the named blocker (BLOCKED); DONE takes none")
    dstate.add_argument("--horizon", help="required with WAITING-ON")
    dstate.add_argument("--desk", help="explicit desk identity; overrides "
                                       "CLAUDE_CODE_SESSION_ID (default)")

    sub.add_parser("retire", help="the lifecycle walk over every registered "
                                  "kind — homes re-listed, growth read as FLOW")
    sub.add_parser("audit", help="the same walk, READ-ONLY: every check's "
                                 "three-answer result, the laws scope audit, "
                                 "the judgment register's fire-rate")

    mig = sub.add_parser("migrate", help="the old carrier → ITEMS.md, "
                                         "ITEMS-DONE.md and a report; or a "
                                         "SCHEMA bump. DRY RUN by default")
    mig.add_argument("--from", dest="from_carrier",
                     help="the old carrier (default: BACKLOG.md). THE CARRIER "
                          "SOURCE — never the schema path; the two never "
                          "share a spelling (§3.8c)")
    mig.add_argument("--from-done", dest="from_done",
                     help="the old closure home (default: BACKLOG-DONE.md)")
    mig.add_argument("--schema-from", dest="schema_from", type=int,
                     help="THE SCHEMA PATH: migrate this repo's declaration "
                          "and carriers FROM schema <n> to this build's. A "
                          "different question from --from, so a different "
                          "spelling")
    mig.add_argument("--report", help="where the classification report is "
                                      "written")
    mig.add_argument("--apply", action="store_true",
                     help="WRITE the schema migration. Without it every "
                          "--schema-from run is a dry run that writes nothing")
    mig.add_argument("--force", action="store_true",
                     help="overwrite an existing ITEMS.md/ITEMS-DONE.md")
    mig.add_argument("--merge", action="store_true",
                     help="APPEND this source to the successor homes instead "
                          "of producing them: existing entries keep their ids "
                          "and their slots, new ids come from the carrier's "
                          "own id space, and conservation is re-checked "
                          "against what is on disk. An absent or empty "
                          "ITEMS.md is an ordinary first migration here, not "
                          "an error. Merge N carriers with N invocations, one "
                          "--from and one --from-done each. NOT --force, "
                          "which REPLACES the carrier with a re-derivation")
    mig.add_argument("--report-only", dest="report_only", action="store_true",
                     help="re-render the REPORT and touch no carrier. R3 has "
                          "the report's findings enter the carrier as items "
                          "and the report then point at their ids, which is "
                          "circular unless the report can be re-rendered "
                          "after the intake")
    return p


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    out = lambda s: sys.stdout.write(f"{s}\n")  # noqa: E731

    if "--test" in argv:
        from . import roster as roster_mod
        code = roster_mod.cmd_test(out, list_only="--list" in argv)
        firelog.fire("--test", outcome=code)
        return code

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.verb is None:
        parser.print_help()
        return exits.COULD_NOT_VERIFY

    path = args.verb
    if args.verb == "init":
        repo, why = resolve_repo(args.repo)
        if repo is None:
            out(f"COULD NOT VERIFY: {why}")
            return exits.COULD_NOT_VERIFY
        args.resolved_repo = str(repo)
        code = init_mod.cmd_init(args, out, repo)
    elif args.verb == "kind":
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
        elif args.item_action in ("add", "amend", "promote", "ready", "park",
                                  "close", "ratio"):
            code = _carrier_verb(args, out)
        else:
            stage = NOT_YET_BUILT.get(path, "a later wave")
            out(f"COULD NOT VERIFY: `{path}` is built in {stage}; this build "
                f"carries {STAGES_BUILT}. It is not an unknown verb — it is "
                "an unbuilt one, and the difference matters to whoever is "
                "reading this.")
            code = exits.COULD_NOT_VERIFY
    elif args.verb in ("retire", "audit"):
        path = args.verb
        code = _walk_verb(args, out)
    elif args.verb == "ledger":
        if not args.ledger_action:
            out("COULD NOT VERIFY: `ledger` needs an action: check, add, "
                "rejected --for <item>.")
            return exits.COULD_NOT_VERIFY
        path = f"ledger {args.ledger_action}"
        code = cmd_ledger(args, out)
    elif args.verb == "lane":
        if not args.lane_action:
            out("COULD NOT VERIFY: `lane` needs an action: list, register, "
                "new.")
            return exits.COULD_NOT_VERIFY
        path = f"lane {args.lane_action}"
        if args.lane_action == "register":
            code = lanes_mod.cmd_lane_register(args, out)
        elif args.lane_action == "new":
            repo, why = resolve_repo(args.repo)
            if repo is None:
                out(f"COULD NOT VERIFY: {why}")
                return exits.COULD_NOT_VERIFY
            args.resolved_repo = str(repo)
            code = lanes_mod.cmd_lane_new(args, out, repo)
        else:
            code = lanes_mod.cmd_lane_list(args, out)
    elif args.verb == "workflow":
        if not args.workflow_action:
            out("COULD NOT VERIFY: `workflow` needs an action: bind.")
            return exits.COULD_NOT_VERIFY
        path = f"workflow {args.workflow_action}"
        if args.workflow_action == "bind":
            repo, why = resolve_repo(args.repo)
            if repo is None:
                out(f"COULD NOT VERIFY: {why}")
                return exits.COULD_NOT_VERIFY
            args.resolved_repo = str(repo)
            code = workflows_mod.cmd_workflow_bind(args, out, repo)
        else:
            out(f"COULD NOT VERIFY: `{path}` is not a recognized workflow "
                "action.")
            code = exits.COULD_NOT_VERIFY
    elif args.verb == "migrate":
        path = "migrate"
        code = cmd_migrate(args, out)
    elif args.verb == "desk":
        if not args.desk_action:
            out("COULD NOT VERIFY: `desk` needs an action: state.")
            return exits.COULD_NOT_VERIFY
        path = f"desk {args.desk_action}"
        if args.desk_action == "state":
            # NOT `resolve_repo`'s own COULD-NOT-VERIFY path: a desk is not
            # scoped to one repo, so being outside a git work tree with no
            # `--repo` is not an error here — only the reporting of the
            # `delegation` field (best-effort) depends on a repo resolving.
            repo, _why = resolve_repo(args.repo)
            args.resolved_repo = str(repo) if repo else None
            code = desk_mod.cmd_desk_state(args, out, repo)
        else:
            out(f"COULD NOT VERIFY: `{path}` is not a recognized desk "
                "action.")
            code = exits.COULD_NOT_VERIFY
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
    if args.item_action == "amend":
        return verbs.cmd_item_amend(args, out, ctx)
    if args.item_action == "promote":
        return verbs.cmd_item_promote(args, out, ctx)
    if args.item_action == "ready":
        if getattr(args, "head", False):
            return verbs.cmd_item_head(args, out, ctx)
        if not args.ident:
            out("COULD NOT VERIFY: `item ready` needs an item id, or `--head` "
                "for the whole derived head. Refusing rather than picking one "
                "for you: an id-less run that printed the head anyway would "
                "answer a question nobody asked.")
            return exits.COULD_NOT_VERIFY
        return verbs.cmd_item_ready(args, out, ctx)
    if args.item_action == "ratio":
        return verbs.cmd_item_ratio(args, out, ctx)
    if args.item_action == "park":
        return verbs.cmd_item_park(args, out, ctx)
    return verbs.cmd_item_close(args, out, ctx)


def _walk_verb(args, out) -> int:
    """`retire` and `audit` — one walk, two verbs over it."""
    repo, why = resolve_repo(args.repo)
    if repo is None:
        out(f"COULD NOT VERIFY: {why}")
        return exits.COULD_NOT_VERIFY
    args.resolved_repo = str(repo)
    res = decl.read(repo)
    if res.declaration is None:
        _report(res, out)
        out(f"{args.verb}: no readable declaration, so the walk had no "
            "registry to walk. An empty walk reads exactly like a repo whose "
            "every kind is in order.")
        return res.code
    if args.verb == "retire":
        return retire_mod.cmd_retire(args, out, repo, res.declaration)
    return retire_mod.cmd_audit(args, out, repo, res.declaration)


def cmd_migrate(args, out) -> int:
    """Stage 9. A DRY RUN: it WRITES the successor files and READS the old
    carrier, and it never edits, moves or deletes the old one (D-e)."""
    ctx, code = _context(args, out)
    if ctx is None:
        return code
    return migrate_mod.run(args, out, ctx)


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
