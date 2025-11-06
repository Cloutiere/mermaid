// frontend/src/components/SubProjectCard.tsx
// Version 1.2 (Intégration de ConfirmDialog pour la suppression)

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { SubProjectRead } from '../types/api'
import apiService from '../services/api'
import { Trash2 } from 'lucide-react'
import ConfirmDialog from './ConfirmDialog' // Importation

interface SubProjectCardProps {
  subproject: SubProjectRead
  projectId: number
  onDeleteSuccess: () => void
}

function SubProjectCard({ subproject, projectId, onDeleteSuccess }: SubProjectCardProps) {
  const navigate = useNavigate()
  const [isDeleting, setIsDeleting] = useState(false)
  const [showConfirmDelete, setShowConfirmDelete] = useState(false) // État pour la modale

  const handleOpenEditor = () => {
    navigate(`/project/${projectId}/subproject/${subproject.id}`)
  }

  const handleDeleteRequest = () => {
    if (isDeleting) return
    setShowConfirmDelete(true) // Ouvre la modale
  }

  const handleConfirmDelete = async () => {
    setShowConfirmDelete(false) // Ferme la modale
    setIsDeleting(true)
    try {
      await apiService.deleteSubProject(subproject.id)
      onDeleteSuccess()
    } catch (err: any) {
      alert(err.message || 'Échec de la suppression du sous-projet.')
      console.error("Erreur lors de la suppression du SubProject:", err)
    } finally {
      setIsDeleting(false)
    }
  }

  const handleCancelDelete = () => {
    setShowConfirmDelete(false)
  }

  return (
    <>
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
            onClick={handleDeleteRequest} // Modifié pour ouvrir la modale
            disabled={isDeleting}
            title="Supprimer ce sous-projet"
            className="p-2 text-red-500 hover:text-red-700 hover:bg-red-100 rounded-full transition duration-150 disabled:opacity-50"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </li>

      {/* Modale de Confirmation */}
      <ConfirmDialog
        isOpen={showConfirmDelete}
        onClose={handleCancelDelete}
        onConfirm={handleConfirmDelete}
        title="Supprimer le Sous-Projet"
        message={`Êtes-vous sûr de vouloir supprimer le sous-projet "${subproject.title}" ? Cette action est irréversible et supprimera tous les Nœuds et Relations associés.`}
        isDestructive={true}
        confirmText="Supprimer"
      />
    </>
  )
}

export default SubProjectCard