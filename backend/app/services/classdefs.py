# backend/app/services/classdefs.py
# Version 1.0
"""
Service layer for ClassDef business logic.
Handles CRUD operations and ensures data consistency, such as updating
the parent SubProject's Mermaid definition upon changes.
"""

from typing import List, Optional

from werkzeug.exceptions import NotFound, Conflict
from sqlalchemy import update as sqlalchemy_update

from app import db
from app.models import ClassDef, SubProject, Node
from app.schemas import ClassDefCreate
from app.services.mermaid_generator import generate_mermaid_from_subproject


def get_classdef_by_id(classdef_id: int) -> ClassDef:
    """
    Retrieves a ClassDef by its ID.

    Args:
        classdef_id: The ID of the ClassDef to retrieve.

    Returns:
        The ClassDef instance.

    Raises:
        NotFound: If no ClassDef with the given ID is found.
    """
    classdef = db.session.get(ClassDef, classdef_id)
    if not classdef:
        raise NotFound(f"ClassDef with ID {classdef_id} not found.")
    return classdef


def get_all_classdefs(subproject_id: Optional[int] = None) -> List[ClassDef]:
    """
    Retrieves all ClassDefs, optionally filtered by subproject_id.

    Args:
        subproject_id: The ID of the subproject to filter by.

    Returns:
        A list of ClassDef instances.
    """
    query = db.select(ClassDef).order_by(ClassDef.id)
    if subproject_id:
        query = query.filter_by(subproject_id=subproject_id)
    return list(db.session.execute(query).scalars().all())


def create_classdef(data: ClassDefCreate) -> ClassDef:
    """
    Creates a new ClassDef and regenerates the SubProject's Mermaid definition.

    Args:
        data: The Pydantic schema containing the data for the new ClassDef.

    Returns:
        The newly created ClassDef instance.

    Raises:
        NotFound: If the specified SubProject does not exist.
        Conflict: If a ClassDef with the same name already exists in the SubProject.
    """
    subproject = db.session.get(SubProject, data.subproject_id)
    if not subproject:
        raise NotFound(f"SubProject with ID {data.subproject_id} not found.")

    # Check for uniqueness within the subproject (AC 2.8)
    existing = db.session.execute(
        db.select(ClassDef).filter_by(subproject_id=data.subproject_id, name=data.name)
    ).scalar_one_or_none()
    if existing:
        raise Conflict(f"ClassDef with name '{data.name}' already exists in this subproject.")

    new_classdef = ClassDef(**data.model_dump())
    db.session.add(new_classdef)

    # Regenerate Mermaid definition (AC 2.7) and commit atomically
    subproject.mermaid_definition = generate_mermaid_from_subproject(subproject.id)
    db.session.commit()

    return new_classdef


def update_classdef(classdef_id: int, data: ClassDefCreate) -> ClassDef:
    """
    Updates an existing ClassDef and regenerates the SubProject's Mermaid definition.

    Args:
        classdef_id: The ID of the ClassDef to update.
        data: The Pydantic schema containing the updated data.

    Returns:
        The updated ClassDef instance.

    Raises:
        NotFound: If the ClassDef or its SubProject is not found.
        Conflict: If the new name conflicts with an existing ClassDef in the SubProject.
    """
    classdef = get_classdef_by_id(classdef_id)

    # Check for name uniqueness if the name is being changed (AC 2.8)
    if classdef.name != data.name:
        existing = db.session.execute(
            db.select(ClassDef).filter_by(subproject_id=data.subproject_id, name=data.name)
        ).scalar_one_or_none()
        if existing:
            raise Conflict(f"ClassDef with name '{data.name}' already exists in this subproject.")

    # Update fields
    classdef.name = data.name
    classdef.definition_raw = data.definition_raw
    # subproject_id cannot be changed as it would be a move, not an update.

    subproject = db.session.get(SubProject, classdef.subproject_id)
    if not subproject:
         raise NotFound(f"SubProject with ID {classdef.subproject_id} not found.")

    # Regenerate Mermaid definition (AC 2.7) and commit atomically
    subproject.mermaid_definition = generate_mermaid_from_subproject(subproject.id)
    db.session.commit()

    return classdef


def delete_classdef(classdef_id: int) -> None:
    """
    Deletes a ClassDef, clears its references from Nodes, and regenerates
    the SubProject's Mermaid definition.

    Args:
        classdef_id: The ID of the ClassDef to delete.

    Raises:
        NotFound: If the ClassDef is not found.
    """
    classdef = get_classdef_by_id(classdef_id)
    subproject_id = classdef.subproject_id
    classdef_name = classdef.name

    subproject = db.session.get(SubProject, subproject_id)
    if not subproject:
        raise NotFound(f"Associated SubProject with ID {subproject_id} not found.")

    # AC 2.4: Set style_class_ref to NULL for all nodes using this class
    # Use a bulk update for efficiency
    db.session.execute(
        sqlalchemy_update(Node)
        .where(Node.subproject_id == subproject_id, Node.style_class_ref == classdef_name)
        .values(style_class_ref=None)
    )

    # Now, delete the ClassDef object
    db.session.delete(classdef)

    # AC 2.7: Regenerate the mermaid definition to reflect the changes
    subproject.mermaid_definition = generate_mermaid_from_subproject(subproject_id)

    db.session.commit()