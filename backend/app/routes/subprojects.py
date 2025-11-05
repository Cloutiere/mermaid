# backend/app/routes/subprojects.py
from flask import Blueprint, jsonify

# Définition du Blueprint pour les sous-projets
subprojects_bp = Blueprint('subprojects', __name__)

@subprojects_bp.route('/', methods=['GET'])
def list_subprojects():
    """Endpoint de base pour lister les sous-projets."""
    # Ceci est un placeholder, la logique sera implémentée plus tard
    return jsonify({"message": "Subprojects API route is active", "data": []}), 200

# D'autres routes (POST, PUT, DELETE) seront ajoutées ici