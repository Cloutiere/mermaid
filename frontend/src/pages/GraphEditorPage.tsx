// frontend/src/pages/GraphEditorPage.tsx
// Version 3.0 (Refactoring with useGraphEditor Hook)

import { useParams, useNavigate } from 'react-router-dom'
import { useState, useMemo, useRef } from 'react'
import { useGraphEditor } from '@/hooks/useGraphEditor' // NOUVEAU

import MermaidEditor from '@/components/MermaidEditor'
import MermaidViewer from '@/components/MermaidViewer'
import ImportContentModal from '@/components/ImportContentModal'
import StyleManagerModal from '@/components/StyleManagerModal'
import ApplyStyleModal from '@/components/ApplyStyleModal'
import SubgraphManagerModal from '@/components/SubgraphManagerModal'

function GraphEditorPage() {
  // --- 1. Initialisation et Hooks ---
  const { projectId, subprojectId } = useParams<{ projectId: string; subprojectId: string }>()
  const navigate = useNavigate()
  const subprojectIdNumber = subprojectId ? Number(subprojectId) : null

  // Le hook gère toute la logique de données
  const {
    subproject,
    currentMermaidCode,
    loading,
    isSaving,
    isExporting,
    error,
    isDirty,
    setCurrentMermaidCode,
    refetchSubProject,
    saveMermaidCode,
    handleExport,
  } = useGraphEditor(subprojectIdNumber)

  // États spécifiques à l'UI
  const [hasMermaidError, setHasMermaidError] = useState(false)
  const [editorWidthRatio, setEditorWidthRatio] = useState(50)
  const [showJsonImportModal, setShowJsonImportModal] = useState(false)
  const [showStyleManagerModal, setShowStyleManagerModal] = useState(false)
  const [showApplyStyleModal, setShowApplyStyleModal] = useState(false)
  const [showSubgraphManagerModal, setShowSubgraphManagerModal] = useState(false)

  const fileInputRef = useRef<HTMLInputElement>(null)

  // --- 2. Logique Dérivée pour l'UI ---
  const isSaveEnabled = useMemo(() => {
    return !isSaving && !hasMermaidError && !!currentMermaidCode.trim()
  }, [isSaving, hasMermaidError, currentMermaidCode])

  const isSaveDisabled = !isSaveEnabled

  // --- 3. Handlers d'UI ---
  const handleBack = () => navigate('/')

  // Import Structure (.mmd)
  const handleImportClick = () => fileInputRef.current?.click()

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        if (e.target?.result && typeof e.target.result === 'string') {
          setCurrentMermaidCode(e.target.result)
        }
      }
      reader.onerror = () => {
        // Idéalement, cet état d'erreur devrait aussi être géré par le hook.
        // Pour cette refactorisation, on garde une alerte simple.
        alert('Erreur lors de la lecture du fichier.')
      }
      reader.readAsText(file)
    }
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  // --- 4. Callbacks des Modales ---
  // Ces callbacks se contentent d'appeler le refetch du hook.
  const handleJsonImportSuccess = () => {
    setShowJsonImportModal(false)
    refetchSubProject(true)
  }

  const handleStyleChangeSuccess = () => {
    refetchSubProject(true)
  }

  const handleNodeStyleApplySuccess = () => {
    refetchSubProject(true)
  }

  const handleSubgraphUpdateSuccess = () => {
    refetchSubProject(true)
  }

  // --- 5. Rendu Conditionnel ---
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8 flex justify-center items-center">
        <p className="text-xl font-semibold text-indigo-600">Chargement de l'Éditeur...</p>
      </div>
    )
  }

  if (error && !isSaving && !isExporting) {
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
  const layoutOptions = [
    { label: 'Vue', ratio: 0 },
    { label: '25/75', ratio: 25 },
    { label: '50/50', ratio: 50 },
    { label: '75/25', ratio: 75 },
    { label: 'Éditeur', ratio: 100 },
  ]

  // --- 6. Rendu du Composant ---
  return (
    <div className="min-h-screen bg-gray-50 p-4 lg:p-8 flex flex-col">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: 'none' }}
        accept=".mmd,.txt"
      />

      <header className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl lg:text-4xl font-extrabold text-indigo-700">
            Éditeur : {subProjectTitle}
          </h1>
          <p className="text-md lg:text-lg text-gray-500">
            ID Projet: {projectId} | ID Sous-Projet: {subprojectId}
          </p>
        </div>
        <button
          onClick={handleBack}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition text-sm font-medium"
        >
          &larr; Retour à la liste
        </button>
      </header>

      {error && (isSaving || isExporting) && (
        <div
          className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4"
          role="alert"
        >
          <strong className="font-bold">Erreur: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}
      {isDirty && !isSaving && !hasMermaidError && (
        <div
          className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded relative mb-4"
          role="alert"
        >
          <span className="block sm:inline">Modifications non sauvegardées.</span>
        </div>
      )}

      <div className="mb-4 flex justify-between items-center">
        {/* Layout controls */}
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-600">Affichage:</span>
          <div className="flex items-center rounded-md border border-gray-300 p-0.5 bg-gray-100">
            {layoutOptions.map(({ label, ratio }) => (
              <button
                key={ratio}
                onClick={() => setEditorWidthRatio(ratio)}
                className={`px-3 py-1 text-xs font-semibold rounded ${
                  editorWidthRatio === ratio
                    ? 'bg-white text-indigo-600 shadow-sm'
                    : 'bg-transparent text-gray-500 hover:bg-gray-200'
                } transition-colors`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex flex-wrap justify-end gap-3">
          <button
            onClick={() => setShowSubgraphManagerModal(true)}
            disabled={isSaving || isExporting || loading}
            className={`px-4 py-2 rounded-md text-sm font-medium transition border ${
              isSaving || isExporting || loading
                ? 'bg-gray-200 text-gray-400 border-gray-300 cursor-not-allowed'
                : 'bg-white text-blue-600 border-blue-300 hover:bg-blue-50'
            }`}
          >
            Gérer Subgraphs
          </button>
          <button
            onClick={() => setShowStyleManagerModal(true)}
            disabled={isSaving || isExporting || loading}
            className={`px-4 py-2 rounded-md text-sm font-medium transition border ${
              isSaving || isExporting || loading
                ? 'bg-gray-200 text-gray-400 border-gray-300 cursor-not-allowed'
                : 'bg-white text-purple-600 border-purple-300 hover:bg-purple-50'
            }`}
          >
            Gérer Styles (ClassDef)
          </button>
          <button
            onClick={() => setShowApplyStyleModal(true)}
            disabled={isSaving || isExporting || loading}
            className={`px-4 py-2 rounded-md text-sm font-medium transition border ${
              isSaving || isExporting || loading
                ? 'bg-gray-200 text-gray-400 border-gray-300 cursor-not-allowed'
                : 'bg-white text-teal-600 border-teal-300 hover:bg-teal-50'
            }`}
          >
            Appliquer Style à Nœud
          </button>
          <button
            onClick={() => setShowJsonImportModal(true)}
            disabled={isSaving || isExporting || loading}
            className={`px-4 py-2 rounded-md text-sm font-medium transition border ${
              isSaving || isExporting || loading
                ? 'bg-gray-200 text-gray-400 border-gray-300 cursor-not-allowed'
                : 'bg-white text-indigo-600 border-indigo-300 hover:bg-indigo-50'
            }`}
          >
            Importer Contenu JSON
          </button>
          <button
            onClick={handleImportClick}
            disabled={isSaving || isExporting || loading}
            className={`px-4 py-2 rounded-md text-sm font-medium transition border ${
              isSaving || isExporting || loading
                ? 'bg-gray-200 text-gray-400 border-gray-300 cursor-not-allowed'
                : 'bg-white text-indigo-600 border-indigo-300 hover:bg-indigo-50'
            }`}
          >
            Importer Structure (.mmd)
          </button>
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
            onClick={saveMermaidCode}
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
      </div>

      <main className="flex-grow flex flex-row gap-6 h-[calc(100vh-250px)]">
        {editorWidthRatio > 0 && (
          <div className="h-full flex flex-col" style={{ flexBasis: `${editorWidthRatio}%` }}>
            <h2 className="text-lg font-semibold text-gray-700 mb-2">Éditeur Mermaid</h2>
            <div className="flex-grow">
              <MermaidEditor code={currentMermaidCode} onChange={setCurrentMermaidCode} />
            </div>
          </div>
        )}
        {editorWidthRatio < 100 && (
          <div className="h-full flex flex-col" style={{ flexBasis: `${100 - editorWidthRatio}%` }}>
            <h2 className="text-lg font-semibold text-gray-700 mb-2">Visualiseur</h2>
            <div className="flex-grow">
              <MermaidViewer
                mermaidCode={currentMermaidCode}
                onRenderStateChange={setHasMermaidError}
              />
            </div>
          </div>
        )}
      </main>

      {/* Modals */}
      {showJsonImportModal && subproject && (
        <ImportContentModal
          subprojectId={subproject.id}
          onClose={() => setShowJsonImportModal(false)}
          onImportSuccess={handleJsonImportSuccess}
        />
      )}
      {showStyleManagerModal && subproject && (
        <StyleManagerModal
          isOpen={showStyleManagerModal}
          onClose={() => setShowStyleManagerModal(false)}
          subprojectId={subproject.id}
          onStyleChange={handleStyleChangeSuccess}
        />
      )}
      {showApplyStyleModal && subproject && (
        <ApplyStyleModal
          isOpen={showApplyStyleModal}
          onClose={() => setShowApplyStyleModal(false)}
          subprojectId={subproject.id}
          onApplySuccess={handleNodeStyleApplySuccess}
        />
      )}
      {showSubgraphManagerModal && subproject && (
        <SubgraphManagerModal
          isOpen={showSubgraphManagerModal}
          onClose={() => setShowSubgraphManagerModal(false)}
          subprojectId={subproject.id}
          onUpdateSuccess={handleSubgraphUpdateSuccess}
        />
      )}
    </div>
  )
}

export default GraphEditorPage