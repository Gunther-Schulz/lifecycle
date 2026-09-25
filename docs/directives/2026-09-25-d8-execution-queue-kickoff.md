# 2026-09-25: d8 execution-queue kickoff — lc-291, lc-292, then lc-289

**Desk:** lifecycle-d8 (Opus), successor desk for the answerable arc's
execution queue. **Driving desk / judgment holder:** lifecycle-64
[5d8320] (this machine, live), under the operator's delegation — INERT
until the operator states it first-hand in lifecycle-d8; the desk's ack
on its record authorizes work. **Run declaration: BUILD** (closes at
least as many items as it opens).

## Authority and order

- Operator direction, first-hand at lifecycle-64, recorded as a LEDGER
  decision line (2026-09-24, "what does the NEXT lifecycle session open
  with"): **lc-291, then lc-292, BEFORE the lc-161 after-measurement;
  lc-289 and lc-290 stand behind them.**
- lc-289's gate conditions are MET (LEDGER decision lines: stage-2
  baseline recorded at 3de8ef7; b4 wave 7 of 7): after lc-291 and
  lc-292 close, lc-289's ship set is the third item of this queue.
  lc-290 stays PARKED (waking event); the lc-161 AFTER arm is NOT in
  scope — it needs a post-ship window after lc-289 lands.
- The freeze stands (LEDGER decision, 2026-09-24): no new mechanism;
  defect repairs to shipped instruments are allowed, which is what
  lc-291 and lc-289 are; the admission bar binds any new-mechanism
  candidate (surface it, never build it).

## The briefs

The items ARE the briefs — decision-complete by construction, each with
done-criterion, write-set, and evidence. Read them through the tool,
which resolves amendments (law 8): `lifecycle item slots lc-291`,
`lc-292`, `lc-289`. Re-read at HEAD before each verifier run (law 18).

- **lc-291** — `item ratio` gains a DIVERGENCE verdict (sustained net
  growth in the (1,3) dead zone prints a FINDING); the live carrier is
  the natural red and the repaired verb MUST fire on it, quoted at
  close. PERISHABLE evidence mark: re-derive `lifecycle item ratio` at
  pickup. Sequencing note: run BEFORE lc-292 so the natural red
  (282:151, net +131 at booking) is quoted before the demotion pass
  moves any counts.
- **lc-292** — one demotion pass over every open READY item, classed
  (a) stays READY / (b) PARKED on the one shared blocker (freeze +
  admission bar + lc-161 verdict) / (c) recorded DROP; tool verbs only,
  never hand edits. PERISHABLE mark: re-derive
  `lifecycle item ready --head` at pickup. Runs before the lc-161
  after-measurement by its own criterion.
- **lc-289** — R7 ship set: re-apply 1ad96e5 (reverted at 6db4b3d) plus
  the decision-only document-frequency cap 0.05; pinned-replay
  falsifier (docs/audits/2026-09-24-lc289-replay-pinned.jsonl at
  6824bf0: 30 fires post-cap, 11/11 STRONG kept, 9/30 WEAK firing —
  any divergence is a build finding); red-first on a pinned weak and a
  strong pair; roster row + prove-rows arrangement on the lc-142 pair;
  PROVEN >= 109; per-fire token attribution and K-sweep reported beside
  the close. FAIL branch: gate withdrawn, lc-289 DROPPED, narrow freeze
  exit ends.

## Conduct

- **Arrival check** (three reads, before any scope read): base commit
  stated in the activating message from lifecycle-64;
  `git merge-base --is-ancestor <base> HEAD`,
  `git log --oneline <base>..HEAD`, `git status --porcelain`. Foreign
  commits on top, or a dirty tree: HALT and report.
- **Grounding:** the repo's reading roster gates the first write —
  docs/the-loop.md, docs/answerable-not-felt.md (and its research
  companion's correction block), docs/purpose.md. The refocus round
  record is docs/directives/2026-09-24-refocus-design-round.md
  (rev 2 + §7 judge rulings).
- **One writer:** lifecycle-d8 owns this checkout for the queue's
  duration; lifecycle-64 writes nothing here while it runs. Pushing is
  standing-authorized (CLAUDE.md Carve-outs): commit-and-push per repo
  rules; pre-push leak scan and suite run via the machine-wide hooks;
  never `--no-verify`.
- **Verify block** (CLAUDE.md): unittest suite, `lifecycle --test`,
  `tools/prove-rows.py`, `lifecycle audit`, node leak-scan. Exit codes
  taken without a pipe.
- **Report channel:** `REPORT-CHANNEL: SendMessage lifecycle-64
  [5d8320]`. Cadence: per item close at the latest; blockers, decision
  rounds, and anything reversing a recorded decision IMMEDIATELY.
  A report names the commit shas; the driving desk verifies at the
  artifact before grading. Genuinely operator-only questions (intent,
  preference, irreversible/outward) travel through lifecycle-64.
- **Desk close:** `lifecycle arc narrow` line on arcs/answerable.md in
  the established DESK CLOSE form; ESTABLISHED/OPEN discipline per the
  d9 record's convention (drain OPEN in the same act that closes).
