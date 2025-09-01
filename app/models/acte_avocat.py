
# app/models/acte_avocat.py
from app import db
from datetime import datetime


class ActeAvocat(db.Model):
    __tablename__ = 'actes_avocat'
    
    acte_id = db.Column(db.Integer, primary_key=True)
    avocat_id = db.Column(db.Integer, db.ForeignKey('avocats.avocat_id'), nullable=False)
    date_acte = db.Column(db.Date, nullable=False)
    date_depot = db.Column(db.Date, nullable=False)
    numero_acte = db.Column(db.String(50), nullable=False, unique=True)
    nature_acte = db.Column(db.String(200), nullable=False)
    identites_parties = db.Column(db.Text, nullable=False)
    nombre_pages = db.Column(db.Integer, nullable=False)
    agent_reception = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.Enum('recu', 'traite', 'archive', name='acte_status'), 
                      default='recu')
    
    # Relations
    agent = db.relationship('User', backref='actes_recus')

    def __repr__(self):
        return f'<ActeAvocat {self.numero_acte}>'
