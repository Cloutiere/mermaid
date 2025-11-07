# backend/app/schemas.py
# Version 1.3

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from .models import LinkType

# --- Définitions de bas niveau : ClassDef ---

class ClassDefBase(BaseModel):
    """Schéma de base pour les définitions de style Mermaid."""
    subproject_id: int
    name: str = Field(..., max_length=100)
    definition_raw: str

class ClassDefCreate(ClassDefBase):
    """Schéma utilisé pour la création d'une définition de style."""
    pass

class ClassDefRead(ClassDefBase):
    """Schéma utilisé pour la lecture (réponse API) d'une définition de style."""
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Définitions de bas niveau : Relationship ---

class RelationshipBase(BaseModel):
    """Schéma de base pour les relations (liens) entre nœuds."""
    subproject_id: int
    source_node_id: int
    target_node_id: int
    label: Optional[str] = None
    color: Optional[str] = None
    link_type: LinkType # Utilise l'Enum LinkType de models.py

class RelationshipCreate(RelationshipBase):
    """Schéma utilisé pour la création d'une relation."""
    pass

class RelationshipRead(RelationshipBase):
    """Schéma utilisé pour la lecture (réponse API) d'une relation."""
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Définitions de bas niveau : Node ---

class NodeBase(BaseModel):
    """Schéma de base pour un nœud individuel du graphe."""
    subproject_id: int
    mermaid_id: str = Field(..., max_length=50)
    title: Optional[str] = None
    text_content: str
    style_class_ref: Optional[str] = None

class NodeCreate(NodeBase):
    """Schéma utilisé pour la création d'un nœud."""
    pass

class NodeRead(NodeBase):
    """Schéma utilisé pour la lecture (réponse API) d'un nœud."""
    id: int
    subgraph_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class NodeStyleUpdate(BaseModel):
    """Schéma pour l'application ou le retrait d'une référence de style."""
    style_name: Optional[str] = Field(None, description="Nom de la ClassDef à appliquer, ou None pour retirer.")

# --- Définitions pour les Subgraphs ---

class SubgraphBase(BaseModel):
    """Schéma de base pour un Subgraph."""
    subproject_id: int
    mermaid_id: str = Field(..., max_length=50)
    title: str = Field(..., max_length=255)
    style_class_ref: Optional[str] = Field(None, max_length=100)

class SubgraphRead(SubgraphBase):
    """Schéma de lecture d'un Subgraph, incluant les nœuds."""
    id: int
    nodes: List["NodeRead"] = []
    model_config = ConfigDict(from_attributes=True)

class SubgraphCreatePayload(BaseModel):
    """Schéma pour la création d'un Subgraph avec affectation initiale de nœuds."""
    subproject_id: int
    title: str = Field(..., max_length=255)
    style_class_ref: Optional[str] = Field(None, max_length=100)
    node_ids: List[int] = Field(default_factory=list, description="IDs des nœuds à affecter au nouveau subgraph.")

class SubgraphUpdatePayload(BaseModel):
    """Schéma pour la mise à jour des métadonnées d'un Subgraph."""
    title: str = Field(..., max_length=255)
    style_class_ref: Optional[str] = Field(None, max_length=100)

class NodeAssignmentPayload(BaseModel):
    """Schéma pour affecter ou désaffecter des nœuds à un Subgraph."""
    node_ids: List[int] = Field(..., description="Liste des IDs de nœuds à affecter/désaffecter.")

# --- Définitions de niveau intermédiaire : SubProject ---

class SubProjectBase(BaseModel):
    """Schéma de base pour un SubProject (Graphe Narratif)."""
    project_id: int
    title: str = Field(..., max_length=255)
    mermaid_definition: str
    visual_layout: Optional[Dict[str, Any]] = None # Stocké comme JSON/Dict

class SubProjectCreate(SubProjectBase):
    """Schéma utilisé pour la création d'un SubProject."""
    pass

class SubProjectRead(SubProjectBase):
    """Schéma de lecture d'un SubProject, incluant les relations imbriquées."""
    id: int

    # Relations imbriquées (Liste des schémas Read déjà définis)
    nodes: List[NodeRead] = []
    relationships: List[RelationshipRead] = []
    class_defs: List[ClassDefRead] = []
    subgraphs: List[SubgraphRead] = []

    model_config = ConfigDict(from_attributes=True)

# --- Définitions de haut niveau : Project ---

class ProjectBase(BaseModel):
    """Schéma de base pour un Project (Saga)."""
    title: str = Field(..., max_length=255)

class ProjectCreate(ProjectBase):
    """Schéma utilisé pour la création d'un Project."""
    pass

class ProjectRead(ProjectBase):
    """Schéma de lecture d'un Project, incluant les SubProjects."""
    id: int

    # Relation imbriquée
    subprojects: List[SubProjectRead] = []

    model_config = ConfigDict(from_attributes=True)

# --- Définitions pour l'importation de contenu ---

class NodeContentImport(BaseModel):
    """Schéma pour l'importation en masse du contenu textuel des nœuds."""
    # Représente le JSON de la requête: { "MERMAID_ID": "Contenu Textuel", ... }
    content_map: Dict[str, str] = Field(..., description="Map des mermaid_id aux nouveaux text_content.")

# --- Schéma pour la mise à jour partielle des métadonnées SubProject ---

class SubProjectMetadataUpdate(BaseModel):
    """Schéma pour la mise à jour partielle (title + visual_layout) sans toucher à la structure."""
    title: str = Field(..., max_length=255)
    visual_layout: Optional[Dict[str, Any]] = None