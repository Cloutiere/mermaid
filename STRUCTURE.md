// frontend/STRUCTURE.md
// frontend/STRUCTURE.md
// Version 1.6 (Mise à jour post-Sauvegarde Éditeur)

# Structure du Projet - Éditeur Visuel Mermaid

## Arborescence Complète

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
│   │   │   └── ConfirmDialog.tsx  # [TODO] Dialogue de confirmation
│   │   ├── pages/             # ✅ Pages principales de l'application
│   │   │   ├── ProjectListPage.tsx  # ✅ Liste des projets (CRUD Projet UI fonctionnel)
│   │   │   └── GraphEditorPage.tsx  # ✅ Page Éditeur de Graphe (Logique de chargement, Layout, Édition, Visualisation, et Sauvegarde implémentés)
│   │   ├── types/             # ✅ Interfaces TypeScript pour API
│   │   │   └── api.ts         # ✅ Types synchronisés avec Pydantic
│   │   ├── services/          # ✅ Services frontend
│   │   │   └── api.ts         # ✅ Client API (axios Wrapper)
│   │   ├── App.tsx            # ✅ Composant racine (configuration du routage)
│   │   ├── main.tsx           # ✅ Point d'entrée React (avec BrowserRouter)
│   │   ├── index.css          # ✅ Styles Tailwind
│   │   └── vite-env.d.ts      # ✅ Types Vite
│   ├── index.html             # ✅ Template HTML
│   ├── package.json           # ✅ Dépendances Node.js installées (Ajout de lucide-react nécessaire)
│   ├── tsconfig.json          # ✅ Configuration TypeScript
│   ├── vite.config.ts         # ✅ Configuration Vite (proxy API)
│   └── tailwind.config.js     # ✅ Configuration Tailwind
│
├── attached_assets/           # Documents de référence
│
├── .env.example               # ✅ Template variables d'environnement
├── .gitignore                 # ✅ Configuration Git
├── README.md                  # ✅ Documentation principale
└── STRUCTURE.md               # ✅ Ce fichier (Mis à jour)