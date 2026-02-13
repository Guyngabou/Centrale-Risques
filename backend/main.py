from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, extract
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

import models, schemas, scoring, auth_utils
from database import engine, get_db

# Create tables (In production, use Alembic)
# ---- models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ASAC - Centrale des Risques")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Frontend Static Files
# Path is relative to the backend directory
frontend_path = "../frontend"
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def read_index():
    return FileResponse(f"{frontend_path}/index.html")

# Authentication dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth_utils.SECRET_KEY, algorithms=[auth_utils.ALGORITHM])
        if payload is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception

# Authentication Endpoints
@app.post("/api/v1/auth/login", response_model=schemas.Token)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.Utilisateur).filter(models.Utilisateur.code_utilisateur == request.username).first()
    if user:
        print("user found")
        print(user)
        print(request.password)
        print(user.password_utilisateur)
        print(auth_utils.verify_password(request.password, user.password_utilisateur))
    else:
        print("user not found")
    if not user or not auth_utils.verify_password(request.password, user.password_utilisateur):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    role = "ASAC" if user.compagnie_id == 99 else "COMPAGNIE"
    
    access_token = auth_utils.create_access_token(
        data={
            "sub": user.code_utilisateur, 
            "id": user.utilisateur_id, 
            "compagnie_id": user.compagnie_id, 
            "code_compagnie": user.compagnie.code_compagnie,
            "nom_compagnie": user.compagnie.nom_compagnie,
            "role": role
        }
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": role,
        "code_compagnie": user.compagnie.code_compagnie,
        "nom_compagnie": user.compagnie.nom_compagnie
    }

# Sinistre Endpoints
@app.post("/api/v1/sinistres", response_model=schemas.SinistreOut)
def declarer_sinistre(
    data: schemas.SinistreCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # 1. Handle Insured (Search or Create)
    assure_data = data.assure
    query = db.query(models.Assure)
    if assure_data.numero_document:
        query = query.filter(models.Assure.numero_document == assure_data.numero_document)
    else:
        query = query.filter(models.Assure.nom == assure_data.nom, models.Assure.prenom == assure_data.prenom, models.Assure.date_naissance == assure_data.date_naissance)
    
    assure = query.first()
    
    # Company/user from token
    compagnie_id = current_user.get("compagnie_id")
    utilisateur_id = current_user.get("id")
    
    if not assure:
        assure = models.Assure(**assure_data.dict(), compagnie_id=compagnie_id, utilisateur_id=utilisateur_id)
        db.add(assure)
        db.commit()
        db.refresh(assure)
    
    # 2. Create Sinistre
    sin_data = data.sinistre
    sinistre = models.Sinistre(
        **sin_data.dict(),
        assure_id=assure.assure_id,
        compagnie_id=compagnie_id,
        utilisateur_id=utilisateur_id
    )
    db.add(sinistre)
    db.commit()
    db.refresh(sinistre)

    # 3. Add Causes
    if data.causes:
        for cause_data in data.causes:
            sin_cause = models.SinistreCause(
                sinistre_id=sinistre.sinistre_id,
                cause_code=cause_data.cause_code,
                cause_principale=cause_data.cause_principale
            )
            db.add(sin_cause)
        db.commit()
    
    return sinistre

# Score Consultation
@app.get("/api/v1/assures/score", response_model=schemas.ScoreResult)
def consulter_score(
    request: Request,
    type_document: Optional[str] = None,
    numero_document: Optional[str] = None,
    nom: Optional[str] = None,
    prenom: Optional[str] = None,
    date_naissance: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(models.Assure)
    if numero_document:
        query = query.filter(models.Assure.numero_document == numero_document)
    elif nom and prenom:
        query = query.filter(models.Assure.nom == nom, models.Assure.prenom == prenom)
        if date_naissance:
            query = query.filter(models.Assure.date_naissance == date_naissance)
    else:
        raise HTTPException(status_code=400, detail="Critères d'identification insuffisants")
    
    assure = query.first()
    if not assure:
        # If insured not found, return a zero score (risk faible)
        dummy_score = scoring.calcul_score([])
        return {
            "nom": nom or "INCONNU",
            "prenom": prenom,
            "score": dummy_score["score"],
            "classe_risque": dummy_score["classe_risque"],
            "detail": dummy_score["detail"],
            "date_calcul": datetime.now()
        }
    
    # Found insured, calculate score
    sinistres = db.query(models.Sinistre).filter(models.Sinistre.assure_id == assure.assure_id).all()
    res = scoring.calcul_score(sinistres)
    
    # Log consultation
    log = models.ConsultationLog(
        assure_id=assure.assure_id,
        compagnie_id=current_user.get("compagnie_id"),
        utilisateur_id=current_user.get("id"),
        motif_consultation="Consultation Score",
        adresse_ip=request.client.host
    )
    db.add(log)
    db.commit()
    
    return {
        "assure_id": assure.assure_id,
        "nom": assure.nom,
        "prenom": assure.prenom,
        "score": res["score"],
        "classe_risque": res["classe_risque"],
        "detail": res["detail"],
        "date_calcul": datetime.now()
    }

# Admin Endpoints (Simple versions)
@app.get("/api/v1/admin/compagnies", response_model=List[schemas.Compagnie])
def get_compagnies(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(models.Compagnie).all()

@app.post("/api/v1/admin/compagnies", response_model=schemas.Compagnie)
def create_compagnie(
    comp: schemas.CompagnieCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_comp = models.Compagnie(**comp.dict())
    db.add(db_comp)
    db.commit()
    db.refresh(db_comp)
    return db_comp

@app.get("/api/v1/admin/utilisateurs", response_model=List[schemas.Utilisateur])
def get_users(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(models.Utilisateur).all()

@app.post("/api/v1/admin/utilisateurs", response_model=schemas.Utilisateur)
def create_user(
    user: schemas.UtilisateurCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    hashed_pwd = auth_utils.get_password_hash(user.mot_de_passe)
    db_user = models.Utilisateur(
        code_utilisateur=user.code_utilisateur,
        nom_utilisateur=user.nom_utilisateur,
        password_utilisateur=hashed_pwd,
        compagnie_id=user.compagnie_id,
        tel_utilisateur=user.tel_utilisateur,
        email_utilisateur=user.email_utilisateur,
        role_utilisateur=user.role_utilisateur,
        statut_utilisateur=user.statut_utilisateur
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/v1/admin/stats")
def get_stats(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    current_year = datetime.now().year
    
    # 1. Basics
    total_sinistres = db.query(models.Sinistre).count()
    total_assures = db.query(models.Assure).count()
    total_compagnies = db.query(models.Compagnie).count()
    sinistres_annee = db.query(models.Sinistre).filter(extract('year', models.Sinistre.date_survenance) == current_year).count()
    
    # 2. Ventilation Nature (Current Year)
    nature_stats = db.query(
        models.Sinistre.nature_sinistre, 
        func.count(models.Sinistre.sinistre_id)
    ).filter(extract('year', models.Sinistre.date_survenance) == current_year).group_by(models.Sinistre.nature_sinistre).all()
    print('nature-stats',nature_stats   )
    # 3. Ventilation Cause (Current Year)
    # Note: Using join with SinistreCause to get causes per claim
    cause_stats = db.query(
        models.SinistreCause.cause_code, 
        func.count(models.Sinistre.sinistre_id)
    ).join(models.Sinistre).filter(extract('year', models.Sinistre.date_survenance) == current_year).group_by(models.SinistreCause.cause_code).all()
    print('cause-stats',cause_stats)
    # 4. Ventilation Classe de Coût (Current Year)
    cout_stats = db.query(
        models.Sinistre.classe_cout, 
        func.count(models.Sinistre.sinistre_id)
    ).filter(extract('year', models.Sinistre.date_survenance) == current_year).group_by(models.Sinistre.classe_cout).all()
    print('cout-stats',cout_stats)
    # 5. Trend (Last 3 Years)
    trend_stats = db.query(
        extract('year', models.Sinistre.date_survenance).label('year'), 
        func.count(models.Sinistre.sinistre_id)
    ).filter(extract('year', models.Sinistre.date_survenance) >= current_year - 2)\
     .group_by(extract('year', models.Sinistre.date_survenance))\
     .order_by(extract('year', models.Sinistre.date_survenance)).all()
    print('trend-stats',trend_stats)
    return {
        "total_sinistres": total_sinistres,
        "total_assures": total_assures,
        "total_compagnies": total_compagnies,
        "sinistres_annee_en_cours": sinistres_annee,
        "current_year": current_year,
        "ventilation_nature": {row[0]: row[1] for row in nature_stats},
        "ventilation_cause": {row[0]: row[1] for row in cause_stats},
        "ventilation_cout": {row[0]: row[1] for row in cout_stats},
        "trend_3_ans": {int(row[0]): row[1] for row in trend_stats}
    }
