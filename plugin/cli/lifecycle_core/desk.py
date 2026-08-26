"""`lifecycle desk state` — one desk's turn-end state, one file, no history.

WHAT THIS VERB IS FOR. The design's stall-detector booking (cache-fix
`BACKLOG.md`, the PARKED "ended on an announcement" entry) needs a wave-3
Stop-hook detector to refuse a turn that ends with an open delegation and no
recorded state. This verb is the RECORDING half only — it writes the state a
desk is in the moment it is called. THE WORD "TURN" DOES NOT APPEAR BELOW ON
PURPOSE: whether a given record covers "this turn" is the detector's own
question, answered by comparing the record's timestamp to the turn's start.
Building that comparison here would give the detector a second source of
truth for the same fact, which is exactly the split this design refuses
everywhere else.

WHY IT LIVES UNDER XDG STATE, NEVER `.claude/`. This reuses
`firelog.state_dir()` rather than writing a second resolver: a read or write
under the Claude config directory costs a permission dialog on this
machine — the operator's, and every dispatched agent's — and one such prompt
has already lost a session's work in flight (`firelog.py`'s own reason,
restated here because a caller reading this file alone should not have to
guess why it did not invent its own path).

THE VOCABULARY IS CLOSED. `REPORTED <msg-id>` / `WAITING-ON <lane|peer>
--horizon <t>` / `BLOCKED <named>` / `DONE` — four values, no others, no free
text. A value outside the four is a refusal, not a coercion: the same rule
`declaration.py`'s typed references apply to reader/writer entries, applied
here to a fourth closed set.

THE VERB ALWAYS OVERWRITES. One current state per desk, no history — the
per-turn question belongs to the wave-3 detector, and giving this verb its
own history would let a caller ask "what was the state two turns ago",
which nothing here is designed to answer correctly.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from . import declaration as decl
from . import exits, firelog

REPORTED = "REPORTED"
WAITING_ON = "WAITING-ON"
BLOCKED = "BLOCKED"
DONE = "DONE"

#: The closed vocabulary, in the booking's own order (cache-fix BACKLOG.md,
#: the PARKED "ended on an announcement" entry). Four values, no others.
DESK_STATE_VALUES = (REPORTED, WAITING_ON, BLOCKED, DONE)

#: One JSON object per desk, under the XDG state dir `firelog.state_dir()`
#: already resolves.
DESK_STATE_DIRNAME = "desk-state"

#: A desk id is taken from `--desk` or the environment, never trusted as a
#: path component: a `/` in it would otherwise let a caller's id escape this
#: directory. Folded rather than refused — the identity refusal below is the
#: one place an unusable id is turned away; this is a second, independent
#: belt so a technically-present-but-odd id still resolves to A file inside
#: `DESK_STATE_DIRNAME` and never outside it.
_UNSAFE_FOR_FILENAME = re.compile(r"[^A-Za-z0-9._-]")


def state_dir() -> Path:
    return firelog.state_dir() / DESK_STATE_DIRNAME


def desk_state_path(desk_id: str) -> Path:
    return state_dir() / f"{_UNSAFE_FOR_FILENAME.sub('_', desk_id)}.json"


def resolve_desk_id(args):
    """`(id, source, why-not)`. `--desk` explicit always wins; the default is
    the environment's session id, `CLAUDE_CODE_SESSION_ID`.

    NO REPO-PATH-PLUS-USER FALLBACK, and this is deliberate rather than an
    oversight: two desks working the same repo as the same user would derive
    an IDENTICAL key that way and silently share one state file, which
    destroys the per-desk property this verb exists to provide and would let
    a wave-3 detector read another desk's state as this one's. A refusal is
    recoverable; a collision is invisible — so the third case below refuses
    rather than deriving anything.
    """
    explicit = getattr(args, "desk", None)
    if explicit and explicit.strip():
        return explicit.strip(), "--desk", None
    env = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if env and env.strip():
        return env.strip(), "CLAUDE_CODE_SESSION_ID", None
    return None, None, (
        "neither --desk nor CLAUDE_CODE_SESSION_ID is set. `desk state` "
        "refuses rather than deriving a repo-path-plus-user key: two desks "
        "on the same repo as the same user would then collide on one file, "
        "silently sharing state that a wave-3 detector would read as one "
        "desk's own.")


def _shape_problem(value, argument, horizon):
    """`why-not`, or None where the value's own arguments are in shape."""
    if value == REPORTED:
        if not argument:
            return "REPORTED needs one argument: the message id."
    elif value == WAITING_ON:
        if not argument:
            return ("WAITING-ON needs one argument: the lane or peer waited "
                    "on.")
        if not horizon:
            return "WAITING-ON needs --horizon <t>."
    elif value == BLOCKED:
        if not argument:
            return "BLOCKED needs one argument: the named blocker."
    elif value == DONE:
        if argument or horizon:
            return "DONE takes no argument and no --horizon."
    return None


def _delegation_line(repo) -> str:
    """Best-effort: this repo's declared `delegation` field, or why it could
    not be read. NEVER gates the verb's own exit code — `desk state` with no
    active delegation, or no resolvable repo at all, is not an error; it
    records, and SAYS what it found about the field rather than staying
    silent about it."""
    if repo is None:
        return ("delegation: not checked — no repo context (pass --repo or "
                "run inside a git work tree)")
    res = decl.read(repo)
    if res.declaration is None:
        return ("delegation: not checked — this repo's declaration could "
                "not be read")
    value = res.declaration.get("delegation", "none")
    if "delegation" not in res.declaration:
        return "delegation: absent — no active delegation declared (default)"
    return f"delegation: {value!r} (this repo's declaration)"


def cmd_desk_state(args, out, repo) -> int:
    value = (getattr(args, "value", None) or "").strip()
    if value not in DESK_STATE_VALUES:
        out(f"FINDING [desk_state_unknown_value] {value!r} is not one of "
            f"the closed vocabulary: {', '.join(DESK_STATE_VALUES)}. A "
            "value outside the four is a refusal, not a coercion — the "
            "vocabulary is closed and an open one decays.")
        return exits.FINDING

    argument = getattr(args, "argument", None)
    horizon = getattr(args, "horizon", None)
    problem = _shape_problem(value, argument, horizon)
    if problem:
        out(f"FINDING [desk_state_shape] {problem}")
        return exits.FINDING

    desk_id, source, why_not = resolve_desk_id(args)
    if desk_id is None:
        out(f"COULD NOT VERIFY: {why_not}")
        return exits.COULD_NOT_VERIFY

    rec = {
        "value": value,
        "argument": argument,
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "desk": desk_id,
        "desk_source": source,
    }
    if value == WAITING_ON:
        rec["horizon"] = horizon

    path = desk_state_path(desk_id)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        out(f"COULD NOT VERIFY: the desk-state file at {path} could not be "
            f"written ({exc!r}). Nothing was recorded.")
        return exits.COULD_NOT_VERIFY

    shown = value + (f" {argument}" if argument else "") \
        + (f" --horizon {horizon}" if value == WAITING_ON else "")
    out(f"desk state: {shown}")
    out(f"desk: {desk_id} (source: {source})")
    out(f"recorded at {path} — OVERWRITES any prior state for this desk; "
        "there is no history.")
    out(_delegation_line(repo))
    return exits.CLEAN
