# Design attack round 1 — findings of record (2026-09-19)

**Landed at the round desk per pass-3 NIT1: finding ids cited by the design docs must resolve in a tracked carrier, not a session scratchpad. Opus arm: the condensation below (34 findings; the ten-part message report is the report of record, booked at the desk). Astra arm: verbatim output follows.**

## Opus arm condensation
# Attack round — three locked designs at f8de2f0 (backup copy)

The REPORT is the ten SendMessage parts delivered to the dispatcher; this file
is a backup the message payload gate pushed me toward, not a substitute.
34 findings: V1-V12 (vocabulary contract), A1-A12 (arc kind), W-1..W-10 (waves).

## Vocabulary contract (docs/2026-09-19-vocabulary-contract-design.md)

- **V1 BLOCKING (lens 1/4).** P3's PREDATES-THE-MECHANISM population is not
  computable from the carrier. `items.SLOTS` = grade, requirement, goal,
  write-set, done-criterion, evidence, blocked-by (+ blocker-exercise,
  not-derivable); `Item` (items.py:452-473) carries no date;
  `blocker_slot_census` (items.py:2155) sees only `parsed`. All 8
  evidence-blocked items (lc-24, 53, 66, 82, 94, 136, 147, 199) have no date
  prefix in `requirement:`; lc-136 and lc-199 have zero amendments.
- **V2 BLOCKING (lens 6).** EXERCISE_EPOCH at DATE grain cannot discriminate on
  its own day: lc-175's build commit ae164bc is 2026-09-19 14:22:52 +0200 and
  131 commits carry that date, this round's own bookings included.
- **V3 BLOCKING (lens 1, law 24).** P4's write-set misses realizing files:
  `item ready` renders blockers at verbs.py:1792-1830 (not cli.py); the
  vocabulary is restated at cli.py:557-558, verbs.py:786/1037/1903,
  items.py:1573-1574/1983-1984, migrate.py:737, refusals.py:1297-1299;
  `BLOCKER_TYPES` is items.py:1007 and `blocker_untyped`'s row text says
  "three closed edge types" while declaring no route_set (refusals.py:4092-4105).
- **V4 BLOCKING (lens 2/6).** `cannot-express:` re-opens the door
  `blocker_untyped` closed — items.py:1572-1580 names untypeable blockers "a
  permanent silent park … nothing resolves a wait nobody can type". No clearing
  act, owner or re-ask is named.
- **V5 NOTABLE (lens 6).** P2's "makes read_moments AGREE with
  `_check_reader_when`" is false for 1 of 3 cited cases and leaves three more
  disagreements: `predicate` with no command (MALFORMED vs
  `kind_stage_undeclared`, declaration.py:1563-67), non-string `when`
  (UNDECLARED via declaration.py:1614 vs `declaration_malformed` at 1529),
  `none` with no why (NONE vs `kind_stage_undeclared`), and a PREFIXED reader
  with a `when` — `declaration_malformed` at 1534-41 while `read_moments` has no
  REF_BARE guard and EXECUTES (probe: `predicate touch <marker>` created the
  file).
- **V6 NOTABLE.** `vocab_without_oov`'s text claims a rendering property; its
  plant (`oov_form=None`) proves a data field. `renderer` is named and unused.
- **V7 NOTABLE (lens 1/3).** Observers row 4 has empty verb/record/check and
  names lc-234 as observer; the probe's Rider 2 bounds it to the roster channel
  and its quantity is prove-rows arrangement survival, which a Vocabulary entry
  does not have.
- **V8 NOTABLE (lens 4/5).** The widening arrow's observer is a review nothing
  runs (`audit`'s fire-rate is the judgment register's six rules, use-evidence
  0/0/0); STOP has no owner, cadence or carrier and uses the time-word shape
  banned at required-slots-as-an-autonomy-lever.md:67.
- **V9 NOTABLE (lens 7, reasoning-only).** None of f1/f4/f5 would have been
  caught by the contract; the three detection failures get no mechanism.
- **V10 NOTABLE (lens 3).** The always-on exemption carves out the channel it
  adds to (item check rides dotfiles session-scan.py:232-250, SessionStart at
  dotfiles settings.json:167); 2-6 new roster rows are admitted before the probe
  that measures the roster runs (baseline ROWS 116, PROSE_REST 6).
- **V11 NIT (lens 6).** D-8's six specimens are four (lc-235 is a decision
  blocker, lc-236 an item blocker), while `item check` names eight `evidence
  false` softlocks including lc-82 and lc-199.
- **V12 NIT (law 22).** P1's "registry unimportable = CNV" has no statable
  firing input.

## Arc kind (docs/2026-09-19-arc-kind-design.md)

- **A1 BLOCKING (lens 8).** The schema-shape change IS hiding: `carrier_homes`
  (declaration.py:1878-1907) is hardcoded to items/done/ledger and drops glob
  homes; either the arc carrier enters that machinery (carrier_homes +
  refusals.py:4096 route set + `_watched_schema_carriers` at 2657-2674 +
  migrate.py, which the write-set omits) or it sits outside one-schema-per-repo
  silently. Neither is answered.
- **A2 BLOCKING (lens 8/1).** `operator-judged` is not in
  `TRIGGER_MODES=("verb","predicate","none")` (declaration.py:182, enforced
  1259-1275); the doc calls it both a full-vocabulary member and the
  `none, declared why` arm. lc-239 beat 1 authors 26 triggers on the round's
  close against exactly this vocabulary.
- **A3 BLOCKING (law 23).** `recording-act` is required (declaration.py:1240,
  1247-1250) and unnamed; the audit's growth check reads fire-log exit events
  and reports `kind_grew_without_exit` on this shape (live: `done bodies`, 115
  instances, 0 events). No firelog wiring in the write-set.
- **A4 BLOCKING (invariant 3).** One kind, two homes (arcs/ and arcs/closed/),
  where the form template it cites uses two kinds (items / done bodies).
- **A5 NOTABLE.** Conservation over both homes has no counter home; item
  conservation reads ITEMS.md's head (schema/baseline/added/compacted, lines 1-4).
- **A6 NOTABLE (lens 1/3).** The declared reader is a hook in another repo
  (dotfiles session-scan.py), which calls four lifecycle verbs and knows nothing
  of arcs; and it is new ungated always-on session-start output while W1's line
  is gated.
- **A7 NOTABLE (two exits).** Rulings on lc-225 (READY, blocked-by NONE),
  lc-226 and lc-237 land in no carrier; "amend at its pickup" names an actor who
  cannot know the amendment is owed (law 8).
- **A8 NOTABLE (lens 5/8).** The kill test has no independent grader, its
  "not a re-derivation of a killed path" clause is unfalsifiable at a moment with
  no killed path, and "run once" contradicts "fails twice after repair".
- **A9 NOTABLE (lens 6).** Non-dated external events get no stage-exit arm while
  the same round mints `external <event>` for blockers.
- **A10 NOTABLE (lens 1/4).** Deadline lanes have no generating verb and no
  retirement; the declaration's `lanes` list ([] today) grows unpruned.
- **A11 NIT.** `arc_goal_unattributed` establishes that a line exists, not that
  the operator said it.
- **A12 NIT.** grammar.py absent from the write-set while items.py:1034 says
  `render_block` is the only place the on-disk shape is spelled.

## Wave designs (docs/2026-09-19-wave-designs.md)

- **W-1 BLOCKING (lens 1).** "Disjoint write-sets except declaration.py" is
  false by its own write-sets: W1∩W4 = verbs.py + test_verbs.py; W1∩W2 = cli.py.
  The arc lane's overlaps with P1 (refusals.py), P4/W2 (cli.py) and W4
  (test_verbs.py) are unnamed.
- **W-2 BLOCKING (lens 1/8).** W4's machinery does not exist: plugin/hooks holds
  only pre-commit; plugin.json declares only git-hooks.pre-commit and says
  harness `hooks` there breaks install; no dotfiles hook references desk state;
  `cmd_desk_state` writes value/argument/at/desk/desk_source/repo (desk.py:158-180)
  — no session URL, no model; the one live file (5171166b…, 2026-09-13) has no
  `repo` key.
- **W-3 BLOCKING (invariant 2, law 24).** The `desk state` kind declares
  `writer: verb:desk state` / `trigger: verb desk state`; W4 makes a hook the
  writer without touching `.claude/lifecycle.json` or plugin.json.
- **W-4 NOTABLE (lens 4).** desk state is unbounded-with-reason with an exit
  DECLARED-NOT-IMPLEMENTED; "fresh" names no threshold, so the ambiguity arm
  fires more often the more the repo is used.
- **W-5 BLOCKING (lens 6).** W3 closes on the pattern axis and leaves the file
  axis: emit_sites/relay_sites glob lifecycle_core/*.py (roster.py:105-121), so
  plugin/hooks/pre-commit:154's live `FINDING [{f.row}]` relay is invisible and
  the "7 relay sites" baseline is 7 of 8.
- **W-6 NOTABLE (laws 2/3/24).** W1's finding exit has no refusal row and no
  refusals.py in the write-set; the unbracketed-FINDING form is precedented and
  invisible to the coverage scan.
- **W-7 NOTABLE.** W2 re-forms D-5's decided `re-derive-at-read:` slot marker
  into an evidence-mark member with no recorded supersession.
- **W-8 BLOCKING (law 26).** W2 writes nothing at the consuming moment while the
  repo holds `blocker-exercise:` one import away — a demand already measured at
  0 exercised / 8 unexercised; "recorded where caught" names no home.
- **W-9 NOTABLE.** W2's grammar check grades a mark's argument where
  `evidence_mark_problem` is documented presence-only (items.py:286-292); new
  refusal, refusals.py absent from the write-set.
- **W-10 NIT.** roster.py carries five regexes and only three are verdict-keyed;
  "all four scan patterns" matches neither number.

## Lenses walked with nothing found, and confirmations

- **Lens 2 on its own axis:** nothing found. Every required slot demands the
  statement, not the answer; P2 moves the default rather than adding a duty.
- **Verdict axis (W3):** closed. A scan of the package for any uppercase word
  carrying a bracketed ident returns 119 `FINDING` and 3 `COULD NOT VERIFY`,
  nothing else.
- **Reproduced at HEAD:** ROWS 116 / PROSE_REST 6; the 7 relay sites; census
  "0 exercised, 8 UNEXERCISED"; r3's three-probe matrix; 26 kinds; the
  `desk state` kind's existence.
- **Not done, named:** `--test` and `prove-rows` not run (no repo writes, and
  neither answers a design question here); the design of record's §3.1 in
  claude-code-cache-fix not opened, so V3's §3.1 claim rests on this repo's own
  restatements.

## Astra arm r1, verbatim
The designs are **not build-ready**. The strongest blockers are a contradictory W1 fixture, attribution that can falsely identify a human’s commit, and arc persistence that passes its acceptance test while losing required state.

Read-only review; no suites or state-changing commands run. I resolved blocker values with the repository’s parser and read the amendment tails.

**Vocabulary contract — ranked findings**

1. **BLOCKING — Registration does not prove the consumer contract.**  
   **Lenses 1, 4, 7.** P1 promises to detect a consumer lacking distinct OOV rendering, but its plant removes `oov_form` from registry metadata. A populated registration beside a consumer that ignores or folds OOV passes that arrangement. Only blocker OOV gets a concrete consumer exercise; grades, trigger vocabulary and census buckets receive no specified end-to-end acceptance/rendering behavior. Thus the registry can certify precisely the disconnected mechanism it exists to prevent.  
   **Basis:** `docs/2026-09-19-vocabulary-contract-design.md:25–34,58–68` (reasoning from the specified arrangements).  
   **Repair direction:** Require each registration’s proof to traverse its actual admission and consuming paths.

2. **NOTABLE — The epoch measures item age, not opportunity to record an exercise.**  
   **Lens 6.** P3 permanently classifies by original booking date. An old item acquiring a new evidence blocker after deployment still “predates”; a repo adopting the mechanism later than lifecycle’s build date has the converse problem. The carrier’s fixed slots contain no booking timestamp, and the design supplies no historical-resolution or unavailable-history contract. Its two fixtures cannot expose these states.  
   **Basis:** design `:47–56`; `plugin/cli/lifecycle_core/items.py:70–71,2155–2187`; exercise recording occurs at the blocker admission seam, `plugin/cli/lifecycle_core/verbs.py:918–920`.  
   **Repair direction:** Define the counted opportunity and its provenance, including an unverifiable-history answer.

3. **NOTABLE — P2 repairs the sampled malformed forms, leaving malformed siblings benign.**  
   **Lenses 6, 7.** “Parses to no known mode” covers the three recorded probes, but not all invalid declarations. Empty/non-string `when` currently becomes UNDECLARED; `none` without a reason becomes NONE. Validation rejects both. The six controls plus three probes can pass while the instruments still disagree.  
   **Basis:** design `:36–45`; `plugin/cli/lifecycle_core/declaration.py:1529–1533,1555–1560,1614–1622`.  
   **Repair direction:** Cover the validator’s complete invalid-state partition, preserving absence separately.

4. **NOTABLE — D-10’s surviving repair is named but never implemented.**  
   **Lens 1.** The amended lc-237 and D-10 require **never-run versus runs-quiet**. Registering the trigger syntax vocabulary `verb/predicate/none` does not supply execution status, a last-run record, or its reader. No contract part realizes that distinction. All listed checks can pass with lc-237’s residue untouched.  
   **Basis:** `ITEMS.md:1327`; `docs/2026-09-19-round-decisions.md:148–155`; contract `:27–30,36–74`.  
   **Repair direction:** Give the surviving trigger-status requirement an explicit producer, carrier and consumer.

5. **NOTABLE — Existing banner plumbing is mistaken for an erosion exemption.**  
   **Lens 3.** P4 adds a standing OOV count to every session banner; P3 changes that banner’s census surface. These are additional always-on content even though the caller already exists. Moreover, lc-234 explicitly measures roster-row survival and is silent on session behavior: it cannot establish that registrations are “still consulted.”  
   **Basis:** contract `:89–91,109–113`; `ITEMS.md:1294`; `docs/purpose.md:72–78,141–144`. The arc’s ungated banner and W4’s “hook already runs” rationale repeat this boundary error.  
   **Repair direction:** Inventory added always-on content and execution explicitly, apply the declared gate, and preserve the probe’s stated reach.

6. **NOTABLE — The widening loop has no specified retirement outcome.**  
   **Lenses 4, 5.** Skipping the fire-rate review leaves OOV instances accumulating as permanent mint signals; no other moment detects that the review stopped. Even when run, “zero recordings asks complete-or-unread” is a question, not a stop/yield disposition. Neither consumed OOV instances nor obsolete registrations have a specified retirement leg.  
   **Basis:** contract `:84–100` (reasoning-only lifecycle gap).  
   **Repair direction:** Specify the recurring review’s observable completion and the dispositions that retire signals or stop the mechanism.

**Arc kind — ranked findings**

1. **BLOCKING — The tool-only carrier lacks the writes needed for continuity.**  
   **Lenses 1, 4, 8.** The verb list has no explicit write contract for updating narrowing, preserving its `established:` residue, recording taste verdicts, or changing deadlines. No act requires work performed during a stage to update the carrier. Stage-entry conduct is “consumed” without a defined read action. A pilot killed immediately after a diligent manual update can pass while an ordinary mid-stage death loses the latest elimination or verdict. That does not satisfy persisted truth “at every moment.”  
   **Basis:** arc design `:33–48,65–87,105–111,139–140`; `docs/purpose.md:43–56,79–95`; walk synthesis `:25–33,65–66`.  
   **Repair direction:** Define the write/read seams for every load-bearing state change and exercise kills between those changes.

2. **BLOCKING — Killing a premise does not persist downstream invalidation.**  
   **Lenses 1, 7, 8.** `arc premise` merely prints affected instruments/beliefs. `arc reopen` persists flags only within the arc and prints item citers. After output leaves context, downstream beliefs and items can remain authoritative. The two-belief red-first checks printed names, so it explicitly passes this failure. Additionally, `established:` residue is not required to use belief IDs, bases or kill conditions.  
   **Basis:** arc design `:37–42,73–81,127–129`; `docs/purpose.md:109–116`.  
   **Repair direction:** Make invalidation survive the command across every supported belief surface and test its later consumption.

3. **BLOCKING — The amended close-time requirement disappears.**  
   **Lenses 1, 7, 8.** lc-231’s amended evidence explicitly asks the closing arc to demand the environment-learning question: a runbook cited, minted or declined, with presence computable and the answer judged. The design provides only disposition plus move. Its entire acceptance battery can pass while every completed journey again requires operator pressure to produce the next traveler’s environment.  
   **Basis:** `ITEMS.md:1270` (`amended-evidence`, including its “SECOND HALF”); arc design `:43–44,122–144`.  
   **Repair direction:** Carry the amended close-seam requirement into the design, or record an explicit disposition rejecting it.

4. **BLOCKING — The outward STOP occurs after the act it must govern.**  
   **Lenses 1, 8.** An outward stage’s **close** prints the STOP. An outward act performed during that stage can already have happened before the warning. Calling this “no mechanized gate” accurately limits enforcement, but does not fix the timing. None of the red-first arrangements exercises outward action or approval.  
   **Basis:** arc design `:69–71,122–132`; `docs/purpose.md:120–122`; walk synthesis `:48–55`.  
   **Repair direction:** Place the operator boundary before the outward act and exercise that ordering.

5. **NOTABLE — Deadline lanes have neither a complete intake path nor a retirement path.**  
   **Lenses 1, 4.** Generated date-predicate lanes cover dates, not undated external events such as an arriving letter. The design names no event-intake observer. It also does not specify who regenerates or removes deadline lanes after rescheduling, stage advance or arc closure. Those generated stores can outlive the arc and keep firing.  
   **Basis:** arc design `:57–61,84–87`; walk synthesis `:48–53,70–71`. Existing lanes are routing bodies with `Trigger`, workflow and `Ends`, not just predicates: `plugin/cli/lifecycle_core/lanes.py:162–171`.  
   **Repair direction:** Specify intake and full lifecycle ownership for generated observers.

6. **NOTABLE — “Ten open arcs” violates the flow law and does not bound stored growth.**  
   **Lenses 4, 5, 8.** Ten open arcs are declared a finding solely by count, contrary to the explicit ban on size-based growth control. Meanwhile closing moves bodies into `arcs/closed/`, which conservation still counts; no exit or justified unbounded-growth declaration covers that accumulating population. The pilot’s stop condition resolves neither issue.  
   **Basis:** arc design `:30–32,55–56,134–144`; `CLAUDE.md:32–38,75`.  
   **Repair direction:** State growth policy over both homes in terms of flow, with an explicit policy for retained closed bodies.

7. **NOTABLE — The schema ruling leaves the new carrier’s version boundary undefined.**  
   **Lens 8.** Adding a kind does not by itself prove a global floor bump is needed. But the design also introduces a new structured, tool-owned carrier while specifying no schema head, version validation or migration participation. Existing schema discovery recognizes only items, done bodies and ledger lines, and excludes wildcard homes. Consequently the claimed items-template reuse does not inherit version protection.  
   **Basis:** arc design `:63–87,154–156`; `plugin/cli/lifecycle_core/declaration.py:45–74,1872–1906`; `CLAUDE.md:205–218`.  
   **Repair direction:** Resolve the arc carrier’s version contract explicitly before affirming “no floor bump.”

**Wave mechanisms — ranked findings**

1. **BLOCKING — W1 requires a fixture that P2 explicitly makes invalid.**  
   **Lenses 1, 6, 8.** W1 expects `when: verb:audit` to FIRE after an audit marker. P2’s inherited matrix requires that exact input to become MALFORMED. Current reader moments deliberately exclude `verb`; verb-occasioned reads use the reader reference itself. No audit-marker mechanism is specified either. The locked designs cannot both pass without changing one design’s semantics.  
   **Basis:** wave design `:22–25`; vocabulary design `:42–45`; `docs/begehung-findings-2026-09-19-r3.tsv:2`; `plugin/cli/lifecycle_core/declaration.py:1546–1553`.  
   **Repair direction:** Reconcile the fixture and supported vocabulary; any intentional shape widening needs its own compatibility ruling.

2. **BLOCKING — Exactly one candidate does not identify the committing session.**  
   **Lenses 6, 8.** A human running a carrier verb while one fresh agent desk exists in that repo receives the agent’s trailer. Likewise, a second agent without its own recorded file receives the first agent’s URL. These are precisely the “one fresh file” cases the proposed test declares successful. Candidate uniqueness establishes neither authorship nor caller identity and breaches lc-52’s retained must-not-move.  
   **Basis:** wave design `:73–89`; `ITEMS.md:150,157`; `plugin/cli/lifecycle_core/desk.py:73–95`.  
   **Repair direction:** Require evidence tying the candidate to the caller, with human and different-session controls.

3. **BLOCKING — W4’s supposedly existing writer and carrier fields do not exist.**  
   **Lenses 1, 4, 7.** The plugin manifest declares only a Git pre-commit hook; no session-start hook exists there. Desk-state is written by `desk state`, carries `repo` and `at`, and has no model, session URL, cwd or trailer block. Its writer overwrites the entire object, so even a new hook’s extra fields disappear on the next normal state write unless that writer changes. W4’s write-set omits `desk.py`, the manifest and the declaration. “Fresh by timestamp” also supplies no freshness or liveness predicate; dead-desk deletion is explicitly unimplemented.  
   **Basis:** `plugin/.claude-plugin/plugin.json:5`; `plugin/cli/lifecycle_core/desk.py:159–187`; `.claude/lifecycle.json:398–412`; wave design `:74–90`.  
   **Repair direction:** Specify and include the actual writer, hook registration, field preservation and candidate-lifecycle changes.

4. **NOTABLE — PERISHABLE proves a warning was rendered, not that evidence was refreshed.**  
   **Lenses 1, 6, 7, 8.** The picking session must remember to execute the command; no recorded result or unanswered-demand check follows. Thus the original stale-evidence failure survives a successful banner test. The parser tests also miss a sibling: a slot containing a valid `MEASURED` token plus malformed `PERISHABLE` can pass the existing “any mark present” predicate. An entirely unmarked comparison is not a control for that case.  
   **Basis:** wave design `:39–53`; `plugin/cli/lifecycle_core/items.py:310–338`; `docs/purpose.md:79–89`.  
   **Repair direction:** Define the refresh outcome consumed at pickup and explicitly test malformed marks inside mixed evidence.

5. **NOTABLE — W3 misstates its population and leaves detection dependent on a one-time sweep.**  
   **Lenses 6, 7.** There are four emit-name patterns **plus** `_RELAY`, across two scanners—not four patterns total. `_LITERAL` and `_LITERAL_CNV` are intentionally verdict-specific siblings, so “found-and-widened / already-agnostic” cannot truthfully describe each pattern. The relay regression fixes this instance, but a commit-body sweep does not make future omissions visible.  
   **Basis:** wave design `:57–69`; `plugin/cli/lifecycle_core/roster.py:63–80,106–119`.  
   **Repair direction:** Define the actual population and test the supported verdict-by-emission forms as a continuing contract.

6. **NOTABLE — The stop/yield claims cannot grade several shipped outcomes.**  
   **Lenses 4, 5.** W1 may deliberately ship verb-only, yet its yield requires a banner catch. W2 names a first catch but no no-yield disposition. W4 promises an unmarked-commit rate “at the fire log,” but the log records verb invocations/outcomes, not the marked and unmarked commit population; the design adds no writer for that metric. All three can ship without ever reaching an evaluable stop/yield decision.  
   **Basis:** wave design `:17–21,29–31,51–53,92–94`; `plugin/cli/lifecycle_core/firelog.py:51–63`.  
   **Repair direction:** Give each deployable branch a measurable yield and an explicit no-yield disposition.

7. **NOTABLE — The declared parallel build boundaries are factually overlapping.**  
   **Lens 1.** W1 and W4 both change `verbs.py`; W1, W4 and arcs share `test_verbs.py`; W1, W2 and arcs share `cli.py`; arcs and P2 share `declaration.py`. P4 also needs `verbs.py`: that is where `_blocker_state` renders and routes blockers, despite P4 naming `cli.py` rendering instead. The wave’s claim of disjoint sets misses these dependencies.  
   **Basis:** wave design `:26–28,49–50,89–90,98–104`; arc design `:148–154`; vocabulary design `:73–74`; `plugin/cli/lifecycle_core/verbs.py:1735–1835`.  
   **Repair direction:** Reconcile write-sets against actual producers, consumers and shared tests before dispatch.

**Per-lens nothing-found statements**

- **Lens 2 — OVER-CONSTRAINT versus the model’s default:** No substantiated finding in any of the three designs. The defects above concern missing demands, invalid defaults or unsupported lifecycle claims—not a demonstrated unnecessary required write.
- **Lenses 1, 3, 4, 5, 6, 7 and 8:** Findings reported above; none yielded an empty result.

One small factual correction: the vocabulary design’s lc-66 footnote reverses the dependency. **lc-67 is blocked by lc-66**, whose effective blocker is still `evidence false`; lc-66 is not behind lc-67 (`ITEMS.md:208,217`).
