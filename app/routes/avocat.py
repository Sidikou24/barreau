# app/routes/avocat.py (Routes pour les avocats)
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.utils.decorators import role_required

avocat_bp = Blueprint('avocat', __name__)

@avocat_bp.route('/dashboard')
@login_required
@role_required('avocat')
def dashboard():
    return render_template('avocat/dashboard.html')