"""The write verbs: `item add` (stage 4) and `item ready|park|close` (stage 5).

INTAKE IS A MERGE (§3.2), NOT AN INSERT. `item add` is the only admission
path — both doors and every detector — and before it writes anything it asks
whether this item is already here. That question is the whole point: a
carrier grows because every sighting of one problem enters as a new row, and
no amount of later pruning recovers the fact that three rows were one.

THE JOIN IS TWO-PHASE BECAUSE THE CALLER IS NOT A PROMPT. The design says
"the caller answers merge-into / supersede / new". A CLI has no dialogue, so
the answer is a flag: an add that finds candidates and carries no `--join`
REFUSES and prints them, with the matching `rejected:` ledger lines beside
each. The refusal IS the question. An add that wrote first and reported the
candidates afterwards would be an insert with a report attached.

WHY `new` COSTS MORE THAN THE OTHER TWO. `new` needs a NAMED ABSENCE — what
the build needs that is not here now — and a one-file, one-hunk write-set
with the session live is vetoed outright: booking that costs what doing it
costs is a deferral refuting itself in its own arithmetic. Operator-mentioned
items skip the VETO, never the join: the operator's intent is authority, but
whether the thing is already booked is a question about the carrier, and
authority does not answer it.

THE MOVE (§3.1) IS APPEND, DELETE, COMMIT — in that order, and the order is
the design rather than an implementation choice. The window between append
and delete holds two copies, which is recoverable; the opposite order would
put the window on the loss side. `check_move_integrity` is what makes that
window visible afterwards.
"""

import posixpath
import re
import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from . import arcs, atomic, exits, firelog, judgment, lanes, ledger, retire
from . import declaration as decl
from . import grammar
from . import items as items_mod
from . import vocab

#: A candidate needs this many shared requirement tokens. ONE would match
#: nearly every pair of items in a repo whose vocabulary is its own domain,
#: and a join that lists forty candidates is a join nobody reads — the
#: over-firing guard that trains the reflex to skip it. Write-set path
#: matching is exact and needs no threshold; this is only for prose.
MATCH_MIN_TOKENS = 2

#: The share of the REST of the carrier above which a token is carried by so
#: many items that it cannot say which item you are looking at (lc-46).
#:
#: THE SHORT STOPWORD LIST'S OWN DEFENCE IS WHAT FAILED, and the repair must
#: not restate it. "The two-token threshold is what actually does the work"
#: holds only while no systematic tail contributes two universal tokens —
#: which is exactly what a migration does: every migrated body ends in
#: `— record: <old carrier>:<line>`, so `record` and `backlog` land in nearly
#: every requirement line at once. Measured over dotfiles' migrated carrier
#: (2026-08-27): of 138 live items, EXACTLY TWO tokens appear in more than 90%
#: of the requirement lines — `record` and `backlog`, 126 each — and
#: `MATCH_MIN_TOKENS` is 2. The migration supplies precisely the threshold,
#: against nearly every item, by construction: an ordinary `item add` returned
#: `join_undisposed` over 126 of 138 live items, and a guard that fires on
#: nearly all legitimate work trains the reflex that kills it (R11).
#:
#: A LONGER STOPWORD LIST IS THE WRONG REPAIR, and the comment above is right
#: about why: it is a second vocabulary, and it would need a new entry for
#: every future migration tail — written after that tail had already flooded
#: somebody's join. Rarity needs no list. A token carried by most of the
#: carrier has no discriminating power BY DEFINITION, whatever it says, so the
#: carrier itself is asked rather than a maintained set of words.
#:
#: MORE THAN HALF, and the number is a MEANING rather than a fit: past half
#: the carrier a token describes the carrier's subject, not this item's. Any
#: cut between a few percent and 90% kills the measured tail, so fitting one
#: to 0.91 would tune the constant to one migration; the majority line is the
#: one that can be stated without the measurement in front of you.
MATCH_MAX_DOC_FRACTION = 0.5

#: THE LEDGER'S DECISION JOIN TAKES A TIGHTER CAP (lc-289, judge ruling
#: "R7 REPAIR FIRST", 2026-09-24). Decision questions are short and share a
#: register — "is", "should", the arc's own nouns — so at the item join's
#: majority line two decisions matched on two boilerplate tokens: 30 of the
#: 50 pre-repair fires were WEAK pairs sharing exactly two. The pinned replay
#: (docs/audits/2026-09-24-lc289-replay-pinned.jsonl) swept the cap and 0.05
#: kept all 11 STRONG pairs while dropping 21 of the 30 WEAK. MEASURED, so
#: unlike the majority line above this IS a fit, to that one population —
#: the replay is its falsifier and a re-run that diverges is a finding.
#: Never a change to MATCH_MIN_TOKENS: the threshold is not what floods.
DECISION_MATCH_MAX_DOC_FRACTION = 0.05

#: Words that carry no discriminating power in a requirement line. Kept
#: short on purpose: a long stopword list is a second vocabulary to maintain,
#: and `MATCH_MAX_DOC_FRACTION` above — not this list and not the token
#: threshold alone — is what carries a systematic tail.
STOPWORDS = frozenset("""
that this with from have been were will would should could when what which
they them then than there their these those into over under after before
because while about above below only just also more most some such very
than does done doing make makes made take takes need needs must never
always where whose whom else same both each other another every
""".split())

_TOKEN = re.compile(r"[a-z0-9][a-z0-9-]{3,}")

#: Write-set sentinels. `UNKNOWN` NEVER matches (§3.2, stated in the design
#: itself) — it means "nobody recorded one", and treating unknown as a match
#: would join every migrated entry to every other. `NONE` never matches
#: either, for the same reason one level over: two items that both realize
#: nowhere are not thereby related.
WRITE_SET_SENTINELS = ("NONE", "UNKNOWN")

SOURCE_OPERATOR = "operator"
SOURCE_SESSION = "session"
DETECTOR_PREFIX = "detector:"


@dataclass
class Ctx:
    repo: Path
    declaration: dict
    prefix: str
    items_path: Path
    done_path: Path
    ledger_path: Path


# --- context ------------------------------------------------------------------

def _kind_home(declaration: dict, kind: str) -> str | None:
    body = (declaration.get("kinds") or {}).get(kind)
    home = body.get("home") if isinstance(body, dict) else None
    return home if isinstance(home, str) and home.strip() else None


def context(repo: Path, declaration: dict, out):
    """`(Ctx, code)` — the homes, resolved THROUGH the declaration.

    The done home is resolved through the top-level `closure-home`, and a
    `done bodies` kind naming a DIFFERENT home is a finding rather than a
    tiebreak. Two spellings of one fact diverge, and the one that diverges
    silently is whichever the reader did not open.
    """
    items_home = _kind_home(declaration, "items")
    if not items_home:
        out("FINDING [kind_stage_undeclared] the `items` kind declares no "
            "`home`, so there is no carrier to write to.")
        return None, exits.FINDING

    closure = declaration.get("closure-home")
    if not isinstance(closure, str) or not closure.strip():
        out("FINDING [declaration_malformed] no `closure-home` in the "
            "declaration. A closure MOVES a body to a home; without the "
            "declaration there is nowhere for it to move to, and a close "
            "that had nowhere to move would be a delete.")
        return None, exits.FINDING

    done_home = _kind_home(declaration, "done bodies")
    # lc-280: compare NORMALISED repo-relative paths, not raw strings —
    # `./ITEMS-DONE.md` beside `closure-home: ITEMS-DONE.md` is ONE home
    # spelled two ways, not two homes over one file. Two genuinely
    # different files still fire; only the SPELLING is folded.
    if (done_home
            and posixpath.normpath(done_home) != posixpath.normpath(closure)):
        out(f"FINDING [closure_home_split] the declaration names TWO closure "
            f"homes: `closure-home` says {closure!r} and the `done bodies` "
            f"kind's `home` says {done_home!r}. One fact, one home — a reader "
            "resolves through whichever it happens to open, and the two "
            "diverge from the moment they disagree.")
        return None, exits.FINDING

    ledger_home = _kind_home(declaration, "ledger lines")
    return Ctx(
        repo=repo,
        declaration=declaration,
        prefix=declaration.get("id-prefix") or "",
        items_path=repo / items_home,
        done_path=repo / closure,
        ledger_path=repo / (ledger_home or "LEDGER.md"),
    ), exits.CLEAN


def _load(path: Path):
    """`(Parsed, why-not)` for a carrier home. An ABSENT home is COULD NOT
    VERIFY, never an empty one: they differ in whether anything was checked."""
    if not path.exists():
        return None, (f"no carrier at {path}. An absent file and an empty one "
                      "are not the same answer, and neither is clean.")
    try:
        return items_mod.parse(path.read_text(encoding="utf-8")), None
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"{path} could not be read ({exc!r})."


# --- origin (§3.1) ------------------------------------------------------------

def origin_repo() -> Path | None:
    """The git work tree containing the CWD — the writer's own repo."""
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return Path(r.stdout.strip()).resolve()


def check_origin(ctx: Ctx, out) -> int:
    """A PUBLIC repo refuses an item whose source cwd is another repo (§3.1).

    The hazard is content crossing INTO a public tree from a private one —
    a requirement line quoting another project's problem, an evidence
    pointer naming its paths. The rule is coarse on purpose: it refuses by
    ORIGIN rather than by inspecting the prose, because "is this sentence
    about another repo" has no predicate and the inspection would be the
    judgment remainder pretending to be a check.
    """
    if ctx.declaration.get("public") is not True:
        return exits.CLEAN
    here = origin_repo()
    if here is None:
        out("COULD NOT VERIFY: this repo declares `public: true`, and the "
            "writer's own repo could not be resolved (cwd is not inside a "
            "git work tree). A foreign-origin item cannot be ruled out, and "
            "an unruled-out foreign origin on a public repo is not clean.")
        return exits.COULD_NOT_VERIFY
    if here != ctx.repo.resolve():
        out(f"FINDING [foreign_origin_item] this repo declares `public: "
            f"true` and the item's source cwd is another repo ({here}). "
            "Items are admitted from inside the repo they belong to: the "
            "requirement, the evidence pointer and the write-set all carry "
            "that repo's vocabulary, and a public tree is where it stops "
            "being retractable.")
        return exits.FINDING
    return exits.CLEAN


# --- the join (§3.2) ----------------------------------------------------------

def write_set_entries(value: str) -> list:
    """The write-set's paths/venues. Comma-separated, sentinels dropped.

    Compared as whole normalized ENTRIES, never by substring: `tools/x.py`
    and `tools/x.py.bak` share a prefix and are not the same write-set, and
    a substring test is a prefix match wearing an equality's costume.
    """
    out = []
    for part in (value or "").split(","):
        p = part.strip()
        if not p or p.upper() in WRITE_SET_SENTINELS:
            continue
        out.append(p)
    return out


def requirement_tokens(value: str) -> set:
    return {t for t in _TOKEN.findall((value or "").lower())
            if t not in STOPWORDS}


def document_frequency(live: list, key: str = "requirement") -> dict:
    """`{token: how many of these bodies' `key` slot carry it}`.

    Read off the CARRIER every call, never a stored or restated list: a
    frequency table cached beside the carrier would age apart from it
    silently, and the whole point of asking rarity instead of a stopword list
    is that the answer maintains itself.

    `key` DEFAULTS TO `requirement`, the item-intake join's own slot, so
    every existing caller — `candidates()` below, and `test_verbs.py`'s
    direct call over `parsed.items` — reads unchanged. R7 (lc-289) is the
    second caller: the ledger's decision join asks the SAME rarity question
    of `decision:` lines, whose slot is `question` rather than `requirement`,
    over a body that is a `ledger.Line` rather than an item — both expose
    `.slots`, which is the only shape this function reads.
    """
    freq: dict = {}
    for it in live:
        for t in requirement_tokens(it.slots.get(key, "")):
            freq[t] = freq.get(t, 0) + 1
    return freq


def informative_tokens(tokens: set, freq: dict, live_count: int,
                       carried_by_this_one: set,
                       max_fraction: float | None = None) -> set:
    """`tokens` minus the ones most of the REST of the carrier also carries.

    THE REST, not the whole carrier, and the exclusion is what keeps a small
    carrier working. Document frequency counts the candidate itself, so in a
    two-item carrier every shared token sits at 100% and a naive fraction
    would drop it — killing exactly the planted-duplicate case the join
    exists for. The question is whether the OTHER items carry the token too;
    with no other items there is nothing to compare against and no token can
    be shown uninformative, so every one is kept. Keeping is the join's
    conservative direction: it lists a candidate for a human to read.

    `max_fraction` is the cap. None — every item-intake caller — reads
    MATCH_MAX_DOC_FRACTION AT CALL TIME rather than as a bound default, so
    a rebinding of the module constant still reaches the item join. The
    ledger's decision join passes DECISION_MATCH_MAX_DOC_FRACTION (lc-289).
    """
    cap = MATCH_MAX_DOC_FRACTION if max_fraction is None else max_fraction
    others = live_count - 1
    if others <= 0:
        return set(tokens)
    keep = set()
    for t in tokens:
        elsewhere = freq.get(t, 0) - (1 if t in carried_by_this_one else 0)
        if elsewhere / others <= cap:
            keep.add(t)
    return keep


def candidates(parsed, requirement: str, write_set: str) -> list:
    """`[(item, [why…])]` — LIVE items this intake may already be.

    Live means an OPEN grade. A closed item is not a merge target: merging
    into it would resurrect a body from the done home, which is a move the
    carrier has no verb for and conservation would not survive.

    TOKENS ARE WEIGHTED BY RARITY ACROSS THE CARRIER (lc-46). A shared token
    that most of the rest of the carrier also carries is dropped before the
    threshold is applied — see `MATCH_MAX_DOC_FRACTION`. The write-set half
    is untouched: path matching is exact, so it has no vocabulary that can
    flood.
    """
    want_paths = set(write_set_entries(write_set))
    want_tokens = requirement_tokens(requirement)
    live = [it for it in parsed.items if it.grade in items_mod.GRADES_OPEN]
    freq = document_frequency(live)
    found = []
    for it in live:
        why = []
        shared_paths = want_paths & set(write_set_entries(
            it.slots.get("write-set", "")))
        if shared_paths:
            why.append("shares write-set " + ", ".join(sorted(shared_paths)))
        its_tokens = requirement_tokens(it.slots.get("requirement", ""))
        shared_tokens = informative_tokens(
            want_tokens & its_tokens, freq, len(live), its_tokens)
        if len(shared_tokens) >= MATCH_MIN_TOKENS:
            why.append(f"shares {len(shared_tokens)} requirement token(s): "
                       + ", ".join(sorted(shared_tokens)))
        if why:
            found.append((it, why))
    return found


def print_candidates(ctx: Ctx, found: list, out) -> None:
    """The join's own screen: every candidate, with its matching `rejected:`
    ledger lines beside it (§3.6's first gated reader).

    The rejected lines are the half that stops a re-proposal: an approach
    already tried and rejected reads, from inside a fresh session, exactly
    like a new idea.
    """
    parsed, why = ledger.read(ctx.ledger_path)
    if parsed is None:
        out(f"  (rejected-line gate COULD NOT RUN: {why})")
    for it, reasons in found:
        out(f"  candidate {it.ident}  [{it.grade}]  line {it.line}")
        out(f"      requirement: {it.slots.get('requirement', '')}")
        out(f"      write-set:   {it.slots.get('write-set', '')}")
        for r in reasons:
            out(f"      match: {r}")
        if parsed is not None:
            hits = ledger.rejected_for(parsed, it.ident)
            if hits:
                for h in hits:
                    out(f"      rejected: {h.slots['approach']} — "
                        f"{h.slots['why']}")
            else:
                out("      rejected: none recorded for this item")


# --- the cost test (§3.2) -----------------------------------------------------

def cost_test(write_set: str, hunks: int | None, source: str,
              blocker_kind: str | None):
    """`(verdict, message)` — verdict in "veto", "clear", "unverified".

    THREE CONJUNCTS, and the ask is owed only where ALL THREE hold (§3.11):
    "write-set <= 1 file AND session live AND no typed blocker -> the tool
    asks 'do it now?'; any other shape -> NEW."

    "A one-file, one-hunk write-set with the session live prints 'do it
    now?'" The tool can see the file count; it cannot see the hunk count, so
    the caller states it — and a caller that does NOT state it leaves the
    test unevaluated, which is COULD NOT VERIFY rather than a pass. That
    distinction is the whole rule: a cost test that silently cleared every
    add it could not evaluate would clear exactly the adds worth vetoing.

    `blocker_kind` is the third conjunct, CLASSIFIED BY THE CALLER — the same
    `items.classify_blocker` call the add verb already makes, rather than a
    second classifier here reading a raw value and a prefix. It is required
    rather than defaulted: a default would let a caller drop the conjunct
    silently, which is the defect this parameter closes.
    """
    entries = write_set_entries(write_set)
    if len(entries) != 1:
        return "clear", (f"cost test: not applicable — the write-set names "
                         f"{len(entries)} path(s); the do-it-now shape is one "
                         "file, one hunk.")
    if blocker_kind not in (None, "none"):
        # THE THIRD CONJUNCT, and it sits AHEAD of the hunk question because
        # the conjunction is ALREADY false: demanding evidence that cannot
        # change the verdict is what left a correctly blocked author with no
        # verb at all — `item park` re-grades an ident that must already
        # exist, and this add refused. A typed blocker names what this
        # session cannot dissolve, so the work is not do-it-now whatever its
        # hunk count, and the item must be bookable in ONE verb with its
        # blocker intact.
        return "clear", (
            f"cost test: not applicable — the item carries a TYPED blocker "
            f"({blocker_kind}), and the rule's third conjunct is NO typed "
            "blocker. What the item waits for is what this session cannot "
            "dissolve, so booking it is the only exit there is.")
    if hunks is None:
        return "unverified", (
            "the write-set names ONE file and the hunk count was not stated "
            "(`--hunks <n>`). A one-file, one-hunk write-set with the session "
            "live is do-it-now, not book-it — and this add cannot tell which "
            "it is. State the hunk count.")
    if hunks != 1:
        return "clear", (f"cost test: clear — one file but {hunks} hunks, "
                         "which is not the do-it-now shape.")
    if source == SOURCE_OPERATOR:
        return "clear", ("cost test: one file, one hunk — DO IT NOW? — but "
                         "the source is the operator, who skips the veto. "
                         "The join above was not skipped and never is.")
    return "veto", (
        f"do it now? The write-set is one file ({entries[0]}) and one hunk, "
        "and the session that can see this is live. Booking it costs about "
        "what doing it costs, so the entry would be the deferral refuting "
        "itself in its own arithmetic. If it genuinely cannot be done here, "
        "the blocker is real and belongs on an `item park`; if the operator "
        "asked for it to be booked, say so with `--source operator`.")


# --- the move (§3.1) ----------------------------------------------------------

def move_to_done(ctx: Ctx, ident: str, closing_grade: str, note: str,
                 out) -> int:
    """Append to the done home, delete from the carrier, commit BOTH.

    ONE ACT, in this order, and the order carries the design's judgment: the
    window between append and delete holds two copies of one body, which the
    next `item check` reports as DUPLICATE and recoverable. Deleting first
    would put the same window on the loss side, where a crash leaves nothing
    to recover and no record that there was anything to recover.

    THE MOVE ALSO CLOSES THE WAIT. A closed item waits for nothing, so
    `blocked-by:` is cleared to NONE — and the done home's own shape check
    then reads any SURVIVING blocker as a body that arrived by a path that is
    not a close, which is the property §3.1's write-rules state about the
    closure home.

    CLEARED IS NOT THE SAME AS ANNOTATED, and only one type earns the
    annotation. An `<item-id>` blocker resolves mechanically on its target's
    DONE and an `evidence` one is re-evaluated each pass, so neither is left
    hanging by a close and annotating them would be noise on every archived
    body. A `decision` blocker sits in the OPERATOR's queue and nothing else
    takes it out of there — that one the caller records as `blocker-moot:`,
    which is a real closed-body slot since this wave rather than an annotation
    nothing checks.

    `note` MAY CARRY SEVERAL LINES, newline-separated (lc-44): a DONE close
    appends `closed-reason:` and `closed-ref:` beside the moot record, and
    they land in the SAME buffer write as the move because a second write
    would leave a body moved without its closure record. The caller composes
    them in `DONE_ONLY_SLOTS` order; this function only appends what it is
    handed.
    """
    items_text = ctx.items_path.read_text(encoding="utf-8")
    kept, body = items_mod.replace_body(items_text, ident)
    if body is None:
        out(f"FINDING [unknown_item] no live block {ident!r} in "
            f"{ctx.items_path.name}.")
        return exits.FINDING

    body = _regrade(body, closing_grade)
    body, _cleared = _clear_blocker(body)
    if note:
        body = body.rstrip("\n") + f"\n{note}\n"

    if not ctx.done_path.exists():
        atomic.write_text(ctx.done_path, f"schema: {items_mod.SCHEMA_FLOOR}\n",
                                 encoding="utf-8")
    done_text = ctx.done_path.read_text(encoding="utf-8")

    # 1. APPEND to the done home — before the tree ever holds one copy fewer.
    done_new = _insert_before_archive(done_text, body)
    atomic.write_text(ctx.done_path, done_new, encoding="utf-8")
    # 2. DELETE from the carrier.
    atomic.write_text(ctx.items_path, kept.rstrip("\n") + "\n", encoding="utf-8")
    out(f"moved {ident} → {ctx.done_path.name} (grade {closing_grade})")
    # 3. COMMIT is the CALLER's, because the act's file set is the caller's:
    # a supersede writes three files and a drop writes three, and committing
    # the pair here would leave the third behind — a ledger line recording a
    # move that the same commit did not contain.
    return exits.CLEAN


def _regrade(body: str, grade: str) -> str:
    lines = body.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("grade:"):
            lines[i] = f"grade: {grade}"
            break
    return "\n".join(lines)


def _clear_blocker(body: str):
    """`(body-with-blocker-NONE, the-old-value-or-empty)`.

    Only a value that was actually a wait is returned: `NONE` and a blank are
    not blockers and there is nothing to record about them.
    """
    lines = body.split("\n")
    old = ""
    for i, ln in enumerate(lines):
        if not ln.startswith("blocked-by:"):
            continue
        value = ln.split(":", 1)[1].strip()
        if value and value != items_mod.BLOCKER_NONE:
            old = value
            lines[i] = f"blocked-by: {items_mod.BLOCKER_NONE}"
        break
    return "\n".join(lines), old


def _insert_before_archive(done_text: str, body: str) -> str:
    """Append a body to the done home's LIVE section.

    Before the archive heading, never after it: the archive holds
    pre-migration bodies verbatim, and a fixed-slot block written into it
    would be exempted from the shape check that is supposed to grade it.
    """
    lines = done_text.split("\n")
    for i, ln in enumerate(lines):
        if ln.strip() == items_mod.ARCHIVE_HEADING:
            head = "\n".join(lines[:i]).rstrip("\n")
            tail = "\n".join(lines[i:])
            return f"{head}\n\n{body.rstrip(chr(10))}\n\n{tail}"
    return done_text.rstrip("\n") + "\n\n" + body.rstrip("\n") + "\n"


#: The env var through which a CALLING SESSION supplies the attribution block
#: its own harness prescribes. It is an env var and not a constant because
#: the block names a MODEL and a SESSION URL, and neither is knowable from
#: inside this process — the verb is invoked BY a session, and a constant
#: compiled in here would attribute every future commit to whatever model was
#: current the day the line was written.
COMMIT_TRAILER_ENV = "LIFECYCLE_COMMIT_TRAILER"

#: The two halves the machine's pre-push guard reads together. Keep these in
#: sync with `dotfiles/git/hooks/pre-push:_ist_subagent_trailer`, which is the
#: CONSUMER — this constant exists to avoid writing the shape it flags.
_COAUTHOR_CLAUDE = "Co-Authored-By: Claude "
_SESSION_TRAILER = "Claude-Session:"


def attribution_block(env=None) -> tuple[str, str]:
    """`(block, warning)` — the AI attribution to append, and what to say.

    WHOLE OR NOTHING, AND THE REASON IS A DIFFERENT TOOL. This machine's
    global pre-push hook decides BOOKED vs UNBOOKED subagent commits by one
    predicate: a `Co-Authored-By: Claude ` trailer WITHOUT a
    `Claude-Session:` trailer. A block supplied with only its first half
    therefore does not merely under-attribute — it FORGES the shape that
    guard acts on, and that hook's own comments record its false-fire budget
    as already spent (10 of 234 desk commits, a union variant decided and
    then withdrawn). So a half block is DROPPED, never written.

    A WARNING, NEVER A REFUSAL. Refusing the commit would leave a carrier's
    halves on disk and uncommitted — the exact split `commit_paths` exists to
    prevent — as a punishment for an unset environment variable. An absent
    trailer is already named on every push by the hook above, so the gap
    stays measured rather than papered over either way.

    The `Claude ` in the first constant is load-bearing: an ordinary HUMAN
    co-author trailer is not the flagged shape and passes through untouched.
    """
    import os
    env = os.environ if env is None else env
    raw = (env.get(COMMIT_TRAILER_ENV) or "").strip()
    if not raw:
        return "", (
            f"no attribution trailer: {COMMIT_TRAILER_ENV} is unset, so this "
            "commit records no AI co-authorship. The pre-push hook names "
            "unmarked commits on every push, so this is visible, not hidden.")
    lines = raw.splitlines()
    claims_claude = any(ln.startswith(_COAUTHOR_CLAUDE) for ln in lines)
    has_session = any(ln.startswith(_SESSION_TRAILER) for ln in lines)
    if claims_claude and not has_session:
        return "", (
            f"attribution DROPPED: {COMMIT_TRAILER_ENV} carries a "
            f"`{_COAUTHOR_CLAUDE.strip()}` trailer with no "
            f"`{_SESSION_TRAILER}` trailer. That pair is exactly what the "
            "pre-push hook reads as an UNBOOKED SUBAGENT commit, so writing "
            "it would forge a finding in another tool. Supply both trailers "
            "or none; committing bare instead.")
    return raw, ""


def conservation_guard(ctx: Ctx, paths, out) -> int:
    """Refuse to COMMIT a carrier whose stored identity has gone SHORT (lc-159).

    THE DANGEROUS CASE IS NOT READING A TRUNCATED CARRIER, IT IS WRITING ONE
    BACK. A cut carrier parses `refused=False` with fewer items and no
    problems, so a verb reads it, edits what it sees, and writes the short
    body back over the good one — converting a recoverable truncation (the
    bodies are still in git) into the carrier's new truth. This guard sits at
    the one place every carrier write already passes through.

    IT NEEDS NO CARRIER-FORMAT CHANGE, which is why this is not a schema
    migration. The count a terminator would have added is ALREADY in the head
    — `baseline`, `added`, `compacted` — and the head sits at the TOP of the
    file, so it survives a truncation that takes the bodies. Measured on this
    repo's own carrier: cut to 400 bytes the head is intact and the parse
    returns 1 item; `conservation()` returns ok=False there and ok=True on the
    full 74-item file. The detector existed and discriminated; only its
    PLACEMENT was missing.

    SHORT ONLY, NEVER SURPLUS, and this is the whole of the law-11 care here.
    The two signs are two diagnoses: SHORT means a body left by a path that is
    not a closure, which is this defect. SURPLUS means the homes hold more
    than was admitted — ORDINARILY an INTERRUPTED CLOSE, where the move
    appends to the done home before deleting from the carrier and the window
    between those two writes legitimately holds both copies; where a surplus
    is not fully explained by such a duplicate, `report_conservation` names
    the second cause instead (lc-267: a body admitted without passing `item
    add`) — this guard is silent on BOTH, and either reading, a guard failing
    on surplus would fire on the design working as designed, and worse, would
    block the very commit that finishes the interrupted move.
    """
    if not any(Path(p) == ctx.items_path for p in paths):
        return exits.CLEAN
    try:
        ip = items_mod.parse(ctx.items_path.read_text(encoding="utf-8"))
        dp = (items_mod.parse(ctx.done_path.read_text(encoding="utf-8"))
              if ctx.done_path.exists() else None)
    except OSError:
        # An unreadable carrier is not this guard's finding to make: the
        # caller that could not read it will say so in its own voice, and
        # inventing a second message here would put two diagnoses on one
        # fault.
        return exits.CLEAN
    c = items_mod.conservation(ip, dp)
    if c["ok"] is not False:
        return exits.CLEAN
    delta = c["actual"] - c["expected"]
    if delta >= 0:
        return exits.CLEAN
    out(f"FINDING [conservation_short] REFUSING TO COMMIT: the carrier's "
        f"identity is SHORT by {-delta} (items {c['items']} + done "
        f"{c['done']} = {c['actual']}, but baseline {c['baseline']} + added "
        f"{c['added']} − compacted {c['compacted']} = {c['expected']}). "
        "Bodies are missing from the files, and committing would make that "
        "the carrier's recorded truth. The write is on disk and NOT "
        "committed, so `git diff` shows exactly what would have landed and "
        "the previous carrier is still at HEAD.")
    return exits.FINDING


def commit_paths(ctx: Ctx, paths, msg: str, out, skip: bool = False,
                 what: str = "the move", stage_new: bool = False) -> int:
    """Commit exactly the files this act wrote, BY PATHSPEC, never the index.

    The index is shared with whatever else is running in this work tree, so
    `git add` then commit would carry a co-writer's staged paths out under
    this message. The pathspec form ignores the index for everything else.

    `what` NAMES THE ACT in the failure message. Every carrier write reaches
    this function now (lc-25), and "the move is on disk but was not
    committed" said over an `item add` sends its reader looking for a move
    that never happened. The ROW is unchanged — the refusal is "written and
    not committed", which is one refusal whichever verb wrote.
    """
    if skip:
        out(f"NOT COMMITTED (--no-commit): {what} is consistent on disk, "
            "but the set is durable together only once committed. A caller "
            "batching writes owns that commit.")
        return exits.CLEAN
    code = conservation_guard(ctx, paths, out)
    if code != exits.CLEAN:
        return code
    rel = [str(p.relative_to(ctx.repo)) for p in paths]
    if stage_new:
        # STAGING EXACTLY THIS ACT'S OWN PATHS IS NOT THE `git add` THIS
        # FUNCTION WARNS ABOUT (lc-231b). The warning above is against
        # staging the INDEX wholesale, which carries a co-writer's paths out
        # under this message; naming the same paths the commit is about to
        # name carries nothing extra by construction.
        #
        # IT IS NEEDED BECAUSE A CARRIER CAN BE NEW. The item homes are
        # always tracked, so a pathspec commit over them has always worked;
        # an arc body is a FILE PER ARC and its first commit is of an
        # untracked path, which `git commit -- <path>` refuses. Measured on
        # the first end-to-end open: "pathspec 'arcs/freeze.md' did not match
        # any file(s) known to git", with the body and counter already
        # consistent on disk — the recording step failing, not the write.
        # It also stages the DELETION half of a move, which is the same
        # question one direction over.
        subprocess.run(["git", "-C", str(ctx.repo), "add", "--"] + rel,
                       capture_output=True, text=True)
    block, warning = attribution_block()
    if warning:
        out(warning)
    full_msg = f"{msg}\n\n{block}" if block else msg
    r = subprocess.run(["git", "-C", str(ctx.repo), "commit", "-m", full_msg,
                        "--"] + rel, capture_output=True, text=True)
    if r.returncode != 0:
        out(f"FINDING [move_uncommitted] {what} is on disk but was NOT "
            f"committed, so its halves are not durable together: "
            f"{(r.stderr or r.stdout).strip()[:300]!r}. The files are "
            "consistent — this is the recording step failing, not the write.")
        return exits.FINDING
    out(f"committed: {msg}")
    return exits.CLEAN


# --- `item add` ---------------------------------------------------------------

def cmd_item_add(args, out, ctx: Ctx) -> int:
    code = check_origin(ctx, out)
    if code != exits.CLEAN:
        return code

    source = args.source or SOURCE_SESSION
    if source not in (SOURCE_SESSION, SOURCE_OPERATOR) and not \
            source.startswith(DETECTOR_PREFIX):
        out(f"FINDING [unknown_source] `--source {source}` is not one of "
            f"{SOURCE_SESSION}, {SOURCE_OPERATOR}, {DETECTOR_PREFIX}<name>. "
            "The doors are closed the same way the grades are: an "
            "unrecognised source would decide the cost test's veto silently.")
        return exits.FINDING

    slots, code = _collect_slots(args, ctx, out)
    if code != exits.CLEAN:
        return code

    parsed, why = _load(ctx.items_path)
    if parsed is None:
        out(f"COULD NOT VERIFY: {why}")
        return exits.COULD_NOT_VERIFY
    done_parsed, done_why = _load(ctx.done_path)

    observed: dict = {}
    code = _check_blocker(slots["blocked-by"], ctx, parsed, done_parsed,
                          done_why, out,
                          not_derivable=getattr(args, "not_derivable", None),
                          observed=observed)
    if code != exits.CLEAN:
        return code
    slots[items_mod.BLOCKER_EXERCISE] = _exercise_record(
        args, slots["blocked-by"], ctx, observed)
    slots[items_mod.NOT_DERIVABLE] = _derivability_record(
        args, slots["blocked-by"], ctx)

    found = candidates(parsed, slots["requirement"], slots["write-set"])
    join = args.join
    if found and not join:
        out(f"FINDING [join_undisposed] intake is a MERGE, and this add "
            f"matches {len(found)} live item(s). Answer with `--join "
            "merge-into <id>`, `--join supersede <id>` or `--join new "
            "--absence \"<what is missing now>\"` — nothing was written.")
        print_candidates(ctx, found, out)
        return exits.FINDING

    if join and join.startswith("merge-into"):
        return _do_merge(args, ctx, parsed, out)
    if join and join.startswith("supersede"):
        return _do_supersede(args, ctx, parsed, slots, out)

    return _do_new(args, ctx, parsed, done_parsed, done_why, slots, source, out)


def _collect_slots(args, ctx: Ctx, out):
    """The seven slots, validated. Grade DERIVED unless stated."""
    slots = {
        "requirement": (args.requirement or "").strip(),
        "goal": (args.goal or "").strip(),
        "write-set": (args.write_set or "").strip(),
        "done-criterion": (args.done_criterion or "").strip(),
        "evidence": (args.evidence or "").strip(),
        "blocked-by": (args.blocked_by or items_mod.BLOCKER_NONE).strip(),
    }

    # THE EFFECTIVE SET, not the declared one (§3.1b): declared ∪ {`tend`}.
    # The reserved value is what a repo files its work on ITSELF under, and
    # nothing declares it — so reading `goals` here would refuse, in every
    # repo, the one goal every repo is supposed to accept.
    goals = decl.effective_goals(ctx.declaration)
    if slots["goal"] and slots["goal"] not in goals:
        out(f"FINDING [dangling_reference] `--goal {slots['goal']}` is not "
            f"one of the goals this repo accepts ({', '.join(goals)}) — "
            f"the declared goals plus the plugin-reserved "
            f"`{decl.RESERVED_GOAL}` (work on the repo's own carrier, "
            "method, hooks, machinery or migration residue). An "
            "item advancing none of the repo's goals is a retire-lane drop "
            "candidate, which is a judgment the carrier can only make "
            "against a declared list.")
        return None, exits.FINDING

    # Slot completeness decides the grade, and UNKNOWN is not complete: it is
    # the migration's marker for "nobody recorded one", and the grade
    # workflow fills it. Treating it as filled would grade a migrated entry
    # READY on a slot nobody has ever written.
    complete = all(slots[s] for s in
                   ("requirement", "goal", "write-set", "done-criterion",
                    "evidence")) and slots["write-set"].upper() != "UNKNOWN"

    if args.grade:
        grade = args.grade
        # THE ARM IS PART OF THE VOCABULARY, so the door admits it (D-3). A
        # closed vocabulary whose OOV value cannot be WRITTEN has not gained
        # an arm at all — the state stays inexpressible and the author does
        # the only thing left, which is to pick the nearest member. That is
        # the neighbour-folding this contract exists to end, and it would
        # happen at the one site that could have recorded the reason.
        #
        # THE MALFORMED CLAIM IS STILL REFUSED, and that is not a detail: an
        # undated instance can never be aged, so it could never become the
        # oldest and the drain could never watch the count reach zero. It
        # would sit in the carrier looking like a recorded state while being
        # unreadable by the mechanism that consumes recorded states.
        if grade not in items_mod.GRADES and not vocab.is_oov(grade):
            if vocab.looks_oov(grade):
                out(f"FINDING [unknown_grade_write] `--grade {grade}` claims "
                    f"the out-of-vocabulary arm but is malformed. The form is "
                    f"`{vocab.OOV_FORM}` — both parts required. The DATE is "
                    "what lets the instance be aged, and the count of these "
                    "is the dispositions-owed figure whose OLDEST entry the "
                    "drain reads; an undated one could never become the "
                    "oldest, so it would sit recorded and uncountable. The "
                    "REASON is what a widening is minted FROM — without it "
                    "the instance is a silent park wearing this mechanism's "
                    "own label.")
            else:
                out(f"FINDING [unknown_grade_write] `--grade {grade}` is not "
                    f"one of the five grades "
                    f"({', '.join(items_mod.GRADES)}), and is not the "
                    f"out-of-vocabulary arm (`{vocab.OOV_FORM}`). The "
                    "vocabulary is CLOSED on write: a word the counter does "
                    "not know is folded into neither open nor closed, and "
                    "the drain triggers read exactly those numbers. If this "
                    "is a state the five grades genuinely cannot say, record "
                    "it AS one — dated, with its reason — rather than "
                    "inventing a sixth word nothing consumes.")
            return None, exits.FINDING
    else:
        grade = "READY" if complete else "NEW"
    slots["grade"] = grade

    if grade == "NEW" and not complete:
        kind, _d = items_mod.classify_blocker(slots["blocked-by"], ctx.prefix)
        if kind in (None, "none"):
            missing = [s for s in ("requirement", "goal", "write-set",
                                   "done-criterion", "evidence")
                       if not slots[s]]
            if slots["write-set"].upper() == "UNKNOWN":
                missing.append("write-set (UNKNOWN)")
            out("FINDING [new_without_typed_blocker] slots are incomplete "
                f"({', '.join(missing)}), so this item is NEW — and a NEW "
                "item carries a TYPED blocker saying what it is waiting for: "
                f"{items_mod.blocker_types_rendered(ctx.prefix)}. An "
                "incomplete item with nothing to wait for is "
                "the entry that ages in nobody's court.")
            return None, exits.FINDING

    for slot in items_mod.SLOTS:
        problem = items_mod.slot_value_problem(slot, slots.get(slot))
        if problem:
            out(f"FINDING [item_shape] {problem}")
            return None, exits.FINDING

    problem = items_mod.evidence_mark_problem(slots.get("evidence"))
    if problem:
        out(f"FINDING [evidence_unmarked] {problem}")
        return None, exits.FINDING
    # THE GRAMMAR CHECK RUNS AFTER THE PRESENCE CHECK AND SEPARATELY (W-9).
    # A slot carrying a valid mark beside a malformed PERISHABLE passes the
    # presence test outright, so this is the only place the malformed one is
    # visible at all.
    problem = items_mod.perishable_grammar_problem(slots.get("evidence"))
    if problem:
        out(f"FINDING [evidence_mark_malformed] {problem}")
        return None, exits.FINDING
    return slots, exits.CLEAN


#: How long the mint's PARSE check may take. `sh -n` reads a program and
#: executes nothing, so it answers in milliseconds; the bound is here because
#: an unbounded child on a write path turns a refusal into a hang. The RUN's
#: own bound is the trigger evaluator's (`lanes.TRIGGER_TIMEOUT_S`), which is
#: the one every later `item ready` pass will spend.
_PARSE_TIMEOUT_S = 10


def _predicate_lint(detail: str, ctx: Ctx, out, observed: dict | None = None) -> int:
    """Refuse an `evidence` blocker whose predicate cannot work (lc-130) or
    cannot FAIL (lc-164).

    TWO REFUSALS, ONE PROBE RUN, and the second is why the first's name is
    not the whole story. lc-130 graded whether the predicate WORKS — parses,
    and does not answer BROKEN. It let the two ANSWERS through
    undifferentiated, so a predicate exiting 0 at the mint minted, and an
    unfalsifiable one (a clause true for every input) is exactly that case:
    it reads UNBLOCKED from the moment it is booked and nothing later can
    tell it from an item whose evidence really did arrive. So the booking
    run's exit code is GRADED here rather than merely survived — 1 is the
    ordinary waiting state and mints, 0 is refused with both readings named,
    `>=2` is BROKEN as before.

    THE RUN IS THE SAME ONE, which the item's own MUST-NOT-MOVE demands: a
    predicate that is slow or has side effects is not run twice, so this
    grades the `t` that lc-130's probe already produced and adds no second
    execution.

    THE DEFECT: prose booked into a shell slot. `item ready` reads it, the
    evaluator reports BROKEN, and until somebody reads that board the item
    waits in nobody's court — measured in a live carrier, where the repair
    came weeks later and by hand. The check belongs at the MINT because that
    is where the author is still holding the text.

    `sh -n` FIRST, AND THAT ORDER IS MEASURED RATHER THAN STYLISTIC. The real
    incident's predicate fails the PARSE (`sh -n` exit 2), so the case this
    verb exists for is caught without executing anything at all. Only a
    predicate that parses earns the one probe run — and a mint that ran an
    unparseable program to find out it was unparseable would be executing
    prose somebody typed into a slot.

    THE PROBE IS THE ONE TRIGGER EVALUATOR, never a second `subprocess.run`
    here. §3.1 says an evidence blocker is "evaluated like a trigger" and
    `item ready` calls that function; a second body behind the contract would
    disagree about the `>=2` BROKEN case first, which is exactly the case this
    lint turns on — a mint that admitted what the reader calls broken would
    have moved the defect rather than closed it.

    NO NEW EXECUTION RISK, and the reason is not that the risk is small: the
    same predicate is already run by `lanes.evaluate_trigger` on every `item
    ready` pass over this item. This adds the FIRST of those runs, not a
    kind of run the item did not already carry.
    """
    try:
        # `/bin/sh` RATHER THAN A PATH LOOKUP, and it is the invocation-mode
        # half of law 5: `lanes.evaluate_trigger` runs the predicate through
        # `subprocess`'s `shell=True`, which is `/bin/sh -c` by construction.
        # A parse check resolving `sh` off PATH could grade the predicate
        # under a different grammar than the one that will run it, and would
        # then pass exactly the program the evaluator cannot read. Not a
        # machine path (R6): this is the interpreter the stdlib itself names.
        p = subprocess.run(["/bin/sh", "-n", "-c", detail],
                           capture_output=True, text=True,
                           timeout=_PARSE_TIMEOUT_S)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        out(f"COULD NOT VERIFY: the evidence predicate ({detail!r}) could not "
            f"be parse-checked ({exc!r}). An unchecked predicate and a good "
            "one are not the same answer, and neither is a refusal.")
        return exits.COULD_NOT_VERIFY
    # ONE DECIDING CONDITION PER REFUSAL, and lc-164 is what forced it. This
    # refusal has TWO firing inputs — prose that does not parse, and a program
    # that parses and answers BROKEN — and each used to `return` from its own
    # branch. That was provable while this lint held ONE refusal: the only
    # mutation that darkened the row was the GATE outside it, because
    # neutralising the parse branch alone just lets prose fall through to the
    # probe, which exits 2 on the same syntax error and emits the same row
    # (measured, twice: by the session that recorded the gate anchor, and
    # again at lc-164's pickup). The moment a SECOND refusal moved in behind
    # that gate, the gate mutation darkened both and proved neither — lc-30's
    # class, and the repair it names is scoping rather than a fallback.
    #
    # So the two inputs compose one verdict and the verdict is tested once.
    # `broken` carries the message rather than a flag: the two inputs deserve
    # different sentences (one is prose in a shell slot, the other a program
    # that runs and answers wrong) and folding them into one text would tell
    # the author the wrong thing about their own predicate.
    broken = None
    t = None
    if p.returncode != 0:
        tail = (p.stderr or p.stdout or "").strip().replace("\n", " ")[:200]
        broken = (f"the evidence predicate ({detail!r}) is not a shell "
                  f"program: `sh -n` exited {p.returncode}. {tail} An "
                  "`evidence` blocker is EXECUTED — §3.1 has it evaluated "
                  "like a trigger — so prose booked into this slot never "
                  "parses, reports BROKEN on every `item ready` pass, and "
                  "leaves the item waiting in nobody's court until a reader "
                  "happens to open the board. If what the item waits for is "
                  "a judgment rather than a fact a command can settle, it is "
                  "a `decision <question>` blocker and belongs in the "
                  "operator's court; if it is a fact, write the command that "
                  "decides it.")
    else:
        # THE PROBE STILL RUNS ONLY BEHIND A CLEAN PARSE — `TheProbeOrdering`
        # pins that with a marker file, and the `else` is what keeps it true.
        t = lanes.evaluate_trigger(detail, cwd=ctx.repo)
        if t.state == lanes.BROKEN:
            exited = (f"exited {t.code}, which §3.3 RESERVES for broken"
                      if t.code is not None else "did not answer at all")
            broken = (f"the evidence predicate ({detail!r}) PARSES but is "
                      f"BROKEN on one probe run: it {exited}. {t.detail} "
                      "`item ready` reads that same code through the same "
                      "evaluator, so this blocker would report BROKEN on "
                      "every pass — a wait that can only expire, never "
                      "clear.")
    # THE BOOKING RUN'S EXIT IS HANDED BACK, NOT RE-DERIVED (lc-175). The
    # exercise record's first third is this live exit, and the caller must not
    # run the predicate a second time to learn it — the MUST-NOT-MOVE above
    # ("a predicate that is slow or has side effects is not run twice") binds
    # the record exactly as it binds the lint.
    #
    # NOT HARDCODED AS 1, though lc-164's grading makes 1 the only exit a
    # CLEAN mint can reach today. A literal here would be a restated constant
    # that keeps reading `live 1` on a day the grading changes — the record
    # would then assert an observation nobody made.
    if observed is not None and t is not None:
        observed["code"] = t.code
    if broken is not None:
        out(f"FINDING [blocker_predicate_broken] {broken}")
        return exits.FINDING
    if t is not None and t.state == lanes.FIRE:
        out(f"FINDING [blocker_predicate_satisfied_at_booking] the evidence "
            f"predicate ({detail!r}) PARSES and EXITS 0 on its booking run, "
            "which the blocker mapping reads as `the evidence ARRIVED`. So "
            "this item is not blocked by it — now, or ever. TWO READINGS "
            "AND THE MINT CANNOT TELL THEM APART, which is why both are "
            "reported rather than one guessed at: either the evidence is "
            "genuinely already in, and the item takes `--blocked-by NONE` "
            "and is schedulable today; or the predicate CANNOT FAIL — a "
            "clause that is true for every input, such as a test over a "
            "command whose output was discarded — and the item would read "
            "UNBLOCKED forever while the thing it waits for had not "
            "happened. NOTHING DOWNSTREAM CAN SEPARATE THEM LATER: `item "
            "ready` sees the same 0 on every pass and reports the item "
            "schedulable, so the last moment either state is visible is "
            "this one, with the author still holding the text. A predicate "
            "that discriminates exits 1 here — the evidence has not arrived "
            "yet — and 0 once it has.")
        return exits.FINDING
    return exits.CLEAN


def _exercise_record(args, blocker: str, ctx: Ctx, observed: dict) -> str:
    """The `blocker-exercise:` value this add writes, or `""` (lc-175).

    THREE PARTS AND TWO AUTHORS, which is the whole design. The LIVE EXIT is
    the tool's own — it ran the predicate a moment ago and is reporting what
    it saw. The TWO CONSTRUCTED ARMS are the author's, supplied through
    `--blocker-exercise`, and the tool never synthesises them: a verb that
    manufactured a positive would be grading its own plant, which is the
    same-parentage defect law 2 exists against, and it is this item's
    MUST-NOT-MOVE in one sentence.

    NO DOOR REFUSAL HERE, deliberately, and the boundary is lc-179's: lc-169
    demands its statement AT THE DOOR and that demand stays exactly as it is.
    This slot's done-criterion asks that an unexercised blocker be VISIBLE,
    which the carrier-wide count answers. Adding a second gate would make
    every new evidence blocker unbookable until its author had constructed two
    arms — a guard firing on legitimate work, which trains the override reflex
    that kills it (law 11).

    EMPTY WHERE THE BLOCKER IS NOT `evidence`: the slot is refused there, so
    composing one would write a block this build's own checker rejects.
    """
    kind, _detail = items_mod.classify_blocker(blocker, ctx.prefix)
    if kind != "evidence":
        return ""
    arms = (getattr(args, "blocker_exercise", None) or "").strip()
    if not arms:
        # THE FORWARD-ONLY DOOR STAMP (D-7 rev., P3). An unexercised blocker
        # used to leave the slot ABSENT, and absence conflated two states the
        # drain must tell apart: an item booked SINCE this discipline existed
        # and still owing its arms, and one booked BEFORE it, whose author
        # never had the opportunity. Counted as one number the second
        # inflates the first, so the figure a desk consults to decide whether
        # it owes work counts work nobody could have done.
        #
        # WHY A STAMP AND NOT A DATE COMPARISON: the population is not
        # computable from the carrier. `Item` carries no booking date, and
        # the attack round measured every evidence-blocked item's requirement
        # slot as undated — there is nothing to compare against. The stamp
        # supplies the missing fact at the only moment anyone holds it,
        # passage through the door, which is why it is FORWARD-ONLY and why
        # nothing is backfilled: a backfilled stamp would assert an
        # opportunity that never happened.
        #
        # IT IS NOT A REFUSAL. lc-179's boundary stands — nothing new refuses
        # here, and an author booking an evidence blocker without arms is
        # doing legitimate work (law 11). The stamp only makes the owing
        # VISIBLE and countable.
        return f"none-yet {_today()}"
    code = observed.get("code")
    live = f"live {code}" if code is not None else "live not-observed"
    return f"{_today()} {live} | {arms}"


def _derivability_record(args, blocker: str, ctx: Ctx) -> str:
    """The `not-derivable:` value this write persists, or `""` (lc-179).

    THE STATEMENT IS ALREADY DEMANDED AND ALREADY VALIDATED — lc-169's door
    refusal runs in `_check_blocker` above and has already refused an empty
    one by the time this is reached. This function does not re-ask, re-grade,
    or reword: it takes the author's own text and gives it a home, which is
    the entire item. Re-validating here would be a second reader of one value
    with its own chance to disagree with the first.

    NOT A SECOND GATE, which is this item's MUST-NOT-MOVE stated as code:
    lc-169's demand keeps its current behaviour and wording, and nothing new
    refuses. An empty return means the blocker is not a decision — the only
    case where this slot has no meaning — never that a statement was missing,
    because a missing one cannot reach this line.

    DATED, because the statement is a claim about what the record held ON A
    DAY. A reader checking it against the world needs to know which world:
    "no precedent exists" is true until one is written, and an undated
    statement silently becomes a claim about today.
    """
    kind, _detail = items_mod.classify_blocker(blocker, ctx.prefix)
    if kind != "decision":
        return ""
    why = (getattr(args, "not_derivable", None) or "").strip()
    if not why:
        return ""
    return why if items_mod.opens_with_date(why) else f"{_today()} {why}"


def _check_blocker(value: str, ctx: Ctx, parsed, done_parsed, done_why, out,
                   not_derivable: str | None = None,
                   observed: dict | None = None) -> int:
    """Typed, LEDGER-STORABLE if it is a decision, NOT-DERIVABLE if it is one,
    and — for an item-id blocker — pointing at an item that IS.

    THE STORABILITY HALF IS lc-49, and the three doors are why it lives here:
    `item add`, `item park` and `item amend` all reach this one function, so a
    per-verb check would have covered exactly the verbs somebody remembered.
    lc-40 closed the MINT (`migrate._ledger_storable`) against the same defect
    and left these three hand-write doors open — measured live, not inferred:
    dotfiles' df-135 reached the carrier carrying the ledger's own slot
    separator, written by `item amend --blocked-by`, which retyped an evidence
    blocker into a decision one (repaired in dotfiles `ec47c3c`).
    """
    kind, detail = items_mod.classify_blocker(value, ctx.prefix)
    if kind is None:
        # THE EXEMPTION BUYS SOMETHING (B9). The BLOCKER slot is the one
        # vocabulary the contract leaves open-ended, and an exemption that
        # bought nothing would just be an unwatched hole. A refusal here is
        # the widening signal for this very vocabulary — somebody reached for
        # a wait no member can express — and until now it was observable only
        # in a desk's scrollback. Recording the ROW NAME in the log's detail
        # field makes refusals-where-no-type-fit COUNTABLE.
        #
        # THE FLOOR IS STATED WHERE THE COUNT IS READ, not here: the fire log
        # is machine-local and best-effort, so this count is a floor on one
        # machine and never a census. A widening cites it; it is not the
        # population.
        judgment_detail = "blocker_untyped"
        firelog.fire("item blocker-untyped", repo=str(ctx.repo),
                     outcome=exits.FINDING, detail=judgment_detail)
        if items_mod.is_blocker_none_synonym(value):
            # lc-266: same repair-token clause as the `item check` door —
            # every OTHER untyped value keeps the text below, unchanged.
            out(f"FINDING [blocker_untyped] `--blocked-by {value!r}` "
                f"{items_mod.BLOCKER_UNTYPED_SYNONYM_CLAUSE}")
            return exits.FINDING
        out(f"FINDING [blocker_untyped] `--blocked-by {value!r}` is not a "
            f"typed blocker. The edge types are closed (§3.1): "
            f"{items_mod.blocker_types_rendered(ctx.prefix)}, or NONE. Prose "
            "is not an edge — an aging item is "
            "routed by whose court it sits in, and prose sits in nobody's.")
        return exits.FINDING
    if kind == "decision":
        # THE PREDICATE IS THE LEDGER'S OWN, imported rather than restated —
        # the same shape and the same reason as `migrate._ledger_storable`: a
        # second spelling of "what the ledger refuses" would age apart from
        # the writer it must agree with, and it would fail in the QUIET
        # direction, this gate passing a question the real writer then
        # refuses.
        why = ledger.check_prose(detail, "the decision question")
        if why:
            out(f"FINDING [blocker_unstorable] {why} The question would go "
                f"into the carrier as `blocked-by: {value}` and nothing could "
                "ever answer it: `ledger add decision` refuses to store it, "
                "and `item ready` resolves a decision blocker by "
                "QUESTION-SLOT EQUALITY — so rephrasing at ANSWER time no "
                "longer matches the blocker it was written to clear. Each "
                "mechanism is right alone; jointly they made 69 of 99 "
                "decision-blocked items permanently unanswerable (lc-40, "
                "measured over dotfiles' carrier 2026-08-27). Rephrase the "
                "QUESTION here, at the mint — this is not escaped or "
                "normalised on your behalf, because an escaped spelling puts "
                "two forms of every value in the file.")
            return exits.FINDING
        # THE DERIVABILITY DEMAND (lc-169). MEASURED at this desk, two of six:
        # of six items blocked on operator decisions, lc-166's answer sat one
        # kind over in this repo's own declaration (the fire log already
        # declares a machine-wide XDG path as a per-repo kind with all seven
        # stages) and lc-158's sat in an audit the same desk had written and
        # pushed. Both waited until the operator said to decide what could be
        # decided. Operator attention neither scales nor parallelizes, so a
        # derivable question routed operator-ward spends the one resource
        # that cannot be replaced.
        #
        # THE PRECEDENT IS `--absence` AND SO IS THE FORM. That demand is a
        # door demand whose product is PRINTED, not persisted, and it works:
        # a peer desk reported the absence slot forced them to write why the
        # work could not be done now, the true answer turned out to be
        # substantive, and they state they would not have written it
        # unprompted. What the required statement buys is the ASKING, at the
        # moment the author still has the record open.
        #
        # THE DEMAND IS FOR THE STATEMENT, NEVER FOR THE ANSWER, which is the
        # boundary that keeps this off the operator's own ground: intent,
        # preference and authority over the irreversible are constitutively
        # theirs, and a question that is genuinely one of those says so in
        # one line and passes. A check grading whether the reason is GOOD
        # would be deciding the kind split by predicate, which is judgment.
        if not (not_derivable or "").strip():
            out("FINDING [decision_not_derivable_unstated] a `decision` "
                "blocker is booked without saying why the question is NOT "
                "DERIVABLE from the record. Pass `--not-derivable \"<why>\"`: "
                "which precedent, ledger entry, audit or declaration you "
                "looked for and did not find — or, where the question is "
                "constitutively the operator's (intent, preference, "
                "authority over an irreversible or outward act), that it is, "
                "in one line. MEASURED HERE, TWO OF SIX: two questions this "
                "desk routed to the operator were answerable from artifacts "
                "the desk already held — one from a precedent one kind over "
                "in the same declaration file, one from an audit the same "
                "desk had written and pushed. Neither author was careless; "
                "nothing asked. The demand is for the STATEMENT and never "
                "for the answer — a genuinely undecidable question passes on "
                "one line, the same way `--join new` passes on a named "
                "absence.")
            return exits.FINDING
    if kind == "evidence":
        # THE THIRD DOOR IS WHY IT IS HERE. `item amend --blocked-by` reaches
        # this function too, and it is the door the design's own table does
        # not name — the same reason the storability half above sits here
        # rather than in the verbs somebody remembered.
        code = _predicate_lint(detail, ctx, out, observed)
        if code != exits.CLEAN:
            return code
    if kind != "item":
        return exits.CLEAN
    if done_parsed is None:
        out(f"COULD NOT VERIFY: `blocked-by {detail}` names an item, and the "
            f"done home could not be read to confirm it exists. {done_why}")
        return exits.COULD_NOT_VERIFY
    known = {it.ident for it in parsed.items} | {
        it.ident for it in done_parsed.items}
    if detail not in known:
        out(f"FINDING [dangling_reference] `blocked-by {detail}` names an "
            "item that is in neither home. A blocker pointing at nothing "
            "reads exactly like one pointing at live work, and it never "
            "resolves — the item waits forever in a court that does not "
            "exist.")
        return exits.FINDING
    dropped = [it for it in done_parsed.items
               if it.ident == detail and it.grade == "DROPPED"]
    if dropped:
        out(f"FINDING [dangling_reference] `blocked-by {detail}` names a "
            "DROPPED item. An item-id blocker resolves on its target's DONE; "
            "a dropped target never reaches DONE, so this blocker can only "
            "expire, never clear.")
        return exits.FINDING
    return exits.CLEAN


def _do_merge(args, ctx: Ctx, parsed, out) -> int:
    target = args.join.split(None, 1)[1].strip() if " " in args.join else ""
    it = next((i for i in parsed.items if i.ident == target), None)
    if it is None:
        out(f"FINDING [unknown_item] `--join merge-into {target}` names no "
            "LIVE item. A merge target must be open: merging into a closed "
            "item would resurrect a body from the done home, and conservation "
            "counts that body on the closed side.")
        return exits.FINDING
    out(f"merged into {it.ident} — NOTHING was written to the carrier.")
    out("    This is intake being idempotent, which is what makes a detector "
        "safe to run twice: the second sighting of one problem is the same "
        "problem, and a second row would make it two.")
    out(f"    {it.ident} [{it.grade}]  {it.slots.get('requirement', '')}")
    # SAID, never left silent (lc-25). Every join answers the commit question
    # in the same closed vocabulary, and this one answers it with nothing to
    # commit — which a reader can only tell from an unrecorded write if the
    # verb says so. "It printed no commit line" was true of BOTH before.
    out("NOT COMMITTED: there is nothing to commit — a merge writes no file. "
        "The carrier is unchanged and the tree is as this run found it.")
    args.fire_detail = f"merge-into {it.ident}"
    return exits.CLEAN


def _do_supersede(args, ctx: Ctx, parsed, slots, out) -> int:
    """The new item supersedes a live one: body to the done home, reason here.

    ROUTED ONE WAY (§3.6). The body is counted in the done home; the reason
    is a ledger line and is outside the conservation identity by
    construction — it is not a body and was never counted. Writing the
    reason into the moved body instead would put a decision inside an
    archive nobody gates on.
    """
    target = args.join.split(None, 1)[1].strip() if " " in args.join else ""
    it = next((i for i in parsed.items if i.ident == target), None)
    if it is None:
        out(f"FINDING [unknown_item] `--join supersede {target}` names no "
            "LIVE item.")
        return exits.FINDING
    problem = ledger.check_prose(args.reason, "the supersede reason")
    if problem:
        out(f"FINDING [ledger_body] {problem}")
        return exits.FINDING

    with items_mod.carrier_lock(ctx.items_path):
        parsed2, why = _load(ctx.items_path)
        if parsed2 is None:
            out(f"COULD NOT VERIFY: {why}")
            return exits.COULD_NOT_VERIFY
        done_parsed, done_why = _load(ctx.done_path)
        compacted, c_why = retire.compacted_home_at(ctx.ledger_path)
        if compacted is None:
            out(f"COULD NOT VERIFY: the compaction record could not be read, "
                f"so an id cannot be proven unused — a compacted id is in "
                f"neither carrier. {c_why}")
            return exits.COULD_NOT_VERIFY
        ident, id_why = items_mod.next_ident(ctx.prefix, parsed2, done_parsed,
                                             compacted)
        if ident is None:
            out(f"COULD NOT VERIFY: {id_why}")
            return exits.COULD_NOT_VERIFY
        if done_parsed is None:
            out(f"COULD NOT VERIFY: the done home could not be read, so an "
                f"id cannot be proven unused. {done_why}")
            return exits.COULD_NOT_VERIFY

        code = _append_item(ctx, ident, slots, out)
        if code != exits.CLEAN:
            return code
        code = move_to_done(ctx, it.ident, "DONE",
                            f"superseded-by: {ident}", out)
        if code != exits.CLEAN:
            return code
        line = ledger.append(ctx.ledger_path, "superseded",
                             {"id": it.ident, "by": ident,
                              "reason": args.reason.strip()})
        out(f"ledger: {line}")
        code = commit_paths(
            ctx, (ctx.items_path, ctx.done_path, ctx.ledger_path),
            f"lifecycle: {ident} supersedes {it.ident}", out,
            skip=args.no_commit)
        if code != exits.CLEAN:
            return code
    args.fire_detail = f"supersede {it.ident} by {ident}"
    return exits.CLEAN


def _do_new(args, ctx: Ctx, parsed, done_parsed, done_why, slots, source, out) -> int:
    absence = (args.absence or "").strip()
    if not absence:
        out("FINDING [new_without_absence] `new` is taken only with a NAMED "
            "absence (`--absence \"…\"`): what the build needs that is not "
            "here NOW — the realizing write is at another desk or repo, "
            "evidence or an operator decision is outstanding, the work needs "
            "a tier this session is not, or its blast radius exceeds this "
            "session's remaining attention. An absence this session can "
            "dissolve is the next step wearing an absence's costume.")
        return exits.FINDING

    blocker_kind, _detail = items_mod.classify_blocker(
        slots["blocked-by"], ctx.prefix)
    verdict, message = cost_test(slots["write-set"], args.hunks, source,
                                 blocker_kind)
    # USE-EVIDENCE AT THE EFFECT SITE (§3.11). The judgment register prices a
    # rule's retirement on its fire rate, and a rate reconstructed later from
    # git or from memory is the shape this design replaced everywhere else —
    # so the record is written where the rule is evaluated, by the code that
    # evaluates it.
    if verdict == "unverified":
        out(f"COULD NOT VERIFY: {message}")
        return exits.COULD_NOT_VERIFY
    if verdict == "veto":
        judgment.record_use("intake-cost-test", "fired", repo=str(ctx.repo),
                            detail="veto")
        out(f"FINDING [cost_test_veto] {message}")
        return exits.FINDING
    if source == SOURCE_OPERATOR and "skips the veto" in message:
        # The operator's own override, which is exactly the evidence the
        # fire-rate review needs: a rule overridden often is one whose
        # predicate is wrong, and it is invisible unless the override is what
        # gets recorded rather than only the fire.
        judgment.record_use("intake-cost-test", "overridden",
                            repo=str(ctx.repo), detail="source=operator")
    out(message)

    if done_parsed is None:
        out(f"COULD NOT VERIFY: the done home could not be read, so a new id "
            f"cannot be proven unused. Ids are immutable across moves, so an "
            f"allocator blind to the closed home re-issues them. {done_why}")
        return exits.COULD_NOT_VERIFY

    with items_mod.carrier_lock(ctx.items_path):
        parsed2, why = _load(ctx.items_path)
        if parsed2 is None:
            out(f"COULD NOT VERIFY: {why}")
            return exits.COULD_NOT_VERIFY
        done2, _w = _load(ctx.done_path)
        compacted, c_why = retire.compacted_home_at(ctx.ledger_path)
        if compacted is None:
            out(f"COULD NOT VERIFY: the compaction record could not be read, "
                f"so an id cannot be proven unused — a compacted id is in "
                f"neither carrier. {c_why}")
            return exits.COULD_NOT_VERIFY
        ident, id_why = items_mod.next_ident(ctx.prefix, parsed2, done2,
                                             compacted)
        if ident is None:
            out(f"COULD NOT VERIFY: {id_why}")
            return exits.COULD_NOT_VERIFY
        code = _append_item(ctx, ident, slots, out)
        if code != exits.CLEAN:
            return code
        out(f"absence named: {absence}")
        # COMMITTED HERE, INSIDE THE LOCK, exactly as the supersede join
        # already did (lc-25). `new` wrote the carrier and said nothing about
        # it, so an add left ` M ITEMS.md` in a SHARED work tree — and the
        # consequence is the one `commit_paths` own docstring names: the
        # dirty carrier rides out under the next co-writer's pathspec commit,
        # under their message. `--no-commit` was advertised on the verb as
        # though a commit were the default for every join; for two of the
        # three joins there was no commit to skip.
        code = commit_paths(ctx, (ctx.items_path,),
                            f"lifecycle: add {ident}", out,
                            skip=args.no_commit, what="the add")
    args.fire_detail = f"new {ident} source={source}"
    return code


def _append_item(ctx: Ctx, ident: str, slots: dict, out) -> int:
    """Write one block and bump `added`. Both, or the identity breaks.

    `added` is the identity's own right-hand side: an add that wrote a body
    without bumping it would leave conservation reporting a short carrier
    forever, and the number it reported would be correct.
    """
    text = ctx.items_path.read_text(encoding="utf-8")
    block = items_mod.render_block(ident, slots)
    text = text.rstrip("\n") + "\n\n" + block
    text, ok = _bump_added(text)
    if not ok:
        out("FINDING [item_shape] the carrier head carries no `added: <n>` "
            "line, so this add could not record itself in the conservation "
            "identity. The head is written by the tool; a carrier missing it "
            "was created by something else.")
        return exits.FINDING
    atomic.write_text(ctx.items_path, text, encoding="utf-8")
    out(f"added {ident} [{slots['grade']}] → {ctx.items_path.name}")
    for slot in items_mod.SLOTS:
        out(f"    {slot}: {slots[slot]}")
    return exits.CLEAN


def _bump_added(text: str):
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if grammar.starts_section(ln):
            break
        if grammar.is_slot(ln, "added"):
            try:
                n = int(ln.split(":", 1)[1].strip())
            except ValueError:
                return text, False
            lines[i] = grammar.render_slot("added", n + 1)
            return "\n".join(lines), True
    return text, False


# --- `item ready` (stage 5) ---------------------------------------------------

def cmd_item_ready(args, out, ctx: Ctx) -> int:
    """PRINTS "READY and unblocked". PROMOTES NOTHING. Both halves are load-bearing.

    READY IS JUDGED, NEVER DERIVED (§3.1). A verb that promoted an unblocked
    NEW item to READY would be deriving a decision-completeness judgment from
    a graph property — and this repo has the recorded failure that produces:
    a queue of 95 entries labelled ready that nobody believed, because the
    label asserted something no one had judged. Blocker clearance decides
    SCHEDULABILITY, which is a different question with a different answer.
    """
    parsed, why = _load(ctx.items_path)
    if parsed is None:
        out(f"COULD NOT VERIFY: {why}")
        return exits.COULD_NOT_VERIFY
    it = next((i for i in parsed.items if i.ident == args.ident), None)
    if it is None:
        out(f"FINDING [unknown_item] no live block {args.ident!r} in "
            f"{ctx.items_path.name}.")
        return exits.FINDING

    done_parsed, done_why = _load(ctx.done_path)
    state, code, note = _blocker_state(it, ctx, parsed, done_parsed, done_why)

    # READY IS REFUSED TO AN ITEM HOLDING AN UNKNOWN SLOT (§3.1), and the
    # refusal is HERE as well as over the carrier: this is the verb a lane
    # calls before scheduling, so the answer it gives is the one that decides
    # whether a migrated entry gets picked up. A slot nobody has ever written
    # is the one thing "a fresh context could execute this now" cannot have
    # been judged over.
    unknown = items_mod.unknown_slots_of(it)
    if it.grade == "READY" and unknown:
        out(f"FINDING [ready_with_unknown_slot] {it.ident} is graded READY "
            "and still holds UNKNOWN in "
            + ", ".join(f"`{s}`" for s in unknown)
            + ". UNKNOWN is the migration's declared marker for a slot nobody "
              "recorded, and the grade workflow fills it BEFORE READY. Not "
              "schedulable, and the grade is the finding rather than the "
              "blocker.")
        code = exits.worst([code, exits.FINDING])

    out(f"{it.ident} [{it.grade}]  {it.slots.get('requirement', '')}")
    out(f"    blocked-by: {it.slots.get('blocked-by', '')}")
    out(f"    {state}")
    if note:
        out(f"    {note}")
    if it.grade == "READY" and state.startswith("UNBLOCKED"):
        out("READY and unblocked — schedulable now.")
    elif it.grade == "READY" and state.startswith("FINDING"):
        # "Blocked" would be the wrong word and the wrong instruction. A
        # BROKEN predicate or a dangling reference is not a wait: nothing
        # will re-evaluate it, so the item sits still while a board that
        # said "blocked" would have a reader waiting for it to clear.
        out("READY, and its blocker is BROKEN — not schedulable, and NOT "
            "waiting either. Nothing will re-evaluate this until the blocker "
            "itself is repaired; a board that called this 'blocked' would "
            "leave a reader waiting for a clearance that cannot arrive.")
    elif it.grade == "READY":
        out("READY but blocked — decision-complete, not schedulable. The "
            "grade is the desk's judgment and is unaffected by the blocker.")
    elif vocab.is_oov(it.grade):
        # THE ARM, RENDERED WITH ITS REASON (D-3). "grade is <arm>, not
        # READY" would be true and useless: it reports the value as a word
        # the verb does not recognise, which is precisely the reading the
        # arm exists to prevent. The REASON is the payload — it is what a
        # widening gets minted from — so a rendering that printed only the
        # count would leave a number with no content behind it.
        oov = vocab.parse_oov(it.grade)
        out(f"NOT SCHEDULABLE — this item's grade is the out-of-vocabulary "
            f"arm, recorded {oov.date}: {oov.reason}")
        out("That is a RECORDED state, not a broken one: the five grades "
            "could not say what this item is, and somebody wrote down what "
            "they could not say instead of filing it under the nearest "
            "word. It leaves the count by being amended away — re-typed to "
            "a real member once one exists, or to a corrected slot — and "
            "the reason above is what a new member would be minted FROM. "
            "`item check` prints how many are owed and which is oldest.")
    else:
        out(f"grade is {it.grade}, not READY. THIS VERB PROMOTES NOTHING: "
            "READY is a judgment the desk makes — a fresh context could "
            "execute this now — and clearing a blocker is not that judgment.")
    return code


def cmd_item_head(args, out, ctx: Ctx) -> int:
    """`item ready --head` — the head, DERIVED. No cap, ever (R22).

    THE CAP IS GONE AND ITS ABSENCE IS THE POINT. `ready-cap` bounded a LABEL,
    and a capped label is escaped by relabelling: this repo's own 2026-08-11
    incident is two entries booked READY, the head reaching 12 against a cap
    of 10, and the repair being to regrade both to a word the cap did not
    count. The cap fought the grading rather than the growth. So the head is
    every READY-and-unblocked item, ORDERED by the declared `head-rule`, and
    what watches growth is flow — `item ratio` and the retire lane's
    grew-without-an-exit finding.

    THE ORDER IS THE WHOLE OUTPUT, so it is printed longhand with the reason
    each item sits where it does. A head that printed a truncated list would
    be the cap again, wearing a listing's clothes.
    """
    parsed, why = _load(ctx.items_path)
    if parsed is None:
        out(f"COULD NOT VERIFY: {why}")
        return exits.COULD_NOT_VERIFY
    done_parsed, done_why = _load(ctx.done_path)

    lead = decl.head_lead_goal(ctx.declaration.get("head-rule"))
    ready = [it for it in parsed.items if it.grade == "READY"]

    # lc-16: THE GOAL FILTER, and the undeclared-goal answer is the point of
    # it. A repo can declare a closed goal set and set a goal per item, then
    # have no way to read the carrier back by it — which breaks the consumer
    # story for any carrier serving more than one audience (reported by the
    # dotfiles desk, whose fire-rate review reads corpus entries out of a
    # carrier that also holds machine and deploy work).
    #
    # AN UNDECLARED GOAL IS COULD NOT VERIFY, NEVER AN EMPTY LISTING. Both
    # return no rows, and they are different answers: one says this repo has
    # no such goal, the other says this goal has no ready work. Folding them
    # together prints a zero that reads exactly like a measurement — the
    # false zero this repo exists to remove — and a typo'd query is the
    # commonest way to produce one.
    want = getattr(args, "goal", None)
    if want:
        declared = decl.effective_goals(ctx.declaration)
        if want not in declared:
            out(f"COULD NOT VERIFY [goal_query_undeclared] {want!r} is not a "
                f"goal this repo declares ({', '.join(declared)}). Nothing "
                "was listed, and that is not the same answer as a declared "
                "goal holding no ready work — which prints an explicit zero.")
            return exits.COULD_NOT_VERIFY
        kept = [it for it in ready
                if (it.slots.get("goal") or "").strip() == want]
        out(f"FILTERED to goal={want}: {len(kept)} of {len(ready)} READY "
            "item(s). This is a VIEW over the head and not the head — a "
            "filtered listing read as the whole is the partial view standing "
            "in for its own body.")
        if not kept:
            out(f"zero: {want!r} is declared and carries no READY item. An "
                "explicit zero, measured over "
                f"{len(ready)} READY item(s) — not an absent listing.")
        ready = kept

    out(f"head-rule: lead-goal {lead!r}"
        + ("" if lead and lead != "none" else
           " — no lead goal declared, so the head is source order"))
    out("NO CAP (R22): every READY item is listed. Growth is watched by FLOW "
        "(`item ratio`, and the retire lane's kind-grew-without-an-exit "
        "finding), never by a size — a cap here bounds the LABEL and is "
        "escaped by relabelling.")
    out("")

    code = exits.CLEAN
    rows = []
    for it in ready:
        unknown = items_mod.unknown_slots_of(it)
        state, st_code, _note = _blocker_state(it, ctx, parsed, done_parsed,
                                               done_why)
        schedulable = state.startswith("UNBLOCKED") and not unknown
        rows.append((it, state, unknown, schedulable))
        code = exits.worst([code, st_code])

    leads = [r for r in rows if lead and lead != "none"
             and (r[0].slots.get("goal") or "").strip() == lead]
    rest = [r for r in rows if r not in leads]
    n = 0
    for group, label in ((leads, f"LEAD ({lead})"), (rest, "the rest")):
        if not group:
            continue
        out(f"--- {label}: {len(group)} item(s)")
        for it, state, unknown, schedulable in group:
            n += 1
            out(f"{n:>3}. {it.ident} [{it.grade}] goal={it.slots.get('goal', '')}"
                f"  {'SCHEDULABLE' if schedulable else 'not schedulable'}")
            out(f"        {it.slots.get('requirement', '')}")
            out(f"        {state}")
            if unknown:
                out("        UNKNOWN slot(s): " + ", ".join(unknown)
                    + " — the grade workflow fills these BEFORE READY.")
                code = exits.worst([code, exits.FINDING])
        out("")

    schedulable_n = sum(1 for r in rows if r[3])
    out(f"head: {len(ready)} READY, {schedulable_n} schedulable now. "
        f"{len(parsed.items)} live item(s) in total.")
    if not ready:
        out("No READY item. THIS VERB PROMOTES NOTHING: READY is the desk's "
            "judgment and an empty head means nothing has been judged "
            "decision-complete, never that the carrier is empty.")
    out(f"item ready --head: {exits.word(code)}")
    return code


#: The retirement tripwire the corpus's own doctrine states — booked far
#: outrunning shipped-plus-dropped, roughly 3:1. A RATIO, never a size: a
#: large carrier draining steadily owes nothing and a small one never
#: draining does.
RATIO_TRIPWIRE = 3.0

#: The window the NET-GROWTH verdict reads flows over (lc-291). The tripwire
#: above catches capture-domination SPIKES only: any sustained ratio between
#: 1:1 and 3:1 grows without bound while it answers CLEAN, which is the
#: silent-toward-passing direction on the growth invariant's own instrument.
#: Seven days is a number nobody has measured, so it is printed as a
#: placeholder rather than as a threshold — the same idiom as retire.py's
#: STALE_PASSES_N.
NET_GROWTH_WINDOW_DAYS = 7
NET_GROWTH_WINDOW_STATUS = ("PLACEHOLDER — lc-291 chose seven days without a "
                            "measurement; a window the carrier's own history "
                            "justifies replaces it")


def _carrier_flow_at(ctx: Ctx, rev: str):
    """`((added, compacted, closed), why-not)` for both carrier homes AT A
    COMMIT, read from git rather than from any cache of past counts.

    THE FLOW IS READ OFF THE CARRIER'S OWN HISTORY because it is the one
    record every clone holds. The fire log is machine-local and its own
    docstring says a lost line is not a verdict, so a window built on it would
    read a clean zero on every machine that did not run the verbs.

    A home absent at `rev` is reported as such: at a cut before the carrier
    existed there is no flow to compare, and a zero there would read as a
    carrier that captured nothing."""
    counts = []
    for path in (ctx.items_path, ctx.done_path):
        try:
            rel = path.resolve().relative_to(ctx.repo.resolve()).as_posix()
        except ValueError:
            return None, f"{path} is outside the repo, so git holds no history of it"
        try:
            r = subprocess.run(["git", "-C", str(ctx.repo), "show",
                                f"{rev}:{rel}"],
                               capture_output=True, text=True)
        except (OSError, subprocess.SubprocessError) as exc:
            return None, f"git could not be run ({exc!r})"
        if r.returncode != 0:
            return None, f"{rel} does not exist at {rev[:12]}"
        counts.append(items_mod.parse(r.stdout))
    items_p, done_p = counts
    added = items_p.head.get("added")
    if added is None:
        return None, f"the carrier head at {rev[:12]} declares no `added: <n>`"
    return (added, items_p.head.get("compacted") or 0,
            len(done_p.items)), None


def _rev_at_or_before(ctx: Ctx, when) -> str | None:
    """The newest commit whose COMMITTER date is at or before `when`."""
    try:
        r = subprocess.run(["git", "-C", str(ctx.repo), "rev-list", "-1",
                            f"--before={when.isoformat()}", "HEAD"],
                           capture_output=True, text=True)
    except (OSError, subprocess.SubprocessError):
        return None
    rev = r.stdout.strip()
    return rev if r.returncode == 0 and rev else None


def _net_growth(ctx: Ctx, now_flow, out) -> int:
    """The DIVERGENCE verdict (lc-291): did the open count grow over the
    window, in BOTH of its halves?

    NET, NEVER THE LIFETIME DIFFERENCE. Capture minus drain since the
    carrier's birth is the open count minus its baseline — a STOCK — so
    grading it would fire forever on any carrier holding work, which is the
    size alarm R22 forbids. Only a delta between two cuts is a flow.

    SUSTAINED MEANS BOTH HALVES, so a single booking burst that later drains
    is not a finding. Drain counts compaction too: `compacted` leaves the done
    home by a recorded exit, and by conservation `Δopen = Δadded − Δdone −
    Δcompacted`, so without it a compaction would read as growth."""
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    window = timedelta(days=NET_GROWTH_WINDOW_DAYS)
    start_rev = _rev_at_or_before(ctx, now - window)
    mid_rev = _rev_at_or_before(ctx, now - window / 2)
    out(f"window: {NET_GROWTH_WINDOW_DAYS} days ({NET_GROWTH_WINDOW_STATUS})")
    if start_rev is None:
        out("COULD NOT VERIFY [net_growth]: no commit is older than the "
            "window, so git holds no cut to read the start flow from — the "
            "repo has no history, or all of it is younger than the window.")
        return exits.COULD_NOT_VERIFY
    start, why = _carrier_flow_at(ctx, start_rev)
    if start is None:
        out(f"COULD NOT VERIFY [net_growth]: the carrier was born inside the "
            f"window — {why}. Its lifetime difference is a stock, never a flow.")
        return exits.COULD_NOT_VERIFY
    mid, why = _carrier_flow_at(ctx, mid_rev)
    if mid is None:
        out(f"COULD NOT VERIFY [net_growth]: the mid-window cut is unreadable "
            f"— {why}.")
        return exits.COULD_NOT_VERIFY

    halves = []
    moved = False
    for label, (a0, c0, d0), (a1, c1, d1) in (
            ("first half ", start, mid), ("second half", mid, now_flow)):
        captured = a1 - a0
        drained = (d1 - d0) + (c1 - c0)
        halves.append(captured - drained)
        moved = moved or bool(captured or drained)
        out(f"{label}: +{captured} captured, {drained} drained, "
            f"net {captured - drained:+d}")
    net = sum(halves)
    if all(h > 0 for h in halves):
        out(f"FINDING [net_growth] the open count grew in BOTH halves of the "
            f"last {NET_GROWTH_WINDOW_DAYS} days, net {net:+d}, while the "
            f"ratio sits under the {RATIO_TRIPWIRE:.0f}:1 tripwire. That band "
            "grows without bound and the spike test never fires in it. The "
            "repair is the same as the tripwire's: a retirement pass — drop "
            "the overtaken, merge duplicates, park what no one will schedule.")
        return exits.FINDING
    if net > 0:
        out(f"ratio: not draining — net {net:+d} over the window, but the "
            "growth is not sustained across both halves, so it is not a "
            "finding yet.")
        return exits.CLEAN
    if not moved:
        # IDLE IS NOT DRAINING. Nothing captured and nothing closed is clean
        # for this trigger, but saying "draining" over it is the verdict text
        # asserting a flow the arithmetic does not contain.
        out("ratio: CLEAN — no flow over the window: nothing captured and "
            "nothing drained, so the open count held.")
        return exits.CLEAN
    out("ratio: CLEAN — the carrier is draining: the open count did not grow "
        "over the window. A large carrier draining steadily owes nothing; "
        "this trigger reads flow, never size.")
    return exits.CLEAN


def cmd_item_ratio(args, out, ctx: Ctx) -> int:
    """`item ratio` — capture against drain, the only growth alarm R22 allows.

    BOTH SIDES ARE FLOWS SINCE THE SAME INSTANT, which is the half that gets
    got wrong: `added` is bumped once per admission and the done home's
    fixed-slot blocks are the closures since the migration, so both count from
    the moment the carrier was created. The ARCHIVE is excluded deliberately —
    it is a STOCK of history, and mixing a stock into a flow ratio is the
    `quota_pressure` defect this repo has already booked against itself.

    THREE ANSWERS. A carrier with no flow at all on either side has no ratio,
    and reporting `0` there would be a number shaped exactly like a healthy
    one.
    """
    parsed, why = _load(ctx.items_path)
    if parsed is None:
        out(f"COULD NOT VERIFY: {why}")
        return exits.COULD_NOT_VERIFY
    done_parsed, done_why = _load(ctx.done_path)
    if done_parsed is None:
        out(f"COULD NOT VERIFY: the done home could not be read, so the DRAIN "
            f"side of the ratio is unknown. An unread done home contributes "
            f"0, and 0 on the drain side is the number that fires the "
            f"tripwire hardest. {done_why}")
        return exits.COULD_NOT_VERIFY

    added = parsed.head.get("added")
    if added is None:
        out("COULD NOT VERIFY: the carrier head declares no `added: <n>`, so "
            "the CAPTURE side of the ratio has no flow figure. A count of "
            "live items is a STOCK and would answer a different question.")
        return exits.COULD_NOT_VERIFY

    closed = len(done_parsed.items)
    archive = items_mod.archive_entries(done_parsed.archive_text)
    census = items_mod.census(parsed)

    out(f"capture (added since the carrier was created): {added}")
    out(f"drain    (closed bodies, archive excluded):    {closed}")
    out(f"archive  (pre-migration stock, NOT in the ratio): {archive}")
    out(f"live: open {census['open']}  closed-in-carrier {census['closed']}  "
        f"unknown-grade {sum(census['unknown'].values())}")
    if added == 0 and closed == 0:
        out("COULD NOT VERIFY: no flow on either side — nothing has been "
            "admitted and nothing closed since this carrier was created. A "
            "ratio here would be an arithmetic accident, and printing 0 would "
            "read exactly like a carrier draining perfectly.")
        out(f"item ratio: {exits.word(exits.COULD_NOT_VERIFY)}")
        return exits.COULD_NOT_VERIFY
    if closed == 0:
        out(f"ratio: {added}:0 — capture with NO drain at all.")
        out(f"FINDING [capture_dominated] {added} admitted and nothing closed "
            "or dropped. This is the kind that GREW WITHOUT AN EXIT EVENT "
            "(R22): the alarm is flow, so the count does not matter and a "
            "small carrier that never drains is exactly the case a cap would "
            "have missed. A recorded DROP clears this as well as a closure "
            "does — the goal is to lose nothing SILENTLY.")
        out(f"item ratio: {exits.word(exits.FINDING)}")
        return exits.FINDING
    ratio = added / closed
    out(f"ratio: {added}:{closed} = {ratio:.2f}:1   (tripwire "
        f"{RATIO_TRIPWIRE:.0f}:1)")
    if ratio > RATIO_TRIPWIRE:
        out(f"FINDING [capture_dominated] booking is outrunning "
            "shipped-plus-dropped past the tripwire. The next session working "
            "this repo owes a retirement pass before new bookings: re-check "
            "stale-risk items against the world, drop the overtaken, merge "
            "duplicates. The trigger reads the RATIO and never the size.")
        out(f"item ratio: {exits.word(exits.FINDING)}")
        return exits.FINDING
    code = _net_growth(ctx, (added, parsed.head.get("compacted") or 0, closed),
                       out)
    out(f"item ratio: {exits.word(code)}")
    return code


#: The closed vocabulary a `grade:` line may carry (lc-45). Reused from
#: `items_mod.GRADES` rather than restated: a second spelling would age
#: apart from the writer it must agree with, exactly the reason
#: `grammar.py`'s own module docstring gives for existing as one module.
_STATUSLINE_KNOWN_GRADES = items_mod.GRADES


def cmd_item_statusline(args, out, ctx: Ctx) -> int:
    """`item statusline` — ONE line fit for a per-prompt render (lc-45).

    THIS RUNS ON EVERY STATUSLINE RENDER IN EVERY REPO that declares this
    plugin, so the shape is a SINGLE line-pass over the carrier's raw text
    using the existing block/slot grammar (`grammar.heading_ident`,
    `grammar.ends_block`, `grammar.is_slot`) — never `_load`
    (`items_mod.parse`), never a cache, never held state. A full parse plus
    the ledger and done-home reads `item ready --head` performs (decision
    blockers, item-id blockers, lead-goal grouping) is too much machinery to
    pay on every prompt; this verb answers a narrower question at a
    narrower cost, and the narrower question is stated exactly rather than
    dressed up as the wider one.

    THE HEAD ID IS A SYNTACTIC APPROXIMATION of `item ready --head`, NOT a
    replica of its judgment, and `item ready --head` IS THE AUTHORITATIVE
    ANSWER wherever the two might disagree — this verb trades that authority
    for a cost a per-prompt render can afford. Schedulable here means
    `grade: READY` and a LITERAL `blocked-by: NONE` on the same block, first
    in file order — no ledger read for a decision blocker, no done-home read
    for an item-id blocker, no lead-goal grouping, NO EVALUATION of an
    `evidence <predicate>` blocker at all. A READY item blocked on an
    unanswered decision or a dangling item-id reads as "not the head" here
    exactly as `item ready --head` would judge it not-schedulable. A READY
    item whose blocker is a BROKEN evidence predicate ALSO reads as merely
    "not the head" here — this verb cannot distinguish that from an ordinary
    wait — where `item ready --head` raises it as its own
    `FINDING [trigger_broken]` (§3.3: >=2 is RESERVED for BROKEN, never a
    quiet wait). Measured concretely (lc-45 dispatch report, executed
    2026-09-11): a two-item carrier — `xx-1` READY blocked by
    `evidence echo 'unterminated` (an unbalanced quote, broken by
    construction), `xx-2` READY blocked by NONE, in that file order — gets
    `2R.0P head xx-2` CLEAN from this verb, while `item ready --head` on the
    SAME carrier prints `xx-1` first with `FINDING [trigger_broken] the
    evidence predicate ("echo 'unterminated") is BROKEN — exit 2` and exits
    FINDING overall. That gap is real and stated here
    rather than silently closed by calling this parity it is not — a caller
    that needs to know WHY nothing is ready, rather than merely THAT nothing
    is, reads `item ready --head`.

    THREE ANSWERS, statusline width, never a pass-shaped number this pass
    could not compute. A carrier this line-pass cannot make sense of —
    unreadable, no recognisable item block at all, or an item block whose
    `grade:` line never arrives before the next heading — answers
    `n/a (<reason>)`, visibly non-numeric, at COULD_NOT_VERIFY: guessing at
    counts a malformed block could have thrown off is exactly the silent
    wrongness this whole file argues against elsewhere. A `grade:` word
    outside `items_mod.GRADES` (the carrier's own closed vocabulary) is a
    FINDING carried as a trailing `!<n>?` — the same third-answer shape
    `backlog-census.py`'s `unknown` bucket applies to one carrier grammar
    over, never folded silently into either count.
    """
    try:
        text = ctx.items_path.read_text(encoding="utf-8")
    except OSError as exc:
        out(f"n/a (cannot read {ctx.items_path.name}: {exc!r})")
        return exits.COULD_NOT_VERIFY

    ready = parked = unknown = 0
    head_id = None
    saw_item = False
    malformed = []
    cur_id = cur_grade = cur_blocked = None

    def _flush():
        nonlocal ready, parked, unknown, head_id
        if cur_id is None:
            return
        if cur_grade is None:
            malformed.append(cur_id)
            return
        if cur_grade == "READY":
            ready += 1
            if head_id is None and cur_blocked == items_mod.BLOCKER_NONE:
                head_id = cur_id
        elif cur_grade == "PARKED":
            parked += 1
        elif (cur_grade not in _STATUSLINE_KNOWN_GRADES
                and not vocab.is_oov(cur_grade)):
            # THE ARM IS NOT AN UNKNOWN WORD (D-3). This counter means
            # "words this carrier's closed vocabulary does not know" — a
            # reading failure somebody must repair — and it renders as a
            # trailing `!<n>?` on a line the operator sees at every prompt.
            # An arm grade is the opposite state: one the vocabulary
            # knowingly cannot say, recorded on purpose with its date and
            # reason. Counting it here would raise a repair flag on the
            # mechanism WORKING, which is the guard-fires-on-legitimate-work
            # shape (law 11) at the most-rendered line in the system.
            #
            # IT GAINS NO COUNTER OF ITS OWN, deliberately: this line is
            # always-on, and the dispositions-owed figure already has a home
            # at `item check`, which prints the count and the oldest date.
            # A second home for it here would be an always-on addition
            # owing an inventory row, to say something the operator can
            # already ask for.
            unknown += 1

    for raw in text.splitlines():
        line = raw.rstrip("\n")
        if grammar.ends_block(line):
            _flush()
            ident = grammar.heading_ident(line)
            if ident is not None:
                saw_item = True
                cur_id = ident
                cur_grade = None
                cur_blocked = items_mod.BLOCKER_NONE
            else:
                # A `##` heading that is NOT a block heading — the archive
                # marker, or a malformed separator `ends_block` still
                # catches (grammar.py's own module docstring) — ends
                # tracking without opening a new block.
                cur_id = None
            continue
        if cur_id is None:
            continue
        if grammar.is_slot(line, "grade"):
            cur_grade = line.split(":", 1)[1].strip()
        elif grammar.is_slot(line, "blocked-by"):
            cur_blocked = line.split(":", 1)[1].strip()
    _flush()

    if not saw_item:
        out(f"n/a (no item block found in {ctx.items_path.name} — the "
            "grade-line regex could not match this carrier's format)")
        return exits.COULD_NOT_VERIFY
    if malformed:
        shown = ", ".join(malformed[:3]) + ("…" if len(malformed) > 3 else "")
        out(f"n/a ({len(malformed)} item block(s) with no `grade:` line "
            f"before the next heading: {shown})")
        return exits.COULD_NOT_VERIFY

    line = f"{ready}R.{parked}P head {head_id or '-'}"
    if unknown:
        out(f"{line} !{unknown}?")
        return exits.FINDING
    out(line)
    return exits.CLEAN


def _blocker_state(it, ctx: Ctx, parsed, done_parsed, done_why):
    """`(state, code, note)` for one item's blocker."""
    value = it.slots.get("blocked-by", "")
    kind, detail = items_mod.classify_blocker(value, ctx.prefix)
    if kind == "none":
        return "UNBLOCKED — no blocker recorded.", exits.CLEAN, ""
    if kind is None:
        if items_mod.is_blocker_none_synonym(value):
            # lc-266's THIRD door: the same clause both refusing doors print,
            # here where the untyped blocker is read most.
            return (f"FINDING [blocker_untyped] {value.strip()!r} "
                    f"{items_mod.BLOCKER_UNTYPED_SYNONYM_CLAUSE}"),\
                exits.FINDING, ""
        return ("FINDING [blocker_untyped] the blocker is prose, not a typed "
                "edge, so nothing can re-evaluate it."), exits.FINDING, ""
    if kind == "external":
        # NEITHER COURT, AND SAYING SO IS THE POINT (D-8, astra-c2). The
        # machine's court promises a predicate somebody could repair; the
        # operator's promises a question somebody could answer. This edge
        # promises neither — it waits on an event in the WORLD, evaluated by
        # nothing by design — and rendering it as either sends a reader
        # hunting for a fix that does not exist. That hunt is precisely what
        # the old `evidence false` spelling caused.
        #
        # THE ENDING IS AN ACT, and it is named HERE because this is where a
        # reader asks "so what clears it?". A predicate-typed wait answers
        # that by being re-run; this one cannot, so the rendering carries the
        # instruction: amend the blocker away with the arrival named. Without
        # this sentence the type would be a permanent silent park under a
        # new word — the exact state it was minted to replace.
        return (f"BLOCKED — in the WORLD's court: {detail!r}. Evaluated by "
                "nothing, by design: no predicate can say whether this has "
                "happened, so nothing will re-run and nothing is broken. It "
                "ENDS by an ACT — when the event arrives, `item amend "
                "--blocked-by NONE --reason` with the arrival named and its "
                "evidence, and the amendment is the record that it happened."
                ), exits.CLEAN, ""
    if kind == "decision":
        # RE-DERIVED FROM THE LEDGER, never read off the stored slot (lc-26).
        # No verb ever took a decision blocker off an item — `item park` only
        # SETS one — so an ANSWERED question left the item reading blocked
        # forever, byte-identical to one nobody had answered. The two states
        # have to differ somewhere, and the ledger is where the answer is
        # already recorded: `item close` writes a `decision:` line for a
        # question it makes moot, and `ledger add decision` for one an
        # operator answers.
        #
        # THE SLOT IS NOT REWRITTEN. Deriving here rather than clearing the
        # blocker keeps ONE home for the fact (invariant 3): the ledger says
        # whether the question is answered, the item says which question it
        # waits on, and a stored "cleared" flag would be a second spelling
        # that goes stale the moment a decision is revisited.
        led, led_why = ledger.read(ctx.ledger_path)
        if led is None:
            return (f"COULD NOT VERIFY — the blocker names a decision "
                    f"({detail!r}) and the ledger could not be read, so "
                    f"whether it has been answered is unknown. Reporting it "
                    f"BLOCKED would be a wait nobody checked. {led_why}"
                    ), exits.COULD_NOT_VERIFY, ""
        # SCOPED TO THIS ITEM, because a MOOT line is not an answer (G4). A
        # close over an unanswered decision writes `→ moot (closed by <id>)`,
        # which records that the question died with THAT item. Read as an
        # answer it unblocked every other live item on the same question.
        answers = ledger.decision_for(led, detail, for_item=it.ident)
        if answers:
            last = answers[-1]
            return (f"UNBLOCKED — the ledger ANSWERS this decision: "
                    f"{detail!r} → {last.slots.get('answer', '')!r} "
                    f"({ctx.ledger_path.name}:{last.lineno}).", exits.CLEAN,
                    "§3.1 has the item re-graded at the desk once a blocker "
                    "clears. THIS VERB PROMOTES NOTHING.")
        moots = ledger.moot_decisions_for(led, detail)
        if moots:
            # NAMED, never folded into the flat "no line names this
            # question" below — that sentence would be FALSE here, and a
            # reader who checked the ledger would find the line it denies.
            where = "; ".join(f"{m.slots.get('answer', '')!r} "
                              f"({ctx.ledger_path.name}:{m.lineno})"
                              for m in moots)
            return (f"BLOCKED — in the OPERATOR's court: {detail!r}. The "
                    f"ledger records this question MOOT — {where} — and a "
                    "moot line is NOT an answer: it says the question died "
                    "with the item whose closure wrote it. This is a "
                    "different item and still needs the answer."
                    ), exits.CLEAN, ""
        return (f"BLOCKED — in the OPERATOR's court: {detail!r}. No "
                f"`decision:` line in {ctx.ledger_path.name} names this "
                "question, so it has not been answered. A decision blocker "
                "never resolves mechanically and is never auto-dropped; it "
                "is surfaced until answered."), exits.CLEAN, ""
    if kind == "evidence":
        # §3.1: an evidence predicate is "evaluated like a trigger". It is
        # evaluated by THE trigger evaluator (§3.3/§3.4, stage 7) — the same
        # function `lane list` calls, never a second one. Two bodies behind
        # one contract would disagree about the >=2 BROKEN case first, and
        # that is the case that decides whether a dead predicate reads as a
        # cleared blocker.
        #
        # THE MAPPING, and it is not the identity. A trigger FIRES (0) when
        # its condition holds; for a blocker, the condition holding is the
        # evidence having ARRIVED — so 0 is UNBLOCKED, not "blocked". 1 is
        # quiet: the evidence is not there yet, and the item waits in the
        # machine's court. >=2 is BROKEN, and BROKEN is a FINDING rather than
        # a wait: a predicate that errors keeps the item parked forever while
        # the board renders it as ordinary waiting.
        t = lanes.evaluate_trigger(detail, cwd=ctx.repo)
        if t.state == lanes.FIRE:
            return (f"UNBLOCKED — the evidence predicate ({detail!r}) FIRED "
                    f"(exit 0): the evidence it names is here.", exits.CLEAN,
                    "§3.1 has the item re-graded at the desk once a "
                    "blocker clears. THIS VERB PROMOTES NOTHING.")
        if t.state == lanes.QUIET:
            return (f"BLOCKED — in the MACHINE's court: the evidence "
                    f"predicate ({detail!r}) is QUIET (exit 1). Re-evaluated "
                    "each pass."), exits.CLEAN, ""
        return (f"FINDING [trigger_broken] the evidence predicate "
                f"({detail!r}) is BROKEN — exit {t.code}, which §3.3 RESERVES "
                f"for broken. {t.detail} A broken predicate is not a quiet "
                "one: folded into 'still blocked', this item would wait "
                "forever while the board showed ordinary waiting."
                ), exits.FINDING, ""
    if done_parsed is None:
        return (f"COULD NOT VERIFY — blocker names {detail}, and the done "
                f"home could not be read to see whether it is DONE. "
                f"{done_why}"), exits.COULD_NOT_VERIFY, ""
    target = next((i for i in list(parsed.items) + list(done_parsed.items)
                   if i.ident == detail), None)
    if target is None:
        return (f"FINDING [dangling_reference] blocker names {detail}, which "
                "is in neither home."), exits.FINDING, ""
    if target.grade == "DONE":
        return (f"UNBLOCKED — {detail} is DONE.", exits.CLEAN,
                "\u00a73.1 has the item return to NEW for re-grade here — a "
                "cleared blocker changes what is knowable about it, so the "
                "grade is re-judged rather than inherited. THAT TRANSITION "
                "IS THE DRAIN LANE'S GRADE WORKFLOW (wave 2), not this "
                "verb: this one promotes and demotes nothing, and a message "
                "that did not say so would leave a reader waiting for a "
                "write that never comes.")
    if target.grade == "DROPPED":
        return (f"FINDING [dangling_reference] blocker names {detail}, which "
                "is DROPPED. An item-id blocker resolves on DONE; a dropped "
                "target never reaches it."), exits.FINDING, ""
    return (f"BLOCKED — in the MACHINE's court: {detail} is {target.grade}. "
            "Re-evaluated each pass."), exits.CLEAN, ""


# --- `item park` (stage 5) ----------------------------------------------------

def cmd_item_park(args, out, ctx: Ctx) -> int:
    """PARKED, and a PARKED item without a typed blocker is a checker finding.

    The refusal is HERE and in the file check both. Here it is cheap and
    names the fix; there it catches the block that reached the file some
    other way. A rule enforced only on the write path is a convention with a
    mechanism's reputation.

    THE BASE SLOT IS NOT ALWAYS THE VALUE IN FORCE (lc-112). This verb writes
    the `blocked-by:` slot line, and `items.parse` resolves an
    `amended-blocked-by:` line LAST-WINS over it — the rule `_effective_blocker`
    below already states in its own words. So on a block carrying such a line
    the write landed on a slot nothing reads: the grade moved to PARKED, the
    verb printed the typed value back and returned CLEAN, and the EFFECTIVE
    blocker stayed whatever the amendment said. Measured n=2 at the drain desk
    2026-09-13 (lc-24 and lc-66, both `amended-blocked-by: 2026-09-12 NONE`):
    park reported success and the very next `item check` reported
    `parked_without_typed_blocker` about the block park had just written. The
    verb's output was true about the slot and false about the item.

    THE CHECK IS THE INVARIANT, ASKED OF THE READER'S OWN RESOLVER. Rather than
    re-implement last-wins here — a second copy of a rule that would drift from
    the first silently — the write is composed in memory and handed back to
    `items.parse`, and the value it puts IN FORCE is compared with the value
    given. A park whose blocker would not govern refuses; one that would
    proceeds, which is every block carrying no amendment and so leaves the
    ordinary path exactly as it was.

    IT REFUSES RATHER THAN WRITING THE SUPERSEDING LINE ITSELF, and the reason
    is in `append_amendment`'s own docstring: an in-place slot write is the
    right shape for "a state transition the tool owns end to end (`item park`'s
    grade)", while "a correction to a value a desk wrote is a DIFFERENT act".
    That act is `item amend`, whose every amendment carries a `--reason`
    BECAUSE the tool has no business inventing one ("The tool writes the slots;
    the SESSION writes the prose, and there is no default here on purpose").
    Appending from here would force park either to invent that reason or to
    spell a second, reason-less amendment shape outside `render_amendment`,
    which is the only place the shape is spelled. The refusal names `item
    amend` instead — the route the desk took by hand on both measured items —
    and after that amendment park succeeds, because the value in force is then
    the value it was given.
    """
    value = (args.blocked_by or "").strip()
    kind, detail = items_mod.classify_blocker(value, ctx.prefix)
    if kind in (None, "none"):
        out("FINDING [parked_without_typed_blocker] `item park` needs a "
            f"TYPED `--blocked-by`: `{ctx.prefix}-<n>`, `decision "
            "<question>`, or `evidence <predicate>`. Prose only — or "
            f"nothing — was given ({value!r}). PARKED says the item is "
            "waiting; the type says WHOSE COURT it waits in, and an item in "
            "nobody's court is the one that ages out silently.")
        return exits.FINDING

    parsed, why = _load(ctx.items_path)
    if parsed is None:
        out(f"COULD NOT VERIFY: {why}")
        return exits.COULD_NOT_VERIFY
    done_parsed, done_why = _load(ctx.done_path)
    observed: dict = {}
    code = _check_blocker(value, ctx, parsed, done_parsed, done_why, out,
                          not_derivable=getattr(args, "not_derivable", None),
                          observed=observed)
    if code != exits.CLEAN:
        return code

    # THE CONDITIONAL SLOTS REACH THIS DOOR TOO (the three-doors repair). This
    # verb DEMANDS them through `_check_blocker` above, so dropping them here
    # made the tool refuse a value and then discard it — and park is the
    # COMMON path for a blocker added after booking, so the mechanism was
    # blind on the route most likely to carry one. Composed by the same two
    # helpers the add door uses, never by a second spelling here.
    conditional = {
        items_mod.BLOCKER_EXERCISE: _exercise_record(args, value, ctx,
                                                     observed),
        items_mod.NOT_DERIVABLE: _derivability_record(args, value, ctx),
    }
    conditional = {k: v for k, v in conditional.items() if v}

    with items_mod.carrier_lock(ctx.items_path):
        text = ctx.items_path.read_text(encoding="utf-8")
        new, ok = _set_slots(text, args.ident, {"grade": "PARKED",
                                                "blocked-by": value},
                             insert=conditional)
        if not ok:
            out(f"FINDING [unknown_item] no live block {args.ident!r} in "
                f"{ctx.items_path.name}.")
            return exits.FINDING
        # THE WRITE IS GRADED BEFORE IT LANDS (lc-112). `new` is the carrier
        # this park would produce; the reader's own resolver says what the
        # blocker in it would BE. Nothing is written on either refusing branch.
        effective = _effective_slot(new, args.ident, "blocked-by")
        if effective is None:
            out(f"COULD NOT VERIFY: {args.ident!r} is in "
                f"{ctx.items_path.name} — the slot write found it — but the "
                "parser does not carry it back, so what the blocker would "
                "resolve to cannot be read. Nothing was written.")
            return exits.COULD_NOT_VERIFY
        if effective != value:
            out("FINDING [park_over_superseding_amendment] `item park` would "
                f"write `blocked-by: {value}` into {args.ident}, and that "
                f"value would NOT govern: the block carries a superseding "
                f"`{items_mod.AMEND_PREFIX}blocked-by:` line, so the blocker "
                f"in force would still be {effective!r}. The park was REFUSED "
                "and nothing was written — the grade did not move. An "
                "amendment supersedes the slot line by design, which is how "
                "the carrier keeps what it used to say; a verb that wrote the "
                "slot anyway would report a state the file does not have. Use "
                f"`item amend {args.ident} --blocked-by {value!r} --reason "
                "<why>` — an amendment IS the value in force — and then `item "
                "park` again, which will then agree with the file. The "
                "`--reason` is not ceremony here: it is the record of why the "
                "earlier blocker stopped being the right one.")
            return exits.FINDING
        atomic.write_text(ctx.items_path, new, encoding="utf-8")
    out(f"{args.ident} → PARKED, blocked-by: {value}")
    args.fire_detail = f"park {args.ident}"
    return exits.CLEAN


# --- `item promote` (lc-39) ---------------------------------------------------

def cmd_item_promote(args, out, ctx: Ctx) -> int:
    """The desk's re-grade — THE ONLY path to READY after admission.

    THERE WAS NO PATH AT ALL, which is the defect this closes. `grade` is
    written once, by `item add`; `item amend` refuses it by design; `item
    ready` reads it and PROMOTES NOTHING. So an item admitted NEW could never
    become READY however complete its slots later grew, and a carrier's head
    was empty by construction — measured over dotfiles: 133 items whose slots
    a desk had filled by amendment, `item ready --head` reporting 2 READY, and
    both of those born complete.

    READY IS JUDGED, NEVER DERIVED (§3.1, law 10), so this is an ACT and not a
    re-derivation. The rejected alternative is on the record: computing the
    grade from slot completeness at read time, which would make READY
    automatic — the label asserting something nobody judged, which is the
    95-entry queue this repo already has the incident for. What the refusals
    below check is that the judgment is POSSIBLE, never that it is correct:
    the desk supplies the judgment and the tool refuses to record one over a
    slot nobody wrote or a wait nobody cleared.

    IT DOES NOT REFUSE AN ALREADY-READY ITEM. A desk re-affirming its own
    judgment is legitimate work, and a guard that fired on it would be a
    guard firing on a non-defect (R11) — the second record is appended beside
    the first, which is what the carrier is for.
    """
    by = (args.by or "").strip()
    reason = (args.reason or "").strip()
    if not by or not reason:
        out("FINDING [promote_without_judgment] `item promote` needs BOTH "
            "`--by` (which desk judged) and `--reason` (why it is "
            f"decision-complete). Got --by {by!r} and --reason {reason!r}. "
            "READY is a judgment, and a judgment nobody signed is a grade "
            "that appeared: the next reader cannot ask the desk that made it, "
            "because the carrier does not say there was one.")
        return exits.FINDING
    for name, value in ((items_mod.PROMOTED_BY, by),
                        (items_mod.PROMOTE_REASON, reason)):
        problem = items_mod.slot_value_problem(name, value)
        if problem:
            out(f"FINDING [item_shape] {problem}")
            return exits.FINDING

    parsed, why = _load(ctx.items_path)
    if parsed is None:
        out(f"COULD NOT VERIFY: {why}")
        return exits.COULD_NOT_VERIFY
    it = next((i for i in parsed.items if i.ident == args.ident), None)
    if it is None:
        out(f"FINDING [unknown_item] no live block {args.ident!r} in "
            f"{ctx.items_path.name}. A CLOSED body is not promotable: the "
            "done home records what was true at closure, and a grade written "
            "there would re-open an item the counts have already drained.")
        return exits.FINDING

    # THE SAME UNKNOWN-SLOT REFUSAL `item ready` applies, at the WRITE path.
    # One refusal, two sites (§3.8c): there it reports a grade already
    # written, here it stops the grade being written. UNKNOWN is the
    # migration's marker for a slot nobody ever recorded, and "a fresh context
    # could execute this now" is the one thing it cannot have been judged over.
    unknown = items_mod.unknown_slots_of(it)
    if unknown:
        out(f"FINDING [ready_with_unknown_slot] {it.ident} still holds UNKNOWN "
            "in " + ", ".join(f"`{s}`" for s in unknown)
            + ". The grade workflow fills every slot BEFORE READY; promoting "
              "over one would record a judgment about a slot nobody has "
              "written.")
        return exits.FINDING

    done_parsed, done_why = _load(ctx.done_path)
    state, st_code, _note = _blocker_state(it, ctx, parsed, done_parsed,
                                           done_why)
    if st_code == exits.COULD_NOT_VERIFY:
        # THE THIRD ANSWER, never folded into the refusal (law 1): "could not
        # read the ledger" and "the item is blocked" are different facts, and
        # a caller reading only the code must be able to tell them apart.
        out(f"COULD NOT VERIFY: {state}")
        return exits.COULD_NOT_VERIFY
    if not state.startswith("UNBLOCKED"):
        out(f"FINDING [promote_while_blocked] {it.ident} is not unblocked, so "
            f"the desk's judgment cannot be recorded yet: {state} A promotion "
            "over a standing blocker records READY against a wait nobody "
            "cleared, and the blocker is the thing that would then be read "
            "through.")
        return exits.FINDING

    date = _today()
    with items_mod.carrier_lock(ctx.items_path):
        text = ctx.items_path.read_text(encoding="utf-8")
        # THE RECORD IS COMPOSED BEFORE THE GRADE (invariant 6: a decision is
        # recorded with its basis BEFORE the act), and both land in ONE write:
        # a crash between two writes leaves either a grade nobody judged or a
        # judgment of a grade that never moved.
        new, ok = items_mod.append_promotion(text, args.ident, date, by, reason)
        if ok:
            new, ok = _set_slots(new, args.ident, {"grade": "READY"})
        if not ok:
            out(f"FINDING [unknown_item] no live block {args.ident!r} in "
                f"{ctx.items_path.name}.")
            return exits.FINDING
        atomic.write_text(ctx.items_path, new, encoding="utf-8")
    out(f"{args.ident} → READY, judged by {by} on {date}.")
    for line in items_mod.render_promotion(date, by, reason):
        out(f"    {line}")
    out("The grade is the DESK's, not this verb's: nothing here derived it "
        "from the slots. `item ready --head` now lists this item.")
    code = commit_paths(ctx, (ctx.items_path,),
                        f"lifecycle: promote {args.ident} to READY", out,
                        skip=args.no_commit, what="the promotion")
    args.fire_detail = f"promote {args.ident}"
    return code


# --- `item amend` (stage 5) ---------------------------------------------------

#: The `item amend` flag for each amendable slot. Spelled once, here, and
#: read by BOTH the argparse wiring and the verb: a second list in `cli.py`
#: would be a slot the parser accepts and the verb never reads, which is
#: silent by construction.
#: THE FLAGS THIS DOOR TURNS INTO AMENDMENTS. Derived for the conditional
#: slots rather than restated, so a third conditional slot cannot be added to
#: `BLOCKER_SLOT_RULES` and silently miss this door — which is the exact
#: defect this mapping is being repaired for.
AMEND_FLAGS = {
    "requirement": "requirement",
    "goal": "goal",
    "write-set": "write_set",
    "done-criterion": "done_criterion",
    "evidence": "evidence",
    "blocked-by": "blocked_by",
    **{slot: slot.replace("-", "_")
       for slot in items_mod.BLOCKER_ONLY_SLOTS},
}


def cmd_item_amend(args, out, ctx: Ctx) -> int:
    """Correct a booked item's slot WITHOUT rewriting what it used to say.

    THE CARRIER WAS APPEND-ONLY BY ACCIDENT (lc-27): `item add` was the only
    writer of a block, so every correction to a booked item was either a
    second item — which is the carrier growing because one problem entered
    three times, the exact failure intake's merge exists to stop — or a hand
    edit, which law 8 forbids and the shape check catches only if it happens
    to break the shape.

    THE AMENDMENT IS A DATED GROUP APPENDED TO THE BLOCK. The earlier
    slot-line is RETAINED verbatim and the new one supersedes it; the parser
    resolves the value in force, so every reader sees the correction and the
    file still records that there was one. One slot amended is the slot-line
    form, several under one reason the dated-block form — the same act, and
    the reason a three-slot correction is one group rather than three.

    `grade` IS NOT AMENDABLE and that is not an omission: READY is judged
    (§3.1, law 10), and an amendment path to the grade would be a second
    writer of the one slot the judgment lives in.
    """
    reason = (args.reason or "").strip()
    if not reason:
        out("FINDING [amend_without_reason] `item amend` needs a `--reason`. "
            "An amendment is a correction to something a desk decided, and "
            "the record of WHY is what separates it from an in-place rewrite "
            "with a date on it. The tool writes the slots; the SESSION writes "
            "the prose, and there is no default here on purpose.")
        return exits.FINDING
    problem = items_mod.slot_value_problem(items_mod.AMEND_REASON, reason)
    if problem:
        out(f"FINDING [item_shape] {problem}")
        return exits.FINDING

    updates = {}
    for slot, attr in AMEND_FLAGS.items():
        value = getattr(args, attr, None)
        if value is not None:
            updates[slot] = value.strip()
    if not updates:
        out("FINDING [amend_nothing_to_amend] `item amend` names no slot to "
            "amend. The amendable slots are "
            + ", ".join(f"`--{s}`" for s in items_mod.AMENDABLE_SLOTS)
            + ". An amend that wrote a reason and no value would put a "
              "decision line in the carrier and change nothing, which reads "
              "in every later diff as a correction that was made.")
        return exits.FINDING

    for slot, value in updates.items():
        problem = items_mod.slot_value_problem(slot, value)
        if problem:
            out(f"FINDING [item_shape] {problem}")
            return exits.FINDING

    # THE SECOND DOOR, and it is the one that matters most for this rule:
    # `amended-evidence` is the most-amended slot in this carrier, so the
    # evidence a lane actually reads is often the amended value rather than
    # the booked one. A mark demanded at `add` and not here would leave the
    # read-most value unmarked.
    if "evidence" in updates:
        problem = items_mod.evidence_mark_problem(updates["evidence"])
        if problem:
            out(f"FINDING [evidence_unmarked] {problem}")
            return exits.FINDING
        # AND AT THIS DOOR TOO, for the reason the block above gives: the
        # amended value is the one a lane actually reads, and the
        # re-derivation that clears a flag is itself written here — so a
        # malformed mark introduced BY a re-derivation would be the one
        # nobody could ever clear.
        problem = items_mod.perishable_grammar_problem(updates["evidence"])
        if problem:
            out(f"FINDING [evidence_mark_malformed] {problem}")
            return exits.FINDING

    # The SAME declared-goal check `item add` applies. A goal that was
    # refused at intake and accepted at amendment would make the amendment
    # the way around the check rather than the way to fix a value.
    goals = decl.effective_goals(ctx.declaration)
    if "goal" in updates and updates["goal"] not in goals:
        out(f"FINDING [dangling_reference] `--goal {updates['goal']}` is not "
            f"one of the goals this repo accepts ({', '.join(goals)}) — the "
            f"declared goals plus the plugin-reserved `{decl.RESERVED_GOAL}`.")
        return exits.FINDING

    parsed, why = _load(ctx.items_path)
    if parsed is None:
        out(f"COULD NOT VERIFY: {why}")
        return exits.COULD_NOT_VERIFY
    it = next((i for i in parsed.items if i.ident == args.ident), None)
    if it is None:
        out(f"FINDING [unknown_item] no live block {args.ident!r} in "
            f"{ctx.items_path.name}. A CLOSED body is not amendable: the done "
            "home holds what was true when the item closed, and correcting it "
            "there would edit a record other counts already read.")
        return exits.FINDING

    # The SAME typed-blocker gate `item park` and `item add` apply. Without
    # it `item amend --blocked-by` is the quiet way past
    # `parked_without_typed_blocker`, and a prose blocker put an item in
    # nobody's court by a third door.
    if "blocked-by" in updates:
        done_parsed, done_why = _load(ctx.done_path)
        code = _check_blocker(updates["blocked-by"], ctx, parsed,
                              done_parsed, done_why, out,
                              not_derivable=getattr(args, "not_derivable",
                                                    None))
        if code != exits.CLEAN:
            return code

    # A FIRST VALUE IS AN ADDITION, NOT AN AMENDMENT — the carrier says so
    # itself: `amended-<slot>:` over a slot the block does not carry is a
    # finding, "an addition wearing a correction's clothes". That refusal is
    # right and is not being worked around. The conditional slots are exactly
    # the population it bites: a block parked before the slot existed carries
    # no line to supersede, and that is the population most needing repair.
    #
    # SO THEY SPLIT BY WHAT THE BLOCK ALREADY HAS: present, the value is a
    # genuine correction and travels as an amendment, superseded text
    # retained; absent, the base line is INSERTED and no amendment is written,
    # because there is nothing yet to correct. The split is computed from the
    # block on disk, never from the caller's intent.
    present = {it.ident: it.slots for it in parsed.items}.get(args.ident, {})
    additions = {s: updates.pop(s) for s in list(updates)
                 if s in items_mod.BLOCKER_ONLY_SLOTS and s not in present}

    # THE RE-TYPING DOOR OWNS THE CLEAR (P3, attack r2 B2). A conditional
    # slot is legal beside ONE blocker type; re-typing away from that type
    # strands it, recording an act that cannot have happened. Computed from
    # the NEW value against the slot rules rather than from a list of pairs,
    # so a third conditional slot cannot be added and silently miss this.
    stranded = []
    if "blocked-by" in updates:
        new_kind, _d = items_mod.classify_blocker(updates["blocked-by"],
                                                  ctx.prefix)
        for slot_, (want, _row, _what) in items_mod.BLOCKER_SLOT_RULES.items():
            if slot_ in present and new_kind != want:
                stranded.append(slot_)
                # The caller may also be amending the slot this re-type is
                # about to strand; writing it and then dropping it would be
                # two acts disagreeing inside one amendment.
                updates.pop(slot_, None)
                additions.pop(slot_, None)

        # AND THE DOOR SWINGS BOTH WAYS. A re-type INTO `evidence` is passage
        # through a stamping door exactly as a fresh booking is: the item now
        # carries a predicate and owes its arms. Unstamped it would be filed
        # under PREDATES THE MECHANISM — the carrier asserting nobody had the
        # opportunity at the very moment somebody did, and then not asking
        # for the work it had just become owed.
        #
        # ONLY WHERE THERE IS NOTHING THERE: an existing record is somebody's
        # written arms, and a stamp saying they are missing would overwrite
        # the evidence it exists to report the absence of.
        if (new_kind == "evidence"
                and items_mod.BLOCKER_EXERCISE not in present
                and items_mod.BLOCKER_EXERCISE not in updates
                and items_mod.BLOCKER_EXERCISE not in additions):
            additions[items_mod.BLOCKER_EXERCISE] = _exercise_record(
                args, updates["blocked-by"], ctx, {})

    # ONE DECIDING CONDITION PER REFUSAL (lc-164's rule), NOT A SECOND DOOR.
    # A `[amend_nothing_to_amend]` refusal used to sit here too — added by
    # fa6ea7e's conditional-slot work — re-deciding the exact question line
    # 2298 already answered. `additions` is populated ONLY by popping OUT of
    # `updates` (a few lines above) or by the stamping door just above this
    # comment, so `updates` starting empty (line 2298's own condition)
    # implies `additions` is still empty here too, unconditionally. And once
    # "blocked-by" is part of `updates` it can never leave: the stranding
    # loop above pops the CONDITIONAL slots it invalidates, never
    # "blocked-by" itself, which is only read and classified. So there is no
    # real input where `updates` is non-empty at line 2298 and both `updates`
    # and `additions` are empty here — this branch could never fire on
    # anything but the case its neighbour already refused.
    # PROVED BY EXECUTION, not merely by this reading (lc-251's done-
    # criterion demanded the probe before the removal): a line tracer on this
    # exact source line, driven across ten real `item amend` invocations —
    # no slot flag, one ordinary slot, both blocker-retype directions with
    # the conditional slots stranded / freshly added / re-supplied /
    # untouched, additions-only amendments, and a re-type clearing the
    # blocker outright — never observed `updates` and `additions` both empty
    # here. Removed rather than merged, exactly as lc-164 repaired
    # `blocker_predicate_broken`: one deciding condition is what keeps
    # `tools/prove-rows.py`'s existing `amend_nothing_to_amend` arrangement
    # (line 2298's `if not updates:`, unchanged) provable again.

    date = _today()
    with items_mod.carrier_lock(ctx.items_path):
        text = ctx.items_path.read_text(encoding="utf-8")
        if stranded:
            text, ok = _set_slots(text, args.ident, {}, remove=stranded)
            if not ok:
                out(f"FINDING [unknown_item] no live block {args.ident!r} in "
                    f"{ctx.items_path.name}.")
                return exits.FINDING
            out("cleared by the re-type: "
                + ", ".join(f"`{s}:`" for s in stranded)
                + " — the slot is legal only beside its own blocker type, "
                  "and this amendment changes the type. The clear happens "
                  "HERE because the door that re-types is the only one that "
                  "knows; left behind, the line records an act that cannot "
                  "have happened and the shape check refuses the block.")
        if additions:
            text, ok = _set_slots(text, args.ident, {}, insert=additions)
            if not ok:
                out(f"FINDING [unknown_item] no live block {args.ident!r} in "
                    f"{ctx.items_path.name}.")
                return exits.FINDING
        if not updates:
            atomic.write_text(ctx.items_path, text, encoding="utf-8")
            out(f"amended {args.ident} — {len(additions)} slot(s) ADDED, "
                "dated by their own value. No amendment line: a slot the "
                "block did not carry has nothing to supersede.")
            for slot, value in additions.items():
                out(f"    {slot}: {value}")
            code = commit_paths(ctx, (ctx.items_path,),
                                f"lifecycle: amend {args.ident}", out,
                                skip=args.no_commit, what="the amendment")
            args.fire_detail = f"amend {args.ident} {','.join(sorted(additions))}"
            return code
        new, ok = items_mod.append_amendment(text, args.ident, date, reason,
                                             updates)
        if not ok:
            out(f"FINDING [unknown_item] no live block {args.ident!r} in "
                f"{ctx.items_path.name}.")
            return exits.FINDING
        atomic.write_text(ctx.items_path, new, encoding="utf-8")
        out(f"amended {args.ident} — {len(updates)} slot(s), dated {date}. The "
            "earlier line(s) are RETAINED; the new one supersedes.")
        for line in items_mod.render_amendment(date, reason, updates):
            out(f"    {line}")
        code = commit_paths(ctx, (ctx.items_path,),
                            f"lifecycle: amend {args.ident}", out,
                            skip=args.no_commit, what="the amendment")
    args.fire_detail = f"amend {args.ident} {','.join(sorted(updates))}"
    return code


def _today() -> str:
    """Today, ISO. Its own function so a test can hold the date still without
    reaching into `datetime`, and so the one call site is visible."""
    return date.today().isoformat()


def _set_slots(text: str, ident: str, updates: dict, insert: dict | None = None,
               remove: tuple | list = ()):
    """Rewrite named slots of one block IN PLACE. `(text, found)`.

    `insert` IS FOR SLOTS THAT MAY NOT EXIST YET — the conditional blocker
    slots, which a block acquires only when its blocker gains the matching
    type. `updates` cannot serve them: it rewrites lines that are ALREADY
    there, so a block without the line kept its value silently dropped, which
    is the defect this parameter repairs. Present, the line is rewritten in
    place; absent, it is inserted directly after the fixed run, which is where
    `items.render_block` puts it — one layout, whichever door wrote it.

    In place, and only the named slots: rendering the whole block from a
    parsed dict would rewrite every slot the tool did not mean to touch, and
    a slot rewritten identically is still a slot this act claimed authorship
    of in the diff.

    THE BLOCK IS FOUND AND ENDED BY THE SAME GRAMMAR (lc-40), which it was
    not: the search used the `## <id>` regex and the write loop ended on
    `startswith("## ")`. Those disagree on exactly one input — a heading whose
    separator is not a single space, which the reader's regex has always
    accepted — and where they disagreed this function wrote straight through
    the next block. Measured 2026-08-28 against the old code: a carrier whose
    second block heading is `##\txx-2`, and `item park xx-1` set `grade:
    PARKED` and the blocker on xx-2 as well, exit 0 and no finding. Both ends
    now come from `grammar`, and `ends_block` is the WIDE reading on purpose —
    a block's own body lines never begin with `##`.
    """
    lines = text.split("\n")
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == grammar.ARCHIVE_HEADING:
            break
        found = grammar.heading_ident(ln)
        if found is None:
            continue
        if found == ident:
            start = i
            continue
        if start is not None:
            break
    if start is None:
        return text, False
    i = start + 1
    pending = dict(insert or {})
    dropping = tuple(remove or ())
    dropped = []
    last_fixed = None
    while i < len(lines) and not grammar.ends_block(lines[i]):
        # REMOVAL IS THE INVERSE OF `insert`, AND ONLY FOR CONDITIONAL SLOTS
        # (P3). A conditional slot exists only while the blocker carries the
        # matching type, so a re-type that changes the type leaves a line
        # recording something that cannot have happened — the misplacement
        # the shape check refuses. The caller that CHANGES the type is the
        # only one that can know, so the re-typing door owns the clear.
        #
        # NOT A BREACH OF APPEND-ONLY, and the distinction is what makes this
        # safe: append-only protects the RECORD of what a desk decided — the
        # fixed slots and their `amended-` history, every one of which stays
        # verbatim. This line is not a record, it is a CONDITIONAL
        # ANNOTATION whose precondition just stopped holding, and the same
        # door already INSERTS one when the precondition starts holding. A
        # carrier that could grow an annotation and never shed it would
        # accumulate exactly the stranded slots this part exists to prevent.
        if any(grammar.is_slot(lines[i], s) for s in dropping):
            dropped.append(lines[i])
            del lines[i]
            continue
        for slot, value in updates.items():
            if grammar.is_slot(lines[i], slot):
                lines[i] = grammar.render_slot(slot, value)
        for slot in list(pending):
            if grammar.is_slot(lines[i], slot):
                lines[i] = grammar.render_slot(slot, pending.pop(slot))
        # THE ANCHOR IS THE LAST FIXED-RUN LINE, never "the end of the block":
        # a block's tail can already carry amendment, promotion and closure
        # lines, and an insert after those would put a base slot BELOW its own
        # amendments — which `_resolve_amendments` reports as an amendment
        # among the fixed slots, a finding manufactured by the writer.
        if any(grammar.is_slot(lines[i], s) for s in items_mod.SLOTS):
            last_fixed = i
        i += 1
    if pending and last_fixed is not None:
        for offset, (slot, value) in enumerate(pending.items()):
            lines.insert(last_fixed + 1 + offset,
                         grammar.render_slot(slot, value))
    return "\n".join(lines), True


# --- `item close` (stage 5) ---------------------------------------------------

def _effective_slot(text: str, ident: str, slot: str):
    """The value `items.parse` puts IN FORCE for one slot of one block.

    `None` where the block is not in the parsed carrier at all — the third
    answer, kept separate from a slot that resolves to something: "the parser
    does not carry this block" and "the blocker is X" are different facts, and
    a caller that could not tell them apart would read an unreadable carrier as
    an answer.

    IT TAKES TEXT RATHER THAN A PATH so a caller can grade a write BEFORE it
    lands (`item park`, lc-112): the question "would the value I am about to
    write be the value in force?" is only askable of the carrier as it WOULD
    be. Reading the file instead would answer about the carrier as it is,
    which is the state nobody is asking about.

    THE RESOLUTION RULE IS NOT RESTATED HERE, and that is the point. Last-wins
    over an `amended-<slot>:` line lives in `items._resolve_amendments`; a
    second copy in this module would be a paraphrase that drifts the first time
    either changes. `_effective_blocker` below reads the same resolved slot for
    the same reason, one question narrower.
    """
    try:
        parsed = items_mod.parse(text)
    except (ValueError, TypeError):
        return None
    it = next((i for i in parsed.items if i.ident == ident), None)
    if it is None:
        return None
    return it.slots.get(slot)


def _effective_blocker(ctx: Ctx, ident: str):
    """`(kind, detail)` of the blocker a close is about to end, or `(None, "")`.

    Read off the LIVE block before the move, because after the move the
    block is in the done home and this run would be asking a different file
    the same question. THE VALUE IS THE EFFECTIVE ONE — `items.parse`
    resolves an `amended-blocked-by:` line last-wins over the slot line — and
    that is the whole point: `move_to_done` clears the slot LINE, so the base
    value is gone by the time anything downstream could look, while an amended
    value survives the close untouched (lc-90, measured at 11a8c1d).

    THIS REPLACES `_moot_decision`, WHOSE DOCSTRING CARRIED THE FALSE PREMISE
    (lc-90). It read: "Only `decision` blockers qualify: an `<item-id>` blocker
    resolves mechanically on its target's DONE and an `evidence` one is
    re-evaluated each pass, so neither is left hanging by a close." Nothing
    resolves an item-id blocker — no verb rewrites the closing body's
    `blocked-by`, no verb refused the close, and an amended one reached the
    done home alive, where `item amend` correctly refuses to repair it. That
    sentence is what made the defect reasonable to its author, so it goes with
    the code rather than being left standing over it. The type that USES this
    result now splits three ways: a `decision` blocker is recorded moot and
    ledgered (the caller, unchanged), an `<item-id>` one is disposed by
    `_item_blocker_disposition` below — which needs an answer this function's
    predecessor never had, a refusal, because an item-id blocker names a target
    whose state decides whether the wait was answered or is still live — and an
    `evidence` one is still annotated by nothing, which lc-90 measured and did
    not repair.
    """
    try:
        parsed = items_mod.parse(ctx.items_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return None, ""
    it = next((i for i in parsed.items if i.ident == ident), None)
    if it is None:
        return None, ""
    return items_mod.classify_blocker(it.slots.get("blocked-by", ""),
                                      ctx.prefix)


def _item_blocker_disposition(ctx: Ctx, ident: str, detail: str,
                              dropping: bool, out) -> tuple[str | None, int]:
    """`(the `blocker-moot:` record for an item-id blocker, code)` — lc-90.

    THREE ANSWERS, and the split is the TARGET's state rather than the
    closing item's, because that is what decides whether the wait was
    ANSWERED or is still live:

      * target DONE — the dependency genuinely happened, so the close RECORDS
        it moot and does not refuse. Refusing here would fire on legitimate
        work, which is the repair that stops the lane (R11): the ordinary case
        is exactly this, the blocker closed first and the item followed.
      * the close is a DROP — an abandonment may legitimately leave a live
        dependency behind, and a drop is an exit of equal standing that must
        stay available. The record says so IN THOSE WORDS (`item_moot_record`'s
        second form): the wait ended because the waiter is gone, never because
        anything answered it.
      * anything else on a DONE close — REFUSE. A target still OPEN, a target
        DROPPED (an item-id blocker resolves on its target's DONE, so a dropped
        one can only expire — the same rule `_check_blocker` enforces at the
        write path), or a target in NEITHER home. Recording any of those moot
        would close an item over work that has not happened, which is the worse
        direction by far, and the body is unamendable the moment it moves.

    NOT A SILENT CLEAR EITHER, which is what the refused cases got before this:
    `move_to_done` rewrites the `blocked-by:` LINE to NONE and its caller drops
    the old value on the floor, so a close over a live dependency left no trace
    at all unless an `amended-blocked-by:` line happened to supersede the slot
    — and only then did anything downstream notice (lc-90's finding).
    """
    done_parsed, done_why = _load(ctx.done_path)
    live_parsed, live_why = _load(ctx.items_path)
    if done_parsed is None or live_parsed is None:
        out(f"COULD NOT VERIFY: `blocked-by {detail}` names an item, and "
            "whether that wait was answered cannot be read. "
            f"{done_why or live_why}")
        return None, exits.COULD_NOT_VERIFY

    closed = next((i for i in done_parsed.items if i.ident == detail), None)
    if closed is not None and closed.grade == "DONE":
        return items_mod.item_moot_record(detail, abandoned=False), exits.CLEAN
    if dropping:
        return items_mod.item_moot_record(detail, abandoned=True), exits.CLEAN

    live = next((i for i in live_parsed.items if i.ident == detail), None)
    if closed is not None:
        state = (f"{detail} is itself {closed.grade} in the closure home. An "
                 "item-id blocker resolves on its target's DONE; a dropped "
                 "target never reaches it, so this wait can only expire")
    elif live is not None:
        state = (f"{detail} is still live in the carrier, graded "
                 f"{live.grade or '(none)'}")
    else:
        state = (f"{detail} is in NEITHER home — the wait points at nothing "
                 "and never resolves")
    out(f"FINDING [close_over_live_blocker] {ident} is blocked by {detail!r} "
        f"and {state}. NOT CLOSED. A close that moved this body would end the "
        "wait by deleting it: the moved body records `blocker-moot:` only for "
        "a dependency that actually closed, and a closed body cannot be "
        "amended afterwards — `item amend` refuses it, correctly, because the "
        "done home holds what was true when the item closed. So the state is "
        "refused at the one moment anything can still be done about it. Clear "
        f"the blocker first — `item amend {ident} --blocked-by NONE --reason "
        "<why the dependency no longer holds>` — or close it with --drop, "
        "which records the wait as abandoned rather than as answered.")
    return None, exits.FINDING


def _decision_blocker_disposition(
        ctx: Ctx, ident: str, detail: str,
        out) -> tuple[str | None, str | None, int]:
    """`(the `blocker-moot:` record, the question to LEDGER as moot, code)`.

    TWO VALUES BECAUSE THE TWO ACTS SPLIT (lc-55). Every disposition here
    writes a record onto the moved body; only the UNANSWERED one owes a
    ledger `decision: … → moot` line. Returning one value for both would
    force the caller to re-derive which case it is from the record's text,
    which is the second spelling this module keeps refusing to mint.

    THE SAME READER `item ready` USES, ASKED THE SAME QUESTION. Until this
    existed `cmd_item_close` read the ledger NOWHERE: it took the blocker's
    TYPE off `_effective_blocker` and treated every `decision` blocker as
    unanswered by construction, so its verdict could not depend on the state
    it was writing into. Measured on a private clone at 9839f46: an operator
    answered with `ledger add decision`, `item ready` printed "UNBLOCKED — the
    ledger ANSWERS this decision" citing `LEDGER.md:84`, and the close then
    called the same blocker never answered and appended `LEDGER.md:85`
    recording it moot. One question, two contradictory lines in one carrier,
    and the moot one landed on a body `item amend` refuses afterwards.

    SO THE CALL IS `ledger.decision_for(..., for_item=ident)`, byte-for-byte
    the call `_blocker_state` makes — one reader, one question, agreement by
    construction rather than by two bodies happening to match. `for_item`
    carries G4's scoping across unchanged: a moot line speaks for its own
    closer and for nobody else, so another item's moot line is still no
    answer here and this item's wait is still recorded.

    THREE ANSWERS, and the unreadable one REFUSES rather than falling through
    — the shape `_item_blocker_disposition` above already holds for the
    sibling type. A `blocker-moot:` line ASSERTS the question was never
    answered; with the ledger unreadable that assertion is unverifiable, and
    a close that wrote it anyway would mint the claim onto an unamendable
    body — and, where the ledger is simply absent, would CREATE the file to
    hold it. Dropping the record instead would be the silent clear lc-90
    refused. So neither: the state is refused at the one moment anything can
    still be done about it.
    """
    led, led_why = ledger.read(ctx.ledger_path)
    if led is None:
        out(f"COULD NOT VERIFY: `blocked-by decision {detail}` names a "
            "question, and whether the ledger already ANSWERS it cannot be "
            f"read. {led_why} NOT CLOSED: the `blocker-moot:` line this close "
            "would write asserts the question was never answered, and that "
            "assertion would land — unchecked and unamendable — on the moved "
            "body. Answer the question (`ledger add decision`) or clear the "
            f"blocker (`item amend {ident} --blocked-by NONE --reason <why>`) "
            "once the ledger is readable.")
        return None, None, exits.COULD_NOT_VERIFY
    answers = ledger.decision_for(led, detail, for_item=ident)
    if answers:
        last = answers[-1]
        out(f"blocker-moot: the `decision` blocker {detail!r} was ANSWERED "
            f"before this close — {last.slots.get('answer', '')!r} "
            f"({ctx.ledger_path.name}:{last.lineno}) — so the moved body "
            "records it ANSWERED and NO second `decision:` line is written. "
            "The moot form would say the question died unanswered, which is "
            "what `item ready` reads this same line as refuting: one "
            "question, one verdict, one home.")
        return items_mod.decision_moot_record(detail), None, exits.CLEAN
    return detail, detail, exits.CLEAN


def _resolve_refs(ctx: Ctx, raw: str, out) -> tuple[str | None, int]:
    """`(the `closed-ref:` value, code)` — every ref VERIFIED in this repo.

    REFUSED, never written unverified (lc-44). The closure record's whole
    point is that `items leave BY COMMIT REF` survives the verb that closes
    the item; a ref nobody checked is a label, and a label that resolves to
    nothing reads exactly like one that resolves to the commit. The predicate
    is git's own — `rev-parse --verify <ref>^{commit}` — because "is this a
    commit in this repo" is a question the repo answers and nothing here
    should be modelling.

    WRITTEN AS GIVEN, not resolved to a full sha: the operator's own spelling
    is what the record should carry, and rewriting it would put a value in the
    file nobody typed.
    """
    refs = [r.strip() for r in raw.split(",") if r.strip()]
    if not refs:
        out(f"FINDING [closed_ref_unresolvable] `--ref {raw!r}` names no ref. "
            "The flag is OPTIONAL — omitting it writes no `closed-ref:` line "
            "and says so — so an empty one is a ref that went missing between "
            "the caller and here, not a caller who meant nothing.")
        return None, exits.FINDING
    for ref in refs:
        # `probe.returncode == 0`, NOT the file's usual `if r.returncode != 0`
        # — that spelling at this indent CONTAINS the anchor
        # `tools/prove-rows.py` records for `move_uncommitted`, and a second
        # occurrence puts that row's arrangement at COULD NOT VERIFY. The
        # anchor is a substring match, so an unrelated verb can retire
        # another row's proof simply by spelling a git check the same way.
        probe = subprocess.run(
            ["git", "-C", str(ctx.repo), "rev-parse", "--verify",
             f"{ref}^{{commit}}"], capture_output=True, text=True)
        if probe.returncode == 0:
            continue
        out(f"FINDING [closed_ref_unresolvable] `--ref` names {ref!r}, "
            f"which is not a commit in {ctx.repo}: "
            f"{(probe.stderr or probe.stdout).strip()[:200]!r}. A closure "
            "record is written ONCE onto a body that then stops being "
            "edited, so an unresolvable ref there is permanent — and it "
            "reads exactly like a good one.")
        return None, exits.FINDING
    return ", ".join(refs), exits.CLEAN


#: THE DECLARED FORWARD-CARRIER MARKER (lc-22). ONE SPELLING, and no synonym
#: is added: a closure vocabulary that sprouts synonyms decays invisibly, and
#: the `carried-forward` slot another carrier uses is a DIFFERENT detector's
#: business — `item check` already surfaces it as an unknown slot.
#:
#: THE ANCHOR IS THE DECLARATION, NEVER THE SUBJECT. Uppercase marker, an
#: optional parenthetical, then a colon. Matching the loose words "carrier" or
#: "pointer" over free prose is what a guard must not do here: measured over
#: this repo's own CLAUDE.md, JOURNAL.md, LEDGER.md and both item homes, the
#: loose form hits 252 lines and this one hits none, so the loose form would
#: refuse very nearly every close in the repo — a guard firing on legitimate
#: work stops the lane (R11), and the repair is the narrow anchor rather than
#: a softened report.
_CARRIED_POINTER = re.compile(
    r"CARRIED[ \t]+POINTER[ \t]*(?:\([^)\n]*\))?[ \t]*:")


def _carried_pointer_lines(text: str) -> list:
    """`[(lineno, stripped line)]` for every declared clause in `text`.

    LINE-BASED, and the limit is stated rather than left to be found: a clause
    WRAPPED across lines is not matched. That is not a hole the predicate
    leaves open — a wrapped value is already an `item_shape` finding by this
    carrier's own rule ("slot values are ONE line"), so a body that could hide
    a clause that way is refused by the parser before a close can reach it.

    TEXT IN, NOTHING READ: the same reason `_effective_slot` takes text. It
    makes the predicate askable of any string — the corpus over-fire arm runs
    it over this repo's own prose, which is not a carrier at all.
    """
    return [(n, line.strip())
            for n, line in enumerate(text.split("\n"), start=1)
            if _CARRIED_POINTER.search(line)]


def _carried_pointer_clauses(ctx: Ctx, ident: str) -> tuple[list, str]:
    """`(clauses, why-unreadable)` for the body a close is about to file.

    THE SUBJECT IS THE RAW BLOCK `replace_body` HANDS THE MOVE, not the slot
    values in force. What reaches the closure home is the block's bytes, and an
    `amended-…:` line supersedes a VALUE without deleting the line that carried
    the clause — the earlier line is retained, so the clause still travels. The
    clearance is therefore removing it from the body, or splitting the residue
    into its own item, which is what the refusal says.

    THREE ANSWERS (R1). An unreadable carrier is `why`, never an empty clause
    list: "no clause here" and "this file could not be read" are different
    facts, and folding the second into the first would let a close proceed over
    a body nothing graded. A block that is simply ABSENT is neither — that is
    `move_to_done`'s `unknown_item`, which owns the case and keeps it.
    """
    try:
        text = ctx.items_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [], (f"the carrier at {ctx.items_path} could not be read "
                    f"({type(exc).__name__}), so whether this body declares a "
                    "forward-carrier clause is unknown. A close over an "
                    "ungraded body is the one thing this refusal exists to "
                    "stop, so it is not assumed clean.")
    _kept, body = items_mod.replace_body(text, ident)
    if body is None:
        return [], ""
    return _carried_pointer_lines(body), ""


def cmd_item_close(args, out, ctx: Ctx) -> int:
    """The MOVE, then conservation — re-run at EVERY close, not asserted once.

    An identity that has never been seen to fail is not a check, and one
    computed only at migration time is a claim about a day that has passed.
    Running it here means every close either confirms the carrier is whole
    or names the moment it stopped being.

    THE CLOSURE RECORD (lc-44). A DONE close writes what it was given onto the
    MOVED BODY — `closed-reason:` and `closed-ref:` — and the home is the body
    rather than the ledger because two homes for one fact is the
    paraphrase-drift the carrier doctrine forbids (judgment desk, 2026-08-27).
    A DROP keeps its ledger `dropped:` line instead, because a dropped body
    may be pruned and its record cannot live only there.

    BOTH LINES ARE OPTIONAL AND THE ABSENCE IS SPOKEN. Real closures have no
    ref — already done, closed by decision — so a missing line is legitimate;
    but a silent absence is indistinguishable from the defect this item
    repaired, where `--reason` was accepted and written NOWHERE while the verb
    printed a move and a commit that read as a complete closure record.
    """
    grade = "DROPPED" if args.drop else "DONE"
    reason = (args.reason or "").strip()
    ref_raw = (args.ref or "").strip()
    ref_value = None
    if ref_raw:
        if args.drop:
            # SAID, never silently dropped. A drop's record is the ledger
            # line, and a `--ref` swallowed without a word would look exactly
            # like one that landed.
            out(f"--ref {ref_raw!r}: NOT WRITTEN. A --drop close records "
                "itself as the ledger `dropped:` line and carries no "
                "closed-body slots — a dropped body may be pruned, so its "
                "record cannot live only on it.")
        else:
            ref_value, ref_code = _resolve_refs(ctx, ref_raw, out)
            if ref_code != exits.CLEAN:
                return ref_code
    if args.drop:
        problem = ledger.check_prose(args.reason, "the drop reason")
        if problem:
            out(f"FINDING [ledger_body] {problem} A drop is an exit of equal "
                "standing to a completion — the carrier's goal is to lose "
                "nothing SILENTLY, which a recorded drop satisfies and an "
                "unrecorded one does not.")
            return exits.FINDING
    elif reason:
        # A DONE REASON GOES ON THE MOVED BODY, so it is a SLOT VALUE and the
        # slot writer's own predicate is what grades it — not the ledger's.
        # The two refuse different things: the ledger forbids its slot
        # separator, a carrier slot forbids a wrapped value. Asking the wrong
        # one would let the tool write a file its own shape check rejects.
        problem = items_mod.slot_value_problem(items_mod.CLOSED_REASON, reason)
        if problem:
            out(f"FINDING [item_shape] {problem}")
            return exits.FINDING

    with items_mod.carrier_lock(ctx.items_path):
        if not ctx.items_path.exists():
            out(f"COULD NOT VERIFY: no carrier at {ctx.items_path}.")
            return exits.COULD_NOT_VERIFY

        # A GRADE MUST BE A REAL MEMBER AT CLOSE (D-3), and this is read
        # BEFORE anything is written, for the same reason the forward-carrier
        # clause below is: a refusal arriving after the move would be a
        # verdict about a body already sitting where nothing can amend it.
        #
        # WHY THE MOVE IS THE ONE DOOR THAT REFUSES THE ARM. Everywhere else
        # the arm is the honest answer — the state could not be said, and
        # saying so beats picking a neighbour. At CLOSE the opposite holds:
        # closing files the body under DONE or DROPPED in a home nobody
        # re-reads, so an item whose own grade says "we could not express
        # what this is" would be archived as a settled outcome. That is the
        # neighbour-folding this contract exists to end, performed at the
        # last door before the record stops being looked at.
        close_parsed, close_why = _load(ctx.items_path)
        if close_parsed is None:
            out(f"COULD NOT VERIFY: {close_why}")
            return exits.COULD_NOT_VERIFY
        subject = next((i for i in close_parsed.items
                        if i.ident == args.ident), None)
        if subject is not None and vocab.is_oov(subject.grade):
            oov = vocab.parse_oov(subject.grade)
            out(f"FINDING [unknown_grade_write] {args.ident} is graded with "
                f"the out-of-vocabulary arm, recorded {oov.date}: "
                f"{oov.reason}")
            out("A grade must be a REAL MEMBER at close. The arm records "
                "that the vocabulary could not say what this item is, and "
                "closing it would file exactly that unsaid state under "
                f"{grade} — in the home nobody re-reads. Dispose of it "
                "first: `item amend` it to a real member if one now fits, "
                "or mint the member its reason asks for and re-type it. "
                "Nothing was moved.")
            return exits.FINDING

        # THE FORWARD-CARRIER CLAUSE IS READ FIRST, BEFORE ANYTHING IS
        # WRITTEN (lc-22). Its verdict can be a refusal, and a refusal
        # arriving after the move would be a verdict about a body already
        # sitting where nothing can amend it — the same reason the item-id
        # blocker below is disposed before the write. Its OWN verdict rather
        # than a branch folded into a neighbouring one: it answers a different
        # question from every other check here and owes its own message.
        clauses, why = _carried_pointer_clauses(ctx, args.ident)
        if why:
            out(f"COULD NOT VERIFY: {why}")
            return exits.COULD_NOT_VERIFY
        if clauses:
            out(f"FINDING [close_carries_pointer] {args.ident} declares a "
                "forward-carrier clause and is NOT CLOSED. The move would "
                "file this body in the closure home, where the obligation the "
                "clause declares reads as discharged because its carrier is "
                "filed as discharged (lc-22). Quoted from the body, whole:")
            for lineno, line in clauses:
                out(f"    line {lineno}: {line}")
            out("WHAT THIS ESTABLISHES is that the clause is THERE. Whether "
                "the pointer is still owed is what the clause itself declares "
                "— this check did not measure it and does not claim to. Clear "
                "it the way the clause asks: re-word or remove the pointer it "
                "names, then take the clause out of the body; or split the "
                "residue into its own item, which carries the clause away "
                "with it and leaves this one closable. There is no override "
                "flag, and that is deliberate — a bypass files the clause "
                "among the closed bodies, which is the single outcome this "
                "refusal exists to prevent.")
            return exits.FINDING

        kind, detail = _effective_blocker(ctx, args.ident)
        # THE DECISION TYPE IS DISPOSED AGAINST THE LEDGER (lc-55), not from
        # its type alone. `moot = detail if kind == "decision"` asserted
        # "never answered" without ever reading the file that records the
        # answer, which is how one close came to contradict the `item ready`
        # run before it. Before the write, for the same reason the item-id
        # disposition below is: its answer can be a COULD NOT VERIFY.
        # `decision_moot` is the RECORD the moved body carries; `moot` is the
        # question this close makes MOOT and therefore ledgers below. They
        # part company exactly where the ledger already holds an answer: the
        # body still records what happened to the blocker — silence there
        # leaves an AMENDED one standing in the closure home with nothing to
        # discharge it (lc-90) — while the ledger gets no second line.
        decision_moot = None
        moot = None
        if kind == "decision" and detail:
            decision_moot, moot, decision_code = (
                _decision_blocker_disposition(ctx, args.ident, detail, out))
            if decision_code != exits.CLEAN:
                return decision_code
        # THE ITEM-ID TYPE IS DISPOSED BEFORE ANYTHING IS WRITTEN (lc-90):
        # its answer can be a REFUSAL, and a refusal that arrived after the
        # move would be a verdict about a body already sitting where nothing
        # can amend it.
        item_moot = None
        if kind == "item" and detail:
            item_moot, item_code = _item_blocker_disposition(
                ctx, args.ident, detail, args.drop, out)
            if item_code != exits.CLEAN:
                return item_code
        # R3 SEAM (refocus round, 2026-09-24, lc-288), printed before the
        # move: the already-required `--reason` prose below is the written
        # answer this treatment arm was measuring for; this is only the READ
        # half. Runs for BOTH grades (DONE and DROPPED) — a drop's own
        # required reason is exactly as much "the record" as a done close's.
        _print_item_close_goal(ctx, out, args.ident, subject)
        # THE APPENDED LINES, IN `DONE_ONLY_SLOTS` ORDER, in ONE buffer write
        # with the move. Two writes would leave a body moved without its
        # record, or a record about a move that did not happen — and the
        # order is the tuple's so the shape check reads them as the tail it
        # expects rather than as slots that wandered.
        date = _today()
        note_lines = []
        if decision_moot:
            note_lines.append(f"blocker-moot: {decision_moot}")
        elif item_moot:
            note_lines.append(f"blocker-moot: {item_moot}")
        if not args.drop:
            if reason:
                note_lines.append(
                    f"{items_mod.CLOSED_REASON}: {date} {reason}")
            if ref_value:
                note_lines.append(f"{items_mod.CLOSED_REF}: {ref_value}")
        code = move_to_done(ctx, args.ident, grade, "\n".join(note_lines), out)
        if code != exits.CLEAN:
            return code
        if not args.drop:
            # BOTH ANSWERS ARE SPOKEN, present or absent. The whole defect
            # lc-44 repaired was a `--reason` that reached nothing while the
            # output read as a complete closure record, and an unspoken
            # absence is byte-identical to that.
            if reason:
                out(f"{items_mod.CLOSED_REASON}: {date} {reason}")
            else:
                out(f"{items_mod.CLOSED_REASON}: not given, no line written.")
            if ref_value:
                out(f"{items_mod.CLOSED_REF}: {ref_value}")
            else:
                out(f"{items_mod.CLOSED_REF}: not given, no line written. A "
                    "closure legitimately has none — already done, or closed "
                    "by a decision rather than a commit.")
        touched = [ctx.items_path, ctx.done_path]
        if moot:
            # THE CLOSE STAYS UNGUARDED and this is the whole decision.
            # Closing is the desk's act, and a guard that refused to close an
            # item over an unanswered decision would fire on legitimate work
            # — the ordinary case is exactly this: the question stopped
            # mattering because the item shipped. So the fact is RECORDED
            # rather than refused, in both places a later reader looks: on
            # the moved body, and as a decision line in the ledger. An
            # operator queue that still lists the question after the item
            # that asked it is gone is a queue nobody can drain.
            out(f"blocker-moot: the `decision` blocker {moot!r} was never "
                "answered and this close makes it moot. NOT REFUSED — "
                "closing is the desk's act. Recorded on the moved body and "
                "in the ledger.")
            problem = ledger.check_prose(moot, "the moot decision question")
            if problem:
                # The question is DATA read off the item, not prose this run
                # composed, so it can carry a separator the ledger's shape
                # forbids. The body annotation still lands; the ledger half
                # is COULD NOT VERIFY, never a silently ambiguous line and
                # never a refused close.
                out(f"COULD NOT VERIFY: the ledger `decision:` line was NOT "
                    f"written — {problem}")
                moot_code = exits.COULD_NOT_VERIFY
            else:
                # THE ANSWER TEXT COMES FROM THE LEDGER MODULE, never a
                # literal here: `decision_for` recognises this exact shape to
                # keep a moot line from unblocking another item, and a second
                # spelling on the writing side would drift silently.
                line = ledger.append(ctx.ledger_path, "decision",
                                     {"question": moot,
                                      "answer": ledger.moot_answer(args.ident)})
                out(f"ledger: {line}")
                touched.append(ctx.ledger_path)
                moot_code = exits.CLEAN
        elif item_moot:
            # SPOKEN, and NOT LEDGERED — the two halves are deliberate. An
            # item-id blocker is not a question in anybody's queue: it names a
            # dependency whose own record is that item's closure, already in
            # the ledger under its own id. A second `decision:` line about it
            # would put one fact in two homes, which is the paraphrase-drift
            # the carrier doctrine forbids. The body record is what the done
            # home's own check reads back (lc-90).
            out(f"blocker-moot: {item_moot}. Recorded on the moved body; no "
                "ledger line, because an item-id blocker is not a question in "
                "the operator's queue — its record is the target item's own "
                "closure.")
            moot_code = exits.CLEAN
        else:
            moot_code = exits.CLEAN
        if args.drop:
            line = ledger.append(ctx.ledger_path, "dropped",
                                 {"id": args.ident, "reason": reason})
            out(f"ledger: {line}")
            if ctx.ledger_path not in touched:
                touched.append(ctx.ledger_path)
        code = exits.worst([code, moot_code])
        code = exits.worst([code, commit_paths(
            ctx, touched, f"lifecycle: close {args.ident} ({grade})", out,
            skip=args.no_commit)])

        items_parsed, why = _load(ctx.items_path)
        done_parsed, done_why = _load(ctx.done_path)
        if items_parsed is None:
            out(f"COULD NOT VERIFY: {why}")
            return exits.worst([code, exits.COULD_NOT_VERIFY])
        code = exits.worst([code, items_mod.report_conservation(
            items_mod.conservation(items_parsed, done_parsed, done_why), out)])
    args.fire_detail = f"close {args.ident} {grade}"
    _append_fire_detail(args, "goal-seam=close")
    return code


# --- `item supersede-closure` (lc-120) ----------------------------------------

def cmd_item_supersede_closure(args, out, ctx: Ctx) -> int:
    """Append a FORWARD POINTER to a closed body. Nothing existing is touched.

    `item amend` REFUSES a closed body and this verb does not soften that. The
    refusal's ground is correct — the done home holds what was true when the
    item closed, and correcting it there would edit a record other counts have
    already read — but it left a slot that turns out FALSE asserting itself
    forever, with its correction living only in a ledger line the done-home
    reader never loads. Both versions then stand and the reader who stops at
    the first takes the superseded one.

    SO THIS APPENDS AND NEVER REWRITES. The original `closed-reason:` and
    `closed-ref:` come out of the act byte-identical; what the body gains is
    one line saying a later record exists and where it is. That is why this is
    a verb beside `item amend` rather than a relaxation of it: amending would
    change what the record says, and this changes only what it POINTS AT.

    THE REF IS VERIFIED, through `_resolve_refs` and not a second resolver.
    A pointer is written once onto a body that has ALREADY stopped being
    edited, so a ref that resolves to nothing there is permanent and reads
    exactly like a good one — the same cause and the same repair as
    `closed_ref_unresolvable`'s own case, which is why this fires that refusal
    rather than minting a second name for one defect.

    WHAT "LEDGER-REF" MEANS, settled rather than assumed: `ledger.parse_line`
    keys on KIND and returns kind plus slots, and the ledger carries no
    per-line identifier at all — so a reference INTO it can only be the commit
    that appended the line, and git's own `rev-parse --verify <ref>^{commit}`
    is the predicate.
    """
    line = (args.line or "").strip()
    problem = ledger.check_prose(line, "the pointer's one line")
    if problem:
        out(f"FINDING [ledger_body] {problem} The pointer's whole job is to "
            "route a reader to the later record in one line; a body here "
            "would be a second copy of what the ref already points at.")
        return exits.FINDING

    ref_value, ref_code = _resolve_refs(ctx, (args.ref or "").strip(), out)
    if ref_code != exits.CLEAN:
        return ref_code

    date = _today()
    # GRADED BEFORE IT IS WRITTEN, by the predicate the PARSER will grade it
    # with. The verb must not be able to write a line its own carrier check
    # then refuses — that would leave the repair path producing the finding
    # class it exists to clear.
    problem = items_mod.closure_pointer_problem(f"{date} {ref_value} {line}")
    if problem:
        out(f"FINDING [item_shape] {problem}")
        return exits.FINDING

    with items_mod.carrier_lock(ctx.done_path):
        if not ctx.done_path.exists():
            out(f"COULD NOT VERIFY: no done home at {ctx.done_path}. An absent "
                "closure home and one holding no such body are different "
                "answers, and neither is 'appended'.")
            return exits.COULD_NOT_VERIFY
        text = ctx.done_path.read_text(encoding="utf-8")
        new, ok = items_mod.append_closure_pointer(text, args.ident, date,
                                                   ref_value, line)
        if not ok:
            # THE LIVE CARRIER IS NAMED IN THE REFUSAL, because the near-miss
            # is real: a desk reaching for this verb on an item that has not
            # closed yet wants `item amend`, and a bare "no such block" would
            # send it looking for a missing body instead.
            out(f"FINDING [unknown_item] no closed block {args.ident!r} in "
                f"{ctx.done_path.name}. This verb annotates a body that has "
                "ALREADY closed; an item still live in "
                f"{ctx.items_path.name} is corrected with `item amend`, which "
                "supersedes a slot in place of pointing past it.")
            return exits.FINDING
        atomic.write_text(ctx.done_path, new, encoding="utf-8")
        out(f"{args.ident}: forward pointer appended to {ctx.done_path.name}. "
            "NOTHING existing was rewritten — the closure record still says "
            "what it said.")
        out(f"    {items_mod.render_closure_pointer(date, ref_value, line)}")
        code = commit_paths(ctx, (ctx.done_path,),
                            f"lifecycle: supersede-closure {args.ident}", out,
                            skip=args.no_commit, what="the forward pointer")
    args.fire_detail = f"supersede-closure {args.ident}"
    return code


# --- the ledger's own intake join (R7, lc-289) --------------------------------

def decision_candidates(parsed, question: str) -> list:
    """`[(Line, [shared tokens])]` — existing `decision:` lines this question
    may already be.

    SAME RARITY MACHINERY AS THE ITEM INTAKE JOIN (lc-46), pointed at the
    ledger's own decision QUESTIONS instead of an item's requirement line:
    a token carried by most of the ledger's decisions has no discriminating
    power by definition, whichever carrier is asking. There is no write-set
    half here — a `decision:` line carries no write-set slot, so the join is
    token-only. SCOPED TO `decision` LINES ALONE: `superseded` / `rejected` /
    `dropped` reference an id, never a claim that can be re-decided by
    accident, so they get no join (the settled design, R7).
    """
    want_tokens = requirement_tokens(question)
    decisions = [ln for ln in parsed.lines if ln.kind == "decision"
                 and not ln.slots.get("question", "").startswith(
                     JOIN_DISPOSITION_PREFIX)]
    freq = document_frequency(decisions, key="question")
    found = []
    for ln in decisions:
        its_tokens = requirement_tokens(ln.slots.get("question", ""))
        shared = informative_tokens(
            want_tokens & its_tokens, freq, len(decisions), its_tokens,
            max_fraction=DECISION_MATCH_MAX_DOC_FRACTION)
        if len(shared) >= MATCH_MIN_TOKENS:
            found.append((ln, sorted(shared)))
    return found


def print_decision_candidates(ctx: Ctx, found: list, out) -> None:
    """The ledger join's own screen: every matching decision line, its
    location and the tokens that triggered the match — `print_candidates`'s
    sibling, one carrier over."""
    for ln, shared in found:
        out(f"  match: {ctx.ledger_path.name}:{ln.lineno}  decision: "
            f"{ln.slots.get('question', '')}{ledger.ARROW}"
            f"{ln.slots.get('answer', '')}")
        out(f"      shares {len(shared)} token(s): " + ", ".join(shared))


def _check_decision_join(args, ctx: Ctx, out) -> int:
    """R7 (lc-289): `ledger add decision` runs the intake join on its
    QUESTION before the line is written.

    `cmd_ledger_add` had NO match step at all: a re-decided question could
    be written twice with nobody the wiser, which is the same
    accumulation-by-insert the item carrier's intake join exists to close
    (§3.2), one carrier over. WITH NO MATCH, THIS RETURNS CLEAN AND PRINTS
    NOTHING — behaviour is exactly what it was before this existed, which is
    what keeps an ordinary decision line as cheap as it always was.

    THE ONLY ACCEPTED DISPOSITION IS `--join new --absence "<why>"`. Unlike
    `item add`'s three-way join, there is no `merge-into` or `supersede`
    here: a ledger line is APPEND-ONLY prose, not a body another verb can
    fold two records into or move to a closure home, so the only question a
    match ever raises is whether this is genuinely a NEW question — the same
    named-absence discipline `item add`'s `new` already demands, reused
    rather than restated.

    AN ABSENT LEDGER IS NOT COULD-NOT-VERIFY HERE, unlike `item add`'s
    missing-carrier read: `ledger.append` itself CREATES the head when the
    file does not exist yet (its own docstring), so a not-yet-existing
    ledger has, by construction, no decision lines to near-match — the same
    answer as an existing one with none. Refusing here over `item add`'s
    absent-carrier rule would block the ledger's very first line and would
    have changed `test_an_UNCOMMITTABLE_write_is_a_FINDING_and_never_a_CLEAN`
    (lc-56)'s fixture, whose whole point is that the WRITE still lands and
    only the COMMIT fails when the ledger is untracked.
    """
    parsed, _why = ledger.read(ctx.ledger_path)
    if parsed is None:
        return exits.CLEAN
    found = decision_candidates(parsed, args.question or "")
    if not found:
        return exits.CLEAN
    join = getattr(args, "join", None)
    if not join:
        out(f"FINDING [ledger_join_undisposed] this question shares "
            f"informative tokens with {len(found)} existing decision "
            "line(s) in the ledger. Answer with `--join new --absence "
            "\"<why this is a new question>\"` — the only accepted "
            "disposition — or answer the existing line instead. Nothing "
            "was written.")
        print_decision_candidates(ctx, found, out)
        return exits.FINDING
    if join != "new":
        out(f"FINDING [ledger_join_undisposed] `--join {join!r}` is not "
            "accepted here — the only accepted disposition is `--join new "
            "--absence \"<why this is a new question>\"`. Nothing was "
            "written.")
        return exits.FINDING
    # NAMED `join_absence`, NOT `absence` (prove-rows.py's own anchor test):
    # `item add`'s `_do_new` already has a line `if not absence:` at its
    # own site, and an anchor is a WHOLE-LINE match — a second identical
    # line here would make that existing row's anchor occupy the file
    # twice, unproven by construction (the anchor-uniqueness test this
    # collision was caught by).
    join_absence = (getattr(args, "absence", None) or "").strip()
    if not join_absence:
        out("FINDING [ledger_join_undisposed] `--join new` needs a named "
            "absence (`--absence \"…\"`): why this is a new question rather "
            "than one of the matches above. Nothing was written.")
        return exits.FINDING
    # THE ABSENCE BECOMES A LEDGER LINE (lc-295), so it is judged by the
    # ledger's own body rule HERE, before the question line is written: a
    # refusal after the first append would leave half a disposition.
    problem = ledger.check_prose(join_absence, "the join absence")
    if problem:
        out(f"FINDING [ledger_body] {problem}")
        return exits.FINDING
    args.join_disposition = ([ln.lineno for ln, _ in found], join_absence)
    return exits.CLEAN


#: The companion line's question opens with this, so the join never offers a
#: disposition record as a near-match for a new question: every such line
#: shares this vocabulary, and a join that matched its own bookkeeping would
#: demand a disposition for writing one.
JOIN_DISPOSITION_PREFIX = "join disposition of LEDGER:"


def _append_join_disposition(ctx: Ctx, written: str, disposition, out) -> None:
    """lc-289's `--absence` was validated and then persisted NOWHERE — not in
    the ledger line and not in the commit (lc-295, measured on the join's
    first live fire, a line that reversed an earlier decision). The
    disposition is a decision in its own right, so it lands as one: a
    companion `decision:` line naming the line just written and the lines it
    was judged against, answered with the absence. Same file, same commit."""
    matched, absence = disposition
    parsed, _why = ledger.read(ctx.ledger_path)
    lineno = next((ln.lineno for ln in reversed(parsed.lines)
                   if ln.raw.strip() == written), None) if parsed else None
    at = f"{lineno}" if lineno is not None else "?"
    beside = ", ".join(f"LEDGER:{n}" for n in matched)
    line = ledger.append(ctx.ledger_path, "decision", {
        "question": f"{JOIN_DISPOSITION_PREFIX}{at} beside {beside}",
        "answer": f"new: {absence}"})
    out(f"ledger: {line}")


# --- `ledger add` (stage 6) ---------------------------------------------------

def cmd_ledger_add(args, out, ctx: Ctx) -> int:
    """Append one fixed-slot line. The TOOL writes slots; the SESSION writes prose.

    Every prose argument below is REQUIRED and none has a default. That is
    the split §3.6 asks for, and it is what keeps the operator-as-backstop
    moment at every rationale line: a generated reason would be a paraphrase
    with nobody's judgment behind it, and it would read exactly like one
    somebody meant.

    AND THE WRITE IS COMMITTED, through the one path every carrier write
    already reaches (lc-56, the sibling of lc-25). This verb wrote the ledger
    and said nothing about it, which is the assumed-delivery class: it does
    not fail, it ACCUMULATES. The measured consequence is one level over —
    `item ready` resolves a `decision` blocker against a ledger line, so an
    item read as UNBLOCKED in a tree where the answer was never committed.
    `--no-commit` IS NOW MIRRORED FROM `item add` (lc-116): a caller batching
    several ledger lines into one commit owns that commit the same way it
    can for every item verb — after CLEAN the line is committed unless
    `--no-commit` said otherwise, because a commit that fails is a FINDING
    and not a CLEAN.
    """
    if not args.line_kind:
        out("COULD NOT VERIFY: `ledger add` needs a line kind: "
            + ", ".join(ledger.KINDS))
        return exits.COULD_NOT_VERIFY

    if args.line_kind == "superseded":
        slots = {"id": args.ident, "by": args.by, "reason": args.reason}
        prose = [(args.reason, "the supersede reason")]
    elif args.line_kind == "rejected":
        slots = {"item": args.item, "approach": args.approach,
                 "why": args.why_text}
        prose = [(args.approach, "the rejected approach"),
                 (args.why_text, "the rejection reason")]
    elif args.line_kind == "dropped":
        slots = {"id": args.ident, "reason": args.reason}
        prose = [(args.reason, "the drop reason")]
    else:
        slots = {"question": args.question, "answer": args.answer}
        prose = [(args.question, "the decision question"),
                 (args.answer, "the decision answer")]

    for value, what in prose:
        problem = ledger.check_prose(value, what)
        if problem:
            out(f"FINDING [ledger_body] {problem}")
            return exits.FINDING

    if args.line_kind == "decision":
        code = _check_decision_join(args, ctx, out)
        if code != exits.CLEAN:
            return code

    line = ledger.append(ctx.ledger_path, args.line_kind,
                         {k: str(v).strip() for k, v in slots.items()})
    out(f"ledger: {line}")
    disposition = getattr(args, "join_disposition", None)
    if disposition:
        _append_join_disposition(ctx, line, disposition, out)
    # ONE COMMIT PATH, not a second spelling: `commit_paths` is what every
    # other carrier write in this file calls, and it commits BY PATHSPEC
    # because the index is shared. EVERY line kind reaches this line — a
    # commit written into one of the four branches above would be a fix for
    # one kind of four, and the other three would keep accumulating.
    code = commit_paths(ctx, (ctx.ledger_path,),
                        f"lifecycle: ledger {args.line_kind}", out,
                        what="the ledger line",
                        skip=getattr(args, "no_commit", False))
    args.fire_detail = f"ledger add {args.line_kind}"
    return code


# --- `arc` (lc-231b: the verb core) -------------------------------------------

def _arc_paths(ctx: Ctx, slug: str):
    return (ctx.repo / arcs.ARCS_DIR / f"{slug}.md",
            ctx.repo / arcs.CLOSED_DIR / f"{slug}.md")


# --- R3, the goal seam (refocus round, 2026-09-24, lc-288) --------------------
#
# The treatment arm's TRIGGER moves from a brief directive (memory) to the
# verb itself: `item close`, `arc advance` and `arc narrow` each print the
# LIVE goal immediately before the already-required prose those acts already
# demand (`--reason`, `--text`) records. No new flag, slot or schema — the
# already-demanded prose is the written answer this arm was measuring for;
# this is only the READ half. `LEDGER.md:130`'s arm, window and grading are
# unchanged; only WHAT FIRES the row moves.

def _goal_line(source: str, text) -> str | None:
    """`goal (<source>): <text>`, or `None` if `text` is blank.

    The shared formatter so all three seams below render one sentence
    identically — a second spelling of "the goal line" per verb is exactly
    the paraphrase-drift this corpus warns against.
    """
    text = (text or "").strip()
    return f"goal ({source}): {text}" if text else None


def _print_seam_goal(out, source: str, text) -> None:
    """Single-source seam print (`arc advance`, `arc narrow`): the line, or

    the NAMED absence — `goal: none resolvable for this act` — when the
    arc's own `goal:` slot is blank. Never silence: an unprinted line here
    would be indistinguishable from a verb that never got this far.
    """
    line = _goal_line(source, text)
    out(line if line is not None else "goal: none resolvable for this act")


def _print_item_close_goal(ctx: Ctx, out, ident: str, subject) -> None:
    """R3 seam for `item close`: TWO sources, each printed independently

    when it resolves, neither invented when it does not.

    1. The item's OWN `goal:` slot (source `item goal <ident>`) — resolved
       against the declaration's `goals` (`decl.effective_goals`, which adds
       the plugin-reserved `tend`): an item legitimately advancing no goal
       carries UNKNOWN there (`items.UNKNOWNABLE_SLOTS`), and UNKNOWN is not
       a declared goal, so it silently does not resolve rather than printing
       a line that asserts a goal the item never claimed.
    2. Every OPEN arc (`arcs/*.md` — `arcs/closed/` is a different home and
       a closed arc's thread is no longer live work this close informs)
       that names `ident` as a WHOLE TOKEN in its body (source `arc
       <slug>`), using the same `\\b`-anchored match `arcs.citers` already
       runs for belief ids — a substring match would also catch `xx-10`
       inside a search for `xx-1`.

    `goal: none resolvable for this act` prints once, only when NEITHER
    source produced a line — the MUST-NOT-MOVE this repo's surfacing
    convention already keeps: an absence is spoken, never silent.
    """
    printed = False
    if subject is not None:
        goal_name = (subject.slots.get("goal") or "").strip()
        if goal_name in decl.effective_goals(ctx.declaration):
            line = _goal_line(f"item goal {ident}", goal_name)
            if line is not None:
                out(line)
                printed = True
    pattern = re.compile(r"\b" + re.escape(ident) + r"\b")
    for slug in arcs.live_slugs(ctx.repo):
        path = ctx.repo / arcs.ARCS_DIR / f"{slug}.md"
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if not pattern.search(text):
            continue
        arc_obj, _probs = arcs.parse_arc(text, slug)
        line = _goal_line(f"arc {slug}", arc_obj.slots.get("goal"))
        if line is not None:
            out(line)
            printed = True
    if not printed:
        out("goal: none resolvable for this act")


def _append_fire_detail(args, addition: str) -> None:
    """Append to `args.fire_detail` without ever overwriting one a verb

    already set for its own purpose — the same '; '-joined idiom `cli.py`'s
    `main()` surface already uses for the R1 `surfaced=` token, applied here
    because a verb sets its own detail BEFORE `main()` ever sees it.
    """
    existing = getattr(args, "fire_detail", None)
    args.fire_detail = f"{existing}; {addition}" if existing else addition


def cmd_arc_open(args, out, ctx: Ctx) -> int:
    """Open an arc: the body, then the counter, then ONE commit.

    THE ORDER PUTS THE CRASH WINDOW ON THE RECOVERABLE SIDE, which is law 9's
    judgment applied to an admission rather than a move. Body first: a crash
    before the counter leaves a body nothing admitted, which conservation
    reads as OVER — the homes hold more than was admitted, ordinary cause an
    interrupted write, recoverable. Counter first would leave an admission
    with no body, which reads SHORT: the LOSS side, over a loss that never
    happened. The same window, named the other way, and the name is what a
    desk acts on.
    """
    slug = args.slug.strip()
    if not slug or "/" in slug or slug == arcs.INDEX_STEM:
        out(f"FINDING [arc_shape] {slug!r} is not a usable arc slug. It "
            "becomes a filename in the arc home, so it carries no path "
            f"separator, and it is not {arcs.INDEX_STEM!r}, which is the "
            "home's own bookkeeping file rather than a body.")
        return exits.FINDING

    live, _closed = _arc_paths(ctx, slug)
    if live.exists():
        out(f"FINDING [arc_exists] an arc {slug!r} is already open at "
            f"{live.relative_to(ctx.repo)}. Opening over it would overwrite a "
            "live narrowing — the one thing this carrier exists to keep — and "
            "a second arc on the same question is a different slug, not the "
            "same one twice.")
        return exits.FINDING

    goal = (args.goal or "").strip()
    form = (args.narrowing or "").strip()
    if form not in arcs.NARROWING_FORMS:
        out(f"FINDING [arc_shape] `--narrowing {form or '(unset)'}` is not "
            f"one of {', '.join(arcs.NARROWING_FORMS)}. The form is a per-arc "
            "DECLARATION and not a default: a convergent arc eliminates, a "
            "divergent one keeps a palette whose dead ends are the asset, and "
            "a reader cannot tell what the lines under `narrowing:` mean "
            "without being told which this arc is running.")
        return exits.FINDING

    idx = arcs.read_index(ctx.repo)
    counters = dict(idx.counters) if idx.counters else {
        "baseline": 0, "opened": 0, "closed": 0}
    for c in arcs.INDEX_COUNTERS:
        counters.setdefault(c, 0)

    live.parent.mkdir(parents=True, exist_ok=True)
    body = arcs.render_arc(slug, {
        "goal": goal,
        "stage": (args.stage or "opened").strip(),
        "narrowing": f"{form} — nothing recorded yet",
        "premises": "none recorded yet",
        "beliefs": "none recorded yet",
        # PROSE, NOT A COUNT, from the first write. A `0` here would be the
        # persisted-count class seeded at birth: true for exactly as long as
        # nothing happens, and silently false afterwards.
        "yield": "nothing produced yet",
    }, items_mod.SCHEMA_FLOOR)
    # 1. THE BODY, before any counter says it exists.
    atomic.write_text(live, body, encoding="utf-8")
    # 2. THE COUNTER, in the same act (law 9).
    counters["opened"] = int(counters["opened"]) + 1
    atomic.write_text(arcs.index_path(ctx.repo),
                      arcs.render_index(counters, items_mod.SCHEMA_FLOOR),
                      encoding="utf-8")
    out(f"opened arc {slug} → {live.relative_to(ctx.repo)} "
        f"(opened {counters['opened']}, closed {counters['closed']})")
    for line in arcs.render_status(ctx.repo):
        out(line)
    # THE FIRE-LOG LINE IS THE CLI'S, NOT THIS VERB'S. `cli.main` already
    # writes ONE line per invocation carrying the verb path and this detail;
    # a second `firelog.fire` here wrote a DUPLICATE, and the duplicate was
    # not cosmetic — the growth alarm counts `arc close` events, so every
    # closure was counted twice on a surface `audit` prints. Measured: one
    # open and one close produced two records each. One act, one line.
    args.fire_detail = slug
    return commit_paths(
        ctx, [live, arcs.index_path(ctx.repo)],
        f"arcs: open {slug}", out, what="the arc open", stage_new=True)


def cmd_arc_status(args, out, ctx: Ctx) -> int:
    """What is open, at what stage, narrowing how — and conservation."""
    for line in arcs.render_status(ctx.repo):
        out(line)
    cons = arcs.conservation(ctx.repo)
    if cons.sign == "unread" and not arcs.live_slugs(ctx.repo):
        # NO INDEX AND NO BODIES is not a broken repo: arcs are optional and
        # a zero-arc project is the ordinary case. Answering FINDING here
        # would make every repo that never wanted an arc report one.
        return exits.CLEAN
    if not cons.ok:
        out(f"FINDING [arc_conservation] {cons.message}")
        return exits.FINDING
    return exits.CLEAN


def cmd_arc_close(args, out, ctx: Ctx) -> int:
    """The MOVE: append to the closed home, count it, delete the live body.

    THE SAME ORDER AS THE ITEM CARRIER'S CLOSE, and for the same reason: the
    window between the append and the delete holds two copies of one body,
    which conservation reports as OVER and recoverable. Deleting first would
    put that window on the loss side, where a crash leaves nothing to recover
    and no record that there was anything to recover.
    """
    slug = args.slug.strip()
    live, closed = _arc_paths(ctx, slug)
    if not live.exists():
        out(f"FINDING [unknown_arc] no live arc {slug!r} in "
            f"{arcs.ARCS_DIR}/. A closed arc is not re-closable and a slug "
            "that was never opened has nothing to move.")
        return exits.FINDING

    # THE CONSUMING SEAM (astra-a5). A reopened belief is re-derived, or
    # accepted stale WITH A REASON, before the arc moves past it. Without
    # this the flag is an output nobody re-reads and the reopen bought
    # nothing — the arc closes carrying a claim somebody had already said
    # was in doubt, and the closed body is the one nobody re-opens.
    #
    # CHEAP FOR LEGITIMATE WORK, which is what keeps it law-11 safe: the
    # disposition is one line, and "accepted stale" with a reason is a
    # first-class answer rather than a workaround.
    pending = arcs.undispositioned(live.read_text(encoding="utf-8"))
    if pending:
        out(f"FINDING [arc_undispositioned] arc {slug!r} carries "
            f"{len(pending)} belief(s) flagged for re-derivation and not "
            f"dispositioned: {', '.join(pending)}. A close moves the body to "
            "the home nobody re-reads, so closing over an open flag files a "
            "doubt as a settled record. Answer each with `arc disposition "
            f"{slug} --ident <id> --how re-derived|accepted-stale --reason "
            "<why>` — accepted-stale is a real answer and needs only its "
            "reason.")
        return exits.FINDING

    idx = arcs.read_index(ctx.repo)
    if not idx.ok:
        out(f"COULD NOT VERIFY: {idx.why}, so this close cannot record "
            "itself. The counter and the body move in ONE act; writing the "
            "body without the counter would leave the carrier unable to say "
            "whether anything was lost.")
        return exits.COULD_NOT_VERIFY

    body = live.read_text(encoding="utf-8")
    if args.abandon:
        # ABANDON IS A CLOSE WITH A DIFFERENT REASON, not a third path. The
        # bodies move the same way and conservation counts them the same way;
        # what differs is that nothing was concluded, and a record that did
        # not say so would read as an arc that finished.
        body = body.rstrip("\n") + (
            f"\nabandoned: {slug} {_today()} {args.reason.strip()}\n"
            if args.reason else f"\nabandoned: {slug} {_today()} "
                                "no reason recorded\n")
    # EVERY REMAINING OBSERVER GOES, whatever stage set it (astra-a8). A
    # closed arc's deadline lane is the clearest case of a door nobody can
    # act on: the thing it was watching for cannot matter any more, and the
    # abandoned-arc arm is the same act with a different reason.
    _retire_arc_lanes(ctx, slug, body, arcs.deadline_lanes(body), out)
    closed.parent.mkdir(parents=True, exist_ok=True)
    # 1. APPEND — before the tree ever holds one copy fewer.
    atomic.write_text(closed, body, encoding="utf-8")
    # 2. COUNT, in the same act.
    counters = dict(idx.counters)
    counters["closed"] = int(counters["closed"]) + 1
    atomic.write_text(arcs.index_path(ctx.repo),
                      arcs.render_index(counters, items_mod.SCHEMA_FLOOR),
                      encoding="utf-8")
    # 3. DELETE the live body.
    live.unlink()
    out(f"{'abandoned' if args.abandon else 'closed'} arc {slug} → "
        f"{closed.relative_to(ctx.repo)} "
        f"(opened {counters['opened']}, closed {counters['closed']})")

    cons = arcs.conservation(ctx.repo)
    out(f"  {cons.message}")
    args.fire_detail = f"{'abandon' if args.abandon else 'close'} {slug}"
    code = commit_paths(
        ctx, [live, closed, arcs.index_path(ctx.repo)],
        f"arcs: close {slug}", out, what="the arc close", stage_new=True)
    if code != exits.CLEAN:
        return code
    return exits.CLEAN if cons.ok else exits.FINDING


def _arc_append(ctx: Ctx, slug: str, line: str, out, msg: str, *,
                skip: bool = False) -> int:
    """Append one record line to a live arc body and commit it.

    APPEND-ONLY, like every other record this repo keeps: a belief that was
    reopened and then dispositioned records BOTH acts, because "what did this
    arc believe and when did it stop" is the question a successor asks and a
    rewritten line answers neither half.

    THE HEADER IS REFRESHED IN THE SAME WRITE (lc-271). Every verb routed
    through here appends one line of SOME kind; `arcs.refresh_header`
    recomputes `premises:`/`beliefs:` from the body as it now stands, which
    is a no-op for a kind that is neither — so a disposition or verdict line
    costs one idempotent recompute rather than a second code path deciding
    which kinds matter.

    `skip` IS `commit_paths`' `skip` (lc-116): a caller batching several arc
    writes owns the commit, the same escape every other carrier write has.
    """
    live, _closed = _arc_paths(ctx, slug)
    if not live.exists():
        out(f"FINDING [unknown_arc] no live arc {slug!r} in "
            f"{arcs.ARCS_DIR}/.")
        return exits.FINDING
    text = live.read_text(encoding="utf-8")
    text = arcs.refresh_header(text.rstrip("\n") + "\n" + line + "\n")
    atomic.write_text(live, text, encoding="utf-8")
    out(line)
    return commit_paths(ctx, [live], msg, out, what="the arc record",
                        stage_new=True, skip=skip)


def cmd_arc_premise(args, out, ctx: Ctx) -> int:
    """Record a premise the arc rests on — the inbox with visible emptiness.

    A PREMISE IS NOT A BELIEF. A belief is the arc's own claim, carrying a
    basis and a kill-condition; a premise is something the arc TAKES FROM
    ELSEWHERE and is exposed to. They are separate lines because their
    staleness differs in kind: a belief dies when its kill-condition fires, a
    premise dies when the world it came from moves, and folding them would
    make one staleness rule stand for two.
    """
    return _arc_append(
        ctx, args.slug,
        f"{arcs.PREMISE_LINE}: {args.ident} {_today()} {args.text.strip()}",
        out, f"arcs: premise {args.ident} on {args.slug}",
        skip=getattr(args, "no_commit", False))


def cmd_arc_belief(args, out, ctx: Ctx) -> int:
    """Record a belief with its BASIS and its KILL-CONDITION.

    BOTH HALVES ARE DEMANDED AT THE DOOR, and that is the whole mechanism: a
    belief with no basis is the shape the record checker already refuses one
    carrier over, and one with no kill-condition can never be shown wrong —
    it would sit in the arc forever, unfalsifiable, wearing a verdict's
    clothes. The slot demands the STATEMENT and never the answer: "no
    kill-condition is known" is a legal kill-condition and passes, which is
    what keeps this from being the over-constraint it exists to avoid.
    """
    return _arc_append(
        ctx, args.slug,
        f"{arcs.BELIEF_LINE}: {args.ident} {_today()} {args.claim.strip()} "
        f"| basis: {args.basis.strip()} | kill: {args.kill.strip()}",
        out, f"arcs: belief {args.ident} on {args.slug}",
        skip=getattr(args, "no_commit", False))


def cmd_arc_reopen(args, out, ctx: Ctx) -> int:
    """Reopen a belief — and FLAG EVERY CITER, which is the act's point.

    A REOPEN THAT ONLY PRINTED ITS CITERS would leave the arc free to move
    past them: the flag would live in an output nobody re-reads, which is the
    evaporation this carrier exists to stop (astra-a5). So each affected
    belief gets a LINE, and `arc advance` and `arc close` consult them.

    CROSS-ARC REACH IS DECLARED AND NOT TAKEN: a belief in another arc that
    cites this one is the operator's to look at, not this verb's to flag.
    Flagging across the boundary would let one arc's reopen silently stop
    another's movement, and the desk that would have to dispose of it never
    asked for the edge.
    """
    live, _closed = _arc_paths(ctx, args.slug)
    if not live.exists():
        out(f"FINDING [unknown_arc] no live arc {args.slug!r} in "
            f"{arcs.ARCS_DIR}/.")
        return exits.FINDING
    text = live.read_text(encoding="utf-8")
    known = {r.ident for r in arcs.appended_lines(text)
             if r.kind == arcs.BELIEF_LINE}
    if args.ident not in known:
        out(f"FINDING [unknown_arc] arc {args.slug!r} records no belief "
            f"{args.ident!r}. Reopening one nothing wrote would create a "
            "flag over a claim that was never made, and the disposition it "
            "then demands could never be satisfied honestly.")
        return exits.FINDING

    affected = [args.ident] + arcs.citers(text, args.ident)
    reason = args.reason.strip()
    lines = [f"{arcs.REDERIVE_LINE}: {i} {_today()} "
             f"{'reopened: ' if i == args.ident else 'cites ' + args.ident + ': '}"
             f"{reason}" for i in affected]
    # HEADER REFRESH (lc-271): a `re-derive:` line is neither a premise nor
    # a belief, so this recompute is idempotent — kept for the same reason
    # `_arc_append` keeps it: one write path, one place that can go stale.
    new_text = arcs.refresh_header(
        text.rstrip("\n") + "\n" + "\n".join(lines) + "\n")
    atomic.write_text(live, new_text, encoding="utf-8")
    for ln in lines:
        out(ln)
    out(f"flagged {len(affected)} belief(s) for re-derivation: "
        + ", ".join(affected)
        + ". `arc advance` and `arc close` REFUSE until each is dispositioned "
          "— re-derived, or accepted stale with a reason.")
    return commit_paths(ctx, [live], f"arcs: reopen {args.ident} on "
                        f"{args.slug}", out, what="the arc reopen",
                        stage_new=True, skip=getattr(args, "no_commit", False))


def cmd_arc_disposition(args, out, ctx: Ctx) -> int:
    """Answer a re-derive flag — the only thing that clears one."""
    if args.how not in arcs.DISPOSITIONS:
        out(f"FINDING [arc_shape] `--how {args.how}` is not one of "
            f"{', '.join(arcs.DISPOSITIONS)}. The vocabulary is closed "
            "because the flag exists to stop an arc moving past a belief "
            "nobody re-examined, and an open-ended answer would let 'noted' "
            "clear it.")
        return exits.FINDING
    return _arc_append(
        ctx, args.slug,
        f"{arcs.DISPOSITION_LINE}: {args.ident} {_today()} {args.how} "
        f"{args.reason.strip()}",
        out, f"arcs: disposition {args.ident} on {args.slug}",
        skip=getattr(args, "no_commit", False))


def cmd_arc_advance(args, out, ctx: Ctx) -> int:
    """Move the arc to a new stage — refused while any flag stands.

    THE SAME CONSUMING SEAM `arc close` keeps (astra-a5), and it belongs on
    BOTH movement verbs for the same reason: advancing past a belief somebody
    reopened carries the doubt forward into a stage whose work will rest on
    it. Closing files the doubt; advancing COMPOUNDS it.

    THE OUTWARD STOP RENDERS AT ENTRY, which is astra's correction. An
    outward stage's acts leave the operator's controlled sphere, and a STOP
    printed when the stage CLOSES arrives after the act it exists to govern.
    Marking at entry is the only placement that can precede anything.
    """
    slug = args.slug.strip()
    live, _closed = _arc_paths(ctx, slug)
    if not live.exists():
        out(f"FINDING [unknown_arc] no live arc {slug!r} in "
            f"{arcs.ARCS_DIR}/.")
        return exits.FINDING
    text = live.read_text(encoding="utf-8")
    pending = arcs.undispositioned(text)
    if pending:
        out(f"FINDING [arc_undispositioned] arc {slug!r} carries "
            f"{len(pending)} belief(s) flagged for re-derivation and not "
            f"dispositioned: {', '.join(pending)}. Advancing past a reopened "
            "belief carries the doubt into a stage whose work will rest on "
            "it — a close FILES the doubt, an advance COMPOUNDS it. Answer "
            f"each with `arc disposition {slug} --ident <id> --how "
            "re-derived|accepted-stale --reason <why>`.")
        return exits.FINDING

    to = args.to.strip()
    arc_obj, _probs = arcs.parse_arc(text, slug)
    # THE LEAVING STAGE'S DEADLINES END WITH IT (astra-a8). A deadline belongs
    # to the stage that set it; one that outlived its stage keeps firing about
    # a date nothing is waiting for, and a board carrying doors nobody can act
    # on is how a reader learns to skim the board.
    leaving = (arc_obj.slots.get("stage") or "").strip()
    _retire_arc_lanes(ctx, slug, text,
                      arcs.deadline_lanes(text, stage=leaving), out)
    # R3 SEAM (refocus round, 2026-09-24, lc-288): the treatment arm's
    # trigger moves from a brief directive (memory) to the verb itself. The
    # already-required `--reason` prose below is the written answer; this
    # prints the LIVE goal so the answer has something to be an answer TO,
    # immediately before that prose records.
    _print_seam_goal(out, f"arc {slug}", arc_obj.slots.get("goal"))
    _append_fire_detail(args, "goal-seam=advance")
    mark = f" | {arcs.OUTWARD_MARK}" if args.outward else ""
    line = (f"{arcs.ADVANCED_LINE}: {to} {_today()} {args.reason.strip()}"
            f"{mark}")
    text = arcs.set_slot(text, "stage", to)
    new_text = arcs.refresh_header(text.rstrip("\n") + "\n" + line + "\n")
    atomic.write_text(live, new_text, encoding="utf-8")
    out(line)
    if args.outward:
        out("STOP — THIS STAGE IS MARKED OUTWARD, and the mark is rendered "
            "HERE, at entry, because a warning printed when the stage closes "
            "arrives after the act it governs. Acts in this stage leave the "
            "operator's controlled sphere: a send, a submission, a payment, "
            "a signature, a public push, a release. The carve-out floor "
            "binds — where the act has a DRAFT stage the draft is the veto "
            "point, and where it has none the act and its reasoning are "
            "surfaced to the operator BEFORE it runs.")
    return commit_paths(ctx, [live], f"arcs: advance {slug} to {to}", out,
                        what="the arc advance", stage_new=True,
                        skip=getattr(args, "no_commit", False))


def cmd_arc_narrow(args, out, ctx: Ctx) -> int:
    """Rewrite the live narrowing, and RECORD what it replaced.

    TWO WRITES, ONE ACT, and the split is the point: the slot is the CURRENT
    picture — what is still open — because a log of every narrowing ever held
    guides nothing, which is the finding the investigation-record format
    already carries as NOW versus ESTABLISHED. The appended line keeps what
    was ruled out and when, so the arc can say what it eliminated without the
    live picture accumulating into a pile.
    """
    slug = args.slug.strip()
    live, _closed = _arc_paths(ctx, slug)
    if not live.exists():
        out(f"FINDING [unknown_arc] no live arc {slug!r} in "
            f"{arcs.ARCS_DIR}/.")
        return exits.FINDING
    text = live.read_text(encoding="utf-8")
    arc, _problems = arcs.parse_arc(text, slug)
    form = (arc.slots.get("narrowing") or "").split()[0:1]
    form = form[0] if form and form[0] in arcs.NARROWING_FORMS else None
    if form is None:
        out(f"FINDING [arc_shape] arc {slug!r} does not declare a narrowing "
            f"FORM, so a narrowing cannot be recorded against it: a reader "
            "cannot tell whether the new text eliminates a candidate or adds "
            "one to a palette.")
        return exits.FINDING
    # R3 SEAM (refocus round, 2026-09-24, lc-288) — see `cmd_arc_advance`'s
    # own comment for the full rationale; the shape is identical here.
    _print_seam_goal(out, f"arc {slug}", arc.slots.get("goal"))
    _append_fire_detail(args, "goal-seam=narrow")
    new = args.text.strip()
    text = arcs.set_slot(text, "narrowing", f"{form} — {new}")
    line = f"{arcs.NARROWED_LINE}: {form} {_today()} {new}"
    new_text = arcs.refresh_header(text.rstrip("\n") + "\n" + line + "\n")
    atomic.write_text(live, new_text, encoding="utf-8")
    out(line)
    return commit_paths(ctx, [live], f"arcs: narrow {slug}", out,
                        what="the arc narrowing", stage_new=True,
                        skip=getattr(args, "no_commit", False))


def cmd_arc_verdict(args, out, ctx: Ctx) -> int:
    """Book an operator taste judgment AT UTTERANCE (requirement 4).

    THE GROUND TRUTH IN A SUBJECTIVE DOMAIN IS THE OPERATOR'S VERDICT
    SENTENCES, and today they evaporate in chat. Walk 2 is where this came
    from: a divergent arc's stage exit cannot be a predicate, the referee is
    taste, and a taste judgment that was said and not written is a decision
    the next session re-asks. Booking it as a byproduct of it being said is
    the whole mechanism — this verb exists so the recording is one line
    rather than a memory.

    IT RECORDS, IT DOES NOT GRADE. Whether a verdict is right is the
    operator's; that it was given is the carrier's.
    """
    return _arc_append(
        ctx, args.slug,
        f"{arcs.VERDICT_LINE}: {args.ident} {_today()} {args.text.strip()}",
        out, f"arcs: verdict {args.ident} on {args.slug}",
        skip=getattr(args, "no_commit", False))


def cmd_arc_yield(args, out, ctx: Ctx) -> int:
    """Record what this arc produced, and keep the slot PROSE.

    THE COUNT IS NOT STORED. An earlier shape wrote a number into the
    `yield:` slot, which is the persisted-count class: correct when written
    and silently false once another line lands, with arithmetic the only
    reader that would notice. So the slot carries the arc's own one-line
    statement of what it has produced and `arc status` counts the records at
    read time.
    """
    slug = args.slug.strip()
    live, _closed = _arc_paths(ctx, slug)
    if not live.exists():
        out(f"FINDING [unknown_arc] no live arc {slug!r} in "
            f"{arcs.ARCS_DIR}/.")
        return exits.FINDING
    text = live.read_text(encoding="utf-8")
    line = f"{arcs.YIELD_LINE}: {args.ident} {_today()} {args.text.strip()}"
    text = arcs.set_slot(text, "yield", args.summary.strip())
    new_text = arcs.refresh_header(text.rstrip("\n") + "\n" + line + "\n")
    atomic.write_text(live, new_text, encoding="utf-8")
    out(line)
    return commit_paths(ctx, [live], f"arcs: yield {args.ident} on {slug}",
                        out, what="the arc yield", stage_new=True,
                        skip=getattr(args, "no_commit", False))


def _retire_arc_lanes(ctx: Ctx, slug: str, text: str, names, out) -> list:
    """Remove generated observer lanes — BODY and ROW — and say which.

    BOTH HALVES OR NEITHER IS NOT AVAILABLE, so the order puts the residue on
    the loud side: the ROW goes first, because a declared row whose body is
    gone is a `kind check` finding that names itself, while a body whose row
    is gone is invisible to `lane list` and to everything else. If this dies
    between the two, the repo says so.
    """
    removed = []
    for name in names:
        ok, why = decl.remove_lane(ctx.repo, name)
        if why:
            out(f"COULD NOT VERIFY: lane {name!r} was not deregistered "
                f"({why}), so its row may outlive the arc that generated it.")
            continue
        body = ctx.repo / lanes.LANES_DIR / f"{name}.md"
        if body.exists():
            body.unlink()
        removed.append(name)
    if removed:
        out(f"retired {len(removed)} generated observer lane(s): "
            + ", ".join(removed)
            + " — a deadline's lane belongs to the stage that set it, and one "
              "that outlived its stage keeps firing about a date nothing is "
              "waiting for.")
    return removed


def cmd_arc_deadline(args, out, ctx: Ctx) -> int:
    """A dated deadline, and the OBSERVER that makes it more than a note.

    A DATE WITH NO OBSERVER IS A TIME-WORD, which this repo's own convention
    bans: "later" re-enters only by memory, and memory is what the carrier
    exists to replace. Walk 4 is where the exemption comes from — some exits
    are REAL DATES, a world-fact rather than a lazy hold — and the thing that
    makes a date legitimate here is that something NOTICES it. So the verb
    generates a date-predicate LANE, which is the mechanism this repo already
    owns for "something fires when a condition holds".

    IT REGISTERS ITS OWN OUTPUT, for the reason `lane new` records: a body
    the declaration does not list is invisible to `lane list`, so the door
    has no state, no trigger evaluation and no line on the board. Writing the
    body and declaring the door were two acts with one verb once, and the
    hand step left behind was delivered by nobody.
    """
    slug = args.slug.strip()
    live, _closed = _arc_paths(ctx, slug)
    if not live.exists():
        out(f"FINDING [unknown_arc] no live arc {slug!r} in "
            f"{arcs.ARCS_DIR}/.")
        return exits.FINDING
    date = args.date.strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        out(f"FINDING [arc_shape] `--date {date!r}` is not an ISO date "
            "(YYYY-MM-DD). The observer this generates is a DATE predicate, "
            "so a date it cannot compare is a lane that can never fire — "
            "which is the silent park this mechanism exists to replace.")
        return exits.FINDING

    text = live.read_text(encoding="utf-8")
    arc, _problems = arcs.parse_arc(text, slug)
    stage = (arc.slots.get("stage") or "").strip() or "unstaged"
    name = arcs.lane_name(slug, date)

    body = ctx.repo / lanes.LANES_DIR / f"{name}.md"
    if body.exists():
        out(f"FINDING [lane_new_exists] the observer lane {name!r} already "
            f"exists at {body}. Two deadlines on one arc and one date would "
            "share a door, and retiring either would take the other's row "
            "off the board.")
        return exits.FINDING

    body.parent.mkdir(parents=True, exist_ok=True)
    body.write_text(
        f"# Lane: {name}\n\n"
        f"Decides: nothing alone — this is an OBSERVER generated by `arc "
        f"deadline` for arc {slug!r}. It reports that a date has arrived; "
        "what to do about it is the arc's, and the disposition is the "
        "operator's or the desk's.\n\n"
        f"Trigger: test \"$(date +%Y-%m-%d)\" \\>= \"{date}\"  # fires on and "
        f"after {date}\n\n"
        "| condition | workflow |\n"
        "|---|---|\n"
        f"| the date has arrived | read arc {slug} and disposition the "
        "deadline |\n\n"
        f"Ends: the arc leaves the stage that set this deadline, or closes, "
        "or is abandoned — each retires this lane, body and row together.\n",
        encoding="utf-8")

    added, why = decl.add_lane(ctx.repo, name)
    if why:
        out(f"COULD NOT VERIFY: the observer body is on disk at {body} and "
            f"was NOT declared ({why}). An undeclared lane body is invisible "
            "to `lane list`, so the deadline has no observer despite the "
            "file — reporting CLEAN here would claim a door this verb did "
            "not open.")
        return exits.COULD_NOT_VERIFY

    line = (f"{arcs.DEADLINE_LINE}: {name} {stage} {date} "
            f"{args.what.strip()}")
    new_text = arcs.refresh_header(text.rstrip("\n") + "\n" + line + "\n")
    atomic.write_text(live, new_text, encoding="utf-8")
    out(line)
    out(f"generated observer lane {name!r} and declared it — `lane list` "
        f"reports it QUIET until {date}.")
    return commit_paths(
        ctx, [live, body, ctx.repo / decl.DECLARATION_REL],
        f"arcs: deadline {date} on {slug}", out, what="the arc deadline",
        stage_new=True, skip=getattr(args, "no_commit", False))


# --- `kind moments` (lc-243 W1 act 1): the O6 evaluation half, made visible ---

def cmd_kind_moments(args, out, repo: Path, doc: dict) -> int:
    """Evaluate every kind's declared reader MOMENTS and say what they answer.

    WHAT THIS CLOSES. `declaration.read_moments` has existed and been correct
    and been read by NOTHING — the evaluation half built and not live, which
    is the loop map's O6 gap. A kind whose reader moment is BROKEN (its
    predicate cannot be run) or MALFORMED (its `when` is present and invalid)
    was indistinguishable at every surface from a kind that is fine, because
    no surface asked. The evaluator is not changed here and must not be: one
    trigger evaluator, and a second interpretation of BROKEN living in this
    verb is exactly the divergence `read_moments` documents itself against.

    THE TWO FINDINGS ARE SEPARATE ROWS, and the split is the whole point
    rather than taxonomy. BROKEN is a predicate that ran and could not
    answer — the world moved under a moment that is correctly declared, and
    the repair is out in the world. MALFORMED is a `when` nobody could ever
    have executed — the repair is in the declaration, one line away. Folding
    them would hand a reader one word for two repairs, which is the same
    collapse the third-answer rule forbids one level down.

    THE ABSENT MOMENT IS NOT A FINDING and never becomes one. UNDECLARED is
    the legitimate default across nearly every kind in every repo here: a
    kind is read when a session reads it, and saying so is not a gap. A verb
    that graded absence would fire on the whole registry on its first run,
    which is the guard-over-legitimate-work shape that trains the override
    reflex (law 11).

    FOUR ANSWERS NOW, not three, and DERIVED is honest about what it is NOT
    (O6 §4 Part A, lc-253). A `verb:` or bare `session` reader with no
    authored `when` renders DERIVED rather than UNDECLARED — the ref's own
    shape supplies the moment (the verb running; the kind's home being
    written) — but DERIVED is deliberately NOT folded into `declared`: it
    carries no authored `when`, and derivation is the DEFAULT this design
    supplies, not a declaration anyone made. Counting it as declared would
    let the tally claim authorship for a fact the declaration's author never
    wrote, which is the same false-assurance shape lc-252 repaired one word
    over. So `declared` keeps its exact prior meaning (an authored `when`,
    executed or not) and DERIVED gets its own, fourth number — the three-
    number honesty widens rather than bends.

    THREE ANSWERS, and the empty case is the one that needs saying. A
    declaration with NO kinds, or one whose kinds declare no reader entries
    at all, produces zero evaluations — and a printed zero reads exactly like
    a registry that was checked and found clean. So nothing-to-evaluate is
    COULD NOT VERIFY naming what was absent, never CLEAN.
    """
    kinds = doc.get("kinds") or {}
    if not kinds:
        out("kind moments: COULD NOT VERIFY — the declaration registers no "
            "kinds, so no reader moment could be evaluated. NOT a clean "
            "registry: zero evaluations and zero problems print the same.")
        return exits.COULD_NOT_VERIFY

    broken, malformed, entries, declared, derived, ran = [], [], 0, 0, 0, 0
    for name in kinds:
        body = kinds[name] if isinstance(kinds[name], dict) else {}
        moments = decl.read_moments(body, repo)
        out(f"kind: {name}")
        if not moments:
            out("    (no reader entries declared)")
            continue
        for m in moments:
            entries += 1
            detail = f" — {m.detail}" if m.detail else ""
            out(f"    reader {m.reader}: {m.state}{detail}")
            # `read_moments` preserves an absent `when` as UNDECLARED or, for
            # a derivable ref shape, DERIVED. Every other state comes from a
            # present `when`, including NONE and a malformed one, which
            # remain declarations even when unexecuted. DERIVED is counted
            # apart from both: it is not nothing (UNDECLARED), and it is not
            # authored (declared) — see the docstring's FOUR ANSWERS note.
            if m.state == decl.READ_MOMENT_DERIVED:
                derived += 1
            elif m.state != decl.READ_MOMENT_UNDECLARED:
                declared += 1
            if m.state in (lanes.FIRE, lanes.QUIET, lanes.BROKEN):
                # EXECUTED, and counted apart from the ones merely READ. The
                # two numbers are this verb's own honesty: a registry where
                # every reader entry is UNDECLARED yields many entries and
                # zero declarations or executions; the summary must retain
                # all three facts rather than call those entries declared.
                ran += 1
            if m.state == lanes.BROKEN:
                broken.append((name, m))
            elif m.state == decl.READ_MOMENT_MALFORMED:
                malformed.append((name, m))

    if not entries:
        out(f"kind moments: COULD NOT VERIFY — {len(kinds)} kind(s) "
            "registered and NOT ONE declares a reader entry, so there was no "
            "moment to evaluate. The registry was read; it had nothing to "
            "answer with.")
        return exits.COULD_NOT_VERIFY

    for name, m in broken:
        out(f"FINDING [reader_moment_broken] kind {name!r} declares a "
            f"predicate moment for reader {m.reader!r} that could not be "
            f"evaluated: {m.detail or '(no detail)'}. The declaration is "
            "well-formed and the WORLD is what moved — the predicate's "
            "command is missing, unrunnable, or times out — so the repair is "
            "out there, not in this file. Until it answers, this kind's "
            "reader moment is not QUIET; it is unknown, and a session "
            "reading the declaration alone cannot tell those apart.")
    for name, m in malformed:
        out(f"FINDING [reader_moment_malformed] kind {name!r} declares a "
            f"`when` for reader {m.reader!r} that is PRESENT and invalid: "
            f"{m.detail or '(no detail)'}. Nothing could ever have executed "
            "it, so the repair is one line in the declaration. This is not "
            "an absent moment: an absent `when` is the legitimate default "
            "and is reported UNDECLARED without a finding, while this one is "
            "somebody's mistake wearing the default's face.")

    tally = (f"{entries} reader entr{'y' if entries == 1 else 'ies'}, "
             f"{declared} declared moment(s), {derived} DERIVED, "
             f"{ran} EXECUTED over {len(kinds)} kind(s)")
    # THE RESULT CARRIER (W1 act 2). The banner reads this back, so what is
    # written here is what a later session is told: the four REACH numbers
    # travel with the two problem counts, because a stored "0 broken, 0
    # malformed" over a run that executed nothing is the same false
    # assurance the verdict line above refuses to print. `derived` is its
    # own number rather than folded into `declared`: nothing was authored,
    # so counting it as a declaration would claim authorship for a default
    # (O6 §4 Part A, lc-253).
    if args is not None:
        args.fire_detail = (f"broken={len(broken)} malformed={len(malformed)} "
                            f"entries={entries} declared={declared} "
                            f"derived={derived} executed={ran} "
                            f"kinds={len(kinds)}")
    if broken or malformed:
        out(f"kind moments: FINDING — {tally}: {len(broken)} broken, "
            f"{len(malformed)} malformed.")
        return exits.FINDING
    out(f"kind moments: CLEAN — {tally}, none broken and none malformed. "
        "THE EXECUTED NUMBER IS THE VERDICT'S REACH: only an executed "
        "moment was put to a predicate. DERIVED costs nothing to author and "
        "is not a declaration; an absent `when` with no derivable ref shape "
        "is UNDECLARED, which is the legitimate default rather than a gap. "
        "A run whose EXECUTED number is 0 has read the registry and "
        "exercised no predicate at all — clean, and clean about very "
        "little.")
    return exits.CLEAN


# --- `kind read` (lc-255, O6 §4 Part C, D3a): the read AS AN OBSERVED ACT ---

#: Above this many lines a single-file body is a POINTER, never the text
#: itself (assigned). Named so the two branches below cite one number rather
#: than two copies of a literal drifting apart.
_READ_BODY_LINE_LIMIT = 400


def cmd_kind_read(args, out, repo: Path, doc: dict) -> int:
    """Print a registered kind's BODY (or its pointer where large) — the
    read routed through a verb so the fire log records it (D3a).

    THREE ANSWERS (law 1). An unregistered `name` is a FINDING
    (`read_kind_unregistered`) — the same check `kind show` already makes
    inline in `cli.py`, reused here rather than reinvented. A registered
    kind whose home resolves to nothing READABLE — an unresolvable
    variable, an absent path, an unreadable file, a pattern matching no
    file — is COULD NOT VERIFY, naming what was absent. That is this verb's
    OWN third answer and never a registered refusal: "the world does not
    have this file yet" is a fact about the repo, not a defect in the
    declaration (`kind show`'s sibling reasoning for an absent home,
    `render_digest`, draws the identical line). Anything else is CLEAN.

    BODY VS POINTER (assigned). A home resolving to exactly one existing
    file prints that file's body verbatim when it is at most
    `_READ_BODY_LINE_LIMIT` lines; a longer single file, or a home matching
    more than one file (a directory or a glob), prints a POINTER instead —
    repo-relative path(s), a count where there is more than one, and a
    date. The pointer IS a clean read: it still fires `read=<kind>` below,
    because the proxy this verb exists to supply is "was the verb invoked",
    never "was the whole body dumped".

    WHY THE FILE-RESOLUTION SHAPE COMES FROM `declaration.render_digest`
    AND NOT FROM `retire.list_home`. `list_home` counts INSTANCES OF A
    KIND — for a carrier home it returns one entry per fixed-slot block
    (an item ident per item), which is the right notion for the growth
    walk and the wrong one here: a carrier holding twenty items is still
    ONE PHYSICAL FILE, and grading it by item count would route a
    single-file home onto the multi-file pointer branch it does not
    belong on. `render_digest` already resolves a home to FILES —
    `retire.expand_home`, then glob / directory / plain-file, newest by
    mtime — which is the question this verb is actually asking, so that
    branch shape is reused (`retire.expand_home`, `retire._UNEXPANDED`,
    `retire._shown`, `declaration._mtime_date` — each already reached
    across this same module boundary by `render_digest` itself) rather
    than re-derived a third time.

    THE PROXY BOUND (assigned wording) prints on every clean invocation,
    body and pointer alike: "read" here means read-through-this-verb, and a
    session that opens the file directly is invisible to the fire log by
    construction — the design's own stated boundary (§4 Part C), restated
    in the one place a caller will actually see it.
    """
    kinds = doc.get("kinds") or {}
    if args.name not in kinds:
        out(f"FINDING [read_kind_unregistered] {args.name!r} is not a "
            f"registered kind. Registered: {', '.join(kinds) or '(none)'}")
        return exits.FINDING

    body = kinds[args.name] if isinstance(kinds[args.name], dict) else {}
    home = body.get("home")
    if not isinstance(home, str) or not home.strip():
        out(f"COULD NOT VERIFY: kind {args.name!r} declares no `home`, so "
            "there is nothing to read.")
        return exits.COULD_NOT_VERIFY

    resolved = retire.expand_home(home)
    if retire._UNEXPANDED.search(resolved):
        out(f"COULD NOT VERIFY: the home of kind {args.name!r} ({home!r}) "
            "carries a variable this verb cannot resolve, so nothing was "
            "read — not an empty file.")
        return exits.COULD_NOT_VERIFY

    path = repo / resolved
    try:
        if "*" in resolved:
            # Mirrors `render_digest`'s own glob branch, in-tree and
            # absolute-home alike: an in-repo glob globbed from the
            # matched directory itself would double the prefix and report
            # a false zero over a directory that holds real files.
            if Path(resolved).is_absolute():
                stem = resolved.split("*", 1)[0]
                base = Path(stem if stem.endswith("/")
                            else str(Path(stem).parent))
                pattern = resolved[len(str(base)):].lstrip("/")
                hits = sorted(base.glob(pattern)) if base.is_dir() else []
            else:
                hits = sorted(repo.glob(resolved))
            hits = [p for p in hits if p.is_file()]
        elif path.is_dir():
            hits = sorted(p for p in path.rglob("*") if p.is_file())
        elif path.is_file():
            hits = [path]
        else:
            hits = []
    except OSError as exc:
        out(f"COULD NOT VERIFY: the home of kind {args.name!r} ({home!r}) "
            f"could not be examined ({exc!r}).")
        return exits.COULD_NOT_VERIFY

    if not hits:
        out(f"COULD NOT VERIFY: the home of kind {args.name!r} ({home!r}, "
            f"resolved: {resolved!r}) matched no file. Nothing was read.")
        return exits.COULD_NOT_VERIFY

    if len(hits) == 1:
        target = hits[0]
        try:
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            out(f"COULD NOT VERIFY: {retire._shown(target, repo)} could "
                f"not be read ({exc!r}).")
            return exits.COULD_NOT_VERIFY
        lines = text.splitlines()
        shown = retire._shown(target, repo)
        if len(lines) <= _READ_BODY_LINE_LIMIT:
            out(f"kind {args.name!r} — body of {shown} ({len(lines)} "
                "line(s)):")
            out("")
            for line in lines:
                out(line)
        else:
            out(f"kind {args.name!r} — {shown}, {len(lines)} line(s), "
                f"mtime {decl._mtime_date(target)}")
            out("body large — open the path above.")
    else:
        newest = max(hits, key=lambda p: p.stat().st_mtime)
        out(f"kind {args.name!r} — {len(hits)} file(s) under {home!r}, "
            f"newest: {retire._shown(newest, repo)} "
            f"({decl._mtime_date(newest)})")

    out("proxy bound: read here means read-through-this-verb — a direct "
        "file open is not counted.")
    args.fire_detail = f"read={args.name}"
    return exits.CLEAN
