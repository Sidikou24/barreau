from app import db
from app.models.fond import Fond
from app.models.operation_fond import OperationFond
from datetime import datetime

class GestionFondService:
    @staticmethod
    def get_fonds():
        """Récupère tous les fonds avec leur montant actuel."""
        from sqlalchemy.orm import subqueryload
        return Fond.query.options(subqueryload(Fond.operations)).all()

    @staticmethod
    def crediter_fond(fond_id, provenance, montant, date_reception, commentaire=None, user_id=None):
        """Crédite un fond (sans validation nécessaire)."""
        fond = Fond.query.get(fond_id)
        if not fond:
            return None, "Fond non trouvé."

        # Conversion du montant en integer
        try:
            montant_int = int(montant)
        except (ValueError, TypeError):
            return None, "Montant invalide."

        # Mise à jour du montant du fond
        fond.montant += montant_int

        # Création de l'opération
        operation = OperationFond(
            fond_id=fond_id,
            type_operation="credit",
            montant=montant_int,
            provenance=provenance,
            date_reception=date_reception,
            date_creation=datetime.utcnow(),
            statut="valide",  # Pas de validation nécessaire pour un crédit
            user_id=user_id,
            commentaire=commentaire
        )
        db.session.add(operation)
        db.session.commit()

        return operation, None

    @staticmethod
    def debiter_fond(fond_id, motif, montant, date_depense, user_id=None):
        """Débite un fond (opération en attente de validation)."""
        fond = Fond.query.get(fond_id)
        if not fond:
            return None, "Fond non trouvé."
        
        # Conversion du montant en integer
        try:
            montant_int = int(montant)
        except (ValueError, TypeError):
            return None, "Montant invalide."
            
        if fond.montant < montant_int:
            return None, "Montant insuffisant dans le fond."

        # Création de l'opération en attente
        operation = OperationFond(
            fond_id=fond_id,
            type_operation="debit",
            montant=montant_int,
            motif=motif,
            date_depense=date_depense,
            date_creation=datetime.utcnow(),
            statut="en_attente",
            user_id=user_id
        )
        db.session.add(operation)
        db.session.commit()

        return operation, None

    @staticmethod
    def transférer_fond(fond_source_id, fond_destination_id, montant, user_id=None):
        """Transfère un montant entre deux fonds (opération en attente)."""
        fond_source = Fond.query.get(fond_source_id)
        fond_destination = Fond.query.get(fond_destination_id)

        if not fond_source or not fond_destination:
            return None, "Fond source ou destination non trouvé."
        
        # Conversion du montant en integer
        try:
            montant_int = int(montant)
        except (ValueError, TypeError):
            return None, "Montant invalide."
            
        if fond_source.montant < montant_int:
            return None, "Montant insuffisant dans le fond source."

        # Création de l'opération de transfert en attente
        operation = OperationFond(
            fond_id=fond_source_id,
            type_operation="transfert",
            montant=montant_int,
            fond_destination_id=fond_destination_id,
            date_creation=datetime.utcnow(),
            statut="en_attente",
            user_id=user_id
        )
        db.session.add(operation)
        db.session.commit()

        return operation, None

    @staticmethod
    def valider_operation(operation_id, action, motif_annulation=None, validateur_id=None):
        """Valide ou annule une opération en attente."""
        operation = OperationFond.query.get(operation_id)
        if not operation:
            return None, "Opération non trouvée."
        if operation.statut != "en_attente":
            return None, "Opération déjà traitée."

        if action == "valider":
            # Mise à jour du montant des fonds selon le type d'opération
            if operation.type_operation == "debit":
                fond = Fond.query.get(operation.fond_id)
                fond.montant -= operation.montant
            elif operation.type_operation == "transfert":
                fond_source = Fond.query.get(operation.fond_id)
                fond_destination = Fond.query.get(operation.fond_destination_id)
                fond_source.montant -= operation.montant
                fond_destination.montant += operation.montant

            operation.statut = "valide"
            operation.validateur_id = validateur_id
            operation.date_validation = datetime.utcnow()

        elif action == "annuler":
            operation.statut = "annule"
            operation.motif_annulation = motif_annulation
            operation.validateur_id = validateur_id
            operation.date_validation = datetime.utcnow()

        db.session.commit()
        return operation, None

    @staticmethod
    def get_operations_en_attente():
        """Récupère toutes les opérations en attente de validation."""
        return OperationFond.query.filter_by(statut="en_attente").all()
