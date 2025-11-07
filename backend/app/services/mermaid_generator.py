# backend/app/services/mermaid_generator.py
# Version 1.2

from typing import List, Dict
from sqlalchemy.orm import selectinload
from werkzeug.exceptions import NotFound

from app import db
from app.models import SubProject, Node, Relationship, ClassDef, LinkType, Subgraph

# --- Constantes ---
RELATIONSHIP_LINK_MAP = {
    LinkType.VISIBLE: "-->",
    LinkType.INVISIBLE: "---",
}

def _sanitize_title(title: str, default_id: str) -> str:
    """Nettoie le titre pour l'affichage dans un nœud Mermaid (met entre guillemets si nécessaire)."""
    if not title:
        return default_id

    # Échapper les guillemets internes si le titre est long
    safe_title = title.replace('"', '#quot;')

    # Si le titre contient des espaces ou des caractères spéciaux, le mettre entre guillemets
    # Le titre d'un subgraph peut contenir des crochets, il faut les autoriser
    if ' ' in title:
        return f'"{safe_title}"'

    return safe_title


def generate_mermaid_from_subproject(subproject_id: int) -> str:
    """
    Génère le code Mermaid complet à partir des entités de la base de données
    pour un SubProject donné, en incluant les subgraphs.
    """

    # 1. Charger le SubProject avec toutes ses relations (eager loading)
    subproject = db.session.execute(
        db.select(SubProject)
        .options(
            selectinload(SubProject.nodes), # type: ignore[arg-type]
            selectinload(SubProject.relationships), # type: ignore[arg-type]
            selectinload(SubProject.class_defs), # type: ignore[arg-type]
            selectinload(SubProject.subgraphs).options(selectinload(Subgraph.nodes)) # type: ignore[arg-type]
        )
        .filter(SubProject.id == subproject_id)
    ).scalar_one_or_none()

    if subproject is None:
        raise NotFound(f"SubProject ID {subproject_id} non trouvé.")

    mermaid_parts: List[str] = []

    # --- 2. Déclaration du type de graphe ---
    mermaid_parts.append(f"graph {subproject.graph_direction}")
    mermaid_parts.append("")

    # --- 3. Ajout des Définitions de Classe (classDef) ---
    if subproject.class_defs:
        mermaid_parts.append("%% Class Definitions")
        for class_def in subproject.class_defs:
            mermaid_parts.append(f"classDef {class_def.name} {class_def.definition_raw}")
        mermaid_parts.append("")

    # --- 4. Définition des Nœuds et Subgraphs ---
    mermaid_parts.append("%% Nodes & Subgraphs Definitions")

    # Nœuds qui ne sont dans aucun subgraph
    nodes_without_subgraph = [node for node in subproject.nodes if node.subgraph_id is None]

    for node in nodes_without_subgraph:
        title = node.title if node.title is not None else node.text_content
        safe_title = _sanitize_title(title, node.mermaid_id)
        mermaid_parts.append(f"    {node.mermaid_id}[{safe_title}]")

    # Itérer sur les subgraphs
    if subproject.subgraphs:
        for subgraph in subproject.subgraphs:
            safe_subgraph_title = _sanitize_title(subgraph.title, subgraph.mermaid_id)
            mermaid_parts.append(f"subgraph {subgraph.mermaid_id}[{safe_subgraph_title}]")
            for node in subgraph.nodes:
                title = node.title if node.title is not None else node.text_content
                safe_title = _sanitize_title(title, node.mermaid_id)
                mermaid_parts.append(f"    {node.mermaid_id}[{safe_title}]")
            mermaid_parts.append("end")
            mermaid_parts.append("")

    mermaid_parts.append("")

    # --- 5. Application des Classes (sur nœuds et subgraphs) ---
    mermaid_parts.append("%% Class Applications")
    node_classes_applied = {
        node.mermaid_id: node.style_class_ref
        for node in subproject.nodes if node.style_class_ref
    }
    subgraph_classes_applied = {
        subgraph.mermaid_id: subgraph.style_class_ref
        for subgraph in subproject.subgraphs if subgraph.style_class_ref
    }

    if node_classes_applied:
        for mermaid_id, class_ref in node_classes_applied.items():
            mermaid_parts.append(f"class {mermaid_id} {class_ref}")
    if subgraph_classes_applied:
        for mermaid_id, class_ref in subgraph_classes_applied.items():
            mermaid_parts.append(f"class {mermaid_id} {class_ref}")
    mermaid_parts.append("")


    # --- 6. Définition des Relations (A-->B) ---
    mermaid_parts.append("%% Relationships")
    nodes_map: Dict[int, Node] = {node.id: node for node in subproject.nodes}
    for rel in subproject.relationships:
        source_node = nodes_map.get(rel.source_node_id)
        target_node = nodes_map.get(rel.target_node_id)

        if not source_node or not target_node:
            continue

        connector = RELATIONSHIP_LINK_MAP.get(rel.link_type, "---")

        label_part = ""
        if rel.label:
            safe_label = rel.label.replace('|', '/')
            label_part = f"|{safe_label}|"

        mermaid_parts.append(
            f"{source_node.mermaid_id}{connector}{label_part}{target_node.mermaid_id}"
        )

    # Reconstruit la chaîne complète
    return "\n".join(mermaid_parts)