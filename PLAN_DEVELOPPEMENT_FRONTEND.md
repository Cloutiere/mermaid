// frontend/PLAN_DEVELOPPEMENT_FORNTEND.md.txt
// frontend/PLAN_DEVELOPPEMENT_FRONTEND.md
// Version 1.6 (Mise à jour post-Implémentation et Correction de l'Éditeur)

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
│   ├── MermaidViewer.tsx      # ✅ TERMINÉ (Rendu du graphe Mermaid, Correction Asynchrone Appliquée)
│   ├── MermaidEditor.tsx      # ✅ TERMINÉ (Éditeur de code Mermaid)
│   └── ConfirmDialog.tsx      # [TODO] Dialogue de confirmation
├── pages/
│   ├── ProjectListPage.tsx    (MIS À JOUR) # ✅ CRUD Projet/SubProject UI implémenté
│   └── GraphEditorPage.tsx    (MIS À JOUR) # ✅ Logique de chargement, Layout, et Détection 'isDirty' implémentés
├── services/
│   └── api.ts                  (EXISTE DÉJÀ)
└── types/
    └── api.ts                  (EXISTE DÉJÀ)
```

---

## 🎯 Phase 1 : ProjectListPage - Interface de Gestion des Projets et Sous-Projets (ACHEVÉE)

### Fonctionnalités Implémentées (Phase 1.1 à 1.6)
**Statut : ✅ TERMINÉ**

---

## 🎨 Phase 2 : GraphEditorPage - Éditeur de Graphe Mermaid

### Objectif
Construire l'interface et la logique pour éditer, visualiser, importer et exporter le contenu d'un `SubProject`.

### Fonctionnalités Implémentées / à Implémenter

#### 2.1 - Chargement du SubProject dans GraphEditorPage
**Statut de 2.1 : ✅ TERMINÉ**

#### 2.2 - Visualisation Mermaid
```typescript
// À créer : components/MermaidViewer.tsx
// Statut : ✅ TERMINÉ (Incluant la correction pour le rendu asynchrone)
```
**Statut de 2.2 : ✅ TERMINÉ**

#### 2.3 - Éditeur de Code Mermaid
```typescript
// À créer : components/MermaidEditor.tsx
// Statut : ✅ TERMINÉ
```
**Statut de 2.3 : ✅ TERMINÉ**

#### 2.4 - Layout de l'Éditeur
```typescript
// Structure de GraphEditorPage :
// Disposition en deux colonnes : Éditeur (Gauche) et Aperçu (Droite)
// Boutons : Sauvegarder (avec logique isDirty), Exporter, Importer, Retour
```
**Statut de 2.4 : ✅ TERMINÉ (Logique isDirty et Layout en place)**

#### 2.5 - Sauvegarde (API Update)
```typescript
// Fonction handleSave dans GraphEditorPage :
// - Appelle apiService.updateSubProject(...) pour sauvegarder currentMermaidCode
```
**Statut de 2.5 : 🔨 À FAIRE**

#### 2.6 - Export Mermaid
```typescript
// Fonction handleExport :
// - Appelle l'endpoint backend /api/mermaid/export/{subprojectId}
// - Déclenche le téléchargement du fichier .mmd.
```
**Statut de 2.6 : 🔨 À FAIRE**

#### 2.7 - Import Mermaid
```typescript
// Fonction handleImport :
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
3. [x] **Test Navigation** : Vérifier que le clic sur un sous-projet mène à `GraphEditorPage` et que le chargement fonctionne (Phase 2.1).
4. [x] **Test Éditeur de Graphe** : Modifier le code Mermaid et vérifier le rendu visuel.
5. [ ] **Test Sauvegarde** : (À venir) Modifier le code Mermaid, déclencher la sauvegarde via l'API.