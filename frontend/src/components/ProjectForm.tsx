// frontend/src/components/ProjectForm.tsx
// Version 1.0

import { useState } from 'react'
import type { ProjectCreate } from '../types/api'
import apiService from '../services/api'

interface ProjectFormProps {
  onSuccess: () => void
  onCancel: () => void
}

function ProjectForm({ onSuccess, onCancel }: ProjectFormProps) {
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!title.trim()) {
      setError('Le titre du projet ne peut pas être vide.')
      return
    }

    setLoading(true)
    setError(null)

    // Le type ProjectCreate est équivalent à { title: string }
    const projectData: ProjectCreate = { title: title.trim() }

    try {
      // apiService.createProject est typé pour accepter le payload sans 'id'/'subprojects'
      await apiService.createProject(projectData)
      setTitle('')
      onSuccess() // Notifie le parent du succès pour rafraîchir la liste
    } catch (err: any) {
      setError(err.message || 'Échec de la création du projet.')
      console.error('Erreur de création de projet:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 bg-white border border-indigo-200 rounded-lg shadow-xl">
      <h3 className="text-xl font-semibold mb-4 text-indigo-700">Créer un Nouveau Projet</h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="projectTitle" className="block text-sm font-medium text-gray-700">
            Titre du Projet
          </label>
          <input
            id="projectTitle"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={loading}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
            placeholder="Ex: La Saga des Étoiles Oubliées"
            required
          />
        </div>

        {error && (
          <p className="text-sm text-red-600 bg-red-50 p-2 rounded">{error}</p>
        )}

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Annuler
          </button>
          <button
            type="submit"
            disabled={loading}
            className="py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {loading ? 'Création...' : 'Créer'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default ProjectForm