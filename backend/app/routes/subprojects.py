# backend/app/routes/subprojects.py
from flask import Blueprint, jsonify, request
from http import HTTPStatus

from app.services.subprojects import (
    get_all_subprojects,
    get_subproject_by_id,
    create_subproject,
    update_subproject_structure,
    update_subproject_metadata,
    delete_subproject
)

from app.schemas import SubProjectCreate, SubProjectRead, SubProjectMetadataUpdate

subprojects_bp = Blueprint('subprojects', __name__)

@subprojects_bp.route('/', methods=['GET'])
def list_subprojects():
    """Endpoint pour lister tous les sous-projets, optionnellement filtrés par project_id."""
    project_id = request.args.get('project_id', type=int)
    subprojects = get_all_subprojects(project_id=project_id)
    subproject_schemas = [SubProjectRead.model_validate(sp).model_dump() for sp in subprojects]
    return jsonify(subproject_schemas), HTTPStatus.OK

@subprojects_bp.route('/', methods=['POST'])
def add_subproject():
    """Endpoint pour créer un nouveau sous-projet."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    data = request.get_json()
    try:
        subproject_create_schema = SubProjectCreate.model_validate(data)
    except Exception as e:
        return jsonify({"error": "Validation Error", "details": str(e)}), HTTPStatus.BAD_REQUEST

    new_subproject = create_subproject(subproject_create_schema)
    new_subproject_read_schema = SubProjectRead.model_validate(new_subproject).model_dump()

    return jsonify(new_subproject_read_schema), HTTPStatus.CREATED

@subprojects_bp.route('/<int:subproject_id>', methods=['GET'])
def get_subproject(subproject_id: int):
    """Endpoint pour récupérer un sous-projet spécifique par ID."""
    subproject = get_subproject_by_id(subproject_id)
    subproject_read_schema = SubProjectRead.model_validate(subproject).model_dump()

    return jsonify(subproject_read_schema), HTTPStatus.OK

@subprojects_bp.route('/<int:subproject_id>', methods=['PUT'])
def update_subproject_route(subproject_id: int):
    """Endpoint pour mettre à jour un sous-projet. Détecte si la structure Mermaid a changé."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    data = request.get_json()
    try:
        schema = SubProjectCreate.model_validate(data)
    except Exception as e:
        return jsonify({"error": "Validation Error", "details": str(e)}), HTTPStatus.BAD_REQUEST

    # Charger l'existant pour comparer les définitions Mermaid
    existing = get_subproject_by_id(subproject_id)
    
    # Si la définition Mermaid a changé, reconstruire la structure
    if existing.mermaid_definition.strip() != schema.mermaid_definition.strip():
        updated = update_subproject_structure(subproject_id, schema)
    else:
        # Sinon, mettre à jour uniquement les métadonnées
        meta = SubProjectMetadataUpdate(title=schema.title, visual_layout=schema.visual_layout)
        updated = update_subproject_metadata(subproject_id, meta)

    return jsonify(SubProjectRead.model_validate(updated).model_dump()), HTTPStatus.OK


@subprojects_bp.route('/<int:subproject_id>/metadata', methods=['PATCH'])
def patch_subproject_metadata(subproject_id: int):
    """Endpoint pour mettre à jour uniquement les métadonnées (title + visual_layout)."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    data = request.get_json()
    try:
        schema = SubProjectMetadataUpdate.model_validate(data)
    except Exception as e:
        return jsonify({"error": "Validation Error", "details": str(e)}), HTTPStatus.BAD_REQUEST

    updated = update_subproject_metadata(subproject_id, schema)
    return jsonify(SubProjectRead.model_validate(updated).model_dump()), HTTPStatus.OK

@subprojects_bp.route('/<int:subproject_id>', methods=['DELETE'])
def delete_subproject_route(subproject_id: int):
    """Endpoint pour supprimer un sous-projet par ID."""
    delete_subproject(subproject_id)

    return '', HTTPStatus.NO_CONTENT
