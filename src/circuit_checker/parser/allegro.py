"""
Allegro PST Netlist Parser
解析 pstchip.dat / pstxnet.dat / pstxprt.dat 三個檔案，
建立統一的電路資料模型供 rule engine 使用。
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path


# ─── 資料模型 ────────────────────────────────────────────────────────────────

@dataclass
class PinDef:
    """pstchip.dat 中的 pin 定義"""
    name: str
    number: str
    use: str  # UNSPEC / PWR / GND / IN / OUT / ...


@dataclass
class Primitive:
    """pstchip.dat 中的零件原型（library part）"""
    name: str
    part_name: str = ""
    jedec_type: str = ""
    value: str = ""
    part_class: str = ""          # DISCRETE / IC / ...
    pins: dict[str, PinDef] = field(default_factory=dict)  # pin_name -> PinDef

    @property
    def component_type(self) -> str:
        """根據 JEDEC_TYPE 推斷零件類型"""
        jt = self.jedec_type.upper()
        if re.search(r'IR_C\d|DCASE', jt):
            return "capacitor"
        if re.search(r'IR_R\d|SMR', jt):
            return "resistor"
        if "IND" in jt:
            return "inductor"
        # fallback: 用 value 判斷
        v = self.value.upper()
        if re.search(r'\d\s*(UF|NF|PF)\b', v):
            return "capacitor"
        if re.search(r'\d\s*(OHM|Ω)\b', v) or re.match(r'^\d+(\.\d+)?\s*$', v):
            return "resistor"
        return "other"


@dataclass
class Component:
    """電路板上的一個元件（refdes）"""
    refdes: str
    primitive: Primitive


@dataclass
class NetNode:
    """net 上的一個節點"""
    refdes: str
    pin: str


@dataclass
class Net:
    """一條 net（導線）"""
    name: str
    nodes: list[NetNode] = field(default_factory=list)


@dataclass
class Netlist:
    """完整的電路資料模型"""
    primitives: dict[str, Primitive]          # primitive_name -> Primitive
    components: dict[str, Component]          # refdes -> Component
    nets: dict[str, Net]                      # net_name -> Net
    pin_to_nets: dict[tuple[str, str], str]   # (refdes, pin) -> net_name

    def get_component_nets(self, refdes: str) -> dict[str, str]:
        """回傳某元件所有 pin 對應的 net，{pin: net_name}"""
        result = {}
        comp = self.components.get(refdes)
        if not comp:
            return result
        for pin_name in comp.primitive.pins:
            net = self.pin_to_nets.get((refdes, pin_name))
            if net:
                result[pin_name] = net
        return result

    def get_net_components(self, net_name: str) -> list[tuple[str, str, Component]]:
        """回傳 net 上所有 (refdes, pin, Component)"""
        net = self.nets.get(net_name)
        if not net:
            return []
        result = []
        for node in net.nodes:
            comp = self.components.get(node.refdes)
            if comp:
                result.append((node.refdes, node.pin, comp))
        return result

    def get_other_pin(self, refdes: str, this_pin: str) -> list[tuple[str, str]]:
        """
        對一個兩腳元件，找出另一腳的 (refdes, pin)。
        回傳 [(refdes, other_pin), ...]（通常只有一個）
        """
        comp = self.components.get(refdes)
        if not comp:
            return []
        return [
            (refdes, p)
            for p in comp.primitive.pins
            if p != this_pin
        ]

    def get_pin_net(self, refdes: str, pin: str) -> str | None:
        return self.pin_to_nets.get((refdes, pin))


# ─── 解析函式 ─────────────────────────────────────────────────────────────────

def _strip_quotes(s: str) -> str:
    return s.strip().strip("'\"")


def parse_pstchip(path: Path) -> dict[str, Primitive]:
    """解析 pstchip.dat → {primitive_name: Primitive}"""
    primitives: dict[str, Primitive] = {}
    current: Primitive | None = None
    in_pin = False
    current_pin_name: str | None = None

    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if stripped.startswith("primitive "):
            name = _strip_quotes(stripped[len("primitive "):].rstrip(";"))
            current = Primitive(name=name)
            in_pin = False
            current_pin_name = None

        elif stripped == "end_primitive;" and current:
            primitives[current.name] = current
            current = None

        elif stripped == "pin" and current:
            in_pin = True

        elif stripped == "end_pin;" and current:
            in_pin = False
            current_pin_name = None

        elif in_pin and current:
            # pin name line: '1': 或 'GATE':
            m = re.match(r"'([^']+)':", stripped)
            if m and not stripped.startswith("PIN_NUMBER") and not stripped.startswith("PINUSE"):
                current_pin_name = m.group(1)
                if current_pin_name not in current.pins:
                    current.pins[current_pin_name] = PinDef(
                        name=current_pin_name, number="", use="UNSPEC"
                    )
            elif current_pin_name:
                if stripped.startswith("PIN_NUMBER="):
                    num = re.search(r"'([^']*)'", stripped)
                    if num:
                        current.pins[current_pin_name].number = num.group(1).strip("()")
                elif stripped.startswith("PINUSE="):
                    use = re.search(r"'([^']*)'", stripped)
                    if use:
                        current.pins[current_pin_name].use = use.group(1)

        elif not in_pin and current:
            if stripped.startswith("PART_NAME="):
                m = re.search(r"'([^']*)'", stripped)
                if m:
                    current.part_name = m.group(1)
            elif stripped.startswith("JEDEC_TYPE="):
                m = re.search(r"'([^']*)'", stripped)
                if m:
                    current.jedec_type = m.group(1)
            elif stripped.startswith("VALUE="):
                m = re.search(r"'([^']*)'", stripped)
                if m:
                    current.value = m.group(1)
            elif stripped.startswith("CLASS="):
                m = re.search(r"'([^']*)'", stripped)
                if m:
                    current.part_class = m.group(1)

        i += 1

    return primitives


def parse_pstxprt(path: Path, primitives: dict[str, Primitive]) -> dict[str, Component]:
    """解析 pstxprt.dat → {refdes: Component}"""
    components: dict[str, Component] = {}

    with open(path, encoding="utf-8", errors="replace") as f:
        content = f.read()

    # PART_NAME 行格式: PART_NAME\n REFDES 'PRIMITIVE_NAME':;
    pattern = re.compile(
        r"^PART_NAME\s*\n\s+(\S+)\s+'([^']+)'", re.MULTILINE
    )
    for m in pattern.finditer(content):
        refdes = m.group(1)
        prim_name = m.group(2)
        prim = primitives.get(prim_name)
        if prim is None:
            # 建立一個空的 Primitive 當 fallback
            prim = Primitive(name=prim_name)
        components[refdes] = Component(refdes=refdes, primitive=prim)

    return components


def parse_pstxnet(
    path: Path, components: dict[str, Component]
) -> tuple[dict[str, Net], dict[tuple[str, str], str]]:
    """
    解析 pstxnet.dat
    回傳 (nets, pin_to_nets)
      nets:        {net_name: Net}
      pin_to_nets: {(refdes, pin): net_name}
                   同時儲存物理腳號 (A8) 和邏輯腳名 (IMON2) 兩種 key

    NODE_NAME 區塊格式（共三行）：
      NODE_NAME\\tREFDES  PHYS_PIN
       '@instance_path':
       'LOGICAL_PIN':;
    """
    nets: dict[str, Net] = {}
    pin_to_nets: dict[tuple[str, str], str] = {}

    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    current_net: Net | None = None
    expect_net_name = False
    # 等待讀取邏輯腳名的暫存狀態
    pending_node: tuple[str, str] | None = None   # (refdes, phys_pin)
    skip_instance_line = False                     # 跳過 '@...' 那行

    for line in lines:
        stripped = line.strip()

        # ── 邏輯腳名讀取狀態機 ──────────────────────────────────
        if pending_node and skip_instance_line:
            # 跳過 '@instance_path': 那一行
            if stripped.startswith("'@"):
                skip_instance_line = False
            continue

        if pending_node and not skip_instance_line:
            # 下一個 'XXX':; 就是邏輯腳名
            m = re.match(r"'([^']+)':;", stripped)
            if m:
                logical_pin = m.group(1)
                refdes, phys_pin = pending_node
                # 若邏輯名與物理名不同，額外建立邏輯名的對應
                if logical_pin != phys_pin:
                    pin_to_nets[(refdes, logical_pin)] = pin_to_nets[(refdes, phys_pin)]
            pending_node = None
            continue
        # ──────────────────────────────────────────────────────

        if stripped == "NET_NAME":
            expect_net_name = True
            continue

        if expect_net_name and stripped.startswith("'"):
            net_name = _strip_quotes(stripped.split("'")[1])
            current_net = Net(name=net_name)
            nets[net_name] = current_net
            expect_net_name = False
            continue

        if stripped.startswith("NODE_NAME") and current_net:
            # 格式: NODE_NAME\tREFDES PHYS_PIN
            rest = re.split(r"\s+", stripped, maxsplit=2)
            if len(rest) >= 3:
                refdes = rest[1]
                phys_pin = rest[2]
                node = NetNode(refdes=refdes, pin=phys_pin)
                current_net.nodes.append(node)
                pin_to_nets[(refdes, phys_pin)] = current_net.name
                # 進入等待邏輯腳名的狀態
                pending_node = (refdes, phys_pin)
                skip_instance_line = True

    return nets, pin_to_nets


def load_netlist(netlist_dir: str | Path) -> Netlist:
    """
    從指定目錄讀取三個 PST 檔案，回傳 Netlist 物件。
    """
    d = Path(netlist_dir)
    pstchip = d / "pstchip.dat"
    pstxprt = d / "pstxprt.dat"
    pstxnet = d / "pstxnet.dat"

    for f in (pstchip, pstxprt, pstxnet):
        if not f.exists():
            raise FileNotFoundError(f"找不到 netlist 檔案：{f}")

    primitives = parse_pstchip(pstchip)
    components = parse_pstxprt(pstxprt, primitives)
    nets, pin_to_nets = parse_pstxnet(pstxnet, components)

    return Netlist(
        primitives=primitives,
        components=components,
        nets=nets,
        pin_to_nets=pin_to_nets,
    )
