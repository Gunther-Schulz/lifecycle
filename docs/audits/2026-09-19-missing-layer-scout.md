# The missing-layer scout — agent-layer landscape + augmentation lineage

**2026-09-19, sonnet discovery lane (sonnet-framework-scout's sibling,
sonnet-layer-scout), commissioned at driving desk cachyos-setup-b3 on the
operator's direction: concept BORROWING, explicitly not novelty-proofing.
Two axes the prior three surveys (literature, tooling, process frameworks)
did not cover. Every claim marked VERIFIED (web-checked, source named) or
PARAMETRIC (titles/abstracts or training knowledge, not opened) by the
lane; relayed verbatim-in-substance at the driving desk, which read all
five parts. Landed to the repo at the desk gap; design-round input.**

## Axis 1 — the contemporary agent-layer landscape (6 clusters)

1. **Tiered/hierarchical memory (MemGPT/Letta).** OS-style paging — core
   (in-context, editable), recall (searchable history), archival (vector
   store); the LLM itself moves data between tiers (VERIFIED, arXiv
   2310.08560; letta.com/blog/agent-memory). Failure mode: where the
   control logic sits materially changes what gets forgotten (follow-on
   papers exist on control-plane placement and retrieval bottlenecks —
   PARAMETRIC, title-inferred).
2. **Context engineering / compaction.** Two content-agnostic heuristics
   dominate — reactive (near token budget) and periodic — plus rule-based
   context editing and a real-time remaining-budget signal (VERIFIED,
   Anthropic eng blog 2025-09-29). Failure mode: both heuristics are blind
   to trajectory content; ungrounded compaction silently drops high-signal
   tokens (PARAMETRIC, title-inferred).
3. **Skill/procedure libraries (Voyager).** Automatic curriculum +
   ever-growing library of executable composable skill-code + iterative
   prompting from env feedback (VERIFIED, arXiv 2305.16291). Measured:
   3.3x unique items, 2.3x distances, milestones up to 15.3x faster than
   prior SOTA (VERIFIED). Failure mode: skills added only on success,
   never refined — the SAGE successor exists to patch exactly that
   (PARAMETRIC).
4. **Agent workflow durability (Temporal-class).** Deterministic,
   replayable, event-sourced workflow code split from individually-retried
   nondeterministic activities; every transition recorded, crash resumes
   exactly (VERIFIED, temporal.io + secondary). Failure mode: durability
   does not eliminate failure — non-determinism creeping into "deterministic"
   code, replay mismatches (PARAMETRIC, title-inferred).
5. **Reflection/lesson stores (Reflexion).** Actor / Evaluator /
   Self-Reflection model split; scalar feedback converted to a verbal
   lesson stored episodically — no weight updates (VERIFIED, arXiv
   2303.11366). Measured: +8 points absolute over episodic-memory-alone
   (VERIFIED). Failure mode: naive accumulation of every reflection;
   Meta-Policy Reflexion adds an ADMISSION-CONTROL gate before a lesson
   enters the reusable store (PARAMETRIC).
6. **Multi-agent failure taxonomy (MAST).** Grounded-theory taxonomy,
   150+ traces, kappa=0.88: 14 failure modes in 3 categories — system
   design, inter-agent misalignment, TASK VERIFICATION failures (VERIFIED,
   arXiv 2503.13657). Measured at 1600+ traces / 7 frameworks: **79% of
   failures trace to specification/coordination problems, not base-model
   capability limits** (VERIFIED — the strongest-evidence finding of the
   scout).

## Axis 2 — the augmentation lineage (6 concepts)

1. **Engelbart ABC.** A does the work; B improves how; C improves the
   improving — C-level is what compounds (VERIFIED). Degenerate: NLS
   over-invested in B/C tooling never adopted for daily A-level work
   (PARAMETRIC).
2. **Bush's memex.** Associative TRAILS as the durable, shareable stored
   unit — not just endpoints (PARAMETRIC). Degenerate: trails never
   re-traversed are an unindexed pile (PARAMETRIC).
3. **Zettelkasten (Luhmann).** Anti-categories: ~90k slips organized by
   sequencing/linking + an index of ENTRY POINTS only, no folders; a
   "communication partner" because link-navigation surfaces unanticipated
   connections a category tree cannot (VERIFIED, zettelkasten.de).
   Degenerate: the Collector's Fallacy — accumulation mistaken for
   integration; auto-backlinking graphs where everything connects and
   nothing is discoverable (VERIFIED).
4. **Exocortex.** Externalized cognition consulted MID-DECISION, not
   archival — only works wired into the decision moment (PARAMETRIC).
   Degenerate: the write-only dump (PARAMETRIC).
5. **Evergreen notes (Matuschak).** Atomic, concept-oriented, densely
   linked, continuously REWRITTEN — never write-once logs (PARAMETRIC).
   Degenerate: the note-graveyard — captured once, never synthesized
   (PARAMETRIC).
6. **Incremental/spaced surfacing.** Material resurfaces on a cadence tied
   to its own decay/utility — a priority queue, not a flat archive
   (PARAMETRIC). Degenerate: the scheduling apparatus becomes the work
   (PARAMETRIC).

## Top 5 borrowables, ranked (lane's ranking, mapped to our pieces)

1. **MAST's 79% + task-verification category** (VERIFIED, largest n) →
   independent verification checks SPEC-ADHERENCE and inter-step
   coordination, not just output correctness — that is where the measured
   failure mass is.
2. **Luhmann's anti-categories / communication-partner** (VERIFIED) → the
   always-visible index is a dense set of linked ENTRY POINTS navigated at
   a decision moment, never a category tree.
3. **Voyager's success-gated accretion + SAGE's named refinement gap** →
   self-authored procedures adopt add-on-success but budget a periodic
   refinement/pruning pass explicitly — the base mechanism has none by
   design.
4. **Reflexion's +8pt lesson store + admission-control fix** → gate what
   enters the lesson/ledger store; the Collector's Fallacy recurred
   independently in Axis 1.
5. **Engelbart's ABC** → C-level ("improving the improving") instrumented
   as its own explicit seam — the direct ancestor of
   runbook-authoring-at-close and the meta loop.

## Convergent principles (both lineages independently; safest borrows)

- Links/graphs beat hierarchical categorization for material queried in
  unanticipated contexts.
- Memory earns value only when surfaced AT the decision point — never
  merely archived.
- **Accumulation-without-integration is the dominant failure mode,
  discovered independently three times** (Collector's Fallacy; unrefined
  Voyager skills; un-admitted Reflexion noise) — a refinement/pruning pass
  is a first-class component, not an afterthought.
- Improving the process is its own NAMED activity, distinct from doing the
  work.
- State is an explicit, replayable record — never a reconstructed summary.
- Verification is architecturally separate from production — never sharing
  a pass with the work it checks.

## Driving-desk grading (added at relay, marked as the desk's)

Six of six convergent principles match mechanisms this repo already holds
or has designed (two-stage retrieval; O6/presence; retirement + kaemmung;
the meta loop; restart-over-compact; the desk split + verify) — external
convergence at confirmation strength, not novelty. The genuinely NEW
emphases: MAST's spec-adherence focus for the verifier designs; Luhmann's
entry-points-not-taxonomy for the index's shape; and the NLS degenerate
form as a caution aimed squarely at this arc — B/C-level investment that
daily A-level work never adopts. The admission-control and pruning
borrowables are confirmatory (the mint bar and retirement triggers exist);
their independent triple-discovery upgrades their standing from house rule
to cross-domain law.

Sources actually read by the lane: arXiv 2310.08560, 2305.16291,
2503.13657, 2303.11366; letta.com; Anthropic eng blog (2025-09-29);
temporal.io; dougengelbart.org; zettelkasten.de; Ernest Chiang's Luhmann
writeup. All PARAMETRIC items unopened this session.
