schema: 2
baseline: 8
added: 57
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

## lc-24
grade: READY
requirement: test/absence-scan.test.mjs asserts the walk collects a file under a LITERAL directory list including proxy/ and that the tree holds >500 files — both are claude-code-cache-fix tree facts, so the shared test is red in lifecycle by construction — record: wave-3 step-0 Verify baseline, judgment-desk ruling carve-out 5
goal: enforce-the-invariants
write-set: test/absence-scan.test.mjs,cache-fix test/absence-scan.test.mjs
done-criterion: the expected directory set and file floor derive from the scanned repo own tree or declaration rather than a literal list, so the shared test passes in BOTH copies; red-first against a tree missing a directory the repo does declare, green on lifecycle and on the cache-fix twin
evidence: executed at f2c37fe: node --test test/absence-scan.test.mjs exits 1, 62 tests 61 pass 1 fail — "source: every UUID in a tracked SOURCE_SCANNABLE file is on the synthetic allowlist" (:743) AssertionError "the walk collected no file under proxy/". Source :756-761 loops ["test","tools","proxy","docs"] and asserts files.length > 500. lifecycle has no proxy/ (git ls-files top level: 13 entries) and 51 tracked files total
blocked-by: lc-9

## lc-25
grade: READY
requirement: item add writes the carrier and never commits it on --join new or --join merge-into: commit_paths is called only from _do_supersede, while --no-commit is advertised on the verb as though a commit were the default for every join, and neither a "committed:" nor a "NOT COMMITTED" line is printed — record: wave-3 step-0, judgment-desk GO
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/verbs.py,test/test_items.py
done-criterion: every join of item add either commits its own write by pathspec or says NOT COMMITTED, never silence; red-first by running item add --join new against a clean tree and asserting git status is clean afterwards, which fails on the current build
evidence: observed at f2c37fe: `item add --join new` for lc-23 printed "added lc-23 [READY] -> ITEMS.md" with no commit line and left " M ITEMS.md"; committed by hand by pathspec as 2e9f20c. Source: commit_paths defined verbs.py:406, called at :646 (_do_supersede) and :1222; _do_new at :656 and _do_merge at :582 have no call site. The consequence is the one commit_paths own docstring names — in a shared work tree the dirty carrier rides out under a co-writer pathspec commit
blocked-by: NONE

## lc-26
grade: READY
requirement: No verb clears a typed blocker once its decision is answered: item has only {check,add,ready,park,close,ratio}, park only SETS a blocker, and an answered decision leaves the item reading blocked forever — record: wave-3 step 0, judgment-desk ruling 2026-08-27
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/verbs.py,plugin/cli/lifecycle_core/items.py,test/test_items.py
done-criterion: a decision blocker resolves against a ledger decision line naming the same question, and item ready re-derives blocked-ness from the ledger rather than from the stored slot; red-first on an item whose decision blocker has an answering ledger line, which today still reads blocked
evidence: probed in a throwaway clone at f2c37fe: `item park lc-23 --blocked-by NONE` is refused with FINDING [parked_without_typed_blocker] ("Prose only — or nothing — was given (NONE)") and lc-23 blocked-by is unchanged; `item --help` lists exactly check, add, ready, park, close, ratio — no verb takes a blocker off. Adjacent to lc-15 permanent-silent-park shape, one slot over
blocked-by: NONE

## lc-27
grade: READY
requirement: The carrier is append-only in practice because no verb edits a block: item add is the only writer, and there is no path to clear a blocker, amend a body, or correct a slot — so every correction to a booked item is either a new item or a law-8 violation — record: wave-3 step 0, three sightings in one step
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/verbs.py,plugin/cli/lifecycle_core/cli.py,plugin/cli/lifecycle_core/items.py,test/test_items.py
done-criterion: an edit path exists that LEAVES A RECORD: an amendment is a new dated block or slot-line that supersedes, never an in-place rewrite, so law 8 and the append-only ethic both hold; red-first on a booked item needing a slot correction, which today has no verb at all
evidence: three sightings in wave-3 step 0, all executed: (1) clear a blocker — `item park lc-23 --blocked-by NONE` refused, parked_without_typed_blocker (lc-26, this items first instance); (2) amend a body — the lc-10 live-hit sighting could not be appended to lc-10 by any verb; (3) correct a slot — no verb takes a slot value. `item --help` lists exactly check, add, ready, park, close, ratio
blocked-by: NONE

## lc-28
grade: READY
requirement: An item whose `blocked-by` names another item by id is validated against nothing. A blocker of the declared form `<prefix>-<n>` pointing at an id the carrier does not contain passes `item check` CLEAN and `kind check` CLEAN — measured, by accident, with a real mistake: lc-14 was written `blocked-by: lc-15` when no lc-15 existed, and both checkers reported clean. The consequence is a PERMANENT SILENT PARK: the item never surfaces in `item ready` because it reads as blocked, and nothing ever reports that the blocker is fictional, so it can neither drain nor be noticed.
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/items.py,plugin/cli/lifecycle_core/refusals.py,plugin/cli/lifecycle_core/cli.py,test/test_items.py
done-criterion: red-first against a carrier carrying a blocker id that does not resolve: a named finding, green once the id resolves or the blocker is retyped. The three other blocker forms (`decision <q>`, `evidence <predicate>`, NONE) must NOT fire — they resolve against nothing by design, and a check that cannot tell them apart from a dangling id would fire on legitimate work. cli.py carries EXACTLY ONE added verdict in cmd_item_check, beside the existing calls and never folded into check_move_integrity, whose ok line it would shadow.
evidence: executed: `item check` -> "CLEAN — 0 shape finding(s)", `kind check` -> "CLEAN — 19 kind(s) registered", both with the dangling id in place. REF_TYPES (declaration.py:103) is ("lane","verb","hook","session","producer","operator") — DECLARATION reference types; an item-carrier id is a different namespace. Write-set corrected: no function inside the old set has BOTH item homes AND the declared prefix — check_file has live+prefix, check_move_integrity both homes no prefix, check_done_file done+prefix — so the check body fits items.py but its call site does not.
blocked-by: NONE

## lc-29
grade: READY
requirement: The carrier-side blocker check is NARROWER than the write side under ONE refusal name: items.check_blocker_targets asks only whether the blocker id EXISTS in either home, while verbs._check_blocker also refuses a blocker naming a DROPPED target — an id-blocker resolves on its target DONE, which a dropped item never reaches. So an item blocked on a dropped id passes item check and can never drain — record: lane C closing report (c) gap 3, 2026-08-27
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/items.py,plugin/cli/lifecycle_core/verbs.py,plugin/cli/lifecycle_core/refusals.py,test/test_items.py
done-criterion: the read side and the write side agree on what an item-id blocker resolves against, or the asymmetry is declared with its reason in both sites; red-first on a carrier whose blocker names a DROPPED id — today the write side refuses it and the carrier check passes it
evidence: lane C built the carrier-side check to lc-28 done-criterion exactly (id EXISTS in either home) and declined to widen it, stating the narrower reach in the row text and the check docstring rather than leaving it implied — so the assurance is no wider than its predicate. The asymmetry is real and under one refusal name (dangling_reference), which is what makes it worth a booking rather than a comment.
blocked-by: decision widen the carrier check to match the write side, narrow the write side, or declare the asymmetry intentional with its reason at both sites

## lc-30
grade: READY
requirement: The ROUTE SETS check is asymmetric: a route the refusal TEXT names but nothing watches is a FINDING (route_set_unwatched), while the reverse — the code routing a shape through a refusal whose text does NOT name it — prints a note and sets no code (roster.py:183-187, "not this check failure but is worth knowing"). So a refusal can catch more than it says, and the operator reading the finding gets a WRONG cause for their entry — record: lane A gap 1, judgment desk ruling 2026-08-27
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/roster.py,test/test_refusals.py,tools/prove-rows.py
done-criterion: a refusal whose text is narrower than what the code routes through it FAILS the ROUTE SETS check rather than noting it; red-first on exactly the lane-A state (two ambiguous-closure shapes routed through migration_unclassified, whose text names only the no-rule case), green once the text covers what it catches or the shapes get their own row
evidence: roster.py:177 computes stray = watched - full and :183-187 prints it as a note with no exits.worst call, while :188-195 makes the mirror case (missing) a FINDING. Live instance: lane A routed two NEW ambiguous-closure shapes through migration_unclassified because refusals.py was outside its write set (my brief defect), and that row text reads "an entry whose grade word no rule covers" — false for those entries, which HAVE a grade word, mid-title
blocked-by: evidence the migration_ambiguous_closure roster row exists — lane B builds it; making stray FAIL before that row lands would fire on the legitimate interim state lane A was forced into

## lc-31
grade: READY
requirement: A repeated --from silently discards the first source: build_parser().parse_args(["migrate","--from","A.md","--from","B.md"]) yields from_carrier="B.md" with no warning. argparse overwriting is a silent wrong answer at the migration entry point — the caller believes two sources were read and one was — record: lane B gap 1, judgment desk ruling 2026-08-27
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/cli.py,test/test_migrate.py
done-criterion: a second --from in ONE invocation REFUSES with "one --from per invocation; use --merge for a second source" rather than overwriting; red-first on the executed two---from parse, and the single---from invocation unchanged
evidence: executed by lane B: build_parser().parse_args(["migrate","--from","A.md","--from","B.md"]) returns from_carrier="B.md" — the first source is discarded with no output. Distinct from lc-17 merge mode, which is a second INVOCATION; this is one invocation naming two sources
blocked-by: NONE

## lc-32
grade: READY
requirement: A repo copy placed under a Claude Code scratchpad fails two absence-scan tests for a reason belonging to the ARRANGEMENT, not the code: every scratchpad path contains the session UUID, and the scan asserts over the checkout own root path, so capture-uuid fires on the copy location. A lane that does not check its old-side self-check first sees two extra reds and may FIX them, silencing a correct instrument — record: lane B2, 2026-08-27
goal: enforce-the-invariants
write-set: CLAUDE.md,decision:procedural-note-or-scan-scope-fix
done-criterion: the Verify section states that an old-side or scratch copy of this repo goes at a UUID-free path, with the measured control quoted; OR the scan stops asserting over the checkout own root path. Red-first is already in hand: the same commit copied to two paths must give 62/59/3 under a UUID path and 62/61/1 without
evidence: lane B2 single-variable control, executed 2026-08-27: same commit, same cp -a, ONLY the path differing. Under a scratchpad path (contains session UUID) node --test gives tests 62 / pass 59 / fail 3 — :743 (lc-24) plus :973 "foreign-path: a path under THIS REPO own root does not fire" and :1002 (actual [capture-uuid,foreign-path] vs expected [foreign-path]). At /tmp/lcb2plain/old, no UUID in the path: 62 / 61 / 1, :743 only. Found because devbook step 2 requires the old-side self-check GREEN before any red from it is trusted
blocked-by: decision a procedural note in the Verify section, or narrowing the scan so it does not assert over its own checkout root

## lc-33
grade: READY
requirement: merge_duplicate_body catches a body already present in the HOMES, but not a source that repeats ITSELF — two entries sharing one headline inside a single incoming carrier pass the refusal and both land. The row states its own narrower reach, so the assurance is not wider than the predicate, but the gap is real — record: lane B3 closing report (c) gap 1, 2026-08-27
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/migrate.py,test/test_migrate.py
done-criterion: a --merge source carrying two entries with the same headline REFUSES, red-first on a fixture built that way; and the existing arms stay green — a body already in the live home, a body already in the CLOSED home, and a non-duplicate merge
evidence: lane B3 built merge_duplicate_body scoped to bodies already in the homes and declined to widen it unasked, stating the reach in the row text. Its plant/control differ in ONE WORD of an existing headline and the whole run refuses, nothing written — because a merge is not idempotent and a partial append would leave the carrier half-merged
blocked-by: NONE

## lc-34
grade: READY
requirement: A two-run merge has an UNENFORCED precondition: both runs must write to the SAME --report path, or the provenance chain silently keeps only the last source. The pin keys on the report path, so a merge writing to a fresh path finds no prior report to carry forward and the earlier sources blob lines are simply absent — no warning, no could-not-verify — record: measured at step 4, 2026-08-27
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/migrate.py,test/test_migrate.py
done-criterion: a --merge run whose --report path carries no prior report for the EXISTING carrier says so — could-not-verify or an explicit note that earlier sources pins are not carried — rather than writing a report that silently documents one source; red-first on the measured pair below
evidence: measured 2026-08-27 on the wave-2 blobs with tool 9e33c81. DIFFERENT report paths (root -> reports/root.md, merge -> reports/merged.md): merged.md carries ONE source-blob line, (claude/BACKLOG.md) only; the root line is absent and nothing says so. SAME report path (both -> reports/M.md): BOTH lines present, (claude/BACKLOG.md) and (BACKLOG.md). So the carry-forward lane B3 built works exactly as reported; what is missing is any signal when the precondition is not met
blocked-by: NONE

## lc-36
grade: READY
requirement: migrate TRUNCATES the requirement slot at a fixed ~277 chars with an ellipsis, then appends " — record: <carrier>:<line>" — measured 23 of 133 items in the dotfiles migration; the full body survives only in the source carrier, so the truncation is a silent information loss the conservation identity does not see
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/migrate.py,test/test_migrate.py
done-criterion: either the full requirement body travels into the item, or the slot says TRUNCATED and carries its source range explicitly; red-first on a source entry longer than the cut width, asserting the item is not silently shortened
evidence: wave-4 desk, executed 2026-08-27 over dotfiles/ITEMS.md: 23 of 133 requirement lines carry the mid-sentence ellipsis at len 277-278 (df-2, df-3, df-8 sampled and read in full). All 133 evidence slots are line-range pointers into the old carriers (85 BACKLOG.md, 48 claude/BACKLOG.md), which is what makes the loss recoverable TODAY and unrecoverable once those ranges stop resolving
blocked-by: decision does the full body travel into the slot, or does the slot declare itself TRUNCATED with its range

## lc-37
grade: NEW
requirement: No sweep has been run for items currently MIS-UNBLOCKED by an existing moot ledger line — the G4 fix corrects the reader, but any item whose board reading changes at HEAD is unaudited; residue of the G4 lane, which fixed the mechanism and correctly declined the carrier audit as the desk-s
goal: enforce-the-invariants
write-set: UNKNOWN
done-criterion: every live item whose decision blocker resolved against a moot line before 9800163 is listed with its new board reading, and each is either genuinely blocked or genuinely unblocked by a named answer
evidence: G4 closing report slot (g), lifecycle 9800163: "Whether any OTHER live item in the real ITEMS.md is currently mis-unblocked by an existing moot line: NOT swept." The fix landed in ledger.py/verbs.py; the carrier was deliberately untouched by that lane
blocked-by: evidence the sweep has not been run over any real carrier; which carriers are in scope (lifecycle ITEMS.md, dotfiles ITEMS.md, cache-fix ITEMS.md) is the first thing it must decide

## lc-38
grade: READY
requirement: migrate writes each item an `evidence:` LINE-RANGE pointer into a LIVING file, so every pointer below any later edit silently goes stale — the anchor rule (a check anchored to mutating state) applied to the migrations own output
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/migrate.py,test/test_migrate.py
done-criterion: a pointer survives an edit ABOVE its target, or says it cannot: anchor on something immutable (source blob sha plus range, or the entrys own headline text) and red-first by inserting lines above a pointed entry and asserting the pointer still resolves to the same body
evidence: measured by the wave-4 desk 2026-08-27 over dotfiles: 84 of 85 BACKLOG.md pointers land exactly 2 lines early; the one that does not is the single entry above the edit. Mechanism verified at the commit: 4959d2d added 3 lines and removed 1 (+2 net) INSIDE the first entry, shifting every entry below it. Consequence measured, bounded: the enumeration lanes read windows 2 lines short at the tail, and 2 of 84 entries (df-14, df-47) lost their Done-criterion/Verifier line to it
blocked-by: decision anchor on the source blob sha plus range, or on the entry headline text, or declare the pointer approximate and have readers search near it

## lc-39
grade: READY
requirement: There is NO path from NEW to READY: grade is written once at admission (verbs.py:526), item amend REFUSES --grade, and item ready PROMOTES NOTHING — an item admitted NEW can never be graded READY however complete its slots later become, so the carriers head is empty by construction
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/verbs.py,plugin/cli/lifecycle_core/cli.py,test/test_lanes.py,tools/prove-rows.py
done-criterion: an item whose slots were completed by amendment can be graded READY by an explicit desk act recording who judged it and why, and item ready --head then lists it; red-first on the dotfiles state — 133 items with full slots, grade NEW, head reporting 0 schedulable
evidence: wave-4 desk 2026-08-27, after the dotfiles grade pass: 329 slots filled across 131 items, then item ready --head over 135 live items printed "head: 2 READY, 0 schedulable now"; the only READY items are ones BORN complete (df-134, df-135). df-1 after amendment: "grade is NEW, not READY. THIS VERB PROMOTES NOTHING". Source: verbs.py:526 sits in the add path, no other verb writes a grade
blocked-by: decision an explicit promotion act (law 10: READY is judged, never inherited) versus re-deriving grade from the amendment-resolved slots at read time — the latter makes READY automatic, which law 10 forbids, so the promotion act is the recommended shape

## lc-41
grade: READY
requirement: Not every carrier-writing verb commits its own write or says NOT COMMITTED. lc-25 fixed item add joins; the invariant it rests on is wider and unenforced: a carrier write left uncommitted rides out under a co-writer pathspec commit, which is the absorption one-writer-per-copy exists to prevent
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/verbs.py,plugin/cli/lifecycle_core/lanes.py,plugin/cli/lifecycle_core/workflows.py,plugin/cli/lifecycle_core/desk.py,plugin/cli/lifecycle_core/init.py,plugin/cli/lifecycle_core/ledger.py,test/test_lanes.py
done-criterion: every verb that writes a declared carrier either commits by pathspec or prints NOT COMMITTED with its reason; red-first per verb against the old binary, and the enumeration derived from the RUNNING parser rather than restated, so a verb added later is covered by construction
evidence: observed 2026-08-27 by the wave-4 desk: ledger add decision left M LEDGER.md in the dotfiles tree and printed nothing, while item add and item amend commit theirs. SWEEP, derived by reading the parser (every cmd_* whose body or whose called helper writes a carrier): commits today = item promote, item amend, item close; silent today = desk state, init, lane new, item park, workflow bind, ledger add, migrate. THE SWEEP OWN LIMITS, measured not assumed: it marks item add as NOT committing, which is a FALSE NEGATIVE (observed committing lc-35) because the commit sits in the helper, and its helper match collides with ordinary list append in cmd_test and item head. So the list above is a starting set, not the verdict; the item first step is the precise per-verb enumeration from the running parser
blocked-by: decision does every carrier verb COMMIT, or do the read-only-ish ones (desk state, item head) fall outside the invariant, and is migrate exempt because its whole output is a dry-run artifact

## lc-42
grade: READY
requirement: Closing an item that carries APPENDED lines (amendments, and now promotions) produces a done-home shape finding: item close writes blocker-moot: onto the moved body AFTER those lines, and the ordering check counts the closed-body slots as part of its FIXED run, so an ordinary close reads as an appended line among the fixed slots
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/items.py,test/test_items.py
done-criterion: closing an amended or promoted item leaves the done home CLEAN, while a genuinely misplaced appended line still fires; red-first on the two real bodies already in ITEMS-DONE.md (df-75, df-64) and a two-arm proof that the narrower predicate still catches the real defect
evidence: DESIGN, from the B1 lane measurement rather than a guess: the fixed run is SLOTS, never SLOTS + DONE_ONLY_SLOTS. The closed-body slots are themselves APPENDED (item close writes blocker-moot: onto a body it has already moved), so counting them as fixed is what turns an ordinary close into a finding; and _resolve_amendments own docstring rationale is about a superseding line sitting above the value it supersedes, which blocker-moot: does not do. MEASURED BOTH ARMS by the B1 lane on its own promotion line kind: with the narrower predicate the same close is CLEAN and the real defect still fires, proven by moving a promotion line above blocked-by: and watching it fire. Observed by the desk n=2 in the live carrier: ITEMS-DONE.md df-75 and df-64, both after the wave-4 grade pass amended them
blocked-by: NONE

## lc-43
grade: READY
requirement: WAVE 5 HEAD, the TRANSITION PASS (operator GO 2026-08-27): the design specified states and refusals thoroughly and transitions not at all, so each step an item takes across its life surfaced as a missing verb. Walk ONE item lifecycle end to end (admit, slots filled, blocker answered, promoted, scheduled, closed, drained, compacted) and for every arrow name the verb, the record it writes and the check that proves it, in a table committed to the design; an arrow with no verb is an item booked from the table. Then one shared grammar module for every value that crosses verbs (slot lines, blocker questions, ledger lines, ids), each writer and reader importing it. Then the same walk for a LANE and a KIND, briefer. Full paragraph, quoted and authoritative: dotfiles claude/records/lifecycle-wave4-handoff-2026-08-27.md, the WAVE 5 HEAD paragraph
goal: enforce-the-invariants
write-set: cache-fix docs/directives/carrier-rework-design-2026-08-26.md (new 3.x section, the arrow table), then lifecycle plugin/cli/lifecycle_core/ per the items the table books
done-criterion: the arrow table exists in the design with a verb, a record and a check named for every arrow; every arrow lacking one is booked as its own item; the shared grammar module exists and is imported by each writer and reader of a crossing value, red-first on lc-40 own case
evidence: lc-13 to lc-40, 27 items (lc-15 superseded by lc-28), sorted by the wave-4 desk into transition 16 / nick 11 and ruled by the judgment desk. THE EVIDENCE SENTENCE, verbatim: the five named arrows each surfaced independently as its own item, found by different lanes, none looking for a pattern. Named arrows and their items: amend lc-27, unblock lc-26, promote lc-39, close lc-18/19/21, merge lc-17, register lc-13+lc-14 as one arrow, seed lc-23; cross-verb grammar lc-40, lc-38, lc-36. lc-16 flagged as a missing verb but a QUERY, not an arrow. Not a redesign: the refusal-heavy stance stays
blocked-by: evidence false  # wave 4 must close first; this is the wave-5 head and the operator GO is on the wave, not on starting it early

## lc-45
grade: READY
requirement: dotfiles' statusline renders backlog pressure on EVERY render in EVERY repo, today via 'backlog-census.py --statusline BACKLOG.md'. After the carrier freeze that reader must come here, and no statusline verb exists (grep -rn statusline over the plugin: 0 hits). The two available fallbacks are both defects: pointing the old renderer at ITEMS.md parses 0 bullets and renders a silent 0R.0P, and leaving it on the frozen file renders a number frozen at its last value forever, indistinguishable from a live one.
goal: lean-machinery-strict-checks
write-set: plugin/cli/lifecycle_core/verbs.py (a compact one-line render), and the CLI's verb table
done-criterion: one verb emits a single short line fit for a statusline — counts plus the schedulable head, no multi-line report — and it is CHEAP: it runs on every statusline render, so a full carrier parse per call is the wrong shape and the criterion states which. It exits per the CLI's own convention (0 clean, 2 finding, 3 could not verify) and NEVER emits a pass-shaped number it could not compute: a carrier it cannot parse yields the could-not-verify exit and a visibly non-numeric line. Red-first: the old renderer against ITEMS.md, showing the silent zero this verb exists to prevent. Consumers, which must NOT parse rendered prose to get this: dotfiles claude-worktime/config.sh and claude/hooks/session-scan.py.
evidence: dotfiles claude-worktime/config.sh:301; the freeze dispositions record claude/records/carrier-freeze-dispositions-2026-08-27.md names this reader the sharpest degrading-check in its set; the C lane surfaced the missing verb as a gap rather than bridging it (2026-08-27).
blocked-by: NONE

## lc-46
grade: READY
requirement: the intake join fires on nearly every item over a MIGRATED carrier, so the escape hatch becomes the default path and the guard trains the override reflex. Reported from cache-fix: an add returned FINDING join_undisposed matching 325 of 331 live items. MEASURED at the desk over dotfiles 139 items, and the number is exact rather than approximate: EXACTLY TWO tokens appear in more than 90 percent of requirement lines, "backlog" and "record" at 127/139 each, both contributed by the migration own tail "record: BACKLOG.md:N" that every migrated body carries. MATCH_MIN_TOKENS is 2. So the migration supplies precisely the threshold, against nearly every item, by construction.
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/verbs.py (STOPWORDS, MATCH_MIN_TOKENS and the token match), test/test_verbs.py
done-criterion: the join discriminates over a migrated carrier. THE DESIGN OWN DEFENCE IS WHAT FAILED and the fix must not restate it: the comment at STOPWORDS says the list is kept short on purpose because "the two-token threshold is what actually does the work" — that premise is false wherever a systematic tail contributes two universal tokens, which is every migrated carrier. So do NOT lengthen the stopword list by hand: that is the second vocabulary the comment rightly refuses, and it would need a new entry for every future migration tail. WEIGHT BY RARITY ACROSS THE CARRIER instead — a token present in nearly every item has no discriminating power BY DEFINITION and needs no list to say so, which makes the fix self-maintaining and kills the next tail before it is written. Red-first on the real case: cache-fix 331 items, the exact add that returned 325, expected to fall to a handful. MUST-NOT-MOVE: two items that genuinely share a rare token still match; an item sharing ONLY migration-tail tokens does not; and the finding still fires on a real duplicate, shown on a planted pair.
evidence: judgment desk report from cache-fix 2026-08-27 (325 of 331); desk measurement over dotfiles ITEMS.md the same day, token document-frequency computed with the shipped STOPWORDS and _TOKEN regex; verbs.py STOPWORDS comment and MATCH_MIN_TOKENS = 2.
blocked-by: NONE

## lc-47
grade: READY
requirement: the lc-44 ruling keeps a DROP reason in the LEDGER while a DONE reason goes in the MOVED BODY, and its stated ground is that a dropped body MAY BE PRUNED so its record cannot live only there. The retire lane design of record (cache-fix carrier-rework-design 3.1) specifies a COMPACTION step collapsing done bodies older than N days to one ledger line each, git keeping the body. Once that exists the pruning argument reaches DONE bodies identically: a compacted body takes its closed-reason and closed-ref with it, and the closure record the doctrine calls load-bearing is gone from every carrier a reader loads. Found by the lc-44 lane while building to the ruling; the ruling is correct TODAY because retire.py has no verb for compaction yet.
goal: one-home-per-kind
write-set: whichever change introduces the compaction verb in retire.py, plus the lc-44 slots in items.py if the answer moves them
done-criterion: the compaction verb ships only WITH an answer to where a compacted item closure record lives. THE QUESTION, so it is not re-derived: compaction turns the moved body into a ledger line, so either the closure lines are LIFTED into that ledger line (one fact still one home, the home changing at compaction time) or DONE bodies carrying closure lines are EXEMPT from compaction (the record outlives the body, at the cost of the carrier not shrinking where it most would). Whichever is chosen, the verb REFUSES to compact a body it would silently strip: red-first is compacting a body carrying closed-reason and closed-ref and showing the record survives in whatever home the answer names. Must-not-move: a DROP still keeps exactly one ledger line and no second copy.
evidence: lc-44 lane interim 3, 2026-08-27, citing cache-fix carrier-rework-design 3.1 and retire.py stating that never, compact and delete have no verb yet; the lc-44 ruling itself (judgment desk, 2026-08-27) for the pruning ground it rests on.
blocked-by: evidence the compaction verb does not exist yet — this fires when it is written, and its trigger is that change, not a date

## lc-50
grade: READY
requirement: closed-ref: stores the caller's spelling verbatim, so `--ref HEAD` writes the literal string HEAD into a permanent closure record that then stops being edited: a moving label where the record's whole point is content. Surfaced by the lane that built it, from its own must-not-move arm, record: opus-lc44-48-49 report gap 2, 2026-08-27
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/verbs.py,test/test_verbs.py
done-criterion: _resolve_refs resolves every accepted ref to its full 40-hex sha before writing, keeping the --ref HEAD convenience and storing content. DECIDED by the desk 2026-08-27, option (A) of the three the lane named: (B) refusing a non-sha drops the convenience for nothing, (C) leaving it stores a label the dotfiles devbook's own label-versus-content rule forbids, and lc-44's criterion already said closed-ref: <sha>. The docstring's counter-argument (rewriting puts a value in the file nobody typed) is answered: the full sha IS what the caller meant by HEAD at that instant, and the record must survive the ref moving. Red-first on --ref HEAD writing the literal string. Must-not-move: an unresolvable ref is still refused before the move; a full sha passed in is written unchanged; a comma list still resolves elementwise
evidence: verbs.py:1584-1598 read at the artifact by the desk: the docstring states WRITTEN AS GIVEN, not resolved to a full sha, so this is the built design and not a slip. The predicate git rev-parse --verify <ref>^{commit} accepts HEAD, which is what makes the label writable
blocked-by: NONE

## lc-51
grade: READY
requirement: tools/prove-rows.py anchors its mutation arrangements by SUBSTRING, so an unrelated verb spelling the same line at a deeper indent silently retires another row's proof; and the two rows added for lc-44/lc-49 have no mutation arrangement at all, record: opus-lc44-48-49 report gaps 3 and 4, 2026-08-27
goal: every-refusal-red-first
write-set: tools/prove-rows.py,test/test_refusals.py
done-criterion: Anchors match LINE-EXACT rather than by substring, and blocker_unstorable plus closed_ref_unresolvable each gain a recorded mutation arrangement. Red-first for the anchor half is already in hand and must be reproduced: a copy of move_uncommitted's anchor line indented one level deeper elsewhere in the file makes prove-rows report that row's source as moved. Must-not-move: prove-rows stays exit 0 over the existing arrangements, and the honest COULD NOT VERIFY answer is preserved, since that is what made this catchable
evidence: measured live by the lane during its build: prove-rows went exit 0 to EXIT 3 with move_uncommitted and blocked_in_done_home both reporting 'the source moved under this arrangement'. move_uncommitted's anchor is `    if r.returncode != 0:` at 4-space indent, a substring of the same line at any deeper indent. The lane avoided both rather than repairing prove-rows (outside its write set) and spelled its own git check `if probe.returncode == 0: continue` with a comment saying why. Desk re-ran prove-rows at 8a5d664: exit 0
blocked-by: NONE

## lc-52
grade: READY
requirement: every carrier verb that commits composes its own message and writes NO Co-Authored-By trailer, so an agent-authored carrier commit is unclaimable by trailer and the operator corpus's AI-attribution rule is unmet on this path, record: opus-lc44-48-49 report gap 5, 2026-08-27
goal: lean-machinery-strict-checks
write-set: plugin/cli/lifecycle_core/verbs.py,test/test_verbs.py
done-criterion: commit_paths appends a Co-Authored-By trailer naming the running model, and a Claude-Session trailer where the environment supplies one. Red-first: 89951f4 (the lane's own item amend commit) carries neither and is factually the lane's. Must-not-move: a human-run commit through the same path is not given a false agent trailer, so the model name comes from the environment and its ABSENCE means no trailer rather than a placeholder
evidence: the lane reported 89951f4 as 'present in the tree, not mine by trailer' while stating it is factually its own; desk confirmed at the artifact — git log -1 --format='%(trailers)' 89951f4 is empty. The pre-push gate's own WARN on unmarked commits is the same fact from the other side
blocked-by: NONE

## lc-53
grade: READY
requirement: absence-scan --git-range old..new scans the files CHANGED in the range at their NEW content, so EMPTY..main is a TIP scan wearing a history scan's costume. The publication bar's own verdict line is about a public HISTORY, and no mode of the tool answers that question, record: measured at the public flip 2026-08-27
goal: enforce-the-invariants
write-set: tools/absence-scan.mjs,test/absence-scan.test.mjs
done-criterion: A mode exists that scans every blob reachable from a ref (git rev-list --objects, or per-commit content) and answers 'is my HISTORY clean'. Red-first is already in hand and must be reproduced as a test: EMPTY..main returns exit 0 while EMPTY..8a5d664 returns exit 2 on the same repo, for a leak that IS in main's history. Must-not-move: the existing range mode keeps its current semantics for the pre-push hook, which wants changed-files-at-new-content
evidence: executed at the flip: `--git-range EMPTY..main` exit 0 'clean'; `--git-range EMPTY..8a5d664` exit 2, FINDING foreign-path test/test_verbs.py line 429. Both ran seconds apart on the same repo. 8a5d664 is an ancestor of main, so a true history scan could not return clean. The scope line (46 source files, same as the tracked-file count) is the tell
blocked-by: NONE

## lc-54
grade: READY
requirement: test/absence-scan.test.mjs has a test asserting the walk collects files under proxy/, a directory this repo does not have, so the suite has been RED on an environment premise it does not pin, record: baselined 2026-08-27 before the foreign-path repair
goal: lean-machinery-strict-checks
write-set: test/absence-scan.test.mjs
done-criterion: The test either pins its fixture inside the repo or skips with a named reason; the suite exits 0. Red-first: it fails today with 'the walk collected no file under proxy/'. Must-not-move: the assertion still fires where a proxy-like tree DOES exist, so the repair is a pinned fixture and not a deleted test
evidence: node --test test/absence-scan.test.mjs, run before and after the foreign-path repair: EXIT=1 both times, the SAME single failing test 'source: every UUID in a tracked SOURCE_SCANNABLE file is on the synthetic allowlist' at :743, message 'the walk collected no file under proxy/'. Stated as the baseline in 70bc93c so the repair's own proof could not borrow a pre-existing red
blocked-by: NONE

## lc-55
grade: READY
requirement: item ready and item close disagree about whether one blocker was answered, and the disagreement is written into the ledger as a second contradictory line. Measured on a scratch clone 2026-08-28, wave-5 T walk: ledger add decision wrote the answer at LEDGER.md:35, item ready reported UNBLOCKED citing that line, and item close then reported the same blocker was never answered, wrote blocker-moot: on the moved body and appended LEDGER.md:36 recording the question as moot. One question, two answers, both live in the carrier
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/verbs.py,plugin/cli/lifecycle_core/items.py,test/test_verbs.py
done-criterion: item ready and item close reach the SAME verdict on one blocker from one ledger state, red-first on the recorded walk: today ready says UNBLOCKED and close says never answered on the identical item
evidence: wave-5 T walk, scratch clone of lifecycle at 66bd2af, probe item lc-55: ready output UNBLOCKED with LEDGER.md:35 cited, close output blocker-moot never answered, ledger lines 35 and 36 contradictory. Mechanism NOT established at the desk, only the divergence
blocked-by: NONE

## lc-56
grade: READY
requirement: ledger add decision writes its line and does not commit it, and prints no NOT COMMITTED notice. lc-25 fixed exactly this contract for item add, which now commits on every join or says it did not; the sibling ledger verb never got it. The write with no committing actor is the assumed-delivery class: it does not fail, it accumulates
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/ledger.py,plugin/cli/lifecycle_core/verbs.py,test/test_ledger.py
done-criterion: ledger add commits on every write, or prints NOT COMMITTED, matching lc-25 contract for item add. Red-first on the recorded pair: item add printed committed and moved HEAD while ledger add left M LEDGER.md with no notice, same clone same run
evidence: wave-5 T walk 2026-08-28, two arms in one run on a scratch clone at 66bd2af: item add lc-55 printed committed: lifecycle: add lc-55 and HEAD moved to 86b9009; ledger add decision then wrote LEDGER.md:35 and git status showed M LEDGER.md with HEAD unchanged. Also observed at the desk earlier the same day writing the C4 line, which the desk had to commit by hand. Consequence measured: item ready resolved a blocker from that UNCOMMITTED ledger line, so an item reads as unblocked in a tree where the answer was never committed
blocked-by: NONE

## lc-57
grade: READY
requirement: there is no read-by-goal query: item ready takes only an ident or --head, and no verb answers which items carry a given goal. lc-16 named this arrow as a query and it is still unbuilt, so the goal slot is written on every item and read by nothing
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/items.py,plugin/cli/lifecycle_core/cli.py,test/test_items.py
done-criterion: a goal-scoped read exists and returns only items carrying that goal, red-first: today item ready --goal is rejected at argparse, which is a usage error and not the defect, so the red is the missing OUTPUT on a form the CLI accepts
evidence: wave-5 T walk 2026-08-28: item ready --help lists only [--head] [ident]; the full verb surface item {check,add,ready,amend,promote,park,close,ratio} carries no query verb. Source item lc-16 from the 27-item transition sort
blocked-by: NONE

## lc-58
grade: READY
requirement: the compacted arrow has no verb. retire WALKS and REPORTS and says so in its own output: the acts its findings call for are their own verbs, but no compaction verb exists in the CLI surface, so the last arrow of an item life is unreachable and the conservation line can only ever read compacted 0
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/retire.py,plugin/cli/lifecycle_core/items.py,test/test_retire.py
done-criterion: a compaction verb exists, records what it compacted, and the conservation identity still balances after it runs, red-first: today the conservation line reads compacted 0 by construction because nothing can ever increment it
evidence: wave-5 T walk 2026-08-28 on a scratch clone at 66bd2af: retire output states EXITS TAKEN THIS PASS none and that compaction is its own verb; the top-level surface is {init,kind,item,ledger,lane,workflow,desk,retire,audit,migrate} with no compact; item check conservation printed baseline 8 + added 47 minus compacted 0
blocked-by: NONE

## lc-59
grade: READY
requirement: no verb declares a lane in a repo's lanes list. lane new says so in its own help: it writes the lane file as a stub and does NOT declare it in this repo's lanes list. So a lane can exist as a file and be invisible to the board, which is the router's input, and nothing closes the gap between the two
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/lanes.py,plugin/cli/lifecycle_core/declaration.py,test/test_lanes.py
done-criterion: a lane created by lane new is declarable by a verb, and a lane FILE present but undeclared is a finding rather than silence, red-first on this repo whose declaration reads lanes: (empty, declared not absent) while lane files can be created
evidence: wave-5 L walk 2026-08-28: lane new --help states the non-declaration outright; the lane verb surface is {list,register,new} with no declare; kind list shows lanes: (empty)
blocked-by: NONE

## lc-60
grade: READY
requirement: nothing records that a lane was ENTERED, so the audit's promised per-lane use-evidence has no writer. lifecycle audit is specified to report use-evidence per lane and per judgment rule, but no verb writes an entry event, so that column can only ever be empty or inferred
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/lanes.py,plugin/cli/lifecycle_core/firelog.py,test/test_lanes.py
done-criterion: entering a lane leaves a record the audit reads, and audit's use-evidence column is populated from it, red-first: today the column has no writer at all
evidence: wave-5 L walk 2026-08-28: lane verb surface {list,register,new} has no enter verb; design section on audit promises use-evidence per lane
blocked-by: NONE

## lc-61
grade: READY
requirement: kind sweep reports plugin/workflows/.gitkeep as an unregistered persisted thing. The workflow-templates kind declares growth unbounded-with-reason and says the directory placeholder is what marks the set EMPTY rather than the directory's absence, so the placeholder is deliberate and the declaration simply does not claim it
goal: one-home-per-kind
write-set: .claude/lifecycle.json,test/test_declaration.py
done-criterion: kind sweep returns CLEAN on this repo, with the placeholder claimed by a registered kind rather than exempted, red-first on the current FINDING
evidence: wave-5 K walk 2026-08-28, executed: kind sweep returns FINDING unregistered_persisted_thing naming exactly one file, plugin/workflows/.gitkeep; kind check is CLEAN at 19 kinds, so the declaration is well-formed and merely incomplete
blocked-by: NONE

## lc-62
grade: READY
requirement: lc-40's repair covers the MINT side only; the ANSWER side is still verbatim-equality and nothing says so at answer time. A desk that answers a decision blocker's substance in its own words leaves the item blocked forever: item ready resolves by question-slot equality, reports 'No decision: line names this question', and the answer sits in the ledger unmatched. The blocker's own refusal text coaches the minter and says nothing to the answerer
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/items.py,plugin/cli/lifecycle_core/ledger.py,test/test_items.py
done-criterion: answering a decision blocker is possible without reproducing its text by hand: either the ledger answer is keyed to the item and question at write time, or a near-miss between a ledger question and a standing blocker is reported rather than silently unmatched. Red-first on the measured pair below, where the substance was answered and the item stayed blocked
evidence: measured at the wave-5 peer desk 2026-08-28 on df-130, both arms in one run: a ledger decision was written answering the blocker's substance, item ready still reported BLOCKED with 'No decision: line names this question, so it has not been answered'; the blocker was then re-minted as the bare question matching the ledger text and item ready immediately reported UNBLOCKED citing LEDGER.md:299. Second half of the same finding: df-130's original blocker was a SENTENCE ABOUT the question ('the item own body says decision OPEN: whether ...'), which no answer could ever equal
blocked-by: NONE

## lc-63
grade: READY
requirement: item promote has no red of its own for the block-boundary defect. It is the second caller of _set_slots and inherits the fix through the shared helper, which is inference rather than an executed arm. The corpus rule is that a red certifies the CLASS that fired, never the instrument's reach: a variant of the defect needs its own positive, and park and promote are two variants because they write different slots
goal: every-refusal-red-first
write-set: test/test_verbs.py
done-criterion: item promote carries its own red against the OLD boundary code, in the same shape as the park arm: a carrier whose second block heading is tab-separated, a promote naming the FIRST block, and an assertion that the second block was NOT re-graded. Plus the must-move companion showing the named block IS still written, so the pair separates the defect from a build that stopped writing
evidence: lane opus-lc40-grammar report gap 3, 2026-08-28, its own words: the fix is inherited through the shared helper, inference not an executed arm. The park arm's red is real and pasted (AssertionError: 'PARKED' != 'READY' : xx-2 was parked by a call that named xx-1) against a whole-repo git archive of 66bd2af whose own self-check was green first; promote has no equivalent
blocked-by: NONE

## lc-64
grade: READY
requirement: goal is per-repo DOMAIN vocabulary (design 3.1), so repo-self-work — method decomposition, hook retirement, migration residue — advances no goal and cannot be booked; record: cache-fix design 3.1b (operator 2026-08-28)
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/declaration.py,plugin/cli/lifecycle_core/init.py
done-criterion: item add --goal tend and item check accept tend in every repo with nothing declared; a non-tend undeclared goal still refuses (red-first); init's effective goal set = declared union {tend}
evidence: cache-fix design 3.1b, the plugin-reserved meta-goal
blocked-by: NONE

## lc-65
grade: READY
requirement: migrate converts the carrier and leaves its residue — un-decomposed method file, live old-carrier readers, oversized frozen archive — for a human to notice, and humans don't (the assumed-delivery class); record: cache-fix design 3.1b, 4 row 1
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/migrate.py
done-criterion: migrate --apply emits a fixed set of tend items for its residue, each PARKED with a typed blocker, in the migration report; red-first: a source with a method file plus live BACKLOG readers produces exactly those parked tend items
evidence: cache-fix design 3.1b (seeding), 4 row 1 (the migration report)
blocked-by: lc-64
