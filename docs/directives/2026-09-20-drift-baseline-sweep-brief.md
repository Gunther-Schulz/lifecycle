# Drift-trigger probe, BASELINE arm — sweep brief (handed to lifecycle-ef, 2026-09-20)

DISCOVERY. Read-only everywhere: no writes to any repo, no commits; your
outputs go in YOUR OWN scratchpad only. Judgment holder for the arc: the
driving desk lifecycle-d9 (grading, integration, booking). Composed against
lifecycle HEAD cb32a4c.

## What this is

The baseline arm of `docs/audits/2026-09-20-direction-drift-trigger-probe-design.md`
(this repo — read it FIRST, whole; its vacuous-quantity section and rider 1
bind your grading). The claim being turned from recollection into a rate:
the operator, pressing a session with "what do you think the goal is?",
usually gets a CORRECT answer, and the course then corrects.

## The sweep

Corpus: raw session JSONL under `~/.claude/projects/` (all project dirs).
INSTRUMENT LIMIT, binding: operator goal-questions are characteristically
MID-TURN interjections, which live in `queue-operation` records — the
session-search MCP's declared scope EXCLUDES those, so you read files raw
and do not use that MCP for anything you count.

Find: events where the OPERATOR asks the session to state the goal/purpose
of the current work. The operator types with heavy transposition typos —
the pattern set must be generous ("goal", "teh goal", "waht/whast/wast …
goal", "what do you t(h)ink the goal", "ziel" for German) and you then
FILTER by reading, since "goal" alone over-matches. List the final pattern
set in the report.

Noise class, named: pasted transcripts. Sessions contain `pasted_content`
blocks quoting OTHER sessions (today's lifecycle-d9 session carries pastes
of a wan2gp exchange and a non-technical one) — an event inside a paste is
counted once, in its home session, never in the pasting one.

Known positive (instrument check): a 2026-09-20 session in a non-technical
project contains the operator turn "ye a an dits a problem! … what do you
tink teh goal is?" (~15:37 local) and the session's goal-read answered next
turn, operator-confirmed "yes" (~15:38). Your pattern set must catch this
event; a sweep that misses it is a dead instrument, not an absence.

## Grading (per event — this is why the arm runs at your tier)

- goal-read correctness: CORRECT / CORRECTED-BY-OPERATOR / UNCLEAR, judged
  from the operator's own next turns, never from the answer's confidence.
- course change: did the work's direction change after the event (YES / NO
  / N-A), with the one-line basis.
- suspicion context: was the ask preceded by visible operator drift
  complaints in the same session (YES / NO) — the confound the treatment
  arm must later separate.

Rider 1 of the design doc binds: a WRONG goal restatement is its own class,
never pooled with restated-correctly-but-uncorrected.

## Output

TSV in YOUR scratchpad: project, session-short-id (8 hex max — never full
UUIDs), timestamp, pattern-hit, correctness, course-change, suspicion,
note<=120 chars. Personal-content sessions (health, private matters) are
graded like any other but QUOTED only where grading requires it, and the
report carries grades + pointers, not quotes, for those.

Report: SendMessage to lifecycle-d9 [a0e73a], parts 1/N if long. One
interim message when the event inventory stands (per-project counts, zeros
stated), then the final report: counts, the pattern set, exclusions
applied, the TSV path, the header row quoted from the file itself, and per
the read-only discipline — every claim about something outside your own
work names the read that opened it or carries "inferred, unverified"; a
missing decision, file, or value is surfaced as a gap, never bridged.

Critique pass (commissioned): before sweeping, send ONE message — which
line of this brief you find wrong or unopenable, and which two lines
contradict each other — then continue without waiting.

Start condition: begin when the operator's confirmation of this handoff is
on YOUR record (they will paste it into your session); acknowledge to
lifecycle-d9 both the brief and that confirmation.
