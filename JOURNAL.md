# lifecycle — JOURNAL

Dated incidents and the lesson each one bought. **A law without a journal
pointer has no basis; a journal entry nothing cites is stale by
change-coupling.** Laws live in `CLAUDE.md` and cite entries here by number;
incidents never go inline beside a law, because a law is what binds and an
incident is why, and inlining the why is what makes a laws file unreadable.

Kind: `journal entries` · home: this file · writer: session · reader: the law
or workflow that cites it · staleness: change-coupling (the artifact it is
about moved past the entry) · exit: never-delete · growth: unbounded, declared
— this is history and it accumulates by design.

---

## 2026-08-26 — the founding day

Every law in `CLAUDE.md` was earned on this date, across four dispatches of
the carrier-rework arc (W1a stages 1–3, W1b stages 4–6, W1c stages 7–9, plus
two sonnet lanes in the parent repo). The entries below are grouped by the law
they justify. Where an incident was suffered by the desk rather than a lane,
it says so — those are the ones most worth keeping.

### J1 — cited by law 1 (three answers)

The design described this repo's census ancestor as three-answer: open,
closed, unknown-with-counts. The tool it cites as its parent carries a
**fourth** element the description omits — an explicit could-not-verify when
the closure home cannot be read, with the done count then being the main
text's count alone rather than the true closed population. The tool's own
docstring records why both other answers are wrong: a structurally-zero closed
count leaves the retirement trigger stuck ON (it demanded a pass from a session
that had just completed one), and an unresolvable home leaves it stuck OFF as
a sink. **A trigger nobody can clear carries no information and trains the
override reflex.** The design's sentence was the drift, and the part it dropped
was the safety-relevant one.

### J2 — cited by laws 2 and 3 (a registry row per refusal; the registry is the source)

Three separate instances in one day, each found by a different mechanism:

- **W1a**: the design's refusal table named a firing input — a planted foreign
  path — that the leak scanner had no class for. The row could not go red as
  written. Labelled PROSE-REST carrying the measurement rather than amended to
  a token the scanner *did* catch, which would have greened the roster about
  the exact leak direction the guard exists for.
- **W1b**: eleven refusals existed that the design's table never listed — two
  structural, nine required by prose elsewhere. The table predated the verbs.
- **W1c**: the emit-site coverage check, on its **first run**, found six
  refusals the code already emitted under no registered row at all
  (`unknown_item`, `unknown_source`, `new_without_typed_blocker`,
  `move_uncommitted`, `ledger_shape`, `unregistered_kind`). None was wrong;
  each was unproven, and the roster's green had been saying nothing about them.

The yield of a coverage check over emit sites is not new bugs — it is
**unproven behaviour**.

### J3 — cited by law 3 (a scan reads its own documentation as data)

The coverage scan's first run reported a row called `name`, read out of three
doc-comment lines describing the patterns it matches. The fix was to reword the
comments, **not** to exempt the file: an exemption sized to "this file is the
instrument" removes the instrument's own output from the instrument's reach.

### J4 — cited by law 4 (a module-load red is not a discriminating red)

Two instances, one in each direction:

- A lane reverted a whole scanner file to produce its red arm and got
  `does not provide an export named 'HOME_PATH'` — a load failure. It
  recognised it as non-discriminating, restored, and re-built the arm by
  mutating only the predicate so the module still imported and ran.
- W1c removed a could-not-verify branch and the next line did arithmetic on
  `None`, producing a `TypeError`. The right mutation folded could-not-verify
  **into** clean — one token, and the output is a wrong VERDICT rather than a
  crash.

### J5 — cited by law 5 (a borrowed instrument needs its own pair) — DESK INCIDENT

The desk wrote a verifier row asserting `git check-ignore -v <path>` must exit
non-zero. Two compounding errors: `-v` changes the exit **semantics**, not just
the output (without it `0` means ignored; with it `0` means "some pattern
matched", which a negation satisfies too), and `check-ignore` **skips tracked
paths** unless `--no-index`. The declaration is tracked from the moment stage 9
commits, so the check would have exited "pass" whether or not the negation
existed. **Not an unproven check — an unprovable one.** Measured in a scratch
repo in all four states before the row was rewritten. The durable form is
`--no-index`, no `-v`, exit 1 required.

The same defect then turned up one layer down in shipped code: a lane's own
`ignored_by_git()` omitted `--no-index` **and carried a docstring paragraph
justifying the omission**. The prose read as careful and is what stopped anyone
testing it. The fix deleted the justification along with the flag change.

### J6 — cited by law 6 (no hardcoded machine paths)

The publication bar of the parent repo claimed its leak scanner enforced a
foreign-path class. It had none: a planted `/home/<other>/…` path scanned clean
while a capture token in the same file fired, so the zero discriminated. Four
of the bar's five listed items were real; that one had never existed, and what
established the clean result was a person hand-classifying 3,012 strings, once.
When the class was finally built, both boundaries — repo root and XDG roots —
were derived at run time, because **hardcoding a machine path into a public
repo's leak scanner is the hazard it is scanning for.**

### J7 — cited by law 7 (the leak scan armed before the first commit)

Armed as this repo's pre-push hook before its own first commit. Later exercised
end to end by the desk in a throwaway clone with a `file://` remote: clean tree
→ push allowed; planted capture token → push blocked, finding named. One limit
recorded with it: the machine-wide dispatcher's scan blocked first, so the
repo's own chained hook did not get its turn in that arm. A leak is provably
stopped; which layer stops it is not separated.

### J8 — cited by laws 8, 9 and 14 (one writer, the two-file move, the schema floor)

The interrupted-move test makes `Path.write_text` raise midway through a real
close, so what is on disk is what a genuine crash leaves. Premise pinned first
(the id present in BOTH files), then the check reports DUPLICATE, recoverable,
"never loss", and names which copy to delete. Control: the same repo,
uninterrupted, reports move integrity CLEAN. **Review missed a defect this test
found** — conservation reported "a body left the carrier — a hand deletion"
over a SURPLUS, which is the interrupted move and recoverable, beside a
DUPLICATE line saying the opposite. A check whose message names a CAUSE must
branch wherever the cause does.

### J9 — cited by law 10 (READY is judged, never derived) — DESK INCIDENT

The desk booked two entries as READY. That took the declared READY head to 12
against a cap of 10, and the pre-push guard refused the push. The repair was to
regrade both entries to RECORD — correct, and taken in good faith. **The cap
fought the GRADING rather than the growth.** A capped label is escaped by
relabelling, which is precisely what happened. This incident is cited in the
parent design as part of the evidence for dropping caps entirely: growth is now
controlled by flow — a kind that grew without an exit event — which cannot be
escaped that way.

### J10 — cited by laws 11 and 12 (a guard on legitimate work; versions climb)

The machine's pre-commit blocks a plugin payload change without a version bump.
Its premise is an installed copy that could go stale — false for a
never-released plugin with no remote, so it over-fires here. The lane bumped
rather than taking `--no-verify`, because the bypass **disables every lane in
the hook rather than the one that fired**, and that is how a guard trains the
override reflex that eventually kills it. Versions climbed 0.1.0 → 0.1.6 across
the wave; the guard's false premise is booked as a separate item.

### J11 — cited by law 17 (reports are booked from the file) — DESK INCIDENT

Verifying the migration, the desk's first counts said the archive held 2 bodies
against the lane's 273, and 19 unclassified against 18. **Both were the desk's
own patterns** — `^## ` matches section headings rather than bodies, and the
other grep counted a table header and a rule sentence. Reading the files' actual
shape before counting is what resolved it. Had those numbers been sent, a
working migration would have been reported as broken. **A discrepancy between
your count and a lane's report is a claim about your instrument first.**

### J12 — cited by law 18 (a brief is complete at dispatch) — DESK INCIDENT

The desk wrote "COMPLETE AT DISPATCH, no mid-flight correction assumed" into a
brief and then amended that brief in place three times while the lane worked.
Those cannot both be true: an amended brief is a live document, a
complete-at-dispatch brief is a frozen one, and the desk shipped the frozen
promise while treating the file as live. All three accompanying messages
arrived **hours late** — after the work and after the report. The lane found
the reversal only because it re-read HEAD before committing into a shared public
repo, and it later corrected the credit it was given: that was a **write-safety**
habit, not a reading discipline. Keyed to "before each commit" the rule fires
only for lanes that commit into a shared tree; keyed to **"before each verifier
run"** it fires in every lane and fires earlier.

### J13 — cited by law 19 (an unverified negative that agrees with a suspicion) — DESK INCIDENT

Twice in one day, in opposite directions, both shipped to the judgment desk as
fact. A lane's report said its inbox was empty; the desk read that as a live
measurement and reported a channel failure that had not happened. Hours later
the desk read the same kind of line in another lane's report and reported
message **loss** — inside a message written specifically to correct the first
error. Both times the line was true **when composed** and stale when read. The
cure was one message to a session that was still live, and it was not spent —
twice. A negative that confirms what you already believe is exactly where the
free probe is owed and exactly where it feels unnecessary.

### J14 — cited by law 20 (what a push carried is settled at the remote) — DESK INCIDENT

A desk push was refused: the remote was already at the commit being pushed,
because a peer's push had carried it. Nothing was lost, but the local view had
been wrong about what was published. Separately, a push was refused for
carrying a subagent's commit with no booking behind it — a correct fire, repaired
by writing the booking rather than by taking the offered override.

### J15 — cited by law 21 (a lane reports defects in its own shipped code)

W1a found, after its report and after its write grant ended, that its shipped
`ignored_by_git()` reported a clean board over exactly the misconfiguration it
existed to catch. It **reported rather than edited**, and the fix led the next
dispatch as item 0. W1c did the same for a gap in its own annotation work.

### J16 — cited by law 22 (an unfalsifiable check is deleted, not registered)

W1c built a `migration_reconciliation` guard over a partition that is exact by
construction — every entry is either written or reported unclassified, so no
input could falsify it. Registering it would have put a permanently-green row
in a roster whose entire contract is that rows go red. It was **deleted**; the
arithmetic is still computed and reported as could-not-verify on the run's own
counts, carrying no row ident, so the coverage check stays honest without a
fake row.

The same lane found the same shape a second time in the same dispatch: the
design's replacement row "a kind grew without an exit event" names
`lifecycle retire` as its firing input, and that verb exists in no stage.
**A row whose firing input does not exist cannot be red-proven.**

### J17 — a control going red is a finding about the CODE

`new_without_typed_blocker`'s control fired a different refusal, which revealed
that an add missing a slot entirely never reaches the typed-blocker check — the
empty-slot refusal catches it first. The only input that reaches the intended
row is the migration's own `UNKNOWN` marker. That would not have been found by
reading, and the row would have been proving something other than its name.
Cited by law 2: **a roster asserting only its plants ships green.**

### J18 — a fixture shared by many rows is a dependency surface

A baseline fixture shared three requirement tokens with the seed items, so the
intake join fired inside controls meant to be quiet and one row's CONTROL went
red. The red indicted the FIXTURE, not the verdict — and only the pair's
"control must DIFFER" assertion surfaced it.

### J20 — cited by laws 23 and 24 (a named thing has a home; a named verb has a wave)

Two instances one day apart, and the second was found by the first's own rule.

- **A refusal named in prose with no firing input cannot be red-proven.** The
  design's replacement row "a kind grew without an exit event" named
  `lifecycle retire` as the input; that verb existed in no stage list, so the
  row could only have entered the roster as an UNPROVABLE one — the shape law
  22 had removed two hours earlier in the same dispatch, twice in one lane.
- **A rule named in prose with no home is a rule nobody applies.** The brief
  for this wave said "laws 23–25 are yours to honour and they are new" while
  the laws file carried 22 and the three existed only in the design document.
  Law 23 is itself the rule that a named thing has its home — so the brief
  instructed a session to honour a law that had no home, which is the defect
  the law describes, in the instruction that describes it.

The pair is one class from two sides: **naming a thing is not placing it.** A
verb has a wave, a refusal has its firing input, a law has its file, and a
kind has its home — each explicit, never a default the tool assumes.

### J21 — cited by law 25 (every schema change ships its migration)

The growth-control change (`bound` -> the closed vocabulary, `ready-cap`
removed) is a SCHEMA change with every declaration as a dependent, and it
arrived on a dispatch that had already committed a declaration under the old
stage. Two things followed and only one was obvious. The obvious one: the
migration has to run over both the schema and the artifact that schema
produced. The other one is the reason it is a law rather than a note — the
cheapest moment is NOW and it gets more expensive monotonically, because
exactly one declaration existed the day the change was designed and two exist
the day after.

The wave also measured what a migration must refuse to do. Running
`--schema-from` over both real declarations, every mechanical transform
applied and every one that needed a JUDGMENT — which reference type a prose
reader was, whether a public repo runs the source-scope leak class — came
back UNCLASSIFIED and BLOCKED THE APPLY for that repo. A migration that had
guessed those would have written a declaration nobody made, and it would read
afterwards exactly like a declaration somebody did.

### J19 — running the rule is not reading the rule

The migration's first real run turned two entries from a `## Grades` section —
entries that DESCRIBE the old grade words — into work items. The rule cutting
that section was in a file the lane had already read. **Reading a rule list and
applying it are different acts, and only the second is checkable.**

**UNCITED — no law in `CLAUDE.md` cites this entry.** Checked against all 25
laws: none states "reading a rule and applying it are different acts" or
this entry's specific migration-shape lesson. Recorded here rather than
attached to the nearest-sounding law (law 25, the schema-migration law,
covers a different requirement — that a migration ships with its dry run —
and would misrepresent this entry's own lesson as that law's basis). Per
this file's own rule, "a journal entry nothing cites is stale by
change-coupling": this one is stale until either a new law is earned from
it or a session finds an existing law it genuinely supports.

### J22 — cited by law 24 (an item that will name a refusal reaches refusals.py)

Drain wave 1, 2026-09-15. THREE firings in ONE wave of a single shape: an
item whose done-criterion emits a NEW finding, dispatched with a write set
that cannot reach `plugin/cli/lifecycle_core/refusals.py`, where law 2 says
every refusal is a registry row with its firing input.

The firings, each measured rather than argued:

- **lc-31 shipped the defect.** Its write set was `cli.py` +
  `test/test_migrate.py`. The lane built the refusal correctly, emitted
  `FINDING [migrate_repeated_from]` at `cli.py:838`, had nowhere to declare
  the row, and reported the gap rather than reaching outside its box or
  dropping the bracket tag that would have silenced the coverage scanner.
  The repo went red: `lifecycle --test` 84 of 85, `emit_site_unregistered`.
  A sibling lane bisected it over ten commits — clean at the parent, red at
  `c7c6f74` — rather than inferring the boundary. A second dispatch
  registered the row (`bc35cea`); the item closed at two commits and two
  lanes for what was one item's work.

- **lc-30 could not be built at all.** Same shape, caught BEFORE shipping:
  the lane implemented the fix inside the declared boundary in a private
  clone and `lifecycle --test` answered `FINDING [emit_site_unregistered]
  ... route_set_unnamed: emitted at roster.py:184`. It halted at the write
  boundary and returned the decision, having rejected three escapes by name
  — reusing a row whose text means the OPPOSITE case (which would hand the
  operator a wrong cause, verbatim the defect lc-30 exists to remove),
  emitting a finding with no bracketed row name (evading the scanner's
  regex while violating the law it enforces), and `--no-verify`.

- **The third is older and is recorded in lc-30's own evidence**, in the
  dispatching desk's own words: "lane A routed two NEW ambiguous-closure
  shapes through `migration_unclassified` because refusals.py was outside
  its write set (my brief defect)".

THE CARRIER ALREADY KNEW THE SHAPE. `lc-134` names `refusals.py` in its
write set for exactly this reason, and `lc-34`'s amend-reason records a
previous drain desk running the check across a cohort: "lc-33 and lc-68 DID
need their write-sets widened for a roster row and this one does NOT". So
the question is standard at this repo's dispatch join, and three briefs in
one wave still failed to ask it. That is what makes this a law rather than
an incident: the knowledge existed and did not reach the composing moment.

MECHANISM, stated so the rule is checkable where it is reused: this is the
dispatch discipline's realization-surfaces rule — a write boundary is
complete only once each commissioned change is resolved to the file that
REALIZES it — instantiated for one repo. A refusal's realizing file is
`refusals.py`, always, because law 2 puts it there.

PROSE, NOT A PREDICATE, deliberately. "The criterion emits a NEW finding"
is judgment-shaped: a lint keyed on the criterion's text would fire on
entries that merely DISCUSS findings and stay silent on one that emits
without saying so, which is the over- and under-firing the mechanism bar
forbids. The computable slice already exists and is downstream — the
emit-site coverage check fails `--test` — and this law's whole purpose is
to move the catch UPSTREAM of the commit, where a human is composing.

Judgment-desk GO 2026-09-15 (dotfiles-89), home ruled to this repo's own
project file rather than the global corpus or the dispatch skill: the
general rule lives there already; this is its one-repo instantiation.

### J23 — cited by law 8 (the tool is the carrier's reader too)

Drain wave 1, 2026-09-15. A desk composed four lane briefs by reading item
bodies through a hand-rolled block extractor that truncated at ~1600
characters. Amendment slots sit at the END of a block by construction, and
the bodies ran to 2253, 2785, 3242 and 3423 characters, so the reads dropped
exactly the lines that supersede. THREE Background passages shipped stale:

- lc-132's brief cited two `stderr` emit sites, both FALSE — the item's own
  `amended-evidence` had already re-measured on the EMIT FUNCTION rather
  than the token and found 98 `out()` against exactly ONE `err()`.
- lc-133's brief commissioned a red for a `try/finally` half already live at
  `prove-rows.py:790-798`; the item's amended criterion had narrowed to the
  startup refusal alone.
- lc-30's brief commissioned a red-first on a live instance the item's own
  amended-evidence records as SPENT.

Two lanes caught one each in their critique pass, BEFORE their first build
call, and built against the item body rather than the brief. The desk then
swept all eleven wave and held items rather than repairing only the two
reported instances, and found a fourth (lc-51) that no lane had reached yet.

THE REPO ALREADY HAD THE RIGHT INSTRUMENT AND NOTHING POINTED AT IT. The
desk was about to book this as a MISSING VERB, ran `item slots lc-132`
before claiming the absence, and found the verb exists AND had already
resolved the amendment — its `evidence:` line printed the corrected text,
not the original. So the gap was discoverability, not capability, and the
booking changed shape before it was written.

BOTH READS ARE NEEDED, WHICH IS WHY THE LAW NAMES TWO. `item slots <id>`
emits the slots with amendments RESOLVED — the current truth — and emits
ZERO `amend-reason` lines. But the reasoning lives there: lc-47's
deadlock-dissolution (an evidence blocker whose truth is produced by the
very change it gates is not a blocker, it is a coupling) exists ONLY in an
`amend-reason`, and so does lc-34's record of a previous desk running the
refusals.py write-set check across a cohort — a precedent that would have
prevented three lanes of wave-1 rework had anyone read it. Measured
2026-09-15: `item slots lc-34 | grep` for that sentence returns nothing; the
raw block carries it.

PROSE-REST, and the law says so rather than pretending otherwise: no
computable predicate distinguishes a hand-rolled read of a carrier from any
other file read. There is nothing to hook. The cheap detector is the one
that actually fired here — an executing lane opening the item body the brief
summarised — which is a reason to keep commissioning the critique pass, not
a reason to believe a lint could replace it.

### J24 — cited by law 17 (a rendering is a view over a result object)

Drain waves 1 and 2, 2026-09-15. THREE instances in one day across TWO
parties of a single shape: a claim about WHICH test did what, read off a
console rendering instead of the runner's result object.

The mechanism, and it is specific to `unittest -v`: the runner prints a
test's NAME line and then, for the NEXT test, its DOCSTRING first line
followed by the status. So a name and a status that belong to DIFFERENT
tests sit on adjacent lines, and reading them as a pair attributes the
status to the wrong test.

- A wave-1 lane reported the battery's one skip by its DOCSTRING.
- A second wave-1 lane reported it by a neighbouring test NAME.
- The desk "resolved" the apparent disagreement by declaring them one test
  seen through two namespaces, and shipped that resolution into two lane
  messages and a live brief. They were two different tests.
- A wave-2 lane then reproduced the desk's error independently, from the
  brief, by the same adjacency.

The truth, read from the parsed result: the skipping test is
`test_verbs.LedgerStorableBlocker.test_the_67_REPAIRED_dotfiles_TEXTS_all_pass_and_the_OLD_ONES_do_not`,
skipped because the arm grades real texts in a sibling checkout that is
absent from a clone. Nobody's original quotation was a lie; the PAIRING was
an artefact of the rendering.

THE INSTRUMENT:

    res = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    for t, why in res.skipped: print(t.id(), why)

`t.id()` is the structure. The console is a view over it, and the view puts
unrelated rows side by side.

WIDER THAN SKIPS, which is why this is a law pointer and not a brief
paragraph: the same day, the desk counted failures in a node battery by
`grep -c` over a DIFF, where context lines and changed lines render alike —
the count said a class was touched when the only mention was context.
Filtering on the diff marker answered it. Any two-column rendering read by
eye has this property where the structure is available parsed.

The law it extends already carried the other half: a discrepancy between
your count and a lane's is a claim about YOUR instrument first. That clause
is what sent the desk to reproduce a lane's ARRANGEMENT rather than correct
its number — and the arrangement was the finding twice: once here, and once
when the same desk ran a mutating tool in the clone it was testing in, and
read three failures that were its own doing.

### J25 — cited by law 24 (a new verb has four realizing surfaces)

Drain waves 1-3, 2026-09-15. FIVE instances in three waves of ONE desk
failure: a write boundary that cannot reach the file which REALIZES the
commissioned change. The dispatch discipline states the general rule — a
boundary is complete only once each change is resolved to its realizing
file. Law 24 was minted from the first two instances and names ONE such
file, `refusals.py`, for one kind of change. The desk then checked law 24,
found it satisfied, and treated the boundary as answered — four more times.

  1. lc-31  — refusal shipped unregistered; repo went red, second lane.
  2. lc-30  — could not be built inside its boundary at all.
  3. lc-47/lc-58 — the VERB's surface (cli.py) and the record's kind.
  4. lc-148 — the ALLOCATOR's call sites; the ruled design's write was in
     verbs.py and migrate.py, neither in the item's set.
  5. lc-120 — the verb's WIRING and its SLOT VOCABULARY; the lane halted
     with nothing written and both halves measured.

THE GENERALISATION, from the lc-120 lane, which is what makes this a law
rather than a fifth incident: **a NEW VERB has FOUR realizing surfaces by
construction** — its BODY (`verbs.py`), its WIRING (`cli.py`: the
subparser, the action tuple, the `_carrier_verb` branch), any SLOT
VOCABULARY it writes (`items.py`, where acceptance is decided), and its
REFUSAL (`refusals.py`). lc-120's booked write set carried one of the four.

FOUND PROSPECTIVELY, which is the part worth keeping: that lane then swept
the live carrier for siblings and found lc-131 — "a dedicated clearance
verb", write set `verbs.py, refusals.py, test/test_items.py`, the same
three files and the same missing wiring, waiting to halt a future lane.
THE SWEEP CARRIED ITS OWN CONTROL: 5 candidates matched, 2 were real
members, 1 already correct (lc-107 carries cli.py), 2 were false positives
(lc-41 adds no verb — it makes EXISTING verbs commit). The instrument
over-fires, so each hit's PARSED write-set was read rather than the regex
trusted. A sweep whose hits are all members has usually not been controlled.

PROSE, NOT A PREDICATE, and the lane judged this before the desk did:
"does this criterion propose a new verb" has no computable predicate, and a
guard over item prose would fire on legitimate work — law 11. The
computable slice already exists downstream (the emit-site coverage check
fails `--test` for an unregistered refusal); everything upstream of the
commit is booking discipline.

### J26 — cited by law 24 (a change resolves to what realizes it AND what must move with it)

LAW 24 HAD BEEN WIDENED TWICE BY ENUMERATION — first "a refusal realizes in
`refusals.py`", then "a new verb has FOUR realizing surfaces" — and each
widening was driven by counting cases the previous wording missed. A rule that
needs another round every time a lane finds a surface nobody enumerated is
stated at the wrong altitude. This is the round that stopped counting.

THE MEASUREMENT THAT FORCED IT, from lc-120. Its grant covered all four
realizing surfaces. `lifecycle --test` was CLEAN at 89 rows, the verb worked
end to end in a scratch repo, every surface satisfied — and the whole battery
still went red on a seventh file: `test/test_verbs.py`, whose DESTINATIONS
table derives `cli.py`'s action tuple from source and grades a hand-written
expectation against it. That file REALIZES nothing; the verb runs correctly
without it. It DEPENDS, and it says so loudly the moment the tuple grows.
Cost: one halt, one round trip, one grant, with the work already built and
green.

SO THE PREDICATE TAKES BOTH HALVES, and neither is new. REALIZES is the
dispatch skill's realization-surfaces rule; MUST-MOVE-WITH is the global
corpus's dependents rule, which already demands the dependents search ride the
change. The law's job here is to say that a `write-set:` slot IS that search,
performed at booking time. Realizes is the subset; the difference between the
two is where every measured halt has sat.

THE INCIDENT IS NOT AN ARGUMENT AGAINST THE TABLE, and the framing matters
enough to record. A hand expectation graded against a derived source is the
anchor rule's good form: it fails LOUDLY on growth, which is why this gap
surfaced as one red rather than as silent drift. Deriving that table to keep
boundaries quiet would trade a loud red for permanent blindness — the
restated-enumeration defect the same lane repaired one file over, where a
hardcoded `["closed-reason", "closed-ref"]` had been asserted against the very
vocabulary it graded.

WHAT IS DELIBERATELY NOT FOLDED IN. Lane 1 reported a different fifth
surface — "which ARRANGEMENT grades this predicate", where widening a gate
invalidates another row's control. That is read-or-execute overlap between
agents, booked as lc-139's instrument-coupling class. Two questions, two rules;
one sentence covering both would cover neither.

THE GRADE ON THE NEW HALF, carried from the lane that measured it: ONE
instance, ONE measurement. The lane declined to call it a class and that grade
travels with the law. The computable slice is per-shape and booked as lc-154 —
for a source-derivable enumeration, the files that derive and grade it are
greppable before a lane is briefed. Nothing wider is claimed: a general
dependents checker over item prose is judgment-shaped and would fire on
legitimate work (law 11).

### J27 — cited by law 26 (a prose claim beside a mechanism is held by nothing)

2026-09-18. FOUR INSTANCES IN ONE DAY, one class, found by four different
routes and none of them by a check. The class: the stack HELD the thing, and
the thing was not retrieved at the moment it applied.

1. **A structural fact, one query away, derived instead across a day.**
   `.claude/lifecycle.json` at `9a1eded` — yesterday's HEAD — declared 21 kinds
   split 4 verb-written / 16 `writer: session` / 1 producer. That split is the
   discriminator between a kind that self-administers and one that drifts, and
   it is what the arc's section 2b spent an afternoon arriving at by reasoning.
   Found by the operator asking whether the session had wasted time on the axis
   it was fixing.

2. **A design re-inventing a pattern the repo had already proven.** Mechanism 2
   ("state-advancing acts write") is the verb-writer pattern, working on 4 of
   22 kinds. Found by the begehung's second round, whose registered lens was
   the operator's own naming of the existing carriers; recorded as that round's
   class.

3. **A document written SIX HOURS EARLIER BY THE SAME SESSION, not reached.**
   Asked to mechanize a duty whose firing moment is a non-event, the desk
   declared detection uncomputable and designed a printed readout.
   `docs/required-slots-as-an-autonomy-lever.md` (`d57e02b`, that same morning,
   at the operator's direction) carries the escape verbatim — require a WRITE
   at the moment of deciding; the slot's presence is computable, the fill's
   quality is judgment. Found by the operator: *"didn't we not too long ago
   find a solution for this class?"*

   THIS IS THE INSTANCE THAT SETS THE SCOPE. There was no session boundary to
   cross. The context that failed to retrieve the document is the context that
   wrote it, so the failure is not ignorance of the carrier and cannot be
   repaired by announcing carriers harder. **Retrieval fails at moments of
   APPLICATION; the session boundary is only the most visible of them.**

4. **The laws file trained its own readers to discount a red, for a month.**
   `## Verify` stated that one of 51 node bites "structurally cannot pass in
   this repo" and told the reader to expect it. Measured 2026-09-18: 62 pass,
   0 fail, 0 skipped — `7fe9e68` had repaired it in August by deriving the
   guard's roots from `git ls-files`, and this file never moved with it. The
   bite exists to catch a silent scope collapse, which is precisely the alarm
   the stale sentence taught readers to ignore. Found by a peer desk running
   the block and reading the output against the prose beside it.

**WHY NO MECHANISM CAUGHT (4), AND IT GENERALISES.** `lifecycle verify` —
shipped the same day, `e7c4a9a` — parses the `## Verify` fenced block and
EXECUTES its commands, asserting EXECUTED against REGISTERED. The stale claim
was not a command. It was prose BESIDE the fence asserting an expected OUTCOME
of one, and the verb holds no expectation about it. So the mechanism ran
correctly, reported correctly, and the false sentence sat two lines above its
output for a month. A claim in prose beside a mechanism is held by nothing —
and it inherits the mechanism's authority to every reader, which is what makes
it worse than an unsupported claim standing alone.

**THE ASYMMETRY THAT MAKES THIS A LAW RATHER THAN AN OBSERVATION.** A declared
expectation that goes stale in the FAILING direction is loud: the command goes
red and somebody looks. In the PASSING direction it is silent and it degrades
the instrument — the reader is trained that a red here is expected, so the one
real red arrives pre-discounted. The check does not break; it stops being
believed. The cheap instrument across the class is the assertion on what must
NOT appear, which catches a check DEGRADING where a presence-assertion catches
only one breaking.

**THE COMPUTABLE SLICE, booked as lc-176:** an expectation about a registered
verify command is declared in a form the verb CHECKS (an expected pass/fail
count, or a named known-failure the verb asserts is still failing), so a bite
that starts passing makes the declared expectation WRONG and the verb says so.
RED-FIRST is available and is instance 4 itself: declare one expected failure,
run the block, get zero, and the verb must go red. The judgment remainder stays
prose — whether an expectation is the RIGHT one is not computable, and a guard
over that would fire on legitimate work (law 11).

**WHAT IS DELIBERATELY NOT CLAIMED.** Instance 3's own candidate seam — that
the moment a session declares something *uncomputable* or *not mechanizable* is
a retrieval seam, because it is a claim about what solutions exist made from
memory — is ONE instance, unprobed, and is recorded in the design note as a
candidate rather than booked. One occurrence is not a class, which is the same
grade J26's new half carries.

### J28 — cited by law 26 (the default comes before the writing question)

**2026-09-18. THREE SITES IN ONE DAY WHERE THE CORRECT PREDICATE ALREADY
EXISTED IN THIS REPO AND THE NEAREST ONE WON.** Not three defects of one
author's carelessness — three instances of a route being shorter than the
right thing, which is a property of the design and not of the writer.

**1. `lane new` against `desk state`.** Both turn a caller-supplied string
into a filename. `desk.py:69` folds it — `_UNSAFE_FOR_FILENAME.sub('_',
desk_id)` — and `desk.py:56-58` names the hazard in its own words: *"a `/`
in it would otherwise let a caller's id escape this directory."*
`lanes.py:cmd_lane_new` writes `lanes_dir / f"{door}.md"` raw. Executed,
control first: `goodlane` → `lanes/goodlane.md`, exit 0; `../escape` →
the repo ROOT, the literal string appended to the declaration's lane list,
**exit 0 CLEAN**; `bad/door` → uncaught `FileNotFoundError`, **exit 1**,
the code `exits.py:10` reserves so a traceback is never read as a verdict.
The hazard was understood, written down, and defended at one of the two
sites that has it.

**2. `migrate`'s writer against `carrier_schema`.** The reader partitions
on the first colon and strips (`declaration.py:1567`); the writer tests
`raw.strip().startswith("schema:")` (`migrate.py:2003`) — a cheap retype
of a predicate the package already owned. **THE TWO DISAGREE ON TWO AXES,
AND ONLY ONE WAS FOUND FIRST.** Spelling: any whitespace between `schema`
and the colon splits them (space and tab measured; leading whitespace does
not, both strip). WHICH LINE: the reader inspects only the first
non-comment line and gives up there; the writer scans EVERY line and
rewrites the first match. They coincide only while the head is spelled the
writer's way.

**The cost is data corruption on the branch law 25 licenses.** Measured,
fresh repo, all XDG roots redirected, exit read without a pipe: `ITEMS.md`
line 1 `schema : 1`, line 6 `schema: 9` in a body. After `migrate
--schema-from 1 --apply` — line 1 UNCHANGED, **line 6 rewritten to
`schema: 2`**, output `written: ITEMS.md (schema 1 -> 2)` and `APPLIED — 1
declaration change(s), 3 carrier line(s)`, exit 0. A body line silently
rewritten, the version line untouched, and a clean report over both. A dry
run cannot see any of it: the dry run exercises the READER. Found by
reading the two sites side by side to design the fix — neither the
enumeration lane nor the desk's own reproduction reached it.

**3. `ledger.read` against its own contract.** Its signature returns
`(parsed, why)` — the reason channel EXISTS. Four bodies through the real
parser: no head → `lines=0, why=None`; head only → `0, None`; head + a
well-formed line → `1, None`; **head + unrecognised content → `0, None`**.
Content the parser declined to recognise is reported as zero with no
reason given, so the third answer is never returned and every caller reads
a clean zero. `migration_ledger_nonzero` is the caller that matters: a
REGISTERED, GREEN row carrying a prove-rows arrangement that PROVES it,
whose refusal text claims the criterion is *"checked at the ARTIFACT"* —
and at the artifact, unrecognised content counts as zero. The arrangement
fires on a well-formed line, so the proof exercises exactly the half that
works.

**WHY THIS IS ONE ENTRY AND NOT THREE.** Each site had the right thing one
import away. Each took the shorter route, and each shorter route parsed,
ran, and reported success. No guard fired at any of them, because there is
nothing for a guard to key on: a correct-looking expression in the correct
place. Law 26 asks what must be WRITTEN whose absence is computable; these
three teach that the question BEFORE it is whether the default can make
the writing unnecessary — the character folded at the constructor, the
head identified once and consumed, the third answer returned by the parser
rather than re-derived by each caller. Where the lazy route is correct,
nothing needs remembering and no absence needs computing.

**The grade on the third member, recorded because it is my own.** The
mechanism first booked for it — *"reads one of parse's three answers"* —
was wrong: `migrate.py:2633` handles the `None` case explicitly and all
four consuming sites do. That sentence was relayed and I was one edit from
writing it into this file as earned law, on a reading I had not executed.
The parser table above is what replaced it, and running it is what found
the better defect. (JOURNAL's own attachment costume, on the entry about
taking the shorter route.)
