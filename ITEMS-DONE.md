# This repo had NO legacy closure home. The absence was STATED at
# migration time (`--from-done NONE`), never inferred from a missing
# file: the archive below is empty because there was nothing to
# archive, which is a different fact from nothing having been read.

schema: 2

## lc-15
grade: DONE
requirement: An item whose `blocked-by` names another item by id is validated against nothing. A blocker of the declared form `<prefix>-<n>` pointing at an id the carrier does not contain passes `item check` CLEAN and `kind check` CLEAN — measured, by accident, with a real mistake: lc-14 was written `blocked-by: lc-15` when no lc-15 existed, and both checkers reported clean. The consequence is a PERMANENT SILENT PARK: the item never surfaces in `item ready` because it reads as blocked, and nothing ever reports that the blocker is fictional, so it can neither drain nor be noticed.
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/items.py,plugin/cli/lifecycle_core/refusals.py,test/test_items.py
done-criterion: red-first against a carrier carrying a blocker id that does not resolve: a named finding, green once the id resolves or the blocker is retyped. The three other blocker forms (`decision <q>`, `evidence <predicate>`, NONE) must NOT fire — they resolve against nothing by design, and a check that cannot tell them apart from a dangling id would fire on legitimate work.
evidence: executed: `item check` -> "CLEAN — 0 shape finding(s)", `kind check` -> "CLEAN — 19 kind(s) registered", both with the dangling id in place. REF_TYPES (declaration.py:103) is ("lane","verb","hook","session","producer","operator") — DECLARATION reference types; an item-carrier id is a different namespace and appears in none of them. DISTINCT from the refusal table's recorded `route_set_unwatched`, which is about the declaration resolver narrowed to `lane:`; this is the ITEM carrier's own blocker slot.
blocked-by: NONE
superseded-by: lc-28

## lc-44
grade: DONE
requirement: item close accepts --reason on a DONE close and writes it NOWHERE — not into the moved body, not into the ledger, not into the commit message body. Measured 2026-08-27 in dotfiles: df-143 closed with a 900-char reason naming its commit ref and verification basis; grep for that ref afterwards returns 0 in ITEMS.md, 0 in ITEMS-DONE.md, 0 in LEDGER.md. Reading confirms it: in cmd_item_close, reason is bound once and consumed only inside the 'if args.drop:' branch (ledger dropped: line). The silent direction is the whole defect — the caller sees 'moved df-N to ITEMS-DONE.md (grade DONE)' plus a commit and reads that as a complete closure record.
goal: one-home-per-kind
write-set: plugin/cli/lifecycle_core/verbs.py (cmd_item_close), and the close verb's --help text
done-criterion: a DONE close persists its reason where the doctrine says closures live — items leave BY COMMIT REF, and today the ref cannot survive the verb that closes the item. Red-first: close an item with a reason naming a ref, grep all three carriers for that ref, expect 0 on the old arm and non-zero on the new. Must-not-move: a --drop close still writes exactly one ledger dropped: line and no second copy; an omitted --reason on a DONE close behaves as today. Decide and state which home a DONE reason takes — the moved body or a ledger closed: line — and refuse the OTHER, because two homes for one fact is the paraphrase-drift the carrier doctrine forbids.
evidence: dotfiles LEDGER.md 2026-08-27 carries df-143's closure record written BY HAND with a note saying why; dotfiles df-1 lost its entire closure basis the same way, and the desk reported that basis to the judgment desk as persisted when it was not.
blocked-by: NONE
amend-reason: 2026-08-27 judgment desk ruling 2026-08-27; the two hand-written LEDGER lines for df-1 and df-143 STAY as the record after this lands — no migration of them, one fact one home going forward
amended-done-criterion: 2026-08-27 RULED 2026-08-27 (judgment desk): a DONE reason lives in the MOVED BODY, never the ledger — two lines, 'closed-reason: <date> <text>' and 'closed-ref: <sha>', following the promote precedent (no slot separator inside a value), written in the SAME buffer write as the move. A DROP keeps its ledger line, because a dropped body may be pruned and its record cannot live only there; the ledger stays decisions, supersessions and drops. Red-first: close an item with a reason naming a ref, grep all three carriers for that ref — 0 on the old arm, non-zero in ITEMS-DONE.md on the new. Must-not-move: a --drop close still writes exactly one ledger dropped: line and no second copy; an omitted --reason on a DONE close behaves as today; no closed-reason/closed-ref line appears on a DROP. DISCHARGE IT ALSO CARRIES: the first DONE closure landing a closed-ref after this is the real-repo proof of the ITEMS-carrier accept half of df-143's guard fix, which C1 could only exercise in scratch fixtures.
amend-reason: 2026-08-27 the booked write-set named verbs.py and the --help text only; the slot REGISTRATION in items.py was required and landed in cbfaee6, and the ref refusal needs a registry row in refusals.py or the emit-site coverage check fails
amended-write-set: 2026-08-27 plugin/cli/lifecycle_core/verbs.py (cmd_item_close, _resolve_refs, move_to_done), plugin/cli/lifecycle_core/cli.py (the --ref flag and the close verb's --help), plugin/cli/lifecycle_core/items.py (CLOSED_REASON/CLOSED_REF and their DONE_ONLY_SLOTS registration, landed cbfaee6), plugin/cli/lifecycle_core/refusals.py (row closed_ref_unresolvable), test/test_verbs.py
closed-reason: 2026-08-27 item close now writes closed-reason: and closed-ref: on the moved body; --ref added, optional, absences spoken aloud, an unresolvable ref refused before the move. Verified at the artifact by the desk: 275 tests OK, rows 73, prove-rows exit 0
closed-ref: 8a5d664b5c00283eab67e8983c8fc29b93d7ed1b

## lc-48
grade: DONE
requirement: done_home_check fires blocked_in_done_home on a body whose blocker item close ALREADY recorded as moot, so the check reports a defect on the exact case the close verb handles: measured on dotfiles ITEMS-DONE.md df-141, record: wave-4 desk 2026-08-27
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/items.py,test/test_items.py
done-criterion: done_home_check treats a decision blocker as discharged when the block carries a blocker-moot: line whose text equals the effective blocker DETAIL, and still fires when a closed body carries a live blocker with NO matching moot record. Red-first on df-141 real body: the finding fires today and must not after. Must-not-move: a blocker-moot recording a DIFFERENT question does not discharge, and the 5 blocks whose effective blocker is NONE stay clean
evidence: wave-4 desk, executed 2026-08-27 over dotfiles ITEMS-DONE.md: 6 blocks carry blocker-moot:, exactly 1 (df-141) fires. The other 5 (df-1, df-39, df-64, df-73, df-75) had blocked-by amended to NONE before close, the workaround rather than the design. items.py:1289 classifies the effective blocked-by and never reads blocker-moot; verbs.py:1579 writes the note without clearing the slot, which the append-only model forbids anyway. The docstring at items.py:1251 says close clears it, the code only annotates: spec and verifier disagree
blocked-by: NONE
amend-reason: 2026-08-27 the desk's evidence slot named a mechanism it had inferred from reading verbs.py:1579 rather than measured. The lane measured it. Correcting in place because a wrong mechanism in a closed item's record is what the next reader builds on
amended-evidence: 2026-08-27 wave-4 desk 2026-08-27, CORRECTED at integration by the lane's measurement: 6 blocks in dotfiles ITEMS-DONE.md carry blocker-moot:, exactly 1 (df-141) fired. THE DESK'S ORIGINAL MECHANISM WAS WRONG and is superseded here: it said item close writes the note without clearing the slot. It DOES clear it (_clear_blocker, verbs.py:456, rewrites blocked-by: to NONE). The real mechanism, measured by the lane and re-read at the artifact by the desk: an amended-blocked-by: line resolves LAST-WINS over the cleared slot, and removing that amendment would be the in-place rewrite the append-only model forbids. df-141 carries blocked-by: NONE plus an amended-blocked-by: decision plus a matching blocker-moot:. The conclusion stands (the CHECK moves, not the close) but it rests on last-wins amendment resolution, not on a close that fails to clear
closed-reason: 2026-08-27 done_home_check consults blocker-moot: and discharges a decision blocker whose moot record matches EXACTLY. Verified at the effect site on real data: dotfiles done-home went exit 2 with one blocked_in_done_home against df-141 to exit 0, 0 findings, the other 5 blocks unchanged
closed-ref: 8a5d664b5c00283eab67e8983c8fc29b93d7ed1b

## lc-49
grade: DONE
requirement: _check_blocker validates blocker TYPING and dangling refs but never ledger-storability, so item add, item park and item amend all still write decision questions the ledger cannot store. lc-40 closed the MINT and left the three hand-write doors open, record: wave-4 desk 2026-08-27
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/verbs.py,test/test_verbs.py
done-criterion: _check_blocker refuses a decision-typed blocker the ledger cannot store, using the ledger OWN predicate imported rather than restated (the shape migrate._ledger_storable already uses), with a FINDING naming the rephrase. Red-first on the real text that got in: df-135 pre-repair value. Must-not-move: evidence-typed, item-id and NONE blockers unaffected, and the 67 repaired texts all still pass
evidence: wave-4 desk 2026-08-27. verbs.py:630-663 read in full: the function checks blocker_untyped and dangling_reference only. NOT inferred from the read, measured live in the carrier: dotfiles df-135 reached ITEMS.md carrying a decision question containing the ledger slot separator, written by item amend --blocked-by, which retyped an evidence blocker to a decision one. Repaired in dotfiles ec47c3c; the door it came through is still open
blocked-by: NONE
closed-reason: 2026-08-27 _check_blocker refuses a decision blocker the ledger cannot store, using the ledger's own imported predicate, closing add/park/amend at once. Verified by the desk in three arms: unstorable REFUSED, storable accepted, evidence-typed carrying the separator still accepted
closed-ref: 8a5d664b5c00283eab67e8983c8fc29b93d7ed1b

## lc-35
grade: DONE
requirement: The leak scan finds a foreign home path inside an item BODY (ITEMS.md:300) and the repo declares public:true, so the finding is live even with no remote today — record: wave-4 desk 2026-08-27, re-run at c915bc2 and again at 22adf7e, unchanged
goal: enforce-the-invariants
write-set: UNKNOWN
done-criterion: node tools/absence-scan.mjs --git-range ..HEAD returns 0 findings over ITEMS.md, with the instrument first shown live on a planted positive so a zero is not an unread instrument
evidence: executed twice by the wave-4 desk: "FINDING foreign-path  ITEMS.md  line 300  (481 chars, #ee54ac7003b3)", exit 2, identical at c915bc2 and 22adf7e. .claude/lifecycle.json declares public:true and leak-scan.source-scope-foreign-path:true, whose own reason note records that the SHIPPED foreign-path class is scoped corpus — so the declaration and the shipped scanner disagree, which is the residue this item names
blocked-by: NONE
blocker-moot: does the item BODY change (rewrite the path out of it) or does the foreign-path class scope change (corpus -> source) to honour the declaration
closed-reason: 2026-08-27 NOT a leak: the guard over-fired. ITEMS.md:300 matched the root-path token inside the ordinary filename reports/root.md, because the class permitted a following dot. The literals are deliberately not quoted here: written with a leading boundary they make this carrier match the very guard the closure is about, which blocked a push seconds after this body was written. Repaired at the guard with a leading boundary lookbehind, counter-armed in both directions over ten arms. The item's two offered options (rewrite the body, rescope the class) were both wrong; the third was that a check firing on a non-defect is failing
closed-ref: 70bc93c30130807c25cc96626cfb9b9d217a1591

## lc-40
grade: DONE
requirement: migrate writes decision-blocker QUESTIONS containing the ledgers own slot separator, so the blocker can never be answered: ledger add decision REFUSES the question (FINDING ledger_body, correctly — an escaped spelling would put two forms of every value in the file), while lc-26 resolves a decision blocker by QUESTION-SLOT EQUALITY. The two mechanisms are individually right and jointly make the item permanently blocked
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/migrate.py,plugin/cli/lifecycle_core/ledger.py,test/test_migrate.py
done-criterion: a blocker question minted by migrate is storable as a ledger question verbatim — red-first on the real text "regrade: was READY under the old carrier — READY is judged, never inherited", which today is refused by ledger add and therefore unanswerable
evidence: measured by the wave-4 desk 2026-08-27 over dotfiles ITEMS.md: 99 decision-blocked items, 69 of them carry " — " in the question. The dominant text (66 items) is the regrade question the judgment desk GO-ed a single clearing line for; ledger add decision refused it: "FINDING [ledger_body] the decision question contains the slot separator". The remaining 30 (chiefly "regrade: fill goal, write-set, done-criterion and evidence, or drop") are separator-free and answerable today
blocked-by: NONE
amend-reason: 2026-08-27 DECIDED at the wave-4 peer desk 2026-08-27: option ONE, migrate sanitises at mint time. The other two are refused on the carrier doctrine, not on cost. Escaping in the ledger puts two spellings of every value in the file and the reader cannot tell which it is looking at, which lc-40 own requirement already says. Matching on a normalised form is a comparison over transformed text standing in for the parsed body, so the stored question and the matched question would differ by construction, and that is the paraphrase-drift the doctrine forbids. The minter is the ONE place that controls the text: a question that cannot be stored is a question that must never be minted, so the fix belongs where it is written, not where it is read. SEPARATELY DECIDED: the 69 already-written blockers ARE repaired in place by a batched item amend, using the fixed minter exact output, at this desk after the code lands; B2 pass 2 waits on that pass. NOTE the irony and it is evidence not decoration: this decision could not be recorded through ledger add decision, because the blocker question itself carries the separator and the ledger correctly refuses it. The defect bit its own item on the way to being fixed
amended-blocked-by: 2026-08-27 NONE
closed-reason: 2026-08-28 the defect is fixed and the criterion that outlived it is superseded here. lc-40 asked that a minted blocker question be storable VERBATIM; that is unsatisfiable by design, since the ledger refuses separator-bearing text and the same design refuses both escaping and normalisation. The satisfiable property is STORABLE: the minter never produces a question the ledger would refuse. Option ONE landed at c5164f7 (migrate sanitises at mint time) and a146b62 put the minting form beside the predicate that judges it, in the shared grammar module. Verified at this desk 2026-08-28: c5164f7 is an ancestor of HEAD, and the ledger refusal still fires at HEAD on a separator-bearing question with the tree untouched by the refused call
closed-ref: c5164f7, a146b62

## lc-64
grade: DONE
requirement: goal is per-repo DOMAIN vocabulary (design 3.1), so repo-self-work — method decomposition, hook retirement, migration residue — advances no goal and cannot be booked; record: cache-fix design 3.1b (operator 2026-08-28)
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/declaration.py,plugin/cli/lifecycle_core/init.py
done-criterion: item add --goal tend and item check accept tend in every repo with nothing declared; a non-tend undeclared goal still refuses (red-first); init's effective goal set = declared union {tend}
evidence: cache-fix design 3.1b, the plugin-reserved meta-goal
blocked-by: NONE

## lc-65
grade: DONE
requirement: migrate converts the carrier and leaves its residue — un-decomposed method file, live old-carrier readers, oversized frozen archive — for a human to notice, and humans don't (the assumed-delivery class); record: cache-fix design 3.1b, 4 row 1
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/migrate.py
done-criterion: migrate --apply emits a fixed set of tend items for its residue, each PARKED with a typed blocker, in the migration report; red-first: a source with a method file plus live BACKLOG readers produces exactly those parked tend items
evidence: cache-fix design 3.1b (seeding), 4 row 1 (the migration report)
blocked-by: NONE
amend-reason: 2026-08-28 scope lc-65 to migrate's generically-detectable residue; method-file decomposition rides the file sweep, not migrate (design 3.1b refinement, operator GO 2026-08-28)
amended-done-criterion: 2026-08-28 migrate --apply emits tend items for the residue it can detect generically — old-carrier readers still live, and an over-tripwire frozen archive — each PARKED with a typed blocker, in the migration report; the method file is the file-sweep's job (design 3.1b + 4), NOT migrate's; red-first: a source with live BACKLOG readers plus an oversized archive produces exactly those two parked tend items and no method-file item
amend-reason: 2026-08-28 scope lc-65 to the readers class only; drop the archive class — R22 forbids the size cap my 3.1b clause invented, and the archive is the retire lane's compaction exit (build session halt, operator round; design 3.1b amended)
amended-done-criterion: 2026-08-28 migrate's carrier-writing run (not --report-only) emits ONE parked tend item for the old-carrier readers still live: grep tracked files (git ls-files) for the source basenames excluding sources/successors/report, book only when hits>0, hit paths in evidence, blocker decision 'every consumer migrated or declared exempt'; counted SEPARATELY from source entries (baseline = n_items + n_residue + archive_count; reconciliation identity over source entries only), ids after the migrated block, slots real text (not UNKNOWN); red-first: a source with live readers produces exactly that one item. The method file (file sweep) and the frozen archive (retire-lane compaction, R22 — no size cap) are NOT booked here.
closed-ref: 18ca4e5

## lc-69
grade: DONE
requirement: The dropped reference tier (design 3.3: no reference tier survives; what fits no kind is dropped) leaves cross-cutting REASONING that justifies a SET of laws with no home; worth re-confirming now a concrete instance exists; record: begehung r5, design 3.3 :288-291
goal: one-home-per-kind
write-set: docs/directives/carrier-rework-design-2026-08-26.md@cache-fix
done-criterion: operator re-confirms drop-or-home for cross-cutting reasoning; if home, the kind is declared; if drop, the decision is recorded with the instance that tested it
evidence: begehung r5 reference-tier row
blocked-by: NONE
blocker-moot: re-confirm: drop cross-cutting reasoning, or give it a declared home
closed-ref: f0aae22

## lc-72
grade: DONE
requirement: migrate's entry test (bold-led or grade-word-led bullets) misses DATE-LED closure bullets ('- 2026-08-23 — **title**…', the accretion doctrine's own closure-line shape) under the carrier's closure heading: all 25 of statiker's ## Done bodies classed 'non-entry prose' and excluded from the done-home archive, so retiring the source after a clean-reading report silently loses the closure record — record: statiker docs/audits/migration-report-2026-09-10.md
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/migrate.py, plugin/cli/lifecycle_core/tests (red-first fixture, exact file the fixing desk's to name)
done-criterion: red-first: a fixture with a date-led ungraded bullet under the closure heading routes to the done home verbatim (red under the current recognizer); statiker re-run with --merge routes its 25 archive bodies and both identities still hold
evidence: statiker docs/audits/migration-report-2026-09-10.md — 25 'non-entry prose', every one under ## Done and date-led; source blob a115998c; the report's own closure-shape table says an entry under the closure heading archives verbatim, so the recognizer contradicts the rule table
blocked-by: NONE
amend-reason: 2026-09-10 write-set pointer corrected: the suite is top-level test/, the booked path plugin/cli/lifecycle_core/tests never existed (the fixing lane's report, slot e)
amended-write-set: 2026-09-10 plugin/cli/lifecycle_core/migrate.py, test/test_migrate.py
closed-reason: 2026-09-10 recognizer widened for date-led bullets in closure sections only; red-first stash-proof pasted in the lane report; suite 286 with the two known pre-existing import errors; verified at the artifact by the dispatcher
closed-ref: dd81507

## lc-45
grade: DONE
requirement: dotfiles' statusline renders backlog pressure on EVERY render in EVERY repo, today via 'backlog-census.py --statusline BACKLOG.md'. After the carrier freeze that reader must come here, and no statusline verb exists (grep -rn statusline over the plugin: 0 hits). The two available fallbacks are both defects: pointing the old renderer at ITEMS.md parses 0 bullets and renders a silent 0R.0P, and leaving it on the frozen file renders a number frozen at its last value forever, indistinguishable from a live one.
goal: lean-machinery-strict-checks
write-set: plugin/cli/lifecycle_core/verbs.py (a compact one-line render), and the CLI's verb table
done-criterion: one verb emits a single short line fit for a statusline — counts plus the schedulable head, no multi-line report — and it is CHEAP: it runs on every statusline render, so a full carrier parse per call is the wrong shape and the criterion states which. It exits per the CLI's own convention (0 clean, 2 finding, 3 could not verify) and NEVER emits a pass-shaped number it could not compute: a carrier it cannot parse yields the could-not-verify exit and a visibly non-numeric line. Red-first: the old renderer against ITEMS.md, showing the silent zero this verb exists to prevent. Consumers, which must NOT parse rendered prose to get this: dotfiles claude-worktime/config.sh and claude/hooks/session-scan.py.
evidence: dotfiles claude-worktime/config.sh:301; the freeze dispositions record claude/records/carrier-freeze-dispositions-2026-08-27.md names this reader the sharpest degrading-check in its set; the C lane surfaced the missing verb as a gap rather than bridging it (2026-08-27).
blocked-by: NONE
closed-reason: 2026-09-11 item statusline landed: single line-pass render, three answers at statusline width; head id a stated syntactic approximation (item ready --head authoritative, divergence case locked as a regression test). Entry's red premise corrected in operation: the old renderer's failure is a VANISHED line (statusline_optin gates on the missing Grades: declaration, empty stdout exit 0), not the entry's claimed silent 0R.0P. Follow-on scanner blind spot booked as lc-74
closed-ref: e98c3a42e7479a92720381ac7342828210166316

## lc-9
grade: DROPPED
requirement: The declaration turns the source-scope foreign-path leak class ON, and the shipped scanner has no such scope: its foreign-path class is scoped corpus, so the declaration is honoured by nothing
goal: enforce-the-invariants
write-set: tools/absence-scan.mjs, test/absence-scan.test.mjs
done-criterion: a planted foreign home path in a tracked .md in this repo fires foreign-path and the same file without it is clean, both shown
evidence: .claude/lifecycle.json leak-scan.reason; tools/absence-scan.mjs CLASSES, the foreign-path entry scoped corpus; JOURNAL J6
blocked-by: NONE
amend-reason: 2026-09-12 retirement pass 2026-09-12: the drop basis belongs in the body that moves to the done home, not in the 300-char ledger reason
amended-evidence: 2026-09-12 RETIREMENT PASS 2026-09-12, DROP BASIS (executed at f09e32d): the requirement says the shipped scanner's foreign-path class is scoped corpus. FALSE — tools/absence-scan.mjs:611-612 declares name 'foreign-path', scope 'source'; the comment at :128 dates the widening to 2026-08-26. This item's OWN done-criterion executed as a discriminating pair on a scratch copy of f09e32d, one variable (the planted path): a tracked .md with no absolute home path gives 'absence-scan: clean', exit 0; the SAME file carrying /home/<another-user>/projects/thing/config.yaml gives 'FINDING foreign-path probe-lc9.md line 3 (65 chars, #4a44ca6dd7fa)', exit 2. Both arms shown. ORIGINAL EVIDENCE, retained: .claude/lifecycle.json leak-scan.reason; tools/absence-scan.mjs CLASSES, the foreign-path entry scoped corpus; JOURNAL J6.
blocker-moot: the scanner is a byte-identical copy of claude-code-cache-fix's and both copies move together, so the widening lands there first

## lc-11
grade: DROPPED
requirement: item add leaves a 0-byte ITEMS.md.lock in the repo root and nothing ignores it — record: wave2 L1 booking run, 2026-08-26
goal: lean-machinery-strict-checks
write-set: plugin/cli/lifecycle_core/verbs.py,decision:lock-lifetime-vs-gitignore
done-criterion: after item add, either the lock is gone or the repo's .gitignore (written by init) covers it; git status shows no stray lock
evidence: observed after four item add runs in claude-code-cache-fix: ITEMS.md.lock present, 0 bytes, git check-ignore returns no match
blocked-by: NONE
amend-reason: 2026-09-12 retirement pass 2026-09-12: the drop basis belongs in the body that moves to the done home, not in the 300-char ledger reason
amended-evidence: 2026-09-12 RETIREMENT PASS 2026-09-12, DROP BASIS (executed at f09e32d): the done-criterion reads 'either the lock is gone or the repo's .gitignore (written by init) covers it'. The second branch is satisfied: .gitignore:9 is '*.lock' under a five-line comment naming the carrier lock by design section, 'git check-ignore -v ITEMS.md.lock' returns '.gitignore:9:*.lock ITEMS.md.lock', and init.py:143 has needed = ['!.claude/lifecycle.json', 'ITEMS.md.lock'] so a declaring repo gets the line from init. The named decision (deletion versus gitignore) is therefore answered by the build. SEPARATE AND STILL TRUE: one stale 0-byte ITEMS.md.lock from 2026-08-26 sits in this root; it is inert (items.py:241-262 uses advisory flock, so a leftover file blocks no writer) and is deleted in this same pass as an untracked leftover. ORIGINAL EVIDENCE, retained: observed after four item add runs in claude-code-cache-fix: ITEMS.md.lock present, 0 bytes, git check-ignore returns no match.
blocker-moot: whether the lock is released by deletion or covered by the .gitignore init writes

## lc-25
grade: DROPPED
requirement: item add writes the carrier and never commits it on --join new or --join merge-into: commit_paths is called only from _do_supersede, while --no-commit is advertised on the verb as though a commit were the default for every join, and neither a "committed:" nor a "NOT COMMITTED" line is printed — record: wave-3 step-0, judgment-desk GO
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/verbs.py,test/test_items.py
done-criterion: every join of item add either commits its own write by pathspec or says NOT COMMITTED, never silence; red-first by running item add --join new against a clean tree and asserting git status is clean afterwards, which fails on the current build
evidence: observed at f2c37fe: `item add --join new` for lc-23 printed "added lc-23 [READY] -> ITEMS.md" with no commit line and left " M ITEMS.md"; committed by hand by pathspec as 2e9f20c. Source: commit_paths defined verbs.py:406, called at :646 (_do_supersede) and :1222; _do_new at :656 and _do_merge at :582 have no call site. The consequence is the one commit_paths own docstring names — in a shared work tree the dirty carrier rides out under a co-writer pathspec commit
blocked-by: NONE
amend-reason: 2026-09-12 retirement pass 2026-09-12: the drop basis belongs in the body that moves to the done home, not in the 300-char ledger reason
amended-evidence: 2026-09-12 RETIREMENT PASS 2026-09-12, DROP BASIS (executed at f09e32d on a scratch copy, never the live tree): the done-criterion is 'every join of item add either commits its own write by pathspec or says NOT COMMITTED, never silence; red-first by running item add --join new against a clean tree and asserting git status is clean afterwards'. Run: item add --join new printed 'committed: lifecycle: add lc-76', HEAD moved 6f3601b to cf775e4, and git status --porcelain returned empty. The silent-write behaviour this item booked is gone. The NOT COMMITTED half is also shipped and was exercised repeatedly in this same pass by --no-commit, which prints it explicitly. ORIGINAL EVIDENCE, retained: observed at f2c37fe, item add --join new for lc-23 printed no commit line and left ' M ITEMS.md'; committed by hand as 2e9f20c.

## lc-26
grade: DROPPED
requirement: No verb clears a typed blocker once its decision is answered: item has only {check,add,ready,park,close,ratio}, park only SETS a blocker, and an answered decision leaves the item reading blocked forever — record: wave-3 step 0, judgment-desk ruling 2026-08-27
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/verbs.py,plugin/cli/lifecycle_core/items.py,test/test_items.py
done-criterion: a decision blocker resolves against a ledger decision line naming the same question, and item ready re-derives blocked-ness from the ledger rather than from the stored slot; red-first on an item whose decision blocker has an answering ledger line, which today still reads blocked
evidence: probed in a throwaway clone at f2c37fe: `item park lc-23 --blocked-by NONE` is refused with FINDING [parked_without_typed_blocker] ("Prose only — or nothing — was given (NONE)") and lc-23 blocked-by is unchanged; `item --help` lists exactly check, add, ready, park, close, ratio — no verb takes a blocker off. Adjacent to lc-15 permanent-silent-park shape, one slot over
blocked-by: NONE
amend-reason: 2026-09-12 retirement pass 2026-09-12: the drop basis belongs in the body that moves to the done home, not in the 300-char ledger reason
amended-evidence: 2026-09-12 RETIREMENT PASS 2026-09-12, DROP BASIS (executed at f09e32d on a scratch copy): the requirement's surface claim is that item has only {check,add,ready,park,close,ratio} and no verb takes a blocker off. FALSE at HEAD: the surface is {check,add,ready,amend,promote,park,close,ratio,statusline}, and 'item amend lc-23 --blocked-by NONE' succeeded, writing 'amended-blocked-by: 2026-09-12 NONE' plus its amend-reason and committing. The done-criterion's second half (item ready re-derives blocked-ness from a ledger decision line rather than the stored slot) is also shipped, evidenced inside this carrier by lc-62, whose own measurement is item ready reporting UNBLOCKED citing LEDGER.md:299 once the ledger question matched. THE RESIDUAL IS lc-62, not this item: answering by substance rather than by verbatim question text still leaves an item blocked. ORIGINAL EVIDENCE, retained: probed in a throwaway clone at f2c37fe, item park lc-23 --blocked-by NONE refused with FINDING [parked_without_typed_blocker].

## lc-27
grade: DROPPED
requirement: The carrier is append-only in practice because no verb edits a block: item add is the only writer, and there is no path to clear a blocker, amend a body, or correct a slot — so every correction to a booked item is either a new item or a law-8 violation — record: wave-3 step 0, three sightings in one step
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/verbs.py,plugin/cli/lifecycle_core/cli.py,plugin/cli/lifecycle_core/items.py,test/test_items.py
done-criterion: an edit path exists that LEAVES A RECORD: an amendment is a new dated block or slot-line that supersedes, never an in-place rewrite, so law 8 and the append-only ethic both hold; red-first on a booked item needing a slot correction, which today has no verb at all
evidence: three sightings in wave-3 step 0, all executed: (1) clear a blocker — `item park lc-23 --blocked-by NONE` refused, parked_without_typed_blocker (lc-26, this items first instance); (2) amend a body — the lc-10 live-hit sighting could not be appended to lc-10 by any verb; (3) correct a slot — no verb takes a slot value. `item --help` lists exactly check, add, ready, park, close, ratio
blocked-by: NONE
amend-reason: 2026-09-12 retirement pass 2026-09-12: the drop basis belongs in the body that moves to the done home, not in the 300-char ledger reason
amended-evidence: 2026-09-12 RETIREMENT PASS 2026-09-12, DROP BASIS (executed at f09e32d on a scratch copy): the done-criterion asks for 'an edit path that LEAVES A RECORD: an amendment is a new dated block or slot-line that supersedes, never an in-place rewrite, so law 8 and the append-only ethic both hold'. item amend is exactly that and answers all three recorded sightings: (1) clear a blocker, executed, 'amended-blocked-by: 2026-09-12 NONE'; (2) amend a body and (3) correct a slot, both by the same verb, which prints 'The earlier line(s) are RETAINED; the new one supersedes' and appends a dated amend-reason plus an amended-<slot> line. item promote is the second such recorded act. Superseding lines rather than rewrites is what keeps law 8 intact. ORIGINAL EVIDENCE, retained: three sightings in wave-3 step 0, all executed; item --help then listed exactly check, add, ready, park, close, ratio.

## lc-39
grade: DROPPED
requirement: There is NO path from NEW to READY: grade is written once at admission (verbs.py:526), item amend REFUSES --grade, and item ready PROMOTES NOTHING — an item admitted NEW can never be graded READY however complete its slots later become, so the carriers head is empty by construction
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/verbs.py,plugin/cli/lifecycle_core/cli.py,test/test_lanes.py,tools/prove-rows.py
done-criterion: an item whose slots were completed by amendment can be graded READY by an explicit desk act recording who judged it and why, and item ready --head then lists it; red-first on the dotfiles state — 133 items with full slots, grade NEW, head reporting 0 schedulable
evidence: wave-4 desk 2026-08-27, after the dotfiles grade pass: 329 slots filled across 131 items, then item ready --head over 135 live items printed "head: 2 READY, 0 schedulable now"; the only READY items are ones BORN complete (df-134, df-135). df-1 after amendment: "grade is NEW, not READY. THIS VERB PROMOTES NOTHING". Source: verbs.py:526 sits in the add path, no other verb writes a grade
blocked-by: NONE
amend-reason: 2026-09-12 retirement pass 2026-09-12: the drop basis belongs in the body that moves to the done home, not in the 300-char ledger reason
amended-evidence: 2026-09-12 RETIREMENT PASS 2026-09-12, DROP BASIS (executed at f09e32d on a scratch copy): the requirement is 'There is NO path from NEW to READY'. FALSE at HEAD. item promote ships and is the explicit desk act law 10 requires. Executed, three arms: (a) promote a NEW item holding an UNKNOWN slot returns FINDING [ready_with_unknown_slot] and writes nothing; (b) promote a slot-complete but BLOCKED item returns FINDING [promote_while_blocked] and writes nothing; (c) after clearing that blocker by amend, promote wrote 'grade: READY' plus promoted-by and promote-reason lines, printed 'The grade is the DESK's, not this verb's: nothing here derived it from the slots' and committed. So the arrow exists and it is judged, never derived. ORIGINAL EVIDENCE, retained: wave-4 desk 2026-08-27, 329 slots filled across 131 items and item ready --head still printing 'head: 2 READY, 0 schedulable now'; verbs.py:526 then the only grade write.
blocker-moot: an explicit promotion act (law 10: READY is judged, never inherited) versus re-deriving grade from the amendment-resolved slots at read time — the latter makes READY automatic, which law 10 forbids, so the promotion act is the recommended shape

## lc-54
grade: DROPPED
requirement: test/absence-scan.test.mjs has a test asserting the walk collects files under proxy/, a directory this repo does not have, so the suite has been RED on an environment premise it does not pin, record: baselined 2026-08-27 before the foreign-path repair
goal: lean-machinery-strict-checks
write-set: test/absence-scan.test.mjs
done-criterion: The test either pins its fixture inside the repo or skips with a named reason; the suite exits 0. Red-first: it fails today with 'the walk collected no file under proxy/'. Must-not-move: the assertion still fires where a proxy-like tree DOES exist, so the repair is a pinned fixture and not a deleted test
evidence: node --test test/absence-scan.test.mjs, run before and after the foreign-path repair: EXIT=1 both times, the SAME single failing test 'source: every UUID in a tracked SOURCE_SCANNABLE file is on the synthetic allowlist' at :743, message 'the walk collected no file under proxy/'. Stated as the baseline in 70bc93c so the repair's own proof could not borrow a pre-existing red
blocked-by: NONE
amend-reason: 2026-09-12 retirement pass 2026-09-12: the drop basis belongs in the body that moves to the done home, not in the 300-char ledger reason
amended-evidence: 2026-09-12 RETIREMENT PASS 2026-09-12, DROP BASIS: duplicate of lc-24, which books the same red (the proxy/ anchor in the shared absence-scan test) and was booked first, at wave-3 step 0. Re-measured at f09e32d: node --test test/absence-scan.test.mjs gives tests 62 / pass 61 / fail 1 / skipped 0, the single failure being 'source: every UUID in a tracked SOURCE_SCANNABLE file is on the synthetic allowlist' with 'the walk collected no file under proxy/'. Merged into lc-24 rather than kept as a sibling, per the backlog doctrine's merge rule, and lc-24's evidence now carries this body's two contributions: the baseline stated in 70bc93c so the foreign-path repair's proof could not borrow a pre-existing red, and the must-not-move arm that the assertion still fires where a proxy-like tree does exist, so the repair is a pinned or derived anchor and never a deleted test. ORIGINAL EVIDENCE, retained: node --test run before and after the foreign-path repair, EXIT=1 both times, the same single failing test at :743.

## lc-57
grade: DROPPED
requirement: there is no read-by-goal query: item ready takes only an ident or --head, and no verb answers which items carry a given goal. lc-16 named this arrow as a query and it is still unbuilt, so the goal slot is written on every item and read by nothing
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/items.py,plugin/cli/lifecycle_core/cli.py,test/test_items.py
done-criterion: a goal-scoped read exists and returns only items carrying that goal, red-first: today item ready --goal is rejected at argparse, which is a usage error and not the defect, so the red is the missing OUTPUT on a form the CLI accepts
evidence: wave-5 T walk 2026-08-28: item ready --help lists only [--head] [ident]; the full verb surface item {check,add,ready,amend,promote,park,close,ratio} carries no query verb. Source item lc-16 from the 27-item transition sort
blocked-by: NONE
amend-reason: 2026-09-12 retirement pass 2026-09-12: the drop basis belongs in the body that moves to the done home, not in the 300-char ledger reason
amended-evidence: 2026-09-12 RETIREMENT PASS 2026-09-12, DROP BASIS: duplicate of lc-16, which books the same missing goal-scoped read and was booked first. This body names lc-16 as its own source ('Source item lc-16 from the 27-item transition sort'), so the duplication is stated in the entry itself. Re-confirmed at f09e32d: item ready --help lists only [--head] [ident] and the item surface carries no goal-scoped query. Merged into lc-16 per the merge rule; lc-16's evidence now carries this body's contribution, the red-first shape that item ready --goal is rejected at argparse, which is a usage error and not the defect, so the red is the missing OUTPUT on a form the CLI accepts. ORIGINAL EVIDENCE, retained: wave-5 T walk 2026-08-28.

## lc-59
grade: DROPPED
requirement: no verb declares a lane in a repo's lanes list. lane new says so in its own help: it writes the lane file as a stub and does NOT declare it in this repo's lanes list. So a lane can exist as a file and be invisible to the board, which is the router's input, and nothing closes the gap between the two
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/lanes.py,plugin/cli/lifecycle_core/declaration.py,test/test_lanes.py
done-criterion: a lane created by lane new is declarable by a verb, and a lane FILE present but undeclared is a finding rather than silence, red-first on this repo whose declaration reads lanes: (empty, declared not absent) while lane files can be created
evidence: wave-5 L walk 2026-08-28: lane new --help states the non-declaration outright; the lane verb surface is {list,register,new} with no declare; kind list shows lanes: (empty)
blocked-by: NONE
amend-reason: 2026-09-12 retirement pass 2026-09-12: the drop basis belongs in the body that moves to the done home, not in the 300-char ledger reason
amended-evidence: 2026-09-12 RETIREMENT PASS 2026-09-12, DROP BASIS: duplicate of lc-13 plus lc-14, which together book the same lane-declaration arrow and were booked first. lc-43's evidence already sorts them as ONE arrow: 'register lc-13+lc-14 as one arrow'. This body restates both halves, that a lane created by lane new is not declarable by a verb and that a lane FILE present but undeclared is silence rather than a finding. Re-confirmed at f09e32d: the lane surface is {list,register,new}, lane register puts a REPO on the roster rather than a lane in this repo's lanes list, and lane new --help still states the non-declaration outright. Merged into both existing entries per the merge rule, with this body's executed confirmations carried in each. ORIGINAL EVIDENCE, retained: wave-5 L walk 2026-08-28; kind list shows lanes: (empty).

## lc-1
grade: DROPPED
requirement: PARKED 2026-08-26 — the "leak scan on the plugin repo" refusal row has no firing input the shipped scanner can detect — record: BACKLOG.md:14
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: BACKLOG.md:14-24
blocked-by: NONE
amend-reason: 2026-09-12 retirement pass 2026-09-12: BACKLOG.md is deleted in this pass, so the drop basis and the source body are inlined here rather than left behind a line-range pointer into a deleted file
amended-evidence: 2026-09-12 SOURCE BODY INLINED 2026-09-12 from BACKLOG.md:14-24: 'PARKED 2026-08-26 — the leak scan on the plugin repo refusal row has no firing input the shipped scanner can detect. Design §3.9 names a planted /home/<user>/... path in a template; measured the same day, that input scans CLEAN (exit 0) while a s-+8-hex token in the same file fires capture-key-prefix (exit 2). Missing evidence/decision: whether the scanner gains a foreign-path class (a change to a byte-identical copy, so it lands in claude-code-cache-fix first) or the row firing input is amended to the token form. Both are the judgment desk calls.' DROP BASIS, executed at f09e32d: the first branch was taken and has shipped. The scanner now carries foreign-path at absence-scan.mjs:611-612 with scope 'source', dated by the comment at :128 to 2026-08-26. The exact input the source body measured as CLEAN now fires: a tracked .md carrying /home/<another-user>/projects/thing/config.yaml gave 'FINDING foreign-path' exit 2, while the same file without it gave 'absence-scan: clean' exit 0. One variable, both arms shown. Legacy pointer: BACKLOG.md:14-24.

## lc-2
grade: DROPPED
requirement: PARKED 2026-08-26 — the shape check has no assigned verb in the design's CLI surface — record: BACKLOG.md:25
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: BACKLOG.md:25-31
blocked-by: NONE
amend-reason: 2026-09-12 retirement pass 2026-09-12: BACKLOG.md is deleted in this pass, so the drop basis and the source body are inlined here rather than left behind a line-range pointer into a deleted file
amended-evidence: 2026-09-12 SOURCE BODY INLINED 2026-09-12 from BACKLOG.md:25-31: 'PARKED 2026-08-26 — the shape check has no assigned verb in the design CLI surface. Built as lifecycle item check; the brief D-c list does not contain it. Missing decision: the desk chosen spelling, and whether the pre-commit wiring (§3.9 calls it a pre-commit shape check) is the plugin install step or the repo own hook. Nothing else depends on the answer today.' DROP BASIS, executed at f09e32d, both halves answered. SPELLING: 'item check' is in the shipped surface, {check,add,ready,amend,promote,park,close,ratio,statusline}, and runs clean here. WIRING: plugin/.claude-plugin/plugin.json declares a git-hooks.pre-commit entry pointing at hooks/pre-commit, whose registration field states the answer outright, that the install symlinks .git/hooks/pre-commit at this script and never touches core.hooksPath because a repo-local core.hooksPath would replace the machine dispatcher. So it is the plugin install step, and the declaration says why. Legacy pointer: BACKLOG.md:25-31.
blocker-moot: the missing decision named in the source body — answer it, then re-grade

## lc-4
grade: DROPPED
requirement: PARKED 2026-08-26 — nothing creates `~/.config/lifecycle/repos`, so `lane list` answers `roster_absent` on this machine — record: BACKLOG.md:40
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: BACKLOG.md:40-50
blocked-by: NONE
amend-reason: 2026-09-12 retirement pass 2026-09-12: BACKLOG.md is deleted in this pass, so the drop basis and the source body are inlined here rather than left behind a line-range pointer into a deleted file
amended-evidence: 2026-09-12 SOURCE BODY INLINED 2026-09-12 from BACKLOG.md:40-50: 'PARKED 2026-08-26 — nothing creates ~/.config/lifecycle/repos, so lane list answers roster_absent on this machine. The roster is the router input and its creation is outside every write boundary wave 1 was given. Measured: lane list today exits 2 with roster_absent; with a scratch roster listing three repos it prints the full longhand board, so the verb works and the file does not exist. Missing decision: WHO owns the roster, the plugin install step, the operator dotfiles, or a lane register verb the CLI does not have. Nothing in wave 1 depends on the answer.' DROP BASIS, executed at f09e32d: the third option was taken and has shipped. 'lifecycle lane register' is in the surface {list,register,new} and its own help reads 'put a repo on the roster, the router input'. Run with --dry-run from a scratch checkout it printed 'DRY RUN, would append <repo> to /home/g/.config/lifecycle/repos' and 'roster: 0 repo(s) listed today, 1 after', so the verb both owns the file and creates it. The named decision is answered by the build. Legacy pointer: BACKLOG.md:40-50.
blocker-moot: the missing decision named in the source body — answer it, then re-grade

## lc-5
grade: DROPPED
requirement: PARKED 2026-08-26 — the done home's blocks are never shape-checked, so `blocker-moot:` and `superseded-by:` are unknown slots nothing reports — record: BACKLOG.md:51
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: BACKLOG.md:51-60
blocked-by: NONE
amend-reason: 2026-09-12 retirement pass 2026-09-12: BACKLOG.md is deleted in this pass, so the drop basis and the source body are inlined here rather than left behind a line-range pointer into a deleted file
amended-evidence: 2026-09-12 SOURCE BODY INLINED 2026-09-12 from BACKLOG.md:51-60: 'PARKED 2026-08-26 — the done home blocks are never shape-checked, so blocker-moot: and superseded-by: are unknown slots nothing reports. item check runs check_file over the LIVE carrier only; the done home is parsed for conservation and duplicates, and both callers ignore parsed.problems. Measured: a closed body carrying blocker-moot: passes every check today. Missing decision: either the two annotations become real slots in SLOTS, or the done home gets its own shape check with them exempted by name. Both are design decisions and both change what a done body IS.' DROP BASIS, executed at f09e32d: BOTH branches shipped, which over-answers the either/or. items.py:103 declares DONE_ONLY_SLOTS = ('superseded-by', 'blocker-moot', CLOSED_REASON, CLOSED_REF), so the annotations are real named slots rather than unknowns; and 'item check' now prints its own done-home verdict, 'done home: N closed block(s), archive 2 line(s) held verbatim and not shape-checked' followed by 'done-home check: CLEAN, 0 finding(s)', so the done home has its own shape check with a stated scope. Legacy pointer: BACKLOG.md:51-60.
blocker-moot: the missing decision named in the source body — answer it, then re-grade

## lc-6
grade: DROPPED
requirement: PARKED 2026-08-26 — `LEDGER.md` cannot carry a prose header — record: BACKLOG.md:61
goal: UNKNOWN
write-set: UNKNOWN
done-criterion: UNKNOWN
evidence: BACKLOG.md:61-69
blocked-by: NONE
amend-reason: 2026-09-12 retirement pass 2026-09-12: BACKLOG.md is deleted in this pass, so the drop basis and the source body are inlined here rather than left behind a line-range pointer into a deleted file
amended-evidence: 2026-09-12 SOURCE BODY INLINED 2026-09-12 from BACKLOG.md:61-69: 'PARKED 2026-08-26 — LEDGER.md cannot carry a prose header. The parser requires the first non-blank line to be schema: <n>; anything else is a shape finding before it or an unreadable line after it. Measured while creating claude-code-cache-fix ledger, which is therefore exactly schema: 1, a carrier in a public repo that cannot say what it is for. Missing decision: whether the ledger parser gains a comment-line rule (# or <!-- -->), and if so whether ledger check counts comment lines in its third answer.' DROP BASIS, executed at f09e32d on a scratch copy: the parser gained the rule. ledger.py:88 declares a comment line in the PREAMBLE, matched by shape, and the comment at :189-192 records why. Exercised rather than read: a three-line '#'-prefixed prose header was planted at the top of LEDGER.md and 'ledger check' returned 'ledger check: CLEAN, 0 shape finding(s), 0 unreadable line(s)', exit 0. That answers both halves, since the comment lines counted as neither a finding nor unreadable. Legacy pointer: BACKLOG.md:61-69.
blocker-moot: the missing decision named in the source body — answer it, then re-grade

## lc-17
grade: DONE
requirement: A second carrier migration has no MERGE mode. With ITEMS.md present, migrate returns FINDING [migrate_would_overwrite] (migrate.py:633) and the refusal's own text says --force would REPLACE real work with a re-derivation. So 'N old carriers into one item carrier' has no execution path at all — not a hard case, an absent one
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/migrate.py,test/test_migrate.py
done-criterion: a second --from against a populated ITEMS.md appends without touching existing entries, with conservation asserted across both sources; red-first on the current refusal
evidence: verified here at cf92ad9: migrate.py:633 emits migrate_would_overwrite. Peer measured :630-639 on 6badd58
blocked-by: NONE
closed-reason: 2026-09-12 FIXED AND NEVER CLOSED, found by the 2026-09-12 retirement pass. --merge mode shipped in 9f8350f: cli.py:502 adds --merge, migrate.py:1349 bypasses the migrate_would_overwrite refusal under it, the merge branch appends via append_blocks leaving existing entries byte-for-byte, and merge_conservation() asserts the identity per source and in total. The entry's premise -- 'no execution path at all' -- is dead. Verified twice on independent axes: a sonnet lane's executed read of the live module, and this desk's own re-run against the commit history. Citation drift recorded: the entry cited migrate.py:633 for the refusal, now at :1352.
closed-ref: 9f8350f

## lc-18
grade: DONE
requirement: A '## Done' SECTION migrates as OPEN work. CUT_SECTIONS = ('Grades',) only (migrate.py:80), so the tool models closures as a separate FILE (--from-done) while both dotfiles carriers keep theirs as a Done section of the same file; build_items then writes every migrated entry with grade NEW (migrate.py:359, comment at :346 'EVERY MIGRATED ENTRY IS OPEN'). Measured by the peer on the real files: 7 already-closed root entries and 1 corpus entry would be written back as open work. '--from-done NONE' is not the escape — both carriers genuinely have archives, so stating zero would be a false zero
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/migrate.py,test/test_migrate.py
done-criterion: a source carrying its closures as a '## Done' section migrates them to the done home, not to ITEMS.md as NEW; red-first on a fixture with both an open and a closed section, asserting the closed entries do NOT appear in the open carrier
evidence: verified here at cf92ad9: CUT_SECTIONS at :80 is ('Grades',); grade NEW hardcoded at :359. Peer measured :367 on 6badd58; the line moved, the substance holds. Counts are the peer's, not re-measured here
blocked-by: NONE
closed-reason: 2026-09-12 FIXED AND NEVER CLOSED (retirement pass 2026-09-12). Closure sections now route before the grade word: closure_sections_for() derives headings from CLOSURE_SECTIONS_DEFAULT and classify() short-circuits to archival, so a Done-section entry no longer lands as NEW. Landed f3f7517. Executed lane fixture plus this desk read of the live module. Drift: CUT_SECTIONS cited :80 now :145 and is a separate narrower mechanism; grade-NEW cited :359 now :708, reached only by entries not routed to closure.
closed-ref: f3f7517

## lc-19
grade: DONE
requirement: AMENDED 2026-08-26 — the original diagnosis (a _GRADE_WORD anchoring defect) was WRONG and is replaced; the measurement stands. The real cause: UNCLASSIFIED is a MISSING RULE, not a missing match. classify() matches the grade word and then does RULES.get(word); a word with no rule yields grade=None → UNCLASSIFIED. The RULES key set is BUST, CANDIDATE, FINDING, HANDOFF, NEW, OPEN, PARKED, PARTLY, POINTER, READY, RECORD — there is NO DONE and NO DROPPED. So every properly-graded closure in a source carrier is unclassified by construction. DROPPED is the sharp one: it belongs to the plugin's OWN default grade vocabulary (READY/PARKED/DONE/DROPPED) and still has no rule. Same root cause as lc-18 — the tool expects closures to arrive via --from-done, so the in-carrier closure vocabulary was never given rules
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/migrate.py,test/test_migrate.py
done-criterion: the closure vocabulary classifies rather than falling through — DONE and DROPPED at minimum, plus a declared way for a repo to map its own closure words; red-first on a fixture carrying DONE and DROPPED entries, asserting they do NOT land in the open carrier. A word with no rule must still be reported as unclassified rather than guessed at — the fix is rules, never a looser matcher
evidence: verified here at 40b9c36 by executing the module: sorted(RULES.keys()) returns the 11 words above, 'DONE' in RULES is False, 'DROPPED' in RULES is False. Counts are the peer's executed measurement over files this session did not open, CORRECTED by them post-booking: root BACKLOG.md UNCLASSIFIED 83 = DONE 76 + DROPPED 5 + ERLEDIGT 1 + RESOLVED 1; claude/BACKLOG.md 18 of 66 = DONE 14 + DROPPED 2 + TRACED 1 + EXECUTED 1 (66/18 post-dates their e3b3ebf, which added one Done entry; use these, not the earlier 65/17)
blocked-by: NONE
closed-reason: 2026-09-12 FIXED AND NEVER CLOSED (retirement pass 2026-09-12). The entry own original probe is now a before/after pair: DONE in RULES and DROPPED in RULES were both False at booking and are both True at this HEAD, because CLOSURE_RULES derives from items.GRADES_CLOSED rather than a hardcoded list. Landed f3f7517. REMAINDER NOT CLOSED BY THIS: the criterion also asked for a declared way for a repo to map its OWN closure words; GRADES_CLOSED is a fixed tuple, so that half is unimplemented and books separately after this pass rather than being silently absorbed here.
closed-ref: f3f7517

## lc-21
grade: DONE
requirement: A closed entry whose grade word is NOT at the bullet start is read as UNGRADED and migrated as OPEN work. classify() gives an entry with no leading grade word UNGRADED_RULE (migrate.py:67, applied at :219), whose grade is NEW — so it does not become unclassified and does not refuse; it silently lands in the new carrier as live work. The idiom that trips it puts a real grade word mid-title, e.g. a bullet opening with a topic and carrying DONE and a date later in the same bold span. THIS IS THE WORSE OF THE TWO MIGRATION DEFECTS: lc-19 is a loud refusal (an unclassified entry announces itself), this one is a silent wrong answer that reopens finished work.
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/migrate.py,test/test_migrate.py
done-criterion: a bullet whose grade word sits mid-title classifies by that word, red-first on a fixture drawn from the real idiom, and a closed entry never lands in the open carrier. AND the over-fire half: a bullet carrying a capitalised NON-grade word mid-title must still read as ungraded — without that arm a matcher loosened until the counts improve scores identically to one that got the distinction right.
evidence: split out of lc-19 on the reporting peer's own correction, 2026-08-26 — they had conflated two mechanisms and retracted the diagnosis while the measurement held. Verified here at 40b9c36 by executing the module: UNGRADED_RULE at migrate.py:67 is ('NEW', ...) and is assigned at :219, so an ungraded entry migrates OPEN rather than unclassified. Peer measurement, over files this session did not open: 7 root entries and 1 corpus entry, all with grade_word None, all sitting in a '## Done' section, would be written back as open work.
blocked-by: NONE
closed-reason: 2026-09-12 FIXED AND NEVER CLOSED (retirement pass 2026-09-12), with an ACCEPTED DEVIATION recorded rather than glossed. closure_word_in_title() at migrate.py:402 catches a closure word mid-title, and the over-fire arm holds: a capitalised NON-closure word mid-title still reads ungraded. DEVIATION: the criterion asked that such an entry classify BY that word; the shipped fix REFUSES it as AMBIGUOUS. Accepted by this desk because the file own doctrine at migrate.py:39-41 makes refusal the answer where the source is ambiguous, which supersedes the criterion wording. The silent-wrong-answer defect the entry named is gone either way.
closed-ref: f3f7517

## lc-13
grade: DONE
requirement: Design 3.8b requires that a lane or workflow file the declaration does not list is UNREGISTERED, a finding. No verb produces it: LANES_DIR is used only to build a path from an ALREADY-DECLARED name (lanes.py:147) and no glob or iterdir over the lanes directory exists anywhere in the package. The registration invariant therefore holds in ONE direction only — a declared lane with no file is caught by read_lane, an undeclared file on disk is invisible to every verb
goal: enforce-the-invariants
write-set: plugin/cli/lifecycle_core/lanes.py,plugin/cli/lifecycle_core/refusals.py,plugin/cli/lifecycle_core/roster.py,test/test_lane_new.py
done-criterion: a lane file under lanes/ absent from the declaration's lanes list produces a named finding, red-first against a planted undeclared file and green after declaring it; AND test_lane_list_says_nothing_about_an_undeclared_door is INVERTED in the same change — it currently pins the pre-fix behaviour and will go red when this is fixed, which is correct but must not be read as a regression
evidence: structural: LANES_DIR used only at lanes.py:147 to build a declared name's path, zero glob/iterdir over it anywhere in the package. behavioural: lane list against a repo carrying an undeclared lanes/x.md printed 'declared lanes: 0 — EMPTY, declared rather than absent' and named neither x nor lanes/x.md
blocked-by: NONE
amend-reason: 2026-09-12 retirement pass 2026-09-12: lc-59 restated this entry and lc-14 as one item; merged into the two existing entries rather than left as a sibling, and dropped in the same pass.
amended-evidence: 2026-09-12 structural: LANES_DIR used only at lanes.py:147 to build a declared name's path, zero glob/iterdir over it anywhere in the package. behavioural: lane list against a repo carrying an undeclared lanes/x.md printed 'declared lanes: 0 — EMPTY, declared rather than absent' and named neither x nor lanes/x.md. RE-CONFIRMED 2026-09-12 (retirement pass, executed at f09e32d): the lane verb surface is {list,register,new}; lane register puts a REPO on the roster, not a lane in this repo's lanes list. MERGED IN lc-59 (wave-5 L walk 2026-08-28), which re-found this gap and lc-14's together as one item and is dropped as a duplicate in this pass; its contribution is the executed confirmation that lane new --help states the non-declaration outright and kind list shows lanes: (empty).
closed-reason: 2026-09-12 FIXED 2026-08-27 AND FALSELY RE-CONFIRMED OPEN 2026-09-12. lane_files_on_disk at lanes.py:212 globs the lanes dir and check_lanes_registered wires it into the declaration validator, emitting lane_undeclared (declaration.py:1152, refusals.py:1551), so the registration invariant holds in BOTH directions. METHOD FINDING, recorded because it outlives this entry: the 2026-09-12 amendment on this block re-confirmed the defect open after checking only the lane VERB surface, a scoped read settling an unscoped absence; the fix lives on the kind-check route and predates that amendment by two weeks.
closed-ref: 120c733

## Archive (pre-migration)

