# Éditeur Visuel de Structure Narrative Mermaid

Application fullstack pour l'édition de graphes narratifs utilisant Mermaid, avec architecture découplée Python/Flask + React/TypeScript.

## Architecture

- **Backend**: Python/Flask + SQLAlchemy + PostgreSQL
- **Frontend**: React/TypeScript + Vite + Tailwind CSS + Mermaid.js
- **Base de données**: PostgreSQL (fournie par Replit)

## Structure du Projet

```
/
├── backend/                 # Backend Python/Flask
│   ├── app/                # Code applicatif (à développer)
│   ├── requirements.txt    # Dépendances Python
│   └── .flaskenv          # Configuration Flask
│
├── frontend/               # Frontend React/TypeScript
│   ├── src/               # Code source React (à développer)
│   ├── index.html         # Point d'entrée HTML
│   ├── package.json       # Dépendances Node.js
│   ├── tsconfig.json      # Configuration TypeScript
│   ├── vite.config.ts     # Configuration Vite
│   ├── tailwind.config.js # Configuration Tailwind
│   └── postcss.config.js  # Configuration PostCSS
│
├── .env.example           # Template des variables d'environnement
├── .gitignore            # Fichiers à ignorer par Git
└── README.md             # Ce fichier

```

## Modèle de Données (selon DDA)

### Tables principales:
- **Project (Saga)**: Conteneur racine
- **SubProject (Livre)**: Graphe narratif complet  
- **Node (Paragraphe)**: Nœuds du graphe
- **Relationship (Lien)**: Liens entre nœuds
- **ClassDef**: Définitions de style Mermaid

Voir `attached_assets/backendappmodels.py_1762371637524.txt` pour le schéma SQLModel complet.

## Installation des Dépendances

### Backend (Python)
```bash
cd backend
pip install -r requirements.txt
```

### Frontend (Node.js)
```bash
cd frontend
npm install
```

## Configuration de l'Environnement

Les variables d'environnement PostgreSQL sont automatiquement fournies par Replit:
- `DATABASE_URL`
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`

Copiez `.env.example` vers `.env` et ajustez si nécessaire.

## Développement

### Lancer le Backend (port 5001)
```bash
cd backend
python app.py
```

### Lancer le Frontend (port 5000)
```bash
cd frontend
npm run dev
```

Le frontend proxy les appels `/api` vers `http://localhost:5001`.

## Services Critiques à Implémenter

Selon le Document de Décision d'Architecture (DDA):

### Backend
1. **Modèles SQLAlchemy/SQLModel** (voir fichier fourni)
2. **Service de Parsing** (Import: Mermaid → DB)
3. **Service de Génération** (Export: DB → Mermaid)
4. **API RESTful** avec endpoints CRUD
5. **Validation Pydantic** pour les schémas API

### Frontend
1. **Composants React** pour l'affichage des graphes
2. **Intégration Mermaid.js** pour le rendu
3. **Interfaces TypeScript** synchronisées avec les schémas Pydantic
4. **Gestion d'état** pour la synchronisation UI ↔ Backend
5. **Éditeur interactif** pour création/modification de nœuds

## Flux de Données

```
UI (React) → Requête API → Backend Flask → SQLAlchemy → PostgreSQL
                                    ↓
                           Service de Génération
                                    ↓
                           Code Mermaid généré
                                    ↓
                           UI (Mermaid.js render)
```

## Références

- **DDA**: `attached_assets/DDA_mermaid_1762371637525.md`
- **Modèles**: `attached_assets/backendappmodels.py_1762371637524.txt`
- Documentation Mermaid: https://mermaid.js.org/
- Documentation Flask: https://flask.palletsprojects.com/
- Documentation React: https://react.dev/

## Notes Importantes

- La base de données PostgreSQL est la **source de vérité**
- Le code Mermaid est un **artefact généré** à partir des tables
- Les métadonnées visuelles sont stockées en JSON dans `SubProject.visual_layout`
- Synchronisation stricte requise entre schémas Pydantic (Python) et interfaces TypeScript
