# app/services/droit_plaidoirie.py
from app import db
from app.models.droit_plaidoirie import DroitPlaidoirie
from datetime import datetime

class DroitPlaidoirieService:
    """Service pour la gestion des droits de plaidoirie"""
    
    # Tarifs des timbres
    TARIFS_TIMBRES = {
        '2500': 2500,
        '5000': 5000,
        '10000': 10000
    }
    
    @classmethod
    def calculer_montant(cls, timbres_2500=0, timbres_5000=0, timbres_10000=0):
        """Calcule le montant total des timbres"""
        montant = (
            timbres_2500 * cls.TARIFS_TIMBRES['2500'] +
            timbres_5000 * cls.TARIFS_TIMBRES['5000'] +
            timbres_10000 * cls.TARIFS_TIMBRES['10000']
        )
        return montant
    
    @classmethod
    def creer_droit_plaidoirie(cls, timbres_2500, timbres_5000, timbres_10000, agent_id):
        """Crée un nouveau droit de plaidoirie"""
        try:
            # Validation des données
            if not any([timbres_2500, timbres_5000, timbres_10000]):
                raise ValueError("Au moins un timbre doit être sélectionné")
            
            # Calcul du montant
            montant_total = cls.calculer_montant(timbres_2500, timbres_5000, timbres_10000)
            
            # Création de l'objet
            droit = DroitPlaidoirie(
                montant=montant_total,
                timbres_2500=timbres_2500,
                timbres_5000=timbres_5000,
                timbres_10000=timbres_10000,
                agent_perception=agent_id,
                statut='en_attente'
            )
            
            db.session.add(droit)
            db.session.commit()
            
            return droit, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @classmethod
    def valider_droit(cls, plaidoirie_id, action, validateur_id, commentaire=None):
        """Valide ou rejette un droit de plaidoirie"""
        try:
            droit = DroitPlaidoirie.query.get(plaidoirie_id)
            if not droit:
                raise ValueError("Droit de plaidoirie introuvable")
            
            if droit.statut != 'en_attente':
                raise ValueError("Ce droit a déjà été traité")
            
            # Mise à jour du statut
            if action == 'valider':
                droit.statut = 'valide'
            elif action == 'rejeter':
                droit.statut = 'rejete'
                if not commentaire:
                    raise ValueError("Un commentaire est requis pour le rejet")
            else:
                raise ValueError("Action non valide")
            
            droit.valide_par = validateur_id
            droit.date_validation = datetime.utcnow()
            droit.commentaire = commentaire
            
            db.session.commit()
            
            return droit, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @classmethod
    def get_droits_par_statut(cls, statut=None, agent_id=None):
        """Récupère les droits par statut et/ou agent"""
        query = DroitPlaidoirie.query
        
        if statut:
            query = query.filter_by(statut=statut)
        
        if agent_id:
            query = query.filter_by(agent_perception=agent_id)
        
        return query.order_by(DroitPlaidoirie.date_creation.desc()).all()
    
    @classmethod
    def get_statistiques_agent(cls, agent_id):
        """Récupère les statistiques pour un agent"""
        stats = {
            'total': 0,
            'en_attente': 0,
            'valide': 0,
            'rejete': 0,
            'montant_total_valide': 0
        }
        
        droits = cls.get_droits_par_statut(agent_id=agent_id)
        
        stats['total'] = len(droits)
        
        for droit in droits:
            if droit.statut == 'en_attente':
                stats['en_attente'] += 1
            elif droit.statut == 'valide':
                stats['valide'] += 1
                stats['montant_total_valide'] += droit.montant
            elif droit.statut == 'rejete':
                stats['rejete'] += 1
        
        return stats