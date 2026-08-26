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


# --- scratch scaffolding -----------------------------------------------------

class _Scratch:
    """A throwaway git repo carrying a declaration and a carrier file.

    A real `git init`, because two rows turn on what git can SEE: an ignored
    declaration is invisible to `check-ignore` in anything but a work tree,
    and a fake would report the answer we hoped for.
    """

    def __init__(self, *, declaration=None, gitignore=None, laws_lines=None,
                 items_text=None, declaration_raw=None):
        self.dir = Path(tempfile.mkdtemp(prefix="lifecycle-row-"))
        self._run(["git", "init", "-q", "-b", "main"])
        # No hooks from the machine's global core.hooksPath: this scratch repo
        # is an instrument, and an unrelated gate firing inside it would be
        # read as the row's own verdict.
        self._run(["git", "config", "core.hooksPath", str(self.dir / ".nohooks")])
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
    ("unknown grade word on write", "needs `item add`, wave 1 stage 4"),
    ("PARKED without a typed blocker", "needs `item park`, wave 1 stage 5"),
    ("conservation short", "needs the close verb's baseline deltas, stage 5"),
    ("dangling typed reference (`blocked-by cf-9999`)",
     "the declaration half fires today (see `dangling_reference`); the ITEM "
     "half needs `item park --blocked-by`, stage 5"),
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
