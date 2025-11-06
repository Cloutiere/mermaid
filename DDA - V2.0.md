Document de Décision d'Architecture (DDA) : Évolution de l'Éditeur Mermaid - V2.0

### 1. Rappel des Exigences Fonctionnelles Structurantes (Nouvelles Initiatives)

Cette itération introduit trois initiatives majeures qui étendent l'API et l'interface utilisateur, tout en corrigeant une lacune critique dans la gestion des données structurelles.

1.  **Importation de Contenu JSON (FNS 1)** : Nécessité d'un nouvel endpoint API pour la mise à jour en masse du champ `Node.text_content` à partir d'un objet JSON, garantissant la validation et l'intégrité des mises à jour transactionnelles.
2.  **Gestion des Styles (ClassDef CRUD et Cohérence) (FNS 2)** : Implémentation du CRUD pour l'entité `ClassDef` et, surtout, la correction indispensable des services de Parsing/Génération pour assurer la persistance de l'affectation des classes aux Nœuds (`Node.style_class_ref`).
3.  **Améliorations UX (Zoom/Pan/Layout) (FNS 3)** : Intégration de fonctionnalités de manipulation visuelle (zoom, déplacement) dans le `MermaidViewer` et flexibilité du layout sur `GraphEditorPage`.

### 2. Architecture Globale Proposée

L'architecture découplée Python/Flask + React/TypeScript est maintenue. Les évolutions se concentrent sur l'extension du domaine métier (Backend) et l'amélioration de l'expérience utilisateur (Frontend).

*   **Backend (Extension) :** Le module `nodes.py` sera étendu pour inclure la logique d'importation de contenu (FNS 1). Un nouveau module de routes et de services (`classdefs.py`) sera introduit pour le CRUD de `ClassDef` (FNS 2).
*   **Services de Transformation (Correction Critique) :** Les services `mermaid_parser.py` et `mermaid_generator.py` doivent être mis à jour en priorité pour assurer la cohérence bidirectionnelle des affectations de styles (`Node.style_class_ref`).

### 3. Choix de la Stack Technologique et Justifications

La stack technologique de base (React/TS, Flask/SQLAlchemy, PostgreSQL) est conservée. Les choix suivants sont des extensions nécessaires :

| Domaine | Composant / Outil | Justification et Compromis |
| :--- | :--- | :--- |
| **Backend (FNS 1)** | **Pydantic + Service Python dédié** | **Justification :** Utilisation de Pydantic pour valider le schéma JSON entrant (Clé/Valeur) avant le traitement en masse, assurant la robustesse du nouveau point d'entrée API. |
| **Backend (FNS 2)** | **Extension des Services de Graphe** | **Justification :** La correction de la bidirectionnalité doit être faite en Python (`mermaid_parser.py`, `mermaid_generator.py`) pour garantir que la DB reste la source de vérité structurelle. |
| **Frontend (FNS 3)** | **Librairie de Zoom/Pan SVG** | **Justification :** Pour implémenter AC 3.2 de manière performante sans re-rendre Mermaid, une librairie tierce (ex: `react-zoom-pan-pinch` ou configuration avancée de `mermaid.js` pour utiliser son wrapper SVG) est préférable. Compromis : Ajout d'une dépendance Frontend. |
| **Frontend (FNS 3)** | **Tailwind CSS / Flexbox** | **Justification :** Utilisation des utilitaires de layout existants (Tailwind/CSS) pour implémenter le masquage/minimisation de l'éditeur de code (AC 3.1), assurant la cohérence stylistique. |

### 4. Principes de Conception et Conventions Initiales

#### A. Implémentation du Service d'Importation de Contenu (FNS 1)

1.  **Endpoint API :** Création de l'endpoint `POST /api/nodes/import_content/<int:subproject_id>`.
2.  **Validation :** Le corps de la requête (JSON) doit être validé via un schéma Pydantic qui vérifie que les clés sont des chaînes (supposées être des `mermaid_id`) et les valeurs sont des chaînes (supposées être le `text_content`).
3.  **Logique Transactionnelle :** Le service Python doit exécuter la mise à jour en une seule transaction. Il doit utiliser une requête `UPDATE` en masse (si le nombre de nœuds est très grand) ou itérer et mettre à jour les objets `Node` en mémoire, en filtrant sur `Node.subproject_id` et `Node.mermaid_id`.
4.  **Rapport de Retour :** L'API doit retourner un JSON contenant le nombre de mises à jour réussies et les IDs ignorés (AC 1.7).

#### B. Correction et CRUD des Styles (FNS 2)

1.  **CRUD ClassDef :** Création d'un nouveau Blueprint (`classdefs_bp`) et d'un service (`backend/app/services/classdefs.py`) implémentant le CRUD standard pour l'entité `ClassDef`.
2.  **Correction du Parser (`mermaid_parser.py`) (AC 2.9) :** Le Parser doit être étendu pour identifier et extraire la syntaxe d'application de classe (`class A ref`) et persister la référence de classe dans le champ `Node.style_class_ref` lors de la synchronisation.
3.  **Correction du Générateur (`mermaid_generator.py`) (AC 2.9) :** Le Générateur doit être mis à jour pour lire `Node.style_class_ref` et générer la ligne d'application de classe appropriée (`class {mermaid_id} {style_class_ref}`) après la définition des nœuds.
4.  **Cohérence lors de la Suppression de Style (AC 2.4) :** Le service de suppression de `ClassDef` doit effectuer une requête de mise à jour en cascade pour mettre à `NULL` tous les `Node.style_class_ref` qui référencent la classe supprimée.
5.  **Déclenchement de la Génération :** Toute opération de CRUD sur `ClassDef` ou de modification de `Node.style_class_ref` doit déclencher la régénération et la mise à jour du champ `SubProject.mermaid_definition` pour maintenir la cohérence (comme c'est déjà le cas pour les autres modifications structurelles).

#### C. Conventions Frontend (FNS 3)

1.  **Layout Flexible :** Le `GraphEditorPage.tsx` doit utiliser un état pour contrôler la largeur des deux colonnes (éditeur/visualiseur), permettant un basculement entre les vues (Ex: 50%/50%, 10%/90% ou 0%/100%).
2.  **Mermaid Viewer Augmenté :** Le composant `MermaidViewer.tsx` doit être enveloppé dans un conteneur qui gère le zoom et le pan, soit via une librairie, soit en exploitant directement les fonctionnalités de manipulation du DOM SVG généré par Mermaid.

### 5. Conséquences des Choix et Points de Vigilance

| Choix Architectural | Conséquence / Compromis Accepté | Point de Vigilance |
| :--- | :--- | :--- |
| **Correction du Parser/Générateur (AC 2.9)** | Garantit que le modèle relationnel peut servir de source de vérité pour tous les aspects du graphe, y compris le style. | **Risque de Régression :** La modification des services de transformation est la plus risquée. Des tests unitaires exhaustifs sont impératifs sur `mermaid_parser.py` et `mermaid_generator.py` pour s'assurer qu'aucune syntaxe existante (nœuds, relations) n'est cassée. |
| **Import JSON en Masse (FNS 1)** | Offre une vélocité métier pour le remplissage de contenu. | **Performance :** Si le JSON contient des milliers de nœuds, l'opération de mise à jour en base de données doit être optimisée (mise à jour en masse SQL ou utilisation d'une session SQLAlchemy pour une exécution efficace). |
| **Intégration Zoom/Pan (FNS 3)** | Amélioration significative de l'UX pour les grands graphes. | **Compatibilité Mermaid :** S'assurer que le wrapper de zoom/pan ne perturbe pas la logique de rendu asynchrone et de "hard reset" du `MermaidViewer.tsx` qui semble nécessaire pour stabiliser le rendu Mermaid. |

### 6. Prochaines Étapes et Handoff au Prompteur

Une fois ce Document de Décision d'Architecture validé, vous pouvez transmettre l'intégralité de ce DDA, ainsi que la Spécification Fonctionnelle originale et les clarifications apportées, à notre Chef de Développement (le Prompteur).

Son rôle sera alors de :
1. Prendre en compte cette architecture comme la base technique du projet.
2. Découper la Spécification Fonctionnelle initiale en tâches de développement concrètes et ordonnées. La priorité absolue est donnée à la **Correction de Persistance ClassDef (AC 2.9)** et à l'implémentation du **Service d'Import JSON (FNS 1)**.
3. Générer les prompts nécessaires pour le DBA Stratégique et le Codeur Sénior afin de mettre en œuvre cette architecture et les nouvelles fonctionnalités.

Votre mission pour la genèse de ce projet est terminée.