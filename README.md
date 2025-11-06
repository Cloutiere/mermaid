# Éditeur Visuel de Structure Narrative Mermaid

Application fullstack pour l'édition de graphes narratifs utilisant Mermaid, avec architecture découplée Python/Flask + React/TypeScript.

## Architecture

- **Backend**: Python/Flask + SQLAlchemy + PostgreSQL
- **Frontend**: React/TypeScript + Vite + Tailwind CSS + Mermaid.js
- **Base de données**: PostgreSQL (fournie par Replit)

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
python run.py
```

### Lancer le Frontend (port 5000)
```bash
cd frontend
npm run dev
```

Le frontend proxy les appels `/api` vers `http://localhost:5001`.

## Services Critiques Implémentés (V1.0)

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

## 📁 Structure du Projet (Détail V1.0)

```
/
├── backend/                    # Backend Python/Flask (Architecture complète - Voir DDA.md)
│   ├── app/                    # Modules applicatifs Python
│   │   ├── models.py          # ✅ Modèles SQLAlchemy (Project, SubProject, Node, Relationship, ClassDef)
│   │   ├── __init__.py        # ✅ Factory Pattern
│   │   ├── schemas.py         # ✅ Schémas Pydantic pour API
│   │   ├── routes/            # ✅ Routes API RESTful complètes (CRUD + Mermaid)
│   │   └── services/          # ✅ Services métier critiques (CRUD + Mermaid Transform)
│   ├── migrations/            # ✅ Flask-Migrate
│   ├── run.py                 # ✅ Point d'entrée Flask
│   └── requirements.txt       # ✅ Dépendances Python installées
│
├── frontend/
│   ├── src/
│   │   ├── components/        # ✅ Composants React interactifs
│   │   │   ├── ProjectCard.tsx    # ✅ Carte pour un projet unique (CRUD Projet + SubProject UI)
│   │   │   ├── ProjectForm.tsx    # ✅ Formulaire de création de projet
│   │   │   ├── SubProjectCard.tsx # ✅ Carte pour un sous-projet (Implémenté)
│   │   │   ├── SubProjectForm.tsx # ✅ Formulaire de création de sous-projet (Implémenté)
│   │   │   ├── MermaidViewer.tsx  # ✅ TERMINÉ (Rendu du graphe Mermaid, Corrigé pour l'asynchrone)
│   │   │   ├── MermaidEditor.tsx  # ✅ TERMINÉ (Éditeur de code Mermaid)
│   │   │   └── ConfirmDialog.tsx  # ✅ TERMINÉ (Dialogue de confirmation)
│   │   ├── pages/             # ✅ Pages principales de l'application
│   │   │   ├── ProjectListPage.tsx  # ✅ Liste des projets (CRUD Projet UI fonctionnel)
│   │   │   └── GraphEditorPage.tsx  # ✅ TERMINÉ (Éditeur de Graphe : Chargement, Layout, Édition, Visualisation, Sauvegarde, Export, Import, Navigation)
│   │   ├── types/             # ✅ Interfaces TypeScript pour API
│   │   │   └── api.ts         # ✅ Types synchronisés avec Pydantic
│   │   ├── services/          # ✅ Services frontend
│   │   │   └── api.ts         # ✅ Client API (axios Wrapper)
│   │   ├── App.tsx            # ✅ Composant racine (configuration du routage)
│   │   ├── main.tsx           # ✅ Point d'entrée React (avec BrowserRouter)
│   │   ├── index.css          # ✅ Styles Tailwind
│   │   └── vite-env.d.ts      # ✅ Types Vite
│   ├── index.html             # ✅ Template HTML
│   ├── package.json           # ✅ Dépendances Node.js installées
│   ├── tsconfig.json          # ✅ Configuration TypeScript
│   ├── vite.config.ts         # ✅ Configuration Vite (proxy API)
│   └── tailwind.config.js     # ✅ Configuration Tailwind
│
├── attached_assets/           # Documents de référence
│
├── .env.example               # ✅ Template variables d'environnement
├── .gitignore                 # ✅ Configuration Git
└── README.md                  # ✅ Ce fichier
```

## Notes Importantes

- La base de données PostgreSQL est la **source de vérité**
- Le code Mermaid est un **artefact généré** à partir des tables
- Les métadonnées visuelles sont stockées en JSON dans `SubProject.visual_layout`
- Synchronisation stricte requise entre schémas Pydantic (Python) et interfaces TypeScript

## Références

- **DDA V1.0**: `DDA_mermaid_V1.0.md` (Nom à modifier)
- Documentation Mermaid: https://mermaid.js.org/
- Documentation Flask: https://flask.palletsprojects.com/
- Documentation React: https://react.dev/