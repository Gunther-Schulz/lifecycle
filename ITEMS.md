schema: 2
baseline: 8
added: 30
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

## lc-35
grade: NEW
requirement: The leak scan finds a foreign home path inside an item BODY (ITEMS.md:300) and the repo declares public:true, so the finding is live even with no remote today — record: wave-4 desk 2026-08-27, re-run at c915bc2 and again at 22adf7e, unchanged
goal: enforce-the-invariants
write-set: UNKNOWN
done-criterion: node tools/absence-scan.mjs --git-range ..HEAD returns 0 findings over ITEMS.md, with the instrument first shown live on a planted positive so a zero is not an unread instrument
evidence: executed twice by the wave-4 desk: "FINDING foreign-path  ITEMS.md  line 300  (481 chars, #ee54ac7003b3)", exit 2, identical at c915bc2 and 22adf7e. .claude/lifecycle.json declares public:true and leak-scan.source-scope-foreign-path:true, whose own reason note records that the SHIPPED foreign-path class is scoped corpus — so the declaration and the shipped scanner disagree, which is the residue this item names
blocked-by: decision does the item BODY change (rewrite the path out of it) or does the foreign-path class scope change (corpus -> source) to honour the declaration

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
