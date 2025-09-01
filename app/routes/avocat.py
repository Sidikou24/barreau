# app/routes/avocat.py (Routes pour les avocats)
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.services.cotisations import CotisationService

avocat_bp = Blueprint('avocat', __name__)

@avocat_bp.route('/dashboard')
@login_required
@role_required('avocat')
def dashboard():
    return render_template('avocat/dashboard.html')

#ROUTES POUR LES COTISATIONS
@avocat_bp.route('/cotisations')
@login_required
@role_required('avocat')
def cotisations():
    """Page des cotisations pour l'avocat"""
    # Trouver le profil avocat de l'utilisateur connecté
    avocat_profile = current_user.avocat_profile
    if not avocat_profile:
        flash("Profil avocat introuvable.", "danger")
        return redirect(url_for('avocat.dashboard'))
    
    cotisations = CotisationService.get_cotisations_avocat(avocat_profile.avocat_id)
    
    if request.headers.get('Accept') == 'application/json':
        return jsonify({'cotisations': cotisations})
    
    return render_template('avocat/cotisations.html', 
                         cotisations=cotisations, 
                         qualification=avocat_profile.qualification)