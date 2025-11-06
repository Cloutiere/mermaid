// PLAN_DEVELOPPEMENT_FRONTEND.md
// Version 2.0 (Finalisation des Utilitaires)

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
│   ├── MermaidViewer.tsx      # ✅ TERMINÉ
│   ├── MermaidEditor.tsx      # ✅ TERMINÉ
│   └── ConfirmDialog.tsx      # ✅ TERMINÉ (Dialogue de confirmation implémenté et intégré)
├── pages/
│   ├── ProjectListPage.tsx    (MIS À JOUR) # ✅ CRUD Projet/SubProject UI implémenté
│   └── GraphEditorPage.tsx    (MIS À JOUR) # ✅ Toutes les fonctionnalités UI sont implémentées
├── services/
│   └── api.ts                  (EXISTE DÉJÀ)
└── types/
    └── api.ts                  (EXISTE DÉJÀ)
```

---

## 🎯 Phase 1 : ProjectListPage - Interface de Gestion des Projets et Sous-Projets (ACHEVÉE)

**Statut : ✅ TERMINÉ**

---

## 🎨 Phase 2 : GraphEditorPage - Éditeur de Graphe Mermaid (ACHEVÉE)

**Statut : ✅ TERMINÉ**

---

## 🔧 Phase 3 : Composants Utilitaires

### 3.1 - ConfirmDialog
```typescript
// À créer : components/ConfirmDialog.tsx
// Modale de confirmation réutilisable.
```
**Statut de 3.1 : ✅ TERMINÉ**

---

## 📚 Documentation de Référence

- **DDA** : `attached_assets/DDA_mermaid_1762371637525.md`
- **Configuration** : `CONFIGURATION_COMPLETE.md`

---

## 🧪 Tests Manuels à Effectuer (Finalisation du Frontend)

1. [x] **Test CRUD Projet** : Créer, vérifier l'apparition, **utiliser `ConfirmDialog` pour la suppression**.
2. [x] **Test CRUD SubProject UI** : Créer un sous-projet. **Utiliser `ConfirmDialog` pour la suppression**.
3. [x] **Test Navigation** : Vérifier que le clic sur un sous-projet mène à `GraphEditorPage`.
4. [x] **Test Éditeur de Graphe** : Modifier le code Mermaid et vérifier le rendu visuel.
5. [x] **Test Sauvegarde/Export/Import** : Vérifier toutes les fonctionnalités de l'éditeur de graphe.