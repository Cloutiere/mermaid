## Spécification Fonctionnelle : 4. Gestion des Sous-Graphes (Subgraphs)

### 1. Résumé du Besoin Métier
Permettre aux utilisateurs de regrouper logiquement des nœuds au sein d'un Sous-Projet en créant des Sous-Graphes (Clusters Mermaid), de leur attribuer des titres et des styles visuels, et de gérer leur contenu, afin d'améliorer l'organisation et la lisibilité des graphes complexes.

### 2. User Story
En tant qu'Éditeur de Graphe, je souhaite pouvoir sélectionner un ensemble de Nœuds et les regrouper dans un Sous-Graphe (Subgraph/Cluster) afin d'organiser logiquement la structure de mon récit et d'appliquer un style visuel à ce groupe.

### 3. Critères d'Acceptation (AC)

| ID | Élément | Critère d'Acceptation |
| :--- | :--- | :--- |
| **AC 4.1** | **Prérequis DB** | Le modèle `Node` doit être mis à jour pour inclure un champ `subgraph_id` (clé étrangère optionnelle vers la nouvelle table `Subgraph`). |
| **AC 4.2** | **Interface de Création** | L'utilisateur doit pouvoir sélectionner au moins deux nœuds dans le graphe, puis déclencher une action "Créer Subgraph". |
| **AC 4.3** | **Nommage** | Un identifiant unique Mermaid (`mermaid_id` généré automatiquement, ex: `cluster_SP_1`) doit être attribué au Subgraph. Ce nom doit être unique au sein du `SubProject`. |
| **AC 4.4** | **Titre d'Affichage** | L'utilisateur doit pouvoir définir un titre (`title`) pour le Subgraph, qui sera affiché en haut de la zone (ex: "Rencontres Spéciales"). |
| **AC 4.5** | **Style Visuel** | L'entité `Subgraph` doit pouvoir référencer un style défini dans la table `ClassDef` via un champ `style_class_ref` (le `name` de la `ClassDef`). |
| **AC 4.6** | **Mise à Jour** | L'utilisateur doit pouvoir modifier le titre et le style d'un Subgraph existant. |
| **AC 4.7** | **Mouvement de Nœud** | Lorsque des nœuds sont regroupés dans un nouveau Subgraph : <ul><li>Le champ `Node.subgraph_id` de ces nœuds est mis à jour pour pointer vers le nouveau Subgraph.</li><li>Si un nœud était déjà assigné à un autre Subgraph, cette affectation est supprimée (le `Node.subgraph_id` est mis à jour).</li></ul> |
| **AC 4.8** | **Retrait de Nœud** | L'utilisateur doit pouvoir retirer un ou plusieurs nœuds d'un Subgraph existant, ce qui implique de mettre leur `Node.subgraph_id` à `null`. |
| **AC 4.9** | **Suppression de Subgraph** | La suppression d'un Subgraph doit : <ul><li>Mettre `Node.subgraph_id` à `null` pour tous les nœuds qu'il contenait.</li><li>Supprimer l'entité Subgraph.</li></ul> |
| **AC 4.10** | **Cohérence Bidirectionnelle** | Toute opération de création, modification, suppression de Subgraph ou d'affectation/retrait de nœud doit : <ul><li>Déclencher la régénération de la `mermaid_definition` du `SubProject` pour inclure la syntaxe Mermaid `subgraph ... end`.</li><li>Déclencher l'actualisation du `MermaidViewer` côté frontend.</li></ul> |

### 4. Informations Complémentaires
*   **Modèle de Données Supplémentaire :**
    *   Création d'une nouvelle table `subgraph` avec les champs : `id`, `subproject_id` (FK), `mermaid_id` (unique, généré), `title`, `style_class_ref` (FK optionnel vers `classdef.name`).
    *   Mise à jour du modèle `Node` avec un champ `subgraph_id` (FK optionnel vers `subgraph.id`).
*   **Implications Backend :**
    *   Ajout d'un nouveau Blueprint pour les routes des Subgraphs (`/api/subgraphs/`).
    *   Implémentation des services CRUD pour l'entité `Subgraph`.
    *   Mise à jour des services `nodes.py` pour gérer les affectations de `subgraph_id`.
    *   Mise à jour des services `mermaid_parser.py` et `mermaid_generator.py` pour lire/écrire la syntaxe Mermaid des subgraphs.
*   **Implications Frontend :**
    *   Nouvel composant modal pour la création/édition des Subgraphs (titre, style).
    *   Logique de sélection multiple de nœuds dans le `MermaidViewer`.
    *   Interface pour lister, éditer et supprimer les Subgraphs existants.
    *   Le `GraphEditorPage` devra gérer la mise à jour du `SubProject.mermaid_definition` et le rafraîchissement visuel.

### 5. Blocs Fonctionnels Identifiés
**Bloc 1 : Modélisation & CRUD Backend :** Création du modèle `Subgraph` et des services/routes API pour gérer son cycle de vie.
**Bloc 2 : Liaison Nœuds-Subgraphs :** Logique dans les services `nodes.py` pour affecter/retirer des nœuds à/de sous-graphes.
**Bloc 3 : Gestion Frontend des Subgraphs :** UI pour créer, lister, éditer, supprimer des Subgraphs, et pour affecter des nœuds.
**Bloc 4 : Parsing & Génération Mermaid :** Mise à jour des transformateurs pour gérer la syntaxe `subgraph ... end` et les attributs des sous-graphes (titre, style).