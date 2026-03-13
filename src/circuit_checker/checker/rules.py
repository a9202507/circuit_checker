"""
Rule Engine
讀取 rules.yaml 並對 Netlist 執行所有規則檢查。
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from circuit_checker.parser.allegro import Netlist, Component


# ─── 結果資料結構 ─────────────────────────────────────────────────────────────

@dataclass
class CheckResult:
    rule_name: str
    rule_type: str
    passed: bool
    message: str
    detail: list[str] = field(default_factory=list)


# ─── 工具函式 ─────────────────────────────────────────────────────────────────

_VALUE_RE = re.compile(
    r"(?P<num>[\d.]+)\s*(?P<prefix>[pnumkKMG]?)(?P<unit>[FfHhΩRr]?)", re.IGNORECASE
)

_PREFIX_MAP = {
    "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3,
    "": 1.0,
    "k": 1e3, "K": 1e3, "M": 1e6, "G": 1e9,
}


def _parse_value(s: str) -> float | None:
    """把 '0.1uF'、'1'、'100k' 等字串轉成 float（SI 單位）"""
    s = s.strip().replace("Ω", "R").replace("ohm", "R").replace("OHM", "R")
    m = _VALUE_RE.search(s)
    if not m:
        return None
    num = float(m.group("num"))
    prefix = m.group("prefix") or ""
    mult = _PREFIX_MAP.get(prefix, 1.0)
    return num * mult


def _values_match(target: str, actual: str, tolerance_str: str = "20%") -> bool:
    """在容差範圍內比對兩個數值字串"""
    t = _parse_value(target)
    a = _parse_value(actual)
    if t is None or a is None:
        # fallback: 字串直接比對（不分大小寫）
        return target.strip().lower() == actual.strip().lower()
    tol = 0.20
    m = re.search(r"([\d.]+)%", tolerance_str)
    if m:
        tol = float(m.group(1)) / 100
    return abs(a - t) <= t * tol


def _is_gnd(net_name: str) -> bool:
    """判斷某 net 是否為 GND（支援 GND / AGND / PGND / GND2 等變體）"""
    return bool(re.match(r"^[AP]?GND\d*$", net_name, re.IGNORECASE))


def _other_pins(netlist: Netlist, refdes: str, this_pin: str) -> list[str]:
    """
    回傳同一元件其他腳的 net 名稱。
    直接從 pin_to_nets 找同 refdes 的所有腳，排除 this_pin，
    避免物理腳號 vs 邏輯腳名不一致的問題。
    """
    result = []
    seen_nets: set[str] = set()
    for (r, p), net in netlist.pin_to_nets.items():
        if r == refdes and p != this_pin and net not in seen_nets:
            result.append(net)
            seen_nets.add(net)
    return result


# ─── 各規則實作 ───────────────────────────────────────────────────────────────

def _check_net_cap_to_gnd(rule: dict, netlist: Netlist) -> CheckResult:
    """
    net_cap_to_gnd：指定 net 上必須有電容接到 GND
    """
    net_name: str = rule["net"]
    target_value: str = rule.get("value", "0.1uF")
    tolerance: str = rule.get("tolerance", "20%")

    net = netlist.nets.get(net_name)
    if not net:
        return CheckResult(
            rule_name=rule["name"],
            rule_type=rule["type"],
            passed=False,
            message=f"找不到 net '{net_name}'",
        )

    found: list[str] = []
    for refdes, pin, comp in netlist.get_net_components(net_name):
        if comp.primitive.component_type != "capacitor":
            continue
        # 確認另一腳接 GND
        other_net_names = _other_pins(netlist, refdes, pin)
        for other_net in other_net_names:
            if _is_gnd(other_net):
                actual_val = comp.primitive.value
                if _values_match(target_value, actual_val, tolerance):
                    found.append(
                        f"{refdes} ({actual_val}) — {net_name} ↔ {other_net}"
                    )

    if found:
        return CheckResult(
            rule_name=rule["name"],
            rule_type=rule["type"],
            passed=True,
            message=f"共找到 {len(found)} 個符合的電容",
            detail=found,
        )
    return CheckResult(
        rule_name=rule["name"],
        rule_type=rule["type"],
        passed=False,
        message=f"net '{net_name}' 上找不到 {target_value} 電容接到 GND",
    )


def _check_pin_floating(rule: dict, netlist: Netlist) -> CheckResult:
    """
    pin_floating：指定 pin 必須為 floating（不接任何 net，
    或所在 net 只有這一個 node）
    """
    pins: list[str] = rule.get("pins", [])
    failed: list[str] = []
    passed_pins: list[str] = []

    for pin_spec in pins:
        parts = pin_spec.split(".", 1)
        if len(parts) != 2:
            failed.append(f"{pin_spec}（格式錯誤，需為 REFDES.PIN）")
            continue
        refdes, pin = parts

        net_name = netlist.get_pin_net(refdes, pin)
        if net_name is None:
            # 真的 floating（完全沒接）
            passed_pins.append(f"{pin_spec} ✓ floating")
        else:
            net = netlist.nets.get(net_name)
            # 若 net 只有這一個 node，仍視為 floating（dangling net）
            if net and len(net.nodes) == 1:
                passed_pins.append(f"{pin_spec} ✓ floating（dangling net '{net_name}'）")
            else:
                failed.append(f"{pin_spec} ✗ 接到 net '{net_name}'（{len(net.nodes) if net else '?'} 個節點）")

    ok = len(failed) == 0
    return CheckResult(
        rule_name=rule["name"],
        rule_type=rule["type"],
        passed=ok,
        message="所有指定 pin 均為 floating" if ok else f"{len(failed)} 個 pin 不符合",
        detail=passed_pins + failed,
    )


def _check_pin_to_pin_resistor(rule: dict, netlist: Netlist) -> CheckResult:
    """
    pin_to_pin_resistor：兩個 pin 之間必須有指定阻值的電阻
    """
    pin1_spec: str = rule["pin1"]
    pin2_spec: str = rule["pin2"]
    target_value: str = rule.get("value", "1")
    tolerance: str = rule.get("tolerance", "20%")

    def parse_pin(spec: str) -> tuple[str, str] | None:
        parts = spec.split(".", 1)
        return (parts[0], parts[1]) if len(parts) == 2 else None

    p1 = parse_pin(pin1_spec)
    p2 = parse_pin(pin2_spec)

    if not p1 or not p2:
        return CheckResult(
            rule_name=rule["name"],
            rule_type=rule["type"],
            passed=False,
            message=f"pin 格式錯誤（需為 REFDES.PIN）",
        )

    net1 = netlist.get_pin_net(*p1)
    net2 = netlist.get_pin_net(*p2)

    if net1 is None:
        return CheckResult(
            rule_name=rule["name"],
            rule_type=rule["type"],
            passed=False,
            message=f"{pin1_spec} 找不到對應的 net",
        )
    if net2 is None:
        return CheckResult(
            rule_name=rule["name"],
            rule_type=rule["type"],
            passed=False,
            message=f"{pin2_spec} 找不到對應的 net",
        )

    # 在 net1 上找電阻，確認電阻另一腳接到 net2
    found: list[str] = []
    for refdes, pin, comp in netlist.get_net_components(net1):
        if comp.primitive.component_type != "resistor":
            continue
        other_nets = _other_pins(netlist, refdes, pin)
        if net2 in other_nets:
            actual_val = comp.primitive.value
            if _values_match(target_value, actual_val, tolerance):
                found.append(
                    f"{refdes} ({actual_val}Ω) — {net1} ↔ {net2}"
                )

    if found:
        return CheckResult(
            rule_name=rule["name"],
            rule_type=rule["type"],
            passed=True,
            message=f"找到 {len(found)} 個符合的電阻",
            detail=found,
        )
    return CheckResult(
        rule_name=rule["name"],
        rule_type=rule["type"],
        passed=False,
        message=(
            f"{pin1_spec}（net={net1}）與 {pin2_spec}（net={net2}）"
            f"之間找不到 {target_value}Ω 電阻"
        ),
    )


def _check_pin_cap_to_gnd(rule: dict, netlist: Netlist) -> CheckResult:
    """
    pin_cap_to_gnd：每個指定 pin 的 net 上，必須有電容接到 GND
    """
    pins: list[str] = rule.get("pins", [])
    target_value: str = rule.get("value", "0.1uF")
    tolerance: str = rule.get("tolerance", "20%")

    failed: list[str] = []
    passed_pins: list[str] = []

    for pin_spec in pins:
        parts = pin_spec.split(".", 1)
        if len(parts) != 2:
            failed.append(f"{pin_spec}（格式錯誤）")
            continue
        refdes, pin = parts

        net_name = netlist.get_pin_net(refdes, pin)
        if net_name is None:
            failed.append(f"{pin_spec} ✗ 沒有接到任何 net")
            continue

        # 在這條 net 上找符合的電容
        cap_found = []
        for r, p, comp in netlist.get_net_components(net_name):
            if comp.primitive.component_type != "capacitor":
                continue
            other_nets = _other_pins(netlist, r, p)
            for other_net in other_nets:
                if _is_gnd(other_net):
                    if _values_match(target_value, comp.primitive.value, tolerance):
                        cap_found.append(
                            f"{r} ({comp.primitive.value}) — {net_name} ↔ {other_net}"
                        )

        if cap_found:
            passed_pins.append(f"{pin_spec} ✓ net='{net_name}'，找到 {len(cap_found)} 個電容")
            passed_pins.extend(f"    {c}" for c in cap_found)
        else:
            failed.append(
                f"{pin_spec} ✗ net='{net_name}' 上找不到 {target_value} 電容接到 GND"
            )

    ok = len(failed) == 0
    return CheckResult(
        rule_name=rule["name"],
        rule_type=rule["type"],
        passed=ok,
        message="所有 pin 均有電容到 GND" if ok else f"{len(failed)} 個 pin 不符合",
        detail=passed_pins + failed,
    )


# ─── 主入口 ──────────────────────────────────────────────────────────────────

_HANDLERS = {
    "net_cap_to_gnd":      _check_net_cap_to_gnd,
    "pin_floating":        _check_pin_floating,
    "pin_to_pin_resistor": _check_pin_to_pin_resistor,
    "pin_cap_to_gnd":      _check_pin_cap_to_gnd,
}


def load_rules(rules_file: str | Path) -> list[dict]:
    with open(rules_file, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("rules", [])


def run_checks(netlist: Netlist, rules: list[dict]) -> list[CheckResult]:
    results: list[CheckResult] = []
    for rule in rules:
        rule_type = rule.get("type", "")
        handler = _HANDLERS.get(rule_type)
        if handler is None:
            results.append(CheckResult(
                rule_name=rule.get("name", rule_type),
                rule_type=rule_type,
                passed=False,
                message=f"未知的規則類型：'{rule_type}'",
            ))
        else:
            results.append(handler(rule, netlist))
    return results
