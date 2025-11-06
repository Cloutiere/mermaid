# backend/app/services/subprojects.py
# Version 2.0

from typing import List, Optional
from sqlalchemy.orm import selectinload
from werkzeug.exceptions import NotFound, BadRequest

from app import db
from app.models import SubProject, Project
from app.schemas import SubProjectCreate
from app.services.mermaid_parser import synchronize_subproject_entities

def _get_project_or_404(project_id: int) -> Project:
    """Vérifie l'existence d'un projet et le retourne, sinon lève une exception NotFound."""
    project = db.session.get(Project, project_id)
    if not project:
        raise NotFound(f"Project with ID {project_id} not found.")
    return project

def get_all_subprojects(project_id: Optional[int] = None) -> List[SubProject]:
    """Récupère tous les sous-projets, optionnellement filtrés par project_id."""
    query = db.select(SubProject).options(
        selectinload(SubProject.nodes), # type: ignore[arg-type]
        selectinload(SubProject.relationships), # type: ignore[arg-type]
        selectinload(SubProject.class_defs) # type: ignore[arg-type]
    ).order_by(SubProject.id)

    if project_id:
        query = query.filter_by(project_id=project_id)

    subprojects = db.session.execute(query).scalars().all()
    return list(subprojects)

def get_subproject_by_id(subproject_id: int) -> SubProject:
    """Récupère un sous-projet par son ID avec ses relations."""
    subproject = db.session.execute(
        db.select(SubProject).options(
            selectinload(SubProject.nodes), # type: ignore[arg-type]
            selectinload(SubProject.relationships), # type: ignore[arg-type]
            selectinload(SubProject.class_defs) # type: ignore[arg-type]
        ).filter_by(id=subproject_id)
    ).scalar_one_or_none()

    if subproject is None:
        raise NotFound(f"SubProject with ID {subproject_id} not found.")
    return subproject

def create_subproject(subproject_data: SubProjectCreate) -> SubProject:
    """Crée un nouveau sous-projet et synchronise ses entités structurelles."""
    _get_project_or_404(subproject_data.project_id)

    existing_subproject = db.session.execute(
        db.select(SubProject).filter_by(
            project_id=subproject_data.project_id,
            title=subproject_data.title
        )
    ).scalar_one_or_none()
    if existing_subproject:
        raise BadRequest(f"A subproject with title '{subproject_data.title}' already exists in this project.")

    new_subproject = SubProject(
        project_id=subproject_data.project_id,
        title=subproject_data.title,
        mermaid_definition=subproject_data.mermaid_definition,
        visual_layout=subproject_data.visual_layout
    )
    db.session.add(new_subproject)
    db.session.flush()

    try:
        synchronize_subproject_entities(new_subproject, new_subproject.mermaid_definition)
    except Exception as e:
        db.session.rollback()
        raise BadRequest(f"Failed to parse and synchronize Mermaid definition on create: {e}")

    db.session.commit()
    db.session.refresh(new_subproject)
    return get_subproject_by_id(new_subproject.id)

def update_subproject(subproject_id: int, subproject_data: SubProjectCreate) -> SubProject:
    """Met à jour un sous-projet existant et synchronise ses entités structurelles."""
    subproject = get_subproject_by_id(subproject_id)

    if subproject.title != subproject_data.title:
        existing_subproject = db.session.execute(
            db.select(SubProject).filter(
                SubProject.id != subproject_id,
                SubProject.project_id == subproject.project_id,
                SubProject.title == subproject_data.title
            )
        ).scalar_one_or_none()
        if existing_subproject:
            raise BadRequest(f"A subproject with title '{subproject_data.title}' already exists in this project.")

    subproject.title = subproject_data.title
    subproject.mermaid_definition = subproject_data.mermaid_definition
    subproject.visual_layout = subproject_data.visual_layout

    try:
        synchronize_subproject_entities(subproject, subproject.mermaid_definition)
    except Exception as e:
        db.session.rollback()
        raise BadRequest(f"Failed to parse and synchronize Mermaid definition on update: {e}")

    db.session.commit()
    return get_subproject_by_id(subproject_id)

def delete_subproject(subproject_id: int) -> None:
    """Supprime un sous-projet."""
    subproject = get_subproject_by_id(subproject_id)
    db.session.delete(subproject)
    db.session.commit()