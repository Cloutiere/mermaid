// frontend/src/App.tsx
// Version 1.0

import { useEffect, useState } from 'react'
import type { BackendHealthResponse } from './types/api' // Utilisation de 'import type' selon la règle N°2

function App() {
  const [backendStatus, setBackendStatus] = useState<string>('checking...')

  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then((data: BackendHealthResponse) => setBackendStatus(data.message)) // Typage de la réponse
      .catch(() => setBackendStatus('Backend not reachable'))
  }, [])

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-2xl w-full">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">
          Éditeur Visuel de Structure Narrative Mermaid
        </h1>
        <p className="text-gray-600 mb-4">
          Architecture: Python/Flask + React/TypeScript + PostgreSQL
        </p>
        <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
          <p className="text-sm text-blue-700">
            <strong>Backend Status:</strong> {backendStatus}
          </p>
        </div>
        <div className="mt-6 text-sm text-gray-500">
          <p>L'environnement est configuré et prêt.</p>
          <p className="mt-2">Consultez le README.md pour les instructions de développement.</p>
        </div>
      </div>
    </div>
  )
}

export default App