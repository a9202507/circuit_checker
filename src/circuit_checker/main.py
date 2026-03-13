"""
Circuit Checker CLI
用法：
  circuit-checker --netlist ./netlist --rules ./rules/rule_example.yaml
  circuit-checker --netlist ./netlist --rules ./rules/rule_example.yaml --output report.html
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

from circuit_checker.parser.allegro import load_netlist
from circuit_checker.checker.rules import load_rules, run_checks
from circuit_checker.reporter.html import generate_html


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="circuit-checker",
        description="Allegro PST Netlist 規則檢查工具",
    )
    parser.add_argument(
        "--netlist", "-n",
        required=True,
        help="Allegro netlist 目錄（含 pstchip.dat / pstxnet.dat / pstxprt.dat）",
    )
    parser.add_argument(
        "--rules", "-r",
        required=True,
        help="規則 YAML 檔案路徑",
    )
    parser.add_argument(
        "--output", "-o",
        default="report.html",
        help="輸出 HTML 報告路徑（預設：report.html）",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="在終端機顯示詳細結果",
    )
    args = parser.parse_args()

    netlist_dir = Path(args.netlist)
    rules_file  = Path(args.rules)
    output_path = Path(args.output)

    # 1. 載入 netlist
    print(f"[1/3] 解析 netlist：{netlist_dir}")
    try:
        netlist = load_netlist(netlist_dir)
    except FileNotFoundError as e:
        print(f"  錯誤：{e}", file=sys.stderr)
        sys.exit(1)

    print(f"      零件數：{len(netlist.components)}　"
          f"Net 數：{len(netlist.nets)}　"
          f"零件原型：{len(netlist.primitives)}")

    # 2. 載入並執行規則
    print(f"[2/3] 載入規則：{rules_file}")
    try:
        rules = load_rules(rules_file)
    except Exception as e:
        print(f"  錯誤：{e}", file=sys.stderr)
        sys.exit(1)

    print(f"      共 {len(rules)} 條規則")
    results = run_checks(netlist, rules)

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    print(f"      結果：PASS {passed} / FAIL {failed}")

    # 3. 輸出報告
    print(f"[3/3] 產生報告：{output_path}")
    generate_html(
        results=results,
        netlist_dir=str(netlist_dir.resolve()),
        rules_file=str(rules_file.resolve()),
        output_path=output_path,
    )
    print(f"      報告已輸出至 {output_path.resolve()}")

    # 終端機詳細輸出
    if args.verbose:
        print()
        for r in results:
            status = "✓ PASS" if r.passed else "✗ FAIL"
            print(f"  {status}  [{r.rule_type}]  {r.rule_name}")
            print(f"         {r.message}")
            for d in r.detail:
                print(f"         {d}")

    # 若有失敗，以非零 exit code 結束（方便 CI 整合）
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
