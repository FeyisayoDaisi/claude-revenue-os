#!/usr/bin/env python3
"""Builds the labeled sample pipeline used by the eval harness.

Each deal is written from a scenario a RevOps lead would recognise, and its
label is the call that lead would make in a pipeline review. Most labels follow
from the fields. A handful are judgement calls the fields alone can't settle
(an automated-only activity trail, a champion who left, a long legal review).
Those exist on purpose, so the eval reports where rules stop and a human or
Claude's reading of notes has to take over.

Run: python3 data/generate_sample.py  (writes the plugin's references/sample_deals.csv and data/labels.csv)
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

AS_OF = date(2026, 11, 16)
OWNERS = ["Amara Obi", "Daniel Reyes", "Priya Nair", "Tom Becker"]
COMPANIES = [
    "Lakeshore Industrial", "Northwind Logistics", "Kestrel Health", "Bramble Foods", "Orion Freight",
    "Cobalt Analytics", "Harbor Legal", "Summit Payroll", "Meridian Labs", "Quarry Systems",
    "Juniper Retail", "Atlas Fleet", "Beacon Insurance", "Cedar Clinics", "Delta Grain",
    "Ember Energy", "Falcon Security", "Granite Works", "Helix Bio", "Ivory Hotels",
]
STAGES = ["Discovery", "Qualified", "Solution", "Proposal", "Negotiation"]
FIELDS = ["pain_identified", "budget_confirmed", "decision_maker_identified", "proposal_sent", "paper_process_known"]
ENTRY_REQ = {  # exit criteria of the prior stage, excluding next_step
    "Discovery": [],
    "Qualified": [],
    "Solution": ["pain_identified", "budget_confirmed"],
    "Proposal": ["pain_identified", "budget_confirmed", "decision_maker_identified"],
    "Negotiation": ["pain_identified", "budget_confirmed", "decision_maker_identified", "proposal_sent"],
}
MAX_DAYS = {"Discovery": 21, "Qualified": 21, "Solution": 30, "Proposal": 21, "Negotiation": 14}

rng = random.Random(20261116)


def d(days_ago: int) -> str:
    return (AS_OF - timedelta(days=days_ago)).isoformat()


def f(days_ahead: int) -> str:
    return (AS_OF + timedelta(days=days_ahead)).isoformat()


def base(i: int, stage: str) -> dict:
    row = {
        "deal_id": f"D-{1000 + i}",
        "deal_name": f"{COMPANIES[i % len(COMPANIES)]} {['Platform', 'Expansion', 'Renewal', 'Pilot'][(i // len(COMPANIES)) % 4]}",
        "owner": OWNERS[i % len(OWNERS)],
        "stage": stage,
        "amount": rng.choice([12000, 18000, 24000, 36000, 48000, 60000, 85000, 120000]),
        "created_date": d(rng.randint(40, 120)),
        "stage_entered_date": d(rng.randint(2, MAX_DAYS[stage] - 2)),
        "close_date": f(rng.randint(10, 75)),
        "last_activity_date": d(rng.randint(0, 6)),
        "last_activity_type": rng.choice(["call", "meeting", "email reply"]),
        "forecast_category": "pipeline",
        "next_step": rng.choice(["Demo with ops team", "Send security pack", "Pricing review", "Exec alignment call", "Technical validation"]),
        "next_step_date": f(rng.randint(1, 10)),
        "close_date_push_count": rng.choice([0, 0, 1]),
        "notes": "",
    }
    for fld in FIELDS:
        row[fld] = "no"
    for fld in ENTRY_REQ[stage]:
        row[fld] = "yes"
    if stage in ("Proposal", "Negotiation"):
        row["forecast_category"] = "best_case"
    return row


def healthy(i):
    stage = rng.choice(STAGES)
    r = base(i, stage)
    if stage == "Negotiation":
        r.update(forecast_category="commit", paper_process_known="yes", proposal_sent="yes")
    return r, "healthy", "Meets entry criteria, active, dated next step"


def mis_staged(i):
    stage = rng.choice(["Solution", "Proposal", "Negotiation"])
    r = base(i, stage)
    gap = rng.choice(ENTRY_REQ[stage])
    r[gap] = "no"
    return r, "mis_staged", f"Sits in {stage} without {gap}"


def stalled_age(i):
    stage = rng.choice(STAGES)
    r = base(i, stage)
    r["stage_entered_date"] = d(MAX_DAYS[stage] + rng.randint(8, 30))
    return r, "stalled", f"Stuck in {stage} past the stage age limit"


def stalled_dark(i):
    r = base(i, rng.choice(STAGES))
    r["last_activity_date"] = d(rng.randint(16, 40))
    r["next_step_date"] = d(rng.randint(10, 20))
    return r, "stalled", "Gone dark: no activity in over two weeks"


def abandoned(i):
    r = base(i, rng.choice(STAGES[:4]))
    r["last_activity_date"] = d(rng.randint(50, 90))
    r["close_date"] = d(rng.randint(5, 40))
    r["next_step_date"] = d(rng.randint(30, 60))
    return r, "abandoned", "No activity in 50+ days and the close date has passed"


def at_risk_commit(i):
    r = base(i, "Proposal")
    r.update(forecast_category="commit", paper_process_known="no")
    return r, "at_risk", "Called commit without the paper process known"


def at_risk_slip(i):
    r = base(i, rng.choice(["Solution", "Proposal"]))
    r["close_date_push_count"] = rng.choice([3, 4])
    return r, "at_risk", "Close date pushed three or more times"


def at_risk_no_step(i):
    r = base(i, rng.choice(["Qualified", "Solution", "Proposal"]))
    r["next_step"] = ""
    r["next_step_date"] = ""
    return r, "at_risk", "No next step on an active deal"


# Judgement calls the rules can't see from the fields alone.
def judgement_automated_only(i):
    r = base(i, "Solution")
    r["last_activity_type"] = "automated sequence email"
    r["notes"] = "Last human reply 5 weeks ago; only sequence emails since"
    return r, "stalled", "Activity is automated only, buyer silent for five weeks"


def judgement_champion_left(i):
    r = base(i, "Negotiation")
    r.update(forecast_category="commit", paper_process_known="yes", proposal_sent="yes")
    r["notes"] = "Champion left the company last week, new contact not engaged"
    return r, "at_risk", "Champion left; commit is not real until a new sponsor engages"


def judgement_legal_review(i):
    r = base(i, "Negotiation")
    r.update(forecast_category="commit", paper_process_known="yes", proposal_sent="yes")
    r["stage_entered_date"] = d(26)
    r["notes"] = "Customer legal review, standard 30 day cycle, redlines returned on schedule"
    return r, "healthy", "Long stage age is the buyer's known legal cycle, on schedule"


def judgement_brand_new(i):
    r = base(i, "Discovery")
    r["created_date"] = d(1)
    r["stage_entered_date"] = d(1)
    r["next_step"] = ""
    r["next_step_date"] = ""
    r["notes"] = "Inbound yesterday, first call being booked"
    return r, "healthy", "Created yesterday; no next step yet is expected"


PLAN = (
    [healthy] * 18
    + [mis_staged] * 8
    + [stalled_age] * 5
    + [stalled_dark] * 5
    + [abandoned] * 5
    + [at_risk_commit] * 4
    + [at_risk_slip] * 4
    + [at_risk_no_step] * 4
    + [judgement_automated_only, judgement_champion_left, judgement_legal_review, judgement_brand_new]
)


def main():
    out = Path(__file__).resolve().parent
    sample = out.parent / "plugins/revenue-os/skills/forecast-integrity/references/sample_deals.csv"
    rows, labels = [], []
    order = list(range(len(PLAN)))
    rng.shuffle(order)
    for i, idx in enumerate(order):
        row, label, why = PLAN[idx](i)
        rows.append(row)
        labels.append({"deal_id": row["deal_id"], "label": label, "judgement_call": PLAN[idx].__name__.startswith("judgement"), "rationale": why})
    cols = list(rows[0].keys())
    with open(sample, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    with open(out / "labels.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["deal_id", "label", "judgement_call", "rationale"])
        w.writeheader()
        w.writerows(labels)
    print(f"Wrote {len(rows)} deals as of {AS_OF}")


if __name__ == "__main__":
    main()
