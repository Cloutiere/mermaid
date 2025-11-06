// frontend/src/pages/ProjectListPage.tsx
// Version 1.2

import { useEffect, useState, useCallback } from 'react'
import type { BackendHealthResponse, ProjectRead } from '../types/api'
import apiService from '../services/api'
import ProjectForm from '../components/ProjectForm'
import ProjectCard from '../components/ProjectCard'

function ProjectListPage() {
  // 1. États pour le Health Check (existant)
  const [backendStatus, setBackendStatus] = useState<string>('checking...')

  // 2. Nouveaux États pour les Projets
  const [projects, setProjects] = useState<ProjectRead[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // 3. État pour le formulaire de création
  const [showCreateForm, setShowCreateForm] = useState<boolean>(false)

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
      setError(err.message || 'Une erreur inconnue est survenue lors du chargement des projets.')
      console.error("Erreur lors du chargement des projets:", err)
    } finally {
      setLoading(false)
    }
  }, [])

  // Fonction de suppression de projet
  const handleDeleteProject = useCallback(async (projectId: number) => {
    setError(null)
    try {
      // Note: Pas d'état de chargement dédié ici pour la suppression,
      // on compte sur le re-fetch qui mettra l'état global en `loading`.
      await apiService.deleteProject(projectId)
      await fetchProjects() // Rafraîchit la liste
    } catch (err: any) {
      setError(err.message || 'Échec de la suppression du projet.')
      console.error('Erreur de suppression:', err)
    }
  }, [fetchProjects])

  // Gestion du succès de la création
  const handleCreateSuccess = () => {
    setShowCreateForm(false)
    fetchProjects()
  }

  // Lancement des appels API au montage du composant
  useEffect(() => {
    fetchHealthStatus()
    fetchProjects()
  }, [fetchHealthStatus, fetchProjects])

  // --- Rendu conditionnel ---

  const renderProjectListContent = () => {
    if (loading && projects.length === 0) {
      return (
        <div className="text-center py-10">
          <p className="text-indigo-600 font-medium">Chargement des projets...</p>
        </div>
      )
    }

    if (error) {
      return (
        <div className="p-4 bg-red-100 border-l-4 border-red-500 text-red-700 my-4 rounded-md">
          <h3 className="font-bold">Erreur de Chargement ou Opération</h3>
          <p>{error}</p>
        </div>
      )
    }

    if (projects.length === 0 && !loading) {
      return (
        <div className="text-center py-10 text-gray-500 border border-dashed rounded-lg mt-4">
          <p>Aucun projet trouvé.</p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Créer le premier projet
          </button>
        </div>
      )
    }

    // Affichage des cartes de projets
    return (
      <div className="mt-6 grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {projects.map(project => (
          <ProjectCard
            key={project.id}
            project={project}
            onDelete={handleDeleteProject}
          />
        ))}
      </div>
    )
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <header className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-4xl font-extrabold text-gray-900">
            Liste des Projets
          </h1>
          <p className="text-lg text-gray-600 mt-1">
            Gérez ici vos sagas et livres narratifs.
          </p>
        </div>

        {!showCreateForm && (
          <button
            onClick={() => setShowCreateForm(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            + Nouveau Projet
          </button>
        )}
      </header>

      {showCreateForm && (
        <div className="mb-8 max-w-lg">
          <ProjectForm 
            onSuccess={handleCreateSuccess} 
            onCancel={() => setShowCreateForm(false)} 
          />
        </div>
      )}

      <div className="bg-blue-50 border-l-4 border-blue-500 p-4 shadow-md mb-8">
        <p className="text-sm text-blue-700">
          <strong>Backend Status (Health Check):</strong> {backendStatus}
        </p>
      </div>

      <h2 className="text-2xl font-semibold text-gray-800 border-b pb-2">
        Projets Actuels ({projects.length})
      </h2>

      {renderProjectListContent()}
    </div>
  )
}

export default ProjectListPage