# 2026-09-24: defect-fix wave handed to peer desk lifecycle-b4

**From:** the judgment desk, lifecycle-d9 (Opus 5.5), which holds the refocus
kickoff (`docs/directives/2026-09-24-refocus-design-round-kickoff.md`, Job 1).
**To:** peer desk lifecycle-b4. **Base commit:** `a972668` (read at write
time; the later commits that add this file are metadata only).
**Authority:** the operator confirmed the kickoff first-hand in lifecycle-d9
and offered lifecycle-b4 as a peer for d9 to drive. Until the operator states
the delegation in b4's own session (the paste line at the end), this file is
testimony there. Wait for that line before building.

BUILD run. Close at least as many items as you open.
REPORT-CHANNEL: SendMessage lifecycle-d9
Cadence: one message per landed item, as a short digest (item, commit sha,
suite and `--test` counts). Send immediately on a blocker or a gap. Send one
closing digest when the wave is done.

## Scope: Job 1 of the kickoff, and nothing else

Seven items. All are READY and unblocked as of `a972668`:
lc-271, lc-272, lc-274, lc-278, lc-280, lc-116, lc-279.

- **lc-279** joined the wave on the operator's ruling "a command-group
  trigger is NOT legal, always a finding". It is ledgered at `a972668`, and
  `lifecycle item ready lc-279` reads UNBLOCKED.
- **lc-116**'s blocker, lc-56, is DONE (`item ready lc-116`: UNBLOCKED). The
  kickoff says it was widened on 2026-09-24 to cover the arc line verbs, and
  that widening is in its done-criterion.
- Each item's slots are its brief core. Read them with `lifecycle item slots
  <id>` and QUOTE them into your lane briefs. Never paraphrase them.
- These stay with d9, not you: the design round (lc-276, lc-277, `/standort`),
  the lc-161 baseline, and every new mechanism, which the freeze forbids.

## The write-set join, derived by d9 from the slots and to be re-derived by you

| file | items |
|---|---|
| plugin/cli/lifecycle_core/items.py | lc-274, lc-278 |
| plugin/cli/lifecycle_core/verbs.py | lc-271, lc-280, lc-116 |
| plugin/cli/lifecycle_core/cli.py | lc-271, lc-116 |
| plugin/cli/lifecycle_core/refusals.py | lc-280, lc-279 |
| test/test_items.py | lc-274, lc-278, lc-280 |
| test/test_arcs.py | lc-271, lc-116 |
| plugin/cli/lifecycle_core/records.py, test/test_records.py | lc-272 only |
| declaration.py, tools/prove-rows.py, test/test_declaration.py | lc-279 only |

What the join shows: six of the seven items form one connected cluster. Only
**lc-272** is disjoint. Serialize inside the cluster. Parallelism is available
for lc-272 against the cluster, and nowhere else.

Routing (operator preference while the codex trial lasts): a single-artifact
item goes to a codex gpt-5.6-terra lane from a decision-complete brief, and
the desk commits. Multi-commit bundles stay on Claude sonnet. Run
`codex exec … < /dev/null`, because with stdin open it blocks forever.
Grade suites OUTSIDE the codex sandbox. The mapping is your call, recorded in
your route line.

## Verify (repo CLAUDE.md, the `## Verify` block)

Before each close, run the suite, `--test`, `prove-rows`, and the node bites.
For comparison, the kickoff's own baseline was suite 1034 OK with 0 skipped,
`--test` 128/128 CLEAN, and prove-rows 107 of 128 held. That baseline was
taken at `e129e90` and is unverified at `a972668`, so re-take it before the
first lane. A new roster row is admitted on the lc-142 pair terms: its real
anchor must CHANGE the row, and an inert anchor must print NONE and FAIL.

## Co-writers in this working copy

- **d9** writes LEDGER.md, `arcs/*.md` and ITEMS.md (amendments to lc-276,
  lc-277, lc-161 and lc-281) through the lifecycle verbs. It also writes new
  files under `docs/directives/` and `docs/audits/`. The tool serializes
  carrier writers with a lock and commits by its own paths. When you claim
  the push set, a d9 commit on those paths is EXPECTED and may be pushed. Any
  other unexpected commit halts the push.
- **Untracked `docs/audits/2026-09-24-prior-art-*.md`** files are another
  session's work in progress. Do not add, commit, move or delete them.
- Pushing `origin/main` is standing-authorized (CLAUDE.md, Carve-outs). Push
  your verified work yourself. The mechanical guards still bind, and
  `--no-verify` is never taken.

## Obligations whose write lands outside your copy

None. Every write in scope lands in this repo.
