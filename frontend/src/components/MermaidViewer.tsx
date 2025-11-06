// frontend/src/components/MermaidViewer.tsx
// 1.1.0 (Correction: Rendu asynchrone de mermaid.js)

import { useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'

// Props interface
interface MermaidViewerProps {
  mermaidCode: string
}

const MermaidViewer: React.FC<MermaidViewerProps> = ({ mermaidCode }) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const [renderError, setRenderError] = useState<string | null>(null)

  // Initialize Mermaid.js once on component mount
  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'default',
      securityLevel: 'loose', // Allows for more complex interactions if needed later
    })
  }, []) // Empty dependency array ensures this runs only once

  // Render the graph whenever mermaidCode changes (now handles asynchronous rendering)
  useEffect(() => {
    if (!containerRef.current) {
      return
    }

    // Clear previous content and error
    containerRef.current.innerHTML = ''
    setRenderError(null)

    if (!mermaidCode || mermaidCode.trim() === '') {
      containerRef.current.innerHTML = '<p class="text-gray-400 text-center p-8">Le graphe apparaîtra ici.</p>'
      return
    }

    const renderGraph = async () => {
      try {
        // Generate a unique ID for each render to avoid conflicts
        const graphId = `mermaid-graph-${Date.now()}`

        // ATTENTION: mermaid.render est ASYNCHRONE et retourne une Promesse.
        // Nous devons utiliser await pour récupérer le code SVG et le bindage.
        const { svg } = await mermaid.render(graphId, mermaidCode)

        if (containerRef.current) {
          containerRef.current.innerHTML = svg
        }

      } catch (error) {
        console.error('Erreur de rendu Mermaid:', error)
        let errorMessage = 'Une erreur de syntaxe est survenue dans le code Mermaid.'

        // Tentative de récupérer un message d'erreur lisible
        if (error instanceof Error) {
            // Dans certaines versions, l'erreur de mermaid est encapsulée ou formatée étrangement
            errorMessage = error.message.includes('</style>') 
                ? error.message.split('</style>')[1]?.trim() || error.message
                : error.message
        }
        setRenderError(errorMessage)
      }
    }

    renderGraph()

  }, [mermaidCode])

  return (
    <div className="w-full h-full p-4 border border-gray-200 rounded-lg bg-white shadow-sm overflow-auto">
      {renderError ? (
        <div className="p-4 bg-red-50 border-l-4 border-red-500 text-red-800">
          <h3 className="font-bold">Erreur de Rendu Mermaid</h3>
          <pre className="mt-2 text-sm whitespace-pre-wrap font-mono bg-red-100 p-2 rounded">
            {renderError}
          </pre>
        </div>
      ) : (
        // Le conteneur doit être géré en flex pour centrer le SVG si nécessaire
        <div ref={containerRef} className="mermaid-container flex justify-center items-center h-full w-full" />
      )}
    </div>
  )
}

export default MermaidViewer