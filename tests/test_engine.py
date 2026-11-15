import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "plugins/revenue-os/skills/forecast-integrity/scripts"))
import revenue_engine as engine  # noqa: E402

AS_OF = date(2026, 11, 16)
CTX = engine.load_context(engine.DEFAULT_CONTEXT)


def deal(**over):
    row = {
        "deal_id": "T-1", "deal_name": "Test", "owner": "A", "stage": "Proposal", "amount": "50000",
        "created_date": "2026-09-01", "stage_entered_date": "2026-11-10", "close_date": "2026-12-20",
        "last_activity_date": "2026-11-14", "forecast_category": "best case", "next_step": "Pricing call",
        "next_step_date": "2026-11-20", "close_date_push_count": "0", "pain_identified": "yes",
        "budget_confirmed": "yes", "decision_maker_identified": "yes", "proposal_sent": "no",
        "paper_process_known": "no",
    }
    row.update(over)
    return engine.evaluate_deal(row, CTX, AS_OF)


def codes(result):
    return {f.code for f in result.findings}


class EngineRules(unittest.TestCase):
    def test_healthy(self):
        self.assertEqual(deal().verdict, "healthy")

    def test_missing_entry_criteria_is_mis_staged(self):
        r = deal(decision_maker_identified="no")
        self.assertEqual(r.verdict, "mis_staged")
        self.assertIn("EXIT_CRITERIA_UNMET", codes(r))

    def test_stage_age(self):
        r = deal(stage_entered_date="2026-10-01")
        self.assertEqual(r.verdict, "stalled")
        self.assertIn("STAGE_AGE_EXCEEDED", codes(r))

    def test_dark(self):
        self.assertEqual(deal(last_activity_date="2026-10-25").verdict, "stalled")

    def test_abandoned_long_silence(self):
        self.assertEqual(deal(last_activity_date="2026-09-01").verdict, "abandoned")

    def test_abandoned_past_close_and_dark(self):
        self.assertEqual(deal(last_activity_date="2026-10-25", close_date="2026-11-01").verdict, "abandoned")

    def test_past_close_but_active_is_at_risk(self):
        r = deal(close_date="2026-11-10")
        self.assertEqual(r.verdict, "at_risk")
        self.assertIn("CLOSE_DATE_PAST", codes(r))

    def test_commit_without_paper_process(self):
        r = deal(forecast_category="Commit")
        self.assertEqual(r.verdict, "at_risk")
        self.assertFalse(r.commit_supported)

    def test_commit_too_early(self):
        r = deal(stage="Qualified", forecast_category="commit", paper_process_known="yes")
        self.assertIn("COMMIT_NOT_SUPPORTED", codes(r))

    def test_slip(self):
        self.assertIn("CLOSE_DATE_SLIPPING", codes(deal(close_date_push_count="3")))

    def test_next_step(self):
        self.assertIn("NO_NEXT_STEP", codes(deal(next_step="", next_step_date="")))
        self.assertIn("NEXT_STEP_OVERDUE", codes(deal(next_step_date="2026-11-01")))

    def test_unknown_stage(self):
        self.assertEqual(deal(stage="Closed Won??").verdict, "mis_staged")

    def test_date_formats(self):
        self.assertEqual(engine.parse_date("2026-11-16T09:00:00Z"), AS_OF)
        self.assertEqual(engine.parse_date("11/16/2026"), AS_OF)

    def test_deterministic(self):
        a = engine.run(ROOT / "plugins/revenue-os/skills/forecast-integrity/references/sample_deals.csv", engine.DEFAULT_CONTEXT, AS_OF)
        b = engine.run(ROOT / "plugins/revenue-os/skills/forecast-integrity/references/sample_deals.csv", engine.DEFAULT_CONTEXT, AS_OF)
        self.assertEqual(a, b)

    def test_supported_commit_never_exceeds_called(self):
        s = engine.run(ROOT / "plugins/revenue-os/skills/forecast-integrity/references/sample_deals.csv", engine.DEFAULT_CONTEXT, AS_OF)["summary"]
        self.assertLessEqual(s["commit_supported"], s["commit_called"])
        self.assertAlmostEqual(s["commit_at_risk"], s["commit_called"] - s["commit_supported"], places=2)


if __name__ == "__main__":
    unittest.main()
