# Rollout playbook

How to take a revenue team from "a few reps use Claude" to "the team runs its pipeline review on it". Four phases, about five weeks. Each phase has an exit test. Don't start the next phase until it passes.

## Phase 0: Readiness (week 1)

**Owner:** RevOps lead, with the Claude admin.

- [ ] Team or Enterprise plan, with the plugin marketplace added: Customize > Plugins > Add marketplace > `FeyisayoDaisi/claude-revenue-os` (or a fork you control).
- [ ] CRM connector connected for the pilot group. Read tools Always allow, write tools Needs approval, delete and merge tools Blocked (`permission-matrix.md`).
- [ ] Enterprise: audit existing custom roles. Roles that existed before connector permissions were enabled start wide open.
- [ ] Run `revenue-os-setup` with the sales leader: stages, exit criteria, thresholds, commit rules, field map. Merge the `context.json` change through a pull request.
- [ ] Data check: run `forecast-integrity` once. If more than a fifth of deals show missing properties, fix the CRM fields first, or the review will mostly report data gaps.

**Exit test:** the sales leader agrees with the verdict on 10 deals they pick at random.

## Phase 1: Pilot (weeks 2 and 3)

**Who:** one manager and their reps, three to six people.

- [ ] Run the weekly pipeline review from `forecast-integrity` for two weeks in a row.
- [ ] Reps get their nudges from `change-proposal` and make the changes themselves.
- [ ] RevOps owner creates the Monday brief (`scheduled-tasks.md`) and runs it once with Run now before the first scheduled run.
- [ ] **Write-block test:** create a one-off scheduled task that asks Claude to add a note to a test deal. Confirm it was blocked or stopped for approval, and that the CRM audit log shows no write. If the write went through, don't schedule anything else until the permission settings are fixed.

**Exit test:** two consecutive reviews where the team trusted the commit check, and no unapproved writes in the CRM audit log.

## Phase 2: Team (weeks 4 and 5)

- [ ] Require the plugin for the sales group (Team and Enterprise admins can make a plugin required).
- [ ] 30-minute session per team: how to ask for their own book (`--owner`), how to read a nudge, why stage and close date stay with them.
- [ ] Name one champion per team who collects "the engine got this wrong" cases.
- [ ] Every rule change goes through a pull request on `context.json` and ships as a plugin update. Recheck connector permissions after each update.

**Exit test:** every manager runs their own review without RevOps in the room.

## Phase 3: Measure and keep (ongoing)

Review monthly, using the metrics in `adoption-metrics.md`. Feed each "engine got it wrong" case into `data/labels.csv` and rerun `python3 eval/run_eval.py`. A rule change ships only if the eval still passes.

## Risks and what to do

| Risk | Signal | Response |
|---|---|---|
| Reps ignore nudges | Same flagged deals two weeks running | Manager walks the list in 1:1s. The nudge is the agenda, not a report |
| Rules don't fit how the team sells | Many overrides on one finding type | Change the threshold or criterion in `context.json` through a PR |
| Permission drift | Writes in the audit log without a matching approved change log | Reset write tools to Needs approval, rerun the write-block test |
| Usage limits | Scheduled brief fails or is late | Cut to the weekly brief only; move rep versions to on-demand |
| Bad CRM data | Data gaps section is long | Fix fields first; the review is only as good as the properties it reads |
