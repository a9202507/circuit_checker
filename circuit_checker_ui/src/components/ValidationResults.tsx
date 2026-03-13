import React from 'react'

interface ValidationResultsProps {
  errors: any[]
  isValid: boolean
  rules: any[]
}

function ValidationResults({ errors, isValid, rules }: ValidationResultsProps) {
  return (
    <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* 驗證狀態 */}
      {isValid ? (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-start gap-4">
            <span className="text-4xl">✓</span>
            <div>
              <h3 className="text-lg font-semibold text-green-900">YAML 有效</h3>
              <p className="text-green-700 mt-1">找到 {rules.length} 條有效規則</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-start gap-4">
            <span className="text-4xl">✗</span>
            <div>
              <h3 className="text-lg font-semibold text-red-900">驗證失敗</h3>
              <p className="text-red-700 mt-1">找到 {errors.length} 個錯誤</p>
            </div>
          </div>
        </div>
      )}

      {/* 規則統計 */}
      {rules.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">📊 規則統計</h3>
          <div className="space-y-2 text-sm text-blue-800">
            {rules.map((rule, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <span className="inline-block w-6 h-6 bg-blue-600 text-white rounded-full text-center text-xs leading-6">
                  {idx + 1}
                </span>
                <span className="font-medium">{rule.name}</span>
                <span className="text-xs bg-blue-200 px-2 py-1 rounded">{rule.type}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 錯誤列表 */}
      {errors.length > 0 && (
        <div className="lg:col-span-2 bg-white border border-gray-200 rounded-lg">
          <div className="border-b border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-900">🔴 錯誤詳情</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {errors.map((error, idx) => (
              <div key={idx} className="p-4 bg-red-50">
                <div className="flex items-start gap-3">
                  <span className="text-red-600 font-bold">●</span>
                  <div className="flex-1">
                    <p className="font-mono text-sm text-red-800">
                      {error.field && <strong>[{error.field}]</strong>}
                      {' '}
                      {error.message}
                    </p>
                    {error.line && (
                      <p className="text-xs text-red-600 mt-1">第 {error.line + 1} 行</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ValidationResults
