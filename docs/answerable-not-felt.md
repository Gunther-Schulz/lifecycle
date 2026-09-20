# Answerable, not felt — the assert-vs-query class and the persist-and-query lever

**Status:** design direction for pickup, opened 2026-09-18 (desk session 04c231,
CachyOS-Setup marvel-rivals freeze arc; peer desk 9a744c). Booked as **lc-157**.
Not a spec yet — the point is to dig deeper next session. This note is the
carrier; the ranked mechanisms below are the candidate features.

> **READ `answerable-not-felt-research.md` (this directory) BEFORE ACTING ON
> THIS NOTE.** The three research lanes this note's last section calls for were
> dispatched and returned on 2026-09-18 (desk 79ce75). Their result is a
> **correction to this note's central framing, not a confirmation of it**, so
> anything built from the text below without reading it will be built on the
> wrong variable.
>
> The short form: this note offers *momentum independence* and *role
> separation* as the two candidate explanations for the desk/peer gain. Neither
> is the variable. Role separation over the **same information** is
> decision-theoretically dominated by a single centralized decision maker
> (arXiv:2603.26993, verbatim from the raw abstract) — so a desk that grades its
> peer's *reports* should be expected to underperform no split at all. What does
> the work is an **independent signal the generating party cannot see or
> influence while producing its answer**. The desk's whole value is its
> independent reads of the artifact.
>
> Consequence for the design below: this note states **timing** ("triggered at
> the seam") as the load-bearing property. It is not — **independence** is, and
> timing only answers *when to fire*. A seam-triggered LLM self-reflection
> inherits the identical failure mode as continuous self-monitoring, merely
> fired less often. The five ranked mechanisms all happen to sit on the right
> side of this, because they are deterministic rather than reflective — but that
> is currently good taste, not a stated criterion, and it should become one.
>
> **Open decisions as of 2026-09-18**, none of them made: (1) which mechanisms
> to build — the desk's recommendation on the evidence is #1 (verify-the-
> verifiers) plus a narrowed #2 that runs the *already-executable* `blocked-by:
> evidence` predicate at BOOKING rather than only at read time, with #3-#5 held;
> (2) whether to admit the two candidates the research adds — independent-
> observer verification as #0, and admission control at the world-boundary,
> which maps onto the corpus's existing irreversible/outward gate; (3) the
> plugin-boundary question, which the note's own reasoning arguably settles
> already (lifecycle owns per-project attribution, files stay out of the repo
> tree). A corpus mint needs the operator's GO, asked first-hand.
>
> **Downstream and deliberately not started:** the dotfiles mint round over the
> unharvested `~/.local/state/claude/course-corrections.md` lines. Order is
> lifecycle first — a mechanized lever makes the prose rule it absorbs a
> retirement candidate, so minting ahead of these decisions risks work in the
> wrong direction. Scope measured at
> `dotfiles/docs/directives/2026-09-18-corpus-arc-handoff.md` (superseded as a
> handoff; its §Scope and §"Day one" survive).

**Provenance / lookup.** The two sessions' full transcript UUIDs are deliberately
NOT written here: this repo's pre-push leak scan treats a session UUID as a
capture identifier and blocks it (it blocked this arc's earlier lifecycle push
over exactly that). Short refs — desk `04c231`, peer `9a744c`. The `.jsonl`
transcripts live locally under
`~/.claude/projects/-home-g-dev-Gunther-Schulz-CachyOS-Setup/`, and the exact
filenames are recorded in the arc's local (unscanned) investigation record,
`~/.local/state/claude/investigations/CachyOS-Setup--marvel-rivals-freeze-rootcause.md`
(MOVES, 2026-09-18) — so the JSON is findable without leaking the ids into
public history.

## North star (operator, 2026-09-18)

The goal is to improve the operator↔LLM interaction so work becomes more
**DEPENDABLE, EFFICIENT, and AUTONOMOUS** — and this serves BOTH sides: the
operator gets reliable output with less babysitting, the agent gets to run
further end-to-end instead of stalling at every check. The three are not a
tradeoff but a sequence — **dependability is what earns autonomy** (an agent can
be given more rope only once its output can be trusted, which is exactly what
querying-instead-of-feeling buys). Everything below is means to this end, and it
is the pruning test: a mechanism that does not move dependability, efficiency, or
autonomy does not belong here.

## The stance underneath — ENABLE, don't constrain (operator, 2026-09-18)

The deepest framing, and the reason this beats more rules. A corpus built as a
pile of PATCHES is CONSTRAINING — each rule reacts to a seen failure ("don't do
X, always check Y, remember Z") — and that has a ceiling: it can only patch
failures already seen; every patch costs context and attention every turn; the
remember-to ones under-fire anyway; and — measured in this very corpus
(skill-craft) — a strong model steered too tightly performs BELOW its own
default. Over-constraining suppresses the intelligence it is paying for.

The alternative is to ENABLE via the ENVIRONMENT: build a ground where the right
move is the natural move and the wrong one is hard or visible (the pit of
success), instead of a mind that must hold rules. Then attention is spent on the
PROBLEM, not on self-policing; the environment carries the FLOOR (mechanically,
reliably), the intelligence provides the CEILING (unburdened). This SCALES where
patching does not — a good ground catches whole CLASSES of failure at once,
including unenumerated ones, because the freed intelligence handles the long
tail, not a rule.

This RE-SORTS the corpus rather than deleting it: mechanizable patches move into
the environment (their prose retires — see the payoff section); the genuine
work-ETHICS — disprove before building on, enumerate before claiming complete —
STAY, because those are stances a mind holds, not bookkeeping a mechanism can
carry. End state: a SMALLER corpus that is more purely about judgment, on a
ground good enough that intelligence can just work. Same family as daneel
(investigation state held externally and QUERIED, not carried in the head) and
statiker — build the ground, do not shackle the worker.

The SPLIT (right corpus content vs. patch-to-retire) is not new — it is the
corpus's own `ethic vs lens` test (the maintenance doctrine's abstraction probe:
broad stances that inform every task STAY; situational "when X watch Y" patches
go to project/lens/hooks). What enable-vs-constrain ADDS is a COMPLEMENTARY AXIS
at that gate: the ethic/lens test sorts by SCOPE (general vs situational), while
enable/constrain sorts by EFFECT (frees the intelligence vs over-steers it below
its default). They are not the same — a rule can read as a general "ethic" and
STILL over-constrain, which the scope test alone misses. Candidate for a next
corpus pass: fold enable/constrain in as an explicit second criterion beside the
abstraction probe, so a general-but-suppressing rule is a retirement candidate on
its EFFECT even when its scope looks fine.

## The class

An agent asserts a STATE OF ITS OWN WORK from memory or feeling instead of
QUERYING it, and — the load-bearing part — **the wrong answer is shaped exactly
like the right one.** A clean-looking green, a "nothing owed", a "verify passed",
a false absence. Because success and failure are indistinguishable at the point
of assertion, nothing prompts a second look, and the error is caught by a
person, a peer, or an accident — never by the thing that should catch it.

The corpus already NAMES this (Fixing: "one's own past output ... checked there
before it is asserted"; the COUNT and the NEGATIVE are the under-served halves,
because a tally feels like recollection). What is missing is not a rule — it is
a MECHANISM that makes the felt state answerable at the moment it is asserted.

### Evidence — one session, 2026-09-17→18 (the pile the operator and peer mapped)

- miscounted armed watches asserted inside a closable verdict ("both retired" — a third was still armed)
- "nothing owed / idle" asserted twice before the check that showed a members-sweep was owed
- an unquoted `$t` verify loop: 8 of 9 checks never ran, failure shaped like a pass (grep for FAILED finds none)
- freeze-chain-class.py mode 644: a registered verify entry that could never execute
- a `pgrep -f` "GAME UP" false positive on a closed game (desk, this session)
- cs-45's booked premise "recoverable offline" — unsatisfiable by construction, survived unexamined until executed
- a defect's 558-vs-3 ratio carried from another session as a fixed property (transfer-test failure)
- cs-54: the census "COVERAGE ENDED" marker missing on clean quits, so the exit witness cannot discriminate crash from quit
- a coverage-span probe reading each file's last line as a timestamp — well-formed files (with the marker) read as malformed

All one shape: a state assumed rather than queried, its failure indistinguishable from success.

## Why it recurs (so the fix targets the cause)

1. **Momentum.** The intake/verify check is skipped under the same momentum that
   carries the work — the observed condition under which the gauge gets skipped.
   **AMENDED 2026-09-18 (desk 9553b0), and the amendment bounds this item
   rather than removing it.** Momentum explains why a party cannot reliably
   check ITSELF; it does not explain why a desk/peer split helps, and the
   original note used it for both. It is also not a defect to be suppressed:
   momentum is what depth in the work COSTS, and the peer's depth is exactly
   what makes its reads better than the desk's. A design that treated momentum
   as something to remove would damage the party doing the work.
2. **The trigger is a feeling.** "Do I feel done / idle / clean?" is judgment-shaped
   and under-fires. The rule that should fire (e.g. "sweep the carrier for siblings
   when a defect-class is found") fires late, by luck, not by mechanism.
3. **Failure looks like success**, so there is no red to notice.

## The lever

**Convert the felt judgment into a mechanical, answerable query against PERSISTED
state, triggered at the seam.** Each felt state has a queryable proxy:

- "Am I idle?" → "has any defect-class find closed since the last sweep of its carrier?" (yes/no)
- "Did verify pass?" → "did N registered checks actually EXECUTE?" (count vs registered, not absence-of-red)
- "Is this booking complete?" → "does its done-criterion dry-run pass against data already in hand?" (exercise, not read)

### The deeper insight — persistence has a GUIDING function by mere existence

The investigation record helps not because it stores data but because it keeps
"where we are" IN FRONT OF THE MODEL'S EYES at the moment of the decision, so the
decision QUERIES the record instead of RECALLING from brittle memory. That is the
corpus's "a form whose absence is visible binds; an obligation with no output
under-fires" — the persisted record IS the form. Measured this session: the
record's OPEN/NOW slots kept the GPU question alive across hours and turns and
made its result read as PIVOTAL rather than lost in noise (it had a hand in the
finding), while every felt-state assertion above went wrong. General form:
**persist the state that judgment would otherwise hold in memory, in a shape
re-read at the decision point.** The operator's instinct — that persisting the
process itself guides — is this, generalized.

## Candidate mechanisms, ranked by how REAL vs hopeful

1. **Verify-the-verifiers** (most real, general, mechanical). A repo's declared
   verify block asserts how many checks EXECUTED (count vs registered); a
   could-not-run or a suspiciously-quiet pass is a FAILURE, not a pass. Run at
   session-start and on-commit. Catches the mode-644 + unquoted-loop class. The
   lifecycle plugin already knows the registered checks — natural owner.
2. **Booking-time done-criterion dry-run** (the one to defend on ceremony cost).
   Exercise a booking's done-criterion against cases in hand AT BOOKING — the
   corpus's red-first-at-booking as a mechanism. Catches cs-45's
   unsatisfiable-by-construction class at write time, which nothing but
   EXECUTING the criterion would show.
3. **"Idle is answerable."** A query — "has a defect-class find closed without
   its carrier being swept?" — fires the owed sweep at the FIND, not by a lucky
   quiet moment. Catches the false-idle / late-sweep class.
4. **Per-write record lint.** Widen lc-156 (the investigation-record checker) to
   fire per-WRITE, not only at close — a basis-less claim, a NOW without a
   kill-condition, an OPEN whose probe is not two-way, caught as it is written.
5. **During-session class-recurrence counter** (hypothesis). Count same-class
   corrections over the corrections carrier as they happen ("3rd today"), since a
   class two mistakes share is invisible from inside either one. This session:
   the single-sample-for-a-population class recurred ~5×, surfaced only at the
   close harvest.

## The honest boundary

The class that stays MANUAL: prose claims about runtime behaviour going stale
(a bound, an "armed on request" line). No cheap general mechanism — operator as
backstop. Precipitate the computable slice; leave the judgment remainder as
prose. This note is "mechanize the answerable half", never "mechanize everything".

## Companion question (#1 from the operator)

The investigation-record feature currently lives as a CORPUS discipline
(calibration module + dotfiles format file). lc-156 already books its mechanical
CHECKER into this plugin — so the mechanism is migrating to lifecycle regardless.
Open question for next session: should the whole FEATURE (not just its checker)
have its home in the lifecycle plugin, given it is the same persist-and-query
family as everything above? Decide against the plugin's boundary, not by default.

**Operator's motivation (2026-09-18):** the records persist GLOBALLY
(`~/.local/state/claude/investigations/`, one flat dir) and cannot be attributed
to a project except by the filename prefix (`<project>--<arc>.md`) — so consider
persisting them at PROJECT level for real attribution. **But the global home was
a deliberate choice** (dotfiles `claude/investigation-record-format.md`): tool
state (XDG), OUTSIDE every repo AND outside `~/.claude/`, so (a) no project repo
is dirtied by the record, (b) no permission dialog fires (the `.claude/`-shape
protection), (c) it survives across repo states and branches. A project-level
move must KEEP those three benefits — so the likely shape is the lifecycle
plugin OWNING per-project attribution (a registry, or per-project tool-state
keyed to the repo) while the files stay OUT of the repo tree, rather than
literally moving them into the repo. Understand the original rationale before
changing it — the operator flagged this explicitly, and the format file states
it verbatim.

## Strengthen the "desk" role — TWO ASYMMETRIC INFORMATION HOLDERS (operator, 2026-09-18, amended same day)

**THIS SECTION WAS REWRITTEN IN PLACE on 2026-09-18 (desk 9553b0) and its
earlier text is in git history, not below.** It previously argued that the desk
works because it is a CHECK ON THE PEER'S MOMENTUM. That framing is refuted and
is not preserved here as a second standing version: an appended correction
leaves both readings alive and the reader who stops at the first takes the
superseded one.

**What replaced it, and it came from the operator's own experience before any
paper was read.** The desk is not the checker and the peer is not the checked.
They are TWO PARTIES HOLDING DIFFERENT INFORMATION, each an independent signal
to the other:

- the **peer** is working on the THING. It reads the actual files, sees what is
  really there, and goes deeper than any summary — so it very often corrects
  the desk, and its depth is the reason it can.
- the **desk** holds the OVERVIEW and the record, and is not inside the flow —
  so it catches what a party deep in one thread cannot see from there.

Neither direction is the mechanism alone. What makes the pair work is that each
holds information the other cannot see while producing its own answer.

**Why this is the version that survives the literature rather than a softer
restatement of the old one.** arXiv:2603.26993 is decisive precisely on the
old framing: role separation over *the same information* is decision-
theoretically dominated by one centralized decision maker. A desk that only
re-grades what the peer reports IS that dominated case. Two parties with
genuinely different information is a different case, and it is the one the
operator described from experience. So the correction is not "momentum was
wrong, independence is right" — it is that independence must be REAL
INFORMATIONAL independence, which mutual asymmetry supplies and a role label
does not.

Measured this session: the desk verified the peer's load-bearing claims at the
artifact rather than trusting them — kernel BTF, the GPU-log ordering, the
deploy (md5 + service-load-time), the closable state — and the peer's own
self-corrections landed precisely because it reported into a desk that queries.

**And the reverse direction is measured too, which the original text had no
room for.** 2026-09-18, four instances in one day, running BOTH ways and
including operator→desk: a peer corrected this desk's inverted `args.pid` /
`pid` hypothesis by reading the two deployed `.bt` files instead of applying
the desk's naming (had it deferred, it would have broken the surviving tracer
to match the dead one); this desk widened that peer's own defect report from
two observed commits to the whole surface by counting call sites; that peer
then found a non-atomic carrier write in THIS repo, from outside it, that no
self-review here would have found; and the operator corrected this desk's claim
that tier explained any of it — both sessions were Opus, so that axis was never
varied. Every one of the four was caught by a party with different information,
none by a rule firing.

Measured this session: the desk verified the peer's load-bearing claims at the
artifact rather than trusting them — kernel BTF, the GPU-log ordering, the
deploy (md5 + service-load-time), the closable state — and the peer's own
self-corrections landed precisely because it reported into a desk that queries.
The desk IS the "answerable, not felt" lever embodied as a session ROLE: it
forces the executor's state to be QUERIED (reported and independently verified)
rather than FELT.

**Design direction:** define the desk by WHAT IT INDEPENDENTLY READS, never by
its authority over the peer. A desk that grades the peer's prose is the
dominated case and should be expected to underperform; a desk that reads the
artifact itself is a second information holder and is where the gain lives.
Corollary the old framing hid: **report-grading is a courtesy, not a desk
duty** — and a desk's own claims are as gradeable as a peer's, which the
one-directional reading made unaskable.

This still makes the three threads ONE thing, but the third hat changed: a
**persisted record** (state a session queries, not recalls), a **seam-trigger**
(a check fired by a moment, not a feeling), and a **pair of parties whose
information does not overlap** — no longer "a party out of the flow querying an
in-flow party".

**The open question, now stated so it can be MEASURED rather than argued**
(operator, 2026-09-18): is the reliability gain one-directional checking, or
two asymmetric information holders? This is answerable against the transcripts
of past desk↔peer sessions, of which the operator has many. It discriminates
cleanly: under the one-directional reading, peer→desk corrections should be
rare and desk→peer should dominate; under the asymmetric reading, both
directions should carry real weight. A second axis grades each correction's
BASIS — reading the artifact versus grading the other party's prose — where the
literature predicts artifact-reading dominates (arXiv:2606.09863: no judge
configuration over prose exceeds AUROC 0.65, across five models, five prompt
strategies, and a baseline given the full ground-truth spec).

> **MEASURED, SAME DAY. The question above was run and the study is at
> `docs/audits/2026-09-18-desk-peer-catch-study.md`** — 103 graded correction
> events, 9 sessions, 6 projects, 3 lanes, read-only over raw transcripts.
>
> **ANSWER: two asymmetric information holders.** The one-directional reading
> is refuted, and hardest in the direction it does not permit — the lane with
> the cleanest breakdown found cross-session catches at **8:1 PEER→DESK** (one
> desk→peer, one ambiguous); a second lane split 3:2. The desk is not
> predominantly the checker.
>
> **BASIS CONFIRMED THE PREDICTION:** of 25 cross-session catches, ~21 cite a
> concrete artifact read against ~4 resting on reasoning. The literature's
> judge ceiling reproduced from the other side, in this machine's own data.
>
> **A FINDING NOBODY WENT LOOKING FOR, and it is the one that changes what to
> build: a peer's own "self-correction" label is not evidence of who caught
> something.** Two independent cases where a desk praised its peer's
> self-correction — once as "the arc's best piece of self-correction" — where
> the transcript shows the catch was OPERATOR-triggered. A peer sees only what
> is reported to it, never the other session's private turns with the
> operator. So a desk systematically OVER-ATTRIBUTES self-correction to its
> peer, and the operator's trust calibration (lc-161) is built from exactly
> those reports.
>
> **SCOPE, stated because the counts invite over-reading:** the instrument
> reads INBOUND records only, so SELF and MECHANISM are under-counted BY
> CONSTRUCTION and only the CROSS row carries weight. All 63 SELF events are
> self-catches that were COMMUNICATED. And no control arm exists — this
> measures who catches, never whether desk/peer beats a single session.
>
> **The re-grading that moved the headline:** filing "a party's own dispatched
> lane caught it" as SELF hides cross-context catching, because a dispatched
> lane IS a separate context with its own information. Re-split, one lane's 34
> SELF became 12 lane-caught / 18 true-self / 4 can't-tell — near parity.

**Not answered by the incident that first suggested it.** The `args.pid`
inversion was offered as evidence that a more capable desk was wrong in the
deciding half — but both sessions were Opus (operator, 2026-09-18), so the tier
axis was held FIXED and that incident says nothing about it. Whether desk model
tier affects desk performance at all is a separate, unmeasured question, and
the note should not spend the pid incident on it.

## THE GROOVE — what this is all actually for (operator, 2026-09-18)

The operator's own framing, and it supersedes "answerable, not felt" as the
arc's statement of purpose. That phrase names a defect class; this names the
goal.

**A project finds a GROOVE.** wan2gp found one after a rough start; the Marvel
Rivals arc found one after the operator complained. In the groove, guidance,
rules, learnings and state are persisted AND get read at the right moments,
and they shape the work. **The problem is that the groove is currently earned
by attrition** — ten sessions of the operator being irritated into producing
it. It should be self-building, self-finding, self-refining.

**The thesis, in one line:** *make sure the judgment has the right inputs in
front of it at the moment it is exercised, and do not spend its attention on
self-policing. Trust the capability, feed it properly.*

That is why this is enablement and not more rules. We are NOT encoding
judgment — that is the patching approach, and it has a measured ceiling
(skill-craft: a strong model steered too tightly performs BELOW its own
default). For MEANING we rely on the model's capability, deliberately. The
environment's job is narrower and mechanical: put the right inputs in front
of it, and get out of the way.

### "Self-learning" means the ENVIRONMENT learns, never the model

Stated because the phrase invites the wrong reading. The weights are frozen
and identical in every session. What differs between session 1 and session 20
of wan2gp is what the REPO HOLDS. The learning is real; it is stored outside
the head.

Three parts, and only one is broken:

- **CAPTURE** — a lesson gets written when it is learned. **THE WEAK LINK.**
- **RETRIEVAL** — it gets read at the moment it matters. **THIS WAS GRADED
  "measured working" AND THAT GRADE IS WITHDRAWN.** The measurement — 13,735
  record queries across 230 sessions (2026-09-18; per-100-turn rates 4-13,
  85-97% of sessions querying at least once in the rich-persistence repos) —
  is real and is not in dispute. **What it measures is query VOLUME, and the
  claim it was used to support is that records get read AT THE MOMENT THEY
  MATTER. Those are different quantities, and a high query rate is fully
  consistent with failing at every moment that counted.** The metric cannot
  see the failure, which is this arc's own signature class applied to its own
  evidence: an instrument reporting clean over a question it never examined.
  **Measured the same day, four times, all after this line was written:** a
  structural fact re-derived across an afternoon while sitting in a tracked
  file; a design re-inventing a pattern proven on 4 of 22 kinds; a document
  this session wrote six hours earlier and did not reach for; and a laws-file
  paragraph that trained its readers for a month to discount the one alarm it
  was written to protect. **So retrieval is a WEAK LINK too, and the honest
  state is TWO weak links rather than one** — see the moments-of-application
  section below, which is where this was worked out and which contradicted
  this line until now. Retrieval's real measurement does not yet exist: it
  would have to ask whether the record that would have answered a question was
  read before the question was answered some other way, and nothing counts
  that.
- **REFINEMENT** — wrong or stale entries get corrected and retired. This is
  what lifecycle already IS: staleness and exit stages per kind.

**Why capture is the weak link, measured rather than assumed:** it depends on
someone NOTICING a lesson and choosing to write it. That is a remember-to
duty, and remember-to duties under-fire even while loaded — the corpus's
course-correction capture rule was built for exactly this moment and filled 2
of 308 entries. The step that must happen for learning to accumulate is the
one least likely to happen.

### What statiker and daneel already do, and what they do NOT do

**They capture IN-FLIGHT, and recording is a STEP rather than a reminder.**
daneel's verification map with its `[VERIFIED]` marks; statiker's recorded
decisions before implementation. The protocol does not ask anyone to remember
— it does not proceed until the record exists. That is the pit of success,
and it is why capture fires there and nowhere else. What they capture is rich
and judged: what was found, what was decided and why, what turned out to be a
DEAD END, what mechanism is now understood, what mistake not to repeat.

**What they do not do is outlive their own arc.** The record lives while the
protocol runs, then the arc ends. A naked session has no cycle at all, so
nothing captures, nothing accumulates, and session 11 re-derives what session
3 knew.

**So lifecycle's job is to be what they write INTO** — so the capture survives
the protocol, gets a home and a staleness rule, does not rot into a
confidently-wrong artifact, and is readable by the next session whether or
not it runs statiker, daneel, or nothing at all. That is the fluency: not a
smarter protocol, but the layer underneath that carries each arc's learnings
to the next without the operator ferrying them.

### DEAD ENDS are the category nobody captures, and the most valuable one

"We tried X, it fails because Y" is exactly what stops a future session
burning a day re-deriving it — and it is the first thing lost, because a dead
end FEELS like nothing happened. Everything a carrier holds is framed as
progress; a failed approach produces no commit, no closure, no artifact. It
is pure loss unless something deliberately writes it. No kind currently
claims it.

### The boundary, unchanged from everywhere else in this note

**The EVENT is computable; the MEANING is not.** "This guard fired 6 times
this week on legitimate work" is detectable. "Therefore the predicate is wrong
and here is the right one" is judgment. The mechanism captures the signal and
surfaces it; a mind reads it. Environment carries the FLOOR, intelligence
provides the CEILING — and the capture-by-construction slice already exists in
miniature: `firelog.py` records guard fires, and the judgment register records
fired / legitimate / overridden. The lever is widening what gets captured by
construction, not inventing a new mechanism.

## THE ORGANISING FRAME: THE PLAYER LOOP (operator, 2026-09-18)

**The operator's frame, and it replaces "self-administering" with something
testable.** Their first framing was a game's LOOP; their correction was the one
that matters — **not the engine's `input → update → render`, but the loop the
PLAYER runs, which includes judgment**:

> perceive state → form intent → **act** → get feedback → update model → repeat

**Judgment sits in "form intent", between perceiving and acting.** That is this
design's own sentence, reached from the other side and by someone else.

### What the frame dissolves: the tick

The engine reading raised a problem it could not answer — the tick. A game owns
its clock; this system does not, and a loop with an irregular timestep is where
drift lives. **The player loop has no clock. The world responds to the ACT.**

**So the tick is the VERB**, and that is the whole gap in one line:

> **A kind with a verb is in the loop. A kind with `writer: session` is a
> mechanic with no button** — it can only fire if somebody remembers it exists.

4 of 22 kinds have a button. 17 do not. That is not a missing scheduler; it is
seventeen mechanics the player cannot press, and it is why the write half was
never the thing that needed fixing.

### What the frame catches that nothing else did: FALSE FEEDBACK

**A player loop survives harsh feedback, delayed feedback, even unfair
feedback. It cannot survive FALSE feedback**, because every later decision is
made on a corrupted model.

That is why the robustness review's nine findings and the day's five incidents
all felt like one thing: **they were one thing.** A check reporting CLEAN over a
population it never examined is the game saying "you're fine" while the player
dies. And it explains the asymmetry this arc kept hitting without naming: a
check that OVER-fires is annoying and visible, a check that falsely PASSES is
lethal to learning — the same reason a game that reports a hit on a miss is
worse than one that is merely too strict.

**This is the strongest argument yet for spending on the three-answer contract
and the denominator rule**, and it is why they are not hygiene.

### The three nested loops, and where "ten sessions to find a groove" lives

Games run loops at different rates deliberately; so does this.

| loop | the player | rate | tightens when |
|---|---|---|---|
| inner | the session | minutes | checks fire, records write |
| session | pick up → narrow → close | hours | the record carries forward |
| meta | the project finds its groove | weeks | rules retire, prose leans out |

**GRINDING IS AN INNER LOOP THAT RUNS WHILE THE META LOOP NEVER ADVANCES** —
sessions completing, project not moving. That is the operator's "ten sessions
to find its groove", and it is a LOOP-COUPLING problem rather than a
productivity one: nothing in the inner loop feeds the outer.

**FIRST MEASURED INSTANCE OF THE COUPLING WORKING, 2026-09-18:** lc-172's
denominator rule shipped in the morning and then DEMANDED the row lc-170 needed
in the afternoon — the build desk's own words, *"the two items paid each other
back inside a day"*, and the row in question (`home_unresolvable`) is a
could-not-verify refusal that the pre-widening emit-site scan could not have
seen. One instance. Not a pattern, and recorded as one instance.

### The operator is a player too, on the outer loop

Check in, judge, redirect, leave. Their loop tightens as trust calibrates,
which is exactly what lc-161 books as decision absorption. **A good design makes
the inner loop work without the outer one, and makes the outer one meaningful
because of the inner.** The desk/peer arrangement is that shape already; its
failure mode is the operator being pulled back INTO the inner loop, which is
what the interruption count measures.

### The test this frame buys, replacing an untestable word

"Self-administering" could not be graded. This can:

1. **Does every mechanic have a button?** — every kind reaches a verb, or
   declares why it cannot (lc-168's trigger stage).
2. **Is the feedback true?** — no check reports clean over a population it did
   not examine (lc-172 and the robustness round's whole yield).
3. **Does the inner loop advance the outer one?** — a session's work retires
   prose, or sharpens a rule, or removes a class, rather than only closing
   items.

**Where the analogy is NOT to be pushed**, stated so a later reader does not
over-read it: a game's player acts under a fixed rule set they cannot edit,
while here the player rewrites the rules as part of playing — which is the meta
loop and has no clean game analogue. And skipping a frame is free in a game;
here the skipped tick IS the failure.

### WHAT THIS FRAME HAS ACTUALLY PRODUCED — graded, because an explanatory frame that predicts nothing feels profound

**The grading is here rather than in a journal because the risk is IN this
section:** a frame that explains everything after the fact is indistinguishable
from a true one while it is only ever applied backwards. Astrology has that
property. So the ledger, honestly:

**RESTATED, not discovered.** "The tick is the verb" did not find the gap —
lc-168 had already named the missing stage as the WHEN, measured at the schema
the same morning, and mechanism 2 was already the verb-writer pattern. The frame
arrived afterwards and said it better. Better words are worth something and are
not a discovery.

**GENUINELY NEW — one insight.** *A player loop survives harsh, delayed, even
unfair feedback, and cannot survive FALSE feedback.* That explains why nine
review findings and five incidents were one class, and it grounds the asymmetry
this arc kept using without justifying: over-firing is visible and annoying,
falsely passing corrupts every later decision. It is a mechanism, not a relabel,
and nothing else in this design produced it.

**GENUINELY NEW — one diagnosis.** Grinding as an inner loop running while the
meta loop never advances, which turns "ten sessions to find a groove" from a
complaint into a shape with a test.

**GENUINELY NEW — one MECHANISM, and exactly one: lc-193.** The loop's named
pathology is a SOFTLOCK, and asking what a softlock is HERE gives a state this
carrier can reach and cannot detect — the blocker EDGES are validated and the
GRAPH is never traversed, so a cycle waits forever while every check reports
clean. Nothing else in this design was looking for that, and it is lc-14's own
"permanent silent park" reached from a direction the check built for lc-14 does
not watch.

**MINED AND REJECTED, listed so the count is not inflated:** feedback LATENCY
(checks fire at commit rather than at the act) and AFFORDANCE (the seventeen
buttonless kinds are also invisible) both look like yields and both collapse
into lc-174 and lc-168. A frame is not made productive by booking restatements
of what was already booked.

**THE FALSIFIABLE PREDICTION, so this does not stay backward-looking:** an
ACT-anchored mechanism should outperform a timer- or memory-anchored one. The
close-time observer fires on a skill invocation; lc-174 fires at session start;
both are acts. **If a memory-anchored duty ever measurably outperforms an
act-anchored one at the same job, this frame is wrong** and the section is
rewritten rather than defended.

**Net: the frame earns its place as VOCABULARY and as one mechanism's parent.
It is not a design generator and must not be cited as one.** Its best property
is cheap: "game loop" recruits a large shared understanding for free on every
future read, where "self-administering" named nothing and could not be graded.

## THE PLAN — five mechanisms (operator-framed, 2026-09-18)

This supersedes the earlier "mechanize the answerable half" framing as the
arc's build plan. It is stated in the operator's own terms because their
framing replaced the desk's: the desk had this as BOOKKEEPING (record what
happened); the operator has it as KEEPING THE WORKING CONTEXT IN VIEW (record
what the next decision needs). Same mechanism, different reason — and the
reason decides what gets written.

**The idea in one line: the project keeps a system of record; sessions WRITE
to it as they work and READ from it because the system announces itself.**

Not rules telling a session what to do — FACTS it can use. A rule constrains
and has a measured ceiling; a fact informs. Some facts are judgments or
hypotheses, marked as such so they can be revised when evidence arrives, which
is what the `[VERIFIED]` / `[PENDING]` / `[INVALIDATED]` vocabulary is for. A
record that can be wrong and say so is the only kind safe to accumulate.

### 1. The system announces itself — MOSTLY BUILT

A session-start hook puts the project's state in front of the session: open
items, ledger tail, ready set, gate status. The session does not have to know
to go looking.

**This works and today is the evidence.** This desk knew lc-157 existed only
because the banner said so, and every booking went into the carrier instead of
into chat because the carrier announced itself first. **This is the half that
carries the AWARENESS — "this system exists and I am meant to use it" — which
the operator identifies as carrying the bulk.**

**AND THE HALF IT DOES NOT ANNOUNCE COST THIS SESSION ITS CENTRAL DERIVATION**
(operator question, 2026-09-18, at the close: *"i just wonder if we wasted time
along the axis that we are trying to fix today with better lifecycle"*).
MEASURED, at yesterday's HEAD rather than from recollection: `9a1eded`'s
`.claude/lifecycle.json` already declared 21 kinds split **4 verb-written / 16
`writer: session` / 1 producer** — the exact discriminator this session spent
the day arriving at and wrote up as §2b. One query against a file that was
already in the tree. The banner announces **STATE** — open items, ledger tail,
ready set, gate — and not **STRUCTURE**, so the declaration's own contents were
never in front of the session, and the session went looking only after the
begehung's second round forced the question (round 2's recorded class: *the
design re-invents what the repo already does*).

**The split is the design's own, turned on the session that wrote it.** The
DERIVATION half was shortenable: a structural fact sitting in a tracked file
was re-derived from reasoning. The DECISION half was not — the transition-table
mapping, judgment-between-the-seams, enable-over-constrain, the gate ordering,
the post-treatment baseline catch, and the category-exemption correction all
arrived first-hand from the operator, and no announcement could have supplied
them. This is not a session that ran long; it is a session whose derivable half
ran long, which is exactly the cost mechanism 1 exists to remove and the reason
its remaining gap is worth closing rather than declaring MOSTLY BUILT and
moving on.

**So the mechanism's scope widens, and this is the one amendment the question
earns:** the announcement covers what the repo HOLDS (the carriers' state) and
must also cover what the repo IS (the declaration's kinds, their stages, and
which stages are undeclared). Booked: lc-174.

**AND THE OPERATOR'S OWN READING OF IT MOVES THE ARC'S TARGET** (2026-09-18,
first-hand, on being told the above): *"i was picking up from yesterday on what
was persisted. i was deliberately leaving that old session open because of fear
of us not being able to pick up on the full knowledge properly — i think all got
persisted but maybe there was a gap in how we restarted from what was
persisted."*

**They were right, and the measurement says which half failed.** The persistence
was COMPLETE: the discriminator was in a tracked file at yesterday's HEAD,
committed, pushed, and readable. Nothing was lost on the WRITE side. What failed
was the READ — the restart did not put the persisted structure in front of the
session, so a complete record and an absent one produced the same session.

**This arc has been optimizing CAPTURE, and today's measured loss was
RETRIEVAL.** Every mechanism in this plan except the first is a write-side
mechanism: sessions maintain a narrowing, state-advancing acts write, dead ends
get a home, kinds declare their trigger. They are all correct and none of them
would have saved today, because today's fact was already written. **A record
that is written and never read is indistinguishable from one that was never
written — and it is worse, because it is trusted.**

That is also why the operator's instinct was to keep the old session OPEN rather
than to trust the carriers: a live context is a retrieval mechanism that works,
at the cost of paying the prefix forever. The carriers only become the cheaper
option once the restart reads them as reliably as the session remembered them,
which makes retrieval the arc's real second half rather than a detail of
mechanism 1. **Gate 1 already encodes this and it was not an accident** — the
operator's own wording is *"are things getting written AND READ as we expect
them to"*, and today answers: written yes, read no.

**AND THE THIRD INSTANCE KILLS THE SESSION-RESTART READING OF ALL THIS**
(operator, 2026-09-18, on being handed a mechanism design: *"didn't we not too
long ago find a solution for this class? I feel like we did"* — they had). Asked
to make a judgment-shaped duty computable, this desk decided the duty could only
be a printed readout, because detecting a course change is not computable. The
first half is true. The conclusion does not follow, and the answer was
`docs/required-slots-as-an-autonomy-lever.md` — **written the same morning, by
this same session, at this same operator's direction**, whose stated pattern is
exactly the escape: *do not ask an agent to decide well; require it to WRITE
something at the moment of deciding* — the slot's presence computable, the
fill's quality judgment.

**Three instances in one day, one class, and the third one settles its scope:**

| # | what was not retrieved | where it already sat |
|---|---|---|
| 1 | the verb-written / session-written discriminator | a tracked file, since yesterday |
| 2 | mechanism 2 is a pattern proven on 4 of 22 kinds | the repo's own declaration |
| 3 | required slots are the answer for uncomputable triggers | a doc this session wrote 6h earlier |

**So retrieval does not fail at session boundaries. It fails at MOMENTS OF
APPLICATION**, and the session boundary is merely the most visible of them. A
mechanism scoped to session start — lc-174 as booked — is necessary and NOT
sufficient: it would have caught instances 1 and 2 and would have sailed past
instance 3, where the document was authored inside the same context that then
failed to reach for it. The awkward part is the useful part: this session held
the document, wrote the document, and still answered from reasoning rather than
from the record, which means the failure is not ignorance of the carrier's
existence and cannot be fixed by announcing it harder.

**What the third instance implies about the mechanism, stated as a candidate
rather than a finding:** the retrieval seam is the moment a session declares a
thing UNCOMPUTABLE, UNDECIDABLE, or NOT MECHANIZABLE — which is a claim about
what solutions exist, made from memory, at the exact moment the stack's own
catalogue of solved classes would refute it. That moment is observable and
self-declarable in a way a general "should I check the record?" prompt is not.
Unprobed; recorded here rather than booked, because the mechanism bar is not yet
met and the honest next step is watching whether the moment recurs.

**THE MOMENT RECURRED — 2026-09-20, twice in one day, both specimens from
outside this repo, operator-pasted.** Specimen 1 (wan2gp, desk `58df31`;
transcript-pinned at this desk): a rewrite was held on an expensive probe
booked as its GATE (a loaded model, a render, timings) while the deciding
fact — do a 20B and a 12.9B model fit one card — was one query on an
instrument the session had already run twice for other questions. The
measurement arrived only on the operator's push (32,607 MiB total, 13:31,
three minutes before the session's own post-mortem — both turns read at the
transcript; the twice-run-never-asked count is RELAYED, that session's own
tally). The post-mortem names the mechanism in this paragraph's own terms:
framing the question as a TRADEOFF suspended the measure-it rule — "a
tradeoff has no obvious moment where a number is owed" — and booking the
expensive measurement hid the gap, because a named deferral reads as
diligence. "Tradeoff to weigh" is UNDECIDABLE-BY-COMPUTATION declared from
memory at the exact moment arithmetic answered. Specimen 2 (a non-technical
conversation, RELAYED whole): a killed hypothesis was replaced mid-reply by
an invented premise delivered in the verified register — the session's own
diagnosis, "keeping the theory running" — the same seam crossed in the
opposite direction: specimen 1 declared an answerable question unanswerable,
specimen 2 declared an unanswered one answered. In both, the catching
instrument was the operator; in both, the applicable rule was loaded and
inert — the adherence split replicated in two domains this arc never
touched, which is evidence for the DEMAND leg over the PRESENCE leg from
outside software. Status: the candidate moves from "watching whether the
moment recurs" to RECURRED. The mechanism bar is STILL unmet here — the
moment is self-declarable, not machine-observable, so no lifecycle trigger
fires on it — and the conduct half already has its corpus carrier (specimen
1's session recorded pre-formulated rule text for the dotfiles drain). What
precipitates in THIS repo is the computable slice specimen 1 exposes in the
carrier's own vocabulary: an `evidence` blocker whose clearing decides
nothing — the mirror of blocker_softlock — booked as lc-250.

### 2. Sessions maintain a NARROWING as they work — THE REAL GAP

**IT IS NOT A LOG. It is a live picture of what is still open and what has
been ruled out** (operator, 2026-09-18, correcting this desk's framing). The
desk had written this as "record what happened as you go", which produces an
accumulating pile that guides nothing. Daneel does not do that: hypotheses are
ELIMINATED, `[PENDING]` becomes `[VERIFIED]` or `[INVALIDATED]`, and the space
of live possibilities shrinks with every step.

**That is why it guides by existing.** Not because it stores things — a log
stores things and guides nothing — but because at any moment it says HERE IS
WHAT IS STILL OPEN AND HERE IS WHAT IS RULED OUT. A session reading it
inherits the narrowing instead of redoing it.

**And this is exactly how the ESTIMATE half resolves.** An estimate is not
wrong-then-right; it starts wide and narrows as evidence arrives. Where the
work lands, what counts as done, which facts hold — each begins as a
hypothesis and gets eliminated down to an answer. Daneel's structure IS the
mechanism by which mechanism 5's estimate half converges.

The format already encoded this and the desk had been describing it wrongly:
`NOW` is OVERWRITTEN (the current picture) while `ESTABLISHED` accumulates
(what has been settled). One slot is the narrowing, the other its residue.

**It also explains the peer's worked example precisely.** They did not fail to
LOG the previous day's tool. They failed to have its conclusion in the LIVE
PICTURE — so "does a backgrounding tool already exist?" was still open for
them when it had already been closed.

**What is NOT proven, and it is the plan's sharpest open claim:** that the
narrowing works ACROSS SESSIONS and OUTSIDE a protocol run. Statiker and
daneel maintain it inside their cycles and it dies with the arc. Whether a
project-level narrowing — carried by lifecycle, read at session start — does
the same job is what nobody has run.

Every record entry today is a deliberate act someone had to remember to make.
Measured by a peer the same day: nine hours, the visible-output record line
emitted ONCE. A carrier written from recollection drifts exactly like a stale
label.

Instead, **the act of doing the work also records it** — decisions with their
reasons, what was found, what was tried and ABANDONED, hypotheses marked as
hypotheses. Not everything: the parts a later decision would need.

**The operator's test: closing a session should have almost nothing left to
do.** If the close has work, something upstream deferred instead of writing.

**The worked example, from a peer the same day:** it built a tool that does
not background itself, having written one the day before that does; the
deployed helper already accepted the variant it was arming by hand. Every
piece of plumbing existed. Not a discipline failure — the existing tool was
not IN VIEW. A record removes the need for the read-the-existing-instances
rule to fire at all, because yesterday's instance is already in what the
session is reading.

### 2b. THE MISSING STAGE IS **WHEN** — and it is what self-administering means

**The operator's sharpening, 2026-09-18, and it names the gap exactly.**
Self-administering is not only THAT something gets written. It is the system
deciding WHERE, WHEN and WHAT — rather than a person deciding each time.
wan2gp is the counter-case that proves it: it has a large, working, heavily
READ knowledge layer, and it is ad-hoc on all three axes and triggered by the
operator. Knowledge without a system. It works, and it works because the
operator was the writer-of-last-resort throughout.

**A REGISTERED KIND ALREADY ANSWERS FOUR OF THE FIVE QUESTIONS AND NOT THE
FIFTH:**

| question | declared as | present? |
|---|---|---|
| WHAT | the kind itself | yes |
| WHERE | `home` | yes |
| WHO | `writer` | yes |
| FOR WHOM | `reader` | yes |
| HOW LONG | `staleness` / `exit` / `growth` | yes |
| **WHEN** | — | **NOWHERE** |

**And the WHEN is exactly what separates the two populations measured today.**
For the 4 verb-written kinds the trigger is IMPLICIT — the write fires because
the verb ran, so `item close` writing a closure needs nobody to remember. For
the 17 `writer: session` kinds there is no WHEN at all, which is precisely why
they need a person to decide it is time. The writer field was read this
morning as predicting DRIFT; the sharper reading is that it predicts
SELF-ADMINISTRATION, and drift is the symptom.

**THE MECHANISM IS ALREADY BUILT, ONE LAYER OVER.** `lanes.evaluate_trigger`
runs a `Trigger:` predicate and maps its exit to fire / quiet / broken, with a
mapping total on purpose so no code falls through into silence — and it is
already the SINGLE evaluator shared by lane triggers and by `item ready`'s
`evidence` blockers. So a seventh stage on the kind is not a new mechanism; it
is an existing, proven evaluator applied to a question the schema does not yet
ask.

**What that makes mechanism 2, restated:** not "make records better" and not
even "make acts write", but **move writes from the operator-prompted column
into the self-initiated one.** That has a number today — 4 of 22 — and a
target.

**And it corrects gate 1.** "Are things written and read" is not sufficient: a
record that fills only when the operator says *write that down* passes a naive
write-count while failing the actual test. Gate 1 must distinguish
SELF-INITIATED writes from PROMPTED ones, which is measurable in the same
transcripts — a write following an operator message on that topic is prompted;
one arising from the work itself is not. Otherwise we would measure wan2gp's
success and call it self-management.

### 2c. THE SHAPE IS THE CORPUS'S OWN TRANSITION TABLE, APPLIED TO KINDS

**Operator, 2026-09-18, and it names what all of this has been converging
on.** Accountability, triggers and tracking are not three mechanisms — they
are one shape that already exists in the corpus, prescribed for DESIGNS and
never applied to KINDS:

> arrow → verb → record written → check that proves it → OBSERVER: what
> notices the arrow's moment arriving

Map it onto a registered kind and the correspondence is exact: **accountability
is `writer`. Tracking is `home` plus `reader`. Lifetime is
`staleness`/`exit`/`growth`. And the TRIGGER is the OBSERVER — the thing that
notices the moment — which is precisely the stage a kind does not declare
(lc-168).**

**A kind with all seven carries itself forward:** the seam fires, a verb runs,
the write happens as a byproduct, a check proves it, and nobody remembered
anything. That is why the 4 verb-written kinds self-administer and the 17
`writer: session` kinds do not — the first group has observers, the second has
stages without arrows.

**AND JUDGMENT SITS BETWEEN THE SEAMS** (the operator's completion of the
shape, and the reason this is enablement rather than constraint). The
mechanized steps carry the transitions; the SPANS between them are where the
intelligence judges and carries decisions freely. Nothing in the table tells
the agent what to conclude — it tells the environment when to ask and what to
record. The corpus's own words for the same split: the environment carries the
FLOOR, the intelligence provides the CEILING.

**So the plan's five mechanisms are one mechanism at five seams**, and the
work is completing the table for kinds rather than inventing anything.

### 3. Watch for SURPRISES, not for guards firing

A guard firing is usually an old lesson working correctly — enforcement, not
learning. The signal is a check being SURPRISED: a test failing on a case
nobody planted, two independently-built measurements disagreeing, a control
that should have fired and did not, a runner reporting a pass-shaped number
over zero executions.

**Cheapest path: extend three instruments this stack already runs** — battery
green/red comparisons, independently-built-instrument divergence, and
red-first / positive-control discipline on new guards. No new observation
channel needed.

### 4. Lifecycle governs the SHAPE

Extend lifecycle's existing job — homes, staleness, exits, growth, fire
rate — to the record and to the global corpus. **Shape, never content:**
whether a rule is right, whether it is ethic or lens, stays the operator's.
(Booked: lc-158.)

### 5. RE-GROUND THE SCOPE AT PICKUP — the scoping answer

**"SCOPE" IS TWO DIFFERENT THINGS AND THE WORD HIDES IT** (operator,
2026-09-18, and this is the framing sentence for everything below):

- **the scope of WHAT WE WANT** — the requirement, the goal. This is a
  DECISION. It is made once and it holds.
- **the scope of THE WORK THAT NEEDS DOING** — where it lands, what counts as
  done, what facts it rests on. This is an ESTIMATE. It is a claim about a
  world that keeps moving.

The measurement below is that distinction, in numbers: the decision half is
amended 5% of the time, the estimate half 17-39%.

**AND THE CARRIER ALREADY SEPARATES THEM INTO DIFFERENT SLOTS, THEN GRADES
THEM UNDER ONE WORD.** `READY` means decision-complete and is applied equally
to `requirement` and to `write-set` / `done-criterion` / `evidence`. So an
ESTIMATE is being graded as a DECISION, and the surprise when it rots is
built in. That is the 55%, explained.

What does NOT follow: that entries should be booked vaguely and sorted out
later. 45% of completed items needed no amendment at all, the READY grade's
refusals were right every time they fired, and a scope that is permanently
provisional is not a scope. Both halves hold at once — book it
decision-complete anyway, AND re-ground the estimate half at pickup.

**The operator's opening question this session was how to make work
well-scoped and complete BEFORE building. Read with that distinction, the
answer is: the WANT half already is; the WORK half cannot be, and the record
is what keeps it current.**

Of 88 COMPLETED items, **55% had their scope amended between booking and
closing**, and the slot pattern says what moved:

| slot amended | share | what it means |
|---|---|---|
| evidence | 39% | the facts the scope rested on moved |
| done-criterion | 19% | what "done" means changed |
| write-set | 17% | where the work lands changed |
| **requirement** | **5%** | **what the work IS — almost never changes** |

The amend-reasons are explicit about the mechanism: *"the sweep population
grew while this entry stood"*, *"the booked path never existed"*, *"booked
against a premise this repo had already killed"*, *"the decision it named was
answered by the operator this afternoon"*.

**So scope does not fail at booking — it DECAYS after it.** People state what
they want accurately (requirement, 95% stable); what rots is the evidence
around it. A scope cannot be finished in advance because its facts keep
moving. lc-159's half 2 is this desk's own instance: booked as a cross-repo
schema migration, and by build time the premise was dead and the real work was
five times smaller.

**The mechanism: an item's EVIDENCE is re-read against the world at PICKUP,
not only written at booking.** Not the whole scope — the facts it rests on.
This is the cheapest item on the board because `lifecycle` already knows an
item's evidence slot and its write-set paths: checking that cited paths still
resolve and cited facts still hold is a verb, not an architecture. It is also
already proven by hand — lc-156 shipped correctly only because its executor
was told to grade against the format file at HEAD rather than the booked
criterion, and the booked text turned out to be the stale half.

**And this is why the scoping question and the recording question are ONE
question.** What decays is evidence; a system that records as it works is a
system whose evidence stays live. The 44% of OPEN items already carrying
amendments are scopes being kept current by hand, one retirement pass at a
time. Mechanism 2 makes that a byproduct instead of a chore.

### BEFORE BUILDING: the baseline, and what would KILL this

**THE NUMBERS BELOW ARE POST-TREATMENT, NOT A CLEAN BASELINE** (operator,
2026-09-18, correcting this desk). Every one was measured on repos ALREADY
GOVERNED by lifecycle — the 55% amendment rate comes from lifecycle's OWN
carrier, the most governed on the machine. It is not raw drift; it is the
RESIDUAL drift after the item carrier's discipline, and this desk recorded it
as the thing to improve on without saying so.

**The same confound runs through both of today's studies and was never
stratified.** Of the catch study's 9 sessions, 7 are from lifecycle-governed
repos (dotfiles, CachyOS-Setup, cache-fix, statiker, lifecycle) and 2 are
ungoverned (wan2gp, the B-Plan work) — checked by the presence of
`.claude/lifecycle.json`. The capture study's journal is dotfiles', also
governed. Both measured WHAT FAILS DESPITE GOVERNANCE, while the design was
written as though the baseline were ungoverned.

**Two consequences, and the second could sink a mechanism.** The labels are
wrong and are corrected here. And if the most governed carrier on the machine
still drifts at 55%, then either governance does not address drift or drift is
substantially irreducible — either way mechanism 5's expected yield is LOWER
than this note implied, and gate 2 must be read against that rather than
against zero.

**THE COMPARISON WAS RUN AND IT DOES NOT DISCRIMINATE.** Re-split of the
catch study by governance (presence of `.claude/lifecycle.json`, checked at
the artifact): governed 73 events / 2 escaped = 2.7%, ungoverned 30 events / 9
escaped = 30%, an 11x ratio; excluding lane 1, whose scanner was measurably
blind to the ESCAPED bucket, 8.0% against 30%, still 3.8x. A large apparent
signal that governance reduces operator-caught errors.

**It is not readable as one, because the two groups share no coordinate.**
GOVERNED here is software tooling plus system debugging; UNGOVERNED is video
generation and German planning-office work. Zero domain overlap — so "governed"
and "is a software repo" are the SAME VARIABLE in this sample. Worse, both
ungoverned domains are ones where the operator MUST evaluate personally
(subjective visual quality; real-world planning consequences), so a higher
operator-catch rate follows from the domain alone. Operator presence differs
too: 263 messages mean ungoverned against 162 governed.

**THAT LAST POINT DOES NOT EXEMPT THOSE DOMAINS FROM GOVERNANCE, and this desk
implied it did** (operator's correction, 2026-09-18). Two claims were run
together: that the comparison cannot isolate governance (true), and that
domains where the operator must evaluate therefore do not need a lifecycle
system (false, and smuggled in). The must-evaluate fact explains a higher
CATCH RATE; it says nothing about whether the repo's knowledge needs
governing. Subjective visual quality is one KIND of judgment that stays with
the operator — what was tried, what was decided, what failed and what is still
open is identical work in any domain.

**wan2gp refutes the exemption outright.** It is ungoverned by lifecycle and
carries a 608KB backlog, a 553-line CLAUDE.md and 57 docs, while running
thousands of turns at ~4 operator interjections per 100. It has the knowledge
layer and built it BY HAND. That is evidence the need is strongest where
governance is absent, not that the domain is exempt.

**Verdict: COULD NOT VERIFY, not a finding.** Two measurements only compare
where they share a coordinate, and these do not. Recorded because the desk has
now been wrong about this control arm TWICE in one session — first claiming
none existed without looking, then claiming one existed "one column over"
without checking whether it discriminated. The second error is the one this
corpus names: a comparison whose groups differ on the axis of interest AND on
three others certifies nothing about any of them.

Measured 2026-09-18 on this repo's carrier, and read as post-treatment:

- 55% of 88 COMPLETED items had their scope amended between booking and close
- by slot: evidence 39%, done-criterion 19%, write-set 17%, requirement 5%
- 44% of OPEN items already carry an amendment
- the declaration's writer field: 4 verb-written kinds, 17 `writer: session`
- 13,735 record queries across 230 sessions — a VOLUME figure. The gloss it
  carried, "retrieval already works", is WITHDRAWN: volume is not
  read-at-the-moment-it-mattered, and the same day measured four failures of
  the second while the first stayed true. See the three-parts section.
- one corpus rule measured at 0.27 -> 0.19 fires per 1000 turns across its own
  mint (a duty that did not fire)

If the build happens first and the measurement after, there is no honest
comparison and the verdict is an impression — which is the thing this whole
arc exists to replace.

**TWO GATES, IN ORDER, AND THE ORDER IS LOAD-BEARING** (operator,
2026-09-18). The kill conditions below are not a flat list — they are two
sequential gates, and grading the second before the first passes produces a
result that cannot be read.

**GATE 1 — MECHANICAL: are things getting written and read as expected?**
Countable, no judgment needed: writes occurring as work happens (per session,
per kind), and records actually being read (the retrieval measurement already
has a method — 13,735 queries over 230 sessions is the baseline). This gate
asks only whether the machinery RUNS.

**GATE 1'S WRITE HALF IS NOW MEASURED** —
`docs/audits/2026-09-18-self-initiated-vs-prompted-writes.md`, four lanes, same
day. Read it before grading anything here; three of its results bear directly
on this section.
**(a)** The rubric this design implied was WRONG. Splitting writes into
operator-prompted and self-initiated is the wrong cut in a desk/peer
architecture — being told by a PEER is still being told. The measured split is
four-way, and in the governed peer-rich population it runs operator 25.2% /
peer-content 45.0% / automated ping 10.6% / **unprompted 19.3%** (write grain;
14.8% at the episode grain). Peer-prompting is real causation, not
co-occurrence: 19 of 20 sampled episodes had the peer message naming the exact
artifact written.
**(b)** The unprompted rate TRACKS PEER DENSITY, NOT GOVERNANCE — dotfiles
(41% peer-dense) 18%, dispatch-guards (27%) 52%, cache-fix 54%. Governance is
not visibly moving this number. The comparison is confounded across many axes
at once and CANNOT grade governance; that is a limit, not a result.
**(c)** THE PRE-TREATMENT BASELINE THIS SECTION WANTS DOES NOT EXIST AND CANNOT
BE BUILT FROM TRANSCRIPTS. Only 3 of 1360 candidate writes in the pre-toolchain
repo invoke the toolchain at all, all inside its build window: adoption moved
the WORK to another repo's sessions rather than showing up as a before/after in
one place. The operator's correction that the 55% was measured on
already-governed sessions was right, and the honest consequence is that no
uncontaminated before-arm is available here. Any future before/after must be
designed PROSPECTIVELY, from a marker laid down now.
**What survives for this design, stated at its real width:** 75-83% of carrier
writes in governed repos happen with no operator message in the window. That is
the operator-attention claim, measured. **It is not the claim that the system
writes by itself**, and the two must not be swapped — which is this arc's own
paraphrase-drift class pointed at its own result.

**GATE 2 — EFFECT: does it alleviate the operator's problems?** Fewer
interruptions, less re-derivation, a shorter path to a project's groove.

**WHY THE ORDER CANNOT BE REVERSED, and it is this arc's own signature class:**
if gate 1 fails and gate 2 is measured anyway, a null result says nothing
about the design — it says the design was not running. A mechanism that never
fired and a mechanism that fired and did not help produce IDENTICAL evidence.
Grading effect over an unfired mechanism is the wrong answer shaped exactly
like the right one, one level up from where this arc found it.

**WHAT WOULD KILL THIS AT EACH GATE, named so the approach is falsifiable** (the NOW slot's
own discipline: if nothing could kill the current approach, that is the
finding):

- **drift rate unchanged** after verbs own more of the writing. Mechanism 2's
  central claim is that the writer field predicts drift; if session-written
  kinds keep drifting once a verb writes them, the correlation was not causal.
- **records written but never read.** Retrieval is measured working TODAY, but
  on records humans chose to write. A machine-written record nobody opens is a
  log, which is what mechanism 2 was corrected away from.
- **THE WORST CASE, and the one to watch hardest: records written, read, and
  the work still needing the operator at the same rate.** That would mean the
  bottleneck was never capture — that what the operator supplies is judgment
  and direction rather than knowledge — and the whole plan would be aimed at
  the wrong half. The catch study already hints at this: the dominant capture
  event is the operator ASKING A QUESTION, and no record answers a question
  nobody thought to ask.

**The cheapest live probe, costing nothing to set up because both populations
already exist:** some repos on this machine carry the session-start hook and
some do not. That is the hook/no-hook comparison for mechanism 1's central
claim, runnable now.

### What the plan does NOT solve, stated so it is not assumed

- **The unmechanizable half** (19 YES / 19 NO at event grain): taste, naming,
  scope-of-the-corpus judgments, and "this rule is correct and it is
  ceremony". That is the operator designing the system, not a gap.
- **DIRECTION DRIFT** — an arc where every round is correct work pointed
  slightly away from the question. Cost the most on 2026-09-18, in two
  separate arcs, and has NO mechanism. The GOAL-slot-unmoved-while-ESTABLISHED
  -fills shape is an unprobed guess.
  **THE GAP'S SHAPE MOVED, 2026-09-20 (operator, first-hand):** pressing a
  drifting session with "what do you think the goal is?" usually returns a
  CORRECT answer — their observation across sessions, including where the
  goal was only partly stated and had to be inferred. So the goal is
  articulable in-context while unapplied: the failure is the TRIGGER, not
  the knowledge, and the operator is currently the only trigger — their
  word for it, babysitting, which is the purpose doc's own failure mode
  (the operator pulled back into the inner loop). What that licenses is
  narrower than a drift DETECTOR (uncomputable, and the external survey
  found none): a mechanism need only FIRE the question at seams and demand
  the answer written — the required-slots pattern, the record's GOAL slot
  the natural home, an inferred goal written early so it costs the
  operator one confirmation instead of silent re-inference every turn.
  The confound to probe before believing it: the operator's ask carries a
  suspicion signal a scheduled ask lacks; the intrinsic-self-correction
  result (arXiv:2310.01798) predicts that difference matters, the
  operator's observation predicts it does not (they supply no content,
  only the trigger, and the correction still lands). Probe design:
  `docs/audits/2026-09-20-direction-drift-trigger-probe-design.md` — the
  attempt to BOOK the design was vetoed by the carrier's own cost test as
  do-it-now, and the veto was correct, so the design was written in the
  same session. Until the probe runs, this stays a candidate and the
  operator stays the mechanism.
- **Completeness as distinct from scope decay.** The 55% measures decay, never
  sufficiency. Whether a booked item was COMPLETE is unmeasured.
- **Trust calibration** (lc-161) and **whether desk/peer beats a single
  session** (no control arm exists).

### The one thing worth measuring next

Some repos on this machine have the session-start hook and some do not. **That
is a live natural experiment for mechanism 1's central claim** — does a record
that ANNOUNCES ITSELF change behaviour versus one sitting on disk? It is the
research scout's gap #1 (the unrun "record present but never referenced" arm)
in a form this stack can actually run.

## The payoff — mechanized levers let prose RETIRE (a leaner corpus)

Beyond catching more gaps, each lever has a second payoff that ties directly to
the north-star's EFFICIENCY half and to the operator's multi-session
corpus-improvement thread. The corpus already grades rules by FIRE RATE (the
maintenance doctrine's fire-rate review; the adherence split — a duty with a
VISIBLE OUTPUT fires, a REMEMBER-TO duty under-fires even while loaded, measured,
and re-measured tonight: 5 of 6 corrections against a rule loaded the whole time
and inert). A remember-to prose rule that under-fires is a RETIREMENT candidate
the moment a mechanism enforces its duty by construction (the pit-of-success:
compute or default what the duty asked, so the lazy path is the correct path).

So building a lever here does double work: it makes the guarantee mechanical AND
lets the prose it absorbs LEAVE the corpus. "Verify the verifiers" absorbs "read
what was done off the object, not memory"; the record lint absorbs the record's
prose conventions; each retirement is a paragraph the always-loaded corpus stops
re-billing every turn. That is dependability (mechanism over prose-hope) and
efficiency (less context per turn) moving together, not traded — a leaner corpus
that keeps its teeth.

**The retirement GATE, honestly:** a rule retires only when its duty is GENUINELY
mechanized — fires by construction, near-zero false fires — never merely because
a mechanism exists nearby, and never the judgment-remainder (which stays prose,
operator as backstop). The fire-rate review is that gate; the levers feed it
candidates. Net direction: the corpus gets SMALLER as the answerable half
precipitates into mechanism, and what remains is the judgment that genuinely
needs a mind.

## Next session — scout the external landscape IN PARALLEL (operator direction)

The operator's framing (2026-09-18): persistence + the right triggers + the
desk/peer session division may be three faces of ONE lever for improving LLM
work, and there is likely research that aligns with it and can sharpen or
correct the design. Dispatch research lane(s) to run in the BACKGROUND while the
design discussion proceeds in parallel — operator refinement: NOT blocking-first,
concurrent; the findings AUGMENT the design rather than gate it. Discovery
dispatch, judgment held at the desk. Search axes:

- **Persistent external state / memory for LLM agents** — scratchpads, external
  or working memory, state-offload — and its measured effect on reliability over
  long/multi-session horizons. (Our observation: the investigation record GUIDES
  by mere existence, keeping "where we are" in front of the model vs brittle
  memory.)
- **Trigger / seam-based self-verification** — checkpointing, verify-at-boundary,
  self-check at commit/step seams vs continuous judgment. "Answerable, not felt"
  as a possible known pattern; the silent-error / failure-shaped-like-success
  class and whether the literature names it.
- **Multi-agent role division** — planner/executor, critic/actor, overseer/worker
  (our desk/peer) — and WHY it helps: does it externalize judgment from execution
  and force explicit hand-offs that resist single-context drift? The operator
  notes the desk+peer combination "works best for reasons not fully figured out";
  candidate reading is that it is the persist-and-query lever at the
  session-STRUCTURE level (two parties, explicit state hand-off between them).

Return: aligned findings, terms of art, and any mechanism we have not thought of,
each graded against this note's class and lever. This scouting is what decides
whether the 5 ranked mechanisms above are the right cut or a reinvention.
