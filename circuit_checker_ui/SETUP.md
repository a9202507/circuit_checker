# 快速設置指南

## 一鍵本地開發設置

### Mac 環境

#### 前置檢查
```bash
# 確認已安裝 Node.js 和 Python
node --version  # 需要 v18+
python3 --version  # 需要 3.10+
```

#### 安裝和啟動

```bash
# 1. 進入項目目錄
cd circuit_checker_ui

# 2. 安裝前端依賴
npm install

# 3. 安裝後端依賴
pip install fastapi uvicorn pyyaml python-multipart --break-system-packages

# 4. 啟動後端（新終端）
npm run api:dev
# 後端在 http://localhost:8000 啟動

# 5. 啟動前端（另一個新終端）
npm run dev
# 前端在 http://localhost:5173 啟動

# 6. 打開瀏覽器
open http://localhost:5173
```

### Docker 開發（推薦）

```bash
# 一行命令啟動整個應用
docker-compose up

# 前端：http://localhost:5173
# 後端：http://localhost:8000
# 後端 API docs：http://localhost:8000/docs
```

## 項目目錄結構

```
circuit_checker_ui/
├── src/                               # 前端源碼
│   ├── components/
│   │   ├── Navigation.tsx            # 頂部導航欄
│   │   ├── YamlEditor.tsx            # YAML 編輯器（匯入/匯出/驗證）
│   │   ├── RuleBuilder.tsx           # 規則構建器（表單介面）
│   │   ├── RuleForm.tsx              # 規則編輯表單
│   │   ├── ValidationResults.tsx     # 驗證結果顯示
│   │   └── BeginnerGuide.tsx         # 新手指南
│   ├── api/
│   │   └── client.ts                 # API 客户端
│   ├── App.tsx                       # 主應用元件
│   ├── main.tsx                      # 進入點
│   └── index.css                     # 全局樣式
│
├── api/                              # 後端源碼
│   ├── main.py                       # FastAPI 主應用
│   ├── main_with_static.py           # 生產版（含靜態檔案）
│   ├── models.py                     # Pydantic 資料模型
│   └── __init__.py
│
├── public/                           # 靜態資源
│
├── 配置檔案
├── vite.config.ts                    # Vite 配置
├── tsconfig.json                     # TypeScript 配置
├── tailwind.config.js                # Tailwind CSS 配置
├── postcss.config.js                 # PostCSS 配置
├── package.json                      # NPM 依賴
│
├── Docker 部署
├── Dockerfile                        # 生產多階段構建
├── Dockerfile.backend                # 後端開發容器
├── Dockerfile.frontend               # 前端開發容器
├── docker-compose.yml                # Docker Compose 配置
│
├── 文檔
├── README.md                         # 項目文檔
├── DEMO.md                           # 功能演示
└── SETUP.md                          # 本檔案
```

## 核心功能

### 🎨 三個主要標籤頁

#### 1️⃣ YAML 編輯器 (`📝 YAML 編輯器`)
- **直接編輯模式**：貼上或編寫 YAML
- **匯入功能**：上傳 .yaml / .yml 檔案
- **實時驗證**：檢查語法和規則有效性
- **匯出功能**：下載驗證通過的 rules.yaml
- **錯誤報告**：詳細的錯誤信息和定位

#### 2️⃣ 規則構建器 (`🔨 規則構建器`)
- **圖形化編輯**：使用表單而不是直接編輯 YAML
- **4 種規則類型**：
  - net_cap_to_gnd：電容到 GND
  - pin_floating：Pin Floating
  - pin_to_pin_resistor：Pin 間電阻
  - pin_cap_to_gnd：Pin 電容到 GND
- **模板庫**：快速開始預設
- **規則管理**：新增、編輯、刪除規則
- **自動生成**：生成有效 YAML

#### 3️⃣ 新手指南 (`📚 新手指南`)
- **快速開始流程**：4 步入門
- **規則詳解**：每種規則的完整說明
- **常見問題**：FAQ 解答
- **最佳實踐**：設計建議
- **一鍵建立**：從範本快速建立規則

## API 端點參考

所有 API 都在後端 `http://localhost:8000`

### POST /validate
驗證 YAML 內容

```json
Request:
{
  "content": "rules:\n  - name: \"Test\"\n    type: \"net_cap_to_gnd\"\n    net: \"Vcc\"\n    value: \"0.1uF\""
}

Response:
{
  "valid": true,
  "rules_count": 1,
  "rules": [...],
  "errors": []
}
```

### POST /parse
解析上傳的 YAML 檔案

```
Request:
  Content-Type: multipart/form-data
  file: rules.yaml

Response:
{
  "filename": "rules.yaml",
  "valid": true,
  "rules_count": 1,
  "rules": [...],
  "errors": []
}
```

### POST /generate
從規則列表生成 YAML

```json
Request:
[
  {
    "name": "Vcc cap",
    "type": "net_cap_to_gnd",
    "net": "Vcc",
    "value": "0.1uF",
    "tolerance": "10%"
  }
]

Response:
{
  "valid": true,
  "yaml": "rules:\n- name: Vcc cap\n  type: net_cap_to_gnd\n  net: Vcc\n  value: 0.1uF\n  tolerance: 10%\n",
  "filename": "rules_20240314_120530.yaml"
}
```

### GET /templates
取得規則模板

```json
Response:
{
  "net_cap_to_gnd": {
    "name": "電容到 GND",
    "description": "驗證指定 net 上必須有電容接到 GND",
    "template": {
      "name": "Vcc 必須接 0.1uF 到 GND",
      "type": "net_cap_to_gnd",
      "net": "Vcc",
      "value": "0.1uF",
      "tolerance": "10%"
    }
  },
  ...
}
```

### GET /examples
取得完整規則範例

```json
Response:
{
  "yaml": "rules:\n- name: Vcc 必須接 0.1uF 到 GND\n  ...",
  "rules": [...]
}
```

### GET /health
健康檢查

```json
Response:
{
  "status": "ok",
  "timestamp": "2024-03-14T12:05:30.123456"
}
```

## 開發技巧

### 熱重載

- **前端**：修改 `.tsx` 或 `.css` 檔案自動重新載入
- **後端**：使用 `npm run api:dev` 啟用 `--reload` 自動重啟

### 調試

#### 前端（React DevTools）
```bash
# 安裝 React DevTools 瀏覽器擴展
# Chrome: https://chrome.google.com/webstore/...
# 在開發者工具中查看組件樹和狀態
```

#### 後端（FastAPI 文檔）
```
http://localhost:8000/docs      # Swagger UI
http://localhost:8000/redoc     # ReDoc
```

### 測試 API

使用 `curl`：
```bash
# 驗證 YAML
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"content":"rules:\n  - name: \"Test\"\n    type: \"net_cap_to_gnd\"\n    net: \"Vcc\"\n    value: \"0.1uF\""}'

# 取得範本
curl http://localhost:8000/templates

# 上傳檔案
curl -X POST http://localhost:8000/parse \
  -F "file=@rules.yaml"
```

## 生產部署

### 使用 Docker

#### 構建生產鏡像
```bash
# 多階段構建：優化大小
docker build -t circuit-checker-ui:latest .
```

#### 運行生產容器
```bash
docker run -p 8000:8000 circuit-checker-ui:latest
```

#### 上傳到鏡像倉庫
```bash
docker tag circuit-checker-ui:latest your-registry.com/circuit-checker-ui:latest
docker push your-registry.com/circuit-checker-ui:latest
```

### OpenShift 部署

#### 1. 建立 ImageStream 和 BuildConfig
```bash
oc new-build \
  --name=circuit-checker-ui \
  --image-stream=python:3.10 \
  --source=git \
  --source-secret=github-secret \
  https://your-repo.git

oc start-build circuit-checker-ui
```

#### 2. 建立 DeploymentConfig
```bash
oc new-app \
  --image-stream=circuit-checker-ui:latest \
  --name=circuit-checker-ui \
  -e ENVIRONMENT=production
```

#### 3. 暴露服務
```bash
oc expose svc/circuit-checker-ui
oc get routes
```

#### 4. 配置資源限制
```yaml
resources:
  limits:
    memory: 512Mi
    cpu: 250m
  requests:
    memory: 256Mi
    cpu: 100m
```

## 環境變數配置

### 開發環境 (`.env.local`)
```
VITE_API_URL=http://localhost:8000
VITE_DEBUG=true
```

### 生產環境
```
VITE_API_URL=https://api.production.com
VITE_DEBUG=false
```

## 常見問題

### Q1: 依賴安裝失敗？
**A:** 嘗試清除緩存
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Q2: 後端連接失敗？
**A:** 確認後端正在運行
```bash
curl http://localhost:8000/health
```

### Q3: YAML 驗證總是失敗？
**A:** 檢查：
1. 規則類型是否正確（`net_cap_to_gnd` 等）
2. 必填欄位是否完整
3. 縮進是否正確（YAML 對空格敏感）
4. 查看詳細錯誤信息

### Q4: 如何修改驗證規則？
**A:** 編輯 `api/main.py` 中的 `validate_rule()` 函數

### Q5: 可以新增新的規則類型嗎？
**A:** 可以，按照以下步驟：
1. 在後端驗證函數中新增邏輯
2. 在前端 `RuleForm.tsx` 中新增表單欄位
3. 在 `/templates` 中新增範本
4. 更新文檔

## 效能優化

### 前端
- 使用 Vite 的快速冷啟動（<100ms）
- Tree shaking 自動移除未使用代碼
- 代碼分割實現按需載入

### 後端
- FastAPI 自動生成 OpenAPI 文檔
- YAML 解析使用流式處理（大檔案支持）
- CORS 中間件已配置

### 構建
- 前端：~200KB（gzipped）
- 後端：~100MB（包括 Python 環境）

## 後續改進計畫

- [ ] 規則版本控制
- [ ] 協作編輯（WebSocket）
- [ ] 雲同步
- [ ] 複雜規則編程介面
- [ ] 與 CI/CD 的直接整合
- [ ] 規則範本社區庫
- [ ] 多語言支持

## 取得幫助

1. **查看 DEMO.md** - 完整功能演示
2. **查看 README.md** - 詳細文檔
3. **檢查 FastAPI 文檔** - http://localhost:8000/docs
4. **查看源碼** - 代碼註解詳細解釋

## 聯絡方式

如有問題或建議，請提交 Issue 或 PR。
