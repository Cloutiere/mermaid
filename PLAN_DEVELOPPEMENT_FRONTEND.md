// frontend/PLAN_DEVELOPPEMENT_FORNTEND.md.txt
// frontend/PLAN_DEVELOPPEMENT_FRONTEND.md
// Version 1.4 (Mise à jour post-CRUD SubProject UI)

# Plan Détaillé de Développement Frontend
## Éditeur Visuel de Structure de Récit Mermaid

---

## 📁 Structure des Fichiers à Créer/Modifier

```
frontend/src/
├── components/           (MIS À JOUR)
│   ├── ProjectCard.tsx        # ✅ Implémenté (CRUD Projet)
│   ├── ProjectForm.tsx        # ✅ Implémenté (CRUD Projet)
│   ├── SubProjectCard.tsx     # ✅ Implémenté (UI SubProject)
│   ├── SubProjectForm.tsx     # ✅ Implémenté (UI SubProject)
│   ├── MermaidViewer.tsx      # [TODO] Rendu du graphe Mermaid
│   ├── MermaidEditor.tsx      # [TODO] Éditeur de code Mermaid
│   └── ConfirmDialog.tsx      # [TODO] Dialogue de confirmation
├── pages/
│   ├── ProjectListPage.tsx    (MIS À JOUR) # ✅ CRUD Projet/SubProject UI implémenté
│   └── GraphEditorPage.tsx    (À VENIR)    # Page principale pour l'édition du graphe
├── services/
│   └── api.ts                  (EXISTE DÉJÀ)
└── types/
    └── api.ts                  (EXISTE DÉJÀ)
```

---

## 🎯 Phase 1 : ProjectListPage - Interface de Gestion des Projets et Sous-Projets (ACHEVÉE)

### Fonctionnalités Implémentées (Phase 1.1 à 1.6)

#### 1.1 - 1.4 : CRUD Projet UI
**Statut de 1.1 - 1.4 : ✅ TERMINÉ**

#### 1.5 - Composant SubProjectCard
**Statut de 1.5 : ✅ TERMINÉ** (Créé et intégré dans `ProjectCard.tsx`)

#### 1.6 - Composant SubProjectForm
**Statut de 1.6 : ✅ TERMINÉ** (Créé et intégré dans `ProjectCard.tsx`)

---

## 🎨 Phase 2 : GraphEditorPage - Éditeur de Graphe Mermaid

### Objectif
Construire l'interface et la logique pour éditer, visualiser, importer et exporter le contenu d'un `SubProject`.

### Fonctionnalités à Implémenter (Dépend de la Phase 1.5 et 1.6)

#### 2.1 - Chargement du SubProject
```typescript
// Dans GraphEditorPage.tsx

// États nécessaires :
// - subproject: SubProjectRead | null
// - mermaidCode: string
// - loading: boolean
// - saving: boolean
// - error: string | null

// Au montage (useEffect) :
// 1. Récupérer projectId et subprojectId des paramètres d'URL.
// 2. Appeler apiService.getSubProject(Number(subprojectId)) pour charger l'entité complète.
// 3. Initialiser mermaidCode avec subproject.mermaid_definition.
// 4. Gérer le cas où le SubProject n'existe pas (404).
```
**Statut de 2.1 : 🔨 À FAIRE**

#### 2.2 - Visualisation Mermaid
```typescript
// À créer : components/MermaidViewer.tsx

// Implémentation :
// - Initialiser Mermaid dans useEffect.
// - Afficher le diagramme basé sur le code via `mermaid.initialize` et `mermaid.render`.
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

// Utiliser un textarea simple pour commencer.
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
// - Appelle apiService.updateSubProject(subprojectId, { mermaid_definition: mermaidCode, ... })
// - Gère l'état 'saving' et affiche un message de succès.
// NOTE: Le backend doit supporter la mise à jour des champs principaux du SubProject (titre, layout, definition).
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
// Modale de confirmation réutilisable.
```
**Statut de 3.1 : 🔨 À FAIRE**

---

## 📚 Documentation de Référence

- **DDA** : `attached_assets/DDA_mermaid_1762371637525.md`
- **Configuration** : `CONFIGURATION_COMPLETE.md`

---

## 🧪 Tests Manuels à Effectuer (Prioritaires suite à cette mise à jour)

1. [x] **Test CRUD Projet** : Créer, vérifier l'apparition, supprimer.
2. [x] **Test CRUD SubProject UI** : Créer un sous-projet via `SubProjectForm` dans `ProjectCard`, vérifier la mise à jour du compteur et de la liste. Supprimer un sous-projet, vérifier la mise à jour.
3. [ ] **Navigation** : Vérifier que le clic sur un sous-projet mène à `GraphEditorPage`.
4. [ ] **Test Éditeur de Graphe** : (À venir) Modifier le code Mermaid et sauvegarder.