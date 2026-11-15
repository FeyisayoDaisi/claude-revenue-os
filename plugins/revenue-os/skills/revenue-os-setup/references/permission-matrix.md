# Connector permission matrix

Set per tool, per role. In Claude each connector tool can be **Always allow**, **Needs approval** or **Blocked**. On Team plans the owner sets these organization-wide. On Enterprise they can differ by custom role.

## CRM connector (HubSpot shown; apply the same split to Salesforce, Pipedrive, Attio)

| Tool type | HubSpot tools | Rep | Sales manager | RevOps owner |
|---|---|---|---|---|
| Search and read records | `search_crm_objects`, `get_crm_objects`, `query_crm_data` | Always allow | Always allow | Always allow |
| Read schema and owners | `get_properties`, `search_properties`, `search_owners`, `get_user_details` | Always allow | Always allow | Always allow |
| Create or update records | `manage_crm_objects` | Needs approval | Needs approval | Needs approval |
| Delete, merge, bulk import | any delete, merge or import tool | Blocked | Blocked | Blocked (do it in the CRM) |

Tool names change as connectors add tools. Recheck the list in each connector's settings, not just this table.

## Delivery connectors used by the scheduled brief

| Connector | Tool | RevOps owner (runs the brief) | Everyone else |
|---|---|---|---|
| Slack | post a message | Always allow, and name one channel in the task prompt | Needs approval |
| Gmail | create draft | Always allow | Always allow |
| Gmail | send | Needs approval | Needs approval |

Connector permissions can't limit a tool to one channel. The skill and the task prompt do that, so check the first few runs.

## Why these defaults

- **Reads open, writes gated.** The value is in reading the whole pipeline every week. The risk is in writes.
- **Needs approval, not Always allow, on writes.** In Cowork a member confirms each write unless the organization allows Always allow for connector tools. Keep that setting off for CRM write tools.
- **Stage, amount, close date and forecast category are never written by Claude.** The `change-proposal` skill drafts a nudge to the deal owner instead. The person accountable for the number moves it.

## Known ways these settings drift

Check these after setup, after every plugin update and once a month:

1. **Per-tool settings reset.** Treat Always allow and Needs approval as something to recheck after a connector reconnects or a plugin updates. Open each CRM connector and confirm the write tools still say Needs approval.
2. **Enterprise roles seeded wide open.** When connector permissions are first turned on for an organization, existing custom roles start at "All connectors: Always allow". New roles start at Needs approval. Audit the existing roles.
3. **Claude Code uses its own permission rules.** Don't rely on claude.ai's per-tool toggles alone in the Claude Code CLI. The plugin's hook (`hooks/hooks.json`) forces a prompt on CRM write tools, and `claude-code-settings.json` adds `ask` rules as a second layer.
4. **Scheduled runs behave differently.** Claude Code's cloud scheduled tasks run with no approval prompts. Revenue OS's scheduled brief never writes to the CRM. Run it as a Claude scheduled task, not a Claude Code routine, and test it once with the write-block test in the rollout checklist.
