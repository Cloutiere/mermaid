// frontend/src/types/api.ts
// Version 2.1 (Ajout NodeStyleUpdatePayload)

// Type pour le health check
export interface BackendHealthResponse {
  status: string
  message: string
}

// Type pour Project
export interface ProjectRead {
  id: number
  title: string
  subprojects: SubProjectRead[]
}

// Type pour SubProject
export interface SubProjectRead {
  id: number
  project_id: number
  title: string
  mermaid_definition: string
  visual_layout?: Record<string, any> | null
  nodes?: NodeRead[]
  relationships?: RelationshipRead[]
  class_defs?: ClassDefRead[]
}

// Type pour Node
export interface NodeRead {
  id: number
  subproject_id: number
  mermaid_id: string
  title?: string | null
  text_content: string
  style_class_ref?: string | null
}

// Type pour Relationship
export interface RelationshipRead {
  id: number
  subproject_id: number
  source_node_id: number
  target_node_id: number
  label?: string | null
  color?: string | null
  link_type: 'VISIBLE' | 'INVISIBLE'
}

// Type pour ClassDef
export interface ClassDefRead {
  id: number
  subproject_id: number
  name: string
  definition_raw: string
}

// Types pour les payloads de création (sans id)
export type ProjectCreate = Omit<ProjectRead, 'id' | 'subprojects'>
export type SubProjectCreate = Omit<SubProjectRead, 'id' | 'nodes' | 'relationships' | 'class_defs'>
export type NodeCreate = Omit<NodeRead, 'id'>
export type RelationshipCreate = Omit<RelationshipRead, 'id'>
export type ClassDefCreate = Omit<ClassDefRead, 'id'>

// Type pour la mise à jour de style d'un noeud
export interface NodeStyleUpdatePayload {
  style_name: string | null;
}

// Type pour l'import Mermaid
export interface MermaidImportRequest {
  code: string
  project_title?: string
}

export interface MermaidImportResponse {
  id: number
  title: string
  subprojects: {
    id: number
    title: string
    mermaid_definition: string
  }[]
}

// Type pour l'import de contenu de nœuds
export interface NodeContentImportResponse {
  updated_count: number
  ignored_ids: string[]
}