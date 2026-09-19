# Design: the ARC kind (lc-231; decision D-2)

**Round desk, 2026-09-19. Status: LOCKED pending the fresh-context attack
round; no build before it returns. Direction decided at D-2 (ledger): a NEW
REGISTERED KIND, not a widened lane — lanes are stateless router rows, arcs
are stateful carriers; reuse happens at the seams (exits via
`lanes.evaluate_trigger`; deadline observers ARE lanes; entry/close under
two-exits + conservation). Inputs: arc-walk synthesis (8 requirements),
lc-231's entry (kill test, belief vocabulary, reopen-and-propagate),
purpose.md (session-independence: the window is a cache, the persisted
state is the truth), round map E12/E13 (folded here by D-5), head-rule
re-open (d). The item carrier is the FORM TEMPLATE (the worked example);
where this document fixes structure and not spelling, items.py's existing
grammar decides the spelling — the read-the-existing-instances rule as a
binding instruction to the builder.**

## What an arc IS

The persisted working state of one goal-directed effort: the operator's
goal, the current stage, the live narrowing, the premises the instruments
rest on, the beliefs derived so far (each reopenable), the yield series,
and the deadlines — held OUTSIDE every session that thinks with it, written
as a byproduct of the work, resumable by a fresh context with measured loss
approaching zero (the KILL TEST, purpose.md — this design's acceptance
criterion, not a slogan).

## Kind declaration (all seven stages, law 15 — declared now, computable
## slices implemented in v1, the rest DECLARED-NOT-IMPLEMENTED as a state)

- **home:** `arcs/<slug>.md`, one file per arc; closure MOVES the body to
  `arcs/closed/<slug>.md` (law 9: append, delete, commit; conservation
  counts both homes).
- **writer:** the tool's arc verbs ONLY (law 8). Verbs, v1:
  `arc open` (goal is a REQUIRED slot and is the operator's word — top
  goals are never self-minted; refusal `arc_goal_unattributed` fires on an
  open without an operator attribution line), `arc advance` (stage
  transition; demands the exit trigger's answer), `arc premise`
  (add/kill a premise; killing PRINTS the instruments/beliefs whose basis
  lines cite it), `arc belief` (add, with REQUIRED basis and
  kill-condition-or-`unknown`), `arc reopen <belief-id>` (flags every
  within-arc citer for re-derivation; prints carrier items whose text
  names the belief id — grep-derived, reported not auto-flagged),
  `arc yield` (append a round outcome to the series), `arc close`
  (disposition + the move).
- **reader:** session at start (the banner prints open arcs: goal, stage,
  narrowing head, yield line, premise-inbox count); the reader-when
  machinery (lc-224) once its caller ships — an arc's stage-due moments are
  read moments by construction.
- **staleness:** beliefs age by KILL-CONDITION and by contradicting writes,
  never by clock (governed-persistence scout: interference over decay);
  premises re-ground at pickup (mechanism 5's existing seam).
- **exit:** `arc close` with a closed disposition vocabulary
  (goal-met / superseded / absorbed-into:<id> / abandoned-with-reason) —
  registered under the D-3 vocabulary contract WITH its OOV arm from birth.
- **growth:** bounded-by-exit (arcs are FEW and optional; a repo with ten
  open arcs is its own finding — see stop/yield).
- **trigger:** per-stage exit in the FULL vocabulary (requirement 1):
  `verb <name>` / `predicate <cmd>` (evaluated by `lanes.evaluate_trigger`,
  the one-evaluator law) / `operator-judged: <what they judge>` (the
  `none, declared why` arm — walk 2's taste referee, expressible from
  birth).

## The slot grammar (structural; items.py idiom fixes spelling)

Per arc: `goal:` (operator-attributed, stable) · `stage:` (current, from
the arc's own declared stage list) · `stages:` (each with
`exit: <trigger>`, `conduct: <allowed/forbidden act classes — prose,
consumed at stage entry by the session>` (requirement 2; v1
declared-not-enforced), `outward: yes/no` (requirement 8 — a `yes` stage's
close engages the carve-out floor: v1 renders a STOP line naming the
operator; no mechanized gate)) · `narrowing-shape:
eliminative | palette | none-with-reason` (requirement 3 — answers
Begehung axis A11 by construction) · `narrowing:` (the live picture;
OVERWRITTEN, its residue accumulating under `established:`) ·
`premises:` (the E12 INBOX: each `premise: <id> <text> basis: <mark per
the evidence-mark vocabulary> status: live|killed`; **the section is
REQUIRED and an empty one prints `premises: NONE RECORDED` — emptiness
visible, never absent** — the friction extract's requirement 6 verbatim;
E13's compiled assumptions are premises with `basis: DERIVED (assumption)`)
· `beliefs:` (`belief: <id> <text> basis: <…> kill: <condition|unknown>
cites: <premise/belief ids>`) · `yield:` (one line per round:
`round <n>: <decisive|nothing-new|instrument-repair> <one clause>` — the
arc-grain answer to friction requirement 1; the SERIES is printed by the
banner as "round N; last decisive: round K") · `deadlines:` (dated slots,
requirement 7, EXEMPT-BY-DESIGN from the time-word ban; each deadline's
observer is a GENERATED date-predicate LANE — the lane mechanism as the
intake observer walk 4 demands).

## Integration rulings (each supersedes an open question elsewhere;
## amendments land at the affected entries' next touch)

- **lc-225 (round-series readout): its home is the ARC's yield slot** for
  arc-carried work; the investigation record keeps the readout for arc-less
  work. lc-225's open home-question is answered so; amend at its pickup.
- **Multi-arc ordering (head-rule re-open (d)):** DEFERRED with a
  computable re-open — the moment a SECOND arc opens in one repo
  (`arc open` prints the standing count; two = the re-open event). No
  ordering machinery in v1; the head-rule decision's reach note stands.
- **lc-161 (decision absorption) and lc-226 (goal-advance):** the arc's
  goal slot is what a goal-advance fill READS; lc-226's enforcement-home
  question stays its own, but its fill's referent is fixed here.

## Session-independence: the kill test as acceptance

Gate (pre-registered): mid-arc, at an arbitrary moment chosen by the
operator or by dice, a FRESH context resumes from the arc file alone (no
chat, no summary). PASS = it names the current stage, the live narrowing,
the open premises, and the next act, and its next act is not a re-derivation
of a killed path. This is run on the PILOT (below), once, before v1 is
graded shipped — gate 1 (mechanical: writes happen and are read) before
gate 2 (effect), the design doc's own order.

## The pilot

The CachyOS freeze arc, per lc-239's recorded DERIVED note: beat 1's
authoring pass and the arc kind's first real trial share one repo. The
pilot arc is opened THERE when the lc-239 pilot runs (post-attack,
post-build); its kink harvest feeds both designs. Walk 1's registered
predictions (arc-walk doc) are graded against it — MODELLED claims meeting
their first real arc.

## Red-first arrangements (named now, built at build)

`arc open` without operator attribution → refuses (plant: an open with no
attribution line; control: one with). A stage exit `predicate` that
CANNOT run → BROKEN, distinct from quiet (reuses the evaluator's proven
contract; plant: unknown command). A premise KILLED while beliefs cite it →
the kill prints the citer list (plant: two-belief chain, kill the root,
both citers named; control: kill a leaf, empty list). Conservation over
arcs/ + arcs/closed/ (plant: hand-delete a closed body, SHORT fires).
`premises: NONE RECORDED` renders on an empty section (plant: strip it —
shape check fires missing-section, distinct from empty).

## Stop/yield (this mechanism's own)

Arcs are OPTIONAL, instantiated per-arc, never a per-project obligation
(walk 3; zero-arc repos run on the queue exactly as today). v1 = verbs +
schema + ONE pilot arc; no auto-instantiation, no ordering, no
verdict-capture mechanization (walk 2's verdict-capture seam is a DECLARED
stage input consumed as prose in v1 — its mechanization is its own later
item with its own incident pressure). YIELD = the pilot's kill-test result
and kink harvest. STOP = if the pilot's kill test fails twice after repair,
the design returns to the operator as a redesign question (the lc-239
gate's own continue-or-redesign, shared).

## Write-set (the build wave's boundary)

plugin/cli/lifecycle_core/arcs.py (new), cli.py (verb wiring —
REMEMBER lc-120's lesson: the hand-written dispatch table in test_verbs.py
derives the action tuple and MUST move with it, law 24's worked example),
declaration.py (kind registration + stage vocabulary), refusals.py (the
red-first rows above), items.py untouched, test/test_arcs.py (new),
test/test_verbs.py (the table), .claude/lifecycle.json (the kind's own
declaration in THIS repo). Schema question: the arc kind adds a KIND, not
a stage — no floor bump; if the attack round finds a schema-shape change
hiding here, that is a blocking finding (lc-218's MUST-NOT-BUILD pattern).
