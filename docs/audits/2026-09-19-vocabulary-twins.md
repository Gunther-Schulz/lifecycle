# Vocabulary twins graded by load-bearing organs — 2026-09-19

**Method (the operator's statiker test, formalized):** grade repos
sharing this design's vocabulary by five load-bearing organs, never by
goals. Sonnet wrapper collected 7 repos (2 named specimens + 5 fresh
finds), codex gpt-5.6-luna ran the C1-C5 extraction (clean run, 163,959
tokens), the wrapper spot-checked codex's strongest citations against
fetched source (all confirmed) and independently verified one C3 by its
own grep before dispatch. VERIFIED throughout unless noted.

Organs: C1 three-valued verdict contract in code · C2 checks proven by
mutation/planted defect · C3 growth governed by flow (exits,
retirement) · C4 required writes at decision moments (computable
absence) · C5 verification independent of the generator in the
learning loop.

## Results

| repo | C1 | C2 | C3 | C4 | C5 | clean YES |
|---|---|---|---|---|---|---|
| a9650615/LLM_constitution (named) | NO | YES | part | part | part | 1 |
| rjmurillo/ai-agents (named) | YES | YES | part | YES | YES | 4 |
| Fareground/agent-knowledge | NO | NO | YES | part | YES | 2 |
| systemfsoftware/constitution | NO | NO | NO | YES | NO | 1 |
| vladimirrott/maintainer-agent | NO | YES | YES | YES | part | 3 |
| daniel-ospina/agent-infra | NO | NO | part | part | YES | 1 |
| eugenelim/agent-ready-repo | NO | NO | YES | YES | YES | 3 |

## The refined headline

The operator's prior (vocabulary without organs) holds for 4-5 of 7,
including the original named specimen. It is REVISED for two genuinely
strong twins with COMPLEMENTARY halves: **rjmurillo/ai-agents** holds
the verification organs (a merged-verdict contract that never coerces
unknown to pass; a mutation harness treating empty batteries, identity
mutations, missing anchors and timeouts as trust failures; blocking
Step-0 gates; independent debate review) while missing flow governance
— its own owner-filed issue #5698 the live proof (0 of 228 open issues
carry its spec's required answers). **eugenelim/agent-ready-repo**
holds the persistence organs (active/needs_review/retired lifecycle
enums with enumerated retirement reasons, successors and verified
coverage required before retirement; a blocking lint; and ADR-0082's
capture/distill/enquire authority split — raw observations cannot
become enquiry-visible without a guarded committed promotion) while
missing red-first and the third answer. **No repo holds both halves;
the combination remains unfound; C1 is the rarest organ (one
implementation in seven).**

## Convergence vs shared vocabulary (the lane's read)

Structural divergence under shared surface vocabulary: the twins'
actual designs differ substantially (CONST-IDs + YAML validation;
signed RFC wire spec; capture/distill/enquire modes; Ten Laws prose)
while sharing recurring boilerplate (P0/P1/P2 severity, PASS/FAIL/WARN
tokens, "fresh context"/"independent reviewer" phrasing, do/don't/check
tables) — reading as shared LLM-era governance boilerplate convention,
neither pure convergent evolution nor copying.

## Borrowables, each one line

1. **Tree-head-pinned receipts** (maintainer-agent): merge receipts
   bound to the exact tree head + production globs, so a rebase
   INVALIDATES the receipt — the check-anchoring rule as shipped
   mechanism; stale green evidence cannot survive.
2. **Contradictions kept attached, never overwritten** (Fareground):
   the audit trail is the data structure — independent arrival at the
   living record's belief design.
3. **Declared-vs-parsed ID cross-check** (systemfsoftware): the
   validator guards its own vacuous-parse mode — reach discipline in
   miniature.
4. **Capture/distill/enquire authority split** (agent-ready-repo,
   ADR-0082): three write-path authorities with guarded promotion —
   directly relevant to lc-229/admission design.
5. **merge_verdicts never-coerce + mutation trust-failure semantics**
   (rjmurillo): kin of laws 1/22 — worth a comparative read when the
   round designs the schema third answer.
6. **Vacuous-test taxonomy incl. the torn-read case** (agent-infra
   issue #820): an equality assertion true under every interleaving
   can never catch the race it names — proposes operation-history
   counting; enriches law 22's class. The issue itself is the purest
   external specimen of written-above-the-code-not-in-it.

Lane scratch (fetched files, tree listings, full codex transcript)
remains in the grading session's scratchpad under repos/ with an
INDEX.md, retrievable while that session's tmp dir survives.
