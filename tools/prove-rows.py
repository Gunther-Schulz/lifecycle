#!/usr/bin/env python3
"""Red-first proof for every refusal row, RE-RUNNABLE rather than remembered.

WHY THIS IS A TOOL AND NOT A TRANSCRIPT. "A check counts only once it has
gone RED on the real defect" — demonstrated, with the arrangement recorded.
The demonstration was being done by hand: disable one named condition, run
the roster, watch one row go dark, restore by file copy. That reasoning is
exactly what does not survive into the next session, and a row added next
month gets no proof at all unless someone remembers the ritual. So the
arrangement lives here, executable, one entry per row.

WHAT IT ASSERTS, and it is a PAIR like every row itself. For each mutation:

  * the named row's verdict CHANGES  — the row was reading that condition;
  * EXACTLY ONE row's verdict changes — the mutation removed that condition
    and not its neighbours.

The second half is the one that catches a mutation deleting adjacent
machinery instead of the named condition. A mutation that darkens four rows
has not proven any of them; it has proven that something large broke.

A ROW WHOSE MUTATION DARKENS NOTHING is the loud case: the condition it
names is not what produces its verdict, so the row is passing for a reason
nobody wrote down.

RESTORE IS BY FILE COPY, never `git checkout`/`restore`/`stash` — those take
the whole tree, and this runs in a work tree that has uncommitted work in it
by construction. `__pycache__` is cleared around every arm: a stale `.pyc`
would let the unmutated module answer for the mutated source, which reads
exactly like a row that does not discriminate.

    python3 tools/prove-rows.py            # every row that has a mutation
    python3 tools/prove-rows.py <ident>…   # only these

Exit: 0 every proof held · 2 a proof failed · 3 a mutation anchor was not
found (the source moved under the arrangement — the arrangement is stale,
which is a finding about THIS file, not about the row).
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLI = REPO / "plugin" / "cli"
CORE = CLI / "lifecycle_core"

CLEAN, FINDING, COULD_NOT_VERIFY = 0, 2, 3

#: (row ident, file, anchor, replacement, what the anchor IS).
#:
#: The anchor is the single place the row's finding is DECIDED — not a place
#: near it. Each replacement removes that decision and nothing else, which is
#: what makes "exactly one row changes" a meaningful assertion rather than a
#: coincidence.
MUTATIONS = [
    ("declaration_ignored_tracked", "declaration.py",
     '["git", "-C", str(repo), "check-ignore",\n                            '
     '"--no-index", str(rel)]',
     '["git", "-C", str(repo), "check-ignore",\n                            '
     'str(rel)]',
     "the `--no-index` flag that lets check-ignore see a TRACKED path"),

    ("unknown_grade_write", "verbs.py",
     "        if grade not in items_mod.GRADES:",
     "        if False:",
     "the closed grade vocabulary's test on write"),

    ("foreign_origin_item", "verbs.py",
     "    if here != ctx.repo.resolve():",
     "    if False:",
     "the origin comparison between the writer's repo and the target"),

    ("join_undisposed", "verbs.py",
     "    if found and not join:",
     "    if False:",
     "the refusal to write while the join is undisposed"),

    ("new_without_absence", "verbs.py",
     "    if not absence:",
     "    if False:",
     "the named-absence requirement on `new`"),

    ("cost_test_veto", "verbs.py",
     '    return "veto", (',
     '    return "clear", (',
     "the cost test's veto verdict on a one-file one-hunk write-set"),

    ("cost_test_unverified", "verbs.py",
     "    if hunks is None:\n        return \"unverified\", (",
     "    if False:\n        return \"unverified\", (",
     "the cost test's refusal to clear what it could not evaluate"),

    ("blocker_untyped", "verbs.py",
     "    kind, detail = items_mod.classify_blocker(value, ctx.prefix)\n"
     "    if kind is None:",
     "    kind, detail = items_mod.classify_blocker(value, ctx.prefix)\n"
     "    if False:",
     "the typed-blocker test in `_check_blocker`"),

    ("dangling_reference_item", "verbs.py",
     "    if detail not in known:",
     "    if False:",
     "the referential-integrity test on an item-id blocker"),

    ("parked_without_typed_blocker", "verbs.py",
     "    value = (args.blocked_by or \"\").strip()\n"
     "    kind, detail = items_mod.classify_blocker(value, ctx.prefix)\n"
     "    if kind in (None, \"none\"):",
     "    value = (args.blocked_by or \"\").strip()\n"
     "    kind, detail = items_mod.classify_blocker(value, ctx.prefix)\n"
     "    if False:",
     "`item park`'s own typed-blocker requirement"),

    ("duplicate_id_cross_home", "items.py",
     "    both = [(d.ident, live[d.ident], d.line)\n"
     "            for d in done_parsed.items if d.ident in live]",
     "    both = []",
     "the cross-home id intersection"),

    # BOTH sign rows anchor on the same branch, with OPPOSITE replacements:
    # each sends its OWN case down the wrong side. Disabling the branch
    # outright, or making the whole identity report clean, would darken both
    # rows at once and prove neither — the mutation that removes adjacent
    # machinery rather than the named condition.
    ("conservation_short", "items.py",
     "    if delta < 0:",
     "    if delta < -999:",
     "the SHORT branch — a shortfall then reports under the surplus row, "
     "which is the wrong diagnosis and the wrong repair"),

    ("conservation_surplus", "items.py",
     "    if delta < 0:",
     "    if True:",
     "the SURPLUS branch — a surplus then reports as loss, which is exactly "
     "the defect this row was found by"),

    # NOT `if False:` here. Removing the branch outright makes the next line
    # do arithmetic on None and the row goes red with a TypeError — which
    # proves the branch is on the executed path, not that the row tells a
    # clean identity from an uncomputable one. Folding could-not-verify into
    # CLEAN is the actual defect the row exists to catch, so that is the
    # mutation: one token, and the output is a verdict rather than a crash.
    ("conservation_unverified", "items.py",
     '        out(f"COULD NOT VERIFY: conservation — {c[\'why\']}")\n'
     "        return exits.COULD_NOT_VERIFY",
     '        out(f"COULD NOT VERIFY: conservation — {c[\'why\']}")\n'
     "        return exits.CLEAN",
     "the could-not-verify ANSWER for an identity that could not be "
     "computed — folded into CLEAN, which is the number shaped like a pass"),

    ("ledger_body", "ledger.py",
     '    if "\\n" in v or "\\r" in v:',
     "    if False:",
     "the ledger's one-line rule — the NO BODIES half"),

    ("closure_home_split", "verbs.py",
     "    if done_home and done_home != closure:",
     "    if False:",
     "the comparison between the two declared closure homes"),
]


def clear_pycache():
    for d in CORE.rglob("__pycache__"):
        shutil.rmtree(d, ignore_errors=True)


def verdicts(only=None) -> dict:
    """`{ident: signature}` for every row's PLANT, in a fresh interpreter.

    THE SIGNATURE IS THE CODE **AND** THE ROW NAME IN THE OUTPUT, and the
    second half was added after this tool reported a row unproven that is
    not. Disabling `item park`'s own typed-blocker guard leaves the exit
    code at 2, because the shared `_check_blocker` catches the same input
    under a DIFFERENT row's name — so a comparison over codes alone
    separates something-happened from nothing-happened when the question is
    WHICH refusal fired. Two rows that share an exit code are the normal
    case here, not the exotic one: every finding is a 2.

    A fresh process per arm, because the modules under mutation are imported
    once per interpreter: reading the roster twice in one process would grade
    the mutation against a module the mutation never reached.
    """
    src = (
        "import json, sys\n"
        f"sys.path.insert(0, {str(CLI)!r})\n"
        "from lifecycle_core import refusals\n"
        "out = {}\n"
        "for row in refusals.ROWS:\n"
        "    try:\n"
        "        f = row.fire()\n"
        "        named = ('[' + row.expected_finding_row + ']') in f.output\n"
        "        out[row.ident] = '%s/%s' % (f.code, 'named' if named\n"
        "                                    else 'unnamed')\n"
        "    except Exception as exc:\n"
        "        out[row.ident] = 'RAISED: ' + type(exc).__name__\n"
        "print(json.dumps(out))\n"
    )
    r = subprocess.run([sys.executable, "-c", src], capture_output=True,
                       text=True, cwd=str(REPO))
    if r.returncode != 0:
        raise SystemExit(f"the roster could not be read:\n{r.stderr[-2000:]}")
    import json
    return json.loads(r.stdout.strip().split("\n")[-1])


def main(argv) -> int:
    wanted = set(argv) or None
    rows = [m for m in MUTATIONS if wanted is None or m[0] in wanted]
    if wanted:
        unknown = wanted - {m[0] for m in MUTATIONS}
        if unknown:
            print(f"COULD NOT VERIFY: no mutation recorded for "
                  f"{', '.join(sorted(unknown))}")
            return COULD_NOT_VERIFY

    backup = Path(tempfile.mkdtemp(prefix="prove-rows-"))
    for f in CORE.glob("*.py"):
        shutil.copy2(f, backup / f.name)

    clear_pycache()
    print("BASELINE — the unmutated roster, stated rather than assumed.")
    print("(Over an already-red baseline a mutate-and-restore proof is "
          "indistinguishable from a check that is simply always red.)")
    base = verdicts()
    for ident, code in sorted(base.items()):
        print(f"    {ident:<34} {code}")

    failures = []
    stale = []
    for ident, fname, anchor, replacement, what in rows:
        path = CORE / fname
        text = path.read_text(encoding="utf-8")
        if text.count(anchor) != 1:
            stale.append((ident, fname, text.count(anchor)))
            print(f"\n[{ident}] COULD NOT VERIFY — the anchor appears "
                  f"{text.count(anchor)} times in {fname}, not once. The "
                  "source moved under this arrangement.")
            continue
        try:
            clear_pycache()
            path.write_text(text.replace(anchor, replacement, 1),
                            encoding="utf-8")
            clear_pycache()
            after = verdicts()
        finally:
            shutil.copy2(backup / fname, path)   # BY FILE COPY
            clear_pycache()

        changed = sorted(k for k in base
                         if base.get(k) != after.get(k))
        ok_named = ident in changed
        ok_alone = len(changed) == 1
        verdict = "PROVEN" if (ok_named and ok_alone) else "FAILED"
        print(f"\n[{ident}] {verdict}")
        print(f"    disabled: {what}")
        print(f"    {fname}: {anchor.splitlines()[0][:66]}…")
        print(f"    verdict {base.get(ident)} -> {after.get(ident)}")
        print(f"    rows changed: {', '.join(changed) or 'NONE'}")
        if not ok_named:
            print("    -> the row did NOT change. The condition this "
                  "mutation names is not what produces its verdict.")
        if not ok_alone:
            print("    -> more than one row changed. This mutation removed "
                  "adjacent machinery, so it proves nothing about any one "
                  "row.")
        if verdict == "FAILED":
            failures.append(ident)

    shutil.rmtree(backup, ignore_errors=True)
    covered = {m[0] for m in MUTATIONS}
    unproven = sorted(set(base) - covered)
    print(f"\nrows with a recorded mutation: {len(covered)} of {len(base)}")
    if unproven:
        print("rows with NO mutation recorded (proven elsewhere or not at "
              "all — listed, never omitted):")
        for ident in unproven:
            print(f"    {ident}")
    if stale:
        return COULD_NOT_VERIFY
    if failures:
        print(f"\nFAILED: {', '.join(failures)}")
        return FINDING
    print("\nevery recorded arrangement held: the named row went dark, and "
          "it went dark alone.")
    return CLEAN


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
