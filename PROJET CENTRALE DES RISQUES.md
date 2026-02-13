PROJET "CENTRALE DES RISQUES"
# OBJECTIFS
ce projet, initié par l'ASAC(Association des sociétés d'assurance du cameroun), dans le cadre de la gestion des risques, a pour but de mettre en place un **fichier centralisé des antécédents de sinistres**,

Ce dispositif a pour finalité exclusive :

> **l’évaluation objective et harmonisée du risque d’un assuré**,
> lors de la **souscription**, du **renouvellement** ou de la **révision d’un contrat**.

Le score constitue un **outil d’aide à la décision**, sans caractère automatique ni contraignant.
# FONCTIONNALITES
    il s'agit de permettre aux compagnies membres de l'association :
    - d'alimenter le fichier centralisé avec les sinistres survenus à leurs assurés
    - de consulter le fichier centralisé pour obtenir le score de risque d'un assuré.
    on gardera trace de toutes les consultations.
# UX/UI LE FRONTEND
    ## LE MODULE D'ADMINISTRATION
    il s'agit de permettre à l'utilisateur de niveau administrateur (Personnel de l'ASAC) de :
    - se connecter
    - créer, modifier, activer/désactiver les utilisateurs
    - creér, modifier, activer/désactiver   les compagnies
    - voir les consultations, tirer des rapports sur les logs des consultations
    - avoir un tableau de bord présentant les statistiques pertinentes sur les sinistres.
    ## LE MODULE COMPAGNIE
    Il s'agit de permettre à l'utilisateur de niveau compagnie de :
    - se connecter
    - consulter le score de risque d'un assuré
    - alimenter le fichier centralisé avec les sinistres survenus à leurs assurés
    - voir les consultations, tirer des rapports sur les logs des consultations (limitées à sa compagnie)
    - avoir un tableau de bord présentant les statistiques pertinentes sur les sinistres.
    ### Saisie d'un sinistre
        on renseignera les informations suivantes dans cet ordre :
        - informations sur l'assuré
        - informations sur le sinistre  
        - informations sur le véhicule si c'est la branche AUTOMOBILE
        - informations sur le conducteur si c'est la branche AUTOMOBILE
    ### Consultation du score
        on renseignera les informations sur l'assuré
         et in obtiendra en retour : 
         - le score de risque
    ## Tableau de bord
        les statistiques pertinentes sur les sinistres :
        - nombre de sinistres
        - Nombre de sinistres responsables
        - Nombre de sinistres non responsables
        - Nombre de sinistres corporels
        - Nombre de sinistres matériels                     
        présentés sous forme de graphiques
# LE BACKEND
    ## le schéma de la base de données
    ## le calcul du score de risque
    ## gestion des logs    
# OUTILS & ENVIRONNEMENT 
 ✅ **Base de données SQL** (SQL Server compatible)
* ✅ **API REST FastAPI** (simple, lisible, auditable)
* ✅ **Calcul du score officiel conforme à la méthodologie**
* ✅ **Journalisation automatique des consultations**
* ✅ **UX/UI moderne, professionnelle, Responsive**