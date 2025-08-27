
# app/routes/batonnier.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.models.user import User
from app.models.avocat import Avocat
from app.models import db
from datetime import datetime

batonnier_bp = Blueprint('batonnier', __name__)

@batonnier_bp.route('/dashboard')
@login_required
@role_required('batonnier')
def dashboard():
    # Statistiques pour le tableau de bord
    total_avocats = User.query.filter_by(role='avocat').count()
    total_utilisateurs = User.query.filter(User.role != 'batonnier').count()
    
    # Avocats récemment ajoutés (7 derniers jours)
    from datetime import timedelta
    sept_jours_ago = datetime.utcnow() - timedelta(days=7)
    nouveaux_avocats = User.query.filter(
        User.role == 'avocat',
        User.date_creation >= sept_jours_ago
    ).count()
    
    stats = {
        'total_avocats': total_avocats,
        'total_utilisateurs': total_utilisateurs,
        'nouveaux_avocats': nouveaux_avocats
    }
    
    return render_template('batonnier/dashboard.html', stats=stats)

@batonnier_bp.route('/utilisateurs')
@login_required
@role_required('batonnier')
def utilisateurs():
    page = request.args.get('page', 1, type=int)
    users = User.query.filter(User.role != 'batonnier').paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('batonnier/utilisateurs.html', users=users)

@batonnier_bp.route('/utilisateurs/nouveau', methods=['GET', 'POST'])
@login_required
@role_required('batonnier')
def nouveau_utilisateur():
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            nom = request.form.get('nom')
            prenom = request.form.get('prenom')
            email = request.form.get('email')
            date_naissance = datetime.strptime(request.form.get('date_naissance'), '%Y-%m-%d').date()
            telephone = request.form.get('telephone')
            adresse = request.form.get('adresse')
            role = request.form.get('role')
            
            # Vérification que l'email n'existe pas déjà
            if User.query.filter_by(email=email).first():
                flash('Un utilisateur avec cet email existe déjà.', 'danger')
                return render_template('batonnier/create_user.html')
            
            # Création de l'utilisateur
            user = User(
                nom=nom,
                prenom=prenom,
                email=email,
                date_naissance=date_naissance,
                telephone=telephone,
                adresse=adresse,
                role=role,
                cree_par=current_user.id
            )
            
            # Mot de passe temporaire (à changer lors de la première connexion)
            mot_de_passe_temp = f"{nom.lower()}{date_naissance.year}"
            user.set_password(mot_de_passe_temp)
            
            db.session.add(user)
            db.session.flush()  # Pour obtenir l'ID de l'utilisateur
            
            # Si c'est un avocat, créer aussi le profil avocat
            if role == 'avocat':
                avocat = Avocat(
                    user_id=user.id,
                    nom=nom,
                    naissance=date_naissance,
                    sexe=request.form.get('sexe', 'M'),
                    telephone=telephone,
                    adresse=adresse,
                    qualification=request.form.get('qualification', 'stagiaire')
                )
                db.session.add(avocat)
            
            db.session.commit()
            
            flash(f'Utilisateur {nom} {prenom} créé avec succès. '
                  f'Mot de passe temporaire: {mot_de_passe_temp}', 'success')
            return redirect(url_for('batonnier.utilisateurs'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création de l\'utilisateur: {str(e)}', 'danger')
    
    return render_template('batonnier/create_user.html')

@batonnier_bp.route('/utilisateurs/<int:user_id>/modifier', methods=['GET', 'POST'])
@login_required
@role_required('batonnier')
def modifier_utilisateur(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            user.nom = request.form.get('nom')
            user.prenom = request.form.get('prenom')
            user.email = request.form.get('email')
            user.date_naissance = datetime.strptime(request.form.get('date_naissance'), '%Y-%m-%d').date()
            user.telephone = request.form.get('telephone')
            user.adresse = request.form.get('adresse')
            user.statut = request.form.get('statut')
            
            db.session.commit()
            flash('Utilisateur modifié avec succès.', 'success')
            return redirect(url_for('batonnier.utilisateurs'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la modification: {str(e)}', 'danger')
    
    return render_template('batonnier/modifier_user.html', user=user)
@batonnier_bp.route('/utilisateurs/<int:user_id>/supprimer', methods=['POST'])
@login_required
@role_required('batonnier')
def supprimer_utilisateur(user_id):
    user = User.query.get_or_404(user_id)
    
    try:
        # Si c'est un avocat, supprimer aussi son profil avocat
        if user.role == 'avocat' and user.avocat_profile:
            db.session.delete(user.avocat_profile)
        
        db.session.delete(user)
        db.session.commit()
        
        flash(f'Utilisateur {user.nom} {user.prenom} supprimé avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'danger')
    
    return redirect(url_for('batonnier.utilisateurs'))

# Routes pour les autres sections du Bâtonnier
@batonnier_bp.route('/droit-plaidoirie')
@login_required
@role_required('batonnier')
def droit_plaidoirie():
    # Vue d'ensemble des droits de plaidoirie
    return render_template('batonnier/droit_plaidoirie.html')

@batonnier_bp.route('/actes-avocats')
@login_required
@role_required('batonnier')
def actes_avocats():
    # Vue d'ensemble des actes d'avocats
    return render_template('batonnier/actes_avocats.html')

@batonnier_bp.route('/assistance-juridique')
@login_required
@role_required('batonnier')
def assistance_juridique():
    # Vue d'ensemble de l'assistance juridique
    return render_template('batonnier/assistance_juridique.html')

@batonnier_bp.route('/cotisations')
@login_required
@role_required('batonnier')
def cotisations():
    # Vue d'ensemble des cotisations
    return render_template('batonnier/cotisations.html')

@batonnier_bp.route('/gestion-fonds')
@login_required
@role_required('batonnier')
def gestion_fonds():
    # Gestion des fonds
    return render_template('batonnier/gestion_fonds.html')

@batonnier_bp.route('/gestion-avocats')
@login_required
@role_required('batonnier')
def gestion_avocats():
    # Gestion spécifique des avocats
    avocats = Avocat.query.all()
    return render_template('batonnier/gestion_avocats.html', avocats=avocats)
