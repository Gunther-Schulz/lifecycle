"""The kind registry: `.claude/lifecycle.json`, its schema, and its reader.

THE PRIMITIVE IS THE KIND, NOT THE ITEM (design §3.0). Every kind of thing a
repo persists is registered with six declared stages:

    home · writer · reader · staleness · exit · bound

and a kind with an UNDECLARED STAGE is a checker finding. That is the whole
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
SCHEMA_FLOOR = 1

#: Where the declaration lives, relative to the repo root. Tracked; the
#: install step adds the `.gitignore` negation and this reader fails on an
#: ignored declaration (§3.0 — G1's recorded defect, closed once per repo
#: family rather than once per repo).
DECLARATION_REL = Path(".claude") / "lifecycle.json"

#: §3.4. `unattended` is designed-for and PARKED — it is a legal declared
#: value, and the machinery behind it is wave 3's.
TRIGGER_POLICIES = ("on-demand", "advise", "auto", "unattended")

#: §3.0 — writer is one of these three, whatever detail follows.
WRITER_ROLES = ("tool", "session", "producer")

#: §3.0 — exit is one of these four, WITH the recording act.
EXIT_ACTIONS = ("move", "compact", "delete", "never")

#: The six stages, closed. `kind_stage_undeclared` is a finding for any kind
#: missing any of them, which is why this tuple is the single source and no
#: check below restates it.
KIND_STAGES = ("home", "writer", "reader", "staleness", "exit", "bound")

#: Top-level keys every declaration carries. An EMPTY declared list is not the
#: same as an ABSENT key — absent is a finding, empty is a stated fact — so
#: `lanes` and `template-bindings` are required even where a repo has none.
REQUIRED_KEYS = (
    "schema", "id-prefix", "public", "laws", "closure-home", "trigger-policy",
    "goals", "ready-cap", "head-rule", "lanes", "template-bindings", "kinds",
)

#: §3.3. The laws file is required reading at every session start, so its size
#: is the injected-prefix budget. The cap is the mechanism; "laws, never
#: method" is the judgment and is labelled prose-rest.
LAWS_CAP_LINES = 60


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

    cap = doc.get("ready-cap")
    if "ready-cap" in doc and (not isinstance(cap, int) or isinstance(cap, bool) or cap < 1):
        res.add("declaration_malformed",
                f"`ready-cap` must be a positive integer, got {cap!r}. It "
                "bounds the SCHEDULED head, not the carrier.")

    hr = doc.get("head-rule")
    if "head-rule" in doc:
        if not isinstance(hr, dict) or "lead-goal" not in hr:
            res.add("declaration_malformed",
                    "`head-rule` must be an object carrying `lead-goal` — "
                    "the goal whose items lead the head whenever one is "
                    "complete, or the string \"none\".")
        elif hr["lead-goal"] != "none" and hr["lead-goal"] not in goals:
            res.add("dangling_reference",
                    f"`head-rule.lead-goal` names {hr['lead-goal']!r}, which "
                    "is not one of the declared goals. A head rule keyed to "
                    "a goal no item can carry never picks anything, and the "
                    "board renders as if it had.")

    lanes = doc.get("lanes")
    if "lanes" in doc:
        if not isinstance(lanes, list) or not all(
                isinstance(x, str) and x.strip() for x in lanes):
            res.add("declaration_malformed",
                    "`lanes` must be a list of lane names (possibly empty).")
            lanes = []
    lane_names = set(lanes) if isinstance(lanes, list) else set()

    if "template-bindings" in doc and not isinstance(doc["template-bindings"], dict):
        res.add("declaration_malformed",
                "`template-bindings` must be an object (possibly empty).")

    kinds = doc.get("kinds")
    if "kinds" in doc:
        if not isinstance(kinds, dict) or not kinds:
            res.add("declaration_malformed",
                    "`kinds` must be a non-empty object. A repo that "
                    "persists nothing needs no declaration; a repo that "
                    "persists something registers it.")
        else:
            for name, body in kinds.items():
                _validate_kind(name, body, res, lane_names)

    if repo is not None and isinstance(doc.get("laws"), str) and doc["laws"].strip():
        check_laws_cap(repo, doc["laws"], res)


def _validate_kind(name: str, body, res: Result, lane_names: set) -> None:
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
        elif writer.split()[0].strip(":,—-") not in WRITER_ROLES:
            res.add("declaration_malformed",
                    f"kind {name!r}: `writer` must begin with one of "
                    f"{', '.join(WRITER_ROLES)}, got {writer!r}.")

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
            _check_lane_refs(name, "reader", reader, res, lane_names)

    if isinstance(writer, str):
        _check_lane_refs(name, "writer", [writer], res, lane_names)

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

    bound = body.get("bound")
    if "bound" in body:
        if not isinstance(bound, str) or not bound.strip():
            res.add("declaration_malformed",
                    f"kind {name!r}: `bound` must be a count/size or "
                    "\"unbounded, declared why: …\".")
        elif bound.strip().lower().startswith("unbounded") and _needs_why(
                bound.strip(), "unbounded"):
            res.add("kind_stage_undeclared",
                    f"kind {name!r}: `bound` says \"unbounded\" with no "
                    "declared why.")


def _check_lane_refs(kind: str, stage: str, values, res: Result, lane_names: set) -> None:
    """`lane: <name>` in a reader/writer must name a declared lane.

    Referential integrity, from log4brains' build-time supersede-link check
    and Backstage's relation resolution. A declaration pointing at a lane
    that does not exist reads exactly like one pointing at a lane that does.
    """
    for v in values:
        for part in str(v).split(","):
            part = part.strip()
            if not part.lower().startswith("lane:"):
                continue
            lane = part.split(":", 1)[1].strip()
            if lane and lane not in lane_names:
                res.add("dangling_reference",
                        f"kind {kind!r}: `{stage}` names lane {lane!r}, "
                        "which is not in the declared `lanes` list.")


def check_laws_cap(repo: Path, laws_rel: str, res: Result) -> None:
    """The declared laws file, against the 60-line cap — from the WORKING TREE.

    THIS IS THE COULD-NOT-VERIFY CASE THE DESIGN NAMES EXPLICITLY. The laws
    file may be UNTRACKED by design (claude-code-cache-fix declares
    `CLAUDE.local.md`, which is untracked because the tracked `CLAUDE.md` is
    upstream's and non-binding there). A cap check that resolved the file
    through the git INDEX would see zero lines and report a clean 0 — an
    absence of evidence wearing a verdict's clothes. So this reads the
    working tree, and a file it cannot read is exit 3, never 0.
    """
    path = repo / laws_rel
    if not path.is_file():
        res.cannot_verify(
            f"the declared laws file {laws_rel!r} is not present in the "
            "working tree, so its line count could not be measured. This is "
            "COULD NOT VERIFY and not a clean zero — an absent file and a "
            "60-line-compliant file are not the same answer.")
        return
    try:
        n = len(path.read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeDecodeError) as exc:
        res.cannot_verify(f"the declared laws file {laws_rel!r} could not be "
                          f"read ({exc!r}).")
        return
    if n > LAWS_CAP_LINES:
        res.add("laws_over_cap",
                f"the declared laws file {laws_rel!r} is {n} lines, over the "
                f"cap of {LAWS_CAP_LINES}. The cap is the mechanism behind "
                "\"laws, never method\": it is injected at every session "
                "start, so its size is the prefix budget.")


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
