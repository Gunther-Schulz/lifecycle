"""The kind registry: `.claude/lifecycle.json`, its schema, and its reader.

THE PRIMITIVE IS THE KIND, NOT THE ITEM (design §3.0). Every kind of thing a
repo persists is registered with six declared stages:

    home · writer · reader · staleness · exit · growth

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
SCHEMA_FLOOR = 2

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

#: The six stages, closed. `kind_stage_undeclared` is a finding for any kind
#: missing any of them, which is why this tuple is the single source and no
#: check below restates it.
KIND_STAGES = ("home", "writer", "reader", "staleness", "exit", "growth")

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
    if "delegation" in doc and doc["delegation"] not in DELEGATION_VALUES:
        res.add("declaration_malformed",
                f"`delegation` must be one of {', '.join(DELEGATION_VALUES)}"
                f", got {doc['delegation']!r}. Optional (absent means "
                "\"none\" — no active delegation); the wave-3 Stop-hook "
                "detector is what reads it.")

    lanes = doc.get("lanes")
    if "lanes" in doc:
        if not isinstance(lanes, list) or not all(
                isinstance(x, str) and x.strip() for x in lanes):
            res.add("declaration_malformed",
                    "`lanes` must be a list of lane names (possibly empty).")
            lanes = []
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

    if repo is not None and isinstance(doc.get("laws"), str) and doc["laws"].strip():
        check_laws_present(repo, doc["laws"], res)
    if repo is not None:
        check_schema_agreement(repo, doc, res)


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


def _validate_kind(name: str, body, res: Result, world) -> None:
    if not isinstance(body, dict):
        res.add("kind_stage_undeclared",
                f"kind {name!r} is {type(body).__name__}, not an object, so "
                f"all six stages ({', '.join(KIND_STAGES)}) are undeclared.")
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
        if not isinstance(reader, list) or not reader or not all(
                isinstance(r, str) and r.strip() for r in reader):
            res.add("declaration_malformed",
                    f"kind {name!r}: `reader` must be a non-empty list of "
                    "non-empty strings. A kind nothing reads is the "
                    "registry's own recorded defect — it accumulates "
                    "forever and no gate ever looks at it.")
        else:
            _check_typed_refs(name, "reader", reader, res, world)

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

    growth = body.get("growth")
    if "growth" in body:
        if not isinstance(growth, str) or not growth.strip():
            res.add("declaration_malformed",
                    f"kind {name!r}: `growth` must be one of "
                    f"{', '.join(GROWTH_MODES)}.")
        else:
            mode = growth.strip().split()[0].strip(":,—-").lower()
            if mode not in GROWTH_MODES:
                res.add("declaration_malformed",
                        f"kind {name!r}: `growth` must BEGIN with one of "
                        f"{', '.join(GROWTH_MODES)}, got {growth!r}. The "
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


def plugin_hooks() -> frozenset:
    """Every git hook the plugin DECLARES in `plugin.json` (§3.8c, the seam).

    Read from the plugin's own manifest rather than from the machine: a hook
    that exists on this disk and is declared nowhere is the registration
    nobody can find, and a hook declared and absent is the one that silently
    never fires. The manifest is the declaration; the dispatcher registration
    is the wiring, and they are different failures.
    """
    manifest = Path(__file__).resolve().parents[2] / ".claude-plugin" / "plugin.json"
    try:
        doc = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return frozenset()
    hooks = doc.get(PLUGIN_GIT_HOOKS_KEY)
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
    def kind_home(kind):
        body = (doc.get("kinds") or {}).get(kind)
        h = body.get("home") if isinstance(body, dict) else None
        return h if isinstance(h, str) and h.strip() and "*" not in h else None

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
    return out


def carrier_schema(path: Path):
    """`(n, why-not)` — the `schema:` a carrier head declares.

    Comment lines before the schema line are SKIPPED rather than refused
    (§3.8c): a public `LEDGER.md` must be able to say what it is for, and a
    parser that demanded the version on line 1 forced a carrier in a public
    tree to be exactly `schema: 1` and nothing else.
    """
    if not path.is_file():
        return None, f"{path.name} is not present"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"{path.name} could not be read ({exc!r})"
    for raw in text.split("\n"):
        s = raw.strip()
        if not s or s.startswith("#") or s.startswith("<!--"):
            continue
        head, colon, val = s.partition(":")
        if colon and head.strip() == "schema":
            try:
                return int(val.strip()), None
            except ValueError:
                return None, (f"{path.name}'s `schema:` value {val.strip()!r} "
                              "is not an integer")
        return None, f"{path.name} carries no `schema:` head line"
    return None, f"{path.name} carries no `schema:` head line"


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
        n, why = carrier_schema(repo / home)
        if n is None:
            res.cannot_verify(
                f"the `{kind}` carrier's schema line could not be read, so "
                f"one-schema-per-repo was not checked for it: {why}.")
            continue
        if n != declared:
            res.add("schema_mismatch",
                    f"the declaration is stamped schema {declared} and the "
                    f"`{kind}` carrier {home!r} is stamped {n}. ONE schema "
                    "version per repo (§3.8c): one number, one command per "
                    "bump. Two numbers for one fact diverge from the moment "
                    "they disagree, and each reader resolves through "
                    "whichever it opened. Run `lifecycle migrate "
                    f"--schema-from {min(n, declared)}`.")


# --- rendering ---------------------------------------------------------------

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
