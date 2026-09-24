# Prior art, problem side: within-session drift and tunnel vision

**Provenance.** Codex lane (gpt-5.6-luna, `codex exec -s read-only`, live web search), commissioned 2026-09-24 by session dev-17 (996fa1b7) on the operator's direction: search from the PROBLEM side, not our mechanism vocabulary. 39 web searches, 173,052 tokens. The body below is the lane's final message VERBATIM; its [VERIFIED]/[UNVERIFIED] marks are the LANE's own grades (lane-verified: it says it opened the URL), not desk-verified. Desk checks and grading: `2026-09-24-prior-art-problem-side-synthesis.md`. The lane's angle prompt is reproduced at the end.

---

## Headline

- Direct answers now exist: CodeBolt’s sidecar compares the original task/plan with recent phases; IDS proposes a semantic/structural/temporal trajectory score. [VERIFIED: https://docs.codebolt.ai/docs/build-on-codebolt/multi-agent-orchestration/drift-detection] [VERIFIED: https://nips.cc/virtual/2025/loc/san-diego/128062]
- The strongest recurring mechanism is independent re-anchoring: compare current state and actions against the goal using a fresh observer or independently verified environment state. [VERIFIED: https://arxiv.org/abs/2608.01964] [VERIFIED: https://docs.codebolt.ai/docs/build-on-codebolt/multi-agent-orchestration/drift-detection]
- ReflAct addresses tunnel vision inside the loop by reflecting on current state “in relation to” the final goal before every action. [VERIFIED: https://arxiv.org/abs/2505.15182]
- Most long-horizon benchmarks measure terminal success or partial progress, not the earliest point where a locally plausible trajectory becomes globally wrong. [VERIFIED: https://metr.org/time-horizons/] [VERIFIED: https://odysseysbench.com/] [VERIFIED: https://labs.scale.com/leaderboard/swe_bench_pro_public_v2?tab=full]
- Aviation and surgery point to the same countermeasure: precommit alternatives, repeatedly assess conformity to plan, and empower an external observer to interrupt fixation. [VERIFIED: https://www.faa.gov/sites/faa.gov/files/SE_Topic_22-11_CFIT%20Plan%20Continuation%20Bias_0.pdf] [VERIFIED: https://pubmed.ncbi.nlm.nih.gov/32115301/]

## Findings

### Evaluating Goal Drift in Language Model Agents

URL: <https://arxiv.org/abs/2505.02709>

- What it is: A 2025 technical report testing agents in a simulated stock-trading environment with competing goals and goal-switching phases lasting over 100,000 tokens. [VERIFIED: https://arxiv.org/abs/2505.02709]
- It measures action drift, inaction drift, and whether the model’s stated goal remains aligned with its system goal. [VERIFIED: https://arxiv.org/abs/2505.02709]
- The report finds increasing drift in longer goal-switching phases and a correlation between measured drift and misaligned self-reported goals. [VERIFIED: https://arxiv.org/abs/2505.02709]
- Activity: submitted May 5, 2025; this is a research report rather than a deployed tool. [VERIFIED: https://arxiv.org/abs/2505.02709]
- Scope: primarily within-session drift. [VERIFIED: https://arxiv.org/abs/2505.02709]
- Borrowable: benchmark “return to the original goal after an instrumental subtask,” including inaction and behavioral flexibility, not only explicit wrong actions. [UNVERIFIED: recommendation]

### ReflAct: World-Grounded Decision Making

URL: <https://arxiv.org/abs/2505.15182>

- What it is: An agent reasoning backbone that reflects continuously on the current belief/state and the task goal, rather than only predicting the next action. [VERIFIED: https://arxiv.org/abs/2505.15182]
- The paper specifically describes failures where actions are locally plausible but ignore the long-term goal, including revisiting already searched locations and fixating on a found object. [VERIFIED: https://arxiv.org/abs/2505.15182]
- Its signal is an explicit state–goal relationship at each timestep; the authors report 93.3% ALFWorld success and a 27.7% average improvement over ReAct. [VERIFIED: https://arxiv.org/abs/2505.15182]
- Activity: submitted May 21, 2025; no adoption signal was checked beyond the public preprint. [VERIFIED: https://arxiv.org/abs/2505.15182]
- Scope: within-session drift. [VERIFIED: https://arxiv.org/abs/2505.15182]
- Borrowable: require every action proposal to contain “current state → remaining goal → why this action advances that relationship.” [UNVERIFIED: recommendation]

### Towards Trajectory-Level Alignment: Intent Drift Score

URL: <https://nips.cc/virtual/2025/loc/san-diego/128062>

- What it is: A NeurIPS 2025 workshop poster defining “intent drift” as a trajectory-level divergence that can occur even when individual steps appear correct. [VERIFIED: https://nips.cc/virtual/2025/loc/san-diego/128062]
- Its Intent Drift Score combines semantic, structural, and temporal signals into a prefix-monotone score intended for real-time monitoring. [VERIFIED: https://nips.cc/virtual/2025/loc/san-diego/128062]
- The page reports linear-time computation, million-token scalability, correlation above 0.82 with human ratings, and earlier detection than BLEU, ROUGE, and graph-based diagnostics. [VERIFIED: https://nips.cc/virtual/2025/loc/san-diego/128062]
- Activity: presented at the Workshop on Multi-Turn Interactions in LLMs on December 6, 2025; no deployment/adoption signal was shown on the page. [VERIFIED: https://nips.cc/virtual/2025/loc/san-diego/128062]
- Scope: within-session trajectory drift; potentially applicable across session boundaries if prefixes are persisted. [VERIFIED: https://nips.cc/virtual/2025/loc/san-diego/128062]
- Borrowable: maintain a monotonic “trajectory suspicion” signal over prefixes, rather than judging only the final answer. [UNVERIFIED: recommendation]

### LongHorizon-Harness

URL: <https://arxiv.org/abs/2608.01964>

- What it is: A harness that separates management, execution, and auditing into a Manage–Execute–Audit loop. [VERIFIED: https://arxiv.org/abs/2608.01964]
- It keeps task state outside the executor and updates that state only with facts independently verified from the environment; each round uses a fresh-context executor and read-only auditor. [VERIFIED: https://arxiv.org/abs/2608.01964]
- The authors report improvements on WeaveBench, Terminal-Bench 2.1, and OSWorld 2.0 across several models. [VERIFIED: https://arxiv.org/abs/2608.01964]
- Activity: submitted August 3, 2026; public arXiv preprint, with no adoption signal established here. [VERIFIED: https://arxiv.org/abs/2608.01964]
- Scope: both—within-session drift and loss of trustworthy state across execution rounds. [VERIFIED: https://arxiv.org/abs/2608.01964]
- Borrowable: make “what is true now?” an independently audited state transition, not something the acting model is allowed to infer and carry forward unchallenged. [UNVERIFIED: recommendation]

### CodeBolt Drift Detection

URL: <https://docs.codebolt.ai/docs/build-on-codebolt/multi-agent-orchestration/drift-detection>

- What it is: A documented runtime sidecar for long runs. [VERIFIED: https://docs.codebolt.ai/docs/build-on-codebolt/multi-agent-orchestration/drift-detection]
- The detector loads the original task, initial plan, and recent event-log phases, then asks a separate model for `on_track`, `drifting`, or `off_track`. [VERIFIED: https://docs.codebolt.ai/docs/build-on-codebolt/multi-agent-orchestration/drift-detection]
- Its reactions are graded: reminder for `drifting`, replan or human pause for `off_track`. [VERIFIED: https://docs.codebolt.ai/docs/build-on-codebolt/multi-agent-orchestration/drift-detection]
- The documentation explicitly says the acting agent is a poor judge of its own drift and recommends an external observer with a fresh context. [VERIFIED: https://docs.codebolt.ai/docs/build-on-codebolt/multi-agent-orchestration/drift-detection]
- Activity: documentation page was read September 24, 2026; no independent usage or adoption signal was checked. [VERIFIED: https://docs.codebolt.ai/docs/build-on-codebolt/multi-agent-orchestration/drift-detection]
- Scope: within-session drift. [VERIFIED: https://docs.codebolt.ai/docs/build-on-codebolt/multi-agent-orchestration/drift-detection]
- Borrowable: compare the current trajectory with both the original goal and the initial plan; use a cheap, independent judge and graded intervention thresholds. [UNVERIFIED: recommendation]

### AgentFuse

URL: <https://github.com/ns-0437/agentfuse>

- What it is: An open-source supervisor/circuit breaker for long-running agents. [VERIFIED: https://github.com/ns-0437/agentfuse]
- It watches tool calls, graph routes, state changes, token spend, loops, goal drift, and logic traps; it then applies a deterministic escalation ladder such as goal restatement, forbidding a failing action, challenging assumptions, or decomposing the task. [VERIFIED: https://github.com/ns-0437/agentfuse]
- It persists monitor state in SQLite so restart does not reset budget and loop counters. [VERIFIED: https://github.com/ns-0437/agentfuse]
- Activity read September 24, 2026: GitHub showed 2 stars, 1 fork, 490 commits, and no visible release entry. [VERIFIED: https://github.com/ns-0437/agentfuse]
- The project reports 100% recall/precision/F1 on its own 1,018-scenario suite, while explicitly warning that the suite’s labels and generators are self-authored and not evidence of production readiness. [VERIFIED: https://github.com/ns-0437/agentfuse]
- Scope: both. [VERIFIED: https://github.com/ns-0437/agentfuse]
- Borrowable: separate monitoring from acting, prefer deterministic recovery rules where possible, and persist the supervisor’s own state across restarts. [UNVERIFIED: recommendation]

### ContinuityBench

URL: <https://github.com/ning-coeva/continuity-bench>

- What it is: A benchmark for behavioral continuity under multi-domain, multi-turn, adversarial interaction. [VERIFIED: https://github.com/ning-coeva/continuity-bench]
- Its taxonomy includes goal drift, defined as preserving task objectives across interruptions, alongside identity, abstraction, and style drift. [VERIFIED: https://github.com/ning-coeva/continuity-bench]
- Stressors include domain switching, goal interruption, multi-project interleaving, and stance erosion; an `adaptation_vs_drift` condition is intended to distinguish legitimate adaptation from drift. [VERIFIED: https://github.com/ning-coeva/continuity-bench]
- Activity read September 24, 2026: GitHub showed 1 star, 0 forks, 19 commits, and no visible release entry. [VERIFIED: https://github.com/ning-coeva/continuity-bench]
- Scope: within-session continuity and interruption robustness; it is a proxy for cross-session continuity, not a repository-persistence system. [VERIFIED: https://github.com/ning-coeva/continuity-bench]
- Borrowable: include hard negatives where retries, pivots, subgoals, or paraphrases look like drift but are actually correct adaptation. [UNVERIFIED: recommendation]

### Reflexion

URL: <https://arxiv.org/abs/2303.11366>

- What it is: A loop with an Actor, Evaluator, and Self-Reflection component; feedback is converted into verbal experience and stored in an episodic memory buffer for later attempts. [VERIFIED: https://arxiv.org/abs/2303.11366]
- It detects failure through an evaluator signal, then produces a postmortem-style reflection rather than merely replaying the raw failed trajectory. [VERIFIED: https://arxiv.org/abs/2303.11366]
- Its mechanism is primarily reactive and cross-trial: it improves later attempts after a failure signal rather than continuously detecting semantic drift during the current trajectory. [VERIFIED: https://arxiv.org/abs/2303.11366]
- Activity: arXiv paper from 2023; no current adoption signal was checked. [VERIFIED: https://arxiv.org/abs/2303.11366]
- Scope: mainly cross-attempt/session continuity, with limited within-session protection. [VERIFIED: https://arxiv.org/abs/2303.11366]
- Borrowable: store a compact causal lesson—what assumption failed and what must change—rather than a generic transcript summary. [UNVERIFIED: recommendation]

### METR Task-Completion Time Horizons

URL: <https://metr.org/time-horizons/>

- What it is: A benchmark metric estimating the human-equivalent task duration at which an agent reaches a chosen reliability level, commonly 50% or 80%. [VERIFIED: https://metr.org/time-horizons/]
- The current page says its estimates use over 100 diverse software tasks and fit success probability against human expert task duration. [VERIFIED: https://metr.org/time-horizons/]
- METR explicitly distinguishes task difficulty from the amount of autonomous time an agent can operate. [VERIFIED: https://metr.org/time-horizons/]
- Activity: page last updated May 8, 2026; methodology and raw data links are provided. [VERIFIED: https://metr.org/time-horizons/]
- Scope: within-session long-horizon capability, but the published metric is terminal reliability rather than a live drift detector. [VERIFIED: https://metr.org/time-horizons/]
- Borrowable: measure failure probability as horizon grows, then add “first irreversible drift step” and recovery-after-intervention as separate metrics. [UNVERIFIED: recommendation]

### Odysseys

URL: <https://odysseysbench.com/>

- What it is: A benchmark of 200 realistic, multi-site, long-horizon web tasks derived from browsing sessions. [VERIFIED: https://odysseysbench.com/]
- It uses rubric checkpoints to score partial progress and introduces Trajectory Efficiency, defined as rubric progress per step. [VERIFIED: https://odysseysbench.com/]
- The site reports 44.5% perfect-task success for its strongest evaluated model and 1.15% trajectory efficiency. [VERIFIED: https://odysseysbench.com/]
- The benchmark records full trajectories and checkpoint outcomes, making it useful for locating where progress stopped even though it does not itself intervene online. [VERIFIED: https://odysseysbench.com/]
- Activity read September 24, 2026: public site exposes 200 tasks, a leaderboard, task viewer, and trajectory recordings. [VERIFIED: https://odysseysbench.com/]
- Scope: within-session drift and tunnel vision. [VERIFIED: https://odysseysbench.com/]
- Borrowable: use explicit rubric checkpoints and score progress-per-step, not only final pass/fail. [UNVERIFIED: recommendation]

### SWE-Bench Pro V2

URL: <https://labs.scale.com/leaderboard/swe_bench_pro_public_v2?tab=full>

- What it is: A refreshed benchmark for difficult, long-horizon software-engineering tasks. [VERIFIED: https://labs.scale.com/leaderboard/swe_bench_pro_public_v2?tab=full]
- The September 22, 2026 update contains 642 tasks across 11 repositories, publishes trajectories, re-grades diffs in pristine environments, and applies a two-sided reference/empty-patch gate. [VERIFIED: https://labs.scale.com/leaderboard/swe_bench_pro_public_v2?tab=full]
- The earlier SWE-Bench Pro paper describes tasks requiring hours to days for professionals and reports trajectory failure categories such as wrong solutions, tool-use errors, context overflow, and loops. [VERIFIED: https://arxiv.org/abs/2509.16941]
- Its primary metric remains resolve rate: whether the final patch passes required tests without regressions. [VERIFIED: https://labs.scale.com/leaderboard/swe_bench_pro_public_v2?tab=full]
- Activity: V2 update dated September 22, 2026; trajectories and per-task grades are published. [VERIFIED: https://labs.scale.com/leaderboard/swe_bench_pro_public_v2?tab=full]
- Scope: within-session long-horizon coding; it exposes failures but does not provide a runtime drift intervention. [VERIFIED: https://labs.scale.com/leaderboard/swe_bench_pro_public_v2?tab=full]
- Borrowable: retain full trajectories and label failure onset, not just final patch status; use pristine re-grading to prevent false success. [UNVERIFIED: recommendation]

### τ-Bench

URL: <https://taubench.com/?lang=es>

- What it is: A benchmark for agents that converse with users, call tools, retrieve knowledge, and follow domain policies. [VERIFIED: https://taubench.com/?lang=es]
- The original benchmark uses simulated users, domain APIs, and verifiable database outcomes with pass^k reliability. [VERIFIED: https://taubench.com/?lang=es]
- The current project has expanded into τ²/τ³ variants with dual-control, banking knowledge retrieval, voice interaction, and audited task fixes. [VERIFIED: https://taubench.com/?lang=es]
- The original GitHub repository warns that its airline and retail tasks are outdated and points users to τ³-bench. [VERIFIED: https://github.com/sierra-research/tau-bench]
- Activity read September 24, 2026: the original GitHub repository showed 218 forks, 39 issues, and 17 pull requests. [VERIFIED: https://github.com/sierra-research/tau-bench]
- Scope: within-session goal adherence under interruptions and tool use; terminal pass^k does not identify the first drift point. [VERIFIED: https://taubench.com/?lang=es]
- Borrowable: treat tool effects and user actions as externally verifiable state transitions, then add prefix-level drift labels to the existing pass^k evaluation. [UNVERIFIED: recommendation]

### FAA Plan Continuation Bias

URL: <https://www.faa.gov/sites/faa.gov/files/SE_Topic_22-11_CFIT%20Plan%20Continuation%20Bias_0.pdf>

- What it is: An FAA safety briefing on “plan continuation bias,” the tendency to continue an original plan despite information suggesting it should be abandoned. [VERIFIED: https://www.faa.gov/sites/faa.gov/files/SE_Topic_22-11_CFIT%20Plan%20Continuation%20Bias_0.pdf]
- It describes stacked weak signals—weather, fuel, darkness, warnings—that may be individually rationalized until the safe diversion window is gone. [VERIFIED: https://www.faa.gov/sites/faa.gov/files/SE_Topic_22-11_CFIT%20Plan%20Continuation%20Bias_0.pdf]
- Its countermeasures are explicit alternatives, continual objective assessment of conformity to plan, and dealing with small problems before they become large ones. [VERIFIED: https://www.faa.gov/sites/faa.gov/files/SE_Topic_22-11_CFIT%20Plan%20Continuation%20Bias_0.pdf]
- Activity: FAA document dated December 22, 2022. [VERIFIED: https://www.faa.gov/newsroom/safety-briefing/cfit-and-plan-continuation-bias]
- Scope: within-session human-operator drift. [VERIFIED: https://www.faa.gov/sites/faa.gov/files/SE_Topic_22-11_CFIT%20Plan%20Continuation%20Bias_0.pdf]
- Borrowable: require periodic “conformance checks” against the goal and predeclare what evidence will trigger a replan. [UNVERIFIED: recommendation]

### Surgical Situational Awareness and Inattention Blindness

URLs: <https://pubmed.ncbi.nlm.nih.gov/32115301/> and <https://www.frontiersin.org/journals/surgery/articles/10.3389/fsurg.2022.916228/pdf>

- A surgical human-factors review describes tunnel vision as concentrating on one aspect of patient care while losing broader situational awareness, and emphasizes team members watching for one another. [VERIFIED: https://pubmed.ncbi.nlm.nih.gov/32115301/]
- A 2022 pilot study tested 28 young neurosurgeons; 13 who completed mindfulness training had fewer inattention errors than 15 controls in the study’s operative-video task. [VERIFIED: https://www.frontiersin.org/journals/surgery/articles/10.3389/fsurg.2022.916228/pdf]
- The study itself cautions that the sample was small, matched rather than randomized, and conducted virtually, so translation to patient outcomes remains uncertain. [VERIFIED: https://www.frontiersin.org/journals/surgery/articles/10.3389/fsurg.2022.916228/pdf]
- The operational signal is not semantic plan comparison; it is missed unexpected information outside the current focus, reduced by deliberate vigilance and team monitoring. [VERIFIED: https://pubmed.ncbi.nlm.nih.gov/32115301/] [VERIFIED: https://www.frontiersin.org/journals/surgery/articles/10.3389/fsurg.2022.916228/pdf]
- Scope: within-session tunnel vision. [VERIFIED: https://pubmed.ncbi.nlm.nih.gov/32115301/]
- Borrowable: give the agent or a supervisor a standing duty to inspect for salient evidence outside the current subtask, and allow another observer to interrupt. [UNVERIFIED: recommendation]

### Lost in the Middle

URL: <https://arxiv.org/abs/2307.03172>

- What it is: A controlled study of long-context question answering and key-value retrieval. [VERIFIED: https://arxiv.org/abs/2307.03172]
- It finds a U-shaped position effect: relevant information is used best at the beginning or end of context and substantially worse in the middle. [VERIFIED: https://arxiv.org/abs/2307.03172]
- The study is not an agent drift detector, but it supplies a plausible substrate for drift: the original goal or a critical constraint may remain technically present while becoming poorly accessible. [VERIFIED: https://arxiv.org/abs/2307.03172]
- Activity: arXiv paper originally submitted July 6, 2023; the authors released code and evaluation data. [VERIFIED: https://arxiv.org/abs/2307.03172]
- Scope: within-session context access. [VERIFIED: https://arxiv.org/abs/2307.03172]
- Borrowable: place the authoritative goal and current state in retrieval-stable locations, but verify that this improves trajectory behavior rather than assuming prompt placement solves drift. [UNVERIFIED: recommendation]

## Queries run

1. `LLM agents goal drift plan drift long-horizon tasks detect wrong trajectory`
2. `agentic LLM long horizon coherence benchmark goal adherence plan drift`
3. `LLM agent self-monitoring detect trajectory failure local steps globally wrong`
4. `lost in the middle long context language models original paper`
5. `site:arxiv.org goal drift language model agents long horizon`
6. `site:openreview.net long-horizon agents goal adherence trajectory drift`
7. `site:metr.org task horizon agents benchmark time horizon official`
8. `site:arxiv.org LLM agent trajectory global plan local action error detection`
9. `LLM agent progress monitor trajectory verifier detects off-track plan supervisor long horizon`
10. `LLM agent periodic goal restatement re-anchor plan long horizon self monitoring paper`
11. `Reflexion verbal reinforcement learning self-reflection agent trajectory failure paper`
12. `LLM agent critic detects subgoal failure global trajectory local correctness`
13. `human factors cognitive tunneling fixation plan continuation bias aviation primary research`
14. `aviation plan continuation bias detecting wrong trajectory monitoring research`
15. `surgery cognitive fixation tunnel vision human factors review primary study`
16. `cognitive tunneling goal neglect human factors aviation surgery review`
17. `SWE-bench official benchmark long-horizon software engineering agent task duration trajectory evaluation`
18. `tau-bench official benchmark tool agent user interaction long horizon`
19. `WebArena benchmark long horizon web agents success official`
20. `GAIA benchmark agent general assistant long horizon`
21. `Towards Trajectory-Level Alignment: Detecting Intent`
22. `Intent Drift Score trajectory stability paper`
23. `local global trajectory reasoning LLM agent failure detector`
24. `site:openreview.net trajectory-level alignment intent drift`
25. `site:pmc.ncbi.nlm.nih.gov surgical tunnel vision cognitive tunneling inattention blindness surgeons study`
26. `site:pubmed.ncbi.nlm.nih.gov surgery cognitive tunneling inattention blindness surgeons 73`
27. `surgical tunnel vision concentration overall awareness human factors open access`
28. `Noah Shinn Reflexion GitHub evaluator self-reflection episodic memory`
29. `Reflexion paper ALFWorld failure heuristic looping excessive steps`

## Not found / limits

- I did not find a mature, widely adopted coding-agent standard for online semantic drift detection with independently validated ground truth. The clearest direct implementations were CodeBolt’s documented sidecar and AgentFuse’s small open-source project. [UNVERIFIED: synthesis of the searches above]
- I did not find a benchmark whose primary metric is “the earliest point where each locally reasonable action begins steadily reducing global goal progress.” Existing benchmarks expose this indirectly through checkpoint scores, trajectory efficiency, failure categories, or final success. [VERIFIED: https://odysseysbench.com/] [VERIFIED: https://labs.scale.com/leaderboard/swe_bench_pro_public_v2?tab=full] [VERIFIED: https://metr.org/time-horizons/]
- Human-factors literature offered stronger operational countermeasures than automated detectors: plan-conformance checks, precommitted alternatives, team cross-monitoring, and early interruption. [VERIFIED: https://www.faa.gov/sites/faa.gov/files/SE_Topic_22-11_CFIT%20Plan%20Continuation%20Bias_0.pdf] [VERIFIED: https://pubmed.ncbi.nlm.nih.gov/32115301/]
- Several search hits were recent preprints, project documentation, or self-reported benchmarks; I treated their claims as verified only when I opened the cited page, but did not independently reproduce their experiments. [UNVERIFIED: research limitation]


---

## Lane prompt (angle)

WITHIN-SESSION DRIFT AND TUNNEL VISION. Find research and tooling on an agent (or a human operator) staying oriented to the overall goal during long tasks: goal drift / plan drift in LLM agents, "lost in the middle" and long-horizon agent failures, benchmarks measuring long-horizon coherence (e.g. METR task-length work, SWE-bench long tasks, tau-bench), self-monitoring / metacognition / reflexion-style checks, plan re-anchoring, periodic goal restatement, supervisor/critic agents that detect wrong trajectories, and human-factors research on fixation / cognitive tunneling / "plan continuation bias" (aviation, surgery). Key question: does anything DETECT that work is steadily going the wrong way while each step is locally correct — and what signal does it use? An earlier survey found nothing for this, so either find it or state clearly, with your queries, that it does not exist.
