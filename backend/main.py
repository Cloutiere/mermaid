import os
from flask import Flask
from flask_migrate import Migrate
from sqlmodel import create_engine, SQLModel
from app.models import * # IMPORTANT: Importe tous les modèles pour que Alembic les voie

# Importe l'instance d'application Flask déjà définie dans app.py
from app.app import app # Note: Assurez-vous que l'instance est nommée 'app'

# 1. Configuration de l'Engine PostgreSQL
# Récupère l'URL de la DB depuis l'environnement (Replit/Neon)
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise EnvironmentError("DATABASE_URL non définie. Impossible de se connecter à la DB.")

# Crée l'Engine (non utilisé directement ici, mais utile pour des opérations manuelles futures)
engine = create_engine(DATABASE_URL, echo=False)

# 2. Initialisation de Fla (Alembic)
# On passe SQLModel.metadata comme source de vérité (db=...)
# render_as_batch=True est crucial pour les types ENUM dans PostgreSQL
migrate = Migrate(app, db=SQLModel.metadata, render_as_batch=True)

# L'application est maintenant configurée pour les commandes 'flask db'