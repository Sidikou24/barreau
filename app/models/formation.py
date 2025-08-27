
# app/models/formation.py
from app import db
from datetime import datetime

class Formation(db.Model):
    __tablename__ = 'formations'
    
    formation_id = db.Column(db.Integer, primary_key=True)
    avocat_id = db.Column(db.Integer, db.ForeignKey('avocats.avocat_id'), nullable=False)
    date_formation = db.Column(db.Date, nullable=False)
    lieu = db.Column(db.String(200), nullable=False)
    titre_formation = db.Column(db.String(300), nullable=False)
    duree = db.Column(db.Integer, nullable=False)  # Durée en heures
    format_formation = db.Column(db.Enum('distantiel', 'presentiel', 'hybride', 
                                        name='format_type'), nullable=False)
    organisateur = db.Column(db.String(200), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    certificat_obtenu = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Formation {self.titre_formation}>'
