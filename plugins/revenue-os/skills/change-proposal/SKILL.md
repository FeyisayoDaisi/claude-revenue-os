---
name: change-proposal
description: Turn pipeline findings into a reviewed set of CRM changes and rep nudges, and apply approved changes one at a time with the user confirming each write. Use after a forecast-integrity review, or when asked to fix, update or clean up deal records, close dates, stages, next steps or forecast categories.
---

# Change proposal

Writes are where AI in a CRM goes wrong: a confident update to the wrong record, a close date a rep didn't agree to, a bulk change nobody reviewed. This skill keeps every change visible, owned and approved.

## Never in an unattended run

If this session was started by a schedule, or no person is responding, **draft the proposal and stop**. Scheduled runs have no approval prompts, so nothing in them can count as approval. Save the proposal as the run's output. Applying changes waits for a live session.

## Step 1: Classify each change

| Class | Examples | What you do |
|---|---|---|
| A. Additive | Add a next-step task, log a note that records the review, add a missing association | Propose, then apply only after the user approves it in this session |
| B. Rep-owned | Close date, amount, stage, forecast category, deal owner | **Never write.** Draft a nudge to the owner with the evidence. The rep makes the change |
| C. Destructive | Delete, merge, bulk overwrite, closing a deal lost | **Never write.** List it for the RevOps owner to handle in the CRM directly |

Stage and forecast category are rep-owned on purpose. Moving them is a forecast decision, and the person accountable for the number makes it.

## Step 2: Present the proposal

One table, nothing applied yet:

| # | Record | Class | Field | Current | Proposed | Reason (engine finding) | Evidence |
|---|---|---|---|---|---|---|---|

Under it, draft the owner nudges for class B, grouped by rep. Each nudge names the deal, says what looks wrong in one line, gives the evidence and asks one question. Plain and friendly, no blame. Example: "Kestrel Health is in Proposal but the CRM has no decision maker. Who signs, and can we add them before Thursday's call?"

## Step 3: Apply approved class A changes

Only after the user says which rows to apply:

1. Confirm the CRM connector's write tools are set to **Needs approval** (see `references/permission-matrix.md` in the `revenue-os-setup` skill). If they are set to Always allow, tell the user and ask them to change it before you continue.
2. Apply **one record per tool call**. No bulk writes.
3. Before each call, restate the record, field, current value and new value.
4. After each call, re-read the record and confirm the value changed. If it didn't, stop and report it.
5. Finish with a change log: record, field, old value, new value, time, approved by.

If the user asks you to apply a class B or C change anyway, explain once that the plugin's governance keeps it with the owner, and offer the nudge or the RevOps-owner list instead.
