#!/usr/bin/env python3
"""Scores the rules engine against the labeled sample pipeline.

Reports, per verdict, precision and recall; for the flag/no-flag decision a
pipeline review cares about most, precision, recall and false-positive rate;
and lists every miss so the known limits stay visible.

Run: python3 eval/run_eval.py [--min-flag-recall 0.9] [--write-results]
Exit code 1 if a threshold is missed, so CI can gate on it.
"""

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "plugins/revenue-os/skills/forecast-integrity/scripts"))
import revenue_engine as engine  # noqa: E402

AS_OF = date(2026, 11, 16)


def ratio(a, b):
    return round(a / b, 3) if b else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-flag-recall", type=float, default=0.9)
    ap.add_argument("--min-flag-precision", type=float, default=0.9)
    ap.add_argument("--min-verdict-accuracy", type=float, default=0.85)
    ap.add_argument("--write-results", action="store_true")
    args = ap.parse_args()

    report = engine.run(ROOT / "plugins/revenue-os/skills/forecast-integrity/references/sample_deals.csv", engine.DEFAULT_CONTEXT, AS_OF)
    predicted = {d["deal_id"]: d["verdict"] for d in report["deals"]}
    with open(ROOT / "data/labels.csv", newline="") as fh:
        labels = {r["deal_id"]: r for r in csv.DictReader(fh)}

    per = {v: {"tp": 0, "fp": 0, "fn": 0} for v in engine.VERDICTS}
    flag = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    correct = 0
    misses = []
    for deal_id, lab in labels.items():
        truth, pred = lab["label"], predicted[deal_id]
        if truth == pred:
            correct += 1
            per[truth]["tp"] += 1
        else:
            per[pred]["fp"] += 1
            per[truth]["fn"] += 1
            misses.append({"deal_id": deal_id, "label": truth, "engine": pred,
                           "judgement_call": lab["judgement_call"] == "True", "why": lab["rationale"]})
        t_flag, p_flag = truth != "healthy", pred != "healthy"
        key = "tp" if t_flag and p_flag else "fp" if p_flag else "fn" if t_flag else "tn"
        flag[key] += 1

    results = {
        "as_of": AS_OF.isoformat(),
        "deals": len(labels),
        "verdict_accuracy": ratio(correct, len(labels)),
        "flag_precision": ratio(flag["tp"], flag["tp"] + flag["fp"]),
        "flag_recall": ratio(flag["tp"], flag["tp"] + flag["fn"]),
        "false_positive_rate": ratio(flag["fp"], flag["fp"] + flag["tn"]),
        "flag_confusion": flag,
        "per_verdict": {v: {"precision": ratio(c["tp"], c["tp"] + c["fp"]), "recall": ratio(c["tp"], c["tp"] + c["fn"]), **c}
                        for v, c in per.items()},
        "misses": misses,
    }

    print(f"Deals: {results['deals']}   Verdict accuracy: {results['verdict_accuracy']}")
    print(f"Flag decision  precision {results['flag_precision']}  recall {results['flag_recall']}  false-positive rate {results['false_positive_rate']}")
    print("\nPer verdict:")
    for v, c in results["per_verdict"].items():
        print(f"  {v:<11} precision {c['precision']}  recall {c['recall']}")
    print(f"\nMisses ({len(misses)}):")
    for m in misses:
        tag = "judgement call" if m["judgement_call"] else "RULE GAP"
        print(f"  {m['deal_id']}  label={m['label']:<10} engine={m['engine']:<10} [{tag}] {m['why']}")

    if args.write_results:
        (ROOT / "eval/results.json").write_text(json.dumps(results, indent=2) + "\n")

    ok = (results["flag_recall"] >= args.min_flag_recall
          and results["flag_precision"] >= args.min_flag_precision
          and results["verdict_accuracy"] >= args.min_verdict_accuracy
          and not any(not m["judgement_call"] for m in misses))
    print("\nPASS" if ok else "\nFAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
