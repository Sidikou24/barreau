# app/models/user.py
from flask_login import UserMixin
from app import db
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    telephone = db.Column(db.String(20))
    adresse = db.Column(db.Text)
    role = db.Column(db.Enum('batonnier', 'avocat', 'assistant_comptable', 
                            'assistant_administratif', 'tresorier', 'secretaire', 
                            name='user_roles'), nullable=False)
    statut = db.Column(db.Enum('actif', 'inactif', 'suspendu', name='user_status'), 
                      default='actif')
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    cree_par = db.Column(db.Integer, db.ForeignKey('users.id'))
    must_change_password = db.Column(db.Boolean, default=True)

    # Relations
    avocat_profile = db.relationship(
        'Avocat',
        backref='user_account',
        uselist=False,
        cascade="all, delete-orphan",   # 👈 Ici la magie
        passive_deletes=True
    )
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.nom} {self.prenom}>'
