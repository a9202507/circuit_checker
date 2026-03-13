"""
端到端整合測試。
1. 使用手寫的 fixture netlist + YAML rules
2. 執行完整 pipeline：parse → check → report
3. 驗證最終結果和 CLI exit code
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from circuit_checker.parser.allegro import load_netlist
from circuit_checker.checker.rules import load_rules, run_checks
from circuit_checker.reporter.html import generate_html
from tests.conftest import FIXTURES_DIR


class TestPipelineIntegration(unittest.TestCase):
    """Parser → Checker → Reporter 完整流程"""

    def _write_rules(self, tmpdir: str, rules: list[dict]) -> Path:
        rules_file = Path(tmpdir) / "rules.yaml"
        rules_file.write_text(
            yaml.dump({"rules": rules}, allow_unicode=True),
            encoding="utf-8",
        )
        return rules_file

    def test_full_pipeline_passing(self):
        """Vcc 上 C1 接 GND → 規則 PASS"""
        netlist = load_netlist(FIXTURES_DIR)
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_file = self._write_rules(tmpdir, [
                {
                    "name": "Vcc cap to GND",
                    "type": "net_cap_to_gnd",
                    "net": "Vcc",
                    "value": "0.1uF",
                    "tolerance": "20%",
                }
            ])
            rules = load_rules(rules_file)
            results = run_checks(netlist, rules)

            self.assertEqual(len(results), 1)
            self.assertTrue(results[0].passed)

            output = Path(tmpdir) / "report.html"
            generate_html(results, str(FIXTURES_DIR), str(rules_file), output)
            self.assertTrue(output.exists())
            self.assertIn("PASS", output.read_text(encoding="utf-8"))

    def test_full_pipeline_failing(self):
        """找不到的 net → FAIL"""
        netlist = load_netlist(FIXTURES_DIR)
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_file = self._write_rules(tmpdir, [
                {
                    "name": "Missing net",
                    "type": "net_cap_to_gnd",
                    "net": "NONEXISTENT",
                    "value": "0.1uF",
                }
            ])
            rules = load_rules(rules_file)
            results = run_checks(netlist, rules)
            self.assertFalse(results[0].passed)

    def test_multiple_rules_mixed(self):
        netlist = load_netlist(FIXTURES_DIR)
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_file = self._write_rules(tmpdir, [
                {
                    "name": "Vcc cap to GND",
                    "type": "net_cap_to_gnd",
                    "net": "Vcc",
                    "value": "0.1uF",
                    "tolerance": "20%",
                },
                {
                    "name": "Missing net",
                    "type": "net_cap_to_gnd",
                    "net": "NONEXISTENT",
                    "value": "0.1uF",
                },
            ])
            rules = load_rules(rules_file)
            results = run_checks(netlist, rules)
            self.assertEqual(len(results), 2)
            self.assertTrue(results[0].passed)
            self.assertFalse(results[1].passed)

    def test_pin_to_pin_resistor_with_fixture(self):
        """
        Fixture: R1 連接 Vcc (pin1) ↔ NET_VDRV (pin2)
        U1.VDD(邏輯腳) → Vcc, U1.VDRV(邏輯腳) → NET_VDRV
        """
        netlist = load_netlist(FIXTURES_DIR)
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_file = self._write_rules(tmpdir, [
                {
                    "name": "VDD-VDRV resistor",
                    "type": "pin_to_pin_resistor",
                    "pin1": "U1.VDD",
                    "pin2": "U1.VDRV",
                    "value": "1",
                    "tolerance": "20%",
                }
            ])
            rules = load_rules(rules_file)
            results = run_checks(netlist, rules)
            self.assertEqual(len(results), 1)
            self.assertTrue(results[0].passed)

    def test_pwm_floating_with_fixture(self):
        """Fixture 中 U1.PWM 沒接任何 net → PASS"""
        netlist = load_netlist(FIXTURES_DIR)
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_file = self._write_rules(tmpdir, [
                {
                    "name": "PWM floating",
                    "type": "pin_floating",
                    "pins": ["U1.PWM"],
                }
            ])
            rules = load_rules(rules_file)
            results = run_checks(netlist, rules)
            self.assertEqual(len(results), 1)
            self.assertTrue(results[0].passed)


class TestCLI(unittest.TestCase):
    """測試 CLI exit code"""

    def test_cli_exit_0_on_all_pass(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_file = Path(tmpdir) / "rules.yaml"
            rules_file.write_text(yaml.dump({
                "rules": [{
                    "name": "Vcc cap",
                    "type": "net_cap_to_gnd",
                    "net": "Vcc",
                    "value": "0.1uF",
                    "tolerance": "20%",
                }]
            }, allow_unicode=True))

            output = Path(tmpdir) / "report.html"
            result = subprocess.run(
                [
                    sys.executable, "-m", "circuit_checker.main",
                    "--netlist", str(FIXTURES_DIR),
                    "--rules", str(rules_file),
                    "--output", str(output),
                ],
                capture_output=True, text=True,
                env={"PYTHONPATH": str(FIXTURES_DIR.parent.parent / "src")},
            )
            self.assertEqual(result.returncode, 0)
            self.assertTrue(output.exists())

    def test_cli_exit_1_on_fail(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_file = Path(tmpdir) / "rules.yaml"
            rules_file.write_text(yaml.dump({
                "rules": [{
                    "name": "Missing",
                    "type": "net_cap_to_gnd",
                    "net": "NONEXISTENT",
                    "value": "0.1uF",
                }]
            }, allow_unicode=True))

            result = subprocess.run(
                [
                    sys.executable, "-m", "circuit_checker.main",
                    "--netlist", str(FIXTURES_DIR),
                    "--rules", str(rules_file),
                    "--output", str(Path(tmpdir) / "report.html"),
                ],
                capture_output=True, text=True,
                env={"PYTHONPATH": str(FIXTURES_DIR.parent.parent / "src")},
            )
            self.assertEqual(result.returncode, 1)

    def test_cli_verbose(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_file = Path(tmpdir) / "rules.yaml"
            rules_file.write_text(yaml.dump({
                "rules": [{
                    "name": "Vcc cap",
                    "type": "net_cap_to_gnd",
                    "net": "Vcc",
                    "value": "0.1uF",
                    "tolerance": "20%",
                }]
            }, allow_unicode=True))

            result = subprocess.run(
                [
                    sys.executable, "-m", "circuit_checker.main",
                    "--netlist", str(FIXTURES_DIR),
                    "--rules", str(rules_file),
                    "--output", str(Path(tmpdir) / "report.html"),
                    "--verbose",
                ],
                capture_output=True, text=True,
                env={"PYTHONPATH": str(FIXTURES_DIR.parent.parent / "src")},
            )
            self.assertIn("PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
