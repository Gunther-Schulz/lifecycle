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
