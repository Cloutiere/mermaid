# backend/app/routes/projects.py
from flask import Blueprint, jsonify, request
from http import HTTPStatus

# Import service functions
from app.services.projects import (
    get_all_projects,
    get_project_by_id,
    create_project,
    update_project,
    delete_project
)

# Import Pydantic schemas for validation and serialization
from app.schemas import ProjectCreate, ProjectRead
# Import Project model if needed for type hinting or direct manipulation (less common for route handlers)
# from app.models import Project


projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/', methods=['GET'])
def list_projects():
    """Endpoint to list all projects."""
    projects = get_all_projects()
    # Serialize each project using ProjectRead schema
    project_schemas = [ProjectRead.model_validate(p).model_dump() for p in projects]
    return jsonify(project_schemas), HTTPStatus.OK

@projects_bp.route('/', methods=['POST'])
def add_project():
    """Endpoint to create a new project."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    data = request.get_json()
    try:
        # Validate incoming data using Pydantic schema
        project_create_schema = ProjectCreate.model_validate(data)
    except Exception as e: # Catch Pydantic validation errors (e.g., ValidationError)
        # Pydantic validation errors can be complex, simplify for a basic message
        return jsonify({"error": "Validation Error", "details": str(e)}), HTTPStatus.BAD_REQUEST

    # Create the project using the service layer
    new_project = create_project(project_create_schema)

    # Serialize the newly created project for the response
    new_project_read_schema = ProjectRead.model_validate(new_project).model_dump()

    # Return the created project and 201 Created status
    return jsonify(new_project_read_schema), HTTPStatus.CREATED

@projects_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id: int):
    """Endpoint to get a specific project by ID."""
    # get_project_by_id will raise NotFound (which is handled by the global error handler)
    project = get_project_by_id(project_id)

    # Serialize the project for the response
    project_read_schema = ProjectRead.model_validate(project).model_dump()

    return jsonify(project_read_schema), HTTPStatus.OK

@projects_bp.route('/<int:project_id>', methods=['PUT'])
def update_project_route(project_id: int):
    """Endpoint to update an existing project."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    data = request.get_json()
    try:
        # Validate incoming data using Pydantic schema. ProjectCreate is suitable for PUT.
        project_update_schema = ProjectCreate.model_validate(data)
    except Exception as e:
        return jsonify({"error": "Validation Error", "details": str(e)}), HTTPStatus.BAD_REQUEST

    # Update the project using the service layer
    # update_project will raise NotFound if project_id is invalid
    updated_project = update_project(project_id, project_update_schema)

    # Serialize the updated project for the response
    updated_project_read_schema = ProjectRead.model_validate(updated_project).model_dump()

    return jsonify(updated_project_read_schema), HTTPStatus.OK

@projects_bp.route('/<int:project_id>', methods=['DELETE'])
def delete_project_route(project_id: int):
    """Endpoint to delete a project by ID."""
    # delete_project will raise NotFound if project_id is invalid
    delete_project(project_id)

    # Return 204 No Content for successful deletion
    return '', HTTPStatus.NO_CONTENT