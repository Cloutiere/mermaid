# backend/app/services/projects.py
from typing import List
from werkzeug.exceptions import NotFound
from sqlalchemy.exc import IntegrityError # Optionnel, pour les erreurs de DB spécifiques

from app.__init__ import db
from app.models import Project
from app.schemas import ProjectCreate


def get_all_projects() -> List[Project]:
    """Récupère tous les projets."""
    # Utilisation de db.select pour une approche compatible SQLAlchemy 2.0
    return db.session.execute(db.select(Project)).scalars().all()


def get_project_by_id(project_id: int) -> Project:
    """Récupère un projet par ID, lève 404 si non trouvé."""
    # db.session.get est la méthode la plus efficace pour récupérer par clé primaire
    project = db.session.get(Project, project_id)
    if project is None:
        # Werkzeug NotFound sera intercepté par app.register_error_handler(404, handle_api_error)
        raise NotFound(f"Project with ID {project_id} not found.")
    return project


def create_project(data: ProjectCreate) -> Project:
    """Crée un nouveau projet à partir des données validées."""
    project = Project(
        title=data.title,
    )
    db.session.add(project)
    db.session.commit()
    db.session.refresh(project)
    return project


def update_project(project_id: int, data: ProjectCreate) -> Project:
    """Met à jour un projet existant. Lève 404 si non trouvé."""
    # Récupère l'entité, ce qui gère automatiquement le 404
    project = get_project_by_id(project_id)

    # Mise à jour des champs à partir des données validées
    project.title = data.title

    db.session.commit()
    # Pas besoin de refresh ici si on n'a pas touché à des relations ou des champs calculés
    return project


def delete_project(project_id: int) -> bool:
    """Supprime un projet par ID. Lève 404 si non trouvé."""
    project = get_project_by_id(project_id)

    db.session.delete(project)
    db.session.commit()
    return True