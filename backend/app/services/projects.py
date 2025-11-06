# backend/app/services/projects.py
# Version 1.0

from typing import List
from sqlalchemy.orm import selectinload
from werkzeug.exceptions import NotFound, BadRequest
from app import db
from app.models import Project
from app.schemas import ProjectCreate, ProjectRead

def get_all_projects() -> List[Project]:
    """Récupère tous les projets de la base de données."""
    projects = db.session.execute(
        db.select(Project).options(selectinload(Project.subprojects))
    ).scalars().all()
    return list(projects)

def get_project_by_id(project_id: int) -> Project:
    """Récupère un projet spécifique par son ID."""
    project = db.session.execute(
        db.select(Project)
        .options(selectinload(Project.subprojects))
        .filter_by(id=project_id)
    ).scalar_one_or_none()

    if project is None:
        raise NotFound(f"Project ID {project_id} not found.")
    return project

def create_project(project_data: ProjectCreate) -> Project:
    """Crée un nouveau projet."""
    if not project_data.title:
        raise BadRequest("Project title cannot be empty.")

    existing_project = db.session.execute(
        db.select(Project).filter_by(title=project_data.title)
    ).scalar_one_or_none()
    if existing_project:
        raise BadRequest(f"Project with title '{project_data.title}' already exists.")

    new_project = Project(title=project_data.title)  # type: ignore[call-arg]
    db.session.add(new_project)
    db.session.commit()

    db.session.refresh(new_project)
    return new_project

def update_project(project_id: int, project_data: ProjectCreate) -> Project:
    """Met à jour un projet existant."""
    if not project_data.title:
        raise BadRequest("Project title cannot be empty.")

    project = get_project_by_id(project_id)

    existing_project_with_same_title = db.session.execute(
        db.select(Project).filter(Project.id != project_id, Project.title == project_data.title)
    ).scalar_one_or_none()
    if existing_project_with_same_title:
        raise BadRequest(f"Project with title '{project_data.title}' already exists.")

    project.title = project_data.title
    db.session.commit()

    db.session.refresh(project)
    return project

def delete_project(project_id: int) -> None:
    """Supprime un projet existant."""
    project = get_project_by_id(project_id)

    db.session.delete(project)
    db.session.commit()
