# The erosion probe — RESULTS, 2026-09-19 (lc-234)

**Status: EXECUTED per the sampling plan of record** (`docs/2026-09-19-round-decisions.md`
§D-1, item `lc-234`'s done-criterion, both riders of
`docs/audits/2026-09-19-erosion-probe-design.md`). This file reports the
measurement mechanically. **It does not close lc-234 and does not issue the
probe's verdict** — the done-criterion's pre-registered rule is applied to
the numbers below and the result is stated; whether that result closes the
item is the dispatching desk's call.

## Sample set

Per D-1: for each calendar day with at least one commit changing
`len(refusals.ROWS)` in `plugin/cli/lifecycle_core/refusals.py`, that day's
LAST such commit; HEAD always included. **6 distinct days found — under the
10-sample thinning threshold, so no thinning applied.**

Positive control (day-boundary enumeration instrument): `grep -c "^    Row("`
over `refusals.py` at HEAD returns **116**, matching `len(refusals.ROWS)`
imported directly (`python3 -c "from lifecycle_core import refusals;
print(len(refusals.ROWS))"` → 116, `len(refusals.PROSE_REST)` → 6) — pasted
here as the required control before the enumeration is believed. The
day-boundary enumeration itself used this same regex proxy over
`git show <sha>:...refusals.py` for all 52 commits touching the file (never
imported per-commit, which would need per-commit dependency resolution); the
actual per-sample counts below come from `len(...)` computed live inside each
sample's own worktree, not from the proxy.

| # | sha (short) | commit date | commit subject | roster rows | mutated/tested | PROVEN | FAILED | CNV | unmutated | tool-era note |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `7af36b4` | 2026-08-26 21:37:08 | lc-C correction: binding_slot_unbound catches an absent required key | 62 | 54 | 52 | 0 | 2 | 8 | earliest era; `roster_absent`/`repo_unresolved` anchors not yet resolved (CNV) |
| 2 | `8a5d664` | 2026-08-27 20:44:47 | lc-44, lc-48, lc-49 and the restated-row fix; bump 0.3.19 -> 0.3.20 | 73 | 63 | 63 | 0 | 0 | 10 | all mutated rows proven |
| 3 | `a94261d` | 2026-09-13 19:37:23 | lifecycle: migrate --merge refuses a source that repeats itself (lc-33) | 83 | 68 | 68 | 0 | 0 | 15 | all mutated rows proven |
| 4 | `a2ab890` | 2026-09-15 19:52:18 | lc-120: a closed body gains a forward pointer, append-only | 89 | 75 | 75 | 0 | 0 | 14 | all mutated rows proven |
| 5 | `41cee8b` | 2026-09-18 20:52:19 | lc-168: the seventh stage — WHEN a kind's write fires | 112 | 92 | 91 | 0 | 1 | 20 | `capture_dominated` now CNV (crash, honestly reported) |
| 6 | `0bb97d0` (HEAD, pinned) | 2026-09-19 16:02:12 | round: decisions D-1..D-10 — grounds body | 116 | 96 | 94 | 1 | 1 | 20 | `amend_nothing_to_amend` newly FAILED; `capture_dominated` still CNV |

**Tool-era self-consistency:** each sample ran its OWN `tools/prove-rows.py`
inside a detached worktree at that commit (never the live tree, never a
foreign era's tool). `prove-rows.py`'s own `MUTATIONS` table grew in step
with the roster across samples (54→63→68→75→92→96 tested rows), consistent
with "self-consistent per era." The `amend_nothing_to_amend` mutation entry
itself is **byte-identical** in `tools/prove-rows.py` between sample 5 and
sample 6 (`git diff 41cee8b 0bb97d0 -- tools/prove-rows.py` shows no change
in that entry) — the instrument did not change; see the REGRESSED row detail
below for what did.

**One entry is COULD-NOT-SAMPLE-free:** all 6 sampled commits carried
`tools/prove-rows.py`; none needed a could-not-sample disposition.

## Execution record

One detached worktree per sample, in the session scratchpad, one at a time,
each removed immediately after its run and verified absent from
`git worktree list` before the next was created (transcript below, §Verifier).
The live tree was never mutated by `prove-rows` (it copies `lifecycle_core`
into a temp dir per its own `lc-163` discipline) and was confirmed clean
before and after every sample.

## The four buckets

Join key: row ident, across the 6 samples in time order. **116 distinct
idents span the full history** (matches HEAD's roster size exactly — no
ident present at an earlier sample vanished by a later one; the
`closed_ref_unresolvable` / `closure_pointer_ref_unresolvable` pair looked
like a possible rename at first read and is **not one** — both are live,
distinct idents at HEAD, one proven (gained a mutation at sample 4) and one
still unmutated; checked at the artifact, not assumed).

### SURVIVED — 94 rows

Proven at an earlier sample, proven at every later sample it appears in
(through HEAD). This includes rows that started **COULD NOT VERIFY** at
sample 1 and became proven from sample 2 onward and stayed proven
(`roster_absent`, `repo_unresolved`) — an early arrangement gap closed, not
erosion, and not counted as survival "from the start," only from first proof
onward. Full per-row timelines: `verdicts-*.txt` / `parsed-*.txt` /
`join-timeline.txt` in this session's scratchpad (not committed — see
"what was NOT verified" in the closing report for the retention boundary).

Per-interval survival among the previously-proven set, computed directly
(not by feel):

| interval | proven at start | survived | FAILED | CNV (arrangement-broke) |
|---|---|---|---|---|
| `7af36b4` → `8a5d664` | 52 | 52 | 0 | 0 |
| `8a5d664` → `a94261d` | 63 | 63 | 0 | 0 |
| `a94261d` → `a2ab890` | 68 | 68 | 0 | 0 |
| `a2ab890` → `41cee8b` | 75 | 74 | 0 | 1 (`capture_dominated`) |
| `41cee8b` → `0bb97d0` (HEAD) | 91 | 90 | 1 (`amend_nothing_to_amend`) | 0 |

Four of five growth intervals show **zero** regressions and zero
arrangement-breaks among the previously-proven population; the two non-zero
events land in the two most recent intervals, one apiece.

### REGRESSED — 1 row: `amend_nothing_to_amend`

Timeline: `ABSENT → PROVEN → PROVEN → PROVEN → PROVEN → FAILED`. Proven at
samples 2-5 (2026-08-27 through 2026-09-18), FAILED at HEAD.

**This is erosion under the design doc's rider 1, not arrangement-broke**,
and the tool's own output says so in its own words rather than by my
inference: `prove-rows` reported `verdict 2/named -> 2/named`, `rows
changed: NONE`, and printed *"the row did NOT change. The condition this
mutation names is not what produces its verdict."* — the FAILED branch, not
the "anchor matches N times, not one" COULD-NOT-VERIFY branch. The anchor
resolved to exactly one line and the mutation applied cleanly; it simply
stopped being sufficient.

**Read at the artifact, not left as a bare number.** The mutation disables
`plugin/cli/lifecycle_core/verbs.py`'s original `if not updates:` guard
inside `cmd_item_amend` (line 2150 at HEAD; same line content, same anchor
text, byte-identical in `tools/prove-rows.py` between sample 5 and HEAD —
checked by diff, not assumed). Between sample 5 (`41cee8b`, 2026-09-18) and
HEAD, `verbs.py` grew a **second, later branch** in the same function
(`plugin/cli/lifecycle_core/verbs.py:2224` at HEAD) —
`if not updates and not additions:` — introduced by the conditional-slots
work landing between the two samples (`git log 41cee8b..0bb97d0 --
plugin/cli/lifecycle_core/verbs.py` shows `fa6ea7e "the conditional blocker
slots reach all three doors"` among the intervening commits) — that emits
the **identical** `[amend_nothing_to_amend]` finding text when both
`updates` and the newly-added `additions` dict are empty. So disabling the
FIRST branch (the recorded arrangement) no longer eliminates the refusal:
execution falls through to the second branch, which re-derives the same
verdict from the same "nothing to amend" condition through a different
code path the arrangement does not touch. The roster still emits the
correct refusal on real input — the CODE gained a second route to it, and
the RECORDED PROOF that this one condition (`if not updates:`) singularly
decides `amend_nothing_to_amend` no longer holds. This is exactly the
design doc's target signature: "its mutation no longer darkens the row
while the arrangement still resolves."

**Not a false positive from an ambiguous anchor.** `anchor_hits` in
`tools/prove-rows.py` refuses (COULD NOT VERIFY) when a whole-line anchor
matches other than exactly once; it did not refuse here, because the two
`if not updates:`-shaped branches at HEAD are textually different
(`if not updates:` vs. `if not updates and not additions:`) — only the
first is a literal match for the recorded anchor, so the match count is 1
and the tool proceeded to mutate and compare, correctly, per its own design.

### ARRANGEMENT-BROKE — 1 row: `capture_dominated`

Timeline: `PROVEN → PROVEN → PROVEN → PROVEN → COULD NOT VERIFY → COULD NOT
VERIFY`. This is the row named in advance in both the item's evidence slot
and this arc's Background as the expected non-erosion instance, and it
lands exactly where predicted.

Read at the artifact: `ITEMS.md:984-988` (lc-197's own body, still present
as a closed item) records that the row's mutation drives the ratio
computation into a `ZeroDivisionError`, and that **before** the fix landed
the crash was mis-scored as a PROVEN pass (`prove-rows` treated any
different post-mutation signature — including a raised exception — as "the
row changed," which is exactly the false-positive class the design doc's
"a crash is not a red" passage names). After the fix, the same crash reads
honestly as COULD NOT VERIFY. The sample boundary (`a2ab890` PROVEN →
`41cee8b` CNV) straddles that fix landing. **Correctly excluded from the
erosion count per rider 1.**

### NEVER-PROVEN — 20 rows

Rows with no mutation recorded at any sampled commit — never fired, so
never assessed either way. Not "erosion," not "health": rows this
instrument has not yet been extended to cover, listed rather than silently
dropped:

```
binding_slot_unbound            binding_slot_unbound_absent_key
binding_template_missing        binding_template_unparsable
closure_pointer_ref_unresolvable
desk_state_shape                desk_state_unknown_value
emit_site_unregistered_could_not_verify
hook_not_executable_declared    lane_new_exists
migration_readback_disagrees    record_line_unbasised_hyphen
record_route_outside_set        retire_source_laws_absent
retire_source_not_writing       retire_source_uncommitted
retire_source_unpinned_anchor   trigger_verb_unknown
verify_check_failed             workflow_binding_exists
```

### COULD-NOT-TRACK — 0 rows

No ident present at one sample was absent at a later one (checked
programmatically over the full 116×6 timeline grid, not by inspection of a
subset). The one pair that read like a possible rename at first glance —
`closed_ref_unresolvable` / `closure_pointer_ref_unresolvable` — is not: both
persist to HEAD as separate idents (see the buckets note above).

## Mechanical application of the pre-registered rule

Quoted from `lc-234`'s done-criterion, verbatim: *"regression among
previously-proven rows rising with roster size is erosion; flat survival
under a growing roster is health; dilution by new rows is neither and must
not move the figure."*

Applied to the numbers above, mechanically:

- **Dilution:** 20 rows never proven, spanning the roster's growth from 62
  to 116 rows. Per the rule, this does not move the figure, and it has not
  been allowed to: neither the SURVIVED nor REGRESSED counts include any
  never-proven row.
- **Flat survival:** 4 of 5 growth intervals (covering roster sizes 62→89,
  a 44% roster increase) show 100% survival among previously-proven rows —
  0 regressions, 0 arrangement-breaks. This is the "flat survival under a
  growing roster" pattern the rule reads as health, over that span.
- **Regression:** exactly 1 of 96 rows ever proven regressed (≈1.0%),
  occurring in the single most recent interval (roster 112→116, the
  smallest growth step measured: +4 rows, +3.6%). It is not distributed
  across the growth history — it is a single occurrence at the most recent
  point sampled.
- **Rising with roster size:** **six samples and one regression event
  cannot establish or refute a trend.** A single data point has no slope.
  The honest mechanical reading: erosion is not ABSENT (one clean instance
  exists, traced to its exact mechanism above, and it is a genuine
  same-verdict-two-code-paths case, not an artifact of this probe's own
  method) and it is not SYSTEMATIC over the sampled history (4 of 5
  intervals show none). Whether one occurrence at n=96 constitutes
  "erosion" or "noise" under the pre-registered rule is the verdict
  question, not a fact this probe can resolve by more arithmetic on 6
  points — that determination is the dispatching desk's, per the brief.

## Rider 2 — reach

This result covers the **roster channel only**: whether `tools/prove-rows.py`
+ `refusals.py`'s recorded arrangements still discriminate as the roster
grows. It says nothing about rule-corpus effects on session behaviour, and
licenses or forbids nothing about prose rules, conventions, or required
slots — per the design doc's own stated boundary. It bounds
INSTRUMENT-BEARING always-on mechanism admission only (D-5/f2's gate).

## Verifier

1. Row-counter positive control at HEAD: `len(refusals.ROWS)` → **116**,
   `len(refusals.PROSE_REST)` → **6** (python import, live tree, before any
   worktree was created).
2. `git worktree list` after the final sample: only the main tree
   (`/home/g/dev/Gunther-Schulz/lifecycle`) plus the two pre-existing
   foreign worktrees (`.../CachyOS-Setup/0125284a.../scratchpad/base-eb69b02`,
   `.../lifecycle/55c5d05e.../scratchpad/wt-old`) — none of this run's six
   `ero-<shortsha>` worktrees remained registered.
3. `git status --porcelain` in the live tree after all six runs: clean
   except this new results file (added via `git add -N`, per the write
   boundary).

## Deviations from the brief, named

- The live tree's `HEAD` moved twice during this run by another party's
  commits (`f8de2f0` "round: three design docs to the dispatchable stop",
  then `a3a9e61` "directive: successor sessions start in the lifecycle
  repo") — a foreign-commit event, not present at the base check. Both were
  checked with the brief's own instrument before continuing:
  `git diff --quiet 0bb97d0 <new-head> -- tools/prove-rows.py
  plugin/cli/lifecycle_core/refusals.py docs/audits/` returned unchanged
  (exit 0) both times, so per the brief's stated rule this proceeded rather
  than halting. The final sample used the literally pinned sha `0bb97d0`
  (as the brief and D-1 both name it explicitly), not whatever HEAD had
  moved to by the time each sample ran — an explicitly pinned commit is
  not "current HEAD."
- The done-criterion's own text ("the fraction still proving at HEAD") and
  this brief's step-3 JOIN definition (full longitudinal chain, "PROVEN at
  every later one it appears in") do not read identically on a
  dip-then-recover row; raised in the critique pass before sampling and
  resolved by following the JOIN definition, which matches the design
  doc's own T0/T1-longitudinal framing. No row in this data exhibits the
  dip-then-recover shape, so the choice was not load-bearing for this
  run's numbers, but the ambiguity itself is worth resolving in lc-234's
  own text if the item is re-run later.
