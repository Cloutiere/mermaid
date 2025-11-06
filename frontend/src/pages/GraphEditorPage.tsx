// frontend/src/pages/GraphEditorPage.tsx
// 1.2.0 (Ajout de la logique isDirty pour activer le bouton Sauvegarder)

import { useParams, useNavigate } from 'react-router-dom'
import { useState, useEffect, useMemo } from 'react'
import apiService from '@/services/api'
import type { SubProjectRead } from '@/types/api'
import MermaidEditor from '@/components/MermaidEditor'
import MermaidViewer from '@/components/MermaidViewer'

function GraphEditorPage() {
  // Définition des types attendus pour les paramètres d'URL
  interface EditorParams {
    projectId: string
    subprojectId: string
  }

  const { projectId, subprojectId } = useParams<keyof EditorParams>() as EditorParams
  const navigate = useNavigate()

  // --- 1. Gestion des États ---
  const [subproject, setSubProject] = useState<SubProjectRead | null>(null)
  const [currentMermaidCode, setCurrentMermaidCode] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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
        // Initialisation du code éditable avec la définition Mermaid récupérée
        // Cette valeur sert de base de comparaison pour l'état "dirty"
        setCurrentMermaidCode(data.mermaid_definition || '') 
      } catch (err) {
        console.error('Échec du chargement du sous-projet:', err)
        setError(err instanceof Error ? err.message : 'Une erreur inconnue est survenue lors du chargement.')
      } finally {
        setLoading(false)
      }
    }

    fetchSubProject()
  }, [subprojectIdNumber])

  // --- 3. Logique de Détection de Changement (Dirty State) ---
  const isDirty = useMemo(() => {
    if (!subproject || loading) return false

    // Compare le code actuel avec le code chargé original
    return currentMermaidCode !== subproject.mermaid_definition
  }, [currentMermaidCode, subproject, loading])

  // --- 4. Rendu Conditionnel (Chargement et Erreur) ---

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8 flex justify-center items-center">
        <p className="text-xl font-semibold text-indigo-600">Chargement de l'Éditeur...</p>
      </div>
    )
  }

  if (error) {
    // ... (Code de rendu d'erreur inchangé)
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

  // --- 5. Handlers d'Action ---
  const handleSave = () => {
    // TODO: Implémenter l'appel API PUT pour sauvegarder currentMermaidCode
    console.log("Sauvegarde en cours...", currentMermaidCode)
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 lg:p-8 flex flex-col">
      <header className="mb-6">
        <h1 className="text-3xl lg:text-4xl font-extrabold text-indigo-700">
          Éditeur : {subProjectTitle}
        </h1>
        <p className="text-md lg:text-lg text-gray-500">
          ID Projet: {projectId} | ID Sous-Projet: {subprojectId}
        </p>
      </header>

      {/* Barre d'actions */}
      <div className="mb-4 flex justify-end space-x-3">
         <button
            disabled // L'export nécessite une logique backend/API dédiée, laissé désactivé.
            className="px-4 py-2 bg-gray-300 text-gray-500 rounded-md text-sm font-medium cursor-not-allowed"
          >
            Exporter
          </button>
          <button
            onClick={handleSave}
            disabled={!isDirty}
            className={`px-5 py-2 text-white rounded-md text-sm font-semibold transition ${
                isDirty 
                    ? 'bg-indigo-600 hover:bg-indigo-700 cursor-pointer' 
                    : 'bg-indigo-300 cursor-not-allowed'
            }`}
          >
            Sauvegarder
          </button>
      </div>

      {/* Layout principal de l'éditeur */}
      <main className="flex-grow grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-200px)]">
        {/* Colonne Gauche: Éditeur de code */}
        <div className="h-full flex flex-col">
           <h2 className="text-lg font-semibold text-gray-700 mb-2">Éditeur Mermaid</h2>
           <div className="flex-grow">
             <MermaidEditor code={currentMermaidCode} onChange={setCurrentMermaidCode} />
           </div>
        </div>

        {/* Colonne Droite: Visualiseur de graphe */}
        <div className="h-full flex flex-col">
           <h2 className="text-lg font-semibold text-gray-700 mb-2">Visualiseur</h2>
           <div className="flex-grow">
            <MermaidViewer mermaidCode={currentMermaidCode} />
           </div>
        </div>
      </main>
    </div>
  )
}

export default GraphEditorPage