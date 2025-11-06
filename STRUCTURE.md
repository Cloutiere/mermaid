// frontend/STRUCTURE.md
// frontend/STRUCTURE.md
// Version 1.4 (Mise à jour post-Chargement GraphEditorPage)

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
│   │   │   ├── MermaidViewer.tsx  # [TODO] Rendu du graphe Mermaid
│   │   │   ├── MermaidEditor.tsx  # [TODO] Éditeur de code Mermaid
│   │   │   └── ConfirmDialog.tsx  # [TODO] Dialogue de confirmation
│   │   ├── pages/             # ✅ Pages principales de l'application
│   │   │   ├── ProjectListPage.tsx  # ✅ Liste des projets (CRUD Projet UI fonctionnel)
│   │   │   └── GraphEditorPage.tsx  # ✅ Page Éditeur de Graphe (Logique de chargement des données fonctionnelle)
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
```

## Statut de Configuration

### ✅ Complété (Backend & Infrastructure Frontend)
- [x] Backend API RESTful (CRUD + Transformation Mermaid)
- [x] Modèles SQLAlchemy (Complet)
- [x] **Routage React fonctionnel (`App.tsx`)**
- [x] **Chargement Initial des Projets** (`ProjectListPage.tsx`)
- [x] **Composants CRUD Projet UI** (`ProjectForm`, `ProjectCard`)
- [x] **Composants de Gestion de Sous-Projets UI** (`SubProjectCard`, `SubProjectForm`)
- [x] **Page Éditeur de Graphe** (`GraphEditorPage.tsx`) - Logique de chargement des données active.

### 🔨 À Développer (Composants UI React)
Le développement se concentre maintenant sur l'éditeur de graphe :

1.  **Composants d'Édition de Graphe** : `MermaidViewer.tsx`, `MermaidEditor.tsx`.
2.  **Composants Utilitaires** : `ConfirmDialog.tsx`.
3.  **Page d'Édition** : `GraphEditorPage.tsx` (Logique de sauvegarde, export/import).

## Commandes Utiles

```bash
# Démarrer le backend (Port 5001)
cd backend
python run.py

# Démarrer le frontend (Port 5000)
cd frontend
npm run dev
# NOTE: Assurez-vous que 'lucide-react' est installé (npm install lucide-react)
```

## Prochaines Étapes

Poursuite du développement selon le plan, en attaquant la `GraphEditorPage.tsx` (Phase 2.2).

---

## 📚 Documentation de Référence

- **DDA** : `attached_assets/DDA_mermaid_1762371637525.md` (Stable)
- **Plans de développement** : `PLAN_DEVELOPPEMENT_FRONTEND.md`
```

### 4. `DDA_mermaid.md` et `CONFIGURATION_COMPLETE.md`

Ces deux documents décrivent l'architecture fondamentale (DDA) et l'état de la configuration/BD (Configuration), qui n'ont pas été remises en question par l'implémentation frontend de la Phase 2.1. **Ils restent inchangés.**

---

## 5. Contenu Récent de `GraphEditorPage.tsx` (Pour Référence)

```typescript
// frontend/src/pages/GraphEditorPage.tsx
import { useParams, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import apiService from '@/services/api' // Assurez-vous que cet alias est configuré
import { SubProjectRead } from '@/types/api' // Assurez-vous que cet alias est configuré

function GraphEditorPage() {
  // Définition des types attendus pour les paramètres d'URL
  interface EditorParams {
    projectId: string
    subprojectId: string
  }

  // Utilisation de useParams avec le typage défini
  const { projectId, subprojectId } = useParams<keyof EditorParams>() as EditorParams
  const navigate = useNavigate()

  // --- 1. Gestion des États ---
  const [subproject, setSubProject] = useState<SubProjectRead | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Convertir l'ID pour l'API
  const subprojectIdNumber = subprojectId ? Number(subprojectId) : null

  // --- 2. Fonction de Chargement Asynchrone ---
  useEffect(() => {
    if (!subprojectIdNumber || isNaN(subprojectIdNumber)) {
      setError("Erreur de routage: ID du sous-projet invalide ou manquant.")
      setLoading(false)
      return
    }

    const fetchSubProject = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await apiService.getSubProject(subprojectIdNumber)
        setSubProject(data)
      } catch (err) {
        console.error('Échec du chargement du sous-projet:', err)
        // Utilise le message d'erreur formaté par apiService.handleError
        setError(err instanceof Error ? err.message : 'Une erreur inconnue est survenue lors du chargement.')
      } finally {
        setLoading(false)
      }
    }

    fetchSubProject()
  }, [subprojectIdNumber]) // Déclenchement au changement de subprojectId

  // --- 3. Rendu Conditionnel (Chargement et Erreur) ---

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8 flex justify-center items-center">
        <p className="text-xl font-semibold text-indigo-600">Chargement du Graphe...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <header className="mb-8">
          <h1 className="text-4xl font-extrabold text-red-700">Erreur de Chargement</h1>
        </header>
        <div className="bg-white p-6 rounded-xl shadow-lg border border-red-100">
          <p className="text-red-700 font-medium">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
          >
            Retour à la liste des projets
          </button>
        </div>
      </div>
    )
  }

  // Si chargé avec succès
  const subProjectTitle = subproject?.title || `Sous-Projet ID: ${subprojectId}`

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <header className="mb-8">
        <h1 className="text-4xl font-extrabold text-indigo-700">
          Éditeur : {subProjectTitle}
        </h1>
        <p className="text-lg text-gray-500">
          ID Projet: {projectId} | ID Sous-Projet: {subprojectId}
        </p>
      </header>

      <div className="bg-white p-6 rounded-xl shadow-lg border border-indigo-100">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
          Contenu du Sous-Projet (Mermaid Definition)
        </h2>
        <pre className="whitespace-pre-wrap bg-gray-100 p-3 rounded text-sm">
            {subproject?.mermaid_definition || "// Définition Mermaid non disponible"}
        </pre>
      </div>

      <div className="mt-8 p-4 bg-yellow-50 border-l-4 border-yellow-500">
        <p className="text-sm text-yellow-700">
          Placeholder : Les composants MermaidViewer et MermaidEditor seront implémentés ici.
        </p>
      </div>
    </div>
  )
}

export default GraphEditorPage