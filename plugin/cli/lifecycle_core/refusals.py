"""The refusal table, executable — ONE source for two consumers.

The design's §3.9 table is wave 1's acceptance test AND the plugin's `--test`
roster, and it says so explicitly: one source for both. So the rows live here
as FIRING INPUTS that can be run, not as prose that can be read. A row
restated in a test file and again in a roster is two bodies for one fact, and
they diverge.

WHAT A ROW PROMISES. `expect` is the exit code the firing input must produce.
That is the discriminating half: an assertion that "something happened"
separates nothing, because the correct and the defective behaviour both
satisfy it. A row is proven when its firing input produces `expect` AND a
clean control produces something else — every `fire()` below therefore builds
its own control alongside its plant, and the row's proof is the PAIR.

ROWS THIS BUILD DOES NOT CARRY are absent rather than stubbed green. Wave 1
stages 4-9 add theirs. A row that cannot be fired at all is labelled
PROSE_REST with its reason and is never deleted to make a roster green.

`--test` (stage 8) is the printer over this list. It does not exist yet; the
list does, and `test/test_refusals.py` executes it today.
"""

import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from . import exits
from . import declaration as decl
from . import items as items_mod
from . import ledger as ledger_mod

#: A declaration that is VALID in every respect, used as the control every
#: row mutates exactly one thing away from. Derived from the design's own
#: stage list, never read back out of a real repo's file.
GOOD_DECLARATION = {
    "schema": 2,
    "id-prefix": "xx",
    "public": True,
    "laws": "LAWS.md",
    "closure-home": "ITEMS-DONE.md",
    "trigger-policy": "on-demand",
    "goals": ["see", "attribute", "mitigate", "verify", "retire"],
    "head-rule": {"lead-goal": "mitigate"},
    "lanes": [],
    "template-bindings": {},
    "leak-scan": {"source-scope-foreign-path": True},
    "kinds": {
        "items": {
            "home": "ITEMS.md",
            "writer": "verb:item add, verb:item park, verb:item close",
            "reader": ["verb:item ready", "verb:item ratio"],
            "staleness": "change-coupling — the cited record no longer resolves",
            "exit": {"action": "move",
                     "recording-act": "the item close fire-log line"},
            "growth": "bounded-by-exit — every item leaves by a recorded "
                      "closure or a recorded drop",
        },
    },
}

GOOD_ITEMS = """schema: 2
baseline: 0

## xx-1
grade: READY
requirement: the control block, valid in every slot — record: LEDGER.md
goal: mitigate
write-set: tools/thing.py
done-criterion: the check goes red on the real defect and green after
evidence: none yet
blocked-by: NONE
"""


@dataclass
class Fired:
    code: int
    output: str


@dataclass
class Row:
    #: Matches the `row` field a Finding carries, so the finding and the
    #: roster entry that proves it have one name rather than two.
    ident: str
    #: The design's own wording for the refusal or state.
    refusal: str
    #: The design's own wording for the firing input.
    firing_input: str
    #: What the firing input must exit.
    expect: int
    #: Plant, and control. Both run; the pair is the proof.
    fire: Callable[[], Fired]
    control: Callable[[], Fired]
    stage: str = "wave 1, stages 1-3"
    #: THE ROUTE SET (§3.8c): the closed vocabulary this refusal's own TEXT
    #: names. Read from the DESIGN's side — a declared tuple in the module the
    #: refusal defends — never from the resolver it grades. An expectation
    #: derived from the artifact it grades moves with the mutant.
    route_set: tuple = ()
    #: How the routes the CODE actually watches are DERIVED FROM THE SOURCE,
    #: exactly as the emit-site check derives sites. A row declaring a route
    #: set without this would be comparing a claim against itself.
    routes_watched: Callable[[], set] | None = None
    #: Set only where a roster row is NOT one-to-one with a FINDING row —
    #: two roster rows can prove two firing inputs of ONE refusal (the
    #: ignored declaration, tracked and untracked). Declared rather than
    #: derived from the ident by string surgery: a `split()` over a label is
    #: a prefix match in an equality's costume, and it silently returns the
    #: whole ident for every ident lacking the magic substring — which reads
    #: as "no mapping needed" whether or not one is.
    finding_row: str | None = None

    @property
    def expected_finding_row(self) -> str:
        return self.finding_row or self.ident


# --- scratch scaffolding -----------------------------------------------------

class _Scratch:
    """A throwaway git repo carrying a declaration and a carrier file.

    A real `git init`, because two rows turn on what git can SEE: an ignored
    declaration is invisible to `check-ignore` in anything but a work tree,
    and a fake would report the answer we hoped for.
    """

    def __init__(self, *, declaration=None, gitignore=None, laws_lines=None,
                 items_text=None, declaration_raw=None, track=False):
        self.dir = Path(tempfile.mkdtemp(prefix="lifecycle-row-"))
        self._run(["git", "init", "-q", "-b", "main"])
        # No hooks from the machine's global core.hooksPath: this scratch repo
        # is an instrument, and an unrelated gate firing inside it would be
        # read as the row's own verdict.
        self._run(["git", "config", "core.hooksPath", str(self.dir / ".nohooks")])
        self._run(["git", "config", "user.email", "row@lifecycle.invalid"])
        self._run(["git", "config", "user.name", "refusal row"])
        if gitignore is not None:
            (self.dir / ".gitignore").write_text(gitignore, encoding="utf-8")
        if declaration is not None or declaration_raw is not None:
            (self.dir / ".claude").mkdir(exist_ok=True)
            body = (declaration_raw if declaration_raw is not None
                    else json.dumps(declaration, indent=2))
            (self.dir / ".claude" / "lifecycle.json").write_text(body, encoding="utf-8")
        if laws_lines is not None:
            (self.dir / "LAWS.md").write_text(
                "\n".join(f"law {i}" for i in range(laws_lines)) + "\n",
                encoding="utf-8")
        # THE CARRIERS ARE SEEDED BY DEFAULT, at the declaration's own schema.
        # One schema version per repo (§3.8c) is checked over the CARRIERS, so
        # a scratch repo with no carriers answers COULD NOT VERIFY for that
        # question and every declaration row's control degrades from CLEAN to
        # code 3 — a control that differs from its plant for the wrong reason,
        # which is a pair that has stopped discriminating.
        (self.dir / "ITEMS.md").write_text(
            items_text if items_text is not None else EMPTY_ITEMS,
            encoding="utf-8")
        (self.dir / "ITEMS-DONE.md").write_text(EMPTY_DONE, encoding="utf-8")
        (self.dir / "LEDGER.md").write_text(ledger_mod.head_text(),
                                            encoding="utf-8")
        if track:
            # `-f` because the plant's whole point is a path git is ignoring:
            # a plain `git add` there is silently a no-op, and the row would
            # then be measuring an UNTRACKED repo while claiming a tracked
            # one — the plant missing its target and reading as a pass.
            self._run(["git", "add", "-f", ".claude/lifecycle.json",
                       ".gitignore"])
            self._run(["git", "commit", "-qm", "declaration tracked"])

    def _run(self, argv):
        subprocess.run(argv, cwd=str(self.dir), capture_output=True, text=True)

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def _decl_run(**kw) -> Fired:
    """Read a scratch repo's declaration and render the verdict as a CLI would."""
    with _Scratch(**kw) as s:
        if kw.get("track"):
            # ANTI-VACUITY. A `git commit` that silently failed would leave an
            # UNTRACKED repo, where the tracked-case rows below degrade into
            # the untracked row that already passes — the plant missing its
            # target while the roster stays green. So the premise is pinned
            # INSIDE the row rather than assumed from the setup code.
            ls = subprocess.run(
                ["git", "-C", str(s.dir), "ls-files", "--error-unmatch",
                 ".claude/lifecycle.json"], capture_output=True, text=True)
            if ls.returncode != 0:
                return Fired(-1, "SETUP FAILED: the declaration is not "
                                 "tracked, so this row measured an untracked "
                                 f"repo. git said: {ls.stderr.strip()!r}")
        res = decl.read(s.dir)
        lines = [f"FINDING [{f.row}] {f.message}" for f in res.findings]
        lines += [f"COULD NOT VERIFY: {u}" for u in res.unverified]
        lines.append(f"kind check: {exits.word(res.code)}")
        return Fired(res.code, "\n".join(lines))


def _items_run(items_text: str, prefix: str = "xx") -> Fired:
    with _Scratch(items_text=items_text) as s:
        buf = []
        code = items_mod.check_file(s.dir / "ITEMS.md", buf.append, prefix=prefix)
        return Fired(code, "\n".join(buf))


def _done_run(done_text: str, prefix: str = "xx") -> Fired:
    """The DONE HOME's own shape check, over a scratch closure home."""
    with _Scratch() as s:
        p = s.dir / "ITEMS-DONE.md"
        p.write_text(done_text, encoding="utf-8")
        buf = []
        code = items_mod.check_done_file(p, buf.append, prefix=prefix)
        return Fired(code, "\n".join(buf))


#: A laws file written to the discipline: a numbered law list, each law's
#: basis a ONE-LINE journal pointer. Deliberately longer than the 60-line cap
#: R22 withdrew — the replacement checks SCOPE, and a long well-scoped laws
#: file is correct.
LAWS_CLEAN = (
    "# repo — working discipline\n\n"
    "This file is this repo's declared LAWS file. Laws bind; they do not\n"
    "explain themselves. Every law cites a dated entry in the JOURNAL.\n\n"
    "## The LAWS\n\n"
    + "".join(f"{i}. A law, stated as one binding sentence. (J{i})\n"
             for i in range(1, 61))
    + "\n")

#: The same file with ONE mis-homed paragraph appended: an incident with its
#: date and its measured figure, which belongs in the JOURNAL and in an AUDIT.
LAWS_WITH_INCIDENT = LAWS_CLEAN + (
    "\n## Why law 12 exists\n\n"
    "On 2026-08-11 the declared head reached 12 against a cap of 10 and the\n"
    "push was refused; the repair regraded two entries, so the cap fought\n"
    "the grading rather than the growth.\n")


def _laws_audit_run(laws_text: str) -> Fired:
    """The laws scope audit over a scratch repo's declared laws file."""
    from . import retire as retire_mod
    with _Scratch() as s:
        (s.dir / "LAWS.md").write_text(laws_text, encoding="utf-8")
        buf = []
        code = retire_mod.laws_scope_audit(s.dir, "LAWS.md", buf.append)
        return Fired(code, "\n".join(buf))


# --- the rows ----------------------------------------------------------------

def _kind_missing_exit() -> dict:
    d = json.loads(json.dumps(GOOD_DECLARATION))
    del d["kinds"]["items"]["exit"]
    return d


def _kind_lane_nope() -> dict:
    d = json.loads(json.dumps(GOOD_DECLARATION))
    d["kinds"]["items"]["reader"] = ["lane: nope"]
    return d


_GOOD_KW = dict(declaration=GOOD_DECLARATION, gitignore="", laws_lines=10)

ROWS = [
    Row(
        ident="declaration_absent",
        refusal="public undeclared — a repo with no declaration",
        firing_input="a repo with no `.claude/lifecycle.json` at all",
        expect=exits.FINDING,
        fire=lambda: _decl_run(gitignore="", laws_lines=10),
        control=lambda: _decl_run(**_GOOD_KW),
    ),
    Row(
        ident="declaration_malformed",
        refusal="public undeclared — a malformed declaration",
        firing_input="`.claude/lifecycle.json` whose bytes are not valid JSON",
        expect=exits.FINDING,
        fire=lambda: _decl_run(declaration_raw='{"schema": 1, "public":',
                               gitignore="", laws_lines=10),
        control=lambda: _decl_run(**_GOOD_KW),
    ),
    Row(
        ident="declaration_malformed_missing_key",
        finding_row="declaration_malformed",
        refusal="public undeclared — `public` absent, so the repo is neither "
                "declared public nor declared private",
        firing_input="a declaration with the `public` key removed",
        expect=exits.FINDING,
        fire=lambda: _decl_run(
            declaration={k: v for k, v in GOOD_DECLARATION.items() if k != "public"},
            gitignore="", laws_lines=10),
        control=lambda: _decl_run(**_GOOD_KW),
    ),
    Row(
        ident="declaration_ignored",
        refusal="ignored declaration",
        firing_input="`.gitignore` swallowing `lifecycle.json` (`.claude/*` "
                     "with no negation)",
        expect=exits.FINDING,
        fire=lambda: _decl_run(declaration=GOOD_DECLARATION,
                               gitignore=".claude/*\n", laws_lines=10),
        # The SAME .gitignore shape WITH the negation — so the control
        # differs from the plant in exactly the one line under test, not in
        # whether a .gitignore exists at all.
        control=lambda: _decl_run(
            declaration=GOOD_DECLARATION,
            gitignore=".claude/*\n!.claude/lifecycle.json\n", laws_lines=10),
    ),
    Row(
        ident="declaration_ignored_tracked",
        finding_row="declaration_ignored",
        refusal="ignored declaration — the TRACKED case, which is every "
                "declaration a real repo has once it is committed",
        firing_input="`.gitignore` swallowing `lifecycle.json` with the "
                     "declaration COMMITTED (`.claude/*`, no negation)",
        expect=exits.FINDING,
        # WHY THIS ROW EXISTS. The shipped `ignored_by_git` omitted
        # `--no-index`, so `check-ignore` skipped the tracked path, exited 1,
        # and `kind check` reported CLEAN over exactly the misconfiguration it
        # exists to catch. Measured before the fix: plant CLEAN/0, control
        # CLEAN/0 — the two indistinguishable. Today's roster covered only the
        # untracked case, which is why a real defect had no row.
        fire=lambda: _decl_run(declaration=GOOD_DECLARATION,
                               gitignore=".claude/*\n", laws_lines=10,
                               track=True),
        # The control differs in the ONE line under test — the negation — and
        # is tracked exactly as the plant is, so trackedness cannot be what
        # separates them.
        control=lambda: _decl_run(
            declaration=GOOD_DECLARATION,
            gitignore=".claude/*\n!.claude/lifecycle.json\n", laws_lines=10,
            track=True),
    ),
    Row(
        ident="kind_stage_undeclared",
        refusal="a kind with an undeclared stage",
        firing_input="a registry row missing `exit`",
        expect=exits.FINDING,
        fire=lambda: _decl_run(declaration=_kind_missing_exit(),
                               gitignore="", laws_lines=10),
        control=lambda: _decl_run(**_GOOD_KW),
    ),
    Row(
        ident="dangling_reference",
        refusal="dangling typed reference in the declaration",
        firing_input="a `lifecycle.json` row naming `lane: nope`",
        expect=exits.FINDING,
        fire=lambda: _decl_run(declaration=_kind_lane_nope(),
                               gitignore="", laws_lines=10),
        control=lambda: _decl_run(**_GOOD_KW),
    ),
    Row(
        # `laws_over_cap` IS GONE, not renamed. R22 withdrew the 60-line cap
        # outright: a laws file may need 200 lines and the only question is
        # whether every line is a law. This row is its REPLACEMENT and it
        # checks a different property — SCOPE, not size — so the size figure
        # it prints decides nothing and no input can make it fire on length.
        ident="laws_scope_audit",
        refusal="a line in the declared laws file carries ANOTHER KIND's "
                "marker — a numbered step sequence (workflow), a dated "
                "incident (journal), a measured figure with a unit (audit), a "
                "file:line citation wrapped in explanation (journal). "
                "POSSIBLY mis-homed: a finding for review, never a refusal, "
                "since the same markers appear legitimately inside a law's "
                "one-line basis pointer",
        firing_input="a laws file whose law list is followed by a dated "
                     "incident paragraph",
        expect=exits.FINDING,
        fire=lambda: _laws_audit_run(LAWS_WITH_INCIDENT),
        # The SAME laws file with the incident paragraph removed: the arms
        # differ in the mis-homed prose alone, not in whether the file has a
        # law list — and the control is 40 lines longer than the retired cap,
        # which is the point of the replacement.
        control=lambda: _laws_audit_run(LAWS_CLEAN),
    ),
    Row(
        ident="laws_absent_could_not_verify",
        refusal="the laws file the declaration names is not in the working "
                "tree — COULD NOT VERIFY, never a clean zero",
        firing_input="a declaration naming a laws file that is not there "
                     "(the shape an index-resolved cap check reports as 0)",
        expect=exits.COULD_NOT_VERIFY,
        fire=lambda: _decl_run(declaration=GOOD_DECLARATION, gitignore=""),
        control=lambda: _decl_run(**_GOOD_KW),
    ),
    Row(
        ident="schema_above_floor",
        refusal="schema above floor",
        firing_input="`schema: <n+1>` in the carrier head",
        expect=exits.FINDING,
        fire=lambda: _items_run(
            GOOD_ITEMS.replace(f"schema: {items_mod.SCHEMA_FLOOR}",
                       f"schema: {items_mod.SCHEMA_FLOOR + 1}", 1)),
        control=lambda: _items_run(GOOD_ITEMS),
    ),
    Row(
        ident="item_shape",
        refusal="item written outside the tool",
        firing_input="a hand-edited block missing a slot",
        expect=exits.FINDING,
        fire=lambda: _items_run(
            "\n".join(l for l in GOOD_ITEMS.split("\n")
                      if not l.startswith("evidence:"))),
        control=lambda: _items_run(GOOD_ITEMS),
    ),
    Row(
        ident="duplicate_id",
        refusal="duplicate on move (a crash between the append and the commit)",
        firing_input="two copies of one id in the carrier",
        expect=exits.FINDING,
        fire=lambda: _items_run(GOOD_ITEMS + "\n" + GOOD_ITEMS.split("\n\n", 1)[1]),
        control=lambda: _items_run(GOOD_ITEMS),
    ),
    Row(
        ident="unknown_grade_read",
        refusal="unknown grade word READ (merge / old tool) — the census's "
                "third answer, not a crash and not folded into open or closed",
        firing_input="a file line with `grade: FOO`",
        expect=exits.COULD_NOT_VERIFY,
        fire=lambda: _items_run(GOOD_ITEMS.replace("grade: READY", "grade: FOO")),
        control=lambda: _items_run(GOOD_ITEMS),
    ),
]

#: Rows the design names that THIS build cannot fire, each with why. Labelled,
#: never deleted — a roster that dropped them would report a completeness it
#: does not have.
PROSE_REST = [
    # RETIRED FROM THIS LIST IN STAGES 4-6, each now an executable row above:
    # "unknown grade word on write" -> `unknown_grade_write`;
    # "PARKED without a typed blocker" -> `parked_without_typed_blocker`;
    # "conservation short" -> `conservation_short`;
    # "dangling typed reference", ITEM half -> `dangling_reference_item`;
    # "public repo, foreign-origin item" -> `foreign_origin_item`, which was
    # in NEITHER list before stage 4 — a §3.9 row that was neither fired nor
    # labelled, which is the one state this list exists to make impossible.
    # RETIRED FROM THIS LIST IN STAGE 7, each now an executable row below:
    # "trigger BROKEN" -> `trigger_broken`;
    # "roster absent / repo unresolved" -> `roster_absent` and
    # `repo_unresolved`, which are two firing inputs the design's single
    # table cell names together and this roster fires apart.
    ("lane body over one screen", "lanes' BODIES are wave 2 — this build "
                                  "parses `Trigger:` and reports the other "
                                  "three parts by presence, so it has no "
                                  "one-screen cap to fire"),
    ("unbound required slot", "template bindings are wave 2"),
    ("exact template duplication in a repo", "templates are wave 2"),
    ("detector without disposition", "the detector registry is wave 3"),
    # RETIRED FROM THIS LIST IN THE SCHEMA WAVE, now an executable row:
    # "unregistered persisted thing" -> `unregistered_persisted_thing`. §3.8c
    # brought the unregistered-file half of invariant 1 forward from wave 4
    # (`kind sweep`), so the row has a firing input and a control and is no
    # longer something this build cannot fire.
    ("version compare (`0.9` vs `0.11`)", "the plugin cache bound is wave 3"),
    ("leak scan on the plugin repo",
     "FIRES, but NOT on the input the design names. The scanner has no "
     "foreign-path class, so a planted `/home/<user>/…` path scans clean "
     "(measured, exit 0); the row was red-proven with a capture-key token "
     "instead (exit 2). Reported to the judgment desk — closing it is either "
     "a new scanner class or an amended row, and both are design decisions."),
    ("procedure text elsewhere; near-duplicate templates; laws-vs-method; the "
     "no-operator-quote rule; \"subagents never book\"",
     "the design's own prose-rest row: no predicate exists, operator is the "
     "backstop"),
]


# --- stages 4-6: a repo the CLI can actually be run against -------------------
#
# The rows above read modules directly, which was enough while every refusal
# lived inside one function. From stage 4 on, the refusals are properties of
# a VERB — the join, the cost test, the move, the conservation identity — and
# a row that called the checker function directly would exercise everything
# except the path a caller takes. So these rows run `cli.main`, in a real git
# work tree, and read the exit code the contract promises.

#: A declaration valid in every respect, with all three wave-1 kinds. Written
#: from the design's own stage list and D-h's assigned values, never read back
#: out of a repo: an expectation derived from the artifact it grades moves
#: with the mutant.
GOOD_FULL_DECLARATION = {
    "schema": 2, "id-prefix": "xx", "public": False, "laws": "LAWS.md",
    "closure-home": "ITEMS-DONE.md", "trigger-policy": "on-demand",
    "goals": ["see", "attribute", "mitigate", "verify", "retire"],
    "head-rule": {"lead-goal": "mitigate"},
    "lanes": [], "template-bindings": {},
    "leak-scan": {"source-scope-foreign-path": True},
    "kinds": {
        "items": {
            "home": "ITEMS.md",
            "writer": "verb:item add, verb:item park, verb:item close",
            "reader": ["verb:item ready", "verb:item ratio"],
            "staleness": "change-coupling — the cited record no longer resolves",
            "exit": {"action": "move",
                     "recording-act": "the item close fire-log line"},
            "growth": "bounded-by-exit — every item leaves by a recorded "
                      "closure or a recorded drop",
        },
        "done bodies": {
            "home": "ITEMS-DONE.md",
            "writer": "verb:item close",
            "reader": ["verb:item check", "verb:retire"],
            "staleness": "none, declared why: a closure record is history",
            "exit": {"action": "compact",
                     "recording-act": "a ledger decision line naming the range"},
            "growth": "compacted — done bodies fold on the retire lane's rule",
        },
        "ledger lines": {
            "home": "LEDGER.md",
            "writer": "verb:ledger add, session",
            "reader": ["verb:ledger rejected"],
            "staleness": "none, declared why: append-only decision history",
            "exit": {"action": "never", "recording-act": "compaction only"},
            "growth": "unbounded-with-reason — one line per decision event and "
                      "no bodies; the decision rate is the control",
        },
        # THE LAWS FILE IS A KIND. Registered here rather than left implicit:
        # `kind sweep` asks the world whether anything sits outside the
        # registry, and a fixture whose own laws file is unregistered makes
        # the sweep's CONTROL fire — a control going red for the fixture's
        # reason rather than the row's (J18's shape, one axis over).
        "laws": {
            "home": "LAWS.md",
            "writer": "session",
            "reader": ["session", "verb:audit"],
            "staleness": "change-coupling — a law whose journal pointer no "
                         "longer resolves has lost its basis",
            "exit": {"action": "never",
                     "recording-act": "a retirement is a ledger decision line "
                                      "naming the law and the evidence"},
            "growth": "unbounded-with-reason — no cap (R22); the control is "
                      "SCOPE, checked by the laws scope audit, and the size "
                      "is reported as a number",
        },
    },
}

#: A carrier head whose conservation identity balances against ONE live item.
SEED_ITEMS = """schema: 2
baseline: 1
added: 0
compacted: 0

## xx-1
grade: READY
requirement: the harvest timer double-fires on a rotated capture — LEDGER.md
goal: mitigate
write-set: tools/harvest.mjs
done-criterion: one fire per window, shown on the rotated fixture
evidence: none yet
blocked-by: NONE
"""

EMPTY_ITEMS = "schema: 2\nbaseline: 0\nadded: 0\ncompacted: 0\n"
EMPTY_DONE = "schema: 2\n"

#: A complete, valid `item add` — the argument baseline every row below
#: mutates exactly one thing away from. A row that built its own argument
#: list would drift from this one, and the drift would look like the row.
# Its requirement shares NO token with `SEED_ITEMS`, deliberately: the join
# is what most of these rows run through, and a baseline that matched the
# seed would fire `join_undisposed` in every control. Measured once by the
# control going red — the fixture was the suspect, not the verdict.
GOOD_ADD = [
    "item", "add",
    "--requirement", "the serving config is read from defaults — docs/x.md",
    "--goal", "verify",
    "--write-set", "tools/replay.mjs",
    "--done-criterion", "the gate reads what is serving",
    "--evidence", "none yet",
    "--hunks", "4",
    "--absence", "the decision belongs to a desk this session is not",
]


class _Repo:
    """A real git work tree with a declaration and both carrier homes."""

    def __init__(self, *, declaration=None, items=None, done=None,
                 ledger_text=None, public=None, lanes=None, lane_files=None,
                 fail_commit=False):
        self.dir = Path(tempfile.mkdtemp(prefix="lifecycle-verb-"))
        d = declaration if declaration is not None else GOOD_FULL_DECLARATION
        if public is not None or lanes is not None:
            d = json.loads(json.dumps(d))
            if public is not None:
                d["public"] = public
            if lanes is not None:
                d["lanes"] = list(lanes)
        self._run(["git", "init", "-q", "-b", "main"])
        # The machine's global core.hooksPath must not reach into an
        # instrument: an unrelated gate firing here would be read as this
        # row's own verdict.
        self._run(["git", "config", "core.hooksPath", str(self.dir / ".nohooks")])
        self._run(["git", "config", "user.email", "row@lifecycle.invalid"])
        self._run(["git", "config", "user.name", "refusal row"])
        (self.dir / ".claude").mkdir(exist_ok=True)
        (self.dir / ".claude" / "lifecycle.json").write_text(
            json.dumps(d, indent=2), encoding="utf-8")
        (self.dir / "LAWS.md").write_text("law\n", encoding="utf-8")
        (self.dir / "ITEMS.md").write_text(
            EMPTY_ITEMS if items is None else items, encoding="utf-8")
        (self.dir / "ITEMS-DONE.md").write_text(
            EMPTY_DONE if done is None else done, encoding="utf-8")
        (self.dir / "LEDGER.md").write_text(
            ledger_mod.head_text() if ledger_text is None else ledger_text,
            encoding="utf-8")
        for name, body in (lane_files or {}).items():
            (self.dir / "lanes").mkdir(exist_ok=True)
            (self.dir / "lanes" / f"{name}.md").write_text(body,
                                                           encoding="utf-8")
        self._run(["git", "add", "-A"])
        self._run(["git", "commit", "-qm", "seed"])
        if fail_commit:
            # Installed AFTER the seed commit, so the plant differs from its
            # control in the COMMIT step alone and not in whether the repo
            # has a history. A hook rather than a broken `.git`: removing
            # `.git` would also blind `check-ignore`, and the declaration
            # reader would answer COULD NOT VERIFY — a different verdict for
            # a different reason, which is the plant missing its target.
            hooks = self.dir / ".hooks"
            hooks.mkdir(exist_ok=True)
            hook = hooks / "pre-commit"
            hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
            hook.chmod(0o755)
            self._run(["git", "config", "core.hooksPath", str(hooks)])

    def _run(self, argv):
        subprocess.run(argv, cwd=str(self.dir), capture_output=True, text=True)

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def _cli(argv, *, cwd=None, **repo_kw) -> Fired:
    """Run one `lifecycle` invocation in a scratch repo. `cli` is imported
    HERE rather than at module scope: stage 8's `--test` will print this
    roster from inside `cli`, and a module-level import would close the
    cycle."""
    import io
    from contextlib import redirect_stdout
    from . import cli as cli_mod

    with _Repo(**repo_kw) as r:
        here = os.getcwd()
        try:
            os.chdir(str(cwd) if cwd else str(r.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(r.dir)] + list(argv))
            return Fired(code, buf.getvalue())
        finally:
            os.chdir(here)


def _cli_foreign(argv, **repo_kw) -> Fired:
    """Same, but run from INSIDE ANOTHER git repo — the foreign-origin arm."""
    with _Repo() as elsewhere:
        return _cli(argv, cwd=elsewhere.dir, **repo_kw)


def _mutate(text: str, old: str, new: str) -> str:
    assert old in text, f"the plant's anchor {old!r} is not in the text"
    return text.replace(old, new, 1)


VERB_ROWS = [
    Row(
        ident="unknown_grade_write",
        refusal="unknown grade word on write",
        firing_input="`item add --grade FOO`",
        expect=exits.FINDING,
        fire=lambda: _cli(GOOD_ADD + ["--grade", "FOO"]),
        control=lambda: _cli(GOOD_ADD + ["--grade", "READY"]),
        stage="wave 1, stage 4",
    ),
    Row(
        ident="foreign_origin_item",
        refusal="public repo, foreign-origin item",
        firing_input="`item add` from another repo's cwd against `public: true`",
        expect=exits.FINDING,
        fire=lambda: _cli_foreign(GOOD_ADD, public=True),
        # SAME public repo, SAME add — only the cwd differs, so origin is
        # what separates them and not the `public` flag.
        control=lambda: _cli(GOOD_ADD, public=True),
        stage="wave 1, stage 4",
    ),
    Row(
        ident="join_undisposed",
        refusal="intake is a MERGE: candidates found, no disposition given "
                "(§3.2 — the caller answers merge-into / supersede / new)",
        firing_input="an `item add` whose write-set path a live item already "
                     "carries, with no `--join`",
        expect=exits.FINDING,
        fire=lambda: _cli(
            _mutate_add("--write-set", "tools/harvest.mjs"), items=SEED_ITEMS),
        # The identical add against a carrier holding the SAME item under a
        # different write-set and different requirement words: the join runs
        # and finds nothing, so the refusal is the MATCH and not the join.
        control=lambda: _cli(GOOD_ADD, items=SEED_ITEMS),
        stage="wave 1, stage 4",
    ),
    Row(
        ident="new_without_absence",
        refusal="`new` is taken only with a named absence (§3.2)",
        firing_input="`item add` with no `--absence`",
        expect=exits.FINDING,
        fire=lambda: _cli([a for i, a in enumerate(GOOD_ADD)
                           if a != "--absence"
                           and GOOD_ADD[i - 1] != "--absence"]),
        control=lambda: _cli(GOOD_ADD),
        stage="wave 1, stage 4",
    ),
    Row(
        ident="cost_test_veto",
        refusal="the cost test — a one-file, one-hunk write-set with the "
                "session live is do-it-now, not book-it (§3.2)",
        firing_input="`item add --hunks 1` over a one-path write-set, "
                     "source session",
        expect=exits.FINDING,
        fire=lambda: _cli(_mutate_add("--hunks", "1")),
        # The SAME one-file one-hunk add, from the OPERATOR: the veto is
        # skipped, the join never is. So the arms differ in the source alone.
        control=lambda: _cli(_mutate_add("--hunks", "1")
                             + ["--source", "operator"]),
        stage="wave 1, stage 4",
    ),
    Row(
        ident="cost_test_unverified",
        refusal="the cost test could not be evaluated — one file named, hunk "
                "count not stated. COULD NOT VERIFY, never a pass",
        firing_input="`item add` over a one-path write-set with no `--hunks`",
        expect=exits.COULD_NOT_VERIFY,
        fire=lambda: _cli([a for i, a in enumerate(GOOD_ADD)
                           if a != "--hunks" and GOOD_ADD[i - 1] != "--hunks"]),
        control=lambda: _cli(GOOD_ADD),
        stage="wave 1, stage 4",
    ),
    Row(
        ident="blocker_untyped",
        refusal="a blocker that is prose rather than one of §3.1's three "
                "closed edge types",
        firing_input="`item add --blocked-by 'we should think about it'`",
        expect=exits.FINDING,
        fire=lambda: _cli(GOOD_ADD + ["--blocked-by",
                                      "we should think about it"]),
        control=lambda: _cli(GOOD_ADD + ["--blocked-by",
                                         "decision which window is canonical"]),
        stage="wave 1, stage 4",
    ),
    Row(
        ident="dangling_reference_item",
        finding_row="dangling_reference",
        refusal="dangling typed reference — `blocked-by <item-id>` naming an "
                "id no home holds (the ITEM half of §3.9's row; the "
                "declaration half is `dangling_reference` above)",
        firing_input="`item add --blocked-by xx-9999`",
        expect=exits.FINDING,
        fire=lambda: _cli(GOOD_ADD + ["--blocked-by", "xx-9999"],
                          items=SEED_ITEMS),
        control=lambda: _cli(GOOD_ADD + ["--blocked-by", "xx-1"],
                             items=SEED_ITEMS),
        stage="wave 1, stage 4",
    ),
    Row(
        ident="parked_without_typed_blocker",
        refusal="PARKED without a typed blocker",
        firing_input="`item park <id>` with prose only",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "park", "xx-1", "--blocked-by",
                           "we should think about it"], items=SEED_ITEMS),
        control=lambda: _cli(["item", "park", "xx-1", "--blocked-by",
                              "decision which window is canonical"],
                             items=SEED_ITEMS),
        stage="wave 1, stage 5",
    ),
    Row(
        ident="duplicate_id_cross_home",
        finding_row="duplicate_id",
        refusal="duplicate on move, ACROSS THE TWO HOMES — the within-file "
                "row above cannot see this one: a close appends to the done "
                "home and then deletes from the carrier, so the crash window "
                "leaves one copy in EACH file and no single-file check looks "
                "at both. DUPLICATE and RECOVERABLE, never loss",
        firing_input="one id present in BOTH homes",
        expect=exits.FINDING,
        # baseline 2 so CONSERVATION balances in both arms: without that the
        # plant would go red for two reasons and the row would not know
        # which one it proved.
        fire=lambda: _cli(
            ["item", "check"],
            items=_mutate(SEED_ITEMS, "baseline: 1", "baseline: 2"),
            done=EMPTY_DONE + "\n" + SEED_ITEMS.split("\n\n", 1)[1].replace(
                "grade: READY", "grade: DONE")),
        control=lambda: _cli(
            ["item", "check"],
            items=_mutate(SEED_ITEMS, "baseline: 1", "baseline: 2"),
            done=EMPTY_DONE + "\n" + SEED_ITEMS.split("\n\n", 1)[1].replace(
                "grade: READY", "grade: DONE").replace("## xx-1", "## xx-2")),
        stage="wave 1, stage 5",
    ),
    Row(
        ident="conservation_short",
        refusal="conservation short — a body left the carrier by a path that "
                "is not a closure",
        firing_input="a body deleted by hand → the delta fails",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "check"],
                          items=_mutate(SEED_ITEMS, "baseline: 1",
                                        "baseline: 2")),
        control=lambda: _cli(["item", "check"], items=SEED_ITEMS),
        stage="wave 1, stage 5",
    ),
    Row(
        ident="conservation_surplus",
        refusal="conservation OVER — the homes hold more bodies than were "
                "ever admitted. NOT loss, and it must not be repaired as if "
                "it were: the ordinary cause is an interrupted close. This "
                "row is not in §3.9, which names only 'conservation short'; "
                "it was found by the interrupted-move test, where the single "
                "short-message told a deletion story over the recoverable "
                "case (surfaced to the desk)",
        firing_input="a carrier whose head under-counts what the two homes "
                     "hold (here: the interrupted move's two copies)",
        expect=exits.FINDING,
        fire=lambda: _cli(
            ["item", "check"],
            items=SEED_ITEMS,
            done=EMPTY_DONE + "\n" + SEED_ITEMS.split("\n\n", 1)[1].replace(
                "grade: READY", "grade: DONE").replace("## xx-1", "## xx-2")),
        control=lambda: _cli(["item", "check"], items=SEED_ITEMS),
        stage="wave 1, stage 5",
    ),
    Row(
        ident="conservation_unverified",
        refusal="the conservation identity could not be computed — the head "
                "declares no baseline. COULD NOT VERIFY, never a clean "
                "identity",
        firing_input="a carrier head with `baseline` removed",
        expect=exits.COULD_NOT_VERIFY,
        fire=lambda: _cli(["item", "check"],
                          items=SEED_ITEMS.replace("baseline: 1\n", "", 1)),
        control=lambda: _cli(["item", "check"], items=SEED_ITEMS),
        stage="wave 1, stage 5",
    ),
    Row(
        ident="ledger_body",
        refusal="the ledger carries NO BODIES — one fixed-slot line per "
                "decision event (§3.6)",
        firing_input="a `ledger add` whose reason spans more than one line",
        expect=exits.FINDING,
        fire=lambda: _cli(["ledger", "add", "dropped", "xx-1", "--reason",
                           "overtaken by the rework\n\nand here is the body "
                           "that does not belong in a ledger"]),
        control=lambda: _cli(["ledger", "add", "dropped", "xx-1", "--reason",
                              "overtaken by the rework"]),
        stage="wave 1, stage 6",
    ),
    Row(
        ident="closure_home_split",
        refusal="the declaration names TWO closure homes — one fact, one "
                "home (§3.1's closure MOVE has one destination)",
        firing_input="`closure-home` and the `done bodies` kind's `home` "
                     "disagreeing",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "check"],
                          declaration=_split_closure_home()),
        control=lambda: _cli(["item", "check"]),
        stage="wave 1, stage 5",
    ),
]


# --- stages 7-9: the router, and the sites stage 8's coverage check found ----
#
# The rows below split into two groups, and the second group is the point of
# assigned item B. The FIRST is stage 7's own: the roster, an unresolved repo,
# a broken trigger. The SECOND is six refusals the code was already emitting
# under NO REGISTERED ROW — found by the emit-site coverage check on its first
# run, which is exactly the class it was built for. They were not new
# behaviour; they were unproven behaviour.

def _lane_cli(argv, *, roster_lines=None, **repo_kw) -> Fired:
    """Run `lane list` with a scratch roster under a scratch XDG config root.

    `roster_lines is None` means NO ROSTER FILE — the absent-roster plant.
    `"@repo"` in a line is substituted with the scratch repo's own path, so
    the control lists a repo that genuinely resolves rather than a path this
    row invented.
    """
    import io
    from contextlib import redirect_stdout
    from . import cli as cli_mod

    with _Repo(**repo_kw) as r:
        cfg = Path(tempfile.mkdtemp(prefix="lifecycle-cfg-"))
        try:
            if roster_lines is not None:
                (cfg / "lifecycle").mkdir(parents=True, exist_ok=True)
                (cfg / "lifecycle" / "repos").write_text(
                    "\n".join(l.replace("@repo", str(r.dir))
                              for l in roster_lines) + "\n",
                    encoding="utf-8")
            here = os.getcwd()
            prev = os.environ.get("XDG_CONFIG_HOME")
            try:
                os.environ["XDG_CONFIG_HOME"] = str(cfg)
                os.chdir(str(r.dir))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    code = cli_mod.main(list(argv))
                return Fired(code, buf.getvalue())
            finally:
                os.chdir(here)
                if prev is None:
                    os.environ.pop("XDG_CONFIG_HOME", None)
                else:
                    os.environ["XDG_CONFIG_HOME"] = prev
        finally:
            shutil.rmtree(cfg, ignore_errors=True)


#: A lane body carrying all four of §3.3's parts. The trigger is the only one
#: this build parses; the others are present so the row exercises a real lane
#: file rather than a `Trigger:` line on its own.
def _lane_body(trigger: str) -> str:
    return (f"# lane: x\n\nDecides: nothing — this is a row's fixture\n"
            f"Trigger: {trigger}\n\n| when | workflow |\n|---|---|\n"
            f"| never | none |\n\nEnds: dropped\n")


LANE_ROWS = [
    Row(
        ident="roster_absent",
        refusal="roster absent — the router is GENERATED over the roster, so "
                "with no roster there is no board, and an empty board renders "
                "exactly like one on which every lane is quiet",
        firing_input="rm the roster; run `lane list`",
        expect=exits.FINDING,
        fire=lambda: _lane_cli(["lane", "list"], roster_lines=None),
        # The SAME repo with a roster that lists it: only the roster's
        # existence differs.
        control=lambda: _lane_cli(["lane", "list"], roster_lines=["@repo"]),
        stage="wave 1, stage 7",
    ),
    Row(
        ident="repo_unresolved",
        refusal="a listed repo that does not resolve is NAMED — a router that "
                "dropped the line would print a shorter board rather than a "
                "broken one",
        firing_input="a roster line naming a moved repo",
        expect=exits.FINDING,
        fire=lambda: _lane_cli(["lane", "list"],
                               roster_lines=["/nonexistent/moved-repo"]),
        control=lambda: _lane_cli(["lane", "list"], roster_lines=["@repo"]),
        stage="wave 1, stage 7",
    ),
    Row(
        ident="trigger_broken",
        refusal="trigger BROKEN — a predicate exiting >=2 (§3.3's reserved "
                "code) is a FINDING, never folded into quiet: a dead lane "
                "that renders quiet is a clean board over a router that does "
                "not work",
        firing_input="a lane whose `Trigger:` predicate exits 2",
        expect=exits.FINDING,
        fire=lambda: _lane_cli(["lane", "list"], roster_lines=["@repo"],
                               lanes=["x"],
                               lane_files={"x": _lane_body("exit 2")}),
        # The SAME lane with a QUIET predicate: the arms differ in the
        # predicate's exit code alone, which is the reserved value under test.
        control=lambda: _lane_cli(["lane", "list"], roster_lines=["@repo"],
                                  lanes=["x"],
                                  lane_files={"x": _lane_body("exit 1")}),
        stage="wave 1, stage 7",
    ),
    Row(
        ident="unknown_item",
        refusal="a verb naming an item no live home holds",
        firing_input="`item ready xx-9999`",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "ready", "xx-9999"], items=SEED_ITEMS),
        control=lambda: _cli(["item", "ready", "xx-1"], items=SEED_ITEMS),
        stage="wave 1, stage 8 (found by the emit-site coverage check)",
    ),
    Row(
        ident="unknown_source",
        refusal="a `--source` outside the closed door set — an unrecognised "
                "source would decide the cost test's veto silently",
        firing_input="`item add --source somebody`",
        expect=exits.FINDING,
        fire=lambda: _cli(GOOD_ADD + ["--source", "somebody"]),
        control=lambda: _cli(GOOD_ADD + ["--source", "operator"]),
        stage="wave 1, stage 8 (found by the emit-site coverage check)",
    ),
    Row(
        ident="new_without_typed_blocker",
        refusal="an item whose slots are incomplete is NEW, and a NEW item "
                "carries a TYPED blocker saying what it waits for. An "
                "incomplete item with nothing to wait for ages in nobody's "
                "court",
        # `--write-set UNKNOWN` and NOT a removed flag. Measured while
        # building this row: an add missing a slot ENTIRELY never reaches
        # this refusal, because `slot_value_problem` refuses the empty slot
        # first and the run exits under `item_shape`. So the only input that
        # reaches it is the migration's own marker — a slot that is present,
        # non-empty and not filled. The first draft used a removed
        # `--evidence` and its CONTROL went red under `item_shape`, which is
        # what surfaced this.
        firing_input="`item add --write-set UNKNOWN` with no `--blocked-by`",
        expect=exits.FINDING,
        fire=lambda: _cli(_mutate_add("--write-set", "UNKNOWN")),
        # The SAME incomplete add WITH a typed blocker: the arms differ in
        # the blocker alone, not in slot completeness.
        control=lambda: _cli(_mutate_add("--write-set", "UNKNOWN")
                             + ["--blocked-by", "decision which window"]),
        stage="wave 1, stage 8 (found by the emit-site coverage check)",
    ),
    Row(
        ident="move_uncommitted",
        refusal="the move is on disk but was NOT committed, so its two halves "
                "are not durable together — the third step of the move "
                "failing, not the move",
        firing_input="`item close` in a repo whose commit is refused",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "close", "xx-1"], items=SEED_ITEMS,
                          fail_commit=True),
        control=lambda: _cli(["item", "close", "xx-1"], items=SEED_ITEMS),
        stage="wave 1, stage 8 (found by the emit-site coverage check)",
    ),
    Row(
        ident="ledger_shape",
        refusal="a ledger with no `schema:` head line — a carrier without a "
                "version cannot be refused by a future tool",
        firing_input="a `LEDGER.md` whose first line is a ledger entry",
        expect=exits.FINDING,
        fire=lambda: _cli(["ledger", "check"],
                          ledger_text="dropped: xx-1 — overtaken\n"),
        control=lambda: _cli(["ledger", "check"],
                             ledger_text=ledger_mod.head_text()
                                         + "dropped: xx-1 — overtaken\n"),
        stage="wave 1, stage 8 (found by the emit-site coverage check)",
    ),
    Row(
        ident="unregistered_kind",
        refusal="`kind show` naming a kind the declaration does not register",
        firing_input="`kind show nosuchkind`",
        expect=exits.FINDING,
        fire=lambda: _cli(["kind", "show", "nosuchkind"]),
        control=lambda: _cli(["kind", "show", "items"]),
        stage="wave 1, stage 8 (found by the emit-site coverage check)",
    ),
    Row(
        ident="emit_site_unregistered",
        refusal="ASSIGNED ITEM B — a site in the code emits a FINDING under a "
                "row the roster does not register: no plant, no control, no "
                "line in the §3.9 snapshot, so the roster's green says "
                "nothing about it",
        firing_input="a planted `FINDING [<unregistered row>]` in a copy of "
                     "the package, scanned",
        expect=exits.FINDING,
        fire=lambda: _coverage_over_copy(plant=True),
        # The SAME copy without the planted line: the arms differ in one
        # emitted row name, not in whether a copy was scanned.
        control=lambda: _coverage_over_copy(plant=False),
        stage="wave 1, stage 8",
    ),
    Row(
        ident="migrate_would_overwrite",
        refusal="`migrate` over a repo whose successor carrier already exists "
                "— a second run would replace real work with a re-derivation "
                "of the carrier it replaced",
        firing_input="`migrate` with `ITEMS.md` already present, no `--force`",
        expect=exits.FINDING,
        fire=lambda: _migrate_run(items=EMPTY_ITEMS),
        # `--force` is the ONE difference: the same repo, the same existing
        # carrier, so what separates the arms is the flag and not the state.
        control=lambda: _migrate_run(items=EMPTY_ITEMS, force=True),
        stage="wave 1, stage 9",
    ),
    Row(
        ident="migration_unclassified",
        refusal="an entry whose grade word no rule in §4 row 1 or §3.1 covers "
                "(D-f): reported with its grade word and line number, never "
                "given a plausible mapping",
        firing_input="a source carrier entry graded with an unknown word",
        expect=exits.FINDING,
        fire=lambda: _migrate_run(
            backlog="# old\n\n## Open\n\n- **FLURB 2026-01-01 — a grade word "
                    "no rule covers.** body\n"),
        # The SAME carrier with a grade word the rules DO cover: the arms
        # differ in the word alone.
        control=lambda: _migrate_run(
            backlog="# old\n\n## Open\n\n- **READY 2026-01-01 — a grade word "
                    "the rules cover.** body\n"),
        stage="wave 1, stage 9",
    ),
    Row(
        ident="migration_ledger_nonzero",
        refusal="the acceptance criterion 'zero entries routed to the ledger' "
                "(§3.6, §4 row 1) is checked at the ARTIFACT and not only in "
                "the report",
        firing_input="a `LEDGER.md` already carrying a line when `migrate` "
                     "runs",
        expect=exits.FINDING,
        fire=lambda: _migrate_run(
            ledger_text=ledger_mod.head_text()
                        + "dropped: xx-1 — overtaken\n"),
        control=lambda: _migrate_run(ledger_text=ledger_mod.head_text()),
        stage="wave 1, stage 9",
    ),
]


def _coverage_over_copy(*, plant: bool) -> Fired:
    """Run the emit-site coverage check over a COPY of this package.

    A copy rather than the live tree: the check's own red must not depend on
    editing the module that is running it, and a mutation left behind by a
    crashed row would poison every later row in the same process.
    """
    from . import roster as roster_mod

    d = Path(tempfile.mkdtemp(prefix="lifecycle-cov-"))
    try:
        for f in Path(__file__).resolve().parent.glob("*.py"):
            shutil.copy2(f, d / f.name)
        if plant:
            target = d / "exits.py"
            target.write_text(
                target.read_text(encoding="utf-8")
                + '\n\ndef _planted(out):\n'
                  '    out("FINDING [not_a_registered_row] planted")\n',
                encoding="utf-8")
        buf = []
        code = roster_mod.check_coverage(buf.append, root=d)
        return Fired(code, "\n".join(buf))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _migrate_run(*, backlog=None, force=False, **repo_kw) -> Fired:
    """Run `migrate` in a scratch repo carrying an old carrier."""
    import io
    from contextlib import redirect_stdout
    from . import cli as cli_mod

    body = backlog if backlog is not None else (
        "# old\n\n## Open\n\n- **READY 2026-01-01 — an ordinary entry.** body\n")
    with _Repo(**repo_kw) as r:
        if "items" not in repo_kw:
            # `_Repo` seeds both successor homes, and `migrate` refuses to
            # overwrite an existing one — so without this every migrate row
            # would fire `migrate_would_overwrite` and prove that row instead
            # of its own. Measured: two rows failed exactly this way, each
            # reporting a finding it had not planted.
            (r.dir / "ITEMS.md").unlink(missing_ok=True)
            (r.dir / "ITEMS-DONE.md").unlink(missing_ok=True)
        (r.dir / "BACKLOG.md").write_text(body, encoding="utf-8")
        (r.dir / "BACKLOG-DONE.md").write_text(
            "# old done\n\n## Done\n\n- **DONE 2026-01-01 — closed.** body\n",
            encoding="utf-8")
        argv = ["--repo", str(r.dir), "migrate",
                "--report", "docs/audits/report.md"]
        if force:
            argv.append("--force")
        here = os.getcwd()
        try:
            os.chdir(str(r.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(argv)
            return Fired(code, buf.getvalue())
        finally:
            os.chdir(here)


def _mutate_add(flag: str, value: str) -> list:
    """`GOOD_ADD` with one flag's value replaced — one thing at a time."""
    out = list(GOOD_ADD)
    if flag in out:
        out[out.index(flag) + 1] = value
    else:
        out += [flag, value]
    return out


def _split_closure_home() -> dict:
    d = json.loads(json.dumps(GOOD_FULL_DECLARATION))
    d["kinds"]["done bodies"]["home"] = "SOMEWHERE-ELSE.md"
    return d


# --- the SCHEMA WAVE (1d): the rows §3.8c's decisions create -----------------
#
# Each of these defends a decision round 4 accepted, and each is red-proven
# the same way every row above is: a plant, a control differing in exactly the
# thing under test, and a recorded mutation in `tools/prove-rows.py`.

def _decl_without(key: str) -> dict:
    d = json.loads(json.dumps(GOOD_DECLARATION))
    d.pop(key, None)
    return d


def _decl_with(**kw) -> dict:
    d = json.loads(json.dumps(GOOD_DECLARATION))
    d.update(kw)
    return d


def _kind_field(stage: str, value) -> dict:
    d = json.loads(json.dumps(GOOD_DECLARATION))
    d["kinds"]["items"][stage] = value
    return d


def _watched_ref_types() -> set:
    """Which typed-reference kinds the RESOLVER actually resolves.

    DERIVED FROM THE SOURCE of `_check_typed_refs`, never from a list beside
    it: a set restated from the code it grades is an expectation with the same
    parentage as its subject, and it stays green the day a type is added and
    left unresolved. The resolver's pool table maps each PREFIXED type to what
    it resolves against, so the types it can resolve are that table's keys; a
    BARE role resolves by definition, and the branch that returns early on one
    is what makes that true.
    """
    src = Path(decl.__file__).read_text(encoding="utf-8")
    body = src.split("def _check_typed_refs", 1)[1].split("\ndef ", 1)[0]
    found = set(re.findall(r'"([a-z]+)": \(world\.', body))
    if "if typ in REF_BARE" in body:
        found |= set(decl.REF_BARE)
    return found


def _watched_schema_carriers() -> set:
    """Which CARRIERS the schema-floor refusal is actually emitted from.

    Derived from the emit sites, exactly as the coverage check derives them.
    The mapping from module to carrier is the design's: one parser serves both
    item homes, so a site in `items.py` watches the live carrier and the
    closure home together.
    """
    from . import roster as roster_mod
    per_module = {
        "declaration.py": ("declaration",),
        "items.py": ("items", "done"),
        "ledger.py": ("ledger",),
    }
    out = set()
    for site in roster_mod.emit_sites().get("schema_above_floor", []):
        out.update(per_module.get(site.split(":", 1)[0], ()))
    return out


def _route_check_over_copy(*, narrow: bool) -> Fired:
    """Run the ROUTE-SET check over a COPY of this package.

    `narrow=True` mutates the copy's reference resolver back to the ONE type
    it watched before this wave — `lane:` — which is the OLD implementation
    the new expectation has to be run against (law 4). A copy rather than the
    live tree, for the reason `_coverage_over_copy` gives: the check's red
    must not depend on editing the module that is running it.
    """
    d = Path(tempfile.mkdtemp(prefix="lifecycle-routes-"))
    try:
        for f in Path(__file__).resolve().parent.glob("*.py"):
            shutil.copy2(f, d / f.name)
        if narrow:
            # THE POOL TABLE is what the derivation reads, so the pool table is
            # what the mutation narrows. Disabling the branch beneath it would
            # leave the derived set unchanged and the check green — a mutation
            # that misses its target and reads as a check that does not
            # discriminate. Measured while building this row.
            target = d / "declaration.py"
            text = target.read_text(encoding="utf-8")
            for gone in ('"verb": (world.verbs, "this build\'s CLI verbs"),',
                         '"hook": (world.hooks, "the hooks the plugin declares in "',
                         '"producer": (world.producers, "the producers this declaration\'s "'):
                assert gone in text, f"the route-narrowing anchor moved: {gone[:30]}"
            text = text.replace(
                '''            "verb": (world.verbs, "this build\'s CLI verbs"),
            "hook": (world.hooks, "the hooks the plugin declares in "
                                  "plugin.json"),
            "producer": (world.producers, "the producers this declaration\'s "
                                          "kinds name as writers"),
''', "", 1)
            bare = '''        if typ in REF_BARE:
            continue
'''
            assert bare in text, "the bare-role anchor moved"
            text = text.replace(bare, "", 1)
            target.write_text(text, encoding="utf-8")
        src = (
            "import json, sys\n"
            f"sys.path.insert(0, {str(d.parent)!r})\n"
            f"sys.path.insert(0, {str(Path(__file__).resolve().parents[1])!r})\n"
            "import importlib.util, types\n"
            f"pkg = types.ModuleType('lcopy')\n"
            f"pkg.__path__ = [{str(d)!r}]\n"
            "sys.modules['lcopy'] = pkg\n"
            "from lcopy import roster as r\n"
            "buf = []\n"
            "code = r.check_routes(buf.append)\n"
            "print(json.dumps({'code': code, 'out': '\\n'.join(buf)}))\n"
        )
        p = subprocess.run([__import__("sys").executable, "-c", src],
                           capture_output=True, text=True)
        if p.returncode != 0:
            return Fired(-1, f"SETUP FAILED: {p.stderr[-800:]}")
        rec = json.loads(p.stdout.strip().split("\n")[-1])
        return Fired(rec["code"], rec["out"])
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _retire_growth(*, closed: bool) -> Fired:
    """`retire`'s GROWTH question over a scratch repo, with and without a close.

    The control CLOSES an item through the real verb, so the exit event it
    reads is one the tool actually recorded rather than a line this row wrote
    into a log. A planted log line would prove the reader parses JSON.
    """
    import io
    from contextlib import redirect_stdout
    from . import cli as cli_mod
    from . import retire as retire_mod

    with _Repo(items=SEED_ITEMS) as r:
        here = os.getcwd()
        try:
            os.chdir(str(r.dir))
            if closed:
                with redirect_stdout(io.StringIO()):
                    cli_mod.main(["--repo", str(r.dir), "item", "close",
                                  "xx-1"])
            buf = []
            code = retire_mod.growth_verdict(r.dir, GOOD_FULL_DECLARATION,
                                             buf.append)
            return Fired(code, "\n".join(buf))
        finally:
            os.chdir(here)


def _sweep_run(*, stray: bool) -> Fired:
    """`kind sweep` over a scratch repo, with and without an unregistered file."""
    import io
    from contextlib import redirect_stdout
    from . import cli as cli_mod

    with _Repo() as r:
        if stray:
            (r.dir / "STRAY-NOTES.md").write_text("a file no kind claims\n",
                                                  encoding="utf-8")
            subprocess.run(["git", "-C", str(r.dir), "add", "STRAY-NOTES.md"],
                           capture_output=True, text=True)
            subprocess.run(["git", "-C", str(r.dir), "commit", "-qm", "stray",
                            "--", "STRAY-NOTES.md"],
                           capture_output=True, text=True)
        here = os.getcwd()
        try:
            os.chdir(str(r.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(r.dir), "kind", "sweep"])
            return Fired(code, buf.getvalue())
        finally:
            os.chdir(here)


#: A live carrier whose head declares a capture flow and whose done home is
#: empty — booking with no drain at all.
# THREE, not four: the control closes ONE item, so the arms differ in the
# DRAIN alone and the control lands exactly AT the 3:1 tripwire rather than
# over it. A pair whose control is still over the wire would separate nothing.
NO_DRAIN_ITEMS = SEED_ITEMS.replace("added: 0", "added: 3")

#: A closed body, as `item close` writes one.
DONE_BLOCK = """## xx-1
grade: DONE
requirement: a closed body — record: LEDGER.md
goal: mitigate
write-set: tools/thing.py
done-criterion: the check goes red on the real defect and green after
evidence: none yet
blocked-by: NONE
"""

SCHEMA_ROWS = [
    Row(
        ident="declaration_retired_key",
        refusal="a declaration carrying a key this schema WITHDREW — "
                "`ready-cap`, whose whole premise R22 removed",
        firing_input="a declaration still carrying `ready-cap: 10`",
        expect=exits.FINDING,
        fire=lambda: _decl_run(declaration=_decl_with(**{"ready-cap": 10}),
                               gitignore="", laws_lines=10),
        # The SAME declaration without the withdrawn key: the arms differ in
        # that key alone, not in whether the declaration is otherwise valid.
        control=lambda: _decl_run(**_GOOD_KW),
        stage="wave 1d, the schema wave",
    ),
    Row(
        ident="leak_scan_undeclared_reason",
        refusal="the source-scope foreign-path class turned OFF with no "
                "reason declared (§3.3 — the enabling decision is the repo's "
                "and it is written down)",
        firing_input="`leak-scan: {source-scope-foreign-path: false}` with no "
                     "`reason`",
        expect=exits.FINDING,
        fire=lambda: _decl_run(
            declaration=_decl_with(**{"leak-scan": {
                "source-scope-foreign-path": False}}),
            gitignore="", laws_lines=10),
        # The SAME `false` WITH its reason: the arms differ in the reason
        # alone, so what fires is the undeclared decision and not the value.
        control=lambda: _decl_run(
            declaration=_decl_with(**{"leak-scan": {
                "source-scope-foreign-path": False,
                "reason": "this repo's own prose names this machine's home "
                          "throughout, so the source-scope class fires on "
                          "ordinary operating text"}}),
            gitignore="", laws_lines=10),
        stage="wave 1d, the schema wave",
    ),
    Row(
        ident="reference_untyped",
        refusal="PROSE in a `reader`/`writer` slot — §3.8c's reference types "
                "are closed, and prose cannot be resolved",
        firing_input="a kind whose `reader` says \"the drain lane\"",
        expect=exits.FINDING,
        fire=lambda: _decl_run(
            declaration=_kind_field("reader", ["the drain lane"]),
            gitignore="", laws_lines=10),
        # The SAME reader, TYPED: the arms differ in the typing alone.
        # `verb:item ready` and not `lane:drain`: the control must differ in
        # the TYPING alone, and a `lane:` reference in a declaration with no
        # declared lanes fires `dangling_reference` instead — a control going
        # red for the neighbouring reason, which proves nothing about this row.
        control=lambda: _decl_run(
            declaration=_kind_field("reader", ["verb:item ready"]),
            gitignore="", laws_lines=10),
        stage="wave 1d, the schema wave",
    ),
    Row(
        ident="schema_mismatch",
        refusal="ONE schema version per repo — the declaration and a carrier "
                "disagree (§3.8c). Not a floor question: the floor asks what "
                "this BUILD can read, this asks whether the REPO agrees with "
                "itself",
        firing_input="a declaration stamped 2 over an `ITEMS.md` stamped 1",
        expect=exits.FINDING,
        fire=lambda: _decl_run(
            declaration=GOOD_DECLARATION, gitignore="", laws_lines=10,
            items_text=EMPTY_ITEMS.replace("schema: 2", "schema: 1", 1)),
        # The SAME repo with the carrier at the declaration's number.
        control=lambda: _decl_run(**_GOOD_KW),
        stage="wave 1d, the schema wave",
    ),
    Row(
        ident="done_slot_on_live_item",
        refusal="a LIVE block carrying a closed-body slot — `superseded-by:` "
                "or `blocker-moot:`, each of which records something a "
                "CLOSURE did",
        firing_input="a READY block with a `superseded-by:` line",
        expect=exits.FINDING,
        fire=lambda: _items_run(
            GOOD_ITEMS.rstrip("\n") + "\nsuperseded-by: xx-9\n"),
        control=lambda: _items_run(GOOD_ITEMS),
        stage="wave 1d, the schema wave",
    ),
    Row(
        ident="open_grade_in_done_home",
        refusal="an OPEN grade in the closure home — a body that arrived by "
                "some path that is not a close",
        firing_input="a `READY` block in `ITEMS-DONE.md`",
        expect=exits.FINDING,
        fire=lambda: _done_run(EMPTY_DONE + "\n"
                               + DONE_BLOCK.replace("grade: DONE",
                                                    "grade: READY")),
        # The SAME body, CLOSED: the arms differ in the grade alone.
        control=lambda: _done_run(EMPTY_DONE + "\n" + DONE_BLOCK),
        stage="wave 1d, the schema wave",
    ),
    Row(
        ident="blocked_in_done_home",
        refusal="a closed body still carrying a blocker — a wait recorded "
                "against something that has stopped waiting, which is what "
                "leaves an unanswerable question in the operator's queue "
                "after the item that asked it is gone",
        firing_input="a DONE block with `blocked-by: decision <question>`",
        expect=exits.FINDING,
        fire=lambda: _done_run(
            EMPTY_DONE + "\n" + DONE_BLOCK.replace(
                "blocked-by: NONE", "blocked-by: decision which window")),
        control=lambda: _done_run(EMPTY_DONE + "\n" + DONE_BLOCK),
        stage="wave 1d, the schema wave",
    ),
    Row(
        ident="unknown_slot_misplaced",
        refusal="UNKNOWN in a slot that may never hold it — a grade is one of "
                "the five and a blocker is typed or NONE, so UNKNOWN there is "
                "a value nothing can ever fill in",
        firing_input="a block with `blocked-by: UNKNOWN`",
        expect=exits.FINDING,
        fire=lambda: _items_run(
            GOOD_ITEMS.replace("blocked-by: NONE", "blocked-by: UNKNOWN")),
        control=lambda: _items_run(GOOD_ITEMS),
        stage="wave 1d, the schema wave",
    ),
    Row(
        ident="ready_with_unknown_slot",
        refusal="READY over a slot nobody has ever written (§3.1) — UNKNOWN "
                "is the migration's declared marker and the grade workflow "
                "fills it BEFORE READY",
        firing_input="a READY block whose `goal` is UNKNOWN",
        expect=exits.FINDING,
        fire=lambda: _items_run(
            GOOD_ITEMS.replace("goal: mitigate", "goal: UNKNOWN")),
        # The SAME block with the goal filled: the arms differ in the one slot.
        control=lambda: _items_run(GOOD_ITEMS),
        stage="wave 1d, the schema wave",
    ),
    Row(
        ident="capture_dominated",
        refusal="booking outrunning shipped-plus-dropped — a RATIO, never a "
                "size (R22). A large carrier draining steadily owes nothing "
                "and a small one that never drains does",
        firing_input="a carrier that admitted four items and closed none",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "ratio"], items=NO_DRAIN_ITEMS),
        # The SAME carrier with a real closure behind it: the arms differ in
        # the DRAIN and not in the size, which is the whole point of the row.
        control=lambda: _ratio_after_close(),
        stage="wave 1d, the schema wave",
    ),
    Row(
        ident="kind_grew_without_exit",
        refusal="a kind that GREW WITHOUT AN EXIT EVENT (the design's own "
                "replacement for a cap) — its home holds instances, it "
                "declares `bounded-by-exit`, and its exit has recorded nothing",
        firing_input="a repo holding items with no `item close` ever recorded",
        expect=exits.FINDING,
        fire=lambda: _retire_growth(closed=False),
        # The SAME repo after ONE real close: the exit event is one the tool
        # recorded, not a line this row wrote into a log.
        control=lambda: _retire_growth(closed=True),
        stage="wave 1d, the schema wave",
    ),
    Row(
        ident="unregistered_persisted_thing",
        refusal="invariant 1 — a tracked file that resolves to no registered "
                "kind",
        firing_input="a tracked file under a home no kind claims",
        expect=exits.FINDING,
        fire=lambda: _sweep_run(stray=True),
        control=lambda: _sweep_run(stray=False),
        stage="wave 1d, the schema wave",
    ),
    Row(
        ident="route_set_unwatched",
        refusal="a refusal whose TEXT names an effect WIDER than the routes "
                "the code watches — round 4's cross-row cure. The row fires "
                "correctly on the routes it does watch, so its green says "
                "nothing about the rest",
        firing_input="the reference resolver narrowed to `lane:` alone, which "
                     "is what it watched before this wave, with "
                     "`dangling_reference` still claiming every type",
        expect=exits.FINDING,
        fire=lambda: _route_check_over_copy(narrow=True),
        # The SAME copy, unnarrowed: the arms differ in the resolver's reach
        # alone, not in whether a copy was scanned.
        control=lambda: _route_check_over_copy(narrow=False),
        stage="wave 1d, the schema wave",
    ),
]


# --- wave 2, item B: `desk state`'s own closed-vocabulary refusals --------
#
# Found the same way the six stage-8 rows above were found: `--test`'s
# emit-site coverage check ran over the new module and reported both FINDING
# sites as unregistered. Neither reaches the write step (the vocabulary
# check runs before the shape check, and both run before `resolve_desk_id`
# and the write), so — unlike `_lane_cli`'s roster row above — no XDG root
# needs isolating for the FIRE arm; the CONTROL arm below is a real CLEAN
# write, though, and that one DOES need its own scratch state root, or a
# `--test` run leaves `row-desk-*.json` debris under the operator's real
# `$XDG_STATE_HOME/lifecycle/desk-state/`.

def _desk_cli(argv) -> Fired:
    """Run one `desk state` invocation under a scratch `XDG_STATE_HOME`,
    isolated the same way `_lane_cli` isolates `XDG_CONFIG_HOME` above."""
    import io
    from contextlib import redirect_stdout
    from . import cli as cli_mod

    with _Repo() as r:
        state = Path(tempfile.mkdtemp(prefix="lifecycle-state-"))
        prev = os.environ.get("XDG_STATE_HOME")
        try:
            os.environ["XDG_STATE_HOME"] = str(state)
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(r.dir)] + list(argv))
            return Fired(code, buf.getvalue())
        finally:
            if prev is None:
                os.environ.pop("XDG_STATE_HOME", None)
            else:
                os.environ["XDG_STATE_HOME"] = prev
            shutil.rmtree(state, ignore_errors=True)


DESK_ROWS = [
    Row(
        ident="desk_state_unknown_value",
        refusal="a `desk state` value outside the closed vocabulary "
                "(REPORTED / WAITING-ON / BLOCKED / DONE) is a refusal, not "
                "a coercion — the vocabulary is closed and an open one "
                "decays",
        firing_input="`desk state BOGUS`",
        expect=exits.FINDING,
        fire=lambda: _desk_cli(["desk", "state", "BOGUS"]),
        # The SAME verb, a value the closed vocabulary actually carries: the
        # arms differ in the value word alone.
        control=lambda: _desk_cli(["desk", "state", "DONE",
                                   "--desk", "row-desk-vocab"]),
        stage="wave 2",
    ),
    Row(
        ident="desk_state_shape",
        refusal="a closed-vocabulary `desk state` value missing its own "
                "required argument",
        firing_input="`desk state REPORTED` with no message id",
        expect=exits.FINDING,
        fire=lambda: _desk_cli(["desk", "state", "REPORTED",
                                "--desk", "row-desk-shape"]),
        # The SAME value, WITH its required argument: the arms differ in the
        # argument's presence alone.
        control=lambda: _desk_cli(["desk", "state", "REPORTED", "msg-1",
                                   "--desk", "row-desk-shape"]),
        stage="wave 2",
    ),
]


def _ratio_after_close() -> Fired:
    """`item ratio` over a scratch repo that has actually closed something."""
    import io
    from contextlib import redirect_stdout
    from . import cli as cli_mod

    with _Repo(items=NO_DRAIN_ITEMS) as r:
        here = os.getcwd()
        try:
            os.chdir(str(r.dir))
            with redirect_stdout(io.StringIO()):
                cli_mod.main(["--repo", str(r.dir), "item", "close", "xx-1"])
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(r.dir), "item", "ratio"])
            return Fired(code, buf.getvalue())
        finally:
            os.chdir(here)


ROWS = ROWS + VERB_ROWS + LANE_ROWS + SCHEMA_ROWS + DESK_ROWS

# --- the ROUTE SETS, attached to the rows whose refusal has a vocabulary -----
#
# Attached here rather than inline so the two sides stay visibly independent:
# the route SET is a tuple the module under test declares from the design, and
# the WATCHED set is derived from that module's source. A row that computed
# one from the other would be comparing a claim against itself.

for _row in ROWS:
    if _row.ident == "dangling_reference":
        _row.route_set = tuple(decl.REF_TYPES)
        _row.routes_watched = _watched_ref_types
    elif _row.ident == "schema_above_floor":
        _row.route_set = ("declaration", "items", "done", "ledger")
        _row.routes_watched = _watched_schema_carriers
del _row
