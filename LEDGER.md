# lifecycle — ledger
#
# On-disk ledger for this repo. From the schema wave on, the TOOL owns the
# region above the archive heading: one fixed-slot line per decision event
# (`superseded:` / `rejected:` / `dropped:` / `decision:`), written by
# `lifecycle ledger add` for the slots and by the SESSION for the reason
# prose. `lifecycle ledger check` grades it, and the gated readers —
# `ledger rejected --for <item>`, the intake join's rejected-line print —
# are what it exists for.
#
# The comment block you are reading is licensed by the schema wave (§3.8c):
# before it, the first non-blank line had to BE the version, so a carrier in
# a public repo could not say what it was for.
#
# **Consumer:** any session working in this repo — read before re-deriving
# something that may already be settled. Boundaries: work items go to
# `ITEMS.md` (via `lifecycle item add`), standing rules to `CLAUDE.md`,
# incidents and their lessons to `JOURNAL.md`, maintenance notes to
# `dev-notes/`.

schema: 2
decision: the sixth kind stage under R22: keep the key spelled `bound` or replace it → replace it with `growth`, closed to bounded-by-exit/compacted/unbounded-with-reason; `bound` IS the cap concept R22 withdrew and a key whose body has moved is a label that misleads (§3.0b invariant 2 already says growth control)
decision: where the laws SIZE and SCOPE are reported once the 60-line cap is withdrawn → in `lifecycle audit`, not `kind check`: `kind check` validates the DECLARATION, and a prose-content finding inside it left the verb unable to answer CLEAN over a healthy repo
decision: whether `item close` leaves the blocker on the moved body → no: it CLEARS it, so no blocker survives in the closure home; only a `decision` blocker is recorded as `blocker-moot:`, since item-id and evidence blockers are not left hanging by a close
decision: how the plugin declares the git hooks it ships, given `hooks` in plugin.json → under `git-hooks`: measured on this machine, `hooks` is Claude Code's harness hook map (ai-bureau's manifest is the live example), so a git hook declared there breaks the plugin at install time
decision: what a repo with NO legacy closure home passes to `migrate` → `--from-done NONE`, an explicit statement by the caller; an absent file stays COULD NOT VERIFY, because a stated absence and an unread file are different answers
decision: where the plugin's own pre-tool prose ledger lives now that the tool owns LEDGER.md → below an `## Archive (pre-migration)` heading, the same mechanism the carrier already uses; held verbatim, counted apart, and `ledger add` writes ABOVE it
decision: whether `producer:plugin-drift-scan` may be named as a reader before wave 3 → no: a `producer:` reference resolves against the producers this declaration's kinds name as writers, and naming one the machine has no home for is law 23's own case
decision: does init seed the declared carriers on a bare repo → Yes: init creates every carrier the declaration names, empty and schema-stamped, so no later verb assumes a file init never made. Ruled by the judgment desk at wave 2 under the operator's standing delegation; design text saying otherwise is amended (3.8b). Recorded wave 3 step 0, 2026-08-27.
superseded: lc-15 by lc-28 — write-set omitted the call site; lane C found it (2f interim, 2026-08-27)
decision: who builds lc-17 merge mode, after two lanes were briefed for it → B2 builds. Lane B was STOPPED (TaskStop) and is absent from the agent listing; its uncommitted work was saved to scratch and reverted; nothing of it is reused. B2 is the only writer in this copy. Dispatcher error, contained, no commit entered history. 2026-08-27.
decision: does the stated reason in lifecycle cbfaee6 hold: that lane opus-lifecycle-bundle's mailbox had failed → NO, refuted 2026-08-27 by the lane's own transcript: all four messages delivered in ONE batch at a turn boundary after its report. The commit and the stop stand on other grounds (uncommitted work in a shared tree); only the reason is withdrawn. Class: dispatch-guards 6822924.
decision: does the item BODY change (rewrite the path out of it) or does the foreign-path class scope change (corpus -> source) to honour the declaration → moot (closed by lc-35)
decision: does the 2026-08-26 line no remote, and none is to be created still bind → SUPERSEDED. The operator created the public remote 2026-08-27 (bar commit 70bc93c, .git/config 22:04:54, gh repo view PUBLIC), the very act that line reserved. Push authority is separate and open at the judgment desk; lifecycle commits stay unpushed until it lands (wave 5, C4)
decision: lc-64 close omitted --ref; where is its payload ref recorded → lc-64 payload 9e2debc, close 6f7660e; the close-ref was not given at close time and closed bodies are immutable, so it is recorded here (the close commit itself also names lc-64)
decision: re-confirm: drop cross-cutting reasoning, or give it a declared home → drop stands; cross-cutting reasoning that must persist is a JOURNAL incident cited by each law it justifies, no reference tier re-introduced (operator as-you-recommend 2026-08-28; design 3.3 amended)
decision: is merge-of-N-carriers a real path worth the dedup, or is --merge-twice out of scope → real path: --merge re-runs legitimately as new source entries appear (cf-328 intake-additions), so a second run must not double-book residue; build the dedup on residue identity (operator as-you-recommend 2026-08-28)
decision: the coordination mechanism SHAPE: typed cross-repo edge (recommended) vs a declared coordination kind vs both → typed cross-repo edge (blocked-by <repo>:<id>) plus the cross-repo detector home and roll-up as one coordination layer, not a separate kind: the dependency is an edge between existing items (operator as-you-recommend 2026-08-28, design 3.1 amended)
decision: re-confirm: drop cross-cutting reasoning, or give it a declared home → moot (closed by lc-69)

## Archive (pre-migration)

Everything below is this repo's ledger as it was written BEFORE the tool
owned this file: prose entries, one per bullet, in the corpus's on-disk-ledger
form. Held verbatim and not graded — it will never satisfy a fixed-slot shape
and was never meant to, and deleting it to make the parse clean would be the
exit that leaves no trace. `ledger check` prints how many lines it did not
read rather than reporting a clean parse over the part it did.

## Entries

- **2026-08-26 — repo born.** `git init -b main`, laid out to
  dispatch-guards' convention (root `.claude-plugin/marketplace.json`
  + `CLAUDE.md`/`LEDGER.md`/`BACKLOG.md`/`dev-notes/`/`tools/`;
  `plugin/` holding `.claude-plugin/plugin.json`, `cli/`, `skills/`).
  Basis: the wave-1 dispatch brief D-a, itself resting on
  carrier-rework-design-2026-08-26 §3.8. **No remote, and none is to
  be created** — publishing a new public repo is the operator's act.
- **2026-08-26 — the leak scan precedes the first commit.**
  `tools/absence-scan.mjs` and `test/absence-scan.test.mjs` are
  byte-identical copies of claude-code-cache-fix's (`cmp` silent on
  both), armed as `.git/hooks/pre-push` -> `tools/git-hooks/pre-push`
  before this repo's first commit, per design §3.3/§5. Rejected
  alternative: porting the 1,127-line node scanner to python to match
  the CLI. Rejected because it would re-derive a red-proven
  instrument for no requirement the design states; `lifecycle` shells
  out and reports its exit code, and a missing node runtime is
  COULD-NOT-VERIFY, never a pass.
- **2026-08-26 — two transitive dependencies came with the copy.**
  `tools/tmpdir.mjs` and `test/fixtures/cc-transcript-shape-snapshot.json`
  are imported by the bite file; without them it does not load, and a
  bite file that cannot execute is not a bite file. Both copied
  byte-identically, both `cmp`-silent.
- **2026-08-26 — FINDING, open: the design's named firing input for
  the "leak scan on the plugin repo" refusal row does not fire.**
  §3.9 names "a planted `/home/<user>/…` path in a template"; the
  scanner has no such class (its classes are `b64-run`,
  `nested-payload`, `live-timestamp`, `capture-uuid`, `raw-content`,
  `capture-key-prefix`). Measured: a planted absolute home path
  naming a SIBLING repo under the operator's dev tree (the literal is
  not reproduced here — this repo is built to be published and the
  path is exactly the class the scan exists to catch; the concrete
  string is in the desk's internal notes, and `git log -S` over this
  file's history resolves it for anyone who needs the original
  measurement) in a markdown file scans CLEAN, exit 0; the same
  planted line under the SOURCE-scope class shipped 2026-08-26 fires
  `foreign-path`, exit 2 — which is what closed this gap. A planted
  `s-`+8-hex token in
  the same file fires `capture-key-prefix`, exit 2. The row was
  red-proven with the second input; the first is reported to the
  judgment desk as a design-vs-instrument gap, since closing it means
  either a new scanner class or an amended row — both design
  decisions, not this repo's to take.
- **2026-08-26 — declaration schema decisions** (stage 2; the
  brief's D-h assigns the VALUES for claude-code-cache-fix, the key
  spellings are this schema's). `head-rule` is structured
  (`{"lead-goal": "mitigate"}`) rather than the prose sentence "a
  MITIGATE-goal item leads whenever one is complete", so the head
  picker can read it and the prose is its rendering rather than a
  second body. `exit` is an object (`action` + `recording-act`, plus
  an optional `detail`) so that "a registry row missing `exit`" and
  "an exit without its recording act" are both mechanically visible;
  the other five stages are strings with shape rules.
  `schema` is a required integer with a floor, mirroring `ITEMS.md`'s
  own version line — the Begehung's "the registry no reader,
  `ITEMS.md` no version" findings are the reason a declaration
  without a version is not acceptable here.
- **2026-08-26 — `lifecycle item check` exists because the shape
  check needed an entry point.** §3.9 names a "pre-commit shape
  check" over `ITEMS.md`; the brief's D-c verb list
  (`item add|ready|park|close|ratio`, `ledger`, `lane list`, `kind`,
  `migrate`, `--test`) gives it none. Surfaced to the desk as a gap;
  spelled `item check` here so stage 3 can deliver the check it owes.
- **2026-08-26 — `git check-ignore -v` does NOT answer "is this
  ignored".** Measured here after this repo's own pair test went red on
  its control. `-v` changes the EXIT SEMANTICS, not just the output:
  without it, 0 = ignored and 1 = not ignored; with it, 0 = "some
  pattern had an opinion", which a NEGATION also satisfies. One scratch
  repo, one invocation apart: without `-v`, a negated path → 1, a
  genuinely ignored sibling → 0, an untouched path → 1; with `-v`, the
  negated path → 0 and the ignored sibling → 0, indistinguishable. The
  first draft of `ignored_by_git` used `-v` and would have fired on
  every repo whose negation was correct. Second property, kept
  deliberately: `check-ignore` skips TRACKED paths (exit 1) unless
  `--no-index`, which is the right answer to the question actually
  asked — a tracked file reaches every clone whatever the ignore rules
  say. **Consequence for wave 1 stage 9:** the brief's verifier item 6
  expects `check-ignore -v .claude/lifecycle.json` to exit non-zero
  with no output after the negation lands. That holds only once the
  file is TRACKED. Run against the working tree BEFORE the commit it
  exits 0 and prints the negation line, which reads like a failure and
  is not one.
- **2026-08-26 — FINDING, open: cache-fix's declared laws file is 243
  lines against a cap of 60.** Measured (`wc -l CLAUDE.local.md`). So
  `kind check` on cache-fix's real declaration will fire
  `laws_over_cap` at stage 9. That is the checker working, not a
  defect: the decomposition that brings the file under cap is wave 2's
  (design §3.3, laws to the declared file under a 60-line cap).
  Recorded so the stage-9 desk does not read the red as a stage-9 bug.
- **2026-08-26 — DEVIATION: the plugin version moves during
  construction, against the brief's "no version bump anywhere".** The
  machine's global pre-commit blocks a plugin payload change without a
  version bump. Its premise is an installed copy that could go stale;
  for a plugin never released, with no remote, installed nowhere, that
  premise is false and the guard over-fires. Its repair (a declared
  exemption in the guard's own data) lives in the dotfiles repo, which
  this dispatch may not write. Rejected alternative: `--no-verify` —
  it disables EVERY lane in that hook rather than the one that fired,
  and trains the override habit that kills a guard. So: 0.1.0 birth,
  0.1.1 stage 2, 0.1.2 stage 3. Open for the desk: reset to 0.1.0 at
  release, or get the never-released case declared in the guard.
- **2026-08-26 — FIXED, shipped defect: `ignored_by_git` omitted
  `--no-index`, so `kind check` reported CLEAN over a TRACKED ignored
  declaration** — which is every declaration a real repo has once it
  is committed. Found by W1a in its own shipped code, confirmed at the
  source by the execution desk, fixed here. Measured before the fix,
  one repo, one path: PLANT (tracked, negation absent) exit 0 CLEAN,
  no findings; CONTROL (tracked, negation present) exit 0 CLEAN — the
  two INDISTINGUISHABLE, which is what makes it a defect rather than a
  gap. After: plant exit 2 `declaration_ignored`, control exit 0. The
  four `git check-ignore` arms: tracked+absent `--no-index`→0 / bare→1;
  untracked+absent `--no-index`→0; untracked+present `--no-index`→1 —
  so the flag closes the tracked case and leaves the existing row's
  pair intact. The docstring paragraph justifying the omission ("a
  tracked file reaches every clone whatever the ignore rules say") is
  DELETED rather than amended: it is true and answers a different
  question than the hazard, which is a declaration one `git rm
  --cached` away from vanishing silently. Correct-sounding prose left
  beside a corrected line is how the next reader restores the bug.
- **2026-08-26 — FINDING on the neighbouring line, fixed in the same
  commit: `ignore_pattern` needed `--no-index` too.** Probed rather
  than reasoned about, per the brief. Measured on a tracked, genuinely
  ignored path: `check-ignore -v` without the flag prints NOTHING and
  exits 1, while with it it prints `.gitignore:1:.claude/*`. So the
  moment the verdict call gained `--no-index`, the two calls were
  asking about different universes of paths and the newly-covered
  tracked finding would have carried "(pattern could not be resolved)"
  in place of the line that caused it. The `-v` exit-semantics hazard
  does not reach this call: it reads STDOUT only, never the exit code,
  and runs only after the verdict is already True.
- **2026-08-26 — the roster's row→finding-row mapping is DECLARED, not
  derived.** `Row.finding_row` (default None = same as `ident`) replaces
  `row.ident.split("_missing_")[0]` in `test_refusals.py`. Two roster
  rows now prove two firing inputs of ONE refusal
  (`declaration_ignored`, tracked and untracked), which the string
  surgery could not express. The derivation was also unsound in the
  general case: a split on a magic substring silently returns the whole
  ident for every ident that does not contain it, which reads as "no
  mapping needed" whether or not one is. The assertion also tightened
  from a prefix match (`[name`) to the full token (`[name]`).
- **2026-08-26 — DEVIATION: stages 4, 5 and 6 land in ONE commit, not
  three.** The brief's commit plan says one per stage; D-d's stage
  ORDER cannot be honoured as a commit order because stage 4 depends on
  both later stages. §3.2's intake join must print matching `rejected:`
  ledger lines (stage 6's reader) and its `supersede` disposition must
  move a body to the done home (stage 5's move). Reconstructing three
  commits would mean committing two states that fail their own
  verifier, in an order the work never had. Reported to the desk as an
  ordering defect in D-d rather than resolved here.
- **2026-08-26 — the join is TWO-PHASE because a CLI has no dialogue.**
  §3.2 says "the caller answers merge-into / supersede / new". An add
  that finds candidates and carries no `--join` REFUSES (exit 2) and
  prints them with their `rejected:` lines; the caller re-runs with the
  answer. Rejected alternative: write first and report candidates
  afterwards — that is an insert with a report attached, and the whole
  point of §3.2 is that the question precedes the write.
- **2026-08-26 — the join's matching rule, and why the two halves
  differ.** Write-set: EXACT equality over comma-separated normalized
  entries, `NONE` and `UNKNOWN` never matching (§3.2 states UNKNOWN;
  NONE is the same argument one level over — two items realizing
  nowhere are not thereby related). Deliberately not substring or
  prefix matching: `tools/x.py` and `tools/x.py.bak` share a prefix and
  are different write-sets, and a substring test is a prefix match in
  an equality's costume. Requirement: >= 2 shared tokens
  (`MATCH_MIN_TOKENS`), token = a >=4-char word minus a short stopword
  list. One token would match nearly every pair in a repo whose
  vocabulary is its own domain, and a join listing forty candidates is
  one nobody reads — the over-firing guard that trains the reflex to
  skip it.
- **2026-08-26 — the cost test needs `--hunks` and says so rather than
  clearing.** The tool can count the write-set's files; it cannot see
  hunks, so the caller states the count. A one-path write-set with no
  `--hunks` is COULD NOT VERIFY (exit 3), never a pass: a cost test
  that silently cleared every add it could not evaluate would clear
  exactly the adds worth vetoing. Veto = one path + one hunk + a
  non-operator source. `--source operator` skips the VETO and never the
  join (§3.2), because whether a thing is already booked is a question
  about the carrier and authority does not answer it.
- **2026-08-26 — `--absence` is required for EVERY `new`, candidates or
  not.** §3.2 puts the named absence on `new` itself, not on the
  contested case; the join only decides whether `new` is the right
  disposition. Rejected alternative: require it only when candidates
  exist — that would make the uncontested add, which is most adds, the
  one path with no cost question at all.
- **2026-08-26 — `merge-into` writes NOTHING to the carrier.** That is
  what makes a detector safe to run twice (§3.2's own reason for the
  disposition): the second sighting of one problem is the same problem,
  and any carrier write would make it two. The event is recorded in the
  fire log (`detail=merge-into <id>`) — an id, never a body, so the
  fire log's no-payload rule holds.
- **2026-08-26 — the move's COMMIT belongs to the caller, not to
  `move_to_done`.** §3.1's "append, delete, commit" is three steps, and
  the third one's FILE SET depends on the act: a plain close commits
  two files, a drop and a supersede commit three (the ledger line).
  Committing the pair inside the move would leave the ledger line
  recording a move that the same commit did not contain. Commits are by
  PATHSPEC — the index is shared with whatever else runs in the work
  tree, so `git add` then commit would carry a co-writer's staged paths
  out under this message.
- **2026-08-26 — FINDING, fixed: the conservation identity told the
  LOSS story over the RECOVERABLE case.** One message for both signs of
  the delta. Found by the interrupted-move test, not by review: the
  crash window leaves two copies, so `actual − expected` is +1, and the
  message read "a body left the carrier by a path that is not a
  closure — a hand deletion". A reader following it would hunt for a
  deletion that never happened, next to a DUPLICATE line saying the
  opposite. Now two rows: `conservation_short` (delta < 0, a real loss)
  and `conservation_surplus` (delta > 0, ordinarily an interrupted
  close, recoverable, cross-referencing the duplicate line).
  **`conservation_surplus` is NOT a §3.9 row** — the table names only
  "conservation short". Surfaced to the desk.
- **2026-08-26 — FINDING about the INSTRUMENT: comparing exit codes
  alone does not discriminate between two refusals.** `tools/prove-rows.py`
  first compared each row's plant by exit code. It reported
  `parked_without_typed_blocker` unproven: disabling `item park`'s own
  typed-blocker guard left the code at 2, because the shared
  `_check_blocker` catches the same input under a DIFFERENT row's name.
  Every finding in this system is a 2, so a code comparison separates
  something-happened from nothing-happened when the question is WHICH
  refusal fired. The verdict signature is now `code` + whether the
  row's own name appears in its output, and the row proves cleanly
  (`2/named -> 2/unnamed`).
- **2026-08-26 — `item ready` answers COULD NOT VERIFY on an `evidence`
  blocker, deliberately.** §3.1 says an evidence predicate is
  "evaluated like a trigger", and trigger evaluation plus its policy is
  §3.3/§3.4 — `lane list`, stage 7, which is W1c's. Building a second
  evaluator here would put two bodies behind one contract and they
  would disagree about the `>=2` BROKEN case first. So the blocker's
  state is reported as unknown, which is not the same as still blocked.
  Open for W1c: `item ready` should call stage 7's evaluator once it
  exists.
- **2026-08-26 — `item ratio` has no stage in D-d.** W1a's
  `NOT_YET_BUILT` mapped it to stage 5, but D-d's stage 5 is
  `item ready|park|close` and the W1b brief's scope repeats that list
  without ratio. Left unbuilt rather than given a stage this desk did
  not assign; the refusal message now says so instead of naming a stage
  that would have been contradicted the moment stage 5 shipped.
- **2026-08-26 — FINDING: `foreign_origin_item` was in NEITHER the row
  list nor PROSE_REST before stage 4.** §3.9 names it ("public repo,
  foreign-origin item"), and the roster's whole contract is that a row
  it cannot fire is LABELLED. A row in neither list is the one state
  the two lists exist to make impossible. Now an executable row.
- **2026-08-26 — the declaration names the closure home TWICE and the
  disagreement is a finding.** Top-level `closure-home` and the `done
  bodies` kind's `home` are two spellings of one fact. Resolution runs
  through `closure-home`; a `done bodies` home that differs is
  `closure_home_split`, refused rather than tie-broken. A reader
  resolves through whichever it happens to open, and the two diverge
  from the moment they disagree. Also not a §3.9 row — surfaced.
- **2026-08-26 — `item check` now answers for the whole carrier
  SYSTEM, so its answer can be COULD NOT VERIFY where it was CLEAN.**
  It runs the single-file shape check, then the cross-home duplicate
  check, then conservation. A repo whose done home is absent now gets
  exit 3 rather than 0 — correct under the three-answer rule (an unread
  done home contributes 0, and 0 is a number shaped like a pass), but
  it is a behaviour change to a verb stage 3 shipped. Stage 3's own
  unit tests are unaffected: they call `items.check_file` directly.
- **2026-08-26 — `lane list` reads a roster FILE under XDG config, one
  repo path per line.** `$XDG_CONFIG_HOME/lifecycle/repos`, default
  `~/.config/lifecycle/repos`; `#` comments and blanks ignored. §3.3
  names the path and not the format, so the format is this decision.
  Rejected alternative: a directory of per-repo files — it makes the
  roster's ORDER unstated and the "roster count" figure the design asks
  for becomes a listing rather than a read. Not under `~/.claude/`, for
  the fire log's reason. **Nothing creates this file in wave 1**: it is
  outside every write boundary this dispatch was given, so on this
  machine `lane list` answers `roster_absent` today — correctly, and it
  is a real gap for the desk rather than a defect.
- **2026-08-26 — a lane's `Trigger:` is parsed; the other three parts are
  reported by PRESENCE.** §3.3 gives a lane four parsed parts. The router
  needs one of them, and `Decides:`/the decision table/`Ends:` are wave
  2's along with the one-screen cap. The run says so in its own output
  rather than implying it read the whole lane — an assurance wider than
  its predicate is what this arc keeps finding.
- **2026-08-26 — ONE trigger evaluator, and the blocker mapping is not the
  identity** (W1b's open item, closed). `item ready`'s `evidence` blocker
  calls `lanes.evaluate_trigger`, the same function `lane list` calls. A
  trigger FIRES when its condition holds, and for a BLOCKER the condition
  holding means the evidence ARRIVED — so 0 is UNBLOCKED, 1 is the
  machine's court, and >=2 is a FINDING rather than a wait. Folding BROKEN
  into "still blocked" would leave the item waiting forever while the
  board showed ordinary waiting; the summary line therefore says "its
  blocker is BROKEN — not schedulable, and NOT waiting either".
- **2026-08-26 — the emit-site coverage check found SIX refusals the code
  was already emitting under no registered row** (assigned item B).
  `unknown_item`, `unknown_source`, `new_without_typed_blocker`,
  `move_uncommitted`, `ledger_shape`, `unregistered_kind` — each had no
  plant, no control and no line in §3.9's snapshot, so the roster's green
  said nothing about them. All six are executable rows now. The check
  derives its sites from the SOURCE (a literal bracketed row name,
  `Result.add("…")`, `problems.append(("…"))`) rather than from a list,
  so a site added tomorrow is found without anyone updating anything, and
  it names its own limit in its output: it cannot catch a refusal the
  PROSE requires and the code LACKS.
- **2026-08-26 — the coverage scan read its OWN documentation as data.**
  Its first run reported a row called `name`, from the three doc-comment
  lines describing the patterns it matches. Repaired by rewording the
  comments, NOT by exempting the file: an exemption would have blinded
  the scan to `emit_site_unregistered`, the one finding this module
  really emits.
- **2026-08-26 — `migration_reconciliation` was REMOVED rather than
  registered.** Every entry is either written or reported unclassified by
  construction — the two sets partition the read entries — so no INPUT
  falsifies the check. A predicate no input can falsify is unprovable
  rather than unproven, and registering it would have put a row in the
  roster that can never go red. The arithmetic is still checked; its
  answer is COULD NOT VERIFY on the run's own counts, which carries no
  row ident at all.
- **2026-08-26 — an `item add` missing a slot ENTIRELY never reaches
  `new_without_typed_blocker`.** `slot_value_problem` refuses the empty
  slot first and the run exits under `item_shape`, so the only input that
  reaches the typed-blocker refusal is `--write-set UNKNOWN` — the
  migration's own marker, present and non-empty and not filled. Found by
  that row's CONTROL going red, which is what a control is for.
- **2026-08-26 — prove-rows' "exactly one row changed" widened to "every
  changed row proves the SAME refusal".** Forced by `declaration_ignored`
  and `declaration_ignored_tracked`: two roster rows, one refusal, one
  decision site — so the honest mutation darkens both and the old
  assertion could not tell it from a careless one. The family is DERIVED
  from the roster's `finding_row` mapping, never hand-listed; for a row
  with no sibling the assertion is unchanged. Measured: of 41 mutations,
  exactly one exercises the widening.
- **2026-08-26 — CLOSED (backlog entry, was READY): `tools/prove-rows.py`
  covers 41 of 41 rows.** Was 16 of 28. The 12
  stage 1-3 rows assigned as item C, plus the 13 rows stages 7-9 added.
  Each mutation folds one VERDICT into another rather than removing
  machinery; two needed a non-obvious shape and both are recorded at
  their entries (`declaration_absent` and `laws_absent_could_not_verify`,
  where deleting the branch lets an exception produce the SAME
  could-not-verify and the row would not move).
- **2026-08-26 — `item close` RECORDS a moot decision blocker and does not
  refuse** (assigned item E). Closing is the desk's act and a guard there
  would fire on legitimate work — the ordinary case is exactly this: the
  question stopped mattering because the item shipped. So the fact is
  recorded in both places a later reader looks: `blocker-moot: <question>`
  on the moved body, and a `decision: <question> → moot (closed by <id>)`
  ledger line. Only a `decision` blocker qualifies; an item-id blocker
  resolves on its target's DONE and an evidence one is re-evaluated each
  pass, so neither is left hanging by a close. Where the question carries
  a ledger separator the body annotation still lands and the ledger half
  is COULD NOT VERIFY — never an ambiguous line, and never a refused
  close.
- **2026-08-26 — KNOWN GAP: the done home's blocks are never
  shape-checked**, so `blocker-moot:` and the pre-existing
  `superseded-by:` are UNKNOWN SLOTS that nothing reports. `item check`
  runs `check_file` over the LIVE carrier only; the done home is parsed
  for conservation and duplicates, whose callers ignore `parsed.problems`.
  Surfaced to the desk rather than repaired here: either the annotations
  become real slots or the done home gets its own shape check with them
  exempted, and both are design decisions.
- **2026-08-26 — the migration CUTS the `## Grades` section, and this was
  found by running it.** §4 row 1 says so ("`## Grades` prose
  declarations … CUT — the tool owns the vocabulary"), and the first real
  run over claude-code-cache-fix migrated that section's two bullets —
  which DESCRIBE the old grade words — as items `cf-1` and `cf-2`. The
  cut is data (`CUT_SECTIONS`) and the report PRINTS what was cut: a cut
  nobody prints is indistinguishable from a section that held nothing.
- **2026-08-26 — the migration's entry rule is "a top-level bullet that is
  BOLD or led by a grade-shaped word".** Not "starts with `- **`": the
  real carrier holds two entries written as plain `- DONE …` bullets,
  which that rule would have dropped in silence. The grade word is
  matched with a trailing guard against a following lowercase letter, so
  `OPEN-BOOKED` does not collapse onto `OPEN` and `MITIGATE-goal` is not
  a grade word at all — a prefix match in an equality's costume would
  silently give an entry another word's rule. A bullet that is neither is
  PROSE and is listed as non-entry content; the report carries the
  identity `bullets = entries + prose + cut`, so a bullet the reader did
  not see leaves a gap in a sum rather than no trace.
- **2026-08-26 — §4 row 1's PARKED branch is UNREACHABLE over
  claude-code-cache-fix's carrier.** "PARKED→PARKED with a typed blocker
  or NEW" turns on a typed blocker; the old carrier has no blocker slot
  and the design states no rule for deriving one from a body. So all 58
  PARKED entries take the NEW branch and the parked-ness — which court
  the item waits in — does not cross. That is the largest single
  information loss in the migration. Extracting a blocker from prose
  would be a classification rule invented at this tier, which D-f
  forbids; surfaced to the desk with the rule text recorded per entry.
- **2026-08-26 — `goal`, `done-criterion` and `evidence` have no
  migration rule.** §4 row 1 names UNKNOWN for the write-set alone, and a
  slot cannot be empty. `goal` and `done-criterion` are written UNKNOWN
  at the same width the design gives the write-set; `evidence` carries
  the source line range, which is the evidence a migrated entry actually
  has. Reported as a design gap, not closed here.
- **2026-08-26 — `LEDGER.md` cannot carry a prose header.** The ledger
  parser requires the FIRST non-blank line to be `schema: <n>`, and any
  other line is either a shape finding (before the schema line) or an
  unreadable line (after it). So a repo's ledger is exactly `schema: 1`
  until its first decision — a carrier in a public repo that cannot
  explain itself. Surfaced; the fix is a comment-line rule in the parser
  and that is a design decision.
- **2026-08-26 — the fire log lives under XDG state, never
  `~/.claude/`.** `$XDG_STATE_HOME/lifecycle/fire.jsonl` (default
  `~/.local/state/lifecycle/fire.jsonl`). Basis: on this machine
  `~/.claude/` is protected by path shape, so tool data kept there
  costs a permission dialog on every read and write — for the
  operator and for every dispatched agent — and one such prompt
  denied mid-task has already lost a session's work.

- 2026-08-26 — **G10, in the W1c lane's words, landed by the integrating desk
  because its write grant had ended.** A row whose firing input does not exist
  cannot be red-proven. Design §3.9's replacement row "a kind grew without an
  exit event" names `lifecycle retire` as its firing input; that verb is in no
  D-c list and no D-d stage. Registering it today would put an UNPROVABLE row
  in the roster — not an unproven one — the same shape the lane removed
  `migration_reconciliation` for two hours earlier in the same dispatch. Two
  instances of one class inside one lane, and the strongest single argument
  for giving the no-caps correction its own brief rather than folding it in.
  Basis: the lane's addendum; JOURNAL J16.

- 2026-08-26 — **G11, same provenance.** `bound` → the growth-control
  vocabulary (`bounded-by-exit` / `compacted` / `unbounded-with-reason`) is a
  SCHEMA change with every declaration as a dependent, landing on a dispatch
  that had already committed a declaration under the old stage. The migration
  would have to run over both the schema and the artifact it produced. A wave
  boundary, not a patch. Cheapest NOW rather than later: exactly one
  declaration exists today (claude-code-cache-fix's dry-run one), and two exist
  tomorrow. Basis: the lane's addendum.
- **2026-08-28 — wave 5, item G: the shared grammar module, and the
  silent-corruption defect it uncovered.** Lane `opus-lc40-grammar`
  (opus; peer desk `dotfiles-a7` dispatching, grading and integrating;
  judgment desk `claude-code-cache-fix-14`). Four commits, booked here
  because the pre-push gate rightly blocks a marked subagent commit
  whose sha sits in no record carrier: `0c11b7f` bump 0.3.20 -> 0.3.21
  alone and FIRST (the bump-first plan, measured this wave in a scratch
  clone: payload without bump REFUSED, payload+bump in one commit
  ACCEPTED, and with the bump committed-but-unpushed a second payload
  commit ACCEPTED, because the guard compares against origin and not
  against the parent) · `a146b62` `grammar.py` NEW plus six modules,
  +301/-65 · `ec1ab60` `test_verbs.py` +134 · `c03399e` the third id
  spelling the lane's own first sweep missed. THE MODULE owns the
  `## <id>` heading, the slot line, ARCHIVE_HEADING, the id forms, the
  ledger separators and `check_prose`, and REGRADE_BLOCKER — the
  minting form now beside the predicate that judges it; old names
  re-exported so every existing reader keeps one source.
  THE SECOND RED, not in the brief and worth more than the refactor:
  `verbs._set_slots` FOUND a block with `^##\s+(\S+)\s*$` and ENDED it
  with `startswith("## ")`. Those disagree on a tab-separated heading,
  and where they disagreed the write loop ran past its block into the
  next item — `item park` and `item promote` the two callers, exit 0,
  no finding, both blocks still well-formed. Red against a whole-repo
  `git archive` of 66bd2af whose own self-check was green first:
  `AssertionError: 'PARKED' != 'READY' : xx-2 was parked by a call that
  named xx-1`. Both ends now come from `grammar`.
  EXISTING DATA IS CLEAN, measured before the fix was trusted rather
  than assumed: 551 `##` headings across all six live carriers
  (dotfiles, lifecycle, cache-fix ITEMS.md + ITEMS-DONE.md), every one
  `'## '` with exactly one space, zero anomalies — with a planted-file
  control that flagged tab, double-space and no-space while ignoring
  the good headings and a real `###` body line, so the zero is an
  absence and not a dead pattern. Blast radius future-only; no repair
  owed.
  VERIFIED AT THE ARTIFACT by the peer desk, bytecode caches deleted
  first: `Ran 281 tests … OK` (275 baseline + 6), 0 failed 0 SKIPPED;
  `--test` `rows: 73  73 passed, 0 failed, 0 raised, 0 skipped`,
  identical to baseline; `prove-rows` `63 of 73`, same ten named rows,
  none newly dark. Booked from the lane's honest residue: lc-63
  (`item promote` inherits the fix through the shared helper and has no
  executed arm of its own). One basis correction fed back: `ends_block`'s
  docstring says a block's body lines never begin with `##`, which is
  false — `cache-fix/ITEMS-DONE.md:2509` is a `###` line inside a body
  — while the predicate is anchored at exactly two hashes and is
  therefore correct. The code holds; the sentence justifying it was
  wider than what it establishes.
