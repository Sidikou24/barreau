# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
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
