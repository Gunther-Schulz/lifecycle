# lifecycle — working discipline

A Claude Code plugin: lifecycle management for everything a repo
persists. The primitive is the KIND, not the item — every kind of
thing a repo keeps is registered in that repo's
`.claude/lifecycle.json` with six declared stages (home, writer,
reader, staleness, exit, bound), and a kind with an undeclared stage
is a checker finding.

Design of record: `carrier-rework-design-2026-08-26.md` in
claude-code-cache-fix (`docs/directives/`), revision 2. Where this
repo and that document differ, the design wins and the difference is
a defect here.

**This file is this repo's declared LAWS file. It has no cap — its size is
reported, never refused (R22).** Laws bind; they do not explain themselves.
Every law that was earned rather than assumed cites a dated entry in
`JOURNAL.md`, and **a law without a journal pointer has no basis, while a
journal entry nothing cites is stale by change-coupling.** Incidents never
appear inline beside a law: inlining the why is what makes a laws file too
long to be read, which is the only way a laws file actually fails.

## The INVARIANTS — this plugin's definition of "controlled"

Distinct from LAWS (how a session acts in a repo) and from REFUSALS (checks
the tool runs): **invariants are properties that must hold of the workspace at
every moment, whoever worked last, and they do not care who broke them.** They
open these docs because the refusal registry is DERIVED from them — a row
exists to defend an invariant, and a row defending none is a row nobody can
justify. A declaring repo is held to them by the tool, may add its own in its
declaration, and may never subtract.

1. Every persisted thing resolves to a registered kind.
2. Every kind has an owner for every stage: writer, reader, staleness, exit,
   growth control.
3. One home per kind; a fact lives in exactly one place.
4. Nothing dangles: every typed reference resolves; every lane has a reader;
   every producer has a disposition; every detector has a home.
5. Every exit is recorded — a move, a compaction, a drop, each with its reason
   and its commit.
6. Every autonomous decision is recorded with its basis before the act, and is
   redirectable.
7. Nothing enters without a reason: an item names its requirement and goal; a
   kind names why it exists; an unbounded kind names why.
8. Growth is controlled by flow, never by size.
9. What the tool cannot enforce is labelled prose-rest, never presented as
   enforced.

## The LAWS

Every one of these was earned on 2026-08-26, across four dispatches. The
journal pointer is where the incident lives.

1. **Three answers, always**: clean / finding / could-not-verify. A finding
   and an unreadable input never share an exit code. (J1)
2. **Every refusal is a registry row with the input that fires it, proven red
   first**; a row that cannot be fired is labelled PROSE-REST, never deleted to
   green the roster. A roster asserting only its plants ships green. (J2, J17)
3. **The registry is the source**; every table of it elsewhere is a snapshot.
   Every site that emits a finding maps to a row, or `--test` fails. (J2, J3)
4. **A red from a module-load or import error is not a discriminating red.**
   The arrangement is stated: which side was old, where the expectation came
   from, baseline green first. (J4)
5. **A check whose verdict is another tool's exit code draws its own pair from
   that tool**, in the invocation mode the code will use, before the code is
   written around it. Flags are part of the instrument. (J5)
6. **No hardcoded machine path, login, repo root or XDG root anywhere**;
   boundaries are derived at run time. A public tree is the reason. (J6)
7. **The leak scan is armed before the repo's own first commit** and runs on
   every push; a clean scan never shown to fire proves nothing. (J7)
8. **The tool is the only writer of the carriers it owns**; a hand edit that
   breaks the shape fails at commit; a lock serializes writers. (J8)
9. **A two-file move is one act**: append, delete, commit. A crash leaves a
   DUPLICATE, never a loss, and the next check says so. (J8)
10. **READY is judged, never derived.** Blocker clearance decides
    schedulability only. (J9)
11. **A guard that fires on legitimate work stops the lane**; the repair is a
    declared exemption the guard verifies, never a softened predicate, and
    `--no-verify` is never taken — it kills every lane in the hook. (J10)
12. **Versions climb and never go backwards**; the birth series is `0.1.x`.
    (J10)
13. **Installed symlinked from the dev checkout** on the machine that builds
    it; pinned and drift-detected elsewhere; the cache keeps three.
14. **`ITEMS.md` carries a schema line**; the tool refuses above its floor.
    (J8)
15. **Every registered kind declares all its stages**, including the ones a
    later wave implements — declared-but-not-implemented is a state,
    undeclared is a finding.
16. **Templates carry no project identifiers**; a public repo refuses a foreign
    binding; the default under a missing declaration is refuse.
17. **Reports are booked from the file, never the summary**; every figure a
    lane reports is re-run at the integrating desk before it is believed — and
    a discrepancy between your count and a lane's is a claim about your
    instrument first. (J11)
18. **A brief is not amended in place after dispatch; the executor re-reads it
    at HEAD before each verifier run; a correction that matters is a
    stop-and-redispatch.** Three clauses because three parties: the sender does
    not edit under a running lane, the receiver does not trust its
    dispatch-time copy, and a change that invalidates the work stops the work.
    The report channel names a target the executor can resolve. (J12)
19. **An unverified negative that agrees with a held suspicion is where the
    free probe is owed** — and where it feels unnecessary. (J13)
20. **What a push carried is settled at the remote**, never by the local
    reflog or the hook's printed range. (J14)
21. **A lane that finds a defect in its own shipped code after its report
    REPORTS it**; its write grant is over. (J15)
22. **A check no input can falsify is deleted, not registered**; a partition
    exact by construction is reported as could-not-verify arithmetic, never as
    a green row. (J16)

---

The sections below are OPERATIONAL REFERENCE, not laws. Wave 2 sorts them —
procedures into workflows, measurements into audits — under the design's
decomposition rule. They are kept here rather than dropped because nothing has
a home for them yet, and a rule dropped before its home exists is a rule lost.

## The two exit-code contracts — do not unify them

They are different contracts and a translation layer between them
would destroy the distinction each one exists to make.

- **A `lifecycle` verb exits** `0` clean · `2` a finding · `3` could
  not verify. A finding and an unreadable input never share a code.
  This is what a caller of `lifecycle item …`, `lifecycle kind …`,
  `lifecycle migrate`, `lifecycle --test` reads.
- **A lane's `Trigger:` predicate — a command `lane list` EXECUTES,
  never a `lifecycle` verb — exits** `0` fire · `1` quiet · `>=2`
  broken. `lane list` reads that code and reports the lane's state,
  so a dead predicate never renders as a clean board.

`lane list` is the one place both meet: it EXITS under the first
contract while READING the second. A `lane list` run that finds a
broken predicate exits `2` because it found something — not because
it saw a `2`.

## Discipline

- **A checker has THREE answers**: verified clean, verified broken,
  and COULD NOT VERIFY — which is its own answer, folded into
  neither. Silence, or a number shaped like a pass, is never allowed:
  if a run proves nothing, its output says it proves nothing.
- **A check counts only once it has gone RED on the real defect.**
  Not "would have caught it" — demonstrated, with the arrangement
  recorded. A red that is a module-load or import error proves the
  code is new, never that the check discriminates: after the checker
  exists, disable ONE named condition and watch that specific bite go
  red.
- **The refusal table is one source for two consumers** — the
  acceptance test and `lifecycle --test`. Rows live in
  `plugin/cli/lifecycle_core/refusals.py` as executable firing
  inputs; nothing restates them in prose. A row that cannot be fired
  is labelled PROSE-REST with its reason and is never deleted to make
  the roster green.
- **The leak scan runs before the irreversible boundary.**
  `tools/absence-scan.mjs` is armed as this repo's pre-push hook
  (`tools/git-hooks/pre-push`, symlinked into `.git/hooks/`) from the
  repo's first commit, because this repo is where workflow templates
  extracted from PRIVATE repos will land. No template is extracted
  until that hook exists.
- **Nothing crosses the seam.** Templates carry no project
  identifiers upward; a repo file declares and never restates
  downward.

## Role files

- `LEDGER.md` — the on-disk ledger: one entry per line, append-only,
  chronological. Facts with their basis, decisions with their why,
  open questions. Read its tail before re-deriving anything that may
  be settled.
- `BACKLOG.md` — parked items (each with its named missing evidence)
  and ready items (decision-complete, dispatchable).
- `dev-notes/` — the maintenance layer, never loaded by operational
  files.
- `tools/` — repo-owned checks. `absence-scan.mjs` and `tmpdir.mjs`
  are byte-identical copies of claude-code-cache-fix's; they are not
  edited here. That repo keeps its own copy and its own wiring, and
  the de-duplication is a later wave's act with the hook rewiring in
  the same change. Two copies for one wave is the deliberate cost.
- `test/` — `absence-scan.test.mjs` and its fixture are byte-identical
  copies too; the `test_*.py` files are this repo's own.
- `plugin/cli/` — the `lifecycle` entry point and its package.

## The two carrier invariants a reader must not conflate

- **Conservation has a SIGN, and the two signs are two diagnoses.** SHORT
  (`items + done` below `baseline + added − compacted`) means a body left by
  a path that is not a closure — a hand deletion, a bad merge. OVER means
  the homes hold more than was ever admitted, whose ordinary cause is an
  interrupted close, and it is RECOVERABLE. One message for both told the
  loss story over the recoverable case; that is why there are two rows.
- **DUPLICATE is the move's design working, not corruption.** A close
  appends to the done home, then deletes from the carrier, then commits. The
  window between the first two holds two copies of one body, and the
  opposite ordering would put that window on the LOSS side instead. So an id
  in both homes is expected debris from an interrupted close: the repair is
  to delete the LIVE copy once the done copy is confirmed complete, never to
  pick one at random.

## The router, and the ONE trigger evaluator

`lane list` is generated over `~/.config/lifecycle/repos` — one repo path
per line — and each listed repo's declaration. It prints the roster count
and every repo's resolution state LONGHAND, because a sparse table renders
as silence and silence reads as clean: an absent roster is BROKEN, a listed
repo that does not resolve is NAMED, and a repo declaring zero lanes says
so in a line of its own.

**There is ONE trigger evaluator, `lanes.evaluate_trigger`, and both callers
use it.** `lane list` reads a lane's `Trigger:`; `item ready` reads an
`evidence <predicate>` blocker, which §3.1 says is "evaluated like a
trigger". A second body behind that contract would disagree about the `>=2`
BROKEN case first, and that is the case that decides whether a dead
predicate reads as a clean board.

The blocker mapping is NOT the identity, and the reason is worth keeping:
a trigger FIRES when its condition holds, and for a blocker the condition
holding means the evidence ARRIVED — so `0` is UNBLOCKED, `1` is waiting in
the machine's court, and `>=2` is a FINDING rather than a wait. A broken
predicate folded into "still blocked" leaves the item waiting forever while
the board shows ordinary waiting.

## Verify

```bash
python3 -m unittest discover -s test -p 'test_*.py' -t .   # the CLI
python3 plugin/cli/lifecycle --test                        # the roster + coverage
python3 tools/prove-rows.py                                # every row, red-first
node --test test/absence-scan.test.mjs                     # the leak scan's bites
node tools/absence-scan.mjs --git-range ..HEAD             # the leak scan itself
```

`lifecycle --test` runs every roster row's plant AND control and prints
full counts including skips, then runs the EMIT-SITE COVERAGE check: every
site in the source that emits a FINDING maps to a registered row, or
`--test` fails. `--test --list` prints the roster as data — design §3.9's
table is a SNAPSHOT of that list and updates from it, never the reverse.

**The coverage check's assurance is exactly as wide as its predicate, and
it says so in its own output.** It reads the SOURCE, so it catches a
finding the code emits under no registered row — six of those existed and
were unproven until it first ran. It CANNOT catch a refusal the PROSE
requires and the code LACKS: that site does not exist, so no scan finds it,
and only an end-to-end walk of §3.9 does.

`tools/prove-rows.py` is the RED half of "a check counts only once it has
gone red", made re-runnable. For each recorded arrangement it disables one
named condition, runs the whole roster, and asserts a PAIR: the named row's
verdict changes, and no other row's does. A row whose mutation darkens
nothing is passing for a reason nobody wrote down; a mutation that darkens
four rows proves none of them. It restores by FILE COPY and clears
`__pycache__` around every arm. Rows with no recorded mutation are LISTED at
the end, never omitted — the roster says how much of itself is proven.

**A mutation may darken a row's SIBLINGS and that is not a stray.** Two
roster rows can prove two firing inputs of ONE refusal — the roster declares
that with `Row.finding_row`, and the ignored declaration (untracked, and
committed) is the case. The single site where that refusal is decided is one
branch, so a mutation there darkens both. The assertion is therefore "the
named row changed, and every row that changed proves the SAME refusal",
with the family derived from the roster's own mapping rather than listed
here. For a row with no sibling it is bit-for-bit the old "exactly one".

**The verdict it compares is the exit code AND the row name in the output.**
Codes alone do not discriminate here: every finding is a `2`, so a guard
removed at one site while a shared one catches the same input under a
different row's name reads as "unchanged" and the row reads as unproven.

**One of the 51 node bites fails here and is EXPECTED to** — read it
before treating it as a defect. `source: every UUID in a tracked
SOURCE_SCANNABLE file is on the synthetic allowlist` guards itself
against a silent scope collapse by asserting the walk reached
`test/`, `tools/`, `proxy/` and `docs/`, that `BACKLOG.md` is in it,
and that it enumerated more than 500 files. Those anchors are
claude-code-cache-fix's tree, and the file is a byte-identical copy
that is not edited here — so the bite structurally cannot pass in
this repo. It is a COULD NOT VERIFY for that one bite, never a
statement about the scanner: the other 50 pass, and the scanner is
separately red-proven on this repo's own files by the pre-push hook.
Making it portable means parameterising the anchors in cache-fix
first, so both copies move together.
