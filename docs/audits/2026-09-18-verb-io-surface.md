# Every verb's input/output surface against malformed input

**Read-only enumeration, 2026-09-18, one sonnet lane at `aa1cc44`,
integrated and spot-verified at this desk.** The question: for each verb,
what happens on absent · empty · unparseable · huge · unresolvable input,
a missing or malformed argument, unset environment, outside a git work
tree, a subprocess failure, and shell metacharacters — classified CLEAN /
FINDING / COULD-NOT-VERIFY / CRASH / SILENT / REFUSED.

**Surface size, derived from `build_parser()` rather than counted by
hand:** 12 top-level verbs, 36 leaf command paths, plus the `--test`
entry point. No design-named verb is unwired.

**Coverage, stated so the green is not read wider than it is:** ~90
invocations, roughly 70-80 of the 36 x 10 matrix executed. The rest
generalize through genuinely shared code (`resolve_repo`, `decl.read`,
`_context`, `_load` back every carrier-reading verb identically), and the
cells that do neither are listed under UNTESTED below rather than
assumed.

## The two defects

### 1 — `lane new <door>` does not validate its one positional argument

`lanes.py:cmd_lane_new` builds `lanes_dir / f"{door}.md"` from unchecked
input. **Re-run at this desk in a scratch clone with all three XDG roots
redirected, not taken on report:**

| input | result |
|---|---|
| `goodlane` (control) | writes `lanes/goodlane.md`, declares `goodlane`, exit 0 |
| `../escape` | writes `lanes/../escape.md` — the repo ROOT — declares the literal `../escape`, **exit 0 CLEAN** |
| `bad/door` | uncaught `FileNotFoundError`, raw traceback, **exit 1** |
| `""` | writes `lanes/.md`, declares the empty string, exit 0 |

Exit 1 is outside this tool's contract, and `exits.py:10` says so in its
own words: *"`1` is deliberately unused here, so a python traceback's
exit 1 is never mistaken for a verdict of ours."* This is that sentence's
first live counter-example.

**THE FIX IS PLACED, NOT INVENTED — THE SYSTEM ALREADY HOLDS THIS
CONCEPT.** `desk.py:69-70` takes the same shape of input (a caller-named
string that becomes a filename) and folds it:
`_UNSAFE_FOR_FILENAME.sub('_', desk_id)`. Its comment at `desk.py:56-58`
names the exact hazard — *"a `/` in it would otherwise let a caller's id
escape this directory"* — and chose FOLDING over refusal deliberately. So
the hazard was understood, written down, and defended at one of the two
sites that has it. `lane new` predates nothing and shares everything;
what it lacks is the sweep that would have found it.

Read the right way round, this is the members question at a defect-class
find (global corpus, dependents-or-members): the artifact carrying the
found instance is the first population to sweep, and the found instance
is the sweep's own positive control. Nobody swept.

**Whether `lane new` folds or refuses is a real choice and the two are
not equivalent.** `desk state` folds because a desk id is an identity it
must not lose. A lane door is a NAME THE DECLARATION WILL CARRY and that
`lane list` resolves later, so a folded `bad_door` silently renames the
caller's lane, while a refusal costs one retry. Recommendation: REFUSE
with a registered row, reusing `_UNSAFE_FOR_FILENAME` as the predicate
and not as the transform.

### 2 — a carrier truncated at a block boundary is invisible to five of six read verbs

A carrier cut immediately before a `## <id>` heading — the exact shape
`atomic.py`'s own docstring warns about — was built as a real 2-item
carrier cut to 1:

| verb | answer |
|---|---|
| `item check` | **FINDING [conservation_short]**, exit 2 — the only catch |
| `item ready --head` | "1 live item(s) in total", exit 0, silent |
| `item waves` | "scanned: 1 live item(s)", no truncation signal |
| `item statusline` | `1R.0P head -`, exit 0, silent |
| `item ratio` | fires exit 2, but as `capture_dominated` — a flow alarm, never "a body is missing" |

`item slots`, `close`, `promote`, `park`, `amend` share the same `_load`
path with no conservation call of their own. **Marked inferred from
source, not each individually executed.**

**Conservation is the only instrument that can see this, and it runs in
exactly one verb.** Every other verb reports a population it never
checked the extent of — the same defect class this repo found five times
on 2026-09-18, here at the widest surface yet: a caller scripting against
any item verb but `check` gets a confidently-reported, silently
incomplete answer.

## What was examined and found CLEAN — a result, not an omission

The shared foundation is genuinely sound, and the three-answer contract
holds across it: no `--repo` outside a work tree, a `--repo` that is a
file, a non-repo directory, the git binary removed from PATH, an absent
declaration, malformed JSON, non-UTF8 declaration bytes, a
gitignore-swallowed declaration, an absent carrier, a zero-byte carrier —
each lands on a named FINDING or COULD-NOT-VERIFY with its reason, none
on a crash and none on a false CLEAN.

Notable positives worth keeping: `item add` EXECUTES an `evidence`
predicate at admission time and classifies subprocess-not-found as a
finding rather than a crash; a multi-line slot value is refused
pre-write, so the carrier cannot be injected with an unparseable body;
`migrate` refuses an absent source because *"zero entries is a number
shaped exactly like a clean migration"*; `ledger rejected` prints "NONE
recorded" rather than conflating found-nothing with could-not-check;
`init` never reports CLEAN even on a fully successful write.

## Two lower-ranked cells

**`--repo` must precede the subcommand.** `lifecycle kind check --repo X`
exits 3 on an argparse usage error. The contract is right, the message
misleads: it reads as a bad repo path when the real fault is flag order.

**`init` resolves its own installed position** (`parents[3]`) to find the
carrier-kind definitions. Well-guarded — COULD-NOT-VERIFY, "nothing was
written" — but a vendored copy without that sibling file makes `init`
permanently unusable there, silently as a capability.

## UNTESTED, named rather than assumed clean

`item compact`, `item supersede-closure`; `workflow bind --set` parsing
(no template fixture exists — `plugin/workflows/` holds only
`.gitkeep`); `verify`'s subprocess-failure and timeout paths; `record
check` against a malformed or binary record; `migrate
--apply/--merge/--retire-source` against real conflicting content; huge
inputs at any verb; non-UTF8 or control bytes inside carrier BODIES
(tested only in the declaration).

`migrate.py` is the shallowest-tested verb here at 3,263 lines, which is
the same conclusion the robustness review reached from the other
direction.

## The lane's own two disclosures, and what they cost the instrument

Reported unprompted rather than hidden, which is the conduct wanted.

**`lane register` wrote to the real roster.** The brief isolated
`XDG_STATE_HOME`; `lane register` writes under `XDG_CONFIG_HOME`. The
lane caught it, restored `~/.config/lifecycle/repos`, and re-ran
everything with both redirected. **Verified at the file by this desk: 3
lines, the single declared repo intact.**

**This is a defect in the BRIEF and a finding about the TOOL.** The
isolation set must be checked against the enumeration of globals the
exercised path CONSUMES, never the ones the test happens to touch (global
corpus, the partial override) — and here nothing publishes that
enumeration. A caller isolating lifecycle for a probe has no way to learn
the set but to be bitten by it. Booked as lc-204.

**THE NUMBER, EXECUTED RATHER THAN ESTIMATED, AND IT SPLITS IN TWO.**
References across `plugin/cli/`: `XDG_STATE_HOME` 30, `XDG_CONFIG_HOME`
8, `XDG_DATA_HOME` 1, `XDG_CACHE_HOME` 1, over six files
(`XDG_RUNTIME_DIR` returns 0 — the sweep discriminates rather than
matching anything XDG-shaped). But the two singletons are the same two
lines, `retire.py:160` and `:162`, and they appear nowhere else: they are
entries in the resolution table for a home a REPO MAY DECLARE, not paths
this tool writes. **What lifecycle itself writes under is TWO** —
`XDG_STATE_HOME` (fire log, desk state) and `XDG_CONFIG_HOME`
(`lanes.py:133`, the roster). The brief isolated one of two.

So lc-204's published set must derive over CONSUMPTION SITES and keep the
two questions apart — written-by-the-tool versus resolvable-as-a-declared-home.
An enumeration of all four would tell a probe author to isolate two roots
that do not matter, which is an assurance wider than its predicate
shipped by the mechanism built to prevent exactly that.

**And the knowledge was already in the repo, one file from the author who
needed it.** `refusals.py:1657-1670` isolates `XDG_CONFIG_HOME` by hand
in `_lane_cli`, and `refusals.py:2952` documents doing it "the same way
`_lane_cli` isolates `XDG_CONFIG_HOME` above". The test harness knew the
roster escapes state-only isolation. That is the same shape as
`desk.py:56` knowing about the path escape `lane new` does not defend —
twice in one audit, the lesson written beside one mechanism and never
swept to its sibling.

**One unexplained fire-log line** carries the lane's scratchpad UUID with
a `sweepprobe` directory it says it never created. The fire log records
verb, repo and outcome only, so the line cannot be attributed further,
and the 138MB file was not touched again. Recorded as unexplained; the
fire log is already known to be dominated by test pollution (lc-183).
