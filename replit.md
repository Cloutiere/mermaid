# Éditeur Visuel de Structure Narrative Mermaid

## Vue d'ensemble du Projet

Application fullstack pour l'édition de graphes narratifs utilisant Mermaid.js, avec une architecture découplée Python/Flask + React/TypeScript.

**Statut**: Environnement configuré, prêt pour le développement

**Date de création**: 5 novembre 2025

## Architecture

### Stack Technique
- **Backend**: Python 3.11 + Flask + SQLAlchemy/SQLModel + PostgreSQL
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + Mermaid.js
- **Base de données**: PostgreSQL (Neon, fournie par Replit)

### Principes Architecturaux Clés
1. **Base de données comme source de vérité**: La structure relationnelle PostgreSQL est l'autorité pour les données narratives
2. **Code Mermaid comme artefact**: Le code Mermaid est généré à partir de la DB, pas l'inverse
3. **Transformation bidirectionnelle**: Services Python dédiés pour Import (Mermaid → DB) et Export (DB → Mermaid)
4. **API RESTful**: Communication Frontend ↔ Backend via JSON
5. **Synchronisation des types**: Schémas Pydantic (Python) ↔ Interfaces TypeScript

## Modèle de Données (Hiérarchie)

```
Project (Saga)
  └── SubProject (Livre/Graphe Narratif)
       ├── Node (Paragraphe/Nœud)
       ├── Relationship (Lien entre nœuds)
       └── ClassDef (Définition de style)
```

### Tables Principales
- **Project**: Conteneur racine pour les sagas
- **SubProject**: Graphe narratif complet avec métadonnées visuelles JSON
- **Node**: Nœuds individuels avec identifiants Mermaid, titre, contenu texte
- **Relationship**: Liens dirigés entre nœuds (VISIBLE/INVISIBLE)
- **ClassDef**: Définitions de style CSS/Mermaid

Voir `attached_assets/backendappmodels.py_1762371637524.txt` pour le schéma SQLModel complet.

## Structure du Projet

```
backend/          - API Flask, modèles, services de transformation
  app/            - Code applicatif (à développer)
  app.py          - Point d'entrée minimal
  requirements.txt - Dépendances Python (installées)

frontend/         - SPA React/TypeScript
  src/            - Code source (à développer)
  package.json    - Dépendances Node.js (installées)
  vite.config.ts  - Configuration Vite (proxy API vers :5001)

attached_assets/  - Documents de référence
  - DDA_mermaid_1762371637525.md
  - backendappmodels.py_1762371637524.txt
```

## Préférences Utilisateur

### Développement
- **Pas de code généré automatiquement**: L'utilisateur souhaite coder lui-même
- **Configuration seulement**: Environnement, dépendances, structure préparés
- **Langue**: Français pour la communication

### Workflow
- Frontend sur port 5000 (configuré automatiquement)
- Backend prévu sur port 5001 (à démarrer manuellement)

## Configuration Actuelle

### Complété ✅
- [x] Python 3.11 et Node.js 20 installés
- [x] PostgreSQL créé avec variables d'environnement
- [x] Dépendances backend installées (Flask, SQLAlchemy, Pydantic, Flask-Migrate, etc.)
- [x] Dépendances frontend installées (React, TypeScript, Vite, Tailwind, Mermaid)
- [x] Arborescence du projet créée
- [x] Fichiers de configuration créés
- [x] Workflow frontend configuré
- [x] Points d'entrée créés (run.py, main.tsx)
- [x] **Modèles SQLAlchemy complets** (backend/app/models.py)
- [x] **Base de données initialisée** avec Flask-Migrate
- [x] **Toutes les tables créées** (project, subproject, node, relationship, classdef)

### À Développer 🔨
#### Backend
1. ~~Modèles SQLAlchemy~~ ✅ **TERMINÉ**
2. ~~Configuration DB et migrations~~ ✅ **TERMINÉ**
3. Schémas Pydantic (`backend/app/schemas.py`)
4. Routes API RESTful (`backend/app/routes/`)
5. Service de parsing Mermaid → DB (`backend/app/services/mermaid_parser.py`)
6. Service de génération DB → Mermaid (`backend/app/services/mermaid_generator.py`)

#### Frontend
1. Types TypeScript API (`frontend/src/types/api.ts`)
2. Client API Axios (`frontend/src/services/api.ts`)
3. Composant MermaidViewer avec Mermaid.js
4. Composant NodeEditor
5. Composant GraphEditor principal
6. Router et navigation

## Variables d'Environnement

Automatiquement disponibles (via Replit):
- `DATABASE_URL` - URL complète PostgreSQL
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`
- `SESSION_SECRET`

## Commandes Utiles

```bash
# Lancer le frontend (port 5000) - Automatique via workflow
cd frontend && npm run dev

# Lancer le backend (port 5001) - Manuel
cd backend && python app.py

# Vérifier la santé du backend
curl http://localhost:5001/api/health
```

## Documents de Référence

- **Document de Décision d'Architecture**: `attached_assets/DDA_mermaid_1762371637525.md`
- **Modèle de données complet**: `attached_assets/backendappmodels.py_1762371637524.txt`
- **Guide de structure**: `STRUCTURE.md`
- **Instructions**: `README.md`

## Modifications Récentes

### 5 novembre 2025 - Configuration initiale ET base de données
- Installation complète de l'environnement Python/Flask + React/TypeScript
- Configuration PostgreSQL avec toutes les variables d'environnement
- Installation de toutes les dépendances
- Création de l'arborescence du projet
- Configuration Vite avec proxy API
- Mise en place du workflow frontend
- **Création des modèles SQLAlchemy complets** (Project, SubProject, Node, Relationship, ClassDef)
- **Initialisation Flask-Migrate** et génération de la migration initiale
- **Toutes les tables créées dans PostgreSQL** avec relations et contraintes
- Fichier principal renommé de `app.py` à `run.py` pour éviter conflits de noms
