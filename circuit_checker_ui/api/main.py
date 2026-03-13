"""
Circuit Checker Rules UI Backend
FastAPI 服務，提供 YAML 驗證、解析、轉換等功能。
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yaml
from typing import Any, Dict, List, Optional
import io
from datetime import datetime
import json

app = FastAPI(title="Circuit Checker Rules UI API")

# 啟用 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 資料模型 ────────────────────────────────────────────────────────────────


class ValidationError:
    """驗證錯誤訊息"""
    def __init__(self, field: str, message: str, line: Optional[int] = None):
        self.field = field
        self.message = message
        self.line = line

    def dict(self):
        return {
            "field": self.field,
            "message": self.message,
            "line": self.line,
        }


# ── YAML 驗證邏輯 ────────────────────────────────────────────────────────────


def validate_rule(rule: Dict[str, Any], index: int) -> List[ValidationError]:
    """驗證單個規則"""
    errors = []

    # 檢查必填欄位
    if "name" not in rule:
        errors.append(ValidationError("name", f"Rule {index}: 缺少必填欄位 'name'"))
    elif not isinstance(rule["name"], str) or not rule["name"].strip():
        errors.append(ValidationError("name", f"Rule {index}: 'name' 必須是非空字串"))

    if "type" not in rule:
        errors.append(ValidationError("type", f"Rule {index}: 缺少必填欄位 'type'"))
    else:
        rule_type = rule["type"]
        valid_types = ["net_cap_to_gnd", "pin_floating", "pin_to_pin_resistor", "pin_cap_to_gnd"]
        if rule_type not in valid_types:
            errors.append(ValidationError(
                "type",
                f"Rule {index}: 無效的規則類型 '{rule_type}'。有效值：{', '.join(valid_types)}"
            ))

    # 根據規則類型檢查必填欄位
    rule_type = rule.get("type")
    if rule_type == "net_cap_to_gnd":
        if "net" not in rule:
            errors.append(ValidationError("net", f"Rule {index}: net_cap_to_gnd 需要 'net' 欄位"))
        if "value" not in rule:
            errors.append(ValidationError("value", f"Rule {index}: net_cap_to_gnd 需要 'value' 欄位"))

    elif rule_type == "pin_floating":
        if "pins" not in rule:
            errors.append(ValidationError("pins", f"Rule {index}: pin_floating 需要 'pins' 欄位"))
        elif not isinstance(rule["pins"], list) or len(rule["pins"]) == 0:
            errors.append(ValidationError("pins", f"Rule {index}: 'pins' 必須是非空列表"))
        else:
            for pin in rule["pins"]:
                if not isinstance(pin, str) or "." not in pin:
                    errors.append(ValidationError(
                        "pins",
                        f"Rule {index}: pin 格式必須為 'REFDES.PIN'，例如 'U1.PWM'"
                    ))

    elif rule_type == "pin_to_pin_resistor":
        if "pin1" not in rule:
            errors.append(ValidationError("pin1", f"Rule {index}: pin_to_pin_resistor 需要 'pin1' 欄位"))
        else:
            if not isinstance(rule["pin1"], str) or "." not in rule["pin1"]:
                errors.append(ValidationError("pin1", f"Rule {index}: pin1 格式必須為 'REFDES.PIN'"))
        if "pin2" not in rule:
            errors.append(ValidationError("pin2", f"Rule {index}: pin_to_pin_resistor 需要 'pin2' 欄位"))
        else:
            if not isinstance(rule["pin2"], str) or "." not in rule["pin2"]:
                errors.append(ValidationError("pin2", f"Rule {index}: pin2 格式必須為 'REFDES.PIN'"))
        if "value" not in rule:
            errors.append(ValidationError("value", f"Rule {index}: pin_to_pin_resistor 需要 'value' 欄位"))

    elif rule_type == "pin_cap_to_gnd":
        if "pins" not in rule:
            errors.append(ValidationError("pins", f"Rule {index}: pin_cap_to_gnd 需要 'pins' 欄位"))
        elif not isinstance(rule["pins"], list) or len(rule["pins"]) == 0:
            errors.append(ValidationError("pins", f"Rule {index}: 'pins' 必須是非空列表"))
        if "value" not in rule:
            errors.append(ValidationError("value", f"Rule {index}: pin_cap_to_gnd 需要 'value' 欄位"))

    return errors


def validate_rules_yaml(content: str) -> tuple[bool, List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    驗證 rules.yaml 內容
    回傳 (is_valid, rules, errors)
    """
    errors = []

    # 1. 嘗試解析 YAML
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        errors.append({
            "field": "yaml_syntax",
            "message": f"YAML 語法錯誤：{str(e)}",
            "line": getattr(e, 'problem_mark', None).line if hasattr(e, 'problem_mark') else None,
        })
        return False, [], errors

    # 2. 檢查頂層結構
    if not isinstance(data, dict):
        errors.append({
            "field": "structure",
            "message": "根結構必須是字典（object），應包含 'rules' 鍵",
        })
        return False, [], errors

    if "rules" not in data:
        errors.append({
            "field": "rules",
            "message": "缺少必填鍵 'rules'",
        })
        return False, [], errors

    rules = data["rules"]
    if not isinstance(rules, list):
        errors.append({
            "field": "rules",
            "message": "'rules' 必須是列表",
        })
        return False, [], errors

    # 3. 驗證每個規則
    validated_rules = []
    for idx, rule in enumerate(rules):
        if not isinstance(rule, dict):
            errors.append({
                "field": f"rule_{idx}",
                "message": f"Rule {idx}: 必須是字典（object）",
            })
            continue

        rule_errors = validate_rule(rule, idx)
        for err in rule_errors:
            errors.append(err.dict())

        if not rule_errors:  # 僅添加有效規則
            validated_rules.append(rule)

    is_valid = len(errors) == 0
    return is_valid, validated_rules, errors


# ── API 端點 ────────────────────────────────────────────────────────────────


@app.get("/health")
async def health():
    """健康檢查"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.post("/validate")
async def validate_yaml(content: str):
    """驗證 YAML 內容"""
    is_valid, rules, errors = validate_rules_yaml(content)
    return {
        "valid": is_valid,
        "rules_count": len(rules),
        "rules": rules,
        "errors": errors,
    }


@app.post("/parse")
async def parse_yaml_file(file: UploadFile = File(...)):
    """解析上傳的 YAML 檔案"""
    try:
        content = await file.read()
        text = content.decode("utf-8")
        is_valid, rules, errors = validate_rules_yaml(text)

        return {
            "filename": file.filename,
            "valid": is_valid,
            "rules_count": len(rules),
            "rules": rules,
            "errors": errors,
            "raw_content": text if is_valid else None,
        }
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="檔案必須是 UTF-8 編碼")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate")
async def generate_yaml(rules_data: List[Dict[str, Any]]):
    """從規則列表生成 YAML"""
    output = {
        "rules": rules_data
    }

    try:
        yaml_content = yaml.dump(output, allow_unicode=True, default_flow_style=False, sort_keys=False)
        return {
            "valid": True,
            "yaml": yaml_content,
            "filename": f"rules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成 YAML 失敗：{str(e)}")


@app.get("/templates")
async def get_templates():
    """取得規則模板"""
    templates = {
        "net_cap_to_gnd": {
            "name": "電容到 GND",
            "description": "驗證指定 net 上必須有電容接到 GND",
            "template": {
                "name": "Vcc 必須接 0.1uF 到 GND",
                "type": "net_cap_to_gnd",
                "net": "Vcc",
                "value": "0.1uF",
                "tolerance": "10%",
            }
        },
        "pin_floating": {
            "name": "Pin Floating",
            "description": "驗證指定 pin 必須為 floating（不接任何 net）",
            "template": {
                "name": "PWM pin 必須 floating",
                "type": "pin_floating",
                "pins": ["U1.PWM", "U2.PWM"],
            }
        },
        "pin_to_pin_resistor": {
            "name": "Pin 之間的電阻",
            "description": "驗證兩個 pin 之間必須有指定阻值的電阻",
            "template": {
                "name": "VDD 與 VDRV 之間必須有 1Ω",
                "type": "pin_to_pin_resistor",
                "pin1": "U1.VDD",
                "pin2": "U1.VDRV",
                "value": "1",
                "tolerance": "20%",
            }
        },
        "pin_cap_to_gnd": {
            "name": "Pin 電容到 GND",
            "description": "驗證每個指定 pin 的 net 上必須有電容接到 GND",
            "template": {
                "name": "VDD / VDRV 各接 0.1uF 到 GND",
                "type": "pin_cap_to_gnd",
                "pins": ["U1.VDD", "U1.VDRV"],
                "value": "0.1uF",
                "tolerance": "20%",
            }
        }
    }
    return templates


@app.get("/examples")
async def get_examples():
    """取得完整規則範例"""
    example_rules = {
        "rules": [
            {
                "name": "Vcc 必須接 0.1uF 到 GND",
                "type": "net_cap_to_gnd",
                "net": "Vcc",
                "value": "0.1uF",
                "tolerance": "10%",
            },
            {
                "name": "PWM pins 必須 floating",
                "type": "pin_floating",
                "pins": ["U1.PWM", "U2.PWM"],
            },
            {
                "name": "VDD 與 VDRV 之間必須有 1Ω",
                "type": "pin_to_pin_resistor",
                "pin1": "U1.VDD",
                "pin2": "U1.VDRV",
                "value": "1",
                "tolerance": "20%",
            },
            {
                "name": "VDD / VDRV 各接 0.1uF 到 GND",
                "type": "pin_cap_to_gnd",
                "pins": ["U1.VDD", "U1.VDRV"],
                "value": "0.1uF",
                "tolerance": "20%",
            }
        ]
    }

    yaml_content = yaml.dump(example_rules, allow_unicode=True, default_flow_style=False, sort_keys=False)

    return {
        "yaml": yaml_content,
        "rules": example_rules["rules"],
    }
