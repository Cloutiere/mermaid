
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