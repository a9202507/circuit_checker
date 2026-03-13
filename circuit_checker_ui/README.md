# Circuit Checker Rules UI

一個現代化的 Web UI，用於管理和編輯 circuit-checker 的規則檔案。

**Tech Stack:**
- 前端：Vite 6 + React 18 + TypeScript + Tailwind CSS
- 後端：FastAPI + Uvicorn
- 驗證：PyYAML

## 快速開始

### 前置要求
- Node.js 18+
- Python 3.10+

### 安装依赖

```bash
# 前端
npm install

# 後端（可選，通常自動安裝）
pip install fastapi uvicorn pyyaml python-multipart --break-system-packages
```

### 開發模式

**終端 1：啟動後端**
```bash
npm run api:dev
```
後端將在 `http://localhost:8000` 啟動

**終端 2：啟動前端開發伺服器**
```bash
npm run dev
```
前端將在 `http://localhost:5173` 啟動

### 生產構建

```bash
# 構建前端
npm run build

# 啟動生產後端
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## 功能

### 📝 YAML 編輯器
- 直接編輯 YAML 內容
- 匯入本地 rules.yaml 檔案
- 實時語法驗證
- 匯出驗證後的規則

### 🔨 規則構建器
- 圖形化規則編輯器
- 四種規則類型支持
- 實時 YAML 生成
- 規則範本庫

### 📚 新手指南
- 快速開始教程
- 規則類型詳細說明
- 常見問題解答
- 最佳實踐建議

## API 端點

| 方法 | 端點 | 說明 |
|------|------|------|
| POST | `/validate` | 驗證 YAML 內容 |
| POST | `/parse` | 解析上傳的 YAML 檔案 |
| POST | `/generate` | 從規則列表生成 YAML |
| GET | `/templates` | 取得規則範本 |
| GET | `/examples` | 取得完整範例 |
| GET | `/health` | 健康檢查 |

## Docker 部署

```dockerfile
# 多階段構建
FROM node:18 as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM python:3.10
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY api ./api
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## OpenShift 部署

```bash
# 建立 DeploymentConfig
oc new-app python:3.10~https://your-repo.git \
  --name=circuit-checker-ui \
  --context-dir=.

# 暴露服務
oc expose svc/circuit-checker-ui
```

## 項目結構

```
circuit_checker_ui/
├── src/
│   ├── components/          # React 組件
│   │   ├── Navigation.tsx
│   │   ├── YamlEditor.tsx
│   │   ├── RuleBuilder.tsx
│   │   ├── RuleForm.tsx
│   │   ├── ValidationResults.tsx
│   │   └── BeginnerGuide.tsx
│   ├── api/
│   │   └── client.ts        # API 客户端
│   ├── App.tsx              # 主應用
│   ├── main.tsx             # 進入點
│   └── index.css            # 全局樣式
├── api/
│   ├── main.py              # FastAPI 應用
│   └── models.py            # Pydantic 模型
├── public/                  # 靜態資源
├── vite.config.ts
├── tsconfig.json
└── package.json
```

## 規則類型說明

### net_cap_to_gnd
驗證指定 net 上必須有電容接到 GND。

### pin_floating
驗證指定 pin 必須為 floating（不接任何 net）。

### pin_to_pin_resistor
驗證兩個 pin 之間必須有指定阻值的電阻。

### pin_cap_to_gnd
驗證每個指定 pin 的 net 上必須有電容接到 GND。

## 開發筆記

- API 在 `http://localhost:8000`
- 前端代理設定在 `vite.config.ts` 的 `/api` 路徑
- Tailwind CSS 用於樣式
- 所有 API 響應支持 CORS

## 常見問題

**Q: 如何在 Windows 上開發？**
A: 可以使用 Git Bash 或 WSL。確保 Python 和 Node.js 正確安裝。

**Q: 為什麼驗證失敗？**
A: 檢查 YAML 語法、必填欄位是否完整。查看「新手指南」獲取更多幫助。

**Q: 如何在 OpenShift 上部署？**
A: 使用提供的 Dockerfile 建立鏡像，然後通過 `oc new-app` 部署。

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 許可

MIT
