// frontend/src/services/api.ts
// Version 2.1 (Ajout de patchNodeStyle)

import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'
import type {
  ProjectRead,
  SubProjectRead,
  NodeRead,
  RelationshipRead,
  BackendHealthResponse,
  SubProjectCreate,
  ClassDefRead,
  ClassDefCreate,
  NodeContentImportResponse,
  NodeStyleUpdatePayload,
} from '@/types/api'

// Type générique pour les payloads POST/PUT (correspondant aux schémas *Create du backend)
// Nous utilisons Omit dans les méthodes spécifiques pour mieux typer les données attendues.
type Payload = Record<string, any>

// 1. Configuration de l'instance Axios
// La base URL est fixée à '/api', ce qui permet à VITE de rediriger les requêtes vers le backend (localhost:5001) via le proxy.
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Service Client API centralisé.
 * Encapsule la logique HTTP et gère le typage des requêtes/réponses.
 */
class ApiService {
  private api = api

  /**
   * Gestion générique des erreurs Axios.
   * @param error L'objet erreur capturé.
   * @returns Une nouvelle erreur avec un message clarifié.
   */
  private handleError(error: unknown): Error {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status
      const data = error.response?.data
      const detail =
        data && typeof data === 'object' && 'detail' in data ? data.detail : JSON.stringify(data)

      if (status === 404) {
        return new Error(`Resource not found (404) at ${error.config?.url}.`)
      }
      if (status === 400 || status === 422) {
        // 400 Bad Request, 422 Validation Error
        return new Error(`Validation Error (${status}). Details: ${detail}`)
      }
      if (status && status >= 400 && status < 500) {
        return new Error(`Client Error (${status}). Details: ${detail}`)
      }
      return new Error(`Network or Server Error: ${error.message}`)
    }
    return new Error(`An unexpected error occurred: ${error}`)
  }

  // --- Abstractions CRUD génériques ---

  public async get<T>(path: string, params?: Record<string, any>): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.api.get(path, { params })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  public async post<T, P extends Payload>(path: string, data: P): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.api.post(path, data)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  public async put<T, P extends Payload>(path: string, data: P): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.api.put(path, data)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  public async delete(path: string): Promise<void> {
    try {
      await this.api.delete(path)
    } catch (error) {
      throw this.handleError(error)
    }
  }

  public async patch<T, P extends Payload>(path: string, data: P): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.api.patch(path, data)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // --- Méthodes Spécifiques par Entité ---

  // -- Health --
  public async getHealth(): Promise<BackendHealthResponse> {
    return this.get<BackendHealthResponse>('/health')
  }

  // -- Projects --

  /** Récupère tous les projets. */
  public async getProjects(): Promise<ProjectRead[]> {
    return this.get<ProjectRead[]>('/projects/')
  }

  /** Récupère un projet par ID. */
  public async getProject(id: number): Promise<ProjectRead> {
    return this.get<ProjectRead>(`/projects/${id}`)
  }

  /** Crée un nouveau projet. */
  public async createProject(data: Omit<ProjectRead, 'id' | 'subprojects'>): Promise<ProjectRead> {
    return this.post<ProjectRead, typeof data>('/projects/', data)
  }

  /** Met à jour un projet existant. */
  public async updateProject(
    id: number,
    data: Omit<ProjectRead, 'id' | 'subprojects'>
  ): Promise<ProjectRead> {
    return this.put<ProjectRead, typeof data>(`/projects/${id}`, data)
  }

  /** Supprime un projet par ID. */
  public async deleteProject(id: number): Promise<void> {
    return this.delete(`/projects/${id}`)
  }

  // -- SubProjects --

  /** Récupère les subprojects. Filtre optionnel par projectId. */
  public async getSubProjects(projectId?: number): Promise<SubProjectRead[]> {
    const params = projectId ? { project_id: projectId } : undefined
    return this.get<SubProjectRead[]>('/subprojects/', params)
  }

  /** Récupère un subproject par ID. */
  public async getSubProject(id: number): Promise<SubProjectRead> {
    return this.get<SubProjectRead>(`/subprojects/${id}`)
  }

  /** Crée un nouveau subproject. */
  public async createSubProject(data: SubProjectCreate): Promise<SubProjectRead> {
    return this.post<SubProjectRead, typeof data>('/subprojects/', data)
  }

  /** Met à jour un subproject existant (détection automatique structure vs métadonnées). */
  public async updateSubProject(id: number, data: SubProjectCreate): Promise<SubProjectRead> {
    return this.put<SubProjectRead, typeof data>(`/subprojects/${id}`, data)
  }

  /** Met à jour UNIQUEMENT les métadonnées (title + visual_layout) sans toucher à la structure. */
  public async patchSubProjectMetadata(
    id: number,
    data: { title: string; visual_layout?: any }
  ): Promise<SubProjectRead> {
    return this.patch<SubProjectRead, typeof data>(`/subprojects/${id}/metadata`, data)
  }

  /** Met à jour la structure Mermaid complète (reconstruction des entités). */
  public async updateSubProjectStructure(id: number, data: SubProjectCreate): Promise<SubProjectRead> {
    return this.put<SubProjectRead, typeof data>(`/subprojects/${id}`, data)
  }

  /** Supprime un subproject par ID. */
  public async deleteSubProject(id: number): Promise<void> {
    return this.delete(`/subprojects/${id}`)
  }

  /** Exporte le code Mermaid généré par le backend. */
  public async exportMermaid(subprojectId: number): Promise<string> {
    try {
      const response: AxiosResponse<string> = await this.api.get(
        `/mermaid/export/${subprojectId}`,
        {
          responseType: 'text',
        }
      )
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // -- Nodes --

  /** Récupère les nœuds. Filtre optionnel par subprojectId. */
  public async getNodes(subprojectId?: number): Promise<NodeRead[]> {
    const params = subprojectId ? { subproject_id: subprojectId } : undefined
    return this.get<NodeRead[]>('/nodes/', params)
  }

  /** Crée un nouveau nœud. */
  public async createNode(data: Omit<NodeRead, 'id'>): Promise<NodeRead> {
    return this.post<NodeRead, typeof data>('/nodes/', data)
  }

  /** Met à jour un nœud. */
  public async updateNode(nodeId: number, data: Omit<NodeRead, 'id'>): Promise<NodeRead> {
    return this.put<NodeRead, typeof data>(`/nodes/${nodeId}`, data)
  }

  /** Applique ou retire un style à un nœud spécifique. */
  public async patchNodeStyle(
    nodeId: number,
    data: NodeStyleUpdatePayload
  ): Promise<NodeRead> {
    return this.patch<NodeRead, NodeStyleUpdatePayload>(`/nodes/${nodeId}/style`, data)
  }

  /** Importe du contenu pour des nœuds existants via un dictionnaire. */
  public async importNodeContent(
    subprojectId: number,
    contentMap: Record<string, string>
  ): Promise<NodeContentImportResponse> {
    return this.post<NodeContentImportResponse, { content_map: Record<string, string> }>(
      `/nodes/import_content/${subprojectId}`,
      { content_map: contentMap }
    )
  }

  // -- Relationships --

  /** Récupère les relations. Filtre optionnel par subprojectId. */
  public async getRelationships(subprojectId?: number): Promise<RelationshipRead[]> {
    const params = subprojectId ? { subproject_id: subprojectId } : undefined
    return this.get<RelationshipRead[]>('/nodes/relationships/', params)
  }

  /** Crée une nouvelle relation. */
  public async createRelationship(data: Omit<RelationshipRead, 'id'>): Promise<RelationshipRead> {
    return this.post<RelationshipRead, typeof data>('/nodes/relationships/', data)
  }

  /** Supprime une relation. */
  public async deleteRelationship(relationshipId: number): Promise<void> {
    return this.delete(`/nodes/relationships/${relationshipId}`)
  }

  // -- ClassDefs --

  /** Récupère les définitions de classe. Filtre optionnel par subprojectId. */
  public async getClassDefs(subprojectId?: number): Promise<ClassDefRead[]> {
    const params = subprojectId ? { subproject_id: subprojectId } : undefined
    return this.get<ClassDefRead[]>('/classdefs/', params)
  }

  /** Crée une nouvelle définition de classe. */
  public async createClassDef(data: ClassDefCreate): Promise<ClassDefRead> {
    return this.post<ClassDefRead, ClassDefCreate>('/classdefs/', data)
  }

  /** Met à jour une définition de classe. */
  public async updateClassDef(id: number, data: ClassDefCreate): Promise<ClassDefRead> {
    return this.put<ClassDefRead, ClassDefCreate>(`/classdefs/${id}`, data)
  }

  /** Supprime une définition de classe. */
  public async deleteClassDef(id: number): Promise<void> {
    return this.delete(`/classdefs/${id}`)
  }
}

const apiService = new ApiService()
export default apiService