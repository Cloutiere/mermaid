
## Mémorandum Technique DBA Stratégique

**À :** Équipe de Développement Backend et Architecture (via le Prompteur)
**De :** Administrateur de Base de Données Stratégique
**Date :** 8 novembre 2025
**Objet :** Validation du Schéma de Base de Données v4.0 – Intégration de l'Entité `Subgraph` (Bloc 1 & 2 du DDA)

---

### **Synthèse Exécutive**

La phase de modélisation de la version 4.0, concernant l'intégration de la gestion des **Sous-Graphes (Subgraphs)**, est **terminée et validée** par une migration de schéma réussie.

Le modèle de données supporte désormais la hiérarchie à trois niveaux (`SubProject` -> `Subgraph` -> `Node`). L'architecture de persistance est prête pour le développement des services CRUD et de la logique d'affectation des nœuds.

### **1. Changements de Schéma Implémentés**

La migration `411342cce6d6` a apporté les modifications structurelles suivantes, garantissant la normalisation et l'intégrité référentielle :

| Table | Modification | Détails Techniques | Contexte DDA |
| :--- | :--- | :--- | :--- |
| **`subgraph` (NOUVELLE)** | Création de la table | Contient `id`, `subproject_id` (FK), `mermaid_id`, `title`, `style_class_ref`. | AC 4.1, 4.3, 4.4, 4.5 |
| **`node`** | Ajout de colonne | Ajout de `subgraph_id` (`INT`, `NULLABLE`). Clé étrangère vers `subgraph.id`. | AC 4.1 |
| **`subproject`** | Ajout de relation | Nouvelle relation one-to-many vers `subgraph`. | Support de la hiérarchie |

### **2. Garanties d'Intégrité et Contraintes Clés**

Les contraintes de la DDA sont respectées au niveau du schéma pour garantir la robustesse :

#### **2.1. Unicité (`mermaid_id`)**

Une contrainte d'unicité composite (`uq_subproject_subgraph_mermaid_id`) a été mise en place sur `(subproject_id, mermaid_id)`.
*Conséquence :* Il est impossible d'avoir deux Subgraphs avec le même `mermaid_id` au sein d'un même `SubProject`. Le Backend doit donc garantir la génération d'un `mermaid_id` unique lors de la création (AC 4.3).

#### **2.2. Intégrité Référentielle et Désaffectation des Nœuds (AC 4.9)**

La colonne `node.subgraph_id` est `NULLABLE`.

*   **Comportement de Suppression du Subgraph :** Bien que la clé étrangère permette théoriquement un `ON DELETE SET NULL`, la stratégie retenue dans le DDA impose que le **Service Backend** gère explicitement l'étape de désaffectation (mise à jour de `Node.subgraph_id = NULL` pour les nœuds concernés) *avant* la suppression du `Subgraph`.
*   **Point de Vigilance pour le Backend (AC 4.9) :** Le service de suppression du Subgraph (Bloc 2) doit impérativement exécuter cette mise à jour transactionnelle pour éviter que les nœuds ne soient laissés dans un état incohérent lors de la tentative de suppression de la référence.

### **3. Conséquences et Prochaines Étapes pour le Développement**

La structure de données étant établie, l'équipe de développement peut désormais se concentrer sur l'implémentation de la logique d'application définie dans les Blocs 1, 2 et 4 du DDA.

| Bloc DDA | Tâche Backend Principale | Dépendance Schéma |
| :--- | :--- | :--- |
| **Bloc 1** | Implémenter le CRUD pour `/api/subgraphs`. | Utilisation des modèles `Subgraph` et `SubProject`. |
| **Bloc 2** | Développer la logique d'affectation/désaffectation des nœuds. | Nécessite des écritures ciblées sur `Node.subgraph_id` (AC 4.7, 4.8). |
| **Bloc 4** | Mettre à jour `mermaid_generator.py`. | Doit interroger les `Subproject.subgraphs` et itérer sur `Subgraph.nodes` pour générer la syntaxe `subgraph ... end`. **Ceci est le point le plus critique pour la cohérence bidirectionnelle (AC 4.10).** |

Je reste disponible pour valider les modèles de Pydantic et les requêtes de services qui manipuleront ces nouvelles structures afin de garantir une performance optimale, notamment l'utilisation efficace des indexes créés (`ix_node_subgraph_id` et `ix_subgraph_subproject_id`).

## Mémorandum Technique : Implémentation du Backend Core

**À :** Chef de Projet, Équipe de Développement Frontend
**De :** Codeur Sénior / Architecte Logiciel
**Date :** 9 novembre 2025
**Objet :** **Finalisation du Backend Core pour la Gestion des Subgraphs (DDA v4.0 - Blocs 1 & 2)**

---

### **Synthèse Exécutive**

Les services backend pour la gestion complète du cycle de vie des **Subgraphs** sont désormais **implémentés, testés et opérationnels**. Cette livraison couvre les Blocs 1 (CRUD) et 2 (Liaison Nœuds-Subgraphs) du Document de Décision d'Architecture (DDA) v4.0.

L'API est stable et fournit tous les endpoints nécessaires pour que l'équipe Frontend puisse développer l'interface utilisateur de gestion des clusters. L'intégrité des données et la synchronisation bidirectionnelle avec la définition Mermaid sont garanties au niveau du service, conformément aux exigences critiques (AC 4.7, 4.9, 4.10).

### **1. Architecture Implémentée et Composants Livrés**

Conformément au DDA, l'architecture a été étendue avec les composants suivants :

*   **Service Métier (`services/subgraphs.py`) :** Un nouveau service encapsule toute la logique transactionnelle, incluant la création, la mise à jour, la suppression, et surtout, l'affectation/désaffectation en masse des nœuds.
*   **Blueprint API (`routes/subgraphs.py`) :** Un ensemble de routes RESTful a été créé pour exposer ces fonctionnalités de manière sécurisée et structurée.
*   **Schémas de Données (`schemas.py`) :** De nouveaux schémas Pydantic (`SubgraphCreatePayload`, `SubgraphUpdatePayload`, `NodeAssignmentPayload`, etc.) ont été définis pour valider rigoureusement les données d'entrée de l'API.
*   **Mise à jour Critique du Générateur (`services/mermaid_generator.py`) :** Le générateur a été refactorisé pour interpréter la relation `SubProject -> Subgraph -> Node` et produire la syntaxe Mermaid `subgraph ... end` (AC 4.10).

### **2. API Endpoints et Logique Associée**

Le tableau suivant détaille les fonctionnalités désormais disponibles via l'API `/api/subgraphs/` :

| Fonctionnalité (DDA) | Endpoint HTTP | Payload Requis (Schéma) | Logique Clé Implémentée |
| :--- | :--- | :--- | :--- |
| **Création & Affectation Initiale** (Bloc 1 & 2) | `POST /` | `SubgraphCreatePayload` | 1. Génération d'un `mermaid_id` unique (AC 4.3). 2. Création de l'entité `Subgraph`. 3. Affectation en masse des `node_ids` fournis (AC 4.7). 4. Régénération de `mermaid_definition`. |
| **Lecture** (Bloc 1) | `GET /<subgraph_id>` | - | Chargement du Subgraph et de ses nœuds associés. |
| **Mise à Jour des Métadonnées** (Bloc 1) | `PUT /<subgraph_id>` | `SubgraphUpdatePayload` | Modification du `title` et/ou du `style_class_ref`. Déclenche la régénération Mermaid. |
| **Affectation / Remplacement de Nœuds** (Bloc 2) | `PATCH /<id>/assign_nodes` | `NodeAssignmentPayload` | Mise à jour en masse du champ `Node.subgraph_id` pour la liste de nœuds fournie. |
| **Désaffectation de Nœuds** (Bloc 2) | `PATCH /<id>/unassign_nodes` | `NodeAssignmentPayload` | Mise à jour en masse du champ `Node.subgraph_id` à `NULL` pour les nœuds spécifiés. |
| **Suppression** (Bloc 2) | `DELETE /<subgraph_id>` | - | **Transactionnelle :** 1. Désaffecte tous les nœuds contenus (`UPDATE Node SET subgraph_id=NULL`). 2. Supprime l'entité `Subgraph` (AC 4.9). 3. Régénère `mermaid_definition`. |

### **3. Garanties d'Intégrité et de Cohérence**

Les principes fondamentaux du DDA ont été respectés :

*   **Intégrité Transactionnelle :** Toutes les opérations modifiant la structure (création, suppression, affectation) sont atomiques. Un échec, y compris lors de la régénération Mermaid, entraîne un `rollback` complet de la transaction, empêchant tout état incohérent de la base de données.
*   **Cohérence Bidirectionnelle (AC 4.10) :** La fonction `generate_mermaid_from_subproject` est systématiquement invoquée à la fin de chaque transaction réussie. La `mermaid_definition` du `SubProject` est donc en permanence le reflet exact de la structure relationnelle de la base de données.
*   **Utilisation d'Opérations en Masse (`Bulk Update`) :** L'affectation et la désaffectation des nœuds sont réalisées via des instructions `UPDATE` en masse, garantissant une performance optimale même avec un grand nombre de nœuds à manipuler.

### **4. Prochaines Étapes : Handoff à l'Équipe Frontend**

Le backend est prêt. L'équipe Frontend peut désormais commencer l'implémentation de l'interface utilisateur (Bloc 3) en s'appuyant sur les endpoints décrits ci-dessus.

**Actions recommandées pour le Frontend :**
1.  Implémenter la logique de sélection multiple de nœuds dans le `MermaidViewer`.
2.  Créer le composant modal pour la création (`POST`) et l'édition (`PUT`) d'un Subgraph, en utilisant les schémas `SubgraphCreatePayload` et `SubgraphUpdatePayload` comme contrat.
3.  Connecter les actions utilisateur (ex: glisser-déposer un nœud dans un cluster, supprimer un cluster) aux endpoints `PATCH` et `DELETE` correspondants.
4.  **Crucial :** Après chaque opération réussie, rafraîchir les données du `SubProject` pour récupérer la nouvelle `mermaid_definition` et forcer le `MermaidViewer` à se redessiner.

Le backend garantit la logique et la cohérence des données ; le frontend peut se concentrer sur l'expérience utilisateur.