// frontend/src/components/MermaidViewer.tsx
// Version 2.0 (Intégration de react-zoom-pan-pinch)

import { useEffect, useRef } from 'react'
import type { Mermaid } from 'mermaid'
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch'

// Props interface
interface MermaidViewerProps {
  mermaidCode: string
  onRenderStateChange?: (hasError: boolean) => void
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
      containerRef.current.innerHTML = ''

      if (!mermaidCode || mermaidCode.trim() === '') {
        containerRef.current.innerHTML =
          '<p class="text-gray-400 text-center p-8">Le graphe apparaîtra ici.</p>'
        onRenderStateChange?.(false)
        return
      }

      try {
        delete (window as any).mermaid
        const mermaid: Mermaid = (await import('mermaid')).default

        mermaid.initialize({
          startOnLoad: false,
          theme: 'default',
          securityLevel: 'loose',
        })

        await mermaid.parse(mermaidCode)
        const graphId = `mermaid-graph-${Date.now()}`
        const { svg } = await mermaid.render(graphId, mermaidCode)

        if (renderVersionRef.current === currentRenderVersion && containerRef.current) {
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
      <TransformWrapper
        centerOnInit={true}
        limitToBounds={false}
        minScale={0.1}
        maxScale={15}
      >
        <TransformComponent
          wrapperStyle={{ width: '100%', height: '100%' }}
          contentStyle={{ width: '100%', height: '100%' }}
        >
          <div
            ref={containerRef}
            className="mermaid-container flex justify-center items-center h-full w-full"
          />
        </TransformComponent>
      </TransformWrapper>
    </div>
  )
}

export default MermaidViewer