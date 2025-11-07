# backend/app/services/nodes.py
# Version 1.2

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
    """Crée un nouveau nœud et met à jour la définition Mermaid du subproject."""
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
        # Flush pour que le nouveau nœud soit visible par le générateur
        db.session.flush()

        # Régénérer et mettre à jour la définition Mermaid du subproject
        subproject.mermaid_definition = generate_mermaid_from_subproject(subproject.id)

        db.session.commit()
        db.session.refresh(node)
    except IntegrityError:
        db.session.rollback()
        raise BadRequest(f"Node with mermaid_id '{data.mermaid_id}' already exists in SubProject ID {data.subproject_id}.")

    return node


def update_node(node_id: int, data: NodeCreate) -> Node:
    """Met à jour un nœud existant et met à jour la définition Mermaid du subproject."""
    node = get_node_by_id(node_id)
    original_subproject_id = node.subproject_id

    if data.subproject_id != node.subproject_id:
        new_subproject = db.session.get(SubProject, data.subproject_id)
        if new_subproject is None:
            raise NotFound(f"SubProject with ID {data.subproject_id} not found.")

    title = data.title if data.title is not None else data.mermaid_id
    text_content = data.text_content if data.text_content is not None else data.mermaid_id

    node.subproject_id = data.subproject_id
    node.mermaid_id = data.mermaid_id
    node.title = title
    node.text_content = text_content
    node.style_class_ref = data.style_class_ref

    try:
        # Flush pour que les modifications du nœud soient visibles par le générateur
        db.session.flush()

        # Régénérer la définition pour le subproject concerné
        subproject = db.session.get(SubProject, original_subproject_id)
        if subproject:
            subproject.mermaid_definition = generate_mermaid_from_subproject(subproject.id)

        # Si le nœud a été déplacé, l'ancien subproject doit aussi être mis à jour
        if data.subproject_id != original_subproject_id:
            old_subproject = db.session.get(SubProject, original_subproject_id)
            if old_subproject:
                old_subproject.mermaid_definition = generate_mermaid_from_subproject(old_subproject.id)


        db.session.commit()
        db.session.refresh(node)
    except IntegrityError:
        db.session.rollback()
        raise BadRequest(f"Node with mermaid_id '{data.mermaid_id}' already exists in SubProject ID {data.subproject_id}.")

    return node


def delete_node(node_id: int) -> bool:
    """Supprime un nœud par ID. Lève 404 si non trouvé."""
    node = get_node_by_id(node_id)
    subproject_id = node.subproject_id # Garder l'ID avant la suppression

    db.session.delete(node)

    # Régénération après la suppression
    subproject = db.session.get(SubProject, subproject_id)
    if subproject:
        subproject.mermaid_definition = generate_mermaid_from_subproject(subproject_id)

    db.session.commit()
    return True

def import_node_content(subproject_id: int, content_map: Dict[str, str]) -> Dict[str, Any]:
    """
    Importe en masse le contenu textuel pour les nœuds d'un subproject.
    Cette opération est transactionnelle et met à jour la définition Mermaid.

    Accepte les clés du content_map soit comme IDs numériques (ex: "1136") 
    soit comme mermaid_id (ex: "A001").
    """
    try:
        subproject = db.session.get(SubProject, subproject_id)
        if subproject is None:
            raise NotFound(f"SubProject with ID {subproject_id} not found.")

        # Séparer les clés en IDs numériques vs mermaid_id
        numeric_ids = []
        mermaid_ids = []

        for key in content_map.keys():
            try:
                numeric_ids.append(int(key))
            except ValueError:
                mermaid_ids.append(key)

        # Construire la requête pour chercher par ID OU mermaid_id
        conditions = []
        if numeric_ids:
            conditions.append(Node.id.in_(numeric_ids))
        if mermaid_ids:
            conditions.append(Node.mermaid_id.in_(mermaid_ids))

        if not conditions:
            # Aucune clé valide fournie
            return {
                'updated_count': 0,
                'ignored_ids': list(content_map.keys())
            }

        nodes_to_update_query = db.select(Node).where(
            Node.subproject_id == subproject_id,
            db.or_(*conditions)
        )
        nodes_to_update = list(db.session.execute(nodes_to_update_query).scalars().all())

        # Créer un mapping pour retrouver le contenu par ID ou mermaid_id
        updated_keys = set()
        updated_count = 0

        # Mettre à jour les nœuds trouvés
        for node in nodes_to_update:
            # Chercher le contenu soit par ID numérique soit par mermaid_id
            content = None
            matched_key = None

            if str(node.id) in content_map:
                content = content_map[str(node.id)]
                matched_key = str(node.id)
            elif node.mermaid_id in content_map:
                content = content_map[node.mermaid_id]
                matched_key = node.mermaid_id

            if content is not None:
                node.text_content = content
                updated_keys.add(matched_key)
                updated_count += 1

        ignored_ids = list(set(content_map.keys()) - updated_keys)

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