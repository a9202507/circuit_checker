import React, { useState } from 'react'
import './App.css'
import YamlEditor from './components/YamlEditor'
import RuleBuilder from './components/RuleBuilder'
import ValidationResults from './components/ValidationResults'
import Navigation from './components/Navigation'
import BeginnerGuide from './components/BeginnerGuide'

type Tab = 'editor' | 'builder' | 'guide'

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('editor')
  const [yamlContent, setYamlContent] = useState('')
  const [validationErrors, setValidationErrors] = useState<any[]>([])
  const [isValid, setIsValid] = useState(false)
  const [rules, setRules] = useState<any[]>([])

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />

      <div className="container mx-auto px-4 py-8">
        {activeTab === 'editor' && (
          <YamlEditor
            yamlContent={yamlContent}
            setYamlContent={setYamlContent}
            setValidationErrors={setValidationErrors}
            setIsValid={setIsValid}
            setRules={setRules}
            isValid={isValid}
          />
        )}

        {activeTab === 'builder' && (
          <RuleBuilder
            rules={rules}
            setRules={setRules}
            setYamlContent={setYamlContent}
          />
        )}

        {activeTab === 'guide' && (
          <BeginnerGuide onSelectTemplate={(template) => {
            setActiveTab('builder')
            setRules([template])
          }} />
        )}

        {(validationErrors.length > 0 || (isValid && yamlContent)) && activeTab === 'editor' && (
          <ValidationResults errors={validationErrors} isValid={isValid} rules={rules} />
        )}
      </div>
    </div>
  )
}

export default App
