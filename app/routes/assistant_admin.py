
# app/routes/assistant_admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.models.droit_plaidoirie import DroitPlaidoirie
from app.models import db

assistant_admin_bp = Blueprint('assistant_admin', __name__)

@assistant_admin_bp.route('/dashboard')
@login_required
@role_required('assistant_administratif')
def dashboard():
    return render_template('assistant_admin/dashboard.html')

@assistant_admin_bp.route('/saisie-plaidoirie', methods=['GET', 'POST'])
@login_required
@role_required('assistant_administratif')
def saisie_plaidoirie():
    if request.method == 'POST':
        try:
            # Calcul du montant total des timbres
            timbres_2500 = int(request.form.get('timbres_2500', 0))
            timbres_5000 = int(request.form.get('timbres_5000', 0))
            timbres_10000 = int(request.form.get('timbres_10000', 0))
            
            montant_total = (timbres_2500 * 2500) + (timbres_5000 * 5000) + (timbres_10000 * 10000)
            
            plaidoirie = DroitPlaidoirie(
                avocat_id=request.form.get('avocat_id'),
                numero_affaire=request.form.get('numero_affaire'),
                nature_affaire=request.form.get('nature_affaire'),
                tribunal=request.form.get('tribunal'),
                montant=montant_total,
                agent_perception=current_user.id  # Automatiquement l'assistant admin
            )
            
            db.session.add(plaidoirie)
            db.session.commit()
            
            flash(f'Plaidoirie saisie avec succès. Montant total: {montant_total} FCFA', 'success')
            return redirect(url_for('assistant_admin.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la saisie: {str(e)}', 'danger')
    
    # Récupérer la liste des avocats pour le formulaire
    from app.models.avocat import Avocat
    avocats = Avocat.query.filter_by(statut='actif').all()
    return render_template('assistant_admin/saisie_plaidoirie.html', avocats=avocats)
