// frontend/src/components/ProjectCard.tsx
// Version 1.2 - Intégration de ConfirmDialog pour la suppression

import { useState } from 'react'
import type { ProjectRead } from '../types/api'
import SubProjectCard from './SubProjectCard'
import SubProjectForm from './SubProjectForm'
import ConfirmDialog from './ConfirmDialog' // Importation
import { Plus } from 'lucide-react'

interface ProjectCardProps {
  project: ProjectRead
  onDelete: (id: number) => Promise<void>
  onProjectUpdate: () => void
}

function ProjectCard({ project, onDelete, onProjectUpdate }: ProjectCardProps) {
  const [showSubProjectForm, setShowSubProjectForm] = useState(false)
  const [showConfirmDelete, setShowConfirmDelete] = useState(false) // État pour la modale

  const handleDeleteRequest = () => {
    setShowConfirmDelete(true) // Ouvre la modale au lieu de confirmer directement
  }

  const handleConfirmDelete = async () => {
    await onDelete(project.id)
    setShowConfirmDelete(false)
  }

  const handleCancelDelete = () => {
    setShowConfirmDelete(false)
  }

  const handleSubProjectFormSuccess = () => {
    setShowSubProjectForm(false)
    onProjectUpdate()
  }

  return (
    <>
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

          {showSubProjectForm && (
              <div className="mb-4">
                  <SubProjectForm 
                      projectId={project.id}
                      onSuccess={handleSubProjectFormSuccess}
                      onCancel={() => setShowSubProjectForm(false)}
                  />
              </div>
          )}

          {project.subprojects.length > 0 ? (
            <ul className="space-y-2">
              {project.subprojects.map((subproject) => (
                <SubProjectCard 
                  key={subproject.id}
                  subproject={subproject}
                  projectId={project.id}
                  onDeleteSuccess={onProjectUpdate}
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
            onClick={handleDeleteRequest} // Modifié pour ouvrir la modale
            className="text-sm font-medium text-red-600 hover:text-red-800 transition duration-150 p-2 rounded-md hover:bg-red-50"
          >
            Supprimer le Projet
          </button>
        </div>
      </div>

      {/* Modale de Confirmation */}
      <ConfirmDialog
        isOpen={showConfirmDelete}
        onClose={handleCancelDelete}
        onConfirm={handleConfirmDelete}
        title="Supprimer le Projet"
        message={`Êtes-vous sûr de vouloir supprimer le projet "${project.title}" et tous ses sous-projets ? Cette action est irréversible.`}
        isDestructive={true}
        confirmText="Supprimer"
      />
    </>
  )
}

export default ProjectCard