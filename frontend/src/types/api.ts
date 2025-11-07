// frontend/src/types/api.ts
// Version 3.0 (Ajout des types pour les Subgraphs)

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

// --- Types de Graphes et Composants ---

// Type pour SubProject (Graphe)
export interface SubProjectRead {
  id: number
  project_id: number
  title: string
  mermaid_definition: string
  visual_layout?: Record<string, any> | null
  nodes?: NodeRead[]
  relationships?: RelationshipRead[]
  class_defs?: ClassDefRead[]
  subgraphs?: SubgraphRead[] // AJOUT
}

// Type pour Node
export interface NodeRead {
  id: number
  subproject_id: number
  mermaid_id: string
  title?: string | null
  text_content: string
  style_class_ref?: string | null
  subgraph_id?: number | null // AJOUT
}

// Type pour Relationship (Lien)
export interface RelationshipRead {
  id: number
  subproject_id: number
  source_node_id: number
  target_node_id: number
  label?: string | null
  color?: string | null
  link_type: 'VISIBLE' | 'INVISIBLE'
}

// Type pour ClassDef (Style)
export interface ClassDefRead {
  id: number
  subproject_id: number
  name: string
  definition_raw: string
}

// Type pour Subgraph (Cluster)
export interface SubgraphRead {
  id: number
  subproject_id: number
  mermaid_id: string
  title: string
  style_class_ref?: string | null
  nodes: NodeRead[] // Liste des nœuds contenus
}

// --- Types pour les Payloads de Création (Schemas *Create) ---

export type ProjectCreate = Omit<ProjectRead, 'id' | 'subprojects'>
export type SubProjectCreate = Omit<
  SubProjectRead,
  'id' | 'nodes' | 'relationships' | 'class_defs' | 'subgraphs'
>
export type NodeCreate = Omit<NodeRead, 'id'>
export type RelationshipCreate = Omit<RelationshipRead, 'id'>
export type ClassDefCreate = Omit<ClassDefRead, 'id'>

// --- Types pour les Payloads de Mise à Jour & Actions Spécifiques ---

// Pour la mise à jour de style d'un noeud
export interface NodeStyleUpdatePayload {
  style_name: string | null
}

// Payloads pour les Subgraphs
export interface SubgraphCreatePayload {
  subproject_id: number
  title: string
  style_class_ref?: string | null
  node_ids: number[] // IDs des nœuds à affecter immédiatement
}

export interface SubgraphUpdatePayload {
  title: string
  style_class_ref?: string | null
}

export interface NodeAssignmentPayload {
  node_ids: number[]
}

// --- Types pour l'Import/Export ---

// Pour l'import Mermaid
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

// Pour l'import de contenu de nœuds
export interface NodeContentImportResponse {
  updated_count: number
  ignored_ids: string[]
}