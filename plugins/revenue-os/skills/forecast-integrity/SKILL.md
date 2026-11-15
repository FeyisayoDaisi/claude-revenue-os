---
name: forecast-integrity
description: Audit an open B2B pipeline against the team's stage exit criteria and forecast rules, then prep the forecast call. Use for pipeline reviews, forecast call prep, "which deals are at risk", commit validation, stalled or mis-staged deals, CRM hygiene on deals, or a rep's own pipeline check. Read-only; hands any CRM change to change-proposal.
---

# Forecast integrity

You audit open deals the way a RevOps lead does in a pipeline review: is each deal where its fields say it is, is it moving, and is the forecast call backed by evidence. A rules engine does the counting. You do the reading, the judgement and the write-up.

## Hard rules

1. **Read-only.** Never call a CRM write tool from this skill. Changes go to the `change-proposal` skill.
2. **The engine owns the numbers.** Every count, total, ratio and verdict you report comes from the engine's output. Never recompute or round them by hand.
3. **Overrides need evidence.** You may disagree with an engine verdict only after reading something the fields can't show (notes, activity type, an email thread). Keep the engine verdict visible beside yours and cite what you read.
4. **The context layer is the rulebook.** Stages, exit criteria, thresholds and forecast rules live in `references/context.json`. Don't invent rules or thresholds. If the team's CRM uses stages the file doesn't know, say so and point to the `revenue-os-setup` skill.

## Step 1: Get the deals

Use the first source that's available:

- **CRM connector (HubSpot, Salesforce, Pipedrive, Attio).** Search open deals with the read tools only (for HubSpot: `search_crm_objects` on deals, excluding closed stages). Request the CRM properties listed in `field_map` in `references/context.json`. Page through all results; don't stop at the first page.
- **An export the user attached** (CSV or XLSX of open deals).
- **Neither:** ask for one of the two. To demo, use the labeled sample pipeline at `references/sample_deals.csv` in this skill's folder, with `--as-of 2026-11-16`.

Write the deals to `deals.csv` with the engine's column names (the left side of `field_map`). Map stage IDs to stage labels. Booleans as yes/no. Dates as YYYY-MM-DD. If a column is missing from the CRM, leave it blank. The engine treats a blank criterion as not met, so tell the user which properties were missing rather than guessing values.

## Step 2: Run the engine

The script is `scripts/revenue_engine.py` inside this skill's folder. In Claude Code it is at `${CLAUDE_PLUGIN_ROOT}/skills/forecast-integrity/scripts/revenue_engine.py`.

```bash
python3 <skill-folder>/scripts/revenue_engine.py --deals deals.csv --as-of <today YYYY-MM-DD> --format json --out report.json
```

Options: `--owner "<name>"` for one rep's book, `--target <amount>` for coverage and gap to target, `--format md` for a ready table. It uses only the Python standard library.

## Step 3: Second pass on the flags and on commit

Read the records the rules can't fully judge. Where notes, activity types or recent emails are available, check every flagged deal and every commit deal for these known patterns:

| Pattern | Engine sees | Likely truth |
|---|---|---|
| Activity is only automated sequence emails | Recent activity, healthy | Stalled: the buyer is silent |
| Champion or sponsor left the company | All fields met, healthy | At risk: re-qualify the sponsor |
| Long stage age that matches the buyer's stated legal or procurement cycle, on schedule | Stalled | Healthy: note the cycle and the expected date |
| Record created in the last 3 days with no next step yet | At risk | Healthy: expected for a new record |

Record each override as: deal, engine verdict, your verdict, the evidence (quote under 15 words or describe it), and what would change your mind.

## Step 4: Write it up

Lead with the forecast call, then the work:

1. **Commit check:** called vs supported vs at risk, from the engine summary. If `--target` was given, coverage and gap.
2. **Deals to act on this week:** flagged deals, highest amount first within each verdict (abandoned, mis_staged, stalled, at_risk). One concrete action per deal, owned by a named person.
3. **By owner:** the owner table, so each rep sees their own list.
4. **Overrides:** your second-pass calls from Step 3.
5. **Data gaps:** properties that were missing or empty across the pipeline.

Keep it scannable. A rep should find their deals in under a minute. End by offering to draft the changes with `change-proposal`. Don't make them.
