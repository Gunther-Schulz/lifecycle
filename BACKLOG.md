# lifecycle — backlog

Two grades. **Parked** items carry their named missing evidence or
trigger. **Ready** items are decision-complete: design decided,
verifier named, done-criterion stated, write-set named. Items leave
by commit ref, or are dropped with a one-line reason.

This carrier is this repo's own work queue and is deliberately NOT
the system the plugin builds — it migrates to `ITEMS.md` when the
tool can migrate itself.

## Open

- **PARKED 2026-08-26 — the "leak scan on the plugin repo" refusal
  row has no firing input the shipped scanner can detect.** Design
  §3.9 names a planted `/home/<user>/…` path in a template; measured
  the same day, that input scans CLEAN (exit 0) while a `s-`+8-hex
  token in the same file fires `capture-key-prefix` (exit 2). Missing
  evidence/decision: whether the scanner gains a foreign-path class
  (a change to a byte-identical copy, so it lands in
  claude-code-cache-fix first) or the row's firing input is amended
  to the token form. Both are the judgment desk's calls; reported at
  the wave-1 stage-1 hand-back.

- **PARKED 2026-08-26 — the shape check has no assigned verb in the
  design's CLI surface.** Built as `lifecycle item check`; the
  brief's D-c list does not contain it. Missing decision: the desk's
  chosen spelling, and whether the pre-commit wiring (§3.9 calls it a
  "pre-commit shape check") is the plugin's install step or the
  repo's own hook. Nothing else depends on the answer today.

- **PARKED 2026-08-26 — where the leak scan lives once it is a
  SHARED tool.** Design §3.8 lists it among PLUGIN-layer contents
  (what one install carries); brief D-a puts `tools/` at the repo
  root, outside `plugin/`. Today only the repo's own pre-push hook
  consumes it, and root `tools/` serves that. Trigger: the first
  template extraction, which is what makes the scan a thing the
  plugin must SHIP rather than a thing this repo runs.

- **PARKED 2026-08-26 — nothing creates `~/.config/lifecycle/repos`, so
  `lane list` answers `roster_absent` on this machine.** The roster is
  the router's input and its creation is outside every write boundary
  wave 1 was given (the plugin repo, six new files in
  claude-code-cache-fix, one `.gitignore` line). Measured: `lane list`
  today exits 2 with `roster_absent`; with a scratch roster listing three
  repos it prints the full longhand board, so the verb works and the file
  does not exist. Missing decision: WHO owns the roster — the plugin's
  install step, the operator's dotfiles, or a `lane register` verb the
  CLI does not have. Nothing in wave 1 depends on the answer.

- **PARKED 2026-08-26 — the done home's blocks are never shape-checked,
  so `blocker-moot:` and `superseded-by:` are unknown slots nothing
  reports.** `item check` runs `check_file` over the LIVE carrier only;
  the done home is parsed for conservation and duplicates, and both
  callers ignore `parsed.problems`. Measured: a closed body carrying
  `blocker-moot:` passes every check today. Missing decision: either the
  two annotations become real slots in `SLOTS`, or the done home gets its
  own shape check with them exempted by name. Both are design decisions
  and both change what a done body IS.

- **PARKED 2026-08-26 — `LEDGER.md` cannot carry a prose header.** The
  parser requires the first non-blank line to be `schema: <n>`; anything
  else is a shape finding before it or an unreadable line after it.
  Measured while creating claude-code-cache-fix's ledger, which is
  therefore exactly `schema: 1` — a carrier in a public repo that cannot
  say what it is for. Missing decision: whether the ledger parser gains a
  comment-line rule (`#` or `<!-- -->`), and if so whether `ledger check`
  counts comment lines in its third answer.

- **PARKED 2026-08-26 — a detector's home repo is taken from the cwd,
  not from a registry.** §3.1 says detectors register their home repo;
  the detector registry is wave 3. So `--source detector:<name>` is
  origin-checked exactly like a session add. Missing evidence: the
  registry's shape. Nothing in wave 1 depends on the answer, and the
  coarse check is not wrong today — it is narrower than the design.

- **READY 2026-08-26 — `dev-notes/` needs its OBSERVATIONS carrier.**
  Design, decided: copy dispatch-guards' four-slot form (incident +
  basis · class · pre-formulated rule text · consumer + drain seam)
  into `dev-notes/lifecycle-OBSERVATIONS.md`, same-class entries
  merging into the existing entry rather than a sibling; provenance
  `dev-notes/OBSERVATIONS-FORM.md` in that repo. Write-set:
  `dev-notes/lifecycle-OBSERVATIONS.md`. Verifier: the file exists
  and its head states the four slots. Done-criterion: the first
  instrument lesson from wave 2 lands in it rather than in a commit
  message.
