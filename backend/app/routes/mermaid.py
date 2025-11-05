# backend/app/routes/mermaid.py
# Version 1.0

from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest, NotFound

from app.services.mermaid_parser import parse_and_save_mermaid
from app.services.mermaid_generator import generate_mermaid_from_subproject
from app.models import Project, SubProject # Import models for type hinting and potential serialization

# Création du Blueprint pour les routes liées à Mermaid
mermaid_bp = Blueprint('mermaid_bp', __name__)

@mermaid_bp.route('/import', methods=['POST'])
def import_mermaid():
    """
    Endpoint pour importer un code Mermaid et le sauvegarder dans la base de données.
    Expects a JSON payload with 'code' (Mermaid string) and optionally 'project_title'.
    """
    data = request.get_json()

    if not data or 'code' not in data:
        raise BadRequest("Requête invalide : le corps JSON doit contenir une clé 'code' avec le code Mermaid.")

    mermaid_code = data['code']
    project_title = data.get('project_title', "Graphe Importé") # Titre par défaut

    try:
        # Appel au service de parsing
        project = parse_and_save_mermaid(mermaid_code, project_title)

        # Sérialisation de l'objet Project pour la réponse API
        # On utilise une approche simple ici, une sérialisation Pydantic serait plus robuste
        project_data = {
            "id": project.id,
            "title": project.title,
            "subprojects": []
        }
        for sp in project.subprojects:
            project_data["subprojects"].append({
                "id": sp.id,
                "title": sp.title,
                "mermaid_definition": sp.mermaid_definition # Peut être utile pour confirmation
            })

        return jsonify(project_data), 201 # 201 CREATED est approprié pour une importation réussie

    except BadRequest as e:
        # Les erreurs spécifiques (parsing, validation) sont déjà des BadRequest
        raise e
    except Exception as e:
        # Gestion des erreurs serveur imprévues
        raise BadRequest(description=f"Erreur lors de l'importation du code Mermaid : {str(e)}")


@mermaid_bp.route('/export/<int:subproject_id>', methods=['GET'])
def export_mermaid(subproject_id: int):
    """
    Endpoint pour exporter un SubProject sous forme de code Mermaid.
    """
    try:
        # Appel au service de génération
        mermaid_code = generate_mermaid_from_subproject(subproject_id)

        # Retourne le code Mermaid en texte brut
        return mermaid_code, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    except NotFound as e:
        # L'erreur NotFound est déjà gérée par le gestionnaire global de l'app
        raise e
    except Exception as e:
        # Gestion des erreurs serveur imprévues
        raise BadRequest(description=f"Erreur lors de l'exportation du code Mermaid pour le SubProject {subproject_id} : {str(e)}")