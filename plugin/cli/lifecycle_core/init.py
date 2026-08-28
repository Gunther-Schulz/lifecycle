"""`lifecycle init` — a fresh repo's declaration and lane stubs (wave 2,
design §3.11: "Authoring support is part of the plugin").

WHAT THIS VERB OWNS. A repo's `.claude/lifecycle.json` with all twelve
`REQUIRED_KEYS`, made visible to git, plus a stub `lanes/<name>.md` for each
`--lane` named. It does NOT create carrier files (`ITEMS.md`,
`ITEMS-DONE.md`, `LEDGER.md`) — those are `migrate`'s job for a repo with an
old carrier to convert FROM, or a human's for a truly greenfield one; a repo
that has never run any of the above will see `kind check`'s one-schema-
per-repo agreement answer COULD NOT VERIFY on those three carriers rather
than CLEAN until they exist. That is a real gap in the wave-2 design this
verb inherited rather than one it introduced — see the module's own report
for the evidence — and it is named here rather than silently patched by
having `init` invent carrier files the settled design never asked for.

EVERY DEFAULT THIS VERB WRITES IS PRINTED WITH ITS REASON. §3.11's own rule:
"a schema default is what `lifecycle init` WRITES into the file, never what
the tool assumes when a line is absent." An unstated derivation (the
id-prefix, the laws branch) reads afterwards exactly like a hand-authored
choice, so every one of them is echoed to the caller as it is decided.
"""

import copy
import json
import re
import subprocess
from pathlib import Path

from . import declaration as decl
from . import exits
from . import lanes as lanes_mod


def derive_id_prefix(repo: Path) -> str:
    """The repo's directory name, split on `-`/`_`: first letter of each of
    the first two words, lowercased; a one-word name yields its own first
    two letters. Specified exactly this way rather than left to judgment
    (brief, section A) — `claude-code-cache-fix` -> `cc`, `lifecycle` -> `li`.
    """
    words = [w for w in re.split(r"[-_]+", repo.name) if w]
    if len(words) >= 2:
        return (words[0][:1] + words[1][:1]).lower()
    if words:
        return words[0][:2].lower()
    return repo.name[:2].lower() or "xx"


def determine_laws(repo: Path):
    """`(laws_file, branch, reason)` per §3.11 judgment rule 5.

    branch is one of "operator-only", "foreign", "could-not-verify" — the
    THREE cases the rule names, each with why, so a could-not-verify reading
    says WHICH of the three it was rather than only that it happened.

    `Co-Authored-By` trailers are NOT authors and need no special-casing to
    stay that way: `git log --format=%ae` reads the commit's AUTHOR field
    only, and a trailer lives in the message body — the discriminator
    ignores them by what it reads, not by an extra filter (the brief's own
    point, verified by the Co-Authored-By test arm).
    """
    ls = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--error-unmatch", "CLAUDE.md"],
        capture_output=True, text=True)
    if ls.returncode != 0:
        return ("CLAUDE.local.md", "could-not-verify",
                "no tracked CLAUDE.md in this repo (checked: git ls-files "
                "--error-unmatch CLAUDE.md)")

    log = subprocess.run(
        ["git", "-C", str(repo), "log", "--format=%ae", "--", "CLAUDE.md"],
        capture_output=True, text=True)
    if log.returncode != 0:
        return ("CLAUDE.local.md", "could-not-verify",
                "git could not read CLAUDE.md's author history (checked: "
                f"git log --format=%ae -- CLAUDE.md; {log.stderr.strip()!r})")

    authors = [a.strip() for a in log.stdout.splitlines() if a.strip()]
    if not authors:
        return ("CLAUDE.local.md", "could-not-verify",
                "CLAUDE.md is tracked but carries no commit history "
                "(checked: git log --format=%ae -- CLAUDE.md, 0 lines)")

    cfg = subprocess.run(["git", "config", "user.email"], cwd=str(repo),
                         capture_output=True, text=True)
    if cfg.returncode != 0 or not cfg.stdout.strip():
        return ("CLAUDE.local.md", "could-not-verify",
                "this repo's own operator identity could not be read "
                "(checked: git config user.email)")
    operator = cfg.stdout.strip()

    foreign = sorted(set(authors) - {operator})
    if foreign:
        return ("CLAUDE.local.md", "foreign",
                f"CLAUDE.md's author history includes {', '.join(foreign)}, "
                f"which is not the operator ({operator})")
    return ("CLAUDE.md", "operator-only",
            f"every author of CLAUDE.md's history is the operator ({operator})")


#: The three carrier kinds `init` COPIES from the plugin's own declaration,
#: never invents (brief, section A). Populated lazily by `_plugin_kinds()`
#: rather than at import time: the plugin's declaration is read from disk
#: once, on first use, and the result is a plain dict any caller may mutate
#: its own deep copy of.
_PLUGIN_KIND_NAMES = ("items", "done bodies", "ledger lines")


def _plugin_declaration_path() -> Path:
    # plugin/cli/lifecycle_core/init.py -> <repo root>/.claude/lifecycle.json
    # (unlike `.claude-plugin/plugin.json`, which DOES live under `plugin/`
    # — `declaration.py`'s own `plugin_hooks()` walks up 2 for that one;
    # this one is the REPO's own declaration, one level further up, at 3).
    return Path(__file__).resolve().parents[3] / ".claude" / "lifecycle.json"


def plugin_kinds() -> dict:
    """The three carrier kinds, taken WHOLE from the plugin repo's own
    declaration — including the typed `writer`/`reader` shapes exactly as
    written there (writer a comma-joined string, reader a list; not
    normalized). Raises if the plugin's own declaration cannot be read: a
    fresh repo's `init` has nothing honest to fall back to here, and a
    silent empty `kinds` block would violate `kind check`'s own "kinds must
    be a non-empty object" rule while looking like a choice `init` made.
    """
    path = _plugin_declaration_path()
    doc = json.loads(path.read_text(encoding="utf-8"))
    kinds = doc.get("kinds") or {}
    out = {}
    for name in _PLUGIN_KIND_NAMES:
        if name not in kinds:
            raise KeyError(f"the plugin's own declaration at {path} carries "
                           f"no {name!r} kind to copy from")
        out[name] = copy.deepcopy(kinds[name])
    return out


def ensure_gitignore(repo: Path) -> list:
    """Append the declaration negation and the `ITEMS.md.lock` ignore line
    (booked as lc-11) if either is missing. Returns the lines actually
    added, for the caller to report — silence about what changed on disk
    is the failure mode this whole area exists to avoid.
    """
    needed = ["!.claude/lifecycle.json", "ITEMS.md.lock"]
    gi = repo / ".gitignore"
    existing_text = gi.read_text(encoding="utf-8") if gi.exists() else ""
    existing_lines = {ln.strip() for ln in existing_text.splitlines()}
    to_add = [ln for ln in needed if ln not in existing_lines]
    if to_add:
        with open(gi, "a", encoding="utf-8") as fh:
            if existing_text and not existing_text.endswith("\n"):
                fh.write("\n")
            for ln in to_add:
                fh.write(ln + "\n")
    return to_add


def cmd_init(args, out, repo: Path) -> int:
    """Write `.claude/lifecycle.json`, the `.gitignore` lines, and a lane
    stub per `--lane`. REFUSES by default if the declaration already
    exists; `--force` overwrites.
    """
    decl_path = repo / decl.DECLARATION_REL
    if decl_path.exists() and not getattr(args, "force", False):
        out(f"declaration already exists at {decl.DECLARATION_REL} "
            f"({decl_path}). Refusing to overwrite it — pass --force to "
            "overwrite. A silent overwrite of a declaration is not available.")
        return exits.FINDING

    if args.id_prefix:
        prefix = args.id_prefix
        out(f"id-prefix: {prefix!r} (explicit --id-prefix)")
    else:
        prefix = derive_id_prefix(repo)
        out(f"id-prefix: {prefix!r} (derived from directory name {repo.name!r} "
            "— uniqueness across repos is NOT checked; there is no registry "
            "to check against yet, and a collision is a real possibility "
            "this verb cannot see)")

    laws_file, branch, reason = determine_laws(repo)
    if branch == "could-not-verify":
        out(f"laws: {laws_file} (the local overlay) — COULD NOT VERIFY: "
            f"{reason}. Taking the overlay branch; this reading is NOT "
            "established.")
    else:
        out(f"laws: {laws_file} — {branch} branch: {reason}")

    out("trigger-policy: on-demand (recommended next step: switch to "
        "`advise` once the router has run clean for a week — a suggestion "
        "in the file, never a silent switch)")

    lane_names = list(getattr(args, "lane", None) or [])
    if lane_names:
        out(f"lanes: {', '.join(lane_names)}")
    else:
        out("lanes: (none named) — declared as an empty list, never absent "
            "(§3.0: an empty declared list is a stated fact)")

    try:
        kinds = plugin_kinds()
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError) as exc:
        out(f"could not copy the carrier kinds from the plugin's own "
            f"declaration ({exc!r}). Nothing was written.")
        return exits.COULD_NOT_VERIFY

    goals = ["general-maintenance"]
    out(f"goals: {goals} (placeholder — declare this repo's real goals "
        "before relying on the head or the retire lane)")
    # §3.1b: the reserved goal is NOT written into the declaration — it is
    # not declarable, and a repo that listed it would be declaring a value
    # the plugin owns. It is therefore invisible in the file this verb just
    # wrote, which makes `init`'s own output the one moment a repo's author
    # is told the value exists at all.
    out(f"goals (effective): {decl.effective_goals({'goals': goals})} — the "
        f"declared list plus the plugin-reserved `{decl.RESERVED_GOAL}`, "
        "accepted in every repo and declared in none: work on this repo's "
        "own carrier, method, hooks, machinery or migration residue "
        "(§3.1b). Book self-work under it from day one rather than leaving "
        "it in prose nobody re-reads.")

    doc = {
        "schema": decl.SCHEMA_FLOOR,
        "id-prefix": prefix,
        "public": False,
        "laws": laws_file,
        "closure-home": "ITEMS-DONE.md",
        "trigger-policy": "on-demand",
        "goals": goals,
        "head-rule": "none",
        "lanes": lane_names,
        "template-bindings": {},
        "leak-scan": {
            "source-scope-foreign-path": False,
            "reason": "not yet scanned — this repo has not run the leak "
                      "scan and no decision has been made about scope; "
                      "`init` never turns this on by default.",
        },
        "kinds": kinds,
    }

    missing = [k for k in decl.REQUIRED_KEYS if k not in doc]
    if missing:
        out(f"internal: the declaration `init` built is missing required "
            f"key(s) {', '.join(missing)} before it was even written. "
            "Nothing was written.")
        return exits.COULD_NOT_VERIFY
    retired_present = [k for k in decl.RETIRED_KEYS if k in doc]
    if retired_present:
        out(f"internal: the declaration `init` built carries retired "
            f"key(s) {', '.join(retired_present)}. Nothing was written.")
        return exits.COULD_NOT_VERIFY

    decl_path.parent.mkdir(parents=True, exist_ok=True)
    decl_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    out(f"wrote {decl.DECLARATION_REL} ({decl_path})")

    added = ensure_gitignore(repo)
    if added:
        out(f".gitignore: added {', '.join(added)}")
    else:
        out(".gitignore: already carried both lines — nothing added")

    ignored = decl.ignored_by_git(repo, decl.DECLARATION_REL)
    if ignored is None:
        out("COULD NOT VERIFY: git could not answer whether the "
            f"declaration is ignored (checked: git check-ignore --no-index "
            f"{decl.DECLARATION_REL}).")
        code = exits.COULD_NOT_VERIFY
    elif ignored:
        pattern = decl.ignore_pattern(repo, decl.DECLARATION_REL)
        out(f"the declaration at {decl.DECLARATION_REL} is STILL ignored by "
            f"git after adding the negation (matching pattern: {pattern}). "
            "A declaration git cannot see is G1's recorded defect — check "
            "whether a parent-directory ignore rule (e.g. a bare `.claude` "
            "line rather than `.claude/*`) is swallowing the whole "
            "directory, which a file-level negation cannot undo.")
        code = exits.FINDING
    else:
        out(f"declaration visible to git: {decl.DECLARATION_REL} is not "
            "ignored (checked: git check-ignore --no-index).")
        code = exits.CLEAN

    lane_lines_dir = repo / "lanes"
    for name in lane_names:
        lane_path = lane_lines_dir / f"{name}.md"
        if lane_path.exists():
            out(f"lane stub for {name!r} already exists at {lane_path} — "
                "left untouched (init never overwrites an existing lane "
                "body, --force included: --force covers the DECLARATION "
                "only).")
            continue
        lane_lines_dir.mkdir(parents=True, exist_ok=True)
        # ONE STUB BODY, NOT TWO (wave 2, item A): `lane_stub` moved to
        # `lanes.py`, the module that owns every other lane-shape fact
        # (`LANE_PARTS`, `LANES_DIR`, `_TRIGGER_LINE`) — `lane new` calls
        # the identical function rather than a copy that could drift from
        # this one.
        lane_path.write_text(lanes_mod.lane_stub(name), encoding="utf-8")
        out(f"wrote lane stub: {lane_path}")

    return code
