# app/routes/batonnier.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.services.user_service import UserService
from app.models.user import User
from app import db

batonnier_bp = Blueprint('batonnier', __name__)

@batonnier_bp.route('/dashboard')
@login_required
@role_required('batonnier')
def dashboard():
    return render_template('batonnier/dashboard.html')

@batonnier_bp.route('/utilisateurs')
@login_required
@role_required('batonnier')
def utilisateurs():
    users = User.query.all()
    return render_template('batonnier/dashboard.html', users=users)

@batonnier_bp.route('/utilisateurs/nouveau', methods=['GET', 'POST'])
@login_required
@role_required('batonnier')
def nouveau_utilisateur():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            user, mot_de_passe_temp = UserService.create_user(data, cree_par=current_user.id)
            flash(f"Utilisateur {user.nom} {user.prenom} créé. Mot de passe temporaire: {mot_de_passe_temp}", "success")
            return redirect(url_for('batonnier.utilisateurs'))
        except Exception as e:
            flash(str(e), 'danger')
    return redirect(url_for('batonnier.utilisateurs'))

@batonnier_bp.route('/utilisateurs/<int:user_id>/modifier', methods=['GET', 'POST'])
@login_required
@role_required('batonnier')
def modifier_utilisateur(user_id):
    if request.method == 'POST':
        try:
            UserService.update_user(user_id, request.form.to_dict())
            flash("Utilisateur modifié avec succès", "success")
            return redirect(url_for('batonnier.utilisateurs'))
        except Exception as e:
            flash(str(e), 'danger')
    user = User.query.get_or_404(user_id)
    return render_template('batonnier/modifier_user.html', user=user)

@batonnier_bp.route('/utilisateurs/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@role_required('batonnier')
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    user.statut = 'inactif' if user.statut == 'actif' else 'actif'
    db.session.commit()
    flash(f"Statut de {user.nom} {user.prenom} mis à jour.", "success")
    return redirect(url_for('batonnier.utilisateurs'))

@batonnier_bp.route('/utilisateurs/<int:user_id>/supprimer', methods=['POST'])
@login_required
@role_required('batonnier')
def supprimer_utilisateur(user_id):
    try:
        UserService.delete_user(user_id)
        flash("Utilisateur supprimé.", "success")
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('batonnier.utilisateurs'))

@batonnier_bp.route('/cotisations')
@login_required
@role_required('batonnier')
def cotisations():
    return render_template('batonnier/cotisations.html')

@batonnier_bp.route('/gestion-fonds')
@login_required
@role_required('batonnier')
def gestion_fonds():
    return render_template('batonnier/gestion_fonds.html')

@batonnier_bp.route('/assistance-juridique')
@login_required
@role_required('batonnier')
def assistance_juridique():
    return render_template('batonnier/assistance_juridique.html')

@batonnier_bp.route('/droit-plaidoirie')
@login_required
@role_required('batonnier')
def droit_plaidoirie():
    return render_template('batonnier/droit_plaidoirie.html')

@batonnier_bp.route('/actes-avocats')
@login_required
@role_required('batonnier')
def actes_avocats():
    return render_template('batonnier/actes_avocats.html')