
# app/models/cotisation.py
from app import db
from datetime import datetime

class Cotisation(db.Model):
    __tablename__ = 'cotisations'
    
    cotisation_id = db.Column(db.Integer, primary_key=True)
    avocat_id = db.Column(db.Integer, db.ForeignKey('avocats.avocat_id'), nullable=False)
    annee_cotisation = db.Column(db.Integer, nullable=False)
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    d_echeance = db.Column(db.Date, nullable=False)  # Date d'échéance
    d_paiement = db.Column(db.Date)  # Date de paiement
    statut = db.Column(db.Enum('impaye', 'partiel', 'paye', 'en_retard', 
                              name='cotisation_status'), default='impaye')
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    mode_paiement = db.Column(db.String(50))
    reference_paiement = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Cotisation {self.annee_cotisation} - Avocat {self.avocat_id}>'
