# backend/tests/test_projects.py
# Version 1.0

import pytest
import json
from app.models import Project

# --- Tests pour la ressource Project ---

# Base URL pour les endpoints de projet
PROJECTS_URL = '/api/projects/'

# --- Tests pour la création de projet (POST /api/projects/) ---

def test_create_project_success(client, db_session):
    """Teste la création réussie d'un nouveau projet."""
    project_data = {"title": "Mon Premier Projet"}
    response = client.post(PROJECTS_URL, json=project_data)

    assert response.status_code == 201
    data = json.loads(response.get_data(as_text=True))

    assert data['title'] == project_data['title']
    assert 'id' in data
    assert data['id'] is not None

    # Vérification dans la base de données (optionnel mais bon pour la robustesse)
    created_project = db_session.get(Project, data['id'])
    assert created_project is not None
    assert created_project.title == project_data['title']

def test_create_project_missing_title(client, db_session):
    """Teste la création d'un projet sans le champ 'title' (devrait échouer)."""
    project_data = {"description": "Ceci est une description"} # Titre manquant
    response = client.post(PROJECTS_URL, json=project_data)

    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "title" in data['error'] # Le message d'erreur devrait indiquer le problème avec 'title'

def test_create_project_empty_title(client, db_session):
    """Teste la création d'un projet avec un titre vide (devrait échouer)."""
    project_data = {"title": ""}
    response = client.post(PROJECTS_URL, json=project_data)

    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "title" in data['error']

def test_create_project_empty_json(client, db_session):
    """Teste la création d'un projet avec un corps JSON vide (devrait échouer)."""
    response = client.post(PROJECTS_URL, json={})

    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "title" in data['error'] # Le schema Pydantic devrait toujours requérir le titre

# --- Tests pour la lecture de tous les projets (GET /api/projects/) ---

def test_get_all_projects_empty(client, db_session):
    """Teste la récupération de tous les projets lorsqu'il n'y en a aucun."""
    response = client.get(PROJECTS_URL)

    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))

    assert isinstance(data, list)
    assert len(data) == 0

def test_get_all_projects_with_data(client, db_session):
    """Teste la récupération de tous les projets lorsqu'il y en a plusieurs."""
    # Créer des projets manuellement dans la DB pour s'assurer qu'ils existent
    project1 = Project(title="Projet A")
    project2 = Project(title="Projet B")
    db_session.add_all([project1, project2])
    db_session.commit()

    response = client.get(PROJECTS_URL)

    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))

    assert isinstance(data, list)
    assert len(data) == 2

    # Vérifier que les données retournées correspondent
    titles = sorted([p['title'] for p in data])
    assert titles == ["Projet A", "Projet B"]
    assert all('id' in p and 'title' in p for p in data)

# --- Tests pour la lecture d'un projet par ID (GET /api/projects/<id>) ---

def test_get_project_by_id_success(client, db_session):
    """Teste la récupération réussie d'un projet par son ID."""
    project = Project(title="Projet Unique")
    db_session.add(project)
    db_session.commit()
    project_id = project.id

    response = client.get(f"{PROJECTS_URL}{project_id}")

    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))

    assert data['id'] == project_id
    assert data['title'] == "Projet Unique"

def test_get_project_by_id_not_found(client, db_session):
    """Teste la récupération d'un projet avec un ID inexistant (devrait échouer)."""
    non_existent_id = 9999
    response = client.get(f"{PROJECTS_URL}{non_existent_id}")

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert str(non_existent_id) in data['error']

# --- Tests pour la mise à jour d'un projet (PUT /api/projects/<id>) ---

def test_update_project_success(client, db_session):
    """Teste la mise à jour réussie d'un projet existant."""
    project = Project(title="Projet à Modifier")
    db_session.add(project)
    db_session.commit()
    project_id = project.id

    update_data = {"title": "Projet Modifié avec Succès"}
    response = client.put(f"{PROJECTS_URL}{project_id}", json=update_data)

    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))

    assert data['id'] == project_id
    assert data['title'] == update_data['title']

    # Vérification dans la base de données
    updated_project = db_session.get(Project, project_id)
    assert updated_project is not None
    assert updated_project.title == update_data['title']

def test_update_project_not_found(client, db_session):
    """Teste la mise à jour d'un projet avec un ID inexistant (devrait échouer)."""
    non_existent_id = 9999
    update_data = {"title": "Nouveau Titre"}
    response = client.put(f"{PROJECTS_URL}{non_existent_id}", json=update_data)

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert str(non_existent_id) in data['error']

def test_update_project_invalid_data(client, db_session):
    """Teste la mise à jour d'un projet avec des données invalides (titre vide)."""
    project = Project(title="Projet Initial")
    db_session.add(project)
    db_session.commit()
    project_id = project.id

    update_data = {"title": ""} # Titre vide
    response = client.put(f"{PROJECTS_URL}{project_id}", json=update_data)

    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "title" in data['error']

# --- Tests pour la suppression d'un projet (DELETE /api/projects/<id>) ---

def test_delete_project_success(client, db_session):
    """Teste la suppression réussie d'un projet existant."""
    project = Project(title="Projet à Supprimer")
    db_session.add(project)
    db_session.commit()
    project_id = project.id

    response = client.delete(f"{PROJECTS_URL}{project_id}")

    assert response.status_code == 204 # No Content

    # Vérifier que le projet a bien été supprimé
    deleted_project = db_session.get(Project, project_id)
    assert deleted_project is None

def test_delete_project_not_found(client, db_session):
    """Teste la suppression d'un projet avec un ID inexistant (devrait échouer)."""
    non_existent_id = 9999
    response = client.delete(f"{PROJECTS_URL}{non_existent_id}")

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert str(non_existent_id) in data['error']