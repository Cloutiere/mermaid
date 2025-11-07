# backend/app/services/mermaid_parser.py
# Version 2.3

import re
from typing import Dict, List, Tuple, Optional
from sqlalchemy import update
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, NotFound

from app import db
from app.models import Project, SubProject, Node, Relationship, ClassDef, Subgraph, LinkType

# --- Exceptions et Helpers ---

class MermaidParsingError(BadRequest):
    """Erreur spécifique de syntaxe Mermaid."""
    pass

# --- REGEX PATTERNS ---
GRAPH_TYPE_PATTERN = re.compile(r'^\s*graph\s+(\w+)\s*', re.IGNORECASE)
CLASSDEF_PATTERN = re.compile(r'^\s*classDef\s+(\w+)\s+(.+?)\s*$', re.IGNORECASE)
# Handles both A["..."] and S{{"..."}} syntax
NODE_DEFINITION_PATTERN = re.compile(r'^\s*(\w+)\s*(?:\[(.*?)\]|\{\{(.*?)\}\})\s*$', re.IGNORECASE)
# Handles optional semicolon at the end: class A style;
NODE_CLASS_PATTERN = re.compile(r'^\s*class\s+(\w+)\s+(\w+)\s*;?\s*$', re.IGNORECASE)
# Relation : Source --> Target : Label | Source --- Target : Label
RELATIONSHIP_PATTERN = re.compile(r'^\s*(\w+)\s*--\s*(?:\|(.*?)\|)?\s*>\s*(\w+)\s*$|^\s*(\w+)\s*---\s*(?:\|(.*?)\|)?\s*(\w+)\s*$', re.IGNORECASE)
# Subgraph: subgraph cluster_A[Title]
SUBGRAPH_START_PATTERN = re.compile(r'^\s*subgraph\s+(\w+)(?:\[(.*?)\])?\s*$', re.IGNORECASE)
SUBGRAPH_END_PATTERN = re.compile(r'^\s*end\s*$', re.IGNORECASE)


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

def _parse_mermaid_elements(mermaid_code: str) -> Tuple[str, Dict, Dict, List, Dict[str, List[str]]]:
    """
    Analyse le code Mermaid pour extraire la direction, les nœuds, relations, classdefs et groupements de subgraphs.
    Retourne la direction du graphe et les dictionnaires/listes des éléments extraits.
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
    subgraphs_grouping: Dict[str, List[str]] = {} # {subgraph_mermaid_id: [node_mermaid_id, ...]}
    current_subgraph_mermaid_id: Optional[str] = None

    # Parsing ligne par ligne
    for line in lines[1:]: # Ignorer la première ligne (graph type)
        line = line.strip()
        if not line:
            continue

        # 0. Subgraph start
        match = SUBGRAPH_START_PATTERN.match(line)
        if match:
            current_subgraph_mermaid_id, _ = match.groups()
            current_subgraph_mermaid_id = current_subgraph_mermaid_id.strip()
            subgraphs_grouping[current_subgraph_mermaid_id] = []
            continue

        # 0. Subgraph end
        match = SUBGRAPH_END_PATTERN.match(line)
        if match:
            current_subgraph_mermaid_id = None
            continue

        # A. ClassDefs
        match = CLASSDEF_PATTERN.match(line)
        if match:
            name, definition = match.groups()
            classdefs_data[name.strip()] = definition.strip()
            continue

        # B. Nodes definition
        match = NODE_DEFINITION_PATTERN.match(line)
        if match:
            mermaid_id, title_from_brackets, title_from_braces = match.groups()
            title_raw = title_from_brackets if title_from_brackets is not None else title_from_braces
            mermaid_id = mermaid_id.strip()
            title = title_raw.strip().strip('"') if title_raw else None

            if mermaid_id not in nodes_data:
                nodes_data[mermaid_id] = {'title': title, 'text_content': title, 'style_class_ref': None}
            else:
                nodes_data[mermaid_id]['title'] = title
                nodes_data[mermaid_id]['text_content'] = title

            if current_subgraph_mermaid_id:
                subgraphs_grouping[current_subgraph_mermaid_id].append(mermaid_id)
            continue

        # C. Nodes class
        match = NODE_CLASS_PATTERN.match(line)
        if match:
            mermaid_id, class_ref = match.groups()
            mermaid_id = mermaid_id.strip()
            class_ref = class_ref.strip()

            if mermaid_id not in nodes_data:
                nodes_data[mermaid_id] = {'title': None, 'text_content': mermaid_id, 'style_class_ref': class_ref}
            else:
                nodes_data[mermaid_id]['style_class_ref'] = class_ref
            continue

        # D. Relationships
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
            for node_id in [source.strip(), target.strip()]:
                if node_id not in nodes_data:
                    nodes_data[node_id] = {'title': None, 'text_content': node_id, 'style_class_ref': None}
            continue

    return graph_direction, classdefs_data, nodes_data, relationships_data, subgraphs_grouping


def synchronize_subproject_entities(subproject: SubProject, mermaid_code: str) -> None:
    """
    Synchronise les entités structurelles d'un SubProject avec le code Mermaid parsé.
    Cette fonction opère dans la transaction de l'appelant (pas de commit/rollback).
    """
    subproject_id = subproject.id

    # 1. Parsing
    graph_direction, classdefs_data, nodes_data_raw, relationships_data_raw, subgraphs_grouping = _parse_mermaid_elements(mermaid_code)
    subproject.graph_direction = graph_direction

    # 2. Suppression des entités non-éditables
    db.session.query(Relationship).filter_by(subproject_id=subproject_id).delete(synchronize_session='fetch')
    db.session.query(ClassDef).filter_by(subproject_id=subproject_id).delete(synchronize_session='fetch')
    db.session.flush()

    # 3. Récupération des entités existantes
    existing_nodes = {node.mermaid_id: node for node in db.session.scalars(db.select(Node).filter_by(subproject_id=subproject_id))}
    existing_subgraphs = {sg.mermaid_id: sg for sg in db.session.scalars(db.select(Subgraph).filter_by(subproject_id=subproject_id))}

    node_id_map: Dict[str, int] = {}

    # 4. Ré-insertion ClassDefs
    for name, definition_raw in classdefs_data.items():
        db.session.add(ClassDef(subproject_id=subproject_id, name=name, definition_raw=definition_raw))

    # 5. Update-or-Create Nœuds
    parsed_mermaid_ids = set(nodes_data_raw.keys())
    for mermaid_id, data in nodes_data_raw.items():
        node = existing_nodes.get(mermaid_id)
        if node:
            if data['title'] is not None: node.title = data['title']
            if data['text_content'] and data['text_content'] != node.text_content and data['text_content'] not in [mermaid_id, data['title']]:
                node.text_content = data['text_content']
            node.style_class_ref = data['style_class_ref']
            node_id_map[mermaid_id] = node.id
        else:
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

    # 6. Suppression des nœuds obsolètes
    for mermaid_id, node in existing_nodes.items():
        if mermaid_id not in parsed_mermaid_ids:
            db.session.delete(node)
    db.session.flush()

    # 7. Synchronisation des Subgraphs (affectation des nœuds)
    # 7.1. Désaffecter tous les nœuds du projet en premier
    db.session.execute(update(Node).where(Node.subproject_id == subproject_id).values(subgraph_id=None))

    # 7.2. Ré-affecter les nœuds aux subgraphs existants
    for subgraph_mermaid_id, node_mermaid_ids in subgraphs_grouping.items():
        if subgraph_mermaid_id in existing_subgraphs and node_mermaid_ids:
            subgraph_db_id = existing_subgraphs[subgraph_mermaid_id].id
            node_db_ids_to_assign = [node_id_map[nid] for nid in node_mermaid_ids if nid in node_id_map]

            if node_db_ids_to_assign:
                db.session.execute(
                    update(Node)
                    .where(Node.id.in_(node_db_ids_to_assign))
                    .values(subgraph_id=subgraph_db_id)
                )

    # 8. Ré-insertion des Relations
    for rel_data in relationships_data_raw:
        source_node_db_id = node_id_map.get(rel_data['source'])
        target_node_db_id = node_id_map.get(rel_data['target'])
        if source_node_db_id is None or target_node_db_id is None:
            raise NotFound(f"Erreur interne: Nœud source ({rel_data['source']}) ou cible ({rel_data['target']}) manquant.")
        db.session.add(Relationship(
            subproject_id=subproject_id,
            source_node_id=source_node_db_id,
            target_node_id=target_node_db_id,
            label=rel_data['label'],
            link_type=rel_data['link_type'],
            color=None
        ))

def parse_and_save_mermaid(mermaid_code: str, project_title: str = "Graphe Importé") -> Project:
    """
    Analyse le code Mermaid, crée un nouveau Project/SubProject et peuple les entités
    structurelles dans la base de données de manière transactionnelle.
    """
    db.session.begin()
    try:
        project = _ensure_project(project_title)
        subproject = _find_or_create_subproject(project, mermaid_code)
        synchronize_subproject_entities(subproject, mermaid_code)
        db.session.commit()
    except (IntegrityError, MermaidParsingError, NotFound, BadRequest) as e:
        db.session.rollback()
        if isinstance(e, MermaidParsingError): raise BadRequest(description=str(e))
        elif isinstance(e, IntegrityError): raise BadRequest("Erreur d'intégrité de la DB (unicité/clé étrangère).")
        else: raise e
    except Exception as e:
        db.session.rollback()
        raise e

    project_read = db.session.execute(
        db.select(Project)
        .options(selectinload(Project.subprojects)) # type: ignore[arg-type]
        .where(Project.id == project.id)
    ).scalar_one()

    return project_read