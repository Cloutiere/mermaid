# Plan Détaillé de Développement Frontend
## Éditeur Visuel de Structure Narrative Mermaid

---

## 📁 Structure des Fichiers à Créer/Modifier

```
frontend/src/
├── components/           (À CRÉER)
│   ├── ProjectCard.tsx
│   ├── ProjectForm.tsx
│   ├── SubProjectCard.tsx
│   ├── SubProjectForm.tsx
│   ├── MermaidViewer.tsx
│   ├── MermaidEditor.tsx
│   └── ConfirmDialog.tsx
├── pages/
│   ├── ProjectListPage.tsx    (À MODIFIER)
│   └── GraphEditorPage.tsx    (À MODIFIER)
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

#### 1.1 - Affichage de la Liste des Projets
```typescript
// Dans ProjectListPage.tsx

// États nécessaires :
- projects: ProjectRead[]           // Liste des projets
- loading: boolean                  // État de chargement
- error: string | null              // Gestion des erreurs
- showCreateForm: boolean           // Afficher/masquer le formulaire

// Au montage du composant (useEffect) :
1. Appeler apiService.getProjects()
2. Stocker les résultats dans l'état projects
3. Gérer le loading et les erreurs

// Affichage :
- Utiliser une grille (grid) pour afficher les projets
- Pour chaque projet, utiliser le composant ProjectCard
- Si aucun projet : afficher un message d'invitation à créer
```

#### 1.2 - Bouton "Créer un Nouveau Projet"
```typescript
// Fonctionnalité :
- Bouton visible en haut de page
- Au clic : ouvre le formulaire de création (ProjectForm)
- Le formulaire est une modale ou un panneau latéral
```

#### 1.3 - Composant ProjectCard
```typescript
// À créer : components/ProjectCard.tsx

interface ProjectCardProps {
  project: ProjectRead
  onDelete: (id: number) => void
  onRefresh: () => void
}

// Affichage :
- Titre du projet
- Nombre de sous-projets
- Liste des sous-projets (SubProjectCard pour chacun)
- Bouton "Ajouter un Sous-Projet"
- Bouton "Supprimer le Projet" (avec confirmation)

// Actions :
- Cliquer sur un sous-projet → navigue vers GraphEditorPage
- Supprimer un projet → appelle apiService.deleteProject(id)
- Ajouter un sous-projet → ouvre SubProjectForm
```

#### 1.4 - Composant ProjectForm
```typescript
// À créer : components/ProjectForm.tsx

interface ProjectFormProps {
  onSuccess: () => void
  onCancel: () => void
}

// Champs du formulaire :
- title: string (obligatoire)

// Actions :
- Soumettre → appelle apiService.createProject({ title })
- Annuler → ferme le formulaire
- Gérer la validation (titre non vide)
```

#### 1.5 - Composant SubProjectCard
```typescript
// À créer : components/SubProjectCard.tsx

interface SubProjectCardProps {
  subproject: SubProjectRead
  projectId: number
}

// Affichage :
- Titre du sous-projet
- Aperçu du code Mermaid (première ligne ou icône)
- Bouton "Ouvrir l'Éditeur"

// Actions :
- Cliquer → navigate(`/project/${projectId}/subproject/${subproject.id}`)
```

#### 1.6 - Composant SubProjectForm
```typescript
// À créer : components/SubProjectForm.tsx

interface SubProjectFormProps {
  projectId: number
  onSuccess: () => void
  onCancel: () => void
}

// Champs du formulaire :
- title: string (obligatoire)
- mermaid_definition: string (avec un textarea ou éditeur simple)

// Valeur par défaut pour mermaid_definition :
const DEFAULT_MERMAID = `graph TD
    A[Début] --> B[Milieu]
    B --> C[Fin]`

// Actions :
- Soumettre → appelle apiService.createSubProject({ project_id, title, mermaid_definition })
- Annuler → ferme le formulaire
```

---

## 🎨 Phase 2 : GraphEditorPage - Éditeur de Graphe Mermaid

### Objectif
Créer un éditeur complet pour visualiser et modifier les graphes Mermaid.

### Fonctionnalités à Implémenter

#### 2.1 - Chargement du SubProject
```typescript
// Dans GraphEditorPage.tsx

// États nécessaires :
- subproject: SubProjectRead | null
- nodes: NodeRead[]
- relationships: RelationshipRead[]
- mermaidCode: string
- loading: boolean
- saving: boolean
- error: string | null

// Au montage (useEffect) :
const { projectId, subprojectId } = useParams()

1. Appeler apiService.getSubProject(Number(subprojectId))
2. Stocker dans l'état subproject
3. Initialiser mermaidCode avec subproject.mermaid_definition
4. Charger les nodes et relationships (optionnel, déjà dans subproject)
```

#### 2.2 - Visualisation Mermaid
```typescript
// À créer : components/MermaidViewer.tsx

// Installation requise :
npm install mermaid

interface MermaidViewerProps {
  code: string
}

// Implémentation :
import mermaid from 'mermaid'

// Initialiser Mermaid dans useEffect :
mermaid.initialize({ 
  startOnLoad: true,
  theme: 'default'
})

// Afficher le diagramme :
- Utiliser un div avec un id unique
- Appeler mermaid.render() ou mermaid.contentLoaded()
- Gérer les erreurs de syntaxe Mermaid
```

#### 2.3 - Éditeur de Code Mermaid
```typescript
// À créer : components/MermaidEditor.tsx

interface MermaidEditorProps {
  initialCode: string
  onChange: (code: string) => void
}

// Option 1 - Simple textarea :
<textarea 
  value={code}
  onChange={(e) => onChange(e.target.value)}
  className="font-mono"
  rows={20}
/>

// Option 2 - Éditeur enrichi (optionnel) :
npm install @monaco-editor/react
// Utiliser Monaco Editor pour la coloration syntaxique
```

#### 2.4 - Layout de l'Éditeur
```typescript
// Structure de GraphEditorPage :

<div className="grid grid-cols-2 gap-4">
  {/* Colonne Gauche - Éditeur */}
  <div>
    <h2>Code Mermaid</h2>
    <MermaidEditor 
      initialCode={mermaidCode}
      onChange={setMermaidCode}
    />
    
    <div className="mt-4 flex gap-2">
      <button onClick={handleSave}>Sauvegarder</button>
      <button onClick={handleExport}>Exporter</button>
      <button onClick={handleImport}>Importer</button>
    </div>
  </div>
  
  {/* Colonne Droite - Aperçu */}
  <div>
    <h2>Aperçu du Graphe</h2>
    <MermaidViewer code={mermaidCode} />
  </div>
</div>
```

#### 2.5 - Sauvegarde
```typescript
// Fonction handleSave dans GraphEditorPage :

const handleSave = async () => {
  setSaving(true)
  try {
    // Mettre à jour le SubProject avec le nouveau code
    await apiService.updateSubProject(subprojectId, {
      project_id: projectId,
      title: subproject.title,
      mermaid_definition: mermaidCode
    })
    
    // Afficher un message de succès (toast ou alert)
    alert('Graphe sauvegardé avec succès!')
  } catch (err) {
    setError('Erreur lors de la sauvegarde')
  } finally {
    setSaving(false)
  }
}
```

#### 2.6 - Export Mermaid
```typescript
// Fonction handleExport :

const handleExport = async () => {
  try {
    // Appeler l'API d'export
    const response = await fetch(`/api/mermaid/export/${subprojectId}`)
    const mermaidText = await response.text()
    
    // Télécharger comme fichier
    const blob = new Blob([mermaidText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${subproject.title}.mmd`
    a.click()
  } catch (err) {
    setError('Erreur lors de l\'export')
  }
}
```

#### 2.7 - Import Mermaid
```typescript
// Fonction handleImport :

const handleImport = () => {
  // Créer un input file
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.mmd,.txt'
  
  input.onchange = async (e) => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (!file) return
    
    const text = await file.text()
    setMermaidCode(text)
  }
  
  input.click()
}
```

#### 2.8 - Bouton Retour
```typescript
// Ajouter un bouton pour revenir à la liste :

import { useNavigate } from 'react-router-dom'

const navigate = useNavigate()

<button onClick={() => navigate('/')}>
  ← Retour à la liste des projets
</button>
```

---

## 🔧 Phase 3 : Composants Utilitaires

### 3.1 - ConfirmDialog
```typescript
// À créer : components/ConfirmDialog.tsx

interface ConfirmDialogProps {
  isOpen: boolean
  title: string
  message: string
  onConfirm: () => void
  onCancel: () => void
}

// Utilisation :
- Afficher une modale de confirmation
- Boutons "Confirmer" et "Annuler"
- Utilisé avant la suppression d'un projet
```

---

## 🎨 Styles et UI

### Recommandations TailwindCSS

```typescript
// Boutons principaux :
className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"

// Boutons secondaires :
className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded"

// Boutons danger :
className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded"

// Cartes :
className="bg-white p-6 rounded-lg shadow-md border"

// Grille de projets :
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
```

---

## 📦 Dépendances à Installer

```bash
cd frontend
npm install mermaid
npm install @monaco-editor/react  # Optionnel, pour éditeur enrichi
```

---

## 🔄 Flux de Données

### Création d'un Projet
1. Utilisateur clique "Créer un Projet"
2. Formulaire s'ouvre (ProjectForm)
3. Utilisateur entre le titre
4. Soumission → `apiService.createProject({ title })`
5. Rafraîchir la liste des projets

### Création d'un Sous-Projet
1. Depuis ProjectCard, clic "Ajouter Sous-Projet"
2. Formulaire s'ouvre (SubProjectForm)
3. Utilisateur entre titre et code Mermaid initial
4. Soumission → `apiService.createSubProject({ project_id, title, mermaid_definition })`
5. Rafraîchir le projet parent

### Édition d'un Graphe
1. Clic sur SubProjectCard
2. Navigation vers `/project/:projectId/subproject/:subprojectId`
3. GraphEditorPage charge le subproject
4. Affichage éditeur + aperçu en temps réel
5. Modifications → bouton Sauvegarder
6. Sauvegarde → `apiService.updateSubProject(...)`

---

## 🧪 Tests Manuels à Effectuer

### Test 1 : CRUD Projet
- [ ] Créer un projet
- [ ] Voir le projet dans la liste
- [ ] Supprimer le projet

### Test 2 : CRUD Sous-Projet
- [ ] Créer un sous-projet
- [ ] Voir le sous-projet dans la carte du projet
- [ ] Ouvrir l'éditeur du sous-projet

### Test 3 : Édition Mermaid
- [ ] Modifier le code Mermaid
- [ ] Voir l'aperçu se mettre à jour
- [ ] Sauvegarder les modifications
- [ ] Recharger la page → vérifier que les modifications sont conservées

### Test 4 : Import/Export
- [ ] Exporter un graphe Mermaid
- [ ] Importer un fichier Mermaid
- [ ] Vérifier que le code est chargé correctement

---

## 💡 Conseils de Développement

### Ordre Recommandé d'Implémentation

1. **Commencer par ProjectListPage**
   - Affichage liste basique
   - Formulaire création projet
   - Test CRUD projet

2. **Ajouter les Sous-Projets**
   - ProjectCard avec liste de subprojects
   - SubProjectForm
   - Navigation vers éditeur

3. **Développer GraphEditorPage**
   - Chargement du subproject
   - MermaidViewer simple
   - MermaidEditor (textarea)
   - Sauvegarde

4. **Améliorer l'UX**
   - Éditeur Monaco (optionnel)
   - Aperçu temps réel
   - Import/Export
   - Confirmations de suppression

### Gestion des Erreurs
```typescript
// Toujours wrapper les appels API dans try/catch
try {
  const projects = await apiService.getProjects()
  setProjects(projects)
} catch (err) {
  setError(err instanceof Error ? err.message : 'Erreur inconnue')
}
```

### État de Chargement
```typescript
// Afficher un spinner pendant le chargement
{loading ? (
  <div className="text-center">Chargement...</div>
) : (
  <div>Contenu</div>
)}
```

---

## 📝 Checklist Finale

- [ ] ProjectListPage affiche tous les projets
- [ ] Création de projet fonctionne
- [ ] Suppression de projet fonctionne
- [ ] Création de sous-projet fonctionne
- [ ] Navigation vers GraphEditorPage fonctionne
- [ ] GraphEditorPage charge et affiche le subproject
- [ ] Visualisation Mermaid fonctionne
- [ ] Édition et sauvegarde du code Mermaid fonctionnent
- [ ] Export Mermaid fonctionne
- [ ] Import Mermaid fonctionne
- [ ] Gestion des erreurs est en place
- [ ] UI est responsive et agréable

---

Bon développement ! 🚀
