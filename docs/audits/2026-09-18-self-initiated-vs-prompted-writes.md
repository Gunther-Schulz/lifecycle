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
| L2 | dotfiles + dispatch-guards | high | **REPORTED (parts 1-2 of 3)** |
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

## THE RUBRIC WAS WRONG, AND BOTH LANES CAUGHT IT INDEPENDENTLY

**The brief defined PROMPTED as an operator message in the window. In a
desk/peer architecture that is the wrong cut — being told by a PEER is still
being told**, and the question gate 1 asks is whether a session writes without
being prompted BY ANYONE.

L2 flagged it unprompted (*"if your design question actually cares about
externally triggered vs spontaneous rather than specifically human vs the agent
itself, the 359 peer/automated-context writes are a materially different bucket
from the 126 true no-context ones"*) and L1 flagged the same fork in its own
words, from a different population, in the same hour. The desk had just sent L2
a correction saying so; the messages crossed. **Two lanes and the desk reached
one finding from three directions, which is the divergence detector working in
the agreeing direction.**

**So every number below is reported THREE ways** — operator-prompted,
peer/automated-prompted, and genuinely unprompted — and they are never averaged.

| arm | population | operator | peer/auto | unprompted | n |
|---|---|---|---|---|---|
| L1 | claude-code-cache-fix | 17% | 26% | 54% | 76 confirmed |
| L2 | dotfiles | 24.8% | 57% | 18% | 625 |
| L2 | dispatch-guards | 40% | 8% | 52% | 25 |
| L3 | wan2gp | \~54% / 42% | (two-way rubric only) | \~44% / 42% | 182 / 24 |

(L3 ran before the rubric was repaired; its population carries almost no peer
traffic, so its "self-initiated" is close to "unprompted" — but it is NOT the
same quantity and the two are not compared here as though it were.)

## THE PATTERN, AND IT IS NOT THE ONE THE DESIGN PREDICTED

**Unprompted-write rate tracks PEER DENSITY, not governance.** The peer-rich
governed population (dotfiles, 18%) sits far below the peer-poor governed one
(dispatch-guards, 52%) and below the peer-moderate one (cache-fix, 54%). The
ungoverned population sits in between. **Governance is not visibly doing
anything to this number; the presence of a peer to be told by is.**

**That is not a failure — it may be the architecture working.** In a driven
desk/peer setup, being driven BY A PEER is the intended mode, and the design's
actual claim is about OPERATOR attention, which neither scales nor
parallelizes. Read that way the governed populations say: **17-25% of carrier
writes follow an operator message; 75-83% happen without one.** That is the
autonomy claim, measured, and it is the one result here that supports the
design.

**WHAT CANNOT BE CONCLUDED, and it is the larger half:** these populations
differ on many axes at once — peer density, era, repo purpose, session length,
who was driving. This is not a controlled comparison and it cannot grade
governance. Two measurements only compare where they share a coordinate, and
these share few.

## Arm detail: L1 — claude-code-cache-fix

Mechanical detection over all 130 files (100%, a ~1s script), 1360 candidates
after **two rounds of false-positive repair caught by planted positive and
negative controls**. Manual classification of 79 sampled systematically across
the full 2026-08-05→28 range, during which **3 further false positives surfaced
that no regex could have caught** — heredocs authoring a script into scratch,
where the real write happens in a later separate call. 76 confirmed.

**The era split was requested and came back NOT MEANINGFUL, which is itself the
finding:** only 3 of 1360 candidates invoke `lifecycle item`/`ledger` at all,
all dated Aug 26-28, the tool's own build window. 99.8% of writes are
pre-toolchain `BACKLOG.md`/`JOURNAL.md`/docs edits, and this repo's September
sessions are the same tiny single-turn compliance-ping shape as the lifecycle
repo's stubs. **The toolchain's adoption moved the WORK to another repo's
sessions rather than showing up in this repo's transcripts** — the same
CWD-scatter finding that voided L1's first run, confirmed from the other side.

So there is **no before/after arm available on this machine.** The pre-treatment
baseline the operator's correction asked for cannot be constructed from
transcripts, because the population that would carry it does not exist as a
population.

## Arm detail: L2 — dotfiles + dispatch-guards

45 sessions (dotfiles 34/166, dispatch-guards 11/33), 650 writes, 222 episodes.
Parsed raw JSONL directly **including `queue-operation` records**, which the
session-search tool's own declared scope excludes — so operator mid-turn
interjections were visible to this instrument where they would not have been to
that one.

**Bug found and fixed mid-run:** the first pass matched any file under
`claude/` regardless of extension, counting `hooks/*.py` rewrites as carrier
writes. Numbers are post-fix. 159 ordinary source edits and **440 Bash
reads-only excluded — a carrier NAMED is not a carrier WRITTEN**, which is
where a sibling lane's instrument failed before catching itself.

**Its own caveats, carried rather than smoothed, and both bias the same way:**
a Bash heredoc editing `manifest.py` matched because the script's own string
literals mention `JOURNAL.md` (confirmed one instance, not exhaustively
corrected); and two episodes cite an operator GO that occurred MORE than 10
assistant turns earlier, outside the lookback, scored as no-context though the
write's own text asserts a prior prompt. **So the unprompted bucket is a soft
OVERESTIMATE and the true operator share is a few points higher than 25.4%.**
Read it as "roughly a quarter, plausibly somewhat higher", never as a point
estimate.

**Its strongest control:** a full manual read of all 9 dispatch-guards episodes
matched the automated output exactly, zero discrepancies.

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
