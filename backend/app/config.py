# backend/app/config.py
import os
from dotenv import load_dotenv

# Charger les variables d'environnement du fichier .env
load_dotenv()

class Config:
    """Configuration de base pour l'application."""

    # Sécurité et Authentification
    SECRET_KEY = os.getenv('SESSION_SECRET', 'a_default_secret_for_dev')

    # Base de données
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS (Sécurité)
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5000')

    # Autres configurations
    TESTING = False
    DEBUG = False

class DevelopmentConfig(Config):
    """Configurations spécifiques au développement."""
    DEBUG = True

class ProductionConfig(Config):
    """Configurations spécifiques à la production."""
    # Désactiver le mode débogage en production
    DEBUG = False

class TestingConfig(Config):
    """Configurations spécifiques aux tests."""
    TESTING = True
    # Utiliser une base de données en mémoire ou de test
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:')

# Mappage des noms d'environnement vers les classes de configuration
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(env_name=None):
    """Récupère la configuration appropriée en fonction du nom de l'environnement."""
    if env_name is None:
        env_name = os.getenv('FLASK_ENV', 'default')

    return config_map.get(env_name.lower(), config_map['default'])