// frontend/src/components/StyleManagerModal.tsx
// Version 1.0

import { useState, useEffect, useCallback } from 'react'
import apiService from '@/services/api'
import type { ClassDefRead, ClassDefCreate } from '@/types/api'

interface StyleManagerModalProps {
  isOpen: boolean
  onClose: () => void
  subprojectId: number
  onStyleChange: () => void // Callback to refetch subproject data
}

function StyleManagerModal({
  isOpen,
  onClose,
  subprojectId,
  onStyleChange,
}: StyleManagerModalProps) {
  const [styles, setStyles] = useState<ClassDefRead[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Form state
  const [isEditing, setIsEditing] = useState<number | null>(null)
  const [name, setName] = useState('')
  const [definition, setDefinition] = useState('')
  const [formError, setFormError] = useState<string | null>(null)

  const fetchStyles = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiService.getClassDefs(subprojectId)
      setStyles(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load styles.')
    } finally {
      setLoading(false)
    }
  }, [subprojectId])

  useEffect(() => {
    if (isOpen) {
      fetchStyles()
    }
  }, [isOpen, fetchStyles])

  if (!isOpen) {
    return null
  }

  const resetForm = () => {
    setIsEditing(null)
    setName('')
    setDefinition('')
    setFormError(null)
  }

  const handleEditClick = (style: ClassDefRead) => {
    setIsEditing(style.id)
    setName(style.name)
    setDefinition(style.definition_raw)
    setFormError(null)
  }

  const handleDelete = async (styleId: number) => {
    if (!window.confirm('Are you sure you want to delete this style? This cannot be undone.')) {
      return
    }
    setError(null)
    try {
      await apiService.deleteClassDef(styleId)
      await fetchStyles() // Refetch the list
      onStyleChange() // Notify parent to refetch subproject
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete style.')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError(null)
    setError(null)

    if (!name.trim() || !definition.trim()) {
      setFormError('Name and definition cannot be empty.')
      return
    }

    const payload: ClassDefCreate = {
      subproject_id: subprojectId,
      name: name.trim(),
      definition_raw: definition.trim(),
    }

    try {
      if (isEditing) {
        await apiService.updateClassDef(isEditing, payload)
      } else {
        await apiService.createClassDef(payload)
      }
      resetForm()
      await fetchStyles() // Refetch list after create/update
      onStyleChange() // Notify parent to refetch subproject
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'An unexpected error occurred.'
      setError(`Failed to save style: ${errorMessage}`)
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-2xl p-6 w-full max-w-3xl max-h-[90vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-gray-800">Manage Styles (ClassDef)</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-800 text-2xl"
            aria-label="Close"
          >
            &times;
          </button>
        </div>

        {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{error}</div>}

        <div className="flex-grow overflow-y-auto pr-2">
          {loading ? (
            <p>Loading styles...</p>
          ) : styles.length === 0 ? (
            <p className="text-gray-500">No styles defined for this subproject yet.</p>
          ) : (
            <div className="space-y-3">
              {styles.map((style) => (
                <div key={style.id} className="p-3 bg-gray-50 rounded-md border border-gray-200">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold text-indigo-700">{style.name}</h4>
                      <pre className="mt-1 text-sm bg-gray-100 p-2 rounded text-gray-600 whitespace-pre-wrap font-mono">
                        {style.definition_raw}
                      </pre>
                    </div>
                    <div className="flex space-x-2 flex-shrink-0 ml-4">
                      <button
                        onClick={() => handleEditClick(style)}
                        className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(style.id)}
                        className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="mt-6 pt-4 border-t">
          <h3 className="text-xl font-semibold mb-3">{isEditing ? 'Edit Style' : 'Add New Style'}</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="style-name" className="block text-sm font-medium text-gray-700">Name</label>
              <input
                id="style-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="e.g., 'databaseStyle'"
              />
            </div>
            <div>
              <label htmlFor="style-definition" className="block text-sm font-medium text-gray-700">CSS Definition (raw)</label>
              <textarea
                id="style-definition"
                rows={3}
                value={definition}
                onChange={(e) => setDefinition(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 font-mono"
                placeholder="e.g., fill:#f9f,stroke:#333,stroke-width:4px"
              />
            </div>
            {formError && <p className="text-sm text-red-600">{formError}</p>}
            <div className="flex justify-end space-x-3">
              {isEditing && (
                 <button type="button" onClick={resetForm} className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300">
                    Cancel Edit
                 </button>
              )}
              <button type="submit" className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
                {isEditing ? 'Update Style' : 'Add Style'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default StyleManagerModal