# app/models/operation_fond.py
from app import db
from datetime import datetime

class OperationFond(db.Model):
    __tablename__ = 'operations_fonds'

    id = db.Column(db.Integer, primary_key=True)
    fond_id = db.Column(db.Integer, db.ForeignKey('fonds.id'), nullable=False)
    type_operation = db.Column(db.String(20), nullable=False)
    montant = db.Column(db.Integer, nullable=False)
    provenance = db.Column(db.String(200))
    motif = db.Column(db.String(200))
    fond_destination_id = db.Column(db.Integer, db.ForeignKey('fonds.id'))
    date_reception = db.Column(db.Date)
    date_depense = db.Column(db.Date)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.String(20), default="en_attente")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Initiateur
    validateur_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Validateur
    date_validation = db.Column(db.DateTime)
    commentaire = db.Column(db.Text)
    motif_annulation = db.Column(db.Text)

    # Relations
    fond = db.relationship('Fond', foreign_keys=[fond_id])
    fond_destination = db.relationship('Fond', foreign_keys=[fond_destination_id])
    initiateur = db.relationship('User', foreign_keys=[user_id], backref='operations_initiees')  # Backref pour l'initiateur
    validateur = db.relationship('User', foreign_keys=[validateur_id], backref='operations_validees_by')  # Backref pour le validateur
