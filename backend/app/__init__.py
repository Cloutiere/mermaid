# backend/app/__init__.py
import os
from flask import Flask, Blueprint, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Import de la configuration (pas de routes ici pour éviter les imports circulaires)
from app.config import get_config

# Initialisation des extensions qui seront liées à l'application plus tard
db = SQLAlchemy()
migrate = Migrate()

# Définition du Blueprint principal (pour les routes globales comme le health check)
main = Blueprint('main', __name__)

@main.route('/api/health', methods=['GET'])
def health_check():
    """Route de vérification de santé."""
    return jsonify({'status': 'ok', 'message': 'Backend Flask is running'})

def handle_api_error(e):
    """
    Gestionnaire d'erreurs pour retourner les erreurs HTTP courantes au format JSON.
    """
    # Tente de récupérer le code de statut de l'exception, sinon utilise 500.
    status_code = getattr(e, 'code', 500)

    # Récupère la description de l'erreur
    message = getattr(e, 'description', 'An unexpected error occurred.')

    # Pour les 404 non capturées, fournit un message standard
    if status_code == 404 and not getattr(e, 'description', None):
        message = 'The requested URL was not found on the server.'

    # Pour les erreurs serveur, on peut masquer les détails spécifiques si en production
    if status_code >= 500 and not get_config().DEBUG:
        message = 'Internal Server Error.'

    return jsonify({'error': message, 'status_code': status_code}), status_code


def create_app(config_name=None):
    """
    Fonction d'usine pour créer l'application Flask.
    """
    app = Flask(__name__)

    # Configuration
    config = get_config(config_name)
    app.config.from_object(config)

    # Activation de CORS sécurisée, utilisant la variable FRONTEND_URL de la configuration
    CORS(app, resources={r"/api/*": {
        "origins": config.FRONTEND_URL,
        "supports_credentials": True,
        "methods": ["GET", "POST", "PUT", "DELETE"]
    }})

    # Initialisation des extensions avec l'application
    db.init_app(app)
    migrate.init_app(app, db)

    # Enregistrement des gestionnaires d'erreurs
    app.register_error_handler(400, handle_api_error) # Bad Request
    app.register_error_handler(404, handle_api_error) # Not Found
    app.register_error_handler(405, handle_api_error) # Method Not Allowed
    app.register_error_handler(500, handle_api_error) # Internal Server Error

    # Importation des modèles pour que Flask puisse les voir (nécessaire pour Alembic/SQLAlchemy)
    from app import models  # noqa: F401

    # Enregistrement des Blueprints
    app.register_blueprint(main) # Le health check est à /api/health

    # Import des blueprints ICI (après init de db) pour éviter les imports circulaires
    from app.routes.projects import projects_bp
    from app.routes.subprojects import subprojects_bp
    from app.routes.nodes import nodes_bp

    # Blueprints d'API structurés
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(subprojects_bp, url_prefix='/api/subprojects')
    app.register_blueprint(nodes_bp, url_prefix='/api/nodes')

    return app