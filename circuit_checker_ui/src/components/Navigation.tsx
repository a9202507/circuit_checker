import React from 'react'

type Tab = 'editor' | 'builder' | 'guide'

interface NavigationProps {
  activeTab: Tab
  setActiveTab: (tab: Tab) => void
}

function Navigation({ activeTab, setActiveTab }: NavigationProps) {
  const tabs = [
    { id: 'editor' as Tab, label: '📝 YAML 編輯器', icon: '✎' },
    { id: 'builder' as Tab, label: '🔨 規則構建器', icon: '⚙' },
    { id: 'guide' as Tab, label: '📚 新手指南', icon: '?' },
  ]

  return (
    <nav className="bg-white shadow-md border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <span className="text-2xl">⚡</span>
            <h1 className="text-xl font-bold text-gray-900">Circuit Checker Rules Manager</h1>
          </div>
        </div>

        <div className="flex gap-4 border-t border-gray-200">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 font-medium transition-colors border-b-2 ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 bg-blue-50'
                  : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
    </nav>
  )
}

export default Navigation
