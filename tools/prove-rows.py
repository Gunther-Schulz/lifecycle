#!/usr/bin/env python3
"""Red-first proof for every refusal row, RE-RUNNABLE rather than remembered.

WHY THIS IS A TOOL AND NOT A TRANSCRIPT. "A check counts only once it has
gone RED on the real defect" — demonstrated, with the arrangement recorded.
The demonstration was being done by hand: disable one named condition, run
the roster, watch one row go dark, restore by file copy. That reasoning is
exactly what does not survive into the next session, and a row added next
month gets no proof at all unless someone remembers the ritual. So the
arrangement lives here, executable, one entry per row.

WHAT IT ASSERTS, and it is a PAIR like every row itself. For each mutation:

  * the named row's verdict CHANGES  — the row was reading that condition;
  * every row that changed proves THE SAME REFUSAL — the mutation removed
    that condition and not its neighbours.

The second half is the one that catches a mutation deleting adjacent
machinery instead of the named condition. A mutation that darkens four
unrelated rows has not proven any of them; it has proven that something
large broke.

WHY THE SECOND HALF IS NOT "EXACTLY ONE ROW", which is what it used to say.
Two roster rows can prove two firing inputs of ONE refusal — the roster
declares that with `Row.finding_row`, and `declaration_ignored` and
`declaration_ignored_tracked` are the case: an ignored declaration, once
untracked and once committed. The single site where THAT refusal is decided
is one branch, so a mutation there necessarily darkens both, and "exactly
one" made the honest mutation indistinguishable from a careless one. The
sibling set is DERIVED from the roster's own `finding_row` mapping, never
hand-listed here: a hand list would be a second body for the same fact and
would go stale the day a row was added. For a row with no sibling the
assertion is bit-for-bit the old one.

A ROW WHOSE MUTATION DARKENS NOTHING is the loud case: the condition it
names is not what produces its verdict, so the row is passing for a reason
nobody wrote down.

RESTORE IS BY FILE COPY, never `git checkout`/`restore`/`stash` — those take
the whole tree, and this runs in a work tree that has uncommitted work in it
by construction. `__pycache__` is cleared around every arm: a stale `.pyc`
would let the unmutated module answer for the mutated source, which reads
exactly like a row that does not discriminate.

IT REFUSES TO START OVER A MUTATION TARGET THAT ALREADY DIFFERS FROM HEAD,
and the restore under `try/finally` is not a substitute for that check. The
`finally` covers an ordinary exception; it covers neither a SIGKILL nor a
harness timeout nor an operator Ctrl-C, and a run cut down between the write
and the restore leaves the injected mutation LIVE in the tree with nothing
marking that it did. Measured 2026-09-15: a desk ran this tool on a live
shared checkout, killed it mid-arm, and left a one-line mutation standing in
`migrate.py` — found only by sha256-ing every tracked file against its HEAD
blob, because nothing was looking.

The startup refusal is the half that survives that kill, and it turns BOTH
hazards into ONE computable predicate: residue from an earlier crashed run,
and a co-writer's uncommitted work in a file this tool is about to overwrite.
Neither needs the question "is this checkout shared?", which is not
computable. A dirty mutation target is a FINDING rather than a
could-not-verify because the tool DID form a verdict — it read both sides and
found them different; what it refuses is to proceed, not to answer.

THE COMPARISON IS SHA, NEVER GREP. Searching the source for the mutated form
is the instrument that looks cheapest and is wrong: the replacement text of
at least one recorded arrangement occurs LEGITIMATELY in its own file at
HEAD, so a grep reports a false positive on a clean tree and nothing
distinguishes it from residue. Only the working bytes against the committed
blob are authoritative — and `git status` is not that instrument either: its
stat cache keys on (mtime, size), so a restore preserving both can leave a
byte-identical file reading modified, and a same-size edit under a kept
timestamp can leave a changed one reading clean.

    python3 tools/prove-rows.py            # every row that has a mutation
    python3 tools/prove-rows.py <ident>…   # only these

Exit: 0 every proof held · 2 a proof failed, OR a file this run would mutate
already differs from HEAD (the refusal above) · 3 a mutation anchor was not
found (the source moved under the arrangement — the arrangement is stale,
which is a finding about THIS file, not about the row).
"""

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLI = REPO / "plugin" / "cli"
CORE = CLI / "lifecycle_core"

CLEAN, FINDING, COULD_NOT_VERIFY = 0, 2, 3

#: (row ident, file, anchor, replacement, what the anchor IS).
#:
#: The anchor is the single place the row's finding is DECIDED — not a place
#: near it. Each replacement removes that decision and nothing else, which is
#: what makes "exactly one row changes" a meaningful assertion rather than a
#: coincidence.
MUTATIONS = [
    # SPELLED FROM LINE START TO LINE END, like every other anchor here. It
    # used to begin mid-line, at the `[` of the argument list; `anchor_hits`
    # accepts whole-line runs ONLY, so the mid-line spelling would have gone
    # to COULD NOT VERIFY. Same site, same effect — only the spelling moved.
    ("declaration_ignored_tracked", "declaration.py",
     '        p = subprocess.run(["git", "-C", str(repo), "check-ignore",\n'
     '                            "--no-index", str(rel)],',
     '        p = subprocess.run(["git", "-C", str(repo), "check-ignore",\n'
     '                            str(rel)],',
     "the `--no-index` flag that lets check-ignore see a TRACKED path"),

    ("unknown_grade_write", "verbs.py",
     "        if grade not in items_mod.GRADES:",
     "        if False:",
     "the closed grade vocabulary's test on write"),

    ("foreign_origin_item", "verbs.py",
     "    if here != ctx.repo.resolve():",
     "    if False:",
     "the origin comparison between the writer's repo and the target"),

    ("join_undisposed", "verbs.py",
     "    if found and not join:",
     "    if False:",
     "the refusal to write while the join is undisposed"),

    ("new_without_absence", "verbs.py",
     "    if not absence:",
     "    if False:",
     "the named-absence requirement on `new`"),

    ("cost_test_veto", "verbs.py",
     '    return "veto", (',
     '    return "clear", (',
     "the cost test's veto verdict on a one-file one-hunk write-set"),

    ("cost_test_unverified", "verbs.py",
     "    if hunks is None:\n        return \"unverified\", (",
     "    if False:\n        return \"unverified\", (",
     "the cost test's refusal to clear what it could not evaluate"),

    ("blocker_untyped", "verbs.py",
     "    kind, detail = items_mod.classify_blocker(value, ctx.prefix)\n"
     "    if kind is None:",
     "    kind, detail = items_mod.classify_blocker(value, ctx.prefix)\n"
     "    if False:",
     "the typed-blocker test in `_check_blocker`"),

    # THE ANCHOR IS THE GATE, NOT THE PARSE BRANCH INSIDE IT, and the reason
    # is that the narrower mutation darkens NOTHING: the plant's predicate is
    # prose, so neutralising the `sh -n` test only lets it fall through to the
    # probe, which exits 2 on the same syntax error and emits the same row.
    # A mutation whose row keeps firing proves the row, not the mutation.
    # THE SECOND LINE RUNS TO ITS OWN END, not to a convenient stop inside
    # it. `    if kind == "evidence":` occurs twice in this file, so the
    # comment line is what disambiguates — but cut mid-line it was a PREFIX
    # match, satisfied by any longer line starting the same way, which is the
    # failure `anchor_hits` rejects at the far end.
    ("blocker_predicate_broken", "verbs.py",
     "    if kind == \"evidence\":\n"
     "        # THE THIRD DOOR IS WHY IT IS HERE. `item amend --blocked-by` "
     "reaches",
     "    if False:\n"
     "        # THE THIRD DOOR IS WHY IT IS HERE. `item amend --blocked-by` "
     "reaches",
     "the mint-time lint's gate on an `evidence` blocker — removed, prose "
     "booked into a shell slot is admitted and the item waits in nobody's "
     "court"),

    ("dangling_reference_item", "verbs.py",
     "    if detail not in known:",
     "    if False:",
     "the referential-integrity test on an item-id blocker"),

    ("parked_without_typed_blocker", "verbs.py",
     "    value = (args.blocked_by or \"\").strip()\n"
     "    kind, detail = items_mod.classify_blocker(value, ctx.prefix)\n"
     "    if kind in (None, \"none\"):",
     "    value = (args.blocked_by or \"\").strip()\n"
     "    kind, detail = items_mod.classify_blocker(value, ctx.prefix)\n"
     "    if False:",
     "`item park`'s own typed-blocker requirement"),

    ("promote_without_judgment", "verbs.py",
     "    if not by or not reason:",
     "    if False:",
     "`item promote`'s requirement that the judgment be signed and reasoned"),

    ("promote_while_blocked", "verbs.py",
     '    if not state.startswith("UNBLOCKED"):',
     "    if False:",
     "`item promote`'s test that nothing is still blocking the item"),

    ("ready_with_unknown_slot_promote", "verbs.py",
     "    unknown = items_mod.unknown_slots_of(it)\n"
     "    if unknown:",
     "    unknown = items_mod.unknown_slots_of(it)\n"
     "    if False:",
     "the UNKNOWN-slot test at the WRITE path — the read-path site in "
     "`cmd_item_ready` is a DIFFERENT anchor proving the same refusal, "
     "which is why this one names two lines and not the assignment alone"),

    ("amend_without_reason", "verbs.py",
     "    reason = (args.reason or \"\").strip()\n"
     "    if not reason:",
     "    reason = (args.reason or \"\").strip()\n"
     "    if False:",
     "`item amend`'s requirement that the amendment record its own WHY"),

    ("amend_nothing_to_amend", "verbs.py",
     "    if not updates:",
     "    if False:",
     "`item amend`'s requirement that some slot actually be named"),

    ("duplicate_id_cross_home", "items.py",
     "    both = [(d.ident, live[d.ident], d.line)\n"
     "            for d in done_parsed.items if d.ident in live]",
     "    both = []",
     "the cross-home id intersection"),

    # BOTH sign rows anchor on the same branch, with OPPOSITE replacements:
    # each sends its OWN case down the wrong side. Disabling the branch
    # outright, or making the whole identity report clean, would darken both
    # rows at once and prove neither — the mutation that removes adjacent
    # machinery rather than the named condition.
    ("conservation_short", "items.py",
     "    if delta < 0:",
     "    if delta < -999:",
     "the SHORT branch — a shortfall then reports under the surplus row, "
     "which is the wrong diagnosis and the wrong repair"),

    ("conservation_surplus", "items.py",
     "    if delta < 0:",
     "    if True:",
     "the SURPLUS branch — a surplus then reports as loss, which is exactly "
     "the defect this row was found by"),

    # NOT `if False:` here. Removing the branch outright makes the next line
    # do arithmetic on None and the row goes red with a TypeError — which
    # proves the branch is on the executed path, not that the row tells a
    # clean identity from an uncomputable one. Folding could-not-verify into
    # CLEAN is the actual defect the row exists to catch, so that is the
    # mutation: one token, and the output is a verdict rather than a crash.
    ("conservation_unverified", "items.py",
     '        out(f"COULD NOT VERIFY: conservation — {c[\'why\']}")\n'
     "        return exits.COULD_NOT_VERIFY",
     '        out(f"COULD NOT VERIFY: conservation — {c[\'why\']}")\n'
     "        return exits.CLEAN",
     "the could-not-verify ANSWER for an identity that could not be "
     "computed — folded into CLEAN, which is the number shaped like a pass"),

    # FILE FIELD MOVED ledger.py -> grammar.py, 2026-09-13. The anchor STRING
    # was never wrong; the predicate MOVED. lc-40 single-sourced it into
    # grammar.check_prose and left ledger.check_prose a re-export, so this row
    # read COULD NOT VERIFY (count 0 in ledger.py) for as long as that stood —
    # a registered refusal silently unproven, which is worse than the defect it
    # guards. Found by the lc-56 lane, landed here: prove-rows is never granted
    # to a lane, so a check and its subject never share one author.
    # DO NOT RE-POINT THIS AT items.py. The byte-identical line also sits at
    # items.py:797 inside slot_value_problem, a DIFFERENT predicate about item
    # SLOTS — pinned there the mutation would still compile, still go red, and
    # prove the wrong thing. grammar.py is the ledger-prose predicate: its own
    # message says "The ledger carries NO BODIES".
    ("ledger_body", "grammar.py",
     '    if "\\n" in v or "\\r" in v:',
     "    if False:",
     "the ledger's one-line rule — the NO BODIES half"),

    ("closure_home_split", "verbs.py",
     "    if done_home and done_home != closure:",
     "    if False:",
     "the comparison between the two declared closure homes"),

    # THE ANCHOR IS THE REFUSAL'S OWN BRANCH, never the predicate under it.
    # `_CARRIED_POINTER` and `_carried_pointer_lines` are read by a SECOND
    # caller — the corpus over-fire arm asks the helper directly, over prose
    # that is not a carrier at all — so a mutation there would remove
    # machinery this row does not name and darken a neighbour's question
    # along with it. `if clauses:` is the single place the FINDING is
    # decided; `if False:` folds it into the close that files the clause,
    # which is precisely the defect lc-22 was found by.
    ("close_carries_pointer", "verbs.py",
     "        if clauses:",
     "        if False:",
     "the refusal's own verdict on a body that declares a forward-carrier "
     "clause — the move then files that body in the closure home, where the "
     "obligation the clause declares reads as discharged because its carrier "
     "is filed as discharged"),

    # --- ASSIGNED ITEM C: the stage 1-3 rows, which passed their plant and
    # control pair but had never been shown to go dark. Each mutation below
    # folds one VERDICT into another rather than removing machinery: a
    # mutation that crashes proves the branch is on the executed path, not
    # that the row discriminates.

    ("declaration_absent", "declaration.py",
     "    if not path.exists():\n"
     '        res.add("declaration_absent",',
     "    if not path.exists():\n"
     "        res.cannot_verify(",
     "the FINDING answer for a repo with no declaration — folded into "
     "could-not-verify, which is refuse-unless-declared-private turning into "
     "a shrug"),

    ("declaration_malformed", "declaration.py",
     '        res.add("declaration_malformed",\n'
     '                f"{DECLARATION_REL} is not valid JSON: {exc.msg} "',
     "        res.cannot_verify(\n"
     '                f"{DECLARATION_REL} is not valid JSON: {exc.msg} "',
     "the FINDING answer for bytes that are present and wrong — folded into "
     "could-not-verify, which is the one distinction `exits.py` exists to "
     "keep"),

    ("declaration_malformed_missing_key", "declaration.py",
     "    missing = [k for k in REQUIRED_KEYS if k not in doc]",
     "    missing = []",
     "the required-key set's test — an ABSENT key then reads exactly like an "
     "empty declared one, which is the distinction §3.0 turns on"),

    # SHARES ITS SITE with `declaration_ignored_tracked` above, and that is
    # correct rather than sloppy: the two roster rows prove two firing inputs
    # (untracked, tracked) of ONE refusal, which is what `finding_row`
    # declares. The sibling rule in this tool's header is why both may darken.
    ("declaration_ignored", "declaration.py",
     "    elif ign:",
     "    elif False:",
     "the ignored-declaration verdict itself — the repo then reports a clean "
     "board over a declaration git cannot see"),

    ("kind_stage_undeclared", "declaration.py",
     "    absent = [s for s in KIND_STAGES if s not in body]",
     "    absent = []",
     "the closed stage list's completeness test — the primitive of the whole "
     "design, since a kind with an undeclared stage is where the Begehung's "
     "thirty findings sorted"),

    ("dangling_reference", "declaration.py",
     "        if name not in pool:",
     "        if False:",
     "referential integrity on a declaration's TYPED reference — a "
     "declaration pointing at a lane, verb, hook or producer that does not "
     "exist then reads exactly like one pointing at something that does"),

    # NOT `if False:` here. Removing the branch lets `read_text` raise
    # FileNotFoundError, which the next `except (OSError, …)` turns into the
    # SAME could-not-verify — the row would not move and the mutation would
    # read as a row that does not discriminate. So the ANSWER is folded into
    # silence instead: the parenthesised message becomes a discarded value.
    ("laws_absent_could_not_verify", "declaration.py",
     "    if not path.is_file():\n"
     "        res.cannot_verify(",
     "    if not path.is_file():\n"
     "        _folded = (",
     "the could-not-verify ANSWER for a laws file that is not in the working "
     "tree — folded into CLEAN, which is the index-resolved zero the design "
     "names explicitly"),

    ("schema_above_floor", "items.py",
     '    elif out.head["schema"] > SCHEMA_FLOOR:',
     "    elif False:",
     "the version floor's comparison — an old tool then parses a newer file "
     "and drops every slot it does not recognise, silently"),

    ("item_shape", "items.py",
     "    if missing:\n        out.problems.append((\n"
     '            "item_shape", item.line,',
     "    if False:\n        out.problems.append((\n"
     '            "item_shape", item.line,',
     "the missing-slot report in `_close_block` — a hand-written block then "
     "passes the check that makes \"the tool is the only writer\" a mechanism"),

    ("duplicate_id", "items.py",
     "        if len(at) > 1:",
     "        if len(at) > 999:",
     "the within-file id collision test — two copies of one body then read "
     "as two bodies"),

    ("unknown_grade_read", "items.py",
     '    if c["unknown"] or blockers_unverified:',
     "    if blockers_unverified:",
     "the census's THIRD ANSWER being carried into the exit code — an "
     "unclassifiable grade word then rides out under a CLEAN, and every "
     "count printed beside it is provisional"),

    # --- stages 7-9's own rows, and the six the emit-site coverage check
    # found already emitting under no registered row.

    # RE-ANCHORED (lane C, lc-13/14 wave). Both anchors below were the
    # pre-split source lines, where `cmd_lane_list` printed as it walked. The
    # `--json` work divided that into `gather_lane_list` (which DECIDES every
    # finding and the code) and two renderers (which only FORMAT), so the old
    # anchors matched zero times and this tool refused them as stale — which
    # is the refusal working. The decision moved; it did not leave `lanes.py`,
    # so both rows re-anchor here on the gather pass. Anchoring on a RENDERER
    # would have been the mistake available: a renderer computes no verdict,
    # so mutating one changes the printed prose while the exit code holds.
    ("roster_absent", "lanes.py",
     "    if entries is None:\n"
     "        return RosterRunResult(roster_path=path, roster_absent=True,\n"
     "                               roster_error=why, code=exits.FINDING)",
     "    if entries is None:\n"
     "        return RosterRunResult(roster_path=path, roster_absent=True,\n"
     "                               roster_error=why, "
     "code=exits.COULD_NOT_VERIFY)",
     "the FINDING answer for an absent roster — folded into could-not-verify, "
     "so a missing board reads as a limit of the run rather than a state of "
     "the system"),

    ("repo_unresolved", "lanes.py",
     '                           repo_unresolved=row.resolution.startswith("UNRESOLVED"))',
     "                           repo_unresolved=False)",
     "the unresolved-repo test itself — the walk then carries the line as an "
     "ordinary repo, the router prints it with no finding beside it, and the "
     "board is SHORTER rather than broken"),

    ("trigger_broken", "lanes.py",
     "            if t.state == BROKEN:",
     "            if False:",
     "the >=2 reserved code being read as BROKEN — a dead predicate then "
     "falls through to the quiet count, which is a clean board over a router "
     "that does not work"),

    ("lane_table_absent", "lanes.py",
     "                table_present=has_decision_table(text))",
     "                table_present=True)",
     "the lane body being ASKED whether it carries §3.3's decision table — "
     "every lane then reads as carrying one, and a lane that routes nowhere "
     "is a clean board again"),

    ("park_over_superseding_amendment", "verbs.py",
     "        if effective != value:",
     "        if False:",
     "`item park`'s supersession check — the comparison between the value "
     "written and the value the reader would actually put in force; disabled, "
     "park returns CLEAN over a blocker that does not govern, which is the "
     "verb telling the truth about its slot and lying about the item"),

    ("unknown_item", "verbs.py",
     '        out(f"FINDING [unknown_item] no live block {args.ident!r} in "\n'
     '            f"{ctx.items_path.name}.")\n'
     "        return exits.FINDING\n\n    done_parsed, done_why = "
     "_load(ctx.done_path)",
     '        out(f"FINDING [unknown_item] no live block {args.ident!r} in "\n'
     '            f"{ctx.items_path.name}.")\n'
     "        return exits.CLEAN\n\n    done_parsed, done_why = "
     "_load(ctx.done_path)",
     "the exit code behind `item ready`'s unknown-item message — the finding "
     "is still PRINTED and the run exits CLEAN, which is the shape a caller "
     "reading only the code cannot see"),

    ("unknown_source", "verbs.py",
     "    if source not in (SOURCE_SESSION, SOURCE_OPERATOR) and not \\",
     "    if False and not \\",
     "the closed door set on `--source` — an unrecognised source then "
     "decides the cost test's veto silently"),

    ("new_without_typed_blocker", "verbs.py",
     '        kind, _d = items_mod.classify_blocker(slots["blocked-by"], '
     "ctx.prefix)\n        if kind in (None, \"none\"):",
     '        kind, _d = items_mod.classify_blocker(slots["blocked-by"], '
     "ctx.prefix)\n        if False:",
     "the typed-blocker requirement on an INCOMPLETE item — it is then "
     "admitted with nothing to wait for, which is the entry that ages in "
     "nobody's court"),

    ("move_uncommitted", "verbs.py",
     "    if r.returncode != 0:",
     "    if False:",
     "the commit's own return code — the move's two halves are then reported "
     "durable together when the third step did not run"),

    ("ledger_shape", "ledger.py",
     '        out.problems.append(("ledger_shape", 1,\n'
     '                             "the ledger carries no `schema: <n>` head '
     'line."))',
     '        out.head["schema"] = SCHEMA_FLOOR',
     "the missing-version report on a ledger — the file is then STAMPED with "
     "the floor by the reader, so a future tool can never refuse it"),

    ("unregistered_kind", "cli.py",
     '            out(f"FINDING [unregistered_kind] {args.name!r} is not a "\n'
     "                f\"registered kind. Registered: {', '.join(kinds) or "
     "'(none)'}\")\n            return exits.FINDING",
     '            out(f"FINDING [unregistered_kind] {args.name!r} is not a "\n'
     "                f\"registered kind. Registered: {', '.join(kinds) or "
     "'(none)'}\")\n            return exits.CLEAN",
     "the exit code behind `kind show`'s unregistered-kind message"),

    ("emit_site_unregistered", "roster.py",
     "    if not uncovered:",
     "    if True:",
     "assigned item B's own verdict — the coverage check then reports CLEAN "
     "over a finding emitted under no registered row, which is the "
     "clean-forever check it exists to prevent"),

    # THE ANCHOR MOVED WHEN `--merge` LANDED (lc-17), and this tool is what
    # said so: it answers COULD NOT VERIFY on an anchor that no longer matches
    # rather than mutating whichever line looks closest, so a guard silently
    # left unproven is not a state this file can reach.
    ("migrate_would_overwrite", "migrate.py",
     "    if not args.force and not report_only and not merge:",
     "    if False:",
     "the refusal to overwrite an existing successor carrier — a second "
     "migration then replaces real work with a re-derivation of the carrier "
     "it replaced"),

    # ANCHORED ON THE MESSAGE, not on `if unclassified:` — the schema wave
    # added a SECOND `if unclassified:` in `run_schema`, and an anchor that
    # matches twice is a stale arrangement rather than a mutation: this tool
    # refuses it, which is how the collision was found rather than silently
    # mutating whichever came first.
    # THE AMBIGUITY BRANCH, which the message anchor below cannot reach. Both
    # rows prove ONE refusal (`migration_unclassified`), so each needs the
    # anchor where ITS OWN case is decided: `migration_unclassified`'s plant is
    # the no-rule word, and disabling the closure-word scan leaves that verdict
    # untouched — measured on a copy of HEAD before this row existed, `verdict
    # 2/named -> 2/named`, `rows changed: NONE`, prove-rows FAILED. The
    # replacement folds the SEARCH's result, never the branch around it: a
    # mutation that removed the call would crash and prove the branch is
    # reached rather than that the row discriminates.
    ("migration_ambiguous_closure", "migrate.py",
     "    m = _CLOSURE_WORD.search(headline_of(entry))",
     "    m = None",
     "the closure-word scan over an ungraded entry's title — the ambiguous "
     "shape is then written into the open carrier as ordinary NEW work, which "
     "is the silent half of the defect: a finished entry lands in the "
     "successor looking exactly like work nobody has started"),

    ("migration_unclassified", "migrate.py",
     '        out(f"FINDING [migration_unclassified] {len(unclassified)} '
     'entry/ies "',
     '        out(f"UNCLASSIFIED (not reported as a finding) '
     '{len(unclassified)} entry/ies "',
     "D-f's report of entries no rule covers — they are then absent from "
     "both the carrier and the run's verdict, which is a silent loss"),

    # --- THE SCHEMA WAVE (1d). Each folds one VERDICT into another; none
    # removes machinery, because a mutation that crashes proves the branch is
    # reached and not that the row discriminates.

    # lc-103. The replacement makes the condition ALWAYS TRUE so every mode
    # takes the `continue`, which disables the finding without touching the
    # separate symlink could-not-verify branch below it — one arm moves, which
    # is what makes the row discriminate rather than merely react. Measured by
    # the build lane against a scratch copy whose unmutated baseline ran green
    # FIRST (80/80, exit 0): it darkened EXACTLY the two sibling rows and no
    # other verdict. Anchor and replacement were chosen independently at the
    # desk and by the lane and came out identical.
    ("hook_not_executable", "declaration.py",
     '        if mode == EXECUTABLE_MODE:\n            continue',
     '        if mode != "no-such-mode":\n            continue',
     "the committed-mode comparison that decides whether a git hook the repo "
     "ships is launchable — with it folded away a hook committed at 100644 "
     "reads as fine, which is the gate that fails OPEN while every content "
     "check reports clean because the bytes are right"),

    ("declaration_retired_key", "declaration.py",
     "    for key, why in RETIRED_KEYS.items():\n        if key in doc:",
     "    for key, why in RETIRED_KEYS.items():\n        if False:",
     "the withdrawn-key test — `ready-cap` then sits in a declaration reading "
     "exactly like a live key, and a reader believes a number still bounds "
     "the head"),

    ("leak_scan_undeclared_reason", "declaration.py",
     "    if needs_reason and (not isinstance(reason, str) or len(reason.strip()) < 8):",
     "    if False:",
     "the demand that turning the source-scope foreign-path class OFF in a "
     "public tree carries its reason — the decision is then indistinguishable "
     "from nobody having considered it"),

    ("reference_untyped", "declaration.py",
     "        if typ is None:\n            res.add(\"reference_untyped\",",
     "        if typ is None:\n            res.cannot_verify(",
     "the FINDING answer for PROSE in a reader/writer slot — folded into "
     "could-not-verify, so an unresolvable reader reads as a limit of the run "
     "rather than a kind nothing reads"),

    ("schema_mismatch", "declaration.py",
     "        if n != declared:",
     "        if False:",
     "one-schema-per-repo's own comparison — the declaration and its carriers "
     "then disagree silently, and each reader resolves through whichever file "
     "it happened to open"),

    ("done_slot_on_live_item", "items.py",
     "    if done_only and item.grade not in GRADES_CLOSED:",
     "    if False:",
     "the closed-only rule on `superseded-by:`/`blocker-moot:` — a live block "
     "then claims an act no closure performed"),

    ("unknown_slot_misplaced", "items.py",
     "            if slot in UNKNOWNABLE_SLOTS:",
     "            if True:",
     "the separation between a slot UNKNOWN may fill and one it may not — "
     "`blocked-by: UNKNOWN` is then counted as an ordinary migration marker, "
     "and it is a value nothing can ever fill in"),

    ("ready_with_unknown_slot", "items.py",
     "                     if it.grade == \"READY\" and unknown_slots_of(it)]",
     "                     if False]",
     "the refusal of READY over a slot nobody has ever written — a migrated "
     "entry is then schedulable on a judgment that cannot have been made"),

    ("open_grade_in_done_home", "items.py",
     "    open_here = [it for it in parsed.items if it.grade not in GRADES_CLOSED]",
     "    open_here = []",
     "the closed-grade rule over the closure home — a body that arrived by "
     "some path other than a close then reads as an ordinary closure"),

    ("blocked_in_done_home", "items.py",
     "        if kind not in (None, \"none\"):",
     "        if False:",
     "the no-surviving-blocker rule over the closure home — a wait then stays "
     "recorded against a body that has stopped waiting, which is what leaves "
     "an unanswerable question in the operator's queue"),

    # ANCHORED ON THE MESSAGE TAIL, not on the bare `return None,
    # exits.FINDING` — that spelling appears TEN times in verbs.py, so a bare
    # anchor would mutate whichever one came first and prove a different row.
    # Tying it to this refusal's own closing sentence means a reworded message
    # reports COULD NOT VERIFY rather than silently moving the mutation.
    ("close_over_live_blocker", "verbs.py",
     "        \"which records the wait as abandoned rather than as answered.\")"
     "\n    return None, exits.FINDING",
     "        \"which records the wait as abandoned rather than as answered.\")"
     "\n    return None, exits.CLEAN",
     "the refusal of a DONE close over a live item-id dependency — the close "
     "then proceeds and `move_to_done` rewrites the `blocked-by:` line to "
     "NONE, so the wait is deleted with no record anywhere, which is the "
     "silent half of lc-90 and the direction nothing reported"),

    ("laws_scope_audit", "retire.py",
     "    if not hits:",
     "    if True:",
     "the scope audit's own verdict — the laws file then reports CLEAN over "
     "prose belonging to another kind, which is the clean-forever check the "
     "60-line cap was replaced BY rather than the cap it replaced"),

    ("capture_dominated", "verbs.py",
     "    if closed == 0:",
     "    if False:",
     "the no-drain branch of the flow alarm — a carrier that has admitted "
     "work and closed none then divides by zero's neighbour and reads as a "
     "ratio, which is the one case a size-based cap also missed"),

    ("kind_grew_without_exit", "retire.py",
     "    if count and not events:",
     "    if False:",
     "R22's replacement for the cap — an EXIT-CONTROLLED kind whose exit has "
     "recorded nothing then reports clean, and growth is watched by nothing "
     "at all. Since lc-145 that is every mode the declaration does not opt "
     "out of, `compacted` among them — not `bounded-by-exit` alone, which is "
     "what this line said while the predicate had already widened under it"),

    ("unregistered_persisted_thing", "retire.py",
     "    if not unregistered:",
     "    if True:",
     "invariant 1's own verdict — a tracked file under no registered home "
     "then reads exactly like one the registry claims"),

    # NOT `if False:` here. The route check's finding is the DIFFERENCE
    # between a declared route set and a derived one, so the mutation that
    # kills it is the one that makes the derived set answer for the declared
    # one — which is precisely the same-parentage defect this check exists to
    # avoid, and it produces a wrong VERDICT rather than a crash.
    # SCOPED TO ONE DIRECTION, and it was not always. Until lc-30 this
    # arrangement read `full = set(row.route_set)` -> `full = set(watched)`,
    # which is the same-parentage defect stated at its widest. That was a
    # proof while the stray direction was a NOTE; once the mirror became
    # `route_set_unnamed`, one mutation emptied BOTH difference sets and
    # darkened two rows proving two refusals — which this tool's own rule
    # says proves neither. So each direction now gets the same-parentage
    # mutation SCOPED TO ITSELF: `full - watched` computed as
    # `watched - watched` is still the derived set answering for the
    # declared one, and it leaves the other direction reading real input.
    ("route_set_unwatched", "roster.py",
     "        missing = sorted(full - watched)",
     "        missing = sorted(watched - watched)",
     "the independence of the two sides in the UNWATCHED direction — the "
     "route set is then computed FROM the code it grades, so it moves with "
     "the mutant and stays green on every narrowing of the code"),

    # The mirror, and NOT `if False:` for the reason stated above: the
    # finding is a DIFFERENCE, so the mutation that kills it makes one side
    # answer for the other rather than removing the branch around it.
    ("route_set_unnamed", "roster.py",
     "        stray = sorted(watched - full)",
     "        stray = sorted(full - full)",
     "the independence of the two sides in the UNNAMED direction — the "
     "declared route set then answers for the derived one, so a refusal "
     "catching more than its text says reads exactly like one that does not"),

    # ANCHORED ON THE COMPARISON, not on the branch around it — the same
    # choice `migration_ambiguous_closure` makes above and for the same
    # reason: folding the LOOKUP's result leaves the branch reached and the
    # machinery intact, so what the arm measures is whether the row reads that
    # comparison. Disabling it, the merge APPENDS the duplicate body: one
    # piece of work booked twice under two ids, which on the closed side means
    # a finished body coming back as open work.
    ("merge_duplicate_body", "migrate.py",
     "        ident = known.get(headline_of(e))",
     "        ident = None",
     "the headline comparison between an incoming source entry and the bodies "
     "already in the successor homes"),
    ("merge_source_self_duplicate", "migrate.py",
     "        first = known.get(headline_of(e))",
     "        first = None",
     "the parsed-headline comparison between a later source entry and the "
     "first source entry carrying it"),

    ("migration_ledger_nonzero", "migrate.py",
     "    elif ledger_count != 0:",
     "    elif False:",
     "the acceptance criterion 'zero entries routed to the ledger', checked "
     "at the artifact"),

    # NOT `if False:` on the loop's own test. Folding the ANSWER is the
    # mutation that discriminates here: an undeclared body is then reported as
    # a limit of the run rather than a state of the repo, which is precisely
    # the distinction `exits.py` exists to keep and the one a caller reading
    # only the code cannot recover.
    # NOT the `detail not in known` test, and the difference decides whether
    # this proves anything. Removing that test makes EVERY item-id blocker
    # dangle, so the row goes red for the opposite reason — an over-fire, not
    # a missing finding — and a mutation that produces the wrong defect proves
    # the branch is reached, never that the row discriminates. Folding the
    # ANSWER is the one that names the real failure: the ids are still
    # resolved, the dangling one is still found, and the run reports CLEAN
    # over it, which is exactly the permanent silent park this row exists for.
    ("dangling_reference_carrier", "items.py",
     "    if dangling:\n        return exits.FINDING",
     "    if dangling:\n        return exits.CLEAN",
     "the exit code behind the carrier-side dangling-blocker message — the "
     "finding is still PRINTED and the run exits CLEAN, which is the shape a "
     "caller reading only the code cannot see"),

    # THE STORABILITY TEST ITSELF, not the `classify_blocker` call above it.
    # Removing the classification would make EVERY blocker untyped and darken
    # `blocker_untyped` too — the wrong defect, proving the branch is reached
    # rather than that this row discriminates. Folding the `if why:` leaves
    # the question classified, the ledger's own predicate still consulted,
    # and the unstorable answer simply ignored: the item is admitted with a
    # `blocked-by:` line nothing can ever answer, which is the row's defect.
    ("blocker_unstorable", "verbs.py",
     '        why = ledger.check_prose(detail, "the decision question")\n'
     "        if why:",
     '        why = ledger.check_prose(detail, "the decision question")\n'
     "        if False:",
     "the mint-time storability test on a `decision` blocker — removed, a "
     "question the ledger refuses is written into the carrier anyway and "
     "`item ready` can never match it back"),

    # THE PROBE'S VERDICT, not the probe. Removing the `rev-parse` call would
    # raise rather than answer, and an arm that RAISES proves the code is new,
    # never that the row discriminates. Inverting the verdict to `if True`
    # makes every ref resolve, so the loop falls through and the close writes
    # the unresolvable ref into a body that then stops being edited — the
    # permanent label this row exists to refuse.
    ("closed_ref_unresolvable", "verbs.py",
     "        if probe.returncode == 0:\n"
     "            continue",
     "        if True:\n"
     "            continue",
     "the resolution test behind `item close --ref` — removed, a ref naming "
     "no commit is written into the closure record and reads exactly like a "
     "good one"),

    # THE GUARD, NOT THE DETECTION. `pinned_body` still runs and `detail` is
    # still computed — removing either would raise rather than answer, and an
    # arm that RAISES proves the code is new. Disabling only the branch that
    # ACTS on `detail` leaves the verb walking the same path and reaching the
    # compaction it should have refused: the body leaves the carrier while the
    # blob pin does not carry it, which is the silent strip this row exists to
    # refuse. Anchor is a whole-line run and unique in retire.py (1 line-exact
    # hit, 1 raw substring), so a deeper-indented twin cannot retire it.
    ("compaction_would_strip", "retire.py",
     "        if detail is not None:",
     "        if False:",
     "the guard that refuses to compact a body the blob pin does not carry — "
     "disabled, the verb strips the body out of the carrier and the text is "
     "recoverable from nowhere"),

    ("lane_undeclared", "declaration.py",
     '        res.add("lane_undeclared",\n'
     '                f"{lanes_mod.LANES_DIR}/{name}.md is a lane body and '
     '{name!r} "',
     "        res.cannot_verify(\n"
     '                f"{lanes_mod.LANES_DIR}/{name}.md is a lane body and '
     '{name!r} "',
     "the FINDING answer for a lane body the declaration does not list — "
     "folded into could-not-verify, so the direction of the registration "
     "invariant that nothing watched reads as a shrug instead of a state"),

    # lc-142. THE COUNT'S OWN TEST, not the `from_count = sum(…)` line above
    # it and not the message below it. Folding the SUM would leave
    # `from_count` undefined and the arm would raise, which proves the branch
    # is reached and never that the row discriminates; anchoring the message
    # would grade the printing rather than the decision. `if from_count > 1:`
    # is the single place this refusal is decided, and with it folded the two
    # arms become BYTE-IDENTICAL invocations — argparse discards the first
    # `--from`, so `--from X --from X` and `--from X` reach `cmd_migrate` as
    # the same run. That is what makes the darkening attributable to the
    # repeated token and to nothing else, and it is the property the row's own
    # fire/control pair was built around.
    ("migrate_repeated_from", "cli.py",
     "        if from_count > 1:",
     "        if False:",
     "the repeated-`--from` count's own test — a caller then names two "
     "sources in one invocation, argparse keeps the second alone, and the "
     "run reports a migration from a carrier it never opened"),
]


def anchor_hits(text: str, anchor: str) -> list:
    """Offsets where `anchor` occurs as a run of COMPLETE LINES.

    LINE-EXACT, NEVER SUBSTRING, and the difference is a row's proof. An
    anchor is an indented source line, so a plain substring search finds it
    inside the SAME line at any DEEPER indent — `    if r.returncode != 0:`
    is a substring of `        if r.returncode != 0:`. An unrelated verb
    spelling a git check the ordinary way then makes the anchor match twice,
    `move_uncommitted`'s arrangement goes to COULD NOT VERIFY, and that row's
    proof is retired by a change that has nothing to do with it. It happened:
    `_resolve_refs` spells its probe `if probe.returncode == 0: continue`
    with a comment saying it had to, because the natural spelling would have
    darkened another row's arrangement.

    The mirror hazard is the other end: an anchor ending mid-line is a PREFIX
    match wearing an equality's costume, satisfied by any longer line that
    begins the same way. So BOTH ends are anchored to a line boundary, and
    every recorded anchor is a whole-line run — there is no mid-line form and
    no fallback to one, because a fallback would reinstate exactly the hole.

    Returned as OFFSETS rather than a count, because the caller must write at
    the offset this function accepted: `str.replace` would substitute the
    first SUBSTRING occurrence, which may be one of the mid-line matches this
    function exists to reject.
    """
    out, i = [], text.find(anchor)
    while i != -1:
        end = i + len(anchor)
        if (i == 0 or text[i - 1] == "\n") and \
                (end == len(text) or text[end] == "\n"):
            out.append(i)
        i = text.find(anchor, i + 1)
    return out


def head_blob(rel: str):
    """The committed bytes of `rel` at HEAD, or `None` where HEAD has none."""
    r = subprocess.run(["git", "-C", str(REPO), "show", f"HEAD:{rel}"],
                       capture_output=True)
    return r.stdout if r.returncode == 0 else None


def dirty_targets(paths) -> list:
    """`[(rel, why)]` for every file whose working bytes differ from HEAD's.

    THE PRECONDITION THIS TOOL CANNOT RUN WITHOUT, checked before anything is
    written. Every path here is one the run would overwrite and then restore
    from a backup taken moments earlier — so a file already carrying somebody's
    uncommitted work, or residue from a crashed earlier run, is not a tree this
    tool may touch: the backup would capture the FOREIGN state and the restore
    would write it back as though it were the original.

    A path absent from HEAD counts as differing. The tool cannot establish what
    it would be restoring such a file TO, and proceeding on an unknown baseline
    is the same hazard by a quieter route.
    """
    out = []
    for path in sorted(paths):
        rel = path.relative_to(REPO).as_posix()
        blob = head_blob(rel)
        work = path.read_bytes()
        if blob is None:
            out.append((rel, "HEAD carries no blob at this path, so there is "
                             "no committed state to restore it to"))
            continue
        if blob != work:
            out.append((rel,
                        f"working sha256 {hashlib.sha256(work).hexdigest()} "
                        f"!= HEAD blob sha256 "
                        f"{hashlib.sha256(blob).hexdigest()}"))
    return out


def clear_pycache():
    for d in CORE.rglob("__pycache__"):
        shutil.rmtree(d, ignore_errors=True)


def verdicts(only=None) -> dict:
    """`{ident: signature}` for every row's PLANT, in a fresh interpreter.

    THE SIGNATURE IS THE CODE **AND** THE ROW NAME IN THE OUTPUT, and the
    second half was added after this tool reported a row unproven that is
    not. Disabling `item park`'s own typed-blocker guard leaves the exit
    code at 2, because the shared `_check_blocker` catches the same input
    under a DIFFERENT row's name — so a comparison over codes alone
    separates something-happened from nothing-happened when the question is
    WHICH refusal fired. Two rows that share an exit code are the normal
    case here, not the exotic one: every finding is a 2.

    A fresh process per arm, because the modules under mutation are imported
    once per interpreter: reading the roster twice in one process would grade
    the mutation against a module the mutation never reached.
    """
    src = (
        "import json, sys\n"
        f"sys.path.insert(0, {str(CLI)!r})\n"
        "from lifecycle_core import refusals\n"
        "out = {}\n"
        "for row in refusals.ROWS:\n"
        "    try:\n"
        "        f = row.fire()\n"
        "        named = ('[' + row.expected_finding_row + ']') in f.output\n"
        "        out[row.ident] = '%s/%s' % (f.code, 'named' if named\n"
        "                                    else 'unnamed')\n"
        "    except Exception as exc:\n"
        "        out[row.ident] = 'RAISED: ' + type(exc).__name__\n"
        "print(json.dumps(out))\n"
    )
    r = subprocess.run([sys.executable, "-c", src], capture_output=True,
                       text=True, cwd=str(REPO))
    if r.returncode != 0:
        raise SystemExit(f"the roster could not be read:\n{r.stderr[-2000:]}")
    import json
    return json.loads(r.stdout.strip().split("\n")[-1])


def sibling_map() -> dict:
    """`{ident: finding_row}` read from the UNMUTATED roster, once.

    Read from the roster rather than restated here: the mapping is the
    roster's own declaration, and a copy of it in this file would be a second
    body that goes stale the day a row is added.
    """
    src = (
        "import json, sys\n"
        f"sys.path.insert(0, {str(CLI)!r})\n"
        "from lifecycle_core import refusals\n"
        "print(json.dumps({r.ident: r.expected_finding_row\n"
        "                  for r in refusals.ROWS}))\n"
    )
    r = subprocess.run([sys.executable, "-c", src], capture_output=True,
                       text=True, cwd=str(REPO))
    if r.returncode != 0:
        raise SystemExit(f"the roster's mapping could not be read:\n"
                         f"{r.stderr[-2000:]}")
    import json
    return json.loads(r.stdout.strip().split("\n")[-1])


def main(argv) -> int:
    wanted = set(argv) or None
    rows = [m for m in MUTATIONS if wanted is None or m[0] in wanted]
    if wanted:
        unknown = wanted - {m[0] for m in MUTATIONS}
        if unknown:
            print(f"COULD NOT VERIFY: no mutation recorded for "
                  f"{', '.join(sorted(unknown))}")
            return COULD_NOT_VERIFY

    # BEFORE the backup, because the backup is what makes a dirty target
    # dangerous: it would capture the foreign state and the restore would
    # write it back under this tool's hand.
    dirty = dirty_targets({CORE / fname for _, fname, *_ in rows})
    if dirty:
        print(f"REFUSING TO START — {len(dirty)} file(s) this run would "
              "mutate already differ from HEAD:")
        for rel, why in dirty:
            print(f"    {rel}")
            print(f"        {why}")
        print("\nThis tool overwrites each of those files and restores them "
              "from a backup taken at startup, so running now would capture "
              "the current state as the 'original' and write it back as such. "
              "Either commit the work, or restore the file from its committed "
              "blob — `git show HEAD:<path>` — never with `git checkout`, "
              "`git restore` or `git stash`, which are whole-file destructive "
              "against uncommitted work.")
        return FINDING

    backup = Path(tempfile.mkdtemp(prefix="prove-rows-"))
    for f in CORE.glob("*.py"):
        shutil.copy2(f, backup / f.name)

    siblings = sibling_map()
    clear_pycache()
    print("BASELINE — the unmutated roster, stated rather than assumed.")
    print("(Over an already-red baseline a mutate-and-restore proof is "
          "indistinguishable from a check that is simply always red.)")
    base = verdicts()
    for ident, code in sorted(base.items()):
        print(f"    {ident:<34} {code}")

    failures = []
    stale = []
    for ident, fname, anchor, replacement, what in rows:
        path = CORE / fname
        text = path.read_text(encoding="utf-8")
        hits = anchor_hits(text, anchor)
        if len(hits) != 1:
            stale.append((ident, fname, len(hits)))
            print(f"\n[{ident}] COULD NOT VERIFY — the anchor matches "
                  f"{len(hits)} complete-line run(s) in {fname}, not one. The "
                  "source moved under this arrangement.")
            continue
        at = hits[0]
        try:
            clear_pycache()
            path.write_text(text[:at] + replacement + text[at + len(anchor):],
                            encoding="utf-8")
            clear_pycache()
            after = verdicts()
        finally:
            shutil.copy2(backup / fname, path)   # BY FILE COPY
            clear_pycache()

        changed = sorted(k for k in base
                         if base.get(k) != after.get(k))
        refusal = siblings.get(ident, ident)
        family = sorted(k for k, v in siblings.items() if v == refusal)
        strays = [k for k in changed if siblings.get(k, k) != refusal]
        ok_named = ident in changed
        ok_alone = not strays
        verdict = "PROVEN" if (ok_named and ok_alone) else "FAILED"
        print(f"\n[{ident}] {verdict}")
        print(f"    disabled: {what}")
        print(f"    {fname}: {anchor.splitlines()[0][:66]}…")
        print(f"    verdict {base.get(ident)} -> {after.get(ident)}")
        print(f"    rows changed: {', '.join(changed) or 'NONE'}")
        if len(family) > 1:
            print(f"    refusal {refusal!r} is proven by {len(family)} roster "
                  f"row(s): {', '.join(family)} — a mutation at the single "
                  "site where that refusal is decided darkens the family, "
                  "and that is not a stray.")
        if not ok_named:
            print("    -> the row did NOT change. The condition this "
                  "mutation names is not what produces its verdict.")
        if not ok_alone:
            print(f"    -> row(s) proving ANOTHER refusal changed: "
                  f"{', '.join(strays)}. This mutation removed adjacent "
                  "machinery, so it proves nothing about any one row.")
        if verdict == "FAILED":
            failures.append(ident)

    shutil.rmtree(backup, ignore_errors=True)
    covered = {m[0] for m in MUTATIONS}
    unproven = sorted(set(base) - covered)
    print(f"\nrows with a recorded mutation: {len(covered)} of {len(base)}")
    if unproven:
        print("rows with NO mutation recorded (proven elsewhere or not at "
              "all — listed, never omitted):")
        for ident in unproven:
            print(f"    {ident}")
    if stale:
        return COULD_NOT_VERIFY
    if failures:
        print(f"\nFAILED: {', '.join(failures)}")
        return FINDING
    print("\nevery recorded arrangement held: the named row went dark, and "
          "nothing proving another refusal went dark with it.")
    return CLEAN


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
