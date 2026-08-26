schema: 2
baseline: 8
added: 5
compacted: 0

## lc-1
grade: NEW
requirement: PARKED 2026-08-26 — the "leak scan on the plugin repo" refusal row has no firing input the shipped scanner can detect — record: BACKLOG.md:14
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: BACKLOG.md:14-24
blocked-by: evidence false  # the named missing evidence in the source body

## lc-2
grade: NEW
requirement: PARKED 2026-08-26 — the shape check has no assigned verb in the design's CLI surface — record: BACKLOG.md:25
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: BACKLOG.md:25-31
blocked-by: decision the missing decision named in the source body — answer it, then re-grade

## lc-3
grade: NEW
requirement: PARKED 2026-08-26 — where the leak scan lives once it is a SHARED tool — record: BACKLOG.md:32
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: BACKLOG.md:32-39
blocked-by: evidence false  # the named missing evidence in the source body

## lc-4
grade: NEW
requirement: PARKED 2026-08-26 — nothing creates `~/.config/lifecycle/repos`, so `lane list` answers `roster_absent` on this machine — record: BACKLOG.md:40
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: BACKLOG.md:40-50
blocked-by: decision the missing decision named in the source body — answer it, then re-grade

## lc-5
grade: NEW
requirement: PARKED 2026-08-26 — the done home's blocks are never shape-checked, so `blocker-moot:` and `superseded-by:` are unknown slots nothing reports — record: BACKLOG.md:51
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: BACKLOG.md:51-60
blocked-by: decision the missing decision named in the source body — answer it, then re-grade

## lc-6
grade: NEW
requirement: PARKED 2026-08-26 — `LEDGER.md` cannot carry a prose header — record: BACKLOG.md:61
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: BACKLOG.md:61-69
blocked-by: decision the missing decision named in the source body — answer it, then re-grade

## lc-7
grade: NEW
requirement: PARKED 2026-08-26 — a detector's home repo is taken from the cwd, not from a registry — record: BACKLOG.md:70
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: BACKLOG.md:70-76
blocked-by: evidence false  # the named missing evidence in the source body

## lc-8
grade: NEW
requirement: READY 2026-08-26 — `dev-notes/` needs its OBSERVATIONS carrier — record: BACKLOG.md:77
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: BACKLOG.md:77-87
blocked-by: decision regrade: was READY under the old carrier — READY is judged, never inherited

## lc-9
grade: NEW
requirement: The declaration turns the source-scope foreign-path leak class ON, and the shipped scanner has no such scope: its foreign-path class is scoped corpus, so the declaration is honoured by nothing
goal: enforce-the-invariants
write-set: tools/absence-scan.mjs, test/absence-scan.test.mjs
done-criterion: a planted foreign home path in a tracked .md in this repo fires foreign-path and the same file without it is clean, both shown
evidence: .claude/lifecycle.json leak-scan.reason; tools/absence-scan.mjs CLASSES, the foreign-path entry scoped corpus; JOURNAL J6
blocked-by: decision the scanner is a byte-identical copy of claude-code-cache-fix's and both copies move together, so the widening lands there first

## lc-10
grade: READY
requirement: §3.11's intake cost test has three conjuncts and the third is unimplemented: cost_test() never receives the typed blocker — record: wave2 L1 booking run, 2026-08-26
goal: every-refusal-red-first
write-set: plugin/cli/lifecycle_core/verbs.py,test/test_items.py
done-criterion: an item with a typed decision blocker and a one-file write-set is graded NEW without the do-it-now ask, red-first against the current implementation
evidence: verbs.py:268 signature is cost_test(write_set, hunks, source) — no blocker parameter, and its docstring cites §3.2 not §3.11; observed live when a booking carrying a typed decision blocker was held for a hunk count
blocked-by: NONE

## lc-11
grade: READY
requirement: item add leaves a 0-byte ITEMS.md.lock in the repo root and nothing ignores it — record: wave2 L1 booking run, 2026-08-26
goal: lean-machinery-strict-checks
write-set: plugin/cli/lifecycle_core/verbs.py,decision:lock-lifetime-vs-gitignore
done-criterion: after item add, either the lock is gone or the repo's .gitignore (written by init) covers it; git status shows no stray lock
evidence: observed after four item add runs in claude-code-cache-fix: ITEMS.md.lock present, 0 bytes, git check-ignore returns no match
blocked-by: decision whether the lock is released by deletion or covered by the .gitignore init writes

## lc-12
grade: READY
requirement: Nothing checks that a lane carries its decision table — §3.3 names four parsed parts and LANE_PARTS detects three — record: wave2 L2a brief grounding, 2026-08-26
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/lanes.py,test/test_lanes.py
done-criterion: a lane file missing its decision table is a FINDING with its own refusal row, red-proven on a lane carrying Decides:/Trigger:/Ends: and no table
evidence: lanes.py:59 LANE_PARTS = ('Decides:', 'Trigger:', 'Ends:'); design §3.3 line 249 'four parsed parts' incl. 'a decision table -> workflows'. The table has no label prefix, so the startswith scan that finds the other three cannot find it.
blocked-by: NONE

## lc-13
grade: READY
requirement: Design 3.8b requires that a lane or workflow file the declaration does not list is UNREGISTERED, a finding. No verb produces it: LANES_DIR is used only to build a path from an ALREADY-DECLARED name (lanes.py:147) and no glob or iterdir over the lanes directory exists anywhere in the package. The registration invariant therefore holds in ONE direction only — a declared lane with no file is caught by read_lane, an undeclared file on disk is invisible to every verb
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/lanes.py,plugin/cli/lifecycle_core/refusals.py,plugin/cli/lifecycle_core/roster.py,test/test_lane_new.py
done-criterion: a lane file under lanes/ absent from the declaration's lanes list produces a named finding, red-first against a planted undeclared file and green after declaring it; AND test_lane_list_says_nothing_about_an_undeclared_door is INVERTED in the same change — it currently pins the pre-fix behaviour and will go red when this is fixed, which is correct but must not be read as a regression
evidence: structural: LANES_DIR used only at lanes.py:147 to build a declared name's path, zero glob/iterdir over it anywhere in the package. behavioural: lane list against a repo carrying an undeclared lanes/x.md printed 'declared lanes: 0 — EMPTY, declared rather than absent' and named neither x nor lanes/x.md
blocked-by: NONE
