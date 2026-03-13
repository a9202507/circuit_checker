"""
Circuit Checker Rules UI Backend with Static Files
生產版本：包含靜態文件服務
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import yaml
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

# 導入原始邏輯
from .main import (
    ValidationError, validate_rule, validate_rules_yaml,
    app as base_app
)

# 使用基礎應用的所有路由
app = base_app

# 提供靜態檔案（SPA）
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # SPA 回退：所有未知路由指向 index.html
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """SPA 回退路由"""
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"error": "Not found"}
