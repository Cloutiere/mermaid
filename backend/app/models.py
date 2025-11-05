"""
Modèles de données pour l'éditeur visuel de structure narrative Mermaid.
Utilise SQLAlchemy avec Flask-SQLAlchemy pour la compatibilité avec Flask-Migrate.
"""
import enum
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

# Initialisation de db sera faite dans app.py
db = SQLAlchemy()


# --- Définition des ENUM pour l'intégrité des données ---
class LinkType(str, enum.Enum):
    """
    Type de lien entre deux nœuds, utilisé pour la visualisation dans Mermaid (DDA 4.A).
    """
    VISIBLE = "VISIBLE"
    INVISIBLE = "INVISIBLE"


# --- 1. Modèle Project (Saga) ---
class Project(db.Model):
    """
    Conteneur de haut niveau pour l'ensemble des subprojects.
    """
    __tablename__ = 'project'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, index=True)
    
    # Relations
    subprojects = relationship("SubProject", back_populates="project", cascade="all, delete-orphan")


# --- 2. Modèle SubProject (Livre / Graphe Narratif) ---
class SubProject(db.Model):
    """
    Représente un unique graphe narratif.
    """
    __tablename__ = 'subproject'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    mermaid_definition = Column(Text, nullable=False)
    visual_layout = Column(JSON, nullable=True)
    
    # Relations
    project = relationship("Project", back_populates="subprojects")
    nodes = relationship("Node", back_populates="subproject", cascade="all, delete-orphan")
    relationships = relationship("Relationship", back_populates="subproject", cascade="all, delete-orphan")
    class_defs = relationship("ClassDef", back_populates="subproject", cascade="all, delete-orphan")


# --- 3. Modèle Node (Paragraphe / Unité du Graphe) ---
class Node(db.Model):
    """
    Représente un nœud individuel dans un subproject.
    """
    __tablename__ = 'node'
    __table_args__ = (UniqueConstraint('subproject_id', 'mermaid_id', name='uq_subproject_mermaid_id'),)
    
    id = Column(Integer, primary_key=True)
    subproject_id = Column(Integer, ForeignKey('subproject.id'), nullable=False, index=True)
    mermaid_id = Column(String(50), nullable=False)
    title = Column(String(255), nullable=True)
    text_content = Column(Text, nullable=False)
    style_class_ref = Column(String(100), nullable=True)
    
    # Relations
    subproject = relationship("SubProject", back_populates="nodes")
    source_relationships = relationship(
        "Relationship",
        foreign_keys="Relationship.source_node_id",
        back_populates="source_node",
        cascade="all, delete-orphan"
    )
    target_relationships = relationship(
        "Relationship",
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
    
    id = Column(Integer, primary_key=True)
    subproject_id = Column(Integer, ForeignKey('subproject.id'), nullable=False, index=True)
    source_node_id = Column(Integer, ForeignKey('node.id'), nullable=False, index=True)
    target_node_id = Column(Integer, ForeignKey('node.id'), nullable=False, index=True)
    label = Column(Text, nullable=True)
    color = Column(String(20), nullable=True)
    link_type = Column(SQLEnum(LinkType, name="link_type_enum", create_type=True), nullable=False)
    
    # Relations
    subproject = relationship("SubProject", back_populates="relationships")
    source_node = relationship("Node", foreign_keys=[source_node_id], back_populates="source_relationships")
    target_node = relationship("Node", foreign_keys=[target_node_id], back_populates="target_relationships")


# --- 5. Modèle ClassDef (Définition de Style Mermaid) ---
class ClassDef(db.Model):
    """
    Définit des styles ou des classes utilisés dans le graphe.
    """
    __tablename__ = 'classdef'
    __table_args__ = (UniqueConstraint('subproject_id', 'name', name='uq_subproject_classdef_name'),)
    
    id = Column(Integer, primary_key=True)
    subproject_id = Column(Integer, ForeignKey('subproject.id'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    definition_raw = Column(Text, nullable=False)
    
    # Relations
    subproject = relationship("SubProject", back_populates="class_defs")
