## Document de Décision d'Architecture (DDA) : Gestion des Sous-Graphes (Subgraphs)

### 1. Rappel des Exigences Fonctionnelles Structurantes

L'architecture doit maintenant gérer une structure de données arborescente à trois niveaux (`SubProject > Subgraph > Node`) et garantir la synchronisation bidirectionnelle de cette hiérarchie complexe avec le code Mermaid.

*   **Hiérarchie et Normalisation (AC 4.1) :** Création d'une nouvelle entité `Subgraph` et modification de `Node` pour gérer la propriété de regroupement (FK).
*   **Intégrité de l'Affectation (AC 4.7, 4.9) :** Les opérations de regroupement et de dégroupement doivent être transactionnelles, garantissant qu'un nœud est soit dans un Subgraph, soit non assigné. La suppression d'un Subgraph doit cascader vers la désassignation des Nœuds.
*   **Transformation Critique (AC 4.10) :** Le Service de Génération Python doit placer correctement les définitions de Nœuds et leurs relations *à l'intérieur* des blocs `subgraph ... end`. Le Parser doit être capable de reconstruire l'appartenance structurelle lors de l'import.

### 2. Architecture Globale Proposée

L'architecture reste **Découplée (Python/Flask SOT + React UI)**.

*   **Backend (Extension Métier) :** Ajout d'un nouveau domaine (`subgraphs`) pour le CRUD. Le Backend assume la responsabilité complète de la gestion de la hiérarchie et de l'intégrité référentielle, agissant comme le seul endroit où la logique `Node.subgraph_id` est mise à jour.
*   **Services de Transformation (Cœur du Changement) :** Les modules `mermaid_parser.py` et `mermaid_generator.py` feront l'objet d'un développement très poussé pour supporter les structures de clustering Mermaid.

### 3. Choix de la Stack Technologique et Justifications

La stack technique existante est maintenue, avec l'extension des outils de persistance.

| Domaine | Composant / Outil | Justification et Rôle |
| :--- | :--- | :--- |
| **Persistance/Modélisation** | **SQLAlchemy/Flask-Migrate** | Nécessaire pour implémenter la nouvelle table `Subgraph` et la colonne `Node.subgraph_id` de manière professionnelle (clés primaires/étrangères, contraintes d'unicité). |
| **Backend Services** | **Flask / Pydantic** | Flask accueillera le nouveau Blueprint (`/api/subgraphs`). Pydantic sera utilisé pour valider les payloads des Subgraphs (titre, style) et les listes d'IDs de Nœuds pour l'affectation. |
| **Transformation** | **Service Python Custom (Refactoring)** | Le Parsing et la Génération de la syntaxe `subgraph` nécessiteront des mises à jour complexes des expressions régulières et de la logique de parcours des entités. |
| **Frontend UI** | **React / Custom Modal** | Les composants existants (`GraphEditorPage.tsx`) devront être étendus pour gérer l'état de la sélection multiple de Nœuds (AC 4.2) et lancer la requête de création de Subgraph. |

### 4. Principes de Conception et Conventions Initiales

#### A. Extension du Modèle de Données (AC 4.1)

Une **migration de base de données** est requise pour ajouter la nouvelle table `subgraph` et mettre à jour la table `node`.

1.  **Nouvelle Table `Subgraph`:**
    *   `id` (PK, SERIAL)
    *   `subproject_id` (FK vers `subproject.id`, NOT NULL)
    *   `mermaid_id` (String unique, ex: `cluster_A`, NOT NULL)
    *   `title` (String, NOT NULL)
    *   `style_class_ref` (FK optionnel vers `classdef.name`, NULLABLE)

2.  **Mise à jour de `Node`:**
    *   `subgraph_id` (FK optionnel vers `subgraph.id`, NULLABLE)

#### B. Nouveaux Services et Logique d'Affectation (AC 4.7, 4.9)

Un nouveau service `backend/app/services/subgraphs.py` sera créé pour le CRUD de l'entité `Subgraph`.

*   **Création de Subgraph (Transactionnelle) :** Le service de création de Subgraph doit recevoir le `subproject_id`, le `title` et une liste d'IDs de Nœuds.
    *   Le service doit : 1) Créer la nouvelle entité `Subgraph`. 2) Mettre à jour en masse le champ `Node.subgraph_id` pour les nœuds listés, écrasant toute affectation précédente (AC 4.7). 3) Déclencher la régénération Mermaid (AC 4.10).
*   **Suppression de Subgraph (AC 4.9) :**
    *   Le service de suppression doit d'abord exécuter une mise à jour en masse (`SQLAlchemy update`) pour mettre `Node.subgraph_id` à `NULL` pour tous les nœuds associés.
    *   Seulement après la désassignation, le `Subgraph` peut être supprimé.
    *   La régénération Mermaid est déclenchée.

#### C. Mise à Jour des Services de Transformation (AC 4.10)

C'est l'étape la plus délicate, nécessitant une refactorisation des générateurs et des parseurs.

*   **Génération (`mermaid_generator.py`) :**
    1.  Charger le SubProject avec `nodes`, `relationships`, `class_defs` et **`subgraphs`** (eager loading).
    2.  Après les `classDef`, itérer sur `SubProject.subgraphs`.
    3.  Pour chaque Subgraph, ouvrir le bloc `subgraph {title}`.
    4.  Dans ce bloc, générer les lignes de définition de tous les `Node` dont le `Node.subgraph_id` correspond au Subgraph actuel.
    5.  Fermer le bloc `end`.
    6.  Les relations (`A-->B`) doivent être générées *après* tous les Subgraphs.

*   **Parsing (`mermaid_parser.py`) :**
    *   Le parser doit être étendu pour détecter la syntaxe `subgraph ... end`.
    *   Lors de la détection d'un nœud (`A[Title]`) entre les marqueurs `subgraph` et `end`, il doit attribuer l'ID du Subgraph à ce nœud dans la structure des données intermédiaires (`nodes_data`).

### 5. Conséquences des Choix et Points de Vigilance

| Choix Architectural | Conséquence / Compromis Accepté | Point de Vigilance |
| :--- | :--- | :--- |
| **Nouveau Modèle `Subgraph`** | Base de données entièrement normalisée, supportant la hiérarchie. | Nécessite une migration de base de données réussie (via Flask-Migrate). Le risque de régression sur le `Node` est élevé pendant cette migration. |
| **Logique d'Affectation en Backend** | Intégrité référentielle garantie pour le regroupement/dégroupement. | Le `mermaid_id` généré pour le Subgraph (AC 4.3) doit être infailliblement unique au sein du SubProject. |
| **Modification Parser/Générateur** | Permet la synchronisation bidirectionnelle complète (AC 4.10). | La complexité du Parsing des Subgraphs est critique. Des tests unitaires ciblant les scénarios de Subgraphs imbriqués (même si Mermaid ne les supporte pas tous, la robustesse est clé) sont impératifs. |
| **Gestion Frontend de Sélection** | L'UI doit permettre la sélection de N nœuds pour l'action "Créer Subgraph" (AC 4.2). | Le Frontend ne doit pas tenter de modifier le code Mermaid directement pour créer un Subgraph; il doit uniquement envoyer les IDs des Nœuds sélectionnés à l'API `/api/subgraphs/` POST. |

### 6. Prochaines Étapes et Handoff au Prompteur

Une fois ce Document de Décision d'Architecture validé, vous pouvez transmettre l'intégralité de ce DDA, ainsi que la Spécification Fonctionnelle originale et les clarifications apportées, à notre Chef de Développement (le Prompteur).

Son rôle sera alors de :
1.  **Démarrer la Migration de Base de Données :** Définir le modèle `Subgraph` et mettre à jour `Node` dans `backend/app/models.py`, puis exécuter `flask db migrate` et `flask db upgrade`.
2.  **Développer le Bloc 1 et 2 (Backend CRUD/Liaison) :** Implémenter le CRUD pour `/api/subgraphs` et la logique d'affectation des nœuds dans les services.
3.  **Mettre à jour le Bloc 4 (Transformation) :** Refactoriser `mermaid_parser.py` et `mermaid_generator.py` pour supporter la syntaxe `subgraph`.
4.  Générer les prompts nécessaires pour le DBA Stratégique et le Codeur Sénior afin de mettre en œuvre cette architecture et les premières fonctionnalités.

Votre mission pour la genèse de ce projet est terminée.