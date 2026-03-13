"""
測試 parser/allegro.py 的解析邏輯。
使用 tests/fixtures/ 下的手寫 .dat 檔案，
驗證 Parser 能正確將 PST 格式轉成 Python 資料模型。
"""

from __future__ import annotations

import unittest
import tempfile
from pathlib import Path

from circuit_checker.parser.allegro import (
    load_netlist,
    parse_pstchip,
    parse_pstxprt,
    parse_pstxnet,
    Netlist,
)
from tests.conftest import FIXTURES_DIR


class TestParsePstchip(unittest.TestCase):

    def setUp(self):
        self.prims = parse_pstchip(FIXTURES_DIR / "pstchip.dat")

    def test_loads_all_primitives(self):
        self.assertEqual(len(self.prims), 3)
        self.assertIn("CAP_0603_0.1UF", self.prims)
        self.assertIn("RES_0603_1R", self.prims)
        self.assertIn("IC_TDM22545T", self.prims)

    def test_capacitor_attributes(self):
        cap = self.prims["CAP_0603_0.1UF"]
        self.assertEqual(cap.part_name, "0.1uF-0603")
        self.assertEqual(cap.jedec_type, "IR_C0603")
        self.assertEqual(cap.value, "0.1uF")
        self.assertEqual(cap.part_class, "DISCRETE")
        self.assertEqual(cap.component_type, "capacitor")

    def test_resistor_attributes(self):
        res = self.prims["RES_0603_1R"]
        self.assertEqual(res.value, "1")
        self.assertEqual(res.jedec_type, "IR_R0603")
        self.assertEqual(res.component_type, "resistor")

    def test_ic_attributes(self):
        ic = self.prims["IC_TDM22545T"]
        self.assertEqual(ic.jedec_type, "QFN32")
        self.assertEqual(ic.part_class, "IC")
        self.assertEqual(ic.component_type, "other")

    def test_two_pin_component(self):
        cap = self.prims["CAP_0603_0.1UF"]
        self.assertEqual(len(cap.pins), 2)
        self.assertIn("1", cap.pins)
        self.assertIn("2", cap.pins)

    def test_ic_pin_definitions(self):
        ic = self.prims["IC_TDM22545T"]
        self.assertEqual(len(ic.pins), 4)
        self.assertIn("VDD", ic.pins)
        self.assertIn("VDRV", ic.pins)
        self.assertIn("PWM", ic.pins)
        self.assertIn("GND", ic.pins)
        self.assertEqual(ic.pins["VDD"].use, "PWR")
        self.assertEqual(ic.pins["GND"].use, "GND")
        self.assertEqual(ic.pins["PWM"].use, "IN")

    def test_pin_numbers(self):
        ic = self.prims["IC_TDM22545T"]
        self.assertEqual(ic.pins["VDD"].number, "A1")
        self.assertEqual(ic.pins["GND"].number, "C1")


class TestParsePstxprt(unittest.TestCase):

    def setUp(self):
        self.prims = parse_pstchip(FIXTURES_DIR / "pstchip.dat")
        self.comps = parse_pstxprt(FIXTURES_DIR / "pstxprt.dat", self.prims)

    def test_loads_all_components(self):
        self.assertEqual(len(self.comps), 3)
        self.assertIn("C1", self.comps)
        self.assertIn("R1", self.comps)
        self.assertIn("U1", self.comps)

    def test_component_primitive_linkage(self):
        self.assertEqual(self.comps["C1"].primitive.name, "CAP_0603_0.1UF")
        self.assertEqual(self.comps["R1"].primitive.name, "RES_0603_1R")
        self.assertEqual(self.comps["U1"].primitive.name, "IC_TDM22545T")

    def test_unknown_primitive_fallback(self):
        """未知 primitive 應建立空 fallback"""
        comps = parse_pstxprt(FIXTURES_DIR / "pstxprt.dat", {})
        self.assertEqual(len(comps), 3)
        self.assertEqual(comps["C1"].primitive.name, "CAP_0603_0.1UF")
        self.assertEqual(comps["C1"].primitive.value, "")  # fallback


class TestParsePstxnet(unittest.TestCase):

    def setUp(self):
        prims = parse_pstchip(FIXTURES_DIR / "pstchip.dat")
        comps = parse_pstxprt(FIXTURES_DIR / "pstxprt.dat", prims)
        self.nets, self.pin_to_nets = parse_pstxnet(
            FIXTURES_DIR / "pstxnet.dat", comps
        )

    def test_loads_all_nets(self):
        self.assertEqual(len(self.nets), 3)
        self.assertIn("Vcc", self.nets)
        self.assertIn("GND", self.nets)
        self.assertIn("NET_VDRV", self.nets)

    def test_net_nodes_count(self):
        vcc = self.nets["Vcc"]
        self.assertEqual(len(vcc.nodes), 3)  # C1.1, U1.A1, R1.1

    def test_net_nodes_content(self):
        vcc = self.nets["Vcc"]
        refdes_set = {n.refdes for n in vcc.nodes}
        self.assertEqual(refdes_set, {"C1", "U1", "R1"})

    def test_pin_to_nets_physical(self):
        self.assertEqual(self.pin_to_nets[("C1", "1")], "Vcc")
        self.assertEqual(self.pin_to_nets[("C1", "2")], "GND")

    def test_pin_to_nets_logical_mapping(self):
        """U1 物理腳 A1 = 邏輯腳 VDD，都應對應到 Vcc"""
        self.assertEqual(self.pin_to_nets[("U1", "A1")], "Vcc")
        self.assertEqual(self.pin_to_nets[("U1", "VDD")], "Vcc")

    def test_pin_to_nets_logical_vdrv(self):
        self.assertEqual(self.pin_to_nets[("U1", "A2")], "NET_VDRV")
        self.assertEqual(self.pin_to_nets[("U1", "VDRV")], "NET_VDRV")


class TestLoadNetlist(unittest.TestCase):

    def setUp(self):
        self.nl = load_netlist(FIXTURES_DIR)

    def test_full_load(self):
        self.assertEqual(len(self.nl.primitives), 3)
        self.assertEqual(len(self.nl.components), 3)
        self.assertEqual(len(self.nl.nets), 3)

    def test_get_component_nets(self):
        nets = self.nl.get_component_nets("C1")
        self.assertIn("1", nets)
        self.assertIn("2", nets)
        self.assertEqual(nets["1"], "Vcc")
        self.assertEqual(nets["2"], "GND")

    def test_get_net_components(self):
        comps = self.nl.get_net_components("Vcc")
        refdes_list = [r for r, p, c in comps]
        self.assertIn("C1", refdes_list)
        self.assertIn("U1", refdes_list)

    def test_get_pin_net(self):
        self.assertEqual(self.nl.get_pin_net("C1", "1"), "Vcc")
        self.assertIsNone(self.nl.get_pin_net("NONEXISTENT", "1"))

    def test_get_other_pin(self):
        others = self.nl.get_other_pin("C1", "1")
        self.assertEqual(len(others), 1)
        self.assertEqual(others[0], ("C1", "2"))

    def test_missing_file_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(FileNotFoundError):
                load_netlist(tmpdir)


class TestComponentType(unittest.TestCase):

    def setUp(self):
        self.nl = load_netlist(FIXTURES_DIR)

    def test_capacitor_by_jedec(self):
        self.assertEqual(
            self.nl.components["C1"].primitive.component_type, "capacitor"
        )

    def test_resistor_by_jedec(self):
        self.assertEqual(
            self.nl.components["R1"].primitive.component_type, "resistor"
        )

    def test_ic_is_other(self):
        self.assertEqual(
            self.nl.components["U1"].primitive.component_type, "other"
        )


if __name__ == "__main__":
    unittest.main()
