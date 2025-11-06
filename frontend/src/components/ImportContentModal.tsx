// frontend/src/components/ImportContentModal.tsx
import React, { useState, useRef } from 'react'
import apiService from '@/services/api'
import type { NodeContentImportResponse } from '@/types/api'

interface ImportContentModalProps {
  subprojectId: number
  onClose: () => void
  onImportSuccess: () => void // Function to trigger parent reload
}

const ImportContentModal: React.FC<ImportContentModalProps> = ({
  subprojectId,
  onClose,
  onImportSuccess,
}) => {
  const [file, setFile] = useState<File | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [report, setReport] = useState<NodeContentImportResponse | null>(null)

  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0] || null
    if (selectedFile) {
      // Basic check for JSON mime type
      if (
        selectedFile.type !== 'application/json' &&
        !selectedFile.name.toLowerCase().endsWith('.json')
      ) {
        setError('Le fichier doit être de type JSON (.json).')
        setFile(null)
        return
      }
      setError(null)
      setFile(selectedFile)
    }
  }

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file || isLoading) return

    setIsLoading(true)
    setError(null)
    setReport(null)

    const reader = new FileReader()

    reader.onload = async (e) => {
      const content = e.target?.result as string
      let contentMap: Record<string, string> = {}

      try {
        const parsedJson = JSON.parse(content)

        // Validation 1: Must be a non-null object, not an array
        if (typeof parsedJson !== 'object' || parsedJson === null || Array.isArray(parsedJson)) {
          throw new Error(
            'Le contenu du fichier JSON doit être un objet Clé/Valeur (ex: {"mermaid_id": "contenu..."}).'
          )
        }

        // Validation 2: Coerce all entries to string:string map as expected by the API
        for (const key in parsedJson) {
          if (Object.prototype.hasOwnProperty.call(parsedJson, key)) {
            // Use String() to safely coerce to string
            contentMap[key] = String(parsedJson[key])
          }
        }
      } catch (validationError) {
        setError(
          validationError instanceof Error
            ? validationError.message
            : 'Erreur de lecture ou de format JSON.'
        )
        setIsLoading(false)
        return
      }

      // API Call
      try {
        const result = await apiService.importNodeContent(subprojectId, contentMap)
        setReport(result)
        onImportSuccess() // Notify parent to reload data
      } catch (apiError) {
        console.error('API Import Error:', apiError)
        setError(
          apiError instanceof Error
            ? apiError.message
            : "Échec de l'importation via l'API. Vérifiez la console pour plus de détails."
        )
      } finally {
        setIsLoading(false)
        setFile(null) // Reset file selection after process
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
      }
    }

    reader.onerror = () => {
      setError('Erreur lors de la lecture du fichier.')
      setIsLoading(false)
    }

    reader.readAsText(file)
  }

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto"
      aria-labelledby="modal-title"
      role="dialog"
      aria-modal="true"
    >
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          aria-hidden="true"
        ></div>

        {/* Modal panel */}
        <span
          className="hidden sm:inline-block sm:align-middle sm:h-screen"
          aria-hidden="true"
        >
          &#8203;
        </span>
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3
              className="text-xl leading-6 font-bold text-gray-900"
              id="modal-title"
            >
              Importation de Contenu Narratif JSON
            </h3>
            <p className="text-sm text-gray-500 mt-2">
              Importez un fichier JSON qui mappe les `mermaid_id` des nœuds existants à leur nouveau
              `text_content`.
            </p>

            {!report ? (
              <form onSubmit={handleImport} className="mt-4">
                <div className="mb-4">
                  <label
                    htmlFor="file-upload"
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    Sélectionnez le fichier JSON (.json)
                  </label>
                  <input
                    id="file-upload"
                    type="file"
                    accept=".json"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    className="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none p-2"
                    disabled={isLoading}
                  />
                  {file && (
                    <p className="text-xs text-indigo-600 mt-1">Fichier prêt : {file.name}</p>
                  )}
                </div>

                {error && (
                  <div
                    className="bg-red-100 border-l-4 border-red-500 text-red-700 p-3 mb-4 text-sm"
                    role="alert"
                  >
                    <p>{error}</p>
                  </div>
                )}

                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    type="button"
                    onClick={onClose}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                    disabled={isLoading}
                  >
                    Annuler
                  </button>
                  <button
                    type="submit"
                    disabled={!file || isLoading}
                    className={`px-4 py-2 text-sm font-medium text-white rounded-md transition ${
                      !file || isLoading
                        ? 'bg-indigo-300 cursor-not-allowed'
                        : 'bg-indigo-600 hover:bg-indigo-700'
                    }`}
                  >
                    {isLoading ? 'Importation...' : "Lancer l'Importation"}
                  </button>
                </div>
              </form>
            ) : (
              // Success Report View
              <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
                <h4 className="text-lg font-semibold text-green-700">Importation Réussie !</h4>
                <p className="mt-2 text-sm text-gray-700">
                  <span className="font-bold">{report.updated_count}</span> nœud(s) mis à jour avec
                  succès.
                </p>
                {report.ignored_ids.length > 0 && (
                  <div className="mt-3">
                    <p className="text-sm font-medium text-yellow-700">
                      <span className="font-bold">{report.ignored_ids.length}</span> ID(s) ignoré(s)
                      (non trouvés):
                    </p>
                    <ul className="list-disc list-inside mt-1 text-xs text-gray-600 max-h-20 overflow-y-auto p-1 bg-white border rounded">
                      {report.ignored_ids.map((id, index) => (
                        <li key={index}>{id}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className="flex justify-end mt-4">
                  <button
                    type="button"
                    onClick={onClose}
                    className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700"
                  >
                    Fermer
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ImportContentModal