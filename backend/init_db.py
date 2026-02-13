from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models, auth_utils

def init_db():
    db = SessionLocal()
    
    # 1. Create ASAC Compagnie (ID 99)
    # We use a trick if the DB is empty to force IDs or just check existence
    asac = db.query(models.Compagnie).filter(models.Compagnie.compagnie_id == 99).first()
    if not asac:
        asac = models.Compagnie(compagnie_id=99, code_compagnie="ASAC", nom_compagnie="Association des Sociétés d'Assurance")
        db.add(asac)
        db.commit()
    
    # 2. Create a test Compagnie (ID 100)
    axa = db.query(models.Compagnie).filter(models.Compagnie.compagnie_id == 100).first()
    if not axa:
        axa = models.Compagnie(compagnie_id=100, code_compagnie="AXA", nom_compagnie="AXA Assurances")
        db.add(axa)
        db.commit()

    # 3. Create ASAC Admin User
    admin = db.query(models.Utilisateur).filter(models.Utilisateur.code_utilisateur == "admin_asac").first()
    if not admin:
        admin = models.Utilisateur(
            code_utilisateur="admin_asac",
            nom_utilisateur="Administrateur ASAC",
            password_utilisateur=auth_utils.get_password_hash("admin123"),
            compagnie_id=99,
            tel_utilisateur="600000001",
            email_utilisateur="admin@asac.cm",
            role_utilisateur ="Administrateur",
            statut_utilisateur ="Actif"
        )
        db.add(admin)
        db.commit()

    # 4. Create Compagnie User
    user_axa = db.query(models.Utilisateur).filter(models.Utilisateur.code_utilisateur == "user_axa").first()
    if not user_axa:
        user_axa = models.Utilisateur(
            code_utilisateur="user_axa",
            nom_utilisateur="Agent AXA",
            password_utilisateur=auth_utils.get_password_hash("123456"),
            compagnie_id=100,
            tel_utilisateur="600000002",
            email_utilisateur="agent@axa.cm",
            role_utilisateur ="Gestionnaire",
            statut_utilisateur ="Actif"
        )
        db.add(user_axa)
        db.commit()

    # 5. Create default Causes
    causes = [
        ("H", "Facteur Humain"),
        ("V", "Défaillances Véhicule"),
        ("I", "État Infrastructures")
    ]
    for code, lib in causes:
        if not db.query(models.Cause).filter(models.Cause.cause_code == code).first():
            db.add(models.Cause(cause_code=code, libelle=lib))
    db.commit()

    db.close()
    print("Base de données initialisée avec succès.")

if __name__ == "__main__":
    init_db()
