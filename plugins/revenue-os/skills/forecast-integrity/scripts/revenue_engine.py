#!/usr/bin/env python3
"""Revenue OS rules engine.

Deterministic pipeline and forecast integrity checks. Claude runs this so the
counts, totals and verdicts come out the same on every run; Claude then writes
the diagnosis and the narrative on top of the engine's output.

Standard library only, so it runs in Claude's code sandbox, in Claude Code and
in CI with nothing to install.

Usage:
  python3 revenue_engine.py --deals deals.csv [--context context.json]
                            [--as-of YYYY-MM-DD] [--format md|json]
                            [--owner NAME] [--target 250000]
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timezone
from pathlib import Path

DEFAULT_CONTEXT = Path(__file__).resolve().parent.parent / "references" / "context.json"

VERDICTS = ["abandoned", "mis_staged", "stalled", "at_risk", "healthy"]
TRUE_VALUES = {"yes", "y", "true", "1", "x"}
CATEGORY_ALIASES = {
    "commit": "commit",
    "best case": "best_case",
    "best_case": "best_case",
    "bestcase": "best_case",
    "pipeline": "pipeline",
    "omitted": "omitted",
    "omit": "omitted",
    "": "pipeline",
}


# ---------------------------------------------------------------- parsing

def parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    # Epoch milliseconds, as HubSpot exports some dates.
    if value.isdigit() and len(value) >= 12:
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc).date()
    raise ValueError(f"Unrecognised date: {value!r}")


def parse_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() in TRUE_VALUES


def parse_amount(value: str | None) -> float:
    text = str(value or "").replace(",", "").replace("$", "").strip()
    return float(text) if text else 0.0


def parse_int(value: str | None) -> int:
    text = str(value or "").strip()
    return int(float(text)) if text else 0


# ---------------------------------------------------------------- model

@dataclass
class Finding:
    code: str
    detail: str


@dataclass
class DealResult:
    deal_id: str
    deal_name: str
    owner: str
    stage: str
    amount: float
    close_date: str
    forecast_category: str
    verdict: str
    findings: list[Finding] = field(default_factory=list)
    commit_supported: bool | None = None
    days_since_activity: int | None = None
    days_in_stage: int | None = None


class ContextError(Exception):
    pass


def load_context(path: Path) -> dict:
    ctx = json.loads(Path(path).read_text(encoding="utf-8"))
    if not ctx.get("stages"):
        raise ContextError("context.json has no stages")
    ctx["_stage_by_name"] = {s["name"].strip().lower(): s for s in ctx["stages"]}
    ctx["_stage_by_order"] = {s["order"]: s for s in ctx["stages"]}
    return ctx


def required_on_entry(ctx: dict, stage: dict) -> list[str]:
    """A deal sitting in stage N must already meet the exit criteria of stage N-1."""
    prior = ctx["_stage_by_order"].get(stage["order"] - 1)
    return list(prior["exit_criteria"]) if prior else []


# ---------------------------------------------------------------- rules

def evaluate_deal(row: dict, ctx: dict, as_of: date) -> DealResult:
    stage_name = (row.get("stage") or "").strip()
    stage = ctx["_stage_by_name"].get(stage_name.lower())
    category = CATEGORY_ALIASES.get((row.get("forecast_category") or "").strip().lower(), "pipeline")

    result = DealResult(
        deal_id=str(row.get("deal_id", "")).strip(),
        deal_name=str(row.get("deal_name", "")).strip(),
        owner=str(row.get("owner", "")).strip(),
        stage=stage_name,
        amount=parse_amount(row.get("amount")),
        close_date=str(row.get("close_date", "")).strip(),
        forecast_category=category,
        verdict="healthy",
    )

    if stage is None:
        result.findings.append(Finding("UNKNOWN_STAGE", f"Stage '{stage_name}' is not in the context layer"))
        result.verdict = "mis_staged"
        return result

    close = parse_date(row.get("close_date"))
    last_activity = parse_date(row.get("last_activity_date"))
    stage_entered = parse_date(row.get("stage_entered_date")) or parse_date(row.get("created_date"))
    next_step = str(row.get("next_step") or "").strip()
    next_step_date = parse_date(row.get("next_step_date"))
    pushes = parse_int(row.get("close_date_push_count"))

    days_since_activity = (as_of - last_activity).days if last_activity else None
    days_in_stage = (as_of - stage_entered).days if stage_entered else None
    result.days_since_activity = days_since_activity
    result.days_in_stage = days_in_stage

    flags: set[str] = set()

    # Activity
    if days_since_activity is None:
        result.findings.append(Finding("NO_ACTIVITY_LOGGED", "No activity date on the record"))
        flags.add("dark")
    elif days_since_activity >= ctx["abandon_activity_days"]:
        result.findings.append(Finding("ABANDONED_ACTIVITY", f"No activity for {days_since_activity} days"))
        flags.add("abandoned")
    elif days_since_activity >= ctx["stale_activity_days"]:
        result.findings.append(Finding("STALE_ACTIVITY", f"No activity for {days_since_activity} days"))
        flags.add("dark")

    # Close date
    if close is None:
        result.findings.append(Finding("MISSING_CLOSE_DATE", "No close date"))
        flags.add("risk")
    elif close < as_of:
        result.findings.append(Finding("CLOSE_DATE_PAST", f"Close date {close.isoformat()} has passed while the deal is open"))
        flags.add("close_past")
    if pushes > ctx["close_date_push_limit"]:
        result.findings.append(Finding("CLOSE_DATE_SLIPPING", f"Close date pushed {pushes} times"))
        flags.add("risk")

    # Stage age
    if days_in_stage is not None and days_in_stage > stage["max_days_in_stage"]:
        result.findings.append(Finding("STAGE_AGE_EXCEEDED", f"{days_in_stage} days in {stage['name']} (limit {stage['max_days_in_stage']})"))
        flags.add("stuck")

    # Exit criteria of the previous stage must be met to sit in this one.
    missing = [f for f in required_on_entry(ctx, stage) if f != "next_step" and not parse_bool(row.get(f))]
    if missing:
        result.findings.append(Finding("EXIT_CRITERIA_UNMET", f"In {stage['name']} without: {', '.join(missing)}"))
        flags.add("mis_staged")

    # Next step
    if not next_step:
        result.findings.append(Finding("NO_NEXT_STEP", "No next step recorded"))
        flags.add("risk")
    elif next_step_date and (as_of - next_step_date).days > ctx["next_step_grace_days"]:
        result.findings.append(Finding("NEXT_STEP_OVERDUE", f"Next step was due {next_step_date.isoformat()}"))
        flags.add("risk")

    # Forecast category support
    rules = ctx["forecast_rules"]
    if category == "commit":
        reasons = []
        if stage["order"] < rules["commit_min_stage_order"]:
            reasons.append(f"stage {stage['name']} is below the commit minimum")
        lacking = [f for f in rules["commit_required_fields"] if not parse_bool(row.get(f))]
        if lacking:
            reasons.append("missing " + ", ".join(lacking))
        result.commit_supported = not reasons
        if reasons:
            result.findings.append(Finding("COMMIT_NOT_SUPPORTED", "; ".join(reasons)))
            flags.add("risk")
    elif category == "best_case" and stage["order"] < rules["best_case_min_stage_order"]:
        result.findings.append(Finding("BEST_CASE_TOO_EARLY", f"Best case from {stage['name']}"))
        flags.add("risk")

    # Verdict precedence: abandoned > mis_staged > stalled > at_risk > healthy
    if "abandoned" in flags or ("close_past" in flags and "dark" in flags):
        result.verdict = "abandoned"
    elif "mis_staged" in flags:
        result.verdict = "mis_staged"
    elif "stuck" in flags or "dark" in flags:
        result.verdict = "stalled"
    elif flags & {"risk", "close_past"}:
        result.verdict = "at_risk"
    else:
        result.verdict = "healthy"
    return result


# ---------------------------------------------------------------- rollups

def summarise(results: list[DealResult], ctx: dict, target: float | None) -> dict:
    by_verdict = {v: {"count": 0, "amount": 0.0} for v in VERDICTS}
    by_category = {c: {"count": 0, "amount": 0.0} for c in ("commit", "best_case", "pipeline", "omitted")}
    weighted = 0.0
    supported_commit = 0.0
    owners: dict[str, dict] = {}
    for r in results:
        by_verdict[r.verdict]["count"] += 1
        by_verdict[r.verdict]["amount"] += r.amount
        by_category[r.forecast_category]["count"] += 1
        by_category[r.forecast_category]["amount"] += r.amount
        stage = ctx["_stage_by_name"].get(r.stage.lower())
        if stage and r.forecast_category != "omitted":
            weighted += r.amount * stage["probability"]
        if r.forecast_category == "commit" and r.commit_supported and r.verdict == "healthy":
            supported_commit += r.amount
        o = owners.setdefault(r.owner or "(unassigned)", {"deals": 0, "flagged": 0, "amount": 0.0, "flagged_amount": 0.0})
        o["deals"] += 1
        o["amount"] += r.amount
        if r.verdict != "healthy":
            o["flagged"] += 1
            o["flagged_amount"] += r.amount

    commit = by_category["commit"]["amount"]
    open_pipeline = sum(v["amount"] for k, v in by_category.items() if k != "omitted")
    summary = {
        "deals": len(results),
        "open_pipeline": round(open_pipeline, 2),
        "weighted_pipeline": round(weighted, 2),
        "by_verdict": {k: {"count": v["count"], "amount": round(v["amount"], 2)} for k, v in by_verdict.items()},
        "by_category": {k: {"count": v["count"], "amount": round(v["amount"], 2)} for k, v in by_category.items()},
        "commit_called": round(commit, 2),
        "commit_supported": round(supported_commit, 2),
        "commit_at_risk": round(commit - supported_commit, 2),
        "owners": {k: {**v, "amount": round(v["amount"], 2), "flagged_amount": round(v["flagged_amount"], 2)} for k, v in sorted(owners.items())},
    }
    if target:
        summary["target"] = target
        summary["coverage_ratio"] = round(open_pipeline / target, 2) if target else None
        summary["gap_to_target_supported_commit"] = round(target - supported_commit, 2)
    return summary


def run(deals_path: Path, context_path: Path, as_of: date, owner: str | None = None, target: float | None = None) -> dict:
    ctx = load_context(context_path)
    with open(deals_path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if owner:
        rows = [r for r in rows if (r.get("owner") or "").strip().lower() == owner.strip().lower()]
    results = [evaluate_deal(r, ctx, as_of) for r in rows]
    return {
        "as_of": as_of.isoformat(),
        "context_version": ctx.get("version"),
        "summary": summarise(results, ctx, target),
        "deals": [
            {**asdict(r), "findings": [asdict(f) for f in r.findings]} for r in results
        ],
    }


# ---------------------------------------------------------------- output

def money(x: float, cur: str = "USD") -> str:
    return f"${x:,.0f}" if cur == "USD" else f"{x:,.0f} {cur}"


def to_markdown(report: dict) -> str:
    s = report["summary"]
    lines = [
        f"# Forecast integrity report (as of {report['as_of']})",
        "",
        f"Context layer version {report['context_version']}. {s['deals']} open deals, {money(s['open_pipeline'])} open pipeline, {money(s['weighted_pipeline'])} weighted.",
        "",
        "## Commit",
        "",
        f"- Called: {money(s['commit_called'])}",
        f"- Supported by exit criteria and healthy: {money(s['commit_supported'])}",
        f"- At risk: {money(s['commit_at_risk'])}",
    ]
    if "target" in s:
        lines += [f"- Target: {money(s['target'])}, coverage {s['coverage_ratio']}x, gap after supported commit {money(s['gap_to_target_supported_commit'])}"]
    lines += ["", "## Deals by verdict", "", "| Verdict | Deals | Amount |", "|---|---:|---:|"]
    for v in VERDICTS:
        lines.append(f"| {v} | {s['by_verdict'][v]['count']} | {money(s['by_verdict'][v]['amount'])} |")
    lines += ["", "## By owner", "", "| Owner | Deals | Flagged | Flagged amount |", "|---|---:|---:|---:|"]
    for name, o in s["owners"].items():
        lines.append(f"| {name} | {o['deals']} | {o['flagged']} | {money(o['flagged_amount'])} |")
    flagged = [d for d in report["deals"] if d["verdict"] != "healthy"]
    flagged.sort(key=lambda d: (VERDICTS.index(d["verdict"]), -d["amount"]))
    lines += ["", "## Flagged deals", "", "| Deal | Owner | Stage | Amount | Verdict | Findings |", "|---|---|---|---:|---|---|"]
    for d in flagged:
        found = "; ".join(f"{f['code']}: {f['detail']}" for f in d["findings"])
        lines.append(f"| {d['deal_name']} ({d['deal_id']}) | {d['owner']} | {d['stage']} | {money(d['amount'])} | {d['verdict']} | {found} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--deals", required=True, type=Path)
    p.add_argument("--context", type=Path, default=DEFAULT_CONTEXT)
    p.add_argument("--as-of", type=parse_date, default=date.today())
    p.add_argument("--format", choices=["md", "json"], default="md")
    p.add_argument("--owner")
    p.add_argument("--target", type=float)
    p.add_argument("--out", type=Path)
    args = p.parse_args(argv)

    report = run(args.deals, args.context, args.as_of, args.owner, args.target)
    text = json.dumps(report, indent=2) if args.format == "json" else to_markdown(report)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
