"""One fire log for every `lifecycle` verb (design §3.8).

WHERE IT LIVES, and why not `~/.claude/`. On this machine the Claude config
directory is protected by path SHAPE, not by what a file is: anything read or
written under `~/.claude/` costs a permission dialog — the operator's, and
every dispatched agent's — and a prompt on a data write is one the operator
cannot triage. One such prompt was denied mid-task and the session lost the
work in flight. Tool data therefore lives in XDG state.

WHAT IT IS FOR. `item close`'s recording act is a line here (the `items`
kind's declared exit); so is every other verb's, so that "what did the tool
do to this carrier" is answerable from one file rather than reconstructed
from git. It is append-only JSONL, one object per invocation.

WHAT IT NEVER CARRIES. Argument VALUES are not logged — only the verb path
and the repo. A fire log that echoed arguments would carry item bodies, and
on a public repo that is the leak direction. The cap below is a second belt.

FAILING TO LOG IS NOT A VERDICT. If the state directory cannot be written,
the verb still runs and still returns its own answer; the log line is lost
and `logged=False` says so to a caller that cares. A tool that refused to
work because its journal was unwritable would convert a cosmetic failure
into an outage.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

#: Hard cap on any single logged string, so one pathological value cannot
#: turn the log into a payload store.
FIELD_CAP = 512


def state_dir() -> Path:
    """`$XDG_STATE_HOME/lifecycle`, defaulting per the XDG spec."""
    base = os.environ.get("XDG_STATE_HOME") or (Path.home() / ".local" / "state")
    return Path(base) / "lifecycle"


def log_path() -> Path:
    return state_dir() / "fire.jsonl"


def _clip(s: str) -> str:
    s = str(s)
    return s if len(s) <= FIELD_CAP else s[:FIELD_CAP] + "…"


def fire(verb: str, *, repo: str | None = None, outcome: int | None = None,
         detail: str | None = None) -> bool:
    """Append one line. Returns whether it was written."""
    rec = {
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "verb": _clip(verb),
    }
    if repo is not None:
        rec["repo"] = _clip(repo)
    if outcome is not None:
        rec["outcome"] = outcome
    if detail is not None:
        rec["detail"] = _clip(detail)
    try:
        d = state_dir()
        d.mkdir(parents=True, exist_ok=True)
        with open(d / "fire.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return True
    except OSError:
        return False
