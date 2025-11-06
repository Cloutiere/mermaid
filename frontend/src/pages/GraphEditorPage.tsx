// frontend/src/pages/GraphEditorPage.tsx
import { useParams } from 'react-router-dom'

function GraphEditorPage() {
  // Définition des types attendus pour les paramètres d'URL
  interface EditorParams {
    projectId: string
    subprojectId: string
  }

  // Utilisation de useParams avec le typage défini
  const { projectId, subprojectId } = useParams<keyof EditorParams>() as EditorParams

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <header className="mb-8">
        <h1 className="text-4xl font-extrabold text-indigo-700">
          Éditeur de Graphe Narratif
        </h1>
        <p className="text-lg text-gray-500">
          Visualisation et édition du sous-projet sélectionné.
        </p>
      </header>

      <div className="bg-white p-6 rounded-xl shadow-lg border border-indigo-100">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
          Statut de l'URL (Vérification du Routage)
        </h2>
        <div className="space-y-2">
          <p className="text-gray-700">
            <strong className="font-medium text-indigo-600">ID du Projet :</strong> {projectId || 'Non spécifié'}
          </p>
          <p className="text-gray-700">
            <strong className="font-medium text-indigo-600">ID du Sous-Projet :</strong> {subprojectId || 'Non spécifié'}
          </p>
        </div>
      </div>

      <div className="mt-8 p-4 bg-yellow-50 border-l-4 border-yellow-500">
        <p className="text-sm text-yellow-700">
          Placeholder : Le composant d'édition de graphe (Mermaid.js) sera implémenté ici.
        </p>
      </div>
    </div>
  )
}

export default GraphEditorPage