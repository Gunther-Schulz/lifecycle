#!/usr/bin/env python3
"""Did a verb's output reach the session that ran it? (lc-306 design round)

The fire log records that a verb PRINTED or REFUSED. Callers habitually run
a verb through `grep`, `tail` or `head`, so what the session saw is a
different fact. This tool joins the two records that hold each half:

  * the fire log: which verb ran, when, with what outcome, at which seam;
  * the session transcripts: the Bash call that ran it and the tool result
    the session actually received.

The join key is TIME plus the verb's own words: a fire record at `at`
belongs to the Bash call whose tool_use timestamp is at or before `at` and
whose tool_result timestamp is at or after it, and whose command names the
verb. A record no call matches is UNJOINED and is counted, never dropped.

For every joined record it reports
  * the CALLER SHAPE of that invocation: bare, piped into which filter,
    captured by `$(...)`, and what happened to stderr (free, merged into the
    pipe by `2>&1`, or discarded);
  * DELIVERED: the tool result carries the marker the verb printed. For a
    goal seam the marker is the goal line; for a finding it is the
    `[row]` tag or the words FINDING / COULD NOT VERIFY;
  * for a REFUSED WRITE (outcome 2 on a carrier-writing verb): whether the
    same session ran the same verb to outcome 0 within the follow window.

What it cannot see, said so the output is not over-read:
  * the caller shape is read by pattern over the command text, not by a
    shell parser. A verb inside a loop, a function or a script file is
    classed OTHER;
  * delivered means the marker is IN the tool result. Whether the session
    read it is not observable;
  * a session whose transcript is gone is UNJOINED, not undelivered.

Aggregates go to stdout. `--out` takes one JSON row per joined record and
belongs outside this repo: the rows carry other repos' command text.

Exit 0 with the tables; exit 3 when no fire record fell in the window or no
transcript could be read.
"""
import argparse
import bisect
import collections
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "plugin" / "cli"))

from lifecycle_core import firelog, lanes  # noqa: E402

#: The verbs that write a carrier. A finding from one of these is a REFUSAL:
#: the act did not happen. A finding from any other verb is a report.
WRITE_VERBS = ("item add", "item amend", "item close", "item park",
               "item bench", "item promote", "ledger add", "arc open",
               "arc close", "arc narrow", "arc advance", "arc premise",
               "arc belief", "arc verdict", "arc yield", "arc disposition")
GOAL_MARKER = re.compile(r"^goal(?: \(|: none resolvable)", re.M)
FINDING_MARKER = re.compile(r"FINDING|COULD NOT VERIFY|\[[a-z_]+\]")
FOLLOW = timedelta(minutes=30)
SLACK = timedelta(seconds=2)


def ts(text: str):
    try:
        return datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    except ValueError:
        return None


def result_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(b.get("text", "")) for b in content
                         if isinstance(b, dict))
    return ""


def load_calls(root: Path, since):
    """Every Bash call naming `lifecycle`, in every transcript under `root`
    touched since `since`: `(start, end, command, result)`, sorted by start."""
    calls = []
    files = 0
    floor = since.timestamp()
    for path in root.rglob("*.jsonl"):
        try:
            if path.stat().st_mtime < floor:
                continue
            fh = open(path, encoding="utf-8", errors="replace")
        except OSError:
            continue
        files += 1
        pending = {}
        with fh:
            for line in fh:
                if "lifecycle" not in line and "tool_result" not in line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                msg = rec.get("message")
                content = msg.get("content") if isinstance(msg, dict) else None
                if not isinstance(content, list):
                    continue
                when = ts(rec.get("timestamp", ""))
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if (block.get("type") == "tool_use"
                            and block.get("name") == "Bash"):
                        cmd = str((block.get("input") or {}).get("command", ""))
                        if "lifecycle" in cmd and when is not None:
                            pending[block.get("id")] = (when, cmd)
                    elif block.get("type") == "tool_result":
                        hit = pending.pop(block.get("tool_use_id"), None)
                        if hit is not None and when is not None:
                            calls.append((hit[0], when, hit[1],
                                          result_text(block.get("content"))))
    calls.sort(key=lambda c: c[0])
    return calls, files


def unquoted_run(text: str):
    """`(segment, stop)`: `text` up to its first UNQUOTED separator, with
    quoted spans dropped from the segment, and the separator found (`|`,
    `||`, `&&`, `;`, a newline, or `""` at the end of the text).

    Quote-aware because a verb's own arguments are prose: a `--reason` holds
    semicolons and bars, and a scan that stopped at the first one read a
    piped call as a bare one (measured on the first run of this tool: 12 of
    15 goal seams classed bare had no goal line in their result).
    """
    seg = []
    quote = None
    i = 0
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\" and quote == '"':
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in "'\"":
            quote = ch
        elif ch == "\\":
            i += 2
            continue
        elif text.startswith("||", i) or text.startswith("&&", i):
            return "".join(seg), text[i:i + 2], i + 2
        elif ch in "|;\n":
            return "".join(seg), ch, i + 1
        else:
            seg.append(ch)
        i += 1
    return "".join(seg), "", len(text)


def shape(cmd: str, verb: str):
    """`(shape, filter, stderr)` of the first invocation of `verb` in `cmd`."""
    text = cmd.replace("2>&1", " \x01 ").replace("2>/dev/null", " \x02 ")
    words = r"\s+".join(re.escape(w) for w in verb.split())
    m = re.search(r"lifecycle['\"]?\s+(?:--repo\s+\S+\s+)?" + words, text)
    if m is None:
        return None
    before = text[:m.start()]
    line_start = max(before.rfind("\n"), before.rfind(";")) + 1
    lead = before[line_start:]
    rest = text[m.end():]
    seg, stop, end = unquoted_run(rest)
    stderr = "merged" if "\x01" in seg else "discarded" if "\x02" in seg else "free"
    if lead.rfind("$(") > lead.rfind(")"):
        return ("captured", "-", stderr)
    if re.search(r"\b(for|while|do|if|then)\b", lead):
        return ("other", "-", stderr)
    if stop == "|":
        name = re.match(r"[\w./-]+", rest[end:].lstrip())
        return ("piped", Path(name.group(0)).name if name else "?", stderr)
    if re.search(r">\s*\S", seg.replace("\x01", "").replace("\x02", "")):
        return ("redirected", "-", stderr)
    return ("bare", "-", stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--since", required=True, help="ISO date, inclusive")
    ap.add_argument("--until", default=None, help="ISO timestamp, exclusive")
    ap.add_argument("--transcripts", default=str(Path.home() / ".claude" / "projects"))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    since = ts(args.since if "T" in args.since else args.since + "T00:00:00+00:00")
    until = ts(args.until) if args.until else None
    roster = {ln.strip() for ln in lanes.roster_path().read_text(
        encoding="utf-8").splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")}

    records = []
    malformed = 0
    try:
        with open(firelog.log_path(), encoding="utf-8") as fh:
            for line in fh:
                if '"outcome": 2' not in line and "goal-seam=" not in line \
                        and '"outcome": 0' not in line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    malformed += line.endswith("\n")
                    continue
                if not isinstance(rec, dict) or rec.get("repo") not in roster:
                    continue
                when = ts(rec.get("at", ""))
                if when is None or when < since or (until and when >= until):
                    continue
                records.append((when, rec))
    except OSError:
        print("COULD NOT VERIFY — no readable fire log")
        return 3
    calls, files = load_calls(Path(args.transcripts).expanduser(),
                              since - timedelta(days=1))
    if not records or not calls:
        print(f"COULD NOT VERIFY — {len(records)} fire record(s) in the window, "
              f"{len(calls)} lifecycle call(s) in {files} transcript file(s)")
        return 3
    starts = [c[0] for c in calls]

    def join(when, verb):
        hi = bisect.bisect_right(starts, when + SLACK)
        for i in range(hi - 1, max(hi - 400, -1), -1):
            start, end, cmd, result = calls[i]
            if when - start > timedelta(minutes=12):
                break
            if end + SLACK >= when:
                sh = shape(cmd, verb)
                if sh is not None:
                    return sh, result
        return None, None

    successes = collections.defaultdict(list)
    for when, rec in records:
        if rec.get("outcome") == 0:
            successes[(rec.get("session"), rec.get("verb"))].append(when)

    rows = []
    for when, rec in records:
        verb = str(rec.get("verb", ""))
        seam = "goal-seam=" in str(rec.get("detail", ""))
        finding = rec.get("outcome") == 2
        if not seam and not finding:
            continue
        sh, result = join(when, verb)
        row = {"at": rec.get("at"), "verb": verb, "repo": Path(rec["repo"]).name,
               "session": str(rec.get("session", ""))[:8],
               "class": ("goal-seam" if seam else
                         "refused-write" if verb in WRITE_VERBS else "report-finding"),
               "joined": sh is not None}
        if sh is not None:
            row["shape"], row["filter"], row["stderr"] = sh
            marker = GOAL_MARKER if seam else FINDING_MARKER
            row["delivered"] = bool(marker.search(result))
        if row["class"] == "refused-write":
            row["complied"] = any(
                when < t <= when + FOLLOW
                for t in successes.get((rec.get("session"), verb), ()))
        rows.append(row)

    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"window: {args.since} .. {args.until or 'now'}; roster repos only; "
          f"{files} transcript file(s), {len(calls)} lifecycle call(s); "
          f"fire-log lines skipped as damaged: {malformed}")
    for cls in ("goal-seam", "refused-write", "report-finding"):
        sub = [r for r in rows if r["class"] == cls]
        joined = [r for r in sub if r["joined"]]
        print(f"\n{cls}: {len(sub)} fire record(s), {len(joined)} joined to a "
              f"call, {len(sub) - len(joined)} UNJOINED")
        if not joined:
            continue
        tally = collections.defaultdict(lambda: [0, 0])
        for r in joined:
            key = (r["shape"] if r["shape"] != "piped"
                   else f"piped to {r['filter']}", r["stderr"])
            tally[key][0] += 1
            tally[key][1] += r["delivered"]
        print("  caller shape | stderr | records | marker delivered")
        for key in sorted(tally, key=lambda k: -tally[k][0]):
            n, d = tally[key]
            print(f"  {key[0]} | {key[1]} | {n} | {d}")
        n = len(joined)
        d = sum(r["delivered"] for r in joined)
        print(f"  ALL JOINED | {n} | delivered {d} ({100 * d // n}%)")
        piped = [r for r in joined if r["shape"] == "piped"]
        if piped:
            merged = sum(r["stderr"] == "merged" for r in piped)
            print(f"  of {len(piped)} piped call(s), stderr is merged into the "
                  f"pipe in {merged}, discarded in "
                  f"{sum(r['stderr'] == 'discarded' for r in piped)}, free in "
                  f"{sum(r['stderr'] == 'free' for r in piped)}")
        if cls == "refused-write":
            for label, pick in (("delivered", True), ("not delivered", False)):
                grp = [r for r in joined if r["delivered"] is pick]
                if grp:
                    print(f"  refusal {label}: {len(grp)}; same verb ran clean in "
                          f"the same session within {int(FOLLOW.total_seconds() // 60)}"
                          f" min in {sum(r['complied'] for r in grp)}")
    if args.out:
        print(f"\nrows written: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
