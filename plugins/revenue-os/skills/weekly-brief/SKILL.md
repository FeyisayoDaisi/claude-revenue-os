---
name: weekly-brief
description: Produce the weekly forecast-risk brief for a sales team, built to run as a scheduled task with no one watching. Use when a schedule fires the brief, or when asked for the Monday pipeline brief, weekly forecast digest or pipeline health summary.
---

# Weekly brief

This skill is built to run unattended. Everything in it is read-only except one delivery step the task owner chose in advance.

## Rules for unattended runs

- **No CRM writes.** Not even additive ones. Scheduled runs have no approval prompts.
- **No messages to individual reps.** Delivery goes to one place only: the channel, inbox draft or file named in the scheduled task's prompt. If none is named, return the brief as the run's output.
- **Fail loudly.** If the CRM connector fails or needs approval, don't fill gaps from memory or earlier runs. Put "Brief incomplete: <what failed>" as the first line and stop.
- **Stamp it.** Start with the as-of date, the context layer version and the number of deals read, so a reader can tell a fresh brief from a stale one.

## Steps

1. Run the `forecast-integrity` skill, Steps 1 and 2, across the whole open pipeline. Use today's date for `--as-of` and the task's target if it gives one.
2. Skip the per-deal second pass unless the task says otherwise. Note in the brief that verdicts are engine verdicts.
3. Write the brief in this shape, under 250 words plus the table:

```
Pipeline brief, week of <date>  |  context v<version>  |  <n> open deals

Commit: <called> called, <supported> supported, <at risk> at risk
Coverage: <ratio>x of <target>   (only if a target was given)

Top 5 deals to act on this week
| Deal | Owner | Amount | Verdict | Do this |

By owner: <name> <flagged>/<deals> flagged, ...

Changes since last week: <only if the previous brief is available in the destination; otherwise omit>
```

4. Deliver it to the destination named in the task, then end. Offer `change-proposal` as the next step in a line at the bottom, for whoever reads it in a live session.
