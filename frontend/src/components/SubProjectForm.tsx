// frontend/src/components/SubProjectForm.tsx
// Version 1.0

import { useState } from 'react'
import type { SubProjectRead } from '../types/api'
import apiService from '../services/api'

const DEFAULT_MERMAID = `graph TD
    A[Début] --> B[Milieu]
    B --> C[Fin]`

interface SubProjectFormProps {
  projectId: number
  onSuccess: (newSubProject: SubProjectRead) => void
  onCancel: () => void
}

function SubProjectForm({ projectId, onSuccess, onCancel }: SubProjectFormProps) {
  const [title, setTitle] = useState<string>('')
  const [mermaidCode, setMermaidCode] = useState<string>(DEFAULT_MERMAID)
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!title.trim()) {
      setError('Le titre du sous-projet est obligatoire.')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const payload = {
        title: title,
        project_id: projectId,
        mermaid_definition: mermaidCode,
        visual_layout: null, // Initialisé à null
      }

      // Utilise apiService.createSubProject avec le payload de type SubProjectCreate
      const newSubProject = await apiService.createSubProject(payload)
      onSuccess(newSubProject)

      // Réinitialisation optionnelle (si le formulaire devait rester ouvert)
      setTitle('')
      setMermaidCode(DEFAULT_MERMAID)
    } catch (err: any) {
      setError(err.message || 'Échec de la création du sous-projet.')
      console.error('Erreur de création de SubProject:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 bg-white border border-indigo-200 rounded-lg shadow-inner">
      <h4 className="text-xl font-semibold mb-4 text-indigo-700">
        Créer un nouveau Sous-Projet (Livre/Graphe)
      </h4>
      {error && (
        <div className="p-3 mb-4 bg-red-100 border border-red-400 text-red-700 text-sm rounded-md">
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700">
            Titre du Sous-Projet
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Ex: Acte I - La Montée en Puissance"
            disabled={loading}
          />
        </div>

        <div>
          <label htmlFor="mermaidCode" className="block text-sm font-medium text-gray-700">
            Définition initiale Mermaid (facultatif)
          </label>
          <textarea
            id="mermaidCode"
            rows={5}
            value={mermaidCode}
            onChange={(e) => setMermaidCode(e.target.value)}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 font-mono text-sm focus:ring-indigo-500 focus:border-indigo-500"
            disabled={loading}
          />
        </div>

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md shadow-sm hover:bg-gray-200 disabled:opacity-50"
          >
            Annuler
          </button>
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400"
          >
            {loading ? 'Création...' : 'Créer le Sous-Projet'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default SubProjectForm