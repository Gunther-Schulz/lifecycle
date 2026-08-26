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
- **2026-08-26 — the fire log lives under XDG state, never
  `~/.claude/`.** `$XDG_STATE_HOME/lifecycle/fire.jsonl` (default
  `~/.local/state/lifecycle/fire.jsonl`). Basis: on this machine
  `~/.claude/` is protected by path shape, so tool data kept there
  costs a permission dialog on every read and write — for the
  operator and for every dispatched agent — and one such prompt
  denied mid-task has already lost a session's work.
