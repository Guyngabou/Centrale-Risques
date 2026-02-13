from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, CHAR, BigInteger, DECIMAL
from sqlalchemy.dialects.mssql import BIT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Compagnie(Base):
    __tablename__ = "compagnie"
    compagnie_id = Column(Integer, primary_key=True, index=True)
    code_compagnie = Column(String(20), unique=True, nullable=False)
    nom_compagnie = Column(String(150), nullable=False)
    date_creation = Column(DateTime, default=func.now())
    
    utilisateurs = relationship("Utilisateur", back_populates="compagnie")
    sinistres = relationship("Sinistre", back_populates="compagnie")
    assures = relationship("Assure", back_populates="compagnie")

class Utilisateur(Base):
    __tablename__ = "utilisateur"
    utilisateur_id = Column(Integer, primary_key=True, index=True)
    code_utilisateur = Column(String(20), unique=True, nullable=False)
    nom_utilisateur = Column(String(150), nullable=False)
    password_utilisateur = Column(String(255), nullable=False)  # Hashed password
    compagnie_id = Column(Integer, ForeignKey("compagnie.compagnie_id"), nullable=False)
    tel_utilisateur = Column(String(20), unique=True, nullable=False)
    email_utilisateur = Column(String(50), nullable=False)
    role_utilisateur = Column(String(20), nullable=False)
    statut_utilisateur = Column(String(20), nullable=False)
    date_creation = Column(DateTime, default=func.now())
    
    compagnie = relationship("Compagnie", back_populates="utilisateurs")
    sinistres = relationship("Sinistre", back_populates="declarateur")

class Assure(Base):
    __tablename__ = "assure"
    assure_id = Column(BigInteger, primary_key=True, index=True)
    compagnie_id = Column(Integer, ForeignKey("compagnie.compagnie_id"), nullable=False)
    type_assure = Column(CHAR(1), nullable=False) # P or M
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100))
    date_naissance = Column(Date)
    lieu_naissance = Column(String(50))
    sexe = Column(CHAR(1))
    type_document = Column(String(20))
    numero_document = Column(String(30))
    region = Column(String(50))
    date_creation = Column(DateTime, default=func.now())
    utilisateur_id = Column(Integer, ForeignKey("utilisateur.utilisateur_id"))
    
    compagnie = relationship("Compagnie", back_populates="assures")
    sinistres = relationship("Sinistre", back_populates="assure")

class Sinistre(Base):
    __tablename__ = "sinistre"
    sinistre_id = Column(BigInteger, primary_key=True, index=True)
    assure_id = Column(BigInteger, ForeignKey("assure.assure_id"), nullable=False)
    compagnie_id = Column(Integer, ForeignKey("compagnie.compagnie_id"), nullable=False)
    utilisateur_id = Column(Integer, ForeignKey("utilisateur.utilisateur_id"), nullable=False)
    date_survenance = Column(Date, nullable=False)
    lieu_survenance = Column(String(50))
    nature_sinistre = Column(String(50))
    branche = Column(String(50))
    role_assure = Column(String(50)) # responsable, partiel, non_responsable
    taux_responsabilite = Column(DECIMAL(5, 2))
    classe_cout = Column(String(20))
    corporel = Column(Boolean, default=False)
    deces = Column(Boolean, default=False)
    vehicule_au_rebut = Column(Boolean, default=False)
    date_declaration = Column(DateTime, default=func.now())
    
    assure = relationship("Assure", back_populates="sinistres")
    compagnie = relationship("Compagnie", back_populates="sinistres")
    declarateur = relationship("Utilisateur", back_populates="sinistres")
    causes = relationship("SinistreCause", back_populates="sinistre")

class Cause(Base):
    __tablename__ = "cause"
    cause_code = Column(String(20), primary_key=True)
    libelle = Column(String(100))

class SinistreCause(Base):
    __tablename__ = "sinistre_cause"
    sinistre_id = Column(BigInteger, ForeignKey("sinistre.sinistre_id"), primary_key=True)
    cause_code = Column(String(20), ForeignKey("cause.cause_code"), primary_key=True)
    cause_principale = Column(Boolean, default=False)
    
    sinistre = relationship("Sinistre", back_populates="causes")

class ConsultationLog(Base):
    __tablename__ = "consultation_log"
    log_id = Column(BigInteger, primary_key=True, index=True)
    assure_id = Column(BigInteger, nullable=False)
    compagnie_id = Column(Integer, nullable=False)
    utilisateur_id = Column(Integer, nullable=False)
    motif_consultation = Column(String(50))
    date_consultation = Column(DateTime, default=func.now())
    adresse_ip = Column(String(45))
