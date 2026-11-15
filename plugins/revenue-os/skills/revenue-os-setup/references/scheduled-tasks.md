# Scheduled tasks

## How scheduled tasks actually work (read before creating one)

- **One person owns each task.** It runs as them, uses their connectors and counts against their usage. Teammates can't see or share it.
- **Plans cap scheduled runs.** Users have reported limits on cloud scheduled sessions per day, so keep the team to a weekly brief and, at most, one mid-week check.
- **No approval prompts during a run.** Nobody is there to approve, so the brief is read-only. Changes wait for a live session with `change-proposal`.
- **No local folders.** A scheduled task works from connectors and the files saved to the Claude account. Everything the brief needs is in the CRM connector and this plugin.
- **The brief uses the plugin's context layer.** When the team's rules change, update `context.json` through the plugin, and the next run picks it up. Don't paste rules into the task prompt, where they'd drift from everyone else's.

Recommended owner: the RevOps lead or sales ops owner, on a Team or Enterprise seat, with the CRM connector set to read tools Always allow and write tools Needs approval.

## Task 1: Monday forecast-risk brief

Schedule: weekly, Monday 07:40 in the team's main time zone (off the hour, so it isn't queued behind every other task set for the top of the hour).

Prompt:

```
Run the revenue-os weekly-brief skill on our open pipeline in HubSpot.
Quarter target: <amount>. Deliver the brief as a post in Slack #<channel>.
Do not write to the CRM and do not message individual reps.
If any connector call fails, post "Brief incomplete" with what failed and stop.
```

## Task 2 (optional): Thursday commit check

Schedule: weekly, Thursday 13:10.

Prompt:

```
Run the revenue-os forecast-integrity skill, read-only, on deals in the Commit
forecast category only. Post a five-line summary to Slack #<channel>: commit
called, commit supported, the deals at risk with owner and the one fix each.
Do not write to the CRM.
```

## Rep version (optional, each rep creates their own)

```
Every weekday at 08:20, run the revenue-os forecast-integrity skill with
--owner "<my name>" and send me the five deals I should act on today, as a
Gmail draft to myself. Read-only.
```

## Test before you trust it

Run each task once with **Run now** and check:

1. The brief's first line has today's date, the context version and a deal count that matches the CRM.
2. The commit totals match the CRM's own forecast view.
3. Nothing changed in the CRM. Check the audit log for writes attributed to the connector.
