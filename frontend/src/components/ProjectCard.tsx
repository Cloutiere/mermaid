// frontend/src/components/ProjectCard.tsx
// Version 1.1 - Intégration du CRUD des SubProjects

import { useState } from 'react'
import type { ProjectRead } from '../types/api'
import SubProjectCard from './SubProjectCard'
import SubProjectForm from './SubProjectForm'
import { Plus } from 'lucide-react'

interface ProjectCardProps {
  project: ProjectRead
  onDelete: (id: number) => Promise<void>
  onProjectUpdate: () => void // Nouvelle prop pour rafraîchir la liste globale
}

function ProjectCard({ project, onDelete, onProjectUpdate }: ProjectCardProps) {
  const [showSubProjectForm, setShowSubProjectForm] = useState(false)

  const handleDelete = () => {
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer le projet "${project.title}" et tous ses sous-projets ?`)) {
      onDelete(project.id)
    }
  }

  // Gère la fin du formulaire de création/modification de SubProject
  const handleSubProjectFormSuccess = () => {
    setShowSubProjectForm(false)
    onProjectUpdate() // Force le rafraîchissement de ProjectListPage pour mettre à jour la liste des subprojects.
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
        <div className="flex justify-between items-center mb-3">
            <h4 className="text-lg font-semibold text-gray-700">Sous-Projets ({project.subprojects.length}) :</h4>
            <button
                onClick={() => setShowSubProjectForm(true)}
                title="Ajouter un nouveau sous-projet"
                className="p-1 text-indigo-600 hover:text-indigo-800 rounded-full hover:bg-indigo-50 transition"
            >
                <Plus size={20} />
            </button>
        </div>

        {/* Affichage du Formulaire de Création */}
        {showSubProjectForm && (
            <div className="mb-4">
                <SubProjectForm 
                    projectId={project.id}
                    onSuccess={handleSubProjectFormSuccess}
                    onCancel={() => setShowSubProjectForm(false)}
                />
            </div>
        )}

        {/* Liste des Sous-Projets existants */}
        {project.subprojects.length > 0 ? (
          <ul className="space-y-2">
            {project.subprojects.map((subproject) => (
              <SubProjectCard 
                key={subproject.id}
                subproject={subproject}
                projectId={project.id}
                onDeleteSuccess={onProjectUpdate} // Rafraîchit après suppression
              />
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-500 italic py-2">
            Aucun sous-projet. Utilisez le bouton '+' ci-dessus pour en créer un.
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