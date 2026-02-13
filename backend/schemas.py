from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import List, Optional, Any

# Authentication
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str # ASAC or COMPAGNIE
    code_compagnie: Optional[str] = None
    nom_compagnie: Optional[str] = None

# Insured
class AssureBase(BaseModel):
    type_assure: str = Field(..., pattern="^[PM]$")
    nom: str
    prenom: Optional[str] = None
    date_naissance: Optional[date] = None
    lieu_naissance: Optional[str] = None
    sexe: Optional[str] = Field(None, pattern="^[MFX]$")
    type_document: Optional[str] = None
    numero_document: Optional[str] = None
    region: Optional[str] = None

class AssureCreate(AssureBase):
    pass

class Assure(AssureBase):
    assure_id: int
    compagnie_id: int
    date_creation: datetime

    class Config:
        from_attributes = True

# Cause
class CauseBase(BaseModel):
    cause_code: str
    libelle: str

class SinistreCauseBase(BaseModel):
    cause_code: str
    cause_principale: bool = False

# Sinistre
class SinistreBase(BaseModel):
    date_survenance: date
    lieu_survenance: Optional[str] = None
    nature_sinistre: str
    branche: Optional[str] = "AUTOMOBILE"
    role_assure: str
    taux_responsabilite: Optional[float] = 0.0
    classe_cout: str
    corporel: bool = False
    deces: bool = False
    vehicule_au_rebut: bool = False

class SinistreCreate(BaseModel):
    assure: AssureBase
    sinistre: SinistreBase
    causes: Optional[List[SinistreCauseBase]] = []

class SinistreOut(SinistreBase):
    sinistre_id: int
    assure_id: int
    compagnie_id: int
    date_declaration: datetime

    class Config:
        from_attributes = True

# Score
class ScoreDetail(BaseModel):
    frequence: int
    responsabilite: int
    gravite: int
    corporel: int
    recidive: int

class ScoreResult(BaseModel):
    assure_id: Optional[int] = None
    nom: str
    prenom: Optional[str] = None
    score: int
    classe_risque: str
    detail: ScoreDetail
    date_calcul: datetime

# Admin
class CompagnieBase(BaseModel):
    code_compagnie: str
    nom_compagnie: str

class CompagnieCreate(CompagnieBase):
    pass

class Compagnie(CompagnieBase):
    compagnie_id: int
    date_creation: datetime

    class Config:
        from_attributes = True

class UtilisateurBase(BaseModel):
    code_utilisateur: str
    nom_utilisateur: str
    compagnie_id: int
    tel_utilisateur: str
    email_utilisateur: EmailStr
    role_utilisateur: str
    statut_utilisateur: str

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str

class Utilisateur(UtilisateurBase):
    utilisateur_id: int
    date_creation: datetime

    class Config:
        from_attributes = True
