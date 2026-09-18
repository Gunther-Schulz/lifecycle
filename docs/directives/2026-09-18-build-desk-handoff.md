# Build-desk handoff — lifecycle execution, lc-157 arc

**Written:** 2026-09-18 by the judgment desk (session `9553b0`, lifecycle-6f),
at the operator's direction. **Receiver:** `lifecycle-8c`.
**Base commit:** `0d156bf` (read at compose time; verify before building).

## The split

**The receiving desk holds EXECUTION.** It builds, tests, commits, pushes,
books closures, and routes its own dispatch lanes by the standing defaults.

**This desk holds JUDGMENT** — design decisions, the corpus/project split,
what gets mechanized and what stays prose, and the operator interface. The
design discussion continues here and does not pause for builds.

**Why the split now, stated because it is a premise that can die:** the
judgment desk went execution-heavy through 2026-09-18 (nine commits, three
dispatch lanes, a transcript study) while the design work — the one thing
needing this context — queued behind it. If the build queue empties and the
remaining work is judgment, the split has done its job and the receiver hands
back.

## What is yours to build

**Ordered, but the order is a recommendation and not a schedule.** Grade each
against the carrier, not against this list — a stored brief's premises are
as of its write date, and this one is no exception.

1. **lc-156 — the investigation-record checker.** READY, unblocked,
   decision-complete. Its done-criterion in ITEMS.md is the spec; read it
   there rather than from this paragraph.
   **A DRAFT EXISTS AND IS NOT TRACKED, DELIBERATELY** — this desk's
   half-built module `records-DRAFT-lc156.py`, parked OUT of the package so
   it would not sit uncommitted inside your write set. Its absolute path is
   in this desk's handoff MESSAGE rather than here: the path contains a
   session UUID, this repo is public, and the pre-push leak scan blocks
   exactly that (it blocked this file's first push, correctly). Treat it as
   a starting draft with
   no authority: it is unwired, untested, has no registered refusal rows, and
   would fail `--test`'s emit-site coverage as written. Take from it what
   survives your own reading and discard the rest.
   **One thing in it IS load-bearing and is not in lc-156's booked text:**
   the record format gained a `route:` token TODAY (dotfiles `c2315da`) — an
   OPEN line now names `route: ask|measure|query`. Grade against the format
   file at HEAD, not against lc-156's booking, which predates it.
2. **lc-159 is DONE** (both halves, `65ef1cd` and `96629e7`) — listed only so
   you do not re-open it.
3. **The rest of the READY set**, by your own grading.

## What is NOT yours

- **lc-158 and lc-160** are blocked on operator decisions held at this desk.
- **Corpus mints** (dotfiles `claude/modules/*`): the GO is the operator's,
  first-hand, and this desk holds that interface. Send findings here.
- **Design of the capture mechanism** (the lc-157 successor question: what
  gets captured BY CONSTRUCTION rather than by remembering). Being designed
  here. If your build surfaces evidence about it, that is exactly the kind of
  fact to send.

## Conduct

- **Report channel:** `REPORT-CHANNEL: SendMessage lifecycle-6f` — every
  decision round, every blocker, and a closing report per item. Your final
  terminal text reaches no one.
- **Cadence:** batched. Digests for routine completions; immediate messages
  for blockers, decisions, and milestones.
- **Push:** this repo is standing-authorized (CLAUDE.md `## Carve-outs`).
  Commit and push per its rules; the leak scan and full suite still bind and
  `--no-verify` is never taken.
- **Attribution:** the tool now writes it. Export
  `LIFECYCLE_COMMIT_TRAILER` with your own model and session line before any
  `lifecycle item` verb, or its commits land bare (a warning says so).
- **Verify before claiming green:** `python3 plugin/cli/lifecycle verify`
  runs the declared block and asserts EXECUTED vs REGISTERED — new today,
  and the point is that a check which did not run is COULD NOT VERIFY, never
  a pass.

## Residue this desk keeps

Obligations whose realizing write lands outside your copy stay MINE, named
here so neither of us reads the other's silence as completion:

- the dotfiles format file and any corpus module change;
- the operator-facing decisions on lc-158 / lc-160 / lc-161;
- the design write-ups in `docs/answerable-not-felt.md`.

If you find one of these needs changing, report it — do not reach across.
