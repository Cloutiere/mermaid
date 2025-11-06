// frontend/src/types/api.ts
// Version 1.0

/**
 * Types for API interactions, mirroring Pydantic schemas from the backend.
 */

// --- Backend Health Response ---
export interface BackendHealthResponse {
  message: string;
  status: string;
}

// --- Enum Types ---
// Corresponds to backend/app/models.py -> LinkType
export type LinkType = "VISIBLE" | "INVISIBLE";

// --- Low-level Definitions: ClassDef ---
// Corresponds to backend/app/schemas.py -> ClassDefRead
export interface ClassDefRead {
  id: number;
  subproject_id: number;
  name: string;
  definition_raw: string;
}

// --- Low-level Definitions: Relationship ---
// Corresponds to backend/app/schemas.py -> RelationshipRead
export interface RelationshipRead {
  id: number;
  subproject_id: number;
  source_node_id: number;
  target_node_id: number;
  label?: string;
  color?: string;
  link_type: LinkType;
}

// --- Low-level Definitions: Node ---
// Corresponds to backend/app/schemas.py -> NodeRead
export interface NodeRead {
  id: number;
  subproject_id: number;
  mermaid_id: string;
  title?: string;
  text_content: string;
  style_class_ref?: string;
}

// --- Mid-level Definitions: SubProject ---
// Corresponds to backend/app/schemas.py -> SubProjectRead
export interface SubProjectRead {
  id: number;
  project_id: number;
  title: string;
  mermaid_definition: string;
  visual_layout?: Record<string, any>; // JSON field from backend
  nodes: NodeRead[];
  relationships: RelationshipRead[];
  class_defs: ClassDefRead[];
}

// --- High-level Definitions: Project ---
// Corresponds to backend/app/schemas.py -> ProjectRead
export interface ProjectRead {
  id: number;
  title: string;
  subprojects: SubProjectRead[];
}