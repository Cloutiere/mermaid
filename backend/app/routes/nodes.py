# backend/app/routes/nodes.py
# Version 1.0

from flask import Blueprint, jsonify, request
from http import HTTPStatus

# Import service functions for Node and Relationship
from app.services.nodes import (
    get_all_nodes, get_node_by_id, create_node, update_node, delete_node,
    get_all_relationships, get_relationship_by_id, create_relationship, update_relationship, delete_relationship
)

# Import Pydantic schemas for validation and serialization
from app.schemas import NodeCreate, NodeRead, RelationshipCreate, RelationshipRead

# Création du Blueprint pour les routes liées aux Nœuds et Relations
nodes_bp = Blueprint('nodes', __name__)

# --- Routes pour les Nœuds ---

@nodes_bp.route('/', methods=['GET'])
def list_nodes():
    """Endpoint pour lister tous les nœuds, optionnellement filtrés par subproject_id."""
    subproject_id = request.args.get('subproject_id', type=int)
    nodes = get_all_nodes(subproject_id=subproject_id)
    # Sérialisation des nœuds en utilisant le schéma NodeRead
    node_schemas = [NodeRead.model_validate(node).model_dump() for node in nodes]
    return jsonify(node_schemas), HTTPStatus.OK

@nodes_bp.route('/', methods=['POST'])
def add_node():
    """Endpoint pour créer un nouveau nœud."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    data = request.get_json()
    try:
        # Valider les données entrantes avec le schéma NodeCreate
        node_create_schema = NodeCreate.model_validate(data)
    except Exception as e:
        return jsonify({"error": "Validation Error", "details": str(e)}), HTTPStatus.BAD_REQUEST

    # Créer le nœud via la couche de service
    new_node = create_node(node_create_schema)

    # Sérialiser le nouveau nœud pour la réponse
    new_node_read_schema = NodeRead.model_validate(new_node).model_dump()

    # Retourner le nœud créé avec le statut 201 CREATED
    return jsonify(new_node_read_schema), HTTPStatus.CREATED

@nodes_bp.route('/<int:node_id>', methods=['GET'])
def get_node(node_id: int):
    """Endpoint pour récupérer un nœud spécifique par ID."""
    # get_node_by_id lèvera NotFound si l'ID n'est pas trouvé
    node = get_node_by_id(node_id)

    # Sérialiser le nœud pour la réponse
    node_read_schema = NodeRead.model_validate(node).model_dump()
    return jsonify(node_read_schema), HTTPStatus.OK

@nodes_bp.route('/<int:node_id>', methods=['PUT'])
def update_node_route(node_id: int):
    """Endpoint pour mettre à jour un nœud existant."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    data = request.get_json()
    try:
        # Valider les données entrantes avec le schéma NodeCreate (utilisé aussi pour la mise à jour)
        node_update_schema = NodeCreate.model_validate(data)
    except Exception as e:
        return jsonify({"error": "Validation Error", "details": str(e)}), HTTPStatus.BAD_REQUEST

    # Mettre à jour le nœud via la couche de service
    updated_node = update_node(node_id, node_update_schema)

    # Sérialiser le nœud mis à jour pour la réponse
    updated_node_read_schema = NodeRead.model_validate(updated_node).model_dump()

    return jsonify(updated_node_read_schema), HTTPStatus.OK

@nodes_bp.route('/<int:node_id>', methods=['DELETE'])
def delete_node_route(node_id: int):
    """Endpoint pour supprimer un nœud par ID."""
    # delete_node lèvera NotFound si l'ID n'est pas trouvé
    delete_node(node_id)

    # Retourner 204 No Content pour une suppression réussie
    return '', HTTPStatus.NO_CONTENT

# --- Routes pour les Relations (imbriquées sous /api/nodes/relationships) ---

@nodes_bp.route('/relationships/', methods=['GET'])
def list_relationships():
    """Endpoint pour lister toutes les relations, optionnellement filtrées par subproject_id."""
    subproject_id = request.args.get('subproject_id', type=int)
    relationships = get_all_relationships(subproject_id=subproject_id)
    # Sérialisation des relations en utilisant le schéma RelationshipRead
    relationship_schemas = [RelationshipRead.model_validate(rel).model_dump() for rel in relationships]
    return jsonify(relationship_schemas), HTTPStatus.OK

@nodes_bp.route('/relationships/', methods=['POST'])
def add_relationship():
    """Endpoint pour créer une nouvelle relation."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    data = request.get_json()
    try:
        # Valider les données entrantes avec le schéma RelationshipCreate
        relationship_create_schema = RelationshipCreate.model_validate(data)
    except Exception as e:
        return jsonify({"error": "Validation Error", "details": str(e)}), HTTPStatus.BAD_REQUEST

    # Créer la relation via la couche de service
    new_relationship = create_relationship(relationship_create_schema)

    # Sérialiser la nouvelle relation pour la réponse
    new_relationship_read_schema = RelationshipRead.model_validate(new_relationship).model_dump()

    return jsonify(new_relationship_read_schema), HTTPStatus.CREATED

@nodes_bp.route('/relationships/<int:relationship_id>', methods=['GET'])
def get_relationship(relationship_id: int):
    """Endpoint pour récupérer une relation spécifique par ID."""
    # get_relationship_by_id lèvera NotFound si l'ID n'est pas trouvé
    relationship = get_relationship_by_id(relationship_id)

    # Sérialiser la relation pour la réponse
    relationship_read_schema = RelationshipRead.model_validate(relationship).model_dump()
    return jsonify(relationship_read_schema), HTTPStatus.OK

@nodes_bp.route('/relationships/<int:relationship_id>', methods=['PUT'])
def update_relationship_route(relationship_id: int):
    """Endpoint pour mettre à jour une relation existante."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    data = request.get_json()
    try:
        # Valider les données entrantes avec le schéma RelationshipCreate
        relationship_update_schema = RelationshipCreate.model_validate(data)
    except Exception as e:
        return jsonify({"error": "Validation Error", "details": str(e)}), HTTPStatus.BAD_REQUEST

    # Mettre à jour la relation via la couche de service
    updated_relationship = update_relationship(relationship_id, relationship_update_schema)

    # Sérialiser la relation mise à jour pour la réponse
    updated_relationship_read_schema = RelationshipRead.model_validate(updated_relationship).model_dump()

    return jsonify(updated_relationship_read_schema), HTTPStatus.OK

@nodes_bp.route('/relationships/<int:relationship_id>', methods=['DELETE'])
def delete_relationship_route(relationship_id: int):
    """Endpoint pour supprimer une relation par ID."""
    # delete_relationship lèvera NotFound si l'ID n'est pas trouvé
    delete_relationship(relationship_id)

    # Retourner 204 No Content pour une suppression réussie
    return '', HTTPStatus.NO_CONTENT