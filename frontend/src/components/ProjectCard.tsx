// frontend/src/components/ProjectCard.tsx
// Version 1.0

import { useNavigate } from 'react-router-dom'
import type { ProjectRead } from '../types/api'

interface ProjectCardProps {
  project: ProjectRead
  onDelete: (id: number) => Promise<void>
}

function ProjectCard({ project, onDelete }: ProjectCardProps) {
  const navigate = useNavigate()

  const handleDelete = () => {
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer le projet "${project.title}" et tous ses sous-projets ?`)) {
      onDelete(project.id)
    }
  }

  const handleSubProjectClick = (subprojectId: number) => {
    // Navigation vers l'éditeur de graphe
    navigate(`/project/${project.id}/subproject/${subprojectId}`)
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-lg hover:shadow-xl transition duration-300 flex flex-col">
      {/* En-tête du Projet */}
      <div className="p-5 border-b border-gray-200">
        <h3 className="text-2xl font-bold text-gray-900 truncate">{project.title}</h3>
        <p className="text-sm text-gray-500 mt-1">ID Projet: {project.id}</p>
      </div>

      {/* Liste des Sous-Projets */}
      <div className="flex-grow p-5 space-y-3">
        <h4 className="text-lg font-semibold text-gray-700">Sous-Projets ({project.subprojects.length}) :</h4>

        {project.subprojects.length > 0 ? (
          <ul className="space-y-2">
            {project.subprojects.map((subproject) => (
              <li key={subproject.id} className="flex justify-between items-center">
                <span 
                  className="text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer transition truncate"
                  onClick={() => handleSubProjectClick(subproject.id)}
                  title={`Ouvrir: ${subproject.title}`}
                >
                  {subproject.title}
                </span>
                <span className="text-xs text-gray-400">ID: {subproject.id}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-500 italic">
            Aucun sous-projet. <span className="text-indigo-500 font-medium cursor-pointer">Créer le premier.</span>
            {/* L'action de création sera implémentée ultérieurement */}
          </p>
        )}
      </div>

      {/* Actions */}
      <div className="p-5 border-t border-gray-200 flex justify-end">
        <button
          onClick={handleDelete}
          className="text-sm font-medium text-red-600 hover:text-red-800 transition duration-150 p-2 rounded-md hover:bg-red-50"
        >
          Supprimer le Projet
        </button>
      </div>
    </div>
  )
}

export default ProjectCard