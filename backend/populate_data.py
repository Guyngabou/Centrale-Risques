import requests
import json
import random
from datetime import date, timedelta

API_URL = "http://127.0.0.1:8000/api/v1"

def populate():
    # 1. Login
    login_data = {"username": "user_axa", "password": "123456"}
    resp = requests.post(f"{API_URL}/auth/login", json=login_data)
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 2. Sample Data
    noms = ["NANA", "TCHAMOU", "KAMGA", "FOTSO", "NGUE", "DIKONGUE", "EKOTTO", "MBIA", "ABESSOLO", "OWONA"]
    prenoms = ["Jean", "Paul", "Marie", "Anne", "Luc", "Sophie", "Pierre", "Claire", "Hervé", "Julie"]
    natures = ["RC", "DOMMAGES", "VOL ET INCENDIE", "BRIS DE GLACES"]
    roles = ["responsable", "partiel", "non_responsable"]
    couts = ["tres_faible", "faible", "moyenne", "elevee", "tres_elevee"]
    causes_pool = ["H", "V", "I"]

    for i in range(10):
        # Random dates
        survenance = date.today() - timedelta(days=random.randint(10, 300))
        dob = date(1970, 1, 1) + timedelta(days=random.randint(1000, 15000))

        payload = {
            "assure": {
                "type_assure": "P",
                "nom": noms[i % len(noms)],
                "prenom": prenoms[i % len(prenoms)],
                "date_naissance": dob.isoformat(),
                "lieu_naissance": "Douala",
                "sexe": random.choice(["M", "F"]),
                "type_document": "CNI",
                "numero_document": f"100000{i:02d}"
            },
            "sinistre": {
                "date_survenance": survenance.isoformat(),
                "lieu_survenance": "Yaoundé",
                "nature_sinistre": random.choice(natures),
                "branche": "AUTOMOBILE",
                "role_assure": random.choice(roles),
                "taux_responsabilite": random.randint(0, 100) if random.random() > 0.3 else 100,
                "classe_cout": random.choice(couts),
                "corporel": random.random() > 0.7,
                "deces": random.random() > 0.9,
                "vehicule_au_rebut": random.random() > 0.8
            },
            "causes": [
                {"cause_code": random.choice(causes_pool), "cause_principale": True}
            ]
        }

        print(f"Declaring sinistre {i+1} for {payload['assure']['nom']}...")
        r = requests.post(f"{API_URL}/sinistres", json=payload, headers=headers)
        if r.status_code == 200:
            print(f"Success!")
        else:
            print(f"Error: {r.text}")

if __name__ == "__main__":
    populate()
