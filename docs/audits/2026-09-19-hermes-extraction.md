Hermes discovery — findings (read-only dispatch, no repo writes)

## 1. Identification

**Primary:** Hermes Agent by Nous Research — `github.com/NousResearch/hermes-agent`, official site `hermes-agent.nousresearch.com`. Open-source, self-hosted, MIT-licensed autonomous agent explicitly marketed as "the self-improving AI agent" with a "built-in learning loop." Released Feb 2026; reported 140k+ GitHub stars within three months (self-reported/press, not independently checked here).

**Alternates found, named but not fetched:**
- `NousResearch/hermes-agent-self-evolution` — a separate add-on repo doing evolutionary self-improvement of Hermes's own skills/prompts/code via DSPy + GEPA (genetic prompt optimization) — the closest thing to actual weight/behavior-search-space learning, distinct from the base agent's runtime skill/memory system.
- Nous Research's older "Hermes" model lineage (Hermes 2/3/4 — fine-tuned LLM checkpoints) is a *different* project under the same org/name; not agentic, not fetched, noted only to avoid confusion since the org overloads the name.
- `mudrii/hermes-agent-docs` and `0xNyk/awesome-hermes-agent` — third-party doc/directory mirrors, not authoritative, not fetched.

## 2. Extraction — codex gpt-5.6-luna, verbatim (read-only, cwd = my scratch dir with README.md + llms.txt + 13 extracted doc sections; clean run, no quota kill, 74,169 tokens)

### (a) Where learning or memory lives

Hermes does not describe online fine-tuning or updates to model weights. Its learning is implemented through prompt context plus external files/databases.

- Built-in persistent memory lives in `~/.hermes/memories/MEMORY.md` and `USER.md`. `MEMORY.md` stores agent notes; `USER.md` stores the user profile. They are injected into the system prompt at session start as a frozen snapshot. (`sec-PersistentMemory.md`)
- Session history is stored externally in SQLite at `~/.hermes/state.db`, with FTS5 search. The agent can retrieve prior messages through `session_search`; this is not summarized into weights. (`sec-PersistentMemory.md`, `sec-SessionStorage.md`, `sec-Architecture.md`)
- Skills are procedural knowledge stored as Markdown files, normally under `~/.hermes/skills/`. They are listed compactly and loaded into context on demand through `skill_view`. (`sec-SkillsSystem.md`, `sec-WorkingWithSkills.md`)
- Optional external memory providers store and retrieve knowledge through systems such as Honcho, OpenViking, Mem0, Hindsight, and others. They inject retrieved context and provide memory tools. (`sec-MemoryProviders.md`)
- Context compression summarizes or prunes conversation history to fit the model's context window. This changes the active prompt, not model weights. (`sec-ContextCompressionCaching.md`)
- Batch processing can generate trajectories for later fine-tuning or evaluation, but the supplied documentation does not say that Hermes itself fine-tunes its live model. (`sec-BatchProcessing.md`)

The README's "learning loop" means "creates skills from experience," "persists knowledge," and searches past conversations — not weight updates. (`README.md`, `llms.txt`)

### (b) Staleness, pruning, and verification mechanisms

- Built-in memory is bounded by character limits: 2,200 characters for `MEMORY.md` and 1,375 for `USER.md`. It does not auto-compact. If a write exceeds the limit, the tool errors and the agent must consolidate or remove entries before retrying. (`sec-PersistentMemory.md`)
- The memory tool supports `add`, `replace`, and `remove`; the documentation explicitly suggests removing stale or less important entries when memory is full. Exact duplicates are rejected. (`sec-PersistentMemory.md`)
- A deterministic memory security scan rejects entries containing prompt-injection, exfiltration, SSH-backdoor patterns, or invisible Unicode. (`sec-PersistentMemory.md`)
- The curator tracks skill use, views, patches, and inactivity. It deterministically transitions skills from active to stale and then archives long-unused skills. The curator never automatically deletes them; archives remain recoverable under `.archive/`. (`sec-Curator.md`)
- Curator pruning is deterministic and does not require an LLM. Optional consolidation is LLM-driven and may patch, merge, or archive skills. It is off by default. (`sec-Curator.md`)
- Pinned skills and skills referenced by cron jobs are protected from automatic transitions. Hub-installed skills are excluded from curator mutation. (`sec-Curator.md`)
- Archived skills can be restored. Curator consolidation has backups, an append-only mutation ledger, and rollback support. Archive purging is explicit rather than automatic. (`sec-Curator.md`)
- Skills can become stale through external change: users are told to update skills when they stop reflecting reality. Hub updates skip locally edited skills unless `--force`. (`sec-WorkingWithSkills.md`, `sec-SkillsSystem.md`)
- NVIDIA SkillEvaluator is described as an advisory scan, not a learning-quality benchmark. (`sec-SkillsSystem.md`)
- Context compression deterministically prunes old tool outputs and summarizes older conversation turns with an auxiliary LLM; soft-archived session messages remain searchable/recoverable rather than deleted. (`sec-ContextCompressionCaching.md`)

### (c) Independent verification versus self-checking

Self-checking / same-context mechanisms:
- The normal background learning review runs on the main chat model **by default** and replays the conversation — same model, same reasoning settings, same system prompt/tools, same conversation snapshot, unless routed to a different model explicitly. (`sec-PersistentMemory.md`)
- Curator consolidation is another auxiliary-model review; "auto" routing sends it to the main model too. (`sec-Curator.md`)
- Skill-embedded verification steps ("run check-command") are executed and interpreted by the same agent using the skill. (`sec-WorkingWithSkills.md`, `sec-CreatingSkills.md`)
- Honcho's "self-audit"/"reconciliation" passes are additional LLM passes inside the provider's own reasoning, not an independent verifier. (`sec-MemoryProviders.md`)

Independent / non-LLM checks:
- Memory-entry security scanning is a deterministic pre-write check. (`sec-PersistentMemory.md`)
- Skill security scanning (prompt injection, credential exfiltration, destructive commands, shell injection); NVIDIA SkillEvaluator as optional advisory scanner. (`sec-CreatingSkills.md`, `sec-SkillsSystem.md`)
- Protected-path checks, write sandboxes, dangerous-command blocklists, malformed-command checks, and pre-execution scanning are separate security mechanisms, not the generating model judging its own prose. (`sec-Security.md`)
- A file-mutation verifier can report what actually happened on disk, independently of the model's closing claim that an edit succeeded. (`sec-Security.md`)
- Human approval acts as an independent reviewer for gated memory writes, skill writes, and dangerous commands when those gates are enabled. (`sec-PersistentMemory.md`, `sec-Security.md`, `sec-SkillsSystem.md`)

### (d) Claims versus what is measured

Claims (README/index): "the self-improving AI agent," "built-in learning loop," agent-curated memory, periodic nudges, autonomous skill creation, self-improving skills, FTS5 cross-session recall, a "deepening model" of the user.

What's actually measured in the docs supplied:
- Batch runs record API-call counts, tool-call counts, tool success/failure rates, tool errors, reasoning coverage, discarded samples, duration. (`sec-BatchProcessing.md`)
- Batch processing can run an arbitrary JSONL eval suite producing `statistics.json`, but no standard benchmark dataset is named there. (`sec-BatchProcessing.md`)
- Prompt-caching and session-storage token-usage metrics exist. (`sec-AgentLoopInternals.md`, `sec-ContextCompressionCaching.md`, `sec-SessionStorage.md`)
- An approximate "3-5x" cost-reduction figure for routing background reviews to a cheaper model is mentioned, with no benchmark name or methodology. (`sec-PersistentMemory.md`)
- The only named external eval/security tool is NVIDIA SkillEvaluator, described as an advisory skill scan. (`sec-SkillsSystem.md`)

Luna checked README.md, llms.txt, and every supplied sec-*.md and reports: **none of the fetched files name TerminalBench2, HermesSweEnv, SWE-bench, MMLU, or any other standard task benchmark** — those names came from the *dispatch brief's own candidate list*, not from anything luna found in the fetched material. I re-checked this directly by grepping all sec-*.md files for those four terms: zero hits, confirming luna's negative is correct for the material it was actually given. (TerminalBench2 and HermesSweEnv do appear elsewhere in the full ~4.8MB docs dump — in a subagent-sandboxing passage about per-task Docker image overrides, well outside the 13 sections I selected and handed to codex — so a broader read of the site would surface them, but nothing in luna's actual input set did, and its answer is not a miss.)

### (e) Role of the human operator

Not a reviewer-of-everything; combines autonomous operation with specific gates.
- Human supplies initial conversation, preferences, corrections, task direction; the agent then autonomously reviews conversations and proposes/writes memories and skills. (`README.md`, `sec-PersistentMemory.md`)
- Dangerous terminal commands require explicit approval by default (once/session/permanent/deny); timeouts fail closed. An always-on hardline blocklist refuses catastrophic commands even under YOLO mode or approval. Protected-path writes are hard-blocked with no prompt. (`sec-Security.md`)
- Memory writes are autonomous by default; `memory.write_approval: true` stages them for human approval. Same pattern for skill writes via `skills.write_approval: true`. (`sec-PersistentMemory.md`, `sec-SkillsSystem.md`)
- Curator pruning runs automatically without per-transition approval, but stays reversible (archived, not deleted; consolidation has rollback). (`sec-Curator.md`)
- Installing a suggested automation "blueprint" requires explicit human acceptance. (`sec-CreatingSkills.md`)
- Messaging-platform users must pass authorization/pairing gates before interacting with the gateway. (`sec-Security.md`)

## 3. My own note on what codex/luna missed or overstated

**Overstated inconsistency in (b).** Luna claims: "The curator's documentation is internally inconsistent about thresholds... a later lifecycle passage says 30 days to stale and 90 days to archive." I checked `sec-Curator.md` directly — **this "30/90" pairing does not appear anywhere in the file**. The deterministic defaults are unambiguously 14 days stale / 30 days archive (lines 33, 53-54, and the `curator prune --days N` default). Separately, an unrelated passage about *adopting* long-idle unmanaged skills says adoption "does not buy it a fresh 90-day window" (line 264) — a loose turn of phrase with no matching config default in the file (the closest real 90 is a `curator purge --days 90` one-off CLI override example, and `archive_ttl_days` defaults to 180). There is a genuine minor documentation loose end (an undefined "90-day window" reference), but luna's framing of it as a second, contradicting 30/90 threshold pair is not supported by the text — it invented the pairing rather than quoting it.

(I initially drafted a second note here claiming luna missed "TerminalBench2"/"HermesSweEnv" in the fetched text — I re-checked by grepping the actual 13 sec-*.md files handed to codex before sending and found zero hits for those terms in that set; the mention I remembered was in an unrelated part of the original ~4.8MB docs dump that I did not select or hand to codex. Correcting myself: luna's negative on those two names was accurate for its actual input, not a miss. Noted here rather than silently dropped, since the retraction is itself part of the record.)

## 4. Sources fetched

- `https://raw.githubusercontent.com/NousResearch/hermes-agent/main/README.md`
- `https://hermes-agent.nousresearch.com/llms.txt` (doc index)
- `https://hermes-agent.nousresearch.com/llms-full.txt` (~4.8MB full docs concatenation — downloaded once, then sliced by heading boundaries into the 13 `sec-*.md` files luna read: Security, SkillsSystem, Curator, PersistentMemory, MemoryProviders, Architecture, AgentLoopInternals, ContextCompressionCaching, SessionStorage, CreatingSkills, WorkingWithSkills, TrajectoryFormat, BatchProcessing; the raw combined file was deleted after slicing to keep the scratch dir small)

All sliced files remain in the probing session's scratchpad (hermes/, session-local, mortal) if the judgment desk wants to re-open any of them.
