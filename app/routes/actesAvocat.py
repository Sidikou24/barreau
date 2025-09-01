# app/routes/actesAvocat.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app import db
from app.models.acte_avocat import ActeAvocat
from app.models.avocat import Avocat
from sqlalchemy import or_, func
from datetime import datetime
import os
import hashlib
import mimetypes
from werkzeug.utils import secure_filename
from app.models.acte_document import ActeDocument

actes_avocat_bp = Blueprint('actes_avocat', __name__)


# Helpers
ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg'}

def allowed_file(filename: str):
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS


def generate_numero_acte():
    now = datetime.now()
    year = now.year
    # Compter les actes de l'année en cours pour générer un index
    count_year = ActeAvocat.query.filter(func.extract('year', ActeAvocat.date_depot) == year).count()
    return f"ACT-{year}-{count_year + 1:03d}"


def save_uploaded_file(file_storage, numero_acte: str) -> dict | None:
    if not file_storage or file_storage.filename == '':
        return None
    if not allowed_file(file_storage.filename):
        raise ValueError('Format de fichier non supporté. Formats autorisés: PDF, PNG, JPG, JPEG')

    original_name = secure_filename(file_storage.filename)
    # Nom final: préfix numéro + nom original
    final_name = f"{numero_acte}_{original_name}"
    upload_dir = os.path.join(current_app.instance_path, 'uploads', 'actes')
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, final_name)
    file_storage.save(file_path)

    # Métadonnées
    rel_path = os.path.relpath(file_path, start=current_app.instance_path)
    mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    size_bytes = os.path.getsize(file_path)
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256_hash.update(chunk)

    return {
        'storage_path': rel_path,
        'original_name': original_name,
        'mime_type': mime_type,
        'size_bytes': size_bytes,
        'sha256_hash': sha256_hash.hexdigest(),
    }


# Routes
@actes_avocat_bp.route('/', methods=['GET'])
@login_required
@role_required('assistant_administratif')
def index():
    q = request.args.get('q', '').strip()
    # Redirige vers le dashboard Assistant Admin (section actes) sans changer de page
    target = url_for('assistant_admin.dashboard_actes', q=q)
    return redirect(target + '#actes')


@actes_avocat_bp.route('/nouveau', methods=['POST'])
@login_required
@role_required('assistant_administratif')
def create():
    try:
        numero_acte = request.form.get('numero_acte') or generate_numero_acte()
        avocat_nom = request.form.get('avocat_nom')
        if not avocat_nom:
            raise ValueError('Veuillez sélectionner un avocat.')
        avocat = Avocat.query.filter_by(nom=avocat_nom).first()
        if not avocat:
            raise ValueError("Avocat introuvable.")

        # Vérifier unicité du numéro
        if ActeAvocat.query.filter_by(numero_acte=numero_acte).first():
            raise ValueError("Le numéro d'acte existe déjà, veuillez en saisir un autre.")

        # Sauvegarder un ou plusieurs documents si présents
        doc_metas = []
        files = request.files.getlist('documents') or []
        for f in files:
            if f and f.filename:
                meta = save_uploaded_file(f, numero_acte)
                if meta:
                    doc_metas.append(meta)
        # Compatibilité: si un seul champ 'document' est utilisé
        if not doc_metas:
            single = request.files.get('document')
            if single and single.filename:
                meta = save_uploaded_file(single, numero_acte)
                if meta:
                    doc_metas.append(meta)

        # Récupération des champs manuels
        nature_acte = request.form.get('nature_acte', '').strip()
        # Multi-champs identités: identites_parties[]
        parties_list = [p.strip() for p in request.form.getlist('identites_parties[]') if p and p.strip()]
        # Compat: fallback sur champ unique
        if not parties_list:
            single_parties = request.form.get('identites_parties', '').strip()
            if single_parties:
                parties_list = [single_parties]
        identites_parties = '\n'.join(parties_list)
        nombre_pages_raw = request.form.get('nombre_pages')
        if not nature_acte:
            raise ValueError('Veuillez saisir la nature de l’acte.')
        if not identites_parties:
            raise ValueError('Veuillez saisir au moins une identité de partie.')
        try:
            nombre_pages = int(nombre_pages_raw)
            if nombre_pages <= 0:
                raise ValueError()
        except Exception:
            raise ValueError('Le nombre de pages doit être un entier positif.')

        # Date de création sélectionnable
        date_creation_str = request.form.get('date_creation')
        selected_dt = None
        if date_creation_str:
            try:
                selected_dt = datetime.fromisoformat(date_creation_str)
            except Exception:
                raise ValueError('Format de date de création invalide.')

        now = datetime.now()
        effective_dt = selected_dt or now
        acte = ActeAvocat(
            numero_acte=numero_acte,
            avocat_id=avocat.avocat_id,
            date_acte=effective_dt.date(),
            date_depot=effective_dt.date(),
            nature_acte=nature_acte,
            identites_parties=identites_parties,
            nombre_pages=nombre_pages,
            agent_reception=current_user.id,
            date_creation=effective_dt,
            statut='recu',
        )
        # Si vous souhaitez stocker le chemin du document, ajoutez une colonne dans le modèle
        # puis affectez-la ici, ex: acte.document_path = saved_path

        db.session.add(acte)
        db.session.flush()  # acte_id disponible sans commit

        # Enregistrer les documents et leurs métadonnées si présents
        if doc_metas:
            for meta in doc_metas:
                doc = ActeDocument(
                    acte_id=acte.acte_id,
                    storage_path=meta['storage_path'],
                    original_name=meta['original_name'],
                    mime_type=meta['mime_type'],
                    size_bytes=meta['size_bytes'],
                    sha256_hash=meta['sha256_hash'],
                    uploaded_by=current_user.id,
                )
                db.session.add(doc)

        db.session.commit()
        flash("Acte enregistré avec succès.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur: {str(e)}", 'danger')

    return redirect(url_for('actes_avocat.index'))


@actes_avocat_bp.route('/<int:acte_id>', methods=['GET'])
@login_required
@role_required('assistant_administratif')
def view(acte_id):
    acte = ActeAvocat.query.get_or_404(acte_id)
    return render_template('assistant_admin/actes_avocat_detail.html', acte=acte)


@actes_avocat_bp.route('/<int:acte_id>/modifier', methods=['GET', 'POST'])
@login_required
@role_required('assistant_administratif')
def edit(acte_id):
    acte = ActeAvocat.query.get_or_404(acte_id)
    if request.method == 'POST':
        try:
            new_statut = request.form.get('statut')
            if new_statut in {'recu', 'traite', 'archive'}:
                acte.statut = new_statut
            db.session.commit()
            flash('Acte mis à jour.', 'success')
            return redirect(url_for('actes_avocat.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {str(e)}', 'danger')
    return render_template('assistant_admin/actes_avocat_edit.html', acte=acte)


@actes_avocat_bp.route('/<int:acte_id>/supprimer', methods=['POST'])
@login_required
@role_required('assistant_administratif')
def delete(acte_id):
    acte = ActeAvocat.query.get_or_404(acte_id)
    try:
        db.session.delete(acte)
        db.session.commit()
        flash("Acte supprimé.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur: {str(e)}", 'danger')
    return redirect(url_for('actes_avocat.index'))


# Route utilitaire si on souhaite servir les fichiers uploadés depuis /app/uploads/actes
@actes_avocat_bp.route('/fichiers/<path:filename>')
@login_required
@role_required('assistant_administratif')
def serve_file(filename):
    directory = os.path.join(current_app.instance_path, 'uploads', 'actes')
    return send_from_directory(directory, filename)