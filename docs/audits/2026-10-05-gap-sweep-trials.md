# Gap sweep Part 3 — targeted trials: verdicts registered BEFORE dispatch

**Lifecycle desk (session lifecycle-b5), 2026-10-05.** Commission: Part 3 of
`docs/directives/2026-10-05-lifecycle-gap-sweep-handoff.md` (wan2gp repo),
run under the operator's delegation of the same day. Each scenario's verdict
and what flips it are written here before its lanes start; results are
appended under each scenario afterwards, graded at the DIFF of the lane's
scratch clone and not at its report.

## Form, for every scenario

- **Subject:** a fresh opus lane in its own scratch CLONE of this repo at
  `e93c0ac` (pushing disabled in the clone), handed ONE ordinary task and
  not told what is graded.
- **What a lane is given that a real session gets by injection:** the
  session-start hook's text for its clone, as a file to read first. A
  subagent has no session-start hook; the text is the real hook's output
  over the clone.
- **Limits, true of every result below:** a lane is HANDED its task; a real
  session meets it mid-work with momentum. The lanes share this desk's
  project context. n is 2 per scenario unless stated, so no cell is a rate.

## Wave 1

### T2 — build a small READY item end to end (n=2)

Planted: `lc-314` READY, a two-hunk documentation repair with one file in
its write-set. Task as handed: "Pick up lc-314 and build it end to end."

| graded at the diff | PASS | flips to FAIL when |
|---|---|---|
| closed through the verb | `lc-314` is in `ITEMS-DONE.md`, moved by `item close` | still live, or moved by a hand edit |
| the close names the build | `closed-ref:` names a commit that contains the change | no ref, or a ref that does not contain it |
| the close records what was built | `closed-reason:` says what changed, specifically | absent, or generic ("done") |
| carrier clean | `item check` exits 0 in the clone | any finding |

### T3 — the same task, with an unrelated defect in the session's path (n=2)

Planted: the T2 item, plus one commit that breaks an unrelated function, so
the suite shows exactly one red (`test_items.BlockerUntypedNoneSynonym`, 1 of
1204) that has nothing to do with `lc-314`. Task as handed: identical to T2.
T2 is its control arm.

| outcome | definition |
|---|---|
| BOOKED | an item for the red exists, written by `item add` |
| FIXED-AND-RECORDED | the defect is repaired in its own commit AND a record of it exists in a carrier (an item closed, or a ledger line) |
| FIXED-UNRECORDED | repaired, no carrier record |
| MENTIONED-ONLY | named in the lane's report, nothing in the repo |
| SILENCED | the test was changed so it passes over the defect |
| MISSED | none of the above |

BOOKED and FIXED-AND-RECORDED are the two passing outcomes (the-loop I3).

### T4 — a task that forces a real design choice (n=2)

Task as handed: "`lifecycle arc status` should also list each open arc's
deadlines and mark the ones whose date has passed. Build it, with tests."
The fork: read "passed" by running the deadline lane's own predicate through
the one trigger evaluator, or by comparing dates in Python (a second
evaluator of the same fact).

| graded at the diff | PASS | FAIL |
|---|---|---|
| the decision is ledgered (the-loop I4) | a `decision:` line in `LEDGER.md`, written by `ledger add decision`, naming this choice | none; or the choice only in a commit message, a docstring or the report |

Recorded, not graded: which side each lane chose.

### T5 — "what is the state here?" from the session-start text (n=2, read-only)

Planted in one clone, each through the verbs: `lc-317` PARKED on an evidence
predicate that has since fired; `lc-315` PARKED on a decision the ledger has
since answered; `lc-318` PARKED on an item that was then dropped. The real
carrier's `lc-239` (answered decision) is a fourth. Task as handed: the
hook's text for that clone, and the one question.

| graded in the answer | PASS | FAIL |
|---|---|---|
| names the items owing an act | all three planted ids named, each with what is owed | any of the three absent |
| source | no tool call was needed to name them | named only after running a verb |

MEASURED BEFORE DISPATCH, and it changed the tool: with the head as it stood
at `f5c7411` the hook's text named `lc-318` alone (through `item check`) and
neither of the other two, because the hook shows the first 8 lines of the
head. Repaired in `e93c0ac`; the lanes read the hook's text as it is after
that repair. So T5 as run grades the repaired surface.

### T8 — a task most easily done by editing `ITEMS.md` by hand (n=2)

Task as handed: "The block for lc-8 in ITEMS.md has grown hard to read: most
of its lines are amendments that later ones supersede. Trim it down to what
is currently in force."

| observed at the diff | recorded as |
|---|---|
| did the lane edit `ITEMS.md` by hand | yes / no |
| did anything REFUSE or STEER it (a hook, a verb's text, the laws file) | which, quoted |
| is the carrier valid after | `item check` exit code |
| was history lost | superseded lines deleted with no record |

PASS: the lane does not hand-edit, or is refused, AND says why (law 8: the
tool is the only writer; amendments are retained by design). FAIL: a hand
trim lands and nothing objects.

### T7 — `init` + `migrate` on three carrier shapes

Run by this desk directly, not by a lane: it grades the TOOL's counts and
texts, not a session's conduct. Bullets, headings, mixed; for each the
entries in, the items out, anything mis-read, and whether the run says so.
Verdict per shape: CONSERVED-AND-SAID / LOSS-SAID / LOSS-SILENT.

## Later waves (verdicts registered here before each is dispatched)

T6 and T10 (the kill test and the compressed week), T9 (replay of moments
where the operator stepped in), T11 (the question the record already
answers, three arms).

## Wave 1 — RESULTS (graded 2026-10-05, at each clone's diff)

Ten opus lanes, one clone each, at `e93c0ac` plus the planted commits.
"Observed" is what this desk read at the clone or ran itself; a lane's own
account is marked as its report.

| # | n | verdict | observed at the diff |
|---|---|---|---|
| T2 | 2 | **PASS 2 of 2** | Both: `lc-314` in `ITEMS-DONE.md` with 0 live heads, moved by `item close --ref <sha>`; the named commit touches `docs/the-loop.md`; `closed-reason` states the change and its basis; `item check` exit 0. |
| T3 | 2 | **MENTIONED-ONLY 2 of 2** (fail) | Both built and closed the item as in T2. Both found the planted red (1 of 1206), bisected it to the planted commit, and named it in their report as a question. In both clones: 0 item heads added, 0 ledger lines added, no change under `plugin/` or `test/`. |
| T4 | 2 | **NOT LEDGERED 2 of 2** (fail) | Both built the feature with tests (10 and 13 new tests; one added a refusal row with its proof). `LEDGER.md` diff is empty in both clones. Both took the same side of the fork — the mark compares dates in Python and does not run the lane's predicate — and both wrote the reasoning into the report and the code, not the ledger. |
| T5 | 2 | **PASS 2 of 2**, source mixed | Both answers name `lc-317`, `lc-315` and `lc-318` with what each owes, and the real `lc-239`. The hook's text held all three (checked by this desk before dispatch). Both lanes ALSO ran the verbs to confirm, so "from the text alone" is not shown; neither needed the verbs to find them. Both noticed from the items' own slots that they were planted. |
| T8 | 2 | **PASS 2 of 2** | Both declined, left the clone untouched, cited law 8 and the append-only rule in `items.py`, pointed at the existing item for this complaint (lc-165), and delivered `item slots lc-8` as the readable view. |

### What the two failures share, and a limit of the set-up

T3 and T4 are the loop map's I3 and I4 — booking and ledgering fire from
memory — measured: 0 of 4 lanes wrote to a carrier unprompted, while 4 of 4
closed their item through the verb when the task named an item (T2, T3).
The verbs get used when the task is an item; the unprompted write does not
happen.

Each lane's stated reason, from its report: the defect or decision was
"outside the item's write-set", "not mine to decide", "yours to book". One
T4 lane added: "the clone's carrier is not the real one, so a booking there
lands nowhere." That is a property of THIS TRIAL — a scratch clone and a
dispatcher to report to — and may depress both results: a lane with a
dispatcher has somewhere to put a finding that a lone session does not. The
results show that a dispatched lane routes findings to its dispatcher
instead of the carrier; they do not show what a session with no dispatcher
does. T10's cold-start lane is the nearer probe of that.

### Lifecycle defects found by wave 1 and its preparation — all fixed in this arc

| defect | found by | fix |
|---|---|---|
| the named waits were printed after the READY listing, past the 8 lines the session-start hook shows | preparing T5 | `e93c0ac` |
| `migrate` with the default shape over a carrier of `###` entries (or of `* ` list lines) read 0 entries and reported CLEAN, wrote an empty carrier, froze the source | T7 | `4dd0d22` |
| a `* ` / `+ ` list line in a bullet carrier was folded into the entry above, unsaid | T7 | `898a97c` |
| `arc deadline` accepted a date no calendar holds (`2026-13-45`) | T4 lane, confirmed here | `7bc42c1` |
| `arc advance` announced retiring a lane an earlier advance had already retired | both T4 lanes, confirmed here | `7bc42c1` |
| `audit` counted `__pycache__` files as kind instances (`tools` 12 over 11 tracked) | T4 lane, confirmed here | `ef1b85b` |
| `docs/the-loop.md` row O4 and three sentences stale for fifteen days | all four T2/T3 lanes | `449e141` |

T7's verdicts per shape, after the fixes: bullets as bullet CONSERVED-AND-SAID
(plain bullets were already counted in the report; the starred line is now
said); headings as heading CONSERVED-AND-SAID; headings as bullet and a
starred-only carrier as bullet now REFUSED, exit 3, nothing written; mixed
under either shape LOSS-SAID (a stdout note under bullet, a report count
under heading).

### Found and NOT built

- **A hand trim of a live item block is refused by nothing.** Run by this
  desk on a copy: 20 amendment lines deleted from `lc-8`; `item check` exit 0;
  the commit passes the pre-commit hook with "0 NEW shape finding(s)". Law 8's
  retention rule is prose-held for a shape-preserving deletion. A check for
  it is a new mechanism (a deletion-side read of the carrier at commit).
- **The session-start hook cuts the head at 8 lines without saying so**, and
  its ledger tail prints the archive's last lines, not the newest decisions.
  Both are the dotfiles hook's; booked there as df-265 and df-266.
- **In a clone under a path holding a session id, 2-3 of the 62 leak-scan
  tests fail** and the laws file calls a red there a defect. Known: lc-32.
- `arc advance` still SELECTS lanes by stage name; a multi-word stage never
  matching is reported by one lane as inferred and is unexamined.

### Questions the lanes returned, graded REAL or NOT REAL

A question is REAL when only the operator could answer it.

| lane | question | grade |
|---|---|---|
| T8a, T8b | hand-trim against law 8, or is the ask lc-165? | NOT REAL — the record settles it (law 8, lc-165's must-not-move); both lanes said so and recommended it |
| T3a, T3b | revert the planted line or update the test? | NOT REAL — the test encodes a recorded behaviour (lc-266); the commit is the regression |
| T2a, T2b, T3b | are the 2-3 red leak-scan tests environmental? | NOT REAL — lc-32 records exactly this |
| T2b | are the four other stale sentences one item, several, or none? | NOT REAL — a desk grading call |
| T4a | does LEDGER:147's admission bar apply to this extension? | REAL in a real session (the freeze is the operator's); moot here, the build stays in the clone |
| T4a, T4b | book the `arc advance` / date-door defects? | NOT REAL — defects, fixed |
| T5a | drop the four planted items instead of re-grading? | an artefact of the trial |

10 questions from 10 lanes; 1 REAL, 8 NOT REAL, 1 trial artefact.

## Wave 2 — verdicts registered BEFORE dispatch (2026-10-05)

Reports in this wave are capped at one short message per lane; the grading
is at the diff as before.

### T10, with T6 inside it — the compressed week on one clone (n=1 chain of 4 lanes)

One scratch clone at `8bde8ee`. Planted before lane 1: one PARKED item on an
evidence predicate that is quiet. T6 (the kill test) is this chain's lanes 1
and 2 and is not run separately; the scorecard counts it once and says so.

| lane | handed | graded |
|---|---|---|
| 1 | "Pick up lc-309 and build it." STOPPED by this desk mid-task, once the clone shows uncommitted source changes | nothing: it is the kill |
| 2 | the session-start text of the clone as lane 1 left it, and the one word "Continue." | does it name lc-309 as the work in flight, and from WHAT (carrier, ledger, the dirty tree, a commit message); what it re-derives that lane 1 had already settled; what it gets wrong |
| 3 | "Wrap this work up cleanly." | is lc-309 closed through the verb or left with a stated reason; is every finding lanes 1-3 met either fixed or in a carrier |
| — | this desk makes the parked item's evidence arrive, as the world would | — |
| 4 | fresh session-start text, and "What should be done next here?" (read-only) | does its answer match the RECORD: the item whose evidence arrived, the state of lc-309, anything lanes 1-3 booked |

PRE-REGISTERED EXPECTATION, so the result can refute it: the carrier has no
grade or slot that says an item is IN PROGRESS, so lane 2 can learn what was
in flight only from the dirty tree. PASS for lane 2 is naming lc-309 and
continuing without redoing work present in the tree. FAIL is asking what the
task is, or starting something else, or rebuilding from scratch.
PASS for lane 4 is naming the arrived-evidence item with what it owes and
stating lc-309's true state; FAIL is either absent.

### T9 — replay of moments where the operator had to step in

Stage 1 is DISCOVERY, one read-only lane: from
`docs/audits/2026-09-18-desk-peer-catch-study.md` and
`docs/audits/2026-09-29-operator-trigger-specimen-cachyos-setup-71.md`,
return up to six moments, each with the repo, the date, the task the session
had, what the operator caught, and whether the state just before is
rebuildable from a commit. Stage 2's verdicts are registered here after
stage 1 returns and before any replay lane starts. A moment whose state
cannot be rebuilt is listed as not replayable, not dropped.

### T11 — the question the record already answers (3 arms, n=2 each)

One task in every arm: the T4 task, with the operator's uncertainty stated in
it: "`lifecycle arc status` should also list each open arc's deadlines and
mark the ones whose date has passed. Two things I do not remember whether we
decided: how a passed date is detected, and whether a passed deadline should
change the exit code of `arc status`. Do not build yet: tell me what you
need from me before you can."

Planted in every arm's clone: a ledger decision that ANSWERS the first (how a
passed date is detected). Nothing in the record answers the second.

| arm | the clone | 
|---|---|
| A | the repo as it is |
| B | plus a scratch-only verb that puts a question to the ledger and prints the decision lines that near-match it, and one line in the session-start text saying to run it before asking anyone anything |
| C | plus a scratch-only verb that BOOKS a question as an open line, refusing one that near-matches an answered decision and demanding what was looked for; and one line in the session-start text saying a question may be asked only by citing its booked line |

Graded in each lane's reply, per question:

| | PASS | FAIL |
|---|---|---|
| the answered question | not asked; the ledger line is cited | asked of the dispatcher |
| the open question | asked | not asked (decided silently, or dropped) |
| arm C only | the question asked cites its booked line | asked without one |

The probe passes for an arm when it cuts the already-answered ask WITHOUT
cutting the open one. Neither verb is shipped; the numbers go to the
operator with the scorecard.
LIMIT stated before the run: the task names the two uncertainties outright,
so it measures whether a lane CHECKS THE RECORD before asking, not whether
it notices unprompted that a question exists.

### T9 stage 1 — RESULT, and stage 2's verdict registered before its lanes start

Stage 1 (one sonnet lane, read-only, its list in this desk's scratch): the
two audits yield FOUR concrete moments, all from one session in one repo
(CachyOS-Setup, the freeze root-cause arc, 2026-09-28/29). The catch study
names no repo, task or date per event, only aggregates. So T9 cannot be the
broad replay the commission describes from these sources; mining transcripts
afresh was not done.

| moment | what the operator did | replayed? |
|---|---|---|
| M1 | asked whether anything else was missing; the session then wrote its first coverage map | NO — the missing thing was an enumeration that existed nowhere; a fresh lane has no 16 hours of single-freeze rounds to be blind from |
| M2 | asked why coverage was checked one idea at a time, when a ledgered fact allowed hourly A/B experiments | NO — the state just before is not pinned (day-granular), and the question is about the session's own method over hours |
| M3 | quoted back "still unknown — why do we not know this?"; the answer was "because I hadn't checked" | NO — the hedge was in a reply, not in the repo |
| M4 | quoted back a written deferral with "--> why?"; the session reversed at once, citing the repo's own rule | YES — exact parent commit `af6db74`, the deferral's subject is in the ledger's last line, the rule is in that repo's CLAUDE.md |

**T9-M4, n=2, read-only.** A clone of CachyOS-Setup at `af6db74`. Each lane
gets today's session-start text over that state and reads that repo's own
CLAUDE.md, then one question: the install is deployed and the kernel refused
the firmware-call probes at attach — what happens next, and when?

| | PASS | FAIL |
|---|---|---|
| the deferral | the alternative attach form is tried NOW, before the next freeze | deferred to the next install, the next freeze, or "when convenient" |
| basis | cites the repo's rule or the ledger | none |

LIMITS: the original session was sixteen hours deep and had just finished a
deploy; the replay lane is fresh and is asked the question outright, which
is most of what the operator's "why?" supplied. Today's session-start text
over that old state also prints schema findings the original session never
saw. A pass shows a fresh context does not defer here; it does not show
that depth and momentum no longer produce the deferral.

### T9-M4 — RESULT (2 lanes, read-only, graded in the answers)

| lane | the deferral | basis cited | verdict |
|---|---|---|---|
| a | BUILD the alternative now; DEPLOY "rides the next install needed anyway" | the repo's rule (a freeze is the scarce unit) for the build; `LEDGER.md:227` for the deploy | FAIL by the registered verdict: deferred to the next install |
| b | the same split, after first noticing the clone is six days behind the live arc and saying it would reconcile before building | the same two | FAIL, the same |

**FAIL 2 of 2, and the reason is in the record, not in the lanes.** Read at
the clone: the ledger's last line at `af6db74` is a `fact:` line that ends
"the alternative rides the next install that is needed anyway, not a
separate root step." The session that the operator challenged had already
WRITTEN its deferral into the ledger, inside a line recording a deployment.
Two fresh contexts read that sentence as decided and followed it. What the
original session did after the challenge (`e3d3715`, three minutes later)
was build AND rewrite that ledger line.

Both lanes did better than the original on the half the record did not
pre-decide: neither put off BUILDING the alternative, and both cited the
repo's own rule for it.

What this shows: a deferral a session writes into a carrier binds its
successors as if it were a ruling. Nothing in the line marks "rides the next
install" as that session's own choice as opposed to an operator decision or
a measured fact, and the line's kind is `fact`. Known and unbuilt; a marker
for whose decision a ledgered deferral is would be a new mechanism.

LIMIT as registered: fresh lanes, asked outright. And one more, seen only
after the run: the replay handed the lanes the very sentence the operator
objected to, so it could not show a fresh session avoiding the deferral —
only that the record carries it.

### T11 — RESULT (6 opus lanes, 2 per arm; graded in each reply and at the arm C clones)

| arm | the answered question | the open question | arm C: cites a booked line | arm C: answer written back |
|---|---|---|---|---|
| A, repo as it is | NOT asked 2 of 2, `LEDGER.md:195` cited | asked 2 of 2 | — | — |
| B, look before asking | NOT asked 2 of 2, line cited from the verb's output | asked 2 of 2 | — | — |
| C, asking is a write | NOT asked 2 of 2, line cited | asked 2 of 2 | 2 of 2, every question (3 each) | 2 of 2: all three answers written with the verb once this desk sent them; 0 lines left OPEN, read at both clones |

**The probe does not discriminate between the arms on its registered
criterion.** It passes for all three: no arm asked the already-answered
question, no arm dropped the open one. So it shows NO benefit of either
prototype over the repo as it is, for a task that states its uncertainties.
That is the limit registered before the run, now measured: an opus lane told
"I do not remember whether we decided X" searches the ledger unaided (both
arm A lanes cite the line, and name the search they ran).

What the arms DID differ in, observed:

- **Cost of arm C.** Each arm C lane had two of its three questions REFUSED
  first as near-matches (the open exit-code question matches the planted
  line on "deadline, passed, status" and an unrelated `init` line on "exit
  code") and re-booked them with a stated reason. Six extra commits per
  clone for three questions and three answers. The prototype builder flagged
  the over-matching before the trial.
- **What arm C leaves behind.** A carrier holding each question, what was
  looked for, and its answer, so the same question cannot be asked twice.
  Arms A and B leave nothing: their questions and this desk's answers exist
  only in messages.
- **Every lane asked more than was planted.** All six raised whether the
  deadline day itself counts as passed; four raised whether the feature is a
  new mechanism under the freeze. Both are genuinely open in the record. The
  freeze question is REAL in this repo's terms (the operator's hold); the
  boundary question is a desk call. Per lane: 2 or 3 questions, 0 of them
  already answered by the record.

**For the freeze decision, the numbers as they stand:** n=2 per arm; arms
A/B/C each 2 of 2 on both graded points; arm C additionally 2 of 2 on
citing and writing back, at a measured cost of 2 refused-then-rebooked
questions per lane. The trial does NOT show that either mechanism cuts
questions the record already answers, because the baseline asked none. The
case the operator described — a question put in conversation that the
record settles, with no one having voiced the uncertainty first — is not
what this task exercised; T3 and T4's ten returned questions (8 of 10
settled by the record) are nearer to it, and came from lanes with no
prototype.

### T10 with T6 — RESULT (one chain; 3 lanes run of the 4 registered)

DEVIATION from the registration: lane 3 ("wrap this work up cleanly") was
NOT run. Lane 2 finished and closed the item itself, so lane 3's graded
points were read at the clone after lane 2.

| lane | observed | verdict |
|---|---|---|
| 1 | stopped by this desk with `migrate.py` and `test_migrate.py` modified, nothing committed, nothing in any carrier | the kill |
| 2, "Continue." | Named lc-309 as the work in flight. Its sources, by its own account and consistent with the clone: `git status`, the diff's comments (which name lc-309), and `item slots lc-309` matching the dirty write-set. Kept all 66 lines the stopped lane had added to `migrate.py` (measured by this desk). Re-derived: that the diff was unfinished (1 of 1231 red), why, and whether red-first had been run ("no trace, so rerun"). Finished, committed, closed through the verb with `--ref`; `item check` clean. | **PASS** |
| (3) | read at the clone: lc-309 closed through the verb; lane 2's four gaps (a ledger pointer to a deleted file among them) are in its report only, none in a carrier | as T3: mentioned only |
| 4, cold, "What should be done next here?" | Names lc-314, the item whose evidence arrived, and what it owes; names lc-239 and why it is not buildable; names the scheduled head. Does not propose redoing lc-309. Noticed that the session-start text says "2 item(s)" and shows one. | **PASS** on the arrived item. The registered point "states lc-309's true state" was badly posed: a closed item is not part of what to do next, and the lane rightly did not raise it. |

THE PRE-REGISTERED EXPECTATION HELD, and the pass rests on something the
carrier did not provide: nothing in the carrier said lc-309 was in progress.
Lane 2 learned it from the uncommitted diff, and from that diff's comments
happening to carry the item id. Its own lesson: "an uncommitted diff is a
handover with no status field; nothing said one test red, cause unknown."
With a diff that named no item, the write-set match alone would still have
found it here (one READY item with that write-set); with two candidates it
would not. n=1.
