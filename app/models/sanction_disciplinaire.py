
# app/models/sanction_disciplinaire.py
from app import db
from datetime import datetime

class SanctionDisciplinaire(db.Model):
    __tablename__ = 'sanctions_disciplinaires'
    
    sanction_id = db.Column(db.Integer, primary_key=True)
    avocat_id = db.Column(db.Integer, db.ForeignKey('avocats.avocat_id'), nullable=False)
    numero_decision = db.Column(db.String(50), nullable=False, unique=True)
    date_sanction = db.Column(db.Date, nullable=False)
    type_sanction = db.Column(db.Enum('avertissement', 'blame', 'suspension', 
                                     'radiation_temporaire', 'radiation_definitive', 
                                     name='sanction_type'), nullable=False)
    motif_sanction = db.Column(db.Text, nullable=False)
    duree_sanction = db.Column(db.Integer)  # Durée en jours pour suspension
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.Enum('active', 'levee', 'expiree', name='sanction_status'), 
                      default='active')
    date_levee = db.Column(db.Date)
    
    def __repr__(self):
        return f'<Sanction {self.numero_decision}>'
