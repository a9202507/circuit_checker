"""
測試 reporter/html.py 的 HTML 報告生成。
"""

from __future__ import annotations

import unittest
import tempfile
from pathlib import Path

from circuit_checker.checker.rules import CheckResult
from circuit_checker.reporter.html import generate_html


class TestGenerateHtml(unittest.TestCase):

    def _sample_results(self):
        return [
            CheckResult(
                rule_name="Vcc cap to GND",
                rule_type="net_cap_to_gnd",
                passed=True,
                message="共找到 1 個符合的電容",
                detail=["C1 (0.1uF) — Vcc ↔ GND"],
            ),
            CheckResult(
                rule_name="PWM floating",
                rule_type="pin_floating",
                passed=False,
                message="1 個 pin 不符合",
                detail=["U1.PWM ✗ 接到 net 'PWM_BUS'（2 個節點）"],
            ),
        ]

    def test_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "report.html"
            generate_html(self._sample_results(), "/test", "/test/rules.yaml", output)
            self.assertTrue(output.exists())

    def test_contains_pass_fail(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "report.html"
            generate_html(self._sample_results(), "/test", "/test/rules.yaml", output)
            html = output.read_text(encoding="utf-8")
            self.assertIn("PASS", html)
            self.assertIn("FAIL", html)

    def test_contains_rule_names(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "report.html"
            generate_html(self._sample_results(), "/test", "/test/rules.yaml", output)
            html = output.read_text(encoding="utf-8")
            self.assertIn("Vcc cap to GND", html)
            self.assertIn("PWM floating", html)

    def test_contains_rule_types(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "report.html"
            generate_html(self._sample_results(), "/test", "/test/rules.yaml", output)
            html = output.read_text(encoding="utf-8")
            self.assertIn("net_cap_to_gnd", html)
            self.assertIn("pin_floating", html)

    def test_contains_detail(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "report.html"
            generate_html(self._sample_results(), "/test", "/test/rules.yaml", output)
            html = output.read_text(encoding="utf-8")
            self.assertIn("C1 (0.1uF)", html)

    def test_empty_results(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "report.html"
            generate_html([], "/test", "/test/rules.yaml", output)
            self.assertTrue(output.exists())
            html = output.read_text(encoding="utf-8")
            self.assertIn("Circuit Checker Report", html)

    def test_valid_html_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "report.html"
            generate_html(self._sample_results(), "/test", "/test/rules.yaml", output)
            html = output.read_text(encoding="utf-8")
            self.assertTrue(html.startswith("<!DOCTYPE html>"))
            self.assertIn("</html>", html)
            self.assertIn("<body>", html)
            self.assertIn("</body>", html)


if __name__ == "__main__":
    unittest.main()
