# app/models/avocat.py
from app import db
from datetime import datetime

class Avocat(db.Model):
    __tablename__ = 'avocats'
    
    avocat_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    naissance = db.Column(db.Date, nullable=False)
    sexe = db.Column(db.Enum('M', 'F', name='sexe_type'), nullable=False)
    d_serment = db.Column(db.Date)  # Date de serment
    d_inscription = db.Column(db.Date)  # Date d'inscription
    telephone = db.Column(db.String(20))
    adresse = db.Column(db.Text)
    statut = db.Column(db.Enum('actif', 'suspendu', 'radie', name='avocat_status'), 
                      default='actif')
    qualification = db.Column(db.Enum('conseil_ordre', 'titulaire', 'stagiaire', 
                                    name='qualification_type'))
    responsabilite_civile = db.Column(db.Text)
    formation = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    plaidoiries = db.relationship('DroitPlaidoirie', backref='avocat', lazy=True)
    actes = db.relationship('ActeAvocat', backref='avocat', lazy=True)
    assistances = db.relationship('AssistanceJuridique', backref='avocat', lazy=True)
    cotisations = db.relationship('Cotisation', backref='avocat', lazy=True)
    formations = db.relationship('Formation', backref='avocat', lazy=True)
    sanctions = db.relationship('SanctionDisciplinaire', backref='avocat', lazy=True)
    cabinets = db.relationship('CabinetAvocat', secondary='cabinet_membres', 
                              back_populates='membres')
    
    def __repr__(self):
        return f'<Avocat {self.nom}>'
