# backend/app/config.py
# Version 1.0

import os
from dotenv import load_dotenv

# Charger les variables d'environnement à partir d'un fichier .env
# Ceci est utile pour les configurations locales (dev, test)
load_dotenv()

class BaseConfig:
    """Configuration de base pour l'application."""
    # Clé secrète pour signer les tokens de session, etc.
    # Doit être une variable d'environnement en production.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'une-cle-secrete-par-defaut-qui-devrait-etre-changee')

    # Configuration de la base de données PostgreSQL
    # Utilise une variable d'environnement DATABASE_URL
    # Exemple: postgresql://user:password@host:port/database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:password@host:port/database')
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Désactive le suivi des modifications pour la performance
    
    # Options du moteur SQLAlchemy pour gérer les connexions perdues
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Vérifie que la connexion est valide avant de l'utiliser
        'pool_recycle': 300,    # Recycle les connexions après 5 minutes (300 secondes)
        'pool_size': 10,        # Nombre de connexions permanentes dans le pool
        'max_overflow': 20,     # Connexions supplémentaires au-delà du pool_size
    }

    # URL du frontend pour la configuration CORS
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5000') # Par défaut, le frontend tourne sur le port 5000

    # Mode Debug
    DEBUG = False
    TESTING = False

class DevelopmentConfig(BaseConfig):
    """Configuration pour l'environnement de développement."""
    DEBUG = True
    TESTING = True
    # Utilise une URI de base de données locale pour le développement
    # Assurez-vous que cette variable d'environnement est définie ou modifiez-la directement.
    # Exemple: export DATABASE_URL="postgresql://myuser:mypassword@localhost:5432/mydatabase_dev"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/narrative_editor_dev')
    # Si vous n'avez pas configuré DATABASE_URL, vous pouvez utiliser ceci pour tester rapidement
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Utilisation d'une base de données en mémoire pour le dev rapide

class TestingConfig(BaseConfig):
    """Configuration pour les tests automatisés."""
    DEBUG = True
    TESTING = True
    # Utilise une base de données en mémoire pour les tests afin d'isoler les exécutions
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Pas nécessaire en mémoire

class ProductionConfig(BaseConfig):
    """Configuration pour l'environnement de production."""
    DEBUG = False
    TESTING = False
    
    def __init__(self):
        super().__init__()
        # Assurez-vous que DATABASE_URL est correctement configurée dans l'environnement de production
        # Exemple: DATABASE_URL="postgresql://user:password@prod-db.example.com:5432/narrative_editor"
        self.SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        if not self.SQLALCHEMY_DATABASE_URI:
            raise ValueError("DATABASE_URL doit être définie en mode production.")

        # La clé secrète est CRUCIALE en production
        self.SECRET_KEY = os.environ.get('SECRET_KEY')
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY doit être définie en mode production.")

        # FRONTEND_URL doit être l'URL de votre application frontend déployée
        self.FRONTEND_URL = os.environ.get('FRONTEND_URL')
        if not self.FRONTEND_URL:
            raise ValueError("FRONTEND_URL doit être définie en mode production.")


# Dictionnaire pour mapper les noms de configuration aux classes
config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig
)

def get_config(config_name: str | None = None):
    """
    Récupère l'objet de configuration approprié.
    Si config_name est None, utilise la variable d'environnement FLASK_ENV.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development') # Par défaut, développement

    if config_name not in config_by_name:
        raise ValueError(f"Configuration '{config_name}' non reconnue. Options disponibles : {list(config_by_name.keys())}")

    return config_by_name[config_name]()