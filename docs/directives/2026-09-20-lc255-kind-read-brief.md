# lc-255 — the read verb: `kind read <name>` (O6 §4 Part C, D3a)

Repo: /home/g/dev/Gunther-Schulz/lifecycle (PUBLIC — law 6: no machine paths, logins, or XDG roots in anything committed). Base commit: e04948a (measured at dispatch). Item: run `python3 plugin/cli/lifecycle item slots lc-255` and re-read it at HEAD before each verifier run (law 18).

## The item, in the design's own words

The booked design (docs/directives/2026-09-20-o6-surfacing-design.md §4 Part C — READ it, lines 129-146): "a read verb that prints the kind's body (or its pointer where the body is large), and whose invocation the fire log already records", and its stated boundary: "'unread' means *not read through the verb*. A session that opens the file directly reads it and the counter says otherwise. The design must report this as a proxy in the verb's own output." §7's transition table row 2 fixes the record contract: fire line `detail: read=<kind>`; red-first: reading through the verb writes a line; not reading writes none. D3a is operator-decided (GO 2026-09-20, ledgered).

## Assignments (dispatcher-made; invent nothing)

- Verb: `lifecycle kind read <name>` — a subcommand of the existing `kind` group. Fire-log verb path follows the group's existing spelling (read it off how `kind show` reaches `firelog.fire`; do not invent a new path format).
- NOT a carrier verb: it writes no carrier, takes no lock. Wire it the way `kind show` is wired (subparser, action tuple, dispatch branch) — `kind show` is the existing instance this change reuses; name in your report what you reused from it.
- Refusal row ident: `read_kind_unregistered` — fires when `<name>` is not a registered kind. FINDING, exit 2. Row lives in plugin/cli/lifecycle_core/refusals.py; its prove-rows arrangement lives in tools/prove-rows.py MUTATIONS (two files by design — lc-251 measured that split).
- Body-vs-pointer rule (assigned, print the branch taken): a home resolving to exactly ONE existing file of ≤400 lines prints the body verbatim; a longer single file prints a pointer block (repo-relative path, line count, mtime date) plus "body large — open the path above"; a glob/multi-file home prints a pointer block (file count, newest member repo-relative path + date). The pointer block IS a clean read: it still fires `read=<kind>`.
- Proxy-bound line (assigned wording, printed on EVERY successful invocation, body and pointer branches alike): `proxy bound: read here means read-through-this-verb — a direct file open is not counted.`
- Fire detail: set `args.fire_detail = "read=<name>"` exactly the way existing verbs set theirs (grep `fire_detail` in verbs.py for the idiom). Note lc-254's surfacing may APPEND `; surfaced=…` to your detail at main() — that is correct behavior, not interference; your tests must not assert the detail is ONLY `read=<kind>` on the live dispatch path (assert containment, or test below main()'s append point).

## Three answers (law 1 — a finding and an unreadable input never share an exit)

- Unregistered kind name → FINDING (exit 2), via the `read_kind_unregistered` row.
- Registered kind whose home cannot be read (no file matches, unreadable path) → COULD NOT VERIFY (exit 3), the output NAMING what was absent (the resolved home pattern and what it matched). This is not a refusal row; it is the verb's own third answer.
- Clean → body or pointer block + proxy-bound line, exit 0, fire line carries `read=<kind>`.

## MUST NOT MOVE

- `kind show` stays the STAGES surface — untouched output, untouched wiring.
- This verb never writes: not the kind's home, not any carrier. Read-only end to end.
- No always-on output anywhere outside this verb's own invocation.

## Grounding — files to read before building (report (h) cites what you actually read)

1. `python3 plugin/cli/lifecycle item slots lc-255` — the item is the brief's core; its requirement names the four-places rule applied.
2. docs/directives/2026-09-20-o6-surfacing-design.md §4 Part C (lines ~129-146), §5 D3, §7 row 2.
3. CLAUDE.md law 24 (the four-places worked example — verbs.py body, cli.py wiring, refusals.py refusal, test_verbs.py dispatch table as MUST-MOVE-WITH) and law 1, law 2 (lc-142 pair admission).
4. `kind show`'s implementation (verbs.py + cli.py) — the reuse instance.
5. tools/prove-rows.py header comments + one existing MUTATIONS entry (the arrangement form you are adding to).
6. The `## Verify` section of CLAUDE.md.

## Write boundaries

You own exactly: plugin/cli/lifecycle_core/verbs.py, plugin/cli/lifecycle_core/cli.py, plugin/cli/lifecycle_core/refusals.py, test/test_verbs.py, tools/prove-rows.py. Nothing else — not declaration.py, not test_declaration.py, not the carriers (ITEMS.md/LEDGER.md are tool-written and not yours to close). Scratch: your OWN scratchpad only. This is a shared working copy: the dispatcher works in it between your commits — commit by pathspec only.

## Done-criterion checks (all four run, real output in report (b))

At your final HEAD: `python3 -m unittest discover -s test -p 'test_*.py'` (baseline 990 OK (measured at e04948a) — yours must be baseline+your-new-tests, 0 failures, skips dispositioned); `python3 plugin/cli/lifecycle --test` (baseline 127 rows CLEAN (measured at e04948a), +1 for your row, CLEAN); the lc-142 PAIR for your new arrangement — real anchor run quoting `rows changed: read_kind_unregistered`, inert-anchor run quoting `rows changed: NONE` and its FAILED line (both verbatim in the report; the pair replaces a full walk unless you touched shared roster machinery, in which case the full tools/prove-rows.py walk runs too and its closing line is quoted); RED-FIRST both live arms at the real repo — before your change `kind read` does not exist (quote the CLI error), after it a clean read prints the body/pointer + proxy line and the last fire.jsonl line contains `read=<kind>`, and an unregistered name exits 2 under your row's message.

## Commit plan

One commit (or two if refusal+arrangement separate cleanly from verb+wiring; never more), message head `lc-255: kind read — reading becomes an observable act (O6 Part C, D3a)`, by pathspec: `git commit -m "…" -- plugin/cli/lifecycle_core/verbs.py plugin/cli/lifecycle_core/cli.py plugin/cli/lifecycle_core/refusals.py test/test_verbs.py tools/prove-rows.py` (flags before `--`). Commits stay unpushed; pushing is the dispatcher's act. Never amend.

## Critique pass (before your first build call)

Open every file/line the Grounding section names; anything unopenable or contradicting this brief is reported BEFORE building. Flag judgment calls; do not redesign.

---

A mid-run message may not arrive before the turn ends: on a gap
HALT THE ITEM, FINISH THE REMAINDER, REPORT — never halt the
LANE, since "halt and wait" is not a survivable state for a
subagent (source: §2, the delivery binding).
Closing report (mandatory; the project's own report form if it
defines one, else the §2 form here — never both; "none" is a
valid slot answer, silence is not): (a) items completed w/
evidence, (b) checks RUN w/ real output — FULL counts incl.
skips (`N passed, M failed, K skipped`), each skip dispositioned
(which check, why, whether the reason touches the item); a skip
in a check YOU built is a finding, not a pass — the built branch
did not execute, (c) gaps surfaced —
incl. anything needing a tier above yours, returned as a question
with its evidence, never settled at your tier,
(d) deviations w/ reason, (e) candidate lessons, (f) files
touched + commit hashes (unpushed) — only commits whose
Co-Authored-By trailer is YOURS; one you cannot claim by
trailer is "present in the tree, not mine"; a `.git/config`
write counts as a repo write, (g) what was NOT verified,
(h) sources actually read, of those the brief named.
Every claim about something OUTSIDE your own work — a file you
did not write, a mechanism, another repo, a tool's behavior —
names the read that opened it, or carries "inferred,
unverified"; a recommendation resting on an unopened claim
carries the grade too.
Drain your inbox before sending, and between parts of a
multi-part report: every dispatcher message received up to send
time is dispositioned or named as unhandled.
Report channel: SendMessage to the dispatcher — your final text
reaches no one.
Message ≤3000 chars each: a report longer than one message is
SPLIT into labeled parts (1/N) — do NOT write a report FILE
(harness-blocked for subagents); supporting data goes to the
brief's assigned DATA files, the message carries key findings
+ any such paths. A missing decision, file,
or value is surfaced as a gap, never bridged with a guess.
A check that got backgrounded is AWAITED before the closing
report (TaskOutput block=true on its task id) — ending your
turn orphans it; a report sent with a check still running is
an INTERIM report, says so, and names what remains.
Commits unpushed, by pathspec — `git commit -m "…" -- <paths>`
with every flag BEFORE the `--` (after it git reads `-m` as a
pathspec and the commit fails; `-F` for a multi-line message),
never
`git add` then `git commit` and never `-A`: the index is shared,
so a co-writer staging between your `git status` and your commit
rides out under your message whatever you added. A NEW file is
invisible to a pathspec commit until `git add -N <path>`
registers it (intent-to-add: zero content staged, full body
still committed). Trailer:
`Co-Authored-By: Claude <model> <noreply@anthropic.com>`.
Never amend — always a new commit: the amend-gate denies
subagent amends regardless of ownership (source: §1 amend
rule).
After sending the report your write grant is over: a defect you
find later is REPORTED, never edited or amended (source: §4
ownership rule).
