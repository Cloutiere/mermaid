## Document de Décision d'Architecture (DDA) : Éditeur Visuel de Structure de Récit Mermaid (Version Finale Python/Flask)

### 1. Rappel des Exigences Fonctionnelles Structurantes

Le projet exige la construction d'un outil d'édition de graphe haute performance où la base de données relationnelle est la source de vérité pour la structure narrative.

*   **Intégrité et Normalisation des Données :** Schéma relationnel strict pour la hiérarchie `Projet (Saga) > Sous-Projet (Livre) > Nœud`.
*   **Base de Données Source de Vérité :** La structure Mermaid est un artefact *généré* à partir des tables.
*   **Transformation Bidirectionnelle Critique :** Implémentation des services d'Import (Parsing) et d'Export (Génération) du code Mermaid.
*   **Interactivité Élevée :** Nécessité d'une Single Page Application (SPA) réactive.
*   **Contexte Technique :** Python/Flask/SQLAlchemy pour le Backend, React/TS pour le Frontend, persistance sur PostgreSQL (Neon), sécurisation par Clé API.

### 2. Architecture Globale Proposée

**Architecture Découplée avec Backend Python comme Autorité Structurelle (Structural Authority).**

Le Backend Python gère toute la logique métier complexe et garantit l'intégrité des données stockées dans PostgreSQL.

*   **Frontend (React/TS) :** Gère l'affichage, le rendu `Mermaid.js`, l'interactivité utilisateur et la gestion des états locaux.
*   **Backend (Flask/SQLAlchemy) :** Sert une API RESTful transactionnelle. Il est responsable de l'exécution des opérations CRUD et de l'orchestration des services de transformation du graphe.
*   **Flux de Données :** L'UI envoie des requêtes d'état métier (ex: "créer un lien") → Le Backend met à jour les tables via SQLAlchemy → Le Backend génère le nouveau code Mermaid → Le Frontend reçoit le code généré et le visualise.

### 3. Choix de la Stack Technologique et Justifications

| Domaine | Technologie Recommandée | Justification et Compromis |
| :--- | :--- | :--- |
| **Frontend (SPA)** | **React (avec TypeScript)** | Choix maintenu. Excellent pour l'interactivité, l'état complexe (synchronisation) et les mises à jour fréquentes du DOM. |
| **Backend (API)** | **Flask (Python)** | **Justification :** Alignement sur les compétences Python, garantissant une haute vélocité de développement. Flask est léger, mais permet une structure d'application professionnelle (via Blueprints) pour encapsuler la logique complexe de graphe. |
| **ORM / Accès BD** | **SQLAlchemy (Python)** | **Justification :** ORM de niveau professionnel essentiel pour implémenter un schéma PostgreSQL robuste avec gestion des clés primaires auto-incrémentées (`SERIAL`) et l'intégrité des clés étrangères. |
| **Sérialisation API** | **Pydantic (Python)** | Garantit la validation des données entrantes et la sérialisation cohérente des objets SQLAlchemy vers des JSON (et inversement), renforçant la sécurité et la clarté de l'API. |
| **Base de Données** | **PostgreSQL (via Neon)** | Base de données relationnelle la plus adaptée à l'intégrité des données hiérarchiques et à la gestion des transactions nécessaires pour les manipulations de graphe. |
| **Outils Clés : Graphe** | **Services Python Custom** | Le Parsing et la Génération de Graphe seront des modules Python dédiés dans le Backend, s'appuyant sur les classes SQLAlchemy. |

### 4. Principes de Conception et Conventions Initiales

#### A. Modèle de Données Relationnel (SQLAlchemy/PostgreSQL)

Le schéma garantit l'intégrité et la hiérarchie, avec des identifiants numériques auto-incrémentés comme clés primaires (`id` PK, SERIAL) :

| Table | Rôle | Attributs Clés |
| :--- | :--- | :--- |
| `Project (Saga)` | Conteneur racine | `id` (PK, SERIAL), `title` |
| `SubProject (Livre)` | Graphe narratif complet | `id` (PK, SERIAL), `project_id` (FK), `title` |
| `Node (Paragraphe)` | Les boîtes du graphe | `id` (PK, SERIAL), `subproject_id` (FK), `mermaid_id` (String ID unique, ex: A1), `title`, `text_content` (TEXT, Markdown), `style_class_ref` |
| `Relationship (Lien)` | Les flèches entre nœuds | `id` (PK, SERIAL), `subproject_id` (FK), `source_node_id` (FK), `target_node_id` (FK), `label`, `link_type` (ENUM: VISIBLE, INVISIBLE), `color` |
| `ClassDef` | Définitions de style | `id` (PK, SERIAL), `subproject_id` (FK), `name`, `definition_raw` (CSS/Mermaid) |

#### B. Synchronisation Bidirectionnelle

*   **Service de Parsing (Import) :** Reçoit le code Mermaid, utilise des algorithmes d'analyse pour extraire les entités et utilise SQLAlchemy pour les mapper et les insérer/mettre à jour de manière transactionnelle.
*   **Service de Génération (Export) :** Reçoit le `subproject_id`, interroge les tables `Node`, `Relationship` et `ClassDef` pour reconstituer l'intégralité du code Mermaid textuel dans l'ordre de priorité (définitions de classes, nœuds, relations, sous-graphes) avant de le renvoyer au client.

#### C. Gestion des Types (Convention Polyglotte)

Puisque le Frontend est en TypeScript et le Backend en Python, l'effort de synchronisation des types est accru :

*   Les schémas de données pour l'API seront définis en Python via **Pydantic**.
*   Des interfaces **TypeScript** correspondantes devront être définies manuellement côté React pour garantir que le Frontend communique correctement avec le Backend (contrat d'API).

### 5. Conséquences des Choix et Points de Vigilance

| Choix Architectural | Conséquence / Compromis Accepté | Point de Vigilance |
| :--- | :--- | :--- |
| **Backend Python/Flask** | Vélocité maximale grâce à l'alignement des compétences de l'équipe. | **Désalignement Linguistique :** Nécessité d'une discipline stricte pour maintenir les schémas Pydantic (Python) et TypeScript (Frontend) synchronisés. |
| **SQLAlchemy et Schéma Professionnel** | Intégrité des données garantie. Les outils d'analyse future du graphe seront facilités. | La mise en place initiale du schéma complexe du graphe dans SQLAlchemy demande une expertise significative dans l'ORM. |
| **Services Custom de Transformation** | Absolument critique pour la fonctionnalité essentielle (DB $\leftrightarrow$ Mermaid). | Ces services doivent être robustes face aux entrées non conventionnelles et être optimisés pour éviter la latence lors de la régénération du code Mermaid après chaque modification. |
| **Persistance des Méta-données Visuelles** | Les données de disposition visuelle (CA-800, coordonnées X/Y) ne sont pas gérées par Mermaid. | Ces informations doivent être stockées dans une colonne `visual_layout` (JSON) sur la table `SubProject` et gérées uniquement par le Frontend pour des raisons de performance. |

### 6. Prochaines Étapes et Handoff au Prompteur

Une fois ce Document de Décision d'Architecture validé, vous pouvez transmettre l'intégralité de ce DDA, ainsi que la Spécification Fonctionnelle originale et les clarifications apportées, à notre Chef de Développement (le Prompteur).

Son rôle sera alors de :
1. Prendre en compte cette architecture **Python/Flask/SQLAlchemy** comme la base technique du projet.
2. Découper la Spécification Fonctionnelle initiale en tâches de développement concrètes et ordonnées. La priorité absolue est donnée au développement du schéma relationnel (SQLAlchemy) et aux **Services Python de Parsing et de Génération de Graphe**.
3. Générer les prompts nécessaires pour le DBA Stratégique et le Codeur Sénior afin de mettre en œuvre cette architecture et les premières fonctionnalités.

Votre mission pour la genèse de ce projet est terminée.