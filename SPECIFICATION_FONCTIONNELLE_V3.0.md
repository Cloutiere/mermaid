## Spécification Fonctionnelle : 1. Importation de Contenu Narratif JSON

### 1. Résumé du Besoin Métier
Permettre à l'utilisateur de charger en masse le contenu textuel (`text_content`) des nœuds d'un Sous-Projet en utilisant un fichier JSON simple, afin de séparer la création de la structure du graphe (Mermaid) de l'écriture du contenu narratif.

### 2. User Story
En tant qu'Éditeur de Récit, je souhaite importer ou mettre à jour le contenu textuel des Nœuds d'un Sous-Projet à partir d'un fichier JSON formaté (Clé: `mermaid_id`, Valeur: `text_content`) afin de peupler rapidement le contenu narratif de mon graphe.

### 3. Critères d'Acceptation (AC)

| ID | Élément | Critère d'Acceptation |
| :--- | :--- | :--- |
| **AC 1.1** | **Interface** | Un nouveau bouton "Importer Contenu JSON" doit être ajouté à la page `GraphEditorPage`. |
| **AC 1.2** | **Fichier Source** | L'interface ne doit accepter que des fichiers de type `JSON`. |
| **AC 1.3** | **Format** | Le fichier JSON attendu doit être un objet simple: `{ "MERMAID_ID": "Contenu Textuel (MD supporté)", ... }`. |
| **AC 1.4** | **Comportement (Mise à Jour)** | L'opération met à jour le champ `text_content` du Nœud correspondant au `mermaid_id` dans la base de données. |
| **AC 1.5** | **Comportement (Nœud Manquant)** | Si un `mermaid_id` est dans le JSON mais n'existe pas dans le Sous-Projet, il doit être ignoré. |
| **AC 1.6** | **Impact sur le Graphe** | Seul le `text_content` est modifié. La structure du graphe (`mermaid_definition`, relations, etc.) reste intacte. |
| **AC 1.7** | **Rapport** | L'utilisateur reçoit un rapport de confirmation après l'opération, incluant : <ul><li>Le nombre total de Nœuds mis à jour.</li><li>La liste des `mermaid_id` qui n'ont pas pu être trouvés et ont été ignorés.</li></ul>|
| **AC 1.8** | **Gestion des Erreurs** | L'opération doit être annulée si le fichier n'est pas un JSON valide. |
| **AC 1.9** | **Persistance** | Les modifications du `text_content` doivent être immédiatement sauvegardées en base de données après le traitement. |

### 4. Informations Complémentaires
*   **Permissions :** Tout utilisateur accédant au Sous-Projet peut exécuter l'import.
*   **Backend Implication :** Nécessité d'un nouvel endpoint API (ex: `POST /api/nodes/import_content/{subproject_id}`) et d'un service Python dédié dans `backend/app/services/nodes.py` ou un nouveau module.
*   **Mise à jour UI :** Le `text_content` n'est pas affiché dans le `MermaidViewer`, mais il doit être accessible dans l'éditeur de nœud (fonctionnalité à venir) et doit être mis à jour dans l'objet `SubProject` côté frontend après l'import.

### 5. Blocs Fonctionnels Identifiés
**Bloc 1 : Interface de Téléchargement** : Bouton et gestion de la sélection de fichier JSON sur la page d'édition.
**Bloc 2 : Service d'Import Backend** : Nouvelle logique métier pour valider le JSON, itérer sur les clés/valeurs, trouver les Nœuds correspondants par `mermaid_id` et mettre à jour `Node.text_content`.
**Bloc 3 : Affichage du Rapport** : Affichage d'une notification ou d'une modale pour le rapport de succès/erreur.

---

## Spécification Fonctionnelle : 2. Gestion et Application des Styles (ClassDef)

### 1. Résumé du Besoin Métier
Fournir une interface utilisateur dédiée pour gérer les définitions de styles (`classDef`) d'un Sous-Projet, et corriger la persistance de l'application de ces styles aux Nœuds.

### 2. User Story
En tant qu'Éditeur de Récit, je souhaite disposer d'un panneau latéral dans l'éditeur de graphe pour créer, modifier ou supprimer les Définitions de Classe (ClassDef) et les appliquer aux Nœuds via une interface simple, afin de contrôler visuellement la signification de mes éléments narratifs.

### 3. Critères d'Acceptation (AC)

| ID | Élément | Critère d'Acceptation |
| :--- | :--- | :--- |
| **AC 2.1** | **Interface** | Un panneau ou une modale (accessible depuis le `GraphEditorPage`) doit afficher la liste des `ClassDef` (Nom et Définition brute) du Sous-Projet. |
| **AC 2.2** | **Création (CRUD)** | L'utilisateur peut ajouter un nouveau `ClassDef` (Nom et Définition CSS brute). |
| **AC 2.3** | **Modification (CRUD)** | L'utilisateur peut modifier la définition CSS brute d'un `ClassDef` existant. |
| **AC 2.4** | **Suppression (CRUD)** | L'utilisateur peut supprimer un `ClassDef`. Si des Nœuds utilisaient ce style, leur `style_class_ref` doit être mis à `null`. |
| **AC 2.5** | **Application** | L'interface permet de sélectionner un `ClassDef` et de l'appliquer à un ou plusieurs Nœuds sélectionnés, en mettant à jour le champ `style_class_ref` du Nœud. |
| **AC 2.6** | **Désapplication** | L'interface permet de retirer le style d'un Nœud (mettre `style_class_ref` à `null`). |
| **AC 2.7** | **Cohérence** | Toute modification de style doit : <ul><li>Déclencher la mise à jour de la `mermaid_definition` (par le Service de Génération du Backend).</li><li>Déclencher l'actualisation du `MermaidViewer`.</li></ul> |
| **AC 2.8** | **Validation** | Le nom du `ClassDef` doit être unique dans le Sous-Projet. |
| **AC 2.9 (Critique)** | **Correction de Persistance** | **Préalable technique indispensable :** Le `mermaid_parser` et le `mermaid_generator` doivent être corrigés pour s'assurer que les affectations de classes (`class A001 start_node;`) sont correctement parsées, stockées dans `Node.style_class_ref`, et correctement régénérées lors de l'exportation. |

### 4. Informations Complémentaires
*   **UX/UI :** L'interface d'application (AC 2.5) pourrait se faire via une liste de Nœuds filtrable/recherchable dans le panneau des styles, ou via un outil de sélection de Nœuds directement dans le `MermaidViewer` (UX/UI complexe à spécifier ici, la priorité est sur la logique métier et la correction du Backend).
*   **Backend Implication :** Ajout de routes CRUD pour `ClassDef` (si elles ne sont pas déjà couvertes) et modification des services `nodes.py` et `class_defs.py` (à créer) pour gérer la mise à jour des Nœuds/Styles et garantir la cohérence (AC 2.9).

### 5. Blocs Fonctionnels Identifiés
**Bloc 1 : Correction du Backend Bi-directionnel :** Mise à jour du Parsing et de la Génération pour gérer correctement les affectations de classe (`class A ref`).
**Bloc 2 : CRUD des ClassDef :** Routes API et services pour gérer les entités `ClassDef`.
**Bloc 3 : Panneau de Gestion des Styles :** Composant Frontend pour lister, créer, éditer et supprimer les `ClassDef`.
**Bloc 4 : Application des Styles :** Logique Frontend/Backend pour mettre à jour le champ `Node.style_class_ref` pour les nœuds sélectionnés.

---

## Spécification Fonctionnelle : 3. Améliorations UX du Visualiseur

### 1. Résumé du Besoin Métier
Améliorer l'ergonomie de la page d'édition en ajoutant des fonctions de base de manipulation visuelle (zoom, déplacement) et en permettant de maximiser l'espace de visualisation du graphe.

### 2. User Story
**En tant qu'Éditeur de Graphe, je souhaite pouvoir zoomer, déplacer le graphe dans la fenêtre de visualisation, et masquer le panneau de l'éditeur de code afin d'améliorer mon expérience utilisateur et de me concentrer sur la structure visuelle.**

### 3. Critères d'Acceptation (AC)

| ID | Élément | Critère d'Acceptation |
| :--- | :--- | :--- |
| **AC 3.1** | **Redimensionnement UI** | La page d'édition (`GraphEditorPage`) doit permettre de masquer ou de minimiser la colonne contenant l'éditeur de code (`MermaidEditor`) pour donner plus d'espace à la colonne du visualiseur (`MermaidViewer`). (Exemple : basculer entre un layout 50/50 et 10/90, ou éditeur masqué/visualiseur plein écran). |
| **AC 3.2** | **Zoom et Pan** | Le `MermaidViewer` doit intégrer des fonctionnalités de zoom (via molette ou boutons + / -) et de déplacement (pan) du graphe dans son conteneur. *Conseil Expert : Ces fonctionnalités sont généralement intégrées via la configuration de la librairie Mermaid ou un wrapper SVG/DOM.* |
| **AC 3.3** | **Performance** | Le zoom et le déplacement doivent être fluides et ne pas re-déclencher un rendu Mermaid complet. |

### 4. Blocs Fonctionnels Identifiés
**Bloc 1 : Gestion du Layout :** Logique `GraphEditorPage.tsx` pour gérer l'état de la disposition des colonnes.
**Bloc 2 : Intégration du Zoom/Pan :** Mise à jour du composant `MermaidViewer.tsx` pour activer/intégrer les capacités de manipulation du graphe.