# app/routes/assistant_comptable.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services.cotisations import CotisationService
from app.utils.decorators import role_required
from app.services.gestion_fond import GestionFondService
from app.models.fond import Fond

assistant_comptable_bp = Blueprint('assistant_comptable', __name__)

@assistant_comptable_bp.route('/dashboard')
@login_required
@role_required('assistant_comptable')
def dashboard():
    return render_template('assistant_comptable/dashboard.html')

@assistant_comptable_bp.route('/gestion-fonds')
@login_required
@role_required('assistant_comptable')
def fonds():
    fonds = GestionFondService.get_fonds()
    return render_template('assistant_comptable/gestion_fond.html', fonds=fonds)

@assistant_comptable_bp.route('/crediter-fond', methods=['POST'])
@login_required
@role_required('assistant_comptable')
def crediter_fond():
    fond_id = request.form.get('fond_id')
    provenance = request.form.get('provenance')
    montant = (request.form.get('montant'))
    date_reception = request.form.get('date_reception')
    commentaire = request.form.get('commentaire', '').strip()

    operation, erreur = GestionFondService.crediter_fond(
        fond_id=fond_id,
        provenance=provenance,
        montant=montant,
        date_reception=date_reception,
        commentaire=commentaire,
        user_id=current_user.id
    )

    if erreur:
        flash(f"Erreur : {erreur}", "danger")
    else:
        flash(f"Fond crédité avec succès ! Montant : {montant} FCFA", "success")

    return redirect(url_for('assistant_comptable.dashboard'))

@assistant_comptable_bp.route('/debiter-fond', methods=['POST'])
@login_required
@role_required('assistant_comptable')
def debiter_fond():
    fond_id = request.form.get('fond_id')
    motif = request.form.get('motif')
    montant = (request.form.get('montant'))
    date_depense = request.form.get('date_depense')

    operation, erreur = GestionFondService.debiter_fond(
        fond_id=fond_id,
        motif=motif,
        montant=montant,
        date_depense=date_depense,
        user_id=current_user.id
    )

    if erreur:
        flash(f"Erreur : {erreur}", "danger")
    else:
        flash(f"Opération de débit enregistrée en attente de validation.", "info")

    return redirect(url_for('assistant_comptable.dashboard'))

@assistant_comptable_bp.route('/transférer-fond', methods=['POST'])
@login_required
@role_required('assistant_comptable')
def transférer_fond():
    fond_source_id = request.form.get('fond_source_id')
    fond_destination_id = request.form.get('fond_destination_id')
    montant = (request.form.get('montant'))

    operation, erreur = GestionFondService.transférer_fond(
        fond_source_id=fond_source_id,
        fond_destination_id=fond_destination_id,
        montant=montant,
        user_id=current_user.id
    )

    if erreur:
        flash(f"Erreur : {erreur}", "danger")
    else:
        flash(f"Opération de transfert enregistrée en attente de validation.", "info")

    return redirect(url_for('assistant_comptable.dashboard'))

#ROUTES POUR LA GESTION DES COTISATIONS

@assistant_comptable_bp.route('/cotisations')
@login_required
@role_required('assistant_comptable')
def cotisations():
    """Page de gestion des cotisations pour l'assistant comptable"""
    cotisations_par_annee = CotisationService.get_cotisations_par_annee()
    avocats = CotisationService.get_avocats_pour_selection()
    return render_template('assistant_comptable/cotisations.html', 
                         cotisations=cotisations_par_annee, avocats=avocats)

@assistant_comptable_bp.route('/cotisations/<int:annee>')
@login_required
@role_required('assistant_comptable')
def detail_cotisation(annee):
    """Détails d'une cotisation par année"""
    cotisations = CotisationService.get_cotisation_par_annee(annee)
    avocats = CotisationService.get_avocats_pour_selection()
    
    if request.headers.get('Accept') == 'application/json':
        return jsonify({'cotisations': cotisations, 'annee': annee, 'avocats': avocats})
    
    return render_template('assistant_comptable/detail_cotisation.html', 
                         cotisations=cotisations, annee=annee, avocats=avocats)

@assistant_comptable_bp.route('/enregistrer-paiement-cotisation', methods=['POST'])
@login_required
@role_required('assistant_comptable')
def enregistrer_paiement_cotisation():
    """Enregistre le paiement d'une cotisation"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        avocat_id = int(data.get('avocat_id'))
        annee_cotisation = int(data.get('annee_cotisation'))
        
        resultat, erreur = CotisationService.enregistrer_paiement_cotisation(
            avocat_id=avocat_id,
            annee_cotisation=annee_cotisation,
            comptable_id=current_user.id
        )
        
        if erreur:
            if request.is_json:
                return jsonify({'success': False, 'error': erreur}), 400
            flash(f"Erreur : {erreur}", "danger")
            return redirect(url_for('assistant_comptable.cotisations'))
        
        message = f"Paiement enregistré avec succès ! Montant : {resultat['montant']} FCFA"
        
        if request.is_json:
            return jsonify({'success': True, 'message': message, 'data': resultat})
        
        flash(message, "success")
        return redirect(url_for('assistant_comptable.detail_cotisation', annee=annee_cotisation))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': f'Erreur inattendue : {str(e)}'}), 500
        flash(f"Erreur inattendue : {str(e)}", "danger")
        return redirect(url_for('assistant_comptable.cotisations'))

@assistant_comptable_bp.route('/api/avocats-search')
@login_required
@role_required('assistant_comptable')
def search_avocats():
    """API pour la recherche d'avocats"""
    query = request.args.get('q', '').strip()
    avocats = CotisationService.get_avocats_pour_selection()
    
    if query:
        avocats = [a for a in avocats if query.lower() in a['nom_complet'].lower()]
    
    return jsonify(avocats[:20])  # Limiter à 20 résultats

