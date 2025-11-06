// frontend/src/components/SubProjectCard.tsx
// Version 1.1 (Correction: Ajout de l'import useState)

import { useState } from 'react' // <-- Correction: useState manquait
import { useNavigate } from 'react-router-dom'
import type { SubProjectRead } from '../types/api'
import apiService from '../services/api'
import { Trash2 } from 'lucide-react'

interface SubProjectCardProps {
  subproject: SubProjectRead
  projectId: number
  onDeleteSuccess: () => void
}

function SubProjectCard({ subproject, projectId, onDeleteSuccess }: SubProjectCardProps) {
  const navigate = useNavigate()
  const [isDeleting, setIsDeleting] = useState(false)

  const handleOpenEditor = () => {
    // Navigation vers l'éditeur de graphe: /project/:projectId/subproject/:subprojectId
    navigate(`/project/${projectId}/subproject/${subproject.id}`)
  }

  const handleDelete = async () => {
    if (isDeleting) return // Empêche le double clic

    const confirmation = window.confirm(
      `Êtes-vous sûr de vouloir supprimer le sous-projet "${subproject.title}" (ID: ${subproject.id}) ? Cette action est irréversible et supprimera tous les Nœuds et Relations associés.`
    )

    if (confirmation) {
      setIsDeleting(true)
      try {
        await apiService.deleteSubProject(subproject.id)
        // Informe le parent (ProjectCard) qui informera le grand-parent (ProjectListPage)
        onDeleteSuccess()
      } catch (err: any) {
        alert(err.message || 'Échec de la suppression du sous-projet.')
        console.error("Erreur lors de la suppression du SubProject:", err)
      } finally {
        setIsDeleting(false)
      }
    }
  }

  return (
    <li className="flex justify-between items-center p-3 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition duration-150 group">
      {/* Informations et lien de navigation */}
      <div 
        className="flex-grow min-w-0 cursor-pointer"
        onClick={handleOpenEditor}
        title={`Ouvrir l'éditeur pour : ${subproject.title}`}
      >
        <span className="text-gray-800 hover:text-indigo-600 font-medium transition truncate block">
          {subproject.title}
        </span>
        <span className="text-xs text-gray-400">ID: {subproject.id}</span>
      </div>

      {/* Actions */}
      <div className="flex space-x-2 items-center ml-4">
        <button
          onClick={handleOpenEditor}
          className="text-sm px-3 py-1 font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 transition duration-150 disabled:opacity-50"
          disabled={isDeleting}
        >
          {isDeleting ? 'Patientez...' : 'Ouvrir l\'Éditeur'}
        </button>

        <button
          onClick={handleDelete}
          disabled={isDeleting}
          title="Supprimer ce sous-projet"
          className="p-2 text-red-500 hover:text-red-700 hover:bg-red-100 rounded-full transition duration-150 disabled:opacity-50"
        >
          <Trash2 size={16} />
        </button>
      </div>
    </li>
  )
}

export default SubProjectCard