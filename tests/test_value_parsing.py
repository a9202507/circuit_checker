"""
測試 rules.py 中的數值解析與容差比對函式。
這些是最容易出 edge case 的地方，需要完整覆蓋。
"""

from __future__ import annotations

import unittest
import math

from circuit_checker.checker.rules import _parse_value, _values_match, _is_gnd


class TestParseValue(unittest.TestCase):
    """測試 SI 單位解析"""

    def _approx(self, a: float | None, b: float, rel: float = 1e-6):
        self.assertIsNotNone(a)
        self.assertAlmostEqual(a / b, 1.0, delta=rel)

    def test_capacitor_uf(self):
        self._approx(_parse_value("0.1uF"), 1e-7)
        self._approx(_parse_value("1uF"), 1e-6)
        self._approx(_parse_value("22uF"), 2.2e-5)
        self._approx(_parse_value("4.7uF"), 4.7e-6)
        self._approx(_parse_value("330uF"), 3.3e-4)

    def test_capacitor_nf(self):
        self._approx(_parse_value("100nF"), 1e-7)
        self._approx(_parse_value("10nF"), 1e-8)

    def test_capacitor_pf(self):
        self._approx(_parse_value("100000pF"), 1e-7)
        self._approx(_parse_value("220 pF"), 2.2e-10)

    def test_resistor_plain(self):
        self._approx(_parse_value("1"), 1.0)
        self._approx(_parse_value("47"), 47.0)
        self._approx(_parse_value("0.01"), 0.01)

    def test_resistor_k(self):
        self._approx(_parse_value("1k"), 1e3)
        self._approx(_parse_value("4.7k"), 4.7e3)
        self._approx(_parse_value("10k"), 1e4)
        self._approx(_parse_value("100k"), 1e5)

    def test_resistor_K_uppercase(self):
        self._approx(_parse_value("1K"), 1e3)

    def test_resistor_M(self):
        self._approx(_parse_value("1M"), 1e6)
        self._approx(_parse_value("4.7M"), 4.7e6)

    def test_resistor_with_unit_R(self):
        self._approx(_parse_value("1R"), 1.0)
        self._approx(_parse_value("10R"), 10.0)

    def test_resistor_with_ohm_symbol(self):
        self._approx(_parse_value("100Ω"), 100.0)

    def test_resistor_with_ohm_text(self):
        result = _parse_value("100ohm")
        self.assertIsNotNone(result)
        self._approx(result, 100.0)

    def test_milli_farad(self):
        self._approx(_parse_value("1mF"), 1e-3)

    def test_invalid_empty(self):
        self.assertIsNone(_parse_value(""))

    def test_invalid_letters(self):
        self.assertIsNone(_parse_value("abc"))

    def test_invalid_symbols(self):
        self.assertIsNone(_parse_value("---"))

    def test_spaces_trimmed(self):
        result = _parse_value("  0.1uF  ")
        self.assertIsNotNone(result)
        self._approx(result, 1e-7)


class TestValuesMatch(unittest.TestCase):
    """測試容差比對"""

    def test_exact_match(self):
        self.assertTrue(_values_match("0.1uF", "0.1uF"))

    def test_equivalent_units(self):
        self.assertTrue(_values_match("0.1uF", "100nF"))

    def test_within_tolerance_10pct(self):
        self.assertTrue(_values_match("0.1uF", "0.105uF", "10%"))
        self.assertTrue(_values_match("0.1uF", "0.095uF", "10%"))

    def test_outside_tolerance(self):
        self.assertFalse(_values_match("0.1uF", "0.2uF", "10%"))
        self.assertFalse(_values_match("1k", "2k", "20%"))

    def test_default_tolerance_20pct(self):
        # 1k ± 20% → 800 ~ 1200
        self.assertTrue(_values_match("1k", "1.19k"))
        self.assertTrue(_values_match("1k", "0.81k"))
        self.assertFalse(_values_match("1k", "1.3k"))

    def test_string_fallback_case_insensitive(self):
        self.assertTrue(_values_match("abc", "ABC"))
        self.assertFalse(_values_match("abc", "def"))

    def test_resistor_values(self):
        self.assertTrue(_values_match("1", "1"))
        self.assertTrue(_values_match("1", "1.1", "20%"))
        self.assertTrue(_values_match("10k", "10k"))

    def test_zero_target(self):
        self.assertTrue(_values_match("0", "0"))


class TestIsGnd(unittest.TestCase):
    """測試 GND 判斷"""

    def test_plain_gnd(self):
        self.assertTrue(_is_gnd("GND"))

    def test_analog_gnd(self):
        self.assertTrue(_is_gnd("AGND"))

    def test_power_gnd(self):
        self.assertTrue(_is_gnd("PGND"))

    def test_numbered_gnd(self):
        self.assertTrue(_is_gnd("GND2"))
        self.assertTrue(_is_gnd("GND0"))
        self.assertTrue(_is_gnd("AGND1"))

    def test_case_insensitive(self):
        self.assertTrue(_is_gnd("gnd"))
        self.assertTrue(_is_gnd("Gnd"))
        self.assertTrue(_is_gnd("agnd"))

    def test_not_gnd(self):
        self.assertFalse(_is_gnd("Vcc"))
        self.assertFalse(_is_gnd("VDD"))
        self.assertFalse(_is_gnd("NET_GND_SIGNAL"))
        self.assertFalse(_is_gnd("GROUND"))
        self.assertFalse(_is_gnd("12VIN"))


if __name__ == "__main__":
    unittest.main()
