# Robustness review: which checks report CLEAN without having looked?

**Read-only, at pinned sha `09ea70a`, 2026-09-18.** Two opus lanes; lane 1
(checks) reported in full. **Lane 2 (the instruments themselves) NEVER
RETURNED — its run was dropped 2026-09-24 (LEDGER.md, 2026-09-24 decision for item lc-261),
its output unrecoverable; its QUESTION is re-booked as `lc-268`.** The Lane 2
heading below was filled by lc-268 on 2026-09-24.

**Why this lens and not a general review.** This repo found the same defect in
itself five times in one day: a check reporting clean over a population it never
examined. The review was briefed on those five instances rather than on the
abstract class, and told to START FROM THE EMITTED CLEAN-VERDICT STRINGS and
walk back to what each one examined — never from the file list, because the file
list is what produced the blind spots.

**Method, carried because it decides what the findings are worth:** `git
archive` of the pinned sha into the lane's own scratchpad, every probe in a
scratch clone with `XDG_STATE_HOME` redirected. The real repo and the
machine-wide fire log were not written — which matters here, since a review of
fire-log pollution that polluted the fire log would have been this arc's own
shape one more time.

## What was found — 5 EXECUTED, each with a positive control

Ranked by whether a false clean there would hide a real defect. Two are booked
as lc-184 and lc-185; the rest went to the build desk with their grading.

| # | site | the false clean | booked |
|---|---|---|---|
| 1 | `retire.py:586` `_home_claims` | a glob home claims its suffix at ANY depth | lc-184 |
| 2 | `items.py:2472/2907` the wave join | unresolved path strings collide with nothing | lc-185 |
| 3 | `items.py:1363-1381` `check_blocker_targets` | an untypeable blocker is counted nowhere | build desk |
| 4 | `declaration.py:1184-1271` the `producer:` route | one direction is structurally unfalsifiable | build desk |
| 5 | `records.py:332-335` `record check` | a record with ZERO graded lines reads clean | build desk |

**1 — `Path.match` is RIGHT-ANCHORED.** `docs/*.md` also claims
`plugin/docs/notes.md`. Re-run at the integrating desk rather than taken on
report (python 3.14.7): two positives True, negative control
`plugin/notes.md` False. The lane's own run: both strays committed →
`sweep: CLEAN — all 91 tracked file(s) resolve to a registered kind`, exit 0;
control `vendor/stray.txt` → `FINDING [unregistered_persisted_thing]`, exit 2,
so the sweep is live and the suffix-matched pair is invisible to it
specifically. **This is the only check that asks the FILESYSTEM whether
anything sits outside the registry — invariant 1's sole world-facing
instrument — and it is blind exactly where a file is MISPLACED rather than
misnamed.** The printed denominator counts the strays as resolved.

**2 — the join's paths are never resolved.** Two items on one file, one spelled
`plguin/`, returned `[['lc-a'], ['lc-b']]` — two disjoint lanes, an instruction
to dispatch two writers onto one file. Control with correct spelling returned
one serialized lane. **The repo's own `CLAUDE.md` already carries the measured
2026-09-14 incident AND the rule that write-set paths resolve at booking.** The
lesson was written down and the mechanism was never built.

**3 — the untypeable blocker.** `classify_blocker` returns `(None, "")` for
anything unrecognised; with a prefix present that falls through both arms of the
loop. `blocked-by: lc-99999 (typo, no such id)` on a READY item →
`blocker targets: CLEAN — 4 item-id blocker(s)`, the fifth in neither the count
nor the output; the well-formed spelling correctly finds `dangling_reference`.
`check_parked_blockers` covers only PARKED. **It misses precisely the failure
its own docstring names** (lc-14, "a permanent silent park"). Second half: with
`typed` empty it returns CLEAN with NO OUTPUT — and an absent line is not
readable as a verdict.

**4 — the self-referential producer pool.** The set is built by scanning every
kind's WRITER, then `producer:` references resolve against that same set, so a
producer named in a writer can never dangle while the identical reference in a
`reader` correctly finds. An expectation derived from the artifact it grades.
It matters past its size because `--test`'s ROUTE-SET check counts `producer`
as a watched route, so the roster green and the route-set green both hold over
the hole.

**5 — the empty record.** Five headings present, ESTABLISHED and OPEN bodies
empty → `record check: CLEAN`. The module docstring names this class in its own
words — *"a record of pure prose passes every tag-shaped check ever written"* —
and `record_line_untagged` closes the prose case but not the same case with the
prose REMOVED. No line denominator is printed, so lc-172's remedy is absent at
this site.

## 4 REASONED, labelled as such and not run

- **`growth_verdict` still carries the defect `walk` repaired** (retire.py
  364-380 vs 426-439): no-home and unresolvable-home are both `continue`d
  silently, so it can return CLEAN having examined nothing, while `walk` routes
  both to could-not-verify with a reason. **Two bodies behind one contract,
  disagreeing about the case that decides whether a board reads clean** — which
  is what this repo's laws file warns about for `lane list`/`item ready`, inside
  the growth check. Bounded today: roster row only, never the CLI.
- **Conservation is a sum and its sentence is wider than a sum.** A hand-deleted
  live block plus an unrelated appended done body leaves the identity unmoved
  and shares no id, so both checks report clean. Compensating errors are
  inherent to a count identity; what is wrong is the SENTENCE. Wording, not
  math — the identity is not to be touched.
- **A PIPELINE `Trigger:` predicate makes BROKEN unreachable.** A shell pipeline
  returns the last stage's status, so a broken `find` piped to `grep -q` exits 1
  → QUIET, and a dead lane renders as a clean board — the failure the `>=2`
  mapping exists to prevent, defeated by the shell rather than by the code. NOT
  firable here (this repo declares `"lanes": []`), and this repo SHIPS THE TOOL,
  so the hazard is every declaring repo's.
- **HYPOTHESIS, latent:** the emit-site scan has no pattern for a RELAYED
  could-not-verify row name. Grepped: no such site exists at this sha. **The
  correct act is one sentence in the check's printed LIMIT paragraph, not a
  pattern for a site that does not exist** — a mechanism minted without an
  incident is the thing this repo's own admission bar refuses.

## THE PATTERN ACROSS THE FINDINGS

**Four of the nine sit inside checks whose own docstring names this exact
class.** The growth check that reported clean over 132MB; the blocker check that
misses the failure it cites by name; the record check whose docstring says pure
prose passes every tag-shaped check, and which then passes a record with no
lines at all. **Writing the lesson above the code did not put the lesson into
the code** — which is law 26's second clause measured at scale rather than
argued.

## WHAT WAS EXAMINED AND FOUND CLEAN — a result, not an omission

- **`verify.py`, all 166 lines.** Three verdicts kept apart; 126/127 routed to
  did-not-run; a timeout booked as did-not-run rather than a failure; `never`
  reported BEFORE `failed`; counts printed as `executed: R of N registered`.
  **Its stated boundary — ran is not discriminates — matches its predicate
  exactly.** Shipped the same day.
- `lane list`'s gather/render path: absent roster FINDING, unresolved repo
  FINDING, zero declared lanes stated in its own line, `--no-run`
  could-not-verify, a real tri-state.
- `judgment.py report`: zeros included for every rule; unsited and
  sited-but-unobserved both forced to could-not-verify.
- `items.py check_staged`: a real denominator, a line-number-free identity, and
  the 0-of-0 case unreachable by construction.
- `check_move_integrity` post-lc-177, and the laws/manifest checks, which
  over-fire loudly rather than passing quietly.

## COVERAGE, stated so the green is not read wider than it is

**~6,000 of the package's ~22,000 lines**, chosen by grepping emitted
clean-verdict strings and walking back.

**NOT READ:** `migrate.py` (3,263 lines — **and it emits conservation verdicts
of its own around 2689-2730**), `verbs.py`, `refusals.py`,
`tools/prove-rows.py`, `init.py`, `ledger.py`, `workflows.py`, `desk.py`,
`grammar.py`, `atomic.py`, `firelog.py`, and the whole test suite. The lane did
not run the suite or the prover, and no verdict here rests on either.

**`migrate.py` is where the next pass belongs, and it is lc-168's own file — so
that pass is owed BEFORE the migration, not after.**

## Lane 2 — RUN 2026-09-24 at `a011b01` (lc-268; the original 2026-09-18 run was lost, see LEDGER.md 2026-09-24 decision for item lc-261)

The instruments themselves: which recorded proofs prove less than they claim.
Lens: *a pair proves the refusal's AXIS and never its REACH; reach is proven by
the arm that must stay SILENT.*

**Result: 47 of 128 rows prove REACH, 60 prove AXIS only, 21 have NO recorded proof.** Row count derived from `lifecycle --test --list` at `a011b01` (128 executable, 6 prose-rest out of scope); the table below covers exactly those 128, checked by set comparison at the desk (0 missing, 0 extra). Reviewer: an opus read-only lane (opus-lc268-review); `[read]` = test body read, `[name]` = graded from the test name only; (P+) the reviewer probed the near-miss and the row held, (P!) the probe exposed a defect. The reviewer did not run prove-rows or the suite.

**Grading rule.** A row's own plant/control pair is its AXIS. REACH-PROVEN needs one more arm: a control keeping a surface feature a too-wide predicate would key on and still silent; a test case firing on a far member or silent on a near-miss; or a sibling row at the same decision site firing on a far member.

**Two defects found, both reproduced at the desk with the roster's own fixtures:** D1 — a command GROUP passes as a verb (`trigger: verb item` exits 0; control `verb item clsoe` exits 2) → lc-279. D2 — `closure_home_split` fires on `./ITEMS-DONE.md` beside `ITEMS-DONE.md`, one file → lc-280.

**Most likely to hide a real defect** (reviewer's ranking): D1; D2; `records_kind_undeclared` (two checkouts sharing a basename; unprobed); `closed_ref_unresolvable` with a resolving non-commit object (`HEAD^{tree}`; unprobed); `arc_conservation` OVER side (unplanted, unprobed).

**Messages wider than any arm:** declaration_malformed (40 emit sites behind one row), arc_conservation, migration_ambiguous_closure, laws_scope_audit, conservation_surplus, blocker_predicate_broken, dangling_reference_carrier, retire_source_not_writing, unknown_slot_misplaced, and dangling_reference/trigger_verb_unknown (falsified by D1).

### REACH-PROVEN (47)

| row | basis / untested near-miss |
|---|---|
| `verify_expectation_wrong` | t_verify:165 [read] a matching ran-failed stays silent; :199 |
| `declaration_malformed` | t_declaration:1035 [read] well-formed arm accepted; t_migrate:2354-2380 far members [name] |
| `declaration_ignored` | the tracked sibling shares its one check-ignore site (prove-rows.py:24-33) = far member |
| `declaration_ignored_tracked` | same basis, reversed |
| `kind_stage_undeclared` | t_declaration:382,386 far members [name]; probe: a missing growth fires |
| `dangling_reference` | t_tend_goal:103 goal-type far member [name]; probe: verb/hook fire (but see D1) |
| `unknown_grade_read` | sibling grade_arm_malformed's control, R:1001-1008, silent on the well-formed arm |
| `arc_undispositioned` | control R:409-422 (flag existed, dispositioned) |
| `arc_shape` | t_arcs:301,533,820 far forms [name] |
| `dangling_reference_carrier` | control R:1822-1829 keeps 3 other blocker forms; t_items:927,948 [name] |
| `blocker_predicate_broken` | t_verbs:1474 exit>=2 far member, :1572 [name] |
| `blocker_predicate_satisfied_at_booking` | control R:1630-1638, same head -N shape |
| `close_over_live_blocker` | t_verbs:430 DROPPED target [name]; probe: drop over a live blocker CLEAN |
| `close_carries_pointer` | control R:1741-1746 is the over-fire probe; t_items:1631,1648 [name] |
| `blocker_softlock` | t_items:1050 chain-into-false far member [name] |
| `park_over_superseding_amendment` | t_items:1436 [name] |
| `promote_while_blocked` | t_lanes:760 an answered decision promotes [name] |
| `cost_test_veto` | t_items:1224 [read], :1239 |
| `conservation_short` | t_retire:251 [read] compacted>0 stays CLEAN |
| `conservation_surplus` | t_items:868 the pure-duplicate branch [name] |
| `evidence_unmarked` | t_items:2166 legacy carrier silent, :2145 amend door [name] |
| `decision_not_derivable_unstated` | t_items:2269,2286 [name] |
| `item_shape` | t_items:1872 each malformed shape [name] |
| `done_slot_on_live_item` | t_items:453,1897 [name only, weak] |
| `blocked_in_done_home` | t_items:566-599 prefix and other-question moot records [name] |
| `blocker_exercise_misplaced` | control R:3409-3412; t_vocab:755 |
| `not_derivable_misplaced` | control R:3430-3434; t_items:2540 |
| `ready_with_unknown_slot` | t_items:2460 [read] a migrated item's UNKNOWN stays silent |
| `kind_grew_without_exit` | t_retire:626,667,827 [name] |
| `route_set_unwatched` | t_refusals:281 an agreeing row stays silent, :290 [name] |
| `route_set_unnamed` | same |
| `schema_mismatch` | t_schema:628 live glob home, far member [name] |
| `hook_not_executable` | control R:3776-3779 keeps a 100644 non-hook file (R:3700-3704) |
| `compaction_would_strip` | t_retire:318 edited but COMMITTED compacts [name] |
| `trigger_broken` | t_lane_new:257 [read] a fresh lane reads QUIET; t_lanes:1030 |
| `lane_table_absent` | t_lanes:889 [read] the other generator is accepted |
| `verify_check_did_not_run` | t_verify:88 non-executable script, far member [name] |
| `goal_query_undeclared` | control R:4412-4418, a declared goal holding nothing; t_items:2032 |
| `desk_state_kind_undeclared` | t_declaration:168 another repo's file stays silent [name] |
| `reader_moment_malformed` | control R:4550-4558, the absent-when default |
| `roster_population_undeclared` | control R:4451-4457 diverges identically under a subset contract |
| `merge_duplicate_body` | t_migrate:830,1209 [name] |
| `move_uncommitted` | t_ledger:203 ledger door, far member [name] |
| `record_line_unbasised` | hyphen sibling fires on a present-but-wrong separator |
| `record_route_invalid` | outside_set sibling, plus the route-set check |
| `emit_site_unregistered` | the CNV sibling R:4387, far member |
| `capture_dominated` | control lands AT the 3:1 tripwire (R:3231-3233), a boundary arm |

### AXIS-ONLY (60)

| row | basis / untested near-miss |
|---|---|
| `declaration_absent` | a zero-byte lifecycle.json (must be malformed, not absent) |
| `declaration_malformed_missing_key` | public: null or "false" |
| `laws_scope_audit` | message names 4 markers, plant fires one (a dated pointer P+) |
| `laws_absent_could_not_verify` | laws path naming a directory |
| `schema_above_floor` | done-home or declaration above the floor (ledger P+) |
| `duplicate_id` | xx-1 beside xx-10 (P+) |
| `arc_exists` | arc open freeze2 while freeze is open |
| `unknown_arc` | re-closing a CLOSED slug (P+) |
| `arc_conservation` | the OVER side: text claims SHORT and OVER, only SHORT planted |
| `unknown_grade_write` | a well-formed cannot-express arm on write (P+) |
| `foreign_origin_item` | cwd in a subdirectory of the target repo; private repo with foreign cwd |
| `join_undisposed` | a write-set sharing only a path prefix (tools/harvest.mjs.bak) |
| `new_without_absence` | --absence "" |
| `cost_test_unverified` | a two-path write-set with no --hunks (P+) |
| `blocker_untyped` | decisionwhich window (no space) |
| `closed_ref_unresolvable` | a sha that resolves but is not a commit (HEAD^{tree}) |
| `blocker_unstorable` | an en dash or " - " separator |
| `dangling_reference_item` | a DONE id must stay silent; a DROPPED id on the write path must fire |
| `parked_without_typed_blocker` | an evidence blocker that parses |
| `amend_without_reason` | --reason " " |
| `promote_without_judgment` | only one of --by/--reason (P+: both fire) |
| `ready_with_unknown_slot_promote` | the word UNKNOWN inside requirement prose |
| `amend_nothing_to_amend` | --goal <its current value> (a no-op change) |
| `duplicate_id_cross_home` | xx-1 live, xx-10 done (P+) |
| `conservation_unverified` | baseline: x |
| `ledger_body` | a reason with a trailing newline (probe FIRES, debatable) |
| `closure_home_split` | ./ITEMS-DONE.md (P!: D2, lc-280) |
| `roster_absent` | roster present but empty or comments-only |
| `repo_unresolved` | a path with a trailing slash or ~ |
| `unknown_item` | item ready <id held only in the done home> |
| `unknown_source` | --source Operator |
| `new_without_typed_blocker` | --write-set UNKNOWN --blocked-by NONE |
| `ledger_shape` | a blank line before schema: |
| `unregistered_kind` | kind show item (a prefix of items) |
| `read_kind_unregistered` | kind read item |
| `migrate_would_overwrite` | only ITEMS-DONE.md present |
| `migrate_repeated_from` | --from-done X --from Y (derived to hold, cli.py:1305) |
| `migration_unclassified` | a lowercase ready |
| `migration_ambiguous_closure` | UNDONE mid-title; shape 2 claimed and unplanted |
| `merge_source_self_duplicate` | a re-imported duplicate must stay silent |
| `migration_ledger_nonzero` | a ledger holding only blank lines after its head |
| `lane_undeclared` | a non-lane lanes/README.md |
| `declaration_retired_key` | the withdrawn bound stage (probe: fires declaration_malformed instead) |
| `leak_scan_undeclared_reason` | reason: "" |
| `reference_untyped` | verb: item ready (space after the colon) |
| `open_grade_in_done_home` | DROPPED must stay silent (P+) |
| `unknown_slot_misplaced` | grade: UNKNOWN (text names grade; probe fires CNV, code 3) |
| `unregistered_persisted_thing` | an untracked stray file must stay silent |
| `record_slot_missing` | ## Moves (different case) |
| `record_now_empty` | NOW holding only a whitespace line |
| `record_line_untagged` | a blank or continuation line under ESTABLISHED |
| `record_tag_unknown` | a lowercase [verified] |
| `record_probe_missing` | probe: present and empty |
| `record_closed_undrained` | the word PENDING inside a VERIFIED basis |
| `record_closed_unpointed` | a CLOSED prose line carrying no arrow |
| `home_unresolvable` | an absent in-tree home (CLEAN by design, P+, unpinned by the row) |
| `records_kind_undeclared` | two repos with the same basename (glob keys on basename; derived, unprobed) |
| `reader_moment_broken` | predicate false (exit 1, quiet) |
| `evidence_mark_malformed` | a lowercase perishable in prose (P+) |
| `roster_population_diverges` | a listed repo spelled non-canonically (trailing slash or symlink) |

### NO-PROOF-RECORDED (21)

| row | basis / untested near-miss |
|---|---|
| `grade_arm_malformed` | reach bounded by control (well-formed arm, R:1001) |
| `hook_not_executable_declared` | reach bounded by control (plain file) |
| `verify_check_failed` | reach bounded by test (t_verify:165) |
| `binding_slot_unbound` | reach bounded by test (t_workflow_bind:295) |
| `retire_source_not_writing` | reach bounded by test (t_migrate:2147, schema-from half) |
| `record_route_outside_set` | reach bounded by sibling |
| `record_line_unbasised_hyphen` | reach bounded by sibling |
| `emit_site_unregistered_could_not_verify` | reach bounded by sibling |
| `binding_slot_unbound_absent_key` | axis only |
| `binding_template_missing` | axis only |
| `binding_template_unparsable` | axis only |
| `closure_pointer_ref_unresolvable` | axis only |
| `desk_state_shape` | axis only |
| `desk_state_unknown_value` | axis only |
| `lane_new_exists` | axis only |
| `workflow_binding_exists` | axis only |
| `retire_source_uncommitted` | axis only |
| `retire_source_laws_absent` | axis only |
| `retire_source_unpinned_anchor` | axis only |
| `trigger_verb_unknown` | DEFECT D1 (group names pass as verbs), lc-279 |
| `migration_readback_disagrees` | reach not applicable (plant is a monkeypatched writer) |
