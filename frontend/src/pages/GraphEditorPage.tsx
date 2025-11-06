// frontend/src/pages/GraphEditorPage.tsx
// 1.5.0 (Ajout de la fonctionnalité d'exportation)

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
  const [isExporting, setIsExporting] = useState(false) // État pour l'exportation
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

  // 3b. Détermination de l'activation du bouton de sauvegarde
  const isSaveEnabled = useMemo(() => {
    return !isSaving && !hasMermaidError && !!normalize(currentMermaidCode);
  }, [isSaving, hasMermaidError, currentMermaidCode]);

  // Déterminer la variable de désactivation finale pour la sauvegarde
  const isSaveDisabled = !isSaveEnabled;

  // --- 4. Rendu Conditionnel (Chargement et Erreur) - DOIT ÊTRE APRÈS TOUS LES HOOKS ---

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8 flex justify-center items-center">
        <p className="text-xl font-semibold text-indigo-600">Chargement de l'Éditeur...</p>
      </div>
    )
  }

  if (error && !isSaving && !isExporting) { // N'affiche l'erreur pleine page que si ce n'est pas une erreur d'action
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

  // --- 5. Handlers d'Action : Sauvegarde et Exportation ---
  const handleSave = async () => {
    if (!subproject) return

    setIsSaving(true)
    setError(null)

    const payload: SubProjectCreate = {
        project_id: subproject.project_id,
        title: subproject.title,
        mermaid_definition: currentMermaidCode, 
        visual_layout: subproject.visual_layout || null,
    }

    try {
        const updatedData = await apiService.updateSubProject(subproject.id, payload)
        setSubProject(updatedData)
        setCurrentMermaidCode(updatedData.mermaid_definition)
        console.log("Sauvegarde réussie!", updatedData)
    } catch (err) {
        console.error("Échec de la sauvegarde:", err)
        setError(err instanceof Error ? err.message : 'Une erreur inconnue est survenue lors de la sauvegarde.')
    } finally {
        setIsSaving(false)
    }
  }

  const handleExport = async () => {
    if (!subproject) return;

    setIsExporting(true);
    setError(null);

    try {
        const mermaidCodeExported = await apiService.exportMermaid(subproject.id);

        const blob = new Blob([mermaidCodeExported], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');

        const fileName = `${subproject.title.replace(/\s+/g, '_')}_export.mmd`;
        link.href = url;
        link.setAttribute('download', fileName);

        document.body.appendChild(link);
        link.click();

        document.body.removeChild(link);
        URL.revokeObjectURL(url);

    } catch (err) {
        console.error("Échec de l'exportation:", err);
        setError(err instanceof Error ? err.message : "Une erreur inconnue est survenue lors de l'exportation.");
    } finally {
        setIsExporting(false);
    }
  };

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

      {/* Affichage des erreurs d'action (sauvegarde, export) */}
      {error && (isSaving || isExporting) && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
            <strong className="font-bold">Erreur: </strong>
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
            onClick={handleExport}
            disabled={isSaving || isExporting || loading}
            className={`px-4 py-2 rounded-md text-sm font-medium transition ${
              isSaving || isExporting || loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            {isExporting ? 'Exportation...' : 'Exporter'}
          </button>
          <button
            onClick={handleSave}
            disabled={isSaveDisabled} 
            className={`px-5 py-2 text-white rounded-md text-sm font-semibold transition ${
                isSaveDisabled
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