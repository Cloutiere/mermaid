# backend/app/services/mermaid_parser.py
# Version 2.2

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
GRAPH_TYPE_PATTERN = re.compile(r'^\s*graph\s+(\w+)\s*', re.IGNORECASE)
CLASSDEF_PATTERN = re.compile(r'^\s*classDef\s+(\w+)\s+(.+?)\s*$', re.IGNORECASE)
# Handles both A["..."] and S{{"..."}} syntax
NODE_DEFINITION_PATTERN = re.compile(r'^\s*(\w+)\s*(?:\[(.*?)\]|\{\{(.*?)\}\})\s*$', re.IGNORECASE)
# Handles optional semicolon at the end: class A style;
NODE_CLASS_PATTERN = re.compile(r'^\s*class\s+(\w+)\s+(\w+)\s*;?\s*$', re.IGNORECASE)
# Relation : Source --> Target : Label | Source --- Target : Label
RELATIONSHIP_PATTERN = re.compile(r'^\s*(\w+)\s*--\s*(?:\|(.*?)\|)?\s*>\s*(\w+)\s*$|^\s*(\w+)\s*---\s*(?:\|(.*?)\|)?\s*(\w+)\s*$', re.IGNORECASE)


def _get_link_type(match_groups: tuple) -> Tuple[LinkType, str, str, str]:
    """Détermine le LinkType et extrait les composants de la relation à partir des groupes de la regex."""
    # Match pour "-->"
    if match_groups[0] is not None:
        source, label, target = match_groups[0:3]
        return LinkType.VISIBLE, source, label, target
    # Match pour "---"
    else:
        source, label, target = match_groups[3:6]
        return LinkType.INVISIBLE, source, label, target

def _ensure_project(title: str) -> Project:
    """Récupère un projet existant ou en crée un nouveau."""
    project = db.session.execute(
        db.select(Project).filter_by(title=title)
    ).scalar_one_or_none()

    if project is None:
        project = Project(title=title)  # type: ignore[call-arg]
        db.session.add(project)
        db.session.flush() # Assure que l'ID est généré
    return project

def _find_or_create_subproject(project: Project, mermaid_code: str) -> SubProject:
    """Crée un nouveau SubProject ou le met à jour s'il existe par son code."""
    subproject = SubProject(  # type: ignore[call-arg]
        project_id=project.id,
        # Utiliser un titre temporaire, l'utilisateur devra le changer
        title=f"Nouveau Graphe ({len(project.subprojects) + 1})",
        mermaid_definition=mermaid_code,
        visual_layout={}
    )
    db.session.add(subproject)
    db.session.flush()

    return subproject

def _parse_mermaid_elements(mermaid_code: str) -> Tuple[str, Dict, Dict, List]:
    """
    Analyse le code Mermaid pour extraire la direction, les nœuds, relations et définitions de classe.
    Retourne la direction du graphe et les listes des éléments extraits.
    """
    lines = mermaid_code.strip().split('\n')
    graph_direction = "TD"  # Valeur par défaut robuste

    if not lines:
        raise MermaidParsingError("Le code Mermaid ne peut être vide.")

    match = GRAPH_TYPE_PATTERN.match(lines[0])
    if not match:
        raise MermaidParsingError(f"Le code Mermaid doit commencer par 'graph TD', 'graph LR', etc. Ligne 1: {lines[0]}")

    graph_direction = match.group(1).upper()

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

        # B. Nodes definition (Ex: A[Title] or S{{"Title"}})
        match = NODE_DEFINITION_PATTERN.match(line)
        if match:
            mermaid_id, title_from_brackets, title_from_braces = match.groups()
            title_raw = title_from_brackets if title_from_brackets is not None else title_from_braces

            mermaid_id = mermaid_id.strip()
            # The content from {{...}} might have extra quotes, like '"..."'
            title = title_raw.strip().strip('"')

            # Initialise le noeud si non vu, ou met à jour le titre
            if mermaid_id not in nodes_data:
                nodes_data[mermaid_id] = {'title': title, 'text_content': title, 'style_class_ref': None}
            else:
                nodes_data[mermaid_id]['title'] = title
                nodes_data[mermaid_id]['text_content'] = title
            continue

        # C. Nodes class (Ex: class A blue_box;) - Application de classe aux noeuds
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

        # D. Relationships (Ex: A-->B ou A---|Label|---B)
        match = RELATIONSHIP_PATTERN.match(line)
        if match:
            link_type, source, label_raw, target = _get_link_type(match.groups())

            label = label_raw.strip() if label_raw else None

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
            continue

    return graph_direction, classdefs_data, nodes_data, relationships_data


def synchronize_subproject_entities(subproject: SubProject, mermaid_code: str) -> None:
    """
    Synchronise les entités structurelles d'un SubProject avec le code Mermaid parsé.
    Utilise une stratégie update-or-create pour préserver le contenu enrichi des nœuds.
    Cette fonction opère dans la transaction de l'appelant (pas de commit/rollback).
    """
    subproject_id = subproject.id

    # 1. Parsing du nouveau code Mermaid pour extraire toutes les données structurelles
    graph_direction, classdefs_data, nodes_data_raw, relationships_data_raw = _parse_mermaid_elements(mermaid_code)

    # 1.5. Mettre à jour la direction du graphe sur l'objet SubProject
    subproject.graph_direction = graph_direction

    # 2. Suppression des Relations (toujours recréées car pas de contenu utilisateur)
    db.session.query(Relationship).filter_by(subproject_id=subproject_id).delete(synchronize_session='fetch')
    
    # 3. Suppression des ClassDefs (toujours recréées car pas de contenu utilisateur)
    db.session.query(ClassDef).filter_by(subproject_id=subproject_id).delete(synchronize_session='fetch')
    db.session.flush()

    # 4. Récupération des nœuds existants pour update-or-create
    existing_nodes_query = db.select(Node).filter_by(subproject_id=subproject_id)
    existing_nodes = {node.mermaid_id: node for node in db.session.execute(existing_nodes_query).scalars().all()}

    # Dictionnaire de mapping pour convertir les mermaid_id en id de DB
    node_id_map: Dict[str, int] = {}

    # 5. Ré-insertion des ClassDefs
    for name, definition_raw in classdefs_data.items():
        class_def = ClassDef(subproject_id=subproject_id, name=name, definition_raw=definition_raw)  # type: ignore[call-arg]
        db.session.add(class_def)

    # 6. Update-or-Create des Nœuds (préserve le text_content enrichi)
    parsed_mermaid_ids = set(nodes_data_raw.keys())
    
    for mermaid_id, data in nodes_data_raw.items():
        if mermaid_id in existing_nodes:
            # Mise à jour du nœud existant
            node = existing_nodes[mermaid_id]
            
            # Mise à jour du titre si fourni
            if data['title'] is not None:
                node.title = data['title']
            
            # Préservation du text_content enrichi : ne met à jour que si c'est le titre par défaut
            # (indique que le contenu n'a pas été enrichi par l'utilisateur)
            if data['text_content'] and data['text_content'] != node.text_content:
                # Si le nouveau text_content est juste le mermaid_id ou le title, on garde l'ancien
                if data['text_content'] not in [mermaid_id, data['title']]:
                    node.text_content = data['text_content']
            
            # Mise à jour du style (toujours appliqué car vient du code Mermaid)
            node.style_class_ref = data['style_class_ref']
            
            node_id_map[mermaid_id] = node.id
        else:
            # Création d'un nouveau nœud
            node = Node(  # type: ignore[call-arg]
                subproject_id=subproject_id,
                mermaid_id=mermaid_id,
                title=data['title'],
                text_content=data['text_content'] or mermaid_id, 
                style_class_ref=data['style_class_ref']
            )
            db.session.add(node)
            db.session.flush()
            node_id_map[mermaid_id] = node.id

    # 7. Suppression des nœuds qui ne sont plus dans la définition Mermaid
    for mermaid_id, node in existing_nodes.items():
        if mermaid_id not in parsed_mermaid_ids:
            db.session.delete(node)
    
    db.session.flush()

    # 8. Ré-insertion des Relations
    for rel_data in relationships_data_raw:
        source_id_mermaid = rel_data['source']
        target_id_mermaid = rel_data['target']

        source_node_db_id = node_id_map.get(source_id_mermaid)
        target_node_db_id = node_id_map.get(target_id_mermaid)

        if source_node_db_id is None or target_node_db_id is None:
            raise NotFound(f"Erreur interne de synchronisation: Nœud source ({source_id_mermaid}) ou cible ({target_id_mermaid}) manquant après l'insertion.")

        relationship = Relationship(  # type: ignore[call-arg]
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