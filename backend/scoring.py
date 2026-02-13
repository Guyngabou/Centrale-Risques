from datetime import date, datetime, timedelta
from typing import List
from models import Sinistre

def calcul_score(sinistres: List[Sinistre]) -> dict:
    score = 0
    detail = {
        "frequence": 0,
        "responsabilite": 0,
        "gravite": 0,
        "corporel": 0,
        "recidive": 0
    }

    if not sinistres:
        return {
            "score": 0,
            "classe_risque": "FAIBLE",
            "detail": detail
        }

    # 1. Fréquence des sinistres (Plafond 30) - 5 dernières années
    limit_5ans = date.today() - timedelta(days=5*365)
    sinistres_5ans = [s for s in sinistres if s.date_survenance >= limit_5ans]
    nb = len(sinistres_5ans)
    
    if nb == 1: detail["frequence"] = 8
    elif nb == 2: detail["frequence"] = 15
    elif nb == 3: detail["frequence"] = 22
    elif nb >= 4: detail["frequence"] = 30
    
    score += detail["frequence"]

    # 2. Responsabilité (Plafond 25)
    # On compte les sinistres où le rôle est responsable ou partiel
    nb_responsables = sum(1 for s in sinistres if s.role_assure in ("responsable", "partiel"))
    detail["responsabilite"] = min(nb_responsables * 7, 20)
    
    # Bonus si ≥ 3 sinistres responsables
    if nb_responsables >= 3:
        detail["responsabilite"] += 5
        
    score += detail["responsabilite"]

    # 3. Gravité financière (Plafond 20)
    # On prend le max de la classe de coût de TOUS les sinistres
    gravite_map = {
        "tres_faible": 2,
        "faible": 5,
        "moyenne": 10,
        "elevee": 15,
        "tres_elevee": 20
    }
    
    max_gravite = 0
    for s in sinistres:
        points = gravite_map.get(s.classe_cout, 0)
        if points > max_gravite:
            max_gravite = points
            
    detail["gravite"] = max_gravite
    score += detail["gravite"]

    # 4. Corporel / Décès (Plafond 15)
    has_deces = any(s.deces for s in sinistres)
    has_corporel = any(s.corporel for s in sinistres)
    
    if has_deces:
        detail["corporel"] = 15
    elif has_corporel:
        detail["corporel"] = 10
        
    score += detail["corporel"]

    # 5. Récidive récente (Plafond 10) - 12 derniers mois
    limit_12mois = date.today() - timedelta(days=365)
    if any(s.date_survenance >= limit_12mois for s in sinistres):
        detail["recidive"] = 10
        
    score += detail["recidive"]

    # Final score capped at 100
    final_score = min(score, 100)
    
    # Interpretation
    if final_score <= 20: classe = "FAIBLE"
    elif final_score <= 40: classe = "MODERE"
    elif final_score <= 60: classe = "ELEVE"
    elif final_score <= 80: classe = "TRES_ELEVE"
    else: classe = "CRITIQUE"

    return {
        "score": final_score,
        "classe_risque": classe,
        "detail": detail
    }
