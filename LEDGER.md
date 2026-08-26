# lifecycle — ledger

On-disk ledger for this repo: one entry per line, append-only,
chronological. Facts carry their basis, decisions carry their why
(and the rejected alternative where it is not obvious), open
questions stay listed until they close. Absence of an entry never
reads as settled.

**Consumer:** any session working in this repo — read the tail before
re-deriving something that may already be settled, and append here
rather than leaving a rationale only in a commit message.
Boundaries: work items go to `BACKLOG.md`, standing rules to
`CLAUDE.md`, maintenance journals to `dev-notes/`.

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
  `capture-key-prefix`). Measured: a planted
  `/home/g/dev/Gunther-Schulz/private-repo/tools/x.sh` line in a
  markdown file scans CLEAN, exit 0; a planted `s-`+8-hex token in
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
- **2026-08-26 — the fire log lives under XDG state, never
  `~/.claude/`.** `$XDG_STATE_HOME/lifecycle/fire.jsonl` (default
  `~/.local/state/lifecycle/fire.jsonl`). Basis: on this machine
  `~/.claude/` is protected by path shape, so tool data kept there
  costs a permission dialog on every read and write — for the
  operator and for every dispatched agent — and one such prompt
  denied mid-task has already lost a session's work.
