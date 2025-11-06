// frontend/src/components/MermaidEditor.tsx
// 1.0.0

import type React from 'react'

// Props interface
interface MermaidEditorProps {
  code: string
  onChange: (newCode: string) => void
}

const MermaidEditor: React.FC<MermaidEditorProps> = ({ code, onChange }) => {
  const handleCodeChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(event.target.value)
  }

  return (
    <div className="w-full h-full">
      <textarea
        value={code}
        onChange={handleCodeChange}
        className="w-full h-full p-4 border border-gray-300 rounded-lg shadow-sm resize-none
                   font-mono text-sm bg-gray-50 focus:outline-none focus:ring-2
                   focus:ring-indigo-500 focus:border-indigo-500"
        placeholder="Saisissez ou collez votre code Mermaid ici..."
        rows={25}
        spellCheck="false"
        autoCapitalize="off"
        autoComplete="off"
        autoCorrect="off"
      />
    </div>
  )
}

export default MermaidEditor