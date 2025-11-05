# backend/tests/test_nodes.py
# Version 1.0

import pytest
import json
from app.models import Project, SubProject, Node

# Base URL pour les endpoints de nœuds
NODES_URL = '/api/nodes/'

# --- Tests pour la création de nœud (POST /api/nodes/) ---

def test_create_node_success(client, db_session):
    """Teste la création réussie d'un nouveau nœud."""
    # Pré-requis : Créer un projet parent et un sous-projet
    project = Project(title="Projet Parent Pour Nœud")
    subproject = SubProject(project_id=project.id, title="Sous-Projet Pour Nœud", mermaid_definition="graph TD\nStart --> End")
    db_session.add_all([project, subproject])
    db_session.commit()
    subproject_id = subproject.id

    node_data = {
        "subproject_id": subproject_id,
        "mermaid_id": "A",
        "title": "Nœud Initial",
        "text_content": "Contenu du nœud A",
        "style_class_ref": "blue_box"
    }

    response = client.post(NODES_URL, json=node_data)

    assert response.status_code == 201
    data = json.loads(response.get_data(as_text=True))

    assert data['subproject_id'] == subproject_id
    assert data['mermaid_id'] == "A"
    assert data['title'] == "Nœud Initial"
    assert data['text_content'] == "Contenu du nœud A"
    assert data['style_class_ref'] == "blue_box"
    assert 'id' in data
    assert data['id'] is not None

    # Vérification dans la base de données
    created_node = db_session.get(Node, data['id'])
    assert created_node is not None
    assert created_node.subproject_id == subproject_id
    assert created_node.mermaid_id == "A"

def test_create_node_success_minimal(client, db_session):
    """Teste la création réussie d'un nœud avec les champs minimums."""
    project = Project(title="Projet Minimal Nœud")
    subproject = SubProject(project_id=project.id, title="Sous-Projet Minimal Nœud", mermaid_definition="graph TD\nStart --> End")
    db_session.add_all([project, subproject])
    db_session.commit()
    subproject_id = subproject.id

    node_data = {
        "subproject_id": subproject_id,
        "mermaid_id": "B",
        # title et text_content peuvent être omis si mermaid_id est utilisé comme fallback
        # style_class_ref est optionnel
    }

    response = client.post(NODES_URL, json=node_data)

    assert response.status_code == 201
    data = json.loads(response.get_data(as_text=True))

    assert data['subproject_id'] == subproject_id
    assert data['mermaid_id'] == "B"
    # Le titre et text_content devraient être déduits de mermaid_id par le service
    assert data['title'] is None or data['title'] == "B" # Peut être None ou le mermaid_id selon l'implémentation du service
    assert data['text_content'] is None or data['text_content'] == "B" # Idem
    assert data['style_class_ref'] is None
    assert 'id' in data

def test_create_node_missing_subproject_id(client, db_session):
    """Teste la création d'un nœud sans 'subproject_id'."""
    node_data = {
        "mermaid_id": "C",
        "title": "Nœud sans Projet",
        "text_content": "Contenu"
    }
    response = client.post(NODES_URL, json=node_data)

    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "subproject_id" in data['error']

def test_create_node_invalid_subproject_id(client, db_session):
    """Teste la création d'un nœud avec un 'subproject_id' inexistant."""
    node_data = {
        "subproject_id": 9999, # ID inexistant
        "mermaid_id": "D",
        "title": "Nœud avec Projet Invalide",
        "text_content": "Contenu"
    }
    response = client.post(NODES_URL, json=node_data)

    assert response.status_code == 404 # On attend une 404 car le FK n'existe pas
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "SubProject ID" in data['error'] and "not found" in data['error']

def test_create_node_missing_mermaid_id(client, db_session):
    """Teste la création d'un nœud sans 'mermaid_id'."""
    project = Project(title="Projet")
    subproject = SubProject(project_id=project.id, title="Sous-Projet", mermaid_definition="graph TD\nStart --> End")
    db_session.add_all([project, subproject])
    db_session.commit()

    node_data = {
        "subproject_id": subproject.id,
        "title": "Nœud sans Mermaid ID",
        "text_content": "Contenu"
    }
    response = client.post(NODES_URL, json=node_data)

    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "mermaid_id" in data['error']

def test_create_node_duplicate_mermaid_id(client, db_session):
    """Teste la création d'un nœud avec un 'mermaid_id' déjà existant dans le même sous-projet."""
    project = Project(title="Projet Duplicate")
    subproject = SubProject(project_id=project.id, title="Sous-Projet Duplicate", mermaid_definition="graph TD\nA --> B")
    db_session.add_all([project, subproject])
    db_session.commit()

    # Créer le premier nœud
    node1 = Node(subproject_id=subproject.id, mermaid_id="DUP", title="Nœud Dupliqué 1", text_content="Contenu 1")
    db_session.add(node1)
    db_session.commit()

    # Essayer de créer un deuxième nœud avec le même mermaid_id et subproject_id
    node_data = {
        "subproject_id": subproject.id,
        "mermaid_id": "DUP",
        "title": "Nœud Dupliqué 2",
        "text_content": "Contenu 2"
    }
    response = client.post(NODES_URL, json=node_data)

    assert response.status_code == 400 # On attend une erreur d'intégrité / BadRequest
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "mermaid_id" in data['error'] and "already exists" in data['error']

# --- Tests pour la lecture de tous les nœuds (GET /api/nodes/) ---

def test_get_all_nodes_empty(client, db_session):
    """Teste la récupération de tous les nœuds lorsqu'il n'y en a aucun."""
    response = client.get(NODES_URL)

    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))

    assert isinstance(data, list)
    assert len(data) == 0

def test_get_all_nodes_with_data(client, db_session):
    """Teste la récupération de tous les nœuds."""
    project = Project(title="Projet Nœuds")
    subproject1 = SubProject(project_id=project.id, title="SP Nœuds 1", mermaid_definition="graph TD\nA --> B")
    subproject2 = SubProject(project_id=project.id, title="SP Nœuds 2", mermaid_definition="graph LR\nX --> Y")
    db_session.add_all([project, subproject1, subproject2])
    db_session.commit()

    node1 = Node(subproject_id=subproject1.id, mermaid_id="N1", title="Nœud 1", text_content="Contenu 1")
    node2 = Node(subproject_id=subproject1.id, mermaid_id="N2", title="Nœud 2", text_content="Contenu 2")
    node3 = Node(subproject_id=subproject2.id, mermaid_id="N3", title="Nœud 3", text_content="Contenu 3")
    db_session.add_all([node1, node2, node3])
    db_session.commit()

    response = client.get(NODES_URL)
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 3

    # Vérifier que les données retournées correspondent
    mermaid_ids = sorted([n['mermaid_id'] for n in data])
    assert mermaid_ids == ["N1", "N2", "N3"]
    assert all('id' in n and 'subproject_id' in n and 'mermaid_id' in n for n in data)

def test_get_all_nodes_filtered_by_subproject(client, db_session):
    """Teste la récupération de nœuds filtrés par 'subproject_id'."""
    project = Project(title="Projet Nœuds Filtré")
    subproject1 = SubProject(project_id=project.id, title="SP Filtré Alpha", mermaid_definition="graph TD\nA --> B")
    subproject2 = SubProject(project_id=project.id, title="SP Filtré Beta", mermaid_definition="graph LR\nX --> Y")
    db_session.add_all([project, subproject1, subproject2])
    db_session.commit()

    node1 = Node(subproject_id=subproject1.id, mermaid_id="NA1", title="Nœud A1", text_content="Contenu A1")
    node2 = Node(subproject_id=subproject1.id, mermaid_id="NA2", title="Nœud A2", text_content="Contenu A2")
    node3 = Node(subproject_id=subproject2.id, mermaid_id="NB1", title="Nœud B1", text_content="Contenu B1")
    db_session.add_all([node1, node2, node3])
    db_session.commit()

    # Filtrer par subproject1.id
    response = client.get(f"{NODES_URL}?subproject_id={subproject1.id}")
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert len(data) == 2
    mermaid_ids = sorted([n['mermaid_id'] for n in data])
    assert mermaid_ids == ["NA1", "NA2"]

    # Filtrer par subproject2.id
    response = client.get(f"{NODES_URL}?subproject_id={subproject2.id}")
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['mermaid_id'] == "NB1"

    # Filtrer par un subproject_id qui n'a pas de nœuds
    response = client.get(f"{NODES_URL}?subproject_id=9999")
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert len(data) == 0

# --- Tests pour la lecture d'un nœud par ID (GET /api/nodes/<id>) ---

def test_get_node_by_id_success(client, db_session):
    """Teste la récupération réussie d'un nœud par son ID."""
    project = Project(title="Projet Lecture Nœud")
    subproject = SubProject(project_id=project.id, title="SP Lecture Nœud", mermaid_definition="graph TD\nStart --> End")
    db_session.add_all([project, subproject])
    db_session.commit()

    node = Node(subproject_id=subproject.id, mermaid_id="READ_N", title="Nœud à Lire", text_content="Contenu du nœud à lire", style_class_ref="important")
    db_session.add(node)
    db_session.commit()
    node_id = node.id

    response = client.get(f"{NODES_URL}{node_id}")

    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))

    assert data['id'] == node_id
    assert data['subproject_id'] == subproject.id
    assert data['mermaid_id'] == "READ_N"
    assert data['title'] == "Nœud à Lire"
    assert data['text_content'] == "Contenu du nœud à lire"
    assert data['style_class_ref'] == "important"

def test_get_node_by_id_not_found(client, db_session):
    """Teste la récupération d'un nœud avec un ID inexistant."""
    non_existent_id = 9999
    response = client.get(f"{NODES_URL}{non_existent_id}")

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert str(non_existent_id) in data['error']

# --- Tests pour la mise à jour d'un nœud (PUT /api/nodes/<id>) ---

def test_update_node_success(client, db_session):
    """Teste la mise à jour réussie d'un nœud existant."""
    project = Project(title="Projet Mise à Jour Nœud")
    subproject = SubProject(project_id=project.id, title="SP Mise à Jour Nœud", mermaid_definition="graph TD\nA --> B")
    db_session.add_all([project, subproject])
    db_session.commit()

    node = Node(subproject_id=subproject.id, mermaid_id="OLD_ID", title="Nœud Ancien Titre", text_content="Ancien contenu", style_class_ref="old_style")
    db_session.add(node)
    db_session.commit()
    node_id = node.id

    update_data = {
        "subproject_id": subproject.id, # Garder le même subproject
        "mermaid_id": "NEW_ID", # Changer le mermaid_id
        "title": "Nœud Nouveau Titre",
        "text_content": "Nouveau contenu",
        "style_class_ref": "new_style"
    }
    response = client.put(f"{NODES_URL}{node_id}", json=update_data)

    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))

    assert data['id'] == node_id
    assert data['subproject_id'] == subproject.id
    assert data['mermaid_id'] == "NEW_ID"
    assert data['title'] == "Nœud Nouveau Titre"
    assert data['text_content'] == "Nouveau contenu"
    assert data['style_class_ref'] == "new_style"

    # Vérification dans la base de données
    updated_node = db_session.get(Node, node_id)
    assert updated_node is not None
    assert updated_node.mermaid_id == "NEW_ID"
    assert updated_node.title == "Nœud Nouveau Titre"

def test_update_node_not_found(client, db_session):
    """Teste la mise à jour d'un nœud avec un ID inexistant."""
    non_existent_id = 9999
    update_data = {"subproject_id": 1, "mermaid_id": "NEW_ID", "title": "Nouveau Titre", "text_content": "Contenu"}
    response = client.put(f"{NODES_URL}{non_existent_id}", json=update_data)

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert str(non_existent_id) in data['error']

def test_update_node_invalid_subproject_id(client, db_session):
    """Teste la mise à jour d'un nœud avec un 'subproject_id' inexistant."""
    project = Project(title="Projet SP Invalide")
    subproject = SubProject(project_id=project.id, title="SP original", mermaid_definition="graph TD\nA --> B")
    db_session.add_all([project, subproject])
    db_session.commit()

    node = Node(subproject_id=subproject.id, mermaid_id="OLD_ID", title="Nœud", text_content="Contenu")
    db_session.add(node)
    db_session.commit()
    node_id = node.id

    update_data = {
        "subproject_id": 9999, # ID inexistant
        "mermaid_id": "NEW_ID",
        "title": "Nouveau Titre",
        "text_content": "Nouveau contenu"
    }
    response = client.put(f"{NODES_URL}{node_id}", json=update_data)

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "SubProject ID" in data['error'] and "not found" in data['error']

def test_update_node_duplicate_mermaid_id(client, db_session):
    """Teste la mise à jour d'un nœud pour lui donner un 'mermaid_id' déjà utilisé dans le même sous-projet."""
    project = Project(title="Projet Duplicate Update")
    subproject = SubProject(project_id=project.id, title="SP Duplicate Update", mermaid_definition="graph TD\nA --> B\nC --> D")
    db_session.add_all([project, subproject])
    db_session.commit()

    # Créer deux nœuds existants
    node1 = Node(subproject_id=subproject.id, mermaid_id="N1", title="Nœud 1", text_content="Contenu 1")
    node2 = Node(subproject_id=subproject.id, mermaid_id="N2", title="Nœud 2", text_content="Contenu 2")
    db_session.add_all([node1, node2])
    db_session.commit()
    node1_id = node1.id

    # Essayer de renommer node1 pour qu'il ait le mermaid_id de node2
    update_data = {
        "subproject_id": subproject.id,
        "mermaid_id": "N2", # Mermaid ID déjà utilisé par node2
        "title": "Nœud 1 Renommé",
        "text_content": "Nouveau contenu 1"
    }
    response = client.put(f"{NODES_URL}{node1_id}", json=update_data)

    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "mermaid_id" in data['error'] and "already exists" in data['error']

def test_update_node_change_subproject_to_duplicate_mermaid_id(client, db_session):
    """Teste le changement de subproject_id d'un nœud vers un SP où son mermaid_id existe déjà."""
    project = Project(title="Projet SP Duplicate Update")
    subproject1 = SubProject(project_id=project.id, title="SP Original", mermaid_definition="graph TD\nA --> B")
    subproject2 = SubProject(project_id=project.id, title="SP Cible Duplicate", mermaid_definition="graph LR\nX --> Y")
    db_session.add_all([project, subproject1, subproject2])
    db_session.commit()

    # Créer un nœud dans subproject1
    node_to_move = Node(subproject_id=subproject1.id, mermaid_id="MOVE_ME", title="Nœud à déplacer", text_content="Contenu")
    # Créer un autre nœud dans subproject2 avec le même mermaid_id
    existing_node_in_target = Node(subproject_id=subproject2.id, mermaid_id="MOVE_ME", title="Nœud existant", text_content="Contenu cible")
    db_session.add_all([node_to_move, existing_node_in_target])
    db_session.commit()
    node_to_move_id = node_to_move.id

    # Essayer de déplacer node_to_move vers subproject2
    update_data = {
        "subproject_id": subproject2.id, # Cible avec un mermaid_id existant
        "mermaid_id": "MOVE_ME",
        "title": "Nœud déplacé",
        "text_content": "Nouveau contenu"
    }
    response = client.put(f"{NODES_URL}{node_to_move_id}", json=update_data)

    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "mermaid_id" in data['error'] and "already exists" in data['error']


# --- Tests pour la suppression d'un nœud (DELETE /api/nodes/<id>) ---

def test_delete_node_success(client, db_session):
    """Teste la suppression réussie d'un nœud existant."""
    project = Project(title="Projet Suppression Nœud")
    subproject = SubProject(project_id=project.id, title="SP Suppression Nœud", mermaid_definition="graph TD\nA --> B")
    db_session.add_all([project, subproject])
    db_session.commit()

    node = Node(subproject_id=subproject.id, mermaid_id="DEL_N", title="Nœud à Supprimer", text_content="Contenu")
    db_session.add(node)
    db_session.commit()
    node_id = node.id

    response = client.delete(f"{NODES_URL}{node_id}")

    assert response.status_code == 204 # No Content

    # Vérifier que le nœud a bien été supprimé
    deleted_node = db_session.get(Node, node_id)
    assert deleted_node is None

def test_delete_node_not_found(client, db_session):
    """Teste la suppression d'un nœud avec un ID inexistant."""
    non_existent_id = 9999
    response = client.delete(f"{NODES_URL}{non_existent_id}")

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert str(non_existent_id) in data['error']

# Note: Les tests pour la suppression en cascade (suppression d'un sous-projet supprime ses nœuds)
# devraient être ajoutés dans test_subprojects.py pour une couverture complète.