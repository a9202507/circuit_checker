import React, { useState, useRef } from 'react'
import { validateYaml, parseYamlFile, generateYaml } from '../api/client'

interface YamlEditorProps {
  yamlContent: string
  setYamlContent: (content: string) => void
  setValidationErrors: (errors: any[]) => void
  setIsValid: (valid: boolean) => void
  setRules: (rules: any[]) => void
  isValid: boolean
}

function YamlEditor({
  yamlContent,
  setYamlContent,
  setValidationErrors,
  setIsValid,
  setRules,
  isValid,
}: YamlEditorProps) {
  const [isValidating, setIsValidating] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleValidate = async () => {
    if (!yamlContent.trim()) {
      setValidationErrors([{ message: '請先輸入或上傳 YAML 內容' }])
      return
    }

    setIsValidating(true)
    try {
      const result = await validateYaml(yamlContent)
      setValidationErrors(result.errors)
      setIsValid(result.valid)
      setRules(result.rules)
      if (result.valid) {
        setSuccessMessage(`✓ YAML 有效！找到 ${result.rules_count} 條規則`)
        setTimeout(() => setSuccessMessage(''), 3000)
      }
    } catch (error) {
      setValidationErrors([{ message: `驗證失敗: ${error}` }])
      setIsValid(false)
    } finally {
      setIsValidating(false)
    }
  }

  const handleFileImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsValidating(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const result = await parseYamlFile(formData)

      if (result.raw_content) {
        setYamlContent(result.raw_content)
      }
      setValidationErrors(result.errors)
      setIsValid(result.valid)
      setRules(result.rules)

      if (result.valid) {
        setSuccessMessage(`✓ 檔案 '${file.name}' 匯入成功！`)
        setTimeout(() => setSuccessMessage(''), 3000)
      }
    } catch (error) {
      setValidationErrors([{ message: `匯入失敗: ${error}` }])
    } finally {
      setIsValidating(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleExportYaml = () => {
    if (!isValid || !yamlContent.trim()) {
      alert('請先驗證有效的 YAML')
      return
    }

    const element = document.createElement('a')
    element.setAttribute(
      'href',
      'data:text/plain;charset=utf-8,' + encodeURIComponent(yamlContent)
    )
    element.setAttribute('download', 'rules.yaml')
    element.style.display = 'none'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)

    setSuccessMessage('✓ YAML 檔案已下載')
    setTimeout(() => setSuccessMessage(''), 3000)
  }

  const handleLoadExample = async () => {
    setIsValidating(true)
    try {
      const response = await fetch('/api/examples')
      const data = await response.json()
      setYamlContent(data.yaml)
      setSuccessMessage('✓ 範例已載入，請點擊「驗證」確認')
      setTimeout(() => setSuccessMessage(''), 3000)
    } catch (error) {
      setValidationErrors([{ message: `載入範例失敗: ${error}` }])
    } finally {
      setIsValidating(false)
    }
  }

  const handleClear = () => {
    if (confirm('確定要清空內容嗎？')) {
      setYamlContent('')
      setValidationErrors([])
      setIsValid(false)
      setRules([])
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
      {/* 編輯區 */}
      <div className="lg:col-span-2">
        <div className="bg-white rounded-lg shadow-md border border-gray-200">
          <div className="border-b border-gray-200 p-4 flex justify-between items-center">
            <h2 className="text-lg font-semibold text-gray-900">YAML 內容</h2>
            {isValid && (
              <span className="text-sm text-green-600 font-medium">✓ 有效</span>
            )}
          </div>

          <textarea
            value={yamlContent}
            onChange={(e) => setYamlContent(e.target.value)}
            placeholder="貼上 YAML 內容或使用下面的按鈕匯入檔案..."
            className="w-full h-96 p-4 font-mono text-sm resize-none border-0 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          <div className="bg-gray-50 border-t border-gray-200 p-4 flex gap-2 flex-wrap">
            <button
              onClick={handleValidate}
              disabled={isValidating}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors font-medium"
            >
              {isValidating ? '驗證中...' : '✓ 驗證'}
            </button>

            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
            >
              📤 匯入 YAML
            </button>

            <input
              ref={fileInputRef}
              type="file"
              accept=".yaml,.yml"
              onChange={handleFileImport}
              className="hidden"
            />

            <button
              onClick={handleExportYaml}
              disabled={!isValid}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 transition-colors font-medium"
            >
              📥 匯出 YAML
            </button>

            <button
              onClick={handleLoadExample}
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors font-medium"
            >
              📋 載入範例
            </button>

            <button
              onClick={handleClear}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
            >
              🗑️ 清空
            </button>
          </div>
        </div>

        {successMessage && (
          <div className="mt-4 p-4 bg-green-100 border border-green-400 text-green-800 rounded-lg">
            {successMessage}
          </div>
        )}
      </div>

      {/* 提示區 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-4">💡 提示</h3>
        <ul className="space-y-3 text-sm text-blue-800">
          <li>✓ 使用左邊的編輯器輸入或貼上 YAML 內容</li>
          <li>✓ 點擊「驗證」檢查語法是否正確</li>
          <li>✓ 點擊「匯入 YAML」上傳本地檔案</li>
          <li>✓ 點擊「匯出 YAML」下載驗證後的檔案</li>
          <li>✓ 不確定怎麼寫？點擊「載入範例」查看</li>
          <li>✓ 想用表單建立？切換到「規則構建器」標籤</li>
        </ul>

        <div className="mt-6 pt-6 border-t border-blue-200">
          <h4 className="font-semibold text-blue-900 mb-2">📝 YAML 結構</h4>
          <pre className="text-xs bg-white p-3 rounded border border-blue-300 overflow-x-auto">
{`rules:
  - name: "規則名稱"
    type: "規則類型"
    # 根據類型添加相應欄位
    # 查看「新手指南」瞭解更多`}
          </pre>
        </div>
      </div>
    </div>
  )
}

export default YamlEditor
