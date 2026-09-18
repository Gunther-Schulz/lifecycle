# The gate-1 baseline: are carrier writes SELF-INITIATED or PROMPTED?

**Status: INCOMPLETE — one arm of four reported.** Written at the moment the
first arm landed rather than at the study's end, because the alternative was
leaving it in a session scratchpad that dies with the session. The remaining
arms are appended here as they return; a reader finding this file with arms
still marked PENDING is reading it correctly.

## Why this measurement exists

`answerable-not-felt.md` gate 1 asks whether records get written and read as
expected. The operator's correction, 2026-09-18, is what forces this arm:
*"you graded sessions that were partly already governed by the existing
lifecycle."* A write-count alone passes gate 1 while failing its actual test,
because a session writing only when told is not self-administering. So the
count splits: **a write following an operator message on that topic is
PROMPTED; one arising from the work itself is SELF-INITIATED.**

**PREDICTION REGISTERED BEFORE ANY LANE READ A LINE:** prompted dominates in
every population, matching the same day's capture-route study (an operator
asking a direct question was the single largest capture event type, ~18-20 of
~54 sampled journal events).

## Arms

| arm | population | governance | status |
|---|---|---|---|
| L1 | `-home-g-dev-Gunther-Schulz-lifecycle` | high | **VOID — wrong population, see below** |
| L2 | dotfiles + dispatch-guards | high | PENDING |
| L3 | wan2gp | none (by that repo's own declaration) | **REPORTED** |
| L4 | claude-code-cache-fix, before/after the item toolchain | mixed | PENDING |

## L1 — VOID, and the void is itself the finding

L1 returned **n=0 carrier writes over 21 of 21 non-live sessions**, and
correctly refused to report that as a 0% self-initiation rate. Verified
independently at this desk: that project directory holds 38MB across 23 files,
the two largest being the two live sessions L1 rightly excluded; the remaining
21 are ~500KB single-turn automated compliance pings. Meanwhile git shows ~150
commits/day on dates matching several of those session files, many of them
carrier writes.

**THE FINDING, which outlives the void run:** a project-directory glob is keyed
by the session's CWD, so a repo's work scatters across whichever directory each
session happened to run in. **The glob named after a repo is not the same
population as the work on that repo.** The environment corpus already carries
the neighbouring fact — that the transcripts listing is the reach-complete
enumeration of directories sessions have worked in — and this is the sharper
consequence: even that listing answers "where did sessions RUN", never "where
was this repo WORKED ON".

L1 also caught its own false positive before reporting: greps over carrier
PATHS match prose mentions as well as writes and read as a write count. That
trap was carried forward into L4's brief.

## L3 — wan2gp, the ungoverned arm

**Method.** 53 sessions, 48 with real content (>5KB); 12 sampled (25%)
systematically, every 4th by mtime across the full 2026-08-14 → 09-13 span;
34,818 events read. 281 source-code edits correctly excluded.

**Carrier finding, and it is a result rather than background:** this repo's own
CLAUDE.md states it keeps NO ledger and NO journal — `BACKLOG.md`'s `## Done`
section is its sole closure carrier. Carriers actually used: `BACKLOG.md`
(608KB of prose), `CLAUDE.md`, ad-hoc `docs/directives/*.md` and
`docs/runbooks/*.md`. Zero hits on investigation records or the
course-correction carrier.

**Results, at two grains, because the raw count is misleading** — several files
took 20-30 small Edits as ONE running test log, which is one decision and not
thirty:

| grain | n | PROMPTED | SELF-INITIATED | UNCLEAR |
|---|---|---|---|---|
| every write event | 182 | ~54% | ~44% | ~2% |
| distinct file×session episodes | 24 | 42% | 42% | 17% |

**The two grains disagree on plurality and the lane flagged that rather than
resolving it**, which is the right call: the episode grain is the more
meaningful unit and also the smaller sample, with a 17% unclear rate.

**Clearest PROMPTED**, operator verbatim: *"actually i wanto go to bed so just
book that we want to resach this next time"* → `BACKLOG.md` edit.
**Clearest SELF-INITIATED:** `docs/directives/h3-nag-vdn-branch-test.md` edited
29× as a running test-result log, with no operator message in any single edit's
window.

**Instrument grading, carried because it is why the number is usable.** Two
bugs caught and fixed BEFORE the result was trusted: (1) a naive write-regex
matched the `Co-Authored-By: ...Claude Opus 5...` git trailer, inflating 83 hits
to 338 — caught by hand-re-deriving one flagged hit against raw JSONL and
finding it was a plain commit carrying no write; (2) a case-insensitive
vendor-path exclusion zeroed out real `docs/` hits. Positive control:
two sessions independently reparsed counting only Write/Edit tool_use blocks
returned 10 and 35, matching the instrument exactly, where a naive grep gave
14 and 73 — inflated by tool_result echoes, resolved by field ROLE rather than
token presence.

**The lane's own grade, carried verbatim rather than smoothed:**
moderate-trust. Mechanical counts verified twice independently; the
prompted/self split rests on ~30 individually-read hits extrapolated by
pattern, and could shift ±10 points on a full manual read, though the lane
judges the near-even headline unlikely to overturn.

## What L3 does to the registered prediction

**Partial miss, recorded as such.** "Prompted dominates" survives weakly at the
event grain (54/44) and fails at the episode grain (42/42, a tie). A direction
surviving at 54/44 is not what the word *dominates* claimed when it was
written, and grading it as confirmed would be the agreement-drift this arc
exists to catch.

## What must NOT be concluded yet

**One arm decides nothing, and this arm is the ungoverned one.** The entire
point is the comparison: wan2gp carries unusually rich persisted guidance and no
formal toolchain, running at ~4 operator interjections per 100 turns. If the
GOVERNED populations return a LOWER self-initiation rate than this arm's
42-44%, that is evidence against the design's central claim, not for it — and
it is exactly the outcome gate 1 exists to be able to see. Any reading of that
comparison waits for L2 and L4.

**Also unmeasured, and not to be assumed:** whether self-initiated writes are
BETTER writes. This measures who caused the write, never whether it was worth
making.
