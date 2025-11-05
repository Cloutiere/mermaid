# backend/app/routes/subprojects.py
from flask import Blueprint, jsonify, request
from http import HTTPStatus

from app.services.subprojects import (
    get_all_subprojects,
    get_subproject_by_id,
    create_subproject,
    update_subproject,
    delete_subproject
)
from app.schemas import SubProjectCreate, SubProjectRead

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
    """Endpoint pour mettre à jour un sous-projet existant."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    
    data = request.get_json()
    try:
        subproject_update_schema = SubProjectCreate.model_validate(data)
    except Exception as e:
        return jsonify({"error": "Validation Error", "details": str(e)}), HTTPStatus.BAD_REQUEST
    
    updated_subproject = update_subproject(subproject_id, subproject_update_schema)
    updated_subproject_read_schema = SubProjectRead.model_validate(updated_subproject).model_dump()
    
    return jsonify(updated_subproject_read_schema), HTTPStatus.OK


@subprojects_bp.route('/<int:subproject_id>', methods=['DELETE'])
def delete_subproject_route(subproject_id: int):
    """Endpoint pour supprimer un sous-projet par ID."""
    delete_subproject(subproject_id)
    return '', HTTPStatus.NO_CONTENT