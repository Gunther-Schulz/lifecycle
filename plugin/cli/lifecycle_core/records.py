"""`lifecycle record check` — the investigation record's FORM, mechanized (lc-156).

WHY THIS EXISTS, AND WHY ITS ABSENCE WAS THE POINT. The 2026-09-17 corpus mint
created a lintable carrier — one record per project+arc under
`$XDG_STATE_HOME/claude/investigations/`, five slots, fixed-shape basis lines,
closure by graduation — and its format file stated that the mechanical check
"is lifecycle-plugin work, booked separately". It was not booked. A consumer
named over an unwritten list, which is the assumed-delivery class, occurring
INSIDE the mint built to fight that class. It was caught by the requester
asking whether the write was linted at all, not by anything in the mint.

WHAT IT GRADES, and the boundary is deliberate: the FILE's form. Slot
presence, line shape, the route vocabulary, and the closure gate. It does NOT
grade the `record: +VERIFIED …` reply-line duty, whose trigger — is this reply
diagnosis-continuing? — is judgment-shaped, fails the mechanism bar, and stays
a visible-output convention by the booking's own words.

THE ROUTE TOKEN IS WHAT MAKES "I DON'T KNOW" COUNTABLE (dotfiles
`claude/investigation-record-format.md`, 2026-09-18, which POSTDATES lc-156's
booking and is graded here instead of it). An OPEN line names how its question
gets settled — `ask` (only the reporter can answer), `measure` (exercise the
system), `query` (a record already answers it) — because a probe says WHAT
settles a question and never WHO OR WHAT does. `ask` is the route that stalls
silently: nothing wakes it, and a question nobody asks reads exactly like a
question nobody had. Measured over one arc: ~30h, zero observational
questions, five instruments keyed on mechanism assumptions and silent through
real events; the global rule minted afterwards did not move the rate
(0.27 -> 0.19 per 1000 turns, same instrument both sides). So the waiting
`ask` lines are COUNTED here rather than left for someone to remember.

THE TWO FAILURES THIS FILE IS SHAPED AGAINST, both measured on the real
records before a line of it was written (four records at the live home,
2026-09-18):

  * A RECORD OF PURE PROSE passes every tag-shaped check ever written,
    because a check over tagged lines finds no tagged line to fault. Two of
    the four live records carry ZERO `[TAG]` lines — bullets and paragraphs
    under the right headings. Without `record_line_untagged` below, the
    checker would have called them clean, which is the arc's own signature:
    the wrong answer shaped exactly like the right one.
  * A SLOT HEADING CARRYING AN ANNOTATION (`## GOAL (the requester's words)`)
    is the same slot. A checker demanding a bare heading reports all five
    slots missing on a record that has all five, which is a guard firing on
    legitimate work — it stops the lane and trains the override reflex.

THREE ANSWERS, per record and per run: an unreadable record is COULD NOT
VERIFY and never clean, because a record that could not be read contributes
zero findings, and zero findings is a number shaped exactly like a pass.
"""

import os
import re
from pathlib import Path

from . import exits

#: The five slots, in the format file's order. `CLOSED` is deliberately NOT
#: one of them: a record without it is open, which is the normal state and
#: not a finding.
SLOTS = ("GOAL", "NOW", "ESTABLISHED", "OPEN", "MOVES")

#: daneel's tracker vocabulary, adopted verbatim by the format so a grown
#: record escalates into a daneel run without translation. Closed: a tag
#: outside it is counted by nothing and drains through every gate.
TAGS = ("VERIFIED", "INVALIDATED", "PENDING")

#: The route vocabulary, CLOSED. Written from the format file's own sentence
#: — `route: ask|measure|query` — and not read back out of any record this
#: module grades, which is what keeps the roster's route-set check from
#: comparing a claim against itself.
ROUTES = ("ask", "measure", "query")

#: The heading that marks a record CLOSED and carries its graduation
#: pointers. A HEADING rather than a word anywhere in the text: a closure
#: detector keyed on the word "closed" fires on every record whose NOW or
#: MOVES merely DISCUSSES closing one — the carrier-checker rule this plugin
#: already applies to grade words, which anchor on the slot's position and
#: never on a word occurring anywhere.
CLOSED_SLOT = "CLOSED"

#: The basis separator, as the format writes it. A hyphen is a DIFFERENT
#: character and is not accepted: admitting both would put two spellings of
#: one slot in every record, and a reader could not tell which they were
#: looking at.
BASIS = "—"

_HEADING = re.compile(r'^##+\s+(?P<word>[A-Za-z]+)')
_TAG_LINE = re.compile(r'^\[(?P<tag>[A-Za-z_]+)\]\s*(?P<body>.*)$', re.S)
_ROUTE = re.compile(r'\broute:\s*(?P<route>[A-Za-z]+)')
_PROBE = re.compile(r'\bprobe:\s*\S')


def records_dir() -> Path:
    """`$XDG_STATE_HOME/claude/investigations`, the XDG default applied.

    Resolved at run time rather than hardcoded: the home is tool state
    OUTSIDE every repo and outside `~/.claude/`, and a hardcoded machine path
    is what law 6 forbids in this public tree.
    """
    base = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(base) / "claude" / "investigations"


def logical_lines(raw_lines):
    """Wrapped lines folded into the logical line they continue.

    A continuation is an INDENTED non-empty line, which is how every wrapped
    record in the live home spells one. Without the fold, the second half of
    a wrapped `[VERIFIED]` line is a line carrying no tag — so the checker
    would report an untagged-line finding for every wrap in the corpus, fire
    on legitimate work, and be switched off within a day.
    """
    out = []
    for raw in raw_lines:
        if not raw.strip():
            continue
        if out and (raw[:1].isspace()):
            out[-1] = out[-1] + " " + raw.strip()
            continue
        out.append(raw.rstrip())
    return out


def split_slots(text: str) -> dict:
    """`{SLOT: [logical lines]}` for the slot headings present.

    TERMINATED BY ANY `##` HEADING, not only by a recognised one. A record
    may carry sections the format does not name (`## HELD FOR WAVE-4
    INTEGRATION` is in the live home today); attributing their bodies to
    whichever known slot happened to precede them would grade one slot's
    lines under another's rules — and the reader of the finding would be sent
    to the wrong place in the file.
    """
    out, cur, buf = {}, None, []

    def flush():
        if cur is not None:
            out.setdefault(cur, [])
            out[cur] += logical_lines(buf)

    for raw in text.splitlines():
        m = _HEADING.match(raw.strip())
        if m:
            flush()
            buf = []
            word = m.group("word").upper()
            cur = word if word in (SLOTS + (CLOSED_SLOT,)) else None
            if cur is not None:
                out.setdefault(cur, [])
            continue
        buf.append(raw)
    flush()
    return out


def check_one(path: Path):
    """`(findings, unreadable, waiting_asks)` for one record.

    `findings` are whole message strings, one per CLASS per record rather
    than one per offending line: a record of loose prose yields hundreds of
    line-level faults, and a finding list nobody reads to the end is a
    finding list that reports nothing. Each message therefore carries its
    COUNT and its first instance, which is what a repair starts from.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return [], f"{path.name} — {type(e).__name__}: {e}", 0

    findings = []
    slots = split_slots(text)
    name = path.name

    missing = [s for s in SLOTS if s not in slots]
    if missing:
        findings.append(
            f"FINDING [record_slot_missing] {name}: no `## "
            + "`, `## ".join(missing)
            + "` heading. A record missing a slot answers nothing about it, "
              "and an absent slot reads exactly like an empty one.")

    if "NOW" in slots and not slots["NOW"]:
        findings.append(
            f"FINDING [record_now_empty] {name}: NOW is present and empty. "
            "NOW is the anti-blinders slot — if nothing could kill the "
            "current approach, that is itself the finding, and an empty NOW "
            "does not say it.")

    untagged, bad_tag, unbasised, unrouted, badroute, unprobed = [], [], [], [], [], []
    waiting = 0
    for slot in ("ESTABLISHED", "OPEN"):
        for line in slots.get(slot, []):
            stripped = line.strip()
            m = _TAG_LINE.match(stripped)
            if not m:
                untagged.append(f"{slot}: {stripped[:70]}")
                continue
            tag, body = m.group("tag").upper(), m.group("body")
            if tag not in TAGS:
                bad_tag.append(f"[{m.group('tag')}] {body[:50]}")
                continue
            if BASIS not in body:
                unbasised.append(f"[{tag}] {body[:60]}")
                continue
            if tag != "PENDING":
                continue
            rm = _ROUTE.search(body)
            if not rm:
                unrouted.append(body[:60])
            elif rm.group("route").lower() not in ROUTES:
                badroute.append(f"{rm.group('route')} — {body[:45]}")
            elif rm.group("route").lower() == "ask":
                waiting += 1
            if not _PROBE.search(body):
                unprobed.append(body[:60])

    if untagged:
        findings.append(
            f"FINDING [record_line_untagged] {name}: {len(untagged)} line(s) "
            "in ESTABLISHED/OPEN carry no `[TAG]`. A line is fixed-shape — "
            "tag, one-sentence claim, basis artifact — and prose under the "
            "right heading is what the shape exists to replace: it passes "
            "every check written over tagged lines by having none. First: "
            f"{untagged[0]!r}")
    if bad_tag:
        findings.append(
            f"FINDING [record_tag_unknown] {name}: {len(bad_tag)} line(s) "
            f"carry a tag outside the closed set ({', '.join(TAGS)}). An "
            "unrecognised tag is counted by nothing and drains through every "
            f"gate this checker has. First: {bad_tag[0]!r}")
    if unbasised:
        findings.append(
            f"FINDING [record_line_unbasised] {name}: {len(unbasised)} "
            "tagged line(s) carry no basis after the em dash. A tagged claim "
            "without its basis is precisely what the record exists to "
            f"prevent — the label standing where the evidence should be. "
            f"First: {unbasised[0]!r}")
    if unrouted:
        findings.append(
            f"FINDING [record_route_invalid] {name}: {len(unrouted)} PENDING "
            "line(s) name no `route:`. \"I don't know\" is not a terminal "
            "state — it is a claim about what would make it known, and the "
            f"route says how ({', '.join(ROUTES)}). First: {unrouted[0]!r}")
    if badroute:
        findings.append(
            f"FINDING [record_route_invalid] {name}: {len(badroute)} PENDING "
            f"line(s) name a route outside the closed set "
            f"({', '.join(ROUTES)}). The three carry different costs and "
            "different failure modes, so a fourth word routes the question "
            f"nowhere. First: {badroute[0]!r}")
    if unprobed:
        findings.append(
            f"FINDING [record_probe_missing] {name}: {len(unprobed)} PENDING "
            "line(s) name no `probe:`. A question whose probe is unnamed "
            "cannot be settled by anyone but its author, and a probe "
            "consistent with either answer decides nothing — naming it is "
            f"what makes the question answerable. First: {unprobed[0]!r}")

    if CLOSED_SLOT in slots:
        undrained = [l for l in slots.get("OPEN", [])
                     if l.strip().startswith("[PENDING]")]
        if undrained:
            findings.append(
                f"FINDING [record_closed_undrained] {name}: marked closed "
                f"with {len(undrained)} undrained [PENDING] line(s) in OPEN. "
                "Closure is GRADUATION — open lines land in the item carrier "
                "or take a recorded one-line disposition — never deletion "
                "and never silence.")
        if not slots[CLOSED_SLOT]:
            findings.append(
                f"FINDING [record_closed_unpointed] {name}: marked closed "
                "with no pointer under the heading. A record closes WITH a "
                "pointer to where everything went; a closure that says only "
                "that it happened leaves every graduated line unfindable, "
                "which is the same loss as deleting them.")

    return findings, None, waiting


def cmd_record_check(args, out) -> int:
    d = Path(getattr(args, "dir", None) or records_dir())

    if not d.is_dir():
        out(f"COULD NOT VERIFY: no investigation-record home at {d}. Nothing "
            "was checked, and a run over a home that does not exist is not a "
            "clean result — it is no result.")
        return exits.COULD_NOT_VERIFY

    files = sorted(p for p in d.glob("*.md") if p.is_file())
    if not files:
        out(f"COULD NOT VERIFY: {d} holds no records. A run over nothing "
            "reports that it ran over nothing: 0 of 0 is a number shaped "
            "exactly like a pass.")
        return exits.COULD_NOT_VERIFY

    all_findings, unreadable, waiting = [], [], 0
    for p in files:
        f, bad, w = check_one(p)
        all_findings += f
        if bad:
            unreadable.append(bad)
        waiting += w

    out(f"records: {len(files)} at {d}")
    for line in all_findings:
        out(f"  {line}")
    for bad in unreadable:
        out(f"  COULD NOT VERIFY: {bad}")

    if waiting:
        # NOT a finding. A question legitimately waiting on the reporter is
        # correct work in progress; it is SURFACED because nothing else wakes
        # it. The measured failure is that such a question stalls invisibly,
        # never that it exists — so this line counts them and judges none.
        out(f"  waiting on the reporter: {waiting} OPEN line(s) at "
            "`route: ask`. Nothing wakes an unasked question, and one nobody "
            "asks reads exactly like a question nobody had.")

    # COULD NOT VERIFY OUTRANKS A FINDING, and the order is the point: a run
    # that failed to read part of its input cannot promise the findings below
    # are the complete list. The findings are still printed in full — only
    # the promise of completeness is withdrawn.
    if unreadable:
        out(f"record check: COULD NOT VERIFY — {len(unreadable)} record(s) "
            f"could not be read, {len(all_findings)} finding(s) among the "
            f"{len(files) - len(unreadable)} that could.")
        return exits.COULD_NOT_VERIFY
    if all_findings:
        out(f"record check: {len(all_findings)} finding(s) across "
            f"{len(files)} record(s).")
        return exits.FINDING
    out(f"record check: CLEAN — {len(files)} record(s): five slots each, "
        "every tagged line carrying a basis, every PENDING line routed and "
        "probed, every closure pointed and drained.")
    return exits.CLEAN
