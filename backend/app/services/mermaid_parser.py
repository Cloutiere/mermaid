# backend/app/services/mermaid_parser.py
# Version 2.0

import re
from typing import Dict, List, Tuple
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, NotFound

from app import db
from app.models import Project, SubProject, Node, Relationship, ClassDef, LinkType

# --- Exceptions et Helpers ---

class MermaidParsingError(BadRequest):
    """Erreur spécifique de syntaxe Mermaid."""
    pass

# Note: Ces patterns sont simplifiés et se concentrent sur les structures de base des diagrammes de flux.
GRAPH_TYPE_PATTERN = re.compile(r'^\s*(graph\s+\w+)\s*', re.IGNORECASE)
CLASSDEF_PATTERN = re.compile(r'^\s*classDef\s+(\w+)\s+(.+?)\s*$', re.IGNORECASE)
NODE_DEFINITION_PATTERN = re.compile(r'^\s*(\w+)\s*\[(.+?)\]\s*$', re.IGNORECASE)
NODE_CLASS_PATTERN = re.compile(r'^\s*class\s+(\w+)\s+(\w+)\s*$', re.IGNORECASE)
# Relation : Source --> Target : Label | Source --- Target : Label
RELATIONSHIP_PATTERN = re.compile(r'^\s*(\w+)\s*([->|-]+)\s*(?:\|(.*?)\|)?\s*(\w+)\s*$', re.IGNORECASE)


def _get_link_type(connector: str) -> LinkType:
    """Détermine le LinkType basé sur le connecteur Mermaid (ex: '-->', '---')."""
    if '---' in connector:
        return LinkType.INVISIBLE
    # Par défaut, y compris si '-->' est utilisé
    return LinkType.VISIBLE

def _ensure_project(title: str) -> Project:
    """Récupère un projet existant ou en crée un nouveau."""
    project = db.session.execute(
        db.select(Project).filter_by(title=title)
    ).scalar_one_or_none()

    if project is None:
        project = Project(title=title)
        db.session.add(project)
        db.session.flush() # Assure que l'ID est généré
    return project

def _find_or_create_subproject(project: Project, mermaid_code: str) -> SubProject:
    """Crée un nouveau SubProject ou le met à jour s'il existe par son code."""
    subproject = SubProject(
        project_id=project.id,
        # Utiliser un titre temporaire, l'utilisateur devra le changer
        title=f"Nouveau Graphe ({len(project.subprojects) + 1})",
        mermaid_definition=mermaid_code,
        visual_layout={}
    )
    db.session.add(subproject)
    db.session.flush()

    return subproject

def _parse_mermaid_elements(mermaid_code: str) -> Tuple[Dict, Dict, List]:
    """
    Analyse le code Mermaid pour extraire les nœuds, relations et définitions de classe.
    Retourne les listes des éléments extraits.
    """
    lines = mermaid_code.strip().split('\n')

    if not lines or not GRAPH_TYPE_PATTERN.match(lines[0]):
        raise MermaidParsingError(f"Le code Mermaid doit commencer par 'graph TD', 'graph LR', etc. Ligne 1: {lines[0] if lines else 'Vide'}")

    nodes_data: Dict[str, Dict] = {}  # {mermaid_id: {title, text_content, style_class_ref}}
    relationships_data = [] # List[{source, target, label, link_type}]
    classdefs_data = {} # {name: definition_raw}

    # Parsing ligne par ligne
    for line in lines[1:]: # Ignorer la première ligne (graph type)
        line = line.strip()
        if not line:
            continue

        # A. ClassDefs (Ex: classDef blue fill:#f9f,stroke:#333)
        match = CLASSDEF_PATTERN.match(line)
        if match:
            name, definition = match.groups()
            classdefs_data[name.strip()] = definition.strip()
            continue

        # B. Nodes definition (Ex: A[Title])
        match = NODE_DEFINITION_PATTERN.match(line)
        if match:
            mermaid_id, title_raw = match.groups()
            mermaid_id = mermaid_id.strip()
            title = title_raw.strip().strip('"')

            # Initialise le noeud si non vu, ou met à jour le titre
            if mermaid_id not in nodes_data:
                nodes_data[mermaid_id] = {'title': title, 'text_content': title, 'style_class_ref': None}
            else:
                nodes_data[mermaid_id]['title'] = title
                nodes_data[mermaid_id]['text_content'] = title
            continue

        # C. Nodes class (Ex: class A blue_box) - Application de classe aux noeuds
        match = NODE_CLASS_PATTERN.match(line)
        if match:
            mermaid_id, class_ref = match.groups()
            mermaid_id = mermaid_id.strip()
            class_ref = class_ref.strip()

            # S'assurer que le nœud existe (peut être implicitement créé par une relation)
            if mermaid_id not in nodes_data:
                nodes_data[mermaid_id] = {'title': None, 'text_content': mermaid_id, 'style_class_ref': class_ref}
            else:
                nodes_data[mermaid_id]['style_class_ref'] = class_ref
            continue

        # D. Relationships (Ex: A-->B ou A--|Label|B)
        match = RELATIONSHIP_PATTERN.match(line)
        if match:
            source, connector, label_raw, target = match.groups()

            label = label_raw.strip() if label_raw else None

            link_type = _get_link_type(connector)

            relationships_data.append({
                'source': source.strip(),
                'target': target.strip(),
                'label': label,
                'link_type': link_type
            })

            # S'assurer que les noeuds impliqués existent minimalement (si non définis par A[Title])
            for node_id in [source.strip(), target.strip()]:
                if node_id not in nodes_data:
                    nodes_data[node_id] = {'title': None, 'text_content': node_id, 'style_class_ref': None}

    return classdefs_data, nodes_data, relationships_data


def synchronize_subproject_entities(subproject: SubProject, mermaid_code: str) -> None:
    """
    Supprime toutes les entités structurelles (nœuds, relations, classdefs) d'un
    SubProject, puis parse le nouveau code Mermaid et insère les nouvelles entités.
    Cette fonction opère dans la transaction de l'appelant (pas de commit/rollback).
    """
    subproject_id = subproject.id

    # 1. Parsing du nouveau code Mermaid
    classdefs_data, nodes_data_raw, relationships_data_raw = _parse_mermaid_elements(mermaid_code)

    # 2. Suppression des anciennes entités (dans un ordre qui respecte les FK)
    # Utilise des requêtes de suppression en masse pour la performance.
    db.session.query(Relationship).filter_by(subproject_id=subproject_id).delete(synchronize_session='fetch')
    db.session.query(Node).filter_by(subproject_id=subproject_id).delete(synchronize_session='fetch')
    db.session.query(ClassDef).filter_by(subproject_id=subproject_id).delete(synchronize_session='fetch')

    # On peut `flush` pour s'assurer que les suppressions sont prises en compte avant les insertions,
    # bien que ce ne soit pas strictement nécessaire dans ce flux.
    db.session.flush()

    # Dictionnaire de mapping pour convertir les mermaid_id en id de DB
    node_id_map: Dict[str, int] = {}

    # 3. Ré-insertion des ClassDefs
    for name, definition_raw in classdefs_data.items():
        class_def = ClassDef(
            subproject_id=subproject_id,
            name=name,
            definition_raw=definition_raw
        )
        db.session.add(class_def)

    # 4. Ré-insertion des Nœuds
    for mermaid_id, data in nodes_data_raw.items():
        node = Node(
            subproject_id=subproject_id,
            mermaid_id=mermaid_id,
            title=data['title'],
            text_content=data['text_content'] or mermaid_id, 
            style_class_ref=data['style_class_ref']
        )
        db.session.add(node)
        db.session.flush()
        node_id_map[mermaid_id] = node.id

    # 5. Ré-insertion des Relations
    for rel_data in relationships_data_raw:
        source_id_mermaid = rel_data['source']
        target_id_mermaid = rel_data['target']

        source_node_db_id = node_id_map.get(source_id_mermaid)
        target_node_db_id = node_id_map.get(target_id_mermaid)

        if source_node_db_id is None or target_node_db_id is None:
            raise NotFound(f"Erreur interne de synchronisation: Nœud source ({source_id_mermaid}) ou cible ({target_id_mermaid}) manquant après l'insertion.")

        relationship = Relationship(
            subproject_id=subproject_id,
            source_node_id=source_node_db_id,
            target_node_id=target_node_db_id,
            label=rel_data['label'],
            link_type=rel_data['link_type'],
            color=None
        )
        db.session.add(relationship)


def parse_and_save_mermaid(mermaid_code: str, project_title: str = "Graphe Importé") -> Project:
    """
    Analyse le code Mermaid, crée un nouveau Project/SubProject et peuple les entités
    structurelles dans la base de données de manière transactionnelle.
    """
    db.session.begin()
    try:
        # 1. Assurer l'existence du Project
        project = _ensure_project(project_title)

        # 2. Créer le SubProject
        subproject = _find_or_create_subproject(project, mermaid_code)

        # 3. Synchroniser les entités structurelles
        synchronize_subproject_entities(subproject, mermaid_code)

        # 4. Commit la transaction
        db.session.commit()

    except (IntegrityError, MermaidParsingError, NotFound, BadRequest) as e:
        db.session.rollback()
        if isinstance(e, MermaidParsingError):
             raise BadRequest(description=str(e))
        elif isinstance(e, IntegrityError):
             raise BadRequest("Erreur d'intégrité de la base de données lors de l'insertion (unicité/clé étrangère).")
        else:
             raise e
    except Exception as e:
        db.session.rollback()
        raise e

    # Charger le Project avec ses SubProjects pour la réponse API (optimisé)
    project_read = db.session.execute(
        db.select(Project)
        .options(selectinload(Project.subprojects)) # type: ignore[arg-type]
        .where(Project.id == project.id)
    ).scalar_one()

    return project_read