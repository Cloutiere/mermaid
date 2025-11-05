# backend/app/services/nodes.py
# Version 1.0

from typing import List, Optional
from werkzeug.exceptions import NotFound, BadRequest
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Node, SubProject, Relationship # Import Relationship for cascade delete checks if needed
from app.schemas import NodeCreate, NodeRead # Import schemas for validation and reading

# --- Services pour Node ---

def get_all_nodes(subproject_id: Optional[int] = None) -> List[Node]:
    """Récupère tous les nœuds, optionnellement filtrés par subproject_id."""
    query = db.select(Node)
    if subproject_id is not None:
        # Optionnel : vérifier l'existence du subproject_id avant de filtrer pour une meilleure gestion d'erreur
        # subproject = db.session.get(SubProject, subproject_id)
        # if subproject is None:
        #     raise NotFound(f"SubProject with ID {subproject_id} not found.")
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

    # Si title ou text_content sont None, utiliser mermaid_id par défaut
    title = data.title if data.title is not None else data.mermaid_id
    text_content = data.text_content if data.text_content is not None else data.mermaid_id

    node = Node(
        subproject_id=data.subproject_id,
        mermaid_id=data.mermaid_id,
        title=title,
        text_content=text_content,
        style_class_ref=data.style_class_ref
    )

    try:
        db.session.add(node)
        db.session.commit()
        # Refresh pour s'assurer que tous les champs calculés ou générés sont présents (ex: ID)
        db.session.refresh(node) 
    except IntegrityError:
        db.session.rollback()
        # L'IntegrityError pour la contrainte unique (subproject_id, mermaid_id) sera gérée ici.
        raise BadRequest(f"Node with mermaid_id '{data.mermaid_id}' already exists in SubProject ID {data.subproject_id}.")

    return node


def update_node(node_id: int, data: NodeCreate) -> Node:
    """Met à jour un nœud existant. Lève 404 si non trouvé."""
    node = get_node_by_id(node_id)

    # Vérifier que le nouveau subproject_id existe si changé
    if data.subproject_id != node.subproject_id:
        subproject = db.session.get(SubProject, data.subproject_id)
        if subproject is None:
            raise NotFound(f"SubProject with ID {data.subproject_id} not found.")

    # Si title ou text_content sont None, utiliser mermaid_id par défaut
    title = data.title if data.title is not None else data.mermaid_id
    text_content = data.text_content if data.text_content is not None else data.mermaid_id

    node.subproject_id = data.subproject_id
    node.mermaid_id = data.mermaid_id
    node.title = title
    node.text_content = text_content
    node.style_class_ref = data.style_class_ref

    try:
        db.session.commit()
        # Refresh pour s'assurer que les données mises à jour sont chargées
        db.session.refresh(node)
    except IntegrityError:
        db.session.rollback()
        # Gérer le cas où le mermaid_id change pour un ID existant dans le même SP
        raise BadRequest(f"Node with mermaid_id '{data.mermaid_id}' already exists in SubProject ID {data.subproject_id}.")

    return node


def delete_node(node_id: int) -> bool:
    """Supprime un nœud par ID. Lève 404 si non trouvé."""
    node = get_node_by_id(node_id)

    # La suppression d'un nœud devrait entraîner la suppression des relations qui lui sont associées
    # grâce aux cascades `delete-orphan` définies dans les relations `source_relationships` et `target_relationships` de Node.
    db.session.delete(node)
    db.session.commit()
    return True


# --- Services pour Relationship ---

def get_all_relationships(subproject_id: Optional[int] = None) -> List[Relationship]:
    """Récupère toutes les relations, optionnellement filtrées par subproject_id."""
    query = db.select(Relationship)
    if subproject_id is not None:
        # Optionnel : vérifier l'existence du subproject_id avant de filtrer
        # subproject = db.session.get(SubProject, subproject_id)
        # if subproject is None:
        #     raise NotFound(f"SubProject with ID {subproject_id} not found.")
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

    # Vérifier que les nodes source et target existent
    source_node = db.session.get(Node, data.source_node_id)
    if source_node is None:
        raise NotFound(f"Source Node with ID {data.source_node_id} not found.")

    target_node = db.session.get(Node, data.target_node_id)
    if target_node is None:
        raise NotFound(f"Target Node with ID {data.target_node_id} not found.")

    # Vérifier que les nodes appartiennent au même subproject que celui spécifié pour la relation
    if source_node.subproject_id != data.subproject_id:
        raise BadRequest(f"Source Node ID {data.source_node_id} does not belong to SubProject ID {data.subproject_id}.")
    if target_node.subproject_id != data.subproject_id:
        raise BadRequest(f"Target Node ID {data.target_node_id} does not belong to SubProject ID {data.subproject_id}.")

    # Vérifier que source et target ne sont pas le même nœud (si nécessaire, selon les règles métier)
    if data.source_node_id == data.target_node_id:
        raise BadRequest("Source and target nodes cannot be the same.")

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

    # Vérifier que le nouveau subproject_id existe s'il est changé
    if data.subproject_id != relationship.subproject_id:
        subproject = db.session.get(SubProject, data.subproject_id)
        if subproject is None:
            raise NotFound(f"SubProject with ID {data.subproject_id} not found.")

    # Vérifier que les nodes source et target existent
    source_node = db.session.get(Node, data.source_node_id)
    if source_node is None:
        raise NotFound(f"Source Node with ID {data.source_node_id} not found.")

    target_node = db.session.get(Node, data.target_node_id)
    if target_node is None:
        raise NotFound(f"Target Node with ID {data.target_node_id} not found.")

    # Vérifier la cohérence du subproject pour les nœuds
    if source_node.subproject_id != data.subproject_id:
        raise BadRequest(f"Source Node ID {data.source_node_id} does not belong to SubProject ID {data.subproject_id}.")
    if target_node.subproject_id != data.subproject_id:
        raise BadRequest(f"Target Node ID {data.target_node_id} does not belong to SubProject ID {data.subproject_id}.")

    # Vérifier que source et target ne sont pas le même nœud
    if data.source_node_id == data.target_node_id:
        raise BadRequest("Source and target nodes cannot be the same.")

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