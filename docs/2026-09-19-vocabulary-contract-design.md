# Design v2: the registered-closed-vocabulary contract (D-3; D-7 as revised; D-8; D-10 deferred)

**Round desk, 2026-09-19, SECOND LOCK — v1's attack round (opus arm 34
findings, astra arm additive; both booked) returned 6 blocking + 8 notable
against this doc; every repair below cites its finding. v1 is in git
(f8de2f0). Status: LOCKED pending the SECOND attack pass; no build before
it returns clean-or-repaired. Builder inherits zero design freedom; the
repo's existing instances fix spelling.**

## The mechanism (unchanged in intent, narrowed in application)

Every closed VALUE vocabulary the declaration or the carriers' slots carry
is REGISTERED: name, members, the IMPORTABLE CONSUMER that renders it. Each
carries a typed OOV arm — `cannot-express: <reason>` — rendered DISTINCTLY.
Registration ON CONTACT. A recorded OOV reason is the widening signal.
**The BLOCKER slot is exempt BY RULE (V4): its contract is resolvability,
and an OOV arm there legalizes the permanent silent park `blocker_untyped`
exists to refuse. The blocker vocabulary widens only by REAL members minted
from recorded refusals — `blocker_untyped`'s refusal text gains one line:
"if no type fits, the vocabulary is the defect — book it against the
registry" — the mint signal without the park.**

## Parts

**P1 — the registry, proof through the consuming path (V6, AV1).**
`vocab.py`: `Vocabulary(name, members, oov_form, consumer)` where
`consumer` is the importable rendering function, never a prose label. The
roster row's plant per vocabulary: push an OOV value THROUGH the consumer
and assert its output differs from every member's rendering (the
discriminating pair); a vocabulary whose registration names no consumer, or
whose consumer folds the OOV value into a member rendering, FIRES. The
v1 "registry unimportable = CNV" claim is DELETED, not softened — no input
could produce it short of taking the CLI down (V12, law 22). Initial
registrations (on-contact set): reader-when states; census buckets; item
grade words; trigger-stage vocabulary; the evidence-mark vocabulary (W2's
home). Write-set: vocab.py (new), refusals.py, roster.py, test_vocab.py.

**P2 — ONE invalid-state partition, shared by both instruments (V5, f1,
astra-P2).** The valid/invalid classification of a reader `when` is
EXTRACTED into one function consumed by BOTH `_check_reader_when` and
`read_moments` — the repair is structural, not case-patching: the two
instruments cannot disagree about a state neither separately classifies.
MALFORMED (offending text quoted) covers the checker's ENTIRE invalid
partition: unknown mode, mode without command, non-string `when`, `none`
without why, and the prefixed-reader-with-`when` case. **That last one is
also a LIVE code repair shipped in the same part: `read_moments` currently
EXECUTES a predicate for a declaration the validator refuses (proven by the
attack arm's marker-file probe) — the shared partition is checked BEFORE
any execution.** Red-first: r3's three probes + the four disagreement cases
the attack round enumerated, as a NINE-case agreement test asserting the
two instruments return the same classification for every invalid input.
Write-set: declaration.py, test_declaration.py.

**P3 — census third bucket, FORWARD-ONLY door stamp (D-7 as revised on the
ledger; kills V1/V2/astra-epoch).** No dates are parsed from anywhere: the
blocker-admission door (the `_check_blocker` seam all three verbs pass
through — the wave's own three-doors lesson) writes `blocker-exercise:
none-yet <date>` at admission from the build forward. The census then
reads three states off marks alone: EXERCISED (a real exercise record) /
UNEXERCISED (the none-yet stamp — a dated, real opportunity) /
PREDATES-THE-RECORDING-DOOR (neither mark). Exact, permanent, retroactively
correct for the eight (they carry neither), and an old item gaining a NEW
evidence blocker post-build gets stamped at that admission — astra's
opportunity definition satisfied: opportunity = passage through the
stamping door. Zero new findings; lc-175's MUST-NOT-MOVE holds. Red-first:
live carrier reads 0/0/8; a fixture item admitted post-build reads the
stamp; an exercised fixture reads EXERCISED. Write-set: items.py,
test_items.py.

**P4 — blocker type `external <event>` (D-8; V3's write-set completed; NO
OOV arm here, per the exemption above).** `classify_blocker` gains the
member; rendering lands where the renderer LIVES: verbs.py's
`_blocker_state` (the realizing file — v1 named cli.py, wrong, V3/astra).
Every restatement site moves in the same change: `blocker_untyped`'s row
text ("three closed edge types" → the current member list, derived not
retyped), cli.py:557, verbs.py's three sites, items.py's two, migrate.py's
one — the enumeration from the attack arm's executed grep, re-run at build.
Specimens re-typed at build, each read via `item slots` first: lc-24,
lc-53, lc-147 (cache-fix waits), lc-66 (cross-repo layer; **lc-67 is
blocked BY lc-66** — v1's footnote reversed it, V11/astra), lc-52 (the
dotfiles export wait, parked 2026-09-19), and CANDIDATES lc-82, lc-199
(external-court shapes the v1 list closed over — graded per-item at build,
not batch-retyped). Red-first: planted `external …` renders its named
court; bare prose still refuses; the row-text derivation goes red when a
member is added without it (the V3 class caught by construction).
Write-set: items.py, verbs.py, refusals.py, migrate.py, cli.py,
test_items.py, test_verbs.py, + carrier amendments by verb.

## Always-on: the DEFINITION and the inventory (V10, astra)

**Always-on = content or execution added to any path that runs without a
session choosing it**: session-start hooks and everything their output
gains, git hooks, and any banner line. Inventory of THIS design: P3's
three-way count line and P4's external-court line both ride `item check`,
which the banner runs — always-on CONTENT, admitted on: (a) the erosion
probe's verdict (HEALTH, lc-234 closed 2026-09-19 at d645ec9) for the
instrument-bearing half, WITH its rider-2 boundary stated: the probe
bounds roster-channel instrument decay only — it says NOTHING about banner
content's effect on session behaviour, which remains purpose.md's open
kill-condition watch, not a cleared gate; (b) the content delta is two
lines replacing two lines. No new always-on EXECUTION anywhere in this
design.

## Observers (the transition table; home = this section, re-read at close)

| arrow | verb | record | check | OBSERVER |
|---|---|---|---|---|
| vocabulary registered → consumer proven | build act | vocab.py entry | the consumer-path plant (P1) | `--test` — each run IS the consultation (V7: the v1 row named lc-234's probe, which cannot see this arrow; removed) |
| OOV instance written → surfaced AND AGING | any accepting verb | the slot line | `item check` prints count WITH OLDEST AGE ("N cannot-express, oldest Kd") | the banner (existing) — an aging recording is the visible undrained signal (V8: no time-words, no unowned review; the drain act writes a disposition line on the registry entry, the retirement leg astra asked for) |
| OOV reasons accumulate → widened or retired | mint round / disposition | ledger + registry disposition line | the widened member's red-first | the kaemmung/retirement machinery reads the same count line (existing trigger, not a new pass) |

## Named non-goals (V9, astra — stated as loudly as (m)'s)

This contract EXPRESSES states; it does not DETECT the three failure modes
that silenced f1/f4/f5: cross-instrument disagreement over one input (P2
repairs the one measured instance structurally; the general comparator is
not built), the denominator question at a count's birth, and the sibling
sweep at a repair (W3 v2 carries its one instance as a continuing contract;
the general duty stays prose-rest, review-consumed). (m)-class shared-exit
conflicts: unchanged non-goal. **D-10's surviving direction (never-run vs
runs-quiet as distinct trigger states) is NOT realized by this contract**
(astra): lc-237 stays parked on this design's build and carries that as its
own first design question — recorded there at re-point, not silently
absorbed here.

## Stop/yield

Register on contact; no sweep. YIELD = consumer-proof findings + recorded
OOV instances with their dispositions. STOP = the count line's age+count
signal drained to zero dispositions owed — computable from the line the
banner already prints, no review window, no owner beyond the machinery
that already reads it.
