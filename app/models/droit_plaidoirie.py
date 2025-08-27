
# app/models/droit_plaidoirie.py
from app import db
from datetime import datetime

class DroitPlaidoirie(db.Model):
    __tablename__ = 'droits_plaidoirie'
    
    plaidoirie_id = db.Column(db.Integer, primary_key=True)
    avocat_id = db.Column(db.Integer, db.ForeignKey('avocats.avocat_id'), nullable=False)
    numero_affaire = db.Column(db.String(50), nullable=False)
    nature_affaire = db.Column(db.String(200), nullable=False)
    tribunal = db.Column(db.String(100), nullable=False)
    montant = db.Column(db.Integer, nullable=False)  # Montant total des timbres
    agent_perception = db.Column(db.Integer, db.ForeignKey('users.id'))  # Assistant administratif
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.Enum('en_attente', 'valide', 'rejete', name='plaidoirie_status'), 
                      default='en_attente')
    valide_par = db.Column(db.Integer, db.ForeignKey('users.id'))  # Trésorier
    date_validation = db.Column(db.DateTime)
    commentaire = db.Column(db.Text)
    
    # Relations
    agent = db.relationship('User', foreign_keys=[agent_perception], backref='plaidoiries_saisies')
    validateur = db.relationship('User', foreign_keys=[valide_par], backref='plaidoiries_validees')
    
    def __repr__(self):
        return f'<DroitPlaidoirie {self.numero_affaire}>'
