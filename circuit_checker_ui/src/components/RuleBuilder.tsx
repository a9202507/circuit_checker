import React, { useState, useEffect } from 'react'
import { generateYaml, getTemplates } from '../api/client'
import RuleForm from './RuleForm'

interface RuleBuilderProps {
  rules: any[]
  setRules: (rules: any[]) => void
  setYamlContent: (content: string) => void
}

function RuleBuilder({ rules, setRules, setYamlContent }: RuleBuilderProps) {
  const [templates, setTemplates] = useState<any>({})
  const [selectedType, setSelectedType] = useState('net_cap_to_gnd')
  const [successMessage, setSuccessMessage] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)

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

  const handleAddRule = () => {
    const template = templates[selectedType]?.template
    if (!template) return

    const newRule = { ...template, name: template.name + ` (複製 ${rules.length + 1})` }
    setRules([...rules, newRule])
    setSuccessMessage('✓ 規則已新增')
    setTimeout(() => setSuccessMessage(''), 2000)
  }

  const handleUpdateRule = (index: number, updatedRule: any) => {
    const newRules = [...rules]
    newRules[index] = updatedRule
    setRules(newRules)
  }

  const handleDeleteRule = (index: number) => {
    if (confirm('確定要刪除此規則嗎？')) {
      const newRules = rules.filter((_, i) => i !== index)
      setRules(newRules)
      setSuccessMessage('✓ 規則已刪除')
      setTimeout(() => setSuccessMessage(''), 2000)
    }
  }

  const handleGenerateYaml = async () => {
    if (rules.length === 0) {
      alert('請先新增至少一條規則')
      return
    }

    setIsGenerating(true)
    try {
      const result = await generateYaml(rules)
      setYamlContent(result.yaml)
      setSuccessMessage(`✓ YAML 已生成！共 ${rules.length} 條規則`)
      setTimeout(() => setSuccessMessage(''), 2000)
    } catch (error) {
      alert('生成失敗: ' + error)
    } finally {
      setIsGenerating(false)
    }
  }

  const ruleTypeOptions = Object.entries(templates).map(([key, value]: [string, any]) => ({
    key,
    name: value.name,
    description: value.description,
  }))

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
      {/* 左側：模板選擇 */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 h-fit">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔧 規則類型</h3>
        <div className="space-y-2 mb-6">
          {ruleTypeOptions.map((option) => (
            <button
              key={option.key}
              onClick={() => setSelectedType(option.key)}
              className={`w-full text-left p-3 rounded-lg border-2 transition-colors ${
                selectedType === option.key
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <div className="font-medium text-gray-900">{option.name}</div>
              <div className="text-xs text-gray-600 mt-1">{option.description}</div>
            </button>
          ))}
        </div>

        <button
          onClick={handleAddRule}
          className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
        >
          ➕ 新增規則
        </button>
      </div>

      {/* 右側：規則列表 */}
      <div className="lg:col-span-3">
        {successMessage && (
          <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-800 rounded-lg">
            {successMessage}
          </div>
        )}

        {rules.length === 0 ? (
          <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <span className="text-4xl mb-2 block">📝</span>
            <p className="text-gray-600">還沒有規則，左邊選擇類型後點擊「新增規則」</p>
          </div>
        ) : (
          <div className="space-y-4">
            {rules.map((rule, index) => (
              <div
                key={index}
                className="bg-white rounded-lg shadow-md border border-gray-200 p-6"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900">規則 {index + 1}</h4>
                    <p className="text-sm text-gray-600">{rule.name}</p>
                  </div>
                  <button
                    onClick={() => handleDeleteRule(index)}
                    className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors text-sm"
                  >
                    🗑️ 刪除
                  </button>
                </div>

                <RuleForm
                  rule={rule}
                  onUpdate={(updatedRule) => handleUpdateRule(index, updatedRule)}
                />
              </div>
            ))}

            <div className="flex gap-2 mt-6">
              <button
                onClick={handleGenerateYaml}
                disabled={isGenerating}
                className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors font-medium"
              >
                {isGenerating ? '生成中...' : '✓ 生成 YAML'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default RuleBuilder
