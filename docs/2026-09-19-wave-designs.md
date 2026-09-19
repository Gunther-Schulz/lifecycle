# Design: the wave's four small mechanisms (decisions D-5, D-9; Begehung f2/f5; map E10)

**Round desk, 2026-09-19. Status: LOCKED pending the fresh-context attack
round, same as the two sibling design docs. Each part: settled design,
write-set, red-first, three answers, observer, stop/yield. Builder inherits
zero design freedom; spelling follows the repo's existing instances.**

## W1 — wire the O6 evaluation half (Begehung f2; the read_moments caller)

TWO ACTS, split by the erosion gate. **Act 1 (ungated): the verb.**
`kind moments` — for every registered kind with a reader `when`, print
`read_moments`' answer longhand (FIRE / QUIET / BROKEN / MALFORMED /
UNDECLARED / NONE-with-why per kind; sparse renders as silence, so kinds
with no `when` print their state too — the lane-list rendering idiom).
Exit contract: verb contract (0 clean / 2 finding / 3 CNV) — BROKEN or
MALFORMED anywhere is a finding; an unreadable declaration is CNV.
**Act 2 (GATED on lc-234's graded probe result — blocked-by: lc-234): the
banner.** The session-start structure line (lc-174's home) gains the due
read-moments line, computed by the same function. MUST-NOT-BUILD: no
always-on wiring before the probe's verdict is graded at the desk; the
verb ships alone if the probe answers erosion.
Red-first: a fixture kind with `when: verb:audit` fires after an audit run
marker and is listed; the MALFORMED fixture (P2's matrix) renders MALFORMED
in the verb output — both as test_declaration/test_verbs cases. Depends on
the vocabulary contract's P2 (MALFORMED state) landing first — same wave,
ordered. Write-set: declaration.py (shared with P2), verbs.py, cli.py,
test/test_verbs.py (the derived dispatch table moves with the tuple — law
24's worked example), test/test_declaration.py.
Observer: the verb's own run; the banner once gated-in. Stop/yield: the
verb is pull-only (no new always-on surface); yield = the banner line's
first real catch, recorded on the item at close.

## W2 — the PERISHABLE evidence mark (map E10; friction requirement 2)

The evidence-mark vocabulary (MEASURED / DERIVED / RECALLED / RELAYED —
itself registered under the D-3 contract, with its OOV arm) gains
**PERISHABLE (re-derive: <command>)**: a comparison between moving
artifacts is stored as a measurement WITH ITS SHELF-LIFE ACT, never as a
durable fact. Consumers: `evidence_unmarked` accepts the new mark;
`item slots` renders every PERISHABLE claim under a loud RE-DERIVE banner
naming the command — the pickup instrument both wave-B entries already
mandate is the consuming seam (mechanism 5), and the picking session runs
the command; v1 does NOT auto-execute (an arbitrary command at ready-time
is an over-reach — the slot demands the statement, the seam demands the
act). Red-first: a planted PERISHABLE claim renders the banner; a MEASURED
control does not; an unmarked comparison still refuses (existing row, the
positive control that the door did not widen). Three answers: the mark
grammar's parse failure is refused at the door (slot refusal), never
silently accepted as prose. Write-set: items.py, cli.py rendering,
test/test_items.py; vocab.py registration rides the contract build.
Observer: item slots at every pickup. Stop/yield: marks enter at authoring
choice — no retro-sweep of old evidence (on-contact rule); yield = the
first stale-comparison catch at a pickup, recorded where caught.

## W3 — the `_RELAY` widening plus its sibling sweep (Begehung f5)

`roster.py:80` `_RELAY` goes verdict-agnostic (matches the relay shape
under FINDING and COULD-NOT-VERIFY alike), and — the r4 lesson discharged
in the same change, not after it — ALL FOUR scan patterns are swept for
verdict-key blindness in one commit, the sweep's outcome per pattern
stated in the commit body (found-and-widened / already-agnostic).
Red-first: the Begehung lane's own four-arm arrangement (baseline 7 relay
sites; finding-relay control seen; CNV-relay arm — currently invisible,
must be SEEN after; literal-CNV control unchanged) lands as the test, run
over a package copy exactly as the lane ran it. Latent defect, so the
plant IS the red. Write-set: roster.py, test (new arrangement in
prove-rows' recorded form so the proof is re-runnable). Observer: --test's
emit-site check. Stop/yield: one module, one sweep, closed enumeration
(the four patterns are the population — source-derived, not chosen).

## W4 — the trailer default (decision D-9; lc-52)

`attribution_block` gains a fallback chain with THREE answers: (1)
`LIFECYCLE_COMMIT_TRAILER` set → as today. (2) Unset → read the desk-state
kind: IF exactly one live desk-state file claims this repo's cwd (fresh by
its own written timestamp; the hook that writes desk-state records session
URL + model + cwd), use its trailer block WHOLE (both halves — a half
block stays dropped, the forged-shape rule unchanged). (3) Zero candidates
OR more than one → today's warning fallback, with the count named
("no/2 desk-state candidates") — AMBIGUITY IS NEVER RESOLVED BY
LAST-WRITER-WINS: a wrong Claude-Session URL is silent misinformation that
sends an auditor to the wrong transcript, strictly worse than the unmarked
state the pre-push hook already names on every push. The hook side: the
plugin's session-start machinery writes the desk-state trailer file (the
kind exists; the write is the hook's, the read the verb's — the plugin
owning both ends is the decision's pit-of-success ground). Red-first:
env-set beats file (control); one fresh file → trailer read back off the
commit 1/1; two files → warning names the count and the commit is
unmarked; zero → today's exact warning. Write-set: verbs.py,
plugin/hooks/ (the desk-state write), test/test_verbs.py. Observer: the
pre-push hook's unmarked-commit line (unchanged, still the backstop).
Stop/yield: no new always-on surface (the hook already runs); yield = the
unmarked-commit rate on this repo's pushes, before vs after, read at the
fire log — the entry's own gate-1 metric.

## Wave ordering (post-attack build)

Contract P1/P2 first (W1 depends on MALFORMED; W2's mark registers in
vocab.py) → W1 act 1, W2, W3, W4 in any order, disjoint write-sets except
declaration.py (P2+W1: one lane, per-item commits) → P3/P4 (carrier-side)
→ specimen amendments → W1 act 2 waits on lc-234's graded result. The arc
kind (its own doc) is a separate lane on a disjoint set (arcs.py new file;
the cli.py/test_verbs.py overlap with W1 serializes those two lanes on
that pair — named here so the join does not re-discover it).
