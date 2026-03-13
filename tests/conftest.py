"""
Shared test utilities for circuit_checker tests.
提供可重用的 Netlist 構造輔助函式和 Builder。
（不依賴 pytest，純 Python 標準庫即可使用）
"""

from __future__ import annotations

from pathlib import Path

from circuit_checker.parser.allegro import (
    Netlist, Primitive, Component, Net, NetNode, PinDef,
)


# ── 輔助建構函式 ──────────────────────────────────────────────────────────────


def make_primitive(
    name: str,
    value: str = "",
    jedec_type: str = "",
    part_name: str = "",
    part_class: str = "DISCRETE",
    pin_names: list[str] | None = None,
) -> Primitive:
    """快速建立 Primitive（預設兩腳元件）"""
    if pin_names is None:
        pin_names = ["1", "2"]
    pins = {
        p: PinDef(name=p, number=f"({p})", use="UNSPEC")
        for p in pin_names
    }
    return Primitive(
        name=name,
        part_name=part_name or name,
        jedec_type=jedec_type,
        value=value,
        part_class=part_class,
        pins=pins,
    )


def make_cap(name: str = "CAP_0603", value: str = "0.1uF") -> Primitive:
    """建立電容 Primitive"""
    return make_primitive(name=name, value=value, jedec_type="IR_C0603")


def make_resistor(name: str = "RES_0603", value: str = "1") -> Primitive:
    """建立電阻 Primitive"""
    return make_primitive(name=name, value=value, jedec_type="IR_R0603")


def make_ic(
    name: str = "IC_U1",
    pin_names: list[str] | None = None,
) -> Primitive:
    """建立 IC Primitive"""
    if pin_names is None:
        pin_names = ["VDD", "VDRV", "PWM", "GND"]
    return make_primitive(
        name=name,
        value="",
        jedec_type="QFN32",
        part_class="IC",
        pin_names=pin_names,
    )


class NetlistBuilder:
    """
    流式介面，方便在測試中快速組裝 Netlist。

    用法:
        nl = (NetlistBuilder()
              .add_primitive(cap_prim)
              .add_component("C1", cap_prim)
              .add_net("Vcc", [("C1", "1"), ("U1", "VDD")])
              .add_net("GND", [("C1", "2")])
              .build())
    """

    def __init__(self) -> None:
        self._primitives: dict[str, Primitive] = {}
        self._components: dict[str, Component] = {}
        self._nets: dict[str, Net] = {}
        self._pin_to_nets: dict[tuple[str, str], str] = {}

    def add_primitive(self, prim: Primitive) -> "NetlistBuilder":
        self._primitives[prim.name] = prim
        return self

    def add_component(self, refdes: str, prim: Primitive) -> "NetlistBuilder":
        if prim.name not in self._primitives:
            self._primitives[prim.name] = prim
        self._components[refdes] = Component(refdes=refdes, primitive=prim)
        return self

    def add_net(
        self, name: str, nodes: list[tuple[str, str]]
    ) -> "NetlistBuilder":
        net_nodes = [NetNode(refdes=r, pin=p) for r, p in nodes]
        self._nets[name] = Net(name=name, nodes=net_nodes)
        for r, p in nodes:
            self._pin_to_nets[(r, p)] = name
        return self

    def build(self) -> Netlist:
        return Netlist(
            primitives=dict(self._primitives),
            components=dict(self._components),
            nets=dict(self._nets),
            pin_to_nets=dict(self._pin_to_nets),
        )


FIXTURES_DIR = Path(__file__).parent / "fixtures"
