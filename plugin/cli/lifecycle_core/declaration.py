"""The kind registry: `.claude/lifecycle.json`, its schema, and its reader.

THE PRIMITIVE IS THE KIND, NOT THE ITEM (design §3.0). Every kind of thing a
repo persists is registered with seven declared stages:

    home · writer · reader · staleness · exit · growth · trigger

and a kind with an UNDECLARED STAGE is a checker finding. The sixth stage was
`bound` until the schema wave and is `growth` now — not a rename but a
replacement: R22 withdrew caps outright, so what a kind declares is one of
`bounded-by-exit` / `compacted` / `unbounded-with-reason`, and the alarm is
FLOW rather than size. That is the whole
design in one sentence: the Begehung's thirty findings sorted almost entirely
into "a kind with one stage undeclared" — the ledger had no exit, the done
home no staleness rule, the registry no reader, the plugin cache no exit and
no rollback — so the stage list is what this file refuses to let anyone leave
blank.

WHAT COUNTS AS CORRECT comes from the design document, never from a
declaration found on disk. An expectation derived from the artifact it grades
moves with the mutant and stays green on the corruption it exists to catch.
So the required key sets, the closed vocabularies and the shape rules below
are written from §3.0/§3.1/§3.3/§3.4, and a real `lifecycle.json` is only
ever an input.

REFUSE-UNLESS-DECLARED-PRIVATE (§3.1). An undeclared, ignored or malformed
declaration fails LOUDLY — never open. The three failures are distinct rows
with distinct messages, because "there is no declaration" and "git cannot see
the declaration" have different repairs and a shared message would send a
reader to the wrong one.

THE THIRD ANSWER runs all the way through: a declaration that cannot be READ
(a permission error, a directory where a file belongs) is COULD NOT VERIFY,
not a finding. A declaration whose bytes are present and wrong is a finding.
The two never share an exit code — that is the contract in `exits.py`.
"""

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from . import exits
from . import firelog

#: The declaration format this build understands. A file stamped ABOVE it is
#: refused rather than guessed at — the same rule `ITEMS.md` gets, and for the
#: same reason: an old tool reading a new file silently drops what it does not
#: recognise, and a dropped slot is invisible in the output.
#:
#: ONE SCHEMA VERSION PER REPO (§3.8c). This number is stamped in the
#: declaration and the carrier files' `schema:` lines must EQUAL it — a
#: mismatch is `schema_mismatch`, not a floor question. Two numbers for one
#: fact is the shape that diverges the moment they disagree, and the reader
#: resolves through whichever it happens to open.
#: BUMPED 2 -> 3 on 2026-09-19 (lc-218). The number had stopped identifying
#: the shape: lc-168 (41cee8b) made the `trigger` stage REQUIRED, so a
#: declaration valid under schema 2 on one day was invalid under schema 2 on
#: the next, while the stamp said the same thing both times. That is the
#: label-over-body class at the most load-bearing label in the system, since
#: every reader resolving through the number resolves through a label whose
#: body moved under it. The bump was owed from 2026-09-18 and was deferred
#: then for a timing reason rather than a correctness one.
#: BUMPED 3 -> 4 on 2026-09-19 (lc-224 act 2, its OWN act per lc-218's
#: MUST-NOT-BUILD — one number, one command per bump, so a failure names one
#: cause). lc-224 gave the `reader` stage a per-entry `when`, so a reader list
#: entry is now a bare string OR an object. That widened the accepted SHAPE,
#: and the reason it is a bump rather than an additive convenience was PROVED
#: rather than argued: run against a build at floor 3, a declaration carrying
#: the object form returns `declaration_malformed` ("reader must be a
#: non-empty list of non-empty strings"), with a bare-string control clean. So
#: without the bump an older build reads a NEWER declaration and reports it
#: BROKEN — a confident wrong finding — where `schema_above_floor` would
#: otherwise refuse honestly, which is the very failure the floor guard's own
#: rationale names: an old tool reading a new file drops what it does not
#: recognise, and a dropped slot is invisible in the output.
SCHEMA_FLOOR = 6

#: Where the declaration lives, relative to the repo root. Tracked; the
#: install step adds the `.gitignore` negation and this reader fails on an
#: ignored declaration (§3.0 — G1's recorded defect, closed once per repo
#: family rather than once per repo).
DECLARATION_REL = Path(".claude") / "lifecycle.json"

#: §3.4. `unattended` is designed-for and PARKED — it is a legal declared
#: value, and the machinery behind it is wave 3's.
TRIGGER_POLICIES = ("on-demand", "advise", "auto", "unattended")

#: §3.0 — exit is one of these four, WITH the recording act.
EXIT_ACTIONS = ("move", "compact", "delete", "never")

#: R22 — the GROWTH CONTROL vocabulary, closed. This replaces the `bound`
#: stage outright rather than re-labelling it: `bound` is the CAP concept R22
#: withdrew ("no caps at all — everything has a place, a good reason, and is
#: controlled"), and a key still spelled `bound` over a value reading
#: "unbounded-with-reason" is a label whose body has moved. §3.0b's invariant
#: 2 already names the sixth stage "growth control".
#:
#:   bounded-by-exit        every instance leaves by a recorded exit
#:   compacted              instances fold on a declared rule
#:   unbounded-with-reason  it grows, and the reason is declared
#:
#: The alarm is FLOW, never size: a kind that GREW WITHOUT AN EXIT EVENT is
#: the finding, whatever its count. A large kind draining steadily is fine; a
#: small one never draining is not.
GROWTH_MODES = ("bounded-by-exit", "compacted", "unbounded-with-reason")

#: The seven stages, closed. `kind_stage_undeclared` is a finding for any kind
#: missing any of them, which is why this tuple is the single source and no
#: check below restates it.
KIND_STAGES = ("home", "writer", "reader", "staleness", "exit", "growth",
               "trigger")

#: THE SEVENTH STAGE IS **WHEN** (lc-168). The other six say what a kind is,
#: where it lives, who writes and reads it, when it goes stale and how its
#: growth is controlled — and none of them says when the write FIRES. For the
#: four verb-written kinds the answer was always implicit in the act: `item
#: close` writes a closure because the verb ran, and nobody has to remember
#: anything. For the seventeen `writer: session` kinds there was no WHEN at
#: all, which is the whole distance between a kind that administers itself and
#: one that waits for a person to notice it.
#:
#: The vocabulary is closed and has exactly two members, because there are
#: exactly two ways a write can be occasioned: an ACT that carries it, or a
#: CONDITION somebody must evaluate.
#:
#:   verb <name>        the trigger is implicit in the act — the write happens
#:                      because that verb ran. `<name>` must be a real command
#:                      path, checked against the PARSER rather than a list
#:                      restated here: a restated list cannot age loudly, and a
#:                      trigger naming a verb that does not exist is a kind
#:                      nothing will ever fire.
#:   predicate <cmd>    a condition, evaluated by `lanes.evaluate_trigger` —
#:                      the ONE evaluator, whose exit mapping is total, so a
#:                      predicate that cannot run is BROKEN and never quiet.
#:
#: WRITING A PREDICATE: PROVE THREE ARMS BEFORE THE VALUE LANDS — fire, quiet,
#: and BROKEN, the last being the one nothing else will ever exercise. A
#: predicate accepted on its fire-and-quiet pair is an unproven instrument in a
#: declaration's costume, and it is WORSE than `none`: none-with-a-reason is
#: honest prose, while a false-firing predicate is a lane that reads alarming
#: forever and trains the override reflex that kills the guard. This is law 2's
#: red-first applied to a declared VALUE rather than a registry row, and the
#: argument is the same — a value nobody has fired is not known to discriminate.
#:
#: THE SHAPE RULE HAS TWO HALVES AND BOTH ARE NEEDED. Measured on two
#: predicates, 2026-09-18:
#:   * DO NOT WRAP A COMMAND WHOSE OWN EXIT ALREADY CARRIES THREE STATES. A
#:     bare `grep -q PATTERN FILE` is 0 found / 1 not-found / 2 file-unreadable
#:     — the contract, free. Wrapping it in `test "$(...)" -ne "$(...)"`
#:     destroys it: `test` answers 0 or 1 only, so BROKEN has nowhere to land
#:     and the dead instrument renders as a FIRING lane rather than a quiet
#:     one — the mirror of the failure the mapping exists to prevent, and the
#:     worse direction, because a permanent alarm is overridden rather than
#:     investigated.
#:   * WHERE NO BARE COMMAND CARRIES THE THREE STATES, the predicate needs
#:     INPUT GUARDS to give BROKEN somewhere to land — and that makes it a
#:     SCRIPT in the repo's tools, not a longer one-liner. A script is also the
#:     answer to a second hazard: shell inside a quoted JSON payload is two
#:     transforming layers between author and executor, and a backticked word
#:     in such a payload is command-substituted away, leaving a value that
#:     parses and reads like prose with a word missing. A file has one reader.
#: The first half prevents the defect; the second catches it where prevention
#: is not available.
#:   none, declared why: <reason>
#:                      the kind genuinely has no button, and says so. NOT a
#:                      loophole and not invented here: the design of record's
#:                      own test is "every kind reaches a verb, OR DECLARES WHY
#:                      IT CANNOT", and this repo already spells that escape
#:                      twice — `staleness: "none, declared why: ..."` and
#:                      `growth: "unbounded-with-reason — ..."`. The word
#:                      carries the obligation: without the reason it is a
#:                      shrug, which is what the stage exists to stop being.
#:                      What it buys is that seventeen buttonless kinds stop
#:                      being INVISIBLE and become COUNTABLE — a kind that
#:                      declares no trigger is a finding, one that declares
#:                      `none` is a known member of a population somebody can
#:                      read off the registry.
#:
#: What is deliberately NOT a member: a time, a cadence, a "periodically". A
#: schedule is a thing that must be remembered by whatever holds the clock,
#: and this system owns no clock — the tick is the verb.
TRIGGER_MODES = ("verb", "predicate", "none")

#: §3.8c — the TYPED reference vocabulary for `reader` and `writer`. Closed:
#: prose in the slot is a finding, because prose cannot be RESOLVED, and an
#: unresolvable reader is exactly the "kind nothing reads" this registry
#: exists to make visible. Two shapes: PREFIXED types name a target that must
#: resolve, BARE types are roles that resolve by definition.
REF_PREFIXES = ("lane", "verb", "hook", "producer")
REF_BARE = ("session", "operator")

#: The whole closed set, in the design's own order — the ROUTE SET the
#: `dangling_reference` refusal's text names (§3.8c: "`dangling_reference`
#: then reaches every type"). Read by the roster's route-set check, which is
#: why it lives here as data rather than in a sentence.
REF_TYPES = ("lane", "verb", "hook", "session", "producer", "operator")

#: lc-224 — THE READER STAGE GAINS A PER-ENTRY WHEN. Decision (LEDGER
#: 8a5d760): the WHEN attaches to each `reader` ENTRY rather than as an
#: eighth kind stage, because a per-kind scalar cannot describe a kind whose
#: reader list MIXES a bare role with a `verb:`/`hook:` reference — this
#: repo's own `laws` kind (`reader: ["session", "verb:audit"]`) is exactly
#: such a kind, and seventeen of twenty-six declared kinds carry more than
#: one reader entry.
#:
#: Deliberately NARROWER than `TRIGGER_MODES`: `verb` is not a member. A read
#: occasioned by a verb is already expressible by making the reader entry
#: itself `verb:<name>` — a `verb` WHEN there would be a second spelling of a
#: fact the reader TYPE already carries, not a new one.
#:
#:   predicate <cmd>       a condition, evaluated by `lanes.evaluate_trigger`
#:                         — the ONE evaluator, same as the `trigger` stage.
#:   none, declared why: <reason>
#:                         the read genuinely has no moment, and says so —
#:                         the same escape `staleness`, `growth` and
#:                         `trigger` already use.
#:
#: LEGAL ONLY ON A BARE READER (`session`, `operator`). On a prefixed reader
#: the moment is the referenced act firing, so a `when` there is a second
#: answer to a settled question.
READER_WHEN_MODES = ("predicate", "none")

#: THE ONE PLUGIN-RESERVED GOAL (§3.1b, operator 2026-08-28): "work on this
#: repo's own carrier, method, hooks, machinery, or migration residue". It is
#: in no declaration's `goals` list and is not declarable per repo — the
#: plugin adds it to every repo's EFFECTIVE goal set (`effective_goals`
#: below), so self-work is bookable in a fresh repo from its first `item add`
#: and in a migrated one with nothing declared. A rename is this constant and
#: nothing else; no per-repo edit follows it.
RESERVED_GOAL = "tend"

#: Top-level keys every declaration carries. An EMPTY declared list is not the
#: same as an ABSENT key — absent is a finding, empty is a stated fact — so
#: `lanes` and `template-bindings` are required even where a repo has none.
#:
#: `ready-cap` IS GONE (R22, this wave). It demanded a positive integer under
#: a design that had withdrawn caps, so the only honest value was one the
#: schema refused; the head is DERIVED by `head-rule` over all READY instead.
#: `leak-scan` is new (§3.3): the source-scope foreign-path class is enabled
#: PER REPO by declaration, never by the scanner guessing which repo it is in.
REQUIRED_KEYS = (
    "schema", "id-prefix", "public", "laws", "closure-home", "trigger-policy",
    "goals", "head-rule", "lanes", "template-bindings", "leak-scan", "kinds",
)

#: `delegation` (wave 2, the stall-detector booking: cache-fix BACKLOG.md's
#: PARKED "ended on an announcement" entry) is OPTIONAL, deliberately NOT in
#: `REQUIRED_KEYS`. A new REQUIRED key is a schema bump by definition (§3.8c:
#: one schema version per repo), and law 25 makes every schema change ship
#: its migration, dry-run first, over every declared repo — dragging
#: `migrate --schema-from 2` into a lane whose scope is the verb and the
#: field, not a migration wave. Absent means "none" — no active delegation —
#: the same shape `leak-scan` (absent-equivalent: off) and `head-rule`
#: (bare "none") already use. THE VALUE SHAPE BEYOND "closed two-word
#: vocabulary" is NOT specified anywhere this build's grounding reaches
#: (the design document, this repo's CLAUDE.md/JOURNAL.md, the booking
#: entry) — the wave-3 Stop-hook detector that actually reads this field is
#: what will need a richer shape (which peer, which lane) if one turns out
#: to be required, and inventing that shape now would be this lane
#: deciding wave 3's design. So the vocabulary is the minimum the booking's
#: own predicate needs ("delegation active AND ..."), flagged in the
#: dispatch report as a judgment call rather than a brief-specified value.
DELEGATION_VALUES = ("none", "active")

#: A REPO'S OWN CLOSURE WORDS (lc-91), mapped onto the closed vocabulary's
#: two. OPTIONAL for the reason `delegation` is: a new REQUIRED key is a schema
#: bump by definition (§3.8c), and a repo declaring none must behave exactly as
#: it does today.
#:
#: WHAT IT FIXES. `migrate` reads a source carrier's grade word and looks it up
#: in `migrate.RULES`; a carrier that closes entries as `ERLEDIGT` or
#: `RESOLVED` therefore migrated them as UNCLASSIFIED — the closure never
#: reached the done home. The map TRANSLATES such a word at the migration
#: boundary: `{"ERLEDIGT": "DONE"}`. It does NOT widen `items.GRADES_CLOSED`,
#: so everything downstream keeps seeing DONE and DROPPED, and `ERLEDIGT`
#: never becomes a grade a carrier may itself carry.
#:
#: FLAT, word -> grade, because that is the LOOKUP direction — the code always
#: asks "the carrier says ERLEDIGT, which grade is that?", never "which words
#: mean DONE?" — and because JSON object keys are unique, so one word mapping
#: to two grades is a state the file itself cannot express. The inverted shape
#: would need its own detection, its own refusal and its own roster row.
#:
#: MATCHING IS CASE-SENSITIVE. `migrate._GRADE_WORD` yields an UPPERCASE word
#: and nothing else, so the declared key is compared byte-for-byte against
#: what the carrier's own shape already isolated; a lower- or mixed-case
#: declared word could never match anything, and is refused here rather than
#: sitting in the file reading like a live rule. Same for a word this tool
#: already rules on, and for a grade outside the closed two: each is a way the
#: declaration says something the tool will not do, which is worse than saying
#: nothing.
#:
#: AN UNDECLARED WORD STAYS UNCLASSIFIED. The repair for a missing mapping is
#: a declared rule, never a looser matcher (lc-19's own sentence).
CLOSURE_WORDS_KEY = "closure-words"

#: Keys a declaration may NOT carry any more, each with what replaced it.
#: Named rather than ignored: a withdrawn key left in a file reads exactly
#: like a live one, and silently dropping it would leave the writer believing
#: a number still bounds something.
RETIRED_KEYS = {
    "ready-cap": "R22 withdrew caps. The head is DERIVED by `head-rule` over "
                 "all READY items (`item ready --head`); a cap fights the "
                 "GRADING rather than the growth and is escaped by "
                 "relabelling, which is this repo's recorded 2026-08-11 "
                 "failure (JOURNAL J9).",
    "bound": "renamed to `growth` and its vocabulary closed to "
             + ", ".join(GROWTH_MODES) + " (R22).",
}


@dataclass(frozen=True)
class Finding:
    """One thing wrong. `row` is the refusal-table row id, so a finding and
    the roster entry that proves it carry the same name rather than two."""
    row: str
    message: str


@dataclass
class Result:
    """What a read or a check answered.

    `code` is the verb contract's answer for the whole run; `findings` says
    what, and `declaration` is the parsed body when there is one. A caller
    that only reads `code` is still correct — the findings never hide a
    verdict.
    """
    code: int
    findings: list[Finding] = field(default_factory=list)
    declaration: dict | None = None
    path: Path | None = None
    #: Checks that could not run at all, each with why. Kept apart from
    #: findings so a run says which of the three answers each half gave.
    unverified: list[str] = field(default_factory=list)

    def add(self, row: str, message: str) -> None:
        self.findings.append(Finding(row, message))
        self.code = exits.worst([self.code, exits.FINDING])

    def cannot_verify(self, why: str) -> None:
        self.unverified.append(why)
        self.code = exits.worst([self.code, exits.COULD_NOT_VERIFY])


# --- git visibility ----------------------------------------------------------

def ignored_by_git(repo: Path, rel: Path) -> bool | None:
    """Is `rel` swallowed by a `.gitignore` in `repo`?

    Three answers, not two: True ignored, False visible, None COULD NOT
    VERIFY — no git, not a repo, git errored. Treating every non-zero as "not
    ignored" is how this check would report a clean board over a repo git
    cannot read at all.

    NEVER `-v` FOR THE VERDICT. Measured 2026-08-26, and it is the opposite
    of what the flag looks like it does: `-v` changes the EXIT SEMANTICS, not
    just the output. Without it, 0 means ignored and 1 means not ignored.
    With it, 0 means "some pattern had an opinion" — INCLUDING a negation —
    so a correctly negated `!.claude/lifecycle.json` exits 0 and reads as
    ignored. The pair, one invocation apart, in one scratch repo:

        without -v:  negated -> 1   genuinely ignored -> 0   untouched -> 1
        with    -v:  negated -> 0   genuinely ignored -> 0

    This build's first draft used `-v` and fired on a repo whose negation was
    correct. A guard that fires on legitimate work trains the override reflex
    that kills it, so the flag is asked separately, AFTER the verdict, and
    only to name the pattern in the message.

    `--no-index` IS REQUIRED, and its absence was a shipped defect. Without
    it `check-ignore` skips TRACKED paths and exits 1 — "not ignored" — for
    every declaration that has been committed, which is every declaration
    this checker will ever meet in a real repo. Measured 2026-08-26, one
    repo, one path, negation absent:

        tracked, negation absent:  --no-index -> 0 (sees it)   bare -> 1
        untracked, negation absent:  --no-index -> 0    (the plant still fires)
        untracked, negation present: --no-index -> 1    (the control still clean)

    So the flag closes the tracked case and leaves the existing row's pair
    intact. The hazard is NOT "a tracked file reaches every clone whatever
    the ignore rules say" — that sentence is true and answers a different
    question. The hazard is a declaration one `git rm --cached` away from
    vanishing silently: tracked today, ignored tomorrow, and a checker that
    could not see it would report a clean board over the exact
    misconfiguration it exists to catch.
    """
    try:
        p = subprocess.run(["git", "-C", str(repo), "check-ignore",
                            "--no-index", str(rel)],
                           capture_output=True, text=True)
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode == 0:
        return True
    if p.returncode == 1:
        return False
    return None


def ignore_pattern(repo: Path, rel: Path) -> str:
    """The `.gitignore` line doing the swallowing — for the message only.

    Asked only once `ignored_by_git` has already said True, because on its
    own this call cannot tell a match from a negation (see above).

    `--no-index` here too, and it must MATCH the verdict call's universe of
    paths. Measured 2026-08-26 on a tracked, genuinely ignored path: without
    the flag this call prints NOTHING and exits 1, so the message on the
    newly-covered tracked case would degrade to "(pattern could not be
    resolved)" — a finding that cannot name what caused it. The `-v`
    exit-semantics hazard above does not reach here: this function reads
    STDOUT only and never the exit code, and it runs only after the verdict
    is already True.
    """
    try:
        p = subprocess.run(["git", "-C", str(repo), "check-ignore", "-v",
                            "--no-index", str(rel)],
                           capture_output=True, text=True)
    except (OSError, subprocess.SubprocessError):
        return "(pattern could not be resolved)"
    line = p.stdout.strip().split("\t")[0] if p.stdout.strip() else ""
    return line or "(pattern could not be resolved)"


# --- reading -----------------------------------------------------------------

def read(repo: Path) -> Result:
    """Load and validate a repo's declaration. The whole refusal surface."""
    path = repo / DECLARATION_REL
    res = Result(code=exits.CLEAN, path=path)

    if not path.exists():
        res.add("declaration_absent",
                f"no declaration at {DECLARATION_REL}. A repo with no "
                "declaration is REFUSED, never treated as private by "
                "default: the tool cannot know whether it is public, what "
                "its goals are, or which kinds it keeps.")
        return res

    ign = ignored_by_git(repo, DECLARATION_REL)
    if ign is None:
        res.cannot_verify(
            f"could not ask git whether {DECLARATION_REL} is ignored "
            "(no git, or not a work tree). The declaration may be invisible "
            "to every other checkout and nothing here would know.")
    elif ign:
        res.add("declaration_ignored",
                f"{DECLARATION_REL} is swallowed by "
                f"{ignore_pattern(repo, DECLARATION_REL)}. It is present here "
                "and absent in every fresh clone, so a checker elsewhere "
                "reports a clean board over an unregistered repo. Add the "
                "negation (`!.claude/lifecycle.json`) beside the `.claude/*` "
                "rule, in the SAME commit as the file itself — a `git add` "
                "against a still-ignored path is silently a no-op.")
        return res

    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        res.cannot_verify(f"{DECLARATION_REL} could not be read ({exc!r}). "
                          "Unreadable is not clean and it is not a finding.")
        return res

    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as exc:
        res.add("declaration_malformed",
                f"{DECLARATION_REL} is not valid JSON: {exc.msg} "
                f"(line {exc.lineno}, column {exc.colno}).")
        return res

    if not isinstance(doc, dict):
        res.add("declaration_malformed",
                f"{DECLARATION_REL} parses, but its top level is "
                f"{type(doc).__name__}, not an object.")
        return res

    res.declaration = doc
    validate(doc, res, repo=repo)
    return res


# --- validation --------------------------------------------------------------

def _needs_why(value: str, opener: str) -> bool:
    """A declared "none"/"unbounded" must carry its reason.

    `staleness: "none"` and `bound: "unbounded"` are exactly the undeclared
    stages this registry exists to make visible — the word alone is a blank
    with a plausible face on it. §3.0 spells both as "…, declared why", so
    the bare word is refused and anything carrying a reason is accepted.
    """
    rest = value[len(opener):].strip(" \t:,—-")
    return len(rest) < 8


def validate(doc: dict, res: Result, repo: Path | None = None) -> None:
    """Every rule the design states about a declaration's body."""
    missing = [k for k in REQUIRED_KEYS if k not in doc]
    if missing:
        res.add("declaration_malformed",
                "declaration is missing required key(s): "
                + ", ".join(sorted(missing))
                + ". An ABSENT key is a finding even where the repo has none "
                "of the thing — an empty declared list is a stated fact, an "
                "absent one is silence.")

    for key, why in RETIRED_KEYS.items():
        if key in doc:
            res.add("declaration_retired_key",
                    f"`{key}` is no longer part of the declaration: {why} A "
                    "withdrawn key left in the file reads exactly like a live "
                    "one, so it is refused rather than ignored — `lifecycle "
                    "migrate --schema-from <n>` removes it.")

    schema = doc.get("schema")
    if "schema" in doc:
        if not isinstance(schema, int) or isinstance(schema, bool):
            res.add("declaration_malformed",
                    f"`schema` must be an integer, got {schema!r}.")
        elif schema > SCHEMA_FLOOR:
            res.add("schema_above_floor",
                    f"declaration is stamped schema {schema}; this build "
                    f"understands {SCHEMA_FLOOR}. Refusing rather than "
                    "parsing it: an old tool reading a new file drops what "
                    "it does not recognise, and a dropped slot is invisible "
                    "in the output.")
            return
        elif schema < 1:
            res.add("declaration_malformed",
                    f"`schema` must be >= 1, got {schema}.")

    if "public" in doc and not isinstance(doc["public"], bool):
        res.add("declaration_malformed",
                f"`public` must be true or false, got {doc['public']!r}. "
                "There is no third value: the default in the absence of a "
                "declaration is refuse, not private.")

    for key in ("id-prefix", "laws", "closure-home"):
        if key in doc and (not isinstance(doc[key], str) or not doc[key].strip()):
            res.add("declaration_malformed",
                    f"`{key}` must be a non-empty string, got {doc[key]!r}.")

    if isinstance(doc.get("id-prefix"), str) and doc["id-prefix"].strip():
        pref = doc["id-prefix"]
        if not pref.replace("-", "").isalnum() or not pref[0].isalpha() or pref != pref.lower():
            res.add("declaration_malformed",
                    f"`id-prefix` must be lowercase alphanumeric with "
                    f"hyphens and start with a letter, got {pref!r} — item "
                    "ids are `<prefix>-<n>` and immutable across moves.")

    if "trigger-policy" in doc and doc["trigger-policy"] not in TRIGGER_POLICIES:
        # USE-EVIDENCE for §3.11 rule 6, recorded where the rule is evaluated.
        # The rule is "on-demand is the default and the vocabulary is closed";
        # what it FIRES on is a policy word outside that vocabulary, and a
        # rate reconstructed later from git is not a rate.
        from . import judgment
        judgment.record_use("trigger-policy-default", "fired",
                            detail=f"policy={doc['trigger-policy']!r}")
        res.add("declaration_malformed",
                f"`trigger-policy` must be one of {', '.join(TRIGGER_POLICIES)}"
                f", got {doc['trigger-policy']!r}.")

    goals = doc.get("goals")
    if "goals" in doc:
        if not isinstance(goals, list) or not goals or not all(
                isinstance(g, str) and g.strip() for g in goals):
            res.add("declaration_malformed",
                    "`goals` must be a non-empty list of non-empty strings — "
                    "an item advancing none of them is a retire-lane drop "
                    "candidate, which needs a list to be measured against.")
            goals = []
        elif len(set(goals)) != len(goals):
            res.add("declaration_malformed", "`goals` contains duplicates.")
    goals = goals if isinstance(goals, list) else []

    # THE PREDICATE WIDENS TO MATCH THE MESSAGE, not the other way round
    # (desk ruling, 2026-08-26). The message has always said the value may be
    # "an object carrying `lead-goal` … or the string \"none\"", and the code
    # accepted only the object — an assurance wider than its predicate, inside
    # the validator whose whole job is predicates. The message was the design's
    # intent: a repo with no lead goal says so in one word, and forcing
    # `{"lead-goal": "none"}` on it is a required object wrapping a required
    # absence.
    hr = doc.get("head-rule")
    if "head-rule" in doc:
        lead = head_lead_goal(hr)
        if lead is None:
            res.add("declaration_malformed",
                    "`head-rule` must be an object carrying `lead-goal` — "
                    "the goal whose items lead the head whenever one is "
                    "complete — or the bare string \"none\".")
        elif lead != "none" and lead not in goals:
            res.add("dangling_reference",
                    f"`head-rule.lead-goal` names {lead!r}, which "
                    "is not one of the declared goals. A head rule keyed to "
                    "a goal no item can carry never picks anything, and the "
                    "board renders as if it had.")

    ls = doc.get("leak-scan")
    if "leak-scan" in doc:
        _validate_leak_scan(ls, res)

    # OPTIONAL, never required (see DELEGATION_VALUES above): `kind check`
    # accepts a declaration that carries no `delegation` key at all — that
    # is the absent-means-"none" default, not a finding — and accepts a
    # present one only from the closed vocabulary. This is the ONLY place
    # this key is validated; a stray copy elsewhere would be the two-readers
    # split this design refuses everywhere else.
    # OPTIONAL, never required (see CLOSURE_WORDS_KEY above): a repo that
    # declares none migrates exactly as it does today. Validated HERE and
    # nowhere else, for the reason the `delegation` comment below gives.
    if CLOSURE_WORDS_KEY in doc:
        _validate_closure_words(doc[CLOSURE_WORDS_KEY], res)

    if "delegation" in doc and doc["delegation"] not in DELEGATION_VALUES:
        res.add("declaration_malformed",
                f"`delegation` must be one of {', '.join(DELEGATION_VALUES)}"
                f", got {doc['delegation']!r}. Optional (absent means "
                "\"none\" — no active delegation); the wave-3 Stop-hook "
                "detector is what reads it.")

    lanes = doc.get("lanes")
    #: Whether `lanes` is a list this build may READ — not whether the key is
    #: present. A malformed `lanes` is normalised to `[]` below so the rest of
    #: validation has something to walk, and an undeclared-lane scan run
    #: against that substitute would report every body in the tree as
    #: undeclared: one defect reported twice, the second time as a pile of
    #: findings the repo cannot act on.
    lanes_readable = "lanes" in doc
    if "lanes" in doc:
        if not isinstance(lanes, list) or not all(
                isinstance(x, str) and x.strip() for x in lanes):
            res.add("declaration_malformed",
                    "`lanes` must be a list of lane names (possibly empty).")
            lanes = []
            lanes_readable = False
            doc = {**doc, "lanes": []}
    world = ref_world(doc)

    if "template-bindings" in doc:
        if not isinstance(doc["template-bindings"], dict):
            res.add("declaration_malformed",
                    "`template-bindings` must be an object (possibly "
                    "empty).")
        else:
            _validate_template_bindings(doc["template-bindings"], res)

    kinds = doc.get("kinds")
    if "kinds" in doc:
        if not isinstance(kinds, dict) or not kinds:
            res.add("declaration_malformed",
                    "`kinds` must be a non-empty object. A repo that "
                    "persists nothing needs no declaration; a repo that "
                    "persists something registers it.")
        else:
            for name, body in kinds.items():
                _validate_kind(name, body, res, world)

    if repo is not None:
        check_records_kind_declared(repo, doc, res)
        check_desk_state_kind_declared(repo, doc, res)
    if repo is not None and isinstance(doc.get("laws"), str) and doc["laws"].strip():
        check_laws_present(repo, doc["laws"], res)
    if repo is not None:
        check_schema_agreement(repo, doc, res)
    if repo is not None and lanes_readable:
        check_lanes_registered(repo, lanes, res)
    if repo is not None:
        check_hook_modes(repo, res)


def head_lead_goal(hr):
    """The lead goal a `head-rule` names, or None if the value is neither form.

    TWO ACCEPTED FORMS, one meaning: the object `{"lead-goal": "<goal>"}` and
    the bare string `"none"`. Read in ONE place so `item ready --head` and the
    validator cannot disagree about what a head rule says — two readers of one
    key is the split this design refuses everywhere else.
    """
    if isinstance(hr, str):
        return hr.strip() if hr.strip() == "none" else None
    if isinstance(hr, dict) and isinstance(hr.get("lead-goal"), str):
        return hr["lead-goal"].strip() or None
    return None


def closure_words(doc) -> dict:
    """The repo's declared closure word -> grade map, or `{}` where none.

    READ IN ONE PLACE, like `head_lead_goal` above: two readers of one key is
    the split this design refuses everywhere else.

    A MALFORMED VALUE READS AS EMPTY here rather than half-applied. `validate`
    has already reported it as a finding — but a finding does NOT stop the
    verb (`cli._context` proceeds on any declaration it could parse), so this
    is the last reader before the carrier is written, and migrating under half
    a vocabulary nobody declared is the one outcome worse than migrating under
    none.
    """
    cw = (doc or {}).get(CLOSURE_WORDS_KEY)
    if not isinstance(cw, dict):
        return {}
    return {w: g for w, g in cw.items() if isinstance(g, str)}


def effective_goals(doc) -> list:
    """The goal vocabulary an ITEM may carry: the declared set ∪ {`tend`}.

    §3.1b, the plugin-reserved meta-goal. `goals` is a per-repo DOMAIN
    vocabulary — every declared goal names a stage of the work the repo
    EXISTS to do — which leaves a repo's work on ITSELF (its carrier, its
    method file, its hooks, the migration's own residue) advancing no goal
    and therefore unbookable. It fell out of the carrier into design prose,
    where nothing surfaces it: THIS design's own dev-loop decomposition sat
    fully specified and never booked until an operator asked, weeks late.
    The gap is structural — the carrier had no slot for the work, so care
    could not put it there.

    RESERVED, NOT DECLARABLE: `tend` is added here, by the plugin, for every
    repo — new, migrated, or one whose declaration predates the value. So a
    repo never declares it (`init` writes it into no `goals` list) and a repo
    can never fail to have it.

    THE HEAD RULE DOES NOT READ THIS. `head-rule.lead-goal` validates against
    the DECLARED set, because §3.1b puts `tend` outside the head's ordering:
    meta-work is visible and schedulable but never takes the scheduled head
    from domain work. Widening this one call site to the validator above
    would be invisible in every acceptance test and would quietly let a repo
    key its head to a goal the design says never leads.
    """
    goals = doc.get("goals") if isinstance(doc, dict) else None
    goals = [g for g in goals if isinstance(g, str)] if isinstance(
        goals, list) else []
    # A union, not an append: `tend` is undeclarable but a hand edit or a
    # merge can still put it in the list, and a doubled entry would render
    # twice in every message that prints the vocabulary.
    return goals + ([RESERVED_GOAL] if RESERVED_GOAL not in goals else [])


def _validate_closure_words(cw, res: Result) -> None:
    """`closure-words` (lc-91) — see the constant above for the key itself.

    FOUR REFUSALS, and every one of them is the same shape: the declaration
    states a rule this tool would silently not apply. A key that sits in the
    file doing nothing is worse than an absent one, because it reads as live
    to the next person who looks — and the migration it was supposed to fix
    reports UNCLASSIFIED exactly as it did before, with the file apparently
    saying otherwise.

    THE TWO FACTS ARE FETCHED, NEVER RESTATED. The closed grades live in
    `items` and the grade-word SHAPE lives in `migrate`; both import THIS
    module at their top, so both are imported inside the function — the same
    cycle break `check_lanes_registered` uses below. A copy of either here
    would be a second body that goes stale the day its original is tightened,
    and the stale copy would accept a word nothing can ever match.
    """
    from . import items as items_mod
    from . import migrate as migrate_mod

    if not isinstance(cw, dict):
        res.add("declaration_malformed",
                f"`{CLOSURE_WORDS_KEY}` must be an object mapping this repo's "
                f"own closure word to one of "
                f"{', '.join(items_mod.GRADES_CLOSED)} — "
                f'e.g. {{"ERLEDIGT": "DONE"}}. Got {type(cw).__name__}.')
        return
    for word, grade in sorted(cw.items()):
        if not isinstance(grade, str) or grade not in items_mod.GRADES_CLOSED:
            res.add("declaration_malformed",
                    f"`{CLOSURE_WORDS_KEY}` maps {word!r} to {grade!r}, which "
                    f"is not one of the closed grades "
                    f"({', '.join(items_mod.GRADES_CLOSED)}). The map "
                    "TRANSLATES a word onto the closed vocabulary; it does "
                    "not widen it, and a grade outside that pair would be "
                    "written into the successor carrier as a word no verb "
                    "understands.")
            continue
        if not migrate_mod.grade_word_shaped(word):
            res.add("declaration_malformed",
                    f"`{CLOSURE_WORDS_KEY}` declares {word!r}, which a "
                    "carrier's own shape can never yield: a grade word is "
                    "UPPERCASE, at least two characters, and made of A-Z, "
                    "0-9 and `-`. Matching is case-sensitive, so this entry "
                    "could not fire on any carrier — and a rule that cannot "
                    "fire reads exactly like one that never had to.")
            continue
        if word in migrate_mod.RULES:
            res.add("declaration_malformed",
                    f"`{CLOSURE_WORDS_KEY}` declares {word!r}, which this "
                    "tool already rules on (`migrate.RULES`, from §4 row 1 "
                    "and §3.1). The declaration may name a word the tool does "
                    "not know; it may not redefine one it does — a repo and "
                    "the tool disagreeing about one word is a vocabulary with "
                    "two bodies, and the run would apply whichever the lookup "
                    "order happened to reach.")


def _validate_leak_scan(ls, res: Result) -> None:
    """§3.3's source-scope foreign-path class, declared PER REPO.

    The class is right for one repo and blind in another — corpus-only fits a
    repo whose own prose names this machine's home, and misses everything in a
    repo whose payload is `.md`. So the enabling decision is the REPO's and it
    is written down, with its reason, rather than inferred by the scanner from
    the directory it happens to be standing in.

    OFF WITHOUT A REASON IS THE ONE STATE REFUSED. `true` needs no defence;
    `false` is a decision to run a public tree without that class, and a
    decision nobody wrote down is indistinguishable from nobody having thought
    about it.
    """
    if not isinstance(ls, dict):
        res.add("declaration_malformed",
                f"`leak-scan` must be an object carrying "
                f"`source-scope-foreign-path` and, where that is false or "
                f"allowlisted, a `reason`. Got {type(ls).__name__}.")
        return
    unknown = [k for k in ls if k not in
               ("source-scope-foreign-path", "reason", "allowlist")]
    if unknown:
        res.add("declaration_malformed",
                "`leak-scan` declares unknown key(s): "
                + ", ".join(sorted(unknown))
                + ". The keys are source-scope-foreign-path, reason, "
                  "allowlist.")
    on = ls.get("source-scope-foreign-path")
    if not isinstance(on, bool):
        res.add("declaration_malformed",
                "`leak-scan.source-scope-foreign-path` must be true or false, "
                f"got {on!r}. There is no third value: a class nobody decided "
                "about is a class nobody runs.")
        return
    allowlist = ls.get("allowlist", [])
    if not isinstance(allowlist, list) or not all(
            isinstance(x, str) and x.strip() for x in allowlist):
        res.add("declaration_malformed",
                "`leak-scan.allowlist` must be a list of non-empty path "
                "prefixes (possibly absent).")
        allowlist = []
    reason = ls.get("reason")
    needs_reason = (not on) or bool(allowlist)
    if needs_reason and (not isinstance(reason, str) or len(reason.strip()) < 8):
        res.add("leak_scan_undeclared_reason",
                "`leak-scan` turns the source-scope foreign-path class OFF "
                "(or narrows it with an allowlist) and states no `reason`. "
                "Turning a leak class off in a public tree is a decision; a "
                "decision nobody wrote down cannot be reviewed, and it reads "
                "afterwards exactly like nobody having considered it.")


def _validate_template_bindings(tb: dict, res: Result) -> None:
    """§3.8b/§3.11: every `template-bindings` entry's slots, and its named
    template's existence AND PARSEABILITY, checked against the PLUGIN
    REGISTRY itself — `workflows.read_template()`'s own directory-and-
    parser, imported locally to avoid the module cycle (`workflows.py`
    imports this module at load time; this import is deferred to call
    time, the same pattern `validate()` already uses for `judgment`
    above). ONE PARSER, ONE CALLER OF ITS SLOT LOGIC — this function never
    re-derives a template's required-slot set by any means other than
    `read_template()`, the same function `workflow bind` calls.

    CORRECTED 2026-08-26 (the judgment desk's own defect, not the
    executor's): the first cut compared each binding's VALUES against
    "UNKNOWN" and separately asked only whether the template FILE exists
    — never whether the binding's KEYS match the template's declared
    slots. That is the restated-comparison-basis drift this lane's central
    decision (no index; derive the slot set from the file on every read)
    exists to prevent, one level down: a template gains a slot, and every
    binding written before it does not carry that key at all — no UNKNOWN
    value to find, so the old check read clean over an incomplete binding.
    So an ABSENT required key is now the SAME finding as a PRESENT-UNKNOWN
    one: both are "a required slot nobody has answered", one with no value
    to see and one with an explicit marker. And a template that EXISTS but
    whose `Slots:` header does not parse gets its own finding
    (`binding_template_unparsable`) rather than silently passing the
    file-exists check the way it did before.

    NOTHING DANGLES, IN EITHER DIRECTION (§3.8b's own line): a lane naming
    a missing workflow already fails `kind check`, and now so does a
    binding naming a missing template — checked against the SAME registry
    `workflow bind` reads, never a second, restated list of what exists.

    OUT OF SCOPE, DELIBERATELY: a binding carrying a key the template does
    NOT declare. The design requires only that every required slot is
    filled; the stale-key direction is a real, unspecced question left
    for its own decision rather than folded in here.
    """
    from . import workflows as workflows_mod

    for template_id, binding in tb.items():
        if not isinstance(binding, dict):
            res.add("declaration_malformed",
                    f"`template-bindings` entry {template_id!r} must be "
                    f"an object mapping slot name to value, got "
                    f"{type(binding).__name__}.")
            continue

        present_unknown = sorted(
            slot for slot, value in binding.items()
            if isinstance(value, str) and value.strip().upper() == "UNKNOWN")

        tmpl = workflows_mod.read_template(template_id)
        missing_keys: list = []

        if tmpl.path is None:
            template_path = workflows_mod.registry_dir() / f"{template_id}.md"
            res.add("binding_template_missing",
                    f"`template-bindings` names template {template_id!r}, "
                    f"which has no file at {template_path}. Nothing "
                    "dangles, in either direction: a lane naming a "
                    "missing workflow already fails `kind check`, and now "
                    "so does a binding naming a missing template.")
        elif tmpl.problem:
            res.add("binding_template_unparsable",
                    f"`template-bindings` names template {template_id!r}, "
                    f"whose file exists but does not parse: {tmpl.problem} "
                    "A template that cannot be read has no required-slot "
                    "set to bind against, exactly as `workflow bind` "
                    "itself refuses to proceed against it.")
        else:
            missing_keys = sorted(s for s in tmpl.slots if s not in binding)

        if present_unknown or missing_keys:
            parts = []
            if present_unknown:
                parts.append("holds UNKNOWN in "
                             + ", ".join(f"`{s}`" for s in present_unknown))
            if missing_keys:
                parts.append("is missing required slot(s) "
                             + ", ".join(f"`{s}`" for s in missing_keys))
            res.add("binding_slot_unbound",
                    f"`template-bindings` entry {template_id!r} "
                    + " and ".join(parts)
                    + ". An unanswered required slot is the same defect "
                      "whether it carries UNKNOWN (the same transitional "
                      "marker `items.py` uses for a slot nobody has ever "
                      "recorded) or is absent from the binding entirely — "
                      "a template gaining a slot after a binding was "
                      "written leaves exactly this second shape, with no "
                      "value to see. `workflow bind --set` fills either.")


#: The investigation record's home, as the format file fixes it. Matched as a
#: SUBSTRING of a declared `home`, because a repo may legitimately spell the
#: XDG root as `$XDG_STATE_HOME`, `${XDG_STATE_HOME}` or an expanded path —
#: what identifies the kind is the directory the records actually live in.
RECORDS_HOME_MARK = "claude/investigations"

#: THE XDG HOMES THIS PLUGIN ITSELF WRITES, each with the row that fires when
#: its files exist and no kind names them (lc-171, generalising lc-166).
#:
#: WHY A TABLE AND NOT A SECOND COPY OF THE CHECK. lc-166 built this for the
#: investigation record and the next instance arrived one directory over
#: within a day — desk state, written by a shipped verb and governed by no
#: kind. A second hand-written check would have been a second implementation
#: of a concept this file already had, and a third home would have needed a
#: third. The population is CLOSED and knowable: it is the set of XDG homes
#: the plugin's own modules write, so it is listed here beside the check that
#: consumes it rather than rediscovered per home.
#:
#: SEPARATE ROWS, NOT ONE. The two refusals name different kinds with
#: different stage answers — a record's exit is `never` because closure is
#: graduation of its CONTENT, while desk state is overwritten in place and
#: keeps no history — so an operator told only "an XDG kind is undeclared"
#: would get the same sentence for two different declarations to write.
#: `records_kind_undeclared` also keeps its own proof this way, which a
#: rename would have retired.
TOOL_STATE_HOMES = (
    ("records_kind_undeclared", RECORDS_HOME_MARK, "investigation record"),
    ("desk_state_kind_undeclared", "lifecycle/desk-state", "desk state"),
)


def check_records_kind_declared(repo, doc, res: Result) -> None:
    """A repo whose investigation records EXIST must register the kind.

    INVARIANT 1 REACHES OUT OF THE TREE HERE, which is the whole reason this
    check exists rather than the sweep. `kind sweep` walks TRACKED files, and
    the investigation record is deliberately outside every repo — XDG state,
    so no repo is dirtied and no permission dialog fires from the
    config-directory protection. That design is right and it has a
    consequence nobody had drawn: the sweep structurally CANNOT see these
    files, so the one carrier that grades them (`lifecycle record check`,
    shipped 2026-09-18) was grading a kind no declaration governed. One
    carrier ends and none picks up.

    SILENT WHERE THERE IS NOTHING TO GOVERN. A repo with no records of its
    own needs no kind, so the absence of both is clean — this fires only
    where the files are actually there, which is what keeps it off every
    repo that never opened an investigation.
    """
    from . import records as records_mod

    prefix = Path(repo).resolve().name
    try:
        found = sorted(records_mod.records_dir().glob(f"{prefix}--*.md"))
    except OSError:
        return
    if not found:
        return

    kinds = doc.get("kinds")
    if isinstance(kinds, dict):
        for body in kinds.values():
            home = isinstance(body, dict) and body.get("home")
            if isinstance(home, str) and RECORDS_HOME_MARK in home:
                return

    res.add("records_kind_undeclared",
            f"{len(found)} investigation record(s) exist for this repo "
            f"({', '.join(p.name for p in found[:3])}"
            + (", …" if len(found) > 3 else "")
            + ") and no registered kind names their home. They sit OUTSIDE "
              "the tree by design, so `kind sweep` cannot reach them — it "
              "walks tracked files — and their absence from the declaration "
              "is therefore invisible to every other check. Register the "
              "kind with all seven stages; the home is a pattern under "
              f"`{RECORDS_HOME_MARK}`, the files are never moved into any "
              "tree, and `the fire log` is the precedent for an XDG home "
              "declared as a per-repo kind.")


def _home_is_declared(doc, mark: str) -> bool:
    """Does any registered kind name a home under `mark`?"""
    kinds = doc.get("kinds")
    if not isinstance(kinds, dict):
        return False
    for body in kinds.values():
        home = isinstance(body, dict) and body.get("home")
        if isinstance(home, str) and mark in home:
            return True
    return False


DESK_STATE_HOME_MARK = "lifecycle/desk-state"


def check_desk_state_kind_declared(repo, doc, res: Result) -> None:
    """Desk state written BY THIS REPO exists and no kind names it (lc-182).

    THIS CHECK WAS WITHDRAWN ONCE, and the withdrawal is why it is spelled
    this way. lc-171's first cut mirrored the records check and asked only
    whether desk-state files EXIST — and desk state is machine-wide, so it
    demanded that every repo declare the kind because some other repo's
    session had written a file. Measured: the roster went from CLEAN to 22
    rows COULD NOT VERIFY in one run, every one of them a declaration row
    running `kind check` over a scratch repo. That is law 11's guard firing
    on legitimate work, and the repair was not a softer predicate but a
    SCOPE the kind did not yet have.

    SO THE WRITER RECORDS THE REPO (`desk.cmd_desk_state`), on the fire log's
    own idiom, and this reads only files that name THIS one. Records are
    scoped by the repo name in their filename and that is why the same shape
    transferred there and not here — a desk-state file is keyed by session id
    and carried no repo at all.

    A FILE WITHOUT THE KEY BELONGS TO NOBODY, deliberately: state written
    before lc-182 cannot be attributed, and attributing it by guess would
    re-create the over-fire one layer in. Such files age out as each desk
    overwrites its own.
    """
    from . import desk as desk_mod

    try:
        files = sorted(desk_mod.state_dir().glob("*.json"))
    except OSError:
        return
    here = str(Path(repo).resolve())
    mine = []
    for f in files:
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(rec, dict) and rec.get("repo") == here:
            mine.append(f)
    if not mine or _home_is_declared(doc, DESK_STATE_HOME_MARK):
        return

    res.add("desk_state_kind_undeclared",
            f"{len(mine)} desk-state file(s) written IN THIS REPO exist and "
            "no registered kind names their home. `lifecycle desk state` "
            "writes them, so this is the plugin governing its own state "
            "everywhere except the file it writes about the desk. They sit "
            "OUTSIDE the tree by design — an XDG home costs no permission "
            "dialog and dirties no repo — so `kind sweep` cannot reach them: "
            "it walks tracked files. Register the kind with all seven stages. "
            "Its answers are not the investigation record's: the verb ALWAYS "
            "OVERWRITES and keeps no history, so staleness is "
            "current-by-construction and the exit is not a compaction. `the "
            "fire log` and `investigation records` are both precedents for an "
            "XDG home declared as a per-repo kind.")


def _verb_exists(spelled: str) -> bool:
    """Is `spelled` a real command path, per the PARSER?

    DERIVED, NEVER RESTATED (law 24's worked example, and lc-204's rule one
    stage over). A hardcoded verb list beside the parser it mirrors cannot age
    loudly: the parser gains a subcommand, the list stays green, and the two
    part company with no symptom. So this walks the live parser's subactions —
    the same source `--test` derives its surface size from.

    The import is deferred because `cli` imports this module; the same lazy
    form `refusals.py` already uses for its own CLI drives. A parser that
    cannot be built at all answers TRUE rather than false: this predicate
    exists to catch a MISSPELLED verb, and a broken parser is a different and
    much louder failure that every other verb would report first — answering
    false there would turn one defect into a finding on every declared kind.
    """
    import argparse
    try:
        from . import cli as cli_mod
        parser = cli_mod.build_parser()
    except Exception:
        return True

    want = tuple(spelled.split())

    def paths(p, prefix=()):
        found = {prefix} if prefix else set()
        for action in getattr(p, "_actions", ()):
            if isinstance(action, argparse._SubParsersAction):
                for verb, sub in action.choices.items():
                    found |= paths(sub, prefix + (verb,))
        return found

    return want in paths(parser)


def _validate_kind(name: str, body, res: Result, world) -> None:
    if not isinstance(body, dict):
        res.add("kind_stage_undeclared",
                f"kind {name!r} is {type(body).__name__}, not an object, so "
                f"all {len(KIND_STAGES)} stages "
                f"({', '.join(KIND_STAGES)}) are undeclared.")
        return

    absent = [s for s in KIND_STAGES if s not in body]
    if absent:
        res.add("kind_stage_undeclared",
                f"kind {name!r} leaves stage(s) undeclared: "
                + ", ".join(absent)
                + ". A kind with an undeclared stage is a checker finding — "
                "the stage list is closed and no member is optional.")

    unknown = [k for k in body if k not in KIND_STAGES]
    if unknown:
        res.add("declaration_malformed",
                f"kind {name!r} declares unknown stage(s): "
                + ", ".join(sorted(unknown))
                + f". The stages are exactly {', '.join(KIND_STAGES)}.")

    home = body.get("home")
    if "home" in body and (not isinstance(home, str) or not home.strip()):
        res.add("declaration_malformed",
                f"kind {name!r}: `home` must be a non-empty path or pattern.")

    writer = body.get("writer")
    if "writer" in body:
        if not isinstance(writer, str) or not writer.strip():
            res.add("declaration_malformed",
                    f"kind {name!r}: `writer` must be a non-empty string.")

    reader = body.get("reader")
    if "reader" in body:
        if not isinstance(reader, list) or not reader:
            res.add("declaration_malformed",
                    f"kind {name!r}: `reader` must be a non-empty list of "
                    "non-empty strings, or objects carrying `reader` and "
                    "`when`. A kind nothing reads is the registry's own "
                    "recorded defect — it accumulates forever and no gate "
                    "ever looks at it.")
        else:
            # lc-224: A `reader` ENTRY IS EITHER TODAY'S BARE STRING
            # (unchanged) OR AN OBJECT carrying `reader` (the same typed
            # token) and `when` (§ READER_WHEN_MODES). `typed` collects the
            # plain typed-reference strings either shape reduces to, so an
            # all-bare-string declaration feeds `_check_typed_refs` the
            # IDENTICAL list it always did — byte-identical findings for
            # every declaration written before this change.
            typed = []
            for entry in reader:
                if isinstance(entry, str):
                    if not entry.strip():
                        res.add("declaration_malformed",
                                f"kind {name!r}: `reader` must be a "
                                "non-empty list of non-empty strings, or "
                                "objects carrying `reader` and `when`. A "
                                "kind nothing reads is the registry's own "
                                "recorded defect — it accumulates forever "
                                "and no gate ever looks at it.")
                        continue
                    typed.append(entry)
                elif isinstance(entry, dict):
                    ref = entry.get("reader")
                    if not isinstance(ref, str) or not ref.strip():
                        res.add("declaration_malformed",
                                f"kind {name!r}: a `reader` object must "
                                "carry a non-empty `reader` key — the same "
                                "typed token a bare entry carries.")
                        continue
                    typed.append(ref)
                    if "when" in entry:
                        _check_reader_when(name, ref, entry["when"], res)
                else:
                    res.add("declaration_malformed",
                            f"kind {name!r}: `reader` must be a non-empty "
                            "list of non-empty strings, or objects carrying "
                            "`reader` and `when`. A kind nothing reads is "
                            "the registry's own recorded defect — it "
                            "accumulates forever and no gate ever looks at "
                            "it.")
            if typed:
                _check_typed_refs(name, "reader", typed, res, world)

    if isinstance(writer, str) and writer.strip():
        _check_typed_refs(name, "writer", [writer], res, world)

    stale = body.get("staleness")
    if "staleness" in body:
        if not isinstance(stale, str) or not stale.strip():
            res.add("declaration_malformed",
                    f"kind {name!r}: `staleness` must be a predicate or "
                    "\"none, declared why: …\".")
        elif stale.strip().lower().startswith("none") and _needs_why(stale.strip(), "none"):
            res.add("kind_stage_undeclared",
                    f"kind {name!r}: `staleness` says \"none\" with no "
                    "declared why. The bare word is the undeclared stage "
                    "this registry exists to make visible.")

    ex = body.get("exit")
    if "exit" in body:
        if not isinstance(ex, dict):
            res.add("kind_stage_undeclared",
                    f"kind {name!r}: `exit` must be an object carrying "
                    "`action` and `recording-act`.")
        else:
            act = ex.get("action")
            if act not in EXIT_ACTIONS:
                res.add("declaration_malformed",
                        f"kind {name!r}: `exit.action` must be one of "
                        f"{', '.join(EXIT_ACTIONS)}, got {act!r}.")
            rec = ex.get("recording-act")
            if not isinstance(rec, str) or not rec.strip():
                res.add("kind_stage_undeclared",
                        f"kind {name!r}: `exit` declares no `recording-act`. "
                        "An exit nobody records is a deletion that leaves no "
                        "trace, which is the loss this carrier exists to "
                        "prevent.")

    trigger = body.get("trigger")
    if "trigger" in body:
        if not isinstance(trigger, str) or not trigger.strip():
            res.add("declaration_malformed",
                    f"kind {name!r}: `trigger` must BEGIN with one of "
                    f"{', '.join(TRIGGER_MODES)}.")
        else:
            spelled = trigger.strip()
            mode = spelled.split()[0].strip(":,—-").lower()
            rest = spelled[len(spelled.split()[0]):].strip(" :,—-")
            # THE VALUE IS `<mode> <value> — <reason>`, which is the shape
            # `growth` already uses ("bounded-by-exit — every item leaves…").
            # Splitting on the em dash is what separates the verb NAME from
            # the sentence explaining it: without this the existence check
            # received the whole reason as a command path and refused every
            # verb that carried one.
            rest = rest.split("—")[0].strip(" :,-")
            if mode not in TRIGGER_MODES:
                res.add("declaration_malformed",
                        f"kind {name!r}: `trigger` must BEGIN with one of "
                        f"{', '.join(TRIGGER_MODES)}, got {trigger!r}. The "
                        "vocabulary is closed: a write is occasioned by an ACT "
                        "that carries it or by a CONDITION somebody "
                        "evaluates, and a cadence is neither — this system "
                        "owns no clock, so the tick is the verb.")
            elif mode == "none":
                if _needs_why(spelled, "none"):
                    res.add("kind_stage_undeclared",
                            f"kind {name!r}: `trigger` says \"none\" and "
                            "states no reason. The word carries the "
                            "obligation — spelled `none, declared why: "
                            "<reason>`, the same shape `staleness` and "
                            "`growth` already use. A bare \"none\" is the "
                            "undeclared stage wearing a plausible face, "
                            "which is what this stage exists to stop.")
            elif not rest:
                res.add("kind_stage_undeclared",
                        f"kind {name!r}: `trigger` says {mode!r} and names "
                        f"nothing. The word carries the obligation: "
                        f"{'a verb with no name fires on nothing' if mode == 'verb' else 'a predicate with no command has no state, and no state is not quiet'}.")
            elif mode == "verb" and not _verb_exists(rest):
                res.add("trigger_verb_unknown",
                        f"kind {name!r}: `trigger` names the verb {rest!r}, "
                        f"which this build does not have. Checked against the "
                        f"PARSER, not a list restated here, so this cannot go "
                        f"stale silently as the verb set moves. A trigger "
                        f"naming a verb that does not exist is a kind nothing "
                        f"will ever fire — the WHEN is declared and "
                        f"unreachable, which reads exactly like a kind that "
                        f"is simply quiet.")

    growth = body.get("growth")
    if "growth" in body:
        if not isinstance(growth, str) or not growth.strip():
            res.add("declaration_malformed",
                    f"kind {name!r}: `growth` must be one of "
                    f"{', '.join(GROWTH_MODES)}.")
        else:
            mode = growth.strip().split()[0].strip(":,—-").lower()
            # THE ARM, REGISTERED ON CONTACT (D-3). Some kinds are a SINGLE
            # FIXED FILE: they do not accrue, are never compacted, and have
            # no exit, so every one of the three members would be a
            # NEIGHBOUR standing in for a state this vocabulary cannot say —
            # which is the failure the contract exists to end, and the
            # neighbour is always the benign one. Recording the arm with its
            # reason keeps the honest answer in the declaration and makes it
            # the widening signal, instead of a kind quietly claiming a
            # growth control it does not have.
            #
            # A MALFORMED ARM IS STILL REFUSED, and by the same predicate the
            # grade door uses: undated, the instance could never be aged, so
            # the signal it exists to be could never reach zero owed.
            from . import vocab as vocab_mod
            if vocab_mod.is_oov(growth.strip()):
                pass
            elif mode not in GROWTH_MODES:
                res.add("declaration_malformed",
                        f"kind {name!r}: `growth` must BEGIN with one of "
                        f"{', '.join(GROWTH_MODES)}, got {growth!r} — or be "
                        f"the out-of-vocabulary arm, `{vocab_mod.OOV_FORM}`, "
                        "where no member is true of this kind. The "
                        "vocabulary is closed (R22): a count or a size is not "
                        "a growth control, it is a cap, and the alarm this "
                        "design reads is FLOW.")
            elif mode == "unbounded-with-reason" and _needs_why(
                    growth.strip(), "unbounded-with-reason"):
                res.add("kind_stage_undeclared",
                        f"kind {name!r}: `growth` says "
                        "\"unbounded-with-reason\" and states no reason. The "
                        "word carries the obligation; without the reason it "
                        "is the undeclared stage with a plausible face on it.")


# --- typed references (§3.8c) ------------------------------------------------

@dataclass(frozen=True)
class RefWorld:
    """What each typed-reference kind resolves AGAINST, gathered once.

    ONE PLACE, because the six types resolve against six different worlds and
    a resolver assembled per call site would resolve some of them and quietly
    skip the rest — which is the state this whole row exists to end: before
    this wave `dangling_reference` reached `lane:` alone while its own text
    said "typed reference", an assurance wider than its predicate.
    """
    lanes: frozenset = frozenset()
    verbs: frozenset = frozenset()
    hooks: frozenset = frozenset()
    producers: frozenset = frozenset()


def cli_verbs() -> frozenset:
    """Every `<verb> <action>` this build carries — DERIVED from the parser.

    Never a list: a list beside the parser it mirrors is a coverage assertion
    restated from its source, and it stays green the day a verb is added. The
    parser is walked, so a `verb:` reference to something this build does not
    have goes red without anyone updating anything here.
    """
    import argparse as _ap
    from . import cli as cli_mod
    out = set()
    parser = cli_mod.build_parser()
    for action in parser._actions:
        if not isinstance(action, _ap._SubParsersAction):
            continue
        for verb, sub in action.choices.items():
            out.add(verb)
            for sub_action in sub._actions:
                if not isinstance(sub_action, _ap._SubParsersAction):
                    continue
                for name in sub_action.choices:
                    out.add(f"{verb} {name}")
    out.add("--test")
    return frozenset(out)


#: Where the plugin declares the GIT hooks it ships. NOT `hooks`: measured on
#: this machine, `hooks` in a `plugin.json` is Claude Code's own harness hook
#: map (`PreToolUse` and friends — ai-bureau's manifest is the live example),
#: so a git hook declared there would break the plugin at install time. The
#: two are different things and they get different keys.
PLUGIN_GIT_HOOKS_KEY = "git-hooks"


def plugin_root() -> Path:
    """The plugin tree this build is running from.

    ONE body for a fact two readers need: the manifest lives under it, and
    the manifest's `script` values are relative to it. A second copy of this
    expression beside the first would be the restated set this repo's own law
    refuses — it stays right until the layout moves, and then one reader
    follows and the other does not.
    """
    return Path(__file__).resolve().parents[2]


def plugin_manifest() -> dict:
    """The plugin's own `plugin.json` as a dict, `{}` where it cannot be read.

    Unreadable yields an EMPTY manifest here rather than a raise, and every
    caller must therefore decide for itself what an empty one means: for
    `plugin_hooks` it is "no declared hook", for `check_hook_modes` it is a
    population that contributes no member. Neither is a clean board over a
    manifest this build could not open, because neither claims anything about
    what the manifest does not say.
    """
    manifest = plugin_root() / ".claude-plugin" / "plugin.json"
    try:
        doc = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return doc if isinstance(doc, dict) else {}


def plugin_hooks() -> frozenset:
    """Every git hook the plugin DECLARES in `plugin.json` (§3.8c, the seam).

    Read from the plugin's own manifest rather than from the machine: a hook
    that exists on this disk and is declared nowhere is the registration
    nobody can find, and a hook declared and absent is the one that silently
    never fires. The manifest is the declaration; the dispatcher registration
    is the wiring, and they are different failures.
    """
    hooks = plugin_manifest().get(PLUGIN_GIT_HOOKS_KEY)
    if isinstance(hooks, dict):
        return frozenset(hooks)
    return frozenset()


def ref_world(doc: dict) -> RefWorld:
    lanes = doc.get("lanes")
    kinds = doc.get("kinds")
    producers = set()
    if isinstance(kinds, dict):
        for body in kinds.values():
            if not isinstance(body, dict):
                continue
            w = body.get("writer")
            for kind_, name_ in parse_refs([w] if isinstance(w, str) else []):
                if kind_ == "producer" and name_:
                    producers.add(name_)
    return RefWorld(
        lanes=frozenset(lanes) if isinstance(lanes, list) else frozenset(),
        verbs=cli_verbs(),
        hooks=plugin_hooks(),
        producers=frozenset(producers),
    )


def parse_refs(values):
    """`[(type, name)]` for every comma-separated entry in `values`.

    A bare role yields `(role, "")`; an unrecognised entry yields
    `(None, entry)` — PROSE, which is a finding rather than something to be
    guessed at. The split is on commas only: a reference's own name may carry
    spaces, and splitting on whitespace would truncate it into a prefix match
    in an equality's costume.
    """
    out = []
    for v in values:
        for part in str(v).split(","):
            part = part.strip()
            if not part:
                continue
            low = part.lower()
            if low in REF_BARE:
                out.append((low, ""))
                continue
            head, colon, rest = part.partition(":")
            head = head.strip().lower()
            if colon and head in REF_PREFIXES:
                out.append((head, rest.strip()))
                continue
            out.append((None, part))
    return out


def _check_typed_refs(kind: str, stage: str, values, res: Result,
                      world: RefWorld) -> None:
    """Every `reader`/`writer` entry is TYPED, and every type RESOLVES.

    Referential integrity, from log4brains' build-time supersede-link check
    and Backstage's relation resolution. A declaration pointing at a lane
    that does not exist reads exactly like one pointing at a lane that does —
    and the same is true of a verb, a hook and a producer, which is why the
    predicate now covers all six types rather than the one it happened to
    start with.
    """
    for typ, name in parse_refs(values):
        if typ is None:
            res.add("reference_untyped",
                    f"kind {kind!r}: `{stage}` carries PROSE — {name!r}. The "
                    "types are closed (§3.8c): "
                    + ", ".join(f"{p}:<name>" for p in REF_PREFIXES)
                    + ", " + ", ".join(REF_BARE)
                    + ". Prose cannot be resolved, so a reader written as "
                      "prose is indistinguishable from a kind nothing reads — "
                      "which is the registry's own recorded defect.")
            continue
        if typ in REF_BARE:
            continue
        if not name:
            res.add("reference_untyped",
                    f"kind {kind!r}: `{stage}` names the type {typ!r} with no "
                    "target after the colon.")
            continue
        pool, what = {
            "lane": (world.lanes, "the declared `lanes` list"),
            "verb": (world.verbs, "this build's CLI verbs"),
            "hook": (world.hooks, "the hooks the plugin declares in "
                                  "plugin.json"),
            "producer": (world.producers, "the producers this declaration's "
                                          "kinds name as writers"),
        }[typ]
        if name not in pool:
            res.add("dangling_reference",
                    f"kind {kind!r}: `{stage}` names {typ}:{name!r}, which is "
                    f"not in {what}. Nothing dangles (invariant 4): a "
                    "reference that resolves to nothing renders exactly like "
                    "one that resolves.")


#: The partition's fourth state, used only inside it: a `when` that is
#: present, well-formed, and names a command to run. `read_moments` turns it
#: into FIRE / QUIET / BROKEN by running it; the checker never does.
WHEN_PREDICATE = "PREDICATE"


@dataclass(frozen=True)
class WhenClass:
    """ONE invalid-state partition over a reader entry's `when` (D-3, P2).

    TWO INSTRUMENTS, ONE BODY. `_check_reader_when` validates and
    `read_moments` evaluates, and each used to parse the value with its own
    copy of the same three lines. Two bodies behind one contract disagree,
    and these did — on a `predicate` naming nothing, on a non-string, on a
    `none` with no why, and on a PREFIXED reader carrying a `when`, which
    the checker refused while the evaluator had no guard and RAN it.

    PRESENCE IS ITS OWN ARGUMENT, and this is the repair N4 named. An
    ABSENT `when` is the legitimate default across every kind in this repo;
    folding absence into MALFORMED would fire on all of them at once, which
    is a guard firing on legitimate work (law 11). So `present` is passed in
    rather than inferred from the value, because `None` and "absent" are not
    the same fact and only the caller knows which it holds.

    `problem` carries the message WITHOUT its `kind` prefix, because the
    evaluator does not know the kind's name and the checker does — the one
    piece neither can share. `row` is the checker's refusal row, kept per
    case so this extraction changes no finding anyone already relies on.
    """
    state: str
    command: str = ""
    why: str = ""
    problem: str = ""
    row: str = ""


def classify_reader_when(ref: str, when, *, present: bool) -> WhenClass:
    """The partition. Both instruments read this and nothing else."""
    if not present:
        return WhenClass(READ_MOMENT_UNDECLARED)
    if not isinstance(when, str) or not when.strip():
        return WhenClass(
            READ_MOMENT_MALFORMED, row="declaration_malformed",
            problem=(f"reader {ref!r} carries a `when` that is not a "
                     "non-empty string."))
    if ref not in REF_BARE:
        return WhenClass(
            READ_MOMENT_MALFORMED, row="declaration_malformed",
            problem=(f"reader {ref!r} carries a `when`, but `when` is only "
                     "legal on a bare reader (" + ", ".join(REF_BARE)
                     + "). A prefixed reader's moment is the referenced act "
                     "firing — a `when` there is a second answer to a "
                     "settled question."))
    spelled = when.strip()
    mode = spelled.split()[0].strip(" :,—-").lower()
    rest = spelled[len(spelled.split()[0]):].strip(" :,—-")
    rest = rest.split("—")[0].strip(" :,-")
    if mode not in READER_WHEN_MODES:
        return WhenClass(
            READ_MOMENT_MALFORMED, row="declaration_malformed",
            problem=(f"reader {ref!r}'s `when` must BEGIN with one of "
                     f"{', '.join(READER_WHEN_MODES)}, got {when!r}. The "
                     "vocabulary is closed and narrower than a kind's own "
                     "`trigger`: `verb` is not a member here because a "
                     "verb-occasioned read is already expressible as "
                     "`verb:<name>` in the reader type itself."))
    if mode == "none":
        if _needs_why(spelled, "none"):
            return WhenClass(
                READ_MOMENT_MALFORMED, row="kind_stage_undeclared",
                problem=(f"reader {ref!r}'s `when` says \"none\" and states "
                         "no reason. The word carries the obligation — "
                         "spelled `none, declared why: <reason>`."))
        return WhenClass(READ_MOMENT_NONE, why=rest)
    if not rest:
        return WhenClass(
            READ_MOMENT_MALFORMED, row="kind_stage_undeclared",
            problem=(f"reader {ref!r}'s `when` says 'predicate' and names "
                     "nothing. A predicate with no command has no state, "
                     "and no state is not quiet."))
    return WhenClass(WHEN_PREDICATE, command=rest)


def _check_reader_when(kind: str, ref: str, when, res: Result) -> None:
    """Validate one reader entry's `when` — STRUCTURALLY ONLY.

    Never executes a predicate: the seventh stage does not either at
    validation time, and a `kind check` that ran shell would be a new side
    effect nobody asked for — execution is `read_moments`'s job alone.

    THE PARTITION IS NOT DECIDED HERE ANY MORE (P2). This maps the shared
    classifier's verdict onto this instrument's findings, so the two
    instruments cannot drift apart again by one of them being edited.
    """
    verdict = classify_reader_when(ref, when, present=True)
    if verdict.state == READ_MOMENT_MALFORMED:
        res.add(verdict.row, f"kind {kind!r}: {verdict.problem}")


#: `read_moments`'s per-entry answer. `state` is always one of FIRE / QUIET /
#: BROKEN (from `lanes.evaluate_trigger`, for a `predicate` WHEN) or NONE (a
#: declared `none, declared why: ...`) or UNDECLARED (no `when` at all and no
#: computable default — the residue) or DERIVED (no `when` at all, but the
#: ref shape supplies one — O6 §4 Part A). An absent moment and a quiet one
#: are different answers, so both are reported; only a `predicate` WHEN is
#: ever actually run.
@dataclass
class ReadMoment:
    reader: str
    state: str
    detail: str = ""


#: The three states `read_moments` assigns itself, never `lanes.evaluate_trigger`
#: — that function's own contract is FIRE/QUIET/BROKEN and stays untouched
#: (the ONE evaluator, CLAUDE.md "The router, and the ONE trigger evaluator").
READ_MOMENT_NONE = "NONE"
READ_MOMENT_UNDECLARED = "UNDECLARED"

#: A `when` that is PRESENT and invalid — the third answer this evaluator
#: used to fold into UNDECLARED (D-3, P2). The fold was the defect: an
#: ABSENT moment is the legitimate default across every kind here, while a
#: present-and-broken one is somebody's mistake, and reporting them with one
#: word meant the mistake rendered as the default and nothing looked. It is
#: the register's own signature class — a state the vocabulary could not
#: say, arriving as its nearest benign neighbour.
READ_MOMENT_MALFORMED = "MALFORMED"

#: No `when` at all, but the reader's OWN SHAPE supplies a default moment
#: (O6 §4 Part A, lc-253). This is the fourth answer the vocabulary could
#: not say before: a `verb:` or `session` reader without an authored `when`
#: used to fold into UNDECLARED — the same neighbour-fold vocab.py's
#: contract names, here caught by the evaluator rather than left to render
#: as "nothing to surface". DERIVED is never authored and never validated by
#: `_check_reader_when` — it is `read_moments`'s own default, applied only
#: where `classify_reader_when` has already said UNDECLARED (no `when`
#: present); a present-and-invalid `when` stays MALFORMED regardless of the
#: ref's shape, because an authored mistake is not the same fact as nothing
#: authored at all.
READ_MOMENT_DERIVED = "DERIVED"

#: Tier 1 (§4 Part A): the ref prefix whose moment IS the verb running.
#: Read literally against the ref string, never re-derived from
#: REF_PREFIXES — a `lane:`, `hook:` or `producer:` reader is prefixed too
#: and has no stated default yet, so it stays residue (UNDECLARED).
_DERIVE_VERB_PREFIX = "verb:"

#: Tier 2 (§4 Part A): the one bare ref whose moment defaults to the kind's
#: own `home` being written. `operator` is REF_BARE's other member and is
#: deliberately excluded — the design names only `verb:` and `session`
#: readers as having a computable default; an `operator` reader stays
#: residue, authorable via `when` exactly like today.
_DERIVE_SESSION_REF = "session"


def _derived_reader_detail(ref: str, home) -> str | None:
    """The tier-specific detail for a DERIVED moment, or None if `ref` is
    not one of the two derivable shapes.

    Kept separate from the state itself so a caller can tell "derived, and
    here is which tier" from "not derivable" without parsing prose out of
    `detail` — the same reason `WhenClass.state` and `.problem` are two
    fields rather than one.
    """
    if ref.startswith(_DERIVE_VERB_PREFIX):
        verb_name = ref[len(_DERIVE_VERB_PREFIX):]
        return (f"tier 1 (verb reader): the moment is {verb_name!r} running "
                "— nothing authored, nothing to author (O6 §4 Part A)")
    if ref == _DERIVE_SESSION_REF:
        if isinstance(home, str) and home.strip():
            where = f"home ({home})"
        else:
            where = "home (undeclared)"
        return (f"tier 2 (session reader): default moment is the kind's "
                f"{where} being written — nothing authored (O6 §4 Part A)")
    return None


def read_moments(body: dict, repo: Path | None = None) -> list:
    """Evaluate every `reader` entry's declared WHEN — the O6 evaluation half.

    A `predicate` WHEN is RUN, through `lanes.evaluate_trigger` and NOTHING
    ELSE — no second mapping, no local exit interpretation, so this cannot
    disagree with `lane list` or `item ready` about what BROKEN means. A
    `none` WHEN or an absent one is reported, never executed and never
    silently dropped: an absent moment and a quiet one are different
    answers.

    AN ABSENT `when` IS NOT ALWAYS UNDECLARED (O6 §4 Part A, lc-253). Where
    `classify_reader_when` says UNDECLARED — no `when` present — this
    function asks a second, narrower question the shared partition does not:
    does the ref's OWN SHAPE supply a default? A `verb:` reader's moment IS
    the verb running; a bare `session` reader's default moment is the
    kind's `home` being written. Both are derivable from fields the
    declaration already carries, so DERIVED costs nothing to author and
    UNDECLARED narrows to the genuine residue (`operator`, and any
    `lane:`/`hook:`/`producer:` reader, none of which have a stated
    default). This is deliberately NOT folded into `classify_reader_when`:
    that function's contract is the checker/evaluator shared PARTITION over
    `when`'s presence and validity, and a `verb:`/`session` ref with no
    `when` is still, structurally, "no `when`" — the derivation is what
    THIS evaluator does about that fact, not a new partition state the
    checker must also validate.

    Deferred import: `lanes` imports this module (`from . import
    declaration as decl`), so a module-level import here would be circular
    — the same reason `_verb_exists` defers its own `cli` import.
    """
    from . import lanes
    out = []
    for entry in body.get("reader") or []:
        if isinstance(entry, dict):
            ref = entry.get("reader")
            # PRESENCE, carried explicitly rather than inferred from the
            # value: `{"when": null}` and an entry with no `when` key are
            # different facts, and only this loop can tell them apart.
            present = "when" in entry
            when = entry.get("when")
        else:
            ref = entry
            present = False
            when = None
        ref = ref if isinstance(ref, str) else str(ref)
        # THE PARTITION IS READ BEFORE ANYTHING IS EXECUTED (P2), and that
        # ordering is the live repair rather than a tidy-up. This evaluator
        # had no bare-reader guard, so a `when` on a PREFIXED reader — which
        # the checker refuses — was still RUN; both attack arms drove a
        # `predicate touch <marker>` through it and watched the file appear.
        # Classifying first closes that by construction: only a verdict of
        # WHEN_PREDICATE ever reaches `evaluate_trigger`.
        verdict = classify_reader_when(ref, when, present=present)
        if verdict.state == WHEN_PREDICATE:
            trig = lanes.evaluate_trigger(verdict.command, cwd=repo)
            out.append(ReadMoment(ref, trig.state, trig.detail))
        elif verdict.state == READ_MOMENT_NONE:
            out.append(ReadMoment(ref, READ_MOMENT_NONE, verdict.why))
        elif verdict.state == READ_MOMENT_MALFORMED:
            # ITS OWN ANSWER, no longer folded into UNDECLARED. An absent
            # moment is the legitimate default; a present-and-broken one is
            # somebody's mistake, and reporting both with one word made the
            # mistake render as the default.
            out.append(ReadMoment(ref, READ_MOMENT_MALFORMED,
                                  verdict.problem))
        else:
            # verdict.state == READ_MOMENT_UNDECLARED: no `when` present.
            # Ask the second question classify_reader_when does not: does
            # the ref's shape itself supply a default (O6 §4 Part A)?
            derived_detail = _derived_reader_detail(ref, body.get("home"))
            if derived_detail is not None:
                out.append(ReadMoment(ref, READ_MOMENT_DERIVED,
                                      derived_detail))
            else:
                out.append(ReadMoment(ref, READ_MOMENT_UNDECLARED))
    return out


@dataclass
class DueRead:
    """One kind whose DERIVED reader moment fires for a given act (O6 §4 Part
    B, lc-254: "surface it on the ACT — when a verb runs, name the kinds
    whose derived moment that act fired").

    `note` is the SAME prose `_derived_reader_detail` already produces for
    `kind moments` — reused rather than re-worded, so the two surfaces
    (`kind moments`'s evaluation and this act-time surface) can never drift
    apart describing the same derivation two ways.
    """
    kind: str
    reader: str
    note: str


def due_reads_for_act(doc: dict, act_path: str) -> list:
    """Every kind whose DERIVED reader moment IS `act_path` running.

    Consumed by `cli.py`'s `main()` — the ONE dispatch point that already
    observes every act — to surface a due-read line on the acting verb's own
    output (O6 §4 Part B1) and to add `surfaced=<kinds>` to that invocation's
    fire-log detail (§7's transition table, row 1). Never called from a
    per-verb copy: a second implementation beside `main()` would be exactly
    the class this repo's own CLAUDE.md (law 24, the `_carrier_verb`
    incident) already names as the wrong shape.

    STRUCTURAL ONLY — this never calls `lanes.evaluate_trigger`, unlike
    `read_moments`. DERIVED never comes from a predicate: it is assigned
    only where `classify_reader_when` returns UNDECLARED, and that function
    returns UNDECLARED if and only if no `when` is present on the entry (its
    own contract, one branch, nothing else reaches it) — so checking
    presence here answers the same question `classify_reader_when` would,
    without running anything. Calling `read_moments` here instead would run
    every kind's declared predicate as a side effect of every unrelated verb
    invocation — a `predicate touch <marker>`-shaped entry would fire on
    every single command run in the repo, not only the one act it declares.

    Two tiers, matching O6 §4 Part A and `_derived_reader_detail` exactly:
      - Tier 1 (`verb:<name>` reader): fires when `act_path == name` — the
        moment IS that verb running.
      - Tier 2 (bare `session` reader): fires when `act_path` is one of the
        kind's own declared WRITER verbs. The write-target mapping is not
        invented here: `writer` already names, per kind, which verb(s)
        write its `home` (e.g. `items`: `writer: "verb:item add, verb:item
        park, verb:item close"`), in the exact `verb:<path>` spelling
        `main()`'s own dispatch paths already use — parsed with
        `parse_refs`, the one typed-ref parser every reader/writer check
        already goes through, rather than re-derived from source.

    At most one `DueRead` per kind: further reader entries on a kind already
    found due for this act cannot change whether that kind is due.
    """
    out = []
    for name, body in (doc.get("kinds") or {}).items():
        if not isinstance(body, dict):
            continue
        for entry in body.get("reader") or []:
            if isinstance(entry, dict):
                ref = entry.get("reader")
                present = "when" in entry
            else:
                ref = entry
                present = False
            ref = ref if isinstance(ref, str) else str(ref)
            if present:
                continue
            fires = False
            if ref.startswith(_DERIVE_VERB_PREFIX):
                fires = ref[len(_DERIVE_VERB_PREFIX):] == act_path
            elif ref == _DERIVE_SESSION_REF:
                writer = body.get("writer")
                if isinstance(writer, str) and writer.strip():
                    fires = any(typ == "verb" and wname == act_path
                                for typ, wname in parse_refs([writer]))
            if fires:
                note = _derived_reader_detail(ref, body.get("home")) or ""
                out.append(DueRead(name, ref, note))
                break
    return sorted(out, key=lambda d: d.kind)


def check_laws_present(repo: Path, laws_rel: str, res: Result) -> None:
    """The declared laws file exists and is readable — nothing about its SIZE.

    THIS IS THE COULD-NOT-VERIFY CASE THE DESIGN NAMES EXPLICITLY (§3.8b: an
    absent laws file is COULD-NOT-VERIFY naming the source, never a pass). The
    laws file may be UNTRACKED by design (claude-code-cache-fix declares
    `CLAUDE.local.md`, untracked because the tracked `CLAUDE.md` is upstream's
    and non-binding there), so this reads the WORKING TREE: a check that
    resolved the file through the git INDEX would see zero lines and report a
    clean 0, which is an absence of evidence wearing a verdict's clothes.

    THE 60-LINE CAP IS GONE (R22). It was withdrawn as a cap, not moved: a
    laws file may need 200 lines and the only question is whether every line
    is a law. Its size is now REPORTED as a number by `lifecycle audit`, and
    the scope audit there is the mechanism that replaced the cap. `kind check`
    validates the declaration; what the file it names CONTAINS is the audit's
    screen, and keeping a prose-content finding inside the declaration's own
    verb is what made `kind check` unable to answer CLEAN over a healthy repo.
    """
    path = repo / laws_rel
    if not path.is_file():
        res.cannot_verify(
            f"the declared laws file {laws_rel!r} is not present in the "
            "working tree, so nothing about it could be measured. This is "
            "COULD NOT VERIFY and not a clean zero — an absent file and a "
            "present one are not the same answer.")
        return
    try:
        path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        res.cannot_verify(f"the declared laws file {laws_rel!r} could not be "
                          f"read ({exc!r}).")


# --- the git hooks a repo SHIPS stay launchable ------------------------------

#: Where a repo keeps the git hooks it owns ITSELF — its own tooling rather
#: than plugin payload. `tools/` is this family's home for repo-owned checks,
#: and a hook there is TRACKED, so the population is identical in a fresh
#: clone. NOT `.git/hooks/*`: that is machine-local, untracked and absent in
#: a fresh clone, so a guard reading it is green by construction exactly
#: where it matters least.
REPO_GIT_HOOKS_DIR = "tools/git-hooks"

#: The only mode git can LAUNCH a tracked regular file at.
EXECUTABLE_MODE = "100755"

#: A tracked symlink. Git's record cannot answer launchability here — the
#: TARGET's mode decides, and the target is not in this tree's record — so
#: this is the could-not-verify answer: never a finding (which would be the
#: guard firing on legitimate work) and never a silent pass.
SYMLINK_MODE = "120000"


def head_commit(repo: Path) -> bool | None:
    """Three answers about HEAD: True a commit, False none yet, None unasked.

    The middle answer is the one worth separating. A repo with no commit has
    committed no hook, so the guarded set below is EMPTY — a state, not an
    unanswered question — while a path git cannot be asked about at all
    leaves the set UNKNOWN. Measured: `rev-parse --verify -q HEAD` exits 1 on
    an unborn branch and 128 outside a work tree, which is what makes the two
    distinguishable without parsing an error message.
    """
    try:
        p = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify",
                            "-q", "HEAD"], capture_output=True, text=True)
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode == 0:
        return True
    if p.returncode == 1:
        return False
    return None


def tree_modes(repo: Path, pathspecs: list) -> dict | None:
    """`{path: mode}` for the BLOBS HEAD's tree carries at `pathspecs`.

    NOT recursive, deliberately: a directory pathspec with a trailing slash
    then answers for the files DIRECTLY under it — the population the ruling
    names — and a nested directory arrives as a tree entry this walk skips
    rather than as a member it would have to explain.

    `-z` because `ls-tree`'s default output QUOTES a path carrying special
    characters: a quoted name is a RENDERED view of a path, and a lookup
    against it is the paraphrase comparison this repo keeps finding. With
    `-z` the name is the bytes.

    None means git could not answer — no git, not a work tree, no such
    revision — and is kept apart from the empty dict, which means git
    answered and the tree carries nothing there.
    """
    try:
        p = subprocess.run(["git", "-C", str(repo), "ls-tree", "-z", "HEAD",
                            "--", *pathspecs], capture_output=True, text=True)
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode != 0:
        return None
    out = {}
    for record in p.stdout.split("\0"):
        meta, tab, path = record.partition("\t")
        bits = meta.split()
        if not tab or not path or len(bits) < 3 or bits[1] != "blob":
            continue
        out[path] = bits[0]
    return out


def declared_hook_scripts(repo: Path) -> list:
    """The plugin-declared hook scripts that live INSIDE `repo`, repo-relative.

    The manifest's `script` values are relative to the plugin tree. In the
    plugin's OWN checkout that tree is inside the repo under test and its
    hooks are this repo's payload; in a consumer repo the plugin is installed
    elsewhere, and a hook shipped by someone else's release is not that
    repo's to police. So membership is decided by containment, computed every
    run, rather than by a flag anyone has to remember to set.
    """
    hooks = plugin_manifest().get(PLUGIN_GIT_HOOKS_KEY)
    if not isinstance(hooks, dict):
        return []
    try:
        root = Path(repo).resolve()
    except OSError:
        return []
    out = []
    for body in hooks.values():
        script = body.get("script") if isinstance(body, dict) else None
        if not isinstance(script, str) or not script.strip():
            continue
        try:
            rel = (plugin_root() / script).resolve().relative_to(root)
        except (ValueError, OSError):
            continue
        out.append(rel.as_posix())
    return out


def hook_population(repo: Path) -> tuple:
    """`({path: mode}, [declared scripts])` — the whole guarded set, derived.

    ONE body, because this is both what the check measures and what the
    battery pins. A pin written over a DIFFERENT expression than the check's
    own is a coverage assertion restated from its source, and it stays green
    the day the check's derivation loses a half — measured here (lc-103, bite
    1): with the `tools/git-hooks/` half removed from the check, a pin over
    the helper called directly stayed GREEN, which is exactly the guard that
    would have shipped green over this repo's own incident.

    The dict is None where git could not answer at all; the declared list is
    returned beside it because a declared script ABSENT from the tree is a
    third answer the modes alone cannot express.
    """
    declared = declared_hook_scripts(repo)
    return tree_modes(repo, [REPO_GIT_HOOKS_DIR + "/"] + declared), declared


def check_hook_modes(repo: Path, res: Result) -> None:
    """Every git hook this repo SHIPS is committed EXECUTABLE (mode 100755).

    A hook committed at 100644 is a gate that fails OPEN: git cannot launch
    it, the push or the commit proceeds, and every CONTENT check reports
    clean because the bytes are right. Measured here — `0cbd1ad` committed
    this repo's push gate at 100644 and `d8c3934` restored the bit against
    the SAME blob `887ecff8`, mode alone differing, which is exactly why a
    bytes-only restore check passed it; the leak scan was dead for those
    twenty minutes. Second instance the same day in a sibling repo
    (claude-code-cache-fix `d3f4ee8`). The cause generalises past both: a
    Python atomic write creates its temp file at the default 0644 and
    `os.replace` carries that mode onto the target, so the source's mode is
    dropped while sha256 and `git status` both look right.

    THE POPULATION IS DERIVED EVERY RUN, never a list beside the thing it
    mirrors: the plugin-declared scripts that live inside this repo, UNION
    every file directly under `tools/git-hooks/`. The declaration alone would
    not do — this repo's manifest declares `pre-commit` and nothing else, so
    a guard keyed on it would have been GREEN over the very file that
    shipped dead, which is the expectation derived from an artifact that does
    not mention the case.

    THE MODE IS READ FROM GIT, NEVER `stat`. A deployed hook is reached
    through a symlink, so `stat` follows the link and answers about the
    target; and the committed mode is what a fresh clone gets, which is the
    thing that actually fails open.
    """
    head = head_commit(repo)
    if head is None:
        res.cannot_verify(
            "could not ask git for HEAD, so the committed mode of the hooks "
            "this repo ships could not be read. A hook committed without its "
            "executable bit is a gate that fails open, and nothing else here "
            "would notice.")
        return
    if head is False:
        return

    modes, declared = hook_population(repo)
    if modes is None:
        res.cannot_verify(
            "git could not read HEAD's tree, so the committed mode of the "
            "hooks this repo ships could not be read. Unlaunchable and "
            "unmeasured are not the same answer.")
        return

    for rel in declared:
        if rel in modes:
            continue
        res.cannot_verify(
            f"the plugin declares the git hook {rel!r} and HEAD carries no "
            "blob there, so its committed mode could not be read. A declared "
            "hook absent from the tree is the one that silently never fires.")

    for path in sorted(modes):
        mode = modes[path]
        if mode == EXECUTABLE_MODE:
            continue
        if mode == SYMLINK_MODE:
            res.cannot_verify(
                f"{path} is a git hook this repo ships and HEAD carries it as "
                "a SYMLINK, whose launchability is decided by the target's "
                "mode rather than by anything in this tree's record.")
            continue
        res.add("hook_not_executable",
                f"{path} is a git hook this repo ships and HEAD carries it at "
                f"mode {mode}, not {EXECUTABLE_MODE}. Git cannot launch it, "
                "so the gate FAILS OPEN — the push or the commit proceeds and "
                "every content check reports clean, because the bytes are "
                "right. Restore it with `git update-index --chmod=+x` and "
                "commit that; a `chmod` in the working tree alone leaves the "
                "committed mode, which is what a fresh clone gets, unchanged.")


# --- one schema version per repo (§3.8c) -------------------------------------

#: Which declared kinds keep a carrier whose head carries a `schema:` line.
#: The kind NAMES are the declaration's, so a repo that spells them
#: differently simply has no carrier to compare and says so.
SCHEMA_CARRIER_KINDS = ("items", "done bodies", "ledger lines")


def carrier_homes(doc: dict) -> dict:
    """`{label: repo-relative path}` for every carrier that carries a version.

    RESOLVED THE WAY EVERY OTHER READER RESOLVES THEM, which is the whole
    point of putting it here: the closure home comes through the top-level
    `closure-home` and only falls back to the `done bodies` kind, and the
    ledger falls back to `LEDGER.md` — exactly `verbs.context`'s rules. A
    second resolution would disagree with the first the day a repo declared
    one and not the other, and the disagreement is silent: measured on this
    build, a declaration that registered only the `items` kind had its
    closure home and ledger left at the OLD schema by an `--apply` that
    reported success, because the bump resolved homes through the KINDS alone
    while the closure home is named at the top level.
    """
    def kind_home(kind, *, allow_glob=False):
        body = (doc.get("kinds") or {}).get(kind)
        h = body.get("home") if isinstance(body, dict) else None
        if not (isinstance(h, str) and h.strip()):
            return None
        return h if allow_glob or "*" not in h else None

    out = {}
    items_home = kind_home("items")
    if items_home:
        out["items"] = items_home
    closure = doc.get("closure-home")
    closure = closure if isinstance(closure, str) and closure.strip() \
        else kind_home("done bodies")
    if closure and "*" not in closure:
        out["done bodies"] = closure
    out["ledger lines"] = kind_home("ledger lines") or "LEDGER.md"

    # THE GLOB EXCLUSION IS REVERSED FOR THE LIVE ARC HOME, AND ONLY IT
    # (lc-242; arc design N9/T-a2). A kind whose bodies are `arcs/*.md` sat
    # OUTSIDE one-schema-per-repo silently — neither checked nor declared
    # exempt, which is the worst of the three states because nothing said
    # which it was.
    #
    # WHAT THE EXCLUSION PROTECTED, now explicit instead of implicit in a
    # parse-time guard: it kept CLOSURE RECORDS out of the rewrite path.
    # Reversing it wholesale would make every closed body schema-stamped and
    # a bump would rewrite the archive — which contradicts what a closure
    # record IS. So `closed arcs` is deliberately NOT here, and its ABSENCE
    # is the pin: a closed body keeps the schema it closed at, and nothing
    # grades it against the floor. The law text carries the same exemption in
    # the same versioned act, because an exemption living only in code is a
    # rule nobody can read and one living only in prose is a rule nothing
    # enforces.
    #
    # NAMED RATHER THAN INFERRED. The kinds this function watches are a
    # declared list — it already names items, done bodies and ledger lines —
    # and deriving "is this a record kind?" from a stage's prose would be a
    # heuristic over text somebody writes freely. A kind joins this list by
    # being added to it, visibly.
    arcs_home = kind_home("arcs", allow_glob=True)
    if arcs_home:
        out["arcs"] = arcs_home
    return out


def carrier_paths(repo: Path, home: str) -> list:
    """Every concrete file a carrier home names, in a stable order.

    A HOME MAY BE A GLOB (lc-242), and before that was possible every caller
    could treat `repo / home` as one file. A glob home is N bodies, each
    carrying its own `schema:` line, so the expansion happens HERE — once —
    rather than in each consumer: two expansions would disagree about
    ordering or about what an absent directory means, and the disagreement
    would be silent.

    SORTED, because callers report per file and an unstable order makes two
    runs over one tree read as two different answers.
    """
    if "*" not in home:
        return [repo / home]
    return sorted(repo.glob(home))


def schema_head(text: str, name: str = "the carrier"):
    """`(index, n, why-not)` — WHICH line carries the `schema:` head, and what
    it says.

    ONE BODY DECIDES BOTH HALVES, AND THE SECOND HALF IS WHY THIS FUNCTION
    EXISTS (lc-205). A reader that answers only "what version" leaves every
    writer to find the line for itself, and a writer that goes looking does
    not agree with this loop for free. It did not: `migrate --schema-from
    --apply` matched `raw.strip().startswith("schema:")` over EVERY line,
    while this loop inspects only the first non-comment line and stops. Those
    coincide exactly while the head is spelled the writer's way. Where it was
    not — `schema : 1`, a space before the colon, which this loop accepts
    because it strips around the partition — the writer skipped the head,
    kept scanning, and rewrote the first BODY line beginning `schema:`,
    leaving the real version line untouched and printing `written:` at exit
    0. Measured: a body line `schema: 9` became `schema: 2` while line 1
    stayed `schema : 1`.

    So the position is returned, not just the number, and a caller that
    REWRITES the head rewrites `index` rather than searching. Two predicates
    cannot disagree about spelling or position when there is one.

    Comment lines before the schema line are SKIPPED rather than refused
    (§3.8c): a public `LEDGER.md` must be able to say what it is for, and a
    parser that demanded the version on line 1 forced a carrier in a public
    tree to be exactly `schema: 1` and nothing else. That leniency is
    load-bearing in production rather than hypothetical — this repo's own
    heads sit at ITEMS.md:1, ITEMS-DONE.md:6 and LEDGER.md:21.

    `index` is returned alongside a REFUSED value too (a non-integer), so a
    caller can name the offending line rather than the file.
    """
    for i, raw in enumerate(text.split("\n")):
        s = raw.strip()
        if not s or s.startswith("#") or s.startswith("<!--"):
            continue
        head, colon, val = s.partition(":")
        if colon and head.strip() == "schema":
            try:
                return i, int(val.strip()), None
            except ValueError:
                return i, None, (f"{name}'s `schema:` value {val.strip()!r} "
                                 "is not an integer")
        return None, None, f"{name} carries no `schema:` head line"
    return None, None, f"{name} carries no `schema:` head line"


def carrier_schema(path: Path):
    """`(n, why-not)` — the `schema:` a carrier head declares.

    The head is located by `schema_head`, which is the ONE body deciding
    which line that is; this wrapper adds only the file read. A caller that
    must WRITE the head calls `schema_head` directly and uses its index.
    """
    if not path.is_file():
        return None, f"{path.name} is not present"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"{path.name} could not be read ({exc!r})"
    _index, n, why = schema_head(text, path.name)
    return n, why


def check_schema_agreement(repo: Path, doc: dict, res: Result) -> None:
    """ONE schema version per repo: the carriers must EQUAL the declaration.

    §3.8c states it as one number and one command per bump. Without this the
    declaration and its carriers are two spellings of one fact, and two
    spellings diverge from the moment they disagree — silently, because each
    reader resolves through whichever file it happens to open. The FLOOR check
    is a different question and stays where it is: "stamped above what this
    build understands" is about the TOOL, this is about the REPO.
    """
    declared = doc.get("schema")
    if not isinstance(declared, int) or isinstance(declared, bool):
        return
    for kind, home in carrier_homes(doc).items():
        paths = carrier_paths(repo, home)
        if "*" in home and not paths:
            # A GLOB MATCHING NOTHING IS NOT A CLEAN ANSWER and is not a
            # finding either: the kind is declared and has no bodies yet,
            # which is the ordinary state of an optional carrier before its
            # first instance. Silence here would read as "checked and
            # agreeing" over a population that was never examined.
            continue
        for path in paths:
            n, why = carrier_schema(path)
            where = str(path.relative_to(repo)) if path.is_relative_to(repo) \
                else str(path)
            if n is None:
                res.cannot_verify(
                    f"the `{kind}` carrier {where!r} could not be read for "
                    f"its schema line, so one-schema-per-repo was not "
                    f"checked for it: {why}.")
                continue
            if n != declared:
                res.add("schema_mismatch",
                        f"the declaration is stamped schema {declared} and "
                        f"the `{kind}` carrier {where!r} is stamped {n}. ONE "
                        "schema "
                        "version per repo (§3.8c): one number, one command "
                        "per bump. Two numbers for one fact diverge from the "
                        "moment they disagree, and each reader resolves "
                        "through whichever it opened. Run `lifecycle migrate "
                        f"--schema-from {min(n, declared)}`.")


def check_lanes_registered(repo: Path, declared, res: Result) -> None:
    """§3.8b's registration invariant, in the direction nothing watched.

    A lane BODY the declaration does not list is UNREGISTERED, and until this
    existed nothing said so: `read_lane` catches a declared lane with no file,
    while a file with no declaration was invisible to every verb — `lane list`
    walks the declaration's own list and has no directory scan, so it rendered
    `declared lanes: 0 — EMPTY` over a tree carrying `lanes/x.md` and exited
    CLEAN. A router that cannot see a door cannot route to it, and the board
    that omits it reads exactly like a board with nothing to say.

    NOT `unregistered_persisted_thing`, and the difference is measurable
    rather than a matter of taste. That row (invariant 1, `kind sweep`) asks
    whether a TRACKED file resolves to a registered KIND — measured over a
    scratch repo, an untracked `lanes/x.md` is absent from its sweep entirely
    (4 tracked files, 3 findings), and a repo registering a lanes kind would
    clear it while the door stayed undeclared. This asks whether the
    DECLARATION names the door, which is what decides whether any verb can
    reach it — and the freshly written stub, untracked by construction, is
    exactly the case the other row cannot see.

    THE DIRECTORY IS ASKED THROUGH `lanes.py`, which owns every other
    lane-shape fact (`LANES_DIR`, `LANE_PARTS`, `read_lane`). Imported inside
    the function because `lanes` imports THIS module at its top: the shape
    question belongs there and the finding belongs here, and a copy of either
    on the other side would be a second body for one fact.
    """
    from . import lanes as lanes_mod

    try:
        on_disk = lanes_mod.lane_files_on_disk(repo)
    except OSError as exc:
        res.cannot_verify(
            f"the {lanes_mod.LANES_DIR}/ directory could not be listed "
            f"({exc!r}), so a lane body the declaration does not name would "
            "not have been seen. An unlistable directory is not an empty one.")
        return
    known = set(declared)
    for name in on_disk:
        if name in known:
            continue
        res.add("lane_undeclared",
                f"{lanes_mod.LANES_DIR}/{name}.md is a lane body and {name!r} "
                "is not in this repo's declared `lanes` list. §3.8b: a lane "
                "file the declaration does not list is UNREGISTERED. It is "
                "not merely unrouted — `lane list` walks the declaration's own "
                "list, so the door has no state, no trigger evaluation and no "
                "line on the board, and the board renders CLEAN over it. "
                f"Declare it (`lifecycle lane new {name}` registers what it "
                "writes) or remove the body.")


def add_lane(repo: Path, name: str) -> tuple[bool, str | None]:
    """Append `name` to a repo's declared `lanes` list. `(added, why-not)`.

    THE WRITE HALF OF THE INVARIANT `check_lanes_registered` READS. `lane new`
    writes `lanes/<door>.md`; a verb whose normal output is invisible to the
    tool that owns it has not finished, and the hand step it left behind was
    delivered by nobody — `lane list` said nothing about the door and the only
    place the author learned that was a hint in the verb's own output.

    IDEMPOTENT, AND IT SAYS WHICH HAPPENED. `(False, None)` is "already
    declared" — a fact, not a failure; `(False, <why>)` is "could not", and
    the caller must not report CLEAN over it. A single boolean would have
    collapsed the two, which is the shape that lets a no-op read as a write.

    IT NEVER INVENTS THE LIST. An absent, unreadable or non-list `lanes` is
    returned as a reason, never normalised to `[]` and appended to: writing a
    `lanes` key onto a declaration this function could not parse would silently
    discard whatever was there.

    BYTE FIDELITY IS PART OF THE CONTRACT: `ensure_ascii=False`, two-space
    indent, one trailing newline — measured against this repo's own
    declaration, that pair round-trips byte-identically, so the diff a caller
    sees is EXACTLY ONE added name. With the default `ensure_ascii=True` the
    same round trip rewrites 217 lines' worth of `—` and `§` into `\\uXXXX`
    escapes, and a one-name registration would arrive buried in it.
    """
    path = repo / DECLARATION_REL
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return False, (f"{DECLARATION_REL} could not be read ({exc!r}), so "
                       f"{name!r} was not declared.")
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as exc:
        return False, (f"{DECLARATION_REL} is not valid JSON ({exc.msg}, line "
                       f"{exc.lineno}), so {name!r} was not declared.")
    if not isinstance(doc, dict):
        return False, (f"{DECLARATION_REL} parses to {type(doc).__name__}, not "
                       f"an object, so {name!r} was not declared.")
    lanes = doc.get("lanes")
    if not isinstance(lanes, list) or not all(
            isinstance(x, str) for x in lanes):
        return False, (f"the declaration's `lanes` is {lanes!r}, not a list of "
                       f"names, so {name!r} was not appended to it. Repairing "
                       "the key is a separate act from declaring a door, and "
                       "guessing what the value meant would discard it.")
    if name in lanes:
        return False, None
    doc["lanes"] = list(lanes) + [name]
    try:
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    except OSError as exc:
        return False, (f"{DECLARATION_REL} could not be written ({exc!r}), so "
                       f"{name!r} was not declared.")
    return True, None


def remove_lane(repo: Path, name: str) -> tuple[bool, str | None]:
    """Drop `name` from a repo's declared `lanes` list. `(removed, why-not)`.

    THE MISSING HALF OF `add_lane`, and its absence had a consequence rather
    than being an asymmetry on paper: a GENERATED lane — one a deadline
    creates as its observer — outlives the thing that generated it unless
    something takes the row back out. An arc closes, its deadline stops
    meaning anything, and the row keeps the door on the board forever. The
    body would be deletable by hand; the ROW was not removable at all.

    THE SAME THREE-ANSWER SHAPE its counterpart keeps, for the same reason:
    `(False, None)` is "was not declared" — a fact, not a failure, and the
    ordinary case when a retirement runs twice — while `(False, <why>)` is
    "could not", which a caller must never report CLEAN over. One boolean
    would collapse them, and a no-op would read as a write.

    IT NEVER INVENTS OR NORMALISES THE LIST. An absent, unreadable or
    non-list `lanes` is returned as a reason: rewriting a key this function
    could not parse would discard whatever was there, which is the one
    failure mode a deregistration must not have.

    BYTE FIDELITY MIRRORS `add_lane` EXACTLY — `ensure_ascii=False`, two-space
    indent, one trailing newline — so a removal shows as exactly one dropped
    name rather than arriving buried in 217 lines of re-escaped punctuation.
    """
    path = repo / DECLARATION_REL
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return False, (f"{DECLARATION_REL} could not be read ({exc!r}), so "
                       f"{name!r} was not deregistered.")
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as exc:
        return False, (f"{DECLARATION_REL} is not valid JSON ({exc.msg}, line "
                       f"{exc.lineno}), so {name!r} was not deregistered.")
    if not isinstance(doc, dict):
        return False, (f"{DECLARATION_REL} parses to {type(doc).__name__}, not "
                       f"an object, so {name!r} was not deregistered.")
    lanes = doc.get("lanes")
    if not isinstance(lanes, list) or not all(
            isinstance(x, str) for x in lanes):
        return False, (f"the declaration's `lanes` is {lanes!r}, not a list of "
                       f"names, so {name!r} was not removed from it. "
                       "Repairing the key is a separate act, and guessing "
                       "what the value meant would discard it.")
    if name not in lanes:
        return False, None
    doc["lanes"] = [x for x in lanes if x != name]
    try:
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    except OSError as exc:
        return False, (f"{DECLARATION_REL} could not be written ({exc!r}), so "
                       f"{name!r} was not deregistered.")
    return True, None


# --- rendering ---------------------------------------------------------------

def render_digest(doc: dict, repo: Path) -> list[str]:
    """One line per kind — the MAP a session holds, not the files (lc-219).

    Twenty of this repo's twenty-five kinds declare `reader: session` and no
    command fires those reads. The session-start injection fires ONCE, before
    a session knows what it will need, and nothing fires at the moment of
    APPLICATION — which is where retrieval actually fails: a desk dispatched
    four research lanes past a document it had already handled 17 times.

    WHY MEMBER COUNTS RATHER THAN A BARE MAP, which is the whole mechanism: a
    map naming `docs/audits/` would have told that desk where audits live and
    it would still have dispatched. A line naming the NEWEST member puts the
    document itself in front of the session. It also answers the wallpaper
    risk — a block that never changes stops being read, and counts move as
    work happens.

    IT SHARES `expand_home` WITH THE RETIRE WALK AND DELIBERATELY NOT
    `list_home`. That function counts what an INSTANCE of a kind is, parsing
    a carrier's fixed-slot blocks; this asks a different question on purpose —
    FILES — because the digest is a POINTER SURFACE and never an authority on
    content. Parsing per-kind entry structure here would be a second body for
    what the owning verbs already read.

    WHAT IT DOES NOT DO, so a later reader does not over-read it: it says what
    kinds EXIST, never what is IN them, and it does not replace `kind sweep` —
    this reports what is DECLARED, the sweep reports what is on disk and
    unaccounted for. Only the sweep catches what nobody declared.
    """
    from . import retire as retire_mod

    # WHAT THE REPO KEEPS, per git — the same instrument `kind sweep` asks.
    # Without it the newest member of `cli source` came back as a
    # `__pycache__/*.pyc`: true of the filesystem, useless as a pointer, and
    # actively misleading in a block a session is meant to trust. An untracked
    # build artifact is not a member of a source kind. Asked ONCE for the
    # whole repo rather than per kind; a repo git cannot answer for falls back
    # to the filesystem, which is the honest degrade — out-of-tree homes
    # (XDG state) have no git listing by construction and are counted there.
    tracked = None
    try:
        import subprocess
        p = subprocess.run(["git", "-C", str(repo), "ls-files"],
                           capture_output=True, text=True, timeout=10)
        if p.returncode == 0:
            tracked = {(repo / line).resolve()
                       for line in p.stdout.split("\n") if line.strip()}
    except (OSError, subprocess.SubprocessError):
        tracked = None

    def keep(paths):
        """In-tree members filtered to what git tracks; out-of-tree kept."""
        if tracked is None:
            return list(paths)
        out_ = []
        for q in paths:
            rq = q.resolve()
            inside = str(rq).startswith(str(repo.resolve()) + "/")
            if not inside or rq in tracked:
                out_.append(q)
        return out_

    kinds = doc.get("kinds")
    if not isinstance(kinds, dict) or not kinds:
        return ["kinds: NONE DECLARED — a repo that persists something "
                "registers it; this declaration registers nothing."]

    lines = ["THE REGISTRY — what this repo keeps, and where. "
             "`[session-read]` marks a kind no verb reads for you."]
    for name in kinds:
        body = kinds[name] if isinstance(kinds[name], dict) else {}
        home = body.get("home")
        reader = body.get("reader")
        reads = reader if isinstance(reader, list) else [reader or ""]
        reader_refs = [entry.get("reader") if isinstance(entry, dict)
                       else entry for entry in reads]
        # parse_refs, not startswith: a comma-joined entry ("session,
        # verb:x") is legal to the typed-ref grammar, and this predicate
        # must read refs with the same parser _check_typed_refs does or
        # the two disagree on exactly that shape.
        typed = parse_refs([r for r in reader_refs if isinstance(r, str)])
        marker = ("  [session-read]"
                  if not any(t == "verb" for t, _ in typed) else "")

        if not isinstance(home, str) or not home.strip():
            lines.append(f"  {name:<22} COULD NOT VERIFY: no home declared, "
                         f"so there is nothing to point at.{marker}")
            continue

        resolved = retire_mod.expand_home(home)
        if retire_mod._UNEXPANDED.search(resolved):
            # THE THIRD ANSWER, and it is the easiest thing to get wrong here:
            # a zero and an unreadable home are the SAME STRING to a reader,
            # and this block is trusted at a glance. Never `0 file(s)`.
            lines.append(
                f"  {name:<22} {home}"
                f"\n      COULD NOT VERIFY: carries a variable this cannot "
                f"resolve, so no member was examined — not a count of "
                f"zero.{marker}")
            continue

        path = repo / resolved
        try:
            if "*" in resolved:
                # THE BRANCH KEYS ON ABSOLUTE, NOT ON base.is_dir(), and the
                # first version got that wrong: an in-repo glob was globbed
                # from the matched directory, so `docs/audits/*.md` searched
                # `docs/audits/docs/audits/*.md` and reported 0 file(s) over a
                # directory holding several. A false zero in the one block
                # that exists to be trusted at a glance.
                if Path(resolved).is_absolute():
                    stem = resolved.split("*", 1)[0]
                    base = Path(stem if stem.endswith("/")
                                else str(Path(stem).parent))
                    pattern = resolved[len(str(base)):].lstrip("/")
                    hits = base.glob(pattern) if base.is_dir() else []
                else:
                    hits = repo.glob(resolved)
                hits = sorted(keep(p for p in hits if p.is_file()))
            elif path.is_dir():
                hits = sorted(keep(p for p in path.rglob("*")
                                   if p.is_file()))
            elif path.is_file():
                stamp = _mtime_date(path)
                lines.append(f"  {name:<22} {home}   ({stamp}){marker}")
                continue
            else:
                lines.append(f"  {name:<22} {home}   not present{marker}")
                continue
        except OSError as exc:
            lines.append(f"  {name:<22} {home}"
                         f"\n      COULD NOT VERIFY: {exc!r}{marker}")
            continue

        if not hits:
            lines.append(f"  {name:<22} {home}   0 file(s){marker}")
            continue
        newest = max(hits, key=lambda p: p.stat().st_mtime)
        try:
            shown = newest.relative_to(repo)
        except ValueError:
            shown = newest
        lines.append(f"  {name:<22} {home}   {len(hits)} file(s), "
                     f"newest: {shown}{marker}")
    return lines


def _mtime_date(path: Path) -> str:
    import datetime
    return datetime.date.fromtimestamp(
        path.stat().st_mtime).isoformat()


def render_kinds(doc: dict) -> list[str]:
    """Every kind, every stage, LONGHAND.

    Never a sparse table. A table that omits what it has nothing to say
    about renders as silence, and silence reads as clean — the same defect
    the router's longhand roster state exists to prevent.
    """
    out = []
    kinds = doc.get("kinds")
    if not isinstance(kinds, dict) or not kinds:
        return ["kinds: NONE DECLARED — a repo that persists something "
                "registers it; this declaration registers nothing."]
    for name in kinds:
        body = kinds[name] if isinstance(kinds[name], dict) else {}
        out.append(f"kind: {name}")
        for stage in KIND_STAGES:
            if stage not in body:
                out.append(f"    {stage:<10} UNDECLARED  <- checker finding")
                continue
            v = body[stage]
            if stage == "reader" and isinstance(v, list):
                out.append(f"    {stage:<10} {'; '.join(v)}")
            elif stage == "exit" and isinstance(v, dict):
                detail = f" {v['detail']}" if v.get("detail") else ""
                out.append(f"    {stage:<10} {v.get('action')}{detail}")
                out.append(f"    {'':<10}   recording act: {v.get('recording-act')}")
            else:
                out.append(f"    {stage:<10} {v}")
    return out


def _writer_bucket(writer) -> str:
    """One kind's `writer` value, bucketed for `structure_summary` — lc-174.

    THE RULE READS THE ACTUAL TYPED REFERENCE, never the raw string, because
    `writer` is not always a single token: `parse_refs` (§3.8c, the typed-ref
    parser every other writer/reader check already goes through) splits a
    comma-joined value into `(type, name)` pairs, and this repo's own
    declaration carries a writer worth exactly that split — `"verb:ledger
    add, session"` on `ledger lines`, written by both a verb and the bare
    session. Reading it with a plain `== "session"` or a hand-rolled
    substring test would silently drop that kind into the wrong bucket
    (an equality test in a typed-parser's clothing, the paraphrase-drift
    class), and a fresh `in`/`startswith` here would be a second, competing
    parser for a fact `parse_refs` already owns.

    'verb' fires wherever ANY entry in the writer is typed `verb:` — a kind
    written partly by a verb still carries partial self-administration,
    which is the property this split predicts. The literal bare `session`
    (and ONLY that, alone) is its own bucket. Everything else — absent,
    malformed, `producer:`/`hook:`/`lane:`/`operator`, or a mix that never
    names a verb — is `other`, exactly as the booking's own wording puts it:
    "everything else counts as other".

    PROVED against this repo's live declaration, not merely reasoned: the
    booking's MEASURED-AGAIN figures (26 kinds, verb 5 / session 20 /
    other 1, 0 undeclared) reproduce ONLY under this rule — a plain
    `writer == "session"` check would move `ledger lines` (a verb+session
    mix) out of the verb bucket the booking counts it in.
    """
    if not isinstance(writer, str) or not writer.strip():
        return "other"
    types = {typ for typ, _ in parse_refs([writer])}
    if "verb" in types:
        return "verb"
    if types == {"session"}:
        return "session"
    return "other"


def structure_summary(doc: dict) -> dict:
    """Three facts about what the repo IS — lc-174, the session-start
    announcement's structure half (`docs/answerable-not-felt.md`, mechanism
    1: the banner puts open items, the ledger tail, the ready set and gate
    status in front of a session, and never the declaration's own shape, so
    a fact already sitting in a tracked file gets re-derived by reasoning).

    Read from THIS FUNCTION'S OWN `doc` ARGUMENT — the parsed declaration —
    never from a rendered view of it: `render_kinds`/`render_digest` already
    read the same structure this way, and a hand-grep over either one's
    OUTPUT would be a partial or transformed view standing in for the
    source (the paraphrase-drift class's ASSERTION-site shape).

    Every count comes back paired with its own denominator's INPUT (the
    total), never printed alone — `render_structure` is what actually joins
    them into "N of M" text (lc-172: a bare count cannot tell a small
    numerator from a small population).

    A malformed kind body (not an object) counts as `other` and as
    undeclared-in-full, the same verdict `_validate_kind` reaches for it
    (every one of the seven stages is undeclared when there is no body to
    hold them).
    """
    kinds = doc.get("kinds")
    if not isinstance(kinds, dict):
        kinds = {}
    verb = session = other = 0
    both = 0
    undeclared = 0
    for body in kinds.values():
        if not isinstance(body, dict):
            other += 1
            undeclared += 1
            continue
        writer = body.get("writer")
        bucket = _writer_bucket(writer)
        if bucket == "verb":
            verb += 1
            # THE OVERLAP, COUNTED RATHER THAN HIDDEN. `_writer_bucket` puts
            # a kind written by BOTH a verb and the session in the `verb`
            # bucket, deliberately: partial self-administration is the
            # property this split predicts, and that call is right. What is
            # NOT right is letting the resulting labels overstate it. The
            # buckets are exclusive while the underlying fact is not —
            # `ledger lines` is `verb:ledger add, session` — so a reader
            # seeing "N session" reads "N kinds have a session writer" when
            # the honest reading is "N kinds have ONLY a session writer",
            # and one more has a session writer besides a verb.
            # This is the same arity shape lc-224 found one field over: a
            # per-kind scalar cannot describe a multi-valued field, and the
            # state the vocabulary cannot express renders as a neighbouring
            # one that reads as ordinary. There it forced a per-entry
            # sub-field; here the buckets stay and the overlap is simply
            # made visible, because the bucketing itself is sound and only
            # its silence was not.
            if any(t == "session" for t, _ in parse_refs([writer or ""])):
                both += 1
        elif bucket == "session":
            session += 1
        else:
            other += 1
        if any(stage not in body for stage in KIND_STAGES):
            undeclared += 1
    return {
        "total": len(kinds),
        "verb": verb,
        "session": session,
        "other": other,
        "both": both,
        "undeclared": undeclared,
    }


def render_structure(doc: dict) -> list[str]:
    """The session-start STRUCTURE line(s) — lc-174's done-criterion.

    A READOUT, never a refusal (MUST-NOT-MOVE, law 11): it prints the three
    counts whatever they are and exits clean regardless — a repo with a
    perfectly clean declaration prints its counts with denominators and
    never a bare silence, the same standard `render_kinds`/`render_digest`
    already hold for an empty declaration.
    """
    s = structure_summary(doc)
    total = s["total"]
    # THE SESSION BUCKET IS SPELLED "session-only" AND THE OVERLAP IS NAMED.
    # The buckets are exclusive; the fact underneath is not. A kind written
    # by both a verb and the session sits in the verb bucket (deliberately —
    # partial self-administration is what this split predicts), so calling
    # the other bucket "writer:session" invites the reading "this many kinds
    # have a session writer", which is short by exactly the overlap. The
    # word and the trailing clause are the whole repair: no count moves.
    both = s.get("both", 0)
    split = (f"writer split: {s['verb']} of {total} verb-written, "
             f"{s['session']} of {total} session-only, "
             f"{s['other']} of {total} other")
    if both:
        split += (f" — {both} of the verb-written also name session, so "
                  f"{s['session'] + both} of {total} carry a session writer "
                  f"in all")
    return [
        f"kinds registered: {total}",
        split,
        f"stage undeclared: {s['undeclared']} of {total}",
    ]


#: How old a recorded `kind moments` result may be before the banner calls it
#: STALE. Not a freshness policy and not enforcement: the line reports the age
#: either way, and the word exists so a reader scanning a banner sees the one
#: that has drifted without doing date arithmetic in their head.
MOMENTS_STALE_DAYS = 7


def render_moments_line(repo) -> list[str]:
    """The W1 act-2 banner line: the LAST `kind moments` run, with its date.

    A NAMED-STALE CARRIER, and every word of that matters. The line reports
    a PAST run, never the present state — nothing here evaluates a moment —
    so it carries the run's DATE and says when that date is old. A banner
    line that printed yesterday's verdict in the present tense would be a
    label standing over a body it no longer describes.

    MACHINE-LOCAL AND BEST-EFFORT, STATED IN THE LINE ITSELF. The carrier is
    the fire log under `$XDG_STATE_HOME`: it does not travel with the repo.
    On another machine, or after a lost write, the honest rendering is "no
    recorded run on this machine" — which is what this prints, and it claims
    NO MORE THAN THAT. It is not "the moments are fine" and it is not "the
    moments are broken"; the project-scoped truth is the verb's own output
    at run time, and this line never stands in for it.

    THE REACH NUMBERS TRAVEL WITH THE PROBLEM COUNTS. A stored "0 broken, 0
    malformed" says nothing on its own — a run that executed no predicate
    produces exactly that — so the line carries how many moments were
    declared and how many actually ran, the same pair the verb's own verdict
    refuses to print without.
    """
    rec = firelog.last_run("kind moments", repo)
    if rec is None:
        return ["moments: no recorded run on this machine — the carrier is "
                "the machine-local fire log, so this is a fact about THIS "
                "machine and not about the repo's moments. `lifecycle kind "
                "moments` answers now."]
    at = str(rec.get("at", ""))
    day = at.split("T")[0] if "T" in at else at
    detail = str(rec.get("detail") or "")
    fields = dict(
        part.split("=", 1) for part in detail.split() if "=" in part)

    def _n(key):
        try:
            return int(fields[key])
        except (KeyError, ValueError):
            return None

    broken, malformed = _n("broken"), _n("malformed")
    entries, declared = _n("entries"), _n("declared")
    derived, executed = _n("derived"), _n("executed")
    age = ""
    try:
        from datetime import date as _date
        d = _date.fromisoformat(day)
        days = (_date.today() - d).days
        if days >= MOMENTS_STALE_DAYS:
            age = f" — STALE, {days} day(s) old"
        elif days > 0:
            age = f" — {days} day(s) old"
    except ValueError:
        pass
    if broken is None or malformed is None:
        # A RECORD WITH NO PARSEABLE COUNTS is not a clean run. It is a
        # record this build cannot read, which is its own answer: rendering
        # it as zeros would invent a verdict out of a formatting change.
        return [f"moments: a run is recorded for {day or 'an unknown date'} "
                "whose result this build could not parse, so it reports no "
                f"counts{age}. Re-run `lifecycle kind moments`."]
    reach = ""
    if declared is not None and executed is not None:
        if derived is not None and entries is not None:
            reach = (f"; {entries} reader entries — {declared} declared, "
                     f"{derived} derived, {executed} executed")
        elif derived is not None:
            reach = (f"; {declared} declared moment(s), {derived} derived, "
                     f"{executed} executed")
        else:
            reach = f"; {declared} declared moment(s), {executed} executed"
        reach += (" — no predicate ran, so this verdict is about the "
                  "declaration only" if executed == 0 else "")
    if broken or malformed:
        return [f"moments: LAST RUN {day} found {broken} broken, "
                f"{malformed} malformed{reach}{age}"]
    return [f"moments: LAST RUN {day} clean — 0 broken, 0 malformed"
            f"{reach}{age}"]
