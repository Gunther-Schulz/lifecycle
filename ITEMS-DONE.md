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

## Archive (pre-migration)

