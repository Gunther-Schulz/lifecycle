# Design v4: the wave's small mechanisms (D-5; D-9 re-ruled; W4 withdrawn)

**Round desk, 2026-09-19, FOURTH LOCK — pass 3 integrated; finding ids
resolve in docs/audits/2026-09-19-design-attack-r1.md and -r2-pass3.md.
astra r2 cleared W4's withdrawal.**

## W1 — wire the O6 evaluation half (f2)

**Act 1: the verb** `kind moments`, longhand per kind, findings under
REGISTERED rows (`reader_moment_broken`, `reader_moment_malformed`).
Red-first: FIRE fixture is a predicate-mode moment; MALFORMED fixture is
the shared partition's case (P2 v3 — presence-aware, so absent-`when`
stays UNDECLARED). **Act 2: the banner line shows the LAST VERB RUN's results WITH THEIR
DATE — a named-stale carrier (astra-w3). The read itself is counted
honestly (T-c4): one fire-log read per session start IS always-on
EXECUTION, row 6 of the inventory below, admitted explicitly — v3's
"zero execution" row was false under the design's own definition.** The
result carrier: the fire log's detail — **machine-local and best-effort,
stated (FF-1/T-w2): on another machine or after a lost write the line
renders "no recorded run on this machine", which is itself the honest
state; the project-scoped truth stays the verb's own output at run time,
and the banner line claims no more.**
No-yield disposition, owned (B8): **graded at the retirement pass the
banner already triggers — when "pass owed" prints, the pass's ledger note
grades this line's catches since last pass; writer = the session running
the pass; event = the existing computable trigger.** Write-set:
declaration.py (shared partition consumer), verbs.py, cli.py, refusals.py,
firelog.py, test_verbs.py, test_declaration.py.

## W2 — the PERISHABLE evidence mark (E10)

Mark form: **`PERISHABLE(<date>, re-derive: <command>)` — the mark carries
its own date (B7: the base-slot case, the first anyone writes, had no
comparison input; law 26 now met at exactly that case).** Freshness
semantics defined (astra-w2): the flag "PERISHABLE, never re-derived"
fires iff no evidence amendment STRICTLY LATER than the mark's date
carries a re-derive result naming this mark's command; SAME-DAY resolves by BLOCK POSITION, not by date arithmetic (T-c3: dates
alone would false-flag an immediate legitimate re-derivation — a guard
firing on legitimate work): an amendment SEQUENCED AFTER the mark's
introducing line in the block counts as later, same-day included —
amendment order in a block is the carrier's own total order. A claim with
no amendments and a past-dated mark fires. The
re-derivation act = `item amend --evidence` appending the dated result
(recorded, the W-8 answer). Refusal row for the mark grammar (W-9),
red-first on the malformed-PERISHABLE-beside-valid-MEASURED sibling.
No-yield disposition, owned (B8): graded at the same retirement pass, same
writer, same event. Write-set: items.py, cli.py, refusals.py, vocab.py,
test_items.py.

## W3 — relay reach as a continuing contract (f5)

`_RELAY` verdict-agnostic. **The reach population derives from the
REGISTERED KINDS whose members are executable Python — detection by ONE
testable classifier (T-w3): a member file whose name ends `.py` OR whose
first line matches `^#!.*python`; membership enumerated per home shape by
the kind machinery's own member listing (file, glob, directory — the same
enumeration `kind list` uses), so every legal home shape has defined
behaviour (B5/astra-w1: plugin/hooks'
members are extensionless BY CONSTRUCTION, so any extension-keyed
predicate returns a true-absence-shaped zero over that whole kind; both
arms proved the eighth site survives a `*.py` glob). The acceptance check
uses the ACTUAL pre-commit relay site (plugin/hooks/pre-commit:154), not
a planted file.** Pattern facts stated exactly (verified by both arms):
five regexes, two scanners, three verdict-keyed, two call-shaped. No
no-yield disposition and why (B8's completeness): W3 is a correctness
contract, not a surfacing line — it retires only with the scanners it
guards. Write-set: roster.py, refusals.py, test file.

## W4 — WITHDRAWN (D-9 re-ruled; astra r2: "no additional finding against
## the replacement"). The dotfiles-side export is a cross-repo booking;
## lc-52 parked on it; lifecycle's warning fallback stands built. The
## unmarked-commit rate reads at the pre-push hook's own output when the
## export lands.

## THE WAVE-LEVEL ALWAYS-ON INVENTORY (B6 — one table, every addition its
## own delta; the definition is the invariant, the carrier list
## non-exhaustive and now including the statusline path, N2)

| addition | kind | delta | basis |
|---|---|---|---|
| census line split (P3) | content | 1 line → 1 line | inventory delta |
| external-court line (P4) | content | +1 line per external blocker in ready output | inventory delta |
| OOV count+age line (P1) | content | +1 line when nonzero | inventory delta (v2 omitted its own line — astra-c5) |
| arc status block (arc v3) | content | +N lines, one small fixed field-set per OPEN arc; bounded by the flow alarm, not a cap | inventory delta; the borrowed-delta error (B6) repaired by this row |
| W1 act 2 line | content (named-stale) | +1 line | inventory delta (astra-w3); its READ is row 6 |
| W1 act 2's fire-log read (T-c4) | EXECUTION | one local log read + parse per session start | admitted under the instrument-bearing gate (the desk's HEALTH grading, reach stated N5) + this row's own delta; v3's "zero execution" row was false and is replaced by this one |

## Wave construction (r2-completed)

Write-sets feed `item waves`; the join orders file-granular lanes — and
the collisions list now includes P1's real homes (declaration.py,
items.py — B10) and the arc lane's items.py share (N1). **The CROSS-REPO
ordering the join cannot see is the desk's, stated: the carrier_homes
reach act lands before lc-239 beat 1 opens any repo, or after beat 2 —
never during (N7).** Numbered booking steps with actors (N6): (1) this
desk books the contract item, RE-POINTS lc-237's blocker to it AND amends
lc-237's done-criterion to the settled direction (predicate mode stays;
never-run vs runs-quiet realized under the contract item) in the same
act (N6/c6: the criterion half was the unaddressed residue); (2) books the arc items (reach act + kinds+verbs as separate
items per law 25's own-act rule); (3) books W1/W2/W3 items; (4) the
router-roster incompleteness finding (arc v3) is booked; (5) the join
runs over the booked set. Build conduct: the contract v3's N10 line binds
every lane.
