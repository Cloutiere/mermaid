// frontend/src/pages/ProjectListPage.tsx
import { useEffect, useState } from 'react'
import type { BackendHealthResponse } from '../types/api' // Assurez-vous que le type est bien défini ici ou dans un fichier type global

function ProjectListPage() {
  const [backendStatus, setBackendStatus] = useState<string>('checking...')

  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then((data: BackendHealthResponse) => {
        // Supposition que BackendHealthResponse est { message: string }
        setBackendStatus(data.message)
      })
      .catch(() => setBackendStatus('Backend not reachable'))
  }, [])

  return (
    <div className="p-8">
      <h1 className="text-4xl font-extrabold text-gray-900 mb-6">
        Liste des Projets (Page d'Accueil)
      </h1>
      <p className="text-lg text-gray-600 mb-8">
        Bienvenue dans l'Éditeur Visuel de Structure Narrative Mermaid.
      </p>

      <div className="bg-blue-50 border-l-4 border-blue-500 p-4 shadow-md">
        <p className="text-sm text-blue-700">
          <strong>Backend Status (Health Check):</strong> {backendStatus}
        </p>
      </div>

      <div className="mt-8">
        <h2 className="text-2xl font-semibold text-gray-800">
          Projets Actuels
        </h2>
        {/* Placeholder pour la liste des projets */}
        <div className="mt-4 p-4 border rounded-lg bg-white">
          <p className="text-gray-500">
            [Future liste des projets ici. Cliquer sur un projet mènera à l'éditeur.]
          </p>
        </div>
      </div>
    </div>
  )
}

export default ProjectListPage