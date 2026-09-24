# Prior art, problem side: where practitioners complain

**Provenance.** Codex lane (gpt-5.6-luna, `codex exec -s read-only`, live web search), commissioned 2026-09-24 by session dev-17 (996fa1b7) on the operator's direction: search from the PROBLEM side, not our mechanism vocabulary. 21 web searches, 113,113 tokens. The body below is the lane's final message VERBATIM; its [VERIFIED]/[UNVERIFIED] marks are the LANE's own grades (lane-verified: it says it opened the URL), not desk-verified. Desk checks and grading: `2026-09-24-prior-art-problem-side-synthesis.md`. The lane's angle prompt is reproduced at the end.

---

## Headline

- The strongest complaint is not merely “new sessions start blank”: compaction can make an active session forget completed work, repeat searches, or revive rejected approaches. [VERIFIED: https://github.com/anthropics/claude-code/issues/75759] [VERIFIED: https://github.com/openai/codex/issues/36712]
- Handoffs are the dominant homemade workaround, but large handoffs become context bloat; users increasingly split static rules from evolving state. [VERIFIED: https://www.reddit.com/r/ClaudeCode/comments/1uefjj1/context_drastically_exhausts_with_handoffs/] [VERIFIED: https://www.reddit.com/r/ClaudeAI/comments/1tmjqhy/anyone_found_a_good_pattern_for_sharing_context/]
- The information users most fear losing is not “what files exist,” but why a decision was made, what failed, and what must not be retried. [VERIFIED: https://josangel.com/blog/handoff-skill/] [VERIFIED: https://www.reddit.com/r/ChatGPTCoding/comments/1vegq98/claude_code_spent_40_minutes_ruling_out_an/]
- Independent workarounds converge on repo-owned, structured state: current goal, completed work, decisions, rejected paths, open questions, files, and verification results. [VERIFIED: https://docs.cline.bot/best-practices/memory-bank] [VERIFIED: https://github.com/ravbyte-ai/agent-memory-system]
- Persistent memory creates a second failure mode: stale, contradictory, or poisoned memories can become authoritative unless they support provenance, revision, and validation. [VERIFIED: https://github.com/hotovo/aider-desk/issues/749] [VERIFIED: https://www.reddit.com/r/LocalLLaMA/comments/1r5q7xd/how_are_you_handling_persistent_memory_for_ai/]

## Findings

#### Cross-session amnesia and handoff failure

### Claude Code users’ session-reset complaint

URL: [Reddit discussion](https://www.reddit.com/r/ClaudeAI/comments/1w4dhx6/how_do_you_guys_save_tokens_and_keep_context_with/) — read 2026-09-24. [VERIFIED: https://www.reddit.com/r/ClaudeAI/comments/1w4dhx6/how_do_you_guys_save_tokens_and_keep_context_with/]

What it is: A practitioner says that reopening Claude Code means “I basically start from scratch.” [VERIFIED: https://www.reddit.com/r/ClaudeAI/comments/1w4dhx6/how_do_you_guys_save_tokens_and_keep_context_with/]

Reported workaround: One commenter uses handoff documents; another uses `claude -c`, `claude -r`, and auto-memory. [VERIFIED: https://www.reddit.com/r/ClaudeAI/comments/1w4dhx6/how_do_you_guys_save_tokens_and_keep_context_with/]

Borrowable: Make session resume a first-class operation with an explicit, inspectable boot briefing rather than relying on transcript continuity.

Addresses: Cross-session.

Activity/adoption: Reddit thread; no reliable adoption metric was visible. [VERIFIED: https://www.reddit.com/r/ClaudeAI/comments/1w4dhx6/how_do_you_guys_save_tokens_and_keep_context_with/]

### Multi-agent handoff and re-litigated decisions

URL: [r/ChatGPTCoding discussion](https://www.reddit.com/r/ChatGPTCoding/comments/1vegq98/claude_code_spent_40_minutes_ruling_out_an/) — read 2026-09-24. [VERIFIED: https://www.reddit.com/r/ChatGPTCoding/comments/1vegq98/claude_code_spent_40_minutes_ruling_out_an/]

What it is: A user reports that Claude Code spent 40 minutes rejecting a caching approach, then Codex proposed the same approach two hours later. Their summary: “none of them know what the others already figured out.” [VERIFIED: https://www.reddit.com/r/ChatGPTCoding/comments/1vegq98/claude_code_spent_40_minutes_ruling_out_an/]

What people do: Paste conversations, update `CLAUDE.md`, write notes, or explain everything again; the user says they sometimes allow the new agent to repeat the dead end because explaining it costs nearly as much. [VERIFIED: https://www.reddit.com/r/ChatGPTCoding/comments/1vegq98/claude_code_spent_40_minutes_ruling_out_an/]

Borrowable: Store rejected approaches as durable, tool-neutral records with reasons and evidence, not merely as prose summaries.

Addresses: Cross-session and cross-tool.

Activity/adoption: Individual practitioner report; the author says they were testing a local-first memory tool called Memmy, but no adoption evidence was provided. [VERIFIED: https://www.reddit.com/r/ChatGPTCoding/comments/1vegq98/claude_code_spent_40_minutes_ruling_out_an/]

### Static rules versus evolving state

URL: [Reddit discussion](https://www.reddit.com/r/ClaudeAI/comments/1tmjqhy/anyone_found_a_good_pattern_for_sharing_context/) — read 2026-09-24. [VERIFIED: https://www.reddit.com/r/ClaudeAI/comments/1tmjqhy/anyone_found_a_good_pattern_for_sharing_context/]

What it is: A user says their `CLAUDE.md` had grown to about 200 lines and was “half stale context from two weeks ago.” [VERIFIED: https://www.reddit.com/r/ClaudeAI/comments/1tmjqhy/anyone_found_a_good_pattern_for_sharing_context/]

Reported workaround: Commenters recommend a small static `CLAUDE.md` for conventions and constraints, plus an evolving `STATE.md` containing recent changes, decisions, and next steps. [VERIFIED: https://www.reddit.com/r/ClaudeAI/comments/1tmjqhy/anyone_found_a_good_pattern_for_sharing_context/]

The unresolved problem is write-back: one participant says getting the agent to update the state file reliably at session close is “the whole problem.” [VERIFIED: https://www.reddit.com/r/ClaudeAI/comments/1tmjqhy/anyone_found_a_good_pattern_for_sharing_context/]

Borrowable: Separate stable project truth from time-varying working state, and mechanically require the latter to be updated.

Addresses: Cross-session.

Activity/adoption: Practitioner discussion; no reliable usage metric was visible. [VERIFIED: https://www.reddit.com/r/ClaudeAI/comments/1tmjqhy/anyone_found_a_good_pattern_for_sharing_context/]

### Cline Memory Bank

URL: [Cline Memory Bank documentation](https://docs.cline.bot/best-practices/memory-bank) — read 2026-09-24. [VERIFIED: https://docs.cline.bot/best-practices/memory-bank]

What it is: Cline documents a structured markdown methodology intended to turn a stateless assistant into a persistent development partner. [VERIFIED: https://docs.cline.bot/best-practices/memory-bank]

What it persists/enforces: Six files separate project purpose, product context, active context, system patterns, technical context, and progress; the documentation instructs Cline to read them at every task start and update them after significant changes. [VERIFIED: https://docs.cline.bot/best-practices/memory-bank]

The manual recovery sequence is: update the Memory Bank, start a new conversation, then tell Cline to follow its custom instructions. [VERIFIED: https://docs.cline.bot/best-practices/memory-bank]

Borrowable: A fixed schema makes “what should survive?” explicit, especially by separating current focus from durable architecture.

Addresses: Cross-session, with some within-session context management.

Activity/adoption: Official Cline documentation; no independent adoption metric was visible. [VERIFIED: https://docs.cline.bot/best-practices/memory-bank]

### Agent Memory System

URL: [GitHub repository](https://github.com/ravbyte-ai/agent-memory-system) — read 2026-09-24. [VERIFIED: https://github.com/ravbyte-ai/agent-memory-system]

What it is: A TypeScript CLI that generates repository-local markdown/JSON memory, code-graph artifacts, worklogs, checkpoints, and handoffs for agents including Codex, Claude Code, and Cursor. [VERIFIED: https://github.com/ravbyte-ai/agent-memory-system]

What it persists/enforces: It creates `AGENTS.md`, a context index, repository maps, testing notes, dependency graphs, append-only worklogs, and a current handoff file. Its example workflow requires reading the relevant memory, querying the graph before high-impact edits, running tests, and recording a checkpoint. [VERIFIED: https://github.com/ravbyte-ai/agent-memory-system]

The repository reports a maintainer-run benchmark on 21 tasks: fewer files traversed and higher concept accuracy, but more tokens per task; the repository explicitly says these are early, non-independent measurements. [VERIFIED: https://github.com/ravbyte-ai/agent-memory-system]

Borrowable: Combine human-readable state with machine-readable checkpoints and verification commands; make the memory layer reviewable in Git.

Addresses: Cross-session and within-session drift.

Activity/adoption: At read time, GitHub showed 23 commits, 0 issues, 0 pull requests, and 1 fork; the project describes itself as early. [VERIFIED: https://github.com/ravbyte-ai/agent-memory-system]

### Drift

URL: [Hacker News discussion](https://news.ycombinator.com/item?id=47934325) — read 2026-09-24. [VERIFIED: https://news.ycombinator.com/item?id=47934325]

What it is: A local tool for moving coding-agent work between agents by capturing session logs, compacting them into structured markdown, binding them to Git commits, and exposing them through CLI/MCP. [VERIFIED: https://news.ycombinator.com/item?id=47934325]

The author says exporting raw chat was too noisy because the next agent would re-debate everything. [VERIFIED: https://news.ycombinator.com/item?id=47934325]

Borrowable: Bind durable agent state to repository history and commits, so continuity is project-owned rather than tied to one vendor’s transcript format.

Addresses: Cross-session and cross-tool.

Activity/adoption: Show HN announcement; no independent adoption signal was visible. [VERIFIED: https://news.ycombinator.com/item?id=47934325]

#### Within-session drift, compaction, and loops

### Claude Code compaction forgetting completed actions

URL: [Claude Code issue #75759](https://github.com/anthropics/claude-code/issues/75759) — read 2026-09-24. [VERIFIED: https://github.com/anthropics/claude-code/issues/75759]

What it is: An open issue reports that after mid-session compaction, Claude Code denies or cannot find evidence of actions it performed earlier in the same session. [VERIFIED: https://github.com/anthropics/claude-code/issues/75759]

The user’s quoted failure is that the agent searched repeatedly for backup files it had itself created; the user had to paste the earlier conversation to prove the action occurred. [VERIFIED: https://github.com/anthropics/claude-code/issues/75759]

What it persists/enforces: Nothing in the reported failure; the issue requests faithful preservation of file paths, Git operations, and artifacts in the compaction summary. [VERIFIED: https://github.com/anthropics/claude-code/issues/75759]

Borrowable: Every consequential action should leave an external, queryable receipt rather than relying on a later summary to remember it.

Addresses: Within-session.

Activity/adoption: Issue opened July 8, 2026 and still marked open when read. [VERIFIED: https://github.com/anthropics/claude-code/issues/75759]

### Codex compaction losing the task entirely

URL: [Codex issue #36712](https://github.com/openai/codex/issues/36712) — read 2026-09-24. [VERIFIED: https://github.com/openai/codex/issues/36712]

What it is: A report says automatic compaction can leave the agent saying, “What would you like me to work on?” despite an ongoing task. [VERIFIED: https://github.com/openai/codex/issues/36712]

The reporter tried asking the agent to read the uncompacted history, but instead had to open a new conversation and treat the worktree as another agent’s implementation attempt. [VERIFIED: https://github.com/openai/codex/issues/36712]

The problem reportedly happened three times in one task and caused repeated rewriting of acceptable work. [VERIFIED: https://github.com/openai/codex/issues/36712]

Borrowable: Recovery should begin from repository state plus an explicit task/checkpoint record, not from the model’s ability to reconstruct a lost transcript.

Addresses: Within-session and cross-session recovery.

Activity/adoption: GitHub issue labeled as a Codex CLI context-management bug; no response, assignee, project, or milestone was shown when read. [VERIFIED: https://github.com/openai/codex/issues/36712]

### Progressive amnesia across multiple compactions

URL: [Claude Code issue #33212](https://github.com/anthropics/claude-code/issues/33212) — read 2026-09-24. [VERIFIED: https://github.com/anthropics/claude-code/issues/33212]

What it is: The issue says that after two or three compactions, earlier reasoning and decisions disappear and the model no longer knows that earlier compactions happened. [VERIFIED: https://github.com/anthropics/claude-code/issues/33212]

Reported workaround: The author added compact instructions to `CLAUDE.md` and manually ran a structured pre-compact brain dump containing what was done, why, what was rejected, and what was next. They report that this preserved the session’s “full road” after four or more compactions. [VERIFIED: https://github.com/anthropics/claude-code/issues/33212]

Borrowable: Compaction summaries should be cumulative and append historical decisions instead of replacing history with only recent work.

Addresses: Within-session.

Activity/adoption: Issue #33212 was opened March 11, 2026, marked stale, and closed as not planned when read; the Claude Code repository showed 5k+ issues and 24.3k forks at read time. [VERIFIED: https://github.com/anthropics/claude-code/issues/33212]

### Codex loops after compaction

URL: [r/codex discussion](https://www.reddit.com/r/codex/comments/1uy70sl/context_compactment_is_completely_broken/) — read 2026-09-24. [VERIFIED: https://www.reddit.com/r/codex/comments/1uy70sl/context_compactment_is_completely_broken/]

What it is: Users report old screenshots being treated as current, already-fixed UI being “fixed” again, and the agent repeatedly searching the same repository state. [VERIFIED: https://www.reddit.com/r/codex/comments/1uy70sl/context_compactment_is_completely_broken/]

A particularly concrete description is: “check repo → search the same code → say ‘ok, now I’ll fix it’ → context compacted → check the same stuff again → repeat.” [VERIFIED: https://www.reddit.com/r/codex/comments/1uy70sl/context_compactment_is_completely_broken/]

Reported workaround: One commenter says a handoff markdown file, read after compaction and updated with the last state, fixed “99%” of their problems; this is anecdotal and unvalidated. [VERIFIED: https://www.reddit.com/r/codex/comments/1uy70sl/context_compactment_is_completely_broken/]

Borrowable: Detect repeated states mechanically and stop/resume only after reloading a checkpoint.

Addresses: Within-session drift.

Activity/adoption: The post and comments were active in July–August 2026; no reliable prevalence estimate was available. [VERIFIED: https://www.reddit.com/r/codex/comments/1uy70sl/context_compactment_is_completely_broken/]

### Cursor context rot

URL: [r/cursor discussion](https://www.reddit.com/r/cursor/comments/1r1veb4/context_rot_in_cursor_whats_working_to_avoid/) — read 2026-09-24. [VERIFIED: https://www.reddit.com/r/cursor/comments/1r1veb4/context_rot_in_cursor_whats_working_to_avoid/]

What it is: A user says that as a Cursor thread grows, the model starts missing constraints and making assumptions; after summarizing or starting a new chat, the user must re-explain information the model previously understood. [VERIFIED: https://www.reddit.com/r/cursor/comments/1r1veb4/context_rot_in_cursor_whats_working_to_avoid/]

The user’s concise diagnosis is: “After a point I’m not coding anymore, I’m doing context maintenance.” [VERIFIED: https://www.reddit.com/r/cursor/comments/1r1veb4/context_rot_in_cursor_whats_working_to_avoid/]

Borrowable: Treat context maintenance as a budgeted workflow with explicit stop points, not as an accidental byproduct of a long conversation.

Addresses: Within-session and cross-session.

Activity/adoption: Practitioner discussion; no reliable adoption metric was visible. [VERIFIED: https://www.reddit.com/r/cursor/comments/1r1veb4/context_rot_in_cursor_whats_working_to_avoid/]

### Cline subtasks and infinite loops

URL: [Cline discussion #4249](https://github.com/cline/cline/discussions/4249) — read 2026-09-24. [VERIFIED: https://github.com/cline/cline/discussions/4249]

What it is: A discussion proposes child tasks/subagents so search-heavy work does not consume the main task’s context. [VERIFIED: https://github.com/cline/cline/discussions/4249]

A Cline participant reports infinite loops in `replace_file` and `write_file` operations on files over 4,000 lines, affecting both main tasks and subtasks. [VERIFIED: https://github.com/cline/cline/discussions/4249]

The suggested control is manual intervention, prompting, pausing, or conversation-turn limits for subtasks. [VERIFIED: https://github.com/cline/cline/discussions/4249]

Borrowable: Isolate exploratory work, cap loops, and preserve the parent task’s state independently of child execution.

Addresses: Within-session drift.

Activity/adoption: The discussion showed 8 replies when read and dates from June 2025. [VERIFIED: https://github.com/cline/cline/discussions/4249]

### Anthropic’s official session-management guidance

URL: [Anthropic: Using Claude Code](https://claude.com/blog/using-claude-code-session-management-and-1m-context) — read 2026-09-24. [VERIFIED: https://claude.com/blog/using-claude-code-session-management-and-1m-context]

What it is: Anthropic explicitly describes “context rot” as performance degradation as context grows and recommends `/compact`, `/clear`, `/rewind`, and subagents as separate context-management moves. [VERIFIED: https://claude.com/blog/using-claude-code-session-management-and-1m-context]

Anthropic says compaction is lossy and recommends steering it with a focus, while `/clear` is normally paired with a brief distilled from what was learned. [VERIFIED: https://claude.com/blog/using-claude-code-session-management-and-1m-context]

The post also says `/rewind` is useful when an approach failed because it lets the user preserve the useful file-reading context while dropping the failed branch. [VERIFIED: https://claude.com/blog/using-claude-code-session-management-and-1m-context]

Borrowable: Make correction branch-aware: preserve the evidence-gathering state, explicitly record the failed approach, and restart from the last sound seam.

Addresses: Both.

Activity/adoption: First-party guidance; no independent usage metric was provided. [VERIFIED: https://claude.com/blog/using-claude-code-session-management-and-1m-context]

#### Memory quality, staleness, and enforcement

### AiderDesk’s memory-maintenance problem

URL: [AiderDesk issue #749](https://github.com/hotovo/aider-desk/issues/749) — read 2026-09-24. [VERIFIED: https://github.com/hotovo/aider-desk/issues/749]

What it is: A feature request says AiderDesk’s memory operations are agent-driven, so the primary model must decide when to store, retrieve, and correct memories. [VERIFIED: https://github.com/hotovo/aider-desk/issues/749]

The issue identifies duplicate, contradictory, stale, and noisy memories as causes of declining retrieval quality. [VERIFIED: https://github.com/hotovo/aider-desk/issues/749]

The proposed remedy is background extraction, consolidation, deduplication, correction, and categorization by a cheaper utility model; the issue lists categories such as decision, action, fact, strategy, rejected, and preference. [VERIFIED: https://github.com/hotovo/aider-desk/issues/749]

Borrowable: A durable ledger needs update/reversal semantics and maintenance separate from the main coding turn; “append forever” is insufficient.

Addresses: Both.

Activity/adoption: Issue opened April 14, 2026 and was closed when read; the repository showed 132 forks, 49 issues, and 3 pull requests. [VERIFIED: https://github.com/hotovo/aider-desk/issues/749]

### Practitioner concern: memory can preserve the wrong truth

URL: [r/LocalLLaMA discussion](https://www.reddit.com/r/LocalLLaMA/comments/1r5q7xd/how_are_you_handling_persistent_memory_for_ai/) — read 2026-09-24. [VERIFIED: https://www.reddit.com/r/LocalLLaMA/comments/1r5q7xd/how_are_you_handling_persistent_memory_for_ai/]

What it is: Practitioners report that summaries and extracted decisions may help temporarily, but agents later continue relying on architectural decisions that became obsolete. [VERIFIED: https://www.reddit.com/r/LocalLLaMA/comments/1r5q7xd/how_are_you_handling_persistent_memory_for_ai/]

One proposed design separates “context” from “execution history,” snapshots artifacts, hashes state, and logs decisions separately from raw chat. [VERIFIED: https://www.reddit.com/r/LocalLLaMA/comments/1r5q7xd/how_are_you_handling_persistent_memory_for_ai/]

Another practitioner says persistent memory should have provenance, delete/update semantics, health checks, and a separate behavioral-safety layer. [VERIFIED: https://www.reddit.com/r/LocalLLaMA/comments/1r5q7xd/how_are_you_handling_persistent_memory_for_ai/]

Borrowable: Treat memory entries as versioned claims with evidence, status, confidence, and supersession—not as unquestionable prompt text.

Addresses: Both.

Activity/adoption: Discussion thread with multiple proposed personal systems; no independently verified adoption metric was visible. [VERIFIED: https://www.reddit.com/r/LocalLLaMA/comments/1r5q7xd/how_are_you_handling_persistent_memory_for_ai/]

### OpenSpec: durable specifications and verification

URL: [OpenSpec](https://openspec.dev/) — read 2026-09-24. [VERIFIED: https://openspec.dev/]

What it is: A lightweight framework for creating and managing software specifications that keeps teams and coding agents aligned as requirements evolve. [VERIFIED: https://openspec.dev/]

What it persists/enforces: Its documented workflow creates proposals, specifications, designs, and tasks, then applies, verifies, and archives the resulting work. [VERIFIED: https://openspec.dev/]

This is not a memory system in the narrow sense, but it externalizes purpose, acceptance intent, implementation tasks, and verification outside the conversation. [VERIFIED: https://openspec.dev/]

Borrowable: Keep the current goal and acceptance criteria in durable artifacts that the agent must verify against, rather than letting the latest prompt define reality.

Addresses: Cross-session and within-session drift.

Activity/adoption: The site reported 68.0k GitHub stars, more than 265,000 developers per month, a new spec every two seconds, and version `v1.13.0`; these are site-reported figures read 2026-09-24, not independently audited here. [VERIFIED: https://openspec.dev/]

## Queries run

- `site:news.ycombinator.com AI coding agent forgets context between sessions memory handoff`
- `site:reddit.com/r/ClaudeAI Claude Code forgets between sessions context memory handoff`
- `site:reddit.com/r/ChatGPTCoding coding agent loses track mid task goes in circles context`
- `site:reddit.com/r/cursor Cursor agent forgets context between sessions memory rules`
- `site:github.com/anthropics/claude-code/issues forget context session memory context compaction`
- `site:github.com/openai/codex/issues context compaction loses track status`
- `site:github.com/getcursor/cursor/issues agent forgets context session`
- `site:github.com/cline/cline/issues context memory handoff forgets`
- `AI coding agent context rot handoff notes blog Claude Code memory decisions rejected`
- `Claude Code session handoff context loss blog lessons learned`
- `Codex context compaction loses track blog markdown progress updates`
- `Cursor context rot memory file project rules practitioner blog`
- `site:github.com/cline/cline/issues "context" "forget" agent`
- `site:github.com/Aider-AI/aider/issues context forgets session memory`
- `site:news.ycombinator.com coding agent "goes in circles" context`
- `site:reddit.com/r/LocalLLaMA coding agent memory handoff context loss`
- `site:reddit.com/r/ClaudeAI "already rejected" "context" Claude`
- `site:reddit.com/r/codex "repeat" "context compacted"`
- `site:news.ycombinator.com "re-debates" agent context`
- `site:github.com/anthropics/claude-code/issues "re-propose" rejected approach`

## Not found / limits

- I found many qualitative complaints, but no reliable prevalence study measuring how often coding agents lose state, loop, or re-litigate decisions in real projects. [UNVERIFIED: this search]
- I found no opened Cursor GitHub issue that was as directly relevant as the Cursor Reddit discussions; the useful Cursor evidence here is practitioner-reported. [UNVERIFIED: search result / this search]
- I found no evidence that any workaround survives arbitrary session kills and repeated compactions without human review. The strongest claims were self-reported, including “fixed 99%,” and were not independently tested. [VERIFIED: https://www.reddit.com/r/codex/comments/1uy70sl/context_compactment_is_completely_broken/]
- Handoff files are widely suggested, but users also report that large handoffs dilute attention and that agents often fail to write them back reliably. [VERIFIED: https://www.reddit.com/r/ClaudeCode/comments/1uefjj1/context_drastically_exhausts_with_handoffs/] [VERIFIED: https://www.reddit.com/r/ClaudeAI/comments/1tmjqhy/anyone_found_a_good_pattern_for_sharing_context/]
- Several memory tools and projects appeared to be promotional or early-stage. I treated their capabilities and benchmark numbers as claims made by their authors, not as independent validation. [VERIFIED: https://github.com/ravbyte-ai/agent-memory-system] [VERIFIED: https://openspec.dev/]

---

## Lane prompt (angle)

WHERE PEOPLE COMPLAIN. Search practitioner discussion — Hacker News, Reddit (r/ClaudeAI, r/ChatGPTCoding, r/cursor, r/LocalLLaMA), GitHub issues of Claude Code / Codex / Cursor / Cline, and practitioner blog posts — for the frustration: agent forgets between sessions, loses track mid-task, context rot, tunnel vision, re-litigating decisions, "it keeps going in circles", handoff notes, "memory bank" failures. Extract: (a) the recurring failure descriptions in users' own words (quote short snippets with links); (b) the homemade workarounds people report and whether they say those worked or were abandoned, and why; (c) any tool or practice multiple people independently converge on. Group findings by failure type rather than by site.
