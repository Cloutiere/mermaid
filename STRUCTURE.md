# Structure du Projet - Éditeur Visuel Mermaid

## Arborescence Complète

```
/
├── backend/
│   ├── app/                    # [À DÉVELOPPER] Modules applicatifs Python
│   │   ├── models.py          # [TODO] Modèles SQLAlchemy (voir attached_assets/)
│   │   ├── schemas.py         # [TODO] Schémas Pydantic pour API
│   │   ├── routes/            # [TODO] Endpoints API RESTful
│   │   │   ├── projects.py    # Routes pour Projects
│   │   │   ├── subprojects.py # Routes pour SubProjects
│   │   │   └── nodes.py       # Routes pour Nodes
│   │   ├── services/          # [TODO] Services métier critiques
│   │   │   ├── mermaid_parser.py    # Service Import: Mermaid → DB
│   │   │   └── mermaid_generator.py # Service Export: DB → Mermaid
│   │   └── database.py        # [TODO] Configuration SQLAlchemy
│   ├── app.py                 # ✅ Point d'entrée Flask (minimal)
│   ├── requirements.txt       # ✅ Dépendances Python installées
│   └── .flaskenv             # ✅ Configuration Flask
│
├── frontend/
│   ├── src/
│   │   ├── components/        # [À DÉVELOPPER] Composants React
│   │   │   ├── MermaidViewer.tsx    # [TODO] Affichage graphe Mermaid
│   │   │   ├── NodeEditor.tsx       # [TODO] Éditeur de nœuds
│   │   │   └── GraphEditor.tsx      # [TODO] Éditeur principal
│   │   ├── types/             # [À DÉVELOPPER] Interfaces TypeScript
│   │   │   └── api.ts         # [TODO] Types synchronisés avec Pydantic
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
│   ├── vite.config.ts         # ✅ Configuration Vite
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
- [x] Installation Python 3.11
- [x] Installation Node.js 20
- [x] Base de données PostgreSQL créée
- [x] Dépendances Python installées
- [x] Dépendances Node.js installées
- [x] Fichiers de configuration créés
- [x] Arborescence de base créée
- [x] Points d'entrée minimaux (app.py, main.tsx)

### 🔨 À Développer

#### Backend (Python/Flask)
1. **Modèles de données** (`backend/app/models.py`)
   - Implémenter les classes SQLModel fournies dans `attached_assets/`
   - Project, SubProject, Node, Relationship, ClassDef

2. **Configuration base de données** (`backend/app/database.py`)
   - Connexion PostgreSQL via DATABASE_URL
   - Session SQLAlchemy
   - Initialisation des tables

3. **Schémas Pydantic** (`backend/app/schemas.py`)
   - Schémas de validation pour chaque modèle
   - DTOs pour les requêtes/réponses API

4. **Routes API** (`backend/app/routes/`)
   - CRUD pour Projects
   - CRUD pour SubProjects
   - CRUD pour Nodes et Relationships
   - Endpoints pour Import/Export Mermaid

5. **Services critiques** (`backend/app/services/`)
   - **Parser Mermaid** : Analyse du code Mermaid → Création entités DB
   - **Générateur Mermaid** : Lecture DB → Génération code Mermaid

#### Frontend (React/TypeScript)
1. **Types TypeScript** (`frontend/src/types/api.ts`)
   - Interfaces synchronisées avec schémas Pydantic
   - Types pour Project, SubProject, Node, Relationship

2. **Client API** (`frontend/src/services/api.ts`)
   - Wrapper Axios pour appels backend
   - Gestion des erreurs

3. **Composants React**
   - `MermaidViewer.tsx` : Rendu graphe avec Mermaid.js
   - `NodeEditor.tsx` : Formulaire édition nœud
   - `GraphEditor.tsx` : Interface principale
   - `ProjectList.tsx` : Liste des projets/sous-projets

4. **Router et Navigation**
   - Configuration React Router
   - Navigation entre projets/sous-projets

## Commandes Utiles

### Développement
```bash
# Backend
cd backend && python app.py

# Frontend
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
