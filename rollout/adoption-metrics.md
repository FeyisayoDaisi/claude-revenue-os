# Adoption and impact metrics

Measure the rollout like any other revenue system: is it used, is it right, and does it change the number.

## Usage

| Metric | How to get it | Healthy by week 6 |
|---|---|---|
| Weekly reviews run per manager | Count of `forecast-integrity` runs (org usage analytics, or a tally from the brief channel) | 1 or more per manager per week |
| Scheduled brief delivery rate | Briefs posted on time / briefs scheduled | 95% or higher |
| Reps who acted on a nudge | Nudged deals changed by their owner within 7 days / deals nudged | 60% or higher |

## Accuracy

| Metric | How to get it | Bar |
|---|---|---|
| Flag precision and recall | `python3 eval/run_eval.py` on the labeled set, grown with real cases | 0.90 or higher each |
| Override rate | Second-pass overrides / flagged deals | Under 15%. Higher means a rule needs changing |
| Unapproved writes | CRM audit log entries from the connector with no matching change log | 0 |

## Impact on the forecast

| Metric | How to get it | Direction |
|---|---|---|
| Commit accuracy | Closed-won in period / commit called at the start of the period | Up, toward 90% or higher |
| Supported share of commit | `commit_supported / commit_called` from the engine | Up |
| Mis-staged deals | Engine count, weekly | Down |
| Average days in stage beyond the limit | Engine output, weekly | Down |
| Time spent on pipeline review prep | Ask managers before and after | Down |

Take a baseline in Phase 0 before anyone changes behavior, or there's nothing to compare against.
