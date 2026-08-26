"""`lifecycle --test` — the refusal roster, and the emit-site coverage check.

ONE SOURCE, TWO CONSUMERS (design §3.9). The rows live in `refusals.py` as
executable firing inputs; `test/test_refusals.py` executes them under
unittest and this prints them as a roster. Nothing is restated here — a row
described in a second file is a second body for one fact, and the two
diverge.

WHAT A GREEN ROSTER PROMISES, AND WHAT IT DOES NOT. Each row runs its PLANT
and its CONTROL: the plant must exit what the row names, the control must
exit something else, and a FINDING row must name itself in its own output.
That is the pair, and without it "something happened" passes for "the right
thing happened".

THE COVERAGE CHECK IS THE SECOND HALF, and its limit is printed in its own
output rather than left for a reader to discover. It walks the SOURCE for
every site that emits a FINDING and asks whether that row is registered. It
therefore catches a finding the code emits under no row. It CANNOT catch a
refusal the PROSE requires and the code lacks: that site does not exist, so
no scan finds it, and only an end-to-end walk of §3.9 does. An assurance
wider than the predicate that establishes it is the defect this whole arc
keeps finding, so the assurance is stated at its real width.

PROSE-REST ROWS ARE PRINTED, NEVER DROPPED (D-g). A row that cannot be fired
is labelled with its reason and counted apart. Deleting one to make a roster
green would report a completeness the roster does not have.
"""

import re
import traceback
from pathlib import Path

from . import exits, refusals

CORE = Path(__file__).resolve().parent

#: Every way a row ident reaches a caller's eyes. Derived from the SOURCE, so
#: a site added tomorrow is found without anyone updating a list here.
#:
#: 1. a literal bracketed row name in a FINDING message string;
#: 2. `Result.add("<row>", …)` — the declaration reader's recorder;
#: 3. `problems.append(("<row>", …))` — the carrier and ledger parsers'.
#:
#: The three lines above are worded to avoid the literal forms themselves.
#: They used to carry them, and the scan then found its own documentation and
#: reported a row called `name` — an instrument reading its own description as
#: data. Cheaper to reword than to exempt this file, and an exemption here
#: would have blinded the scan to the one finding this module really emits.
_LITERAL = re.compile(r"FINDING \[([a-z_][a-z0-9_]*)\]")
_RESULT_ADD = re.compile(r"\.add\(\s*\n?\s*[\"']([a-z_][a-z0-9_]*)[\"']")
_PROBLEM = re.compile(r"problems\.append\(\(\s*\n?\s*[\"']([a-z_][a-z0-9_]*)[\"']")
#: A site that RELAYS a row name computed elsewhere. Counted and named, never
#: silently treated as covered: the name it prints comes from one of the
#: three patterns above, which is what makes this honest rather than a hole.
_RELAY = re.compile(r"FINDING \[\{")


def emit_sites(root: Path = CORE) -> dict:
    """`{ident: [file:line, …]}` for every finding-emitting site in the CLI."""
    found: dict = {}
    for path in sorted(root.glob("*.py")):
        if path.name == "refusals.py":
            # The roster's own file quotes row idents as DATA — the design's
            # firing inputs and the plants' expected output. Scanning it
            # would report the roster as its own coverage, which is the
            # same-parentage defect: an expectation derived from the artifact
            # it grades.
            continue
        text = path.read_text(encoding="utf-8")
        for pat in (_LITERAL, _RESULT_ADD, _PROBLEM):
            for m in pat.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                found.setdefault(m.group(1), []).append(f"{path.name}:{line}")
    return found


def relay_sites(root: Path = CORE) -> list:
    out = []
    for path in sorted(root.glob("*.py")):
        if path.name == "refusals.py":
            continue
        text = path.read_text(encoding="utf-8")
        for m in _RELAY.finditer(text):
            out.append(f"{path.name}:{text.count(chr(10), 0, m.start()) + 1}")
    return out


def check_coverage(out, root: Path = CORE) -> int:
    """ASSIGNED ITEM B. Every emit site maps to a registered row, or this
    fails with "finding emitted with no registered row".

    `root` is a parameter so the check itself can be RED-PROVEN: a row plants
    an unregistered emit site in a copy of this package and runs the scan
    over the copy. A coverage check that had never been shown to fire is the
    same clean-forever report it exists to catch.
    """
    registered = {r.expected_finding_row for r in refusals.ROWS}
    sites = emit_sites(root)
    relays = relay_sites(root)
    uncovered = {k: v for k, v in sites.items() if k not in registered}

    out("")
    out("EMIT-SITE COVERAGE (assigned item B) — every site in the code that "
        "emits a FINDING maps to a registered row, or this fails.")
    out(f"    finding-emitting row names found in the source: {len(sites)}")
    out(f"    registered rows (roster `finding_row` values): {len(registered)}")
    out(f"    relay sites (a row name computed elsewhere, printed here): "
        f"{len(relays)}"
        + (f" — {', '.join(relays)}" if relays else ""))
    out("    LIMIT, stated rather than left to be discovered: this check "
        "reads the SOURCE, so it catches a finding the code emits under no "
        "registered row. It CANNOT catch a refusal the PROSE requires and "
        "the code LACKS — that site does not exist, so no scan finds it. "
        "That remainder is found only by an end-to-end walk of design §3.9, "
        "and saying so is part of the check.")

    if not uncovered:
        out(f"    coverage: CLEAN — all {len(sites)} emitted row name(s) are "
            "registered.")
        return exits.CLEAN
    out(f"    FINDING [emit_site_unregistered] finding emitted with no "
        f"registered row — {len(uncovered)} row name(s):")
    for ident in sorted(uncovered):
        out(f"        {ident}: emitted at {', '.join(uncovered[ident])}")
    out("    A finding under an unregistered row is a refusal nobody proved: "
        "it has no plant, no control, and no line in the §3.9 snapshot, so "
        "the roster's green says nothing about it.")
    return exits.FINDING


def cmd_list(out) -> int:
    """`--test --list` — the roster as DATA, nothing executed.

    §3.9's table is a SNAPSHOT of this list; the table updates from here and
    never the reverse (decided at W1b's integration).
    """
    out(f"refusal roster: {len(refusals.ROWS)} executable row(s), "
        f"{len(refusals.PROSE_REST)} prose-rest row(s)")
    out("")
    for row in refusals.ROWS:
        out(f"{row.ident}")
        out(f"    refusal:       {row.refusal}")
        out(f"    firing input:  {row.firing_input}")
        out(f"    expects:       {exits.word(row.expect)}")
        out(f"    finding row:   {row.expected_finding_row}")
        out(f"    stage:         {row.stage}")
    out("")
    out("PROSE-REST — named by the design, not fireable here. Labelled with "
        "the reason, never deleted to make a roster green (D-g):")
    for name, why in refusals.PROSE_REST:
        out(f"    {name}")
        out(f"        {why}")
    return exits.CLEAN


def cmd_test(out, list_only: bool = False) -> int:
    if list_only:
        return cmd_list(out)

    out(f"lifecycle --test: the refusal roster, {len(refusals.ROWS)} row(s). "
        "Each row runs its PLANT and its CONTROL; the pair is the proof.")
    out("")

    passed = failed = skipped = raised = 0
    failures = []
    for row in refusals.ROWS:
        skip = getattr(row, "skip_reason", None)
        if skip:
            skipped += 1
            out(f"SKIP  {row.ident:<34} {skip}")
            continue
        try:
            fired = row.fire()
            control = row.control()
        except Exception:                                  # noqa: BLE001
            raised += 1
            failures.append(row.ident)
            out(f"ERROR {row.ident:<34} the row RAISED — could not verify")
            out("      " + traceback.format_exc().strip().replace(
                "\n", "\n      "))
            continue

        problems = []
        if fired.code != row.expect:
            problems.append(f"plant exited {exits.word(fired.code)}, expected "
                            f"{exits.word(row.expect)}")
        if control.code == row.expect:
            problems.append(f"the CONTROL also exited "
                            f"{exits.word(row.expect)} — the input under test "
                            "is not what produced it")
        if row.expect == exits.FINDING and \
                f"[{row.expected_finding_row}]" not in fired.output:
            problems.append("the plant fired, but nothing in its output names "
                            f"row [{row.expected_finding_row}]")
        if problems:
            failed += 1
            failures.append(row.ident)
            out(f"FAIL  {row.ident:<34} {row.stage}")
            for p in problems:
                out(f"      {p}")
            out(f"      plant output:\n      "
                + fired.output.strip().replace("\n", "\n      "))
        else:
            passed += 1
            out(f"PASS  {row.ident:<34} plant "
                f"{exits.word(fired.code)} / control "
                f"{exits.word(control.code)}   [{row.stage}]")

    out("")
    out("PROSE-REST — the design names these and this build cannot fire "
        "them. LABELLED, never deleted (D-g); they are not counted as "
        "passes and a green roster does not cover them:")
    for name, why in refusals.PROSE_REST:
        out(f"    PROSE-REST  {name}")
        out(f"                {why}")

    code = check_coverage(out)

    out("")
    out(f"rows: {len(refusals.ROWS)}   {passed} passed, {failed} failed, "
        f"{raised} raised, {skipped} skipped")
    out(f"prose-rest rows (not executed, labelled): "
        f"{len(refusals.PROSE_REST)}")
    if skipped:
        out("EVERY SKIP IS A CHECK THAT DID NOT RUN, and it is listed above "
            "with its reason. A skip is never part of a green line.")
    if raised:
        code = exits.worst([code, exits.COULD_NOT_VERIFY])
    if failed:
        code = exits.worst([code, exits.FINDING])
    if failures:
        out(f"FAILED/ERRORED: {', '.join(failures)}")
    out(f"lifecycle --test: {exits.word(code)}")
    return code
