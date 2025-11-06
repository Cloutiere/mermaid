// frontend/PLAN_DEVELOPPEMENT_FRONTEND.md.txt
// Version 1.3 (Mise à jour post-CRUD Projet UI & Next Steps)

# Plan Détaillé de Développement Frontend
## Éditeur Visuel de Structure de Récit Mermaid

---

## 📁 Structure des Fichiers à Créer/Modifier

```
frontend/src/
├── components/           (MIS À JOUR)
│   ├── ProjectCard.tsx        # ✅ Implémenté (CRUD Projet)
│   ├── ProjectForm.tsx        # ✅ Implémenté (CRUD Projet)
│   ├── SubProjectCard.tsx     # [TODO] Carte pour un sous-projet
│   ├── SubProjectForm.tsx     # [TODO] Formulaire de création de sous-projet
│   ├── MermaidViewer.tsx      # [TODO] Rendu du graphe Mermaid
│   ├── MermaidEditor.tsx      # [TODO] Éditeur de code Mermaid
│   └── ConfirmDialog.tsx      # [TODO] Dialogue de confirmation
├── pages/
│   ├── ProjectListPage.tsx    (MIS À JOUR) # ✅ CRUD Projet UI implémenté
│   └── GraphEditorPage.tsx    (À VENIR)    # Routage fonctionnel, chargement des données à implémenter
├── services/
│   └── api.ts                  (EXISTE DÉJÀ)
└── types/
    └── api.ts                  (EXISTE DÉJÀ)
```

---

## 🎯 Phase 1 : ProjectListPage - Interface de Gestion des Projets

### Objectif
Créer une page complète pour lister, créer et gérer tous les projets.

### Fonctionnalités Implémentées

#### 1.1 - Affichage de la Liste des Projets (Fetch & États)
**Statut de 1.1 : ✅ TERMINÉ** (Chargement initial dans `ProjectListPage.tsx`)

#### 1.2 - Bouton "Créer un Nouveau Projet"
**Statut de 1.2 : ✅ TERMINÉ** (Intégré dans `ProjectListPage.tsx`, ouvre `ProjectForm`)

#### 1.3 - Composant ProjectCard
**Statut de 1.3 : ✅ TERMINÉ** (Implémenté : affichage, navigation placeholder vers SubProject, et appel de la fonction de suppression).

#### 1.4 - Composant ProjectForm
**Statut de 1.4 : ✅ TERMINÉ** (Implémenté : soumission via `apiService.createProject`, gestion d'état et de succès/annulation).

#### 1.5 - Composant SubProjectCard
```typescript
// À créer : components/SubProjectCard.tsx

interface SubProjectCardProps {
  subproject: SubProjectRead
  projectId: number
}

// Affichage :
// - Titre du sous-projet
// - Aperçu du code Mermaid (première ligne ou icône)
// - Bouton "Ouvrir l'Éditeur"

// Actions :
// - Cliquer → navigate(`/project/${projectId}/subproject/${subproject.id}`)
```
**Statut de 1.5 : 🔨 À FAIRE**

#### 1.6 - Composant SubProjectForm
```typescript
// À créer : components/SubProjectForm.tsx

interface SubProjectFormProps {
  projectId: number
  onSuccess: () => void // Fonction de rappel pour rafraîchir la liste des sous-projets
  onCancel: () => void
}

// Champs du formulaire :
// - title: string (obligatoire)
// - mermaid_definition: string (avec un textarea ou éditeur simple)

const DEFAULT_MERMAID = `graph TD
    A[Début] --> B[Milieu]
    B --> C[Fin]`

// Actions :
// - Soumettre → appelle apiService.createSubProject({ project_id, title, mermaid_definition })
// - Annuler → ferme le formulaire
```
**Statut de 1.6 : 🔨 À FAIRE**

---

## 🎨 Phase 2 : GraphEditorPage - Éditeur de Graphe Mermaid

### Objectif
Créer un éditeur complet pour visualiser et modifier les graphes Mermaid associés à un `SubProject`.

### Fonctionnalités à Implémenter (Dépend de la Phase 1.5 et 1.6)

#### 2.1 - Chargement du SubProject
```typescript
// Dans GraphEditorPage.tsx

// États nécessaires :
// - subproject: SubProjectRead | null
// - nodes: NodeRead[]
// - relationships: RelationshipRead[]
// - mermaidCode: string
// - loading: boolean
// - saving: boolean
// - error: string | null

// Au montage (useEffect) :
// 1. Récupérer projectId et subprojectId
// 2. Appeler apiService.getSubProject(Number(subprojectId)) ✅ À FAIRE
// 3. Initialiser mermaidCode avec subproject.mermaid_definition ✅ À FAIRE
// 4. Charger les nodes et relationships (optionnel, déjà dans subproject) ✅ À FAIRE
```
**Statut de 2.1 : 🔨 À FAIRE**

#### 2.2 - Visualisation Mermaid
```typescript
// À créer : components/MermaidViewer.tsx

// Implémentation :
// - Initialiser Mermaid dans useEffect.
// - Afficher le diagramme basé sur le code.
// - Gérer les erreurs de syntaxe Mermaid.
```
**Statut de 2.2 : 🔨 À FAIRE**

#### 2.3 - Éditeur de Code Mermaid
```typescript
// À créer : components/MermaidEditor.tsx

interface MermaidEditorProps {
  initialCode: string
  onChange: (code: string) => void
}

// Utiliser un textarea simple ou Monaco Editor.
```
**Statut de 2.3 : 🔨 À FAIRE**

#### 2.4 - Layout de l'Éditeur
```typescript
// Structure de GraphEditorPage :
// Disposition en deux colonnes : Éditeur (Gauche) et Aperçu (Droite)
// Boutons : Sauvegarder, Exporter, Importer, Retour
```
**Statut de 2.4 : 🔨 À FAIRE**

#### 2.5 - Sauvegarde (API Update)
```typescript
// Fonction handleSave dans GraphEditorPage :
// - Appelle apiService.updateSubProject(subprojectId, { ..., mermaid_definition: mermaidCode })
// - Gère l'état 'saving' et affiche un message de succès.
```
**Statut de 2.5 : 🔨 À FAIRE**

#### 2.6 - Export Mermaid
```typescript
// Fonction handleExport :
// - Appelle l'endpoint backend /api/mermaid/export/{subprojectId}
// - Déclenche le téléchargement du fichier .mmd côté client.
```
**Statut de 2.6 : 🔨 À FAIRE**

#### 2.7 - Import Mermaid
```typescript
// Fonction handleImport :
// - Ouvre un sélecteur de fichier côté client.
// - Lit le contenu du fichier .mmd.
// - Met à jour l'état mermaidCode.
```
**Statut de 2.7 : 🔨 À FAIRE**

#### 2.8 - Bouton Retour
```typescript
// Ajouter un bouton pour revenir à la liste :
// Utilisation de useNavigate de react-router-dom pour naviguer vers '/'
```
**Statut de 2.8 : 🔨 À FAIRE**

---

## 🔧 Phase 3 : Composants Utilitaires

### 3.1 - ConfirmDialog
```typescript
// À créer : components/ConfirmDialog.tsx
// Modale de confirmation réutilisable (utilisée pour la suppression de projets et sous-projets).
```
**Statut de 3.1 : 🔨 À FAIRE**

---

## 🎨 Styles et UI

### Recommandations TailwindCSS
Styles basiques définis pour les cartes, boutons (principal, secondaire, danger) et la grille de projets.

---

## 📦 Dépendances à Installer

```bash
cd frontend
npm install mermaid
# Monaco Editor est optionnel, on commencera avec un textarea simple.
```

---

## 🔄 Flux de Données (Rappel)

### Création d'un Projet (✅ TERMINÉ)
1. Utilisateur clique "Créer un Projet"
2. Formulaire s'ouvre (ProjectForm)
3. Soumission → `apiService.createProject({ title })`
4. Rafraîchir la liste des projets dans `ProjectListPage`

### Création d'un Sous-Projet (À venir)
1. Utilisateur clique "Ajouter un SubProject" sur `ProjectCard`
2. Formulaire s'ouvre (SubProjectForm)
3. Soumission → `apiService.createSubProject(...)`
4. Rafraîchir la liste des subprojects dans ProjectCard/ProjectListPage.

### Édition d'un Graphe
1. Clic sur SubProjectCard
2. Navigation vers `/project/:projectId/subproject/:subprojectId`
3. GraphEditorPage charge le subproject
4. Modifications → bouton Sauvegarder
5. Sauvegarde → `apiService.updateSubProject(...)`

---

## 🧪 Tests Manuels à Effectuer (Prioritaires)

1. [x] **Test CRUD Projet** : Créer un projet via `ProjectForm`, vérifier son apparition dans `ProjectListPage`, puis le supprimer.
2. [x] **Navigation** : Vérifier que le clic sur un projet mène à `GraphEditorPage`.
3. [ ] **Test CRUD Sous-Projet** : (À venir) Créer un sous-projet.
4. [ ] **Test Éditeur de Graphe** : (À venir) Modifier le code Mermaid et sauvegarder.

---

## 💡 Conseils de Développement

### Ordre Recommandé d'Implémentation (Suite)

1. **Composants de Gestion de Sous-Projet** : `SubProjectCard.tsx` et `SubProjectForm.tsx` (pour pouvoir créer des éléments à éditer et les afficher sur ProjectListPage).
2. **Page Éditeur** : `GraphEditorPage.tsx` et ses dépendances (`MermaidViewer`, `MermaidEditor`).

### Gestion des Erreurs
Continuer d'utiliser `try/catch` autour des appels API pour mettre à jour l'état `error` dans les pages concernées.

---

**Prochaine Phase :** Développement de la gestion des Sous-Projets (`SubProjectCard` et `SubProjectForm`) pour enrichir la `ProjectListPage`.