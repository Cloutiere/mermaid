# backend/app/services/mermaid_generator.py
# Version 1.1

from typing import List, Dict
from sqlalchemy.orm import selectinload
from werkzeug.exceptions import NotFound

from app import db
from app.models import SubProject, Node, Relationship, ClassDef, LinkType

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
    if ' ' in title or '[' in title or ']' in title or '{' in title or '}' in title:
        return f'"{safe_title}"'

    return safe_title


def generate_mermaid_from_subproject(subproject_id: int) -> str:
    """
    Génère le code Mermaid complet à partir des entités de la base de données
    pour un SubProject donné.
    """

    # 1. Charger le SubProject avec toutes ses relations (eager loading)
    subproject = db.session.execute(
        db.select(SubProject)
        .options(
            selectinload(SubProject.nodes), # type: ignore[arg-type]
            selectinload(SubProject.relationships), # type: ignore[arg-type]
            selectinload(SubProject.class_defs) # type: ignore[arg-type]
        )
        .filter(SubProject.id == subproject_id)
    ).scalar_one_or_none()

    if subproject is None:
        raise NotFound(f"SubProject ID {subproject_id} non trouvé.")

    # Utiliser le SubProject pour commencer la génération
    mermaid_parts: List[str] = []

    # --- 2. Déclaration du type de graphe ---
    # Utilise la direction stockée dans la base de données
    mermaid_parts.append(f"graph {subproject.graph_direction}")
    mermaid_parts.append("")

    # --- 3. Ajout des Définitions de Classe (classDef) ---
    if subproject.class_defs:
        mermaid_parts.append("%% Class Definitions")
        for class_def in subproject.class_defs:
            mermaid_parts.append(f"classDef {class_def.name} {class_def.definition_raw}")
        mermaid_parts.append("")

    # Indexation des nœuds pour référence rapide
    nodes_map: Dict[int, Node] = {node.id: node for node in subproject.nodes}

    # Dictionnaire des classes appliquées (pour éviter la redondance)
    node_classes_applied: Dict[str, str] = {} 

    # --- 4. Définition des Nœuds (A[Title]) ---
    mermaid_parts.append("%% Node Definitions")
    for node in subproject.nodes:
        # Le contenu du nœud Mermaid (le titre affiché) est pris en priorité
        # si `title` est null, on fallback sur `text_content` qui ne devrait pas l'être.
        title = node.title if node.title is not None else node.text_content
        safe_title = _sanitize_title(title, node.mermaid_id)

        # On utilise la syntaxe A[Title] pour définir le nœud
        mermaid_parts.append(f"{node.mermaid_id}[{safe_title}]")

        # Enregistrer les références de classe si elles existent
        if node.style_class_ref:
            node_classes_applied[node.mermaid_id] = node.style_class_ref

    mermaid_parts.append("")

    # --- 5. Application des Classes (class A class_ref) ---
    if node_classes_applied:
        mermaid_parts.append("%% Node Classes")
        for mermaid_id, class_ref in node_classes_applied.items():
            mermaid_parts.append(f"class {mermaid_id} {class_ref}")
        mermaid_parts.append("")

    # --- 6. Définition des Relations (A-->B) ---
    mermaid_parts.append("%% Relationships")
    for rel in subproject.relationships:
        source_node = nodes_map.get(rel.source_node_id)
        target_node = nodes_map.get(rel.target_node_id)

        if not source_node or not target_node:
            # Ceci ne devrait pas se produire si l'intégrité BD est respectée
            continue

        connector = RELATIONSHIP_LINK_MAP.get(rel.link_type, "---") # Par défaut invisible

        label_part = ""
        if rel.label:
            # Assainissement de l'étiquette (les étiquettes doivent être entre | |)
            safe_label = rel.label.replace('|', '/') 
            label_part = f"|{safe_label}|"

        mermaid_parts.append(
            f"{source_node.mermaid_id}{connector}{label_part}{target_node.mermaid_id}"
        )

    # Reconstruit la chaîne complète
    return "\n".join(mermaid_parts)