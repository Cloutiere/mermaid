// frontend/src/pages/ProjectListPage.tsx
// Version 1.1

import { useEffect, useState, useCallback } from 'react'
import type { BackendHealthResponse, ProjectRead } from '../types/api' // Import type pour les types de données
import apiService from '../services/api' // Import de l'instance du service API

function ProjectListPage() {
  // 1. États pour le Health Check (existant)
  const [backendStatus, setBackendStatus] = useState<string>('checking...')

  // 2. Nouveaux États pour les Projets
  const [projects, setProjects] = useState<ProjectRead[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // Fonction pour vérifier la santé du backend (conservation de la logique existante)
  const fetchHealthStatus = useCallback(() => {
    apiService.getHealth()
      .then((data: BackendHealthResponse) => {
        setBackendStatus(data.message)
      })
      .catch(() => setBackendStatus('Backend not reachable'))
  }, [])

  // Fonction pour charger la liste des projets
  const fetchProjects = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiService.getProjects()
      setProjects(data)
    } catch (err: any) {
      // Gère les erreurs renvoyées par apiService.handleError
      setError(err.message || 'Une erreur inconnue est survenue lors du chargement des projets.')
      console.error("Erreur lors du chargement des projets:", err)
    } finally {
      setLoading(false)
    }
  }, [])

  // Lancement des appels API au montage du composant
  useEffect(() => {
    fetchHealthStatus()
    fetchProjects()
  }, [fetchHealthStatus, fetchProjects]) // Les dépendances sont incluses pour la robustesse

  // --- Rendu conditionnel ---

  const renderProjectListContent = () => {
    if (loading) {
      return (
        <div className="text-center py-10">
          <p className="text-indigo-600 font-medium">Chargement des projets...</p>
        </div>
      )
    }

    if (error) {
      return (
        <div className="p-4 bg-red-100 border-l-4 border-red-500 text-red-700">
          <h3 className="font-bold">Erreur de Chargement</h3>
          <p>{error}</p>
        </div>
      )
    }

    if (projects.length === 0) {
      return (
        <div className="text-center py-10 text-gray-500">
          Aucun projet trouvé. Créez-en un pour commencer.
        </div>
      )
    }

    // Affichage simple du nombre de projets pour l'instant
    return (
      <div className="mt-4 p-4 border rounded-lg bg-white shadow-sm">
        <p className="text-gray-700 font-semibold">
          Projets trouvés : {projects.length}
        </p>
        <ul className="mt-2 space-y-2">
            {/* Future boucle map sur projects pour afficher les liens */}
            {projects.slice(0, 3).map(p => (
                <li key={p.id} className="text-sm text-gray-500 truncate">
                    ID {p.id}: {p.title}
                </li>
            ))}
            {projects.length > 3 && <li className="text-sm text-gray-400">... et {projects.length - 3} autres.</li>}
        </ul>
      </div>
    )
  }

  return (
    <div className="p-8">
      <h1 className="text-4xl font-extrabold text-gray-900 mb-6">
        Liste des Projets (Page d'Accueil)
      </h1>
      <p className="text-lg text-gray-600 mb-8">
        Bienvenue dans l'Éditeur Visuel de Structure Narrative Mermaid.
      </p>

      <div className="bg-blue-50 border-l-4 border-blue-500 p-4 shadow-md mb-8">
        <p className="text-sm text-blue-700">
          <strong>Backend Status (Health Check):</strong> {backendStatus}
        </p>
      </div>

      <div>
        <h2 className="text-2xl font-semibold text-gray-800">
          Projets Actuels
        </h2>
        {renderProjectListContent()}
      </div>
    </div>
  )
}

export default ProjectListPage