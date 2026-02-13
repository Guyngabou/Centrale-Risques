import random
from datetime import date
from sqlalchemy.orm import Session
from database import SessionLocal
import models

def seed_sinistres():
    db = SessionLocal()
    try:
        # Get some existing data to link to
        assure = db.query(models.Assure).first()
        compagnie = db.query(models.Compagnie).first()
        user = db.query(models.Utilisateur).first()
        
        if not assure or not compagnie or not user:
            print("Missing prerequisite data (assure, compagnie, or user). Please add them first.")
            return

        natures = ["RC", "DOMMAGES", "BRIS DE GLACES", "VOL ET INCENDIE", "DEFENSE ET RECOURS"]
        causes = ["H", "I", "V"] # Updated to valid codes
        classes_cout = ["FAIBLE", "MOYEN", "ELEVE"]

        print(f"Adding 10 claims for January 2026 to Assure ID {assure.assure_id}...")

        for i in range(10):
            day = random.randint(1, 31)
            sinistre = models.Sinistre(
                assure_id=assure.assure_id,
                compagnie_id=compagnie.compagnie_id,
                utilisateur_id=user.utilisateur_id,
                date_survenance=date(2026, 1, day),
                nature_sinistre=random.choice(natures),
                branche="Auto",
                role_assure="responsable",
                taux_responsabilite=100.0,
                classe_cout=random.choice(classes_cout),
                corporel=random.choice([True, False]),
                deces=False
            )
            db.add(sinistre)
            db.flush() # Get the ID

            # Add a cause
            sinistre_cause = models.SinistreCause(
                sinistre_id=sinistre.sinistre_id,
                cause_code=random.choice(causes),
                cause_principale=True
            )
            db.add(sinistre_cause)

        db.commit()
        print("Successfully added 10 claims.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_sinistres()
