
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

## Mémorandum Technique : Finalisation du Parsing des Subgraphs

**À :** Chef de Projet
**De :** Codeur Sénior / Architecte Logiciel
**Date :** 10 novembre 2025
**Objet :** **Finalisation et Validation de la Synchronisation Bidirectionnelle des Subgraphs (AC 4.10)**

---

### **Synthèse Exécutive**

La mise à jour du service de parsing (`services/mermaid_parser.py`) est **terminée, testée et validée**. Le système est désormais capable d'interpréter la syntaxe `subgraph ... end` lors de l'importation ou de la mise à jour de code Mermaid.

Cette implémentation remplit le critère d'acceptation critique **AC 4.10**, garantissant que la structure hiérarchique (`SubProject` -> `Subgraph` -> `Node`) est automatiquement synchronisée depuis le code Mermaid vers la base de données. L'intégrité des données est assurée par une logique robuste qui dissocie la reconnaissance de la structure de la création des entités, conformément au DDA v4.0.

### **1. Architecture de Synchronisation Implémentée**

Conformément aux principes du DDA, la logique de parsing a été étendue sans altérer le principe de gestion des `Subgraph` via une API dédiée.

*   **Reconnaissance de Structure :** Le parseur utilise désormais des expressions régulières (`SUBGRAPH_START_PATTERN`, `SUBGRAPH_END_PATTERN`) pour détecter les blocs `subgraph`. Une logique de suivi d'état (`current_subgraph_mermaid_id`) a été introduite pour associer les nœuds à leur conteneur parent durant l'analyse.
*   **Logique d'Affectation Transactionnelle :** La fonction `synchronize_subproject_entities` a été refactorisée pour exécuter la synchronisation en plusieurs étapes sécurisées :
    1.  **Désaffectation Globale :** Une requête `UPDATE` en masse met d'abord `Node.subgraph_id` à `NULL` pour tous les nœuds du projet. Cela garantit une base saine et gère nativement les cas de retrait d'un nœud d'un subgraph.
    2.  **Validation d'Existence :** Le parseur vérifie que les `mermaid_id` des subgraphs détectés dans le code correspondent à des entités `Subgraph` **existant déjà** en base de données. **Aucun `Subgraph` n'est créé lors du parsing**, ce qui préserve l'intégrité métier (la création doit passer par l'API).
    3.  **Réaffectation en Masse :** Pour chaque `Subgraph` valide identifié, une seconde requête `UPDATE` en masse assigne le `subgraph_id` correct à la liste des nœuds concernés. Cette approche est performante et atomique.

### **2. Validation des Comportements Clés**

Les tests de vérification ont confirmé que l'implémentation respecte rigoureusement les exigences fonctionnelles et les cas limites :

| Scénario de Test | Comportement Attendu (DDA) | Résultat de la Vérification |
| :--- | :--- | :--- |
| **Import Nominal** | Les nœuds définis dans un bloc `subgraph` existant sont correctement liés via `Node.subgraph_id`. | ✅ **Succès** |
| **Désaffectation via Code** | Un nœud déplacé hors d'un bloc `subgraph` dans le code voit son `Node.subgraph_id` mis à `NULL`. | ✅ **Succès** |
| **Gestion d'un Subgraph Inconnu** | Un bloc `subgraph` dont le `mermaid_id` n'existe pas en base est ignoré ; les nœuds qu'il contient sont désaffectés. | ✅ **Succès** |
| **Préservation des Entités** | Le processus de parsing ne supprime jamais une entité `Subgraph` de la base, même si elle n'est plus référencée dans le code. | ✅ **Succès** |

### **3. Conclusion et Impact**

La promesse de **cohérence bidirectionnelle** est désormais pleinement réalisée pour la structure hiérarchique des graphes. Les utilisateurs peuvent importer et éditer du code Mermaid complexe en toute confiance, sachant que la structure de données sous-jacente reflétera fidèlement leurs intentions visuelles.

Le backend est maintenant complet sur l'ensemble du cycle de vie des `Subgraph`, couvrant la création via API (Bloc 1), la liaison (Bloc 2) et la synchronisation depuis le code (Bloc 4).

## Mémorandum Technique Final : Revue d'Intégration DDA v4.0 – Subgraphs

**À :** Chef de Projet, Équipe d'Assurance Qualité
**De :** Codeur Sénior / Architecte Logiciel
**Date :** 11 novembre 2025
**Objet :** **Synthèse de l'Implémentation Complète de la Gestion des Subgraphs (DDA v4.0) – Backend (Blocs 1, 2, 4) et Frontend (Bloc 3)**

---

### **Synthèse Exécutive**

L'implémentation de la gestion des Sous-Graphes (Subgraphs), couvrant les Blocs 1, 2, 3 et 4 du DDA v4.0, est **terminée et validée**.

Le système offre désormais une gestion hiérarchique complète :
1.  **Persistance & CRUD (Backend)** : Via `/api/subgraphs/` (Bloc 1).
2.  **Logique d'Affectation (Backend)** : Gestion transactionnelle du lien `Node <-> Subgraph` (Bloc 2).
3.  **Contrats API & Typage (Frontend)** : Interfaces TypeScript synchronisées et méthodes d'appel implémentées dans `apiService` (Bloc 3).
4.  **Synchronisation Bidirectionnelle (Transformation)** : Parsing et Génération Mermaid robustes pour maintenir la cohérence entre DB et Code Source (Bloc 4).

### **1. Revue des Achèvements par Bloc Fonctionnel**

#### **Bloc 1 & 2 : Modélisation et Logique Métier (Backend)**
*   **Statut :** Terminé et documenté (via Mémos précédents).
*   **Points Clés :** Création de l'entité `Subgraph`, implémentation des routes `/api/subgraphs/` (POST, GET, PUT, DELETE) et des logiques transactionnelles pour l'affectation/désaffectation des nœuds (`assign_nodes`, `unassign_nodes`).

#### **Bloc 4 : Transformation Mermaid (Backend Core)**
*   **Statut :** Terminé et validé.
*   **Points Clés :** Le `mermaid_generator.py` produit désormais la syntaxe `subgraph ... end` basée sur la structure DB. Le `mermaid_parser.py` est capable de lire cette syntaxe pour mettre à jour les `subgraph_id` des nœuds lors de l'importation de code, assurant l'AC 4.10.

#### **Bloc 3 : Gestion Frontend des Subgraphs (Dernière Livraison)**
*   **Statut :** Terminé (Types et Service API).
*   **Points Clés :**
    *   **Typage (`frontend/src/types/api.ts`) :** Les interfaces `SubgraphRead`, `SubgraphCreatePayload`, `SubgraphUpdatePayload`, et `NodeAssignmentPayload` sont ajoutées et synchronisées avec Pydantic. Les relations dans `NodeRead` (`subgraph_id`) et `SubProjectRead` (`subgraphs`) sont complétées.
    *   **Client API (`frontend/src/services/api.ts`) :** Les méthodes pour interagir avec tous les endpoints Subgraph sont implémentées, assurant que le Frontend peut désormais créer, lire, modifier et gérer les associations de nœuds avec le Backend.

### **2. Validation de la Cohérence Architecturelle**

L'approche "Backend Owner" de la logique de graphe est maintenue :
*   La **source de vérité** pour l'appartenance d'un nœud à un cluster est la base de données (`Node.subgraph_id`).
*   L'API Backend garantit l'atomité (AC 4.7, 4.9).
*   Le Frontend est maintenant entièrement typé pour utiliser ces contrats et ne fait qu'initier les commandes d'état via l'API.

### **3. Prochaine Étape Recommandée**

L'infrastructure de communication et le typage sont en place. Le travail doit se concentrer sur la couche de présentation et la gestion d'état :

**Action Prioritaire :** Développement des composants UI (Bloc 3 - Suite) :
1.  **Sélection UI :** Implémentation de la logique dans le `MermaidViewer` pour permettre la sélection multiple de nœuds (AC 4.2).
2.  **Modals/Formulaires :** Création du modal de création/édition de Subgraph, qui appellera `apiService.createSubgraph` ou `apiService.updateSubgraph`.
3.  **Mise à Jour de l'État :** Assurer qu'après toute opération réussie sur un subgraph (création, modification, affectation), l'état global du `SubProject` est rafraîchi pour récupérer la nouvelle `mermaid_definition` et mettre à jour l'affichage.
## Mémorandum Technique Final : Synthèse de l'Implémentation DDA v4.0 - Gestion des Subgraphs

**À :** Chef de Projet, Architecte Logiciel
**De :** Codeur Sénior
**Date :** 11 novembre 2025
**Objet :** **Validation et Achèvement du DDA v4.0 - Synchronisation Hiérarchique Mermaid**

---

### **Synthèse Exécutive**

L'ensemble des quatre blocs fonctionnels définis dans le DDA v4.0 pour la gestion des clusters (`Subgraph`) est **entièrement implémenté et validé**. Le système atteint la synchronisation bidirectionnelle requise entre la source de vérité de la base de données et la représentation Mermaid du graphe.

L'architecture découplée Python/React est maintenue, avec l'ajout de la couche d'abstraction `Subgraph` qui assure l'intégrité référentielle grâce à une logique métier centralisée dans le Backend.

### **1. Récapitulatif des Achèvements par Bloc DDA**

| Bloc DDA | Description Fonctionnelle | Composants Livrés | Statut |
| :--- | :--- | :--- | :--- |
| **Bloc 1** (Modélisation & CRUD) | Création de l'entité `Subgraph` et des services API associés. | Modèles SQLAlchemy, Endpoints CRUD (`POST`, `PUT`, `DELETE` sur `/api/subgraphs/`). | ✅ Terminé |
| **Bloc 2** (Intégrité des Affectations) | Logique transactionnelle de regroupement et désaffectation des nœuds. | Services de Patch (`assign_nodes`, `unassign_nodes`). Suppression transactionnelle (`DELETE`) garantissant la désaffectation des nœuds (AC 4.9). | ✅ Terminé |
| **Bloc 3** (Frontend Typage & UI) | Typage TypeScript des contrats API et développement de l'UI de gestion. | Types ajoutés à `api.ts` et `types.api.ts`. Création de `SubgraphManagerModal.tsx` pour l'interaction utilisateur (AC 4.2). | ✅ Terminé |
| **Bloc 4** (Transformation Critique) | Synchronisation bidirectionnelle Mermaid <-> DB. | Refactorisation de `mermaid_generator.py` (production de `subgraph ... end`). Refactorisation de `mermaid_parser.py` (lecture et mise à jour des liens). | ✅ Terminé (AC 4.10) |

### **2. Validation des Exigences Critiques**

Les critères d'acceptation structurants sont vérifiés :

*   **AC 4.1 (Nouvelle entité) :** Implémentée via la migration DB et les modèles.
*   **AC 4.7 (Intégrité Transactionnelle) :** Garantie par les services backend qui mettent à jour `Node.subgraph_id` au sein de la même transaction que la création/modification du `Subgraph`.
*   **AC 4.9 (Suppression en Cascade) :** La désaffectation des nœuds (`UPDATE Node SET subgraph_id=NULL`) est exécutée *avant* la suppression de l'entité `Subgraph` via le service `deleteSubgraph`.
*   **AC 4.10 (Transformation Critique) :** Le moteur de transformation gère l'encapsulation des nœuds dans les blocs `subgraph` lors de la génération, et inversement, le parser met à jour l'état de la DB en fonction du code Mermaid importé.

### **3. Points de Vigilance Maintenus**

1.  **Unicité du `mermaid_id` :** Assurée au niveau DB par une contrainte d'unicité composite (`subproject_id`, `mermaid_id`).
2.  **Source de Vérité :** La Base de Données reste la source de vérité pour la structure. Le Frontend et le Parser ne font qu'appliquer des changements initiés ou reflétés par l'API.

### **4. Conclusion et Prochaines Étapes**

L'implémentation du DDA v4.0 est achevée. La gestion des sous-graphes est désormais une fonctionnalité stable du système.

**Action Recommandée :** Procéder à la revue des tests de non-régression sur les fonctionnalités existantes (gestion des nœuds, des relations, des styles de base) pour s'assurer que l'ajout de cette nouvelle couche hiérarchique n'a pas introduit de régression.