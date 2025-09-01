# app/routes/tresorier.py
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services.cotisations import CotisationService
from app.services.gestion_fond import GestionFondService
from app.utils.decorators import role_required
from app.services.droit_plaidoirie import DroitPlaidoirieService
from app.models.droit_plaidoirie import DroitPlaidoirie

tresorier_bp = Blueprint('tresorier', __name__)

@tresorier_bp.route('/dashboard')
@login_required
@role_required('tresorier')
def dashboard():
    """Dashboard du tresorier avec statistiques"""
    # Statistiques generales
    stats = {
        'en_attente': len(DroitPlaidoirieService.get_droits_par_statut('en_attente')),
        'valides_aujourdhui': 0,  # A implementer si necessaire
        'total_mois': 0,  # A implementer si necessaire
    }
    
    # Derniers droits a valider
    droits_attente = DroitPlaidoirieService.get_droits_par_statut('en_attente')[:5]
    droits_attente_dict = [droit.to_dict() for droit in droits_attente]
    
    return render_template('tresorier/dashboard.html', 
                         stats=stats, 
                         droits_attente=droits_attente_dict)

@tresorier_bp.route('/droit-plaidoirie')
@login_required
@role_required('tresorier')
def droit_plaidoirie():
    """Liste de tous les droits de plaidoirie pour validation"""
    statut_filtre = request.args.get('statut', 'en_attente')
    
    # Récupération des droits
    if statut_filtre == 'tous':
        droits = DroitPlaidoirieService.get_droits_par_statut()
    else:
        droits = DroitPlaidoirieService.get_droits_par_statut(statut_filtre)
    
    droits_dict = [droit.to_dict() for droit in droits]
    
    stats = {
        'en_attente': len(DroitPlaidoirieService.get_droits_par_statut('en_attente')),
        'valide': len(DroitPlaidoirieService.get_droits_par_statut('valide')),
        'rejete': len(DroitPlaidoirieService.get_droits_par_statut('rejete')),
    }
    
    # Si requête JSON
    if request.headers.get('Accept') == 'application/json':
        return jsonify({'droits': droits_dict, 'stats': stats})
    
    return render_template('tresorier/droit_plaidoirie.html', 
                         droits=droits_dict, 
                         stats=stats, 
                         statut_filtre=statut_filtre)
    
@tresorier_bp.route('/valider-droit/<int:plaidoirie_id>', methods=['POST'])
@login_required
@role_required('tresorier')
def valider_droit(plaidoirie_id):
    """Validation ou rejet d'un droit de plaidoirie"""
    try:
        # Supporte à la fois form-data et JSON
        data = request.form if request.form else request.get_json()
        action = data.get('action')
        commentaire = data.get('commentaire', '').strip()
        
        # Validation des données
        if action not in ['valider', 'rejeter']:
            return jsonify({'success': False, 'error': 'Action non valide.'}), 400
        
        if action == 'rejeter' and not commentaire:
            return jsonify({'success': False, 'error': 'Un commentaire est requis pour rejeter.'}), 400
        
        # Traitement
        droit, erreur = DroitPlaidoirieService.valider_droit(
            plaidoirie_id=plaidoirie_id,
            action=action,
            validateur_id=current_user.id,
            commentaire=commentaire if commentaire else None
        )
        
        if erreur:
            return jsonify({'success': False, 'error': f'Erreur lors du traitement : {erreur}'}), 400
        
        return jsonify({
            'success': True,
            'message': f'Droit de plaidoirie {"validé" if action == "valider" else "rejeté"} avec succès !',
            'montant_formate': droit.montant_formate if action == 'valider' else None
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erreur inattendue : {str(e)}'}), 500
    
    
@tresorier_bp.route('/detail-droit/<int:plaidoirie_id>')
@login_required
@role_required('tresorier')
def detail_droit(plaidoirie_id):
    """Affichage des details d'un droit de plaidoirie"""
    droit = DroitPlaidoirie.query.get_or_404(plaidoirie_id)
    
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify({
            'id': droit.plaidoirie_id,
            'montant': droit.montant_formate,
            'detail_timbres': droit.detail_timbres,
            'agent_nom': f"{droit.agent.nom} {droit.agent.prenom}",
            'date_creation': droit.date_creation.strftime('%d/%m/%Y a %H:%M'),
            'statut': droit.statut,
            'validateur': f"{droit.validateur.nom} {droit.validateur.prenom}" if droit.validateur else None,
            'date_validation': droit.date_validation.strftime('%d/%m/%Y a %H:%M') if droit.date_validation else None,
            'commentaire': droit.commentaire
        })
    
    return render_template('tresorier/detail_droit.html', droit=droit)

@tresorier_bp.route('/tresorier/gestion-fonds')
@login_required
@role_required('tresorier')
def gestion_fonds():
    fonds = GestionFondService.get_fonds()
    operations_en_attente = GestionFondService.get_operations_en_attente()
    return render_template('tresorier/gestion_fond.html', fonds=fonds, operations_en_attente=operations_en_attente)

@tresorier_bp.route('/valider-operation/<int:operation_id>', methods=['POST'])
@login_required
@role_required('tresorier')
def valider_operation(operation_id):
    action = request.form.get('action')
    motif_annulation = request.form.get('motif_annulation', '').strip()

    operation, erreur = GestionFondService.valider_operation(
        operation_id=operation_id,
        action=action,
        motif_annulation=motif_annulation,
        validateur_id=current_user.id
    )

    if erreur:
        flash(f"Erreur : {erreur}", "danger")
    else:
        if action == "valider":
            flash(f"Operation validee avec succes !", "success")
        else:
            flash(f"Operation annulee.", "info")

    return redirect(url_for('tresorier.gestion_fonds'))

#ROUTES POUR LA COTISATION

@tresorier_bp.route('/cotisations')
@login_required
@role_required('tresorier')
def cotisations():
    """Page de gestion des cotisations pour le trésorier"""
    cotisations_par_annee = CotisationService.get_cotisations_par_annee()
    annee_courante = datetime.datetime.now().year
    return render_template('tresorier/cotisations.html', cotisations=cotisations_par_annee, annee_courante=annee_courante)

@tresorier_bp.route('/lancer-cotisation', methods=['POST'])
@login_required
@role_required('tresorier')
def lancer_cotisation():
    """Lance une nouvelle campagne de cotisation"""
    try:
        if request.is_json:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'Données JSON manquantes.'}), 400
        else:
            data = request.form
        
        # Validate required fields presence
        required_fields = ['annee', 'montant_stagiaire', 'montant_titulaire', 'd_echeance']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            error_msg = f"Champs manquants : {', '.join(missing_fields)}"
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(error_msg, "danger")
            return redirect(url_for('tresorier.cotisations'))
        
        # Convert numeric fields safely
        try:
            annee = int(data.get('annee'))
            montant_stagiaire = int(data.get('montant_stagiaire'))
            montant_titulaire = int(data.get('montant_titulaire'))
        except ValueError:
            error_msg = "Les champs 'annee', 'montant_stagiaire' et 'montant_titulaire' doivent être des nombres entiers valides."
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 400
            flash(error_msg, "danger")
            return redirect(url_for('tresorier.cotisations'))
        
        d_echeance = data.get('d_echeance')
        
        resultat, erreur = CotisationService.lancer_cotisation_annuelle(
            annee=annee,
            montant_stagiaire=montant_stagiaire,
            montant_titulaire=montant_titulaire,
            d_echeance=d_echeance,
            lanceur_id=current_user.id
        )
        
        if erreur:
            if request.is_json:
                return jsonify({'success': False, 'error': erreur}), 400
            flash(f"Erreur : {erreur}", "danger")
            return redirect(url_for('tresorier.cotisations'))
        
        message = f"Cotisation {annee} lancée avec succès ! {resultat['cotisations_creees']} avocats ont été notifiés."
        
        if request.is_json:
            return jsonify({'success': True, 'message': message, 'data': resultat})
        
        flash(message, "success")
        return redirect(url_for('tresorier.cotisations'))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': f'Erreur inattendue : {str(e)}'}), 500
        flash(f"Erreur inattendue : {str(e)}", "danger")
        return redirect(url_for('tresorier.cotisations'))

@tresorier_bp.route('/cotisations/<int:annee>')
@login_required
@role_required('tresorier')
def detail_cotisation(annee):
    """Détails d'une cotisation par année"""
    cotisations = CotisationService.get_cotisation_par_annee(annee)
    
    if request.headers.get('Accept') == 'application/json':
        return jsonify({'cotisations': cotisations, 'annee': annee})
    
    return render_template('tresorier/detail_cotisation.html', 
                         cotisations=cotisations, annee=annee)
