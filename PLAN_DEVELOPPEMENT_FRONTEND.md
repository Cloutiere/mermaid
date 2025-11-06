// PLAN_DEVELOPPEMENT_FRONTEND.md.txt
// Version 1.1 (Mise à jour post-Routage & Fetch initial)

# Plan Détaillé de Développement Frontend
## Éditeur Visuel de Structure de Récit Mermaid

---

## 📁 Structure des Fichiers à Créer/Modifier

```
frontend/src/
├── components/           (À CRÉER)
│   ├── ProjectCard.tsx        # [TODO] Carte pour un projet (Affichage/Actions)
│   ├── ProjectForm.tsx        # [TODO] Formulaire de création de projet
│   ├── SubProjectCard.tsx     # [TODO] Carte pour un sous-projet
│   ├── SubProjectForm.tsx     # [TODO] Formulaire de création de sous-projet
│   ├── MermaidViewer.tsx      # [TODO] Rendu du graphe Mermaid
│   ├── MermaidEditor.tsx      # [TODO] Éditeur de code Mermaid
│   └── ConfirmDialog.tsx      # [TODO] Dialogue de confirmation
├── pages/
│   ├── ProjectListPage.tsx    (MIS À JOUR) # ✅ Logique de Fetch/Loading implémentée
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

### Fonctionnalités à Implémenter

#### 1.1 - Affichage de la Liste des Projets (Fetch & États)
```typescript
// Dans ProjectListPage.tsx

// États nécessaires :
// - projects: ProjectRead[]           // Liste des projets (Initialisation à [])
// - loading: boolean                  // État de chargement (Initialisation à true)
// - error: string | null              // Gestion des erreurs (Initialisation à null)
// - showCreateForm: boolean           // Afficher/masquer le formulaire (Initialisation à false)

// Au montage du composant (useEffect) :
// 1. Appeler apiService.getProjects() ✅ FAIT
// 2. Stocker les résultats dans l'état projects ✅ FAIT
// 3. Gérer le loading et les erreurs ✅ FAIT

// Affichage :
// - Utiliser une grille (grid) pour afficher les projets
// - Pour chaque projet, utiliser le composant ProjectCard ✅ PROCHAINE ÉTAPE
// - Si aucun projet : afficher un message d'invitation à créer ✅ PROCHAINE ÉTAPE
```
**Statut de 1.1 : ✅ TERMINÉ (Mécanisme de fetch et gestion d'état en place)**

#### 1.2 - Bouton "Créer un Nouveau Projet"
```typescript
// Fonctionnalité :
// - Bouton visible en haut de page
// - Au clic : met à jour l'état showCreateForm à true, ouvrant le formulaire (ProjectForm)
```
**Statut de 1.2 : 🔨 À FAIRE**

#### 1.3 - Composant ProjectCard
```typescript
// À créer : components/ProjectCard.tsx

interface ProjectCardProps {
  project: ProjectRead
  onDelete: (id: number) => void // Nécessite l'implémentation de la suppression
  onRefresh: () => void         // Nécessaire pour rafraîchir la liste après une action
}

// Affichage :
// - Titre du projet
// - Nombre de sous-projets (doit être calculé ou récupéré)
// - Liste des sous-projets (via SubProjectCard)
// - Bouton "Ajouter un Sous-Projet"
// - Bouton "Supprimer le Projet" (avec confirmation via ConfirmDialog)

// Actions :
// - Cliquer sur un sous-projet → navigue vers GraphEditorPage
// - Supprimer un projet → appelle apiService.deleteProject(id)
// - Ajouter un sous-projet → ouvre SubProjectForm
```
**Statut de 1.3 : 🔨 À FAIRE**

#### 1.4 - Composant ProjectForm
```typescript
// À créer : components/ProjectForm.tsx

interface ProjectFormProps {
  onSuccess: () => void // Fonction de rappel pour rafraîchir la liste après succès
  onCancel: () => void
}

// Champs du formulaire :
// - title: string (obligatoire)

// Actions :
// - Soumettre → appelle apiService.createProject({ title })
// - Annuler → ferme le formulaire
// - Gérer la validation (titre non vide)
```
**Statut de 1.4 : 🔨 À FAIRE**

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
Créer un éditeur complet pour visualiser et modifier les graphes Mermaid.

### Fonctionnalités à Implémenter

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

// Installation requise :
// npm install mermaid

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
// Modale de confirmation réutilisable (utilisée pour la suppression de projets).
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
npm install @monaco-editor/react  # Optionnel, pour éditeur enrichi
```

---

## 🔄 Flux de Données (Rappel)

### Création d'un Projet
1. Utilisateur clique "Créer un Projet"
2. Formulaire s'ouvre (ProjectForm)
3. Soumission → `apiService.createProject({ title })`
4. Rafraîchir la liste des projets dans `ProjectListPage`

### Édition d'un Graphe
1. Clic sur SubProjectCard
2. Navigation vers `/project/:projectId/subproject/:subprojectId`
3. GraphEditorPage charge le subproject
4. Modifications → bouton Sauvegarder
5. Sauvegarde → `apiService.updateSubProject(...)`

---

## 🧪 Tests Manuels à Effectuer (Prioritaires)

1. [ ] **Test CRUD Projet** : Créer un projet via `ProjectForm`, vérifier son apparition dans `ProjectListPage`, puis le supprimer.
2. [ ] **Navigation** : Vérifier que le clic sur un projet (futur `ProjectCard`) mène à `GraphEditorPage`.
3. [ ] **API Health Check** : Vérifier que le statut reste vert/atteignable.

---

## 💡 Conseils de Développement

### Ordre Recommandé d'Implémentation (Suite)

1.  **Composants de Gestion de Projet** : `ProjectCard.tsx` et `ProjectForm.tsx`.
2.  Intégration dans `ProjectListPage.tsx` (Affichage des données récupérées + boutons CRUD).
3.  Développement de la Phase 2 (Éditeur de Graphe).

### Gestion des Erreurs
Continuer d'utiliser `try/catch` autour des appels API pour mettre à jour l'état `error` dans les pages concernées.

---

**Prochaine Phase :** Développement des composants d'interaction pour la `ProjectListPage`.