import React, { useState, useEffect } from 'react'
import { getTemplates } from '../api/client'

interface BeginnerGuideProps {
  onSelectTemplate: (template: any) => void
}

function BeginnerGuide({ onSelectTemplate }: BeginnerGuideProps) {
  const [templates, setTemplates] = useState<any>({})

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    try {
      const data = await getTemplates()
      setTemplates(data)
    } catch (error) {
      console.error('載入模板失敗:', error)
    }
  }

  const guideSteps = [
    {
      number: 1,
      title: '了解規則類型',
      description: 'circuit-checker 支持 4 種規則類型，每種都用於檢查不同的電路設計約束。',
    },
    {
      number: 2,
      title: '選擇規則類型',
      description: '根據你的需求選擇合適的規則類型，查看下面的詳細說明。',
    },
    {
      number: 3,
      title: '配置規則參數',
      description: '為選中的規則類型填入必要的參數（如 Net 名稱、Pin 號等）。',
    },
    {
      number: 4,
      title: '驗證 YAML',
      description: '使用「YAML 編輯器」標籤驗證生成的規則，確保語法正確。',
    },
  ]

  return (
    <div className="space-y-12">
      {/* 快速開始 */}
      <section className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-8 border border-blue-200">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">🚀 快速開始</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {guideSteps.map((step) => (
            <div key={step.number} className="bg-white rounded-lg p-4 border border-gray-200">
              <div className="w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold mb-3">
                {step.number}
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{step.title}</h3>
              <p className="text-sm text-gray-600">{step.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 規則類型詳解 */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">📚 規則類型詳解</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Object.entries(templates).map(([key, template]: [string, any]) => (
            <div key={key} className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{template.name}</h3>
              <p className="text-gray-600 mb-4">{template.description}</p>

              {/* 參數說明 */}
              <div className="bg-gray-50 rounded p-4 mb-4">
                <h4 className="font-medium text-gray-900 mb-3">📋 參數說明</h4>
                {key === 'net_cap_to_gnd' && (
                  <ul className="space-y-2 text-sm text-gray-700">
                    <li><strong>name:</strong> 規則名稱（自訂）</li>
                    <li><strong>net:</strong> 要檢查的 Net 名稱（如：Vcc、DVDD）</li>
                    <li><strong>value:</strong> 期望的電容值（如：0.1uF、100nF）</li>
                    <li><strong>tolerance:</strong> 容差範圍（如：10%、20%，可選）</li>
                  </ul>
                )}
                {key === 'pin_floating' && (
                  <ul className="space-y-2 text-sm text-gray-700">
                    <li><strong>name:</strong> 規則名稱</li>
                    <li><strong>pins:</strong> Pin 列表（格式：REFDES.PIN，如：U1.PWM）</li>
                  </ul>
                )}
                {key === 'pin_to_pin_resistor' && (
                  <ul className="space-y-2 text-sm text-gray-700">
                    <li><strong>name:</strong> 規則名稱</li>
                    <li><strong>pin1:</strong> 第一個 Pin（格式：REFDES.PIN）</li>
                    <li><strong>pin2:</strong> 第二個 Pin（格式：REFDES.PIN）</li>
                    <li><strong>value:</strong> 期望的電阻值（如：1、10k、4.7M）</li>
                    <li><strong>tolerance:</strong> 容差範圍（可選）</li>
                  </ul>
                )}
                {key === 'pin_cap_to_gnd' && (
                  <ul className="space-y-2 text-sm text-gray-700">
                    <li><strong>name:</strong> 規則名稱</li>
                    <li><strong>pins:</strong> Pin 列表（格式：REFDES.PIN）</li>
                    <li><strong>value:</strong> 期望的電容值</li>
                    <li><strong>tolerance:</strong> 容差範圍（可選）</li>
                  </ul>
                )}
              </div>

              {/* 範例 */}
              <div className="mb-4">
                <h4 className="font-medium text-gray-900 mb-2">💡 範例</h4>
                <pre className="bg-gray-900 text-gray-100 p-3 rounded text-xs overflow-x-auto">
                  {`name: "${template.template.name}"
type: "${template.template.type}"
${
  template.template.net ? `net: "${template.template.net}"\nvalue: "${template.template.value}"` :
  template.template.pin1 ? `pin1: "${template.template.pin1}"\npin2: "${template.template.pin2}"\nvalue: "${template.template.value}"` :
  template.template.pins ? `pins:\n${template.template.pins.map((p: string) => `  - "${p}"`).join('\n')}\nvalue: "${template.template.value}"` :
  ''
}`}
                </pre>
              </div>

              <button
                onClick={() => onSelectTemplate(template.template)}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                用此類型建立規則
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* 常見問題 */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">❓ 常見問題</h2>
        <div className="space-y-4">
          <details className="bg-white rounded-lg border border-gray-200 p-6">
            <summary className="font-semibold text-gray-900 cursor-pointer hover:text-blue-600">
              Pin 格式是什麼？
            </summary>
            <p className="text-gray-600 mt-3">
              Pin 格式為 <code className="bg-gray-100 px-2 py-1 rounded">REFDES.PIN</code>，其中 REFDES 是元件標識符（如 U1、C1），PIN 是 Pin 名稱或編號（如 VDD、PWM、1）。
            </p>
          </details>

          <details className="bg-white rounded-lg border border-gray-200 p-6">
            <summary className="font-semibold text-gray-900 cursor-pointer hover:text-blue-600">
              GND 包括哪些 Net？
            </summary>
            <p className="text-gray-600 mt-3">
              規則檢查器會自動識別以下 GND 變體：GND、AGND（模擬地）、PGND（電源地）以及帶數字後綴的 GND（如 GND2、AGND1）。
            </p>
          </details>

          <details className="bg-white rounded-lg border border-gray-200 p-6">
            <summary className="font-semibold text-gray-900 cursor-pointer hover:text-blue-600">
              數值單位支持哪些？
            </summary>
            <p className="text-gray-600 mt-3">
              容值：pF、nF、uF、mF（如 0.1uF、100nF）。電阻值：Ω/R、k、M、G（如 1k、4.7M）。系統會自動進行單位轉換和容差計算。
            </p>
          </details>

          <details className="bg-white rounded-lg border border-gray-200 p-6">
            <summary className="font-semibold text-gray-900 cursor-pointer hover:text-blue-600">
              如何驗證我的規則？
            </summary>
            <p className="text-gray-600 mt-3">
              1. 在「規則構建器」中建立規則 2. 點擊「生成 YAML」 3. 切換到「YAML 編輯器」 4. 點擊「驗證」檢查語法 5. 修復任何錯誤並重複步驟 4-5 直到驗證通過
            </p>
          </details>
        </div>
      </section>

      {/* 最佳實踐 */}
      <section className="bg-green-50 border border-green-200 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">✅ 最佳實踐</h2>
        <div className="space-y-4">
          <div className="flex gap-4">
            <span className="text-2xl">✓</span>
            <div>
              <h4 className="font-semibold text-gray-900">使用描述性的規則名稱</h4>
              <p className="text-gray-600">好的名稱幫助其他人理解規則的目的</p>
            </div>
          </div>
          <div className="flex gap-4">
            <span className="text-2xl">✓</span>
            <div>
              <h4 className="font-semibold text-gray-900">設置合理的容差範圍</h4>
              <p className="text-gray-600">考慮元件的實際容差等級（如常見的 10%、20%）</p>
            </div>
          </div>
          <div className="flex gap-4">
            <span className="text-2xl">✓</span>
            <div>
              <h4 className="font-semibold text-gray-900">分組相關規則</h4>
              <p className="text-gray-600">相同 IC 或功能塊的規則放在一起便於維護</p>
            </div>
          </div>
          <div className="flex gap-4">
            <span className="text-2xl">✓</span>
            <div>
              <h4 className="font-semibold text-gray-900">定期驗證規則集</h4>
              <p className="text-gray-600">在設計變更後重新驗證以確保規則仍然適用</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default BeginnerGuide
