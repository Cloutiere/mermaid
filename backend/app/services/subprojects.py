# backend/app/services/subprojects.py
# Version 1.0

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import selectinload
from werkzeug.exceptions import NotFound, BadRequest
from app import db
from app.models import Project, SubProject
from app.schemas import SubProjectCreate, SubProjectRead # Import schemas for validation and reading

def get_all_subprojects(project_id: Optional[int] = None) -> List[SubProject]:
    """
    Récupère tous les sous-projets, avec un filtrage optionnel par project_id.
    Charge également les nœuds, relations et class_defs associés de manière efficace.
    """
    query = db.select(SubProject).options(
        selectinload(SubProject.nodes),         # type: ignore[arg-type]
        selectinload(SubProject.relationships), # type: ignore[arg-type]
        selectinload(SubProject.class_defs)     # type: ignore[arg-type]
    )

    if project_id is not None:
        # Vérifier que le project_id existe avant de filtrer
        project = db.session.get(Project, project_id)
        if project is None:
            raise NotFound(f"Project ID {project_id} not found.")
        query = query.filter(SubProject.project_id == project_id)

    subprojects = db.session.execute(query).scalars().all()
    return subprojects

def get_subproject_by_id(subproject_id: int) -> SubProject:
    """Récupère un sous-projet spécifique par son ID."""
    subproject = db.session.execute(
        db.select(SubProject)
        .options(
            selectinload(SubProject.nodes),         # type: ignore[arg-type]
            selectinload(SubProject.relationships), # type: ignore[arg-type]
            selectinload(SubProject.class_defs)     # type: ignore[arg-type]
        )
        .filter(SubProject.id == subproject_id)
    ).scalar_one_or_none()

    if subproject is None:
        raise NotFound(f"SubProject ID {subproject_id} not found.")
    return subproject

def _validate_project_id(project_id: int) -> Project:
    """Valide l'existence d'un Project ID et retourne l'objet Project."""
    project = db.session.get(Project, project_id)
    if project is None:
        raise NotFound(f"Project ID {project_id} not found.")
    return project

def create_subproject(subproject_data: SubProjectCreate) -> SubProject:
    """Crée un nouveau sous-projet."""
    # Valider l'existence du project_id parent
    _validate_project_id(subproject_data.project_id)

    # Vérifier s'il existe déjà un sous-projet avec le même titre dans le même projet (optionnel)
    existing_subproject = db.session.execute(
        db.select(SubProject).filter(
            SubProject.project_id == subproject_data.project_id,
            SubProject.title == subproject_data.title
        )
    ).scalar_one_or_none()
    if existing_subproject:
        raise BadRequest(f"SubProject with title '{subproject_data.title}' already exists for Project ID {subproject_data.project_id}.")

    new_subproject = SubProject(
        project_id=subproject_data.project_id,
        title=subproject_data.title,
        mermaid_definition=subproject_data.mermaid_definition,
        visual_layout=subproject_data.visual_layout # Peut être None
    )
    db.session.add(new_subproject)
    db.session.commit()

    # Rafraîchir pour charger les relations si elles sont nécessaires pour la réponse API
    db.session.refresh(new_subproject)
    return new_subproject

def update_subproject(subproject_id: int, subproject_data: SubProjectCreate) -> SubProject:
    """Met à jour un sous-projet existant."""
    # Obtenir le sous-projet existant (gère NotFound)
    subproject = get_subproject_by_id(subproject_id)

    # Valider l'existence du nouveau project_id parent s'il est modifié
    if subproject.project_id != subproject_data.project_id:
        _validate_project_id(subproject_data.project_id)

    # Vérifier s'il existe déjà un sous-projet avec le même titre dans le même projet (excluant le sous-projet actuel)
    existing_subproject_with_same_title = db.session.execute(
        db.select(SubProject).filter(
            SubProject.id != subproject_id,
            SubProject.project_id == subproject_data.project_id,
            SubProject.title == subproject_data.title
        )
    ).scalar_one_or_none()
    if existing_subproject_with_same_title:
        raise BadRequest(f"SubProject with title '{subproject_data.title}' already exists for Project ID {subproject_data.project_id}.")

    subproject.project_id = subproject_data.project_id
    subproject.title = subproject_data.title
    subproject.mermaid_definition = subproject_data.mermaid_definition
    subproject.visual_layout = subproject_data.visual_layout

    db.session.commit()

    # Rafraîchir pour s'assurer que les relations sont à jour si elles sont chargées dans la réponse
    db.session.refresh(subproject)
    return subproject

def delete_subproject(subproject_id: int) -> None:
    """Supprime un sous-projet existant."""
    subproject = get_subproject_by_id(subproject_id) # Utilise la fonction pour gérer le NotFound

    # La suppression de SubProject devrait déclencher la cascade delete pour les nœuds, relations, class_defs
    # grâce à `cascade="all, delete-orphan"` dans les relations de SubProject dans models.py
    db.session.delete(subproject)
    db.session.commit()