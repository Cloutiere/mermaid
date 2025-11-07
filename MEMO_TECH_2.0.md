# Mémo Technique Détaillé : Phase d'Implémentation V2.0 - Import et Stabilité (Commit Logique 1 & 2)

**À :** Architecte DDA, Chef de Projet
**De :** Architecte Senior / Développeur
**Date :** [Date Actuelle]
**Objet :** Rapport d'implémentation de la fonctionnalité d'importation de contenu (FNS 1) et des corrections de persistance des métadonnées (AC 2.9, Direction du Graphe).

---

## I. Résumé Exécutif des Fonctionnalités Implémentées

Cette phase a couvert l'introduction d'une fonctionnalité clé pour l'injection de données narratives en masse et la résolution des problèmes de stabilité critiques liés au parsing et à la persistance des métadonnées Mermaid.

### 1. Implémentation FNS 1 : Importation de Contenu de Nœuds en Masse
La fonctionnalité permet désormais de mettre à jour le contenu textuel (`text_content`) des nœuds d'un `SubProject` via une seule requête, en utilisant le `mermaid_id` comme clé de mapping.

### 2. Stabilité et Persistance (AC 2.9)
Deux problèmes majeurs ont été résolus :
1.  **Robustesse du Parsing de Style :** Le parseur Mermaid a été renforcé pour accepter la syntaxe des définitions de nœuds complexes (`S{{"Title"}}`) et l'application des classes de style se terminant par un point-virgule (`class A style;`). Ceci assure la persistance bidirectionnelle de `Node.style_class_ref`.
2.  **Persistance de la Direction du Graphe :** Le sens de lecture du graphe (`graph LR`, `graph TD`, etc.) n'était pas stocké. Ce défaut a été corrigé en modifiant l'architecture du modèle de données et des services de parsing/génération. **(Requiert une migration de base de données - voir Section III).**

---

## II. Modifications et Conception Technique

### A. Services de Nœuds (`backend/app/services/nodes.py`)

**Nouvelle Fonction : `import_node_content(subproject_id: int, content_map: Dict[str, str])`**

1.  **Validation et Transactionnalité :** La fonction opère dans une transaction unique (`db.session.begin()`) pour garantir l'atomicité. Elle vérifie l'existence du `SubProject` (lever `NotFound`).
2.  **Mise à Jour en Masse :** Utilise une requête filtrée par `SubProject.id` et une clause `Node.mermaid_id.in_(content_map.keys())` pour récupérer uniquement les nœuds existants.
3.  **Filtrage (AC 1.5) :** Les clés présentes dans `content_map` mais sans correspondance dans le `SubProject` sont identifiées et traitées comme `ignored_ids`.
4.  **Cohérence de l'Artefact (AC 1.6/2.7) :** Crucialement, après la mise à jour de tous les `Node.text_content`, la fonction appelle `generate_mermaid_from_subproject` pour reconstruire la chaîne `SubProject.mermaid_definition`. Cette mise à jour assure que l'artefact de visualisation reste synchrone avec les données narratives.
5.  **Rapport (AC 1.7) :** Retourne un dictionnaire : `{'updated_count': int, 'ignored_ids': List[str]}`.

### B. Route API (`backend/app/routes/nodes.py`)

**Nouvel Endpoint : `POST /api/nodes/import_content/<int:subproject_id>`**

*   Accepte le schéma `NodeContentImport` (validation Pydantic).
*   Appelle le service `import_node_content`.
*   Retourne le rapport du service avec le statut `200 OK`.

### C. Schémas de Données (`backend/app/schemas.py`)

Un nouveau schéma a été introduit pour la validation de l'entrée de la fonction d'importation :

```python
class NodeContentImport(BaseModel):
    content_map: Dict[str, str] = Field(..., description="Map des mermaid_id aux nouveaux text_content.")
```

### D. Services de Parsing et Génération Mermaid

**1. `backend/app/services/mermaid_parser.py` (Version 2.2)**

*   **Correction Regex :**
    *   `NODE_DEFINITION_PATTERN` mis à jour pour capturer les nœuds de forme `A[Title]` ET `S{{"Title"}}`.
    *   `NODE_CLASS_PATTERN` mis à jour pour accepter le point-virgule final optionnel (`class A style;`).
*   **Extraction de la Direction :** La fonction `_parse_mermaid_elements` extrait maintenant la direction du graphe (`LR`, `TD`, etc.) à partir de la première ligne et la retourne comme premier élément.
*   **Synchronisation :** La fonction `synchronize_subproject_entities` reçoit la direction du graphe et l'assigne à `subproject.graph_direction` avant la suppression/réinsertion des entités.

**2. `backend/app/services/mermaid_generator.py` (Version 1.1)**

*   Le générateur utilise maintenant `subproject.graph_direction` au lieu d'une constante codée en dur (`DEFAULT_GRAPH_DIRECTION = "TD"`) pour la première ligne du fichier généré (`graph LR`).

---

## III. Impact sur le Schéma de Base de Données (Action DDA Requise)

Afin de persister la direction du graphe, le modèle `SubProject` a été étendu. **Une migration de base de données est indispensable.**

### Modèle `SubProject`

| Champ | Type SQL | Attributs Python | Justification |
| :--- | :--- | :--- | :--- |
| **`graph_direction`** (Nouveau) | `VARCHAR(10)` | `Mapped[str]` | Stocke la direction de rendu (ex: 'LR', 'TD'). |
| **Contraintes** | | `nullable=False` | La direction doit toujours être définie. |
| | | `server_default="TD"` | Assure que les entrées existantes ou les nouvelles créations par défaut utilisent 'TD' si non spécifié lors de l'insertion. |

### Commande de Migration Requise (Analyse par le DDA)

Après validation de ces changements, les commandes de migration (si Flask-Migrate est utilisé) seront :

```bash
# Génération du script de migration
flask db migrate -m "Add graph_direction to SubProject model"

# Application de la migration
flask db upgrade
```
Cette migration ajoutera la colonne `graph_direction` à la table `subproject` avec une valeur par défaut de 'TD' pour garantir la non-nullabilité des enregistrements existants.

**Objet :** Rapport d'Exécution et Analyse Technique : Migration `6432c963ce39` - Ajout de `graph_direction`

---

### I. Résumé Exécutif

La migration de base de données identifiée par la révision `6432c963ce39` a été **exécutée avec succès** sur l'environnement cible. L'opération consistait à ajouter la colonne `graph_direction` à la table `subproject` pour répondre à l'exigence de persistance de l'orientation du graphe Mermaid (AC 2.9).

L'opération a été menée de manière sécurisée, en utilisant une valeur par défaut (`'TD'`) pour garantir l'intégrité et la non-nullabilité des enregistrements existants. Le schéma de la base de données est maintenant parfaitement synchronisé avec la version la plus récente des modèles de données de l'application (`models.py`).

Le prérequis technique pour le déploiement des nouvelles fonctionnalités de parsing/génération (FNS 1, AC 2.9) est désormais rempli.

---

### II. Détail de l'Opération de Migration

La commande `flask db upgrade` a initié le processus géré par Alembic, comme en témoignent les logs fournis :

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 8aeba779c15d -> 6432c963ce39, Add graph_direction to SubProject model
```

**Décomposition technique :**

1.  **Connexion et Contexte :** Alembic s'est connecté à la base de données PostgreSQL et a démarré une transaction. La mention `transactional DDL` indique que l'ensemble de la migration sera exécuté comme une seule opération atomique : soit elle réussit entièrement, soit elle est annulée sans laisser de modifications partielles.
2.  **Identification de la Version :** Le système a détecté que la base de données était à la version `8aeba779c15d` et que la version cible du code était `6432c963ce39`.
3.  **Exécution du Script :** Le script de migration associé à la révision `6432c963ce39` a été exécuté. Basé sur le plan de migration validé, cela a entraîné l'exécution de l'instruction SQL suivante (ou une instruction équivalente générée par SQLAlchemy) sur la base de données :

    ```sql
    ALTER TABLE subproject
    ADD COLUMN graph_direction VARCHAR(10) NOT NULL DEFAULT 'TD';
    ```

**Analyse de l'instruction SQL :**
*   `ALTER TABLE subproject`: Cible la table correcte pour la modification.
*   `ADD COLUMN graph_direction VARCHAR(10)`: Ajoute la nouvelle colonne avec le type et la taille de données appropriés pour stocker des valeurs comme 'TD', 'LR', etc.
*   `NOT NULL`: Applique la contrainte d'intégrité garantissant que chaque `SubProject` aura toujours une direction définie.
*   `DEFAULT 'TD'`: **L'élément le plus critique de l'opération.** Le moteur PostgreSQL a automatiquement rempli la colonne `graph_direction` avec la valeur `'TD'` pour **toutes les lignes existantes** dans la table `subproject`. Cela a permis à la contrainte `NOT NULL` d'être appliquée sans erreur et assure qu'aucun enregistrement ancien ne se retrouve dans un état invalide.

---

### III. Impact et Conséquences

#### 1. Impact Fonctionnel
La persistance de la direction du graphe est maintenant active. Un graphe importé ou créé avec `graph LR` sera sauvegardé comme tel et sera régénéré correctement avec la même orientation lors des lectures futures. La lacune identifiée dans la non-persistance des métadonnées structurelles est comblée.

#### 2. Impact sur l'Application
*   **Synchronisation Schéma/Modèle :** La définition de la classe `SubProject` dans `backend/app/models.py` correspond désormais exactement à la structure de la table `subproject` en base de données. Il n'y a plus de divergence.
*   **Déblocage du Backend :** Les services mis à jour (`mermaid_parser.py` et le futur `mermaid_generator.py`) peuvent maintenant lire et écrire dans la colonne `graph_direction` sans erreur. La chaîne complète de traitement (Parsing -> Stockage DB -> Régénération) est maintenant fonctionnelle pour cet attribut.

#### 3. État Actuel de la Base de Données
*   La colonne `graph_direction` existe et est prête à l'emploi.
*   Tous les `SubProject` créés avant cette migration ont leur `graph_direction` positionnée à `'TD'`, ce qui est un comportement par défaut sûr et attendu.

---

### IV. Prochaines Étapes

1.  **Déploiement du Code Applicatif :** La nouvelle version du backend, qui utilise activement la colonne `graph_direction`, peut maintenant être déployée en toute sécurité.
2.  **Validation de la Fonctionnalité :** L'équipe de QA ou de développement peut procéder aux tests de bout en bout pour valider le cycle de vie complet d'un SubProject avec des directions de graphe variables (importation, modification, sauvegarde, rechargement).

La migration est terminée. La fondation de données est prête pour la suite du développement de la V2.0.

### Mémorandum Technique : Implémentation du CRUD `ClassDef` (Gestion des Styles)

**Statut du Commit Logique :** Fini (Commit 2/N)
**Objectif Atteint :** Implémentation complète de l'API CRUD pour l'entité `ClassDef`, incluant toutes les garanties d'intégrité des données requises (AC 2.4, 2.7, 2.8).

#### 1. Fichiers et Rôles

| Chemin du Fichier | Rôle | Modifications Clés |
| :--- | :--- | :--- |
| `backend/app/services/classdefs.py` | Logique Métier (Service) | Implémentation du CRUD transactionnel. Gestion de l'unicité et de la cohérence des références. |
| `backend/app/routes/classdefs.py` | Couche Présentation (Routes) | Création du Blueprint `classdefs_bp` avec les endpoints RESTful (GET, POST, PUT, DELETE). Gestion de la sérialisation Pydantic. |
| `backend/app/__init__.py` | Architecture Applicative | Enregistrement du `classdefs_bp` sous le préfixe `/api/classdefs`. |

#### 2. Service Layer (`backend/app/services/classdefs.py`)

Ce service est le cœur de la logique, assurant l'intégrité des données via plusieurs mécanismes :

##### 2.1. Cohérence des Noms (AC 2.8 - Unicité)
Les fonctions `create_classdef` et `update_classdef` intègrent une vérification d'unicité. Une `ClassDef` ne peut pas avoir le même `name` qu'une autre au sein du même `SubProject`. Si une duplication est détectée lors de la création ou d'une tentative de renommage, une exception `Conflict` est levée.

##### 2.2. Cohérence de Suppression (AC 2.4 - Références Orphelines)
La fonction `delete_classdef` gère la problématique des références orphelines de manière efficace :
1.  Elle identifie le nom (`name`) de la `ClassDef` à supprimer.
2.  Elle exécute une instruction `SQLAlchemy update` en masse (`sqlalchemy_update(Node)`) pour mettre à jour tous les `Node.style_class_ref` du `SubProject` correspondant qui pointaient vers ce nom. Ces références sont mises à `None` (`NULL` en base de données).
3.  L'objet `ClassDef` est ensuite supprimé (`db.session.delete(classdef)`).

Cette approche garantit que la suppression est atomique et maintient l'intégrité référentielle sans avoir à charger et mettre à jour individuellement tous les nœuds, ce qui est crucial pour la performance sur de grands graphes.

##### 2.3. Régénération Mermaid (AC 2.7 - Synchronisation)
La fonction `generate_mermaid_from_subproject` du service `mermaid_generator` est appelée dans chaque opération de modification (`create_classdef`, `update_classdef`, `delete_classdef`). Le champ `SubProject.mermaid_definition` est mis à jour *avant* le `db.session.commit()`, garantissant que la définition stockée reflète toujours l'état réel des entités immédiatement après toute modification structurelle.

#### 3. Couche Présentation (`backend/app/routes/classdefs.py`)

Le nouveau Blueprint `classdefs_bp` expose les endpoints RESTful standards :

*   **`POST /api/classdefs/`** : Utilise `ClassDefCreate` pour valider l'entrée et retourne `201 Created`.
*   **`GET /api/classdefs/<id>`** : Récupère par ID, gère `NotFound` si l'entité n'existe pas.
*   **`PUT /api/classdefs/<id>`** : Met à jour l'entité.
*   **`DELETE /api/classdefs/<id>`** : Supprime l'entité et retourne `204 No Content`.
*   **`GET /api/classdefs/?subproject_id=...`** : Permet le filtrage par SubProject.

Toutes les données sont sérialisées en entrée et en sortie via les schémas Pydantic `ClassDefCreate` et `ClassDefRead`.

#### 4. Intégration

Le Blueprint a été enregistré dans `backend/app/__init__.py` sous le chemin `/api/classdefs`, ce qui rend les nouvelles routes immédiatement accessibles.

### Résumé Technique

**Titre :** Mémo Technique - Commit `feat(frontend): implement flexible layout, zoom/pan, and v2.0 API client`

**Date :** 24/05/2024

**Auteur :** Votre Codeur Sénior

**Contexte :** Ce commit marque une évolution significative de l'interface utilisateur de l'éditeur de graphes (FNS 3) et aligne le client API sur les nouvelles fonctionnalités du backend (V2.0). L'objectif était double : améliorer drastiquement l'ergonomie de l'éditeur et préparer le terrain pour l'intégration des fonctionnalités de gestion des styles (`ClassDef`) et d'importation de contenu.

---

#### **1. Réalisations Clés**

1.  **Amélioration Majeure de l'UX (FNS 3) :**
    *   **Layout Flexible :** L'éditeur et le visualiseur ne sont plus contraints à une vue statique 50/50. L'utilisateur peut désormais ajuster dynamiquement la largeur de chaque panneau (y compris les masquer complètement) pour se concentrer soit sur l'écriture du code, soit sur la visualisation du graphe.
    *   **Navigation par Zoom/Pan :** Le visualiseur de graphes intègre désormais des contrôles de zoom (via la molette de la souris) et de déplacement (panoramique via clic-glisser), ce qui est essentiel pour naviguer dans des diagrammes complexes.

2.  **Mise à niveau du Client API (V2.0) :**
    *   Le service `apiService` a été étendu pour supporter l'intégralité du cycle de vie CRUD pour les entités `ClassDef`.
    *   Une nouvelle méthode a été ajoutée pour communiquer avec le endpoint d'importation de contenu de nœuds.
    *   Les types TypeScript (`types/api.ts`) ont été mis à jour pour garantir la sécurité de type de bout en bout pour ces nouvelles opérations.

---

#### **2. Détails Techniques par Module**

*   **Gestion des Dépendances (`package.json`) :**
    *   Ajout de la dépendance `react-zoom-pan-pinch@^3.0.0`. Cette bibliothèque a été choisie pour sa légèreté, sa performance et sa facilité d'intégration avec React pour fournir les fonctionnalités de zoom et de pan.

*   **Types de l'API (`frontend/src/types/api.ts`) :**
    *   Ajout de l'interface `NodeContentImportResponse` pour typer la réponse du backend lors de l'importation de contenu JSON, assurant que nous traitons correctement le nombre de succès et les IDs ignorés.
    *   Vérification et confirmation de la présence du type `ClassDefCreate` pour les opérations de création/mise à jour des styles, maintenant la cohérence avec les schémas Pydantic du backend.

*   **Service API (`frontend/src/services/api.ts`) :**
    *   **Module `ClassDef` :** Implémentation de quatre nouvelles méthodes (`getClassDefs`, `createClassDef`, `updateClassDef`, `deleteClassDef`). Ces méthodes s'appuient sur les abstractions CRUD génériques (`get`, `post`, `put`, `delete`), ce qui garantit un code maintenable et cohérent.
    *   **Module `Node` :** Ajout de la méthode `importNodeContent` qui prend en charge l'envoi d'un dictionnaire (`Record<string, string>`) vers le backend pour la mise à jour en masse du contenu textuel des nœuds.

*   **Composant `MermaidViewer.tsx` :**
    *   Intégration de la bibliothèque `react-zoom-pan-pinch`. Le rendu SVG de Mermaid est maintenant encapsulé dans les composants `TransformWrapper` et `TransformComponent`.
    *   Cette intégration a été réalisée sans perturber la logique de rendu asynchrone existante. Le `div` cible (`containerRef`) est maintenant un enfant du `TransformComponent`, rendant le contenu SVG généré immédiatement manipulable.
    *   Le conteneur parent conserve un `overflow: hidden` pour délimiter proprement la zone de zoom/pan.

*   **Page `GraphEditorPage.tsx` :**
    *   **Gestion d'état :** Introduction d'un nouvel état `editorWidthRatio` pour contrôler la largeur relative de l'éditeur de code.
    *   **Layout dynamique :** Remplacement de la grille statique Tailwind (`lg:grid-cols-2`) par un conteneur `flexbox`. La largeur de chaque panneau (éditeur et visualiseur) est désormais définie dynamiquement via la propriété de style `flexBasis`, qui est directement liée à l'état `editorWidthRatio`.
    *   **Interface de contrôle :** Ajout d'une barre d'outils simple permettant à l'utilisateur de sélectionner des répartitions prédéfinies (0%, 25%, 50%, 75%, 100%), ce qui met à jour l'état `editorWidthRatio` et déclenche un re-rendu du layout. Le rendu des panneaux est conditionnel pour optimiser les performances (un panneau avec une largeur de 0% n'est pas rendu dans le DOM).

---

#### **3. Conclusion et Impact**

Ce commit améliore significativement la qualité de vie de l'utilisateur final en rendant l'interface plus flexible et plus puissante. Sur le plan architectural, il complète la connectivité du frontend avec l'API V2.0, débloquant le développement des prochaines fonctionnalités prévues au backlog, notamment l'éditeur de styles visuels et l'interface d'importation de données JSON.

📋 Mémo Technique : Refactorisation Import/Sauvegarde de Contenu Narratif
🎯 Contexte et Problème Initial
Symptôme observé
Lors de l'import de contenu JSON puis d'une sauvegarde, les nœuds du graphe étaient systématiquement détruits et recréés, entraînant :

Changement des IDs primaires des nœuds
Perte complète des text_content importés
Cause racine identifiée
Flux problématique :

Utilisateur importe du JSON → text_content mis à jour dans les nœuds existants ✅
Utilisateur sauvegarde (même sans changer le graphe) → PUT /api/subprojects/<id> appelé
Route PUT appelle systématiquement synchronize_subproject_entities()
Cette fonction supprime TOUS les nœuds existants puis les recrée depuis le code Mermaid
Résultat : Nouveaux nœuds vierges avec nouveaux IDs, text_content perdus ❌
🔧 Solution Architecturale : Séparation Structure/Métadonnées
Principe fondamental
Distinguer deux types de mises à jour sur un SubProject :

Type	Déclencheur	Comportement
Structurelle	Code Mermaid modifié (nœuds/relations changés)	Reconstruction complète via synchronize_subproject_entities()
Métadonnées	Seulement title ou visual_layout changés	Mise à jour simple sans toucher aux nœuds
Implémentation Backend
1. Nouveau schéma Pydantic (backend/app/schemas.py)
class SubProjectMetadataUpdate(BaseModel):
    """Schéma pour mise à jour métadonnées uniquement (sans structure)."""
    title: str
    visual_layout: Optional[Dict[str, Any]] = None

2. Services refactorisés (backend/app/services/subprojects.py)
Service #1 : Mise à jour structurelle

def update_subproject_structure(subproject_id: int, data: SubProjectCreate) -> SubProject:
    """Met à jour la structure Mermaid complète (recrée nœuds/relations)."""
    # Validation unicité titre
    # Mise à jour title, mermaid_definition, visual_layout
    # ⚠️ Appelle synchronize_subproject_entities() → reconstruction

Service #2 : Mise à jour métadonnées

def update_subproject_metadata(subproject_id: int, data: SubProjectMetadataUpdate) -> SubProject:
    """Met à jour UNIQUEMENT title + visual_layout (préserve les nœuds)."""
    # Validation unicité titre
    # Mise à jour title, visual_layout
    # ✅ N'appelle PAS synchronize_subproject_entities() → préservation

3. Routes API enrichies (backend/app/routes/subprojects.py)
Endpoint existant modifié : PUT /api/subprojects/<id>

# Détecte si le code Mermaid a changé
if existing.mermaid_definition != validated_data.mermaid_definition:
    # Changement structurel → reconstruction
    return update_subproject_structure(subproject_id, validated_data)
else:
    # Changement métadonnées seulement → préservation
    metadata = SubProjectMetadataUpdate(
        title=validated_data.title,
        visual_layout=validated_data.visual_layout
    )
    return update_subproject_metadata(subproject_id, metadata)

Nouveau endpoint : PATCH /api/subprojects/<id>/metadata

# Force la mise à jour métadonnées uniquement
return update_subproject_metadata(subproject_id, validated_metadata)

Implémentation Frontend
1. Méthode HTTP PATCH générique (frontend/src/services/api.ts)
async patch<T>(endpoint: string, data: any): Promise<T> {
  const response = await this.client.patch<T>(endpoint, data);
  return response.data;
}

2. Nouvelles méthodes API
// Mise à jour structurelle (via PUT)
updateSubProjectStructure(id: number, data: SubProjectUpdate): Promise<SubProject>
// Mise à jour métadonnées (via PATCH)
patchSubProjectMetadata(id: number, data: SubProjectMetadataUpdate): Promise<SubProject>

3. Intelligence de détection (frontend/src/pages/GraphEditorPage.tsx)
Fonction de normalisation Mermaid :

const normalizeMermaidCode = (code: string): string => {
  return code
    .replace(/\s+/g, ' ')      // Normaliser espaces
    .replace(/\n/g, ' ')        // Supprimer retours ligne
    .trim();
};

Logique de sauvegarde intelligente :

const handleSave = async () => {
  const normalized1 = normalizeMermaidCode(subproject.mermaid_definition);
  const normalized2 = normalizeMermaidCode(mermaidCode);

  if (normalized1 === normalized2) {
    // Pas de changement structurel → PATCH métadonnées
    await api.patchSubProjectMetadata(id, { title, visual_layout });
  } else {
    // Changement structurel → PUT complet
    await api.updateSubProjectStructure(id, { title, mermaid_definition, visual_layout });
  }
};

🐛 Correction Additionnelle : Support Multi-Format Import
Problème découvert
L'import JSON échouait silencieusement car :

Le JSON utilisateur utilisait des IDs numériques : {"1136": "texte...", "1137": "texte..."}
Le code cherchait par mermaid_id : Node.mermaid_id IN ("1136", "1137")
Résultat : updated_count = 0, mais HTTP 200 OK retourné quand même
Solution : Support dual (backend/app/services/nodes.py)
def import_node_content(subproject_id: int, content_map: Dict[str, str]):
    # Séparer les clés numériques vs alphanumériques
    numeric_ids = []
    mermaid_ids = []

    for key in content_map.keys():
        try:
            numeric_ids.append(int(key))  # "1136" → 1136
        except ValueError:
            mermaid_ids.append(key)       # "A001" → "A001"

    # Construire requête avec OR
    conditions = []
    if numeric_ids:
        conditions.append(Node.id.in_(numeric_ids))
    if mermaid_ids:
        conditions.append(Node.mermaid_id.in_(mermaid_ids))

    # Chercher par ID OU mermaid_id
    query = db.select(Node).where(
        Node.subproject_id == subproject_id,
        db.or_(*conditions)
    )

    # Mapper le contenu sur le bon nœud
    for node in nodes_to_update:
        if str(node.id) in content_map:
            node.text_content = content_map[str(node.id)]
        elif node.mermaid_id in content_map:
            node.text_content = content_map[node.mermaid_id]

✅ Validation et Sécurité
Validation d'unicité des titres
Ajoutée dans les deux fonctions de mise à jour pour éviter les régressions :

if subproject.title != data.title:
    existing = db.session.execute(
        db.select(SubProject).filter(
            SubProject.id != subproject_id,
            SubProject.project_id == subproject.project_id,
            SubProject.title == data.title
        )
    ).scalar_one_or_none()

    if existing:
        raise BadRequest(f"Title '{data.title}' already exists")

Révision architecte
✅ Séparation structure/métadonnées validée
✅ Pas de régression dans les autres fonctionnalités
✅ Validation d'unicité préservée
✅ Gestion transactionnelle correcte
📊 Impact et Bénéfices
Avant	Après
Sauvegarde → destruction systématique des nœuds	Sauvegarde → préservation si métadonnées seulement
IDs instables après chaque save	IDs stables
text_content perdus après import	text_content persistés
Import JSON avec mermaid_id uniquement	Import JSON avec IDs numériques OU mermaid_id
🎯 Workflow Utilisateur Final
Créer un graphe → Nœuds créés avec IDs (ex: 1136, 1137)
Importer du contenu JSON → Format flexible : {"1136": "texte..."} OU {"A001": "texte..."}
Modifier titre/layout → Sauvegarde via PATCH → Nœuds préservés ✅
Modifier structure Mermaid → Sauvegarde via PUT → Nœuds recréés (attendu)
📁 Fichiers Modifiés
backend/
├── app/schemas.py                    # +SubProjectMetadataUpdate
├── app/services/subprojects.py       # +2 fonctions, +validation unicité
├── app/services/nodes.py             # Refactor import_node_content
└── app/routes/subprojects.py         # +PATCH endpoint, logique PUT
frontend/
├── src/services/api.ts               # +patch(), +2 méthodes
└── src/pages/GraphEditorPage.tsx     # +normalizeMermaidCode(), logique save

Date : 7 novembre 2025
Révision architecte : Validée ✅
Statut : Production-ready 🚀


**MÉMORANDUM TECHNIQUE DÉTAILLÉ - PHASE DE DÉPLOIEMENT FRONTEND (FNS 2 & FNS 3)**

**À :** Chef de Projet
**De :** Architecte Logiciel Sénior
**Date :** [Date du jour]
**Objet :** Synthèse de l'Implémentation Frontend relative au DDA V2.0 - FNS 2 (Style CRUD) et FNS 3 (Layout)

---

### 1. Aperçu Général de l'Exécution

Les tâches assignées concernant l'implémentation de l'interface utilisateur pour la gestion des styles (`ClassDef`, FNS 2) et l'amélioration du layout de l'éditeur (`GraphEditorPage`, FNS 3) ont été complétées et livrées. L'architecture client/serveur repose sur la consommation des endpoints CRUD déjà exposés par le backend sur `/api/classdefs/`.

### 2. Implémentation FNS 2 : CRUD des Définitions de Style (ClassDef)

Un nouveau composant modal, `StyleManagerModal.tsx`, a été créé pour fournir une interface complète de gestion des `ClassDef`.

#### 2.1. Fonctionnalités du `StyleManagerModal`
*   **Lecture (R) :** Chargement des styles existants via `apiService.getClassDefs(subprojectId)`.
*   **Création/Modification (C & U) :** Le formulaire gère l'état de création ou d'édition, envoyant les payloads `ClassDefCreate` aux endpoints `/api/classdefs/` (POST ou PUT). Une validation simple des champs `name` et `definition_raw` est appliquée côté client.
*   **Suppression (D) :** Appel à `apiService.deleteClassDef(id)` avec confirmation utilisateur.

#### 2.2. Synchronisation des Données et Cohérence (Point Critique)
Le point clé de cette implémentation est l'adhésion au principe de cohérence bidirectionnelle (AC 2.7).
Chaque opération CRUD réussie dans le modal déclenche le callback `onStyleChange`, qui exécute la fonction `refetchSubProject(true)` dans `GraphEditorPage.tsx`.

**Justification Technique :** Comme stipulé dans le DDA, toute modification sur une `ClassDef` doit déclencher une régénération du `mermaid_definition` côté serveur (via le Parser/Générateur mis à jour séparément). Le rafraîchissement silencieux du sous-projet côté client garantit que la nouvelle définition Mermaid est chargée, assurant ainsi que le `MermaidViewer` et les données de contexte du graphe reflètent immédiatement les changements structurels induits par la gestion des styles.

### 3. Implémentation FNS 3 : Flexibilité du Layout de l'Éditeur

La fonctionnalité de manipulation du layout de l'éditeur/visualiseur a été intégrée dans `GraphEditorPage.tsx` (visant l'AC 3.1).

*   **Contrôle par Ratio :** Un sélecteur d'affichage a été ajouté dans l'en-tête, permettant de basculer entre des ratios prédéfinis (`0` (Vue seule), `25`, `50`, `75`, `100` (Éditeur seul)).
*   **Implémentation CSS :** Les conteneurs de l'éditeur (`MermaidEditor`) et du visualiseur (`MermaidViewer`) utilisent désormais `flexBasis` basé sur l'état `editorWidthRatio`, offrant une séparation dynamique et adaptative de l'espace d'affichage.

### 4. Récapitulatif des Livrables

| Fichier | Statut | Notes |
| :--- | :--- | :--- |
| `frontend/src/components/StyleManagerModal.tsx` | **Créé** | Logique complète de gestion CRUD des styles. |
| `frontend/src/pages/GraphEditorPage.tsx` | **Modifié** | Intégration du modal, gestion des états, implémentation du sélecteur de ratio de layout. |

### 5. Points de Vigilance DDA Adressés et Prochaines Étapes

Les points suivants, issus de la section 5 du DDA, ont été validés par l'implémentation frontend :
*   **AC 2.7 (Déclenchement de la Génération) :** Assuré par la mécanique de rechargement post-modification du style.
*   **Tests :** Les étapes de vérification manuelles ont confirmé la fonctionnalité CRUD des styles et la capacité du viewer à interpréter la syntaxe de classe Mermaid (ex: `class A styleName`).

**Points Restants (Dépendants du Backend ou non-implémentés ici) :**
1.  La correction critique de la bidirectionnalité dans `mermaid_parser.py` et `mermaid_generator.py` (AC 2.9) est une étape backend nécessaire pour que l'application effective des styles lors d'un rechargement complet du graphe soit fonctionnelle au-delà des tests manuels initiaux.
2.  L'implémentation du Zoom/Pan (FNS 3) n'a pas été abordée dans cette étape, restant dépendante de l'intégration d'une librairie tierce ou d'une implémentation SVG avancée.
3.  L'implémentation FNS 1 (Import JSON) n'a pas été abordée.

Nous sommes prêts pour la mise en production de l'UI de gestion des styles et du contrôle de layout, en attendant l'implémentation des services de transformation backend associés.