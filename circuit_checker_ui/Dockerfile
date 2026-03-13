# 多階段構建：前端
FROM node:18-alpine as frontend-builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build


# 最終階段：後端 + 靜態檔案
FROM python:3.10-slim

WORKDIR /app

# 安裝依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    pyyaml==6.0.1 \
    python-multipart==0.0.6

# 複製後端應用
COPY api ./api

# 複製前端靜態檔案
COPY --from=frontend-builder /app/dist ./static

# 修改 FastAPI 以提供靜態檔案
COPY api/main_with_static.py ./api/main.py

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
