# Circuit Checker

電路檢查系統 - 根據自定義規則驗證電路網表的正確性

## 功能特色

- 📝 **視覺化規則編輯器** - 使用 Vite + React 建立的友善介面
- 🔍 **智能電路檢查** - 支援 8 種連接規則類型
- 📊 **多格式支援** - PADs 和 Allegro 網表格式
- 🎯 **詳細報告** - 完整的檢查結果和錯誤訊息

## 快速開始

### 一鍵啟動所有服務

**Windows:**
```bash
start_all.bat
```

或使用 PowerShell:
```powershell
.\start_all.ps1
```

這將自動啟動：
- **前端 Rule Creator**: http://localhost:5173
- **後端 API**: http://127.0.0.1:8001
- **API 文件**: http://127.0.0.1:8001/docs

### 分別啟動

#### 前端 (Rule File Creator)
```bash
cd frontend
npm install
npm run dev
```
訪問: http://localhost:5173

#### 後端 (Circuit Checker API)
```bash
cd backend
start.bat
```
訪問: http://127.0.0.1:8001/docs

## 系統架構

```
circuit_checker/
├── frontend/          # Vite + React + TypeScript
│   ├── src/
│   │   ├── components/    # UI 組件
│   │   ├── store/         # Zustand 狀態管理
│   │   ├── types/         # TypeScript 類型定義
│   │   └── utils/         # YAML 工具
│   └── package.json
│
├── backend/           # FastAPI + Python 3.12
│   ├── parsers/       # PADs 和 Allegro 解析器
│   ├── models.py      # 資料模型
│   ├── rule_parser.py # YAML 規則解析
│   ├── rule_engine.py # 檢查引擎
│   ├── main.py        # FastAPI 應用
│   └── requirements.txt
│
├── examples/          # 範例規則檔案
│   ├── power_module_rules.yaml
│   └── simple_patterns.yaml
│
├── netlist/           # 測試網表檔案
│   └── PADs_type_netlist.asc
│
├── RULE_FORMAT.md     # 規則格式文件
├── start_all.ps1      # 啟動所有服務 (PowerShell)
└── start_all.bat      # 啟動所有服務 (Batch)
```

## 支援的規則類型

1. **direct_connection** - 直接網路連接 (支援 exact 和 regex)
2. **decoupling_capacitor** - 去耦電容檢查
3. **pull_up_resistor** - 上拉電阻
4. **pull_down_resistor** - 下拉電阻
5. **series_resistor** - 串聯電阻
6. **series_capacitor** - 串聯電容
7. **filter_network** - LC 濾波網路
8. **no_connection** - 未連接驗證

## 使用流程

### 1. 建立規則檔案

使用前端介面建立規則：
1. 訪問 http://localhost:5173
2. 新增 Component Rule
3. 填寫 Part Number, Package, Product Family
4. 定義 Pins 和 Connection Rules
5. 匯出 YAML 檔案

### 2. 執行電路檢查

使用 API 或測試腳本：

```bash
# 使用測試腳本
python test_backend.py

# 或使用 API
curl -X POST "http://127.0.0.1:8001/api/netlist/upload" \
  -F "file=@netlist/PADs_type_netlist.asc" \
  -F "format=pads"

curl -X POST "http://127.0.0.1:8001/api/rules/upload" \
  -F "file=@examples/power_module_rules.yaml"

curl -X POST "http://127.0.0.1:8001/api/check" \
  -d "netlist_id=PADs_type_netlist.asc" \
  -d "rule_id=power_module_rules.yaml" \
  -d "component_refdes=U15" \
  -d "part_number=TDM22545T"
```

### 3. 查看結果

檢查報告包含：
- 總檢查次數
- 通過/失敗/警告數量
- 每項檢查的詳細結果
- 錯誤訊息和建議

## API 端點

### 上傳 Netlist
```
POST /api/netlist/upload
Content-Type: multipart/form-data

file: <netlist.asc>
format: "pads" | "allegro"
```

### 上傳規則
```
POST /api/rules/upload
Content-Type: multipart/form-data

file: <rules.yaml>
```

### 執行檢查
```
POST /api/check

netlist_id: string
rule_id: string
component_refdes: string
part_number: string
```

### 列出上傳的檔案
```
GET /api/netlists
GET /api/rules
```

## 技術棧

### 前端
- **框架**: Vite 6 + React 18 + TypeScript
- **狀態管理**: Zustand + Immer
- **表單處理**: React Hook Form
- **YAML 處理**: js-yaml
- **驗證**: Ajv (JSON Schema)
- **編輯器**: Monaco Editor

### 後端
- **框架**: FastAPI 0.115.0
- **語言**: Python 3.12
- **驗證**: Pydantic 2.9.0
- **YAML**: PyYAML 6.0.2
- **伺服器**: Uvicorn

## 開發

### 前端開發
```bash
cd frontend
npm run dev    # 開發伺服器
npm run build  # 生產建置
npm run lint   # 程式碼檢查
```

### 後端開發
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

### 測試
```bash
# 後端測試
python test_backend.py

# 前端測試 (開發中)
cd frontend
npm test
```

## 範例檔案

### 規則檔案
- [examples/power_module_rules.yaml](examples/power_module_rules.yaml) - TDM22545T 電源模組規則
- [examples/simple_patterns.yaml](examples/simple_patterns.yaml) - 常見電路模式

### 網表檔案
- [netlist/PADs_type_netlist.asc](netlist/PADs_type_netlist.asc) - PADs 格式測試網表

## 部署

目標平台: OpenShift

部署設定檔 (開發中):
- `Dockerfile` - 容器化設定
- `openshift/` - OpenShift 部署配置

## 文件

- [RULE_FORMAT.md](RULE_FORMAT.md) - 完整的規則格式說明
- [frontend/FRONTEND_README.md](frontend/FRONTEND_README.md) - 前端使用指南
- [backend/README.md](backend/README.md) - 後端 API 文件

## 故障排除

### 埠號已被佔用
```powershell
# 停止佔用 8001 的進程
Get-NetTCPConnection -LocalPort 8001 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }

# 停止佔用 5173 的進程
Get-NetTCPConnection -LocalPort 5173 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

### Python 虛擬環境問題
```bash
# 刪除並重建
rm -rf backend/venv
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 前端依賴問題
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 授權

內部專案 - Infineon Technologies


