UTILISE LE SCHEma ci après pour compléter l'interface de saisie des sinistres.
on doit saisir l'assuré, le sinistre, et la ou les causes du sinistres.

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
'''
