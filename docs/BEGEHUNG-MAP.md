# Begehung MAP — the lc-157 design (five mechanisms for a self-building groove)

System under review: the DESIGN, not the lifecycle tool. Design of record:
`docs/answerable-not-felt.md` (the PLAN section). Supporting measurements:
`docs/audits/2026-09-18-capture-routes-and-the-groove.md` and
`docs/audits/2026-09-18-desk-peer-catch-study.md`.

Interval: a row unvisited for the two rounds before the current one is itself
a finding at the next invocation.

Surfaces this MAP was derived from (step 1-2), each with the consumer where
wrongness lands:

1. **The PLAN's five mechanisms** → the build desk. Cost: the wrong thing gets
   built, correctly.
2. **The two audits' measurements** → the design itself, and every future
   session reading them. Cost: the design rests on a number that is wrong.
3. **The booked items** (lc-156, 158-162) → the build desk. Cost: wrong work,
   or work whose premise died.
4. **The record format file** (dotfiles `claude/investigation-record-format.md`)
   → every session writing a record, and the shipped checker. Cost: the
   checker grades against a definition that does not say what it should.
5. **The shipped code** (`lifecycle verify`, `lifecycle record check`) → any
   repo that runs them. Cost: a false clean or a false finding, silently.
6. **Outward messages** (to the build desk, to peer sessions, to the operator)
   → parties who act on them. Cost: another party acts on a wrong fact.

## Axes

| axis (what against what) | status | last visited (date · round) | yield | next step |
|---|---|---|---|---|
| A1 the PLAN's mechanism claims vs what was actually measured — does each mechanism rest on a measurement, or on the desk's reasoning? | dark (modelled) | — | — | walk each of the five, name its cited basis, check the basis says what the mechanism claims |
| A2 the audits' numbers vs the artifacts they were computed from — recompute, do not re-read | dark (modelled) | — | — | recompute the 55% amend rate and the 44%/39%/19%/17%/5% split independently |
| A3 booked items vs the world they were booked against — the design's own mechanism 5, applied to the design's own bookings | dark (modelled) | — | — | re-ground lc-158/160/161/162 evidence slots at HEAD |
| A4 the format file vs the shipped checker — definition against the thing grading by it | dark (modelled) | — | — | diff the format's stated rules against records.py's predicates |
| A5 shipped code vs its own three-answer contract — do `verify` and `record check` carry could-not-verify where they must? | dark (modelled) | — | — | the unregistered `verify_check_did_not_run` row is the known instance; sweep for siblings |
| A6 outward messages vs what the artifacts actually said — claims relayed to peer/operator, re-read at source | dark (modelled) | — | — | sample this session's peer messages, check each factual claim at its artifact |
| A7 the design's coverage vs the ORIGINAL question — "well scoped and complete before building"; completeness is measured nowhere | dark (modelled) | — | — | name what "complete" would mean and whether any mechanism reaches it |
| A8 label-vs-body drift over the design's own carriers — headings, counts and summaries against their bodies | dark (modelled) | — | — | the design note is 550+ lines and amended 6x today; check its section claims against their bodies |
| A9 enumeration marks — every population the design counts, checked for the chosen-mark failure | dark (modelled) | — | — | three instances already measured today; sweep the design's remaining populations |
| A10 THE EXISTING CARRIERS vs the design's five mechanisms — items, runbooks, directives, ledger and records were EACH built to solve a piece of this; what do they already cover, where do they overlap, and where does the handoff between them fail so the right action does not fire at the right time (operator-named, 2026-09-18) | prose-covered (the declaration's writer/reader fields carry it; no guard holds the design to them) | 2026-09-18 · r2 | 3 | extend the verb-writer pattern to a session-written kind and measure whether it stops drifting |
| A11 THE NARROWING'S UNIVERSALITY — mechanism 2 assumes CONVERGENT work (hypotheses eliminated toward an answer); is it the right shape for DIVERGENT work where the space is widening, and for routine execution where there are no hypotheses at all? (operator-named, 2026-09-18) | dark (modelled) | — | — | classify this session's own phases as convergent or divergent; check whether a narrowing would have helped or distorted each |
| CROSS-CUTTING lifecycle — per artifact the design holds: where does it live, who writes it, who reads it | dark (modelled) | — | — | the MAP and findings file themselves: is a `.tsv` in docs/ claimed by any registered kind? |
| ENFORCER under its own invariants — the design demands that sessions maintain a narrowing, re-ground evidence at pickup, and write as they work; asked of THIS design and THIS session | prose-covered (the design note's own PLAN section; no guard holds the design to its own mandates) | 2026-09-18 · r1 | 7 | walk A11's boundary into the format's tag vocabulary — a LOCKED tag for decisions |

## Rounds

| round | date | axis | why that axis | read-at | closed-at | reach | class |
|---|---|---|---|---|---|---|---|
| 1 | 2026-09-18 | ENFORCER under its own invariants | operator-named ("we are missing an angle still"); and it is the darkest row by construction — a design that mandates practices has never been held to them | 7a12a88 | 99e998c | 0 hold, 1 superseded | THE DESIGN GENERALISES FROM ONE WORK-KIND. Read across A11, A10 and ENFORCER: mechanism 2 assumes diagnosis-shaped work, mechanism 5's estimate half assumes evidence settles it, and the existing carriers were each built for a different kind. The recurring property is a rule stated universally from a single instance — the corpus's own transfer test, unapplied to the design itself. |
| 2 | 2026-09-18 | A10 THE EXISTING CARRIERS vs the design's five mechanisms | operator-named — items, runbooks, directives, ledger and records were each built to solve a piece of this puzzle, and the design has been ADDING mechanisms without mapping what already covers what | cf14946 | cf14946 | 3 hold, 0 superseded | THE DESIGN RE-INVENTS WHAT THE REPO ALREADY DOES. Read across A10 and ENFORCER: mechanism 2 is the verb-writer pattern already proven on 4 of 22 kinds; the round-1 class (generalising from one work-kind) has a sibling here — generalising from one's own reasoning without first reading what the system already carries, which is the corpus's own read-the-existing-instances rule unapplied to the design. |
