# app/routes/assistant_comptable.py
from flask import Blueprint, render_template
from flask_login import login_required
from app.utils.decorators import role_required

assistant_comptable_bp = Blueprint('assistant_comptable', __name__)

@assistant_comptable_bp.route('/dashboard')
@login_required
@role_required('assistant_comptable')
def dashboard():
    return render_template('assistant_comptable/dashboard.html')
