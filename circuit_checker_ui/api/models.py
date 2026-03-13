"""
資料模型定義
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class Rule(BaseModel):
    """單個規則"""
    name: str
    type: str
    # 可選欄位
    net: Optional[str] = None
    value: Optional[str] = None
    tolerance: Optional[str] = None
    pin: Optional[str] = None
    pin1: Optional[str] = None
    pin2: Optional[str] = None
    pins: Optional[List[str]] = None

    class Config:
        extra = "allow"  # 允許額外欄位


class RulesYaml(BaseModel):
    """rules.yaml 檔案結構"""
    rules: List[Rule]


class ValidationResult(BaseModel):
    """驗證結果"""
    valid: bool
    rules_count: int
    rules: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]


class YamlGenerationResult(BaseModel):
    """YAML 生成結果"""
    valid: bool
    yaml: str
    filename: str
