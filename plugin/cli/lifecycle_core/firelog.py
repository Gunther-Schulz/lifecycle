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


def last_run(verb: str, repo=None):
    """The NEWEST fire-log record for `verb`, optionally narrowed to a repo.

    THIS IS A BEST-EFFORT, MACHINE-LOCAL READ and its contract says so
    rather than hiding it. The fire log lives under `$XDG_STATE_HOME`: it
    does not travel with the repo, it is not a git object, and a fresh
    machine or a lost write leaves it empty. A caller that rendered None as
    "nothing to report" would turn a missing CARRIER into a verdict about
    the repo, which is the absence-read-as-clean class one layer down from
    where this module usually sits.

    So: `None` means NO RECORD HERE — never "the verb found nothing". The
    two are different answers and only the caller can render the difference.

    NEWEST BY THE RECORD'S OWN `at`, not by file order. Append order and
    timestamp order agree today and the coupling is invisible: a log
    concatenated from two machines, or rotated and restored, would hand a
    tail-read a stale record that looks exactly like a current one.
    """
    path = log_path()
    if not path.is_file():
        return None
    import json
    want = str(repo) if repo is not None else None
    best = None
    try:
        for line in path.read_text(encoding="utf-8").split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                # A TORN LINE IS SKIPPED, NOT FATAL. This log is appended by
                # every invocation on the machine; a half-written tail is an
                # ordinary state, and refusing to read the whole log because
                # of one would lose every good record behind it.
                continue
            if str(rec.get("verb", "")) != verb:
                continue
            if want is not None and str(rec.get("repo", "")) != want:
                continue
            if best is None or str(rec.get("at", "")) > str(best.get("at", "")):
                best = rec
    except OSError:
        return None
    return best
