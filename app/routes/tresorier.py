
# app/routes/tresorier.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.models.droit_plaidoirie import DroitPlaidoirie
from app.models import db
from datetime import datetime

tresorier_bp = Blueprint('tresorier', __name__)

@tresorier_bp.route('/dashboard')
@login_required
@role_required('tresorier')
def dashboard():
    # Plaidoiries en attente de validation
    plaidoiries_attente = DroitPlaidoirie.query.filter_by(statut='en_attente').count()
    return render_template('tresorier/dashboard.html', plaidoiries_attente=plaidoiries_attente)

@tresorier_bp.route('/validation-plaidoiries')
@login_required
@role_required('tresorier')
def validation_plaidoiries():
    plaidoiries = DroitPlaidoirie.query.filter_by(statut='en_attente').all()
    return render_template('tresorier/validation_plaidoiries.html', plaidoiries=plaidoiries)

@tresorier_bp.route('/valider-plaidoirie/<int:plaidoirie_id>', methods=['POST'])
@login_required
@role_required('tresorier')
def valider_plaidoirie(plaidoirie_id):
    plaidoirie = DroitPlaidoirie.query.get_or_404(plaidoirie_id)
    action = request.form.get('action')
    
    try:
        if action == 'valider':
            plaidoirie.statut = 'valide'
            flash('Plaidoirie validée avec succès.', 'success')
        elif action == 'rejeter':
            plaidoirie.statut = 'rejete'
            plaidoirie.commentaire = request.form.get('commentaire', '')
            flash('Plaidoirie rejetée.', 'warning')
        
        plaidoirie.valide_par = current_user.id
        plaidoirie.date_validation = datetime.utcnow()
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la validation: {str(e)}', 'danger')
    
    return redirect(url_for('tresorier.validation_plaidoiries'))
