// frontend/src/components/SubgraphManagerModal.tsx
// Version 1.0

import type React from 'react'
import { useState, useEffect, useCallback, useMemo } from 'react'
import apiService from '@/services/api'
import type { SubProjectRead, SubgraphRead, NodeRead, ClassDefRead } from '@/types/api'
import ConfirmDialog from './ConfirmDialog'

interface SubgraphManagerModalProps {
  isOpen: boolean
  onClose: () => void
  onUpdateSuccess: () => void
  subprojectId: number
}

// Initial state for the form
const getInitialFormData = () => ({
  title: '',
  style_class_ref: '', // Empty string for 'none'
})

function SubgraphManagerModal({
  isOpen,
  onClose,
  onUpdateSuccess,
  subprojectId
}: SubgraphManagerModalProps) {
  // --- State Management ---
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [subproject, setSubproject] = useState<SubProjectRead | null>(null)
  const [classDefs, setClassDefs] = useState<ClassDefRead[]>([])

  const [isEditing, setIsEditing] = useState<SubgraphRead | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  const [formData, setFormData] = useState(getInitialFormData())
  const [selectedNodeIds, setSelectedNodeIds] = useState<Set<number>>(new Set())

  const [subgraphToDelete, setSubgraphToDelete] = useState<SubgraphRead | null>(null)

  // --- Data Fetching ---
  const fetchData = useCallback(async () => {
    if (!isOpen) return
    setLoading(true)
    setError(null)
    try {
      const [subprojectData, classDefsData] = await Promise.all([
        apiService.getSubProject(subprojectId),
        apiService.getClassDefs(subprojectId)
      ])
      setSubproject(subprojectData)
      setClassDefs(classDefsData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data.')
    } finally {
      setLoading(false)
    }
  }, [isOpen, subprojectId])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // --- Form & Selection Logic ---
  const resetFormAndSelection = useCallback(() => {
    setIsEditing(null)
    setFormData(getInitialFormData())
    setSelectedNodeIds(new Set())
  }, [])

  const handleEditClick = useCallback(
    (subgraph: SubgraphRead) => {
      setIsEditing(subgraph)
      setFormData({
        title: subgraph.title,
        style_class_ref: subgraph.style_class_ref || ''
      })
      setSelectedNodeIds(new Set(subgraph.nodes.map((node) => node.id)))
    },
    []
  )

  const handleNodeSelectionChange = (nodeId: number) => {
    setSelectedNodeIds((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(nodeId)) {
        newSet.delete(nodeId)
      } else {
        newSet.add(nodeId)
      }
      return newSet
    })
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!formData.title) {
      setError('Title is required.')
      return
    }

    setIsSaving(true)
    setError(null)

    try {
      const node_ids = Array.from(selectedNodeIds)

      if (isEditing) {
        // --- UPDATE LOGIC ---
        // 1. Update metadata (title, style)
        await apiService.updateSubgraph(isEditing.id, {
          title: formData.title,
          style_class_ref: formData.style_class_ref || null
        })
        // 2. Assign nodes (this replaces the old set of nodes)
        await apiService.assignNodesToSubgraph(isEditing.id, node_ids)
      } else {
        // --- CREATE LOGIC ---
        await apiService.createSubgraph({
          subproject_id: subprojectId,
          title: formData.title,
          style_class_ref: formData.style_class_ref || null,
          node_ids
        })
      }

      onUpdateSuccess() // Trigger refetch on parent page
      resetFormAndSelection()
      await fetchData() // Re-fetch data for the modal itself
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during save.')
    } finally {
      setIsSaving(false)
    }
  }

  // --- Deletion Logic ---
  const handleDeleteClick = (subgraph: SubgraphRead) => {
    setSubgraphToDelete(subgraph)
  }

  const handleConfirmDelete = async () => {
    if (!subgraphToDelete) return

    setIsSaving(true)
    setError(null)
    try {
      await apiService.deleteSubgraph(subgraphToDelete.id)
      onUpdateSuccess()
      setSubgraphToDelete(null)
      // If the deleted subgraph was being edited, reset the form
      if (isEditing && isEditing.id === subgraphToDelete.id) {
        resetFormAndSelection()
      }
      await fetchData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete subgraph.')
    } finally {
      setIsSaving(false)
    }
  }

  const sortedNodes = useMemo(() => {
    return subproject?.nodes?.slice().sort((a, b) => a.mermaid_id.localeCompare(b.mermaid_id)) || []
  }, [subproject?.nodes])

  if (!isOpen) return null

  // --- Render ---
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60">
      <div className="relative mx-4 my-8 h-[90vh] w-full max-w-5xl rounded-lg bg-white shadow-xl">
        <header className="flex items-center justify-between border-b border-gray-200 p-4">
          <h2 className="text-xl font-semibold text-gray-800">Manage Subgraphs</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Close"
          >
            <svg
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </header>

        <main className="flex h-[calc(90vh-120px)] overflow-hidden">
          {loading ? (
            <div className="flex w-full items-center justify-center">
              <p className="text-indigo-600">Loading data...</p>
            </div>
          ) : error && !isSaving ? (
            <div className="w-full p-4 text-center text-red-600">{error}</div>
          ) : (
            <>
              {/* Left Panel: List of Subgraphs */}
              <div className="w-1/3 overflow-y-auto border-r border-gray-200 p-4">
                <button
                  onClick={resetFormAndSelection}
                  className="mb-4 w-full rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:bg-indigo-300"
                  disabled={isSaving}
                >
                  + Create New Subgraph
                </button>
                <ul className="space-y-2">
                  {subproject?.subgraphs?.map((sg) => (
                    <li
                      key={sg.id}
                      className={`rounded-md p-3 transition-colors ${
                        isEditing?.id === sg.id
                          ? 'bg-indigo-100 ring-2 ring-indigo-500'
                          : 'bg-gray-50 hover:bg-gray-100'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold text-gray-800">{sg.title}</p>
                          <p className="text-xs text-gray-500">
                            ID: {sg.mermaid_id} &bull; Nodes: {sg.nodes.length}
                          </p>
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleEditClick(sg)}
                            className="text-gray-500 hover:text-indigo-600"
                            disabled={isSaving}
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteClick(sg)}
                            className="text-gray-500 hover:text-red-600"
                            disabled={isSaving}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Right Panel: Form for Create/Edit */}
              <div className="flex w-2/3 flex-col p-4">
                <h3 className="mb-4 text-lg font-semibold text-gray-700">
                  {isEditing ? `Editing "${isEditing.title}"` : 'Create New Subgraph'}
                </h3>
                <form onSubmit={handleSubmit} className="flex flex-grow flex-col overflow-hidden">
                  {/* Form fields */}
                  <div className="space-y-4">
                    <div>
                      <label
                        htmlFor="title"
                        className="block text-sm font-medium text-gray-700"
                      >
                        Title
                      </label>
                      <input
                        type="text"
                        id="title"
                        value={formData.title}
                        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        required
                      />
                    </div>
                    <div>
                      <label
                        htmlFor="style_class_ref"
                        className="block text-sm font-medium text-gray-700"
                      >
                        Style Class
                      </label>
                      <select
                        id="style_class_ref"
                        value={formData.style_class_ref}
                        onChange={(e) =>
                          setFormData({ ...formData, style_class_ref: e.target.value })
                        }
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      >
                        <option value="">-- No Style --</option>
                        {classDefs.map((cd) => (
                          <option key={cd.id} value={cd.name}>
                            {cd.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Node Selection */}
                  <div className="mt-6 flex flex-grow flex-col overflow-hidden">
                    <h4 className="mb-2 font-medium text-gray-700">Assign Nodes</h4>
                    <div className="flex-grow overflow-y-auto rounded-md border border-gray-300 p-2">
                      <div className="grid grid-cols-2 gap-x-4 gap-y-2 sm:grid-cols-3">
                        {sortedNodes.map((node) => (
                          <div key={node.id} className="flex items-center">
                            <input
                              type="checkbox"
                              id={`node-${node.id}`}
                              checked={selectedNodeIds.has(node.id)}
                              onChange={() => handleNodeSelectionChange(node.id)}
                              className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                            />
                            <label
                              htmlFor={`node-${node.id}`}
                              className="ml-2 block truncate text-sm text-gray-900"
                              title={node.title || node.mermaid_id}
                            >
                              {node.mermaid_id} ({node.title || 'No title'})
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  {error && isSaving && <p className="mt-2 text-sm text-red-600">{error}</p>}
                  {/* Actions */}
                  <div className="mt-4 flex justify-end space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={resetFormAndSelection}
                      className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:bg-gray-200"
                      disabled={isSaving}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:bg-indigo-400"
                      disabled={isSaving}
                    >
                      {isSaving ? 'Saving...' : isEditing ? 'Save Changes' : 'Create Subgraph'}
                    </button>
                  </div>
                </form>
              </div>
            </>
          )}
        </main>
      </div>
      <ConfirmDialog
        isOpen={!!subgraphToDelete}
        onClose={() => setSubgraphToDelete(null)}
        onConfirm={handleConfirmDelete}
        title="Delete Subgraph"
        message={`Are you sure you want to delete the subgraph "${subgraphToDelete?.title}"? All nodes within it will be unassigned.`}
        isDestructive
        confirmText="Delete"
      />
    </div>
  )
}

export default SubgraphManagerModal