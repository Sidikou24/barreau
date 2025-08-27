
# app/models/assistance_juridique.py
from app import db
from datetime import datetime

class AssistanceJuridique(db.Model):
    __tablename__ = 'assistance_juridique'
    
    assistance_id = db.Column(db.Integer, primary_key=True)
    date_reception_demande = db.Column(db.Date, nullable=False)
    date_demande = db.Column(db.Date, nullable=False)
    numero_demande = db.Column(db.String(50), nullable=False, unique=True)
    nature_demande = db.Column(db.String(200), nullable=False)
    nom_demandeur = db.Column(db.String(200), nullable=False)
    agent_reception = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    avocat_id = db.Column(db.Integer, db.ForeignKey('avocats.avocat_id'))
    montant_alloue = db.Column(db.Numeric(10, 2))
    statut = db.Column(db.Enum('en_attente', 'assigne', 'en_cours', 'termine', 'annule', 
                              name='assistance_status'), default='en_attente')
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    commentaire = db.Column(db.Text)
    
    # Relations
    agent = db.relationship('User', backref='assistances_recues')
    
    def __repr__(self):
        return f'<AssistanceJuridique {self.numero_demande}>'
