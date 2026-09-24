#!/usr/bin/env python3
"""lc-161 stage 1: extract operator mid-turn interventions and per-session
turn counts from Claude Code session records, across the governed roster.

Extraction only — no classification of WHAT an intervention is about. That
is a later stage.

Sources of operator text, mirroring the discrimination logic in dotfiles'
claude/hooks/midturn-answer-check.py (read, not imported — that hook lives
in another repo):

  (a) "prompt" channel  — `type:"user"` records whose message content is a
      string or contains a text block, excluding isMeta records and
      excluding any record whose `origin.kind` is present and not "human".
      This is the hook's `_is_human_prompt()` predicate, reused verbatim in
      `is_human_prompt_event()` below. Covers both turn-opening prompts and
      queued messages that happened to be delivered as an ordinary turn
      (`promptSource:"queued"` still produces a full `type:"user"` event).

  (b) "queued" channel  — `type:"attachment"` records with
      `attachment.type == "queued_command"`, `commandMode == "prompt"`
      (never "task-notification", which is a harness event with no
      `origin`), and `origin.kind == "human"` when origin is present. This
      is the hook's mid-turn-injection lane (`queued_midturn()`). A queued
      message whose exact prompt text later shows up inside a delivered
      `type:"user"` record is the SAME operator message surfacing twice —
      it is attributed to channel (a) and dropped from (b), the same
      "delivered" de-duplication the hook itself performs (substring
      containment; weak for very short prompts, e.g. a bare "ok" can
      collide with any later text containing that substring — a known,
      inherited limitation, not one this tool tries to improve on).

`type:"queue-operation"` (enqueue/remove/dequeue) records are deliberately
EXCLUDED from extraction. They read like a third channel — Background
research for this brief treated an enqueue's `content` as potential
operator text — but a full read of midturn-answer-check.py shows it never
references `type:"queue-operation"` at all: its entire discrimination runs
over `type:"attachment"`. Measured on a real session (lifecycle, ref
09020605): of 20 queue-operation enqueues, 11
carry harness task-notification content, 1 carries a peer
`<cross-session-message>` (neither operator nor harness), and the
remaining 8 human-authored ones are exact-content duplicates (by
timestamp and text) of records already reachable through channel (a) or
(b). Counting them as an independent channel would double-count. This
finding was reported to the dispatcher before this file was written; see
the extractor's closing report for the message log.

Three answers, always (repo law 1): every run prints CLEAN, or a FINDING
(an unparseable line, or a record this tool could not classify as
operator/not-operator), never silence in place of either. A finding never
suppresses the rest of the extraction — everything parseable still gets
written.

No hardcoded machine path, login, repo root, or XDG root (repo law 6):
the projects root and the roster path are both derived at run time, with
env overrides for testing.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

TAIL_CHARS = 600  # prev_assistant_tail length
COULD_NOT_CLASSIFY = "could-not-classify"


# ---------------------------------------------------------------- roots ---

def projects_root() -> Path:
    """~/.claude/projects, overridable via CLAUDE_PROJECTS_DIR (no
    hardcoded home or login: derived from Path.home() at run time)."""
    override = os.environ.get("CLAUDE_PROJECTS_DIR")
    if override:
        return Path(override)
    return Path.home() / ".claude" / "projects"


def config_home() -> Path:
    """$XDG_CONFIG_HOME, defaulting to ~/.config — never a hardcoded XDG
    root."""
    override = os.environ.get("XDG_CONFIG_HOME")
    if override:
        return Path(override)
    return Path.home() / ".config"


def roster_path() -> Path:
    return config_home() / "lifecycle" / "repos"


def read_roster(path: Path) -> tuple[list[str], str | None]:
    """[repo paths] and an error string (or None). Comment (#) and blank
    lines are skipped — the roster format lifecycle's own `lane list`
    reads."""
    if not path.exists():
        return [], f"roster missing: {path}"
    repos = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        repos.append(line)
    return repos, None


def project_dir_name(repo_path: str) -> str:
    """The projects/ subdirectory name Claude Code derives from a cwd:
    every "/" and "." replaced by "-"."""
    return repo_path.replace("/", "-").replace(".", "-")


# ------------------------------------------------------------- parsing ---

def parse_ts(s):
    """ISO8601 timestamp -> aware datetime, or None if unparseable."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def parse_date_or_ts(s: str) -> datetime:
    """--since (YYYY-MM-DD, midnight UTC) or --until (any ISO timestamp)."""
    try:
        return datetime.fromisoformat(s + "T00:00:00+00:00")
    except ValueError:
        pass
    dt = parse_ts(s)
    if dt is None:
        raise argparse.ArgumentTypeError(f"unparseable date/timestamp: {s!r}")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


# ------------------------------------------- operator-message discrimination

def is_human_prompt_event(event: dict) -> bool:
    """Channel (a): mirrors midturn-answer-check.py's _is_human_prompt()."""
    msg = event.get("message")
    if not isinstance(msg, dict) or msg.get("role") != "user":
        return False
    if event.get("isMeta") is True:
        return False
    origin = event.get("origin")
    if origin and not (isinstance(origin, dict) and origin.get("kind") == "human"):
        return False
    content = msg.get("content")
    if isinstance(content, str):
        return bool(content.strip())
    if isinstance(content, list):
        return any(isinstance(b, dict) and b.get("type") == "text" for b in content)
    return False


def prompt_text(event: dict) -> str:
    content = event.get("message", {}).get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        for b in content:
            if isinstance(b, dict) and b.get("type") == "text":
                return str(b.get("text") or "")
    return ""


def is_peer_event(event: dict) -> bool:
    origin = event.get("origin")
    return isinstance(origin, dict) and origin.get("kind") == "peer"


# Two harness/relay text shapes land as plain type:"user" records with NO
# `isMeta` and NO `origin` field at all — so is_human_prompt_event() alone
# passes them as operator text. Found by inspecting the positive-control
# session (09020605), not anticipated by the brief or by
# midturn-answer-check.py (whose own risk model never needed to tell these
# apart from real operator text): (1) an AgentTeam teammate relay
# ("Another Claude session sent a message:\n<teammate-message ...>" — a
# DIFFERENT wrapper from the `<cross-session-message>` SendMessage channel,
# which DOES carry isMeta+origin.peer and is caught by is_peer_event()
# instead); (2) a background task-notification delivered as an ordinary
# turn rather than mid-turn-queued ("<task-notification>..." with no
# wrapper at all). Content-prefix matching is the only signal available
# for either. 15 and 3 occurrences respectively in one real session file.
RELAY_TEXT_PREFIX = "Another Claude session sent a message:"
HARNESS_TEXT_PREFIXES = ("<task-notification>",)

# lc-161 stage 2 (this desk, 2026-09-24): a second population of plain
# type:"user" prompt-channel records carries no operator content at all —
# the harness's own echo of a slash command's outcome, or of the harness
# interrupting/compacting the session — mixed among genuine operator text
# with no isMeta/origin signal to tell them apart, same as the two shapes
# above. And a THIRD population is a real operator act, but a TOOLING one
# (invoking the harness itself, not addressing the work): a bare
# "/name ..." or the harness's own "<command-name>...</command-name>"
# expansion of one. Neither population belongs in operator_messages —
# the first carries nothing, the second is not an intervention in the
# work — but only the second is still an operator act worth a count, so
# it gets its own column (`operator_commands`) rather than being dropped.
# Measured on the stage-1 baseline (lc161-2026-09-24-stage1.jsonl, 2327
# message rows): compaction-continuation summaries 68, interrupted
# markers 77, local-command stdout/caveat echoes 73, slash commands
# (bare or wrapped) 165 — of which 14 (`/close-session`,
# `/skill-craft:release-plugin`) wrap with `<command-message>` BEFORE
# `<command-name>` rather than after, so both tag orderings are checked;
# a `<command-name>`-only check silently missed all 14 (found re-checking
# this same population, not by the brief).
COMPACTION_CONTINUATION_PREFIX = "This session is being continued"
INTERRUPTED_MARKER_PREFIX = "[Request interrupted by user"
COMMAND_ECHO_PREFIXES = ("<local-command-stdout>", "<local-command-caveat>")
COMMAND_NAME_WRAPPER_PREFIXES = ("<command-name>", "<command-message>")
BARE_SLASH_COMMAND_RE = re.compile(r"/[A-Za-z0-9_-]+(?:\s+\S.*)?$", re.DOTALL)


def classify_user_text(text: str) -> str:
    """"operator" | "command" | "peer" | "harness" for a type:"user" event's
    own text, on top of (never instead of) the isMeta/origin check above.

    "command" is a slash-command invocation — an operator act, but a
    TOOLING one, counted in operator_commands rather than operator_messages.
    "harness" additionally covers compaction-continuation summaries,
    interrupted markers, and a local command's own stdout/caveat echo —
    none of these carry any operator content (lc-161 stage 2 finding)."""
    t = text.lstrip()
    if t.startswith(RELAY_TEXT_PREFIX):
        return "peer"
    if any(t.startswith(p) for p in HARNESS_TEXT_PREFIXES):
        return "harness"
    if t.startswith(COMPACTION_CONTINUATION_PREFIX):
        return "harness"
    if t.startswith(INTERRUPTED_MARKER_PREFIX):
        return "harness"
    if any(t.startswith(p) for p in COMMAND_ECHO_PREFIXES):
        return "harness"
    if any(t.startswith(p) for p in COMMAND_NAME_WRAPPER_PREFIXES):
        return "command"
    if BARE_SLASH_COMMAND_RE.match(t.strip()):
        return "command"
    return "operator"


def queued_command_classification(attachment: dict) -> str:
    """"operator" | "harness" | "peer" | could-not-classify sentinel, for
    an attachment.type=="queued_command" record. Mirrors
    midturn-answer-check.py's queued_midturn() gating, in classification
    form rather than suppression form."""
    mode = attachment.get("commandMode")
    if mode == "task-notification":
        return "harness"
    if mode == "prompt":
        origin = attachment.get("origin")
        if isinstance(origin, dict):
            kind = origin.get("kind")
            if kind == "human":
                return "operator"
            if kind == "peer":
                return "peer"
            return COULD_NOT_CLASSIFY
        return "operator"  # no origin: same default the hook applies
    return COULD_NOT_CLASSIFY  # unknown commandMode


# ------------------------------------------------------------- extraction

@dataclass
class SessionResult:
    repo: str
    session_ref: str
    first_ts: str = None
    last_ts: str = None
    assistant_turns: int = 0
    operator_messages: int = 0
    operator_commands: int = 0
    cross_session_inbound: int = 0
    messages: list = field(default_factory=list)
    unparseable_lines: int = 0
    could_not_classify: int = 0


def extract_session(path: Path, repo: str, since: datetime, until: datetime):
    session_ref = path.stem[:8]
    res = SessionResult(repo=repo, session_ref=session_ref)

    # Running (whole-file, not window-gated) state for context fields.
    seen_assistant_ids = set()
    last_assistant_text = ""
    any_ts_in_window = False

    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                res.unparseable_lines += 1
                continue

            if ev.get("isSidechain") is True:
                continue  # subagent sidechain record, never a session event

            ts = parse_ts(ev.get("timestamp"))
            in_window = ts is not None and since <= ts <= until
            if in_window:
                any_ts_in_window = True
                if res.first_ts is None or ts < parse_ts(res.first_ts):
                    res.first_ts = ev["timestamp"]
                if res.last_ts is None or ts > parse_ts(res.last_ts):
                    res.last_ts = ev["timestamp"]

            etype = ev.get("type")

            if etype == "assistant":
                msg = ev.get("message")
                if isinstance(msg, dict) and msg.get("role") == "assistant":
                    mid = msg.get("id")
                    content = msg.get("content")
                    if isinstance(content, list):
                        for b in content:
                            if isinstance(b, dict) and b.get("type") == "text":
                                t = str(b.get("text") or "")
                                if t.strip():
                                    last_assistant_text = t
                    if in_window:
                        if mid:
                            if mid not in seen_assistant_ids:
                                seen_assistant_ids.add(mid)
                                res.assistant_turns += 1
                        else:
                            # no message id at all: cannot dedupe, count as
                            # its own turn rather than silently dropping it
                            res.assistant_turns += 1
                continue

            if etype == "user":
                if not in_window:
                    continue
                if is_peer_event(ev):
                    res.cross_session_inbound += 1
                    continue
                if not is_human_prompt_event(ev):
                    continue
                text = prompt_text(ev)
                cls = classify_user_text(text)
                if cls == "harness":
                    continue
                if cls == "peer":
                    res.cross_session_inbound += 1
                    continue
                if cls == "command":
                    res.operator_commands += 1
                    continue
                res.operator_messages += 1
                res.messages.append({
                    "type": "message",
                    "repo": repo,
                    "session_ref": session_ref,
                    "timestamp": ev.get("timestamp"),
                    "channel": "prompt",
                    "text": text,
                    "prev_assistant_tail": last_assistant_text[-TAIL_CHARS:],
                    "turn_index": len(seen_assistant_ids),
                })
                continue

            if etype == "attachment":
                att = ev.get("attachment")
                if not (isinstance(att, dict) and att.get("type") == "queued_command"):
                    continue
                if not in_window:
                    continue
                cls = queued_command_classification(att)
                if cls == "harness":
                    continue
                if cls == COULD_NOT_CLASSIFY:
                    res.could_not_classify += 1
                    continue
                p = att.get("prompt")
                if isinstance(p, list):
                    p = " ".join(str(b.get("text") or "") for b in p
                                 if isinstance(b, dict) and b.get("type") == "text")
                p = str(p or "").strip()
                if not p:
                    continue
                if cls == "peer":
                    res.cross_session_inbound += 1
                    continue
                # cls == "operator": de-dupe against a later delivered
                # type:user event carrying this same text (the hook's own
                # "delivered" check).
                if _delivered_later(path, p, ev.get("timestamp")):
                    continue
                res.operator_messages += 1
                res.messages.append({
                    "type": "message",
                    "repo": repo,
                    "session_ref": session_ref,
                    "timestamp": ev.get("timestamp"),
                    "channel": "queued",
                    "text": p,
                    "prev_assistant_tail": last_assistant_text[-TAIL_CHARS:],
                    "turn_index": len(seen_assistant_ids),
                })
                continue

    if not any_ts_in_window:
        return None
    return res


def _delivered_later(path: Path, prompt: str, after_ts) -> bool:
    """Re-scans the file for a type:"user" event after `after_ts` whose
    content contains `prompt` verbatim — mirrors the hook's `delivered`
    check. A second pass per queued attachment is acceptable at this
    tool's data volume (governed roster, weeks of history, not a hot
    path)."""
    after = parse_ts(after_ts)
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") != "user":
                continue
            ts = parse_ts(ev.get("timestamp"))
            if after is not None and ts is not None and ts <= after:
                continue
            if not is_human_prompt_event(ev):
                continue
            if prompt in prompt_text(ev):
                return True
    return False


# ------------------------------------------------------------------ main ---

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--since", required=True, type=parse_date_or_ts,
                     help="YYYY-MM-DD, window start (midnight UTC)")
    ap.add_argument("--until", type=parse_date_or_ts, default=None,
                     help="ISO timestamp, window end (default: now)")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()

    since = args.since
    until = args.until or datetime.now(timezone.utc)

    roster, err = read_roster(roster_path())
    if err:
        print(f"FINDING: {err}", file=sys.stderr)
        return 3

    root = projects_root()
    all_sessions = []
    absent_repos = []
    zero_repos = []
    total_unparseable = 0
    total_could_not_classify = 0

    for repo_path in roster:
        repo = Path(repo_path).name
        proj_dir = root / project_dir_name(repo_path)
        if not proj_dir.is_dir():
            absent_repos.append(repo)
            continue
        session_files = sorted(proj_dir.glob("*.jsonl"))
        repo_sessions = []
        for sf in session_files:
            res = extract_session(sf, repo, since, until)
            if res is not None:
                total_unparseable += res.unparseable_lines
                total_could_not_classify += res.could_not_classify
                repo_sessions.append(res)
        if not repo_sessions:
            zero_repos.append(repo)
        all_sessions.extend(repo_sessions)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as out:
        for res in all_sessions:
            n = res.assistant_turns
            per100 = (res.operator_messages / n * 100) if n else None
            out.write(json.dumps({
                "type": "session",
                "repo": res.repo,
                "session_ref": res.session_ref,
                "first_ts": res.first_ts,
                "last_ts": res.last_ts,
                "assistant_turns": res.assistant_turns,
                "operator_messages": res.operator_messages,
                "operator_per_100_turns": per100,
                "operator_commands": res.operator_commands,
                "cross_session_inbound": res.cross_session_inbound,
            }) + "\n")
            for m in res.messages:
                out.write(json.dumps(m) + "\n")

    for repo in absent_repos:
        print(f"ABSENT: {repo} (no project directory under {root})", file=sys.stderr)
    for repo in zero_repos:
        print(f"ZERO: {repo} (0 in-window sessions, {since.date()}..{until.isoformat()})",
              file=sys.stderr)
    if total_unparseable:
        print(f"FINDING: {total_unparseable} unparseable line(s) across all sessions",
              file=sys.stderr)
    if total_could_not_classify:
        print(f"FINDING: {total_could_not_classify} could-not-classify record(s) "
              "across all sessions", file=sys.stderr)

    if args.summary:
        print(f"\n{'repo':<26}{'sessions':>9}{'turns':>8}{'oper':>7}{'per100':>9}{'peer':>7}")
        by_repo = {}
        for res in all_sessions:
            by_repo.setdefault(res.repo, []).append(res)
        for repo_path in roster:
            repo = Path(repo_path).name
            rows = by_repo.get(repo, [])
            if repo in absent_repos:
                print(f"{repo:<26}{'ABSENT':>9}")
                continue
            if repo in zero_repos:
                print(f"{repo:<26}{'ZERO':>9}")
                continue
            turns = sum(r.assistant_turns for r in rows)
            oper = sum(r.operator_messages for r in rows)
            peer = sum(r.cross_session_inbound for r in rows)
            per100 = (oper / turns * 100) if turns else 0.0
            print(f"{repo:<26}{len(rows):>9}{turns:>8}{oper:>7}{per100:>9.1f}{peer:>7}")
            for r in sorted(rows, key=lambda x: x.first_ts or ""):
                per100_s = f"{(r.operator_messages / r.assistant_turns * 100):.1f}" \
                    if r.assistant_turns else "n/a"
                print(f"    {r.session_ref}  {r.first_ts}..{r.last_ts}  "
                      f"turns={r.assistant_turns} oper={r.operator_messages} "
                      f"per100={per100_s} peer={r.cross_session_inbound}")

    return 3 if (total_unparseable or total_could_not_classify) else 0


if __name__ == "__main__":
    sys.exit(main())
