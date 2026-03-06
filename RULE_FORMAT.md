# Custom Rule File 格式說明

本文件說明如何撰寫 custom rule file 來檢查電路網表中的元件連接規則。

## 支援格式

系統格式：
- **YAML** - 更易讀，支援註解


---

## 檔案結構

### 基本結構

```yaml
version: "1.0.0"                    # 必須：規則檔案版本
description: "規則說明"              # 可選：整體說明

component_rules:                     # 必須：元件規則列表
  - Product family: "元件開發代號"    # 必須：元件開發代號 ex:McKinley
    part_number: "元件型號"          # 必須：元件型號
    package: "封裝類型"               # 可選：封裝資訊
    description: "元件說明"          # 可選：元件描述
    pin_count: 5                     # 必須：預期腳位總數
    
    pins:                            # 必須：腳位規則列表
      - pin_id: "1"                  # 必須：腳位編號
        pin_name: "VCC"              # 可選：腳位名稱
        required: true               # 可選：是否必須存在（預設 true）
        
        connection_rules:            # 可選：連接規則列表
          - rule_type: "規則類型"    # 必須：規則類型
            # ... 其他規則參數
```

---

## 規則類型 (rule_type)

### 1. `direct_connection` - 直接連接檢查

檢查腳位是否直接連接到指定的網路。

**參數：**
- `destination_net`: 精確網路名稱（如 `"GND"`）
- `destination_net_pattern`: 網路名稱 regex 模式（如 `"VCC.*|3P3.*"`）
- `destination_voltage`: 參考電壓值（資訊用途）

**範例：**

```yaml
- pin_id: "2"
  pin_name: GND
  connection_rules:
    - rule_type: direct_connection
      destination_net: GND
      description: "接地腳位必須連接到 GND"
```

```yaml
- pin_id: A5
  pin_name: VCC
  connection_rules:
    - rule_type: direct_connection
      destination_net_pattern: "VCC.*|3P3.*"
      destination_voltage: "3.3V"
      description: "VCC 必須連接到 3.3V 電源"
```

---

### 2. `decoupling_capacitor` - 去耦電容檢查

檢查腳位是否透過指定值的電容連接到地或其他網路。

**參數：**
- `component_type`: `"capacitor"` 
- `value`: 電容值（如 `"0.1uF"`）
- `tolerance_percent`: 容差百分比（如 `20` 表示 ±20%）
- `destination_net`: 目標網路（通常為 `"GND"`）
- `proximity`: 距離要求 - `"local"`（緊鄰）/ `"nearby"`（附近）/ `"any"`（任意）

**範例：**

```yaml
- pin_id: A5
  pin_name: VCC
  connection_rules:
    - rule_type: decoupling_capacitor
      component_type: capacitor
      value: "0.1uF"
      tolerance_percent: 20
      destination_net: GND
      proximity: local
      description: "VCC 需要 0.1uF 去耦電容到地"
```

---

### 3. `pull_up_resistor` - 上拉電阻檢查

檢查腳位是否透過電阻連接到電源。

**參數：**
- `component_type`: `"resistor"`
- `value`: 電阻值（如 `"4.7K"`、`"10K"`）
- `value_min` / `value_max`: 允許範圍
- `tolerance_percent`: 容差百分比
- `destination_net_pattern`: 目標電源網路模式
- `destination_voltage`: 目標電壓

**範例：**

```yaml
- pin_id: "4"
  pin_name: V+
  connection_rules:
    - rule_type: pull_up_resistor
      component_type: resistor
      value: "4.7K"
      tolerance_percent: 10
      destination_net_pattern: "3P3.*|VCC.*"
      destination_voltage: "3.3V"
      description: "V+ 需要 4.7KΩ 上拉電阻到 3.3V"
```

---

### 4. `pull_down_resistor` - 下拉電阻檢查

類似 `pull_up_resistor`，但目標為接地。

**範例：**

```yaml
- pin_id: EN
  connection_rules:
    - rule_type: pull_down_resistor
      component_type: resistor
      value: "10K"
      destination_net: GND
      description: "EN 需要下拉到地以預設關閉"
```

---

### 5. `series_resistor` / `series_capacitor` - 串聯元件檢查

檢查腳位是否透過串聯元件連接到另一網路。

**範例：**

```yaml
- pin_id: LED
  connection_rules:
    - rule_type: series_resistor
      component_type: resistor
      value_min: "220"
      value_max: "1K"
      description: "LED 需串聯限流電阻 220Ω-1KΩ"
```

---

### 6. `no_connection` - 無連接檢查

檢查腳位是否保持懸空（NC - No Connect）。

**範例：**

```yaml
- pin_id: "3"
  pin_name: NC
  connection_rules:
    - rule_type: no_connection
      description: "此腳位必須保持懸空"
```

---

## 進階功能

### 多條規則組合

單一腳位可同時定義多條規則，所有規則都必須滿足：

```yaml
- pin_id: VCC
  connection_rules:
    # 規則 1: 必須連接到 3.3V
    - rule_type: direct_connection
      destination_net_pattern: "3P3.*"
      
    # 規則 2: 必須有 0.1uF 去耦電容
    - rule_type: decoupling_capacitor
      component_type: capacitor
      value: "0.1uF"
      destination_net: GND
      
    # 規則 3: 建議有 10uF 大電容
    - rule_type: decoupling_capacitor
      component_type: capacitor
      value: "10uF"
      destination_net: GND
      proximity: nearby
```

---

### 元件值格式

支援的元件值格式：

**電容：**
- `"0.1uF"`, `"100nF"`, `"10pF"`, `"22uF"`

**電阻：**
- `"4.7K"`, `"10K"`, `"1M"`, `"220"`, `"100ohm"`

**電感：**
- `"10uH"`, `"1mH"`, `"100nH"`

單位符號：
- `p` = pico (10⁻¹²)
- `n` = nano (10⁻⁹)
- `u` = micro (10⁻⁶)
- `m` = milli (10⁻³)
- `K` = kilo (10³)
- `M` = mega (10⁶)

---

### 網路名稱 Regex 模式

使用 `destination_net_pattern` 可匹配多種命名變化：

```yaml
# 匹配 VCC_1, VCC_2, VCC_CORE 等
destination_net_pattern: "VCC.*"

# 匹配 3P3_1, 3.3V, 3V3 等
destination_net_pattern: "3P3.*|3\\.3V.*|3V3.*"

# 匹配 12VIN_1, 12VIN_2, 12V_INPUT 等
destination_net_pattern: "12VIN.*|12V.*"
```

---

## 完整範例

### 範例 1: TDM22545T 電源模組

```json
{
  "version": "1.0.0",
  "description": "TDM22545T dual-phase power module rules",
  "component_rules": [
    {
      "part_number": "TDM22545T",
      "product_family": "Power Management",
      "pin_count": 81,
      "pins": [
        {
          "pin_id": "A5",
          "pin_name": "VCC",
          "connection_rules": [
            {
              "rule_type": "direct_connection",
              "destination_net_pattern": "VCC.*|3P3.*",
              "destination_voltage": "3.3V"
            },
            {
              "rule_type": "decoupling_capacitor",
              "component_type": "capacitor",
              "value": "0.1uF",
              "tolerance_percent": 20,
              "destination_net": "GND"
            }
          ]
        }
      ]
    }
  ]
}
```

### 範例 2: 溫度感測器 LM26

詳見 [examples/power_module_rules.yaml](examples/power_module_rules.yaml)

---

## 檔案範例位置

本專案提供以下範例檔案：

1. **[power_module_rules.json](examples/power_module_rules.json)** / **[.yaml](examples/power_module_rules.yaml)**
   - TDM22545T 電源模組完整規則
   - LM26 溫度感測器規則
   - 通用 IC 去耦電容範本

2. **[simple_patterns.json](examples/simple_patterns.json)** / **[.yaml](examples/simple_patterns.yaml)**
   - 常見電路模式範本
   - 微控制器基本規則
   - 可重複使用的規則模式

---

## JSON Schema

完整的 JSON Schema 定義位於：
- [backend/schemas/custom_rule_schema.json](backend/schemas/custom_rule_schema.json)

可使用此 schema 驗證您的規則檔案格式是否正確。

---

## 使用流程

1. **建立規則檔案**：根據您的元件規格書，定義腳位連接規則
2. **選擇格式**：使用 JSON（程式友善）或 YAML（人類友善）
3. **驗證格式**：透過 API 端點 `/rules/validate` 驗證規則檔案
4. **執行檢查**：上傳網表與規則檔案，執行檢查
5. **查看報告**：系統回傳違反規則的詳細資訊

---

## 注意事項

### PADs vs Allegro 格式差異

- **PADs 格式**：
  - 腳位編號為數字或字母（`1`, `2`, `A5`, `B12`）
  - 無腳位名稱資訊
  - 無元件值資訊（僅 footprint）
  - 適合檢查：腳位數量、腳位存在性、連接拓樸

- **Allegro 格式**：
  - 腳位有編號和名稱（`pin 4` 名稱 `V+`）
  - part description 包含元件值（如 `0.1UF-0402`）
  - 適合檢查：完整規則包含元件值驗證

**建議**：若需檢查元件值（電阻、電容），優先使用 Allegro 格式網表。

---

## 常見問題

**Q: 如何處理一個腳位需要多個電容？**

A: 使用 `multiple_allowed: true` 和 `min_count` / `max_count`：

```yaml
- rule_type: decoupling_capacitor
  component_type: capacitor
  value: "0.1uF"
  destination_net: GND
  multiple_allowed: true
  min_count: 2
  max_count: 4
  description: "需要 2-4 個 0.1uF 電容"
```

**Q: 網路名稱不確定怎麼辦？**

A: 使用 regex pattern 匹配多種可能：

```yaml
destination_net_pattern: "VCC.*|VDD.*|3P3.*|3\\.3V.*"
```

**Q: pin_count 設為 0 是什麼意思？**

A: 表示這是通用規則範本，不檢查總腳位數，僅檢查列出的特定腳位。

---

## 下一步

- 查看 [examples/](examples/) 目錄中的完整範例
- 使用 [custom_rule_schema.json](backend/schemas/custom_rule_schema.json) 驗證您的規則
- 參考 [README.md](README.md) 了解整體系統架構
