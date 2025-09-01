# app/routes/assistant_admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.services.droit_plaidoirie import DroitPlaidoirieService
from app.models.droit_plaidoirie import DroitPlaidoirie

assistant_admin_bp = Blueprint('assistant_admin', __name__)

@assistant_admin_bp.route("/plaidoirie")
@login_required
@role_required('assistant_administratif')
def plaidoirie():
    return render_template("assistant_admin/plaidoirie.html")

@assistant_admin_bp.route('/dashboard')
@login_required
@role_required('assistant_administratif')
def dashboard():
    # Récupération des statistiques
    stats = DroitPlaidoirieService.get_statistiques_agent(current_user.id)
    
    # Derniers droits créés
    derniers_droits = DroitPlaidoirieService.get_droits_par_statut(agent_id=current_user.id)[:5]
    
    return render_template('assistant_admin/dashboard.html', 
                         stats=stats, 
                         derniers_droits=derniers_droits)

@assistant_admin_bp.route('/detail-droit/<int:plaidoirie_id>')
@login_required
@role_required('assistant_administratif')
def detail_droit(plaidoirie_id):
    """Affichage des détails d'un droit de plaidoirie pour l'assistant administratif"""
    droit = DroitPlaidoirie.query.get_or_404(plaidoirie_id)

    # Vérifie que l'assistant administratif est bien le propriétaire du droit
    if droit.agent_perception != current_user.id:
        flash("Vous n'êtes pas autorisé à consulter ce droit.", "danger")
        return redirect(url_for('assistant_admin.droit_plaidoirie'))

    return render_template('assistant_admin/detail_droit.html', droit=droit)

@assistant_admin_bp.route('/droit-plaidoirie')
@login_required
@role_required('assistant_administratif')
def droit_plaidoirie():
    """Affiche la liste des droits de plaidoirie de l'assistant"""
    droits = DroitPlaidoirieService.get_droits_par_statut(agent_id=current_user.id)
    stats = DroitPlaidoirieService.get_statistiques_agent(current_user.id)
    
    # Convertir les objets en dictionnaires pour la sérialisation JSON
    droits_serializable = [droit.to_dict() for droit in droits]
    
    return render_template('assistant_admin/droit_plaidoirie.html', 
                         droits=droits, 
                         droits_serializable=droits_serializable,
                         stats=stats)

@assistant_admin_bp.route('/nouveau-droit', methods=['GET', 'POST'])
@login_required
@role_required('assistant_administratif')
def nouveau_droit():
    """Création d'un nouveau droit de plaidoirie"""
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            timbres_2500 = int(request.form.get('timbres_2500', 0))
            timbres_5000 = int(request.form.get('timbres_5000', 0))
            timbres_10000 = int(request.form.get('timbres_10000', 0))
            
            # Validation
            if not any([timbres_2500, timbres_5000, timbres_10000]):
                flash('Vous devez sélectionner au moins un timbre.', 'warning')
                return render_template('assistant_admin/nouveau_droit.html', 
                                     tarifs=DroitPlaidoirieService.TARIFS_TIMBRES)
            
            # Création du droit
            droit, erreur = DroitPlaidoirieService.creer_droit_plaidoirie(
                timbres_2500=timbres_2500,
                timbres_5000=timbres_5000,
                timbres_10000=timbres_10000,
                agent_id=current_user.id
            )
            
            if erreur:
                flash(f'Erreur lors de la création : {erreur}', 'danger')
            else:
                flash(f'Droit de plaidoirie créé avec succès ! Montant total : {droit.montant_formate}', 'success')
                return redirect(url_for('assistant_admin.droit_plaidoirie'))
                
        except ValueError as ve:
            flash(f'Données invalides : {str(ve)}', 'danger')
        except Exception as e:
            flash(f'Erreur inattendue : {str(e)}', 'danger')
    
    return render_template('assistant_admin/nouveau_droit.html', 
                         tarifs=DroitPlaidoirieService.TARIFS_TIMBRES)

@assistant_admin_bp.route('/calculer-montant', methods=['POST'])
@login_required
@role_required('assistant_administratif')
def calculer_montant():
    """API pour calculer le montant total en temps réel"""
    try:
        timbres_2500 = int(request.form.get('timbres_2500', 0))
        timbres_5000 = int(request.form.get('timbres_5000', 0))
        timbres_10000 = int(request.form.get('timbres_10000', 0))
        
        montant = DroitPlaidoirieService.calculer_montant(
            timbres_2500, timbres_5000, timbres_10000
        )
        
        return jsonify({
            'success': True,
            'montant': montant,
            'montant_formate': f"{montant:,} FCFA".replace(',', ' ')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })