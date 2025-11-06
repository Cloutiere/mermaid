// frontend/src/pages/GraphEditorPage.tsx
import { useParams, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import apiService from '@/services/api' // Assurez-vous que cet alias est configuré
import { SubProjectRead } from '@/types/api' // Assurez-vous que cet alias est configuré

function GraphEditorPage() {
  // Définition des types attendus pour les paramètres d'URL
  interface EditorParams {
    projectId: string
    subprojectId: string
  }

  // Utilisation de useParams avec le typage défini
  const { projectId, subprojectId } = useParams<keyof EditorParams>() as EditorParams
  const navigate = useNavigate()

  // --- 1. Gestion des États ---
  const [subproject, setSubProject] = useState<SubProjectRead | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Convertir l'ID pour l'API
  const subprojectIdNumber = subprojectId ? Number(subprojectId) : null

  // --- 2. Fonction de Chargement Asynchrone ---
  useEffect(() => {
    if (!subprojectIdNumber || isNaN(subprojectIdNumber)) {
      setError("Erreur de routage: ID du sous-projet invalide ou manquant.")
      setLoading(false)
      return
    }

    const fetchSubProject = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await apiService.getSubProject(subprojectIdNumber)
        setSubProject(data)
      } catch (err) {
        console.error('Échec du chargement du sous-projet:', err)
        // Utilise le message d'erreur formaté par apiService.handleError
        setError(err instanceof Error ? err.message : 'Une erreur inconnue est survenue lors du chargement.')
      } finally {
        setLoading(false)
      }
    }

    fetchSubProject()
  }, [subprojectIdNumber]) // Déclenchement au changement de subprojectId

  // --- 3. Rendu Conditionnel (Chargement et Erreur) ---

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8 flex justify-center items-center">
        <p className="text-xl font-semibold text-indigo-600">Chargement du Graphe...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <header className="mb-8">
          <h1 className="text-4xl font-extrabold text-red-700">Erreur de Chargement</h1>
        </header>
        <div className="bg-white p-6 rounded-xl shadow-lg border border-red-100">
          <p className="text-red-700 font-medium">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
          >
            Retour à la liste des projets
          </button>
        </div>
      </div>
    )
  }

  // Si chargé avec succès
  const subProjectTitle = subproject?.title || `Sous-Projet ID: ${subprojectId}`

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <header className="mb-8">
        <h1 className="text-4xl font-extrabold text-indigo-700">
          Éditeur : {subProjectTitle}
        </h1>
        <p className="text-lg text-gray-500">
          ID Projet: {projectId} | ID Sous-Projet: {subprojectId}
        </p>
      </header>

      <div className="bg-white p-6 rounded-xl shadow-lg border border-indigo-100">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
          Contenu du Sous-Projet (Mermaid Definition)
        </h2>
        <pre className="whitespace-pre-wrap bg-gray-100 p-3 rounded text-sm">
            {subproject?.mermaid_definition || "// Définition Mermaid non disponible"}
        </pre>
      </div>

      <div className="mt-8 p-4 bg-yellow-50 border-l-4 border-yellow-500">
        <p className="text-sm text-yellow-700">
          Placeholder : Les composants MermaidViewer et MermaidEditor seront implémentés ici.
        </p>
      </div>
    </div>
  )
}

export default GraphEditorPage