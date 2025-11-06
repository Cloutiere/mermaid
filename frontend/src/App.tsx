// frontend/src/App.tsx
// Version 1.1

import { Routes, Route } from 'react-router-dom'
import ProjectListPage from './pages/ProjectListPage'
import GraphEditorPage from './pages/GraphEditorPage'

function App() {
  return (
    <Routes>
      {/* Route de l'interface principale : Liste des projets */}
      <Route path="/" element={<ProjectListPage />} />

      {/* Route de l'éditeur : utilise des paramètres dynamiques */}
      <Route
        path="/project/:projectId/subproject/:subprojectId"
        element={<GraphEditorPage />}
      />

      {/* Gérer les routes non définies, rediriger vers la liste des projets */}
      <Route path="*" element={<ProjectListPage />} />
    </Routes>
  )
}

export default App