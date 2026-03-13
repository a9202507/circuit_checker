/**
 * API 客户端
 */

const API_BASE = '/api'

export async function validateYaml(content: string) {
  const response = await fetch(`${API_BASE}/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })
  if (!response.ok) throw new Error('驗證失敗')
  return response.json()
}

export async function parseYamlFile(formData: FormData) {
  const response = await fetch(`${API_BASE}/parse`, {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) throw new Error('解析失敗')
  return response.json()
}

export async function generateYaml(rules: any[]) {
  const response = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(rules),
  })
  if (!response.ok) throw new Error('生成失敗')
  return response.json()
}

export async function getTemplates() {
  const response = await fetch(`${API_BASE}/templates`)
  if (!response.ok) throw new Error('取得範本失敗')
  return response.json()
}

export async function getExamples() {
  const response = await fetch(`${API_BASE}/examples`)
  if (!response.ok) throw new Error('取得範例失敗')
  return response.json()
}
