"""
測試 rules.py 中的四種規則檢查器。
每種規則都有 PASS / FAIL 的測試案例。
使用 conftest.py 中的 NetlistBuilder 來構造測試電路。
"""

from __future__ import annotations

import unittest

from circuit_checker.checker.rules import (
    run_checks,
    _check_net_cap_to_gnd,
    _check_pin_floating,
    _check_pin_to_pin_resistor,
    _check_pin_cap_to_gnd,
)
from tests.conftest import NetlistBuilder, make_cap, make_resistor, make_ic


# ── net_cap_to_gnd ────────────────────────────────────────────────────────────


class TestNetCapToGnd(unittest.TestCase):

    def _rule(self, net="Vcc", value="0.1uF", tolerance="10%"):
        return {
            "name": f"{net} cap to GND",
            "type": "net_cap_to_gnd",
            "net": net,
            "value": value,
            "tolerance": tolerance,
        }

    def test_pass_cap_on_net_to_gnd(self):
        """Vcc 上有 0.1uF 電容另一腳接 GND → PASS"""
        cap = make_cap(value="0.1uF")
        nl = (
            NetlistBuilder()
            .add_component("C1", cap)
            .add_net("Vcc", [("C1", "1")])
            .add_net("GND", [("C1", "2")])
            .build()
        )
        result = _check_net_cap_to_gnd(self._rule(), nl)
        self.assertTrue(result.passed)
        self.assertEqual(len(result.detail), 1)

    def test_pass_multiple_caps(self):
        """同一 net 上有多顆符合電容 → PASS"""
        cap = make_cap(value="0.1uF")
        nl = (
            NetlistBuilder()
            .add_component("C1", cap)
            .add_component("C2", cap)
            .add_net("Vcc", [("C1", "1"), ("C2", "1")])
            .add_net("GND", [("C1", "2"), ("C2", "2")])
            .build()
        )
        result = _check_net_cap_to_gnd(self._rule(), nl)
        self.assertTrue(result.passed)
        self.assertEqual(len(result.detail), 2)

    def test_fail_net_not_found(self):
        nl = NetlistBuilder().build()
        result = _check_net_cap_to_gnd(self._rule(net="Vcc"), nl)
        self.assertFalse(result.passed)
        self.assertIn("找不到", result.message)

    def test_fail_no_cap_on_net(self):
        """net 上只有 IC，沒有電容 → FAIL"""
        ic = make_ic()
        nl = (
            NetlistBuilder()
            .add_component("U1", ic)
            .add_net("Vcc", [("U1", "VDD")])
            .add_net("GND", [("U1", "GND")])
            .build()
        )
        result = _check_net_cap_to_gnd(self._rule(), nl)
        self.assertFalse(result.passed)

    def test_fail_cap_wrong_value(self):
        cap = make_cap(value="1uF")  # 要求 0.1uF ± 10%
        nl = (
            NetlistBuilder()
            .add_component("C1", cap)
            .add_net("Vcc", [("C1", "1")])
            .add_net("GND", [("C1", "2")])
            .build()
        )
        result = _check_net_cap_to_gnd(self._rule(tolerance="10%"), nl)
        self.assertFalse(result.passed)

    def test_fail_cap_not_to_gnd(self):
        cap = make_cap(value="0.1uF")
        nl = (
            NetlistBuilder()
            .add_component("C1", cap)
            .add_net("Vcc", [("C1", "1")])
            .add_net("SOME_NET", [("C1", "2")])  # 不是 GND
            .build()
        )
        result = _check_net_cap_to_gnd(self._rule(), nl)
        self.assertFalse(result.passed)

    def test_pass_agnd_variant(self):
        """AGND 也是 GND"""
        cap = make_cap(value="0.1uF")
        nl = (
            NetlistBuilder()
            .add_component("C1", cap)
            .add_net("Vcc", [("C1", "1")])
            .add_net("AGND", [("C1", "2")])
            .build()
        )
        result = _check_net_cap_to_gnd(self._rule(), nl)
        self.assertTrue(result.passed)


# ── pin_floating ──────────────────────────────────────────────────────────────


class TestPinFloating(unittest.TestCase):

    def _rule(self, pins):
        return {"name": "pins must float", "type": "pin_floating", "pins": pins}

    def test_pass_truly_floating(self):
        ic = make_ic(pin_names=["VDD", "PWM", "GND"])
        nl = (
            NetlistBuilder()
            .add_component("U1", ic)
            .add_net("Vcc", [("U1", "VDD")])
            .add_net("GND", [("U1", "GND")])
            .build()
        )
        result = _check_pin_floating(self._rule(["U1.PWM"]), nl)
        self.assertTrue(result.passed)

    def test_pass_dangling_net(self):
        """只有一個 node 的 net → 仍視為 floating"""
        ic = make_ic(pin_names=["VDD", "PWM", "GND"])
        nl = (
            NetlistBuilder()
            .add_component("U1", ic)
            .add_net("DANGLING", [("U1", "PWM")])
            .build()
        )
        result = _check_pin_floating(self._rule(["U1.PWM"]), nl)
        self.assertTrue(result.passed)

    def test_fail_pin_connected(self):
        ic = make_ic(pin_names=["VDD", "PWM", "GND"])
        nl = (
            NetlistBuilder()
            .add_component("U1", ic)
            .add_component("U2", make_ic(pin_names=["VDD", "PWM", "GND"]))
            .add_net("PWM_BUS", [("U1", "PWM"), ("U2", "PWM")])
            .build()
        )
        result = _check_pin_floating(self._rule(["U1.PWM"]), nl)
        self.assertFalse(result.passed)

    def test_mixed_pass_fail(self):
        ic = make_ic(pin_names=["VDD", "PWM", "GND"])
        nl = (
            NetlistBuilder()
            .add_component("U1", ic)
            .add_component("U2", make_ic(pin_names=["VDD", "PWM", "GND"]))
            .add_net("Vcc", [("U1", "VDD"), ("U2", "VDD")])
            .build()
        )
        result = _check_pin_floating(self._rule(["U1.PWM", "U1.VDD"]), nl)
        self.assertFalse(result.passed)  # VDD is connected

    def test_fail_bad_format(self):
        nl = NetlistBuilder().build()
        result = _check_pin_floating(self._rule(["BAD_FORMAT"]), nl)
        self.assertFalse(result.passed)
        self.assertIn("格式錯誤", result.detail[0])


# ── pin_to_pin_resistor ──────────────────────────────────────────────────────


class TestPinToPinResistor(unittest.TestCase):

    def _rule(self, pin1="U1.VDD", pin2="U1.VDRV", value="1", tolerance="20%"):
        return {
            "name": f"{pin1}-{pin2} resistor",
            "type": "pin_to_pin_resistor",
            "pin1": pin1,
            "pin2": pin2,
            "value": value,
            "tolerance": tolerance,
        }

    def test_pass_resistor_between_pins(self):
        ic = make_ic(pin_names=["VDD", "VDRV"])
        res = make_resistor(value="1")
        nl = (
            NetlistBuilder()
            .add_component("U1", ic)
            .add_component("R1", res)
            .add_net("NET_VDD", [("U1", "VDD"), ("R1", "1")])
            .add_net("NET_VDRV", [("U1", "VDRV"), ("R1", "2")])
            .build()
        )
        result = _check_pin_to_pin_resistor(self._rule(), nl)
        self.assertTrue(result.passed)

    def test_fail_no_resistor(self):
        ic = make_ic(pin_names=["VDD", "VDRV"])
        nl = (
            NetlistBuilder()
            .add_component("U1", ic)
            .add_net("NET_VDD", [("U1", "VDD")])
            .add_net("NET_VDRV", [("U1", "VDRV")])
            .build()
        )
        result = _check_pin_to_pin_resistor(self._rule(), nl)
        self.assertFalse(result.passed)

    def test_fail_wrong_value(self):
        ic = make_ic(pin_names=["VDD", "VDRV"])
        res = make_resistor(value="10k")
        nl = (
            NetlistBuilder()
            .add_component("U1", ic)
            .add_component("R1", res)
            .add_net("NET_VDD", [("U1", "VDD"), ("R1", "1")])
            .add_net("NET_VDRV", [("U1", "VDRV"), ("R1", "2")])
            .build()
        )
        result = _check_pin_to_pin_resistor(self._rule(), nl)
        self.assertFalse(result.passed)

    def test_fail_pin_not_found(self):
        nl = NetlistBuilder().build()
        result = _check_pin_to_pin_resistor(self._rule(), nl)
        self.assertFalse(result.passed)

    def test_fail_bad_pin_format(self):
        nl = NetlistBuilder().build()
        result = _check_pin_to_pin_resistor(
            self._rule(pin1="NO_DOT", pin2="ALSO_BAD"), nl
        )
        self.assertFalse(result.passed)
        self.assertIn("格式錯誤", result.message)

    def test_pass_within_tolerance(self):
        ic = make_ic(pin_names=["VDD", "VDRV"])
        res = make_resistor(value="1.1")  # 1Ω ± 20%
        nl = (
            NetlistBuilder()
            .add_component("U1", ic)
            .add_component("R1", res)
            .add_net("NET_VDD", [("U1", "VDD"), ("R1", "1")])
            .add_net("NET_VDRV", [("U1", "VDRV"), ("R1", "2")])
            .build()
        )
        result = _check_pin_to_pin_resistor(self._rule(), nl)
        self.assertTrue(result.passed)


# ── pin_cap_to_gnd ────────────────────────────────────────────────────────────


class TestPinCapToGnd(unittest.TestCase):

    def _rule(self, pins, value="0.1uF", tolerance="20%"):
        return {
            "name": "pin cap to GND",
            "type": "pin_cap_to_gnd",
            "pins": pins,
            "value": value,
            "tolerance": tolerance,
        }

    def test_pass_single_pin(self):
        ic = make_ic(pin_names=["VDD"])
        cap = make_cap(value="0.1uF")
        nl = (
            NetlistBuilder()
            .add_component("U1", ic)
            .add_component("C1", cap)
            .add_net("NET_VDD", [("U1", "VDD"), ("C1", "1")])
            .add_net("GND", [("C1", "2")])
            .build()
        )
        result = _check_pin_cap_to_gnd(self._rule(["U1.VDD"]), nl)
        self.assertTrue(result.passed)

    def test_pass_multiple_pins(self):
        ic = make_ic(pin_names=["VDD", "VDRV"])
        cap1 = make_cap("CAP1", "0.1uF")
        cap2 = make_cap("CAP2", "0.1uF")
        nl = (
            NetlistBuilder()
            .add_component("U1", ic)
            .add_component("C1", cap1)
            .add_component("C2", cap2)
            .add_net("NET_VDD", [("U1", "VDD"), ("C1", "1")])
            .add_net("NET_VDRV", [("U1", "VDRV"), ("C2", "1")])
            .add_net("GND", [("C1", "2"), ("C2", "2")])
            .build()
        )
        result = _check_pin_cap_to_gnd(self._rule(["U1.VDD", "U1.VDRV"]), nl)
        self.assertTrue(result.passed)

    def test_fail_no_net(self):
        ic = make_ic(pin_names=["VDD"])
        nl = NetlistBuilder().add_component("U1", ic).build()
        result = _check_pin_cap_to_gnd(self._rule(["U1.VDD"]), nl)
        self.assertFalse(result.passed)

    def test_fail_no_cap_on_net(self):
        ic = make_ic(pin_names=["VDD"])
        res = make_resistor()
        nl = (
            NetlistBuilder()
            .add_component("U1", ic)
            .add_component("R1", res)
            .add_net("NET_VDD", [("U1", "VDD"), ("R1", "1")])
            .add_net("GND", [("R1", "2")])
            .build()
        )
        result = _check_pin_cap_to_gnd(self._rule(["U1.VDD"]), nl)
        self.assertFalse(result.passed)

    def test_fail_partial(self):
        ic = make_ic(pin_names=["VDD", "VDRV"])
        cap = make_cap(value="0.1uF")
        nl = (
            NetlistBuilder()
            .add_component("U1", ic)
            .add_component("C1", cap)
            .add_net("NET_VDD", [("U1", "VDD"), ("C1", "1")])
            .add_net("GND", [("C1", "2")])
            .add_net("NET_VDRV", [("U1", "VDRV")])  # 沒電容
            .build()
        )
        result = _check_pin_cap_to_gnd(self._rule(["U1.VDD", "U1.VDRV"]), nl)
        self.assertFalse(result.passed)

    def test_fail_cap_wrong_value(self):
        ic = make_ic(pin_names=["VDD"])
        cap = make_cap(value="1uF")  # 要求 0.1uF
        nl = (
            NetlistBuilder()
            .add_component("U1", ic)
            .add_component("C1", cap)
            .add_net("NET_VDD", [("U1", "VDD"), ("C1", "1")])
            .add_net("GND", [("C1", "2")])
            .build()
        )
        result = _check_pin_cap_to_gnd(
            self._rule(["U1.VDD"], value="0.1uF", tolerance="10%"), nl
        )
        self.assertFalse(result.passed)


# ── run_checks ────────────────────────────────────────────────────────────────


class TestRunChecks(unittest.TestCase):

    def test_unknown_rule_type(self):
        nl = NetlistBuilder().build()
        rules = [{"name": "bad rule", "type": "nonexistent_type"}]
        results = run_checks(nl, rules)
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].passed)
        self.assertIn("未知", results[0].message)

    def test_multiple_rules(self):
        cap = make_cap(value="0.1uF")
        nl = (
            NetlistBuilder()
            .add_component("C1", cap)
            .add_net("Vcc", [("C1", "1")])
            .add_net("GND", [("C1", "2")])
            .build()
        )
        rules = [
            {"name": "r1", "type": "net_cap_to_gnd", "net": "Vcc", "value": "0.1uF"},
            {"name": "r2", "type": "net_cap_to_gnd", "net": "NONE", "value": "0.1uF"},
        ]
        results = run_checks(nl, rules)
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].passed)
        self.assertFalse(results[1].passed)

    def test_empty_rules(self):
        nl = NetlistBuilder().build()
        results = run_checks(nl, [])
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
