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

from . import exits, firelog
from . import declaration as decl
from . import items as items_mod

#: Verbs the design names that this build does not carry yet. Listed rather
#: than omitted: a refusal that says "wave 1 stage N builds this" is a fact,
#: while an "unknown command" is a lie about the design.
NOT_YET_BUILT = {
    "item add": "stage 4",
    "item ready": "stage 5",
    "item park": "stage 5",
    "item close": "stage 5",
    "item ratio": "stage 5",
    "ledger": "stage 6",
    "lane": "stage 7",
    "migrate": "stage 9",
    "--test": "stage 8",
}


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


def cmd_item_check(args, out) -> int:
    repo, why = resolve_repo(args.repo)
    if repo is None:
        out(f"COULD NOT VERIFY: {why}")
        return exits.COULD_NOT_VERIFY
    res = decl.read(repo)
    if res.declaration is None:
        _report(res, out)
        out("item check: the carrier's home is named by the declaration, and "
            "there is no readable declaration to name it.")
        return res.code
    home = res.declaration.get("kinds", {}).get("items", {})
    home = home.get("home") if isinstance(home, dict) else None
    if not isinstance(home, str) or not home.strip():
        out("FINDING [kind_stage_undeclared] the `items` kind declares no "
            "`home`, so there is no file to check.")
        return exits.FINDING
    return items_mod.check_file(repo / home, out,
                                prefix=res.declaration.get("id-prefix"))


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
    for verb in ("add", "ready", "park", "close", "ratio"):
        its.add_parser(verb, help="(not built in this build)")

    sub.add_parser("ledger", help="(not built in this build)")
    lane = sub.add_parser("lane", help="(not built in this build)")
    lane.add_subparsers(dest="lane_action").add_parser("list")
    sub.add_parser("migrate", help="(not built in this build)")
    return p


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    out = lambda s: sys.stdout.write(f"{s}\n")  # noqa: E731

    if "--test" in argv:
        out("COULD NOT VERIFY: `--test` is the refusal-table roster and is "
            "built in stage 8 of wave 1; this build carries stages 1-3. The "
            "rows this build implements are executable in "
            "lifecycle_core/refusals.py and are exercised by "
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
        else:
            out(f"COULD NOT VERIFY: `{path}` is built in "
                f"{NOT_YET_BUILT[path]} of wave 1; this build carries "
                "stages 1-3. It is not an unknown verb — it is an unbuilt "
                "one, and the difference matters to whoever is reading this.")
            code = exits.COULD_NOT_VERIFY
    else:
        stage = NOT_YET_BUILT.get(path, "a later stage")
        out(f"COULD NOT VERIFY: `{path}` is built in {stage} of wave 1; this "
            "build carries stages 1-3.")
        code = exits.COULD_NOT_VERIFY

    firelog.fire(path, repo=args.repo, outcome=code)
    return code
