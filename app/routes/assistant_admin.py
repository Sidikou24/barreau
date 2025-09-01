# app/routes/assistant_admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.services.droit_plaidoirie import DroitPlaidoirieService
from app.models.droit_plaidoirie import DroitPlaidoirie
from app.models import db
from app.models.acte_avocat import ActeAvocat
from app.models.avocat import Avocat
from app.models.assistance_juridique import AssistanceJuridique
from sqlalchemy import or_, func
from datetime import datetime


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

    # Redirige vers la section actes du dashboard sans changer de page
    return redirect(url_for('assistant_admin.dashboard_actes'))

@assistant_admin_bp.route('/dashboard/actes')
@login_required
@role_required('assistant_administratif')
def dashboard_actes():
    # Recherche actes
    q = request.args.get('q', '').strip()
    query = ActeAvocat.query.join(Avocat)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(ActeAvocat.numero_acte.ilike(like), Avocat.nom.ilike(like)))
    actes = query.order_by(ActeAvocat.date_depot.desc()).all()

    # Statistiques actes
    total_actes = ActeAvocat.query.count()
    actes_en_attente = ActeAvocat.query.filter_by(statut='recu').count()
    actes_archives = ActeAvocat.query.filter_by(statut='archive').count()

    # Recherche assistance
    aq = request.args.get('aq', '').strip()
    aquery = AssistanceJuridique.query
    if aq:
        alike = f"%{aq}%"
        aquery = aquery.filter(or_(AssistanceJuridique.numero_demande.ilike(alike), AssistanceJuridique.nom_demandeur.ilike(alike)))
    assistances = aquery.order_by(AssistanceJuridique.date_reception_demande.desc()).all()

    # Statistiques assistance
    total_ass = AssistanceJuridique.query.count()
    en_attente_ass = AssistanceJuridique.query.filter_by(statut='en_attente').count()
    termine_ass = AssistanceJuridique.query.filter_by(statut='termine').count()
    annule_ass = AssistanceJuridique.query.filter_by(statut='annule').count()

    # Avocats pour les formulaires
    avocats = Avocat.query.filter_by(statut='actif').order_by(Avocat.nom.asc()).all()
    
    # Récupération des statistiques droit de plaidoirie
    stats = DroitPlaidoirieService.get_statistiques_agent(current_user.id)
    
    # Derniers droits de plaidoirie créés
    derniers_droits = DroitPlaidoirieService.get_droits_par_statut(agent_id=current_user.id)[:5]

    return render_template('assistant_admin/dashboard.html',
                           actes=actes,
                           total_actes=total_actes,
                           actes_en_attente=actes_en_attente,
                           actes_archives=actes_archives,
                           q=q,
                           assistances=assistances,
                           total_ass=total_ass,
                           en_attente_ass=en_attente_ass,
                           termine_ass=termine_ass,
                           annule_ass=annule_ass,
                           aq=aq,
                           avocats=avocats,
                          stats=stats, 
                         derniers_droits=derniers_droits)

def _generate_numero_demande():
    now = datetime.now()
    year = now.year
    count_year = AssistanceJuridique.query.filter(func.extract('year', AssistanceJuridique.date_reception_demande) == year).count()
    return f"AJ-{year}-{count_year + 1:03d}"

@assistant_admin_bp.route('/assistance/nouvelle', methods=['POST'])
@login_required
@role_required('assistant_administratif')
def assistance_nouvelle():
    try:
        numero = request.form.get('numero_demande') or _generate_numero_demande()
        nom_demandeur = request.form.get('nom_demandeur', '').strip()
        nature_demande = request.form.get('nature_demande', '').strip()
        date_reception = request.form.get('date_reception')
        date_demande = request.form.get('date_demande')
        avocat_nom = request.form.get('ass_avocat_nom', '').strip()
        montant_alloue = request.form.get('montant_alloue')
        if not nom_demandeur:
            raise ValueError('Veuillez saisir le nom du demandeur')
        if not nature_demande:
            raise ValueError('Veuillez saisir la nature de la demande')
        if not date_reception or not date_demande:
            raise ValueError('Veuillez saisir les dates de réception et de demande')

        av_id = None
        if avocat_nom:
            av = Avocat.query.filter_by(nom=avocat_nom).first()
            if not av:
                raise ValueError("Avocat introuvable pour l'assistance")
            av_id = av.avocat_id

        # parse dates
        d_recep = datetime.fromisoformat(date_reception).date()
        d_dem = datetime.fromisoformat(date_demande).date()

        ass = AssistanceJuridique(
            date_reception_demande=d_recep,
            date_demande=d_dem,
            numero_demande=numero,
            nature_demande=nature_demande,
            nom_demandeur=nom_demandeur,
            agent_reception=current_user.id,
            avocat_id=av_id,
            montant_alloue=montant_alloue or None,
            statut='en_attente'
        )
        db.session.add(ass)
        db.session.commit()
        flash('Demande d\'assistance créée', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur: {str(e)}", 'danger')
    return redirect(url_for('assistant_admin.dashboard') + '#assistance-juridique')

@assistant_admin_bp.route('/assistance/<int:assistance_id>/annuler', methods=['POST'])
@login_required
@role_required('assistant_administratif')
def assistance_annuler(assistance_id):
    ass = AssistanceJuridique.query.get_or_404(assistance_id)
    try:
        if ass.statut == 'termine':
            flash('Impossible d\'annuler une demande terminée.', 'warning')
        elif ass.statut == 'annule':
            flash('Demande déjà annulée.', 'info')
        else:
            ass.statut = 'annule'
            db.session.commit()
            flash('Demande annulée.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur: {str(e)}", 'danger')
    return redirect(url_for('assistant_admin.dashboard') + '#assistance-juridique')

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