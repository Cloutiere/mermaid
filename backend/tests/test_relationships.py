# backend/tests/test_relationships.py
# Version 1.0

import pytest
import json
from app.models import Project, SubProject, Node, Relationship, LinkType

# Base URL pour les endpoints de relations
RELATIONSHIPS_URL = '/api/nodes/relationships' # Note: L'API est sous /api/nodes/relationships

# --- Tests pour la création de relation (POST /api/nodes/relationships) ---

def test_create_relationship_success(client, db_session):
    """Teste la création réussie d'une nouvelle relation."""
    # Pré-requis : Créer un projet, un sous-projet et deux nœuds dans le même sous-projet
    project = Project(title="Projet Relation")
    subproject = SubProject(project_id=project.id, title="SP Relation", mermaid_definition="graph TD\nA --> B")
    db_session.add_all([project, subproject])
    db_session.commit()

    node_a = Node(subproject_id=subproject.id, mermaid_id="A", title="Nœud A", text_content="Contenu A")
    node_b = Node(subproject_id=subproject.id, mermaid_id="B", title="Nœud B", text_content="Contenu B")
    db_session.add_all([node_a, node_b])
    db_session.commit()

    relationship_data = {
        "subproject_id": subproject.id,
        "source_node_id": node_a.id,
        "target_node_id": node_b.id,
        "label": "Connecte",
        "link_type": "VISIBLE" # Utilise l'enum string
    }

    response = client.post(RELATIONSHIPS_URL, json=relationship_data)

    assert response.status_code == 201
    data = json.loads(response.get_data(as_text=True))

    assert data['subproject_id'] == subproject.id
    assert data['source_node_id'] == node_a.id
    assert data['target_node_id'] == node_b.id
    assert data['label'] == "Connecte"
    assert data['link_type'] == "VISIBLE"
    assert 'id' in data
    assert data['id'] is not None

    # Vérification dans la base de données
    created_relationship = db_session.get(Relationship, data['id'])
    assert created_relationship is not None
    assert created_relationship.subproject_id == subproject.id
    assert created_relationship.source_node_id == node_a.id
    assert created_relationship.link_type == LinkType.VISIBLE

def test_create_relationship_success_invisible_link(client, db_session):
    """Teste la création d'une relation de type invisible."""
    project = Project(title="Projet Relation Invisible")
    subproject = SubProject(project_id=project.id, title="SP Relation Invisible", mermaid_definition="graph TD\nA --- B")
    db_session.add_all([project, subproject])
    db_session.commit()

    node_a = Node(subproject_id=subproject.id, mermaid_id="A", title="Nœud A", text_content="Contenu A")
    node_b = Node(subproject_id=subproject.id, mermaid_id="B", title="Nœud B", text_content="Contenu B")
    db_session.add_all([node_a, node_b])
    db_session.commit()

    relationship_data = {
        "subproject_id": subproject.id,
        "source_node_id": node_a.id,
        "target_node_id": node_b.id,
        "link_type": "INVISIBLE" # Utilise l'enum string
    }

    response = client.post(RELATIONSHIPS_URL, json=relationship_data)

    assert response.status_code == 201
    data = json.loads(response.get_data(as_text=True))

    assert data['link_type'] == "INVISIBLE"

    # Vérification dans la base de données
    created_relationship = db_session.get(Relationship, data['id'])
    assert created_relationship is not None
    assert created_relationship.link_type == LinkType.INVISIBLE

def test_create_relationship_missing_subproject_id(client, db_session):
    """Teste la création d'une relation sans 'subproject_id'."""
    # Créer les nœuds nécessaires
    project = Project(title="Projet Sans SPID")
    subproject = SubProject(project_id=project.id, title="SP Sans SPID", mermaid_definition="graph TD\nA --> B")
    db_session.add_all([project, subproject])
    db_session.commit()
    node_a = Node(subproject_id=subproject.id, mermaid_id="A", title="Nœud A", text_content="Contenu A")
    node_b = Node(subproject_id=subproject.id, mermaid_id="B", title="Nœud B", text_content="Contenu B")
    db_session.add_all([node_a, node_b])
    db_session.commit()

    relationship_data = {
        # "subproject_id": subproject.id, # Manquant
        "source_node_id": node_a.id,
        "target_node_id": node_b.id,
        "link_type": "VISIBLE"
    }
    response = client.post(RELATIONSHIPS_URL, json=relationship_data)

    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "subproject_id" in data['error']

def test_create_relationship_invalid_subproject_id(client, db_session):
    """Teste la création d'une relation avec un 'subproject_id' inexistant."""
    # Créer les nœuds nécessaires
    project = Project(title="Projet SP Invalide")
    subproject = SubProject(project_id=project.id, title="SP SP Invalide", mermaid_definition="graph TD\nA --> B")
    db_session.add_all([project, subproject])
    db_session.commit()
    node_a = Node(subproject_id=subproject.id, mermaid_id="A", title="Nœud A", text_content="Contenu A")
    node_b = Node(subproject_id=subproject.id, mermaid_id="B", title="Nœud B", text_content="Contenu B")
    db_session.add_all([node_a, node_b])
    db_session.commit()

    relationship_data = {
        "subproject_id": 9999, # ID inexistant
        "source_node_id": node_a.id,
        "target_node_id": node_b.id,
        "link_type": "VISIBLE"
    }
    response = client.post(RELATIONSHIPS_URL, json=relationship_data)

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "SubProject ID" in data['error'] and "not found" in data['error']

def test_create_relationship_missing_source_node_id(client, db_session):
    """Teste la création d'une relation sans 'source_node_id'."""
    project = Project(title="Projet Sans Source")
    subproject = SubProject(project_id=project.id, title="SP Sans Source", mermaid_definition="graph TD\nA --> B")
    db_session.add_all([project, subproject])
    db_session.commit()
    node_b = Node(subproject_id=subproject.id, mermaid_id="B", title="Nœud B", text_content="Contenu B")
    db_session.add(node_b)
    db_session.commit()

    relationship_data = {
        "subproject_id": subproject.id,
        # "source_node_id": node_a.id, # Manquant
        "target_node_id": node_b.id,
        "link_type": "VISIBLE"
    }
    response = client.post(RELATIONSHIPS_URL, json=relationship_data)

    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "source_node_id" in data['error']

def test_create_relationship_invalid_source_node_id(client, db_session):
    """Teste la création d'une relation avec un 'source_node_id' inexistant."""
    project = Project(title="Projet Source Invalide")
    subproject = SubProject(project_id=project.id, title="SP Source Invalide", mermaid_definition="graph TD\nA --> B")
    db_session.add_all([project, subproject])
    db_session.commit()
    node_b = Node(subproject_id=subproject.id, mermaid_id="B", title="Nœud B", text_content="Contenu B")
    db_session.add(node_b)
    db_session.commit()

    relationship_data = {
        "subproject_id": subproject.id,
        "source_node_id": 9999, # ID inexistant
        "target_node_id": node_b.id,
        "link_type": "VISIBLE"
    }
    response = client.post(RELATIONSHIPS_URL, json=relationship_data)

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "Source Node ID" in data['error'] and "not found" in data['error']

def test_create_relationship_missing_target_node_id(client, db_session):
    """Teste la création d'une relation sans 'target_node_id'."""
    project = Project(title="Projet Sans Target")
    subproject = SubProject(project_id=project.id, title="SP Sans Target", mermaid_definition="graph TD\nA --> B")
    db_session.add_all([project, subproject])
    db_session.commit()
    node_a = Node(subproject_id=subproject.id, mermaid_id="A", title="Nœud A", text_content="Contenu A")
    db_session.add(node_a)
    db_session.commit()

    relationship_data = {
        "subproject_id": subproject.id,
        "source_node_id": node_a.id,
        # "target_node_id": node_b.id, # Manquant
        "link_type": "VISIBLE"
    }
    response = client.post(RELATIONSHIPS_URL, json=relationship_data)

    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "target_node_id" in data['error']

def test_create_relationship_invalid_target_node_id(client, db_session):
    """Teste la création d'une relation avec un 'target_node_id' inexistant."""
    project = Project(title="Projet Target Invalide")
    subproject = SubProject(project_id=project.id, title="SP Target Invalide", mermaid_definition="graph TD\nA --> B")
    db_session.add_all([project, subproject])
    db_session.commit()
    node_a = Node(subproject_id=subproject.id, mermaid_id="A", title="Nœud A", text_content="Contenu A")
    db_session.add(node_a)
    db_session.commit()

    relationship_data = {
        "subproject_id": subproject.id,
        "source_node_id": node_a.id,
        "target_node_id": 9999, # ID inexistant
        "link_type": "VISIBLE"
    }
    response = client.post(RELATIONSHIPS_URL, json=relationship_data)

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "Target Node ID" in data['error'] and "not found" in data['error']

def test_create_relationship_nodes_in_different_subprojects(client, db_session):
    """Teste la création d'une relation où source et target sont dans des sous-projets différents."""
    project = Project(title="Projet SP Différents")
    subproject1 = SubProject(project_id=project.id, title="SP 1", mermaid_definition="graph TD\nA --> B")
    subproject2 = SubProject(project_id=project.id, title="SP 2", mermaid_definition="graph TD\nC --> D")
    db_session.add_all([project, subproject1, subproject2])
    db_session.commit()

    node_a = Node(subproject_id=subproject1.id, mermaid_id="A", title="Nœud A", text_content="Contenu A")
    node_c = Node(subproject_id=subproject2.id, mermaid_id="C", title="Nœud C", text_content="Contenu C") # Nœud dans un autre SP
    db_session.add_all([node_a, node_c])
    db_session.commit()

    relationship_data = {
        "subproject_id": subproject1.id, # Le subproject_id de la relation DOIT correspondre au SP des nœuds
        "source_node_id": node_a.id,
        "target_node_id": node_c.id, # Nœud C est dans subproject2
        "link_type": "VISIBLE"
    }
    response = client.post(RELATIONSHIPS_URL, json=relationship_data)

    assert response.status_code == 400 # On attend une erreur car les nœuds ne sont pas dans le même SP
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "Source node and target node must belong to the same SubProject" in data['error']

# --- Tests pour la lecture de toutes les relations (GET /api/nodes/relationships) ---

def test_get_all_relationships_empty(client, db_session):
    """Teste la récupération de toutes les relations lorsqu'il n'y en a aucune."""
    response = client.get(RELATIONSHIPS_URL)

    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))

    assert isinstance(data, list)
    assert len(data) == 0

def test_get_all_relationships_with_data(client, db_session):
    """Teste la récupération de toutes les relations."""
    project = Project(title="Projet Relations Liste")
    subproject1 = SubProject(project_id=project.id, title="SP Liste 1", mermaid_definition="graph TD\nA --> B")
    subproject2 = SubProject(project_id=project.id, title="SP Liste 2", mermaid_definition="graph LR\nX --> Y")
    db_session.add_all([project, subproject1, subproject2])
    db_session.commit()

    node_a1 = Node(subproject_id=subproject1.id, mermaid_id="A1", title="Nœud A1", text_content="Contenu A1")
    node_b1 = Node(subproject_id=subproject1.id, mermaid_id="B1", title="Nœud B1", text_content="Contenu B1")
    node_x2 = Node(subproject_id=subproject2.id, mermaid_id="X2", title="Nœud X2", text_content="Contenu X2")
    node_y2 = Node(subproject_id=subproject2.id, mermaid_id="Y2", title="Nœud Y2", text_content="Contenu Y2")
    db_session.add_all([node_a1, node_b1, node_x2, node_y2])
    db_session.commit()

    rel1 = Relationship(subproject_id=subproject1.id, source_node_id=node_a1.id, target_node_id=node_b1.id, link_type=LinkType.VISIBLE, label="Lien 1")
    rel2 = Relationship(subproject_id=subproject1.id, source_node_id=node_b1.id, target_node_id=node_a1.id, link_type=LinkType.INVISIBLE)
    rel3 = Relationship(subproject_id=subproject2.id, source_node_id=node_x2.id, target_node_id=node_y2.id, link_type=LinkType.VISIBLE, label="Lien 3")
    db_session.add_all([rel1, rel2, rel3])
    db_session.commit()

    response = client.get(RELATIONSHIPS_URL)
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 3

    # Vérifier que les données retournées correspondent
    rel_ids = sorted([r['id'] for r in data])
    assert rel_ids == sorted([rel1.id, rel2.id, rel3.id])
    assert all('id' in r and 'subproject_id' in r and 'source_node_id' in r and 'target_node_id' in r for r in data)

def test_get_all_relationships_filtered_by_subproject(client, db_session):
    """Teste la récupération de relations filtrées par 'subproject_id'."""
    project = Project(title="Projet Relations Filtré")
    subproject1 = SubProject(project_id=project.id, title="SP Filtré Alpha", mermaid_definition="graph TD\nA --> B")
    subproject2 = SubProject(project_id=project.id, title="SP Filtré Beta", mermaid_definition="graph LR\nX --> Y")
    db_session.add_all([project, subproject1, subproject2])
    db_session.commit()

    node_a1 = Node(subproject_id=subproject1.id, mermaid_id="A1", title="Nœud A1", text_content="Contenu A1")
    node_b1 = Node(subproject_id=subproject1.id, mermaid_id="B1", title="Nœud B1", text_content="Contenu B1")
    node_x2 = Node(subproject_id=subproject2.id, mermaid_id="X2", title="Nœud X2", text_content="Contenu X2")
    db_session.add_all([node_a1, node_b1, node_x2])
    db_session.commit()

    rel1 = Relationship(subproject_id=subproject1.id, source_node_id=node_a1.id, target_node_id=node_b1.id, link_type=LinkType.VISIBLE)
    rel2 = Relationship(subproject_id=subproject1.id, source_node_id=node_b1.id, target_node_id=node_a1.id, link_type=LinkType.VISIBLE)
    rel3 = Relationship(subproject_id=subproject2.id, source_node_id=node_x2.id, target_node_id=node_a1.id, link_type=LinkType.VISIBLE) # Relation inter-SP non autorisée pour la création, mais on la met ici pour le test de lecture
    db_session.add_all([rel1, rel2, rel3])
    db_session.commit()

    # Filtrer par subproject1.id
    response = client.get(f"{RELATIONSHIPS_URL}?subproject_id={subproject1.id}")
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert len(data) == 2
    rel_ids = sorted([r['id'] for r in data])
    assert rel_ids == sorted([rel1.id, rel2.id])

    # Filtrer par subproject2.id
    response = client.get(f"{RELATIONSHIPS_URL}?subproject_id={subproject2.id}")
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['id'] == rel3.id

    # Filtrer par un subproject_id qui n'a pas de relations
    response = client.get(f"{RELATIONSHIPS_URL}?subproject_id=9999")
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert len(data) == 0

# --- Tests pour la lecture d'une relation par ID (GET /api/nodes/relationships/<id>) ---

def test_get_relationship_by_id_success(client, db_session):
    """Teste la récupération réussie d'une relation par son ID."""
    project = Project(title="Projet Lecture Relation")
    subproject = SubProject(project_id=project.id, title="SP Lecture Relation", mermaid_definition="graph TD\nA --> B")
    db_session.add_all([project, subproject])
    db_session.commit()

    node_a = Node(subproject_id=subproject.id, mermaid_id="A", title="Nœud A", text_content="Contenu A")
    node_b = Node(subproject_id=subproject.id, mermaid_id="B", title="Nœud B", text_content="Contenu B")
    db_session.add_all([node_a, node_b])
    db_session.commit()

    relationship = Relationship(subproject_id=subproject.id, source_node_id=node_a.id, target_node_id=node_b.id, link_type=LinkType.VISIBLE, label="Lien A->B", color="#FF0000")
    db_session.add(relationship)
    db_session.commit()
    relationship_id = relationship.id

    response = client.get(f"{RELATIONSHIPS_URL}/{relationship_id}")

    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))

    assert data['id'] == relationship_id
    assert data['subproject_id'] == subproject.id
    assert data['source_node_id'] == node_a.id
    assert data['target_node_id'] == node_b.id
    assert data['label'] == "Lien A->B"
    assert data['color'] == "#FF0000"
    assert data['link_type'] == "VISIBLE"

def test_get_relationship_by_id_not_found(client, db_session):
    """Teste la récupération d'une relation avec un ID inexistant."""
    non_existent_id = 9999
    response = client.get(f"{RELATIONSHIPS_URL}/{non_existent_id}")

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert str(non_existent_id) in data['error']

# --- Tests pour la mise à jour d'une relation (PUT /api/nodes/relationships/<id>) ---

def test_update_relationship_success(client, db_session):
    """Teste la mise à jour réussie d'une relation existante."""
    project = Project(title="Projet Mise à Jour Relation")
    subproject = SubProject(project_id=project.id, title="SP Mise à Jour Relation", mermaid_definition="graph TD\nA --> B")
    db_session.add_all([project, subproject])
    db_session.commit()

    node_a = Node(subproject_id=subproject.id, mermaid_id="A", title="Nœud A", text_content="Contenu A")
    node_b = Node(subproject_id=subproject.id, mermaid_id="B", title="Nœud B", text_content="Contenu B")
    db_session.add_all([node_a, node_b])
    db_session.commit()

    relationship = Relationship(subproject_id=subproject.id, source_node_id=node_a.id, target_node_id=node_b.id, link_type=LinkType.VISIBLE, label="Ancien Label", color="#000000")
    db_session.add(relationship)
    db_session.commit()
    relationship_id = relationship.id

    update_data = {
        "subproject_id": subproject.id,
        "source_node_id": node_a.id, # Garder les mêmes nœuds pour cette mise à jour
        "target_node_id": node_b.id,
        "label": "Nouveau Label",
        "link_type": "INVISIBLE",
        "color": "#FF0000"
    }
    response = client.put(f"{RELATIONSHIPS_URL}/{relationship_id}", json=update_data)

    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))

    assert data['id'] == relationship_id
    assert data['label'] == "Nouveau Label"
    assert data['link_type'] == "INVISIBLE"
    assert data['color'] == "#FF0000"

    # Vérification dans la base de données
    updated_relationship = db_session.get(Relationship, relationship_id)
    assert updated_relationship is not None
    assert updated_relationship.label == "Nouveau Label"
    assert updated_relationship.link_type == LinkType.INVISIBLE
    assert updated_relationship.color == "#FF0000"

def test_update_relationship_change_nodes(client, db_session):
    """Teste la mise à jour d'une relation pour changer les nœuds source et cible."""
    project = Project(title="Projet Change Nœuds Relation")
    subproject = SubProject(project_id=project.id, title="SP Change Nœuds Relation", mermaid_definition="graph TD\nA --> B\nC --> D")
    db_session.add_all([project, subproject])
    db_session.commit()

    node_a = Node(subproject_id=subproject.id, mermaid_id="A", title="Nœud A", text_content="Contenu A")
    node_b = Node(subproject_id=subproject.id, mermaid_id="B", title="Nœud B", text_content="Contenu B")
    node_c = Node(subproject_id=subproject.id, mermaid_id="C", title="Nœud C", text_content="Contenu C")
    node_d = Node(subproject_id=subproject.id, mermaid_id="D", title="Nœud D", text_content="Contenu D")
    db_session.add_all([node_a, node_b, node_c, node_d])
    db_session.commit()

    relationship = Relationship(subproject_id=subproject.id, source_node_id=node_a.id, target_node_id=node_b.id, link_type=LinkType.VISIBLE)
    db_session.add(relationship)
    db_session.commit()
    relationship_id = relationship.id

    update_data = {
        "subproject_id": subproject.id,
        "source_node_id": node_c.id, # Changer la source vers C
        "target_node_id": node_d.id, # Changer la cible vers D
        "link_type": "VISIBLE"
    }
    response = client.put(f"{RELATIONSHIPS_URL}/{relationship_id}", json=update_data)

    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))

    assert data['source_node_id'] == node_c.id
    assert data['target_node_id'] == node_d.id

    # Vérification dans la base de données
    updated_relationship = db_session.get(Relationship, relationship_id)
    assert updated_relationship.source_node_id == node_c.id
    assert updated_relationship.target_node_id == node_d.id

def test_update_relationship_not_found(client, db_session):
    """Teste la mise à jour d'une relation avec un ID inexistant."""
    non_existent_id = 9999
    update_data = {"subproject_id": 1, "source_node_id": 1, "target_node_id": 2, "link_type": "VISIBLE"}
    response = client.put(f"{RELATIONSHIPS_URL}/{non_existent_id}", json=update_data)

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert str(non_existent_id) in data['error']

def test_update_relationship_invalid_subproject_id(client, db_session):
    """Teste la mise à jour d'une relation avec un 'subproject_id' inexistant."""
    project = Project(title="Projet SP Invalide Update")
    subproject = SubProject(project_id=project.id, title="SP original", mermaid_definition="graph TD\nA --> B")
    db_session.add_all([project, subproject])
    db_session.commit()

    node_a = Node(subproject_id=subproject.id, mermaid_id="A", title="Nœud A", text_content="Contenu A")
    db_session.add(node_a)
    db_session.commit()

    relationship = Relationship(subproject_id=subproject.id, source_node_id=node_a.id, target_node_id=node_a.id, link_type=LinkType.VISIBLE)
    db_session.add(relationship)
    db_session.commit()
    relationship_id = relationship.id

    update_data = {
        "subproject_id": 9999, # ID inexistant
        "source_node_id": node_a.id,
        "target_node_id": node_a.id,
        "link_type": "VISIBLE"
    }
    response = client.put(f"{RELATIONSHIPS_URL}/{relationship_id}", json=update_data)

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "SubProject ID" in data['error'] and "not found" in data['error']

def test_update_relationship_invalid_node_ids(client, db_session):
    """Teste la mise à jour d'une relation avec des 'source_node_id' ou 'target_node_id' inexistants."""
    project = Project(title="Projet Nœuds Invalides Update")
    subproject = SubProject(project_id=project.id, title="SP Nœuds Invalides", mermaid_definition="graph TD\nA --> B")
    db_session.add_all([project, subproject])
    db_session.commit()

    node_a = Node(subproject_id=subproject.id, mermaid_id="A", title="Nœud A", text_content="Contenu A")
    db_session.add(node_a)
    db_session.commit()

    relationship = Relationship(subproject_id=subproject.id, source_node_id=node_a.id, target_node_id=node_a.id, link_type=LinkType.VISIBLE)
    db_session.add(relationship)
    db_session.commit()
    relationship_id = relationship.id

    # Test avec source_node_id invalide
    update_data_source_invalid = {
        "subproject_id": subproject.id,
        "source_node_id": 9999, # ID inexistant
        "target_node_id": node_a.id,
        "link_type": "VISIBLE"
    }
    response_source = client.put(f"{RELATIONSHIPS_URL}/{relationship_id}", json=update_data_source_invalid)
    assert response_source.status_code == 404
    data_source = json.loads(response_source.get_data(as_text=True))
    assert 'error' in data_source
    assert "Source Node ID" in data_source['error'] and "not found" in data_source['error']

    # Test avec target_node_id invalide
    update_data_target_invalid = {
        "subproject_id": subproject.id,
        "source_node_id": node_a.id,
        "target_node_id": 9999, # ID inexistant
        "link_type": "VISIBLE"
    }
    response_target = client.put(f"{RELATIONSHIPS_URL}/{relationship_id}", json=update_data_target_invalid)
    assert response_target.status_code == 404
    data_target = json.loads(response_target.get_data(as_text=True))
    assert 'error' in data_target
    assert "Target Node ID" in data_target['error'] and "not found" in data_target['error']

def test_update_relationship_nodes_in_different_subprojects(client, db_session):
    """Teste la mise à jour d'une relation pour qu'elle lie des nœuds dans des sous-projets différents."""
    project = Project(title="Projet SP Différents Update")
    subproject1 = SubProject(project_id=project.id, title="SP 1", mermaid_definition="graph TD\nA --> B")
    subproject2 = SubProject(project_id=project.id, title="SP 2", mermaid_definition="graph TD\nC --> D")
    db_session.add_all([project, subproject1, subproject2])
    db_session.commit()

    node_a = Node(subproject_id=subproject1.id, mermaid_id="A", title="Nœud A", text_content="Contenu A")
    node_d = Node(subproject_id=subproject2.id, mermaid_id="D", title="Nœud D", text_content="Contenu D") # Nœud dans un autre SP
    db_session.add_all([node_a, node_d])
    db_session.commit()

    # Créer une relation initiale valide dans subproject1
    relationship = Relationship(subproject_id=subproject1.id, source_node_id=node_a.id, target_node_id=node_a.id, link_type=LinkType.VISIBLE) # Relation auto-référencée pour simplifier
    db_session.add(relationship)
    db_session.commit()
    relationship_id = relationship.id

    # Essayer de lier node_a (SP1) à node_d (SP2) tout en spécifiant subproject1 comme SP de la relation
    update_data = {
        "subproject_id": subproject1.id, # Le SP de la relation est SP1
        "source_node_id": node_a.id,      # Nœud A est dans SP1
        "target_node_id": node_d.id,      # Nœud D est dans SP2
        "link_type": "VISIBLE"
    }
    response = client.put(f"{RELATIONSHIPS_URL}/{relationship_id}", json=update_data)

    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "Source node and target node must belong to the same SubProject" in data['error']

# --- Tests pour la suppression d'une relation (DELETE /api/nodes/relationships/<id>) ---

def test_delete_relationship_success(client, db_session):
    """Teste la suppression réussie d'une relation existante."""
    project = Project(title="Projet Suppression Relation")
    subproject = SubProject(project_id=project.id, title="SP Suppression Relation", mermaid_definition="graph TD\nA --> B")
    db_session.add_all([project, subproject])
    db_session.commit()

    node_a = Node(subproject_id=subproject.id, mermaid_id="A", title="Nœud A", text_content="Contenu A")
    node_b = Node(subproject_id=subproject.id, mermaid_id="B", title="Nœud B", text_content="Contenu B")
    db_session.add_all([node_a, node_b])
    db_session.commit()

    relationship = Relationship(subproject_id=subproject.id, source_node_id=node_a.id, target_node_id=node_b.id, link_type=LinkType.VISIBLE)
    db_session.add(relationship)
    db_session.commit()
    relationship_id = relationship.id

    response = client.delete(f"{RELATIONSHIPS_URL}/{relationship_id}")

    assert response.status_code == 204 # No Content

    # Vérifier que la relation a bien été supprimée
    deleted_relationship = db_session.get(Relationship, relationship_id)
    assert deleted_relationship is None

def test_delete_relationship_not_found(client, db_session):
    """Teste la suppression d'une relation avec un ID inexistant."""
    non_existent_id = 9999
    response = client.delete(f"{RELATIONSHIPS_URL}/{non_existent_id}")

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert str(non_existent_id) in data['error']

# Note: Les tests pour la suppression en cascade (suppression d'un sous-projet supprime ses relations)
# devraient être ajoutés dans test_subprojects.py pour une couverture complète.