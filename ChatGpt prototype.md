
* ✅ **Base de données SQL** (SQL Server compatible)
* ✅ **API REST FastAPI** (simple, lisible, auditable)
* ✅ **Calcul du score officiel conforme à la méthodologie**
* ✅ **Journalisation automatique des consultations**



---

# 🧱 1️⃣ BASE DE DONNÉES (SQL – VERSION FINALE)

```markdown
👉 Compatible **PostgreSQL / SQL Server** (syntaxe standard).

### `schema.sql`
```

```sql
CREATE DATABASE RISQUESAGG;
GO
USE RISQUESAGG;
GO

-- COMPAGNIE
CREATE TABLE compagnie (
    compagnie_id INT IDENTITY(100,1) PRIMARY KEY,
    code_compagnie VARCHAR(20) UNIQUE NOT NULL,
    nom_compagnie VARCHAR(150) NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP   
);

-- UTILISATEUR
CREATE TABLE utilisateur (
    utilisateur_id INT IDENTITY(1,1) PRIMARY KEY,
    code_utilisateur VARCHAR(20) UNIQUE NOT NULL,
    nom_utilisateur VARCHAR(150) NOT NULL,
    compagnie_id INT NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    tel_utilisateur VARCHAR(20) NOT NULL,
    email_utilisateur VARCHAR(50) NOT NULL,
    role_utilisateur VARCHAR(20) NOT NULL DEFAULT 'consultant', -- {administrateur, gestionnaire, consultant}
    statut_utilisateur VARCHAR(20) NOT NULL DEFAULT 'actif', -- {actif, inactif}
    password_utilisateur VARCHAR(20) NOT NULL, -- hash du mot de passe 
    FOREIGN KEY (compagnie_id) REFERENCES compagnie(compagnie_id)
);
ADD CONSTRAINT UQ_utilisateur_telephone UNIQUE (tel_utilisateur);

-- ASSURE
CREATE TABLE assure (
    assure_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    compagnie_id INTEGER NOT NULL,
    type_assure CHAR(1) NOT NULL, -- {P: Personne physique, M: Personne morale
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100),
    date_naissance DATE,
    Lieu_naissance VARCHAR(50),
    sexe CHAR(1), -- {M: Masculin, F: Féminin, X: Autre}
    type_document VARCHAR(20), -- {CNI, Passeport, NIU, RC, Carte de Séjour}
    numero_document VARCHAR(30),
    region VARCHAR(50),
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    utilisateur_id INT,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(utilisateur_id),
    FOREIGN KEY (compagnie_id) REFERENCES compagnie(compagnie_id)
);

CREATE UNIQUE NONCLUSTERED INDEX DOCUMENT_OFFICIEL_ASSURE 
ON [dbo].[assure](numero_document, type_document);

CREATE UNIQUE NONCLUSTERED INDEX IDENTIFIANT_ASSURE 
ON [dbo].[assure](nom, prenom, date_naissance, lieu_naissance, sexe);

-- SINISTRE
CREATE TABLE sinistre (
    sinistre_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    assure_id BIGINT NOT NULL,
    compagnie_id INTEGER NOT NULL,
    date_survenance DATE NOT NULL,
    Lieu_survenance VARCHAR(50),
    nature_sinistre VARCHAR(50),    -- {RC, DOMMAGES, VOL ET INCENDIE, DEFENSE ET RECOURS, HONORAIRES D'EXPERTS, BRIS DE GLACES}
    branche VARCHAR(50), -- {AUTOMOBILE, AUTRES BRANCHES}
    role_assure VARCHAR(50), -- {responsable, partiel, non_responsable}
    taux_responsabilite DECIMAL(5,2),
    classe_cout VARCHAR(20), -- { "tres_faible", "faible", "moyenne", "elevee","tres_elevee" }
    corporel BIT DEFAULT 0,
    deces BIT DEFAULT 0,
    vehicule_au_rebut BIT DEFAULT 0,
    date_declaration DATETIME DEFAULT CURRENT_TIMESTAMP,
    utilisateur_id INT NOT NULL,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(utilisateur_id),
    FOREIGN KEY (assure_id) REFERENCES assure(assure_id),
    FOREIGN KEY (compagnie_id) REFERENCES compagnie(compagnie_id)
);

-- CAUSE
CREATE TABLE cause (
    cause_code VARCHAR(20) PRIMARY KEY,
    libelle VARCHAR(100) -- {facteur_humain, defaillances_vehicule, etat_infrastructures}
);

-- SINISTRE_CAUSE
CREATE TABLE sinistre_cause (
    Sinistre_id BIGINT NOT NULL,
    cause_code VARCHAR(20),
    cause_principale BIT DEFAULT 0,
    PRIMARY KEY (Sinistre_id, cause_code),
    FOREIGN KEY (sinistre_id) REFERENCES sinistre(sinistre_id),
    FOREIGN KEY (cause_code) REFERENCES cause(cause_code)
);

-- LOG DES CONSULTATIONS
CREATE TABLE consultation_log (
    log_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    assure_id BIGINT NOT NULL,
    compagnie_id INTEGER NOT NULL,
    utilisateur_id INT NOT NULL,
    motif_consultation VARCHAR(50), -- {consultation pour souscription, declaration sinistre, consultation_statistique, Autres}
    date_consultation DATETIME DEFAULT CURRENT_TIMESTAMP,
    adresse_ip VARCHAR(45) -- format adresse ip v4 ou v6
);
```

## 🧮 Moteur de calcul du score

```python
# scoring.py
from datetime import date, timedelta

def calcul_score(sinistres):
    score = 0

    # 1. Fréquence (5 ans)
    nb = len(sinistres)
    if nb == 1: score += 8
    elif nb == 2: score += 15
    elif nb == 3: score += 22
    elif nb >= 4: score += 30

    # 2. Responsabilité
    responsables = sum(1 for s in sinistres if s.role_assure in ("responsable", "partiel"))
    score += min(responsables * 7, 25)

    # 3. Gravité
    gravite_map = {
        "tres_faible": 2,
        "faible": 5,
        "moyenne": 10,
        "elevee": 15,
        "tres_elevee": 20
    }
    score += max((gravite_map.get(s.classe_cout, 0) for s in sinistres), default=0)

    # 4. Corporel / décès
    if any(s.deces for s in sinistres):
        score += 15
    elif any(s.corporel for s in sinistres):
        score += 10

    # 5. Récidive récente
    recent = date.today() - timedelta(days=365)
    if any(s.date_survenance >= recent for s in sinistres):
        score += 10

    return min(score, 100)
```

---

## 🚀 API PRINCIPALE (prototype)

```python
# main.py
from fastapi import FastAPI, Depends, Request
from scoring import calcul_score

app = FastAPI(title="Fichier Central Sinistres")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

### 🔹 POST – Déclaration d’un sinistre (prototype)

```python
@app.post("/api/v1/sinistres")
def declarer_sinistre(data: dict, db: Session = Depends(get_db)):
    sin = Sinistre(**data["sinistre"])
    db.add(sin)
    db.commit()
    return {"status": "ACCEPTE", "sinistre_id": sin.sinistre_id}
```

---

### 🔹 GET – Consultation du score (prototype)

```python
@app.get("/api/v1/assures/{assure_id}/score")
def score_assure(
    assure_id: int,
    request: Request,
    compagnie_id: int,
    utilisateur: str,
    motif: str,
    db: Session = Depends(get_db)
):
    sinistres = db.query(Sinistre)\
        .filter(Sinistre.assure_id == assure_id)\
        .all()

    score = calcul_score(sinistres)

    # Log consultation
    db.execute(
        "INSERT INTO consultation_log "
        "(assure_id, compagnie_id, utilisateur, motif_consultation, adresse_ip) "
        "VALUES (:a, :c, :u, :m, :ip)",
        {
            "a": assure_id,
            "c": compagnie_id,
            "u": utilisateur,
            "m": motif,
            "ip": request.client.host
        }
    )
    db.commit()

    return {
        "assure_id": assure_id,
        "score": score,
        "classe_risque": (
            "FAIBLE" if score <= 20 else
            "MODERE" if score <= 40 else
            "ELEVE" if score <= 60 else
            "TRES_ELEVE" if score <= 80 else
            "CRITIQUE"
        )
    }
```

```

```

-