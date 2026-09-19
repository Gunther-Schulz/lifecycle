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

A ROW HAS THE SAME THREE ANSWERS THE TOOL HAS (law 1, lc-143). A plant that
answers wrongly is a FAIL: the row's machinery was read and found broken. A
control that exits what the plant was supposed to prove is something else
entirely — the arms did not separate, so the row is unproven in EITHER
direction and the honest verdict is COULD NOT VERIFY. The two were one
verdict until lc-143, and the case that exposed it is this module's own
coverage check: its control scans a copy of the LIVE source, so a real
unregistered emit anywhere in the package contaminates the control, and the
row reported FAIL exactly when a genuine instance existed — the detector
disabled by the defect it detects, rendered as a failure of the detector.
Precedence is stated rather than left to fall out: a broken plant FAILS even
when the control is also contaminated, because a demonstrated wrong answer is
a verdict and must never hide behind an absence of one.

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

#: The repo this package lives in — `plugin/cli/lifecycle_core` up three.
#: Used to resolve the REACH POPULATION from the declaration's registered
#: kinds rather than from a directory glob (lc-245, W3).
PACKAGE_REPO = CORE.parent.parent.parent

#: THE CLASSIFIER, and it is the whole of W3's reach contract. A file is in
#: the scan's population if it IS executable Python — never if it is merely
#: NAMED like it.
#:
#: WHY THE NAME ALONE WAS THE DEFECT. `emit_sites` and `relay_sites` globbed
#: `lifecycle_core/*.py`, so `plugin/hooks/pre-commit` — which relays row
#: names on two live lines — was invisible, and the roster reported a clean
#: sweep over a population it had never visited. That is a check reporting
#: CLEAN over what it did not examine, which is the false feedback this
#: whole plugin exists to refuse.
#:
#: AND A WIDER GLOB CANNOT REPAIR IT. The `git hooks` kind's members are
#: EXTENSIONLESS BY CONSTRUCTION — a hook must be named `pre-commit` and
#: nothing else — so any extension-keyed predicate returns, over that entire
#: kind, a zero shaped exactly like a true absence. The second arm is what
#: makes the contract keyed on what a file IS.
_PY_SHEBANG = re.compile(r"^#!.*python")

#: KINDS THE REACH DECLARES OUT, with the reason, because a reach that
#: reads its own grading apparatus is not wider — it is wrong.
#:
#: `tests` is the roster's own instrument. Its members PLANT strings shaped
#: like emit sites in order to red-prove that this very scan fires on one,
#: so scanning them reports the planted fixtures as real unregistered
#: refusals — measured the moment W3 widened the reach: two fixtures in
#: `test_refusals.py` surfaced as findings about the product. That is the
#: same-parentage defect `emit_sites` already names for `refusals.py`: an
#: expectation read off the artifact that defines it.
#:
#: DECLARED RATHER THAN PATTERN-MATCHED, and VERIFIED below. A guard firing
#: on legitimate work is repaired by naming the legitimate case in data the
#: guard checks, never by softening the predicate — and `reach_paths`
#: RAISES if a name here is not a registered kind, so a rename fails loudly
#: instead of silently restoring the whole population.
REACH_EXCLUDED_KINDS = ("tests",)

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
#: A REFUSAL IS A REFUSAL WHICHEVER EXIT CODE CARRIES IT (lc-16 follow-up,
#: ruled 2026-09-18). This scan matched `FINDING [` alone, so a refusal
#: emitted as COULD NOT VERIFY was invisible to it — and `verify` shipped
#: with `verify_check_did_not_run` unregistered and unprovable while this
#: check reported CLEAN over it. That is the defect class this whole plugin
#: is built against, inside the instrument built to catch it: a check
#: reporting clean because it cannot see what it does not match. The
#: three-answer contract makes could-not-verify a FIRST-CLASS verdict, so a
#: roster blind to it proves two thirds of the contract and says nothing
#: about the third.
_LITERAL_CNV = re.compile(r"COULD NOT VERIFY \[([a-z_][a-z0-9_]*)\]")
_RESULT_ADD = re.compile(r"\.add\(\s*\n?\s*[\"']([a-z_][a-z0-9_]*)[\"']")
_PROBLEM = re.compile(r"problems\.append\(\(\s*\n?\s*[\"']([a-z_][a-z0-9_]*)[\"']")
#: A site that RELAYS a row name computed elsewhere. Counted and named, never
#: silently treated as covered: the name it prints comes from one of the
#: three patterns above, which is what makes this honest rather than a hole.
#:
#: VERDICT-AGNOSTIC SINCE lc-245, and it is the same repair `_LITERAL_CNV`
#: made for the literal side: this matched the finding word alone, so a
#: refusal RELAYED as could-not-verify was invisible to the scan that exists
#: to count relays. The verdict vocabulary is CLOSED at two members —
#: measured over the package in the r1 corpus, 119 of one and 3 of the other
#: and nothing else — so agnostic here means BOTH, never a widening.
_RELAY = re.compile(r"(?:FINDING|COULD NOT VERIFY) \[\{")


def is_executable_python(path: Path) -> bool:
    """Is this file executable Python — by what it IS, not what it is called?

    TWO ARMS, and the second is the one W3 exists for: a `.py` name, OR a
    first line naming a python interpreter. An unreadable or binary file is
    NOT python here — a file this classifier cannot read is a file the scan
    cannot scan, and answering True would hand the scanner bytes it will
    fail on rather than excluding them honestly.
    """
    if path.suffix == ".py":
        return True
    try:
        with open(path, "r", encoding="utf-8", errors="strict") as fh:
            first = fh.readline()
    except (OSError, UnicodeDecodeError):
        return False
    return bool(_PY_SHEBANG.match(first))


def reach_paths(root: Path | None = None, repo: Path | None = None,
                doc: dict | None = None) -> list:
    """The files the refusal scanners READ — the reach contract's population.

    TWO MODES, and they are not two policies: the CLASSIFIER is the same in
    both, and only the enumeration differs.

    THE REGISTERED-KIND MODE (`repo` + `doc`) is the production one. The
    population is every member of every registered kind that is executable
    Python, enumerated by the kind machinery's OWN member listing — the same
    `retire.list_home` that `kind list` and the retire walk use, so every
    legal home shape (a plain file, a glob, a carrier) has DEFINED behaviour
    here. A home shape this scan handled differently from the walk would be
    a second enumeration of one fact, and the shape nobody thought about
    would return a true-absence-shaped zero, which is the exact defect W3
    was booked for one level down.

    THE DIRECTORY MODE (`root`) is the RED-PROOF one, and it is not a
    fallback for production: the coverage check is proven by planting an
    unregistered emit site in a COPY of this package, and a copy has no
    declaration to enumerate from. It walks that directory with the SAME
    classifier — never a `*.py` glob, which would put an extension-keyed
    predicate back in the reach by the back door.
    """
    if repo is not None and doc is not None:
        from . import retire as retire_mod
        kinds = doc.get("kinds") or {}
        # THE EXEMPTION IS CHECKED AGAINST THE DECLARATION, not assumed. A
        # name that no longer registers a kind means the exemption is
        # silently covering nothing and the excluded population has quietly
        # rejoined the scan — the failure mode a hand-list always has, made
        # loud here rather than left to be discovered.
        missing = [k for k in REACH_EXCLUDED_KINDS if k not in kinds]
        if missing:
            raise ValueError(
                "reach_paths: REACH_EXCLUDED_KINDS names "
                f"{', '.join(repr(m) for m in missing)}, which this "
                "declaration does not register. The exemption is stale: "
                "either the kind was renamed and this list must follow, or "
                "it was retired and this entry must go. Left alone, the "
                "excluded files rejoin the scan without a word.")
        found = []
        for _name, body in kinds.items():
            if _name in REACH_EXCLUDED_KINDS:
                continue
            home = (body or {}).get("home")
            if not isinstance(home, str) or not home:
                continue
            instances, _note = retire_mod.list_home(repo, home)
            if instances is None:
                # COULD NOT VERIFY at the walk is COULD NOT VERIFY here too:
                # an unresolvable home contributes no files, and pretending
                # it contributed zero would be the absence-as-clean read.
                continue
            for inst in instances:
                p = Path(inst) if not isinstance(inst, Path) else inst
                if p.is_file() and is_executable_python(p):
                    found.append(p.resolve())
        return sorted(set(found))

    base = root if root is not None else CORE
    out = []
    for p in sorted(base.rglob("*")):
        if any(part in _SCAN_SKIP for part in p.parts):
            continue
        if p.is_file() and is_executable_python(p):
            out.append(p)
    return out


#: Directories the directory-mode walk never descends into. Named rather than
#: pattern-guessed, for `retire.SWEEP_SKIP_DIRS`' own reason: a walk that
#: skipped something by accident would report a clean board over exactly the
#: file nobody scanned.
_SCAN_SKIP = ("__pycache__", ".git", "node_modules", ".pytest_cache")


def emit_sites(root: Path = CORE, *, paths: list | None = None) -> dict:
    """`{ident: [file:line, …]}` for every REFUSAL-emitting site in the CLI.

    BOTH VERDICT WORDS, since lc-16's follow-up: the finding word and the
    could-not-verify word, each followed by a bracketed row name. A row's
    ident is its name whichever code carries it, and scanning one word alone
    left the other half of the three-answer contract unproven.

    Worded WITHOUT the literal forms, like the patterns above and for the
    same measured reason: this scan reads the package's own source, so a
    docstring spelling a pattern out is data the scan finds — the widening
    commit's first run reported a row called `x` from these very lines.
    """
    found: dict = {}
    for path in (paths if paths is not None else sorted(root.glob("*.py"))):
        if path.name == "refusals.py":
            # The roster's own file quotes row idents as DATA — the design's
            # firing inputs and the plants' expected output. Scanning it
            # would report the roster as its own coverage, which is the
            # same-parentage defect: an expectation derived from the artifact
            # it grades.
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for pat in (_LITERAL, _LITERAL_CNV, _RESULT_ADD, _PROBLEM):
            for m in pat.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                found.setdefault(m.group(1), []).append(f"{path.name}:{line}")
    return found


def relay_sites(root: Path = CORE, *, paths: list | None = None) -> list:
    """`[file:line, …]` for every site that prints a row name computed
    elsewhere — over the REACH POPULATION, not over a name pattern (lc-245).
    """
    out = []
    for path in (paths if paths is not None else sorted(root.glob("*.py"))):
        if path.name == "refusals.py":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for m in _RELAY.finditer(text):
            out.append(f"{path.name}:{text.count(chr(10), 0, m.start()) + 1}")
    return out


def check_coverage(out, root: Path = CORE, reach: list | None = None) -> int:
    """ASSIGNED ITEM B. Every emit site maps to a registered row, or this
    fails with "finding emitted with no registered row".

    `root` is a parameter so the check itself can be RED-PROVEN: a row plants
    an unregistered emit site in a copy of this package and runs the scan
    over the copy. A coverage check that had never been shown to fire is the
    same clean-forever report it exists to catch.
    """
    registered = {r.expected_finding_row for r in refusals.ROWS}
    # THE REACH, RESOLVED ONCE AND SHARED. Both scanners read the SAME
    # population, so a file one sees and the other does not is impossible by
    # construction — the relay count and the emit count are about one set.
    paths = reach if reach is not None else reach_paths(root=root)
    sites = emit_sites(paths=paths)
    relays = relay_sites(paths=paths)
    uncovered = {k: v for k, v in sites.items() if k not in registered}

    out("")
    out("EMIT-SITE COVERAGE (assigned item B) — every site in the code that "
        "emits a REFUSAL maps to a registered row, or this fails. BOTH "
        "verdict words are scanned, the finding word and the "
        "could-not-verify word. Scanning only the first is how one of "
        "`verify`'s two refusals shipped unregistered and unprovable while "
        "this check reported CLEAN over it.")
    if reach is None:
        out("    REACH: COULD NOT VERIFY — the registered kinds could not be "
            "read, so this scan fell back to walking this package's own "
            f"directory ({len(paths)} file(s)). Sites outside it — the "
            "commit-time hooks above all — were NOT examined, and a clean "
            "result below says nothing about them.")
    else:
        out(f"    REACH: {len(paths)} executable-Python file(s), enumerated "
            "from the REGISTERED KINDS by the kind machinery's own member "
            "listing and classified by what each file IS (a `.py` name OR a "
            "python shebang) — never by name alone. The `git hooks` kind's "
            "members are extensionless by construction, so an "
            "extension-keyed reach returned a true-absence-shaped zero over "
            "that whole kind (lc-245).")
    out(f"    refusal-emitting row names found in the source: {len(sites)}")
    out(f"    registered rows (roster `finding_row` values): {len(registered)}")
    out(f"    relay sites (a row name computed elsewhere, printed here): "
        f"{len(relays)}"
        + (f" — {', '.join(relays)}" if relays else ""))
    out("    LIMIT, stated rather than left to be discovered: this check "
        "reads the SOURCE, so it catches a refusal the code emits under no "
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


def check_routes(out) -> int:
    """THE ROUTE SET PER REFUSAL ROW (design §3.8c) — round 4's cross-row cure.

    THE DEFECT IT CATCHES is not an unproven row; it is a PROVEN row whose
    NAME promises more than the code watches. `dangling_reference` is the
    recorded case: its text said "dangling typed reference", the design says
    the refusal "reaches every type", and the code resolved `lane:` alone —
    so five of the six typed references in a declaration could point at
    nothing and the roster stayed green, because the row it belonged to fired
    correctly on the one route it did watch. A green row is not the same
    claim as a covered refusal.

    THE COMPARISON HAS TWO DIRECTIONS AND BOTH ARE FINDINGS (lc-30). The
    mirror — the code watching a route the refusal's own TEXT does not
    name — printed a note here and set no code, so a refusal catching MORE
    than it says contributed CLEAN and the operator reading the finding got
    a WRONG CAUSE for their entry. That asymmetry was itself the defect: one
    difference set is `route_set_unwatched`, the other `route_set_unnamed`,
    and a note is not a verdict. The two are separate rows rather than one
    because they have separate REPAIRS — widen the code, or widen the text —
    and an operator told only "these disagree" cannot tell which is owed.

    THE TWO SIDES ARE READ INDEPENDENTLY, which is what makes the comparison
    mean anything. The ROUTE SET is the closed vocabulary the refusal's own
    text names and is read from the DESIGN's side of the code (a declared
    tuple such as `declaration.REF_TYPES`); the WATCHED set is derived from
    the SOURCE, exactly as the emit-site check derives sites. An expectation
    read off the artifact it grades moves with the mutant and stays green on
    the corruption it exists to catch — so neither side is computed from the
    other.

    ROWS WITH NO DECLARED ROUTE SET are not silently passed: their derived
    emit sites are printed and counted, so the roster says how much of itself
    this check covered.
    """
    out("")
    out("ROUTE SETS (design §3.8c) — beside its firing input, a row states "
        "the ROUTE SET it watches. A row whose refusal TEXT names an effect "
        "WIDER than its routes fails here, even though its plant and control "
        "both pass: a green row and a covered refusal are different claims. "
        "So does the MIRROR: a row whose code watches a route its own text "
        "does not name catches MORE than it says, and the operator reading "
        "that finding gets a wrong cause.")

    sites = emit_sites()
    declared = [r for r in refusals.ROWS if getattr(r, "route_set", ())]
    undeclared = [r for r in refusals.ROWS if not getattr(r, "route_set", ())]

    code = exits.CLEAN
    for row in declared:
        try:
            watched = set(row.routes_watched())
        except Exception as exc:                              # noqa: BLE001
            out(f"    COULD NOT VERIFY  {row.ident}: its watched-route "
                f"derivation raised {type(exc).__name__}: {exc}")
            code = exits.worst([code, exits.COULD_NOT_VERIFY])
            continue
        full = set(row.route_set)
        missing = sorted(full - watched)
        stray = sorted(watched - full)
        out(f"    {row.ident}")
        out(f"        route set (what the refusal's TEXT names): "
            f"{', '.join(row.route_set)}")
        out(f"        watched   (derived from the SOURCE):        "
            f"{', '.join(sorted(watched)) or '(none)'}")
        if stray:
            out(f"        FINDING [route_set_unnamed] {len(stray)} route(s) "
                f"watched by the code and named by nothing in this refusal's "
                f"TEXT: {', '.join(stray)}. The refusal catches MORE than it "
                "says, so an entry arriving by one of these is refused under "
                "a text that does not describe it and the operator gets a "
                "WRONG CAUSE. The repair is the TEXT's — widen it to what the "
                "code watches, or split the extra route into its own row.")
            code = exits.worst([code, exits.FINDING])
        if missing:
            out(f"        FINDING [route_set_unwatched] {len(missing)} route(s) "
                f"named by this refusal and watched by nothing: "
                f"{', '.join(missing)}. The row fires correctly on the routes "
                "it does watch, so its green says nothing about these — an "
                "input arriving by an unwatched route returns exactly what a "
                "clean repo returns.")
            code = exits.worst([code, exits.FINDING])
        # NOT an `else` on `missing`, which is what it was: with the mirror
        # now a finding, an `else` would print CLEAN over a row whose stray
        # set is non-empty — the verdict line contradicting the finding two
        # lines above it, and a reader who stops at the verdict taking the
        # CLEAN.
        if not missing and not stray:
            out("        routes: CLEAN — every route the refusal names is "
                "watched, and every route it watches is named.")

    out(f"    rows with a declared route set: {len(declared)}")
    out(f"    rows without one: {len(undeclared)} — their route set is their "
        "derived EMIT SITES, printed by `--test --list`. Listed rather than "
        "passed: this check covers a refusal defined over a closed "
        "VOCABULARY, and a row whose refusal is one site has no vocabulary "
        "for it to be wider than.")
    multi = sorted(k for k in sites if len(sites[k]) > 1)
    out(f"    refusals emitted at MORE THAN ONE site: {len(multi)} — "
        + (", ".join(f"{k} ({len(sites[k])})" for k in multi) or "none"))
    out("    A refusal at several sites is not itself a defect (§3.8c splits "
        "a row only where the sites yield different ANSWER CLASSES); it is "
        "where the route question is worth asking.")
    return code


def cmd_list(out) -> int:
    """`--test --list` — the roster as DATA, nothing executed.

    §3.9's table is a SNAPSHOT of this list; the table updates from here and
    never the reverse (decided at W1b's integration).
    """
    sites = emit_sites()
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
        emitted = sites.get(row.expected_finding_row, [])
        if getattr(row, "route_set", ()):
            out(f"    route set:     {', '.join(row.route_set)}   (a closed "
                "VOCABULARY, checked against the source)")
        elif not emitted:
            out("    route set:     (no emit site — this row's verdict is a "
                "code, not a named finding)")
        else:
            # THE MODULES AND THE COUNT, never a truncated list of sites. A
            # list cut off at a column width is a partial view standing in for
            # its whole body, and the reader cannot tell a short one from a
            # clipped one. The full sites are in `emit_sites()`, which is what
            # the coverage check reads.
            mods = sorted({s.split(":", 1)[0] for s in emitted})
            out(f"    route set:     {len(emitted)} emit site(s) in "
                f"{', '.join(mods)}   (derived; this refusal names no closed "
                "vocabulary for the route check to compare against)")
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

    passed = failed = skipped = raised = unverified = 0
    failures = []
    unproven = []
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

        # BROKEN is what the PLANT answered; BLIND is what the CONTROL did.
        # Kept apart because they are different answers: the first is a
        # verdict about the row, the second is the absence of one.
        broken = []
        blind = []
        if fired.code != row.expect:
            broken.append(f"plant exited {exits.word(fired.code)}, expected "
                          f"{exits.word(row.expect)}")
        if control.code == row.expect:
            blind.append(f"the CONTROL also exited "
                         f"{exits.word(row.expect)} — the input under test "
                         "is not what produced it, so this pair separates "
                         "nothing and the row is UNPROVEN in either "
                         "direction")
        if row.expect == exits.FINDING and \
                f"[{row.expected_finding_row}]" not in fired.output:
            broken.append("the plant fired, but nothing in its output names "
                          f"row [{row.expected_finding_row}]")
        if broken:
            failed += 1
            failures.append(row.ident)
            out(f"FAIL  {row.ident:<34} {row.stage}")
            for p in broken + blind:
                out(f"      {p}")
            out(f"      plant output:\n      "
                + fired.output.strip().replace("\n", "\n      "))
        elif blind:
            # The plant answered exactly as the row names it should. What
            # went wrong is outside the input under test, so the CONTROL's
            # output is the evidence here — it is what carries the name of
            # whatever contaminated it, and without that name the reader is
            # told the pair is blind and not what blinded it.
            unverified += 1
            unproven.append(row.ident)
            out(f"COULD NOT VERIFY  {row.ident:<34} {row.stage}")
            for p in blind:
                out(f"      {p}")
            out("      The plant answered exactly what this row names, so "
                "this is not a failure of the row — the control could not "
                "serve as one. Control output:")
            out("      " + control.output.strip().replace("\n", "\n      "))
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

    # THE PRODUCTION REACH comes from the REGISTERED KINDS, not from this
    # package's directory (lc-245). Falling back to the directory walk when
    # the declaration cannot be read is deliberate and is REPORTED by
    # `check_coverage` itself: a scan that silently narrowed its own
    # population would be the clean-over-unexamined report this check exists
    # to refuse.
    reach = None
    try:
        from . import declaration as decl_mod
        res = decl_mod.read(PACKAGE_REPO)
        if res.declaration is not None:
            reach = reach_paths(repo=PACKAGE_REPO, doc=res.declaration)
    except Exception:  # noqa: BLE001 — a broken declaration must not kill
        reach = None   # the roster; the narrowed reach is reported below.

    code = check_coverage(out, reach=reach)
    code = exits.worst([code, check_routes(out)])

    out("")
    out(f"rows: {len(refusals.ROWS)}   {passed} passed, {failed} failed, "
        f"{unverified} could not verify, {raised} raised, {skipped} skipped")
    out(f"prose-rest rows (not executed, labelled): "
        f"{len(refusals.PROSE_REST)}")
    if skipped:
        out("EVERY SKIP IS A CHECK THAT DID NOT RUN, and it is listed above "
            "with its reason. A skip is never part of a green line.")
    if unverified:
        out("A ROW THAT COULD NOT BE VERIFIED IS NOT A ROW THAT FAILED, and "
            "it is not part of a green line either. Its arms did not "
            "separate, so nothing here says whether its refusal works; the "
            "repair is to the ARRANGEMENT — give the control a source the "
            "contaminating defect cannot reach — never to the row's verdict.")
    if raised:
        code = exits.worst([code, exits.COULD_NOT_VERIFY])
    if unverified:
        code = exits.worst([code, exits.COULD_NOT_VERIFY])
    if failed:
        code = exits.worst([code, exits.FINDING])
    if failures:
        out(f"FAILED/ERRORED: {', '.join(failures)}")
    if unproven:
        out(f"COULD NOT VERIFY: {', '.join(unproven)}")
    out(f"lifecycle --test: {exits.word(code)}")
    return code
