# lifecycle — working discipline

A Claude Code plugin: lifecycle management for everything a repo
persists. The primitive is the KIND, not the item — every kind of
thing a repo keeps is registered in that repo's
`.claude/lifecycle.json` with six declared stages (home, writer,
reader, staleness, exit, bound), and a kind with an undeclared stage
is a checker finding.

Design of record: `carrier-rework-design-2026-08-26.md` in
claude-code-cache-fix (`docs/directives/`), revision 2. Where this
repo and that document differ, the design wins and the difference is
a defect here.

## The two exit-code contracts — do not unify them

They are different contracts and a translation layer between them
would destroy the distinction each one exists to make.

- **A `lifecycle` verb exits** `0` clean · `2` a finding · `3` could
  not verify. A finding and an unreadable input never share a code.
  This is what a caller of `lifecycle item …`, `lifecycle kind …`,
  `lifecycle migrate`, `lifecycle --test` reads.
- **A lane's `Trigger:` predicate — a command `lane list` EXECUTES,
  never a `lifecycle` verb — exits** `0` fire · `1` quiet · `>=2`
  broken. `lane list` reads that code and reports the lane's state,
  so a dead predicate never renders as a clean board.

`lane list` is the one place both meet: it EXITS under the first
contract while READING the second. A `lane list` run that finds a
broken predicate exits `2` because it found something — not because
it saw a `2`.

## Discipline

- **A checker has THREE answers**: verified clean, verified broken,
  and COULD NOT VERIFY — which is its own answer, folded into
  neither. Silence, or a number shaped like a pass, is never allowed:
  if a run proves nothing, its output says it proves nothing.
- **A check counts only once it has gone RED on the real defect.**
  Not "would have caught it" — demonstrated, with the arrangement
  recorded. A red that is a module-load or import error proves the
  code is new, never that the check discriminates: after the checker
  exists, disable ONE named condition and watch that specific bite go
  red.
- **The refusal table is one source for two consumers** — the
  acceptance test and `lifecycle --test`. Rows live in
  `plugin/cli/lifecycle_core/refusals.py` as executable firing
  inputs; nothing restates them in prose. A row that cannot be fired
  is labelled PROSE-REST with its reason and is never deleted to make
  the roster green.
- **The leak scan runs before the irreversible boundary.**
  `tools/absence-scan.mjs` is armed as this repo's pre-push hook
  (`tools/git-hooks/pre-push`, symlinked into `.git/hooks/`) from the
  repo's first commit, because this repo is where workflow templates
  extracted from PRIVATE repos will land. No template is extracted
  until that hook exists.
- **Nothing crosses the seam.** Templates carry no project
  identifiers upward; a repo file declares and never restates
  downward.

## Role files

- `LEDGER.md` — the on-disk ledger: one entry per line, append-only,
  chronological. Facts with their basis, decisions with their why,
  open questions. Read its tail before re-deriving anything that may
  be settled.
- `BACKLOG.md` — parked items (each with its named missing evidence)
  and ready items (decision-complete, dispatchable).
- `dev-notes/` — the maintenance layer, never loaded by operational
  files.
- `tools/` — repo-owned checks. `absence-scan.mjs` and `tmpdir.mjs`
  are byte-identical copies of claude-code-cache-fix's; they are not
  edited here. That repo keeps its own copy and its own wiring, and
  the de-duplication is a later wave's act with the hook rewiring in
  the same change. Two copies for one wave is the deliberate cost.
- `test/` — `absence-scan.test.mjs` and its fixture are byte-identical
  copies too; the `test_*.py` files are this repo's own.
- `plugin/cli/` — the `lifecycle` entry point and its package.

## The two carrier invariants a reader must not conflate

- **Conservation has a SIGN, and the two signs are two diagnoses.** SHORT
  (`items + done` below `baseline + added − compacted`) means a body left by
  a path that is not a closure — a hand deletion, a bad merge. OVER means
  the homes hold more than was ever admitted, whose ordinary cause is an
  interrupted close, and it is RECOVERABLE. One message for both told the
  loss story over the recoverable case; that is why there are two rows.
- **DUPLICATE is the move's design working, not corruption.** A close
  appends to the done home, then deletes from the carrier, then commits. The
  window between the first two holds two copies of one body, and the
  opposite ordering would put that window on the LOSS side instead. So an id
  in both homes is expected debris from an interrupted close: the repair is
  to delete the LIVE copy once the done copy is confirmed complete, never to
  pick one at random.

## Verify

```bash
python3 -m unittest discover -s test -p 'test_*.py' -t .   # the CLI
python3 tools/prove-rows.py                                # every row, red-first
node --test test/absence-scan.test.mjs                     # the leak scan's bites
node tools/absence-scan.mjs --git-range ..HEAD             # the leak scan itself
```

`tools/prove-rows.py` is the RED half of "a check counts only once it has
gone red", made re-runnable. For each recorded arrangement it disables one
named condition, runs the whole roster, and asserts a PAIR: the named row's
verdict changes, and no other row's does. A row whose mutation darkens
nothing is passing for a reason nobody wrote down; a mutation that darkens
four rows proves none of them. It restores by FILE COPY and clears
`__pycache__` around every arm. Rows with no recorded mutation are LISTED at
the end, never omitted — the roster says how much of itself is proven.

**The verdict it compares is the exit code AND the row name in the output.**
Codes alone do not discriminate here: every finding is a `2`, so a guard
removed at one site while a shared one catches the same input under a
different row's name reads as "unchanged" and the row reads as unproven.

**One of the 51 node bites fails here and is EXPECTED to** — read it
before treating it as a defect. `source: every UUID in a tracked
SOURCE_SCANNABLE file is on the synthetic allowlist` guards itself
against a silent scope collapse by asserting the walk reached
`test/`, `tools/`, `proxy/` and `docs/`, that `BACKLOG.md` is in it,
and that it enumerated more than 500 files. Those anchors are
claude-code-cache-fix's tree, and the file is a byte-identical copy
that is not edited here — so the bite structurally cannot pass in
this repo. It is a COULD NOT VERIFY for that one bite, never a
statement about the scanner: the other 50 pass, and the scanner is
separately red-proven on this repo's own files by the pre-push hook.
Making it portable means parameterising the anchors in cache-fix
first, so both copies move together.
