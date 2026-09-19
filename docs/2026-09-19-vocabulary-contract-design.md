# Design v4: the registered-closed-vocabulary contract (D-3; D-7 rev.; D-8; D-10 deferred)

**Round desk, 2026-09-19, FOURTH LOCK — pass 3 (opus verification: 34/42 discharged; terra recovery) integrated; finding ids resolve in docs/audits/2026-09-19-design-attack-r1.md and -r2-pass3.md (NIT1 discharged by landing them). v2's attack pass (opus r2: 10
blocking/11 notable/2 nit; astra r2: source-backed convergents + uniques)
concentrated entirely in realization detail — zero findings against any
decision or mechanism core, eight v2 repairs verified held on their own
claims. Every repair cites its finding; ids resolve in the two landed
audits files and docs/2026-09-19-round-decisions.md. v1-v3 in git.**

## The mechanism (intent unchanged)

Every closed VALUE vocabulary is REGISTERED: name, members, the IMPORTABLE
consumer, and the PROOF PATH — the sanctioned write/read route the OOV
proof traverses (astra-c4: a renderer can pass while the operational path
never reaches it, so each registration names its route: grades through the
carrier parse + census; reader-when through read_moments; evidence marks
through the admission door). OOV form: **`cannot-express(<date>): <reason>`
— dated at birth (B7's cure applied contract-wide)**. Registration on
contact. The BLOCKER slot stays exempt (V4), and the exemption now BUYS
something (B9): when `blocker_untyped` fires, the refusal path writes a
fire-log event carrying the row name in the detail field (firelog's
existing optional detail — verbs.py + firelog.py in P4's write-set), so
refusals-where-no-type-fit are countable from the log. **Scope, stated
(FF-1): the fire log is machine-local and best-effort (a lost write is
silent, firelog.py:19-23), so this count is a FLOOR on one machine, never
a census — the durable half of the signal is the refusal text at the desk
that met it. A widening decision cites the floor; it never treats it as
the population.**

## The OOV lifecycle, computable end to end (astra-c3, V8)

An OOV instance is a dated line in a carrier slot. It LEAVES the count by
being amended away (re-typed to a real member once one exists, or its slot
corrected) — so **the count IS the dispositions-owed figure**: `item check`
prints "N cannot-express, oldest <date>", and zero means drained. The
drain act is a desk act whose trigger is the printed age, **and its RECORD
is a ledger line written by the session that runs the pass (T-c2/T-w1:
the pass-owed print is today an instruction with no pass record — the
ledger verb is the existing recorder, so a graded pass IS its ledger
line, no new mechanism). Rate decoupled (FF-5): the print fires only
above the 3:1 tripwire (2.00:1 live), so dispositions are ALSO graded at
any kaemmung or close pass — the trigger is whichever arrives first.**

## Parts

**P1 — the registry.** `vocab.py`: `Vocabulary(name, members, oov_form,
consumer, proof_path)`. Initial registrations and where their accepting
predicates LIVE — **write-set includes those files (B10, law 24):
declaration.py (READER_WHEN_MODES :221, TRIGGER_MODES :182), items.py
(GRADES :62-64, EVIDENCE_MARKS :293, census buckets :1843)** — plus
vocab.py (new), refusals.py, roster.py, test_vocab.py. Grade vocabulary's
OOV consequence stated (N11): `census()` gains an explicit
`cannot-express` bucket, EXCLUDED from the drain-trigger denominators its
docstring protects, printed on its own; `item ready` renders an OOV-graded
item as unschedulable-with-reason; the move refuses it (a grade must be a
real member at close). Roster row: OOV value through each registration's
proof path, output distinct from every member (V6/AV1). **Write-set also
carries verbs.py (N11-new-defect: the `item ready` unschedulable-with-reason
rendering realizes in cmd_item_ready — the repair's own added claim gets
law 24's resolution).**

**P2 — ONE invalid-state partition (V5, f1, N4).** The classifier is
extracted from `_check_reader_when` and consumed by both instruments;
**PRESENCE is its own argument (N4): absent `when` stays UNDECLARED — the
legitimate default across all 26 kinds — and only a PRESENT, invalid
`when` is MALFORMED** (unknown mode, mode without command, non-string,
`none` without why, prefixed-reader-with-`when`). The prefixed case is
also the live repair: read_moments checks the partition BEFORE executing
anything (the marker-file hole both arms reproduced). Red-first: the
**SEVEN-case agreement test, addends enumerated (N3, FF-6): r3's three
probes (verb-mode when; mode-without-command; pure-prose when) plus the
four r2 disagreement cases (non-string when; none-without-why;
prefixed-reader-with-when; mode-without-command at the CHECKER side)** plus the six existing controls, asserting both
instruments return the same classification for every input.

**P3 — census third bucket, forward-only door stamp (D-7 rev.).** The
stamp is written by the door for **`evidence`-kind blockers ONLY (B2 — the
slot rule's own type predicate, stated: `BLOCKER_SLOT_RULES` already keys
blocker-exercise to evidence, and the stamp follows the same key, so a
later re-type to `external` cannot strand a misplaced stamp)**. **The stamp's carrier form is the EXISTING slot: `blocker-exercise:
none-yet <date>` (T-c1 — slot name, serialization and reader are lc-175's
machinery, nothing new); a re-type evidence→external REMOVES the stamp in
the SAME amendment (the re-typing door owns the clear), red-first: stamped
evidence fixture → re-typed external → zero blocker_exercise_misplaced.**
Population
figures are **DERIVED at build from `blocker_slot_census`, never restated
(B1 — the v2 "0/0/8" was falsified by this desk's own re-park ten minutes
before the lock; the persisted-count class, recorded)**. Write-set:
items.py, **verbs.py (astra-c1: `_check_blocker` and `_exercise_record`
live there, and persistence is proven at ALL THREE doors — add, park,
amend — with a per-door red-first, the lc-175/lc-179 arrangement
pattern)**, test_items.py, test_verbs.py.

**P4 — blocker type `external <event>` (D-8), with its ENDING defined
(astra-c2).** Classification, court rendering, and the resolution
contract: an external blocker CLEARS by a dated amendment naming the
arrival with its evidence (`--blocked-by NONE` + reason quoting the
event's arrival); `item ready` renders the cleared state from the
amendment; **red-first includes a REAL TRANSITION out of waiting** (a
fixture external blocker amended-with-arrival becomes schedulable), not
only the court print. Ordering against P3: **P4's specimen re-typing runs
BEFORE P3's stamp lands (B2)**. The mint-signal fire-log event (B9) rides
this part. Row-text derivation: the red-first arrangement IS a mutation of
the deriving expression, stated as such (NIT2 — a derived text cannot be
falsified by member addition, only by breaking the derivation). Write-set:
items.py, verbs.py, refusals.py, migrate.py, cli.py, firelog.py, tests,
carrier amendments by verb.

## Always-on (revised per B6/N2/N5)

The definition is the INVARIANT — any path that runs without a session
choosing it — and the carrier list is MARKED NON-EXHAUSTIVE, now including
the statusline path (`lifecycle item statusline` per render, N2's find).
**The inventory moves to the wave doc as ONE wave-level table, every
addition with its own delta (B6)**; this design contributes: the census
line split (delta: one line → one line), the external-court line (new: +1
line per external blocker in ready output), the OOV count+age line (new:
+1 line when nonzero — v2 omitted it from its own inventory, astra-c5).
Basis, stated precisely (N5): the HEALTH verdict is **this desk's
grading** of the probe artifact, its reach the INSTRUMENT-BEARING half
only; content additions rest on the inventory deltas alone, and the
behavioural surface remains purpose.md's open kill-condition watch.

## Observers

| arrow | verb | record | check | OBSERVER |
|---|---|---|---|---|
| vocabulary registered → proof-path proven | build act | vocab.py entry | the proof-path plant (P1) | `--test` per run |
| OOV instance written → surfaced, aging | any accepting verb | the dated slot line | `item check` count+oldest | the banner; drain = amendment away, count = dispositions owed |
| no-type-fits refusal → counted | the refusal itself | fire-log event w/ row detail (B9) | log grep, countable | the drain review reads it beside the OOV line |
| OOV reasons accumulate → widened or retired | mint round / disposition amendment | ledger + the amendment | the widened member's red-first | the same printed count reaching zero |

## Build conduct (N10 — once here, cited by every row-adding part)

Every new roster row obeys the repo's two admission rules: admitted on a
PAIR (real anchor + inert anchor, lc-142), and any row whose verdict is
computed from an expression an existing arrangement mutates RE-CHECKS that
arrangement before green is claimed (lc-30).

## Named non-goals (unchanged from v2, plus)

Expression not detection (the three detection failures); (m)-class
conflicts; D-10's trigger-status distinction NOT realized here — and the
deferral is now ON lc-237's effective slots, not promised (N6/astra-c6):
**lc-237's re-point is an explicit numbered step of wave construction,
actor = this desk, executed when the contract item is booked** — recorded
there because a re-point "at its booking" with no booking and no actor is
the assumed-delivery class.

## Stop/yield

Register on contact; no sweep. YIELD = proof-path findings + dated OOV
instances with their amendment-dispositions. STOP = the printed count and
oldest-age reaching zero owed — computable from the line the banner
prints; the drain act's trigger is that print (the existing pass-owed
pattern), no unowned review anywhere (B8's standard applied to this doc's
own rows).
