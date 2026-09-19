# Design: the registered-closed-vocabulary contract (decision D-3)

**Round desk, 2026-09-19. Decision: ledger D-3 (+ D-7, D-8, D-10 as
instances). Status: LOCKED pending the fresh-context attack round; no build
before the attack returns. Test population: round map E16. This document is
the dispatchable design; the builder inherits zero design freedom — form
follows the repo's existing instances (refusals.py registry idiom, items.py
slot grammar).**

## The mechanism in one paragraph

Every closed vocabulary the declaration or the carriers' slots carry is
REGISTERED: name, members, the consumer that renders it. Each registered
vocabulary carries a typed OUT-OF-VOCABULARY arm — value form
`cannot-express: <reason>` — rendered DISTINCTLY by its consumer, never
folded into a member. A registered vocabulary without the arm is a checker
finding. A recorded OOV instance with its reason is the WIDENING SIGNAL:
new members are minted from recorded reasons, never guessed (the Begehung's
sharpened class — "the repair is where the class survives" — turned into
the mint mechanism). Registration happens ON CONTACT (a gap found, or a
vocabulary next touched), never as a big-bang sweep.

## Parts (write-set per part; each names its red-first)

**P1 — the registry.** New `plugin/cli/lifecycle_core/vocab.py`:
`Vocabulary(name, members, oov_form, consumer, renderer)` entries + a shape
check. Initial registrations (on-contact set, nothing more): reader-when
states; blocker types; census buckets; item grade words (already closed in
the carrier — registered, not changed); trigger-stage vocabulary
(verb/predicate/none-with-reason). New refusal row `vocab_without_oov`
(fires on a registered vocabulary whose consumer lacks the distinct OOV
rendering — plant: register a vocabulary with `oov_form=None`). `--test`
walks the registry the way it walks ROWS. Write-set: vocab.py (new),
refusals.py, roster.py wiring, test/test_vocab.py (new).

**P2 — reader-when MALFORMED (red-first input 1, Begehung f1).**
`read_moments` gains state MALFORMED, distinct from UNDECLARED (no `when`
at all) and BROKEN (a predicate that ran and failed): a `when` that parses
to no known mode is MALFORMED with the offending text quoted. This makes
read_moments AGREE with `_check_reader_when` (which already answers
declaration_malformed for two of the three probed cases — the Begehung's
two-instruments-disagree finding). Red-first: the lane's own 9-case state
matrix (r3 TSV row 1 basis) — the three malformed probes must return
MALFORMED, the six controls unchanged; the matrix lands as
test_declaration.py cases. Write-set: declaration.py, test_declaration.py.

**P3 — census third bucket (red-first input 2, f4; decision D-7).**
`blocker_slot_census` gains PREDATES-THE-MECHANISM: population = evidence
blockers on items whose booking predates the exercise mechanism's build
epoch — a recorded constant `EXERCISE_EPOCH` in items.py, value = lc-175's
build commit date, comment citing D-7's ledger line. The item-check line
splits into three counts; zero grade changes, zero new findings (lc-175's
MUST-NOT-MOVE honoured exactly). Red-first: at the current carrier the
bucket reads 8 / missing 0 (all eight predate — f4's executed basis); a
planted post-epoch fixture item with an unexercised evidence blocker reads
missing 1. Write-set: items.py, test_items.py.

**P4 — blocker type `external <event>` (decision D-8).** `classify_blocker`
gains the member: evaluated by nothing, cleared by hand or desk with the
event named; `item ready` renders it "in a NAMED EXTERNAL court: <event>",
never as waiting-on-evidence. AND the general OOV arm lands in the same
grammar: a blocker written `cannot-express: <reason>` is ACCEPTED, rendered
as its own line ("the vocabulary cannot express this blocker; reason
quoted"), counted separately by item check — each instance a standing mint
signal. Red-first: a planted `external cache-fix ships its next release`
blocker renders the external court (not evidence-waiting); a planted
`cannot-express: …` renders the OOV line; a malformed bare prose blocker
still refuses (blocker_untyped unchanged — proven live at this desk today).
Specimen re-typing at build: the four cache-fix `evidence false` items
(lc-24, lc-53, lc-66*, lc-147) amend to `external <named event>`; lc-235's
round-close blocker clears at close, untouched. (*lc-66 sits behind lc-67's
item blocker — re-read its slots at build; the tool resolves amendments.)
Write-set: items.py, cli.py rendering, test_items.py, + the specimen
amendments (carrier, by verb).

## Three answers, per part

P1's shape check: clean / vocab_without_oov / could-not-verify (registry
unimportable = CNV, never silence). P2: MALFORMED is itself the third
answer's instantiation at the evaluator. P3: three buckets ARE the repaired
answer set. P4: OOV blocker = the answer set's open end, counted, never
folded.

## Observers (the transition table; home = this section, re-read at close)

| arrow | verb | record | check | OBSERVER |
|---|---|---|---|---|
| vocabulary registered → covered | (build act) | vocab.py entry | vocab_without_oov row | `--test` walks the registry |
| OOV instance written → surfaced | any carrier verb accepting it | the slot line itself | item check's OOV count line | session-start banner (prints item check) |
| OOV reasons accumulate → widening minted | mint round | ledger decision + member added | the widened member's own red-first | fire-rate review sweeps `cannot-express:` lines (grep, whole-list, never recollection) — judgment remainder, prose-rest declared |
| registry grows → still consulted? | — | — | — | the erosion probe's roster channel bounds instrument growth (lc-234); vocab registrations are code-side, same channel |

## Stop/yield (the admission lens, this mechanism's own)

Register ON CONTACT only — the initial set above is what this round
touched; no sweep for every enum in the codebase (over-constraint bound;
the sweep is the Collector's Fallacy arm). YIELD = checker findings plus
recorded OOV instances. STOP = a review window with zero OOV recordings
across all registered vocabularies asks WHICH of complete-or-unread — the
fire-rate review's question, not a new mechanism's.

## Named non-goal

(m)-class conflicts — two correct mechanisms with no shared exit — are NOT
rendering defects and get no OOV arm; each needs its own shared-exit design
(first specimen: the redaction-verb / scan-at-admission pair, unbooked,
carried on the round map).

## Deployment note

All four parts are verb/check-side — none is always-on beyond the existing
banner's item-check print, so NONE gates on the erosion probe's result.
(The probe gates f2's read_moments CALLER deployment, a separate design.)
