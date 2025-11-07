# backend/app/services/subgraphs.py
# Version 1.0

import secrets
import string
from typing import List
from sqlalchemy import update, select
from sqlalchemy.orm import selectinload
from werkzeug.exceptions import NotFound, BadRequest
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Subgraph, SubProject, Node, ClassDef
from app.schemas import SubgraphCreatePayload, SubgraphUpdatePayload
from app.services.mermaid_generator import generate_mermaid_from_subproject

def _generate_unique_mermaid_id(subproject_id: int) -> str:
    """Génère un ID Mermaid unique pour un Subgraph au sein d'un SubProject."""
    while True:
        # Génère un ID aléatoire plus robuste, ex: cluster_SP1_abc123
        random_part = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
        mermaid_id = f"cluster_SP{subproject_id}_{random_part}"

        # Vérifie l'unicité dans la base de données
        existing = db.session.execute(
            db.select(Subgraph).filter_by(subproject_id=subproject_id, mermaid_id=mermaid_id)
        ).scalar_one_or_none()

        if not existing:
            return mermaid_id

def _bulk_assign_nodes(subproject_id: int, subgraph_id: int, node_ids: List[int]) -> None:
    """Met à jour en masse le subgraph_id pour une liste de nœuds."""
    if not node_ids:
        return

    # Valider que tous les nœuds appartiennent au bon subproject
    valid_nodes_count = db.session.scalar(
        select(db.func.count(Node.id)).where(
            Node.id.in_(node_ids),
            Node.subproject_id == subproject_id
        )
    )
    if valid_nodes_count != len(node_ids):
        raise BadRequest("One or more nodes do not belong to the specified subproject.")

    # Mettre à jour en masse le `subgraph_id`
    db.session.execute(
        update(Node)
        .where(Node.id.in_(node_ids))
        .values(subgraph_id=subgraph_id)
    )

def _bulk_unassign_nodes(subproject_id: int, node_ids: List[int]) -> None:
    """Met à jour en masse le subgraph_id à NULL pour une liste de nœuds."""
    if not node_ids:
        return

    # Valider que tous les nœuds appartiennent au bon subproject
    valid_nodes_count = db.session.scalar(
        select(db.func.count(Node.id)).where(
            Node.id.in_(node_ids),
            Node.subproject_id == subproject_id
        )
    )
    if valid_nodes_count != len(node_ids):
        raise BadRequest("One or more nodes do not belong to the specified subproject.")

    # Mettre à jour en masse le `subgraph_id` à NULL
    db.session.execute(
        update(Node)
        .where(Node.id.in_(node_ids))
        .values(subgraph_id=None)
    )

def get_subgraph_by_id(subgraph_id: int) -> Subgraph:
    """Récupère un subgraph par ID avec ses nœuds."""
    subgraph = db.session.execute(
        db.select(Subgraph).options(selectinload(Subgraph.nodes)).filter_by(id=subgraph_id) # type: ignore[arg-type]
    ).scalar_one_or_none()
    if subgraph is None:
        raise NotFound(f"Subgraph with ID {subgraph_id} not found.")
    return subgraph

def create_subgraph(data: SubgraphCreatePayload) -> Subgraph:
    """Crée un Subgraph, lui assigne des nœuds, et régénère le Mermaid."""
    subproject = db.session.get(SubProject, data.subproject_id)
    if not subproject:
        raise NotFound(f"SubProject with ID {data.subproject_id} not found.")

    if data.style_class_ref:
        class_def = db.session.execute(
            select(ClassDef).filter_by(subproject_id=data.subproject_id, name=data.style_class_ref)
        ).scalar_one_or_none()
        if not class_def:
            raise BadRequest(f"ClassDef '{data.style_class_ref}' not found in SubProject {data.subproject_id}.")

    mermaid_id = _generate_unique_mermaid_id(data.subproject_id)
    new_subgraph = Subgraph(
        subproject_id=data.subproject_id,
        mermaid_id=mermaid_id,
        title=data.title,
        style_class_ref=data.style_class_ref
    )

    try:
        db.session.add(new_subgraph)
        db.session.flush()

        if data.node_ids:
            _bulk_assign_nodes(data.subproject_id, new_subgraph.id, data.node_ids)

        subproject.mermaid_definition = generate_mermaid_from_subproject(data.subproject_id)
        db.session.commit()
        db.session.refresh(new_subgraph)
        return get_subgraph_by_id(new_subgraph.id)
    except Exception as e:
        db.session.rollback()
        raise BadRequest(f"Failed to create subgraph: {e}")

def update_subgraph(subgraph_id: int, data: SubgraphUpdatePayload) -> Subgraph:
    """Met à jour les métadonnées d'un Subgraph et régénère le Mermaid."""
    subgraph = get_subgraph_by_id(subgraph_id)
    subproject_id = subgraph.subproject_id

    if data.style_class_ref:
        class_def = db.session.execute(
            select(ClassDef).filter_by(subproject_id=subproject_id, name=data.style_class_ref)
        ).scalar_one_or_none()
        if not class_def:
            raise BadRequest(f"ClassDef '{data.style_class_ref}' not found in SubProject {subproject_id}.")

    subgraph.title = data.title
    subgraph.style_class_ref = data.style_class_ref

    try:
        subproject = db.session.get(SubProject, subproject_id)
        if subproject:
             subproject.mermaid_definition = generate_mermaid_from_subproject(subproject_id)
        db.session.commit()
        return get_subgraph_by_id(subgraph_id)
    except Exception as e:
        db.session.rollback()
        raise BadRequest(f"Failed to update subgraph: {e}")

def assign_nodes_to_subgraph(subgraph_id: int, node_ids: List[int]) -> Subgraph:
    """Assigner une liste de nœuds à un subgraph (écrase les affectations précédentes)."""
    subgraph = get_subgraph_by_id(subgraph_id)
    subproject_id = subgraph.subproject_id
    try:
        _bulk_assign_nodes(subproject_id, subgraph_id, node_ids)
        subproject = db.session.get(SubProject, subproject_id)
        if subproject:
             subproject.mermaid_definition = generate_mermaid_from_subproject(subproject_id)
        db.session.commit()
        return get_subgraph_by_id(subgraph_id)
    except Exception as e:
        db.session.rollback()
        raise BadRequest(f"Failed to assign nodes: {e}")

def unassign_nodes_from_subgraph(subgraph_id: int, node_ids: List[int]) -> Subgraph:
    """Désassigner une liste de nœuds d'un subgraph."""
    subgraph = get_subgraph_by_id(subgraph_id)
    subproject_id = subgraph.subproject_id

    # Vérifier que les nœuds appartiennent bien à ce subgraph
    nodes_in_subgraph = db.session.scalars(
        select(Node.id).where(Node.id.in_(node_ids), Node.subgraph_id == subgraph_id)
    ).all()

    if len(nodes_in_subgraph) != len(node_ids):
         raise BadRequest("Some nodes do not belong to the specified subgraph.")

    try:
        _bulk_unassign_nodes(subproject_id, node_ids)
        subproject = db.session.get(SubProject, subproject_id)
        if subproject:
            subproject.mermaid_definition = generate_mermaid_from_subproject(subproject_id)
        db.session.commit()
        return get_subgraph_by_id(subgraph_id)
    except Exception as e:
        db.session.rollback()
        raise BadRequest(f"Failed to unassign nodes: {e}")

def delete_subgraph(subgraph_id: int) -> None:
    """Supprime un subgraph après avoir désassigné tous ses nœuds."""
    subgraph = get_subgraph_by_id(subgraph_id)
    subproject_id = subgraph.subproject_id

    try:
        # Désassigner tous les nœuds du subgraph
        db.session.execute(
            update(Node)
            .where(Node.subgraph_id == subgraph_id)
            .values(subgraph_id=None)
        )

        db.session.delete(subgraph)

        subproject = db.session.get(SubProject, subproject_id)
        if subproject:
            subproject.mermaid_definition = generate_mermaid_from_subproject(subproject_id)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise BadRequest(f"Failed to delete subgraph: {e}")