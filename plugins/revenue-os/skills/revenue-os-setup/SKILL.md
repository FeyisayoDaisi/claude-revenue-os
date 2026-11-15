---
name: revenue-os-setup
description: Set up Revenue OS for a sales team. Captures the team's stages, exit criteria and forecast rules into the context layer, checks connectors and their tool permissions, and writes the scheduled task. Use when installing or configuring Revenue OS, changing stage definitions or forecast rules, or onboarding a new team.
---

# Revenue OS setup

You are configuring this plugin for one team. The output is a context layer the whole team shares, connectors set up safely, and one scheduled brief. Ask one question at a time. Skip anything the user has already answered or attached.

## Step 1: The team's rules

Start from `../forecast-integrity/references/context.json` (the defaults) and ask:

1. Which CRM, and which pipeline? Pull the real stage names from the CRM if the connector is available.
2. For each stage, what must be true before a deal leaves it? Map each answer to a yes/no deal property. If no property exists, say so: the rule can't be checked until one exists.
3. Days a deal can sit in each stage before it counts as stuck.
4. Days without activity before a deal is dark, and before it's abandoned.
5. What a deal needs before a rep may call it commit.
6. The CRM property names behind each engine field (fill in `field_map`).

Write the updated `context.json`, bump its `version`, and show the diff. Tell the user the change ships to the team when an admin commits it to the plugin repository and publishes a plugin update. That's how everyone, including scheduled tasks, reads the same rules.

## Step 2: Connectors and permissions

Check, and tell the user what you find:

- The CRM connector is connected, and reads return deals.
- **Write tools are set to Needs approval, or Blocked.** Never Always allow. Per-tool settings can reset after a plugin update or reconnect, so recheck after every update. Use the matrix in `references/permission-matrix.md`.
- **Claude Code users:** the claude.ai per-tool approval settings are not reliably applied in the CLI. The plugin's hook prompts on CRM write tools. Also add the `ask` rules from `references/claude-code-settings.json`.
- **HubSpot with Sensitive Data turned on:** activity and conversation data may not come through the connector. Activity-based checks will show as missing data.

## Step 3: The scheduled brief

Draft the scheduled task, but let the user create it (Scheduled in the sidebar, or ask Claude to schedule it). Use the template in `references/scheduled-tasks.md`. Make sure they know:

- A scheduled task belongs to the person who creates it, runs as them, uses their connectors and counts against their usage. Have the RevOps owner create the team brief, not every rep.
- Plans limit cloud scheduled runs, so one weekly brief plus an optional mid-week check is the right size.
- Scheduled tasks can't read local folders. Everything the brief needs comes from connectors and the plugin.

## Step 4: Prove it works

Run `forecast-integrity` on the team's real pipeline, or on the forecast-integrity skill's `references/sample_deals.csv` with `--as-of 2026-11-16` for a demo. Walk through three flagged deals with the user and confirm the verdicts match how they'd call them. Where they disagree, decide together whether the rule or the threshold should change, and go back to Step 1 if so.
