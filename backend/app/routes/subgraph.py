# backend/app/routes/subgraphs.py
# Version 1.0

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from werkzeug.exceptions import BadRequest

from app.services.subgraph import (
    create_subgraph,
    get_subgraph_by_id,
    update_subgraph,
    delete_subgraph,
    assign_nodes_to_subgraph,
    unassign_nodes_from_subgraph,
)
from app.schemas import (
    SubgraphRead,
    SubgraphCreatePayload,
    SubgraphUpdatePayload,
    NodeAssignmentPayload,
)

subgraphs_bp = Blueprint('subgraphs', __name__)

@subgraphs_bp.route('/', methods=['POST'])
def create_subgraph():
    """Crée un nouveau subgraph et assigne des nœuds."""
    try:
        data = SubgraphCreatePayload.model_validate(request.json)
    except ValidationError as e:
        raise BadRequest(str(e))

    new_subgraph = subgraph_service.create_subgraph(data)
    response_data = SubgraphRead.model_validate(new_subgraph).model_dump()
    return jsonify(response_data), 201

@subgraphs_bp.route('/<int:subgraph_id>', methods=['GET'])
def get_subgraph(subgraph_id: int):
    """Récupère un subgraph par son ID."""
    subgraph = subgraph_service.get_subgraph_by_id(subgraph_id)
    response_data = SubgraphRead.model_validate(subgraph).model_dump()
    return jsonify(response_data), 200

@subgraphs_bp.route('/<int:subgraph_id>', methods=['PUT'])
def update_subgraph(subgraph_id: int):
    """Met à jour le titre et/ou le style d'un subgraph."""
    try:
        data = SubgraphUpdatePayload.model_validate(request.json)
    except ValidationError as e:
        raise BadRequest(str(e))

    updated_subgraph = subgraph_service.update_subgraph(subgraph_id, data)
    response_data = SubgraphRead.model_validate(updated_subgraph).model_dump()
    return jsonify(response_data), 200

@subgraphs_bp.route('/<int:subgraph_id>', methods=['DELETE'])
def delete_subgraph(subgraph_id: int):
    """Supprime un subgraph et désassigne ses nœuds."""
    subgraph_service.delete_subgraph(subgraph_id)
    return '', 204

@subgraphs_bp.route('/<int:subgraph_id>/assign_nodes', methods=['PATCH'])
def assign_nodes(subgraph_id: int):
    """Assigne ou remplace les nœuds d'un subgraph."""
    try:
        data = NodeAssignmentPayload.model_validate(request.json)
    except ValidationError as e:
        raise BadRequest(str(e))

    updated_subgraph = subgraph_service.assign_nodes_to_subgraph(subgraph_id, data.node_ids)
    response_data = SubgraphRead.model_validate(updated_subgraph).model_dump()
    return jsonify(response_data), 200

@subgraphs_bp.route('/<int:subgraph_id>/unassign_nodes', methods=['PATCH'])
def unassign_nodes(subgraph_id: int):
    """Retire des nœuds d'un subgraph."""
    try:
        data = NodeAssignmentPayload.model_validate(request.json)
    except ValidationError as e:
        raise BadRequest(str(e))

    updated_subgraph = subgraph_service.unassign_nodes_from_subgraph(subgraph_id, data.node_ids)
    response_data = SubgraphRead.model_validate(updated_subgraph).model_dump()
    return jsonify(response_data), 200