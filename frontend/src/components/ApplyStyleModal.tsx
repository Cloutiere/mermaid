// frontend/src/components/ApplyStyleModal.tsx
// Version 1.2 (Simplification de l'affichage des nœuds)

import { useState, useEffect, useCallback, useMemo } from 'react'
import apiService from '@/services/api'
import type { NodeRead, ClassDefRead } from '@/types/api'

interface ApplyStyleModalProps {
  isOpen: boolean
  onClose: () => void
  subprojectId: number
  onApplySuccess: () => void
}

function ApplyStyleModal({ isOpen, onClose, subprojectId, onApplySuccess }: ApplyStyleModalProps) {
  // Data states
  const [nodes, setNodes] = useState<NodeRead[]>([])
  const [classDefs, setClassDefs] = useState<ClassDefRead[]>([])

  // UI/Control states
  const [selectedNodeId, setSelectedNodeId] = useState<string>('')
  const [selectedStyleName, setSelectedStyleName] = useState<string>('')
  const [filterStyle, setFilterStyle] = useState<string>('ALL') // 'ALL', 'NONE', ou style_name
  const [isLoading, setIsLoading] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    if (!subprojectId) return
    setIsLoading(true)
    setError(null)
    try {
      const [nodesData, classDefsData] = await Promise.all([
        apiService.getNodes(subprojectId),
        apiService.getClassDefs(subprojectId),
      ])

      // Tri des nœuds par mermaid_id (alphabétique)
      const sortedNodes = nodesData.sort((a, b) => a.mermaid_id.localeCompare(b.mermaid_id))
      setNodes(sortedNodes)
      setClassDefs(classDefsData)

      // Réinitialiser la sélection si l'ID sélectionné n'est plus pertinent
      if (selectedNodeId && !sortedNodes.some(n => n.id.toString() === selectedNodeId)) {
        setSelectedNodeId('');
      }

    } catch (err) {
      console.error('Failed to load data for style application:', err)
      setError(err instanceof Error ? err.message : 'An unknown error occurred.')
    } finally {
      setIsLoading(false)
    }
  }, [subprojectId, selectedNodeId])

  useEffect(() => {
    if (isOpen) {
      // Reset state on open
      setSelectedNodeId('')
      setSelectedStyleName('')
      setFilterStyle('ALL') 
      setError(null)
      fetchData()
    }
  }, [isOpen, fetchData])

  // Logique de filtrage des nœuds affichés
  const filteredNodes = useMemo(() => {
    if (filterStyle === 'ALL') {
      return nodes
    }
    if (filterStyle === 'NONE') {
      return nodes.filter(node => !node.style_class_ref)
    }
    return nodes.filter(node => node.style_class_ref === filterStyle)
  }, [nodes, filterStyle])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedNodeId) {
      setError('Please select a target node.')
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      const nodeId = parseInt(selectedNodeId, 10)
      const payload = {
        style_name: selectedStyleName || null, // Empty string becomes null
      }
      await apiService.patchNodeStyle(nodeId, payload)
      onApplySuccess()
      onClose()
    } catch (err) {
      console.error('Failed to apply style:', err)
      setError(err instanceof Error ? err.message : 'An unknown error occurred during submission.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 transition-opacity"
      aria-labelledby="modal-title"
      role="dialog"
      aria-modal="true"
    >
      <div className="relative w-full max-w-lg transform rounded-xl bg-white p-6 shadow-2xl transition-all">
        <div className="flex items-start justify-between">
          <h2 id="modal-title" className="text-xl font-bold text-gray-800">
            Appliquer un Style à un Nœud
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Fermer"
          >
            <svg
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="mt-4">
          {error && (
            <div className="mb-4 rounded-md border border-red-200 bg-red-50 p-3">
              <p className="text-sm font-medium text-red-700">{error}</p>
            </div>
          )}

          {isLoading ? (
            <div className="flex justify-center items-center py-8">
              <p className="text-gray-500">Chargement des données...</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">

              {/* Filtre des Nœuds */}
              <div>
                <label htmlFor="style-filter" className="block text-sm font-medium text-gray-700">
                  Filtrer par Style Attribué
                </label>
                <select
                  id="style-filter"
                  value={filterStyle}
                  onChange={(e) => {
                      setFilterStyle(e.target.value)
                      setSelectedNodeId('') // Réinitialiser la sélection lors du changement de filtre
                  }}
                  className="mt-1 block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
                >
                  <option value="ALL">Tous les nœuds ({nodes.length})</option>
                  <option value="NONE">Nœuds sans style attribué ({nodes.filter(n => !n.style_class_ref).length})</option>
                  {classDefs.map((def) => {
                      const count = nodes.filter(n => n.style_class_ref === def.name).length
                      return (
                          <option key={def.id} value={def.name}>
                              Style: {def.name} ({count})
                          </option>
                      )
                  })}
                </select>
              </div>

              {/* Sélection du Nœud Cible */}
              <div>
                <label htmlFor="node-select" className="block text-sm font-medium text-gray-700">
                  Nœud Cible (Filtré : {filteredNodes.length})
                </label>
                <select
                  id="node-select"
                  value={selectedNodeId}
                  onChange={(e) => {
                      setSelectedNodeId(e.target.value)
                      const node = nodes.find(n => n.id.toString() === e.target.value)
                      setSelectedStyleName(node?.style_class_ref || '')
                  }}
                  className="mt-1 block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
                  disabled={filteredNodes.length === 0}
                >
                  <option value="" disabled>
                    {filteredNodes.length > 0 ? 'Sélectionner un nœud' : 'Aucun nœud correspondant au filtre'}
                  </option>
                  {filteredNodes.map((node) => (
                    <option key={node.id} value={node.id}>
                      {node.mermaid_id}
                      {/* Affichage du style uniquement s'il est présent */}
                      {node.style_class_ref ? ` [Style: ${node.style_class_ref}]` : ''} 
                    </option>
                  ))}
                </select>
              </div>

              {/* Sélection du Style à Appliquer */}
              <div>
                <label htmlFor="style-select" className="block text-sm font-medium text-gray-700">
                  Style à Appliquer (Actuel sur la sélection : {selectedStyleName || 'Aucun'})
                </label>
                <select
                  id="style-select"
                  value={selectedStyleName}
                  onChange={(e) => setSelectedStyleName(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
                  disabled={classDefs.length === 0}
                >
                  <option value="">-- Retirer le Style --</option>
                  {classDefs.length > 0 ? (
                    classDefs.map((def) => (
                      <option key={def.id} value={def.name}>
                        {def.name}
                      </option>
                    ))
                  ) : (
                    <option disabled>Aucun style défini</option>
                  )}
                </select>
              </div>

              <div className="flex justify-end space-x-3 border-t pt-4 mt-6">
                <button
                  type="button"
                  onClick={onClose}
                  className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={!selectedNodeId || isSubmitting}
                  className="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:bg-indigo-300"
                >
                  {isSubmitting ? 'Application...' : 'Appliquer'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}

export default ApplyStyleModal