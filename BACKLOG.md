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

- **PARKED 2026-08-26 — `item ready` cannot evaluate an `evidence`
  blocker.** §3.1 says an evidence predicate is evaluated like a
  trigger; the trigger evaluator is §3.3/§3.4, built in stage 7
  (`lane list`), which is W1c's. Today `item ready` reports COULD NOT
  VERIFY for such a blocker. Missing evidence/decision: stage 7's
  evaluator, and whether `item ready` calls it directly or through a
  shared predicate runner. Design, decided in part: it must be ONE
  evaluator — two would disagree about the `>=2` BROKEN case first.

- **PARKED 2026-08-26 — a detector's home repo is taken from the cwd,
  not from a registry.** §3.1 says detectors register their home repo;
  the detector registry is wave 3. So `--source detector:<name>` is
  origin-checked exactly like a session add. Missing evidence: the
  registry's shape. Nothing in wave 1 depends on the answer, and the
  coarse check is not wrong today — it is narrower than the design.

- **READY 2026-08-26 — `tools/prove-rows.py` records a mutation for 16
  of 28 rows; the other 12 have none.** They are the stage 1-3 rows,
  proven by their own plant/control pair but never shown to go dark
  when the condition they name is removed. The tool lists them at the
  end of every run rather than omitting them, so the gap is visible;
  closing it is mechanical. Design, decided: one MUTATIONS entry per
  row, anchored on the single site where that row's finding is decided,
  and each must darken its row ALONE — where two rows share a decision
  site, the two entries send each row's own case down the wrong branch
  (the pattern `conservation_short`/`conservation_surplus` already
  uses). Write-set: `tools/prove-rows.py`. Verifier:
  `python3 tools/prove-rows.py` prints "rows with a recorded mutation:
  28 of 28" and exits 0. Done-criterion: no row is listed under "rows
  with NO mutation recorded".

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
