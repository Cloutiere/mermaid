# backend/app/routes/projects.py
from flask import Blueprint, jsonify

# Définition du Blueprint pour les projets
projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/', methods=['GET'])
def list_projects():
    """Endpoint de base pour lister les projets."""
    # Ceci est un placeholder, la logique sera implémentée plus tard
    return jsonify({"message": "Projects API route is active", "data": []}), 200

# D'autres routes (POST, PUT, DELETE) seront ajoutées ici