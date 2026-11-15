# Forecast integrity report (as of 2026-11-16)

Context layer version 1.0.0. 57 open deals, $2,749,000 open pipeline, $1,330,200 weighted.

## Commit

- Called: $348,000
- Supported by exit criteria and healthy: $48,000
- At risk: $300,000
- Target: $600,000, coverage 4.58x, gap after supported commit $552,000

## Deals by verdict

| Verdict | Deals | Amount |
|---|---:|---:|
| abandoned | 5 | $78,000 |
| mis_staged | 8 | $398,000 |
| stalled | 11 | $337,000 |
| at_risk | 13 | $914,000 |
| healthy | 20 | $1,022,000 |

## By owner

| Owner | Deals | Flagged | Flagged amount |
|---|---:|---:|---:|
| Amara Obi | 15 | 8 | $324,000 |
| Daniel Reyes | 14 | 10 | $531,000 |
| Priya Nair | 14 | 9 | $372,000 |
| Tom Becker | 14 | 10 | $500,000 |

## Flagged deals

| Deal | Owner | Stage | Amount | Verdict | Findings |
|---|---|---|---:|---|---|
| Meridian Labs Renewal (D-1048) | Amara Obi | Proposal | $24,000 | abandoned | ABANDONED_ACTIVITY: No activity for 64 days; CLOSE_DATE_PAST: Close date 2026-10-07 has passed while the deal is open; NEXT_STEP_OVERDUE: Next step was due 2026-09-28 |
| Delta Grain Renewal (D-1054) | Priya Nair | Qualified | $18,000 | abandoned | ABANDONED_ACTIVITY: No activity for 50 days; CLOSE_DATE_PAST: Close date 2026-10-19 has passed while the deal is open; NEXT_STEP_OVERDUE: Next step was due 2026-09-19 |
| Cobalt Analytics Platform (D-1005) | Daniel Reyes | Discovery | $12,000 | abandoned | ABANDONED_ACTIVITY: No activity for 82 days; CLOSE_DATE_PAST: Close date 2026-10-18 has passed while the deal is open; NEXT_STEP_OVERDUE: Next step was due 2026-10-15 |
| Harbor Legal Platform (D-1006) | Priya Nair | Proposal | $12,000 | abandoned | ABANDONED_ACTIVITY: No activity for 54 days; CLOSE_DATE_PAST: Close date 2026-10-20 has passed while the deal is open; NEXT_STEP_OVERDUE: Next step was due 2026-09-27 |
| Juniper Retail Platform (D-1010) | Priya Nair | Solution | $12,000 | abandoned | ABANDONED_ACTIVITY: No activity for 68 days; CLOSE_DATE_PAST: Close date 2026-11-08 has passed while the deal is open; NEXT_STEP_OVERDUE: Next step was due 2026-10-03 |
| Helix Bio Expansion (D-1038) | Priya Nair | Negotiation | $120,000 | mis_staged | EXIT_CRITERIA_UNMET: In Negotiation without: decision_maker_identified |
| Atlas Fleet Platform (D-1011) | Tom Becker | Negotiation | $85,000 | mis_staged | EXIT_CRITERIA_UNMET: In Negotiation without: proposal_sent |
| Quarry Systems Renewal (D-1049) | Daniel Reyes | Solution | $85,000 | mis_staged | EXIT_CRITERIA_UNMET: In Solution without: budget_confirmed |
| Cedar Clinics Expansion (D-1033) | Daniel Reyes | Proposal | $48,000 | mis_staged | EXIT_CRITERIA_UNMET: In Proposal without: budget_confirmed |
| Granite Works Platform (D-1017) | Daniel Reyes | Proposal | $24,000 | mis_staged | EXIT_CRITERIA_UNMET: In Proposal without: pain_identified |
| Quarry Systems Expansion (D-1029) | Daniel Reyes | Solution | $12,000 | mis_staged | EXIT_CRITERIA_UNMET: In Solution without: budget_confirmed |
| Beacon Insurance Renewal (D-1052) | Amara Obi | Proposal | $12,000 | mis_staged | EXIT_CRITERIA_UNMET: In Proposal without: decision_maker_identified |
| Cedar Clinics Renewal (D-1053) | Daniel Reyes | Proposal | $12,000 | mis_staged | EXIT_CRITERIA_UNMET: In Proposal without: decision_maker_identified |
| Quarry Systems Platform (D-1009) | Daniel Reyes | Discovery | $85,000 | stalled | STAGE_AGE_EXCEEDED: 31 days in Discovery (limit 21) |
| Ember Energy Platform (D-1015) | Tom Becker | Discovery | $48,000 | stalled | STALE_ACTIVITY: No activity for 20 days; NEXT_STEP_OVERDUE: Next step was due 2026-11-02 |
| Lakeshore Industrial Expansion (D-1020) | Amara Obi | Solution | $48,000 | stalled | STAGE_AGE_EXCEEDED: 59 days in Solution (limit 30) |
| Falcon Security Platform (D-1016) | Amara Obi | Qualified | $36,000 | stalled | STALE_ACTIVITY: No activity for 24 days; NEXT_STEP_OVERDUE: Next step was due 2026-10-28 |
| Beacon Insurance Platform (D-1012) | Amara Obi | Negotiation | $24,000 | stalled | STALE_ACTIVITY: No activity for 23 days; NEXT_STEP_OVERDUE: Next step was due 2026-11-03 |
| Delta Grain Expansion (D-1034) | Priya Nair | Proposal | $24,000 | stalled | STAGE_AGE_EXCEEDED: 46 days in Proposal (limit 21) |
| Kestrel Health Renewal (D-1042) | Priya Nair | Negotiation | $18,000 | stalled | STALE_ACTIVITY: No activity for 24 days; NEXT_STEP_OVERDUE: Next step was due 2026-11-01 |
| Atlas Fleet Renewal (D-1051) | Tom Becker | Discovery | $18,000 | stalled | STALE_ACTIVITY: No activity for 27 days; NEXT_STEP_OVERDUE: Next step was due 2026-10-29 |
| Ivory Hotels Platform (D-1019) | Tom Becker | Negotiation | $12,000 | stalled | STAGE_AGE_EXCEEDED: 32 days in Negotiation (limit 14) |
| Bramble Foods Expansion (D-1023) | Tom Becker | Discovery | $12,000 | stalled | STAGE_AGE_EXCEEDED: 41 days in Discovery (limit 21) |
| Meridian Labs Expansion (D-1028) | Amara Obi | Negotiation | $12,000 | stalled | STAGE_AGE_EXCEEDED: 26 days in Negotiation (limit 14) |
| Lakeshore Industrial Platform (D-1000) | Amara Obi | Qualified | $120,000 | at_risk | NO_NEXT_STEP: No next step recorded |
| Cobalt Analytics Expansion (D-1025) | Daniel Reyes | Proposal | $120,000 | at_risk | NO_NEXT_STEP: No next step recorded |
| Ember Energy Expansion (D-1035) | Tom Becker | Proposal | $120,000 | at_risk | COMMIT_NOT_SUPPORTED: missing paper_process_known |
| Granite Works Expansion (D-1037) | Daniel Reyes | Qualified | $85,000 | at_risk | NO_NEXT_STEP: No next step recorded |
| Bramble Foods Renewal (D-1043) | Tom Becker | Proposal | $85,000 | at_risk | CLOSE_DATE_SLIPPING: Close date pushed 4 times |
| Helix Bio Platform (D-1018) | Priya Nair | Proposal | $60,000 | at_risk | COMMIT_NOT_SUPPORTED: missing paper_process_known |
| Juniper Retail Renewal (D-1050) | Priya Nair | Proposal | $60,000 | at_risk | COMMIT_NOT_SUPPORTED: missing paper_process_known |
| Summit Payroll Expansion (D-1027) | Tom Becker | Solution | $48,000 | at_risk | CLOSE_DATE_SLIPPING: Close date pushed 3 times |
| Ivory Hotels Expansion (D-1039) | Tom Becker | Solution | $48,000 | at_risk | CLOSE_DATE_SLIPPING: Close date pushed 4 times |
| Northwind Logistics Renewal (D-1041) | Daniel Reyes | Proposal | $48,000 | at_risk | CLOSE_DATE_SLIPPING: Close date pushed 4 times |
| Orion Freight Renewal (D-1044) | Amara Obi | Proposal | $48,000 | at_risk | COMMIT_NOT_SUPPORTED: missing paper_process_known |
| Harbor Legal Renewal (D-1046) | Priya Nair | Qualified | $48,000 | at_risk | NO_NEXT_STEP: No next step recorded |
| Ember Energy Renewal (D-1055) | Tom Becker | Discovery | $24,000 | at_risk | NO_NEXT_STEP: No next step recorded |
