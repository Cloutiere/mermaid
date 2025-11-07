// frontend/src/hooks/useGraphEditor.ts
// Version 1.0

import { useState, useEffect, useCallback, useMemo } from 'react'
import apiService from '@/services/api'
import type { SubProjectRead, SubProjectCreate } from '@/types/api'

/**
 * Normalise le code Mermaid pour une comparaison cohérente.
 * @param code Le code Mermaid à normaliser.
 * @returns Le code normalisé (fins de ligne Unix, sans espaces de début/fin).
 */
const normalize = (code: string | null | undefined): string => {
  if (typeof code !== 'string') return ''
  // 1. Uniformiser les fins de ligne
  const unixCode = code.replace(/\r\n/g, '\n')
  // 2. Supprimer les espaces blancs de début et de fin
  return unixCode.trim()
}

/**
 * Hook personnalisé pour encapsuler la logique de gestion de l'éditeur de graphe.
 * @param subprojectId L'ID du sous-projet à gérer.
 */
export function useGraphEditor(subprojectId: number | null) {
  // --- États Internes du Hook ---
  const [subproject, setSubProject] = useState<SubProjectRead | null>(null)
  const [currentMermaidCode, setCurrentMermaidCode] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // --- Fonctions de base ---

  /**
   * Recharge les données du sous-projet depuis l'API.
   * @param silent Si true, ne met pas l'état `loading` à true (pour les rechargements en arrière-plan).
   */
  const refetchSubProject = useCallback(
    async (silent = false) => {
      if (!subprojectId || isNaN(subprojectId)) {
        setError("Erreur : ID du sous-projet invalide ou manquant.")
        if (!silent) setLoading(false)
        return
      }

      if (!silent) setLoading(true)
      setError(null)

      try {
        const data = await apiService.getSubProject(subprojectId)
        setSubProject(data)
        setCurrentMermaidCode(data.mermaid_definition || '')
      } catch (err) {
        console.error('Échec du chargement/rechargement du sous-projet:', err)
        setError(
          err instanceof Error ? err.message : 'Une erreur inconnue est survenue lors du chargement.'
        )
      } finally {
        if (!silent) setLoading(false)
      }
    },
    [subprojectId]
  )

  // --- Effets ---

  // Effet de chargement initial des données.
  useEffect(() => {
    refetchSubProject(false)
  }, [refetchSubProject])

  // --- Logique Dérivée (Memoization) ---

  /**
   * Détermine si le code Mermaid a été modifié par rapport à la version sauvegardée.
   */
  const isDirty = useMemo(() => {
    if (!subproject || loading) return false
    const originalCode = normalize(subproject.mermaid_definition)
    const newCode = normalize(currentMermaidCode)
    return newCode !== originalCode
  }, [currentMermaidCode, subproject, loading])

  // --- Fonctions d'Action Exposées ---

  /**
   * Sauvegarde le code Mermaid.
   * Détecte automatiquement s'il faut mettre à jour la structure ou seulement les métadonnées.
   */
  const saveMermaidCode = async () => {
    if (!subproject) return

    setIsSaving(true)
    setError(null)

    try {
      const mermaidChanged = normalize(currentMermaidCode) !== normalize(subproject.mermaid_definition)
      let updatedData: SubProjectRead

      if (mermaidChanged) {
        const payload: SubProjectCreate = {
          project_id: subproject.project_id,
          title: subproject.title,
          mermaid_definition: currentMermaidCode,
          visual_layout: subproject.visual_layout || null,
        }
        updatedData = await apiService.updateSubProjectStructure(subproject.id, payload)
      } else {
        updatedData = await apiService.patchSubProjectMetadata(subproject.id, {
          title: subproject.title,
          visual_layout: subproject.visual_layout || null,
        })
      }

      setSubProject(updatedData)
      setCurrentMermaidCode(updatedData.mermaid_definition || '')
      console.log('Sauvegarde réussie!', updatedData)
    } catch (err) {
      console.error('Échec de la sauvegarde:', err)
      setError(
        err instanceof Error ? err.message : 'Une erreur inconnue est survenue lors de la sauvegarde.'
      )
    } finally {
      setIsSaving(false)
    }
  }

  /**
   * Exporte le code Mermaid généré par le backend dans un fichier .mmd.
   */
  const handleExport = async () => {
    if (!subproject) return

    setIsExporting(true)
    setError(null)

    try {
      const mermaidCodeExported = await apiService.exportMermaid(subproject.id)
      const blob = new Blob([mermaidCodeExported], { type: 'text/plain;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      const fileName = `${subproject.title.replace(/\s+/g, '_')}_export.mmd`

      link.href = url
      link.setAttribute('download', fileName)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (err) {
      console.error("Échec de l'exportation:", err)
      setError(
        err instanceof Error ? err.message : "Une erreur inconnue est survenue lors de l'exportation."
      )
    } finally {
      setIsExporting(false)
    }
  }

  // --- Contrat de Retour du Hook ---
  return {
    // États
    subproject,
    currentMermaidCode,
    loading,
    isSaving,
    isExporting,
    error,
    // États Dérivés
    isDirty,
    // Fonctions
    setCurrentMermaidCode,
    refetchSubProject,
    saveMermaidCode,
    handleExport,
  }
}