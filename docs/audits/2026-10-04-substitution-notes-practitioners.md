# Practitioner reports of the "babysitting tax" in AI-assisted work (2023-2026)

Method note for the writer. About 15 tool calls: 11 searches and 5 page fetches. Everything below comes from search-result summaries or fetched pages.

- Fetched pages (read by the fetch tool): GitHub issue 98870, HN item 46102048, Stack Overflow blog 2026-05-21, Leon Furze post, Siddhant Khare post.
- Search-snippet only: METR, DORA, the Stack Overflow survey numbers, the Chroma context-rot work, the multi-turn paper, and the HBR/Berkeley study. I did not open the primary documents. Where a number came from an aggregator, the aggregator is the cited source.
- Reddit was not reached. WebSearch returned no Reddit hits and I did not try fetching Reddit, so r/ClaudeAI, r/ExperiencedDevs and r/ChatGPTCoding are NOT covered.
- Hacker News: one thread fetched (about 80 comments).

Central finding for the lead: the broad "AI supervision is tiring" experience is widely reported and partly measured. The specific mechanism in the brief (the model answers its own loaded context instead of what the user said) is reported only as anecdote, and mostly as "ignores my CLAUDE.md or instructions". I found no practitioner source that describes it as paraphrase or substitution of the user's words.

## What do practitioners call this? (vocabulary)

### Takeaway
No single term exists. The vocabulary splits into at least three phenomena that the brief merges. "Babysitting" mostly means attention-tax or permission-prompt supervision, not misreading. "Ignores my instructions / CLAUDE.md" is the closest match to substitution. "Review fatigue / decision fatigue" is the cognitive-load framing.

### Cited Findings
- "Babysitting" is used in Claude Code tooling and blog posts mainly for watching every prompt and tool call, silent stalls on unapproved permission prompts, and agents wandering into directories the user did not want touched. Remedies sold under that name are persistent goals, orchestration frameworks, and self-verification via tests. — [How I Stopped Babysitting Claude Code (DEV)](https://dev.to/yureki_lab/how-i-stopped-babysitting-claude-code-5-patterns-for-247-ai-workers-270n); [XDA](https://www.xda-developers.com/stopped-babysitting-claude-code-with-goal-command/); [Anthropic "Stop babysitting your agents" session page](https://claude.com/code-with-claude/session/tyo-stop-babysitting-your-agents). These came from a search summary, not read page by page.
- "AI agent fatigue" is defined in one blog as "the cumulative cognitive cost of supervising AI agents whose outputs you cannot fully trust, whose contexts you cannot fully see, and whose volume you cannot keep up with." This is a blog's own definition, not a research construct. — [coommit.com](https://coommit.com/blog/ai-agent-fatigue-2026), via search summary.
- "Review fatigue", "decision fatigue" and the reviewer/"quality inspector" identity shift. Siddhant Khare: "I shipped more code last quarter than any quarter in my career. I also felt more drained than any quarter in my career." He also uses "prompt spiral" and "thinking atrophy". — [Khare, AI fatigue is real](https://siddhantkhare.com/writing/ai-fatigue-is-real), fetched.
- The Stack Overflow blog frames it as "decision fatigue". It quotes Smartsheet's CPTO: "The hours haven't changed, but the density of work has." — [Stack Overflow blog 2026-05-21](https://stackoverflow.blog/2026/05/21/coding-agents-are-giving-everyone-decision-fatigue/), fetched.
- "Almost right but not quite" is the Stack Overflow survey's term for the subtly-wrong-output cost. — see the measured-findings section for numbers.
- "Context rot" (Chroma's coinage) and "ignores CLAUDE.md" cover the degradation-with-context framing. — see the context section.
- Khare's complaint is nondeterminism, not misreading: "Same input, same output. That's the contract... AI broke that contract." This is a different phenomenon from substitution. — [Khare](https://siddhantkhare.com/writing/ai-fatigue-is-real), fetched.

### Inferences
- The brief's own framing ("answers its own loaded context instead of what they said") has no matching practitioner term in what I found. Nearest are "ignores my instructions" and "context rot". If the report needs a name, it will have to be coined or mapped onto these.
- "Babysitting" is a poor search key for this mechanism. It over-retrieves the permission-prompt and long-running-autonomy problem.

### Gaps
- No Reddit or Hacker News search with the terms "agent drift", "it ignores what I said", "supervision tax" or "fighting the AI". Not run, call budget.
- Search results are skewed toward vendor and tool-marketing blogs, which have an incentive to name the problem and sell the fix.

## Measured findings on burnout and fatigue: METR, DORA, Stack Overflow, HBR

### Takeaway
Measured data supports "AI use raises review and verification burden and does not reduce burnout". It does not isolate misreading of instructions as a cause. The strongest measured items are METR (a perception gap, not fatigue), the Stack Overflow survey (two-thirds "almost right"), and DORA (no burnout reduction).

### Cited Findings
- METR RCT, early-2025 tools: 16 experienced open-source developers, 246 tasks, mature projects with about 5 years of prior experience. With AI allowed, tasks took 19% longer. Developers forecast a 24% speedup beforehand and still believed after the trial that AI had sped them up by about 20%. Tool was mainly Cursor Pro with Claude 3.5/3.7. — [METR blog](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) and [paper](https://metr.org/Early_2025_AI_Experienced_OS_Devs_Study-paper.pdf), search summary.
- METR now labels the result as historical. It says the result may not reflect current tools or workflows, and it has announced a changed experiment design. — [METR 2026-02-24 update](https://metr.org/blog/2026-02-24-uplift-update/), title and search summary only; contents not read.
- One participant has written up their experience of the METR study. I did not open it. — [domenic.me](https://domenic.me/metr-ai-productivity/)
- DORA 2025 (about 5,000 respondents): 90% use AI at work and over 80% believe it raised their productivity. 30% report little or no trust in AI-generated code. AI shows no measurable impact on burnout or friction. — [Faros summary](https://www.faros.ai/blog/key-takeaways-from-the-dora-report-2025) and [IT Revolution](https://itrevolution.com/articles/ais-mirror-effect-how-the-2025-dora-report-reveals-your-organizations-true-capabilities/), aggregators; the primary dora.dev report was not opened. The DORA framing is "AI amplifies existing strengths and weaknesses".
- Stack Overflow Developer Survey 2025: 84% use AI tools (76% in 2024). 29% trust AI output as accurate (about 40% in 2024). 46% distrust it. 66% say answers are "almost right but not quite". 45% say they lose significant time debugging AI code. The most experienced developers have the lowest "highly trust" rate (2.5%) and the highest "highly distrust" rate (20.7%). — [Particula](https://particula.tech/blog/developer-ai-trust-gap-adoption-vs-confidence), [CODERCOPS](https://blog.codercops.com/blog/stack-overflow-2025-survey-ai-trust-gap); secondary sources, which agree on the figures. The 2025 survey's own page was not opened.
- Berkeley Haas ethnography (Ranganathan and Ye), published in HBR 2026-02-09: about 200 employees at a US tech company over 8 months. AI led to faster pace, broader task scope, longer hours (often unasked), workload creep, cognitive fatigue and burnout risk. — [HBR](https://hbr.org/2026/02/ai-doesnt-reduce-work-it-intensifies-it), [Simon Willison commentary](https://simonwillison.net/2026/Feb/9/ai-intensifies-work/), search summary. Single company, qualitative, not a coding-agent supervision study.
- Smartsheet figures quoted by Stack Overflow: automation intensity up 55% year over year, and 80% of AI-generated content needs editing before it is final. — [Stack Overflow blog](https://stackoverflow.blog/2026/05/21/coding-agents-are-giving-everyone-decision-fatigue/), fetched. The Smartsheet primary was not opened.

### Inferences
- DORA's "no effect on burnout" and the practitioner blogs' "drained" claims conflict at face value. They may measure different things: DORA is a survey of burnout and friction scales, and the blogs are self-selected personal accounts. I did not test that explanation.
- The METR perception gap (felt 20% faster, measured 19% slower) matters for the brief. Self-reports of cost or benefit are unreliable in both directions, so practitioner testimony should not be treated as measurement.
- No measured study I found isolates "the model answers its own context instead of the user's request" as a cost. The Stack Overflow "almost right" item is the nearest proxy.

### Gaps
- No study found comparing hand-coding to AI-supervised coding on validated fatigue or burnout instruments. DORA and HBR are the closest, and neither is that.
- Primary documents for DORA 2025, the Stack Overflow survey, and the METR 2026 update were not opened.
- Whether METR's later results changed direction is unknown to me. The 2026 post is only titled.

## Does more context make the model worse at hearing the current instruction? Session reset as coping

### Takeaway
There is measured support for degradation with length and across turns (Chroma, Laban et al.), and a large body of practitioner anecdote for "Claude ignores CLAUDE.md as it grows or as the session lengthens". Practitioners converge on short instruction files, scoped files, and fresh sessions. Evidence for the practitioner version is anecdotal.

### Cited Findings
- Chroma "context rot": 18 frontier models, all of which get worse as input length grows. Degradation is non-uniform, with cliffs. It is worse on semantic matching than lexical matching. — [Greyling summary](https://cobusgreyling.medium.com/llm-context-rot-28a6d0399655), [Hamel notes](https://hamel.dev/notes/llm/rag/p6-context_rot.html), search summary; the Chroma original was not opened. This measures retrieval-style tasks, not instruction following.
- "LLMs Get Lost in Multi-Turn Conversation" (Laban, Hayashi, Zhou, Neville; Microsoft Research and Salesforce Research): 15 models, over 200,000 simulated conversations, 39% average drop from single-turn to multi-turn. Models above 90% single-turn drop to about 60%. The loss is mostly unreliability, not aptitude. Stated cause: models make assumptions in early turns, prematurely attempt final solutions, and do not recover from a wrong turn. — [arXiv 2505.06120](https://arxiv.org/abs/2505.06120), search summary; the paper was not opened. Setup: instructions revealed piece by piece by a simulator, so it is closer to "underspecified request" than to "long loaded CLAUDE.md".
- GitHub issue 98870 (anthropics/claude-code, version 2.1.283, macOS): the model "ignores claude.md instructions after ~10 conversation turns", and repeated requests to re-read the file in the same session do not fix it. One reporter, no reactions or comments visible, no reproduction. Anecdote of n=1. — [Issue 98870](https://github.com/anthropics/claude-code/issues/98870), fetched.
- HN thread on "Claude often ignores CLAUDE.md" (about 80 comments, fetched): users say long or non-universal files lead to ignoring ("The more information you have in the file that's not universally applicable... the more likely it is that Claude will ignore" — nico). "The longer the context window gets, the more likely it is to forget rules and instructions" (dkersten). Claude "adheres somewhat reliably at the beginning and end" but not "in the middle where the real work is being done" (chickensong). — [HN 46102048](https://news.ycombinator.com/item?id=46102048). All anecdote.
- Practitioner detection trick: tell the model to start every message with a marker (an emoji, or "address me as Mr Tinkleberry") and treat its absence as proof the rules are no longer being followed. This is a user-built canary for the very failure in the brief. — [HN 46102048](https://news.ycombinator.com/item?id=46102048), fetched.
- Stack Overflow blog quotes Smartsheet's Arora: "We see most of our senior people loading a lot more in context and then making smaller changes." This is one executive quote on a coping pattern (heavy context, small edits). — [Stack Overflow blog](https://stackoverflow.blog/2026/05/21/coding-agents-are-giving-everyone-decision-fatigue/), fetched.
- Rule-count claim: frontier thinking models follow about 150-200 instructions with reasonable consistency, and quality degrades as the count rises. — [devops.dev article](https://blog.devops.dev/why-claude-keeps-ignoring-your-instructions-and-the-4-line-fix-1920ffa5bd19?gi=3378c0e08a62), search summary, secondary blog with no primary identified.
- Claim that CLAUDE.md content is delivered as user messages rather than system config, and that Claude may skip rules it judges irrelevant. — same search results; unverified, source is a blog, and the mechanism is not confirmed by Anthropic in anything I read.

### Inferences
- The measured work (Chroma, Laban et al.) supports "performance degrades with length and turns" in general. It does not show that the cause is the model preferring its own loaded context to the latest message. Laban et al. come closest ("premature assumptions it does not recover from").
- Practitioner remedies reflect that belief: shrink the always-loaded file, push rarely-needed material to on-demand skills or per-directory files, and restart sessions. Evidence that these remedies work is anecdotal.

### Gaps
- No measurement found of CLAUDE.md length against compliance. The "150-200 instructions" figure is untraced.
- No Reddit evidence on session-reset habits, so I cannot say how widespread restart-over-continue is. The HN thread shows the idea is present but not its prevalence.

## Neurodivergent (ADHD/autistic) users: the cost of AI paraphrasing or reinterpreting their words

### Takeaway
I found no source describing this specific cost. The neurodivergent material is mostly positive on AI, with some complaints about AI imposing assumptions about how neurodivergent people should work. This question is essentially a gap.

### Cited Findings
- Leon Furze, an AuDHD adult, reports AI "constantly encouraged... to do things in certain ways or think through problems from a certain perspective, based on flawed assumptions". Conversations defaulted to time-blocking and task breakdown that he found condescending. He also reports a compulsive "ennui" after heavy Claude Code use, and describes chatbots as "pinball machines". His coping is intentional distance and ignoring unhelpful advice. — [Furze](https://leonfurze.com/2026/02/22/lived-experience-using-ai-as-an-audhd-adult/), fetched. This is imposition of assumptions about the user, not paraphrase of their words.
- A CNBC piece (2025-11-08) reports people with ADHD, autism and dyslexia saying AI agents help them succeed at work. — [CNBC](https://www.cnbc.com/2025/11/08/adhd-autism-dyslexia-jobs-careers-ai-agents-success.html), search snippet only; not read. Counter-direction to the brief.
- A Substack post on "5,000 conversations" with AI by an ADHD user exists. I did not open it. — [Unexpected Insights](https://unexpectedinsights.substack.com/p/the-adhd-brain-on-ai)

### Inferences
- The brief's premise (paraphrase or reinterpretation as a specific neurodivergent cost) is not supported by anything retrieved. The closest item, Furze, concerns generic advice and assumptions. Do not present this as a documented finding without more searching.

### Gaps
- No source on AI paraphrasing or reinterpretation cost for ADHD or autistic users, and no study. Search was one query. Reddit (r/ADHD, r/autism, r/ClaudeAI) and academic HCI venues are the obvious places and were not searched.
- Self-selection: positive accounts dominate what search returns.

## Workflow mitigations practitioners converge on

### Takeaway
Reported mitigations cluster into: shorter and scoped instruction files, on-demand skills, fresh sessions, canary markers, self-verification through tests, and reducing the review surface. Read-back confirmation, forcing the agent to quote the request, and plan-first are NOT evidenced in what I retrieved.

### Cited Findings
- Keep CLAUDE.md short. The test is "Would removing this cause Claude to make mistakes? If not, cut it." Move occasional knowledge to skills loaded on demand. — [Anthropic best-practices page](https://www.anthropic.com/engineering/claude-code-best-practices) and others, search summary. The "Would removing this" wording comes from the search summary, not from a page I read.
- Per-directory CLAUDE.md files that load automatically when relevant (stingraycharles, HN); a re-read command such as "/bootstrap" (jmathai, HN). A counter-comment (threecheese) notes that such a command only appends to the context and does not clear it. — [HN 46102048](https://news.ycombinator.com/item?id=46102048), fetched.
- Canary markers (emoji at the start of every message, a required form of address) as a drift detector. — [HN 46102048](https://news.ycombinator.com/item?id=46102048), fetched.
- Give the agent a way to verify its own work (tests), so it catches mistakes in place of waiting on human supervision. — [DEV: stopped babysitting](https://dev.to/yureki_lab/how-i-stopped-babysitting-claude-code-5-patterns-for-247-ai-workers-270n), search summary.
- Khare's personal coping list: 30-minute time-boxes on AI sessions, thinking in the morning and AI in the afternoon, accepting about 70% usable output, selective review of critical paths. These manage the human, not the model. — [Khare](https://siddhantkhare.com/writing/ai-fatigue-is-real), fetched.
- Stack Overflow blog suggests moving judgment gates to end-to-end outcomes instead of per-commit review, and focusing on intent and requirements over low-level validation. — [Stack Overflow blog](https://stackoverflow.blog/2026/05/21/coding-agents-are-giving-everyone-decision-fatigue/), fetched.
- A triage protocol for agent code review exists. I did not open it. — [CyberDevTech](https://www.cyberdevtech.com/articles/agent-code-review-fatigue-triage-protocol)
- Superpowers plugin (workflows encoded as skills) and the Babysitter orchestration framework (event-sourced workflow management) are marketed as babysitting cures. — [McNamara](https://colinmcnamara.com/blog/stop-babysitting-your-ai-agents-superpowers-breakthrough), [Babysitter](https://rywalker.com/research/babysitter), search summary; vendor-flavored.

### Inferences
- The mitigations that work against ignoring (canary, short files, scoped files, restarts) are detection and prevention at the instruction-loading level. The ones aimed at review fatigue (time-boxing, outcome gates) are human-side. Few address mis-hearing of the current message directly.
- The convergence on "make the model verify its own work" shifts the checking cost from the human to a test, which only works where a checker exists.

### Gaps
- No source found for read-back confirmation, "quote my request back", or plan-first as practitioner-reported mitigations against misreading. They may exist; I did not search them, and plan mode is a documented Claude Code feature I did not look up.
- No evidence on small-diff discipline or external state files beyond passing mentions in marketing posts.
- No data on which mitigations fail. Failure reports are limited to the HN counter-comment on /bootstrap and the GitHub issue where re-reading CLAUDE.md did not help.

## Is the experience widespread? (anecdote volume)

### Takeaway
Widespread for the general experience, thin for the specific mechanism. The generic "AI fatigue" and "ignores CLAUDE.md" experience shows up repeatedly across many blogs and one 80-comment HN thread. The substitution mechanism as described in the brief shows up in no source as such.

### Cited Findings
- The Stack Overflow 2025 survey figure of 66% "almost right but not quite" is the broadest measured proxy. — see the measured-findings section.
- Anecdote count for this session: 1 GitHub issue (n=1), 1 HN thread (about 80 comments, a handful of distinct claims), and about 6 blog posts on fatigue and babysitting. The blogs overlap heavily and several repeat each other's themes, so they are not independent evidence.

### Inferences
- The HN and GitHub items show up because the search was keyed to Claude Code and CLAUDE.md, so Claude Code is over-represented. Copilot, Cursor and aider are not represented.

### Gaps
- Nothing on Copilot, Cursor or aider specifically. Not searched.
- Prevalence among Claude Code users cannot be estimated from what I found.
