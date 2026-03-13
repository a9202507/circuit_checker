# OrCAD Schematic Auto Checker (方案1 - TCL + Python)

**專案名稱**：`orcad-schematic-checker`  
**版本**：v1.0 (2026)  
**Python 版本**：**3.12**（強制要求）  
**套件管理器**：**uv**（Astral 官方推薦）  
**本地環境**：OrCAD Capture 2022（完整連動）  
**伺服器環境**（OpenShift / Docker）：僅支援 Allegro netlist（無 OrCAD）

---

## ✨ 功能亮點

- 一鍵輸入 `.dsn`（本地）或 `.net`（OpenShift），自動產生**簡潔風格**報告
- 規則全部放在 `rules.yaml`（易讀、易改）
- 支援你所有客製規則：
  - Vcc 必須接 0.1uF 到 GND
  - PWM pin 必須 floating
  - VDD pin 與 VDRV pin 之間必須有 1Ω 電阻
  - VDD / VDRV 各自需接 0.1uF 到 GND
- 輸出格式：**HTML**（預設，超簡潔）或 **PDF**（使用者可選擇）
- 本地模式：直接呼叫 OrCAD Capture 2022 產生 netlist（背景執行）
- OpenShift 模式：純 Python，只吃 Allegro netlist（無 TCL、無 OrCAD）

---

## 📋 前置需求

### 本機（Windows + OrCAD）
- OrCAD Capture 2022（含 TCL 引擎）
- Python **3.12**（官方）
- uv（推薦安裝方式）：
  ```bash
  # Windows
  winget install --id=astral-sh.uv -e
  # 或從 https://docs.astral.sh/uv/getting-started/installation/