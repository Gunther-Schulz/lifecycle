schema: 2
baseline: 8
added: 1
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
