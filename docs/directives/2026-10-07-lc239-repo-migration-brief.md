# lc-239 — migrate one governed repo off schema 2 (2026-10-07)

For the session that already works in the repo. Operator decision,
first-hand at the lifecycle drain desk on 2026-10-07: the session living
in each governed repo runs its own migration, so no outside session
writes a working copy another session holds. To you this is testimony
about that decision; declining, or asking the operator first, is yours.

Exercised at the lifecycle desk the same day on three repos with no live
session (begehung `8211887`, daneel `1a678f0`, claude-code-cache-fix
`a236107`): each went from `kind check` FINDING to
`kind check: CLEAN ... every stage declared`.

## What changes

1. `.claude/lifecycle.json`: the `trigger` stage is added to the `items`
   and `ledger lines` kinds (the migrator states `done bodies` itself),
   the ledger kind's writer names the four executable actions instead of
   the bare `ledger add` group, and `schema` goes from 2 to the current
   floor.
2. The `schema:` head line of `ITEMS.md`, `ITEMS-DONE.md` and `LEDGER.md`.

Nothing else. No item, grade or ledger line moves.

## Procedure

`LC` is the lifecycle checkout; `lifecycle` on your PATH is its CLI. Run
from your repo root, tree clean, on your usual branch.

1. `lifecycle migrate --schema-from 2` — the dry run. Expected: two
   UNCLASSIFIED keys, `kinds.items.trigger` and
   `kinds.ledger lines.trigger`. A repo declaring further kinds lists
   theirs too. Anything else (a COULD NOT VERIFY, another key) — stop and
   report it to the lifecycle desk; do not apply.
2. Author the triggers: `python3 LC/tools/author-standard-triggers.py .claude/lifecycle.json`.
   It inserts the two standard trigger lines and refuses to write if the
   parsed result differs from "the same declaration plus those keys".
   The two texts are a READING of the kind (admission fires on
   `item add`; a ledger line's button is `ledger add decision`) — read
   them and change them if your repo's kinds are occasioned differently.
   Further kinds: write their trigger yourself (`verb <name>`,
   `predicate <cmd>`, or `none, declared why: <reason>`), or pass them in
   a second JSON file mapping kind name to text.
3. If `lifecycle kind check` still prints a `dangling_reference` line for
   the ledger kind, replace the writer value `verb:ledger add, session`
   with `verb:ledger add decision, verb:ledger add dropped, verb:ledger add rejected, verb:ledger add superseded, session`.
4. `lifecycle migrate --schema-from 2` again: `UNCLASSIFIED ... : 0`.
5. `lifecycle migrate --schema-from 2 --apply`. It reads every target
   back from the file and must end
   `APPLIED — ... target(s) read back from the artifact`.
6. Verify: `lifecycle kind check` ends CLEAN with every stage declared;
   `lifecycle item check` exits with the SAME code as before step 1 (take
   it before you start) — the migration must not move it.
7. Read the deletion side of `git diff` before committing: the `schema`
   lines, the writer line, and — a known cosmetic effect — lines whose
   escaped dashes or section signs the migrator re-wrote as literal
   characters. Any other removed line is a stop.
8. Commit the four files by pathspec with your own trailer. Pushing is
   your repo's own rule.

## Two repos known to need diagnosis first

`dispatch-guards` and `skill-craft` answered COULD NOT VERIFY on the dry
run. Measured for skill-craft on 2026-10-07: its `LEDGER.md` opens with a
prose preamble and carries `schema:` further down, where the tool reads
only a head line. dispatch-guards was not re-measured. Diagnose before
step 2 and report what the dry run names.

## Report

One message to the lifecycle desk (`lifecycle-72`, or whichever
lifecycle session is listed) when done or stopped: the commit hash, the
closing lines of `kind check`, the `item check` exit code before and
after, and anything the procedure did not cover.
