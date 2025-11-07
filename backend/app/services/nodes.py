# backend/app/services/nodes.py
# Version 1.1

from typing import List, Optional, Dict, Any
from werkzeug.exceptions import NotFound, BadRequest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update

from app import db
from app.models import Node, SubProject, Relationship
from app.schemas import NodeCreate, RelationshipCreate
from app.services.mermaid_generator import generate_mermaid_from_subproject


# --- Services pour Node ---

def get_all_nodes(subproject_id: Optional[int] = None) -> List[Node]:
    """Récupère tous les nœuds, optionnellement filtrés par subproject_id."""
    query = db.select(Node)
    if subproject_id is not None:
        query = query.where(Node.subproject_id == subproject_id)
    return list(db.session.execute(query).scalars().all())


def get_node_by_id(node_id: int) -> Node:
    """Récupère un nœud par ID, lève 404 si non trouvé."""
    node = db.session.get(Node, node_id)
    if node is None:
        raise NotFound(f"Node with ID {node_id} not found.")
    return node


def create_node(data: NodeCreate) -> Node:
    """Crée un nouveau nœud à partir des données validées."""
    subproject = db.session.get(SubProject, data.subproject_id)
    if subproject is None:
        raise NotFound(f"SubProject with ID {data.subproject_id} not found.")

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
        db.session.refresh(node)
    except IntegrityError:
        db.session.rollback()
        raise BadRequest(f"Node with mermaid_id '{data.mermaid_id}' already exists in SubProject ID {data.subproject_id}.")

    return node


def update_node(node_id: int, data: NodeCreate) -> Node:
    """Met à jour un nœud existant. Lève 404 si non trouvé."""
    node = get_node_by_id(node_id)

    if data.subproject_id != node.subproject_id:
        subproject = db.session.get(SubProject, data.subproject_id)
        if subproject is None:
            raise NotFound(f"SubProject with ID {data.subproject_id} not found.")

    title = data.title if data.title is not None else data.mermaid_id
    text_content = data.text_content if data.text_content is not None else data.mermaid_id

    node.subproject_id = data.subproject_id
    node.mermaid_id = data.mermaid_id
    node.title = title
    node.text_content = text_content
    node.style_class_ref = data.style_class_ref

    try:
        db.session.commit()
        db.session.refresh(node)
    except IntegrityError:
        db.session.rollback()
        raise BadRequest(f"Node with mermaid_id '{data.mermaid_id}' already exists in SubProject ID {data.subproject_id}.")

    return node


def delete_node(node_id: int) -> bool:
    """Supprime un nœud par ID. Lève 404 si non trouvé."""
    node = get_node_by_id(node_id)
    db.session.delete(node)
    db.session.commit()
    return True

def import_node_content(subproject_id: int, content_map: Dict[str, str]) -> Dict[str, Any]:
    """
    Importe en masse le contenu textuel pour les nœuds d'un subproject.
    Cette opération est transactionnelle et met à jour la définition Mermaid.
    """
    try:
        subproject = db.session.get(SubProject, subproject_id)
        if subproject is None:
            raise NotFound(f"SubProject with ID {subproject_id} not found.")

        # Récupérer tous les nœuds concernés en une seule requête
        nodes_to_update_query = db.select(Node).where(
            Node.subproject_id == subproject_id,
            Node.mermaid_id.in_(content_map.keys())
        )
        nodes_to_update = list(db.session.execute(nodes_to_update_query).scalars().all())

        updated_ids = {node.mermaid_id for node in nodes_to_update}
        ignored_ids = list(set(content_map.keys()) - updated_ids)

        updated_count = 0

        # Mettre à jour les nœuds trouvés
        if nodes_to_update:
            for node in nodes_to_update:
                node.text_content = content_map[node.mermaid_id]
            updated_count = len(nodes_to_update)

        # Mettre à jour la définition Mermaid du SubProject
        # `flush` s'assure que les modifications sont envoyées à la BD avant la génération
        db.session.flush()
        new_mermaid_def = generate_mermaid_from_subproject(subproject_id)
        subproject.mermaid_definition = new_mermaid_def

        db.session.commit()

        return {
            'updated_count': updated_count,
            'ignored_ids': ignored_ids
        }

    except Exception as e:
        db.session.rollback()
        raise e

# --- Services pour Relationship ---

def get_all_relationships(subproject_id: Optional[int] = None) -> List[Relationship]:
    """Récupère toutes les relations, optionnellement filtrées par subproject_id."""
    query = db.select(Relationship)
    if subproject_id is not None:
        query = query.where(Relationship.subproject_id == subproject_id)
    return list(db.session.execute(query).scalars().all())


def get_relationship_by_id(relationship_id: int) -> Relationship:
    """Récupère une relation par ID, lève 404 si non trouvée."""
    relationship = db.session.get(Relationship, relationship_id)
    if relationship is None:
        raise NotFound(f"Relationship with ID {relationship_id} not found.")
    return relationship


def create_relationship(data: RelationshipCreate) -> Relationship:
    """Crée une nouvelle relation à partir des données validées."""
    subproject = db.session.get(SubProject, data.subproject_id)
    if subproject is None:
        raise NotFound(f"SubProject with ID {data.subproject_id} not found.")

    source_node = db.session.get(Node, data.source_node_id)
    if source_node is None:
        raise NotFound(f"Source Node with ID {data.source_node_id} not found.")

    target_node = db.session.get(Node, data.target_node_id)
    if target_node is None:
        raise NotFound(f"Target Node with ID {data.target_node_id} not found.")

    if source_node.subproject_id != data.subproject_id:
        raise BadRequest(f"Source Node ID {data.source_node_id} does not belong to SubProject ID {data.subproject_id}.")
    if target_node.subproject_id != data.subproject_id:
        raise BadRequest(f"Target Node ID {data.target_node_id} does not belong to SubProject ID {data.subproject_id}.")

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

    if data.subproject_id != relationship.subproject_id:
        subproject = db.session.get(SubProject, data.subproject_id)
        if subproject is None:
            raise NotFound(f"SubProject with ID {data.subproject_id} not found.")

    source_node = db.session.get(Node, data.source_node_id)
    if source_node is None:
        raise NotFound(f"Source Node with ID {data.source_node_id} not found.")

    target_node = db.session.get(Node, data.target_node_id)
    if target_node is None:
        raise NotFound(f"Target Node with ID {data.target_node_id} not found.")

    if source_node.subproject_id != data.subproject_id:
        raise BadRequest(f"Source Node ID {data.source_node_id} does not belong to SubProject ID {data.subproject_id}.")
    if target_node.subproject_id != data.subproject_id:
        raise BadRequest(f"Target Node ID {data.target_node_id} does not belong to SubProject ID {data.subproject_id}.")

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