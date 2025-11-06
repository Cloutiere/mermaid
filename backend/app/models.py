# backend/app/models.py
# Version 1.1
"""
Modèles de données pour l'éditeur visuel de structure narrative Mermaid.
Utilise SQLAlchemy 2.0 avec typage moderne pour la compatibilité avec Flask-Migrate.
"""
import enum
from typing import Optional, List
from sqlalchemy import String, Text, ForeignKey, Enum as SQLEnum, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import db


# --- Définition des ENUM pour l'intégrité des données ---
class LinkType(str, enum.Enum):
    """
    Type de lien entre deux nœuds, utilisé pour la visualisation dans Mermaid.
    """
    VISIBLE = "VISIBLE"
    INVISIBLE = "INVISIBLE"


# --- 1. Modèle Project (Saga) ---
class Project(db.Model):
    """
    Conteneur de haut niveau pour l'ensemble des subprojects.
    """
    __tablename__ = 'project'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Relations
    subprojects: Mapped[List["SubProject"]] = relationship(back_populates="project", cascade="all, delete-orphan")


# --- 2. Modèle SubProject (Livre / Graphe Narratif) ---
class SubProject(db.Model):
    """
    Représente un unique graphe narratif.
    """
    __tablename__ = 'subproject'

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('project.id'), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    graph_direction: Mapped[str] = mapped_column(String(10), nullable=False, server_default="TD", default="TD")
    mermaid_definition: Mapped[str] = mapped_column(Text, nullable=False)
    visual_layout: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relations
    project: Mapped["Project"] = relationship(back_populates="subprojects")
    nodes: Mapped[List["Node"]] = relationship(back_populates="subproject", cascade="all, delete-orphan")
    relationships: Mapped[List["Relationship"]] = relationship(back_populates="subproject", cascade="all, delete-orphan")
    class_defs: Mapped[List["ClassDef"]] = relationship(back_populates="subproject", cascade="all, delete-orphan")


# --- 3. Modèle Node (Paragraphe / Unité du Graphe) ---
class Node(db.Model):
    """
    Représente un nœud individuel dans un subproject.
    """
    __tablename__ = 'node'
    __table_args__ = (UniqueConstraint('subproject_id', 'mermaid_id', name='uq_subproject_mermaid_id'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    subproject_id: Mapped[int] = mapped_column(ForeignKey('subproject.id'), nullable=False, index=True)
    mermaid_id: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    text_content: Mapped[str] = mapped_column(Text, nullable=False)
    style_class_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relations
    subproject: Mapped["SubProject"] = relationship(back_populates="nodes")
    source_relationships: Mapped[List["Relationship"]] = relationship(
        foreign_keys="Relationship.source_node_id",
        back_populates="source_node",
        cascade="all, delete-orphan"
    )
    target_relationships: Mapped[List["Relationship"]] = relationship(
        foreign_keys="Relationship.target_node_id",
        back_populates="target_node",
        cascade="all, delete-orphan"
    )


# --- 4. Modèle Relationship (Lien entre Nœuds) ---
class Relationship(db.Model):
    """
    Représente un lien dirigé entre deux nœuds.
    """
    __tablename__ = 'relationship'

    id: Mapped[int] = mapped_column(primary_key=True)
    subproject_id: Mapped[int] = mapped_column(ForeignKey('subproject.id'), nullable=False, index=True)
    source_node_id: Mapped[int] = mapped_column(ForeignKey('node.id'), nullable=False, index=True)
    target_node_id: Mapped[int] = mapped_column(ForeignKey('node.id'), nullable=False, index=True)
    label: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    link_type: Mapped[LinkType] = mapped_column(SQLEnum(LinkType, name="link_type_enum", create_type=True), nullable=False)

    # Relations
    subproject: Mapped["SubProject"] = relationship(back_populates="relationships")
    source_node: Mapped["Node"] = relationship(foreign_keys=[source_node_id], back_populates="source_relationships")
    target_node: Mapped["Node"] = relationship(foreign_keys=[target_node_id], back_populates="target_relationships")


# --- 5. Modèle ClassDef (Définition de Style Mermaid) ---
class ClassDef(db.Model):
    """
    Définit des styles ou des classes utilisés dans le graphe.
    """
    __tablename__ = 'classdef'
    __table_args__ = (UniqueConstraint('subproject_id', 'name', name='uq_subproject_classdef_name'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    subproject_id: Mapped[int] = mapped_column(ForeignKey('subproject.id'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    definition_raw: Mapped[str] = mapped_column(Text, nullable=False)

    # Relations
    subproject: Mapped["SubProject"] = relationship(back_populates="class_defs")