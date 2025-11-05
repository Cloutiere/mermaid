    # backend/app/services/projects.py
    # Version 1.0

    from typing import List
    from sqlalchemy.orm import selectinload
    from werkzeug.exceptions import NotFound, BadRequest
    from app import db
    from app.models import Project
    from app.schemas import ProjectCreate, ProjectRead # Import schemas for validation and reading

    def get_all_projects() -> List[Project]:
        """Récupère tous les projets de la base de données."""
        # Utilise selectinload pour charger les subprojects associés de manière efficace
        # Le type: ignore est nécessaire car mypy ne peut pas toujours inférer le type des relations SQLAlchemy avec selectinload
        projects = db.session.execute(
            db.select(Project).options(selectinload(Project.subprojects)) # type: ignore[arg-type]
        ).scalars().all()
        return projects

    def get_project_by_id(project_id: int) -> Project:
        """Récupère un projet spécifique par son ID."""
        # Utilise selectinload pour charger les subprojects associés
        project = db.session.execute(
            db.select(Project)
            .options(selectinload(Project.subprojects)) # type: ignore[arg-type]
            .filter_by(id=project_id)
        ).scalar_one_or_none()

        if project is None:
            raise NotFound(f"Project ID {project_id} not found.")
        return project

    def create_project(project_data: ProjectCreate) -> Project:
        """Crée un nouveau projet."""
        # Vérification de base si le titre existe (déjà géré par Pydantic, mais bonne pratique ici aussi)
        if not project_data.title:
            raise BadRequest("Project title cannot be empty.")

        # Vérifier s'il existe déjà un projet avec le même titre (optionnel, selon les exigences métiers)
        existing_project = db.session.execute(
            db.select(Project).filter_by(title=project_data.title)
        ).scalar_one_or_none()
        if existing_project:
            raise BadRequest(f"Project with title '{project_data.title}' already exists.")

        new_project = Project(title=project_data.title)
        db.session.add(new_project)
        db.session.commit() # Commit pour s'assurer que l'ID est généré avant de le retourner

        # Recharger le projet avec ses relations pour la réponse API si nécessaire,
        # mais ici on retourne juste le modèle créé.
        # Si la réponse API doit contenir les subprojects, il faudrait le recharger avec selectinload.
        db.session.refresh(new_project)
        return new_project

    def update_project(project_id: int, project_data: ProjectCreate) -> Project:
        """Met à jour un projet existant."""
        # Vérification de base si le titre existe
        if not project_data.title:
            raise BadRequest("Project title cannot be empty.")

        project = get_project_by_id(project_id) # Utilise la fonction pour gérer le NotFound

        # Vérifier s'il existe déjà un projet avec le même titre (excluant le projet actuel)
        existing_project_with_same_title = db.session.execute(
            db.select(Project).filter(Project.id != project_id, Project.title == project_data.title)
        ).scalar_one_or_none()
        if existing_project_with_same_title:
            raise BadRequest(f"Project with title '{project_data.title}' already exists.")

        project.title = project_data.title
        db.session.commit()

        # Recharger le projet pour s'assurer que les relations sont à jour si elles sont chargées dans la réponse
        db.session.refresh(project)
        return project

    def delete_project(project_id: int) -> None:
        """Supprime un projet existant."""
        project = get_project_by_id(project_id) # Utilise la fonction pour gérer le NotFound

        db.session.delete(project)
        db.session.commit()