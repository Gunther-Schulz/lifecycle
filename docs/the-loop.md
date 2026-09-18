# The loop — every arrow, and what notices it

**2026-09-18.** Written because gaps in this system keep being found by the
operator noticing something, one at a time, from outside. That works and it
does not scale: it finds whatever the last conversation happened to touch,
and it cannot show an absence nobody thought to look for.

**FORM: this repo's own transition table** (the close convention) — arrow →
verb → record written → check → **OBSERVER: what notices the arrow's moment
arriving**. Not a new form. The observer column exists precisely because a
trigger that is a NON-EVENT is observed by nothing unless something is built
to observe it, and **that column is where every gap below appears.** An arrow
whose observer reads *memory* is not mechanized, however good its verb.

**Three loops, because they fail differently.** The INNER loop runs inside a
session and mostly works. The OUTER loop crosses session boundaries and is
where the design has spent its attention. The META loop is the system
changing itself, and it is the least observed of the three — which matters,
since a meta loop that never advances is this repo's own diagnosis of
grinding.

Status vocabulary, and it is deliberately not a grade of quality:
**MECHANIZED** — something fires without anyone remembering.
**PARTIAL** — fires, but not at the moment that matters, or not for every member.
**GAP** — the observer is memory, or there is none.

---

## OUTER LOOP — session to session

| # | arrow | verb | record | check | OBSERVER | |
|---|---|---|---|---|---|---|
| O1 | nothing → a session exists | — | — | — | SessionStart hooks | MECHANIZED |
| O2 | session → holds standing state | — | — | — | `session-scan.py` injects ledger tail, item census, ready items, gate status | MECHANIZED |
| O3 | session → holds the repo's reading roster | — | `.claude/required-reading.json` | roster gate | `required-reading-inject.py` | **GAP — this repo declares no roster at all** |
| O4 | session → holds the registry map | `kind list --digest` | — | — | a SessionStart hook | **GAP — booked, not built** |
| O5 | session → picks work | `item ready` | — | `item check` | the injected ready list | MECHANIZED |
| O6 | **session needs a kind's CONTENT at the moment it matters** | — | — | — | — | **GAP — the central one; see below** |
| O7 | context dies by compaction → memory replaced by a summary | — | `compactions.jsonl` | — | `postcompact-log.py`, and `compact-reground.py` re-injects the working set | PARTIAL |
| O8 | work → ends cleanly | close ceremony | carriers | close questions | **nothing fires a close** — the operator types it | **GAP** |
| O9 | session → successor | — | ledger, items, records | — | O1 | MECHANIZED |

**O6 IS THE ONE THAT COSTS.** 20 of this repo's 25 kinds declare
`reader: session`. A command-read kind is fine by construction — running the
command IS the moment. For the other twenty nothing fires, and the injection
at O2 fires ONCE, at the start, before the session knows what it will need.
The design of record already concluded that retrieval fails at MOMENTS OF
APPLICATION rather than at session boundaries; the schema has a `reader`
stage that names a party and no stage that names a moment. **O4 raises the
odds and does not close this.** The symmetric fix is the reader stage gaining
a trigger the way lc-168 gives one to the writer, with the same three answers:
a command (free), a predicate (provable, three arms), or an honest event no
predicate computes. The one worked instance of a read-trigger that already
exists anywhere here is the runbook EVENT LANE — entered because something
fired, found through an always-loaded router.

**Measured cost of O6, 2026-09-18:** a document this desk had handled 17
times went unread at the moment it was needed; four discovery lanes were
dispatched to re-derive what it held. External agreement: a rule surviving in
the corpus while absent from context moves violation 0% → 30-59%
(arXiv:2606.22528, lane-verified, unopened here).

---

## INNER LOOP — inside one session

The player loop, with the repo's machinery on each arrow. Judgment lives in
*form intent* and is not mechanizable; everything around it is.

| # | arrow | verb | record | check | OBSERVER | |
|---|---|---|---|---|---|---|
| I1 | perceive: read the artifact | — | — | — | the reader's own act | MECHANIZED |
| I2 | form intent | — | — | — | judgment — correctly unmechanized | n/a |
| I3 | act → a finding exists | `item add` | ITEMS.md | `item check` | **memory** | **GAP** |
| I4 | act → a decision is made | `ledger add` | LEDGER.md | `ledger check` | **memory** | **GAP** |
| I5 | act → a course change occurs | append a line | `course-corrections.md` | close-time count | the session's own noticing; the close slot makes a zero answerable | PARTIAL |
| I6 | act → code changes | edit | the tree | suite, `--test`, `prove-rows` | the verbs themselves | MECHANIZED |
| I7 | change → committed | `git commit` | the object | pre-commit hooks (carrier shape, trailer, claims) | the hook | MECHANIZED |
| I8 | commit → published | `git push` | the remote | pre-push leak scan, claim gate | the hook | MECHANIZED |
| I9 | feedback: a check fires | the verb | its exit code | the three-answer contract | the command's own output | MECHANIZED |
| I9b | **feedback: a check verifies the RIGHT thing** | — | — | — | — | **GAP — see below** |
| I10 | **feedback → model updated** | — | — | — | — | **GAP — nothing records that a red was understood rather than silenced** |
| I11 | work → dispatched | Agent | dispatch log | brief/tail gates | the dispatch hooks | MECHANIZED |
| I12 | lane → returns | SendMessage | — | law 17 re-verification | armed horizon + idle subscription | MECHANIZED |

**I3 and I4 are the same gap and it is the cheapest one to misjudge.** The
verbs are excellent, the records are right, the checks work — and what fires
them is a session remembering to. That is the shape the corpus calls an
obligation with no output: a session that booked nothing reads exactly like a
session with nothing to book. I5 is the one place this was solved, and the
solution was not a better duty — it was a COUNT at close, which makes a zero
answerable instead of silent. **That is the transferable move for I3/I4.**

**I9b WAS FOUND THE DAY THIS FILE WAS WRITTEN, INSIDE THE INSTRUMENT BUILT TO
CLOSE I9.** Law 25 gained a read-back — after applying, re-open the artifact
and confirm the new state arrived, never trust the tool's own `written:`
line. The first read-back re-opened the artifact and asked whether the SCHEMA
NUMBER matched. That number was already correct before the write and had
never been in question, so the check passed over a run that had written none
of its planned changes. **An instrument that re-opens the artifact and asks
it the wrong question returns exactly what a sound one returns.** Caught by a
person reading the file afterwards; by nothing in the run. Repaired so the
read-back verifies EVERY PLANNED CHANGE rather than the version alone.
The generalisation, and it is why this is its own row: I9 asks whether a
check FIRED; I9b asks whether what it fired ON is what the claim needs. A
green from an instrument aimed one field away is indistinguishable from a
green from a correct one, and no exit code carries the difference.

**I10 is the subtlest and has no name yet.** A red that is understood and a
red that is silenced produce the same artifact: a green run afterwards. The
repo has one instance recorded of the failure (repairing a test to restore an
expected red, converting a live finding into a silenced instrument) and no
mechanism.

---

## META LOOP — the system changing itself

| # | arrow | verb | record | check | OBSERVER | |
|---|---|---|---|---|---|---|
| M1 | an incident → a rule | edit CLAUDE.md + JOURNAL | laws + journal | `audit`'s laws scope | **memory** | **GAP** |
| M2 | a rule → cited by an incident | — | the J-pointer | law/journal citation coupling | `audit` | MECHANIZED |
| M3 | a carrier → grows | `item add` | the head counters | `item ratio`, conservation | session-start banner | MECHANIZED |
| M4 | growth → a retirement pass | retirement | closures | the flow ratio | the banner prints "pass owed" | MECHANIZED |
| M5 | a rule → earns its stay or leaves | fire-rate review | the register | fire counts | **memory** | **GAP** |
| M6 | **the corpus grows → does it still help?** | — | — | — | — | **GAP — and there is counter-evidence** |
| M7 | a design → signed off | the transition table | the design doc | the table itself | the close convention | PARTIAL |

**M6 IS THE GAP WITH EXTERNAL COUNTER-EVIDENCE AND IT BELONGS AT THE TOP OF
ANY READING OF THIS FILE.** Agents accumulating rules, skills and memory show
non-monotonic capability erosion *unless explicitly constrained*
(arXiv:2605.09315, lane-verified, unopened here). This repo grows its corpus
every session. The qualifier is where M3-M5 live, so the design is not
refuted — but **no probe has been run here**, and a claim this much rests on
earns one built to disprove it. The measurement that would discriminate is
not yet designed; that is the honest state.

---

## The gaps, ranked by what a miss costs

1. **O6 — nothing fires a read at the moment of application.** Measured cost
   tonight. Everything else on this page is smaller.
2. **M6 — the corpus may be degrading what it improves, unprobed.**
3. **I3/I4 — booking and ledgering fire from memory.** Cheap to fix by I5's
   route: a count at close, not a better duty.
4. **I10 — a silenced red is indistinguishable from an understood one.**
5. **O8 — nothing fires a close.** The ceremony is good; its trigger is a
   person remembering.
6. **O3/O4 — no reading roster, no registry digest.** Both small, both booked.

**Three gaps this file deliberately does NOT claim to have closed**, because
they were open before it and remain so: direction drift has no mechanism and
an external survey found none either; completeness-as-distinct-from-decay is
unmeasured; and there is no control arm for whether the desk/peer split helps.

## How to use this, and its own honest limit

**At a design sign-off:** find the arrow the design adds or changes, and fill
its observer column. A design whose arrow has no observer is unsigned.

**When a gap is found by intuition** — which is how most of these were
found — locate it here first. If it is already a row, the row was not acted
on; if it is not a row, the table was incomplete and gains one. Both outcomes
are more useful than the finding alone.

**The limit:** this table is itself a persisted artifact with `reader:
session` and no read trigger. It is O6's own subject. Nothing fires it, and
the first thing that would make it fire is the registry digest listing it by
name.
