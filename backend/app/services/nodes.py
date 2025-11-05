# backend/app/services/nodes.py
from typing import List
from werkzeug.exceptions import NotFound, BadRequest
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Node, SubProject, Relationship
from app.schemas import NodeCreate, RelationshipCreate


# --- Services pour Node ---

def get_all_nodes(subproject_id: int = None) -> List[Node]:
    """Récupère tous les nœuds, optionnellement filtrés par subproject_id."""
    query = db.select(Node)
    if subproject_id is not None:
        query = query.where(Node.subproject_id == subproject_id)
    return db.session.execute(query).scalars().all()


def get_node_by_id(node_id: int) -> Node:
    """Récupère un nœud par ID, lève 404 si non trouvé."""
    node = db.session.get(Node, node_id)
    if node is None:
        raise NotFound(f"Node with ID {node_id} not found.")
    return node


def create_node(data: NodeCreate) -> Node:
    """Crée un nouveau nœud à partir des données validées."""
    # Vérifier que le subproject_id existe
    subproject = db.session.get(SubProject, data.subproject_id)
    if subproject is None:
        raise NotFound(f"SubProject with ID {data.subproject_id} not found.")
    
    node = Node(
        subproject_id=data.subproject_id,
        mermaid_id=data.mermaid_id,
        title=data.title,
        text_content=data.text_content,
        style_class_ref=data.style_class_ref
    )
    
    try:
        db.session.add(node)
        db.session.commit()
        db.session.refresh(node)
    except IntegrityError as e:
        db.session.rollback()
        raise BadRequest(f"Node with mermaid_id '{data.mermaid_id}' already exists in this SubProject.")
    
    return node


def update_node(node_id: int, data: NodeCreate) -> Node:
    """Met à jour un nœud existant. Lève 404 si non trouvé."""
    node = get_node_by_id(node_id)
    
    # Vérifier que le nouveau subproject_id existe si changé
    if data.subproject_id != node.subproject_id:
        subproject = db.session.get(SubProject, data.subproject_id)
        if subproject is None:
            raise NotFound(f"SubProject with ID {data.subproject_id} not found.")
    
    node.subproject_id = data.subproject_id
    node.mermaid_id = data.mermaid_id
    node.title = data.title
    node.text_content = data.text_content
    node.style_class_ref = data.style_class_ref
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise BadRequest(f"Node with mermaid_id '{data.mermaid_id}' already exists in this SubProject.")
    
    return node


def delete_node(node_id: int) -> bool:
    """Supprime un nœud par ID. Lève 404 si non trouvé."""
    node = get_node_by_id(node_id)
    
    db.session.delete(node)
    db.session.commit()
    return True


# --- Services pour Relationship ---

def get_all_relationships(subproject_id: int = None) -> List[Relationship]:
    """Récupère toutes les relations, optionnellement filtrées par subproject_id."""
    query = db.select(Relationship)
    if subproject_id is not None:
        query = query.where(Relationship.subproject_id == subproject_id)
    return db.session.execute(query).scalars().all()


def get_relationship_by_id(relationship_id: int) -> Relationship:
    """Récupère une relation par ID, lève 404 si non trouvée."""
    relationship = db.session.get(Relationship, relationship_id)
    if relationship is None:
        raise NotFound(f"Relationship with ID {relationship_id} not found.")
    return relationship


def create_relationship(data: RelationshipCreate) -> Relationship:
    """Crée une nouvelle relation à partir des données validées."""
    # Vérifier que le subproject_id existe
    subproject = db.session.get(SubProject, data.subproject_id)
    if subproject is None:
        raise NotFound(f"SubProject with ID {data.subproject_id} not found.")
    
    # Vérifier que les nodes existent
    source_node = db.session.get(Node, data.source_node_id)
    if source_node is None:
        raise NotFound(f"Source Node with ID {data.source_node_id} not found.")
    
    target_node = db.session.get(Node, data.target_node_id)
    if target_node is None:
        raise NotFound(f"Target Node with ID {data.target_node_id} not found.")
    
    # Vérifier que les nodes appartiennent au même subproject
    if source_node.subproject_id != data.subproject_id or target_node.subproject_id != data.subproject_id:
        raise BadRequest("Source and target nodes must belong to the same SubProject as the relationship.")
    
    relationship = Relationship(
        subproject_id=data.subproject_id,
        source_node_id=data.source_node_id,
        target_node_id=data.target_node_id,
        label=data.label,
        color=data.color,
        link_type=data.link_type
    )
    
    db.session.add(relationship)
    db.session.commit()
    db.session.refresh(relationship)
    return relationship


def update_relationship(relationship_id: int, data: RelationshipCreate) -> Relationship:
    """Met à jour une relation existante. Lève 404 si non trouvée."""
    relationship = get_relationship_by_id(relationship_id)
    
    # Vérifier que le nouveau subproject_id existe si changé
    if data.subproject_id != relationship.subproject_id:
        subproject = db.session.get(SubProject, data.subproject_id)
        if subproject is None:
            raise NotFound(f"SubProject with ID {data.subproject_id} not found.")
    
    # Vérifier que les nodes existent
    source_node = db.session.get(Node, data.source_node_id)
    if source_node is None:
        raise NotFound(f"Source Node with ID {data.source_node_id} not found.")
    
    target_node = db.session.get(Node, data.target_node_id)
    if target_node is None:
        raise NotFound(f"Target Node with ID {data.target_node_id} not found.")
    
    # Vérifier la cohérence du subproject
    if source_node.subproject_id != data.subproject_id or target_node.subproject_id != data.subproject_id:
        raise BadRequest("Source and target nodes must belong to the same SubProject as the relationship.")
    
    relationship.subproject_id = data.subproject_id
    relationship.source_node_id = data.source_node_id
    relationship.target_node_id = data.target_node_id
    relationship.label = data.label
    relationship.color = data.color
    relationship.link_type = data.link_type
    
    db.session.commit()
    return relationship


def delete_relationship(relationship_id: int) -> bool:
    """Supprime une relation par ID. Lève 404 si non trouvée."""
    relationship = get_relationship_by_id(relationship_id)
    
    db.session.delete(relationship)
    db.session.commit()
    return True
