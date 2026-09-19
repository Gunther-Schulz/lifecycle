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
from . import grammar
from . import items as items_mod
from . import ledger as ledger_mod

#: A declaration that is VALID in every respect, used as the control every
#: row mutates exactly one thing away from. Derived from the design's own
#: stage list, never read back out of a real repo's file.
GOOD_DECLARATION = {
    # DERIVED, never restated (lc-218). This fixture is the control every
    # row mutates one thing away from, and the carriers beside it are seeded
    # from `ledger.head_text()` / the constants below, which read the live
    # floor. A literal here disagrees with them the moment the floor moves,
    # and `schema_mismatch` then fires on EVERY declaration row's control —
    # 42 of them did exactly that on the 2 -> 3 bump.
    "schema": items_mod.SCHEMA_FLOOR,
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
            # lc-168's seventh stage. `items` is one of the four kinds whose
            # trigger was always implicit: the write happens because the verb
            # ran, which is why nobody ever had to remember it.
            "trigger": "verb item add",
        },
    },
}

GOOD_ITEMS = f"""schema: {items_mod.SCHEMA_FLOOR}
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


#: The exercise record both arms of `blocker_exercise_misplaced` carry (lc-175).
#: SPELLED ONCE because the pair's whole discriminating power is that the two
#: arms differ in the BLOCKER and in nothing else; two spellings of this line
#: would let the arms drift apart and the row would stop proving what it says.
_EXERCISE_LINE = ("blocker-exercise: 2026-09-19 live 1 | positive `true` 0 | "
                  "negative `false` 1 — the predicate answers both ways")

#: The derivability statement both arms of `not_derivable_misplaced` carry
#: (lc-179), spelled once for the reason above: the arms differ in the
#: BLOCKER and in nothing else, and two spellings would let them drift.
_NOT_DERIVABLE_LINE = ("not-derivable: 2026-09-19 constitutively the "
                       "operator's — a preference about scope, decided by no "
                       "precedent, ledger entry or audit")


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


def _decl_run_with_templates(templates: dict, **kw) -> Fired:
    """`_decl_run`, over a SCRATCH template registry monkeypatched onto
    `workflows.registry_dir` — the real registry ships holding only
    `.gitkeep`, and `binding_template_missing`'s row needs at least one
    template that genuinely resolves so its CONTROL differs from its
    plant in the one property under test, not in every named template
    being absent from the real, empty registry."""
    from . import workflows as workflows_mod

    reg = Path(tempfile.mkdtemp(prefix="lifecycle-tmplreg-"))
    try:
        for tid, body in templates.items():
            (reg / f"{tid}.md").write_text(body, encoding="utf-8")
        orig = workflows_mod.registry_dir
        workflows_mod.registry_dir = lambda: reg
        try:
            return _decl_run(**kw)
        finally:
            workflows_mod.registry_dir = orig
    finally:
        shutil.rmtree(reg, ignore_errors=True)


def _items_run(items_text: str, prefix: str = "xx") -> Fired:
    with _Scratch(items_text=items_text) as s:
        buf = []
        code = items_mod.check_file(s.dir / "ITEMS.md", buf.append, prefix=prefix)
        return Fired(code, "\n".join(buf))


def _arc_body_run(text: str, slug: str = "freeze") -> Fired:
    """`arcs.parse_arc` over one body's text — no scratch repo needed.

    THE PARSER IS THE WHOLE SUBJECT HERE, as `_items_run`'s is: an arc body's
    shape is a property of its own text, and standing a repo up around it
    would add failure modes the row is not about. The exit code is derived
    the way every other verb derives one — problems mean FINDING — rather
    than asserted, so this row reads the same contract the verb will.
    """
    from . import arcs as arcs_mod
    _arc, problems = arcs_mod.parse_arc(text, slug)
    out = "\n".join(f"FINDING [{row}] {msg}" for row, _line, msg in problems)
    return Fired(exits.FINDING if problems else exits.CLEAN, out)


#: A well-formed arc body, used as this family's CONTROL and as the base every
#: plant mutates. Spelled once: two spellings of "a good body" drift, and the
#: drift would land in the control, which is the arm that decides whether a
#: plant proved anything.
_GOOD_ARC_SLOTS = {
    "goal": "find the freeze root cause",
    "stage": "narrowing the thread chain",
    "narrowing": "eliminative — three candidates left",
    "premises": "the tracer fires on every frame",
    "beliefs": "b1: RHIThread blocks first (basis: 11 captures)",
    "yield": "0",
}


def _good_arc_body(**over) -> str:
    from . import arcs as arcs_mod
    slots = dict(_GOOD_ARC_SLOTS)
    slots.update(over)
    return arcs_mod.render_arc("freeze", slots, items_mod.SCHEMA_FLOOR)


def _blocker_graph_run(items_text: str, prefix: str = "xx") -> Fired:
    """`check_blocker_graph` over a scratch carrier — no done home needed,

    the same reason `_items_run` needs none: the two computable shapes
    (a cycle, a chain terminating in a literal `evidence false`) are both
    properties of the LIVE carrier alone."""
    parsed = items_mod.parse(items_text)
    buf = []
    code = items_mod.check_blocker_graph(parsed, buf.append, prefix=prefix)
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


def _schema_apply_run(*, items_head: str, split: bool) -> Fired:
    """A `migrate --schema-from --apply` over a scratch repo (lc-168).

    THE FIRING INPUT HERE IS A DEFECTIVE WRITER, NOT REPO CONTENT, and that is
    stated rather than disguised. Once the plan and the write resolve the head
    through ONE body (lc-205), no carrier this repo can hold makes them
    disagree — which is the fix working. The read-back exists to catch the
    CODE going wrong again, so the only faithful plant is a writer that
    targets the wrong line.

    `schema_head` is patched to report the correct NUMBER at a WRONG INDEX.
    That is lc-205's actual shape rather than an invented one: the reader
    found the head, the plan was right, and the write landed somewhere else —
    which is why the run printed `written:` over a carrier it had not changed.
    The number stays correct so the PLAN is untouched and the arms differ in
    the write alone.
    """
    from . import declaration as decl_mod
    from . import migrate as migrate_mod

    doc = json.loads(json.dumps(GOOD_FULL_DECLARATION))
    doc["schema"] = 1

    real = decl_mod.schema_head

    def wrong_index(text, name="the carrier"):
        i, n, why = real(text, name)
        if i is None:
            return i, n, why
        # The head is REPORTED correctly and TARGETED wrongly — the plan is
        # untouched and only the write lands elsewhere.
        return len(text.split("\n")) - 1, n, why

    if split:
        migrate_mod.decl.schema_head = wrong_index
    try:
        return _cli(["migrate", "--schema-from", "1", "--apply"],
                    declaration=doc,
                    items=items_head + "\n\n## xx-1\nrequirement: a body\n",
                    done="schema: 1\n",
                    ledger_text="schema: 1\n")
    finally:
        migrate_mod.decl.schema_head = real


def _kind_trigger_unknown_verb() -> dict:
    """A trigger naming a verb this build does not have (lc-168).

    `item clsoe` is a plausible misspelling rather than nonsense, because that
    is the shape this refusal is for: a declaration whose WHEN is stated and
    unreachable reads exactly like one that is simply quiet, and the
    misspelling is how it happens.
    """
    d = json.loads(json.dumps(GOOD_DECLARATION))
    d["kinds"]["items"]["trigger"] = "verb item clsoe"
    return d


def _decl_with_binding(binding: dict) -> dict:
    d = json.loads(json.dumps(GOOD_DECLARATION))
    d["template-bindings"] = binding
    return d


def _kind_lane_nope() -> dict:
    d = json.loads(json.dumps(GOOD_DECLARATION))
    d["kinds"]["items"]["reader"] = ["lane: nope"]
    return d


_GOOD_KW = dict(declaration=GOOD_DECLARATION, gitignore="", laws_lines=10)

def _verify_run(commands: str) -> Fired:
    """Run `lifecycle verify` over a scratch repo whose laws file declares
    `commands` as its verify block, and render the verdict as the CLI would.

    THE LAWS FILE IS `LAWS.md` HERE, not CLAUDE.md, because that is what
    `GOOD_DECLARATION` names — the verb resolves the laws file THROUGH the
    declaration, so a row hardcoding a filename would test a path the verb
    does not use.
    """
    from . import verify as verify_mod

    class _Args:
        list = False
        timeout = 30

    with _Scratch(declaration=GOOD_DECLARATION, gitignore="") as s:
        (s.dir / "LAWS.md").write_text(
            "# laws\n\n## Verify\n\n```bash\n" + commands + "\n```\n",
            encoding="utf-8")
        said = []
        code = verify_mod.cmd_verify(_Args(), said.append, s.dir,
                                     GOOD_DECLARATION)
        return Fired(code, "\n".join(said))


ROWS = [
    Row(
        ident="verify_check_failed",
        refusal="a registered verify command RAN and returned non-zero",
        firing_input="a laws file whose `## Verify` block names a command "
                     "that exits non-zero (`false`), beside one that passes",
        expect=exits.FINDING,
        fire=lambda: _verify_run("true\nfalse"),
        # The control differs in the ONE line under test — the failing
        # command becomes a passing one — not in whether a verify block
        # exists at all. A control with no block would answer COULD NOT
        # VERIFY, which differs from the plant for the wrong reason and
        # proves nothing about this row.
        control=lambda: _verify_run("true\ntrue"),
    ),
    Row(
        ident="verify_expectation_wrong",
        refusal="a registered command's declared `# expect:` does not match "
                "what it actually did",
        firing_input="a laws file whose `## Verify` block names a command "
                     "that runs CLEAN while its trailing comment declares "
                     "`# expect: ran-failed` — the silent direction (a "
                     "declared failure quietly starting to pass) that "
                     "trained this repo's own readers to discount a real "
                     "red for a month",
        expect=exits.FINDING,
        fire=lambda: _verify_run("true  # expect: ran-failed"),
        # The control differs in the EXPECTATION TOKEN ALONE over an
        # identical command with an identical actual verdict (`true`,
        # ran-clean) — the pair isolates the expectation check itself,
        # never the command's own outcome. A failing command in the
        # control would exit FINDING via `verify_check_failed` for a
        # different reason and prove nothing about this row.
        control=lambda: _verify_run("true  # expect: ran-clean"),
    ),
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
        ident="migration_readback_disagrees",
        refusal="a schema apply whose ARTIFACT disagrees with what it reported",
        firing_input="a carrier head the writer leaves unchanged while the run "
                     "prints `written:` for it — lc-205's own shape",
        expect=exits.FINDING,
        fire=lambda: _schema_apply_run(items_head="schema : 1", split=True),
        # The control is the SAME apply over the SAME repo with the writer
        # WHOLE: the head is rewritten, the read-back agrees, APPLIED is
        # claimed. What separates the two is whether the write landed — not
        # whether a write was attempted, which both arms do.
        control=lambda: _schema_apply_run(items_head="schema: 1", split=False),
    ),
    Row(
        ident="trigger_verb_unknown",
        refusal="a kind whose trigger names a verb this build does not have",
        firing_input="`trigger: verb item clsoe` — a misspelled command path",
        expect=exits.FINDING,
        # The control is the SAME kind with the SAME stage present and
        # correctly spelled, so what separates the two is the verb's existence
        # and nothing else — not the stage being declared, which both share.
        fire=lambda: _decl_run(declaration=_kind_trigger_unknown_verb(),
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
        ident="binding_slot_unbound",
        refusal="a `template-bindings` entry with any slot whose value is "
                "UNKNOWN — an explicit unanswered slot, never a default",
        firing_input="a binding for `t1` holding `{\"a\": \"UNKNOWN\"}`",
        expect=exits.FINDING,
        fire=lambda: _decl_run_with_templates(
            {"t1": "Slots: a\n\nprocedure text\n"},
            declaration=_decl_with_binding({"t1": {"a": "UNKNOWN"}}),
            gitignore="", laws_lines=10),
        # The SAME binding, filled: the arms differ in the slot's value
        # alone, and both name a template that genuinely resolves so
        # `binding_template_missing` cannot fire in either arm.
        control=lambda: _decl_run_with_templates(
            {"t1": "Slots: a\n\nprocedure text\n"},
            declaration=_decl_with_binding({"t1": {"a": "filled-value"}}),
            gitignore="", laws_lines=10),
        stage="wave 2",
    ),
    Row(
        # CORRECTED 2026-08-26 (the judgment desk's own defect): the first
        # cut of `binding_slot_unbound` fired only on a PRESENT value equal
        # to UNKNOWN. This row is the discriminating arm that proves the
        # fix does something — a required key ABSENT from the binding
        # entirely (a template gaining a slot after the binding was
        # written) — and it is the arm that matters: under the pre-
        # correction code this plant read CLEAN, indistinguishable from a
        # complete binding.
        ident="binding_slot_unbound_absent_key",
        finding_row="binding_slot_unbound",
        refusal="the SAME finding as `binding_slot_unbound` above, on its "
                "second firing input: a required slot ABSENT from the "
                "binding entirely, with no UNKNOWN value to see — the "
                "restated-comparison-basis drift this lane's own no-index "
                "decision exists to prevent, one level down",
        firing_input="a binding for `t1` holding only `{\"a\": \"filled\"}` "
                     "where the template declares `Slots: a, b`",
        expect=exits.FINDING,
        fire=lambda: _decl_run_with_templates(
            {"t1": "Slots: a, b\n\nprocedure text\n"},
            declaration=_decl_with_binding({"t1": {"a": "filled"}}),
            gitignore="", laws_lines=10),
        # The SAME template, WITH `b` present and filled: the arms differ
        # in the missing key alone.
        control=lambda: _decl_run_with_templates(
            {"t1": "Slots: a, b\n\nprocedure text\n"},
            declaration=_decl_with_binding({"t1": {"a": "filled",
                                                    "b": "also-filled"}}),
            gitignore="", laws_lines=10),
        stage="wave 2",
    ),
    Row(
        ident="binding_template_missing",
        refusal="a `template-bindings` entry naming a template with no "
                "file under `plugin/workflows/` — nothing dangles, in "
                "either direction: a lane naming a missing workflow "
                "already fails, and now so does a binding naming a "
                "missing template",
        firing_input="a binding for `nope`, no `nope.md` in the registry",
        expect=exits.FINDING,
        fire=lambda: _decl_run_with_templates(
            {},
            declaration=_decl_with_binding({"nope": {}}),
            gitignore="", laws_lines=10),
        # The SAME binding, naming a template that DOES exist (with zero
        # required slots, matching the empty binding body): the arms
        # differ in the template's presence alone.
        control=lambda: _decl_run_with_templates(
            {"nope": "no Slots line — zero required slots\n"},
            declaration=_decl_with_binding({"nope": {}}),
            gitignore="", laws_lines=10),
        stage="wave 2",
    ),
    Row(
        ident="binding_template_unparsable",
        refusal="a `template-bindings` entry naming a template whose FILE "
                "exists but whose `Slots:` header does not parse — a "
                "template that cannot be read has no required-slot set to "
                "bind against, exactly as `workflow bind` itself refuses "
                "to proceed against it",
        firing_input="a binding for `bad`, `bad.md` present with "
                     "`Slots: a, Bad-Name!`",
        expect=exits.FINDING,
        fire=lambda: _decl_run_with_templates(
            {"bad": "Slots: a, Bad-Name!\n\nprocedure\n"},
            declaration=_decl_with_binding({"bad": {"a": "filled"}}),
            gitignore="", laws_lines=10),
        # The SAME template id, with a `Slots:` line that DOES parse: the
        # arms differ in the header's own well-formedness alone.
        control=lambda: _decl_run_with_templates(
            {"bad": "Slots: a\n\nprocedure\n"},
            declaration=_decl_with_binding({"bad": {"a": "filled"}}),
            gitignore="", laws_lines=10),
        stage="wave 2",
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
    Row(
        ident="arc_shape",
        refusal="an arc body whose shape is broken — a slot missing, a slot "
                "written twice, or a narrowing whose FORM is not one the "
                "vocabulary declares",
        firing_input="an arc body with no `yield:` line",
        expect=exits.FINDING,
        # THE PLANT DROPS A SLOT rather than mangling one, because a missing
        # slot is the shape this carrier's own discipline is about: a blank
        # is the undeclared-stage failure at arc scale, a plausible face on a
        # gap. The narrowing-form arm is a SECOND firing input of the same
        # refusal and is proven in test_arcs; this row takes the one an
        # author reaches by accident.
        fire=lambda: _arc_body_run("\n".join(
            ln for ln in _good_arc_body().splitlines()
            if not ln.startswith("yield:"))),
        control=lambda: _arc_body_run(_good_arc_body()),
    ),
    Row(
        ident="grade_arm_malformed",
        finding_row="unknown_grade_read",
        # A SECOND FIRING INPUT OF ONE REFUSAL, not a second refusal — the
        # census's third answer reached by the other road. `unknown_grade_read`
        # fires on a word nobody registered; this fires on a word that CLAIMS
        # the registered out-of-vocabulary arm and gets its form wrong.
        #
        # WHY THIS ROW AND NOT THE ONE THE DESIGN NAMED. The locked design
        # asked for a row proving each registration's OOV value renders apart
        # from its members. That row's firing input would have to be a
        # constructed registry object, and no carrier, declaration or file a
        # repo can write produces one — so its green would assert a property
        # of this package's own source, which law 22 says to delete rather
        # than register (the shape V12 already found once in this part). The
        # rendering invariant lives in the unit layer instead, where its own
        # control is that a member does NOT render apart from itself.
        # Superseded on the record, ledger 2026-09-19, before this was built.
        #
        # WHAT MAKES THIS ONE ADMISSIBLE: `grade: cannot-express` with no date
        # is repo-writable data. It is also the failure that matters, because
        # it is the one an AUTHOR reaches for — the arm is the door somebody
        # opens deliberately, and an instance that lands undated can never be
        # aged, so the drain could never watch the count reach zero while the
        # carrier showed a recorded state.
        refusal="a grade CLAIMING the out-of-vocabulary arm whose form is "
                "malformed — neither a member nor a well-formed instance, so "
                "it is read as the census's third answer rather than counted "
                "as a recorded cannot-express",
        firing_input="a file line with `grade: cannot-express` (no date, no "
                     "reason)",
        expect=exits.COULD_NOT_VERIFY,
        fire=lambda: _items_run(
            GOOD_ITEMS.replace("grade: READY", "grade: cannot-express")),
        # THE CONTROL IS THE WELL-FORMED ARM, never a plain member. Against a
        # member this row would pass on a build that had no arm at all; the
        # claim is specifically that the WELL-FORMED arm is accepted while the
        # malformed one is not, and only this pair separates those.
        control=lambda: _items_run(GOOD_ITEMS.replace(
            "grade: READY",
            "grade: cannot-express(2026-09-19): no member names a wait on "
            "another repo's release")),
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
    # RETIRED FROM THIS LIST IN WAVE 2 (the L2c dispatch), now an
    # executable row below: "unbound required slot" -> `binding_slot_
    # unbound`, plus `binding_template_missing` for the dangling-in-the-
    # OTHER-direction case (a binding naming a template with no file) that
    # this list never named at all.
    ("lane body over one screen", "lanes' BODIES are wave 2 — this build "
                                  "parses `Trigger:` and reports the other "
                                  "three parts by presence, so it has no "
                                  "one-screen cap to fire"),
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
    "schema": items_mod.SCHEMA_FLOOR, "id-prefix": "xx", "public": False,
    "laws": "LAWS.md",
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
            "trigger": "verb item add",
        },
        "done bodies": {
            "home": "ITEMS-DONE.md",
            "writer": "verb:item close",
            "reader": ["verb:item check", "verb:retire"],
            "staleness": "none, declared why: a closure record is history",
            "exit": {"action": "compact",
                     "recording-act": "a ledger decision line naming the range"},
            "growth": "compacted — done bodies fold on the retire lane's rule",
            "trigger": "verb item close",
        },
        "ledger lines": {
            "home": "LEDGER.md",
            "writer": "verb:ledger add, session",
            "reader": ["verb:ledger rejected"],
            "staleness": "none, declared why: append-only decision history",
            "exit": {"action": "never", "recording-act": "compaction only"},
            "growth": "unbounded-with-reason — one line per decision event and "
                      "no bodies; the decision rate is the control",
            "trigger": "verb ledger add",
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
            "trigger": "none, declared why: a law is minted by a session when an incident earns it, and no predicate detects an unwritten law — the reason this kind is buttonless is that the judgment IS the trigger",
        },
    },
}

#: A carrier head whose conservation identity balances against ONE live item.
SEED_ITEMS = f"""schema: {items_mod.SCHEMA_FLOOR}
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

EMPTY_ITEMS = (f"schema: {items_mod.SCHEMA_FLOOR}\n"
               "baseline: 0\nadded: 0\ncompacted: 0\n")
EMPTY_DONE = f"schema: {items_mod.SCHEMA_FLOOR}\n"

#: THE SAME CARRIER WITH A SECOND BODY, built the way the `duplicate_id` row
#: already builds one: the seed block under another id, with `baseline` raised
#: so conservation balances. DERIVED from `SEED_ITEMS` rather than written out
#: again — a second copy of the block would be a second body for one fixture,
#: free to drift from the first the day either is edited.
#:
#: Its consumer is a control that must leave a kind HOLDING something after
#: its exit has fired (`_retire_growth`): with one body, compacting it empties
#: the home and the control passes for having nothing to check.
TWO_SEED_ITEMS = (
    SEED_ITEMS.replace("baseline: 1", "baseline: 2", 1).rstrip("\n") + "\n\n"
    + SEED_ITEMS.split("\n\n", 1)[1].replace("## xx-1", "## xx-2", 1))


def _blocked_block(ident: str, grade: str, blocker: str) -> str:
    return (f"\n{grammar.render_heading(ident)}\ngrade: {grade}\n"
            f"requirement: a blocker-form fixture block — LEDGER.md\n"
            "goal: mitigate\nwrite-set: tools/thing.py\n"
            "done-criterion: it goes red then green\nevidence: none yet\n"
            f"blocked-by: {blocker}\n")


#: A carrier carrying ALL FOUR of §3.1's blocker forms at once, so the row's
#: control is also the OVER-FIRE probe: `decision <q>`, `evidence <predicate>`
#: and NONE resolve against nothing BY DESIGN, and a check that could not tell
#: them from a dangling id would fire on legitimate work (R11). A fixture
#: carrying only the item form would score identically whether or not the
#: check got that distinction right.
FOUR_BLOCKER_ITEMS = (
    (f"schema: {items_mod.SCHEMA_FLOOR}\n"
     "baseline: 4\nadded: 0\ncompacted: 0\n")
    + _blocked_block("xx-1", "PARKED", "xx-9999")
    + _blocked_block("xx-2", "PARKED", "decision which window")
    + _blocked_block("xx-3", "PARKED", "evidence test -f /nonexistent")
    + _blocked_block("xx-4", "READY", "NONE")
)

#: lc-112's PAIR, and the one property between its arms is the SUPERSEDING
#: LINE: both blocks are READY with `blocked-by: NONE` and are parked by the
#: same argv, and only the first carries an `amended-blocked-by:` line. An arm
#: differing in the blocker value as well would prove whichever of the two the
#: reader assumed.
PARK_AMENDED_ITEMS = (
    (f"schema: {items_mod.SCHEMA_FLOOR}\n"
     "baseline: 1\nadded: 0\ncompacted: 0\n")
    + _blocked_block("xx-1", "READY", "NONE")
    + "amend-reason: 2026-09-12 the earlier wait was cleared by the "
      "retirement pass\namended-blocked-by: 2026-09-12 NONE\n"
)
PARK_UNAMENDED_ITEMS = (
    (f"schema: {items_mod.SCHEMA_FLOOR}\n"
     "baseline: 1\nadded: 0\ncompacted: 0\n")
    + _blocked_block("xx-1", "READY", "NONE")
)

#: lc-90's PAIR, and the one property between its arms is WHERE THE TARGET
#: SITS: `xx-1` is blocked by `xx-2` in both, and only the second has `xx-2`
#: closed. Both carriers hold two bodies against `baseline: 2`, so neither arm
#: can separate on conservation — an arm differing in the identity as well as
#: in the blocker's state would be a pair proving whichever of the two the
#: reader assumed.
BLOCKER_TARGET_LIVE_ITEMS = (
    (f"schema: {items_mod.SCHEMA_FLOOR}\n"
     "baseline: 2\nadded: 0\ncompacted: 0\n")
    + _blocked_block("xx-1", "READY", "xx-2")
    + _blocked_block("xx-2", "READY", "NONE")
)
BLOCKER_TARGET_CLOSED_ITEMS = (
    (f"schema: {items_mod.SCHEMA_FLOOR}\n"
     "baseline: 2\nadded: 0\ncompacted: 0\n")
    + _blocked_block("xx-1", "READY", "xx-2")
)
BLOCKER_TARGET_CLOSED_DONE = EMPTY_DONE + _blocked_block("xx-2", "DONE", "NONE")

#: lc-193's RING: `xx-1` and `xx-2` block each other by id. Neither is
#: dangling and neither is DROPPED, so `check_blocker_targets` reads this
#: carrier CLEAN — the whole reason a GRAPH traversal is a different check
#: from an EDGE one.
CYCLE_ITEMS = (
    (f"schema: {items_mod.SCHEMA_FLOOR}\n"
     "baseline: 2\nadded: 0\ncompacted: 0\n")
    + _blocked_block("xx-1", "PARKED", "xx-2")
    + _blocked_block("xx-2", "PARKED", "xx-1")
)

#: lc-193's UNCLEARABLE CHAIN: `xx-1` blocked-by `xx-2`, `xx-2` blocked-by
#: the literal, provably-dead `evidence false`. `xx-1` is the ANCESTOR this
#: check must also name — it is exactly as unschedulable as `xx-2`, and
#: naming only `xx-2` would under-report the members the entry's own
#: done-criterion demands.
UNCLEARABLE_CHAIN_ITEMS = (
    (f"schema: {items_mod.SCHEMA_FLOOR}\n"
     "baseline: 2\nadded: 0\ncompacted: 0\n")
    + _blocked_block("xx-1", "PARKED", "xx-2")
    + _blocked_block("xx-2", "PARKED", "evidence false")
)


def _clause_block(ident: str, requirement: str) -> str:
    """A valid block whose REQUIREMENT is the caller's, every other slot fixed.

    Its own helper rather than a parameter on `_blocked_block`: that one's arms
    vary the BLOCKER and every row built on it reads that way, and a second
    varying slot there would make each of those rows say something it does not
    mean.
    """
    return (f"\n{grammar.render_heading(ident)}\ngrade: READY\n"
            f"requirement: {requirement}\n"
            "goal: mitigate\nwrite-set: tools/thing.py\n"
            "done-criterion: it goes red then green\nevidence: none yet\n"
            "blocked-by: NONE\n")


#: THE MOTIVATING CLAUSE (lc-22), copied from its source rather than described.
#: Source: dotfiles `claude/BACKLOG.md` at commit `bb8edd4`, the L10 entry whose
#: marker sits at line 163 — `git show bb8edd4:claude/BACKLOG.md`. That file was
#: retired 2026-09-12, so the pointer resolves at that commit and nowhere else.
#:
#: UNWRAPPED, AND THE TRANSFORMATION IS STATED because it is the one thing
#: between this fixture and the source bytes. The original is hard-wrapped
#: across six lines; a carrier slot value is ONE line by this repo's own shape
#: rule (`items.parse`: "a wrapped value is a shape break, not a long value").
#: A verbatim paste would therefore be an `item_shape` finding and the red
#: would belong to the ARRANGEMENT rather than to the defect. Newline-plus-
#: indent became one space, nothing else moved, and the MARKER never spanned a
#: line break — it sits entirely on line 163.
CARRIED_POINTER_CLAUSE = (
    "CARRIED POINTER (module 1 residue, 2026-08-26): accretion.md's "
    "backlog-doctrine bullet says \"(mechanism: lifecycle plugin, wave "
    "2)\" and its JOURNAL-stamped `(JOURNAL, …)` pointers are now "
    "checked by `corpus-pointer-check.py` (c17a82f); when wave 2 "
    "lands or is dropped, that parenthetical is re-worded to the "
    "shipped mechanism or removed — this entry is the carrier that "
    "moves with it."
)

#: lc-22's PAIR, and the one property between its arms is THE DECLARED MARKER.
#: The control is the SAME 384 bytes with `CARRIED POINTER` respelled as
#: ordinary prose, so it still carries "pointer", "carrier" and the sentence
#: "this entry is the carrier that moves with it" — which makes the control the
#: OVER-FIRE probe as well as the control. An arm that merely dropped the
#: subject would pass whether or not the predicate anchored on the marker, and
#: a predicate keyed on the loose words would refuse BOTH arms: measured over
#: this repo's own prose corpus, the loose form hits 252 lines and the declared
#: marker hits none (R11 — a guard that fires on legitimate work stops the
#: lane).
CARRIED_POINTER_ITEMS = (
    (f"schema: {items_mod.SCHEMA_FLOOR}\n"
     "baseline: 1\nadded: 0\ncompacted: 0\n")
    + _clause_block("xx-1", CARRIED_POINTER_CLAUSE)
)
CARRIED_POINTER_PROSE_ITEMS = (
    (f"schema: {items_mod.SCHEMA_FLOOR}\n"
     "baseline: 1\nadded: 0\ncompacted: 0\n")
    + _clause_block("xx-1", CARRIED_POINTER_CLAUSE.replace(
        "CARRIED POINTER", "a carried pointer", 1))
)

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
    # MARKED, since lc-167: the shared plant books a real item through the
    # real door, so it carries what every real booking now carries. `none
    # yet` would have been exempt (it reads as no evidence at all) and would
    # have made this fixture the one add in the repo that never exercises the
    # mark — a plant that dodges a rule it should be holding.
    "--evidence", "MEASURED the serving gate read its default config on "
                  "three runs; DERIVED that the deploy path never re-reads it",
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
        ident="decision_not_derivable_unstated",
        refusal="a `decision` blocker booked without saying why the question "
                "is NOT DERIVABLE from the record. Measured at this desk, two "
                "of six: lc-166's answer sat one kind over in this repo's own "
                "declaration, lc-158's in an audit the same desk had written "
                "and pushed, and both waited on the operator until they were "
                "told to decide what could be decided. The demand is for the "
                "STATEMENT, never the answer — a question that is "
                "constitutively the operator's passes on one line, the way "
                "`--join new` passes on a named absence (lc-169)",
        firing_input="`item add --blocked-by 'decision <question>'` with no "
                     "`--not-derivable`",
        expect=exits.FINDING,
        fire=lambda: _cli(GOOD_ADD + ["--blocked-by",
                                      "decision which window is canonical"]),
        # THE SAME ADD, THE SAME QUESTION, the statement supplied: the arms
        # differ in the statement alone, so neither `item add` nor the
        # `decision` type is what separates them. Its CONTENT is deliberately
        # the undecidable case — this row must pass on exactly the question
        # that belongs to the operator, or the refusal would be deciding the
        # kind split by predicate.
        control=lambda: _cli(GOOD_ADD + [
            "--blocked-by", "decision which window is canonical",
            "--not-derivable", "a preference with no precedent in the "
                               "ledger — constitutively the operator's"]),
        stage="wave 1, stage 4 (lc-169)",
    ),
    Row(
        ident="evidence_unmarked",
        refusal="an evidence slot written with no mark saying which of its "
                "claims this session RAN and which it CONCLUDED. Measured "
                "over a desk's full day of booking: every item booked from "
                "measured evidence held up, and the one booked from a "
                "just-formed conclusion was wrong within the hour and would "
                "have sent a lane to make a no-op change. Refused at the "
                "WRITE DOORS only — every entry booked before the rule "
                "carries an unmarked slot, and a check over the carrier "
                "would fire on all of them at once (lc-167)",
        firing_input="`item add --evidence <prose carrying none of "
                     "MEASURED / DERIVED / RECALLED / RELAYED>`",
        expect=exits.FINDING,
        fire=lambda: _cli(_mutate_add(
            "--evidence", "the deploy path re-reads the config on every "
                          "start, so the gate is looking at the wrong file")),
        # THE SAME ADD, THE SAME SENTENCE, one word longer: the claim is now
        # marked as the inference it is. The arms differ in the mark alone,
        # so neither `item add` nor the sentence's content is what separates
        # them — which is the whole predicate, since this check grades
        # PRESENCE and never truth.
        control=lambda: _cli(_mutate_add(
            "--evidence", "DERIVED the deploy path re-reads the config on "
                          "every start, so the gate is looking at the wrong "
                          "file")),
        stage="wave 1, stage 4 (lc-167)",
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
                                         "decision which window is canonical",
                                         "--not-derivable",
                                         "a preference with no ledger "
                                         "precedent"]),
        stage="wave 1, stage 4",
    ),
    Row(
        ident="blocker_predicate_broken",
        refusal="an `evidence` blocker whose predicate cannot work — prose "
                "booked into a shell slot, or a command that is BROKEN on "
                "one probe run. The item then waits in nobody's court: every "
                "`item ready` pass reports the predicate BROKEN and the board "
                "shows it only to whoever opens it (lc-130)",
        firing_input="`item add --blocked-by 'evidence <prose with an "
                     "unbalanced parenthesis>'` — `sh -n` exits 2 and nothing "
                     "is executed",
        expect=exits.FINDING,
        fire=lambda: _cli(GOOD_ADD + [
            "--blocked-by",
            "evidence an operating interval has passed since the burst "
            "(measure then cut: the timing rule; the next review is the "
            "consumer"]),
        # THE SAME VERB, THE SAME BLOCKER TYPE, a predicate that parses and
        # WAITS: the arms differ in the predicate alone, so neither `item
        # add` nor the `evidence` type is what separates them. A control
        # using a `decision` blocker would have scored a lint that refuses
        # every evidence predicate identically.
        #
        # RE-SPELLED FOR lc-164, and the old spelling is why this note is
        # here. The control read `evidence test -f /etc/hostname` — a
        # predicate that parses and exits 0 — chosen when 0 and 1 were the
        # same answer to this lint. lc-164 made 0 a refusal of its own, so
        # that control would have gone red and read as THIS row breaking.
        # The exit-1 spelling keeps the property the control was chosen for
        # (parses, is not refused) under a predicate the sibling row does
        # not claim.
        control=lambda: _cli(GOOD_ADD + [
            "--blocked-by", "evidence test -f /nonexistent-lifecycle-probe"]),
        stage="wave 1, stage 4 (lc-130)",
    ),
    Row(
        ident="blocker_predicate_satisfied_at_booking",
        refusal="an `evidence` blocker whose predicate EXITS 0 on its booking "
                "run — the blocker mapping reads that as evidence ARRIVED, so "
                "the item is blocked by nothing. Either it is schedulable "
                "today and the blocker is noise, or the predicate cannot fail "
                "and the item reads UNBLOCKED forever while what it waits for "
                "has not happened. Both are reported because the mint cannot "
                "tell them apart, and neither is detectable later: `item "
                "ready` sees the same 0 on every pass (lc-164)",
        firing_input="`item add --blocked-by 'evidence <a clause true for "
                     "every input>'` — the measured incident piped a `pgrep` "
                     "through `head -0`, which emits nothing, so `test -z` "
                     "held whatever was running",
        expect=exits.FINDING,
        fire=lambda: _cli(GOOD_ADD + [
            "--blocked-by",
            "evidence test -z \"$(printf 'a-process' | head -0)\""]),
        # THE SAME VERB, THE SAME BLOCKER TYPE, the same `head -0` SHAPE —
        # and the pipeline's output is NOT discarded, so the predicate can
        # answer either way and answers 1 here. The arms differ in the one
        # thing the refusal is about: whether the booking run could have come
        # back anything but 0. A control spelled with an unrelated predicate
        # would have scored a lint that refuses every evidence blocker.
        control=lambda: _cli(GOOD_ADD + [
            "--blocked-by",
            "evidence test -z \"$(printf 'a-process' | head -1)\""]),
        stage="wave 1, stage 4 (lc-164)",
    ),
    Row(
        ident="closed_ref_unresolvable",
        refusal="`item close --ref` naming something that is not a commit in "
                "this repo — a closure record is written once onto a body "
                "that then stops being edited, so an unresolvable ref there "
                "is permanent and reads exactly like a good one (lc-44)",
        firing_input="`item close xx-1 --ref <a 40-hex sha no object has>`",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "close", "xx-1", "--ref",
                           "0123456789abcdef0123456789abcdef01234567"],
                          items=SEED_ITEMS),
        # THE SAME CLOSE with a ref that DOES resolve — the arms differ in
        # the ref alone, so neither the close nor the flag is what separates
        # them. `HEAD` rather than a literal sha because the scratch repo's
        # own commit is not knowable from here.
        control=lambda: _cli(["item", "close", "xx-1", "--ref", "HEAD"],
                             items=SEED_ITEMS),
        stage="wave 1, stage 5",
    ),
    Row(
        # A SIBLING ROW, NOT A SECOND REFUSAL (lc-120). `item
        # supersede-closure` writes a ref onto a body that has ALREADY stopped
        # being edited, so the cause and the repair are `closed_ref_
        # unresolvable`'s exactly — a permanent dangling ref that reads like a
        # good one, cleared by giving one that resolves. §3.8c splits a row
        # only where the sites yield different ANSWER CLASSES, and these do
        # not; the mirror case is lc-30, where two refusals with OPPOSITE
        # repairs had to stop sharing a name because the operator was handed
        # one cause for two defects. Two firing inputs, one refusal, declared
        # through `finding_row` rather than derived by string surgery.
        ident="closure_pointer_ref_unresolvable",
        finding_row="closed_ref_unresolvable",
        refusal="`item supersede-closure --ref` naming something that is not "
                "a commit in this repo — the pointer is appended to a CLOSED "
                "body, which nothing amends afterwards, so a ref that resolves "
                "to nothing there is permanent (lc-120)",
        firing_input="`item supersede-closure xx-2 --ref <a 40-hex sha no "
                     "object has>` against a done home holding xx-2",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "supersede-closure", "xx-2", "--ref",
                           "0123456789abcdef0123456789abcdef01234567",
                           "--line", "the closure reason was falsified the "
                                     "same hour"],
                          done=BLOCKER_TARGET_CLOSED_DONE),
        # THE SAME VERB ON THE SAME BODY WITH THE SAME LINE, and a ref that
        # DOES resolve. The arms differ in the ref alone, so neither the verb
        # nor the flag nor the closed body is what separates them — the
        # control would otherwise score identically against a build that
        # refused every supersede-closure.
        control=lambda: _cli(["item", "supersede-closure", "xx-2", "--ref",
                              "HEAD",
                              "--line", "the closure reason was falsified the "
                                        "same hour"],
                             done=BLOCKER_TARGET_CLOSED_DONE),
        stage="wave 1, stage 5 (lc-120)",
    ),
    Row(
        ident="close_over_live_blocker",
        refusal="a DONE close over an item-id blocker whose target has NOT "
                "closed — the move clears the `blocked-by:` line and a closed "
                "body can never be amended, so a wait ended this way is a "
                "dependency deleted rather than met (lc-90). The target's own "
                "closure is what discharges it; a DROP records the wait as "
                "abandoned instead, and a `decision` blocker keeps exactly the "
                "moot record it already got",
        firing_input="`item close xx-1` where xx-1 is blocked by xx-2 and "
                     "xx-2 is still live",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "close", "xx-1"],
                          items=BLOCKER_TARGET_LIVE_ITEMS),
        # THE SAME CLOSE over the SAME blocker, with xx-2 CLOSED: the arms
        # differ in the target's state alone, so neither the close nor the
        # blocker's presence is what separates them. A control with no blocker
        # at all would pass whether or not this refusal read the target.
        control=lambda: _cli(["item", "close", "xx-1"],
                             items=BLOCKER_TARGET_CLOSED_ITEMS,
                             done=BLOCKER_TARGET_CLOSED_DONE),
        stage="wave 1, stage 5",
    ),
    Row(
        ident="close_carries_pointer",
        refusal="a close whose live body carries a DECLARED forward-carrier "
                "clause — the uppercase marker `CARRIED POINTER`, an optional "
                "parenthetical, then a colon. The move files that body in the "
                "closure home, and the obligation the clause declares then "
                "reads as discharged because its carrier is filed as "
                "discharged (lc-22). WHAT THE PREDICATE ESTABLISHES is the "
                "clause's PRESENCE in the body the move would file, and no "
                "more: whether the pointer is still owed is what the clause "
                "DECLARES, never anything this check measured. Cleared by "
                "removing the clause from the body, or by splitting the "
                "residue into its own item, which takes the clause with it; "
                "there is no override flag, because a bypass files the clause "
                "in the closure home, which is the one outcome the refusal "
                "exists to prevent",
        firing_input="`item close xx-1` where xx-1's requirement carries the "
                     "lc-22 clause in its own words, from dotfiles `bb8edd4`",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "close", "xx-1"],
                          items=CARRIED_POINTER_ITEMS),
        # THE SAME 384 BYTES with the marker respelled as ordinary prose. The
        # arms differ in the DECLARED MARKER alone, so neither the subject
        # matter nor the words "carrier" and "pointer" is what separates them
        # — which is what makes this control the over-fire probe as well.
        control=lambda: _cli(["item", "close", "xx-1"],
                             items=CARRIED_POINTER_PROSE_ITEMS),
        stage="wave 1, stage 5",
    ),
    Row(
        ident="blocker_unstorable",
        refusal="a `decision` blocker the LEDGER cannot store — the question "
                "would be written into the carrier and nothing could ever "
                "answer it, because `ledger add decision` refuses the line "
                "and `item ready` resolves the blocker by question-slot "
                "equality (lc-40, lc-49)",
        firing_input="`item add --blocked-by 'decision <q> — <q>'`, the "
                     "ledger's own slot separator inside the question",
        expect=exits.FINDING,
        fire=lambda: _cli(GOOD_ADD + [
            "--blocked-by",
            "decision does the desk accept X — or does it not"]),
        # THE SAME QUESTION, REPHRASED — the arms differ in the separator
        # alone. A control differing in the TYPE or in the whole sentence
        # would be red for a neighbouring reason and would prove nothing
        # about storability.
        control=lambda: _cli(GOOD_ADD + [
            "--blocked-by",
            "decision does the desk accept X or does it not",
            "--not-derivable", "a preference with no ledger precedent"]),
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
        ident="dangling_reference_carrier",
        finding_row="dangling_reference",
        # THE THIRD firing input of ONE refusal, not a third refusal. The
        # declaration half resolves a typed reference; `dangling_reference_item`
        # resolves an id at the WRITE path; this resolves one already sitting
        # in the carrier. `finding_row` declares the family, so a mutation at
        # this site darkens this row alone and prove-rows reads that as the
        # honest case rather than a stray.
        # THE LABEL NAMES THE ITEM TYPE, not the typed-reference family, and
        # that is deliberate: "dangling typed reference" is the exact phrase
        # `check_routes` records as its motivating case (roster.py:136) — a
        # text claiming the family while the code reached one member. The
        # declaration half carries a `route_set` and is graded on it; this
        # row has none and, being a one-site refusal, has no vocabulary for
        # one to grade, so nothing mechanical stands between its label and
        # that same overclaim. The label is narrowed by hand instead, in the
        # sibling's idiom (`dangling_reference_item` names which half it is).
        refusal="dangling ITEM-id reference over the CARRIER — the ITEM half "
                "of §3.9's row, never the declaration half's other typed "
                "forms: a `blocked-by "
                "<item-id>` already in the file naming an id no home holds, "
                "or naming one the done home holds as DROPPED (lc-29: the "
                "same reach as the write path, which refuses both; an "
                "id-blocker resolves on its target's DONE, and neither a "
                "missing target nor a dropped one can reach it). "
                "The write path is not the only path in: a merge or a hand "
                "edit reaches the file without passing it, and the result is "
                "a PERMANENT SILENT PARK — the block never surfaces in `item "
                "ready` because it reads as blocked, and nothing says the "
                "wait is fictional",
        firing_input="`item check` over a carrier whose PARKED block waits on "
                     "`xx-9999`, beside blocks carrying the three other "
                     "blocker forms",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "check"], items=FOUR_BLOCKER_ITEMS),
        # The SAME carrier with the SAME four forms, the item blocker
        # retargeted to the live `xx-4`: the arms differ in the ID ALONE. The
        # control is doing double duty — it also proves the other three forms
        # stay quiet, which is the half that decides whether this ships.
        control=lambda: _cli(["item", "check"],
                             items=_mutate(FOUR_BLOCKER_ITEMS,
                                           "blocked-by: xx-9999",
                                           "blocked-by: xx-4")),
        stage="wave 3 (lc-28, superseding lc-15)",
    ),
    Row(
        ident="blocker_softlock",
        refusal="the blocker GRAPH traversed, never just its edges (lc-193) "
                "— a CYCLE among item-id blockers, or a CHAIN of them "
                "terminating in a member whose evidence predicate is the "
                "literal command `false` (POSIX-guaranteed to exit 1 "
                "forever, never merely not-true-yet). Either shape is a set "
                "of items that can NEVER become schedulable while `item "
                "ready` renders each as ordinary BLOCKED work and "
                "`check_blocker_targets` above reports the edges CLEAN — "
                "the operator's player-loop frame's SOFTLOCK, lc-14's "
                "'permanent silent park' reached by a different route",
        firing_input="`check_blocker_graph` over a carrier where two items "
                     "block each other by id (`xx-1` blocked-by `xx-2`, "
                     "`xx-2` blocked-by `xx-1`) — CYCLE_ITEMS",
        expect=exits.FINDING,
        fire=lambda: _blocker_graph_run(CYCLE_ITEMS),
        # THE RING'S OWN CLOSING EDGE ALONE differs: `xx-2` no longer points
        # back at `xx-1`, so the two blocks are ordinary serialization (one
        # item waiting on another that can still close) rather than a ring
        # with nothing outside it to supply either member's clearance. An
        # arm that also changed which id `xx-1` names would be red for a
        # neighbouring reason and would prove nothing about the cycle.
        control=lambda: _blocker_graph_run(
            CYCLE_ITEMS.replace("blocked-by: xx-1\n", "blocked-by: NONE\n")),
        stage="lc-193",
    ),
    Row(
        ident="parked_without_typed_blocker",
        refusal="PARKED without a typed blocker",
        firing_input="`item park <id>` with prose only",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "park", "xx-1", "--blocked-by",
                           "we should think about it"], items=SEED_ITEMS),
        control=lambda: _cli(["item", "park", "xx-1", "--blocked-by",
                              "decision which window is canonical",
                              "--not-derivable", "a preference with no ledger precedent"],
                             items=SEED_ITEMS),
        stage="wave 1, stage 5",
    ),
    Row(
        ident="park_over_superseding_amendment",
        refusal="`item park` returning CLEAN over a blocker that would NOT "
                "govern — the base `blocked-by:` slot written while an "
                "`amended-blocked-by:` line supersedes it, so the grade moves "
                "to PARKED and the EFFECTIVE blocker is whatever the "
                "amendment says. The verb's success line is true about the "
                "slot it wrote and false about the item",
        firing_input="`item park <id> --blocked-by <typed>` on a block "
                     "carrying a superseding `amended-blocked-by:` line",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "park", "xx-1", "--blocked-by",
                           "decision which window is canonical",
                           "--not-derivable", "a preference with no ledger precedent"],
                          items=PARK_AMENDED_ITEMS),
        # The SAME park of the SAME block, the amendment group ALONE removed:
        # the arms differ in the superseding line and in nothing else, so the
        # refusal is the supersession and not the park path.
        control=lambda: _cli(["item", "park", "xx-1", "--blocked-by",
                              "decision which window is canonical",
                              "--not-derivable", "a preference with no ledger precedent"],
                             items=PARK_UNAMENDED_ITEMS),
        stage="wave 5 (lc-112)",
    ),
    Row(
        ident="amend_without_reason",
        refusal="an amendment with no recorded WHY — which is an in-place "
                "rewrite with a date on it, and the thing law 8 and the "
                "append-only ethic exist to keep out of the carrier",
        firing_input="`item amend <id> --goal <g>` with no `--reason`",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "amend", "xx-1", "--goal", "verify"],
                          items=SEED_ITEMS),
        # The SAME amendment WITH its reason: the arms differ in the reason
        # alone, so the refusal is the missing prose and not the amend path.
        control=lambda: _cli(["item", "amend", "xx-1", "--goal", "verify",
                              "--reason", "the goal was mis-recorded at "
                                          "intake"],
                             items=SEED_ITEMS),
        stage="wave 4 (lc-27)",
    ),
    Row(
        ident="promote_without_judgment",
        refusal="a promotion to READY with no record of WHO judged it and "
                "WHY — a grade that appeared. READY is a judgment (law 10) "
                "and the next reader cannot ask the desk that made it if the "
                "carrier does not say there was one",
        firing_input="`item promote <id>` with neither `--by` nor `--reason`",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "promote", "xx-1"], items=SEED_ITEMS),
        # The SAME promotion WITH both halves of the record: the arms differ
        # in the flags alone, so the refusal is the missing judgment and not
        # the promote path — which is a real risk here, because this verb is
        # new and a control that also refused would prove nothing.
        control=lambda: _cli(["item", "promote", "xx-1",
                              "--by", "the wave-4 desk",
                              "--reason", "the slots are filled and a fresh "
                                          "context could execute this now"],
                             items=SEED_ITEMS),
        stage="wave 4 (lc-39)",
    ),
    Row(
        ident="promote_while_blocked",
        refusal="a promotion over a STANDING blocker — READY recorded "
                "against a wait nobody cleared, which is then the thing a "
                "reader resolves through",
        firing_input="`item promote <id>` on an item whose `decision` blocker "
                     "no ledger line answers",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "promote", "xx-1",
                           "--by", "the wave-4 desk",
                           "--reason", "the slots are filled"],
                          items=_mutate(SEED_ITEMS, "blocked-by: NONE",
                                        "blocked-by: decision which window "
                                        "is canonical")),
        # The SAME promotion on the SAME item with nothing blocking it: the
        # arms differ in the blocker alone.
        control=lambda: _cli(["item", "promote", "xx-1",
                              "--by", "the wave-4 desk",
                              "--reason", "the slots are filled"],
                             items=SEED_ITEMS),
        stage="wave 4 (lc-39)",
    ),
    Row(
        ident="ready_with_unknown_slot_promote",
        finding_row="ready_with_unknown_slot",
        # THE SECOND FIRING INPUT of ONE refusal, not a second refusal. The
        # row below it reads a grade already written; this stops the grade
        # being written. One refusal — READY over a slot nobody recorded —
        # decided at two sites, so `finding_row` declares the family and a
        # mutation at either site darkens only its own row.
        refusal="READY over a slot nobody has ever written, at the WRITE "
                "path — the promotion is refused rather than reported after "
                "the fact",
        firing_input="`item promote <id>` on an item whose `goal` is UNKNOWN",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "promote", "xx-1",
                           "--by", "the wave-4 desk",
                           "--reason", "the slots are filled"],
                          items=_mutate(SEED_ITEMS, "goal: mitigate",
                                        "goal: UNKNOWN")),
        # The SAME promotion with the goal filled: the arms differ in the one
        # slot, exactly as the read-path row's pair does.
        control=lambda: _cli(["item", "promote", "xx-1",
                              "--by", "the wave-4 desk",
                              "--reason", "the slots are filled"],
                             items=SEED_ITEMS),
        stage="wave 4 (lc-39)",
    ),
    Row(
        ident="amend_nothing_to_amend",
        refusal="an amendment naming no slot — a reason line in the carrier "
                "and no value changed, which reads in every later diff as a "
                "correction that was made",
        firing_input="`item amend <id> --reason <why>` with no slot flag",
        expect=exits.FINDING,
        fire=lambda: _cli(["item", "amend", "xx-1", "--reason",
                           "the goal was mis-recorded at intake"],
                          items=SEED_ITEMS),
        # The SAME call with ONE slot named: the arms differ in whether a
        # value was given, never in the reason.
        control=lambda: _cli(["item", "amend", "xx-1", "--reason",
                              "the goal was mis-recorded at intake",
                              "--goal", "verify"],
                             items=SEED_ITEMS),
        stage="wave 4 (lc-27)",
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


#: The SAME body minus §3.3's fourth part, and nothing else (lc-12). Written
#: as its own literal rather than a `.replace()` over `_lane_body`: a plant
#: built by editing its own control is an expectation derived from the
#: artifact it grades, and it would follow that artifact wherever it moved.
#: Every LABELLED part is still here, which is the point — this is the body
#: the `startswith` scan calls complete.
def _lane_body_no_table(trigger: str) -> str:
    return (f"# lane: x\n\nDecides: nothing — this is a row's fixture\n"
            f"Trigger: {trigger}\n\nEnds: dropped\n")


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
        ident="lane_table_absent",
        refusal="a lane body carrying no decision table — §3.3 names FOUR "
                "parsed parts and the table is the one with NO label, so the "
                "`startswith` scan that finds the other three cannot reach "
                "it: the board printed every label it could find over a lane "
                "that routes nowhere, and exited CLEAN",
        firing_input="a lane carrying `Decides:`, `Trigger:` and `Ends:` and "
                     "no decision table; `lane list`",
        expect=exits.FINDING,
        fire=lambda: _lane_cli(["lane", "list"], roster_lines=["@repo"],
                               lanes=["x"],
                               lane_files={"x": _lane_body_no_table("exit 1")}),
        # The SAME lane WITH the table: the arms differ in that part alone,
        # both triggers are the quiet `exit 1`, and the control asserts
        # nothing about the probed property — so a FINDING arriving for any
        # other reason fails the pair rather than passing it.
        control=lambda: _lane_cli(["lane", "list"], roster_lines=["@repo"],
                                  lanes=["x"],
                                  lane_files={"x": _lane_body("exit 1")}),
        stage="wave 2 (lc-12)",
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
                             + ["--blocked-by", "decision which window",
                                "--not-derivable",
                                "a preference with no ledger precedent"]),
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
        ident="migrate_repeated_from",
        refusal="a repeated `--from` in ONE `migrate` invocation. argparse's "
                "plain dest OVERWRITES, so `--from A.md --from B.md` keeps "
                "B.md alone and silently discards A.md: the caller believes "
                "two sources were read and one was, at the entry point whose "
                "whole job is reading a source. A second source is `--merge`, "
                "which reads a second INVOCATION's carrier; this is one "
                "invocation naming two (lc-31)",
        firing_input="`migrate --from BACKLOG.md --from BACKLOG.md` — the "
                     "flag twice in one argv, counted from the RAW argv "
                     "because `args.from_carrier` by then holds the survivor "
                     "alone and cannot say how many there were",
        expect=exits.FINDING,
        fire=lambda: _migrate_run(from_sources=("BACKLOG.md", "BACKLOG.md")),
        # THE SAME MIGRATE NAMING THE SAME SOURCE ONCE: the arms differ in the
        # repeated flag alone, so neither the verb nor `--from` is what
        # separates them — strip the refusal and the two runs are the same
        # invocation, because argparse discards the first occurrence. A
        # control naming a DIFFERENT second source would differ in that path's
        # existence as well as in the repeat, and one changing the verb or the
        # flag would score a check that refuses every `migrate --from`
        # identically.
        control=lambda: _migrate_run(from_sources=("BACKLOG.md",)),
        stage="wave 1, stage 9 (lc-31)",
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
        ident="migration_ambiguous_closure",
        finding_row="migration_unclassified",
        # THE SECOND FIRING INPUT OF ONE REFUSAL, not a second refusal. Both
        # shapes below reach `migrate._refuse` and surface under
        # `migration_unclassified`, so `finding_row` declares the family and a
        # mutation at the ambiguity branch darkens this row alone.
        #
        # WHY IT IS ITS OWN ROW. `migration_unclassified`'s text names the
        # NO-RULE case — "an entry whose grade word no rule covers" — and that
        # sentence is FALSE of both shapes here: each entry's grade situation
        # is legible, and what the tool refuses is the CONFLICT between two
        # legible statements. A row whose text is narrower than what the code
        # routes through it hands the operator a wrong cause for their entry,
        # and it leaves the ambiguity branch with no mutation that darkens
        # anything — the row's plant being the no-rule case, disabling the
        # ambiguity branch changed no verdict at all (measured on a copy of
        # HEAD: `rows changed: NONE`, prove-rows FAILED).
        refusal="AMBIGUOUS about whether a source entry is CLOSED, in either "
                "of the two shapes the reader produces — a closure word "
                "(`DONE`, `DROPPED`) standing alone LATER in the title of a "
                "bullet carrying no grade word at its start, and an OPEN "
                "grade word sitting under the carrier's own closure heading. "
                "Neither is an uncovered grade word: the entry is refused "
                "because two legible statements about it disagree, and §4 row "
                "1 ranks neither over the other. Reported with its line and "
                "quoted in the run's output, written to neither successor "
                "home — a guess here would be a classification rule invented "
                "at this tier and afterwards indistinguishable from a rule",
        firing_input="a source carrier bullet with NO grade word at its start "
                     "whose title carries a closure word standing alone "
                     "later — `- **a bullet whose title says DONE mid-way.**`",
        expect=exits.FINDING,
        fire=lambda: _migrate_run(
            backlog="# old\n\n## Open\n\n- **a bullet whose title says DONE "
                    "mid-way.** body\n"),
        # The SAME bullet with a NON-closure word in the same position: the
        # arms differ in that one word, never in the entry's shape, its
        # section or whether it carries a grade word. A control that simply
        # dropped the mid-title word would pass against a reader that scans
        # nothing.
        control=lambda: _migrate_run(
            backlog="# old\n\n## Open\n\n- **a bullet whose title says TODO "
                    "mid-way.** body\n"),
        stage="wave 3 (lc-17 lane B — the row lane A's write set could not "
              "reach; unblocks lc-30)",
    ),
    Row(
        ident="merge_duplicate_body",
        refusal="`migrate --merge` where a source entry's HEADLINE is already "
                "carried by a body in the successor homes — the live carrier "
                "or the closed one. The merge appends, so writing it would "
                "book one piece of work twice under two ids, and the closed "
                "side is the silent half: a body that already closed comes "
                "back as open work with the closure that answered it one file "
                "away. Whether it is the same work booked twice or two items "
                "sharing a headline is the desk's call. The WHOLE RUN "
                "refuses and nothing is written: a merge is not idempotent, "
                "so writing the rest and reporting this one would leave the "
                "carrier half-merged and a re-run would write those bodies a "
                "second time. Scoped to the bodies already in the homes — an "
                "incoming source repeating itself is not what this row asks",
        firing_input="`migrate --from BACKLOG.md --merge` where `ITEMS.md` "
                     "already carries a block whose `requirement` headline "
                     "equals the source entry's",
        expect=exits.FINDING,
        fire=lambda: _migrate_run(merge=True, items=MERGE_TARGET_ITEMS),
        # The SAME populated carrier, the SAME flag, one WORD of the existing
        # headline changed. A control that merged into an EMPTY carrier would
        # pass against a checker that never reads the homes at all.
        control=lambda: _migrate_run(merge=True,
                                     items=MERGE_TARGET_ITEMS_OTHER),
        stage="wave 3 (lc-17 lane B3 — merge mode)",
    ),
    Row(
        ident="merge_source_self_duplicate",
        refusal="`migrate --merge` where two non-re-imported entries in the "
                "incoming source carry equal parsed HEADLINEs. The WHOLE RUN "
                "refuses and nothing is written: a merge appends, so writing "
                "the rest and reporting either entry would leave the carrier "
                "half-merged and a re-run would write those bodies twice",
        firing_input="`migrate --from BACKLOG.md --merge` where two source "
                     "entries carry the same parsed headline",
        expect=exits.FINDING,
        fire=lambda: _migrate_run(merge=True,
                                  backlog=MERGE_SOURCE_SELF_DUPLICATE),
        control=lambda: _migrate_run(merge=True,
                                     backlog=MERGE_SOURCE_SELF_DUPLICATE_OTHER),
        stage="wave 6 (lc-33 — the source's self-repeat, the reach "
              "merge_duplicate_body declines)",
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
    # --- `--retire-source`'s four preconditions (lc-86) ----------------------
    #
    # FOUR ROWS, NOT ONE. The flag asks for an irreversible act and the four
    # conditions have four different repairs — commit the carrier, declare a
    # laws file, re-migrate the unpinned blocks, drop the flag. A single
    # `retire_source_refused` would hand the operator one message for all
    # four, which is the row whose text is wider than what its sites decide.
    Row(
        ident="retire_source_not_writing",
        refusal="`--retire-source` on a run that writes no successor state — "
                "`--report-only`, or the `--schema-from` path, which reads no "
                "old carrier at all. Deleting the source there would leave "
                "the repo with NEITHER carrier: the old one gone and the new "
                "one never written",
        firing_input="`migrate --report-only` with `--retire-source`",
        expect=exits.FINDING,
        fire=lambda: _retire_run(report_only=True),
        # The SAME repo and the SAME flag, WITHOUT `--report-only`: the arms
        # differ in whether the run writes a successor and in nothing else. A
        # control that dropped `--retire-source` would pass against a build
        # that never checks the mode at all.
        control=lambda: _retire_run(),
        stage="wave 3 (lc-86)",
    ),
    Row(
        ident="retire_source_uncommitted",
        refusal="`--retire-source` over a carrier whose content is not in a "
                "commit. Every citation the migration writes resolves through "
                "`git cat-file -p <blob>`, and a blob in no commit dies with "
                "the file — the deletion would take the bodies with it and "
                "leave pointers to nothing. Both halves are the condition: "
                "TRACKED is not enough, the CONTENT read here must be the "
                "content committed",
        firing_input="`migrate --retire-source` where `BACKLOG.md` is "
                     "untracked, so `git rev-parse HEAD:BACKLOG.md` resolves "
                     "to nothing",
        expect=exits.FINDING,
        fire=lambda: _retire_run(commit_source=False),
        # The SAME carrier, the SAME flag, COMMITTED. The arms differ in the
        # commit and in nothing else — not in the file's content, not in the
        # mode, not in the declaration.
        control=lambda: _retire_run(commit_source=True),
        stage="wave 3 (lc-86)",
    ),
    Row(
        ident="retire_source_laws_absent",
        refusal="`--retire-source` where the declared `laws` file is not "
                "there to receive the deletion record. The record's home is "
                "the DECLARED laws file and never a filename this tool picks, "
                "so with none readable there is nowhere to write the "
                "justification — and a deletion with no record is the state "
                "the whole stage exists to prevent",
        firing_input="`migrate --retire-source` in a repo whose declaration "
                     "carries no `laws` value",
        expect=exits.FINDING,
        fire=lambda: _retire_run(laws_declared=False),
        # The SAME repo with the SAME laws FILE present, the declaration
        # naming it: the arms differ in the declared value alone.
        control=lambda: _retire_run(laws_declared=True),
        # THE PLANT IS THE UNDECLARED HALF, NOT THE ABSENT-FILE HALF, and the
        # roster's own instrument is why. The condition has two halves and the
        # code enforces both: `laws` must be declared (decided here, in
        # `migrate.retire_refusal`) and the file it names must be readable
        # (decided in `declaration.check_laws_present`, REUSED rather than
        # reimplemented). The second half is decided at the SAME SITE as
        # `laws_absent_could_not_verify`, so a plant keyed to it made
        # `prove-rows` disable one `path.is_file()` branch and darken both
        # rows — which correctly reads as "this mutation removed adjacent
        # machinery, so it proves nothing about any one row", and took a row
        # that had been PROVEN down with it (measured: 62 PROVEN before, 61
        # and one FAILED after). One site, one row: the absent-file half stays
        # proven by the row that owns that site, and this row proves the half
        # that is decided here. The other half is exercised end-to-end in
        # `test_migrate.RetireSource`.
        stage="wave 3 (lc-86)",
    ),
    Row(
        ident="retire_source_unpinned_anchor",
        refusal="`--retire-source` while the successor carrier still holds an "
                "anchor into the source carrying no ` at blob <sha>` pin. A "
                "bare `<path>:<line>` resolves against whatever the file "
                "holds, so once the file is gone it resolves against nothing "
                "— and NOTHING FAILS, which is why it is refused before the "
                "unlink instead of found afterwards. The ordinary cause is a "
                "`--merge` into a carrier an earlier build wrote, whose "
                "anchors predate the pin and are not this run's to rewrite",
        firing_input="`migrate --merge --retire-source` where `ITEMS.md` "
                     "already carries `evidence: BACKLOG.md:5-6` with no pin",
        expect=exits.FINDING,
        fire=lambda: _retire_run(merge=True, items=UNPINNED_ANCHOR_ITEMS),
        # The SAME carrier and the SAME flags with that one anchor PINNED —
        # the arms differ in the pin and in nothing else: same block, same id,
        # same provenance, same merge. A control over an EMPTY carrier would
        # pass against a build that never reads the homes.
        control=lambda: _retire_run(merge=True,
                                    items=PINNED_ANCHOR_ITEMS),
        stage="wave 3 (lc-86)",
    ),
    Row(
        ident="lane_new_exists",
        refusal="`lane new` refuses to overwrite an existing lane body — "
                "no silent overwrite, the same rule `init` applies to the "
                "declaration it writes",
        firing_input="`lane new x` where `lanes/x.md` already exists",
        expect=exits.FINDING,
        fire=lambda: _cli(["lane", "new", "x"],
                          lane_files={"x": _lane_body("exit 1")}),
        # The SAME existing file, WITH --force: the arms differ in the flag
        # alone.
        control=lambda: _cli(["lane", "new", "x", "--force"],
                             lane_files={"x": _lane_body("exit 1")}),
        stage="wave 2",
    ),
    Row(
        ident="lane_undeclared",
        refusal="§3.8b — a lane BODY the declaration does not list is "
                "UNREGISTERED. The registration invariant held one way only: "
                "a declared lane with no file was caught, a file with no "
                "declaration was invisible to every verb, so the router "
                "printed `declared lanes: 0 — EMPTY` over a tree carrying one",
        firing_input="`kind check` in a repo carrying `lanes/x.md` whose "
                     "declared `lanes` list is empty",
        expect=exits.FINDING,
        fire=lambda: _cli(["kind", "check"],
                          lane_files={"x": _lane_body("exit 1")}),
        # The SAME body on disk, DECLARED: the arms differ in the declaration's
        # `lanes` list alone, not in whether a lane file exists. A control that
        # simply omitted the file would pass whether or not the scan works.
        control=lambda: _cli(["kind", "check"], lanes=["x"],
                             lane_files={"x": _lane_body("exit 1")}),
        stage="wave 2 (lc-13)",
    ),
]


def _coverage_over_copy(*, plant: bool, word: str = "FINDING") -> Fired:
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
            # THE VERDICT WORD IS A PARAMETER because the scan now watches
            # two of them. Composed rather than written literally: this file
            # is excluded from the scan, but a literal here would still be
            # one more copy of a pattern the scan's own history says to keep
            # out of the source it reads.
            target.write_text(
                target.read_text(encoding="utf-8")
                + '\n\ndef _planted(out):\n'
                  f'    out("{word} [not_a_registered_row] planted")\n',
                encoding="utf-8")
        buf = []
        code = roster_mod.check_coverage(buf.append, root=d)
        return Fired(code, "\n".join(buf))
    finally:
        shutil.rmtree(d, ignore_errors=True)


#: A populated `ITEMS.md` whose one body carries the SAME headline the
#: default `_migrate_run` source entry carries — the state a merge must
#: refuse. The requirement keeps the `— record: <path>:<line>` tail a
#: migration writes, so the row exercises the title PARSE and not a bare
#: string equality that a tail would defeat.
MERGE_TARGET_ITEMS = f"""schema: {items_mod.SCHEMA_FLOOR}
baseline: 1
added: 0
compacted: 0

## xx-1
grade: NEW
requirement: READY 2026-01-01 — an ordinary entry — record: OTHER.md:5
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: OTHER.md:5-6
blocked-by: decision regrade: fill goal, write-set, done-criterion and evidence, or drop
"""

#: The SAME carrier with one word of that headline changed. The arms differ in
#: whether the body is already there and in nothing else — not in whether
#: `ITEMS.md` is populated, not in the entry count, not in the flag.
MERGE_TARGET_ITEMS_OTHER = MERGE_TARGET_ITEMS.replace(
    "an ordinary entry", "a different entry")


#: Two source entries carry the SAME parsed headline while both successor
#: homes are absent.  The fire/control differ in one word of the second
#: entry's headline, so neither the homes comparison nor a shape change can
#: account for the verdict.
MERGE_SOURCE_SELF_DUPLICATE = """# old

## Open

- **READY 2026-01-01 — repeated source work.** first body
- **READY 2026-01-01 — repeated source work.** second body
"""
MERGE_SOURCE_SELF_DUPLICATE_OTHER = MERGE_SOURCE_SELF_DUPLICATE.replace(
    "READY 2026-01-01 — repeated source work.** second body",
    "READY 2026-01-01 — different source work.** second body")


def _migrate_run(*, backlog=None, force=False, merge=False,
                 from_sources=(), **repo_kw) -> Fired:
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
        # `migrate_repeated_from` needs the SAME flag more than once, which no
        # keyword can express: one `--from <path>` per element, and the empty
        # default leaves every other row's argv byte-identical.
        for src in from_sources:
            argv += ["--from", src]
        if force:
            argv.append("--force")
        if merge:
            argv.append("--merge")
        here = os.getcwd()
        try:
            os.chdir(str(r.dir))
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(argv)
            return Fired(code, buf.getvalue())
        finally:
            os.chdir(here)


#: A carrier holding an anchor into `BACKLOG.md` with NO blob pin — the shape
#: every build before lc-86 wrote. The `evidence` range is what the retire
#: refusal reads; the `requirement` tail is the same anchor's other half and is
#: there so the fixture is a real migrated block rather than a fragment.
UNPINNED_ANCHOR_ITEMS = f"""schema: {items_mod.SCHEMA_FLOOR}
baseline: 1
added: 0
compacted: 0

## xx-1
grade: NEW
requirement: an entry an earlier build migrated — record: BACKLOG.md:5
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: BACKLOG.md:5-6
blocked-by: decision regrade: fill goal, write-set, done-criterion and evidence, or drop
"""

#: The SAME block with both halves of the SAME anchor PINNED. One property
#: differs between this and the fixture above — whether the pin is there — so
#: the pair separates "the carrier is read" from "the pin is what decides".
#: The sha is a literal 40-hex string and names no real blob on purpose: the
#: refusal asks whether a pin is PRESENT, and a control whose sha had to
#: resolve would be testing a second property nobody registered.
PINNED_ANCHOR_ITEMS = (
    UNPINNED_ANCHOR_ITEMS
    .replace("record: BACKLOG.md:5\n",
             "record: BACKLOG.md:5 at blob "
             + "0" * 39 + "1\n")
    .replace("evidence: BACKLOG.md:5-6\n",
             "evidence: BACKLOG.md:5-6 at blob " + "0" * 39 + "1\n"))


def _retire_run(*, merge=False, report_only=False, commit_source=True,
                laws_present=True, laws_declared=True, items=None,
                **repo_kw) -> Fired:
    """Run `migrate --retire-source` in a scratch repo carrying an old carrier.

    THE FLAG IS ON THE COMMAND LINE AND THE RUN GOES THROUGH `cli.main`, which
    is the altitude the guard actually operates at. An earlier draft of these
    rows set `retire_source` on a parsed namespace instead, because the flag's
    declaration sat outside that lane's write set — and those rows would have
    PASSED: a row firing a constructed namespace proves the branch and reads
    in `--test`'s output exactly like a row that proved the CLI. Nothing in
    that output distinguishes them, which is why the altitude is pinned here
    rather than remembered.
    """
    import io
    from contextlib import redirect_stdout
    from . import cli as cli_mod

    if not laws_declared and "declaration" not in repo_kw:
        # The declaration is otherwise VALID and stays readable — `laws` alone
        # is blanked, so the arms differ in that value and in nothing else.
        blank = json.loads(json.dumps(GOOD_FULL_DECLARATION))
        blank["laws"] = ""
        repo_kw["declaration"] = blank
    with _Repo(items=items, **repo_kw) as r:
        if items is None:
            # The successor homes are seeded by `_Repo`, and `migrate` refuses
            # to overwrite one — without this every row here would fire
            # `migrate_would_overwrite` and prove THAT row instead of its own.
            (r.dir / "ITEMS.md").unlink(missing_ok=True)
            (r.dir / "ITEMS-DONE.md").unlink(missing_ok=True)
        (r.dir / "BACKLOG.md").write_text(
            "# old\n\n## Open\n\n- **READY 2026-01-01 — an ordinary entry.** "
            "body\n", encoding="utf-8")
        (r.dir / "BACKLOG-DONE.md").write_text(
            "# old done\n\n## Done\n\n- **DONE 2026-01-01 — closed.** body\n",
            encoding="utf-8")
        if commit_source:
            subprocess.run(["git", "add", "-f", "BACKLOG.md",
                            "BACKLOG-DONE.md"],
                           cwd=str(r.dir), capture_output=True, text=True)
            subprocess.run(["git", "commit", "-qm", "carriers"],
                           cwd=str(r.dir), capture_output=True, text=True)
            # ANTI-VACUITY, the same pin `_decl_run` takes: a silently failed
            # commit would leave the carrier UNTRACKED, where the control arm
            # degrades into the plant arm — the row green while proving
            # nothing.
            ls = subprocess.run(
                ["git", "-C", str(r.dir), "rev-parse", "HEAD:BACKLOG.md"],
                capture_output=True, text=True)
            if ls.returncode != 0:
                return Fired(-1, "SETUP FAILED: BACKLOG.md is not committed, "
                                 "so this row measured an uncommitted repo. "
                                 f"git said: {ls.stderr.strip()!r}")
        if not laws_present:
            (r.dir / "LAWS.md").unlink(missing_ok=True)
        argv = ["--repo", str(r.dir), "migrate",
                "--report", "docs/audits/report.md", "--retire-source"]
        if merge:
            argv.append("--merge")
        if report_only:
            argv.append("--report-only")
        here = os.getcwd()
        try:
            os.chdir(str(r.dir))
            buf = io.StringIO()
            try:
                with redirect_stdout(buf):
                    code = cli_mod.main(argv)
            except SystemExit as exc:
                # ANTI-VACUITY, and it is caught HERE because argparse RAISES.
                # An unrecognised flag never returns a code — `parser.error`
                # exits the process, and in-process that SystemExit escapes
                # the row, aborts the whole roster mid-run and leaves `--test`
                # with no summary line at all. Measured by removing the
                # declaration: the run stopped at the row before these four,
                # exit 3, no `rows:` line. A row that cannot fire must say so
                # and let its siblings finish.
                return Fired(-1, "SETUP FAILED: `--retire-source` is not "
                                 "declared on the migrate parser, so this row "
                                 f"measured a usage error (SystemExit "
                                 f"{exc.code}).\n{buf.getvalue()}")
            text = buf.getvalue()
            if "unrecognized arguments" in text:
                return Fired(-1, "SETUP FAILED: `--retire-source` is not "
                                 "declared on the migrate parser, so this row "
                                 f"measured a usage error.\n{text}")
            return Fired(code, text)
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


def _route_text_check_over_copy(*, narrow: bool) -> Fired:
    """The MIRROR of `_route_check_over_copy`: the TEXT narrowed, not the code.

    `narrow=True` shortens `schema_above_floor`'s declared ROUTE SET to the
    three carriers it would name if nobody had noticed the ledger parser also
    emits the refusal — while the code keeps emitting it from `ledger.py`. So
    the code watches a route the refusal's own text does not name, which is
    the state that printed a note and contributed CLEAN until lc-30.

    THE MUTATION IS ON THE OTHER SIDE ON PURPOSE. The sibling row narrows the
    CODE and leaves the text claiming everything; this one narrows the TEXT
    and leaves the code watching everything. Between them the two rows pin
    both directions of one comparison, and neither can be satisfied by a
    check that simply fires on every row.

    A COPY rather than the live tree, for the reason `_coverage_over_copy`
    gives: the check's red must not depend on editing the module that is
    running it. And the mutation lands in the COPY's `refusals.py` rather
    than in `roster.py`, because the route SET is declared on the design's
    side — mutating the checker would be grading the check against itself.
    """
    d = Path(tempfile.mkdtemp(prefix="lifecycle-route-text-"))
    try:
        for f in Path(__file__).resolve().parent.glob("*.py"):
            shutil.copy2(f, d / f.name)
        if narrow:
            target = d / "refusals.py"
            text = target.read_text(encoding="utf-8")
            gone = ('        _row.route_set = ("declaration", "items", '
                    '"done", "ledger")\n')
            assert gone in text, "the route-set attachment anchor moved"
            text = text.replace(
                gone,
                '        _row.route_set = ("declaration", "items", "done")\n',
                1)
            target.write_text(text, encoding="utf-8")
            # THE MUTATION IS READ BACK before the arm counts either way: a
            # replace that silently matched nothing returns a green
            # byte-identical to a real one.
            back = target.read_text(encoding="utf-8")
            assert gone not in back, "the route-set narrowing did not land"
        src = (
            "import json, sys\n"
            f"sys.path.insert(0, {str(d.parent)!r})\n"
            f"sys.path.insert(0, {str(Path(__file__).resolve().parents[1])!r})\n"
            "import types\n"
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

    AND IT COMPACTS, since lc-145. The close moves the body into the `done
    bodies` kind, which declares `compacted` — a mode the growth gate now
    admits — so a control that stopped at the close left ONE kind clean and
    the NEXT one firing, and the roster answered COULD NOT VERIFY: both arms
    exited FINDING and the pair separated nothing. The repair is the control
    becoming what it always claimed to be — a repo where every declared exit
    has actually fired — and not a narrower question for the row.

    TWO BODIES, AND ONLY ONE OF THEM COMPACTED, because a control that
    compacts its only body leaves the `done bodies` home EMPTY and then passes
    through the nothing-to-check branch — clean for the reason a control must
    never be clean for, and indistinguishable from a working one forever.
    With two, the kind still HOLDS an instance and its exit has FIRED, which
    is the state the row asserts is not a finding. The arms differ in the
    exits having run and in nothing else: both carry the same two-body
    carrier.

    THE SETUP IS CHECKED RATHER THAN ASSUMED. Each verb's exit code is read,
    and a setup that did not run answers SETUP FAILED instead of handing the
    walk a repo whose state nobody established — a compaction that silently
    refused would otherwise leave the kind holding bodies with no event and
    fire the very finding this arm exists to be quiet about.
    """
    import io
    from contextlib import redirect_stdout
    from . import cli as cli_mod
    from . import retire as retire_mod

    with _Repo(items=TWO_SEED_ITEMS) as r:
        here = os.getcwd()
        try:
            os.chdir(str(r.dir))
            if closed:
                for argv in (["item", "close", "xx-1"],
                             ["item", "close", "xx-2"],
                             ["item", "compact", "xx-1"]):
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = cli_mod.main(["--repo", str(r.dir)] + argv)
                    if rc != exits.CLEAN:
                        return Fired(-1, f"SETUP FAILED: {' '.join(argv)} "
                                         f"exited {rc}\n{buf.getvalue()[-600:]}")
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

def _named_list(names) -> str:
    """`a`, `b`, `c` or `d` — for a row whose text ENUMERATES a source set.

    ITS ONE PURPOSE IS THAT THE ENUMERATION IS DERIVED. A row's `refusal` text
    restating a set beside the module that defines it cannot age loudly: the
    source gains a member, the sentence stays byte-identical, and the row
    keeps passing while its own text under-describes what it refuses. That is
    exactly what happened here — `done_slot_on_live_item` named two
    closed-body slots after lc-44 made the set four.
    """
    quoted = [f"`{n}:`" for n in names]
    if len(quoted) < 2:
        return "".join(quoted)
    return ", ".join(quoted[:-1]) + " or " + quoted[-1]


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
            items_text=EMPTY_ITEMS.replace(
                f"schema: {items_mod.SCHEMA_FLOOR}", "schema: 1", 1)),
        # The SAME repo with the carrier at the declaration's number.
        control=lambda: _decl_run(**_GOOD_KW),
        stage="wave 1d, the schema wave",
    ),
    Row(
        ident="done_slot_on_live_item",
        # THE ENUMERATION IS DERIVED from the module that owns the set, never
        # restated. It read "`superseded-by:` or `blocker-moot:`" while
        # `items.DONE_ONLY_SLOTS` held four — lc-44 added `closed-reason:`
        # and `closed-ref:` and nothing here moved, because nothing could:
        # the row's plant and control both pass whatever the sentence says.
        refusal="a LIVE block carrying a closed-body slot — "
                + _named_list(items_mod.DONE_ONLY_SLOTS)
                + ", each of which records something a CLOSURE did",
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
        ident="blocker_exercise_misplaced",
        refusal="`blocker-exercise:` beside a `blocked-by` that runs no "
                "predicate — the slot records a PREDICATE's live exit and its "
                "two constructed arms, and only an `evidence` blocker has "
                "one, so anywhere else it records an act that cannot have "
                "happened",
        firing_input="a block carrying `blocker-exercise:` with "
                     "`blocked-by: NONE`",
        expect=exits.FINDING,
        # THE ARMS DIFFER IN THE BLOCKER, NOT IN THE SLOT — which is what
        # makes this discriminating. Both carry an identical, well-formed
        # exercise record; only the `blocked-by` moves. An arm pair that
        # differed by REMOVING the slot would prove the parser notices a slot,
        # never that it notices a MISPLACED one, and could-not-verify would
        # pass as verified-wrong.
        fire=lambda: _items_run(
            GOOD_ITEMS.rstrip("\n") + "\n" + _EXERCISE_LINE + "\n"),
        control=lambda: _items_run(
            GOOD_ITEMS.rstrip("\n").replace(
                "blocked-by: NONE", "blocked-by: evidence test -f /tmp/nope")
            + "\n" + _EXERCISE_LINE + "\n"),
        stage="wave B, lc-175",
    ),
    Row(
        ident="not_derivable_misplaced",
        refusal="`not-derivable:` beside a `blocked-by` that asks no "
                "question — the slot records why a QUESTION is not derivable "
                "from the record, and only a `decision` blocker has one",
        firing_input="a block carrying `not-derivable:` with "
                     "`blocked-by: NONE`",
        expect=exits.FINDING,
        # ITS OWN PLANT rather than sharing `blocker_exercise_misplaced`'s.
        # The two misplacements share an answer class, which on §3.8c alone
        # would merge them — but a row is proven by its plant, and one plant
        # certifies the class that FIRED, not its variants. Merged, this
        # message would ship having never been seen to fire.
        fire=lambda: _items_run(
            GOOD_ITEMS.rstrip("\n") + "\n" + _NOT_DERIVABLE_LINE + "\n"),
        control=lambda: _items_run(
            GOOD_ITEMS.rstrip("\n").replace(
                "blocked-by: NONE",
                "blocked-by: decision which instrument the arc adopts")
            + "\n" + _NOT_DERIVABLE_LINE + "\n"),
        stage="wave B, lc-179",
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
                "declares a growth mode whose control IS an exit "
                "(`bounded-by-exit` or `compacted`, never the declared opt-out "
                "`unbounded-with-reason`), and its exit has recorded nothing",
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
    Row(
        ident="route_set_unnamed",
        refusal="the MIRROR of the row above: a refusal whose CODE watches a "
                "route its own TEXT does not name. It catches MORE than it "
                "says, so an entry refused by it is refused under a text that "
                "does not describe it and the operator gets a WRONG CAUSE. "
                "Until lc-30 this printed a note and contributed CLEAN",
        firing_input="`schema_above_floor`'s route set narrowed to "
                     "`declaration, items, done` while the code still emits "
                     "the refusal from the ledger parser",
        expect=exits.FINDING,
        fire=lambda: _route_text_check_over_copy(narrow=True),
        # THE SAME COPY with the route set naming every carrier the code
        # watches: the arms differ in the TEXT's reach alone. A control
        # differing in anything else — a second row, a different check, the
        # resolver narrowed as the sibling row narrows it — would be a
        # control a checker that FIRES ON EVERY ROW also passes, and the pair
        # would score `return exits.FINDING` identically to the comparison
        # this row is about. The mirror direction is held fixed by
        # construction here: narrowing the text can only produce STRAY, never
        # MISSING, so a red from this arm cannot be the sibling's finding
        # wearing this row's name.
        control=lambda: _route_text_check_over_copy(narrow=False),
        stage="lc-30",
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


# --- wave 2, item C: `workflow bind`'s own refusal -----------------------
#
# `binding_slot_unbound` and `binding_template_missing` (the brief's two
# `kind check` findings) live in the main `ROWS` list above, beside
# `dangling_reference` — they are DECLARATION checks, proven the same way
# every other `_decl_run` row is. This one is different in kind: it is the
# BIND VERB's own refusal (an existing binding, no `--force`), found the
# way `lane_new_exists` was found — a verb that writes a file and refuses
# to overwrite it silently.

def _workflow_cli(argv, *, templates=None, **repo_kw) -> Fired:
    """Run a `workflow` verb with a scratch template registry monkeypatched
    onto `workflows.registry_dir` — isolated from the real one the same
    way `_decl_run_with_templates` isolates it above."""
    import io
    from contextlib import redirect_stdout
    from . import cli as cli_mod
    from . import workflows as workflows_mod

    reg = Path(tempfile.mkdtemp(prefix="lifecycle-wfcli-"))
    try:
        for tid, body in (templates or {}).items():
            (reg / f"{tid}.md").write_text(body, encoding="utf-8")
        orig = workflows_mod.registry_dir
        workflows_mod.registry_dir = lambda: reg
        try:
            with _Repo(**repo_kw) as r:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    code = cli_mod.main(["--repo", str(r.dir)] + list(argv))
                return Fired(code, buf.getvalue())
        finally:
            workflows_mod.registry_dir = orig
    finally:
        shutil.rmtree(reg, ignore_errors=True)


WORKFLOW_ROWS = [
    Row(
        ident="workflow_binding_exists",
        refusal="`workflow bind` refuses to overwrite an existing "
                "`template-bindings` entry for the same template — no "
                "silent overwrite, the same rule `init` and `lane new` "
                "apply to what they write",
        firing_input="`workflow bind t1` where `template-bindings.t1` "
                     "already exists",
        expect=exits.FINDING,
        fire=lambda: _workflow_cli(
            ["workflow", "bind", "t1"],
            templates={"t1": "Slots: a\n\nprocedure\n"},
            declaration=_decl_with_binding({"t1": {"a": "UNKNOWN"}})),
        # The SAME existing binding, WITH --force: the arms differ in the
        # flag alone.
        control=lambda: _workflow_cli(
            ["workflow", "bind", "t1", "--force"],
            templates={"t1": "Slots: a\n\nprocedure\n"},
            declaration=_decl_with_binding({"t1": {"a": "UNKNOWN"}})),
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


# --- lc-103: the git hooks a repo SHIPS stay launchable ----------------------
#
# A hook committed without its executable bit is a gate that fails OPEN: git
# cannot launch it, the push proceeds, and every CONTENT check reports clean
# because the bytes are right. The pair below is the shape of the real
# incident rather than a shape invented for it — `0cbd1ad` and `d8c3934` carry
# the SAME blob `887ecff8` for `tools/git-hooks/pre-push`, 100644 and 100755,
# so the mode is the only difference between a dead gate and a live one, which
# is exactly why a bytes-only check passed it.
#
# TWO ROUTES, TWO ROWS. The refusal has two firing inputs because its
# population is a union: a hook under `tools/git-hooks/` (the repo's own
# tooling, and the route the real incident took) and a hook the plugin
# manifest DECLARES. A row proving only the first would leave the second
# green on its own blind spot, and the declared route is the one the
# carrier's original done-criterion named.

#: An ordinary tracked file, carried at 100644 in BOTH arms of both rows. The
#: must-not-move control lives INSIDE the pair rather than beside it: a guard
#: that policed ordinary files would fire in the CONTROL too, so the row stops
#: discriminating instead of quietly widening.
_PLAIN_FILE = "notes.md"

_HOOK_BODY = "#!/bin/sh\nexit 0\n"


def _hook_mode_run(mode: int, *, declared_by_manifest: bool = False) -> Fired:
    """`decl.read` over a scratch repo that has COMMITTED one hook at `mode`.

    The arms differ in the committed MODE alone and carry the same blob. The
    mode is read back off git before the verdict counts: a fixture that never
    received the mode it names returns a green byte-identical to a real one,
    and `git init` on a filesystem mounted without the execute bit is one way
    that happens.

    With `declared_by_manifest`, the hook sits in a scratch PLUGIN tree inside
    the repo and `declaration.plugin_root` is pointed at it for the run —
    monkeypatched the way `_decl_run_with_templates` points at a scratch
    template registry, because the real manifest's scripts resolve OUTSIDE any
    scratch repo and would contribute no member at all.
    """
    with _Scratch(**_GOOD_KW) as s:
        (s.dir / _PLAIN_FILE).write_text("an ordinary tracked file\n",
                                         encoding="utf-8")
        if declared_by_manifest:
            root = s.dir / "pluginroot"
            (root / ".claude-plugin").mkdir(parents=True)
            (root / ".claude-plugin" / "plugin.json").write_text(
                json.dumps({"name": "scratch",
                            decl.PLUGIN_GIT_HOOKS_KEY: {
                                "pre-commit": {"script": "hooks/pre-commit"}}},
                           indent=2), encoding="utf-8")
            rel = "pluginroot/hooks/pre-commit"
        else:
            rel = decl.REPO_GIT_HOOKS_DIR + "/pre-push"
        hook = s.dir / rel
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text(_HOOK_BODY, encoding="utf-8")
        hook.chmod(mode)
        s._run(["git", "add", "-A"])
        s._run(["git", "commit", "-qm", "the hook, at the mode under test"])

        want = decl.EXECUTABLE_MODE if mode & 0o111 else "100644"
        ls = subprocess.run(["git", "-C", str(s.dir), "ls-tree", "HEAD", "--",
                             rel], capture_output=True, text=True)
        if not ls.stdout.startswith(want):
            return Fired(-1, f"SETUP FAILED: this arm asked for {want} and "
                             f"git recorded {ls.stdout.strip()!r}. The arm "
                             "never carried the mode under test, so its "
                             "verdict says nothing either way.")

        orig = decl.plugin_root
        if declared_by_manifest:
            decl.plugin_root = lambda: s.dir / "pluginroot"
        try:
            res = decl.read(s.dir)
        finally:
            decl.plugin_root = orig
        lines = [f"FINDING [{f.row}] {f.message}" for f in res.findings]
        lines += [f"COULD NOT VERIFY: {u}" for u in res.unverified]
        lines.append(f"kind check: {exits.word(res.code)}")
        return Fired(res.code, "\n".join(lines))


HOOK_ROWS = [
    Row(
        ident="hook_not_executable",
        refusal="a git hook the repo SHIPS committed without its executable "
                "bit — a gate git cannot launch, so it fails open while every "
                "content check over it reports clean",
        firing_input="`tools/git-hooks/pre-push` committed at mode 100644",
        expect=exits.FINDING,
        fire=lambda: _hook_mode_run(0o644),
        # The same file, same bytes, committed at 100755 — and carrying the
        # same ordinary 100644 file the plant carries, so neither the blob nor
        # the presence of a non-hook file can be what separates the arms.
        control=lambda: _hook_mode_run(0o755),
        stage="lc-103",
    ),
    Row(
        ident="hook_not_executable_declared",
        finding_row="hook_not_executable",
        refusal="the SAME refusal on its second firing input: a hook the "
                "plugin manifest DECLARES, which is the half the carrier's "
                "own done-criterion named and the half that would have been "
                "green over this repo's actual incident",
        firing_input="a manifest-declared `hooks/pre-commit` committed at "
                     "mode 100644",
        expect=exits.FINDING,
        fire=lambda: _hook_mode_run(0o644, declared_by_manifest=True),
        control=lambda: _hook_mode_run(0o755, declared_by_manifest=True),
        stage="lc-103",
    ),
]



# --- lc-58 + lc-47: the compaction verb's own refusal ------------------------
#
# `item compact` removes a closed body from the done home and leaves a ledger
# line naming the BLOB the body is recoverable at. Everything rests on that
# blob actually carrying the body: a pin that does not is a record pointing at
# text nobody can get back, and the carrier has shrunk by exactly the amount
# that is now nowhere. The failure is SILENT by construction — the verb writes
# a well-formed line, the identity still balances, and only someone running
# `git cat-file` a year later finds out — which is why the check is a refusal
# before the write rather than a report after it.

#: The closure reason the pair closes with, and the ONE-CHARACTER-CLASS edit
#: that separates the arms. The edit lands INSIDE the `closed-reason:` value,
#: so the block's SHAPE is untouched: an edit that broke the shape would be
#: caught by a different check and this row would be scoring another refusal's
#: verdict under its own name.
_COMPACT_REASON = ("the checker went red on the real defect and green after, "
                   "arrangement recorded")
_COMPACT_REASON_EDITED = _COMPACT_REASON.replace("red on", "RED on")


def _compact_run(*, edited: bool) -> Fired:
    """`item compact` over a repo that has actually CLOSED a body.

    THE ARMS DIFFER IN ONE DIMENSION: whether the closed body was edited after
    its close and left UNCOMMITTED. The close, its reason, and the commit it
    produced are identical in both, so a red here cannot be the close's doing.

    The edit is read back off disk before the verdict counts. A plant that
    never landed returns a green byte-identical to a real one, and a
    `replace` whose anchor has drifted is exactly how that happens.
    """
    import io
    from contextlib import redirect_stdout
    from . import cli as cli_mod

    with _Repo(items=SEED_ITEMS) as r:
        here = os.getcwd()
        try:
            os.chdir(str(r.dir))
            with redirect_stdout(io.StringIO()):
                cli_mod.main(["--repo", str(r.dir), "item", "close", "xx-1",
                              "--reason", _COMPACT_REASON])
            done = r.dir / "ITEMS-DONE.md"
            if edited:
                text = done.read_text(encoding="utf-8")
                planted = text.replace(_COMPACT_REASON,
                                       _COMPACT_REASON_EDITED)
                done.write_text(planted, encoding="utf-8")
                if _COMPACT_REASON_EDITED not in done.read_text(
                        encoding="utf-8"):
                    return Fired(-1, "SETUP FAILED: the edit is not in the "
                                     "done home after the write, so this arm "
                                     "never carried the difference under "
                                     "test and its verdict says nothing.")
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = cli_mod.main(["--repo", str(r.dir), "item", "compact",
                                     "xx-1"])
            return Fired(code, buf.getvalue())
        finally:
            os.chdir(here)


COMPACT_ROWS = [
    Row(
        ident="compaction_would_strip",
        refusal="`item compact` refuses a closed body whose text is NOT "
                "recoverable at the blob pin the record would carry — the "
                "carrier would shrink and the text would be nowhere, and "
                "nothing afterwards would say so",
        firing_input="a closed body edited after its close and left "
                     "uncommitted, so the live text and the pinned blob "
                     "differ",
        expect=exits.FINDING,
        fire=lambda: _compact_run(edited=True),
        # The SAME repo, the SAME close, WITHOUT the edit: the arms differ in
        # whether the body still matches what git holds, and in nothing else.
        control=lambda: _compact_run(edited=False),
        stage="lc-58 + lc-47",
    ),
]

# --- lc-156: the investigation record's form ---------------------------------
#
# THE CONTROL IS ONE CONFORMANT RECORD, and every plant below differs from it
# in exactly the line it plants. It is written HERE from the format file's
# template rather than copied out of a live record: an expectation derived
# from the artifact it grades moves with that artifact and stays green on the
# drift it exists to catch.

_GOOD_RECORD = """# proj — arc    (opened 2026-09-18; sessions: aaaaaa)

## GOAL
close the thing the requester asked for, in their words

## NOW
current approach: read the carrier first — killed if the carrier is stale

## ESTABLISHED
[VERIFIED] the fold works — test_records.py::test_fold, green

## OPEN
[PENDING] does the gate fire — route: measure — probe: plant a closed record; red = it fires, green = it is blind

## MOVES
2026-09-18 opened — cc: none
"""


def _record_run(text: str) -> Fired:
    """`record check` over a throwaway home holding exactly this one record.

    THE HOME IS A SCRATCH DIRECTORY, never the machine's. A row that read the
    live investigation home would grade whatever that home happened to hold
    on the day it ran — a fixture the environment is free to change, which is
    the premise-drift class this plugin's own anchor rule forbids — and a
    plant would mean writing into records another session owns.
    """
    from . import records as records_mod

    d = Path(tempfile.mkdtemp(prefix="lifecycle-rec-row-"))
    try:
        (d / "record.md").write_text(text, encoding="utf-8")

        class _Args:
            dir = str(d)

        said = []
        code = records_mod.cmd_record_check(_Args(), said.append)
        return Fired(code, "\n".join(said))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _watched_record_routes() -> set:
    """Which route words the CHECKER actually admits.

    DERIVED FROM THE SOURCE of `records.py`, never from the tuple imported
    out of it: importing the module and reading `records.ROUTES` would
    compare the row's claim against the very object the row exists to grade,
    which is a claim compared against itself. The route SET beside it is
    written from the FORMAT FILE's own sentence, so the two sides have
    different parents.
    """
    from . import records as records_mod

    src = Path(records_mod.__file__).read_text(encoding="utf-8")
    m = re.search(r'^ROUTES = \((?P<body>[^)]*)\)', src, re.M)
    if not m:
        raise AssertionError("records.py declares no ROUTES tuple")
    return set(re.findall(r'"([a-z]+)"', m.group("body")))


RECORD_ROWS = [
    Row(
        ident="record_slot_missing",
        refusal="a record missing one of the five declared slots",
        firing_input="a record whose `## MOVES` heading is renamed, so the "
                     "slot is absent rather than empty",
        expect=exits.FINDING,
        fire=lambda: _record_run(_GOOD_RECORD.replace("## MOVES", "## NOTES")),
        control=lambda: _record_run(_GOOD_RECORD),
        stage="lc-156",
    ),
    Row(
        ident="record_now_empty",
        refusal="NOW present and empty — the anti-blinders slot saying "
                "nothing",
        firing_input="a record whose NOW heading stands with no line under it",
        expect=exits.FINDING,
        fire=lambda: _record_run(_GOOD_RECORD.replace(
            "current approach: read the carrier first — killed if the "
            "carrier is stale\n", "")),
        control=lambda: _record_run(_GOOD_RECORD),
        stage="lc-156",
    ),
    Row(
        ident="record_line_untagged",
        refusal="prose under the right heading — a line in ESTABLISHED or "
                "OPEN carrying no `[TAG]`, which passes every check written "
                "over tagged lines BY HAVING NONE",
        firing_input="a record whose ESTABLISHED line is a bullet instead of "
                     "a tagged line (two of the four live records are this "
                     "shape throughout)",
        expect=exits.FINDING,
        fire=lambda: _record_run(_GOOD_RECORD.replace(
            "[VERIFIED] the fold works — test_records.py::test_fold, green",
            "- the fold works, we checked")),
        control=lambda: _record_run(_GOOD_RECORD),
        stage="lc-156",
    ),
    Row(
        ident="record_tag_unknown",
        refusal="a tag outside the closed set — counted by nothing, draining "
                "through every gate",
        firing_input="`[CONFIRMED]`, a plausible word the vocabulary does "
                     "not carry",
        expect=exits.FINDING,
        fire=lambda: _record_run(_GOOD_RECORD.replace("[VERIFIED] the fold",
                                                      "[CONFIRMED] the fold")),
        control=lambda: _record_run(_GOOD_RECORD),
        stage="lc-156",
    ),
    Row(
        ident="record_line_unbasised",
        refusal="a tagged claim with no basis after the em dash — the label "
                "standing where the evidence should be",
        firing_input="a `[VERIFIED]` line whose basis is deleted, the rest "
                     "of the record untouched",
        expect=exits.FINDING,
        fire=lambda: _record_run(_GOOD_RECORD.replace(
            "[VERIFIED] the fold works — test_records.py::test_fold, green",
            "[VERIFIED] the fold works")),
        control=lambda: _record_run(_GOOD_RECORD),
        stage="lc-156",
    ),
    Row(
        ident="record_line_unbasised_hyphen",
        finding_row="record_line_unbasised",
        refusal="the SEPARATOR half of the same refusal: a hyphen is a "
                "different character from an em dash, and admitting both "
                "would put two spellings of one slot in every record",
        firing_input="the same line with its em dash replaced by a hyphen — "
                     "a basis that is present and not machine-findable",
        expect=exits.FINDING,
        fire=lambda: _record_run(_GOOD_RECORD.replace(
            "works — test_records.py", "works - test_records.py")),
        control=lambda: _record_run(_GOOD_RECORD),
        stage="lc-156",
    ),
    Row(
        ident="record_route_invalid",
        refusal="a PENDING line that names no route, or names one outside "
                "the closed set — \"I don't know\" left as a terminal state "
                "instead of a claim about what would make it known",
        firing_input="a PENDING line with its `route:` token removed",
        expect=exits.FINDING,
        fire=lambda: _record_run(_GOOD_RECORD.replace(" — route: measure", "")),
        control=lambda: _record_run(_GOOD_RECORD),
        stage="lc-156",
    ),
    Row(
        ident="record_route_outside_set",
        finding_row="record_route_invalid",
        refusal="the VOCABULARY half of the same refusal: a fourth word "
                "routes the question nowhere, the three carrying different "
                "costs and different failure modes",
        firing_input="`route: think`, a word outside ask / measure / query",
        expect=exits.FINDING,
        fire=lambda: _record_run(_GOOD_RECORD.replace("route: measure",
                                                      "route: think")),
        control=lambda: _record_run(_GOOD_RECORD),
        stage="lc-156",
    ),
    Row(
        ident="record_probe_missing",
        refusal="a PENDING line naming no probe — a question nobody but its "
                "author can settle",
        firing_input="a PENDING line with its `probe:` clause removed, the "
                     "route left in place",
        expect=exits.FINDING,
        fire=lambda: _record_run(_GOOD_RECORD.replace(
            " — probe: plant a closed record; red = it fires, green = it is "
            "blind", "")),
        control=lambda: _record_run(_GOOD_RECORD),
        stage="lc-156",
    ),
    Row(
        ident="record_closed_undrained",
        refusal="a record marked closed over undrained [PENDING] lines — "
                "closure is GRADUATION, never deletion and never silence",
        firing_input="a `## CLOSED` heading with pointers, added to a record "
                     "whose OPEN slot still holds a PENDING line",
        expect=exits.FINDING,
        fire=lambda: _record_run(
            _GOOD_RECORD + "\n## CLOSED\nESTABLISHED → LEDGER.md; OPEN → lc-99\n"),
        # The SAME closure, with the PENDING line graduated to a terminal
        # tag — so the arms differ in whether anything was left undrained,
        # and not in whether the record is closed at all. A control without
        # the CLOSED heading would come back clean for the wrong reason.
        control=lambda: _record_run(
            _GOOD_RECORD.replace(
                "[PENDING] does the gate fire — route: measure — probe: plant "
                "a closed record; red = it fires, green = it is blind",
                "[VERIFIED] the gate fires — prove-rows, red then green")
            + "\n## CLOSED\nESTABLISHED → LEDGER.md; OPEN → lc-99\n"),
        stage="lc-156",
    ),
    Row(
        ident="record_closed_unpointed",
        refusal="a closure with no pointer to where anything went — the same "
                "loss as deleting the graduated lines, minus the honesty",
        firing_input="a `## CLOSED` heading standing empty over a fully "
                     "drained record",
        expect=exits.FINDING,
        fire=lambda: _record_run(
            _GOOD_RECORD.replace(
                "[PENDING] does the gate fire — route: measure — probe: plant "
                "a closed record; red = it fires, green = it is blind",
                "[VERIFIED] the gate fires — prove-rows, red then green")
            + "\n## CLOSED\n"),
        control=lambda: _record_run(
            _GOOD_RECORD.replace(
                "[PENDING] does the gate fire — route: measure — probe: plant "
                "a closed record; red = it fires, green = it is blind",
                "[VERIFIED] the gate fires — prove-rows, red then green")
            + "\n## CLOSED\nESTABLISHED → LEDGER.md; OPEN → lc-99\n"),
        stage="lc-156",
    ),
]


# --- lc-16: reading the carrier BY GOAL -------------------------------------

_TWO_GOAL_ITEMS = f"""schema: {items_mod.SCHEMA_FLOOR}
baseline: 0

## xx-1
grade: READY
requirement: the verify-goal entry — record: LEDGER.md
goal: verify
write-set: tools/a.py
done-criterion: it goes red on the real defect
evidence: measured here
blocked-by: NONE

## xx-2
grade: READY
requirement: the mitigate-goal entry — record: LEDGER.md
goal: mitigate
write-set: tools/b.py
done-criterion: it goes red on the real defect
evidence: measured here
blocked-by: NONE
"""


def _ready_goal_run(goal: str) -> Fired:
    """`item ready --goal <goal>` over a carrier holding TWO goals.

    Two goals and not one: over a single-goal carrier a filter that ignored
    its flag returns the same rows as one that applied it, so the fixture
    itself would be unable to tell them apart.
    """
    import io
    from contextlib import redirect_stdout
    from . import cli as cli_mod

    r = _Repo(items=_TWO_GOAL_ITEMS)
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli_mod.main(["--repo", str(r.dir), "item", "ready",
                                 "--goal", goal])
        return Fired(code, buf.getvalue())
    finally:
        r.close()


def _records_kind_run(*, declare: bool) -> Fired:
    """`kind check` over a repo whose investigation records EXIST.

    THE RECORDS HOME IS REDIRECTED THROUGH `XDG_STATE_HOME`, never the
    machine's: a row that read the real home would grade whatever that home
    held on the day it ran — the premise-drift class this plugin's own anchor
    rule forbids — and the plant would mean writing a file into records
    another session owns.
    """
    d = json.loads(json.dumps(GOOD_FULL_DECLARATION))
    if declare:
        d["kinds"]["investigation records"] = {
            "home": "$XDG_STATE_HOME/claude/investigations/x--*.md",
            "writer": "session",
            "reader": ["session"],
            "staleness": "change-coupling — the cited basis no longer resolves",
            "exit": {"action": "never",
                     "recording-act": "a `## CLOSED` heading with pointers"},
            "growth": "unbounded-with-reason — one file per arc",
            # writer: session, so there is no button. Declared rather than
            # invented: a record opens when work turns diagnosis-shaped,
            # which is a judgment no predicate makes.
            "trigger": "none, declared why: a record opens when work turns diagnosis-shaped, and that reading is the session's own",
        }
    state = Path(tempfile.mkdtemp(prefix="lifecycle-xdg-"))
    r = _Repo(declaration=d)
    old = os.environ.get("XDG_STATE_HOME")
    try:
        home = state / "claude" / "investigations"
        home.mkdir(parents=True)
        # NAMED FOR THE REPO ITSELF: the check globs `<repo dir name>--*.md`,
        # so a fixed filename would match nothing and the row would pass for
        # a reason that has nothing to do with the declaration.
        (home / f"{r.dir.resolve().name}--arc.md").write_text(
            "# rec\n", encoding="utf-8")
        os.environ["XDG_STATE_HOME"] = str(state)
        buf = []
        code = _kind_check(r, buf.append)
        return Fired(code, "\n".join(buf))
    finally:
        if old is None:
            os.environ.pop("XDG_STATE_HOME", None)
        else:
            os.environ["XDG_STATE_HOME"] = old
        r.close()
        shutil.rmtree(state, ignore_errors=True)


def _desk_state_kind_run(*, declare: bool, mine: bool = True) -> Fired:
    """`kind check` over a repo with a desk-state file (lc-182).

    `mine` IS THE ARM THE WITHDRAWN FIRST CUT FAILED. With it False the file
    on disk names a DIFFERENT repo, and the check must stay silent: desk
    state is machine-wide, so a check that only asked whether files EXIST
    demanded every repo declare the kind because some other repo's session
    wrote one — measured at lc-171 as 22 rows could-not-verify in a single
    run.

    THE HOME IS REDIRECTED THROUGH `XDG_STATE_HOME`, as the records row does
    and for the same reason: an arm reading the machine's own home would
    grade whatever it held that day, and the plant would mean writing into
    state another desk owns.
    """
    d = json.loads(json.dumps(GOOD_FULL_DECLARATION))
    if declare:
        d["kinds"]["desk state"] = {
            "home": "$XDG_STATE_HOME/lifecycle/desk-state/*.json",
            "writer": "verb:desk state",
            "reader": ["verb:desk state"],
            "staleness": "none, declared why: overwritten in place",
            "exit": {"action": "delete",
                     "recording-act": "a ledger line naming the desks removed"},
            "growth": "unbounded-with-reason — one file per desk id",
            "trigger": "verb desk state",
        }
    state = Path(tempfile.mkdtemp(prefix="lifecycle-xdg-"))
    r = _Repo(declaration=d)
    old = os.environ.get("XDG_STATE_HOME")
    try:
        home = state / "lifecycle" / "desk-state"
        home.mkdir(parents=True)
        owner = str(Path(r.dir).resolve()) if mine else str(state / "elsewhere")
        (home / "a-desk.json").write_text(
            json.dumps({"value": "READY", "desk": "a-desk", "repo": owner}),
            encoding="utf-8")
        os.environ["XDG_STATE_HOME"] = str(state)
        buf = []
        code = _kind_check(r, buf.append)
        return Fired(code, "\n".join(buf))
    finally:
        if old is None:
            os.environ.pop("XDG_STATE_HOME", None)
        else:
            os.environ["XDG_STATE_HOME"] = old
        r.close()
        shutil.rmtree(state, ignore_errors=True)


def _kind_check(repo_obj, out) -> int:
    from . import cli as cli_mod
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli_mod.main(["--repo", str(repo_obj.dir), "kind", "check"])
    out(buf.getvalue())
    return code


def _list_home_run(home: str) -> Fired:
    """The walk's own answer for one declared home, built from its own body.

    FIRES `list_home` AND `unresolvable_line` DIRECTLY, which is the pattern
    `check_growth`'s rows already use here, and for the same reason: the
    walk's overall exit code is COULD NOT VERIFY by construction — the
    staleness predicate has no pass history — so a row over the whole verb
    would read 3 for both arms and separate nothing. The mapping below is the
    walk's, not a paraphrase of it: `instances is None` is exactly what the
    walk routes to could-not-verify, and the sentence comes from the one
    function that builds it.
    """
    from . import retire as retire_mod

    d = Path(tempfile.mkdtemp(prefix="lifecycle-home-"))
    try:
        (d / "ITEMS.md").write_text(GOOD_ITEMS, encoding="utf-8")
        instances, note = retire_mod.list_home(d, home)
        if instances is None:
            return Fired(exits.COULD_NOT_VERIFY,
                         retire_mod.unresolvable_line(note))
        return Fired(exits.CLEAN,
                     f"count: {len(instances)}   ({note})")
    finally:
        shutil.rmtree(d, ignore_errors=True)


HOME_ROWS = [
    Row(
        ident="home_unresolvable",
        refusal="a declared home this walk never resolved — counted as 0 and "
                "reported CLEAN, which is an absence claim over a population "
                "no instrument ever saw",
        firing_input="a home carrying an unexpanded `$XDG_STATE_HOME`, the "
                     "shape the fire log declares",
        expect=exits.COULD_NOT_VERIFY,
        # RE-INSTANCED BY lc-170 AND THE ROW'S CLAIM DID NOT MOVE. This fired
        # on `$XDG_STATE_HOME/lifecycle/fire.jsonl` while the walk expanded
        # nothing; that item made the four XDG bases resolve, which is the end
        # state lc-172's could-not-verify was the honest waypoint to. What is
        # unresolvable now is a variable that is unset AND has no spec default,
        # so that is what the plant uses — the refusal is unchanged, the world
        # under its old example moved.
        fire=lambda: _list_home_run(
            "$LIFECYCLE_NO_SUCH_BASE_DIR/lifecycle/fire.jsonl"),
        # A RESOLVABLE IN-TREE HOME THAT IS ALSO PRESENT: the arms differ in
        # whether the walk could resolve the home at all. Deliberately NOT an
        # absent in-tree home — that one is CLEAN by design (the walk looked
        # and there is no file), so using it as the control would have proven
        # the wrong boundary and pinned a behaviour lc-172 does not change.
        control=lambda: _list_home_run("ITEMS.md"),
        stage="lc-172",
    ),
]


RECORDS_KIND_ROWS = [
    Row(
        ident="records_kind_undeclared",
        refusal="investigation records EXIST for a repo whose declaration "
                "registers no kind for them — invariant 1 reaching a home "
                "the tracked-file sweep structurally cannot see",
        firing_input="a repo with a record at the XDG investigations home "
                     "and no kind whose `home` names that directory",
        expect=exits.FINDING,
        fire=lambda: _records_kind_run(declare=False),
        # The SAME repo with the SAME record present, and the kind declared:
        # the arms differ in the declaration alone. A control with no record
        # would come back clean because there was nothing to govern, which
        # says nothing about whether the check reads the declaration.
        control=lambda: _records_kind_run(declare=True),
        stage="lc-166",
    ),
    Row(
        ident="desk_state_kind_undeclared",
        refusal="desk-state files WRITTEN IN THIS REPO exist and no registered "
                "kind names their home — the plugin governing its own state "
                "everywhere except the file a shipped verb writes about the "
                "desk. An XDG home is invisible to `kind sweep`, which walks "
                "TRACKED files, so its absence from the declaration is "
                "invisible to every other check too (lc-171, lc-182)",
        firing_input="`kind check` in a repo that has written desk state, "
                     "with no kind naming its home",
        expect=exits.FINDING,
        fire=lambda: _desk_state_kind_run(declare=False),
        # The SAME repo with the SAME file present and the kind declared: the
        # arms differ in the declaration alone. A control with no file would
        # come back clean because there was nothing to govern, which says
        # nothing about whether the check reads the declaration. The SCOPE
        # arm — another repo's file, this repo silent — is the one the
        # withdrawn first cut failed and it is a test arm, because a row
        # carries one pair and this pair is about the refusal's own axis.
        control=lambda: _desk_state_kind_run(declare=True),
        stage="lc-182",
    ),
]


GOAL_ROWS = [
    Row(
        ident="verify_check_did_not_run",
        refusal="a registered verify command that never EXECUTED — reported "
                "COULD NOT VERIFY, never as a pass with fewer checks",
        firing_input="a laws file whose `## Verify` block names a command "
                     "that does not exist (shell exit 127), beside one that "
                     "runs",
        expect=exits.COULD_NOT_VERIFY,
        fire=lambda: _verify_run("true\nlc16_no_such_command_anywhere"),
        # The SAME block with that command REPLACED BY ONE THAT EXISTS — so
        # the arms differ in whether a registered command could start, and in
        # nothing else. A control with a FAILING command would exit FINDING,
        # which differs from the plant for the wrong reason and would prove
        # nothing about the did-not-run half.
        control=lambda: _verify_run("true\ntrue"),
        stage="lc-16 follow-up",
    ),
    Row(
        ident="emit_site_unregistered_could_not_verify",
        finding_row="emit_site_unregistered",
        refusal="the COULD-NOT-VERIFY half of the coverage check's reach: a "
                "site emitting a refusal under that verdict word with no "
                "registered row. Unwatched until 2026-09-18, which is how "
                "`verify`'s did-not-run refusal shipped unprovable",
        firing_input="a planted could-not-verify emission naming an "
                     "unregistered row, in a copy of the package, scanned",
        expect=exits.FINDING,
        fire=lambda: _coverage_over_copy(plant=True, word="COULD NOT VERIFY"),
        # The same copy, same verdict word, no planted line: the arms differ
        # in the emission alone. Sharing the FINDING half's control would
        # have compared two different plants against one baseline and proved
        # neither half on its own.
        control=lambda: _coverage_over_copy(plant=False, word="COULD NOT VERIFY"),
        stage="lc-16 follow-up",
    ),
    Row(
        ident="goal_query_undeclared",
        refusal="a goal filter naming a goal the repo does not declare — "
                "answered COULD NOT VERIFY, never as an empty listing",
        firing_input="`item ready --goal mitigat`, one character off a "
                     "declared goal, over a carrier holding two goals",
        expect=exits.COULD_NOT_VERIFY,
        fire=lambda: _ready_goal_run("mitigat"),
        # THE CONTROL IS A DECLARED GOAL THAT HOLDS NOTHING, not one that
        # holds rows: `retire` returns zero entries here exactly as the typo
        # does, so the arms differ in whether the goal is DECLARED and in
        # nothing else. A control returning rows would pass for a build that
        # answered could-not-verify to every empty result — the very conflation
        # this row exists to forbid.
        control=lambda: _ready_goal_run("retire"),
        stage="lc-16",
    ),
]


ROWS = (ROWS + VERB_ROWS + LANE_ROWS + SCHEMA_ROWS + DESK_ROWS + WORKFLOW_ROWS
        + HOOK_ROWS + COMPACT_ROWS + RECORD_ROWS + GOAL_ROWS
        + RECORDS_KIND_ROWS + HOME_ROWS)

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
    elif _row.ident == "record_route_invalid":
        # THE SET IS THE FORMAT FILE'S SENTENCE — `route: ask|measure|query`,
        # dotfiles claude/investigation-record-format.md — written out here
        # by hand, while the watched half is parsed from records.py's source.
        # Two parents, which is the only thing that makes the comparison mean
        # anything.
        _row.route_set = ("ask", "measure", "query")
        _row.routes_watched = _watched_record_routes
del _row
