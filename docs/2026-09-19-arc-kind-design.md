# Design v3: the ARC kinds (lc-231; D-2)

**Round desk, 2026-09-19, THIRD LOCK. r2 findings integrated (both arms);
zero touched the two-kind direction or the verb-seam core; the repairs
below are contracts, boundaries, and the one remaining design judgment
(N9, the closed-body version pin). Citations resolve per the contract v3's
header note.**

## The two kind declarations — AS DECLARATION OBJECTS (B3: prose failed
## the closed vocabularies it would be validated against; the validator is
## the author's first reader)

```json
"arcs": {
  "home": "arcs/*.md",
  "writer": "verb:arc",
  "reader": "session — via the arc status block the banner carries (A6/N8: rendered by a NEW verb `arc status`, called by the banner beside the existing four; `kind list --structure` is NOT widened — its declared contract is three counts with denominators and stays so)",
  "staleness": "beliefs by kill-condition and contradicting writes; premises re-ground at pickup",
  "exit": {"action": "move", "detail": "arc close — moves the body to arcs/closed/, writes the INDEX counters and the fire-log event"},
  "growth": "bounded-by-exit",
  "trigger": "verb arc"
}
"closed arcs": {
  "home": "arcs/closed/*.md",
  "writer": "verb:arc close",
  "reader": "session — closure archaeology",
  "staleness": "none — closed bodies are record",
  "exit": {"action": "compact", "detail": "declared now so the kind has no undeclared stage, not implemented — the done-bodies pattern verbatim"},
  "growth": "unbounded-with-reason: accrues at arc-closure rate; retention is the record role, git holds every state; no bound is CLAIMED (B3's catch on v2's false one)",
  "trigger": "none — declared why: nothing fires on a closed record (B3: the missing seventh stage)"
}
```

Per-stage EXITS live inside each arc body's `stages:` slot, not in the
kind's trigger stage (B3's third catch — the kind trigger is `verb arc`,
in TRIGGER_MODES).

## Conservation — project-scoped, travels with the repo (astra-a1, a7)

The fire log is ADVISORY ONLY (machine-local, best-effort — astra's read).
The authoritative history is **`arcs/INDEX.md`**: head counters
(baseline/opened/closed), tool-written by `arc open`/`arc close` in the
same act as the file write (law 9's one-act move discipline). Conservation:
opened − closed = live files AND closed = closed files, signs per the
repo's own convention (**fewer bodies than admissions = SHORT, the loss
side; more = OVER, recoverable** — v2 had them reversed, astra-a7).
Growth-without-exit stays a SEPARATE alarm (astra-a7: conservation is not
a flow bound): the audit's growth check gains the arc exit event —
**retire.py and firelog.py in the write-set** — so `kind_grew_without_exit`
reads arc closes the way it reads item closes.

## The version story (A1; N9 resolved — the round's one r2 design judgment)

**Live arcs carry `schema:` and enter the bump machinery; closed bodies
PIN at their closing schema as record** — the same move this repo made for
the retired backlog's citations (a line only means anything against a
fixed blob). `carrier_homes` reverses its glob exclusion for the LIVE arc
home only, and the reversal names what the exclusion protected (N9: it
kept closure records out of the rewrite path — that protection is now
explicit in the closed kind's exemption rather than implicit in a
parse-time guard). The reach change ships as its own law-25 act:
**dry-run over EVERY declared repo, the population named BY COMMAND —
`find ~/dev -name .claude/lifecycle.json` (twelve today, incl. two
throwaway clones, reported not skipped) — never a digit (B4: v2 said
"both"; law 25 says every; lc-239's own requirement records this exact
class as corrected once already). Noted as its own wave finding: the
router roster `~/.config/lifecycle/repos` lists ONE repo and is itself
incomplete — booked at wave construction.** The commit-time boundary
moves with it: **plugin/hooks/pre-commit hardcodes the three carrier
kinds and rejects glob homes — it is IN the write-set (astra-a6), and the
staged arc shape check is part of the reach act's red-first.**

## Stage exits, conduct, outward (unchanged from v2 except timing already
## repaired there): operator-judged = the `none, declared why` spelling,
## LOCKED; outward stages force it, STOP renders at entry.

## Verbs (v2's seams, plus the r2 contracts)

open · advance · narrow · verdict · premise · belief · reopen · deadline ·
yield · status (new — the banner's renderer, N8) · close. Additions:
**`arc advance` and `arc close` REFUSE while undispositioned `re-derive`
flags exist** (astra-a5: the consuming seam — a stale belief is
re-derived, or accepted-stale-with-reason, before the arc moves past it;
the disposition is a written line, cheap for legitimate work, law 11
safe). Cross-arc reach: within-arc only, DECLARED (carrier items naming a
belief id are printed and inboxed, never auto-flagged). **Deadline-lane
retirement covers advance, close, AND abandon** (astra-a8) — and the
representation is settled (astra-a2): generated lanes are FULL lane
bodies at `lanes/<arc-slug>-<deadline>.md`, the existing lane form, no
declaration-shape change; writer `arc deadline`, retirement by the three
verbs above, red-first includes an abandoned arc leaving zero lanes.
**Arc block rendering: its OWN renderer in arcs.py following items.py's
idiom — `render_block` (items.py:1034, N1: v2 named grammar.py, the
wrong-home class again) renders ITEM shape and is not a drop-in; one
spelling per kind, and the arc shape's one spelling lives in arcs.py.**

## Kill test (v2's definition, with its reach stated — astra-a4)

Fresh-context grader; one pass gates, two total failures return to the
operator. **Named residual: the arrangement covers inter-verb moments;
the event-to-verb gap (a verdict heard, the session dying before `arc
verdict`) is NOT covered and cannot be by any write seam — recording
becomes a byproduct only where a verb IS the act. purpose.md's
"every moment" is driven toward, not achieved by v1; the pilot watches
this gap's real size (its kink harvest counts event-to-record latencies
it can see).**

## The wave's real ordering hazard, held at the desk (N7)

The file-granular join CANNOT see it: lc-239's write-set is all
`other-repo:` entries. **Sequencing ruling, this desk's: the
carrier_homes reach act (law-25, every-repo dry-run) lands BEFORE lc-239
beat 1 opens any of the eight, or after beat 2 completes — never during.
Stated here because no instrument computes it.**

## Red-first (v2's set, amended): conservation plants use INDEX counters
## and the corrected signs; the consuming-seam refusal gets its own pair
## (stale flag blocks advance; dispositioned flag passes); the pre-commit
## arc-shape check goes red on a hand-mangled arc file. Build conduct: the
## contract v3's N10 line binds every new row here.

## Write-set (r2-completed)

arcs.py (new, incl. the arc renderer + `arc status`), items.py (shared
slot machinery — N1), cli.py, verbs.py, declaration.py (kinds +
carrier_homes reach), refusals.py, firelog.py (arc events), retire.py
(growth reader, astra-a7), migrate.py, plugin/hooks/pre-commit
(astra-a6), test_arcs.py, test_verbs.py (the derived table),
test_declaration.py, .claude/lifecycle.json, arcs/INDEX.md (created by
first open). Collisions: the JOIN orders file-granular lanes; the
cross-repo hazard above is the desk's (N7).

## Stop/yield (v2's, unchanged in substance; the always-on line moved to
## the wave doc's single inventory per B6 — the arc status block's delta
## is stated THERE, per open arc, bounded by the flow alarm above).
