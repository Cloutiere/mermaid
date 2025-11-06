# backend/app/routes/classdefs.py
# Version 1.0
"""
API routes for managing ClassDef entities.
This blueprint handles the RESTful endpoints for creating, reading,
updating, and deleting style definitions for Mermaid graphs.
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from werkzeug.exceptions import BadRequest

from app.schemas import ClassDefCreate, ClassDefRead
from app.services import classdefs as classdef_service

classdefs_bp = Blueprint('classdefs_bp', __name__)


@classdefs_bp.route('/', methods=['GET'])
def get_classdefs():
    """
    Get a list of all ClassDefs, optionally filtered by subproject_id.
    """
    subproject_id_str = request.args.get('subproject_id')
    subproject_id = None
    if subproject_id_str:
        try:
            subproject_id = int(subproject_id_str)
        except ValueError:
            raise BadRequest("Query parameter 'subproject_id' must be an integer.")

    classdefs = classdef_service.get_all_classdefs(subproject_id)
    return jsonify([ClassDefRead.model_validate(cd).model_dump() for cd in classdefs])


@classdefs_bp.route('/<int:classdef_id>', methods=['GET'])
def get_classdef(classdef_id: int):
    """
    Get a single ClassDef by its ID.
    """
    classdef = classdef_service.get_classdef_by_id(classdef_id)
    return jsonify(ClassDefRead.model_validate(classdef).model_dump())


@classdefs_bp.route('/', methods=['POST'])
def create_classdef():
    """
    Create a new ClassDef.
    """
    json_data = request.get_json()
    if not json_data:
        raise BadRequest("Invalid JSON body.")
    try:
        classdef_data = ClassDefCreate(**json_data)
    except ValidationError as e:
        raise BadRequest(f"Validation error: {e.errors()}")

    new_classdef = classdef_service.create_classdef(classdef_data)
    return jsonify(ClassDefRead.model_validate(new_classdef).model_dump()), 201


@classdefs_bp.route('/<int:classdef_id>', methods=['PUT'])
def update_classdef(classdef_id: int):
    """
    Update an existing ClassDef.
    """
    json_data = request.get_json()
    if not json_data:
        raise BadRequest("Invalid JSON body.")
    try:
        # We reuse ClassDefCreate as the payload is identical for create and update
        classdef_data = ClassDefCreate(**json_data)
    except ValidationError as e:
        raise BadRequest(f"Validation error: {e.errors()}")

    updated_classdef = classdef_service.update_classdef(classdef_id, classdef_data)
    return jsonify(ClassDefRead.model_validate(updated_classdef).model_dump())


@classdefs_bp.route('/<int:classdef_id>', methods=['DELETE'])
def delete_classdef(classdef_id: int):
    """
    Delete a ClassDef.
    """
    classdef_service.delete_classdef(classdef_id)
    return '', 204