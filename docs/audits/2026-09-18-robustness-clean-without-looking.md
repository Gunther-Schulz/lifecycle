# Robustness review: which checks report CLEAN without having looked?

**Read-only, at pinned sha `09ea70a`, 2026-09-18.** Two opus lanes; lane 1
(checks) reported in full, lane 2 (the instruments themselves) still running at
the time of writing and appended when it lands. A reader finding lane 2 marked
PENDING is reading this correctly.

**Why this lens and not a general review.** This repo found the same defect in
itself five times in one day: a check reporting clean over a population it never
examined. The review was briefed on those five instances rather than on the
abstract class, and told to START FROM THE EMITTED CLEAN-VERDICT STRINGS and
walk back to what each one examined — never from the file list, because the file
list is what produced the blind spots.

**Method, carried because it decides what the findings are worth:** `git
archive` of the pinned sha into the lane's own scratchpad, every probe in a
scratch clone with `XDG_STATE_HOME` redirected. The real repo and the
machine-wide fire log were not written — which matters here, since a review of
fire-log pollution that polluted the fire log would have been this arc's own
shape one more time.

## What was found — 5 EXECUTED, each with a positive control

Ranked by whether a false clean there would hide a real defect. Two are booked
as lc-184 and lc-185; the rest went to the build desk with their grading.

| # | site | the false clean | booked |
|---|---|---|---|
| 1 | `retire.py:586` `_home_claims` | a glob home claims its suffix at ANY depth | lc-184 |
| 2 | `items.py:2472/2907` the wave join | unresolved path strings collide with nothing | lc-185 |
| 3 | `items.py:1363-1381` `check_blocker_targets` | an untypeable blocker is counted nowhere | build desk |
| 4 | `declaration.py:1184-1271` the `producer:` route | one direction is structurally unfalsifiable | build desk |
| 5 | `records.py:332-335` `record check` | a record with ZERO graded lines reads clean | build desk |

**1 — `Path.match` is RIGHT-ANCHORED.** `docs/*.md` also claims
`plugin/docs/notes.md`. Re-run at the integrating desk rather than taken on
report (python 3.14.7): two positives True, negative control
`plugin/notes.md` False. The lane's own run: both strays committed →
`sweep: CLEAN — all 91 tracked file(s) resolve to a registered kind`, exit 0;
control `vendor/stray.txt` → `FINDING [unregistered_persisted_thing]`, exit 2,
so the sweep is live and the suffix-matched pair is invisible to it
specifically. **This is the only check that asks the FILESYSTEM whether
anything sits outside the registry — invariant 1's sole world-facing
instrument — and it is blind exactly where a file is MISPLACED rather than
misnamed.** The printed denominator counts the strays as resolved.

**2 — the join's paths are never resolved.** Two items on one file, one spelled
`plguin/`, returned `[['lc-a'], ['lc-b']]` — two disjoint lanes, an instruction
to dispatch two writers onto one file. Control with correct spelling returned
one serialized lane. **The repo's own `CLAUDE.md` already carries the measured
2026-09-14 incident AND the rule that write-set paths resolve at booking.** The
lesson was written down and the mechanism was never built.

**3 — the untypeable blocker.** `classify_blocker` returns `(None, "")` for
anything unrecognised; with a prefix present that falls through both arms of the
loop. `blocked-by: lc-99999 (typo, no such id)` on a READY item →
`blocker targets: CLEAN — 4 item-id blocker(s)`, the fifth in neither the count
nor the output; the well-formed spelling correctly finds `dangling_reference`.
`check_parked_blockers` covers only PARKED. **It misses precisely the failure
its own docstring names** (lc-14, "a permanent silent park"). Second half: with
`typed` empty it returns CLEAN with NO OUTPUT — and an absent line is not
readable as a verdict.

**4 — the self-referential producer pool.** The set is built by scanning every
kind's WRITER, then `producer:` references resolve against that same set, so a
producer named in a writer can never dangle while the identical reference in a
`reader` correctly finds. An expectation derived from the artifact it grades.
It matters past its size because `--test`'s ROUTE-SET check counts `producer`
as a watched route, so the roster green and the route-set green both hold over
the hole.

**5 — the empty record.** Five headings present, ESTABLISHED and OPEN bodies
empty → `record check: CLEAN`. The module docstring names this class in its own
words — *"a record of pure prose passes every tag-shaped check ever written"* —
and `record_line_untagged` closes the prose case but not the same case with the
prose REMOVED. No line denominator is printed, so lc-172's remedy is absent at
this site.

## 4 REASONED, labelled as such and not run

- **`growth_verdict` still carries the defect `walk` repaired** (retire.py
  364-380 vs 426-439): no-home and unresolvable-home are both `continue`d
  silently, so it can return CLEAN having examined nothing, while `walk` routes
  both to could-not-verify with a reason. **Two bodies behind one contract,
  disagreeing about the case that decides whether a board reads clean** — which
  is what this repo's laws file warns about for `lane list`/`item ready`, inside
  the growth check. Bounded today: roster row only, never the CLI.
- **Conservation is a sum and its sentence is wider than a sum.** A hand-deleted
  live block plus an unrelated appended done body leaves the identity unmoved
  and shares no id, so both checks report clean. Compensating errors are
  inherent to a count identity; what is wrong is the SENTENCE. Wording, not
  math — the identity is not to be touched.
- **A PIPELINE `Trigger:` predicate makes BROKEN unreachable.** A shell pipeline
  returns the last stage's status, so a broken `find` piped to `grep -q` exits 1
  → QUIET, and a dead lane renders as a clean board — the failure the `>=2`
  mapping exists to prevent, defeated by the shell rather than by the code. NOT
  firable here (this repo declares `"lanes": []`), and this repo SHIPS THE TOOL,
  so the hazard is every declaring repo's.
- **HYPOTHESIS, latent:** the emit-site scan has no pattern for a RELAYED
  could-not-verify row name. Grepped: no such site exists at this sha. **The
  correct act is one sentence in the check's printed LIMIT paragraph, not a
  pattern for a site that does not exist** — a mechanism minted without an
  incident is the thing this repo's own admission bar refuses.

## THE PATTERN ACROSS THE FINDINGS

**Four of the nine sit inside checks whose own docstring names this exact
class.** The growth check that reported clean over 132MB; the blocker check that
misses the failure it cites by name; the record check whose docstring says pure
prose passes every tag-shaped check, and which then passes a record with no
lines at all. **Writing the lesson above the code did not put the lesson into
the code** — which is law 26's second clause measured at scale rather than
argued.

## WHAT WAS EXAMINED AND FOUND CLEAN — a result, not an omission

- **`verify.py`, all 166 lines.** Three verdicts kept apart; 126/127 routed to
  did-not-run; a timeout booked as did-not-run rather than a failure; `never`
  reported BEFORE `failed`; counts printed as `executed: R of N registered`.
  **Its stated boundary — ran is not discriminates — matches its predicate
  exactly.** Shipped the same day.
- `lane list`'s gather/render path: absent roster FINDING, unresolved repo
  FINDING, zero declared lanes stated in its own line, `--no-run`
  could-not-verify, a real tri-state.
- `judgment.py report`: zeros included for every rule; unsited and
  sited-but-unobserved both forced to could-not-verify.
- `items.py check_staged`: a real denominator, a line-number-free identity, and
  the 0-of-0 case unreachable by construction.
- `check_move_integrity` post-lc-177, and the laws/manifest checks, which
  over-fire loudly rather than passing quietly.

## COVERAGE, stated so the green is not read wider than it is

**~6,000 of the package's ~22,000 lines**, chosen by grepping emitted
clean-verdict strings and walking back.

**NOT READ:** `migrate.py` (3,263 lines — **and it emits conservation verdicts
of its own around 2689-2730**), `verbs.py`, `refusals.py`,
`tools/prove-rows.py`, `init.py`, `ledger.py`, `workflows.py`, `desk.py`,
`grammar.py`, `atomic.py`, `firelog.py`, and the whole test suite. The lane did
not run the suite or the prover, and no verdict here rests on either.

**`migrate.py` is where the next pass belongs, and it is lc-168's own file — so
that pass is owed BEFORE the migration, not after.**

## Lane 2 — PENDING

The instruments themselves: which recorded proofs prove less than they claim.
Lens: *a pair proves the refusal's AXIS and never its REACH; reach is proven by
the arm that must stay SILENT.*
