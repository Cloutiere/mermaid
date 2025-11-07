// frontend/src/components/MermaidViewer.tsx
// Version 2.1 (Audit et Stabilisation du Zoom/Pan)

import { useEffect, useRef } from 'react'
import type { Mermaid } from 'mermaid'
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch'
import type { TransformWrapperProps } from 'react-zoom-pan-pinch' // Import type for better typing

// Props interface
interface MermaidViewerProps {
  mermaidCode: string
  onRenderStateChange?: (hasError: boolean) => void
}

// Configuration par défaut pour TransformWrapper
const transformWrapperConfig: Partial<TransformWrapperProps> = {
  centerOnInit: true,
  limitToBounds: false, // Permet de déplacer le SVG en dehors de la vue si nécessaire
  minScale: 0.1,
  maxScale: 15,
}

const MermaidViewer: React.FC<MermaidViewerProps> = ({ mermaidCode, onRenderStateChange }) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const renderVersionRef = useRef(0)

  useEffect(() => {
    const renderGraph = async () => {
      if (!containerRef.current) {
        return
      }

      renderVersionRef.current += 1
      const currentRenderVersion = renderVersionRef.current
      // Nettoyage forcé de l'ancien SVG pour éviter les problèmes de superposition ou de mise à jour.
      containerRef.current.innerHTML = ''

      if (!mermaidCode || mermaidCode.trim() === '') {
        containerRef.current.innerHTML =
          '<p class="text-gray-400 text-center p-8">Le graphe apparaîtra ici.</p>'
        onRenderStateChange?.(false)
        return
      }

      try {
        // Justification technique:
        // Mermaid.js utilise un état interne global. Lors de la suppression et du
        // remplacement du SVG (rendu destructif), il est crucial de réinitialiser
        // cet état pour éviter les fuites de mémoire et les erreurs de rendu
        // pour le graphe suivant. Supprimer l'objet global 'mermaid' force un
        // chargement propre de la bibliothèque pour chaque nouveau rendu.
        delete (window as any).mermaid 
        const mermaid: Mermaid = (await import('mermaid')).default

        mermaid.initialize({
          startOnLoad: false,
          theme: 'default',
          securityLevel: 'loose',
          // AJOUT CRITIQUE POUR GRANDS GRAPHES
          maxEdges: 3000, // Augmente la limite de 500 à 3000 relations
        })

        await mermaid.parse(mermaidCode)
        const graphId = `mermaid-graph-${Date.now()}`
        const { svg } = await mermaid.render(graphId, mermaidCode)

        if (renderVersionRef.current === currentRenderVersion && containerRef.current) {
          // Note: Le SVG doit être inséré directement dans le containerRef
          // qui est lui-même enveloppé dans TransformComponent.
          containerRef.current.innerHTML = svg
          onRenderStateChange?.(false)
        }
      } catch (error) {
        if (renderVersionRef.current !== currentRenderVersion || !containerRef.current) {
          return
        }

        console.error('Erreur de Rendu Mermaid:', error)

        let errorMessage = 'Une erreur de syntaxe est survenue dans le code Mermaid.'
        if (error instanceof Error) {
          errorMessage = error.message.includes('</style>')
            ? error.message.split('</style>')[1]?.trim() || error.message
            : error.message
        }

        containerRef.current.innerHTML = `
          <div class="p-4 bg-red-50 border-l-4 border-red-500 text-red-800">
            <h3 class="font-bold">Erreur de Rendu Mermaid</h3>
            <pre class="mt-2 text-sm whitespace-pre-wrap font-mono bg-red-100 p-2 rounded">${errorMessage
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')}</pre>
          </div>
        `
        onRenderStateChange?.(true)
      }
    }

    renderGraph()
  }, [mermaidCode, onRenderStateChange])

  return (
    <div className="w-full h-full p-4 border border-gray-200 rounded-lg bg-white shadow-sm overflow-hidden">
      {/* Configuration du wrapper pour le Zoom/Pan */}
      <TransformWrapper
        {...transformWrapperConfig}
      >
        <TransformComponent
          // Ces styles sont critiques pour que TransformWrapper occupe 100% de l'espace disponible
          wrapperStyle={{ width: '100%', height: '100%' }}
          contentStyle={{ width: '100%', height: '100%' }}
        >
          <div
            ref={containerRef}
            // Le conteneur interne doit être flexible pour centrer le SVG s'il est petit
            className="mermaid-container flex justify-center items-center h-full w-full"
          />
        </TransformComponent>
      </TransformWrapper>
    </div>
  )
}

export default MermaidViewer