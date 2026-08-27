schema: 2
baseline: 8
added: 15
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

## lc-14
grade: READY
requirement: "lane new" writes lanes/<door>.md but deliberately does not touch the declaration, and no verb adds a lane name to an existing declaration's "lanes" list. Combined with the undeclared-file blindness booked alongside this (lc-13), the default outcome of "lane new" is a lane file that NO verb can see: the tool prints UNREGISTERED as a hint and offers no way to resolve it. Same assumed-delivery shape as init leaving carriers uncreated
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/lanes.py,plugin/cli/lifecycle_core/declaration.py,test/test_lane_new.py,cache-fix docs/directives/carrier-rework-design-2026-08-26.md
done-criterion: red-first against the current build, then: a fresh "lane new" reads QUIET in "lane list" with the declaration diff showing EXACTLY ONE added name. No new verb
evidence: L2b report (g): no such verb exists today, noted and not built. DECISION TAKEN (judgment desk 2026-08-26): NO new verb — "lane new" registers its own output, appending the name to the declaration's "lanes" list in the same run. Derivable from the same assumed-delivery reading the desk applied to init: a verb's normal output must be visible to the tool that owns it, and init already writes the declaration, so a declaration write is not a new class of act. With lc-13 closing the inverse scan, the invariant then holds in both directions with no hand step left. The "lane register" name collision is moot — no verb is minted. Section 3.8b's "written by the repo, by hand" was said of lane FILES' content, which "lane new" still only stubs, so that sentence stays true and is amended to say registration is the verb's
blocked-by: evidence L2c's declaration.py edits have landed on main (the collision is declaration.py, not cli.py — with no new verb this item adds no subparser)

## lc-15
grade: READY
requirement: An item whose `blocked-by` names another item by id is validated against nothing. A blocker of the declared form `<prefix>-<n>` pointing at an id the carrier does not contain passes `item check` CLEAN and `kind check` CLEAN — measured, by accident, with a real mistake: lc-14 was written `blocked-by: lc-15` when no lc-15 existed, and both checkers reported clean. The consequence is a PERMANENT SILENT PARK: the item never surfaces in `item ready` because it reads as blocked, and nothing ever reports that the blocker is fictional, so it can neither drain nor be noticed.
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/items.py,plugin/cli/lifecycle_core/refusals.py,test/test_items.py
done-criterion: red-first against a carrier carrying a blocker id that does not resolve: a named finding, green once the id resolves or the blocker is retyped. The three other blocker forms (`decision <q>`, `evidence <predicate>`, NONE) must NOT fire — they resolve against nothing by design, and a check that cannot tell them apart from a dangling id would fire on legitimate work.
evidence: executed: `item check` -> "CLEAN — 0 shape finding(s)", `kind check` -> "CLEAN — 19 kind(s) registered", both with the dangling id in place. REF_TYPES (declaration.py:103) is ("lane","verb","hook","session","producer","operator") — DECLARATION reference types; an item-carrier id is a different namespace and appears in none of them. DISTINCT from the refusal table's recorded `route_set_unwatched`, which is about the declaration resolver narrowed to `lane:`; this is the ITEM carrier's own blocker slot.
blocked-by: NONE

## lc-16
grade: READY
requirement: No verb reads the carrier BY goal. '--goal' occurs exactly once in the whole parser (cli.py:279, on 'item add'); 'item ready' takes only [--head] [ident] and 'item check'/'item ratio' take no arguments. So a repo can declare a closed goal set and set a goal per item, then never query by it — which breaks the consumer story for any carrier shared by more than one audience. Reported by the dotfiles desk, whose fire-rate review must read corpus entries out of a carrier that also holds machine and deploy work
goal: lean-machinery-strict-checks
write-set: plugin/cli/lifecycle_core/cli.py,plugin/cli/lifecycle_core/verbs.py,test/test_items.py
done-criterion: a goal-filtered listing exists and returns only entries carrying that goal, red-first against a carrier holding at least two goals
evidence: verified here at cf92ad9: grep '"--goal"' cli.py returns one line, :279. Peer measured it at :262 on 6badd58; the line moved, the substance holds
blocked-by: NONE

## lc-17
grade: READY
requirement: A second carrier migration has no MERGE mode. With ITEMS.md present, migrate returns FINDING [migrate_would_overwrite] (migrate.py:633) and the refusal's own text says --force would REPLACE real work with a re-derivation. So 'N old carriers into one item carrier' has no execution path at all — not a hard case, an absent one
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/migrate.py,test/test_migrate.py
done-criterion: a second --from against a populated ITEMS.md appends without touching existing entries, with conservation asserted across both sources; red-first on the current refusal
evidence: verified here at cf92ad9: migrate.py:633 emits migrate_would_overwrite. Peer measured :630-639 on 6badd58
blocked-by: NONE

## lc-18
grade: READY
requirement: A '## Done' SECTION migrates as OPEN work. CUT_SECTIONS = ('Grades',) only (migrate.py:80), so the tool models closures as a separate FILE (--from-done) while both dotfiles carriers keep theirs as a Done section of the same file; build_items then writes every migrated entry with grade NEW (migrate.py:359, comment at :346 'EVERY MIGRATED ENTRY IS OPEN'). Measured by the peer on the real files: 7 already-closed root entries and 1 corpus entry would be written back as open work. '--from-done NONE' is not the escape — both carriers genuinely have archives, so stating zero would be a false zero
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/migrate.py,test/test_migrate.py
done-criterion: a source carrying its closures as a '## Done' section migrates them to the done home, not to ITEMS.md as NEW; red-first on a fixture with both an open and a closed section, asserting the closed entries do NOT appear in the open carrier
evidence: verified here at cf92ad9: CUT_SECTIONS at :80 is ('Grades',); grade NEW hardcoded at :359. Peer measured :367 on 6badd58; the line moved, the substance holds. Counts are the peer's, not re-measured here
blocked-by: NONE

## lc-19
grade: READY
requirement: AMENDED 2026-08-26 — the original diagnosis (a _GRADE_WORD anchoring defect) was WRONG and is replaced; the measurement stands. The real cause: UNCLASSIFIED is a MISSING RULE, not a missing match. classify() matches the grade word and then does RULES.get(word); a word with no rule yields grade=None → UNCLASSIFIED. The RULES key set is BUST, CANDIDATE, FINDING, HANDOFF, NEW, OPEN, PARKED, PARTLY, POINTER, READY, RECORD — there is NO DONE and NO DROPPED. So every properly-graded closure in a source carrier is unclassified by construction. DROPPED is the sharp one: it belongs to the plugin's OWN default grade vocabulary (READY/PARKED/DONE/DROPPED) and still has no rule. Same root cause as lc-18 — the tool expects closures to arrive via --from-done, so the in-carrier closure vocabulary was never given rules
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/migrate.py,test/test_migrate.py
done-criterion: the closure vocabulary classifies rather than falling through — DONE and DROPPED at minimum, plus a declared way for a repo to map its own closure words; red-first on a fixture carrying DONE and DROPPED entries, asserting they do NOT land in the open carrier. A word with no rule must still be reported as unclassified rather than guessed at — the fix is rules, never a looser matcher
evidence: verified here at 40b9c36 by executing the module: sorted(RULES.keys()) returns the 11 words above, 'DONE' in RULES is False, 'DROPPED' in RULES is False. Counts are the peer's executed measurement over files this session did not open, CORRECTED by them post-booking: root BACKLOG.md UNCLASSIFIED 83 = DONE 76 + DROPPED 5 + ERLEDIGT 1 + RESOLVED 1; claude/BACKLOG.md 18 of 66 = DONE 14 + DROPPED 2 + TRACED 1 + EXECUTED 1 (66/18 post-dates their e3b3ebf, which added one Done entry; use these, not the earlier 65/17)
blocked-by: NONE

## lc-20
grade: READY
requirement: `lifecycle init`'s laws-file branch keys on the git AUTHOR HISTORY of CLAUDE.md, so it answers differently in any mirror, worktree or fresh clone than in the origin — and the wrong answers are plausible enough to book. The deciding rule has three branches (own repo -> CLAUDE.md; foreign tracked CLAUDE.md -> the local overlay; absent -> could-not-verify), and which one fires depends on state the operator does not think of as input: whether the file is tracked at all, and who authored the commits. Nothing in the output announces that the answer is arrangement-dependent.
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/init.py,test/test_init.py
done-criterion: init states the laws branch it took AND the evidence it read (tracked or not; the author set it found), so a wrong branch is visible in the output rather than silent; red-first against a mirror whose author history differs from its origin, showing the same repo yielding different branches with the reason named each time.
evidence: peer measurement (dotfiles desk, 2026-08-26), three runs of `lifecycle init` in a scratch mirror of dotfiles giving three different `laws` readings: (1) 'no tracked CLAUDE.md -> overlay branch', the mirror's tree untracked because a `git add -q` had silently failed; (2) 'foreign branch', the mirror's commit authored x@y; (3) the correct 'operator-only branch' once committed as the operator's own address. NOT a test defect: lifecycle's own test_init.py pins the fixture author deliberately, with a persisted user.email/user.name for what determine_laws reads and a per-commit -c override for authoring history as someone else — verified here at cf92ad9. This is the verb in the field.
blocked-by: NONE

## lc-21
grade: READY
requirement: A closed entry whose grade word is NOT at the bullet start is read as UNGRADED and migrated as OPEN work. classify() gives an entry with no leading grade word UNGRADED_RULE (migrate.py:67, applied at :219), whose grade is NEW — so it does not become unclassified and does not refuse; it silently lands in the new carrier as live work. The idiom that trips it puts a real grade word mid-title, e.g. a bullet opening with a topic and carrying DONE and a date later in the same bold span. THIS IS THE WORSE OF THE TWO MIGRATION DEFECTS: lc-19 is a loud refusal (an unclassified entry announces itself), this one is a silent wrong answer that reopens finished work.
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/migrate.py,test/test_migrate.py
done-criterion: a bullet whose grade word sits mid-title classifies by that word, red-first on a fixture drawn from the real idiom, and a closed entry never lands in the open carrier. AND the over-fire half: a bullet carrying a capitalised NON-grade word mid-title must still read as ungraded — without that arm a matcher loosened until the counts improve scores identically to one that got the distinction right.
evidence: split out of lc-19 on the reporting peer's own correction, 2026-08-26 — they had conflated two mechanisms and retracted the diagnosis while the measurement held. Verified here at 40b9c36 by executing the module: UNGRADED_RULE at migrate.py:67 is ('NEW', ...) and is assigned at :219, so an ungraded entry migrates OPEN rather than unclassified. Peer measurement, over files this session did not open: 7 root entries and 1 corpus entry, all with grade_word None, all sitting in a '## Done' section, would be written back as open work.
blocked-by: NONE

## lc-22
grade: READY
requirement: The closure MOVE has no guard against carrying a LIVE obligation into an archive. An entry can name itself the carrier for a pointer another desk still owes — 'this entry is the carrier that moves with it', its own words — and when its own work closes, the move takes that clause into the done home, which is headed for pruning at reviews. The obligation then reads as closed because its carrier is filed as closed. `item close` should grep the entry body for a forward-carrier clause and REFUSE the move with the clause quoted, so a human splits the residue out first.
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/verbs.py,plugin/cli/lifecycle_core/refusals.py,test/test_items.py
done-criterion: red-first against the L10 entry's body at dotfiles bb8edd4: `item close` refuses and quotes the carrier clause. Green once the clause is gone or the residue has its own entry. AND the over-fire arm, which decides whether this is shippable at all: an ordinary entry that merely DISCUSSES carriers or pointers in its prose must NOT be refused — a phrase-matching predicate over free prose is exactly the shape that fires on legitimate work, so the match anchors on a declared clause form rather than on words occurring anywhere in the body.
evidence: the L10 case at the dotfiles desk, 2026-08-26: the corpus-consolidation entry named itself the carrier for this desk's accretion-module residue and then closed. The peer halted the move by hand, took it to the judgment desk, and the residue was split into its own entry (dotfiles e3b3ebf) — a hand catch where a mechanism should have refused. Clause text is the peer's quotation, not read here; the entry body at dotfiles bb8edd4 is the red-first input. Booked on the judgment desk's instruction.
blocked-by: NONE

## lc-23
grade: READY
requirement: init creates the declaration and lane stubs but no carrier files, so a greenfield repo (no old carrier to migrate FROM) gets a declaration whose three carriers do not exist and kind check answers COULD NOT VERIFY forever — record: wave-3 handoff step 6, claude/records/lifecycle-wave3-handoff-2026-08-27.md
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/init.py,test/test_init.py,decision:who-seeds-greenfield-carriers
done-criterion: a greenfield repo after init has the three carriers resolvable, kind check answering CLEAN rather than COULD NOT VERIFY on them; red-first on a bare repo showing the three could-not-verifies before and their absence after
evidence: init.py:6-13 states it verbatim: "It does NOT create carrier files (ITEMS.md, ITEMS-DONE.md, LEDGER.md) — those are migrate job for a repo with an old carrier to convert FROM, or a human for a truly greenfield one ... That is a real gap in the wave-2 design this verb inherited". grep -i seed over ITEMS.md at f2c37fe returns 0 hits (positive control: carrier returns 19), so no item carried this
blocked-by: decision whether init seeds the three carriers on a greenfield repo, or the design assigns that act elsewhere — init.py argues the settled design never asked for it
