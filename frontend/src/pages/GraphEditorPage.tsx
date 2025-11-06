// frontend/src/pages/GraphEditorPage.tsx
// 1.4.3 (Correction critique de l'ordre des Hooks)

import { useParams, useNavigate } from 'react-router-dom'
import { useState, useEffect, useMemo } from 'react'
import apiService from '@/services/api'
import type { SubProjectRead, SubProjectCreate } from '@/types/api'
import MermaidEditor from '@/components/MermaidEditor'
import MermaidViewer from '@/components/MermaidViewer'

// Fonction utilitaire déplacée à l'extérieur pour ne pas être recréée à chaque rendu
const normalize = (code: string | null | undefined): string => {
  if (typeof code !== 'string') return '';
  // 1. Uniformiser les fins de ligne
  const unixCode = code.replace(/\r\n/g, '\n');
  // 2. Supprimer les espaces blancs de début et de fin
  return unixCode.trim();
};

function GraphEditorPage() {
  // Définition des types attendus pour les paramètres d'URL
  interface EditorParams {
    projectId: string
    subprojectId: string
  }

  const { projectId, subprojectId } = useParams<keyof EditorParams>() as EditorParams
  const navigate = useNavigate()

  // --- 1. Gestion des États (Doit être en premier) ---
  const [subproject, setSubProject] = useState<SubProjectRead | null>(null)
  const [currentMermaidCode, setCurrentMermaidCode] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasMermaidError, setHasMermaidError] = useState(false) // État pour les erreurs de rendu Mermaid

  const subprojectIdNumber = subprojectId ? Number(subprojectId) : null

  // --- 2. Fonction de Chargement Asynchrone (Hook useEffect) ---
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

  // --- 3. Logique de Détection de Changement (Hooks useMemo) - DOIVENT ÊTRE AVANT LES RETOURS CONDITIONNELS ---

  // 3a. Détection des changements (Dirty State)
  const isDirty = useMemo(() => {
    if (!subproject || loading) return false

    const originalCode = normalize(subproject.mermaid_definition);
    const newCode = normalize(currentMermaidCode);

    // Compare les codes normalisés
    return newCode !== originalCode
  }, [currentMermaidCode, subproject, loading])

  // 3b. Détermination de l'activation du bouton de sauvegarde (NOUVEAU)
  const isSaveEnabled = useMemo(() => {
    // Le bouton est activé si :
    // 1. On n'est pas en train de sauvegarder (!isSaving)
    // 2. Il n'y a pas d'erreur de syntaxe (!hasMermaidError)
    // 3. Le code édité n'est pas vide (!!normalize(currentMermaidCode))
    return !isSaving && !hasMermaidError && !!normalize(currentMermaidCode);
  }, [isSaving, hasMermaidError, currentMermaidCode]);

  // Déterminer la variable de désactivation finale
  const isDisabled = !isSaveEnabled;

  // --- 4. Rendu Conditionnel (Chargement et Erreur) - DOIT ÊTRE APRÈS TOUS LES HOOKS ---

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8 flex justify-center items-center">
        <p className="text-xl font-semibold text-indigo-600">Chargement de l'Éditeur...</p>
      </div>
    )
  }

  if (error && !isSaving) { // N'affiche l'erreur pleine page que si ce n'est pas une erreur de sauvegarde
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <header className="mb-8">
          <h1 className="text-4xl font-extrabold text-red-700">Erreur</h1>
        </header>
        <div className="bg-white p-6 rounded-xl shadow-lg border border-red-100">
          <p className="text-red-700 font-medium">Détail: {error}</p>
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

  if (!subproject) {
    return <div className="p-8">Sous-projet non trouvé.</div>
  }

  const subProjectTitle = subproject.title || `Sous-Projet ID: ${subprojectId}`

  // --- 5. Handlers d'Action : Sauvegarde ---
  const handleSave = async () => {
    if (!subproject) return

    setIsSaving(true)
    setError(null)

    const payload: SubProjectCreate = {
        project_id: subproject.project_id,
        title: subproject.title,
        // Sauvegarde du code actuel (non normalisé)
        mermaid_definition: currentMermaidCode, 
        visual_layout: subproject.visual_layout || null,
    }

    try {
        const updatedData = await apiService.updateSubProject(subproject.id, payload)
        // Met à jour l'état du sous-projet avec les données du serveur
        setSubProject(updatedData)
        // Met à jour le code actuel avec la version du serveur (important pour réinitialiser 'isDirty' et l'état général)
        setCurrentMermaidCode(updatedData.mermaid_definition)
        console.log("Sauvegarde réussie!", updatedData)
    } catch (err) {
        console.error("Échec de la sauvegarde:", err)
        setError(err instanceof Error ? err.message : 'Une erreur inconnue est survenue lors de la sauvegarde.')
    } finally {
        setIsSaving(false)
    }
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

      {/* Affichage des erreurs de sauvegarde */}
      {error && isSaving && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
            <strong className="font-bold">Erreur de Sauvegarde: </strong>
            <span className="block sm:inline">{error}</span>
        </div>
      )}
      {/* Affichage des avertissements de modification non sauvegardée */}
      {isDirty && !isSaving && !hasMermaidError && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded relative mb-4" role="alert">
            <span className="block sm:inline">Modifications non sauvegardées.</span>
        </div>
      )}

      {/* Barre d'actions */}
      <div className="mb-4 flex justify-end space-x-3">
         <button
            disabled
            className="px-4 py-2 bg-gray-300 text-gray-500 rounded-md text-sm font-medium cursor-not-allowed"
          >
            Exporter
          </button>
          <button
            onClick={handleSave}
            // Utilise la variable isDisabled, qui est l'inverse de isSaveEnabled
            disabled={isDisabled} 
            className={`px-5 py-2 text-white rounded-md text-sm font-semibold transition ${
                isDisabled
                    ? 'bg-indigo-300 cursor-not-allowed'
                    : 'bg-indigo-600 hover:bg-indigo-700 cursor-pointer' 
            }`}
          >
            {isSaving ? 'Sauvegarde...' : hasMermaidError ? 'Erreur de syntaxe' : 'Sauvegarder'}
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
            <MermaidViewer 
              mermaidCode={currentMermaidCode}
              onRenderStateChange={setHasMermaidError}
            />
           </div>
        </div>
      </main>
    </div>
  )
}

export default GraphEditorPage