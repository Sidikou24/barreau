# app/models/acte_document.py
from app import db
from datetime import datetime

class ActeDocument(db.Model):
    __tablename__ = 'acte_documents'

    id = db.Column(db.Integer, primary_key=True)
    acte_id = db.Column(db.Integer, db.ForeignKey('actes_avocat.acte_id', ondelete='CASCADE'), nullable=False)
    storage_path = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=True)
    size_bytes = db.Column(db.Integer, nullable=True)
    sha256_hash = db.Column(db.String(64), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    acte = db.relationship('ActeAvocat', backref=db.backref('documents', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<ActeDocument acte_id={self.acte_id} name={self.original_name}>"