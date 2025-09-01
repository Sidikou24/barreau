# app/models/droit_plaidoirie.py
from app import db
from datetime import datetime

class DroitPlaidoirie(db.Model):
    __tablename__ = 'droits_plaidoirie'
    
    plaidoirie_id = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Integer, nullable=False)  # Montant total des timbres
    
    # Détail des timbres (pour traçabilité)
    timbres_2500 = db.Column(db.Integer, default=0)
    timbres_5000 = db.Column(db.Integer, default=0)
    timbres_10000 = db.Column(db.Integer, default=0)
    
    agent_perception = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.Enum('en_attente', 'valide', 'rejete', name='plaidoirie_status'), 
                      default='en_attente')
    valide_par = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_validation = db.Column(db.DateTime)
    commentaire = db.Column(db.Text, nullable=True)
    
    # Relations
    agent = db.relationship('User', foreign_keys=[agent_perception], backref='plaidoiries_saisies')
    validateur = db.relationship('User', foreign_keys=[valide_par], backref='plaidoiries_validees')
    
    @property
    def montant_formate(self):
        """Retourne le montant formaté en FCFA"""
        return f"{self.montant:,} FCFA".replace(',', ' ')
    
    @property
    def detail_timbres(self):
        """Retourne le détail des timbres"""
        details = []
        if self.timbres_2500 > 0:
            details.append(f"{self.timbres_2500} x 2 500 FCFA")
        if self.timbres_5000 > 0:
            details.append(f"{self.timbres_5000} x 5 000 FCFA")
        if self.timbres_10000 > 0:
            details.append(f"{self.timbres_10000} x 10 000 FCFA")
        return " + ".join(details) if details else "Aucun timbre"
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire pour la sérialisation JSON"""
        return {
            'plaidoirie_id': self.plaidoirie_id,
            'montant': self.montant,
            'timbres_2500': self.timbres_2500,
            'timbres_5000': self.timbres_5000,
            'timbres_10000': self.timbres_10000,
            'agent_perception': self.agent_perception,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None,
            'statut': self.statut,
            'valide_par': self.valide_par,
            'date_validation': self.date_validation.isoformat() if self.date_validation else None,
            'commentaire': self.commentaire,
            'montant_formate': self.montant_formate,
            'detail_timbres': self.detail_timbres,
            'agent': {
                'id': self.agent.id,
                'nom': self.agent.nom,
                'prenom': self.agent.prenom
            } if self.agent else None,
            'validateur': {
                'id': self.validateur.id,
                'nom': self.validateur.nom,
                'prenom': self.validateur.prenom
            } if self.validateur else None
        }
    
    def __repr__(self):
        return f'<DroitPlaidoirie {self.plaidoirie_id} - {self.montant_formate}>'
