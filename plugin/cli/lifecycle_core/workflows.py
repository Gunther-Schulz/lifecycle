"""`lifecycle workflow bind` and the template registry it binds to (wave 2,
design §3.8b/§3.11 — carrier-rework-design-2026-08-26.md).

THE REGISTRY IS A DIRECTORY AND A PARSER, NOT AN INDEX. §3.8b's own
paragraph ("Why the registry is a directory and a parser, not an index
file") is the spec for this module's central invariant: `plugin/workflows/`
holds one `.md` file per template, the template id is the filename stem,
and a template declares its OWN required slots in an anchored header line
— `Slots:` — parsed the way `lanes.py`'s `_TRIGGER_LINE` parses `Trigger:`:
an anchored regex over the file's text, run fresh on every call. THERE IS
NO INDEX and no cache: an index listing each template's slots beside the
templates it describes is a comparison basis RESTATED from the source it
grades, and it goes stale silently — a template gains a slot, the index
keeps its old list, and every binding validated against it stays green
while being wrong. Deriving the slot set from the file itself cannot
drift, because there is only one copy.

THE BINDER SIDE ALREADY HAS ITS HOME. `template-bindings` is a REQUIRED
top-level key in `.claude/lifecycle.json` (`declaration.REQUIRED_KEYS`)
and is `{}` by default — this module reads and writes that key in place,
never a second file.

EVERY DECLARED SLOT IS REQUIRED (§1 of the brief; no optional slots in
wave 2). A slot `--set` does not fill is written `UNKNOWN` — the same
transitional marker `items.py` uses for a slot nobody has ever recorded,
reused rather than reinvented so `kind check`'s `binding_slot_unbound`
finding and `item check`'s UNKNOWN handling read one word, not two.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import declaration as decl
from . import exits
from . import items as items_mod

#: The anchored header line a template declares its own required slots in.
#: MIRRORS `lanes.py`'s `_TRIGGER_LINE` EXACTLY (the brief's own
#: instruction: do not invent a second parsing style) — with one
#: deliberate difference: `.*?`, not `.+?`. A `Trigger:` line with nothing
#: after it has no state to report and is folded into "no trigger line at
#: all"; a `Slots:` line with nothing after it must stay DISTINGUISHABLE
#: from an absent `Slots:` line (absent = zero required slots, present-
#: empty = a parse failure), and only a group that can capture empty text
#: lets the two be told apart.
_SLOTS_LINE = re.compile(r"^Slots:\s*(.*?)\s*$")

#: A declared slot name (brief §1): `[a-z0-9][a-z0-9_-]*`.
SLOT_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def registry_dir() -> Path:
    """`plugin/workflows/` — resolved from `__file__`, the same depth
    `declaration.py`'s `plugin_hooks()` resolves the plugin's own manifest
    at (`parents[2]`: both modules live at `plugin/cli/lifecycle_core/`).

    A MODULE-LEVEL FUNCTION, NOT A CONSTANT PATH, so a test can redirect it
    by monkeypatching `workflows.registry_dir` — the real directory ships
    holding only `.gitkeep`, and a fixture template must never be planted
    there.
    """
    return Path(__file__).resolve().parents[2] / "workflows"


@dataclass
class Template:
    """One template, as `registry_dir()/<id>.md` parses today."""
    template_id: str
    #: None when no file exists at all — distinct from a `path` whose file
    #: exists but fails to parse (`problem` is set either way).
    path: Path | None
    slots: list = field(default_factory=list)
    #: Set on any of the registry's named failures: no file, an unreadable
    #: file, or a `Slots:` line that is present-but-empty or carries a
    #: malformed name. Never silently read as zero slots (brief §1).
    problem: str | None = None


def read_template(template_id: str) -> Template:
    """Parse one template's required slots. THE PARSER — run fresh on
    every call, since there is no cached index to go stale."""
    path = registry_dir() / f"{template_id}.md"
    if not path.is_file():
        return Template(template_id, None, problem=(
            f"no template file at {path}. A template id naming no file "
            "cannot be bound to."))
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return Template(template_id, path,
                        problem=f"{path} could not be read ({exc!r}).")

    present = False
    raw_value = ""
    for line in text.split("\n"):
        m = _SLOTS_LINE.match(line)
        if m:
            present = True
            raw_value = m.group(1)
            break

    if not present:
        # An ABSENT `Slots:` line means zero required slots — a valid
        # template (brief §1).
        return Template(template_id, path, slots=[])

    if not raw_value.strip():
        return Template(template_id, path, problem=(
            f"{path} carries a `Slots:` line with no slot names. An "
            "absent `Slots:` line means zero required slots; a present, "
            "empty one is a PARSE FAILURE and is never silently read as "
            "zero."))

    names = [s.strip() for s in raw_value.split(",")]
    bad = [n for n in names if not SLOT_NAME_RE.match(n)]
    if bad:
        return Template(template_id, path, problem=(
            f"{path}'s `Slots:` line carries malformed slot name(s): "
            + ", ".join(repr(b) for b in bad)
            + f". Slot names must match {SLOT_NAME_RE.pattern!r}."))

    return Template(template_id, path, slots=names)


# --- `lifecycle workflow bind` ------------------------------------------------

def _parse_set(raw: str):
    """One `--set slot=value` argument -> `(slot, value)`."""
    slot, _sep, value = raw.partition("=")
    return slot.strip(), value


def cmd_workflow_bind(args, out, repo: Path) -> int:
    """`lifecycle workflow bind <template-id> [--set slot=value ...] [--force]`

    Reads `plugin/workflows/<template-id>.md`, parses its `Slots:` line,
    and writes `template-bindings[<template-id>]` into the repo's
    declaration with EVERY required slot present as a key — `--set` fills
    what it names, everything else gets `items_mod.UNKNOWN`, the
    migration's own transitional marker, never a default: an explicit
    unanswered slot is exactly what `kind check`'s `binding_slot_unbound`
    finding exists to flag.
    """
    template_id = args.template_id
    tmpl = read_template(template_id)
    if tmpl.problem:
        # BOTH shapes land here — no file at all, and a template that
        # exists but does not parse: the binder cannot form a required-
        # slot set to bind against either way, so it cannot verify the
        # operation. UNREADABLE INPUT IS NOT A FINDING (the brief's own
        # rule): exit 3, not 2 — the same reason `lifecycle` maps an
        # argparse usage error to 3, and never `FINDING [...]` bracketed —
        # this is not a registry-content claim the roster proves.
        out(f"COULD NOT VERIFY: {tmpl.problem}")
        return exits.COULD_NOT_VERIFY

    overrides = {}
    for raw in getattr(args, "set", None) or []:
        slot, value = _parse_set(raw)
        overrides[slot] = value

    unknown_named = sorted(s for s in overrides if s not in tmpl.slots)
    if unknown_named:
        out(f"COULD NOT VERIFY: --set names slot(s) "
            f"{', '.join(unknown_named)} which template {template_id!r} "
            "does not declare. Never silently accepted. Declared slots: "
            f"{', '.join(tmpl.slots) or '(none)'}.")
        return exits.COULD_NOT_VERIFY

    res = decl.read(repo)
    if res.declaration is None:
        for f in res.findings:
            out(f"FINDING [{f.row}] {f.message}")
        for u in res.unverified:
            out(f"COULD NOT VERIFY: {u}")
        out("`template-bindings` lives in the repo's declaration, and "
            "there is no readable declaration to write it into.")
        return res.code

    # A deep copy, exactly `migrate.py`'s own read-modify-write idiom for
    # this same file: mutate the copy, never the `Result`'s own dict.
    doc = json.loads(json.dumps(res.declaration))
    tb = doc.setdefault("template-bindings", {})
    if not isinstance(tb, dict):
        out("FINDING [declaration_malformed] `template-bindings` is not "
            "an object; refusing to write into it. Run `kind check` "
            "first.")
        return exits.FINDING

    if template_id in tb and not getattr(args, "force", False):
        out(f"FINDING [workflow_binding_exists] a binding for "
            f"{template_id!r} already exists in `template-bindings`. "
            "Refusing to overwrite it — pass --force to overwrite. A "
            "silent overwrite of a binding is not available.")
        return exits.FINDING

    binding = {slot: overrides.get(slot, items_mod.UNKNOWN)
               for slot in tmpl.slots}
    tb[template_id] = binding

    decl_path = repo / decl.DECLARATION_REL
    try:
        decl_path.write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
    except OSError as exc:
        out(f"COULD NOT VERIFY: the declaration could not be written "
            f"({exc!r}). Nothing was written.")
        return exits.COULD_NOT_VERIFY

    filled = sorted(s for s, v in binding.items() if v != items_mod.UNKNOWN)
    left_unknown = sorted(s for s, v in binding.items()
                          if v == items_mod.UNKNOWN)
    out(f"template: {template_id!r}   required slots: "
        f"{', '.join(tmpl.slots) or '(none)'}")
    out(f"filled: {', '.join(filled) or '(none)'}")
    out(f"UNKNOWN: {', '.join(left_unknown) or '(none)'}")
    out(f"wrote {decl.DECLARATION_REL} ({decl_path})")
    return exits.CLEAN
