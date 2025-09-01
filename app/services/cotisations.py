# app/services/cotisations.py
from app import db
from app.models.cotisation import Cotisation
from app.models.avocat import Avocat
from datetime import datetime
from sqlalchemy import func, and_

class CotisationService:
    
    @staticmethod
    def get_cotisations_par_annee():
        """Récupère les cotisations groupées par année avec statistiques"""
        cotisations = db.session.query(
            Cotisation.annee_cotisation,
            func.count(Cotisation.cotisation_id).label('total_avocats'),
            func.sum(Cotisation.montant).label('montant_total'),
            func.count(func.nullif(Cotisation.statut != 'impaye', False)).label('payes'),
            func.count(func.nullif(Cotisation.statut == 'impaye', False)).label('impayes')
        ).group_by(Cotisation.annee_cotisation).order_by(Cotisation.annee_cotisation.desc()).all()
        
        return [{
            'annee': cotisation.annee_cotisation,
            'total_avocats': cotisation.total_avocats,
            'montant_total': float(cotisation.montant_total) if cotisation.montant_total else 0,
            'payes': cotisation.payes,
            'impayes': cotisation.impayes
        } for cotisation in cotisations]
    
    @staticmethod
    def get_cotisation_par_annee(annee):
        """Récupère les détails d'une cotisation pour une année donnée"""
        cotisations = db.session.query(Cotisation, Avocat).join(
            Avocat, Cotisation.avocat_id == Avocat.avocat_id
        ).filter(Cotisation.annee_cotisation == annee).order_by(
            Avocat.nom, Avocat.prenom if hasattr(Avocat, 'prenom') else Avocat.nom
        ).all()
        
        return [{
            'cotisation_id': cotisation.cotisation_id,
            'avocat_id': avocat.avocat_id,
            'nom_complet': avocat.nom,
            'qualification': avocat.qualification,
            'montant': float(cotisation.montant),
            'statut': cotisation.statut,
            'd_echeance': cotisation.d_echeance.strftime('%Y-%m-%d'),
            'd_paiement': cotisation.d_paiement.strftime('%Y-%m-%d') if cotisation.d_paiement else None,
            'date_creation': cotisation.date_creation.strftime('%Y-%m-%d %H:%M')
        } for cotisation, avocat in cotisations]
    
    @staticmethod
    def lancer_cotisation_annuelle(annee, montant_stagiaire, montant_titulaire, d_echeance, lanceur_id):
        """Lance une nouvelle campagne de cotisation annuelle"""
        try:
            # Vérifier si la cotisation pour cette année existe déjà
            cotisation_existante = Cotisation.query.filter_by(annee_cotisation=annee).first()
            if cotisation_existante:
                return None, "Une cotisation pour cette année existe déjà."
            
            # Valider la date d'échéance
            try:
                date_echeance = datetime.strptime(d_echeance, '%Y-%m-%d').date()
                if date_echeance <= datetime.utcnow().date():
                    return None, "La date d'échéance doit être dans le futur."
            except ValueError:
                return None, "Format de date invalide. Utilisez le format YYYY-MM-DD."
            
            # Récupérer tous les avocats actifs
            avocats = Avocat.query.filter_by(statut='actif').all()
            if not avocats:
                return None, "Aucun avocat actif trouvé."
            
            cotisations_creees = []
            
            # Créer une cotisation pour chaque avocat
            for avocat in avocats:
                # Déterminer le montant selon la qualification
                if avocat.qualification == 'stagiaire':
                    montant = montant_stagiaire
                elif avocat.qualification in ['titulaire', 'conseil_ordre']:
                    montant = montant_titulaire
                else:
                    montant = montant_titulaire  # Par défaut
                
                cotisation = Cotisation(
                    avocat_id=avocat.avocat_id,
                    annee_cotisation=annee,
                    montant=montant,
                    d_echeance=date_echeance,
                    statut='impaye'
                )
                
                db.session.add(cotisation)
                cotisations_creees.append(cotisation)
            
            db.session.commit()
            
            return {
                'cotisations_creees': len(cotisations_creees),
                'annee': annee,
                'montant_stagiaire': montant_stagiaire,
                'montant_titulaire': montant_titulaire
            }, None
            
        except Exception as e:
            db.session.rollback()
            return None, f"Erreur lors de la création des cotisations : {str(e)}"
    
    @staticmethod
    def enregistrer_paiement_cotisation(avocat_id, annee_cotisation, comptable_id):
        """Enregistre le paiement d'une cotisation"""
        try:
            # Trouver la cotisation
            cotisation = Cotisation.query.filter_by(
                avocat_id=avocat_id, 
                annee_cotisation=annee_cotisation,
                statut='impaye'
            ).first()
            
            if not cotisation:
                return None, "Cotisation introuvable ou déjà payée."
            
            # Mettre à jour le statut
            cotisation.statut = 'paye'
            cotisation.d_paiement = datetime.utcnow().date()
            
            db.session.commit()
            
            return {
                'cotisation_id': cotisation.cotisation_id,
                'avocat_id': avocat_id,
                'montant': float(cotisation.montant),
                'annee': annee_cotisation
            }, None
            
        except Exception as e:
            db.session.rollback()
            return None, f"Erreur lors de l'enregistrement du paiement : {str(e)}"
    
    @staticmethod
    def get_cotisations_avocat(avocat_id):
        """Récupère toutes les cotisations d'un avocat"""
        cotisations = Cotisation.query.filter_by(
            avocat_id=avocat_id
        ).order_by(Cotisation.annee_cotisation.desc()).all()
        
        return [{
            'cotisation_id': cotisation.cotisation_id,
            'annee_cotisation': cotisation.annee_cotisation,
            'montant': float(cotisation.montant),
            'statut': cotisation.statut,
            'd_echeance': cotisation.d_echeance.strftime('%Y-%m-%d'),
            'd_paiement': cotisation.d_paiement.strftime('%Y-%m-%d') if cotisation.d_paiement else None,
            'en_retard': cotisation.d_echeance < datetime.utcnow().date() and cotisation.statut == 'impaye'
        } for cotisation in cotisations]
    
    @staticmethod
    def get_avocats_pour_selection():
        """Récupère la liste des avocats pour les dropdown avec recherche"""
        avocats = Avocat.query.filter_by(statut='actif').order_by(Avocat.nom).all()
        
        return [{
            'avocat_id': avocat.avocat_id,
            'nom_complet': avocat.nom,
            'qualification': avocat.qualification,
            'user_id': avocat.user_id
        } for avocat in avocats]