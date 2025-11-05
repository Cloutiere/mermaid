# backend/tests/test_mermaid.py
# Version 1.0

import pytest
import json
from app.models import Project, SubProject, Node, Relationship, ClassDef, LinkType
from app.services.mermaid_parser import parse_and_save_mermaid # For setting up data manually if needed
from app.services.mermaid_generator import generate_mermaid_from_subproject # For verifying generated output

# Base URL pour les endpoints Mermaid
MERMAID_IMPORT_URL = '/api/mermaid/import'
MERMAID_EXPORT_URL_TEMPLATE = '/api/mermaid/export/{}' # Placeholder pour le subproject_id

# --- Tests pour l'importation Mermaid (POST /api/mermaid/import) ---

def test_import_mermaid_success(client, db_session):
    """Teste l'importation réussie d'un code Mermaid simple."""
    mermaid_code = """
    graph TD
        A[Nœud A] --> B(Nœud B)
    """
    project_title = "Projet d'Importation Simple"

    response = client.post(MERMAID_IMPORT_URL, json={
        "code": mermaid_code,
        "project_title": project_title
    })

    assert response.status_code == 201
    data = json.loads(response.get_data(as_text=True))

    assert data['title'] == project_title
    assert len(data['subprojects']) == 1

    sp = data['subprojects'][0]
    assert sp['title'].startswith("Nouveau Graphe") # Titre par défaut
    assert sp['mermaid_definition'].strip() == mermaid_code.strip()

    # Vérifier la création des entités dans la DB via les services (on peut aussi vérifier directement)
    created_project = db_session.get(Project, data['id'])
    assert created_project is not None
    assert len(created_project.subprojects) == 1

    created_sp = created_project.subprojects[0]
    assert len(created_sp.nodes) == 2
    assert len(created_sp.relationships) == 1

    node_a = next((n for n in created_sp.nodes if n.mermaid_id == "A"), None)
    node_b = next((n for n in created_sp.nodes if n.mermaid_id == "B"), None)
    rel_ab = created_sp.relationships[0]

    assert node_a is not None and node_b is not None
    assert rel_ab.source_node_id == node_a.id
    assert rel_ab.target_node_id == node_b.id
    assert rel_ab.link_type == LinkType.VISIBLE

def test_import_mermaid_success_with_classdef_and_relations(client, db_session):
    """Teste l'importation d'un code Mermaid plus complexe avec classDef et relations variées."""
    mermaid_code = """
    graph TD
        classDef important fill:#f9f,stroke:#333,stroke-width:2px

        Start(Début) --> Step1[Étape 1]
        class Start important
        Step1 -- Label 1 --> Step2{Étape 2}
        Step2 ---|Label 2| End(Fin)
    """
    project_title = "Projet d'Importation Complexe"

    response = client.post(MERMAID_IMPORT_URL, json={
        "code": mermaid_code,
        "project_title": project_title
    })

    assert response.status_code == 201
    data = json.loads(response.get_data(as_text=True))

    assert len(data['subprojects']) == 1
    sp_data = data['subprojects'][0]

    # Vérification directe des entités dans la DB
    created_project = db_session.get(Project, data['id'])
    created_sp = created_project.subprojects[0]

    assert len(created_sp.class_defs) == 1
    assert created_sp.class_defs[0].name == "important"
    assert created_sp.class_defs[0].definition_raw == "fill:#f9f,stroke:#333,stroke-width:2px"

    assert len(created_sp.nodes) == 4 # Start, Step1, Step2, End
    node_start = next((n for n in created_sp.nodes if n.mermaid_id == "Start"), None)
    node_step1 = next((n for n in created_sp.nodes if n.mermaid_id == "Step1"), None)
    node_step2 = next((n for n in created_sp.nodes if n.mermaid_id == "Step2"), None)
    node_end = next((n for n in created_sp.nodes if n.mermaid_id == "End"), None)

    assert node_start is not None and node_start.style_class_ref == "important"

    assert len(created_sp.relationships) == 3

    rel1 = next((r for r in created_sp.relationships if r.source_node_id == node_start.id and r.target_node_id == node_step1.id), None)
    assert rel1 is not None and rel1.label == "Label 1" and rel1.link_type == LinkType.VISIBLE

    rel2 = next((r for r in created_sp.relationships if r.source_node_id == node_step1.id and r.target_node_id == node_step2.id), None)
    assert rel2 is not None and rel2.label == "Label 1" and rel2.link_type == LinkType.VISIBLE # Mermaid supporte des labels sur les deux sides, ici on prend le premier

    rel3 = next((r for r in created_sp.relationships if r.source_node_id == node_step2.id and r.target_node_id == node_end.id), None)
    assert rel3 is not None and rel3.label == "Label 2" and rel3.link_type == LinkType.INVISIBLE

def test_import_mermaid_missing_code(client, db_session):
    """Teste l'importation sans le champ 'code'."""
    response = client.post(MERMAID_IMPORT_URL, json={"project_title": "Test"})
    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "code" in data['error']

def test_import_mermaid_empty_code(client, db_session):
    """Teste l'importation avec un code Mermaid vide."""
    response = client.post(MERMAID_IMPORT_URL, json={"code": "", "project_title": "Test"})
    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "Le code Mermaid doit commencer par 'graph TD'" in data['error'] # Attendu du parser

def test_import_mermaid_invalid_syntax(client, db_session):
    """Teste l'importation avec un code Mermaid syntaxiquement incorrect."""
    mermaid_code = """
    graph TD
        A[Nœud A] -- Pas une relation valide --> B
    """ # Syntaxe incorrecte pour la relation (manque la cible ou label mal formaté)
    response = client.post(MERMAID_IMPORT_URL, json={"code": mermaid_code, "project_title": "Test Invalide"})
    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    # Le message d'erreur peut varier, mais il doit indiquer un problème
    assert "Erreur d'intégrité" in data['error'] or "syntax" in data['error'].lower() # Le parser actuel peut lever une BadRequest ou une IntegrityError cachée.

def test_import_mermaid_invalid_start_line(client, db_session):
    """Teste l'importation avec une première ligne incorrecte."""
    mermaid_code = """
    flowchart TD
        A --> B
    """ # Devrait commencer par 'graph'
    response = client.post(MERMAID_IMPORT_URL, json={"code": mermaid_code, "project_title": "Test Invalide Start"})
    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert "Le code Mermaid doit commencer par 'graph TD'" in data['error']

# --- Tests pour l'exportation Mermaid (GET /api/mermaid/export/<subproject_id>) ---

def test_export_mermaid_success(client, db_session):
    """Teste l'exportation réussie d'un SubProject avec des données."""
    # Créer des données manuellement pour s'assurer de la source de vérité
    project = Project(title="Projet Export")
    subproject = SubProject(
        project_id=project.id,
        title="SP Exporté",
        mermaid_definition="graph TD\nStart --> Step1[Étape 1]\nStep1 --> End(Fin)\nclass Start important",
        visual_layout={}
    )
    db_session.add_all([project, subproject])
    db_session.commit()

    node_start = Node(subproject_id=subproject.id, mermaid_id="Start", title="Début", text_content="Début", style_class_ref="important")
    node_step1 = Node(subproject_id=subproject.id, mermaid_id="Step1", title="Étape 1", text_content="Étape 1")
    node_end = Node(subproject_id=subproject.id, mermaid_id="End", title="Fin", text_content="Fin")
    db_session.add_all([node_start, node_step1, node_end])
    db_session.commit()

    rel1 = Relationship(subproject_id=subproject.id, source_node_id=node_start.id, target_node_id=node_step1.id, link_type=LinkType.VISIBLE)
    rel2 = Relationship(subproject_id=subproject.id, source_node_id=node_step1.id, target_node_id=node_end.id, link_type=LinkType.VISIBLE)
    db_session.add_all([rel1, rel2])
    db_session.commit()

    # Exporter
    export_url = MERMAID_EXPORT_URL_TEMPLATE.format(subproject.id)
    response = client.get(export_url)

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/plain; charset=utf-8'

    generated_code = response.get_data(as_text=True)

    # Vérifier que le code généré correspond à ce qui est attendu (l'ordre peut varier légèrement)
    # Le générateur actuel met les classDefs en premier, puis les nœuds, puis les relations.
    assert "graph TD" in generated_code
    assert "classDef important" in generated_code # La définition de classe n'est pas dans le mermaid_definition initial, mais générée si on ajoute une ClassDef dans la DB.
    # Si on veut tester classDef, il faut l'ajouter explicitement dans la DB pour l'export.
    # Pour cet exemple, on se base sur le code initial.

    # Le code généré peut avoir des variations d'espacement ou d'ordre.
    # On peut faire des assertions plus faibles ou vérifier la présence des éléments clés.
    assert "Start(Début)" in generated_code
    assert "Step1[Étape 1]" in generated_code
    assert "End(Fin)" in generated_code
    assert "Start-->Step1" in generated_code
    assert "Step1-->End" in generated_code

    # Si on avait ajouté une ClassDef dans la DB :
    # classdef_obj = ClassDef(subproject_id=subproject.id, name="my_style", definition_raw="fill:red")
    # db_session.add(classdef_obj)
    # db_session.commit()
    # ... refaire le test ...
    # assert "classDef my_style fill:red" in generated_code

def test_export_mermaid_not_found(client, db_session):
    """Teste l'exportation d'un SubProject inexistant."""
    non_existent_id = 9999
    export_url = MERMAID_EXPORT_URL_TEMPLATE.format(non_existent_id)
    response = client.get(export_url)

    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert 'error' in data
    assert str(non_existent_id) in data['error']

def test_export_mermaid_empty_subproject(client, db_session):
    """Teste l'exportation d'un SubProject vide (sans nœuds, relations, etc.)."""
    project = Project(title="Projet Export Vide")
    subproject = SubProject(project_id=project.id, title="SP Vide", mermaid_definition="", visual_layout={})
    db_session.add_all([project, subproject])
    db_session.commit()

    export_url = MERMAID_EXPORT_URL_TEMPLATE.format(subproject.id)
    response = client.get(export_url)

    assert response.status_code == 200
    generated_code = response.get_data(as_text=True)

    # Un SP vide devrait générer au minimum la déclaration graph TD
    assert generated_code.strip() == "graph TD"