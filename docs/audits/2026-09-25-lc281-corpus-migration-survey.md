# lc-281: corpus-to-lifecycle migration survey

**2026-09-25, desk lifecycle-d8, queue item 4 under the operator's final delegation (LEDGER decision lines 2026-09-25).**

## Pins — the corpus this survey classifies

The operator corpus lives in TWO repos, not one: six of the eight modules in dotfiles `claude/modules/` are symlinks into ethos. A survey pinned to one dotfiles commit reads six ~60-byte link texts instead of six modules (measured: the first enumeration here counted 26 bullets, not 77).

- **ethos `2fbc442`** — `plugin/modules/`: grounding, fixing, calibration, insurance, reporting, accretion
- **dotfiles `78df677`** — `claude/modules/`: routing, environment (routing includes the 2026-09-25 scope-clause sharpen)

## Method

- **Grain:** a rule-bearing bullet = a line opening `- ` (top) or `  - ` (sub) in a pinned module. The count is DERIVED from the files by two independent instruments (a Python scan and a per-module `grep -cE`), equal for every module.
- **Classes, verbatim from LEDGER.md:148 (refocus R9):** "lifecycle enforces at ACTS by refusal (measured); notice-borne enforcement is untested and is no class. Class (a) a refusal enforces the rule today, (b) an act lifecycle owns could carry a refusal, (c) otherwise."
- **Facts:** four read-only sonnet lanes (A grounding+fixing 23, B calibration+insurance+reporting 22, C accretion+routing 18, D environment 14). Each returned one line per bullet: candidate class, row ident or verb + predicate, the rules, sure/unsure. Lane A first returned 20 of 23 and was asked for the three it skipped.
- **Grading:** the desk. Every row ident cited under (a) resolves in `lifecycle --test --list` (26 of 26). The lanes read roster TEXT, not source: an (a) says the row's stated refusal covers the named part of the rule, not that its code was re-read here. Partial coverage is class (a) with its scope named; the rest of such a bullet stays prose.
- **Desk regrades:** routing:222 a-partial -> (c); reporting:212 (b) -> (c); fixing:387 and fixing:568 merge into one (b) item.

## Counts

**77 bullets = (a) 16 + (b) 3 + (c) 58** (sum: 77).

| module | pin | bullets | (a) | (b) | (c) |
|---|---|---|---|---|---|
| grounding | ethos 2fbc442 | 7 | 3 | 0 | 4 |
| fixing | ethos 2fbc442 | 16 | 6 | 2 | 8 |
| calibration | ethos 2fbc442 | 9 | 1 | 0 | 8 |
| insurance | ethos 2fbc442 | 5 | 1 | 0 | 4 |
| reporting | ethos 2fbc442 | 8 | 2 | 1 | 5 |
| accretion | ethos 2fbc442 | 6 | 3 | 0 | 3 |
| routing | dotfiles 78df677 | 12 | 0 | 0 | 12 |
| environment | dotfiles 78df677 | 14 | 0 | 0 | 14 |

**(b) bookings:** lc-297 (fixing:387, fixing:568) and lc-298 (reporting:75), both PARKED on the shared freeze-release blocker. **(a) corpus edits** (shrinking an enforced rule to a pointer) are NOT done here: the corpus has its own maintenance doctrine and mint gate, so each is a dotfiles/ethos act.

## Per-bullet classes

| bullet | level | class | basis | rules (lane summary) |
|---|---|---|---|---|
| grounding:3 | top | a | row(s) evidence_unmarked — scope partial: the row enforces the named part at lifecycle's own act; the rest of the bullet stays prose | Claims/verdicts need a basis or the label unverified |
| grounding:86 | sub | c | no mechanical test for a basis collapsing under one question | Collapse test |
| grounding:89 | sub | c | verifying a verdict's basis rules nothing out is not mechanizable | Reach test |
| grounding:102 | sub | c | checking a reused mechanism is restated is not computable | Transfer test |
| grounding:111 | sub | a | row(s) evidence_unmarked — scope partial: the row enforces the named part at lifecycle's own act; the rest of the bullet stays prose | Observed vs derived/recalled marked separately |
| grounding:141 | top | a | row(s) conservation_short / conservation_surplus / conservation_unverified — scope partial: the row enforces the named part at lifecycle's own act; the rest of the bullet stays prose | Persisted counts re-derived from parts at every edit |
| grounding:193 | top | c | adequacy of a dependents search is not computable | A change carries its dependents search |
| fixing:7 | top | c | which existing instances a change was read against is not checkable | Fix site and shape set by existing instances |
| fixing:40 | top | a | row(s) closed_ref_unresolvable / closure_pointer_ref_unresolvable — scope partial: the row enforces the named part at lifecycle's own act; the rest of the bullet stays prose | Verification names the object's identity, not its role |
| fixing:62 | top | a | row(s) migration_readback_disagrees — scope partial: the row enforces the named part at lifecycle's own act; the rest of the bullet stays prose | What was done is read off the object, never memory |
| fixing:111 | top | a | row(s) evidence_mark_malformed — scope partial: the row enforces the named part at lifecycle's own act; the rest of the bullet stays prose | New evidence re-opens premises; perishable marks |
| fixing:127 | top | c | effect altitude is not one computable predicate | Wrongness found only at the effect site |
| fixing:212 | top | a | row(s) route_set_unwatched / route_set_unnamed — scope partial: the row enforces the named part at lifecycle's own act; the rest of the bullet stays prose | Check premises pinned or derived from the live source |
| fixing:286 | top | c | designing a disproving probe is not computable | Load-bearing claims earn a refutation probe |
| fixing:309 | sub | c | general absence claims are not lifecycle's act | Absence claimable only with a known positive |
| fixing:331 | sub | a | row(s) record_line_unbasised / record_line_unbasised_hyphen — scope partial: the row enforces the named part at lifecycle's own act; the rest of the bullet stays prose | Delivered causal claims name their check or say unverified |
| fixing:345 | sub | c | reporter's definition capture is not computable | Symptom investigation quotes the reporter |
| fixing:387 | sub | b | booked lc-297: --test refuses a roster row with no recorded red-first arrangement | An instrument is unproven until red on its defect |
| fixing:479 | sub | c | expectation parentage not mechanically decidable | Expectation not derived from the artifact it grades |
| fixing:508 | sub | a | row(s) verify_check_did_not_run / cost_test_unverified / conservation_unverified / laws_absent_could_not_verify | Three answers, never a pass-shaped absence |
| fixing:547 | top | c | enforced by absence-scan.mjs git hook, not a roster verb | A cleanness claim needs a red-first probe before the irreversible boundary |
| fixing:568 | top | b | booked lc-297 (same predicate as fixing:387) | A manual finding is unfinished until a check reproduces it |
| fixing:582 | top | c | which variables a run reproduced is not computable | A result holds only for the variables its run reproduced |
| calibration:3 | top | c | pre-start self-check and reply-naming convention | Self-check loud/checkable/small/one-session; name gauge outcome |
| calibration:17 | top | a | row(s) record_slot_missing + record_closed_undrained/record_closed_unpointed (slot shape + closure-by-graduation; creation trigger & reply-naming unrefused) — scope partial: the row enforces the named part at lifecycle's own act; the rest of the bullet stays prose | Diagnosis-shaped work gets a 5-slot investigation record |
| calibration:45 | top | c | closing-review questions answered from a record | Before closing, answer missing/learned/routed/spent from the record |
| calibration:174 | top | c | whether another review round is owed | A repeat round names its reason and trend |
| calibration:211 | top | c | turn-ending/stall-avoidance discipline | A turn ends on settled state or a named blocker |
| calibration:231 | top | c | statistical judgment | A finding is noise until significance math confirms it |
| calibration:233 | top | c | session depth judgment | Past payback depth, restart rather than compact |
| calibration:279 | top | c | economic judgment over spend units | Price every spend by its unit |
| calibration:334 | top | c | mechanize-vs-prose and truth-level call | After an incident, mechanize only a computable trigger |
| insurance:3 | top | a | row(s) ledger_body (one-line shape only; ledger-read-first convention unrefused) — scope partial: the row enforces the named part at lifecycle's own act; the rest of the bullet stays prose | Ledger entries one line, append-only; re-derivation opens with a ledger read |
| insurance:14 | top | c | when fresh-context review is warranted | Fresh-context review owed for self-blind claims |
| insurance:31 | sub | c | escalation-route decision | Escalate to iterated falsification on the named profile |
| insurance:50 | top | c | dispatch conduct outside lifecycle's carrier domain | Waits carry an armed horizon watched by a poll |
| insurance:87 | sub | c | timer/horizon sizing conduct | Size a recurring horizon to half the remaining estimate |
| reporting:3 | top | c | recommendation-hedging and ratification-ask discipline | Don't hedge; book rather than ask |
| reporting:45 | top | a | row(s) decision_not_derivable_unstated (decision-blocker justification only) — scope partial: the row enforces the named part at lifecycle's own act; the rest of the bullet stays prose | Only operator-only decisions travel, as a numbered round |
| reporting:75 | top | b | booked lc-298: item evidence refuses a MEASURED claim that names no command, file:line or count | A ruling on artifact state is condition+measurement |
| reporting:91 | top | c | message-channel delivery/placement discipline | Writing isn't delivering; live state leads |
| reporting:130 | top | a | row(s) amend_without_reason (live-item in-place correction; general artifacts unrefused) — scope partial: the row enforces the named part at lifecycle's own act; the rest of the bullet stays prose | A correction lands in the delivered artifact |
| reporting:144 | top | c | reply lead/close formatting | Operator output opens with a short lead |
| reporting:206 | top | c | report layout convention | One finding per paragraph, lists for enumerables |
| reporting:212 | top | c | lifecycle's commit verbs WARN on a missing attribution trailer by design (verbs.py:578, 'A WARNING, NEVER A REFUSAL'); LEDGER:148 counts notice-borne enforcement as no class (desk regrade) | AI-authored commits carry attribution |
| accretion:3 | top | c | judgment-shaped session-start reading; no persisted artifact act for lifecycle to check | Read project CLAUDE.md, scan ledger tail/backlog ready items before working; mint generalizing corrections into CLAUDE.md |
| accretion:12 | top | c | interpretive precedence rule between two texts, not an act | Project convention overrides global convention on direct conflict, within that project |
| accretion:16 | top | a | row(s) kind_stage_undeclared (covers only: every kind's stage ownership incl. reader/writer/home must be declared) — scope partial: the row enforces the named part at lifecycle's own act; the rest of the bullet stays prose | Defines file-role homes; consumer named at write time; artifacts in English |
| accretion:102 | top | c | chat-only decisions leave no artifact trace; unobservable to any tool | Work is done now or booked to a carrier; a change stated only in chat evaporates |
| accretion:155 | top | a | row(s) capture_dominated (retirement-ratio trigger) + unknown_grade_write (closed grade vocabulary on write) — scope partial: the row enforces the named part at lifecycle's own act; the rest of the bullet stays prose | Items graded READY/PARKED by decision-completeness; closed vocabulary; write-set slot; retirement pass owed past 3:1 |
| accretion:282 | top | a | row(s) parked_without_typed_blocker (covers only: park requires a typed blocker) — scope partial: the row enforces the named part at lifecycle's own act; the rest of the bullet stays prose | Operator settle-verbs are made decisions executed now, never asked back |
| routing:8 | top | c | session-level dispatch-intake judgment; no lifecycle verb touches it | Gauge discovery/judgment split at intake per-question |
| routing:36 | sub | c | dispatch-brief/hold mechanics outside lifecycle verb space | Settled designs etc. default to dispatch; holds named with grain/release/premise |
| routing:119 | sub | c | reply-composition convention, not a carrier write | A GO reply names route, codex disposition, lane mapping |
| routing:175 | sub | c | retrospective behavioral tell, not a computable artifact predicate | Second consecutive discovery call signals a skipped gauge |
| routing:195 | sub | c | judgment heuristic over work character | Route by remaining work's character, not depth or size |
| routing:207 | top | c | model-tier default, outside lifecycle verb space | Brief-covered execution and discovery default to sonnet |
| routing:220 | top | c | pointer to another skill's reference | Fable dispatch defaults live in the dispatch-skill reference |
| routing:222 | top | c | desk_state_unknown_value enforces only the desk-state vocabulary; the bullet's delegation, release-gate and carve-out rules are judgment (desk regrade) | Top-tier desk delegates heavy arcs to a peer desk; release gate; carve-out floor |
| routing:406 | top | c | model-tier default | Haiku restricted to register-certified classes |
| routing:409 | top | c | vendor model behavior fact | Fable classifiers refuse guard work; route to opus |
| routing:422 | top | c | another plugin's hook mechanism | dispatch-guards veto gates |
| routing:428 | top | c | session-messaging mechanics; no lifecycle verb covers peer traffic | Peer facts direct; handoffs need horizon, ack, residue split |
| environment:7 | top | c | not an act lifecycle owns — a shell/tool config fact, no repo-persisted kind involved | Bash tool runs zsh; use POSIX/zsh syntax, not fish, in tool-issued commands |
| environment:11 | top | c | not an act lifecycle owns — shell-scripting correctness, no repo-persisted kind involved | Quote vars, avoid PIPESTATUS/bare colon-after-var, quote payloads, read back after cd may fail |
| environment:82 | top | c | not an act lifecycle owns — instrument/flag correctness for a shell search tool | Use `-E`/`--no-ignore-files` with ugrep; check subprocess return codes, never trust unread stdout |
| environment:146 | top | c | not an act lifecycle owns — instrument-choice correctness for bfs `find` | Use `-mmin`/`-newer`, not GNU relative `-newermt`, under bfs; verify zero results |
| environment:159 | top | c | not an act lifecycle owns — describes the operator's own terminal, not an agent act | Operator's pasted shell is fish; agent's zsh idioms don't apply there |
| environment:164 | top | c | not an act lifecycle owns — sudo/operator handoff, no repo-persisted kind involved | Root-requiring steps are the operator's to run, written in fish |
| environment:170 | top | c | not an act lifecycle owns — locale/numeric-format mismatch between shell tools | Don't pass awk decimal output to bash printf; locale split produces malformed numbers |
| environment:180 | top | c | not an act lifecycle owns — Claude Code harness settings.json, unrelated to lifecycle.json | Keep permissions.defaultMode pinned to manual; re-check before enabling auto mode |
| environment:210 | top | c | not an act lifecycle owns — Claude Code config-dir/XDG placement, unrelated to lifecycle.json | Keep tool data in XDG dirs, not `~/.claude/`, to avoid permission-prompt costs |
| environment:251 | top | c | not an act lifecycle owns — session rule-injection vs live-file drift, a harness fact | Pin load-bearing rule text in the brief; read from file when pin and injection differ |
| environment:264 | top | c | not an act lifecycle owns — SendMessage/subagent delivery timing, a harness mechanism | Load-bearing directives to a working subagent lane travel in the brief, not a mid-turn send |
| environment:280 | top | c | not an act lifecycle owns — points to an external dotfiles tool, not lifecycle | Use dispatch-economics.py readout for spend review; it judges nothing itself |
| environment:291 | top | c | not an act lifecycle owns — Claude Code compaction mechanics, unrelated to lifecycle.json | Restart/hand off near ~200k rather than rely on autocompact; log via hook |
| environment:320 | top | c | not an act lifecycle owns — harness cwd-move behavior; convention is agent discipline | Use absolute paths and `git -C <repo>` in any session touching more than one repo |
