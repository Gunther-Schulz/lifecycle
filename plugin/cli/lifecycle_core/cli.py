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
from . import records as records_mod
from . import retire as retire_mod
from . import verbs
from . import verify as verify_mod
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

    # THE DIGEST IS THE WHOLE OUTPUT, not a section of the wall form (lc-219).
    # It exists to be INJECTED in front of a session, and the header above —
    # schema, goals, lanes, the leak-scan paragraph — is exactly the bulk that
    # makes a block stop being read. One line per kind and nothing else.
    if getattr(args, "digest", False):
        for line in decl.render_digest(d, repo):
            out(line)
        if res.findings or res.unverified:
            out("")
            _report(res, out)
        return res.code

    # lc-174 — WHAT THE REPO IS, beside `--digest`'s what-it-holds: kind
    # count, writer split, undeclared-stage count. Same shape as the digest
    # branch above (a pointer/readout, findings surfaced beside it rather
    # than swallowed) rather than a special-cased always-CLEAN exit: the
    # counting itself never adds a finding of its own, so a repo whose
    # declaration is otherwise clean reports CLEAN here too, and one with
    # unrelated validation findings reports them exactly as `--digest`
    # already does — one verb, one exit-code contract, not two.
    if getattr(args, "structure", False):
        for line in decl.render_structure(d):
            out(line)
        if res.findings or res.unverified:
            out("")
            _report(res, out)
        return res.code

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


def cmd_item_check(args, out, err=None) -> int:
    ctx, code = _context(args, out)
    if ctx is None:
        return code

    # `--staged` IS A DIFFERENT QUESTION, not a filter over this one. The
    # plain check asks what is wrong with the carrier; the staged check asks
    # what THIS COMMIT made wrong. The cross-home checks below (move
    # integrity, blocker targets, conservation) answer neither — they are
    # about the two homes' relationship, which a staged diff of one body at a
    # time cannot see — so they stay on the plain path rather than being run
    # over index text that has no matching second home.
    if getattr(args, "staged", False):
        if err is None:
            err = lambda s: sys.stderr.write(f"{s}\n")  # noqa: E731
        return items_mod.check_staged(
            ctx.repo,
            [(items_mod.rel_to(ctx.repo, ctx.items_path), ctx.items_path,
              items_mod.check_file, ctx.prefix),
             (items_mod.rel_to(ctx.repo, ctx.done_path), ctx.done_path,
              items_mod.check_done_file, ctx.prefix)],
            out, err)

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

    # THE GRAPH, beside the EDGES above (lc-193). `check_blocker_targets`
    # asks whether each blocker's target exists; this asks whether the graph
    # those edges form can ever drain. Both are needed: lc-A blocked-by lc-B
    # and lc-B blocked-by lc-A both RESOLVE, neither dangles, neither is
    # dropped, and both wait forever while the per-edge check reports CLEAN.
    #
    # WIRED HERE BY THE DESK, not by the lane that built it: cli.py was
    # outside lc-193's write set, and it surfaced the gap rather than
    # scoping it in. An unwired check is the defect this session already
    # booked once (lc-237 — a declared trigger predicate that nothing
    # evaluates, firing unread), and shipping a second instance of it in the
    # same repo on the same day would be minting the class we just recorded.
    code = exits.worst([code, items_mod.check_blocker_graph(
        items_parsed, out, ctx.prefix)])

    # THE REACH LIMIT, PRINTED RATHER THAN LEFT IN A DOCSTRING. Item-id
    # EDGES need the declared `id-prefix` to be told from prose at all, so
    # without one the traversal sees no edges: no cycle and no multi-hop
    # chain, while a length-ONE unclearable terminal still reports normally.
    # That narrower-but-always-checkable shape is the right call — it keeps
    # real coverage where a blanket COULD NOT VERIFY would keep none — but
    # its silence would otherwise read as a clean graph verdict, which is a
    # check reporting CLEAN over a population it never examined. The
    # function's own docstring hands this to its caller; this is the caller.
    if not ctx.prefix:
        out("blocker graph: REACH LIMITED — this repo declares no "
            "`id-prefix`, so item-id edges cannot be told from prose and "
            "the traversal saw none. Cycles and multi-hop chains were NOT "
            "checked; a length-one unclearable terminal still was. This is "
            "a narrower answer, never a clean one.")

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


def cmd_item_repair(args, out) -> int:
    """`item repair --shape` (lc-129) — the MECHANICAL half of hand damage.

    TWO HALVES, AND THE SPLIT IS THE DESIGN. It joins wrapped slot values and
    moves appended lines below the fixed slots — repairs where every word
    survives — and it LISTS missing slots, unknown slots, closed-still-blocked
    bodies and unjoinable continuations, whose repair would mean writing a
    value nobody wrote. The listed bodies are not touched; `items.repair_shape`
    carries the reasoning at the transform.

    THE EXIT CONTRACT, in this repo's three answers: CLEAN when nothing is left
    for judgment — the mechanical repairs landed, or there was nothing to
    repair; FINDING when anything was LISTED, including a run that also
    repaired, because the listing is the part a caller must act on; COULD NOT
    VERIFY when a home could not be read, naming which.

    IT COMMITS ITS WRITE OR SAYS `NOT COMMITTED` (the lc-41 ruling): every
    carrier-WRITING verb answers the commit question in the same closed
    vocabulary, and a run that wrote nothing says so rather than leaving a
    reader to tell silence from a failed commit.
    """
    ctx, code = _context(args, out)
    if ctx is None:
        return code

    code = exits.CLEAN
    written = []
    judgments = []
    for path in (ctx.items_path, ctx.done_path):
        if not path.exists():
            out(f"COULD NOT VERIFY: no carrier at {path}. An absent file and "
                "a clean one are not the same answer, and neither is a "
                "repair.")
            code = exits.worst([code, exits.COULD_NOT_VERIFY])
            continue
        try:
            with items_mod.carrier_lock(path):
                before = path.read_text(encoding="utf-8")
                res = items_mod.repair_shape(before, prefix=ctx.prefix)
                if res.text != before:
                    path.write_text(res.text, encoding="utf-8")
                    written.append(path)
        except (OSError, UnicodeDecodeError) as exc:
            out(f"COULD NOT VERIFY: {path} could not be read or written "
                f"({exc!r}).")
            code = exits.worst([code, exits.COULD_NOT_VERIFY])
            continue

        for ident, slot, lineno, joined in res.joins:
            out(f"joined: {path.name}:{lineno} {ident} `{slot}:` — "
                f"{joined} continuation line(s) folded back into the value. "
                "Every word survives; only the line breaks are gone.")
        for ident, name, lineno in res.moves:
            out(f"moved: {path.name}:{lineno} {ident} `{name}:` — below the "
                "fixed slots, in file order, so the block reads as what it "
                "said and then what it now says.")
        judgments += [(path.name, j) for j in res.judgments]

    for name, (ident, klass, detail) in judgments:
        out(f"JUDGMENT [{klass}] {name} {ident}: {detail} — LISTED, not "
            "repaired. Supplying this is a desk decision; a verb that guessed "
            "it would put a value nobody wrote into the carrier under the "
            "tool's own authority.")
    if judgments:
        out(f"item repair --shape: {len(judgments)} body/bodies left for the "
            "desk pass.")
        code = exits.worst([code, exits.FINDING])

    if written:
        msg = (f"item repair --shape: {len(written)} carrier(s) reshaped "
               "(wrapped values joined, appended lines moved below the fixed "
               "slots)")
        code = exits.worst([code, verbs.commit_paths(
            ctx, written, msg, out,
            skip=getattr(args, "no_commit", False),
            what="the shape repair")])
    else:
        out("NOT COMMITTED: there is nothing to commit — no carrier's shape "
            "changed. The files are as this run found them.")
    return code


def cmd_item_waves(args, out) -> int:
    """`item waves` (lc-123) — the item→lane join, DERIVED from write-sets.

    The routing corpus makes a derived join over write-boundaries the source
    of a dispatch's item→lane mapping, and until this verb nothing computed
    one: every drain paid a manual pass over prose or fell back to the
    identity mapping nobody chose (measured 1.05 items/lane all-time for this
    carrier). The join is mechanical, so it is the tool's; the sizing and the
    tier are not, so they stay the desk's.

    THE POPULATION IS `item ready --head`'s OWN PREDICATE, called here rather
    than restated: `_blocker_state` plus the UNKNOWN-slot refusal, the exact
    pair the head folds into `SCHEDULABLE`. A second spelling of
    schedulability would be a second board, and the two would answer
    differently the first time either moved — which is why this reaches into
    `verbs` for a private helper instead of re-deriving the cheap half.
    """
    ctx, code = _context(args, out)
    if ctx is None:
        return code
    parsed, why = verbs._load(ctx.items_path)
    if parsed is None:
        out(f"COULD NOT VERIFY: {why}")
        return exits.COULD_NOT_VERIFY
    done_parsed, done_why = verbs._load(ctx.done_path)

    ready = [it for it in parsed.items if it.grade == "READY"]
    schedulable, excluded = [], []
    for it in ready:
        unknown = items_mod.unknown_slots_of(it)
        state, st_code, _note = verbs._blocker_state(it, ctx, parsed,
                                                     done_parsed, done_why)
        if state.startswith("UNBLOCKED") and not unknown:
            schedulable.append(it)
            continue
        # THE GATE'S OWN VERDICT TRAVELS, never a fresh one: a broken blocker
        # predicate is a FINDING wherever it is read, and a planning verb that
        # swallowed it would report a tidy plan over a carrier the head calls
        # red.
        code = exits.worst([code, st_code])
        excluded.append((it.ident, state + (
            "; UNKNOWN slot(s): " + ", ".join(unknown) if unknown else "")))

    return exits.worst([code, items_mod.report_waves(
        schedulable, out, ready_n=len(ready), live_n=len(parsed.items),
        excluded=excluded, grouped=getattr(args, "grouped", False))])


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
    kl = ks.add_parser("list",
                       help="every registered kind, every stage, longhand")
    # MUTUALLY EXCLUSIVE ON PURPOSE, and it is a dissolved question rather
    # than a decided one. `--digest` and `--structure` answer different
    # questions (what the repo HOLDS, one line per kind, versus what it IS,
    # three counts), and each branch below RETURNS, so passing both would
    # silently give whichever branch the reader happens to reach first — a
    # precedence nobody chose, invisible in the output, and re-decided by
    # whoever next moves a block. argparse refusing the combination means
    # the ordering of those two branches can never become load-bearing.
    kview = kl.add_mutually_exclusive_group()
    kview.add_argument("--digest", action="store_true",
                    help="ONE LINE PER KIND — the map a session holds: home, "
                         "member count, newest member, and `[session-read]` "
                         "on kinds no verb reads for you. A pointer surface, "
                         "never an authority on content (lc-219)")
    kview.add_argument("--structure", action="store_true",
                    help="THREE COUNTS, each with its denominator — kinds "
                         "registered, the writer split (verb-written / "
                         "writer:session / other), and how many leave a "
                         "stage undeclared. What the repo IS, beside "
                         "`--digest`'s what-it-holds (lc-174)")
    ks.add_parser("check", help="validate the declaration")
    ks.add_parser("sweep", help="invariant 1: every tracked file resolves to "
                                "a registered kind")
    show = ks.add_parser("show", help="one kind, every stage")
    show.add_argument("name")

    it = sub.add_parser("item", help="the item carrier")
    its = it.add_subparsers(dest="item_action")
    chk = its.add_parser("check",
                         help="the shape check over the carrier file")
    chk.add_argument("--staged", action="store_true",
                     help="read the carriers from the git INDEX and report "
                          "only findings this staged edit INTRODUCED — the "
                          "commit-time gate. Findings already at HEAD are "
                          "counted, not reported, so a repo that carries "
                          "some can still commit.")

    rep = its.add_parser("repair",
                         help="the MECHANICAL half of hand-written damage: "
                              "wrapped values joined, appended lines moved "
                              "below the fixed slots. Never invents — missing "
                              "slots, unknown slots and closed-still-blocked "
                              "bodies are LISTED for a desk pass")
    rep.add_argument("--shape", action="store_true", required=True,
                     help="REQUIRED, and it is the verb's whole scope: this "
                          "repairs SHAPE. A bare `item repair` would read as "
                          "a verb that repairs whatever it finds, which is "
                          "the invention the design refuses.")
    rep.add_argument("--no-commit", dest="no_commit", action="store_true",
                     help="skip the commit (a batching caller owns it)")

    slots = its.add_parser("slots", help="one item's effective fixed slots")
    slots.add_argument("ident")
    slots.add_argument("--json", action="store_true",
                       help="one JSON object instead of plain slot lines")

    add = its.add_parser("add", help="the ONLY admission path (the intake join)")
    add.add_argument("--requirement", help="why, one line + a record pointer")
    add.add_argument("--goal", help="one of the repo's declared goals")
    add.add_argument("--write-set", dest="write_set",
                     help="comma-separated paths/venues, or NONE, or UNKNOWN. "
                          "A TRAILING SLASH marks a directory entry — `test/` "
                          "means every file under it, `test` means one file "
                          "of that name; the slash is the only directory form "
                          "the wave join reads, and it reads the slot rather "
                          "than the working tree")
    add.add_argument("--done-criterion", dest="done_criterion")
    add.add_argument("--evidence")
    add.add_argument("--blocked-by", dest="blocked_by",
                     help="TYPED: `<prefix>-<n>` | `decision <q>` | "
                          "`evidence <predicate>` | `external <event>` | "
                          "NONE")
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
    add.add_argument("--not-derivable", dest="not_derivable", help="why the question is NOT DERIVABLE from the record — required with a `decision` blocker (lc-169): which precedent, ledger entry, audit or declaration you looked for and did not find, or that the question is constitutively the operator's")
    add.add_argument("--blocker-exercise", dest="blocker_exercise", help="the exercise record for an `evidence` blocker (lc-175): the TWO CONSTRUCTED ARMS showing the predicate answers both ways — a case it must accept and one it must refuse. The live booking exit is added by the tool, which ran it; the arms are yours, because a verb that synthesised one would be grading its own plant")
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
    ready.add_argument("--goal",
                       help="restrict the listing to entries carrying this "
                            "goal (lc-16). A goal the declaration does not "
                            "carry is COULD NOT VERIFY, never an empty "
                            "listing: an undeclared goal and a declared one "
                            "nobody has used both return nothing, and they "
                            "are different answers")

    waves = its.add_parser("waves", help="the item→lane JOIN over the "
                                         "schedulable READY set: write-set "
                                         "overlap, file-granular. Reports "
                                         "the mapping, decides no sizing "
                                         "and no tier")
    waves.add_argument("--grouped", action="store_true",
                       help="APPEND a partition beside the join: each item "
                            "in the group of its write-set's most-frequent "
                            "entry, plus every cross-group shared file as a "
                            "SERIALIZE warning. A plan, never a permission — "
                            "the lanes above it stay the truthful answer")

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
    park.add_argument("--not-derivable", dest="not_derivable", help="why the question is NOT DERIVABLE from the record — required with a `decision` blocker (lc-169): which precedent, ledger entry, audit or declaration you looked for and did not find, or that the question is constitutively the operator's")
    park.add_argument("--blocker-exercise", dest="blocker_exercise", help="the exercise record for an `evidence` blocker (lc-175): the TWO CONSTRUCTED ARMS showing the predicate answers both ways — a case it must accept and one it must refuse. The live booking exit is added by the tool, which ran it; the arms are yours, because a verb that synthesised one would be grading its own plant")

    close = its.add_parser("close", help="the MOVE: append, delete, commit")
    close.add_argument("ident")
    close.add_argument("--drop", action="store_true",
                       help="close as DROPPED rather than DONE")
    close.add_argument("--reason", help="the SESSION's prose. On a DONE close "
                                        "it lands on the MOVED BODY as "
                                        "`closed-reason: <date> <text>`; on "
                                        "--drop it is the ledger `dropped:` "
                                        "line and is REQUIRED there")
    close.add_argument("--ref", help="the commit(s) this item closed at, "
                                     "comma-separated. Each is verified "
                                     "against this repo; on a DONE close they "
                                     "land on the moved body as `closed-ref:`. "
                                     "OPTIONAL — a closure legitimately has "
                                     "no ref, and the verb says so when none "
                                     "was given")
    close.add_argument("--no-commit", dest="no_commit", action="store_true")

    compact = its.add_parser("compact",
                             help="the DONE BODY's declared exit: collapse "
                                  "one closed body to a ledger line, the body "
                                  "kept recoverable at a BLOB pin")
    compact.add_argument("ident")
    compact.add_argument("--no-commit", dest="no_commit", action="store_true")

    supers = its.add_parser("supersede-closure",
                            help="APPEND a forward pointer to a CLOSED body "
                                 "(lc-120) — nothing existing is rewritten; "
                                 "`item amend` still refuses a closed body "
                                 "and this does not soften it")
    supers.add_argument("ident")
    supers.add_argument("--ref", required=True,
                        help="the commit that carries the later record — "
                             "verified against this repo, because a pointer "
                             "onto a body that has stopped being edited is "
                             "permanent and a dangling one reads exactly like "
                             "a good one")
    supers.add_argument("--line", required=True,
                        help="the SESSION's one line saying what was "
                             "superseded. REQUIRED and with no default: a "
                             "generated sentence would be a paraphrase with "
                             "nobody's judgment behind it")
    supers.add_argument("--no-commit", dest="no_commit", action="store_true")

    its.add_parser("ratio", help="capture against drain — the FLOW alarm "
                                 "(R22); a ratio, never a size")

    its.add_parser("statusline", help="ONE line fit for a per-prompt render "
                                      "(lc-45) — a cheap single-pass "
                                      "approximation, never `_load`")

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
                                            "human then fills. REGISTERS "
                                            "its own output: the name is "
                                            "appended to this repo's "
                                            "`lanes` list in the same run "
                                            "(lc-14)")
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

    ver = sub.add_parser("verify", help="run the laws file's declared `## "
                                        "Verify` block and assert how many "
                                        "commands EXECUTED vs registered")
    ver.add_argument("--list", action="store_true",
                     help="print the registered commands without running them")
    ver.add_argument("--timeout", type=int, default=900,
                     help="per-command timeout in seconds (default 900); a "
                          "timeout is DID NOT RUN, never a failure")

    rec = sub.add_parser("record", help="the investigation record's FORM "
                                        "(lc-156) — slots, line shape, route "
                                        "vocabulary, and the closure gate")
    rec_sub = rec.add_subparsers(dest="record_action")
    rchk = rec_sub.add_parser("check", help="grade every record at the "
                                            "investigation home; an "
                                            "unreadable record is COULD NOT "
                                            "VERIFY, never clean")
    rchk.add_argument("--dir", dest="dir",
                      help="grade this directory instead of the XDG home — "
                           "the seam fixtures and the roster's plants run "
                           "through, so the check is exercisable without "
                           "writing to the machine's live records")

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
    mig.add_argument("--retire-source", dest="retire_source",
                     action="store_true",
                     help="DELETE the source carrier after the successor "
                          "homes are written, and write a deletion record "
                          "into the declared laws file. Refuses unless the "
                          "source is committed, the declaration names a laws "
                          "file that exists, every anchor pointing at the "
                          "source carries its blob pin, and the run writes "
                          "successor state. Without it a writing run FREEZES "
                          "the source with a banner instead")
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
        elif args.item_action == "repair":
            code = cmd_item_repair(args, out)
        elif args.item_action == "slots":
            ctx, code = _context(args, out)
            if ctx is not None:
                code = items_mod.cmd_item_slots(args, out, ctx.items_path)
        elif args.item_action == "waves":
            code = cmd_item_waves(args, out)
        elif args.item_action in ("add", "amend", "promote", "ready", "park",
                                  "close", "compact", "ratio", "statusline",
                                  "supersede-closure"):
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
    elif args.verb == "verify":
        path = "verify"
        code = _verify_verb(args, out)
    elif args.verb == "record":
        if not args.record_action:
            out("COULD NOT VERIFY: `record` needs an action: check.")
            return exits.COULD_NOT_VERIFY
        path = f"record {args.record_action}"
        code = records_mod.cmd_record_check(args, out)
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
        # lc-31: argparse's plain (non-`append`) dest OVERWRITES on a
        # repeated `--from`, so `--from A.md --from B.md` silently keeps
        # only B.md — the caller believes two sources were read and one
        # was. Counted from the RAW argv rather than from `args.from_carrier`
        # (which by then holds only the survivor and cannot say how many
        # there were), and gated to `migrate` because `--from` is that
        # verb's own flag alone (grepped: no other subparser declares it).
        # Distinct from `--merge`, which reads a SECOND INVOCATION's source;
        # this is one invocation naming two.
        from_count = sum(1 for a in argv
                         if a == "--from" or a.startswith("--from="))
        if from_count > 1:
            out("FINDING [migrate_repeated_from] one --from per invocation; "
                "use --merge for a second source")
            code = exits.FINDING
        else:
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
    """The carrier verbs — ONE BRANCH EACH, and no default (lc-146).

    This used to END in an unguarded `return verbs.cmd_item_close(...)`, and
    it was safe only because the CALLER's action tuple happened to admit
    nothing without a branch here. So the guard was a property of a tuple
    somebody else edits while the risk — a two-file MOVE — sat in this
    function, and an action added there would have run CLOSE under its own
    name with nothing at either site saying so.

    `close` therefore names itself like every other action, and an action
    this dispatch does not carry is COULD NOT VERIFY. The caller and this
    function can still disagree; what changed is that they now disagree
    LOUDLY, on the first run, rather than by moving a body.
    """
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
        # A GOAL FILTER OVER ONE NAMED ITEM ANSWERS A QUESTION NOBODY ASKED,
        # and the two readings of it disagree: "show me this item if it
        # carries that goal" and "show me that goal's items, starting here".
        # Refusing is the only answer that cannot be the wrong one — the same
        # reasoning as the id-less run below.
        if args.ident and getattr(args, "goal", None):
            out("COULD NOT VERIFY: `item ready <ident> --goal` names one item "
                "AND a filter over many. Drop the id for the goal's listing, "
                "or drop --goal for that one item.")
            return exits.COULD_NOT_VERIFY
        if getattr(args, "head", False) or getattr(args, "goal", None):
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
    if args.item_action == "statusline":
        return verbs.cmd_item_statusline(args, out, ctx)
    if args.item_action == "park":
        return verbs.cmd_item_park(args, out, ctx)
    if args.item_action == "compact":
        return retire_mod.cmd_item_compact(args, out, ctx)
    if args.item_action == "close":
        return verbs.cmd_item_close(args, out, ctx)
    if args.item_action == "supersede-closure":
        return verbs.cmd_item_supersede_closure(args, out, ctx)
    out(f"COULD NOT VERIFY: `item {args.item_action}` reached the carrier "
        "verbs with no branch of its own. The caller admits it and this "
        "dispatch does not carry it; refusing is the only answer that does "
        "not act on a guess about which verb was meant, and the guess this "
        "function used to make was `close` — a two-file move.")
    return exits.COULD_NOT_VERIFY


def _verify_verb(args, out) -> int:
    """`verify` — the declared block, run and COUNTED (lc-157 mechanism #1).

    Resolution is the walk verbs' own, deliberately: a verb that resolved the
    repo differently would answer about a different repo under the same name,
    which is the class this plugin exists to refuse.
    """
    repo, why = resolve_repo(args.repo)
    if repo is None:
        out(f"COULD NOT VERIFY: {why}")
        return exits.COULD_NOT_VERIFY
    args.resolved_repo = str(repo)
    res = decl.read(repo)
    if res.declaration is None:
        _report(res, out)
        out("verify: no readable declaration, so the laws file could not be "
            "resolved. Nothing ran, and that is not a clean verify.")
        return res.code
    return verify_mod.cmd_verify(args, out, repo, res.declaration)


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
    """Stage 9. It WRITES the successor files, READS the old carrier, and
    DISPOSES of it (lc-86) — UNTOUCHED on a run that writes no successor
    state, FROZEN by default, DELETED under `--retire-source`. Brief D-e's
    "it never edits, moves or deletes the old one" was true of every build
    before lc-86 and is false now, deliberately; `migrate.py`'s module
    docstring carries the reason and the three outcomes in full."""
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
