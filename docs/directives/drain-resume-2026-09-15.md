# Drain resume — successor desk kickoff (2026-09-15, ~17:20)

Successor: **dotfiles-f1** replaces dotfiles-a8 as the drain desk for
this repo. The operator closed dotfiles-a8 at ~17:19; this directive is
the state handoff. The standing protocol is UNCHANGED and lives in
`drain-kickoff-2026-09-15.md` (this directory) — read it first: conduct,
report cadence, tier defaults, and the D1/D2/D3 tool designs all live
there. All three tools are BUILT and live (`item repair --shape`, the
staged shape gate, the mint predicate lint), as is the grouped-wave
scheduler (`item waves --grouped`).

## Verified state at handoff (desk-read at base b23a6fd, clean tree, nothing unpushed)

- Carrier census: 71 live / 67 done; 63 READY, 57 schedulable.
- Write-set join: **1 lane over 47 path-valued items** — six hot files
  chain the component (cli.py, declaration.py, init.py among them), so
  work inside the lane serializes; a second desk was declined earlier on
  this same measurement (collision graph, not capacity). Re-run
  `item waves --grouped` yourself before composing any wave — this
  paragraph is a snapshot, the join is live.
- Held back, machine court (re-evaluated each pass): lc-53, lc-67, lc-94.
- Held back, operator court: **lc-127, lc-131, lc-138** — surfaced to the
  operator by the judgment desk 2026-09-15. Answers arrive as
  `decision:` lines in LEDGER.md; never resolve them yourself.

## Inherited gap

The predecessor closed without a final digest. Its last stretch added
lc-137 and lc-138, amended lc-137, and closed lc-137 DROPPED — the drop
rationale lives in lc-137's done-home block; read it there rather than
re-deriving. Nothing else is known to be in flight: tree clean, all
commits pushed.

## Channel and holds

- Report channel: `SendMessage` to **dotfiles-89 [912bce]** (the
  judgment desk). Batched digests at wave boundaries; immediate messages
  only for blockers, decisions, and milestones.
- FIRST-WAVE HOLD: build nothing until (1) the operator's first-hand
  delegation confirmation is on YOUR record and acknowledged to
  dotfiles-89, and (2) dotfiles-89 answers with the wave GO.
- One writer: this repo (lifecycle) is yours entire. Every other repo —
  dotfiles included — is outside your write set; findings about them
  travel to dotfiles-89.
