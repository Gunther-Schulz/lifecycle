# Prior art, problem side: continuity in non-AI fields

**Provenance.** Codex lane (gpt-5.6-luna, `codex exec -s read-only`, live web search), commissioned 2026-09-24 by session dev-17 (996fa1b7) on the operator's direction: search from the PROBLEM side, not our mechanism vocabulary. 46 web searches, 218,806 tokens. The body below is the lane's final message VERBATIM; its [VERIFIED]/[UNVERIFIED] marks are the LANE's own grades (lane-verified: it says it opened the URL), not desk-verified. Desk checks and grading: `2026-09-24-prior-art-problem-side-synthesis.md`. The lane's angle prompt is reproduced at the end.

---

## Headline

- Structured handoffs work best as bundles: required fields, training, receiver confirmation, observation, and recurring measurement. I-PASS improved handoff completeness across 32 hospitals and was associated with roughly 47% fewer reported handoff-related adverse events. [VERIFIED: https://pmc.ncbi.nlm.nih.gov/articles/PMC10964397/]
- The strongest recurring pattern is receiver-side verification: synthesis/read-back, questions, cross-checking, explicit acceptance, and post-handoff review. [VERIFIED: https://www.ahrq.gov/teamstepps-program/curriculum/communication/tools/ipass.html]
- Currentness must be engineered. Operational periods, timestamps, “record immediately,” end-of-shift checks, review indicators, and explicit supersession all combat stale state. [VERIFIED: https://www.iaea.org/sites/default/files/documents/review-missions/civauxfureport.pdf]
- Good continuity records preserve not only actions, but uncertainty, failed attempts, rationale, consequences, ownership, and next steps. [VERIFIED: https://www.med.upenn.edu/bgs-rcr-exdes/case-study-module-1.html]
- Most non-clinical fields provide strong operational doctrine but little controlled outcome evidence. The clearest quantitative evidence found was clinical; ATC, nuclear, ICS, laboratory, and ADR sources document failure modes and controls rather than comparable effect sizes. [UNVERIFIED: synthesis of the opened sources]

## Findings

### I-PASS clinical handoff bundle

URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC10964397/

I-PASS requires illness severity, a patient summary, an action list with timelines and ownership, situation awareness and contingency planning, and synthesis by the receiver. [VERIFIED: https://www.ahrq.gov/teamstepps-program/curriculum/communication/tools/ipass.html]

The failure mode is directly relevant: at baseline, all five elements appeared in only 20.0% of observed verbal handoffs and 10.4% of written handoffs; the study also reports frequent omissions and outdated or erroneous information. [VERIFIED: https://pmc.ncbi.nlm.nih.gov/articles/PMC10964397/]

The implementation covered 32 hospitals, 2,735 residents, and 760 faculty champions. [VERIFIED: https://pmc.ncbi.nlm.nih.gov/articles/PMC10964397/] Post-implementation, all five elements appeared in 66.3% of verbal and 73.5% of written handoffs, while reported major handoff-related adverse events fell from 1.7 to 0.9 per person-year and minor events from 17.5 to 9.3. [VERIFIED: https://pmc.ncbi.nlm.nih.gov/articles/PMC10964397/]

Staleness and unreadability were addressed through longitudinal coaching, monthly metric reviews, direct observation, feedback, revised handoff tools, and a sustainability campaign. [VERIFIED: https://pmc.ncbi.nlm.nih.gov/articles/PMC10964397/]

Activity/adoption signal: the opened study reports implementation across 32 hospitals rather than repository-style stars or releases. [VERIFIED: https://pmc.ncbi.nlm.nih.gov/articles/PMC10964397/]

Problem coverage: both cross-session continuity and within-session drift. [VERIFIED: https://pmc.ncbi.nlm.nih.gov/articles/PMC10964397/]

Borrowable: require a machine-checkable action list, owner, deadline, contingency, and receiver confirmation; measure completeness after deployment. [UNVERIFIED: application synthesis]

### SBAR and diagnostic-uncertainty handoff

URL: https://www.ahrq.gov/teamstepps-program/curriculum/communication/tools/sbar.html

SBAR structures a handoff as Situation, Background, Assessment, and Recommendation/Request; AHRQ’s guidance also requires identity, relevant history and tests, objective assessment, uncertainty, requested action, timing, and repeat-back. [VERIFIED: https://www.ahrq.gov/teamstepps-program/curriculum/communication/tools/sbar.html]

AHRQ identifies diagnostic momentum, anchoring, passive receivers, failure to ask clarifying questions, and failure to challenge unclear diagnoses as transition risks. [VERIFIED: https://www.ahrq.gov/diagnostic-safety/resources/issue-briefs/dxsafety-care-transitions2.html]

The same AHRQ review reports that DE-PASS was associated with fewer ICU transfers in a pre/post study, while SBAR-DR improved perceived handoff quality but did not reduce perceived diagnostic uncertainty. [VERIFIED: https://www.ahrq.gov/diagnostic-safety/resources/issue-briefs/dxsafety-care-transitions2.html]

Staleness is controlled by explicitly recording the provisional diagnosis, degree of certainty, requested next action, follow-up time, and escalation triggers. [VERIFIED: https://www.ahrq.gov/diagnostic-safety/resources/issue-briefs/dxsafety-care-transitions2.html]

Problem coverage: both, with particular value against within-session premature closure. [VERIFIED: https://www.ahrq.gov/diagnostic-safety/resources/issue-briefs/dxsafety-care-transitions2.html]

Borrowable: every handoff should distinguish facts, working hypotheses, uncertainty, and the next falsifying check. [UNVERIFIED: application synthesis]

### Industrial shift handover: UK HSE

URL: https://www.hse.gov.uk/humanfactors/topics/shift-handover.htm

The HSE defines effective handover as preparation by the outgoing worker, two-way information exchange, and incoming-worker cross-checking. [VERIFIED: https://www.hse.gov.uk/humanfactors/topics/shift-handover.htm]

The recommended minimum is face-to-face, joint-responsibility, verbal plus written communication based on the incoming worker’s information needs. [VERIFIED: https://www.hse.gov.uk/humanfactors/topics/shift-handover.htm]

The HSE cites the 1983 Sellafield Beach Incident and the Piper Alpha disaster as cases where shift-handover communication failures contributed to accidents. [VERIFIED: https://www.hse.gov.uk/humanfactors/topics/shift-handover.htm]

The guidance recommends identifying high-risk handovers, giving adequate time and resources, designing logs and displays around operator needs, and involving end users in communication-system changes. [VERIFIED: https://www.hse.gov.uk/humanfactors/topics/shift-handover.htm]

The opened source provides strong failure documentation and procedural controls, but no controlled before/after effect size. [UNVERIFIED: source-review note]

Problem coverage: both. [VERIFIED: https://www.hse.gov.uk/humanfactors/topics/shift-handover.htm]

Borrowable: make handoff acceptance a two-party protocol: outgoing summary, incoming questions, independent cross-check, explicit responsibility transfer. [UNVERIFIED: application synthesis]

### Air-traffic-control position relief

URL: https://www.faa.gov/air_traffic/publications/atpubs/atc_html/appendix_a.html

The FAA states that reliance on memory causes forgotten or incomplete information and requires a position-relief checklist. [VERIFIED: https://www.faa.gov/air_traffic/publications/atpubs/atc_html/appendix_a.html]

The relieving controller first reviews status displays, equipment, the operational situation, communications, current and pending traffic, and written notes. [VERIFIED: https://www.faa.gov/air_traffic/publications/atpubs/atc_html/appendix_a.html]

The outgoing controller must cover abnormal status, weather, traffic, and communications; the incoming controller asks questions, explicitly assumes responsibility, then verifies and updates the transferred information. [VERIFIED: https://www.faa.gov/air_traffic/publications/atpubs/atc_html/appendix_a.html]

An Australian ATSB investigation documented a controller forgetting a taxi clearance during a handover; it reports that handover increases workload and distraction and notes 13 occurrences since 2008 in which handover was an influencing factor. [VERIFIED: https://www.atsb.gov.au/investigations/ao-2018-040]

The ATSB identifies checklists, delaying handover until a traffic lull, and tools that reduce memory dependence as mitigations, but the opened report does not provide a controlled reduction estimate. [VERIFIED: https://www.atsb.gov.au/investigations/ao-2018-040]

Problem coverage: both. [VERIFIED: https://www.faa.gov/air_traffic/publications/atpubs/atc_html/appendix_a.html]

Borrowable: use a four-phase handoff gate—preview, exception briefing, explicit acceptance, post-acceptance verification. [UNVERIFIED: application synthesis]

### Nuclear operations: shift turnover and operating logs

URLs: https://www.govinfo.gov/content/pkg/CFR-2025-title10-vol1/pdf/CFR-2025-title10-vol1-sec26-205.pdf; https://www.iaea.org/sites/default/files/documents/review-missions/civauxfureport.pdf

U.S. nuclear regulation defines shift turnover as activities necessary to safely transfer information and responsibilities, including plant-equipment status and ongoing tests of safety systems and components. [VERIFIED: https://www.govinfo.gov/content/pkg/CFR-2025-title10-vol1/pdf/CFR-2025-title10-vol1-sec26-205.pdf]

The IAEA inspection record describes shift logs containing events, activities, next-shift objectives, operator signatures, and traceability of actions. [VERIFIED: https://www.iaea.org/sites/default/files/documents/review-missions/civauxfureport.pdf]

The documented failure mode was record-quality decay: a review found declining quality in shift-log entries and some inappropriate corrections without signatures or initials. [VERIFIED: https://www.iaea.org/sites/default/files/documents/review-missions/civauxfureport.pdf]

The plant responded with completion instructions, end-of-shift systematic log checks, second-level checks, real-time monitoring, and a performance indicator; the report also describes work toward a computerized shift logbook. [VERIFIED: https://www.iaea.org/sites/default/files/documents/review-missions/civauxfureport.pdf]

Activity/adoption signal: the source is an IAEA operational-safety review; the opened U.S. regulation is the 2025 Code of Federal Regulations edition. [VERIFIED: https://www.iaea.org/sites/default/files/documents/review-missions/civauxfureport.pdf]

Problem coverage: both, especially stale or unauditable state. [VERIFIED: https://www.iaea.org/sites/default/files/documents/review-missions/civauxfureport.pdf]

Borrowable: make record quality observable and reviewable at every shift boundary, with signed corrections and an explicit next-shift objective. [UNVERIFIED: application synthesis]

### Incident Command System transfer of command

URLs: https://emilms.fema.gov/_is_0200c/groups/247.html; https://training.fema.gov/emiweb/is/icsresource/assets/nims%20ics%20forms%20booklet.v3.pdf; https://www.usfa.fema.gov/downloads/pdf/publications/field_operations_guide.pdf

FEMA requires a face-to-face transfer when possible, a complete briefing, communication of the effective transfer time, and documentation saved for retrieval. [VERIFIED: https://emilms.fema.gov/_is_0200c/groups/247.html]

The minimum briefing includes situation status, objectives and priorities, current organization, resource assignments, ordered and en-route resources, facilities, communications, prognosis, concerns, related issues, and command-staff identities. [VERIFIED: https://emilms.fema.gov/_is_0200c/groups/247.html]

ICS Form 201 persists the situation summary, hazards, current and planned objectives, actions, organization, and resource status; it is both a briefing document and a permanent record of the initial response. [VERIFIED: https://training.fema.gov/emiweb/is/icsresource/assets/nims%20ics%20forms%20booklet.v3.pdf]

The Field Operations Guide requires transferred information to be recorded and displayed for easy retrieval and subsequent briefings. [VERIFIED: https://www.usfa.fema.gov/downloads/pdf/publications/field_operations_guide.pdf]

The opened sources are doctrine and forms rather than a controlled handoff-effectiveness study. [UNVERIFIED: source-review note]

Activity/adoption signal: FEMA maintains an official ICS forms resource center, and the National Interagency Fire Center’s opened page links a 2026 Red Book and archives back to 1997. [VERIFIED: https://training.fema.gov/emiweb/is/icsresource/icsforms/; https://www.nifc.gov/standards/guides/red-book]

Problem coverage: both. [VERIFIED: https://emilms.fema.gov/_is_0200c/groups/247.html]

Borrowable: model each agent resumption packet on an ICS 201: current state, hazards, objectives, actions, organization, resources, communications, and concerns. [UNVERIFIED: application synthesis]

### Military commander’s intent and operations orders

URL: https://www.benning.army.mil/MCOE/199th/~CATD/MCCC/Reserve/content/pdf/A%20Guide%20to%20the%20MDMP.pdf

The opened Army operations-order guide uses five primary sections: Situation, Mission, Execution, Sustainment, and Command and Control. [VERIFIED: https://www.benning.army.mil/MCOE/199th/~CATD/MCCC/Reserve/content/pdf/A%20Guide%20to%20the%20MDMP.pdf]

The guide specifies that commander’s intent should include key tasks, how success is defined, and the purpose and conditions of the end state. [VERIFIED: https://www.benning.army.mil/MCOE/199th/~CATD/MCCC/Reserve/content/pdf/A%20Guide%20to%20the%20MDMP.pdf]

The same order format carries assumptions, decision points, branches and sequels, critical information requirements, rules of engagement, risk controls, sustainment, communications, and succession of command. [VERIFIED: https://www.benning.army.mil/MCOE/199th/~CATD/MCCC/Reserve/content/pdf/A%20Guide%20to%20the%20MDMP.pdf]

The guide also describes a running estimate as a continuous assessment of the current situation against the commander’s intent and supportability of future operations. [VERIFIED: https://www.benning.army.mil/MCOE/199th/~CATD/MCCC/Reserve/content/pdf/A%20Guide%20to%20the%20MDMP.pdf]

This is a continuity and decision-making doctrine, not a quantitative handoff experiment. [UNVERIFIED: source-review note]

Problem coverage: both, with particular relevance to within-session drift when the original plan no longer applies. [UNVERIFIED: application synthesis]

Borrowable: persist purpose, end state, key tasks, constraints, risks, decision points, and “what would change the plan,” rather than only the current task. [UNVERIFIED: application synthesis]

### Maritime official logbooks

URL: https://www.iomshipregistry.com/media/c1se0xsc/msn-004-official-log-book-and-list-of-crew-march-25-v2.pdf

The Isle of Man Ship Registry guidance requires official-log metadata, master identity, dates, safety records, drills, training, inspections, and narrative entries; it specifically requires the date and time of a master handover to be recorded. [VERIFIED: https://www.iomshipregistry.com/media/c1se0xsc/msn-004-official-log-book-and-list-of-crew-march-25-v2.pdf]

For electronic records, the guidance permits continuous records when identity, backup, and retrievability are maintained; records going back at least three years must remain available onboard. [VERIFIED: https://www.iomshipregistry.com/media/c1se0xsc/msn-004-official-log-book-and-list-of-crew-march-25-v2.pdf]

The guidance requires signatures and counter-signatures in several sections and provides a procedure for reporting a lost logbook and documenting recovery steps. [VERIFIED: https://www.iomshipregistry.com/media/c1se0xsc/msn-004-official-log-book-and-list-of-crew-march-25-v2.pdf]

This source emphasizes legal traceability and retention; it does not provide a measured reduction in handover information loss. [UNVERIFIED: source-review note]

Activity/adoption signal: the opened notice states that its electronic-log provisions apply from 1 April 2025. [VERIFIED: https://www.iomshipregistry.com/media/c1se0xsc/msn-004-official-log-book-and-list-of-crew-march-25-v2.pdf]

Problem coverage: primarily cross-session, with some within-watch value. [UNVERIFIED: application synthesis]

Borrowable: require timestamp, responsible actor, handover event, linked evidence, signed correction history, retention policy, and loss/recovery procedure. [UNVERIFIED: application synthesis]

### Laboratory notebooks and research records

URLs: https://www.med.upenn.edu/bgs-rcr-exdes/case-study-module-1.html; https://techtransfer.cancer.gov/investigators/inventions/guide-lab-records

Penn describes the laboratory notebook as a record of primary and secondary data, collaboration, interpretation, decisions, positive results, and negative results. [VERIFIED: https://www.med.upenn.edu/bgs-rcr-exdes/case-study-module-1.html]

A single experiment entry should include date, purpose, materials, protocol, results, discussion, and next steps, with links to raw and derived data. [VERIFIED: https://www.med.upenn.edu/bgs-rcr-exdes/case-study-module-1.html]

The record must be complete even when an experiment fails or is terminated, readable by others, chronologically organized, and accessible to the principal investigator. [VERIFIED: https://www.med.upenn.edu/bgs-rcr-exdes/case-study-module-1.html]

Penn recommends immutable entries, timestamps, version control, read-only conversion, regular backups, real-time PI access, and explicit documentation of pipeline versions and intermediate outputs. [VERIFIED: https://www.med.upenn.edu/bgs-rcr-exdes/case-study-module-1.html]

NCI guidance adds cross-references, signed and dated pages and attachments, preserved mistakes rather than erased mistakes, write protection, author identity, and time stamps. [VERIFIED: https://techtransfer.cancer.gov/investigators/inventions/guide-lab-records]

Failure mode: individually managed primary data can become lost or lose value because background information and provenance disappear. [VERIFIED: https://www.jstage.jst.go.jp/article/dsj/8/0/8_8-18/_article/-char/en]

Activity/adoption signal: these are institutional and federal research-record guidelines, not commercial products with star or release metrics. [VERIFIED: https://www.med.upenn.edu/bgs-rcr-exdes/case-study-module-1.html]

Problem coverage: both. [VERIFIED: https://www.med.upenn.edu/bgs-rcr-exdes/case-study-module-1.html]

Borrowable: capture every attempt, including dead ends, with provenance, rationale, raw evidence, derived result, and next experiment; make prior entries append-only. [UNVERIFIED: application synthesis]

### Open-notebook science

URLs: https://www.nature.com/articles/npre.2007.1225.1.pdf; https://stevesopenlab.org/

Open-notebook science is described as an online version of the classical lab notebook, exposing discoveries as they happen, including negative results, and enabling immediate feedback. [VERIFIED: https://www.nature.com/articles/npre.2007.1225.1.pdf]

The same source identifies risks including fear of being scooped, lack of credit, and cultural rather than technical barriers. [VERIFIED: https://www.nature.com/articles/npre.2007.1225.1.pdf]

Steve’s Open Lab describes itself as an evolving laboratory notebook in which each article is another step in an investigation; the opened site showed a latest article dated 16 September 2026. [VERIFIED: https://stevesopenlab.org/]

There is no controlled evidence in these opened sources that public notebooks reduce information loss or improve research outcomes. [UNVERIFIED: source-review note]

Problem coverage: both, if the record is continuously visible to the next worker and searchable during active work. [UNVERIFIED: application synthesis]

Borrowable: maintain a continuously visible project stream of experiments, observations, failures, and links to evidence, while using access controls where openness is unsafe. [UNVERIFIED: application synthesis]

### Architecture Decision Records

URLs: https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html; https://gds-way.digital.cabinet-office.gov.uk/standards/architecture-decisions.html; https://martinfowler.com/bliki/ArchitectureDecisionRecord.html

The minimum ADR structure is status, context, decision, and consequences; AWS describes the resulting collection as a project decision log. [VERIFIED: https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html]

GDS recommends storing decisions in version control, preferably in the affected application repository, so changes, authors, and dates remain visible. [VERIFIED: https://gds-way.digital.cabinet-office.gov.uk/standards/architecture-decisions.html]

AWS and Fowler recommend immutability after acceptance: a changed decision becomes a new ADR, and the old ADR is marked superseded and linked forward. [VERIFIED: https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html; https://martinfowler.com/bliki/ArchitectureDecisionRecord.html]

Fowler additionally recommends recording alternatives, trade-offs, confidence, and conditions that should trigger reevaluation. [VERIFIED: https://martinfowler.com/bliki/ArchitectureDecisionRecord.html]

The documented failure mode is loss of rationale as projects age and original participants leave; the main anti-staleness controls are discoverability, review, explicit status, supersession, issue-tracker follow-through, and code-review reference. [VERIFIED: https://gds-way.digital.cabinet-office.gov.uk/standards/architecture-decisions.html]

Adoption signals include AWS guidance, a GOV.UK ADR framework published 4 November 2025, and a Ministry of Justice index listing ADR-000 through ADR-011 with Proposed, Accepted, Rejected, Superseded, and Amended states. [VERIFIED: https://www.gov.uk/government/publications/architectural-decision-record-framework; https://dev.developer-portal.service.justice.gov.uk/docs/analytical-platform/adrs/adr-index]

The Ministry of Justice index also exposes the staleness problem: it reports “Last reviewed: 19 December 2024” and “Review status: Review overdue.” [VERIFIED: https://dev.developer-portal.service.justice.gov.uk/docs/analytical-platform/adrs/adr-index]

Problem coverage: primarily cross-session, with decision-seam protection against within-session drift. [UNVERIFIED: application synthesis]

Borrowable: use one immutable record per consequential decision, including rationale, alternatives, confidence, consequences, owner, review triggers, and superseding links. [UNVERIFIED: application synthesis]

## Mapping the strongest mechanisms to AI-agent continuity

- Structured minimum packet: carry purpose/current state, completed work, action list with owner and deadline, risks, contingencies, and unresolved questions. This combines I-PASS, SBAR, ICS, and FAA practice. [UNVERIFIED: application synthesis based on https://www.ahrq.gov/teamstepps-program/curriculum/communication/tools/ipass.html; https://emilms.fema.gov/_is_0200c/groups/247.html; https://www.faa.gov/air_traffic/publications/atpubs/atc_html/appendix_a.html]
- Receiver-side synthesis: the new session must summarize what it understood, ask questions, restate next actions, and verify the repository state before acting. This directly mirrors I-PASS synthesis, SBAR repeat-back, FAA preview/review, and HSE cross-checking. [UNVERIFIED: application synthesis based on https://www.ahrq.gov/teamstepps-program/curriculum/communication/tools/ipass.html; https://www.ahrq.gov/teamstepps-program/curriculum/communication/tools/sbar.html; https://www.faa.gov/air_traffic/publications/atpubs/atc_html/appendix_a.html; https://www.hse.gov.uk/humanfactors/topics/shift-handover.htm]
- Explicit purpose and drift boundaries: persist the project’s purpose, desired end state, key tasks, constraints, risks, and conditions that trigger a plan change. This is the most transferable part of commander’s intent and ADRs. [UNVERIFIED: application synthesis based on https://www.benning.army.mil/MCOE/199th/~CATD/MCCC/Reserve/content/pdf/A%20Guide%20to%20the%20MDMP.pdf; https://martinfowler.com/bliki/ArchitectureDecisionRecord.html]
- Append-only history with supersession: preserve failed attempts and old decisions, but mark them clearly as rejected, superseded, or stale rather than silently rewriting them. [UNVERIFIED: application synthesis based on https://www.med.upenn.edu/bgs-rcr-exdes/case-study-module-1.html; https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html]
- Freshness instrumentation: require timestamps, operational-period boundaries, end-of-session checks, review dates, and automated warnings for overdue or unverified state. The nuclear-log and ADR examples show that records decay unless freshness is actively monitored. [UNVERIFIED: application synthesis based on https://www.iaea.org/sites/default/files/documents/review-missions/civauxfureport.pdf; https://dev.developer-portal.service.justice.gov.uk/docs/analytical-platform/adrs/adr-index]

## Queries run

- `clinical handoff SBAR I-PASS outcome study omission rates systematic review`
- `I-PASS handoff medical errors preventable adverse events study NEJM 2014`
- `SBAR handoff what information must include evidence study`
- `clinical handoff stale unread handoff information failure modes study`
- `nuclear power plant shift turnover log handover human factors operating experience report`
- `NRC nuclear shift turnover communication logs required information guidance`
- `air traffic control shift handover position relief briefing checklist study errors`
- `aviation shift handover logbook fatigue handoff failure study`
- `site:fema.gov ICS transfer of command briefing information must include current situation resources objectives`
- `FEMA Incident Command System transfer of command briefing checklist ICS 201 202 204`
- `incident command handoff shift change failure information loss study emergency management`
- `ICS forms incident action plan operational period handoff continuity lessons learned`
- `site:army.mil commander's intent purpose key tasks end state ADP 5-0 PDF`
- `site:army.mil operation order five paragraph format situation mission execution sustainment command signal PDF`
- `military commander's intent shared understanding initiative failure mission command official doctrine`
- `site:army.mil field manual commander's intent constraints acceptable risk end state`
- `IMO ship logbook records entries bridge logbook official guidance continuity watch handover`
- `site:imo.org bridge watch handover information logbook master standing orders`
- `maritime watch handover checklist information must be exchanged study accidents`
- `aviation maintenance logbook required entries FAA regulation aircraft maintenance records continuity`
- `research laboratory notebook best practices contemporaneous dated signed raw data failed experiments official university`
- `site:nih.gov laboratory notebook record keeping date raw data failed experiments`
- `open notebook science lab notebook public real time research project example`
- `scientific lab notebook continuity handover researchers reproducibility study lost information`
- `Architecture Decision Records ADR context decision status consequences superseded official`
- `site:adr.github.io architecture decision records format status context decision consequences`
- `Michael Nygard document architecture decisions lightweight ADR original`
- `architecture decision records stale outdated superseded decisions maintenance study`
- `incident command transfer of command briefing checklist evaluation study information loss emergency responders`
- `fire incident command transfer briefing checklist outcome study handoff errors`
- `FEMA ICS handoff effectiveness evidence study transfer command`
- `emergency incident management shift handover information loss field study`
- `site:ahrq.gov I-PASS illness severity patient summary action list contingency plans synthesis receiver`
- `I-PASS handoff mnemonic illness severity patient summary action list situation awareness contingency planning synthesis receiver official`
- `I-PASS handoff bundle key elements study written oral handoff`

## Not found / limits

- I did not find an opened, controlled quantitative study showing that ICS or fire-command transfer checklists reduce information loss by a specific percentage. The sources found were official doctrine, forms, and operational guidance. [UNVERIFIED: search-process report]
- I did not find a comparable quantitative before/after study for nuclear shift turnover or maritime logbooks. [UNVERIFIED: search-process report]
- Open-notebook science produced conceptual material and a live example, but no opened outcome study demonstrating reduced continuity loss. [UNVERIFIED: search-process report]
- Several maritime accident-report pages appeared in search results but could not be opened because the web fetch returned access errors; I excluded their substantive claims from the verified findings. [UNVERIFIED: tool-result report]
- Stars, installs, and release counts were generally not meaningful for standards, regulations, doctrine, or institutional guidance, so adoption signals are represented by participating sites, official publication/update dates, active registries, and current operational pages. [UNVERIFIED: search-process report]
- The mapping to AI-agent behavior is synthesis from these fields, not evidence that any one mechanism has been validated for coding agents. [UNVERIFIED: synthesis]

---

## Lane prompt (angle)

NON-AI FIELDS THAT SOLVED CONTINUITY. The same structural problem — a long-running stateful undertaking handled by a sequence of workers who each lose memory at shift end — has decades of practice outside software AI. Research: clinical shift handover (SBAR, I-PASS and its outcome studies), nuclear plant and air traffic control shift turnover/logs, incident command handoff (ICS), military commander's intent and orders format, maritime/aviation logbooks, long-running scientific lab notebooks and open-notebook science, and "decision records" (ADRs) in software architecture. For each: what the handover or record MUST contain, what failure modes the field documented (e.g. handoff omission rates, what gets lost), what mechanisms measurably reduced loss (with the evidence), and how the field keeps the record from going stale or unread. End with a short section mapping the 3-5 strongest mechanisms to the AI-agent problem.
