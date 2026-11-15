# Research: why this exists, and what had to be true for it to work

Researched November 2026. Two questions: what are companies hiring people to do with Claude in revenue teams, and what does it take for a Claude setup to work across a team rather than for one rep?

## 1. What the market is hiring for

The work is rarely titled "Claude". It sits inside RevOps, GTM engineering and AI enablement roles, and the job descriptions describe the same thing: turn Claude into a governed system a whole revenue team runs on.

| Role | What the posting asks for |
|---|---|
| AI Operations, GTM (Hightouch) | Own the AI context layer: build and maintain Claude skills and the knowledge systems that make the team's AI tools better over time. Background in RevOps or GTM operations. |
| GTM Engineer, Revenue Operations (Freshworks) | Build agents and AI workflows with Claude, MCP and similar tools. Needs someone who has built solutions personally, not only managed tools. |
| AI Enablement Lead (Indicium AI) | Take clients from Claude licenses to daily use: configure connectors and MCP servers, admin settings and audit logging, choose first use cases and decide where a person reviews the output. |
| Senior Manager, AI Enablement (CodePath) | Mid-rollout of Claude Enterprise. Build the skills, plugins and templates teams use after the engagement ends. |
| GTM Strategy & Operations, FDE (Anthropic) | Use Claude Code and agents to build and run the models, dashboards and workflows the role depends on. |
| Staff SWE, GTM AI Engineering (Anthropic) | Build agents for go-to-market work, with evaluation, production monitoring and ROI measurement. |

**The problem underneath.** Reps spend most of their week on non-selling work (Salesforce surveyed 5,500 sales professionals and put it at 70%). A Claude setup built for one rep doesn't carry to a team: Arrows, which tried running its own sales team in Claude, says teams need shared playbooks rather than individual setups in individual accounts. And CRM data quality is the bottleneck RevOps teams report most often.

**What's already a commodity.** Free RevOps skill packs already exist (Default ships 32; the Salesforce plugin for Claude ships 37 sales skills; Anthropic's own sales plugin includes pipeline review and forecast skills). Another pack of prompts isn't the gap. The gap is the deployment layer the enablement roles pay for: one shared rulebook, safe connector permissions, unattended runs that can't do damage, and evidence that the output is right.

## 2. Engineering findings: the hidden burdens

Each finding below changed the design.

| # | Finding | Design response |
|---|---|---|
| 1 | Scheduled tasks belong to one account. They run as that person, use their connectors, count against their usage and aren't shared with teammates. | One RevOps owner runs the team brief. Reps can add a personal version. Documented in `scheduled-tasks.md`. |
| 2 | Plans cap scheduled runs. Users have reported limits on daily cloud scheduled sessions, undocumented per tier at the time. | Right-sized schedule: one weekly brief, one optional mid-week check. |
| 3 | Claude Code's cloud scheduled tasks run with no approval prompts, so nobody is there to approve a write during a run. | Scheduled skills are read-only by design. Writes only happen in a live session through `change-proposal`. The rollout checklist includes a write-block test. |
| 4 | Claude Code applies its own permission rules, so claude.ai's per-tool approval settings shouldn't be relied on alone there. | A plugin hook forces an approval prompt on CRM write tools by regex, plus `ask` rules in `claude-code-settings.json`. |
| 5 | Connector permissions need rechecking after reconnects and plugin updates. On Enterprise, existing custom roles start at "All connectors: Always allow" when connector permissions are first enabled. | The permission matrix includes a drift checklist: recheck after every update and monthly. |
| 6 | Hooks and subagents run in Cowork, not in chat. Skills work across chat, Cowork and Claude Code. | All logic lives in skills. The hook is a backstop, not the main control. |
| 7 | claude.ai and Cowork refuse plugins with a top-level `bin/` directory. Plugin names starting with `claude-` are reserved. | No `bin/`. Plugin named `revenue-os`. Both enforced by tests. |
| 8 | Scheduled tasks can't read a folder on someone's computer. | The context layer ships inside the plugin, so every run, attended or not, reads the same rules. |
| 9 | Language models aren't reliable calculators across repeated runs. | A deterministic Python engine (standard library only, nothing to install) produces every count and total. Claude reads, judges and writes. |
| 10 | HubSpot's connector writes are logged in HubSpot's audit log against the user and the connector. HubSpot recommends Needs approval on write tools. With Sensitive Data turned on, activity data may be blocked through MCP. | Writes gated at Needs approval. The setup skill warns about Sensitive Data and treats missing activity as a data gap, not a healthy deal. |
| 11 | A Git repository can act as a plugin marketplace, added in Customize > Plugins by `owner/repo`. Team and Enterprise admins can require plugins org-wide. | This repository is the marketplace. Rule changes ship as plugin updates through pull requests. |
| 12 | `claude plugin eval` runs behavioral eval cases against a plugin with a no-plugin baseline, and every run is a paid model call. | Two eval layers: a free deterministic harness for the engine, and authored plugin eval cases for Claude's behavior, run on demand. |

## Sources

- [Hightouch: AI Operations, GTM](https://job-boards.greenhouse.io/hightouch/jobs/5823552004)
- [Freshworks: GTM Engineer, Revenue Operations](https://revopscareers.com/job/whatjobs-us-freshworks-gtm-engineer-revenue-operations-atherton-united-states/)
- [Indicium AI: AI Enablement Lead](https://job-boards.eu.greenhouse.io/indiciumai/jobs/4955405101)
- [CodePath: Senior Manager of AI Enablement](https://edtechjobs.io/jobs/7d81719d-37bb-453c-957f-60ea6b7051ee-senior-manager-of-ai-enablement)
- [Anthropic: GTM Strategy & Operations, FDE](https://job-boards.greenhouse.io/anthropic/jobs/5427938008)
- [Anthropic: Staff Software Engineer, GTM AI Engineering](https://job-boards.greenhouse.io/anthropic/jobs/5390966008)
- [Composio: Claude skills for sales (Salesforce survey figure)](https://composio.dev/content/claude-skills-for-sales-prospecting-outreach-crm-hygiene)
- [Arrows: Claude Cowork for sales](https://arrows.to/resources/claude-cowork-for-sales)
- [SyncGTM: Claude skills for RevOps](https://syncgtm.com/blog/best-claude-skills-for-revops)
- [Default: free RevOps skills](https://www.default.com/skills)
- [Unite.AI: Salesforce in Claude plugin](https://www.unite.ai/?p=467393)
- [Claude for sales](https://claude.com/solutions/sales)
- [Claude Code docs: cloud scheduled tasks](https://code.claude.com/docs/en/web-scheduled-tasks)
- [Claude Code docs: routines](https://code.claude.com/docs/en/routines.md)
- [Claude Help Center: schedule recurring tasks](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork)
- [GitHub issue 40124: scheduled task limits undocumented](https://github.com/anthropics/claude-code/issues/40124)
- [Claude Help Center: role-based connector permissions](https://support.claude.com/en/articles/13930458)
- [Anthropic Academy: deploying Claude Enterprise, connectors](https://academy.claude.com/courses/deploying-claude-enterprise-with-confidence/connectors)
- [Claude docs: plugins overview](https://claude.com/docs/plugins/overview)
- [Claude docs: plugins in Cowork](https://claude.com/docs/cowork/guide/plugins)
- [Claude Help Center: use plugins in Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude-cowork)
- [Claude Code docs: plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- [Claude Code docs: create a marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude Code docs: hooks](https://code.claude.com/docs/en/hooks)
- [Claude Code docs: plugin evals](https://code.claude.com/docs/en/plugin-evals.md)
- [Coffee.ai: Claude and HubSpot setup](https://www.coffee.ai/articles/?p=11049)
- [eesel: Claude for HubSpot](https://www.eesel.ai/blog/claude-for-hubspot)
