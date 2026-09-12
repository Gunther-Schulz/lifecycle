# lifecycle — dev notes

The maintenance layer. Never loaded by operational files.

**That placement is load-bearing, not incidental.** This directory sits
outside every operational load path so a note about an instrument cannot
become an input to it. Files move within `dev-notes/`; the directory's
position does not.

The declaration registers this directory as the `maintenance notes` kind
(`.claude/lifecycle.json`): home `dev-notes`, writer `session`, reader
`session`, staleness by use-evidence, exit by the drain pass, growth
bounded-by-exit. An entry leaves by being applied or dropped, and both
are recorded — an entry that is merely read has not left.

## What belongs here

- `*-OBSERVATIONS.md` — instrument lessons: a guard that fired on
  legitimate work, a demand that could not be executed, a check whose
  predicate no input could falsify. They live in the OWNING instrument's
  repo, never in a pooled cross-instrument list. None exists here yet;
  `lc-8` books creating this repo's, and `lc-78` asks first whether the
  class becomes a registered lifecycle kind — in which case the entry
  shape is redesigned rather than carried over, so build `lc-8` after
  that call or knowing the shape is provisional.

Nothing else. A file here that is neither this README nor an
observations carrier is a stray, and `lifecycle kind sweep` is what says
so.
