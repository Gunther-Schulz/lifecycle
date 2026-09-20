> **STATUS (driving desk, 2026-09-20): D1–D4 ALL DECIDED AS RECOMMENDED —
> operator GO ("as you recommend") at lifecycle-d9, ledgered beside this
> booking. This repo copy is now the transition table's BINDING home
> (§7's own rule). Build order: lc-252 (the declared=N tally fix) lands
> before any counter that reads the fire detail. Authored by the delegated
> design desk lifecycle-ef; booked verbatim below this block.**

# O6 — the SURFACING half. Design proposal + decision-round material

**Desk:** lifecycle-ef (design judgment, within the kickoff's scope).
**Kickoff:** `docs/directives/2026-09-20-o6-when-stage-arc-kickoff.md` at 7cda522.
**Scope ruling (driving desk, after the premise correction):** design the
SURFACING half only. lc-224's per-reader-entry `when` is settled ground this
design CONSUMES and never re-decides. The zero-adoption fact is a DESIGN INPUT,
so what the default supplies when nothing is declared is part of the
deliverable, not an edge case.
**Not this arc's to decide:** the goal-question slot admission (gated on the
treatment arm, directive at 6dc8b14).

---

## 1. THE STATE, MEASURED — the design's input, not its background

Every number here was run at the artifact in this session; commands in §9.

| fact | number | basis |
|---|---|---|
| kinds registered | 29 | the declaration |
| reader entries | 50 | `kind moments` |
| reader entries with a declared `when` | **0** | 0 of 29 kinds carry an object-form reader entry |
| `kind moments` states rendered | 50 × UNDECLARED, no FIRE/QUIET/BROKEN/MALFORMED/NONE | its own output, exit 0 |
| reader entries by type | **verb 23 · session 24 · hook 3** | the declaration |
| kinds by reader mix | session+verb 13 · session-only 9 · verb-only 4 · hook+session 2 · hook-only 1 | the declaration |
| every verb run emits one fire line | yes — verb, repo, outcome, optional detail | baseline 1,301,044 → 3 runs → +3 lines, the three lines read back |

**The shape those numbers make.** The evaluation half is built, correct, and
describing nothing. The surfacing half has no mechanism at all. And the
authoring burden that would close the gap by declaration — 26 kinds × 8 repos
(lc-239) — is precisely what zero adoption says will not happen: this repo, the
mechanism's own home, authored none in the day the shape has existed.

**So the design's first question is not "what predicate fires" but "what fires
with nothing authored".** That is law 26's bounding question arriving as an
empirical fact rather than as a discipline.

---

## 2. THE HARD BOUNDARY THAT DECIDES EVERYTHING

**Lifecycle can observe ACTS and nothing else.** It sees verb invocations (one
fire line each, measured), git hooks, and session-start hooks. It cannot see a
session's reply text, its reasoning, or its file reads — a `cat` or a Read-tool
open of `CLAUDE.md` is invisible to every mechanism in this repo.

Three consequences, and they are load-bearing:

1. **A "write a line in your reply" demand is not machine-checkable here.** It
   is checkable by a desk reading the reply, which is a person-or-peer
   instrument, not an environmental one. Any design claiming otherwise ships an
   assurance wider than its predicate.
2. **"Was it read?" has no honest answer today** — which is exactly the unbuilt
   measurement the design of record names when it withdraws the retrieval grade.
3. **The only way to make reading observable is to make reading an ACT** — i.e.
   route it through a verb. That is not ceremony; it is the single move that
   converts the whole question from unmeasurable to measurable.

---

## 3. THE PROPOSAL IN ONE LINE

**Derive the moment from what the declaration already says, surface it on acts
the environment already observes, and make the read itself an act — so that
"surfaced and not read" becomes a number for the first time.**

No new always-on channel. No new authored vocabulary as a precondition.

---

## 4. THE THREE PARTS

### Part A — THE DEFAULT (what fires with nothing authored)

A reader entry's moment is DERIVED unless a `when` overrides it:

- **Tier 1 — `verb:` readers (23 of 50 entries).** The moment IS the verb
  running. Nothing to author, and this is already true: lc-224's arity argument
  rests on exactly it ("the verb reader's moment is implicit in the verb
  running"). Declaring a `when` here would be restating the obvious.
- **Tier 2 — `session` readers (24 of 50).** Default moment: **the kind's own
  home is about to be written.** A session writing a carrier is, by
  construction, at the moment where that carrier's other readers matter. This
  is derivable from `home` alone — zero authoring — and it is the one moment
  the environment can already see (the write gate arms on first write; the
  commit hook sees paths).
- **Tier 3 — the residue.** Genuinely event-shaped moments stay authorable as
  today's `when` predicate. UNDECLARED remains legitimate and never a finding
  (`kind moments` already rules this, correctly, under law 11).

**What this changes:** the authoring population drops from "26 kinds in 8 repos"
to "the residue nobody has yet found a default for" — and the default covers the
session-reader population that is the entire O6 gap.

### Part B — THE SURFACE (where a due read appears)

Ranked by reach against cost. **The erosion result does NOT license an always-on
addition here** — its rider 2 bounds *instrument-bearing* mechanisms only and is
explicitly silent on prose, conventions and required slots. An index line is
presence, not an instrument, so it must earn its context cost on its own.

*Provenance, corrected 2026-09-20 after the driving desk's record update: the
erosion probe RAN TWICE — run 1 at lc-234, 2026-09-19
(`docs/audits/2026-09-19-erosion-probe-results.md`), and the second run was an
unintended replication off the design doc's then-stale "not yet run" header,
since repaired at c777e84. Both returned HEALTH, and what is cited above is
rider 2 — the design's own scope statement, unchanged by either run — so nothing
in this section moves. Cite the run-1 results file if the probe is cited again.*

- **B1 (the floor, recommended): the acting verb's own output.** When a verb
  runs, it names the kinds whose derived moment fired for that act. Zero context
  cost when no verb runs; the session sees it exactly when it is acting; no new
  channel; it rides a line the fire log already writes.
- **B2 (the reach, named not taken): the write gate.** Already armed on first
  write, already injects the roster — the natural home for "you are about to
  write X; these kinds are read before writing X".
- **B3 (out of scope, named so it is not rediscovered): harness hooks at
  tool-call granularity.** Maximum reach, machine-local settings, and lc-93's
  territory rather than this arc's.

### Part C — THE READ AS AN ACT (what makes any of it measurable)

`kind show <name>` exists and prints a kind's STAGES. It does not put the kind's
CONTENT in front of a session, and nothing else does either.

**The proposal: a read verb that prints the kind's body (or its pointer where
the body is large), and whose invocation the fire log already records.** Then:

- surfaced-but-not-read is countable — a moment fired, no read line followed;
- the first machine answer to "was the record read before the question was
  answered another way" exists;
- the pit of success does the enforcement: if the cheapest way to read a kind is
  the verb, the proxy converges on the fact without a duty being added.

**The boundary, stated rather than hidden:** "unread" means *not read through the
verb*. A session that opens the file directly reads it and the counter says
otherwise. The design must report this as a proxy in the verb's own output, or
it repeats the class it exists to fix.

---

## 5. THE DECISION ROUND — four numbered decisions

**D1. What supplies a moment when nothing is declared?**
- (a) Nothing. UNDECLARED means no surfacing. *Status quo; zero adoption persists
  and O6 stays open by construction.*
- (b) **Tier 1 + Tier 2 derivation (§4 Part A).** *RECOMMENDED.* Costs no
  authoring, covers the whole session-reader population, and is derivable from
  fields the declaration already carries.
- (c) Require authoring, unblock lc-239 by writing 26 values. *Refuted by its own
  arithmetic: this repo authored zero in the day the shape existed.*

**D2. What carries the surfacing?**
- (a) **The acting verb's output (B1).** *RECOMMENDED.* No always-on cost, no new
  channel, and the erosion rider cannot be cited to license the alternative.
- (b) An always-on index line at session start. *Measured insufficient on its own
  — instance 3 is a document the session WROTE six hours earlier and did not
  reach for — and it is the reader-stops-reading risk.*
- (c) Both. *Defensible only after (a) has a fire-rate number.*

**D3. Is reading routed through a verb?**
- (a) **Yes — a read verb, recorded by the existing fire log (Part C).**
  *RECOMMENDED.* It is the only move that makes the effect measurable at all.
- (b) No — surface only. *Cheaper, and leaves "did it help?" permanently
  unanswerable, which is gate 1's own failure mode.*

**D4. What is written at the moment, whose absence is computable?**
- (a) **Nothing new.** The fire log already carries both halves: the surfacing
  line and the read line. The absence IS the missing second line. *RECOMMENDED —
  law 26's bounding question answered in the affirmative: the default makes the
  writing unnecessary.*
- (b) A reply-line demand (the treatment arm's shape). *Not machine-checkable
  here (§2); belongs to the gated slot, not to this stage.*

---

## 6. DEGENERATE FORMS AND THEIR DETECTORS (lc-240's done-criterion, answered)

| failure | what it looks like | detector | repair |
|---|---|---|---|
| **over-trigger** | every verb output carries due-read noise; the reader stops reading | surfaced-vs-read ratio per kind, from the fire log — a kind surfaced N times and never read is the candidate | move the MOMENT, never the reader (law 11 from the default side) |
| **under-trigger** | no moment, nothing surfaces, invisible | `kind moments` already renders UNDECLARED; the new number is UNDECLARED-**with-a-session-reader**, which is the honest gap count rather than today's 50 *(OVERTAKEN BY THE BUILD, 2026-09-20: lc-253 derives every verb and session reader, so a session-tier UNDECLARED can no longer occur — the under-trigger surface is now the RESIDUE: operator, lane:, hook:, producer: readers, 3 of 50 entries in this repo today)* | supply a default (D1b) or author the residue |
| **drift** | the surfaced description diverges from the body | kinds carry a staleness stage; a surfaced DESCRIPTION inherits lc-247's class and must state its predicate exactly | the staleness stage, and no description wider than its predicate |

**DECLARED UNDETECTED:** whether the surfaced read was *useful*. Relevance is the
model's judgment by lc-240's MUST-NOT-MOVE, so no detector here grades it, and
the ratio above must not be read as a usefulness measure.

---

## 7. THE TRANSITION TABLE (sign-off requirement, per the repo CLAUDE.md)

**Home of this table: this document, until the driving desk books it into the
repo — at which point the repo's copy is the one that binds.**

| arrow | verb | record written | check that proves it | OBSERVER |
|---|---|---|---|---|
| a session acts on a carrier whose kind has other due readers | the acting verb (no new verb) | fire line, `detail: surfaced=<kinds>` | red-first: a kind with a due reader surfaces; one without does not | the verb invocation — already observed, measured at +1 fire line per run |
| a due read happens | the read verb (D3a) | fire line, `detail: read=<kind>` | red-first: reading through the verb writes a line; not reading writes none | the verb invocation |
| a moment is surfaced and never read | — | the ABSENCE of the second line | the surfaced-vs-read counter, over the fire log | the counter's own run (a periodic verb), **not memory** |

**The third row is the one that decides whether this design is worth building**,
and it is the row that did not exist before: today the question has no observer
of any kind.

---

## 8. WHAT WOULD KILL THIS, named so it is falsifiable

1. **Surfaced-vs-read stays flat at zero reads.** Sessions see the line and do
   not act on it — presence without demand, the adherence split reproduced, and
   the design is the wrong leg.
2. **The ratio cannot be read because sessions read files directly.** The proxy
   never converges; the verb is ceremony and the counter measures its own
   adoption rather than retrieval.
3. **Over-trigger arrives first.** Verb outputs grow noisy and the surfacing is
   discounted before it is ever load-bearing — the reader-stops-reading disease,
   and the repair is fewer moments, not louder ones.

**Kill-test alignment (purpose.md):** if this ships and the operator is still the
thing that notices an unread artifact at the same rate, the mechanism did not
move the quantity it exists to move.

---

## 9. COMMANDS, so every number above is re-runnable

```
python3 plugin/cli/lifecycle kind moments                 # 50 entries, all UNDECLARED, exit 0
python3 plugin/cli/lifecycle kind show laws               # stages, not content
python3 plugin/cli/lifecycle kind moments | grep -oE '(UNDECLARED|FIRE|QUIET|BROKEN|MALFORMED|NONE)' | sort | uniq -c
# reader-entry split and kind mix: python over .claude/lifecycle.json (§1)
# fire-line-per-verb: wc -l on $XDG_STATE_HOME/lifecycle/fire.jsonl before/after three verb runs
```

---

## 10. ONE FINDING FOUND WHILE MEASURING — reported, not folded in

`kind moments` labels a count of reader ENTRIES as DECLARED MOMENTS. `seen` is
incremented for every moment including UNDECLARED ones (verbs.py:3909), and the
tally prints `50 declared moment(s)` while the declaration declares **zero**; the
fire detail carries the same word as `declared=50 executed=0` into the carrier a
banner reads back.

The console is saved by its neighbours — it pairs the number with `0 of them
EXECUTED` and a paragraph naming the reach, and the code's own comment shows the
author knew. **The fire-log detail carries no such paragraph**, and it is the
half a later counter reads. Same class as lc-247 (a marker's predicate narrower
than its label), one surface over, and directly load-bearing here because §4
Part C proposes measuring from that carrier.

Not folded into this design because it is a defect in shipped code, not a design
question: it wants an item, and the grading is the driving desk's.
