# Drain kickoff — lifecycle carrier, peer desk dotfiles-a8 (2026-09-15)

Operator decision 2026-09-15 (dotfiles-89 round, "yes go"): the
lifecycle repo's ready set drains at a delegated peer desk (opus,
session dotfiles-a8) while the dotfiles desk (dotfiles-89, this
arc's judgment holder) runs the corpus arc in parallel.

DECLARATION: BUILD run — closes at least as many items as it opens.
REPORT-CHANNEL: SendMessage dotfiles-89 [912bce]
Cadence: batched digests for routine completions; immediate for
blockers, decisions, milestones; every decision round and the close
report. Operator-constitutive decisions (intent, preference,
irreversible outward acts) travel through dotfiles-89 — the
operator's single interface for this arc.

Base commit: 2b41491 (read at compose time; tree clean, last commit
2 days ago). First act: verify per the dispatch discipline's base
check (ancestor + log + status over the write set).

FIRST-WAVE HOLD: no wave runs until the operator has stated the
delegation first-hand in the dotfiles-a8 session and that session
has acknowledged it to dotfiles-89. Until then every directive here
is testimony.

## Scope and boundaries

- The lifecycle working copy (`~/dev/Gunther-Schulz/lifecycle`) is
  the drain desk's after kickoff — dotfiles-89 makes no further
  write to it. The three commissioned items are lc-128 (D1),
  lc-129 (D2), lc-130 (D3) — ids read back from the add output;
  content anchor: each requirement line names this file's section.
  They were booked by dotfiles-89 BEFORE this handoff.
- The dotfiles repo stays dotfiles-89's. The wiring half of D1
  (pre-commit gate) is booked THERE, blocked on D1's `--staged`
  flag existing — no cross-repo write needed from either side.
- Lane routing, integration, booking: the drain desk's own, per
  standing defaults (brief-covered execution → sonnet; verdict
  stages per the reviewer default). Push per this repo's own rules.

## Priority order

Wave A (closure integrity — the classes just measured leaking in
dotfiles' carrier): **D1 checker** (unblocks the dotfiles wiring
item by its `--help` predicate), **lc-55** (one question, two
answers — root-cause candidate for the hand-written blocks),
**lc-29**, **lc-22**. Then **D2**, **D3**. Then the remaining ready
set (62 items) by the desk's own `item waves` join.

Investigation rider (hypothesis, unverified): dotfiles'
ITEMS-DONE.md carries 4+ hand-written closure blocks (df-184,
df-185, df-194, df-195, df-196) and 4 closed-still-blocked bodies
(df-151, df-192, df-196, df-210). Hypothesis: desks hand-wrote the
move because `item close` refused on unresolved blockers (the lc-55
class) or was unavailable mid-wave. Check the blocks' commit
vintages against `item close` refusal behaviour; one line in the
close report either way. The answer decides whether lc-55's fix
alone stops the leak or D1's gate is the real net.

## The three commissioned designs

Settled at mechanism level; naming, placement and idiom follow this
repo's own existing instances (its own law). Each design signs off
with its transition table below; the table's home is THIS file, and
the item bodies point here.

### D1 — `item check --staged`: commit-time shape gate, checker half

`item check` gains `--staged`: read the carrier from the git INDEX,
report only findings ABSENT at HEAD — so a commit-time gate refuses
newly introduced shape breaks without bricking on pre-existing
findings (dotfiles carries 23 today; a gate firing on those trains
`--no-verify`, the fires-on-legitimate-work class). Machine-readable
exit: 0 = no new findings (pre-existing count printed), 2 = new
findings (each block quoted), and the could-not-verify branch per
the table. The consumer is dotfiles' global pre-commit (booked
dotfiles-side); design there: in a repo carrying
`.claude/lifecycle.json`, run the check against the index; CLI
absent or erroring → WARN naming the absence, commit proceeds.

| arrow | verb | record | check (red-first) | observer |
|---|---|---|---|---|
| staged edit introduces a shape break | `item check --staged` exit 2 | findings, block quoted | fixture repo: hand-written block staged → finding; assertion failure, not error | the commit event (wiring gate) |
| finding already at HEAD, untouched | exit 0, pre-existing count printed | count line | same finding committed, staged edit elsewhere → 0 + count | same |
| declared repo, carrier unreadable | COULD NOT VERIFY, named | stderr names what is missing | fixture: declaration present, carrier absent | same |
| no `.claude/lifecycle.json` | not a lifecycle repo — gate does not apply (wiring-side skip) | none | wiring-side test | pre-commit run |

### D2 — `item repair --shape`: mechanical half of hand-written damage

Joins wrapped slot values to one line; moves amendment lines below
the fixed slots. NEVER invents: missing slots, unknown slots,
closed-still-blocked bodies are LISTED for a desk pass (judgment).
Real fixtures exist: dotfiles ITEMS-DONE.md df-196 (wrapped +
misplaced amendment), df-184/185/194/195 (missing blocked-by).
Commits its write or prints NOT COMMITTED (the lc-41 ruling,
LEDGER.md:71).

| arrow | verb | record | check (red-first) | observer |
|---|---|---|---|---|
| wrapped slot lines | joined to one line | rewritten block + verb commit | round-trip on a df-196 copy: word multiset preserved modulo joins; conservation identity unchanged | verb run; dotfiles desk pass is first consumer |
| amendment among fixed slots | moved below slots | same | df-196 fixture | same |
| missing/unknown slot, blocked-in-done | LISTED, file untouched | report lines naming block+slot | df-184 fixture → listed, file byte-identical | the desk pass reading the list |

### D3 — mint-time predicate lint on evidence blockers

`item add` and `item park` refuse an `evidence` blocker whose
predicate fails `sh -n` or exits ≥2 on one probe run, predicate
quoted in the refusal. Kills the df-237 class (prose booked as a
predicate; the item then waits forever, surfacing only as BROKEN at
read time). No new execution risk: blockers already execute on
every `item ready` pass.

| arrow | verb | record | check (red-first) | observer |
|---|---|---|---|---|
| predicate fails `sh -n` or probe exits ≥2 | mint REFUSED, predicate quoted | refusal text, nothing written | df-237's literal prose predicate as fixture → refused | the mint moment |
| predicate exits 0/1 | mint proceeds | normal add | `test -f /etc/hostname` mints | same |

## Verification

Per this repo's own battery conventions (prove-rows, selftests) and
the guard/checker devbook where applicable; the drain desk runs its
own verifies, dotfiles-89 re-verifies at integration seams it
consumes (the `--staged` predicate on the wiring item is one).
