# How lessons actually get captured — and the design that follows

**Run:** 2026-09-18, desk 9553b0, three sonnet lanes, read-only over
`dotfiles/claude/JOURNAL.md` (3089 lines).
**Question:** for each lesson this corpus holds, what observable event marked
the moment it was captured? Serves lc-157's successor question: what can be
captured BY CONSTRUCTION rather than by someone remembering.

**Prediction registered in the brief before any lane read a line:** most
entries will trace to a PERSON noticing rather than to a mechanical event.
**Verdict: HELD, in all three ranges.**

---

## The two findings that decide the design

### 1. A guard firing is ENFORCEMENT, not learning

Lane 2, verbatim: *"MECHANICAL rarely stands alone as what got a lesson
WRITTEN DOWN — even where a guard literally fired many times, that guard was
enforcing a lesson someone had already captured, not capturing a new one."*

The desk had been treating "a hook fired" as a capture event and was building
an event list on that basis. Mostly wrong: `amend-gate` denying a bad amend is
not a lesson, it is a lesson already learned, working correctly.

**What replaced it: the UNPLANTED RED.** The moments something genuinely NEW
entered the system were a test failing *for a reason nobody planted*, two
independently-built instruments *disagreeing*, and a control catching what the
rule missed. Narrower than "a guard fired", rarer, and computable.

### 2. The routes are a PIPELINE, not four parallel buckets

Lane 2 again: *"every MECHANICAL instance in my range comes from
dispatch-guards hooks that were THEMSELVES minted earlier in this same range
by PERSON/SELF events."*

So: **a person notices once → that becomes a detector → the detector catches
every later occurrence silently.** Mechanical capture is the DOWNSTREAM of
person-noticing, not a competing source. That pipeline is what the operator
calls a project finding its groove, and this is the first time it has been
seen happening in the record.

---

## The trajectory — visible only across the three ranges

| range | period | what it shows |
|---|---|---|
| lane 1 | 07-18 → 07-26 | PERSON 23, MECHANICAL 10, SELF 3, UNCLEAR 4 (40 events). **No trajectory** — mechanical present from day one, ratio flat across 9 days. |
| lane 2 | 07-26 → 08-07 | PERSON 8, SELF 5, UNCLEAR 1, MECHANICAL as sole route **0**. Instrument-mediated catches **cluster late**. |
| lane 3 | 08-07 → 09-18 | ~90 consecutive entries **near-totally PERSON**; then a sharp diversification from 09-13. |

**The inflection is real and recent.** Lane 3's last week carries: a guard
blocking a push and the session then RETRACTING ITS OWN DIAGNOSIS after
re-executing the guard and finding the guard right (the tool correcting the
session); a test runner reporting "0 tests ran, exit 0" mistaken for green; a
subprocess exit code swallowed, caught only because a positive control failed
to fire; 24 mis-authored commits found *"by luck, not by any mechanism"*.

**Lane 3's methodological ruling, adopted:** treat 2026-09-13→18 as a
DISTINCT higher-mechanical-rate sample rather than averaging it into the rest.
A forward-looking design that used the aggregate ratio would under-weight the
mechanical half, because the compounding is accelerating.

---

## The half that cannot be mechanized, and why it is not a gap

Lane 1 at event grain: **19 YES / 19 NO** could-have-been-mechanical. Read
what the NOs actually are:

- *"operator judged both ceremony"* — **the rules fired correctly and the
  operator decided the correctness was unwanted**
- coining `evidence-voice` / `directive-voice` — a naming act
- what belongs in the corpus vs protocol machinery — a scoping judgment
- compression, and the ethic-vs-lens boundary — style and taxonomy
- *"reads strange"*

**Not one is a defect.** Every one is taste, scope or naming judgment about
the corpus itself. No instrument can detect "this correct behaviour is
unwanted", because unwanted is a preference and not a state. That half is the
operator designing the corpus — the work, not a gap to close.

**So the honest scope: this design catches the DEFECT half, which is the half
that costs the operator interruptions.**

---

## A fifth capture route the taxonomy lacked

Lane 1 found a lesson traced to a GitHub issue where the community had already
diagnosed the problem — not the session, not the operator, not a guard.
**EXTERNAL / PRIOR-ART.** For a groove meant to build itself, "check whether
this is already solved outside" is a real route and the four-bucket taxonomy
had no slot for it.

---

## Instrument grading — the study's own honesty

- **SELF is confounded; PERSON is not.** Lane 1, asked directly: all 23 PERSON
  events carry explicit verbatim operator quotes, so PERSON is grounded. But
  SELF is assignable only by ELIMINATION — the corpus is written in third
  person throughout and never uses first-person self-report, so no positive
  marker for SELF exists. **SELF's near-zero is carried as could-not-verify**,
  never as a finding about session self-blindness. The confound is asymmetric
  and only one number is affected.
- **Event types SATURATED** (lane 2): the list stopped growing well before the
  reading finished; new types appeared only up to ~2026-08-02. A population
  finding, not a shortcut — and the reason no further lane was commissioned.
- **Compression did NOT strip capture-provenance.** Lane 1's UNCLEAR rate 10%,
  lane 2's 7%, and lane 2 confirmed the heading and paragraph forms do not
  differ in recording HOW a lesson surfaced — only in incident density. The
  corpus's deliberate Narrativ→Evidenz-Register compression kept the how.
- **Three Background errors, all the dispatching desk's, all caught by lanes:**
  a preamble claim (line 41 is a real entry); an entry count off by 7.6x (45
  counted by `##` headings, 344 actual — the file's dominant form is a
  flush-left dated paragraph); and a stated corpus end date of 09-13 when the
  file carries entries through 09-18. All three are the same failure — stating
  an artifact's shape from a quick pattern instead of reading it.
- **Coverage stated per lane, including one caveat corrected UPWARD** (lane 2
  read 100%, not the ~55% it first claimed). Lane 3's ~150+ embedded entries
  were characterised in aggregate and explicitly NOT individually templated.

---

## THE DESIGN

### Part 1 — state-advancing acts WRITE (the backbone)

**Operator, 2026-09-18:** *"closing a session should ideally not even have to
do much if the work was done well during the session persisting state
throughout."*

Measured by a peer the same day: every write to its records was a deliberate
act it had to remember to make; none was a byproduct of the work, and the
record line was emitted ONCE in a nine-hour session. A carrier written from
recollection drifts exactly like a stale label.

**So the verb that does the work also records that it did.** Closing an item
writes its closure; settling a question writes the answer; abandoning an
approach writes the dead end. Not a reminder to write — the write is part of
the act. **Test: the close should find nothing left to do.**

### Part 2 — watch for the unplanted red

Not "a guard fired" (high-volume, near-informationless). The computable set,
drawn from the lanes' merged event list:

- a test fails on a case outside its fixture set
- two independently-built measurements of one quantity disagree
- a stated total does not match the enumeration beneath it
- a positive control fails to fire
- a runner reports a pass-shaped number over zero executions ("0 tests ran")
- a subprocess exit code goes unread while only stdout is checked
- a stored fingerprint mismatches its registered value
- write-set paths fail to resolve, so a join silently reports zero collisions
- a newly-minted guard fires on its own author's next legitimate edit

### Part 3 — dead ends get a home

"We tried X, it fails because Y" is what saves a future session a day, and it
is the first thing lost: a dead end feels like nothing happened and produces
no commit, no closure, no artifact. **No registered kind currently claims
it.** Register it, with a home and a staleness rule.

### Part 4 — lifecycle governs the global corpus as a CARRIER

The corpus is a persisted thing with a home, writers, readers and growth, and
none of it is declared. Nothing checks whether a module grew without an exit
or whether a rule ever fires — one rule measured at 0.27 → 0.19 per 1000 turns
across its own mint, found only by a hand-built scanner at ~1/3 recall.

**Boundary, so it does not become a second corpus:** lifecycle governs the
corpus's SHAPE — homes, staleness, exits, growth, fire rate. It never governs
its CONTENT — what a rule says, whether it is right, ethic vs lens. That stays
the operator's, first-hand. (Booked: lc-158.)
