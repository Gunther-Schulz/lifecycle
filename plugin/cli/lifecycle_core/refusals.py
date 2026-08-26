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
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from . import exits
from . import declaration as decl
from . import items as items_mod

#: A declaration that is VALID in every respect, used as the control every
#: row mutates exactly one thing away from. Derived from the design's own
#: stage list, never read back out of a real repo's file.
GOOD_DECLARATION = {
    "schema": 1,
    "id-prefix": "xx",
    "public": True,
    "laws": "LAWS.md",
    "closure-home": "ITEMS-DONE.md",
    "trigger-policy": "on-demand",
    "goals": ["see", "attribute", "mitigate", "verify", "retire"],
    "ready-cap": 10,
    "head-rule": {"lead-goal": "mitigate"},
    "lanes": [],
    "template-bindings": {},
    "kinds": {
        "items": {
            "home": "ITEMS.md",
            "writer": "tool — lifecycle item add|ready|park|close only",
            "reader": ["the drain lane", "lifecycle item ratio"],
            "staleness": "change-coupling — the cited record no longer resolves",
            "exit": {"action": "move",
                     "recording-act": "the item close fire-log line"},
            "bound": "unbounded, declared why: the ready-cap bounds the head",
        },
    },
}

GOOD_ITEMS = """schema: 1
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
        if items_text is not None:
            (self.dir / "ITEMS.md").write_text(items_text, encoding="utf-8")
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
        ident="laws_over_cap",
        refusal="laws file over cap",
        firing_input="line 61 of the declared laws file",
        expect=exits.FINDING,
        fire=lambda: _decl_run(declaration=GOOD_DECLARATION, gitignore="",
                               laws_lines=decl.LAWS_CAP_LINES + 1),
        control=lambda: _decl_run(declaration=GOOD_DECLARATION, gitignore="",
                                  laws_lines=decl.LAWS_CAP_LINES),
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
            GOOD_ITEMS.replace("schema: 1", f"schema: {items_mod.SCHEMA_FLOOR + 1}", 1)),
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
    ("lane body over one screen", "lanes are wave 2"),
    ("unbound required slot", "template bindings are wave 2"),
    ("exact template duplication in a repo", "templates are wave 2"),
    ("trigger BROKEN", "needs `lane list`, wave 1 stage 7"),
    ("roster absent / repo unresolved", "needs `lane list`, wave 1 stage 7"),
    ("detector without disposition", "the detector registry is wave 3"),
    ("unregistered persisted thing", "the retire lane's walk is wave 4"),
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
    "schema": 1, "id-prefix": "xx", "public": False, "laws": "LAWS.md",
    "closure-home": "ITEMS-DONE.md", "trigger-policy": "on-demand",
    "goals": ["see", "attribute", "mitigate", "verify", "retire"],
    "ready-cap": 10, "head-rule": {"lead-goal": "mitigate"},
    "lanes": [], "template-bindings": {},
    "kinds": {
        "items": {
            "home": "ITEMS.md",
            "writer": "tool — lifecycle item add|ready|park|close only",
            "reader": ["the drain lane", "lifecycle item ratio"],
            "staleness": "change-coupling — the cited record no longer resolves",
            "exit": {"action": "move",
                     "recording-act": "the item close fire-log line"},
            "bound": "unbounded, declared why: the ready-cap bounds the head",
        },
        "done bodies": {
            "home": "ITEMS-DONE.md",
            "writer": "tool — lifecycle item close, the atomic move",
            "reader": ["the retire lane's conservation check"],
            "staleness": "none, declared why: a closure record is history",
            "exit": {"action": "compact",
                     "recording-act": "a ledger decision line naming the range"},
            "bound": "unbounded, declared why: this is the archive",
        },
        "ledger lines": {
            "home": "LEDGER.md",
            "writer": "tool for the slots, session for the reason prose",
            "reader": ["the grade workflow's rejected gate"],
            "staleness": "none, declared why: append-only decision history",
            "exit": {"action": "never", "recording-act": "compaction only"},
            "bound": "unbounded, declared why: one line per decision event",
        },
    },
}

#: A carrier head whose conservation identity balances against ONE live item.
SEED_ITEMS = """schema: 1
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

EMPTY_ITEMS = "schema: 1\nbaseline: 0\nadded: 0\ncompacted: 0\n"
EMPTY_DONE = "schema: 1\n"

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
                 ledger_text=None, public=None):
        self.dir = Path(tempfile.mkdtemp(prefix="lifecycle-verb-"))
        d = declaration if declaration is not None else GOOD_FULL_DECLARATION
        if public is not None:
            d = json.loads(json.dumps(d))
            d["public"] = public
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
            "schema: 1\n" if ledger_text is None else ledger_text,
            encoding="utf-8")
        self._run(["git", "add", "-A"])
        self._run(["git", "commit", "-qm", "seed"])

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


ROWS = ROWS + VERB_ROWS
