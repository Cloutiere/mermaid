// frontend/src/components/MermaidViewer.tsx
// 1.2.0 (Stratégie de Hard Reset)

import { useEffect, useRef } from 'react'
// `mermaid` livre ses propres types à partir de la v10. L'import `type` est conforme à `verbatimModuleSyntax`.
import type { Mermaid } from 'mermaid'

// Props interface
interface MermaidViewerProps {
  mermaidCode: string
  onRenderStateChange?: (hasError: boolean) => void
}

const MermaidViewer: React.FC<MermaidViewerProps> = ({ mermaidCode, onRenderStateChange }) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const renderVersionRef = useRef(0) // Pour gérer les race conditions lors des changements rapides du code

  useEffect(() => {
    // Cet effet se déclenche à chaque modification du code Mermaid.
    const renderGraph = async () => {
      if (!containerRef.current) {
        return
      }

      // Incrémente la version pour invalider les rendus asynchrones précédents qui pourraient se terminer plus tard.
      renderVersionRef.current += 1
      const currentRenderVersion = renderVersionRef.current

      // Efface le contenu précédent
      containerRef.current.innerHTML = ''

      if (!mermaidCode || mermaidCode.trim() === '') {
        containerRef.current.innerHTML = '<p class="text-gray-400 text-center p-8">Le graphe apparaîtra ici.</p>'
        onRenderStateChange?.(false) // Un code vide n'est pas un état d'erreur
        return
      }

      try {
        // --- STRATÉGIE DE HARD RESET ---
        // 1. Supprime l'instance globale potentiellement corrompue attachée à `window`.
        delete (window as any).mermaid

        // 2. Importe dynamiquement une nouvelle instance propre du module mermaid.
        const mermaid: Mermaid = (await import('mermaid')).default

        // 3. Initialise la nouvelle instance avec notre configuration.
        mermaid.initialize({
          startOnLoad: false,
          theme: 'default',
          securityLevel: 'loose',
        })

        // 4. Valide la syntaxe avant de tenter le rendu. Cela lève une erreur détaillée en cas d'échec.
        await mermaid.parse(mermaidCode)

        // 5. Génère le SVG du graphe.
        const graphId = `mermaid-graph-${Date.now()}`
        const { svg } = await mermaid.render(graphId, mermaidCode)

        // Met à jour le DOM uniquement si c'est la tentative de rendu la plus récente.
        if (renderVersionRef.current === currentRenderVersion && containerRef.current) {
          containerRef.current.innerHTML = svg
          onRenderStateChange?.(false) // Notifie le parent du succès du rendu
        }
      } catch (error) {
        // Affiche l'erreur uniquement si elle provient de la tentative de rendu la plus récente.
        if (renderVersionRef.current !== currentRenderVersion || !containerRef.current) {
          return // Un ancien rendu a échoué, mais un nouveau est en cours. On ignore.
        }

        console.error('Erreur de Rendu Mermaid:', error)

        let errorMessage = 'Une erreur de syntaxe est survenue dans le code Mermaid.'
        if (error instanceof Error) {
          // Tente d'extraire un message plus lisible de l'erreur de Mermaid.
          errorMessage = error.message.includes('</style>')
            ? error.message.split('</style>')[1]?.trim() || error.message
            : error.message
        }

        // Affiche le message d'erreur directement dans le conteneur.
        // Utilisation d'un template literal pour une structure HTML propre pour le message d'erreur.
        containerRef.current.innerHTML = `
          <div class="p-4 bg-red-50 border-l-4 border-red-500 text-red-800">
            <h3 class="font-bold">Erreur de Rendu Mermaid</h3>
            <pre class="mt-2 text-sm whitespace-pre-wrap font-mono bg-red-100 p-2 rounded">${errorMessage.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
          </div>
        ` // Échappement des caractères HTML dans le message d'erreur par sécurité.
        onRenderStateChange?.(true) // Notifie le parent de l'échec du rendu
      }
    }

    renderGraph()

    // Aucune fonction de nettoyage n'est nécessaire car on vide `innerHTML` manuellement au début de l'effet.
  }, [mermaidCode, onRenderStateChange])

  // Le composant rend désormais un simple conteneur.
  // Son contenu est entièrement géré par le hook `useEffect` via une manipulation directe du DOM.
  return (
    <div className="w-full h-full p-4 border border-gray-200 rounded-lg bg-white shadow-sm overflow-auto">
        <div ref={containerRef} className="mermaid-container flex justify-center items-center h-full w-full" />
    </div>
  )
}

export default MermaidViewer