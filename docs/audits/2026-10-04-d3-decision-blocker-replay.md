# D3 replay probe: was a decision blocker already answered by the ledger when it was booked?

**2026-10-04, desk lifecycle-4f.** The pre-registered probe for decision D3
of `docs/directives/2026-10-04-refocus-design-round-2.md`. Authorized by
the judgment desk as wave 2. Read-only over git history.

**Verdict: FAIL on the pre-registered criterion.** The comparator finds
real cases, but it fires on unrelated lines almost three times as often.
D3 is not built as designed. Section 4 says what the probe found that is
worth keeping.

The grades in section 2 are this desk's own reading and this desk also
designed D3. **Checked 2026-10-04 by the judgment desk (tmp-ad), RELAYED
from its ruling:** it re-graded 17 rows at the matched ledger lines, all 9
TRUE and 8 sampled FALSE, and agreed on all 17 at the TRUE/FALSE boundary.
It reads three FALSE rows (the "has the design round closed" questions) as
borderline; flipped, the count is 12 against 22 and still fails. It first
read one pair of TRUE subgrades the other way round and then withdrew
that: its own join script printed only the first two matched lines per
row, so it had graded one statiker question without the line that answers
it (the third of six). Re-read on the full set of matched lines, it
confirms this desk's grades for both rows. A head slice read as the whole
body, on the checker's own instrument, caught because the grades file
carries every matched line number. The designer's grades stand as checked:
17 of 17. **D3 and D4 are DECLINED by that ruling, with no comparator
repair spent.**

Matched line numbers are positions in the ledger as of the booking
commit. They equal today's line numbers only because the ledger is
append-only above its archive section; that is assumed here, not checked
per row.

## 1. The instrument

`tools/decision-blocker-replay.py` (committed with this file). For each
roster repo it walks every commit that touched the item carrier, takes the
first commit in which each (item, decision question) pair appears, reads
the ledger as of that commit, and runs the shipped comparator
(`verbs.decision_candidates`, cap 0.05, unchanged) on the question.

Controls, printed on every run: in each repo whose ledger holds decision
lines, the newest decision question replayed against its own ledger fires
on itself, and a nonsense question stays silent. Both held in all seven
such repos. Three repos (beat-the-books, begehung, skill-craft) hold no
decision lines, so the comparator has nothing to match there and their
zeros are not zeros.

Rows, with matched lines, are in
`$XDG_STATE_HOME/lifecycle/baselines/d3-replay-2026-10-04.jsonl`. They
stay outside this repo because they quote other repos' carriers.

## 2. The numbers (machine-computed unless marked)

| quantity | value |
|---|---|
| decision blockers ever booked, ten roster repos | 798 |
| born in a migration commit (20 or more at once), never pooled | 571 |
| booked by a session | 227 |
| of those, ledger held no decision line at the time | 48 |
| EXERCISABLE: session-booked, ledger held at least one decision | 179 |
| fires among the exercisable | 44 rows, 41 distinct questions |

Hand-graded, per distinct question (this desk's reading):

| grade | count | meaning |
|---|---|---|
| EXCLUDED | 5 | the blocker's text equals a ledger question. Four are the carrier's own clearing act (a blocker is amended to the answered question so that it resolves by equality); one is a rewording by `item park`. None is a booking against an unread answer. |
| TRUE | 9 | a matched line answers or bounds the question |
| FALSE | 25 | the matched lines share vocabulary and nothing else |
| duplicates | 2 | spelling variants of a question already counted |

Of the 9 TRUE:
- **3 are strong**: the ledger held an answer the blocker ignored or
  contradicted. A statiker item was held on "an operator-stated deferral"
  two days after the ledger recorded the operator ending that deferral.
  This repo's third-grade freeze exception was booked against a prior
  decision that had ruled the third grade out. A statiker containment
  question was booked after the ledger had ruled which stage owns
  containment.
- **3 were already cited** by the session in the question or its
  not-derivable statement. A cite demand would have passed without
  changing anything.
- **3 bound the question** without settling it.

Of the 25 FALSE, 3 are a separate shape worth naming: an operator GO of
the same class had been granted before. A prior GO does not make the next
one derivable, so they are graded FALSE, but they are not noise.

## 3. Against the pre-registered criterion

| arm | threshold | result |
|---|---|---|
| at least 5 TRUE fires | 5 | 9: met |
| TRUE fires outnumber FALSE | TRUE > FALSE | 9 against 25: **not met** |
| as-of ledger reconstructable for at least two thirds | 67% | 100% (no booking commit lacked a ledger file): met |

FAIL. The round allowed one repair attempt at the comparator. This desk
recommends against spending it: 34 graded questions are the only data, so
any comparator change would be tuned on the set it is then tested on.
Requiring three shared tokens, for instance, keeps 5 TRUE and 7 FALSE, and
that threshold change is the move law 11 forbids in any case.

D4 (the intake join reading the ledger and closed bodies) was parked
behind this result with the stated expectation that a FALSE-fire failure
here would be worse there. It is declined with D3.

## 4. What the probe found anyway

- **The seam is rare.** At most 6 of 179 exercisable bookings (3.4%) were
  made against a ledger line the session had not already cited, and 3
  (1.7%) against one that answered or contradicted the question. A refusal
  at every decision-blocker booking would be paying for a 2 to 3 percent
  case.
- **Those three are exactly the failure this arc is about**, each a
  session writing "this needs a decision" while the record held the
  decision. They are specimens with commit references, in a population
  with a known denominator, which the design of record did not have
  before.
- **Token overlap between questions is the wrong retrieval for this.** It
  worked for R7 because R7 compares a new decision question with old
  decision questions asked about the same thing. A blocker question and
  the ledger line that answers it are often worded differently: the
  strongest case here shares four tokens, the next three, and noise
  reaches five.
- **Three repos cannot be probed at all**: no decision lines in their
  ledgers.

## 5. Not verified

- The TRUE and FALSE grades are one reader's, unblinded, and the reader
  proposed the mechanism. No second grading exists.
- "First commit in which the pair appears" is the booking moment only
  where the carrier history is linear and the text was not reworded. One
  rewording was caught by hand (EXCLUDED); others may sit among the FALSE
  rows without changing their grade.
- Whether any of the three strong cases cost an operator interaction was
  not checked against transcripts.

## 6. Reproduce

```
python3 tools/decision-blocker-replay.py --out "$XDG_STATE_HOME/lifecycle/baselines/d3-replay.jsonl"
```
