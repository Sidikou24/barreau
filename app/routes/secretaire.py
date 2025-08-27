
# app/routes/secretaire.py
from flask import Blueprint, render_template
from flask_login import login_required
from app.utils.decorators import role_required

secretaire_bp = Blueprint('secretaire', __name__)

@secretaire_bp.route('/dashboard')
@login_required
@role_required('secretaire')
def dashboard():
    return render_template('secretaire/dashboard.html')