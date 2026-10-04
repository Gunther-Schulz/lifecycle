# Mitigations and design patterns against "answering from loaded context instead of literal input / recorded state"

Grading legend: [FETCHED] = I opened the source (abstract/page) via fetch; [SNIPPET] = only search-result text seen, source not opened; [VENDOR] = vendor-authored, unreplicated. Effect sizes are as the sources report them, not re-derived by me.

Repo cross-reference (from docs/answerable-not-felt.md, docs/the-loop.md, docs/purpose.md, which I read before writing): the repo already cites arXiv:2606.09863 (judge AUROC ceiling, which I independently fetched below), arXiv:2606.22528 (a rule absent from context moves violation 0% to 30-59%; lane-verified there, NOT opened by me), arXiv:2603.26993 (role separation over the same information is dominated; NOT opened by me) and arXiv:2605.09315 (erosion with accumulated rules; NOT opened by me). Treat those four as repo-sourced, not re-verified here.

## External state/memory architectures: measured reliability over long/multi-session horizons

### Takeaway
Evidence that external state (notes, files, structured summaries) preserves task state is mostly vendor engineering reports and vendor benchmark claims, not independent controlled studies. The one controlled study of repository context files (AGENTS.md) found NO reliable gain from loading them, a direct caution for the "loaded rules" leg. The strongest measured point is that structure with dedicated slots beat free-form regenerated summaries, and even the best system loses file/artifact state.

### Cited Findings
- AGENTS.md/CLAUDE.md-style repository context files do not generally improve task success and raise inference cost by over 20% on average; agents followed the instructions but extra exploration distracted them; useful mainly for non-standard practices; repository overviews unhelpful. [FETCHED] — [Gloaguen et al., arXiv 2602.11988](https://arxiv.org/abs/2602.11988)
- Reported split by source (secondary summary): human-written files about +4%, LLM-generated about -2%. [SNIPPET] — [DAIR academy summary](https://academy.dair.ai/blog/agents-md-evaluation)
- Factory's probe-based comparison of context compression, 36,611 production messages, LLM judge (GPT-5.2) on 0-5 rubric: structured summarization with fixed sections overall 3.70 vs Anthropic built-in 3.44 vs OpenAI compact 3.35; artifact/file-tracking weakest for all (2.19-2.45); "structure forces preservation"; OpenAI compaction lost nearly all technical detail at 99.3% reduction. [FETCHED, VENDOR; scored by an LLM judge, see the verification section on judge limits] — [Factory](https://factory.com/news/evaluating-compression)
- Anthropic describes structured note-taking (notes persisted outside the context window and retrieved later; todo list; a Pokemon agent keeping tallies across context resets) alongside compaction and sub-agents as its long-horizon techniques. No effect sizes given. [SNIPPET, VENDOR] — [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- Manus: file system as "ultimate context", restorable compression (drop content, keep URL/path), and a rewritten todo.md "recited" at the end of context to counter goal drift over about 50 tool calls. Practitioner report, no measurement. [SNIPPET, VENDOR] — [Manus lessons summary](https://agentic-ai.readthedocs.io/en/latest/ContextEngineering/manus/)
- Letta claims a plain filesystem of stored conversation scores 74.0% on LoCoMo, beating specialized memory libraries; Mem0 claims 92.5 on LoCoMo. Competing vendor numbers on the same benchmark. [SNIPPET, VENDOR] — [Letta](https://www.letta.com/blog/benchmarking-ai-agent-memory/); [Mem0](https://mem0.ai/blog/state-of-ai-agent-memory-2026)

### Inferences
- Lifecycle's design (persisted record plus demands) sits on the Factory/Manus side: named slots, restorable pointers. The AGENTS.md result is evidence against relying on the always-loaded-rules leg; it does not test demands at seams.
- Letta/Mem0 numbers are not usable as evidence for lifecycle: they measure conversational QA recall, not project-state fidelity, and the vendors contradict each other.
- Factory's weakest dimension (artifact trail, 2.19-2.45 of 5) matches lifecycle's premise that file/state facts must come from an environment-side record, not a summary.

### Gaps
- No independent controlled study found of agent memory systems (MemGPT/Letta, A-MEM) on multi-session coding or project-state fidelity; the MemGPT and A-MEM papers were not opened.
- Anthropic and Manus claims carry no ablation numbers.

## Read-at-moment-of-application: does WHEN retrieval fires matter more than WHAT is stored?

### Takeaway
Adjacent evidence supports seam-time retrieval, but I found no study that directly compares session-start loading with decision-seam retrieval for agent project state. Support is indirect: multi-time retrieval beats one-shot in RAG, position in context changes use of information, and instruction load degrades following.

### Cited Findings
- Active retrieval during generation (FLARE, Self-RAG) retrieves when needed and repeatedly; a survey statement is that multi-time retrieval outperforms single-time retrieval for long-form generation. [SNIPPET, secondary] — [Unified Active Retrieval, arXiv 2406.12534](https://arxiv.org/pdf/2406.12534)
- Lost in the Middle: accuracy highest when relevant information is at the start or end of context, degrading by more than 30% when in the middle (U-shape); tested on older models with multi-document QA and key-value retrieval. [SNIPPET for the 30% figure; the paper is peer reviewed, TACL] — [Liu et al.](https://arxiv.org/abs/2307.03172)
- IFScale: 20 models, up to 500 keyword instructions; best frontier model 68% at maximum density; omission is the dominant error; bias toward earlier instructions; decay shapes differ (threshold vs linear). [SNIPPET] — [Jaroslawicz et al., arXiv 2507.11538](https://arxiv.org/pdf/2507.11538)
- Chroma "context rot": 18 models all degrade with input length even on simple tasks; distractors worsen it. [SNIPPET, VENDOR; Chroma sells a vector database] — [Chroma](https://www.trychroma.com/research/context-rot)
- Manus todo.md recitation places objectives at the end of context to exploit recency. [SNIPPET, VENDOR, unmeasured] — see previous section.

### Inferences
- All of these point the same way: instructions and state present somewhere in a long context are used unreliably, depending on position and load. This supports re-presenting the relevant record entry at the decision point, but it is inference from adjacent results, not a measured test of the lifecycle design.
- IFScale measures density of simultaneous instructions; a seam that surfaces only the entries relevant to one decision lowers density versus a full-rules load. Inference.
- A caution that none of these results tests: if the seam relies on the model noticing it needs the record, it inherits the fluency problem (repo docs state this as the felt-insufficiency mechanism). The retrieval literature above (FLARE, Self-RAG) triggers on model confidence or reflection tokens, which is model-side triggering; lifecycle's environment-side seam trigger has no direct counterpart in what I found.

### Gaps
- No direct experiment of "inject at seam" vs "load at start" on coding-agent fidelity. This is a candidate for lifecycle's own measurement.
- Lost-in-the-Middle results are from 2023-era models; a current-model replication was not located.

## Structured demands: required slots/schemas vs instructions/reminders

### Takeaway
I found no study showing required-write slots outperform instructions on fidelity. What exists is mixed: format constraints can HURT reasoning, while environment-side checks that fire only on definite defects helped coding agents modestly.

### Cited Findings
- "Let Me Speak Freely?": constrained decoding (JSON mode) hurt reasoning tasks most, format-restricting instructions less, natural language best; constraints helped classification; looser formats reduced the harm; generating in natural language first then converting (NL-to-format) mitigated it. [SNIPPET] — [Tam et al., arXiv 2408.02442](https://arxiv.org/abs/2408.02442)
- SWE-agent: the edit command rejects edits that introduce lint errors; the linting guardrail recovers about 3 percentage points over the same interface without linting; interface design raised resolve rate (GPT-4 Turbo: 18.00% vs 11.00% shell-only on SWE-bench Lite). [SNIPPET] — [SWE-agent, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/5a7c947568c1b1328ccc5230172e1e7c-Paper-Conference.pdf)
- Factory's observation that dedicated summary sections prevent silent drift. [FETCHED, VENDOR] — see first section.
- Re-Reading (Re2) and Rephrase-and-Respond: re-reading or rephrasing the input improves reasoning on benchmarks; effect sizes not retrieved. [SNIPPET] — [Re2, EMNLP 2024](https://aclanthology.org/2024.emnlp-main.871/); [RaR](https://www.emergentmind.com/papers/2311.04205)

### Inferences
- Hard environment-side gates that fire only on certain defects (SWE-agent lint) have a measured, modest positive effect; this supports lifecycle's "cannot be passed unanswered" gates where the trigger is computable.
- The Tam et al. result is a warning for slot design: a rigid schema imposed inside the reasoning step can reduce reasoning quality; making the demand a separate write step (the NL-to-format pattern) is the safer shape. Inference from reasoning tasks, not tested on record-keeping.

### Gaps
- No A/B of "required slot" vs "reminder" on fidelity located. Checklist-as-gate literature (LLM checklist studies, human clinical/aviation analogues) was not searched.

## Literal-input preservation: read-back, restatement, verbatim quoting

### Takeaway
Re-reading or restating the input improves benchmark reasoning (Re2, RaR), but I found no measurement of restatement-checked-against-source on agent task fidelity. The multi-turn degradation paper documents the targeted failure: early wrong assumptions the model keeps relying on.

### Cited Findings
- Multi-turn: average 39% drop vs single-turn across six generation tasks; about -15% aptitude but +112% unreliability; models make assumptions early, attempt final answers prematurely, and rely on earlier answers; reasoning models also affected; "when LLMs take a wrong turn in a conversation, they get lost and do not recover". [FETCHED abstract] — [Laban et al., arXiv 2505.06120](https://arxiv.org/abs/2505.06120)
- Re2 processes the question twice, rationale given as more computation on input encoding; RaR has the model rephrase the query. [SNIPPET] — links above.
- Self-Correction Bench: models fix errors attributed to a user but miss identical errors in their own output (average blind-spot rate 64.5% over 14 non-reasoning models); appending "Wait" cut the blind spot by 89.3%; fine-tuning on 5,306 error-correction sequences cut it by 76.0%. [FETCHED] — [Tsui, arXiv 2507.02778](https://arxiv.org/abs/2507.02778)

### Inferences
- The attribution effect in Self-Correction Bench suggests a check is more likely to catch a divergence if the text is presented as external to the model (the operator's literal words, a persisted record entry) than as its own earlier output. Inference from one paper, on non-reasoning models.
- A mechanical comparison of the model's restatement against the source text, run by the environment, avoids relying on the model grading its own restatement. Inference; not tested.
- Substitution as defined in the repo (reading new input through loaded context) is not what Re2/RaR measure; they test comprehension of a single question, not interference from a rich window. The transfer is untested.

### Gaps
- No study found measuring read-back or verbatim-quote demands on coding or planning task fidelity. The multi-turn paper's mitigation tests (recap, concatenation) were not visible in the fetched excerpt.

## Verification architectures: independent signal vs self-review vs judge-over-prose

### Takeaway
The brief's "AUROC ~0.65 ceiling" is sourced: one study found no LLM-judge configuration above 0.65 at detecting false success on tau2-bench, and 0.54 on AppWorld traces. The consistent field pattern is that self-correction works with reliable external feedback and not with the model's own feedback, and that cheap non-LLM detectors beat LLM judges on the same task.

### Cited Findings
- False-success study: 9,876 tau2-bench and 1,879 AppWorld trajectories; five judges by five prompt strategies including the full task specification: max AUROC 0.65 on tau2-bench and 0.54 on AppWorld API traces; TF-IDF detectors 0.83 and 0.95; judges rely on confident closing language rather than verified state; lightweight detectors recover 4-8x more false successes. [FETCHED] — [arXiv 2606.09863](https://arxiv.org/abs/2606.09863)
- Huang et al.: intrinsic self-correction without external feedback does not improve and sometimes degrades reasoning; prior positive results used oracle labels. [SNIPPET] — [arXiv 2310.01798](https://arxiv.org/abs/2310.01798)
- Kamoi et al. survey: no prior work shows successful self-correction with feedback from prompted LLMs except in tasks especially suited to it; self-correction works with reliable external feedback; the bottleneck is generating feedback, not refining. [SNIPPET] — [TACL survey](https://aclanthology.org/2024.tacl-1.78/)
- CRITIC: tool-interactive verification (search, code interpreter) improves QA, program synthesis and toxicity reduction. [SNIPPET] — [arXiv 2305.11738](https://arxiv.org/abs/2305.11738)
- Cross-Context Review (fresh-session reviewer, 30 artifacts, 150 injected errors): F1 28.6% vs 21.7% for repeated same-session self-review (p<0.001 in the first run; Holm-adjusted p=0.004 across the three-run average), but NOT significantly better than single same-session self-review (27.1%, p=0.26) or context-aware subagent review (23.8%, p=0.057); the authors retracted an earlier claim that the ranking held in all runs. [FETCHED] — [arXiv 2603.12123](https://arxiv.org/abs/2603.12123)
- LLM-judge biases: position, verbosity, self-preference (attributed to perplexity/familiarity); judges struggle when they cannot answer the question themselves; GPT-4 judge agrees with humans over 80% on MT-Bench, a chat-quality task, not state verification. [SNIPPET] — [Zheng et al.](https://arxiv.org/pdf/2306.05685); [Wataoka et al.](https://arxiv.org/abs/2410.21819)
- trajectory-judge: an outcome-only LLM judge catches 84% of loud faults but 45% of silent ones with 33% false alarms; a step-rubric judge reaches 77% silent recall at 3x cost. Synthetic environment, preprint. [SNIPPET] — [arXiv 2609.00038](https://arxiv.org/pdf/2609.00038)

### Inferences
- Fresh-context review has weak, run-unstable evidence: it beat repeated same-session review but not single self-review or subagent review, on a small set with injected errors. That is mixed support for a fresh-context mechanism; the repo's own desk/peer finding (independent artifact reads, not role separation) is the better-supported framing.
- The strongest, most consistent pattern is checks against state or tool output (CRITIC, TF-IDF over trajectories, lint) rather than a judge reading prose. This matches lifecycle's demands against the record.
- The 0.65 result is false-success detection on two agent benchmarks; do not generalize it to other judging tasks (the 80% MT-Bench agreement is a different task).

### Gaps
- No direct comparison of fresh vs same-context reviewer on project-state or decision-record violations found.
- Self-Refine and Reflexion critiques were not searched separately.

## Context hygiene: resets, compaction hazards, less context

### Takeaway
Evidence consistently shows longer context and conversation depth degrade reliability, and compaction loses specifics (file trail, technical detail) even when overall quality is acceptable. I found no controlled study showing that a reset from persisted carriers beats compaction on instruction fidelity; that posture is plausible by inference, not measured.

### Cited Findings
- Chroma: all 18 models degrade with input length; distractors compound. [SNIPPET, VENDOR] — [Chroma](https://www.trychroma.com/research/context-rot)
- Multi-turn paper: unreliability, not aptitude, drives the 39% drop; wrong early turns are not recovered. [FETCHED] — [arXiv 2505.06120](https://arxiv.org/abs/2505.06120)
- Factory: all compression methods weak on artifact trail (2.19-2.45 of 5); structured, anchored iterative summaries (only the newly truncated span summarized and merged into persistent sections) scored best. [FETCHED, VENDOR] — [Factory](https://factory.com/news/evaluating-compression)
- AGENTS.md study: more loaded context raised cost 20%+ without a success gain. [FETCHED] — [arXiv 2602.11988](https://arxiv.org/abs/2602.11988)
- Two 2026 preprints surfaced in search but were not opened: one on interaction costs of context compression, one on engineering reliable coding agents. [SNIPPET, unread] — [arXiv 2608.16370](https://arxiv.org/pdf/2608.16370); [arXiv 2608.13867](https://arxiv.org/pdf/2608.13867)

### Inferences
- "Less loaded context improves fidelity" is supported by length-degradation, IFScale and the AGENTS.md null result; it was not shown for project-rule fidelity specifically.
- Factory shows a persisted structured record with named sections outperforms free-form regenerated summaries; this supports restart-from-carriers if the carrier is structured, but Factory compared summarizers, not reset vs compaction.

### Gaps
- No controlled reset-vs-compaction experiment located; the two unopened preprints (2608.16370, 2608.13867) may bear on it and should be read by whoever continues.
- Chroma and Factory are vendors; no independent replication found.

## Cross-cutting: adopt / avoid, graded

- ADOPT, strong: verification against external state or tool output, not an LLM reading prose (CRITIC, Huang, Kamoi, false-success AUROC study). Basis: several peer-reviewed papers plus one large trajectory study.
- ADOPT, moderate: hard guardrails with near-100% precision at the action site (SWE-agent lint, about +3 points). One study, modest effect.
- ADOPT, moderate-weak: structured persistent summaries with fixed slots (Factory; vendor, LLM-judged).
- AVOID, moderate: relying on loaded rule or context files for fidelity (AGENTS.md null result, IFScale density, length degradation).
- WATCH, moderate: rigid schemas constraining the reasoning output itself (Tam et al.); keep the demand a separate write step.
- AVOID, strong: model self-review of its own prose as the only check (Huang, Kamoi, Self-Correction Bench blind spot).
- UNPROVEN: fresh-context review as a general fix (Cross-Context Review: run-unstable, not significant vs single self-review).
- UNMEASURED anywhere I looked: seam-time retrieval vs start-time loading; read-back or verbatim demands on agent fidelity; reset vs compaction.
