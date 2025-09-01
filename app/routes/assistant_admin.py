
# app/routes/assistant_admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.models.droit_plaidoirie import DroitPlaidoirie
from app.models import db
from app.models.acte_avocat import ActeAvocat
from app.models.avocat import Avocat
from app.models.assistance_juridique import AssistanceJuridique
from sqlalchemy import or_, func
from datetime import datetime

assistant_admin_bp = Blueprint('assistant_admin', __name__)

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
                           avocats=avocats)

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
