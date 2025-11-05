# backend/app/__init__.py
import os
from flask import Flask, Blueprint, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialisation des extensions qui seront liées à l'application plus tard
db = SQLAlchemy()
migrate = Migrate()

# Définition du Blueprint principal
main = Blueprint('main', __name__)

@main.route('/api/health', methods=['GET'])
def health_check():
    """Route de vérification de santé."""
    return jsonify({'status': 'ok', 'message': 'Backend Flask is running'})

def create_app(config_object=None):
    """
    Fonction d'usine pour créer l'application Flask.
    """
    app = Flask(__name__)
    
    # Activation de CORS
    CORS(app)
    
    # Configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        # Configuration par défaut (lecture des variables d'environnement)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialisation des extensions avec l'application
    db.init_app(app)
    migrate.init_app(app, db)

    # Importation des modèles pour que Fla puisse les voir
    # C'est essentiel lorsque db est initialisé dans __init__.py
    from app import models  # noqa: F401

    # Enregistrement des Blueprints
    app.register_blueprint(main)
    
    return app