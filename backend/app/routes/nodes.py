# backend/app/routes/nodes.py
from flask import Blueprint, jsonify, request
from http import HTTPStatus

from app.services.nodes import (
    get_all_nodes,
    get_node_by_id,
    create_node,
    update_node,
    delete_node,
    get_all_relationships,
    get_relationship_by_id,
    create_relationship,
    update_relationship,
    delete_relationship
)
from app.schemas import NodeCreate, NodeRead, RelationshipCreate, RelationshipRead

nodes_bp = Blueprint('nodes', __name__)


# --- Routes pour les Nodes ---

@nodes_bp.route('/', methods=['GET'])
def list_nodes():
    """Endpoint pour lister tous les nœuds, optionnellement filtrés par subproject_id."""
    subproject_id = request.args.get('subproject_id', type=int)
    nodes = get_all_nodes(subproject_id=subproject_id)
    node_schemas = [NodeRead.model_validate(n).model_dump() for n in nodes]
    return jsonify(node_schemas), HTTPStatus.OK


@nodes_bp.route('/', methods=['POST'])
def add_node():
    """Endpoint pour créer un nouveau nœud."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    
    data = request.get_json()
    try:
        node_create_schema = NodeCreate.model_validate(data)
    except Exception as e:
        return jsonify({"error": "Validation Error", "details": str(e)}), HTTPStatus.BAD_REQUEST
    
    new_node = create_node(node_create_schema)
    new_node_read_schema = NodeRead.model_validate(new_node).model_dump()
    
    return jsonify(new_node_read_schema), HTTPStatus.CREATED


@nodes_bp.route('/<int:node_id>', methods=['GET'])
def get_node(node_id: int):
    """Endpoint pour récupérer un nœud spécifique par ID."""
    node = get_node_by_id(node_id)
    node_read_schema = NodeRead.model_validate(node).model_dump()
    return jsonify(node_read_schema), HTTPStatus.OK


@nodes_bp.route('/<int:node_id>', methods=['PUT'])
def update_node_route(node_id: int):
    """Endpoint pour mettre à jour un nœud existant."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    
    data = request.get_json()
    try:
        node_update_schema = NodeCreate.model_validate(data)
    except Exception as e:
        return jsonify({"error": "Validation Error", "details": str(e)}), HTTPStatus.BAD_REQUEST
    
    updated_node = update_node(node_id, node_update_schema)
    updated_node_read_schema = NodeRead.model_validate(updated_node).model_dump()
    
    return jsonify(updated_node_read_schema), HTTPStatus.OK


@nodes_bp.route('/<int:node_id>', methods=['DELETE'])
def delete_node_route(node_id: int):
    """Endpoint pour supprimer un nœud par ID."""
    delete_node(node_id)
    return '', HTTPStatus.NO_CONTENT


# --- Routes pour les Relationships ---

@nodes_bp.route('/relationships', methods=['GET'])
def list_relationships():
    """Endpoint pour lister toutes les relations, optionnellement filtrées par subproject_id."""
    subproject_id = request.args.get('subproject_id', type=int)
    relationships = get_all_relationships(subproject_id=subproject_id)
    relationship_schemas = [RelationshipRead.model_validate(r).model_dump() for r in relationships]
    return jsonify(relationship_schemas), HTTPStatus.OK


@nodes_bp.route('/relationships', methods=['POST'])
def add_relationship():
    """Endpoint pour créer une nouvelle relation."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    
    data = request.get_json()
    try:
        relationship_create_schema = RelationshipCreate.model_validate(data)
    except Exception as e:
        return jsonify({"error": "Validation Error", "details": str(e)}), HTTPStatus.BAD_REQUEST
    
    new_relationship = create_relationship(relationship_create_schema)
    new_relationship_read_schema = RelationshipRead.model_validate(new_relationship).model_dump()
    
    return jsonify(new_relationship_read_schema), HTTPStatus.CREATED


@nodes_bp.route('/relationships/<int:relationship_id>', methods=['GET'])
def get_relationship(relationship_id: int):
    """Endpoint pour récupérer une relation spécifique par ID."""
    relationship = get_relationship_by_id(relationship_id)
    relationship_read_schema = RelationshipRead.model_validate(relationship).model_dump()
    return jsonify(relationship_read_schema), HTTPStatus.OK


@nodes_bp.route('/relationships/<int:relationship_id>', methods=['PUT'])
def update_relationship_route(relationship_id: int):
    """Endpoint pour mettre à jour une relation existante."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    
    data = request.get_json()
    try:
        relationship_update_schema = RelationshipCreate.model_validate(data)
    except Exception as e:
        return jsonify({"error": "Validation Error", "details": str(e)}), HTTPStatus.BAD_REQUEST
    
    updated_relationship = update_relationship(relationship_id, relationship_update_schema)
    updated_relationship_read_schema = RelationshipRead.model_validate(updated_relationship).model_dump()
    
    return jsonify(updated_relationship_read_schema), HTTPStatus.OK


@nodes_bp.route('/relationships/<int:relationship_id>', methods=['DELETE'])
def delete_relationship_route(relationship_id: int):
    """Endpoint pour supprimer une relation par ID."""
    delete_relationship(relationship_id)
    return '', HTTPStatus.NO_CONTENT