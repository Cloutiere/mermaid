# backend/tests/conftest.py
# Version 1.0

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Importation de la fonction factory create_app et de l'instance db globale
from app import create_app, db as app_db

# Importation des modèles pour que SQLAlchemy puisse les référencer lors de la création des tables
from app import models  # noqa: F401

@pytest.fixture(scope='session')
def app():
    """
    Fixture pour créer une instance de l'application Flask configurée pour les tests.
    Utilise la configuration de test (TestingConfig) qui configure une base de données en mémoire.
    """
    # Crée l'application en utilisant la configuration de test
    flask_app = create_app('testing')

    # Assure que le contexte de l'application est poussé pour que db soit utilisable
    with flask_app.app_context():
        yield flask_app

@pytest.fixture(scope='session')
def _db():
    """
    Fixture pour initialiser la base de données SQLAlchemy pour les tests.
    Elle crée toutes les tables et est disponible au niveau de la session.
    """
    with app().app_context():
        app_db.create_all()
        yield app_db
        app_db.drop_all()

@pytest.fixture(scope='function')
def db_session(app, _db):
    """
    Fixture pour une session de base de données isolée pour chaque test.
    Chaque test obtient sa propre transaction qui est annulée à la fin.
    """
    connection = _db.engine.connect()
    transaction = connection.begin()

    # Crée une nouvelle session liée à cette transaction isolée
    session = _db.session_factory(bind=connection)
    _db.session = session # Assigne la session à l'instance db globale pour qu'elle soit utilisée par les modèles

    yield session # Fournit la session au test

    # Annule la transaction et ferme la connexion après le test
    transaction.rollback()
    connection.close()
    session.close()

# Note : Si vous avez besoin d'un client de test pour faire des requêtes API, vous pouvez ajouter :
# @pytest.fixture(scope='session')
# def client(app):
#     return app.test_client()