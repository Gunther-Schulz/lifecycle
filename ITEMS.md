schema: 2
baseline: 8
added: 72
compacted: 0

## lc-3
grade: NEW
requirement: PARKED 2026-08-26 — where the leak scan lives once it is a SHARED tool — record: BACKLOG.md:32
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: BACKLOG.md:32-39
blocked-by: evidence false  # the named missing evidence in the source body
amend-reason: 2026-09-12 BACKLOG.md is deleted in this pass, so this entry's evidence pointer into it would stop resolving. The source body is inlined here and the trigger re-checked against the world; the entry stays PARKED on an unfired trigger.
amended-evidence: 2026-09-12 SOURCE BODY INLINED 2026-09-12, verbatim from BACKLOG.md:32-39 before that file's deletion, because the line-range pointer stops resolving with it: 'PARKED 2026-08-26 — where the leak scan lives once it is a SHARED tool. Design §3.8 lists it among PLUGIN-layer contents (what one install carries); brief D-a puts tools/ at the repo root, outside plugin/. Today only the repo's own pre-push hook consumes it, and root tools/ serves that. Trigger: the first template extraction, which is what makes the scan a thing the plugin must SHIP rather than a thing this repo runs.' TRIGGER RE-CHECKED at f09e32d and NOT fired: plugin/skills and plugin/workflows each hold exactly one file, a 0-byte .gitkeep, so no template has been extracted; the declaration's workflow-templates kind says the same in its own words, 'EMPTY today (wave 2 extracts the first set)'. Legacy pointer, for the record: BACKLOG.md:32-39, resolvable at the sha the reading roster pins.

## lc-7
grade: NEW
requirement: PARKED 2026-08-26 — a detector's home repo is taken from the cwd, not from a registry — record: BACKLOG.md:70
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: BACKLOG.md:70-76
blocked-by: evidence false  # the named missing evidence in the source body
amend-reason: 2026-09-12 BACKLOG.md is deleted in this pass, so this entry's evidence pointer into it would stop resolving. The source body is inlined here and the named missing evidence re-checked against the source; the entry stays PARKED.
amended-evidence: 2026-09-12 SOURCE BODY INLINED 2026-09-12, verbatim from BACKLOG.md:70-76 before that file's deletion: 'PARKED 2026-08-26 — a detector's home repo is taken from the cwd, not from a registry. §3.1 says detectors register their home repo; the detector registry is wave 3. So --source detector:<name> is origin-checked exactly like a session add. Missing evidence: the registry's shape. Nothing in wave 1 depends on the answer, and the coarse check is not wrong today — it is narrower than the design.' RE-CHECKED at f09e32d and STILL OPEN: a grep for detector over declaration.py and verbs.py filtered to registry/registered/home/cwd returns zero hits, so no detector registry exists in the source; the named missing evidence, the registry's shape, is still missing. Legacy pointer, for the record: BACKLOG.md:70-76.
amend-reason: 2026-09-12 the previous amendment's basis was a filtered zero-hit grep read as absence, with no positive control. Replaced with the source's own two statements that the detector registry is wave 3, plus the instrument's reach (20 hits for 'detector' in the package). Same verdict, a basis that discriminates.
amended-evidence: 2026-09-12 SOURCE BODY INLINED 2026-09-12, verbatim from BACKLOG.md:70-76 before that file's deletion: 'PARKED 2026-08-26 — a detector's home repo is taken from the cwd, not from a registry. §3.1 says detectors register their home repo; the detector registry is wave 3. So --source detector:<name> is origin-checked exactly like a session add. Missing evidence: the registry's shape. Nothing in wave 1 depends on the answer, and the coarse check is not wrong today — it is narrower than the design.' RE-CHECKED at f09e32d and STILL OPEN, on the source's own words rather than on a zero-hit search: judgment.py:126 carries sited_in='wave 3, the detector registry, which is what carries a ...' and refusals.py:593 carries the pair ('detector without disposition', 'the detector registry is wave 3'). So the build states the registry is unbuilt, and the named missing evidence, its shape, is still missing. Instrument reach shown rather than assumed: 'detector' returns 20 hits across plugin/cli/lifecycle_core/, so the search was not blind. Legacy pointer, for the record: BACKLOG.md:70-76.

## lc-8
grade: NEW
requirement: READY 2026-08-26 — `dev-notes/` needs its OBSERVATIONS carrier — record: BACKLOG.md:77
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: BACKLOG.md:77-87
blocked-by: decision regrade: was READY under the old carrier — READY is judged, never inherited
amend-reason: 2026-09-12 BACKLOG.md is deleted in this pass, so this entry's evidence pointer into it would stop resolving. The source body is inlined, and the goal, write-set and done-criterion slots are filled FROM the design the source body already decided rather than from any new judgment, so the successor stands alone once the file is gone.
amended-goal: 2026-09-12 lean-machinery-strict-checks
amended-write-set: 2026-09-12 dev-notes/lifecycle-OBSERVATIONS.md
amended-done-criterion: 2026-09-12 the first instrument lesson from wave 2 lands in dev-notes/lifecycle-OBSERVATIONS.md rather than in a commit message; the file exists and its head states the four slots
amended-evidence: 2026-09-12 SOURCE BODY INLINED 2026-09-12, verbatim from BACKLOG.md:77-87 before that file's deletion: 'READY 2026-08-26 — dev-notes/ needs its OBSERVATIONS carrier. Design, decided: copy dispatch-guards four-slot form (incident + basis, class, pre-formulated rule text, consumer + drain seam) into dev-notes/lifecycle-OBSERVATIONS.md, same-class entries merging into the existing entry rather than a sibling; provenance dev-notes/OBSERVATIONS-FORM.md in that repo. Write-set: dev-notes/lifecycle-OBSERVATIONS.md. Verifier: the file exists and its head states the four slots. Done-criterion: the first instrument lesson from wave 2 lands in it rather than in a commit message.' RE-CHECKED at f09e32d and STILL OPEN: dev-notes/ holds exactly one file, README.md, 3 lines, so no OBSERVATIONS carrier exists here. The slots above are filled FROM that decided design rather than newly decided, which is why this amendment adds no judgment of its own. SEE ALSO lc-77, booked in this same pass, which asks whether this carrier class becomes a registered lifecycle kind; if it does, this entry's four-slot form is the shape that gets reconsidered rather than carried over blind. Legacy pointer, for the record: BACKLOG.md:77-87.
amend-reason: 2026-09-12 the earlier amendment named lc-77 for the OBSERVATIONS-kind entry, which was a forward guess made before the ids existed; the entry is lc-77's neighbour lc-78. Corrected here rather than left standing, and the ordering between the two entries stated while correcting it.
amended-evidence: 2026-09-12 SOURCE BODY INLINED 2026-09-12, verbatim from BACKLOG.md:77-87 before that file's deletion: 'READY 2026-08-26 — dev-notes/ needs its OBSERVATIONS carrier. Design, decided: copy dispatch-guards four-slot form (incident + basis, class, pre-formulated rule text, consumer + drain seam) into dev-notes/lifecycle-OBSERVATIONS.md, same-class entries merging into the existing entry rather than a sibling; provenance dev-notes/OBSERVATIONS-FORM.md in that repo. Write-set: dev-notes/lifecycle-OBSERVATIONS.md. Verifier: the file exists and its head states the four slots. Done-criterion: the first instrument lesson from wave 2 lands in it rather than in a commit message.' RE-CHECKED at f09e32d and STILL OPEN: dev-notes/ holds exactly one file, README.md, 3 lines, so no OBSERVATIONS carrier exists here. The slots above are filled FROM that decided design rather than newly decided, which is why this amendment adds no judgment of its own. SEE ALSO lc-78, booked in this same pass, which asks whether this carrier class becomes a registered lifecycle kind; if it does, the four-slot free-prose form this entry would build is exactly what gets redesigned into positional slots rather than carried over, so the two entries are ordered: build this one only after lc-78's shape call, or build it knowing the shape is provisional. Legacy pointer, for the record: BACKLOG.md:77-87.

## lc-10
grade: READY
requirement: §3.11's intake cost test has three conjuncts and the third is unimplemented: cost_test() never receives the typed blocker — record: wave2 L1 booking run, 2026-08-26
goal: every-refusal-red-first
write-set: plugin/cli/lifecycle_core/verbs.py,test/test_items.py
done-criterion: an item with a typed decision blocker and a one-file write-set is graded NEW without the do-it-now ask, red-first against the current implementation
evidence: verbs.py:268 signature is cost_test(write_set, hunks, source) — no blocker parameter, and its docstring cites §3.2 not §3.11; observed live when a booking carrying a typed decision blocker was held for a hunk count
blocked-by: NONE

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
amend-reason: 2026-09-12 retirement pass 2026-09-12: lc-59 restated this entry and lc-14 as one item; merged into the two existing entries rather than left as a sibling, and dropped in the same pass.
amended-evidence: 2026-09-12 structural: LANES_DIR used only at lanes.py:147 to build a declared name's path, zero glob/iterdir over it anywhere in the package. behavioural: lane list against a repo carrying an undeclared lanes/x.md printed 'declared lanes: 0 — EMPTY, declared rather than absent' and named neither x nor lanes/x.md. RE-CONFIRMED 2026-09-12 (retirement pass, executed at f09e32d): the lane verb surface is {list,register,new}; lane register puts a REPO on the roster, not a lane in this repo's lanes list. MERGED IN lc-59 (wave-5 L walk 2026-08-28), which re-found this gap and lc-14's together as one item and is dropped as a duplicate in this pass; its contribution is the executed confirmation that lane new --help states the non-declaration outright and kind list shows lanes: (empty).

## lc-14
grade: READY
requirement: "lane new" writes lanes/<door>.md but deliberately does not touch the declaration, and no verb adds a lane name to an existing declaration's "lanes" list. Combined with the undeclared-file blindness booked alongside this (lc-13), the default outcome of "lane new" is a lane file that NO verb can see: the tool prints UNREGISTERED as a hint and offers no way to resolve it. Same assumed-delivery shape as init leaving carriers uncreated
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/lanes.py,plugin/cli/lifecycle_core/declaration.py,test/test_lane_new.py,cache-fix docs/directives/carrier-rework-design-2026-08-26.md
done-criterion: red-first against the current build, then: a fresh "lane new" reads QUIET in "lane list" with the declaration diff showing EXACTLY ONE added name. No new verb
evidence: L2b report (g): no such verb exists today, noted and not built. DECISION TAKEN (judgment desk 2026-08-26): NO new verb — "lane new" registers its own output, appending the name to the declaration's "lanes" list in the same run. Derivable from the same assumed-delivery reading the desk applied to init: a verb's normal output must be visible to the tool that owns it, and init already writes the declaration, so a declaration write is not a new class of act. With lc-13 closing the inverse scan, the invariant then holds in both directions with no hand step left. The "lane register" name collision is moot — no verb is minted. Section 3.8b's "written by the repo, by hand" was said of lane FILES' content, which "lane new" still only stubs, so that sentence stays true and is amended to say registration is the verb's
blocked-by: evidence L2c's declaration.py edits have landed on main (the collision is declaration.py, not cli.py — with no new verb this item adds no subparser)
amend-reason: 2026-09-12 retirement pass 2026-09-12: lc-59 restated this entry and lc-13 as one item; merged into the two existing entries rather than left as a sibling, and dropped in the same pass.
amended-evidence: 2026-09-12 L2b report (g): no such verb exists today, noted and not built. DECISION TAKEN (judgment desk 2026-08-26): NO new verb — lane new registers its own output, appending the name to the declaration's lanes list in the same run. RE-CONFIRMED 2026-09-12 (retirement pass, executed at f09e32d): lane new --help still states 'Does NOT declare it in this repo's lanes list', and the lane surface {list,register,new} has no declare verb. MERGED IN lc-59 (wave-5 L walk 2026-08-28), the later sibling covering this arrow together with lc-13's inverse scan, dropped as a duplicate in this pass.

## lc-16
grade: READY
requirement: No verb reads the carrier BY goal. '--goal' occurs exactly once in the whole parser (cli.py:279, on 'item add'); 'item ready' takes only [--head] [ident] and 'item check'/'item ratio' take no arguments. So a repo can declare a closed goal set and set a goal per item, then never query by it — which breaks the consumer story for any carrier shared by more than one audience. Reported by the dotfiles desk, whose fire-rate review must read corpus entries out of a carrier that also holds machine and deploy work
goal: lean-machinery-strict-checks
write-set: plugin/cli/lifecycle_core/cli.py,plugin/cli/lifecycle_core/verbs.py,test/test_items.py
done-criterion: a goal-filtered listing exists and returns only entries carrying that goal, red-first against a carrier holding at least two goals
evidence: verified here at cf92ad9: grep '"--goal"' cli.py returns one line, :279. Peer measured it at :262 on 6badd58; the line moved, the substance holds
blocked-by: NONE
amend-reason: 2026-09-12 retirement pass 2026-09-12: lc-57 is a duplicate of this entry, found later by the wave-5 T walk. Merged into the existing entry rather than left as a sibling, per the backlog doctrine's merge rule; lc-57 is dropped in the same pass.
amended-evidence: 2026-09-12 verified here at cf92ad9: grep '"--goal"' cli.py returns one line, :279. Peer measured it at :262 on 6badd58; the line moved, the substance holds. RE-CONFIRMED 2026-09-12 (retirement pass, executed at f09e32d): item ready --help lists only [--head] [ident], and the item verb surface {check,add,ready,amend,promote,park,close,ratio,statusline} carries no goal-scoped query. MERGED IN lc-57 (wave-5 T walk 2026-08-28), the later sibling booking of this same gap, dropped as a duplicate — its own body named lc-16 as its source. Its contribution, kept here: the red-first shape — item ready --goal is rejected at argparse, which is a usage error and not the defect, so the red is the missing OUTPUT on a form the CLI accepts.

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
amend-reason: 2026-09-12 retirement pass 2026-09-12: two changes. (1) lc-54 is a duplicate of this entry — same failing test, same red — merged here per the merge rule and dropped in this pass. (2) The blocker named lc-9, which is dropped this pass as overtaken: tools/absence-scan.mjs:611-612 already declares foreign-path with scope 'source', so the widening lc-9 waited for has shipped and this item no longer waits on it.
amended-evidence: 2026-09-12 executed at f2c37fe: node --test test/absence-scan.test.mjs exits 1, 62 tests 61 pass 1 fail — 'source: every UUID in a tracked SOURCE_SCANNABLE file is on the synthetic allowlist' (:743) AssertionError 'the walk collected no file under proxy/'. Source :756-761 loops ["test","tools","proxy","docs"] and asserts files.length > 500. lifecycle has no proxy/ and 51 tracked files total. RE-MEASURED 2026-09-12 at f09e32d, unchanged: tests 62 / pass 61 / fail 1 / skipped 0, the same single test. MERGED IN lc-54 (baselined 2026-08-27), the later sibling booking of this same red, dropped as a duplicate in this pass; its contributions, kept here: the baseline was stated in 70bc93c so the foreign-path repair's own proof could not borrow a pre-existing red, and its MUST-NOT-MOVE arm — the assertion still fires where a proxy-like tree DOES exist, so the repair is a pinned or derived anchor and never a deleted test.
amended-blocked-by: 2026-09-12 NONE

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

## lc-58
grade: READY
requirement: the compacted arrow has no verb. retire WALKS and REPORTS and says so in its own output: the acts its findings call for are their own verbs, but no compaction verb exists in the CLI surface, so the last arrow of an item life is unreachable and the conservation line can only ever read compacted 0
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/retire.py,plugin/cli/lifecycle_core/items.py,test/test_retire.py
done-criterion: a compaction verb exists, records what it compacted, and the conservation identity still balances after it runs, red-first: today the conservation line reads compacted 0 by construction because nothing can ever increment it
evidence: wave-5 T walk 2026-08-28 on a scratch clone at 66bd2af: retire output states EXITS TAKEN THIS PASS none and that compaction is its own verb; the top-level surface is {init,kind,item,ledger,lane,workflow,desk,retire,audit,migrate} with no compact; item check conservation printed baseline 8 + added 47 minus compacted 0
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

## lc-66
grade: READY
requirement: CROSS-ROW CLASS (begehung r5): the kind/vocabulary system is single-repo AND domain-scoped, so any cross-repo/cross-domain necessity — a dependency, a coordination condition, a detector spanning repos — has no first-class slot and falls to prose nothing surfaces; the tend gap one axis over; record: cache-fix begehung-findings-2026-08-28-r5.tsv, design 3.1/3.5
goal: one-home-per-kind
write-set: docs/directives/carrier-rework-design-2026-08-26.md@cache-fix,plugin/cli/lifecycle_core/declaration.py,plugin/cli/lifecycle_core/verbs.py
done-criterion: a coordination layer: typed cross-repo edge (blocked-by <repo>:<id>, resolves on that item's DONE across carriers) + a cross-repo detector home + a cross-repo roll-up view; red-first on the cf-337->lc-64 case (it auto-returns to NEW when lc-64 closes)
evidence: begehung r5 close-class over five vocabulary-slot rows; the live cf-337/lc-64 instance
blocked-by: decision the coordination mechanism SHAPE: typed cross-repo edge (recommended) vs a declared coordination kind vs both

## lc-67
grade: READY
requirement: The operator decision-queue has no aging/ranking/cross-repo roll-up: decision blockers route to the operator's queue but it is not a declared kind with growth control (R22), and nothing aggregates pending decisions across 14 repos — against cheap oversight; record: begehung r5, design 3.1 :155-156, R3, R22
goal: one-home-per-kind
write-set: docs/directives/carrier-rework-design-2026-08-26.md@cache-fix,plugin/cli/lifecycle_core/verbs.py
done-criterion: the decision queue is a declared kind with a flow alarm (pending-decision count trend) and a cross-repo roll-up (lane list surfaces pending decisions per repo); red-first: a decision blocker aged past a threshold surfaces as a finding
evidence: begehung r5 F3/F4
blocked-by: lc-66

## lc-68
grade: READY
requirement: Conservation checks COUNT and source blob-sha, not body content: a migrated body garbled while the count holds passes clean (paraphrase-drift in a conservation costume); record: begehung r5, R8, cf-324
goal: every-refusal-red-first
write-set: plugin/cli/lifecycle_core/migrate.py,test/test_migrate.py
done-criterion: migrate verifies a per-body content hash across the boundary, not only N-in=N-out; red-first: a body mutated between read and write is caught
evidence: begehung r5 content-conservation row
blocked-by: NONE

## lc-70
grade: READY
requirement: tend feature completeness (lc-64 escalations, not in its done-criterion): (a) a declaration LISTING tend in goals is silently absorbed by the union, but 3.1b says 'not declarable per repo'; (b) orientation (cli.py:144) prints DECLARED goals, so tend is invisible there — assurance narrower than reality; record: lc-64 build report
goal: one-home-per-kind
write-set: plugin/cli/lifecycle_core/declaration.py,plugin/cli/lifecycle_core/cli.py
done-criterion: kind check reports a declaration listing the reserved tend as a redundant-declaration finding (red-first); orientation shows the EFFECTIVE goal set (or marks tend reserved)
evidence: lc-64 build report, escalations (a) and (b)
blocked-by: NONE

## lc-71
grade: READY
requirement: migrate --merge run twice in one repo appends a SECOND residue item: the generated block is not source-derived so duplicate_bodies (reads source headlines) does not see it; --force rebuilds wholesale and is unaffected; record: lc-65 build report, surfaced item 2
goal: every-refusal-red-first
write-set: plugin/cli/lifecycle_core/migrate.py,test/test_migrate.py
done-criterion: a second --merge run books no duplicate residue item (dedup on the residue's own identity, not source headlines); red-first: two --merge runs produce exactly one residue item
evidence: lc-65 build report, merge dedup
blocked-by: decision is merge-of-N-carriers a real path worth the dedup, or is --merge-twice out of scope

## lc-73
grade: READY
requirement: merge refuses WHOLE on duplicate bodies (migrate.py:1432-1453) and no mechanism exists for the desk to STATE the per-entry call the refusal text promises it, so the RE-MIGRATION case (open entries already migrated, only closure sections newly recognizable, exactly lc-72's cross-repo criterion) is structurally uncompletable: 20 already-present-as-st-N duplicates block the 25 closures every run. Carries the unmet cross-repo remainder of lc-72's done-criterion. Record: statiker merge run 2026-09-10, FINDING merge_duplicate_body 20
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/migrate.py, test/test_migrate.py
done-criterion: a desk-stated duplicate disposition exists (form the fixing desk's design under this repo's laws); with all 20 statiker duplicates declared same-work, the merge routes the 25 closure bodies to ITEMS-DONE.md verbatim and conservation holds; red-first on the current whole-run refusal
evidence: executed 2026-09-10: lifecycle migrate --merge --from-done NONE in statiker gives FINDING [merge_duplicate_body] 20, NOTHING written, ITEMS-DONE.md archive still 0 of 25; the refusal text names the desk's call with no flag or verb to express it (migrate --help lists no such option)
blocked-by: decision which duplicate-disposition form the merge takes: per-entry flag, id-list, or byte-identity auto-skip (this repo's own design call)

## lc-74
grade: READY
requirement: the emit-site coverage scanner (--test) detects finding emissions by grepping the literal 'FINDING [row]' bracket idiom, so a site that returns exits.FINDING without the bracket — measured: cmd_item_statusline's unknown-grade '!n?' suffix, lc-45 dispatch report 2026-09-11 — is invisible to the scanner rather than red: the coverage check degrades silently exactly where a new one-line-output verb cannot afford the bracket. Two halves: register the statusline unknown-grade FINDING as a refusals.py row, and re-key the scanner on what cannot be omitted (exits.FINDING returns) rather than the bracket literal
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/refusals.py,plugin/cli/lifecycle_core/verbs.py,test/test_verbs.py
done-criterion: the statusline unknown-grade FINDING maps to a refusals.py row, and the emit-site scanner goes RED on a planted verb that returns exits.FINDING with no bracket and no row (red-first: plant exactly that, show the current scanner staying green, then the re-keyed one failing); must-not-move: every existing bracket-idiom site still maps, --test still CLEAN on the real tree
evidence: lc-45 closing report 2026-09-11 (lane finding 2, confirmed at the desk: --test CLEAN over the bracket-less FINDING path); verbs.py cmd_item_statusline FINDING branch at e98c3a4
blocked-by: NONE

## lc-75
grade: READY
requirement: NEXT UP (operator priority, 2026-09-11): item ids (lc-158/df-158) are honest addresses but carry nothing for the operator's eye — a descriptive shorthand beside the id ('df-158 corpus-review-run') would let the operator recognize items in listings, statusline heads, and close rounds without opening bodies. Requested from dotfiles df-158 as the motivating case
goal: lean-machinery-strict-checks
write-set: plugin/cli/lifecycle_core/verbs.py,plugin/cli/lifecycle_core/grammar.py,test/test_verbs.py
done-criterion: an optional slug slot: settable at admission (--slug, lowercase-hyphen token, uniqueness within the carrier enforced at add) and by amend; rendered beside the id in item ready listings and the item statusline head line where present. SETTLED SCOPE: display only — every verb still addresses by id alone; slug-as-alias is explicitly out (a second address namespace invites the truncated-identifier drift the corpus warns on) and would be its own future item with its own collision rules. Red-first: an add with --slug on a copy, the slug visible in ready and statusline output; must-not-move: slugless items render exactly as today, and a duplicate slug is refused at add with a FINDING
evidence: operator request 2026-09-11 (dotfiles session, df-158 as the recognition-failure case); dotfiles ITEMS.md head-rendering consumers: item ready, item statusline (e98c3a4)
blocked-by: NONE
amend-reason: 2026-09-11 backfill step folded into the lane (named in the close conversation; this amend is its carrier — the brief derives from the entry, so a step only in chat would never reach the lane)
amended-done-criterion: 2026-09-11 an optional slug slot: settable at admission (--slug, lowercase-hyphen token, uniqueness within the carrier enforced at add) and by amend; rendered beside the id in item ready listings and the item statusline head line where present. SETTLED SCOPE: display only — every verb still addresses by id alone; slug-as-alias is explicitly out (a second address namespace invites the truncated-identifier drift the corpus warns on) and would be its own future item with its own collision rules. THE LANE'S BRIEF ALSO CARRIES A BACKFILL STEP (operator, 2026-09-11): after the slot lands, slug the likely-head items of the two live carriers (lifecycle and dotfiles — the READY set's front, not all ~200 items) via item amend, so the statusline head is recognizable from day one rather than only for items added later. Red-first: an add with --slug on a copy, the slug visible in ready and statusline output; must-not-move: slugless items render exactly as today, and a duplicate slug is refused at add with a FINDING

## lc-76
grade: READY
requirement: The stray sweep is not part of the read-only pass and has no fourth disposition. kind sweep already names any tracked file resolving to no registered kind, a stray tracking .md included, but lifecycle audit, the walk a session actually runs, never mentions it: the audit prints 19 kind sections plus the judgment register and no sweep. And the sweep's own disposition vocabulary is closed at three (an instance of an existing kind, a repo-specific kind, or removed) with no fourth for a DECLARED CUSTOM whose consumer is named in the repo's CLAUDE.md. record: retirement pass R1 dispatch, 2026-09-12
goal: one-home-per-kind
write-set: plugin/cli/lifecycle_core/retire.py,plugin/cli/lifecycle_core/declaration.py,plugin/cli/lifecycle_core/refusals.py,test/test_declaration.py
done-criterion: lifecycle audit surfaces every tracked file that resolves to no registered kind, red-first against a planted stray tracking .md which the audit walk today never mentions while kind sweep names it in the same tree; AND the disposition vocabulary either gains the declared-custom fourth, which names its consumer in the repo's CLAUDE.md and is checked there rather than trusted, or the sweep's own text states why there is no fourth. MUST-NOT-MOVE: kind sweep keeps its current finding text and exit code, and a tree with no stray still reports CLEAN rather than silence. DESIGN CONSTRAINT (operator, first-hand, binding on this entry): kind admission means SHAPE REDESIGN, so a file this sweep pulls into a kind gets slot-structured entries a checker can anchor on POSITIONALLY, a closed grade vocabulary and explicit drain semantics, never a blind carry-over of its current free-prose form; content that must carry over as-is is marked LEGACY.
evidence: EXECUTED 2026-09-12 at 2c77eee on a scratch copy, both arms. Positive control first: kind sweep on the untouched tree reports FINDING [unregistered_persisted_thing] 1 tracked file, plugin/workflows/.gitkeep. Then a root TRACKING.md was planted and committed: the same sweep reports 2 tracked files and names TRACKING.md, so the stray .md case is ALREADY covered and only the placement and the fourth disposition are missing. The absence is shown rather than assumed: lifecycle audit over that same planted tree mentions neither TRACKING.md nor any stray, its output being the 19 kind sections, the walk summary line and the judgment register, while the sweep on the identical tree names the file.
blocked-by: decision whether a DECLARED CUSTOM with a named consumer becomes a fourth disposition beside the sweep's three, or whether every tracked file must resolve to a registered kind with no fourth and the CLAUDE.md consumer note is documentation rather than a disposition
amend-reason: 2026-09-12 2026-09-12 desk: fold the operator's machine-read exception registry, the tool-owned declaration class and its ownership-succession slot into the entry text, per the judgment desk's three design inputs
amended-done-criterion: 2026-09-12 lifecycle audit surfaces every tracked file that resolves to no registered kind, red-first against a planted stray tracking .md which the audit walk today never mentions while kind sweep names it in the same tree; AND the disposition vocabulary either gains the declared-custom fourth, which names its consumer in the repo's CLAUDE.md and is checked there rather than trusted, or the sweep's own text states why there is no fourth. MUST-NOT-MOVE: kind sweep keeps its current finding text and exit code, and a tree with no stray still reports CLEAN rather than silence. DESIGN CONSTRAINT (operator, first-hand, binding): kind admission means SHAPE REDESIGN — slot-structured entries a checker can anchor on POSITIONALLY, a closed grade vocabulary, explicit drain semantics, never a blind carry-over of free prose; carried-over content is marked LEGACY. EXCEPTION REGISTRY (operator, first-hand): the sweep's exception registry is MACHINE-READ from the repo's .claude/lifecycle.json (declared customs with named consumer, exempt globs); CLAUDE.md carries only the human-facing rationale pointing at it. The sweep anchors on the DECLARATION FILE, never on prose — a word-presence check over free prose both over-fires and under-fires. TOOL-OWNED CLASS (operator, first-hand): a declaration class 'tool-owned: <glob> -> <owning tool>[, succeeded by <tool>]' in lifecycle.json. Boundary is WHO WRITES: files a tool writes programmatically in its own format for its own consumption (run logs, fire logs, replay state) sit OUTSIDE the carrier machinery — no grades, no ratio, no retire walk — and INSIDE the accounting, so the sweep counts them accounted and 'tool state' never becomes an undeclared exemption. Retention and rotation policy live in the OWNING tool's repo, never the host repo. OWNERSHIP SUCCESSION is expressible: current owner plus optional successor, because a tool-owned path does not have one owner forever. Repo-residence must be justified in the entry: shared fixtures yes, caches and scratch to XDG data/state per existing doctrine; the gitignored variant is covered by promote-or-declare-local with the owner named.

## lc-77
grade: READY
requirement: No verb reports an item's EFFECTIVE slot values. This carrier's edit path is append-and-supersede by design: item amend writes a dated amended-<slot> line and retains the earlier one, item promote writes promoted-by and promote-reason, so a slot's effective value is the LAST amended-<slot> line where one exists and the base slot otherwise. Every reader outside the tool re-derives that rule by hand, and a hand-derived rule is what drifts. record: retirement pass R1 dispatch, 2026-09-12
goal: lean-machinery-strict-checks
write-set: plugin/cli/lifecycle_core/items.py,plugin/cli/lifecycle_core/cli.py,test/test_items.py
done-criterion: a READ-ONLY verb prints each item's effective slot values with the supersession rule applied (last amended-<slot> wins, base slot otherwise), in a form another program can consume. Red-first on an item carrying TWO amendments to ONE slot, asserting the LAST is reported and the first is not: lc-7 in this carrier is that case today, and lc-75 carried amended-done-criterion before this pass, so the red is drawn from the real carrier rather than a fixture. MUST-NOT-MOVE: the verb writes nothing at all (no carrier write, no commit, no lock), and an item with no amendments reports its base slots byte-unchanged. DESIGN CONSTRAINT (operator, first-hand, binding on this entry): this verb is what makes POSITIONAL slot anchoring possible for a future kind's checker, so it reads slots by position in the block and never by matching a word anywhere in free prose, which is the failure the backlog doctrine names.
evidence: Twice-written, which is this repo's own graduation threshold for a probe (the repo-tools kind: a probe used twice graduates or dies). The dispatching desk reports writing this extractor twice as throwaway across three repos in this wave. The rule it must encode is live in the real carrier rather than hypothetical: lc-7 carries TWO amended-evidence lines written minutes apart in this pass, the second correcting the first's basis, and lc-75 already carried amended-done-criterion at f09e32d. The rule also already exists inside the tool, in items.py _resolve_amendments, so the verb EXPOSES an existing rule rather than minting a second body for it, which is what would otherwise disagree first.
blocked-by: decision the verb's spelling and output form: a new item slots verb versus a flag on item ready, plain lines versus a machine-readable mode, and whether it reports one item or the whole carrier. This repo has been bitten by an unspelled verb before (the dropped lc-2), so the spelling is the desk's call

## lc-78
grade: READY
requirement: dev-notes/*-OBSERVATIONS.md carriers are capture-and-drain queues (four slots: incident plus basis, class, pre-formulated rule text, consumer plus drain seam) that are drained only by DOCTRINE today: no kind registers them, so they sit outside the flow and ratio machinery and outside the retire walk, and nothing detects a carrier that captures without draining. That is the assumed-delivery shape the doctrine itself names: a step with no named actor does not fail, it ACCUMULATES. record: retirement pass R1 dispatch, 2026-09-12
goal: one-home-per-kind
write-set: .claude/lifecycle.json,plugin/cli/lifecycle_core/declaration.py,plugin/cli/lifecycle_core/items.py,test/test_declaration.py,dev-notes/lifecycle-OBSERVATIONS.md
done-criterion: an OBSERVATIONS kind is registered with all six stages, so the carrier appears in the retire walk and its capture-against-drain reads like the item carrier's. THE SHAPE IS REDESIGNED, NOT CARRIED OVER (operator, first-hand, binding): entries become slot-structured so a checker anchors POSITIONALLY, the grade vocabulary is closed, and drain semantics are explicit. OPEN AND CLOSED SPLIT, named as part of the design rather than left to the migration: APPLIED and otherwise closed entries are HISTORY and go to a legacy segment or the done home marked LEGACY and not shape-checked, while OPEN entries re-book into the new shape, so only the queue migrates. Red-first on the real fill measured below, not a fixture. MUST-NOT-MOVE: dev-notes/ AS A DIRECTORY keeps its role and home, since sitting outside every operational load path is load-bearing separation; the kind covers the files within it, never the directory's placement.
evidence: CURRENT FILL, measured 2026-09-12. In THIS repo: dev-notes/ holds exactly one file, README.md, 3 lines, and no OBSERVATIONS carrier exists at all, which is what lc-8 books creating. In dotfiles: dev-notes/hooks-OBSERVATIONS.md is 429 lines (wc -l, the dispatcher's census re-run here) carrying 3 entries under ## headings. THE SHAPE ARGUMENT IS MEASURED IN THAT FILE: its status words sit in free prose rather than in a slot, so a scan for them returns 9 lowercase 'closed', 4 lowercase 'applied', 2 'OPEN', 2 'APPLIED', 2 'pending', 1 lowercase 'open', 1 'discarded' across 3 entries. A word-presence checker over that text fires on entries that merely DISCUSS a grade and is silenced by ordinary sentences carrying one, which is exactly why the doctrine says a carrier checker anchors on the slot's position and never on a word occurring anywhere.
blocked-by: decision the kind's slot schema and closed grade vocabulary, and where the LEGACY segment lives: a marked section inside the same file, or the repo's done home

## lc-79
grade: READY
requirement: There is no GROWTH-EXEMPT class, so closed history and unfinished machinery read alike. The growth vocabulary is three values (bounded-by-exit, compacted, unbounded-with-reason) and a kind whose declared exit action this build does not perform is printed as 'growth unchecked', which the walk summary counts: 8 kinds today. That one bucket holds two different facts, a kind whose exit is genuinely unimplemented and a kind that is CLOSED HISTORY with nothing to drain, and a reader cannot tell them apart. The journal, the design directives and the done-home archive are the second sort. record: retirement pass R1 dispatch, 2026-09-12
goal: one-home-per-kind
write-set: .claude/lifecycle.json,plugin/cli/lifecycle_core/declaration.py,plugin/cli/lifecycle_core/retire.py,test/test_declaration.py
done-criterion: journal entries, the design directives and the done-home archive are each registered as kinds carrying an explicit growth-exempt class: covered by the stray sweep so nothing about them is unregistered, and exempt from the flow alarm with the exemption DECLARED and its reason stated, because closed history has nothing to drain. Red-first: a growth-exempt kind must be visibly distinguishable in the retire walk from a kind counted 'growth unchecked' because its exit is unimplemented, so the proof is the walk summary separating today's single bucket of 8 into the two facts it currently conflates. MUST-NOT-MOVE: no kind gains an exemption by default, an undeclared stage stays a finding (invariant 2), and growth stays controlled by FLOW rather than size (R22), the exemption being a declared property of closed history and never a cap. DESIGN CONSTRAINT (operator, first-hand, binding): kind admission means SHAPE REDESIGN, so any of these carriers gaining a kind gets slot structure a checker anchors on POSITIONALLY and a closed vocabulary, with content that must carry over as-is marked LEGACY, which the done-home archive already models: it is held verbatim and not shape-checked.
evidence: MEASURED 2026-09-12 at 2c77eee. The declaration's growth values are exactly three: bounded-by-exit, compacted, unbounded-with-reason, read from .claude/lifecycle.json's 19 kinds. lifecycle retire prints per kind 'growth check: NOT CHECKED, the declared exit action X is not one this build performs (move), so there is no recorded event to look for. NOT the same answer as its exit never fired', and the walk summary line reads 'walk: 19 kind(s); grew-without-exit 1 (items); growth unchecked 8 (refusal-registry, git hooks, plugin manifest, marketplace manifest, maintenance notes, git config, plugin cache versions, legacy backlog)'. POPULATION NOTE, so the entry is not read wider than it is: journal entries IS registered here (home JOURNAL.md, growth unbounded-with-reason) and the done-home archive is inside the done-bodies kind (compacted, archive held verbatim), while docs/directives has NO home in this repo at all, the only docs kind being audits at docs/audits/*.md and docs/ holding exactly one file. So this entry adds a CLASS to the vocabulary and re-declares three populations under it, rather than registering three absent kinds.
blocked-by: decision whether growth-exempt is a FOURTH value in the growth vocabulary or a separate declared flag beside the existing three, and whether the exemption is per kind or per segment (the done-home archive is a segment inside a kind, not a kind)

## lc-80
grade: READY
requirement: The documented Verify command for the Python suite is RED and silently runs 34 fewer tests than the suite has. CLAUDE.md's Verify block says python3 -m unittest discover -s test -p 'test_*.py' -t . which sets the top-level dir to the repo root, so the modules load as test.<name> and two of them fail at import on their sibling imports (test_migrate_residue imports test_migrate, test_tend_goal imports test_init). Both the red and the under-run are invisible to a reader who trusts the documented form. record: retirement pass R1 lane baseline, 2026-09-12
goal: lean-machinery-strict-checks
write-set: CLAUDE.md,test/test_migrate_residue.py,test/test_tend_goal.py
done-criterion: the documented Verify command runs the WHOLE suite green, and the count it reports is the suite's real count. Red-first is already in hand and must be reproduced as the arrangement: at f09e32d with a clean tree, the documented form gives 'Ran 292 tests / FAILED (errors=2)' while the same discover WITHOUT -t . gives 'Ran 326 tests / OK', one variable. MUST-NOT-MOVE: whichever side is repaired, the sibling imports and the package-relative form must not BOTH be supported silently, since two import shapes for one suite is how the count diverged unnoticed; and the fix is not simply deleting -t . from the doc unless that form is shown to run all 326
evidence: EXECUTED 2026-09-12 at f09e32d, clean tree, single-variable control, both arms in one run. WITH -t . (the documented form): Ran 292 tests, FAILED (errors=2), the two errors being ModuleNotFoundError 'No module named test_migrate' at test/test_migrate_residue.py:34 and 'No module named test_init' at test/test_tend_goal.py:38. WITHOUT -t .: Ran 326 tests, OK. So the documented command both fails AND exercises 34 fewer tests, and the 34 is the quiet half: a reader who fixed only the two errors would still be running a short suite. FOREIGN RED, not this lane's: the tree was clean at f09e32d and this lane touched no test file. The sibling imports date to 18ca4e5 (lc-65), which is when the divergence could first have appeared.
blocked-by: NONE
