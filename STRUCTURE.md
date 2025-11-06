// STRUCTURE.md.txt
// Version 1.1 (Mise à jour post-Routage & Fetch)

# Structure du Projet - Éditeur Visuel Mermaid

## Arborescence Complète

```
/
├── backend/                    # Backend Python/Flask
│   ├── app/                    # Modules applicatifs Python
│   │   ├── models.py          # ✅ Modèles SQLAlchemy (Project, SubProject, Node, Relationship, ClassDef)
│   │   ├── __init__.py        # ✅ Package marker + Factory Pattern
│   │   ├── schemas.py         # ✅ Schémas Pydantic pour API
│   │   ├── routes/            # ✅ Routes API RESTful complètes (CRUD + Mermaid)
│   │   └── services/          # ✅ Services métier critiques (CRUD + Mermaid Transform)
│   ├── migrations/            # ✅ Flask-Migrate
│   ├── run.py                 # ✅ Point d'entrée Flask
│   └── requirements.txt       # ✅ Dépendances Python installées
│
├── frontend/
│   ├── src/
│   │   ├── components/        # [À DÉVELOPPER] Composants React interactifs
│   │   │   ├── ProjectCard.tsx    # [TODO] Carte pour un projet unique
│   │   │   ├── ProjectForm.tsx    # [TODO] Formulaire de création/édition de projet
│   │   │   ├── SubProjectCard.tsx # [TODO] Carte pour un sous-projet
│   │   │   ├── SubProjectForm.tsx # [TODO] Formulaire de création/édition de sous-projet
│   │   │   ├── MermaidViewer.tsx  # [TODO] Rendu du graphe Mermaid
│   │   │   └── ConfirmDialog.tsx  # [TODO] Dialogue de confirmation
│   │   ├── pages/             # ✅ Pages principales de l'application
│   │   │   ├── ProjectListPage.tsx  # ✅ Liste des projets (Routage et Fetch API implémentés)
│   │   │   └── GraphEditorPage.tsx  # ✅ Page Éditeur de Graphe (Routage fonctionnel)
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
│   ├── backendappmodels.py_1762371637524.txt
│   └── DDA_mermaid_1762371637525.md
│
├── .env.example               # ✅ Template variables d'environnement
├── .gitignore                 # ✅ Configuration Git
├── README.md                  # ✅ Documentation principale
└── STRUCTURE.md               # ✅ Ce fichier (Mis à jour)
```

## Statut de Configuration

### ✅ Complété (Backend & Infrastructure Frontend)
- [x] Backend API RESTful (CRUD + Transformation Mermaid)
- [x] Modèles SQLAlchemy et DB initialisée
- [x] Types TypeScript API synchronisés
- [x] Client API (Axios Wrapper)
- [x] **Routage React fonctionnel (`App.tsx`)**
- [x] **Chargement initial des projets (`ProjectListPage.tsx`)**

### 🔨 À Développer (Composants UI React)
Le développement se concentre maintenant sur la couche UI pour interagir avec les données récupérées :

1.  **Composants de Gestion de Projet** : `ProjectCard.tsx`, `ProjectForm.tsx`.
2.  **Composants d'Édition** : `MermaidViewer.tsx`, `MermaidEditor.tsx` (pour la Phase 2).

## Commandes Utiles

```bash
# Démarrer le backend (Port 5001)
cd backend && python run.py

# Démarrer le frontend (Port 5000)
cd frontend && npm run dev
```

## Prochaines Étapes

Poursuite du développement selon le `PLAN_DEVELOPPEMENT_FRONTEND.md`, en commençant par les composants de la `ProjectListPage`.