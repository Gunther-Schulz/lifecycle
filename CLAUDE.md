# lifecycle — working discipline

A Claude Code plugin: lifecycle management for everything a repo
persists. The primitive is the KIND, not the item — every kind of
thing a repo keeps is registered in that repo's
`.claude/lifecycle.json` with seven declared stages (home, writer,
reader, staleness, exit, **growth**, **trigger**), and a kind with an
undeclared stage is a checker finding.

## Grounding — read before your first write

**The floor is the reading roster** (`.claude/required-reading.json`),
and it is ENFORCED: a gate arms on your first write in this repo, so
this is a fact about what will happen, not a request. It carries
`docs/the-loop.md` (the gap map), `docs/answerable-not-felt.md` (the
design of record, whose own header block demands its research companion
before anything is built on it), and `docs/purpose.md` (the north star —
a session that skips it optimizes the wrong quantity).

**DESIGN-ARC work** — the decision round, new mechanisms, schema
changes — grounds additionally in `docs/answerable-not-felt-research.md`
(it CORRECTS the design doc's central framing rather than confirming
it), the decision round's agenda in
`docs/directives/2026-09-19-answerable-arc-decision-round.md` addendum 5,
and the audits that agenda cites.

**Everything else is found, not listed.** `kind list --digest` is the
index: one line per kind, home and newest member. This block is a
pointer, never a second corpus — a list that grows here is one nobody
reads.

**Growth is controlled by FLOW, never by size (R22).** The sixth stage takes
one of `bounded-by-exit` / `compacted` / `unbounded-with-reason`, and the
alarm is a kind that GREW WITHOUT AN EXIT EVENT — whatever its count. There
are no caps here: the `bound` stage and `ready-cap` were both withdrawn in
the schema wave, because a cap bounds a LABEL and a capped label is escaped
by relabelling (J9). One schema version per repo, stamped in the declaration;
a carrier whose `schema:` line does not EQUAL it is a finding.
**WITH ONE EXEMPTION, AND IT IS A KIND OF CARRIER RATHER THAN A FILE: a
RECORD home is PINNED at the version it closed at and is never graded
against the floor.** A closure record's whole value is that it means what it
meant when it was written — a line only means anything against a fixed
blob — so a bump that rewrote the archive would destroy the property the
archive exists for. The exemption is EXECUTABLE and not prose-rest:
`carrier_homes` names the homes one-schema-per-repo reaches, and a record
home's ABSENCE from that list is the pin. Live bodies of the same kind are
NOT exempt and are reached even where their home is a glob — the exclusion
that used to drop every glob home was protecting the records, and it now
protects only them.

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
2. Every kind has an owner for every stage: home, writer, reader, staleness,
   exit, growth control.
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
   breaks the shape fails at commit; a lock serializes writers. **And it is
   their authoritative READER:** an item's CURRENT truth comes from
   `item slots <id>`, which resolves amendments, and its amendment HISTORY
   from the raw block, which `item slots` drops — both reads exist because
   neither is sufficient. A hand-rolled slice of a carrier is neither, and a
   truncating one drops exactly the lines that supersede, since amendment
   slots sit at the end of a block. Prose-rest: no predicate distinguishes
   such a read from any other file read. (J8, J23)
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
    it; pinned and drift-detected elsewhere; the cache keeps three. (NO
    JOURNAL ENTRY SUPPORTS THIS — checked against every J-numbered entry in
    `JOURNAL.md`, found in none. It restates the design's own deployment
    convention — §3.8b's homes table row for plugin-cache versions — rather
    than an incident earned in this repo. A fabricated pointer would be
    worse than the gap; left uncited until a real incident earns one.)
14. **`ITEMS.md` carries a schema line**; the tool refuses above its floor.
    (J8)
15. **Every registered kind declares all its stages**, including the ones a
    later wave implements — declared-but-not-implemented is a state,
    undeclared is a finding. (NO JOURNAL ENTRY SUPPORTS THIS — checked
    against every J-numbered entry, found in none. It restates §3.0's own
    invariant 2 directly rather than an incident earned in this repo; left
    uncited rather than pinned to a J-entry that does not actually bear it.)
16. **Templates carry no project identifiers**; a public repo refuses a foreign
    binding; the default under a missing declaration is refuse. (NO JOURNAL
    ENTRY SUPPORTS THIS — checked against every J-numbered entry, found in
    none. No template has been extracted yet (§3.3: "No template is
    extracted until that hook exists"), so no incident about one leaking a
    project identifier could exist; the missing-declaration default is
    §3.1's own REFUSE-UNLESS-DECLARED-PRIVATE rule, not an earned lesson.
    Left uncited until a real incident earns one.)
17. **Reports are booked from the file, never the summary**; every figure a
    lane reports is re-run at the integrating desk before it is believed — and
    a discrepancy between your count and a lane's is a claim about your
    instrument first. **A CONSOLE RENDERING IS A SUMMARY TOO:** where a
    runner exposes a result OBJECT, a claim about which test did what comes
    off the object (`res.skipped`, `t.id()`), never off `-v` output, which
    prints one test's name beside the NEXT test's status. Same for any
    two-column rendering read by eye — a `grep -c` over a diff counts
    context lines alongside changed ones. (J11, J24)
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
23. **A design line that names a thing names its home, its writer and its
    reader**; a home is always explicit, never a default the tool assumes.
    (J20)
24. **A verb named is a verb placed in a stage**; a refusal named has its
    firing input; neither exists in prose alone. **AND A WRITE BOUNDARY
    IS COMPLETE ONLY WHEN EVERY COMMISSIONED CHANGE RESOLVES TO THE FILE
    THAT REALIZES IT *AND* TO EVERY FILE THAT MUST MOVE WITH IT.**
    Neither half is minted here: REALIZES is the dispatch skill's
    realization-surfaces rule, MUST-MOVE-WITH is the global corpus's
    dependents rule, whose own convention already says the dependents
    search rides the change — and a `write-set:` slot is what mechanizes
    that at booking time. Realizes is the SUBSET. Every boundary halt
    this repo has measured sat in the difference between the two.
    WORKED EXAMPLES, which are not the rule and never bound it. An item
    whose done-criterion emits a NEW finding carries `refusals.py`,
    because law 2 puts a refusal's realizing file there. A NEW VERB
    realizes in four places: its BODY (`verbs.py`), its WIRING
    (`cli.py`: the subparser, the action tuple, the `_carrier_verb`
    branch), any SLOT VOCABULARY it writes (`items.py`, where
    acceptance is decided), and its REFUSAL. lc-120 carried all four,
    ran green end to end, and still could not land: `test_verbs.py`
    holds a hand-written dispatch table that DERIVES the action tuple
    from source and grades itself against it. That file realizes
    nothing — the verb works without it — and depends loudly, so it
    reddened the moment the tuple grew.
    READ THAT INCIDENT THE RIGHT WAY ROUND: the table is the anchor
    rule's GOOD form, and its red is the dependents rule WORKING. The
    defect was never the table; it was a write set that did not carry
    it. A law that made anyone derive that table to keep a boundary
    quiet would trade one loud red for permanent silent drift.
    NOT THIS LAW: "which ARRANGEMENT grades this predicate" is
    instrument coupling — read-or-execute overlap between agents — and
    belongs to lc-139, not here. One sentence answering both questions
    would answer neither.
    Prose, not a predicate: "does this criterion propose a verb" is not
    computable and a guard over item prose fires on legitimate work
    (law 11). The computable slice is per-SHAPE and lives at booking:
    lc-154 for a source-derivable enumeration, the one shape measured.
    (J20, J22, J25, J26)
25. **Every schema change ships its migration, dry-run first, over every
    declared repo, before it is applied anywhere.** (J21)
    **A DRY RUN LICENSES ONLY WHAT IT EXERCISES, AND IT EXERCISES THE READER.**
    Measured 2026-09-18: the apply resolved a carrier head with a DIFFERENT
    predicate than the plan read it with, so it reported three carriers written
    while changing none — and where a body line below the head resembled one, it
    rewrote THAT instead. Both are invisible to any number of clean dry runs, by
    construction. So THE APPLY READS BACK FROM THE ARTIFACT and asserts the new
    state arrived, per target, BEFORE it reports applied — never the printed
    `written:` line, which is precisely what lied. The writing command's exit
    says the write happened, never that what arrived is what was meant. A
    read-back catches this class and every unfound sibling of it WITHOUT KNOWING
    THE CLASS IN ADVANCE, which is why it is the general instrument and not this
    defect's cleanup. (J28)
    **AND AFTER A MIGRATION, ONLY THE NEW STATE EXISTS.** Operator decision,
    2026-09-18: the old carrier does not survive as a courtesy copy, and the
    stated basis is that git holds every prior state — retiring the source
    destroys nothing, so the reversible test passes at the REPO and not merely
    at the desk. This is law 9 at carrier scale: a move is append, delete,
    commit, and one that never deletes is not a move but a duplication.
    THE MECHANISM IS POLARITY, NOT FORCE, and that distinction is the rule.
    `--retire-source`'s four preconditions gate the ACT and are not softened —
    deleting past them would be a destructive step sized to intent rather than
    to the object's current state. What changes is the SILENCE: retiring is
    opt-in today, so two coexisting states are the default outcome and nothing
    anywhere calls that wrong. A completed migration whose source still exists
    is a FINDING naming the source and the exit it has not taken. An operator
    who wants both states keeps them, and now has to say so.
    Law 26's default question at its first case: the lazy path currently ends
    with legacy files lying around, so the repair moves the DEFAULT rather than
    adding a rule telling anyone to remember. This repo is its own first case
    and already took the exit correctly — `BACKLOG.md` was DELETED at migration
    with its citations pinned to the deleting commit's parent, which the ruling
    now makes general rather than exemplary.
26. **A DESIGN ANSWERS WHAT MUST BE WRITTEN BEFORE IT ANSWERS WHAT MUST BE
    REMEMBERED, NOTICED OR DECIDED WELL.** Operator direction, 2026-09-18, as
    the guiding principle for everything designed here. The question comes
    first, at sign-off, and it is answerable or the design is not signed: what
    must be WRITTEN at the moment this fires, whose ABSENCE IS COMPUTABLE?
    The slot demands the STATEMENT, never the answer — a genuinely undecidable
    question states that in one line and passes — and the fill's QUALITY stays
    judgment, which is the boundary that keeps this from becoming the
    over-constraint it exists to avoid. It is the transition table's OBSERVER
    column asked as a design question rather than read as a schema field.
    **AND A CLAIM IN PROSE BESIDE A MECHANISM IS HELD BY NOTHING.** It
    inherits the mechanism's authority to every reader while no check grades
    it, which makes it worse than a bare claim standing alone. The direction
    that bites is the SILENT one: a declared expectation going stale toward
    FAILING is loud and somebody looks, while one going stale toward PASSING
    degrades the instrument — readers are trained that a red here is expected,
    and the one real red arrives pre-discounted. This file did exactly that to
    its own readers for a month.
    Not a licence to mechanize judgment: where the trigger is not a computable
    predicate with near-zero false fires, the computable slice precipitates and
    the remainder stays prose (law 11 still binds, and a guard firing on
    legitimate work still stops the lane). (J27)
    **AND ONE QUESTION COMES BEFORE THE WRITING QUESTION: CAN THE DEFAULT MAKE
    THE WRITING UNNECESSARY?** Operator direction, 2026-09-18, and it BOUNDS
    this law rather than extending it — law 26 asked unbounded generates ever
    more required writing, which is the over-constraint it exists to avoid.
    Ask first what route the next writer takes without thinking: the nearest
    pattern, the file already open, the shortest expression that parses. Where
    that route produces the correct behaviour — the value DEFAULTED, the
    dangerous character folded or refused at the constructor, the third answer
    returned by the parser rather than by each caller — nothing needs
    remembering and no absence needs computing. Where it does not, the design
    is paying enforcement to fight its own shape, and a guard that keeps firing
    on honest work is usually THIS defect wearing an enforcement gap's costume:
    the repair moves the default, never the guard (law 11 from the other side).
    Neither half is minted here — the global corpus carries the pit of success
    under Calibration and the laziest-route question under skill-craft. What is
    local is the measured fact that this repo builds the correct predicate and
    then does not reach for it: three instances in one day, each a site where
    the right thing already existed one import away and the nearest thing won.
    (J28)

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

**WHAT A RUN HOLDING BOTH ANSWERS REPORTS IS DECIDED, AND NOT HERE.**
`exits.worst()` is the single home: could-not-verify OUTRANKS finding,
which outranks clean, and its docstring carries the argument — the caller
most at risk reads `2` as "here is the complete list of what is wrong"
and acts on the list, so `3` withdraws the promise of COMPLETENESS while
every finding still prints in full. Nothing is hidden by the code; only
the claim that the list is whole. This paragraph POINTS rather than
restates, because a second body of that rule is the drift the rule is
about. Read it at the function, and add nothing here that the function
does not say.

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
  `tools/absence-scan.mjs` runs on every push, because this repo is
  where workflow templates extracted from PRIVATE repos will land.
  THE ROUTE IS THE MACHINE-WIDE HOOKS PATH, not this repo's own files:
  `core.hooksPath` points at the dotfiles hooks directory, and a set
  `core.hooksPath` overrides `.git/hooks` entirely — so
  `tools/git-hooks/pre-push` and the `.git/hooks` symlink to it both
  exist and are currently UNREACHABLE. The effect is real and verified;
  the wiring this file used to claim was not the live one. Whether this
  repo should carry its own reachable wiring rather than depend on a
  machine-wide path is finding (i) on the decision round's agenda and is
  deliberately still open.
- **Nothing crosses the seam.** Templates carry no project
  identifiers upward; a repo file declares and never restates
  downward.

## Role files

- `LEDGER.md` — the on-disk ledger: one entry per line, append-only,
  chronological. Facts with their basis, decisions with their why,
  open questions. Read its tail before re-deriving anything that may
  be settled.
- `ITEMS.md` / `ITEMS-DONE.md` — the item carrier and its closure home.
  `lifecycle item add` is the only admission path; the tool is their
  only writer (law 8).
- `BACKLOG.md` — RETIRED 2026-09-12, the legacy-backlog kind taking its
  declared `delete` exit. Every entry had its ITEMS.md successor
  (`lc-1`..`lc-8`): five were dropped as overtaken and three had their
  source body inlined, so nothing needs the file to be read. **Legacy
  `BACKLOG.md:<line>` citations resolve at `5c257ec`** — the deleting
  commit's parent. A line number is only meaningful against a fixed
  blob, so cite that sha and never a live path:
  `git show 5c257ec:BACKLOG.md`.
  MEASURED, not asserted (2026-09-12, peer desk, discharging the
  judgment desk's binding precondition that a pin shows citations
  resolving to the ENTRIES THEY NAME — pinning a drifted file would
  sanction the drift permanently). Blob `4c13ab1`, 86 lines, hash
  verified rather than assumed. All 16 citations across `lc-1`..`lc-8`
  (two per entry) resolve to an entry head at EXACTLY the cited start
  line — offset zero, no drift, because no commit touched `BACKLOG.md`
  after the migration. The check is a CONTENT test, not a form test:
  it grades the cited body's vocabulary against the citing entry's own
  requirement, which is the distinction that flipped dotfiles' first
  desk check from a false 2-of-10 failure to a true 122-of-125 pass.
  Its control discriminates — the same probe against a line nobody
  cites scores 1 where the real target scores 8, so the zero-drift
  result is an instrument reading and not an unread instrument.
  ONE COSMETIC DEFECT, recorded because a silent repair teaches the
  next reader nothing: `lc-8` cites `BACKLOG.md:77-87` and its entry
  occupies 77-86, the file's last line. The END bound overruns by one;
  the head resolves correctly at 77 and the cited body is the whole
  entry, so no resolution changes. Contrast `claude-code-cache-fix`,
  whose equivalent pin FAILED this precondition — 313 of 318 pointers
  landing on the wrong entry, 307 by a constant +80 — and which is on
  the repair path (`cf-328`) rather than the pin path. A line number
  always resolves, so nothing fails when it lies; that is why this is
  measured rather than argued.
- `dev-notes/` — the maintenance layer, never loaded by operational
  files. Its placement outside every operational load path is
  load-bearing and does not move.
- `tools/` — repo-owned checks. `absence-scan.mjs` and `tmpdir.mjs`
  ORIGINATED as copies of claude-code-cache-fix's and ARE edited here:
  measured, `absence-scan.mjs` carries 6 commits in this repo and
  `tmpdir.mjs` one. Byte-identity with that repo's copies still holds
  for `absence-scan.mjs` — the copies have been kept in step by hand,
  which is a fact about diligence and not a property of the files.
  The de-duplication is a later wave's act with the hook rewiring in
  the same change. Two copies for one wave is the deliberate cost.
- `test/` — `absence-scan.test.mjs` ALSO originated as a copy AND HAS
  DIVERGED: 4 commits here, and `cmp` against cache-fix's copy differs
  today. `7fe9e68` is one of them — it repaired a scope guard that
  described another repo, so the UUID bite had never run. THE
  CONSEQUENCE IS THE POINT AND IS WHY THIS IS NOT BOOKKEEPING: a fix
  landing in one copy no longer reaches the other, silently, and
  neither side has a check that would say so. The `test_*.py` files
  are this repo's own.
  **These two lines previously read "byte-identical copies … not
  edited here", which was false in both directions at once** — the
  files ARE edited here, and the test copy is no longer identical. A
  role line asserting a property of files nothing measures is the
  label-over-body class in the section that tells a reader what to
  trust.
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
python3 -m unittest discover -s test -p 'test_*.py'        # the CLI
python3 plugin/cli/lifecycle --test                        # roster + coverage + ROUTE SETS
python3 tools/prove-rows.py                                # every row, red-first
python3 plugin/cli/lifecycle audit                         # the walk, read-only: growth,
                                                           # the laws scope audit, the
                                                           # judgment register's fire-rate
node --test test/absence-scan.test.mjs                     # the leak scan's bites
node tools/absence-scan.mjs --git-range ..HEAD             # the leak scan itself
```

`lifecycle --test` runs every roster row's plant AND control and prints
full counts including skips, then runs the EMIT-SITE COVERAGE check: every
site in the source that emits a FINDING maps to a registered row, or
`--test` fails. `--test --list` prints the roster as data — design §3.9's
table is a SNAPSHOT of that list and updates from it, never the reverse.

**Then it runs the ROUTE-SET check, which catches what a green row cannot.**
Beside its firing input a row states the ROUTE SET its refusal's own TEXT
names — a closed vocabulary read from the design's side — and the routes the
CODE watches are derived from the source. A row whose text names an effect
WIDER than its routes fails, even though its plant and control both pass:
`dangling_reference` said "typed reference" while the resolver reached
`lane:` alone, so five of the six types could point at nothing and the roster
stayed green. **THE MIRROR FAILS TOO, since lc-30**: a row whose text is
NARROWER than what the code routes through it fires
`FINDING [route_set_unnamed]`, where it once printed a note and contributed
CLEAN. The two are separate refusals with OPPOSITE repairs — widen the code
versus widen the text — and they are deliberately not one row with two
firing inputs, because an operator told only "these disagree" cannot tell
which repair is owed. A green row and a covered refusal are different claims, and the
two sides of this comparison are read independently or it compares a claim
against itself.

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

**A NEW ARRANGEMENT IS ADMITTED ON A PAIR, not on a PROVEN** (lc-142,
2026-09-15). `PROVEN` is also what an arrangement prints when it could
never have gone red — an anchor pointing at something the mutation cannot
reach reads identically to one that works. So a newly recorded arrangement
runs TWICE: at its real anchor, which must give `rows changed: <the row>`;
and re-pointed at an INERT anchor (a comment line), which must give
`rows changed: NONE` and FAIL with "the row did NOT change". Both quoted.
The cost is one extra run of a single ident, not a full walk, and without
it the first run's PROVEN is an unread instrument. Related but distinct
from the sibling question below: that one asks whether a mutation darkens
too MANY rows, this one whether it darkens any at all.

**ADDING A ROW CAN RETIRE A NEIGHBOUR'S PROOF, and only prove-rows says
so** (lc-30, 2026-09-15, measured not predicted). Where a check emits
SEVERAL findings off ONE comparison, a mutation on the COMPARISON proves
none of them. `route_set_unwatched`'s recorded mutation was
`full = set(row.route_set)` → `full = set(watched)`, a correct proof while
the mirror direction was only a NOTE; the moment lc-30 made that mirror a
FINDING, the same mutation emptied BOTH difference sets and darkened two
rows proving two different refusals — prove-rows answered
`[route_set_unwatched] FAILED … This mutation removed adjacent machinery,
so it proves nothing about any one row`, exit 2. The repair is not a
fallback but SCOPING: each direction takes the same-parentage mutation
narrowed to itself, leaving the other direction reading real input. So a
new row whose verdict is computed from an expression an EXISTING
arrangement mutates RE-CHECKS that arrangement before anyone claims
prove-rows green — the existing row's FIRING is untouched either way, and
it is its PROOF that silently retires.

**The verdict it compares is the exit code AND the row name in the output.**
Codes alone do not discriminate here: every finding is a `2`, so a guard
removed at one site while a shared one catches the same input under a
different row's name reads as "unchanged" and the row reads as unproven.

**All 62 node bites pass here, and this paragraph used to say one of
them could not** — corrected in place 2026-09-18 because a reader who
stops at the first version treats a real red as expected. `source:
every UUID in a tracked SOURCE_SCANNABLE file is on the synthetic
allowlist` guards itself against a silent scope collapse, and its
anchors named claude-code-cache-fix's tree (`proxy/`, `BACKLOG.md`,
more than 500 files) rather than this one. This file recorded that as
a permanent COULD NOT VERIFY. It was neither permanent nor confined
to the guard: those three assertions run BEFORE the UUID scan, so the
scan they protect had never executed once — a scope guard collapsing
the very test it guards, which is the check-that-fires-on-a-non-defect
class pointed at its own subject. `7fe9e68` derives the roots and the
floor from the scanner's own predicates over `git ls-files`; the bite
has run green since, and that test's own duration moved 1.4ms → 14.9ms
— the cost of the scan it had been dying in front of, which is how one
tells a body that RUNS from one that merely stopped failing.
MEASURED 2026-09-18: 62 pass, 0 fail, 0 skipped. A red here is now a
defect, and nothing in this file says otherwise.

## Carve-outs

**Pushing this repo is standing-authorized (operator, 2026-08-28).**
Their words, first-hand, in answer to a held wave-5 push: *"push, an
doyu can always push"*. So `main` here is commit-and-push like
dotfiles: claim the log as its own command, push as its own command,
no round trip to ask.

Why this heading exists at all: the corpus floor treats a push to a
PUBLIC repo as an outward act needing authorization, and "no
`## Carve-outs` heading" means the floor applies unchanged. This repo
went public on 2026-08-27 (`70bc93c` "Publication bar green: one real
leak fixed, one guard over-fire repaired", remote added minutes
later), and until this line was written every session had to stop and
ask. Wave 5 held 16 commits for exactly that reason. Recording the
answer is what stops the next session paying that toll.

Scope, stated so it is not over-read later: this authorizes the PUSH
to `origin/main`. It is not a licence for the other outward acts —
publishing a marketplace entry, a release, or anything under the
operator's accounts stays theirs. The mechanical guards still bind
and are not softened by this heading: the pre-push leak scan runs,
the full suite runs, and a marked subagent commit whose sha sits in
no record carrier is BOOKED before the push, never waved through with
`PUSH_UNBOOKED_SUBAGENT_OK`.

Superseded by this section: the ledger's 2026-08-26 line "**No
remote, and none is to be created** — publishing a new public repo is
the operator's act". The operator performed that act; the decision it
reserved has been made. See the ledger's 2026-08-28 superseding entry.
