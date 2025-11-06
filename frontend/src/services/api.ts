// frontend/src/services/api.ts
// Version 1.2 (Ajout de updateSubProject)

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import type {
  ProjectRead,
  SubProjectRead,
  NodeRead,
  RelationshipRead,
  BackendHealthResponse,
  SubProjectCreate // Import nécessaire pour le typage des payloads
} from '@/types/api';

// Type générique pour les payloads POST/PUT (correspondant aux schémas *Create du backend)
// Nous utilisons Omit dans les méthodes spécifiques pour mieux typer les données attendues.
type Payload = Record<string, any>;

// 1. Configuration de l'instance Axios
// La base URL est fixée à '/api', ce qui permet à VITE de rediriger les requêtes vers le backend (localhost:5001) via le proxy.
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Service Client API centralisé.
 * Encapsule la logique HTTP et gère le typage des requêtes/réponses.
 */
class ApiService {
  private api = api;

  /**
   * Gestion générique des erreurs Axios.
   * @param error L'objet erreur capturé.
   * @returns Une nouvelle erreur avec un message clarifié.
   */
  private handleError(error: unknown): Error {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status;
      const data = error.response?.data;
      const detail = data && typeof data === 'object' && 'detail' in data ? data.detail : JSON.stringify(data);

      if (status === 404) {
          return new Error(`Resource not found (404) at ${error.config?.url}.`);
      }
      if (status === 400 || status === 422) { // 400 Bad Request, 422 Validation Error
          return new Error(`Validation Error (${status}). Details: ${detail}`);
      }
      if (status && status >= 400 && status < 500) {
          return new Error(`Client Error (${status}). Details: ${detail}`);
      }
      return new Error(`Network or Server Error: ${error.message}`);
    }
    return new Error(`An unexpected error occurred: ${error}`);
  }

  // --- Abstractions CRUD génériques ---

  public async get<T>(path: string, params?: Record<string, any>): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.api.get(path, { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  public async post<T, P extends Payload>(path: string, data: P): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.api.post(path, data);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  public async put<T, P extends Payload>(path: string, data: P): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.api.put(path, data);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  public async delete(path: string): Promise<void> {
    try {
      await this.api.delete(path);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // --- Méthodes Spécifiques par Entité ---

  // -- Health --
  public async getHealth(): Promise<BackendHealthResponse> {
    return this.get<BackendHealthResponse>('/health');
  }

  // -- Projects --

  /** Récupère tous les projets. */
  public async getProjects(): Promise<ProjectRead[]> {
    return this.get<ProjectRead[]>('/projects/');
  }

  /** Récupère un projet par ID. */
  public async getProject(id: number): Promise<ProjectRead> {
    return this.get<ProjectRead>(`/projects/${id}`);
  }

  /** Crée un nouveau projet. */
  public async createProject(data: Omit<ProjectRead, 'id' | 'subprojects'>): Promise<ProjectRead> {
      return this.post<ProjectRead, typeof data>('/projects/', data);
  }

  /** Met à jour un projet existant. */
  public async updateProject(id: number, data: Omit<ProjectRead, 'id' | 'subprojects'>): Promise<ProjectRead> {
      return this.put<ProjectRead, typeof data>(`/projects/${id}`, data);
  }

  /** Supprime un projet par ID. */
  public async deleteProject(id: number): Promise<void> {
    return this.delete(`/projects/${id}`);
  }

  // -- SubProjects --

  /** Récupère les subprojects. Filtre optionnel par projectId. */
  public async getSubProjects(projectId?: number): Promise<SubProjectRead[]> {
    const params = projectId ? { project_id: projectId } : undefined;
    return this.get<SubProjectRead[]>('/subprojects/', params);
  }

  /** Récupère un subproject par ID. */
  public async getSubProject(id: number): Promise<SubProjectRead> {
      return this.get<SubProjectRead>(`/subprojects/${id}`);
  }

  /** Crée un nouveau subproject. */
  public async createSubProject(data: SubProjectCreate): Promise<SubProjectRead> {
      // Le type SubProjectCreate est Omit<SubProjectRead, 'id' | 'nodes' | 'relationships' | 'class_defs'>
      return this.post<SubProjectRead, typeof data>('/subprojects/', data);
  }

  /** Met à jour un subproject existant. */
  public async updateSubProject(id: number, data: SubProjectCreate): Promise<SubProjectRead> {
      // Le type SubProjectCreate est Omit<SubProjectRead, 'id' | 'nodes' | 'relationships' | 'class_defs'>
      return this.put<SubProjectRead, typeof data>(`/subprojects/${id}`, data);
  }

  /** Supprime un subproject par ID. */
  public async deleteSubProject(id: number): Promise<void> {
    return this.delete(`/subprojects/${id}`);
  }

  // -- Nodes --

  /** Récupère les nœuds. Filtre optionnel par subprojectId. */
  public async getNodes(subprojectId?: number): Promise<NodeRead[]> {
    const params = subprojectId ? { subproject_id: subprojectId } : undefined;
    return this.get<NodeRead[]>('/nodes/', params);
  }

  /** Crée un nouveau nœud. */
  public async createNode(data: Omit<NodeRead, 'id'>): Promise<NodeRead> {
      return this.post<NodeRead, typeof data>('/nodes/', data);
  }

  /** Met à jour un nœud. */
  public async updateNode(nodeId: number, data: Omit<NodeRead, 'id'>): Promise<NodeRead> {
      return this.put<NodeRead, typeof data>(`/nodes/${nodeId}`, data);
  }

  // -- Relationships --

  /** Récupère les relations. Filtre optionnel par subprojectId. */
  public async getRelationships(subprojectId?: number): Promise<RelationshipRead[]> {
    const params = subprojectId ? { subproject_id: subprojectId } : undefined;
    // Note: L'endpoint est /api/nodes/relationships/
    return this.get<RelationshipRead[]>('/nodes/relationships/', params);
  }

  /** Crée une nouvelle relation. */
  public async createRelationship(data: Omit<RelationshipRead, 'id'>): Promise<RelationshipRead> {
      return this.post<RelationshipRead, typeof data>('/nodes/relationships/', data);
  }

  /** Supprime une relation. */
  public async deleteRelationship(relationshipId: number): Promise<void> {
      return this.delete(`/nodes/relationships/${relationshipId}`);
  }
}

const apiService = new ApiService();
export default apiService;