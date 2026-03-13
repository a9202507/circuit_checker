#!/usr/bin/env python3
"""
測試執行入口。
使用 unittest 標準庫，不需要安裝額外套件。

用法:
    python run_tests.py                # 執行全部測試
    python run_tests.py -v             # 詳細輸出
    python run_tests.py tests/test_rules.py  # 只跑指定檔案
"""

import sys
import os
import unittest

# 確保 src/ 和專案根目錄都在 PYTHONPATH 中
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, ROOT)


def main():
    loader = unittest.TestLoader()

    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        # 指定了特定測試模組
        suite = unittest.TestSuite()
        for arg in sys.argv[1:]:
            if arg.startswith("-"):
                continue
            suite.addTests(loader.discover(
                start_dir=os.path.dirname(arg) or "tests",
                pattern=os.path.basename(arg),
                top_level_dir=ROOT,
            ))
    else:
        # 自動發現所有測試
        suite = loader.discover(
            start_dir="tests",
            pattern="test_*.py",
            top_level_dir=ROOT,
        )

    verbosity = 2 if "-v" in sys.argv else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
