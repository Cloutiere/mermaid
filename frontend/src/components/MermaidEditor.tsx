// frontend/src/components/MermaidEditor.tsx
// 1.0.2 (Correction de l'affichage des numéros de ligne)

import React, { useRef } from 'react'
import type { FC, ChangeEvent } from 'react'

// Props interface
interface MermaidEditorProps {
  code: string
  onChange: (newCode: string) => void
}

const MermaidEditor: React.FC<MermaidEditorProps> = ({ code, onChange }) => {
  // Refs pour la synchronisation
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const lineNumberRef = useRef<HTMLDivElement>(null)

  const handleCodeChange = (event: ChangeEvent<HTMLTextAreaElement>) => {
    onChange(event.target.value)
  }

  // Logique de défilement pour synchroniser les numéros de ligne
  const handleScroll = () => {
    if (textareaRef.current && lineNumberRef.current) {
      // Synchroniser le défilement vertical
      lineNumberRef.current.scrollTop = textareaRef.current.scrollTop
    }
  }

  // Calcul des numéros de ligne (dynamique pour correspondre au code)
  const lineCount = code.split('\n').length
  const lineNumbers = Array.from({ length: lineCount }, (_, i) => i + 1).join('\n')

  return (
    // Conteneur Flex pour aligner les numéros et la textarea, gérant la bordure et l'ombre.
    <div className="w-full h-full flex border border-gray-300 rounded-lg shadow-sm overflow-hidden bg-gray-50">

      {/* Colonne des Numéros de Ligne */}
      <div
        ref={lineNumberRef}
        // AJOUT: whitespace-pre-wrap pour que les '\n' soient interprétés comme des sauts de ligne.
        className="line-numbers w-12 bg-gray-100 text-gray-500 text-right pr-2 pt-4 font-mono text-sm select-none overflow-hidden whitespace-pre-wrap"
        style={{ lineHeight: '1.5rem' }} 
      >
        {lineNumbers}
      </div>

      {/* Zone de Texte Principale */}
      <textarea
        ref={textareaRef}
        value={code}
        onChange={handleCodeChange}
        onScroll={handleScroll}
        // flex-1 pour prendre l'espace horizontal restant.
        // pl-2 pour l'espace après les numéros de ligne.
        // border-none et outline-none pour ne pas doubler les styles du conteneur parent.
        className="flex-1 h-full p-4 pl-2 font-mono text-sm bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none leading-6 border-none outline-none"
        style={{ lineHeight: '1.5rem', border: 'none' }} 
        placeholder="Saisissez ou collez votre code Mermaid ici..."
        spellCheck="false"
        autoCapitalize="off"
        autoComplete="off"
        autoCorrect="off"
      />
    </div>
  )
}

export default MermaidEditor