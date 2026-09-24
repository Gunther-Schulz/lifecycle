# Prior art, problem side: practitioner tools

**Provenance.** Codex lane (gpt-5.6-luna, `codex exec -s read-only`, live web search), commissioned 2026-09-24 by session dev-17 (996fa1b7) on the operator's direction: search from the PROBLEM side, not our mechanism vocabulary. 53 web searches, 273,326 tokens. The body below is the lane's final message VERBATIM; its [VERIFIED]/[UNVERIFIED] marks are the LANE's own grades (lane-verified: it says it opened the URL), not desk-verified. Desk checks and grading: `2026-09-24-prior-art-problem-side-synthesis.md`. The lane's angle prompt is reproduced at the end.

---

## Headline

- Practitioner systems mostly persist tasks, specifications, and instructions—not the full causal history of agent work. [VERIFIED: https://github.com/gastownhall/beads] [VERIFIED: https://github.com/github/spec-kit] [VERIFIED: https://code.claude.com/docs/en/memory]
- Mechanical enforcement is usually limited to schemas, dependency state, file discovery, task gates, or hooks. Most behavioral rules remain prompt prose. [VERIFIED: https://code.claude.com/docs/en/memory] [VERIFIED: https://cursor.com/docs/rules] [VERIFIED: https://aider.chat/docs/usage/conventions.html]
- Staleness is a recurring, reported failure: stale generated instructions, cached task state, ignored conventions, old memory, and standards drifting from code. [VERIFIED: https://github.com/gastownhall/beads/issues/2139] [VERIFIED: https://github.com/eyaltoledano/claude-task-master/issues/348] [VERIFIED: https://github.com/Aider-AI/aider/issues/2384] [VERIFIED: https://github.com/anthropics/claude-code/issues/85075]
- Within-session focus is addressed best by isolated subtasks, explicit task waves, context-sized plans, and verification loops. [VERIFIED: https://roocodeinc.github.io/Roo-Code/features/boomerang-tasks/] [VERIFIED: https://kiro.dev/docs/specs/] [VERIFIED: https://github.com/karausm/GSD]
- The strongest borrowable pattern is: append-only evidence plus a generated current view, with freshness/version checks and lifecycle hooks. [VERIFIED: https://github.com/rosehgal/handoff] [VERIFIED: https://github.com/bmad-code-org/BMAD-METHOD] [VERIFIED: https://github.com/gastownhall/beads/issues/2139]

## Findings

### Beads

URL: https://github.com/gastownhall/beads [VERIFIED: https://github.com/gastownhall/beads]

Beads is a distributed, dependency-aware issue tracker for coding agents, backed by Dolt. [VERIFIED: https://github.com/gastownhall/beads] It persists structured tasks, dependencies, statuses, claims, memories, and graph relationships in a project-local `.beads` store. [VERIFIED: https://github.com/gastownhall/beads]

Its mechanical layer is unusually strong: task IDs, dependency tracking, ready/blocked calculations, status transitions, JSON output, and generated agent instructions. [VERIFIED: https://github.com/gastownhall/beads] It supports session initialization through `bd prime` and integrations in `AGENTS.md`. [VERIFIED: https://github.com/gastownhall/beads]

The repository showed approximately 27.4k stars when read on 2026-09-24. [VERIFIED: https://github.com/gastownhall/beads]

The project reports important staleness failures: overlapping initialization mechanisms can leave static `AGENTS.md` instructions outdated, while stale Dolt locks can make `bd prime` hang during session startup. [VERIFIED: https://github.com/gastownhall/beads/issues/2139] [VERIFIED: https://github.com/gastownhall/beads/issues/3701]

Problem addressed: both cross-session continuity and within-session drift. [VERIFIED: https://github.com/gastownhall/beads]

Borrowable: a typed task graph, explicit claim/dependency state, dynamic session injection, and hash/version checks around generated instructions. [VERIFIED: https://github.com/gastownhall/beads/issues/2139]

### GitHub Spec Kit

URL: https://github.com/github/spec-kit [VERIFIED: https://github.com/github/spec-kit]

Spec Kit is GitHub’s specification-driven workflow for agentic software development. [VERIFIED: https://github.com/github/spec-kit] Its workflow creates constitution, specification, plan, task, implementation, and convergence artifacts. [VERIFIED: https://github.com/github/spec-kit]

It mechanically structures work through named phases and task artifacts, but the repository does not claim that the agent will obey every prose rule. [VERIFIED: https://github.com/github/spec-kit] Its convergence flow includes bugfix reports and final verdicts such as `verified`, `partial`, or `failed`. [VERIFIED: https://github.com/github/spec-kit]

The repository showed approximately 138.7k stars when read on 2026-09-24. [VERIFIED: https://github.com/github/spec-kit]

A reported weakness is that feature-level `spec.md`, `plan.md`, and `tasks.md` become historical artifacts after merge, leaving no obvious living specification for a module or subsystem. [VERIFIED: https://github.com/github/spec-kit/issues/1100] Other reports ask how specifications remain consistent as features evolve. [VERIFIED: https://github.com/github/spec-kit/issues/620] A separate report describes stale extension versions and a `CLAUDE.md` block still pointing at an old plan. [VERIFIED: https://github.com/github/spec-kit/issues/4345]

Problem addressed: both, with stronger support for within-session drift. [VERIFIED: https://github.com/github/spec-kit]

Borrowable: distinguish immutable feature history from living module/project state, and add CI checks for extension/version/spec freshness. [VERIFIED: https://github.com/github/spec-kit/issues/1100] [VERIFIED: https://github.com/github/spec-kit/issues/4345]

### Taskmaster AI

URL: https://github.com/eyaltoledano/claude-task-master [VERIFIED: https://github.com/eyaltoledano/claude-task-master]

Taskmaster AI turns a PRD into persistent tasks stored in files such as `tasks.json`, with dependencies, tags, statuses, `next`, and `show` operations. [VERIFIED: https://github.com/eyaltoledano/claude-task-master] It integrates with multiple coding-agent clients through CLI and MCP tools. [VERIFIED: https://github.com/eyaltoledano/claude-task-master]

The task graph and status transitions are mechanically addressable through CLI/MCP operations, while the quality of task descriptions and agent adherence remain largely prompt-mediated. [VERIFIED: https://github.com/eyaltoledano/claude-task-master]

The repository showed approximately 28.1k stars when read on 2026-09-24. [VERIFIED: https://github.com/eyaltoledano/claude-task-master]

An issue reports that MCP tools returned stale task data compared with the CLI after manual task updates; restarting the MCP server temporarily resolved the discrepancy. [VERIFIED: https://github.com/eyaltoledano/claude-task-master/issues/348]

Problem addressed: primarily cross-session continuity, with some within-session task focus. [VERIFIED: https://github.com/eyaltoledano/claude-task-master]

Borrowable: maintain one authoritative task store and make every operation reread or validate it instead of relying on process-local cached state. [VERIFIED: https://github.com/eyaltoledano/claude-task-master/issues/348]

### BMAD Method

URL: https://github.com/bmad-code-org/BMAD-METHOD [VERIFIED: https://github.com/bmad-code-org/BMAD-METHOD]

BMAD is an agentic development method organized around specialized skills, workflows, artifacts, reviews, and retrospectives. [VERIFIED: https://github.com/bmad-code-org/BMAD-METHOD]

Its memory documentation describes a project-local “sanctum” containing persistent agent files such as `INDEX.md`, `PERSONA.md`, `MEMORY.md`, and `CAPABILITIES.md`, plus append-only session logs. [VERIFIED: https://bmad-builder-docs.bmad-method.org/explanation/agent-memory-and-personalization/] Curated memory is kept separate from raw session history, and the documentation recommends ongoing capture rather than waiting until session close. [VERIFIED: https://bmad-builder-docs.bmad-method.org/explanation/agent-memory-and-personalization/]

Mechanical enforcement varies by workflow. Recent release notes describe evidence-backed retrospectives, rejection of unfinished stories, verified project-context blocks, and a canonical shared memory log. [VERIFIED: https://github.com/bmad-code-org/BMAD-METHOD/releases]

The repository showed approximately 53.4k stars when read on 2026-09-24; its release page listed `v6.12.0` as latest when read. [VERIFIED: https://github.com/bmad-code-org/BMAD-METHOD] [VERIFIED: https://github.com/bmad-code-org/BMAD-METHOD/releases]

Problem addressed: both. [VERIFIED: https://bmad-builder-docs.bmad-method.org/explanation/agent-memory-and-personalization/] [VERIFIED: https://github.com/bmad-code-org/BMAD-METHOD/releases]

Borrowable: retain raw append-only history, maintain a small curated current memory, write during the session, and require evidence references for retrospective or completion claims. [VERIFIED: https://bmad-builder-docs.bmad-method.org/explanation/agent-memory-and-personalization/] [VERIFIED: https://github.com/bmad-code-org/BMAD-METHOD/releases]

### Agent OS

URL: https://github.com/buildermethods/agent-os [VERIFIED: https://github.com/buildermethods/agent-os]

Agent OS manages project standards, specification work, and context-aware standard injection for coding agents. [VERIFIED: https://github.com/buildermethods/agent-os] It provides commands and structures for discovering, indexing, deploying, and shaping standards. [VERIFIED: https://github.com/buildermethods/agent-os]

The primary enforcement mechanism is file organization and contextual injection; ordinary standards prose is not automatically proven against the codebase. [VERIFIED: https://github.com/buildermethods/agent-os]

The repository showed approximately 5.4k stars when read on 2026-09-24. [VERIFIED: https://github.com/buildermethods/agent-os]

A discussion describes standards drift and proposes a `/sync-standards` workflow that compares standards with code, classifies them as in-sync, drifted, partial, or obsolete, and lets the user update, merge, flag, or remove them. [VERIFIED: https://github.com/buildermethods/agent-os/discussions/329]

Problem addressed: cross-session continuity, with drift detection aimed at both. [VERIFIED: https://github.com/buildermethods/agent-os/discussions/329]

Borrowable: maintain a standards index and add a concrete code-versus-standard audit that produces evidence, rather than relying on agents to notice drift. [VERIFIED: https://github.com/buildermethods/agent-os/discussions/329]

### Cline Memory Bank

URL: https://github.com/dazeb/cline-mcp-memory-bank [VERIFIED: https://github.com/dazeb/cline-mcp-memory-bank]

Cline MCP Memory Bank is a community MCP server that stores project context in Markdown files. [VERIFIED: https://github.com/dazeb/cline-mcp-memory-bank] It provides named operations for initializing memory, updating context, recording decisions, and tracking progress. [VERIFIED: https://github.com/dazeb/cline-mcp-memory-bank]

Its files include `activeContext.md`, `progress.md`, `decisionLog.md`, and `projectContext.md`. [VERIFIED: https://github.com/dazeb/cline-mcp-memory-bank] The mechanism is structured storage plus explicit tools, but the README describes workflow integration through MCP settings and rules rather than a strong schema validator or mandatory write hook. [VERIFIED: https://github.com/dazeb/cline-mcp-memory-bank]

The repository showed approximately 61 stars when read on 2026-09-24. [VERIFIED: https://github.com/dazeb/cline-mcp-memory-bank]

A Cline issue reports that `.clinerules` instructions were not reliably respected unless explicitly pointed out, even when memory-bank files were being read. [VERIFIED: https://github.com/cline/cline/issues/3329]

Problem addressed: primarily cross-session continuity. [VERIFIED: https://github.com/dazeb/cline-mcp-memory-bank]

Borrowable: separate current context, progress, decisions, and project facts into named carriers, then add hooks or validators so writing them is not optional. [VERIFIED: https://github.com/dazeb/cline-mcp-memory-bank]

### Roo Code Memory Bank and Boomerang Tasks

URLs: https://github.com/GreatScottyMac/roo-code-memory-bank and https://roocodeinc.github.io/Roo-Code/features/boomerang-tasks/ [VERIFIED: https://github.com/GreatScottyMac/roo-code-memory-bank] [VERIFIED: https://roocodeinc.github.io/Roo-Code/features/boomerang-tasks/]

Roo Code’s Boomerang feature delegates subtasks into isolated contexts and returns concise summaries to the parent task. [VERIFIED: https://roocodeinc.github.io/Roo-Code/features/boomerang-tasks/] This is a within-session focus mechanism rather than durable project memory.

The community Memory Bank stores files such as active context, progress, and decision logs, with mode-specific instructions and real-time updates. [VERIFIED: https://github.com/GreatScottyMac/roo-code-memory-bank] The repository showed approximately 1.7k stars when read on 2026-09-24. [VERIFIED: https://github.com/GreatScottyMac/roo-code-memory-bank]

A Roo Code issue reports that Memory Bank setup required tedious manual copying of instructions into mode configuration and manual initialization, and requests a built-in toggle. [VERIFIED: https://github.com/RooCodeInc/Roo-Code/issues/3312]

Problem addressed: Boomerang addresses within-session drift; Memory Bank addresses cross-session continuity. [VERIFIED: https://roocodeinc.github.io/Roo-Code/features/boomerang-tasks/] [VERIFIED: https://github.com/GreatScottyMac/roo-code-memory-bank]

Borrowable: isolate complex subtasks, require a structured return summary, and make initialization/configuration first-class rather than dependent on pasted per-mode instructions. [VERIFIED: https://roocodeinc.github.io/Roo-Code/features/boomerang-tasks/] [VERIFIED: https://github.com/RooCodeInc/Roo-Code/issues/3312]

### Kiro Specs and Steering

URLs: https://kiro.dev/docs/specs/ and https://kiro.dev/docs/steering/ [VERIFIED: https://kiro.dev/docs/specs/] [VERIFIED: https://kiro.dev/docs/steering/]

Kiro represents work through requirements or bugfix specifications, design, and discrete tasks. [VERIFIED: https://kiro.dev/docs/specs/] Tasks have trackable status, dependencies, and parallelizable waves. [VERIFIED: https://kiro.dev/docs/specs/]

Steering files live under `.kiro/steering/` and support always-included, file-matched, and manually included guidance. [VERIFIED: https://kiro.dev/docs/steering/] `AGENTS.md` is supported as always-included guidance, and file references can point to live workspace files. [VERIFIED: https://kiro.dev/docs/steering/]

The mechanical layer is task status/dependency tracking and deterministic inclusion rules; steering prose itself remains guidance. [VERIFIED: https://kiro.dev/docs/specs/] [VERIFIED: https://kiro.dev/docs/steering/]

Problem addressed: both, with particularly clear support for within-session task sequencing. [VERIFIED: https://kiro.dev/docs/specs/]

Borrowable: scope guidance by file pattern, reference live files instead of copying facts, and represent parallel work as a dependency graph with explicit waves. [VERIFIED: https://kiro.dev/docs/steering/] [VERIFIED: https://kiro.dev/docs/specs/]

### claude-flow / Ruflo

URL: https://github.com/ruvnet/ruflo/blob/main/v3/%40claude-flow/memory/README.md [VERIFIED: https://github.com/ruvnet/ruflo/blob/main/v3/%40claude-flow/memory/README.md]

Ruflo is the current project associated with the former claude-flow line. [VERIFIED: https://github.com/ruvnet/ruflo/blob/main/v3/%40claude-flow/memory/README.md] Its memory service combines persistent vector/index storage, hybrid retrieval, agent scopes, consolidation, deduplication, expiry handling, and snapshots. [VERIFIED: https://github.com/ruvnet/ruflo/blob/main/v3/%40claude-flow/memory/README.md]

A separate claude-flow fork describes session-start/session-end hooks and memory under `.swarm/memory.db`. [VERIFIED: https://github.com/corticalstack/claude-flow]

An opened issue argues that the hook system does not provide complete lifecycle coverage or general blocking validation, including missing pre-compaction and subagent-stop behavior. [VERIFIED: https://github.com/ruvnet/ruflo/issues/377] This is an issue analysis, not an independently verified product guarantee.

Problem addressed: both, especially automatic cross-session recall and memory maintenance. [VERIFIED: https://github.com/ruvnet/ruflo/blob/main/v3/%40claude-flow/memory/README.md]

Borrowable: use session lifecycle hooks, content hashes, consolidation, expiry, and corruption checks—but ensure important truth remains inspectable in the project rather than only in an external database. [VERIFIED: https://github.com/ruvnet/ruflo/blob/main/v3/%40claude-flow/memory/README.md] [VERIFIED: https://github.com/ruvnet/ruflo/issues/377]

### Cursor Rules and Memories

URL: https://cursor.com/docs/rules [VERIFIED: https://cursor.com/docs/rules]

Cursor project rules live in `.cursor/rules`, support frontmatter such as `description`, `globs`, and `alwaysApply`, and can be version-controlled. [VERIFIED: https://cursor.com/docs/rules] Cursor also supports nested `AGENTS.md` files and user/team rules. [VERIFIED: https://cursor.com/docs/rules]

The mechanical behavior is rule discovery and scoped context inclusion; the content is still model guidance. The documentation recommends referencing live files to reduce staleness and explicitly warns that AI rules are not a sufficient security control. [VERIFIED: https://cursor.com/docs/rules]

The separate old Memories URL redirected to the current Rules page when read on 2026-09-24, so I verified rules but not a distinct current Memories implementation. [VERIFIED: https://cursor.com/docs/context/memories] Claims about automatically generated Cursor memories remain `[UNVERIFIED: search snippet]`.

Problem addressed: cross-session instruction continuity and some within-session drift. [VERIFIED: https://cursor.com/docs/rules]

Borrowable: use declarative scope metadata and live-file references, then enforce critical behavior through tests, hooks, or CI. [VERIFIED: https://cursor.com/docs/rules]

### Aider Conventions

URLs: https://aider.chat/docs/usage/conventions.html and https://github.com/Aider-AI/conventions [VERIFIED: https://aider.chat/docs/usage/conventions.html] [VERIFIED: https://github.com/Aider-AI/conventions]

Aider supports Markdown convention files that can be read explicitly or configured as default read-only files. [VERIFIED: https://aider.chat/docs/usage/conventions.html] Its configuration also supports persistent chat history and repository-map settings. [VERIFIED: https://aider.chat/docs/config/aider_conf.html]

Conventions are injected as context; they are not mechanically enforced unless backed by repository tests, hooks, or external checks. [VERIFIED: https://aider.chat/docs/usage/conventions.html] The community conventions repository showed approximately 205 stars when read on 2026-09-24. [VERIFIED: https://github.com/Aider-AI/conventions]

An issue reports that Aider read a convention file but did not follow a commit-message rule. [VERIFIED: https://github.com/Aider-AI/aider/issues/2384]

Problem addressed: mostly cross-session instruction continuity. [VERIFIED: https://aider.chat/docs/usage/conventions.html]

Borrowable: make conventions explicit, read-only, and automatically loaded—but pair them with executable checks for anything that must hold. [VERIFIED: https://aider.chat/docs/usage/conventions.html] [VERIFIED: https://github.com/Aider-AI/aider/issues/2384]

### OpenAI Codex AGENTS.md

URL: https://developers.openai.com/codex/guides/agents-md [VERIFIED: https://developers.openai.com/codex/guides/agents-md]

Codex discovers instruction files from global configuration through the project tree, supports `AGENTS.override.md`, merges instructions from parent to child directories, and has a documented context-size limit. [VERIFIED: https://developers.openai.com/codex/guides/agents-md]

This mechanically enforces discovery, precedence, nesting, and size limits. The behavioral contents are injected instructions rather than proof-producing constraints. [VERIFIED: https://developers.openai.com/codex/guides/agents-md]

Problem addressed: cross-session project-purpose and convention continuity, with limited protection against within-session drift. [VERIFIED: https://developers.openai.com/codex/guides/agents-md]

Borrowable: standardize hierarchical instruction discovery and override precedence, while keeping durable project state separate from instructions and validating important claims externally. [VERIFIED: https://developers.openai.com/codex/guides/agents-md]

### Claude Code Memory and CLAUDE.md

URL: https://code.claude.com/docs/en/memory [VERIFIED: https://code.claude.com/docs/en/memory]

Claude Code loads project/user instructions from `CLAUDE.md`, `AGENTS.md`, and related locations, and also supports automatic memory. [VERIFIED: https://code.claude.com/docs/en/memory] Automatic memory has size/loading limits, including a first-200-lines or 25KB rule described in the documentation. [VERIFIED: https://code.claude.com/docs/en/memory]

The documentation explicitly describes these as context, not enforced configuration, and recommends hooks such as `PreToolUse` when behavior must be blocked. [VERIFIED: https://code.claude.com/docs/en/memory]

An issue reports automatic memory not being persisted despite an instruction to do so, with no reliable stop hook enforcing the write. [VERIFIED: https://github.com/anthropics/claude-code/issues/65173] Another reports months-old `MEMORY.md` being silently loaded without freshness or expiry warnings. [VERIFIED: https://github.com/anthropics/claude-code/issues/85075]

Problem addressed: both, but with documented and reported weaknesses around stale memory and optional writes. [VERIFIED: https://code.claude.com/docs/en/memory] [VERIFIED: https://github.com/anthropics/claude-code/issues/65173] [VERIFIED: https://github.com/anthropics/claude-code/issues/85075]

Borrowable: separate durable instructions from learned memory, timestamp or version memory, surface stale-state warnings, and use stop/pre-tool hooks for mandatory persistence or validation. [VERIFIED: https://code.claude.com/docs/en/memory] [VERIFIED: https://github.com/anthropics/claude-code/issues/85075]

### Handoff Tools

URLs: https://github.com/open-grove/handoff and https://github.com/rosehgal/handoff [VERIFIED: https://github.com/open-grove/handoff] [VERIFIED: https://github.com/rosehgal/handoff]

OpenGrove Handoff creates a portable, immutable `HANDOFF.md` snapshot from a source session without modifying the source session. [VERIFIED: https://github.com/open-grove/handoff] It explicitly treats the snapshot as point-in-time transfer rather than real-time collaboration or native session restoration. [VERIFIED: https://github.com/open-grove/handoff]

The `rosehgal/handoff` project uses hooks to capture actions in an append-only JSONL event log, then renders Markdown handoffs and history from that log. [VERIFIED: https://github.com/rosehgal/handoff] Its repository showed approximately 2 stars when read on 2026-09-24. [VERIFIED: https://github.com/rosehgal/handoff]

Problem addressed: cross-session continuity, especially explicit transfer between agents or sessions. [VERIFIED: https://github.com/open-grove/handoff] [VERIFIED: https://github.com/rosehgal/handoff]

Borrowable: make the event log the source of truth and treat Markdown as a projection; include decisions, failed approaches, blockers, provenance, and exactly one next action. [VERIFIED: https://github.com/rosehgal/handoff]

### agentmemory

URL: https://github.com/rohitg00/agentmemory [VERIFIED: https://github.com/rohitg00/agentmemory]

agentmemory is a cross-agent persistent-memory system supporting hooks, MCP, REST access, local storage, retrieval, compression, confidence, lifecycle metadata, and knowledge-graph-style relationships. [VERIFIED: https://github.com/rohitg00/agentmemory] Its README describes support for multiple coding agents, including Claude, Cursor, Copilot, Gemini, and Codex. [VERIFIED: https://github.com/rohitg00/agentmemory]

The repository showed approximately 28.8k stars and 2.5k forks when read on 2026-09-24. [VERIFIED: https://github.com/rohitg00/agentmemory]

The README describes automatic capture and recall, but the default external-memory orientation creates a project/version binding question: memories may not automatically belong to the repository state that produced them. [VERIFIED: https://github.com/rohitg00/agentmemory]

Problem addressed: cross-session continuity across different agents. [VERIFIED: https://github.com/rohitg00/agentmemory]

Borrowable: use cross-agent recall and lifecycle hooks, but bind each memory to project identity, branch/version, evidence, and persistence health. [VERIFIED: https://github.com/rohitg00/agentmemory]

I did not open an agentmemory issue page, so failure reports found through search remain `[UNVERIFIED: search snippet]`.

### GSD

URL: https://github.com/karausm/GSD [VERIFIED: https://github.com/karausm/GSD]

GSD initializes project artifacts including `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, and research files. [VERIFIED: https://github.com/karausm/GSD] Its workflow is discuss → plan → execute → verify → ship, with phase context, atomic plans, summaries, and verification artifacts. [VERIFIED: https://github.com/karausm/GSD]

The method deliberately makes plans small enough for fresh context and uses `STATE.md` to rehydrate the current project state. [VERIFIED: https://github.com/karausm/GSD]

Problem addressed: both, especially within-session tunnel vision caused by oversized or poorly bounded work. [VERIFIED: https://github.com/karausm/GSD]

Borrowable: keep a compact current state, make plans context-sized, and require verification artifacts before moving to the next phase. [VERIFIED: https://github.com/karausm/GSD]

No issue or discussion page was opened for GSD, so I found no verified user-reported breakage for it.

## Queries run

```text
site:github.com/steveyegge/beads Beads persistent memory coding agents issue README
GitHub spec-kit official repository specs agent workflow issues
Taskmaster AI claude-task-master official repository persistent tasks sessions
BMAD Method official repository AI agent continuity memory
steveyegge beads github
eyaltoledano claude-task-master GitHub README taskmaster AI
bmad-code-org BMAD-METHOD GitHub README memory
buildermethods agent-os GitHub README specs
Cline Memory Bank official GitHub memory-bank coding agent
Roo Code memory bank boomerang tasks official docs
AWS Kiro specs steering official documentation
claude-flow memory persistence official GitHub
site:docs.cursor.com rules memories project rules official
site:aider.chat/docs conventions repository map conventions official docs
site:developers.openai.com codex AGENTS.md official
site:code.claude.com/docs memory CLAUDE.md official
site:aider.chat/docs conventions.md aider coding agent conventions
site:aider.chat/docs repomap aider files conventions
site:github.com/Aider-AI/aider conventions.md
"persistent memory" "coding agents" GitHub project
"handoff" file AI coding agent session GitHub
"agent task tracker" git coding agent
"spec-driven development" AI coding agent GitHub GSD OpenSpec
site:github.com/steveyegge/beads/issues beads stale memory context issue agent
site:github.com/github/spec-kit/issues spec kit context stale issue tasks
site:github.com/eyaltoledano/claude-task-master/issues taskmaster bug tasks not updated context
site:github.com/bmad-code-org/BMAD-METHOD/issues BMAD memory context issue
site:github.com/buildermethods/agent-os/issues Agent OS standards stale spec issue
site:github.com/dazeb/cline-mcp-memory-bank/issues memory bank
site:github.com/RooCodeInc/Roo-Code/issues memory bank boomerang context
site:github.com/corticalstack/claude-flow/issues memory stale session resume
site:github.com/anthropics/claude-code/issues auto memory stale CLAUDE.md
GreatScottyMac roo-code-memory-bank GitHub README
site:github.com/RooCodeInc/Roo-Code/issues memory bank stale context
site:github.com/corticalstack/claude-flow/issues memory query stale
ruvnet claude-flow GitHub persistent memory hooks
site:github.com/ruvnet/claude-flow memory hooks session-start session-end
site:github.com/rohitg00/agentmemory/issues agentmemory bug stale memory
site:github.com/GreatScottyMac/roo-code-memory-bank/issues memory bank stale
site:github.com/open-grove/handoff/issues session handoff
site:github.com/rosehgal/handoff/issues handoff
site:github.com/gastownhall/beads/issues stale memory bd prime outdated context
site:github.com/gastownhall/beads/discussions stale context memory
site:github.com/github/spec-kit/issues stale spec context drift
site:github.com/bmad-code-org/BMAD-METHOD/issues stale context memory
```

## Not found / limits

- I did not find a verified Kiro issue or discussion describing user breakage in this pass.
- Cursor’s old Memories URL redirected to the current Rules documentation; I verified rules, not a separate current Memories implementation. [VERIFIED: https://cursor.com/docs/context/memories]
- I did not open an agentmemory issue, so its issue-search results were not treated as verified.
- GitHub star counts and release information are snapshots read on 2026-09-24 and can change.
- Stars are activity/adoption signals, not evidence that a mechanism works well.
- Most systems do not mechanically prove that stored project facts remain true after code changes. The closest mechanisms found were generated-content hashes, standards/code drift audits, task/schema validation, memory consolidation, and explicit verification gates. [VERIFIED: https://github.com/gastownhall/beads/issues/2139] [VERIFIED: https://github.com/buildermethods/agent-os/discussions/329] [VERIFIED: https://github.com/github/spec-kit] [VERIFIED: https://github.com/ruvnet/ruflo/blob/main/v3/%40claude-flow/memory/README.md]
- Search snippets for additional projects—including other memory banks, AHP+, Hippo, and related tools—were not promoted to findings because their canonical pages or issue evidence were not opened. [UNVERIFIED: search snippet]

---

## Lane prompt (angle)

PRACTITIONER TOOLS. Find the tools and methods practitioners actually built for agent continuity across sessions. Start with these (verify each, do not assume): Beads (steveyegge/beads), GitHub spec-kit, Taskmaster AI (claude-task-master), BMAD Method, Agent OS (buildermethods), Cline Memory Bank, Roo Code memory/boomerang, Kiro specs/steering (AWS), claude-flow, Cursor rules/memories, Aider conventions, OpenAI Codex AGENTS.md conventions, Claude Code memory/CLAUDE.md patterns and community plugins. Then search for others of the same kind you do not know yet (e.g. "persistent memory for coding agents", "agent task tracker git", "spec-driven development AI agents", "handoff file AI agent"). For each, answer specifically: what does it keep between sessions, what does it ENFORCE mechanically versus merely suggest in prose, how does it keep the stored state from going stale, and where do its users say it breaks (issues, discussions).
