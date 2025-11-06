# Structure du Projet - Éditeur Visuel Mermaid

## Arborescence Complète

```
/
├── backend/                    # Backend Python/Flask
│   ├── app/                    # Modules applicatifs Python
│   │   ├── models.py          # ✅ Modèles SQLAlchemy (Project, SubProject, Node, Relationship, ClassDef)
│   │   ├── __init__.py        # ✅ Package marker + Factory Pattern
│   │   ├── schemas.py         # ✅ Schémas Pydantic pour API
│   │   ├── routes/            # ✅ Routes API RESTful complètes
│   │   │   ├── projects.py    # ✅ Routes pour Projects
│   │   │   ├── subprojects.py # ✅ Routes pour SubProjects
│   │   │   ├── nodes.py       # ✅ Routes pour Nodes et Relationships
│   │   │   └── mermaid.py     # ✅ Routes pour Import/Export Mermaid
│   │   └── services/          # ✅ Services métier critiques
│   │       ├── mermaid_parser.py    # ✅ Service Import: Mermaid → DB
│   │       └── mermaid_generator.py # ✅ Service Export: DB → Mermaid
│   ├── migrations/            # ✅ Migrations Flask-Migrate
│   │   └── versions/          # ✅ Scripts de migration générés
│   ├── run.py                 # ✅ Point d'entrée Flask
│   ├── requirements.txt       # ✅ Dépendances Python installées
│   └── .flaskenv             # ✅ Configuration Flask
│
├── frontend/
│   ├── src/
│   │   ├── components/        # [À DÉVELOPPER] Composants React
│   │   │   ├── MermaidViewer.tsx    # [TODO] Affichage graphe Mermaid
│   │   │   ├── NodeEditor.tsx       # [TODO] Éditeur de nœuds
│   │   │   └── GraphEditor.tsx      # [TODO] Éditeur principal
│   │   ├── types/             # ✅ Interfaces TypeScript pour API
│   │   │   └── api.ts         # ✅ Types synchronisés avec Pydantic
│   │   ├── services/          # [À DÉVELOPPER] Services frontend
│   │   │   └── api.ts         # [TODO] Client API (axios)
│   │   ├── App.tsx            # ✅ Composant racine (minimal)
│   │   ├── main.tsx           # ✅ Point d'entrée React
│   │   ├── index.css          # ✅ Styles Tailwind
│   │   └── vite-env.d.ts      # ✅ Types Vite
│   ├── index.html             # ✅ Template HTML
│   ├── package.json           # ✅ Dépendances Node.js installées
│   ├── tsconfig.json          # ✅ Configuration TypeScript
│   ├── tsconfig.node.json     # ✅ Config TypeScript pour Vite
│   ├── vite.config.ts         # ✅ Configuration Vite (proxy API)
│   ├── tailwind.config.js     # ✅ Configuration Tailwind
│   └── postcss.config.js      # ✅ Configuration PostCSS
│
├── attached_assets/           # Documents de référence
│   ├── backendappmodels.py_1762371637524.txt  # Modèle SQLModel complet
│   └── DDA_mermaid_1762371637525.md           # Document d'Architecture
│
├── .env.example               # ✅ Template variables d'environnement
├── .gitignore                 # ✅ Configuration Git
├── README.md                  # ✅ Documentation principale
└── STRUCTURE.md               # ✅ Ce fichier
```

## Statut de Configuration

### ✅ Complété
- [x] Python 3.11 et Node.js 20 installés
- [x] PostgreSQL créé avec variables d'environnement
- [x] **Backend : Toutes les dépendances Python installées**
- [x] **Frontend : Toutes les dépendances Node.js installées**
- [x] Arborescence du projet créée
- [x] Fichiers de configuration créés
- [x] Points d'entrée créés (run.py, main.tsx)
- [x] **Modèles SQLAlchemy créés** (backend/app/models.py)
- [x] **Flask-Migrate initialisé et migration initiale appliquée**
- [x] **Toutes les tables créées** (project, subproject, node, relationship, classdef)
- [x] **API RESTful Backend Complète** (CRUD pour toutes les ressources)
- [x] **Services de transformation Mermaid opérationnels**
- [x] **Schémas Pydantic backend** implémentés
- [x] **Types TypeScript frontend** pour les API (`frontend/src/types/api.ts`)

### 🔨 À Développer

#### Backend (Python/Flask)
Tous les points critiques sont achevés. Les efforts se concentrent maintenant sur le frontend.

#### Frontend (React/TypeScript)
1.  **Client API dédié** (`frontend/src/services/api.ts`)
    *   Wrapper Axios pour centraliser les appels backend.
    *   Gestion des erreurs et réponses typées.
2.  **Composants React**
    *   `MermaidViewer.tsx` : Rendu graphe avec Mermaid.js.
    *   `NodeEditor.tsx` : Formulaire d'édition de nœud.
    *   `GraphEditor.tsx` : Interface principale d'édition.
    *   `ProjectList.tsx` : Liste des projets/sous-projets.
3.  **Router et Navigation**
    *   Configuration React Router pour la navigation entre les vues.
    *   Gestion de l'état global pour la synchronisation UI ↔ Backend.

## Commandes Utiles

### Développement
```bash
# Backend
cd backend && python run.py

# Frontend (déjà actif via workflow)
cd frontend && npm run dev
```

### Tests de connectivité
```bash
# Tester le backend
curl http://localhost:5001/api/health

# Vérifier PostgreSQL
echo $DATABASE_URL
```

## Prochaines Étapes

1. Implémenter les modèles SQLModel dans `backend/app/models.py`
2. Créer la configuration DB et les migrations
3. Développer les services de transformation Mermaid
4. Créer les routes API
5. Implémenter les composants React avec Mermaid.js
6. Synchroniser les types TypeScript avec Pydantic

## Références Techniques

- **Modèle de données complet** : `attached_assets/backendappmodels.py_1762371637524.txt`
- **Architecture détaillée** : `attached_assets/DDA_mermaid_1762371637525.md`
- SQLModel: https://sqlmodel.tiangolo.com/
- Pydantic: https://docs.pydantic.dev/
- Mermaid.js: https://mermaid.js.org/
