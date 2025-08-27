
# app/models/cabinet_avocat.py
from app import db
from datetime import datetime

# Table d'association pour les membres du cabinet
cabinet_membres = db.Table('cabinet_membres',
    db.Column('cabinet_id', db.Integer, db.ForeignKey('cabinets_avocat.cabinet_id'), primary_key=True),
    db.Column('avocat_id', db.Integer, db.ForeignKey('avocats.avocat_id'), primary_key=True)
)

class CabinetAvocat(db.Model):
    __tablename__ = 'cabinets_avocat'
    
    cabinet_id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    telephone = db.Column(db.String(20))
    adresse = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    membres = db.relationship('Avocat', secondary=cabinet_membres, back_populates='cabinets')
    
    def __repr__(self):
        return f'<Cabinet {self.nom}>'
