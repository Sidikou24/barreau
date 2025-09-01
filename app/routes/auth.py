# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from app.models.user import User
from app.models import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if user.statut != 'actif':
                flash('Votre compte est désactivé. Contactez l\'administrateur.', 'danger')
                return render_template('auth/login.html')
            
            login_user(user)
            
            # Redirection selon le rôle
            if user.role == 'batonnier':
                return redirect(url_for('batonnier.dashboard'))
            elif user.role == 'avocat':
                return redirect(url_for('avocat.dashboard'))
            elif user.role == 'assistant_comptable':
                return redirect(url_for('assistant_comptable.dashboard'))
            elif user.role == 'assistant_administratif':
                return redirect(url_for('assistant_admin.dashboard'))
            elif user.role == 'tresorier':
                return redirect(url_for('tresorier.dashboard'))
            elif user.role == 'secretaire':
                return redirect(url_for('secretaire.dashboard'))
            else:
                return redirect(url_for('auth.login'))
        else:
            flash('Email ou mot de passe incorrect.', 'danger')
    

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté avec succès.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Vérification de l'ancien mot de passe
        if not current_user.check_password(old_password):
            flash("L'ancien mot de passe est incorrect.", "danger")
            return render_template('auth/change_password.html')

        # Vérification correspondance nouveau / confirmation
        if new_password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return render_template('auth/change_password.html')

        # Mise à jour du mot de passe
        current_user.set_password(new_password)
        current_user.must_change_password = False
        db.session.commit()

        flash("Votre mot de passe a été mis à jour avec succès ✅", "success")
        role_to_bp = {
            'batonnier': 'batonnier',
            'avocat': 'avocat',
            'assistant_comptable': 'assistant_comptable',
            'assistant_administratif': 'assistant_admin',
            'tresorier': 'tresorier',
            'secretaire': 'secretaire',
        }
        bp = role_to_bp.get(current_user.role)
        if bp:
            return redirect(url_for(f"{bp}.dashboard"))
        return redirect(url_for('auth.login'))

    return render_template('auth/change_password.html')