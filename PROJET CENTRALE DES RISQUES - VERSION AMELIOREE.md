# PROJET "CENTRALE DES RISQUES" - VERSION AMÉLIORÉE

## 1. OBJECTIFS ET PHILOSOPHIE
Ce projet, initié par l'**ASAC (Association des Sociétés d'Assurance du Cameroun)**, vise à mettre en place un **fichier centralisé des antécédents de sinistres**. 

### Finalités Exclusives
1. **Évaluation objective** du risque d'un assuré lors de la souscription, du renouvellement ou de la révision d'un contrat.
2. **Neutralité concurrentielle** : Un socle de données commun à toutes les compagnies.
3. **Aide à la décision** : Le score est indicatif et n'automatise pas le refus.

> [!IMPORTANT]
> **Conformité CIMA** : Le dispositif respecte la finalité unique, la proportionnalité des données (pas de montants, pas de dossiers médicaux) et le droit à rectification.

---

## 2. MÉTHODOLOGIE DU SCORE (0 - 100)
Le score est un outil **déterministe et explicable**, basé sur 5 piliers :

| Composante | Description | Points Max |
| :--- | :--- | :--- |
| **Fréquence** | Nombre de sinistres sur les 5 dernières années | 30 |
| **Responsabilité** | Niveau d'implication dans les sinistres | 25 |
| **Gravité** | Classe de coût (Très faible à Très élevée) | 20 |
| **Corporel** | Présence de dommages corporels ou décès | 15 |
| **Récidive** | Sinistre survenu dans les 12 derniers mois | 10 |

### Interprétation
- **0 – 20** : Risque Faible
- **21 – 40** : Risque Modéré
- **41 – 60** : Risque Élevé
- **61 – 80** : Risque Très Élevé
- **81 – 100** : Risque Critique

---

## 3. ARCHITECTURE TECHNIQUE (BACKEND)

### Schéma de Base de Données (SQL Server / PostgreSQL)
Le modèle est optimisé pour la performance et l'auditabilité.

```sql
-- Tables principales
CREATE TABLE compagnie (
    compagnie_id INT IDENTITY(100,1) PRIMARY KEY,
    code_compagnie VARCHAR(20) UNIQUE NOT NULL,
    nom_compagnie VARCHAR(150) NOT NULL
);

CREATE TABLE utilisateur (
    utilisateur_id INT IDENTITY(1,1) PRIMARY KEY,
    code_utilisateur VARCHAR(20) UNIQUE NOT NULL,
    compagnie_id INT NOT NULL,
    FOREIGN KEY (compagnie_id) REFERENCES compagnie(compagnie_id)
);

CREATE TABLE assure (
    assure_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    type_assure CHAR(1), -- P: Physique, M: Morale
    nom VARCHAR(100) NOT NULL,
    numero_document VARCHAR(30), -- CNI, NIU, etc.
    region VARCHAR(50)
);

CREATE TABLE sinistre (
    sinistre_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    assure_id BIGINT NOT NULL,
    date_survenance DATE NOT NULL,
    nature_sinistre VARCHAR(50), -- RC, Vol, etc.
    role_assure VARCHAR(50), -- responsable, partiel, non_responsable
    classe_cout VARCHAR(20),
    corporel BIT DEFAULT 0,
    deces BIT DEFAULT 0,
    FOREIGN KEY (assure_id) REFERENCES assure(assure_id)
);

CREATE TABLE consultation_log (
    log_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    assure_id BIGINT NOT NULL,
    compagnie_id INTEGER NOT NULL,
    utilisateur_id INT NOT NULL,
    motif_consultation VARCHAR(50),
    date_consultation DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### API REST (FastAPI)
L'API suit les standards **OpenAPI** pour une intégration facile par les services informatiques des compagnies.

- `POST /api/v1/sinistres` : Déclaration d'un nouveau sinistre (inclut les infos d'identification de l'assuré).
- `GET /api/v1/assures/score` : Recherche et récupération du score par critères d'identification (CNI, Nom/Prénom/Date de naissance).

#### Exemples de Requêtes

**Consultation du Score**
`GET /api/v1/assures/score?type_document=CNI&numero_document=123456789`
OU
`GET /api/v1/assures/score?nom=NANA&prenom=JEAN&date_naissance=1980-01-01`

**Déclaration de Sinistre**
```json
{
  "assure": {
    "type_assure": "P",
    "nom": "NANA",
    "prenom": "Jean",
    "numero_document": "123456789",
    "type_document": "CNI"
  },
  "sinistre": {
    "date_survenance": "2024-02-11",
    "nature_sinistre": "AUTOMOBILE",
    "role_assure": "responsable",
    "classe_cout": "moyenne"
  }
}
```

---

## 4. UX/UI ET FONCTIONNALITÉS
### Module Administration (ASAC)
- Gestion du référentiel (Compagnies / Utilisateurs).
- **Statistiques Globales** : Tableaux de bord sur la sinistralité nationale.
- **Audit** : Consultation exhaustive des logs.

### Module Compagnie
- **Saisie simplifiée** : Formulaire guidé (Identification Assuré -> Sinistre -> Détails Auto).
- **Consultation Score** : Recherche par identifiant officiel ou état-civil pour obtenir le score et le profil de risque.
- **Reporting interne** : Suivi des sinistres déclarés par la compagnie.

---

## 5. ENVIRONNEMENT
- **Backend** : Python 3.11+ / FastAPI.
- **Base de données** : SQL Server (Azure/Local).
- **Sécurité** : Authentification OAuth2 / JWT, chiffrement TLS, traçabilité totale.
