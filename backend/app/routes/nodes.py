# backend/app/routes/nodes.py
from flask import Blueprint, jsonify

# Définition du Blueprint pour les noeuds
nodes_bp = Blueprint('nodes', __name__)

@nodes_bp.route('/', methods=['GET'])
def list_nodes():
    """Endpoint de base pour lister les noeuds."""
    # Ceci est un placeholder, la logique sera implémentée plus tard
    return jsonify({"message": "Nodes API route is active", "data": []}), 200

# D'autres routes (POST, PUT, DELETE) seront ajoutées ici