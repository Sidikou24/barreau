#services/user_service.py
from app import db
from app.models.user import User
from app.models.avocat import Avocat
from werkzeug.security import generate_password_hash
from datetime import datetime
import secrets

class UserService:
    @staticmethod
    def create_user(data, cree_par):
        # Vérif email unique
        if User.query.filter_by(email=data['email']).first():
            raise ValueError("Email déjà utilisé.")

        # Génération mot de passe temporaire (plus sûr que nom+année)
        mot_de_passe_temp = secrets.token_urlsafe(8)

        user = User(
            nom=data['nom'],
            prenom=data['prenom'],
            email=data['email'],
            date_naissance=datetime.strptime(data['date_naissance'], '%Y-%m-%d').date(),
            telephone=data.get('telephone'),
            adresse=data.get('adresse'),
            role=data['role'],
            cree_par=cree_par
        )
        user.set_password(mot_de_passe_temp)
        db.session.add(user)
        db.session.flush()

        # Profil Avocat
        if user.role == 'avocat':
            avocat = Avocat(
                nom=user.nom,
                naissance=user.date_naissance,
                sexe=data.get('sexe', 'M'),
                telephone=user.telephone,
                adresse=user.adresse,
                qualification=data.get('qualification', 'titulaire')
            )
            user.avocat_profile = avocat  # liaison via la relation ORM
            db.session.add(avocat)

        db.session.commit()
        return user, mot_de_passe_temp

    # services/user_service.py

    @staticmethod
    def update_user(user_id, data):
        user = User.query.get_or_404(user_id)

        # Mise à jour des infos utilisateur
        user.nom = data['nom']
        user.prenom = data['prenom']
        user.email = data['email']
        user.date_naissance = datetime.strptime(data['date_naissance'], '%Y-%m-%d').date()
        user.telephone = data.get('telephone')
        user.adresse = data.get('adresse')
        user.statut = data.get('statut', user.statut)

        # ⚠️ Important : garder en mémoire l'ancien rôle avant mise à jour
        ancien_role = user.role
        nouveau_role = data.get('role', user.role)
        user.role = nouveau_role

        # --- Cas 1 : Rôle avocat ---
        if nouveau_role == 'avocat':
            if not user.avocat_profile:
                # Création d'un profil avocat si inexistant
                avocat = Avocat(
                    nom=user.nom,
                    naissance=user.date_naissance,
                    sexe=data.get('sexe', 'M'),
                    telephone=user.telephone,
                    adresse=user.adresse,
                    qualification=data.get('qualification', 'titulaire')
                )
                user.avocat_profile = avocat
            else:
                # Mise à jour du profil existant
                avocat = user.avocat_profile
                avocat.nom = user.nom
                avocat.naissance = user.date_naissance
                avocat.sexe = data.get('sexe', avocat.sexe or 'M')
                avocat.telephone = user.telephone
                avocat.adresse = user.adresse
                avocat.qualification = data.get('qualification', avocat.qualification)

        # --- Cas 2 : L'utilisateur n'est plus avocat ---
        elif ancien_role == 'avocat' and user.avocat_profile:
            db.session.delete(user.avocat_profile)

        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)  # le profil Avocat sera supprimé automatiquement
        db.session.commit()
        return True
