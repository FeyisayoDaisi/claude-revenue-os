import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins/revenue-os"
SAMPLE = PLUGIN / "skills/forecast-integrity/references/sample_deals.csv"


class WriteGateHook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        hooks = json.loads((PLUGIN / "hooks/hooks.json").read_text())
        entry = hooks["hooks"]["PreToolUse"][0]
        cls.matcher = re.compile(entry["matcher"])
        cls.command = entry["hooks"][0]["command"]

    def test_gates_crm_writes(self):
        for name in [
            "mcp__claude_ai_HubSpot__manage_crm_objects",
            "mcp__HubSpot__manage_crm_objects",
            "mcp__claude_ai_Salesforce__upsertRecord",
            "mcp__plugin_crm_salesforce__update_record",
            "mcp__Pipedrive__deleteDeal",
            "mcp__claude_ai_Attio__create-record",
        ]:
            self.assertTrue(self.matcher.search(name), name)

    def test_leaves_reads_and_other_apps_alone(self):
        for name in [
            "mcp__claude_ai_HubSpot__search_crm_objects",
            "mcp__HubSpot__get_crm_objects",
            "mcp__claude_ai_HubSpot__get_properties",
            "mcp__Salesforce__soql_query",
            "mcp__Gmail__create_draft",
            "mcp__Slack__slack_send_message",
            "Bash",
        ]:
            self.assertFalse(self.matcher.search(name), name)

    def test_command_returns_ask(self):
        out = subprocess.run(self.command, shell=True, capture_output=True, text=True, check=True).stdout
        payload = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(payload["hookEventName"], "PreToolUse")
        self.assertEqual(payload["permissionDecision"], "ask")


class PackagingRules(unittest.TestCase):
    def test_no_bin_directory(self):
        # claude.ai and Cowork refuse to install a plugin with a top-level bin/.
        self.assertFalse((PLUGIN / "bin").exists())

    def test_plugin_name_is_not_reserved(self):
        name = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text())["name"]
        self.assertNotRegex(name, r"(?i)(^claude|^anthropic|\bclaude\b|\banthropic\b)")

    def test_every_skill_has_frontmatter(self):
        for skill in (PLUGIN / "skills").iterdir():
            text = (skill / "SKILL.md").read_text()
            self.assertTrue(text.startswith("---\n"), skill.name)
            self.assertIn(f"name: {skill.name}\n", text)
            self.assertRegex(text, r"\ndescription: .{40,}")

    def test_eval_fixtures_match_sample(self):
        sample = SAMPLE.read_text()
        for f in (PLUGIN / "evals").glob("*/resources/deals.csv"):
            self.assertEqual(f.read_text(), sample, f"{f} is out of date; re-copy the sample")

    def test_no_em_dashes(self):
        for f in ROOT.rglob("*"):
            if f.is_file() and f.suffix in {".md", ".json", ".py", ".yaml", ".yml"} and ".git" not in f.parts:
                self.assertNotIn(chr(0x2014), f.read_text(encoding="utf-8"), str(f))


if __name__ == "__main__":
    unittest.main()
