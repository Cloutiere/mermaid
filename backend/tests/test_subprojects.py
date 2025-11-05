# backend/tests/test_subprojects.py
# Version 1.0

import pytest
import json
from app.models import Project, SubProject

# Base URL pour les endpoints de sous-projets
SUBPROJECTS_URL = '/api/subprojects/'

# --- Tests pour la création de sous-projet (POST /api/subprojects/) ---

def test_create_subproject_success(client, db_session):
    """Teste la création réussie d'un nouveau sous-projet."""
    # Pré-requis : Créer un projet parent
    project = Project(title="Projet Parent Pour SubProject")
    db_session.add(project)
    db_session.commit()
    project_id = project.id

    subproject_data = {
        "project_id": project_id,
        "title": "Mon Premier Sous-Projet",
        "mermaid_definition": "graph TD\nA[Node A] --> B(Node B)"
    }

    response = client.post(SUBPROJECTS_URL, json=subproject_data)

    assert response.status_code == 201
    data = json.loads(response.get_data(as_text=True))

    assert data['title'] == subproject_data['title']
    assert data['project_id'] == project_id
    assert data['mermaid_definition'] == subproject_data['mermaid_definition']
    assert 'id' in data
    assert data['id'] is not None

    # Vérification dans la base de données
    created_subproject = db_session.get(SubProject, data['id'])
    assert created_subproject is not None
    assert created_subproject.title == subproject_data['title']
    assert created_subproject.project_id == project_id

def test_create_subproject_missing_project_id(client, db_session):
    """Teste la création d'un sous-projet sans 'project_id'."""
    subproject_data = {
        "title": "Sous-Projet sans Projet",
        "mermaid_definition": "graph TD\nA --> B"
    }
    response = client.post(SUBPROJECTS_URL, json=subproject_data)

    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "project_id" in data['error']

def test_create_subproject_invalid_project_id(client, db_session):
    """Teste la création d'un sous-projet avec un 'project_id' inexistant."""
    subproject_data = {
        "project_id": 9999, # ID inexistant
        "title": "Sous-Projet avec Projet Invalide",
        "mermaid_definition": "graph TD\nA --> B"
    }
    response = client.post(SUBPROJECTS_URL, json=subproject_data)

    assert response.status_code == 404 # On attend une 404 car le FK n'existe pas
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "Project ID" in data['error'] and "not found" in data['error']

def test_create_subproject_missing_title(client, db_session):
    """Teste la création d'un sous-projet sans 'title'."""
    project = Project(title="Projet Parent")
    db_session.add(project)
    db_session.commit()

    subproject_data = {
        "project_id": project.id,
        "mermaid_definition": "graph TD\nA --> B"
    }
    response = client.post(SUBPROJECTS_URL, json=subproject_data)

    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "title" in data['error']

def test_create_subproject_missing_mermaid_definition(client, db_session):
    """Teste la création d'un sous-projet sans 'mermaid_definition'."""
    project = Project(title="Projet Parent")
    db_session.add(project)
    db_session.commit()

    subproject_data = {
        "project_id": project.id,
        "title": "Sous-Projet sans Mermaid"
    }
    response = client.post(SUBPROJECTS_URL, json=subproject_data)

    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "mermaid_definition" in data['error']

# --- Tests pour la lecture de tous les sous-projets (GET /api/subprojects/) ---

def test_get_all_subprojects_empty(client, db_session):
    """Teste la récupération de tous les sous-projets lorsqu'il n'y en a aucun."""
    response = client.get(SUBPROJECTS_URL)

    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))

    assert isinstance(data, list)
    assert len(data) == 0

def test_get_all_subprojects_with_data(client, db_session):
    """Teste la récupération de tous les sous-projets."""
    project1 = Project(title="Projet 1")
    project2 = Project(title="Projet 2")
    db_session.add_all([project1, project2])
    db_session.commit()

    subproject1 = SubProject(project_id=project1.id, title="SP 1", mermaid_definition="graph TD\nA --> B")
    subproject2 = SubProject(project_id=project1.id, title="SP 2", mermaid_definition="graph LR\nX --> Y")
    subproject3 = SubProject(project_id=project2.id, title="SP 3", mermaid_definition="graph TD\n1 --> 2")
    db_session.add_all([subproject1, subproject2, subproject3])
    db_session.commit()

    response = client.get(SUBPROJECTS_URL)
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 3

    # Vérifier que les données retournées correspondent
    titles = sorted([sp['title'] for sp in data])
    assert titles == ["SP 1", "SP 2", "SP 3"]
    assert all('id' in sp and 'title' in sp and 'project_id' in sp for sp in data)

def test_get_all_subprojects_filtered_by_project(client, db_session):
    """Teste la récupération de sous-projets filtrés par 'project_id'."""
    project1 = Project(title="Projet Alpha")
    project2 = Project(title="Projet Beta")
    db_session.add_all([project1, project2])
    db_session.commit()

    subproject1 = SubProject(project_id=project1.id, title="SP Alpha 1", mermaid_definition="graph TD\nA --> B")
    subproject2 = SubProject(project_id=project1.id, title="SP Alpha 2", mermaid_definition="graph LR\nX --> Y")
    subproject3 = SubProject(project_id=project2.id, title="SP Beta 1", mermaid_definition="graph TD\n1 --> 2")
    db_session.add_all([subproject1, subproject2, subproject3])
    db_session.commit()

    # Filtrer par project1.id
    response = client.get(f"{SUBPROJECTS_URL}?project_id={project1.id}")
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert len(data) == 2
    titles = sorted([sp['title'] for sp in data])
    assert titles == ["SP Alpha 1", "SP Alpha 2"]

    # Filtrer par project2.id
    response = client.get(f"{SUBPROJECTS_URL}?project_id={project2.id}")
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['title'] == "SP Beta 1"

    # Filtrer par un project_id qui n'a pas de sous-projets
    response = client.get(f"{SUBPROJECTS_URL}?project_id=9999")
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert len(data) == 0

# --- Tests pour la lecture d'un sous-projet par ID (GET /api/subprojects/<id>) ---

def test_get_subproject_by_id_success(client, db_session):
    """Teste la récupération réussie d'un sous-projet par son ID."""
    project = Project(title="Projet pour Lecture")
    db_session.add(project)
    db_session.commit()

    subproject = SubProject(project_id=project.id, title="Sous-Projet à Lire", mermaid_definition="graph TD\nStart --> End")
    db_session.add(subproject)
    db_session.commit()
    subproject_id = subproject.id

    response = client.get(f"{SUBPROJECTS_URL}{subproject_id}")

    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))

    assert data['id'] == subproject_id
    assert data['title'] == "Sous-Projet à Lire"
    assert data['project_id'] == project.id
    assert data['mermaid_definition'] == "graph TD\nStart --> End"

def test_get_subproject_by_id_not_found(client, db_session):
    """Teste la récupération d'un sous-projet avec un ID inexistant."""
    non_existent_id = 9999
    response = client.get(f"{SUBPROJECTS_URL}{non_existent_id}")

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert str(non_existent_id) in data['error']

# --- Tests pour la mise à jour d'un sous-projet (PUT /api/subprojects/<id>) ---

def test_update_subproject_success(client, db_session):
    """Teste la mise à jour réussie d'un sous-projet existant."""
    project1 = Project(title="Projet Parent 1")
    project2 = Project(title="Projet Parent 2")
    db_session.add_all([project1, project2])
    db_session.commit()

    subproject = SubProject(project_id=project1.id, title="SP à Modifier", mermaid_definition="graph TD\nA --> B")
    db_session.add(subproject)
    db_session.commit()
    subproject_id = subproject.id

    update_data = {
        "project_id": project2.id, # Changer le projet parent
        "title": "SP Modifié avec Succès",
        "mermaid_definition": "graph LR\nX --> Y",
        "visual_layout": {"some": "layout"} # Ajouter le champ visual_layout
    }
    response = client.put(f"{SUBPROJECTS_URL}{subproject_id}", json=update_data)

    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))

    assert data['id'] == subproject_id
    assert data['title'] == update_data['title']
    assert data['project_id'] == project2.id
    assert data['mermaid_definition'] == update_data['mermaid_definition']
    assert data['visual_layout'] == update_data['visual_layout']

    # Vérification dans la base de données
    updated_subproject = db_session.get(SubProject, subproject_id)
    assert updated_subproject is not None
    assert updated_subproject.title == update_data['title']
    assert updated_subproject.project_id == project2.id
    assert updated_subproject.mermaid_definition == update_data['mermaid_definition']
    assert updated_subproject.visual_layout == update_data['visual_layout']

def test_update_subproject_not_found(client, db_session):
    """Teste la mise à jour d'un sous-projet avec un ID inexistant."""
    non_existent_id = 9999
    update_data = {"title": "Nouveau Titre", "project_id": 1, "mermaid_definition": "graph TD\n1 --> 2"}
    response = client.put(f"{SUBPROJECTS_URL}{non_existent_id}", json=update_data)

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert str(non_existent_id) in data['error']

def test_update_subproject_invalid_project_id(client, db_session):
    """Teste la mise à jour d'un sous-projet avec un 'project_id' inexistant."""
    project1 = Project(title="Projet Parent 1")
    db_session.add(project1)
    db_session.commit()

    subproject = SubProject(project_id=project1.id, title="SP à Modifier Projet Invalide", mermaid_definition="graph TD\nA --> B")
    db_session.add(subproject)
    db_session.commit()
    subproject_id = subproject.id

    update_data = {
        "project_id": 9999, # ID inexistant
        "title": "Titre Modifié",
        "mermaid_definition": "graph LR\nX --> Y"
    }
    response = client.put(f"{SUBPROJECTS_URL}{subproject_id}", json=update_data)

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "Project ID" in data['error'] and "not found" in data['error']

def test_update_subproject_invalid_data(client, db_session):
    """Teste la mise à jour d'un sous-projet avec des données invalides (titre vide)."""
    project = Project(title="Projet Parent")
    db_session.add(project)
    db_session.commit()

    subproject = SubProject(project_id=project.id, title="SP avec Titre Vide", mermaid_definition="graph TD\nA --> B")
    db_session.add(subproject)
    db_session.commit()
    subproject_id = subproject.id

    update_data = {"title": "", "project_id": project.id, "mermaid_definition": "graph TD\n1 --> 2"}
    response = client.put(f"{SUBPROJECTS_URL}{subproject_id}", json=update_data)

    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "title" in data['error']

# --- Tests pour la suppression d'un sous-projet (DELETE /api/subprojects/<id>) ---

def test_delete_subproject_success(client, db_session):
    """Teste la suppression réussie d'un sous-projet existant."""
    project = Project(title="Projet Parent pour Suppression")
    db_session.add(project)
    db_session.commit()

    subproject = SubProject(project_id=project.id, title="SP à Supprimer", mermaid_definition="graph TD\nA --> B")
    db_session.add(subproject)
    db_session.commit()
    subproject_id = subproject.id

    response = client.delete(f"{SUBPROJECTS_URL}{subproject_id}")

    assert response.status_code == 204 # No Content

    # Vérifier que le sous-projet a bien été supprimé
    deleted_subproject = db_session.get(SubProject, subproject_id)
    assert deleted_subproject is None

def test_delete_subproject_not_found(client, db_session):
    """Teste la suppression d'un sous-projet avec un ID inexistant."""
    non_existent_id = 9999
    response = client.delete(f"{SUBPROJECTS_URL}{non_existent_id}")

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert str(non_existent_id) in data['error']

# Note: Les tests pour la cascade de suppression (suppression d'un projet supprime ses sous-projets)
# devraient être ajoutés dans test_projects.py pour une couverture complète.