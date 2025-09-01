# app/models/fond.py
from app import db
from datetime import datetime
from sqlalchemy.orm import relationship

class Fond(db.Model):
    __tablename__ = 'fonds'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)
    montant = db.Column(db.Integer, default=0.00)
    description = db.Column(db.Text)

    operations = relationship('OperationFond', foreign_keys='OperationFond.fond_id')

    def __repr__(self):
        return f"<Fond {self.nom} - {self.montant}>"
