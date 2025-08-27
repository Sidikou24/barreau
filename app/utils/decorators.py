
# app/utils/decorators.py (Décorateurs utilitaires)
from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user

def role_required(allowed_roles):
    """
    Décorateur pour vérifier si l'utilisateur a le bon rôle
    allowed_roles peut être une string ou une liste de strings
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            if isinstance(allowed_roles, str):
                roles = [allowed_roles]
            else:
                roles = allowed_roles
            
            if current_user.role not in roles:
                flash('Vous n\'avez pas les permissions pour accéder à cette page.', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def login_required_custom(f):
    """Décorateur personnalisé pour vérifier l'authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Veuillez vous connecter pour accéder à cette page.', 'info')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
