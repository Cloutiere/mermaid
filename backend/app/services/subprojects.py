# backend/app/services/subprojects.py
from typing import List
from werkzeug.exceptions import NotFound
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import SubProject, Project
from app.schemas import SubProjectCreate


def get_all_subprojects(project_id: int = None) -> List[SubProject]:
    """Récupère tous les sous-projets, optionnellement filtrés par project_id."""
    query = db.select(SubProject)
    if project_id is not None:
        query = query.where(SubProject.project_id == project_id)
    return db.session.execute(query).scalars().all()


def get_subproject_by_id(subproject_id: int) -> SubProject:
    """Récupère un sous-projet par ID, lève 404 si non trouvé."""
    subproject = db.session.get(SubProject, subproject_id)
    if subproject is None:
        raise NotFound(f"SubProject with ID {subproject_id} not found.")
    return subproject


def create_subproject(data: SubProjectCreate) -> SubProject:
    """Crée un nouveau sous-projet à partir des données validées."""
    # Vérifier que le project_id existe
    project = db.session.get(Project, data.project_id)
    if project is None:
        raise NotFound(f"Project with ID {data.project_id} not found.")
    
    subproject = SubProject(
        project_id=data.project_id,
        title=data.title,
        mermaid_definition=data.mermaid_definition,
        visual_layout=data.visual_layout
    )
    db.session.add(subproject)
    db.session.commit()
    db.session.refresh(subproject)
    return subproject


def update_subproject(subproject_id: int, data: SubProjectCreate) -> SubProject:
    """Met à jour un sous-projet existant. Lève 404 si non trouvé."""
    subproject = get_subproject_by_id(subproject_id)
    
    # Vérifier que le nouveau project_id existe si changé
    if data.project_id != subproject.project_id:
        project = db.session.get(Project, data.project_id)
        if project is None:
            raise NotFound(f"Project with ID {data.project_id} not found.")
    
    subproject.project_id = data.project_id
    subproject.title = data.title
    subproject.mermaid_definition = data.mermaid_definition
    subproject.visual_layout = data.visual_layout
    
    db.session.commit()
    return subproject


def delete_subproject(subproject_id: int) -> bool:
    """Supprime un sous-projet par ID. Lève 404 si non trouvé."""
    subproject = get_subproject_by_id(subproject_id)
    
    db.session.delete(subproject)
    db.session.commit()
    return True
