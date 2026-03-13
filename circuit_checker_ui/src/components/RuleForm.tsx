import React from 'react'

interface RuleFormProps {
  rule: any
  onUpdate: (rule: any) => void
}

function RuleForm({ rule, onUpdate }: RuleFormProps) {
  const handleChange = (key: string, value: any) => {
    onUpdate({ ...rule, [key]: value })
  }

  const handleArrayChange = (key: string, arrayValue: string) => {
    const arr = arrayValue.split('\n').map(s => s.trim()).filter(s => s)
    onUpdate({ ...rule, [key]: arr })
  }

  const renderFields = () => {
    const type = rule.type

    const commonFields = (
      <>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">規則名稱 *</label>
          <input
            type="text"
            value={rule.name || ''}
            onChange={(e) => handleChange('name', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="例如：Vcc 必須接 0.1uF 到 GND"
          />
        </div>
      </>
    )

    if (type === 'net_cap_to_gnd') {
      return (
        <>
          {commonFields}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Net 名稱 *</label>
            <input
              type="text"
              value={rule.net || ''}
              onChange={(e) => handleChange('net', e.target.value)}
              placeholder="例如：Vcc"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">電容值 *</label>
            <input
              type="text"
              value={rule.value || ''}
              onChange={(e) => handleChange('value', e.target.value)}
              placeholder="例如：0.1uF"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">容差</label>
            <input
              type="text"
              value={rule.tolerance || ''}
              onChange={(e) => handleChange('tolerance', e.target.value)}
              placeholder="例如：10%"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </>
      )
    }

    if (type === 'pin_floating') {
      return (
        <>
          {commonFields}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Pins（每行一個） *</label>
            <textarea
              value={(rule.pins || []).join('\n')}
              onChange={(e) => handleArrayChange('pins', e.target.value)}
              placeholder="U1.PWM&#10;U2.PWM"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm h-24"
            />
          </div>
        </>
      )
    }

    if (type === 'pin_to_pin_resistor') {
      return (
        <>
          {commonFields}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Pin 1 *</label>
            <input
              type="text"
              value={rule.pin1 || ''}
              onChange={(e) => handleChange('pin1', e.target.value)}
              placeholder="例如：U1.VDD"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Pin 2 *</label>
            <input
              type="text"
              value={rule.pin2 || ''}
              onChange={(e) => handleChange('pin2', e.target.value)}
              placeholder="例如：U1.VDRV"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">電阻值 *</label>
            <input
              type="text"
              value={rule.value || ''}
              onChange={(e) => handleChange('value', e.target.value)}
              placeholder="例如：1"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">容差</label>
            <input
              type="text"
              value={rule.tolerance || ''}
              onChange={(e) => handleChange('tolerance', e.target.value)}
              placeholder="例如：20%"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </>
      )
    }

    if (type === 'pin_cap_to_gnd') {
      return (
        <>
          {commonFields}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Pins（每行一個） *</label>
            <textarea
              value={(rule.pins || []).join('\n')}
              onChange={(e) => handleArrayChange('pins', e.target.value)}
              placeholder="U1.VDD&#10;U1.VDRV"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm h-24"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">電容值 *</label>
            <input
              type="text"
              value={rule.value || ''}
              onChange={(e) => handleChange('value', e.target.value)}
              placeholder="例如：0.1uF"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">容差</label>
            <input
              type="text"
              value={rule.tolerance || ''}
              onChange={(e) => handleChange('tolerance', e.target.value)}
              placeholder="例如：20%"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </>
      )
    }

    return commonFields
  }

  return (
    <div className="space-y-4">
      {renderFields()}
    </div>
  )
}

export default RuleForm
